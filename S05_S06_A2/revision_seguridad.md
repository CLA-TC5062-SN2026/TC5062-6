# Revisión de seguridad — Autenticación JWT y protección de rutas

**Proyecto:** EcoAlert Tambopata · **Equipo 6** · TC5062 Gpo 10
**Fecha:** 24/10/2026
**Base revisada:** backend CRUD de S05-S06-A1 (commit `9f5070d`) y el módulo de autenticación generado con el agente en esta actividad.
**Fuentes de verdad:** `SRS_equipo.md` (v1.0), `S05_S06_A2/openapi_equipo.yaml` (v1.2.0) y `S05_S06_A2/diagrama_clases_equipo.puml`.
**Stack:** Python 3.12 · FastAPI · PyJWT 2 · pwdlib (bcrypt + Argon2) · psycopg 3 · PostgreSQL 17 + PostGIS 3.5.

---

## 0. Resumen

| Aspecto | Resultado |
|---|---|
| Módulo de autenticación | `POST /auth/register` (201, sin contraseña), `POST /auth/login` (200 con JWT, 401 genérico), `GET /auth/me`, `POST /auth/logout`, `PUT /auth/password`. |
| Expiración del JWT | Explícita y obligatoria: `exp = iat + JWT_EXPIRATION`; además, la sesión expira a los 30 min sin actividad (PS-12). |
| Secreto del JWT | Variable de entorno `JWT_SECRET`, sin valor por defecto; la API no arranca si falta, si mide menos de 32 bytes o si conserva el valor de plantilla. |
| Middleware | Rechaza con 401 la petición sin token, con firma inválida, expirada, de sesión cerrada o inactiva, o de una cuenta desactivada. |
| Control por rol | 18 rutas protegidas; cada una aplica los `x-roles` del contrato (403 `ROL_NO_PERMITIDO`). |
| Pruebas automatizadas | **101 pruebas, 101 aprobadas**, contra PostgreSQL real. Prueba de mutación: 4 de 4 regresiones inyectadas fueron detectadas. |
| Pruebas manuales (curl) | Los 4 casos exigidos dan el resultado esperado (401, 401, 403, 200). Evidencia: `evidencias/pruebas_manuales_curl.txt`. |
| Flujo del video (Postman) | Video `pruebas_auth.mp4` (register → login → me → ruta protegida → sin token → rol incorrecto). Antes de grabar, el mismo flujo se ejecutó con Newman: 7 peticiones y 9 aserciones aprobadas (`evidencias/newman_flujo_video.txt`). |

---

## 1. Decisiones de diseño y su justificación

Cada decisión indica la alternativa descartada y su fundamento en SWEBOK v4 y en la documentación técnica (RFC, OWASP, documentación oficial). Las referencias completas están en la sección 7.

### D-01 · `/auth/register` exclusivo de Coordinación; la primera cuenta se crea con un comando de arranque

- **Decisión:** `POST /auth/register` exige un token de Coordinación y se comporta igual que `crearUsuario` (`POST /usuarios`); ambas rutas comparten la misma función (`insertar_usuario`, `backend/app/routers/usuarios.py:21`). La primera cuenta de Coordinación se crea con `python -m app.cli crear-coordinacion`, que se niega a correr si ya existe una.
- **Alternativa descartada:** registro anónimo (abierto a cualquiera).
- **Justificación:**
  - **SRS:** RF-02 asigna la creación de cuentas solo a Coordinación, y RNF-01 exige autenticación en toda función. Un registro anónimo permitiría que cualquiera se diera de alta en un sistema que maneja información territorial sensible.
  - **OWASP API Security Top 10 (2023), API5 — *Broken Function Level Authorization*:** una función administrativa (alta de cuentas) expuesta a usuarios sin el rol correspondiente es exactamente este riesgo.
  - **SWEBOK v4, KA *Software Requirements*:** la trazabilidad exige que el código implemente el requisito acordado y no una interpretación local. Cuando el enunciado de la actividad (registro) y el SRS (alta por Coordinación) chocaban, se ajustó el contrato y se conservó la regla de negocio.
  - El comando de arranque es el patrón de `createsuperuser` de Django: resuelve el problema del "huevo y la gallina" sin abrir una ruta pública. La contraseña se pide sin eco (`getpass`) o se lee de una variable de entorno, nunca de un argumento, porque los argumentos quedan en el historial del shell y en `ps`.

