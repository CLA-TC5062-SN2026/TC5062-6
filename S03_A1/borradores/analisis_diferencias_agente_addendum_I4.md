# Addendum al análisis de diferencias: integración del SRS del Integrante 4 (I4)

> **Borrador generado por un agente** (analista de requerimientos) como insumo para el equipo.
> Complementa `borradores/analisis_diferencias_agente.md` (I1–I3, conflictos C-01 a C-17). **No
> modifica** `SRS_equipo.md` v1.0: las propuestas de la sección 5 deben revisarse críticamente,
> decidirse en equipo y registrarse en `diferencias_SRS.md` antes de aplicarse.

**Insumos**

| Prefijo | Archivo | Uso |
|---|---|---|
| I4 | `insumos/SRS_integrante4.md` (versión "Final (con ajustes de revisión)", 2026-09-27) | SRS nuevo, leído completo |
| I1, I2, I3 | `insumos/SRS_integrante1_A01840503.md`, `SRS_integrante2.md`, `SRS_integrante3.md` | Verificación puntual |
| Equipo | `SRS_equipo.md` v1.0 y `diferencias_SRS.md` | Decisiones ya tomadas |
| Base | `insumos/proyecto_base.md` | Alcance acordado (B1–B4, como en el análisis previo) |

**Convención.** Igual que en el análisis previo: comparación **por contenido**; los IDs individuales
llevan prefijo (`I4:RF-06-AC-1`, `I1:RF-33`) y los del SRS de equipo van **sin prefijo** (`RF-09`).
Los IDs de I4 chocan con los del equipo (p. ej., `I4:RF-09` es "notificar alta prioridad" y `RF-09`
es "priorización explicada").

---

## 1. Resumen de I4

| Aspecto | Contenido |
|---|---|
| Alcance | Plataforma web para la **RN Tambopata y su ZA** (`I4:§1.2`, `I4:RD-01`). Integra información satelital y geoespacial "de múltiples fuentes" (`I4:RF-01`), compara imágenes de dos periodos (`I4:RF-02`), muestra ubicación, extensión (ha) y fechas de cada "cambio" (`I4:RF-03`), contexto territorial con reserva, ZA, **comunidades** y concesiones (`I4:RF-04`), **observaciones** libres (`I4:RF-05`), **clasificación manual** de prioridad alta/media/baja (`I4:RF-06`), historial (`I4:RF-07`), **filtros y orden por 5 criterios** (`I4:RF-08`), **notificación interna** de alta prioridad (`I4:RF-09`), vista de pendientes (`I4:RF-10`), estados ligados a **asignación** (`I4:RF-11`), usuarios y roles (`I4:RF-12`) y exportación **PDF/Shapefile/GeoJSON** (`I4:RF-13`). Fuera: causas, decisiones de fiscalización, análisis predictivo (`I4:§1.2`). |
| Entidad central | El **"cambio detectado"**, persistente, con historial propio (`I4:RF-07`). No define cómo se crea un cambio: no dice de qué fuente sale ni si se agrupa (igual que I3, ver C-06). Usa "zona" como sinónimo en `I4:RNF-01` y `I4:RD-03`. |
| Roles | **Tres**: Analista (consulta, compara, evalúa, documenta, clasifica), **Especialista** (revisa cambios asignados, observa, finaliza) y **Coordinador** (usuarios, **asigna cambios a especialistas**, supervisa) (`I4:RF-12`). En `I4:§2.3` los perfiles se llaman "Analista Ambiental", "Especialista SIG" y "Coordinador de Monitoreo", y el coordinador hace "gestión de prioridades". |
| Cantidades | **13 RF**, **4 RNF**, **3 RD**, **23 AC** (RF-01 2, RF-02 2, RF-03 1, RF-04 2, RF-05 1, RF-06 1, RF-07 2, RF-08 2, RF-09 2, RF-10 2, RF-11 2, RF-12 2, RF-13 2). Sin MoSCoW, sin trazabilidad a una fuente de elicitación, sin parámetros. Los RNF tienen "criterios de verificación" en texto, no AC. |
| Formato de AC | Given-When-Then ("Dado que / cuando / entonces") con **ID `RF-XX-AC-Y`** y un comportamiento por criterio en la mayoría. Pocos valores concretos (sin datos de prueba, umbrales ni tolerancias) y sin tipo de verificación (API / E2E / manual). |
| ¿Respeta la base? | **Sí en B1, B2 y B4**: Tambopata + ZA (`I4:RD-01`), analistas y especialistas SIG (`I4:§2.3`), sin causas y decisión humana (`I4:§2.4`, `I4:RD-02`, `I4:RD-03`). **Parcialmente en B3**: compara periodos y contextualiza, pero la priorización es **solo manual** (`I4:RF-06`); el sistema no "ayuda a identificar qué zonas requieren revisión prioritaria", solo registra lo que el usuario decide. Menciona fuentes "públicas **y privadas**" (`I4:§2.1`), que la base no menciona. |

---

## 2. Qué cambia en el consenso con cuatro SRS

### 2.1 Temas que pasan a consenso 4/4

| Tema | Antes | I4 | En el SRS de equipo |
|---|---|---|---|
| Aplicación web usable sin programar | 3/3 | `I4:RNF-02` | RNF-06 (se refuerza; ver C-27 para la métrica de 2 h) |
| Comparación de dos periodos | 3/3 | `I4:RF-02` | RF-14 (datos), RF-18 (imágenes, Should; ver C-29) |
| Visualización en mapa | 3/3 | `I4:RF-01-AC-1` ("mapa interactivo"), `I4:RF-04-AC-1` | RF-06 |
| Contexto territorial respecto del área protegida | 3/3 | `I4:RF-04` | RF-08 |
| Estado de revisión e historial | 3/3 | `I4:RF-07`, `I4:RF-11` | RF-12 |
| La decisión final es humana | 3/3 | `I4:§2.1`, `I4:§2.4`, `I4:RD-02`, `I4:RD-03` | §1.2, RD-03 |
| Acceso restringido | 3/3 | `I4:RNF-04`, `I4:RF-12-AC-2` | RF-01, RNF-01 |
| Ver ubicación, extensión (ha) y fechas del cambio | I1, I2, I3 (implícito) | `I4:RF-03-AC-1` | RF-05, RF-06, RF-10, RF-14 |

Los temas de consenso 3/3 que I4 **no** trata siguen en 3/4: fuentes caídas o desactualizadas
(RF-07, RNF-08), calidad de la evidencia (RD-09), incertidumbre visible (RF-13), persistencia como
criterio (RF-09) y trazabilidad de fuentes y periodos (RNF-07). I4 no los contradice.

### 2.2 Temas que pasan a 3/4 (antes 2/3)

| Tema | Ahora presente en | Falta | Efecto en el equipo |
|---|---|---|---|
| Niveles alta / media / baja | I1 (derivado), I3, I4 (`I4:RF-06`, `I4:RD-03`) | I2 | Refuerza PS-04 y el nivel como forma de comunicar la prioridad. |
| Lista ordenable por prioridad | I1, I3, I4 (`I4:RF-08-AC-2`, `I4:RF-10-AC-2`) | I2 | Refuerza RF-10. |
| Roles diferenciados con permisos | I1, I2, I4 (`I4:RF-12`, `I4:RNF-04`) | I3 | Refuerza RNF-02; ver C-19 sobre cuáles. |
| Gestión de usuarios por un rol distinto del operativo | I1 (coordinación), I2 (admin. institucional), I4 (coordinador) | I3 | Refuerza RF-02 y la decisión de C-04 de dejarla en Coordinación. |
| Exportación de resultados | I1, I2, I4 (`I4:RF-13`) | I3 | Refuerza RF-16/RF-17. |
| Exportación GeoJSON | I1, I2, I4 | I3 | Refuerza RF-17 (Must). |
| Exportación **Shapefile** | I1, I2, I4 | I3 | **La decisión C-13 (Shapefile en Could, RF-32) queda en minoría.** Ver C-23. |
| Reporte **PDF** | I1 (ficha), I2 ("reporte"), I4 (`I4:RF-13-AC-1`) | I3 | RF-23 (Should) queda respaldado por 3/4; ver C-23. |
| Cruce con concesiones | I1, I2, I4 (`I4:RF-04-AC-1`) | I3 | **Refuerza C-02** (incluir el catastro). |
| Ámbito Tambopata + ZA | I1, I3, I4 (`I4:RD-01`) | I2 | **Refuerza C-03.** |
| Prohibición de atribuir causas | I1, I3, I4 (`I4:RD-02`, `I4:§2.4`) | I2 (lo contradice) | **Refuerza C-01.** |
| Comparación de **imágenes** lado a lado | I1, I2, I4 (`I4:RF-02-AC-1`, `I4:RF-02-AC-2`) | I3 (solo periodos, sin método) | RF-18 está en Should; ver C-29. |
| Unidad temporal "periodo" | I2, I3, I4 (`I4:RF-02`) | I1 (fechas) | **Refuerza C-16.** |
| Unidad de revisión persistente con historial propio | I1 (zona), I4 (cambio, `I4:RF-07`) e I2 (zona monitoreada) | I3 (zona dentro del análisis) | **Refuerza C-05.** |
| Estado inicial + "en revisión" + "terminado" | I1, I3, I4 (I2 tiene inicial y "en revisión", pero "confirmada" en lugar de terminado) | — | Refuerza RF-12 (nueva, en revisión, revisada). |
| Tabla cerrada de transiciones | I1, I4 (`I4:RF-11`, "Transiciones permitidas") | I3 (libres), I2 (no dice) | Refuerza C-07 (tabla cerrada). |

