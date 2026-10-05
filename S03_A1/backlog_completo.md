# Backlog de Producto — EcoAlert Tambopata

> Equipo 6 — TC5062, Gpo 10. Épicas, historias de usuario, criterios de aceptación, estimación en Story Points (Fibonacci) y prioridad.

---

## E1: Acceso seguro y administración de usuarios

**Descripción:** Garantiza que solo usuarios autenticados accedan al sistema y que la coordinación administre las cuentas. Agrupa: inicio de sesión y expiración por inactividad, gestión de usuarios y roles, y segundo factor TOTP con bloqueo por intentos.
**RF relacionados:** RF-01, RF-02, RF-25.

### HU-E1-1 — Inicio de sesión y expiración
**Como** usuario registrado, **quiero** iniciar sesión con usuario y contraseña y que mi sesión expire por inactividad, **para** acceder de forma segura a las funciones de mi rol.

- **CA1:** Dado un usuario con credenciales correctas, cuando inicia sesión, entonces el sistema crea la sesión y permite acceder según su rol.
- **CA2:** Dado que la contraseña es incorrecta o el usuario no existe, cuando intenta iniciar sesión, entonces responde 401 con "Usuario o contraseña incorrectos" sin crear sesión.
- **CA3:** Dado un usuario con 31 minutos de inactividad, cuando hace una nueva solicitud, entonces responde 401.

**RF relacionados:** RF-01 | **SP:** 5 | **Prioridad:** Alta

### HU-E1-2 — Gestión de cuentas por coordinación
**Como** coordinación, **quiero** crear, editar y desactivar cuentas con rol y contraseña temporal, **para** administrar el acceso sin eliminar la autoría en el historial.

- **CA1:** Dado que coordinación crea una cuenta con contraseña temporal de 12 caracteres, cuando confirma, entonces la cuenta queda activa con ese rol.
- **CA2:** Dado que la contraseña temporal tiene 11 caracteres, cuando se envía, entonces se rechaza indicando el mínimo de 12.
- **CA3:** Dado una sola cuenta activa de coordinación, cuando se intenta desactivar, entonces se rechaza la operación.

**RF relacionados:** RF-02 | **SP:** 5 | **Prioridad:** Alta

### HU-E1-3 — Verificación extra y bloqueo
**Como** usuario, **quiero** un segundo factor TOTP y bloqueo por intentos fallidos, **para** proteger mi cuenta ante accesos no autorizados.

- **CA1:** Dado un usuario con TOTP enrolado, cuando inicia sesión sin código válido, entonces el acceso se rechaza.
- **CA2:** Dado 5 intentos fallidos consecutivos, cuando ocurre el quinto, entonces la cuenta se bloquea 15 minutos aunque la contraseña sea correcta.

**RF relacionados:** RF-25 | **SP:** 8 | **Prioridad:** Media

---

## E2: Ingesta de datos y frescura de fuentes

**Descripción:** Hace posible cargar los datos geográficos que alimentan el sistema y conocer su vigencia. Agrupa: carga de capas de referencia con validación de formato y SRC, ingesta acumulativa de alertas GeoBosques, y visibilidad de la fecha de corte y alertas de desactualización.
**RF relacionados:** RF-03, RF-04, RF-07.

### HU-E2-1 — Carga de capas de referencia
**Como** analista SIG, **quiero** cargar capas de referencia (reserva, ZA, ríos, catastro) con fuente y fecha de corte obligatorias, **para** que los cálculos usen datos vigentes y trazables.

- **CA1:** Dado un Shapefile .zip con .prj en EPSG:4326, cuando se carga como catastro minero con fuente y fecha de corte, entonces el sistema lo acepta y almacena geometría en EPSG:32719.
- **CA2:** Dado que falta la fuente o la fecha de corte, cuando se envía la carga, entonces se rechaza y no se crea ninguna versión.
- **CA3:** Dado un archivo .kml o sin .prj, cuando se intenta cargar, entonces se rechaza indicando los formatos aceptados.

**RF relacionados:** RF-03 | **SP:** 8 | **Prioridad:** Alta

### HU-E2-2 — Ingesta acumulativa de alertas GeoBosques
**Como** analista SIG, **quiero** ingerir alertas de GeoBosques de forma acumulativa, sin duplicados y descartando las fuera del ámbito, **para** mantener un historial completo y limpio.

