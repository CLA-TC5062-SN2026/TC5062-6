# EcoAlert Tambopata — Backend integrado (FastAPI + PostgreSQL/PostGIS)

Backend único que une los servicios CRUD de **S05-S06-A1** (paginación, idempotencia, PUT/PATCH, validaciones y pruebas) con la
autenticación y seguridad de **S05-S06-A2** (JWT, sesiones, roles y protección de rutas). El contrato es
`S05_S06_integracion/openapi_integrado.yaml` (v1.3.0); la relación con los contratos originales de A1 y A2, que se conservan sin
cambios, está en `S05_S06_integracion/integracion.md`. Las decisiones de seguridad están en `S05_S06_A2/revision_seguridad.md`.

## Alcance
Implementa **20 de las 39 operaciones** del contrato integrado:

- **Autenticación (A2):** `POST /auth/login`, `POST /auth/register` (solo Coordinación), `GET /auth/me`, `POST /auth/logout` y `PUT /auth/password`.
- **Usuarios (A1):** listar, crear (idempotente), consultar, reemplazar (`PUT`) y actualizar parcialmente (`PATCH`).
- **Consultas (A1):** alertas (paginadas, con filtros), cargas, marcas, ajustes, historial y trabajos.
- **Pendiente según el contrato:** ingesta de archivos, procesamiento asíncrono, zonas y mapa, prioridad, cambios de estado, creación y retiro de ajustes y marcas, comparación de periodos y exportación. No se simulan como implementadas.

Las cuentas, zonas y análisis **no tienen DELETE** por diseño (RF-02-AC-7, RF-12-AC-17, RF-15-AC-3): responden 405.
**Toda la API de `/api/v1` exige JWT**, salvo `POST /auth/login`; los clientes que no enviaban `Authorization` (p. ej. las colecciones Postman originales de A1) reciben 401.

## Puesta en marcha (PowerShell)

Requisitos: Python 3.13 (el SRS indica 3.12 para el despliegue) y Docker Desktop iniciado. Todos los comandos, desde `backend`.

```powershell
cd .\backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

1. **Secretos en `.env`** (la API no arranca con valores de plantilla ni sin ellos). Genera dos valores distintos y pégalos en `JWT_SECRET` e `IDEMPOTENCY_SECRET`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

2. **Base de datos** PostgreSQL 17 + PostGIS 3.5 con `S05_S06_A1/esquema_bd.sql` importado (crea también las bases de pruebas):

```powershell
docker compose --env-file .env up -d
docker compose ps   # espera (healthy)
```

   Si ya tienes el contenedor `ecoalert_db` (creado con `docker run`), inícialo con `docker start ecoalert_db` y omite este paso; el esquema se importa con `docker cp ..\S05_S06_A1\esquema_bd.sql ecoalert_db:/tmp/e.sql` y `docker exec ecoalert_db psql -U ecoalert -d ecoalert -v ON_ERROR_STOP=1 -f /tmp/e.sql`.

3. **Primera cuenta de Coordinación** (pide la contraseña sin eco; mínimo 12 caracteres). Solo funciona si aún no existe ninguna:

```powershell
python -m app.cli crear-coordinacion --nombre "Coordinación Demo" --correo coordinacion@ecoalert.pe
```

4. **Servidor** (`--env-file` carga `.env`, incluido `IDEMPOTENCY_SECRET`):

```powershell
python -m uvicorn app.main:app --reload --env-file .env
```

5. **Verificar**: `Invoke-RestMethod http://127.0.0.1:8000/salud` → `estado: ok`. `GET /api/v1/usuarios` sin token responde 401. Con `API_DOCS=true` hay documentación interactiva en `/docs` (con el botón *Authorize* para pegar el JWT que entrega `POST /api/v1/auth/login`).

Si PowerShell bloquea la activación del entorno: `Set-ExecutionPolicy -Scope Process Bypass`. `.env` está en `.gitignore`; no subirlo.

## Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `DATABASE_URL` | Sí | Conexión a PostgreSQL. |
| `JWT_SECRET` | Sí | Secreto HS256, mínimo 32 bytes aleatorios. |
| `JWT_EXPIRATION` | Sí | Vida máxima del token en segundos (1 a 86400). |
| `IDEMPOTENCY_SECRET` | Sí | Secreto del HMAC-SHA256 de la huella de `Idempotency-Key`; debe estar en el entorno del proceso (`--env-file`). |
| `JWT_ISSUER`, `JWT_AUDIENCE` | No | Claims `iss` y `aud` (por defecto `ecoalert-api`, `ecoalert-spa`). |
| `SESION_INACTIVIDAD_SEGUNDOS` | No | Expiración por inactividad; por defecto 1800 (PS-12). |
| `API_DOCS` | No | Expone `/docs` y `/openapi.json`; por defecto `false`. |
| `POSTGRES_*` | Para Docker | Credenciales del contenedor de base de datos (solo desarrollo). |

## Autenticación, roles y contraseñas

