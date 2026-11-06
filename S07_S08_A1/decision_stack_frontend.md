# Decisión del stack tecnológico de frontend

**Proyecto:** EcoAlert Tambopata  
**Actividad:** Construye | Generación de Componentes Frontend — Parte 0  
**Estado:** Stack elegido por el equipo  
**Fuente de comparación:** `Parte 0.- Elección del stack frontend.xlsx` (propuestas de cuatro integrantes y recomendación de la última fila).

## 1. Stack elegido

El equipo **elige React + Vite + Tailwind CSS + Context API y `useState`**, correspondiente a la última fila del cuadro comparativo.

| Categoría solicitada | Tecnología elegida | Aplicación en el proyecto |
|---|---|---|
| Framework o biblioteca de interfaz | **React** | Crear componentes reutilizables y vistas de la aplicación web EcoAlert Tambopata. |
| Herramienta de construcción y servidor de desarrollo | **Vite** | Generar la estructura inicial, ejecutar el entorno de desarrollo y compilar el frontend. |
| Enfoque de estilos | **Tailwind CSS** | Construir interfaces responsivas y mantener estilos consistentes entre componentes. |
| Manejo de estado | **`useState` + Context API** | Administrar estados locales y compartir información entre componentes cuando sea necesario. |

La elección concreta el stack de frontend sin cambiar la arquitectura cliente-servidor del proyecto, que contempla una SPA React y un backend independiente con API REST.

## 2. Alternativas consideradas y motivos de descarte

Se revisaron las cuatro propuestas registradas por los cuatro integrantes. Para la elección se tomó en cuenta la evaluación técnica del stack frente a las necesidades de esta actividad.

| Integrante | Framework / UI | Construcción | Estilos | Estado | Motivo para no elegir esta combinación |
|---|---|---|---|---|---|
| **Miguel Arévalo Andrade** | React | Angular CLI | Bootstrap | Context API + `useState` | Conserva React y un estado adecuado, pero **Angular CLI está orientado a Angular**, no es la herramienta habitual para construir un proyecto React. Además, se prefirió Tailwind para personalizar los cuatro componentes sin depender de los estilos predefinidos de Bootstrap. |
| **Anthony Gerardo Gutarra Sánchez** | Vue 3 | Vite | Bootstrap | Pinia | Es técnicamente viable y ofrece gestión de estado centralizada. No se seleccionó porque el equipo cuenta con una práctica introductoria previa con React y Vite; cambiar a Vue y Pinia introduciría conceptos nuevos sin una necesidad clara para los cuatro componentes iniciales. |
| **Daniel Medina Vargas** | Angular | Angular CLI | Angular Material | Signals + servicios | Es una propuesta coherente, con arquitectura y componentes integrados. No se eligió porque sus convenciones y herramientas suponen una curva de adopción mayor que la necesaria para el alcance actual. |
| **Eduardo Daniel Sauza Machado** | Next.js | Herramientas integradas de Next.js | Tailwind CSS | Context API | Es una alternativa viable, con enrutamiento y opciones avanzadas de renderizado. No se seleccionó porque el proyecto ya contempla una SPA que consume una API REST independiente y esta actividad no requiere renderizado del lado del servidor. |

La decisión no implica que las demás tecnologías sean incompatibles con una API REST o con JWT; se da prioridad a cu compatibilidad al alcance y a la experiencia práctica disponible.

## 3. Justificación de la elección

### 3.1. Características del equipo

El equipo ya realizó una práctica introductoria con **React y Vite**, incluyendo creación de componentes y ejecución del servidor de desarrollo. Reutilizar esta base reduce el esfuerzo inicial de configuración y facilita que los integrantes se concentren en comprender, revisar y ajustar el código generado por el agente de programación.

Se consideraron propuestas distintas, pero **no necesariamente cuantifica el dominio individual de cada tecnología**. Por ello, la decisión se fundamenta en la experiencia práctica previa documentada.

### 3.2. Integración con el backend

La arquitectura consolidada de **EcoAlert Tambopata** contempla una **aplicación web SPA con React**, un backend independiente **Python/FastAPI** y una API REST con autenticación y control de acceso. React se alinea con esta separación entre interfaz y lógica del servidor: los componentes presentan información, mientras que una capa `services/` podrá centralizar las solicitudes HTTP al backend.

Vite permite configurar la dirección base de la API mediante variables de entorno (por ejemplo, `VITE_API_URL`), evitando fijar direcciones del servidor en los componentes. `useState` y Context API pueden representar y compartir información visual de sesión cuando corresponda. **La autenticación JWT real, el consumo completo de endpoints y la integración extremo a extremo no forman parte de esta entrega inicial**; quedan para actividades posteriores.

### 3.3. Complejidad de la interfaz requerida

La actividad solicita generar y revisar cuatro componentes reutilizables:

| Componente | Necesidad de la actividad | Adecuación del stack |
|---|---|---|
| **Button** | Variantes primaria/secundaria y estado de carga | React facilita variantes por props; Tailwind aplica estilos según estado. |
| **Input** | Etiqueta y validación visual básica | React permite manejar valores y mensajes visuales; Tailwind define estilos de error y foco. |
| **Card** | Contenedor genérico para contenido estructurado | Composición de componentes React y clases responsivas. |
| **Navbar** | Estado visual autenticado/no autenticado | Props o `useState` permiten simular el estado; Context API queda disponible si se comparte entre vistas. |

Consideramos el hecho de que esta primera entrega **no exige construir todavía los mapas geoespaciales, formularios completos, flujos de autenticación ni funcionalidades operativas del sistema**. La elección permite iniciar con una estructura sencilla (`components/`, `pages/`, `services/`) y extenderla después hacia las pantallas previstas para EcoAlert Tambopata.

### 3.4. Limitaciones reconocidas y mitigación

| Limitación | Medida propuesta |
|---|---|
| React no impone una arquitectura de carpetas ni incluye todas las herramientas de navegación. | Definir convenciones claras para `components/`, `pages/` y `services/`; añadir navegación solo cuando sea necesaria. |
| Tailwind puede producir listas extensas de clases. | Mantener componentes pequeños, reutilizar patrones y revisar legibilidad durante la revisión crítica del código. |
| `useState` y Context API pueden resultar difíciles de mantener con estado global complejo o provocar renderizados innecesarios si se concentra demasiado estado en un contexto. | Preferir estado local y crear contextos únicamente para información realmente compartida; reevaluar herramientas si crece la complejidad. |
| El stack no garantiza accesibilidad automáticamente. | Revisar contraste, etiquetas accesibles y foco de teclado conforme a WCAG 2.1, documentando problemas reales y correcciones en `accesibilidad.md`. |

## 4. Conclusión

El equipo **selecciona React + Vite + Tailwind CSS + Context API y `useState`** por su coherencia con la arquitectura SPA de EcoAlert Tambopata, la práctica previa con React/Vite, la integración futura con la API REST de FastAPI y su suficiencia para implementar los cuatro componentes reutilizables solicitados. Se descartan las otras combinaciones para esta actividad por razones de compatibilidad de herramientas, curva de adopción o complejidad adicional, sin negar su viabilidad para otros escenarios.

**Alcance de la decisión:** elección y justificación del stack de frontend. El scaffolding, la implementación de componentes, su revisión crítica y la evaluación de accesibilidad se documentarán en los entregables correspondientes de las siguientes partes.
