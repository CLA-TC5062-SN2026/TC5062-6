# Paso a paso: levantar el backend y grabar `pruebas_auth.mp4`

Guía para quien grabe el video de S05-S06-A2, desde una computadora sin nada instalado.
Tiempo estimado: 30–40 min la primera vez (la mayor parte son descargas).

**Lo que pide el profesor para el video:** máximo **1 minuto**, **continuo (sin cortes)**, desde **Postman**,
mostrando en este orden:

1. `POST /auth/register` — registro exitoso → **201**
2. `POST /auth/login` — login exitoso → **200** con el token JWT visible
3. `GET /auth/me` — con el token del paso 2 en `Authorization: Bearer` → **200**
4. Ruta CRUD protegida con token válido → **200**
5. La misma ruta sin token → **401**
6. La misma ruta con un token de rol incorrecto → **403**

En cada petición deben verse la **URL**, el **header o body** relevante y el **código de respuesta con el JSON**.
Se permiten pausas breves; no se permiten cortes de edición.

> En nuestro proyecto, `register` solo lo puede usar Coordinación (RF-02 del SRS), por eso el paso 1 lleva el
> token de Coordinación. La ruta CRUD de los pasos 4–6 es `GET /api/v1/usuarios`, que es solo de Coordinación:
> con el token del analista responde 403. La justificación está en `revision_seguridad.md` (D-01).

Los comandos vienen en dos versiones: **macOS / Linux** (Terminal) y **Windows** (PowerShell).

---

## 1. Instalar las herramientas

| Herramienta | Para qué | Dónde |
|---|---|---|
| **Git** | Clonar el repositorio | <https://git-scm.com/downloads> (en macOS ya viene, o `xcode-select --install`) |
| **Docker Desktop** | Base de datos PostgreSQL + PostGIS | <https://www.docker.com/products/docker-desktop/> |
| **Python 3.12** | Ejecutar la API | <https://www.python.org/downloads/> (en Windows marca *"Add python.exe to PATH"*) |
| **Postman (app de escritorio)** | Hacer las peticiones del video | <https://www.postman.com/downloads/> — la versión web no llega a `localhost` sin instalar su agente |
| **Grabador de pantalla** | Grabar el video | macOS: `Cmd + Shift + 5` · Windows: `Win + Alt + R` (Xbox Game Bar) o OBS Studio |

Después de instalar Docker Desktop, **ábrelo** y espera a que diga *"Engine running"*.

Comprueba la instalación:

```bash
git --version
docker --version
python3 --version      # Windows: py -3.12 --version
```

---

## 2. Clonar el repositorio

```bash
git clone https://github.com/CLA-TC5062-SN2026/TC5062-6.git
cd TC5062-6/backend
```

Si ya lo tenías clonado: `cd TC5062-6 && git pull && cd backend`.

---

## 3. Crear el archivo `.env`

El archivo `.env` guarda la configuración y los secretos locales. Nunca se sube al repositorio.

**macOS / Linux**

```bash
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Windows (PowerShell)**

```powershell
Copy-Item .env.example .env
py -3.12 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Abre `.env` con cualquier editor (`notepad .env` en Windows) y reemplaza la línea
`JWT_SECRET=CAMBIAR_...` por `JWT_SECRET=<el texto que imprimió el comando>`. Guarda el archivo.

> Si dejas el valor de plantilla, la API no arranca y muestra `JWT_SECRET conserva el valor de plantilla`.
> Es intencional.

---

## 4. Levantar la base de datos

```bash
docker compose --env-file .env up -d
docker compose ps
```

Repite `docker compose ps` hasta que la columna STATUS diga **`(healthy)`**. La primera vez descarga la imagen
(~600 MB) y crea las tablas de `S05_S06_A1/esquema_bd.sql`, lo que tarda 1–3 minutos.

