"""Pruebas HTTP del recurso Usuarios: POST, GET, PUT, PATCH, idempotencia (HMAC) y concurrencia.

Cada prueba crea sus propios usuarios con correos unicos; las bases de datos `*_test` son de uso exclusivo de estas pruebas.
"""
import concurrent.futures as cf
import hashlib
import hmac
import json
import os
import re
import uuid

import pytest

USUARIOS = '/api/v1/usuarios'
MERGE_PATCH = {'Content-Type': 'application/merge-patch+json'}


def es_problema(respuesta, estado, codigo, conforme):
    assert respuesta.estado == estado
    assert respuesta.cabeceras['Content-Type'].startswith('application/problem+json')
    conforme('Error', respuesta.json)
    assert respuesta.json['codigo'] == codigo, respuesta.json


def enviar(api, metodo, usuario_id, cambios):
    return api(metodo, f'{USUARIOS}/{usuario_id}', cambios, MERGE_PATCH if metodo == 'PATCH' else None)


def cambios_de(metodo, accion, nombre='Coordinacion de Prueba'):
    """Cuerpo valido para PUT (completo) o PATCH (parcial) que desactiva o quita el rol de coordinacion."""
    base = {'activo': False} if accion == 'desactivar' else {'rol': 'analista_sig'}
    return {'nombre_completo': nombre, 'rol': 'coordinacion', 'activo': True, **base} if metodo == 'PUT' else base


def cuerpo_nuevo(correo):
    return {'nombre_completo': 'Usuario Concurrente', 'correo': correo, 'rol': 'analista_sig', 'password_temporal': 'Temporal-2026'}


def dejar_solo(bd, *ids):
    """Deja activas unicamente las cuentas de coordinacion indicadas (aisla la regla RF-02-AC-8)."""
    bd("UPDATE usuarios SET activo = false WHERE rol = 'coordinacion' AND activo AND id <> ALL(%s::uuid[])", (list(ids),))


# --------------------------------------------------------------------------- POST y GET

def test_post_crea_usuario_y_persiste(api, bd, conforme, crear_usuario):
    r, cuerpo = crear_usuario(nombre_completo='  Ana Nueva  ')
    assert r.estado == 201
    conforme('Usuario', r.json)
    assert r.json['nombre_completo'] == 'Ana Nueva'
    assert r.cabeceras['Location'] == f"{USUARIOS}/{r.json['id']}"
    assert 'password_hash' not in r.json and cuerpo['password_temporal'] not in json.dumps(r.json)
    fila = bd("SELECT nombre_completo, correo, rol, activo, debe_cambiar_password, left(password_hash, 9), "
              "password_hash <> %s FROM usuarios WHERE id = %s", (cuerpo['password_temporal'], r.json['id']))[0]
    assert fila == ('Ana Nueva', cuerpo['correo'], 'analista_sig', True, True, '$argon2id', True)
    consulta = api('GET', r.cabeceras['Location'])
    assert consulta.estado == 200 and consulta.json == r.json


@pytest.mark.parametrize('cambio', [
    {'correo': 'sin-arroba'}, {'password_temporal': 'corta'}, {'rol': 'superadmin'},
    {'nombre_completo': '   '}, {'administrador': True},
], ids=['correo', 'password', 'rol', 'nombre', 'campo_extra'])
def test_post_rechaza_cuerpos_invalidos_con_422(api, bd, conforme, crear_usuario, cambio):
    r, cuerpo = crear_usuario(**cambio)
    es_problema(r, 422, 'VALIDACION', conforme)
    assert r.json['detalles']
    assert bd('SELECT count(*) FROM usuarios WHERE correo = %s', (cuerpo['correo'],))[0][0] == 0


def test_post_correo_duplicado_409_sin_distinguir_mayusculas(api, conforme, crear_usuario):
    r, cuerpo = crear_usuario()
    assert r.estado == 201
    otra, _ = crear_usuario(correo=cuerpo['correo'].upper())
    es_problema(otra, 409, 'CORREO_DUPLICADO', conforme)