### 2.3 Temas que siguen minoritarios o que I4 vuelve 2/4

| Tema | Presente en | Comentario |
|---|---|---|
| Prioridad **calculada** por el sistema | I1, I3 | **I4 solo prioriza a mano** (`I4:RF-06`). Sigue 2/4, pero la base (B3) la respalda. Ver C-18. |
| Ajuste manual **con justificación obligatoria** | I1, I3 | I4 permite reclasificar "en cualquier momento" sin justificación (`I4:RF-06-AC-1`). 2/4 + base B4 (trazabilidad de la decisión). |
| Ajuste manual expresado como **nivel** | I3 (`I3:RF-08`), I4 (`I4:RF-06`) | **La decisión de RF-11 (ajuste como puntaje 0–100) solo está en I1**: queda en minoría 1/4 frente a 2/4 que ajustan el nivel. Ver C-18. |
| Escala 0–100 | I1 | Sigue 1/4; el nivel derivado lo hace compatible con I3 e I4. |
| Exactamente dos roles | I1 | I2 e I4 tienen tres (distintos); I3 uno. **La decisión C-04 sigue siendo la única con sustento en la elicitación de usuario real del dominio**, pero en número de roles es minoritaria. Ver C-19. |
| Rol de coordinación | I1, I4 | Pasa a 2/4: **refuerza C-04** en la existencia del rol, pero I4 le da permisos de escritura que el equipo le niega (asignar, "gestión de prioridades"). |
| Capa de **comunidades nativas** | I1 (`I1:RF-01`, `I1:RF-10-AC-2`), I4 (`I4:RF-04-AC-1`) | Pasa a 2/4; el equipo la había dejado fuera de RF-03/RF-06/RF-08. Ver C-25. |
| Filtro por **fecha** | I1 (`I1:RF-12-AC-8`, periodo), I4 (`I4:RF-08-AC-1`) | Pasa a 2/4; RF-10 solo filtra por nivel y estado. Ver C-24. |
| Avisos **internos** al usuario | I1 (`I1:RF-29-AC-3`, `I1:RF-04`), I2 (`I2:RF-11`), I4 (`I4:RF-09`) | Avisos dentro de la app: 3/4 (I3 excluye "notificaciones automáticas" sin precisar). Ver C-21. |
| Observaciones libres sobre la unidad de revisión | I3 (observación opcional al guardar la revisión, `I3:RF-09-AC-3`), I4 (`I4:RF-05`) | 2/4; en el equipo solo hay comentarios ligados a una transición (RF-12) y marcas (RF-13). Ver §3. |
| Registro de accesos y acciones sensibles | I1 (`I1:RNF-04`), I4 (`I4:RNF-04`, criterio de verificación) | 2/4; RF-24 (bitácora) está en Should. Sin cambio propuesto, pero refuerza RF-24. |
| Asignación de cambios a una persona | **Solo I4** | Gap; ver §3 y C-20. |
| Métrica de capacitación (2 h), legibilidad por escala, concurrencia | **Solo I4** | Gaps de RNF; ver C-26 a C-28. |

### 2.4 Estado de las decisiones C-01 a C-17

| Decisión | Efecto de I4 |
|---|---|
| C-01 (sin causas) | **Se refuerza** (3/4; solo I2 en contra). |
| C-02 (catastro como superposición factual, sin titular) | **Se refuerza** la inclusión (3/4). I4 no protege el titular y pide "datos disponibles" de cada capa (`I4:RF-04-AC-2`): ver C-25. |
| C-03 (Tambopata + ZA) | **Se refuerza** (3/4). |
| C-04 (Analista SIG + Coordinación) | **Se refuerza parcialmente** (coordinación 2/4) pero **el número de roles y los permisos de la coordinación quedan discutidos** (C-19). |
| C-05 (zona persistente + análisis inmutable) | **Se refuerza** (unidad persistente con historial). |
| C-06 (alertas oficiales) | Sin cambio: I4 tampoco especifica el origen. |
| C-07 (5 estados, tabla cerrada) | **Se refuerza** en la tabla cerrada; I4 no tiene "descartada" ni "requiere verificación" y añade la vuelta a "Pendiente" por desasignación (C-20). |
| C-08a (0–100 con nivel derivado) | Compatible en el nivel; **la priorización calculada sigue en 2/4** (C-18). |
| C-08b/c/d | I4 no los trata. |
| C-09 (sin offline) | I4 no lo trata. |
| C-10 (notificación = externa) | **I4 usa "notificación" para un aviso interno** (`I4:RF-09-AC-1`): compatible en el fondo, opuesto en el término (C-21). |
| C-11 (contraseña Must, TOTP Should) | Compatible; I4 no pide 2FA. El envío de credenciales es otro tema (C-22). |
| C-12 | I4 no lo trata. |
| C-13 (Must: CSV + GeoJSON; Shapefile Could) | **Shapefile queda en minoría** (3/4 lo piden) (C-23). |
| C-14 (guardado automático y compartido) | **Se refuerza**: observaciones e historial visibles a todos los usuarios autorizados (`I4:RF-05-AC-1`, `I4:RF-07-AC-2`). |
| C-15, C-17 | I4 no los trata. |
| C-16 (periodos) | **Se refuerza** (3/4). |

---

## 3. Gaps de I4 (lo que solo I4 aporta o que I4 vuelve relevante)

