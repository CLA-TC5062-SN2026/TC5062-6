"""Esquemas de solicitud y respuesta alineados con components/schemas de openapi_equipo.yaml."""
from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, model_validator

CODIGO_ZONA = r'^EA-[0-9]{4}-[0-9]{3}$'
Rol = Literal['analista_sig', 'coordinacion']
NombreCompleto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class UsuarioCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_completo: NombreCompleto
    correo: EmailStr
    rol: Rol
    password_temporal: str = Field(min_length=12)


class UsuarioActualizar(BaseModel):
    """JSON Merge Patch: al menos un campo y ninguno nulo (ninguno es opcional en la cuenta)."""
    model_config = ConfigDict(extra='forbid')
    nombre_completo: NombreCompleto | None = None
    rol: Rol | None = None
    activo: bool | None = None

    @model_validator(mode='after')
    def validar(self):
        if not self.model_fields_set:
            raise ValueError('Debe indicar al menos un campo')
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError('Los campos indicados no admiten valor nulo')
        return self


class UsuarioReemplazar(BaseModel):
    """PUT: reemplazo completo de los campos editables; el correo no cambia."""
    model_config = ConfigDict(extra='forbid')
    nombre_completo: NombreCompleto
    rol: Rol
    activo: bool


class UsuarioRef(BaseModel):
    id: UUID
    nombre_completo: str


class Usuario(UsuarioRef):
    correo: str
    rol: Rol
    activo: bool
    debe_cambiar_password: bool
    creado_en: datetime


class Alerta(BaseModel):
    id: UUID
    fuente: str
    codigo: str
    fecha_deteccion: date
    fecha_ingesta: datetime
    presente_en_ultima_carga: bool
    zona_codigo: str
    area_ha: float


class PaginaAlertas(BaseModel):
    total: int
    limite: int
    desplazamiento: int
    alertas: list[Alerta]


class CargaAlertas(BaseModel):
    id: UUID
    fuente: str
    fecha_corte: date
    cargada_en: datetime
    cargada_por: UsuarioRef
    alertas_en_archivo: int
    alertas_nuevas: int
    alertas_existentes: int
    alertas_fuera_ambito: int
    alertas_ausentes: int
    zonas_creadas: int
    zonas_actualizadas: int
    resumen: str


class Marca(BaseModel):
    id: UUID
    tipo: str
    origen: str
    rotulo: str | None = None
    texto: str
    activa: bool
    creada_en: datetime
    creada_por: UsuarioRef | None = None
    retirada_en: datetime | None = None
    retirada_por: UsuarioRef | None = None
    motivo_retiro: str | None = None


class AjustePrioridad(BaseModel):
    id: UUID
    forma: str
    nivel_elegido: str | None
    puntaje_ajustado: int
    puntaje_calculado_al_ajustar: int | None
    justificacion: str
    estado: str
    creado_en: datetime
    creado_por: UsuarioRef
    retirado_en: datetime | None = None
    retirado_por: UsuarioRef | None = None
    justificacion_retiro: str | None = None


class AutorHistorial(BaseModel):
    tipo: Literal['usuario', 'sistema']
    id: UUID | None = None
    nombre: str


class EntradaHistorial(BaseModel):
    id: UUID
    tipo_accion: str
    fecha_hora: datetime
    autor: AutorHistorial
    codigo_alerta_origen: str | None = None
    estado_anterior: str | None = None
    estado_nuevo: str | None = None
    ajuste_id: UUID | None = None
    forma: str | None = None
    nivel_elegido: str | None = None
    puntaje_calculado: int | None = None
    puntaje_ajustado: int | None = None
    marca_id: UUID | None = None
    texto_marca: str | None = None
    texto: str | None = None


class Trabajo(BaseModel):
    id: UUID
    tipo: str
    estado: str
    creado_en: datetime
    actualizado_en: datetime
    mensaje_estado: str | None = None
    resultado: dict | None = None
    error: dict | None = None
