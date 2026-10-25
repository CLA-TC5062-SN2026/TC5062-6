"""Gestión de cuentas (RF-02). Todas las operaciones son exclusivas de Coordinación."""
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from psycopg.errors import UniqueViolation

from app import db
from app.dependencies import COORDINACION, solo_coordinacion
from app.errors import fail
from app.schemas import UsuarioActualizar, UsuarioCrear
from app.security import hashear
from app.serializacion import json_safe

# Nunca incluir password_hash: la lista de columnas es explícita, no SELECT *.
USER_FIELDS = 'id,nombre_completo,correo,rol,activo,debe_cambiar_password,creado_en'
RUTA_USUARIO = '/api/v1/usuarios/{}'

router = APIRouter(prefix='/usuarios', tags=['Usuarios'])


def insertar_usuario(body: UsuarioCrear, response: Response) -> dict:
    """Crea la cuenta activa y con contraseña temporal (RF-02-AC-1). Compartida con /auth/register."""
    try:
        with db.transaccion() as conn:
            fila = conn.execute(
                f'''INSERT INTO usuarios (nombre_completo,correo,rol,password_hash)
                    VALUES (%s,%s,%s,%s) RETURNING {USER_FIELDS}''',
                (body.nombre_completo, str(body.correo), body.rol, hashear(body.password_temporal)),
            ).fetchone()
    except UniqueViolation:
        fail(409, 'Ya existe una cuenta con ese correo', 'CORREO_DUPLICADO')
    response.headers['Location'] = RUTA_USUARIO.format(fila['id'])
    return json_safe(fila)


@router.get('', dependencies=[Depends(solo_coordinacion)])
def listar_usuarios(activo: bool | None = None):
    rows = db.run(f'SELECT {USER_FIELDS} FROM usuarios WHERE (%s::boolean IS NULL OR activo=%s) ORDER BY nombre_completo', (activo, activo))
    return json_safe(rows)


@router.post('', status_code=201, dependencies=[Depends(solo_coordinacion)])
def crear_usuario(body: UsuarioCrear, response: Response):
    return insertar_usuario(body, response)


@router.get('/{usuarioId}', dependencies=[Depends(solo_coordinacion)])
def obtener_usuario(usuarioId: UUID):
    row = db.run(f'SELECT {USER_FIELDS} FROM usuarios WHERE id=%s', (usuarioId,), one=True)
    if not row: fail(404, 'Usuario no encontrado')
    return json_safe(row)


@router.patch('/{usuarioId}', dependencies=[Depends(solo_coordinacion)])
def actualizar_usuario(usuarioId: UUID, body: UsuarioActualizar):
    data = body.model_dump(exclude_unset=True)
    if not data or any(v is None for v in data.values()): fail(422, 'Debe indicar al menos un campo válido')
    # Lista blanca de campos, nunca interpolar nombres provenientes directamente del usuario.
    fields = [k for k in ('nombre_completo', 'rol', 'activo') if k in data]
    updates = ', '.join(f'{k}=%s' for k in fields)
    with db.transaccion() as conn:
        # FOR UPDATE serializa las modificaciones concurrentes de cuentas de coordinación.
        coordinadores = {r['id'] for r in conn.execute(
            'SELECT id FROM usuarios WHERE rol=%s AND activo FOR UPDATE', (COORDINACION,)).fetchall()}
        pierde_coordinacion = usuarioId in coordinadores and (
            data.get('activo') is False or data.get('rol', COORDINACION) != COORDINACION)
        if pierde_coordinacion and len(coordinadores) == 1:
            fail(409, 'No se puede quitar el rol o desactivar la última cuenta de coordinación', 'ULTIMA_COORDINACION')
        row = conn.execute(f'UPDATE usuarios SET {updates} WHERE id=%s RETURNING {USER_FIELDS}',
                           tuple(data[k] for k in fields) + (usuarioId,)).fetchone()
        if not row: fail(404, 'Usuario no encontrado')
        if data.get('activo') is False:
            # Al desactivar se cierran sus sesiones abiertas (contrato, actualizarUsuario).
            conn.execute('UPDATE sesiones SET revocada_en=now() WHERE usuario_id=%s AND revocada_en IS NULL', (usuarioId,))
    return json_safe(row)