def test_post_json_ilegible_400_y_cabecera_idempotency_key(api, conforme, crear_usuario):
    r = api('POST', USUARIOS, crudo=b'{no es json', cabeceras={'Idempotency-Key': str(uuid.uuid4())})
    es_problema(r, 400, 'SOLICITUD_MAL_FORMADA', conforme)
    r, cuerpo = crear_usuario(clave='no-es-uuid')
    es_problema(r, 400, 'SOLICITUD_MAL_FORMADA', conforme)
    sin_clave = api('POST', USUARIOS, {**cuerpo, 'correo': f'x.{uuid.uuid4().hex[:10]}@ecoalert.pe'})
    es_problema(sin_clave, 400, 'SOLICITUD_MAL_FORMADA', conforme)


def test_get_lista_filtra_por_activo_y_valida_parametro(api, bd, conforme, crear_usuario):
    crear_usuario()
    for filtro, esperado in (('true', True), ('false', False)):
        r = api('GET', f'{USUARIOS}?activo={filtro}')
        assert r.estado == 200
        for usuario in r.json:
            conforme('Usuario', usuario)
            assert usuario['activo'] is esperado
        assert len(r.json) == bd('SELECT count(*) FROM usuarios WHERE activo = %s', (esperado,))[0][0]
    es_problema(api('GET', f'{USUARIOS}?activo=quizas'), 400, 'SOLICITUD_MAL_FORMADA', conforme)


def test_get_usuario_inexistente_404_e_id_invalido_400(api, conforme):
    es_problema(api('GET', f'{USUARIOS}/{uuid.uuid4()}'), 404, 'NO_ENCONTRADO', conforme)
    es_problema(api('GET', f'{USUARIOS}/no-es-uuid'), 400, 'SOLICITUD_MAL_FORMADA', conforme)


def test_delete_fisico_no_existe_405(api, bd, conforme, crear_usuario):
    r, _ = crear_usuario()
    borrado = api('DELETE', f"{USUARIOS}/{r.json['id']}")
    es_problema(borrado, 405, 'METODO_NO_PERMITIDO', conforme)
    assert 'DELETE' not in borrado.cabeceras['Allow']
    assert bd('SELECT count(*) FROM usuarios WHERE id = %s', (r.json['id'],))[0][0] == 1


# --------------------------------------------------------------------------- PUT

def test_put_reemplaza_campos_editables_y_persiste(api, bd, conforme, crear_usuario):
    r, _ = crear_usuario()
    usuario = r.json
    hash_antes = bd('SELECT password_hash FROM usuarios WHERE id = %s', (usuario['id'],))[0][0]
    cuerpo = {'nombre_completo': '  Ñandú Pérez (reemplazado) ', 'rol': 'coordinacion', 'activo': False}
    p = api('PUT', f"{USUARIOS}/{usuario['id']}", cuerpo)
    assert p.estado == 200
    conforme('Usuario', p.json)
    assert (p.json['nombre_completo'], p.json['rol'], p.json['activo']) == ('Ñandú Pérez (reemplazado)', 'coordinacion', False)
    for inmutable in ('id', 'correo', 'creado_en', 'debe_cambiar_password'):
        assert p.json[inmutable] == usuario[inmutable]
    fila = bd('SELECT nombre_completo, rol, activo, password_hash FROM usuarios WHERE id = %s', (usuario['id'],))[0]
    assert fila == ('Ñandú Pérez (reemplazado)', 'coordinacion', False, hash_antes)
    assert api('GET', f"{USUARIOS}/{usuario['id']}").json == p.json
    repetido = api('PUT', f"{USUARIOS}/{usuario['id']}", cuerpo)
    assert repetido.estado == 200 and repetido.json == p.json  # mismo estado al repetir


@pytest.mark.parametrize('faltante', ['nombre_completo', 'rol', 'activo'])
def test_put_exige_los_tres_campos(api, bd, conforme, crear_usuario, faltante):
    r, _ = crear_usuario()
    cuerpo = {'nombre_completo': 'Nombre Nuevo', 'rol': 'coordinacion', 'activo': False}
    cuerpo.pop(faltante)
    p = api('PUT', f"{USUARIOS}/{r.json['id']}", cuerpo)
    es_problema(p, 422, 'VALIDACION', conforme)
    assert p.json['detalles'] == [{'campo': faltante, 'mensaje': 'Campo obligatorio'}]
    assert api('GET', f"{USUARIOS}/{r.json['id']}").json == r.json  # sin cambios


