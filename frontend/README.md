# EcoAlert Tambopata — Frontend

## 1. Descripción del proyecto

Frontend de **EcoAlert Tambopata**, desarrollado con React, Vite y Tailwind CSS v4.

Desde S07-S08-A2 la aplicación está **integrada con el backend FastAPI** (`../backend`): inicia sesión con JWT,
protege las rutas que requieren sesión y consulta las alertas de deforestación desde la API REST. En S11-A1 se agregó la
**gestión de usuarios** para Coordinación (RF-02) y el **cambio de contraseña** temporal (RF-02-AC-4). Las decisiones de
la capa de servicios están en [`S07_S08_A2/capa_servicios.md`](../S07_S08_A2/capa_servicios.md).

## 2. Tecnologías utilizadas

- **React 19:** construcción de interfaces mediante componentes reutilizables.
- **Vite 6:** entorno de desarrollo (con proxy hacia la API) y compilación.
- **Tailwind CSS v4:** estilos y diseño responsivo.
- **React Router 7:** rutas públicas (`/login`) y protegidas (`/dashboard`, `/alertas`, `/usuarios`, `/cambiar-password`).
- **useState + Context API:** estado local y sesión compartida (`AuthContext`).
- **fetch** nativo envuelto en un cliente con interceptores (`src/services/httpClient.js`).
- **Vitest + Testing Library:** pruebas de la capa de servicios, la ruta protegida y la vista de alertas.

## 3. Requisitos

- Node.js 20.19+ o 22.12+.
- npm.
- Navegador web actualizado.
- GitHub Codespaces o un entorno local compatible.

## 4. Instalación y ejecución

1. Levantar el backend como indica [`backend/README.md`](../backend/README.md) (base de datos, `.env`, `uvicorn`).
   Para tener datos que mostrar y una cuenta de prueba, desde `backend/`:

   ```bash
   python -m scripts.sembrar_demo   # analista.demo@ecoalert.pe + 6 zonas + 24 alertas; pide la contraseña
   ```

2. Desde la raíz del repositorio:

   ```bash
   cd frontend
   npm install
   cp .env.example .env
   npm run dev
   ```

3. Abrir `http://localhost:5173` e iniciar sesión.

### Ejecución en GitHub Codespaces

1. Iniciar el backend en el puerto 8000 dentro del Codespace.
2. Ejecutar los comandos anteriores; el proxy de Vite reenvía `/api` a `http://localhost:8000` del mismo contenedor.
3. En la pestaña **Ports (Puertos)** abrir el puerto `5173` con **Open in Browser**. No hace falta publicar el 8000.

