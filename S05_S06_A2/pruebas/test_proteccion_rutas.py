"""Protección de rutas: denegación por defecto, matriz de roles del contrato y gestión de cuentas."""
import re
from pathlib import Path

import pytest
import yaml

from app.main import PREFIJO_API, app
from conftest import MERGE_PATCH, bearer

CONTRATO = Path(__file__).resolve().parents[2] / 'S05_S06_integracion' / 'openapi_integrado.yaml'
RUTAS_PUBLICAS = {('POST', '/api/v1/auth/login')}
VALORES_PARAMETROS = {'codigo': 'EA-2026-001'}
UUID_EJEMPLO = '00000000-0000-4000-8000-000000000000'
# logout revocaría la sesión del token compartido por el resto de la prueba.
SIN_PRUEBA_DE_ROL = {('POST', '/api/v1/auth/logout')}


def _rutas_api():
    """(método, ruta) de cada operación montada, leídas del esquema OpenAPI que genera la app."""
    return sorted((metodo.upper(), path) for path, operaciones in app.openapi()['paths'].items()
                  if path.startswith(PREFIJO_API) for metodo in operaciones)


def _url(path):
    return re.sub(r'\{(\w+)\}', lambda m: VALORES_PARAMETROS.get(m.group(1), UUID_EJEMPLO), path)


RUTAS_PROTEGIDAS = [ruta for ruta in _rutas_api() if ruta not in RUTAS_PUBLICAS]


def test_inventario_de_rutas_no_esta_vacio():
    # Evita que las pruebas parametrizadas pasen sin verificar nada: 15 rutas CRUD de A1 + 4 protegidas de auth.
    assert len(RUTAS_PROTEGIDAS) >= 19


@pytest.mark.parametrize('metodo,path', RUTAS_PROTEGIDAS)
def test_RNF_01_toda_ruta_protegida_sin_token_responde_401(client, metodo, path):
    r = client.request(metodo, _url(path), json={})
    assert r.status_code == 401, f'{metodo} {path} quedó accesible sin token'
    assert r.json()['codigo'] == 'NO_AUTENTICADO'
    assert r.headers['www-authenticate'] == 'Bearer realm="ecoalert"'


@pytest.mark.parametrize('metodo,path', RUTAS_PROTEGIDAS)
def test_RNF_01_toda_ruta_protegida_con_token_invalido_responde_401(client, metodo, path):
    r = client.request(metodo, _url(path), json={}, headers=bearer('no.es.un-jwt'))
    assert r.status_code == 401


def test_RNF_02_cada_ruta_aplica_los_x_roles_del_contrato(client, token_analista, token_coordinacion):
    """Prueba de caja negra: cada rol recibe 403 exactamente en las rutas que el contrato no le permite."""
    contrato = yaml.safe_load(CONTRATO.read_text(encoding='utf-8'))['paths']
    tokens = {'analista_sig': token_analista, 'coordinacion': token_coordinacion}
    diferencias = []
    for metodo, path in _rutas_api():
        permitidos = set(contrato[path.removeprefix(PREFIJO_API)][metodo.lower()]['x-roles'])
        if permitidos == {'publico'}:
            assert (metodo, path) in RUTAS_PUBLICAS, f'{metodo} {path} es pública en el contrato'
            continue
        if (metodo, path) in SIN_PRUEBA_DE_ROL:
            continue
        for rol, token in tokens.items():
            r = client.request(metodo, _url(path), json={}, headers=bearer(token))
            rechazado = r.status_code == 403 and r.json()['codigo'] == 'ROL_NO_PERMITIDO'
            if rechazado == (rol in permitidos) or r.status_code == 401:
                diferencias.append(f'{metodo} {path} con {rol}: {r.status_code} (contrato: {sorted(permitidos)})')
    assert not diferencias, '\n'.join(diferencias)


def test_RF_02_AC_9_analista_en_gestion_de_usuarios_responde_403(client, token_analista):
    r = client.get('/api/v1/usuarios', headers=bearer(token_analista))
    assert r.status_code == 403
    assert r.json()['codigo'] == 'ROL_NO_PERMITIDO'


