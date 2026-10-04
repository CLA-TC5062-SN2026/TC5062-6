# Especificación de Requerimientos de Software (SRS)
# EcoAlert Tambopata

## 1. Introducción

### 1.1 Propósito del documento

Este documento especifica los requerimientos funcionales, no funcionales y de dominio de EcoAlert Tambopata. Su propósito es establecer el comportamiento esperado del MVP y servir como referencia para su diseño, implementación y validación.

Los requerimientos se basan en el contexto aprobado del proyecto, la elicitación con stakeholders, la revisión crítica de requerimientos y los criterios de aceptación definidos para los requerimientos funcionales.

### 1.2 Alcance del sistema

EcoAlert Tambopata será una plataforma web de apoyo al monitoreo ambiental en la Reserva Nacional Tambopata y su zona de amortiguamiento, ubicadas en Madre de Dios, en la Amazonía suroriental del Perú.

El MVP apoyará la identificación, contextualización y priorización de cambios de cobertura vegetal mediante información geoespacial y fuentes externas. Permitirá que un especialista revise zonas candidatas, consulte su contexto territorial, analice los factores relacionados con su prioridad y registre el avance de su revisión.

La prioridad generada por el sistema será una recomendación. La decisión final sobre la interpretación y las acciones de revisión permanecerá en manos del especialista ambiental o SIG.

El sistema no determinará automáticamente la causa de un cambio ni determinará automáticamente que un cambio corresponde a minería ilegal. Tampoco establecerá automáticamente la legalidad de una intervención, ya que esas conclusiones requieren análisis especializado y otras evidencias.

#### Fuera de alcance del MVP

- Determinación automática de minería ilegal.
- Gestión documental amplia de evidencias.
- Notificaciones automáticas.
- Aplicación móvil.
- Expansión inicial a todo el Perú.

### 1.3 Definiciones y acrónimos

- **SRS:** Especificación de Requerimientos de Software.
- **RF:** Requerimiento funcional. Describe un comportamiento o capacidad que el sistema debe proporcionar.
- **RNF:** Requerimiento no funcional. Describe una condición de calidad, operación o seguridad del sistema.
- **RD:** Requerimiento de dominio. Describe una regla o condición propia del monitoreo ambiental que el sistema debe respetar.
- **SIG:** Sistema de Información Geográfica. Conjunto de herramientas y conocimientos utilizados para trabajar con información relacionada con ubicaciones geográficas.
- **MVP:** Producto mínimo viable. Primera versión del sistema con el alcance necesario para demostrar el flujo principal del proyecto.
- **Zona candidata:** Área en la que se identifica una posible variación de cobertura vegetal que requiere análisis o revisión adicional. No representa necesariamente un cambio confirmado.
- **Prioridad sugerida:** Recomendación del sistema sobre el orden en que conviene revisar una zona. En el MVP se expresará mediante los niveles Alta, Media o Baja y no sustituirá el criterio profesional.
- **Zona de amortiguamiento:** Área ubicada alrededor de un área natural protegida que forma parte del contexto territorial considerado para el monitoreo y la conservación.
- **Pendiente:** Estado inicial de una zona candidata recién identificada, antes de iniciar su revisión.
- **En revisión:** Estado de una zona cuya revisión ya fue iniciada por el especialista.
- **Incierto:** Estado de una zona cuya evidencia disponible es insuficiente o contradictoria para llegar a una conclusión.
- **Revisado:** Estado que indica que el especialista terminó la revisión. No significa que el cambio, su causa o su legalidad hayan sido confirmados.
- **Limitación conocida:** Condición de calidad, comparabilidad, disponibilidad o suficiencia de la información que puede afectar la interpretación de un análisis.

## 2. Descripción general

### 2.1 Perspectiva del producto

EcoAlert Tambopata será una plataforma web de apoyo al monitoreo ambiental. Su propósito será transformar información geoespacial y datos provenientes de fuentes externas en información más comprensible y contextualizada para un especialista ambiental o SIG.

El sistema apoyará el trabajo de revisión de cambios de cobertura vegetal en un territorio ambientalmente sensible. El especialista podrá comparar periodos, consultar zonas identificadas, revisar su contexto territorial, analizar una prioridad sugerida y actualizar el estado de la revisión.

