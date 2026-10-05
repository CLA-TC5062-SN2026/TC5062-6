# Registro de la conversación — Parte 3 (Priorización comparada)

**Fecha:** 04/10/2026
**Proyecto:** EcoAlert Tambopata — Equipo 6, TC5062, Gpo 10
**Rol asumido:** Product Owner

---

## Mensaje 1 — Usuario

Comienza la Parte 3. Ahora deberás simular ser un Product Owner, aún no hagas nada adicional.

**Respuesta del asistente:** A partir de ese momento asumí el rol de Product Owner del proyecto EcoAlert Tambopata, encargado de priorizar el backlog, definir el valor de cada funcionalidad para los usuarios (analistas SIG y coordinación), validar que las historias aporten valor de negocio y guiar las decisiones de alcance, alineado con el SRS del equipo.

---

## Mensaje 2 — Usuario

Ahora toma en cuenta el backlog con ajustes. Deberás, según el valor de negocio, ordenar las historias. Justificar por qué algunas van arriba y otras abajo, hasta arriba las que tengan mayor valor de negocio. Justifica por cada bloque, considera 4 bloques de orden.

**Respuesta del asistente:** Ordené las 15 historias en 4 bloques de mayor a menor valor de negocio, con justificación por bloque:

- **Bloque 1 — Máximo valor (núcleo de la decisión del analista):** HU-E4-1 (puntaje explicado), HU-E4-2 (lista priorizada y ajuste), HU-E3-1 (agrupación de alertas), HU-E2-2 (ingesta de alertas GeoBosques), HU-E5-1 (comparación de dos periodos inmutable).
- **Bloque 2 — Alto valor (habilitadores del núcleo y visualización):** HU-E2-1 (carga de capas), HU-E2-3 (frescura de fuentes), HU-E3-2 (mapa con capas), HU-E3-3 (contexto territorial), HU-E4-3 (estados e historial).
- **Bloque 3 — Valor medio (salida, acceso y administración):** HU-E5-2 (exportación), HU-E1-1 (inicio de sesión), HU-E1-2 (gestión de cuentas).
- **Bloque 4 — Valor complementario:** HU-E1-3 (TOTP y bloqueo), HU-E5-3 (bitácora de auditoría).

Justificación general: primero el flujo central de valor (priorización explicada sobre zonas agrupadas, desde alertas reales, con comparación de periodos), luego habilitadores y visualización, después salidas y administración, y al final seguridad reforzada y auditoría (ambas Should en el SRS).

---

## Mensaje 3 — Usuario

Exporta estos 4 bloques en un prioriza.md.

**Respuesta del asistente:** Se creó el archivo:

`C:\Users\sauza\OneDrive\Escritorio\Maestría\12_Análisis, diseño y construcción de software\03_Semana\prioriza.md`

con los 4 bloques de priorización y sus justificaciones.

---

## Mensaje 4 — Usuario

Se analizó la propuesta del agente. Se destaca lo siguiente:

> Al comparar la priorización realizada por el equipo con la propuesta del agente actuando como Product Owner, observamos que existe una coincidencia general en las funcionalidades consideradas importantes, aunque cambia el orden en que deberían atenderse.
>
> El equipo asignó prioridad Alta a la mayoría de las historias relacionadas con el funcionamiento principal de EcoAlert. Sin embargo, el agente realizó una distinción adicional dentro de este grupo, colocando primero las funcionalidades que generan directamente el valor principal del sistema. Por esta razón, HU-E4-1 (puntaje de prioridad), HU-E4-2 (lista priorizada) y HU-E3-1 (agrupación de alertas) aparecen en los primeros lugares. Consideramos razonable este criterio, ya que estas historias permiten identificar qué zonas deberían revisarse primero y explicar el motivo.
>
> Una diferencia que identificamos está en historias como HU-E1-1 (inicio de sesión) y HU-E1-2 (gestión de cuentas). Para el equipo ambas tienen prioridad Alta porque son necesarias para operar el sistema de forma controlada. El agente también reconoce su importancia, pero las coloca en las posiciones 12 y 13 debido a que las considera habilitadores técnicos y no funcionalidades que aporten directamente al análisis ambiental. Esta diferencia nos permitió distinguir entre una funcionalidad necesaria para que el sistema opere y una funcionalidad que representa directamente valor para el usuario.
>
> Algo similar ocurre con HU-E5-2 (exportación de lista y zonas). El equipo la clasificó como Alta por su utilidad para continuar el análisis en herramientas como QGIS o en hojas de cálculo, mientras que el agente la ubicó en la posición 11. Su argumento es que la exportación ocurre después de que el sistema ya realizó sus funciones principales de ingesta, agrupación, contextualización y priorización. Consideramos que ambas perspectivas son válidas, aunque para una primera versión del producto resulta razonable priorizar primero el flujo principal.
>
> Finalmente, existe mayor coincidencia en las historias HU-E1-3 (TOTP y bloqueo) y HU-E5-3 (bitácora de auditoría), que el equipo había clasificado con prioridad Media y el agente colocó en las últimas posiciones. Estas funcionalidades aportan seguridad y trazabilidad, pero no impiden realizar el flujo principal de análisis de EcoAlert.
>
> En conclusión, la comparación no mostró contradicciones importantes entre ambas propuestas. La principal diferencia fue el criterio utilizado: el equipo priorizó considerando qué funcionalidades son necesarias para contar con un producto completo, mientras que el agente puso mayor énfasis en el valor de negocio y en entregar primero el flujo central de EcoAlert. A partir de esta comparación consideramos útil conservar las prioridades Alta y Media del backlog, pero utilizar el orden propuesto por el Product Owner como referencia para decidir qué historias deberían desarrollarse primero. Solo toma estos comentarios en cuenta.

**Respuesta del asistente:** Confirmé que tomo en cuenta los comentarios como criterio de trabajo:

- Se conserva la prioridad Alta/Media del backlog (`backlog.md`).
- El orden de los bloques del Product Owner (`prioriza.md`) se usa como referencia para decidir qué historias desarrollar primero.
- Criterio adoptado: distinguir entre funcionalidades necesarias para operar un producto completo (visión del equipo) y las que entregan primero el valor de negocio central (visión del PO), sin contradicciones entre ambas.

---

## Mensaje 5 — Usuario

Ahora desde que comenzó la parte, transcríbela y expórtala en un archivo priorizacion_comparada.md.

**Respuesta del asistente:** Se exportó esta transcripción en:

`C:\Users\sauza\OneDrive\Escritorio\Maestría\12_Análisis, diseño y construcción de software\03_Semana\priorizacion_comparada.md`
