> Salida original del agente (Parte 2), sin editar.

# Sprint Backlog — Sprint 1 · Descomposición en tareas técnicas

**Equipo 6 — TC5062, Gpo 10** · EcoAlert Tambopata · Propuesta del agente de apoyo al Sprint Planning
**Entradas:** `S03_A1/backlog_completo.md` (HU-E2-1, HU-E2-2, HU-E2-3), `S03_A1/SRS_equipo.md`
(RF-03, RF-04, RF-07; §2.3; RD-01, RD-04, RD-06, RD-10; RNF-06, RNF-10; PS-13, PS-14) y
`S03_A2/borradores/propuesta_agente_sprint_goal.md` (contexto; rige el alcance acordado por el equipo).

---

## 0. Alcance que se descompone

| Bloque | Estado | Criterios |
|---|---|---|
| Habilitación técnica (no es HU) | Comprometida | — |
| **HU-E2-1** — Carga de capas de referencia (RF-03) + interfaz mínima | Comprometida | RF-03-AC-1 a AC-11 · **diferido:** AC-12 (403) |
| **HU-E2-2** — Ingesta acumulativa de alertas GeoBosques (RF-04) + interfaz mínima | Comprometida | RF-04-AC-1 a AC-5 (AC-4 sin "sin salir de sus zonas") · **diferidos:** AC-6, AC-7 |
| **HU-E2-3** — Frescura de fuentes (RF-07) | **Extendida** (no comprometida) | Ver §4 |
| Cierre del sprint (manual, demo, backlog) | Comprometida | — |

**Convenciones de esta propuesta**

- **Roles** = funciones, no personas: *Backend dev*, *Frontend dev*, *QA*, *DevOps*, *SM/PO*. Una
  misma persona puede tomar tareas de varios roles (la sección 6 propone un reparto).
- **Revisión de PR:** el revisor siempre es una persona distinta del autor. Las horas de revisión
  se cuentan en tareas propias (T-E21-14/15, T-E22-10/11, T-E23-06) para que no queden ocultas.
- **Pruebas:** viven en `backend/tests/` y se nombran exactamente `test_RF_XX_AC_Y`. Ruff se
  configura para no marcar ese nombre (`N802` ignorado en `tests/`).
- **Errores:** toda respuesta de rechazo de la API devuelve `{"detalle": "<mensaje en español>",
  "campo": "<campo o null>"}` con estado 422 (RNF-06: mensajes en español).
- **Sin sesión:** cada endpoint de escritura declara `Depends(require_role("analista"))`. En el
  Sprint 1 la dependencia devuelve un analista ficticio; en el Sprint 2 se conecta a RF-01/RF-02 y
  se escriben `test_RF_03_AC_12` y `test_RF_04_AC_7`. La API no se expone fuera de local y CI
  (RNF-01).
- **IDs extra:** además de T-HAB, T-E21, T-E22 y T-E23, se usa **T-CIE-xx** para las tareas de
  cierre del sprint que no pertenecen a una HU.

---

## 1. Habilitación técnica (T-HAB)