### D-02 · Rutas `/api/v1/auth/{login,register,me,logout,password}` y contrato v1.2.0 en `S05_S06_A2/`

- **Decisión:** se conserva el prefijo versionado `/api/v1` que declara `servers` en el contrato y se adoptan los nombres de la actividad. El contrato pasa a **v1.2.0** (`/auth/sesion` se divide en `login`, `me` y `logout`, y se añade `register`). La copia de `S05_S06_A1/` no se modifica.
- **Alternativas descartadas:** `/api/auth/...` sin versión, o mantener `/auth/sesion`.
- **Justificación:**
  - **Spec-first:** primero se actualizó el contrato (validado con `openapi-spec-validator`: `OK`) y después el código. La prueba `test_RNF_02_cada_ruta_aplica_los_x_roles_del_contrato` lee el YAML y falla si el código se desvía de él.
  - **SWEBOK v4, KA *Software Configuration Management*:** un artefacto entregado constituye una línea base; los cambios generan una versión nueva e identificable (1.2.0, con historial de cambios en `info.description`) en lugar de alterar la evidencia de S05.
  - **Login responde 200 y no 201:** RFC 9110 §15.3.2 reserva 201 para un recurso nuevo identificado por `Location`. El login entrega una credencial, igual que el *token endpoint* de OAuth 2.0 (RFC 6749 §5.1, que responde 200).
  - El prefijo `/api/v1` permite publicar una versión incompatible sin romper clientes. Además, el código anterior no lo tenía aunque el contrato lo declaraba (hallazgo H-08).

### D-03 · JWT con sesión registrada en el servidor (no puramente *stateless*)

- **Decisión:** cada login inserta una fila en `sesiones` con `id = jti` y `token_hash = SHA-256(token)`. El middleware valida la firma **y** la sesión en una sola sentencia `UPDATE … RETURNING` (`backend/app/dependencies.py:29`), que además renueva `ultima_actividad`.
- **Alternativa descartada:** JWT *stateless*, validado solo por su firma.
- **Justificación:**
  - **SRS:** RF-01-AC-4 (sesión inactiva por 31 min → 401) y RF-01-AC-6 (token reutilizado después del logout → 401) **no se pueden cumplir** con un JWT puramente *stateless*: su firma sigue siendo válida hasta `exp`. El contrato ya lo exigía ("el servidor guarda la sesión asociada al `jti`").
  - **OWASP ASVS v4.0.3, V3.3.1:** el logout y la expiración deben invalidar el token de sesión.
  - **RFC 8725 §3.10 (*Do Not Trust Received Claims*):** el servidor confirma contra su propio estado.
  - Se guarda el **hash** del token y no el token: una filtración de la tabla `sesiones` no entrega credenciales utilizables.
  - Una sola sentencia atómica evita la condición de carrera entre "leer la sesión" y "renovar la actividad". La prueba de mutación lo confirma: si se elimina la consulta de sesión, falla `test_RF_01_AC_6_token_no_sirve_despues_de_logout`.

### D-04 · HS256 con algoritmo fijo, claims obligatorios, emisor y audiencia

- **Decisión:** `jwt.decode(..., algorithms=['HS256'], issuer=..., audience=..., options={'require': [exp, iat, nbf, iss, aud, sub, jti]})` (`backend/app/security.py:61`).
- **Alternativas descartadas:** aceptar el algoritmo que declare la cabecera, o hacer opcional `exp`.
- **Justificación:**
  - **RFC 8725 §3.1 (*Perform Algorithm Verification*):** la lista blanca de algoritmos evita el ataque `alg: none` y la confusión de algoritmos. Verificado en `test_token_con_algoritmo_distinto_de_hs256_se_rechaza[none|HS512]`.
  - **RFC 8725 §3.8 y §3.9:** validar el emisor (`iss`) y la audiencia (`aud`) impide reutilizar un token emitido para otro sistema que compartiera el secreto.
  - **RFC 7519 §4.1.4:** `exp` es opcional en el estándar; aquí se vuelve **obligatorio**, de modo que un token sin `exp` se rechaza (`test_token_sin_claim_obligatorio_se_rechaza[exp]`).
  - **HS256 frente a RS256:** el emisor y el verificador son el mismo monolito (`arquitectura_equipo.md`, ARQ-07/08), así que una clave simétrica basta y es más simple (*economy of mechanism*). RS256 conviene cuando otro servicio debe verificar sin poder firmar; queda como evolución si se separan servicios.
  - **PyJWT** es la librería que usa la documentación oficial de FastAPI para JWT; `python-jose` dejó de mantenerse.