@pytest.mark.parametrize('cambio', [{'correo': 'otro@ecoalert.pe'}, {'id': str(uuid.uuid4())}, {'rol': 'superadmin'},
                                    {'nombre_completo': None}, {'activo': 'quizas'}],
                         ids=['correo', 'id', 'rol_invalido', 'nombre_nulo', 'activo_no_booleano'])
def test_put_rechaza_campos_no_editables_o_invalidos(api, conforme, crear_usuario, cambio):
    r, _ = crear_usuario()
    cuerpo = {'nombre_completo': 'Nombre Nuevo', 'rol': 'analista_sig', 'activo': True, **cambio}
    es_problema(api('PUT', f"{USUARIOS}/{r.json['id']}", cuerpo), 422, 'VALIDACION', conforme)
    assert api('GET', f"{USUARIOS}/{r.json['id']}").json == r.json


def test_put_404_400_y_json_ilegible(api, conforme, crear_usuario):
    valido = {'nombre_completo': 'Nombre Nuevo', 'rol': 'analista_sig', 'activo': True}
    es_problema(api('PUT', f'{USUARIOS}/{uuid.uuid4()}', valido), 404, 'NO_ENCONTRADO', conforme)
    es_problema(api('PUT', f'{USUARIOS}/no-es-uuid', valido), 400, 'SOLICITUD_MAL_FORMADA', conforme)
    r, _ = crear_usuario()
    es_problema(api('PUT', f"{USUARIOS}/{r.json['id']}", crudo=b'{"rol":'), 400, 'SOLICITUD_MAL_FORMADA', conforme)


# --------------------------------------------------------------------------- PATCH

def test_patch_parcial_conserva_lo_no_enviado(api, bd, conforme, crear_usuario):
    r, _ = crear_usuario()
    p = api('PATCH', f"{USUARIOS}/{r.json['id']}", {'activo': False}, MERGE_PATCH)
    assert p.estado == 200
    conforme('Usuario', p.json)
    assert p.json == {**r.json, 'activo': False}
    assert bd('SELECT activo FROM usuarios WHERE id = %s', (r.json['id'],))[0][0] is False


def test_patch_exige_merge_patch_y_rechaza_vacio_o_nulo(api, conforme, crear_usuario):
    r, _ = crear_usuario()
    destino = f"{USUARIOS}/{r.json['id']}"
    es_problema(api('PATCH', destino, {'activo': False}), 415, 'TIPO_CONTENIDO_NO_SOPORTADO', conforme)
    es_problema(api('PATCH', destino, {}, MERGE_PATCH), 422, 'VALIDACION', conforme)
    es_problema(api('PATCH', destino, {'rol': None}, MERGE_PATCH), 422, 'VALIDACION', conforme)
    es_problema(api('PATCH', f'{USUARIOS}/{uuid.uuid4()}', {'activo': True}, MERGE_PATCH), 404, 'NO_ENCONTRADO', conforme)


# --------------------------------------------------------------------------- regla de la ultima coordinacion y sesiones

@pytest.mark.parametrize('metodo', ['PUT', 'PATCH'])
@pytest.mark.parametrize('accion', ['desactivar', 'quitar_rol'])
def test_protege_la_ultima_cuenta_de_coordinacion(api, bd, conforme, crear_usuario, metodo, accion):
    unica = crear_usuario(rol='coordinacion')[0].json
    dejar_solo(bd, unica['id'])
    r = enviar(api, metodo, unica['id'], cambios_de(metodo, accion))
    es_problema(r, 409, 'ULTIMA_COORDINACION', conforme)
    assert bd('SELECT rol, activo FROM usuarios WHERE id = %s', (unica['id'],))[0] == ('coordinacion', True)
    # Con otra coordinacion activa el mismo cambio si procede.
    crear_usuario(rol='coordinacion')
    assert enviar(api, metodo, unica['id'], cambios_de(metodo, accion)).estado == 200


