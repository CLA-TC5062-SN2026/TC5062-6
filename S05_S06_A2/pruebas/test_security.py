"""Validación del JWT aislada de la tabla de sesiones.

En las pruebas de extremo a extremo un token falsificado también falla porque su huella no está
registrada en `sesiones`; aquí se verifica que la capa JWT lo rechaza por sí sola.
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from app.config import get_settings
from app.security import decodificar_token, emitir_token, hashear, huella_token, verificar
from conftest import bearer


@pytest.fixture
def cfg():
    return get_settings()


def _claims_validos(cfg, **cambios):
    ahora = datetime.now(timezone.utc)
    claims = {'sub': str(uuid4()), 'rol': 'analista_sig', 'jti': str(uuid4()), 'iat': ahora, 'nbf': ahora,
              'exp': ahora + timedelta(hours=1), 'iss': cfg.jwt_issuer, 'aud': cfg.jwt_audience}
    claims.update(cambios)
    return {k: v for k, v in claims.items() if v is not None}


def _firmar(cfg, claims, algoritmo='HS256', secreto=None):
    return jwt.encode(claims, secreto or cfg.jwt_secret.get_secret_value(), algorithm=algoritmo)


def test_token_emitido_se_valida_y_conserva_sus_claims(cfg):
    token, jti = emitir_token(uuid4(), 'coordinacion', cfg)
    claims = decodificar_token(token, cfg)
    assert claims['jti'] == str(jti) and claims['rol'] == 'coordinacion'
    assert claims['exp'] - claims['iat'] == cfg.jwt_expiration


@pytest.mark.parametrize('claim', ['exp', 'iat', 'nbf', 'iss', 'aud', 'sub', 'jti'])
def test_token_sin_claim_obligatorio_se_rechaza(cfg, claim):
    with pytest.raises(jwt.MissingRequiredClaimError):
        decodificar_token(_firmar(cfg, _claims_validos(cfg, **{claim: None})), cfg)


def test_token_expirado_se_rechaza(cfg):
    pasado = datetime.now(timezone.utc) - timedelta(hours=2)
    with pytest.raises(jwt.ExpiredSignatureError):
        decodificar_token(_firmar(cfg, _claims_validos(cfg, iat=pasado, nbf=pasado, exp=pasado + timedelta(hours=1))), cfg)


def test_token_aun_no_valido_se_rechaza(cfg):
    futuro = datetime.now(timezone.utc) + timedelta(hours=1)
    with pytest.raises(jwt.ImmatureSignatureError):
        decodificar_token(_firmar(cfg, _claims_validos(cfg, nbf=futuro)), cfg)


@pytest.mark.parametrize('cambio,error', [
    ({'iss': 'otro-emisor'}, jwt.InvalidIssuerError),
    ({'aud': 'otra-audiencia'}, jwt.InvalidAudienceError),
])
def test_token_de_otro_emisor_o_audiencia_se_rechaza(cfg, cambio, error):
    with pytest.raises(error):
        decodificar_token(_firmar(cfg, _claims_validos(cfg, **cambio)), cfg)


def test_token_firmado_con_otro_secreto_se_rechaza(cfg):
    with pytest.raises(jwt.InvalidSignatureError):
        decodificar_token(_firmar(cfg, _claims_validos(cfg), secreto='otro-secreto-de-al-menos-32-bytes-xx'), cfg)


@pytest.mark.parametrize('algoritmo', ['none', 'HS512'])
def test_token_con_algoritmo_distinto_de_hs256_se_rechaza(cfg, algoritmo):
    claims = _claims_validos(cfg)
    token = jwt.encode(claims, None, algorithm='none') if algoritmo == 'none' else _firmar(cfg, claims, algoritmo, 'k' * 64)
    with pytest.raises(jwt.InvalidAlgorithmError):
        decodificar_token(token, cfg)


def test_token_expirado_con_sesion_registrada_responde_401(client, crear_cuenta, conn, cfg):
    # La sesión existe y está activa: el único motivo de rechazo es `exp`.
    crear_cuenta()
    usuario_id = conn.execute('SELECT id FROM usuarios').fetchone()[0]
    pasado = datetime.now(timezone.utc) - timedelta(hours=2)
    claims = _claims_validos(cfg, sub=str(usuario_id), iat=pasado, nbf=pasado, exp=pasado + timedelta(hours=1))
    token = _firmar(cfg, claims)
    conn.execute('INSERT INTO sesiones (id, usuario_id, token_hash) VALUES (%s,%s,%s)',
                 (claims['jti'], usuario_id, huella_token(token)))
    assert client.get('/api/v1/auth/me', headers=bearer(token)).status_code == 401


# --- Hash de contraseñas (Argon2id para las nuevas, bcrypt heredado verificable) ----------------

CLAVE = 'clave-de-prueba-2026'


def _bcrypt(password):
    from pwdlib import PasswordHash
    from pwdlib.hashers.bcrypt import BcryptHasher
    return PasswordHash((BcryptHasher(rounds=4),)).hash(password)


def test_hashear_usa_argon2id_y_se_verifica_sin_migrar():
    guardado = hashear(CLAVE)
    assert guardado.startswith('$argon2id$')
    assert verificar(CLAVE, guardado) == (True, None)
    assert verificar('otra-clave-equivocada', guardado) == (False, None)


def test_hash_bcrypt_heredado_se_verifica_y_pide_migrar_a_argon2():
    valida, nuevo = verificar(CLAVE, _bcrypt(CLAVE))
    assert valida and nuevo.startswith('$argon2id$')
    assert verificar(CLAVE, nuevo) == (True, None)


def test_hash_bcrypt_con_password_de_mas_de_72_bytes_es_invalido_sin_excepcion():
    assert verificar('x' * 100, _bcrypt(CLAVE)) == (False, None)


def test_hash_argon2_admite_passwords_largas():
    larga = 'x' * 128
    assert verificar(larga, hashear(larga)) == (True, None)


@pytest.mark.parametrize('guardado', [None, '', 'texto-que-no-es-un-hash', '$argon2id$basura', '$2b$12$corto'])
def test_hash_ausente_o_ilegible_nunca_es_valido_ni_lanza_excepcion(guardado):
    assert verificar(CLAVE, guardado) == (False, None)
