"""Pruebas del contrato OpenAPI integrado: validez, trazabilidad con el SRS, relación con los contratos originales de
A1 y A2 (que no se modifican), coherencia con el UML de A2 y con las rutas del backend."""
import re

import pytest
import yaml
from openapi_spec_validator import validate

from tests.conftest import CLASES, OPENAPI_A1, OPENAPI_A2, SRS

METODOS = ('get', 'put', 'post', 'patch', 'delete')
SESION_A1 = {('post', '/auth/sesion'), ('get', '/auth/sesion'), ('delete', '/auth/sesion')}


def operaciones(oas):
    return {(metodo, ruta) for ruta, item in oas['paths'].items() for metodo in METODOS if metodo in item}


def cargar(ruta):
    return yaml.safe_load(ruta.read_text(encoding='utf-8'))


def test_openapi_es_valido(oas):
    validate(oas)  # lanza excepcion si el documento no cumple OpenAPI 3.0


def test_operaciones_y_reglas_del_recurso_usuarios(oas):
    ops = operaciones(oas)
    assert len(ops) == 39
    assert {('get', '/usuarios'), ('post', '/usuarios'), ('get', '/usuarios/{usuarioId}'),
            ('put', '/usuarios/{usuarioId}'), ('patch', '/usuarios/{usuarioId}')} <= ops
    assert ('delete', '/usuarios/{usuarioId}') not in ops, 'RF-02-AC-7: las cuentas no se eliminan'
    for ruta, item in oas['paths'].items():
        for metodo in METODOS:
            if metodo in item:
                assert item[metodo].get('x-roles'), f'{metodo.upper()} {ruta} sin x-roles'


def test_contrato_integrado_conserva_las_operaciones_de_a1_y_a2(oas):
    a1, a2 = cargar(OPENAPI_A1), cargar(OPENAPI_A2)
    ops, ops_a1, ops_a2 = operaciones(oas), operaciones(a1), operaciones(a2)
    assert ops == (ops_a1 - SESION_A1) | ops_a2, 'El integrado = A1 sin /auth/sesion + A2'
    for original in (a1, a2):
        for metodo, ruta in operaciones(original) & ops:
            antes, ahora = original['paths'][ruta][metodo], oas['paths'][ruta][metodo]
            for campo in ('operationId', 'x-roles', 'x-acceptance-criteria', 'x-e2e-support'):
                assert ahora.get(campo) == antes.get(campo), f'{metodo.upper()} {ruta}: cambió {campo}'


def test_schemas_del_integrado_difieren_de_los_originales_solo_donde_se_documenta(oas):
    esquemas = oas['components']['schemas']
    a1, a2 = cargar(OPENAPI_A1)['components']['schemas'], cargar(OPENAPI_A2)['components']['schemas']
    assert set(esquemas) == set(a1) == set(a2)
    # A2 cambió el login (correo, expires_in); la integración añade los límites de longitud de contraseña.
    assert {n for n in esquemas if esquemas[n] != a1[n]} == {'CredencialesLogin', 'SesionCreada', 'CambioPassword',
                                                             'UsuarioCrear'}
    assert {n for n in esquemas if esquemas[n] != a2[n]} == {'CredencialesLogin', 'CambioPassword', 'UsuarioCrear'}


def test_put_usuarios_exige_los_tres_campos_y_reutiliza_el_esquema(oas):
    cuerpo = oas['paths']['/usuarios/{usuarioId}']['put']['requestBody']['content']['application/json']['schema']
    referencias = [parte.get('$ref') for parte in cuerpo['allOf'] if '$ref' in parte]
    obligatorios = [parte['required'] for parte in cuerpo['allOf'] if 'required' in parte]
    assert referencias == ['#/components/schemas/UsuarioActualizar']
    assert obligatorios == [['nombre_completo', 'rol', 'activo']]


def test_register_es_alias_de_crear_usuario_con_idempotency_key(oas):
    registrar, crear = oas['paths']['/auth/register']['post'], oas['paths']['/usuarios']['post']
    assert registrar['x-alias-de'] == crear['operationId'] and registrar['x-roles'] == crear['x-roles'] == ['coordinacion']
    assert {'$ref': '#/components/parameters/IdempotencyKey'} in registrar['parameters']


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
    from app.main import app  # no abre conexiones: la base solo se usa al arrancar (lifespan)
    backend = {(metodo, ruta.removeprefix('/api/v1'))
               for ruta, item in app.openapi()['paths'].items() if ruta.startswith('/api/v1')
               for metodo in METODOS if metodo in item}
    assert {('put', '/usuarios/{usuarioId}'), ('post', '/auth/login'), ('post', '/auth/register')} <= backend
    assert backend <= operaciones(oas), f'Rutas implementadas fuera del contrato: {sorted(backend - operaciones(oas))}'
    assert len(backend) == 20  # 15 de A1 + login, register, me, logout y cambio de contraseña de A2
