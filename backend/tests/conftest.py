"""Fixtures de las pruebas: base aislada `*_test`, API levantada por pytest, cliente HTTP y validacion OpenAPI.

Configuracion (variables de entorno o backend/.env; ver backend/README.md):
  DATABASE_URL       conexion del servidor PostgreSQL (se reutilizan usuario, clave y host).
  TEST_DB_NAME       base de pruebas (por defecto ecoalert_test). Debe terminar en _test.
  TEST_DATABASE_URL  alternativa: URL completa de la base de pruebas (tambien debe terminar en _test).
  API_BASE_URL       opcional: usar una API ya levantada (debe apuntar a la base de pruebas; se verifica).
"""
import copy
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import namedtuple
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import psycopg
import pytest
import yaml
from dotenv import load_dotenv
from openapi_schema_validator import OAS30Validator

BACKEND = Path(__file__).resolve().parents[1]
REPO = BACKEND.parent
DISENO = REPO / 'S05_S06_A1'
ESQUEMA = DISENO / 'esquema_bd.sql'
OPENAPI = DISENO / 'openapi_equipo.yaml'
CLASES = DISENO / 'diagrama_clases_equipo.puml'
SRS = REPO / 'S03_A1' / 'SRS_equipo.md'
SQL = Path(__file__).parent / 'sql'

load_dotenv(BACKEND / '.env')  # no sobrescribe variables ya definidas en el entorno
# Si el entorno no define el secreto de idempotencia, se usa uno efimero (solo en memoria).
os.environ.setdefault('IDEMPOTENCY_SECRET', secrets.token_hex(32))

Respuesta = namedtuple('Respuesta', 'estado cabeceras json')


def leer_sql(nombre):
    return (SQL / nombre).read_text(encoding='utf-8')


def ejecutar_script(url, texto):
    """Ejecuta un script de varias sentencias y devuelve las filas del ultimo SELECT."""
    with psycopg.connect(url, autocommit=True) as conexion:
        cursor = conexion.cursor()
        cursor.execute(texto)
        filas = []
        while True:
            if cursor.description:
                filas = cursor.fetchall()
            if not cursor.nextset():
                break
    return filas


@pytest.fixture(scope='session')
def url_bd():
    """URL de la base de pruebas; la crea, importa el esquema y carga la semilla si hace falta."""
    url = os.environ.get('TEST_DATABASE_URL')
    if not url:
        base = os.environ.get('DATABASE_URL')
        if not base:
            pytest.exit('Define DATABASE_URL (copia backend/.env.example a backend/.env) o TEST_DATABASE_URL.', returncode=2)
        url = urlunsplit(urlsplit(base)._replace(path='/' + os.environ.get('TEST_DB_NAME', 'ecoalert_test')))
    partes = urlsplit(url)
    nombre = partes.path.lstrip('/')
    if not re.fullmatch(r'[a-z][a-z0-9_]*_test', nombre):
        pytest.exit(f'La base de pruebas debe llamarse *_test (minusculas); no se usara "{nombre}".', returncode=2)
    with psycopg.connect(urlunsplit(partes._replace(path='/postgres')), autocommit=True) as admin:
        if not admin.execute('SELECT 1 FROM pg_database WHERE datname = %s', (nombre,)).fetchone():
            admin.execute(f'CREATE DATABASE {nombre}')  # nombre validado con la expresion regular anterior
    with psycopg.connect(url, autocommit=True) as conexion:
        if conexion.execute("SELECT to_regclass('public.usuarios')").fetchone()[0] is None:
            conexion.execute(ESQUEMA.read_text(encoding='utf-8'))
        conexion.execute(leer_sql('semilla.sql'))
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


def _puerto_libre():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@pytest.fixture(scope='session')
def api(url_bd, bd, tmp_path_factory):
    """Cliente HTTP de la API. Levanta uvicorn contra la base de pruebas salvo que se defina API_BASE_URL."""
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
    visibles_api = cliente('GET', '/api/v1/alertas?limite=1').json['total']
    visibles_bd = bd('SELECT count(*) FROM alertas WHERE zona_codigo IS NOT NULL AND area_ha IS NOT NULL')[0][0]
    if visibles_bd == 0 or visibles_api != visibles_bd:
        pytest.exit('La API no apunta a la base de pruebas (alertas visibles distintas); se cancelan las pruebas de escritura.', returncode=2)
    yield cliente
    if proceso is not None:
        proceso.terminate()
        proceso.wait(timeout=15)


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
    """crear_usuario(**cambios) -> (respuesta, cuerpo enviado). Correo unico por llamada."""
    def crear(clave=None, **cambios):
        cuerpo = {'nombre_completo': 'Usuario de Prueba', 'correo': f'p.{uuid.uuid4().hex[:12]}@ecoalert.pe',
                  'rol': 'analista_sig', 'password_temporal': 'Temporal-2026'}
        cuerpo.update(cambios)
        return api('POST', '/api/v1/usuarios', cuerpo, {'Idempotency-Key': clave or str(uuid.uuid4())}), cuerpo
    return crear
