// Instancia única del cliente HTTP de la aplicación y sus interceptores.
// Todos los servicios por recurso importan `api` desde aquí; ningún componente llama a fetch directamente.

import { API_TIMEOUT_MS, API_URL } from '../config/env.js';
import { createHttpClient } from './httpClient.js';
import { tokenStorage } from './tokenStorage.js';

export { API_URL };

export const api = createHttpClient({ baseURL: API_URL, timeoutMs: API_TIMEOUT_MS });

// --- Interceptor de solicitud: agrega `Authorization: Bearer <JWT>` (RNF-01) ---
// Las operaciones públicas (solo POST /auth/login) lo omiten con `skipAuth: true`.
api.interceptors.request.use((config) => {
  if (config.skipAuth) return config;
  const token = tokenStorage.obtener();
  if (token) config.headers.set('Authorization', `Bearer ${token}`);
  return config;
});

// --- Interceptor de error: un 401 significa que la sesión ya no sirve ---
// (token vencido, sesión inactiva más de 30 min, sesión revocada o cuenta desactivada).
// Se borra el token y se avisa a quien esté suscrito (AuthContext), que redirige al login.
// El login lo desactiva con `skipSessionHandling`: allí un 401 significa credenciales incorrectas.
const suscriptores = new Set();

api.interceptors.error.use((error, config) => {
  if (error.status !== 401 || config.skipSessionHandling) return;
  tokenStorage.limpiar();
  suscriptores.forEach((notificar) => notificar(error));
});

/** Suscribe una función al evento "sesión expirada". Devuelve la función para cancelar la suscripción. */
export function onSesionExpirada(notificar) {
  suscriptores.add(notificar);
  return () => suscriptores.delete(notificar);
}
