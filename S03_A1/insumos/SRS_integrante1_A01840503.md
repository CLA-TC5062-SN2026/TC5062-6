# Especificación de Requerimientos de Software (SRS) — EcoAlert — Versión final

| Campo | Valor |
|---|---|
| **Versión** | 3.0 final. Historial: v1.0 revisión del borrador del agente; v1.1–v1.2 decisiones de alineación; v1.3 validación con el segundo stakeholder; v2.0 criterios Given-When-Then con IDs (Parte 5) y revisión técnica (Parte 6), con el nombre de trabajo GeoMonitor; **v3.0 realineación a EcoAlert** por la actualización de `proyecto_base.md` y la entrevista complementaria (Sección C, hallazgos C-1 a C-18), según `borradores/especificacion_realineacion_v3.md`, con las correcciones de la revisión técnica V-01 a V-26 (`borradores/revision_tecnica_v3_agente.md`) incorporadas antes de congelar la línea base. |
| **Fecha** | 2026-09-27 |
| **Autor** | Miguel Angel Arevalo Andrade — A01840503 |
| **Estándar de referencia** | IEEE 830-1998 (estructura simplificada) |
| **Estado** | Parámetros definidos por el analista (sección 2.4); pesos de priorización (S-16) por calibrar con resultados de campo; pendiente de validación con el stakeholder real |
| **Documentos relacionados** | `proyecto_base.md` (EcoAlert); `transcript_entrevista.md`: Secciones A (coordinadora) y B (asesoría legal), entrevistas simuladas sobre la base anterior del proyecto, y Sección C (analista SIG, usuario principal), entrevista simulada sobre la base de EcoAlert; `borradores/especificacion_realineacion_v3.md`; `borradores/revision_tecnica_v3_agente.md`; `revision_SRS.md`; `casos_de_uso.md` |

---

## 1. Introducción

### 1.1 Propósito del documento

Este documento especifica los requerimientos funcionales, no funcionales y de dominio de la
**primera versión (v1)** de EcoAlert. Es la base acordada para diseñar, construir, probar y
aceptar el sistema: cada requerimiento tiene un identificador único, una prioridad, su fuente en
la entrevista de elicitación y, en el caso de los funcionales, criterios de aceptación
verificables.

Lectores previstos:

| Lector | Uso del documento |
|---|---|
| Coordinación de la ONG cliente | Validar alcance, prioridades y supuestos (sección 2.4), la matriz de permisos (sección 2.3), la plantilla de la ficha (RNF-13) y el resumen mensual (RF-39). |
| Analistas SIG | Validar que la ingesta, la agrupación y la priorización (RF-31 a RF-37) y los flujos de análisis (RF-05 a RF-10 y RF-23) reflejan su trabajo, y calibrar el umbral de NDVI (S-10), los pesos de priorización (S-16) y las constantes de cálculo (S-21 a S-28). |
| Jefatura de la RN Tambopata (SERNANP), como destinataria | Revisar, a pedido de la coordinación, el contenido de la ficha de zona (RF-17) y las reglas de difusión (RD-17 a RD-19). No tiene cuenta en la v1. |
| Desarrollo y pruebas | Diseñar la solución y derivar casos de prueba de los criterios de aceptación. |

### 1.2 Alcance del sistema

**EcoAlert** es una aplicación web que permite a una ONG de conservación de Puerto Maldonado, que
colabora con la jefatura de la **Reserva Nacional Tambopata**, identificar y revisar los cambios
de cobertura vegetal en la reserva y su zona de amortiguamiento, y reconocer las **zonas que
requieren atención prioritaria** por parte de sus especialistas, **sin determinar automáticamente
las causas** de esos cambios. La interpretación y la decisión final siempre son del especialista.

**Problema que resuelve.** La reserva enfrenta pérdida de cobertura forestal y presiones como la
minería ilegal. Aunque existen datos públicos, hoy el análisis es manual: cada semana el analista
descarga las alertas de GeoBosques, las cruza con alertas radar en Google Earth Engine, las lleva a
QGIS con las capas de contexto y revisa cada polígono con imágenes de antes y después (Sección C,
P1). En temporada seca llegan entre 150 y 300 alertas en dos semanas, muchas duplicadas entre
fuentes, y la priorización depende del criterio individual. En un caso real, muchas alertas
pequeñas y agrupadas quedaron al final de la lista durante semanas y resultaron ser frentes de
minería avanzando hacia el límite de la reserva: no se vio el patrón (Sección C, P1-seg). Además,
armar a mano la ficha para la jefatura es la tarea que más tiempo consume (Sección C, P3).

**Qué hace la v1:**

1. **Ingiere y agrupa alertas.** Reúne las alertas de GeoBosques (carga de archivos) y de RADD
   (radar Sentinel-1, sincronizadas desde GEE) y las agrupa en **zonas de cambio** por cercanía en
   espacio y tiempo, sin duplicados. **Indica lo nuevo desde la última revisión de cada usuario y
   permite filtrarlo** (RF-04, RF-31, RF-32).
2. **Prioriza con explicación.** Cada zona tiene un puntaje de 0 a 100 y un nivel (alta, media o
   baja) con su **desglose por factor siempre visible**. Los pesos son visibles, versionados y
   configurables solo por los analistas, y el analista puede ajustar la prioridad con un
   comentario (RF-33 a RF-35).
3. **Señala la confianza sin ocultar.** Marca las zonas con condiciones que reducen la confianza
   (nubes, bruma, desfase entre la alerta y la imagen, dinámica fluvial, ecosistemas inundables,
   polígonos pequeños sin confirmación) y reabre automáticamente las zonas descartadas o revisadas
   que vuelven a cambiar (RF-36, RF-37).
4. **Permite el análisis detallado.** Compara imágenes Sentinel-2 y Landsat 8/9 de dos fechas con
   control de nubosidad. La detección es **semiautomática**: el sistema propone polígonos
   candidatos a partir de la diferencia de NDVI y **el analista los acepta, edita o descarta**.
   Calcula el área y las superposiciones con la reserva, la zona de amortiguamiento y los derechos
   otorgados (sin titulares), y la distancia a ríos y vías (RF-05 a RF-10, RF-23).
5. **Gestiona la revisión.** Cada zona tiene estado, origen, comentarios, historial y versiones, y
   registra lo necesario para reproducir cada cifra (RF-11 a RF-16).
6. **Documenta y comparte con registro.** Genera la **ficha de zona** en PDF, un documento técnico
   de apoyo para la jefatura con huella de integridad verificable. Antes de compartirse, la ficha
   la valida técnicamente el otro analista, o la revisa la coordinación en su contenido (revisión
   no técnica), o su autor la comparte por una **ruta de urgencia** registrada. Exporta zonas para
   campo (GeoPackage y KML), polígonos y listas, y registra cada exportación y cada compartición.
   El sistema **no envía nada** a terceros (RF-16 a RF-20, RF-25, RF-38, RF-40).

**Fuera del alcance de la v1** (decisiones del cliente en la Sección A, P6 y P7; en la Sección C,
P6-seg y P7; y del alumno el 2026-09-27):

- **Funciones legales:** rol legal, autorización legal, registro de presentaciones ante
  autoridades y registro de presuntos responsables. Las denuncias van por vías formales fuera del
  sistema (RD-19); la v1 solo registra comparticiones (RF-38).
- **Determinación o etiquetado automático de causas** del cambio (RD-17). El sistema solo
  **propone** polígonos candidatos, y ningún polígono se usa sin la decisión de un analista.
- **Notificaciones por correo** u otros canales externos: los avisos son indicadores dentro de la
  aplicación (RF-37).
- Aplicación móvil y funcionamiento sin conexión: en campo se usan las exportaciones (RF-40).
- Más de **3 años** de historia de alertas para comparar.
- Otras áreas protegidas de Madre de Dios: el ámbito es la RN Tambopata y su zona de
  amortiguamiento (RD-14).
- Ingesta de alertas **GLAD** (Could, RF-31): no forma parte del alcance comprometido.
- Tablero para donantes, plantillas por donante, acceso de monitores comunitarios, de
  guardaparques y de la jefatura (sin cuenta en la v1).
- Adjuntar documentos de respaldo a una discrepancia.
- Verificación de integridad de fichas por terceros sin cuenta en el sistema.
- Versión pública o para prensa de una zona.

**Beneficio esperado:** pasar de cientos de alertas sueltas a una lista corta y explicada de zonas
que merecen revisarse primero, reducir el tiempo de armado de la ficha para la jefatura y que toda
cifra compartida sea reproducible y tenga fuente y fecha.

### 1.3 Definiciones y acrónimos

| Término | Definición |
|---|---|
| Alerta | Aviso de pérdida de cobertura publicado por una fuente satelital (GeoBosques o RADD) e ingerido por el sistema (RF-31). Su geometría es un **polígono**. Tiene fuente, código, fecha de detección y fecha de ingesta. |
| Fuente satelital | GeoBosques o RADD (y GLAD si se incorpora). La detección propia y el reporte de campo son orígenes de una zona, no fuentes satelitales. |
| Alerta nueva para el usuario | Alerta cuya **fecha de ingesta** es posterior a la última revisión del usuario (RF-04). |
| Alerta posterior | Alerta cuya **fecha de detección** es posterior al último cambio de estado de la zona (RF-37). |
| Distancia | Distancia mínima entre geometrías, medida en EPSG:32719. |
| Zona de cambio | Entidad central del sistema. Agrupa alertas cercanas en espacio (≤ 500 m, S-14) y tiempo (≤ 90 días, S-15), o la crea manualmente un analista con un polígono (detección propia) o con el punto de un reporte de campo. Tiene código `EA-AAAA-NNN`, estado, origen, prioridad, marcas, historial y versiones (RF-32). |
| Geometría de la zona | Unión de las alertas de la zona y, en zonas manuales, del polígono o punto con que se creó. Es parte de la zona viva. |
| Área de la zona | Superficie, en hectáreas y en EPSG:32719, de la geometría de la zona (0 ha si es solo un punto). Se usa en la priorización y en la reapertura (RF-33, RF-37). |
| Zona activa / zona cerrada | Una zona está **cerrada** si su estado es "revisada" o "descartada"; está **activa** si su estado es "nueva", "en revisión", "requiere verificación" o "verificada en campo". Una zona "fusionada" no es activa ni cerrada. |
| Fusión | Unión automática de dos o más zonas activas cuando una alerta nueva queda a ≤ 500 m de todas ellas. Sobrevive la más antigua; las demás pasan a "fusionada en EA-…" y conservan su historial (RF-32). |
| Detección | Conjunto de alertas que se superponen entre sí, de forma transitiva (si A se superpone con B y B con C, A, B y C son una detección), aunque sean de la misma fuente. Es la unidad del factor de agrupación (RF-33). |
| Confirmación multifuente | Una zona está confirmada si contiene al menos una detección con alertas de dos o más fuentes satelitales distintas. Dos alertas de distinta fuente que no se superponen no confirman (RF-32, RF-33, RF-36). |
| Historial del lugar | Alertas o zonas anteriores a ≤ 500 m de una zona en los últimos 3 años (S-28), que no forman parte de ella (RF-32). |
| Zona viva | Parte de la zona que el sistema y los analistas actualizan en todo momento: geometría, alertas, origen, área, prioridad (y ajuste manual), marcas automáticas, marcas de hipótesis, estado, comentarios de estado y comparticiones (RF-16). |
| Contenido versionado | Parte de la zona que pertenece a una versión: análisis detallado, polígonos de cambio, notas de discrepancia, evaluación de humo y ficha (RF-16). |
| Versión de la zona | Contenedor numerado del contenido versionado. Estados: **en curso** (editable), **pendiente de revisión**, **validada**, **devuelta** y **compartida por urgencia**. Solo una versión en curso admite cambios; las validadas, devueltas y compartidas por urgencia son inmutables. Para continuar se crea una versión nueva que copia la anterior (RF-16). La **versión vigente** es la de número mayor. |
| Autor de una versión | Usuario que ejecutó el análisis de la versión o aceptó, editó o trazó un polígono de cambio en ella. Descartar candidatos no hace autor (RF-15). |
| Validación técnica | Revisión de una versión por un analista SIG que no es su autor: confirma polígonos, imágenes, cálculo y contenido (RF-16). |
| Revisión de contenido (no técnica) | Revisión de una versión por la coordinación, que no es SIG: confirma la claridad y pertinencia del contenido. La ficha la distingue de la validación técnica (RF-16, RF-17). |
| Ruta de urgencia | Compartición de una versión por su autor sin segunda revisión, con motivo obligatorio. La ficha lo indica (RF-16). |
| Ficha definitiva | PDF de una versión generado **una sola vez** al validarla o compartirla por urgencia, almacenado sin cambios y con su huella SHA-256 registrada. Toda descarga devuelve ese archivo (RF-17). |
| Ficha borrador | PDF generado a pedido de una versión no validada ni compartida por urgencia, con marca de agua "BORRADOR" (RF-17). |
| Prioridad | Puntaje de 0 a 100 de una zona, calculado como suma ponderada de 7 factores (RF-33). El **puntaje calculado** lo obtiene el sistema; el **puntaje ajustado** lo fija un analista con comentario (RF-34). El **puntaje vigente** es el ajustado si existe y, si no, el calculado. |
| Nivel de prioridad | Clasificación del puntaje vigente: alta (≥ 70), media (40–69) o baja (< 40) (S-17). |
| Desglose | Contribución de cada factor al puntaje, en puntos y con un texto explicativo (p. ej., "dentro de la reserva; 3 alertas en 4 semanas") (RF-33). |
| Versión de pesos | Conjunto numerado de los 7 pesos de priorización, con autor, fecha y motivo (RF-35). |
| Versión de parámetros de cálculo | Conjunto numerado de las constantes del sistema que usa el cálculo de prioridad, agrupación y marcas (S-01, S-14, S-15, S-17 a S-28). Solo cambia con una versión del sistema, no desde la interfaz. Cada puntaje registra la versión de pesos y la de parámetros que usó. |
| Marca de confianza | Aviso asociado a una zona sobre una condición que reduce la confianza de la detección. No oculta la zona ni cambia su puntaje (RF-36). |
| Marca del analista | Marca manual: "bruma o humo" (representación de la evaluación de humo de la versión) o una hipótesis en texto libre. Se distingue visualmente de las automáticas, se puede retirar con motivo y el sistema nunca la genera (RF-36, RD-17). |
| Evaluación de humo | Dato único de cada versión: "sin humo visible sobre el área de cambio" o "con humo". Solo se modifica en una versión en curso (RF-15). |
| Umbral de visualización | Umbral de nubosidad que el analista ajusta en cada análisis para marcar imágenes en el listado (RF-08). No afecta la validez. |
| Umbral de validez | Umbral de nubosidad del sistema (S-01 = 20 %) que usan la revisión de la ficha (RF-16), la marca de nubosidad (RF-36) y RD-07. No se edita en la interfaz. |
| Reapertura | Regreso automático de una zona cerrada al estado "nueva", con el indicador "reabierta" y su motivo (RF-37). |
| Última revisión del usuario | Fecha y hora en que un usuario marcó por última vez "Revisión completada" (RF-04). |
| Comentario del analista | Último comentario registrado en el historial de estados de la zona (RF-11). |
| Sector | Polígono que delimita un ámbito de trabajo de la ONG dentro de la RN Tambopata o su zona de amortiguamiento, con nombre y cuenca. Lo define la coordinación (RF-22). |
| Cuenca | Nombre de la cuenca hidrográfica a la que pertenece un sector (p. ej., "Tambopata" o "Malinowski"). Es un atributo del sector (RF-22). |
| Área de análisis | Polígono sobre el que se comparan imágenes de dos fechas en el análisis detallado de una zona (RF-05). |
| Polígono candidato | Polígono que el sistema propone como posible cambio, a partir de la diferencia de NDVI entre dos fechas (RF-23). |
| Polígono de cambio | Polígono decidido por un analista: un candidato aceptado o editado, o uno trazado por el analista. Su superficie es el **área de cambio** (RF-09). |
| Compartición | Registro de que una ficha o una exportación se entregó fuera del sistema a la jefatura de la RN Tambopata, a los guardaparques o equipo de campo, o a otro destinatario coordinado con la jefatura, con fecha, medio, contenido y referencia. El sistema no envía nada (RF-38, RD-19). |
| Ficha de zona | Documento PDF técnico de apoyo sobre una zona, dirigido a la jefatura de la RN Tambopata (RF-17). No es una alerta oficial ni determina causas. |
| Expediente de la zona | Paquete descargable con la ficha, los polígonos, las imágenes y un manifiesto de huellas, para trabajar sin conexión (RF-25). |
| Bitácora de auditoría | Registro de solo inserción de acciones relevantes (RNF-04). |
| Capa de referencia | Información geográfica oficial que se cruza con la zona o el área de cambio (límites de la reserva, derechos otorgados, comunidades nativas, etc.). |
| Derecho otorgado | Concesión o petitorio minero, concesión forestal (incluidas las castañeras) o concesión de conservación. Se muestra solo con su tipo de derecho, código y estado, nunca con el nombre de su titular (RD-18). |
| Detección propia | Cambio identificado por un analista que no proviene de una alerta ingerida. |
| Fecha de corte | Fecha a la que corresponde el contenido de una versión de una capa. En las cargas de alertas es solo informativa (RF-31). |
| Nubosidad | Porcentaje del área de análisis cubierto por nubes o sombras de nubes en una imagen, según la máscara de nubes del producto satelital. |
| Petitorio minero | Solicitud de concesión minera en trámite ante INGEMMET. |
| Reporte de campo | Observación de un guardaparque o monitor, con ubicación **puntual**, que un analista registra en el sistema (RF-21). |
| Zona de amortiguamiento | Franja alrededor de un ANP con restricciones de uso. En EcoAlert, la de la RN Tambopata según los límites oficiales del SERNANP. |
| Jefatura de la RN Tambopata | Unidad del SERNANP a cargo de la reserva. Es la autoridad: recibe fichas y capas, decide la verificación en campo y coordina la difusión (RD-19). |
| Cauce activo | Río de la capa de ríos. Una zona a ≤ 100 m (S-26) de un cauce activo recibe la marca "posible dinámica fluvial" (RF-36). |
| ANP / RN | Área Natural Protegida / Reserva Nacional. |
| RADD | *Radar for Detecting Deforestation*: alertas de pérdida de bosque basadas en radar Sentinel-1, que ven a través de las nubes. Se sincronizan desde GEE (RF-31). |
| GLAD | Alertas ópticas de pérdida de bosque de la Universidad de Maryland (Landsat). Su ingesta es Could (RF-31). |
| Sentinel-1 | Satélite de radar de apertura sintética del programa Copernicus. |
| Planet / NICFI | Imágenes ópticas de alta resolución del programa NICFI. Tienen restricciones de redistribución y no se usan en la v1 (RD-12). |
| EPSG:32719 | Código del sistema de coordenadas UTM, datum WGS84, zona 19 Sur. |
| EPSG:4326 | Coordenadas geográficas (latitud y longitud) en WGS84. |
| GEE | Google Earth Engine, plataforma de Google para consultar y procesar imágenes satelitales. |
| GeoBosques | Plataforma de monitoreo de bosques del Ministerio del Ambiente del Perú; referencia oficial de alertas en el país. |
| INGEMMET | Instituto Geológico, Minero y Metalúrgico del Perú, a cargo del catastro minero (GEOCATMIN). |
| MINAM | Ministerio del Ambiente del Perú. |
| QField / Avenza | Aplicaciones móviles de mapas que usan los guardaparques en campo sin conexión. |
| GDAL / ogrinfo | Biblioteca y utilidad de referencia para leer y validar formatos geográficos; se usa en las pruebas automatizadas. |
| MoSCoW | Técnica de priorización: *Must*, *Should*, *Could*, *Won't*. |
| NDVI | Índice de Vegetación de Diferencia Normalizada, calculado con las bandas roja e infrarroja cercana. Una caída del NDVI entre dos fechas indica pérdida de vegetación. |
| 2FA / TOTP | Autenticación de dos factores mediante un código temporal de un solo uso generado en una aplicación del celular. |
| VPS | Servidor privado virtual contratado en la nube. |
| Código seudónimo | Identificador de un informante con el formato `[A-Z]{2,4}-\d+` (p. ej., MON-07 o GP-12), que no revela su nombre. La correspondencia código–nombre la custodia la coordinación **fuera** del sistema (RF-21). |
| Huella SHA-256 | Resumen criptográfico de un archivo. Si el archivo cambia en un solo byte, la huella cambia; permite comprobar que una ficha no fue alterada (RF-17). |
| OSM | OpenStreetMap, cartografía abierta y colaborativa (licencia ODbL). |
| EXIF | Metadatos incrustados en una foto (ubicación GPS, dispositivo, fecha, autor). |
| p90 | Percentil 90: el valor que no se supera en el 90 % de las mediciones. |
| SERNANP | Servicio Nacional de Áreas Naturales Protegidas por el Estado. |
| SERFOR | Servicio Nacional Forestal y de Fauna Silvestre. |
| SIG | Sistema de Información Geográfica. |
| RF / RNF / RD | Requerimiento funcional / no funcional / de dominio. |
| CSV, XLSX, GeoJSON, Shapefile, GeoPackage, KML, PDF | Formatos de archivo: tabular de texto, hoja de cálculo Office Open XML, geográfico basado en JSON, geográfico de Esri, geográfico abierto basado en SQLite, geográfico basado en XML (Google Earth) y documento portable. |

---

## 2. Descripción general

### 2.1 Perspectiva del producto

EcoAlert es un sistema **nuevo**. No reemplaza a las fuentes oficiales ni emite alertas oficiales
(RD-19): sustituye el flujo manual actual (descarga de GeoBosques → script de GEE → QGIS → ficha
armada a mano) por un solo sistema que agrupa, prioriza y documenta con registro. Es una
aplicación web de tres capas: cliente web en el navegador, API de servicios y base de datos
geoespacial. Se despliega con Docker Compose en un VPS en la nube de bajo costo (RNF-11, RNF-12).
Los analistas siguen usando QGIS y Excel con los archivos que exporta el sistema (RF-18, RF-19), y
los guardaparques usan QField o Avenza con las capas para campo (RF-40).

**Interfaces con sistemas externos:**

| Sistema externo | Qué aporta | Tipo de integración en la v1 |
|---|---|---|
| Google Earth Engine | Imágenes Sentinel-2 y Landsat 8/9, sus metadatos y su máscara de nubes, y el cálculo de la diferencia de NDVI para proponer candidatos. | En línea, mediante la API de GEE con la cuenta no comercial de la ONG (RD-12). |
| RADD (vía GEE) | Alertas de pérdida de bosque basadas en radar Sentinel-1 (polígonos). | Sincronización automática semanal y a pedido del analista, mediante la API de GEE (RF-31). |
| GeoBosques (MINAM) | Alertas de pérdida de bosque (polígonos). | Carga de archivos por un analista, como ingesta acumulativa (RF-31). |
| INGEMMET (GEOCATMIN) | Catastro minero: concesiones y petitorios, con tipo de derecho, código y estado. | Carga de archivos por un analista (RF-03), con fecha de corte. **El nombre del titular no se importa** (RD-18). |
| SERNANP | Límites oficiales de la RN Tambopata y de su zona de amortiguamiento. | Carga de archivos (RF-03). |
| SERFOR | Concesiones forestales (incluidas las castañeras) y de conservación. | Carga de archivos (RF-03), sin titulares. |
| MINAM | Capa de ecosistemas inundables y aguajales, para la marca de confianza correspondiente (RF-36). | Carga de archivos (RF-03). Confirmar el conjunto de datos exacto (tema abierto). |
| Ministerio de Cultura | Comunidades nativas: Base de Datos de Pueblos Indígenas u Originarios (BDPI). | Carga de archivos (RF-03). Confirmar el conjunto de datos exacto y su licencia durante la construcción. |
| INEI | Límites departamentales, provinciales y distritales, para ubicar la zona (RF-17). | Carga de archivos (RF-03). Confirmar la fuente oficial vigente de límites (INEI o IGN). |
| OpenStreetMap | Ríos y vías, incluidas trochas informales que no figuran en la cartografía oficial. Solo como contexto. | Carga de archivos (RF-03); la ficha cita "© OpenStreetMap" y la fecha de descarga. |
| Copernicus Data Space Ecosystem | Imágenes Sentinel-2 gratuitas. | **No se integra en la v1.** Es la alternativa documentada si cambian las condiciones de GEE (RNF-15). |
| Planet / NICFI | Imágenes ópticas de alta resolución. | **No se integra en la v1**: no se puede redistribuir (RD-12). |
| GLAD | Alertas ópticas de pérdida de bosque. | Could (RF-31); fuera del alcance comprometido de la v1. |

Las capas de referencia se cargan como archivos y no se consultan en línea. Así cada análisis
queda asociado a una versión fija y fechada de cada capa (RD-06), y el sistema no depende de la
disponibilidad de servicios externos, salvo GEE para imágenes y alertas RADD.

Los casos de uso de esta línea base (UC-01 a UC-36; UC-23, UC-24 y UC-27 se retiraron junto con
RF-24 y RF-26) se describen en `casos_de_uso.md`. Cada RF de la sección 3.1 indica los casos de
uso que lo cubren.

### 2.2 Funciones del producto

| Área | Funciones | Requerimientos | Casos de uso |
|---|---|---|---|
| Ingesta y agrupación | Ingesta de alertas de GeoBosques y RADD, agrupación y fusión de zonas, historial del lugar. | RF-31, RF-32 | UC-03, UC-30, UC-31 |
| Priorización y confianza | Puntaje con nivel y desglose, ajuste manual, configuración versionada de pesos, marcas de confianza y reapertura automática. | RF-33 a RF-37 | UC-12, UC-17, UC-31, UC-32, UC-33 |
| Visualización territorial | Mapa único con capas activables, fechas de corte y zonas nuevas desde la última revisión del usuario. | RF-01 a RF-04 | UC-03, UC-04, UC-17 |
| Análisis detallado | Definir y guardar el área, elegir imágenes por nubosidad, comparar dos fechas, recibir polígonos candidatos y decidirlos, calcular el área, cruzar con capas, medir distancias y seguir el estado del análisis. | RF-05 a RF-10, RF-23, RF-29 | UC-05 a UC-10, UC-22 |
| Gestión de zonas | Estados, lista priorizada, origen, discrepancias, trazabilidad, versiones y revisión de la ficha. | RF-11 a RF-16 | UC-11 a UC-17 |
| Documentación, exportación y compartición | Ficha PDF con huella verificable, expediente, exportación de polígonos, listas y capas para campo, registro de exportaciones y de comparticiones. | RF-17 a RF-20, RF-25, RF-38, RF-40 | UC-18 a UC-21, UC-25, UC-26, UC-34, UC-36 |
| Registro de campo | Registro manual de reportes de campo. | RF-21 | UC-14 |
| Coordinación y administración | Cuentas, perfiles, roles, credenciales y sectores; consulta de la bitácora; supresión de datos personales; resumen mensual. | RF-22, RF-27, RF-28, RF-30, RF-39 | UC-01, UC-02, UC-28, UC-29, UC-35 |

