# EcoAlert Tambopata — CRUD inicial (FastAPI + PostgreSQL/PostGIS)

## Alcance real
Implementa **15 operaciones de lectura y escritura iniciales** con las mismas rutas y códigos de éxito definidos en `openapi_equipo.yaml` (v1.2.0): creación, listado, consulta, reemplazo (`PUT`) y actualización parcial (`PATCH`) de usuarios; consulta de alertas, cargas, marcas, ajustes, historial y trabajos. Las entidades geoespaciales, historiales y comparaciones **no tienen DELETE** en el contrato del equipo; no se inventan endpoints destructivos.

**Importante:** esta entrega es una **base de servicios CRUD, no una implementación completa de las 38 operaciones OpenAPI**. Las operaciones de autenticación, ingesta de archivos, procesamiento asíncrono, construcción de respuestas espaciales completas, cálculo de prioridad, cambios de estado, creación/retiro de ajustes y marcas, comparación y exportación quedan pendientes. No deben simularse como implementadas. Tampoco se habilitan operaciones que requieran `creado_por` o `autor_id` sin autenticación real. Los endpoints existentes **aún no tienen control de acceso** y no deben exponerse fuera de un entorno local de desarrollo.

### Inicio local (PowerShell)

Requisitos: Windows, Python 3.13 (`py -3.13 --version`) y Docker Desktop iniciado. El SRS indica Python 3.12 para el despliegue; en desarrollo local se usa 3.13, compatible con `requirements.txt`. Los pasos 1 y 2 se ejecutan desde la raíz del repositorio.

1. **PostgreSQL 17 + PostGIS 3.5** (credenciales iguales a las de `.env.example`):

```powershell
docker run -d --name ecoalert_db `
  -e POSTGRES_USER=ecoalert -e POSTGRES_PASSWORD=ecoalert_dev -e POSTGRES_DB=ecoalert `
  -p 5432:5432 -v ecoalert_pgdata:/var/lib/postgresql/data `
  postgis/postgis:17-3.5
