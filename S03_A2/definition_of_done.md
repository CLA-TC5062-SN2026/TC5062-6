# Definition of Done (DoD) — EcoAlert Tambopata

> Equipo 6 — TC5062, Gpo 10 · S03-A2, Parte 3 · Versión 1.0 (04/10/2026), vigente desde el Sprint 1.
> Propuesta original del agente: `borradores/propuesta_agente_dod.md`. Los ajustes del equipo y
> sus motivos están en la sección 6.

---

## 1. Qué es la DoD y en qué se diferencia de los criterios de aceptación

| | Criterios de aceptación | Definition of Done |
|---|---|---|
| **Responde a** | ¿La historia hace **lo que se pidió**? | ¿La historia está hecha **con la calidad acordada** y se puede entregar? |
| **Alcance** | Propios de **una** historia (`RF-XX-AC-Y` del SRS). | **Comunes a todas** las historias. |
| **Quién los define** | El Product Owner, a partir del SRS. | Todo el equipo. |
| **Formato** | Dado que / cuando / entonces. | Lista de verificación (sí/no). |
| **Cuándo cambian** | Cuando cambia un requerimiento, con registro en `diferencias_SRS.md`. | En la retrospectiva, si el equipo decide subir o ajustar el nivel. |

Una historia está **terminada** solo si cumple **sus criterios y la DoD completa**. Si pasa sus
criterios pero no tiene pruebas, no fue revisada o no arranca con `docker compose up`, **no** está
terminada y no cuenta para la velocidad del sprint.

## 2. Contexto que condiciona esta DoD

- Equipo de 4 estudiantes con 8–9 h/semana cada uno: cada punto debe costar poco o
  automatizarse. Todo punto se comprueba con un sí o un no.
- **Todavía no hay CI/CD completo.** En el Sprint 1 se crea un workflow mínimo de GitHub Actions
  (lint + pruebas) y no hay despliegue automático ni VPS. La DoD acepta como evidencia la
  ejecución local mientras el workflow no exista.
- **Todavía no hay herramienta de pruebas E2E en navegador.** Ningún criterio del Sprint 1 está
  marcado *(Prueba E2E de interfaz.)*.
- Las convenciones de trazabilidad ya están congeladas en el SRS del equipo (`RF-XX-AC-Y`,
  `test_RF_XX_AC_Y`), así que la DoD las reutiliza en lugar de inventar otras.

Si un punto no aplica a una historia (p. ej., una historia sin interfaz), se marca **N/A con el
motivo** en el PR. No se omite en silencio.

---

## 3. DoD de una historia de usuario

Una historia pasa a la columna **Done** del tablero solo cuando se cumple todo lo siguiente.

### 3.1 Requisitos y trazabilidad

- [ ] **T-1.** El issue de la historia lista los `RF-XX-AC-Y` que implementa: **todos** los
  criterios del SRS de sus RF, no solo los CA1–CA3 resumidos en el backlog. Los criterios
  diferidos a otro sprint aparecen con el sprint previsto.
- [ ] **T-2.** El PR cierra el issue (`Closes #NN`) y menciona los `RF-XX-AC-Y` cubiertos.
- [ ] **T-3.** Si durante el desarrollo un criterio resultó incorrecto o faltaba uno, el cambio
  está registrado en `diferencias_SRS.md` con motivo y aprobación del equipo, **sin renumerar**
  IDs.

### 3.2 Código

- [ ] **C-1.** El código llegó a `main` por un **pull request**, no con *push* directo.
- [ ] **C-2.** Ruff (backend) y ESLint + `tsc --noEmit` (frontend) pasan sin errores.
- [ ] **C-3.** Las entradas y salidas de la API son esquemas Pydantic v2.
- [ ] **C-4.** Todo cambio de esquema de la base de datos tiene su migración Alembic, y
  `alembic upgrade head` funciona sobre una base vacía.
- [ ] **C-5.** No hay secretos ni `.env` en el repositorio, ni `print`/`console.log` de
  depuración.
- [ ] **C-6.** Los parámetros del sistema (PS-01 a PS-15) se leen de un único módulo de
  configuración, no como números sueltos. El límite del ámbito se carga como dato (RD-01).

### 3.3 Pruebas

- [ ] **P-1.** Se cumplen **todos** los criterios comprometidos de la historia.
- [ ] **P-2.** Cada criterio automatizable contra la API tiene una prueba pytest **nombrada con su
  ID**: `RF-03-AC-1` → `test_RF_03_AC_1`.
- [ ] **P-3.** Cada criterio marcado *(Prueba E2E de interfaz.)* o *(Prueba de aceptación
  manual.)* tiene evidencia en el issue: pasos, resultado, captura y quién lo verificó. Esto vale
  hasta que exista la herramienta E2E (ver sección 5).