RF-24 y RF-26 están retirados desde la v3.0 (sección 3.1).

### 2.3 Características del usuario

La v1 tiene **2 roles** y **3 usuarios**. Los roles no heredan permisos entre sí.

| Rol | Usuarios | Perfil | Uso del sistema | Permisos |
|---|---|---|---|---|
| Analista SIG | 2 | Especialistas SIG y analistas ambientales. Dominan QGIS, GEE y teledetección; no programan. | Diario o semanal: revisan las zonas nuevas y priorizadas, analizan imágenes, marcan estados, preparan fichas y exportaciones para campo. Trabajan en laptop desde la oficina de Puerto Maldonado o desde casa. | Todo lo operativo: capas y alertas, análisis, zonas, estados, prioridad, pesos, versiones, reportes de campo, fichas, exportaciones y comparticiones. **Validación técnica** de versiones de las que no son autores, nunca de las propias. |
| Coordinación | 1 | Coordinadora del programa. Conoce el dominio; **no es SIG**. | Semanal o mensual: consulta zonas y fichas, revisa el contenido de las fichas, revisa el resumen para sus reportes y administra el sistema. A menudo usa el celular durante viajes. | Consultar; **revisión de contenido (no técnica)** y devolución de fichas; bitácora; resumen mensual; usuarios, perfiles, credenciales y sectores; supresión de datos personales. **No** cambia estados, no ajusta prioridades, no configura pesos, no lanza análisis, no carga capas ni exporta datos geográficos o listas. |

**Partes interesadas sin cuenta en la v1:** la jefatura de la RN Tambopata (SERNANP) y los
guardaparques. Reciben fichas y exportaciones por fuera del sistema; cada entrega se registra
(RF-38).

**Matriz de permisos** (✔ permitido · — rechazado con 403, RNF-02). La prueba rol × acción de
RNF-02 recorre todas las filas:

| Acción | Analista SIG | Coordinación |
|---|:---:|:---:|
| Ver el mapa, las capas y sus fechas (RF-01, RF-02) | ✔ | ✔ |
| Marcar "Revisión completada" y filtrar lo nuevo (RF-04) | ✔ | ✔ |
| Ver la lista, el detalle, el análisis, el desglose, las marcas, el historial y las versiones de pesos y de parámetros (RF-12, RF-15, RF-33, RF-35, RF-36) | ✔ | ✔ |
| Cargar capas de referencia y archivos de alertas (RF-03, RF-31) | ✔ | — |
| Sincronizar RADD a pedido (RF-31) | ✔ | — |
| Definir y guardar áreas de análisis (RF-05, RF-06) | ✔ | — |
| Lanzar un análisis y reintentarlo (RF-07, RF-08, RF-29) | ✔ | — |
| Generar, aceptar, editar y descartar candidatos, y trazar polígonos (RF-09, RF-10, RF-23) | ✔ | — |
| Registrar o cambiar la evaluación de humo (RF-15) | ✔ | — |
| Crear zonas manuales (RF-13) | ✔ | — |
| Cambiar estados y reabrir manualmente (RF-11) | ✔ | — |
| Registrar notas de discrepancia (RF-14) | ✔ | — |
| Registrar reportes de campo (RF-21) | ✔ | — |
| Registrar y retirar marcas de hipótesis (RF-36) | ✔ | — |
| Ajustar la prioridad y quitar el ajuste (RF-34) | ✔ | — |
| Configurar los pesos de priorización (RF-35) | ✔ | — |
| Crear una versión nueva (RF-16) | ✔ | — |
| Enviar a revisión (RF-16) — solo el autor de la versión | ✔ | — |
| Validar una versión (RF-16) — el analista, validación técnica y nunca sobre una versión propia; la coordinación, revisión de contenido | ✔ | ✔ |
| Devolver una versión con observaciones (RF-16) — nunca sobre una versión propia | ✔ | ✔ |
| Compartir por la ruta de urgencia (RF-16) — solo el autor de la versión | ✔ | — |
| Generar fichas borrador y descargar fichas (RF-17) | ✔ | ✔ |
| Verificar una ficha (RF-17) | ✔ | ✔ |
| Exportar polígonos (RF-18) | ✔ | — |
| Exportar la lista de zonas (RF-19) | ✔ | — |
| Descargar expedientes (RF-25) | ✔ | — |
| Exportar capas GeoPackage y KML (RF-40) | ✔ | — |
| Registrar comparticiones (RF-38) | ✔ | — |
| Consultar y exportar la bitácora (RF-27) | ✔ | ✔ |
| Consultar el resumen mensual (RF-39) | ✔ | ✔ |
| Gestionar usuarios, editar perfiles y administrar credenciales (RF-22, RF-28) | — | ✔ |
| Gestionar sectores (RF-22) | — | ✔ |
| Suprimir datos personales (RF-30) | — | ✔ |

**Entorno de uso:** la conexión en Puerto Maldonado es inestable, se cae con las lluvias y puede
ser muy lenta (referencia: 1 Mbps, parámetro S-04). En campo no hay señal: lo único útil es lo que
se exportó antes de salir (RF-40). Los guardaparques y monitores **no son usuarios** de la v1: sus
reportes los registra un analista (RF-21).

### 2.4 Restricciones

| Tipo | Restricción | Referencia |
|---|---|---|
| Plazo | Versión operativa en 12 semanas, antes de la temporada seca (junio). | RD-15 |
| Costo | USD 0 en licencias de software; infraestructura de hasta USD 25 al mes (un VPS con respaldo externo). El sistema debe poder seguir operando cuando termine el proyecto financiado (2-3 años). | RNF-11 |
| Operación | La ONG no tiene personal de TI: despliegue con un comando y manual en español para analistas SIG. | RNF-12 |
| Fuentes de datos | Solo fuentes gratuitas. GEE se usa con cuenta no comercial, sujeta a sus cuotas y términos de uso, que se revisan una vez al año. Planet/NICFI no se usa en la v1 por sus restricciones de redistribución. | RD-12, RNF-15 |
| Autoridad | La jefatura de la RN Tambopata es la autoridad. EcoAlert no emite alertas oficiales ni envía información a terceros. | RD-19 |
| Causas | El sistema no determina ni etiqueta causas; las hipótesis solo las marca el analista. | RD-17 |
| Marco legal | Ley N.º 29733 de Protección de Datos Personales; consentimiento de las comunidades nativas; confidencialidad de las zonas en verificación, de las verificaciones planificadas y de los informantes; nunca se muestran titulares de derechos. | RD-09, RD-10, RD-11, RD-18 |
| Documentación técnica | Coordenadas en EPSG:32719 (EPSG:4326 para campo); mapas con escala y fecha; fuente y fecha de cada dato; la ficha es un documento técnico de apoyo, no una alerta oficial. | RD-01, RD-02, RD-03, RD-16 |
| Ámbito | RN Tambopata y su zona de amortiguamiento, según los límites oficiales del SERNANP. | RD-14 |
| Idioma | Español en la interfaz, las fichas y la documentación. | RNF-14 |
| Herramientas existentes | Las exportaciones deben leerse con QGIS y Excel, y las capas para campo con QField y Avenza. | RF-18, RF-19, RF-40 |

#### Parámetros del sistema

Los parámetros S-01 a S-13 se fijaron en la sesión de alineación del 2026-09-27 (ver
`revision_SRS.md`, sección 8). Los parámetros S-14 a S-28 surgen de la Sección C de la entrevista,
de `borradores/especificacion_realineacion_v3.md` y de la revisión técnica V-01 a V-26. Todos
deben confirmarse con el stakeholder real. **Por calibrar** significa que el valor se ajustará con
los analistas usando zonas reales.

Salvo los pesos (S-16, configurables por los analistas según RF-35) y el umbral de visualización de
RF-08, **todos los parámetros son constantes del sistema**: no se editan desde la interfaz y solo
cambian con una versión del sistema. Los que intervienen en la prioridad, la agrupación y las
marcas (S-01, S-14, S-15, S-17 a S-28) forman la **versión de parámetros de cálculo**, que cada
puntaje registra (RF-33).

| ID | Parámetro | Valor | Estado | Afecta a |
|---|---|---|---|---|
| S-01 | Umbral de validez de nubosidad dentro del área de análisis (y valor inicial del umbral de visualización). | 20 % | Definido | RF-08, RF-16, RF-36, RD-07 |
| S-02 | Tiempo máximo de un análisis de hasta 2,000 ha, incluida la propuesta de candidatos (p90). | 5 min | Definido | RNF-05 |
| S-03 | Pérdida máxima de trabajo ante un corte de conexión. | 30 s | Definido | RNF-07 |
| S-04 | Conexión de referencia en Puerto Maldonado. | 1 Mbps | Definido | RNF-08 |
| S-05 | Retención de las zonas, sus versiones, fichas y respaldos. | Mínimo 5 años; sin función de borrado de zonas en la v1 | Definido: permite la comparación histórica y los informes anuales (Sección C, P5-seg y P6-seg) | RNF-10 |
| S-06 | Tope mensual de infraestructura. | USD 25 | Definido | RNF-11 |
| S-07 | Expiración de sesión por inactividad. | 30 min | Definido | RNF-03 |
| S-08 | Radio del área de análisis por defecto alrededor de una alerta, un reporte o una zona. | 2.5 km (≈ 1,963 ha) | Definido | RF-05 |
| S-09 | Área mínima de un polígono candidato. | 0.5 ha (50 píxeles Sentinel-2) | Definido | RF-23 |
| S-10 | Umbral de caída de NDVI para proponer un candidato. | ΔNDVI ≤ −0.20 (valor inicial) | Por calibrar entre las semanas 4 y 6 con 10–15 zonas ya verificadas en campo: se evalúan los umbrales de −0.10 a −0.40 en pasos de 0.05 y se adopta el que cubre al menos el 50 % del área de al menos el 90 % de los claros, con no más de 5 candidatos falsos por cada 1,000 ha, y la mayor cobertura; si ninguno cumple, se adopta el de mayor cobertura y el desvío se registra como tema abierto | RF-23 |
| S-11 | Superficie máxima del área de análisis, después del recorte al ámbito (con advertencia por encima de 2,000 ha). | 10,000 ha | Definido | RF-05 |
| S-12 | Rango del radio del área alrededor de un punto. | 0.5–5 km | Definido | RF-05 |
| S-13 | Bloqueo por intentos fallidos de inicio de sesión. | 5 intentos → 15 min | Definido | RF-28 |
| S-14 | Distancia máxima de agrupación de alertas en una zona. | 500 m | Definido (Sección C) | RF-32 |
| S-15 | Ventana temporal de agrupación de alertas en una zona activa. | 90 días | Definido (Sección C) | RF-32 |
| S-16 | Pesos por defecto de la priorización (versión de pesos 1). | Ubicación 30, persistencia y crecimiento 20, agrupación 15, confirmación multifuente 15, cercanía a ríos 10, superficie 5, recencia 5 (suma 100) | Por calibrar por los analistas con los resultados de campo; el sistema nunca los reajusta solo | RF-33, RF-35 |
| S-17 | Umbrales de nivel de prioridad. | Alta ≥ 70; media 40–69; baja < 40 | Definido | RF-33 |
| S-18 | Desfase máximo entre la fecha de detección de la alerta más reciente de la zona (o la fecha de creación, si no tiene alertas) y la fecha de la imagen posterior del análisis. | 60 días | Definido | RF-36 |
| S-19 | Crecimiento del área de la zona que provoca su reapertura. | 20 % | Definido | RF-37 |
| S-20 | Franja de la zona de amortiguamiento "cercana al límite" de la reserva. | 2 km | Definido | RF-33 |
| S-21 | Normalización del factor de agrupación. | 10 detecciones = 1 | Definido; por calibrar con una versión del sistema | RF-33 |
| S-22 | Normalización del factor de superficie. | 10 ha = 1 | Definido; por calibrar con una versión del sistema | RF-33 |
| S-23 | Horizonte del factor de recencia. | 1 hasta 7 días; lineal hasta 0 a los 90 días | Definido; por calibrar con una versión del sistema | RF-33 |
| S-24 | Ventana del factor de persistencia y crecimiento. | 8 semanas (8 ventanas de 7 días) | Definido; por calibrar con una versión del sistema | RF-33 |
| S-25 | Cercanía a ríos. | 1 hasta 500 m; lineal hasta 0 a 2 km | Definido; por calibrar con una versión del sistema | RF-33 |
| S-26 | Distancia a un cauce activo para la marca "posible dinámica fluvial". | 100 m | Definido | RF-36 |
| S-27 | Área máxima de un "polígono pequeño sin confirmación". | Menos de 1 ha | Definido | RF-36 |
| S-28 | Horizonte del historial del lugar y de la agrupación con zonas cerradas. | 3 años | Definido (Sección C, P6-seg) | RF-32 |

#### Temas resueltos en la alineación

| Tema | Resolución | Requerimientos |
|---|---|---|
| Anonimato de informantes frente al sustento de cada dato | Código seudónimo opcional; la correspondencia con el nombre queda fuera del sistema, bajo custodia de la coordinación. | RF-21, RD-09, RD-11 |
| Integridad de la ficha | Ficha definitiva generada una sola vez, almacenada sin cambios, con huella SHA-256 registrada y verificable en el sistema. | RF-16, RF-17 |
| Dependencia de Google Earth Engine | Acceso a imágenes y alertas detrás de una interfaz común, y alternativas documentadas. Los términos de uso se revisan una vez al año. | RNF-15, RD-12 |
| Fuente de comunidades nativas, ríos y vías | BDPI del Ministerio de Cultura; OpenStreetMap para ríos y vías. | RF-03, 2.1 |
| Funciones legales (v2.0) | Fuera de la v1. Se conserva un registro liviano de compartición; las denuncias van por vías formales fuera del sistema. | RF-24 y RF-26 (retirados), RF-38, RD-19 |
| Revisión de la ficha como candado (Sección C, P7; C-10) | Validación técnica por el otro analista, revisión de contenido por la coordinación o ruta de urgencia del autor con motivo registrado. | RF-16 |
| Titulares del catastro (Sección C, P7; C-9, C-14) | El nombre del titular no se importa ni se muestra; solo tipo de derecho, código y estado. | RF-03, RF-10, RD-18 |
| Ciclo de vida de la versión y zona viva (revisión técnica V-03 a V-05) | Tabla de estados de versión; la zona viva se actualiza siempre y el contenido versionado solo en una versión en curso. | RF-15, RF-16, RF-17 |
| Reglas de agrupación y cálculo (revisión técnica V-06 a V-11) | Geometrías, distancia mínima, fusión de zonas, agrupación con zonas cerradas, fórmulas y constantes S-21 a S-28. | RF-32, RF-33, RF-36 |

#### Temas abiertos

- **Calibración de los pesos (S-16)** y de las constantes S-21 a S-28: los analistas los revisan
  con los resultados de campo ("verificada en campo", RF-11). Los pesos se cambian en RF-35; las
  constantes, con una versión del sistema. El sistema nunca reajusta nada solo (RF-35).
- **Desvío de calibración de S-10:** si ningún umbral cumple el criterio de S-10, se registra aquí
  el desvío y el umbral adoptado (RF-23).
- **Fuente de ecosistemas inundables y aguajales** (RF-36): confirmar el conjunto de datos del
  MINAM, su escala y su licencia.
- **Obligaciones de la Ley N.º 29733** (finalidad, consentimiento y registro del banco de datos
  personales ante la autoridad): las gestiona la ONG con asesoría especializada; el sistema aplica
  la minimización de datos (RD-09).
- **Alcance de la supresión** (RF-30) sobre las fichas definitivas almacenadas y sobre las
  exportaciones y fichas ya entregadas fuera del sistema.

---

## 3. Requerimientos específicos

Prioridades según MoSCoW: **Must** (obligatorio para aceptar la v1), **Should** (se entrega en la
v1 salvo que el plazo lo impida, con acuerdo del cliente) y **Could** (deseable; se entrega solo si
hay holgura, sin afectar a los Must ni a los Should). La fuente "P#" sin sección remite a la
Sección A de `transcript_entrevista.md`; las fuentes de la Sección B y la Sección C lo indican
(p. ej., "Sección C, P3"), y los hallazgos C-1 a C-18 son los de la Sección C.

**Criterios de aceptación.** Siguen el formato Given-When-Then: **Dado que** [precondición],
**cuando** [acción], **entonces** [resultado verificable]. Cada criterio prueba un solo
comportamiento y tiene un **identificador único e inmutable**, `RF-xx-AC-n`, que es la clave de
trazabilidad del proyecto:

- En el contrato de la API (`openapi.yaml`, S04-A2), cada endpoint referencia los IDs que implementa.
- En las pruebas automatizadas (S09-A1), cada caso de prueba se nombra con su ID, cambiando los
  guiones por guiones bajos (p. ej., `RF-01-AC-1` → `test_RF_01_AC_1`).
- Los criterios sin marca se automatizan contra la API o los archivos generados. Los marcados
  *(Prueba E2E de interfaz.)* se automatizan en la suite de pruebas de extremo a extremo del
  navegador. Los marcados *(Prueba de aceptación manual.)* no se automatizan.
- La convención completa y la línea base congelada de la v3.0 se detallan al final de la
  sección 3.1.

### 3.1 Requerimientos funcionales

#### RF-01 — Mapa único con capas

**Descripción:** El sistema debe mostrar en un mapa único 15 capas activables: límite de la RN Tambopata, zona de amortiguamiento, alertas de GeoBosques, alertas RADD, zonas de cambio (coloreadas por nivel de prioridad), reportes de campo, catastro minero (concesiones y petitorios), concesiones forestales (incluidas las castañeras), concesiones de conservación, comunidades nativas, ecosistemas inundables y aguajales, ríos, vías, límites distritales y sectores. Los derechos otorgados se muestran sin el nombre de su titular (RD-18).
**Prioridad:** Must | **Fuente:** P3, P6, P7; Sección C, P1, P3, P7 | **Casos de uso:** UC-04

**Criterios de aceptación:**

- **RF-01-AC-1** — **Dado que** un usuario autenticado con rol analista SIG o coordinación está en la aplicación, **cuando** solicita la lista de capas del mapa, **entonces** recibe estas 15 capas: límite de la RN Tambopata, zona de amortiguamiento, alertas de GeoBosques, alertas RADD, zonas de cambio, reportes de campo, catastro minero, concesiones forestales, concesiones de conservación, comunidades nativas, ecosistemas inundables y aguajales, ríos, vías, límites distritales y sectores.
- **RF-01-AC-2** — *(Prueba E2E de interfaz.)* **Dado que** la capa "Catastro minero" está activa y sus elementos se ven en el mapa, **cuando** el usuario la desactiva en el panel, **entonces** sus elementos dejan de mostrarse sin que la página se recargue (la URL y el estado de las demás capas no cambian).
- **RF-01-AC-3** — *(Prueba E2E de interfaz.)* **Dado que** la capa "Catastro minero" está desactivada, **cuando** el usuario la reactiva, **entonces** sus elementos vuelven a mostrarse en el mapa sin recargar la página.
- **RF-01-AC-4** — *(Prueba E2E de interfaz.)* **Dado que** existen zonas de nivel alto, medio y bajo, **cuando** el usuario activa la capa "Zonas de cambio", **entonces** cada zona se dibuja con el color de su nivel y la leyenda muestra los tres niveles con su color.
- **RF-01-AC-5** — **Dado que** la capa "Catastro minero" tiene elementos cargados, **cuando** se solicitan los atributos de una concesión a la API, **entonces** la respuesta contiene su tipo de derecho, código y estado, y ningún nombre de titular (RD-18).
- **RF-01-AC-6** — **Dado que** no hay una sesión iniciada, **cuando** se solicita el servicio de capas de la API, **entonces** el sistema responde 401 y no entrega ningún elemento de ninguna capa (RNF-01).
- **RF-01-AC-7** — *(Prueba E2E de interfaz.)* **Dado que** no hay una sesión iniciada, **cuando** se abre la URL de la pantalla del mapa, **entonces** el navegador es redirigido a la pantalla de inicio de sesión y no se muestra el mapa.

#### RF-02 — Fecha de actualización de capas y fuentes

**Descripción:** El sistema debe mostrar, para cada capa y fuente, su fecha de actualización o de corte. Para las alertas de GeoBosques, es la fecha de corte más reciente entre sus cargas (informativa, RF-31); para las alertas RADD, la fecha de la última sincronización exitosa.
**Prioridad:** Must | **Fuente:** P4, P7; Sección C, P4 | **Casos de uso:** UC-03, UC-04

**Criterios de aceptación:**

- **RF-02-AC-1** — **Dado que** todas las capas y fuentes tienen al menos una carga o sincronización, **cuando** un usuario autenticado consulta el panel de capas, **entonces** cada capa y fuente tiene su fecha en formato dd/mm/aaaa (p. ej., "15/08/2026").
- **RF-02-AC-2** — **Dado que** las alertas de GeoBosques se cargaron con fecha de corte 20/09/2026, **cuando** el usuario consulta el panel de capas, **entonces** la entrada "Alertas de GeoBosques" muestra "20/09/2026".
- **RF-02-AC-3** — **Dado que** la capa del catastro minero muestra la fecha de corte 01/07/2026, **cuando** un analista carga una versión nueva con fecha de corte 15/09/2026 (RF-03), **entonces** el panel de capas muestra "15/09/2026" para esa capa.
- **RF-02-AC-4** — **Dado que** la última sincronización exitosa de RADD fue el 21/09/2026 y la del 28/09/2026 falló, **cuando** el usuario consulta el panel de capas, **entonces** la entrada "Alertas RADD" sigue mostrando "21/09/2026".

#### RF-03 — Carga y versionado de capas de referencia

**Descripción:** Un analista debe poder cargar o actualizar una capa de referencia indicando su fuente y fecha de corte. El sistema debe conservar las versiones anteriores de la capa. Al cargar, el analista **asigna las columnas del archivo** a los atributos del tipo de capa; las columnas no asignadas se descartan y no se almacenan. El sistema valida el **tipo de geometría** de cada tipo de capa:

| Tipo de capa | Geometría | Atributos obligatorios |
|---|---|---|
| Catastro minero (concesiones y petitorios) | Polígono | código, tipo de derecho (concesión / petitorio), estado |
| Concesiones forestales (incluidas castañeras) y de conservación | Polígono | código, tipo de derecho, estado |
| Límite de la RN Tambopata, zona de amortiguamiento y comunidades nativas | Polígono | código, nombre |
| Ecosistemas inundables y aguajales | Polígono | código, tipo de ecosistema |
| Límites distritales | Polígono | código de ubigeo, distrito, provincia, departamento |
| Ríos y vías | Línea | nombre (puede estar vacío) |

Los tipos de capa de derechos otorgados **no tienen ningún atributo para el titular**: el nombre del titular nunca se importa (RD-18). Los análisis nuevos usan, para cada capa, la versión con la **fecha de corte más reciente**, no la última cargada. Las **alertas de GeoBosques no siguen esta semántica de versiones**: su carga usa el mismo formulario y la misma validación de formato, sistema de coordenadas y asignación de columnas (código, fecha de detección; geometría polígono), pero es una ingesta acumulativa (RF-31).
**Prioridad:** Must | **Fuente:** P4 (implícito); Sección C, P7 | **Casos de uso:** UC-03

**Criterios de aceptación:**

- **RF-03-AC-1** — **Dado que** un analista tiene un Shapefile comprimido en .zip con un archivo .prj que declara EPSG:4326, **cuando** lo carga como catastro minero indicando la fuente "INGEMMET" y la fecha de corte 15/09/2026, **entonces** el sistema acepta la carga y almacena las geometrías en EPSG:32719.
- **RF-03-AC-2** — **Dado que** un analista tiene un GeoJSON en EPSG:4326 con un punto de control de coordenadas conocidas, **cuando** lo carga con fuente y fecha de corte, **entonces** el sistema lo acepta y el punto de control almacenado coincide con su transformación a EPSG:32719 (calculada con pyproj) con una diferencia de 1 m o menos.
- **RF-03-AC-3** — **Dado que** un analista completa el formulario de carga con un archivo válido y la fecha de corte, **cuando** envía la carga sin indicar la fuente, **entonces** el sistema la rechaza con un mensaje que indica que falta la fuente y no crea ninguna versión nueva.
- **RF-03-AC-4** — **Dado que** un analista completa el formulario de carga con un archivo válido y la fuente, **cuando** envía la carga sin indicar la fecha de corte, **entonces** el sistema la rechaza con un mensaje que indica que falta la fecha de corte y no crea ninguna versión nueva.
- **RF-03-AC-5** — **Dado que** un analista tiene un Shapefile .zip sin archivo .prj, **cuando** lo carga con fuente y fecha de corte, **entonces** el sistema lo rechaza con un mensaje que indica que el archivo no declara su sistema de coordenadas.
- **RF-03-AC-6** — **Dado que** un analista tiene un archivo en un formato distinto de Shapefile .zip o GeoJSON (p. ej., .kml), **cuando** intenta cargarlo, **entonces** el sistema lo rechaza con un mensaje que indica los formatos aceptados.
- **RF-03-AC-7** — **Dado que** un analista carga como capa de concesiones forestales un archivo cuyas geometrías son puntos, **cuando** envía la carga, **entonces** el sistema la rechaza indicando que ese tipo de capa exige polígonos, y no crea ninguna versión.
- **RF-03-AC-8** — **Dado que** un analista carga como capa de ríos un archivo cuyas geometrías son polígonos, **cuando** envía la carga, **entonces** el sistema la rechaza indicando que ese tipo de capa exige líneas.
- **RF-03-AC-9** — **Dado que** la capa del catastro minero tiene una versión con fecha de corte 01/07/2026, **cuando** un analista carga una versión nueva con fecha de corte 15/09/2026, **entonces** el historial de la capa lista ambas versiones, cada una con su fecha de corte, y la versión del 01/07/2026 sigue siendo consultable.
- **RF-03-AC-10** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** invoca directamente el servicio de carga de capas de la API, **entonces** la API responde 403 y no crea ninguna versión (RNF-02).
- **RF-03-AC-11** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está autenticado, **cuando** abre el panel de capas, **entonces** no ve la opción de cargar o actualizar capas.
- **RF-03-AC-12** — **Dado que** un analista carga una capa del catastro minero cuyo archivo no tiene ninguna columna asignable a "código", **cuando** envía la carga, **entonces** el sistema la rechaza indicando el atributo obligatorio que falta y no crea ninguna versión.
- **RF-03-AC-13** — **Dado que** un analista carga un archivo de alertas con columnas "ID_ALERTA" y "F_DETEC", **cuando** las asigna a "código" y "fecha de detección" y envía la carga, **entonces** el sistema la acepta y cada alerta ingerida tiene esos valores en sus atributos.
- **RF-03-AC-14** — **Dado que** el catastro minero tiene una versión con fecha de corte 15/09/2026, **cuando** un analista carga después una versión con fecha de corte 01/08/2026, **entonces** los análisis nuevos siguen usando la versión del 15/09/2026, y la del 01/08/2026 queda en el historial.
- **RF-03-AC-15** — **Dado que** un analista carga un archivo del catastro minero con una columna "TITULAR", **cuando** completa la carga, **entonces** ni la capa almacenada ni la respuesta de la API para sus elementos contienen el valor de "TITULAR" (RD-18).
- **RF-03-AC-16** — **Dado que** un analista está asignando las columnas de un archivo del catastro minero con una columna "TITULAR", **cuando** consulta los atributos de destino disponibles, **entonces** ninguno corresponde al titular.