def test_ruta_crud_con_token_y_rol_correctos_responde_200(client, token_coordinacion, token_analista):
    assert client.get('/api/v1/usuarios', headers=bearer(token_coordinacion)).status_code == 200
    assert client.get('/api/v1/alertas', headers=bearer(token_analista)).status_code == 200
    assert client.get('/api/v1/alertas', headers=bearer(token_coordinacion)).status_code == 200


def test_respuestas_de_api_incluyen_cabeceras_de_seguridad(client, token_analista):
    r = client.get('/api/v1/alertas', headers=bearer(token_analista))
    assert r.headers['cache-control'] == 'no-store'
    assert r.headers['x-content-type-options'] == 'nosniff'
    assert r.headers['x-frame-options'] == 'DENY'


def test_salud_es_publica_y_no_expone_datos(client):
    r = client.get('/salud')
    assert r.status_code == 200
    assert r.json() == {'estado': 'ok', 'base_datos': True}


def test_RF_02_AC_7_borrar_cuenta_no_existe(client, token_coordinacion, crear_cuenta, conn):
    crear_cuenta()
    usuario_id = conn.execute("SELECT id FROM usuarios WHERE rol='analista_sig'").fetchone()[0]
    r = client.delete(f'/api/v1/usuarios/{usuario_id}', headers=bearer(token_coordinacion))
    assert r.status_code == 405
    assert conn.execute('SELECT count(*) FROM usuarios WHERE id=%s', (usuario_id,)).fetchone()[0] == 1


# --- Efecto inmediato de cambios de cuenta sobre tokens ya emitidos ------------------------

def _id(conn, correo):
    return conn.execute('SELECT id FROM usuarios WHERE correo=%s', (correo,)).fetchone()[0]


def test_desactivar_cuenta_invalida_sus_tokens_al_instante(client, token_coordinacion, crear_cuenta, login, conn):
    correo = crear_cuenta()
    token = login(correo)
    r = client.patch(f'/api/v1/usuarios/{_id(conn, correo)}', json={'activo': False},
                     headers={**bearer(token_coordinacion), **MERGE_PATCH})
    assert r.status_code == 200
    assert client.get('/api/v1/alertas', headers=bearer(token)).status_code == 401


def test_desactivar_cuenta_con_put_invalida_sus_tokens_al_instante(client, token_coordinacion, crear_cuenta, login, conn):
    correo = crear_cuenta()
    token = login(correo)
    r = client.put(f'/api/v1/usuarios/{_id(conn, correo)}', headers=bearer(token_coordinacion),
                   json={'nombre_completo': 'Cuenta Desactivada', 'rol': 'analista_sig', 'activo': False})
    assert r.status_code == 200
    assert client.get('/api/v1/alertas', headers=bearer(token)).status_code == 401


def test_cambio_de_rol_se_aplica_aunque_el_token_diga_otro_rol(client, token_coordinacion, crear_cuenta, login, conn):
    correo = crear_cuenta('coordinacion')
    token = login(correo)
    client.patch(f'/api/v1/usuarios/{_id(conn, correo)}', json={'rol': 'analista_sig'},
                 headers={**bearer(token_coordinacion), **MERGE_PATCH})
    assert client.get('/api/v1/usuarios', headers=bearer(token)).status_code == 403


def test_RF_02_AC_8_no_se_desactiva_la_ultima_coordinacion(client, crear_cuenta, login, conn):
    correo = crear_cuenta('coordinacion')
    token = login(correo)
    r = client.patch(f'/api/v1/usuarios/{_id(conn, correo)}', json={'activo': False},
                     headers={**bearer(token), **MERGE_PATCH})
    assert r.status_code == 409
    assert r.json()['codigo'] == 'ULTIMA_COORDINACION'


def test_RF_02_AC_8_put_no_desactiva_la_ultima_coordinacion(client, crear_cuenta, login, conn):
    correo = crear_cuenta('coordinacion')
    token = login(correo)
    r = client.put(f'/api/v1/usuarios/{_id(conn, correo)}', headers=bearer(token),
                   json={'nombre_completo': 'Coordinación', 'rol': 'coordinacion', 'activo': False})
    assert r.status_code == 409
    assert r.json()['codigo'] == 'ULTIMA_COORDINACION'
