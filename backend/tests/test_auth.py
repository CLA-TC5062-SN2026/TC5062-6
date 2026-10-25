"""Módulo de autenticación: registro, login, /me, logout, cambio de contraseña y validación del JWT."""
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher

from app.config import get_settings
from tests.conftest import PASSWORD, bearer

LOGIN, REGISTER, ME = '/api/v1/auth/login', '/api/v1/auth/register', '/api/v1/auth/me'
NUEVA_CUENTA = {'nombre_completo': 'Ana Quispe Mamani', 'correo': 'ana.quispe@ecoalert.pe',
                'rol': 'analista_sig', 'password_temporal': 'Temporal-2026'}


def _claims(token):
    return jwt.decode(token, options={'verify_signature': False})


def _token_falsificado(claims, *, secreto=None, algoritmo='HS256'):
    cfg = get_settings()
    return jwt.encode(claims, secreto or cfg.jwt_secret.get_secret_value(), algorithm=algoritmo)


# --- Login -----------------------------------------------------------------

def test_RF_01_AC_1_login_exitoso_entrega_jwt_con_expiracion_explicita(client, crear_cuenta):
    correo = crear_cuenta('coordinacion')
    r = client.post(LOGIN, json={'correo': correo, 'password': PASSWORD})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['token_type'] == 'bearer'
    assert cuerpo['expires_in'] == 3600
    assert 'password_hash' not in cuerpo['usuario']
    claims = _claims(cuerpo['access_token'])
    assert claims['exp'] - claims['iat'] == 3600
    assert {'sub', 'rol', 'jti', 'iss', 'aud', 'nbf'} <= claims.keys()
    assert r.headers['cache-control'] == 'no-store'


def test_RF_01_AC_2_password_incorrecta_responde_401_generico(client, crear_cuenta):
    correo = crear_cuenta()
    r = client.post(LOGIN, json={'correo': correo, 'password': 'otra-clave-equivocada'})
    assert r.status_code == 401
    assert r.headers['content-type'] == 'application/problem+json'
    assert r.json()['codigo'] == 'CREDENCIALES_INVALIDAS'
    assert r.json()['mensaje'] == 'Usuario o contraseña incorrectos'
    assert r.headers['www-authenticate'].startswith('Bearer')


def test_RF_01_AC_3_cuenta_inexistente_responde_igual_que_password_incorrecta(client, crear_cuenta):
    correo = crear_cuenta()
    malo = client.post(LOGIN, json={'correo': correo, 'password': 'otra-clave-equivocada'})
    inexistente = client.post(LOGIN, json={'correo': 'nadie@ecoalert.pe', 'password': 'otra-clave-equivocada'})
    assert inexistente.status_code == 401
    assert inexistente.json() == malo.json()


def test_RF_02_AC_5_cuenta_desactivada_no_inicia_sesion(client, crear_cuenta):
    correo = crear_cuenta(activo=False)
    r = client.post(LOGIN, json={'correo': correo, 'password': PASSWORD})
    assert r.status_code == 401
    assert r.json()['codigo'] == 'CREDENCIALES_INVALIDAS'


def test_login_ignora_mayusculas_del_correo(client, crear_cuenta):
    correo = crear_cuenta()
    r = client.post(LOGIN, json={'correo': correo.upper(), 'password': PASSWORD})
    assert r.status_code == 200


def test_login_con_password_mayor_a_72_bytes_responde_401_y_no_500(client, crear_cuenta):
    correo = crear_cuenta()
    r = client.post(LOGIN, json={'correo': correo, 'password': 'x' * 100})
    assert r.status_code == 401


def test_login_migra_hash_argon2_heredado_a_bcrypt(client, crear_cuenta, conn):
    correo = crear_cuenta(hash_=PasswordHasher().hash(PASSWORD))
    assert client.post(LOGIN, json={'correo': correo, 'password': PASSWORD}).status_code == 200
    guardado = conn.execute('SELECT password_hash FROM usuarios WHERE correo=%s', (correo,)).fetchone()[0]
    assert guardado.startswith('$2b$12$')


# --- Registro --------------------------------------------------------------

