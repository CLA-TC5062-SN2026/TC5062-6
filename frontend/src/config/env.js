// Configuración del cliente leída de variables de entorno de Vite (12-Factor App, factor III).
// Las variables VITE_* se incrustan en el bundle y son visibles en el navegador: nunca guardar secretos aquí.

const DEFAULT_API_URL = '/api/v1';
const DEFAULT_TIMEOUT_MS = 15000;

function normalizarUrlBase(valor) {
  const url = (valor ?? '').trim() || DEFAULT_API_URL;
  // Sin barra final: los servicios construyen las rutas como `${API_URL}/recurso`.
  return url.replace(/\/+$/, '');
}

function leerEntero(valor, porDefecto) {
  const numero = Number.parseInt(valor, 10);
  return Number.isFinite(numero) && numero > 0 ? numero : porDefecto;
}

export const API_URL = normalizarUrlBase(import.meta.env.VITE_API_URL);
export const API_TIMEOUT_MS = leerEntero(import.meta.env.VITE_API_TIMEOUT_MS, DEFAULT_TIMEOUT_MS);
