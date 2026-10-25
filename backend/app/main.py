"""EcoAlert: servicios CRUD iniciales, alineados con rutas OpenAPI del equipo.
No reemplaza autenticación, ingesta geoespacial ni comparación de periodos.
"""
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, Header, Path, Query, Request, Response
from fastapi.responses import JSONResponse
from psycopg.errors import UniqueViolation
from pwdlib import PasswordHash

from . import db
from .errors import ApiError, no_encontrado, registrar_errores
from .schemas import (CODIGO_ZONA, AjustePrioridad, CargaAlertas, EntradaHistorial, Marca, PaginaAlertas, Trabajo,
                      Usuario, UsuarioActualizar, UsuarioCrear, UsuarioReemplazar)

password_hash = PasswordHash.recommended()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.pool.open(wait=True)
    try:
        yield
    finally:
        db.pool.close()


app = FastAPI(title='EcoAlert Tambopata - CRUD inicial', version='0.1.0', lifespan=lifespan,
              description='Implementación parcial del contrato OpenAPI; ver README para límites.')

registrar_errores(app)

# El contrato OpenAPI publica sus operaciones bajo /api/v1; /salud queda fuera por no ser contractual.
router = APIRouter(prefix='/api/v1')

CodigoZona = Annotated[str, Path(pattern=CODIGO_ZONA)]
USER_FIELDS = 'id,nombre_completo,correo,rol,activo,debe_cambiar_password,creado_en'
ALERTA_FIELDS = 'id,fuente,codigo,fecha_deteccion,fecha_ingesta,presente_en_ultima_carga,zona_codigo,area_ha'


def ref(alias):
    """UsuarioRef (id, nombre_completo) o NULL, a partir de un LEFT JOIN con usuarios."""
    return (f"CASE WHEN {alias}.id IS NULL THEN NULL "
            f"ELSE json_build_object('id', {alias}.id, 'nombre_completo', {alias}.nombre_completo) END")


CARGAS_SQL = f'''SELECT c.id, c.fuente, c.fecha_corte, c.cargada_en, {ref('u')} AS cargada_por,
    c.alertas_en_archivo, c.alertas_nuevas, c.alertas_existentes, c.alertas_fuera_ambito, c.alertas_ausentes,
    c.zonas_creadas, c.zonas_actualizadas, COALESCE(c.resumen, '') AS resumen
    FROM cargas_alertas c JOIN usuarios u ON u.id = c.cargada_por'''

MARCAS_SQL = f'''SELECT m.id, m.tipo, m.origen, m.rotulo, m.texto, m.activa, m.creada_en,
    {ref('uc')} AS creada_por, m.retirada_en, {ref('ur')} AS retirada_por, m.motivo_retiro
    FROM marcas m LEFT JOIN usuarios uc ON uc.id = m.creada_por LEFT JOIN usuarios ur ON ur.id = m.retirada_por'''

AJUSTES_SQL = f'''SELECT a.id, a.forma, a.nivel_elegido::text AS nivel_elegido, a.puntaje_ajustado,
    a.puntaje_calculado_al_ajustar, a.justificacion, a.estado, a.creado_en, {ref('uc')} AS creado_por,
    a.retirado_en, {ref('ur')} AS retirado_por, a.justificacion_retiro
    FROM ajustes_prioridad a JOIN usuarios uc ON uc.id = a.creado_por LEFT JOIN usuarios ur ON ur.id = a.retirado_por'''

# Sin autor (autor_id nulo) la entrada es del sistema, p. ej. la creación de la zona (RF-12-AC-19).
HISTORIAL_SQL = '''SELECT h.id, h.tipo_accion, h.fecha_hora,
    CASE WHEN u.id IS NULL THEN json_build_object('tipo', 'sistema', 'nombre', 'Sistema')
         ELSE json_build_object('tipo', 'usuario', 'id', u.id, 'nombre', u.nombre_completo) END AS autor,
    h.codigo_alerta_origen, h.estado_anterior::text AS estado_anterior, h.estado_nuevo::text AS estado_nuevo,
    h.ajuste_id, h.forma, h.nivel_elegido::text AS nivel_elegido, h.puntaje_calculado, h.puntaje_ajustado,
    h.marca_id, h.texto_marca, h.texto
    FROM entradas_historial h LEFT JOIN usuarios u ON u.id = h.autor_id'''