#### RF-04 — Zonas nuevas desde la última revisión del usuario

**Descripción:** El sistema debe indicar en el mapa y en la lista, **para cada usuario**, las zonas en las que ocurrió alguno de estos eventos **después de su última revisión**: (a) la zona se creó; (b) la zona se reabrió automáticamente (RF-37); (c) la zona recibió una **alerta nueva para el usuario** (fecha de ingesta posterior a su última revisión). La última revisión es la fecha y hora en que el usuario usó por última vez la acción "Revisión completada"; si nunca la usó, es la fecha de creación de su cuenta. Ningún otro evento (p. ej., el recálculo diario de la prioridad) activa el indicador. El usuario puede filtrar para ver solo esas zonas. La marca de un usuario no afecta a los demás.
**Prioridad:** Must | **Fuente:** P3; Sección C, P3, P7 (C-1) | **Casos de uso:** UC-04, UC-17

**Criterios de aceptación:**

- **RF-04-AC-1** — **Dado que** la última revisión del analista A fue el 20/09/2026 a las 08:00 y existe una zona creada el 22/09/2026, **cuando** A consulta las zonas, **entonces** esa zona tiene el indicador "nueva desde tu última revisión".
- **RF-04-AC-2** — **Dado que** la última revisión del analista A fue el 20/09/2026 y una zona creada el 18/09/2026 no tuvo ninguno de los eventos de RF-04 después, **cuando** A consulta las zonas, **entonces** esa zona no tiene el indicador.
- **RF-04-AC-3** — **Dado que** la última revisión del analista A fue el 20/09/2026 y una zona creada el 15/09/2026 recibió una alerta con fecha de detección 10/09/2026 ingerida el 23/09/2026, **cuando** A consulta las zonas, **entonces** esa zona tiene el indicador.
- **RF-04-AC-4** — **Dado que** la última revisión del analista A fue el 20/09/2026 y una zona fue reabierta automáticamente el 24/09/2026 (RF-37), **cuando** A consulta la lista de zonas, **entonces** la zona tiene el indicador y la etiqueta "reabierta".
- **RF-04-AC-5** — **Dado que** la última revisión del analista A fue el 20/09/2026 y desde entonces la única novedad de una zona es que su puntaje cambió por el recálculo diario, **cuando** A consulta las zonas, **entonces** esa zona no tiene el indicador.
- **RF-04-AC-6** — **Dado que** el analista A y el analista B ven la misma zona con el indicador, **cuando** A usa "Revisión completada" y vuelve a consultar las zonas, **entonces** A ya no ve el indicador en esa zona.
- **RF-04-AC-7** — **Dado que** el analista A y el analista B ven la misma zona con el indicador, **cuando** A usa "Revisión completada", **entonces** B sigue viendo el indicador en esa zona.
- **RF-04-AC-8** — **Dado que** existen 4 zonas nuevas desde la última revisión del usuario y 20 que no lo son, **cuando** el usuario aplica el filtro "Solo nuevas desde mi última revisión", **entonces** la lista muestra exactamente esas 4 zonas, en el orden de RF-12.
- **RF-04-AC-9** — **Dado que** la coordinación creó el 25/09/2026 la cuenta de un analista que nunca usó "Revisión completada", **cuando** ese analista consulta las zonas por primera vez, **entonces** tienen el indicador exactamente las zonas creadas, reabiertas automáticamente o con alertas ingeridas después del 25/09/2026.

#### RF-05 — Definición del área de análisis

**Descripción:** El analista debe poder dibujar un polígono en el mapa o seleccionar un área alrededor de una alerta (centrada en su centroide), un reporte de campo o una zona como área de análisis de una zona. El radio del área alrededor de un punto va de 0.5 a 5 km (S-12). El área debe intersectar el ámbito del sistema, la RN Tambopata y su zona de amortiguamiento (RD-14): un área totalmente fuera se rechaza, y la parte que queda fuera de un área parcialmente dentro se recorta con aviso. El límite de 10,000 ha (S-11) se aplica **después del recorte**. Por encima de 2,000 ha, el sistema advierte que el tiempo de RNF-05 no está garantizado.
**Prioridad:** Must | **Fuente:** P3, P7; Sección C, P5-seg | **Casos de uso:** UC-05

**Criterios de aceptación:**

- **RF-05-AC-1** — **Dado que** un analista está en el mapa, **cuando** envía un triángulo válido (3 vértices, el mínimo) dentro del ámbito como área de análisis, **entonces** el polígono queda establecido como área de análisis.
- **RF-05-AC-2** — **Dado que** un analista selecciona una alerta dentro del ámbito, a más de 2.5 km de su borde, **cuando** elige "Analizar alrededor" sin cambiar el radio, **entonces** el sistema genera un área circular centrada en el centroide de la alerta con radio de 2.5 km (S-08), cuya superficie es 1,963 ha ± 1 %.
- **RF-05-AC-3** — **Dado que** un analista selecciona un reporte de campo, **cuando** elige "Analizar alrededor", **entonces** el sistema genera un área circular de 2.5 km de radio (S-08) centrada en el punto del reporte.
- **RF-05-AC-4** — **Dado que** el sistema propone un área circular de 2.5 km alrededor de una alerta, **cuando** el analista cambia el radio a 1 km antes de confirmar, **entonces** el área confirmada es un círculo de 1 km de radio (314.16 ha ± 1 %).
- **RF-05-AC-5** — **Dado que** un analista dibuja un polígono autointersectado (forma de moño), **cuando** intenta confirmarlo como área de análisis, **entonces** el sistema lo rechaza con un mensaje que explica que el polígono se cruza a sí mismo y no crea el área.
- **RF-05-AC-6** — **Dado que** un analista dibuja una figura de solo 2 vértices, **cuando** intenta confirmarla como área de análisis, **entonces** el sistema la rechaza con un mensaje que explica que un polígono requiere al menos tres vértices.
- **RF-05-AC-7** — **Dado que** un analista dibuja un área de 3,000 ha dentro del ámbito, **cuando** la confirma, **entonces** el sistema la acepta y muestra la advertencia de que el tiempo de análisis no está garantizado por encima de 2,000 ha.
- **RF-05-AC-8** — **Dado que** un analista dibuja un área de 12,000 ha totalmente dentro del ámbito, **cuando** intenta confirmarla, **entonces** el sistema la rechaza indicando el límite de 10,000 ha.
- **RF-05-AC-9** — **Dado que** el sistema propone un área circular alrededor de una alerta, **cuando** el analista cambia el radio a 6 km, **entonces** el sistema rechaza el valor indicando el límite de 5 km.
- **RF-05-AC-10** — **Dado que** un analista dibuja un polígono totalmente fuera de la RN Tambopata y de su zona de amortiguamiento (p. ej., en el Parque Nacional del Manu), **cuando** intenta confirmarlo, **entonces** el sistema lo rechaza indicando que está fuera del ámbito del sistema.
- **RF-05-AC-11** — **Dado que** un analista dibuja un polígono con el 70 % de su superficie dentro del ámbito, **cuando** lo confirma, **entonces** el sistema lo recorta al ámbito, informa la superficie excluida y el área de análisis es solo la parte recortada.
- **RF-05-AC-12** — **Dado que** un analista dibuja un polígono de 12,000 ha del que 9,000 ha quedan dentro del ámbito, **cuando** lo confirma, **entonces** el sistema lo acepta recortado, con un área de análisis de 9,000 ha.
- **RF-05-AC-13** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta definir un área de análisis por la API, **entonces** la API responde 403 y no se crea el área.
- **RF-05-AC-14** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en el mapa, **cuando** revisa las herramientas disponibles, **entonces** no ve la opción de definir un área de análisis.

#### RF-06 — Guardado de áreas de análisis

**Descripción:** El analista debe poder guardar un área de análisis con un nombre y reutilizarla en análisis posteriores.
**Prioridad:** Should | **Fuente:** P3, P7; Sección C, P5-seg | **Casos de uso:** UC-06

**Criterios de aceptación:**

- **RF-06-AC-1** — **Dado que** un analista tiene un área de análisis definida, **cuando** la guarda con el nombre "Malinowski Norte", cierra sesión y vuelve a iniciarla, **entonces** "Malinowski Norte" aparece en la lista de áreas guardadas.
- **RF-06-AC-2** — **Dado que** existe el área guardada "Malinowski Norte", **cuando** el analista la selecciona, **entonces** se carga como área de análisis con los mismos vértices y la misma superficie en hectáreas (dos decimales) que al guardarla.
- **RF-06-AC-3** — **Dado que** el área "Malinowski Norte" se usó en un análisis anterior, **cuando** el analista la selecciona para un análisis nuevo con otras fechas, **entonces** el nuevo análisis usa esa geometría sin redibujarla y el área guardada no se modifica.
- **RF-06-AC-4** — **Dado que** un analista tiene un área de análisis definida, **cuando** intenta guardarla con el nombre vacío, **entonces** el sistema rechaza el guardado con un mensaje que pide un nombre.
- **RF-06-AC-5** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta guardar un área de análisis por la API, **entonces** la API responde 403 y no se guarda ninguna área.

#### RF-07 — Comparación de imágenes de dos fechas

**Descripción:** El analista debe poder comparar las imágenes satelitales de dos fechas elegidas libremente sobre el área de análisis. Cada comparación pertenece a una zona y es el análisis detallado de su versión en curso (RF-15).
**Prioridad:** Must | **Fuente:** P3, P7; Sección C, P3, P7 | **Casos de uso:** UC-07

**Criterios de aceptación:**

- **RF-07-AC-1** — **Dado que** hay imágenes disponibles del área de análisis para el 15/08/2025 y el 15/08/2026, **cuando** el analista elige esas dos fechas, **entonces** el sistema acepta la selección de años distintos y ejecuta la comparación (RD-08).
- **RF-07-AC-2** — *(Prueba E2E de interfaz.)* **Dado que** se eligieron dos fechas con imágenes disponibles, **cuando** se muestra la comparación, **entonces** ambas imágenes aparecen lado a lado y recortadas al área de análisis (no se muestran píxeles fuera del área).
- **RF-07-AC-3** — *(Prueba E2E de interfaz.)* **Dado que** la comparación está en pantalla, **cuando** el analista desplaza o hace zoom en la imagen izquierda, **entonces** la imagen derecha queda con el mismo centro y el mismo nivel de zoom.
- **RF-07-AC-4** — *(Prueba E2E de interfaz.)* **Dado que** la comparación se muestra en color verdadero, **cuando** el analista elige "falso color con infrarrojo cercano", **entonces** ambas imágenes cambian a esa composición.
- **RF-07-AC-5** — *(Prueba E2E de interfaz.)* **Dado que** la comparación se muestra en falso color, **cuando** el analista elige "color verdadero", **entonces** ambas imágenes vuelven a color verdadero.
- **RF-07-AC-6** — **Dado que** terminó una comparación, **cuando** se consultan sus imágenes en la API, **entonces** cada una tiene su fecha de adquisición (dd/mm/aaaa), su sensor (p. ej., "Sentinel-2" o "Landsat 9") y su nubosidad en el área (RF-08).
- **RF-07-AC-7** — **Dado que** no existe ninguna imagen del área para una fecha, **cuando** el analista intenta elegir esa fecha, **entonces** el sistema rechaza la selección e indica que no hay imágenes disponibles para esa fecha.
- **RF-07-AC-8** — **Dado que** la zona EA-2026-014 tiene su versión 2 en curso, **cuando** un analista lanza una comparación desde esa zona y termina, **entonces** la comparación queda como el análisis detallado de la versión 2 de EA-2026-014.
- **RF-07-AC-9** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta ejecutar una comparación de imágenes por la API, **entonces** la API responde 403 y no se crea ningún análisis.
- **RF-07-AC-10** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en el detalle de una zona, **cuando** revisa las acciones disponibles, **entonces** no ve la opción de comparar imágenes.

#### RF-08 — Listado de imágenes y nubosidad

**Descripción:** Para un área y un rango de fechas, el sistema debe listar las imágenes Sentinel-2 y Landsat 8/9 disponibles con su porcentaje de nubosidad **dentro del área de análisis**, calculado con la máscara de nubes del producto, y marcar las que superen el **umbral de visualización** del análisis, configurable entre 0 y 100 % (valor inicial S-01). Este umbral solo afecta el listado; la validez de una imagen para la ficha y la marca de nubosidad usan siempre el **umbral de validez S-01**, que no se edita en la interfaz (RF-16, RF-36, RD-07).
**Prioridad:** Must | **Fuente:** P3, P4, P6; Sección C, P3, P4 | **Casos de uso:** UC-08

**Criterios de aceptación:**

- **RF-08-AC-1** — **Dado que** hay un área de análisis definida, **cuando** el analista consulta el rango 01/06/2026–30/09/2026, **entonces** el sistema lista las imágenes Sentinel-2 y Landsat 8/9 disponibles, cada una con fecha, sensor y porcentaje de nubosidad.
- **RF-08-AC-2** — **Dado que** una imagen tiene 60 % de nubosidad en la escena completa y 5 % dentro del área de análisis según su máscara de nubes, **cuando** aparece en el listado, **entonces** su nubosidad se muestra como 5 %.
- **RF-08-AC-3** — **Dado que** el umbral de visualización está en su valor inicial de 20 %, **cuando** el listado incluye una imagen con 35 % de nubosidad en el área y otra con 5 %, **entonces** la de 35 % aparece marcada y la de 5 % no.
- **RF-08-AC-4** — **Dado que** el umbral de visualización es de 20 %, **cuando** el listado incluye una imagen con exactamente 20 % de nubosidad en el área, **entonces** esa imagen no aparece marcada (solo se marcan las que lo superan).
- **RF-08-AC-5** — **Dado que** una imagen con 35 % de nubosidad aparece marcada con el umbral de visualización de 20 %, **cuando** el analista cambia ese umbral a 40 %, **entonces** esa imagen deja de estar marcada sin volver a consultar el rango.
- **RF-08-AC-6** — **Dado que** el umbral de visualización es de 20 %, **cuando** el analista intenta fijarlo en 120, **entonces** el sistema rechaza el valor con un mensaje y el umbral sigue en 20 %.
- **RF-08-AC-7** — **Dado que** el umbral de visualización es de 20 %, **cuando** el analista intenta fijarlo en "abc", **entonces** el sistema rechaza el valor con un mensaje y el umbral sigue en 20 %.
- **RF-08-AC-8** — **Dado que** un analista cambió el umbral de visualización a 30 % en su análisis, **cuando** otro analista abre un análisis nuevo, **entonces** el umbral de visualización del análisis nuevo es 20 %, y el primer análisis conserva y registra el 30 % (RF-15).
- **RF-08-AC-9** — **Dado que** el umbral de validez S-01 es 20 %, **cuando** un usuario de cualquier rol intenta modificarlo por la API, **entonces** no existe ninguna operación para hacerlo (404 o 405) y S-01 sigue en 20 %.

#### RF-09 — Cálculo del área de cambio

**Descripción:** El sistema debe calcular en hectáreas, con dos decimales y en la proyección EPSG:32719, el área de cada polígono de cambio del análisis de una versión: un candidato aceptado o editado (RF-23), o un polígono que el analista traza sobre las imágenes comparadas.
**Prioridad:** Must | **Fuente:** P1, P6, P7; Sección C, P1 | **Casos de uso:** UC-09

**Criterios de aceptación:**

- **RF-09-AC-1** — **Dado que** una versión tiene un polígono de cambio cuadrado de 100 m × 100 m en EPSG:32719, **cuando** el sistema calcula su área, **entonces** informa "1.00 ha".
- **RF-09-AC-2** — **Dado que** una versión tiene polígonos de cambio de 25,000 m² y de 30,000 m², **cuando** se consultan sus áreas, **entonces** aparecen como "2.50 ha" y "3.00 ha" (siempre con dos decimales).
- **RF-09-AC-3** — **Dado que** una versión tiene dos polígonos de cambio de 1.00 ha y 2.50 ha, **cuando** el usuario consulta el área de cambio, **entonces** el sistema muestra el área de cada polígono y el total "3.50 ha".
- **RF-09-AC-4** — **Dado que** un polígono de cambio de referencia está definido en EPSG:4326, **cuando** el sistema calcula su área, **entonces** el resultado coincide, con diferencia de 0.01 ha o menos, con el área del mismo polígono reproyectado a EPSG:32719 y calculada con pyproj y shapely.
- **RF-09-AC-5** — **Dado que** una versión tiene un candidato aceptado, un candidato editado y un polígono trazado por el analista, **cuando** el sistema calcula las áreas, **entonces** calcula el área de cada uno de los tres y los suma en el total.
- **RF-09-AC-6** — **Dado que** una versión tiene un candidato de 1.20 ha no aceptado y un polígono de cambio de 1.00 ha, **cuando** el sistema calcula el total, **entonces** el total es "1.00 ha" y el candidato no aparece con área de cambio.

#### RF-10 — Superposiciones y distancias

**Descripción:** El sistema debe informar si el área de cambio de la versión (o, si aún no tiene polígonos de cambio, la geometría de la zona) se superpone con estas capas: RN Tambopata, zona de amortiguamiento, catastro minero (concesiones y petitorios), concesiones forestales (incluidas las castañeras), concesiones de conservación y comunidades nativas. Para la reserva, la zona de amortiguamiento y las comunidades nativas indica nombre y código; para los derechos otorgados indica **tipo de derecho, código y estado, nunca el titular** (RD-18). Además, debe informar la **distancia en metros** (entero, distancia mínima en EPSG:32719) al río y a la vía más cercanos, con su nombre si lo tienen; si los cruza, la distancia es 0 m. Ríos, vías, límites distritales y sectores **no** se reportan como superposiciones: son capas de contexto. Estas distancias son las del análisis; la priorización mide siempre sobre la geometría de la zona (RF-33).
**Prioridad:** Must | **Fuente:** P3; Sección C, P3, P7 | **Casos de uso:** UC-10

**Criterios de aceptación:**

- **RF-10-AC-1** — **Dado que** un área de cambio cruza una concesión minera y la zona de amortiguamiento, **cuando** se calcula la superposición, **entonces** el sistema lista la concesión con su tipo de derecho "concesión", su código y su estado, y la zona de amortiguamiento con su nombre y su código.
- **RF-10-AC-2** — **Dado que** un área de cambio cruza la RN Tambopata y el territorio de una comunidad nativa, **cuando** se calcula la superposición, **entonces** el sistema lista ambos elementos con su nombre y su código.
- **RF-10-AC-3** — **Dado que** un área de cambio cruza un petitorio minero, **cuando** se calcula la superposición, **entonces** el sistema lista el petitorio con su tipo de derecho "petitorio", su código y su estado.
- **RF-10-AC-4** — **Dado que** un área de cambio cruza una concesión forestal castañera, **cuando** se calcula la superposición, **entonces** el sistema la lista con su tipo de derecho, su código y su estado, y ningún nombre de titular.
- **RF-10-AC-5** — **Dado que** un área de cambio no cruza ninguna capa de referencia, **cuando** se calcula la superposición, **entonces** el sistema muestra explícitamente "No hay superposiciones" en lugar de una lista vacía.
- **RF-10-AC-6** — **Dado que** la superposición usa la versión del 15/09/2026 del catastro minero, **cuando** se consulta el resultado, **entonces** junto a cada capa usada aparece la fecha de corte de su versión (p. ej., "Catastro minero, corte 15/09/2026") (RD-06).
- **RF-10-AC-7** — **Dado que** el río más cercano a un área de cambio es el Malinowski a 212.4 m y la vía más cercana está a 1,530.2 m, **cuando** se calculan las distancias, **entonces** el sistema muestra "Río Malinowski: 212 m" y la vía con "1,530 m", y cada valor difiere en 1 m o menos del calculado con pyproj y shapely como distancia mínima en EPSG:32719.
- **RF-10-AC-8** — **Dado que** un área de cambio cruza una concesión forestal y una vía, **cuando** se calcula la superposición, **entonces** el sistema lista la concesión forestal, no lista la vía como superposición y muestra la distancia a la vía como "0 m".
- **RF-10-AC-9** — **Dado que** la versión vigente de una zona aún no tiene polígonos de cambio, **cuando** se consultan sus superposiciones y distancias, **entonces** se calculan con la geometría de la zona y el resultado indica "calculado sobre la geometría de la zona".

#### RF-11 — Estados de zona e historial

**Descripción:** El sistema debe registrar el estado de cada zona y guardar el historial de cambios con el usuario, la fecha y hora, y el comentario o motivo de cada cambio. Toda zona nueva inicia como **nueva**. Solo el analista cambia estados manualmente; las zonas no se eliminan. El estado es parte de la zona viva: se puede cambiar aunque la versión vigente esté bloqueada (RF-16). Las transiciones permitidas son:

| Desde | Hacia | Condición | Quién |
|---|---|---|---|
| Nueva | En revisión | — | Analista SIG |
| Nueva | Descartada | Motivo obligatorio | Analista SIG |
| En revisión | Revisada | Comentario obligatorio | Analista SIG |
| En revisión | Requiere verificación | Comentario obligatorio | Analista SIG |
| En revisión | Descartada | Motivo obligatorio | Analista SIG |
| Requiere verificación | Verificada en campo | Resultado ("confirmado" o "no confirmado") y comentario obligatorios | Analista SIG |
| Requiere verificación | En revisión | Motivo obligatorio | Analista SIG |
| Verificada en campo | En revisión | Motivo obligatorio | Analista SIG |
| Revisada, Descartada | En revisión | Reapertura manual, motivo obligatorio; conserva el ajuste de prioridad (RF-34) | Analista SIG |
| Revisada, Descartada | Nueva | Reapertura automática (RF-37); retira el ajuste de prioridad | Sistema |
| Cualquiera | Fusionada (en EA-…) | Fusión automática (RF-32); estado final | Sistema |

**Prioridad:** Must | **Fuente:** P3, P7; Sección C, P2, P2-seg, P7 (C-7) | **Casos de uso:** UC-12, UC-21

**Criterios de aceptación:**

- **RF-11-AC-1** — **Dado que** el sistema crea una zona a partir de alertas (RF-32), **cuando** se guarda, **entonces** la zona tiene el estado "nueva".
- **RF-11-AC-2** — **Dado que** existe una zona, **cuando** se intenta asignarle por la API un estado fuera de la tabla (p. ej., "archivado"), **entonces** el sistema rechaza la operación y el estado no cambia.
- **RF-11-AC-3** — **Dado que** una zona está en "nueva", **cuando** un analista la pasa a "en revisión", **entonces** el sistema acepta la transición.
- **RF-11-AC-4** — **Dado que** una zona está en "nueva", **cuando** un analista la pasa a "descartada" con el motivo "sombra de nube en la alerta", **entonces** el sistema acepta la transición y el historial registra el motivo.
- **RF-11-AC-5** — **Dado que** una zona está en "en revisión", **cuando** un analista la pasa a "revisada" con un comentario, **entonces** el sistema acepta la transición.
- **RF-11-AC-6** — **Dado que** una zona está en "en revisión", **cuando** un analista intenta pasarla a "revisada" sin comentario, **entonces** el sistema rechaza la operación y la zona sigue en "en revisión".
- **RF-11-AC-7** — **Dado que** una zona está en "en revisión", **cuando** un analista la pasa a "requiere verificación" con el comentario "posibles pozas junto al afluente", **entonces** el sistema acepta la transición y el historial muestra el comentario.
- **RF-11-AC-8** — **Dado que** una zona está en "en revisión", **cuando** un analista intenta pasarla a "descartada" sin motivo, **entonces** el sistema rechaza la operación y la zona sigue en "en revisión".
- **RF-11-AC-9** — **Dado que** una zona está en "en revisión", **cuando** un analista la pasa a "descartada" con el motivo "cambio de cauce estacional", **entonces** el sistema acepta la transición y el historial registra el motivo.
- **RF-11-AC-10** — **Dado que** una zona está en "requiere verificación", **cuando** un analista la pasa a "verificada en campo" con el resultado "no confirmado" y un comentario, **entonces** el sistema acepta la transición y el detalle de la zona muestra el resultado y el comentario.
- **RF-11-AC-11** — **Dado que** una zona está en "requiere verificación", **cuando** un analista intenta pasarla a "verificada en campo" sin indicar el resultado, **entonces** el sistema rechaza la operación y la zona sigue en "requiere verificación".
- **RF-11-AC-12** — **Dado que** una zona está en "requiere verificación", **cuando** un analista la pasa a "en revisión" con el motivo "se canceló la salida a campo", **entonces** el sistema acepta la transición.
- **RF-11-AC-13** — **Dado que** una zona está en "verificada en campo", **cuando** un analista la pasa a "en revisión" con el motivo "el frente sigue creciendo", **entonces** el sistema acepta la transición.
- **RF-11-AC-14** — **Dado que** una zona está en "nueva", **cuando** se intenta pasarla a "revisada", **entonces** el sistema rechaza la transición por no estar en la tabla.
- **RF-11-AC-15** — **Dado que** una zona está en "descartada", **cuando** se intenta pasarla a "verificada en campo", **entonces** el sistema rechaza la transición por no estar en la tabla.
- **RF-11-AC-16** — **Dado que** una zona está en "descartada", **cuando** un analista la reabre a "en revisión" con un motivo, **entonces** el sistema acepta la transición.
- **RF-11-AC-17** — **Dado que** una zona está en "descartada", **cuando** un analista intenta reabrirla sin motivo, **entonces** el sistema rechaza la operación y la zona sigue en "descartada".
- **RF-11-AC-18** — **Dado que** una zona descartada tiene un puntaje ajustado de 30 (RF-34), **cuando** un analista la reabre manualmente a "en revisión" con un motivo, **entonces** la zona conserva el puntaje ajustado de 30.
- **RF-11-AC-19** — **Dado que** una zona está en "fusionada en EA-2026-010", **cuando** un analista intenta cambiar su estado, **entonces** el sistema rechaza la operación indicando que la zona se fusionó en EA-2026-010.
- **RF-11-AC-20** — **Dado que** una zona está en "en revisión", **cuando** la coordinación intenta cambiar su estado por la API, **entonces** la API responde 403 y el estado no cambia.
- **RF-11-AC-21** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en el detalle de una zona, **cuando** revisa las acciones disponibles, **entonces** no ve ninguna opción para cambiar el estado.
- **RF-11-AC-22** — **Dado que** existe una zona en cualquier estado, **cuando** un usuario de cualquier rol envía una solicitud de borrado de la zona a la API, **entonces** la API no expone la operación (404 o 405) y la zona sigue existiendo.
- **RF-11-AC-23** — *(Prueba E2E de interfaz.)* **Dado que** un usuario de cualquier rol está en el detalle de una zona, **cuando** revisa las acciones disponibles, **entonces** no hay ninguna opción para eliminar la zona.
- **RF-11-AC-24** — **Dado que** un analista cambió una zona de "en revisión" a "revisada", **cuando** cualquier usuario consulta el historial de la zona, **entonces** ve una entrada con estado anterior "en revisión", estado nuevo "revisada", el nombre del analista, la fecha y hora del cambio y el comentario.
- **RF-11-AC-25** — **Dado que** el sistema reabrió automáticamente una zona (RF-37), **cuando** se consulta su historial, **entonces** aparece una entrada con estado anterior "descartada" o "revisada", estado nuevo "nueva", el usuario "Sistema" y el motivo de la reapertura.

