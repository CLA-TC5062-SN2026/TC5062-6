"""Carga datos de demostración en la base de DESARROLLO para probar el frontend de extremo a extremo.

La ingesta de alertas (POST /cargas-alertas) aún no está implementada, así que sin este script la vista de
alertas solo mostraría una lista vacía. Crea:
  - una cuenta de Analista SIG con contraseña definitiva (debe_cambiar_password = FALSE);
  - 6 zonas de cambio, 1 carga de alertas y 24 alertas de GeoBosques en Tambopata (EPSG:32719).

Uso, desde backend/ y con la base levantada:
    python -m scripts.sembrar_demo --correo analista.demo@ecoalert.pe
La contraseña se pide sin eco o se lee de ECOALERT_PASSWORD_DEMO; nunca se acepta como argumento.

Es idempotente (ON CONFLICT DO NOTHING) y se niega a ejecutarse contra un host que no sea local
o contra una base de pruebas (*_test), para no mezclar datos de demostración con otros entornos.
"""
import argparse
import getpass
import os
import sys
from datetime import date, timedelta
from urllib.parse import urlparse

import psycopg
from psycopg.rows import dict_row
from pydantic import ValidationError

from app.config import get_settings
from app.schemas import UsuarioCrear
from app.security import hashear

HOSTS_LOCALES = {'localhost', '127.0.0.1', '::1', 'db'}
FUENTE = 'GeoBosques'
# Centro aproximado de la zona de amortiguamiento de Tambopata en UTM 19S (EPSG:32719).
ORIGEN_X, ORIGEN_Y = 478_000, 8_614_000
ZONAS = [  # código, nivel, puntaje, área (ha), estado
    ('EA-2026-101', 'alta', 86, 12.40, 'en_revision'),
    ('EA-2026-102', 'alta', 78, 8.15, 'nueva'),
    ('EA-2026-103', 'media', 55, 4.60, 'nueva'),
    ('EA-2026-104', 'media', 47, 3.25, 'requiere_verificacion'),
    ('EA-2026-105', 'baja', 22, 1.10, 'nueva'),
    ('EA-2026-106', 'baja', 15, 0.75, 'revisada'),
]
ALERTAS_POR_ZONA = 4
FECHA_BASE = date(2026, 10, 28)


def _validar_destino(url: str) -> None:
    destino = urlparse(url)
    base = destino.path.lstrip('/')
    if destino.hostname not in HOSTS_LOCALES:
        sys.exit(f'Destino no local ({destino.hostname}): este script solo carga datos en desarrollo.')
    if base.endswith('_test'):
        sys.exit('La base de pruebas tiene su propia semilla (tests/sql/semilla.sql).')


def _leer_password() -> str:
    if valor := os.environ.get('ECOALERT_PASSWORD_DEMO'):
        return valor
    primera = getpass.getpass('Contraseña de la cuenta demo (mínimo 12 caracteres): ')
    if primera != getpass.getpass('Repite la contraseña: '):
        sys.exit('Las contraseñas no coinciden.')
    return primera


def _cuadrado(x: int, y: int, lado: int) -> str:
    return f'POLYGON(({x} {y},{x + lado} {y},{x + lado} {y + lado},{x} {y + lado},{x} {y}))'


def _asegurar_cuenta(conn, nombre: str, correo: str) -> str:
    existente = conn.execute('SELECT id FROM usuarios WHERE lower(correo)=lower(%s)', (correo,)).fetchone()
    if existente:
        print(f'La cuenta {correo} ya existe; se conserva su contraseña.')
        return existente['id']
    try:
        datos = UsuarioCrear(nombre_completo=nombre, correo=correo, rol='analista_sig',
                             password_temporal=_leer_password())
    except ValidationError as exc:
        sys.exit('Datos no válidos: ' + '; '.join(e['msg'] for e in exc.errors()))
    fila = conn.execute(
        '''INSERT INTO usuarios (nombre_completo, correo, rol, password_hash, debe_cambiar_password)
           VALUES (%s, %s, 'analista_sig', %s, FALSE) RETURNING id''',
        (datos.nombre_completo, str(datos.correo), hashear(datos.password_temporal)),
    ).fetchone()
    print(f'Cuenta demo creada: {correo}')
    return fila['id']


def _sembrar_zonas_y_alertas(conn, usuario_id) -> int:
    nuevas = 0
    for indice, (codigo, nivel, puntaje, area, estado) in enumerate(ZONAS):
        x, y = ORIGEN_X + indice * 2_500, ORIGEN_Y + (indice % 3) * 1_800
        conn.execute(
            '''INSERT INTO zonas_cambio (codigo, estado, geometria, area_ha, nivel, puntaje_vigente)
               VALUES (%s, %s, ST_GeomFromText(%s, 32719), %s, %s, %s) ON CONFLICT DO NOTHING''',
            (codigo, estado, _cuadrado(x, y, 400), area, nivel, puntaje),
        )
        for n in range(ALERTAS_POR_ZONA):
            numero = indice * ALERTAS_POR_ZONA + n + 1
            cursor = conn.execute(
                '''INSERT INTO alertas (fuente, codigo, fecha_deteccion, presente_en_ultima_carga, zona_codigo,
                                        area_ha, geometria)
                   VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 32719)) ON CONFLICT DO NOTHING''',
                (FUENTE, f'GB-2026-{numero:04d}', FECHA_BASE - timedelta(days=numero * 3), n != 3, codigo,
                 round(area / ALERTAS_POR_ZONA, 2), f'POINT({x + 50 + n * 80} {y + 50 + n * 60})'),
            )
            nuevas += cursor.rowcount
    conn.execute(
        '''INSERT INTO cargas_alertas (id, fuente, fecha_corte, cargada_por, alertas_en_archivo, alertas_nuevas,
                                       zonas_creadas, resumen)
           VALUES ('30000000-0000-4000-8000-000000000001', %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING''',
        (FUENTE, FECHA_BASE, usuario_id, len(ZONAS) * ALERTAS_POR_ZONA, len(ZONAS) * ALERTAS_POR_ZONA, len(ZONAS),
         'Datos de demostración para la integración frontend-backend (S07-S08-A2)'),
    )
    return nuevas


def main() -> None:
    parser = argparse.ArgumentParser(prog='python -m scripts.sembrar_demo')
    parser.add_argument('--correo', default='analista.demo@ecoalert.pe')
    parser.add_argument('--nombre', default='Analista Demo')
    args = parser.parse_args()

    url = get_settings().database_url.get_secret_value()
    _validar_destino(url)
    with psycopg.connect(url, row_factory=dict_row) as conn:
        usuario_id = _asegurar_cuenta(conn, args.nombre, args.correo)
        nuevas = _sembrar_zonas_y_alertas(conn, usuario_id)
    print(f'Zonas: {len(ZONAS)}. Alertas nuevas insertadas: {nuevas}.')


if __name__ == '__main__':
    main()
