# Especificación de Requerimientos de Software (SRS) — EcoAlert

**Proyecto:** Elicitación y Especificación de Requerimientos | Individual
**Nombre del sistema:** EcoAlert
**Fecha:** 2026-09-27
**Versión:** Final (con ajustes de revisión)
**Estándar:** IEEE 830 (simplificado)

---

## 1. Introducción

### 1.1 Propósito del documento

Este documento define los requerimientos funcionales, no funcionales y de dominio del sistema **EcoAlert**, sirviendo como base para el diseño, desarrollo y validación de la solución. Está dirigido al equipo de desarrollo, evaluadores y stakeholders del proyecto.

### 1.2 Alcance del sistema

EcoAlert es una plataforma web que facilita la identificación y revisión de cambios en la cobertura vegetal de la Reserva Nacional Tambopata y su zona de amortiguamiento. EcoAlert integra información satelital y geoespacial de múltiples fuentes en una misma plataforma, permite comparar periodos, evaluar cambios detectados, clasificarlos por prioridad y darles seguimiento mediante un historial.

**Incluye:**
- Consulta integrada de información geoespacial.
- Comparación de imágenes de distintos periodos.
- Revisión detallada de cambios con contexto territorial.
- Registro, clasificación y seguimiento de cambios.
- Notificación a especialistas sobre cambios de alta prioridad.
- Filtrado y ordenación de cambios por múltiples criterios.
- Gestión de usuarios y roles.
- Exportación de datos y reportes.

**No incluye:**
- Determinación automática de las causas de los cambios detectados.
- Toma de decisiones sobre acciones de fiscalización o intervención.
- Análisis predictivo o de tendencias futuras.

### 1.3 Definiciones y acrónimos

| Término | Definición |
|---------|------------|
| **SIG** | Sistema de Información Geográfica |
| **RF** | Requerimiento Funcional |
| **RNF** | Requerimiento No Funcional |
| **RD** | Requerimiento de Dominio |
| **SRS** | Software Requirements Specification (Especificación de Requerimientos de Software) |
| **AC** | Criterio de Aceptación (Acceptance Criteria) |
| **Cobertura vegetal** | Conformación de la superficie terrestre por bosques y otros tipos de vegetación |
| **Cambio de cobertura** | Variación en la extensión o tipo de cobertura vegetal entre dos periodos comparados |
| **Zona de amortiguamiento** | Área territorial adyacente a un área protegida que limita impactos externos |
| **Falso positivo** | Alerta de cambio que al ser revisada no corresponde un cambio real de cobertura |

---

## 2. Descripción general

### 2.1 Perspectiva del producto

EcoAlert es una aplicación web independiente que se integra con fuentes de datos geoespaciales públicas y privadas. Reemplaza el proceso actual manual y fragmentado por un flujo centralizado donde el analista puede consultar, comparar, evaluar y dar seguimiento a los cambios de cobertura vegetal en un solo sistema.

El sistema no reemplaza el criterio del especialista, sino que le proporciona herramientas e información contextual para facilitar su trabajo.

### 2.2 Funciones del producto

1. **Consulta integrada:** Acceso a información satelital y geoespacial de múltiples fuentes en un solo lugar.
2. **Comparación temporal:** Visualización y comparación de imágenes de distintos periodos.
3. **Evaluación de cambios:** Revisión detallada de cada cambio con información territorial asociada.
4. **Gestión de cambios:** Registro de observaciones, clasificación por prioridad y conservación de historial.
5. **Priorización:** Identificación de cambios que requieren atención inmediata mediante niveles de prioridad y estado de revisión.
6. **Notificación:** Alerta a especialistas sobre cambios de alta prioridad.
7. **Filtrado y ordenación:** Búsqueda eficiente de cambios por fecha, ubicación, extensión, prioridad y estado.
8. **Gestión de usuarios:** Registro, asignación de roles y control de acceso.
9. **Exportación:** Generación de reportes y datos en formatos compartibles.

### 2.3 Características del usuario

| Perfil | Descripción | Necesidades principales |
|--------|-------------|------------------------|
| **Analista Ambiental** | Usuario principal del sistema. Opera la plataforma a diario. | Consultar, comparar, evaluar y documentar cambios de cobertura vegetal. |
| **Especialista SIG** | Técnico con conocimiento en sistemas de información geográfica. | Acceder a datos geoespaciales, revisar contexto y dar seguimiento. |
| **Coordinador de Monitoreo** | Supervisor del equipo de análisis. | Visión global del estado del monitoreo, gestión de prioridades. |

