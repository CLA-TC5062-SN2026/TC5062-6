// Servicio del recurso Autenticación (contrato: tag "Autenticación", RF-01).

import { api } from './api.js';
import { tokenStorage } from './tokenStorage.js';

export const authService = {
  /**
   * POST /auth/login — operationId iniciarSesion.
   * Guarda el JWT y devuelve el usuario autenticado. La contraseña no se conserva en ningún lugar.
   * @param {{correo: string, password: string}} credenciales
   */
  async login({ correo, password }) {
    const sesion = await api.post(
      '/auth/login',
      { correo: correo.trim(), password },
      // Operación pública; su 401 significa credenciales incorrectas, no sesión expirada.
      { skipAuth: true, skipSessionHandling: true },
    );
    tokenStorage.guardar(sesion.access_token, sesion.expires_in);
    return sesion.usuario;
  },

  /** GET /auth/me — operationId obtenerSesionActual. Valida el token guardado y devuelve el usuario. */
  async obtenerSesionActual({ signal } = {}) {
    const { usuario } = await api.get('/auth/me', { signal });
    return usuario;
  },

  /** POST /auth/logout — operationId cerrarSesion. Revoca el jti en el servidor; el token local se borra siempre. */
  async logout() {
    try {
      await api.post('/auth/logout', undefined, { skipSessionHandling: true });
    } finally {
      tokenStorage.limpiar();
    }
  },

  tieneToken() {
    return tokenStorage.obtener() !== null;
  },
};
