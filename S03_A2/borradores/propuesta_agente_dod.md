> Salida original del agente (Parte 3), sin editar.

# Propuesta de Definition of Done (DoD) — EcoAlert Tambopata

**Equipo 6 — TC5062, Gpo 10.** Propuesta del agente asesor de Scrum. Es la DoD "ideal" que
recomiendo; el equipo la ajustará en la revisión.

Fuentes consultadas: `S03_A1/SRS_equipo.md` (v1.0, línea base congelada: §2.1 stack, §2.3 matriz
de permisos, §3 convención Given-When-Then y "Convención de IDs y línea base congelada", RNF-01 a
RNF-15, RD-01 a RD-13) y `S03_A1/backlog_completo.md` (épicas E1–E5, 15 historias).

---

## 1. DoD frente a criterios de aceptación

Son dos cosas distintas que se complementan. Una historia está terminada solo cuando cumple
**ambas**.

| | Criterios de aceptación (CA) | Definition of Done (DoD) |
|---|---|---|
| **Qué responde** | ¿Hace **lo que se pidió**? (el *qué* de esta historia) | ¿Está hecha **con la calidad acordada**? (el *cómo* de todo el trabajo) |
| **Alcance** | Específicos de **una** historia. Cada HU tiene los suyos. | **Comunes a todas** las historias del proyecto. |
| **Quién los define** | El Product Owner, a partir del SRS (`RF-XX-AC-Y`). | Todo el equipo de desarrollo (acuerdo de equipo). |
| **Formato** | Given-When-Then ("Dado que / cuando / entonces"). | Lista de verificación (checklist). |
| **Ejemplo EcoAlert** | HU-E4-2 CA3: "Dado un ajuste sin justificación, cuando se confirma, entonces se rechaza y el puntaje vigente no cambia." | "Toda acción que el rol Coordinación no puede hacer responde 403 en el servidor y tiene una prueba que lo verifica." |
| **Cuándo cambia** | Cuando cambia el requerimiento (con registro en `diferencias_SRS.md`). | En la retrospectiva, cuando el equipo decide subir (o, con motivo, ajustar) el nivel de calidad. |

En pocas palabras: **los CA dicen que la funcionalidad es correcta; la DoD dice que el incremento
es entregable**. Una HU que pasa todos sus CA pero no tiene pruebas, no está revisada o rompe el
despliegue con Docker Compose **no** está terminada. Uno de los puntos de la DoD es, justamente,
"se cumplen todos los criterios de aceptación de la historia" (punto P-01): la DoD contiene a los
CA, pero no se reduce a ellos.

---

## 2. Principios con que se armó la propuesta

1. **Verificable:** cada punto se puede marcar sí/no mirando el PR, el pipeline o el tablero.
   Nada de "código de buena calidad" sin forma de comprobarlo.
2. **Proporcional al equipo:** 4 personas × 8–9 h/semana ≈ 70 h por sprint de 2 semanas. Los
   puntos cuestan poco si se automatizan (Ruff, ESLint, pytest, Vitest, GitHub Actions); lo
   manual se limitó a la revisión por pares y a la demostración.
3. **Anclada en el SRS:** reutiliza la trazabilidad ya congelada (`RF-XX-AC-Y`,
   `test_RF_XX_AC_Y`, `openapi.yaml`) y convierte en verificación permanente los RNF y RD que
   aplican a **todas** las historias (403 en servidor, sin titulares, sin etiquetas causales,
   EPSG, español).
4. **Lo que no aplica, se declara:** si un punto no aplica a una historia (p. ej., una HU sin
   interfaz no lleva prueba E2E), se escribe "N/A" con el motivo en el PR. No se omite en
   silencio.

---

## 3. Definition of Done propuesta (por historia de usuario)

Una historia de usuario pasa a la columna **Done** del tablero de GitHub Projects solo cuando se
cumplen **todos** los puntos siguientes (o están marcados N/A con motivo).

### 3.1 Requisitos y trazabilidad

