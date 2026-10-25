# EcoAlert Tambopata — Diferencias y acuerdos de diseño

**Versión:** 1.1 · **Fecha:** 25/10/2026  
**Proyecto:** Equipo 6 — Análisis, diseño y construcción de software  
**Alcance:** contrato OpenAPI, diagrama de clases y diagrama de componentes.  
**Fuente de verdad:** `SRS\_equipo.md` v1.0, especialmente RF-01 a RF-17 (*Must*).

## 1\. Integrantes y artefactos comparados

|Sigla|Integrante|Contrato API|Diagrama de clases|Diagrama de componentes|
|-|-|-|-|-|
|MAA|**Miguel**|`MAA\_openapi.yaml`|`MAA\_diagrama\_clases.puml`|`MAA\_diagrama\_componentes.puml`|
|AGGS|**Anthony**|`AGGS\_openapi.yaml`|`AGGS\_diagrama\_clases.puml`|`AGGS\_diagrama\_componentes.puml`|
|DMV|**Daniel**|`DMV\_openapi.yaml`|`DMV\_diagrama\_clases.puml`|`DMV\_diagrama\_componentes.puml`|
|EDSM|**Eduardo**|`EDSM\_openapi.yaml`|`EDSM\_diagrama\_clases.puml`|`EDSM\_diagrama\_componentes.puml`|

**Método:** se compararon los cuatro entregables individuales por artefacto, identificando elementos compartidos, diferencias y decisiones de consolidación. Las decisiones documentadas son las **adoptadas en los archivos consolidados de trabajo**; su aprobación formal por todos los integrantes no se presume. No se interpreta una mayor cantidad de endpoints o clases como mayor calidad por sí sola.

**Límite de verificación:** los cuatro entregables individuales (`MAA_*`, `AGGS_*`, `DMV_*`, `EDSM_*`) **no están en este repositorio**; solo se versionan los SRS individuales (`S03_A1/insumos/`) y los artefactos consolidados. Por eso las cifras de las secciones 2 y 3.1 (operaciones, clases y schemas de cada integrante) provienen de la comparación original y **no pudieron volver a contrastarse** con los archivos fuente. Las cifras de los artefactos consolidados sí se verifican con pruebas versionadas (`backend/tests`).

## 2\. Aportaciones de cada integrante

|Integrante|API REST|Modelo de clases|Arquitectura de componentes|
|-|-|-|-|
|**Miguel (MAA)**|40 operaciones; rutas y campos en español, convenciones explícitas de nomenclatura y trazabilidad `x-acceptance-criteria`; delimita el núcleo *Must*.|Modelo de dominio detallado: capas y elementos geográficos especializados, contexto territorial, factores y pesos, eventos específicos, fuentes y limitaciones de comparaciones.|Vista C4 detallada: SPA, FastAPI, Caddy, tareas programadas, PostGIS, volumen de archivos, respaldos externos, GitHub/CI y descarga manual de fuentes oficiales.|
|**Anthony (AGGS)**|29 operaciones; contrato conciso para el MVP; recursos REST en inglés, sesiones revocables y manejo explícito de eventos e historial.|Modelo compacto de 21 clases: usuario, carga, alerta, zona, capas, prioridad, ajustes, marcas, historial y comparación; útil para evitar complejidad innecesaria.|Vista de contenedores sencilla: frontend, backend modular, PostGIS y fuentes oficiales sin integración automática; GEE identificado como ampliación futura.|
|**Daniel (DMV)**|37 operaciones y 62 schemas; delimitación de RF-01 a RF-17, trazabilidad explícita de criterios de aceptación y soporte E2E, control de roles, versiones y procesamiento de cargas.|Modelo detallado de 38 declaraciones de clases/enumeraciones: sesión, contexto territorial, tipos geográficos, cálculo de prioridad, ajuste, eventos y resultados de análisis.|SPA, Nginx, API FastAPI, worker Python y PostgreSQL/PostGIS como cola de trabajos; fuentes descargadas manualmente y GEE fuera del MVP.|
|**Eduardo (EDSM)**|55 operaciones; cobertura más amplia, con endpoints para capacidades *Should/Could* además del núcleo; contempla consultas y operaciones adicionales de zonas, fuentes y trabajos.|Modelo de 40 clases/enumeraciones; incluye sesión, especialización de capas, marcas automáticas/manuales y extensiones como observaciones, parámetros y responsable de zona.|Worker asíncrono y Redis como broker; backend modular, PostGIS, fuentes externas y GEE para funciones futuras.|

