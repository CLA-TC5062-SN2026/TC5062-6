# Integración técnica del backend (A1 + A2)

Documentación técnica auxiliar del backend compartido. Los entregables de la rúbrica son `S05_S06_A1/` y `S05_S06_A2/`; este
documento no es una actividad adicional. Describe cómo se unieron el backend de **A1** (commit `eef17f5`, rama
`fix/s05-s06-validacion`) y el de **A2** (JWT, sesiones y roles, en `origin/main`), qué contratos y evidencias se conservan
y qué queda pendiente. Los entregables originales **no se modificaron**: `S05_S06_A1/` es idéntico a `eef17f5`
(`git diff fix/s05-s06-validacion -- S05_S06_A1/` no muestra diferencias) y los documentos, el contrato y las evidencias
originales de `S05_S06_A2/` son los de `origin/main`.

## 1. Dónde está cada cosa

| Ubicación | Contenido | Estado |
|---|---|---|
| `S05_S06_A1/` | Contrato OpenAPI v1.2.0 de A1 (con `PUT`), esquema SQL, diagramas, colección Postman y `pruebas_postman.mp4` | Sin cambios respecto de `eef17f5` |
| `S05_S06_A2/` | Contrato v1.2.0 de A2 (autenticación), revisión de seguridad, evidencias y colección Postman originales; para demostrar la seguridad del backend final se añadieron `pruebas/` (pruebas automatizadas y script de pruebas manuales), `postman/EcoAlert_Auth_S05_S06_A2_backend_final.*` (colección y entorno) y `evidencias/newman_backend_final.txt` | Originales intactos; solo se añadieron esos archivos |
| `backend/` | Backend único: A1 como base y la seguridad de A2 integrada; pruebas de A1 en `tests/` | Modificado (ver README) |
| `backend/docs/` | Este documento, el contrato integrado `openapi_integrado.yaml` (v1.3.0), que implementa el backend y verifican las pruebas, y `antecedentes_main_A1/` (aportes de Miguel en `origin/main` para A1) | Documentación técnica auxiliar |

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
| Idempotencia HMAC-SHA256 | A1 | Compartida por `POST /usuarios` y `POST /auth/register`; la clave queda asociada a la cuenta autenticada (ver sección 4) |
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
| Idempotencia entre cuentas | `claves_idempotencia` tiene como clave primaria solo el UUID de la clave, así que antes de A2 (sin usuarios autenticados) daba igual quién la usara. Con JWT, otra cuenta que repitiera una clave y su cuerpo habría recibido la respuesta guardada de la primera (incluidos el id y el `Location` del recurso) | La clave se guarda con `operacion = crearUsuario:<id de la cuenta>`; otra cuenta que la reutilice recibe `422 IDEMPOTENCIA_CONFLICTO` sin datos del recurso, y la cuenta dueña sigue recibiendo su respuesta original. No cambia el esquema SQL (`S05_S06_A1/` no se toca). Probado en `test_integracion_auth.py` y en Newman (3.7 y 3.8) |
| Hash | A2 creaba bcrypt; A1 crea Argon2id | Argon2id para cuentas nuevas (D3); bcrypt solo se verifica y se migra |
| Parámetros inválidos | A2 respondía 422 incluso para un UUID de ruta inválido; el contrato dice 400 | Se mantiene el de A1 (400 para ruta, query y cabecera) |
| Base de pruebas | A2 vaciaba `usuarios` y `sesiones` (CASCADE) en `ecoalert_test`, lo que borra la semilla de A1 | Bases separadas (D4): la de A2 es `ecoalert_auth_test`, y su conftest se niega a usar la de A1 |
| `Allow` en 405 | Solo lista los métodos de la primera ruta coincidente (Starlette) | Sin cambios; se documenta en el README |

## 5. Evidencias originales