| ID | Condición | Por qué |
|---|---|---|
| T-01 | Cada CA de la HU está vinculado al ID del SRS que implementa (`RF-XX-AC-Y`) en el issue. | El backlog usa CA1, CA2…; el SRS congeló `RF-XX-AC-Y` como clave de trazabilidad para API y pruebas. Sin el vínculo se pierde la cadena requerimiento → código → prueba. |
| T-02 | Si durante el desarrollo se descubrió que un CA estaba mal o faltaba uno, el cambio está registrado en `diferencias_SRS.md` (o en su sucesor) con motivo y aprobación del equipo, **sin renumerar** IDs existentes. | La línea base está congelada: un criterio nuevo toma el siguiente número libre y uno retirado no se reutiliza. |
| T-03 | El issue está cerrado mediante el PR que lo implementa (`Closes #NN`) y el PR menciona los `RF-XX-AC-Y` cubiertos. | Permite rastrear desde el tablero qué código atiende cada criterio. |

### 3.2 Código

| ID | Condición | Por qué |
|---|---|---|
| C-01 | El código está en `main` mediante un PR fusionado; nadie hace *push* directo a `main`. | Garantiza que todo pasa por revisión y por el pipeline. |
| C-02 | Backend: Ruff (lint + formato) sin errores. Frontend: ESLint sin errores y `tsc --noEmit` sin errores de tipos. | Estilo uniforme entre cuatro personas y errores detectados antes de la revisión. TypeScript es nuevo para parte del equipo: el compilador es su primera red de seguridad. |
| C-03 | Backend con *type hints*; los modelos de entrada y salida de la API son esquemas Pydantic v2 (no `dict` sueltos). | La validación de entrada vive en un solo lugar y alimenta el `openapi.yaml` generado por FastAPI. |
| C-04 | Todo cambio de esquema de base de datos tiene su migración Alembic, que sube (`upgrade`) y baja (`downgrade`) sin error sobre una base limpia. | Evita bases divergentes entre integrantes y despliegues que no arrancan. |
| C-05 | Sin código muerto, sin `print`/`console.log` de depuración y sin secretos (contraseñas, claves de GEE, `.env`) en el repositorio. | Higiene básica y RNF-03 (las contraseñas nunca en texto plano). |
| C-06 | Los parámetros del sistema (PS-01 a PS-15) se leen de una única fuente de configuración, no como números mágicos repartidos en el código; el límite del ámbito se carga como dato (RD-01). | El SRS declara que pesos y umbrales son preliminares (TA-01): deben poder cambiarse en un solo lugar. |

### 3.3 Pruebas

| ID | Condición | Por qué |
|---|---|---|
| P-01 | **Se cumplen todos los criterios de aceptación de la HU**, demostrado por pruebas o, en los marcados manuales, por la evidencia de P-05. | Es el puente entre la DoD y los CA. |
| P-02 | Cada CA automatizable contra la API tiene **al menos una prueba pytest nombrada con su ID**: `RF-09-AC-1` → `test_RF_09_AC_1`. | Convención congelada en el SRS (S09-A1). Permite saber qué criterio falla con solo leer el reporte. |
| P-03 | Cada CA marcado *(Prueba E2E de interfaz.)* tiene su prueba automatizada en navegador (p. ej., Playwright), con el mismo nombre por ID. | El SRS exige automatizarlos en el navegador (RF-06-AC-3, RF-09-AC-15, RF-12-AC-18…). |
| P-04 | La lógica de dominio no trivial tiene pruebas unitarias propias además de las de aceptación: agrupación (PS-01/PS-02), factores y reescalado del puntaje, transiciones de estado, reproyección y áreas. Componentes React con lógica tienen pruebas Vitest. | Los CA cubren ejemplos; las unitarias cubren bordes (300 m vs 500 m, d = 7 y d = 90 en recencia, puntaje 69/70). |
| P-05 | Cada CA marcado *(Prueba de aceptación manual.)* tiene evidencia en el issue: pasos seguidos, resultado y captura o video, con nombre de quien lo verificó. | No se automatizan (p. ej., RF-22-AC-3 en QField/Avenza), pero tampoco se dan por buenos sin evidencia. |
| P-06 | Si la HU agrega o modifica un endpoint: prueba de que **sin sesión responde 401** y de que **cada rol no autorizado según la matriz §2.3 responde 403**. | RNF-01 y RNF-02 aplican a todas las rutas; es la regla que más fácil se rompe al agregar un endpoint nuevo. |
| P-07 | Las pruebas geoespaciales corren contra **PostgreSQL 17 + PostGIS real** (contenedor de Docker), no contra SQLite ni *mocks* de geometría. Los datos de prueba son *fixtures* pequeños y versionados. | Distancias, áreas y SRC solo se pueden verificar con PostGIS; un *mock* daría falsos positivos. |
| P-08 | Toda la suite (backend y frontend) pasa en verde, incluidas las pruebas de historias anteriores (sin regresiones). Ninguna prueba se desactiva (`skip`) para poder fusionar. | Un incremento terminado no rompe lo que ya estaba terminado. |
| P-09 | Cobertura del código nuevo del backend ≥ 80 % (medida con `pytest-cov`), con excepción justificada en el PR. | Umbral orientativo para detectar ramas sin probar; no sustituye a P-02. Recomiendo medirlo sobre el código nuevo, no sobre el total, para no castigar el arranque. |