### D-05 · Secreto y expiración por variables de entorno, validados al arrancar (*fail-fast*)

- **Decisión:** `JWT_SECRET` y `JWT_EXPIRATION` son obligatorios y no tienen valor por defecto (`backend/app/config.py:18-21`). El secreto debe tener ≥ 32 bytes y no puede conservar el texto de plantilla; la expiración debe estar entre 1 y 86400 s. `.env.example` documenta ambas; `.env` está en `.gitignore`.
- **Alternativa descartada:** un secreto por defecto "de desarrollo" escrito en el código.
- **Justificación:**
  - **The Twelve-Factor App, factor III (*Config*):** la configuración que cambia entre entornos, y en especial los secretos, vive en el entorno y no en el código.
  - **RFC 7518 §3.2:** la clave de HS256 debe tener al menos el tamaño de la salida del hash (256 bits = 32 bytes). **RFC 8725 §3.5** advierte contra claves de baja entropía, que permiten ataques de fuerza bruta fuera de línea contra el token.
  - **SWEBOK v4, KA *Software Security*, principio *fail-safe defaults*:** ante una configuración insegura, el sistema no arranca, en vez de arrancar inseguro. Lo verifican 8 casos en `tests/test_config.py`.
  - `JWT_EXPIRATION=28800` (8 h) es el **tiempo absoluto**: una jornada de trabajo, en línea con la guía de OWASP *Session Management*. La protección cotidiana la da la expiración por **inactividad** de 30 min (PS-12).

### D-06 · bcrypt (costo 12) para hashes nuevos, verificación de Argon2id heredado y migración al iniciar sesión

- **Decisión:** `PasswordHash((BcryptHasher(rounds=12), Argon2Hasher()))` (`backend/app/security.py:24`). Los hashes nuevos son bcrypt; un hash Argon2id existente se sigue verificando y se re-hashea a bcrypt en el siguiente login exitoso (`test_login_migra_hash_argon2_heredado_a_bcrypt`).
- **Justificación:**
  - La actividad pide bcrypt, y el SRS (RNF-03) acepta "bcrypt o Argon2". **OWASP *Password Storage Cheat Sheet*** recomienda Argon2id en primer lugar y admite bcrypt con factor de trabajo ≥ 10. Costo 12 está por encima del mínimo y tarda unos 200 ms por verificación en este equipo, tolerable para un login.
  - **Límite de 72 bytes de bcrypt:** la librería `bcrypt` 5 lanza `ValueError` con contraseñas más largas (verificado en este entorno). Sin control, eso sería un error 500 provocable por cualquiera (hallazgo H-03). Las contraseñas nuevas se limitan a 72 bytes (422) y el login trata las entradas largas como credencial inválida (401).
  - **Limitación conocida:** OWASP ASVS V2.1.2 pide admitir contraseñas de al menos 64 caracteres. Con caracteres ASCII se cumple (72 > 64); con caracteres multibyte (p. ej., `ñ`), el máximo efectivo baja. Es la razón por la que OWASP prefiere Argon2id; queda documentado en la sección 5.
  - La migración progresiva evita invalidar cuentas existentes (**SWEBOK v4, KA *Software Maintenance***: cambio sin interrupción del servicio).

### D-07 · Middleware como dependencias de FastAPI, con denegación por defecto

- **Decisión:** `autenticar` se aplica a nivel de router a todo `/api/v1` excepto `POST /auth/login` (`backend/app/main.py:58`). `RequiereRol(...)` declara en cada ruta los roles del contrato.
- **Alternativa descartada:** un middleware ASGI que compare la URL contra una lista de rutas protegidas.
- **Justificación:**
  - **SWEBOK v4, KA *Software Security*, principios de Saltzer y Schroeder:** *fail-safe defaults* (una ruta nueva nace protegida aunque nadie lo recuerde) y *complete mediation* (toda petición pasa por la verificación).
  - **OWASP ASVS V4.1.1 / V4.1.5:** el control de acceso se aplica en una capa de servicio confiable y falla de forma segura.
  - **Documentación de FastAPI (*Security*, *Dependencies in path operation decorators*):** las dependencias son el mecanismo idiomático. A diferencia de un middleware ASGI, se publican en el esquema OpenAPI (`BearerAuth`), se prueban de forma aislada y no dependen de comparar cadenas de URL, que es frágil ante cambios de prefijo o parámetros.
  - FastAPI guarda en caché una dependencia dentro de la misma petición, así que `autenticar` corre una sola vez aunque la declaren el router y `RequiereRol`.