#### RF-12 — Lista priorizada de zonas

**Descripción:** El sistema debe mostrar la lista de zonas **ordenada por prioridad** por defecto: puntaje vigente descendente; en caso de empate, fecha de detección de la alerta más reciente (o fecha de creación, en zonas sin alertas) descendente; y, si persiste el empate, código ascendente. Cada fila muestra código, nivel y puntaje vigente (y el calculado si hay ajuste, RF-34), el texto del desglose (RF-33), las marcas (RF-36), el estado, los sectores y los indicadores "nueva desde tu última revisión" y "reabierta". La lista muestra el conteo por nivel y por estado, y se filtra por nivel, estado, sector y periodo (fecha de creación de la zona), con búsqueda por código. Las zonas fusionadas solo aparecen al filtrar por ese estado. Los **sectores** de una zona se asignan automáticamente: son todos los sectores activos que intersectan su geometría; si no intersecta ninguno, es "Fuera de sectores".
**Prioridad:** Must | **Fuente:** P2; Sección C, P1-seg, P3, P6-seg, P7 (C-2) | **Casos de uso:** UC-17

**Criterios de aceptación:**

- **RF-12-AC-1** — **Dado que** existen zonas con puntajes vigentes 40, 85 y 72, **cuando** un usuario abre la lista sin cambiar el orden, **entonces** las zonas aparecen en el orden 85, 72, 40.
- **RF-12-AC-2** — **Dado que** dos zonas tienen puntaje 60 y sus alertas más recientes tienen fecha de detección 25/09/2026 y 20/09/2026, **cuando** se muestra la lista, **entonces** la del 25/09/2026 aparece primero.
- **RF-12-AC-3** — **Dado que** dos zonas tienen puntaje 60, una con alerta más reciente del 20/09/2026 y otra manual sin alertas creada el 22/09/2026, **cuando** se muestra la lista, **entonces** la zona manual aparece primero.
- **RF-12-AC-4** — **Dado que** EA-2026-021 y EA-2026-017 tienen puntaje 60 y la misma fecha de referencia, **cuando** se muestra la lista, **entonces** EA-2026-017 aparece antes que EA-2026-021.
- **RF-12-AC-5** — **Dado que** una zona tiene puntaje calculado 45 y puntaje ajustado 80 (RF-34), **cuando** se muestra la lista, **entonces** la zona se ordena por 80 y la fila muestra "80 (ajustado; calculado 45)".
- **RF-12-AC-6** — **Dado que** una zona tiene nivel alto y la marca "nubosidad", **cuando** se consulta la lista, **entonces** su fila contiene el nivel "alta", el puntaje, el texto del desglose y la marca.
- **RF-12-AC-7** — **Dado que** existen 3 zonas de nivel alto, 5 de nivel medio y 8 de nivel bajo, de las cuales 4 están en "requiere verificación", **cuando** un usuario abre la lista sin filtros, **entonces** los conteos muestran 3, 5 y 8 por nivel, y 4 en "requiere verificación".
- **RF-12-AC-8** — **Dado que** existen zonas de varios niveles, estados, sectores y fechas, **cuando** el usuario filtra por nivel "alta", estado "requiere verificación", sector "Malinowski" y periodo 01/07/2026–30/09/2026, **entonces** solo aparecen las zonas que cumplen los cuatro criterios y los conteos reflejan solo esas zonas.
- **RF-12-AC-9** — **Dado que** ninguna zona cumple un filtro, **cuando** el usuario lo aplica, **entonces** la lista aparece vacía con un mensaje de sin resultados y todos los conteos muestran 0.
- **RF-12-AC-10** — **Dado que** la geometría de una zona intersecta los sectores "Malinowski" e "Interoceánica", **cuando** el usuario filtra por cualquiera de los dos, **entonces** la zona aparece en ambos resultados.
- **RF-12-AC-11** — **Dado que** existe la zona con código "EA-2026-014", **cuando** el usuario escribe "EA-2026-014" en la búsqueda, **entonces** la lista muestra solo esa zona.
- **RF-12-AC-12** — **Dado que** una zona no intersecta ningún sector, **cuando** el usuario filtra por "Fuera de sectores", **entonces** la zona aparece en el resultado.
- **RF-12-AC-13** — **Dado que** la zona EA-2026-015 está "fusionada en EA-2026-010", **cuando** un usuario abre la lista sin filtros, **entonces** EA-2026-015 no aparece; y al filtrar por el estado "fusionada" sí aparece.

#### RF-13 — Origen de la zona

**Descripción:** Cada zona debe indicar uno o más orígenes: alertas de GeoBosques, alertas RADD, detección propia o reporte de campo. Las zonas creadas por agrupación (RF-32) toman el origen de las fuentes de sus alertas y lo acumulan cuando se agregan alertas de otra fuente. El analista puede crear manualmente una zona dentro del ámbito, con origen "detección propia" (dibujando su polígono) o "reporte de campo" (a partir del punto de un reporte, RF-21); el sistema le asigna un código y calcula su prioridad (RF-33). Las zonas manuales reciben alertas según RF-32. El origen se puede usar como filtro y se muestra en la ficha.
**Prioridad:** Must | **Fuente:** P4, P7; Sección C, P1, P2, P7 | **Casos de uso:** UC-12

**Criterios de aceptación:**

- **RF-13-AC-1** — **Dado que** una zona agrupa alertas de GeoBosques y de RADD, **cuando** un usuario abre su detalle, **entonces** el origen muestra "alertas de GeoBosques" y "alertas RADD".
- **RF-13-AC-2** — **Dado que** un analista completa el formulario de una zona nueva manual, **cuando** intenta guardarla sin indicar el origen, **entonces** el sistema rechaza el guardado con un mensaje que pide el origen.
- **RF-13-AC-3** — **Dado que** con los pesos por defecto un analista dibuja hoy un polígono de 3.00 ha dentro de la RN Tambopata, a 1,250 m del río más cercano y sin alertas cercanas, **cuando** crea la zona con origen "detección propia", **entonces** el sistema la guarda con un código `EA-AAAA-NNN`, estado "nueva", puntaje 52 y nivel "media" (RF-33).
- **RF-13-AC-4** — **Dado que** se intenta crear una zona por la API con un origen fuera de los cuatro definidos (p. ej., "prensa"), **cuando** se envía la solicitud, **entonces** el sistema la rechaza y no crea la zona.
- **RF-13-AC-5** — **Dado que** existen zonas con distintos orígenes, **cuando** el usuario filtra la lista por "alertas RADD", **entonces** solo aparecen las zonas cuyo origen incluye RADD.
- **RF-13-AC-6** — **Dado que** una zona tiene origen "detección propia", **cuando** se genera su ficha PDF y se extrae su texto con pypdf, **entonces** contiene el origen "detección propia" en una sección separada de las alertas ingeridas (RD-05).
- **RF-13-AC-7** — **Dado que** una zona de origen "detección propia" se creó el 10/09/2026 y está activa, **cuando** se ingiere una alerta de GeoBosques a 300 m de su polígono con fecha de detección 20/09/2026, **entonces** la alerta se agrega a la zona y su origen muestra "detección propia" y "alertas de GeoBosques".
- **RF-13-AC-8** — **Dado que** un analista dibuja un polígono totalmente fuera del ámbito, **cuando** intenta crear una zona manual, **entonces** el sistema la rechaza indicando que está fuera del ámbito del sistema.
- **RF-13-AC-9** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta crear una zona por la API, **entonces** la API responde 403 y no se crea la zona.
- **RF-13-AC-10** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en el mapa o en la lista de zonas, **cuando** revisa las acciones disponibles, **entonces** no ve la opción de crear una zona.

#### RF-14 — Notas de discrepancia

**Descripción:** El analista debe poder registrar en la versión en curso de una zona una nota de discrepancia sobre el dato de una fuente oficial, con un campo de **referencia al documento de respaldo** (p. ej., número de resolución). Las notas son contenido versionado (RF-16). El sistema debe mostrar el dato oficial y la nota por separado, sin modificar el dato oficial. Adjuntar el documento queda fuera de la v1.
**Prioridad:** Should | **Fuente:** P4, P7 | **Casos de uso:** UC-13

**Criterios de aceptación:**

- **RF-14-AC-1** — **Dado que** una zona cruza un petitorio minero de INGEMMET, **cuando** un analista registra una nota de discrepancia sobre ese dato con la referencia "Resolución N.º 123-2026", **entonces** el dato oficial del petitorio permanece idéntico al original (todos sus atributos y su geometría).
- **RF-14-AC-2** — **Dado que** una zona tiene una nota de discrepancia con referencia documental, **cuando** se genera la ficha, **entonces** el dato oficial y la nota aparecen en secciones separadas, y la nota muestra su autor, su fecha y la referencia documental.
- **RF-14-AC-3** — **Dado que** una zona tiene una nota de discrepancia sin referencia documental, **cuando** se genera la ficha, **entonces** la nota aparece con el rótulo "Observación del equipo (sin documento de respaldo)" (RD-04).
- **RF-14-AC-4** — **Dado que** una zona tiene una nota de discrepancia, **cuando** un usuario consulta el detalle de la zona, **entonces** el dato oficial y la nota están en secciones separadas.
- **RF-14-AC-5** — **Dado que** un analista registra una nota de discrepancia por la API, **cuando** incluye un archivo adjunto, **entonces** el sistema rechaza el adjunto (fuera de la v1) y solo acepta el texto de referencia.
- **RF-14-AC-6** — **Dado que** la versión vigente de una zona está validada, **cuando** un analista intenta registrar en ella una nota de discrepancia, **entonces** el sistema la rechaza indicando que debe crear una versión nueva (RF-16).
- **RF-14-AC-7** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta registrar una nota de discrepancia por la API, **entonces** la API responde 403 y no se crea la nota.

#### RF-15 — Trazabilidad y reproducibilidad del análisis

**Descripción:** Cada versión de una zona tiene **un único análisis detallado**: una comparación de dos fechas con sus polígonos. Lanzar otra comparación en una versión **en curso** reemplaza la anterior, que queda en el historial de ejecuciones de la versión; en una versión que no está en curso, se rechaza. Reintentar (RF-29) y regenerar candidatos (RF-23) actúan sobre el mismo análisis. Para cada análisis, el sistema debe registrar, para poder reproducir la misma cifra: los identificadores y fechas de las imágenes; el sensor; los polígonos y su método de obtención (RF-23); los parámetros usados (umbral de visualización, índice, umbral de NDVI y área mínima); las versiones de las capas de referencia; el método de cálculo; y los **autores** de la versión: quienes ejecutaron el análisis o aceptaron, editaron o trazaron un polígono de cambio (descartar candidatos no hace autor). La **evaluación de humo** ("sin humo visible sobre el área de cambio" o "con humo") es un dato único de la versión, que solo se registra o cambia en una versión en curso; si es "con humo", la zona muestra la marca del analista "bruma o humo" (RF-36).
**Prioridad:** Must | **Fuente:** P1, P6, P7; Sección C, P4-seg | **Casos de uso:** UC-11

**Criterios de aceptación:**

- **RF-15-AC-1** — **Dado que** un analista guardó un análisis, **cuando** cualquier usuario lo consulta, **entonces** obtiene el identificador y la fecha de cada imagen, el sensor, los polígonos con su método de obtención, el índice, el umbral de NDVI, el área mínima, el umbral de visualización, la evaluación de humo, la versión (fecha de corte) de cada capa de referencia, el método de cálculo y los autores.
- **RF-15-AC-2** — **Dado que** el analista A guardó un análisis y después se cargaron nuevas versiones de capas y hay imágenes más recientes del área, **cuando** el analista B lo reabre en otra sesión, **entonces** el sistema recupera las mismas imágenes (por su identificador en GEE), los mismos polígonos y las mismas versiones de capas, y muestra la misma área en hectáreas y las mismas superposiciones que al guardarse.
- **RF-15-AC-3** — **Dado que** un análisis se guardó con la versión del 01/07/2026 del catastro minero y después se cargó la del 15/09/2026, **cuando** un usuario reabre el análisis, **entonces** las superposiciones siguen calculadas con la versión del 01/07/2026 y se indica esa fecha de corte.
- **RF-15-AC-4** — **Dado que** una imagen registrada en un análisis ya no está disponible en GEE, **cuando** un usuario reabre el análisis, **entonces** el sistema indica explícitamente que esa imagen (con su identificador) no está disponible y no la sustituye por otra.
- **RF-15-AC-5** — **Dado que** el analista A ejecutó el análisis de una versión y el analista B editó uno de sus candidatos, **cuando** se consulta la versión, **entonces** ambos figuran como autores.
- **RF-15-AC-6** — **Dado que** el analista A ejecutó el análisis de una versión y el analista B solo descartó candidatos, **cuando** se consulta la versión, **entonces** solo A figura como autor.
- **RF-15-AC-7** — **Dado que** la versión 2 en curso tiene un análisis con las fechas 15/08/2025 y 15/08/2026, **cuando** un analista lanza en ella otra comparación con las fechas 20/07/2025 y 20/07/2026, **entonces** la versión 2 tiene un único análisis, el de julio, y el de agosto queda en su historial de ejecuciones.
- **RF-15-AC-8** — **Dado que** el análisis de la versión 2 en curso está "fallido" (RF-29), **cuando** un analista lo reintenta y la ejecución termina, **entonces** la versión 2 sigue teniendo un único análisis, con los mismos parámetros y el resultado de la nueva ejecución.
- **RF-15-AC-9** — **Dado que** la versión 2 en curso tiene un análisis con candidatos, **cuando** un analista regenera los candidatos con otro umbral (RF-23), **entonces** la versión 2 sigue teniendo un único análisis, con los parámetros nuevos registrados.
- **RF-15-AC-10** — **Dado que** la versión vigente de una zona está validada, **cuando** un analista intenta lanzar una comparación en ella, **entonces** el sistema la rechaza indicando que debe crear una versión nueva.
- **RF-15-AC-11** — **Dado que** un analista registra la evaluación de humo "con humo" en una versión en curso, **cuando** se guarda, **entonces** la zona muestra la marca del analista "bruma o humo", con su nombre y la fecha (RF-36).
- **RF-15-AC-12** — **Dado que** la versión vigente de una zona está validada con la evaluación "sin humo visible", **cuando** un analista intenta cambiar su evaluación de humo, **entonces** el sistema lo rechaza indicando que solo se modifica en una versión en curso.

#### RF-16 — Versiones de la zona y revisión de la ficha antes de compartir

**Descripción:** La zona tiene dos partes:

- **Zona viva** (siempre actualizable por el sistema o los analistas): geometría, alertas, origen,
  área, prioridad y ajuste manual, marcas automáticas y de hipótesis, estado, comentarios de
  estado y comparticiones.
- **Contenido versionado** (pertenece a una versión): análisis detallado, polígonos de cambio,
  notas de discrepancia, evaluación de humo y ficha.

El contenido versionado sigue este ciclo de vida:

| Estado de la versión | Acción | Estado siguiente | Quién | Condiciones |
|---|---|---|---|---|
| — | Crear la zona | En curso (versión 1) | Sistema o analista SIG | — |
| Validada, compartida por urgencia o devuelta | Crear versión nueva | En curso (versión n+1), copia del contenido de la anterior | Analista SIG | Motivo obligatorio; no hay otra versión en curso ni pendiente de revisión |
| En curso | Enviar a revisión | Pendiente de revisión | Autor de la versión (RF-15) | Análisis detallado terminado |
| Pendiente de revisión | Validar | Validada | Analista SIG no autor (**validación técnica**) o coordinación (**revisión de contenido, no técnica**) | Comprobaciones de validez |
| Pendiente de revisión | Devolver | Devuelta | Analista SIG no autor o coordinación | Observaciones obligatorias |
| En curso | Compartir por urgencia | Compartida por urgencia | Autor de la versión | Motivo obligatorio y comprobaciones de validez |

Solo una versión **en curso** admite cambios de contenido. Las versiones pendientes de revisión no
se editan, y las **validadas, compartidas por urgencia y devueltas son inmutables**; para
continuar tras una devolución, o para modificar una versión validada o compartida, el analista
crea una versión nueva. La única excepción es la supresión de datos personales (RF-30).

**Comprobaciones de validez** (al validar y al compartir por urgencia): (a) la versión tiene al
menos un polígono de cambio (si no hay cambio real, la zona debe descartarse, RF-11); (b) ninguna
de las dos imágenes supera el **umbral de validez S-01** dentro del área de análisis, sea cual sea
el umbral de visualización del análisis; (c) la evaluación de humo está registrada y es "sin humo
visible sobre el área de cambio" (RD-07).

Al validar o compartir por urgencia se genera y almacena la ficha definitiva con su huella SHA-256
(RF-17). En la ruta de urgencia, la ficha indica "Compartida sin segunda revisión: [motivo]". Las
comparticiones previas siguen vinculadas a su versión, y una versión nueva debe revisarse antes de
compartirse.
**Prioridad:** Must | **Fuente:** Sección C, P7 (C-10) | **Casos de uso:** UC-15, UC-16, UC-34

**Criterios de aceptación:**

- **RF-16-AC-1** — **Dado que** el analista A es autor de la versión 1 en curso con un análisis terminado, **cuando** A la envía a revisión, **entonces** la versión pasa a "pendiente de revisión".
- **RF-16-AC-2** — **Dado que** el analista B no es autor de la versión 1 en curso, **cuando** B intenta enviarla a revisión, **entonces** el sistema lo rechaza indicando que solo el autor la envía.
- **RF-16-AC-3** — **Dado que** la versión 1 en curso no tiene un análisis terminado, **cuando** su autor intenta enviarla a revisión, **entonces** el sistema lo rechaza indicando que falta el análisis detallado.
- **RF-16-AC-4** — **Dado que** la versión 1, cuyo autor es el analista A, está pendiente de revisión y cumple las comprobaciones de validez, **cuando** el analista B la valida, **entonces** la versión pasa a "validada" con la leyenda "validación técnica por B", la fecha y hora, y la ficha definitiva queda almacenada con su huella en la bitácora.
- **RF-16-AC-5** — **Dado que** la versión 1 está pendiente de revisión y cumple las comprobaciones de validez, **cuando** la coordinación la valida, **entonces** la versión pasa a "validada" con la leyenda "revisión de contenido (no técnica) por [nombre de la coordinación]".
- **RF-16-AC-6** — **Dado que** el analista A es autor de la versión 1 pendiente de revisión, **cuando** A intenta validarla, **entonces** el sistema rechaza la validación y la versión sigue pendiente.
- **RF-16-AC-7** — **Dado que** la versión 1 tiene como autores a los analistas A y B, **cuando** B intenta validarla, **entonces** el sistema rechaza la validación e indica que puede revisarla la coordinación o compartirse por la ruta de urgencia.
- **RF-16-AC-8** — **Dado que** en la versión 1 pendiente de revisión una imagen tiene 35 % de nubosidad en el área (S-01 = 20 %), **cuando** un revisor no autor intenta validarla, **entonces** el sistema rechaza la validación indicando la imagen que supera el umbral de validez.
- **RF-16-AC-9** — **Dado que** el umbral de visualización del análisis es 40 % y una imagen tiene 35 % de nubosidad en el área, **cuando** un revisor no autor intenta validar la versión, **entonces** el sistema rechaza la validación, porque se aplica S-01 = 20 %.
- **RF-16-AC-10** — **Dado que** en la versión 1 en curso una imagen tiene 35 % de nubosidad en el área, **cuando** su autor intenta compartirla por urgencia con un motivo, **entonces** el sistema rechaza la operación indicando la imagen que supera el umbral de validez.
- **RF-16-AC-11** — **Dado que** la versión 1 pendiente de revisión no tiene registrada la evaluación de humo, **cuando** un revisor no autor intenta validarla, **entonces** el sistema rechaza la validación indicando que falta la evaluación de humo.
- **RF-16-AC-12** — **Dado que** la versión 1 pendiente de revisión tiene la evaluación de humo "con humo", **cuando** un revisor no autor intenta validarla, **entonces** el sistema rechaza la validación indicando el humo.
- **RF-16-AC-13** — **Dado que** la versión 1 en curso tiene la evaluación de humo "con humo", **cuando** su autor intenta compartirla por urgencia con un motivo, **entonces** el sistema rechaza la operación indicando el humo.
- **RF-16-AC-14** — **Dado que** la versión 1 pendiente de revisión no tiene ningún polígono de cambio, **cuando** un revisor no autor intenta validarla, **entonces** el sistema rechaza la validación indicando que no hay polígonos de cambio y que, si no hay cambio real, la zona debe descartarse.
- **RF-16-AC-15** — **Dado que** la versión 1 está pendiente de revisión, **cuando** la coordinación la devuelve con la observación "falta verificar la fecha de la imagen anterior", **entonces** la versión pasa a "devuelta" y la bitácora registra la devolución con la observación.
- **RF-16-AC-16** — **Dado que** la versión 1 está pendiente de revisión, **cuando** un revisor intenta devolverla sin observaciones, **entonces** el sistema rechaza la devolución y la versión sigue pendiente.
- **RF-16-AC-17** — **Dado que** la versión 1 está "devuelta", **cuando** un analista intenta editar uno de sus polígonos, **entonces** el sistema rechaza el cambio indicando que la versión es inmutable.
- **RF-16-AC-18** — **Dado que** la versión 1 está "devuelta" con dos polígonos, una nota y la evaluación "sin humo visible", **cuando** un analista crea una versión nueva con el motivo "corregir fecha de la imagen anterior", **entonces** existe la versión 2 en curso con los mismos polígonos, nota y evaluación, y la versión 1 sigue "devuelta".
- **RF-16-AC-19** — **Dado que** la versión 1 está validada, **cuando** un analista intenta crear una versión nueva sin motivo, **entonces** el sistema lo rechaza y no crea la versión.
- **RF-16-AC-20** — **Dado que** la versión 2 de una zona está en curso, **cuando** un analista intenta crear la versión 3, **entonces** el sistema lo rechaza indicando que ya hay una versión en curso.
- **RF-16-AC-21** — **Dado que** el analista A es autor de la versión 1 en curso, que cumple las comprobaciones de validez, **cuando** A la comparte por la ruta de urgencia con el motivo "la jefatura la solicita para el sobrevuelo del 30/09/2026", **entonces** la versión pasa a "compartida por urgencia" y la bitácora registra el motivo y la huella de la ficha definitiva.
- **RF-16-AC-22** — **Dado que** el analista A es autor de la versión 1 en curso, **cuando** intenta compartirla por la ruta de urgencia sin motivo, **entonces** el sistema rechaza la operación y la versión sigue en curso.
- **RF-16-AC-23** — **Dado que** el analista B no es autor de la versión 1 en curso, **cuando** intenta compartirla por la ruta de urgencia, **entonces** el sistema la rechaza indicando que solo el autor usa esa ruta.
- **RF-16-AC-24** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta usar la ruta de urgencia por la API, **entonces** la API responde 403 y la versión no cambia.
- **RF-16-AC-25** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta crear una versión nueva por la API, **entonces** la API responde 403 y no se crea la versión.
- **RF-16-AC-26** — **Dado que** la versión 1 de una zona está validada y tiene una compartición registrada, **cuando** un analista crea la versión 2 con un motivo, **entonces** la versión 1 sigue consultable con su contenido y su validación sin cambios, y la compartición sigue vinculada a la versión 1.
- **RF-16-AC-27** — **Dado que** la versión 1 de una zona con origen "alertas de GeoBosques" está validada, **cuando** se ingiere una alerta RADD que se agrega a la zona, **entonces** el origen de la zona pasa a incluir "alertas RADD" y su puntaje se recalcula.
- **RF-16-AC-28** — **Dado que** la versión 1 de una zona está validada, **cuando** se ingiere una alerta RADD que se agrega a la zona, **entonces** el contenido de la versión 1 no cambia y "Verificar ficha" sigue respondiendo "coincide" para su ficha definitiva.
- **RF-16-AC-29** — **Dado que** la versión vigente de una zona está validada y la zona está en "en revisión", **cuando** un analista la pasa a "requiere verificación" con un comentario, **entonces** el sistema acepta el cambio de estado sin crear una versión nueva.

#### RF-17 — Ficha de zona en PDF

**Descripción:** El sistema debe generar la ficha de una versión de zona en PDF, titulada "Ficha de zona", para la jefatura de la RN Tambopata, con:

