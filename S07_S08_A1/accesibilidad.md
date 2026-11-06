# Informe de revisión de accesibilidad — EcoAlert Tambopata

**Actividad:** Construye | Generación de Componentes Frontend — Parte 3  
**Proyecto:** EcoAlert Tambopata  
**Tecnologías:** React, Vite y Tailwind CSS  
**Rol de quien documenta:** Agente de IA — apoyo en la revisión técnica de accesibilidad  
**Alcance:** Pantalla de demostración de componentes `Input`, `Button`, `Card` y `Navbar`; pruebas manuales realizadas por el equipo en Firefox.  
**Referencia:** WCAG 2.1, nivel A y AA, según corresponda.

## 1. Objetivo y metodología

El agente de IA propuso una revisión guiada de accesibilidad de la interfaz. El equipo ejecutó pruebas manuales de navegación por teclado, foco visible, contraste de texto, etiquetas y mensajes de validación. Se revisó además la jerarquía de encabezados a partir del código utilizado en la demostración.

Los resultados se clasifican en tres categorías: **satisfactorio en la prueba realizada**, **observación corregida** y **mejora preventiva**. Las pruebas manuales y el inspector de Firefox no constituyen por sí solos una auditoría completa de conformidad WCAG 2.1.

## 2. Resumen de resultados

| Área evaluada | Resultado inicial | Acción | Resultado o estado posterior | WCAG 2.1 relacionada |
|---|---|---|---|---|
| Uso mediante teclado | Satisfactorio en los controles probados | Sin cambios | Se pudo navegar y activar los controles | 2.1.1 (A) |
| Orden y visibilidad del foco | Satisfactorio en la secuencia probada | Sin cambios | Foco perceptible y recorrido funcional | 2.4.3 (A), 2.4.7 (AA) |
| Contraste del texto «Cargando...» | Firefox señaló relación de **1.79:1** | Se eliminó `disabled:opacity-60` de `Button.jsx` | El equipo confirmó que Firefox dejó de mostrar problemas de contraste | 1.4.3 (AA), con excepción aplicable a controles inactivos |
| Mensaje de error de zona vacía | El mensaje era visible y el campo podía recibir el foco | Se agregó `role="alert"` al mensaje en `Input.jsx` | Cambio implementado; **no se verificó con lector de pantalla** | 3.3.1 (A), 4.1.3 (AA) como referencias de revisión |
| Etiquetas de texto | Firefox no mostró incidencias en la comprobación elegida | Sin cambios adicionales | Sin advertencias en esa comprobación | 1.3.1 (A), 4.1.2 (A), según elemento |
| Jerarquía de encabezados | La página pasaba de `h1` a títulos `h3` | Se añadió `headingLevel={2}` a las tres tarjetas en `App.jsx` | El equipo confirmó haber realizado el cambio; no se hizo una segunda inspección del árbol de accesibilidad | 1.3.1 (A) |

## 3. Resultados positivos: controles que funcionaron

### 3.1 Navegación por teclado y foco visible

**Pruebas realizadas por el equipo:**

1. Con **Tab**, el foco llegó al enlace «Inicio».
2. El botón «Iniciar sesión» recibió el foco y pudo activarse con **Enter**.
3. El campo «Zona de monitoreo» recibió el foco y permitió escribir.
4. Los botones «Consultar» y «Limpiar» pudieron activarse mediante teclado.
5. Los elementos interactivos probados mostraron un indicador visible de foco.

**Evaluación del agente:** no se identificaron fallas en estas comprobaciones. Se consideraron satisfactorias dentro de la secuencia evaluada para WCAG 2.1 **2.1.1**, **2.4.3** y **2.4.7**. No se requirió modificar código como resultado de esta prueba.

### 3.2 Identificación visual del error de formulario

Al pulsar «Consultar» con el campo vacío, el equipo confirmó que aparecía el mensaje de error y que el campo «Zona de monitoreo» podía recibir el foco. En la versión revisada de `Input.jsx` ya se utilizaban `aria-invalid` y `aria-describedby` para relacionar el estado y el mensaje de error con el campo.

**Evaluación del agente:** la prueba no evidenció una falla de identificación visual del error (WCAG 2.1 **3.3.1**). La posterior incorporación de `role="alert"` se documenta como una mejora adicional, no como corrección de un incumplimiento comprobado.

### 3.3 Comprobación de etiquetas

En la herramienta **Accesibilidad** de Firefox, el equipo seleccionó la comprobación de etiquetas de texto y reportó que **no aparecieron problemas**.

**Evaluación del agente:** resultado positivo para el análisis automatizado realizado; no equivale a garantizar que todos los elementos de toda la aplicación cumplan todos los criterios de etiquetado.

## 4. Observación 1 — Legibilidad del botón en estado de carga

**Componente:** `frontend/src/components/Button.jsx`  
**Detección:** comprobador de contraste de Firefox  
**Resultado observado:** relación de contraste **1.79:1** para el texto «Cargando...».

**Código inicial propuesto por el agente:**

```jsx
const baseStyles = `
  /* Otras clases */
  disabled:cursor-not-allowed
  disabled:opacity-60
`;
```

**Adecuación aplicada por el equipo:** se eliminó `disabled:opacity-60` y se conservó `disabled:cursor-not-allowed`.

