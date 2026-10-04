# Especificación de Requerimientos de Software (SRS) — Equipo

## EcoAlert Tambopata

| Campo | Valor |
|---|---|
| Versión | 1.0 (línea base de equipo) |
| Fecha | 04/10/2026 |
| Estándar de referencia | IEEE 830 (simplificado), misma estructura que S02-A1 |
| Equipo | Equipo 6 — TC5062, Gpo 10 |
| Integrantes | Integrante 1: Miguel Angel Arevalo Andrade (A01840503) · Integrante 2: *[nombre y matrícula]* · Integrante 3: Anthony Gerardo Gutarra Sánchez (A01840622) · Integrante 4: *[nombre y matrícula]* |
| Insumos | SRS individuales de S02-A1 (`insumos/`) y `insumos/proyecto_base.md` |
| Registro de consolidación | `diferencias_SRS.md` (aportes de cada integrante, conflictos C-01 a C-30 y correspondencia de IDs) |

> Este documento es el **contrato compartido del proyecto** y la fuente de verdad para todas las
> actividades de equipo desde S03: diseño de API, backend, frontend, pruebas y documentación
> final. Integra los cuatro SRS individuales; las decisiones de consolidación y el origen de cada
> requerimiento están en `diferencias_SRS.md`.

---

## 1. Introducción

### 1.1 Propósito del documento

Este documento especifica los requerimientos funcionales, no funcionales y de dominio de
**EcoAlert Tambopata**, una aplicación web de apoyo al monitoreo de la pérdida de cobertura
forestal en la Reserva Nacional Tambopata y su zona de amortiguamiento (Madre de Dios, Perú).

Está dirigido al equipo de desarrollo y a quien valide el producto. Fija:

- qué debe hacer el sistema y qué no debe hacer (alcance y reglas de dominio);
- la prioridad de cada requerimiento (MoSCoW), que define qué construye el equipo primero;
- criterios de aceptación verificables, con un identificador único `RF-XX-AC-Y` que se usa en el
  contrato de la API y en los nombres de las pruebas (sección 3, *Convención de IDs*).

### 1.2 Alcance del sistema

EcoAlert Tambopata ayuda a los **analistas SIG** a decidir **qué zonas revisar primero y por qué**.
El sistema:

1. Recibe **alertas de pérdida de cobertura** publicadas por fuentes oficiales (GeoBosques en la
   v1; RADD como mejora) y las **agrupa en zonas de cambio** que persisten en el tiempo.
2. Muestra cada zona en un mapa con su **contexto territorial**: reserva, zona de amortiguamiento,
   catastro minero y distancia a ríos.
3. Calcula una **prioridad sugerida** de 0 a 100 con un **desglose por factor siempre visible**,
   que el analista puede ajustar con justificación.
4. Registra el **estado de revisión** de cada zona y su historial.
5. **Compara dos periodos** con las alertas de cada zona y guarda cada comparación de forma
   inmutable.
6. **Exporta** la lista de zonas (CSV) y sus geometrías (GeoJSON).

La prioridad es una **recomendación**. La interpretación y la decisión final son siempre del
especialista. El sistema **no determina ni etiqueta causas** (p. ej., minería), **no establece la
legalidad** de un cambio y **no emite alertas oficiales**.

**Prioridades MoSCoW.** **Must**: núcleo que el equipo se compromete a construir y probar.
**Should**: se construye después del núcleo si el plazo lo permite. **Could**: deseable, solo con
holgura. **Won't**: fuera de esta versión (lista siguiente).

