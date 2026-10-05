# Registro de la conversación — Parte 1 (Ajustes de backlog)

**Fecha:** 04/10/2026
**Proyecto:** EcoAlert Tambopata — Equipo 6, TC5062, Gpo 10

---

## Mensaje 1 — Usuario

Inicio de la Parte 1. Te comparto el SRS del equipo `C:\Users\sauza\OneDrive\Escritorio\Maestría\12_Análisis, diseño y construcción de software\03_Semana\SRS_equipo.md`. No hagas nada, solo consideralo.

**Respuesta del asistente:** Leí el SRS completo y presenté un resumen en contexto:

- **Proyecto:** EcoAlert Tambopata — app web de apoyo al monitoreo de pérdida de cobertura forestal en la RN Tambopata y su zona de amortiguamiento.
- **Stack:** Backend Python 3.12 + FastAPI, PostgreSQL 17 + PostGIS, Frontend React 19 + TypeScript, Docker Compose en un VPS.
- **Roles:** Analista SIG (operativo) y Coordinación (consulta + gestión de usuarios). Permisos rechazados se responden 403 en servidor.
- **Alcance:** RF-01 a RF-39. Must = RF-01 a RF-17 (MVP), Should = RF-18–RF-26 y RF-34–RF-37, Could = RF-27–RF-33, RF-38, RF-39.
- **Núcleo Must:** autenticación y sesión (30 min), gestión de usuarios, carga de capas de referencia (RF-03), ingesta de alertas GeoBosques (RF-04), agrupación en zonas (RF-05, 500 m / 90 días), mapa con capas (RF-06), frescura de fuentes (RF-07), contexto territorial (RF-08), priorización explicada de 5 factores (RF-09), lista priorizada (RF-10), ajuste manual de prioridad (RF-11), estados e historial (RF-12), marcas de confianza (RF-13), comparación de dos periodos inmutable (RF-14), consulta de análisis (RF-15), exportación CSV (RF-16) y GeoJSON (RF-17).
- **Convenciones clave:** IDs congelados en v1.0, criterios `RF-XX-AC-Y` inmutables y trazables, parámetros PS-01 a PS-15, temas abiertos TA-01 a TA-05, sin titulares mineros (RD-04), sin causas ni legalidad (RD-02), análisis nunca "concluido" si la evidencia es insuficiente (RNF-08).

---

## Mensaje 2 — Usuario

Identifica las épicas del proyecto (grupos de funcionalidad de alto nivel). Debes proponer 5 épicas.

**Respuesta del asistente:** Propuesta de 5 épicas:

| # | Épica | Descripción | RF incluidos |
|---|---|---|---|
| E1 | Acceso seguro y administración de usuarios | Permitir el ingreso autenticado con sesión con expiración, gestión de cuentas por coordinación, segundo factor TOTP y bloqueo por intentos. | RF-01, RF-02, RF-25 |
| E2 | Ingesta de datos y frescura de fuentes | Cargar capas de referencia y alertas de GeoBosques con validación de formato/SRC, ingesta acumulativa de alertas, frescura de fuentes y sincronización RADD (mejora). | RF-03, RF-04, RF-07, RF-19, RF-35 |
| E3 | Zonas de cambio y visualización territorial | Agrupar alertas en zonas persistentes, mostrar mapa con capas, contexto territorial (reserva, ZA, catastro, ríos), zonas manuales y reapertura/fusión (mejoras). | RF-05, RF-06, RF-08, RF-20, RF-26, RF-28, RF-30 |
| E4 | Priorización y seguimiento de revisión | Calcular prioridad explicada de 5 factores, lista priorizada, ajuste manual justificado, estados con historial, marcas de confianza, observaciones y responsable de zona. | RF-09, RF-10, RF-11, RF-12, RF-13, RF-21, RF-29, RF-34, RF-36, RF-39 |
| E5 | Análisis de periodos y exportación | Comparar alertas de dos periodos con análisis inmutables, consultar análisis anteriores, exportar la lista y las zonas en varios formatos, fichas PDF, bitácora de auditoría y comparación visual de imágenes. | RF-14, RF-15, RF-16, RF-17, RF-18, RF-22, RF-23, RF-24, RF-27, RF-31, RF-32, RF-33, RF-37, RF-38 |

