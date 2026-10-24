# EcoAlert Tambopata — CRUD inicial (FastAPI + PostgreSQL/PostGIS)

## Alcance real
Implementa **14 operaciones de lectura y escritura iniciales** con las mismas rutas y códigos de éxito definidos en `openapi_equipo.yaml`: creación, listado, consulta y actualización de usuarios; consulta de alertas, cargas, marcas, ajustes, historial y trabajos. Las entidades geoespaciales, historiales y comparaciones **no tienen DELETE** en el contrato del equipo; no se inventan endpoints destructivos.

**Importante:** esta entrega es una **base de servicios CRUD, no una implementación completa de las 37 operaciones OpenAPI**. Las operaciones de autenticación, ingesta de archivos, procesamiento asíncrono, construcción de respuestas espaciales completas, cálculo de prioridad, cambios de estado, creación/retiro de ajustes y marcas, comparación y exportación quedan pendientes. No deben simularse como implementadas. Tampoco se habilitan operaciones que requieran `creado_por` o `autor_id` sin autenticación real. Los endpoints existentes **aún no tienen control de acceso** y no deben exponerse fuera de un entorno local de desarrollo.

### Inicio local (PowerShell)

1. Tener `ecoalert_db` levantado con Docker y `esquema_bd.sql` ya importado.
2. Crear un entorno virtual Python 3.12 (también compatible con versiones recientes soportadas por dependencias):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --env-file .env
```

3. Abrir http://127.0.0.1:8000/docs y probar `GET /salud`.

El archivo `.env.example` contiene valores **solo de desarrollo local**. No subir `.env` al repositorio.

### Trazabilidad

| Método | Ruta | Operación | Estado |
|---|---|---|---|
| GET | `/usuarios` | listarUsuarios | Implementado |
| POST | `/usuarios` | crearUsuario | Implementado |
| GET | `/usuarios/{usuarioId}` | obtenerUsuario | Implementado |
| PATCH | `/usuarios/{usuarioId}` | actualizarUsuario | Implementado |
| GET | `/alertas` | listarAlertas | Implementado (sin filtros) |
| GET | `/cargas-alertas` | listarCargasAlertas | Implementado |
| GET | `/cargas-alertas/{cargaId}` | obtenerCargaAlertas | Implementado |
| GET | `/zonas/{codigo}/marcas` | listarMarcasZona | Implementado |
| GET | `/zonas/{codigo}/marcas/{marcaId}` | obtenerMarca | Implementado |
| GET | `/zonas/{codigo}/ajustes` | listarAjustesZona | Implementado |
| GET | `/zonas/{codigo}/ajustes/{ajusteId}` | obtenerAjuste | Implementado |
| GET | `/zonas/{codigo}/historial` | obtenerHistorialZona | Implementado |
| GET | `/zonas/{codigo}/historial/{entradaId}` | obtenerEntradaHistorial | Implementado |
| GET | `/trabajos/{trabajoId}` | obtenerTrabajo | Implementado |
| Resto | Según OpenAPI | Seguridad, zonas, capas, ingesta, prioridad, análisis, exportación | Pendiente |

**Advertencia sobre fidelidad:** la cobertura es parcial: por ejemplo `GET /alertas` no aplica aún todos los filtros del OpenAPI. Se deben verificar los cuerpos de respuesta con el esquema OpenAPI en pruebas de contrato antes de dar el backend por terminado.

### Diseño
- SQL parametrizado con `psycopg` y pool de conexiones.
- `201` al crear usuario, `200` en lecturas y actualizaciones, `404` al faltar recursos, `409` ante correo duplicado, `400` en integridad, `422` en validación.
- La contraseña se guarda como hash Argon2; nunca se devuelve.
- No existe DELETE físico de usuarios o zonas: el SRS define desactivación, retiro o historial.

### Limitaciones importantes
- Para que `POST /usuarios` cumpla con el SRS, debe exigirse rol Coordinación una vez implementado el login; por ahora es **solo demostración local**.
- El modelo SQL y las vistas OpenAPI no son equivalentes 1:1. Los DTO se construyen en la API.
- No se han ejecutado pruebas de integración en la base de datos del usuario.
