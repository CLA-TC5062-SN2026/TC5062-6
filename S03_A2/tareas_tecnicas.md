# Tareas técnicas del Sprint 1 — EcoAlert Tambopata

> Equipo 6 — TC5062, Gpo 10 · S03-A2, Parte 2 · 04/10/2026
> Descomposición propuesta por el agente (`borradores/propuesta_agente_tareas.md`), revisada y
> ajustada por el equipo. Los cambios y sus motivos están en la sección 9. Alcance, Sprint Goal y
> capacidad: `sprint1_planning.md`. Criterio general de terminado: `definition_of_done.md`.

---

## 1. Convenciones

- **Tamaño:** ninguna tarea supera **4 h**. Las horas son de trabajo efectivo.
- **Responsable:** cada tarea indica el **rol** (Backend dev, Frontend dev, QA, DevOps, SM, PO) y
  el **integrante** propuesto. El equipo puede reasignar en la Daily sin replanificar.

  | Integrante | Roles en el Sprint 1 |
  |---|---|
  | **Miguel** Arévalo (A01840503) | Backend dev (núcleo geoespacial: lectura, validación, versiones, ingesta) |
  | **Daniel** Medina (A01658850) | Scrum Master · DevOps · Backend dev (modelos y endpoints) |
  | **Anthony** Gutarra (A01840622) | Frontend dev · QA manual · manual de usuario |
  | **Eduardo** Sauza (A01797466) | Product Owner · QA (datos y pruebas automatizadas) |

- **IDs:** `T-HAB-xx` (habilitación técnica), `T-E21-xx` (HU-E2-1), `T-E22-xx` (HU-E2-2),
  `T-E23-xx` (HU-E2-3, extendida), `T-CIE-xx` (cierre del sprint), `T-PO-xx` (decisiones del PO).
- **Pruebas:** en `backend/tests/`, con el nombre exacto `test_RF_XX_AC_Y` (Ruff ignora `N802` en
  `tests/` para permitir el nombre).
- **Errores de la API:** todo rechazo responde 422 con `{"detalle": "<mensaje en español>",
  "campo": "<campo o null>"}`.
- **Sin sesión en el Sprint 1:** cada endpoint de escritura declara
  `Depends(require_role("analista"))`, que por ahora devuelve un analista ficticio. En el
  Sprint 2 se conecta al inicio de sesión (HU-E1-1) y se escriben `test_RF_03_AC_12` y
  `test_RF_04_AC_7`. Mientras tanto, la API solo corre en local y en CI.
- **Tablero:** cada tarea es un **sub-issue** de su historia en GitHub Projects: HU-E2-1 → #4,
  HU-E2-2 → #5, HU-E2-3 → #6. Las tareas T-HAB, T-CIE y T-PO cuelgan del issue #16,
  "Sprint 1 — Habilitación técnica y cierre". Los sub-issues son #17–#61, con las etiquetas `tarea` y
  `sprint: 1` (y `meta extendida` las de HU-E2-3).

---

## 2. Habilitación técnica (T-HAB)

No es una historia de usuario y no suma Story Points, pero las historias no se pueden terminar
sin ella.