- **CA1:** Dado un archivo con 120 alertas (5 fuera del ámbito), cuando termina la carga, entonces se ingieren 115 y el resumen indica "5 alertas fuera del ámbito".
- **CA2:** Dado 200 alertas ingeridas y un archivo nuevo con 150 repetidas y 30 nuevas, cuando se carga, entonces hay 230 alertas, 30 nuevas, 150 existentes y 50 marcadas "no presente en la última carga".
- **CA3:** Dado una carga con fecha de corte anterior a la última, cuando se ingiere, entonces las alertas nuevas sí se incorporan.

**RF relacionados:** RF-04 | **SP:** 8 | **Prioridad:** Alta

### HU-E2-3 — Frescura de fuentes visible
**Como** cualquier usuario, **quiero** ver la fecha de corte de cada fuente y un aviso cuando las alertas superen 30 días sin actualizarse, **para** no interpretar datos viejos como actuales.

- **CA1:** Dado cortes 10/09/2026 y 20/09/2026, cuando consulto el panel de capas, entonces "Alertas de GeoBosques" muestra "20/09/2026".
- **CA2:** Dado un último corte con más de 30 días respecto de la fecha actual del sistema, cuando consulto la lista o el panel, entonces se muestra "Alertas de GeoBosques posiblemente desactualizadas (corte dd/mm/aaaa)".
- **CA3:** Dado una capa nunca cargada, cuando consulto el panel, entonces muestra "Sin datos cargados".

**RF relacionados:** RF-07 | **SP:** 3 | **Prioridad:** Alta

---

## E3: Zonas de cambio y visualización territorial

**Descripción:** Convierte las alertas en entidades de trabajo persistentes y las muestra en un mapa con su contexto. Agrupa: agrupación de alertas en zonas, mapa con capas activables y selección de zona, y contexto territorial (superposiciones, distancia a ríos, sin titulares).
**RF relacionados:** RF-05, RF-06, RF-08.

### HU-E3-1 — Agrupación de alertas en zonas
**Como** analista SIG, **quiero** que las alertas se agrupen automáticamente en zonas de cambio persistentes, **para** trabajar con entidades estables en el tiempo.

- **CA1:** Dado dos alertas a 300 m y 10 días de diferencia, cuando se ejecuta la agrupación, entonces quedan en la misma zona.
- **CA2:** Dado una alerta compatible con una zona a 400 m y otra a 200 m, cuando se agrupa, entonces se agrega a la más cercana y ambas zonas siguen existiendo.
- **CA3:** Dado que se agrega una cuarta alerta, cuando se recalcula la zona, entonces pasa a 4 alertas y se actualizan área y puntaje.

**RF relacionados:** RF-05 | **SP:** 13 | **Prioridad:** Alta

### HU-E3-2 — Mapa con capas y detalle
**Como** analista SIG, **quiero** un mapa con capas activables y selección de zona, **para** explorar el territorio y abrir el detalle sin buscar en listas.

- **CA1:** Dado un usuario autenticado, cuando solicita la lista de capas, entonces contiene exactamente: límite de RN Tambopata, ZA, ríos, catastro minero, alertas de GeoBosques y zonas de cambio.
- **CA2:** Dado la capa "Catastro minero" activa, cuando se desactiva, entonces sus elementos dejan de mostrarse sin recargar la página.
- **CA3:** Dado la capa de zonas activa, cuando selecciono EA-2026-014, entonces se abre su detalle.

**RF relacionados:** RF-06 | **SP:** 8 | **Prioridad:** Alta

### HU-E3-3 — Contexto territorial de la zona
**Como** analista SIG, **quiero** ver las superposiciones (reserva, ZA, catastro sin titulares) y la distancia al río más cercano, **para** contextualizar cada zona.

- **CA1:** Dado una zona que cruza una concesión y la ZA, cuando consulto su contexto, entonces se listan con tipo de derecho, código, estado y nombre/código, sin titular.
- **CA2:** Dado que no hay superposiciones, cuando consulto el contexto, entonces se muestra "No hay superposiciones".
- **CA3:** Dado que no hay capa de ríos, cuando consulto el contexto, entonces muestra "Información no disponible" y ninguna distancia.

**RF relacionados:** RF-08 | **SP:** 5 | **Prioridad:** Alta

---

## E4: Priorización y seguimiento de revisión

**Descripción:** Define qué zonas revisar primero y cómo se documenta su revisión. Agrupa: puntaje de prioridad explicado con 5 factores, lista priorizada con ajuste manual justificado, y estados de revisión con historial cronológico.
**RF relacionados:** RF-09, RF-10, RF-11, RF-12.

