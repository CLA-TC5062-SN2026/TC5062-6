# Diferencias entre los SRS individuales y consolidación del SRS de equipo

| Campo | Valor |
|---|---|
| Actividad | Parte 0 — Consolidación del SRS de equipo |
| Fecha | 04/10/2026 |
| Resultado | `SRS_equipo.md` v1.0 (línea base de equipo) |
| Insumos | `insumos/SRS_integrante1_A01840503.md`, `insumos/SRS_integrante2.md`, `insumos/SRS_integrante3.md`, `insumos/SRS_integrante4.md`, `insumos/proyecto_base.md` |
| Análisis del agente (originales, sin editar) | `borradores/analisis_diferencias_agente.md` (I1–I3) y `borradores/analisis_diferencias_agente_addendum_I4.md` (I4) |

**Convención.** Los IDs de los SRS individuales no coinciden entre sí. Por ejemplo, RF-01 es
"mapa con capas" en I1, "zona y periodos" en I2 y "autenticación" en I3. Por eso, en este documento
todo ID individual lleva el prefijo de su autor (`I1:`, `I2:`, `I3:`, `I4:`). Los IDs **sin prefijo**
son los del SRS de equipo.

---

## 1. Proceso seguido

1. **Reunir los insumos.** Se reunieron los tres `SRS_final.md` de S02-A1 y la base del proyecto
   acordada por el equipo (`proyecto_base.md`).
2. **Análisis con un agente.** Un agente independiente, con rol de analista de requerimientos,
   comparó los tres documentos **por contenido**, no por número de ID. Identificó consenso, gaps
   y 17 conflictos (C-01 a C-17) y propuso un núcleo MVP. Su salida se conserva sin editar en
   `borradores/`.
3. **Revisión crítica del análisis.** Se aceptaron la mayoría de sus recomendaciones y se
   corrigieron seis puntos (sección 6).
4. **Decisiones de equipo** sobre los conflictos estructurales (sección 5): modelo de zona, roles,
   estados, comparación de periodos y priorización.
5. **Redacción de `SRS_equipo.md`** con la estructura IEEE 830 de S02-A1, numeración nueva y
   congelada, prioridad MoSCoW y criterios Given-When-Then con IDs `RF-XX-AC-Y`.
6. **Integración del cuarto SRS.** El SRS del Integrante 4 llegó después del primer borrador.
   Un segundo agente independiente lo comparó con los otros tres y con el borrador
   (`borradores/analisis_diferencias_agente_addendum_I4.md`). Así surgieron los conflictos C-18 a
   C-30 y los RF-34 a RF-39. Los cambios se aplicaron **sin renumerar** nada: AC nuevos al final
   de cada RF, RF nuevos desde RF-34 y un AC retirado (RF-32-AC-2).
7. **Ratificación** por los cuatro integrantes (sección 10).

---

## 2. Resumen de los SRS individuales

| | I1 — Miguel Angel Arevalo Andrade | I2 — *[nombre]* | I3 — *[nombre]* | I4 — *[nombre]* |
|---|---|---|---|---|
| Base | EcoAlert Tambopata (v3.0) | EcoAlert genérico (v1.0): cualquier zona del Perú | EcoAlert Tambopata | EcoAlert Tambopata |
| Entidad central | Zona de cambio persistente que agrupa alertas | Zona de interés elegida por el usuario | Análisis de dos periodos que contiene zonas candidatas | "Cambio detectado" persistente con historial |
| Origen de los cambios | Alertas GeoBosques/RADD + candidatos NDVI | Detección propia por umbral NDVI/NDFI | No especificado | No especificado |
| Priorización | 0–100, 7 factores, desglose | No tiene | Alta/Media/Baja, 6 factores, sin fórmula | Solo manual (alta/media/baja), sin justificación |
| Causas | Prohibidas | **Clasifica "posible minería"** | Prohibidas | Prohibidas |
| Roles | 2 (Analista SIG, Coordinación) | 3 (Analista, Admin. institucional, Superadmin) | 1 (Especialista) | 3 (Analista, Especialista, Coordinador que asigna) |
| Tamaño | 38 RF activos, 15 RNF, 19 RD, 452 AC | 11 RF, 4 RNF, 3 RD, 41 AC sin ID | 11 RF, 5 RNF, 5 RD, 32 AC | 13 RF, 4 RNF, 3 RD, 23 AC |
| Formato de AC | Given-When-Then con ID | Viñetas sin ID | Given-When-Then con ID | Given-When-Then con ID, pocos valores concretos |
| Fortaleza | Verificable y completo | Necesidades de usuario concretas (campo, fuentes caídas, discrepancias) | Fiel a la base; claro en incertidumbre y periodos | Necesidades de trabajo diario: observaciones, filtros, exportación, métricas de usabilidad |
| Debilidad | Tamaño (no construible en el curso) | Contradice la base (causas, ámbito, sin prioridad) | Subespecificado (sin fuente ni fórmula) | Priorización solo manual; roles inconsistentes; sin origen de los cambios |

---

## 3. Consenso, consenso parcial y gaps

El detalle completo está en `borradores/analisis_diferencias_agente.md`, secciones 2 a 4, y en
`borradores/analisis_diferencias_agente_addendum_I4.md`, secciones 2 y 3. Esta es la síntesis y
su resultado en el SRS de equipo.

### 3.1 Consenso (presente en los tres primeros; con I4 casi todo pasa a 4/4)