- **Ubicación:** sectores y cuenca; distritos y provincias que intersectan los polígonos de cambio, según la capa de límites (RF-03), empezando por el que contiene el centroide del polígono de mayor área; y las coordenadas del centroide de cada polígono en UTM WGS84 zona 19S (EPSG:32719) y en geográficas (EPSG:4326).
- **Mapas:** antes y después, con barra de escala, fecha y flecha de norte visibles.
- **Área:** área de la zona y área de cambio en hectáreas, con el método de obtención de cada polígono (RF-23).
- **Prioridad:** nivel y puntaje con el desglose por factor (puntos y texto), la versión de pesos y la versión de parámetros de cálculo (RF-33); si hay ajuste manual, el puntaje calculado, el ajustado y su comentario (RF-34).
- **Marcas de confianza** y marcas del analista (RF-36).
- **Estado** de la zona y **comentario del analista** (el último del historial de estados).
- **Superposiciones** sin titulares y **distancias** al río y a la vía más cercanos (RF-10), y las discrepancias registradas (RF-14).
- **Historial del lugar** (RF-32).
- **Fuente y fecha de cada dato:** cada alerta con su fuente y fecha de detección; cada imagen con su fecha y **producto satelital** (p. ej., "Copernicus Sentinel-2 L2A", con su identificador), no la plataforma de procesamiento (RD-16), con la advertencia "resolución de 30 m; complementaria" si es Landsat (RD-07); cada capa con su fecha de corte y la fecha en que se cargó.
- **Nota metodológica:** índice, umbrales y decisión humana sobre los polígonos, con la leyenda obligatoria "Documento técnico de apoyo. No es una alerta oficial ni determina causas; requiere verificación en campo."
- **Responsables:** autores con nombre, profesión y cargo; y "Validación técnica por [analista]", "Revisión de contenido (no técnica) por [coordinación]" o "Compartida sin segunda revisión: [motivo]", con la fecha.

La **ficha definitiva** se genera **una sola vez**, al validar o compartir por urgencia (RF-16), con el contenido de la versión y los datos de la zona viva **a esa fecha**; se almacena sin cambios, se calcula su huella SHA-256 y toda descarga devuelve ese mismo archivo. Las versiones no validadas ni compartidas solo tienen **ficha borrador**, generada a pedido con los datos actuales y la marca de agua "BORRADOR". Generar cualquier ficha requiere un análisis detallado terminado. La ficha que se descarga por defecto desde el detalle de una zona es la definitiva de la **última versión validada o compartida por urgencia**; si no hay ninguna, la ficha borrador de la versión vigente. "Verificar ficha" permite a un usuario autenticado comprobar un archivo.
**Prioridad:** Must | **Fuente:** P3, P7; Sección C, P3, P4-seg, P7 (C-11) | **Casos de uso:** UC-19, UC-25

**Criterios de aceptación:**

- **RF-17-AC-1** — **Dado que** una versión de zona está validada, **cuando** se descarga su ficha definitiva y se extrae su texto con pypdf, **entonces** el título es "Ficha de zona" y contiene las secciones ubicación, mapas, área, prioridad, marcas, estado y comentario, superposiciones y distancias, historial del lugar, fuentes y fechas, nota metodológica y responsables.
- **RF-17-AC-2** — **Dado que** una versión está validada, **cuando** se descarga su ficha definitiva y se extrae su texto con pypdf, **entonces** la sección de ubicación contiene los sectores, la cuenca, el distrito, la provincia y las coordenadas en EPSG:32719 y en EPSG:4326.
- **RF-17-AC-3** — *(Prueba de aceptación manual.)* **Dado que** se descargó la ficha definitiva de una versión, **cuando** se revisan visualmente los mapas de antes y después, **entonces** cada mapa muestra una barra de escala, la fecha de la imagen y una flecha de norte.
- **RF-17-AC-4** — **Dado que** la versión usa una imagen Sentinel-2 L2A, **cuando** se descarga su ficha definitiva y se extrae su texto, **entonces** la imagen se cita con su fecha, el producto "Copernicus Sentinel-2 L2A" y su identificador, y "Google Earth Engine" no aparece como fuente de ninguna imagen (RD-16).
- **RF-17-AC-5** — **Dado que** la versión tiene un polígono "candidato aceptado" y otro "trazado por el analista", **cuando** se descarga su ficha definitiva, **entonces** la sección de área contiene el área de la zona y el área en hectáreas de cada polígono junto con su método de obtención.
- **RF-17-AC-6** — **Dado que** al validarse la versión la zona tenía puntaje 75 (nivel alta) con pesos v2 y parámetros v1, **cuando** se descarga la ficha definitiva, **entonces** contiene "alta — 75", los 7 factores con sus puntos y su texto, "pesos v2" y "parámetros v1".
- **RF-17-AC-7** — **Dado que** al validarse la versión la zona tenía puntaje calculado 45 y ajustado 80 con el comentario "frente activo junto al límite", **cuando** se descarga la ficha definitiva, **entonces** contiene ambos puntajes y el comentario del ajuste.
- **RF-17-AC-8** — **Dado que** al validarse la versión la zona tenía las marcas "desfase de fechas" y "posible dinámica fluvial", **cuando** se descarga la ficha definitiva, **entonces** ambas marcas aparecen en la sección de marcas de confianza.
- **RF-17-AC-9** — **Dado que** la zona cruza una concesión minera cuyo archivo de origen tenía el nombre del titular, **cuando** se descarga la ficha y se busca ese nombre en su texto extraído con pypdf, **entonces** el nombre no aparece.
- **RF-17-AC-10** — **Dado que** la zona cruza una concesión minera, **cuando** se descarga la ficha, **entonces** la concesión figura con tipo de derecho, código y estado.
- **RF-17-AC-11** — **Dado que** el análisis de la versión informa el río más cercano a 212 m y la vía más cercana a 1,530 m, **cuando** se descarga la ficha, **entonces** contiene ambas distancias.
- **RF-17-AC-12** — **Dado que** hay dos alertas de 2024 a 300 m de la zona que no forman parte de ella, **cuando** se descarga la ficha, **entonces** la sección de historial del lugar las lista con su fuente y su fecha de detección.
- **RF-17-AC-13** — **Dado que** la versión usa la versión del 15/09/2026 del catastro minero, cargada el 18/09/2026, **cuando** se descarga la ficha, **entonces** la capa aparece con la fecha de corte 15/09/2026 y la fecha de carga 18/09/2026.
- **RF-17-AC-14** — **Dado que** la zona agrupa alertas de GeoBosques y RADD, **cuando** se descarga la ficha, **entonces** cada alerta aparece con su fuente y su fecha de detección.
- **RF-17-AC-15** — **Dado que** se descarga la ficha de una versión, **cuando** se extrae el texto de la nota metodológica, **entonces** menciona el índice (NDVI), el umbral de NDVI, el área mínima y la decisión humana sobre los polígonos, e incluye literalmente "Documento técnico de apoyo. No es una alerta oficial ni determina causas; requiere verificación en campo."
- **RF-17-AC-16** — **Dado que** el analista B validó técnicamente una versión del analista A, **cuando** se descarga la ficha definitiva, **entonces** la sección de responsables contiene al autor A con nombre, profesión y cargo, y "Validación técnica por B" con su nombre, profesión, cargo y fecha.
- **RF-17-AC-17** — **Dado que** la coordinación validó una versión, **cuando** se descarga la ficha definitiva, **entonces** la sección de responsables contiene "Revisión de contenido (no técnica) por" seguido del nombre de la coordinación y la fecha, y no contiene "Validación técnica".
- **RF-17-AC-18** — **Dado que** una versión se compartió por la ruta de urgencia, **cuando** se descarga la ficha definitiva, **entonces** la sección de responsables contiene el autor y "Compartida sin segunda revisión: [motivo]", y el PDF no tiene marca de agua.
- **RF-17-AC-19** — **Dado que** una versión no está validada ni compartida por urgencia, **cuando** un usuario genera su ficha, **entonces** cada página del PDF contiene la marca de agua "BORRADOR".
- **RF-17-AC-20** — **Dado que** existe la ficha definitiva de una versión, **cuando** se extrae el texto del PDF, **entonces** contiene un código de verificación con el código de la zona, la versión y la fecha de validación o compartición, y no contiene la huella SHA-256.
- **RF-17-AC-21** — **Dado que** una versión validada estaba en "en revisión" al validarse y después la zona pasó a "requiere verificación", **cuando** se descarga la ficha definitiva, **entonces** el archivo es idéntico byte a byte al almacenado al validar y su estado dice "en revisión".
- **RF-17-AC-22** — **Dado que** un usuario autenticado tiene la ficha definitiva sin alterar, **cuando** la sube en "Verificar ficha", **entonces** el sistema responde "coincide" e indica la zona y la versión.
- **RF-17-AC-23** — **Dado que** un usuario autenticado tiene una copia de la ficha definitiva con un solo byte modificado, **cuando** la sube en "Verificar ficha", **entonces** el sistema responde "no coincide".
- **RF-17-AC-24** — **Dado que** no hay una sesión iniciada, **cuando** se invoca el servicio "Verificar ficha" de la API, **entonces** el sistema responde 401 y no verifica el archivo.
- **RF-17-AC-25** — **Dado que** un usuario autenticado está en el detalle de una zona, **cuando** descarga la ficha, **entonces** recibe un archivo con extensión .pdf y tipo de contenido application/pdf que pypdf lee sin errores.
- **RF-17-AC-26** — **Dado que** el polígono de mayor área de una versión está en el distrito Inambari y otro polígono en el distrito Tambopata, **cuando** se descarga la ficha, **entonces** la ubicación lista primero Inambari y luego Tambopata, ambos de la provincia Tambopata.
- **RF-17-AC-27** — **Dado que** una de las imágenes de la versión es Landsat 9, **cuando** se descarga la ficha, **entonces** junto a esa imagen aparece la advertencia "resolución de 30 m; complementaria".
- **RF-17-AC-28** — **Dado que** una zona tiene la versión 1 validada y la versión 2 en curso, **cuando** un usuario descarga la ficha desde el detalle de la zona sin elegir versión, **entonces** recibe la ficha definitiva de la versión 1.
- **RF-17-AC-29** — **Dado que** la versión vigente de una zona no tiene un análisis detallado terminado, **cuando** un usuario intenta generar su ficha, **entonces** el sistema no la genera e indica que se requiere un análisis detallado (RF-07).

#### RF-18 — Exportación del polígono de la zona

**Descripción:** El sistema debe exportar los polígonos de cambio de una versión de zona en GeoJSON y en Shapefile, en EPSG:32719, con los atributos código de la zona, versión, método de obtención y área (ha), sin titulares.
**Prioridad:** Should | **Fuente:** P3, P7; Sección C, P7 (C-12) | **Casos de uso:** UC-20

**Criterios de aceptación:**

- **RF-18-AC-1** — **Dado que** una versión tiene polígonos de cambio, **cuando** un analista la exporta en GeoJSON, **entonces** `ogrinfo` lee el archivo sin errores y reporta el sistema de coordenadas EPSG:32719.
- **RF-18-AC-2** — **Dado que** una versión tiene polígonos de cambio, **cuando** un analista la exporta en Shapefile, **entonces** recibe un .zip con los archivos .shp, .shx, .dbf y .prj, y `ogrinfo` lo lee sin errores con el sistema EPSG:32719.
- **RF-18-AC-3** — **Dado que** la versión registra un área de cambio de 3.50 ha, **cuando** se lee el polígono exportado en cada formato con GDAL y shapely y se calcula su área, **entonces** el resultado redondeado a dos decimales es 3.50 ha.
- **RF-18-AC-4** — **Dado que** no hay una sesión iniciada, **cuando** se solicita la exportación o el archivo exportado de un polígono, **entonces** el sistema responde 401 y no entrega el archivo (RNF-01).
- **RF-18-AC-5** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** solicita la exportación del polígono de una zona por la API, **entonces** la API responde 403 y no entrega el archivo.

#### RF-19 — Exportación de la lista de zonas

**Descripción:** El sistema debe exportar a CSV (UTF-8 con BOM) y XLSX la lista de zonas filtrada, en el orden de la lista (RF-12), con 10 columnas: código, nivel, puntaje calculado, puntaje ajustado (vacío si no hay), estado, sectores (separados por ";"), fecha de creación, fecha del último cambio de estado, área de la zona (ha) y área de cambio (ha). Si el filtro no devuelve zonas, se genera igualmente el archivo con solo los encabezados y se muestra un aviso.
**Prioridad:** Should | **Fuente:** P3, P6; Sección C, P7 | **Casos de uso:** UC-18

**Criterios de aceptación:**

- **RF-19-AC-1** — **Dado que** la lista de zonas muestra 5 zonas con un filtro aplicado, **cuando** el analista la exporta a CSV, **entonces** el archivo contiene exactamente esas 5 zonas, en el mismo orden, y ninguna otra.
- **RF-19-AC-2** — **Dado que** la lista de zonas muestra 5 zonas con un filtro aplicado, **cuando** el analista la exporta a XLSX y el archivo se lee con openpyxl, **entonces** la hoja contiene exactamente esas 5 zonas, en el mismo orden.
- **RF-19-AC-3** — **Dado que** se exporta la lista de zonas a CSV o XLSX, **cuando** se leen los encabezados, **entonces** son exactamente 10 columnas en español: código, nivel, puntaje calculado, puntaje ajustado, estado, sectores, fecha de creación, fecha del último cambio de estado, área de la zona (ha) y área de cambio (ha).
- **RF-19-AC-4** — **Dado que** una zona tiene el sector "Río Malinowski" y el estado "en revisión", **cuando** se exporta la lista a CSV, **entonces** el archivo empieza con los bytes EF BB BF y, decodificado como UTF-8, contiene literalmente "Río Malinowski" y "en revisión".
- **RF-19-AC-5** — **Dado que** el filtro aplicado no devuelve zonas, **cuando** el analista exporta la lista a CSV, **entonces** se genera el archivo con solo la fila de encabezados y el sistema muestra el aviso "La exportación no contiene zonas".
- **RF-19-AC-6** — **Dado que** una zona no tiene ajuste manual, **cuando** se exporta la lista, **entonces** su columna "puntaje ajustado" está vacía y "puntaje calculado" tiene su valor.
- **RF-19-AC-7** — **Dado que** una zona intersecta los sectores "Malinowski" e "Interoceánica", **cuando** se exporta la lista a CSV, **entonces** su columna "sectores" contiene "Malinowski;Interoceánica".
- **RF-19-AC-8** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** solicita la exportación de la lista por la API, **entonces** la API responde 403 y no entrega el archivo.

#### RF-20 — Registro de exportaciones

**Descripción:** El sistema debe registrar en la bitácora cada exportación y descarga (fichas, polígonos, listas, capas para campo, expedientes y bitácora) con el elemento exportado, el formato, el usuario y la fecha y hora; en las exportaciones de varias zonas, también el filtro usado, el número de zonas y los códigos de las zonas incluidas. Las comparticiones (RF-38) también quedan registradas.
**Prioridad:** Must | **Fuente:** P3, P7; Sección C, P7 | **Casos de uso:** UC-21

**Criterios de aceptación:**

- **RF-20-AC-1** — **Dado que** un usuario autenticado está en el detalle de una zona, **cuando** descarga la ficha PDF, **entonces** la bitácora contiene un registro con la zona, la versión, el formato "PDF", el usuario y la fecha y hora.
- **RF-20-AC-2** — **Dado que** un analista está en el detalle de una zona, **cuando** exporta su polígono en GeoJSON y luego en Shapefile, **entonces** la bitácora contiene dos registros, uno con formato "GeoJSON" y otro con formato "Shapefile", cada uno con la zona, el usuario y la fecha y hora.
- **RF-20-AC-3** — **Dado que** un analista tiene la lista de zonas filtrada, **cuando** la exporta a CSV, **entonces** la bitácora contiene un registro con el elemento "lista de zonas", el formato "CSV", el filtro, el número de zonas, el usuario y la fecha y hora.
- **RF-20-AC-4** — **Dado que** un analista exporta a GeoPackage las 6 zonas en "requiere verificación" (RF-40), **cuando** se consulta la bitácora, **entonces** hay un registro con el formato "GeoPackage", el filtro "estado = requiere verificación", el número de zonas 6, sus códigos, el usuario y la fecha y hora.
- **RF-20-AC-5** — **Dado que** existe un registro de exportación en la bitácora, **cuando** un usuario de cualquier rol envía a la API una solicitud de edición o borrado de ese registro, **entonces** la API no expone la operación (404 o 405) y el registro permanece sin cambios.
- **RF-20-AC-6** — **Dado que** existe un registro de exportación en la bitácora, **cuando** se ejecuta un UPDATE o DELETE sobre la tabla de bitácora con el usuario de base de datos de la aplicación, **entonces** la base de datos rechaza la sentencia por falta de permisos (RNF-04).

#### RF-21 — Registro manual de reportes de campo

**Descripción:** Un analista debe poder registrar manualmente un reporte de campo con ubicación **puntual** (en grados decimales EPSG:4326, por defecto, o en UTM 19S EPSG:32719; las que lleguen en grados, minutos y segundos las convierte el analista) dentro del ámbito, fecha de la observación (no posterior a hoy), descripción y hasta 10 fotos (JPG o PNG, máximo 10 MB cada una). El informante es **opcional** y, si se registra, se registra solo con un **código seudónimo** con el formato `[A-Z]{2,4}-\d+` (p. ej., MON-07 o GP-12), nunca con su nombre. La correspondencia código–nombre la custodia la coordinación fuera del sistema (RD-09, RD-11). El formulario muestra la advertencia literal "No suba capturas de chats ni escriba datos que identifiquen al informante (nombre, DNI, teléfono o dirección)." El reporte puede vincularse a una zona existente o crear una zona con origen "reporte de campo" (RF-13).
**Prioridad:** Should | **Fuente:** P6, P7; Sección C, P2, P7 | **Casos de uso:** UC-14

**Criterios de aceptación:**

- **RF-21-AC-1** — **Dado que** un analista recibió un reporte de un guardaparque, **cuando** lo registra con coordenadas, fecha de observación, descripción y una foto JPG de 3 MB, **entonces** el sistema lo guarda y el reporte aparece en la capa de reportes de campo en las coordenadas indicadas.
- **RF-21-AC-2** — **Dado que** un analista registra un reporte, **cuando** adjunta 10 fotos JPG o PNG de 10 MB o menos cada una, **entonces** el sistema acepta el registro con las 10 fotos.
- **RF-21-AC-3** — **Dado que** un analista registra un reporte, **cuando** intenta adjuntar 11 fotos, **entonces** el sistema rechaza el registro con un mensaje que indica el máximo de 10 fotos.
- **RF-21-AC-4** — **Dado que** un analista completa el formulario de un reporte, **cuando** lo envía sin coordenadas, **entonces** el sistema rechaza el registro con un mensaje que indica que faltan las coordenadas.
- **RF-21-AC-5** — **Dado que** un analista completa el formulario de un reporte, **cuando** lo envía sin fecha de observación, **entonces** el sistema rechaza el registro con un mensaje que indica que falta la fecha de observación.
- **RF-21-AC-6** — **Dado que** hoy es 27/09/2026, **cuando** un analista registra un reporte con fecha de observación 28/09/2026, **entonces** el sistema rechaza la fecha indicando que no puede ser futura.
- **RF-21-AC-7** — **Dado que** un analista registra un reporte, **cuando** adjunta una foto JPG de 10.5 MB, **entonces** el sistema rechaza la foto con un mensaje que indica el tamaño máximo de 10 MB.
- **RF-21-AC-8** — **Dado que** un analista registra un reporte, **cuando** adjunta una foto en formato HEIC, **entonces** el sistema rechaza la foto con un mensaje que indica los formatos JPG y PNG.
- **RF-21-AC-9** — **Dado que** existe un reporte de campo registrado, **cuando** un analista lo convierte en zona, **entonces** se crea una zona con origen "reporte de campo" (RF-13), cuya geometría es el punto del reporte y que está vinculada al reporte.
- **RF-21-AC-10** — **Dado que** existe un reporte de campo registrado, **cuando** un analista lo vincula a la zona EA-2026-014, **entonces** el reporte aparece en el detalle de esa zona.
- **RF-21-AC-11** — **Dado que** un analista registra un reporte, **cuando** ingresa el informante "MON-07" o "GP-12", **entonces** el sistema acepta el valor.
- **RF-21-AC-12** — **Dado que** un analista registra un reporte, **cuando** deja vacío el campo de informante, **entonces** el sistema acepta el registro.
- **RF-21-AC-13** — **Dado que** un analista registra un reporte, **cuando** ingresa en el campo de informante "Juan Pérez", "MON-" o "M-7", **entonces** el sistema rechaza el valor con un mensaje que indica el formato de 2 a 4 letras mayúsculas, guion y dígitos.
- **RF-21-AC-14** — **Dado que** un reporte con informante "MON-07" se vinculó a una zona, **cuando** se generan la ficha y las exportaciones de la zona, **entonces** el informante aparece solo como "MON-07" y no hay ningún campo con su nombre.
- **RF-21-AC-15** — **Dado que** un analista tiene una foto con metadatos EXIF de GPS, modelo del dispositivo y autor, **cuando** la carga en un reporte y luego se descarga desde el sistema, **entonces** exiftool no encuentra ningún metadato EXIF en la foto descargada.
- **RF-21-AC-16** — **Dado que** una foto tiene coordenadas GPS en EXIF distintas de las ingresadas por el analista, **cuando** se registra el reporte, **entonces** la ubicación del reporte es la ingresada por el analista.
- **RF-21-AC-17** — *(Prueba E2E de interfaz.)* **Dado que** un analista abre el formulario de reporte de campo, **cuando** el formulario se muestra, **entonces** contiene literalmente la advertencia "No suba capturas de chats ni escriba datos que identifiquen al informante (nombre, DNI, teléfono o dirección)."
- **RF-21-AC-18** — **Dado que** un analista registra un reporte, **cuando** ingresa las coordenadas "-12.8421, -69.4745" en grados decimales, dentro del ámbito, **entonces** el reporte se ubica en ese punto y se almacena también en EPSG:32719.
- **RF-21-AC-19** — **Dado que** un analista registra un reporte, **cuando** ingresa una latitud de 95, **entonces** el sistema rechaza las coordenadas indicando que están fuera de rango.
- **RF-21-AC-20** — **Dado que** un analista registra un reporte, **cuando** ingresa un punto fuera de la RN Tambopata y de su zona de amortiguamiento, **entonces** el sistema rechaza las coordenadas indicando que están fuera del ámbito.
- **RF-21-AC-21** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta registrar un reporte de campo por la API, **entonces** la API responde 403 y no se crea el reporte.
- **RF-21-AC-22** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en el mapa, **cuando** revisa las acciones disponibles, **entonces** no ve la opción de registrar un reporte de campo.

#### RF-22 — Gestión de usuarios, perfiles, roles y sectores

**Descripción:** La coordinación debe poder crear y desactivar cuentas de usuario, asignarles uno de los dos roles (analista SIG o coordinación), **editar sus perfiles** y definir los **sectores** de trabajo (nombre, polígono y cuenca, todos obligatorios). Cada perfil tiene **nombre completo, profesión y cargo**, que no pueden quedar vacíos ni al crear ni al editar, y que la ficha usa (RF-17). Los sectores no se eliminan: se **desactivan**, conservan su asignación a las zonas existentes y dejan de asignarse a zonas nuevas (RF-12). Las cuentas no se eliminan, solo se desactivan, para conservar la autoría en el historial y la bitácora.
**Prioridad:** Must | **Fuente:** implícito; Sección C, P2, P2-seg | **Casos de uso:** UC-02

**Criterios de aceptación:**

- **RF-22-AC-1** — **Dado que** la coordinación está en la gestión de usuarios, **cuando** crea una cuenta con rol analista SIG, **entonces** la cuenta queda activa con ese rol y el usuario puede iniciar sesión con contraseña y TOTP (RF-28).
- **RF-22-AC-2** — **Dado que** existe una cuenta de analista SIG, **cuando** ese usuario invoca el servicio de gestión de usuarios de la API, **entonces** la API responde 403.
- **RF-22-AC-3** — *(Prueba E2E de interfaz.)* **Dado que** un analista SIG inició sesión, **cuando** revisa el menú principal, **entonces** no ve la opción de gestión de usuarios ni la de sectores.
- **RF-22-AC-4** — **Dado que** la coordinación está en la gestión de usuarios, **cuando** crea otra cuenta con rol coordinación, **entonces** la cuenta queda activa con ese rol.
- **RF-22-AC-5** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación inició sesión, **cuando** revisa el detalle de una zona y la configuración, **entonces** no ve las opciones de cambiar estados, cargar capas ni editar pesos.
- **RF-22-AC-6** — **Dado que** la coordinación crea una cuenta, **cuando** intenta asignarle un rol distinto de analista SIG o coordinación (p. ej., "técnico"), **entonces** el sistema rechaza la creación indicando los roles válidos.
- **RF-22-AC-7** — **Dado que** la coordinación crea una cuenta, **cuando** deja vacía la profesión, **entonces** el sistema rechaza la creación indicando el campo obligatorio.
- **RF-22-AC-8** — **Dado que** existe el perfil de un analista, **cuando** la coordinación cambia su cargo a "Analista SIG senior", **entonces** el perfil queda con el cargo nuevo.
- **RF-22-AC-9** — **Dado que** existe el perfil de un analista, **cuando** la coordinación intenta dejar vacío su cargo, **entonces** el sistema rechaza la edición y el perfil conserva el cargo anterior.
- **RF-22-AC-10** — **Dado que** una cuenta de analista está activa, **cuando** la coordinación la desactiva y ese usuario intenta iniciar sesión con credenciales correctas, **entonces** el inicio de sesión se rechaza.
- **RF-22-AC-11** — **Dado que** un analista con zonas y registros de bitácora fue desactivado, **cuando** un usuario consulta esas zonas y la bitácora (RF-27), **entonces** el nombre del analista sigue apareciendo como autor.
- **RF-22-AC-12** — **Dado que** existe una cuenta, **cuando** la coordinación envía una solicitud de borrado de la cuenta a la API, **entonces** la API no expone la operación (404 o 405) y la cuenta sigue existiendo.
- **RF-22-AC-13** — **Dado que** la coordinación está en la configuración de sectores, **cuando** crea el sector "Malinowski" con cuenca "Malinowski" cargando un polígono en GeoJSON, **entonces** el sector queda guardado con su cuenca y aparece en la capa de sectores.
- **RF-22-AC-14** — **Dado que** la coordinación crea un sector, **cuando** deja vacía la cuenca, **entonces** el sistema rechaza la creación indicando el campo obligatorio.
- **RF-22-AC-15** — **Dado que** existe el sector "Interoceánica", **cuando** la coordinación edita su polígono y guarda, **entonces** el sector queda con la geometría nueva.
- **RF-22-AC-16** — **Dado que** existe el sector "Interoceánica" con 3 zonas asignadas, **cuando** la coordinación lo desactiva, **entonces** el sector deja de asignarse a zonas nuevas, y las 3 zonas lo conservan con la etiqueta "(inactivo)".
- **RF-22-AC-17** — **Dado que** un analista está autenticado, **cuando** intenta crear, editar o desactivar un sector por la API, **entonces** la API responde 403 y los sectores no cambian.

#### RF-23 — Propuesta semiautomática de polígonos de cambio