> **Mac con chip Apple (M1–M4):** es normal ver un aviso de plataforma `linux/amd64`; Docker la emula.
> **Error "port is already allocated" en el 5432:** ya tienes otro PostgreSQL. En `.env` cambia `POSTGRES_PORT=5433`
> y, en `DATABASE_URL`, `localhost:5432` por `localhost:5433`. Después repite el `docker compose up -d`.

---

## 5. Preparar Python e instalar dependencias

**macOS / Linux**

```bash
python3.12 -m venv .venv          # o: python3 -m venv .venv, si python3 ya es 3.12
source .venv/bin/activate
pip install -r requirements-dev.txt
```

**Windows (PowerShell)**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

> Si PowerShell bloquea `Activate.ps1`, ejecuta una vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

A partir de aquí, cada terminal nueva necesita activar el entorno otra vez (`source .venv/bin/activate` o
`.\.venv\Scripts\Activate.ps1`) desde la carpeta `backend`.

**Opcional, recomendado:** comprueba que todo funciona ejecutando las pruebas. Debe terminar en `101 passed`.

```bash
python -m pytest
```

---

## 6. Crear la cuenta de Coordinación

La colección de Postman espera el correo `coordinacion@ecoalert.pe` y la contraseña `Coordinacion-Demo-2026`.

```bash
python -m app.cli crear-coordinacion --nombre "Coordinación Demo" --correo coordinacion@ecoalert.pe
```

Te pedirá la contraseña dos veces y no mostrará lo que escribes. Escribe `Coordinacion-Demo-2026` en ambas.
Debe responder `Cuenta de coordinación creada: <id>`.

> Si responde `Ya existe una cuenta de coordinación`, ya se había creado antes y puedes seguir.
> Si olvidaste qué contraseña usaste, reinicia la base con `docker compose down -v`,
> luego `docker compose --env-file .env up -d`, y repite este paso.

---

## 7. Arrancar la API

```bash
uvicorn app.main:app --reload
```

Deja esta terminal abierta; debe decir `Uvicorn running on http://127.0.0.1:8000`.
En el navegador, <http://127.0.0.1:8000/salud> debe mostrar `{"estado":"ok","base_datos":true}`.

---

## 8. Preparar Postman (fuera de cámara)

1. **Import** → elige `S05_S06_A2/postman/EcoAlert_Auth_S05_S06_A2.postman_collection.json`.
2. Abre la carpeta **0. Preparación (antes de grabar)** y envía **Login de Coordinación**. Debe dar **200**.
   Esto guarda el token de Coordinación en la variable `{{token_coord}}`.
3. Abre en pestañas, en orden, las 6 peticiones de **1. Video (grabar en este orden)**.
4. **Ensayo:** envíalas una vez en orden. Deben salir 201, 200, 200, 200, 401 y 403.
   Se pueden repetir las veces que quieras: el registro genera un correo nuevo en cada envío.
5. Agranda la ventana y el panel de respuesta para que se lean el código de estado y el JSON.

> Si `register` responde **401**, el token de Coordinación se perdió (por ejemplo, se reinició la base):
> vuelve a enviar **Login de Coordinación** (paso 2).

---

## 9. Grabar (máximo 1 minuto, sin cortes)

Inicia la grabación y recorre las pestañas en orden:

| # | Petición | Qué mostrar antes de enviar | Resultado esperado |
|---|---|---|---|
| 1 | `POST {{baseUrl}}/auth/register` | Pestaña **Headers** (`Authorization: Bearer {{token_coord}}`) y pestaña **Body** | **201 Created**; el JSON no incluye contraseña |
| 2 | `POST {{baseUrl}}/auth/login` | Pestaña **Body** (correo y contraseña del analista) | **200 OK** con `access_token` |
| 3 | `GET {{baseUrl}}/auth/me` | Pestaña **Headers** (`Bearer {{token_analista}}`, el token del paso 2) | **200 OK** con los datos del analista |
| 4 | `GET {{baseUrl}}/usuarios` | Pestaña **Headers** (`Bearer {{token_coord}}`) | **200 OK** con la lista de cuentas |
| 5 | `GET {{baseUrl}}/usuarios` | Pestaña **Headers** sin `Authorization` | **401 Unauthorized**, `NO_AUTENTICADO` |
| 6 | `GET {{baseUrl}}/usuarios` | Pestaña **Headers** (`Bearer {{token_analista}}`) | **403 Forbidden**, `ROL_NO_PERMITIDO` |

