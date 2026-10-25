"""Modelos de solicitud alineados con los schemas de `openapi_equipo.yaml`."""
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.security import MAX_BYTES_PASSWORD

Rol = Literal['analista_sig', 'coordinacion']
# PS-15 / RNF-03: mínimo 12 caracteres. Máximo 1024 para acotar el costo de hashear entradas enormes.
MIN_PASSWORD = 12
MAX_PASSWORD_ENTRADA = 1024


def _cabe_en_bcrypt(valor: str) -> str:
    if len(valor.encode()) > MAX_BYTES_PASSWORD:
        raise ValueError(f'La contraseña no puede superar {MAX_BYTES_PASSWORD} bytes')
    return valor


PasswordNueva = Annotated[str, Field(min_length=MIN_PASSWORD), AfterValidator(_cabe_en_bcrypt)]
PasswordIngresada = Annotated[str, Field(min_length=1, max_length=MAX_PASSWORD_ENTRADA)]


class CredencialesLogin(BaseModel):
    model_config = ConfigDict(extra='forbid')
    correo: EmailStr
    password: PasswordIngresada


class CambioPassword(BaseModel):
    model_config = ConfigDict(extra='forbid')
    password_actual: PasswordIngresada
    password_nueva: PasswordNueva


class UsuarioCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_completo: str = Field(min_length=1, max_length=120)
    correo: EmailStr
    rol: Rol
    password_temporal: PasswordNueva


class UsuarioActualizar(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_completo: str | None = Field(default=None, min_length=1, max_length=120)
    rol: Rol | None = None
    activo: bool | None = None


class CambioEstadoSolicitud(BaseModel):
    model_config = ConfigDict(extra='forbid')
    estado_nuevo: Literal['nueva','en_revision','requiere_verificacion','revisada','descartada']
    texto: str | None = None


class MarcaAnalistaSolicitud(BaseModel):
    model_config = ConfigDict(extra='forbid')
    texto: str = Field(min_length=1)


class RetiroMarcaSolicitud(BaseModel):
    model_config = ConfigDict(extra='forbid')
    activa: Literal[False]
    motivo_retiro: str = Field(min_length=1)


class AjusteSolicitud(BaseModel):
    model_config = ConfigDict(extra='forbid')
    forma: Literal['por_puntaje','por_nivel']
    puntaje: int | None = Field(default=None, ge=0, le=100)
    nivel: Literal['alta','media','baja'] | None = None
    justificacion: str = Field(min_length=1)
    @model_validator(mode='after')
    def validar(self):
        if self.forma == 'por_puntaje' and (self.puntaje is None or self.nivel is not None):
            raise ValueError('por_puntaje requiere puntaje y no nivel')
        if self.forma == 'por_nivel' and (self.nivel is None or self.puntaje is not None):
            raise ValueError('por_nivel requiere nivel y no puntaje')
        return self


class RetiroAjusteSolicitud(BaseModel):
    model_config = ConfigDict(extra='forbid')
    estado: Literal['retirado']
    justificacion_retiro: str = Field(min_length=1)