| ID | Tarea | Responsable | h | Depende de | Criterio de "done" |
|---|---|---|---:|---|---|
| T-HAB-01 | Estructura del repo: `backend/`, `frontend/`, `docs/`, `.github/`; `.gitattributes` (LF), `.editorconfig`, `.gitignore`, `.env.example` y esqueleto del README | DevOps · Daniel | 1.5 | — | PR fusionado; `.env.example` documenta cada variable sin valores reales. |
| T-HAB-02 | `backend/Dockerfile` (python:3.12-slim con dependencias fijadas: FastAPI, SQLAlchemy 2, GeoAlchemy2, Alembic, pyogrio/GeoPandas, pyproj, Shapely) y `docker-compose.yml` con `db` (`postgis/postgis:17-3.5`, *healthcheck*, volumen), `api` y `web` | DevOps · Daniel | 2.5 | T-HAB-01 | `docker compose up --build` deja los tres servicios sanos y `SELECT postgis_version();` responde. Probado en macOS y en Windows/WSL2 por dos integrantes. |
| T-HAB-03 | Esqueleto FastAPI: configuración con pydantic-settings, sesión de SQLAlchemy 2, ruta `GET /api/salud` que consulta la BD. Los parámetros PS-xx van en un único módulo de configuración (DoD C-6) | Backend dev · Miguel | 2 | T-HAB-02 | `curl localhost:8000/api/salud` → `{"estado":"ok","bd":"ok"}`; la ruta aparece en `/docs`. |
| T-HAB-04 | Alembic con GeoAlchemy2 (ignora tablas internas de PostGIS); migración `0001` con `CREATE EXTENSION IF NOT EXISTS postgis`; `conftest.py` de pytest con BD de prueba limpia por prueba | Backend dev · Miguel | 2 | T-HAB-03 | `alembic upgrade head` y `alembic downgrade base` funcionan sobre una BD vacía; una prueba de humo pasa contra PostGIS. |
| T-HAB-05 | Dependencia `require_role(rol)` (*stub* con `TODO Sprint 2`) y manejador global de errores que devuelve `{"detalle","campo"}` en español | Backend dev · Daniel | 1 | T-HAB-03 | Prueba unitaria: un campo faltante devuelve 422 con `detalle` en español y `campo` con su nombre. |
| T-HAB-06 | Esqueleto React 19 + TypeScript + Vite; ESLint, Vitest + Testing Library; proxy `/api → api:8000`; cliente `apiClient.ts` que interpreta `{"detalle","campo"}`; `lang="es"` | Frontend dev · Anthony | 2 | T-HAB-01 | `npm run lint` y `npm run test` pasan; `localhost:5173` muestra "EcoAlert Tambopata" y el estado de `/api/salud`. |
| T-HAB-07 | Workflow mínimo `.github/workflows/ci.yml` en *push* y PR: backend (Ruff, `alembic upgrade head`, pytest con servicio PostGIS) y frontend (`npm ci`, ESLint, Vitest). **Sin despliegue** | DevOps · Daniel | 2.5 | T-HAB-04, T-HAB-06 | Un PR de prueba muestra los dos jobs en verde; un error de Ruff introducido a propósito lo pone en rojo. |
| T-HAB-08 | Proceso: tablero del sprint con todas las tareas y responsables, `.github/pull_request_template.md` con la lista de la DoD y protección de `main` (CI en verde + 1 aprobación) | SM · Daniel | 1 | T-HAB-01 | No se puede fusionar un PR sin aprobación; el tablero lista todas las tareas con responsable. |
| | **Subtotal** | | **14.5** | | |

---

## 3. HU-E2-1 — Carga de capas de referencia (#4 · 8 SP · comprometida)

**Criterios comprometidos:** RF-03-AC-1 a RF-03-AC-11. **Diferido:** RF-03-AC-12 (403 a la
coordinación) → Sprint 2, con HU-E1-1.

**Diseño base:** tablas `capa_version` (tipo, fuente, fecha de corte, fecha de carga, archivo) y
`elemento_capa` (geometría EPSG:32719, código, nombre, tipo de derecho, estado), **sin ninguna
columna para el titular** (RD-04). La versión vigente de una capa es la de **mayor fecha de
corte**. Flujo de la interfaz: elegir el archivo → la API devuelve sus columnas → el analista
asigna columnas a atributos → envía.

