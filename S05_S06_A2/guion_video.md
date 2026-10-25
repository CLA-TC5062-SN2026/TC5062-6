# Guion del video — Flujo de autenticación en Postman (≤ 1 min, sin cortes)

Colección: `postman/EcoAlert_Auth_S05_S06_A2.postman_collection.json` (importar en Postman).
Guarda la grabación como **`S05_S06_A2/pruebas_auth.mp4`** (nombre exigido por la entrega).
Cada petición tiene pruebas que guardan los tokens solos; no hace falta copiar y pegar nada durante la grabación.

## Antes de grabar (fuera de cámara)

1. Base de datos y API en marcha (`backend/README.md`).
2. Cuenta de Coordinación creada con `python -m app.cli crear-coordinacion`. Si usaste otro correo o contraseña,
   ajusta las variables `coord_correo` y `coord_password` de la colección.
3. Ejecuta **0. Preparación → Login de Coordinación** (guarda `token_coord`).
4. Abre las 6 peticiones de la carpeta **1. Video** en pestañas, en orden.

## Durante la grabación (carpeta "1. Video", en este orden)

| # | Petición | Mostrar en pantalla | Esperado |
|---|---|---|---|
| 1 | `POST /api/v1/auth/register` | Pestaña **Headers** (`Authorization: Bearer {{token_coord}}`) y **Body** | **201**; la respuesta no incluye contraseña |
| 2 | `POST /api/v1/auth/login` | Body con el correo y la contraseña del analista | **200** con `access_token` |
| 3 | `GET /api/v1/auth/me` | Header `Authorization: Bearer {{token_analista}}` (token del paso 2) | **200** con los datos del analista |
| 4 | `GET /api/v1/usuarios` | Header con `{{token_coord}}` | **200** con la lista (incluye al analista recién creado) |
| 5 | `GET /api/v1/usuarios` sin token | Pestaña Headers sin `Authorization` | **401** `NO_AUTENTICADO` |
| 6 | `GET /api/v1/usuarios` con token de Analista SIG | Header con `{{token_analista}}` | **403** `ROL_NO_PERMITIDO` |

Consejos: pasa el cursor sobre `{{token_…}}` para que Postman muestre el valor, y amplía el panel de respuesta
para que se lean el código de estado y el JSON. El registro genera un correo nuevo en cada ejecución, así que
el flujo se puede repetir sin conflictos (409) si hay que volver a grabar.
