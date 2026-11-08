// Cliente HTTP sobre fetch con interceptores al estilo de axios.
//
// Responsabilidades (un solo lugar para todo lo transversal a las llamadas a la API):
// - Construir la URL a partir de la URL base y los parámetros de consulta.
// - Ejecutar los interceptores de solicitud (p. ej. agregar el JWT) antes de cada petición.
// - Aplicar un tiempo máximo de espera.
// - Convertir errores de red y respuestas HTTP de error en ApiError, y pasarlos por los
//   interceptores de error (p. ej. cerrar la sesión ante un 401) antes de lanzarlos.
//
// Los servicios por recurso (authService, alertasService) solo declaran método, ruta y parámetros.

import {
  ERROR_RED,
  RESPUESTA_INVALIDA,
  TIEMPO_AGOTADO,
  errorDesdeRespuesta,
  errorSinRespuesta,
} from './apiError.js';

const TIPOS_JSON = /^application\/(?:[\w.+-]+\+)?json\b/i;

function construirUrl(baseURL, ruta, params) {
  const url = `${baseURL}${ruta.startsWith('/') ? ruta : `/${ruta}`}`;
  if (!params) return url;
  const consulta = new URLSearchParams();
  Object.entries(params).forEach(([clave, valor]) => {
    // Los filtros vacíos no se envían: el backend aplica su valor por defecto.
    if (valor !== undefined && valor !== null && valor !== '') consulta.append(clave, String(valor));
  });
  const texto = consulta.toString();
  return texto ? `${url}?${texto}` : url;
}

async function leerCuerpo(response) {
  if (response.status === 204 || response.status === 205) return null;
  const tipo = response.headers.get('Content-Type') ?? '';
  if (!TIPOS_JSON.test(tipo)) return null;
  try {
    return await response.json();
  } catch {
    return undefined; // Cuerpo JSON declarado pero ilegible.
  }
}

/** Combina la señal del llamador con el tiempo máximo; indica cuál de las dos abortó. */
function controlarTiempo(senalExterna, timeoutMs) {
  const controlador = new AbortController();
  let agotado = false;
  const temporizador = setTimeout(() => {
    agotado = true;
    controlador.abort();
  }, timeoutMs);
  const abortarPorLlamador = () => controlador.abort(senalExterna.reason);
  if (senalExterna) {
    if (senalExterna.aborted) abortarPorLlamador();
    else senalExterna.addEventListener('abort', abortarPorLlamador, { once: true });
  }
  return {
    signal: controlador.signal,
    tiempoAgotado: () => agotado,
    liberar() {
      clearTimeout(temporizador);
      senalExterna?.removeEventListener('abort', abortarPorLlamador);
    },
  };
}

export function createHttpClient({ baseURL, timeoutMs, fetchImpl = (...args) => fetch(...args) }) {
  const interceptoresSolicitud = [];
  const interceptoresError = [];

  function registrar(lista, fn) {
    lista.push(fn);
    return () => {
      const indice = lista.indexOf(fn);
      if (indice >= 0) lista.splice(indice, 1);
    };
  }

  async function notificarError(error, config) {
    for (const interceptor of interceptoresError) {
      // Un interceptor que falla no debe ocultar el error original al componente.
      try {
        await interceptor(error, config);
      } catch {
        /* ignorado a propósito */
      }
    }
    return error;
  }

  async function request(ruta, opciones = {}) {
    const headers = new Headers({ Accept: 'application/json, application/problem+json' });
    new Headers(opciones.headers).forEach((valor, clave) => headers.set(clave, valor));
    let config = { method: 'GET', timeoutMs, ...opciones, headers, ruta };
    for (const interceptor of interceptoresSolicitud) {
      config = (await interceptor(config)) ?? config;
    }

    let cuerpo;
    if (config.body !== undefined && config.body !== null) {
      cuerpo = JSON.stringify(config.body);
      if (!config.headers.has('Content-Type')) config.headers.set('Content-Type', 'application/json');
    }

    const tiempo = controlarTiempo(config.signal, config.timeoutMs);
    let response;
    try {
      response = await fetchImpl(construirUrl(baseURL, ruta, config.params), {
        method: config.method,
        headers: config.headers,
        body: cuerpo,
        signal: tiempo.signal,
        // El JWT viaja en Authorization; no se envían cookies, así no hay superficie de CSRF.
        credentials: 'omit',
        cache: 'no-store',
      });
    } catch (causa) {
      // Abortado por el llamador (p. ej. el componente se desmontó): no es un error para el usuario.
      if (config.signal?.aborted) throw causa;
      const codigo = tiempo.tiempoAgotado() ? TIEMPO_AGOTADO : ERROR_RED;
      throw await notificarError(errorSinRespuesta(codigo, causa), config);
    } finally {
      tiempo.liberar();
    }

    const datos = await leerCuerpo(response);
    if (!response.ok) {
      throw await notificarError(errorDesdeRespuesta(response, datos ?? null), config);
    }
    if (datos === undefined) {
      throw await notificarError(errorSinRespuesta(RESPUESTA_INVALIDA), config);
    }
    return datos;
  }

  return {
    interceptors: {
      request: { use: (fn) => registrar(interceptoresSolicitud, fn) },
      error: { use: (fn) => registrar(interceptoresError, fn) },
    },
    request,
    get: (ruta, opciones) => request(ruta, { ...opciones, method: 'GET' }),
    post: (ruta, body, opciones) => request(ruta, { ...opciones, method: 'POST', body }),
    put: (ruta, body, opciones) => request(ruta, { ...opciones, method: 'PUT', body }),
  };
}
