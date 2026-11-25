# Retrospectiva del proyecto y consistencia problema-solución

**EcoAlert Tambopata · Equipo 6 · TC5062 · S11-A1, Parte 3**

Documento elaborado con asistencia de un agente de IA (Claude Code) a partir de la evidencia del repositorio: commits,
documentos de cada semana, resultados de las pruebas y la [matriz de trazabilidad](matriz_trazabilidad.md). Cada
afirmación cita su fuente. Las opiniones del equipo están marcadas como tales.

---

## Sección A — Retrospectiva SCRUM

### A.1 ¿Qué salió bien?

| # | Qué | Evidencia |
|---|---|---|
| 1 | **Requerimientos verificables desde el inicio.** Consolidamos cuatro SRS individuales en uno, con 30 conflictos resueltos (C-01 a C-30) y criterios de aceptación con ID inmutable (`RF-XX-AC-Y`) en formato Dado-Cuando-Entonces. Gracias a eso, la matriz de esta actividad se pudo construir criterio por criterio. | `S03_A1/SRS_equipo.md`, `S03_A1/diferencias_SRS.md` |
| 2 | **Contrato primero.** El contrato OpenAPI define las 39 operaciones del MVP y cubre los 166 criterios Must. Una prueba verifica que cada ruta montada está en el contrato y que no hay rutas fuera de él, así que el código no puede alejarse del diseño sin que falle la suite. | `backend/docs/openapi_integrado.yaml`, `backend/tests/test_contrato.py` |
| 3 | **Seguridad tomada en serio y medida.** JWT con sesión revocable en la base, expiración por inactividad, Argon2id, errores RFC 9457 sin filtrar detalles internos, idempotencia con HMAC y control de acceso en el servidor en todas las rutas. La revisión de seguridad registró 15 hallazgos con su corrección y su prueba. | `S05_S06_A2/revision_seguridad.md` |
| 4 | **Pruebas contra la base real, no contra simulaciones.** 234 pruebas de backend sobre PostgreSQL 17 + PostGIS, con bases `_test` separadas que el código se niega a confundir con la de desarrollo. Incluye pruebas de concurrencia (diez altas simultáneas con el mismo correo dan un 201 y nueve 409). | `S11_A1/evidencias/pytest_backend.txt`, `backend/tests/test_api_usuarios.py` |
| 5 | **Honestidad técnica.** Ninguna operación pendiente se simuló como implementada; el alcance real (20 de 39 operaciones) está escrito en el README del backend desde S06, y la auditoría de S09 no afirmó vulnerabilidades que no pudo demostrar. | `backend/README.md` §Alcance, `S09_A1/clasificacion_problemas.md` |
| 6 | **Frontend con una capa de servicios limpia.** Un solo cliente HTTP con interceptores (JWT, 401 global, tiempo máximo, traducción de errores) hizo que agregar la gestión de usuarios en S11 fuera casi solo escribir la página. | `S07_S08_A2/capa_servicios.md`, `frontend/src/services/` |

### A.2 ¿Qué no salió bien?

