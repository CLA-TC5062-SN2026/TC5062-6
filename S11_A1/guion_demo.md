# Guion del video de demo (`demo_proyecto.mp4`)

**EcoAlert Tambopata · Equipo 6 · S11-A1, Parte 4** · Duración objetivo: **4:40** (máximo 5:00), una sola toma sin
cortes. Miguel maneja el teclado durante todo el video; los cuatro narran por turnos.

Para "Excelente", la rúbrica pide un video de 5 minutos o menos con **los 5 segmentos**, el **sistema funcionando con
datos reales** y una **narración que conecte el problema con lo que se ve en pantalla**. Por eso cada parlamento de la
demo dice qué se ve y para qué le sirve al analista.

| Integrante | Segmentos | Tiempo al micrófono |
|---|---|---|
| Daniel Medina Vargas | 1 · Problema y contexto; 5 · Qué haríamos diferente | ≈ 55 s |
| Miguel Ángel Arévalo Andrade | 2a · Demo: acceso, panel y alertas (y teclado en todo el video) | ≈ 65 s |
| Anthony Gerardo Gutarra Sánchez | 2b · Demo: CRUD de cuentas y caso de error | ≈ 105 s |
| Eduardo Daniel Sauza Machado | 3 · Decisión técnica clave; 4 · Uso del agente de IA | ≈ 55 s |

El reparto es una propuesta: si el equipo cambia quién dice qué, solo hay que respetar los tiempos.

## 1. Antes de grabar

| ✔ | Verificación (las cuatro primeras las pide la tarea) | Cómo |
|---|---|---|
| ☐ | Backend y frontend levantados y comunicándose sin errores de CORS | `gh codespace ssh -c <nombre> -- 'cd /workspaces/TC5062-6 && bash .devcontainer/levantar.sh'` termina con `SPA → API: OK`, y el puerto 4173 está **público** (`gh codespace ports visibility 4173:public -c <nombre>`; vuelve a privado cada vez que el Codespace se reinicia). Abrir la URL pública → *Continue* en el aviso de GitHub → carga el login. La API va por el mismo origen (`/api/v1`), así que no puede haber CORS. |
| ☐ | Usuario de demo creado y con datos reales cargados | Iniciar sesión como Coordinación: el **Panel** muestra 24 alertas, 6 zonas y 30.28 ha. |
| ☐ | Sin errores en la consola del navegador | DevTools → Console con "Preserve log", limpiar antes de empezar. Solo deben aparecer los dos errores provocados: el 401 del login fallido y el 409. Cerrar DevTools antes de grabar. |
| ☐ | El micrófono se escucha con claridad | Cada narrador graba 10 s y se escucha. |
| ☐ | Solo una cuenta de Coordinación activa | En **Usuarios**, solo `coordinacion@ecoalert.pe` tiene rol Coordinación y está Activa (si no, el 409 no aparece). |
| ☐ | La cuenta que se crea no existe | Usar `luis.condori@ecoalert.pe`; si ya se usó en un ensayo, `luis.condori.2@ecoalert.pe`, etc. Las cuentas no se borran. |
| ☐ | Pestañas listas | Pestaña 1: la aplicación. Pestaña 2: el README en GitHub, en **§3 Arquitectura** (diagrama). Pestaña 3: `S11_A1/retrospectiva_proyecto.md`, en **A.4**. Pestaña 4: `S11_A1/matriz_trazabilidad.md`, en **§2 Resumen**. |
| ☐ | Ventana | 1280 × 800 o más, zoom 110 %, sin marcadores personales, notificaciones del sistema ocultas. La contraseña de Coordinación no se lee en voz alta ni se muestra. |
| ☐ | Ensayo | Recorrer el guion completo una vez con cronómetro. Es el mismo flujo que automatiza `evidencias/flujo_e2e.cjs`. |

## 2. Guion

### 0:00–0:30 · Problema y contexto — Daniel

**En pantalla:** la pantalla de login de EcoAlert, sin tocar nada.

> "En la Reserva Nacional Tambopata, los analistas SIG reciben cada semana las alertas oficiales de pérdida de bosque de
> GeoBosques y tienen que decidir qué zona revisar primero cruzando varias herramientas. EcoAlert Tambopata es la
> aplicación web que reúne esas alertas agrupadas por zona de cambio, con acceso por roles. Hoy entrega el acceso seguro,
> la administración de cuentas y la consulta de alertas por zona. El cálculo automático de prioridad todavía no está
> construido, y lo explicamos al final."

### 0:30–1:35 · Demo 1: acceso, panel y alertas — Miguel (teclado y voz)

| Tiempo | En pantalla | Qué dice Miguel |
|---|---|---|
| 0:30–0:50 | Escribir `/dashboard` en la barra de direcciones → redirige al login. Ingresar `coordinacion@ecoalert.pe` con una contraseña incorrecta → *Ingresar*. | "Sin sesión, cualquier pantalla lleva al login. Con una contraseña incorrecta, el servidor responde 401 con un mensaje genérico que no revela si el correo existe." |
| 0:50–1:15 | Escribir la contraseña correcta → *Ingresar* → **Panel**. Señalar las cifras y la tabla. | "La coordinadora entra al panel. Son datos reales guardados en PostGIS: 24 alertas de GeoBosques en 6 zonas de cambio, 30.28 hectáreas alertadas. La tabla responde la primera pregunta del analista: dónde se concentra la pérdida. La zona 101 suma 12.40 hectáreas, el 41 % de todo lo alertado. Ojo: está ordenada por superficie, todavía no por una prioridad calculada." |
| 1:15–1:35 | Pulsar `EA-2026-101` → **Alertas** filtradas a esa zona. Señalar `GB-2026-0004` (Ausente). Pulsar el segmento *Ausentes* y luego *Todas*. | "Al pulsar la zona veo sus cuatro alertas. Tres siguen presentes en la última carga y una ya no vino en el archivo de GeoBosques, algo que el analista necesita saber antes de planear la visita a campo." |

