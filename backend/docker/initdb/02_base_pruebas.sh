#!/bin/bash
# Crea ecoalert_test con el mismo esquema: las pruebas automatizadas vacían sus tablas
# y nunca deben tocar la base de datos de desarrollo.
set -euo pipefail
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'CREATE DATABASE ecoalert_test'
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d ecoalert_test -f /docker-entrypoint-initdb.d/01_esquema.sql
