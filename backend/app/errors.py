"""Errores del contrato: application/problem+json (RFC 9457) con `codigo` y `mensaje` obligatorios."""
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    def __init__(self, status: int, codigo: str, mensaje: str):
        super().__init__(mensaje)
        self.status, self.codigo, self.mensaje = status, codigo, mensaje


def no_encontrado(mensaje: str) -> ApiError:
    return ApiError(404, 'NO_ENCONTRADO', mensaje)


def problema(status: int, codigo: str, mensaje: str, detalles=None, headers=None) -> JSONResponse:
    cuerpo = {'type': 'about:blank', 'title': HTTPStatus(status).phrase, 'status': status,
              'detail': mensaje, 'codigo': codigo, 'mensaje': mensaje}
    if detalles:
        cuerpo['detalles'] = detalles
    return JSONResponse(cuerpo, status_code=status, media_type='application/problem+json', headers=headers)


_PLANTILLAS = {
    'missing': 'Campo obligatorio',
    'extra_forbidden': 'Campo no permitido',
    'string_too_short': 'Debe tener al menos {min_length} caracteres',
    'string_too_long': 'Debe tener como máximo {max_length} caracteres',
    'greater_than_equal': 'Debe ser mayor o igual a {ge}',
    'less_than_equal': 'Debe ser menor o igual a {le}',
    'string_pattern_mismatch': 'No cumple el formato requerido',
    'uuid_parsing': 'Debe ser un UUID válido',
    'bool_parsing': 'Debe ser verdadero o falso',
    'int_parsing': 'Debe ser un número entero',
}


def _mensaje(error: dict) -> str:
    ctx = error.get('ctx', {})
    if error['type'] == 'literal_error':
        return 'Valores válidos: ' + ctx['expected'].replace("'", '').replace(' or ', ', ')
    if error['type'] == 'value_error':
        return str(ctx['error']) if 'error' in ctx else 'Correo electrónico no válido'
    plantilla = _PLANTILLAS.get(error['type'])
    return plantilla.format(**ctx) if plantilla else error['msg']


def registrar_errores(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error(request: Request, exc: ApiError):
        return problema(exc.status, exc.codigo, exc.mensaje)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        codigo, mensaje = {404: ('NO_ENCONTRADO', 'La ruta solicitada no existe'),
                           405: ('METODO_NO_PERMITIDO', 'Método no permitido para esta ruta')
                           }.get(exc.status_code, ('ERROR_HTTP', str(exc.detail)))
        return problema(exc.status_code, codigo, mensaje, headers=exc.headers)

    # 400: JSON ilegible o parámetro (ruta, query, cabecera) inválido; 422: cuerpo legible que incumple el esquema.
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        errores = exc.errors()
        if any(e['type'] == 'json_invalid' for e in errores):
            return problema(400, 'SOLICITUD_MAL_FORMADA', 'El cuerpo de la solicitud no es JSON válido')
        detalles = [{'campo': '.'.join(map(str, e['loc'][1:])) or 'cuerpo', 'mensaje': _mensaje(e)} for e in errores]
        if all(e['loc'][0] != 'body' for e in errores):
            return problema(400, 'SOLICITUD_MAL_FORMADA', 'Un parámetro de la solicitud no es válido', detalles)
        return problema(422, 'VALIDACION', 'La solicitud contiene datos no válidos', detalles)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        return problema(500, 'ERROR_INTERNO', 'Ocurrió un error inesperado. Intenta de nuevo más tarde.')
