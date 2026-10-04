# Especificación de Requisitos de Software (SRS)
## EcoAlert

**Versión:** 1.0
**Fecha:** 27 de septiembre de 2026
**Estándar de referencia:** IEEE 830 (simplificado)

---

## 1. Introducción

### 1.1 Propósito del documento

Este documento especifica los requerimientos funcionales, no funcionales y de dominio del sistema **EcoAlert**, un sistema de monitoreo satelital orientado a identificar cambios en la cobertura terrestre y zonas potencialmente intervenidas por actividades como la deforestación y la minería.

El documento está dirigido al equipo de desarrollo, al Product Owner y a los stakeholders involucrados en la validación funcional del sistema, y sirve como base para el diseño, la construcción, las pruebas y la aceptación del producto. Los requerimientos aquí descritos se derivaron de la sesión de elicitación realizada con el Product Owner (preguntas P1–P10) y fueron posteriormente clasificados, revisados y consolidados en la versión 2 del documento de requerimientos.

### 1.2 Alcance del sistema

EcoAlert permitirá a investigadores, especialistas ambientales e instituciones de gestión territorial:

- Seleccionar una zona de interés y compararla entre dos periodos de tiempo.
- Visualizar de forma automática las áreas donde se detecte pérdida de cobertura terrestre.
- Consultar el detalle de cada cambio detectado, incluyendo su posible causa, ubicación, extensión y nivel de confianza.
- Cruzar los cambios detectados contra información oficial de concesiones mineras (INGEMMET) y áreas protegidas.
- Exportar y dar seguimiento a los hallazgos a lo largo del tiempo.
- Administrar usuarios, roles y fuentes de datos del sistema.

**Fuera de alcance del MVP** (según lo señalado por el PO durante la elicitación, ver sección 2.4 y RD-02):

- El rol de Visor externo/público (RF-10), previsto para una fase futura.
- La comparación de series temporales completas (más de dos periodos), pendiente de confirmación formal.
- El trabajo de verificación en campo mediante una aplicación móvil nativa; el MVP contempla únicamente una versión ligera con soporte offline (RNF-02), no una app dedicada.

### 1.3 Definiciones y acrónimos

| Término | Definición |
| --- | --- |
| **SRS** | Software Requirements Specification (Especificación de Requisitos de Software). |
| **MVP** | Minimum Viable Product (Producto Mínimo Viable). |
| **PO** | Product Owner. |
| **RF / RNF / RD** | Requerimiento Funcional / No Funcional / de Dominio. |
| **GEE** | Google Earth Engine, plataforma de análisis geoespacial e imágenes satelitales. |
| **GeoBosques** | Plataforma del Estado peruano que emite alertas de deforestación. |
| **INGEMMET** | Instituto Geológico, Minero y Metalúrgico del Perú; fuente del catastro de concesiones mineras. |
| **NDVI** | Normalized Difference Vegetation Index, índice espectral usado para medir densidad de vegetación. |
| **NDFI** | Normalized Difference Fraction Index, índice espectral usado para detectar degradación forestal. |
| **Sentinel-2 / Landsat** | Constelaciones de satélites de observación terrestre usadas como fuente de imágenes. |
| **Shapefile / GeoJSON** | Formatos estándar de intercambio de datos geoespaciales vectoriales. |
| **Falso positivo** | Alerta de cambio generada por el sistema que no corresponde a un cambio real (p. ej. por nubosidad). |
| **Zona de interés** | Área geográfica delimitada por el usuario (por nombre, coordenadas o polígono) sobre la cual se realiza el análisis. |

---

## 2. Descripción general

### 2.1 Perspectiva del producto

EcoAlert es un sistema nuevo que actúa como capa de integración y análisis sobre tres fuentes de datos externas —Google Earth Engine, GeoBosques e INGEMMET— cada una con su propia frecuencia de actualización y formato. El sistema no reemplaza a estas fuentes ni pretende resolver discrepancias entre ellas de forma automática (RF-06); su función es facilitar la consulta, comparación y trazabilidad de la información para que un usuario experto tome la decisión final.

El producto se concibe como una aplicación web accesible principalmente desde navegador de escritorio, con un modo adicional orientado a verificación en campo (RNF-02).

### 2.2 Funciones del producto

A alto nivel, EcoAlert ofrece las siguientes funciones:

1. **Comparación geoespacial**: selección de zona y comparación visual entre dos periodos (RF-01, RF-02, RF-03).
2. **Detección y clasificación automática de cambios**: aplicación de umbrales espectrales y cruce con capas oficiales (RF-04, RF-05, RF-06).
3. **Gestión de alertas y seguimiento**: historial por zona, confirmación/descarte de alertas y exportación de resultados (RF-07, RF-08, RF-09).
4. **Administración**: gestión de roles, usuarios y fuentes de datos (RF-10).
5. **Monitoreo de integraciones**: notificación de fuentes caídas o desactualizadas (RF-11).

### 2.3 Características del usuario

| Rol | Descripción | Nivel técnico esperado |
| --- | --- | --- |
| **Investigador / Analista** | Usuario principal. Consulta zonas, compara periodos, revisa alertas, confirma o descarta casos y exporta resultados. | Conocimiento del dominio ambiental/geoespacial; no requiere programar. |
| **Administrador institucional** | Gestiona los usuarios de su organización y define zonas de interés prioritarias para su institución. | Conocimiento administrativo; no requiere programar. |
| **Superadmin** | Gestión global del sistema y configuración de las fuentes de datos integradas. | Perfil técnico. |
| **Visor externo** *(fuera de alcance del MVP)* | Acceso limitado a información ya validada, sin datos sensibles. | Perfil general, sin conocimiento técnico. |

### 2.4 Restricciones

- **RD-01**: la precisión espacial está limitada por la resolución nativa de las fuentes (10 m Sentinel-2 / 30 m Landsat), lo que impone un límite práctico de detección de aproximadamente 0.5–1 hectárea.
- **RD-02**: el alcance del MVP respecto a series temporales completas y seguimiento en el tiempo se encuentra pendiente de confirmación formal con el PO; los requerimientos de este documento asumen el escenario mínimo (comparación de dos periodos) descrito en RF-01.
- **RD-03**: el sistema opera con un desfase inherente de 1 a 4 semanas respecto a la fecha real de los eventos, ya que ninguna de las fuentes integradas entrega datos en tiempo real.
- El sistema depende de la disponibilidad y el formato de tres proveedores de datos externos sobre los cuales el equipo de EcoAlert no tiene control directo (Google Earth Engine, GeoBosques, INGEMMET).
- Los umbrales de clasificación de cambio (NDVI/NDFI) definidos en RF-04 son una propuesta preliminar que debe validarse con un especialista ambiental o forestal antes de su uso en producción (ver PA-04 del documento de evolución de requerimientos).

---

## 3. Requerimientos específicos

### 3.1 Requerimientos funcionales

#### RF-01 — Selección de zona y comparación de periodos
**Descripción:** El sistema debe permitir seleccionar una zona de interés (por nombre, coordenadas o dibujando un polígono) y comparar dos periodos de tiempo mediante vista lado a lado o slider.
**Evidencia:** P1
**Criterios de aceptación:**
- Dado que el usuario ingresa un nombre, coordenadas o dibuja un polígono, el sistema debe delimitar correctamente la zona de interés seleccionada.
- El usuario debe poder definir un "Periodo A" y un "Periodo B" mediante rangos de fecha.
- El sistema debe presentar la comparación en al menos dos modos de visualización: vista lado a lado y slider deslizante.
- Si la zona o alguno de los periodos no es válido, el sistema debe mostrar un mensaje de error claro sin interrumpir el resto de la sesión.

#### RF-02 — Capa de diferencia
**Descripción:** El sistema debe generar una capa de "diferencia" que resalte los polígonos con pérdida de cobertura entre los dos periodos comparados.
**Evidencia:** P1
**Criterios de aceptación:**
- Tras ejecutar una comparación (RF-01), el sistema debe generar automáticamente una capa que resalte visualmente los polígonos con pérdida de cobertura.
- La capa de diferencia debe poder activarse o desactivarse sobre el mapa sin recalcular la comparación completa.
- Si no se detectan cambios en la zona y periodos seleccionados, el sistema debe indicarlo explícitamente en lugar de mostrar una capa vacía sin explicación.

#### RF-03 — Detalle de área resaltada
**Descripción:** Al seleccionar un área resaltada, el sistema debe mostrar como mínimo: hectáreas afectadas, % de cambio, tipo de cambio probable (pérdida de cobertura / posible minería / no clasificado), fecha o rango de detección, nivel de confianza, fuente(s) de datos y contexto legal-administrativo (concesión minera / área protegida) cuando aplique.
**Evidencia:** P1, P3
**Criterios de aceptación:**
- Al hacer clic sobre un polígono resaltado, el sistema debe desplegar un panel o ventana con los siete campos mínimos indicados en la descripción.
- El campo "tipo de cambio probable" debe mostrar uno de los tres valores definidos: pérdida de cobertura, posible minería o no clasificado.
- El campo de contexto legal-administrativo solo debe mostrarse cuando exista información aplicable (concesión minera o área protegida); en caso contrario, el sistema debe omitirlo o indicar "sin información asociada".
- Todos los valores numéricos (hectáreas, % de cambio, nivel de confianza) deben mostrarse con su unidad correspondiente.