**Fuera de alcance (Won't en esta versión):**

- Clasificación automática del tipo o la causa del cambio ("posible minería") y cualquier
  determinación de legalidad (RD-02).
- Aplicación móvil y modo sin conexión con GPS. El trabajo de campo se apoya en exportaciones que
  se abren en QField o Avenza (RF-22, Should).
- Notificaciones fuera del sistema (correo, SMS, push) y envío de información a terceros (RD-05).
- Varias organizaciones con datos aislados, rol Superadmin y visor externo o público.
- Ámbitos distintos de la RN Tambopata y su zona de amortiguamiento (RD-01).
- Series temporales de más de dos periodos, índice NDFI y alertas GLAD.
- Ciclo de versiones de fichas con validación técnica o de contenido, expediente ZIP, resumen
  mensual y supresión de datos personales.
- Reporte PDF de varias zonas a la vez (la ficha es por zona, RF-23).
- Envío de credenciales u otros mensajes por correo al crear usuarios (RF-02).

### 1.3 Definiciones y acrónimos

| Término | Definición |
|---|---|
| **SRS / RF / RNF / RD** | Especificación de requerimientos / requerimiento funcional / no funcional / de dominio. |
| **MVP** | Producto mínimo viable: los requerimientos **Must** de este documento. |
| **SIG** | Sistema de Información Geográfica. |
| **RN Tambopata / ZA** | Reserva Nacional Tambopata / su zona de amortiguamiento, según los límites oficiales del SERNANP. Juntas forman el **ámbito** del sistema. |
| **SERNANP** | Servicio Nacional de Áreas Naturales Protegidas; la jefatura de la reserva es la autoridad. No tiene cuenta en el sistema. |
| **GeoBosques** | Plataforma del Estado peruano que publica alertas de pérdida de bosque. En la v1 se ingiere por carga de archivo. |
| **RADD** | Alertas de perturbación forestal por radar (Sentinel-1), disponibles vía Google Earth Engine. Should. |
| **GEE** | Google Earth Engine, plataforma de procesamiento de imágenes satelitales. |
| **INGEMMET** | Instituto Geológico, Minero y Metalúrgico; fuente del catastro minero. |
| **NDVI** | Índice de vegetación de diferencia normalizada. Solo se usa en RF-27 (Could). |
| **Alerta** | Polígono de posible pérdida de cobertura **publicado por una fuente externa**, con fuente, código, geometría, fecha de detección y fecha de ingesta. El sistema **no genera** alertas propias. |
| **Fecha de detección / de ingesta** | Fecha en que la fuente detectó la alerta / fecha en que el sistema la recibió. Todos los cálculos usan la fecha de detección. |
| **Zona de cambio (zona)** | Entidad central del sistema: agrupación persistente de alertas cercanas en espacio y tiempo (RF-05), con código `EA-AAAA-NNN`, estado, prioridad e historial. Sobrevive entre comparaciones de periodos. |
| **Zona activa / cerrada** | Activa: en estado nueva, en revisión o requiere verificación. Cerrada: revisada o descartada. |
| **Capa de referencia** | Capa geográfica cargada por un analista con fuente y fecha de corte: límite de la reserva, ZA, ríos, catastro minero. |
| **Fecha de corte** | Fecha a la que corresponden los datos de una capa o de una carga de alertas, declarada al cargarla. |
| **Periodo** | Rango de fechas `[inicio, fin]`, con inicio ≤ fin. Un periodo de un solo día es válido. |
| **Comparación de periodos (análisis)** | Ejecución que compara las alertas de cada zona en dos periodos (RF-14). Se almacena automáticamente y es **inmutable**. |
| **Limitación conocida** | Condición de disponibilidad, calidad o comparabilidad de los datos que afecta la interpretación de un análisis (p. ej., periodo posterior a la última fecha de corte). Se registra y se muestra; nunca se oculta. |
| **Puntaje calculado / ajustado / vigente** | Calculado: el que produce RF-09. Ajustado: el que fija un analista (RF-11). Vigente: el ajustado si existe; si no, el calculado. El nivel y el orden usan el vigente. |
| **Nivel de prioridad** | Alta (puntaje ≥ 70), media (40–69) o baja (< 40). "No disponible" si no se puede calcular ningún factor. |
| **Desglose** | Aporte en puntos y texto explicativo de cada factor del puntaje. |
| **Fecha de referencia del cálculo** | Fecha (America/Lima) respecto de la cual se miden la recencia y las ventanas de persistencia. Se registra con cada puntaje. |
| **Marca de confianza** | Advertencia asociada a una zona que **no la oculta ni cambia su puntaje** (RF-13). Puede ser automática o del analista. |
| **Marca del analista** | Hipótesis o advertencia en texto libre escrita por un analista, rotulada "Marca del analista". Es la única forma de registrar una hipótesis de causa. |
| **Notificación** | Mensaje enviado **fuera** del sistema (correo, SMS, push). Fuera de alcance. Los avisos **dentro** de la interfaz se llaman **indicadores** y sí están permitidos (RF-07, RF-29). |
| **Observación** | Nota de texto libre sobre una zona, con autor y fecha, que no cambia su estado (RF-34). |
| **Responsable** | Analista SIG asignado a una zona activa (RF-39). No cambia el estado de la zona. |
| **SRC** | Sistema de referencia de coordenadas. EPSG:32719 = UTM WGS84 zona 19 Sur; EPSG:4326 = WGS84 geográficas. |
| **PS-xx** | Parámetro del sistema (sección 2.4). |

---

## 2. Descripción general

### 2.1 Perspectiva del producto

EcoAlert Tambopata es un sistema nuevo. Funciona como capa de **integración y priorización** sobre
fuentes externas (GeoBosques, INGEMMET, límites del SERNANP y, como mejora, RADD e imágenes
Sentinel-2 vía GEE). No reemplaza esas fuentes ni modifica sus datos (RD-06), y no fusiona sus
resultados en un veredicto: cada alerta conserva siempre su fuente.

Es una aplicación web para navegador de escritorio con este stack: backend Python 3.12 +
FastAPI, PostgreSQL 17 con PostGIS, frontend React 19 + TypeScript, despliegue con Docker Compose
en un único VPS. Complementa el análisis profesional y la verificación en campo; no las reemplaza.

### 2.2 Funciones del producto

| Bloque | Función | RF | Prioridad |
|---|---|---|---|
| Acceso | Inicio de sesión, sesión que expira, gestión de usuarios y roles | RF-01, RF-02 | Must |
| Datos | Carga de capas de referencia; ingesta de alertas GeoBosques; frescura de fuentes | RF-03, RF-04, RF-07 | Must |
| Zonas | Agrupación en zonas; mapa; contexto territorial | RF-05, RF-06, RF-08 | Must |
| Priorización | Puntaje explicado; lista priorizada; ajuste manual | RF-09, RF-10, RF-11 | Must |
| Revisión | Estados e historial; marcas de confianza | RF-12, RF-13 | Must |
| Periodos | Comparación de dos periodos por alertas; consulta de análisis anteriores | RF-14, RF-15 | Must |
| Exportación | Lista en CSV; zonas en GeoJSON | RF-16, RF-17 | Must |
| Mejoras | Imágenes lado a lado, RADD, reapertura, pesos, GeoPackage/KML, ficha PDF, bitácora, TOTP, zonas manuales | RF-18 a RF-26 | Should |
| Mejoras (I4) | Observaciones, capa de comunidades nativas, filtros y orden adicionales, Shapefile | RF-34 a RF-37 | Should |
| Opcionales | NDVI, fusión de zonas, novedades, sectores, discrepancias, formatos extra, reportes de campo | RF-27 a RF-33 | Could |
| Opcionales (I4) | Selección manual de zonas para exportar, responsable de la zona | RF-38, RF-39 | Could |

### 2.3 Características del usuario

La v1 tiene **dos roles**, que no heredan permisos entre sí.

| Rol | Perfil | Uso | Permisos |
|---|---|---|---|
| **Analista SIG** | Especialista SIG o analista ambiental. Domina QGIS y teledetección; **no programa**. | Diario o semanal: carga datos, revisa la lista priorizada, analiza zonas, cambia estados, compara periodos y exporta. | Todo lo operativo. **No** gestiona usuarios. |
| **Coordinación** | Coordinador(a) del programa. Conoce el dominio; **no es SIG**. | Semanal o mensual: consulta zonas, prioridades y comparaciones, y administra las cuentas. | Consultar todo, comparar periodos y gestionar usuarios. **No** carga datos, no cambia estados ni prioridades, no registra marcas y no exporta. |

No tienen cuenta en la v1 la jefatura de la reserva (SERNANP), los guardaparques ni otras
instituciones.

**Matriz de permisos** (✔ permitido · — rechazado con **403 en el servidor**, RNF-02). Solo
incluye los RF Must; cada RF Should o Could indica sus permisos en su descripción.

| Acción | Analista SIG | Coordinación |
|---|:---:|:---:|
| Ver mapa, capas, fechas de corte y avisos de frescura (RF-06, RF-07) | ✔ | ✔ |
| Ver lista, detalle, desglose, contexto, marcas e historial de zonas (RF-08 a RF-13) | ✔ | ✔ |
| Ejecutar una comparación de periodos y consultar análisis anteriores (RF-14, RF-15) | ✔ | ✔ |
| Cargar capas de referencia y archivos de alertas (RF-03, RF-04) | ✔ | — |
| Ajustar la prioridad y quitar el ajuste (RF-11) | ✔ | — |
| Cambiar estados y reabrir zonas (RF-12) | ✔ | — |
| Registrar y retirar marcas del analista (RF-13) | ✔ | — |
| Exportar la lista (CSV) y las zonas (GeoJSON) (RF-16, RF-17) | ✔ | — |
| Crear, editar y desactivar cuentas (RF-02) | — | ✔ |

### 2.4 Restricciones

- **Ámbito:** RN Tambopata y su ZA (RD-01).
- **Datos externos:** el sistema depende de la disponibilidad y del formato de fuentes que el
  equipo no controla. Sus datos llegan con un desfase de 1 a 4 semanas (RD-08) y pueden estar
  incompletos o ser contradictorios. En esos casos el sistema informa la situación y no presenta
  el resultado como concluido (RNF-08).
- **Resolución:** la detección está limitada por la resolución de las fuentes (RD-07).
- **Tecnología y costo:** stack de la sección 2.1, sin licencias de pago, un VPS de USD 25 al mes
  como máximo (RNF-09).
- **Plazo:** el núcleo Must debe poder construirse y probarse en el curso por un equipo de tres
  personas.
- **Pesos y umbrales preliminares:** los pesos (PS-03) y las normalizaciones (PS-05 a PS-08) son
  valores iniciales que deben calibrarse con especialistas. Mientras no exista RF-21 (Should),
  solo cambian con una versión del sistema y **nunca se reajustan automáticamente** (RD-03).

#### Parámetros del sistema

| ID | Parámetro | Valor | Usado en |
|---|---|---|---|
| PS-01 | Distancia máxima de agrupación de una alerta a una zona activa | 500 m (distancia mínima entre geometrías, EPSG:32719) | RF-05 |
| PS-02 | Ventana temporal de agrupación en una zona activa | 90 días | RF-05 |
| PS-03 | Pesos por defecto de la priorización (versión de pesos 1) | Ubicación 35 · persistencia y crecimiento 25 · cercanía a ríos 15 · superficie 15 · recencia 10 (suma 100) | RF-09 |
| PS-04 | Umbrales de nivel | Alta ≥ 70 · media 40–69 · baja < 40 | RF-09 |
| PS-05 | Franja de la ZA "cercana al límite" de la reserva | 2 km | RF-09 |
| PS-06 | Normalización de superficie | 10 ha = 1 | RF-09 |
| PS-07 | Recencia | 1 si d ≤ 7 días; (90 − d) ÷ 83 si 7 < d < 90; 0 si d ≥ 90 | RF-09 |
| PS-08 | Persistencia: ventanas de 7 días contadas hacia atrás desde la fecha de referencia | 8 ventanas | RF-09 |
| PS-09 | Cercanía a ríos | 1 hasta 500 m; (2,000 − d) ÷ 1,500 entre 500 m y 2 km; 0 desde 2 km | RF-09 |
| PS-10 | Distancia a un río para la marca "posible dinámica fluvial" | ≤ 100 m | RF-13 |
| PS-11 | Área máxima para la marca "área pequeña" | < 1 ha | RF-13 |
| PS-12 | Expiración de sesión por inactividad | 30 min | RF-01 |
| PS-13 | Antigüedad de la última fecha de corte de alertas a partir de la cual se avisa "posiblemente desactualizada" | > 30 días | RF-07 |
| PS-14 | Tiempo máximo hasta mostrar un resultado, un estado de procesamiento o un error | 60 s | RNF-04 |
| PS-15 | Longitud mínima de contraseña | 12 caracteres | RF-02, RNF-03 |

#### Temas abiertos

| ID | Tema | Impacto |
|---|---|---|
| TA-01 | Calibrar los pesos (PS-03) y las normalizaciones con especialistas y resultados de campo. | RF-09, RF-21 |
| TA-02 | Fuente oficial y vigencia de la capa de ríos (¿ANA, IGN?). | RF-08, RF-09, RF-13 |
| TA-03 | Si se incorporan reportes de campo con datos personales (RF-33), definir las obligaciones de la Ley N.º 29733. | RF-33, RD-12 |
| TA-04 | Validar las entrevistas: todas las elicitaciones de S02-A1 fueron **simuladas**. Conviene confirmar el núcleo con un analista real. | Todo el documento |
| TA-05 | Fuente oficial y licencia de la capa de comunidades nativas (¿BDPI del Ministerio de Cultura?). | RF-35 |

---

## 3. Requerimientos específicos

**Criterios de aceptación.** Siguen el formato Given-When-Then: **Dado que** [precondición],
**cuando** [acción], **entonces** [resultado verificable]. Cada criterio prueba un solo
comportamiento. Los criterios sin marca se automatizan contra la API o contra los archivos
generados. Los marcados *(Prueba E2E de interfaz.)* se automatizan en el navegador. Los marcados
*(Prueba de aceptación manual.)* no se automatizan.

### 3.1 Requerimientos funcionales

---

#### RF-01 — Autenticación y sesión

**Descripción:** El sistema debe permitir el acceso solo a usuarios autenticados con usuario y
contraseña. La sesión expira tras 30 minutos de inactividad (PS-12). El mensaje de error de inicio
de sesión no revela si falló el usuario o la contraseña. Un usuario sin sesión que abre cualquier
pantalla es redirigido al inicio de sesión.
**Prioridad:** Must | **Origen:** I3:RF-01, I1:RF-28 (reducido), I1:RNF-01

**Criterios de aceptación:**

- **RF-01-AC-1** — **Dado que** existe una cuenta activa con contraseña válida, **cuando** el usuario inicia sesión con sus credenciales correctas, **entonces** el sistema crea una sesión y le permite acceder a las funciones de su rol.
- **RF-01-AC-2** — **Dado que** existe una cuenta activa, **cuando** se intenta iniciar sesión con una contraseña incorrecta, **entonces** el sistema responde 401 con el mensaje "Usuario o contraseña incorrectos" y no crea sesión.
- **RF-01-AC-3** — **Dado que** no existe la cuenta indicada, **cuando** se intenta iniciar sesión, **entonces** el sistema responde 401 con el mismo mensaje "Usuario o contraseña incorrectos".
- **RF-01-AC-4** — **Dado que** un usuario tiene una sesión sin actividad durante 31 minutos, **cuando** hace una nueva solicitud a la API, **entonces** el sistema responde 401 y exige iniciar sesión de nuevo.
- **RF-01-AC-5** — **Dado que** un usuario tiene una sesión con actividad hace 29 minutos, **cuando** hace una nueva solicitud a la API, **entonces** la solicitud se atiende normalmente.
- **RF-01-AC-6** — **Dado que** un usuario cerró sesión, **cuando** reutiliza el token o la cookie de esa sesión, **entonces** el sistema responde 401.
- **RF-01-AC-7** — *(Prueba E2E de interfaz.)* **Dado que** no hay una sesión iniciada, **cuando** se abre la URL de la pantalla del mapa, **entonces** el navegador es redirigido a la pantalla de inicio de sesión y no se muestra el mapa.

#### RF-02 — Gestión de usuarios y roles

**Descripción:** La coordinación debe poder crear cuentas con nombre completo, usuario (correo),
uno de los dos roles (analista SIG o coordinación) y una contraseña temporal de al menos 12
caracteres (PS-15). También debe poder editar el nombre y el rol, y desactivar o reactivar
cuentas. En el primer ingreso, el usuario debe cambiar la contraseña temporal. Las cuentas no se
eliminan, para conservar la autoría en el historial. No se puede desactivar la única cuenta
activa de coordinación.
**Prioridad:** Must | **Origen:** I1:RF-22 (sin perfiles de ficha ni sectores), I1:RF-28, I2:RF-10 (reducido a dos roles)

**Criterios de aceptación:**

- **RF-02-AC-1** — **Dado que** la coordinación está autenticada, **cuando** crea una cuenta con rol analista SIG y contraseña temporal de 12 caracteres, **entonces** la cuenta queda activa con ese rol.
- **RF-02-AC-2** — **Dado que** la coordinación crea una cuenta, **cuando** indica un rol distinto de "analista SIG" o "coordinación" (p. ej., "superadmin"), **entonces** el sistema rechaza la creación indicando los roles válidos.
- **RF-02-AC-3** — **Dado que** la coordinación crea una cuenta, **cuando** la contraseña temporal tiene 11 caracteres, **entonces** el sistema la rechaza indicando el mínimo de 12.
- **RF-02-AC-4** — **Dado que** la coordinación creó una cuenta con contraseña temporal, **cuando** el usuario inicia sesión por primera vez, **entonces** el sistema le exige definir una contraseña nueva antes de acceder a cualquier otra función.
- **RF-02-AC-5** — **Dado que** una cuenta de analista está activa, **cuando** la coordinación la desactiva y ese usuario intenta iniciar sesión con credenciales correctas, **entonces** el inicio de sesión se rechaza.
- **RF-02-AC-6** — **Dado que** un analista desactivado cambió estados de zonas, **cuando** se consulta el historial de esas zonas, **entonces** su nombre sigue apareciendo como autor.
- **RF-02-AC-7** — **Dado que** existe una cuenta, **cuando** se envía una solicitud de borrado a la API, **entonces** la API no expone la operación (404 o 405) y la cuenta sigue existiendo.
- **RF-02-AC-8** — **Dado que** hay una sola cuenta activa de coordinación, **cuando** se intenta desactivarla, **entonces** el sistema lo rechaza indicando que es la última cuenta de coordinación.
- **RF-02-AC-9** — **Dado que** un analista SIG está autenticado, **cuando** invoca el servicio de gestión de usuarios de la API, **entonces** la API responde 403.
- **RF-02-AC-10** — *(Prueba E2E de interfaz.)* **Dado que** un analista SIG inició sesión, **cuando** revisa el menú principal, **entonces** no ve la opción de gestión de usuarios.

#### RF-03 — Carga de capas de referencia

**Descripción:** Un analista debe poder cargar o actualizar una capa de referencia de los tipos
siguientes, como Shapefile comprimido (.zip con .prj) o GeoJSON, indicando su **fuente** y su
**fecha de corte** (ambas obligatorias):

| Tipo de capa | Geometría | Atributos obligatorios |
|---|---|---|
| Límite de la RN Tambopata | Polígono | código, nombre |
| Zona de amortiguamiento | Polígono | código, nombre |
| Ríos | Línea | nombre (puede estar vacío) |
| Catastro minero (concesiones y petitorios) | Polígono | código, tipo de derecho (concesión / petitorio), estado |

Al cargar, el analista asigna las columnas del archivo a los atributos del tipo de capa. Las
columnas no asignadas no se almacenan. El catastro minero **no tiene ningún atributo para el
titular** (RD-04). El sistema reproyecta a EPSG:32719, valida el tipo de geometría y conserva las
versiones anteriores. Los cálculos usan la versión con la fecha de corte más reciente, no la
última cargada.
**Prioridad:** Must | **Origen:** I1:RF-03 (cuatro tipos de capa), I1:RD-06, I1:RD-18, I2:RF-05

**Criterios de aceptación:**

- **RF-03-AC-1** — **Dado que** un analista tiene un Shapefile .zip con un .prj que declara EPSG:4326, **cuando** lo carga como catastro minero con fuente "INGEMMET" y fecha de corte 15/09/2026, **entonces** el sistema acepta la carga y almacena las geometrías en EPSG:32719.
- **RF-03-AC-2** — **Dado que** un analista carga un GeoJSON en EPSG:4326 con un punto de control de coordenadas conocidas, **cuando** la carga termina, **entonces** el punto almacenado coincide con su transformación a EPSG:32719, calculada con pyproj, con una diferencia de 1 m o menos.
- **RF-03-AC-3** — **Dado que** un analista completa la carga con un archivo válido y la fecha de corte, **cuando** la envía sin fuente, **entonces** el sistema la rechaza indicando que falta la fuente y no crea ninguna versión.
- **RF-03-AC-4** — **Dado que** un analista completa la carga con un archivo válido y la fuente, **cuando** la envía sin fecha de corte, **entonces** el sistema la rechaza indicando que falta la fecha de corte y no crea ninguna versión.
- **RF-03-AC-5** — **Dado que** un analista tiene un Shapefile .zip sin archivo .prj, **cuando** lo carga, **entonces** el sistema lo rechaza indicando que el archivo no declara su sistema de coordenadas.
- **RF-03-AC-6** — **Dado que** un analista tiene un archivo .kml, **cuando** intenta cargarlo como capa de referencia, **entonces** el sistema lo rechaza indicando los formatos aceptados (Shapefile .zip o GeoJSON).
- **RF-03-AC-7** — **Dado que** un analista carga como capa de ríos un archivo con polígonos, **cuando** envía la carga, **entonces** el sistema la rechaza indicando que ese tipo de capa exige líneas.
- **RF-03-AC-8** — **Dado que** un analista carga el catastro minero sin ninguna columna asignada a "código", **cuando** envía la carga, **entonces** el sistema la rechaza indicando el atributo obligatorio que falta.
- **RF-03-AC-9** — **Dado que** un analista carga un catastro minero con una columna "TITULAR", **cuando** la carga termina, **entonces** ni la capa almacenada ni la respuesta de la API contienen el valor de "TITULAR", y entre los atributos de destino disponibles no hay ninguno para el titular.
- **RF-03-AC-10** — **Dado que** el catastro minero tiene una versión con fecha de corte 01/07/2026, **cuando** un analista carga otra con fecha de corte 15/09/2026, **entonces** el historial de la capa lista ambas versiones con su fecha de corte y los cálculos usan la del 15/09/2026.
- **RF-03-AC-11** — **Dado que** el catastro minero tiene una versión con fecha de corte 15/09/2026, **cuando** un analista carga después una con fecha de corte 01/08/2026, **entonces** los cálculos siguen usando la del 15/09/2026.
- **RF-03-AC-12** — **Dado que** la coordinación está autenticada, **cuando** invoca el servicio de carga de capas de la API, **entonces** la API responde 403 y no se crea ninguna versión.

#### RF-04 — Ingesta de alertas de GeoBosques

**Descripción:** Un analista debe poder cargar un archivo de alertas de GeoBosques (polígonos,
Shapefile .zip o GeoJSON) con la misma validación de formato y SRC que RF-03, y asignar las
columnas "código" y "fecha de detección". La ingesta es **acumulativa**:

- agrega las alertas nuevas y conserva las existentes;
- no ingiere dos veces la misma alerta (misma fuente y código);
- descarta las alertas que están completamente fuera del ámbito (RD-01) e informa cuántas;
- marca como "no presente en la última carga", sin borrarlas, las alertas ya ingeridas que no
  vienen en la carga nueva.

De cada alerta registra fuente, código, geometría, fecha de detección y fecha de ingesta. La
fecha de corte de cada carga es informativa (RF-07), y una carga con fecha de corte anterior a la
última también se ingiere. Cada ingesta termina con la agrupación en zonas (RF-05).
**Prioridad:** Must | **Origen:** I1:RF-31 (solo GeoBosques), I2:RF-06 (cada alerta conserva su fuente)

**Criterios de aceptación:**

- **RF-04-AC-1** — **Dado que** un analista carga un archivo de GeoBosques con 120 alertas, 5 de ellas fuera del ámbito, **cuando** la carga termina, **entonces** el sistema ingiere 115 alertas, cada una con fuente "GeoBosques", código, fecha de detección y fecha de ingesta.
- **RF-04-AC-2** — **Dado que** el archivo del criterio anterior tenía 5 alertas fuera del ámbito, **cuando** la carga termina, **entonces** el resumen de la carga indica "5 alertas fuera del ámbito".
- **RF-04-AC-3** — **Dado que** un analista carga un archivo de alertas cuyas geometrías son puntos, **cuando** envía la carga, **entonces** el sistema la rechaza indicando que las alertas deben ser polígonos.
- **RF-04-AC-4** — **Dado que** hay 200 alertas ingeridas y un archivo nuevo trae 150 de ellas y 30 nuevas, **cuando** se carga, **entonces** el sistema tiene 230 alertas, el resumen indica 30 nuevas y 150 ya existentes, y las 50 ausentes quedan marcadas "no presente en la última carga" sin salir de sus zonas.
- **RF-04-AC-5** — **Dado que** la última carga tiene fecha de corte 20/09/2026, **cuando** un analista carga un archivo con fecha de corte 10/09/2026 que contiene 3 alertas no ingeridas, **entonces** el sistema ingiere esas 3 alertas.
- **RF-04-AC-6** — **Dado que** una ingesta terminó, **cuando** se consultan las alertas ingeridas, **entonces** cada una pertenece a exactamente una zona (RF-05).
- **RF-04-AC-7** — **Dado que** la coordinación está autenticada, **cuando** invoca el servicio de carga de alertas de la API, **entonces** la API responde 403 y no se ingiere ninguna alerta.

#### RF-05 — Agrupación en zonas de cambio

**Descripción:** El sistema debe asignar cada alerta ingerida a una zona, midiendo la **distancia
mínima** entre la alerta y la geometría de la zona en EPSG:32719:

1. La alerta es **compatible** con una zona activa si está a ≤ 500 m (PS-01) y su fecha de
   detección difiere en ≤ 90 días (PS-02) de la fecha de detección de la alerta más reciente de
   la zona.
2. Si es compatible con una sola zona activa, se agrega a ella. Si es compatible con varias, se
   agrega a la **más cercana**; si hay empate, a la más antigua (menor fecha de creación). La
   fusión de zonas es Could (RF-28).
3. Si no es compatible con ninguna zona activa, crea una **zona nueva** con código `EA-AAAA-NNN`
   (año de creación y correlativo del año) en estado "nueva". Una alerta cercana a una zona
   **cerrada** no se agrega a ella; la reapertura es Should (RF-20).

La geometría de la zona es la unión de sus alertas. El área se expresa en hectáreas con dos
decimales, calculada en EPSG:32719. Al agregarse una alerta, la zona recalcula su geometría, su
área, su número de alertas y su prioridad (RF-09).
**Prioridad:** Must | **Origen:** I1:RF-32 (sin fusión ni historial del lugar), I1:RF-09, I3:RF-03

**Criterios de aceptación:**

- **RF-05-AC-1** — **Dado que** se ingieren dos alertas a 300 m una de otra con fechas de detección separadas por 10 días, **cuando** se ejecuta la agrupación, **entonces** ambas quedan en la misma zona.
- **RF-05-AC-2** — **Dado que** se ingieren dos alertas a 600 m una de otra con fechas de detección separadas por 10 días, **cuando** se ejecuta la agrupación, **entonces** quedan en zonas distintas.
- **RF-05-AC-3** — **Dado que** una zona activa tiene una alerta y llega otra a 400 m cuya fecha de detección difiere en 120 días, **cuando** se ejecuta la agrupación, **entonces** la alerta nueva crea otra zona.
- **RF-05-AC-4** — **Dado que** dos alertas están exactamente a 500 m una de otra con fechas de detección separadas exactamente por 90 días, **cuando** se ejecuta la agrupación, **entonces** quedan en la misma zona.
- **RF-05-AC-5** — **Dado que** dos alertas poligonales tienen sus centroides a 900 m y sus bordes a 450 m, **cuando** se ejecuta la agrupación, **entonces** quedan en la misma zona.
- **RF-05-AC-6** — **Dado que** una alerta nueva es compatible con la zona EA-2026-010 a 400 m y con la zona EA-2026-015 a 200 m, **cuando** se ejecuta la agrupación, **entonces** la alerta se agrega a EA-2026-015 y ambas zonas siguen existiendo.
- **RF-05-AC-7** — **Dado que** una zona fue descartada, **cuando** se ingiere una alerta a 300 m de ella dentro de la ventana, **entonces** la alerta crea una zona nueva en estado "nueva" y la zona descartada no cambia.
- **RF-05-AC-8** — **Dado que** la última zona creada en 2026 es EA-2026-041, **cuando** se crea una zona nueva en 2026, **entonces** su código es EA-2026-042.
- **RF-05-AC-9** — **Dado que** una zona agrupa dos alertas que no se superponen, de 1.20 ha y 0.80 ha, **cuando** se calcula el área de la zona, **entonces** es "2.00 ha".
- **RF-05-AC-10** — **Dado que** un polígono de referencia está definido en EPSG:4326, **cuando** el sistema calcula su área, **entonces** el resultado coincide, con diferencia de 0.01 ha o menos, con el área del mismo polígono reproyectado a EPSG:32719 y calculada con pyproj y shapely.
- **RF-05-AC-11** — **Dado que** una zona tiene 3 alertas, **cuando** se le agrega una cuarta que amplía su geometría, **entonces** su número de alertas pasa a 4 y su área y su puntaje se recalculan.

#### RF-06 — Mapa con capas

**Descripción:** El sistema debe mostrar un mapa con estas capas activables: límite de la RN
Tambopata, zona de amortiguamiento, ríos, catastro minero, alertas de GeoBosques y zonas de
cambio. Las zonas se colorean por nivel de prioridad, con leyenda. Activar o desactivar una capa
no recarga la página ni recalcula nada. Al seleccionar una zona en el mapa se abre su detalle.
**Prioridad:** Must | **Origen:** I1:RF-01 (seis capas), I3:RF-04, I2:RF-02-AC-2

**Criterios de aceptación:**

- **RF-06-AC-1** — **Dado que** un usuario autenticado solicita la lista de capas del mapa, **cuando** la API responde, **entonces** contiene exactamente: límite de la RN Tambopata, zona de amortiguamiento, ríos, catastro minero, alertas de GeoBosques y zonas de cambio.
- **RF-06-AC-2** — **Dado que** existen dos zonas con geometrías distintas, **cuando** se consulta la capa de zonas en la API, **entonces** cada zona se devuelve con su propia geometría en EPSG:4326, su código y su nivel.
- **RF-06-AC-3** — *(Prueba E2E de interfaz.)* **Dado que** la capa "Catastro minero" está activa, **cuando** el usuario la desactiva, **entonces** sus elementos dejan de mostrarse sin que la página se recargue y las demás capas no cambian.
- **RF-06-AC-4** — *(Prueba E2E de interfaz.)* **Dado que** existen zonas de nivel alto, medio y bajo, **cuando** el usuario activa la capa "Zonas de cambio", **entonces** cada zona se dibuja con el color de su nivel y la leyenda muestra los tres niveles.
- **RF-06-AC-5** — *(Prueba E2E de interfaz.)* **Dado que** la capa de zonas está activa, **cuando** el usuario selecciona la zona EA-2026-014 en el mapa, **entonces** se abre el detalle de EA-2026-014.
- **RF-06-AC-6** — **Dado que** el catastro minero tiene elementos, **cuando** se solicitan los atributos de una concesión a la API, **entonces** la respuesta contiene tipo de derecho, código y estado, y ningún titular.

#### RF-07 — Frescura de las fuentes

**Descripción:** El sistema debe mostrar, para cada capa de referencia y para las alertas de
GeoBosques, su **fecha de corte** (para las alertas, la más reciente entre sus cargas). Si la
última fecha de corte de las alertas tiene más de 30 días (PS-13) respecto de la fecha actual, el
panel de capas y la lista de zonas muestran el aviso "Alertas de GeoBosques posiblemente
desactualizadas (corte dd/mm/aaaa)". La lista indica siempre "Alertas al dd/mm/aaaa". El sistema
nunca presenta datos de una fecha de corte anterior como si fueran actuales. Si nunca se cargó una
capa, se muestra "Sin datos cargados".
**Prioridad:** Must | **Origen:** I2:RF-11, I1:RF-02, I3:RNF-05, I2:RD-03

**Criterios de aceptación:**

- **RF-07-AC-1** — **Dado que** las alertas se cargaron con fechas de corte 10/09/2026 y 20/09/2026, **cuando** un usuario consulta el panel de capas, **entonces** la entrada "Alertas de GeoBosques" muestra "20/09/2026".
- **RF-07-AC-2** — **Dado que** la última fecha de corte de las alertas es el 20/09/2026 y hoy es 04/10/2026 (14 días), **cuando** un usuario consulta la lista de zonas, **entonces** se muestra "Alertas al 20/09/2026" y no se muestra el aviso de desactualización.
- **RF-07-AC-3** — **Dado que** la última fecha de corte de las alertas es el 20/08/2026 y hoy es 04/10/2026 (45 días), **cuando** un usuario consulta la lista de zonas o el panel de capas, **entonces** ambos muestran "Alertas de GeoBosques posiblemente desactualizadas (corte 20/08/2026)".
- **RF-07-AC-4** — **Dado que** nunca se cargó la capa de ríos, **cuando** un usuario consulta el panel de capas, **entonces** la entrada "Ríos" muestra "Sin datos cargados".
- **RF-07-AC-5** — **Dado que** el catastro minero tiene la fecha de corte 01/07/2026, **cuando** un analista carga una versión con fecha de corte 15/09/2026, **entonces** el panel de capas muestra "15/09/2026" para esa capa.

#### RF-08 — Contexto territorial de la zona

**Descripción:** El detalle de cada zona debe informar:

- **Superposiciones** con la RN Tambopata, la ZA y el catastro minero. Para la reserva y la ZA se
  indican nombre y código; para el catastro, **tipo de derecho, código y estado, nunca el
  titular** (RD-04). Junto a cada capa se muestra la fecha de corte de la versión usada (RD-06).
  Si no hay superposiciones, se muestra "No hay superposiciones".
- La **distancia mínima en metros** (entero, EPSG:32719) entre la geometría de la zona y el río
  más cercano, con su nombre si lo tiene. Si la cruza, la distancia es 0 m. Si no hay capa de
  ríos cargada, se muestra "Información no disponible" y no se presenta ninguna distancia.

Las superposiciones son **datos espaciales**, no conclusiones: el sistema no indica si un cambio
es legal o ilegal (RD-02).
**Prioridad:** Must | **Origen:** I1:RF-10 (reducido), I3:RF-05, I2:RF-05 (reformulado sin "legal-administrativo")

**Criterios de aceptación:**

- **RF-08-AC-1** — **Dado que** una zona cruza una concesión minera y la ZA, **cuando** se consulta su contexto, **entonces** el sistema lista la concesión con tipo de derecho "concesión", código y estado, y la ZA con su nombre y código.
- **RF-08-AC-2** — **Dado que** una zona cruza un petitorio minero, **cuando** se consulta su contexto, **entonces** el sistema lista el petitorio con tipo de derecho "petitorio", código y estado, y ningún nombre de titular.
- **RF-08-AC-3** — **Dado que** una zona no cruza ninguna capa de referencia, **cuando** se consulta su contexto, **entonces** el sistema muestra "No hay superposiciones" en lugar de una lista vacía.
- **RF-08-AC-4** — **Dado que** el cruce usa la versión del catastro minero con fecha de corte 15/09/2026, **cuando** se consulta el contexto, **entonces** aparece "Catastro minero, corte 15/09/2026".
- **RF-08-AC-5** — **Dado que** el río más cercano a una zona es el Malinowski a 212.4 m, **cuando** se consulta el contexto, **entonces** se muestra "Río Malinowski: 212 m", y el valor difiere en 1 m o menos del calculado con pyproj y shapely como distancia mínima en EPSG:32719.
- **RF-08-AC-6** — **Dado que** una zona cruza un río, **cuando** se consulta el contexto, **entonces** la distancia al río es "0 m".
- **RF-08-AC-7** — **Dado que** no hay ninguna versión de la capa de ríos, **cuando** se consulta el contexto de una zona, **entonces** se muestra "Información no disponible" y la respuesta de la API no contiene ninguna distancia.
- **RF-08-AC-8** — **Dado que** se consulta el contexto de cualquier zona, **cuando** se revisa la respuesta de la API, **entonces** no contiene ningún campo ni texto que califique el cambio como legal, ilegal o de un tipo de actividad.

#### RF-09 — Priorización explicada

**Descripción:** El sistema debe calcular para cada zona un **puntaje de 0 a 100** como suma
ponderada de 5 factores normalizados de 0 a 1, con los pesos de PS-03. Todas las fechas son
fechas de detección en America/Lima. Las distancias se miden desde la geometría de la zona en
EPSG:32719. La **fecha de referencia** (FR) es la fecha del cálculo y se registra con el puntaje.
La "ventana k" (k = 1…8) es el k-ésimo intervalo de 7 días contado hacia atrás desde FR.

| Factor | Normalización (0 a 1) | Disponible si… |
|---|---|---|
| Ubicación | 1 si alguna parte de la zona está dentro de la reserva; si no, 0.6 si su distancia al límite de la reserva es ≤ 2 km (PS-05); si no, 0.3. | hay capa del límite de la reserva |
| Persistencia y crecimiento | 0.5 × (ventanas con al menos una alerta ÷ 8) + 0.5 × min(crecimiento, 1). Crecimiento = (área actual − área hace 8 semanas) ÷ max(área hace 8 semanas, 1 ha), con mínimo 0. El "área hace 8 semanas" es la de las alertas con fecha de detección anterior a la ventana 8. | siempre (deriva de las alertas) |
| Cercanía a ríos | Según PS-09, con d = distancia al río más cercano. | hay capa de ríos |
| Superficie | Área de la zona ÷ 10 ha (PS-06), con tope 1. | siempre |
| Recencia | Según PS-07, con d = días entre FR y la fecha de detección de la alerta más reciente. | siempre |

**Cálculo.** Aporte de cada factor = peso × factor. Si algún factor **no está disponible**, se
muestra "No disponible" y los aportes de los disponibles se **reescalan**: puntaje = Σ aportes
disponibles × 100 ÷ Σ pesos disponibles. Si ningún factor estuviera disponible, la prioridad sería
"No disponible", sin nivel. El puntaje es esa suma sin redondear, redondeada después al entero
más cercano (0.5 hacia arriba). El nivel se asigna con ese entero según PS-04.

**Explicabilidad.** La lista y el detalle **siempre** muestran los 5 factores. Para cada uno
muestran el aporte en puntos (un decimal, solo para mostrar) o "No disponible", y un texto
explicativo (p. ej., "dentro de la reserva; alertas en 3 de 8 semanas; a 200 m del río
Malinowski").

**Determinismo.** Con los mismos datos de la zona, las mismas versiones de capas y la misma FR,
el resultado es idéntico. El puntaje se recalcula cuando cambia la zona, cuando se carga una
versión de capa que afecta un factor y una vez al día.

Ningún factor ni texto asigna causas (RD-02). La calidad de la evidencia **no** es un factor: se
expresa con marcas de confianza que no cambian el puntaje (RF-13).
**Prioridad:** Must | **Origen:** I1:RF-33 (5 de 7 factores), I3:RF-06, I3:RF-07 ("No disponible", determinismo), RD-03

**Criterios de aceptación:**

- **RF-09-AC-1** — **Dado que** una zona está dentro de la reserva, tuvo alertas en 3 de las 8 ventanas, medía 2.00 ha hace 8 semanas y hoy 3.00 ha, está a 200 m del río y su alerta más reciente es de hace 3 días, **cuando** se calcula su prioridad con PS-03, **entonces** el desglose es ubicación 35.0, persistencia y crecimiento 10.9, cercanía a ríos 15.0, superficie 4.5 y recencia 10.0, y el puntaje es 75, nivel "alta".
- **RF-09-AC-2** — **Dado que** la zona del criterio anterior se calcula sin ninguna versión de la capa de ríos, **cuando** se calcula su prioridad, **entonces** cercanía a ríos muestra "No disponible" y el puntaje es 71 (60.4375 × 100 ÷ 85), nivel "alta".
- **RF-09-AC-3** — **Dado que** tres zonas tienen los demás factores iguales y una está dentro de la reserva, otra en la ZA a 1.5 km del límite y otra a 3 km, **cuando** se calcula su prioridad, **entonces** el factor de ubicación vale 1, 0.6 y 0.3, respectivamente.
- **RF-09-AC-4** — **Dado que** hay zonas a 300 m, 500 m, 1,250 m y 2,000 m del río más cercano, **cuando** se calcula su prioridad, **entonces** el factor de cercanía a ríos vale 1, 1, 0.5 y 0, respectivamente.
- **RF-09-AC-5** — **Dado que** hay zonas con puntajes enteros 70, 69, 40 y 39, **cuando** se asigna el nivel, **entonces** son "alta", "media", "media" y "baja", respectivamente.
- **RF-09-AC-6** — **Dado que** los aportes sin redondear de una zona suman 69.45, **cuando** se calcula su prioridad, **entonces** el puntaje es 69 y el nivel "media".
- **RF-09-AC-7** — **Dado que** los aportes sin redondear de una zona suman 69.5, **cuando** se calcula su prioridad, **entonces** el puntaje es 70 y el nivel "alta".
- **RF-09-AC-8** — **Dado que** una zona se creó hace 3 semanas, tuvo alertas en 3 ventanas, mide 2.00 ha y no tenía alertas hace 8 semanas, **cuando** se calcula su prioridad, **entonces** el factor de persistencia y crecimiento vale 0.6875 (0.5 × 3/8 + 0.5 × 1) y su aporte es 17.2 puntos.
- **RF-09-AC-9** — **Dado que** la alerta más reciente de una zona tiene fecha de detección 7 días antes de FR, **cuando** se calcula su prioridad, **entonces** el factor de recencia vale 1.
- **RF-09-AC-10** — **Dado que** la alerta más reciente de una zona tiene fecha de detección 45 días antes de FR, **cuando** se calcula su prioridad, **entonces** el aporte de recencia es 5.4 puntos ((90 − 45) ÷ 83 × 10).
- **RF-09-AC-11** — **Dado que** una alerta tiene fecha de detección 20 días antes de FR y se ingirió hoy, **cuando** se calcula la prioridad de su zona, **entonces** la recencia se calcula con 20 días (fecha de detección), no con 0 (fecha de ingesta).
- **RF-09-AC-12** — **Dado que** se calcula dos veces la prioridad de la misma zona con los mismos datos, las mismas versiones de capas y la misma FR, **cuando** se comparan los resultados, **entonces** el puntaje, el nivel y el desglose son idénticos.
- **RF-09-AC-13** — **Dado que** se calcula el puntaje de una zona, **cuando** se consulta en la API, **entonces** registra la FR y la versión de pesos usadas.
- **RF-09-AC-14** — **Dado que** se calcula la prioridad de cualquier zona, **cuando** se consulta el desglose en la API, **entonces** contiene exactamente los 5 factores de la tabla, cada uno con su aporte o "No disponible", y ningún factor, etiqueta o texto de causa (p. ej., "minería").
- **RF-09-AC-15** — *(Prueba E2E de interfaz.)* **Dado que** una zona tiene puntaje 75, **cuando** se consulta en la lista y en el detalle, **entonces** en ambos lugares aparecen los 5 factores con sus puntos y el texto explicativo.

#### RF-10 — Lista priorizada de zonas

**Descripción:** El sistema debe mostrar la lista de zonas ordenada por defecto así:

1. puntaje vigente, de mayor a menor;
2. si hay empate, fecha de detección de la alerta más reciente, de la más nueva a la más antigua;
3. si persiste el empate, código ascendente.

Cada fila muestra código, nivel, puntaje vigente (y el calculado si hay ajuste, RF-11), texto del
desglose, marcas (RF-13), estado y área. La lista muestra el conteo de zonas por nivel y por
estado. Se puede filtrar por nivel y por estado y buscar por código. Si ninguna zona cumple el
filtro, se muestra un mensaje de sin resultados.
**Prioridad:** Must | **Origen:** I1:RF-12 (sin sectores ni indicador de novedades), I3:RF-06-AC-4, I3:RF-08-AC-3

**Criterios de aceptación:**

- **RF-10-AC-1** — **Dado que** existen zonas con puntajes vigentes 40, 85 y 72, **cuando** un usuario abre la lista sin cambiar el orden, **entonces** las zonas aparecen en el orden 85, 72, 40.
- **RF-10-AC-2** — **Dado que** dos zonas tienen puntaje 60 y sus alertas más recientes son del 25/09/2026 y del 20/09/2026, **cuando** se muestra la lista, **entonces** la del 25/09/2026 aparece primero.
- **RF-10-AC-3** — **Dado que** EA-2026-021 y EA-2026-017 tienen puntaje 60 y la misma fecha de su alerta más reciente, **cuando** se muestra la lista, **entonces** EA-2026-017 aparece antes que EA-2026-021.
- **RF-10-AC-4** — **Dado que** una zona tiene puntaje calculado 45 y ajustado 80, **cuando** se muestra la lista, **entonces** se ordena por 80 y la fila muestra "80 (ajustado; calculado 45)".
- **RF-10-AC-5** — **Dado que** existen 3 zonas de nivel alto, 5 de nivel medio y 8 de nivel bajo, y 4 de ellas están en "requiere verificación", **cuando** un usuario abre la lista sin filtros, **entonces** los conteos muestran 3, 5 y 8 por nivel y 4 en "requiere verificación".
- **RF-10-AC-6** — **Dado que** existen zonas de varios niveles y estados, **cuando** el usuario filtra por nivel "alta" y estado "en revisión", **entonces** solo aparecen las zonas que cumplen ambos criterios y los conteos reflejan solo esas zonas.
- **RF-10-AC-7** — **Dado que** ninguna zona cumple un filtro, **cuando** el usuario lo aplica, **entonces** la lista aparece vacía con un mensaje de sin resultados y todos los conteos muestran 0.
- **RF-10-AC-8** — **Dado que** existe la zona EA-2026-014, **cuando** el usuario busca "EA-2026-014", **entonces** la lista muestra solo esa zona.
- **RF-10-AC-9** — **Dado que** una zona de nivel medio pasa a nivel alto por un ajuste manual (RF-11), **cuando** se vuelve a consultar la lista, **entonces** la zona aparece en la posición que le corresponde a su puntaje vigente.
- **RF-10-AC-10** — *(Prueba E2E de interfaz.)* **Dado que** la lista contiene zonas de nivel alto, medio y bajo, **cuando** un usuario la consulta, **entonces** cada fila muestra su nivel con el mismo color que usa el mapa (RF-06) y la lista muestra la leyenda de los tres niveles.

#### RF-11 — Ajuste manual de prioridad

**Descripción:** El analista debe poder fijar un **puntaje ajustado** para una zona, con
**justificación obligatoria**, de una de dos formas:

- **Por puntaje:** escribe un valor de 0 a 100.
- **Por nivel:** elige alta, media o baja. Si sube de nivel, el puntaje ajustado es el mínimo del
  nivel elegido (alta = 70, media = 40). Si baja de nivel, es el máximo del nivel elegido
  (media = 69, baja = 39). No se puede elegir el nivel en el que la zona ya está.

El historial registra la forma usada. El sistema conserva y muestra el puntaje calculado y el ajustado. El
nivel y el orden de la lista usan el ajustado. El puntaje calculado se sigue actualizando. El
analista puede quitar el ajuste con una justificación. Cada ajuste y cada retiro quedan en el
historial de la zona, con usuario, fecha y hora, ambos valores y la justificación.
**Prioridad:** Must | **Origen:** I1:RF-34 (por puntaje), I3:RF-08 e I4:RF-06 (por nivel); ver C-08 y C-18 en `diferencias_SRS.md`

**Criterios de aceptación:**

- **RF-11-AC-1** — **Dado que** una zona tiene puntaje calculado 45, **cuando** un analista fija un puntaje ajustado de 80 con la justificación "frente activo junto al límite", **entonces** la zona muestra "80 (ajustado; calculado 45)" y nivel "alta".
- **RF-11-AC-2** — **Dado que** un analista está ajustando la prioridad de una zona, **cuando** confirma sin justificación, **entonces** el sistema rechaza el ajuste indicando que la justificación es obligatoria y el puntaje vigente no cambia.
- **RF-11-AC-3** — **Dado que** un analista está ajustando la prioridad, **cuando** ingresa 120, −5 o "alto", **entonces** el sistema rechaza el valor indicando el rango de 0 a 100.
- **RF-11-AC-4** — **Dado que** una zona tiene puntaje calculado 45 y ajustado 80, **cuando** llegan alertas nuevas y el calculado pasa a 52, **entonces** la zona muestra "80 (ajustado; calculado 52)".
- **RF-11-AC-5** — **Dado que** una zona tiene un ajuste, **cuando** un analista lo quita con una justificación, **entonces** el puntaje vigente vuelve a ser el calculado y el historial conserva el ajuste y su retiro.
- **RF-11-AC-6** — **Dado que** una zona tuvo dos ajustes, **cuando** un usuario consulta su detalle, **entonces** ve ambos con analista, fecha y hora, valores y justificación.
- **RF-11-AC-7** — **Dado que** la coordinación está autenticada, **cuando** intenta ajustar la prioridad de una zona por la API, **entonces** la API responde 403 y el puntaje no cambia.
- **RF-11-AC-8** — **Dado que** una zona tiene puntaje calculado 45 (media), **cuando** un analista elige el nivel "alta" con una justificación, **entonces** el puntaje ajustado es 70, el nivel es "alta" y la zona muestra "70 (ajustado por nivel; calculado 45)".
- **RF-11-AC-9** — **Dado que** una zona tiene puntaje calculado 75 (alta), **cuando** un analista elige el nivel "baja" con una justificación, **entonces** el puntaje ajustado es 39 y el nivel es "baja".
- **RF-11-AC-10** — **Dado que** una zona tiene puntaje calculado 75 (alta), **cuando** un analista elige el nivel "media" con una justificación, **entonces** el puntaje ajustado es 69 y el nivel es "media".
- **RF-11-AC-11** — **Dado que** una zona tiene puntaje vigente 45 (media), **cuando** un analista elige el nivel "media", **entonces** el sistema rechaza el ajuste indicando que la zona ya está en ese nivel y el puntaje vigente no cambia.
- **RF-11-AC-12** — **Dado que** un analista ajusta por nivel, **cuando** envía por la API el nivel "urgente", **entonces** el sistema lo rechaza indicando los niveles válidos (alta, media, baja).
- **RF-11-AC-13** — **Dado que** un analista ajustó una zona por nivel, **cuando** se consulta el historial de ajustes, **entonces** la entrada indica la forma "por nivel", el nivel elegido, ambos puntajes y la justificación.

#### RF-12 — Estados de revisión e historial

**Descripción:** El sistema debe registrar el estado de cada zona y guardar el historial de cambios
con usuario, fecha y hora, y comentario o motivo. Toda zona nueva inicia como **nueva**. Solo el
analista cambia estados y las zonas no se eliminan. Las transiciones permitidas son solo estas:

| Desde | Hacia | Condición |
|---|---|---|
| Nueva | En revisión | Comentario opcional |
| Nueva | Descartada | Motivo obligatorio |
| En revisión | Revisada | Comentario obligatorio |
| En revisión | Requiere verificación | Comentario obligatorio |
| En revisión | Descartada | Motivo obligatorio |
| Requiere verificación | Revisada | Comentario obligatorio (p. ej., resultado de campo) |
| Requiere verificación | En revisión | Motivo obligatorio |
| Revisada / Descartada | En revisión | Reapertura manual; motivo obligatorio; conserva el ajuste de prioridad |

"Requiere verificación" es el estado para la evidencia insuficiente o contradictoria (el
"incierto" de I3). **"Revisada" significa que el analista terminó la revisión, no que el cambio,
su causa o su legalidad estén confirmados** (RD-11). No existe un estado "confirmada".
**Prioridad:** Must | **Origen:** I1:RF-11 (sin verificada en campo ni fusionada), I2:RF-08, I2:RF-09, I3:RF-09, I3:RD-02, I4:RF-07, I4:RF-11

**Criterios de aceptación:**

- **RF-12-AC-1** — **Dado que** el sistema crea una zona a partir de alertas, **cuando** se guarda, **entonces** su estado es "nueva".
- **RF-12-AC-2** — **Dado que** existe una zona, **cuando** se intenta asignarle por la API un estado fuera de la tabla (p. ej., "confirmada"), **entonces** el sistema rechaza la operación y el estado no cambia.
- **RF-12-AC-3** — **Dado que** una zona está en "nueva", **cuando** un analista la pasa a "en revisión" sin comentario, **entonces** el sistema acepta la transición.
- **RF-12-AC-4** — **Dado que** una zona está en "nueva", **cuando** un analista la pasa a "descartada" con el motivo "sombra de nube en la alerta", **entonces** el sistema acepta la transición y el historial registra el motivo.
- **RF-12-AC-5** — **Dado que** una zona está en "nueva", **cuando** un analista intenta pasarla a "descartada" sin motivo, **entonces** el sistema rechaza la operación y la zona sigue en "nueva".
- **RF-12-AC-6** — **Dado que** una zona está en "en revisión", **cuando** un analista intenta pasarla a "revisada" sin comentario, **entonces** el sistema rechaza la operación y la zona sigue en "en revisión".
- **RF-12-AC-7** — **Dado que** una zona está en "en revisión", **cuando** un analista la pasa a "requiere verificación" con el comentario "posibles pozas junto al afluente", **entonces** el sistema acepta la transición y el historial muestra el comentario.
- **RF-12-AC-8** — **Dado que** una zona está en "requiere verificación", **cuando** un analista la pasa a "revisada" con el comentario "verificado en campo: claro agrícola", **entonces** el sistema acepta la transición.
- **RF-12-AC-9** — **Dado que** una zona está en "requiere verificación", **cuando** un analista la pasa a "en revisión" con el motivo "se canceló la salida a campo", **entonces** el sistema acepta la transición.
- **RF-12-AC-10** — **Dado que** una zona está en "nueva", **cuando** se intenta pasarla a "revisada", **entonces** el sistema rechaza la transición por no estar en la tabla.
- **RF-12-AC-11** — **Dado que** una zona está en "descartada", **cuando** se intenta pasarla a "requiere verificación", **entonces** el sistema rechaza la transición por no estar en la tabla.
- **RF-12-AC-12** — **Dado que** una zona está en "descartada", **cuando** un analista la reabre a "en revisión" con un motivo, **entonces** el sistema acepta la transición.
- **RF-12-AC-13** — **Dado que** una zona está en "revisada", **cuando** un analista intenta reabrirla sin motivo, **entonces** el sistema rechaza la operación y la zona sigue en "revisada".
- **RF-12-AC-14** — **Dado que** una zona descartada tiene un puntaje ajustado de 30, **cuando** un analista la reabre a "en revisión" con un motivo, **entonces** la zona conserva el puntaje ajustado de 30.
- **RF-12-AC-15** — **Dado que** un analista cambió una zona de "en revisión" a "revisada", **cuando** cualquier usuario consulta su historial, **entonces** ve una entrada con estado anterior, estado nuevo, nombre del analista, fecha y hora y comentario.
- **RF-12-AC-16** — **Dado que** la coordinación está autenticada, **cuando** intenta cambiar el estado de una zona por la API, **entonces** la API responde 403 y el estado no cambia.
- **RF-12-AC-17** — **Dado que** existe una zona, **cuando** un usuario de cualquier rol envía una solicitud de borrado a la API, **entonces** la API no expone la operación (404 o 405) y la zona sigue existiendo.
- **RF-12-AC-18** — *(Prueba E2E de interfaz.)* **Dado que** la coordinación está en el detalle de una zona, **cuando** revisa las acciones disponibles, **entonces** no ve opciones para cambiar el estado, ajustar la prioridad ni registrar marcas.
- **RF-12-AC-19** — **Dado que** el sistema crea la zona EA-2026-042 a partir de una alerta, **cuando** se consulta su historial, **entonces** la primera entrada es "zona creada", con usuario "Sistema", fecha y hora, y el código de la alerta que la originó.
- **RF-12-AC-20** — **Dado que** una zona tuvo, en este orden, un cambio de estado, un ajuste de prioridad y una marca del analista, **cuando** cualquier usuario consulta su historial, **entonces** ve las tres acciones en una sola lista cronológica, cada una con tipo de acción, usuario, fecha y hora.

#### RF-13 — Marcas de confianza

**Descripción:** El sistema debe asociar a cada zona las marcas de confianza que correspondan,
**sin ocultarla ni cambiar su puntaje**. Las marcas se muestran en el mapa, en la lista y en el
detalle.

- **Marcas automáticas** (se recalculan cuando cambian la zona o las capas):
  - **área pequeña**: la zona mide menos de 1 ha (PS-11), cerca del límite de detección de las
    fuentes (RD-07);
  - **posible dinámica fluvial**: la zona está a ≤ 100 m (PS-10) de un río.
- **Marcas del analista**: texto libre, p. ej., una hipótesis como "posible actividad minera".
  Llevan nombre y fecha, se rotulan "Marca del analista" y se distinguen visualmente de las
  automáticas. Se retiran con motivo y el retiro queda en el historial.

El sistema **nunca genera ni sugiere** hipótesis de causa (RD-02).
**Prioridad:** Must | **Origen:** I1:RF-36 (dos marcas automáticas sin imágenes), I2:RF-03 (nivel de confianza), I3:RD-02

**Criterios de aceptación:**

- **RF-13-AC-1** — **Dado que** una zona mide 0.80 ha, **cuando** se evalúan sus marcas, **entonces** tiene la marca "área pequeña".
- **RF-13-AC-2** — **Dado que** una zona mide 1.00 ha, **cuando** se evalúan sus marcas, **entonces** no tiene la marca "área pequeña".
- **RF-13-AC-3** — **Dado que** una zona está a 80 m del río Tambopata, **cuando** se evalúan sus marcas, **entonces** tiene la marca "posible dinámica fluvial".
- **RF-13-AC-4** — **Dado que** una zona está a 150 m del río más cercano, **cuando** se evalúan sus marcas, **entonces** no tiene la marca "posible dinámica fluvial".
- **RF-13-AC-5** — **Dado que** una zona de puntaje 75 tiene dos marcas automáticas, **cuando** un usuario consulta la lista filtrada por nivel "alta", **entonces** la zona aparece con sus marcas y su puntaje sigue siendo 75.
- **RF-13-AC-6** — **Dado que** un analista registra la marca "posible actividad minera" en una zona, **cuando** se consultan sus marcas en la API, **entonces** la marca tiene tipo "marca del analista", el nombre del analista y la fecha.
- **RF-13-AC-7** — **Dado que** una zona tiene una marca del analista, **cuando** un analista la retira con el motivo "pozas descartadas en campo", **entonces** la marca deja de estar activa y el historial conserva la marca, el retiro y el motivo.
- **RF-13-AC-8** — **Dado que** una zona tiene una marca del analista, **cuando** un analista intenta retirarla sin motivo, **entonces** el sistema rechaza el retiro y la marca sigue activa.
- **RF-13-AC-9** — **Dado que** el sistema evalúa las marcas de cualquier zona, **cuando** se consultan sus marcas automáticas en la API, **entonces** solo son de los dos tipos definidos y ninguna contiene una hipótesis o causa.
- **RF-13-AC-10** — **Dado que** la coordinación está autenticada, **cuando** intenta registrar o retirar una marca del analista por la API, **entonces** la API responde 403 y las marcas no cambian.
- **RF-13-AC-11** — *(Prueba E2E de interfaz.)* **Dado que** una zona tiene una marca automática y una marca del analista, **cuando** un usuario revisa su detalle, **entonces** ambas se distinguen visualmente y la del analista lleva el rótulo "Marca del analista".

#### RF-14 — Comparación de dos periodos

**Descripción:** Un usuario debe poder seleccionar **dos periodos** y comparar las alertas de cada
zona en ellos.

- **Validación de periodos:**
  - cada periodo tiene inicio ≤ fin, y un periodo de un solo día es válido;
  - los dos periodos deben ser distintos y no superponerse;
  - el sistema los ordena cronológicamente: A es el anterior y B el posterior.
- **Resultado por zona** (zonas con al menos una alerta cuya fecha de detección cae en A o en B):
  - número de alertas en A y en B;
  - área en hectáreas de la unión de esas alertas en A y en B;
  - diferencia de área B − A;
  - indicador "solo en A", "solo en B" o "en ambos";
  - nivel, puntaje y estado de la zona en el momento del análisis.

  Las zonas se ordenan por puntaje vigente, como en RF-10.
- **Sin resultados:** si no hay alertas en ninguno de los dos periodos, el sistema informa "No se
  identificaron zonas con alertas en los periodos analizados".
- **Limitaciones conocidas:**
  - Si la última fecha de corte de las alertas es anterior al fin de B, el sistema registra la
    limitación "Las alertas están cargadas hasta dd/mm/aaaa; el periodo B termina después" y el
    análisis queda en estado **"incompleto"**, no "concluido".
  - Si no hay ninguna carga de alertas, el análisis queda **"sin datos"** y no muestra resultados.
- **Almacenamiento:** cada análisis se almacena automáticamente, sin acción adicional, con:
  - fecha y hora, y usuario;
  - los periodos;
  - las fuentes usadas con su fecha de corte;
  - las limitaciones;
  - el estado (concluido, incompleto o sin datos);
  - el resultado por zona.

  Un análisis almacenado es **inmutable**: los cambios posteriores en las zonas no lo alteran.

La comparación visual de imágenes satelitales de ambos periodos es Should (RF-18).
**Prioridad:** Must | **Origen:** I3:RF-02, I3:RF-03, I3:RF-10, I2:RF-01 (periodos A y B), I1:RF-15 (trazabilidad), I1:RF-07 (en versión de datos)

**Criterios de aceptación:**

- **RF-14-AC-1** — **Dado que** un usuario está autenticado, **cuando** selecciona los periodos 01/06/2026–30/06/2026 y 01/08/2026–31/08/2026 y ejecuta la comparación, **entonces** el sistema la ejecuta con A = junio y B = agosto.
- **RF-14-AC-2** — **Dado que** un usuario selecciona primero 01/08/2026–31/08/2026 y después 01/06/2026–30/06/2026, **cuando** ejecuta la comparación, **entonces** el sistema asigna A = junio y B = agosto.
- **RF-14-AC-3** — **Dado que** un periodo tiene inicio 10/08/2026 y fin 01/08/2026, **cuando** el usuario intenta ejecutar la comparación, **entonces** el sistema no la ejecuta e informa que la fecha de inicio es posterior a la de fin.
- **RF-14-AC-4** — **Dado que** los periodos 01/06/2026–15/07/2026 y 01/07/2026–31/07/2026 se superponen, **cuando** el usuario intenta ejecutar la comparación, **entonces** el sistema no la ejecuta e informa que los periodos no deben superponerse.
- **RF-14-AC-5** — **Dado que** ambos periodos son 01/06/2026–30/06/2026, **cuando** el usuario intenta ejecutar la comparación, **entonces** el sistema no la ejecuta e informa que los periodos deben ser distintos.
- **RF-14-AC-6** — **Dado que** los periodos son 15/06/2026–15/06/2026 y 15/08/2026–15/08/2026, **cuando** el usuario ejecuta la comparación, **entonces** el sistema la acepta.
- **RF-14-AC-7** — **Dado que** la zona EA-2026-014 tiene 2 alertas en A (1.00 ha en total) y 3 en B (2.50 ha en total), **cuando** se ejecuta la comparación, **entonces** su fila muestra 2 y 3 alertas, 1.00 ha y 2.50 ha, diferencia +1.50 ha e indicador "en ambos".
- **RF-14-AC-8** — **Dado que** la zona EA-2026-020 solo tiene alertas en B, **cuando** se ejecuta la comparación, **entonces** su fila muestra 0 alertas en A e indicador "solo en B".
- **RF-14-AC-9** — **Dado que** una zona solo tiene alertas fuera de A y de B, **cuando** se ejecuta la comparación, **entonces** la zona no aparece en el resultado.
- **RF-14-AC-10** — **Dado que** la última fecha de corte de las alertas es posterior al fin de B y no hay alertas con fecha de detección en A ni en B, **cuando** se ejecuta la comparación, **entonces** el sistema informa "No se identificaron zonas con alertas en los periodos analizados" y almacena el análisis con estado "concluido" y 0 zonas.
- **RF-14-AC-11** — **Dado que** la última fecha de corte de las alertas es 20/08/2026 y B termina el 31/08/2026, **cuando** se ejecuta la comparación, **entonces** el análisis queda "incompleto" con la limitación "Las alertas están cargadas hasta 20/08/2026; el periodo B termina después", y la interfaz no lo presenta como concluido.
- **RF-14-AC-12** — **Dado que** nunca se cargaron alertas, **cuando** se ejecuta una comparación, **entonces** el análisis queda "sin datos" con la limitación "No hay alertas cargadas" y no muestra resultados por zona.
- **RF-14-AC-13** — **Dado que** una comparación terminó, **cuando** se consulta el análisis almacenado, **entonces** contiene fecha y hora, usuario, ambos periodos, las fuentes con su fecha de corte, las limitaciones, el estado y el resultado por zona, sin que el usuario haya pedido guardarlo.
- **RF-14-AC-14** — **Dado que** un análisis almacenado registró EA-2026-014 con puntaje 62 y estado "nueva", **cuando** después la zona cambia a puntaje 80 y estado "revisada", **entonces** el análisis almacenado sigue mostrando 62 y "nueva".
- **RF-14-AC-15** — **Dado que** la coordinación está autenticada, **cuando** ejecuta una comparación por la API, **entonces** la API la acepta y la almacena con su usuario.

#### RF-15 — Consulta de análisis anteriores

**Descripción:** Cualquier usuario debe poder consultar la lista de análisis almacenados (RF-14),
del más reciente al más antiguo, con fecha, usuario, periodos y estado. También debe poder abrir
el detalle de uno con todo lo que se almacenó. Los análisis no se editan ni se eliminan.
**Prioridad:** Must | **Origen:** I3:RF-11, I3:RNF-02, I2:RF-07 (guardar comparaciones)

**Criterios de aceptación:**

- **RF-15-AC-1** — **Dado que** existen 3 análisis almacenados, **cuando** un usuario consulta los análisis anteriores, **entonces** ve los 3, del más reciente al más antiguo, cada uno con fecha, usuario, periodos y estado.
- **RF-15-AC-2** — **Dado que** un usuario está en la lista de análisis, **cuando** abre uno, **entonces** ve sus periodos, sus fuentes con fecha de corte, sus limitaciones, su estado y el resultado por zona.
- **RF-15-AC-3** — **Dado que** existe un análisis almacenado, **cuando** se envía una solicitud de modificación o borrado a la API, **entonces** la API no expone la operación (404 o 405) y el análisis no cambia.
- **RF-15-AC-4** — **Dado que** no existe ningún análisis almacenado, **cuando** un usuario consulta los análisis anteriores, **entonces** ve el mensaje "Aún no hay análisis almacenados".

#### RF-16 — Exportación de la lista de zonas (CSV)

**Descripción:** El analista debe poder exportar a CSV (UTF-8 con BOM, separador coma) la lista
de zonas filtrada, en el orden de la lista (RF-10), con estas 10 columnas: código, nivel, puntaje
calculado, puntaje ajustado (vacío si no hay), estado, fecha de creación, fecha del último cambio
de estado, área (ha), número de alertas y marcas (separadas por ";"). Si el filtro no devuelve
zonas, se genera el archivo solo con los encabezados y se muestra un aviso.
**Prioridad:** Must | **Origen:** I1:RF-19 (CSV), I2:RF-07

**Criterios de aceptación:**

- **RF-16-AC-1** — **Dado que** la lista muestra 5 zonas con un filtro aplicado, **cuando** el analista la exporta a CSV, **entonces** el archivo contiene exactamente esas 5 zonas, en el mismo orden.
- **RF-16-AC-2** — **Dado que** se exporta la lista, **cuando** se leen los encabezados, **entonces** son exactamente las 10 columnas de la descripción, en español y en ese orden.
- **RF-16-AC-3** — **Dado que** una zona está en "en revisión" y tiene la marca "posible dinámica fluvial", **cuando** se exporta la lista, **entonces** el archivo empieza con los bytes EF BB BF y, decodificado como UTF-8, contiene literalmente "en revisión" y "posible dinámica fluvial".
- **RF-16-AC-4** — **Dado que** una zona no tiene ajuste manual, **cuando** se exporta la lista, **entonces** su columna "puntaje ajustado" está vacía y "puntaje calculado" tiene su valor.
- **RF-16-AC-5** — **Dado que** el filtro no devuelve zonas, **cuando** el analista exporta la lista, **entonces** se genera el archivo solo con los encabezados y se muestra el aviso "La exportación no contiene zonas".
- **RF-16-AC-6** — **Dado que** la coordinación está autenticada, **cuando** solicita la exportación por la API, **entonces** la API responde 403 y no entrega el archivo.

#### RF-17 — Exportación de zonas (GeoJSON)

**Descripción:** El analista debe poder exportar a GeoJSON (RFC 7946, EPSG:4326) las zonas de la
lista filtrada, con los atributos código, nivel, puntaje vigente, estado, área (ha) y fecha de la
alerta más reciente, **sin titulares** (RD-04). Si el filtro no devuelve zonas, se genera una
colección vacía y se muestra un aviso.
**Prioridad:** Must | **Origen:** I1:RF-18 (adaptado a zonas y a EPSG:4326), I2:RF-07

**Criterios de aceptación:**

- **RF-17-AC-1** — **Dado que** la lista filtrada muestra 6 zonas, **cuando** el analista las exporta a GeoJSON y el archivo se lee con `ogrinfo`, **entonces** se lee sin errores y tiene 6 elementos en EPSG:4326 con los 6 atributos de la descripción.
- **RF-17-AC-2** — **Dado que** una zona exportada mide 3.50 ha, **cuando** se lee su geometría con GDAL y shapely, se reproyecta a EPSG:32719 y se calcula su área, **entonces** el resultado redondeado a dos decimales es 3.50.
- **RF-17-AC-3** — **Dado que** una zona exportada cruza una concesión minera, **cuando** se inspecciona el GeoJSON, **entonces** no contiene ningún atributo ni texto con el nombre del titular.
- **RF-17-AC-4** — **Dado que** el filtro no devuelve zonas, **cuando** el analista exporta a GeoJSON, **entonces** el archivo es una FeatureCollection con 0 elementos y se muestra el aviso "La exportación no contiene zonas".
- **RF-17-AC-5** — **Dado que** no hay una sesión iniciada, **cuando** se solicita la exportación, **entonces** el sistema responde 401 y no entrega el archivo.
- **RF-17-AC-6** — **Dado que** la coordinación está autenticada, **cuando** solicita la exportación por la API, **entonces** la API responde 403.

---

#### RF-18 — Comparación visual de imágenes de dos periodos

**Descripción:** Para una zona y los periodos de una comparación (RF-14), el sistema debe mostrar
lado a lado, con zoom y desplazamiento sincronizados, una imagen Sentinel-2 de cada periodo
obtenida vía GEE. Para cada periodo elige la de **menor nubosidad dentro del área de la zona** y
muestra su fecha, su fuente y su porcentaje de nubosidad. La ejecución es asíncrona, con estados
en cola, en curso, terminado y fallido, y con reintento. Si alguna imagen supera el 20 % de
nubosidad, la zona recibe la marca automática "nubosidad". Solo el analista la ejecuta.
**Prioridad:** Should | **Origen:** I1:RF-07, I1:RF-08, I1:RF-29, I2:RF-01-AC-3 (vista lado a lado), I4:RF-02, RD-09

**Criterios de aceptación:**

- **RF-18-AC-1** — **Dado que** el periodo B tiene imágenes con 35 %, 12 % y 18 % de nubosidad en el área de la zona, **cuando** se ejecuta la comparación visual, **entonces** se usa la de 12 % y se muestran su fecha, su fuente y "12 %".
- **RF-18-AC-2** — **Dado que** GEE responde con un error (simulado en la prueba), **cuando** termina la ejecución, **entonces** la comparación visual queda "fallida" con un mensaje en español y el analista puede reintentarla.
- **RF-18-AC-3** — **Dado que** la imagen elegida para A tiene 25 % de nubosidad en el área, **cuando** termina la comparación, **entonces** la zona tiene la marca "nubosidad 25 % > 20 %" y su puntaje no cambia.
- **RF-18-AC-4** — *(Prueba E2E de interfaz.)* **Dado que** se muestran lado a lado las imágenes de A y B de una zona, **cuando** el analista hace zoom o desplaza una de ellas, **entonces** la otra muestra la misma extensión geográfica y la misma escala.

#### RF-19 — Ingesta de alertas RADD y confirmación multifuente

**Descripción:** El sistema debe sincronizar alertas RADD desde GEE una vez por semana (lunes 06:00,
hora de Lima) y a pedido del analista, con las mismas reglas de RF-04 (sin duplicados, descarte
fuera del ámbito, conservar alertas previas si falla). Una zona con alertas de dos fuentes que se
superponen tiene **confirmación multifuente**: se muestra en el detalle, y cada alerta conserva
su fuente, sin un veredicto combinado. Al incorporarse, los analistas pueden añadir el factor
"confirmación multifuente" mediante una versión de pesos (RF-21).
**Prioridad:** Should | **Origen:** I1:RF-31, I1:RF-32, I1:RF-33, I2:RF-06

**Criterios de aceptación:**

- **RF-19-AC-1** — **Dado que** una alerta RADD con código "R-889120" ya fue ingerida, **cuando** una sincronización posterior la vuelve a recibir, **entonces** no se crea una alerta duplicada.
- **RF-19-AC-2** — **Dado que** una alerta RADD se superpone con una de GeoBosques, **cuando** se agrupan, **entonces** quedan en la misma zona, la zona muestra "confirmada por GeoBosques y RADD" y el detalle lista cada alerta con su fuente.
- **RF-19-AC-3** — **Dado que** la sincronización falla, **cuando** termina el proceso, **entonces** queda "fallida", las alertas previas siguen intactas y RF-07 sigue mostrando la fecha de la última sincronización exitosa.

#### RF-20 — Reapertura automática de zonas cerradas

**Descripción:** Una zona revisada o descartada debe volver automáticamente a "nueva", con el
indicador "reabierta" y su motivo, en dos casos:

- recibe una alerta a ≤ 500 m con fecha de detección posterior a su último cambio de estado;
- su área crece ≥ 20 % respecto de la que tenía en ese cambio.

La reapertura retira el ajuste de prioridad, que queda en el historial, y la registra el usuario
"Sistema". No se envía ningún aviso externo. Con este RF, la regla 3 de RF-05 cambia: una alerta
cercana a una zona cerrada se agrega a ella.
**Prioridad:** Should | **Origen:** I1:RF-37, I1:RF-32 (regla de zonas cerradas)

**Criterios de aceptación:**

- **RF-20-AC-1** — **Dado que** una zona se descartó el 01/09/2026, **cuando** recibe a 300 m una alerta con fecha de detección 20/09/2026, **entonces** pasa a "nueva" con el indicador "reabierta" y el motivo "1 alerta nueva (GeoBosques, 20/09/2026)".
- **RF-20-AC-2** — **Dado que** una zona descartada tenía puntaje calculado 35 y ajustado 20, **cuando** se reabre automáticamente, **entonces** su puntaje vigente es 35 y el historial conserva el ajuste con la indicación "ajuste retirado por reapertura".
- **RF-20-AC-3** — **Dado que** una zona de 10.00 ha se marcó "revisada", **cuando** recibe alertas anteriores a ese cambio que llevan su área a 12.00 ha, **entonces** pasa a "nueva" con el motivo "área creció 20 %".

#### RF-21 — Configuración de pesos de priorización

**Descripción:** Los analistas deben poder cambiar los pesos de RF-09: enteros de 0 a 100 que suman
100, con motivo obligatorio. Cada cambio crea una versión numerada, con quién, cuándo y por qué, y
recalcula los puntajes. Todos pueden consultar las versiones. **El sistema nunca reajusta los
pesos automáticamente** (RD-03). La coordinación recibe 403 al guardar pesos.
**Prioridad:** Should | **Origen:** I1:RF-35, I2:RF-04-AC-4 (umbrales configurables)

**Criterios de aceptación:**

- **RF-21-AC-1** — **Dado que** la versión vigente es la 1, **cuando** un analista guarda los pesos 40, 20, 15, 15, 10 con el motivo "calibración de agosto", **entonces** se crea la versión 2 y los puntajes se recalculan con ella.
- **RF-21-AC-2** — **Dado que** un analista guarda pesos que suman 105, **cuando** confirma, **entonces** el sistema rechaza el cambio y la versión vigente no cambia.
- **RF-21-AC-3** — **Dado que** pasaron 30 días sin que ningún analista cambie los pesos, **cuando** se consulta el historial de pesos, **entonces** no existe ninguna versión creada por el sistema.

#### RF-22 — Exportación para campo (GeoPackage y KML)

**Descripción:** El analista debe poder exportar las zonas de la lista filtrada en GeoPackage y KML
(EPSG:4326), con los atributos de RF-17 más el último comentario del historial de estados, sin
titulares, para cargarlas en QField o Avenza y usarlas en campo sin conexión. Es la alternativa
acordada al modo offline (C-09).
**Prioridad:** Should | **Origen:** I1:RF-40, I2:RNF-02 (necesidad de campo)

**Criterios de aceptación:**

- **RF-22-AC-1** — **Dado que** la lista filtrada por "requiere verificación" muestra 6 zonas, **cuando** el analista exporta a GeoPackage y el archivo se lee con `ogrinfo`, **entonces** tiene 6 elementos en EPSG:4326 con los atributos de la descripción.
- **RF-22-AC-2** — **Dado que** se exportan las mismas 6 zonas a KML, **cuando** el archivo se lee con `ogrinfo`, **entonces** se lee sin errores y tiene 6 elementos.
- **RF-22-AC-3** — *(Prueba de aceptación manual.)* **Dado que** se generaron el GeoPackage y el KML, **cuando** se cargan en QField y en Avenza en un celular sin conexión, **entonces** las zonas se ven en su ubicación y se pueden consultar sus atributos.

#### RF-23 — Ficha de zona en PDF

**Descripción:** El analista debe poder generar una ficha PDF de una zona con estos contenidos:

- código, mapa con escala y fecha, nivel, puntaje y desglose;
- marcas, contexto territorial con fechas de corte, estado e historial;
- la leyenda "Documento técnico de apoyo: no determina causas ni es una alerta oficial".

La ficha incluye su huella SHA-256, que se registra. "Verificar ficha" recalcula la huella de un
archivo y responde "coincide" o "no coincide". No hay ciclo de versiones ni revisión previa.
**Prioridad:** Should | **Origen:** I1:RF-17 (simplificado), I2:RF-07 ("reporte"), I1:RD-16

**Criterios de aceptación:**

- **RF-23-AC-1** — **Dado que** un analista genera la ficha de EA-2026-014, **cuando** se extrae su texto, **entonces** contiene el código, el puntaje, los 5 factores del desglose y la leyenda de la descripción.
- **RF-23-AC-2** — **Dado que** se generó una ficha, **cuando** se verifica el mismo archivo, **entonces** el sistema responde "coincide"; y si se modifica un byte, responde "no coincide".

#### RF-24 — Bitácora de auditoría

**Descripción:** El sistema debe registrar en una bitácora **de solo inserción** estos eventos:
cargas e ingestas, cambios de estado, ajustes de prioridad, marcas del analista, exportaciones,
comparaciones y gestión de usuarios, con usuario, fecha y hora y detalle. Ninguna función permite
editar ni borrar registros. El usuario de base de datos de la aplicación no tiene UPDATE ni DELETE
sobre esa tabla. Ambos roles pueden consultarla.
**Prioridad:** Should | **Origen:** I1:RF-27, I1:RNF-04 (sin registro de consultas)

**Criterios de aceptación:**

- **RF-24-AC-1** — **Dado que** un analista exportó la lista a CSV, **cuando** se consulta la bitácora, **entonces** hay un registro con el formato, el número de zonas, el usuario y la fecha y hora.
- **RF-24-AC-2** — **Dado que** existe un registro en la bitácora, **cuando** se intenta modificarlo o borrarlo por la API o con el usuario de base de datos de la aplicación, **entonces** la operación no existe o es rechazada y el registro no cambia.

#### RF-25 — Segundo factor TOTP y bloqueo por intentos

**Descripción:** El inicio de sesión debe exigir, además de la contraseña, un código TOTP
obligatorio para todos los roles, que se enrola en el primer ingreso. Tras 5 intentos fallidos
consecutivos, la cuenta se bloquea 15 minutos. La coordinación puede restablecer el segundo factor
de otro usuario.
**Prioridad:** Should | **Origen:** I1:RF-28, I1:RNF-03

**Criterios de aceptación:**

- **RF-25-AC-1** — **Dado que** un usuario tiene TOTP enrolado, **cuando** inicia sesión con contraseña correcta y sin código válido, **entonces** el inicio de sesión se rechaza.
- **RF-25-AC-2** — **Dado que** un usuario falló la contraseña 4 veces seguidas, **cuando** la falla por quinta vez, **entonces** la cuenta queda bloqueada 15 minutos, incluso con la contraseña correcta.

#### RF-26 — Zonas manuales (detección propia)

**Descripción:** El analista debe poder crear una zona dibujando un polígono dentro del ámbito, con
un comentario obligatorio. La zona se marca con origen "detección propia" y se distingue de las
zonas de alertas oficiales (RD-06). Participa en la agrupación y en la priorización. En las zonas
sin alertas, la recencia se mide desde la fecha de creación.
**Prioridad:** Should | **Origen:** I1:RF-13, I1:RD-05

**Criterios de aceptación:**

- **RF-26-AC-1** — **Dado que** un analista dibuja un polígono de 3.00 ha dentro de la reserva con un comentario, **cuando** guarda la zona, **entonces** la zona se crea en "nueva" con origen "detección propia" y área 3.00 ha.
- **RF-26-AC-2** — **Dado que** un analista dibuja un polígono completamente fuera del ámbito, **cuando** intenta guardarlo, **entonces** el sistema lo rechaza indicando que está fuera del ámbito.

---

#### RF-27 — Candidatos semiautomáticos por NDVI

**Descripción:** En la comparación visual (RF-18), el sistema puede proponer polígonos candidatos
donde ΔNDVI ≤ −0.20 (valor inicial, por calibrar) con un área de al menos 0.5 ha. Ningún candidato
se usa sin que el analista lo acepte, edite o descarte, y los candidatos no tienen atributo de causa
(RD-02). Solo NDVI: NDFI queda fuera.
**Prioridad:** Could | **Origen:** I1:RF-23, I2:RF-04 (reformulado sin clasificación)

**Criterios de aceptación:**

- **RF-27-AC-1** — **Dado que** se generaron candidatos, **cuando** se consultan en la API, **entonces** ninguno tiene un atributo de causa o tipo de cambio.
- **RF-27-AC-2** — **Dado que** hay un candidato no aceptado, **cuando** se calcula el área de cambio de la zona, **entonces** el candidato no se cuenta.

#### RF-28 — Fusión de zonas e historial del lugar

**Descripción:** Si una alerta es compatible con dos o más zonas activas, esas zonas se fusionan en
la más antigua. Las demás quedan en el estado final "fusionada en EA-…", con su historial
conservado. Cada zona muestra además su historial del lugar: alertas o zonas a ≤ 500 m en los
últimos 3 años que no forman parte de ella. Con este RF, la regla 2 de RF-05 cambia.
**Prioridad:** Could | **Origen:** I1:RF-32, I1:RF-11

**Criterios de aceptación:**

- **RF-28-AC-1** — **Dado que** EA-2026-010 (creada el 01/07/2026) y EA-2026-015 (creada el 10/08/2026) son compatibles con una alerta nueva, **cuando** se agrupa, **entonces** las alertas de EA-2026-015 pasan a EA-2026-010 y EA-2026-015 queda "fusionada en EA-2026-010".
- **RF-28-AC-2** — **Dado que** una zona está "fusionada en EA-2026-010", **cuando** un analista intenta cambiar su estado, **entonces** el sistema lo rechaza indicando la zona en la que se fusionó.

#### RF-29 — Zonas nuevas desde la última revisión del usuario

**Descripción:** Cada usuario puede marcar "Revisión completada". Desde entonces, la lista indica
"nueva desde tu última revisión", con su motivo, en las zonas que:

- se crearon;
- se reabrieron;
- recibieron alertas nuevas;
- pasaron a nivel alta.

La lista permite filtrar por ese indicador. Es un **indicador** dentro de la interfaz: no se envía
ningún mensaje fuera del sistema (RD-05).
**Prioridad:** Could | **Origen:** I1:RF-04, I4:RF-09 (aviso de alta prioridad)

**Criterios de aceptación:**

- **RF-29-AC-1** — **Dado que** un usuario marcó "Revisión completada" el 01/10/2026, **cuando** el 03/10/2026 se crea una zona y él consulta la lista, **entonces** la zona tiene el indicador "nueva desde tu última revisión".
- **RF-29-AC-2** — **Dado que** un analista marcó "Revisión completada" el 01/10/2026 y una zona de nivel "media" pasa a nivel "alta" el 02/10/2026, **cuando** él consulta la lista el 03/10/2026, **entonces** la zona tiene el indicador "nueva desde tu última revisión" con el motivo "pasó a nivel alta".
- **RF-29-AC-3** — **Dado que** el sistema usa un servidor de correo simulado, **cuando** una zona pasa a nivel "alta", **entonces** el servidor de correo simulado no recibe ningún mensaje.

#### RF-30 — Sectores de trabajo

**Descripción:** La coordinación puede definir sectores (nombre, cuenca y polígono) y desactivarlos.
A cada zona se le asignan los sectores activos que intersectan su geometría. La lista se puede
filtrar por sector.
**Prioridad:** Could | **Origen:** I1:RF-22, I1:RF-12

**Criterios de aceptación:**

- **RF-30-AC-1** — **Dado que** una zona intersecta los sectores "Malinowski" e "Interoceánica", **cuando** el usuario filtra por cualquiera de los dos, **entonces** la zona aparece en ambos resultados.

#### RF-31 — Notas de discrepancia

**Descripción:** El analista puede registrar en una zona una nota de discrepancia entre fuentes o
respecto de un dato oficial. La nota se muestra separada del dato oficial, que nunca se modifica
(RD-06), con autor, fecha y, si existe, el documento que la respalda.
**Prioridad:** Could | **Origen:** I1:RF-14, I2:RF-06

**Criterios de aceptación:**

- **RF-31-AC-1** — **Dado que** un analista registra una nota de discrepancia sobre la superposición con una concesión, **cuando** se consulta el contexto, **entonces** el dato del catastro aparece sin cambios y la nota aparece aparte, con autor y fecha.

#### RF-32 — Formatos y vistas adicionales

**Descripción:** Mejoras opcionales:

- exportación de la lista a XLSX;
- exportación de la comparación visual como imagen PNG;
- comparación visual con deslizador (*slider*) además de la vista lado a lado.

**Prioridad:** Could | **Origen:** I1:RF-19, I2:RF-01-AC-3, I2:RF-07. La exportación a Shapefile pasó a RF-37 (Should).

**Criterios de aceptación:**

- **RF-32-AC-1** — **Dado que** la lista muestra 5 zonas, **cuando** el analista la exporta a XLSX y se lee con openpyxl, **entonces** la hoja contiene esas 5 zonas, en el mismo orden y con las columnas de RF-16.
- **RF-32-AC-2** — *(Retirado: trasladado a RF-37-AC-1. El ID no se reutiliza.)*

#### RF-33 — Reportes de campo

**Descripción:** El analista puede registrar un reporte de campo con fecha, ubicación, texto,
fotos e informante opcional con seudónimo. El sistema elimina los metadatos EXIF de las fotos y no
tiene campos para DNI ni teléfonos (RD-12).
**Prioridad:** Could | **Origen:** I1:RF-21, I1:RD-09

**Criterios de aceptación:**

- **RF-33-AC-1** — **Dado que** un analista adjunta una foto con coordenadas GPS en sus metadatos EXIF, **cuando** se descarga la foto almacenada, **entonces** no contiene metadatos EXIF.

---

*Los RF-34 a RF-39 se agregaron al integrar el SRS del Integrante 4 (C-18 a C-30 en
`diferencias_SRS.md`). Siguen la regla de numeración: los RF nuevos empiezan en RF-34 y ningún RF
existente se renumera.*

#### RF-34 — Observaciones de la zona

**Descripción:** El analista debe poder registrar en una zona una observación de texto libre, sin
cambiar su estado. Cada observación guarda autor, fecha y hora, es visible para ambos roles y
aparece en el historial (RF-12). Las observaciones no se editan ni se eliminan. La coordinación
recibe 403 al registrar observaciones.
**Prioridad:** Should | **Origen:** I4:RF-05, I3:RF-09-AC-3

**Criterios de aceptación:**

- **RF-34-AC-1** — **Dado que** una zona está en "en revisión", **cuando** un analista registra la observación "revisar con imagen de octubre", **entonces** la observación queda asociada a la zona con su nombre, fecha y hora, y el estado sigue siendo "en revisión".
- **RF-34-AC-2** — **Dado que** un analista registró una observación en una zona, **cuando** la coordinación consulta el detalle de esa zona, **entonces** ve la observación con su autor y fecha.
- **RF-34-AC-3** — **Dado que** un analista intenta registrar una observación vacía, **cuando** confirma, **entonces** el sistema la rechaza indicando que el texto es obligatorio.
- **RF-34-AC-4** — **Dado que** la coordinación está autenticada, **cuando** intenta registrar una observación por la API, **entonces** la API responde 403 y no se crea la observación.
- **RF-34-AC-5** — **Dado que** existe una observación, **cuando** se envía una solicitud de modificación o borrado a la API, **entonces** la API no expone la operación (404 o 405) y la observación no cambia.

#### RF-35 — Capa de comunidades nativas

**Descripción:** Se agrega el tipo de capa de referencia **"Comunidades nativas"**: polígono, con
atributos obligatorios código y nombre, y ningún otro atributo almacenado. Al implementarse este
RF:

- la tabla de RF-03 incluye el nuevo tipo;
- el mapa de RF-06 incluye la capa;
- el contexto de RF-08 lista las comunidades superpuestas con nombre, código y fecha de corte.

La fuente oficial está pendiente (TA-05). Como RF-06-AC-1 fija "exactamente" seis capas, al
implementar este RF se retira RF-06-AC-1 y se agrega un criterio nuevo con siete capas; el
criterio existente no se reescribe.
**Prioridad:** Should | **Origen:** I4:RF-04-AC-1, I1:RF-01, I1:RF-10-AC-2

**Criterios de aceptación:**

- **RF-35-AC-1** — **Dado que** un analista carga un GeoJSON de comunidades nativas con fuente y fecha de corte y asigna código y nombre, **cuando** la carga termina, **entonces** la capa queda disponible con esos dos atributos y ninguna otra columna del archivo se almacena.
- **RF-35-AC-2** — **Dado que** una zona cruza el territorio de una comunidad nativa, **cuando** se consulta su contexto, **entonces** el sistema lista la comunidad con su nombre, su código y la fecha de corte de la capa.
- **RF-35-AC-3** — **Dado que** existe una versión de la capa de comunidades nativas, **cuando** un usuario solicita la lista de capas del mapa, **entonces** "Comunidades nativas" aparece como capa activable.
- **RF-35-AC-4** — **Dado que** la coordinación está autenticada, **cuando** intenta cargar la capa de comunidades por la API, **entonces** la API responde 403 y no se crea ninguna versión.

#### RF-36 — Filtros y orden adicionales de la lista

**Descripción:** Además de los filtros de nivel y estado, la lista de zonas (RF-10) admite filtrar
por:

- rango de la fecha de detección de la alerta más reciente;
- área mínima y máxima (ha);
- ubicación: "dentro de la reserva" o "en la ZA".

También admite ordenar por puntaje vigente, fecha de la alerta más reciente, área o estado, de
forma ascendente o descendente. El orden por defecto sigue siendo el de RF-10. Los filtros se
combinan entre sí y con los de RF-10, y los conteos reflejan el resultado.
**Prioridad:** Should | **Origen:** I4:RF-08, I1:RF-12-AC-8

**Criterios de aceptación:**

- **RF-36-AC-1** — **Dado que** existen zonas cuya alerta más reciente es del 05/08/2026, del 20/09/2026 y del 02/10/2026, **cuando** el usuario filtra por el rango 01/09/2026–30/09/2026, **entonces** solo aparece la zona del 20/09/2026.
- **RF-36-AC-2** — **Dado que** existen zonas de 0.80 ha, 2.00 ha y 12.50 ha, **cuando** el usuario filtra por área mínima 1 ha y máxima 10 ha, **entonces** solo aparece la de 2.00 ha.
- **RF-36-AC-3** — **Dado que** una zona está dentro de la reserva y otra solo en la ZA, **cuando** el usuario filtra por "dentro de la reserva", **entonces** solo aparece la primera.
- **RF-36-AC-4** — **Dado que** existen zonas de 3.00 ha, 0.50 ha y 7.25 ha, **cuando** el usuario ordena por área ascendente, **entonces** aparecen en el orden 0.50, 3.00, 7.25.
- **RF-36-AC-5** — **Dado que** el usuario ordenó por área, **cuando** elige "restablecer orden", **entonces** la lista vuelve al orden por defecto de RF-10.
- **RF-36-AC-6** — **Dado que** el usuario indica un área mínima mayor que la máxima, **cuando** aplica el filtro, **entonces** el sistema lo rechaza indicando que el mínimo no puede superar al máximo.

#### RF-37 — Exportación de zonas a Shapefile

**Descripción:** El analista debe poder exportar las zonas de la lista filtrada a Shapefile
comprimido (.zip) en EPSG:32719 (RD-10). Usa los atributos de RF-17, con nombres de campo de 10
caracteres como máximo, y nunca incluye titulares (RD-04). La coordinación recibe 403.
**Prioridad:** Should | **Origen:** I4:RF-13-AC-2, I1:RF-18, I2:RF-07, RF-32-AC-2 (retirado)

**Criterios de aceptación:**

- **RF-37-AC-1** — **Dado que** se exportan zonas a Shapefile, **cuando** se lee el .zip con `ogrinfo`, **entonces** contiene .shp, .shx, .dbf y .prj y reporta EPSG:32719.
- **RF-37-AC-2** — **Dado que** la lista filtrada muestra 6 zonas, **cuando** el analista las exporta a Shapefile, **entonces** el archivo tiene 6 elementos con los atributos de RF-17 y ninguno con el nombre del titular.
- **RF-37-AC-3** — **Dado que** la coordinación está autenticada, **cuando** solicita la exportación a Shapefile por la API, **entonces** la API responde 403.

#### RF-38 — Selección manual de zonas para exportar

**Descripción:** En la lista, el analista puede marcar zonas y exportar solo las seleccionadas en
los formatos de RF-16, RF-17 y RF-37. Si no hay selección, se exporta la lista filtrada.
**Prioridad:** Could | **Origen:** I4:RF-13

**Criterios de aceptación:**

- **RF-38-AC-1** — **Dado que** la lista filtrada muestra 8 zonas y el analista seleccionó 2, **cuando** exporta a GeoJSON "solo seleccionadas", **entonces** el archivo tiene exactamente esas 2 zonas.
- **RF-38-AC-2** — **Dado que** el analista no seleccionó ninguna zona, **cuando** exporta, **entonces** el archivo contiene todas las zonas de la lista filtrada.

#### RF-39 — Responsable de la zona

**Descripción:** Una zona activa puede tener un **analista responsable**. Un analista puede
asignarse una zona o liberarla, y la coordinación puede asignar o reasignar el responsable. Es la
única acción de escritura que la coordinación hace sobre una zona. La asignación **no cambia el
estado** de la zona (RF-12) y queda en el historial. La lista se puede filtrar por responsable.
**Prioridad:** Could | **Origen:** I4:RF-11, I4:RF-12

**Criterios de aceptación:**

- **RF-39-AC-1** — **Dado que** una zona en "nueva" no tiene responsable, **cuando** un analista se la asigna, **entonces** la zona tiene a ese analista como responsable, su estado sigue en "nueva" y el historial registra la asignación.
- **RF-39-AC-2** — **Dado que** una zona tiene responsable, **cuando** la coordinación la reasigna a otro analista, **entonces** el responsable cambia y el historial registra ambos nombres, quién reasignó y la fecha.
- **RF-39-AC-3** — **Dado que** se intenta asignar una zona a una cuenta con rol coordinación, **cuando** se confirma, **entonces** el sistema lo rechaza indicando que el responsable debe ser analista SIG.

---

#### Convención de IDs y línea base congelada (equipo v1.0)

- **Por qué se renumeró:** los IDs de los cuatro SRS individuales no se podían conservar tal
  cual, porque eran incompatibles entre sí:
  - el mismo número designaba requerimientos distintos (p. ej., RF-01 era "mapa con capas" en
    I1, "zona y periodos" en I2, "autenticación" en I3 y "consulta integrada" en I4);
  - un SRS no tenía IDs de criterios;
  - otro tenía huecos por RF retirados.

  Para que los IDs sean **consistentes**, el equipo los renumeró **una sola vez** al consolidar
  y los congeló en esta línea base. Desde aquí rigen las reglas de inmutabilidad de abajo, y el
  origen de cada requerimiento se conserva en su campo **Origen** (`I1:RF-33`, `I3:RF-07`, etc.).
- **Línea base:** este documento es la **línea base del equipo** y queda congelado en la v1.0. Los
  IDs de los SRS individuales **no** se usan en artefactos de equipo. Su correspondencia completa
  con los IDs de equipo (individual → equipo, incluidos los descartados) está en
  `diferencias_SRS.md`, sección 8.
- **Requerimientos funcionales:** RF-01 a RF-39. Los Must son RF-01 a RF-17; los Should, RF-18 a
  RF-26 y RF-34 a RF-37; los Could, RF-27 a RF-33, RF-38 y RF-39. Los RF-34 a RF-39 se agregaron al
  integrar el SRS del Integrante 4, antes de ratificar la línea base. Un RF que se retire conserva
  su número, sin criterios, y ese número **no se reutiliza**. Los RF nuevos empiezan en RF-40.
  Cambiar la prioridad de un RF no cambia su número.
- **Criterios retirados:** RF-32-AC-2 (trasladado a RF-37-AC-1).
- **Criterios:** `RF-XX-AC-Y`, consecutivos desde AC-1 en cada RF y **inmutables**. Un criterio
  eliminado conserva su ID sin reutilizarlo, y uno nuevo toma el siguiente número libre de su RF.
- **Trazabilidad:**
  - cada endpoint de `openapi.yaml` (S04-A2) referencia los IDs `RF-XX-AC-Y` que implementa;
  - cada prueba automatizada se nombra con su ID, cambiando los guiones por guiones bajos
    (`RF-09-AC-1` → `test_RF_09_AC_1`) (S09-A1);
  - los criterios marcados *(Prueba E2E de interfaz.)* se automatizan en el navegador, y los
    marcados *(Prueba de aceptación manual.)* no son pruebas unitarias de la API.
- **Cambios:** todo cambio posterior a esta línea base se registra en `diferencias_SRS.md` (o en
  el registro de cambios que lo suceda) con su motivo y la aprobación del equipo.

### 3.2 Requerimientos no funcionales

| ID | Requerimiento | Categoría | Verificación | Prioridad | Origen |
|---|---|---|---|---|---|
| RNF-01 | Todas las funciones y datos requieren autenticación. Ningún contenido, incluidos los archivos exportados, es accesible de forma anónima. | Seguridad | Prueba: toda ruta de la API sin sesión responde 401. | Must | I1:RNF-01, I3:RNF-04 |
| RNF-02 | El control de acceso se basa en los dos roles y en la matriz de la sección 2.3. Toda acción no permitida se rechaza **en el servidor** con 403, no solo se oculta en la interfaz. | Seguridad | Prueba: matriz rol × acción; cada acción no permitida responde 403 aunque se invoque directamente en la API. | Must | I1:RNF-02, I2:RF-10 |
| RNF-03 | Toda comunicación usa HTTPS (TLS 1.2 o superior). Las contraseñas tienen al menos 12 caracteres y se almacenan con bcrypt o Argon2. Nunca se guardan ni se registran en texto plano. | Seguridad | Inspección de la configuración TLS y de la tabla de usuarios; prueba de que el valor almacenado no es la contraseña. | Must | I1:RNF-03 (sin TOTP) |
| RNF-04 | Desde que el usuario solicita una carga, una ingesta o una comparación, el sistema muestra un resultado, un estado de procesamiento o un mensaje de error en 60 s o menos (PS-14). | Rendimiento | Prueba con un archivo de 1,000 alertas y una comparación sobre 300 zonas. | Must | I3:RNF-03, I1:RF-29 |
| RNF-05 | Con una conexión limitada a 1 Mbps y la caché vacía, la lista de zonas, el detalle de una zona y el detalle de un análisis almacenado (RF-15) cargan en 5 s o menos con **500 zonas activas** y **20 usuarios concurrentes** consultando. | Rendimiento | Prueba con limitación de red en el navegador + prueba de carga con 20 usuarios virtuales. | Should | I1:RNF-08, I1:RNF-06, I4:RNF-01 |
| RNF-06 | Las funciones Must se ejecutan desde la interfaz web sin escribir código, comandos ni consultas geoespaciales. La interfaz, los mensajes, las exportaciones y la documentación están en español. | Usabilidad | Demostración del flujo completo por una persona sin programación; inspección del idioma. | Must | I3:RNF-01, I1:RNF-14, I2:§2.3 |
| RNF-07 | Todo resultado (puntaje, contexto, comparación) permite consultar las fuentes y fechas de corte, los periodos, la fecha de referencia y las limitaciones con que se obtuvo. | Trazabilidad | Prueba: cada respuesta de RF-08, RF-09 y RF-14 incluye esos campos. | Must | I3:RNF-02, I1:RF-15, I2:RF-07-AC-3 |
| RNF-08 | Ante una fuente externa no disponible, incompleta o desactualizada, el sistema conserva los datos previos, sigue operando con ellos, muestra la situación y nunca presenta un análisis como concluido si la evidencia es insuficiente. | Robustez | Prueba: RF-07-AC-3, RF-14-AC-11 y RF-14-AC-12; en Should, RF-19-AC-3. | Must | I3:RNF-05, I2:RNF-01, I2:RF-11, I1:RF-31 |
| RNF-09 | No se requieren licencias de pago, y el costo mensual de infraestructura (VPS y respaldos) no supera USD 25. | Costo | Inspección de licencias de las dependencias y del plan de hosting. | Must | I1:RNF-11 |
| RNF-10 | El sistema se despliega con un solo comando (Docker Compose) e incluye un manual en español de despliegue, carga de capas e ingesta de alertas. | Mantenibilidad | Demostración: despliegue desde cero siguiendo solo el manual. | Must | I1:RNF-12 |
| RNF-11 | La base de datos se respalda automáticamente cada día en una ubicación distinta del servidor principal, y se pierden como máximo 24 h de datos. | Confiabilidad | Inspección de la política; demostración de una restauración. | Should | I1:RNF-10 |
| RNF-12 | El acceso a las fuentes de alertas e imágenes está detrás de una interfaz común, de modo que agregar una fuente (RADD, GLAD) no modifica la agrupación ni la priorización. | Extensibilidad | Inspección del diseño. | Should | I1:RNF-15 |
| RNF-13 | La interfaz es usable en pantallas desde 1366 px en las dos últimas versiones de Chrome y Firefox. La consulta de la lista y del detalle es usable desde 360 px. | Portabilidad | Prueba en ambos anchos y navegadores. | Could | I1:RNF-09 |
| RNF-14 | Tras una capacitación de 2 h o menos, una persona del perfil analista SIG que no programa completa sin ayuda este guion: consultar la lista priorizada y el desglose de una zona, cambiar su estado, ajustar su prioridad con justificación, ejecutar una comparación de periodos y exportar la lista a CSV. | Usabilidad (aprendizaje) | Prueba de usabilidad con al menos una persona ajena al equipo; se mide el tiempo y si completó cada tarea sin ayuda. | Should | I4:RNF-02 |
| RNF-15 | El mapa se puede ver a escalas entre 1:10,000 y 1:50,000 con barra de escala visible. A esas escalas, las zonas se distinguen de las capas de referencia superpuestas por estilos declarados en la leyenda. En RF-18, cada imagen se rotula con su periodo y su fecha. | Usabilidad (legibilidad) | Prueba E2E a 1:10,000 y 1:50,000; revisión por una persona del perfil. | Should | I4:RNF-03 |

### 3.3 Requerimientos de dominio

| ID | Requerimiento | Prioridad | Origen | Relacionado con |
|---|---|---|---|---|
| RD-01 | El ámbito es la **RN Tambopata y su zona de amortiguamiento**, según los límites oficiales del SERNANP. Lo que está completamente fuera se descarta o se rechaza. El límite se carga como dato (RF-03), no como constante en el código. | Must | I1:RD-14, I3:RD-05, base | RF-03, RF-04, RF-26 |
| RD-02 | El sistema **no determina ni etiqueta causas** de los cambios (p. ej., minería) y **no establece su legalidad**. Las hipótesis solo las registra el analista como "Marca del analista" y nunca se generan automáticamente. | Must | I1:RD-17, I3:RD-03, base; rechaza I2:RF-03, I2:RF-04 | RF-08, RF-09, RF-13, RF-27 |
| RD-03 | La prioridad es una **recomendación** que no sustituye el criterio profesional. El sistema **nunca reajusta pesos ni umbrales automáticamente**. | Must | I3:RD-04, I1:RF-35 | RF-09, RF-11, RF-21 |
| RD-04 | Nunca se muestra, exporta ni imprime el **nombre del titular** de un derecho minero; solo tipo de derecho, código y estado. El titular ni siquiera se importa. | Must | I1:RD-18 | RF-03, RF-06, RF-08, RF-17 |
| RD-05 | La jefatura de la reserva es la autoridad. EcoAlert **no emite alertas oficiales ni envía información a terceros**. Las notificaciones externas están fuera de alcance; los avisos dentro de la interfaz están permitidos. | Must | I1:RD-19, I3:§1.2, I2:RF-11 | RF-07, RF-20 |
| RD-06 | Los datos de fuentes oficiales (GeoBosques, INGEMMET, SERNANP) **nunca se modifican**. Todo cruce indica la fecha de corte de la versión usada, para no presentar como vigentes derechos extinguidos. Las detecciones propias se distinguen de las alertas oficiales. | Must | I1:RD-04, I1:RD-05, I1:RD-06 | RF-03, RF-08, RF-26, RF-31 |
| RD-07 | La detección está limitada por la resolución de las fuentes: unos 10 m en Sentinel-2 y 30 m en Landsat, con un límite práctico de 0.5 a 1 ha. Las zonas menores de 1 ha llevan una marca. | Must | I2:RD-01, I1:RD-07 | RF-13 |
| RD-08 | Las fuentes entregan datos con un **desfase de 1 a 4 semanas** respecto del evento. Por eso los cálculos usan la fecha de detección, no la de ingesta, y se muestra la frescura de los datos. | Must | I2:RD-03 | RF-04, RF-07, RF-09 |
| RD-09 | Las comparaciones deben considerar la **comparabilidad temporal, la nubosidad, las sombras y la estacionalidad**; la práctica de referencia es comparar el mismo mes del año anterior. Las limitaciones relevantes se registran y se muestran, y un resultado con evidencia insuficiente **no se presenta como concluido**. | Must | I3:RD-01, I3:RD-02, I2:RNF-04, I1:RD-08 | RF-13, RF-14, RF-18 |
| RD-10 | El almacenamiento y los cálculos de área y distancia usan **EPSG:32719**. Las exportaciones GeoJSON, GeoPackage y KML y la API del mapa usan **EPSG:4326**, y el Shapefile usa EPSG:32719. | Must | I1:RD-01 (ajustado) | RF-03, RF-05, RF-08, RF-17, RF-22, RF-32 |
| RD-11 | "Revisada" indica que el analista terminó la revisión. **No** significa que el cambio, su causa o su legalidad estén confirmados. | Must | I3:RF-09 | RF-12 |
| RD-12 | Si el sistema llega a tratar datos personales (RF-33), aplica la Ley N.º 29733: minimización, seudónimos, eliminación de metadatos de fotos y nunca nombres de titulares. | Could | I1:RD-09 | RF-33 |
| RD-13 | El uso de GEE, RADD, GeoBosques, INGEMMET y demás fuentes respeta sus términos de uso. Las imágenes Planet/NICFI no se redistribuyen y no se usan. | Must | I1:RD-12 | RF-04, RF-18, RF-19 |
