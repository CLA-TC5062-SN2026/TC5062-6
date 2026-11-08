import { describe, expect, it, vi } from 'vitest';
import { jsonResponse, problemaResponse } from '../test/respuestas.js';
import { ApiError, ERROR_RED, TIEMPO_AGOTADO } from './apiError.js';
import { createHttpClient } from './httpClient.js';

function cliente(fetchImpl, opciones = {}) {
  return createHttpClient({ baseURL: '/api/v1', timeoutMs: 1000, fetchImpl, ...opciones });
}

describe('httpClient', () => {
  it('construye la URL con la base y omite los parámetros vacíos', async () => {
    const fetchImpl = vi.fn().mockImplementation(async () => jsonResponse({ ok: true }));
    await cliente(fetchImpl).get('/alertas', { params: { zona: '', limite: 10, presente: false, x: undefined } });
    expect(fetchImpl.mock.calls[0][0]).toBe('/api/v1/alertas?limite=10&presente=false');
  });

  it('aplica los interceptores de solicitud antes de llamar a fetch', async () => {
    const fetchImpl = vi.fn().mockImplementation(async () => jsonResponse({}));
    const http = cliente(fetchImpl);
    http.interceptors.request.use((config) => {
      config.headers.set('Authorization', 'Bearer abc');
      return config;
    });
    await http.get('/auth/me');
    expect(fetchImpl.mock.calls[0][1].headers.get('Authorization')).toBe('Bearer abc');
    expect(fetchImpl.mock.calls[0][1].credentials).toBe('omit');
  });

  it('envía el cuerpo como JSON', async () => {
    const fetchImpl = vi.fn().mockImplementation(async () => jsonResponse({}));
    await cliente(fetchImpl).post('/auth/login', { correo: 'a@b.pe' });
    const [, init] = fetchImpl.mock.calls[0];
    expect(init.body).toBe('{"correo":"a@b.pe"}');
    expect(init.headers.get('Content-Type')).toBe('application/json');
  });

  it('convierte un problem+json 4xx en ApiError con el mensaje del contrato', async () => {
    const fetchImpl = vi.fn().mockImplementation(async () => problemaResponse(404, 'NO_ENCONTRADO', 'No existe la zona EA-2026-999'));
    const error = await cliente(fetchImpl).get('/zonas/EA-2026-999').catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 404, codigo: 'NO_ENCONTRADO', message: 'No existe la zona EA-2026-999' });
  });

  it('no muestra al usuario el detalle interno de un 500', async () => {
    const fetchImpl = vi.fn().mockImplementation(async () => problemaResponse(500, 'ERROR_INTERNO', 'psycopg.OperationalError ...'));
    const error = await cliente(fetchImpl).get('/alertas').catch((e) => e);
    expect(error.message).toBe('Ocurrió un error en el servidor. Inténtalo más tarde.');
  });

  it('incluye el tiempo de espera de Retry-After en un 429', async () => {
    const fetchImpl = vi.fn().mockImplementation(async () =>
      problemaResponse(429, 'DEMASIADAS_SOLICITUDES', 'Demasiadas solicitudes', { 'Retry-After': '30' }),
    );
    const error = await cliente(fetchImpl).get('/alertas').catch((e) => e);
    expect(error.message).toBe('Demasiadas solicitudes (reintenta en 30 s)');
  });

  it('traduce un fallo de red en un mensaje útil para el usuario', async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
    const error = await cliente(fetchImpl).get('/alertas').catch((e) => e);
    expect(error.codigo).toBe(ERROR_RED);
    expect(error.esErrorDeRed).toBe(true);
    expect(error.message).toMatch(/No se pudo conectar con el servidor/);
  });

  it('trata un 5xx del proxy (backend caído, sin problem+json) como fallo de conexión', async () => {
    const fetchImpl = vi.fn().mockImplementation(async () => new Response('', { status: 500 }));
    const error = await cliente(fetchImpl).get('/alertas').catch((e) => e);
    expect(error.status).toBe(500);
    expect(error.message).toMatch(/No se pudo conectar con el servidor/);
  });

  it('corta la petición al superar el tiempo máximo', async () => {
    const fetchImpl = vi.fn((_url, { signal }) => new Promise((_resolve, reject) => {
      signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));
    const error = await cliente(fetchImpl, { timeoutMs: 10 }).get('/alertas').catch((e) => e);
    expect(error.codigo).toBe(TIEMPO_AGOTADO);
  });

  it('propaga la cancelación del llamador sin convertirla en error de usuario', async () => {
    const fetchImpl = vi.fn((_url, { signal }) => new Promise((_resolve, reject) => {
      signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));
    const controlador = new AbortController();
    const promesa = cliente(fetchImpl).get('/alertas', { signal: controlador.signal });
    controlador.abort();
    const error = await promesa.catch((e) => e);
    expect(error).not.toBeInstanceOf(ApiError);
    expect(error.name).toBe('AbortError');
  });

  it('pasa cada error por los interceptores de error una sola vez', async () => {
    const fetchImpl = vi.fn().mockImplementation(async () => problemaResponse(403, 'ROL_NO_PERMITIDO', 'Sin permiso'));
    const http = cliente(fetchImpl);
    const interceptor = vi.fn();
    http.interceptors.error.use(interceptor);
    await http.get('/usuarios').catch(() => {});
    expect(interceptor).toHaveBeenCalledTimes(1);
    expect(interceptor.mock.calls[0][0].status).toBe(403);
  });
});