#### RF-04 — Clasificación automática del tipo de cambio
**Descripción:** El sistema debe clasificar el tipo de cambio detectado aplicando umbrales sobre índices espectrales (NDVI/NDFI), generando una alerta solo cuando el cambio se sostenga en ≥2 lecturas consecutivas, para reducir falsos positivos por nubosidad u otros factores transitorios.
**Evidencia:** P2
**Criterios de aceptación:**
- El sistema debe calcular los índices NDVI y/o NDFI para cada zona analizada en cada periodo.
- Una alerta solo debe generarse si la variación del índice supera el umbral configurado en al menos dos lecturas consecutivas.
- Si la variación se detecta en una sola lectura, el sistema no debe generar una alerta, pero puede registrar el evento como "no confirmado" para trazabilidad interna.
- Los umbrales utilizados deben ser configurables por el rol Superadmin, dado que son una propuesta preliminar sujeta a validación (ver sección 2.4).

#### RF-05 — Cruce con concesiones mineras y áreas protegidas
**Descripción:** El sistema debe cruzar automáticamente cada zona con cambio detectado contra capas de concesiones mineras (INGEMMET) y áreas protegidas, indicando si el cambio cae dentro o fuera de una concesión activa o de un área protegida.
**Evidencia:** P2, P10
**Criterios de aceptación:**
- Para cada cambio detectado, el sistema debe verificar automáticamente su ubicación contra la capa vigente de concesiones mineras de INGEMMET.
- El sistema debe indicar explícitamente si el cambio se ubica dentro o fuera de una concesión activa.
- El sistema debe indicar explícitamente si el cambio se ubica dentro o fuera de un área protegida.
- Si la capa de INGEMMET no está disponible al momento del cruce, el sistema debe aplicar el comportamiento definido en RF-11 (notificación de fuente desactualizada) en lugar de omitir el resultado silenciosamente.

#### RF-06 — Manejo de discrepancias entre fuentes
**Descripción:** Cuando distintas fuentes arrojen resultados distintos para una misma zona, el sistema debe mostrarlas de forma independiente y trazable (ej. "GeoBosques indica X, imagen satelital sugiere Y"), sin fusionarlas automáticamente en un solo veredicto.
**Evidencia:** P4
**Criterios de aceptación:**
- Si dos o más fuentes entregan resultados distintos para una misma zona y periodo, el sistema debe mostrar cada resultado de forma separada, identificando la fuente de cada uno.
- El sistema no debe combinar ni promediar automáticamente los resultados de distintas fuentes en un único veredicto.
- El usuario debe poder identificar visualmente, sin ambigüedad, qué fuente respalda cada resultado mostrado.

#### RF-07 — Exportación y guardado de comparaciones
**Descripción:** El sistema debe permitir exportar los resultados de una comparación en formato reporte, imagen o archivo geoespacial (Shapefile/GeoJSON), y guardar la comparación para darle seguimiento posterior.
**Evidencia:** P1
**Criterios de aceptación:**
- El sistema debe permitir exportar una comparación como reporte, como imagen y como archivo geoespacial (Shapefile o GeoJSON).
- El sistema debe permitir guardar una comparación realizada para que pueda ser recuperada posteriormente por el mismo usuario.
- Los archivos exportados deben conservar la referencia a la zona, los periodos comparados y la fecha de generación.

#### RF-08 — Historial y trazabilidad de zonas
**Descripción:** El sistema debe mantener un historial/trazabilidad de cada zona monitoreada a lo largo del tiempo, incluyendo estados del caso (nueva, en revisión, confirmada, descartada).
**Evidencia:** P7
**Criterios de aceptación:**
- Cada zona monitoreada debe tener asociado un historial consultable con las comparaciones y cambios detectados previamente.
- El sistema debe soportar, como mínimo, los estados: nueva, en revisión, confirmada y descartada.
- Todo cambio de estado debe quedar registrado en el historial de la zona con su fecha correspondiente.