**Consenso transversal:** SPA React 19/TypeScript, API Python 3.12/FastAPI, PostgreSQL 17/PostGIS, dos roles sin herencia, zonas construidas a partir de alertas, prioridad explicable, historial, comparación de periodos y exportación. El SRS exige además mantener las fuentes y sus fechas, no inferir causas ni legalidad, y no exponer titulares mineros.

## 3\. Artefacto 1 — Contrato OpenAPI

### 3.1 Consensos y diferencias

Las cuatro propuestas contemplan autenticación, usuarios, capas, carga y consulta de alertas, zonas, prioridad, estados, marcas, historial, comparaciones y exportaciones. Difieren en idioma de rutas, métodos HTTP, recursos intermedios, códigos de respuesta y alcance opcional. El número de operaciones individuales fue: **Miguel 40; Anthony 29; Daniel 37; Eduardo 55**.

### 3.2 Conflictos y resolución

|ID|Conflicto entre propuestas|Resolución en `openapi\_equipo.yaml`|Motivo|
|-|-|-|-|
|API-01|Rutas en inglés (Anthony, Eduardo) y español (Miguel, Daniel)|**Rutas en español**, sustantivos plurales y `/api/v1`|Consistencia con la interfaz y el contrato consolidado.|
|API-02|Diferentes métodos y códigos para cerrar sesión|`DELETE /auth/sesion` → **204**|Revocación de sesión sin cuerpo de respuesta.|
|API-03|Cambio de contraseña con `PATCH`, `PUT` o `POST`|`PUT /auth/password` → **204**|Una operación uniforme y documentable.|
|API-04|Actualización de usuario con `PUT` o `PATCH`|`PATCH /usuarios/{usuarioId}` (se mantiene; para `PUT` ver API-13)|Modificación parcial; usuarios no se eliminan físicamente.|
|API-05|Carga directa `multipart` vs recurso previo de archivo|`POST /archivos` y referencia al archivo cargado|Unifica la validación y reutilización de archivos en las ingestas.|
|API-06|Carga de capas mediante recurso genérico o versión explícita|`POST /capas-referencia/{tipoCapa}/versiones`|Conserva versiones y fechas de corte conforme a RF-03.|
|API-07|Ingesta síncrona `201` vs asíncrona `202`|`POST /cargas-alertas` → **202**; consulta de trabajo|Evita bloquear HTTP durante el procesamiento espacial.|
|API-08|Cambio de estado con `PATCH` vs creación de transición|`POST /zonas/{codigo}/cambios-estado` → **201**|La transición deja un registro histórico.|
|API-09|Retiro de ajustes por evento, operación específica o actualización|`PATCH` del ajuste con justificación|Mantiene registro y evita borrado físico.|
|API-10|Retiro de marcas con diferentes verbos y rutas|`PATCH` de la marca con justificación|Mantiene trazabilidad del retiro.|
|API-11|Comparación como análisis o comparación; posible procesamiento diferido|`POST /analisis` → **201**|Crea un resultado inmutable según RF-14 y RF-15.|
|API-12|Exportación en rutas separadas o una ruta con formato|`GET /exportaciones/zonas` con formato CSV/GeoJSON|Reutiliza filtros y mantiene ambos formatos *Must*.|
|API-13|La actividad exige POST, GET y PUT o DELETE; el contrato 1.1.0 solo ofrecía `PATCH` para actualizar usuarios y prohibía DELETE (RF-02-AC-7)|Se agrega `PUT /usuarios/{usuarioId}` (contrato **1.2.0**, `reemplazarUsuario`): reemplazo completo de `nombre_completo`, `rol` y `activo`, sin cambiar el correo. `PATCH` se mantiene y no se agrega `DELETE`|Cumple la rúbrica sin borrar cuentas y reutiliza las mismas validaciones, regla de última coordinación (RF-02-AC-8) y transacción. **Es una propuesta adoptada para cumplir la actividad; no se afirma que todos los integrantes la hayan aprobado.** No cambia ningún criterio de aceptación.|