### 2.4 Restricciones

- El sistema no determina automáticamente las causas de los cambios detectados.
- La interpretación y decisión final recae siempre en el especialista.
- El acceso a la información territorial sensible debe estar protegido.
- La información geoespacial debe ser clara y legible a escala de trabajo de zona.

---

## 3. Requerimientos específicos

### 3.1 Requerimientos funcionales

#### RF-01: Consultar información satelital y geoespacial integrada

**Descripción:** El sistema debe permitir consultar información satelital y geoespacial de múltiples fuentes integradas en un solo lugar.

**Criterios de aceptación:**

- **RF-01-AC-1:**
  - **Dado que** el usuario ha iniciado sesión en el sistema,
  - **cuando** selecciona una fuente de información geoespacial disponible,
  - **entonces** el sistema muestra los datos de dicha fuente en el mapa interactivo.

- **RF-01-AC-2:**
  - **Dado que** el usuario ha iniciado sesión en el sistema,
  - **cuando** consulta las fuentes de datos disponibles,
  - **entonces** el sistema presenta al menos 2 fuentes distintas de información geoespacial.

---

#### RF-02: Comparar imágenes de distintos periodos

**Descripción:** El sistema debe permitir comparar imágenes de distintos periodos para identificar cambios en la cobertura vegetal.

**Criterios de aceptación:**

- **RF-02-AC-1:**
  - **Dado que** el usuario ha seleccionado una zona de interés en el mapa,
  - **cuando** elige dos periodos de tiempo distintos para comparar,
  - **entonces** el sistema muestra las imágenes satelitales de ambos periodos de forma simultánea o con herramienta de comparación visual.

- **RF-02-AC-2:**
  - **Dado que** el usuario está comparando dos periodos,
  - **cuando** selecciona un periodo con cobertura vegetal y otro sin ella,
  - **entonces** el sistema muestra ambas imágenes utilizando la misma extensión geográfica y escala para permitir su comparación.

---

#### RF-03: Ver ubicación, extensión y fechas de cambios

**Descripción:** El sistema debe mostrar la ubicación, extensión y fechas de los cambios detectados.

**Criterios de aceptación:**

- **RF-03-AC-1:**
  - **Dado que** el usuario ha iniciado sesión y visualiza la lista de cambios detectados,
  - **cuando** selecciona un cambio de la lista o del mapa,
  - **entonces** el sistema muestra la ubicación del cambio, su extensión en hectáreas y las fechas del periodo en que fue detectado.

---

#### RF-04: Revisar área con detalle e información territorial

**Descripción:** El sistema debe permitir revisar el área de un cambio identificado con mayor detalle, incluyendo la información territorial disponible sobre la zona.

**Criterios de aceptación:**

- **RF-04-AC-1:**
  - **Dado que** el usuario ha seleccionado un cambio detectado,
  - **cuando** hace zoom al área del cambio,
  - **entonces** el sistema muestra la zona ampliada con las capas territoriales que intersectan (límites de reserva, zona de amortiguamiento, comunidades, concesiones).

- **RF-04-AC-2:**
  - **Dado que** el usuario está revisando un cambio,
  - **cuando** consulta la información territorial de la zona,
  - **entonces** el sistema muestra el nombre, tipo y datos disponibles de cada capa territorial asociada a la zona.

---

#### RF-05: Registrar observaciones sobre un cambio

**Descripción:** El sistema debe permitir registrar observaciones sobre un cambio detectado.

**Criterios de aceptación:**

- **RF-05-AC-1:**
  - **Dado que** el usuario ha seleccionado un cambio detectado,
  - **cuando** agrega una nota de texto como observación,
  - **entonces** la observación queda asociada al cambio, visible para otros usuarios autorizados, con fecha y autor registrados.

---

#### RF-06: Clasificar prioridad de un cambio

**Descripción:** El sistema debe permitir clasificar la prioridad de un cambio identificado.

**Criterios de aceptación:**

- **RF-06-AC-1:**
  - **Dado que** el usuario ha seleccionado un cambio detectado,
  - **cuando** asigna un nivel de prioridad (alta, media o baja),
  - **entonces** la clasificación queda registrada con fecha y autor, y el cambio puede ser reclasificado en cualquier momento.

---

#### RF-07: Conservar historial de cambios y revisiones

**Descripción:** El sistema debe conservar un historial de los cambios y revisiones realizadas para darles seguimiento.

