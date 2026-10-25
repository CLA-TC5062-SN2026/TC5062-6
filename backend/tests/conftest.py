"""Fixtures de las pruebas de A1 (con la autenticación JWT de A2): base `ecoalert_test` sembrada, API levantada
por pytest, sesiones autenticadas y validacion OpenAPI.

Configuracion (variables de entorno o backend/.env; ver backend/README.md y tests/base_pruebas.py):
  DATABASE_URL       conexion del servidor PostgreSQL (se reutilizan usuario, clave y host).
  TEST_DB_NAME       base de pruebas de A1 (por defecto ecoalert_test). Debe terminar en _test.
  TEST_DATABASE_URL  alternativa: URL completa de la base de pruebas (tambien debe terminar en _test).
  API_BASE_URL       opcional: usar una API ya levantada (debe apuntar a la base de pruebas; se verifica).
"""
import copy
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import namedtuple
from pathlib import Path

import psycopg
import pytest
import yaml
from openapi_schema_validator import OAS30Validator

from tests.base_pruebas import BACKEND, REPO, asegurar_base, entorno_de_pruebas, url_de_pruebas

entorno_de_pruebas()

from app.security import hashear  # noqa: E402

OPENAPI = REPO / 'S05_S06_integracion' / 'openapi_integrado.yaml'
OPENAPI_A1 = REPO / 'S05_S06_A1' / 'openapi_equipo.yaml'
OPENAPI_A2 = REPO / 'S05_S06_A2' / 'openapi_equipo.yaml'
CLASES = REPO / 'S05_S06_A2' / 'diagrama_clases_equipo.puml'
SRS = REPO / 'S03_A1' / 'SRS_equipo.md'
SQL = Path(__file__).parent / 'sql'
PASSWORD = 'clave-de-prueba-2026'

Respuesta = namedtuple('Respuesta', 'estado cabeceras json')


def leer_sql(nombre):
    return (SQL / nombre).read_text(encoding='utf-8')


@pytest.fixture(scope='session')
def url_bd():
    """URL de la base de pruebas de A1; la crea, importa el esquema y carga la semilla si hace falta."""
    url = url_de_pruebas('ecoalert_test', 'TEST_DB_NAME', 'TEST_DATABASE_URL')
    asegurar_base(url, SQL / 'semilla.sql')
    return url


@pytest.fixture(scope='session')
def bd(url_bd):
    """Ejecuta SQL en la base de pruebas: bd(sql, params) -> filas (o None si no devuelve filas)."""
    def ejecutar(sql, params=None):
        with psycopg.connect(url_bd, autocommit=True) as conexion:
            cursor = conexion.execute(sql, params)
            return cursor.fetchall() if cursor.description else None
    return ejecutar


class Cliente:
    def __init__(self, base):
        self.base = base

    def __call__(self, metodo, ruta, cuerpo=None, cabeceras=None, crudo=None):
        datos = crudo if crudo is not None else (json.dumps(cuerpo).encode() if cuerpo is not None else None)
        cabeceras = dict(cabeceras or {})
        if datos is not None:
            cabeceras.setdefault('Content-Type', 'application/json')
        peticion = urllib.request.Request(self.base + ruta, data=datos, method=metodo, headers=cabeceras)
        try:
            with urllib.request.urlopen(peticion, timeout=30) as respuesta:
                estado, encabezados, texto = respuesta.status, respuesta.headers, respuesta.read()
        except urllib.error.HTTPError as error:
            estado, encabezados, texto = error.code, error.headers, error.read()
        return Respuesta(estado, encabezados, json.loads(texto) if texto else None)


class Sesion:
    """Cliente HTTP autenticado: añade el token Bearer y expone la cuenta (id, correo, rol)."""

    def __init__(self, cliente, token, usuario):
        self.cliente, self.token, self.usuario = cliente, token, usuario

    def __call__(self, metodo, ruta, cuerpo=None, cabeceras=None, crudo=None):
        return self.cliente(metodo, ruta, cuerpo, {'Authorization': f'Bearer {self.token}', **(cabeceras or {})}, crudo)

    @property
    def id(self):
        return self.usuario['id']


def _puerto_libre():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def _insertar_cuenta(bd, rol='coordinacion', *, activo=True, debe_cambiar=False, password=PASSWORD, hash_=None):
    correo = f'{rol}.{uuid.uuid4().hex[:10]}@ecoalert.pe'
    bd('INSERT INTO usuarios (nombre_completo, correo, rol, activo, debe_cambiar_password, password_hash) '
       'VALUES (%s, %s, %s, %s, %s, %s)', (f'Prueba {rol}', correo, rol, activo, debe_cambiar,
                                           hashear(password) if hash_ is None else hash_))
    return correo