def test_put_que_no_cambia_rol_ni_actividad_de_la_ultima_coordinacion_es_valido(api, bd, crear_usuario):
    unica = crear_usuario(rol='coordinacion')[0].json
    dejar_solo(bd, unica['id'])
    r = api('PUT', f"{USUARIOS}/{unica['id']}", {'nombre_completo': 'Solo Cambia el Nombre', 'rol': 'coordinacion', 'activo': True})
    assert r.estado == 200 and r.json['nombre_completo'] == 'Solo Cambia el Nombre'


@pytest.mark.parametrize('metodo', ['PUT', 'PATCH'])
def test_desactivar_cierra_las_sesiones_abiertas(api, bd, crear_usuario, metodo):
    usuario = crear_usuario()[0].json
    token = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    bd('INSERT INTO sesiones (usuario_id, token_hash) VALUES (%s, %s)', (usuario['id'], token))
    cambios = {'nombre_completo': 'Cuenta Desactivada', 'rol': 'analista_sig', 'activo': False} if metodo == 'PUT' else {'activo': False}
    assert enviar(api, metodo, usuario['id'], cambios).estado == 200
    assert bd('SELECT revocada_en IS NOT NULL FROM sesiones WHERE token_hash = %s', (token,))[0][0] is True


@pytest.mark.parametrize('metodo', ['PUT', 'PATCH'])
def test_desactivaciones_simultaneas_nunca_dejan_cero_coordinaciones(api, bd, crear_usuario, metodo):
    for _ in range(5):
        a, b = (crear_usuario(rol='coordinacion')[0].json for _ in range(2))
        dejar_solo(bd, a['id'], b['id'])
        with cf.ThreadPoolExecutor(2) as pool:
            estados = sorted(r.estado for r in pool.map(lambda u: enviar(api, metodo, u['id'], cambios_de(metodo, 'desactivar')), (a, b)))
        assert estados == [200, 409]
        assert bd("SELECT count(*) FROM usuarios WHERE rol = 'coordinacion' AND activo")[0][0] == 1


# --------------------------------------------------------------------------- idempotencia

def test_reintento_identico_devuelve_la_misma_respuesta_sin_duplicar(api, bd, crear_usuario):
    clave = str(uuid.uuid4())
    r1, cuerpo = crear_usuario(clave=clave)
    r2 = api('POST', USUARIOS, cuerpo, {'Idempotency-Key': clave})
    assert (r1.estado, r2.estado) == (201, 201)
    assert r2.json == r1.json and r2.cabeceras['Location'] == r1.cabeceras['Location']
    assert bd('SELECT count(*) FROM usuarios WHERE correo = %s', (cuerpo['correo'],))[0][0] == 1
    assert bd('SELECT count(*) FROM claves_idempotencia WHERE clave = %s', (clave,))[0][0] == 1


def test_el_mismo_cuerpo_con_otro_formato_json_es_el_mismo_reintento(api, crear_usuario):
    clave = str(uuid.uuid4())
    r1, cuerpo = crear_usuario(clave=clave)
    reordenado = json.dumps(dict(reversed(list(cuerpo.items()))), indent=4, ensure_ascii=False).encode()
    r2 = api('POST', USUARIOS, crudo=reordenado, cabeceras={'Idempotency-Key': clave})
    assert r2.estado == 201 and r2.json == r1.json


@pytest.mark.parametrize('campo', ['nombre_completo', 'rol', 'password_temporal', 'correo'])
def test_misma_clave_con_cuerpo_distinto_es_conflicto_422(api, bd, conforme, crear_usuario, campo):
    clave = str(uuid.uuid4())
    _, cuerpo = crear_usuario(clave=clave)
    distinto = {**cuerpo, campo: {'nombre_completo': 'Otro Nombre', 'rol': 'coordinacion',
                                  'password_temporal': 'Otra-Clave-2026', 'correo': f'otro.{uuid.uuid4().hex[:10]}@ecoalert.pe'}[campo]}
    r = api('POST', USUARIOS, distinto, {'Idempotency-Key': clave})
    es_problema(r, 422, 'IDEMPOTENCIA_CONFLICTO', conforme)  # incluye cambiar solo la contrasena
    assert bd('SELECT count(*) FROM usuarios WHERE correo = %s', (distinto['correo'],))[0][0] == (1 if campo != 'correo' else 0)