### D-08 · La autorización usa el rol vigente en la base de datos, no el claim `rol` del token

- **Justificación:** si Coordinación cambia el rol de una cuenta o la desactiva, el cambio debe surtir efecto de inmediato y no cuando expire el token (hasta 8 h después). **OWASP ASVS V4** pide que las decisiones de acceso se basen en el estado actual del servidor, y **RFC 8725 §3.10** recomienda no confiar ciegamente en los claims recibidos. Como la consulta de sesión ya va a la base de datos (D-03), el costo adicional es nulo. Lo verifican `test_cambio_de_rol_se_aplica_aunque_el_token_diga_otro_rol` y `test_desactivar_cuenta_invalida_sus_tokens_al_instante`.

### D-09 · Orden de verificación: 401 → 403 por rol → 403 por contraseña temporal

- **Justificación:** sin identidad no hay nada que autorizar (401, RFC 9110 §15.5.2). Entre los dos 403, el de rol es **permanente** (ese rol nunca tendrá acceso), mientras que el de contraseña temporal es **remediable**. Informar primero el permanente evita que el usuario cambie su contraseña solo para recibir otro 403. `me`, `logout` y `password` quedan fuera del 403 por contraseña temporal porque son las únicas operaciones permitidas durante ese estado (RF-02-AC-4).

### D-10 · Errores RFC 9457, `WWW-Authenticate` según RFC 6750 y login sin filtración de información

- **Decisión:** todos los errores son `application/problem+json` con `codigo` y `mensaje` (`backend/app/errors.py`). Los 401 incluyen `WWW-Authenticate: Bearer realm="ecoalert"` y, si el token es inválido, `error="invalid_token"`. El login responde el mismo 401 (`CREDENCIALES_INVALIDAS`, "Usuario o contraseña incorrectos") para correo inexistente, contraseña incorrecta o cuenta desactivada, y verifica contra un hash señuelo cuando el correo no existe.
- **Justificación:**
  - **Contrato del equipo** (convenciones de respuesta) y **RFC 9457**.
  - **RFC 6750 §3 y §3.1:** sin credenciales no se envía código de error; con un token inválido, `invalid_token`. **RFC 9110 §15.5.2:** un 401 debe incluir `WWW-Authenticate`.
  - **OWASP *Authentication Cheat Sheet*:** respuestas genéricas y tiempos uniformes evitan la enumeración de cuentas (RF-01-AC-2/3). Las tres ramas de `verificar()` ejecutan una verificación completa, incluso con contraseñas de más de 72 bytes (hallazgo H-10).
  - Los errores 500 registran el detalle en el log del servidor y devuelven un mensaje genérico. Los errores de validación devuelven campo y motivo, **nunca el valor recibido**, que podría ser una contraseña.

### D-11 · Cabeceras de seguridad y `Cache-Control: no-store`

- **Justificación:** **RFC 6749 §5.1** exige `Cache-Control: no-store` en respuestas con tokens. **OWASP *REST Security Cheat Sheet*** recomienda `Cache-Control: no-store`, `Content-Security-Policy: frame-ancestors 'none'`, `X-Content-Type-Options: nosniff` y `X-Frame-Options: DENY` en APIs, para que ningún proxy o navegador almacene datos de usuarios. Se aplican solo bajo `/api/v1`, para no romper la interfaz `/docs` en desarrollo. HSTS corresponde al proxy Nginx que termina TLS (ARQ-01).

### D-12 · `/docs` desactivado por defecto y `/salud` como única ruta anónima fuera de la API

- **Justificación:** **OWASP API9:2023 (*Improper Inventory Management*)** y **API8 (*Security Misconfiguration*)**: la documentación interactiva expone el inventario completo de la API. `API_DOCS` es falso por defecto (seguro por defecto) y `.env.example` lo activa solo para desarrollo. `/salud` vive fuera de `/api/v1`, no devuelve datos de negocio y sirve al *healthcheck* de Docker; no contradice RNF-01 porque no expone contenido.

### D-13 · Modularización del `main.py` monolítico