| ID | Tarea | Responsable | h | Depende de | Criterio de "done" | Cubre |
|---|---|---|---:|---|---|---|
| T-E21-01 | *Spike* de datos reales (compartido con HU-E2-2): límite de la RN Tambopata y ZA (SERNANP), catastro de Madre de Dios (INGEMMET) y un archivo de alertas de GeoBosques. Documentar formato, SRC, geometría, columnas, tamaño, codificación y **términos de uso** (RD-13) | QA · Eduardo | 1.5 | — | `docs/datos_fuente.md` fusionado con una ficha por fuente; dudas anotadas para T-PO-01. Los archivos de más de 5 MB no se versionan. | Insumo |
| T-E21-02 | Datos de prueba sintéticos con un script reproducible (`tests/fixtures/generar.py`): catastro `.zip` con `.prj` EPSG:4326 y columna `TITULAR`; `.zip` sin `.prj`; GeoJSON con punto de control; `.kml`; ríos con polígonos; catastro sin código; límite y ZA sintéticos | QA · Eduardo | 2 | T-HAB-04 | `python generar.py` produce los archivos; un README indica qué criterio usa cada uno. | Insumo AC-1 a AC-11 |
| T-E21-03 | **Contrato de la API de capas** (temprano, para desbloquear el frontend): esquemas Pydantic y rutas que responden 501: `GET /api/capas/tipos`, `POST /api/capas/inspeccion`, `POST /api/capas/{tipo}/versiones`, `GET /api/capas/{tipo}/versiones` | Backend dev · Miguel | 1 | T-HAB-05 | Fusionado **a más tardar el día 3**; `/docs` muestra las 4 rutas con esquemas y ejemplos. | Base de AC-9 |
| T-E21-04 | Modelos y migración `0002` de `capa_version` y `elemento_capa` (índice GiST; fuente y fecha de corte NOT NULL) | Backend dev · Daniel | 2 | T-HAB-04 | `\d elemento_capa` muestra `geometry(Geometry,32719)` y ninguna columna de titular. | AC-1, AC-9 |
| T-E21-05 | Módulo común `app/ingesta/lector.py` (lo reutiliza HU-E2-2): acepta solo `.zip` con `.shp/.shx/.dbf/.prj` o `.geojson`; rechaza otros formatos y `.zip` sin `.prj` con mensajes en español; lee con pyogrio; inspección de columnas | Backend dev · Miguel | 2.5 | T-HAB-04, T-E21-02 | Pruebas unitarias pasan con el `.kml`, el `.zip` sin `.prj` y un archivo válido. | AC-5, AC-6 |
| T-E21-06 | Validación por tipo de capa: tipo de geometría, atributos obligatorios, lista blanca de atributos de destino (lo no asignado se descarta, incluido `TITULAR`), reproyección a EPSG:32719 con pyproj (`always_xy`) | Backend dev · Miguel | 2.5 | T-E21-05 | Ríos con polígonos → "La capa de ríos exige geometrías de tipo línea"; catastro sin código → "Falta asignar el atributo obligatorio: código"; el resultado no tiene `TITULAR` y está en EPSG:32719. | AC-1, AC-2, AC-7, AC-8, AC-9 |
| T-E21-07 | Servicio de versiones: versión y elementos en **una sola transacción**; fuente y fecha de corte validadas antes de leer el archivo; `version_vigente(tipo)` por mayor fecha de corte (el criterio de empate lo decide T-PO-01); historial ordenado | Backend dev · Miguel | 2 | T-E21-04, T-E21-06, T-PO-01 | Tras un rechazo, el número de versiones no cambia; con cortes 01/07 y 15/09, cargados en cualquier orden, la vigente es la del 15/09. | AC-3, AC-4, AC-10, AC-11 |
| T-E21-08 | Implementación de las 4 rutas del contrato; la respuesta de carga devuelve id, tipo, fuente, fecha de corte, número de elementos y atributos almacenados | Backend dev · Daniel | 2 | T-E21-03, T-E21-07 | Desde `/docs` se carga el catastro de prueba (201); ninguna ruta responde 501; ninguna respuesta contiene el valor de `TITULAR`. | AC-1 a AC-11 (API) |
| T-E21-09 | Pruebas `test_RF_03_AC_1` … `test_RF_03_AC_6` (AC-2: distancia entre el punto almacenado y su transformación con pyproj ≤ 1 m) | QA · Eduardo | 2 | T-E21-02, T-E21-08 | Las 6 pruebas pasan en local y en CI, con el Dado/cuando/entonces del SRS en su docstring. | AC-1 a AC-6 |
| T-E21-10 | Pruebas `test_RF_03_AC_7` … `test_RF_03_AC_11` (AC-9 revisa columnas de la tabla, contenido almacenado, respuesta JSON y atributos ofrecidos por `GET /tipos`) | QA · Eduardo | 2 | T-E21-02, T-E21-08 | Las 5 pruebas pasan en local y en CI. | AC-7 a AC-11 |
| T-E21-11a | Pantalla "Cargar datos", parte 1: selector de tipo de capa (desde `GET /tipos`), archivo, fuente y fecha de corte, contra un *mock* del contrato | Frontend dev · Anthony | 2 | T-HAB-06, T-E21-03 | El formulario se completa en el navegador; "Cargar" solo se habilita con archivo, fuente y fecha. | AC-3, AC-4 (UI) |
| T-E21-11b | Pantalla "Cargar datos", parte 2: al elegir el archivo llama a la inspección y muestra un selector de columna por atributo de destino; no existe opción de titular | Frontend dev · Anthony | 2 | T-E21-11a | Con el catastro de prueba aparecen sus columnas; "Cargar" solo se habilita con los atributos obligatorios asignados. | AC-8, AC-9 (UI) |
| T-E21-12 | Mensajes: errores de la API junto al campo indicado, confirmación "Capa cargada: <tipo>, corte dd/mm/aaaa, N elementos", estado "Procesando…" (RNF-04); pruebas Vitest | Frontend dev · Anthony | 2 | T-E21-11b | Al menos 3 pruebas Vitest pasan; con la API real, el `.kml` muestra el mensaje de formatos aceptados en español. | AC-3 a AC-8 (UI) |
| T-E21-13 | Integración UI ↔ API y prueba manual con los datos reales: cargar límite, ZA, ríos y catastro **solo desde la interfaz**; revisar en QGIS (conectado a PostGIS) que quedan en EPSG:32719 y bien ubicados | QA · Anthony | 1.5 | T-E21-08, T-E21-12, T-E21-01 | `docs/pruebas_manuales/sprint1_capas.md` con resultado y capturas; defectos registrados en el tablero. | AC-1, AC-9 (de punta a punta) |
| T-E21-14 | Revisión de los PR de backend y pruebas (revisor ≠ autor: los PR de Miguel los revisa Daniel y viceversa) con la lista de la DoD | Backend dev · Daniel | 1 | T-E21-08 a T-E21-10 | PR aprobados, comentarios resueltos, CI en verde. | — |
| T-E21-15 | Revisión de los PR de frontend | QA · Eduardo | 0.5 | T-E21-12 | PR aprobados, comentarios resueltos, CI en verde. | — |
| | **Subtotal** | | **28.5** | | | |