Consejos:
- Para que la URL completa se vea, pasa el cursor sobre `{{baseUrl}}`; Postman muestra `http://127.0.0.1:8000/api/v1`.
  Lo mismo con `{{token_...}}`.
- Unos 8–9 segundos por petición alcanzan para el minuto. Ensaya una vez cronometrando.
- Si te equivocas, detén la grabación y empieza de nuevo: el video no puede tener cortes.

Guarda el archivo como **`pruebas_auth.mp4`**. Si tu grabador genera `.mov` (macOS) u otro formato, conviértelo
a MP4; por ejemplo, abre el `.mov` con QuickTime → *Archivo → Exportar como → 1080p* y cambia la extensión, o
usa <https://handbrake.fr>.

---

## 10. Subir el video al repositorio

Copia `pruebas_auth.mp4` a la carpeta `S05_S06_A2/` del repositorio y, desde la raíz `TC5062-6`:

```bash
git pull
git add S05_S06_A2/pruebas_auth.mp4
git commit -m "docs(S05_S06_A2): add authentication flow video"
git push
```

> GitHub rechaza archivos de más de 100 MB; un video de 1 minuto suele pesar 5–30 MB.
> Si no tienes permiso de push, envía el video a Miguel para que lo suba.

---

## 11. Zip para Canvas

La entrega en Canvas es un `.zip` con el **contenido** de la carpeta `S05_S06_A2/` (los archivos en la raíz del zip,
sin la carpeta envolvente). El nombre sigue la convención del equipo: `S05_S06_A2_<matrícula>.zip`.

**macOS / Linux** (desde la raíz `TC5062-6`)

```bash
cd S05_S06_A2 && zip -r S05_S06_A2_A0XXXXXXX.zip . -x "*.zip" ".DS_Store" && cd ..
```

**Windows (PowerShell)** (desde la raíz `TC5062-6`)

```powershell
Compress-Archive -Path S05_S06_A2\* -DestinationPath S05_S06_A2\S05_S06_A2_A0XXXXXXX.zip
```

Los `.zip` están en `.gitignore`: no se suben a GitHub.

---

## 12. Apagar todo al terminar

En la terminal de la API: `Ctrl + C`. Después:

```bash
docker compose down        # detiene la base y conserva los datos
docker compose down -v     # (opcional) también borra los datos
```

---

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop no está abierto | Ábrelo y espera *"Engine running"* |
| `port is already allocated` (5432) | Otro PostgreSQL usa el puerto | Paso 4: cambia a 5433 en `.env` |
| `address already in use` (8000) | Otra app usa el puerto 8000 | `uvicorn app.main:app --port 8001` y cambia `baseUrl` en la colección a `http://127.0.0.1:8001/api/v1` |
| La API no arranca: `JWT_SECRET ...` | Secreto vacío, corto o de plantilla | Paso 3 |
| `connection refused` al arrancar la API | La base no está lista | `docker compose ps` hasta ver `(healthy)` |
| `register` responde 401 | Falta `{{token_coord}}` | Envía **Login de Coordinación** (carpeta 0) |
| `register` responde 422 | Se editó el body | Vuelve a importar la colección |
| `login` del analista responde 401 | Se envió el login sin haber registrado al analista | Envía el paso 1 y luego el 2 |
| El paso 6 da 403 `CAMBIO_PASSWORD_REQUERIDO` | No debería ocurrir: el rol se revisa primero | Avisa a Miguel con captura |
| `python -m pytest` falla en todo | La base `ecoalert_test` no existe (volumen creado con una versión anterior) | `docker compose down -v` y `docker compose --env-file .env up -d` |