### HU-E4-1 — Puntaje de prioridad explicado
**Como** analista SIG, **quiero** un puntaje 0–100 con desglose visible de 5 factores, **para** decidir qué zonas revisar primero y por qué.

- **CA1:** Dada una zona con factores conocidos, cuando se calcula con PS-03, entonces el desglose muestra los 5 aportes y el puntaje/nivel correctos (p. ej., 75, "alta").
- **CA2:** Dado que no hay capa de ríos, cuando se calcula, entonces cercanía a ríos muestra "No disponible" y el puntaje se reescala.
- **CA3:** Dado el mismo dato, misma versión de capas y misma FR, cuando se recalcula, entonces el resultado es idéntico.

**RF relacionados:** RF-09 | **SP:** 13 | **Prioridad:** Alta

### HU-E4-2 — Lista priorizada y ajuste manual
**Como** analista SIG, **quiero** ver la lista ordenada por prioridad vigente y ajustarla con justificación obligatoria, **para** reflejar mi criterio experto.

- **CA1:** Dada una zona con puntajes 40, 85 y 72, cuando abro la lista, entonces aparecen en orden 85, 72, 40.
- **CA2:** Dado puntaje calculado 45 y ajuste de 80 con justificación, cuando se muestra, entonces aparece "80 (ajustado; calculado 45)" y nivel "alta".
- **CA3:** Dado un ajuste sin justificación, cuando se confirma, entonces se rechaza y el puntaje vigente no cambia.

**RF relacionados:** RF-10, RF-11 | **SP:** 8 | **Prioridad:** Alta

### HU-E4-3 — Estados e historial de revisión
**Como** analista SIG, **quiero** cambiar el estado de una zona con comentario/motivo obligatorio y ver su historial, **para** dar trazabilidad al proceso de revisión.

- **CA1:** Dado una zona en "nueva", cuando pasa a "descartada" con motivo, entonces se acepta y el historial registra el motivo.
- **CA2:** Dado una zona en "en revisión", cuando intento pasarla a "revisada" sin comentario, entonces se rechaza y el estado no cambia.
- **CA3:** Dado una zona con cambios de estado, ajuste y marca, cuando consulto su historial, entonces veo las tres acciones en una lista cronológica con tipo, usuario, fecha y hora.

**RF relacionados:** RF-12 | **SP:** 8 | **Prioridad:** Alta

---

## E5: Análisis de periodos y exportación

**Descripción:** Permite analizar la evolución en el tiempo y sacar la información del sistema. Agrupa: comparación de dos periodos con análisis inmutables y consulta de análisis anteriores, exportación de la lista y de las zonas en varios formatos con control de permisos, y bitácora de auditoría de solo inserción.
**RF relacionados:** RF-14, RF-15, RF-16, RF-17, RF-37, RF-24.

### HU-E5-1 — Comparación de dos periodos inmutable
**Como** usuario, **quiero** comparar las alertas de cada zona en dos periodos y que el análisis se guarde inmutable, **para** tener evidencia trazable de la evolución.

- **CA1:** Dado periodos 01/06–30/06 y 01/08–31/08, cuando ejecuto la comparación, entonces A = junio y B = agosto.
- **CA2:** Dado periodos superpuestos o idénticos, cuando intento ejecutarla, entonces se rechaza con mensaje claro.
- **CA3:** Dado un análisis almacenado con puntaje 62, cuando la zona pasa a 80, entonces el análisis sigue mostrando 62.

**RF relacionados:** RF-14, RF-15 | **SP:** 8 | **Prioridad:** Alta

### HU-E5-2 — Exportación de lista y zonas
**Como** analista SIG, **quiero** exportar la lista filtrada a CSV y las zonas a GeoJSON/Shapefile, **para** trabajarlas en QGIS o en hojas de cálculo.

- **CA1:** Dada la lista con 5 zonas filtradas, cuando exporto a CSV, entonces el archivo tiene esas 5 en el mismo orden, UTF-8 con BOM y las 10 columnas definidas.
- **CA2:** Dada una zona exportada de 3.50 ha, cuando se reproyecta y se mide en EPSG:32719, entonces el área redondeada es 3.50.
- **CA3:** Dado que coordinación solicita exportar, cuando invoca la API, entonces responde 403 y no entrega archivo.

**RF relacionados:** RF-16, RF-17, RF-37 | **SP:** 8 | **Prioridad:** Alta

### HU-E5-3 — Bitácora de auditoría
**Como** coordinación, **quiero** consultar una bitácora de solo inserción de eventos del sistema, **para** supervisar el uso y auditar acciones.

