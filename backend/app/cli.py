"""Crea la primera cuenta de Coordinación (equivalente a `createsuperuser` de Django).

Uso: python -m app.cli crear-coordinacion --nombre "Ana Quispe" --correo ana@ecoalert.pe
La contraseña se pide sin eco en la terminal o se lee de ECOALERT_PASSWORD_INICIAL
(para scripts). Nunca se acepta como argumento: quedaría en el historial del shell.
"""
import argparse
import getpass
import os
import sys

import psycopg
from psycopg.rows import dict_row
from pydantic import ValidationError

from app.config import get_settings
from app.schemas import UsuarioCrear
from app.security import hashear


def _leer_password() -> str:
    if valor := os.environ.get('ECOALERT_PASSWORD_INICIAL'):
        return valor
    primera = getpass.getpass('Contraseña (mínimo 12 caracteres): ')
    if primera != getpass.getpass('Repite la contraseña: '):
        sys.exit('Las contraseñas no coinciden.')
    return primera


def crear_coordinacion(nombre: str, correo: str) -> None:
    try:
        datos = UsuarioCrear(nombre_completo=nombre, correo=correo, rol='coordinacion',
                             password_temporal=_leer_password())
    except ValidationError as exc:
        sys.exit('Datos no válidos: ' + '; '.join(e['msg'] for e in exc.errors()))
    with psycopg.connect(get_settings().database_url.get_secret_value(), row_factory=dict_row) as conn:
        # Solo sirve para el arranque: después, las cuentas se crean por la API (RF-02).
        if conn.execute("SELECT 1 FROM usuarios WHERE rol='coordinacion' LIMIT 1").fetchone():
            sys.exit('Ya existe una cuenta de coordinación; crea las demás con POST /api/v1/auth/register.')
        # Quien ejecuta el comando elige la contraseña, así que no es temporal.
        fila = conn.execute(
            '''INSERT INTO usuarios (nombre_completo, correo, rol, password_hash, debe_cambiar_password)
               VALUES (%s, %s, 'coordinacion', %s, FALSE) RETURNING id''',
            (datos.nombre_completo, str(datos.correo), hashear(datos.password_temporal)),
        ).fetchone()
    print(f'Cuenta de coordinación creada: {fila["id"]}')


def main() -> None:
    parser = argparse.ArgumentParser(prog='python -m app.cli')
    sub = parser.add_subparsers(dest='comando', required=True)
    crear = sub.add_parser('crear-coordinacion', help='Crea la primera cuenta de Coordinación')
    crear.add_argument('--nombre', required=True)
    crear.add_argument('--correo', required=True)
    args = parser.parse_args()
    crear_coordinacion(args.nombre, args.correo)


if __name__ == '__main__':
    main()