**Criterios de aceptación:**

- **RF-07-AC-1:**
  - **Dado que** un cambio ha sido creado en el sistema,
  - **cuando** se realiza cualquier acción sobre él (creación, observación, clasificación, cambio de estado),
  - **entonces** el sistema registra la acción en un historial cronológico con fecha, usuario y descripción.

- **RF-07-AC-2:**
  - **Dado que** un cambio tiene un historial de acciones,
  - **cuando** cualquier usuario autorizado consulta el historial,
  - **entonces** el sistema muestra todas las acciones registradas de forma cronológica.

---

#### RF-08: Filtrar y ordenar cambios

**Descripción:** El sistema debe permitir filtrar y ordenar los cambios detectados por fecha, ubicación, extensión, prioridad y estado.

**Criterios de aceptación:**

- **RF-08-AC-1:**
  - **Dado que** el usuario visualiza la lista de cambios detectados,
  - **cuando** aplica uno o más filtros (fecha, ubicación, extensión, prioridad, estado),
  - **entonces** el sistema muestra únicamente los cambios que cumplen los criterios seleccionados.

- **RF-08-AC-2:**
  - **Dado que** el usuario visualiza la lista de cambios detectados,
  - **cuando** ordena los resultados por un criterio (fecha, ubicación, extensión, prioridad o estado) de forma ascendente o descendente,
  - **entonces** el sistema reorganiza la lista según el criterio y dirección seleccionados.

---

#### RF-09: Notificar a especialistas sobre cambios de alta prioridad

**Descripción:** El sistema debe notificar a los especialistas cuando se detecte un nuevo cambio clasificado como de alta prioridad.

**Criterios de aceptación:**

- **RF-09-AC-1:**
  - **Dado que** un cambio ha sido clasificado como de alta prioridad,
  - **cuando** se guarda dicha clasificación,
  - **entonces** el sistema genera una notificación interna para todos los usuarios con rol de especialista, asociada al cambio clasificado.

- **RF-09-AC-2:**
  - **Dado que** una notificación ha sido generada,
  - **cuando** un especialista revisa sus notificaciones,
  - **entonces** encuentra la notificación con la ubicación del cambio y su clasificación de alta prioridad.

---

#### RF-10: Identificar cambios prioritarios

**Descripción:** El sistema debe permitir identificar qué cambios deben revisarse primero mediante su nivel de prioridad y estado de revisión.

**Criterios de aceptación:**

- **RF-10-AC-1:**
  - **Dado que** el usuario visualiza la lista de cambios detectados,
  - **cuando** accede a la vista o filtro de cambios pendientes de revisión,
  - **entonces** el sistema muestra los cambios que aún no han sido revisados.

- **RF-10-AC-2:**
  - **Dado que** existen cambios con distintos niveles de prioridad,
  - **cuando** el usuario ordena los cambios por prioridad,
  - **entonces** los cambios de alta prioridad se distinguen visualmente de los demás.

---

#### RF-11: Gestionar estados de revisión de cambios

**Descripción:** El sistema debe permitir gestionar el estado de revisión de los cambios detectados, definiendo los estados posibles y las transiciones permitidas.

**Estados definidos:**
- **Pendiente:** El cambio ha sido detectado pero aún no ha sido asignado a un especialista.
- **En revisión:** Un especialista está evaluando el cambio activamente.
- **Completado:** El especialista ha finalizado la evaluación del cambio.

**Transiciones permitidas:**
- Pendiente → En revisión (cuando un especialista se asigna al cambio)
- En revisión → Completado (cuando el especialista finaliza la evaluación)
- En revisión → Pendiente (cuando se desasigna el especialista)

**Criterios de aceptación:**

- **RF-11-AC-1:**
  - **Dado que** un cambio se encuentra en estado "Pendiente",
  - **cuando** un especialista se asigna al cambio,
  - **entonces** el sistema cambia el estado a "En revisión" y registra la asignación en el historial.

- **RF-11-AC-2:**
  - **Dado que** un cambio se encuentra en estado "En revisión",
  - **cuando** el especialista finaliza la evaluación,
  - **entonces** el sistema cambia el estado a "Completado" y registra la finalización en el historial.

---

#### RF-12: Gestionar usuarios y roles

**Descripción:** El sistema debe permitir la gestión de usuarios, incluyendo registro, asignación de roles y desactivación de cuentas.