docker exec ecoalert_db pg_isready -U ecoalert -d ecoalert
```

   Si el contenedor ya existe, iniciarlo con `docker start ecoalert_db`.

2. **Importar el esquema** en una base vacía. El script no es idempotente y se detiene en el primer error:

```powershell
docker cp .\S05_S06_A1\esquema_bd.sql ecoalert_db:/tmp/esquema_bd.sql
docker exec ecoalert_db psql -U ecoalert -d ecoalert -v ON_ERROR_STOP=1 -f /tmp/esquema_bd.sql
```

3. **Entorno virtual, dependencias y servidor** (desde `backend`):

```powershell
cd .\backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
[Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

   El último comando imprime un secreto aleatorio: copiarlo como valor de `IDEMPOTENCY_SECRET` en `.env`. Es obligatorio (la API no arranca sin él) y no debe subirse a Git. Luego iniciar el servidor:

```powershell
python -m uvicorn app.main:app --reload --env-file .env
```

   Si PowerShell bloquea la activación del entorno: `Set-ExecutionPolicy -Scope Process Bypass`.

4. **Verificar**: `Invoke-RestMethod http://127.0.0.1:8000/salud` debe devolver `estado: ok` y `base_datos: True`. Documentación interactiva en http://127.0.0.1:8000/docs. Las operaciones del contrato se sirven bajo `/api/v1` (p. ej. `GET http://127.0.0.1:8000/api/v1/usuarios`); `/salud` es un endpoint operativo fuera del contrato y del prefijo.

El archivo `.env.example` contiene valores **solo de desarrollo local** y un marcador en `IDEMPOTENCY_SECRET`. `.env` está en `.gitignore`; no subirlo al repositorio.

### Trazabilidad

| Método | Ruta | Operación | Estado |
|---|---|---|---|
| GET | `/api/v1/usuarios` | listarUsuarios | Implementado |
| POST | `/api/v1/usuarios` | crearUsuario | Implementado (`Location`, `Idempotency-Key`) |
| GET | `/api/v1/usuarios/{usuarioId}` | obtenerUsuario | Implementado |
| PUT | `/api/v1/usuarios/{usuarioId}` | reemplazarUsuario | Implementado (`nombre_completo`, `rol` y `activo` obligatorios; mismas reglas y transacción que PATCH) |
| PATCH | `/api/v1/usuarios/{usuarioId}` | actualizarUsuario | Implementado (merge-patch, regla de última coordinación) |
| GET | `/api/v1/alertas` | listarAlertas | Implementado (paginado; filtros `zona` y `presente_en_ultima_carga`) |
| GET | `/api/v1/cargas-alertas` | listarCargasAlertas | Implementado |
| GET | `/api/v1/cargas-alertas/{cargaId}` | obtenerCargaAlertas | Implementado |
| GET | `/api/v1/zonas/{codigo}/marcas` | listarMarcasZona | Implementado |
| GET | `/api/v1/zonas/{codigo}/marcas/{marcaId}` | obtenerMarca | Implementado |
| GET | `/api/v1/zonas/{codigo}/ajustes` | listarAjustesZona | Implementado |
| GET | `/api/v1/zonas/{codigo}/ajustes/{ajusteId}` | obtenerAjuste | Implementado |
| GET | `/api/v1/zonas/{codigo}/historial` | obtenerHistorialZona | Implementado |
| GET | `/api/v1/zonas/{codigo}/historial/{entradaId}` | obtenerEntradaHistorial | Implementado |
| GET | `/api/v1/trabajos/{trabajoId}` | obtenerTrabajo | Implementado |
| Resto | Según OpenAPI | Seguridad, zonas, capas, ingesta, prioridad, análisis, exportación | Pendiente |

**Fidelidad al contrato:** las 15 operaciones se verifican contra los schemas de `openapi_equipo.yaml` con datos reales en PostgreSQL (ver *Pruebas automatizadas*). La cobertura sigue siendo parcial: 15 de 38 operaciones.

### Diseño
- Módulos de `app/`: `main.py` (rutas), `schemas.py` (modelos de solicitud y respuesta alineados con los schemas del OpenAPI), `errors.py` (errores del contrato) y `db.py` (pool, transacciones, SQL parametrizado e idempotencia).
- Respuestas: `201` con `Location` al crear; `200` en lecturas y actualizaciones; `400` para JSON ilegible o parámetros inválidos; `404` si falta el recurso; `409` por correo duplicado o última cuenta de coordinación; `415` si el `PATCH` no usa `application/merge-patch+json`; `422` si el cuerpo incumple el esquema. Los errores son `application/problem+json` con `codigo` y `mensaje` en español.
- `PUT` y `PATCH` de usuarios comparten la misma función transaccional: bloquean las cuentas de coordinación activas, aplican la regla de la última coordinación (también al quitar el rol), cierran las sesiones al desactivar y no permiten cambiar el correo. `PUT` exige los tres campos editables; `PATCH` acepta un subconjunto. `PUT` se añadió en la versión 1.2.0 del contrato como propuesta adoptada para cumplir la actividad, sin aprobación formal de todos los integrantes (`diferencias_diseno.md`, API-13).
- `POST /usuarios` exige `Idempotency-Key` (UUID). Durante 24 h, repetir la clave con el mismo cuerpo devuelve la respuesta original y con cualquier cambio del cuerpo (incluida la contraseña temporal) responde `422 IDEMPOTENCIA_CONFLICTO`. La huella es un **HMAC-SHA256 del JSON canónico del cuerpo completo** con el secreto `IDEMPOTENCY_SECRET` (variable de entorno, fuera de Git); en `claves_idempotencia` no se guarda ninguna contraseña ni hash simple de ella. Solo se almacenan respuestas 2xx y cada clave se serializa con un bloqueo asesor.
- La contraseña temporal (mínimo 12 caracteres) se guarda como hash Argon2; nunca se devuelve.
- No existe DELETE físico de usuarios o zonas: el SRS define desactivación, retiro o historial.

### Pruebas automatizadas (pytest)
Las pruebas viven en `backend/tests/` y **nunca tocan la base `ecoalert`**: usan una base aparte cuyo nombre debe terminar en `_test` (por defecto `ecoalert_test`; si no existe se crea, se importa `S05_S06_A1/esquema_bd.sql` y se carga la semilla controlada `tests/sql/semilla.sql`). La API se levanta sola en un puerto libre contra esa base. Requisitos: PostgreSQL/PostGIS en marcha (paso 1) y `backend/.env` creado (paso 3).

Desde VS Code:
1. Abrir la carpeta del repositorio (*File > Open Folder*) y un terminal integrado (<kbd>Ctrl</kbd>+<kbd>`</kbd>).
2. Seleccionar el intérprete: <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> > *Python: Select Interpreter* > `backend\.venv\Scripts\python.exe`.
3. Instalar las dependencias de pruebas (solo de pruebas, además de las de ejecución) y ejecutar:

```powershell
cd .\backend
python -m pip install -r requirements-test.txt
python -m pytest
```

También se pueden correr desde el panel *Testing*: <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> > *Python: Configure Tests* > *pytest* > carpeta `backend`.

| Archivo | Qué comprueba |
|---|---|
| `tests/sql/integridad.sql` + `test_integridad_sql.py` | 22 tablas, claves primarias y 32 claves foráneas, PostGIS (EPSG:32719) y 35 casos de restricciones (CHECK, UNIQUE, FK, índice parcial, historial con autor Sistema, idempotencia) dentro de una transacción que se revierte |
| `test_contrato.py` | OpenAPI válido, 38 operaciones, PUT presente y sin DELETE de usuarios, 166 criterios Must del SRS cubiertos, 62 schemas = 62 clases UML y rutas del backend contenidas en el contrato |
| `test_api_lecturas.py` | GET de alertas (paginación, filtros, 400), cargas, marcas, ajustes, historial (autor Sistema), trabajos, 404 y 400, con cada respuesta validada contra el esquema OpenAPI |
| `test_api_usuarios.py` | POST, GET, PUT y PATCH con persistencia en PostgreSQL, regla de la última coordinación, sesiones cerradas al desactivar, idempotencia HMAC (reintento idéntico, conflicto por cualquier campo incluida la contraseña, errores no almacenados, expiración a 24 h) y concurrencia (10 reintentos con la misma clave, 10 altas con el mismo correo, desactivaciones simultáneas) |

Variables opcionales: `TEST_DB_NAME` (otra base `*_test`; con un nombre nuevo se parte de una base limpia), `TEST_DATABASE_URL` (URL completa de una base `*_test`) y `API_BASE_URL` (usar una API ya levantada; se comprueba que lea la base de pruebas). Sin `IDEMPOTENCY_SECRET` en el entorno ni en `.env`, las pruebas usan uno efímero en memoria. El script SQL también corre con `psql`: `docker exec -i ecoalert_db psql -U ecoalert -d ecoalert_test -v ON_ERROR_STOP=1 < tests/sql/integridad.sql`.

### Verificación local (25/10/2026)
Entorno: Windows, Python 3.13.7, Docker Engine 29.8.0 e imagen `postgis/postgis:17-3.5` (PostgreSQL 17.5, PostGIS 3.5.2). El detalle de las correcciones y de lo pendiente está en `S05_S06_A1/revision_sql.md`, sección 7.
- **Suite `pytest`:** 76 de 76 pruebas aprobadas, tanto en la base existente `ecoalert_test` como en una base nueva (`ecoalert_limpia_test`) que la propia suite creó e inicializó: importación del esquema sin errores, 22 tablas, 35 casos de integridad SQL, contrato, lecturas, PUT, PATCH, idempotencia HMAC y concurrencia.
- **Postman/Newman** (`EcoAlert_pruebas`, API en el puerto 8001 sobre `ecoalert_test`): 31 requests de la colección (34 solicitudes HTTP contando 3 comprobaciones internas con `pm.sendRequest`), 68 aserciones, 0 fallos; ejecutada dos veces seguidas sin limpiar la base. La carpeta *1. Demostración* sola corre en menos de 1 s.
- **Sin verificar:** operaciones no implementadas, escrituras sobre marcas, ajustes e historial (no existen en la API), rendimiento (RNF-04) y seguridad (esta entrega no tiene autenticación).

### Pruebas con Postman
`S05_S06_A1/postman/` contiene la colección y dos entornos: `EcoAlert_pruebas` (API en el puerto **8001** sobre la base `ecoalert_test`, el que usan la demostración y Newman) y `EcoAlert_local` (API de desarrollo en el 8000 sobre `ecoalert`, sin datos de prueba; solo sirve para `GET /salud`). La colección escribe datos, así que el request *0.2* aborta si la API no apunta a la base de pruebas sembrada.

1. Preparar la base de pruebas una vez: `python -m pytest` (crea `ecoalert_test`, importa el esquema y carga la semilla).
2. Levantar la API de pruebas (desde `backend`, con el entorno virtual activo; el valor de `DATABASE_URL` definido en la sesión tiene prioridad sobre el de `.env`):

```powershell
$env:DATABASE_URL = 'postgresql://ecoalert:ecoalert_dev@localhost:5432/ecoalert_test'
python -m uvicorn app.main:app --port 8001 --env-file .env
```

3. Importar en Postman `EcoAlert_S05_S06_A1.postman_collection.json` y `EcoAlert_pruebas.postman_environment.json`, y seleccionar el entorno *EcoAlert - Pruebas*. O bien, desde la raíz del repositorio:

```powershell
npx --yes newman run S05_S06_A1/postman/EcoAlert_S05_S06_A1.postman_collection.json -e S05_S06_A1/postman/EcoAlert_pruebas.postman_environment.json
```

La carpeta *1. Demostración* tiene los seis requests del video (POST, GET y PUT de `/usuarios`, más `GET /alertas`, `GET /cargas-alertas` y `GET /zonas/{codigo}/historial`: seis operaciones sobre cinco rutas distintas); *1b* mantiene el `PATCH`; la carpeta *2* cubre `400`, `404`, `405`, `409`, `415`, `422`, idempotencia (incluido el cambio solo de contraseña) y la regla de la última coordinación con `PATCH` y `PUT`. Los correos y las claves se generan en cada ejecución, así que la colección se puede repetir sin limpiar la base.

### Limitaciones importantes
- Para que `POST /usuarios` y `PUT`/`PATCH /usuarios/{usuarioId}` cumplan con el SRS, debe exigirse rol Coordinación una vez implementado el login; por ahora es **solo demostración local**.
- El modelo SQL y las vistas OpenAPI no son equivalentes 1:1. Los DTO se construyen en la API.
- Las alertas sin zona o sin área no se publican en `GET /alertas` (el contrato exige ambas); cuando exista la ingesta deberán completarse en la misma transacción.
- Una respuesta `405` (p. ej. `DELETE /usuarios/{id}`) incluye `Allow` solo con los métodos de la primera ruta coincidente (`GET`), no con todos los permitidos; no afecta al contrato.
- Si se rota `IDEMPOTENCY_SECRET`, las claves de las últimas 24 h dejan de coincidir y sus reintentos responderán `422`; el secreto no debe cambiarse con operaciones en vuelo.
