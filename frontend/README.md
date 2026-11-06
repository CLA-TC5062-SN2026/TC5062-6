# EcoAlert Tambopata — Frontend

Scaffolding de la Parte 1: React + Vite + Tailwind CSS v4 + useState / Context API (reservados para cuando se necesiten).

## Requisitos

Node.js 20.19+ o 22.12+ y npm.

## Instalación y ejecución

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Abrir la dirección que indique Vite (normalmente `http://localhost:5173`). En GitHub Codespaces, abrir la pestaña **Ports** y seleccionar el puerto **5173**. Para la pantalla inicial no hace falta iniciar el backend.

## Verificación

1. El comando `npm run dev` debe mostrar que Vite está listo, sin errores.
2. El navegador debe mostrar el título «Frontend inicial configurado» y los estilos verdes de Tailwind.
3. Abrir las herramientas de desarrollador (F12), pestaña **Console**, y comprobar que no haya errores.
4. Ejecutar `npm run build` para comprobar la compilación de producción.

## Variable de entorno

`VITE_API_URL` define la URL base de la futura API REST de FastAPI. Se incluye en `.env.example` como plantilla; copiarla a `.env` y ajustar la dirección. En Vite las variables `VITE_*` son públicas en el frontend: **nunca incluir contraseñas o secretos**. Reiniciar `npm run dev` tras modificar `.env`.

## Video `scaffolding.mp4` (máximo 20 segundos)

Grabar una captura real de la pantalla de Codespaces/VS Code con terminal y navegador visibles. Mostrar el comando `npm run dev`, el mensaje de Vite y la página cargada; abrir la consola del navegador para demostrar que no hay errores. Guardar la grabación como `scaffolding.mp4` (duración máxima: 20 s).

La grabación debe realizarse en el entorno del equipo; no se incluye una demostración ficticia.
