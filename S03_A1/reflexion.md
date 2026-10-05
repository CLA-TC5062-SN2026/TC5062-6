# Reflexión

## 1. ¿Qué ventajas y riesgos tiene utilizar IA para generar el Product Backlog?

Una de las principales ventajas que encontramos al utilizar inteligencia
artificial para generar el Product Backlog es que permite partir de la
información del SRS y organizarla de una manera más rápida. En nuestro
caso, el agente pudo tomar los requerimientos de EcoAlert Tambopata y
proponer épicas, historias de usuario, criterios de aceptación,
prioridades y Story Points. Esto nos permitió tener una primera versión
del backlog sin tener que comenzar completamente desde cero.

Otra ventaja es que la IA puede ayudar a encontrar relaciones entre los
diferentes requerimientos. Por ejemplo, algunos requerimientos
relacionados con la carga de información, las zonas de cambio o la
priorización podían agruparse dentro de una misma épica. Esto nos ayudó
a entender que los requerimientos del SRS no necesariamente se
convierten directamente en historias de usuario, sino que primero es
necesario analizar qué funcionalidad representan y qué valor tienen para
el usuario.

Sin embargo, también encontramos algunos riesgos. El principal es
aceptar directamente todo lo que genera la IA sin revisarlo. El agente
puede proponer una historia que no corresponda completamente con el SRS,
agregar detalles que no fueron solicitados o realizar una estimación que
no represente correctamente la dificultad de la historia. Por esta razón
fue necesario revisar el backlog y realizar algunos ajustes, por ejemplo
en los Story Points, en algunos criterios de aceptación y en la
trazabilidad con los requerimientos.

Por lo tanto, consideramos que la IA es útil para generar una primera
propuesta y ahorrar tiempo, pero el equipo debe revisar el resultado
antes de considerarlo como definitivo.

## 2. ¿Puede el agente reemplazar al Product Owner? Argumenta tu respuesta.

Consideramos que el agente puede apoyar bastante el trabajo de un
Product Owner, pero no puede reemplazarlo completamente. Durante la
actividad observamos que el agente pudo analizar las historias de
usuario y ordenarlas de acuerdo con el valor de negocio. Incluso pudo
explicar por qué algunas historias deberían desarrollarse antes que
otras.

Por ejemplo, el agente consideró que las historias relacionadas con el
puntaje de prioridad, la lista priorizada y la agrupación de alertas
representan una parte central de EcoAlert. Esto tiene sentido porque el
objetivo principal del sistema es ayudar al analista a identificar qué
zonas debería revisar primero. También colocó más abajo historias
relacionadas con administración, seguridad adicional y auditoría, porque
aunque son importantes, no representan directamente la función principal
del sistema.

Sin embargo, un Product Owner no solamente ordena historias. También
debe conocer las necesidades reales de los usuarios, entender las
decisiones del negocio, hablar con los interesados y tomar decisiones
cuando existen diferentes opiniones. La IA solamente puede trabajar con
la información que se le proporciona. Si el SRS o el backlog no
contienen suficiente información, el agente podría tomar una decisión
que parezca lógica, pero que no necesariamente sea la mejor decisión
para el proyecto.

Por eso consideramos que el agente funciona mejor como una herramienta
de apoyo para el Product Owner. Puede ayudar a analizar información,
generar propuestas y encontrar posibles inconsistencias, pero la
decisión final debe seguir siendo responsabilidad de las personas
involucradas en el proyecto.

## 3. ¿Cómo afecta la calidad del SRS a la calidad del backlog generado?

La calidad del SRS afecta directamente la calidad del Product Backlog
porque el backlog se construye utilizando los requerimientos definidos
anteriormente. Si los requerimientos están bien escritos, son claros y
tienen criterios de aceptación específicos, es mucho más sencillo
convertirlos en historias de usuario.

Esto lo pudimos observar en EcoAlert, ya que el SRS del equipo tenía
requerimientos identificados mediante RF y también tenía criterios de
aceptación. Gracias a esto, el agente pudo relacionar las historias del
backlog con requerimientos específicos. Después de revisar el backlog
también agregamos explícitamente los RF relacionados a cada historia, lo
que permitió tener una trazabilidad más clara entre el SRS y el Product
Backlog.

Por otro lado, si el SRS tuviera requerimientos ambiguos,
contradictorios o incompletos, esos mismos problemas probablemente
pasarían al backlog. Una historia de usuario podría quedar demasiado
general o sus criterios de aceptación podrían no ser verificables.
Incluso la IA podría completar información por su cuenta para cubrir lo
que no está definido, generando funcionalidades que realmente no fueron
solicitadas.

Por esta razón consideramos que el SRS funciona como una base para las
siguientes etapas del proyecto. Mientras más claro y consistente sea el
SRS, más sencillo será generar un backlog que represente lo que
realmente se quiere construir. La IA puede ayudar a transformar esa
información, pero la calidad del resultado sigue dependiendo en gran
parte de la calidad de la información que se le proporciona.