La plataforma complementará el análisis profesional y las verificaciones de campo. No reemplazará la interpretación del especialista ni presentará como confirmados los resultados que dependan de información insuficiente o no disponible.

### 2.2 Funciones del producto

Las funciones principales del producto son:

- Permitir la autenticación del usuario.
- Permitir la selección de dos periodos de comparación válidos, distintos y no superpuestos.
- Identificar zonas candidatas con cambios de cobertura vegetal dentro de la Reserva Nacional Tambopata o su zona de amortiguamiento.
- Visualizar en un mapa la ubicación georreferenciada de las zonas identificadas.
- Consultar el contexto territorial de cada zona, incluida la distancia mínima en metros al recurso hídrico georreferenciado disponible más cercano cuando exista información.
- Generar una prioridad sugerida expresada como Alta, Media o Baja cuando exista al menos un factor disponible, o como No disponible cuando ninguno de los factores tenga información.
- Consultar siempre los seis factores de prioridad definidos y mostrar su valor o No disponible cuando no exista información.
- Permitir que el especialista modifique la prioridad y registre una justificación.
- Registrar el estado de revisión de cada zona como Pendiente, En revisión, Incierto o Revisado, incluyendo una observación opcional asociada a la revisión.
- Al completar un análisis, almacenarlo automáticamente con sus fuentes, periodos, limitaciones conocidas y datos específicos de cada zona candidata.
- Consultar la lista de análisis almacenados previamente y acceder al detalle de un análisis seleccionado, incluyendo sus limitaciones y datos por zona.
- Mostrar las zonas con prioridad Alta antes que las de prioridad Media y estas antes que las de prioridad Baja; actualizar ese orden cuando cambie una prioridad.

### 2.3 Características del usuario

El usuario principal será el **Especialista ambiental / SIG**.

Este usuario cuenta con experiencia en la interpretación de información territorial y geoespacial. Puede analizar cambios de cobertura vegetal, comparar información de diferentes periodos y orientar la revisión de zonas ambientalmente sensibles.

No debe necesitar conocimientos de programación para ejecutar las funciones principales de la plataforma desde la interfaz web.

### 2.4 Restricciones

- El MVP estará limitado a la Reserva Nacional Tambopata y su zona de amortiguamiento.
- Cada periodo seleccionado debe tener una fecha inicial menor o igual a su fecha final. Un periodo de un solo día es válido.
- Los dos periodos seleccionados deben ser distintos y no deben superponerse.
- El análisis deberá considerar la comparabilidad temporal, la nubosidad, las sombras y la estacionalidad.
- Las zonas candidatas procesadas y mostradas por el MVP deben encontrarse dentro de la Reserva Nacional Tambopata o de su zona de amortiguamiento.
- La información de fuentes externas puede estar incompleta, ser contradictoria o no estar disponible; en esos casos el sistema debe informar la situación y no presentar el análisis como concluido o confirmado.
- Cuando las limitaciones de calidad o comparabilidad sean relevantes, deben registrarse y mostrarse al especialista. Si la evidencia es insuficiente, el resultado no debe presentarse como confirmado.
- Los casos con evidencia insuficiente deberán mantenerse identificados como inciertos y no presentarse como confirmados.
- El acceso al sistema estará restringido a usuarios autenticados.
- La prioridad generada será una recomendación y no sustituirá el criterio profesional.
- El sistema no atribuirá automáticamente la causa ni establecerá la legalidad de un cambio.
- Desde que el usuario solicita un análisis, el sistema debe mostrar un resultado, un estado de procesamiento o un mensaje de error en un máximo de 60 segundos.

## 3. Requerimientos específicos

### 3.1 Requerimientos funcionales

#### RF-01 — Autenticación del usuario

**Descripción:** El sistema debe permitir la autenticación del usuario.

**Origen:** Elicitación con stakeholder y revisión crítica de requerimientos.

**Criterios de aceptación:**

##### RF-01-AC-1

**Dado que** el usuario dispone de datos de autenticación válidos  
**cuando** solicita el acceso al sistema  
**entonces** el sistema autentica al usuario y permite acceder a las funciones protegidas.

##### RF-01-AC-2

**Dado que** el usuario proporciona datos de autenticación inválidos o incompletos  
**cuando** intenta autenticarse  
**entonces** el sistema no concede el acceso autenticado.

#### RF-02 — Selección de periodos de comparación