- [ ] **P-4.** Las pruebas geoespaciales corren contra **PostgreSQL 17 + PostGIS** en Docker (no
  contra SQLite ni con geometrías simuladas), con datos de prueba pequeños versionados en el repo.
- [ ] **P-5.** Toda la suite pasa en verde, incluidas las pruebas de historias anteriores. No se
  desactivan pruebas (`skip`) para poder fusionar.
- [ ] **P-6.** Todo endpoint nuevo responde **401 sin sesión** y **403 al rol no autorizado** según
  la matriz §2.3 del SRS, con su prueba. *Sprint 1:* no hay inicio de sesión todavía (HU-E1-1 va
  al Sprint 2). Por eso cada endpoint declara la dependencia de rol y estas pruebas se agregan en
  el Sprint 2 (RF-03-AC-12, RF-04-AC-7).

### 3.4 Revisión y aceptación

- [ ] **R-1.** El PR tiene la aprobación de **al menos un integrante distinto del autor**, que
  revisó también esta lista, no solo el código.
- [ ] **R-2.** Los comentarios de la revisión están resueltos o convertidos en un issue enlazado.
- [ ] **R-3.** El Product Owner vio la historia funcionando en la Sprint Review y la aceptó en el
  issue.

### 3.5 Reglas del dominio (se revisan en cada historia)

- [ ] **D-1.** No introduce etiquetas, textos, campos ni colores que atribuyan una **causa** o la
  **legalidad** de un cambio (RD-02).
- [ ] **D-2.** Ninguna respuesta de la API, pantalla, tabla ni exportación contiene el **titular**
  de un derecho minero. El dato ni siquiera se importa (RD-04).
- [ ] **D-3.** No envía nada fuera del sistema (correo, *webhooks*, terceros) (RD-05).
- [ ] **D-4.** Áreas y distancias en **EPSG:32719**; API del mapa y GeoJSON en **EPSG:4326**
  (RD-10). Los cálculos temporales usan la **fecha de detección** (RD-08).
- [ ] **D-5.** Ante datos faltantes, muestra la situación ("Sin datos cargados", "No disponible")
  y no presenta el resultado como concluido (RNF-08).
- [ ] **D-6.** Todo texto visible, mensaje de error y encabezado de exportación está en
  **español** (RNF-06).
- [ ] **D-7.** Si toca contraseñas: bcrypt o Argon2, mínimo 12 caracteres, nunca en logs
  (RNF-03).

### 3.6 Documentación

- [ ] **DOC-1.** Si la historia cambia cómo se instala, se levanta el sistema, se cargan capas o
  se ingieren alertas, el **README en español** está actualizado (RNF-10).
- [ ] **DOC-2.** Las variables de entorno nuevas están en `.env.example`, sin valores reales.
- [ ] **DOC-3.** Los endpoints aparecen en la documentación OpenAPI con descripción en español.
  Desde S04-A2, `openapi.yaml` referencia los `RF-XX-AC-Y` de cada endpoint.
- [ ] **DOC-4.** El issue está actualizado en GitHub Projects: estado, responsable, SP y enlace al
  PR, y sus sub-issues (tareas) están cerradas.

### 3.7 Integración

- [ ] **I-1.** Las verificaciones de C-2 y P-5 pasan en GitHub Actions. Mientras el workflow no
  exista, el autor pega en el PR la salida local de `ruff check`, `pytest` y `npm run lint`.
- [ ] **I-2.** `docker compose up` desde cero levanta el sistema con las migraciones aplicadas, y
  la historia funciona ahí, no solo en la máquina del autor.
- [ ] **I-3.** No se agregan dependencias de pago (RNF-09). Las dependencias nuevas se justifican
  en el PR.

---

## 4. DoD del sprint (incremento)

Al cierre de cada sprint, además de la DoD por historia:

- [ ] **S-1.** Las historias que no cumplen la DoD **vuelven al Product Backlog**: no hay "casi
  terminadas" y no suman a la velocidad.
- [ ] **S-2.** `main` se levanta con `docker compose up` en una máquina limpia y la demo de la
  Sprint Review se hace sobre ese entorno.
- [ ] **S-3.** Se registra la **velocidad real** (SP terminados) y las horas reales, para
  planificar el siguiente sprint.
- [ ] **S-4.** Los criterios diferidos quedan anotados en sus issues con el sprint previsto.
- [ ] **S-5.** `main` se etiqueta con la versión del sprint (p. ej., `v0.1.0-sprint1`).
- [ ] **S-6.** En la retrospectiva se revisa esta DoD: qué punto costó más, cuál se saltó y si se
  ajusta.

**Regla del Sprint 1:** mientras no exista el inicio de sesión (HU-E1-1), la API **solo corre en
local y en CI**; no se publica en ningún servidor (RNF-01).

