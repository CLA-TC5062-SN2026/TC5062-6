import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

/**
 * Content-Security-Policy del bundle de producción (mitiga XSS, que es la principal amenaza para un
 * token guardado en el navegador). Solo se inyecta en `vite build`: el servidor de desarrollo usa
 * scripts en línea para el recargado en caliente. En producción conviene enviarla además como cabecera
 * HTTP desde Nginx, que también admite `frame-ancestors`.
 */
function cspDeProduccion(apiUrl) {
  const origenApi = /^https?:\/\//i.test(apiUrl) ? ` ${new URL(apiUrl).origin}` : '';
  const politica = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self'",
    "img-src 'self' data:",
    `connect-src 'self'${origenApi}`,
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join('; ');
  return {
    name: 'ecoalert-csp',
    apply: 'build',
    transformIndexHtml: () => [
      { tag: 'meta', attrs: { 'http-equiv': 'Content-Security-Policy', content: politica }, injectTo: 'head-prepend' },
    ],
  };
}

export default defineConfig(({ mode }) => {
  // El tercer argumento '' carga también variables sin prefijo VITE_. Solo se usan aquí, en Node:
  // Vite expone al navegador únicamente las VITE_*.
  const env = loadEnv(mode, process.cwd(), '');
  // Proxy de desarrollo: el navegador habla solo con el origen de Vite y Vite reenvía /api al backend.
  // Así frontend y API comparten origen (como en producción detrás de Nginx) y el backend no necesita CORS.
  const proxy = {
    '/api': { target: env.API_PROXY_TARGET || 'http://localhost:8000', changeOrigin: true },
  };

  return {
    plugins: [react(), tailwindcss(), cspDeProduccion(env.VITE_API_URL || '/api/v1')],
    server: { proxy },
    preview: { proxy },
    test: {
      environment: 'jsdom',
      setupFiles: './src/test/setup.js',
      css: false,
      restoreMocks: true,
      unstubGlobals: true,
    },
  };
});