**Base de consolidación:** se partió del contrato de **Daniel (DMV)** por su cobertura y trazabilidad del MVP, incorporando criterios de consistencia y simplificación identificados en las otras propuestas. El resultado de la consolidación contenía **37 operaciones**; con API-13 (contrato 1.2.0) son **38**. Mantiene **157 IDs únicos** en `x-acceptance-criteria` y 9 en `x-e2e-support` (166 criterios *Must* en total). `backend/tests/test_contrato.py` comprueba que el contrato es válido OpenAPI 3.0, que sus 38 operaciones incluyen `PUT` y no `DELETE` de usuarios, que los 166 IDs coinciden con los del SRS, que sus 62 schemas coinciden con las 62 clases del UML (nombres y atributos) y que las rutas del backend están contenidas en el contrato. Es una verificación estática de consistencia; la ejecución del API se prueba aparte con la misma suite (15 operaciones implementadas).

**Alcance:** RF-01 a RF-17 son obligatorios; las funcionalidades *Should* y *Could* no se incorporan solo por aparecer en un contrato individual. El comportamiento del API debe respetar **401** sin autenticación y **403** cuando el rol no está autorizado.

## 4\. Artefacto 2 — Diagrama de clases

### 4.1 Consenso

Los cuatro modelos incluyen, con nombres y grados de detalle distintos, los conceptos de **usuario, capa y versión de capa, carga de alertas, alerta, zona, cálculo y factores de prioridad, ajuste manual, marca, historial, periodo, comparación y resultado por zona**. Coinciden también en que una zona agrupa alertas, posee seguimiento y se utiliza para comparaciones históricas.

### 4.2 Diferencias y conflictos resueltos

|ID|Diferencia / aportaciones|Resolución de diseño|Justificación|
|-|-|-|-|
|CLS-01|Nombres distintos: `ZonaCambio`/`ZonaDeCambio`, `PuntajePrioridad`/`CalculoPrioridad`, etc.|Nombres y propiedades alineados con los **schemas del OpenAPI consolidado**.|Evita traducciones inconsistentes entre modelo y contrato.|
|CLS-02|Anthony no modela sesión separada; Miguel, Daniel y Eduardo sí.|Conservar representación de **sesión**.|RF-01 exige caducidad y revocación.|
|CLS-03|Capas genéricas (Anthony) vs elementos geográficos y subtipos (Miguel, Daniel, Eduardo).|Capas, versiones y elementos, sin jerarquías de dominio innecesarias en el MVP.|RF-03 exige versionado y consulta; la herencia no es obligatoria.|
|CLS-04|Asociación simple vs agregación entre zona y alertas.|**Asociación sin composición destructiva**.|La alerta oficial debe persistir independientemente de la zona.|
|CLS-05|Un cálculo vigente vs varios cálculos históricos.|Prioridad vigente con desglose y posibilidad de conservar cálculos/historial.|RF-09 y RF-12 requieren explicación y trazabilidad.|
|CLS-06|Ajuste de prioridad como clase o subtipo de evento.|Ajuste identificado y relacionado con la zona; cambios registrados en historial.|RF-11 exige justificación y retiro auditable.|
|CLS-07|Marca única (Anthony) vs marcas especializadas (Miguel, Daniel, Eduardo).|**Una representación de marca** con tipo/origen y datos de retiro.|RF-13 se satisface sin una jerarquía extensa.|
|CLS-08|Eventos especializados vs historial genérico.|`EntradaHistorial` como registro común de acciones.|RF-12 exige historial cronológico e inmutable.|
|CLS-09|Contexto territorial como entidad o como atributos/relaciones.|Representar contexto y superposiciones en las respuestas de zona.|RF-08 requiere superposición y distancia al río.|
|CLS-10|Comparaciones con distinta distribución de periodo, fuente y resultado.|Periodos, análisis y resultados por zona como **instantáneas inmutables**.|RF-14 y RF-15 impiden alterar análisis anteriores.|
|CLS-11|Eduardo incluye observaciones y responsables; otras propuestas incluyen extensiones de pesos o capas.|No elevar las mejoras *Should/Could* a dependencias del MVP.|Respeta MoSCoW del SRS.|