def encontrado(fila, mensaje):
    if not fila:
        raise no_encontrado(mensaje)
    return fila


def exigir_merge_patch(request: Request):
    if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/merge-patch+json':
        raise ApiError(415, 'TIPO_CONTENIDO_NO_SOPORTADO', 'Usa Content-Type application/merge-patch+json')


@app.get('/salud')
def salud():
    return {'estado': 'ok', 'base_datos': bool(db.run('SELECT 1 AS ok', one=True))}


@router.get('/usuarios', response_model=list[Usuario])
def listar_usuarios(activo: bool | None = None):
    return db.run(f'SELECT {USER_FIELDS} FROM usuarios WHERE (%s::boolean IS NULL OR activo=%s) ORDER BY nombre_completo',
                  (activo, activo))


@router.post('/usuarios', status_code=201, response_model=Usuario)
def crear_usuario(body: UsuarioCrear, response: Response, idempotency_key: Annotated[UUID, Header()]):
    operacion = 'crearUsuario'
    huella = db.huella(body.model_dump(mode='json'))
    with db.transaction() as conn:
        previa = db.respuesta_previa(conn, idempotency_key, operacion, huella)
        if previa:
            return JSONResponse(previa['cuerpo_respuesta'], previa['estado_http'], {'Location': previa['location']})
        try:
            fila = db.query(conn, f'INSERT INTO usuarios (nombre_completo, correo, rol, password_hash) '
                                  f'VALUES (%s, %s, %s, %s) RETURNING {USER_FIELDS}',
                            (body.nombre_completo, str(body.correo), body.rol, password_hash.hash(body.password_temporal)),
                            one=True)
        except UniqueViolation:
            raise ApiError(409, 'CORREO_DUPLICADO', 'Ya existe una cuenta con ese correo') from None
        usuario = Usuario(**fila)
        location = app.url_path_for('obtener_usuario', usuarioId=usuario.id)
        db.guardar_respuesta(conn, idempotency_key, operacion, huella, 201, usuario.model_dump(mode='json'), location)
    response.headers['Location'] = location
    return usuario


@router.get('/usuarios/{usuarioId}', response_model=Usuario)
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


@router.put('/usuarios/{usuarioId}', response_model=Usuario)
def reemplazar_usuario(usuarioId: UUID, body: UsuarioReemplazar):
    return aplicar_cambios(usuarioId, body.model_dump())


@router.patch('/usuarios/{usuarioId}', response_model=Usuario, dependencies=[Depends(exigir_merge_patch)])
def actualizar_usuario(usuarioId: UUID, body: UsuarioActualizar):
    return aplicar_cambios(usuarioId, body.model_dump(exclude_unset=True))


@router.get('/alertas', response_model=PaginaAlertas)
def listar_alertas(zona: Annotated[str | None, Query(pattern=CODIGO_ZONA)] = None,
                   presente_en_ultima_carga: bool | None = None,
                   limite: Annotated[int, Query(ge=1, le=500)] = 100,
                   desplazamiento: Annotated[int, Query(ge=0)] = 0):
    # El contrato exige zona y área en toda alerta; las aún sin agrupar o sin área no se publican.
    filtros, params = ['zona_codigo IS NOT NULL', 'area_ha IS NOT NULL'], []
    if zona is not None:
        filtros.append('zona_codigo=%s')
        params.append(zona)
    if presente_en_ultima_carga is not None:
        filtros.append('presente_en_ultima_carga=%s')
        params.append(presente_en_ultima_carga)
    donde = ' AND '.join(filtros)
    with db.transaction() as conn:
        total = db.query(conn, f'SELECT count(*) AS total FROM alertas WHERE {donde}', params, one=True)['total']
        alertas = db.query(conn, f'SELECT {ALERTA_FIELDS} FROM alertas WHERE {donde} '
                                 'ORDER BY fecha_deteccion DESC, id LIMIT %s OFFSET %s', (*params, limite, desplazamiento))
    return {'total': total, 'limite': limite, 'desplazamiento': desplazamiento, 'alertas': alertas}