**Descripción:** El sistema debe permitir seleccionar dos periodos de comparación. Cada periodo debe tener una fecha inicial menor o igual a su fecha final; un periodo de un solo día es válido. Los dos periodos deben ser distintos y no deben superponerse.

**Origen:** Elicitación con stakeholders, revisión crítica de requerimientos y decisión final de revisión humana.

**Criterios de aceptación:**

##### RF-02-AC-1

**Dado que** el usuario está autenticado  
**cuando** selecciona dos periodos de comparación y confirma la selección  
**entonces** el sistema registra ambos periodos como entrada para el análisis.

##### RF-02-AC-2

**Dado que** el usuario no ha seleccionado exactamente dos periodos, alguno de los periodos tiene una fecha inicial posterior a su fecha final, los dos periodos son iguales o los dos periodos se superponen  
**cuando** intenta iniciar el análisis  
**entonces** el sistema no inicia el análisis e informa que la selección temporal no es válida.

#### RF-03 — Identificación de zonas candidatas

**Descripción:** El sistema debe identificar zonas candidatas con cambios de cobertura vegetal. Las zonas candidatas procesadas y mostradas por el MVP deben encontrarse dentro de la Reserva Nacional Tambopata o de su zona de amortiguamiento. Si el análisis no puede concluir debido a información externa indisponible o insuficiente, el sistema debe informar esa situación y no presentar el análisis como concluido o confirmado.

**Origen:** Elicitación con stakeholders y revisión crítica de requerimientos.

**Criterios de aceptación:**

##### RF-03-AC-1

**Dado que** el usuario está autenticado, ha seleccionado dos periodos y existe información disponible para analizarlos  
**cuando** solicita el análisis  
**entonces** el sistema identifica y muestra las zonas candidatas encontradas.

##### RF-03-AC-2

**Dado que** existen dos periodos válidos y el análisis no identifica variaciones que generen zonas candidatas  
**cuando** finaliza el análisis  
**entonces** el sistema informa que no se identificaron zonas candidatas para los periodos analizados.

##### RF-03-AC-3

**Dado que** existen dos periodos válidos y el análisis no puede concluir debido a información externa indisponible o insuficiente  
**cuando** finaliza el procesamiento disponible  
**entonces** el sistema informa la insuficiencia o indisponibilidad y no presenta el análisis como concluido o confirmado.

##### RF-03-AC-4

**Dado que** el análisis identifica y procesa una o más zonas candidatas  
**cuando** el sistema muestra el resultado  
**entonces** todas las zonas candidatas procesadas y mostradas se encuentran dentro de la Reserva Nacional Tambopata o de su zona de amortiguamiento.

##### RF-03-AC-5

**Dado que** existen limitaciones relevantes de calidad o comparabilidad para interpretar el análisis  
**cuando** el sistema muestra el resultado  
**entonces** registra y muestra esas limitaciones al especialista y no presenta el resultado como confirmado si la evidencia es insuficiente.

#### RF-04 — Visualización de zonas en mapa

**Descripción:** El sistema debe visualizar en un mapa la ubicación georreferenciada de las zonas identificadas.

**Origen:** Elicitación con stakeholders y revisión crítica de requerimientos.

**Criterios de aceptación:**

##### RF-04-AC-1

**Dado que** existe una o más zonas identificadas con ubicación georreferenciada  
**cuando** el especialista abre la visualización en mapa  
**entonces** el sistema muestra la ubicación de cada zona identificada.

##### RF-04-AC-2

**Dado que** existen dos zonas candidatas con ubicaciones georreferenciadas diferentes  
**cuando** el sistema muestra el mapa del análisis  
**entonces** cada zona aparece representada en su posición geográfica correspondiente.

#### RF-05 — Consulta del contexto territorial

**Descripción:** El sistema debe mostrar el contexto territorial de cada zona, incluyendo su ubicación respecto a la Reserva Nacional Tambopata, su zona de amortiguamiento y su proximidad a recursos hídricos. Para el MVP, la proximidad hídrica se expresa como la distancia mínima en metros entre el límite de la zona candidata y el recurso hídrico georreferenciado disponible más cercano. Si no existe información georreferenciada disponible, el sistema debe mostrar “Información no disponible” y no presentar una distancia calculada.

**Origen:** Elicitación con stakeholders, alcance aprobado del proyecto, revisión crítica de requerimientos y decisión final de revisión humana.

