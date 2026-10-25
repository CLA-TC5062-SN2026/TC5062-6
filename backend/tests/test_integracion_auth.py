"""Integración A1 + A2: la API de A1 (datos sembrados, idempotencia, PUT/PATCH, Argon2) detrás de la seguridad JWT de A2.

Cubre lo que ninguna suite prueba por separado: roles sobre los datos de A1, cuentas creadas por A1 que inician sesión
con el verificador de A2, contraseña temporal, revocación inmediata de tokens y conformidad con el contrato integrado.
"""
import uuid

import pytest
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from tests.conftest import PASSWORD

API = '/api/v1'
LECTURAS = ['/alertas', '/cargas-alertas', '/zonas/EA-2026-001/marcas', '/zonas/EA-2026-001/ajustes',
            '/zonas/EA-2026-001/historial', '/trabajos/60000000-0000-4000-8000-000000000001']
CUENTA = {'nombre_completo': 'Cuenta Integrada', 'rol': 'analista_sig', 'password_temporal': 'Temporal-2026'}


def correo_nuevo():
    return f'int.{uuid.uuid4().hex[:10]}@ecoalert.pe'


def clave():
    return {'Idempotency-Key': str(uuid.uuid4())}


@pytest.mark.parametrize('ruta', LECTURAS)
def test_sin_token_o_con_token_invalido_las_lecturas_de_a1_responden_401(api_base, conforme, ruta):
    for cabeceras in (None, {'Authorization': 'Bearer no.es.un-jwt'}):
        r = api_base('GET', API + ruta, cabeceras=cabeceras)
        assert r.estado == 401 and r.json['codigo'] == 'NO_AUTENTICADO'
        assert r.cabeceras['WWW-Authenticate'].startswith('Bearer realm="ecoalert"')
        conforme('Error', r.json)


@pytest.mark.parametrize('ruta', LECTURAS)
def test_analista_y_coordinacion_leen_los_datos_de_a1(api, api_analista, ruta):
    assert api('GET', API + ruta).estado == 200
    assert api_analista('GET', API + ruta).estado == 200


def test_analista_no_gestiona_cuentas_y_la_coordinacion_si(api, api_analista, conforme, crear_usuario):
    objetivo = crear_usuario()[0].json['id']
    intentos = [('GET', '/usuarios', None, None), ('POST', '/usuarios', {**CUENTA, 'correo': correo_nuevo()}, clave()),
                ('GET', f'/usuarios/{objetivo}', None, None),
                ('PUT', f'/usuarios/{objetivo}', {'nombre_completo': 'X', 'rol': 'analista_sig', 'activo': True}, None),
                ('PATCH', f'/usuarios/{objetivo}', {'activo': False}, {'Content-Type': 'application/merge-patch+json'}),
                ('POST', '/auth/register', {**CUENTA, 'correo': correo_nuevo()}, clave())]
    for metodo, ruta, cuerpo, cabeceras in intentos:
        r = api_analista(metodo, API + ruta, cuerpo, cabeceras)
        assert r.estado == 403 and r.json['codigo'] == 'ROL_NO_PERMITIDO', (metodo, ruta)
        conforme('Error', r.json)
    assert api('GET', f'{API}/usuarios/{objetivo}').json['activo'] is True


def test_cuenta_creada_por_a1_inicia_sesion_cambia_su_contrasena_y_queda_en_argon2(api, api_base, bd, conforme, crear_usuario):
    r, cuerpo = crear_usuario()
    assert r.estado == 201
    acceso = api_base('POST', f'{API}/auth/login', {'correo': cuerpo['correo'], 'password': cuerpo['password_temporal']})
    assert acceso.estado == 200 and acceso.cabeceras['Cache-Control'] == 'no-store'
    conforme('SesionCreada', acceso.json)
    cuenta = {'Authorization': f"Bearer {acceso.json['access_token']}"}
    # Contrasena temporal: solo /auth/me, /auth/password y /auth/logout (RF-02-AC-4), tambien sobre las rutas de A1.
    bloqueo = api_base('GET', f'{API}/alertas', cabeceras=cuenta)
    assert bloqueo.estado == 403 and bloqueo.json['codigo'] == 'CAMBIO_PASSWORD_REQUERIDO'
    assert api_base('GET', f'{API}/auth/me', cabeceras=cuenta).estado == 200
    nueva = 'una-clave-nueva-2026'
    cambio = api_base('PUT', f'{API}/auth/password', {'password_actual': cuerpo['password_temporal'], 'password_nueva': nueva}, cuenta)
    assert cambio.estado == 204
    assert api_base('GET', f'{API}/alertas', cabeceras=cuenta).estado == 200
    assert bd('SELECT left(password_hash, 9) FROM usuarios WHERE correo = %s', (cuerpo['correo'],))[0][0] == '$argon2id'
    assert api_base('POST', f'{API}/auth/login', {'correo': cuerpo['correo'], 'password': cuerpo['password_temporal']}).estado == 401