### 3.4 Revisión

| ID | Condición | Por qué |
|---|---|---|
| R-01 | El PR tiene al menos **una aprobación** de un integrante distinto del autor. | Cuatro ojos; también reparte el conocimiento del código (si alguien falta un sprint, otro conoce esa parte). |
| R-02 | Quien revisa recorre la lista de verificación de la plantilla del PR (sección 6), no solo el código. | Hace que la DoD se aplique de verdad y no de memoria. |
| R-03 | Todos los comentarios de la revisión están resueltos o convertidos en un issue nuevo enlazado. | Nada queda "para después" sin registrar. |
| R-04 | El Product Owner (o quien el equipo designe) validó el comportamiento con la aplicación corriendo, idealmente en la *Sprint Review*, y lo aceptó en el issue. | Verificar contra la intención del usuario, no solo contra la prueba que escribió el desarrollador. |

### 3.5 Reglas del dominio (verificación obligatoria en cada HU)

Estas reglas son transversales: cualquier historia puede violarlas sin darse cuenta. Por eso
forman parte de la DoD y no solo de los CA de un RF concreto.

| ID | Condición | Regla |
|---|---|---|
| D-01 | La HU **no introduce etiquetas, textos, campos ni colores que atribuyan una causa** (p. ej., "minería", "tala ilegal") ni determinen legalidad. Las hipótesis solo existen como "Marca del analista". | RD-02 |
| D-02 | Ninguna respuesta de la API, pantalla, exportación (CSV, GeoJSON, Shapefile, GeoPackage, KML) ni ficha PDF **contiene el nombre del titular** de un derecho minero; el campo ni siquiera se importa. | RD-04 |
| D-03 | La HU **no envía nada fuera del sistema** (correo, SMS, *webhooks*, llamadas a terceros) ni presenta resultados como alertas oficiales. Los avisos se muestran solo dentro de la interfaz. | RD-05 |
| D-04 | Los datos de fuentes oficiales no se modifican; todo resultado muestra fuente y fecha de corte. | RD-06, RNF-07 |
| D-05 | Cálculos de área y distancia en **EPSG:32719**; API del mapa y exportaciones GeoJSON/GeoPackage/KML en **EPSG:4326**; Shapefile en EPSG:32719. | RD-10 |
| D-06 | Los cálculos temporales usan la **fecha de detección** (no la de ingesta) y la fecha de referencia en America/Lima. | RD-08 |
| D-07 | Las marcas de confianza **nunca ocultan una zona ni cambian su puntaje**; los pesos **nunca se reajustan automáticamente**. | RD-03, RF-13 |
| D-08 | Ante datos faltantes o insuficientes, la HU muestra la situación ("No disponible", "Sin datos cargados", limitación conocida) y no presenta el resultado como concluido. | RNF-08, RD-09 |
| D-09 | Todo texto visible al usuario, mensaje de error y encabezado de exportación está **en español**. | RNF-06 |
| D-10 | Si la HU toca contraseñas o sesiones: almacenamiento con bcrypt/Argon2, mínimo 12 caracteres, nunca en logs. | RNF-03, PS-15 |

### 3.6 Documentación