- **Decisión:** `main.py` (226 líneas con todo mezclado) se dividió en `config`, `db`, `errors`, `security`, `dependencies`, `schemas`, `serializacion` y `routers/{auth,usuarios,consultas}`. El SQL y la lógica de las rutas de S05 se conservaron.
- **Justificación:** **SWEBOK v4, KA *Software Construction*:** *minimizing complexity*, *anticipating change* y *constructing for verification*. El módulo de autenticación necesitaba compartir la conexión y los errores con las rutas existentes sin crear imports circulares, y la seguridad debe poder probarse de forma aislada (`tests/test_security.py`). Corresponde también a los "módulos lógicos internos" de `arquitectura_equipo.md` §5.

### D-14 · Pruebas de integración con base de datos real, de caja negra y de mutación

- **Justificación:** **SWEBOK v4, KA *Software Testing*:** niveles de prueba (unitarias en `test_security.py`, de integración en `test_auth.py` y `test_proteccion_rutas.py`) y técnicas basadas en fallas (*mutation testing*). Las pruebas corren contra PostgreSQL real (`ecoalert_test`) porque las reglas críticas (sesiones, `FOR UPDATE`, índices únicos en minúsculas) viven en SQL y un *mock* no las ejercitaría. La matriz de roles se prueba **por comportamiento**: cada ruta se invoca con cada rol y se compara contra los `x-roles` del contrato. La prueba de mutación expuso dos defectos de las propias pruebas (H-11 y H-12), lo que justifica la técnica.

---

## 2. Revisión del código generado (preguntas de la actividad)

| Pregunta | Respuesta | Evidencia |
|---|---|---|
| ¿El JWT tiene tiempo de expiración explícito? | **Sí.** `exp = iat + JWT_EXPIRATION` siempre se emite; `JWT_EXPIRATION` es obligatorio (1 a 86400 s) y `exp` es un claim requerido al validar. | `app/security.py:55`, `app/config.py:21`; `test_RF_01_AC_1_…`, `test_token_sin_claim_obligatorio_se_rechaza[exp]`, `test_configuracion_insegura_impide_arrancar` |
| ¿`/register` devuelve la contraseña? | **No.** Se devuelve una lista explícita de columnas (`USER_FIELDS`, sin `password_hash`); la contraseña solo existe como hash bcrypt. Campos extra como `password_hash` en el cuerpo se rechazan (422). | `app/routers/usuarios.py:15`; `test_register_devuelve_201_sin_password`, `test_register_rechaza_campos_extra_como_password_hash` |
| ¿El middleware rechaza tokens con firma inválida o expirados? | **Sí.** También rechaza `alg: none`, otro algoritmo, otro secreto, otro emisor o audiencia, tokens sin claims obligatorios o con `nbf` futuro, y sesiones cerradas o inactivas. | `app/security.py:61`, `app/dependencies.py:59`; `tests/test_security.py` (16 casos), `test_token_expirado_con_sesion_registrada_responde_401` |
| ¿El secreto está en código duro o en variable de entorno? | **Variable de entorno**, sin valor por defecto, ≥ 32 bytes y distinto del texto de plantilla. Tampoco quedan credenciales de base de datos en el código (H-04). | `app/config.py:18-37`, `.env.example`; `tests/test_config.py` |

---

## 3. Hallazgos y correcciones

**Origen:** *S05* = código del CRUD anterior; *Agente* = código generado en esta actividad y corregido durante la revisión.