| Método | Ruta (`/api/v1`) | Acceso |
|---|---|---|
| POST | `/auth/login` | Público |
| POST | `/auth/register` | Coordinación (alias de `POST /usuarios`; `Idempotency-Key` obligatoria) |
| GET | `/auth/me` · POST `/auth/logout` · PUT `/auth/password` | Cualquier usuario autenticado |
| GET, POST | `/usuarios` · GET, PUT, PATCH `/usuarios/{usuarioId}` | Coordinación |
| GET | `/alertas`, `/cargas-alertas[/{id}]`, `/trabajos/{id}`, `/zonas/{codigo}/{marcas,ajustes,historial}[/{id}]` | Analista SIG y Coordinación |

- **401** sin token, con token inválido o expirado, o con la sesión cerrada, inactiva o de una cuenta desactivada. **403** `ROL_NO_PERMITIDO` si el rol no tiene acceso; **403** `CAMBIO_PASSWORD_REQUERIDO` mientras la contraseña sea temporal (solo `me`, `logout` y `password` quedan abiertos).
- El rol y el estado de la cuenta se leen de la base en cada petición: desactivar una cuenta (con `PUT` o `PATCH`) o cambiar su rol surte efecto al instante, y al desactivar se revocan sus sesiones.
- **Contraseñas:** las cuentas nuevas se guardan con **Argon2id** (como en A1). El login verifica Argon2id y bcrypt (hashes heredados de A2); un hash bcrypt válido se migra a Argon2id al iniciar sesión. Una contraseña nueva tiene de 12 a 128 caracteres; en el login se aceptan hasta 1024. Un hash ausente, ilegible o incompatible nunca lanza error 500: se responde el mismo 401 genérico que para una contraseña incorrecta.
- `POST /usuarios` y `POST /auth/register` exigen `Idempotency-Key` (UUID) y comparten la misma lógica: durante 24 h, repetir la clave con el mismo cuerpo devuelve la respuesta original y con cualquier cambio (incluida la contraseña temporal) responde `422 IDEMPOTENCIA_CONFLICTO`. La huella es un HMAC-SHA256 del JSON canónico del cuerpo completo; solo se almacenan respuestas 2xx.
- `PUT` y `PATCH` de usuarios comparten una función transaccional (regla de la última coordinación también al quitar el rol, cierre de sesiones al desactivar, correo inmutable). `PATCH` exige `application/merge-patch+json` (415 si no). `PUT` se añadió al contrato como propuesta adoptada para cumplir la actividad, sin aprobación formal de todos los integrantes (`S05_S06_A1/diferencias_diseno.md`, API-13).
- `GET /salud` (fuera de `/api/v1`) es público y solo informa si la base responde.

### Trazabilidad con el contrato integrado

| Método | Ruta | Operación | Origen |
|---|---|---|---|
| POST | `/api/v1/auth/login` | iniciarSesion | A2 |
| POST | `/api/v1/auth/register` | registrarUsuario | A2 (+ `Idempotency-Key` de A1) |
| GET | `/api/v1/auth/me` | obtenerSesionActual | A2 |
| POST | `/api/v1/auth/logout` | cerrarSesion | A2 |
| PUT | `/api/v1/auth/password` | cambiarPassword | A2 |
| GET, POST | `/api/v1/usuarios` | listarUsuarios, crearUsuario | A1 |
| GET, PUT, PATCH | `/api/v1/usuarios/{usuarioId}` | obtenerUsuario, reemplazarUsuario, actualizarUsuario | A1 |
| GET | `/api/v1/alertas` | listarAlertas (paginado; filtros `zona` y `presente_en_ultima_carga`) | A1 |
| GET | `/api/v1/cargas-alertas[/{cargaId}]` | listarCargasAlertas, obtenerCargaAlertas | A1 |
| GET | `/api/v1/zonas/{codigo}/marcas[/{marcaId}]` | listarMarcasZona, obtenerMarca | A1 |
| GET | `/api/v1/zonas/{codigo}/ajustes[/{ajusteId}]` | listarAjustesZona, obtenerAjuste | A1 |
| GET | `/api/v1/zonas/{codigo}/historial[/{entradaId}]` | obtenerHistorialZona, obtenerEntradaHistorial | A1 |
| GET | `/api/v1/trabajos/{trabajoId}` | obtenerTrabajo | A1 |

## Estructura

```
app/
  main.py           Fábrica de la app: routers, denegación por defecto, cabeceras de seguridad
  config.py         Variables de entorno validadas al arrancar (A2)
  security.py       Hash (Argon2id; verifica bcrypt heredado) y JWT (A2)
  dependencies.py   Autenticación (autenticar) y autorización por rol (RequiereRol) (A2)
  errors.py         Errores RFC 9457 (application/problem+json), con 400/422 del contrato (A1)
  db.py             Pool, transacciones, SQL parametrizado e idempotencia HMAC (A1)
  schemas.py        Modelos de solicitud y respuesta alineados con el contrato
  routers/          auth (A2), usuarios y consultas (A1)
  cli.py            Creación de la primera cuenta de Coordinación (A2)
tests/              Suite de A1 (base ecoalert_test sembrada) e integración A1 + A2
docker-compose.yml  Base local con el esquema importado
docker/initdb/      Creación de las bases de pruebas
```