---

## 4. HU-E2-2 — Ingesta acumulativa de alertas GeoBosques (#5 · 8 SP · comprometida)

**Criterios comprometidos:** RF-04-AC-1 a RF-04-AC-5; AC-4 sin la cláusula "sin salir de sus
zonas". **Diferidos:** RF-04-AC-6 (cada alerta en una zona; requiere HU-E3-1) y RF-04-AC-7 (403;
requiere HU-E1-1) → Sprint 2.

**Diseño base:** tablas `carga_alertas` y `alerta` con restricción única **(fuente, código)**.
El ámbito es la unión de las versiones vigentes del límite de la reserva y de la ZA (RD-01). Una
alerta se descarta solo si **no toca** el ámbito. Al final de la ingesta se llama a un gancho
vacío `agrupar_en_zonas(carga_id)` que implementará HU-E3-1.

| ID | Tarea | Responsable | h | Depende de | Criterio de "done" | Cubre |
|---|---|---|---:|---|---|---|
| T-E22-01 | Datos de prueba de alertas (extiende `generar.py`): 120 polígonos con 5 fuera del ámbito; base de 200 + archivo con 150 repetidas y 30 nuevas; archivo de puntos; 3 alertas nuevas con fecha de corte anterior; nombres de columnas reales del *spike* | QA · Eduardo | 1.5 | T-E21-01, T-E21-02 | `generar.py` produce los archivos; una prueba verifica sus conteos. | Insumo AC-1 a AC-5 |
| T-E22-02 | Modelos y migración `0003` de `carga_alertas` y `alerta` (índice GiST, restricción única fuente + código) | Backend dev · Daniel | 1.5 | T-E21-04 | Insertar dos veces la misma alerta GeoBosques falla por la restricción. | AC-1, AC-4 |
| T-E22-03 | Validación y descarte por ámbito: reutiliza `lector.py`; exige polígonos; exige asignar "código" y "fecha de detección"; calcula el ámbito con `version_vigente` y descarta lo que no lo toca; comportamiento sin ámbito cargado según T-PO-01 | Backend dev · Miguel | 1.5 | T-E22-02, T-E21-07, T-PO-01 | Con el archivo de 120 quedan 115 y se descartan 5; el archivo de puntos se rechaza con "Las alertas deben ser polígonos". | AC-1, AC-2, AC-3 |
| T-E22-04 | Lógica acumulativa en una transacción: inserta las nuevas, reconoce las existentes sin modificarlas (RD-06), marca y desmarca "no presente en la última carga", acepta cortes anteriores, arma el resumen y llama al gancho de agrupación | Backend dev · Miguel | 2.5 | T-E22-03 | Escenario 200 → 150 + 30: total 230, 30 nuevas, 150 existentes, 50 no presentes, ninguna borrada. | AC-1, AC-4, AC-5 |
| T-E22-05 | Endpoints `POST /api/alertas/cargas` (fuente fija "GeoBosques", `require_role("analista")`) y `GET /api/alertas/cargas/{id}`; el resumen incluye "N alertas fuera del ámbito". Se mide el tiempo con el archivo real (RNF-04, ≤ 60 s) | Backend dev · Daniel | 2 | T-E22-04, T-E21-03 | Desde `/docs`, el archivo de 120 devuelve `fuera_del_ambito: 5` y "5 alertas fuera del ámbito"; el tiempo con el archivo real queda anotado en el PR. | AC-1 a AC-5 (API) |
| T-E22-06 | Pruebas `test_RF_04_AC_1` … `test_RF_04_AC_5` (AC-4 con la nota `# Sprint 2: RF-05` para la cláusula de zonas) | QA · Eduardo | 2.5 | T-E22-01, T-E22-05 | Las 5 pruebas pasan en local y en CI. | AC-1 a AC-5 |
| T-E22-07 | Pantalla "Cargar datos", modo *alertas GeoBosques*: reutiliza el formulario (fuente fija), asigna "código" y "fecha de detección" | Frontend dev · Anthony | 1.5 | T-E21-11b, T-E22-05 | El archivo de 120 se carga desde la interfaz; el de puntos muestra "Las alertas deben ser polígonos". | AC-3 (UI) |
| T-E22-08 | Resumen de la ingesta en pantalla (nuevas / ya existentes / fuera del ámbito / no presentes / total); prueba Vitest | Frontend dev · Anthony | 1.5 | T-E22-07 | Tras la segunda carga del escenario se ve "30 nuevas · 150 ya existentes · 50 no presentes en la última carga"; `npm run test` pasa. | AC-2, AC-4 (UI) |
| T-E22-09 | Prueba manual con el archivo real de GeoBosques: dos cargas (la segunda modificada), revisar el resumen y comprobar en QGIS que las descartadas están fuera del ámbito | QA · Anthony | 1 | T-E22-08, T-E21-13 | `docs/pruebas_manuales/sprint1_alertas.md` con resultado y capturas. | AC-1, AC-2, AC-4 (de punta a punta) |
| T-E22-10 | Revisión de los PR de backend y pruebas | Backend dev · Miguel | 0.5 | T-E22-06 | PR aprobados y CI en verde. | — |
| T-E22-11 | Revisión de los PR de frontend | QA · Eduardo | 0.5 | T-E22-08 | PR aprobados y CI en verde. | — |
| | **Subtotal** | | **16.5** | | | |