| ID | Severidad | Origen | Hallazgo | Corrección | Verificación |
|---|---|---|---|---|---|
| H-01 | Alta | S05 | Ninguna ruta CRUD exigía autenticación (el README lo advertía). | Denegación por defecto en `/api/v1` y roles por ruta (D-07). | 36 pruebas parametrizadas sin token o con token inválido → 401 |
| H-02 | Alta | S05 | `password_temporal` aceptaba 8 caracteres; PS-15 y RNF-03 exigen 12. | `min_length=12`. | `test_RF_02_AC_3_…` |
| H-03 | Alta | Agente | `bcrypt` 5 lanza `ValueError` con contraseñas de más de 72 bytes, lo que producía un **error 500** provocable sin autenticación (en el login). | Validación de 72 bytes en contraseñas nuevas (422) y tratamiento como credencial inválida en el login (401). | `test_register_password_mayor_a_72_bytes_…`, `test_login_con_password_mayor_a_72_bytes_…` |
| H-04 | Media | S05 | `DATABASE_URL` tenía credenciales por defecto escritas en el código. | Variable obligatoria (`SecretStr`); sin ella, la API no arranca. | `test_variables_obligatorias_sin_valor_por_defecto[database_url]` |
| H-05 | Media | S05 | El README pedía copiar `.env.example`, pero el archivo no existía. | Se creó `.env.example` con `JWT_SECRET` y `JWT_EXPIRATION`; `.env` se añadió a `.gitignore`. | Inspección |
| H-06 | Media | S05 | Errores en `application/json` con `codigo: HTTP_404`; 401 sin `WWW-Authenticate`; validación con `DATOS_INVALIDOS` en vez de `VALIDACION`. | Problem Details RFC 9457 con los códigos del contrato (D-10). | `test_RF_01_AC_2_…`, `test_RNF_01_…_sin_token_…` |
| H-07 | Media | S05 | Desactivar una cuenta no cerraba sus sesiones, y no se impedía desactivar la última cuenta de Coordinación (RF-02-AC-8). | Revocación de sesiones y bloqueo transaccional con `FOR UPDATE`. | `test_desactivar_cuenta_invalida_sus_tokens_al_instante`, `test_RF_02_AC_8_…` |
| H-08 | Media | S05 | Las rutas no tenían el prefijo `/api/v1` que declara `servers` en el contrato. | Router con prefijo `/api/v1`. | Prueba de conformidad de roles (lee el contrato) |
| H-09 | Baja | S05 | Fechas serializadas con `str()` (`2026-10-24 10:00:00+00:00`), que no cumple RFC 3339 (`format: date-time`). | `isoformat()`. | `test_me_devuelve_el_usuario_del_token` |
| H-10 | Baja | Agente | Con una contraseña de más de 72 bytes, la rama del hash señuelo lanzaba `ValueError` al instante: un correo inexistente respondía más rápido (canal lateral de tiempo). | Todas las ramas de `verificar()` hacen una verificación completa. | Revisión de código |
| H-11 | Proceso | Agente | Las pruebas de denegación por defecto **pasaban sin verificar nada**: FastAPI 0.162 guarda los routers incluidos como `_IncludedRouter` y la enumeración de rutas devolvía una lista vacía. | Inventario desde `app.openapi()` (API pública) y la prueba `test_inventario_de_rutas_no_esta_vacio`. | Ya no hay pruebas omitidas (antes: 2 *skipped*) |
| H-12 | Proceso | Agente | La prueba de mutación "no exigir `exp`" **no se detectaba**: la verificación de la huella en `sesiones` rechazaba los tokens falsificados y ocultaba la validación del JWT. | Pruebas unitarias de `decodificar_token` aisladas de la sesión y una prueba de token expirado **con** sesión registrada. | La mutación ahora se detecta (sección 4.4) |
| H-13 | Proceso | Agente | El script de pruebas afirmaba que alterar el último carácter de la firma podía no invalidarla. Se verificó y es **falso** con PyJWT 2.15 (0 de 63 sustituciones aceptadas). | Se eliminó la afirmación. El caso 2 altera un carácter a mitad del token. | Verificación ejecutada |
| H-14 | Baja | S05 | `/docs` y `/openapi.json` quedaban siempre públicos. | `API_DOCS=false` por defecto (D-12). | Inspección |
| H-15 | Baja | S05 | `PATCH /usuarios/{id}` con cuerpo vacío respondía 400; el contrato especifica 422. | 422 `VALIDACION`. | Inspección |

**Nota sobre S05:** el `revision_sql.md` de S05 dejaba pendiente ejecutar `esquema_bd.sql`. En esta actividad se importó en PostgreSQL 17 + PostGIS 3.5 (`docker-compose.yml`) **sin errores**: se crearon 21 tablas en `ecoalert` y en `ecoalert_test`.

---

## 4. Protección de rutas

### 4.1 Rutas y nivel de acceso

Niveles: **Público** (sin token) · **Autenticado** (token válido, cualquier rol, permitido aun con contraseña temporal) · **Ambos roles** (Analista SIG o Coordinación, contraseña ya cambiada) · **Solo Coordinación**.