@pytest.fixture(scope='session')
def api_base(url_bd, bd, tmp_path_factory):
    """Cliente HTTP sin credenciales. Levanta uvicorn contra la base de pruebas salvo que se defina API_BASE_URL."""
    externa = os.environ.get('API_BASE_URL')
    proceso = None
    if externa:
        base = externa.rstrip('/')
    else:
        base = f'http://127.0.0.1:{_puerto_libre()}'
        entorno = {**os.environ, 'DATABASE_URL': url_bd}
        registro = open(tmp_path_factory.mktemp('api') / 'uvicorn.log', 'w')
        proceso = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'app.main:app', '--port', base.rsplit(':', 1)[1]],
            cwd=BACKEND, env=entorno, stdout=registro, stderr=subprocess.STDOUT)
    cliente = Cliente(base)
    for _ in range(80):
        if proceso is not None and proceso.poll() is not None:
            pytest.exit('uvicorn termino antes de responder; revisa su registro en el directorio temporal de pytest.', returncode=2)
        try:
            if cliente('GET', '/salud').estado == 200:
                break
        except OSError:
            time.sleep(0.25)
    else:
        pytest.exit('La API no respondio en /salud.', returncode=2)
    # Proteccion: la API debe leer la base de pruebas (el total de alertas visibles coincide con la base).
    correo = _insertar_cuenta(bd)
    acceso = cliente('POST', '/api/v1/auth/login', {'correo': correo, 'password': PASSWORD})
    if acceso.estado != 200:
        pytest.exit('El login de la API fallo con una cuenta de prueba; se cancelan las pruebas.', returncode=2)
    visibles_api = cliente('GET', '/api/v1/alertas?limite=1',
                           cabeceras={'Authorization': f"Bearer {acceso.json['access_token']}"}).json['total']
    visibles_bd = bd('SELECT count(*) FROM alertas WHERE zona_codigo IS NOT NULL AND area_ha IS NOT NULL')[0][0]
    if visibles_bd == 0 or visibles_api != visibles_bd:
        pytest.exit('La API no apunta a la base de pruebas (alertas visibles distintas); se cancelan las pruebas de escritura.', returncode=2)
    yield cliente
    if proceso is not None:
        proceso.terminate()
        proceso.wait(timeout=15)


@pytest.fixture
def nueva_cuenta(bd):
    """nueva_cuenta(rol, activo=, debe_cambiar=, password=, hash_=) -> correo de una cuenta con contraseña conocida."""
    return lambda rol='coordinacion', **opciones: _insertar_cuenta(bd, rol, **opciones)


@pytest.fixture
def iniciar_sesion(api_base):
    """iniciar_sesion(correo, password=) -> Sesion autenticada por el login real de la API."""
    def iniciar(correo, password=PASSWORD):
        r = api_base('POST', '/api/v1/auth/login', {'correo': correo, 'password': password})
        assert r.estado == 200, r.json
        return Sesion(api_base, r.json['access_token'], r.json['usuario'])
    return iniciar


@pytest.fixture
def abrir_sesion(nueva_cuenta, iniciar_sesion):
    """abrir_sesion(rol) -> Sesion de una cuenta nueva con ese rol (contraseña ya definitiva)."""
    return lambda rol='coordinacion': iniciar_sesion(nueva_cuenta(rol))


@pytest.fixture
def api(abrir_sesion):
    """Sesión de una cuenta de Coordinación nueva: autoriza todas las operaciones implementadas."""
    return abrir_sesion('coordinacion')


@pytest.fixture
def api_analista(abrir_sesion):
    return abrir_sesion('analista_sig')


@pytest.fixture(scope='session')
def oas():
    return yaml.safe_load(OPENAPI.read_text(encoding='utf-8'))


def _normalizar(nodo):
    """`allOf` + `nullable` es ambiguo en OAS 3.0.3: se valida el esquema referenciado sin `nullable` en el envoltorio."""
    if isinstance(nodo, dict):
        if 'allOf' in nodo and nodo.get('nullable') is True and len(nodo['allOf']) == 1:
            return {'oneOf': [{'enum': [None]}, _normalizar(nodo['allOf'][0])]}
        return {clave: _normalizar(valor) for clave, valor in nodo.items()}
    if isinstance(nodo, list):
        return [_normalizar(elemento) for elemento in nodo]
    return nodo


@pytest.fixture(scope='session')
def conforme(oas):
    """conforme('Usuario', instancia): valida la instancia contra components.schemas del OpenAPI."""
    componentes = _normalizar(copy.deepcopy(oas['components']))

    def validar(nombre, instancia):
        validador = OAS30Validator({'$ref': f'#/components/schemas/{nombre}', 'components': componentes})
        errores = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in validador.iter_errors(instancia)]
        assert not errores, f'{nombre} no cumple el contrato: {errores[:3]}'
    return validar


@pytest.fixture
def crear_usuario(api):
    """crear_usuario(**cambios) -> (respuesta, cuerpo enviado). Correo unico por llamada; lo crea la sesión `api`."""
    def crear(clave=None, **cambios):
        cuerpo = {'nombre_completo': 'Usuario de Prueba', 'correo': f'p.{uuid.uuid4().hex[:12]}@ecoalert.pe',
                  'rol': 'analista_sig', 'password_temporal': 'Temporal-2026'}
        cuerpo.update(cambios)
        return api('POST', '/api/v1/usuarios', cuerpo, {'Idempotency-Key': clave or str(uuid.uuid4())}), cuerpo
    return crear