**Descripción:** Al comparar dos fechas (RF-07), el sistema debe calcular la diferencia de NDVI
entre ambas imágenes dentro del área de análisis y proponer como **polígonos candidatos** los
conjuntos de píxeles contiguos (**vecindad de 8**) donde el NDVI cae al menos lo indicado por el
umbral (−0.20 por defecto, S-10), con un área mínima de 0.5 ha (S-09) y excluyendo los píxeles
con nubes. El analista debe poder aceptar, editar o descartar cada candidato, y trazar polígonos
adicionales. Solo los polígonos aceptados, editados o trazados son polígonos de cambio. Solo se
generan candidatos si las dos imágenes son de la misma familia de sensores (Sentinel-2 con
Sentinel-2, o Landsat con Landsat). Al regenerar candidatos con otros parámetros, solo se
reemplazan los que están sin decidir. Los candidatos **no llevan ninguna etiqueta de causa**
(RD-17). (Se agregó en la v1.1, por eso su ID no sigue el orden temático; se relaciona con RF-07 a
RF-10.)
**Prioridad:** Must | **Fuente:** P1 ("que el sistema me ayude a descartar rápido"), sesión de alineación; Sección C, P4-seg | **Casos de uso:** UC-22

**Criterios de aceptación:**

- **RF-23-AC-1** — **Dado que** se usa un ráster sintético de ΔNDVI sin nubes con un bloque de 2 ha con ΔNDVI = −0.40 y el resto con ΔNDVI = 0, **cuando** se generan los candidatos con los valores por defecto, **entonces** el sistema propone un candidato que cubre al menos el 90 % del bloque.
- **RF-23-AC-2** — **Dado que** el umbral de NDVI está en su valor inicial de −0.20 (S-10), **cuando** se generan los candidatos sobre un ráster sintético, **entonces** una zona contigua de 1 ha con ΔNDVI = −0.25 se propone como candidato y una de 1 ha con ΔNDVI = −0.15 no.
- **RF-23-AC-3** — **Dado que** el área mínima está en su valor por defecto de 0.5 ha (S-09), **cuando** se generan los candidatos sobre un área con una caída de ΔNDVI = −0.40 que abarca 0.3 ha, **entonces** esa zona no se propone y ningún candidato mide menos de 0.50 ha.
- **RF-23-AC-4** — **Dado que** en un ráster sintético dos bloques de 0.3 ha con ΔNDVI = −0.40 se tocan solo por la esquina de un píxel, **cuando** se generan los candidatos, **entonces** forman un único candidato de 0.6 ha (vecindad de 8).
- **RF-23-AC-5** — **Dado que** una zona con ΔNDVI ≤ −0.20 está marcada como nube en la máscara de al menos una de las dos imágenes, **cuando** se generan los candidatos, **entonces** ningún candidato incluye píxeles de esa zona.
- **RF-23-AC-6** — **Dado que** se generaron candidatos con los valores por defecto, **cuando** el analista cambia el umbral a −0.30 y el área mínima a 1 ha y vuelve a generarlos, **entonces** los nuevos candidatos cumplen ΔNDVI ≤ −0.30 y un área de 1.00 ha o más, y el análisis registra los nuevos parámetros.
- **RF-23-AC-7** — **Dado que** el sistema propuso un candidato, **cuando** el analista lo acepta sin cambios, **entonces** se convierte en polígono de cambio con el método "candidato aceptado".
- **RF-23-AC-8** — **Dado que** el sistema propuso un candidato, **cuando** el analista mueve al menos un vértice y lo guarda, **entonces** se convierte en polígono de cambio con el método "candidato editado".
- **RF-23-AC-9** — **Dado que** hay una comparación de dos fechas en pantalla, **cuando** el analista traza un polígono propio y lo guarda, **entonces** se registra como polígono de cambio con el método "trazado por el analista".
- **RF-23-AC-10** — **Dado que** una versión tiene polígonos con los tres métodos de obtención, **cuando** un usuario consulta el detalle del análisis filtrando por "candidato editado", **entonces** solo obtiene los polígonos con ese método, cada uno con su método indicado.
- **RF-23-AC-11** — **Dado que** una versión tiene un candidato descartado y otro sin decidir, **cuando** se calcula el área de cambio y se genera la ficha, **entonces** ninguno de los dos cuenta para el área ni aparece en la ficha.
- **RF-23-AC-12** — *(Prueba de aceptación manual — calibración, semanas 4–6.)* **Dado que** hay un conjunto de 10–15 zonas ya verificadas en campo por los analistas, **cuando** se ejecuta la detección con los umbrales de −0.10 a −0.40 en pasos de 0.05, **entonces** se adopta el umbral que cumple S-10 (al menos el 90 % de los claros cubierto en al menos un 50 % de su área, con no más de 5 candidatos falsos por cada 1,000 ha) con la mayor cobertura; y si ninguno cumple, se adopta el de mayor cobertura y el desvío se registra en los temas abiertos.
- **RF-23-AC-13** — **Dado que** hay candidatos propuestos en una versión, **cuando** la coordinación intenta aceptar, editar o descartar un candidato por la API, **entonces** la API responde 403 y el candidato no cambia.
- **RF-23-AC-14** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación consulta un análisis con candidatos, **cuando** revisa las acciones disponibles, **entonces** no ve las opciones de aceptar, editar o descartar candidatos.
- **RF-23-AC-15** — **Dado que** un analista aceptó 2 candidatos y dejó 3 sin decidir, **cuando** regenera los candidatos con otro umbral, **entonces** los 2 aceptados se conservan y solo se reemplazan los 3 sin decidir.
- **RF-23-AC-16** — **Dado que** la comparación usa una imagen Sentinel-2 y otra Landsat 9, **cuando** termina el análisis, **entonces** no se generan candidatos, el sistema indica que se requieren imágenes de la misma familia de sensores, y el analista puede trazar polígonos propios.
- **RF-23-AC-17** — **Dado que** se generaron candidatos, **cuando** se consultan en la API, **entonces** cada candidato tiene solo ΔNDVI, área, geometría y estado de decisión, y ningún atributo o etiqueta de causa (p. ej., "minería").

#### RF-24 — (Retirado en v3.0)

**Motivo:** la presentación ante autoridades queda fuera de la v1; la reemplaza el registro de compartición (RF-38).

#### RF-25 — Descarga del expediente de la zona

**Descripción:** Un analista debe poder descargar el expediente de una versión de una zona (por
defecto, la última validada o compartida por urgencia; si no hay, la vigente) como un único archivo
ZIP que incluye:

- la ficha definitiva o, si la versión no está validada ni compartida por urgencia, la ficha
  borrador con marca de agua "BORRADOR"
- los polígonos de cambio (GeoJSON y Shapefile)
- las imágenes de antes y después en PNG
- un manifiesto con la versión y la huella SHA-256 de cada archivo

El objetivo es llevar el material de una zona a campo o trabajar con él sin conexión (Sección C,
P5; C-12).
**Prioridad:** Should | **Fuente:** Sección C, P5 (C-12) | **Casos de uso:** UC-26

**Criterios de aceptación:**

- **RF-25-AC-1** — **Dado que** una versión de zona está validada, **cuando** un analista descarga su expediente, **entonces** recibe un único archivo ZIP con la ficha definitiva, los polígonos en GeoJSON y en Shapefile, las imágenes de antes y después en PNG y un manifiesto de huellas.
- **RF-25-AC-2** — **Dado que** se descargó el expediente de una versión validada, **cuando** se calcula la huella SHA-256 de cada archivo del ZIP con sha256sum, **entonces** todas coinciden con las del manifiesto y el manifiesto lista todos los archivos del ZIP.
- **RF-25-AC-3** — **Dado que** un analista está en el detalle de una zona, **cuando** descarga el expediente, **entonces** la bitácora contiene un registro con la zona, el formato "ZIP", el usuario y la fecha y hora (RF-20).
- **RF-25-AC-4** — **Dado que** una zona no tiene ninguna versión validada ni compartida por urgencia, **cuando** un analista descarga su expediente, **entonces** el ZIP contiene la ficha borrador con marca de agua "BORRADOR", los polígonos, las imágenes y el manifiesto, y no contiene ficha definitiva.
- **RF-25-AC-5** — **Dado que** no hay una sesión iniciada, **cuando** se solicita la descarga del expediente de una zona, **entonces** el sistema responde 401 y no entrega el archivo (RNF-01).
- **RF-25-AC-6** — **Dado que** una zona tiene la versión 1 validada y la versión 2 en curso, **cuando** un analista descarga el expediente sin elegir versión, **entonces** el ZIP corresponde a la versión 1 y su manifiesto indica "versión 1".
- **RF-25-AC-7** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** solicita el expediente de una zona por la API, **entonces** la API responde 403 y no entrega el archivo.

#### RF-26 — (Retirado en v3.0)

**Motivo:** el registro de presuntos responsables queda fuera del alcance de la v1 y es contrario a RD-17 y RD-18.

#### RF-27 — Consulta y exportación de la bitácora

**Descripción:** La coordinación y los analistas deben poder consultar la bitácora de auditoría
(RNF-04), filtrarla por zona, usuario, tipo de acción y rango de fechas, y exportar el resultado a
CSV. La exportación también queda registrada. Cada vez que un usuario **abre el detalle de una zona
o descarga una ficha**, se registra una entrada de consulta con el usuario, la zona y la fecha y
hora.
**Prioridad:** Must | **Fuente:** Sección C, P2-seg, P7; revisión técnica H-04 | **Casos de uso:** UC-28

**Criterios de aceptación:**

- **RF-27-AC-1** — **Dado que** un analista abrió el detalle de la zona EA-2026-014, **cuando** la coordinación filtra la bitácora por esa zona, **entonces** aparece una entrada de tipo "consulta" con el analista y la fecha y hora.
- **RF-27-AC-2** — **Dado que** la bitácora tiene entradas de varias zonas, **cuando** un analista filtra por la zona EA-2026-014 y el rango 01/09/2026–30/09/2026, **entonces** solo aparecen entradas de esa zona dentro de ese rango.
- **RF-27-AC-3** — **Dado que** la coordinación tiene un resultado filtrado, **cuando** lo exporta a CSV, **entonces** el archivo contiene exactamente esas entradas y la bitácora registra la exportación.
- **RF-27-AC-4** — **Dado que** un analista cambió los pesos de priorización (RF-35) y otro ajustó la prioridad de una zona (RF-34), **cuando** la coordinación filtra la bitácora por los tipos de acción "cambio de pesos" y "ajuste de prioridad", **entonces** aparecen ambas entradas con el usuario, la fecha y hora y el motivo o comentario.
- **RF-27-AC-5** — **Dado que** un usuario filtra la bitácora, **cuando** indica una fecha final anterior a la inicial, **entonces** el sistema rechaza el filtro con un mensaje y no ejecuta la consulta.
- **RF-27-AC-6** — **Dado que** no hay una sesión iniciada, **cuando** se solicita la bitácora o su exportación a la API, **entonces** el sistema responde 401 y no entrega ninguna entrada.

#### RF-28 — Autenticación y ciclo de vida de las credenciales

**Descripción:** El sistema debe gestionar:

- **Primer ingreso:** obliga a cambiar la contraseña temporal y a enrolar el segundo factor TOTP
  (RNF-03).
- **Intentos fallidos:** tras 5 intentos fallidos consecutivos, la cuenta se bloquea 15 minutos
  (S-13).
- **Contraseña olvidada o factor perdido:** la coordinación puede emitir una contraseña temporal
  y restablecer el segundo factor de otro usuario. Ambas acciones quedan en la bitácora.
- **Última cuenta de coordinación:** no se puede desactivar la única cuenta activa de
  coordinación.
- **Emergencia:** si la única coordinación pierde el acceso, se recupera con un procedimiento
  documentado en el manual de operación (RNF-12), que se ejecuta en el servidor.

**Prioridad:** Must | **Fuente:** RNF-03; revisión técnica H-08 | **Casos de uso:** UC-01, UC-02

**Criterios de aceptación:**

- **RF-28-AC-1** — **Dado que** la coordinación creó una cuenta con contraseña temporal, **cuando** el usuario inicia sesión por primera vez, **entonces** el sistema le exige definir una contraseña nueva y enrolar el TOTP antes de acceder a cualquier otra función.
- **RF-28-AC-2** — **Dado que** un usuario falló la contraseña 4 veces seguidas, **cuando** la falla por quinta vez, **entonces** la cuenta queda bloqueada 15 minutos, incluso con la contraseña correcta, y la bitácora registra el bloqueo.
- **RF-28-AC-3** — **Dado que** un analista perdió su celular, **cuando** la coordinación restablece su segundo factor, **entonces** en el siguiente ingreso el analista debe enrolar un TOTP nuevo, el anterior deja de ser válido y la bitácora registra el restablecimiento.
- **RF-28-AC-4** — **Dado que** hay una sola cuenta activa de coordinación, **cuando** alguien intenta desactivarla, **entonces** el sistema lo rechaza indicando que es la última cuenta de coordinación.
- **RF-28-AC-5** — *(Prueba de aceptación manual — inspección y demostración.)* **Dado que** existe el manual de operación, **cuando** un analista ejecuta en una demostración el procedimiento de recuperación de emergencia de la cuenta de coordinación que describe, **entonces** la coordinación recupera el acceso.

#### RF-29 — Estados y errores del análisis

**Descripción:** Cada ejecución del análisis de una versión debe tener un estado visible: **en
cola**, **en curso**, **terminado** o **fallido**. Al terminar o fallar, el sistema notifica dentro
de la aplicación al analista que la lanzó (RNF-05). Si GEE devuelve un error (cuota agotada, tiempo
de espera agotado o error de procesamiento), la ejecución pasa a "fallido", muestra el motivo en
español y ofrece **reintentar** con los mismos parámetros sobre el mismo análisis (RF-15).
**Prioridad:** Must | **Fuente:** RNF-05; revisión técnica H-22 | **Casos de uso:** UC-07

**Criterios de aceptación:**

- **RF-29-AC-1** — **Dado que** un analista lanzó un análisis que aún se procesa, **cuando** consulta su estado, **entonces** obtiene "en cola" o "en curso".
- **RF-29-AC-2** — **Dado que** un análisis terminó correctamente, **cuando** el analista consulta su estado, **entonces** obtiene "terminado".
- **RF-29-AC-3** — **Dado que** un analista lanzó un análisis, **cuando** el análisis termina, **entonces** el analista tiene una notificación nueva en la aplicación que lo indica.
- **RF-29-AC-4** — **Dado que** GEE responde con un error de cuota agotada (simulado en la prueba), **cuando** se procesa el análisis, **entonces** queda "fallido" con un mensaje en español que indica la cuota agotada.
- **RF-29-AC-5** — **Dado que** un análisis está "fallido", **cuando** el analista elige "reintentar", **entonces** se crea una ejecución nueva del mismo análisis con los mismos parámetros, que pasa a "en cola".
- **RF-29-AC-6** — **Dado que** un análisis está "fallido", **cuando** la coordinación intenta reintentarlo por la API, **entonces** la API responde 403 y no se crea ninguna ejecución.

#### RF-30 — Supresión de datos personales

**Descripción:** Para atender solicitudes de supresión según la Ley N.º 29733 (RD-09), la
coordinación debe poder **suprimir** una foto de un reporte de campo o un fragmento de texto libre
(descripción de un reporte, nota o comentario). El elemento se reemplaza por "[suprimido]" y la
bitácora registra quién lo suprimió, cuándo, el motivo y el **identificador** del elemento, pero no
su contenido. La supresión es una **excepción explícita al bloqueo** de las versiones (RF-16): si
el elemento pertenece a una versión inmutable, se registra en esa versión como "contenido
suprimido" sin crear una versión nueva. La ficha definitiva almacenada no se modifica (tema
abierto). Al **restaurar un respaldo**, el sistema reaplica todas las supresiones registradas en
la bitácora (RNF-10). El alcance sobre las exportaciones y fichas ya entregadas fuera del sistema
es un tema abierto.
**Prioridad:** Should | **Fuente:** RD-09; revisión técnica H-25; Sección C, P2-seg | **Casos de uso:** UC-29

**Criterios de aceptación:**

- **RF-30-AC-1** — **Dado que** un reporte de campo tiene 3 fotos, **cuando** la coordinación suprime una indicando un motivo, **entonces** el reporte muestra "[suprimido]" en su lugar y el archivo ya no se puede descargar.
- **RF-30-AC-2** — **Dado que** el comentario de una zona contiene un fragmento que identifica a una persona, **cuando** la coordinación suprime ese fragmento con un motivo, **entonces** el comentario muestra "[suprimido]" en su lugar y la entrada de la bitácora contiene el identificador del elemento pero no el texto suprimido.
- **RF-30-AC-3** — **Dado que** la versión 1 de una zona está validada y tiene una nota de discrepancia con un nombre de persona, **cuando** la coordinación suprime ese fragmento con un motivo, **entonces** la nota muestra "[suprimido]", la versión 1 queda con la indicación "contenido suprimido" y no se crea ninguna versión nueva.
- **RF-30-AC-4** — **Dado que** una versión de zona tiene una ficha definitiva registrada, **cuando** la coordinación suprime una foto de un reporte vinculado a la zona, **entonces** "Verificar ficha" sigue respondiendo "coincide" para esa ficha.
- **RF-30-AC-5** — **Dado que** se tomó un respaldo antes de suprimir una foto y la supresión quedó registrada, **cuando** se restaura ese respaldo, **entonces** la foto sigue suprimida después de la restauración.
- **RF-30-AC-6** — **Dado que** la coordinación seleccionó un elemento para suprimir, **cuando** confirma sin indicar un motivo, **entonces** el sistema rechaza la supresión y el elemento no cambia.
- **RF-30-AC-7** — **Dado que** un analista está autenticado, **cuando** intenta suprimir un dato por la API, **entonces** la API responde 403 y el dato no cambia.

#### RF-31 — Ingesta de alertas multifuente

**Descripción:** El sistema debe ingerir alertas (polígonos) de dos fuentes satelitales:

- **GeoBosques**, por carga de archivo con el formulario de RF-03. La carga es una **ingesta
  acumulativa**: no crea versiones de capa; agrega las alertas nuevas y conserva las existentes. La
  fecha de corte de cada carga es **solo informativa** (RF-02), y una carga con fecha de corte
  anterior también se ingiere. Las alertas ya ingeridas que no vienen en una carga nueva **no se
  borran**: se marcan "no presente en la última carga" y siguen en su zona.
- **RADD** (radar Sentinel-1), sincronizada desde GEE **una vez por semana** (los lunes a las
  06:00, hora de Lima) y **a pedido** del analista.

De cada alerta registra la fuente, el código de la fuente, la geometría, la **fecha de detección**
y la **fecha de ingesta**. No ingiere dos veces la misma alerta (misma fuente y código) y descarta
las alertas fuera del ámbito (RD-14), informando cuántas. Cada ingesta termina con la agrupación
en zonas (RF-32) y queda en la bitácora. Si la sincronización falla, se conservan las alertas
previas y el analista puede reintentar. La ingesta de alertas **GLAD** es **Could**: no forma
parte del alcance comprometido de la v1 ni de estos criterios.
**Prioridad:** Must | **Fuente:** Sección C, P1, P4, P5, P6-seg, P7 (C-1, C-17) | **Casos de uso:** UC-30, UC-03

**Criterios de aceptación:**

- **RF-31-AC-1** — **Dado que** un analista carga un archivo de GeoBosques con 120 alertas, 5 de ellas fuera del ámbito, **cuando** la carga termina, **entonces** el sistema ingiere 115 alertas, cada una con fuente "GeoBosques", código, fecha de detección y fecha de ingesta.
- **RF-31-AC-2** — **Dado que** un analista cargó un archivo de GeoBosques con 5 alertas fuera del ámbito, **cuando** la carga termina, **entonces** el resumen indica "5 alertas fuera del ámbito".
- **RF-31-AC-3** — **Dado que** un analista carga un archivo de alertas de GeoBosques cuyas geometrías son puntos, **cuando** envía la carga, **entonces** el sistema la rechaza indicando que las alertas deben ser polígonos.
- **RF-31-AC-4** — **Dado que** hay 200 alertas de GeoBosques ingeridas y un archivo nuevo trae 150 de ellas y 30 nuevas, **cuando** se carga, **entonces** el sistema tiene 230 alertas de GeoBosques y las 50 ausentes quedan marcadas "no presente en la última carga" sin salir de sus zonas.
- **RF-31-AC-5** — **Dado que** la última carga de GeoBosques tiene fecha de corte 20/09/2026, **cuando** un analista carga un archivo con fecha de corte 10/09/2026 que contiene 3 alertas no ingeridas, **entonces** el sistema ingiere esas 3 alertas y el panel de capas sigue mostrando "20/09/2026".
- **RF-31-AC-6** — **Dado que** es lunes a las 06:00 (hora de Lima) y hay alertas RADD nuevas en GEE desde la última sincronización, **cuando** se ejecuta la sincronización programada, **entonces** el sistema ingiere esas alertas con fuente "RADD" y la bitácora registra la sincronización con el número de alertas nuevas.
- **RF-31-AC-7** — **Dado que** un analista está en el panel de fuentes, **cuando** elige "Sincronizar RADD ahora", **entonces** el sistema ejecuta la sincronización y devuelve un resumen con el número de alertas nuevas, las fuera del ámbito y la fecha y hora.
- **RF-31-AC-8** — **Dado que** una alerta RADD con código "R-889120" ya fue ingerida, **cuando** una sincronización posterior la vuelve a recibir, **entonces** no se crea una alerta duplicada y el resumen la cuenta como ya existente.
- **RF-31-AC-9** — **Dado que** GEE responde con un error durante la sincronización (simulado en la prueba), **cuando** termina el proceso, **entonces** la sincronización queda "fallida" con un mensaje en español y las alertas previas siguen intactas.
- **RF-31-AC-10** — **Dado que** una sincronización RADD quedó "fallida", **cuando** el analista la reintenta y GEE responde bien, **entonces** la sincronización termina y la fecha de la última sincronización exitosa se actualiza (RF-02).
- **RF-31-AC-11** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta ejecutar "Sincronizar RADD ahora" por la API, **entonces** la API responde 403 y no se ejecuta la sincronización.
- **RF-31-AC-12** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en el panel de fuentes, **cuando** revisa las acciones disponibles, **entonces** no ve la opción "Sincronizar RADD ahora".
- **RF-31-AC-13** — **Dado que** una ingesta de GeoBosques o RADD terminó, **cuando** se consultan las alertas ingeridas, **entonces** cada una pertenece a una zona (RF-32).

#### RF-32 — Agrupación en zonas de cambio

**Descripción:** El sistema debe agrupar cada alerta ingerida con estas reglas, en este orden,
midiendo la **distancia mínima** entre la alerta y la **geometría de la zona** (alertas, polígono
o punto de creación) en EPSG:32719:

1. **Zonas activas:** la alerta es compatible con una zona activa si está a ≤ 500 m (S-14) y su
   fecha de detección difiere en ≤ 90 días (S-15) de la fecha de referencia de la zona (la fecha de
   detección de su alerta más reciente o, si no tiene alertas, su fecha de creación). Si es
   compatible con una sola zona, se agrega a ella. Si es compatible con dos o más, esas zonas se
   **fusionan** en la más antigua (menor fecha de creación): la alerta y las alertas de las demás
   pasan a la sobreviviente, y las demás quedan en el estado "fusionada en EA-…" con su historial,
   sus versiones y sus fichas conservados.
2. **Zonas cerradas:** si no es compatible con ninguna zona activa y está a ≤ 500 m de una zona
   cerrada (revisada o descartada) cuya fecha de referencia está dentro de los últimos 3 años
   (S-28), se agrega a la más cercana **aunque supere la ventana de 90 días**; si es una alerta
   posterior, dispara la reapertura (RF-37).
3. **Zona nueva:** si no, crea una zona nueva con código `EA-AAAA-NNN` (año de creación y número
   correlativo del año).

Las alertas que se superponen forman una **detección** (1.3); una detección con alertas de dos o
más fuentes satelitales **confirma** la zona, sin descartar ninguna alerta. Al agregarse una
alerta, la zona actualiza su geometría, su área, su número de detecciones, sus fuentes y su
prioridad (RF-33). Cada zona muestra su **historial del lugar**: alertas o zonas anteriores a
≤ 500 m en los últimos 3 años (S-28) que no forman parte de ella.
**Prioridad:** Must | **Fuente:** Sección C, P1-seg, P3, P7 (C-1, C-8) | **Casos de uso:** UC-31

**Criterios de aceptación:**