@pytest.mark.parametrize('metodo', ['PUT', 'PATCH'])
def test_desactivar_con_put_o_patch_revoca_el_token_de_la_cuenta_al_instante(api, abrir_sesion, bd, metodo):
    victima = abrir_sesion('analista_sig')
    assert victima('GET', f'{API}/alertas').estado == 200
    cuerpo = {'nombre_completo': 'Cuenta Desactivada', 'rol': 'analista_sig', 'activo': False} if metodo == 'PUT' else {'activo': False}
    cabeceras = {'Content-Type': 'application/merge-patch+json'} if metodo == 'PATCH' else None
    assert api(metodo, f'{API}/usuarios/{victima.id}', cuerpo, cabeceras).estado == 200
    assert victima('GET', f'{API}/alertas').estado == 401
    assert bd('SELECT count(*) FROM sesiones WHERE usuario_id = %s AND revocada_en IS NULL', (victima.id,))[0][0] == 0


def test_logout_revoca_el_token_tambien_en_las_rutas_de_a1(abrir_sesion):
    sesion = abrir_sesion('coordinacion')
    assert sesion('GET', f'{API}/usuarios').estado == 200
    assert sesion('POST', f'{API}/auth/logout').estado == 204
    assert sesion('GET', f'{API}/usuarios').estado == 401


def test_register_es_alias_de_post_usuarios_con_la_misma_idempotencia(api, api_analista, conforme):
    cuerpo = {**CUENTA, 'correo': correo_nuevo()}
    cabeceras = clave()
    creada = api('POST', f'{API}/usuarios', cuerpo, cabeceras)
    repetida = api('POST', f'{API}/auth/register', cuerpo, cabeceras)
    assert (creada.estado, repetida.estado) == (201, 201) and repetida.json == creada.json
    assert repetida.cabeceras['Location'] == creada.cabeceras['Location']
    conforme('Usuario', repetida.json)
    assert api('POST', f'{API}/auth/register', cuerpo).estado == 400  # sin Idempotency-Key
    assert api('POST', f'{API}/auth/register', {**cuerpo, 'rol': 'coordinacion'}, cabeceras).json['codigo'] == 'IDEMPOTENCIA_CONFLICTO'
    assert api_analista('POST', f'{API}/auth/register', cuerpo, clave()).estado == 403


def test_me_cumple_el_contrato(api, conforme):
    r = api('GET', f'{API}/auth/me')
    assert r.estado == 200
    conforme('SesionActual', r.json)
    assert r.json['usuario']['id'] == api.id and 'password_hash' not in r.json['usuario']


def test_login_con_hash_bcrypt_heredado_migra_a_argon2_y_con_hash_ilegible_responde_401(api_base, nueva_cuenta, bd):
    bcrypt = PasswordHash((BcryptHasher(rounds=4),)).hash(PASSWORD)
    heredada = nueva_cuenta('analista_sig', hash_=bcrypt)
    assert api_base('POST', f'{API}/auth/login', {'correo': heredada, 'password': PASSWORD}).estado == 200
    assert bd('SELECT left(password_hash, 9) FROM usuarios WHERE correo = %s', (heredada,))[0][0] == '$argon2id'
    for hash_ in ('hash-de-prueba-no-valido', '', '$argon2id$basura'):
        ilegible = nueva_cuenta('analista_sig', hash_=hash_)
        r = api_base('POST', f'{API}/auth/login', {'correo': ilegible, 'password': PASSWORD})
        assert r.estado == 401 and r.json['codigo'] == 'CREDENCIALES_INVALIDAS'


def test_contrasenas_demasiado_largas_se_rechazan_sin_error_500(api_base, api, nueva_cuenta):
    r = api('POST', f'{API}/usuarios', {**CUENTA, 'correo': correo_nuevo(), 'password_temporal': 'x' * 5000}, clave())
    assert r.estado == 422 and r.json['detalles'][0]['campo'] == 'password_temporal'
    correo = nueva_cuenta('analista_sig', hash_=PasswordHash((BcryptHasher(rounds=4),)).hash(PASSWORD))
    assert api_base('POST', f'{API}/auth/login', {'correo': correo, 'password': 'x' * 100}).estado == 401
    assert api_base('POST', f'{API}/auth/login', {'correo': correo, 'password': 'x' * 5000}).estado == 422
