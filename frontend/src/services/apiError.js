// Error único de la capa de servicios. Todo fallo de red o de HTTP llega a los componentes como ApiError,
// con un `message` listo para mostrarse al usuario (RNF-06: mensajes en español).
//
// El backend responde los errores como application/problem+json (RFC 9457) con `codigo` y `mensaje`
// obligatorios (esquema `Error` del contrato). Este módulo traduce esa respuesta, o la ausencia de ella,
// a un mensaje útil: los componentes no interpretan códigos de estado.

export const ERROR_RED = 'ERROR_RED';
export const TIEMPO_AGOTADO = 'TIEMPO_AGOTADO';
export const RESPUESTA_INVALIDA = 'RESPUESTA_INVALIDA';

const MENSAJES_POR_ESTADO = {
  400: 'La solicitud no es válida. Revisa los datos e inténtalo de nuevo.',
  401: 'Tu sesión expiró o no es válida. Inicia sesión de nuevo.',
  403: 'No tienes permiso para realizar esta acción.',
  404: 'El recurso solicitado no existe.',
  409: 'La operación entra en conflicto con el estado actual de los datos.',
  415: 'El formato de la solicitud no es compatible.',
  422: 'Los datos enviados no son válidos.',
  429: 'Has realizado demasiadas solicitudes. Espera un momento e inténtalo de nuevo.',
  503: 'El servicio no está disponible en este momento. Inténtalo más tarde.',
};

const MENSAJE_ERROR_SERVIDOR = 'Ocurrió un error en el servidor. Inténtalo más tarde.';

const MENSAJES_POR_CODIGO = {
  [ERROR_RED]:
    'No se pudo conectar con el servidor. Verifica tu conexión a internet o que el backend esté en ejecución.',
  [TIEMPO_AGOTADO]: 'El servidor tardó demasiado en responder. Inténtalo de nuevo.',
  [RESPUESTA_INVALIDA]: 'El servidor envió una respuesta inesperada. Inténtalo más tarde.',
  CAMBIO_PASSWORD_REQUERIDO: 'Debes cambiar tu contraseña temporal antes de continuar.',
};

export class ApiError extends Error {
  constructor({ status = 0, codigo, message, detalles = [], retryAfter = null, cause } = {}) {
    super(message, { cause });
    this.name = 'ApiError';
    this.status = status;
    this.codigo = codigo;
    this.detalles = detalles;
    this.retryAfter = retryAfter;
  }

  get esErrorDeRed() {
    return this.codigo === ERROR_RED || this.codigo === TIEMPO_AGOTADO;
  }
}

function mensajeConEspera(mensaje, retryAfter) {
  return retryAfter ? `${mensaje} (reintenta en ${retryAfter} s)` : mensaje;
}

/**
 * Elige el mensaje para el usuario:
 * - 5xx: mensaje genérico; el detalle interno del servidor no se muestra (OWASP: no filtrar información).
 * - 4xx: el `mensaje` del contrato si existe (ya está en español y pensado para el usuario);
 *   si no, un mensaje genérico por código de estado.
 */
function mensajeParaUsuario(status, problema, retryAfter) {
  if (MENSAJES_POR_CODIGO[problema?.codigo]) return MENSAJES_POR_CODIGO[problema.codigo];
  // El backend siempre responde sus errores como problem+json. Un 5xx sin ese cuerpo, o un 502/504, viene del
  // intermediario (proxy de Vite o Nginx) porque no pudo llegar a la API: para el usuario es un problema de conexión.
  if (status === 502 || status === 504 || (status >= 500 && !problema)) return MENSAJES_POR_CODIGO[ERROR_RED];
  if (status >= 500 && status !== 503) return MENSAJE_ERROR_SERVIDOR;
  const mensaje = typeof problema?.mensaje === 'string' && problema.mensaje.trim()
    ? problema.mensaje
    : MENSAJES_POR_ESTADO[status] ?? MENSAJE_ERROR_SERVIDOR;
  return status === 429 || status === 503 ? mensajeConEspera(mensaje, retryAfter) : mensaje;
}

/** Construye un ApiError a partir de una respuesta HTTP con estado de error y su cuerpo ya leído. */
export function errorDesdeRespuesta(response, problema) {
  const retryAfter = response.headers.get('Retry-After');
  return new ApiError({
    status: response.status,
    codigo: problema?.codigo ?? `HTTP_${response.status}`,
    message: mensajeParaUsuario(response.status, problema, retryAfter),
    detalles: Array.isArray(problema?.detalles) ? problema.detalles : [],
    retryAfter,
  });
}

/** Construye un ApiError para fallos sin respuesta HTTP: sin red, CORS, DNS o tiempo agotado. */
export function errorSinRespuesta(codigo, cause) {
  return new ApiError({ status: 0, codigo, message: MENSAJES_POR_CODIGO[codigo], cause });
}

/** Garantiza que cualquier valor lanzado se presente como ApiError con mensaje para el usuario. */
export function comoApiError(error) {
  if (error instanceof ApiError) return error;
  return errorSinRespuesta(RESPUESTA_INVALIDA, error);
}
