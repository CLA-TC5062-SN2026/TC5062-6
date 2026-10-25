"""Módulo de autenticación (RF-01, RF-02-AC-4): registro, login, sesión actual, logout y contraseña."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, Response

from app import db
from app.config import Settings, get_settings
from app.dependencies import REALM, Identidad, autenticar, solo_coordinacion
from app.errors import ApiError
from app.routers.usuarios import USER_FIELDS, insertar_usuario
from app.schemas import CambioPassword, CredencialesLogin, SesionActual, SesionCreada, Usuario, UsuarioCrear
from app.security import emitir_token, hashear, huella_token, verificar

# RFC 6749 §5.1: una respuesta que contiene un token no debe almacenarse en cachés.
SIN_CACHE = {'Cache-Control': 'no-store', 'Pragma': 'no-cache'}

publico = APIRouter(prefix='/auth', tags=['Autenticación'])
protegido = APIRouter(prefix='/auth', tags=['Autenticación'])


@publico.post('/login', response_model=SesionCreada)
def login(body: CredencialesLogin, response: Response, cfg: Settings = Depends(get_settings)):
    cuenta = db.run('SELECT id, rol, activo, password_hash FROM usuarios WHERE lower(correo)=lower(%s)',
                    (str(body.correo),), one=True)
    valida, hash_nuevo = verificar(body.password, cuenta['password_hash'] if cuenta else None)
    # Mismo mensaje para correo inexistente, contraseña incorrecta o cuenta desactivada
    # (RF-01-AC-2, RF-01-AC-3, RF-02-AC-5): la respuesta no revela qué falló.
    if not (cuenta and valida and cuenta['activo']):
        raise ApiError(401, 'CREDENCIALES_INVALIDAS', 'Usuario o contraseña incorrectos',
                       headers={'WWW-Authenticate': REALM})
    token, jti = emitir_token(cuenta['id'], cuenta['rol'], cfg)
    with db.transaction() as conn:
        if hash_nuevo:
            conn.execute('UPDATE usuarios SET password_hash=%s WHERE id=%s', (hash_nuevo, cuenta['id']))
        conn.execute('INSERT INTO sesiones (id, usuario_id, token_hash) VALUES (%s,%s,%s)',
                     (jti, cuenta['id'], huella_token(token)))
        usuario = conn.execute(f'SELECT {USER_FIELDS} FROM usuarios WHERE id=%s', (cuenta['id'],)).fetchone()
    response.headers.update(SIN_CACHE)
    return SesionCreada(access_token=token, token_type='bearer', expires_in=cfg.jwt_expiration,
                        inactividad_max_segundos=cfg.sesion_inactividad_segundos, usuario=usuario)


@protegido.post('/register', status_code=201, response_model=Usuario, dependencies=[Depends(solo_coordinacion)])
def register(body: UsuarioCrear, request: Request, response: Response, idempotency_key: Annotated[UUID, Header()]):
    # RF-02: solo Coordinación crea cuentas; no existe registro anónimo (RNF-01). Misma lógica que POST /usuarios.
    return insertar_usuario(body, request, response, idempotency_key)


# me, logout y password solo exigen sesión válida: son las únicas operaciones permitidas
# mientras la contraseña temporal no se haya cambiado (RF-02-AC-4).
@protegido.get('/me', response_model=SesionActual)
def me(identidad: Identidad = Depends(autenticar)):
    return SesionActual(usuario=identidad.usuario, ultima_actividad=identidad.ultima_actividad)


@protegido.post('/logout', status_code=204)
def logout(identidad: Identidad = Depends(autenticar)):
    # RF-01-AC-6: el jti queda revocado y el token deja de servir aunque su firma siga vigente.
    db.run('UPDATE sesiones SET revocada_en=now() WHERE id=%s', (identidad.jti,))


@protegido.put('/password', status_code=204)
def cambiar_password(body: CambioPassword, identidad: Identidad = Depends(autenticar)):
    usuario_id = identidad.usuario['id']
    cuenta = db.run('SELECT password_hash FROM usuarios WHERE id=%s', (usuario_id,), one=True)
    valida, _ = verificar(body.password_actual, cuenta['password_hash'])
    if not valida:
        raise ApiError(422, 'VALIDACION', 'La contraseña actual no es correcta')
    if body.password_nueva == body.password_actual:
        raise ApiError(422, 'VALIDACION', 'La contraseña nueva debe ser distinta de la actual')
    with db.transaction() as conn:
        conn.execute('UPDATE usuarios SET password_hash=%s, debe_cambiar_password=FALSE WHERE id=%s',
                     (hashear(body.password_nueva), usuario_id))
        # Las demás sesiones se cierran: quien conociera la contraseña anterior pierde el acceso.
        conn.execute('''UPDATE sesiones SET revocada_en=now()
                        WHERE usuario_id=%s AND id<>%s AND revocada_en IS NULL''', (usuario_id, identidad.jti))
