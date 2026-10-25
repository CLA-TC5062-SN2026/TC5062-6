"""Pruebas de integración de A2 (JWT, sesiones y protección de rutas) contra PostgreSQL real.

Usan su propia base `*_test` (por defecto `ecoalert_auth_test`, separada de la de A1): antes de cada prueba vacían
`usuarios` y `sesiones` (CASCADE), así que nunca comparten base con la semilla de A1 ni apuntan a desarrollo o producción.
Se ejecutan desde backend con `python -m pytest` (junto con las de A1) o solas: `python -m pytest ../S05_S06_A2/pruebas`.
"""
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))

import psycopg  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from tests.base_pruebas import asegurar_base, entorno_de_pruebas, url_de_pruebas  # noqa: E402

# La configuración se fija antes de importar la app: get_settings() se evalúa al importar app.main.
entorno_de_pruebas()
URL = url_de_pruebas('ecoalert_auth_test', 'TEST_AUTH_DB_NAME', 'TEST_AUTH_DATABASE_URL')
URL_A1 = url_de_pruebas('ecoalert_test', 'TEST_DB_NAME', 'TEST_DATABASE_URL')
assert urlsplit(URL).path != urlsplit(URL_A1).path, \
    'La base de A2 se trunca antes de cada prueba: no puede ser la base sembrada de A1'
os.environ['DATABASE_URL'] = URL

from app.main import app  # noqa: E402
from app.security import hashear  # noqa: E402

PASSWORD = 'clave-de-prueba-2026'


@pytest.fixture(scope='session', autouse=True)
def base_auth():
    asegurar_base(URL)


@pytest.fixture(scope='session')
def client(base_auth):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def conn():
    with psycopg.connect(URL, autocommit=True) as c:
        yield c


@pytest.fixture(autouse=True)
def base_limpia(conn):
    conn.execute('TRUNCATE usuarios, sesiones CASCADE')


@pytest.fixture
def crear_cuenta(conn):
    def _crear(rol='analista_sig', *, correo=None, activo=True, debe_cambiar=False, password=PASSWORD,
               hash_=None):
        correo = correo or f'{rol}.{os.urandom(4).hex()}@ecoalert.pe'
        conn.execute(
            '''INSERT INTO usuarios (nombre_completo, correo, rol, activo, debe_cambiar_password, password_hash)
               VALUES (%s,%s,%s,%s,%s,%s)''',
            (f'Prueba {rol}', correo, rol, activo, debe_cambiar, hashear(password) if hash_ is None else hash_))
        return correo
    return _crear


@pytest.fixture
def login(client):
    def _login(correo, password=PASSWORD):
        r = client.post('/api/v1/auth/login', json={'correo': correo, 'password': password})
        assert r.status_code == 200, r.text
        return r.json()['access_token']
    return _login


@pytest.fixture
def token_coordinacion(crear_cuenta, login):
    return login(crear_cuenta('coordinacion'))


@pytest.fixture
def token_analista(crear_cuenta, login):
    return login(crear_cuenta('analista_sig'))


def bearer(token):
    return {'Authorization': f'Bearer {token}'}


def con_clave(token):
    """Cabeceras de una operación de creación: token y una Idempotency-Key nueva (obligatoria en A1)."""
    return {**bearer(token), 'Idempotency-Key': str(uuid.uuid4())}


MERGE_PATCH = {'Content-Type': 'application/merge-patch+json'}