- **RF-32-AC-1** — **Dado que** existen dos alertas de GeoBosques a 300 m una de otra con fechas de detección separadas por 10 días, **cuando** se ejecuta la agrupación, **entonces** ambas quedan en la misma zona.
- **RF-32-AC-2** — **Dado que** existen dos alertas a 600 m una de otra con fechas de detección separadas por 10 días, **cuando** se ejecuta la agrupación, **entonces** quedan en zonas distintas.
- **RF-32-AC-3** — **Dado que** una zona activa tiene una alerta y llega otra a 400 m cuya fecha de detección difiere en 120 días, **cuando** se ejecuta la agrupación, **entonces** la alerta nueva crea otra zona.
- **RF-32-AC-4** — **Dado que** existen dos alertas exactamente a 500 m una de otra con fechas de detección separadas por exactamente 90 días, **cuando** se ejecuta la agrupación, **entonces** quedan en la misma zona.
- **RF-32-AC-5** — **Dado que** dos alertas poligonales tienen sus centroides a 900 m y sus bordes a 450 m, **cuando** se ejecuta la agrupación, **entonces** quedan en la misma zona (distancia mínima entre geometrías).
- **RF-32-AC-6** — **Dado que** una alerta RADD se superpone con una alerta de GeoBosques, **cuando** se ejecuta la agrupación, **entonces** ambas quedan en la misma zona como una detección confirmada por 2 fuentes y ninguna de las dos alertas se descarta.
- **RF-32-AC-7** — **Dado que** dos alertas de GeoBosques se superponen, **cuando** se ejecuta la agrupación, **entonces** la zona tiene 1 detección.
- **RF-32-AC-8** — **Dado que** la alerta A se superpone con B y B con C, pero A no se superpone con C, **cuando** se ejecuta la agrupación, **entonces** A, B y C forman una sola detección.
- **RF-32-AC-9** — **Dado que** una alerta RADD y una de GeoBosques están a 400 m sin superponerse, **cuando** se ejecuta la agrupación, **entonces** quedan en la misma zona con 2 detecciones y la zona no tiene confirmación multifuente.
- **RF-32-AC-10** — **Dado que** la zona activa EA-2026-014 tiene 3 detecciones, **cuando** se ingiere una alerta que no se superpone con ninguna, a 200 m de su geometría y dentro de la ventana, **entonces** la zona pasa a 4 detecciones y su área y su puntaje se recalculan.
- **RF-32-AC-11** — **Dado que** las zonas activas EA-2026-010 (creada el 01/07/2026) y EA-2026-015 (creada el 10/08/2026) son compatibles con una alerta nueva a 200 m y 300 m, **cuando** se ejecuta la agrupación, **entonces** la alerta y las alertas de EA-2026-015 pasan a EA-2026-010, y EA-2026-015 queda "fusionada en EA-2026-010" con su historial consultable.
- **RF-32-AC-12** — **Dado que** una zona de detección propia sin alertas se creó el 01/09/2026 y está activa, **cuando** se ingiere una alerta a 300 m de su polígono con fecha de detección 20/09/2026, **entonces** la alerta se agrega a esa zona.
- **RF-32-AC-13** — **Dado que** una zona de detección propia sin alertas se creó el 01/03/2026 y está activa, **cuando** se ingiere una alerta a 300 m de su polígono con fecha de detección 20/09/2026, **entonces** la alerta crea una zona nueva.
- **RF-32-AC-14** — **Dado que** una zona activa se creó a partir del punto de un reporte de campo, **cuando** se ingiere dentro de la ventana una alerta a 450 m de ese punto, **entonces** la alerta se agrega a esa zona.
- **RF-32-AC-15** — **Dado que** una zona fue descartada el 15/07/2024 y su alerta más reciente es del 01/07/2024, **cuando** se ingiere una alerta a 300 m con fecha de detección 20/09/2026, **entonces** la alerta se agrega a esa zona y la zona se reabre (RF-37).
- **RF-32-AC-16** — **Dado que** una zona descartada tiene como fecha de referencia el 01/06/2022 (más de 3 años), **cuando** se ingiere una alerta a 300 m con fecha de detección 20/09/2026, **entonces** la alerta crea una zona nueva y la zona descartada aparece en su historial del lugar.
- **RF-32-AC-17** — **Dado que** una alerta nueva es compatible con una zona activa a 300 m y está a 200 m de una zona descartada hace un año, **cuando** se ejecuta la agrupación, **entonces** la alerta se agrega a la zona activa.
- **RF-32-AC-18** — **Dado que** hay una alerta de hace 2 años a 350 m de una zona, otra de hace 4 años a 350 m y otra de hace 1 año a 700 m, ninguna dentro de la zona, **cuando** un usuario consulta el detalle de la zona, **entonces** el historial del lugar lista solo la alerta de hace 2 años, con su fuente y su fecha de detección.
- **RF-32-AC-19** — **Dado que** la última zona creada en 2026 es EA-2026-041, **cuando** se crea una zona nueva en 2026, **entonces** su código es EA-2026-042.
- **RF-32-AC-20** — **Dado que** una zona agrupa dos alertas que no se superponen, de 1.20 ha y 0.80 ha, **cuando** se calcula el área de la zona, **entonces** es "2.00 ha" (unión en EPSG:32719, dos decimales).

#### RF-33 — Priorización explicada

**Descripción:** El sistema debe calcular para cada zona no fusionada un **puntaje de 0 a 100**,
suma ponderada de 7 factores normalizados de 0 a 1, con los pesos de la versión vigente (RF-35) y
los parámetros de la versión de parámetros de cálculo vigente. Todas las fechas son **fechas de
detección** (no de ingesta), en la zona horaria America/Lima, y todas las distancias se miden como
distancia mínima desde la **geometría de la zona** (nunca desde los polígonos de cambio del
análisis). "Ventana k" (k = 1…8) es el k-ésimo intervalo de 7 días contado hacia atrás desde hoy
(la ventana 1 es hoy y los 6 días anteriores).

| Factor | Normalización (0 a 1) |
|---|---|
| Ubicación | 1 si alguna parte de la geometría está dentro de la RN Tambopata; si no, 0.6 si su distancia al límite de la reserva es ≤ 2 km (S-20); si no, 0.3. |
| Persistencia y crecimiento | 0.5 × (ventanas, de las 8 de S-24, con al menos una alerta ÷ 8) + 0.5 × min(crecimiento, 1). Crecimiento = (área actual − área hace 8 semanas) ÷ max(área hace 8 semanas, 1 ha); si es negativo, vale 0. El "área hace 8 semanas" es la de la geometría formada solo por las alertas con fecha de detección anterior a la ventana 8 y, en zonas manuales creadas antes de esa fecha, por el polígono o punto de creación. |
| Agrupación | Número de detecciones ÷ 10 (S-21), con tope 1. |
| Confirmación multifuente | 1 si la zona tiene confirmación multifuente (1.3); 0 si no. |
| Cercanía a ríos | 1 si la distancia al río más cercano es ≤ 500 m; (2,000 − d) ÷ 1,500 entre 500 m y 2 km; 0 desde 2 km (S-25). |
| Superficie | Área de la zona ÷ 10 ha (S-22), con tope 1. |
| Recencia | Con d = días desde la alerta más reciente (en zonas sin alertas, desde la fecha de creación): 1 si d ≤ 7; (90 − d) ÷ 83 si 7 < d < 90; 0 si d ≥ 90 (S-23). |