| # | Qué | Evidencia | Consecuencia |
|---|---|---|---|
| 1 | **El Sprint Goal del Sprint 1 no se cumplió.** Comprometimos cargar capas de referencia e ingerir alertas (HU-E2-1 y HU-E2-2, 16 SP). Ninguna de las dos se construyó. | `S03_A2/sprint1_planning.md` §4; matriz: RF-03 y RF-04 ❌/🟡 | El núcleo del producto (zonas, prioridad, mapa) depende de esas dos historias y quedó bloqueado. |
| 2 | **El backlog dejó de guiar el trabajo.** Desde S05 trabajamos según la actividad de cada semana (CRUD, autenticación, frontend, calidad) y no según el orden del Product Owner. No hubo un Sprint 2 planificado ni una revisión del backlog. | No existe un `sprint2_planning.md`; las carpetas `S05`–`S09` siguen las actividades, no las HU | Construimos con mucha calidad lo que menos valor aportaba al analista (bloque 3 del PO) y nada del bloque 1. |
| 3 | **Alcance sobredimensionado.** El SRS tiene 39 RF y 166 criterios Must para un equipo con 8–9 h por semana por persona. El propio SRS dice que el núcleo Must "debe poder construirse por un equipo de tres personas", y no lo verificamos al estimar. | `S03_A1/SRS_equipo.md` §2.4; `S03_A2/sprint1_planning.md` §5 | Ya en el Sprint 1 la capacidad (≈ 2.8 h/SP) mostraba que el MVP no cabía en el curso. |
| 4 | **Dos implementaciones en paralelo.** A1 y A2 construyeron dos backends con contratos distintos, ambos rotulados "1.2.0". Unirlos costó una integración con 8 discrepancias, y las colecciones Postman originales dejaron de funcionar. | `backend/docs/integracion.md` §2, §4 y §5 | El esfuerzo se fue en reconciliar versiones en lugar de avanzar el backlog. |
| 5 | **Desvíos del stack acordado sin registrarlos.** El SRS fija React + **TypeScript** y despliegue con Docker Compose en un VPS. El frontend quedó en JavaScript y Docker Compose solo levanta la base; no hubo un registro de cambio. | `S03_A1/SRS_equipo.md` §2.1; `frontend/src/*.jsx`; `backend/docker-compose.yml` | Los acuerdos de la línea base dejaron de ser confiables como fuente de verdad. |
| 6 | **Sin integración continua.** Nunca configuramos CI; las pruebas corrían solo en la máquina de quien las ejecutaba. | `S09_A1/deuda_tecnica.md` ("No se encontró un directorio `.github/workflows`") | Un bug de interfaz (siguiente punto) y enlaces rotos llegaron a `main`. |
| 7 | **Defectos que se detectaron tarde.** En S11, la prueba E2E mostró que, tras cerrar sesión, la siguiente cuenta que iniciaba sesión en la pestaña caía en la última página de la cuenta anterior. También faltaba la prueba de RF-02-AC-6 y `S09_A1` enlaza archivos que no se subieron. | Commit `feat(frontend)…` de S11; matriz §5, H-2 y H-4 | Se corrigieron en S11, pero muestran que las pruebas unitarias no cubrían flujos entre usuarios. |
| 8 | **Despliegue en la última semana.** La aplicación no estuvo accesible fuera de una laptop hasta S11. | `.devcontainer/` creado en S11 | No pudimos mostrar el producto a nadie ajeno al equipo durante el desarrollo. |

### A.3 ¿Qué haríamos diferente la próxima vez?

1. **Construir primero un esqueleto vertical del flujo de valor**: subir un archivo de alertas → agruparlo en zonas →
   calcular un puntaje simple → verlo en una lista. Aunque cada paso fuera rudimentario, habría validado la arquitectura
   geoespacial y habría dado al analista algo útil desde el Sprint 1. La autenticación robusta podía esperar a que hubiera
   algo que proteger.
2. **Recortar el MVP con datos, no con intuición.** Con la capacidad medida en el Sprint 1 (≈ 2.8 h/SP), el MVP
   realista eran unas 5 historias. Habríamos movido a *Should* todo lo que no fuera ingesta → zonas → prioridad → lista.
3. **Una sola rama de backend y un solo contrato desde el día uno**, con PR obligatorio y revisión cruzada, en lugar de
   que cada actividad produjera su versión.
4. **CI desde el primer commit**: GitHub Actions con un servicio PostGIS, `pytest`, `vitest`, la prueba de contrato y
   `npm run build`. Habría bloqueado los enlaces rotos y el bug de navegación.
5. **Mapear cada actividad del curso a historias del backlog** antes de empezarla, para que el trabajo semanal hiciera
   avanzar el Sprint Goal y no compitiera con él.
6. **Desplegar en la semana 1** (aunque fuera un Codespace) y registrar en `diferencias_SRS.md` cada desvío de la línea
   base, como el de TypeScript.

### A.4 Uso de herramientas agentes durante el proyecto

Usamos agentes de IA en todas las fases. En el repositorio quedó registrado Claude (Claude Code): más de 20 commits llevan su
coautoría. Las herramientas que cada integrante usó fuera del repositorio no se registraron. La tabla resume dónde
aportaron y dónde generaron trabajo extra, con evidencia de cada caso.

