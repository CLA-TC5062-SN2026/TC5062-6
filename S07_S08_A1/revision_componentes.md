# Revisión crítica y adecuación de componentes frontend

**Proyecto:** EcoAlert Tambopata  
**Actividad:** Construye | Generación de Componentes Frontend  
**Tecnologías:** React, Vite y Tailwind CSS  
**Archivo:** `revision_componentes.md`

## 1. Propósito y metodología

Este documento registra la revisión del código de cuatro componentes reutilizables del frontend: `Input`, `Button`, `Card` y `Navbar`. Se trabajó en dos etapas:

1. **Propuesta inicial del agente de IA:** generación de una primera versión funcional de cada componente, con propiedades configurables y estilos básicos.
2. **Versión definitiva revisada por el equipo:** evaluación de las limitaciones de la propuesta inicial, implementación de ajustes y comprobación de su funcionamiento en la interfaz de EcoAlert Tambopata.

Cada integrante asumió la revisión de un componente. **Los identificadores «Integrante 1» a «Integrante 4» son marcadores pendientes de sustituir por los nombres reales del equipo.** Las observaciones descritas son las adecuaciones trabajadas durante la revisión conjunta; no se atribuyen a personas concretas hasta completar esa información.

## 2. Distribución de revisiones

| Responsable | Componente | Archivo | Enfoque de la revisión |
|---|---|---|---|
| Miguel Arévalo Andrade | Input | `frontend/src/components/Input.jsx` | Asociación de etiqueta, validación y accesibilidad |
| Anthony Gerardo Gutarra Sánchez | Button | `frontend/src/components/Button.jsx` | Estados de carga, foco, deshabilitación y reutilización |
| Daniel Medina Vargas | Card | `frontend/src/components/Card.jsx` | Semántica, jerarquía de títulos y diseño responsivo |
| Eduardo Daniel Sauza Machado | Navbar | `frontend/src/components/Navbar.jsx` | Reutilización de Button, navegación accesible y adaptación móvil |

## 3. Observación 1 — Componente Input

**Responsable:** Miguel Arévalo Andrade  
**Archivo:** `frontend/src/components/Input.jsx`

### Propuesta inicial del agente de IA

La primera versión permitía recibir una etiqueta (`label`), un valor (`value`), un manejador de cambios (`onChange`), un texto de ejemplo (`placeholder`), un tipo de dato (`type`) y un mensaje de error (`error`). Mostraba un borde rojo y un texto de validación cuando existía un error. Sin embargo, la etiqueta `<label>` no estaba asociada explícitamente con el elemento `<input>`, no existía un identificador para vincular el mensaje de error y no se definía un estilo de foco específico.

### Cambios realizados

| Elemento | Propuesta inicial | Versión definitiva |
|---|---|---|
| Asociación de etiqueta | `<label>` sin `htmlFor` | `htmlFor={id}` y `id={id}` en el campo |
| Identificadores | Sin identificador único | `useId()` de React |
| Comunicación de errores | Mensaje visual y borde rojo | `aria-invalid` y `aria-describedby` asociados al error |
| Foco | Sin estilo personalizado | `focus:outline-none` y `focus:ring-2 focus:ring-green-700` |
| Extensibilidad | Propiedades explícitas | Admite atributos adicionales mediante `...props` |

### Justificación

Se consideró necesario que la etiqueta y los mensajes de validación pudieran relacionarse de forma programática con el campo correspondiente. El uso de `useId()` evita colisiones de identificadores cuando se reutiliza el componente. Los atributos ARIA facilitan la interpretación de los errores mediante tecnologías de asistencia; el indicador de foco permite reconocer visualmente el campo seleccionado. La incorporación de `...props` amplía las posibilidades de reutilización sin alterar su estructura.

**Comprobación:** se verificó que el campo «Zona de monitoreo» permitiera escribir, que la consulta con el campo vacío mostrara el error y que la interacción siguiera funcionando después de la revisión.

## 4. Observación 2 — Componente Button

**Responsable:** Anthony Gerardo Gutarra Sánchez  
**Archivo:** `frontend/src/components/Button.jsx`

### Propuesta inicial del agente de IA

El botón inicial admitía las variantes `primary` y `secondary`, mostraba el texto «Cargando...» cuando `loading` era verdadero y se deshabilitaba durante la carga. No tenía un indicador animado, un estado `disabled` independiente, un estilo explícito de foco mediante teclado ni un mecanismo general para recibir atributos HTML adicionales.

### Cambios realizados

| Elemento | Propuesta inicial | Versión definitiva |
|---|---|---|
| Estado de carga | Sustitución del texto por «Cargando...» | Texto acompañado por un indicador giratorio con `animate-spin` |
| Comunicación del estado | `disabled={loading}` | `aria-busy={loading}` y `disabled={disabled || loading}` |
| Deshabilitación | Solo durante la carga | Propiedad `disabled` independiente y estilos de estado deshabilitado |
| Foco | Sin estilo específico | `focus-visible:outline` y contorno con separación |
| Extensibilidad | Propiedades limitadas | Atributos adicionales mediante `...props` |

### Justificación

Se buscó hacer más evidente la ejecución de operaciones y evitar acciones repetidas mientras una consulta está en curso. El indicador animado aporta retroalimentación visual, mientras que el texto mantiene una indicación legible. La propiedad `disabled` permite controlar otras situaciones de indisponibilidad y los estilos `focus-visible` facilitan la navegación con teclado. Finalmente, `...props` permite añadir atributos sin duplicar el componente.