| Método | Ruta (`/api/v1`) | Nivel de acceso | `x-roles` del contrato |
|---|---|---|---|
| POST | `/auth/login` | Público | `publico` |
| POST | `/auth/register` | Solo Coordinación | `coordinacion` |
| GET | `/auth/me` | Autenticado | `analista_sig, coordinacion` |
| POST | `/auth/logout` | Autenticado | `analista_sig, coordinacion` |
| PUT | `/auth/password` | Autenticado | `analista_sig, coordinacion` |
| GET | `/usuarios` | Solo Coordinación | `coordinacion` |
| POST | `/usuarios` | Solo Coordinación | `coordinacion` |
| GET | `/usuarios/{usuarioId}` | Solo Coordinación | `coordinacion` |
| PATCH | `/usuarios/{usuarioId}` | Solo Coordinación | `coordinacion` |
| GET | `/alertas` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/cargas-alertas` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/cargas-alertas/{cargaId}` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/trabajos/{trabajoId}` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/zonas/{codigo}/marcas` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/zonas/{codigo}/marcas/{marcaId}` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/zonas/{codigo}/ajustes` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/zonas/{codigo}/ajustes/{ajusteId}` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/zonas/{codigo}/historial` | Ambos roles | `analista_sig, coordinacion` |
| GET | `/zonas/{codigo}/historial/{entradaId}` | Ambos roles | `analista_sig, coordinacion` |

Fuera de `/api/v1`: `GET /salud` es público para el *healthcheck* (D-12). Un `DELETE /usuarios/{id}` responde 405 y la cuenta sigue existiendo (RF-02-AC-7, `test_RF_02_AC_7_borrar_cuenta_no_existe`).

Las rutas del contrato que todavía no tienen implementación (ingesta, zonas, capas, análisis, exportación) quedarán protegidas automáticamente al montarse en `/api/v1` gracias a la denegación por defecto. Al implementarlas solo hay que declarar su `RequiereRol`; la prueba de conformidad indicará cualquier diferencia con el contrato.

### 4.2 Pruebas manuales desde la terminal (curl)

Script: `backend/scripts/pruebas_manuales.sh`. Salida completa, con los tokens ocultos: `evidencias/pruebas_manuales_curl.txt`. Ejecutado contra `uvicorn` y PostgreSQL en Docker el 24/10/2026.

| # | Caso exigido | Petición | Esperado | Obtenido | Cuerpo |
|---|---|---|---|---|---|
| 1 | Ruta protegida sin token | `GET /api/v1/usuarios` | 401 | **401** ✅ | `NO_AUTENTICADO`, con `WWW-Authenticate` |
| 2 | Token alterado en 1 carácter | `GET /api/v1/usuarios` + token modificado | 401 | **401** ✅ | `NO_AUTENTICADO` |
| 3 | Rol incorrecto | `GET /api/v1/usuarios` + token de Analista SIG | 403 | **403** ✅ | `ROL_NO_PERMITIDO` |
| 4 | Token válido y rol correcto | `GET /api/v1/usuarios?activo=true` + token de Coordinación | 200 | **200** ✅ | Lista de cuentas, sin `password_hash` |

Casos adicionales en la misma ejecución: registro por Coordinación → 201 sin contraseña · analista con contraseña temporal en `/alertas` → 403 `CAMBIO_PASSWORD_REQUERIDO` · cambio de contraseña → 204 · `/alertas` con Analista SIG → 200 · registro con token de Analista SIG → 403 · login con contraseña incorrecta → 401 genérico · logout → 204 · reutilizar el token después del logout → 401. El log del servidor no registró ningún 500.

### 4.3 Pruebas automatizadas

`cd backend && .venv/bin/python -m pytest` → **101 passed**.

| Archivo | Qué cubre | Casos |
|---|---|---|
| `tests/test_auth.py` | Login, registro, `/me`, logout, inactividad (29 y 31 min), contraseña temporal, cambio de contraseña, migración de hash | 30 |
| `tests/test_security.py` | Validación del JWT aislada: claims obligatorios, `exp`, `nbf`, `iss`, `aud`, secreto, algoritmo | 16 |
| `tests/test_proteccion_rutas.py` | 401 en las 18 rutas (sin token y con token inválido), matriz de roles contra el contrato, cabeceras, efectos inmediatos de desactivar o cambiar rol | 46 |
| `tests/test_config.py` | Arranque rechazado con secretos débiles o expiración inválida | 9 |

### 4.4 Prueba de mutación

Se inyectó cada regresión, se ejecutó la suite y se restauró el código; la integridad se verificó comparando sumas MD5.