---

## 5. Puntos que se suman cuando exista la infraestructura

| Cuándo | Se agrega a la DoD |
|---|---|
| Cuando exista el workflow de GitHub Actions (Sprint 1) | I-1 es **bloqueante**: protección de rama en `main`, que no deja fusionar con el workflow en rojo. |
| Sprint 2 (inicio de sesión) | P-6 completo: 401 y 403 probados en cada endpoint, con la matriz rol × acción de §2.3. |
| Cuando haya pantallas con criterios E2E (mapa, HU-E3-2) | Pruebas automatizadas en navegador (p. ej., Playwright), nombradas por ID, para cada criterio *(Prueba E2E de interfaz.)*. P-3 queda solo para los criterios manuales. |
| Cuando exista el VPS | Despliegue automatizado y verificación de RNF-04 (≤ 60 s con 1,000 alertas). |
| Desde el Sprint 3 | La cobertura del código nuevo (`pytest-cov`) se reporta en el PR. Es informativa, no bloqueante. |

---

## 6. Ajustes a la propuesta del agente

La propuesta del agente estaba bien fundamentada en el SRS (trazabilidad, reglas de dominio,
separación de la DoD y los criterios), pero apuntaba a un equipo con CI/CD, E2E y despliegue ya
montados. Se ajustó así:

| # | Propuesta del agente | Ajuste del equipo | Motivo |
|---|---|---|---|
| 1 | P-09: cobertura ≥ 80 % del código nuevo, bloqueante desde el Sprint 3. | Se quita de la DoD. Desde el Sprint 3 se reporta, sin bloquear (§5). | Con 8–9 h/semana, un umbral fijo empuja a escribir pruebas "para el número". Lo que garantiza la calidad es P-2, una prueba por criterio. |
| 2 | I-01: GitHub Actions completo (lint, `tsc`, pytest, Vitest, construcción de imágenes). | I-1 acepta evidencia local hasta que exista el workflow mínimo (lint + pruebas). La construcción de imágenes y el despliegue quedan fuera. | La actividad pide una DoD para un proyecto **sin CI/CD completo todavía**. |
| 3 | P-03: prueba E2E automatizada para cada criterio marcado E2E. | Se pospone hasta que existan pantallas con criterios E2E (§5). Mientras tanto, evidencia manual (P-3). | En el Sprint 1 no hay criterios E2E, y montar Playwright ahora sería trabajo sin uso. |
| 4 | I-04: verificar RNF-04 (≤ 60 s, 1,000 alertas) en cada historia afectada. | Se pasa a §5 (cuando exista el VPS). | Medir rendimiento en las laptops del equipo no representa el servidor. |
| 5 | DOC-04: registro de decisiones (ADR) para decisiones no obvias. | Se elimina como punto obligatorio. | Es valioso pero no se puede verificar con un sí o un no. Basta un comentario en el código o en el PR. |
| 6 | DOC-01: `openapi.yaml` con referencias `RF-XX-AC-Y` desde el Sprint 1. | DOC-3: la documentación generada por FastAPI basta hasta S04-A2. | `openapi.yaml` es el entregable de S04-A2; no se adelanta. |
| 7 | S-03 y S-04: reporte de trazabilidad automatizado y prueba de humo de la matriz de roles por sprint. | Se sustituyen por S-3 (velocidad real) y S-4 (criterios diferidos). La matriz de roles pasa a P-6 desde el Sprint 2. | En el Sprint 1 no hay roles todavía. El dato más útil al cerrar el primer sprint es la velocidad real. |
| 8 | P-06: 401/403 en todo endpoint, sin excepción. | Se mantiene como regla, con la excepción explícita del Sprint 1 y su compensación (dependencia de rol declarada, pruebas en el Sprint 2, API solo local). | Es una decisión del Sprint Planning (`sprint1_planning.md` §6.3). La DoD la hace visible en lugar de ignorarla. |
| 9 | T-01 sin precisar qué criterios cuentan. | T-1 exige **todos** los `RF-XX-AC-Y` del RF, no solo los CA1–CA3 del backlog. | El backlog resume 2–3 criterios por historia, pero el SRS congelado tiene más (RF-03 tiene 12). Sin esta regla, una historia podría quedar "Done" con criterios del SRS sin probar (observación del propio agente). |
| 10 | Siete categorías con 42 puntos y una plantilla de PR completa. | 32 puntos por historia y 6 del sprint. La plantilla de PR se crea como tarea de habilitación del Sprint 1 a partir de esta lista. | Una lista más corta sí se revisa en cada PR. |

Se mantuvieron sin cambios, por ser baratos y críticos: pruebas nombradas por ID, pruebas contra
PostGIS real, revisión por un segundo integrante y las reglas de dominio RD-02, RD-04 y RD-05.