| ID | Tarea | Rol | h | Depende de | Criterio de "done" (verificable) |
|---|---|---|---:|---|---|
| T-HAB-01 | Estructura del repo: `backend/`, `frontend/`, `docs/`, `.github/`; `.gitattributes` (LF), `.editorconfig`, `.gitignore`, `.env.example` (credenciales de BD de desarrollo, sin secretos reales) y README con el esqueleto de secciones | DevOps | 1.5 | — | PR fusionado; `git ls-files` muestra la estructura; `.env.example` documenta cada variable. |
| T-HAB-02 | `backend/Dockerfile` (python:3.12-slim, dependencias fijadas: FastAPI, SQLAlchemy 2, GeoAlchemy2, Alembic, pyogrio/GeoPandas, pyproj, Shapely, python-multipart) y `docker-compose.yml` con `db` (`postgis/postgis:17-3.5`, *healthcheck*, volumen persistente), `api` (espera a `db` sana) y `web` (Vite en modo desarrollo) | DevOps | 2.5 | T-HAB-01 | En una máquina limpia, `docker compose up --build` deja los tres servicios en estado *running/healthy*; `docker compose exec db psql -U ecoalert -c "SELECT postgis_version();"` responde. Probado en macOS y en Windows/WSL2 por dos integrantes distintos. |
| T-HAB-03 | Esqueleto FastAPI: `app/main.py`, configuración con pydantic-settings, motor y sesión de SQLAlchemy 2, ruta `GET /api/salud` que consulta la BD | Backend dev | 2 | T-HAB-02 | `curl localhost:8000/api/salud` → `{"estado":"ok","bd":"ok"}`; `/docs` muestra la ruta. |
| T-HAB-04 | Alembic configurado con GeoAlchemy2 (sin detectar tablas internas de PostGIS); migración `0001` con `CREATE EXTENSION IF NOT EXISTS postgis`; `conftest.py` de pytest con BD de prueba (esquema creado con `alembic upgrade head` y limpieza por prueba) | Backend dev | 2 | T-HAB-03 | `docker compose exec api alembic upgrade head` sobre BD vacía termina sin error; `alembic downgrade base` también; `pytest` ejecuta una prueba de humo contra PostGIS y pasa. |
| T-HAB-05 | Dependencia `require_role(rol)` (stub que devuelve un analista ficticio, con `TODO Sprint 2`) y manejador global de errores que traduce `RequestValidationError` y las excepciones de dominio al formato `{"detalle","campo"}` en español | Backend dev | 1 | T-HAB-03 | Prueba unitaria: un campo de formulario faltante devuelve 422 con `detalle` en español y `campo` con su nombre; `grep require_role` muestra la dependencia en la plantilla de router. |
| T-HAB-06 | Esqueleto React 19 + TypeScript + Vite; ESLint (reglas recomendadas TS + React Hooks); Vitest + Testing Library; proxy de Vite `/api → api:8000`; cliente `apiClient.ts` que interpreta `{"detalle","campo"}`; diseño base en español (`lang="es"`) | Frontend dev | 2 | T-HAB-01 | `npm run lint` y `npm run test` pasan; en `localhost:5173` se ve la página "EcoAlert Tambopata" con el estado de `/api/salud`. |
| T-HAB-07 | Workflow `.github/workflows/ci.yml` en *push* y *pull request*: job **backend** (Ruff `check` + `format --check`, `alembic upgrade head`, pytest contra servicio `postgis/postgis:17-3.5`) y job **frontend** (`npm ci`, ESLint, Vitest). Sin despliegue | DevOps | 2.5 | T-HAB-04, T-HAB-06 | Un PR de prueba muestra los dos jobs en verde; un PR con un error de Ruff introducido a propósito queda en rojo. |
| T-HAB-08 | Proceso: tablero del sprint con estas tareas, plantilla de PR con la checklist de la DoD (IDs `RF-XX-AC-Y` cubiertos, pruebas, captura si hay UI), protección de `main` (CI verde + 1 aprobación) | SM/PO | 1 | T-HAB-01 | Intentar fusionar un PR sin aprobación está bloqueado; el tablero lista todas las tareas T-xxx con responsable. |
| | **Subtotal habilitación** | | **14.5** | | |

---

## 2. HU-E2-1 — Carga de capas de referencia (comprometida)

**Diseño acordado para la descomposición** (para que las tareas encajen entre sí):

- Tablas: `capa_version` (id, tipo_capa ∈ {limite_reserva, zona_amortiguamiento, rios,
  catastro_minero}, fuente, fecha_corte, fecha_carga, nombre_archivo) y `elemento_capa`
  (version_id, geom `Geometry(srid=32719)`, codigo, nombre, tipo_derecho, estado). **No existe
  ninguna columna para el titular** (RD-04); los datos de origen no se alteran más allá de la
  reproyección (RD-06).
- Versión vigente de un tipo = la de **mayor fecha de corte** (no la última cargada). Esta función
  (`version_vigente(tipo)`) es "lo que usan los cálculos" en RF-03-AC-10/11; la primera que la
  consume es la ingesta de alertas (ámbito, HU-E2-2).
- Flujo de la interfaz: el analista elige el archivo → la API lo **inspecciona** y devuelve sus
  columnas → el analista asigna columnas a los atributos del tipo de capa → envía.