**Resultado:** `diagrama\_clases\_equipo.puml`. Para asegurar una correspondencia verificable con el API, el diagrama consolidado representa los **62 schemas** de `components/schemas` del OpenAPI de equipo y sus **267 propiedades** (incluidas las heredadas mediante `allOf`), además de relaciones conceptuales. Esta decisión hace que el archivo sea un **modelo de estructuras de contrato/DTO con asociaciones de dominio**, no un modelo físico de tablas. `ZonaResumen` y `ZonaDetalle`, por ejemplo, son representaciones de la misma zona y no entidades independientes que deban persistirse por duplicado.

## 5\. Artefacto 3 — Diagrama de componentes y arquitectura

### 5.1 Consenso

Las cuatro propuestas coinciden en una **arquitectura cliente-servidor de tres capas**, con **SPA React/TypeScript**, **backend FastAPI modular** y **PostgreSQL/PostGIS**, desplegada en un VPS con Docker Compose. También reconocen a GeoBosques, SERNANP e INGEMMET como fuentes y reservan GEE/RADD/Sentinel-2 para mejoras posteriores.

### 5.2 Conflictos y resolución

|ID|Propuestas|Decisión en `arquitectura\_equipo.md` / `diagrama\_componentes\_equipo.puml`|Motivo|
|-|-|-|-|
|ARQ-01|Miguel propone **Caddy**; Daniel **Nginx**; Anthony y Eduardo no detallan proxy.|**Nginx**.|HTTPS y enrutamiento al backend sin nuevos componentes.|
|ARQ-02|Anthony no explicita worker; Daniel usa worker con PostgreSQL; Eduardo añade Redis; Miguel usa tareas programadas.|**Worker Python y tabla de trabajos en PostgreSQL; sin Redis**.|Soporta ingestas asíncronas con menos infraestructura.|
|ARQ-03|Miguel, Anthony y Daniel describen descarga manual; Eduardo dibuja conexiones fuente→API.|**Descarga por el Analista y subida de archivos**.|El MVP no depende de integraciones automáticas externas.|
|ARQ-04|Tareas programadas (Miguel) vs worker asíncrono (Daniel/Eduardo).|**Worker para ingesta y agrupación**; programación periódica no es requisito arquitectónico central.|Separa petición HTTP del trabajo pesado.|
|ARQ-05|Miguel representa volumen temporal; otros lo omiten.|**Volumen Docker temporal compartido** por API y worker.|Compatible con `POST /archivos` y la ingesta posterior.|
|ARQ-06|GEE/RADD/Sentinel-2 dibujados con distintos niveles de integración.|**Dependencia futura, fuera del MVP**.|Corresponde a funcionalidades *Should*.|
|ARQ-07|Cálculos espaciales en backend o base de datos.|**PostGIS para operaciones espaciales persistidas**, con validaciones en backend.|EPSG:32719 para cálculos; EPSG:4326 para GeoJSON.|
|ARQ-08|Sesión en cookie vs JWT y persistencia.|**Bearer JWT + sesión validada en servidor**.|Permite expiración por inactividad y revocación; roles sin herencia.|
|ARQ-09|Miguel incluye CI/CD, Let's Encrypt y respaldo externo; Daniel incluye respaldo.|**Documentar aspectos operativos** sin tratarlos como módulos del dominio.|Mantiene legible el diagrama del MVP.|