def test_register_devuelve_201_sin_password(client, token_coordinacion, conn):
    r = client.post(REGISTER, json=NUEVA_CUENTA, headers=bearer(token_coordinacion))
    assert r.status_code == 201
    cuerpo = r.json()
    assert not {'password', 'password_temporal', 'password_hash'} & cuerpo.keys()
    assert cuerpo['debe_cambiar_password'] is True and cuerpo['activo'] is True
    assert r.headers['location'] == f"/api/v1/usuarios/{cuerpo['id']}"
    guardado = conn.execute('SELECT password_hash FROM usuarios WHERE id=%s', (cuerpo['id'],)).fetchone()[0]
    assert guardado.startswith('$2b$12$') and NUEVA_CUENTA['password_temporal'] not in guardado


def test_register_sin_token_responde_401(client):
    r = client.post(REGISTER, json=NUEVA_CUENTA)
    assert r.status_code == 401


def test_RF_02_AC_9_register_con_rol_analista_responde_403(client, token_analista):
    r = client.post(REGISTER, json=NUEVA_CUENTA, headers=bearer(token_analista))
    assert r.status_code == 403
    assert r.json()['codigo'] == 'ROL_NO_PERMITIDO'


def test_RF_02_AC_2_rol_invalido_responde_422(client, token_coordinacion):
    r = client.post(REGISTER, json={**NUEVA_CUENTA, 'rol': 'superadmin'}, headers=bearer(token_coordinacion))
    assert r.status_code == 422
    assert r.json()['detalles'][0]['campo'] == 'rol'


def test_RF_02_AC_3_password_de_11_caracteres_responde_422(client, token_coordinacion):
    r = client.post(REGISTER, json={**NUEVA_CUENTA, 'password_temporal': 'x' * 11},
                    headers=bearer(token_coordinacion))
    assert r.status_code == 422
    assert r.json()['detalles'][0]['campo'] == 'password_temporal'


def test_register_password_mayor_a_72_bytes_responde_422_y_no_500(client, token_coordinacion):
    r = client.post(REGISTER, json={**NUEVA_CUENTA, 'password_temporal': 'ñ' * 40},
                    headers=bearer(token_coordinacion))
    assert r.status_code == 422


def test_register_correo_duplicado_responde_409(client, token_coordinacion):
    client.post(REGISTER, json=NUEVA_CUENTA, headers=bearer(token_coordinacion))
    r = client.post(REGISTER, json={**NUEVA_CUENTA, 'correo': NUEVA_CUENTA['correo'].upper()},
                    headers=bearer(token_coordinacion))
    assert r.status_code == 409
    assert r.json()['codigo'] == 'CORREO_DUPLICADO'


def test_register_rechaza_campos_extra_como_password_hash(client, token_coordinacion):
    r = client.post(REGISTER, json={**NUEVA_CUENTA, 'password_hash': 'x', 'debe_cambiar_password': False},
                    headers=bearer(token_coordinacion))
    assert r.status_code == 422


# --- /me, logout y sesión ----------------------------------------------------

def test_me_devuelve_el_usuario_del_token(client, crear_cuenta, login):
    correo = crear_cuenta('coordinacion')
    r = client.get(ME, headers=bearer(login(correo)))
    assert r.status_code == 200
    assert r.json()['usuario']['correo'] == correo
    assert 'password_hash' not in r.json()['usuario']
    assert 'T' in r.json()['ultima_actividad']


def test_RF_01_AC_6_token_no_sirve_despues_de_logout(client, token_analista):
    assert client.post('/api/v1/auth/logout', headers=bearer(token_analista)).status_code == 204
    assert client.get(ME, headers=bearer(token_analista)).status_code == 401


def test_RF_01_AC_4_sesion_inactiva_31_minutos_responde_401(client, token_analista, conn):
    conn.execute("UPDATE sesiones SET ultima_actividad = now() - interval '31 minutes', creada_en = now() - interval '1 hour'")
    assert client.get(ME, headers=bearer(token_analista)).status_code == 401


