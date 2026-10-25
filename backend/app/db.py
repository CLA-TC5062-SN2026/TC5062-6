"""Acceso a PostgreSQL: pool de conexiones, consultas parametrizadas e idempotencia de los POST."""
import hashlib
import hmac
import json
import os
from contextlib import contextmanager
from uuid import UUID

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from .errors import ApiError

pool: ConnectionPool | None = None

# Sin valor por defecto: el secreto nunca debe estar en el código ni en Git.
IDEMPOTENCY_SECRET = os.environ.get('IDEMPOTENCY_SECRET')
if not IDEMPOTENCY_SECRET:
    raise RuntimeError('Falta la variable de entorno IDEMPOTENCY_SECRET (ver backend/.env.example).')


def abrir(url: str) -> None:
    global pool
    pool = ConnectionPool(url, min_size=1, max_size=5, open=False, kwargs={'row_factory': dict_row})
    pool.open(wait=True)


def cerrar() -> None:
    if pool is not None:
        pool.close()


@contextmanager
def transaction():
    """Conexión con commit al salir y rollback ante cualquier excepción."""
    with pool.connection() as conn:
        yield conn


def query(conn, sql, params=(), *, one=False):
    cur = conn.execute(sql, params)
    if not cur.description:
        return None
    return cur.fetchone() if one else cur.fetchall()


def run(sql, params=(), *, one=False):
    with transaction() as conn:
        return query(conn, sql, params, one=one)


def huella(cuerpo: dict) -> str:
    """HMAC-SHA256 del cuerpo completo en JSON canónico; sin el secreto no se puede derivar la contraseña de la huella."""
    canonico = json.dumps(cuerpo, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hmac.new(IDEMPOTENCY_SECRET.encode(), canonico.encode(), hashlib.sha256).hexdigest()


def respuesta_previa(conn, clave: UUID, operacion: str, huella_cuerpo: str):
    """Serializa los reintentos de una clave y devuelve la respuesta guardada, si existe (24 h)."""
    query(conn, 'SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))', (str(clave),))
    query(conn, "DELETE FROM claves_idempotencia WHERE creada_en < now() - interval '24 hours'")
    previa = query(conn, 'SELECT operacion, huella, estado_http, cuerpo_respuesta, location '
                         'FROM claves_idempotencia WHERE clave=%s', (clave,), one=True)
    if previa and not (previa['operacion'] == operacion and hmac.compare_digest(previa['huella'], huella_cuerpo)):
        raise ApiError(422, 'IDEMPOTENCIA_CONFLICTO', 'La clave de idempotencia ya se usó con otra solicitud')
    return previa


def guardar_respuesta(conn, clave: UUID, operacion: str, huella_cuerpo: str, estado_http: int, cuerpo: dict, location: str):
    query(conn, 'INSERT INTO claves_idempotencia (clave, operacion, huella, estado_http, cuerpo_respuesta, location) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
          (clave, operacion, huella_cuerpo, estado_http, Jsonb(cuerpo), location))
