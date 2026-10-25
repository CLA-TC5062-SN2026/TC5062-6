# Integración de S05-S06-A1 y S05-S06-A2

Documento de la rama `integracion/a1-a2`. Describe cómo se unieron el backend de **A1** (commit `eef17f5`, rama
`fix/s05-s06-validacion`) y el de **A2** (JWT, sesiones y roles, en `origin/main`), qué contratos y evidencias se conservan
y qué queda pendiente. Los entregables originales **no se modificaron**: `S05_S06_A1/` es idéntico a `eef17f5`
(`git diff fix/s05-s06-validacion -- S05_S06_A1/` no muestra diferencias) y los documentos, el contrato y las evidencias de
`S05_S06_A2/` son los de `origin/main`.

## 1. Qué contiene cada carpeta

| Carpeta | Contenido | Estado |
|---|---|---|
| `S05_S06_A1/` | Contrato OpenAPI v1.2.0 de A1 (con `PUT`), esquema SQL, diagramas, colección Postman y `pruebas_postman.mp4` | Sin cambios respecto de `eef17f5` |
| `S05_S06_A2/` | Contrato v1.2.0 de A2 (autenticación), revisión de seguridad, evidencias, colección Postman y, ahora, `pruebas/` con sus pruebas automatizadas y el script de pruebas manuales | Originales intactos; solo se añadió `pruebas/` |
| `S05_S06_integracion/` | Contrato integrado `openapi_integrado.yaml` (v1.3.0) y este documento | Nuevo |
| `backend/` | Backend único: A1 como base y la seguridad de A2 integrada | Modificado (ver README) |

## 2. Contrato integrado

Los dos contratos originales se rotularon "1.2.0" con contenidos distintos. El integrado (**1.3.0**) parte del de A2 y le añade lo de A1:

| Elemento | A1 (`eef17f5`) | A2 (`origin/main`) | Integrado |
|---|---|---|---|
| Sesión | `POST/GET/DELETE /auth/sesion` | `POST /auth/login`, `GET /auth/me`, `POST /auth/logout` | Rutas de A2 (D1) |
| Registro | No existe | `POST /auth/register` (alias de `crearUsuario`, sin `Idempotency-Key`) | De A2, **con** `Idempotency-Key` (D2) |
| Credenciales | `usuario` | `correo` | `correo` |
| `SesionCreada` | sin `expires_in` | con `expires_in` | con `expires_in` |
| Seguridad | `bearerAuth` | `BearerAuth` | `BearerAuth` |
| `PUT /usuarios/{usuarioId}` | Sí | No | Sí (propuesta adoptada, sin aprobación formal de todos los integrantes) |
| Longitud de contraseñas | solo `minLength: 12` | solo `minLength: 12` (el código limitaba a 72 bytes sin documentarlo) | `password_temporal` y `password_nueva`: 12 a 128; contraseñas del login y de `password_actual`: hasta 1024 |
| Operaciones | 38 | 38 | **39** (A1 sin `/auth/sesion` + A2) |

Los `x-roles` y `x-acceptance-criteria` de las operaciones comunes son idénticos en los tres; los 166 criterios Must del SRS
siguen cubiertos. `tests/test_contrato.py` comprueba estas relaciones (operaciones, esquemas que difieren y su motivo).

**Justificación de las rutas de A2:** su backend, sus pruebas, su revisión de seguridad y su evidencia usan `/auth/login`,
`/auth/me` y `/auth/logout`; volver a `/auth/sesion` invalidaría esa evidencia. Las operaciones de A1 se conservan todas.

**Justificación de los límites de contraseña:** el backend de A2 rechazaba más de 72 bytes por el límite de bcrypt, sin que el
contrato lo dijera. Con Argon2id ese tope ya no aplica, pero un máximo evita que una entrada gigante encarezca el hash. Se
documenta en el contrato en lugar de dejarlo implícito.

## 3. Qué viene de cada actividad en `backend/`

| Aspecto | Origen | Cómo quedó |
|---|---|---|
| Base de datos y SQL, CRUD, paginación, validaciones, respuestas y reglas de negocio | A1 | Sin cambios de comportamiento; las rutas pasaron de `main.py` a `routers/usuarios.py` y `routers/consultas.py` |
| Idempotencia HMAC-SHA256 | A1 | Compartida por `POST /usuarios` y `POST /auth/register` |
| Errores (400 para parámetros, 422 para cuerpo, español) | A1 | Se añadió `headers` a `ApiError` (para `WWW-Authenticate`) y registro de errores 500 |
| JWT, sesiones, revocación, 401/403, roles, cabeceras de seguridad, `/docs` apagado | A2 | Tal cual, usando `ApiError` en lugar de `fail()` |
| Configuración fail-fast (`JWT_SECRET`, `JWT_EXPIRATION`) | A2 | Tal cual; `IDEMPOTENCY_SECRET` sigue en `db.py` (A1) |
| Hash de contraseñas | A1 + A2 | **Argon2id** para las cuentas nuevas (A1); el verificador de A2 acepta Argon2id y bcrypt, migra bcrypt a Argon2id al iniciar sesión y trata un hash ilegible o una contraseña demasiado larga como credencial inválida (401), no como error 500 |
| CLI de la primera Coordinación, `docker-compose.yml`, `initdb` | A2 | Tal cual (`initdb` crea también `ecoalert_auth_test`) |

