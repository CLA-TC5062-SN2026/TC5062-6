"""Middleware de autenticación y autorización, implementado como dependencias de FastAPI.

`autenticar` se aplica a nivel de router a todo `/api/v1` excepto `POST /auth/login`, de modo que
una ruta nueva queda protegida aunque se olvide declararla (denegación por defecto).
`RequiereRol` añade el control por rol de la columna `x-roles` del contrato.
"""
from dataclasses import dataclass
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import db
from app.config import Settings, get_settings
from app.errors import fail
from app.security import decodificar_token, huella_token

ANALISTA_SIG = 'analista_sig'
COORDINACION = 'coordinacion'
REALM = 'Bearer realm="ecoalert"'

# auto_error=False: el 401 se construye aquí con el formato del contrato y WWW-Authenticate.
_bearer = HTTPBearer(auto_error=False, scheme_name='BearerAuth')

# Una sola sentencia valida la sesión y renueva su actividad, sin carreras entre lectura y escritura.
# El rol y el estado se leen de la base de datos, no del token: un cambio de rol o una
# desactivación surten efecto en la siguiente petición.
_SQL_SESION = '''
UPDATE sesiones s SET ultima_actividad = now()
FROM usuarios u
WHERE s.id = %(jti)s AND s.usuario_id = %(sub)s AND s.token_hash = %(huella)s
  AND u.id = s.usuario_id AND u.activo
  AND s.revocada_en IS NULL
  AND s.ultima_actividad > now() - make_interval(secs => %(inactividad)s)
RETURNING u.id, u.nombre_completo, u.correo, u.rol, u.activo, u.debe_cambiar_password,
          u.creado_en, s.ultima_actividad
'''


@dataclass(frozen=True)
class Identidad:
    usuario: dict
    jti: UUID
    ultima_actividad: object

    @property
    def rol(self) -> str:
        return self.usuario['rol']


def _no_autenticado(con_token: bool):
    # RFC 6750 §3.1: sin credenciales no se incluye código de error; con token inválido, invalid_token.
    cabecera = f'{REALM}, error="invalid_token"' if con_token else REALM
    fail(401, 'La sesión expiró o no es válida. Inicia sesión de nuevo.', 'NO_AUTENTICADO',
         headers={'WWW-Authenticate': cabecera})


def autenticar(credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
               cfg: Settings = Depends(get_settings)) -> Identidad:
    if credenciales is None:
        _no_autenticado(con_token=False)
    token = credenciales.credentials
    try:
        claims = decodificar_token(token, cfg)
        jti, sub = UUID(claims['jti']), UUID(claims['sub'])
    except (jwt.InvalidTokenError, ValueError):
        _no_autenticado(con_token=True)
    fila = db.run(_SQL_SESION, {'jti': jti, 'sub': sub, 'huella': huella_token(token),
                                'inactividad': cfg.sesion_inactividad_segundos}, one=True)
    if not fila:
        _no_autenticado(con_token=True)
    ultima_actividad = fila.pop('ultima_actividad')
    return Identidad(usuario=fila, jti=jti, ultima_actividad=ultima_actividad)


class RequiereRol:
    """Autoriza si el rol del usuario está en `roles` y ya cambió su contraseña temporal."""

    def __init__(self, *roles: str):
        self.roles = frozenset(roles)

    def __call__(self, identidad: Identidad = Depends(autenticar)) -> Identidad:
        # El rol se evalúa primero: es una negativa permanente; el cambio de contraseña es remediable.
        if identidad.rol not in self.roles:
            fail(403, 'Tu rol no permite realizar esta acción', 'ROL_NO_PERMITIDO')
        if identidad.usuario['debe_cambiar_password']:
            fail(403, 'Debes definir una contraseña nueva antes de continuar', 'CAMBIO_PASSWORD_REQUERIDO')
        return identidad


cualquier_rol = RequiereRol(ANALISTA_SIG, COORDINACION)
solo_coordinacion = RequiereRol(COORDINACION)