| Tema | IDs I4 | ¿Incorporar? | MoSCoW sugerido | Dónde encaja |
|---|---|---|---|---|
| Observaciones libres sobre la zona, con autor y fecha, visibles para todos, independientes de un cambio de estado | `I4:RF-05-AC-1` (parcial en `I3:RF-09-AC-3`) | **Sí.** Hoy una nota exige cambiar de estado o usar una "marca del analista", que tiene otro significado (advertencia o hipótesis). Costo bajo. | Should | **RF nuevo RF-34** "Observaciones de la zona"; aparecen en el historial (RF-12) y, si existe, en la ficha (RF-23). |
| Capa de comunidades nativas en el mapa y en el contexto | `I4:RF-04-AC-1` (también `I1:RF-10-AC-2`) | **Sí, como Should.** Contexto relevante en Tambopata; sin fuente oficial confirmada (I1 propone BDPI del Ministerio de Cultura, a confirmar). | Should | **RF nuevo RF-35**, que al implementarse amplía la tabla de RF-03, la lista de RF-06 y las superposiciones de RF-08 (mismo patrón que RF-20 respecto de RF-05). |
| Filtros por fecha, extensión y ubicación | `I4:RF-08-AC-1` | **Parcial.** Fecha (rango de la alerta más reciente) y extensión (área mín./máx.) son baratos y verificables. "Ubicación" debe definirse: dentro de la reserva / en la ZA (dato ya calculado para el factor de ubicación de RF-09). | Should | **RF nuevo RF-36** "Filtros y orden adicionales de la lista". |
| Orden por cualquier criterio, ascendente o descendente | `I4:RF-08-AC-2` | **Parcial.** Orden por fecha, área, puntaje y estado; "ubicación" no tiene orden natural. El orden por defecto de RF-10 no cambia. | Should | RF-36. |
| Vista de pendientes de revisión | `I4:RF-10-AC-1` | **Ya cubierto** por el filtro de estado de RF-10 ("nueva"). No requiere RF. | — | RF-10-AC-6 (filtro de estado). |
| Distinción visual de la prioridad alta | `I4:RF-10-AC-2` | **Ya cubierto** en el mapa (RF-06-AC-4). En la lista solo se exige mostrar el nivel (RF-10); se puede añadir un AC E2E. | Must (AC en RF existente) | RF-10, AC nuevo. |
| Aviso interno a los analistas cuando una zona pasa a nivel alto | `I4:RF-09` | **Sí, como aviso dentro de la interfaz**, no como "notificación" (glosario §1.3). | Could | **RF-29** (zonas nuevas desde la última revisión): añadir el evento "pasó a nivel alta" (ver C-21). |
| Historial cronológico único con todas las acciones (creación, observación, clasificación, estado) | `I4:RF-07-AC-1`, `I4:RF-07-AC-2` | **Sí.** El equipo registra estados (RF-12), ajustes (RF-11) y marcas (RF-13) pero ningún AC exige la **creación** de la zona en el historial ni una vista cronológica unificada. | Must (AC en RF existente) | RF-12, AC nuevos. |
| Comparación de imágenes con la misma extensión y escala | `I4:RF-02-AC-2` | **Sí.** RF-18 dice "zoom y desplazamiento sincronizados" pero no tiene AC para ello. | Should (AC en RF existente) | RF-18, AC nuevo. |
| Asignación de una zona a un responsable | `I4:RF-11`, `I4:RF-12` | **Opcional**, desacoplada del estado (ver C-20). Con 2–3 usuarios (perfil de I1) aporta poco. | Could | **RF nuevo RF-39** "Responsable de la zona". |
| Selección manual de zonas para exportar | `I4:RF-13-AC-1`, `I4:RF-13-AC-2` | **Opcional.** La lista filtrada y la búsqueda por código ya permiten acotar. | Could | **RF nuevo RF-38**. |
| Reporte PDF de **varios** cambios con mapa, datos y observaciones | `I4:RF-13-AC-1` | **No en esta versión.** RF-23 (ficha por zona) cubre el caso principal; un reporte multizona multiplica la plantilla. | Won't (v1) | Lista Won't de §1.2. |
| Métrica de facilidad de aprendizaje (≤ 2 h de capacitación) | `I4:RNF-02` | **Sí**, reformulada con tareas y criterio de éxito. | Should | **RNF nuevo RNF-14** (ver C-27). |
| Legibilidad del mapa entre 1:10,000 y 1:50,000 | `I4:RNF-03` | **Sí**, con criterio verificable. | Should | **RNF nuevo RNF-15** (ver C-28). |
| Concurrencia (20 usuarios) y volumen (500 cambios) | `I4:RNF-01` | **Parcial** (ver C-26). | Should | RNF-05 (cambio de condiciones de prueba). |
| Envío de credenciales al usuario nuevo | `I4:RF-12-AC-1` | **No** (ver C-22). | Won't | — |

---

## 4. Conflictos nuevos (C-18 en adelante)

### C-18 — Prioridad manual (I4) frente a prioridad calculada con ajuste justificado (equipo)

- **Descripción.** En I4 la prioridad es un atributo que el usuario **asigna** (alta/media/baja) y
  puede **reclasificar en cualquier momento**, con fecha y autor y **sin justificación**. No hay
  cálculo, factores ni desglose. El equipo calcula un puntaje 0–100 con 5 factores, deriva el
  nivel y permite un **puntaje ajustado** con justificación obligatoria.
- **Posiciones.**
  - I4: `I4:RF-06`, `I4:RF-06-AC-1`, `I4:RD-03` ("niveles alta, media y baja"), `I4:§2.3` (el coordinador hace "gestión de prioridades").
  - Equipo: RF-09 (cálculo y desglose), RF-10 (orden por puntaje vigente), RF-11 (ajuste 0–100, justificación obligatoria, RF-11-AC-2, RF-11-AC-3 rechaza "alto"), RD-03.
  - Otros: I1 (`I1:RF-33`, `I1:RF-34`, puntaje) e I3 (`I3:RF-06`–`I3:RF-08`: prioridad sugerida por nivel, **ajuste por nivel** con justificación).
- **Impacto.** Alto. Es el valor principal de la base (B3: "ayude al usuario a identificar qué
  zonas requieren una revisión prioritaria"). Una prioridad solo manual no ayuda a identificar
  nada: el analista tendría que revisar todo para clasificarlo. Además, sin justificación, el
  historial no explica por qué cambió la prioridad. Hay un punto donde I4 **sí** mueve el
  consenso: **I3 e I4 expresan la decisión humana como nivel**, y el ajuste por puntaje de RF-11
  solo está en I1 (`RF-11-AC-3` rechaza explícitamente el valor "alto").
- **Opciones.**
  1. Mantener RF-09 y RF-11 sin cambios (puntaje ajustado 0–100 con justificación).
  2. Mantener RF-09 y permitir **ajuste por nivel o por puntaje**: si el analista elige un nivel,
     el puntaje vigente es el límite inferior del nivel (alta = 70, media = 40, baja = 0) salvo que
     el calculado ya esté dentro de ese nivel; justificación obligatoria en ambos casos.
  3. Adoptar I4: prioridad solo manual por nivel, sin cálculo.
- **Recomendación: 1, registrando la opción 2 como alternativa para la ratificación.** La opción 3
  contradice B3 y deja sin uso los factores que I1 e I3 acordaron. El ajuste por puntaje conserva
  un orden total y verificable en la lista (RF-10); un ajuste por nivel obliga a inventar un puntaje
  (opción 2) o a romper el orden dentro del nivel. La justificación obligatoria se mantiene: I1 e
  I3 la exigen y es lo que hace auditable la decisión del especialista (B4). Para atender la
  forma de trabajo de I3 e I4 basta con que la interfaz muestre el nivel resultante al escribir el
  puntaje (ya implícito en RF-11-AC-1). Si el equipo elige la opción 2, hay que **retirar**
  RF-11-AC-3 en su parte "alto" y agregar criterios nuevos (no reescribir el existente).

### C-19 — Roles: Especialista separado y Coordinador con permisos de escritura

- **Descripción.** I4 define tres roles: Analista (clasifica), **Especialista** (revisa lo
  asignado, finaliza evaluaciones) y **Coordinador** (usuarios, **asigna cambios**, supervisa y, en
  §2.3, "gestión de prioridades"). El equipo tiene dos roles sin herencia: Analista SIG (todo lo
  operativo) y Coordinación (consulta, compara periodos, usuarios; **no** cambia estados ni
  prioridades, **no** exporta).
- **Posiciones.** I4: `I4:§2.3`, `I4:RF-12` (roles definidos), `I4:RF-11` (el especialista se
  asigna y finaliza), `I4:RF-09-AC-1` (notifica al "rol de especialista"), `I4:RNF-04`. Equipo:
  §2.3 (matriz), RF-02, RF-11-AC-7, RF-12-AC-16, RNF-02, decisión C-04.
- **Impacto.** Alto en la API y las pruebas (cada rol multiplica casos de 403). Separar
  Analista y Especialista divide entre dos roles el trabajo que la base atribuye a un mismo
  perfil ("analistas ambientales y especialistas SIG", B2). Además I4 es **internamente
  inconsistente**: el Analista "clasifica" pero solo el Especialista "finaliza"; `I4:RF-11-AC-1`
  dice que el especialista **se asigna** mientras `I4:RF-12` dice que **el coordinador asigna**; y
  los nombres de §2.3 ("Especialista SIG") y de RF-12 ("Especialista") no coinciden.
- **Opciones.**
  1. Mantener los dos roles del equipo (C-04).
  2. Dos roles, pero permitir a la coordinación **asignar responsables** (si se adopta RF-39), sin
     cambiar estados ni prioridades.
  3. Adoptar los tres roles de I4.
- **Recomendación: 1, con la opción 2 solo si el equipo adopta RF-39.** La base no distingue
  analista y especialista como roles con permisos distintos; I1 (único con elicitación del
  perfil) los une en "Analista SIG". La "gestión de prioridades" por parte de la coordinación
  contradice C-04 y RF-11-AC-7: quien no es SIG no debería fijar la prioridad de una zona. Asignar
  trabajo, en cambio, es una tarea de supervisión que no altera datos analíticos, por lo que la
  opción 2 es compatible con el espíritu de C-04.

### C-20 — Estados ligados a la asignación (Pendiente / En revisión / Completado) y desasignación

- **Descripción.** En I4 el estado depende de la asignación: "Pendiente" = sin especialista
  asignado; "En revisión" = especialista asignado; "Completado" = evaluación finalizada; y
  "En revisión → Pendiente" al **desasignar**. No hay "descartada" (aunque el glosario define
  "falso positivo"), ni "requiere verificación", ni reapertura desde "Completado".
- **Posiciones.** I4: `I4:RF-11` (estados y transiciones), `I4:RF-11-AC-1`, `I4:RF-11-AC-2`,
  `I4:§1.3` ("Falso positivo"). Equipo: RF-12 (5 estados, tabla cerrada, motivo obligatorio al
  descartar y reabrir), RD-11, decisión C-07.
- **Impacto.** Medio-alto. Equivalencias directas: Pendiente → "nueva", En revisión → "en
  revisión", Completado → "revisada" (I4 lo define como "finalizado la evaluación", compatible con
  RD-11). Lo que **no** encaja: (a) que la asignación cambie el estado; (b) la vuelta a
  "Pendiente", que el equipo no tiene (RF-12 no permite "en revisión → nueva"); (c) la ausencia de
  "descartada", necesaria para registrar falsos positivos, que el propio I4 define; (d) "Completado"
  como estado final sin reapertura, que contradice RF-12 y RF-20.
