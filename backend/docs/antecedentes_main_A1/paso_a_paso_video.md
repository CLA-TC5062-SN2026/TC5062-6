# Paso a paso: grabar `pruebas_postman.mp4` (S05-S06-A1)

Guía para quien grabe el video de pruebas del CRUD.

**Lo que pide el profesor:** video de máximo **1 minuto**, **continuo (sin cortes)**, que pruebe en **Postman**
al menos **5 endpoints distintos**, con al menos **un POST, un GET y un PUT o DELETE**. En cada uno deben verse
la **URL**, el **body** de la petición cuando aplique y la **respuesta con su código de estado**.
También hay que verificar que el código HTTP coincida con `openapi_equipo.yaml`, que la respuesta sea JSON y que
**los datos persistan** (un GET después del POST).

La colección cubre **6 endpoints distintos** en 7 peticiones:

| # | Endpoint | Método | Esperado | Qué demuestra |
|---|---|---|---|---|
| 1 | `/usuarios` | POST | **201** | Crear una cuenta |
| 2 | `/usuarios/{usuarioId}` | GET | **200** | El POST persistió en la base de datos |
| 3 | `/usuarios/{usuarioId}` | PATCH | **200** | Actualizar el nombre |
| 4 | `/usuarios?activo=true` | GET | **200** | La actualización persistió |
| 5 | `/auth/login` | POST | **200** | La cuenta nueva puede iniciar sesión |
| 6 | `/auth/password` | **PUT** | **204** | Cambiar la contraseña temporal (cubre el requisito de PUT) |
| 7 | `/usuarios/{usuarioId}` | **DELETE** | **405** | El contrato no permite borrar cuentas (RF-02-AC-7) |

> **Por qué no hay un PUT o DELETE "de CRUD" con 200:** el contrato del equipo define la actualización de cuentas
> como `PATCH` (JSON Merge Patch) y prohíbe borrarlas para conservar la autoría en el historial (RF-02-AC-7):
> `DELETE` responde 405 a propósito. El PUT exitoso es `PUT /auth/password`. El 405 coincide con lo que
> especifica el contrato, que es justo lo que pide verificar la actividad.
>
> **Por qué se usa un token:** desde S05-S06-A2 el backend exige autenticación. El token de Coordinación se
> obtiene antes de grabar (carpeta 0) y Postman lo envía solo en cada petición.

---

## 1. Levantar el backend

Si nunca lo has instalado, sigue los **pasos 1 a 7** de `S05_S06_A2/paso_a_paso_video.md`: instalar herramientas,
clonar, `.env`, base de datos, Python, cuenta de Coordinación y API. Esa guía se probó desde un clon limpio.

Si ya lo tienes instalado, basta con esto desde `TC5062-6/backend`:

**macOS / Linux**

```bash
git pull
docker compose --env-file .env up -d
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

**Windows (PowerShell)**

```powershell
git pull
docker compose --env-file .env up -d
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Comprueba que <http://127.0.0.1:8000/salud> responda `{"estado":"ok","base_datos":true}`.

La colección espera la cuenta `coordinacion@ecoalert.pe` con contraseña `Coordinacion-Demo-2026`. Si la creaste
con otros datos, cambia las variables `coord_correo` y `coord_password` de la colección.

---

## 2. Preparar Postman (fuera de cámara)

1. **Import** → `S05_S06_A1/postman/EcoAlert_CRUD_S05_S06_A1.postman_collection.json`.
2. En la carpeta **0. Preparación (antes de grabar)**, envía **Login de Coordinación** → **200**.
3. Abre en pestañas, en orden, las 7 peticiones de **1. Video (grabar en este orden)**.
4. **Ensayo:** envíalas una vez. Deben salir 201, 200, 200, 200, 200, 204 y 405.
   Se puede repetir las veces que quieras: cada envío del paso 1 crea una cuenta con un correo nuevo.
5. Agranda la ventana y el panel de respuesta para que se lean el código y el JSON.

> Si el paso 1 responde **401**, vuelve a enviar **Login de Coordinación**.

---

## 3. Grabar (máximo 1 minuto, sin cortes)

Unos 8 segundos por petición. Recorre las pestañas en orden:

| # | Qué mostrar antes de enviar | Resultado que debe verse |
|---|---|---|
| 1 · `POST /usuarios` | La URL y la pestaña **Body** (nombre, correo, rol, contraseña temporal) | **201 Created** con la cuenta (sin contraseña) |
| 2 · `GET /usuarios/{{usuario_id}}` | La URL (pasa el cursor sobre `{{usuario_id}}` para ver el id) | **200 OK** con la misma cuenta: persistió |
| 3 · `PATCH /usuarios/{{usuario_id}}` | La pestaña **Body** con el nombre nuevo | **200 OK** con el nombre editado |
| 4 · `GET /usuarios?activo=true` | La URL | **200 OK**; en la lista aparece el nombre editado |
| 5 · `POST /auth/login` | La pestaña **Body** con el correo y la contraseña temporal | **200 OK** con `access_token` |
| 6 · `PUT /auth/password` | La pestaña **Body** (contraseña actual y nueva) | **204 No Content** |
| 7 · `DELETE /usuarios/{{usuario_id}}` | La URL y el método DELETE | **405** con `METODO_NO_PERMITIDO` |

Si el tiempo no alcanza, la petición 7 es opcional: la 6 ya cubre el requisito de PUT y quedan 6 endpoints
distintos. Si te equivocas, detén la grabación y empieza de nuevo: el video no puede tener cortes.

Guarda el archivo como **`pruebas_postman.mp4`**. Si tu grabador genera `.mov`, conviértelo a MP4; el paso 9 de
la guía de A2 explica cómo.

---

## 4. Subir el video

Copia el video a `S05_S06_A1/pruebas_postman.mp4` y, desde la raíz `TC5062-6`:

```bash
git pull
git add S05_S06_A1/pruebas_postman.mp4
git commit -m "docs(S05_S06_A1): add Postman CRUD tests video"
git push
```

Si no tienes permiso de push, envía el video a Miguel.

---

## 5. Zip para Canvas

La entrega en Canvas de esta actividad es un `.zip` con el contenido de `S05_S06_A1/` **y el video**. Desde la
raíz `TC5062-6`:

**macOS / Linux**

```bash
cd S05_S06_A1 && zip -r S05_S06_A1_A0XXXXXXX.zip . -x "*.zip" ".DS_Store" ".gitkeep" && cd ..
```

**Windows (PowerShell)**

```powershell
Compress-Archive -Path S05_S06_A1\* -DestinationPath S05_S06_A1\S05_S06_A1_A0XXXXXXX.zip
```

Los `.zip` están en `.gitignore` y no se suben a GitHub.
