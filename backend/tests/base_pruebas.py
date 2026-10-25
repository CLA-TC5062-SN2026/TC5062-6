"""Preparación común de las suites de pruebas (A1 y A2).

Cada suite trabaja en su propia base `*_test` (nunca en la de desarrollo ni en la de producción):
  A1: `ecoalert_test`      con la semilla de tests/sql/semilla.sql, que ninguna prueba borra.
  A2: `ecoalert_auth_test` vacía; su suite la trunca antes de cada prueba.
Variables (entorno o backend/.env): DATABASE_URL (servidor, usuario y clave), TEST_DB_NAME, TEST_AUTH_DB_NAME,
TEST_DATABASE_URL y TEST_AUTH_DATABASE_URL (URL completa de la base, que también debe terminar en _test).
"""
import os
import re
import secrets
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import psycopg
import pytest
from dotenv import load_dotenv

BACKEND = Path(__file__).resolve().parents[1]
REPO = BACKEND.parent
ESQUEMA = REPO / 'S05_S06_A1' / 'esquema_bd.sql'
_entorno_listo = False


def entorno_de_pruebas():
    """Carga backend/.env y fija la configuración que la app exige al arrancar, sin depender de secretos reales."""
    global _entorno_listo
    if _entorno_listo:
        return
    load_dotenv(BACKEND / '.env')  # no sobrescribe variables ya definidas en el entorno
    os.environ.setdefault('IDEMPOTENCY_SECRET', secrets.token_hex(32))
    os.environ.update(JWT_SECRET=secrets.token_hex(32), JWT_EXPIRATION='3600', SESION_INACTIVIDAD_SEGUNDOS='1800',
                      API_DOCS='false')
    _entorno_listo = True


def url_de_pruebas(nombre_por_defecto, variable_nombre, variable_url):
    """URL de una base de pruebas: reutiliza servidor y credenciales de DATABASE_URL y exige un nombre `*_test`."""
    url = os.environ.get(variable_url)
    if not url:
        base = os.environ.get('DATABASE_URL')
        if not base:
            pytest.exit(f'Define DATABASE_URL (copia backend/.env.example a backend/.env) o {variable_url}.', returncode=2)
        url = urlunsplit(urlsplit(base)._replace(path='/' + os.environ.get(variable_nombre, nombre_por_defecto)))
    nombre = urlsplit(url).path.lstrip('/')
    if not re.fullmatch(r'[a-z][a-z0-9_]*_test', nombre):
        pytest.exit(f'La base de pruebas debe llamarse *_test (minusculas); no se usara "{nombre}".', returncode=2)
    return url


def asegurar_base(url, semilla=None):
    """Crea la base si falta, importa el esquema si está vacía y, si se indica, carga la semilla idempotente."""
    partes = urlsplit(url)
    nombre = partes.path.lstrip('/')  # validado por url_de_pruebas
    with psycopg.connect(urlunsplit(partes._replace(path='/postgres')), autocommit=True) as admin:
        if not admin.execute('SELECT 1 FROM pg_database WHERE datname = %s', (nombre,)).fetchone():
            admin.execute(f'CREATE DATABASE {nombre}')
    with psycopg.connect(url, autocommit=True) as conexion:
        if conexion.execute("SELECT to_regclass('public.usuarios')").fetchone()[0] is None:
            conexion.execute(ESQUEMA.read_text(encoding='utf-8'))
        if semilla is not None:
            conexion.execute(semilla.read_text(encoding='utf-8'))


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