| ID | Condición | Por qué |
|---|---|---|
| DOC-01 | Cada endpoint nuevo o modificado aparece en `openapi.yaml` con descripción en español, códigos de respuesta (incluidos 401/403/422) y la referencia a los `RF-XX-AC-Y` que implementa. | Exigencia de S04-A2; además el contrato es lo que consume el frontend. |
| DOC-02 | Si la HU cambia cómo se instala, despliega, cargan capas o ingieren alertas, el **manual en español** (README / `docs/`) está actualizado. | RNF-10: el sistema debe poder desplegarse desde cero siguiendo solo el manual. |
| DOC-03 | Variables de entorno nuevas documentadas en `.env.example` (sin valores reales). | Que cualquier integrante pueda levantar el entorno. |
| DOC-04 | Decisiones de diseño no obvias (p. ej., cómo se resuelve la zona más cercana en HU-E3-1) quedan en un comentario breve o en un registro de decisiones (ADR) de pocas líneas. | El "por qué" se olvida entre sprints; el "qué" ya lo dice el código. |
| DOC-05 | El issue de la HU en GitHub Projects tiene actualizados: estado, responsable, SP, sprint y enlace al PR. | El tablero es la fuente de verdad del avance para el equipo y el profesor. |

### 3.7 Integración y despliegue

| ID | Condición | Por qué |
|---|---|---|
| I-01 | El pipeline de **GitHub Actions** pasa en verde en el PR: Ruff, ESLint, `tsc`, pytest (con PostGIS como servicio), Vitest y construcción de imágenes. | Automatiza C-02, P-08 y I-02. Mientras el pipeline esté solo planeado, el autor ejecuta los mismos comandos localmente y pega el resultado en el PR (ver sección 5). |
| I-02 | `docker compose up` levanta el sistema completo desde cero (con migraciones aplicadas) y la funcionalidad de la HU funciona en ese entorno, no solo en la máquina del autor. | RNF-10 (despliegue con un comando) y evita el "en mi máquina funciona". |
| I-03 | La HU no agrega dependencias con licencia de pago ni servicios que superen el presupuesto del VPS (≤ USD 25/mes). Dependencias nuevas justificadas en el PR. | RNF-09. |
| I-04 | Las operaciones de carga, ingesta o comparación que toque la HU muestran resultado, estado de procesamiento o error en ≤ 60 s con el volumen de referencia (1,000 alertas / 300 zonas). | RNF-04 (PS-14); se verifica con un dato de prueba de ese tamaño al menos una vez por HU afectada. |
| I-05 | La rama de la HU está fusionada y eliminada; `main` queda desplegable al cierre de la HU. | El incremento siempre está en estado entregable. |

---

## 4. DoD a nivel de sprint (incremento)

Además de la DoD por historia, recomiendo una comprobación breve al cierre de cada sprint:

| ID | Condición |
|---|---|
| S-01 | Todas las HU marcadas Done cumplen la DoD; las que no, vuelven al backlog (no hay "casi terminadas"). |
| S-02 | `main` se despliega con Docker Compose en un entorno limpio (o en el VPS, cuando exista) y se hace la demostración de la *Sprint Review* sobre ese despliegue. |
| S-03 | Se genera un reporte de trazabilidad: lista de `RF-XX-AC-Y` del alcance del sprint con su prueba (`test_RF_XX_AC_Y`) en verde, su prueba E2E o su evidencia manual. Puede salir de `pytest --collect-only` + un script sencillo. |
| S-04 | Prueba de humo de seguridad: matriz rol × acción de §2.3 completa en verde (RNF-02). |
| S-05 | Se etiqueta la versión en Git (p. ej., `v0.2.0-sprint2`) y se registran en un `CHANGELOG` las HU entregadas. |
| S-06 | En la retrospectiva se revisa la DoD: qué punto costó más, cuál se saltó y si debe ajustarse. |

---

## 5. Recomendación de adopción gradual

La DoD de la sección 3 es la **ideal**. Con ~70 h por sprint, recomiendo aplicarla completa desde
el primer sprint en todo lo que es barato y crítico, y madurar el resto:

| Momento | Qué se exige | Qué se relaja temporalmente (y cómo se compensa) |
|---|---|---|
| **Sprint 1** (arranque: Docker Compose, esqueleto, HU-E1-1) | T-01–T-03, C-01–C-05, P-01, P-02, P-06, P-07, R-01, R-03, todas las D-xx, DOC-03, DOC-05, I-02. | I-01: sin pipeline aún → ejecución local con evidencia en el PR. P-03: sin E2E hasta tener interfaz → N/A. P-09: cobertura se mide pero no bloquea. DOC-01: el `openapi.yaml` generado por FastAPI basta hasta S04-A2. |
| **Desde que exista GitHub Actions** | I-01 bloqueante (protección de rama: no se fusiona con pipeline en rojo). | — |
| **Desde la primera pantalla real** | P-03 obligatorio para los CA marcados E2E. | — |
| **Desde el sprint 3** | P-09 bloqueante (≥ 80 % del código nuevo), I-04 con volumen de referencia, S-01–S-06 completos. | — |