No se incorporaron: `serializacion.py` de A2 (A1 usa modelos de respuesta) ni los modelos de solicitud sin uso de A2
(cambio de estado, marcas y ajustes), que A1 ya había retirado.

## 4. Discrepancias identificadas

| Tema | Discrepancia | Resolución |
|---|---|---|
| PATCH | El contrato exige `application/merge-patch+json` (415 si no); el backend de A2 aceptaba `application/json` | Se mantiene el comportamiento de A1 (el del contrato); las pruebas de A2 envían el tipo correcto |
| PUT | El contrato de A2 y su backend no lo tienen; A1 sí | Incluido en el contrato integrado y protegido para Coordinación; probado con las mismas reglas que PATCH (última coordinación, revocación de sesiones) |
| Registro | `/auth/register` de A2 no pedía `Idempotency-Key`; el contrato 1.1.0 la exige a todo POST de creación | Es alias de `POST /usuarios` y la exige (D2); las pruebas y el script de A2 envían la cabecera |
| Hash | A2 creaba bcrypt; A1 crea Argon2id | Argon2id para cuentas nuevas (D3); bcrypt solo se verifica y se migra |
| Parámetros inválidos | A2 respondía 422 incluso para un UUID de ruta inválido; el contrato dice 400 | Se mantiene el de A1 (400 para ruta, query y cabecera) |
| Base de pruebas | A2 vaciaba `usuarios` y `sesiones` (CASCADE) en `ecoalert_test`, lo que borra la semilla de A1 | Bases separadas (D4): la de A2 es `ecoalert_auth_test`, y su conftest se niega a usar la de A1 |
| `Allow` en 405 | Solo lista los métodos de la primera ruta coincidente (Starlette) | Sin cambios; se documenta en el README |

## 5. Evidencias originales

- **Intactos:** `S05_S06_A1/pruebas_postman.mp4`, las tres colecciones/entornos Postman de A1 y toda la carpeta `S05_S06_A1/`; en `S05_S06_A2/`, la colección Postman, `evidencias/`, `revision_seguridad.md`, `paso_a_paso_video.md`, el contrato y el UML.
- **Ya no se reproducen tal cual contra el backend integrado** (describen los backends originales, no se alteraron para ocultarlo):
  - Postman de A1: no envía `Authorization`; sus solicitudes a `/api/v1` responderían 401 (solo `/salud` es público).
  - Postman de A2: su primer request de registro no envía `Idempotency-Key` y respondería 400. No se ejecutó Newman con ninguna de las dos; es una conclusión por lectura de las colecciones.
  - `S05_S06_A2/evidencias/pruebas_manuales_curl.txt` es la salida del backend original de A2 (hashes bcrypt, registro sin clave).
  - Los documentos de A2 citan `backend/scripts/pruebas_manuales.sh` y `tests/test_auth.py`, `test_security.py`, `test_config.py` y `test_proteccion_rutas.py`; ahora están en `S05_S06_A2/pruebas/`. Sus cifras (101 pruebas, 30 en `test_auth.py`, 16 en `test_security.py`) corresponden al backend original.
- Las pruebas automatizadas de A2 se movieron de `backend/tests/` a `S05_S06_A2/pruebas/` con las adaptaciones de la sección 4. Se conservaron todas sus aserciones de seguridad; las que cambian son las de algoritmo de hash (de bcrypt a Argon2id), el límite de 72 bytes (ahora 128), las cabeceras de PATCH y la clave de idempotencia.

## 6. Diferencias con `origin/main` dentro de `S05_S06_A1/`

Por la restricción de dejar esa carpeta exactamente como en `eef17f5`, **no se incorporaron** los cambios que `origin/main` trae allí:
`evidencias/newman_flujo_video.txt`, `paso_a_paso_video.md`, `postman/EcoAlert_CRUD_S05_S06_A1.postman_collection.json`, y las
ediciones a `diagrama_clases_equipo.puml` (sin `!pragma layout smetana`), `diagrama_componentes_equipo.puml`,
`diferencias_diseno.md`, `openapi_equipo.yaml` (`BearerAuth`) y `revision_sql.md`. Siguen en `origin/main`; si esta rama se
fusiona después en `main`, esos archivos aparecerían como revertidos. Hay que decidir antes qué versión prevalece.

## 7. Pruebas

`python -m pytest` desde `backend` ejecuta las dos suites (225 pruebas: 101 de A1 e integración, 124 de A2). Detalles, bases
y variables en `backend/README.md`. Resultados y pendientes de la integración se resumen en la sección de verificación de ese README.

## 8. Pendientes

- Decidir el destino de los cambios de `origin/main` en `S05_S06_A1/` (sección 6) antes de abrir el Pull Request.
- Colecciones Postman integradas (login y token, `Idempotency-Key`): las originales no se tocaron y ya no sirven contra este backend.
- Actualizar `S05_S06_A1/revision_sql.md` y `diferencias_diseno.md` (no se hizo por la restricción) para reflejar la integración.
- Ligar `claves_idempotencia` a la cuenta que solicita, si el equipo lo considera necesario (hoy es global).
- Operaciones del contrato sin implementar (19 de 39).