| ID | Tarea | Rol | h | Depende de | Criterio de "done" | Cubre |
|---|---|---|---:|---|---|---|
| T-E21-01 | *Spike* de datos reales (compartido con HU-E2-2): obtener el límite oficial de la RN Tambopata y su ZA (SERNANP), el catastro minero de Madre de Dios (INGEMMET) y un archivo de alertas de GeoBosques; documentar formato, SRC, tipo de geometría, columnas, tamaño y codificación en `docs/datos_fuente.md`. Los archivos reales **no** se versionan si pesan más de 5 MB | QA | 1.5 | — | `docs/datos_fuente.md` fusionado con una ficha por fuente; dudas abiertas (p. ej., formato de fecha de detección) anotadas para el PO. | — (insumo) |
| T-E21-02 | Datos de prueba sintéticos generados por script (`backend/tests/fixtures/generar.py`, reproducible): catastro `.zip` con `.prj` EPSG:4326 y columna `TITULAR`; `.zip` sin `.prj`; GeoJSON EPSG:4326 con un punto de control de coordenadas conocidas; archivo `.kml`; capa de ríos con polígonos; catastro sin columna de código; límite de reserva y ZA sintéticos en la zona de Tambopata | QA | 2 | T-HAB-04 | `python generar.py` produce los archivos en `tests/fixtures/`; un README breve indica qué criterio usa cada archivo. | Insumo de AC-1 a AC-11 |
| T-E21-03 | **Contrato de la API de capas** (temprano, para desbloquear el frontend): esquemas Pydantic y rutas con respuesta 501 — `GET /api/capas/tipos` (tipos con geometría y atributos de destino), `POST /api/capas/inspeccion` (devuelve columnas y tipo de geometría), `POST /api/capas/{tipo}/versiones` (multipart: archivo, fuente, fecha_corte, asignación de columnas), `GET /api/capas/{tipo}/versiones` | Backend dev | 1 | T-HAB-05 | `/docs` muestra las 4 rutas con sus esquemas y ejemplos; el frontend puede generar un *mock* a partir de ellos. Todas declaran `require_role("analista")` salvo `GET /tipos`. | Base de AC-9 (atributos de destino) |
| T-E21-04 | Modelo SQLAlchemy/GeoAlchemy2 y migración `0002` de `capa_version` y `elemento_capa` (índice GiST en `geom`; restricciones NOT NULL en fuente y fecha_corte) | Backend dev | 2 | T-HAB-04 | `alembic upgrade head` crea ambas tablas; `\d elemento_capa` muestra `geometry(Geometry,32719)` y **ninguna** columna de titular. | AC-1, AC-9 (estructura) |
| T-E21-05 | Módulo común `app/ingesta/lector.py` (reutilizado por HU-E2-2): acepta solo `.zip` con `.shp`/`.shx`/`.dbf`/`.prj` o `.geojson`; rechaza otros formatos con "Formatos aceptados: Shapefile comprimido (.zip) o GeoJSON"; rechaza `.zip` sin `.prj` con "El archivo no declara su sistema de coordenadas"; lee a GeoDataFrame con pyogrio. Incluye la función de inspección de columnas | Backend dev | 2.5 | T-HAB-04, T-E21-02 | Pruebas unitarias del módulo pasan con los archivos `.kml`, `.zip` sin `.prj` y válidos de T-E21-02. | AC-5, AC-6; base de AC-1 |
| T-E21-06 | Validación y transformación por tipo de capa: tipo de geometría (polígono/multipolígono o línea), atributos obligatorios asignados, lista blanca de atributos de destino (las columnas no asignadas se descartan, incluido `TITULAR`), reproyección a EPSG:32719 con pyproj (`always_xy`) | Backend dev | 2.5 | T-E21-05 | Pruebas unitarias: ríos con polígonos → "La capa de ríos exige geometrías de tipo línea"; catastro sin código → "Falta asignar el atributo obligatorio: código"; el GeoDataFrame resultante no contiene `TITULAR` y su CRS es EPSG:32719. | AC-1, AC-2, AC-7, AC-8, AC-9 |
| T-E21-07 | Servicio de versiones: crear versión + elementos en **una sola transacción** (si algo falla no queda versión); validar fuente y fecha de corte antes de leer el archivo; `version_vigente(tipo)` por mayor fecha de corte (empate: la última cargada, pendiente de confirmar con el PO); historial ordenado por fecha de corte | Backend dev | 2 | T-E21-04, T-E21-06 | Pruebas unitarias del servicio: tras un rechazo, `SELECT count(*) FROM capa_version` no cambia; con cortes 01/07 y 15/09 cargados en cualquier orden, la vigente es la del 15/09. | AC-3, AC-4, AC-10, AC-11 |
| T-E21-08 | Implementación de las 4 rutas del contrato (T-E21-03) sobre el lector y el servicio; la respuesta de carga devuelve id, tipo, fuente, fecha de corte, número de elementos y atributos almacenados | Backend dev | 2 | T-E21-03, T-E21-07 | Desde `/docs` se carga el catastro de prueba y se obtiene 201; las rutas ya no responden 501; ninguna respuesta incluye el valor de `TITULAR`. | AC-1 a AC-11 (vía API) |
| T-E21-09 | Pruebas de aceptación de API `test_RF_03_AC_1` … `test_RF_03_AC_6` (AC-2: distancia entre el punto almacenado y su transformación con pyproj ≤ 1 m, medida con `ST_Distance` en 32719) | QA | 2 | T-E21-02, T-E21-08 | Las 6 pruebas pasan en local y en CI; cada una sigue el Dado/cuando/entonces del SRS en su docstring. | AC-1 a AC-6 |
| T-E21-10 | Pruebas `test_RF_03_AC_7` … `test_RF_03_AC_11` (AC-9: consulta a `information_schema.columns` + búsqueda del valor del titular en la tabla y en el JSON de respuesta + verificación de que `GET /api/capas/tipos` no ofrece atributo de titular; AC-10/11: historial con ambas versiones y `version_vigente` = 15/09/2026) | QA | 2 | T-E21-02, T-E21-08 | Las 5 pruebas pasan en local y en CI. | AC-7 a AC-11 |
| T-E21-11 | Pantalla "Cargar datos" (modo *capa de referencia*): selector de tipo de capa (desde `GET /tipos`), archivo, fuente, fecha de corte; al elegir el archivo llama a la inspección y muestra un selector por atributo de destino con las columnas del archivo. Funciona contra un *mock* si la API aún no está lista | Frontend dev | 4 | T-HAB-06, T-E21-03 | En el navegador se completa el formulario con el catastro de prueba; el botón "Cargar" se habilita solo con archivo, fuente, fecha y atributos obligatorios asignados; no aparece ninguna opción de titular. | AC-3, AC-4, AC-8, AC-9 (en interfaz) |
| T-E21-12 | Mensajes de la pantalla: errores de la API mostrados junto al campo indicado en `campo` (o arriba del formulario); confirmación "Capa cargada: <tipo>, corte dd/mm/aaaa, N elementos"; estado "Procesando…" mientras dura la carga (RNF-04). Pruebas Vitest del formulario (campos obligatorios, error mostrado, confirmación) | Frontend dev | 2 | T-E21-11 | `npm run test` pasa con ≥ 3 pruebas de la pantalla; con la API real, cargar el `.kml` muestra el mensaje de formatos aceptados en español. | AC-3 a AC-8 (en interfaz) |
| T-E21-13 | Integración frontend ↔ API y prueba manual guiada (RNF-06) con los datos reales del *spike*: cargar límite de la reserva, ZA, ríos y catastro desde la interfaz, sin `/docs` ni comandos; verificar en QGIS conectado a PostGIS que las geometrías están en EPSG:32719 y bien ubicadas | QA | 1.5 | T-E21-08, T-E21-12, T-E21-01 | Checklist en `docs/pruebas_manuales/sprint1_capas.md` con resultado y capturas; defectos registrados en el tablero. | AC-1, AC-9 (verificación extremo a extremo) |
| T-E21-14 | Revisión de los PR de backend y pruebas de HU-E2-1 (revisor ≠ autor): DoD, nombres `test_RF_03_AC_Y`, ausencia de titular, mensajes en español | Backend dev | 1 | T-E21-08 a T-E21-10 | PR aprobados con comentarios resueltos y CI en verde. | — |
| T-E21-15 | Revisión de los PR de frontend de HU-E2-1 (revisor ≠ autor) | Frontend dev | 0.5 | T-E21-12 | PR aprobados con comentarios resueltos y CI en verde. | — |
| | **Subtotal HU-E2-1** | | **28.5** | | | |

