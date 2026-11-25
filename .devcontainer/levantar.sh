#!/usr/bin/env bash
# Levanta EcoAlert Tambopata completo dentro de un GitHub Codespace (o cualquier Linux con Docker):
# PostGIS (docker compose) → cuenta de Coordinación → datos de demostración → API (uvicorn) → SPA (vite preview).
# Es idempotente: se puede volver a ejecutar tras reiniciar el Codespace.
#
# Contraseñas: se piden sin eco, o se leen de ECOALERT_PASSWORD_INICIAL (Coordinación) y
# ECOALERT_PASSWORD_DEMO (Analista SIG demo). Nunca se pasan como argumento ni se escriben en el repositorio.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$RAIZ/backend"
FRONTEND="$RAIZ/frontend"
PY="$BACKEND/.venv/bin/python"
LOGS="${TMPDIR:-/tmp}"

paso() { printf '\n==> %s\n' "$1"; }

paso "1/6 Dependencias"
[ -x "$PY" ] || { python3 -m venv "$BACKEND/.venv" && "$PY" -m pip install -q -r "$BACKEND/requirements.txt"; }
[ -d "$FRONTEND/node_modules" ] || npm --prefix "$FRONTEND" ci --no-audit --no-fund

paso "2/6 Variables de entorno (backend/.env con secretos aleatorios, solo si no existe)"
if [ ! -f "$BACKEND/.env" ]; then
  "$PY" - "$BACKEND" <<'PY'
import pathlib, secrets, sys
backend = pathlib.Path(sys.argv[1])
pg = secrets.token_hex(16)
valores = {
    'POSTGRES_PASSWORD': pg,
    'DATABASE_URL': f'postgresql://ecoalert:{pg}@localhost:5432/ecoalert',
    'JWT_SECRET': secrets.token_urlsafe(48),
    'IDEMPOTENCY_SECRET': secrets.token_urlsafe(48),
    'API_DOCS': 'false',  # despliegue: sin /docs
}
lineas = []
for linea in (backend / '.env.example').read_text(encoding='utf-8').splitlines():
    clave = linea.split('=', 1)[0]
    lineas.append(f'{clave}={valores[clave]}' if clave in valores and '=' in linea else linea)
destino = backend / '.env'
destino.write_text('\n'.join(lineas) + '\n', encoding='utf-8')
destino.chmod(0o600)
print('backend/.env creado (no se versiona).')
PY
else
  echo "backend/.env ya existe; se conserva."
fi
[ -f "$FRONTEND/.env" ] || cp "$FRONTEND/.env.example" "$FRONTEND/.env"

paso "3/6 Base de datos PostgreSQL 17 + PostGIS 3.5"
(cd "$BACKEND" && docker compose --env-file .env up -d)
for _ in $(seq 1 60); do
  [ "$(docker inspect -f '{{.State.Health.Status}}' ecoalert_db 2>/dev/null)" = healthy ] && break
  sleep 3
done
[ "$(docker inspect -f '{{.State.Health.Status}}' ecoalert_db)" = healthy ] || { echo 'La base no quedó healthy'; exit 1; }
set -a; . "$BACKEND/.env"; set +a

paso "4/6 Cuenta de Coordinación y datos de demostración"
hay_coordinacion=$(docker exec ecoalert_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
  "SELECT count(*) FROM usuarios WHERE rol='coordinacion'")
if [ "$hay_coordinacion" = 0 ]; then
  (cd "$BACKEND" && "$PY" -m app.cli crear-coordinacion --nombre "Rosa Huamán Quispe" --correo coordinacion@ecoalert.pe)
else
  echo "Ya existe una cuenta de Coordinación; se conserva."
fi
(cd "$BACKEND" && "$PY" -m scripts.sembrar_demo --nombre "Carmen Mamani Ccori")

paso "5/6 API FastAPI en 127.0.0.1:8000 (interna)"
if curl -fsS http://127.0.0.1:8000/salud >/dev/null 2>&1; then
  echo "La API ya está en ejecución."
else
  # exec + redirección del grupo completo: ningún proceso conserva la salida de esta terminal (ni la de ssh).
  (cd "$BACKEND" && exec nohup "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --env-file .env) \
    </dev/null >"$LOGS/ecoalert-api.log" 2>&1 &
  for _ in $(seq 1 30); do curl -fsS http://127.0.0.1:8000/salud >/dev/null 2>&1 && break; sleep 1; done
fi
curl -fsS http://127.0.0.1:8000/salud; echo

paso "6/6 SPA: build de producción servido con vite preview en el puerto 4173"
npm --prefix "$FRONTEND" run build >/dev/null
if ! curl -fsS -o /dev/null http://127.0.0.1:4173/ 2>/dev/null; then
  (cd "$FRONTEND" && exec nohup npx vite preview --host 0.0.0.0 --port 4173 --strictPort) \
    </dev/null >"$LOGS/ecoalert-spa.log" 2>&1 &
  for _ in $(seq 1 30); do curl -fsS -o /dev/null http://127.0.0.1:4173/ 2>/dev/null && break; sleep 1; done
fi
# 401 = la SPA llega a la API a través del proxy (mismo origen, sin CORS) y la API exige JWT.
estado=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:4173/api/v1/auth/me)
[ "$estado" = 401 ] || { echo "SPA → API respondió $estado (se esperaba 401)"; exit 1; }
echo "SPA → API: OK (401 sin token, como exige RNF-01)"

if [ -n "${CODESPACE_NAME:-}" ]; then
  echo
  echo "URL pública (tras hacer público el puerto 4173 en la pestaña Ports o con"
  echo "  gh codespace ports visibility 4173:public -c $CODESPACE_NAME):"
  echo "  https://${CODESPACE_NAME}-4173.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
else
  echo "Abre http://localhost:4173"
fi
echo "Registros: $LOGS/ecoalert-api.log y $LOGS/ecoalert-spa.log"