Lo que **no recomiendo relajar nunca**: P-02 (pruebas nombradas por ID), P-06 (401/403 en el
servidor), las reglas de dominio D-01 a D-03 (causas, titulares, envío a terceros) y la revisión
por pares R-01. Son las que, si se rompen, invalidan el producto o la trazabilidad exigida por el
curso, y corregirlas después cuesta mucho más que cumplirlas desde el principio.

---

## 6. Lista de verificación para la plantilla de PR

Sugiero copiarla en `.github/pull_request_template.md` para que la DoD se revise en cada PR:

```markdown
## HU y criterios
- HU: #NN — Closes #NN
- Criterios implementados: RF-XX-AC-Y, RF-XX-AC-Z

## Definition of Done
### Trazabilidad
- [ ] Cada CA vinculado a su RF-XX-AC-Y; cambios al SRS registrados sin renumerar
### Código
- [ ] Ruff / ESLint / tsc sin errores
- [ ] Esquemas Pydantic v2; migración Alembic (upgrade/downgrade) si cambia la BD
- [ ] Sin secretos, sin código de depuración; parámetros PS-xx en configuración
### Pruebas
- [ ] test_RF_XX_AC_Y por cada CA de API; E2E por cada CA marcado E2E; evidencia de los manuales
- [ ] 401 sin sesión y 403 por rol no autorizado en endpoints nuevos
- [ ] Pruebas contra PostGIS real; suite completa en verde, sin skips; cobertura nuevo código ≥ 80 %
### Reglas de dominio
- [ ] Sin etiquetas causales ni de legalidad (RD-02)
- [ ] Sin nombre de titulares en API, UI ni exportaciones (RD-04)
- [ ] Nada se envía fuera del sistema (RD-05)
- [ ] EPSG correcto (32719 cálculo / 4326 API y exportaciones) (RD-10)
- [ ] Fecha de detección; datos faltantes mostrados, no ocultos (RD-08, RNF-08)
- [ ] Textos en español (RNF-06)
### Documentación
- [ ] openapi.yaml con referencias RF-XX-AC-Y; manual y .env.example actualizados si aplica
### Integración
- [ ] GitHub Actions en verde (o evidencia local mientras no exista)
- [ ] `docker compose up` desde cero funciona con esta HU
- [ ] Sin dependencias de pago

N/A (con motivo):
```

---

## 7. Observaciones sobre el backlog actual relacionadas con la DoD

Al cruzar el backlog con el SRS encontré puntos que conviene resolver para poder aplicar T-01 y
P-02 sin fricción:

1. **Los CA del backlog no llevan el ID del SRS.** Las HU usan CA1, CA2, CA3; las pruebas deben
   nombrarse `test_RF_XX_AC_Y`. Sugiero agregar en cada CA su ID (p. ej., HU-E1-1 CA2 →
   `RF-01-AC-?`) o una tabla de correspondencia HU → `RF-XX-AC-Y`.
2. **Las HU resumen solo 2–3 criterios por RF**, mientras que el SRS tiene bastantes más (p. ej.,
   RF-09 llega a AC-15, RF-12 a AC-18). La DoD (P-01) debería referirse a **todos** los
   `RF-XX-AC-Y` del RF que la HU implementa, no solo a los tres copiados en el backlog; si no, la
   HU puede quedar "Done" con criterios del SRS sin probar.
3. **HU que cubren varios RF** (HU-E4-2: RF-10 + RF-11; HU-E5-1: RF-14 + RF-15; HU-E5-2: RF-16 +
   RF-17 + RF-37) reciben 8 SP. Con la DoD completa (pruebas por cada AC, E2E, documentación),
   puede que no quepan en un sprint para una persona; conviene revisar si se dividen.
4. **HU-E5-2 mezcla prioridades:** RF-16/RF-17 son Must y RF-37 (Shapefile) es Should. Si la HU
   se declara Done con Shapefile pendiente, no cumple P-01; recomiendo separar el Shapefile en
   su propia HU.

Estas observaciones son sugerencias; no modifiqué el backlog.