**Comprobación:** se verificó el funcionamiento de «Consultar» y «Limpiar», la presentación del indicador de carga y la navegación mediante la tecla Tab.

## 5. Observación 3 — Componente Card

**Responsable:** Daniel Medina Vargas  
**Archivo:** `frontend/src/components/Card.jsx`

### Propuesta inicial del agente de IA

La tarjeta inicial utilizaba un contenedor `<div>`, presentaba un título opcional fijo en `<h3>`, mostraba contenido mediante `children` y permitía un pie de tarjeta mediante `footer`. Incluía `className` para personalizar estilos, pero el espaciado interior era fijo y no ofrecía control sobre la jerarquía del encabezado.

### Cambios realizados

| Elemento | Propuesta inicial | Versión definitiva |
|---|---|---|
| Contenedor | `<div>` genérico | `<article>` para las tarjetas informativas independientes de esta pantalla |
| Encabezado | `<h3>` fijo | Propiedad `headingLevel` con validación de niveles 1 a 6 |
| Relación título-tarjeta | Sin asociación explícita | `aria-labelledby` e identificador generado con `useId()` |
| Espaciado | `p-5` fijo | `p-4 sm:p-6` según el tamaño de pantalla |
| Extensibilidad | `className` | Conserva `className` y admite `...props` |

### Justificación

En el panel de monitoreo, cada tarjeta comunica un bloque de información con sentido propio, por lo que se adoptó `<article>` para esta aplicación. La propiedad `headingLevel` evita imponer un nivel de encabezado que podría no corresponder a la jerarquía de otras pantallas. `aria-labelledby` relaciona la tarjeta con su título, mientras que las clases responsivas mejoran el aprovechamiento del espacio en pantallas pequeñas. Se mantiene la posibilidad de personalización mediante `className`.

**Consideración:** `<article>` no es obligatorio para todas las tarjetas genéricas; si el componente se utiliza posteriormente como agrupador puramente visual, convendría permitir seleccionar el elemento contenedor.

**Comprobación:** se revisó que las tres tarjetas del panel conservaran sus títulos, contenidos, botones y pie informativo después del cambio.

## 6. Observación 4 — Componente Navbar

**Responsable:** Eduardo Daniel Sauza Machado  
**Archivo:** `frontend/src/components/Navbar.jsx`

### Propuesta inicial del agente de IA

La barra de navegación mostraba el nombre «EcoAlert Tambopata», un enlace a «Inicio» y un botón para iniciar o cerrar sesión según `isAuthenticated`. Aunque los dos estados se representaban correctamente, los botones tenían estilos propios duplicados, la navegación no contaba con un nombre accesible y la distribución móvil podía mejorarse.

### Cambios realizados

| Elemento | Propuesta inicial | Versión definitiva |
|---|---|---|
| Botones | Etiquetas `<button>` con clases independientes | Uso del componente reutilizable `Button` |
| Identificación de navegación | `<nav>` sin nombre específico | `aria-label="Navegación principal"` |
| Página actual | Enlace «Inicio» sin indicador | `aria-current="page"` en «Inicio» |
| Foco del enlace | Solo estilo `hover` | Estilos `focus-visible` con contorno visible |
| Distribución | `flex-wrap` horizontal | `flex-col sm:flex-row` para pantallas pequeñas y amplias |
| Estados de sesión | Inicio y cierre de sesión | Se mantienen los dos estados y sus callbacks |

### Justificación

Reutilizar `Button` reduce la duplicación de código y mantiene una apariencia y comportamiento consistentes en la interfaz. El nombre de navegación y el indicador de página actual aportan información semántica; el contorno visible facilita identificar el enlace seleccionado mediante teclado. La nueva distribución adapta los elementos al ancho disponible sin cambiar la lógica de autenticación simulada.

**Consideración:** el atributo `aria-current="page"` es correcto mientras «Inicio» sea la página activa. Si se agregan rutas, deberá establecerse dinámicamente según la ruta actual.

**Comprobación:** se verificaron las transiciones visuales entre «Iniciar sesión» y «Cerrar sesión», la navegación con Tab y la adaptación de la barra al reducir el ancho del navegador.

## 7. Síntesis de las adecuaciones

| Componente | Principal limitación detectada | Resultado de la revisión |
|---|---|---|
| Input | Etiqueta y errores sin asociación programática | Campo con identificadores, validación accesible y foco visible |
| Button | Retroalimentación y estados limitados | Indicador de carga, deshabilitación configurable y mejor navegación por teclado |
| Card | Estructura y encabezado rígidos | Tarjeta semántica con encabezado configurable y espaciado responsivo |
| Navbar | Estilos duplicados y adaptación móvil básica | Reutilización de Button y navegación más accesible y responsiva |

## 8. Conclusión

La propuesta inicial generada por el agente de IA permitió construir y probar rápidamente los cuatro componentes requeridos. No obstante, la revisión del equipo identificó oportunidades concretas para mejorar su semántica, accesibilidad, adaptabilidad y reutilización. La versión definitiva conserva la funcionalidad inicial y añade cambios justificados en el código, en lugar de limitarse a aceptar la primera respuesta de la herramienta.

Las pruebas se realizaron sobre una interfaz demostrativa de EcoAlert Tambopata. La consulta y el cambio de estado de autenticación son simulaciones locales; **no se implementó ni se verificó una conexión real al backend o autenticación JWT** en esta etapa. Las mejoras documentadas aportan insumos para la evaluación de accesibilidad de la siguiente parte de la actividad, sin sustituir una auditoría integral de WCAG 2.1.