- **Opciones.**
  1. Mantener RF-12 sin cambios y, si se quiere asignación, tratarla como **atributo
     independiente** del estado (RF-39, Could).
  2. Agregar a RF-12 la transición "en revisión → nueva" con motivo obligatorio.
  3. Adoptar la máquina de estados de I4.
- **Recomendación: 1.** El estado describe el avance de la revisión, no quién la tiene; ligarlos
  obliga a asignar para empezar a revisar, lo que con dos analistas es burocracia. La vuelta a
  "nueva" (opción 2) no aporta información que no dé el historial y abre un ciclo nueva ↔ en
  revisión sin significado analítico; si el equipo la quiere, es un AC nuevo en RF-12 con motivo
  obligatorio, no un cambio de los existentes. "Descartada" y "requiere verificación" deben
  quedarse: cubren el falso positivo (que I4 nombra) y la incertidumbre (I1, I3).

### C-21 — "Notificación" interna de alta prioridad

- **Descripción.** I4 genera una **notificación interna** para todos los especialistas cuando un
  cambio se clasifica como de alta prioridad. El equipo define "notificación" como mensaje
  **externo** (correo, SMS, push), fuera de alcance, y permite avisos dentro de la interfaz (§1.3,
  RD-05, decisión C-10).
- **Posiciones.** I4: `I4:RF-09`, `I4:RF-09-AC-1`, `I4:RF-09-AC-2`, `I4:§1.2` ("Notificación a
  especialistas"). Equipo: §1.3, RD-05, RF-07 (aviso de frescura), RF-29 (Could, "nueva desde tu
  última revisión"). Otros: I1 (`I1:RF-29-AC-3`, notificación en la app), I3 (`I3:§1.2`, fuera
  "notificaciones automáticas").
- **Impacto.** Bajo-medio. En el fondo **no hay contradicción**: el mecanismo de I4 es interno. El
  problema es el **término** (choca con el glosario) y el **disparador**: en I4 la alta prioridad
  la fija una persona (`I4:RF-06`); en el equipo la calcula el sistema y puede cambiar a diario
  (RF-09: recálculo diario), lo que generaría avisos repetidos si una zona oscila alrededor de 70.
  Además, la descripción de `I4:RF-09` dice "cuando se **detecte** un nuevo cambio" y el AC dice
  "cuando se **guarda** la clasificación": son dos disparadores distintos.
- **Opciones.**
  1. Incorporar el aviso como evento de **RF-29** (Could): la zona que pasa a nivel "alta" queda
     marcada "nueva desde tu última revisión" para cada analista, una sola vez por cruce de umbral.
  2. RF nuevo con bandeja de avisos interna (lista, leídos/no leídos).
  3. No incorporarlo.
- **Recomendación: 1.** Reutiliza un mecanismo ya especificado, no requiere bandeja ni estado de
  lectura y respeta el glosario (es un **indicador**, no una notificación). Si el equipo quiere el
  aviso en el núcleo, la vía es subir RF-29 a Should, no crear un sistema de mensajería.

### C-22 — Envío de credenciales al crear un usuario

- **Descripción.** En I4, al registrar un usuario, "el sistema crea la cuenta y **envía las
  credenciales** al nuevo usuario". En el equipo la coordinación define una contraseña temporal de
  al menos 12 caracteres y el usuario debe cambiarla en el primer ingreso; el sistema no envía
  nada.
- **Posiciones.** I4: `I4:RF-12-AC-1`. Equipo: RF-02, RF-02-AC-1, RF-02-AC-4, RNF-03 (contraseñas
  nunca en texto plano), §1.2 (notificaciones externas fuera), RD-05. I1: `I1:RF-28-AC-1` (igual
  que el equipo).
- **Impacto.** Medio. Enviar credenciales implica un canal externo (correo) que el equipo dejó
  fuera, un servidor SMTP en el VPS y, si se envía la contraseña, una contraseña en texto plano en
  tránsito y en el buzón, contra RNF-03. El canal ni siquiera está definido en I4.
- **Opciones.**
  1. Mantener RF-02: contraseña temporal entregada por la coordinación fuera del sistema y cambio
     obligatorio en el primer ingreso.
  2. Correo de invitación con enlace de un solo uso y expiración (sin enviar la contraseña).
  3. Adoptar I4 tal cual.
- **Recomendación: 1.** La opción 2 es la forma segura de "enviar credenciales", pero introduce
  correo saliente, que el equipo excluyó; con tres usuarios no compensa. La opción 3 se descarta por
  seguridad. Registrar la opción 2 como mejora futura si el número de usuarios crece.

### C-23 — Exportaciones: PDF, Shapefile, GeoJSON y selección de cambios

- **Descripción.** I4 exporta los cambios **seleccionados** a PDF (mapa, datos y observaciones), a
  Shapefile y a GeoJSON. El equipo exporta la **lista filtrada** a CSV y GeoJSON (Must), la ficha
  PDF **por zona** (RF-23, Should) y el Shapefile como Could (RF-32).
- **Posiciones.** I4: `I4:RF-13`, `I4:RF-13-AC-1`, `I4:RF-13-AC-2`. Equipo: RF-16, RF-17, RF-23,
  RF-32 (Shapefile, Could), RD-10, decisión C-13. Otros: Shapefile en `I1:RF-18` e `I2:RF-07`; PDF
  en `I1:RF-17` e `I2:RF-07` ("reporte").
- **Impacto.** Medio.
  - **Shapefile:** con I4 lo piden **3 de 4** SRS y el equipo lo tiene en Could. Su costo es bajo
    (GDAL/OGR, que ya se usa para leer Shapefile en RF-03) y es el formato que más usan los
    analistas SIG de la base. La decisión C-13 queda en minoría.
  - **PDF:** 3/4 lo piden. RF-23 cubre una zona; el reporte multizona de I4 es otro producto.
  - **Selección vs. filtro:** el equipo filtra; I4 selecciona. La búsqueda por código (RF-10-AC-8)
    permite exportar una zona, pero no un conjunto arbitrario.
  - I4 no fija el SRC (mismo problema que I2 en C-13); RD-10 lo resuelve.
- **Opciones.**
  1. Subir el Shapefile a **Should** como RF nuevo (RF-37) y retirar RF-32-AC-2; mantener PDF por
     zona (RF-23); selección manual como Could (RF-38); reporte PDF multizona Won't.
  2. Subir el Shapefile a Must.
  3. Mantener C-13 sin cambios.
- **Recomendación: 1.** Atiende el consenso 3/4 sin ampliar el núcleo Must, cuyo volumen ya
  preocupa al equipo (157 AC en Must). El Shapefile en EPSG:32719 ya está especificado en RD-10 y
  en RF-32-AC-2, así que el traslado no requiere redefinir nada. El reporte multizona queda fuera
  porque RF-23 ya necesita mucha plantilla y la exportación CSV/GeoJSON cubre el análisis de
  varias zonas.

### C-24 — Filtros y ordenación

- **Descripción.** I4 filtra por **fecha, ubicación, extensión, prioridad y estado** y ordena por
  cualquiera de ellos, ascendente o descendente. El equipo ordena por defecto por puntaje vigente
  con desempates (sin orden alternativo), filtra por nivel y estado y busca por código.
- **Posiciones.** I4: `I4:RF-08`, `I4:RF-08-AC-1`, `I4:RF-08-AC-2`. Equipo: RF-10. Otros: I1 filtra
  además por sector y periodo (`I1:RF-12-AC-8`); I3 solo ordena por nivel (`I3:RF-06-AC-4`).