- **Intactos:** `S05_S06_A1/pruebas_postman.mp4`, las tres colecciones/entornos Postman de A1 y toda la carpeta `S05_S06_A1/`; en `S05_S06_A2/`, la colección Postman, `evidencias/`, `revision_seguridad.md`, `paso_a_paso_video.md`, el contrato y el UML.
- **Ya no se reproducen tal cual contra el backend final** (describen los backends originales, no se alteraron para ocultarlo). Se ejecutaron con Newman contra el backend final:
  - Postman de A1 (`EcoAlert_S05_S06_A1`, con su entorno de pruebas): 31 de 34 requests responden 401 porque no envía `Authorization` (solo `/salud` es público); 59 de 68 aserciones fallan.
  - Postman de A2 (`EcoAlert_Auth_S05_S06_A2`): su registro no envía `Idempotency-Key` y responde 400; arrastra los pasos 2, 3 y 6 (5 de 9 aserciones fallan). Los pasos de login de Coordinación, listado y 401 sin token pasan.
  - Para el backend final se añadió `S05_S06_A2/postman/EcoAlert_Auth_S05_S06_A2_backend_final.postman_collection.json`, con su entorno y la evidencia `S05_S06_A2/evidencias/newman_backend_final.txt`.
  - `S05_S06_A2/evidencias/pruebas_manuales_curl.txt` es la salida del backend original de A2 (hashes bcrypt, registro sin clave).
  - Los documentos de A2 citan `backend/scripts/pruebas_manuales.sh` y `tests/test_auth.py`, `test_security.py`, `test_config.py` y `test_proteccion_rutas.py`; ahora están en `S05_S06_A2/pruebas/`. Sus cifras (101 pruebas, 30 en `test_auth.py`, 16 en `test_security.py`) corresponden al backend original.
- Las pruebas automatizadas de A2 se movieron de `backend/tests/` a `S05_S06_A2/pruebas/` con las adaptaciones de la sección 4. Se conservaron todas sus aserciones de seguridad; las que cambian son las de algoritmo de hash (de bcrypt a Argon2id), el límite de 72 bytes (ahora 128), las cabeceras de PATCH y la clave de idempotencia.

## 6. Aportes de Miguel en `origin/main` para A1 (antecedentes)

`origin/main` trae, dentro del área de A1, trabajo de Miguel hecho sobre el backend de A1 original (`9f5070d`). Para dejar
`S05_S06_A1/` exactamente como en `eef17f5`, esos archivos **no se copiaron a esa carpeta**; se conservan, byte a byte
desde `origin/main`, en `backend/docs/antecedentes_main_A1/`:

| Archivo | Qué es |
|---|---|
| `evidencias/newman_flujo_video.txt`, `paso_a_paso_video.md`, `postman/EcoAlert_CRUD_S05_S06_A1.postman_collection.json` | Evidencia y guía de su video de CRUD sobre el backend de A1 original |
| `revision_sql.md` | Importación del esquema (21 tablas) y correcciones al código generado (C-01 a C-14) |
| `diagrama_componentes_equipo.puml`, `diagrama_clases_equipo.puml` | Su diagrama de componentes y el de clases sin `!pragma layout smetana` |
| `diferencias_diseno.md` | Misma comparación sin escapes de Markdown y sin la frase sobre la aprobación formal |

No se copió su `openapi_equipo.yaml`: solo renombra `bearerAuth` a `BearerAuth` (y rotula 1.1.0), cambios que ya están en
`S05_S06_A2/openapi_equipo.yaml` y en el contrato integrado.

Lo que describen estos antecedentes ya no coincide con el backend integrado: C-11 a C-14 figuran allí como pendientes y A1
los resolvió (idempotencia, paginación, `UsuarioRef`, 415 en PATCH); `diferencias_diseno.md` no menciona `PUT`. **Consecuencia
para un futuro Pull Request a `main`:** como la integración deja `S05_S06_A1/` igual a `eef17f5`, esos archivos aparecerían
eliminados o revertidos dentro de `S05_S06_A1/` (siguen en `antecedentes_main_A1/` y en el historial de `origin/main`). El
equipo debe aceptarlo o acordar otra solución antes de publicar.

## 7. Estado de las 39 operaciones del contrato integrado

**20 implementadas y 19 pendientes.** Se obtuvo comparando el contrato con las rutas que monta la aplicación; `tests/test_contrato.py`
comprueba que las 20 implementadas están en el contrato y que no hay rutas fuera de él.