**Criterios de aceptación:**

##### RF-05-AC-1

**Dado que** el especialista ha seleccionado una zona y existe información territorial disponible  
**cuando** consulta su contexto territorial  
**entonces** el sistema muestra la ubicación de la zona respecto a la Reserva Nacional Tambopata y su zona de amortiguamiento.

##### RF-05-AC-2

**Dado que** existe información georreferenciada de recursos hídricos para la zona seleccionada  
**cuando** el especialista consulta su contexto territorial  
**entonces** el sistema muestra la distancia mínima en metros entre el límite de la zona candidata y el recurso hídrico georreferenciado disponible más cercano.

##### RF-05-AC-3

**Dado que** no existe información georreferenciada de recursos hídricos disponible para la zona seleccionada  
**cuando** el especialista consulta su contexto territorial  
**entonces** el sistema muestra “Información no disponible” y no presenta una distancia calculada.

#### RF-06 — Generación de prioridad sugerida

**Descripción:** El sistema debe generar una prioridad sugerida para orientar el orden de revisión. Si existe al menos un factor de prioridad disponible, la prioridad sugerida debe expresarse mediante uno de los siguientes niveles: Alta, Media o Baja. Si ninguno de los factores definidos dispone de información, la prioridad sugerida debe mostrarse como “No disponible”. Ante la misma información de entrada de una zona, el sistema debe producir el mismo resultado de prioridad sugerida.

**Origen:** Elicitación con stakeholders, revisión crítica de requerimientos y decisión final de revisión humana.

**Criterios de aceptación:**

##### RF-06-AC-1

**Dado que** existe una zona candidata con al menos un factor de prioridad disponible  
**cuando** el sistema genera la prioridad sugerida  
**entonces** la prioridad se expresa únicamente como Alta, Media o Baja.

##### RF-06-AC-2

**Dado que** se proporciona la misma información de una zona en dos ejecuciones del análisis  
**cuando** el sistema genera la prioridad sugerida en ambas ejecuciones  
**entonces** produce el mismo resultado de prioridad en ambas ocasiones; si existe al menos un factor disponible, el resultado es el mismo nivel Alta, Media o Baja, y si no existe ningún factor disponible, el resultado es No disponible.

##### RF-06-AC-3

**Dado que** ninguno de los factores de prioridad definidos dispone de información para una zona candidata  
**cuando** el sistema genera la prioridad sugerida  
**entonces** el sistema muestra No disponible y no asigna los niveles Alta, Media o Baja.

##### RF-06-AC-4

**Dado que** se muestran varias zonas candidatas con prioridades Alta, Media y Baja  
**cuando** el sistema presenta el orden de revisión  
**entonces** muestra primero las zonas con prioridad Alta, después las de prioridad Media y finalmente las de prioridad Baja, sin exigir un orden entre zonas con el mismo nivel.

#### RF-07 — Consulta de factores de prioridad

**Descripción:** El sistema debe mostrar siempre los seis factores de prioridad: extensión del cambio, persistencia temporal, ubicación territorial, proximidad a recursos hídricos, recencia y calidad o incertidumbre de la evidencia. Cuando exista información, debe mostrar el valor del factor; cuando no exista, debe mostrar “No disponible”. Para la recencia, la fecha de referencia es el fin del periodo más reciente seleccionado para el análisis.

**Origen:** Elicitación con stakeholders, revisión crítica de requerimientos y decisión final de revisión humana.

**Criterios de aceptación:**

##### RF-07-AC-1

**Dado que** una zona candidata está siendo revisada  
**cuando** el especialista consulta los factores de prioridad  
**entonces** el sistema muestra siempre las seis categorías extensión del cambio, persistencia temporal, ubicación territorial, proximidad a recursos hídricos, recencia y calidad o incertidumbre de la evidencia, con el valor disponible de cada factor o No disponible cuando no exista información.

##### RF-07-AC-2

**Dado que** uno o más factores de prioridad no disponen de información  
**cuando** el especialista consulta los factores de una zona  
**entonces** el sistema muestra “No disponible” para cada factor sin información, en lugar de omitirlo.

##### RF-07-AC-3

**Dado que** existen dos periodos seleccionados y hay información disponible para calcular la recencia  
**cuando** el especialista consulta los factores de prioridad  
**entonces** el sistema utiliza como fecha de referencia el fin del periodo más reciente seleccionado y no la fecha actual de ejecución.

