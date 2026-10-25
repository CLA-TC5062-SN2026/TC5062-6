"""Pruebas HTTP de las lecturas implementadas (alertas, cargas, marcas, ajustes, historial, trabajos).

Dependen de los datos controlados de tests/sql/semilla.sql y comprueban cada respuesta contra el esquema del OpenAPI.
"""
import uuid

import pytest

API = '/api/v1'
ZONA = 'EA-2026-001'
ZONA_MENOR = 'EA-2026-002'
CARGA_1 = '20000000-0000-4000-8000-000000000001'
CARGA_2 = '20000000-0000-4000-8000-000000000002'
MARCA_ACTIVA = '30000000-0000-4000-8000-000000000002'
AJUSTE_VIGENTE = '40000000-0000-4000-8000-000000000002'
HISTORIAL_CREACION = '50000000-0000-4000-8000-000000000001'
TRABAJO_OK = '60000000-0000-4000-8000-000000000001'
TRABAJO_FALLIDO = '60000000-0000-4000-8000-000000000002'


def es_problema(respuesta, estado, codigo, conforme):
    assert respuesta.estado == estado
    assert respuesta.cabeceras['Content-Type'].startswith('application/problem+json')
    conforme('Error', respuesta.json)
    assert respuesta.json['codigo'] == codigo


# --------------------------------------------------------------------------- alertas

def test_alertas_pagina_conforme_y_solo_alertas_publicables(api, bd, conforme):
    r = api('GET', f'{API}/alertas')
    assert r.estado == 200
    conforme('PaginaAlertas', r.json)
    publicables = bd('SELECT count(*) FROM alertas WHERE zona_codigo IS NOT NULL AND area_ha IS NOT NULL')[0][0]
    assert r.json['total'] == publicables == len(r.json['alertas'])
    codigos = {a['codigo'] for a in r.json['alertas']}
    assert {'SIN-ZONA', 'SIN-AREA'}.isdisjoint(codigos), 'El contrato exige zona y area en toda alerta'
    fechas = [a['fecha_deteccion'] for a in r.json['alertas']]
    assert fechas == sorted(fechas, reverse=True)


def test_alertas_paginacion_y_filtros(api, conforme):
    total = api('GET', f'{API}/alertas').json['total']
    primera = api('GET', f'{API}/alertas?limite=2')
    segunda = api('GET', f'{API}/alertas?limite=2&desplazamiento=2')
    assert (primera.json['limite'], len(primera.json['alertas']), primera.json['total']) == (2, 2, total)
    assert segunda.json['desplazamiento'] == 2
    assert {a['id'] for a in primera.json['alertas']}.isdisjoint({a['id'] for a in segunda.json['alertas']})
    por_zona = api('GET', f'{API}/alertas?zona={ZONA}')
    assert por_zona.json['total'] == 3 and {a['zona_codigo'] for a in por_zona.json['alertas']} == {ZONA}
    ausentes = api('GET', f'{API}/alertas?presente_en_ultima_carga=false')
    assert ausentes.json['total'] == 1 and ausentes.json['alertas'][0]['codigo'] == 'A-3'
    vacia = api('GET', f'{API}/alertas?zona=EA-2099-999')
    assert vacia.estado == 200 and vacia.json['total'] == 0 and vacia.json['alertas'] == []


@pytest.mark.parametrize('consulta', ['limite=0', 'limite=501', 'limite=abc', 'desplazamiento=-1', 'zona=ZONA-1',
                                      'presente_en_ultima_carga=quizas'])
def test_alertas_parametros_invalidos_400(api, conforme, consulta):
    es_problema(api('GET', f'{API}/alertas?{consulta}'), 400, 'SOLICITUD_MAL_FORMADA', conforme)


# --------------------------------------------------------------------------- cargas de alertas

def test_cargas_lista_ordenada_y_detalle_conforme(api, conforme):
    r = api('GET', f'{API}/cargas-alertas')
    assert r.estado == 200
    for carga in r.json:
        conforme('CargaAlertas', carga)
    ids = [c['id'] for c in r.json]
    assert ids.index(CARGA_2) < ids.index(CARGA_1), 'Mas reciente primero'
    detalle = api('GET', f'{API}/cargas-alertas/{CARGA_1}')
    assert detalle.estado == 200 and detalle.json == next(c for c in r.json if c['id'] == CARGA_1)
    assert detalle.json['cargada_por'] == {'id': '00000000-0000-4000-8000-000000000001', 'nombre_completo': 'Ana Quispe Mamani'}
    assert api('GET', f'{API}/cargas-alertas/{CARGA_2}').json['resumen'] == ''


def test_cargas_404_y_400(api, conforme):
    es_problema(api('GET', f'{API}/cargas-alertas/{uuid.uuid4()}'), 404, 'NO_ENCONTRADO', conforme)
    es_problema(api('GET', f'{API}/cargas-alertas/no-es-uuid'), 400, 'SOLICITUD_MAL_FORMADA', conforme)


# --------------------------------------------------------------------------- marcas

