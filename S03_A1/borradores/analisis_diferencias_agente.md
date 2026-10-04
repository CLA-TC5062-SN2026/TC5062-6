# Análisis de diferencias entre los SRS individuales — EcoAlert

> **Borrador generado por un agente** (analista de requerimientos) como insumo para consolidar el
> SRS de equipo. No es el SRS consolidado. Debe revisarse críticamente antes de usarse.

**Insumos comparados**

| Prefijo | Archivo | Tamaño |
|---|---|---|
| I1 | `insumos/SRS_integrante1_A01840503.md` (v3.0, 2026-09-27) | ~1,460 líneas |
| I2 | `insumos/SRS_integrante2.md` (v1.0, 27/09/2026) | ~210 líneas |
| I3 | `insumos/SRS_integrante3.md` (sin versión ni fecha) | ~440 líneas |
| Base | `insumos/proyecto_base.md` | referencia de alcance acordado |

**Convención.** Los IDs no coinciden entre documentos (p. ej., `I1:RF-05` es "definición del área
de análisis", `I2:RF-05` es "cruce con concesiones" e `I3:RF-05` es "contexto territorial"). Por
eso la comparación es por **contenido** y todo ID lleva el prefijo del integrante. "AC" = criterio
de aceptación.

**Puntos de la base usados para juzgar el alcance** (`proyecto_base.md`):

- B1. Ámbito: **Reserva Nacional Tambopata** (presiones por pérdida de cobertura y minería ilegal).
- B2. Usuarios: **analistas ambientales y especialistas SIG**.
- B3. Valor: identificar **qué zonas requieren revisión prioritaria**, con información
  **comprensible y contextualizada**, **comparando periodos**.
- B4. **Sin determinar automáticamente las causas**; la interpretación y la decisión final son del
  especialista.

---

## 1. Resumen de cada SRS

### 1.1 Integrante 1 (I1)

| Aspecto | Contenido |
|---|---|
| Base y alcance | App web para una ONG de Puerto Maldonado que colabora con la jefatura de la RN Tambopata. **Ingiere alertas** de GeoBosques (carga de archivos) y RADD (vía GEE), las **agrupa en "zonas de cambio"** (≤ 500 m, ≤ 90 días), las **prioriza** con un puntaje 0–100 de 7 factores con desglose, marca la confianza sin ocultar, permite un **análisis detallado** de dos fechas con candidatos NDVI semiautomáticos, gestiona estados y **versiones**, genera una **ficha PDF** con huella SHA-256, exporta (GeoJSON, Shapefile, CSV, XLSX, GeoPackage, KML, expediente ZIP) y **registra comparticiones** (no envía nada). Fuera: funciones legales, causas, notificaciones por correo, app móvil/offline, otras ANP, GLAD (Could). |
| Roles | 2 roles, 3 usuarios: **Analista SIG** (todo lo operativo) y **Coordinación** (no SIG: consulta, revisión de contenido de fichas, usuarios/sectores, bitácora). Matriz rol × acción con 403 en servidor (`I1:§2.3`, `I1:RNF-02`). SERNANP y guardaparques sin cuenta. |
| Cantidades | **38 RF activos** (RF-01…RF-40; `I1:RF-24` y `I1:RF-26` retirados): 30 Must, 7 Should, 1 Could. **15 RNF**, **19 RD**. 28 parámetros del sistema (S-01…S-28). **452 AC**. |
| Formato de AC | Given-When-Then ("Dado que / cuando / entonces") con **ID único e inmutable** `RF-xx-AC-n`, valores concretos, tipo de verificación marcado (API, *E2E de interfaz*, *aceptación manual*). RNF con método de verificación (prueba / inspección / demostración). |
| ¿Respeta la base? | **Sí** en B1, B3 y B4 (`I1:RD-14`, `I1:RD-17`, `I1:RF-33`). Amplía B2 con un rol de Coordinación no SIG y con destinatarios externos (jefatura), coherente pero fuera de lo que la base menciona. El riesgo no es de alineación sino de **tamaño**: alcance de producto completo (plazo propio de 12 semanas en `I1:RD-15`). Depende de documentos no compartidos con el equipo (entrevistas Sección A/B/C, casos de uso, borradores). |

### 1.2 Integrante 2 (I2)

| Aspecto | Contenido |
|---|---|
| Base y alcance | "Sistema de monitoreo satelital" genérico: el usuario **selecciona una zona de interés** (nombre, coordenadas o polígono) y **dos periodos**, el sistema genera una **capa de diferencia**, **clasifica automáticamente el tipo de cambio** (NDVI/NDFI, ≥ 2 lecturas consecutivas), lo cruza con **concesiones mineras (INGEMMET)** y áreas protegidas, mantiene historial con estados y permite exportar. Usuarios: "investigadores, especialistas ambientales e **instituciones** de gestión territorial". Fuera: Visor externo, series temporales completas, app nativa (pero sí una "versión ligera offline"). |
| Roles | 3 roles en el MVP: **Investigador/Analista**, **Administrador institucional** (usuarios de su organización y zonas prioritarias), **Superadmin** (configuración global y fuentes). Visor externo para fase futura (`I2:RF-10`). |
| Cantidades | **11 RF**, **4 RNF**, **3 RD** (las RD-01…RD-03 se repiten en §2.4). Sin prioridad MoSCoW. 41 AC en total (sin ID). |
| Formato de AC | Viñetas "El sistema debe…", **sin IDs** y **mayormente sin Given-When-Then** (solo algunos empiezan con "Dado que" sin "cuando/entonces"). Trazabilidad a la entrevista con el PO ("Evidencia: P1…P10"). RNF sin métricas ni método de verificación. |
| ¿Respeta la base? | **Parcialmente / no.** Contradice **B4**: muestra "posible causa" (§1.2), "tipo de cambio probable: … **posible minería**" (`I2:RF-03`) y clasificación automática (`I2:RF-04`), y un "contexto legal-administrativo" (`I2:RF-03`, `I2:RF-05`). **No menciona Tambopata** (B1): la zona la elige el usuario libremente. **No tiene priorización** (B3: "zonas que requieren revisión prioritaria"). Amplía B2 a instituciones/multiorganización. Sí respeta la comparación de periodos (B3) y la decisión final humana en la confirmación/descarte (`I2:§2.1`, `I2:RF-09`). |

### 1.3 Integrante 3 (I3)

| Aspecto | Contenido |
|---|---|
| Base y alcance | "EcoAlert Tambopata": plataforma web limitada a la **RN Tambopata y su zona de amortiguamiento**. El especialista elige **dos periodos válidos**; el sistema identifica **zonas candidatas**, las muestra en mapa con su **contexto territorial** (incluida la distancia a recursos hídricos), genera una **prioridad sugerida Alta/Media/Baja** (o "No disponible") a partir de **6 factores** siempre visibles, permite modificarla con justificación, registra el **estado de revisión** y **almacena cada análisis** automáticamente. Fuera: minería ilegal automática, gestión documental, notificaciones automáticas, app móvil, todo el Perú. |
| Roles | **Un solo rol**: Especialista ambiental / SIG. Solo autenticación (`I3:RF-01`, `I3:RNF-04`), sin autorización por roles. |
| Cantidades | **11 RF**, **5 RNF**, **5 RD**. Sin prioridad MoSCoW. **32 AC**. |
| Formato de AC | Given-When-Then con **IDs `RF-XX-AC-Y`** (encabezados `#####`), un comportamiento por criterio. RNF sin método de verificación (solo `I3:RNF-03` tiene métrica). Fuentes genéricas ("Elicitación con stakeholders…"). |
| ¿Respeta la base? | **Sí, es el más fiel a la letra de la base** (B1: `I3:RD-05`, `I3:RF-03-AC-4`; B2: §2.3; B3: `I3:RF-06`–`I3:RF-08`; B4: `I3:RD-03`, `I3:RD-04`). Su debilidad es la **subespecificación**: no dice de qué fuentes salen las zonas candidatas ni cómo se calcula la prioridad, y no tiene exportación. |

### 1.4 Vista rápida

| | I1 | I2 | I3 |
|---|---|---|---|
| Entidad central | Zona de cambio persistente (agrupa alertas) + versiones | Zona de interés elegida por el usuario + comparación | Análisis (dos periodos) que contiene zonas candidatas |
| Origen de los cambios | Alertas ingeridas (GeoBosques, RADD) + candidatos NDVI validados por el analista | Detección automática propia por umbral NDVI/NDFI | No especificado ("identifica zonas candidatas") |
| Priorización | 0–100, 7 factores ponderados, niveles | **No tiene** | Alta/Media/Baja/No disponible, 6 factores |
| Causas | Prohibido (`I1:RD-17`) | **Clasifica "posible minería"** | Prohibido (`I3:RD-03`) |
| Ámbito | Tambopata + ZA, rechaza lo de fuera | Libre | Tambopata + ZA |
| Roles | 2 | 3 (+1 futuro) | 1 |

---

## 2. Consenso (presente en los tres)

| Tema | I1 | I2 | I3 | Observaciones sobre diferencias de detalle |
|---|---|---|---|---|
| Aplicación web usable sin programar | `I1:§2.1`, `I1:§2.3` ("no programan"), `I1:RNF-14` | `I2:§2.1`, `I2:§2.3` ("no requiere programar") | `I3:§2.3`, `I3:RNF-01` | I3 lo expresa como RNF ("sin escribir código, comandos ni consultas geoespaciales"); I1 y I2 solo en el perfil de usuario. I1 agrega idioma español y responsive (`I1:RNF-09`). |
| Comparación de dos fechas/periodos | `I1:RF-07` (dos **fechas** de imagen elegidas libremente), `I1:RF-08` (listado por rango), `I1:RD-08` (mismo mes del año anterior) | `I2:RF-01` (Periodo A y B como **rangos**, lado a lado o slider) | `I3:RF-02` (dos **periodos**, inicio ≤ fin, distintos, **no superpuestos**, un día válido) | Difiere la unidad: fecha de imagen (I1) vs. rango (I2, I3). Solo I3 define reglas de validez; solo I2 exige slider; I1 exige lado a lado sincronizado y falso color. En I1 la comparación es el *análisis detallado de una zona*, no el punto de partida. |
| Identificación de zonas/áreas con cambio | `I1:RF-31`, `I1:RF-32` (alertas agrupadas), `I1:RF-23` (candidatos NDVI) | `I2:RF-02` (capa de diferencia), `I2:RF-04` (clasificación) | `I3:RF-03` (zonas candidatas) | Método totalmente distinto (ver **C-05**, **C-06**). Solo I1 especifica el algoritmo; I3 no lo especifica. |
| Visualización en mapa | `I1:RF-01` (15 capas activables, color por nivel) | `I2:RF-02` (capa de diferencia activable sin recalcular) | `I3:RF-04` (ubicación de cada zona) | I1 y I2 coinciden en activar/desactivar capas sin recargar (`I1:RF-01-AC-2`, `I2:RF-02-AC-2`). I3 es el mínimo. |
| Contexto territorial / superposición con área protegida | `I1:RF-10` (reserva, ZA, catastro, concesiones forestales, de conservación, comunidades; distancia a río y vía) | `I2:RF-05` (dentro/fuera de concesión activa y área protegida) | `I3:RF-05` (posición respecto a la reserva y ZA; distancia a recurso hídrico) | Coinciden en ubicar el cambio respecto al área protegida. Difiere la amplitud de capas y el tratamiento de concesiones (ver **C-02**). |
| Estado de revisión e historial de la zona | `I1:RF-11` (7 estados con tabla de transiciones, comentario/motivo obligatorio, usuario y fecha) | `I2:RF-08`, `I2:RF-09` (nueva, en revisión, confirmada, descartada; registra quién y cuándo) | `I3:RF-09` (Pendiente, En revisión, Incierto, Revisado; transiciones libres; observación opcional) | Conjuntos de estados incompatibles (ver **C-07**). I3 no registra usuario ni fecha del cambio de estado. |
| Decisión final humana | `I1:§1.2`, `I1:RF-23` (el analista acepta/edita/descarta), `I1:RF-34` | `I2:§2.1` ("un usuario experto tome la decisión final"), `I2:RF-09` | `I3:§1.2`, `I3:RD-04` | En I2 la clasificación de tipo de cambio sí es automática; solo la confirmación es humana (ver **C-01**). |
| Comportamiento ante fuentes externas caídas o insuficientes | `I1:RF-02-AC-4` (muestra la última sincronización exitosa), `I1:RF-31` (conserva alertas, reintento), `I1:RF-29` (estado "fallido" y reintento), `I1:RF-15-AC-4` | `I2:RF-11` (aviso visible, caché marcada como desactualizada), `I2:RNF-01`, `I2:RF-05-AC-4` | `I3:RF-03-AC-3`, `I3:RNF-05`, `I3:§2.4` (no presentar como concluido) | Principio común: **no ocultar ni presentar como vigente**. I2 es el único con caché explícita; I1 lo resuelve con fechas de corte y reintento; I3 solo exige informar. |
| Calidad de la evidencia: nubes, sombras, estacionalidad | `I1:RF-08` (nubosidad en el área), `I1:RF-36` (marcas), `I1:RD-07`, `I1:RD-08` | `I2:RF-04` (≥ 2 lecturas por nubosidad), `I2:RNF-04` (nubes, sombras, cultivos estacionales) | `I3:RD-01`, `I3:RF-03-AC-5` (limitaciones registradas y mostradas) | I1 lo hace verificable (S-01 = 20 %, umbral de validez); I2 lo resuelve filtrando (no genera alerta); I3 lo registra como "limitaciones conocidas". |
| Incertidumbre visible / nivel de confianza | `I1:RF-36` (marcas de confianza que no ocultan) | `I2:RF-03` (campo "nivel de confianza"), `I2:RF-04-AC-3` (evento "no confirmado") | `I3:RD-02` (estado Incierto), `I3:RF-07` (factor "calidad o incertidumbre") | Tres representaciones distintas: marcas (I1), valor numérico (I2), estado + factor de prioridad (I3). Ver **C-08** (si la incertidumbre afecta o no la prioridad). |
| Persistencia temporal del cambio como criterio | `I1:RF-33` (factor "persistencia y crecimiento", 8 ventanas de 7 días) | `I2:RF-04` (≥ 2 lecturas consecutivas para generar alerta) | `I3:RF-07` (factor "persistencia temporal") | En I2 es un **filtro** (sin persistencia no hay alerta); en I1 e I3 es un **factor de prioridad**. |
| Trazabilidad de fuentes y periodos | `I1:RF-15` (reproducibilidad completa), `I1:RF-02`, `I1:RD-06` | `I2:RF-06` (fuente identificable), `I2:RF-07-AC-3` (exportación conserva zona, periodos y fecha) | `I3:RNF-02`, `I3:RF-10` | I1 exige reproducir la misma cifra (IDs de imagen, versiones de capas); I3 exige fuentes, periodos y limitaciones; I2 solo la fuente visible. |
| Conservación del trabajo para consulta posterior | `I1:RF-15`, `I1:RF-16` (versiones inmutables), `I1:RNF-10` (5 años) | `I2:RF-07` (guardar comparación), `I2:RF-08` | `I3:RF-10` (almacenamiento automático), `I3:RF-11` (lista de análisis) | Modelos de datos distintos (ver **C-05**). I2 requiere acción del usuario para guardar; I3 lo hace automáticamente; I1 por zona y versión. |
| Acceso restringido | `I1:RNF-01` (todo requiere autenticación, 401), `I1:RF-28`, `I1:RNF-03` | Implícito en `I2:RF-09-AC-4` y `I2:RF-10` (roles, acceso denegado) | `I3:RF-01`, `I3:RNF-04` | **I2 no tiene un RF ni RNF de autenticación** aunque define roles. Nivel de exigencia muy distinto (ver **C-11**). |

---

## 3. Consenso parcial (presente en dos de tres)

| Tema | I1 | I2 | I3 | Falta | Observaciones |
|---|---|---|---|---|---|
| Priorización de zonas | `I1:RF-33` | — | `I3:RF-06`, `I3:RF-07` | **I2** | Es el valor principal de la base (B3) y **I2 no lo tiene**. Escala y factores distintos (ver **C-08**). |
| Lista ordenada por prioridad | `I1:RF-12` (puntaje desc., desempates definidos, filtros, conteos) | — | `I3:RF-06-AC-4`, `I3:RF-08-AC-3` (Alta > Media > Baja, sin orden dentro del nivel) | I2 | I1 define desempate total; I3 lo deja libre. |
| Factores de prioridad siempre visibles | `I1:RF-33` (desglose en puntos y texto en lista, detalle y ficha) | — | `I3:RF-07` (6 factores con valor o "No disponible") | I2 | Ambos coinciden en no ocultar factores. Solo I3 trata el factor sin datos. |
| Modificación manual de la prioridad con justificación | `I1:RF-34` (puntaje ajustado 0–100, comentario obligatorio, se puede quitar) | — | `I3:RF-08` (otro nivel, justificación obligatoria, conserva la sugerida) | I2 | Concuerdan en conservar lo sugerido y lo elegido. Difieren en la escala (puntaje vs. nivel) y en el alcance (zona viva vs. zona dentro de un análisis). |
| Proximidad a ríos / recursos hídricos | `I1:RF-10` (distancia en m al río y a la vía), `I1:RF-33` (factor), `I1:RF-36` (dinámica fluvial) | — | `I3:RF-05` (distancia mínima en m, "Información no disponible"), `I3:RF-07` (factor) | I2 | Coinciden en distancia mínima en metros. Solo I3 especifica qué mostrar sin capa hídrica. |
| Ámbito RN Tambopata + zona de amortiguamiento | `I1:RD-14`, `I1:RF-05` (rechazo/recorte) | — | `I3:RD-05`, `I3:RF-03-AC-4` | **I2** | I2 deja el ámbito libre (ver **C-03**). |
| Prohibición explícita de atribuir causa o legalidad | `I1:RD-17`, `I1:RF-23-AC-17`, `I1:RD-16` | — (lo contradice) | `I3:RD-03`, `I3:§1.2` | **I2** | Ver **C-01**. |
| Prioridad como recomendación | `I1:§1.2`, `I1:RF-35` ("nunca reajusta solo") | — | `I3:RD-04` | I2 | Sin conflicto entre I1 e I3. |
| Comentario u observación en la revisión | `I1:RF-11` (obligatorio en varias transiciones) | — | `I3:RF-09-AC-3` (opcional) | I2 | Difiere la obligatoriedad (ver **C-07**). |
| Registro de quién y cuándo cambió el estado | `I1:RF-11-AC-24` | `I2:RF-09-AC-2` | — | **I3** | I3 solo conserva el estado y la observación. |
| Exportación de resultados geoespaciales | `I1:RF-18` (GeoJSON, Shapefile EPSG:32719), `I1:RF-19` (CSV/XLSX), `I1:RF-40` (GeoPackage/KML EPSG:4326), `I1:RF-25`, `I1:RF-17` (PDF) | `I2:RF-07` (reporte, imagen, Shapefile o GeoJSON) | — | **I3** | Común mínimo: **GeoJSON/Shapefile**. I2 no fija el SRC. Ver **C-13**. |
| Cruce con catastro minero (INGEMMET) | `I1:RF-10` (tipo de derecho, código, estado; sin titular), `I1:RD-06` (fecha de corte) | `I2:RF-05` (dentro/fuera de concesión activa) | — | I3 | Ver **C-02** (titulares, lenguaje "legal-administrativo"). |
| Discrepancias entre fuentes | `I1:RF-14` (nota de discrepancia separada del dato oficial), `I1:RD-04` | `I2:RF-06` (mostrar cada fuente por separado, no fusionar en un veredicto) | — | I3 | Enfoques distintos: I1 trata discrepancia equipo vs. fuente oficial; I2 entre fuentes. Ver **C-15**. |
| Roles diferenciados con permisos | `I1:§2.3`, `I1:RNF-02` | `I2:RF-10` | — (un solo rol) | I3 | Ver **C-04**. |
| Gestión de usuarios | `I1:RF-22` (coordinación) | `I2:RF-10` (Admin institucional) | — | I3 | Quién la hace difiere. |
| Umbrales de detección configurables | `I1:RF-08` (umbral de visualización), `I1:RF-23-AC-6` (umbral NDVI por análisis), `I1:RF-35` (pesos) | `I2:RF-04-AC-4` (umbrales NDVI/NDFI por Superadmin) | — | I3 | Ver **C-12**. |
| App móvil fuera de alcance | `I1:§1.2` (móvil y offline fuera; campo vía exportaciones `I1:RF-40`) | — (pide versión ligera offline, `I2:RNF-02`) | `I3:§1.2` | — | I1 e I3 coinciden; I2 discrepa (ver **C-09**). |
| Notificaciones externas fuera de alcance | `I1:§1.2`, `I1:RF-37` (no correos; indicadores en la app) | — | `I3:§1.2` ("Notificaciones automáticas") | — | I2 pide avisos de fuente caída (`I2:RF-11`); ver **C-10**. |
| Límite de resolución espacial | `I1:RD-07` (10 m Sentinel-2; Landsat complemento), `I1:S-09` (0.5 ha mínimo) | `I2:RD-01` (0.5–1 ha) | — | I3 | Coinciden en ~0.5 ha. |
| Desfase temporal de las fuentes | `I1:RF-36` (marca "desfase de fechas" > 60 días entre alerta e imagen) | `I2:RD-03` (1–4 semanas respecto al evento) | — | I3 | Conceptos distintos pero complementarios. |
| Protección de información sensible | `I1:RD-09`, `I1:RD-11`, `I1:RD-18`, `I1:RF-21` (seudónimos, EXIF), `I1:RF-39` (sin coordenadas) | `I2:RNF-03` (restringir detalle geoespacial por rol para proteger comunidades y propiedad privada) | — | I3 | I2 propone ocultar coordenadas por rol; I1 restringe por tipo de dato y no por rol (ver **C-04**). |
| Rendimiento con métrica | `I1:RNF-05` (≤ 5 min p90 para 2,000 ha, en segundo plano), `I1:RNF-08` (≤ 5 s a 1 Mbps) | — | `I3:RNF-03` (resultado, **estado de procesamiento** o error en ≤ 60 s) | I2 | **Compatibles**: I3 exige retroalimentación en 60 s; I1 ejecuta en segundo plano con estados visibles (`I1:RF-29`). Conviene adoptar ambos. |
| Selección/guardado de un área de análisis | `I1:RF-05`, `I1:RF-06` (polígono o radio alrededor de alerta, guardar con nombre) | `I2:RF-01` (nombre, coordenadas o polígono), `I2:RF-07` (guardar comparación) | — | I3 | I3 analiza todo el ámbito; no hay selección de área. |
| Vista lado a lado de dos imágenes | `I1:RF-07-AC-2`, `I1:RF-07-AC-3` | `I2:RF-01-AC-3` (además slider) | — | I3 | Slider solo en I2. |

---

## 4. Gaps (presentes en un solo SRS)

### 4.1 Solo en I1

| Tema | Integrante | IDs | ¿Incorporarlo? (justificación) |
|---|---|---|---|
| Ingesta de alertas GeoBosques (archivo) y RADD (GEE) | I1 | `I1:RF-31` | **Sí (GeoBosques Must, RADD Should).** Resuelve el hueco de I3 (de dónde salen las zonas) sin construir un detector propio. RADD agrega riesgo de integración con GEE. |
| Agrupación de alertas en zonas (500 m / 90 días) y fusión | I1 | `I1:RF-32` | **Sí, simplificado.** Es la base de la priorización. La fusión de zonas y el historial del lugar (3 años) pueden quedar en Should/Could. |
| Reapertura automática de zonas cerradas | I1 | `I1:RF-37` | **Should.** Valioso para el dominio (frentes que avanzan), pero depende de la agrupación. |
| "Nuevas desde tu última revisión" por usuario | I1 | `I1:RF-04` | **Could.** Útil, no esencial para demostrar el flujo. |
| Capas de referencia versionadas con fecha de corte | I1 | `I1:RF-02`, `I1:RF-03`, `I1:RD-06` | **Sí, versión mínima** (carga con fuente y fecha de corte). El versionado histórico completo puede ser Should. |
| 15 capas de mapa | I1 | `I1:RF-01` | **Parcial.** Núcleo: reserva, ZA, zonas, alertas, ríos, catastro minero. Resto Could. |
| Definición de área con recorte al ámbito y límites de superficie | I1 | `I1:RF-05` | **Sí si se adopta el análisis detallado**; los límites (10,000 ha, radio 0.5–5 km) son baratos de validar. |
| Listado de imágenes con nubosidad en el área | I1 | `I1:RF-08` | **Should.** Depende de GEE. |
| Cálculo de área en EPSG:32719 | I1 | `I1:RF-09` | **Sí.** Barato y alimenta el factor "extensión" que I3 también pide. |
| Candidatos NDVI semiautomáticos | I1 | `I1:RF-23` | **Could.** Alto costo (ráster, GEE, calibración S-10 en semanas 4–6). El analista puede trazar polígonos a mano. |
| Versiones de zona, revisión técnica / de contenido, ruta de urgencia | I1 | `I1:RF-16` | **Could/Won't para el MVP.** Máquina de estados compleja (29 AC); depende de un rol de Coordinación que I2 e I3 no tienen. |
| Ficha PDF con huella SHA-256 y verificación | I1 | `I1:RF-17` | **Should, versión simple** (PDF sin ciclo de versiones). La huella es barata; la plantilla completa no. |
| Exportación de lista CSV/XLSX | I1 | `I1:RF-19` | **Sí (CSV Must, XLSX Could).** Barato y muy útil para analistas (Excel). |
| Registro de exportaciones y comparticiones | I1 | `I1:RF-20`, `I1:RF-38` | **Should** (registro simple). Compartición con reglas de versión: Could. |
| Reportes de campo con seudónimo y EXIF | I1 | `I1:RF-21` | **Could.** Implica manejo de fotos y datos personales. |
| Sectores y cuencas | I1 | `I1:RF-22`, `I1:RF-12` | **Could.** Filtro organizativo, no núcleo. |
| Expediente ZIP | I1 | `I1:RF-25` | **Could/Won't.** |
| Bitácora de auditoría de solo inserción | I1 | `I1:RF-27`, `I1:RNF-04` | **Should, versión mínima** (tabla insert-only de acciones clave); el registro de cada consulta es Could. |
| TOTP obligatorio, bloqueo, ciclo de credenciales | I1 | `I1:RF-28`, `I1:RNF-03` | **Parcial.** Contraseña con hash + expiración de sesión: Must. TOTP: Should (ver **C-11**). |
| Estados del análisis (en cola, en curso, terminado, fallido) | I1 | `I1:RF-29` | **Sí si hay análisis con GEE.** Además satisface `I3:RNF-03`. |
| Supresión de datos personales (Ley 29733) | I1 | `I1:RF-30` | **Won't en el MVP** si no hay reportes de campo con fotos. |
| Pesos configurables y versionados | I1 | `I1:RF-35` | **Should.** Pesos fijos en configuración bastan para el MVP; versionarlos es Should. |
| Marcas de confianza automáticas | I1 | `I1:RF-36` | **Sí, subconjunto** (polígono pequeño sin confirmación, dinámica fluvial). Cubre la "incertidumbre" que piden I2 e I3. |
| Resumen mensual | I1 | `I1:RF-39` | **Won't** (ya es Could en I1). |
| GeoPackage/KML para QField/Avenza | I1 | `I1:RF-40` | **Should.** Es la alternativa de I1 al modo offline de I2 (ver **C-09**). |
| Autoguardado ante cortes (30 s) | I1 | `I1:RNF-07` | **Could.** |
| Responsive 360 px | I1 | `I1:RNF-09` | **Could** (consulta en móvil). |
| Respaldos diarios y retención 5 años | I1 | `I1:RNF-10` | **Should** (respaldo diario sí; prueba trimestral y retención fuera del horizonte del curso). |
| Costo ≤ USD 25/mes, sin licencias | I1 | `I1:RNF-11` | **Sí.** Coincide con el stack del equipo (un VPS). |
| Despliegue con un comando + manual | I1 | `I1:RNF-12` | **Sí** (Docker Compose). |
| Interfaz en español | I1 | `I1:RNF-14` | **Sí.** Trivial e implícito en los tres. |
| Abstracción de fuentes (GLAD, Copernicus) | I1 | `I1:RNF-15` | **Should** como principio de diseño. |
| Nunca mostrar titulares de derechos | I1 | `I1:RD-18` | **Sí.** Barato (no importar la columna) y evita riesgo legal al cruzar con concesiones. |
| No emitir alertas oficiales ni enviar a terceros | I1 | `I1:RD-19` | **Sí.** Coherente con la base y con "notificaciones fuera" de I3. |
| SRC EPSG:32719 / EPSG:4326 | I1 | `I1:RD-01` | **Sí.** Necesario para que las áreas y distancias sean verificables. |
| Datos oficiales nunca se modifican | I1 | `I1:RD-04` | **Sí.** Regla barata. |
| Detecciones propias distinguidas | I1 | `I1:RD-05`, `I1:RF-13` | **Should** (zonas manuales). |
| Plazo propio de 12 semanas | I1 | `I1:RD-15` | **No**: es una restricción del cliente simulado, no del curso (~10 semanas). |

### 4.2 Solo en I2

| Tema | Integrante | IDs | ¿Incorporarlo? (justificación) |
|---|---|---|---|
| Slider deslizante entre periodos | I2 | `I2:RF-01-AC-3` | **Could.** Mejora de UX, no núcleo. |
| Capa de diferencia y mensaje explícito de "sin cambios" | I2 | `I2:RF-02` | **Sí, el mensaje** ("no se detectaron cambios"), que también está en `I3:RF-03-AC-2` (en realidad es consenso parcial I2–I3). La capa de diferencia ráster: Could. |
| Panel de detalle con % de cambio y nivel de confianza | I2 | `I2:RF-03` | **Parcial.** Hectáreas, fecha, fuentes, confianza: sí. "Tipo de cambio probable" y "contexto legal": **no** (ver **C-01**, **C-02**). |
| Clasificación por NDVI/NDFI con ≥ 2 lecturas consecutivas | I2 | `I2:RF-04` | **No como clasificación de tipo.** La idea de exigir persistencia sí está cubierta como factor (I1, I3). NDFI no aparece en otros SRS. |
| Fuentes mostradas por separado sin veredicto único | I2 | `I2:RF-06` | **Sí, como principio** (cada alerta conserva su fuente), compatible con la agrupación de I1 si no se presenta un veredicto (ver **C-15**). |
| Guardar una comparación para el mismo usuario | I2 | `I2:RF-07-AC-2` | **Cubierto** por el almacenamiento de I3/I1. |
| Exportar como imagen o reporte | I2 | `I2:RF-07` | **Could** (la ficha PDF de I1 es el "reporte"). |
| Aviso de fuente desactualizada con caché | I2 | `I2:RF-11` | **Sí, como indicador en la app** con fecha de última actualización (coincide con `I1:RF-02`). |
| Modo de campo offline con GPS | I2 | `I2:RNF-02` | **No** (ver **C-09**). |
| Restringir detalle geoespacial por rol | I2 | `I2:RNF-03` | **No por rol en el MVP**; sí la regla de no mostrar titulares y datos personales. |
| Minimizar falsos positivos | I2 | `I2:RNF-04` | **Sí, reformulado** como marcas de confianza; tal como está no es verificable. |
| Administrador institucional / multiorganización | I2 | `I2:RF-10` | **No** (ver **C-04**). |
| Superadmin configura fuentes | I2 | `I2:RF-10-AC-4` | **No** como función de UI en el MVP; fuentes por configuración de despliegue. |
| Series temporales completas (tema abierto) | I2 | `I2:RD-02` | **No en el MVP**; registrar como tema abierto. |
| Desfase de 1–4 semanas | I2 | `I2:RD-03` | **Sí, como RD informativa** (justifica fechas de detección e ingesta). |

### 4.3 Solo en I3

| Tema | Integrante | IDs | ¿Incorporarlo? (justificación) |
|---|---|---|---|
| Reglas de validez de los periodos (inicio ≤ fin, distintos, no superpuestos, un día válido) | I3 | `I3:RF-02-AC-2` | **Sí.** Barato, verificable y aplica a cualquier comparación. |
| Prioridad "No disponible" cuando ningún factor tiene datos | I3 | `I3:RF-06-AC-3` | **Sí.** Evita inventar prioridad; el modelo de I1 nunca llega a ese caso porque "ubicación" siempre existe, pero la regla debe estar. |
| Factor sin datos se muestra "No disponible", no se omite | I3 | `I3:RF-07-AC-2` | **Sí.** Mejora la explicabilidad de I1 (que asume datos completos). |
| Determinismo de la prioridad | I3 | `I3:RF-06-AC-2` | **Sí.** Muy fácil de probar; I1 lo cumple implícitamente al registrar versión de pesos y parámetros. |
| Estado "Incierto" | I3 | `I3:RF-09`, `I3:RD-02` | **Discutir** (ver **C-07**). |
| "Revisado" no implica confirmación | I3 | `I3:RF-09` | **Sí.** Aclaración clave para B4. |
| Almacenamiento automático del análisis e inmutabilidad del histórico | I3 | `I3:RF-10` | **Sí** (equivale a la reproducibilidad de `I1:RF-15` en versión ligera). |
| Lista y detalle de análisis anteriores | I3 | `I3:RF-11` | **Sí** si el análisis es entidad propia (ver **C-05**). |
| Feedback en ≤ 60 s | I3 | `I3:RNF-03` | **Sí.** Medible y compatible con ejecución en segundo plano. |
| "Información no disponible" sin capa hídrica | I3 | `I3:RF-05-AC-3` | **Sí.** |
| Recencia referida al fin del periodo seleccionado | I3 | `I3:RF-07-AC-3` | **Discutir** (ver **C-08**). |

---

## 5. Conflictos

### C-01 — Atribución de causa ("posible minería") y clasificación automática del tipo de cambio

- **Descripción.** I2 hace que el sistema clasifique y muestre un "tipo de cambio probable" que
  incluye "posible minería"; I1 e I3 prohíben cualquier etiqueta de causa.
- **Posiciones.**
  - I1: `I1:RD-17` ("no determina ni etiqueta causas"), `I1:RF-23-AC-17` (candidatos sin atributo de causa), `I1:RF-33` (ningún texto del desglose asigna causas), `I1:RF-36` (las hipótesis solo las escribe el analista como "Marca del analista"), `I1:RD-16`.
  - I2: `I2:§1.2` ("su posible causa"), `I2:RF-03` y `I2:RF-03-AC-2` (pérdida de cobertura / **posible minería** / no clasificado), `I2:RF-04` (clasificación automática por NDVI/NDFI).
  - I3: `I3:RD-03`, `I3:§1.2`, `I3:§2.4` ("no atribuirá automáticamente la causa").
- **Impacto.** Alto. Contradice directamente la base (B4: "sin determinar automáticamente sus
  causas"). Además "posible minería" junto a un cruce con concesiones puede leerse como acusación.
- **Opciones.**
  1. Eliminar la clasificación de tipo de cambio de I2; mantener solo atributos medibles (área, fecha, fuente, confianza).
  2. Mantener un campo de "hipótesis" **solo manual**, escrito por el analista y rotulado como tal (modelo `I1:RF-36`).
  3. Conservar la clasificación automática renombrada como "patrón espectral" sin la categoría minería.
- **Recomendación: 1 + 2.** La base es explícita; la opción 3 sigue siendo una inferencia de causa
  disfrazada y obliga a validar umbrales con un especialista (el propio I2 lo reconoce en §2.4).

### C-02 — Cruce con concesiones mineras: "contexto legal-administrativo" y titulares

- **Descripción.** I2 presenta el cruce con INGEMMET como contexto "legal-administrativo" e indica
  si el cambio está "dentro o fuera de una concesión activa"; I1 lo presenta como superposición
  neutral sin titular y con fecha de corte; I3 no incluye concesiones y prohíbe establecer legalidad.
- **Posiciones.**
  - I1: `I1:RF-10` (tipo de derecho, código y estado, **nunca el titular**), `I1:RD-18`, `I1:RF-03-AC-15` (la columna del titular ni se importa), `I1:RD-06` (fecha de corte para no reportar petitorios extinguidos).
  - I2: `I2:RF-03` (contexto legal-administrativo), `I2:RF-05` (dentro/fuera de concesión activa contra "la capa vigente").
  - I3: `I3:RD-03` ("no establecer la legalidad"); sin capa de concesiones.
- **Impacto.** Medio-alto. Ubicar un cambio dentro/fuera de una concesión es un dato espacial
  legítimo, pero rotularlo como "legal" y mostrar titulares se acerca a determinar legalidad (B4).
- **Opciones.**
  1. Incluir el cruce como **superposición factual** (tipo de derecho, código, estado, fecha de corte), sin titulares ni rótulo "legal" (modelo I1).
  2. Excluir concesiones del MVP (modelo I3).
  3. Adoptar I2 tal cual.
- **Recomendación: 1.** El contexto minero es relevante en Tambopata (la base menciona minería
  ilegal como presión) y el cruce es barato con PostGIS. La regla "sin titulares" y la fecha de
  corte eliminan el riesgo.

### C-03 — Alcance geográfico

- **Descripción.** I2 permite cualquier zona de interés (por nombre, coordenadas o polígono) y no
  menciona Tambopata; I1 e I3 limitan el sistema a la RN Tambopata y su zona de amortiguamiento.
- **Posiciones.** I1: `I1:RD-14`, `I1:RF-05-AC-10` (rechaza fuera), `I1:RF-05-AC-11` (recorta), `I1:RF-31` (descarta alertas fuera). I2: `I2:RF-01`, `I2:§1.2` ("instituciones de gestión territorial"). I3: `I3:RD-05`, `I3:RF-03-AC-4`, `I3:§1.2` (fuera: "expansión a todo el Perú").
- **Impacto.** Alto: condiciona capas a cargar, volumen de datos, pruebas y costo del VPS. La base fija Tambopata (B1).
- **Opciones.** 1. Ámbito fijo Tambopata + ZA, con rechazo/recorte (I1/I3). 2. Ámbito libre (I2). 3. Ámbito configurable en despliegue, con Tambopata como único valor en el MVP.
- **Recomendación: 1** para requerimientos y pruebas, diseñando el límite como dato cargado (no
  constante en el código), lo que deja abierta la opción 3 sin costo extra.

### C-04 — Roles, permisos y multiorganización

- **Descripción.** Tres modelos incompatibles: 1 rol (I3), 2 roles sin herencia con matriz 403 (I1) y 3 roles jerárquicos con instituciones (I2).
- **Posiciones.**
  - I1: Analista SIG y Coordinación (no SIG); la Coordinación **no** cambia estados ni exporta datos geográficos pero sí gestiona usuarios y revisa contenido de fichas (`I1:§2.3`, `I1:RNF-02`, `I1:RF-22`). El analista no gestiona usuarios.
  - I2: Investigador/Analista, Administrador institucional (usuarios de su institución y zonas prioritarias), Superadmin (fuentes y umbrales); "Investigador/Analista **o superior**" confirma alertas (`I2:RF-09-AC-1`, `I2:RF-10`), es decir, roles jerárquicos. Restricción de detalle por rol (`I2:RNF-03`).
  - I3: un solo rol, Especialista ambiental/SIG (`I3:§2.3`); sin autorización.
- **Impacto.** Alto en API y pruebas: cada rol multiplica casos de 403. La multiorganización de I2 exige aislamiento de datos por institución (tenant), fuera de la base (B2).
- **Opciones.**
  1. **Un rol operativo + un rol administrador** mínimo (crear/desactivar usuarios), sin multiorganización.
  2. Los dos roles de I1 con su matriz completa.
  3. Los tres roles de I2.
- **Recomendación: 1** para el MVP, con la estructura de autorización preparada para agregar un
  rol de solo lectura/revisión (Coordinación de I1) como Should. La base solo nombra analistas;
  la multiorganización (I2) y la restricción de coordenadas por rol no tienen sustento en la base.

### C-05 — Entidad central y ciclo de vida de la "zona"

- **Descripción.** "Zona" significa cosas distintas:
  - I1: **zona de cambio** persistente que agrupa alertas a lo largo del tiempo, con estado vivo y contenido versionado (`I1:§1.3`, `I1:RF-32`, `I1:RF-16`); el área que el usuario dibuja se llama **área de análisis** (`I1:RF-05`).
  - I2: **zona de interés** = el área que el usuario selecciona para comparar (`I2:§1.3`, `I2:RF-01`), con historial de "zona monitoreada" (`I2:RF-08`).
  - I3: **zona candidata** que pertenece al **análisis** que la generó; una zona similar en un análisis posterior **no** se vincula ni altera la anterior (`I3:RF-10-AC-3`, `I3:RF-09-AC-3`, `I3:RF-08`).
- **Impacto.** Muy alto: define el modelo de datos, la API (`/zonas` vs `/analisis/{id}/zonas`), la trazabilidad y si el estado/prioridad de una zona sobrevive entre análisis. En I3 el analista revisaría de nuevo el mismo lugar en cada análisis; en I1 la zona acumula historia.
- **Opciones.**
  1. Zona persistente (I1) con un registro inmutable de cada análisis/cálculo asociado (toma la inmutabilidad de I3).
  2. Análisis como entidad central (I3), sin identidad de zona entre análisis.
  3. Área de interés del usuario como entidad (I2).
- **Recomendación: 1, simplificada** (sin versiones con ciclo de revisión). Es la que cumple B3
  ("qué zonas requieren revisión prioritaria" a lo largo del tiempo) y la que permite reapertura y
  persistencia. Unificar el glosario: *zona de cambio* (entidad), *área de análisis* (polígono del
  usuario), *análisis* (ejecución inmutable).

### C-06 — Origen de los cambios: alertas externas vs. detección propia automática

- **Descripción.** I1 parte de alertas oficiales ya publicadas (GeoBosques, RADD) y usa NDVI solo para proponer candidatos que el analista decide; I2 detecta y genera alertas automáticamente con umbrales NDVI/NDFI y ≥ 2 lecturas; I3 no dice cómo se identifican las zonas candidatas.
- **Posiciones.** I1: `I1:RF-31`, `I1:RF-32`, `I1:RF-23` ("ningún polígono se usa sin la decisión de un analista"), `I1:S-10` (por calibrar). I2: `I2:RF-04`, `I2:§2.4` (umbrales "preliminares" por validar). I3: `I3:RF-03` (sin método).
- **Impacto.** Muy alto en esfuerzo y riesgo: un detector propio confiable requiere procesamiento ráster, series de imágenes y validación experta; ingerir alertas es carga de archivos + reglas espaciales.
- **Opciones.**
  1. Alertas externas como fuente principal (GeoBosques por archivo Must; RADD Should) y detección propia solo como apoyo opcional con validación humana.
  2. Detección propia automática (I2).
  3. Dejarlo sin especificar (I3).
- **Recomendación: 1.** Menor riesgo técnico para 10 semanas, alineado con B4 (el sistema no
  "detecta" causas, solo organiza señales oficiales) y verificable con archivos de prueba. La opción
  3 no es aceptable: sin fuente definida `I3:RF-03` no se puede implementar ni probar.

### C-07 — Estados de revisión y transiciones

- **Descripción.**
  - I1: nueva → en revisión → revisada / requiere verificación → verificada en campo (resultado confirmado/no confirmado); descartada; fusionada. Tabla cerrada de transiciones, motivo/comentario obligatorio en varias, reapertura manual y automática (`I1:RF-11`, `I1:RF-37`).
  - I2: nueva, en revisión, **confirmada**, descartada (`I2:RF-08`, `I2:RF-09`).
  - I3: Pendiente, En revisión, **Incierto**, Revisado; **cualquier transición** permitida; observación opcional; "Revisado" no confirma nada (`I3:RF-09`, `I3:RD-02`).
- **Impacto.** Alto: la máquina de estados es parte del contrato de la API y de muchas pruebas.
  Además "confirmada" (I2) choca con B4 y con `I3:RF-09` ("Revisado no significa que el cambio,
  su causa o su legalidad hayan sido confirmados").
- **Opciones.**
  1. Conjunto mínimo unificado: **nueva, en revisión, requiere verificación, revisada, descartada**, con "incierto" como marca o como motivo, transiciones cerradas y motivo obligatorio solo al descartar y al reabrir.
  2. Transiciones libres de I3 con sus 4 estados.
  3. Tabla completa de I1 (incluye verificada en campo y fusionada).
- **Recomendación: 1.** Evita "confirmada" (B4), conserva la idea de incertidumbre de I3 sin
  convertirla en un estado terminal ambiguo, y mantiene la tabla cerrada (más fácil de probar con
  un AC por transición rechazada). "Verificada en campo" y "fusionada" pueden agregarse como Should.

### C-08 — Escala, factores y cálculo de la prioridad

- **Descripción.** I1 calcula un puntaje 0–100 con 7 factores ponderados y niveles por umbral; I3
  asigna directamente Alta/Media/Baja (o No disponible) con 6 factores sin fórmula; I2 no prioriza.
- **Posiciones y diferencias concretas.**

| Aspecto | I1 (`I1:RF-33`–`I1:RF-35`) | I3 (`I3:RF-06`–`I3:RF-08`) |
|---|---|---|
| Escala | 0–100 + nivel (alta ≥ 70, media 40–69, baja < 40) | Solo nivel Alta/Media/Baja; "No disponible" |
| Factores | Ubicación, persistencia y crecimiento, agrupación, confirmación multifuente, cercanía a ríos, superficie, recencia | Extensión, persistencia temporal, ubicación territorial, proximidad hídrica, recencia, **calidad o incertidumbre de la evidencia** |
| Calidad/incertidumbre | **No** afecta el puntaje (`I1:RF-36`: las marcas "no cambian su puntaje") | **Es un factor** de la prioridad |
| Fecha de referencia de la recencia | Hoy: días desde la alerta más reciente; ventanas contadas "hacia atrás desde hoy" | **Fin del periodo más reciente seleccionado**, explícitamente **no** la fecha de ejecución (`I3:RF-07-AC-3`) |
| Fórmula | Definida y verificable (normalizaciones S-20…S-25) | No definida: `I3:RF-06-AC-1` solo verifica que el valor sea uno de tres |
| Ajuste manual | Puntaje ajustado 0–100 + comentario; se puede quitar; la reapertura lo retira | Otro nivel + justificación obligatoria |
| Pesos | Configurables por analistas, versionados, nunca automáticos | No mencionados |
| Orden dentro del nivel | Desempate total (fecha, código) | No exigido |

- **Impacto.** Alto: es el valor principal (B3). Sin fórmula (I3) la prioridad no es verificable; con la de I1 completa el costo es alto. Los dos puntos en contradicción directa son **incertidumbre como factor** y **referencia de la recencia**.
- **Opciones.**
  1. Puntaje 0–100 con nivel derivado (I1), **factores reducidos** a los que coinciden I1 e I3 (ubicación, persistencia, extensión/superficie, proximidad hídrica, recencia) + confirmación multifuente si se ingieren dos fuentes; pesos fijos en configuración; desglose visible; "No disponible" por factor (I3).
  2. Solo niveles con reglas cualitativas (I3), definiendo una tabla de decisión.
  3. Modelo completo de I1 (7 factores, pesos versionados, parámetros versionados).
- **Recomendación: 1.** Mantiene la verificabilidad de I1 y la transparencia de I3. Sobre los dos
  conflictos directos: (a) la **incertidumbre no debe bajar la prioridad** sino mostrarse como
  marca (I1), porque una zona dudosa pero grande dentro de la reserva igual debe revisarse primero;
  (b) la **recencia** debe medirse respecto de la fecha de cálculo si las zonas son persistentes
  (C-05, opción 1); la regla de I3 solo tiene sentido si el análisis es la entidad central. Decidir
  ambos con el equipo y dejarlo explícito en un AC.

### C-09 — Modo offline / aplicación de campo

- **Descripción.** I2 exige una "versión ligera con soporte offline y uso del GPS del dispositivo"; I1 e I3 dejan la app móvil fuera, e I1 también el funcionamiento sin conexión, resolviendo el campo con exportaciones para QField/Avenza.
- **Posiciones.** I1: `I1:§1.2` (fuera), `I1:RF-40` (GeoPackage/KML), `I1:RF-25` (expediente), `I1:RNF-07` (autoguardado ante cortes). I2: `I2:RNF-02`, `I2:§1.2`, `I2:§2.1`. I3: `I3:§1.2` ("Aplicación móvil" fuera).
- **Impacto.** Alto: un modo offline con GPS implica PWA/service workers, sincronización y conflictos; está fuera de la capacidad de 10 semanas y la base no lo menciona.
- **Opciones.** 1. Fuera del MVP; campo vía exportación KML/GeoPackage (I1). 2. PWA de solo lectura con caché (I2 reducido). 3. I2 completo.
- **Recomendación: 1.** Las herramientas de campo ya existen (QField/Avenza); exportar es mucho más barato y verificable (abrir el archivo con GDAL en pruebas).

### C-10 — Notificaciones

- **Descripción.** I3 excluye "notificaciones automáticas"; I1 excluye correos/canales externos pero usa **indicadores dentro de la app** (análisis terminado, zona reabierta, nuevas); I2 exige notificar de forma visible cuando una fuente cae.
- **Posiciones.** I1: `I1:§1.2`, `I1:RF-29` (notifica en la app al terminar/fallar), `I1:RF-37`, `I1:RF-04`. I2: `I2:RF-11`, `I2:§2.2` punto 5. I3: `I3:§1.2`.
- **Impacto.** Bajo-medio; es sobre todo ambigüedad del término. Un aviso en pantalla de fuente caída (I2) no contradice "sin notificaciones automáticas" si esta se entiende como envío externo.
- **Opciones.** 1. Definir "notificación" = mensaje fuera del sistema (correo, SMS, push): fuera del MVP; los avisos en la interfaz están permitidos. 2. Excluir también los avisos internos. 3. Incluir correo.
- **Recomendación: 1.** Agregar la definición al glosario; conservar `I2:RF-11` como indicador en la app (coincide con `I1:RF-02-AC-4`).

### C-11 — Nivel de autenticación

- **Descripción.** I1 exige contraseña ≥ 12 caracteres con bcrypt/Argon2, **TOTP obligatorio**, bloqueo tras 5 intentos, sesión de 30 min y ciclo de credenciales; I3 solo "datos de autenticación válidos"; I2 no tiene requerimiento de autenticación.
- **Posiciones.** I1: `I1:RF-28`, `I1:RNF-01`, `I1:RNF-03`. I2: ninguno explícito (implícito en `I2:RF-10`). I3: `I3:RF-01`, `I3:RNF-04`.
- **Impacto.** Medio: el 2FA y la recuperación de credenciales añaden flujos y pruebas; I3 es inverificable en parámetros concretos.
- **Opciones.** 1. Contraseña con hash + expiración de sesión + 401 en toda ruta (Must); TOTP y bloqueo como Should. 2. Todo I1 como Must. 3. I3 tal cual.
- **Recomendación: 1.** Cubre el riesgo real (datos sensibles, ubicación de zonas) con poco costo y deja TOTP como mejora planificada.

### C-12 — Quién configura umbrales y pesos

- **Descripción.** I2: los umbrales NDVI/NDFI los configura el **Superadmin**. I1: los **pesos** los configuran los **analistas** con motivo y versión; el umbral NDVI se cambia **por análisis** al regenerar candidatos; las demás constantes **no se editan desde la interfaz**, solo con una versión del sistema. I3: no hay parámetros configurables.
- **Posiciones.** I1: `I1:RF-35`, `I1:RF-23-AC-6`, `I1:RF-08-AC-9`, `I1:§2.4` (parámetros). I2: `I2:RF-04-AC-4`, `I2:RF-10-AC-4`.
- **Impacto.** Medio: define endpoints de configuración y permisos.
- **Opciones.** 1. Parámetros como configuración del despliegue (sin UI) en el MVP; pesos editables por analistas como Should. 2. Pantalla de administración (I2). 3. Modelo completo de I1.
- **Recomendación: 1.** Menos superficie de API y de pruebas; la regla "el sistema nunca reajusta solo" (`I1:RF-35`) debe mantenerse en cualquier caso.

### C-13 — Formatos y SRC de exportación

- **Descripción.** I1 define seis formatos con SRC por caso (GeoJSON/Shapefile en EPSG:32719, GeoPackage/KML en EPSG:4326, CSV UTF-8 con BOM, XLSX, PDF, ZIP); I2 pide "reporte, imagen y Shapefile o GeoJSON" sin SRC; I3 no exporta.
- **Posiciones.** I1: `I1:RF-17`, `I1:RF-18`, `I1:RF-19`, `I1:RF-25`, `I1:RF-40`, `I1:RD-01`. I2: `I2:RF-07`. I3: —.
- **Impacto.** Medio. Hay una ambigüedad en I2 ("Shapefile **o** GeoJSON": ¿ambos o uno?) y la ausencia de SRC hace inverificables las coordenadas.
- **Opciones.** 1. Must: GeoJSON (EPSG:4326 o 32719, definido) + CSV; Should: KML/GeoPackage y PDF simple; Could: Shapefile, XLSX, imagen, expediente. 2. Todos los formatos de I1. 3. Sin exportación (I3).
- **Recomendación: 1.** GeoJSON y CSV son casi gratis con el stack (Python) y cubren QGIS y Excel.

### C-14 — Guardado del análisis: manual vs. automático, y retención

- **Descripción.** I2 guarda una comparación a pedido del usuario y solo para él (`I2:RF-07-AC-2`: "recuperada posteriormente **por el mismo usuario**"); I3 almacena **automáticamente** todo análisis (`I3:RF-10-AC-1`); I1 conserva todo por zona y versión, sin borrado, con retención de 5 años (`I1:RF-15`, `I1:RNF-10`, `I1:S-05`, `I1:RF-11-AC-22`).
- **Impacto.** Medio: visibilidad compartida vs. privada entre analistas; política de borrado.
- **Opciones.** 1. Guardado automático, visible para todo el equipo, sin borrado en el MVP. 2. Guardado manual privado (I2). 3. I1 completo con retención y respaldos verificados.
- **Recomendación: 1.** El equipo de analistas comparte zonas (todos los SRS hablan de seguimiento); la retención de 5 años se registra como restricción operativa, no como prueba del MVP.

### C-15 — Combinación de fuentes en una misma zona

- **Descripción.** `I2:RF-06-AC-2` prohíbe "combinar ni promediar automáticamente los resultados de distintas fuentes en un único veredicto". I1 agrupa alertas de GeoBosques y RADD en una misma zona y usa la **confirmación multifuente** como factor de prioridad (`I1:RF-32`, `I1:RF-33`).
- **Impacto.** Bajo-medio. No es contradicción si cada alerta conserva su fuente (I1 lo hace: `I1:RF-13-AC-1`, `I1:RF-17-AC-14`) y la zona no emite un "veredicto", pero la redacción de I2 podría leerse como prohibición de agrupar.
- **Opciones.** 1. Permitir la agrupación espacial y el factor multifuente, exigiendo que el detalle muestre cada alerta con su fuente y que no exista un campo "veredicto". 2. Mostrar zonas separadas por fuente (sin agrupar). 
- **Recomendación: 1**, redactando el requerimiento consolidado como "agrupar sin perder la fuente de cada alerta".

### C-16 — Unidad temporal de la comparación

- **Descripción.** I1 compara dos **imágenes de fechas concretas** (y lista imágenes por rango con nubosidad); I2 e I3 comparan dos **periodos** (rangos). I3 prohíbe periodos superpuestos; I1 acepta cualquier par de fechas con imagen disponible y recomienda el mismo mes del año anterior (`I1:RD-08`).
- **Posiciones.** I1: `I1:RF-07`, `I1:RF-08`. I2: `I2:RF-01`. I3: `I3:RF-02`.
- **Impacto.** Medio: cambia el formulario, la API y cómo se elige la imagen dentro de un rango (¿la menos nubosa?, ¿un compuesto?).
- **Opciones.** 1. Periodos (I2/I3) con reglas de validez de I3, y dentro de cada periodo el sistema elige la imagen de menor nubosidad en el área (mostrándola, como I1). 2. Fechas exactas (I1). 3. Periodos con compuesto (mediana).
- **Recomendación: 1.** Coincide con dos de tres SRS y con la base ("comparar periodos"), y conserva la trazabilidad de I1 (la imagen usada queda registrada).

### C-17 — Índices espectrales

- **Descripción.** I2 usa NDVI **y NDFI**; I1 solo NDVI; I3 no especifica.
- **Posiciones.** `I2:RF-04`, `I2:§1.3`; `I1:RF-23`, `I1:§1.3`.
- **Impacto.** Bajo para el MVP si la detección propia queda como Could (C-06).
- **Opciones.** 1. Solo NDVI. 2. NDVI + NDFI.
- **Recomendación: 1.** NDFI requiere desmezcla espectral, mucho más costosa; registrar NDFI como tema abierto.

---

## 6. Diferencias de calidad y forma

### 6.1 Formato de los criterios de aceptación

| Criterio | I1 | I2 | I3 |
|---|---|---|---|
| Given-When-Then | Sí, en todos | **No** (viñetas "El sistema debe…"; algunos empiezan con "Dado que" sin "cuando/entonces", p. ej. `I2:RF-01` AC 1) | Sí, en todos |
| IDs de AC (`RF-XX-AC-Y`) | Sí, inmutables, con convención y línea base | **No** | Sí (`I3:RF-03-AC-1`…) |
| Un comportamiento por AC | Sí | No siempre (p. ej. `I2:RF-03` AC 1 exige siete campos a la vez) | Mayormente (excepción: `I3:RF-02-AC-2` agrupa cuatro condiciones de rechazo; `I3:RF-06-AC-2` combina dos casos) |
| Valores concretos y oráculos | Sí (áreas, fechas, ± tolerancias, comparación con pyproj/shapely) | No | Pocos |
| Tipo de verificación (API / E2E / manual) | Sí | No | No |
| Prioridad MoSCoW | Sí | No | No |
| Trazabilidad a la fuente | Sí (P#, Sección C, C-#) | Sí (P1–P10) | Genérica ("elicitación con stakeholders") |
| RNF con métrica y método de verificación | Sí, los 15 | No (ninguno) | Solo `I3:RNF-03` (60 s) |

**Consecuencia para el curso:** la convención exigida (endpoints en `openapi.yaml` con IDs
`RF-XX-AC-Y`, pruebas `test_RF_XX_AC_Y`) la cumplen I1 e I3; I2 tendría que reescribirse entera.

### 6.2 Términos ambiguos o no verificables

| SRS | Ejemplos |
|---|---|
| I2 | "delimitar **correctamente**" (`I2:RF-01`), "mensaje de error **claro**" (`I2:RF-01`), "reflejarse **inmediatamente**" (`I2:RF-09-AC-3`), "aviso **visible**" (`I2:RF-11`), "**minimizarse**" la tasa de falsos positivos (`I2:RNF-04`), "versión **ligera**" (`I2:RNF-02`), "**sin ambigüedad**" (`I2:RF-06`), "umbral configurado" sin valor, "Shapefile **o** GeoJSON" (`I2:RF-07`), "reporte" e "imagen" sin formato. `I2:RD-02` no es un requerimiento sino un tema abierto. Las RD-01…RD-03 se duplican en §2.4 y §3.3. |
| I3 | "datos de autenticación válidos" (`I3:RF-01`), "información disponible" (`I3:RF-03-AC-1`), "limitaciones **relevantes**" (`I3:RF-03-AC-5`, `I3:RD-01`), "zona **geográficamente similar**" (`I3:RF-10-AC-3`), "información **insuficiente**" (`I3:RF-03-AC-3`), "el sistema identifica" (sin método). La prioridad no tiene regla de cálculo, por lo que `I3:RF-06-AC-1` y `I3:RF-06-AC-4` solo verifican la forma, no el resultado. Repeticiones textuales entre §2.2, §2.4, RNF y RD (p. ej. 60 s en §2.4 y `I3:RNF-03`; ámbito en §2.4, `I3:RF-03` y `I3:RD-05`). |
| I1 | Pocos términos vagos; los temas por calibrar están marcados (`I1:S-10`, `I1:S-16`, `I1:S-21`…`S-25`). Problemas de forma distintos: **volumen** (452 AC, 28 parámetros) difícil de revisar en equipo; **dependencia de documentos no compartidos** (transcripciones Sección A/B/C, `casos_de_uso.md`, `borradores/`, `revision_SRS.md`); `I1:RNF-13` depende de una demostración subjetiva ("comprensible"); restricciones del cliente simulado (12 semanas, ONG, donante) que no son del equipo. |

### 6.3 Terminología que hay que unificar

| Concepto | I1 | I2 | I3 |
|---|---|---|---|
| Polígono que dibuja el usuario | Área de análisis | Zona de interés | — |
| Unidad de revisión | Zona de cambio | Zona monitoreada / alerta | Zona candidata |
| Señal de entrada | Alerta (fuente externa) | Alerta (generada por el sistema) | — |
| Ventana temporal | Fecha | Periodo | Periodo |
| Rol principal | Analista SIG | Investigador / Analista | Especialista ambiental / SIG |
| Resultado de revisión | Revisada / verificada en campo | Confirmada | Revisado |

Nota: "alerta" en I2 es un producto del sistema; en I1 es un dato externo. Usar la misma palabra
para ambos generaría confusión en la API.

---

## 7. Propuesta de núcleo MVP

**Supuestos.** Equipo de 3 estudiantes, ~10 semanas, que construye API (FastAPI), backend
geoespacial (PostgreSQL/PostGIS), frontend (React) y pruebas. El MVP debe demostrar el flujo de la
base (B1–B4): *ver cambios en Tambopata → saber cuáles revisar primero y por qué → registrar la
revisión*, con criterios Given-When-Then trazables a pruebas. Se priorizan funciones verificables
con datos de archivo (sin depender de GEE en la ruta crítica).

### 7.1 Must (núcleo)

| # | Requerimiento consolidado | Origen principal | Justificación |
|---|---|---|---|
| M1 | Autenticación con contraseña con hash, sesión que expira y 401 en toda ruta | `I1:RNF-01`, `I3:RF-01` | Mínimo de seguridad para datos sensibles; barato. |
| M2 | Dos roles: analista (operativo) y administrador (usuarios); 403 en servidor | `I1:RNF-02` reducido, `I2:RF-10` reducido | Resuelve C-04 con la menor matriz útil. |
| M3 | Ámbito fijo RN Tambopata + ZA; lo de fuera se rechaza/descarta | `I1:RD-14`, `I3:RD-05` | Base B1; acota datos y pruebas. |
| M4 | Carga de capas de referencia (límites, ZA, ríos, catastro minero sin titular) con fuente y fecha de corte | `I1:RF-02`, `I1:RF-03` (sin versionado histórico), `I1:RD-18` | Sin capas no hay contexto ni prioridad. |
| M5 | Ingesta de alertas GeoBosques por archivo, sin duplicados, con fecha de detección e ingesta | `I1:RF-31` (solo GeoBosques) | Fuente concreta para `I3:RF-03`; resuelve C-06 sin GEE. |
| M6 | Agrupación de alertas en zonas de cambio (≤ 500 m, ≤ 90 días), con código y área en ha | `I1:RF-32` (sin fusión ni historial del lugar), `I1:RF-09` | Entidad central (C-05). |
| M7 | Mapa con capas activables y zonas coloreadas por nivel | `I1:RF-01` reducido, `I3:RF-04`, `I2:RF-02-AC-2` | Consenso de los tres. |
| M8 | Contexto territorial: superposición con reserva, ZA y catastro (tipo, código, estado, fecha de corte; sin titular) y distancia al río en m, "Información no disponible" si falta | `I1:RF-10`, `I3:RF-05`, `I2:RF-05` reformulado | Consenso; resuelve C-02. |
| M9 | Prioridad explicada: puntaje 0–100 + nivel, factores ubicación, persistencia, superficie, proximidad hídrica, recencia (pesos fijos en configuración), desglose siempre visible, "No disponible" por factor, determinista | `I1:RF-33` reducido, `I3:RF-06`, `I3:RF-07` | Valor principal B3; resuelve C-08. |
| M10 | Lista ordenada por prioridad con filtro por nivel y estado | `I1:RF-12` reducido, `I3:RF-06-AC-4` | Es la "lista corta" que justifica el producto. |
| M11 | Ajuste manual de prioridad con justificación obligatoria, conservando el calculado | `I1:RF-34`, `I3:RF-08` | Consenso I1–I3; B4 (decisión del especialista). |
| M12 | Estados de revisión unificados con tabla cerrada, historial con usuario, fecha y comentario; motivo obligatorio al descartar | `I1:RF-11` reducido, `I2:RF-09`, `I3:RF-09` | Consenso de los tres; resuelve C-07. |
| M13 | Reglas de dominio: no etiquetar causas ni legalidad; no mostrar titulares; no emitir alertas oficiales; "revisada" ≠ confirmada | `I1:RD-17`, `I1:RD-18`, `I1:RD-19`, `I3:RD-03`, `I3:RF-09` | Base B4; costo casi nulo y verificable (ausencia de campos). |
| M14 | Indicador de fuente desactualizada / fecha de última actualización; nunca presentar dato viejo como vigente | `I2:RF-11`, `I1:RF-02`, `I3:RNF-05` | Consenso de los tres; barato. |
| M15 | Exportación de la lista filtrada a CSV y de zonas a GeoJSON (SRC definido) | `I1:RF-19`, `I1:RF-18`, `I2:RF-07` | Consenso parcial; barato; uso en QGIS/Excel. |
| M16 | Despliegue con Docker Compose en un VPS ≤ USD 25/mes; interfaz en español | `I1:RNF-11`, `I1:RNF-12`, `I1:RNF-14` | Restricción del stack del equipo. |
| M17 | Respuesta en ≤ 60 s (resultado, estado o error) y lista de zonas en ≤ 5 s | `I3:RNF-03`, `I1:RNF-08` | Medibles y compatibles. |

### 7.2 Should

| Requerimiento | Origen | Motivo de no ser Must |
|---|---|---|
| Comparación visual de dos periodos (lado a lado) con imágenes vía GEE, elección de la imagen menos nubosa y estados del análisis (en cola/en curso/terminado/fallido) | `I1:RF-07`, `I1:RF-08`, `I1:RF-29`, `I2:RF-01`, `I3:RF-02` (con reglas de validez) | Presente en los tres y en la base, pero depende de GEE (cuenta, cuotas, latencia): se planifica pronto pero no bloquea el flujo núcleo. **Si el equipo considera "comparar periodos" innegociable por la base, subirlo a Must con un alcance de solo visualización.** |
| Ingesta RADD vía GEE y confirmación multifuente | `I1:RF-31`, `I1:RF-33` | Integración externa de riesgo. |
| Marcas de confianza (polígono pequeño sin confirmación, posible dinámica fluvial) sin ocultar ni cambiar puntaje | `I1:RF-36`, `I2:RF-03` (confianza), `I3:RD-02` | Cubre incertidumbre de los tres; necesita capas adicionales. |
| Reapertura automática de zonas cerradas | `I1:RF-37` | Depende de M6; alto valor de dominio. |
| Pesos configurables por analistas con motivo e historial | `I1:RF-35` | M9 funciona con pesos fijos. |
| Exportación GeoPackage/KML para QField/Avenza | `I1:RF-40` | Alternativa a offline (C-09). |
| Ficha PDF simple (sin ciclo de versiones) con huella SHA-256 | `I1:RF-17` reducido, `I2:RF-07` ("reporte") | Útil pero con mucha plantilla. |
| Bitácora de acciones de solo inserción | `I1:RNF-04`, `I1:RF-27` reducido | Trazabilidad; tabla simple. |
| TOTP obligatorio y bloqueo por intentos | `I1:RNF-03`, `I1:RF-28` | Mejora de seguridad sobre M1. |
| Rol de solo lectura / revisión (Coordinación) | `I1:§2.3` | Amplía M2 si el equipo lo valida. |
| Respaldo diario automático | `I1:RNF-10` | Operativo. |
| Zonas manuales ("detección propia") | `I1:RF-13`, `I1:RD-05` | Complementa la ingesta. |

### 7.3 Could

- Candidatos NDVI semiautomáticos (`I1:RF-23`) o capa de diferencia (`I2:RF-02`).
- Fusión de zonas e historial del lugar (`I1:RF-32`).
- "Nuevas desde tu última revisión" (`I1:RF-04`).
- Sectores y cuencas (`I1:RF-22`), filtros adicionales (`I1:RF-12`).
- Slider (`I2:RF-01-AC-3`), exportación como imagen (`I2:RF-07`), XLSX y Shapefile (`I1:RF-18`, `I1:RF-19`).
- Notas de discrepancia (`I1:RF-14`, `I2:RF-06`).
- Reportes de campo (`I1:RF-21`), responsive móvil (`I1:RNF-09`), autoguardado (`I1:RNF-07`).

### 7.4 Won't (esta versión)

- Clasificación automática de tipo de cambio o causa (`I2:RF-03`, `I2:RF-04`) — contraria a la base.
- Modo offline con GPS (`I2:RNF-02`), multiorganización y Superadmin (`I2:RF-10`), visor externo.
- Ciclo de versiones con validación técnica/de contenido y ruta de urgencia (`I1:RF-16`), registro de compartición (`I1:RF-38`), expediente (`I1:RF-25`), supresión de datos (`I1:RF-30`), resumen mensual (`I1:RF-39`).
- NDFI, series temporales completas (`I2:RD-02`), GLAD.

### 7.5 Justificación global

- **Cobertura de la base:** M3 (B1), M2/M12 (B2), M9–M11 (B3), M13 (B4). Ningún Must contradice la base.
- **Consenso primero:** M7, M8, M12, M14 están en los tres SRS; M9–M11 en dos de tres (I2 no prioriza, pero la base lo exige).
- **Riesgo técnico controlado:** el flujo núcleo funciona solo con archivos cargados y PostGIS; GEE entra como Should, de modo que una falla de cuota o de credenciales no bloquea la entrega.
- **Capacidad:** ~17 Must con AC reducidos (estimación 60–90 AC) es un volumen que un equipo de 3 puede implementar y probar con nombres `test_RF_XX_AC_Y`; los 452 AC de I1 no lo son.
- **Trazabilidad:** conviene partir del formato de I1/I3 (Given-When-Then con IDs) y reescribir los AC de I2 que se conserven.

### 7.6 Decisiones que el equipo debe tomar antes de consolidar

1. C-05: zona persistente vs. análisis como entidad (define todo el modelo).
2. C-08: incertidumbre como factor o como marca; referencia de la recencia.
3. C-04: número de roles.
4. C-07: conjunto de estados (¿"incierto" estado o marca?).
5. Si la comparación visual de periodos (GEE) es Must o Should.