---

## 5. HU-E2-3 — Frescura de fuentes visible (#6 · 3 SP · **extendida, no comprometida**)

Solo se toma si HU-E2-1 y HU-E2-2 ya cumplen la DoD (punto de control del día 8). Como aún no
existen el mapa (HU-E3-2) ni la lista de zonas (RF-10), el "panel de capas" es una sección
**"Estado de las fuentes"** en la pantalla "Cargar datos". RF-07-AC-2 y la parte de RF-07-AC-3
que menciona la lista de zonas quedan para cuando exista RF-10.

| ID | Tarea | Responsable | h | Depende de | Criterio de "done" | Cubre |
|---|---|---|---:|---|---|---|
| T-E23-01 | Servicio de frescura: fecha de corte vigente por capa, última fecha de corte de alertas y aviso si pasaron **más de 30 días** (PS-13), con reloj inyectable | Backend dev · Miguel | 2 | T-E21-07, T-E22-04 | Con el reloj en 04/10/2026: 14 días → sin aviso; 30 días exactos → sin aviso; 45 días → aviso. | AC-1, AC-3, AC-4, AC-5 |
| T-E23-02 | `GET /api/fuentes/frescura` (lectura para ambos roles) con fechas dd/mm/aaaa, "Sin datos cargados" y el texto del aviso | Backend dev · Daniel | 1 | T-E23-01 | `/docs` devuelve una entrada por cada capa y por "Alertas de GeoBosques". | AC-1, AC-3 a AC-5 (API) |
| T-E23-03 | Pruebas `test_RF_07_AC_1`, `test_RF_07_AC_3` (panel), `test_RF_07_AC_4`, `test_RF_07_AC_5` | QA · Eduardo | 1.5 | T-E23-02 | Las 4 pruebas pasan en CI. | AC-1, AC-3 (parcial), AC-4, AC-5 |
| T-E23-04 | Sección "Estado de las fuentes" en la interfaz, que se refresca tras cada carga; prueba Vitest | Frontend dev · Anthony | 2.5 | T-E23-02, T-E22-08 | Tras cargar el catastro con corte 15/09/2026 se ve "15/09/2026"; "Ríos" muestra "Sin datos cargados". | AC-1, AC-3 a AC-5 (UI) |
| T-E23-05 | Prueba manual con una fecha de corte antigua | QA · Anthony | 0.5 | T-E23-04 | Resultado en `docs/pruebas_manuales/sprint1_alertas.md`. | AC-3, AC-5 |
| T-E23-06 | Revisión de PR | Backend dev · Daniel | 0.5 | T-E23-03, T-E23-04 | PR aprobados y CI en verde. | — |
| | **Subtotal (extendida)** | | **8** | | | |

