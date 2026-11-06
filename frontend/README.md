# EcoAlert Tambopata — Frontend

## 1. Descripción del proyecto

Frontend de **EcoAlert Tambopata**, desarrollado con React, Vite y Tailwind CSS v4 como parte de la actividad de generación de componentes frontend.

La aplicación presenta un panel demostrativo de monitoreo ambiental que permite visualizar información general, consultar zonas de monitoreo y probar componentes reutilizables.

La interfaz incluye estados de autenticación simulados, validación de formularios y estados de carga. Actualmente no requiere conexión con el backend para su funcionamiento.

## 2. Tecnologías utilizadas

- **React:** construcción de interfaces mediante componentes reutilizables.
- **Vite:** entorno de desarrollo y compilación.
- **Tailwind CSS v4:** estilos y diseño responsivo.
- **useState:** administración de estados locales.
- **Context API:** alternativa prevista para compartir estados cuando la aplicación lo requiera.

## 3. Requisitos

- Node.js 20.19+ o 22.12+.
- npm.
- Navegador web actualizado.
- GitHub Codespaces o un entorno local compatible.

## 4. Instalación y ejecución

Desde la raíz del repositorio, ejecutar:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Abrir la dirección indicada por Vite, normalmente:

`http://localhost:5173`

### Ejecución en GitHub Codespaces

1. Abrir el repositorio en GitHub Codespaces.
2. Ejecutar los comandos anteriores desde la terminal.
3. Abrir la pestaña **Ports (Puertos)**.
4. Localizar el puerto `5173`.
5. Seleccionar **Open in Browser** para visualizar la aplicación.

Para utilizar la interfaz demostrativa no es necesario iniciar el backend.

## 5. Estructura principal

```text
frontend/
├── src/
│   ├── components/
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Card.jsx
│   │   └── Navbar.jsx
│   ├── context/
│   ├── pages/
│   │   └── Inicio.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── package-lock.json
└── vite.config.js
```

## 6. Componentes reutilizables

Se desarrollaron cuatro componentes configurables mediante propiedades (*props*).

| Componente | Funcionalidad |
|---|---|
| **Button** | Botones primarios y secundarios, estado de carga, indicador animado y soporte para deshabilitar acciones. |
| **Input** | Campos de entrada con etiqueta, validación, mensajes de error y atributos de accesibilidad. |
| **Card** | Tarjetas para presentar contenido, encabezados configurables y secciones opcionales de pie de tarjeta. |
| **Navbar** | Barra de navegación responsiva con estados visuales para usuarios autenticados y no autenticados. |

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

## 7. Funcionalidades de la interfaz demostrativa

La aplicación permite:

- Visualizar el panel de monitoreo ambiental.
- Ingresar una zona de monitoreo.
- Mostrar un mensaje de validación cuando el campo está vacío.
- Simular un proceso de consulta mediante un estado de carga.
- Limpiar el formulario.
- Alternar entre estados visuales de sesión iniciada y cerrada.
- Visualizar tarjetas informativas sobre el monitoreo ambiental.

**Nota:** las consultas y la autenticación son simulaciones de interfaz. No existe todavía una integración funcional con la API REST ni con un mecanismo real de autenticación.

## 8. Variables de entorno

El archivo `.env.example` contiene la configuración de referencia:

```env
VITE_API_URL=http://localhost:8000
```

La variable `VITE_API_URL` define la dirección base prevista para la futura API REST desarrollada con FastAPI.

Para utilizarla, copiar `.env.example` a `.env` y ajustar la dirección según el entorno.

**Importante:**

- El archivo `.env` no debe publicarse en GitHub.
- Las variables `VITE_*` son accesibles desde el frontend y no deben contener contraseñas ni secretos.
- Reiniciar Vite después de modificar las variables de entorno.

## 9. Verificación del funcionamiento

Después de ejecutar `npm run dev`, comprobar:

1. Vite inicia correctamente y muestra su dirección local.
2. El navegador presenta el título **«Panel de monitoreo ambiental»**.
3. Se visualiza la barra de navegación de EcoAlert Tambopata.
4. Aparecen las tarjetas **«Consulta de zonas»**, **«Estado del monitoreo»** y **«Prueba de estado de carga»**.
5. El formulario permite ingresar texto y muestra un error cuando se intenta consultar sin indicar una zona.
6. Los botones **Consultar**, **Limpiar**, **Iniciar sesión** y **Cerrar sesión** funcionan según su comportamiento demostrativo.
7. Los indicadores de carga se muestran correctamente.
8. La consola del navegador no presenta errores de ejecución.

### Compilación de producción

Ejecutar:

```bash
npm run build
```

El comando debe finalizar sin errores y generar los archivos de distribución en `dist/`.

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

## 11. Documentación de la actividad

Los documentos correspondientes a la actividad se organizan en la carpeta `S07_S08_A1/`, ubicada en la raíz del repositorio:

- `decision_stack_frontend.md`: selección y justificación de tecnologías.
- `revision_componentes.md`: revisión de la propuesta inicial del agente de IA y modificaciones del equipo.
- `accesibilidad.md`: resultados de las pruebas, observaciones y adecuaciones de accesibilidad.

## 12. Evidencia de scaffolding

Para la evidencia `scaffolding.mp4` se hizo una grabación real de aproximadamente 20 segundos que muestra:

- La ejecución de `npm run dev`.
- El inicio correcto de Vite.
- La interfaz cargada en el navegador.
- La consola del navegador sin errores.
