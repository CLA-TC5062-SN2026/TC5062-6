"""Pruebas de integración contra PostgreSQL real (base ecoalert_test de docker-compose)."""
import os

# La configuración se fija antes de importar la app: get_settings() se evalúa al importar app.main.
os.environ['DATABASE_URL'] = os.environ.get(
    'TEST_DATABASE_URL', 'postgresql://ecoalert:ecoalert_dev@localhost:5432/ecoalert_test')
os.environ['JWT_SECRET'] = 'secreto-solo-para-pruebas-automatizadas-0123456789'
os.environ['JWT_EXPIRATION'] = '3600'
os.environ['API_DOCS'] = 'false'

import psycopg  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.security import hashear  # noqa: E402

PASSWORD = 'clave-de-prueba-2026'

assert os.environ['DATABASE_URL'].rsplit('/', 1)[-1].endswith('_test'), \
    'Las pruebas vacían tablas: solo pueden correr contra una base *_test'


@pytest.fixture(scope='session')
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def conn():
    with psycopg.connect(os.environ['DATABASE_URL'], autocommit=True) as c:
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
            (f'Prueba {rol}', correo, rol, activo, debe_cambiar, hash_ or hashear(password)))
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
