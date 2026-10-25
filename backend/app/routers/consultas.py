"""Consultas de alertas, cargas, marcas, ajustes, historial y trabajos (ambos roles, según x-roles)."""
from uuid import UUID

from fastapi import APIRouter, Depends

from app.db import run
from app.dependencies import cualquier_rol
from app.errors import fail
from app.serializacion import json_safe

router = APIRouter(dependencies=[Depends(cualquier_rol)])


@router.get('/alertas', tags=['Alertas'])
def listar_alertas():
    return json_safe(run('''SELECT id,fuente,codigo,fecha_deteccion,fecha_ingesta,
        presente_en_ultima_carga,zona_codigo,area_ha FROM alertas ORDER BY fecha_deteccion DESC'''))


@router.get('/cargas-alertas', tags=['Alertas'])
def listar_cargas():
    return json_safe(run('''SELECT id,fuente,fecha_corte,cargada_en,cargada_por,alertas_en_archivo,
        alertas_nuevas,alertas_existentes,alertas_fuera_ambito,alertas_ausentes,
        zonas_creadas,zonas_actualizadas,resumen FROM cargas_alertas ORDER BY cargada_en DESC'''))


@router.get('/cargas-alertas/{cargaId}', tags=['Alertas'])
def obtener_carga(cargaId: UUID):
    row=run('''SELECT id,fuente,fecha_corte,cargada_en,cargada_por,alertas_en_archivo,
        alertas_nuevas,alertas_existentes,alertas_fuera_ambito,alertas_ausentes,
        zonas_creadas,zonas_actualizadas,resumen FROM cargas_alertas WHERE id=%s''',(cargaId,),one=True)
    if not row: fail(404,'Carga no encontrada')
    return json_safe(row)


@router.get('/zonas/{codigo}/marcas', tags=['Revisión de zonas'])
def listar_marcas(codigo: str, incluir_retiradas: bool=False):
    ensure_zone(codigo)
    return json_safe(run('SELECT * FROM marcas WHERE zona_codigo=%s AND (%s OR activa) ORDER BY creada_en DESC',
                         (codigo,incluir_retiradas)))


@router.get('/zonas/{codigo}/marcas/{marcaId}', tags=['Revisión de zonas'])
def obtener_marca(codigo: str,marcaId: UUID):
    row=run('SELECT * FROM marcas WHERE zona_codigo=%s AND id=%s',(codigo,marcaId),one=True)
    if not row: fail(404,'Marca no encontrada')
    return json_safe(row)


def ensure_zone(codigo):
    if not run('SELECT codigo FROM zonas_cambio WHERE codigo=%s',(codigo,),one=True): fail(404,'Zona no encontrada')


@router.get('/zonas/{codigo}/ajustes', tags=['Revisión de zonas'])
def listar_ajustes(codigo: str):
    ensure_zone(codigo)
    return json_safe(run('SELECT * FROM ajustes_prioridad WHERE zona_codigo=%s ORDER BY creado_en DESC',(codigo,)))


@router.get('/zonas/{codigo}/ajustes/{ajusteId}', tags=['Revisión de zonas'])
def obtener_ajuste(codigo: str, ajusteId: UUID):
    row=run('SELECT * FROM ajustes_prioridad WHERE zona_codigo=%s AND id=%s',(codigo,ajusteId),one=True)
    if not row: fail(404,'Ajuste no encontrado')
    return json_safe(row)


_SQL_HISTORIAL = '''SELECT h.id,h.tipo_accion,h.fecha_hora,h.codigo_alerta_origen,h.estado_anterior,
        h.estado_nuevo,h.ajuste_id,h.forma,h.nivel_elegido,h.puntaje_calculado,h.puntaje_ajustado,
        h.marca_id,h.texto_marca,h.texto,
        json_build_object('id',u.id,'nombre_completo',u.nombre_completo) AS autor
        FROM entradas_historial h JOIN usuarios u ON u.id=h.autor_id
        WHERE h.zona_codigo=%s'''


@router.get('/zonas/{codigo}/historial', tags=['Revisión de zonas'])
def historial(codigo: str):
    ensure_zone(codigo)
    return json_safe(run(_SQL_HISTORIAL + ' ORDER BY h.fecha_hora DESC',(codigo,)))


@router.get('/zonas/{codigo}/historial/{entradaId}', tags=['Revisión de zonas'])
def historial_entrada(codigo: str,entradaId: UUID):
    row=run(_SQL_HISTORIAL + ' AND h.id=%s',(codigo,entradaId),one=True)
    if not row: fail(404,'Entrada de historial no encontrada')
    return json_safe(row)


@router.get('/trabajos/{trabajoId}', tags=['Trabajos'])
def obtener_trabajo(trabajoId: UUID):
    row=run('SELECT * FROM trabajos WHERE id=%s',(trabajoId,),one=True)
    if not row: fail(404,'Trabajo no encontrado')
    return json_safe(row)