- **Impacto.** Bajo-medio. Los filtros por fecha y área son baratos. "Ubicación" es ambiguo en I4:
  ¿coordenadas, polígono, sector, dentro/fuera de la reserva? Ordenar por "ubicación" no tiene un
  criterio natural. El orden alternativo no contradice RF-10 si el orden **por defecto** sigue
  siendo el de prioridad (el valor de B3).
- **Opciones.**
  1. RF nuevo **RF-36 (Should)**: filtro por rango de fecha de la alerta más reciente, por área
     mínima y máxima y por ubicación respecto del área protegida ("dentro de la reserva", "en la
     ZA"); orden alternativo por puntaje, fecha, área o estado, ascendente o descendente.
  2. Añadir esos filtros como AC nuevos de RF-10 (Must).
  3. No incorporarlos.
- **Recomendación: 1.** Respeta la política del equipo de no inflar el Must, mantiene el orden por
  prioridad como predeterminado y define "ubicación" con un dato que el sistema ya calcula (factor
  de ubicación de RF-09). Sectores siguen en RF-30 (Could).

### C-25 — Capas territoriales: comunidades y "datos disponibles" de cada capa

- **Descripción.** I4 muestra al hacer zoom las capas que intersectan el cambio: límites de la
  reserva, ZA, **comunidades** y **concesiones** (sin precisar el tipo), y para cada capa "el
  nombre, tipo y **datos disponibles**". El equipo tiene cuatro tipos de capa (reserva, ZA, ríos,
  catastro minero), sin comunidades, y para el catastro solo tipo de derecho, código y estado,
  **nunca el titular**.