@router.get('/cargas-alertas', response_model=list[CargaAlertas])
def listar_cargas():
    return db.run(CARGAS_SQL + ' ORDER BY c.cargada_en DESC, c.id')


@router.get('/cargas-alertas/{cargaId}', response_model=CargaAlertas)
def obtener_carga(cargaId: UUID):
    return encontrado(db.run(CARGAS_SQL + ' WHERE c.id=%s', (cargaId,), one=True), f'No existe la carga {cargaId}')


@router.get('/zonas/{codigo}/marcas', response_model=list[Marca], response_model_exclude_none=True)
def listar_marcas(codigo: CodigoZona, incluir_retiradas: bool = False):
    ensure_zone(codigo)
    return db.run(MARCAS_SQL + ' WHERE m.zona_codigo=%s AND (%s OR m.activa) ORDER BY m.creada_en DESC, m.id',
                  (codigo, incluir_retiradas))


@router.get('/zonas/{codigo}/marcas/{marcaId}', response_model=Marca, response_model_exclude_none=True)
def obtener_marca(codigo: CodigoZona, marcaId: UUID):
    return encontrado(db.run(MARCAS_SQL + ' WHERE m.zona_codigo=%s AND m.id=%s', (codigo, marcaId), one=True),
                      f'No existe la marca {marcaId}')


# El API requiere actor autenticado para crear/retirar marcas, ajustes y cambios.
# No se habilitan escrituras sin identidad verificable: implementar /auth/sesion primero.
def ensure_zone(codigo):
    encontrado(db.run('SELECT 1 FROM zonas_cambio WHERE codigo=%s', (codigo,), one=True), f'No existe la zona {codigo}')


@router.get('/zonas/{codigo}/ajustes', response_model=list[AjustePrioridad])
def listar_ajustes(codigo: CodigoZona):
    ensure_zone(codigo)
    return db.run(AJUSTES_SQL + ' WHERE a.zona_codigo=%s ORDER BY a.creado_en DESC, a.id', (codigo,))


@router.get('/zonas/{codigo}/ajustes/{ajusteId}', response_model=AjustePrioridad)
def obtener_ajuste(codigo: CodigoZona, ajusteId: UUID):
    return encontrado(db.run(AJUSTES_SQL + ' WHERE a.zona_codigo=%s AND a.id=%s', (codigo, ajusteId), one=True),
                      f'No existe el ajuste {ajusteId}')


# Orden cronológico ascendente: la primera entrada es la creación de la zona (RF-12-AC-19).
@router.get('/zonas/{codigo}/historial', response_model=list[EntradaHistorial], response_model_exclude_none=True)
def historial(codigo: CodigoZona):
    ensure_zone(codigo)
    return db.run(HISTORIAL_SQL + ' WHERE h.zona_codigo=%s ORDER BY h.fecha_hora, h.id', (codigo,))


@router.get('/zonas/{codigo}/historial/{entradaId}', response_model=EntradaHistorial, response_model_exclude_none=True)
def historial_entrada(codigo: CodigoZona, entradaId: UUID):
    return encontrado(db.run(HISTORIAL_SQL + ' WHERE h.zona_codigo=%s AND h.id=%s', (codigo, entradaId), one=True),
                      f'No existe la entrada de historial {entradaId}')


@router.get('/trabajos/{trabajoId}', response_model=Trabajo, response_model_exclude_none=True)
def obtener_trabajo(trabajoId: UUID):
    return encontrado(db.run('SELECT id, tipo, estado, creado_en, actualizado_en, mensaje_estado, resultado, error '
                             'FROM trabajos WHERE id=%s', (trabajoId,), one=True),
                      f'No existe el trabajo {trabajoId}')


app.include_router(router)