#### RF-09 — Confirmación o descarte manual de alertas
**Descripción:** El sistema debe permitir a un usuario autorizado marcar manualmente una alerta como confirmada o descartada, registrando quién y cuándo lo hizo.
**Evidencia:** P3, P7
**Criterios de aceptación:**
- Solo un usuario con el rol adecuado (Investigador/Analista o superior) puede confirmar o descartar una alerta.
- Al confirmar o descartar una alerta, el sistema debe registrar el usuario que realizó la acción y la fecha/hora exacta.
- El cambio de estado debe reflejarse inmediatamente en el historial de la zona (RF-08).
- El sistema debe impedir que un usuario sin los permisos adecuados realice esta acción, mostrando un mensaje de acceso denegado.

#### RF-10 — Roles y permisos
**Descripción:** El sistema debe soportar los roles Investigador/Analista, Administrador institucional y Superadmin, con permisos diferenciados de consulta, gestión de usuarios/zonas y configuración de fuentes de datos. El rol Visor externo queda fuera del alcance del MVP (fase futura).
**Evidencia:** P6
**Criterios de aceptación:**
- El sistema debe permitir asignar a cada usuario uno de los tres roles del MVP: Investigador/Analista, Administrador institucional o Superadmin.
- Un usuario con rol Investigador/Analista solo debe poder consultar, comparar, exportar y confirmar/descartar alertas, sin acceso a la gestión de usuarios ni configuración de fuentes.
- Un usuario con rol Administrador institucional debe poder gestionar los usuarios de su institución y definir zonas de interés prioritarias, sin acceso a la configuración global de fuentes.
- Un usuario con rol Superadmin debe tener acceso a la configuración global del sistema, incluyendo las fuentes de datos integradas.
- El sistema no debe exponer funcionalidad alguna asociada al rol Visor externo en esta versión.

#### RF-11 — Notificación de fuente desactualizada
**Descripción:** El sistema debe notificar de forma visible al usuario cuando una fuente de datos no responda o esté desactualizada, indicando la fecha de la última actualización disponible, y utilizar el último dato en caché sin presentarlo como información vigente.
**Evidencia:** P9
**Criterios de aceptación:**
- Si una fuente de datos no responde, el sistema debe mostrar un aviso visible al usuario indicando la fuente afectada y la fecha de su última actualización conocida.
- Mientras la fuente esté indisponible, el sistema debe continuar operando con el último dato disponible en caché, sin bloquear el resto de la funcionalidad.
- El dato mostrado desde caché debe estar claramente marcado como potencialmente desactualizado, y nunca debe presentarse como información vigente.
- Todo incidente de indisponibilidad debe quedar registrado para monitoreo técnico (ver RNF-01).

### 3.2 Requerimientos no funcionales

| ID | Categoría | Descripción | Evidencia |
| --- | --- | --- | --- |
| RNF-01 | Disponibilidad / Confiabilidad | El sistema no debe bloquear su funcionalidad completa ante la caída o desactualización de una sola fuente de datos, y debe registrar el incidente para monitoreo técnico (observabilidad de integraciones). | P9 |
| RNF-02 | Usabilidad / Accesibilidad | El sistema debe ofrecer un modo de uso adaptado a verificación en campo, mediante una versión ligera con soporte offline y uso del GPS del dispositivo, para escenarios de conectividad limitada. | P8 |
| RNF-03 | Seguridad | El sistema debe permitir restringir el nivel de detalle geoespacial mostrado (p. ej. coordenadas exactas) según el rol del usuario, para proteger comunidades y propiedad privada de un uso indebido de la información. | P6 |
| RNF-04 | Calidad de detección | La tasa de falsos positivos debe minimizarse considerando fuentes de confusión conocidas (nubosidad, sombras, cambios estacionales de cultivo que se confunden con deforestación). | P5 |

### 3.3 Requerimientos de dominio

| ID | Descripción | Evidencia |
| --- | --- | --- |
| RD-01 | La precisión espacial del sistema está limitada por la resolución nativa de las fuentes disponibles (10 m con Sentinel-2 o 30 m con Landsat), lo que condiciona la capacidad de detectar cambios menores a 0.5–1 hectárea. | P5 |
| RD-02 | El alcance del MVP debe definirse formalmente respecto a si incluye comparación de series temporales completas o solo dos periodos puntuales, y si el "seguimiento en el tiempo" forma parte del alcance mínimo. | P1, P7 |
| RD-03 | El sistema opera con un desfase inherente de 1 a 4 semanas frente a la fecha real de los eventos, dado que ninguna de las fuentes integradas (Google Earth Engine, GeoBosques, INGEMMET) entrega datos en tiempo real. | P5 |