def test_la_huella_es_hmac_del_cuerpo_completo_y_no_expone_la_contrasena(bd, crear_usuario):
    clave = str(uuid.uuid4())
    r, cuerpo = crear_usuario(clave=clave)
    huella, respuesta = bd('SELECT huella, cuerpo_respuesta::text FROM claves_idempotencia WHERE clave = %s', (clave,))[0]
    canonico = json.dumps(cuerpo, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    assert re.fullmatch(r'[0-9a-f]{64}', huella)
    assert huella != hashlib.sha256(canonico).hexdigest(), 'La huella debe depender de un secreto (HMAC), no ser un SHA-256 simple'
    assert cuerpo['password_temporal'] not in huella + respuesta
    if not os.environ.get('API_BASE_URL'):  # con API propia el secreto es conocido por la prueba
        assert huella == hmac.new(os.environ['IDEMPOTENCY_SECRET'].encode(), canonico, hashlib.sha256).hexdigest()


def test_los_errores_no_se_guardan_y_la_clave_sigue_disponible(api, bd, crear_usuario):
    clave = str(uuid.uuid4())
    invalido, cuerpo = crear_usuario(clave=clave, rol='superadmin')
    assert invalido.estado == 422
    assert bd('SELECT count(*) FROM claves_idempotencia WHERE clave = %s', (clave,))[0][0] == 0
    valido = api('POST', USUARIOS, {**cuerpo, 'rol': 'analista_sig'}, {'Idempotency-Key': clave})
    assert valido.estado == 201
    duplicado = api('POST', USUARIOS, {**cuerpo, 'rol': 'analista_sig'}, {'Idempotency-Key': str(uuid.uuid4())})
    assert duplicado.estado == 409


def test_clave_con_mas_de_24_horas_ya_no_se_reutiliza(api, bd, crear_usuario):
    clave = str(uuid.uuid4())
    bd("INSERT INTO claves_idempotencia (clave, operacion, huella, estado_http, cuerpo_respuesta, location, creada_en) "
       "VALUES (%s, 'crearUsuario', %s, 201, '{}', '/api/v1/usuarios/x', now() - interval '25 hours')", (clave, 'f' * 64))
    r, cuerpo = crear_usuario(clave=clave)
    assert r.estado == 201 and r.json['correo'] == cuerpo['correo']
    assert bd('SELECT huella <> %s FROM claves_idempotencia WHERE clave = %s', ('f' * 64, clave))[0][0] is True


def test_concurrencia_misma_clave_crea_un_solo_usuario(api, bd):
    clave = str(uuid.uuid4())
    cuerpo = cuerpo_nuevo(f'conc.{uuid.uuid4().hex[:10]}@ecoalert.pe')
    with cf.ThreadPoolExecutor(10) as pool:
        respuestas = list(pool.map(lambda _: api('POST', USUARIOS, cuerpo, {'Idempotency-Key': clave}), range(10)))
    assert {r.estado for r in respuestas} == {201}
    assert len({r.json['id'] for r in respuestas}) == 1
    assert bd('SELECT count(*) FROM usuarios WHERE correo = %s', (cuerpo['correo'],))[0][0] == 1
    assert bd('SELECT count(*) FROM claves_idempotencia WHERE clave = %s', (clave,))[0][0] == 1


def test_concurrencia_mismo_correo_con_claves_distintas_un_201_y_nueve_409(api, bd):
    cuerpo = cuerpo_nuevo(f'carrera.{uuid.uuid4().hex[:10]}@ecoalert.pe')
    with cf.ThreadPoolExecutor(10) as pool:
        respuestas = list(pool.map(lambda _: api('POST', USUARIOS, cuerpo, {'Idempotency-Key': str(uuid.uuid4())}), range(10)))
    assert sorted(r.estado for r in respuestas) == [201] + [409] * 9
    assert bd('SELECT count(*) FROM usuarios WHERE correo = %s', (cuerpo['correo'],))[0][0] == 1