### 1:35–3:20 · Demo 2: CRUD de cuentas y caso de error — Anthony

El recurso que el sistema administra completo, de alta a baja, son las **cuentas**: las alertas se consultan, no se
editan.

| Tiempo | En pantalla | Qué dice Anthony |
|---|---|---|
| 1:35–1:50 | Pestaña **Usuarios**: lista con Carmen (Analista SIG) y Rosa (Coordinación). | "Coordinación administra quién puede ver estas alertas. Esta es la lista: el rol se distingue por color y cada cuenta muestra si está activa." |
| 1:50–2:25 | *Nueva cuenta* → `Luis Condori Mamani`, `luis.condori@ecoalert.pe`, *Analista SIG*, contraseña temporal `corta` → *Crear cuenta* → error. Cambiarla por `Malinowski-Temporal-26` → *Crear cuenta*. | "Doy de alta a un analista de la brigada del río Malinowski. Si la contraseña temporal tiene menos de 12 caracteres, la interfaz la rechaza antes de llamar al servidor. Con una válida, la cuenta aparece en la lista marcada con contraseña temporal: deberá cambiarla en su primer ingreso." |
| 2:25–2:45 | *Editar* en la fila de Luis → nombre `Luis Condori Mamani (Brigada Malinowski)` → *Guardar*. | "Editar envía al servidor solo los campos que cambiaron." |
| 2:45–3:05 | *Desactivar* en la fila de Rosa (tu cuenta) → *Desactivar cuenta* → aparece "No se puede desactivar la última cuenta de coordinación". Pulsar *Cancelar*. | "Este es el caso de error. Si intento desactivar la única cuenta de Coordinación, el servidor lo impide con un 409 y la interfaz explica el motivo: el sistema se quedaría sin nadie que administre las cuentas." |
| 3:05–3:20 | *Desactivar* en la fila de Luis → *Desactivar cuenta* → estado *Desactivada*. | "No hay botón de eliminar: las cuentas se desactivan, porque el historial de cada zona debe conservar quién hizo cada revisión. Al desactivarla, sus sesiones abiertas se cierran al instante." |

### 3:20–3:50 · Decisión técnica clave — Eduardo

**En pantalla:** pestaña 2, el diagrama de arquitectura del README (§3).

> "Nuestra decisión clave fue no usar un JWT puramente sin estado. Cada token lleva un identificador de sesión guardado en
> PostgreSQL, y en cada petición el backend comprueba que esa sesión siga abierta, que no lleve más de 30 minutos
> inactiva y que la cuenta siga activa. Por eso, como acaban de ver, desactivar una cuenta o cerrar sesión invalida el
> token en ese momento, y no cuando expira. Lo exigen los criterios RF-01-AC-6 y RF-02-AC-5."

### 3:50–4:15 · Uso del agente de IA — Eduardo

**En pantalla:** pestaña 3, la tabla A.4 de la retrospectiva.

> "El agente fue más útil en las fases de mucho volumen con reglas claras: el contrato OpenAPI y más de doscientas pruebas
> automatizadas. Pero también escribió pruebas que pasaban sin verificar nada, y solo lo descubrimos rompiendo el código
> a propósito. Revisar lo generado nos costó más que generarlo."

### 4:15–4:40 · Qué haríamos diferente — Daniel

**En pantalla:** pestaña 4, el resumen de la matriz de trazabilidad (2 completos, 4 parciales, 33 no implementados).

> "La limitación real es que el núcleo del producto no está construido: la carga de alertas desde un archivo, la
> agrupación automática en zonas y el cálculo de su prioridad. Por eso la matriz marca 2 requerimientos completos de 39.
> Pusimos primero la seguridad y la administración. Con más tiempo haríamos primero un flujo vertical simple, de la carga
> a la lista priorizada, aunque fuera rudimentario, y después lo reforzaríamos."

Holgura: 20 s. Si el ensayo pasa de 4:45, recortar la explicación de la alerta ausente (1:15–1:35).

## 3. Después de grabar

1. Exportar como `demo_proyecto.mp4` (H.264, 1080p o 720p) y comprobar que dura 5:00 o menos.
2. Si pesa **menos de 100 MB**, copiarlo a `S11_A1/demo_proyecto.mp4` y subirlo con un commit en una rama y un pull
   request. Los videos anteriores del repositorio pesan hasta 67 MB, así que 5 minutos a 720p suelen caber.
3. Si pesa **100 MB o más**, subirlo a YouTube (no listado) o a Google Drive con acceso por enlace, y crear
   `S11_A1/demo_link.txt` con la URL en una sola línea.
4. Comprobar que el video se reproduce desde GitHub, o desde el enlace en una ventana de incógnito.
5. Incluir el video (o `demo_link.txt`) en el .zip de Canvas.