**Diferido:** RF-03-AC-12 (403 a la coordinación) → Sprint 2, con HU-E1-1.

---

## 3. HU-E2-2 — Ingesta acumulativa de alertas GeoBosques (comprometida)

**Diseño acordado para la descomposición:**

- Tablas: `carga_alertas` (id, fuente, fecha_corte, fecha_ingesta, nombre_archivo, conteos del
  resumen) y `alerta` (id, fuente, codigo, geom `Geometry(srid=32719)`, fecha_deteccion,
  fecha_ingesta, carga_origen_id, `no_presente_ultima_carga` booleano), con **restricción única
  (fuente, codigo)**.
- **Ámbito** = unión de las versiones vigentes de `limite_reserva` y `zona_amortiguamiento`
  (RD-01, el límite es dato). Una alerta se descarta solo si **no interseca** el ámbito
  (completamente fuera); si toca el ámbito, se ingiere.
- El final de la ingesta llama a un punto de extensión vacío `agrupar_en_zonas(carga_id)` que
  HU-E3-1 implementará (RF-04-AC-6, Sprint 2).

| ID | Tarea | Rol | h | Depende de | Criterio de "done" | Cubre |
|---|---|---|---:|---|---|---|
| T-E22-01 | Datos de prueba de alertas (extiende el script de T-E21-02): archivo de 120 polígonos con 5 completamente fuera del ámbito sintético; base de 200 alertas y archivo nuevo con 150 de ellas + 30 nuevas; archivo con puntos; archivo con 3 alertas nuevas y fecha de corte anterior; columnas con los nombres reales documentados en el *spike* | QA | 1.5 | T-E21-01, T-E21-02 | `python generar.py` produce los archivos; conteos verificados con una prueba que solo cuenta registros. | Insumo de AC-1 a AC-5 |
| T-E22-02 | Modelo y migración `0003` de `carga_alertas` y `alerta` (índice GiST, restricción única fuente+código) | Backend dev | 1.5 | T-E21-04 | `alembic upgrade head` crea las tablas; insertar dos veces (GeoBosques, mismo código) falla por la restricción. | AC-1 (estructura), AC-4 |
| T-E22-03 | Validación específica y descarte por ámbito: reutiliza `lector.py` (formato, SRC, reproyección); exige polígonos ("Las alertas deben ser polígonos"); exige asignar "código" y "fecha de detección"; calcula el ámbito con `version_vigente` y descarta lo que no lo interseca; si no hay límite de reserva o ZA cargados, rechaza con "Cargue primero el límite de la reserva y la zona de amortiguamiento" | Backend dev | 1.5 | T-E22-02, T-E21-07 | Pruebas unitarias: con el archivo de 120 quedan 115 candidatas y 5 descartadas; archivo de puntos rechazado con el mensaje esperado. | AC-1, AC-2, AC-3 |
| T-E22-04 | Lógica acumulativa en una transacción: inserta nuevas, reconoce existentes por (fuente, código) sin modificarlas (RD-06), marca `no_presente_ultima_carga` en las ingeridas que no vienen (y la limpia en las que vuelven), registra fecha de ingesta y la carga; no rechaza cargas con fecha de corte anterior; arma el resumen {nuevas, existentes, fuera_del_ambito, no_presentes, total}; llama al gancho vacío de agrupación | Backend dev | 2.5 | T-E22-03 | Prueba unitaria del servicio con el escenario 200 → 150 + 30: total 230, 30 nuevas, 150 existentes, 50 no presentes, ninguna borrada. | AC-1, AC-4, AC-5 |
| T-E22-05 | Endpoint `POST /api/alertas/cargas` (multipart: archivo, fecha_corte, asignación de columnas; fuente fija "GeoBosques") con `require_role("analista")`, y `GET /api/alertas/cargas/{id}`; la respuesta incluye el resumen con el texto "N alertas fuera del ámbito". Procesamiento síncrono, medido con el archivo real (RNF-04, ≤ 60 s) | Backend dev | 2 | T-E22-04, T-E21-03 | Desde `/docs` se ingiere el archivo de 120 y la respuesta trae `fuera_del_ambito: 5` y el texto "5 alertas fuera del ámbito"; tiempo con el archivo real anotado en el PR. | AC-1 a AC-5 (vía API) |
| T-E22-06 | Pruebas `test_RF_04_AC_1` … `test_RF_04_AC_5` (AC-1 verifica fuente "GeoBosques", código, fecha de detección y fecha de ingesta en las 115; AC-4 **sin** la cláusula "sin salir de sus zonas", anotada como `# Sprint 2: RF-05`) | QA | 2.5 | T-E22-01, T-E22-05 | Las 5 pruebas pasan en local y en CI. | AC-1 a AC-5 |
| T-E22-07 | Pantalla "Cargar datos" (modo *alertas GeoBosques*): reutiliza el formulario de T-E21-11 con fuente fija y solo lectura, asignación de "código" y "fecha de detección", fecha de corte | Frontend dev | 1.5 | T-E21-11, T-E22-05 | En el navegador se carga el archivo de 120 alertas desde la interfaz; el archivo de puntos muestra "Las alertas deben ser polígonos". | AC-3 (en interfaz) |
| T-E22-08 | Resumen de la ingesta en pantalla: nuevas / ya existentes / fuera del ámbito / no presentes en la última carga / total; prueba Vitest del componente de resumen | Frontend dev | 1.5 | T-E22-07 | Tras la segunda carga del escenario 200 → 150 + 30 se ve "30 nuevas · 150 ya existentes · 50 no presentes en la última carga"; `npm run test` pasa. | AC-2, AC-4 (en interfaz) |
| T-E22-09 | Integración y prueba manual guiada con el archivo real de GeoBosques: cargarlo dos veces (la segunda con una copia modificada) y revisar el resumen; comprobar en QGIS que las descartadas están fuera del ámbito | QA | 1 | T-E22-08, T-E21-13 | Checklist en `docs/pruebas_manuales/sprint1_alertas.md` con resultado y capturas. | AC-1, AC-2, AC-4 (extremo a extremo) |
| T-E22-10 | Revisión de los PR de backend y pruebas de HU-E2-2 (revisor ≠ autor) | Backend dev | 0.5 | T-E22-06 | PR aprobados y CI en verde. | — |
| T-E22-11 | Revisión de los PR de frontend de HU-E2-2 (revisor ≠ autor) | Frontend dev | 0.5 | T-E22-08 | PR aprobados y CI en verde. | — |
| | **Subtotal HU-E2-2** | | **16.5** | | | |

