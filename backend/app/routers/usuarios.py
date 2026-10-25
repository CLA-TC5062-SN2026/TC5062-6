"""Gestión de cuentas (RF-02). Todas las operaciones son exclusivas de Coordinación."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from psycopg.errors import UniqueViolation

from app import db
from app.dependencies import solo_coordinacion
from app.errors import ApiError, encontrado
from app.schemas import Usuario, UsuarioActualizar, UsuarioCrear, UsuarioReemplazar
from app.security import hashear

# Nunca incluir password_hash: la lista de columnas es explícita, no SELECT *.
USER_FIELDS = 'id,nombre_completo,correo,rol,activo,debe_cambiar_password,creado_en'

router = APIRouter(prefix='/usuarios', tags=['Usuarios'], dependencies=[Depends(solo_coordinacion)])


def exigir_merge_patch(request: Request):
    if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/merge-patch+json':
        raise ApiError(415, 'TIPO_CONTENIDO_NO_SOPORTADO', 'Usa Content-Type application/merge-patch+json')


def insertar_usuario(body: UsuarioCrear, request: Request, response: Response, clave: UUID):
    """Alta idempotente de la cuenta, activa y con contraseña temporal (RF-02-AC-1). Compartida con /auth/register."""
    operacion = 'crearUsuario'
    huella = db.huella(body.model_dump(mode='json'))
    with db.transaction() as conn:
        previa = db.respuesta_previa(conn, clave, operacion, huella)
        if previa:
            return JSONResponse(previa['cuerpo_respuesta'], previa['estado_http'], {'Location': previa['location']})
        try:
            fila = db.query(conn, f'INSERT INTO usuarios (nombre_completo, correo, rol, password_hash) '
                                  f'VALUES (%s, %s, %s, %s) RETURNING {USER_FIELDS}',
                            (body.nombre_completo, str(body.correo), body.rol, hashear(body.password_temporal)),
                            one=True)
        except UniqueViolation:
            raise ApiError(409, 'CORREO_DUPLICADO', 'Ya existe una cuenta con ese correo') from None
        usuario = Usuario(**fila)
        location = request.app.url_path_for('obtener_usuario', usuarioId=usuario.id)
        db.guardar_respuesta(conn, clave, operacion, huella, 201, usuario.model_dump(mode='json'), location)
    response.headers['Location'] = location
    return usuario


@router.get('', response_model=list[Usuario])
def listar_usuarios(activo: bool | None = None):
    return db.run(f'SELECT {USER_FIELDS} FROM usuarios WHERE (%s::boolean IS NULL OR activo=%s) ORDER BY nombre_completo',
                  (activo, activo))


@router.post('', status_code=201, response_model=Usuario)
def crear_usuario(body: UsuarioCrear, request: Request, response: Response,
                  idempotency_key: Annotated[UUID, Header()]):
    return insertar_usuario(body, request, response, idempotency_key)


@router.get('/{usuarioId}', response_model=Usuario)
def obtener_usuario(usuarioId: UUID):
    return encontrado(db.run(f'SELECT {USER_FIELDS} FROM usuarios WHERE id=%s', (usuarioId,), one=True),
                      f'No existe el usuario {usuarioId}')


def aplicar_cambios(usuarioId: UUID, cambios: dict):
    """Actualización transaccional de una cuenta, compartida por PUT y PATCH."""
    with db.transaction() as conn:
        # Se bloquean las cuentas de coordinación activas para que dos cambios simultáneos no dejen el sistema sin ninguna.
        coordinacion = db.query(conn, "SELECT id FROM usuarios WHERE rol='coordinacion' AND activo ORDER BY id FOR UPDATE")
        actual = encontrado(db.query(conn, 'SELECT rol, activo FROM usuarios WHERE id=%s FOR UPDATE', (usuarioId,), one=True),
                            f'No existe el usuario {usuarioId}')
        desactiva = cambios.get('activo') is False
        quita_rol = cambios.get('rol', actual['rol']) != 'coordinacion'
        if actual['rol'] == 'coordinacion' and actual['activo'] and len(coordinacion) == 1 and (desactiva or quita_rol):
            accion = 'desactivar' if desactiva else 'quitar el rol a'
            raise ApiError(409, 'ULTIMA_COORDINACION', f'No se puede {accion} la última cuenta de coordinación')
        # Los nombres de columna provienen del esquema (extra='forbid'), nunca del cliente.
        asignaciones = ', '.join(f'{campo}=%s' for campo in cambios)
        fila = db.query(conn, f'UPDATE usuarios SET {asignaciones} WHERE id=%s RETURNING {USER_FIELDS}',
                        (*cambios.values(), usuarioId), one=True)
        if desactiva:
            db.query(conn, 'UPDATE sesiones SET revocada_en = now() WHERE usuario_id=%s AND revocada_en IS NULL',
                     (usuarioId,))
    return fila


@router.put('/{usuarioId}', response_model=Usuario)
def reemplazar_usuario(usuarioId: UUID, body: UsuarioReemplazar):
    return aplicar_cambios(usuarioId, body.model_dump())


@router.patch('/{usuarioId}', response_model=Usuario, dependencies=[Depends(exigir_merge_patch)])
def actualizar_usuario(usuarioId: UUID, body: UsuarioActualizar):
    return aplicar_cambios(usuarioId, body.model_dump(exclude_unset=True))
