> Salida original del agente (Parte 1), sin editar.

# Sprint Planning — Sprint 1 · EcoAlert Tambopata

**Equipo 6 — TC5062, Gpo 10** · Facilitación: agente en rol de Scrum Master
**Fecha de la planeación:** 04/10/2026 · **Duración del sprint:** 2 semanas (propuesta: 05/10/2026 – 18/10/2026)
**Entradas:** `S03_A1/backlog_completo.md` (15 HU, 5 épicas, SP Fibonacci), `S03_A1/priorizacion_comparada.md` (orden del PO en 4 bloques), `S03_A1/SRS_equipo.md` (línea base v1.0, criterios `RF-XX-AC-Y`).

---

## 0. Punto de partida

| Aspecto | Situación |
|---|---|
| Código | El repositorio del equipo **no tiene código**: no hay backend, frontend, base de datos, Docker Compose ni CI. |
| Stack (SRS §2.1) | Python 3.12 + FastAPI + SQLAlchemy 2 + Alembic · PostgreSQL 17 + PostGIS · React 19 + TypeScript + Vite · Docker Compose. |
| Velocidad histórica | No existe (primer sprint). La capacidad se estima con un supuesto explícito (sección 2). |
| Orden del PO | Bloque 1: HU-E4-1, HU-E4-2, HU-E3-1, HU-E2-2, HU-E5-1 · Bloque 2: HU-E2-1, HU-E2-3, HU-E3-2, HU-E3-3, HU-E4-3 · Bloque 3: HU-E5-2, HU-E1-1, HU-E1-2 · Bloque 4: HU-E1-3, HU-E5-3. |

**Observación clave de la facilitación.** El orden del PO es por **valor de negocio**, pero las
historias de mayor valor forman una **cadena de dependencias técnicas** que obliga a construir
desde abajo:

```
HU-E2-1 Capas de referencia (límite RN + ZA = ámbito, RD-01)
   └─► HU-E2-2 Ingesta de alertas GeoBosques (descarta lo que está fuera del ámbito)
          └─► HU-E3-1 Agrupación en zonas (RF-05; RF-04-AC-6 exige que cada alerta quede en una zona)
                 └─► HU-E4-1 Puntaje explicado (RF-09; necesita zonas, límite de la reserva y ríos)
                        └─► HU-E4-2 Lista priorizada y ajuste manual (RF-10, RF-11)
                        └─► HU-E5-1 Comparación de periodos (RF-14; compara alertas y puntajes por zona)
```

