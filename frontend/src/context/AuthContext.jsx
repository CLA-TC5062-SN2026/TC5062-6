// Estado de la sesión compartido por la aplicación (Context API, según decision_stack_frontend.md).
// Solo guarda lo que varias vistas necesitan: el usuario autenticado y el estado de la verificación.
// El token no vive aquí: lo administra tokenStorage y lo agrega el interceptor de services/api.js.

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { onSesionExpirada } from '../services/api.js';
import { authService } from '../services/authService.js';

export const ESTADO_SESION = Object.freeze({
  VERIFICANDO: 'verificando',
  AUTENTICADO: 'autenticado',
  ANONIMO: 'anonimo',
});

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [estado, setEstado] = useState(() =>
    authService.tieneToken() ? ESTADO_SESION.VERIFICANDO : ESTADO_SESION.ANONIMO,
  );
  const [usuario, setUsuario] = useState(null);
  // Mensaje para la pantalla de login cuando la sesión terminó sin que el usuario la cerrara.
  const [aviso, setAviso] = useState(null);
  // true tras "Cerrar sesión": la ruta protegida no recuerda la página anterior, así la próxima persona que
  // inicie sesión en la pestaña llega al panel y no a la última página de la cuenta anterior.
  const [cierreVoluntario, setCierreVoluntario] = useState(false);

  // Al recargar la página con un token guardado, se confirma con el servidor (GET /auth/me) antes de
  // mostrar contenido protegido: el token pudo revocarse o expirar por inactividad.
  useEffect(() => {
    if (!authService.tieneToken()) return undefined;
    const controlador = new AbortController();
    authService
      .obtenerSesionActual({ signal: controlador.signal })
      .then((actual) => {
        setUsuario(actual);
        setEstado(ESTADO_SESION.AUTENTICADO);
      })
      .catch((error) => {
        if (controlador.signal.aborted) return;
        setUsuario(null);
        setEstado(ESTADO_SESION.ANONIMO);
        setAviso(error.message);
      });
    return () => controlador.abort();
  }, []);

  // Cualquier 401 en cualquier llamada termina la sesión en toda la aplicación.
  useEffect(
    () =>
      onSesionExpirada((error) => {
        setUsuario(null);
        setEstado(ESTADO_SESION.ANONIMO);
        setAviso(error.message);
        setCierreVoluntario(false);
      }),
    [],
  );

  const login = useCallback(async (credenciales) => {
    const autenticado = await authService.login(credenciales);
    setUsuario(autenticado);
    setEstado(ESTADO_SESION.AUTENTICADO);
    setAviso(null);
    setCierreVoluntario(false);
    return autenticado;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // Aunque el servidor no responda, el token local ya se borró: la sesión termina en el cliente.
    } finally {
      setUsuario(null);
      setEstado(ESTADO_SESION.ANONIMO);
      setAviso(null);
      setCierreVoluntario(true);
    }
  }, []);

  // Vuelve a leer el usuario (p. ej. tras cambiar la contraseña temporal, debe_cambiar_password pasa a false).
  const refrescarUsuario = useCallback(async () => {
    const actual = await authService.obtenerSesionActual();
    setUsuario(actual);
    return actual;
  }, []);

  const valor = useMemo(
    () => ({
      estado,
      usuario,
      aviso,
      cierreVoluntario,
      login,
      logout,
      refrescarUsuario,
      estaAutenticado: estado === ESTADO_SESION.AUTENTICADO,
    }),
    [estado, usuario, aviso, cierreVoluntario, login, logout, refrescarUsuario],
  );

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const contexto = useContext(AuthContext);
  if (!contexto) throw new Error('useAuth debe usarse dentro de <AuthProvider>');
  return contexto;
}
