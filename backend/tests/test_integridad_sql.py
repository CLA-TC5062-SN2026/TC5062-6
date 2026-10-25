"""Pruebas de integridad del esquema PostgreSQL/PostGIS (22 tablas) y de las restricciones criticas."""
import pytest

from tests.base_pruebas import ejecutar_script
from tests.conftest import leer_sql

TABLAS = {
    'usuarios', 'sesiones', 'archivos_temporales', 'capas_referencia', 'versiones_capa', 'elementos_capa',
    'cargas_alertas', 'zonas_cambio', 'alertas', 'carga_alerta_detalle', 'prioridades', 'factores_prioridad',
    'ajustes_prioridad', 'marcas', 'entradas_historial', 'contextos_territoriales', 'superposiciones',
    'analisis', 'fuentes_usadas', 'resultados_zona', 'trabajos', 'claves_idempotencia',
}


def test_esquema_tiene_las_22_tablas(bd):
    filas = bd("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' "
               "AND table_type = 'BASE TABLE' AND table_name <> 'spatial_ref_sys'")
    assert {fila[0] for fila in filas} == TABLAS


def test_todas_las_tablas_tienen_clave_primaria_y_las_fk_son_32(bd):
    sin_pk = bd("SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname <> 'spatial_ref_sys' "
                "AND NOT EXISTS (SELECT 1 FROM pg_constraint k WHERE k.conrelid = c.oid AND k.contype = 'p')")
    assert sin_pk == []
    assert bd("SELECT count(*) FROM pg_constraint k JOIN pg_namespace n ON n.oid = k.connamespace "
              "WHERE n.nspname = 'public' AND k.contype = 'f'")[0][0] == 32


def test_postgis_y_columnas_geometricas_en_epsg_32719(bd):
    assert bd("SELECT count(*) FROM pg_extension WHERE extname = 'postgis'")[0][0] == 1
    columnas = bd("SELECT f_table_name, srid FROM geometry_columns WHERE f_table_schema = 'public' ORDER BY 1")
    assert {tabla for tabla, _ in columnas} == {'alertas', 'elementos_capa', 'zonas_cambio'}
    assert {srid for _, srid in columnas} == {32719}


def test_integridad_sql_todas_las_pruebas_pasan(url_bd, bd):
    tablas_de_datos = ('usuarios', 'zonas_cambio', 'alertas', 'ajustes_prioridad', 'marcas', 'entradas_historial',
                       'trabajos', 'analisis', 'claves_idempotencia')
    conteo = ' UNION ALL '.join(f"SELECT '{t}', count(*) FROM {t}" for t in tablas_de_datos)
    antes = bd(conteo)
    script = leer_sql('integridad.sql')
    resultados = ejecutar_script(url_bd, script)
    fallos = [f'{prueba}: {detalle}' for estado, prueba, detalle in resultados if estado != 'PASS']
    assert not fallos, 'Pruebas SQL con fallo:\n' + '\n'.join(fallos)
    assert len(resultados) == script.count('PERFORM pg_temp.') >= 35
    assert bd(conteo) == antes, 'La transaccion de pruebas debe revertirse sin dejar filas'