#### RF-08 — Modificación de prioridad y justificación

**Descripción:** Cuando el especialista modifique la prioridad de una zona candidata dentro de un análisis, el sistema debe conservar la prioridad sugerida originalmente, la prioridad seleccionada por el especialista y la justificación ingresada.

**Origen:** Elicitación con stakeholder ficticio, revisión crítica de requerimientos y decisión final de revisión humana.

**Criterios de aceptación:**

##### RF-08-AC-1

**Dado que** una zona candidata dentro de un análisis tiene una prioridad sugerida  
**cuando** el especialista selecciona una prioridad diferente e ingresa una justificación  
**entonces** el sistema conserva la prioridad sugerida originalmente, la prioridad seleccionada por el especialista y la justificación ingresada.

##### RF-08-AC-2

**Dado que** una zona tiene una prioridad sugerida y el especialista selecciona una prioridad diferente  
**cuando** intenta guardar el cambio sin ingresar una justificación  
**entonces** el sistema no guarda la modificación e informa que la justificación es obligatoria.

##### RF-08-AC-3

**Dado que** se muestran varias zonas candidatas y el especialista modifica la prioridad de una de ellas  
**cuando** guarda la modificación con una justificación  
**entonces** el sistema actualiza el orden mostrado para colocar las zonas Alta antes que las Media y las Media antes que las Baja, sin exigir un orden entre zonas con el mismo nivel.

#### RF-09 — Actualización del estado de revisión

**Descripción:** El sistema debe registrar el estado de revisión de cada zona identificada. Toda nueva zona candidata inicia con el estado Pendiente. Para el MVP, los estados permitidos serán Pendiente, En revisión, Incierto y Revisado, y el especialista podrá cambiar entre ellos sin restricciones adicionales de transición. El sistema debe permitir registrar una observación opcional asociada a la revisión de una zona. Revisado indica que la revisión terminó, pero no significa que el cambio, su causa o su legalidad hayan sido confirmados.

**Origen:** Elicitación con stakeholders, revisión crítica de requerimientos y decisión final de revisión humana.

**Criterios de aceptación:**

##### RF-09-AC-1

**Dado que** una nueva zona candidata ha sido identificada  
**cuando** se registra por primera vez para revisión  
**entonces** el sistema le asigna el estado Pendiente.

##### RF-09-AC-2

**Dado que** una zona tiene cualquiera de los estados permitidos registrado  
**cuando** el especialista actualiza su estado  
**entonces** el sistema permite seleccionar cualquiera de Pendiente, En revisión, Incierto o Revisado y conserva el nuevo estado asociado a la zona, sin restricciones adicionales de transición.

##### RF-09-AC-3

**Dado que** una zona candidata está asociada a una revisión  
**cuando** el especialista registra una observación opcional y guarda la revisión  
**entonces** el sistema conserva la observación asociada a esa zona dentro del análisis que la generó.

#### RF-10 — Almacenamiento de análisis

**Descripción:** Al completar un análisis, el sistema debe almacenarlo automáticamente sin requerir una acción manual adicional. Cada análisis almacenado debe conservar como mínimo la fecha del análisis, los periodos comparados, las fuentes utilizadas y las limitaciones conocidas. Para cada zona candidata dentro del análisis que la generó, debe conservar su prioridad sugerida, la prioridad modificada y su justificación cuando aplique, el estado de revisión y las observaciones registradas. Una ocurrencia similar en un análisis posterior no debe alterar los datos históricos de un análisis anterior.

**Origen:** Elicitación con stakeholders, revisión crítica de requerimientos y decisión final de revisión humana.

**Criterios de aceptación:**

##### RF-10-AC-1

**Dado que** un análisis ha finalizado y tiene una fecha, dos periodos comparados, fuentes utilizadas y limitaciones conocidas  
**cuando** finaliza el análisis  
**entonces** el sistema almacena automáticamente la fecha del análisis, los periodos comparados, las fuentes utilizadas y las limitaciones conocidas sin requerir una acción manual adicional del usuario.

##### RF-10-AC-2

**Dado que** un análisis contiene varias zonas candidatas  
**cuando** el análisis se almacena automáticamente  
**entonces** el sistema conserva para cada zona su prioridad sugerida, su prioridad modificada y justificación cuando aplique, su estado de revisión y sus observaciones dentro del análisis que la generó.

