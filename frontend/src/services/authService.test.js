import { describe, expect, it, vi } from 'vitest';
import { SESION_CREADA, USUARIO, jsonResponse, problemaResponse } from '../test/respuestas.js';
import { onSesionExpirada } from './api.js';
import { authService } from './authService.js';
import { tokenStorage } from './tokenStorage.js';

describe('authService e interceptores de api', () => {
  it('login guarda el token y no envía Authorization', async () => {
    const fetchMock = vi.fn().mockImplementation(async () => jsonResponse(SESION_CREADA));
    vi.stubGlobal('fetch', fetchMock);

    const usuario = await authService.login({ correo: ' ana.quispe@ecoalert.pe ', password: 'secreta' });

    expect(usuario).toEqual(USUARIO);
    expect(tokenStorage.obtener()).toBe(SESION_CREADA.access_token);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/v1/auth/login');
    expect(init.headers.has('Authorization')).toBe(false);
    expect(JSON.parse(init.body)).toEqual({ correo: 'ana.quispe@ecoalert.pe', password: 'secreta' });
  });

  it('un 401 en el login muestra el mensaje de credenciales y no dispara "sesión expirada"', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () =>
      problemaResponse(401, 'CREDENCIALES_INVALIDAS', 'Usuario o contraseña incorrectos'),
    ));
    const expirada = vi.fn();
    const cancelar = onSesionExpirada(expirada);

    const error = await authService.login({ correo: 'a@b.pe', password: 'x' }).catch((e) => e);

    cancelar();
    expect(error.message).toBe('Usuario o contraseña incorrectos');
    expect(expirada).not.toHaveBeenCalled();
    expect(tokenStorage.obtener()).toBeNull();
  });

  it('el interceptor agrega el JWT a las operaciones protegidas', async () => {
    tokenStorage.guardar('jwt-vigente', 3600);
    const fetchMock = vi.fn().mockImplementation(async () => jsonResponse({ usuario: USUARIO, ultima_actividad: 'x' }));
    vi.stubGlobal('fetch', fetchMock);

    await authService.obtenerSesionActual();

    expect(fetchMock.mock.calls[0][1].headers.get('Authorization')).toBe('Bearer jwt-vigente');
  });

  it('un 401 en una operación protegida borra el token y avisa a los suscriptores', async () => {
    tokenStorage.guardar('jwt-revocado', 3600);
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () =>
      problemaResponse(401, 'NO_AUTENTICADO', 'La sesión expiró o no es válida. Inicia sesión de nuevo.'),
    ));
    const expirada = vi.fn();
    const cancelar = onSesionExpirada(expirada);

    await authService.obtenerSesionActual().catch(() => {});

    cancelar();
    expect(tokenStorage.obtener()).toBeNull();
    expect(expirada).toHaveBeenCalledTimes(1);
  });

  it('logout borra el token local aunque el servidor no responda', async () => {
    tokenStorage.guardar('jwt', 3600);
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    await authService.logout().catch(() => {});

    expect(tokenStorage.obtener()).toBeNull();
  });
});

describe('tokenStorage', () => {
  it('descarta un token vencido', () => {
    tokenStorage.guardar('jwt', 1); // vence dentro del margen de seguridad
    expect(tokenStorage.obtener()).toBeNull();
    expect(window.sessionStorage.getItem('ecoalert.sesion')).toBeNull();
  });

  it('usa sessionStorage y no localStorage', () => {
    tokenStorage.guardar('jwt', 3600);
    expect(window.sessionStorage.getItem('ecoalert.sesion')).toContain('jwt');
    expect(window.localStorage.length).toBe(0);
  });
});
