"""Configuración leída de variables de entorno (12-Factor App, factor III).

Ningún secreto tiene valor por defecto: si falta, la aplicación no arranca (fail-fast).
"""
from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# RFC 7518 §3.2: la clave de HS256 debe tener al menos el tamaño del hash (256 bits).
MIN_BYTES_SECRETO = 32
MARCADOR_PLANTILLA = 'CAMBIAR'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    database_url: SecretStr
    jwt_secret: SecretStr
    # Vida máxima del token en segundos. Obligatoria y acotada: no existen tokens sin expiración.
    jwt_expiration: int = Field(gt=0, le=86_400)
    jwt_issuer: str = 'ecoalert-api'
    jwt_audience: str = 'ecoalert-spa'
    # PS-12 del SRS: la sesión expira tras 30 min sin actividad.
    sesion_inactividad_segundos: int = Field(default=1800, gt=0)
    api_docs: bool = False

    @field_validator('jwt_secret')
    @classmethod
    def secreto_robusto(cls, valor: SecretStr) -> SecretStr:
        secreto = valor.get_secret_value()
        if secreto.startswith(MARCADOR_PLANTILLA):
            raise ValueError('JWT_SECRET conserva el valor de plantilla de .env.example')
        if len(secreto.encode()) < MIN_BYTES_SECRETO:
            raise ValueError(f'JWT_SECRET debe tener al menos {MIN_BYTES_SECRETO} bytes')
        return valor


@lru_cache
def get_settings() -> Settings:
    return Settings()