Para el despliegue completo (base, API y build de producción en el puerto 4173) usar `bash .devcontainer/levantar.sh`;
ver la sección *Despliegue* del [README raíz](../README.md#8-despliegue). Vite solo acepta los hosts `*.app.github.dev`
además de `localhost` (`allowedHosts` en `vite.config.js`).

## 5. Estructura principal

```text
frontend/src/
├── config/env.js              Lee VITE_API_URL y VITE_API_TIMEOUT_MS
├── services/                  Capa de servicios: el único lugar que habla con la API
│   ├── httpClient.js          fetch + interceptores + timeout + conversión de errores
│   ├── api.js                 Instancia configurada: interceptor JWT e interceptor de 401
│   ├── apiError.js            ApiError y tabla única de mensajes para el usuario
│   ├── tokenStorage.js        JWT en sessionStorage + memoria, con expiración
│   ├── authService.js         login, obtenerSesionActual (/auth/me), logout, cambiarPassword
│   ├── usuariosService.js     listar, crear (Idempotency-Key), actualizar (merge-patch), desactivar/reactivar
│   └── alertasService.js      listar (GET /alertas), listarCargas (GET /cargas-alertas)
├── context/AuthContext.jsx    Sesión compartida (usuario y estado de verificación)
├── routes/ProtectedRoute.jsx  Redirige a /login sin sesión
├── hooks/useApiQuery.js       Carga, error, reintento y cancelación de consultas
├── pages/                     LoginPage, DashboardPage, AlertasPage, UsuariosPage, CambiarPasswordPage, NotFoundPage
├── components/                Button, Input, Card, Navbar, AppLayout, ErrorAlert, LoadingState, Segmento, Simbolo, Marca
├── test/                      Configuración y utilidades de pruebas
└── App.jsx                    Definición de rutas
```

## 6. Componentes reutilizables

Se desarrollaron cuatro componentes configurables mediante propiedades (*props*).

| Componente | Funcionalidad |
|---|---|
| **Button** | Botones primarios y secundarios, estado de carga, indicador animado y soporte para deshabilitar acciones. |
| **Input** | Campos de entrada con etiqueta, validación, mensajes de error y atributos de accesibilidad. |
| **Card** | Tarjetas para presentar contenido, encabezados configurables y secciones opcionales de pie de tarjeta. |
| **Navbar** | Barra de navegación responsiva con estados visuales para usuarios autenticados y no autenticados. |
| **Segmento** | Filtro de pocas opciones como botones excluyentes con `aria-pressed` (presencia de alertas, estado de cuentas). |
| **Simbolo** | Punto relleno o aro: la misma simbología de estado en alertas (presente/ausente) y cuentas (activa/desactivada), siempre con texto. |

### Sistema visual

La identidad parte de la cartografía, porque EcoAlert es una herramienta SIG. Los colores son tokens `@theme` de
Tailwind en `src/index.css`, y cada uno tiene un solo significado:

| Token | Valor | Uso |
|---|---|---|
| `papel` | `#f4f6f1` | Fondo de la aplicación |
| `tinta` / `tinta-suave` | `#18231f` / `#56635c` | Texto principal y secundario (contraste AA sobre blanco y papel) |
| `dosel` | `#24533f` | Acciones principales y cuenta activa |
| `perdida` | `#b8235f` | Solo datos de pérdida de bosque (superficie alertada, alerta presente) |
| `rio` | `#2b5f86` | Rol de Coordinación y foco del teclado |
| `ocre` / `peligro` | `#9a6400` / `#b42318` | Avisos de cuenta / errores y acciones destructivas |

La tipografía es una sola familia, **Archivo**, servida desde el build (`@fontsource-variable/archivo`) y usada con su
eje de ancho: expandida para títulos y cifras (`ancho-titulo`, `ancho-cifra`) y condensada para encabezados de tabla y
códigos (`ancho-encabezado`, `ancho-codigo`).

Los componentes se encuentran en `src/components/` y pueden importarse desde otras páginas.

### Ejemplo de reutilización

```jsx
import Button from "./components/Button";
import Card from "./components/Card";

function Ejemplo() {
  return (
    <Card title="Monitoreo ambiental" headingLevel={2}>
      <p>Consulta de información ambiental.</p>
      <Button variant="primary">
        Consultar
      </Button>
    </Card>
  );
}
```

## 7. Funcionalidades

| Ruta | Acceso | Qué hace |
|---|---|---|
| `/login` | Pública | Formulario con validación; llama a `authService.login()`, guarda el JWT y redirige a la ruta pedida o a `/dashboard`. |
| `/dashboard` | Protegida | Cifras de la última carga (alertas, zonas, superficie alertada, ausentes) y zonas ordenadas por superficie, calculadas en el cliente con `GET /alertas` y `GET /cargas-alertas`. Con contraseña temporal solo pide cambiarla. |
| `/alertas` | Protegida | `GET /api/v1/alertas` con estado de carga, error con reintento, filtros por zona y presencia, y paginación. Pulsar un código de zona filtra por ella; acepta `?zona=` desde el panel. |
| `/usuarios` | Protegida, solo Coordinación | Lista con filtro por estado, alta idempotente, edición de nombre y rol (PATCH merge-patch) y desactivación/reactivación con confirmación. El enlace no aparece en el menú de Analista SIG (RF-02-AC-10); el backend responde 403 de todos modos. |
| `/cambiar-password` | Protegida | Reemplaza la contraseña temporal (`PUT /auth/password`); el panel enlaza aquí mientras `debe_cambiar_password` sea verdadero. |
| `/` | — | Redirige a `/dashboard`. |

El botón **Cerrar sesión** revoca el token en el servidor (`POST /auth/logout`) y lo borra del navegador. Después de un
cierre voluntario, la siguiente cuenta que inicie sesión en la pestaña entra al panel, no a la última página de la anterior.

## 8. Variables de entorno

Copiar `.env.example` a `.env` (no se versiona):

| Variable | Llega al navegador | Valor por defecto | Uso |
|---|---|---|---|
| `VITE_API_URL` | Sí | `/api/v1` | URL base de la API, con el prefijo del contrato. Relativa: usa el proxy (dev) o Nginx (producción). |
| `VITE_API_TIMEOUT_MS` | Sí | `15000` | Tiempo máximo de cada petición. |
| `API_PROXY_TARGET` | **No** | `http://localhost:8000` | Destino del proxy de Vite para `/api`. Solo lo lee `vite.config.js`. |

- Las variables `VITE_*` se incrustan en el bundle: nunca deben contener secretos.
- Reiniciar Vite después de modificar `.env`.

## 9. Verificación del funcionamiento

```bash
npm test          # 49 pruebas (Vitest + Testing Library)
npm run build     # compilación de producción con Content-Security-Policy
```

Con backend y frontend en ejecución:

1. Abrir `http://localhost:5173/dashboard` sin sesión → redirige a `/login`.
2. Credenciales incorrectas → "Usuario o contraseña incorrectos".
3. Credenciales correctas → redirige a `/dashboard`.
4. Entrar a **Alertas** → indicador de carga y, después, la tabla con datos del backend.
5. Detener el backend y pulsar **Buscar** → mensaje "No se pudo conectar con el servidor…" con botón **Reintentar**.

## 10. Accesibilidad

Durante la revisión de la interfaz se evaluaron aspectos relacionados con WCAG 2.1:

- Navegación mediante teclado.
- Visibilidad del foco.
- Contraste de colores.
- Asociación de etiquetas con campos de entrada.
- Identificación y anuncio de errores.
- Jerarquía de encabezados.

Se realizaron mejoras en los componentes para facilitar su utilización y comprensión.

La revisión documentada no constituye una certificación integral de conformidad con WCAG 2.1.

## 11. Documentación de las actividades

- `S07_S08_A1/`: `decision_stack_frontend.md`, `revision_componentes.md`, `accesibilidad.md`, `scaffolding.mp4`.
- `S07_S08_A2/`: `capa_servicios.md` (decisiones de la capa de servicios), `flujo_auth.mp4` y `flujo_e2e.mp4`.
- `S11_A1/`: matriz de trazabilidad, retrospectiva, capturas y la prueba E2E `evidencias/flujo_e2e.cjs`.

## 12. Evidencia de scaffolding

Para la evidencia `scaffolding.mp4` se hizo una grabación real de aproximadamente 20 segundos que muestra:

- La ejecución de `npm run dev`.
- El inicio correcto de Vite.
- La interfaz cargada en el navegador.
- La consola del navegador sin errores.