| Módulo | Método | Ruta (`/api/v1`) | Operación | Roles | Estado |
|---|---|---|---|---|---|
| Autenticación | `POST` | `/auth/login` | iniciarSesion | público | Implementada (A2) |
| Autenticación | `POST` | `/auth/register` | registrarUsuario | coordinación | Implementada (A2 + A1) |
| Autenticación | `GET` | `/auth/me` | obtenerSesionActual | ambos | Implementada (A2) |
| Autenticación | `POST` | `/auth/logout` | cerrarSesion | ambos | Implementada (A2) |
| Autenticación | `PUT` | `/auth/password` | cambiarPassword | ambos | Implementada (A2) |
| Usuarios | `GET` | `/usuarios` | listarUsuarios | coordinación | Implementada (A1) |
| Usuarios | `POST` | `/usuarios` | crearUsuario | coordinación | Implementada (A1) |
| Usuarios | `GET` | `/usuarios/{usuarioId}` | obtenerUsuario | coordinación | Implementada (A1) |
| Usuarios | `PUT` | `/usuarios/{usuarioId}` | reemplazarUsuario | coordinación | Implementada (A1) |
| Usuarios | `PATCH` | `/usuarios/{usuarioId}` | actualizarUsuario | coordinación | Implementada (A1) |
| Alertas | `GET` | `/alertas` | listarAlertas | ambos | Implementada (A1) |
| Alertas | `GET` | `/cargas-alertas` | listarCargasAlertas | ambos | Implementada (A1) |
| Alertas | `GET` | `/cargas-alertas/{cargaId}` | obtenerCargaAlertas | ambos | Implementada (A1) |
| Trabajos | `GET` | `/trabajos/{trabajoId}` | obtenerTrabajo | ambos | Implementada (A1) |
| Revisión de zonas | `GET` | `/zonas/{codigo}/marcas` | listarMarcasZona | ambos | Implementada (A1) |
| Revisión de zonas | `GET` | `/zonas/{codigo}/marcas/{marcaId}` | obtenerMarca | ambos | Implementada (A1) |
| Revisión de zonas | `GET` | `/zonas/{codigo}/ajustes` | listarAjustesZona | ambos | Implementada (A1) |
| Revisión de zonas | `GET` | `/zonas/{codigo}/ajustes/{ajusteId}` | obtenerAjuste | ambos | Implementada (A1) |
| Revisión de zonas | `GET` | `/zonas/{codigo}/historial` | obtenerHistorialZona | ambos | Implementada (A1) |
| Revisión de zonas | `GET` | `/zonas/{codigo}/historial/{entradaId}` | obtenerEntradaHistorial | ambos | Implementada (A1) |
| Archivos | `POST` | `/archivos` | subirArchivo | analista | Pendiente |
| Capas de referencia | `GET` | `/capas-referencia` | listarCapasReferencia | ambos | Pendiente |
| Capas de referencia | `GET` | `/capas-referencia/{tipoCapa}/versiones` | listarVersionesCapa | ambos | Pendiente |
| Capas de referencia | `POST` | `/capas-referencia/{tipoCapa}/versiones` | cargarVersionCapa | analista | Pendiente |
| Alertas | `POST` | `/cargas-alertas` | ingerirAlertas | analista | Pendiente |
| Mapa | `GET` | `/mapa/capas` | listarCapasMapa | ambos | Pendiente |
| Mapa | `GET` | `/mapa/capas/{capaMapaId}/elementos` | obtenerElementosCapa | ambos | Pendiente |
| Mapa | `GET` | `/mapa/capas/{capaMapaId}/elementos/{elementoId}` | obtenerElementoCapa | ambos | Pendiente |
| Zonas | `GET` | `/zonas` | listarZonas | ambos | Pendiente |
| Zonas | `GET` | `/zonas/{codigo}` | obtenerZona | ambos | Pendiente |
| Revisión de zonas | `POST` | `/zonas/{codigo}/cambios-estado` | cambiarEstadoZona | analista | Pendiente |
| Revisión de zonas | `POST` | `/zonas/{codigo}/ajustes` | ajustarPrioridad | analista | Pendiente |
| Revisión de zonas | `PATCH` | `/zonas/{codigo}/ajustes/{ajusteId}` | retirarAjuste | analista | Pendiente |
| Revisión de zonas | `POST` | `/zonas/{codigo}/marcas` | registrarMarcaAnalista | analista | Pendiente |
| Revisión de zonas | `PATCH` | `/zonas/{codigo}/marcas/{marcaId}` | retirarMarcaAnalista | analista | Pendiente |
| Análisis de periodos | `GET` | `/analisis` | listarAnalisis | ambos | Pendiente |
| Análisis de periodos | `POST` | `/analisis` | ejecutarComparacion | ambos | Pendiente |
| Análisis de periodos | `GET` | `/analisis/{analisisId}` | obtenerAnalisis | ambos | Pendiente |
| Exportaciones | `GET` | `/exportaciones/zonas` | exportarZonas | analista | Pendiente |