## Pruebas automatizadas (pytest)

Hay dos suites, cada una con **su propia base `*_test`**; ninguna toca la base de desarrollo (`ecoalert`) ni de producción, y ambas se niegan a correr si el nombre no termina en `_test`:

| Suite | Ubicación | Base | Qué hace con los datos |
|---|---|---|---|
| A1 + integración | `backend/tests/` | `ecoalert_test` | Importa el esquema y carga la semilla controlada `tests/sql/semilla.sql`; **no borra nada** |
| A2 | `S05_S06_A2/pruebas/` | `ecoalert_auth_test` | Vacía `usuarios` y `sesiones` (CASCADE) antes de cada prueba; se niega a usar la base de A1 |

Las bases se crean solas si no existen. Requisitos: PostgreSQL/PostGIS en marcha y `backend/.env` creado. Desde `backend` (con el entorno virtual activo):

```powershell
python -m pip install -r requirements-test.txt
python -m pytest                         # ambas suites
python -m pytest tests                   # solo A1 + integración
python -m pytest ../S05_S06_A2/pruebas   # solo A2
```

En VS Code: abrir la carpeta del repositorio, seleccionar el intérprete `backend\.venv\Scripts\python.exe` y ejecutar los comandos en el terminal integrado, o usar el panel *Testing* (*Python: Configure Tests* > *pytest* > carpeta `backend`).

| Archivo | Qué comprueba |
|---|---|
| `tests/sql/integridad.sql` + `test_integridad_sql.py` | 22 tablas, claves, PostGIS (EPSG:32719) y 35 casos de restricciones, en una transacción que se revierte |
| `tests/test_contrato.py` | Contrato integrado válido, 39 operaciones, relación con los contratos originales de A1 y A2, 166 criterios Must del SRS, 62 schemas = 62 clases UML y 20 rutas del backend contenidas en el contrato |
| `tests/test_api_lecturas.py`, `tests/test_api_usuarios.py` | Lecturas, POST/GET/PUT/PATCH, idempotencia HMAC, concurrencia y regla de la última coordinación, con una sesión JWT de Coordinación |
| `tests/test_integracion_auth.py` | Roles sobre los datos de A1, login de cuentas creadas por A1, contraseña temporal, revocación inmediata con PUT/PATCH, `register` idempotente, hashes bcrypt/ilegibles y contraseñas largas |
| `S05_S06_A2/pruebas/test_auth.py`, `test_security.py`, `test_config.py` | Login, registro, JWT (firma, expiración, `alg`), sesiones, cambio de contraseña, hash y configuración |
| `S05_S06_A2/pruebas/test_proteccion_rutas.py` | 401 sin token y 403 por rol en **todas** las rutas montadas, según los `x-roles` del contrato integrado |
| `S05_S06_A2/pruebas/pruebas_manuales.sh` | Pruebas manuales con `curl` (API en marcha, bash) |

Variables opcionales: `TEST_DB_NAME` / `TEST_DATABASE_URL` (base de A1) y `TEST_AUTH_DB_NAME` / `TEST_AUTH_DATABASE_URL` (base de A2), siempre `*_test`; `API_BASE_URL` (usar una API ya levantada en la suite de A1; se comprueba que lea la base de pruebas). Las pruebas fijan secretos efímeros en memoria, de modo que no dependen de los de `.env`.

### Verificación local (25/10/2026)
Entorno: Windows, Python 3.13.7, Docker Engine 29.8.0, `postgis/postgis:17-3.5` (PostgreSQL 17.5, PostGIS 3.5.2).
- **`python -m pytest`:** 225 de 225 aprobadas (101 de A1 + integración y 124 de A2), también por separado y en orden inverso.
- **Prueba de humo contra uvicorn y PostgreSQL reales:** creación de la Coordinación con la CLI, login, 401 sin token y con token alterado, reintento idempotente, `PUT`/`PATCH`/`DELETE`, `register`, contraseña temporal, cambio de contraseña, revocación al desactivar y logout; todos los códigos coinciden con el contrato.
- **Sin verificar:** operaciones no implementadas, rendimiento (RNF-04) y las colecciones Postman originales contra el backend integrado (usan el contrato anterior; ver `S05_S06_integracion/integracion.md`).

## Limitaciones
- El modelo SQL y las vistas OpenAPI no son equivalentes 1:1; los DTO se construyen en la API.
- Las alertas sin zona o sin área no se publican en `GET /alertas` (el contrato exige ambas).
- Una respuesta `405` incluye `Allow` solo con los métodos de la primera ruta coincidente, no con todos los permitidos; no afecta al contrato.
- Si se rota `IDEMPOTENCY_SECRET`, las claves de las últimas 24 h dejan de coincidir y sus reintentos responderán `422`.
- `claves_idempotencia` no está ligada a la cuenta que hizo la solicitud: quien repita una clave con el mismo cuerpo recibe la respuesta guardada.
- La verificación de una cuenta con hash bcrypt tarda algo más que la de una Argon2id; es la única diferencia de tiempo entre cuentas existentes.
