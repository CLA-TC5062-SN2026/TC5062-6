# Sprint Planning — Sprint 1 · EcoAlert Tambopata

> Equipo 6 — TC5062, Gpo 10 · S03-A2, Parte 1 · Planeación del 04/10/2026
> Facilitación simulada con un agente de IA en el rol de Scrum Master. Su propuesta original está
> en `borradores/propuesta_agente_sprint_goal.md`; la evaluación y los ajustes del equipo, en la
> sección 7. Tareas: `tareas_tecnicas.md`. Definition of Done: `definition_of_done.md`.

---

## 1. Datos del sprint

| | |
|---|---|
| **Sprint** | 1 de N |
| **Duración** | 2 semanas: lunes 05/10/2026 a domingo 18/10/2026 (10 días hábiles) |
| **Dedicación** | 8–9 h por semana por integrante |
| **Entradas** | `S03_A1/backlog_completo.md` (15 HU, 5 épicas, 113 SP); `S03_A1/priorizacion_comparada.md` (orden del PO en 4 bloques); `S03_A1/SRS_equipo.md` (línea base v1.0, criterios `RF-XX-AC-Y`); tablero "EcoAlert Tambopata — Product Backlog" (issues #1–#15) |
| **Punto de partida** | El repositorio no tiene código: no hay backend, frontend, base de datos, Docker Compose ni CI. No hay velocidad histórica. |

## 2. Roles del equipo

### 2.1 Roles de Scrum

| Rol | Quién | Responsabilidad en el Sprint 1 |
|---|---|---|
| **Product Owner** | Eduardo Sauza | Dueño del backlog y del orden por valor (ya lo ejerció en S03-A1). Responde las preguntas abiertas antes del día 2 (T-PO-01), acepta o rechaza las historias en la Review y decide qué recortar si se activa la contingencia (§5.3). |
| **Scrum Master** | Daniel Medina | Facilita los eventos, cuida que se cumpla la DoD (protección de `main`, plantilla de PR) y elimina bloqueos. Lleva el registro de horas reales para calibrar el Sprint 2. |
| **Developers** | Los cuatro integrantes | Se autoorganizan para cumplir el Sprint Goal. En un equipo de 4, el PO y el SM también desarrollan. |

### 2.2 Roles técnicos

| Rol técnico | Integrante principal | Apoyo |
|---|---|---|
| Backend dev | Miguel Arévalo (núcleo geoespacial) | Daniel Medina (modelos y endpoints) |
| Frontend dev | Anthony Gutarra | — |
| QA | Eduardo Sauza (pruebas automatizadas y datos) | Anthony Gutarra (pruebas manuales) |
| DevOps | Daniel Medina | — |

Los roles se asignaron según la fortaleza de cada quien y para que el revisor de un PR nunca sea
su autor (DoD R-1). Se revisan en la retrospectiva.

### 2.3 Eventos del sprint

| Evento | Cuándo | Duración |
|---|---|---|
| Sprint Planning | Lunes 05/10 (con base en este documento) | 1.5 h |
| Daily (asíncrona) | Lunes, miércoles y viernes en el canal del equipo: qué hice, qué haré, qué me bloquea | ≈ 15 min por semana |
| Punto de control | Lunes 12/10 (día 6) | Dentro de la Daily |
| Decisión de la meta extendida | Miércoles 14/10 (día 8) | Dentro de la Daily |
| Sprint Review | Viernes 16/10 (día 10) | 1 h |
| Retrospectiva | Viernes 16/10 | 0.75 h |
| Refinamiento del Sprint 2 | Viernes 16/10 | 0.5 h |

## 3. Cómo se hizo la planeación

1. Se entregó al agente el Product Backlog completo, el orden del PO y el SRS. Se le pidió
   proponer un Sprint Goal concreto, medible y alcanzable, la capacidad en SP y las historias con
   su justificación.
2. El equipo evaluó la propuesta: ¿es realista? ¿entrega valor? Ajustó el alcance (§7).
3. Con el alcance ajustado, un agente independiente descompuso las historias en tareas
   (`tareas_tecnicas.md`). Al hacerlo, mostró que el ajuste no cabía en la capacidad (§5.2).
4. El equipo decidió el alcance final con un plan de contingencia (§5.3).

---

## 4. Sprint Goal acordado

> **Al cierre del Sprint 1, un analista SIG puede, desde la interfaz web y sin escribir código,
> cargar las capas de referencia del ámbito (límite de la RN Tambopata, zona de amortiguamiento,
> ríos y catastro minero sin titulares) e ingerir de forma acumulativa un archivo de alertas de
> GeoBosques, y ver un resumen con las alertas nuevas, las ya existentes, las fuera del ámbito y
> las no presentes en la última carga. Todo corre sobre un entorno que se levanta con
> `docker compose up`.**

**Cómo se mide (el objetivo se cumple si todo esto es cierto el 16/10):**

1. Los **16 criterios comprometidos** (RF-03-AC-1 a AC-11 y RF-04-AC-1 a AC-5) tienen su prueba
   `test_RF_XX_AC_Y` y pasan contra PostgreSQL 17 + PostGIS.
2. `docker compose up` levanta la base de datos, la API y el frontend en una máquina limpia de un
   integrante distinto del que configuró el entorno.
3. En la Review, el PO, **sin usar `/docs` ni la terminal**:
   - carga el límite, la ZA, los ríos y el catastro reales;
   - ingiere el archivo de GeoBosques dos veces;
   - ve el resumen;
   - provoca un rechazo con un archivo inválido y lee el mensaje en español.

   Las capas se abren en QGIS para comprobar que están en EPSG:32719 y que ningún dato contiene
   titulares.
4. Ambas historias cumplen la Definition of Done, salvo las excepciones explícitas del Sprint 1
   (sin inicio de sesión, `definition_of_done.md` §3.3 P-6).

**Por qué es valioso aunque todavía no haya zonas ni prioridad:** todo lo que el PO puso arriba
(puntaje, lista priorizada, agrupación, comparación) se calcula **sobre estos datos**. El sprint
deja la materia prima en el sistema, cargada como la usará el analista (desde la interfaz, con
fuente y fecha de corte), con dos reglas de dominio críticas aseguradas desde el día uno:

- el ámbito se carga como dato (RD-01);
- nunca se importa un titular minero (RD-04).

---

## 5. Capacidad del equipo

### 5.1 Horas disponibles

| Concepto | Cálculo | Horas |
|---|---|---:|
| Capacidad bruta | 4 integrantes × 8–9 h/semana × 2 semanas | 64–72 |
| Eventos Scrum | ≈ 4 h por persona (§2.3) | − 16 |
| **Capacidad neta** | | **48–56** |

### 5.2 Story Points y conversión

| | Valor |
|---|---|
| **SP comprometidos** | **16 SP**: HU-E2-1 (8) + HU-E2-2 (8) |
| SP de la meta extendida | 3 SP: HU-E2-3 |
| Horas de las tareas comprometidas | 63.5 h: 14.5 de habilitación, 45 de las dos historias y 4 de cierre y PO |
| Horas por SP observadas | ≈ 2.8 h/SP (45 h ÷ 16 SP, sin contar la habilitación) |

El agente estimó primero una capacidad de **14–16 SP**, con el supuesto de 1 SP ≈ 1.8–2 h,
calibrado con HU-E2-3 como historia de referencia. Ese supuesto **no** incluía la interfaz, las
revisiones de PR, las pruebas manuales, el manual ni la demo, y todas esas tareas hacen falta
para cumplir la DoD. Al descomponer en tareas, la cifra real quedó en ≈ 2.8 h/SP. **Esta es la
primera lección del sprint:** sin velocidad histórica, la estimación en SP tiene que contrastarse
con las tareas.

Desde el Sprint 2 se planifica con la **velocidad real** del Sprint 1 (SP de historias que
cumplen la DoD), no con horas.

### 5.3 Decisión de alcance y plan de contingencia

Las tareas comprometidas (63.5 h) **superan la capacidad neta en 7.5 h** si todos dan 9 h/semana,
y en 15.5 h si dan 8 h/semana. El agente recomendó comprometer solo HU-E2-1 y dejar HU-E2-2 como
meta extendida. El equipo **decidió mantener ambas historias**, por tres motivos:

- HU-E2-2 es la primera historia del Bloque 1 del PO que se puede construir;
- buena parte de su costo ya está pagado por HU-E2-1, que comparte el lector, la validación y la
  pantalla;
- sin alertas ingeridas, el Sprint 2 no podría empezar por la agrupación en zonas (HU-E3-1).

Para que la decisión no sea solo optimismo, se acuerdan desde ahora estas condiciones:

1. **Cada integrante se compromete a 9 h/semana** durante este sprint: 56 h netas.
2. **Primero HU-E2-1, después HU-E2-2.** No se empieza la lógica de ingesta (T-E22-03 en
   adelante) hasta que el lector y el servicio de versiones (T-E21-05 a T-E21-07) estén
   fusionados. Una historia terminada vale más que dos a medias.
3. **Orden de recorte acordado de antemano.** Si el punto de control del día 6 (12/10) muestra
   atraso, el PO recorta en este orden sin replanificar:

   | Paso | Se recorta | Horas que libera | Efecto en el Sprint Goal |
   |---|---|---:|---|
   | 1 | HU-E2-3 (meta extendida) no se empieza | — | Ninguno |
   | 2 | Workflow de CI (T-HAB-07) → evidencia local en el PR (la DoD I-1 lo permite) | 2.5 | Ninguno |
   | 3 | Interfaz de alertas (T-E22-07, 08, 09, 11) → Sprint 2; la ingesta se demuestra por `/docs` | 4.5 | Parcial: la interfaz cubre solo las capas |
   | 4 | Si T-E21-08 (rutas de capas) no está fusionada el día 6, HU-E2-2 vuelve al Product Backlog | 16.5 | Se reduce a la carga de capas y se informa en la Review |

   Los pasos 2 y 3 liberan 7 h, casi toda la brecha de 7.5 h con 9 h/semana, antes de tener que
   sacar una historia.
4. **Registro de horas reales** por tarea (T-CIE-03), para que el Sprint 2 se planifique con
   datos y no con supuestos.

---

## 6. Sprint Backlog: historias seleccionadas

### 6.1 Resumen

| Orden | Issue | HU | SP | Bloque PO | Compromiso | Criterios comprometidos | Diferidos (sprint) |
|---|---|---|---:|---|---|---|---|
| 1 | #4 | **HU-E2-1** — Carga de capas de referencia (RF-03) | 8 | 2 | Comprometida, con interfaz | RF-03-AC-1 a AC-11 | RF-03-AC-12 (S2) |
| 2 | #5 | **HU-E2-2** — Ingesta acumulativa de alertas GeoBosques (RF-04) | 8 | 1 | Comprometida, con interfaz | RF-04-AC-1 a AC-5 (AC-4 parcial) | RF-04-AC-6, AC-7 (S2) |
| — | | **Total comprometido** | **16** | | | **16 criterios** | |
| 3 | #6 | HU-E2-3 — Frescura de fuentes visible (RF-07) | 3 | 2 | Meta extendida | RF-07-AC-1, 3 (parcial), 4, 5 | RF-07-AC-2 (con RF-10) |

La habilitación técnica (Docker Compose con PostGIS, esqueletos de FastAPI y React, CI mínimo,
14.5 h) no es una historia y no suma SP. Se registra como un issue propio en el tablero.

### 6.2 Justificación

**El orden del PO es por valor, pero las historias de más valor forman una cadena de
dependencias:**

```
HU-E2-1 Capas de referencia (el límite de la RN y la ZA definen el ámbito, RD-01)
   └─► HU-E2-2 Ingesta de alertas (descarta lo que está fuera del ámbito)
          └─► HU-E3-1 Agrupación en zonas (RF-04-AC-6: cada alerta en una zona)
                 └─► HU-E4-1 Puntaje explicado ─► HU-E4-2 Lista priorizada
                 └─► HU-E5-1 Comparación de periodos
```

No se pueden priorizar zonas sin agruparlas, ni agrupar sin alertas, ni filtrar las alertas "del
ámbito" sin el límite cargado como dato. El Sprint 1 empieza por la base de la cadena, y el
equipo respeta el orden del PO **dentro** de lo que las dependencias permiten.

- **HU-E2-1 (8 SP).** Sin el límite de la reserva y la ZA no hay ámbito. Sin ríos ni catastro no
  hay contexto territorial (RF-08), y faltarían dos de los cinco factores del puntaje (RF-09).
  Además, asegura desde el inicio que nunca se importe un titular (RD-04, RF-03-AC-9) y que toda
  capa tenga fuente y fecha de corte (RD-06). No depende de otras historias. Aunque es del
  Bloque 2, va primero porque es un prerrequisito técnico de HU-E2-2.
- **HU-E2-2 (8 SP).** Es la **primera historia del Bloque 1 que se puede construir**, y las tres
  anteriores del Bloque 1 (HU-E4-1, HU-E4-2, HU-E3-1) dependen de ella. Las alertas son la materia
  prima de zonas, puntaje y comparación. La ingesta acumulativa conserva el historial que
  necesitan la persistencia (RF-09) y la comparación (RF-14). Reutiliza el lector, la validación
  y la pantalla de HU-E2-1 (RF-04: "con la misma validación de formato y SRC que RF-03").
- **HU-E2-3 (3 SP, extendida).** Es barata porque solo lee las fechas de corte que las otras dos
  ya guardan, y protege contra interpretar datos viejos como actuales (RD-08). No se compromete
  porque la capacidad ya está superada. Se toma solo si ambas historias cumplen la DoD el día 8.

### 6.3 Criterios diferidos y parciales

Los IDs no cambian; solo se mueve el sprint en que se cumplen. Quedan anotados en los issues
(DoD S-4).

| Criterio | Motivo | Cómo queda en el Sprint 1 | Sprint |
|---|---|---|---|
| RF-03-AC-12, RF-04-AC-7 (403 a la coordinación) | No hay inicio de sesión ni roles (HU-E1-1). | Cada endpoint ya declara `require_role("analista")`. La API **no** se publica fuera de local y CI (RNF-01). | 2 |
| RF-04-AC-6 (cada alerta en una zona) | Requiere la agrupación (HU-E3-1). | La ingesta llama a un gancho vacío `agrupar_en_zonas`. | 2 |
| RF-04-AC-4, cláusula "sin salir de sus zonas" | Aún no hay zonas. | Se prueba el resto: 230 alertas, 30 nuevas, 150 existentes, 50 "no presentes", ninguna borrada. | 2 |
| RF-03-AC-10 y AC-11 ("los cálculos usan…") | El único cálculo que existe es el ámbito de la ingesta. | Se prueba `version_vigente` (mayor fecha de corte), que luego reutilizan RF-05, RF-08 y RF-09. | — |

### 6.4 Historias que quedan fuera, y por qué

| HU | Bloque PO | SP | Motivo |
|---|---|---:|---|
| HU-E4-1 Puntaje explicado | 1 | 13 | Calcula sobre zonas (HU-E3-1). Sus 13 SP solos casi igualan el sprint. |
| HU-E4-2 Lista priorizada | 1 | 8 | Ordena por el puntaje de HU-E4-1. |
| HU-E3-1 Agrupación en zonas | 1 | 13 | Necesita alertas ingeridas. 16 + 13 = 29 SP. Es la candidata principal del Sprint 2. |
| HU-E5-1 Comparación de periodos | 1 | 8 | Compara por zona y guarda el puntaje (depende de HU-E3-1 y HU-E4-1). |
| HU-E3-2 Mapa con capas | 2 | 8 | Necesita zonas que dibujar, y es la historia con más TypeScript, que el equipo maneja a nivel básico. |
| HU-E3-3 Contexto territorial | 2 | 5 | Cruza zonas con capas (depende de HU-E3-1). |
| HU-E4-3 Estados e historial | 2 | 8 | Opera sobre zonas. |
| HU-E1-1 Inicio de sesión | 3 | 5 | No bloquea el desarrollo local; sí bloquea cualquier despliegue (RNF-01). Va al Sprint 2 junto con los 403 diferidos. |
| HU-E5-2, HU-E1-2, HU-E1-3, HU-E5-3 | 3–4 | 26 | Menor valor según el PO, o dependen de zonas. |

---

## 7. Evaluación de la propuesta del agente

**¿Es realista?** En parte. La selección de historias y su orden eran correctos: el agente vio
la cadena de dependencias que el orden por valor del PO no muestra, y descartó con buenos
argumentos una "rebanada vertical" de 34 SP. Pero la cifra de capacidad (14–16 SP, ≈ 39.5 h de
tareas) era optimista, porque dejaba fuera trabajo que la DoD exige. La descomposición en tareas
lo corrigió (§5.2).

**¿Está enfocada en entregar valor?** No del todo. En la propuesta original, el analista cargaba
los datos a través de `/docs` de FastAPI y la demo se hacía en QGIS. El SRS define al analista
SIG como alguien que **no programa** (§2.3), y RNF-06 (Must) exige que las funciones se usen desde
la interfaz web sin escribir código. Un incremento que solo un desarrollador puede usar no entrega
valor al usuario, aunque pasen todas las pruebas de la API.

| # | Propuesta del agente | Ajuste del equipo | Motivo |
|---|---|---|---|
| 1 | Solo API; demo por `/docs` y QGIS. | **Se agrega una interfaz mínima** de carga de capas y alertas, con el resumen de la ingesta (sin mapa). El Sprint Goal se reescribió: "desde la interfaz web y sin escribir código". | RNF-06 y el perfil del analista (SRS §2.3). Es lo que convierte el sprint en valor para el usuario. |
| 2 | El Sprint Goal se medía con "16 criterios en verde **en CI**". | La medición no depende del CI: las pruebas pasan contra PostGIS, y el CI mínimo es una tarea más (T-HAB-07) que se puede recortar (§5.3). | El proyecto aún no tiene CI/CD completo. Si el CI falla por configuración, no debe arrastrar al objetivo de producto. |
| 3 | Capacidad de 14–16 SP con 1 SP ≈ 1.8–2 h. | Se mantiene el compromiso de 16 SP, pero con 63.5 h de tareas reales y un plan de contingencia (§5.3). | La descomposición mostró ≈ 2.8 h/SP al incluir la interfaz, las revisiones, las pruebas manuales y el manual. |
| 4 | Recomendación del segundo agente: comprometer solo HU-E2-1. | **No se aceptó.** Se mantienen ambas historias, con 9 h/semana, el orden HU-E2-1 → HU-E2-2 y un recorte acordado de antemano. | Ver §5.3. El riesgo se aceptó de forma explícita. |
| 5 | Responsables "Integrante 1–4". | Roles de Scrum y técnicos con nombre (§2). | La actividad pide definir los roles del equipo. Así, ningún PR lo revisa su autor. |
| 6 | Tareas sin dueño para las dudas del SRS. | Se agrega T-PO-01: el PO responde 6 preguntas abiertas antes del día 2. | Dos tareas de backend dependen de esas respuestas (`tareas_tecnicas.md` §8). |

---

## 8. Riesgos principales

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | **El compromiso supera la capacidad** (63.5 h frente a 48–56 h). | Alta | Alto | 9 h/semana, orden HU-E2-1 → HU-E2-2, punto de control el día 6 y orden de recorte acordado (§5.3). |
| R2 | La habilitación técnica (Docker con PostGIS, GDAL/PROJ en macOS arm64 y Windows) consume más de 14.5 h. | Alta | Alto | Backend y pruebas solo dentro de Docker; imagen oficial `postgis/postgis:17-3.5`; validar el arranque en las 4 máquinas la primera semana. |
| R3 | El formato real de GeoBosques o del catastro es distinto del supuesto. | Media | Alto | *Spike* T-E21-01 en los días 1–2; la asignación de columnas absorbe diferencias de nombres. |
| R4 | Backend como cuello de botella: ruta crítica de ≈ 23.5 h casi secuencial. | Media | Alto | Dos personas en backend; contrato de la API (T-E21-03) fusionado el día 3 para que el frontend avance con *mocks*. |
| R5 | Curva de aprendizaje de React con TypeScript. | Media | Medio | Pantalla dividida en tareas de 2 h (T-E21-11a/b); una sola pantalla reutilizada para capas y alertas. |
| R6 | API sin autenticación durante el sprint. | Baja | Alto | No publicarla fuera de local y CI (DoD §4); `require_role` desde el primer endpoint; HU-E1-1 en el Sprint 2. |
| R7 | El PO no responde a tiempo las preguntas abiertas. | Media | Medio | T-PO-01 con fecha límite el día 2; si no hay respuesta, se aplica la propuesta por defecto (`tareas_tecnicas.md` §8). |

## 9. Proyección (no es compromiso)

| Sprint | Candidatas | Comentario |
|---|---|---|
| 2 | HU-E3-1 (13) + HU-E1-1 (5) + criterios diferidos; HU-E2-3 si no se hizo | Cierra la cadena alertas → zonas y habilita el despliegue con sesión. Se ajusta con la velocidad real del Sprint 1. |
| 3 | HU-E4-1 (13) + HU-E1-2 | Primer puntaje explicado: el núcleo de valor del PO. |
| 4+ | HU-E4-2, HU-E3-2, HU-E3-3, HU-E4-3, HU-E5-1, HU-E5-2… | Según el orden del PO y la velocidad medida. |