No se puede priorizar zonas sin haberlas agrupado, ni agrupar sin alertas ingeridas, ni ingerir
alertas "dentro del ámbito" sin el límite de la reserva y la ZA cargados **como dato** (RD-01: "el
límite se carga como dato, no como constante en el código"). Por eso el Sprint 1 empieza por la
base de la cadena, que es la única parte del Bloque 1 que el equipo puede terminar en dos semanas
partiendo de cero.

---

## 1. Sprint Goal propuesto

> **Al cierre del Sprint 1, un analista SIG puede cargar el límite de la RN Tambopata, la zona de
> amortiguamiento y el catastro minero, e ingerir un archivo de alertas de GeoBosques de forma
> acumulativa —sin duplicados y descartando lo que queda fuera del ámbito— sobre un entorno que se
> levanta con `docker compose up` y se valida en CI.**

**Por qué es concreto:** nombra exactamente qué datos entran al sistema y con qué reglas.

**Cómo se mide (criterio de éxito del objetivo):**

1. Los **16 criterios comprometidos** (RF-03-AC-1 a RF-03-AC-11 y RF-04-AC-1 a RF-04-AC-5) están
   automatizados como `test_RF_03_AC_1` … `test_RF_04_AC_5` y pasan **en verde en GitHub Actions**
   contra un contenedor PostgreSQL 17 + PostGIS.
2. `docker compose up` levanta base de datos, API y frontend en una máquina limpia de cualquier
   integrante, y `alembic upgrade head` crea el esquema con la extensión PostGIS.
3. En la Sprint Review se hace una demostración con datos reales de Tambopata: se carga el límite
   de la reserva y la ZA, se ingiere un archivo de GeoBosques dos veces (la segunda con alertas
   repetidas y nuevas) y el resumen muestra nuevas / existentes / fuera del ámbito / "no presente
   en la última carga". Las capas almacenadas se abren en QGIS conectado a PostGIS para comprobar
   la reproyección a EPSG:32719.

**Por qué es alcanzable:** compromete 16 SP (dos historias de 8 SP que comparten el mismo
mecanismo de carga, validación y reproyección) dentro de una capacidad estimada de 14–16 SP, con
margen reservado y con tres criterios explícitamente diferidos (sección 3.3).

**Por qué aporta valor aunque no llegue a la priorización:** deja en el sistema los datos de los
que depende **todo** el Bloque 1 del PO (HU-E3-1, HU-E4-1, HU-E4-2, HU-E5-1), con trazabilidad de
fuente y fecha de corte (RD-06, RD-08) desde el primer día, y deja resuelta la plataforma técnica
que el resto de los sprints reutiliza.

---

## 2. Capacidad del equipo

### 2.1 Horas

| Concepto | Cálculo | Horas |
|---|---|---|
| Capacidad bruta | 4 integrantes × 8–9 h/semana × 2 semanas | 64–72 h |
| **Base de planeación** | Se toma el **límite inferior** por ser el primer sprint | **64 h** |
| Eventos Scrum | ≈ 4 h por persona: Sprint Planning 1.5 h, Daily asíncrona (≈ 15 min/semana de lectura y escritura), refinamiento del Sprint 2 0.5 h, Sprint Review 1 h, Retrospectiva 0.75 h | − 16 h |
| Capacidad neta | | 48 h |
| Habilitación técnica (no es HU, no se estima en SP) | Estructura del repo, Docker Compose con PostGIS, esqueleto FastAPI + SQLAlchemy + Alembic, esqueleto React + Vite, pytest/Ruff y Vitest/ESLint, workflow de GitHub Actions con servicio PostGIS | − 12 h |
| Disponible para historias | | 36 h |
| **Margen de incertidumbre (20 %)** | Primer sprint, curva de aprendizaje de PostGIS/GeoAlchemy y lectura de Shapefiles, TypeScript básico, cargas académicas de otros cursos | − 7 h |
| **Capacidad comprometible** | | **≈ 29 h** |

### 2.2 Conversión a Story Points

- **Supuesto de conversión:** sin velocidad histórica, el equipo calibra con una **historia de
  referencia**: HU-E2-3 (3 SP) se descompone en un endpoint, dos reglas de fechas y cinco pruebas,
  más revisión de PR; se estima en **5.5–6 h** → **1 SP ≈ 1.8–2 h** de trabajo efectivo,
  incluyendo pruebas, revisión y fusión.
- **Capacidad en SP:** 29 h ÷ 2 h/SP ≈ 14.5 SP · 29 h ÷ 1.8 h/SP ≈ 16 SP → **14–16 SP**.
- **Compromiso:** **16 SP** (límite superior del rango). Se justifica porque:
  1. HU-E2-2 reutiliza el mecanismo de HU-E2-1 (RF-04: "con la misma validación de formato y SRC
     que RF-03"), así que su costo real es menor que el de dos historias independientes;
  2. se difieren tres criterios que dependen de historias no seleccionadas (sección 3.3);
  3. el margen del 20 % ya está descontado antes de convertir.
- **Meta extendida (no comprometida):** HU-E2-3 (3 SP). Solo se toma si ambas historias
  comprometidas cumplen la Definition of Done antes del día 8 del sprint.
- **Nota:** esta conversión horas ↔ SP es un supuesto **solo para el primer sprint**. A partir del
  Sprint 2 se planifica con la velocidad real medida (SP terminados), no con horas.

---

## 3. Sprint Backlog

### 3.1 Historias seleccionadas

| Orden | HU | SP | Bloque PO | Estado en el sprint |
|---|---|---|---|---|
| 1 | **HU-E2-1** — Carga de capas de referencia (RF-03) | 8 | 2 | Comprometida (acotada: 11 de 12 criterios) |
| 2 | **HU-E2-2** — Ingesta acumulativa de alertas GeoBosques (RF-04) | 8 | 1 | Comprometida (acotada: 5 de 7 criterios) |
| — | **Total comprometido** | **16** | | |
| 3 | HU-E2-3 — Frescura de fuentes visible (RF-07) | 3 | 2 | Meta extendida, no comprometida |

### 3.2 Justificación de cada historia

**HU-E2-1 — Carga de capas de referencia (8 SP).**
- *Valor:* sin el límite de la RN Tambopata y la ZA no existe el **ámbito** (RD-01), y sin ríos y
  catastro no hay contexto (RF-08) ni tres de los cinco factores del puntaje dependen de capas
  (ubicación y cercanía a ríos, RF-09). Además, garantiza desde el inicio dos reglas de dominio
  críticas: **ningún titular minero se importa** (RD-04, RF-03-AC-9) y toda capa queda con fuente
  y fecha de corte (RD-06).
- *Dependencias:* ninguna hacia otras HU; solo de la habilitación técnica. Es la raíz de la cadena.
- *Orden del PO:* está en el Bloque 2, pero se adelanta porque es **prerrequisito técnico** de
  HU-E2-2 (Bloque 1). El PO ordena por valor; el equipo respeta ese orden **dentro** de lo que las
  dependencias permiten.

**HU-E2-2 — Ingesta acumulativa de alertas GeoBosques (8 SP).**
- *Valor:* es la **primera historia del Bloque 1 que se puede construir**. Las alertas son la
  materia prima de zonas, puntaje y comparación. La ingesta acumulativa con detección de
  duplicados y la marca "no presente en la última carga" protegen el historial completo que
  necesitan la persistencia (RF-09) y la comparación de periodos (RF-14).
- *Dependencias:* necesita HU-E2-1 (límite + ZA cargados para descartar lo que está fuera del
  ámbito, RF-04-AC-1/AC-2) y reutiliza su validación de formato y SRC. Por eso va **después** de
  HU-E2-1 en el sprint.
- *Orden del PO:* Bloque 1, posición 4. Las tres historias anteriores del Bloque 1 dependen de ella.

**HU-E2-3 — Frescura de fuentes (3 SP, meta extendida).**
- *Valor:* evita interpretar datos viejos como actuales (RD-08, RNF-08); es barata porque solo usa
  las fechas de corte que las dos historias anteriores ya guardan.
- *Por qué no se compromete:* la capacidad calculada (14–16 SP) ya está cubierta. Se deja como
  meta extendida para no poner en riesgo el Sprint Goal.

### 3.3 Acotamiento: criterios diferidos por dependencias no seleccionadas

Las dos historias seleccionadas tienen criterios que dependen de historias que **no** entran al
Sprint 1. Se propone acotarlas así (los IDs no cambian; solo se mueve el sprint en que se cumplen):

| Criterio | Depende de | Decisión | Sprint previsto |
|---|---|---|---|
| **RF-03-AC-12** — la coordinación recibe 403 al cargar capas | HU-E1-1 (RF-01: sesión) y roles de HU-E1-2 (RF-02) | Diferido. Los endpoints se escriben desde ya con una dependencia `require_role("analista")` de FastAPI, para que el 403 real se active al integrar el inicio de sesión. | Sprint 2 |
| **RF-04-AC-7** — la coordinación recibe 403 al ingerir alertas | HU-E1-1 / HU-E1-2 | Diferido, igual que el anterior. | Sprint 2 |
| **RF-04-AC-6** — cada alerta ingerida pertenece a exactamente una zona | HU-E3-1 (RF-05: agrupación) | Diferido. En el Sprint 1 la ingesta termina en "alertas almacenadas"; el gancho para invocar la agrupación al final de la ingesta se deja como punto de extensión vacío. | Sprint 2 |

Además, dos criterios comprometidos se cumplen **parcialmente** porque mencionan elementos que aún
no existen; se deja explícito qué se verifica ahora y qué se completa después:

| Criterio | Se verifica en el Sprint 1 | Se completa en |
|---|---|---|
| **RF-04-AC-4** ("…sin salir de sus zonas") | 230 alertas, resumen 30 nuevas / 150 existentes, 50 marcadas "no presente en la última carga" sin borrarse. | La cláusula "sin salir de sus zonas" se agrega a la prueba cuando exista HU-E3-1 (Sprint 2). |
| **RF-03-AC-10 / AC-11** ("…los cálculos usan la del 15/09/2026") | Una función de consulta de **versión vigente por tipo de capa** (la de fecha de corte más reciente, no la última cargada) y el historial de versiones. | Los cálculos que la consumen (RF-05, RF-08, RF-09) la reutilizan en sprints posteriores. |

**Riesgo aceptado por diferir el control de acceso:** mientras no exista HU-E1-1, la API **no se
despliega** fuera de las máquinas de los integrantes ni del CI (RNF-01 exige autenticación en todas
las rutas). Esta condición forma parte de la Definition of Done del Sprint 1.

### 3.4 Por qué quedan fuera las demás historias de mayor prioridad del PO

| HU | Bloque PO | SP | Motivo por el que no entra al Sprint 1 |
|---|---|---|---|
| HU-E4-1 Puntaje explicado | 1 (pos. 1) | 13 | Calcula sobre **zonas** (HU-E3-1) y usa el límite de la reserva y los ríos (HU-E2-1). Sin zonas no hay nada que puntuar. Sus 13 SP, solos, ya igualan la capacidad del sprint. |
| HU-E4-2 Lista priorizada y ajuste | 1 (pos. 2) | 8 | Ordena por el puntaje de HU-E4-1; sin puntaje no hay lista que ordenar ni ajustar. |
| HU-E3-1 Agrupación en zonas | 1 (pos. 3) | 13 | Necesita alertas ingeridas (HU-E2-2), que se construyen en este sprint. 8 + 8 + 13 = 29 SP, casi el doble de la capacidad. Es la candidata principal del Sprint 2. |
| HU-E5-1 Comparación de periodos | 1 (pos. 5) | 8 | Compara alertas **por zona** y guarda el puntaje en el análisis (CA3: "puntaje 62"); depende de HU-E3-1 y HU-E4-1. |
| HU-E3-2 Mapa con capas | 2 | 8 | Necesita capas y zonas que mostrar (RF-06-AC-1 lista la capa de zonas) y es la historia con más trabajo de frontend en TypeScript, que el equipo maneja a nivel básico; conviene hacerla cuando ya hay datos que dibujar. |
| HU-E3-3 Contexto territorial | 2 | 5 | Cruza **zonas** con capas (RF-08); depende de HU-E3-1. |
| HU-E4-3 Estados e historial | 2 | 8 | Opera sobre zonas (RF-12-AC-1: "el sistema crea una zona…") y sobre ajustes y marcas para el historial unificado (RF-12-AC-20). |
| HU-E1-1 Inicio de sesión | 3 | 5 | Su valor de negocio es menor según el PO y no bloquea el desarrollo local; sí bloquea cualquier **despliegue** (RNF-01). Se planifica para el Sprint 2, junto con la activación de los criterios 403 diferidos. |

**Alternativas evaluadas y descartadas:**
- *Rebanada vertical delgada (ingesta → agrupación → puntaje):* 8 + 13 + 13 = 34 SP como mínimo,
  más del doble de la capacidad; recortarla dejaría las tres historias a medias y ninguna
  terminada, lo que no permite medir velocidad.
- *HU-E2-2 + HU-E3-1, cargando el límite con un script en lugar de HU-E2-1:* 21 SP (fuera de
  capacidad) y contradice RD-01 (el límite se carga como dato con fuente y fecha de corte) y RD-06.

### 3.5 Tareas del Sprint Backlog (propuesta para que el equipo las afine)

| # | Tarea | HU | Estimación | Sugerencia de responsable |
|---|---|---|---|---|
| T1 | Estructura del repo (`backend/`, `frontend/`, `docker/`), `.env.example`, README de arranque | Habilitación | 1.5 h | Integrante 1 |
| T2 | `docker-compose.yml` con `postgis/postgis:17`, API FastAPI y frontend Vite; volumen persistente | Habilitación | 3 h | Integrante 1 |
| T3 | Esqueleto FastAPI + SQLAlchemy 2 + GeoAlchemy2 + Alembic (migración inicial con `CREATE EXTENSION postgis`), endpoint de salud | Habilitación | 3 h | Integrante 2 |
| T4 | Esqueleto React 19 + TS + Vite con Vitest y ESLint (pantalla vacía) | Habilitación | 1.5 h | Integrante 3 |
| T5 | GitHub Actions: Ruff + pytest con servicio PostGIS; Vitest + ESLint | Habilitación | 3 h | Integrante 1 |
| T6 | *Spike* (día 1–2): descargar un archivo real de GeoBosques y el límite oficial SERNANP de Tambopata; documentar columnas, formato y SRC | HU-E2-1 / HU-E2-2 | 2 h | Integrante 4 |
| T7 | Datos de prueba sintéticos: Shapefile .zip con y sin .prj, GeoJSON con punto de control, archivo con puntos, catastro con columna "TITULAR", alertas dentro/fuera del ámbito | HU-E2-1 / HU-E2-2 | 3 h | Integrante 4 |
| T8 | Modelo y migración de capas y versiones (tipo, fuente, fecha de corte, geometría EPSG:32719); **sin atributo de titular** | HU-E2-1 | 2.5 h | Integrante 2 |
| T9 | Módulo común de lectura y validación: formato (.zip con .prj o GeoJSON), SRC, tipo de geometría, asignación de columnas, reproyección a EPSG:32719 | HU-E2-1 (reutiliza HU-E2-2) | 4 h | Integrante 2 |
| T10 | Endpoint de carga de capas + consulta de versión vigente e historial de versiones | HU-E2-1 | 2.5 h | Integrante 3 |
| T11 | Pruebas `test_RF_03_AC_1` … `test_RF_03_AC_11` | HU-E2-1 | 3 h | Integrante 3 |
| T12 | Modelo y migración de alertas y cargas (fuente, código, geometría, fecha de detección, fecha de ingesta, fecha de corte de la carga, marca "no presente") | HU-E2-2 | 2 h | Integrante 4 |
| T13 | Lógica de ingesta acumulativa: duplicados por (fuente, código), descarte fuera del ámbito (RN ∪ ZA vigentes), marca "no presente", resumen de la carga | HU-E2-2 | 4 h | Integrante 2 / 4 |
| T14 | Pruebas `test_RF_04_AC_1` … `test_RF_04_AC_5` | HU-E2-2 | 2.5 h | Integrante 3 / 4 |
| T15 | Preparar la demo de la Review (guion, datos reales, conexión QGIS → PostGIS) | Sprint Goal | 1 h | Integrante 1 |

Total aproximado: 12 h de habilitación (T1–T5) + ≈ 27.5 h de historias (T6–T15) ≈ 39.5 h, dentro de
las 48 h netas y dejando ≈ 8.5 h de margen.

### 3.6 Definition of Done aplicada en el Sprint 1

- Cada criterio comprometido tiene una prueba automatizada con su nombre `test_RF_XX_AC_Y` y pasa
  en CI.
- Ruff y ESLint sin errores; migraciones Alembic reproducibles desde una base vacía.
- Pull request revisado y aprobado por otro integrante antes de fusionar a `main`.
- Ningún dato, respuesta de la API ni tabla contiene el titular de un derecho minero (RD-04).
- La API no se expone fuera de los entornos locales y del CI mientras no exista inicio de sesión.
- Los criterios diferidos quedan anotados en el Product Backlog con el sprint previsto.

### 3.7 Secuencia sugerida dentro del sprint

| Días | Enfoque |
|---|---|
| 1–3 | Habilitación técnica (T1–T5) en paralelo con el *spike* de datos reales y los datos de prueba (T6–T7). |
| 3–6 | HU-E2-1 completa (T8–T11). **Punto de control día 6:** si HU-E2-1 no cumple la DoD, el equipo y el PO renegocian el alcance de HU-E2-2 sin cambiar el Sprint Goal (p. ej., mover RF-04-AC-5 al Sprint 2). |
| 6–9 | HU-E2-2 (T12–T14). Si ambas historias están terminadas el día 8, se toma HU-E2-3. |
| 10 | Preparación de la demo, Sprint Review y Retrospectiva; registro de la velocidad real. |

---

## 4. Riesgos del sprint

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | **La habilitación técnica consume más de las 12 h previstas** (primer Docker Compose con PostGIS, CI con servicio de base de datos). | Alta | Alto | Un responsable (Integrante 1) y timebox; usar la imagen oficial `postgis/postgis:17`; si el día 3 no está lista, el resto avanza con PostGIS local y se integra después. |
| R2 | **Formato real de GeoBosques distinto del supuesto** (nombres de columnas, polígonos vs. puntos, SRC, codificación). | Media | Alto | *Spike* T6 en los días 1–2, antes de escribir la lógica de ingesta; la asignación de columnas (RF-04) absorbe diferencias de nombres. |
| R3 | **Dependencias geoespaciales nativas** (GDAL/pyogrio/Fiona, PROJ) difíciles de instalar en distintas máquinas y arquitecturas (arm64/amd64). | Media | Alto | Ejecutar backend y pruebas **solo dentro de Docker**; fijar versiones en el `Dockerfile`; la CI usa la misma imagen. |
| R4 | **Entornos heterogéneos del equipo** (Windows y macOS; finales de línea, rutas, Docker Desktop/WSL2). | Media | Medio | `.gitattributes` con LF, `.editorconfig`, todo el flujo vía `docker compose`; validar el arranque en las cuatro máquinas en la primera semana. |
| R5 | **Estimación sin velocidad histórica**: la conversión 1 SP ≈ 1.8–2 h puede estar equivocada. | Alta | Medio | Margen del 20 %, meta extendida separada del compromiso y punto de control el día 6; registrar horas reales para calibrar el Sprint 2. |
| R6 | **Disponibilidad parcial** (8–9 h/semana) y entregas de otros cursos que se cruzan. | Media | Medio | Daily asíncrona para detectar bloqueos temprano; tareas pequeñas (≤ 4 h) que se puedan reasignar. |
| R7 | **Curva de aprendizaje** de PostGIS, GeoAlchemy2 y reproyección; casos límite de SRC (.prj sin código EPSG, ejes lat/lon). | Media | Medio | Pruebas con punto de control contra pyproj (RF-03-AC-2) desde el inicio; programación en pareja en T9. |
| R8 | **API sin autenticación** durante el sprint (criterios 403 diferidos). | Baja | Alto | No desplegar fuera de local/CI (DoD); dependencia `require_role` presente desde el primer endpoint; HU-E1-1 como prioridad del Sprint 2. |
| R9 | **Fuente oficial de algunas capas no resuelta** (TA-02: capa de ríos). | Media | Bajo | No bloquea el Sprint 1: RF-03 acepta cualquier fuente declarada; se usa una capa de ríos de prueba y se registra la fuente real cuando el equipo la defina. |
| R10 | **Desviación de alcance hacia la interfaz** (formularios de carga, mapa) antes de tener la API estable. | Media | Medio | Los criterios comprometidos son de API; la demo usa `/docs` de FastAPI y QGIS. La pantalla de carga se planifica con HU-E1-1 y HU-E3-2. |
| R11 | **El valor visible para el PO es limitado** (no hay zonas ni puntaje al final del sprint). | Media | Medio | Explicar la cadena de dependencias en la Review, mostrar datos reales de Tambopata en QGIS y presentar el plan tentativo del Sprint 2 (HU-E3-1 + HU-E1-1). |

---

## 5. Proyección tentativa (para el refinamiento, no es compromiso)

| Sprint | Candidatas | Comentario |
|---|---|---|
| 2 | HU-E3-1 (13) + HU-E1-1 (5) + criterios diferidos (RF-03-AC-12, RF-04-AC-6, RF-04-AC-7); HU-E2-3 si no se tomó | Cierra la cadena ingesta → zonas y habilita el despliegue con sesión. Se ajusta con la velocidad real del Sprint 1. |
| 3 | HU-E4-1 (13) + HU-E2-3 / HU-E1-2 | Primer puntaje explicado: el núcleo de valor del PO. |
| 4+ | HU-E4-2, HU-E3-2, HU-E3-3, HU-E4-3, HU-E5-1, HU-E5-2 … | Según el orden de bloques del PO y la velocidad medida. |