Las pendientes (archivos, capas, ingesta, mapa, zonas, escrituras de revisión, análisis y exportación) quedan fuera del alcance
de estas dos actividades y no se simulan.

## 8. Pruebas y resultados (25/10/2026)

Entorno: Windows, Python 3.13.7, PostgreSQL 17.5 + PostGIS 3.5.2 en Docker, Node con `npx newman`.

| Verificación | Resultado |
|---|---|
| `python -m pytest` desde `backend` (ambas suites) | **226 de 226** (102 de A1 e integración en `ecoalert_test` + 124 de A2 en `ecoalert_auth_test`); también por separado, en orden inverso y desde la raíz |
| Newman, `S05_S06_A2/postman/EcoAlert_Auth_S05_S06_A2_backend_final.postman_collection.json`, API en el 8001 sobre una base nueva `ecoalert_postman_test` | 43 requests (48 solicitudes HTTP con las 5 `pm.sendRequest` de verificación), 58 aserciones, **0 fallos**, 3 corridas seguidas sin limpiar la base; salida en `S05_S06_A2/evidencias/newman_backend_final.txt` |
| 401 | Matriz de A2 sobre todas las rutas montadas (sin token y con token inválido), token alterado/expirado/sin `exp`/`alg: none`, sesión inactiva (29 y 31 min), cerrada o de cuenta desactivada; Newman 2.1, 2.2, 2.11, 2.12 y 2.15 |
| 403 | `ROL_NO_PERMITIDO` según los `x-roles` del contrato en todas las rutas y `CAMBIO_PASSWORD_REQUERIDO` sobre las rutas de A1; Newman 2.5, 2.8 y 2.9 |
| Revocación de sesiones | Logout, cambio de contraseña (cierra las demás sesiones) y desactivación con `PUT` o `PATCH` (el token deja de servir al instante); Newman 2.10 a 2.15 |
| Persistencia | POST, PUT y PATCH comprobados con una consulta directa a PostgreSQL (pytest) y con un `GET` posterior (Newman 1.2, 1.4, 1.5, 2.10 y 3.15); hash Argon2id en la base |
| Idempotencia | Reintento idéntico, conflicto por cuerpo, concurrencia, expiración a 24 h y **no reutilización entre cuentas** (pytest y Newman 3.7 y 3.8) |
| Mutaciones temporales (se revirtieron) | Quitar autenticación y rol de las lecturas de A1 hace fallar 31 pruebas; volver a la clave de idempotencia global hace fallar la prueba de aislamiento entre cuentas |

Preparar la base de Newman exige este orden: esquema, **CLI de Coordinación**, semilla. La semilla de A1 trae una cuenta de
coordinación (inactiva) y la CLI se niega a crear la primera si ya existe cualquiera (ver `backend/README.md`).

## 9. Pendientes

- Decidir el destino de los aportes de `origin/main` en `S05_S06_A1/` antes de abrir el Pull Request (sección 6).
- Actualizar `S05_S06_A1/revision_sql.md` y `diferencias_diseno.md` para reflejar la integración: no se hizo por la restricción de dejar esa carpeta intacta.
- Las colecciones Postman originales de A1 y A2 y las evidencias de A2 describen los backends anteriores (sección 5); se conservan sin cambios y no funcionan contra el backend final.
- La CLI de A2 se niega a crear la primera Coordinación si existe una cuenta de coordinación inactiva (caso de la semilla de A1); es el comportamiento original de A2 y se evita con el orden de preparación.
- Si se rota `IDEMPOTENCY_SECRET`, las claves de las últimas 24 h dejan de coincidir; `IDEMPOTENCY_SECRET` debe estar en el entorno del proceso (`--env-file`), a diferencia de las variables JWT, que también se leen de `.env`.
- 19 de las 39 operaciones del contrato siguen sin implementar (sección 7).