| Regresión inyectada | ¿Detectada? | Prueba que falla |
|---|---|---|
| Quitar la denegación por defecto y el rol de las consultas | ✅ | `test_RF_02_AC_4_password_temporal_bloquea_…` |
| Abrir `GET /usuarios` a ambos roles | ✅ | `test_RNF_02_cada_ruta_aplica_los_x_roles_del_contrato` |
| No exigir el claim `exp` | ✅ (tras corregir H-12) | `test_token_sin_claim_obligatorio_se_rechaza[exp]` |
| Validar solo la firma, sin consultar la sesión | ✅ | `test_RF_01_AC_6_token_no_sirve_despues_de_logout` |

---

## 5. Riesgos residuales y trabajo pendiente

| Riesgo | Situación | Recomendación |
|---|---|---|
| Fuerza bruta contra el login | Sin límite de intentos; el contrato declara 429 y RF-25 (bloqueo tras 5 intentos) es *Should*. | `limit_req` en Nginx (ARQ-01) y, al abordar RF-25, contador de intentos por cuenta. OWASP ASVS V2.2.1. |
| Transporte | La API local corre en HTTP. | TLS 1.2+ en Nginx (RNF-03) y HSTS en el proxy. |
| Almacenamiento del token en la SPA | No aplica aún (no hay frontend). | Guardarlo en memoria, no en `localStorage` (exposición ante XSS). |
| Rotación del secreto | Un solo `JWT_SECRET`. | Cabecera `kid` y periodo de convivencia de dos claves al rotar. |
| Contraseñas multibyte | Límite de 72 bytes de bcrypt (D-06). | Si el equipo prioriza ASVS V2.1.2, volver a Argon2id como hash principal; el código ya verifica ambos. |
| `Idempotency-Key` | Exigida por el contrato en los POST de creación, no implementada desde S05. | Tabla de claves con la respuesta original y vigencia de 24 h. |
| Limpieza de sesiones | Las sesiones expiradas permanecen en la tabla. | Tarea periódica del *worker* (ARQ-02) que borre sesiones revocadas o inactivas. |
| Auditoría | No se registran los intentos fallidos de login. | Log estructurado sin datos sensibles (OWASP *Logging Cheat Sheet*). |

---

## 6. Cómo reproducir

```bash
cd backend
cp .env.example .env            # y reemplazar JWT_SECRET (comando en el propio archivo)
docker compose --env-file .env up -d
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt
.venv/bin/python -m pytest                        # 101 pruebas
.venv/bin/python -m app.cli crear-coordinacion --nombre "Coordinación Demo" --correo coordinacion@ecoalert.pe
.venv/bin/uvicorn app.main:app --reload
COORD_PASSWORD='…' ./scripts/pruebas_manuales.sh  # en otra terminal
```

---

## 7. Referencias

- IEEE Computer Society (2024). *SWEBOK Guide v4.0*. KA *Software Requirements*, *Software Construction*, *Software Testing*, *Software Configuration Management*, *Software Maintenance* y *Software Security*.
- Saltzer, J. H. y Schroeder, M. D. (1975). *The Protection of Information in Computer Systems*. Proceedings of the IEEE, 63(9).
- IETF RFC 7519 — *JSON Web Token (JWT)*.
- IETF RFC 7518 — *JSON Web Algorithms (JWA)*, §3.2.
- IETF RFC 8725 — *JSON Web Token Best Current Practices*, §3.1, §3.5, §3.8, §3.9, §3.10.
- IETF RFC 6749 — *The OAuth 2.0 Authorization Framework*, §5.1.
- IETF RFC 6750 — *Bearer Token Usage*, §3.
- IETF RFC 9110 — *HTTP Semantics*, §15.3.2, §15.5.2.
- IETF RFC 9457 — *Problem Details for HTTP APIs*.
- OWASP *Application Security Verification Standard* 4.0.3 — V2 Autenticación, V3 Gestión de sesiones, V4 Control de acceso.
- OWASP *API Security Top 10* (2023) — API3, API5, API8, API9.
- OWASP Cheat Sheets — *Password Storage*, *Authentication*, *Session Management*, *REST Security*, *Logging*.
- *The Twelve-Factor App* — III. Config.
- Documentación de FastAPI — *Security*, *OAuth2 with Password (and hashing), Bearer with JWT tokens*, *Dependencies*.
- Documentación de PyJWT 2 y pwdlib.