---

## 6. Cierre del sprint y decisiones del PO

| ID | Tarea | Responsable | h | Depende de | Criterio de "done" |
|---|---|---|---:|---|---|
| T-PO-01 | Responder las preguntas abiertas que el SRS no resuelve (sección 8) y anotar las decisiones en los issues #4 y #5. Las que cambien un criterio se registran en `diferencias_SRS.md` (DoD T-3) | PO · Eduardo | 0.5 | — | Decisiones publicadas **a más tardar el día 2**, antes de que empiecen T-E21-07 y T-E22-03. |
| T-CIE-01 | Manual en español (RNF-10, parcial): README con requisitos, `docker compose up`, migraciones y pruebas; `docs/manual_carga.md` con capturas de la carga de capas y de la ingesta de alertas | Frontend dev · Anthony | 1.5 | T-E21-13, T-E22-09 | Un integrante que no escribió el manual levanta el sistema desde cero y carga una capa siguiendo solo el documento. |
| T-CIE-02 | Demo de la Sprint Review: guion (capas e ingesta desde la interfaz, un rechazo en español, PostGIS en QGIS, CI en verde), datos listos y un ensayo | PO · Eduardo | 1.5 | T-E21-13, T-E22-09 | `docs/demo_sprint1.md` fusionado; ensayo hecho en una máquina distinta a la del autor. |
| T-CIE-03 | Actualizar el Product Backlog con los criterios diferidos y su sprint, y registrar las horas reales de cada tarea para calibrar el Sprint 2 | SM · Daniel | 0.5 | — | Las tareas cerradas tienen horas reales; RF-03-AC-12, RF-04-AC-6 y RF-04-AC-7 aparecen anotados en el Sprint 2. |
| | **Subtotal** | | **4** | | |