##### RF-10-AC-3

**Dado que** existe un análisis almacenado y un análisis posterior contiene una zona geográficamente similar  
**cuando** el análisis posterior se almacena o se modifica  
**entonces** los datos históricos del análisis anterior permanecen sin cambios.

#### RF-11 — Consulta de análisis anteriores

**Descripción:** El usuario debe poder consultar la lista de análisis almacenados previamente y acceder al detalle de un análisis seleccionado, incluyendo sus limitaciones conocidas y la información asociada a cada zona candidata.

**Origen:** Elicitación con stakeholders y revisión crítica de requerimientos.

**Criterios de aceptación:**

##### RF-11-AC-1

**Dado que** existen análisis almacenados previamente  
**cuando** el usuario consulta los análisis anteriores  
**entonces** el sistema muestra la lista de análisis almacenados.

##### RF-11-AC-2

**Dado que** el usuario visualiza la lista de análisis almacenados  
**cuando** selecciona uno de los análisis  
**entonces** el sistema permite acceder al detalle del análisis seleccionado, incluyendo fecha, periodos comparados, fuentes, limitaciones conocidas y la prioridad, estado, justificación y observaciones de cada zona candidata.

### 3.2 Requerimientos no funcionales

#### RNF-01 — Usabilidad

**Descripción:** Las funciones principales deben poder ejecutarse desde la interfaz web sin que el usuario escriba código, comandos ni consultas geoespaciales manuales.

**Origen:** Elicitación con stakeholder y revisión crítica de requerimientos.

#### RNF-02 — Trazabilidad

**Descripción:** Para cada resultado de análisis, el sistema debe permitir consultar las fuentes utilizadas, los periodos analizados y las limitaciones conocidas registradas.

**Origen:** Elicitación con stakeholders y revisión crítica de requerimientos.

#### RNF-03 — Rendimiento

**Descripción:** Desde que el usuario solicita un análisis, el sistema debe mostrar un resultado, un estado de procesamiento o un mensaje de error en un máximo de 60 segundos.

**Origen:** Elicitación con stakeholder y revisión crítica de requerimientos.

#### RNF-04 — Seguridad

**Descripción:** El acceso al sistema debe estar restringido a usuarios autenticados.

**Origen:** Elicitación con stakeholder y revisión crítica de requerimientos.

#### RNF-05 — Robustez

**Descripción:** Ante la indisponibilidad o insuficiencia de una fuente externa, el sistema debe informar la situación y no presentar el análisis como concluido o confirmado.

**Origen:** Elicitación con stakeholders y revisión crítica de requerimientos.

### 3.3 Requerimientos de dominio

#### RD-01 — Comparabilidad temporal y calidad de la evidencia

**Descripción:** El análisis debe considerar la comparabilidad temporal, la nubosidad, las sombras y la estacionalidad. Cuando estas limitaciones sean relevantes para interpretar el análisis, deben registrarse como limitaciones, mostrarse al especialista y evitar que el resultado se presente como confirmado si la evidencia es insuficiente.

**Origen:** Elicitación con stakeholders y revisión crítica de requerimientos.

#### RD-02 — Tratamiento de casos inciertos

**Descripción:** Los casos con evidencia insuficiente o contradictoria deben mantenerse identificados como inciertos y no presentarse como confirmados.

**Origen:** Elicitación con stakeholders y revisión crítica de requerimientos.

#### RD-03 — No atribución automática de causa o legalidad

**Descripción:** El sistema no debe atribuir automáticamente una causa ni establecer la legalidad de un cambio, incluida la posible minería ilegal.

**Origen:** Alcance aprobado del proyecto, elicitación con stakeholders y revisión crítica de requerimientos.

#### RD-04 — Carácter recomendativo de la prioridad

**Descripción:** La prioridad generada por el sistema debe ser una recomendación y no sustituir el criterio profesional.

**Origen:** Elicitación con stakeholders y revisión crítica de requerimientos.

#### RD-05 — Alcance geográfico del MVP

**Descripción:** El MVP debe limitarse a la Reserva Nacional Tambopata y su zona de amortiguamiento.

**Origen:** Alcance aprobado del proyecto y revisión crítica de requerimientos.