"""Pruebas del contrato OpenAPI: validez, trazabilidad con el SRS, coherencia con el UML y con las rutas del backend."""
import re

import pytest
from openapi_spec_validator import validate

from conftest import CLASES, SRS

METODOS = ('get', 'put', 'post', 'patch', 'delete')


def operaciones(oas):
    return {(metodo, ruta) for ruta, item in oas['paths'].items() for metodo in METODOS if metodo in item}


def test_openapi_es_valido(oas):
    validate(oas)  # lanza excepcion si el documento no cumple OpenAPI 3.0


def test_operaciones_y_reglas_del_recurso_usuarios(oas):
    ops = operaciones(oas)
    assert len(ops) == 38
    assert {('get', '/usuarios'), ('post', '/usuarios'), ('get', '/usuarios/{usuarioId}'),
            ('put', '/usuarios/{usuarioId}'), ('patch', '/usuarios/{usuarioId}')} <= ops
    assert ('delete', '/usuarios/{usuarioId}') not in ops, 'RF-02-AC-6: las cuentas no se eliminan'
    for ruta, item in oas['paths'].items():
        for metodo in METODOS:
            if metodo in item:
                assert item[metodo].get('x-roles'), f'{metodo.upper()} {ruta} sin x-roles'


def test_put_usuarios_exige_los_tres_campos_y_reutiliza_el_esquema(oas):
    cuerpo = oas['paths']['/usuarios/{usuarioId}']['put']['requestBody']['content']['application/json']['schema']
    referencias = [parte.get('$ref') for parte in cuerpo['allOf'] if '$ref' in parte]
    obligatorios = [parte['required'] for parte in cuerpo['allOf'] if 'required' in parte]
    assert referencias == ['#/components/schemas/UsuarioActualizar']
    assert obligatorios == [['nombre_completo', 'rol', 'activo']]


def test_criterios_de_aceptacion_must_cubiertos(oas):
    texto = SRS.read_text(encoding='utf-8')
    del_srs = set(re.findall(r'\*\*(RF-(?:0[1-9]|1[0-7])-AC-\d+)\*\*', texto))
    del_contrato = set()
    for item in oas['paths'].values():
        for metodo in METODOS:
            operacion = item.get(metodo, {})
            del_contrato |= set(operacion.get('x-acceptance-criteria', [])) | set(operacion.get('x-e2e-support', []))
    assert len(del_srs) == 166
    assert del_srs - del_contrato == set(), 'Criterios del SRS sin operacion'
    assert del_contrato - del_srs == set(), 'Criterios del contrato que no existen en el SRS'


def atributos_uml():
    clases, actual = {}, None
    for linea in CLASES.read_text(encoding='utf-8').splitlines():
        cabecera = re.match(r'\s*(?:abstract class|class|enum)\s+(\w+)', linea)
        if cabecera:
            actual = cabecera.group(1)
            clases[actual] = set()
        elif actual and (atributo := re.match(r'\s*\+(\w+):', linea)):
            clases[actual].add(atributo.group(1))
    return clases


def propiedades(esquema, componentes):
    if '$ref' in esquema:
        return propiedades(componentes[esquema['$ref'].rsplit('/', 1)[1]], componentes)
    props = set(esquema.get('properties', {}))
    for parte in esquema.get('allOf', []):
        props |= propiedades(parte, componentes)
    return props


def test_schemas_y_clases_uml_coinciden(oas):
    esquemas = oas['components']['schemas']
    clases = atributos_uml()
    assert set(esquemas) == set(clases) and len(esquemas) == 62
    for nombre, esquema in esquemas.items():
        if esquema.get('type') == 'object' or 'properties' in esquema:
            assert propiedades(esquema, esquemas) == clases[nombre], f'Atributos distintos en {nombre}'


def test_rutas_del_backend_estan_en_el_contrato(oas):
    from app.main import app  # exige IDEMPOTENCY_SECRET (definido en conftest); no abre conexiones
    backend = {(metodo, ruta.removeprefix('/api/v1'))
               for ruta, item in app.openapi()['paths'].items() if ruta.startswith('/api/v1')
               for metodo in METODOS if metodo in item}
    assert ('put', '/usuarios/{usuarioId}') in backend
    assert backend <= operaciones(oas), f'Rutas implementadas fuera del contrato: {sorted(backend - operaciones(oas))}'
    assert len(backend) == 15
