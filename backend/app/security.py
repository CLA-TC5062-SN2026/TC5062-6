"""Hash de contraseñas y emisión/validación de JWT.

- Contraseñas: bcrypt (costo 12) para hashes nuevos; los hashes Argon2id existentes se siguen
  verificando y se migran a bcrypt en el siguiente inicio de sesión exitoso.
- JWT: HS256 con algoritmo fijo en la validación (RFC 8725 §3.1) y claims obligatorios.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config import Settings

# bcrypt solo procesa 72 bytes; la librería lanza ValueError si se excede.
MAX_BYTES_PASSWORD = 72
ALGORITMO_JWT = 'HS256'
CLAIMS_OBLIGATORIOS = ['exp', 'iat', 'nbf', 'iss', 'aud', 'sub', 'jti']

hasher = PasswordHash((BcryptHasher(rounds=12), Argon2Hasher()))
# Se verifica contra este hash cuando el correo no existe, para que el tiempo de respuesta
# no revele qué cuentas existen (enumeración de usuarios, RF-01-AC-3).
_HASH_SENUELO = hasher.hash(secrets.token_urlsafe(32))


def hashear(password: str) -> str:
    return hasher.hash(password)


def verificar(password: str, hash_guardado: str | None) -> tuple[bool, str | None]:
    """Devuelve (válida, hash_nuevo). `hash_nuevo` no es None si conviene re-hashear con bcrypt.

    Todas las ramas ejecutan una verificación completa, para que el tiempo de respuesta sea el mismo.
    """
    excede = len(password.encode()) > MAX_BYTES_PASSWORD
    if hash_guardado is None or (excede and not hash_guardado.startswith('$argon2')):
        hasher.verify(password.encode()[:MAX_BYTES_PASSWORD], _HASH_SENUELO)
        return False, None
    if excede:
        # Solo un hash Argon2 heredado puede corresponder a una contraseña tan larga,
        # y no se puede migrar a bcrypt sin truncarla.
        return hasher.verify(password, hash_guardado), None
    return hasher.verify_and_update(password, hash_guardado)


def emitir_token(usuario_id: UUID, rol: str, cfg: Settings) -> tuple[str, UUID]:
    jti = uuid4()
    ahora = datetime.now(timezone.utc)
    claims = {
        'sub': str(usuario_id), 'rol': rol, 'jti': str(jti),
        'iat': ahora, 'nbf': ahora, 'exp': ahora + timedelta(seconds=cfg.jwt_expiration),
        'iss': cfg.jwt_issuer, 'aud': cfg.jwt_audience,
    }
    return jwt.encode(claims, cfg.jwt_secret.get_secret_value(), algorithm=ALGORITMO_JWT), jti


def decodificar_token(token: str, cfg: Settings) -> dict:
    """Valida firma, expiración, emisor y audiencia. Lanza jwt.InvalidTokenError si algo falla."""
    return jwt.decode(
        token, cfg.jwt_secret.get_secret_value(), algorithms=[ALGORITMO_JWT],
        issuer=cfg.jwt_issuer, audience=cfg.jwt_audience,
        options={'require': CLAIMS_OBLIGATORIOS},
    )


def huella_token(token: str) -> str:
    """SHA-256 del token: la base de datos nunca guarda el token en claro."""
    return hashlib.sha256(token.encode()).hexdigest()
