"""Pruebas HTTP de GET /mapa/capas/{capaMapaId}/elementos (RF-06-AC-2, RF-06-AC-6) con la semilla de pruebas.

Las zonas de la semilla están en UTM 19S cerca de (500000, 8580000), es decir, alrededor de 69°W y 12.8°S.
"""
import pytest

RUTA = '/api/v1/mapa/capas/{}/elementos'


def coordenadas(geometria):
    """Todas las posiciones [lon, lat] de un Point o de un Polygon GeoJSON."""
    if geometria['type'] == 'Point':
        return [geometria['coordinates']]
    return [posicion for anillo in geometria['coordinates'] for posicion in anillo]


def en_tambopata(lon, lat):
    return -70.0 < lon < -68.0 and -14.0 < lat < -12.0


def test_RF_06_AC_2_cada_zona_con_su_geometria_en_4326_codigo_y_nivel(api, conforme):
    r = api('GET', RUTA.format('zonas_cambio'))
    assert r.estado == 200
    assert r.cabeceras['Content-Type'].startswith('application/geo+json')
    conforme('FeatureCollection', r.json)
    zonas = {f['properties']['codigo']: f for f in r.json['features']}
    assert {'EA-2026-001', 'EA-2026-002'} <= zonas.keys()
    uno, dos = zonas['EA-2026-001'], zonas['EA-2026-002']
    assert uno['geometry']['type'] == dos['geometry']['type'] == 'Polygon'
    assert uno['geometry'] != dos['geometry'], 'Cada zona trae su propia geometría'
    assert all(en_tambopata(lon, lat) for f in (uno, dos) for lon, lat in coordenadas(f['geometry'])), \
        'Las coordenadas deben estar en grados (EPSG:4326), no en metros UTM'
    assert (uno['properties']['nivel'], dos['properties']['nivel']) == ('alta', 'baja')
    assert uno['id'] == 'EA-2026-001'


def test_zonas_incluyen_solo_las_marcas_activas(api):
    zonas = {f['properties']['codigo']: f['properties'] for f in api('GET', RUTA.format('zonas_cambio')).json['features']}
    assert [m['texto'] for m in zonas['EA-2026-001']['marcas']] == ['posible actividad minera']
    assert [m['tipo'] for m in zonas['EA-2026-002']['marcas']] == ['area_pequena']


def test_capa_de_alertas_con_codigo_fecha_y_zona(api, conforme):
    r = api('GET', RUTA.format('alertas_geobosques'))
    assert r.estado == 200
    conforme('FeatureCollection', r.json)
    alertas = {f['properties']['codigo']: f for f in r.json['features']}
    assert {'A-1', 'A-2', 'A-3', 'B-1'} <= alertas.keys()
    a3 = alertas['A-3']
    assert a3['geometry']['type'] == 'Point' and en_tambopata(*a3['geometry']['coordinates'])
    assert a3['properties'] == {'codigo': 'A-3', 'fecha_deteccion': '2026-09-20', 'zona_codigo': 'EA-2026-001',
                                'presente_en_ultima_carga': False}


def test_capa_de_referencia_sin_version_vigente_devuelve_coleccion_vacia(api, conforme):
    r = api('GET', RUTA.format('catastro_minero'))
    assert r.estado == 200
    conforme('FeatureCollection', r.json)
    assert r.json['features'] == []


def test_bbox_recorta_por_extension(api):
    # Las dos zonas están separadas 1 km en el eje este; una extensión de 0.005° alrededor de la primera solo la incluye.
    uno = next(f for f in api('GET', RUTA.format('zonas_cambio')).json['features'] if f['id'] == 'EA-2026-001')
    lon, lat = coordenadas(uno['geometry'])[0]
    recorte = api('GET', RUTA.format('zonas_cambio') + f'?bbox={lon - 0.002},{lat - 0.002},{lon + 0.002},{lat + 0.002}')
    assert recorte.estado == 200
    assert [f['id'] for f in recorte.json['features']] == ['EA-2026-001']
    lejos = api('GET', RUTA.format('zonas_cambio') + '?bbox=-75,-10,-74,-9')
    assert lejos.estado == 200 and lejos.json['features'] == []


@pytest.mark.parametrize('consulta', ['bbox=1,2,3', 'bbox=a,b,c,d', 'bbox=-69,-12,-70,-13', 'bbox=-69,-12,-68,-13'])
def test_bbox_invalido_400(api, conforme, consulta):
    r = api('GET', RUTA.format('zonas_cambio') + f'?{consulta}')
    assert r.estado == 400 and r.json['codigo'] == 'SOLICITUD_MAL_FORMADA'
    conforme('Error', r.json)


def test_capa_inexistente_400_y_sin_sesion_401(api, api_base, conforme):
    r = api('GET', RUTA.format('capa_inventada'))
    assert r.estado == 400 and r.json['codigo'] == 'SOLICITUD_MAL_FORMADA'
    sin_sesion = api_base('GET', RUTA.format('zonas_cambio'))
    assert sin_sesion.estado == 401
    conforme('Error', sin_sesion.json)


def test_RF_06_AC_6_catastro_vigente_con_tipo_codigo_y_estado_sin_titular(api, bd, conforme):
    """Solo se publica la versión vigente y nunca el titular, aunque esté en los atributos originales."""
    ana = '00000000-0000-4000-8000-000000000001'
    vigente, antigua = '70000000-0000-4000-8000-000000000001', '70000000-0000-4000-8000-000000000002'
    poligono = "ST_GeomFromText('POLYGON((500000 8581000,500200 8581000,500200 8581200,500000 8581200,500000 8581000))', 32719)"
    bd("INSERT INTO capas_referencia (tipo, nombre, geometria_esperada) VALUES ('catastro_minero', 'Catastro minero', "
       "'poligono') ON CONFLICT DO NOTHING")
    bd('INSERT INTO versiones_capa (id, tipo, fuente, fecha_corte, cargada_por, num_elementos, vigente) VALUES '
       "(%s, 'catastro_minero', 'INGEMMET', '2026-08-01', %s, 1, false), "
       "(%s, 'catastro_minero', 'INGEMMET', '2026-10-01', %s, 1, true)", (antigua, ana, vigente, ana))
    try:
        bd('INSERT INTO elementos_capa (version_capa_id, codigo_origen, tipo_derecho, estado_derecho, atributos, geometria) '
           f"VALUES (%s, 'MIN-ANTIGUA', 'concesion', 'extinguido', '{{}}', {poligono}), "
           f"(%s, '010203-26', 'concesion minera', 'vigente', '{{\"titular\": \"Minera Ejemplo SAC\"}}', {poligono})",
           (antigua, vigente))
        r = api('GET', RUTA.format('catastro_minero'))
        assert r.estado == 200
        conforme('FeatureCollection', r.json)
        assert [f['properties'] for f in r.json['features']] == [
            {'tipo_derecho': 'concesion minera', 'codigo': '010203-26', 'estado': 'vigente', 'fecha_corte': '2026-10-01'}]
        assert 'Minera Ejemplo' not in str(r.json)
    finally:
        bd('DELETE FROM elementos_capa WHERE version_capa_id IN (%s, %s)', (antigua, vigente))
        bd('DELETE FROM versiones_capa WHERE id IN (%s, %s)', (antigua, vigente))
        bd("DELETE FROM capas_referencia WHERE tipo = 'catastro_minero'")
