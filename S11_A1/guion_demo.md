# Guion del video de demo (`demo_proyecto.mp4`)

**EcoAlert Tambopata · Equipo 6 · S11-A1, Parte 4** · Duración objetivo: **4:30** (máximo 5:00), una sola toma sin
cortes. Una persona maneja el teclado; las demás narran por turnos (A, B, C y D).

## 1. Antes de grabar (checklist)

| ✔ | Verificación | Cómo |
|---|---|---|
| ☐ | Codespace encendido y servicios arriba | `gh codespace ssh -c <nombre> -- 'cd /workspaces/TC5062-6 && bash .devcontainer/levantar.sh'` debe terminar con `SPA → API: OK` |
| ☐ | Backend y frontend se comunican sin CORS | Abrir la URL pública → *Continue* en el aviso de GitHub → la pantalla de login carga. Toda la API va por el mismo origen (`/api/v1`), así que no puede haber errores de CORS. |
| ☐ | Datos reales cargados | Iniciar sesión como Coordinación → **Alertas** muestra "24 alertas encontradas" (6 zonas EA-2026-101 a 106) |
| ☐ | Cuenta de Coordinación única activa | En **Usuarios**, solo `coordinacion@ecoalert.pe` tiene rol Coordinación y estado Activa (si no, el error 409 de la demo no aparece) |
| ☐ | El correo que se va a crear no existe | Usar uno nuevo en cada ensayo (`luis.condori.<n>@ecoalert.pe`); las cuentas no se borran |
| ☐ | Consola del navegador limpia | DevTools → Console, "Preserve log" activo, limpiar antes de empezar. Solo deben aparecer los dos errores provocados (401 del login fallido y 409). |
| ☐ | Ventana | Navegador a 1280 × 800 o más, zoom 110 %, sin pestañas ni marcadores personales; ocultar notificaciones del sistema |
| ☐ | Audio | Probar el micrófono de cada narrador 10 s y escuchar la grabación |
| ☐ | Ensayo | Recorrer el guion una vez completo con cronómetro. El flujo es el mismo que automatiza `evidencias/flujo_e2e.cjs`. |

Cuentas: `coordinacion@ecoalert.pe` y la contraseña de demo, que **no** debe verse en pantalla (escribirla con el
campo enmascarado y no leerla en voz alta).

## 2. Guion

| Tiempo | Segmento | Quién | En pantalla | Qué se dice |
|---|---|---|---|---|
| 0:00–0:30 | **Problema y contexto** | A | Pantalla de login de EcoAlert | "En la Reserva Nacional Tambopata, los analistas SIG reciben cada semana cientos de alertas oficiales de pérdida de bosque y tienen que decidir, cruzando varias herramientas, qué zona revisar primero. EcoAlert Tambopata es la aplicación web que les da ese punto de partida común: hoy, acceso seguro por roles, la administración de cuentas y la consulta de alertas por zona. La prioridad automática todavía no está construida, y lo diremos al final." |
| 0:30–0:55 | Demo · protección de rutas y error de login | B | Escribir `/dashboard` en la barra → redirige al login. Ingresar `coordinacion@ecoalert.pe` con una contraseña incorrecta. | "Sin sesión, cualquier pantalla redirige al login. Con una contraseña incorrecta, el servidor responde 401 con un mensaje genérico que no revela si el correo existe." |
| 0:55–1:20 | Demo · login y alertas | B | Login correcto → Panel → **Alertas**; filtrar zona `EA-2026-101`; mostrar la columna *Última carga* | "Ya con sesión, la coordinadora ve las 24 alertas de GeoBosques de seis zonas, guardadas en PostGIS. Puede filtrarlas por zona y ver cuáles no vinieron en la última carga." |
| 1:20–2:10 | Demo · CRUD: crear y leer | C | **Usuarios** → formulario *Nueva cuenta*: `Luis Condori Mamani`, `luis.condori.<n>@ecoalert.pe`, Analista SIG, contraseña temporal. Primero una de 5 caracteres (error de validación), luego una válida. | "El recurso principal que administra Coordinación son las cuentas. Creo un analista para la brigada del río Malinowski. Si la contraseña temporal tiene menos de 12 caracteres, la interfaz lo rechaza antes de llamar al servidor. Con una válida, la cuenta aparece en la lista, marcada con 'contraseña temporal'." |
| 2:10–2:35 | Demo · CRUD: actualizar | C | *Editar* la cuenta nueva → nombre `Luis Condori Mamani (Brigada Malinowski)` → *Guardar* | "Editar envía un PATCH solo con los campos que cambiaron." |
| 2:35–3:00 | Demo · **caso de error manejado** | C | *Desactivar* la propia cuenta de Coordinación → *Confirmar* → aparece "No se puede desactivar la última cuenta de coordinación" | "Si intento desactivar la única cuenta de Coordinación, el servidor lo impide con un 409 y la interfaz muestra el motivo: el sistema se quedaría sin nadie que administre las cuentas." |
| 3:00–3:30 | Demo · CRUD: baja lógica | C | *Desactivar* la cuenta de Luis → *Confirmar* → estado "Desactivada" | "No hay botón de eliminar: las cuentas se desactivan, porque el historial de cada zona debe conservar quién hizo cada revisión. Al desactivarla, sus sesiones abiertas se cierran al instante." |
| 3:30–4:00 | **Decisión técnica clave** | D | `backend/app/dependencies.py` (función `autenticar`) o el diagrama del README | "Nuestra decisión clave fue no usar un JWT puramente sin estado. Cada token tiene un identificador de sesión guardado en PostgreSQL, y en cada petición comprobamos que esa sesión siga abierta, que no lleve más de 30 minutos inactiva y que la cuenta siga activa. Por eso cerrar sesión o desactivar una cuenta invalida el token en el momento, que es lo que exigen los criterios RF-01-AC-6 y RF-02-AC-5." |
| 4:00–4:20 | **Uso del agente de IA** | A | Tabla A.4 de `retrospectiva_proyecto.md` | "El agente fue más útil generando el contrato OpenAPI y más de doscientas pruebas automatizadas. Pero también escribió pruebas que pasaban sin verificar nada, y solo lo descubrimos rompiendo el código a propósito: revisar lo generado nos costó más que generarlo." |
| 4:20–4:45 | **Qué haríamos diferente** | B | Matriz de trazabilidad, §2 Resumen | "La limitación real es que el núcleo del producto, agrupar alertas en zonas y calcular su prioridad, no está construido: pusimos primero la seguridad y la administración. Con más tiempo haríamos primero un flujo vertical simple de ingesta, zonas, prioridad y lista, aunque fuera rudimentario, y después lo reforzaríamos." |

Holgura: 15 s. Si el ensayo pasa de 4:45, acortar el segmento de alertas (0:55–1:20).

## 3. Después de grabar

1. Exportar como `demo_proyecto.mp4` (H.264, 1080p o 720p).
2. Si pesa **menos de 100 MB**, copiarlo a `S11_A1/demo_proyecto.mp4` y subirlo con un commit. Los videos anteriores
   del repositorio pesan hasta 67 MB, así que 5 minutos a 720p suelen caber.
3. Si pesa **100 MB o más**, subirlo a YouTube (no listado) o a Google Drive con acceso por enlace, y crear
   `S11_A1/demo_link.txt` con la URL en una sola línea.
4. Comprobar que el video se reproduce desde GitHub o desde el enlace en una ventana de incógnito.