---

## 7. Totales

### 7.1 Por bloque

| Bloque | Tareas | Horas |
|---|---:|---:|
| Habilitación técnica | 8 | 14.5 |
| HU-E2-1 | 16 | 28.5 |
| HU-E2-2 | 11 | 16.5 |
| Cierre y PO | 4 | 4 |
| **Comprometido** | **39** | **63.5** |
| HU-E2-3 (extendida) | 6 | 8 |

### 7.2 Por rol (comprometido)

| Rol | Horas |
|---|---:|
| Backend dev | 26 |
| Frontend dev | 12.5 |
| QA | 15 |
| DevOps | 6.5 |
| SM | 1.5 |
| PO | 2 |
| **Total** | **63.5** |

### 7.3 Por integrante (comprometido)

| Integrante | Tareas | Horas | Capacidad neta* |
|---|---|---:|---:|
| Miguel | T-HAB-03, 04 · T-E21-03, 05, 06, 07 · T-E22-03, 04, 10 | 16.5 | 12–14 |
| Daniel | T-HAB-01, 02, 05, 07, 08 · T-E21-04, 08, 14 · T-E22-02, 05 · T-CIE-03 | 17.5 | 12–14 |
| Anthony | T-HAB-06 · T-E21-11a, 11b, 12, 13 · T-E22-07, 08, 09 · T-CIE-01 | 15 | 12–14 |
| Eduardo | T-E21-01, 02, 09, 10, 15 · T-E22-01, 06, 11 · T-PO-01 · T-CIE-02 | 14.5 | 12–14 |
| **Total** | | **63.5** | **48–56** |

\* 8–9 h/semana × 2 semanas, menos ≈ 4 h de eventos Scrum por persona. **El compromiso supera la
capacidad**: es una decisión consciente del equipo, explicada con su plan de contingencia en
`sprint1_planning.md` §5.

---

## 8. Preguntas abiertas para el PO (T-PO-01)

Las detectó el agente al descomponer. El SRS no las responde. Junto a cada una va la propuesta
por defecto, que se aplica si el PO no decide otra cosa:

| # | Pregunta | Propuesta por defecto | Afecta a |
|---|---|---|---|
| 1 | ¿Qué pasa si se ingieren alertas antes de cargar el límite de la reserva y la ZA? | Rechazar con "Cargue primero el límite de la reserva y la zona de amortiguamiento". | T-E22-03 |
| 2 | Si dos versiones de una capa tienen la misma fecha de corte, ¿cuál es la vigente? | La última cargada. | T-E21-07 |
| 3 | Una carga con fecha de corte **anterior** (RF-04-AC-5), ¿marca como "no presente" las alertas más recientes que no trae? | No: solo marca la carga con la fecha de corte más reciente. Si no, el analista perdería información válida. | T-E22-04 |
| 4 | Una alerta repetida (misma fuente y código) llega con otra geometría. | Se conserva la original (RD-06), se cuenta como existente y el resumen lo informa. | T-E22-04 |
| 5 | Algunas filas tienen fecha de detección vacía o inválida. | Se ingiere el resto y el resumen informa las filas omitidas. | T-E22-03 |
| 6 | ¿Cuál es el tamaño máximo de archivo? | El *spike* mide los archivos reales; propuesta inicial de 50 MB. | T-E21-05 |

---

## 9. Revisión de la descomposición del agente

**¿Faltan tareas? ¿Hay alguna demasiado grande?** La propuesta del agente fue buena en lo
esencial:
- separó la habilitación de las historias;
- puso el contrato de la API temprano para que el frontend trabaje en paralelo;
- contó las revisiones de PR y las pruebas manuales como tareas;
- nombró cada prueba con su criterio;
- detectó el exceso de capacidad.

Se ajustó así:

| # | Cambio | Motivo |
|---|---|---|
| 1 | **T-E21-11 (4 h) se dividió** en T-E21-11a (formulario base) y T-E21-11b (inspección y asignación de columnas), de 2 h cada una. | Estaba en el límite de 4 h y es la tarea de mayor incertidumbre: React con TypeScript, que el equipo maneja a nivel básico. Dividida, queda un avance demostrable a mitad de camino y es fácil reasignar la segunda parte. |
| 2 | **Se agregó T-PO-01** (0.5 h, día 2). | El agente dejó 6 preguntas abiertas para el PO, pero ninguna tarea para responderlas. Dos tareas de backend (T-E21-07, T-E22-03) dependen de esas respuestas: sin una fecha límite, el backend se bloquearía o decidiría por su cuenta. |
| 3 | El *spike* (T-E21-01) también revisa los **términos de uso** de cada fuente. | RD-13 lo exige, y descargar datos de SERNANP, INGEMMET y GeoBosques es el primer contacto con ellos. |
| 4 | T-HAB-03 centraliza los **parámetros PS-xx** en un único módulo de configuración. | DoD C-6. El agente no lo asignó a ninguna tarea. |
| 5 | Las revisiones de frontend (T-E21-15, T-E22-11) pasan de "Frontend dev" a **QA · Eduardo**. | Hay un solo integrante en frontend: si el rol de revisor era Frontend dev, el autor se revisaba a sí mismo, contra la DoD R-1. |
| 6 | Se cambió el reparto por persona del agente (pensado para su opción A) por **uno para el alcance completo** (§7.3), con nombres y roles. | El equipo decidió mantener ambas historias (ver `sprint1_planning.md` §5). Miguel toma el núcleo geoespacial (domina Python); Daniel, la infraestructura y los endpoints; Anthony, el frontend; Eduardo, como PO, los datos y las pruebas de aceptación. |
| 7 | En la opción elegida (alcance completo), T-CIE-01 y T-CIE-02 vuelven a depender de las pruebas manuales de **ambas** historias. | El agente había quitado esa dependencia solo para su opción A. |
| 8 | Se mantuvieron las decisiones de diseño del agente: errores 422 en `{"detalle","campo"}`, versión vigente por mayor fecha de corte, descarte solo si la alerta no toca el ámbito, y N802 ignorado en las pruebas. | Son coherentes con el SRS (RD-01, RD-06, RF-03, convención `test_RF_XX_AC_Y`). Las que el SRS no resuelve pasaron a T-PO-01. |

**No se aceptó** la recomendación del agente de mover HU-E2-2 a meta extendida (su opción A). Se
documenta en `sprint1_planning.md` §5.
