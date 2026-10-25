"""Errores como Problem Details (RFC 9457) con los miembros `codigo` y `mensaje` del contrato."""
import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

PROBLEM_JSON = 'application/problem+json'
CODIGOS = {
    400: 'SOLICITUD_MAL_FORMADA',
    401: 'NO_AUTENTICADO',
    403: 'ROL_NO_PERMITIDO',
    404: 'NO_ENCONTRADO',
    405: 'METODO_NO_PERMITIDO',
    409: 'CONFLICTO',
    415: 'TIPO_CONTENIDO_NO_SOPORTADO',
    422: 'VALIDACION',
    500: 'ERROR_INTERNO',
}


class ErrorApi(Exception):
    def __init__(self, status: int, codigo: str, mensaje: str, *, detalles=None, headers=None):
        super().__init__(mensaje)
        self.status, self.codigo, self.mensaje = status, codigo, mensaje
        self.detalles, self.headers = detalles, headers


def fail(status: int, mensaje: str, codigo: str | None = None, *, headers=None):
    raise ErrorApi(status, codigo or CODIGOS.get(status, f'HTTP_{status}'), mensaje, headers=headers)


def problema(status, codigo, mensaje, *, detalles=None, headers=None) -> JSONResponse:
    cuerpo = {'type': 'about:blank', 'title': HTTPStatus(status).phrase, 'status': status,
              'detail': mensaje, 'codigo': codigo, 'mensaje': mensaje}
    if detalles:
        cuerpo['detalles'] = detalles
    return JSONResponse(cuerpo, status_code=status, headers=headers, media_type=PROBLEM_JSON)


async def _error_api(request: Request, exc: ErrorApi):
    return problema(exc.status, exc.codigo, exc.mensaje, detalles=exc.detalles, headers=exc.headers)


async def _error_http(request: Request, exc: StarletteHTTPException):
    # Rutas inexistentes (404) y métodos no expuestos (405, RF-02-AC-7) también salen en el formato del contrato.
    mensaje = exc.detail if isinstance(exc.detail, str) else HTTPStatus(exc.status_code).phrase
    return problema(exc.status_code, CODIGOS.get(exc.status_code, f'HTTP_{exc.status_code}'), mensaje,
                    headers=getattr(exc, 'headers', None))


async def _error_validacion(request: Request, exc: RequestValidationError):
    errores = exc.errors()
    if any(e['type'] == 'json_invalid' for e in errores):
        return problema(400, CODIGOS[400], 'El cuerpo de la solicitud no es JSON válido')
    # Solo ubicación y mensaje: nunca se devuelve el valor recibido (podría ser una contraseña).
    detalles = [{'campo': '.'.join(map(str, e['loc'][1:] or e['loc'])), 'mensaje': e['msg']} for e in errores]
    return problema(422, CODIGOS[422], 'La solicitud contiene datos no válidos', detalles=detalles)


async def _error_inesperado(request: Request, exc: Exception):
    # El detalle va al log del servidor, nunca al cliente (OWASP: manejo seguro de errores).
    logger.exception('Error no controlado en %s %s', request.method, request.url.path)
    return problema(500, CODIGOS[500], 'Ocurrió un error inesperado. Intenta de nuevo más tarde.')


def registrar_manejadores(app: FastAPI) -> None:
    app.add_exception_handler(ErrorApi, _error_api)
    app.add_exception_handler(StarletteHTTPException, _error_http)
    app.add_exception_handler(RequestValidationError, _error_validacion)
    app.add_exception_handler(Exception, _error_inesperado)