**Diferidos:** RF-04-AC-6 (cada alerta en una zona, HU-E3-1) y RF-04-AC-7 (403, HU-E1-1) →
Sprint 2. La cláusula "sin salir de sus zonas" de AC-4 se agrega a `test_RF_04_AC_4` en el
Sprint 2.

---

## 4. HU-E2-3 — Frescura de fuentes visible (**extendida**, no comprometida)

Solo se toma si HU-E2-1 y HU-E2-2 cumplen la DoD (punto de control del día 8). Como el mapa
(RF-06, HU-E3-2) y la lista de zonas (RF-10) aún no existen, el "panel de capas" se materializa
como una sección **"Estado de las fuentes"** en la pantalla "Cargar datos", y los criterios que
mencionan la lista de zonas quedan parciales.

| ID | Tarea | Rol | h | Depende de | Criterio de "done" | Cubre |
|---|---|---|---:|---|---|---|
| T-E23-01 | Servicio de frescura: fecha de corte vigente por tipo de capa (`version_vigente`), fecha de corte más reciente de las cargas de alertas, `posiblemente_desactualizada` si han pasado **más de 30 días** (PS-13) respecto de la fecha actual en hora de Lima; reloj inyectable para las pruebas | Backend dev | 2 | T-E21-07, T-E22-04 | Pruebas unitarias con el reloj fijado en 04/10/2026: 14 días → sin aviso; 30 días exactos → sin aviso; 45 días → aviso. | AC-1, AC-3, AC-4, AC-5 (lógica) |
| T-E23-02 | Endpoint `GET /api/fuentes/frescura` (lectura, ambos roles) con fechas dd/mm/aaaa, "Sin datos cargados" y el texto del aviso | Backend dev | 1 | T-E23-01 | `/docs` devuelve una entrada por fuente (4 capas + "Alertas de GeoBosques"). | AC-1, AC-3, AC-4, AC-5 (vía API) |
| T-E23-03 | Pruebas `test_RF_07_AC_1`, `test_RF_07_AC_3` (parte del panel), `test_RF_07_AC_4`, `test_RF_07_AC_5` | QA | 1.5 | T-E23-02 | Las 4 pruebas pasan en CI. `test_RF_07_AC_2` y la parte de la lista de AC-3 se marcan pendientes (`# Sprint con RF-10`). | AC-1, AC-3 (parcial), AC-4, AC-5 |
| T-E23-04 | Sección "Estado de las fuentes" en la interfaz: tabla fuente → fecha de corte / "Sin datos cargados", aviso destacado "Alertas de GeoBosques posiblemente desactualizadas (corte dd/mm/aaaa)"; se refresca tras cada carga; prueba Vitest | Frontend dev | 2.5 | T-E23-02, T-E22-08 | En pantalla, tras cargar el catastro con corte 15/09/2026, la fila muestra "15/09/2026"; "Ríos" sin cargar muestra "Sin datos cargados". | AC-1, AC-3, AC-4, AC-5 (en interfaz) |
| T-E23-05 | Prueba manual de la sección con datos reales y fecha de corte antigua | QA | 0.5 | T-E23-04 | Resultado anotado en `docs/pruebas_manuales/sprint1_alertas.md`. | AC-3, AC-5 |
| T-E23-06 | Revisión de PR de HU-E2-3 | Backend dev | 0.5 | T-E23-03, T-E23-04 | PR aprobados y CI en verde. | — |
| | **Subtotal HU-E2-3 (extendida)** | | **8** | | | |

