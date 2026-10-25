"""Pool de conexiones PostgreSQL y helpers de consulta parametrizada."""
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.errors import fail

pool: ConnectionPool | None = None


def abrir(url: str) -> None:
    global pool
    pool = ConnectionPool(url, min_size=1, max_size=5, open=False, kwargs={'row_factory': dict_row})
    pool.open(wait=True)


def cerrar() -> None:
    if pool is not None:
        pool.close()


def transaccion():
    """Conexión cuyo bloque `with` es una transacción: commit al salir, rollback ante excepción."""
    return pool.connection()


def sql_error(exc):
    if isinstance(exc, UniqueViolation): fail(409, 'Recurso duplicado')
    if isinstance(exc, (CheckViolation, ForeignKeyViolation)): fail(400, 'Los datos violan una restricción de integridad')
    raise exc


def run(sql, params=None, *, one=False):
    with pool.connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                result = cur.fetchone() if one else cur.fetchall() if cur.description else None
            return result
        except (UniqueViolation, CheckViolation, ForeignKeyViolation) as exc:
            sql_error(exc)