- **Posiciones.** I4: `I4:RF-04-AC-1`, `I4:RF-04-AC-2`, `I4:§2.4` ("información territorial
  sensible debe estar protegida"). Equipo: RF-03, RF-06, RF-08, RD-04, RD-06. Otros: comunidades en
  `I1:RF-01`, `I1:RF-10-AC-2`; I1 también trae concesiones forestales y de conservación, que el
  equipo dejó fuera.
- **Impacto.** Medio.
  - "Datos disponibles" de cada capa podría incluir el **titular** de una concesión, prohibido por
    RD-04, o datos de comunidades que I1 trataba como sensibles (`I1:RD-10`, consentimiento).
  - "Concesiones" en I4 puede ser mineras, forestales o de conservación; el equipo solo tiene
    mineras.
  - Agregar comunidades no es gratis: requiere fuente oficial y su fecha de corte (RD-06), y I1
    advierte que la fuente (BDPI) y su licencia están por confirmar.
  - No hay ríos en I4 (I1, I3 y el equipo los usan como factor).
- **Opciones.**
  1. Agregar la capa de comunidades nativas como **Should** (RF-35) con atributos cerrados
     (código, nombre) y sin otros datos; mantener RD-04; no adoptar "datos disponibles".
  2. Agregarla como Must, modificando RF-03, RF-06 y RF-08.
  3. No agregarla.
- **Recomendación: 1.** Atiende a I1 e I4 (2/4) y a la preocupación de I2 por las comunidades
  (`I2:RNF-03`) mostrando solo nombre y código. Agregarla al Must exigiría cambiar
  RF-06-AC-1, que fija "exactamente" seis capas. Abrir un tema (TA-05) sobre la fuente oficial y la
  licencia de la capa. Las concesiones forestales y de conservación siguen fuera.

### C-26 — RNF de rendimiento: volumen, concurrencia, ancho de banda y tiempos

- **Descripción.** I4: consulta de zonas **y comparación de periodos** en < 5 s con **500 cambios
  activos**, **20 capas** simultáneas, **10 Mbps** y **20 usuarios concurrentes**. Equipo: RNF-04
  (Must) resultado, estado o error en ≤ 60 s para cargas, ingestas y comparaciones; RNF-05 (Should)
  lista y detalle en ≤ 5 s a **1 Mbps** con **300 zonas**; sin concurrencia.
- **Posiciones.** I4: `I4:RNF-01`. Equipo: RNF-04, RNF-05, PS-14. I1: `I1:RNF-08` (1 Mbps,
  "conexión de referencia en Puerto Maldonado", `I1:S-04`), `I1:RNF-06` (300 zonas activas, 1,000
  alertas/semana), `I1:RNF-05` (análisis con imágenes en ≤ 5 min p90).
- **Impacto.** Medio.
  - **Ancho de banda:** 10 Mbps es una condición **menos exigente** que 1 Mbps; I4 la llama
    "conexión estándar de oficina" sin fuente. I1 la sustenta en la conexión real de Puerto
    Maldonado.
  - **Volumen:** 500 > 300; probar con 500 es más seguro y barato.
  - **Concurrencia:** el equipo no la mide. 20 usuarios supera con holgura los 3 del perfil de I1,
    y es una prueba de carga sencilla.
  - **Comparación en 5 s:** si se refiere a RF-14 (por datos), es plausible con 500 zonas; si se
    refiere a imágenes (RF-18, vía GEE), no es alcanzable (I1 estima minutos).
  - **20 capas:** el equipo tiene 6; la condición no aplica.
- **Opciones.**
  1. Endurecer RNF-05 con lo compatible de I4: **500 zonas activas**, **20 usuarios concurrentes**,
     manteniendo **1 Mbps**; mantener RNF-04 (60 s) para ejecutar comparaciones e imágenes.
  2. Adoptar I4 tal cual (10 Mbps, 5 s para comparar).
  3. Sin cambios.
- **Recomendación: 1.** Toma de I4 lo que hace la prueba más exigente (volumen y concurrencia) y
  descarta lo que la relaja (10 Mbps). El 5 s se aplica a mostrar resultados ya calculados (lista,
  detalle y análisis almacenados, RF-15), no a ejecutar comparaciones. RNF-05 sigue en Should,
  porque la decisión R-7 del equipo (no bloquear el núcleo con pruebas de red) sigue vigente.

### C-27 — Usabilidad: 2 horas de capacitación

- **Descripción.** I4 exige que un analista sin experiencia en programación complete las
  operaciones principales en **menos de 2 horas de capacitación**, verificado con pruebas de
  usabilidad y medición del tiempo sin asistencia. El equipo solo exige que las funciones Must no
  requieran código (RNF-06), verificado con una demostración.
- **Posiciones.** I4: `I4:RNF-02`. Equipo: RNF-06. Otros: `I3:RNF-01` (sin código), `I1:RNF-12`
  (manual que un analista sin programación puede seguir).
- **Impacto.** Bajo-medio. No hay contradicción: I4 añade una **métrica**. Pero no define cuántos
  participantes, qué tareas exactamente, ni el criterio de éxito; y todas las entrevistas fueron
  simuladas (TA-04), por lo que encontrar usuarios del perfil es en sí un riesgo.
- **Opciones.**
  1. RNF nuevo **RNF-14 (Should)**: tras una capacitación de 2 h o menos, una persona del perfil
     analista SIG que no programa completa sin asistencia un guion fijo de tareas Must (consultar
     la lista priorizada y el desglose, cambiar el estado de una zona, ajustar su prioridad,
     ejecutar una comparación de periodos y exportar a CSV); verificación: prueba de usabilidad con
     al menos una persona ajena al equipo (número a ratificar).
  2. Incorporarlo al RNF-06 (Must).
  3. No incorporarlo.
- **Recomendación: 1.** La métrica es valiosa y barata de medir, pero depende de reclutar
  usuarios, así que no debe bloquear el Must. Las tareas del guion se toman del propio `I4:RNF-02`
  (consulta, comparación, registro y clasificación) traducidas a funciones del equipo.

### C-28 — Legibilidad por escala (1:10,000 a 1:50,000)

- **Descripción.** I4 exige mostrar la información con distinción visual entre periodos y
  legibilidad de capas superpuestas a escalas entre **1:10,000 y 1:50,000**. El equipo no tiene un
  RNF de legibilidad; solo RF-06-AC-4 (colores por nivel con leyenda) y, en la ficha, mapa con
  escala (RF-23).
- **Posiciones.** I4: `I4:RNF-03`, `I4:§2.4` ("legible a escala de trabajo de zona"). Equipo:
  RF-06, RF-18, RF-23. I1: escala y fecha visibles en la ficha (`I1:RD-03`).
- **Impacto.** Bajo. La métrica de escala es concreta; "claridad" y "legibilidad" no lo son. La
  "distinción entre periodos" solo aplica a la comparación de imágenes (RF-18, Should).
- **Opciones.**
  1. RNF nuevo **RNF-15 (Should)** con criterios verificables: el mapa permite visualizar entre
     1:10,000 y 1:50,000 con barra de escala visible; a esas escalas, los contornos de las zonas
     se distinguen de las capas de referencia superpuestas (estilos distintos declarados en la
     leyenda); en RF-18, cada imagen se rotula con su periodo y su fecha. Verificación: prueba E2E
     a ambas escalas + revisión por un usuario del perfil.
  2. Adoptar el texto de I4 tal cual.
  3. No incorporarlo.
- **Recomendación: 1.** Conserva la escala de I4 (dato útil para diseñar la simbología) y
  sustituye "claridad" por condiciones observables.

### C-29 — Prioridad de la comparación de imágenes y su criterio de "misma extensión y escala"

- **Descripción.** Con I4, la comparación **visual de imágenes** de dos periodos aparece en 3 de 4
  SRS (I1, I2, I4), y en I4 es la definición misma de "comparar periodos" (`I4:RF-02`). El equipo la
  dejó en Should (RF-18) y llevó al Must la comparación por datos de alertas (RF-14), por el riesgo
  de GEE (revisión R-1).
- **Posiciones.** I4: `I4:RF-02-AC-1` ("de forma simultánea o con herramienta de comparación
  visual"), `I4:RF-02-AC-2` (misma extensión y escala). Equipo: RF-14, RF-18, revisión R-1 de
  `diferencias_SRS.md`.
- **Impacto.** Medio. La decisión R-1 se tomó por riesgo técnico, no por falta de demanda; I4
  aumenta la demanda pero no reduce el riesgo. Además `I4:RF-02-AC-2` tiene una precondición
  que presupone el resultado ("selecciona un periodo con cobertura vegetal y otro sin ella").
- **Opciones.**
  1. Mantener RF-18 en Should y añadirle el AC de extensión y escala sincronizadas.
  2. Subir RF-18 a Must.
  3. Subir a Must una versión mínima (una imagen por periodo, sin elegir la de menor nubosidad).
- **Recomendación: 1, señalando la tensión en la ratificación.** El argumento de R-1 sigue en pie:
  el flujo núcleo no debe depender de las cuotas y credenciales de GEE. Si el equipo resuelve
  pronto el acceso a GEE, la opción 3 es la vía para subirlo sin arrastrar todo RF-18.

### C-30 — Origen de los cambios y fuentes "privadas"

- **Descripción.** I4 no dice cómo se crea un "cambio detectado" (`I4:RF-07-AC-1`: "un cambio ha
  sido creado en el sistema") y exige "al menos 2 fuentes distintas de información geoespacial"
  (`I4:RF-01-AC-2`), de fuentes "públicas **y privadas**" (`I4:§2.1`).
- **Posiciones.** Equipo: RF-04 (GeoBosques, Must), RF-19 (RADD, Should), RF-03 (capas de
  INGEMMET y SERNANP), RNF-09 (sin licencias de pago), RD-13 (Planet/NICFI no se usan).
- **Impacto.** Bajo. Si "fuente" incluye las capas de referencia, el núcleo ya integra al menos
  tres (GeoBosques, INGEMMET, SERNANP) y cumple `I4:RF-01-AC-2`. Si se refiere a fuentes de
  **alertas**, la segunda (RADD) es Should. Las fuentes privadas chocan con RNF-09 y RD-13 si
  implican pago o licencias restrictivas.
- **Opciones.** 1. Mantener el equipo y documentar que la integración multifuente se cumple con
  alertas + capas de referencia. 2. Subir RADD a Must para tener dos fuentes de alertas.
- **Recomendación: 1.** La decisión C-06 sigue siendo la única que hace implementable el origen de
  los cambios; I4, como I3, no la cuestiona. "Privadas" se descarta por RNF-09 y RD-13.

---

## 5. Cambios concretos propuestos al SRS de equipo

> Reglas aplicadas: no se renumera ningún RF; los RF nuevos empiezan en **RF-34**; los AC nuevos
> toman el siguiente número libre de su RF; ningún AC existente se reescribe (si cambia, se retira
> y se agrega otro). Los RNF nuevos siguen la misma lógica desde **RNF-14**. Todo cambio requiere
> la aprobación del equipo y su registro en `diferencias_SRS.md`.

### 5.1 RF existentes: AC nuevos

| RF | AC nuevo | Redacción propuesta | Origen | Conflicto |
|---|---|---|---|---|
| RF-10 | **RF-10-AC-10** | *(Prueba E2E de interfaz.)* **Dado que** la lista contiene zonas de nivel alto, medio y bajo, **cuando** un usuario la consulta, **entonces** cada fila muestra su nivel con el mismo color que usa el mapa (RF-06) y la leyenda de los tres niveles. | `I4:RF-10-AC-2` | §3 |
| RF-12 | **RF-12-AC-19** | **Dado que** el sistema crea la zona EA-2026-042 a partir de una alerta, **cuando** se consulta su historial, **entonces** la primera entrada es "zona creada", con usuario "Sistema", fecha y hora, y el código de la alerta que la originó. | `I4:RF-07-AC-1` | §3 |
| RF-12 | **RF-12-AC-20** | **Dado que** una zona tuvo, en este orden, un cambio de estado, un ajuste de prioridad y una marca del analista, **cuando** cualquier usuario consulta su historial, **entonces** ve las tres acciones en una sola lista en orden cronológico, cada una con tipo de acción, usuario, fecha y hora. | `I4:RF-07-AC-2` | §3 |
| RF-18 | **RF-18-AC-4** | *(Prueba E2E de interfaz.)* **Dado que** se muestran lado a lado las imágenes de A y B de una zona, **cuando** el analista hace zoom o desplaza una de ellas, **entonces** la otra muestra la misma extensión geográfica y la misma escala. | `I4:RF-02-AC-2` | C-29 |
| RF-29 | **RF-29-AC-2** | **Dado que** un analista marcó "Revisión completada" el 01/10/2026 y una zona de nivel "media" pasa a nivel "alta" el 02/10/2026, **cuando** él consulta la lista el 03/10/2026, **entonces** la zona tiene el indicador "nueva desde tu última revisión" con el motivo "pasó a nivel alta". | `I4:RF-09` | C-21 |
| RF-29 | **RF-29-AC-3** | **Dado que** una zona pasó a nivel "alta", **cuando** se revisa el servidor de correo simulado y la API, **entonces** no se envió ningún mensaje fuera del sistema. | RD-05, `I1:RF-37-AC-7` | C-21 |

Además, en la **descripción de RF-29**, añadir el evento "(d) la zona pasó a nivel alta" a la lista
de eventos que activan el indicador.

### 5.2 RF existentes: retiro de un AC

| AC | Acción | Motivo |
|---|---|---|
| RF-32-AC-2 | **Retirar** (conserva el ID sin criterio, con la nota "trasladado a RF-37-AC-1"). Quitar la viñeta de Shapefile de la descripción de RF-32. | Shapefile sube a Should (C-23). |

### 5.3 RF nuevos

#### RF-34 — Observaciones de la zona (Should)

**Descripción propuesta:** El analista debe poder registrar en una zona una observación de texto
libre, sin cambiar su estado. Cada observación guarda autor, fecha y hora, es visible para ambos
roles y aparece en el historial (RF-12). Las observaciones no se editan ni se eliminan. La
coordinación no registra observaciones (403). **Origen:** `I4:RF-05`, `I3:RF-09-AC-3`.

- **RF-34-AC-1** — **Dado que** una zona está en "en revisión", **cuando** un analista registra la observación "revisar con imagen de octubre", **entonces** la observación queda asociada a la zona con su nombre, fecha y hora, y el estado sigue siendo "en revisión".
- **RF-34-AC-2** — **Dado que** un analista registró una observación en una zona, **cuando** la coordinación consulta el detalle de esa zona, **entonces** ve la observación con su autor y fecha.
- **RF-34-AC-3** — **Dado que** un analista intenta registrar una observación vacía, **cuando** confirma, **entonces** el sistema la rechaza indicando que el texto es obligatorio.
- **RF-34-AC-4** — **Dado que** la coordinación está autenticada, **cuando** intenta registrar una observación por la API, **entonces** la API responde 403 y no se crea la observación.
- **RF-34-AC-5** — **Dado que** existe una observación, **cuando** se envía una solicitud de modificación o borrado a la API, **entonces** la API no expone la operación (404 o 405) y la observación no cambia.

*(Si se adopta, agregar la fila correspondiente a la matriz de §2.3 en la descripción del RF, como
hacen los demás RF Should, y considerar un AC en RF-23 para que la ficha incluya las observaciones.)*

#### RF-35 — Capa de comunidades nativas (Should)

**Descripción propuesta:** Se agrega el tipo de capa de referencia "Comunidades nativas"
(polígono; atributos obligatorios código y nombre; ningún otro atributo se almacena). Al
implementarse este RF: la tabla de RF-03 incluye el nuevo tipo, el mapa de RF-06 incluye la capa
y el contexto de RF-08 lista las comunidades superpuestas con nombre, código y fecha de corte.
**Origen:** `I4:RF-04-AC-1`, `I1:RF-01`, `I1:RF-10-AC-2`. **Tema abierto nuevo TA-05:** fuente
oficial y licencia de la capa (I1 propone la BDPI del Ministerio de Cultura).

- **RF-35-AC-1** — **Dado que** un analista carga un GeoJSON de comunidades nativas con fuente y fecha de corte y asigna código y nombre, **cuando** la carga termina, **entonces** la capa queda disponible con esos dos atributos y ninguna otra columna del archivo se almacena.
- **RF-35-AC-2** — **Dado que** una zona cruza el territorio de una comunidad nativa, **cuando** se consulta su contexto, **entonces** el sistema lista la comunidad con su nombre, su código y la fecha de corte de la capa.
- **RF-35-AC-3** — **Dado que** existe una versión de la capa de comunidades nativas, **cuando** un usuario solicita la lista de capas del mapa, **entonces** "Comunidades nativas" aparece como capa activable.
- **RF-35-AC-4** — **Dado que** la coordinación está autenticada, **cuando** intenta cargar la capa de comunidades por la API, **entonces** la API responde 403 y no se crea ninguna versión.

*Nota:* RF-06-AC-1 dice "exactamente" seis capas. Al implementar RF-35 hay que **retirar**
RF-06-AC-1 y agregar RF-06-AC-7 con la lista de siete capas; no reescribir el criterio existente.

#### RF-36 — Filtros y orden adicionales de la lista (Should)

**Descripción propuesta:** La lista de zonas (RF-10) admite, además de los filtros de nivel y
estado, filtros por **rango de fecha de detección de la alerta más reciente**, **área mínima y
máxima (ha)** y **ubicación** ("dentro de la reserva", "en la ZA"). Admite también ordenar por
puntaje vigente, fecha de la alerta más reciente, área o estado, de forma ascendente o
descendente. El orden por defecto sigue siendo el de RF-10. Los filtros se combinan entre sí y
con los de RF-10, y los conteos reflejan el resultado. **Origen:** `I4:RF-08`, `I1:RF-12-AC-8`.

- **RF-36-AC-1** — **Dado que** existen zonas cuya alerta más reciente es del 05/08/2026, 20/09/2026 y 02/10/2026, **cuando** el usuario filtra por el rango 01/09/2026–30/09/2026, **entonces** solo aparece la zona del 20/09/2026.
- **RF-36-AC-2** — **Dado que** existen zonas de 0.80 ha, 2.00 ha y 12.50 ha, **cuando** el usuario filtra por área mínima 1 ha y máxima 10 ha, **entonces** solo aparece la de 2.00 ha.
- **RF-36-AC-3** — **Dado que** una zona está dentro de la reserva y otra solo en la ZA, **cuando** el usuario filtra por "dentro de la reserva", **entonces** solo aparece la primera.
- **RF-36-AC-4** — **Dado que** existen zonas de 3.00 ha, 0.50 ha y 7.25 ha, **cuando** el usuario ordena por área ascendente, **entonces** aparecen en el orden 0.50, 3.00, 7.25.
- **RF-36-AC-5** — **Dado que** el usuario ordenó por área, **cuando** elige "restablecer orden", **entonces** la lista vuelve al orden por defecto de RF-10.
- **RF-36-AC-6** — **Dado que** el usuario indica un área mínima mayor que la máxima, **cuando** aplica el filtro, **entonces** el sistema lo rechaza indicando que el mínimo no puede superar al máximo.

#### RF-37 — Exportación de zonas a Shapefile (Should)

**Descripción propuesta:** El analista debe poder exportar las zonas de la lista filtrada a
Shapefile comprimido (.zip) en EPSG:32719 (RD-10), con los atributos de RF-17 (nombres de campo
de 10 caracteres como máximo), sin titulares (RD-04). La coordinación recibe 403. Sustituye la
viñeta de Shapefile de RF-32. **Origen:** `I4:RF-13-AC-2`, `I1:RF-18`, `I2:RF-07`, RF-32-AC-2.

- **RF-37-AC-1** — **Dado que** se exportan zonas a Shapefile, **cuando** se lee el .zip con `ogrinfo`, **entonces** contiene .shp, .shx, .dbf y .prj y reporta EPSG:32719. *(Traslado del retirado RF-32-AC-2.)*
- **RF-37-AC-2** — **Dado que** la lista filtrada muestra 6 zonas, **cuando** el analista las exporta a Shapefile, **entonces** el archivo tiene 6 elementos con los atributos de RF-17 y ninguno con el nombre del titular.
- **RF-37-AC-3** — **Dado que** la coordinación está autenticada, **cuando** solicita la exportación a Shapefile por la API, **entonces** la API responde 403.

#### RF-38 — Selección manual de zonas para exportar (Could)

**Descripción propuesta:** En la lista, el analista puede marcar zonas y exportar solo las
seleccionadas en los formatos de RF-16, RF-17 y RF-37. Sin selección, se exporta la lista filtrada
como hasta ahora. **Origen:** `I4:RF-13`.

- **RF-38-AC-1** — **Dado que** la lista filtrada muestra 8 zonas y el analista seleccionó 2, **cuando** exporta a GeoJSON "solo seleccionadas", **entonces** el archivo tiene exactamente esas 2 zonas.
- **RF-38-AC-2** — **Dado que** el analista no seleccionó ninguna zona, **cuando** exporta, **entonces** el archivo contiene todas las zonas de la lista filtrada (comportamiento de RF-16 y RF-17).

#### RF-39 — Responsable de la zona (Could)

**Descripción propuesta:** Una zona activa puede tener un analista responsable. Un analista puede
asignarse una zona o liberarla; la coordinación puede asignar o reasignar el responsable. La
asignación **no cambia el estado** de la zona (RF-12) y queda en el historial. La lista se puede
filtrar por responsable. **Origen:** `I4:RF-11`, `I4:RF-12`. *(Si se adopta, la matriz de §2.3
debe reflejar que la coordinación asigna responsables; ver C-19, opción 2.)*

- **RF-39-AC-1** — **Dado que** una zona en "nueva" no tiene responsable, **cuando** un analista se la asigna, **entonces** la zona tiene a ese analista como responsable, su estado sigue en "nueva" y el historial registra la asignación.
- **RF-39-AC-2** — **Dado que** una zona tiene responsable, **cuando** la coordinación la reasigna a otro analista, **entonces** el responsable cambia y el historial registra ambos nombres, quién reasignó y la fecha.
- **RF-39-AC-3** — **Dado que** se intenta asignar una zona a una cuenta con rol coordinación, **cuando** se confirma, **entonces** el sistema lo rechaza indicando que el responsable debe ser analista SIG.

### 5.4 RNF

| RNF | Cambio | Redacción propuesta | Verificación | Prioridad |
|---|---|---|---|---|
| RNF-05 | **Modificar condiciones** (no cambia la categoría ni la prioridad) | Con una conexión limitada a 1 Mbps y la caché vacía, la lista de zonas, el detalle de una zona y el detalle de un análisis almacenado (RF-15) cargan en 5 s o menos con **500 zonas activas** y **20 usuarios concurrentes** consultando. | Prueba con limitación de red en el navegador + prueba de carga con 20 usuarios virtuales. | Should |
| RNF-14 | **Nuevo** — Facilidad de aprendizaje | Tras una capacitación de 2 h o menos, una persona del perfil analista SIG que no programa completa sin asistencia este guion: consultar la lista priorizada y el desglose de una zona, cambiar su estado, ajustar su prioridad con justificación, ejecutar una comparación de periodos y exportar la lista a CSV. | Prueba de usabilidad con al menos una persona ajena al equipo (número a ratificar); se mide el tiempo y si completó cada tarea sin ayuda. | Should |
| RNF-15 | **Nuevo** — Legibilidad del mapa | El mapa permite visualizar a escalas entre 1:10,000 y 1:50,000, con barra de escala visible; a esas escalas, las zonas se distinguen de las capas de referencia superpuestas por estilos declarados en la leyenda. En RF-18, cada imagen se rotula con su periodo y su fecha. | Prueba E2E a 1:10,000 y 1:50,000; revisión por un usuario del perfil. | Should |

Si el equipo aplica RNF-05 tal como se propone, la descripción de RNF-04 no cambia (60 s para
ejecutar cargas, ingestas y comparaciones).

### 5.5 Otros cambios de texto

| Sección | Cambio | Motivo |
|---|---|---|
| §1.2, lista Won't | Añadir "Reporte PDF de varias zonas" y "Envío de credenciales por correo" | C-22, C-23 |
| §1.3 | Añadir "**Responsable**" (si se adopta RF-39) y "**Observación**" (si se adopta RF-34); precisar en "Notificación" que los avisos internos se llaman **indicadores** | C-21 |
| §2.2 | Actualizar los rangos de Should y Could con RF-34 a RF-39 | Convención |
| §2.4, temas abiertos | **TA-05:** fuente oficial y licencia de la capa de comunidades nativas | C-25 |
| Convención de IDs | "RF-01 a RF-39"; listar los Should y Could nuevos | Convención |
| `diferencias_SRS.md` | Añadir I4 a los insumos, al resumen (§2), a los aportes (§4), los conflictos C-18 a C-30 (§5), la tabla de correspondencia (§8.4) y la ratificación (§10) | Trazabilidad |

### 5.6 Lo que se propone **no** cambiar

- RF-09 y RF-11 (priorización calculada y ajuste por puntaje con justificación), salvo que el
  equipo elija la opción 2 de C-18.
- Los dos roles y la matriz de §2.3 (C-19), salvo la asignación de responsables si se adopta RF-39.
- La máquina de estados de RF-12 (C-20).
- RF-02 (sin envío de credenciales) (C-22).
- RF-18 en Should (C-29).
- RD-04 (nunca titulares), aunque `I4:RF-04-AC-2` pida "datos disponibles".

---

## 6. Calidad de I4

### 6.1 Criterios de aceptación

| AC | Verificable | Problema |
|---|---|---|
| `I4:RF-01-AC-1` | Parcial | "Muestra los datos de dicha fuente": no dice qué datos ni cómo comprobarlo. |
| `I4:RF-01-AC-2` | Sí | Número concreto (≥ 2), pero "fuente" no está definida (¿alertas, capas, imágenes?). |
| `I4:RF-02-AC-1` | Parcial | Disyunción "simultánea **o** con herramienta de comparación visual": cualquier implementación cumple. |
| `I4:RF-02-AC-2` | Parcial | El resultado (misma extensión y escala) es verificable, pero la precondición ("un periodo con cobertura vegetal y otro sin ella") presupone lo que se quiere detectar y no se puede preparar como dato de prueba. |
| `I4:RF-03-AC-1` | Sí | Falta precisión de la extensión (decimales, SRC del cálculo). |
| `I4:RF-04-AC-1` | Parcial | "Hace zoom" no define el nivel; "concesiones" no dice de qué tipo. |
| `I4:RF-04-AC-2` | No | "Datos disponibles" es abierto y puede incluir datos prohibidos (titulares, RD-04). |
| `I4:RF-05-AC-1` | Sí | Claro y completo (asociación, visibilidad, autor, fecha). |
| `I4:RF-06-AC-1` | Parcial | Mezcla dos comportamientos (registrar y "puede ser reclasificado en cualquier momento"); "en cualquier momento" no es comprobable en un solo caso. |
| `I4:RF-07-AC-1` | Parcial | "Cualquier acción" no es una lista cerrada; los ejemplos entre paréntesis sí lo son. |
| `I4:RF-07-AC-2` | Sí | — |
| `I4:RF-08-AC-1` | Parcial | "Ubicación" como filtro no está definido. |
| `I4:RF-08-AC-2` | Parcial | Ordenar por "ubicación" no tiene criterio definido. |
| `I4:RF-09-AC-1` | Sí | El disparador del AC ("se guarda la clasificación") no coincide con el de la descripción ("se detecte un nuevo cambio"). |
| `I4:RF-09-AC-2` | Sí | — |
| `I4:RF-10-AC-1` | Parcial | "Pendientes de revisión" = "aún no revisados": ¿incluye "En revisión"? Ambiguo frente a los estados de `I4:RF-11`. |
| `I4:RF-10-AC-2` | No | "Se distinguen visualmente" sin criterio (color, ícono, posición). |
| `I4:RF-11-AC-1` | Sí | Contradice `I4:RF-12` sobre quién asigna (el especialista se asigna vs. el coordinador asigna). |
| `I4:RF-11-AC-2` | Sí | — |
| `I4:RF-12-AC-1` | Parcial | "Envía las credenciales" sin canal ni contenido; riesgo de seguridad (C-22). |
| `I4:RF-12-AC-2` | Sí | Buen criterio (impide acceso y preserva historial). |
| `I4:RF-13-AC-1` | Parcial | "Mapa" sin contenido mínimo (escala, fecha, leyenda). |
| `I4:RF-13-AC-2` | Parcial | Sin SRC ni atributos; "Shapefile **o** GeoJSON" en un mismo criterio. |

**Resumen:** de 23 AC, unos **9 son verificables** tal como están, **12 parcialmente** y **2 no**.
Faltan casos negativos en casi todos los RF: transiciones rechazadas y la transición "En revisión
→ Pendiente" (`I4:RF-11` la define sin AC), accesos 403 por rol (`I4:RNF-04` los exige sin AC),
entradas inválidas (prioridad fuera de los tres niveles, filtros incoherentes) y exportación sin
resultados. No hay valores de prueba (áreas, fechas, distancias) ni tipo de verificación (API / E2E
/ manual), que la convención del equipo exige para nombrar las pruebas `test_RF_XX_AC_Y`.

### 6.2 RNF

- `I4:RNF-01`: el más medible (5 s, 500, 20, 10 Mbps, 20 usuarios), pero su verificación cita un
  "volumen típico de datos de la zona de estudio" que no coincide con la condición numérica.
- `I4:RNF-02`: métrica concreta (2 h), sin número de participantes, guion de tareas ni criterio
  de éxito.
- `I4:RNF-03`: la escala es concreta; "claridad" y "legibilidad" son subjetivas.
- `I4:RNF-04`: verificable; añade "registro de accesos y acciones sensibles" sin definir cuáles.

### 6.3 Términos ambiguos o inconsistentes

| Término | Problema |
|---|---|
| "Cambio" / "zona" | Se usan como sinónimos (`I4:RF-01`, `I4:RNF-01`, `I4:RD-03` hablan de zonas; el resto, de cambios), y "cambio de cobertura" se define como variación entre periodos, no como un objeto con estado. |
| "Especialista" | Es a la vez un **rol** (`I4:RF-12`) y la **persona que decide** (`I4:§2.4`, `I4:RD-02`, `I4:RD-03`), lo que hace ambiguo si el Analista puede decidir. |
| Nombres de roles | "Analista Ambiental", "Especialista SIG" y "Coordinador de Monitoreo" (`I4:§2.3`) frente a "Analista", "Especialista" y "Coordinador" (`I4:RF-12`, `I4:RNF-04`). |
| "Notificación" | Interna en I4; externa en el glosario del equipo (C-21). |
| "Detecte" | `I4:RF-09` habla de detectar un cambio de alta prioridad, pero en I4 la prioridad la asigna una persona. |
| "Fuentes privadas" | Sin ejemplo; potencial conflicto con RNF-09 y RD-13 (C-30). |
| "Falso positivo" | Definido en el glosario pero sin estado ni flujo que lo registre (C-20). |
| "Datos disponibles", "información territorial sensible" | Sin lista cerrada (C-25). |
| "Escala de trabajo de zona" | `I4:§2.4`; solo se concreta en `I4:RNF-03`. |
| "Gestión de prioridades" (coordinador) | `I4:§2.3`; no aparece en los permisos de `I4:RF-12`. |

### 6.4 Valoración global

I4 es un SRS **breve, bien alineado con la base en ámbito y en la regla de no atribuir causas**, y
con un formato de AC que respeta la convención del equipo (Given-When-Then con IDs). Sus aportes
útiles son de **experiencia de uso**: observaciones libres, filtros y orden, capa de comunidades,
historial unificado, Shapefile y métricas de usabilidad, escala y concurrencia. Sus debilidades
son: priorización solo manual (no cumple el valor principal de B3), origen de los cambios sin
especificar, roles y estados internamente inconsistentes, y AC sin datos de prueba ni casos
negativos. Ninguna de sus diferencias obliga a revertir una decisión estructural del equipo
(C-04, C-05, C-07, C-08); las que quedan en minoría (ajuste por puntaje en RF-11, Shapefile en
Could) se señalan para la ratificación.