**Parcial/pendiente:** RF-07-AC-2 y la parte "lista de zonas" de RF-07-AC-3 dependen de RF-10.

---

## 5. Cierre del sprint (T-CIE)

| ID | Tarea | Rol | h | Depende de | Criterio de "done" |
|---|---|---|---:|---|---|
| T-CIE-01 | Manual de arranque y uso en español (RNF-10, parcial): README con requisitos, `docker compose up`, migraciones, cómo correr pruebas; `docs/manual_carga.md` con capturas de la carga de capas y de la ingesta de alertas y la tabla de mensajes de error | DevOps | 1.5 | T-E21-13, T-E22-09 | Un integrante que no escribió el manual levanta el sistema desde cero y carga una capa siguiendo solo el documento (se anota quién y cuánto tardó). |
| T-CIE-02 | Preparación de la demo de la Sprint Review: guion (cargar límite + ZA + catastro desde la interfaz, ingerir GeoBosques dos veces, mostrar resumen, mostrar un rechazo en español, abrir PostGIS en QGIS, CI en verde), datos listos, ensayo de 15 min | SM/PO | 1.5 | T-E21-13, T-E22-09 | Guion en `docs/demo_sprint1.md`; ensayo realizado una vez en una máquina distinta a la del autor. |
| T-CIE-03 | Actualizar el Product Backlog (criterios diferidos con sprint previsto, preguntas abiertas al PO) y registrar horas reales por tarea para calibrar el Sprint 2 | SM/PO | 0.5 | — | El tablero muestra horas reales en todas las tareas cerradas; RF-03-AC-12, RF-04-AC-6, RF-04-AC-7 anotados en el Sprint 2. |
| | **Subtotal cierre** | | **3.5** | | |