El **puntaje** es la suma **sin redondear** de los aportes (peso × factor), redondeada después al
entero más cercano (0.5 hacia arriba); el **nivel** se calcula con ese entero: alta (≥ 70), media
(40–69) o baja (< 40) (S-17). La lista, el detalle y la ficha **siempre** muestran el **desglose**
por factor, en puntos (un decimal, solo para mostrar) y con texto (p. ej., "dentro de la reserva;
3 alertas en 4 semanas; confirmada por GeoBosques y RADD; a 200 m del río Malinowski"). Cada
puntaje registra la **versión de pesos** y la **versión de parámetros de cálculo** usadas. El
puntaje se recalcula al cambiar la zona, al crear una versión de pesos y una vez al día. Ningún
factor ni texto del desglose asigna causas (RD-17).
**Prioridad:** Must | **Fuente:** Sección C, P1-seg, P3-seg, P7 (C-2, C-3) | **Casos de uso:** UC-17, UC-31

**Criterios de aceptación:**

- **RF-33-AC-1** — **Dado que** con los pesos por defecto (S-16) una zona está dentro de la reserva, tuvo alertas en 3 de las 8 ventanas, medía 2.00 ha hace 8 semanas y hoy 3.00 ha, tiene 3 detecciones y confirmación multifuente, está a 200 m del río y su alerta más reciente es de hace 3 días, **cuando** se calcula su prioridad, **entonces** el desglose es ubicación 30.0, persistencia y crecimiento 8.8, agrupación 4.5, confirmación multifuente 15.0, cercanía a ríos 10.0, superficie 1.5 y recencia 5.0, y el puntaje es 75, nivel "alta".
- **RF-33-AC-2** — **Dado que** hay tres zonas con los demás factores iguales, una con parte de su geometría dentro de la reserva, otra en la zona de amortiguamiento a 1.5 km del límite y otra a 3 km, **cuando** se calcula su prioridad, **entonces** el factor de ubicación vale 1, 0.6 y 0.3 respectivamente.
- **RF-33-AC-3** — **Dado que** hay zonas a 300 m, 500 m, 1,250 m y 2,000 m del río más cercano, **cuando** se calcula su prioridad, **entonces** el factor de cercanía a ríos vale 1, 1, 0.5 y 0 respectivamente.
- **RF-33-AC-4** — **Dado que** la geometría de una zona está a 400 m del río y los polígonos de cambio de su análisis están a 800 m, **cuando** se calcula su prioridad, **entonces** el factor de cercanía a ríos vale 1.
- **RF-33-AC-5** — **Dado que** hay zonas con puntajes enteros 70, 69, 40 y 39, **cuando** se asigna el nivel, **entonces** son "alta", "media", "media" y "baja" respectivamente.
- **RF-33-AC-6** — **Dado que** los aportes sin redondear de una zona suman 69.45, **cuando** se calcula su prioridad, **entonces** el puntaje es 69 y el nivel "media".
- **RF-33-AC-7** — **Dado que** los aportes sin redondear de una zona suman 69.5, **cuando** se calcula su prioridad, **entonces** el puntaje es 70 y el nivel "alta".
- **RF-33-AC-8** — **Dado que** una zona se creó hace 3 semanas, tuvo alertas en 3 ventanas, mide hoy 2.00 ha y no tenía alertas hace 8 semanas, **cuando** se calcula su prioridad con los pesos por defecto, **entonces** el aporte de persistencia y crecimiento es 13.8 puntos (0.5 × 3/8 + 0.5 × 1 = 0.6875).
- **RF-33-AC-9** — **Dado que** con los pesos por defecto una zona de detección propia sin alertas se creó hace 10 días con un polígono de 3.00 ha dentro de la reserva, a 1,250 m del río más cercano, **cuando** se calcula su prioridad, **entonces** el desglose es ubicación 30.0, persistencia y crecimiento 10.0, agrupación 0.0, confirmación multifuente 0.0, cercanía a ríos 5.0, superficie 1.5 y recencia 4.8, y el puntaje es 51, nivel "media".
- **RF-33-AC-10** — **Dado que** la alerta más reciente de una zona tiene fecha de detección de hace 7 días, **cuando** se calcula su prioridad, **entonces** el factor de recencia vale 1.
- **RF-33-AC-11** — **Dado que** la alerta más reciente de una zona tiene fecha de detección de hace 45 días, **cuando** se ejecuta el recálculo diario, **entonces** el aporte de recencia es 2.7 puntos con los pesos por defecto.
- **RF-33-AC-12** — **Dado que** la única alerta de una zona es RADD, con fecha de detección de hace 20 días e ingerida hoy, **cuando** se calcula su prioridad, **entonces** el factor de recencia vale (90 − 20) ÷ 83 y su aporte es 4.2 puntos con los pesos por defecto.
- **RF-33-AC-13** — **Dado que** una zona tiene puntaje 75, **cuando** se consulta en la lista, en el detalle y en su ficha, **entonces** en los tres lugares aparecen los 7 factores con sus puntos y el texto explicativo.
- **RF-33-AC-14** — **Dado que** una zona solo tiene alertas de GeoBosques, **cuando** se calcula su prioridad, **entonces** el factor de confirmación multifuente vale 0 y el texto indica "una sola fuente (GeoBosques)".
- **RF-33-AC-15** — **Dado que** están vigentes la versión de pesos 1 y la versión de parámetros 1, **cuando** se calcula el puntaje de una zona, **entonces** el puntaje registra "pesos v1" y "parámetros v1".
- **RF-33-AC-16** — **Dado que** el puntaje de una zona se calculó con la versión de pesos 1, **cuando** un analista crea la versión 2 (RF-35), **entonces** el puntaje se recalcula, registra "pesos v2" y el historial de la zona conserva el puntaje anterior con "pesos v1".
- **RF-33-AC-17** — **Dado que** se calcula la prioridad de cualquier zona, **cuando** se consulta el desglose en la API, **entonces** contiene exactamente los 7 factores de la tabla y ningún factor, etiqueta o texto de causa (p. ej., "minería").

#### RF-34 — Ajuste manual de prioridad

**Descripción:** El analista debe poder subir o bajar la prioridad de una zona fijando un **puntaje ajustado** de 0 a 100, con **comentario obligatorio**. El sistema conserva y muestra el puntaje calculado y el ajustado; el nivel y el orden de la lista usan el ajustado. El puntaje calculado se sigue actualizando. El analista puede quitar el ajuste con un comentario. La **reapertura automática** (RF-37) retira el ajuste, lo deja en el historial y lo indica; la **reapertura manual** (RF-11) lo conserva. Cada ajuste queda en el historial de la zona y en la bitácora.
**Prioridad:** Must | **Fuente:** Sección C, P3-seg, P7 (C-4) | **Casos de uso:** UC-32

**Criterios de aceptación:**

- **RF-34-AC-1** — **Dado que** una zona tiene puntaje calculado 45, **cuando** un analista fija un puntaje ajustado de 80 con el comentario "frente activo junto al límite", **entonces** la zona muestra "80 (ajustado; calculado 45)" y nivel "alta".
- **RF-34-AC-2** — **Dado que** un analista fijó un puntaje ajustado de 80 sobre un calculado de 45, **cuando** se consulta la bitácora, **entonces** hay una entrada con el usuario, la fecha y hora, ambos valores y el comentario.
- **RF-34-AC-3** — **Dado que** un analista está ajustando la prioridad de una zona, **cuando** confirma sin comentario, **entonces** el sistema rechaza el ajuste y el puntaje vigente no cambia.
- **RF-34-AC-4** — **Dado que** un analista está ajustando la prioridad de una zona, **cuando** ingresa 120, −5 o "alto", **entonces** el sistema rechaza el valor indicando el rango de 0 a 100.
- **RF-34-AC-5** — **Dado que** una zona tiene puntaje calculado 45 y ajustado 80, **cuando** llegan alertas nuevas y el puntaje calculado pasa a 52, **entonces** la zona muestra "80 (ajustado; calculado 52)".
- **RF-34-AC-6** — **Dado que** una zona tiene un ajuste manual, **cuando** un analista lo quita con un comentario, **entonces** el puntaje vigente vuelve a ser el calculado y el historial conserva el ajuste anterior y su retiro.
- **RF-34-AC-7** — **Dado que** una zona tuvo dos ajustes manuales, **cuando** un usuario consulta su detalle, **entonces** obtiene el historial de ajustes con el analista, la fecha y hora, los valores y el comentario de cada uno.
- **RF-34-AC-8** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta ajustar la prioridad de una zona por la API, **entonces** la API responde 403 y el puntaje no cambia.
- **RF-34-AC-9** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en el detalle de una zona, **cuando** revisa las acciones disponibles, **entonces** no ve la opción de ajustar la prioridad.

#### RF-35 — Configuración de pesos de priorización

**Descripción:** El sistema debe permitir a los analistas cambiar los 7 pesos de la priorización (RF-33), cuyos valores por defecto (versión de pesos 1) son los de S-16. Los pesos son enteros de 0 a 100 que **deben sumar 100**, y cada cambio exige un **motivo**. Cada cambio crea una **versión** numerada con historial (quién, cuándo, por qué) y recalcula los puntajes de las zonas con la versión nueva; las fichas definitivas conservan el puntaje y las versiones con que se emitieron. Todos los usuarios pueden consultar las versiones de pesos y la versión de parámetros de cálculo vigente (solo lectura). **El sistema nunca reajusta los pesos automáticamente.**
**Prioridad:** Must | **Fuente:** Sección C, P3-seg, P7 (C-5) | **Casos de uso:** UC-33

**Criterios de aceptación:**

- **RF-35-AC-1** — **Dado que** no se ha cambiado ningún peso, **cuando** un usuario consulta la configuración de pesos, **entonces** obtiene la versión 1 con ubicación 30, persistencia y crecimiento 20, agrupación 15, confirmación multifuente 15, cercanía a ríos 10, superficie 5 y recencia 5.
- **RF-35-AC-2** — **Dado que** la versión vigente es la 1, **cuando** un analista guarda los pesos 35, 15, 15, 15, 10, 5 y 5 con el motivo "calibración con verificaciones de agosto", **entonces** se crea la versión 2 con su usuario, fecha y hora y motivo, y los puntajes de las zonas se recalculan con ella.
- **RF-35-AC-3** — **Dado que** la versión vigente es la 1, **cuando** un analista intenta guardar pesos que suman 105, **entonces** el sistema rechaza el cambio indicando que deben sumar 100 y la versión 1 sigue vigente.
- **RF-35-AC-4** — **Dado que** un analista cambió pesos que suman 100, **cuando** intenta guardarlos sin motivo, **entonces** el sistema rechaza el cambio y no crea ninguna versión.
- **RF-35-AC-5** — **Dado que** un analista está editando los pesos, **cuando** ingresa un peso negativo o con decimales (p. ej., −5 o 12.5), **entonces** el sistema rechaza el valor indicando que deben ser enteros de 0 a 100.
- **RF-35-AC-6** — **Dado que** existen las versiones 1, 2 y 3, **cuando** un usuario consulta el historial de pesos, **entonces** obtiene las tres versiones con sus valores, su autor, su fecha y hora y su motivo.
- **RF-35-AC-7** — **Dado que** la ficha definitiva de la versión 1 de una zona se emitió con puntaje 75 y pesos v1, **cuando** un analista crea la versión de pesos 2, **entonces** esa ficha sigue conteniendo 75 y "pesos v1" y "Verificar ficha" sigue respondiendo "coincide".
- **RF-35-AC-8** — **Dado que** se registraron 20 resultados de verificación en campo (RF-11) y pasaron 30 días sin que ningún analista cambie los pesos, **cuando** se consulta la configuración, **entonces** la versión vigente sigue siendo la misma y no existe ninguna versión creada por el sistema.
- **RF-35-AC-9** — **Dado que** la versión de parámetros de cálculo vigente es la 1, **cuando** un usuario de cualquier rol intenta modificar un parámetro de cálculo (p. ej., S-21) por la API, **entonces** no existe ninguna operación para hacerlo (404 o 405) y la versión sigue siendo la 1.
- **RF-35-AC-10** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta guardar pesos por la API, **entonces** la API responde 403 y no se crea ninguna versión.
- **RF-35-AC-11** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación abre la configuración de pesos, **cuando** revisa la pantalla, **entonces** ve los pesos en modo de solo lectura, sin opción de edición.

#### RF-36 — Marcas de confianza

**Descripción:** El sistema debe asociar a cada zona las **marcas de confianza** que correspondan, sin **ocultarla** ni cambiar su puntaje. Las marcas se muestran en el mapa, la lista, el detalle y la ficha. **Marcas automáticas** (se recalculan sobre la zona viva y el análisis de la versión vigente cuando cambian los datos):

- **nubosidad:** alguna de las dos imágenes del análisis supera el **umbral de validez S-01** (no el
  umbral de visualización)
- **desfase de fechas:** más de 60 días (S-18) entre la fecha de detección de la alerta más
  reciente de la zona (o su fecha de creación, si no tiene alertas) y la fecha de la imagen
  posterior del análisis
- **polígono pequeño sin confirmación:** la zona mide menos de 1 ha (S-27) y no tiene confirmación
  multifuente (1.3)
- **posible dinámica fluvial:** la zona está a ≤ 100 m (S-26) de un cauce activo
- **posible ecosistema inundable:** la zona intersecta la capa de ecosistemas inundables o
  aguajales del MINAM

**Marcas del analista** (manuales, con nombre y fecha, visualmente distintas de las automáticas):
"bruma o humo", que es la representación de la evaluación de humo "con humo" de la versión
vigente (RF-15), y **hipótesis** en texto libre (p. ej., "posible actividad minera"), rotuladas
"Marca del analista". El analista puede **retirar** una marca del analista con motivo, y el retiro
queda en el historial; la marca "bruma o humo" se retira cambiando la evaluación de humo en una
versión en curso. El sistema nunca genera ni sugiere hipótesis (RD-17).
**Prioridad:** Must | **Fuente:** Sección C, P4-seg, P7 (C-6, C-9) | **Casos de uso:** UC-12, UC-17

**Criterios de aceptación:**

- **RF-36-AC-1** — **Dado que** S-01 es 20 % y una imagen del análisis tiene 25 % de nubosidad en el área, **cuando** se evalúan las marcas, **entonces** la zona tiene la marca "nubosidad 25 % > 20 %".
- **RF-36-AC-2** — **Dado que** S-01 es 20 % y la imagen más nubosa del análisis tiene exactamente 20 % en el área, **cuando** se evalúan las marcas, **entonces** la zona no tiene la marca de nubosidad.
- **RF-36-AC-3** — **Dado que** el umbral de visualización del análisis es 40 % y una imagen tiene 25 % de nubosidad en el área, **cuando** se evalúan las marcas, **entonces** la zona tiene la marca de nubosidad, porque se aplica S-01.
- **RF-36-AC-4** — **Dado que** la alerta más reciente de la zona tiene fecha de detección 01/08/2026 y la imagen posterior del análisis es del 15/10/2026 (75 días), **cuando** se evalúan las marcas, **entonces** la zona tiene la marca "desfase de fechas: 75 días".
- **RF-36-AC-5** — **Dado que** el análisis compara el 15/08/2025 con el 15/08/2026 (práctica de RD-08) y la alerta más reciente de la zona es del 01/08/2026, **cuando** se evalúan las marcas, **entonces** la zona no tiene la marca de desfase de fechas.
- **RF-36-AC-6** — **Dado que** la alerta más reciente de la zona es del 01/08/2026 y la imagen posterior del análisis es del 30/09/2026 (60 días), **cuando** se evalúan las marcas, **entonces** la zona no tiene la marca de desfase de fechas.
- **RF-36-AC-7** — **Dado que** una zona de 0.80 ha tiene alertas de una sola fuente, **cuando** se evalúan las marcas, **entonces** tiene la marca "polígono pequeño sin confirmación".
- **RF-36-AC-8** — **Dado que** una zona de 0.80 ha tiene una detección con alertas de GeoBosques y RADD, **cuando** se evalúan las marcas, **entonces** no tiene la marca "polígono pequeño sin confirmación".
- **RF-36-AC-9** — **Dado que** una zona de 0.80 ha tiene una alerta de GeoBosques y otra de RADD a 300 m que no se superponen, **cuando** se evalúan las marcas, **entonces** tiene la marca "polígono pequeño sin confirmación".
- **RF-36-AC-10** — **Dado que** una zona está a 80 m del río Tambopata, **cuando** se evalúan las marcas, **entonces** tiene la marca "posible dinámica fluvial".
- **RF-36-AC-11** — **Dado que** una zona está a 150 m del río más cercano, **cuando** se evalúan las marcas, **entonces** no tiene la marca "posible dinámica fluvial".
- **RF-36-AC-12** — **Dado que** una zona intersecta un polígono de la capa de ecosistemas inundables y aguajales, **cuando** se evalúan las marcas, **entonces** tiene la marca "posible ecosistema inundable".
- **RF-36-AC-13** — **Dado que** una zona de nivel alto con puntaje 75 tiene tres marcas automáticas, **cuando** un usuario consulta la lista con el filtro de nivel "alta", **entonces** la zona aparece con sus marcas y su puntaje sigue siendo 75.
- **RF-36-AC-14** — **Dado que** la versión vigente en curso tiene la evaluación de humo "con humo" registrada por el analista A, **cuando** se consultan las marcas de la zona en la API, **entonces** incluyen "bruma o humo" con tipo "marca del analista", el nombre de A y la fecha.
- **RF-36-AC-15** — *(Prueba de aceptación manual.)* **Dado que** una zona tiene una marca automática y una marca del analista, **cuando** un usuario revisa el detalle de la zona, **entonces** ambas marcas se distinguen visualmente y la del analista lleva el rótulo "Marca del analista".
- **RF-36-AC-16** — **Dado que** un analista registra la hipótesis "posible actividad minera" en una zona, **cuando** se consultan sus marcas, **entonces** la hipótesis aparece rotulada "Marca del analista", con el nombre del analista y la fecha.
- **RF-36-AC-17** — **Dado que** una zona tiene la hipótesis "posible actividad minera", **cuando** un analista la retira con el motivo "pozas descartadas en campo", **entonces** la hipótesis deja de estar activa y el historial conserva la hipótesis, el retiro y el motivo.
- **RF-36-AC-18** — **Dado que** una zona tiene una marca del analista, **cuando** un analista intenta retirarla sin motivo, **entonces** el sistema rechaza el retiro y la marca sigue activa.
- **RF-36-AC-19** — **Dado que** el sistema evalúa las marcas de cualquier zona, **cuando** se consultan sus marcas automáticas en la API, **entonces** solo pueden ser de los cinco tipos automáticos definidos y ninguna contiene una hipótesis o causa.
- **RF-36-AC-20** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta registrar o retirar una marca del analista por la API, **entonces** la API responde 403 y las marcas no cambian.

#### RF-37 — Reapertura automática

**Descripción:** Una zona cerrada ("descartada" o "revisada") debe volver automáticamente a "nueva", con el indicador **"reabierta"** y el motivo, si recibe una **alerta posterior** (fecha de detección posterior a su último cambio de estado) o si su área crece **≥ 20 %** (S-19) respecto del área que tenía en ese cambio de estado (p. ej., por alertas con fecha de detección anterior que llegan con rezago). La reapertura **retira el ajuste manual de prioridad**, que queda en el historial con la indicación "ajuste retirado por reapertura" (RF-34). El cambio queda en el historial (RF-11) y en la bitácora, y se muestra un indicador en la aplicación (RF-04); **no se envían correos** ni otros avisos externos. Las zonas activas se actualizan sin cambiar de estado.
**Prioridad:** Must | **Fuente:** Sección C, P1-seg, P7 (C-8) | **Casos de uso:** UC-12, UC-31

**Criterios de aceptación:**

- **RF-37-AC-1** — **Dado que** una zona se descartó el 01/09/2026, **cuando** recibe una alerta RADD con fecha de detección 20/09/2026, **entonces** pasa a "nueva" con el indicador "reabierta" y el motivo "1 alerta nueva (RADD, 20/09/2026)".
- **RF-37-AC-2** — **Dado que** una zona descartada fue reabierta automáticamente, **cuando** se consulta la bitácora, **entonces** hay una entrada de reapertura con la zona, el motivo y la fecha y hora.
- **RF-37-AC-3** — **Dado que** una zona de 10.00 ha se marcó "revisada" el 27/08/2026, **cuando** recibe alertas con fecha de detección anterior al 27/08/2026 que llevan su área a 11.90 ha, **entonces** la zona sigue en "revisada".
- **RF-37-AC-4** — **Dado que** una zona de 10.00 ha se marcó "revisada" el 27/08/2026, **cuando** recibe alertas con fecha de detección anterior al 27/08/2026 que llevan su área a 12.00 ha, **entonces** pasa a "nueva" con el indicador "reabierta" y el motivo "área creció 20 %".
- **RF-37-AC-5** — **Dado que** una zona está en "verificada en campo", **cuando** recibe una alerta posterior, **entonces** se actualizan su área y su puntaje y su estado sigue siendo "verificada en campo".
- **RF-37-AC-6** — **Dado que** una zona fue reabierta, **cuando** un usuario consulta la lista, **entonces** la zona tiene el indicador "reabierta" con su motivo.
- **RF-37-AC-7** — **Dado que** el sistema usa un servidor de correo simulado, **cuando** una zona se reabre automáticamente, **entonces** el servidor de correo simulado no recibe ningún mensaje.
- **RF-37-AC-8** — **Dado que** una zona descartada con el motivo "cambio de cauce estacional" fue reabierta, **cuando** un usuario consulta su detalle, **entonces** el historial conserva el descarte anterior con su motivo, su analista y su fecha.
- **RF-37-AC-9** — **Dado que** una zona descartada tiene puntaje calculado 35 y ajustado 20, **cuando** se reabre automáticamente, **entonces** su puntaje vigente es 35 y el historial conserva el ajuste con la indicación "ajuste retirado por reapertura".

#### RF-38 — Registro de compartición

**Descripción:** El analista debe poder registrar cada vez que una ficha o una exportación se comparte fuera del sistema, con:

- **destinatario:** jefatura de la RN Tambopata (SERNANP); guardaparques o equipo de campo; u
  **"otro (coordinado con la jefatura)"**, con descripción del destinatario y **referencia
  obligatoria de la coordinación con la jefatura** (p. ej., n.º de oficio o correo de la jefatura)
- **fecha** de la compartición (no posterior a hoy)
- **medio** (p. ej., correo electrónico, entrega en persona, memoria USB, mensajería)
- **qué** se compartió: la ficha definitiva de una versión, o una exportación registrada de
  polígonos (RF-18), de capas para campo (RF-40) o un expediente (RF-25)
- **referencia** opcional (p. ej., n.º de oficio)

Compartir una ficha exige que su versión esté **validada** o que el autor use en ese momento la
**ruta de urgencia** (RF-16). Compartir una exportación exige que **todas las zonas incluidas**
tengan una versión validada o compartida por urgencia; si no, se rechaza. El sistema **no envía
nada**: solo registra (RD-19). Cada compartición se muestra en el detalle de las zonas incluidas y
queda en la bitácora.
**Prioridad:** Must | **Fuente:** Sección C, P1, P6, P7 (C-11, C-15) | **Casos de uso:** UC-34

**Criterios de aceptación:**

- **RF-38-AC-1** — **Dado que** la versión 1 de la zona EA-2026-014 está validada, **cuando** un analista registra que compartió su ficha con la jefatura de la RN Tambopata (SERNANP) el 26/09/2026 por correo electrónico con la referencia "Oficio N.º 045-2026", **entonces** el sistema guarda la compartición vinculada a la versión 1, la muestra en el detalle de la zona y la bitácora la registra.
- **RF-38-AC-2** — **Dado que** una versión está validada, **cuando** un analista registra su compartición con los guardaparques sin referencia, **entonces** el sistema la acepta.
- **RF-38-AC-3** — **Dado que** un analista registra una compartición, **cuando** la envía sin destinatario, **entonces** el sistema la rechaza indicando que falta el destinatario.
- **RF-38-AC-4** — **Dado que** un analista registra una compartición, **cuando** la envía sin fecha, **entonces** el sistema la rechaza indicando que falta la fecha.
- **RF-38-AC-5** — **Dado que** un analista registra una compartición, **cuando** la envía sin medio, **entonces** el sistema la rechaza indicando que falta el medio.
- **RF-38-AC-6** — **Dado que** un analista elige el destinatario "otro (coordinado con la jefatura)" con una descripción, **cuando** envía la compartición sin referencia de la coordinación con la jefatura, **entonces** el sistema la rechaza indicando que falta esa referencia.
- **RF-38-AC-7** — **Dado que** un analista elige el destinatario "otro (coordinado con la jefatura)", **cuando** la envía con la descripción "Municipalidad de Laberinto" y la referencia "correo de la jefatura del 20/09/2026", **entonces** el sistema la acepta.
- **RF-38-AC-8** — **Dado que** un analista registra una compartición por la API, **cuando** indica como destinatario "OEFA" fuera de las tres categorías, **entonces** el sistema la rechaza indicando las categorías válidas.
- **RF-38-AC-9** — **Dado que** hoy es 27/09/2026, **cuando** un analista registra una compartición con fecha 28/09/2026, **entonces** el sistema la rechaza indicando que la fecha no puede ser futura.
- **RF-38-AC-10** — **Dado que** una versión no está validada ni compartida por urgencia, **cuando** un analista intenta registrar la compartición de su ficha, **entonces** el sistema la rechaza indicando que falta la validación y que el autor puede usar la ruta de urgencia (RF-16).
- **RF-38-AC-11** — **Dado que** un analista exportó a KML 6 zonas que tienen versión validada o compartida por urgencia (RF-40), **cuando** registra que compartió esa exportación con los guardaparques, **entonces** la compartición queda vinculada al registro de esa exportación y aparece en el detalle de las 6 zonas.
- **RF-38-AC-12** — **Dado que** un analista exportó a KML 6 zonas y una de ellas, EA-2026-020, no tiene versión validada ni compartida por urgencia, **cuando** intenta registrar la compartición de esa exportación, **entonces** el sistema la rechaza indicando EA-2026-020.
- **RF-38-AC-13** — **Dado que** la red saliente está monitoreada y hay un servidor de correo simulado, **cuando** un analista registra una compartición, **entonces** no se envía ningún correo, mensaje ni solicitud a un destinatario externo.
- **RF-38-AC-14** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** intenta registrar una compartición por la API, **entonces** la API responde 403 y no se crea el registro.
- **RF-38-AC-15** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en el detalle de una zona validada, **cuando** revisa las acciones disponibles, **entonces** no ve la opción de registrar una compartición.

#### RF-39 — Resumen mensual para la coordinación

**Descripción:** El sistema debe tomar y **almacenar una foto** de las zonas al **último día de cada mes a las 23:59 (hora de Lima)**, con el número de zonas no fusionadas por nivel y por estado a esa fecha, agregado por **sector** o por **cuenca** (a elección del usuario), incluida la fila **"Fuera de sectores"**, y mostrar su evolución en los últimos 12 meses. El resumen se muestra **sin coordenadas precisas**: no incluye coordenadas, geometrías ni mapas con la ubicación de las zonas (RD-11). Una zona que intersecta varios sectores se cuenta en cada uno y una sola vez en el total.
**Prioridad:** Could | **Fuente:** Sección C, P2, P7 (C-13) | **Casos de uso:** UC-35

**Criterios de aceptación:**

- **RF-39-AC-1** — **Dado que** al 30/09/2026 a las 23:59 el sector "Malinowski" tenía 3 zonas de nivel alto y 2 de nivel medio, 1 de ellas en "requiere verificación", **cuando** la coordinación abre el resumen de septiembre de 2026 agregado por sector, **entonces** la fila "Malinowski" muestra 3 en alta, 2 en media y 1 en "requiere verificación".
- **RF-39-AC-2** — **Dado que** la foto de septiembre se tomó el 30/09/2026 a las 23:59 y una zona cambió de nivel el 02/10/2026, **cuando** se consulta el resumen de septiembre, **entonces** la zona se cuenta con el nivel que tenía al 30/09/2026.
- **RF-39-AC-3** — **Dado que** los sectores "Malinowski Alto" y "Malinowski Bajo" pertenecen a la cuenca "Malinowski", **cuando** el usuario cambia la agregación a cuenca, **entonces** la fila "Malinowski" suma las zonas de ambos sectores.
- **RF-39-AC-4** — **Dado que** 2 zonas no intersectan ningún sector al cierre del mes, **cuando** se consulta el resumen por sector o por cuenca, **entonces** aparece la fila "Fuera de sectores" con 2 zonas.
- **RF-39-AC-5** — **Dado que** existen fotos de los últimos 12 meses, **cuando** el usuario abre la evolución mensual, **entonces** obtiene, para cada uno de los 12 meses, el número de zonas por nivel.
- **RF-39-AC-6** — **Dado que** se consulta el resumen, **cuando** se inspecciona la respuesta de la API, **entonces** no contiene coordenadas, geometrías ni mapas con la ubicación de las zonas.
- **RF-39-AC-7** — **Dado que** una zona intersecta dos sectores, **cuando** se genera el resumen por sector, **entonces** la zona se cuenta en ambos sectores y una sola vez en el total.
- **RF-39-AC-8** — **Dado que** no hay una sesión iniciada, **cuando** se solicita el resumen a la API, **entonces** el sistema responde 401 y no entrega datos.

#### RF-40 — Exportación de zonas en GeoPackage y KML

**Descripción:** El sistema debe exportar las zonas de la lista filtrada (p. ej., las que están en "requiere verificación") en **GeoPackage** y **KML**, en EPSG:4326, con los atributos código, nivel, puntaje vigente, estado, fecha de creación, fecha del último cambio de estado, fuentes y comentario del analista (el último del historial de estados), **sin titulares** (RD-18). Los archivos deben poder cargarse en QField y Avenza para llevarlos a campo sin conexión. Si el filtro no devuelve zonas, se genera igualmente el archivo con 0 elementos y se muestra un aviso. Cada exportación queda registrada (RF-20).
**Prioridad:** Must | **Fuente:** Sección C, P2, P3, P5, P7 (C-12) | **Casos de uso:** UC-36

**Criterios de aceptación:**

- **RF-40-AC-1** — **Dado que** la lista filtrada por "requiere verificación" muestra 6 zonas, **cuando** un analista la exporta a GeoPackage y se lee con `ogrinfo`, **entonces** el archivo tiene 6 elementos en EPSG:4326, cada uno con código, nivel, puntaje vigente, estado, fecha de creación, fecha del último cambio de estado, fuentes y comentario del analista.
- **RF-40-AC-2** — **Dado que** la lista filtrada muestra las mismas 6 zonas, **cuando** un analista la exporta a KML y se lee con `ogrinfo`, **entonces** el archivo se lee sin errores y tiene 6 elementos con esos mismos atributos.
- **RF-40-AC-3** — **Dado que** el último comentario del historial de estados de una zona es "posibles pozas junto al afluente", **cuando** se exporta a GeoPackage, **entonces** su atributo de comentario del analista es "posibles pozas junto al afluente".
- **RF-40-AC-4** — **Dado que** una de las zonas exportadas cruza una concesión minera, **cuando** se inspeccionan el GeoPackage y el KML, **entonces** no contienen ningún atributo ni texto con el nombre del titular.
- **RF-40-AC-5** — *(Prueba de aceptación manual.)* **Dado que** se generaron el GeoPackage y el KML de 6 zonas, **cuando** se cargan en QField y en Avenza en un celular sin conexión, **entonces** las 6 zonas se ven en su ubicación y sus atributos se pueden consultar.
- **RF-40-AC-6** — **Dado que** un analista exporta zonas a GeoPackage o KML, **cuando** se consulta la bitácora, **entonces** hay un registro con el formato, el filtro, el número de zonas, sus códigos, el usuario y la fecha y hora (RF-20).
- **RF-40-AC-7** — **Dado que** el filtro aplicado no devuelve zonas, **cuando** un analista exporta a GeoPackage, **entonces** se genera el archivo con 0 elementos y el sistema muestra el aviso "La exportación no contiene zonas".
- **RF-40-AC-8** — **Dado que** un usuario con rol coordinación está autenticado, **cuando** solicita la exportación a GeoPackage o KML por la API, **entonces** la API responde 403 y no se genera el archivo.
- **RF-40-AC-9** — *(Prueba E2E de interfaz.)* **Dado que** un usuario con rol coordinación está en la lista de zonas, **cuando** revisa las acciones disponibles, **entonces** no ve las opciones de exportar a GeoPackage o KML.
- **RF-40-AC-10** — **Dado que** no hay una sesión iniciada, **cuando** se solicita la exportación o el archivo exportado, **entonces** el sistema responde 401 y no entrega el archivo (RNF-01).

#### Convención de IDs y línea base congelada (v3.0)

- **Línea base:** la v3.0 es la **nueva línea base** del proyecto y queda **congelada** con este
  documento. Reemplaza a la de la v2.0, cuyos IDs ningún artefacto posterior llegó a usar. Las
  correcciones de la revisión técnica V-01 a V-26 se aplicaron antes del congelamiento, por lo que
  la numeración de criterios de esta versión es la definitiva.
- **Requerimientos funcionales:** RF-01 a RF-40. RF-24 y RF-26 están **retirados**: conservan su
  número, sin criterios, y **ese número no se reutiliza**. Los RF nuevos de la v3.0 empiezan en
  RF-31; cualquier RF futuro empezará en RF-41.
- **Criterios:** `RF-xx-AC-n`, consecutivos desde AC-1 en cada RF. Desde la v3.0 son inmutables:
  un criterio que se elimine conserva su ID sin reutilizarlo, y uno nuevo toma el siguiente número
  libre de su RF.
- **Trazabilidad:** cada endpoint de `openapi.yaml` (S04-A2) referencia los IDs que implementa, y
  cada prueba se nombra `test_RF_xx_AC_n` (S09-A1).
- **Tipos de verificación:** sin marca, prueba automatizada contra la API o los archivos
  generados; *(Prueba E2E de interfaz.)*, prueba automatizada en el navegador; *(Prueba de
  aceptación manual.)*, prueba no automatizada.

### 3.2 Requerimientos no funcionales

Cada RNF indica cómo se verifica: **Prueba** (automatizada o manual con un resultado medible),
**Inspección** (revisión de configuración, código o documento) o **Demostración** (ejecución
observada por el cliente).

| ID | Requerimiento | Categoría | Verificación | Prioridad | Fuente |
|---|---|---|---|---|---|
| RNF-01 | Todas las funciones y datos del sistema requieren autenticación. Ningún contenido, incluidos archivos exportados y fotos, es accesible de forma anónima. | Seguridad | Prueba: toda ruta de la API y todo archivo solicitado sin sesión responde 401. | Must | P6, P7; Sección C, P2-seg |
| RNF-02 | El control de acceso se basa en los dos roles y la matriz de la sección 2.3. Toda acción no permitida para el rol es rechazada **en el servidor**, no solo ocultada en la interfaz. En particular, la coordinación recibe 403 al cambiar estados, ajustar o quitar ajustes de prioridad, configurar pesos, lanzar o reintentar análisis, decidir candidatos, registrar la evaluación de humo o marcas del analista, crear zonas o versiones, enviar a revisión, compartir por urgencia, cargar capas, sincronizar alertas, exportar **polígonos, listas, capas GeoPackage/KML o expedientes** y registrar comparticiones; y el analista recibe 403 al gestionar usuarios, perfiles, credenciales o sectores y al suprimir datos. | Seguridad | Prueba: matriz rol × acción con todas las filas de la sección 2.3; cada acción no permitida responde 403 aunque se invoque directamente en la API. | Must | P2, P7; Sección C, P2-seg, P7 |
| RNF-03 | Toda comunicación usa HTTPS (TLS 1.2 o superior). El inicio de sesión exige contraseña (mínimo 12 caracteres, almacenada con bcrypt o Argon2) **y un segundo factor TOTP obligatorio** para todos los roles. Las sesiones expiran tras 30 minutos de inactividad (S-07). La coordinación puede restablecer el segundo factor de un usuario, y la acción queda en la bitácora. | Seguridad | Inspección de configuración TLS y del almacenamiento de contraseñas; prueba: sin un código TOTP válido el inicio de sesión se rechaza; prueba de expiración de sesión. | Must | P2 (implícito) |
| RNF-04 | La bitácora de auditoría es de solo inserción. Registra sincronizaciones y cargas, cambios de estado, **reaperturas**, **fusiones**, **ajustes de prioridad**, **cambios de pesos**, envíos a revisión, validaciones, devoluciones, comparticiones por urgencia, versiones nuevas, **comparticiones**, exportaciones, supresiones (solo identificadores), gestión de usuarios y **cada consulta de una zona o ficha** (quién y cuándo): ninguna función del sistema permite editar ni borrar sus registros, y el usuario de base de datos de la aplicación no tiene permisos UPDATE ni DELETE sobre esa tabla. | Seguridad / auditabilidad | Inspección de permisos de base de datos; prueba de que no existe ninguna operación de edición o borrado y de que cada tipo de acción genera su entrada. | Must | P2, P3 (implícito); Sección C, P2-seg, P7 |
| RNF-05 | Un análisis de comparación sobre un área de hasta 2,000 ha, incluida la propuesta de candidatos (RF-23), se completa en 5 minutos o menos en el 90 % de los casos (S-02). Se ejecuta en segundo plano sin bloquear la interfaz y notifica al usuario dentro del sistema al terminar. | Rendimiento | Prueba: 20 análisis de 2,000 ha; al menos 18 terminan en 5 min o menos. | Should | P5, P7 |
| RNF-06 | El sistema soporta al menos **1,000 alertas nuevas por semana** (ingesta y agrupación, RF-31 y RF-32), **300 zonas activas** (1.3) y 20 análisis completos por semana, sin incumplir RNF-05 ni los tiempos de carga de la lista y del detalle de RNF-08. | Escalabilidad | Prueba de carga: ingesta de 1,000 alertas con 300 zonas activas, seguida de la medición de RNF-08. | Should | P5; Sección C, P1-seg, P5-seg (C-17) |
| RNF-07 | El trabajo en curso (polígonos, comentarios, notas y cambios de una zona) se guarda automáticamente. Ante un corte de conexión se pierden como máximo los últimos 30 segundos de trabajo (parámetro S-03), y al reconectar el sistema recupera el borrador. | Confiabilidad | Prueba: cortar la red durante una edición y verificar lo recuperado. | Should | P5, P7; Sección C, P5 |
| RNF-08 | Con una conexión limitada a 1 Mbps (parámetro S-04) y caché vacía, la **lista de zonas** y el **detalle de una zona** (datos, desglose, marcas e historial) cargan y son utilizables en **5 segundos o menos**, y la pantalla principal del mapa en 10 segundos o menos. | Rendimiento | Prueba con limitación de red en el navegador (1 Mbps). | Should | P5; Sección C, P5, P7 (C-16) |
| RNF-09 | La interfaz es adaptable (*responsive*): la consulta de zonas y fichas, la revisión de contenido de fichas, la bitácora y el resumen son usables en celulares desde 360 px de ancho, y todas las funciones en pantallas desde 1366 px. Soporta las dos últimas versiones de Chrome, Firefox y Safari. | Usabilidad / portabilidad | Prueba en 360 px y 1366 px con los navegadores indicados. | Should | P5; Sección C, P2 |
| RNF-10 | La base de datos y los archivos (fotos, capas y fichas) se respaldan automáticamente cada día en una ubicación distinta del servidor principal. Se pierden como máximo 24 horas de datos, las zonas, sus versiones, fichas y respaldos se conservan al menos 5 años (S-05), la v1 no permite eliminar zonas, la restauración reaplica las supresiones registradas (RF-30) y se prueba al menos una vez por trimestre. | Confiabilidad | Inspección de la política de respaldo; demostración de una restauración completa con una supresión posterior al respaldo. | Must | P5, P7; Sección C, P5, P5-seg, P6-seg |
| RNF-11 | El sistema no requiere licencias de software de pago (costo de licencias: USD 0), y el costo mensual de infraestructura, con VPS y almacenamiento de respaldos, no supera USD 25 (S-06). | Costo / sostenibilidad | Inspección de licencias de las dependencias y de la factura mensual de infraestructura. | Must | P6, P7; Sección C, P6 |
| RNF-12 | El sistema se despliega con un solo comando e incluye un manual de operación en español (despliegue, respaldo, restauración, actualización de capas y sincronización de alertas). Un analista SIG sin conocimientos de programación puede seguirlo. | Mantenibilidad | Demostración: un analista de la ONG despliega y restaura el sistema siguiendo solo el manual. | Must | P6; Sección C, P6 |
| RNF-13 | La ficha PDF es comprensible para la jefatura de la RN Tambopata y para una persona sin conocimientos de SIG. | Usabilidad | Demostración: la **coordinación (no SIG)** revisa y aprueba la plantilla antes de liberar la v1. | Must | P2, P3; Sección C, P2, P3 |
| RNF-14 | La interfaz, los mensajes de error, la ficha PDF, las exportaciones y la documentación están en español. | Usabilidad | Inspección de la interfaz y de los documentos. | Must | Implícito |
| RNF-15 | El sistema obtiene imágenes de Sentinel-2 y Landsat 8/9 y alertas RADD mediante GEE. El acceso a fuentes de imágenes y de alertas está detrás de una interfaz común, de modo que agregar otra fuente (p. ej., GLAD) no requiere modificar el módulo de análisis ni el de agrupación. El manual de operación documenta cómo cambiar a **Copernicus Data Space Ecosystem** (Sentinel-2 gratuito) y a la carga de archivos RADD si cambian las condiciones de GEE, y los términos de uso de GEE se revisan una vez al año. | Extensibilidad / continuidad | Inspección del diseño y del manual: el análisis y la ingesta no dependen de una fuente concreta y el plan alternativo está documentado. | Should | P4; Sección C, P6 (C-18) |

### 3.3 Requerimientos de dominio

| ID | Requerimiento | Prioridad | Fuente | Relacionado con |
|---|---|---|---|---|
| RD-01 | Toda coordenada de las fichas y de las exportaciones de polígonos debe expresarse en UTM WGS84 zona 19 Sur (EPSG:32719); la ficha agrega EPSG:4326. La única excepción son las capas para campo (RF-40), en EPSG:4326, que exigen el formato KML y las aplicaciones móviles. | Must | P3; Sección C, P3 | RF-17, RF-18, RF-40 |
| RD-02 | Toda imagen usada en una ficha debe tener fuente y fecha de adquisición identificables. Sin ellas no puede sustentar ninguna afirmación de la ficha. | Must | P3, P4; Sección C, P4-seg | RF-07, RF-15, RF-17 |
| RD-03 | Los mapas de una ficha deben incluir escala y fecha visibles, y la ficha debe identificar a sus autores y el tipo de revisión (validación técnica, revisión de contenido o compartición sin segunda revisión). | Must | P3; Sección C, P7 | RF-16, RF-17 |
| RD-04 | Los datos de fuentes oficiales (INGEMMET, GeoBosques, SERNANP) nunca se modifican. Una afirmación que los contradiga debe citar un documento que la respalde; si no lo cita, se presenta como observación del equipo y no como hecho (RF-14). | Must | P4 | RF-14 |
| RD-05 | Las detecciones propias deben declararse como tales y distinguirse de las alertas ingeridas, porque no tienen el respaldo de una fuente oficial. | Must | P4 | RF-13 |
| RD-06 | El catastro minero de INGEMMET cambia con frecuencia. Todo cruce con él debe indicar la fecha de la versión usada, para no reportar como vigentes petitorios extinguidos. | Must | P4; Sección C, P4 | RF-02, RF-03, RF-10 |
| RD-07 | Una imagen no es válida para una ficha si su nubosidad dentro del área supera el **umbral de validez S-01**, o si hay humo visible sobre el área de cambio (lo evalúa el analista en la evaluación de humo, porque la máscara de nubes no lo detecta). Para detectar claros de 1-2 ha se requiere una resolución de 10 m o mejor (Sentinel-2); Landsat (30 m) solo sirve de complemento. | Must | P4; Sección C, P4-seg | RF-08, RF-15, RF-16, RF-36 |
| RD-08 | Las comparaciones deben considerar la estacionalidad (ríos en época seca, inundación estacional, chacras estacionales, quemas). La comparación con el mismo mes del año anterior es la práctica de referencia. | Should | P1, P3; Sección C, P4-seg | RF-07, RF-36 |
| RD-09 | El tratamiento de datos personales de informantes y de personas que aparezcan en fotos debe cumplir la Ley N.º 29733, Ley de Protección de Datos Personales del Perú. El sistema aplica **minimización**: no tiene campos para DNI ni teléfonos, el informante es opcional y seudónimo, se eliminan los metadatos de las fotos (RF-21) y no se importan los nombres de titulares de derechos (RD-18). | Must | P6, P7; Sección C, P2-seg, P6 (C-14) | RF-03, RF-21, RF-30, RNF-01 |
| RD-10 | Publicar información sobre territorios de comunidades nativas, o datos aportados por ellas, requiere su consentimiento. La v1 no tiene funciones de publicación: la información solo sale como ficha o exportación, que quedan registradas (RF-20, RF-38). | Must | P6, P7 | RF-17, RF-20, RF-38, RNF-01 |
| RD-11 | Son confidenciales la ubicación de las zonas en "requiere verificación", las verificaciones en campo planificadas y la identidad de los informantes. El resumen para la coordinación se presenta a nivel de sector o cuenca, sin coordenadas precisas. | Must | P2; Sección C, P2-seg, P7 (C-13, C-14) | RF-21, RF-39, RF-40, RNF-01, RNF-02 |
| RD-12 | El uso de Google Earth Engine, RADD, GeoBosques, INGEMMET y cualquier otra fuente debe respetar sus términos de uso para una organización sin fines de lucro. Las imágenes de **Planet/NICFI** no se pueden redistribuir y no se usan en la v1. Los términos de uso de GEE se revisan una vez al año. | Must | P4, P6; Sección C, P1, P6 (C-18) | RNF-11, RNF-15 |
| RD-13 | Las fichas y los polígonos de zonas activas solo pueden compartirse con el equipo, con la jefatura de la RN Tambopata, con los guardaparques o el equipo de campo y, solo en coordinación con la jefatura y con la referencia registrada, con otros destinatarios. Cada compartición se registra y exige una versión revisada o compartida por urgencia. | Must | P3; Sección C, P6 (C-15) | RF-18, RF-20, RF-38, RF-40 |
| RD-14 | El ámbito geográfico del sistema es la Reserva Nacional Tambopata y su zona de amortiguamiento, según los límites oficiales del SERNANP. Lo que está fuera se rechaza. Las capas de referencia y el sistema de coordenadas se configuran para ese ámbito. | Must | P3, P5; Sección C, P1, P5-seg; decisión del alumno | RF-01, RF-05, RF-13, RF-21, RF-31 |
| RD-15 | La primera versión debe estar operativa en 12 semanas, antes del inicio de la temporada seca (junio), y mostrar avances en el reporte de medio término al donante principal. | Must | P6; Sección C, P6 | — |
| RD-16 | La ficha es un **documento técnico de apoyo**: no determina causas ni es una alerta oficial, y requiere verificación en campo. Debe explicar el método e identificar a los especialistas que la elaboraron y revisaron. Como fuente de una imagen se cita el producto satelital (p. ej., Copernicus Sentinel-2), no la plataforma de procesamiento (GEE). | Must | Sección C, P4-seg, P6 | RF-17 |
| RD-17 | El sistema **no determina ni etiqueta causas** de los cambios. Las hipótesis solo las marca el analista, se distinguen visualmente como "marca del analista" y nunca se generan automáticamente. | Must | Sección C, P4-seg, P7 (C-9) | RF-23, RF-33, RF-36 |
| RD-18 | Nunca se muestra, exporta ni imprime el nombre del titular de un derecho junto a un cambio; solo el tipo de derecho, el código y el estado. | Must | Sección C, P2-seg, P7 (C-9, C-14) | RF-01, RF-03, RF-10, RF-17, RF-40 |
| RD-19 | La jefatura de la RN Tambopata es la autoridad. EcoAlert no emite alertas oficiales ni envía información a terceros; la difusión se coordina con la jefatura y las denuncias van por vías formales fuera del sistema. | Must | Sección C, P4-seg, P6 (C-15) | RF-17, RF-37, RF-38 |
