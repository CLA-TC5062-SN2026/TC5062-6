"""Consultas de alertas, cargas, marcas, ajustes, historial y trabajos (ambos roles, según x-roles)."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from app import db
from app.dependencies import cualquier_rol
from app.errors import encontrado
from app.schemas import (CODIGO_ZONA, AjustePrioridad, CargaAlertas, EntradaHistorial, Marca, PaginaAlertas,
                         Trabajo)

router = APIRouter(dependencies=[Depends(cualquier_rol)])

CodigoZona = Annotated[str, Path(pattern=CODIGO_ZONA)]
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


def ensure_zone(codigo):
    encontrado(db.run('SELECT 1 FROM zonas_cambio WHERE codigo=%s', (codigo,), one=True), f'No existe la zona {codigo}')


@router.get('/alertas', response_model=PaginaAlertas, tags=['Alertas'])
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


@router.get('/cargas-alertas', response_model=list[CargaAlertas], tags=['Alertas'])
def listar_cargas():
    return db.run(CARGAS_SQL + ' ORDER BY c.cargada_en DESC, c.id')


@router.get('/cargas-alertas/{cargaId}', response_model=CargaAlertas, tags=['Alertas'])
def obtener_carga(cargaId: UUID):
    return encontrado(db.run(CARGAS_SQL + ' WHERE c.id=%s', (cargaId,), one=True), f'No existe la carga {cargaId}')


@router.get('/zonas/{codigo}/marcas', response_model=list[Marca], response_model_exclude_none=True,
            tags=['Revisión de zonas'])
def listar_marcas(codigo: CodigoZona, incluir_retiradas: bool = False):
    ensure_zone(codigo)
    return db.run(MARCAS_SQL + ' WHERE m.zona_codigo=%s AND (%s OR m.activa) ORDER BY m.creada_en DESC, m.id',
                  (codigo, incluir_retiradas))


@router.get('/zonas/{codigo}/marcas/{marcaId}', response_model=Marca, response_model_exclude_none=True,
            tags=['Revisión de zonas'])
def obtener_marca(codigo: CodigoZona, marcaId: UUID):
    return encontrado(db.run(MARCAS_SQL + ' WHERE m.zona_codigo=%s AND m.id=%s', (codigo, marcaId), one=True),
                      f'No existe la marca {marcaId}')


@router.get('/zonas/{codigo}/ajustes', response_model=list[AjustePrioridad], tags=['Revisión de zonas'])
def listar_ajustes(codigo: CodigoZona):
    ensure_zone(codigo)
    return db.run(AJUSTES_SQL + ' WHERE a.zona_codigo=%s ORDER BY a.creado_en DESC, a.id', (codigo,))


@router.get('/zonas/{codigo}/ajustes/{ajusteId}', response_model=AjustePrioridad, tags=['Revisión de zonas'])
def obtener_ajuste(codigo: CodigoZona, ajusteId: UUID):
    return encontrado(db.run(AJUSTES_SQL + ' WHERE a.zona_codigo=%s AND a.id=%s', (codigo, ajusteId), one=True),
                      f'No existe el ajuste {ajusteId}')


# Orden cronológico ascendente: la primera entrada es la creación de la zona (RF-12-AC-19).
@router.get('/zonas/{codigo}/historial', response_model=list[EntradaHistorial], response_model_exclude_none=True,
            tags=['Revisión de zonas'])
def historial(codigo: CodigoZona):
    ensure_zone(codigo)
    return db.run(HISTORIAL_SQL + ' WHERE h.zona_codigo=%s ORDER BY h.fecha_hora, h.id', (codigo,))


@router.get('/zonas/{codigo}/historial/{entradaId}', response_model=EntradaHistorial, response_model_exclude_none=True,
            tags=['Revisión de zonas'])
def historial_entrada(codigo: CodigoZona, entradaId: UUID):
    return encontrado(db.run(HISTORIAL_SQL + ' WHERE h.zona_codigo=%s AND h.id=%s', (codigo, entradaId), one=True),
                      f'No existe la entrada de historial {entradaId}')


@router.get('/trabajos/{trabajoId}', response_model=Trabajo, response_model_exclude_none=True, tags=['Trabajos'])
def obtener_trabajo(trabajoId: UUID):
    return encontrado(db.run('SELECT id, tipo, estado, creado_en, actualizado_en, mensaje_estado, resultado, error '
                             'FROM trabajos WHERE id=%s', (trabajoId,), one=True),
                      f'No existe el trabajo {trabajoId}')
