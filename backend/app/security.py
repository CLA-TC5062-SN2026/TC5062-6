"""Hash de contraseñas y emisión/validación de JWT.

- Contraseñas: Argon2id para los hashes nuevos (el mismo de las cuentas creadas por A1). Los hashes bcrypt
  heredados se siguen verificando y se migran a Argon2id en el siguiente inicio de sesión exitoso.
- JWT: HS256 con algoritmo fijo en la validación (RFC 8725 §3.1) y claims obligatorios.
"""
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config import Settings

logger = logging.getLogger(__name__)

# bcrypt solo procesa 72 bytes; la librería lanza ValueError si se excede.
MAX_BYTES_BCRYPT = 72
ALGORITMO_JWT = 'HS256'
CLAIMS_OBLIGATORIOS = ['exp', 'iat', 'nbf', 'iss', 'aud', 'sub', 'jti']

hasher = PasswordHash((Argon2Hasher(), BcryptHasher(rounds=12)))
# Se verifica contra este hash cuando la cuenta no existe o su hash es ilegible, para que el tiempo
# de respuesta no revele qué cuentas existen (enumeración de usuarios, RF-01-AC-3).
_HASH_SENUELO = hasher.hash(secrets.token_urlsafe(32))


def hashear(password: str) -> str:
    return hasher.hash(password)


def verificar(password: str, hash_guardado: str | None) -> tuple[bool, str | None]:
    """Devuelve (válida, hash_nuevo). `hash_nuevo` no es None si el hash debe migrarse a Argon2id.

    Un hash ausente, ilegible o incompatible con la longitud de la contraseña (bcrypt no admite más de
    72 bytes) nunca es válido ni lanza una excepción: se ejecuta igualmente una verificación completa.
    """
    if hash_guardado is not None and (len(password.encode()) <= MAX_BYTES_BCRYPT or hash_guardado.startswith('$argon2')):
        try:
            return hasher.verify_and_update(password, hash_guardado)
        except (UnknownHashError, ValueError):
            logger.warning('Una cuenta tiene un hash de contraseña ilegible; no puede iniciar sesión')
    hasher.verify(password, _HASH_SENUELO)
    return False, None


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
