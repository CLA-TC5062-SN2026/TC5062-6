"""Capas del mapa en GeoJSON (operationId obtenerElementosCapa, RF-06-AC-2 y RF-06-AC-6).

Las geometrías se guardan en UTM 19S (EPSG:32719) y se publican en EPSG:4326 como exige RFC 7946 (sección 4),
simplificadas a 5 m para el mapa. Solo se publican atributos que el contrato enumera por capa: el catastro minero
nunca incluye al titular (RF-06-AC-6).
"""
import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from app import db
from app.dependencies import cualquier_rol
from app.errors import ApiError

router = APIRouter(dependencies=[Depends(cualquier_rol)])

CapaMapaId = Literal['limite_reserva', 'zona_amortiguamiento', 'rios', 'catastro_minero', 'alertas_geobosques',
                     'zonas_cambio']

# Tolerancia de simplificación en metros (unidades de EPSG:32719) y decimales de las coordenadas publicadas:
# 6 decimales de grado ≈ 0.1 m, más precisión que la de las fuentes.
SIMPLIFICACION_M = 5
DECIMALES = 6
GEOMETRIA = f'ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology({{col}}, {SIMPLIFICACION_M}), 4326), {DECIMALES})'
FILTRO_BBOX = '{col} && ST_Transform(ST_MakeEnvelope(%s, %s, %s, %s, 4326), 32719)'

ZONAS_SQL = f'''SELECT z.codigo AS id, {GEOMETRIA.format(col='z.geometria')} AS geometria,
    json_build_object('codigo', z.codigo, 'nivel', z.nivel, 'puntaje_vigente', z.puntaje_vigente, 'estado', z.estado,
        'marcas', COALESCE((SELECT json_agg(json_build_object('id', m.id, 'tipo', m.tipo, 'texto', m.texto)
                                            ORDER BY m.creada_en, m.id)
                            FROM marcas m WHERE m.zona_codigo = z.codigo AND m.activa), '[]'::json)) AS propiedades
    FROM zonas_cambio z WHERE {{donde}} ORDER BY z.codigo'''

ALERTAS_SQL = f'''SELECT a.id::text AS id, {GEOMETRIA.format(col='a.geometria')} AS geometria,
    json_build_object('codigo', a.codigo, 'fecha_deteccion', a.fecha_deteccion, 'zona_codigo', a.zona_codigo,
        'presente_en_ultima_carga', a.presente_en_ultima_carga) AS propiedades
    FROM alertas a WHERE {{donde}} ORDER BY a.fecha_deteccion DESC, a.id'''

# Capas de referencia: solo la versión vigente (RF-06, "usa la versión vigente de cada capa").
REFERENCIA_SQL = f'''SELECT e.id::text AS id, {GEOMETRIA.format(col='e.geometria')} AS geometria,
    CASE WHEN v.tipo = 'catastro_minero'
         THEN json_build_object('tipo_derecho', e.tipo_derecho, 'codigo', e.codigo_origen, 'estado', e.estado_derecho,
                                'fecha_corte', v.fecha_corte)
         ELSE json_build_object('codigo', e.codigo_origen, 'nombre', e.nombre) END AS propiedades
    FROM elementos_capa e JOIN versiones_capa v ON v.id = e.version_capa_id
    WHERE v.vigente AND v.tipo = %s::tipo_capa AND {{donde}} ORDER BY e.codigo_origen, e.id'''


def leer_bbox(valor: str | None) -> tuple[float, float, float, float] | None:
    """bbox = oeste,sur,este,norte en grados (style form, explode false). None si no se envía."""
    if valor is None:
        return None
    try:
        oeste, sur, este, norte = (float(parte) for parte in valor.split(','))
    except ValueError:
        raise ApiError(400, 'SOLICITUD_MAL_FORMADA', 'bbox debe tener cuatro números: oeste,sur,este,norte') from None
    if not (-180 <= oeste < este <= 180 and -90 <= sur < norte <= 90):
        raise ApiError(400, 'SOLICITUD_MAL_FORMADA',
                       'bbox no es una extensión válida en EPSG:4326 (oeste < este y sur < norte, en grados)')
    return oeste, sur, este, norte


@router.get('/mapa/capas/{capaMapaId}/elementos', tags=['Mapa'],
            responses={200: {'content': {'application/geo+json': {}}}})
def obtener_elementos_capa(capaMapaId: Annotated[CapaMapaId, Path()],
                           bbox: Annotated[str | None, Query(description='oeste,sur,este,norte en EPSG:4326')] = None):
    extension = leer_bbox(bbox)
    if capaMapaId == 'zonas_cambio':
        sql, columna, params = ZONAS_SQL, 'z.geometria', []
    elif capaMapaId == 'alertas_geobosques':
        sql, columna, params = ALERTAS_SQL, 'a.geometria', []
    else:
        sql, columna, params = REFERENCIA_SQL, 'e.geometria', [capaMapaId]
    donde = FILTRO_BBOX.format(col=columna) if extension else 'TRUE'
    filas = db.run(sql.format(donde=donde), (*params, *(extension or ())))
    coleccion = {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'id': fila['id'], 'geometry': json.loads(fila['geometria']),
         'properties': fila['propiedades']} for fila in filas]}
    return JSONResponse(coleccion, media_type='application/geo+json')
