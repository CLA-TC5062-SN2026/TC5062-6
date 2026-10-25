#!/usr/bin/env bash
# Pruebas manuales de protección de rutas con curl (S05-S06-A2 Parte 2).
# Requisitos: API en marcha y cuenta de coordinación creada con `python -m app.cli crear-coordinacion`.
# Uso: COORD_PASSWORD='...' ./scripts/pruebas_manuales.sh [correo_coordinacion]
set -euo pipefail

API="${API:-http://127.0.0.1:8000/api/v1}"
COORD_CORREO="${1:-coordinacion@ecoalert.pe}"
: "${COORD_PASSWORD:?Define COORD_PASSWORD con la contraseña de la cuenta de coordinación}"
SUFIJO="$(date +%s)"
ANALISTA_CORREO="analista.${SUFIJO}@ecoalert.pe"
ANALISTA_TEMPORAL='Temporal-2026-xyz'
ANALISTA_NUEVA='Analista-Nueva-2026'

campo() { python3 -c "import json,sys; print(json.load(sys.stdin)$1)"; }

peticion() {  # peticion "titulo" curl-args... -> imprime método, URL, código y cuerpo
  local titulo="$1"; shift
  echo "=== ${titulo}"
  printf '$ curl'; printf ' %q' "$@" | sed -E 's/(Bearer\\? )[A-Za-z0-9._-]{20,}/\1<token>/'; echo
  local salida codigo
  salida="$(curl -s -w '\n%{http_code}' "$@")"
  codigo="${salida##*$'\n'}"
  echo "HTTP ${codigo}"
  echo "${salida%$'\n'*}" | sed -E 's/("access_token":")[^"]+/\1<jwt>/'
  echo
}

# --- Preparación ------------------------------------------------------------
TOKEN_COORD="$(curl -s "$API/auth/login" -H 'Content-Type: application/json' \
  -d "{\"correo\":\"$COORD_CORREO\",\"password\":\"$COORD_PASSWORD\"}" | campo "['access_token']")"

peticion "Registro de analista por Coordinación (201, sin contraseña en la respuesta)" \
  -X POST "$API/auth/register" -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN_COORD" \
  -d "{\"nombre_completo\":\"Analista Prueba\",\"correo\":\"$ANALISTA_CORREO\",\"rol\":\"analista_sig\",\"password_temporal\":\"$ANALISTA_TEMPORAL\"}"

TOKEN_ANALISTA="$(curl -s "$API/auth/login" -H 'Content-Type: application/json' \
  -d "{\"correo\":\"$ANALISTA_CORREO\",\"password\":\"$ANALISTA_TEMPORAL\"}" | campo "['access_token']")"

peticion "Analista con contraseña temporal en ruta CRUD (403 CAMBIO_PASSWORD_REQUERIDO)" \
  "$API/alertas" -H "Authorization: Bearer $TOKEN_ANALISTA"

peticion "Analista cambia su contraseña temporal (204)" \
  -X PUT "$API/auth/password" -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN_ANALISTA" \
  -d "{\"password_actual\":\"$ANALISTA_TEMPORAL\",\"password_nueva\":\"$ANALISTA_NUEVA\"}"

# Se altera un carácter a mitad del token (en la carga útil): la firma deja de corresponder.
MITAD=$(( ${#TOKEN_COORD} / 2 ))
ORIGINAL="${TOKEN_COORD:$MITAD:1}"
if [ "$ORIGINAL" = "A" ]; then REEMPLAZO="B"; else REEMPLAZO="A"; fi
TOKEN_ALTERADO="${TOKEN_COORD:0:$MITAD}${REEMPLAZO}${TOKEN_COORD:$((MITAD + 1))}"

# --- Casos exigidos por la actividad ---------------------------------------------
peticion "CASO 1 - Ruta protegida sin token (401)" \
  "$API/usuarios"
peticion "CASO 2 - Ruta protegida con token alterado en 1 carácter (401)" \
  "$API/usuarios" -H "Authorization: Bearer $TOKEN_ALTERADO"
peticion "CASO 3 - Ruta de Coordinación con token de Analista SIG (403)" \
  "$API/usuarios" -H "Authorization: Bearer $TOKEN_ANALISTA"
peticion "CASO 4 - Ruta de Coordinación con token de Coordinación (200)" \
  "$API/usuarios?activo=true" -H "Authorization: Bearer $TOKEN_COORD"

# --- Casos adicionales ----------------------------------------------------------
peticion "EXTRA - Ruta de ambos roles con token de Analista SIG (200)" \
  "$API/alertas" -H "Authorization: Bearer $TOKEN_ANALISTA"
peticion "EXTRA - Registro con token de Analista SIG (403)" \
  -X POST "$API/auth/register" -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN_ANALISTA" \
  -d '{"nombre_completo":"X","correo":"x@ecoalert.pe","rol":"coordinacion","password_temporal":"Temporal-2026-xyz"}'
peticion "EXTRA - Login con contraseña incorrecta (401 genérico)" \
  -X POST "$API/auth/login" -H 'Content-Type: application/json' \
  -d "{\"correo\":\"$ANALISTA_CORREO\",\"password\":\"incorrecta-123\"}"
peticion "EXTRA - Logout (204)" \
  -X POST "$API/auth/logout" -H "Authorization: Bearer $TOKEN_ANALISTA"
peticion "EXTRA - Reutilizar el token después del logout (401)" \
  "$API/auth/me" -H "Authorization: Bearer $TOKEN_ANALISTA"
