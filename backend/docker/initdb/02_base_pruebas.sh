#!/bin/bash
# Crea las bases de pruebas con el mismo esquema: ecoalert_test (A1; su suite carga una semilla y no borra datos) y
# ecoalert_auth_test (A2; su suite vacía usuarios y sesiones antes de cada prueba). Nunca deben tocar la base de desarrollo.
set -euo pipefail
for base in ecoalert_test ecoalert_auth_test; do
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE DATABASE $base"
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$base" -f /docker-entrypoint-initdb.d/01_esquema.sql
done