**Resultado:** `arquitectura\_equipo.md` documenta el acuerdo y contiene el diagrama PlantUML; `diagrama\_componentes\_equipo.puml` mantiene la versión editable. La arquitectura resultante incluye **SPA, Nginx, API FastAPI, worker Python, PostgreSQL/PostGIS y volumen temporal**, además de actores y fuentes externas. No se adoptaron microservicios ni Redis.

## 6\. Trazabilidad y consistencia entre artefactos

|Requerimientos del SRS|API consolidada|Modelo de clases|Componentes responsables|
|-|-|-|-|
|RF-01–02: autenticación y usuarios|Sesiones, contraseña y usuarios|Usuario, sesión y DTO de acceso|SPA + API (acceso) + DB|
|RF-03–04: capas e ingesta|Archivos, versiones, cargas y alertas|Capa, versión, carga, alerta y trabajo|API + volumen + worker + PostGIS|
|RF-05–08: zonas, mapa y contexto|Zonas, capas de mapa y contexto|Zona, alerta, geometrías y contexto|API (zonas/mapa) + PostGIS|
|RF-09–13: prioridad y revisión|Prioridad, ajustes, estados, marcas e historial|Prioridad, factor, ajuste, marca y entrada histórica|API (priorización/revisión) + DB|
|RF-14–15: comparación|Creación y consulta de análisis|Periodo, análisis y resultado por zona|API (comparaciones) + DB|
|RF-16–17: exportación|CSV y GeoJSON|DTO de zonas y geometrías|API (exportación) + SPA|

**Reglas comunes que no deben perderse:** 401/403 según autenticación y rol; solo el Analista carga datos, ajusta prioridades, cambia estados, marca y exporta; Coordinación administra usuarios y consulta/compara; no se infiere causa o legalidad ni se expone titular minero; se preservan datos e historiales; las comparaciones son inmutables.

## 7\. Acuerdos finales y límites de la verificación

1. **Contrato API definitivo de trabajo:** `openapi_equipo.yaml` v1.2.0, basado en DMV y armonizado con las demás propuestas, conservando `x-acceptance-criteria`.
2. **Diagrama de clases definitivo de trabajo:** `diagrama\_clases\_equipo.puml`, alineado por nombre de schemas y propiedades con el OpenAPI consolidado; sus DTO no equivalen automáticamente a tablas.
3. **Arquitectura definitiva de trabajo:** `arquitectura\_equipo.md` y `diagrama\_componentes\_equipo.puml`, con monolito modular, worker y PostgreSQL/PostGIS, sin Redis.
4. **Prioridad del equipo:** implementar RF-01 a RF-17 (*Must*) antes de las mejoras *Should/Could*.
5. **Validación realizada y pendiente (25/10/2026):** realizada — contrato válido y coherente con el SRS y el UML; los tres PlantUML renderizados sin errores; 15 de las 38 operaciones implementadas y probadas contra PostgreSQL/PostGIS reales (pytest y Newman). Pendiente — las 23 operaciones restantes, la revisión completa de reglas y multiplicidades del modelo, y las pruebas de seguridad y rendimiento. La consistencia estática de schemas no garantiza por sí sola el comportamiento del software no implementado.

**Síntesis:** Miguel aportó detalle de dominio e infraestructura; Anthony, un modelo compacto del núcleo; Daniel, una base de API trazable y un worker sencillo; Eduardo, una perspectiva extensible y procesamiento asíncrono. Se conservaron las aportaciones compatibles con el SRS y se descartaron las complejidades que no son necesarias para el MVP.