- **CA1:** Dado que un analista exportó la lista a CSV, cuando consulto la bitácora, entonces hay un registro con formato, número de zonas, usuario y fecha/hora.
- **CA2:** Dado un registro existente, cuando se intenta editar o borrar por API o por el usuario de BD de la app, entonces la operación no existe o es rechazada.

**RF relacionados:** RF-24 | **SP:** 5 | **Prioridad:** Media


---

## Justificación de las estimaciones en Story Points

Las estimaciones se realizaron utilizando la escala de Fibonacci (1, 2, 3, 5, 8 y 13). Para asignar los puntos se consideró de manera relativa la complejidad de la lógica, las validaciones necesarias, la integración con datos o componentes externos y la incertidumbre técnica. Los Story Points no representan horas de trabajo, sino una comparación del esfuerzo esperado entre las historias del backlog.

### HU-E1-1 — Inicio de sesión y expiración — 5 SP
Requiere autenticación, manejo de sesiones, permisos por rol y control de expiración por inactividad. Es una funcionalidad conocida, pero incluye varias validaciones de seguridad.

### HU-E1-2 — Gestión de cuentas por coordinación — 5 SP
Incluye crear, editar y desactivar usuarios, validar roles y contraseñas, además de impedir la desactivación de la única cuenta activa de coordinación.

### HU-E1-3 — Verificación extra y bloqueo — 8 SP
Agrega TOTP, control de intentos fallidos y bloqueo temporal. Tiene mayor complejidad que el inicio de sesión básico por las reglas adicionales de seguridad.

### HU-E2-1 — Carga de capas de referencia — 8 SP
Requiere recibir archivos geográficos, validar formato y proyección, registrar fuente y fecha de corte y transformar la geometría a EPSG:32719.

### HU-E2-2 — Ingesta acumulativa de alertas GeoBosques — 8 SP
Debe detectar duplicados, descartar alertas fuera del ámbito, mantener información acumulativa y distinguir alertas nuevas, existentes y ausentes en la última carga.

### HU-E2-3 — Frescura de fuentes visible — 3 SP
Utiliza información de fechas ya almacenada y aplica reglas sencillas para mostrar la última fecha de corte, advertencias de más de 30 días o ausencia de datos.

### HU-E3-1 — Agrupación de alertas en zonas — 13 SP
Es una de las historias con mayor complejidad porque requiere lógica espacial y temporal para agrupar alertas, resolver coincidencias entre zonas y recalcular información cuando llegan nuevas alertas.

### HU-E3-2 — Mapa con capas y detalle — 8 SP
Implica visualizar varias capas geográficas, activarlas o desactivarlas y permitir la interacción con las zonas para consultar su detalle.

### HU-E3-3 — Contexto territorial de la zona — 5 SP
Requiere consultar superposiciones y distancia al río más cercano. La lógica geoespacial existe, pero su alcance es menor que el de la agrupación completa de zonas.

### HU-E4-1 — Puntaje de prioridad explicado — 13 SP
Es una funcionalidad central que combina cinco factores, reglas de cálculo, reescalamiento cuando falta información y resultados reproducibles. Tiene alta lógica de negocio y varias condiciones que validar.

### HU-E4-2 — Lista priorizada y ajuste manual — 8 SP
Incluye ordenar por prioridad, permitir ajustes manuales, conservar el valor calculado y exigir una justificación para modificar la prioridad vigente.

### HU-E4-3 — Estados e historial de revisión — 8 SP
Requiere controlar cambios de estado, validar comentarios o motivos y mantener un historial cronológico con usuario, fecha y tipo de acción.

### HU-E5-1 — Comparación de dos periodos inmutable — 8 SP
Debe validar periodos, comparar información temporal y guardar resultados que no cambien aunque posteriormente se modifique la zona.

### HU-E5-2 — Exportación de lista y zonas — 8 SP
Incluye diferentes formatos de salida, conservación de filtros y orden, reproyección y medición geográfica, además del control de permisos para exportar.

### HU-E5-3 — Bitácora de auditoría — 5 SP
Requiere registrar eventos con sus datos principales y garantizar que los registros no puedan modificarse o eliminarse desde la aplicación.

En general, las historias de 3 puntos corresponden a funciones más acotadas y con reglas simples; las de 5 puntos tienen una complejidad intermedia; las de 8 puntos requieren varias validaciones, integraciones o procesamiento adicional; y las de 13 puntos concentran la mayor complejidad e incertidumbre técnica del backlog.