```jsx
const baseStyles = `
  /* Otras clases */
  disabled:cursor-not-allowed
`;
```

**Justificación:** la reducción de opacidad disminuía la legibilidad del texto. Al eliminarla, se preservó el contraste visual del botón deshabilitado sin alterar su estado funcional.

**Verificación posterior:** el equipo volvió a ejecutar la comprobación de contraste en Firefox y reportó que **ya no aparecían problemas de contraste**.

**Precisión normativa:** WCAG 2.1 **1.4.3 (Contraste mínimo, AA)** exige normalmente al menos **4.5:1** para texto de tamaño normal; sin embargo, **los componentes inactivos están exceptuados** de este criterio. Por ello, el aviso de Firefox se registra como **problema de legibilidad corregido**, no como incumplimiento WCAG demostrado.

## 5. Observación 2 — Anuncio dinámico del error

**Componente:** `frontend/src/components/Input.jsx`  
**Detección:** revisión del código de la validación dinámica  
**Situación inicial:** el mensaje de error aparecía visualmente y estaba vinculado al campo mediante `aria-describedby`, pero no contaba con un rol de anuncio explícito.

**Código anterior:**

```jsx
{error && (
  <span id={errorId} className="text-sm text-red-700">
    {error}
  </span>
)}
```

**Adecuación aplicada por el equipo:**

```jsx
{error && (
  <span
    id={errorId}
    role="alert"
    className="text-sm text-red-700"
  >
    {error}
  </span>
)}
```

**Justificación:** `role="alert"` permite que las tecnologías de asistencia reconozcan el mensaje insertado dinámicamente como un aviso prioritario, sin depender exclusivamente de que el usuario vuelva a situar el foco en el campo. Se conservó `aria-describedby` para mantener la asociación entre el campo y el texto de error.

**Verificación posterior:** el equipo confirmó haber realizado la modificación. **No se documentó una prueba con lector de pantalla**, por lo que no se afirma que el anuncio audible haya sido comprobado.

**Precisión normativa:** mejora preventiva relacionada con la comunicación de errores y mensajes de estado, especialmente WCAG 2.1 **4.1.3 (Mensajes de estado, AA)**. No se demostró un incumplimiento previo del criterio **3.3.1**.

## 6. Observación 3 — Jerarquía de encabezados

**Archivos:** `frontend/src/App.jsx` y componente reutilizable `frontend/src/components/Card.jsx`  
**Detección:** revisión de la estructura de encabezados utilizada en la página.

**Situación inicial:** la pantalla tenía un encabezado principal `h1` («Panel de monitoreo ambiental») y las tres tarjetas usaban, por defecto, `h3`, sin encabezados `h2` intermedios.

**Código anterior en `App.jsx`:**

```jsx
<Card title="Consulta de zonas">
```

**Adecuación aplicada por el equipo:** se estableció explícitamente `headingLevel={2}` en las tres tarjetas.

```jsx
<Card title="Consulta de zonas" headingLevel={2}>

<Card
  title="Estado del monitoreo"
  headingLevel={2}
  footer="Información demostrativa, sin conexión al backend."
>

<Card title="Prueba de estado de carga" headingLevel={2}>
```

**Justificación:** el orden `h1` → `h2` ofrece una organización más clara de las secciones principales. Se aprovechó la propiedad `headingLevel` ya incorporada al componente `Card`, sin duplicar componentes ni modificar el contenido.

**Verificación posterior:** el equipo confirmó haber aplicado los tres ajustes. No consta una inspección posterior del árbol de accesibilidad; esa verificación se recomienda como comprobación final.

**Precisión normativa:** la jerarquía semántica se relaciona con WCAG 2.1 **1.3.1 (Información y relaciones, A)**. **Saltar de `h1` a `h3` no implica por sí mismo un incumplimiento automático**, por lo que se registra como mejora estructural.

## 7. Balance de la revisión del agente

La revisión identificó resultados satisfactorios en **navegación por teclado, foco visible, aparición del mensaje de validación y comprobación de etiquetas**. También permitió aplicar tres adecuaciones concretas:

1. **`Button.jsx`:** eliminación de la opacidad del estado deshabilitado, con desaparición de las advertencias de contraste reportadas por Firefox.
2. **`Input.jsx`:** incorporación de `role="alert"` para favorecer el anuncio de errores dinámicos.
3. **`App.jsx` / `Card.jsx`:** establecimiento de títulos `h2` en las tres tarjetas para mejorar la estructura de encabezados.

**Alcance de la evidencia:** la primera adecuación responde a una advertencia real de la herramienta, aunque exceptuada del requisito de contraste por tratarse de un control inactivo. Las otras dos son mejoras de accesibilidad fundamentadas en la revisión del código, **no incumplimientos normativos confirmados**. Por tanto, esta evidencia documenta **una incidencia de legibilidad y dos mejoras preventivas**, pero **no acredita dos incumplimientos WCAG verificados**. Si la rúbrica exige específicamente dos problemas demostrados, será necesario ampliar las pruebas antes de afirmarlo.


## 8. Referencia

World Wide Web Consortium (W3C). (2018). *Web Content Accessibility Guidelines (WCAG) 2.1*. https://www.w3.org/TR/WCAG21/