Criterios de agrupación: cada épica corresponde a un flujo de valor reconocible (acceso → datos → zonas → priorización/revisión → análisis/salida); las funcionalidades Should/Could se asignaron a la épica de mayor valor.

---

## Mensaje 3 — Usuario

Ahora, para cada épica genera historias de usuario en el formato estándar:

    Como [tipo de usuario], quiero [acción/funcionalidad], para [beneficio/valor].

**Respuesta del asistente:** Se generaron historias de usuario por épica (E1: 8 HU, E2: 8 HU, E3: 8 HU, E4: 12 HU, E5: 11 HU), cada una en el formato estándar, con referencia a sus RF.

---

## Mensaje 4 — Usuario

En total deben ser 15 historias. Cada historia debe incluir:

    Criterios de aceptación (mínimo 2 por historia)

    Estimación inicial en Story Points (usando la escala Fibonacci: 1, 2, 3, 5, 8, 13)

    Prioridad: Alta / Media / Baja

**Respuesta del asistente:** Se consolidaron 15 historias (3 por épica), cada una con:

- Criterios de aceptación (mínimo 2, formato Dado-Cuando-Entonces).
- Estimación en Story Points (Fibonacci).
- Prioridad Alta/Media/Baja.

Resumen de estimaciones: HU-E3-1, HU-E4-1, HU-E5-1 con 13 SP; HU-E1-3, HU-E2-1, HU-E2-2, HU-E3-2, HU-E4-2, HU-E4-3 con 8 SP; HU-E1-1, HU-E1-2, HU-E3-3, HU-E5-2, HU-E5-3 con 5 SP; HU-E2-3 con 3 SP.

---

## Mensaje 5 — Usuario

Esas épicas que tienen sus historias, con sus componentes, criterios de aceptación, estimación inicial en story point, y prioridad. Expórtalos en un .md llamado backlog.

**Respuesta del asistente:** Se creó el archivo:

`C:\Users\sauza\OneDrive\Escritorio\Maestría\12_Análisis, diseño y construcción de software\03_Semana\backlog.md`

con las 5 épicas y las 15 historias de usuario (criterios, SP, prioridad).

---

## Mensaje 6 — Usuario

Se revisó las épicas exportadas. En base a eso podrías realizar los siguientes ajustes, y el nuevo backlog exportarlo:

1. Agregar una descripción breve a cada épica indicando qué integra. Por ejemplo: objetivo de la épica, funcionalidades que agrupa y/o RF relacionados. Actualmente aparecen los nombres E1–E5, pero se pasa directamente a las historias.
2. Agregar trazabilidad con el SRS a cada historia. Incluir RF relacionados: RF-XX, RF-YY, verificando que cada funcionalidad provenga realmente de SRS_equipo.md.
3. Revisar algunas estimaciones de Story Points. En particular, valorar HU-E5-1 de 13 → 8 SP y HU-E5-2 de 5 → 8 SP, ya que la segunda contempla varios formatos de exportación, reproyección y control de permisos.
4. Ajustar criterios para que sean precisos y automatizables. Por ejemplo, en HU-E2-3 sustituir "respecto de hoy" por "respecto de la fecha actual del sistema", evitando expresiones dependientes del contexto y facilitando las pruebas.

**Respuesta del asistente:** Se actualizó `backlog.md` aplicando los cuatro ajustes:

1. Descripción breve en cada épica (objetivo, funcionalidades agrupadas, RF relacionados).
2. Trazabilidad SRS en cada historia (`RF relacionados: RF-XX`).
3. HU-E5-1: 13 → 8 SP; HU-E5-2: 5 → 8 SP.
4. HU-E2-3-CA2: "respecto de hoy" → "respecto de la fecha actual del sistema".

---

## Mensaje 7 — Usuario

Desde que inició la parte 1. Transcribe la conversación, y expórtala en un ajustes_backlog.md.

**Respuesta del asistente:** Se exportó esta transcripción en:

`C:\Users\sauza\OneDrive\Escritorio\Maestría\12_Análisis, diseño y construcción de software\03_Semana\ajustes_backlog.md`