---

## 6. Totales y comparación con la capacidad

### 6.1 Horas por bloque

| Bloque | Tareas | Horas |
|---|---:|---:|
| Habilitación técnica | 8 | 14.5 |
| HU-E2-1 (comprometida) | 15 | 28.5 |
| HU-E2-2 (comprometida) | 11 | 16.5 |
| Cierre del sprint | 3 | 3.5 |
| **Total comprometido** | **37** | **63.0** |
| HU-E2-3 (extendida) | 6 | 8.0 |
| **Total con meta extendida** | **43** | **71.0** |

### 6.2 Horas por rol

| Rol | Habilitación | HU-E2-1 | HU-E2-2 | Cierre | **Comprometido** | HU-E2-3 (ext.) |
|---|---:|---:|---:|---:|---:|---:|
| Backend dev | 5 | 13 | 8 | — | **26** | 3.5 |
| Frontend dev | 2 | 6.5 | 3.5 | — | **12** | 2.5 |
| QA | — | 9 | 5 | — | **14** | 2 |
| DevOps | 6.5 | — | — | 1.5 | **8** | — |
| SM/PO | 1 | — | — | 2 | **3** | — |
| **Total** | **14.5** | **28.5** | **16.5** | **3.5** | **63** | **8** |

### 6.3 Comparación con la capacidad

| Concepto | Horas |
|---|---:|
| Capacidad neta del sprint (64 h brutas − 16 h de eventos Scrum) | 48 |
| Trabajo comprometido según esta descomposición | 63 |
| **Diferencia** | **−15 h (31 % por encima)** |
| Capacidad neta si todos dan 9 h/semana (72 − 16) | 56 → aún **−7 h**, sin margen |

**Conclusión: con la interfaz mínima añadida, el alcance acordado no cabe en las 48 h netas.**
La planeación anterior (≈ 39.5 h) no incluía interfaz, revisión de PR, pruebas manuales, manual ni
demo; esas tareas suman ≈ 19 h en esta descomposición (interfaz 11 h, revisiones 2.5 h, pruebas
manuales 2.5 h, manual y demo 3 h), y el resto de la diferencia viene de estimaciones algo mayores
en habilitación (14.5 h frente a 12 h) y en backend. Equivale a ≈ 2.8 h por SP en las dos historias, frente al
supuesto inicial de 1.8–2 h/SP.