| Tema | Resultado en el SRS de equipo |
|---|---|
| Aplicación web usable sin programar | RNF-06 |
| Comparación de dos periodos | RF-14 (datos, Must) y RF-18 (imágenes, Should) |
| Identificación de zonas con cambio | RF-04 + RF-05 (alertas oficiales agrupadas) |
| Visualización en mapa con capas activables | RF-06 |
| Contexto territorial / área protegida | RF-08 |
| Estado de revisión e historial | RF-12 |
| La decisión final es humana | §1.2, RD-03, RF-11, RF-12 |
| No ocultar fallas de fuentes externas | RF-07, RNF-08 |
| Calidad de la evidencia (nubes, sombras, estacionalidad) | RD-09, RF-13, RF-18 |
| Incertidumbre visible | RF-13 (marcas), RF-12 ("requiere verificación") |
| Persistencia temporal del cambio | Factor de RF-09 |
| Trazabilidad de fuentes y periodos | RNF-07, RF-14 |
| Conservación del trabajo para consulta posterior | RF-14, RF-15, RF-12 |
| Acceso restringido | RF-01, RNF-01 |

### 3.2 Gaps: aportes que solo tenía un integrante

| Aporte | De | ¿Se incorporó? |
|---|---|---|
| Ingesta y agrupación de alertas en zonas persistentes | I1 | Sí: RF-04, RF-05 (Must) |
| Fórmula verificable de prioridad con desglose | I1 | Sí, reducida a 5 factores: RF-09 |
| Capas con fuente y fecha de corte; nunca titulares | I1 | Sí: RF-03, RD-04, RD-06 |
| Matriz rol × acción con 403 | I1 | Sí: §2.3, RNF-02 |
| Reapertura automática, pesos versionados, GeoPackage/KML, ficha PDF, bitácora, TOTP | I1 | Sí, como Should: RF-20 a RF-25 |
| Versiones de zona con revisión técnica o de contenido, expediente, resumen mensual, supresión | I1 | No (Won't): costo alto y fuera del núcleo |
| Aviso de fuente desactualizada | I2 | Sí: RF-07 (con umbral PS-13, que I2 no fijaba) |
| Mensaje explícito "sin cambios" en lugar de una capa vacía | I2 | Sí: RF-14-AC-10 (también estaba en I3) |
| Fuentes mostradas por separado, sin veredicto único | I2 | Sí: RF-04 (cada alerta conserva su fuente), RF-19-AC-2, RF-31 |
| Desfase de 1–4 semanas de las fuentes | I2 | Sí: RD-08 |
| Necesidad de trabajo en campo | I2 | Sí, por exportación (RF-22), no como modo offline |
| Slider y exportación como imagen | I2 | Como Could: RF-32 |
| Reglas de validez de periodos (inicio ≤ fin, distintos, no superpuestos, un día válido) | I3 | Sí: RF-14-AC-3 a AC-6 |
| "No disponible" por factor, sin omitirlo | I3 | Sí: RF-09 (con reescalado, sección 5, C-08) |
| Determinismo de la prioridad | I3 | Sí: RF-09-AC-12 |
| Almacenamiento automático e inmutable del análisis | I3 | Sí: RF-14-AC-13, AC-14 |
| Lista y detalle de análisis anteriores | I3 | Sí: RF-15 |
| "Revisado" no implica confirmación | I3 | Sí: RD-11 |
| Retroalimentación en ≤ 60 s | I3 | Sí: RNF-04 |
| "Información no disponible" si no hay capa de ríos | I3 | Sí: RF-08-AC-7 |
| Análisis "no concluido" ante información insuficiente | I3 | Sí: estados "incompleto" y "sin datos" de RF-14 |
| Observaciones libres sobre la zona (también parcial en I3) | I4 | Sí: RF-34 (Should) |
| Capa de comunidades nativas (también en I1) | I4 | Sí, solo con nombre y código: RF-35 (Should) |
| Filtros por fecha, área y ubicación; orden ascendente/descendente | I4 | Sí: RF-36 (Should) |
| Exportación a Shapefile (también en I1 e I2) | I4 | Sí: RF-37 (Should; antes Could) |
| Historial cronológico único, incluida la creación | I4 | Sí: RF-12-AC-19, AC-20 |
| Aviso interno de alta prioridad | I4 | Sí, como indicador: RF-29-AC-2, AC-3 (Could) |
| Asignación de un responsable | I4 | Sí, desacoplada del estado: RF-39 (Could) |
| Selección manual de zonas para exportar | I4 | Sí: RF-38 (Could) |
| Métricas de aprendizaje (2 h), legibilidad por escala y concurrencia | I4 | Sí: RNF-14, RNF-15, RNF-05 |
| Reporte PDF de varios cambios; envío de credenciales | I4 | No (Won't): C-23, C-22 |

---

## 4. Qué aportó cada integrante al SRS consolidado

### Integrante 1 — Miguel Angel Arevalo Andrade (A01840503)

- **Modelo de datos y flujo central:** ingesta de alertas oficiales (RF-04), agrupación en zonas
  persistentes (RF-05) y glosario de zona, alerta y fecha de corte.
- **Priorización verificable:** fórmula 0–100 con normalizaciones, desempates y redondeo (RF-09,
  RF-10), ajuste manual (RF-11) y la regla "nunca reajusta solo" (RD-03).
- **Contexto territorial con salvaguardas:** superposición con el catastro minero sin titulares y
  con fecha de corte (RF-08, RD-04, RD-06), carga de capas validada (RF-03).
- **Estados con tabla cerrada** (RF-12) y **marcas de confianza** que no ocultan ni cambian el
  puntaje (RF-13).
- **Seguridad y operación:** matriz de roles con 403 (§2.3, RNF-02), RNF con método de
  verificación, costo y despliegue (RNF-09, RNF-10).
- **Formato:** convención de IDs inmutables `RF-XX-AC-Y`, tipos de verificación y prioridad MoSCoW.
- **Mejoras Should y Could:** RF-18 a RF-33, en su mayoría versiones reducidas de sus RF.

### Integrante 2 — *[nombre y matrícula]*

- **Necesidades del usuario que no estaban en los otros SRS:** aviso de fuente desactualizada con
  datos en caché (RF-07, RNF-08), desfase de 1–4 semanas de las fuentes (RD-08) y no fusionar
  fuentes en un veredicto (RF-04, RF-19, RF-31).
- **Comparación de periodos A y B** como función visible para el usuario (RF-14), con vista lado a
  lado (RF-18) y slider (RF-32).
- **Trabajo en campo:** su RNF-02 motivó la exportación para QField/Avenza (RF-22).
- **Calidad de detección:** nubes, sombras y cultivos estacionales (RD-09) y la persistencia en
  lecturas consecutivas, que se convirtió en el factor "persistencia" de RF-09.
- **Exportación de resultados:** reporte e imagen (RF-23, RF-32).
- **Configurabilidad de umbrales** (RF-21).
- **Límite de resolución espacial** de 0.5–1 ha (RD-07, marca "área pequeña" de RF-13).

### Integrante 3 — *[nombre y matrícula]*

- **Fidelidad a la base:** ámbito Tambopata (RD-01), no atribuir causa ni legalidad (RD-02),
  prioridad como recomendación (RD-03).
- **Periodos:** reglas de validez completas (RF-14-AC-3 a AC-6).
- **Manejo de la incertidumbre:**
  - "No disponible" por factor y prioridad "No disponible" (RF-09);
  - "Información no disponible" en el contexto (RF-08-AC-7);
  - análisis "incompleto" o "sin datos" en lugar de presentarlo como concluido (RF-14-AC-11, AC-12);
  - estado para evidencia insuficiente, que se convirtió en "requiere verificación" (RF-12).
- **Persistencia del análisis:** almacenamiento automático e inmutable (RF-14) y consulta de
  análisis anteriores (RF-15).
- **Determinismo** de la prioridad (RF-09-AC-12) y **"Revisado ≠ confirmado"** (RD-11).
- **RNF medibles:** retroalimentación en 60 s (RNF-04), trazabilidad (RNF-07) y robustez (RNF-08).
- **Formato:** Given-When-Then con IDs, un comportamiento por criterio.

### Integrante 4 — *[nombre y matrícula]*

- **Trabajo diario del analista:**
  - observaciones libres sobre la zona (RF-34);
  - historial cronológico único que incluye la creación (RF-12-AC-19, AC-20);
  - filtros por fecha, área y ubicación, y orden ascendente o descendente (RF-36);
  - color de nivel en la lista (RF-10-AC-10).
- **Ajuste de prioridad por nivel** (alta/media/baja), junto con I3: RF-11-AC-8 a AC-13.
- **Exportaciones:** Shapefile (RF-37) y selección manual de zonas (RF-38); su PDF refuerza
  RF-23.
- **Contexto territorial:** capa de comunidades nativas (RF-35).
- **Supervisión:** responsable de la zona, asignable por la coordinación (RF-39), y aviso de alta
  prioridad como indicador (RF-29-AC-2).
- **RNF medibles:** 20 usuarios concurrentes y 500 zonas (RNF-05), aprendizaje en ≤ 2 h (RNF-14) y
  legibilidad entre 1:10,000 y 1:50,000 (RNF-15).
- **Imágenes con la misma extensión y escala** en la comparación visual (RF-18-AC-4).
- **Refuerzo de decisiones:** con su SRS pasan a 3/4 el ámbito Tambopata (C-03), la prohibición de
  causas (C-01), el catastro como contexto (C-02), los periodos (C-16) y la tabla cerrada de
  estados (C-07).

---

## 5. Resolución de conflictos

Las posiciones completas de cada integrante, con sus IDs, están en
`borradores/analisis_diferencias_agente.md`, sección 5. Las decisiones C-04, C-05, C-07 y la
comparación de periodos las tomó el equipo sobre opciones concretas. Las demás siguen la
recomendación del análisis, revisada. Todas quedan sujetas a la ratificación de la sección 10.

| ID | Conflicto | Posiciones | Decisión del equipo | Motivo | En el SRS |
|---|---|---|---|---|---|
| C-01 | Atribución de causa ("posible minería") | I2 clasifica automáticamente; I1 e I3 lo prohíben | **Se elimina la clasificación automática.** Las hipótesis solo como "Marca del analista", manual y rotulada | La base dice "sin determinar automáticamente sus causas". "Posible minería" junto a una concesión se lee como acusación. Una clasificación renombrada ("patrón espectral") sería la misma inferencia disfrazada | RD-02, RF-13, RF-09-AC-14, RF-08-AC-8, RF-27-AC-1 |
| C-02 | Cruce con concesiones mineras | I2: contexto "legal-administrativo"; I1: superposición neutral sin titular; I3: sin concesiones | **Superposición factual** (tipo de derecho, código, estado, fecha de corte), **sin titulares** y sin rótulo "legal" | El contexto minero es relevante en Tambopata y barato con PostGIS; la regla sin titulares y la fecha de corte eliminan el riesgo | RF-03, RF-08, RD-04, RD-06 |
| C-03 | Alcance geográfico | I2: zona libre; I1 e I3: Tambopata + ZA | **Tambopata + ZA**, con el límite cargado como dato | Lo fija la base; acota los datos, las pruebas y el costo | RD-01 |
| C-04 | Roles | I1: 2 roles; I2: 3 roles con instituciones; I3: 1 rol | **Analista SIG + Coordinación**. La Coordinación consulta, compara periodos y gestiona usuarios, pero no cambia datos ni exporta. Sin multiorganización ni Superadmin | Mantiene a quien administra separado de quien opera, con la matriz de I1 reducida. La multiorganización no tiene sustento en la base. El agente proponía un "administrador" genérico; el equipo prefirió el perfil de usuario real de I1 | §2.3, RF-02, RNF-02 |
| C-05 | Qué es una "zona" | I1: zona persistente; I2: área del usuario; I3: zona dentro de un análisis | **Zona de cambio persistente** + **análisis inmutable** (de I3) como registro de cada comparación | Responde "qué zonas revisar primero" a lo largo del tiempo sin revisar el mismo lugar en cada análisis; conserva la inmutabilidad del histórico de I3 | §1.3, RF-05, RF-14, RF-15 |
| C-06 | Origen de los cambios | I1: alertas oficiales; I2: detector NDVI/NDFI propio; I3: no dice | **Alertas oficiales**: GeoBosques por archivo (Must), RADD (Should). NDVI solo como candidatos que valida el analista (Could) | Menor riesgo técnico y verificable con archivos de prueba. "No especificado" no es implementable | RF-04, RF-19, RF-27 |
| C-07 | Estados de revisión | I1: 7 estados con tabla; I2: incluye "confirmada"; I3: 4 estados con transiciones libres | **5 estados con tabla cerrada:** nueva, en revisión, requiere verificación, revisada, descartada. "Incierto" pasa a ser "requiere verificación". Sin "confirmada" | "Confirmada" choca con la base. La tabla cerrada se prueba con un AC por transición. "Verificada en campo" y "fusionada" quedan fuera del núcleo (RF-28 en Could) | RF-12, RD-11 |
| C-08a | Escala de la prioridad | I1: 0–100 + nivel; I3: solo nivel; I2: nada | **0–100 con nivel derivado** y 5 factores comunes a I1 e I3 | Sin fórmula (I3) la prioridad no es verificable; con 7 factores (I1) el costo es mayor y dos dependen de RADD | RF-09 |
| C-08b | ¿La incertidumbre baja la prioridad? | I3: es un factor; I1: no cambia el puntaje | **No es un factor**: se muestra como marca de confianza | Una zona dudosa pero grande dentro de la reserva debe revisarse igual; ocultar o hundir la duda iría contra la transparencia | RF-09, RF-13-AC-5 |
| C-08c | Referencia de la recencia | I1: hoy; I3: fin del periodo seleccionado | **Fecha de referencia (FR) registrada con cada puntaje**, igual a la fecha del cálculo | Con zonas persistentes, la prioridad es "hoy". Registrar la FR cumple el determinismo de I3: misma entrada y misma FR dan el mismo resultado. La comparación de periodos (RF-14) usa A y B, no la fecha actual | RF-09, RF-09-AC-12, AC-13 |
| C-08d | Factor sin datos | I3: "No disponible"; I1: no contemplado | **"No disponible" + reescalado** de los pesos disponibles | Sumar 0 por falta de una capa bajaría artificialmente la prioridad | RF-09, RF-09-AC-2 |
| C-09 | Modo offline / app de campo | I2: versión ligera offline con GPS; I1 e I3: fuera | **Fuera**. El campo se cubre con GeoPackage/KML para QField/Avenza (Should) | Una PWA offline con sincronización excede el curso; esas herramientas de campo ya existen | §1.2, RF-22 |
| C-10 | Notificaciones | I3: fuera; I1: solo indicadores internos; I2: avisar si una fuente cae | "Notificación" = mensaje **fuera** del sistema: fuera. Los avisos en la interfaz sí se permiten | Era sobre todo ambigüedad del término | §1.3, RF-07, RD-05 |
| C-11 | Nivel de autenticación | I1: TOTP obligatorio; I3: genérico; I2: no tiene | Contraseña con hash, sesión de 30 min, 401 en todo (Must); **TOTP y bloqueo, Should** | Cubre el riesgo real con poco costo; el 2FA queda planificado | RF-01, RF-02, RNF-03, RF-25 |
| C-12 | Quién configura umbrales y pesos | I2: Superadmin; I1: analistas con versión; I3: nadie | Parámetros fijos (PS-xx) en el núcleo; **pesos editables por analistas, Should**. Nunca automáticos | Menos superficie de API en el MVP | §2.4, RF-21, RD-03 |
| C-13 | Formatos y SRC de exportación | I1: 6 formatos con SRC; I2: "Shapefile o GeoJSON" sin SRC; I3: no exporta | **Must: CSV + GeoJSON (EPSG:4326)**. Should: GeoPackage/KML, PDF. Could: XLSX, Shapefile, PNG | Casi gratis con Python; cubre QGIS y Excel. GeoJSON en 4326 por el estándar RFC 7946 (I1 usaba 32719) | RF-16, RF-17, RF-22, RF-23, RF-32, RD-10 |
| C-14 | Guardado del análisis | I2: manual y privado; I3: automático; I1: por zona, 5 años | **Automático, visible para todos, inmutable, sin borrado** | El trabajo es de equipo; la retención de 5 años es operativa, no prueba del MVP | RF-14, RF-15 |
| C-15 | Combinar fuentes en una zona | I2 prohíbe un veredicto combinado; I1 agrupa por cercanía | **Se agrupa sin perder la fuente de cada alerta**, sin campo "veredicto" | No hay contradicción si cada alerta conserva su fuente | RF-04, RF-05, RF-19-AC-2 |
| C-16 | Unidad temporal | I1: fechas de imagen; I2 e I3: periodos | **Periodos** con las reglas de I3; en la vista de imágenes (Should), la de menor nubosidad de cada periodo | Coinciden dos de tres y la base ("comparar periodos"); conserva la trazabilidad de I1 | RF-14, RF-18 |
| C-17 | Índices espectrales | I2: NDVI + NDFI; I1: NDVI | **Solo NDVI** (Could); NDFI fuera | NDFI requiere desmezcla espectral, mucho más costosa | RF-27, §1.2 |

### 5.1 Conflictos introducidos por el SRS del Integrante 4

C-18 y C-23 los decidió el equipo sobre opciones concretas. Los demás siguen la recomendación del
addendum, revisada.

| ID | Conflicto | Posiciones | Decisión del equipo | Motivo | En el SRS |
|---|---|---|---|---|---|
| C-18 | Prioridad manual frente a calculada | I4: solo manual, sin justificación; I1 e I3: calculada + ajuste justificado; I3 e I4 ajustan por nivel | **Se mantiene el cálculo (RF-09)**. El ajuste se puede hacer **por puntaje o por nivel**: al subir, el mínimo del nivel; al bajar, el máximo. Siempre con justificación | La base pide que el sistema ayude a identificar qué revisar primero, y una prioridad solo manual no lo hace. El ajuste por nivel recoge la forma de trabajo de I3 e I4 sin romper el orden total de la lista. La justificación hace auditable la decisión | RF-11-AC-8 a AC-13 |
| C-19 | Roles: Especialista separado; Coordinador que asigna y gestiona prioridades | I4: 3 roles; equipo: 2 | **Se mantienen 2 roles.** La coordinación puede asignar responsables (RF-39), pero no fija prioridades | La base atribuye el trabajo a un mismo perfil; quien no es SIG no debe fijar prioridades. I4 se contradice sobre quién asigna | §2.3, RF-39 |
| C-20 | Estados ligados a la asignación; vuelta a "Pendiente" | I4: Pendiente/En revisión/Completado según asignación | **Se mantiene RF-12.** La asignación es un atributo independiente (RF-39) | El estado describe el avance, no quién revisa. "Descartada" cubre el falso positivo que el propio I4 define | RF-12, RF-39 |
| C-21 | "Notificación" interna de alta prioridad | I4: notificación a especialistas; equipo: notificación = externa | **Indicador** en RF-29: "pasó a nivel alta", una vez por cruce de umbral | Reutiliza un mecanismo existente y respeta el glosario; evita una bandeja de mensajes | RF-29-AC-2, AC-3, §1.3 |
| C-22 | Envío de credenciales al crear un usuario | I4: el sistema las envía; equipo: contraseña temporal entregada fuera del sistema | **Se mantiene RF-02**; el envío por correo queda en Won't | El correo saliente está fuera de alcance, y enviar contraseñas viola RNF-03 | RF-02, §1.2 |
| C-23 | Exportaciones (PDF, Shapefile, selección) | I4: PDF de varios cambios + Shapefile + GeoJSON de los seleccionados | **Shapefile sube a Should (RF-37)**; selección manual Could (RF-38); PDF por zona (RF-23); PDF de varias zonas Won't | El Shapefile lo piden 3 de 4, pero el núcleo Must ya es grande. El PDF de varias zonas multiplica la plantilla | RF-37, RF-38, RF-32-AC-2 (retirado) |
| C-24 | Filtros y orden | I4: 5 criterios, orden libre; equipo: nivel, estado, código | **RF-36 (Should)**, con "ubicación" definida como "dentro de la reserva" o "en la ZA". El orden por defecto no cambia | "Ubicación" era ambigua en I4. El orden por prioridad es el valor de la base | RF-36 |
| C-25 | Comunidades y "datos disponibles" de cada capa | I4: comunidades + "datos disponibles"; equipo: sin comunidades, sin titulares | **RF-35 (Should)** con nombre y código solamente. No se adoptan los "datos disponibles" | Los "datos disponibles" podrían exponer titulares (RD-04) o datos sensibles de comunidades | RF-35, TA-05 |
| C-26 | Rendimiento | I4: < 5 s, 500 cambios, 20 usuarios, 10 Mbps; equipo: 300 zonas, 1 Mbps | **RNF-05:** 500 zonas y 20 usuarios concurrentes, manteniendo **1 Mbps** | Se toma de I4 lo que endurece la prueba y se descarta lo que la relaja. 1 Mbps es la conexión real de Puerto Maldonado | RNF-05 |
| C-27 | Aprendizaje en 2 h | Solo I4 | **RNF-14 (Should)** con guion de tareas | Métrica valiosa, pero depende de reclutar usuarios | RNF-14 |
| C-28 | Legibilidad por escala | Solo I4 | **RNF-15 (Should)** con criterios observables | "Claridad" no es verificable; la escala sí | RNF-15 |
| C-29 | Comparación de imágenes (3 de 4 la piden) | I1, I2, I4 la quieren; equipo: Should | **Se mantiene en Should** y se agrega RF-18-AC-4 (misma extensión y escala) | El motivo de R-1 (riesgo de GEE) sigue en pie. Si el acceso a GEE se resuelve pronto, se puede subir una versión mínima | RF-18 |
| C-30 | Origen de los cambios y fuentes "privadas" | I4: no dice; "públicas y privadas" | **Se mantiene C-06**. La integración multifuente se cumple con alertas + capas de referencia. Las fuentes privadas se descartan | RNF-09 y RD-13 | RF-03, RF-04 |

---

## 6. Revisión crítica del análisis del agente

Se aceptó la estructura del análisis, la identificación de los 17 conflictos y la mayoría de las
recomendaciones. Se corrigieron estos puntos:

| # | Propuesta del agente | Decisión | Motivo |
|---|---|---|---|
| R-1 | Toda la comparación de periodos como **Should**, para no depender de GEE (§7.2) | **Se divide:** la comparación por datos de alertas es **Must** (RF-14); la de imágenes, Should (RF-18) | Comparar periodos está en los tres SRS y en la base. El riesgo real era GEE, y la comparación por alertas no lo usa |
| R-2 | Recencia: elegir entre "hoy" (I1) y "fin del periodo" (I3) | **Fecha de referencia registrada** (C-08c) | Las dos posiciones no se excluyen. Registrar la FR da determinismo sin atar la prioridad viva a un periodo |
| R-3 | Rol "administrador" genérico (§7.1, M2) | **Coordinación** con permisos de consulta + usuarios | Decisión del equipo (C-04): el perfil de I1 tiene sustento en la elicitación |
| R-4 | Marcas de confianza como **Should** | **Must** (RF-13), con dos marcas que no requieren imágenes | La incertidumbre visible es consenso de los tres SRS. Sin marcas, el núcleo no la expresaría |
| R-5 | "No disponible" por factor sin definir cómo afecta el puntaje | **Reescalado** sobre los pesos disponibles (C-08d) | Sin regla, el AC de I3 no es verificable |
| R-6 | GeoJSON con "SRC definido" sin elegir; I1 usaba EPSG:32719 | **EPSG:4326** (RD-10) | RFC 7946 exige WGS84; muchas herramientas ignoran otro SRC en GeoJSON |
| R-7 | "Lista en ≤ 5 s" como Must (M17) | **Should** (RNF-05) | Depende de pruebas con red limitada que no bloquean el flujo núcleo; el Must medible es RNF-04 (60 s) |
| R-8 | Addendum I4: ajuste solo por puntaje (C-18, opción 1) | **Puntaje o nivel** (opción 2), decidido por el equipo | El ajuste por nivel lo usan 2 de 4 SRS |
| R-9 | Addendum I4: el ajuste por nivel lleva siempre al **mínimo** del nivel elegido | Al subir, el mínimo; **al bajar, el máximo** (media = 69, baja = 39) | Bajar una zona de 75 a "media" la dejaría en 40, más abajo de lo que el analista pidió; el máximo del nivel es el cambio menor que cumple la decisión |
| R-10 | Addendum I4: retirar la parte "alto" de RF-11-AC-3 | **No se retira** | RF-11-AC-3 sigue siendo válido para el ajuste por puntaje ("alto" no es un número). El ajuste por nivel tiene sus propios criterios (AC-8 a AC-13) |

**Observación sobre el volumen.** El agente estimaba 60–90 AC para el núcleo. El SRS de equipo
tiene **166 AC en los 17 RF Must** (225 en total, incluido un AC retirado), porque se conservaron los casos límite de
umbrales, permisos y errores, que son los más baratos de automatizar y los que más defectos
encuentran. Si el equipo detecta que no es construible, la vía es **bajar RF completos a Should**
(p. ej., RF-13 o RF-15), no borrar AC sueltos (convención de IDs).

---

## 7. Requerimientos descartados (Won't) y por qué

| Requerimiento individual | Motivo |
|---|---|
| I2:RF-03 (tipo de cambio probable), I2:RF-04 (clasificación automática) | Contradicen la base (C-01) |
| I2:RF-01 (zona libre por nombre, coordenadas o polígono) | Ámbito fijo (C-03); el sistema trabaja con zonas de cambio, no con áreas arbitrarias |
| I2:RF-10 (Administrador institucional, Superadmin, visor externo) | Sin multiorganización (C-04) |
| I2:RNF-02 (modo offline con GPS) | C-09; se sustituye por RF-22 |
| I2:RNF-03 (restringir el detalle geoespacial por rol) | Sin sustento en la base; la protección se hace por tipo de dato (RD-04) y por autenticación (RNF-01) |
| I1:RF-05, I1:RF-06 (áreas de análisis dibujadas y guardadas) | La comparación es por zona y por periodo; el dibujo se usa solo en zonas manuales (RF-26) |
| I1:RF-16 (versiones de zona, revisión técnica o de contenido, ruta de urgencia) | Máquina de estados de 29 AC; fuera del núcleo |
| I1:RF-25, I1:RF-30, I1:RF-38, I1:RF-39 (expediente, supresión, registro de compartición, resumen mensual) | Fuera del núcleo; sin datos personales en el MVP |
| I1:RNF-07 (autoguardado ante cortes), I1:RNF-13 (ficha comprensible) | El primero tiene costo alto; el segundo depende de RF-23 (Should) |
| I1:RD-02, I1:RD-03, I1:RD-13 (reglas de la ficha y de compartición) | Dependen de funciones Won't; lo esencial de la ficha está en RF-23 |
| I1:RD-10 (consentimiento de comunidades) | La v1 no publica información (RD-05) |
| I1:RD-15 (plazo de 12 semanas) | Es una restricción del cliente simulado, no del curso |
| I2:RD-02 (alcance de series temporales) | Resuelto: dos periodos (RF-14); series completas, Won't |
| I4:RF-12-AC-1 (envío de credenciales al usuario nuevo) | C-22: correo saliente fuera de alcance y contraseñas en texto plano |
| I4:RF-13-AC-1 (reporte PDF de varios cambios) | C-23: la ficha es por zona (RF-23) |
| I4:RF-06 (prioridad solo manual, sin justificación) | C-18: se mantiene el cálculo y la justificación obligatoria |
| I4:RF-11 (estados según la asignación; vuelta a "Pendiente") | C-20 |
| I4:RF-12 (rol Especialista) | C-19 |
| I4:RF-04-AC-2 ("datos disponibles" de cada capa) | C-25: riesgo de exponer titulares |

---

## 8. Tabla de correspondencia de IDs

**¿Por qué una numeración nueva?** Ningún esquema individual servía como base común: los números
chocan entre documentos, I2 no tiene IDs de AC y la numeración de I1 tiene huecos (RF-24 y RF-26
retirados) y 40 RF. El equipo decidió una **numeración nueva y congelada**, ordenada por bloque
funcional y por prioridad (Must RF-01 a RF-17, Should RF-18 a RF-26, Could RF-27 a RF-33). Los
IDs individuales **no se usan** en artefactos de equipo. Esta tabla permite rastrear el origen de
cada requerimiento.

### 8.1 Integrante 1

| I1 | Equipo | | I1 | Equipo |
|---|---|---|---|---|
| RF-01 | RF-06 (15 → 6 capas) | | RF-21 | RF-33 |
| RF-02 | RF-07 | | RF-22 | RF-02, RF-30 |
| RF-03 | RF-03 (4 tipos de capa) | | RF-23 | RF-27 |
| RF-04 | RF-29 | | RF-24 | — (retirado en I1) |
| RF-05, RF-06 | Won't | | RF-25 | Won't |
| RF-07, RF-08 | RF-18 | | RF-26 | — (retirado en I1) |
| RF-09 | RF-05 (área), RF-27 | | RF-27 | RF-24 |
| RF-10 | RF-08 | | RF-28 | RF-01, RF-02, RF-25 |
| RF-11 | RF-12 | | RF-29 | RF-18, RNF-04 |
| RF-12 | RF-10, RF-30 | | RF-30 | Won't |
| RF-13 | RF-26 | | RF-31 | RF-04, RF-19 |
| RF-14 | RF-31 | | RF-32 | RF-05, RF-28 |
| RF-15 | RF-14, RNF-07 | | RF-33 | RF-09 |
| RF-16 | Won't | | RF-34 | RF-11 |
| RF-17 | RF-23 | | RF-35 | RF-21 |
| RF-18 | RF-17, RF-32 | | RF-36 | RF-13, RF-18 |
| RF-19 | RF-16, RF-32 | | RF-37 | RF-20 |
| RF-20 | RF-24 | | RF-38, RF-39 | Won't |
| | | | RF-40 | RF-22 |

| I1 | Equipo | | I1 | Equipo |
|---|---|---|---|---|
| RNF-01 | RNF-01 | | RD-01 | RD-10 |
| RNF-02 | RNF-02 | | RD-02, RD-03 | RF-18, RF-23 (parcial) |
| RNF-03 | RNF-03, RF-25 | | RD-04, RD-05, RD-06 | RD-06 |
| RNF-04 | RF-24 | | RD-07 | RD-07, RD-09 |
| RNF-05 | RNF-04 | | RD-08 | RD-09 |
| RNF-06, RNF-08 | RNF-05 | | RD-09 | RD-12 |
| RNF-07 | Won't | | RD-10 | Won't |
| RNF-09 | RNF-13 | | RD-11 | RNF-01, RD-05 (parcial) |
| RNF-10 | RNF-11 | | RD-12 | RD-13 |
| RNF-11 | RNF-09 | | RD-13 | Won't |
| RNF-12 | RNF-10 | | RD-14 | RD-01 |
| RNF-13 | Won't | | RD-15 | Won't |
| RNF-14 | RNF-06 | | RD-16 | RF-23 |
| RNF-15 | RNF-12 | | RD-17 | RD-02 |
| | | | RD-18 | RD-04 |
| | | | RD-19 | RD-05 |

### 8.2 Integrante 2

| I2 | Equipo |
|---|---|
| RF-01 | RF-14 (periodos), RF-18 (lado a lado), RF-32 (slider); zona libre: Won't |
| RF-02 | RF-14-AC-10 ("sin cambios"); capa de diferencia ráster: RF-27 (parcial) |
| RF-03 | RF-08 (contexto), RF-13 (confianza), RF-14 (diferencia de área); "tipo de cambio probable": Won't |
| RF-04 | Persistencia → factor de RF-09; NDVI → RF-27; umbrales configurables → RF-21; clasificación: Won't |
| RF-05 | RF-08 (sin "legal-administrativo"), RF-07 (capa no disponible) |
| RF-06 | RF-04, RF-19-AC-2, RF-31 |
| RF-07 | RF-16, RF-17, RF-23, RF-32; guardar comparación → RF-14, RF-15 |
| RF-08 | RF-12 (sin "confirmada") |
| RF-09 | RF-12 (AC-15, AC-16) |
| RF-10 | §2.3, RF-02 (2 roles) |
| RF-11 | RF-07, RNF-08 |
| RNF-01 | RNF-08 |
| RNF-02 | RF-22 (alternativa); offline: Won't |
| RNF-03 | Won't |
| RNF-04 | RF-13, RD-09 |
| RD-01 | RD-07 |
| RD-02 | Resuelto en RF-14 |
| RD-03 | RD-08 |

### 8.3 Integrante 3

| I3 | Equipo | | I3 | Equipo |
|---|---|---|---|---|
| RF-01 | RF-01 | | RF-11 | RF-15 |
| RF-02 | RF-14 (AC-1 a AC-6) | | RNF-01 | RNF-06 |
| RF-03 | RF-04, RF-05 (origen); RF-14 (AC-10 a AC-12); RD-01; RD-09 | | RNF-02 | RNF-07 |
| RF-04 | RF-06 | | RNF-03 | RNF-04 |
| RF-05 | RF-08 | | RNF-04 | RNF-01 |
| RF-06 | RF-09 (AC-5, AC-12), RF-10 | | RNF-05 | RNF-08 |
| RF-07 | RF-09 (AC-2, AC-14, AC-15); recencia: C-08c | | RD-01 | RD-09 |
| RF-08 | RF-11 | | RD-02 | RD-09, RF-12 |
| RF-09 | RF-12 (Pendiente → nueva; Incierto → requiere verificación; Revisado → revisada) | | RD-03 | RD-02 |
| RF-10 | RF-14 (AC-13, AC-14) | | RD-04 | RD-03 |
| | | | RD-05 | RD-01 |

### 8.4 Integrante 4

| I4 | Equipo |
|---|---|
| RF-01 | RF-03, RF-04, RF-06 (fuentes integradas en el mapa); fuentes privadas: no (C-30) |
| RF-02 | RF-14 (periodos), RF-18 + RF-18-AC-4 (imágenes con la misma extensión y escala) |
| RF-03 | RF-05 (área), RF-06, RF-10, RF-14 (fechas) |
| RF-04 | RF-08 (contexto), RF-35 (comunidades); "datos disponibles": no (C-25) |
| RF-05 | RF-34 |
| RF-06 | RF-11 (ajuste por nivel, AC-8 a AC-13), RF-09 (cálculo) |
| RF-07 | RF-12 (AC-15, AC-19, AC-20) |
| RF-08 | RF-10 (nivel, estado), RF-36 (fecha, área, ubicación, orden) |
| RF-09 | RF-29 (AC-2, AC-3) |
| RF-10 | RF-10 (filtro de estado "nueva"; AC-10, color de nivel) |
| RF-11 | RF-12 (estados), RF-39 (asignación) |
| RF-12 | RF-02, §2.3; rol Especialista: no (C-19); envío de credenciales: no (C-22) |
| RF-13 | RF-17 (GeoJSON), RF-37 (Shapefile), RF-23 (PDF por zona), RF-38 (selección) |
| RNF-01 | RNF-05 |
| RNF-02 | RNF-14 |
| RNF-03 | RNF-15 |
| RNF-04 | RNF-01, RNF-02, RF-24 |
| RD-01 | RD-01 |
| RD-02 | RD-02 |
| RD-03 | RD-03, PS-04 |

---

## 9. Temas abiertos

Son los mismos de `SRS_equipo.md`, §2.4:

- **TA-01:** calibrar pesos y normalizaciones.
- **TA-02:** fuente oficial de la capa de ríos.
- **TA-03:** Ley N.º 29733 si se agregan reportes de campo.
- **TA-04:** validar el núcleo con un analista real, porque todas las entrevistas de S02-A1 fueron
  simuladas.
- **TA-05:** fuente oficial y licencia de la capa de comunidades nativas.

---

## 10. Ratificación del equipo

Cada integrante revisa `SRS_equipo.md` y las decisiones de la sección 5, y marca su conformidad. Un
desacuerdo se registra aquí con la propuesta alternativa y se resuelve antes de S04-A2 (diseño de
la API).

| Integrante | Revisó el SRS de equipo | Conforme con C-01 a C-30 | Observaciones |
|---|:---:|:---:|---|
| Integrante 1 — Miguel Angel Arevalo Andrade | ☑ | ☑ | Propuso las decisiones de la sección 5 a partir de los análisis del agente |
| Integrante 2 — *[nombre]* | ☐ | ☐ | |
| Integrante 3 — *[nombre]* | ☐ | ☐ | |
| Integrante 4 — *[nombre]* | ☐ | ☐ | En especial C-18 a C-30, que responden a su SRS |