def test_marcas_solo_activas_por_defecto_e_incluye_retiradas_si_se_pide(api, conforme):
    activas = api('GET', f'{API}/zonas/{ZONA}/marcas')
    todas = api('GET', f'{API}/zonas/{ZONA}/marcas?incluir_retiradas=true')
    assert activas.estado == todas.estado == 200
    for marca in todas.json:
        conforme('Marca', marca)
    assert [m['id'] for m in activas.json] == [MARCA_ACTIVA]
    assert len(todas.json) == 2 and {m['activa'] for m in todas.json} == {True, False}
    retirada = next(m for m in todas.json if not m['activa'])
    assert retirada['motivo_retiro'] and retirada['retirada_por']['nombre_completo'] == 'Ana Quispe Mamani'


def test_marca_automatica_no_tiene_autor_y_el_detalle_coincide(api, conforme):
    marca = api('GET', f'{API}/zonas/{ZONA_MENOR}/marcas').json[0]
    conforme('Marca', marca)
    assert (marca['origen'], marca['tipo']) == ('automatica', 'area_pequena') and 'creada_por' not in marca
    assert api('GET', f"{API}/zonas/{ZONA_MENOR}/marcas/{marca['id']}").json == marca
    es_problema(api('GET', f'{API}/zonas/{ZONA}/marcas/{marca["id"]}'), 404, 'NO_ENCONTRADO', conforme)


# --------------------------------------------------------------------------- ajustes

def test_ajustes_lista_mas_reciente_primero_y_detalle(api, conforme):
    r = api('GET', f'{API}/zonas/{ZONA}/ajustes')
    assert r.estado == 200 and len(r.json) == 2
    for ajuste in r.json:
        conforme('AjustePrioridad', ajuste)
    assert r.json[0]['id'] == AJUSTE_VIGENTE and r.json[0]['estado'] == 'vigente'
    assert (r.json[0]['forma'], r.json[0]['nivel_elegido']) == ('por_nivel', 'alta')
    assert api('GET', f'{API}/zonas/{ZONA}/ajustes/{AJUSTE_VIGENTE}').json == r.json[0]
    es_problema(api('GET', f'{API}/zonas/{ZONA_MENOR}/ajustes/{AJUSTE_VIGENTE}'), 404, 'NO_ENCONTRADO', conforme)


# --------------------------------------------------------------------------- historial

def test_historial_cronologico_con_autor_sistema(api, conforme):
    r = api('GET', f'{API}/zonas/{ZONA}/historial')
    assert r.estado == 200 and len(r.json) == 4
    for entrada in r.json:
        conforme('EntradaHistorial', entrada)
    fechas = [e['fecha_hora'] for e in r.json]
    assert fechas == sorted(fechas), 'Orden ascendente: la primera entrada es la creacion de la zona'
    primera = r.json[0]
    assert primera['id'] == HISTORIAL_CREACION and primera['tipo_accion'] == 'zona_creada'
    assert primera['autor'] == {'tipo': 'sistema', 'nombre': 'Sistema'}
    assert all(e['autor']['tipo'] == 'usuario' for e in r.json[1:])
    assert api('GET', f'{API}/zonas/{ZONA}/historial/{HISTORIAL_CREACION}').json == primera


# --------------------------------------------------------------------------- trabajos

def test_trabajos_completado_y_fallido(api, conforme):
    ok = api('GET', f'{API}/trabajos/{TRABAJO_OK}')
    fallido = api('GET', f'{API}/trabajos/{TRABAJO_FALLIDO}')
    for r in (ok, fallido):
        assert r.estado == 200
        conforme('Trabajo', r.json)
    assert (ok.json['estado'], fallido.json['estado']) == ('completado', 'fallido')
    assert ok.json['resultado']['carga_alertas_id'] == CARGA_1
    assert fallido.json['error']['codigo'] == 'GEOMETRIA_NO_VALIDA'


# --------------------------------------------------------------------------- 404 y 400 comunes

@pytest.mark.parametrize('ruta', ['zonas/EA-2099-777/marcas', 'zonas/EA-2099-777/ajustes', 'zonas/EA-2099-777/historial'])
def test_zona_inexistente_404(api, conforme, ruta):
    es_problema(api('GET', f'{API}/{ruta}'), 404, 'NO_ENCONTRADO', conforme)


@pytest.mark.parametrize('ruta', ['zonas/ABC/marcas', 'zonas/EA-26-1/historial', f'zonas/{ZONA}/ajustes/no-es-uuid',
                                  'trabajos/no-es-uuid'])
def test_parametros_de_ruta_invalidos_400(api, conforme, ruta):
    es_problema(api('GET', f'{API}/{ruta}'), 400, 'SOLICITUD_MAL_FORMADA', conforme)


def test_trabajo_inexistente_404_y_ruta_desconocida(api, conforme):
    es_problema(api('GET', f'{API}/trabajos/{uuid.uuid4()}'), 404, 'NO_ENCONTRADO', conforme)
    es_problema(api('GET', f'{API}/no-existe'), 404, 'NO_ENCONTRADO', conforme)
