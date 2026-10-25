# EcoAlert Tambopata — Backend (FastAPI + PostgreSQL/PostGIS)

API REST con autenticación JWT y control de acceso por rol, construida a partir del contrato
`S05_S06_A2/openapi_equipo.yaml` (v1.2.0). Las decisiones de seguridad y su justificación están en
`S05_S06_A2/revision_seguridad.md`.

## Alcance

- **Autenticación (S05-S06-A2):** registro (solo Coordinación), login con JWT, sesión actual, logout y cambio de contraseña.
- **CRUD inicial (S05-S06):** gestión de cuentas y consultas de alertas, cargas, marcas, ajustes, historial y trabajos.
- **Pendiente según el contrato:** ingesta de archivos, procesamiento asíncrono, zonas y mapa, prioridad,
  cambios de estado, creación y retiro de ajustes y marcas, comparación de periodos, exportación e `Idempotency-Key`.
  No se simulan como implementadas.

Las cuentas, zonas y análisis **no tienen DELETE** por diseño (RF-02-AC-7, RF-12-AC-17, RF-15-AC-3): responden 405.

## Puesta en marcha

Requisitos: Docker y Python 3.12 (`uv` recomendado).

```bash
cd backend
cp .env.example .env
# Genera un secreto y pégalo en JWT_SECRET (la API no arranca con el valor de plantilla):
python -c "import secrets; print(secrets.token_urlsafe(48))"

# 1. Base de datos: PostgreSQL 17 + PostGIS con S05_S06_A1/esquema_bd.sql importado
#    (crea también la base ecoalert_test para las pruebas).
docker compose --env-file .env up -d

# 2. Entorno Python
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-dev.txt

# 3. Primera cuenta de Coordinación (pide la contraseña sin eco; mínimo 12 caracteres)
.venv/bin/python -m app.cli crear-coordinacion --nombre "Coordinación Demo" --correo coordinacion@ecoalert.pe

# 4. API en http://127.0.0.1:8000 (documentación en /docs si API_DOCS=true)
.venv/bin/uvicorn app.main:app --reload
```

En Windows (PowerShell), activa el entorno con `.\.venv\Scripts\Activate.ps1` y usa `Copy-Item` en lugar de `cp`.
La imagen `postgis/postgis` solo existe para amd64; en Apple Silicon Docker la emula (ya está declarado en `docker-compose.yml`).

## Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `DATABASE_URL` | Sí | Conexión a PostgreSQL. |
| `JWT_SECRET` | Sí | Secreto HS256, mínimo 32 bytes aleatorios. |
| `JWT_EXPIRATION` | Sí | Vida máxima del token en segundos (1 a 86400). |
| `JWT_ISSUER`, `JWT_AUDIENCE` | No | Claims `iss` y `aud` (por defecto `ecoalert-api`, `ecoalert-spa`). |
| `SESION_INACTIVIDAD_SEGUNDOS` | No | Expiración por inactividad; por defecto 1800 (PS-12). |
| `API_DOCS` | No | Expone `/docs` y `/openapi.json`; por defecto `false`. |
| `POSTGRES_*` | Para Docker | Credenciales del contenedor de base de datos (solo desarrollo). |

## Autenticación y roles

Todas las rutas de `/api/v1` exigen `Authorization: Bearer <token>`, excepto `POST /auth/login`.

| Método | Ruta (`/api/v1`) | Acceso |
|---|---|---|
| POST | `/auth/login` | Público |
| POST | `/auth/register` | Coordinación |
| GET | `/auth/me` · POST `/auth/logout` · PUT `/auth/password` | Cualquier usuario autenticado |
| GET, POST | `/usuarios` · GET, PATCH `/usuarios/{usuarioId}` | Coordinación |
| GET | `/alertas`, `/cargas-alertas[/{id}]`, `/trabajos/{id}`, `/zonas/{codigo}/{marcas,ajustes,historial}[/{id}]` | Analista SIG y Coordinación |

- **401** sin token, con token inválido o expirado, o con la sesión cerrada o inactiva.
- **403** `ROL_NO_PERMITIDO` si el rol no tiene acceso; **403** `CAMBIO_PASSWORD_REQUERIDO` mientras la contraseña sea temporal.
- `GET /salud` (fuera de `/api/v1`) es público y solo informa si la base de datos responde.

## Pruebas

```bash
.venv/bin/python -m pytest                        # 101 pruebas contra la base ecoalert_test
COORD_PASSWORD='…' ./scripts/pruebas_manuales.sh  # pruebas manuales con curl (API en marcha)
```

La colección de Postman del video está en `S05_S06_A2/postman/`.

## Estructura

```
app/
  main.py           Ensamblado: routers, denegación por defecto, cabeceras de seguridad
  config.py         Variables de entorno validadas al arrancar
  security.py       Hash de contraseñas (bcrypt; verifica Argon2 heredado) y JWT
  dependencies.py   Middleware de autenticación (autenticar) y de rol (RequiereRol)
  errors.py         Errores RFC 9457 (application/problem+json)
  db.py             Pool de conexiones y consultas parametrizadas
  schemas.py        Modelos de solicitud alineados con el contrato
  routers/          auth, usuarios, consultas
  cli.py            Creación de la primera cuenta de Coordinación
tests/              Pruebas de integración, unitarias y de configuración
scripts/            Pruebas manuales con curl
docker/initdb/      Creación de la base de pruebas
```