def test_RF_01_AC_5_sesion_con_actividad_hace_29_minutos_sigue_vigente(client, token_analista, conn):
    conn.execute("UPDATE sesiones SET ultima_actividad = now() - interval '29 minutes', creada_en = now() - interval '1 hour'")
    assert client.get(ME, headers=bearer(token_analista)).status_code == 200


# --- Validación del JWT ------------------------------------------------------

def test_token_con_firma_alterada_responde_401(client, token_analista):
    cabecera, carga, firma = token_analista.split('.')
    alterado = f"{cabecera}.{carga}.{firma[:-2]}{'A' if firma[-2] != 'A' else 'B'}{firma[-1]}"
    r = client.get(ME, headers=bearer(alterado))
    assert r.status_code == 401
    assert 'invalid_token' in r.headers['www-authenticate']


def test_token_firmado_con_otro_secreto_responde_401(client, token_analista):
    falso = _token_falsificado(_claims(token_analista), secreto='otro-secreto-de-al-menos-32-bytes-xx')
    assert client.get(ME, headers=bearer(falso)).status_code == 401


def test_token_expirado_responde_401(client, token_analista):
    claims = _claims(token_analista)
    pasado = datetime.now(timezone.utc) - timedelta(hours=2)
    claims.update(iat=pasado, nbf=pasado, exp=pasado + timedelta(hours=1))
    assert client.get(ME, headers=bearer(_token_falsificado(claims))).status_code == 401


def test_token_sin_exp_responde_401(client, token_analista):
    claims = _claims(token_analista)
    del claims['exp']
    assert client.get(ME, headers=bearer(_token_falsificado(claims))).status_code == 401


def test_token_con_alg_none_responde_401(client, token_analista):
    sin_firma = jwt.encode(_claims(token_analista), key=None, algorithm='none')
    assert client.get(ME, headers=bearer(sin_firma)).status_code == 401


def test_token_con_otro_algoritmo_responde_401(client, token_analista):
    hs512 = _token_falsificado(_claims(token_analista), algoritmo='HS512')
    assert client.get(ME, headers=bearer(hs512)).status_code == 401


def test_token_valido_sin_sesion_registrada_responde_401(client, token_analista):
    # Firma correcta, pero el jti no corresponde a ninguna sesión emitida por el servidor.
    claims = {**_claims(token_analista), 'jti': '00000000-0000-4000-8000-000000000000'}
    assert client.get(ME, headers=bearer(_token_falsificado(claims))).status_code == 401


def test_cabecera_sin_esquema_bearer_responde_401(client, token_analista):
    r = client.get(ME, headers={'Authorization': f'Basic {token_analista}'})
    assert r.status_code == 401


# --- Contraseña temporal (RF-02-AC-4) ------------------------------------------

def test_RF_02_AC_4_password_temporal_bloquea_todo_salvo_me_password_y_logout(client, crear_cuenta, login):
    token = login(crear_cuenta(debe_cambiar=True))
    r = client.get('/api/v1/alertas', headers=bearer(token))
    assert r.status_code == 403
    assert r.json()['codigo'] == 'CAMBIO_PASSWORD_REQUERIDO'
    assert client.get(ME, headers=bearer(token)).status_code == 200
    r = client.put('/api/v1/auth/password', headers=bearer(token),
                   json={'password_actual': PASSWORD, 'password_nueva': 'una-clave-nueva-2026'})
    assert r.status_code == 204
    assert client.get('/api/v1/alertas', headers=bearer(token)).status_code == 200


def test_cambio_de_password_cierra_las_demas_sesiones(client, crear_cuenta, login):
    correo = crear_cuenta()
    otra_sesion, actual = login(correo), login(correo)
    client.put('/api/v1/auth/password', headers=bearer(actual),
               json={'password_actual': PASSWORD, 'password_nueva': 'una-clave-nueva-2026'})
    assert client.get(ME, headers=bearer(otra_sesion)).status_code == 401
    assert client.get(ME, headers=bearer(actual)).status_code == 200


def test_cambio_de_password_exige_la_actual_correcta(client, token_analista):
    r = client.put('/api/v1/auth/password', headers=bearer(token_analista),
                   json={'password_actual': 'no-es-la-actual', 'password_nueva': 'una-clave-nueva-2026'})
    assert r.status_code == 422