**Roles definidos:**
- **Analista:** Puede consultar, comparar, evaluar, documentar y clasificar cambios.
- **Especialista:** Puede revisar cambios asignados, registrar observaciones y finalizar evaluaciones.
- **Coordinador:** Puede gestionar usuarios, asignar cambios a especialistas y supervisar el estado global.

**Criterios de aceptación:**

- **RF-12-AC-1:**
  - **Dado que** un usuario con rol de Coordinador ha iniciado sesión,
  - **cuando** registra un nuevo usuario y le asigna un rol,
  - **entonces** el sistema crea la cuenta y envía las credenciales al nuevo usuario.

- **RF-12-AC-2:**
  - **Dado que** un usuario con rol de Coordinador ha iniciado sesión,
  - **cuando** desactiva una cuenta de usuario,
  - **entonces** el sistema impide el acceso a dicho usuario y preserva su historial de acciones.

---

#### RF-13: Exportar datos y reportes

**Descripción:** El sistema debe permitir exportar datos y reportes en formatos compartibles.

**Formatos soportados:**
- **PDF:** Reportes de cambios con mapa, datos y observaciones.
- **Shapefile:** Datos geoespaciales de cambios para uso en software SIG.
- **GeoJSON:** Formato abierto para intercambio de datos geoespaciales.

**Criterios de aceptación:**

- **RF-13-AC-1:**
  - **Dado que** el usuario ha seleccionado uno o más cambios,
  - **cuando** solicita la exportación en formato PDF,
  - **entonces** el sistema genera un reporte con mapa, datos del cambio y observaciones registradas.

- **RF-13-AC-2:**
  - **Dado que** el usuario ha seleccionado uno o más cambios,
  - **cuando** solicita la exportación en formato Shapefile o GeoJSON,
  - **entonces** el sistema genera un archivo con los datos geoespaciales de los cambios seleccionados.

---

### 3.2 Requerimientos no funcionales

#### RNF-01: Rendimiento

**Descripción:** El sistema debe cargar los resultados de consulta de zonas y la comparación de periodos en menos de 5 segundos, bajo las siguientes condiciones de prueba:
- **Volumen de datos:** hasta 500 cambios activos y 20 capas geoespaciales cargadas simultáneamente.
- **Conexión:** ancho de banda de 10 Mbps (conexión estándar de oficina).
- **Carga del servidor:** hasta 20 usuarios concurrentes realizando consultas simultáneas.

**Criterios de verificación:**
- Tiempo de respuesta medido bajo las condiciones de prueba definidas.
- Pruebas de rendimiento con volumen típico de datos de la zona de estudio.

---

#### RNF-02: Usabilidad — Facilidad de aprendizaje

**Descripción:** El sistema debe permitir a un analista ambiental sin experiencia en programación ni administración de sistemas completar las operaciones principales (consulta, comparación, registro y clasificación de cambios) en menos de 2 horas de capacitación.

**Criterios de verificación:**
- Pruebas de usabilidad con usuarios del perfil objetivo sin experiencia técnica.
- Medición del tiempo hasta completar tareas principales sin asistencia.

---

#### RNF-03: Usabilidad — Claridad de información geoespacial

**Descripción:** El sistema debe mostrar la información geoespacial con claridad, incluyendo distinción visual entre periodos comparados y legibilidad de capas superpuestas a escalas entre 1:10,000 y 1:50,000.

**Criterios de verificación:**
- Evaluación de legibilidad con usuarios especialistas a las escalas definidas.
- Verificación de contraste y diferenciación visual entre capas y periodos.

---

#### RNF-04: Seguridad

**Descripción:** El acceso a la información debe estar protegido mediante autenticación de usuarios y control de acceso basado en roles (analista, especialista, coordinador).

**Criterios de verificación:**
- Verificación de que usuarios no autenticados no pueden acceder al sistema.
- Verificación de que cada rol solo puede realizar las acciones permitidas.
- Registro de accesos y acciones sensibles.

---

### 3.3 Requerimientos de dominio

#### RD-01: Área de monitoreo

**Descripción:** El sistema está orientado al monitoreo de la Reserva Nacional Tambopata y su zona de amortiguamiento.

---

#### RD-02: Interpretación humana

**Descripción:** El sistema no debe determinar automáticamente las causas de los cambios detectados; la interpretación y decisión final recae en el especialista.

---

#### RD-03: Priorización asistida

**Descripción:** La priorización de zonas debe utilizar los niveles alta, media y baja, manteniendo la decisión final de revisión bajo responsabilidad del especialista.

---

## Fin del documento