| Fase | Dónde fue más útil | Dónde generó trabajo adicional | Evidencia |
|---|---|---|---|
| Requisitos (S02–S03) | Consolidar cuatro SRS: detectó 30 conflictos y propuso una numeración única. Generó la primera versión del backlog en minutos. | Propuso historias y criterios que no estaban en el SRS y estimaciones que hubo que corregir. Omitió una historia para RF-13 (Must) y nadie lo notó hasta S11. | `S03_A1/reflexion.md` §1; `S03_A1/borradores/`; matriz H-1 |
| Planeación (S03-A2) | Vio la cadena de dependencias (capas → ingesta → zonas → prioridad) que el orden por valor del PO ocultaba. | Su propuesta entregaba el sprint solo por `/docs` de FastAPI, sin interfaz para un usuario que no programa, y con una capacidad optimista. El equipo hizo 6 ajustes. | `S03_A2/sprint1_planning.md` §7 |
| Diseño (S05) | Generar el esquema SQL, el contrato OpenAPI y los diagramas UML de forma coherente entre sí (62 schemas ↔ 62 clases). | El SQL y el código generados tenían 14 errores que se corrigieron antes de ejecutarlos (C-01 a C-14). | `backend/docs/antecedentes_main_A1/revision_sql.md` |
| Construcción backend (S05–S06) | Implementar JWT, sesiones, idempotencia y pruebas parametrizadas sobre todas las rutas. | 5 de los 15 hallazgos de seguridad los **introdujo el propio agente**: un error 500 con contraseñas de más de 72 bytes (H-03), un canal lateral de tiempo (H-10) y, el más grave, **pruebas que pasaban sin verificar nada** (H-11, H-12). | `S05_S06_A2/revision_seguridad.md`, origen "Agente" |
| Frontend (S07–S08) | Generar los componentes y la capa de servicios con manejo de errores completo. | La primera versión de los componentes no era accesible (sin asociación de etiquetas, sin foco visible) y hubo que revisarla. | `S07_S08_A1/revision_componentes.md`, `accesibilidad.md` |
| Calidad (S09) | Clasificar 216 diagnósticos de flake8 y mypy sin exagerar su severidad, y proponer refactorizaciones acotadas con pruebas. | Los documentos enlazan archivos de salida que nunca se subieron. | `S09_A1/`, matriz H-4 |
| Cierre (S11) | Construir la gestión de usuarios y el cambio de contraseña con 12 pruebas nuevas (11 de frontend y 1 de backend), una prueba E2E que encontró un bug real de navegación y la prueba faltante de RF-02-AC-6, y desplegar con un script reproducible. | Durante el despliegue, el agente cometió errores que costaron varios intentos: sesiones ssh que no terminaban por procesos que heredaban la terminal, y un `pkill` cuyo patrón coincidía con su propio comando y cerró la sesión dos veces. | Este documento; `.devcontainer/levantar.sh` (historial de commits) |

**¿En qué fases fueron más útiles?** En las de **volumen con reglas claras**: consolidar documentos largos, generar un
contrato coherente con el esquema y escribir pruebas parametrizadas. Ahí el agente hizo en horas lo que nos habría
tomado días, y la trazabilidad con IDs le daba un criterio objetivo para comprobarse.

**¿En cuáles generaron trabajo adicional?** En las que exigen **juicio sobre el usuario o sobre la verificación**: el
agente optimizó para "que funcione la API" en vez de "que el analista pueda usarlo" (S03-A2), y escribió pruebas que
parecían rigurosas pero no probaban nada (H-11). El costo no fue escribir el código, sino revisarlo. Aprendimos a exigir
pruebas de mutación: romper el código a propósito y confirmar que la prueba falla.

**¿Cambió nuestra forma de programar?** *(Opinión del equipo.)* Sí. Pasamos de escribir código a **especificar y
revisar**: el trabajo valioso se movió al SRS, al contrato y a la revisión crítica de lo generado. También subió nuestro
estándar. Con un agente, escribir pruebas, documentación y justificaciones cuesta poco, así que dejó de haber excusa para
no hacerlo. El riesgo que vimos es el contrario: producir mucho artefacto bien redactado sobre poco producto funcionando.
Eso es parte de lo que nos pasó (A.2, puntos 1 y 2).

---

## Sección B — Consistencia problema-solución

### B.1 ¿La aplicación resuelve el problema planteado en la Semana 2?

**Todavía no.** El problema de la Semana 2 era: *ayudar a los analistas SIG a identificar qué zonas de cambio de
cobertura requieren revisión prioritaria, con contexto territorial y sin determinar causas*
([`S03_A1/insumos/proyecto_base.md`](../S03_A1/insumos/proyecto_base.md)). Lo construido resuelve las **condiciones
previas** de ese problema, pero no su núcleo:

| Necesidad del problema | ¿Resuelta? | Evidencia concreta |
|---|---|---|
| Solo personal autorizado accede a la información y cada rol hace solo lo que le corresponde | ✅ Sí | Login con mensaje genérico, redirección sin sesión, 403 en el servidor y menú por rol. Capturas [`01-login.png`](capturas/01-login.png) y [`02-panel-coordinacion.png`](capturas/02-panel-coordinacion.png); RF-01 y RF-02 ✅ en la matriz. |
| La coordinación administra quién trabaja en el sistema sin perder la autoría del historial | ✅ Sí | Gestión de usuarios con baja lógica y regla de la última Coordinación. Capturas [`04-usuarios-creado.png`](capturas/04-usuarios-creado.png), [`05-error-ultima-coordinacion.png`](capturas/05-error-ultima-coordinacion.png) y [`07-usuario-desactivado.png`](capturas/07-usuario-desactivado.png). |
| El analista consulta las alertas oficiales y a qué zona pertenecen | 🟡 Parcialmente | Consulta paginada con filtros por zona y presencia en la última carga ([`03-alertas.png`](capturas/03-alertas.png)), pero las alertas **no se pueden cargar** desde el sistema. |
| Las alertas se agrupan en zonas que persisten en el tiempo | ❌ No | RF-05 sin implementar. |
| Cada zona tiene una prioridad explicada para decidir qué revisar primero | ❌ No | RF-09 y RF-10 sin implementar: es **el valor principal** del proyecto. |
| Contexto territorial (reserva, ZA, catastro minero sin titulares, ríos) | ❌ No | RF-03, RF-06 y RF-08 sin implementar. |
| Comparar periodos y registrar la revisión | ❌ / 🟡 | RF-14 sin implementar; historial, marcas y ajustes solo se pueden **consultar** (RF-11 a RF-13 🟡). |

Lo que sí es consistente con el problema es el **diseño**. Las restricciones de dominio que hacían delicado el caso
están en el SRS, en el contrato y en el esquema: no determinar causas ni legalidad (RD-02), nunca guardar titulares
mineros (RD-04), conservar las fuentes oficiales sin modificar (RD-06) y no presentar un análisis como concluido si la
evidencia es insuficiente (RNF-08). Ninguna decisión de lo construido las contradice. Por ejemplo, el historial
distingue al autor "Sistema" del analista, y las cuentas no se borran para conservar la autoría.

### B.2 ¿Qué partes del problema no se resolvieron?

| Parte no resuelta | ¿Fuera de alcance u obstáculo? | Explicación |
|---|---|---|
| RF-18 a RF-39 (imágenes satelitales, RADD, TOTP, PDF, bitácora, etc.) | **Fuera de alcance** por decisión | Son *Should* y *Could*; el SRS las dejaba para después del núcleo. |
| Ingesta, agrupación, prioridad, mapa, contexto, comparación y exportación (RF-03 a RF-10, RF-14 a RF-17) | **Obstáculo de planificación, no técnico** | No encontramos un impedimento técnico: PostGIS, el esquema y el contrato ya los soportan. El obstáculo fue la capacidad (A.2, punto 3) sumada a que el trabajo siguió las actividades semanales y no el backlog (A.2, punto 2). La lógica espacial de RF-05 (13 SP) era además la de mayor incertidumbre técnica y nunca llegamos a enfrentarla. |
| Escrituras de revisión (cambios de estado, ajustes, marcas) | **Obstáculo de dependencia** | Las tablas y las lecturas existen, pero estas operaciones actúan sobre zonas, y las zonas no se generan sin la ingesta. |
| Validación con usuarios reales | **Fuera de alcance del curso** | Todas las entrevistas de S02 fueron simuladas (SRS, tema abierto TA-04); los pesos de la prioridad están sin calibrar (TA-01). |

### B.3 ¿Qué demostraríamos primero al stakeholder y por qué?

Al **analista SIG** de la Semana 2 le mostraríamos primero la **consulta de alertas agrupadas por zona con datos de su
propio ámbito**, y enseguida el **contrato del desglose de prioridad** (los cinco factores de RF-09 con sus pesos),
aunque el cálculo todavía no exista.

**Por qué:**

1. **Es lo más cercano a su trabajo diario que funciona de punta a punta.** El login y la gestión de cuentas son
   necesarios, pero no son la razón por la que usaría la herramienta. Empezar por ahí mostraría lo que construimos, no lo
   que él necesita.
2. **Su opinión cambia lo que construiríamos después.** Las entrevistas fueron simuladas (TA-04) y los pesos de la
   prioridad son preliminares (TA-01). Una hora con el analista revisando qué factores pesan más y si la agrupación de
   500 m / 90 días tiene sentido en el terreno vale más que cualquier funcionalidad nueva, porque evita construir mal
   el núcleo.
3. **Es honesto.** Mostrar primero lo que resuelve su problema, aunque esté incompleto, deja claro qué falta y nos
   permite pedirle que priorice con nosotros el siguiente incremento (ingesta → zonas → prioridad).

A la **coordinación** sí le mostraríamos primero la gestión de usuarios y la separación de permisos: es su función en
el sistema (SRS §2.3) y hoy está completa.