Además hay un **cuello de botella de rol**: 26 h de backend en una ruta crítica casi secuencial
(T-HAB-02 → 03 → 04 → T-E21-04 → 05 → 06 → 07 → 08 → T-E22-03 → 04 → 05 ≈ 23.5 h). Con ≈ 12 h
netas por persona, el backend necesita a **dos** personas y que el contrato (T-E21-03) se fusione
el día 3 para que el frontend avance en paralelo con *mocks*.

### 6.4 Opciones para el equipo (decisión del PO y del equipo)

| Opción | Qué cambia | Horas comprometidas | Holgura con 48 h | Efecto en el Sprint Goal |
|---|---|---:|---:|---|
| **A (recomendada)** | Comprometer habilitación + HU-E2-1 completa con interfaz + cierre. HU-E2-2 pasa a **meta extendida 1** (empieza por backend y pruebas, T-E22-01 a T-E22-06) y HU-E2-3 a meta extendida 2. | 46.5 | +1.5 h | Se reescribe: "el analista carga desde la interfaz las capas de referencia del ámbito…". Si la ingesta se termina, se demuestra como extra. |
| B | Mantener ambas HU, diferir al Sprint 2 su interfaz de alertas (T-E22-07, 08, 09, 11: −4.5 h) y comprometer 9 h/semana | 58.5 vs 56 | −2.5 h | Se mantiene, pero la ingesta se demuestra por `/docs`, en contra del ajuste del equipo (RNF-06). |
| C | Mantener todo y asumir el riesgo | 63 vs 48–56 | −7 a −15 h | Alta probabilidad de terminar con dos historias a medias y ninguna "Done", sin velocidad medible. |

Recomiendo **A** porque deja una historia de punta a punta (API + interfaz + pruebas + manual),
respeta el ajuste de interfaz del equipo, sigue la cadena de dependencias (HU-E2-1 es
prerrequisito de HU-E2-2) y mide una velocidad real para el Sprint 2. Las tareas de HU-E2-2 ya
están descompuestas y listas para tomarse en cuanto HU-E2-1 cumpla la DoD.

### 6.5 Reparto sugerido por persona (opción A, ≈ 12 h cada una)

| Integrante | Rol principal | Tareas comprometidas | h |
|---|---|---|---:|
| 1 | DevOps + SM | T-HAB-01, 02, 07, 08, T-CIE-01, 02, 03, T-E21-14 | 12 |
| 2 | Backend | T-HAB-03, 04, 05, T-E21-03, 04, 05, 07 | 12.5 |
| 3 | Backend + QA | T-E21-06, 08, 09, 10, 13, 15 | 10.5 |
| 4 | Frontend + QA | T-HAB-06, T-E21-01, 02, 11, 12 | 11.5 |

El integrante 4 hace el *spike* y los datos de prueba (T-E21-01/02) en los días 1–2, mientras
el backend termina la habilitación. Cada revisión la hace alguien distinto del autor (T-E21-14:
integrante 1; T-E21-15: integrante 3). En la opción A, T-CIE-01 y T-CIE-02 dependen solo de
T-E21-13. Las holguras (≈ 1.5 h en total) y quien termine antes empiezan HU-E2-2 por T-E22-01 a
T-E22-04.

---

## 7. Preguntas abiertas para el PO (detectadas al descomponer)

1. **Ingesta sin ámbito cargado:** el SRS no dice qué pasa si se ingieren alertas antes de cargar
   el límite de la reserva y la ZA. Propuesta: rechazar la carga con un mensaje (T-E22-03).
2. **Empate de fecha de corte** entre dos versiones de la misma capa: ¿cuál es la vigente?
   Propuesta: la última cargada (T-E21-07).
3. **Carga con fecha de corte anterior** (RF-04-AC-5): ¿debe marcar como "no presente en la
   última carga" las alertas más recientes que no trae? Leída literalmente, sí; puede confundir
   al analista. Propuesta: marcar solo cuando la carga es la de fecha de corte más reciente.
4. **Misma alerta (fuente, código) con geometría distinta** en una carga posterior: se conserva
   la original (RD-06) y se cuenta como existente; ¿se debe avisar?
5. **Fecha de detección con formato inválido o vacía** en algunas filas: ¿se rechaza todo el
   archivo o solo esas filas (y se informan en el resumen)?
6. **Tamaño máximo de archivo** de carga: no está en el SRS; el *spike* (T-E21-01) medirá el
   tamaño real de GeoBosques y del catastro para proponerlo junto con PS-14.
