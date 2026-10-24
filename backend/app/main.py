"""EcoAlert: servicios CRUD iniciales, alineados con rutas OpenAPI del equipo.
No reemplaza autenticación, ingesta geoespacial ni comparación de periodos.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID
import os

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from psycopg.errors import UniqueViolation, CheckViolation, ForeignKeyViolation
from fastapi import FastAPI, Depends, HTTPException, Query, Response, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from pwdlib import PasswordHash

DB_URL = os.getenv('DATABASE_URL', 'postgresql://ecoalert:ecoalert_dev@localhost:5432/ecoalert')
pool = ConnectionPool(DB_URL, min_size=1, max_size=5, open=False, kwargs={'row_factory': dict_row})
password_hash = PasswordHash.recommended()

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=True)
    try:
        yield
    finally:
        pool.close()

app = FastAPI(title='EcoAlert Tambopata - CRUD inicial', version='0.1.0', lifespan=lifespan,
              description='Implementación parcial del contrato OpenAPI; ver README para límites.')

class UsuarioCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_completo: str = Field(min_length=1)
    correo: EmailStr
    rol: Literal['analista_sig','coordinacion']
    password_temporal: str = Field(min_length=8)

class UsuarioActualizar(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_completo: str | None = Field(default=None, min_length=1)
    rol: Literal['analista_sig','coordinacion'] | None = None
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

# Contrato OpenAPI: Error {codigo,mensaje}; validaciones FastAPI 422 son adaptadas.
@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    detail = exc.detail
    return JSONResponse(status_code=exc.status_code, content={
        'codigo': f'HTTP_{exc.status_code}', 'mensaje': detail if isinstance(detail,str) else str(detail)
    })

from fastapi.exceptions import RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={'codigo':'DATOS_INVALIDOS','mensaje':'Datos de solicitud inválidos',
                                                   'detalles': [{'campo':'.'.join(map(str,e['loc'])), 'mensaje':e['msg']} for e in exc.errors()]})

def fail(status, message):
    raise HTTPException(status_code=status, detail=message)

def sql_error(exc):
    if isinstance(exc, UniqueViolation): fail(409,'Recurso duplicado')
    if isinstance(exc, (CheckViolation, ForeignKeyViolation)): fail(400,'Los datos violan una restricción de integridad')
    raise exc

def run(sql, params=None, *, one=False):
    with pool.connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                result = cur.fetchone() if one else cur.fetchall() if cur.description else None
            return result
        except (UniqueViolation,CheckViolation,ForeignKeyViolation) as exc:
            sql_error(exc)

def json_safe(value):
    if isinstance(value, dict): return {k:json_safe(v) for k,v in value.items()}
    if isinstance(value,list): return [json_safe(v) for v in value]
    if isinstance(value,(UUID,Decimal,datetime)): return str(value)
    return value

USER_FIELDS='id,nombre_completo,correo,rol,activo,debe_cambiar_password,creado_en'

@app.get('/salud')
def salud():
    return {'estado':'ok','base_datos':bool(run('SELECT 1 AS ok',one=True))}

@app.get('/usuarios')
def listar_usuarios(activo: bool | None=None):
    rows=run(f'SELECT {USER_FIELDS} FROM usuarios WHERE (%s::boolean IS NULL OR activo=%s) ORDER BY nombre_completo', (activo,activo))
    return json_safe(rows)

@app.post('/usuarios',status_code=201)
def crear_usuario(body: UsuarioCrear):
    return json_safe(run(f'''INSERT INTO usuarios (nombre_completo,correo,rol,password_hash)
        VALUES (%s,%s,%s,%s) RETURNING {USER_FIELDS}''',
        (body.nombre_completo, str(body.correo),body.rol,password_hash.hash(body.password_temporal)),one=True))

@app.get('/usuarios/{usuarioId}')
def obtener_usuario(usuarioId: UUID):
    row=run(f'SELECT {USER_FIELDS} FROM usuarios WHERE id=%s',(usuarioId,),one=True)
    if not row: fail(404,'Usuario no encontrado')
    return json_safe(row)

@app.patch('/usuarios/{usuarioId}')
def actualizar_usuario(usuarioId: UUID, body: UsuarioActualizar):
    data=body.model_dump(exclude_unset=True)
    if not data or any(v is None for v in data.values()): fail(400,'Debe indicar al menos un campo válido')
    # Lista blanca de campos, nunca interpolar nombres provenientes directamente del usuario.
    fields=[k for k in ('nombre_completo','rol','activo') if k in data]
    updates=', '.join(f'{k}=%s' for k in fields)
    row=run(f'UPDATE usuarios SET {updates} WHERE id=%s RETURNING {USER_FIELDS}',
            tuple(data[k] for k in fields)+(usuarioId,),one=True)
    if not row: fail(404,'Usuario no encontrado')
    return json_safe(row)

@app.get('/alertas')
def listar_alertas():
    return json_safe(run('''SELECT id,fuente,codigo,fecha_deteccion,fecha_ingesta,
        presente_en_ultima_carga,zona_codigo,area_ha FROM alertas ORDER BY fecha_deteccion DESC'''))

@app.get('/cargas-alertas')
def listar_cargas():
    return json_safe(run('''SELECT id,fuente,fecha_corte,cargada_en,cargada_por,alertas_en_archivo,
        alertas_nuevas,alertas_existentes,alertas_fuera_ambito,alertas_ausentes,
        zonas_creadas,zonas_actualizadas,resumen FROM cargas_alertas ORDER BY cargada_en DESC'''))

@app.get('/cargas-alertas/{cargaId}')
def obtener_carga(cargaId: UUID):
    row=run('''SELECT id,fuente,fecha_corte,cargada_en,cargada_por,alertas_en_archivo,
        alertas_nuevas,alertas_existentes,alertas_fuera_ambito,alertas_ausentes,
        zonas_creadas,zonas_actualizadas,resumen FROM cargas_alertas WHERE id=%s''',(cargaId,),one=True)
    if not row: fail(404,'Carga no encontrada')
    return json_safe(row)

@app.get('/zonas/{codigo}/marcas')
def listar_marcas(codigo: str, incluir_retiradas: bool=False):
    ensure_zone(codigo)
    return json_safe(run('SELECT * FROM marcas WHERE zona_codigo=%s AND (%s OR activa) ORDER BY creada_en DESC',
                         (codigo,incluir_retiradas)))

@app.get('/zonas/{codigo}/marcas/{marcaId}')
def obtener_marca(codigo: str,marcaId: UUID):
    row=run('SELECT * FROM marcas WHERE zona_codigo=%s AND id=%s',(codigo,marcaId),one=True)
    if not row: fail(404,'Marca no encontrada')
    return json_safe(row)

# El API requiere actor autenticado para crear/retirar marcas, ajustes y cambios.
# No se habilitan escrituras sin identidad verificable: implementar /auth/sesion primero.
def ensure_zone(codigo):
    if not run('SELECT codigo FROM zonas_cambio WHERE codigo=%s',(codigo,),one=True): fail(404,'Zona no encontrada')

@app.get('/zonas/{codigo}/ajustes')
def listar_ajustes(codigo: str):
    ensure_zone(codigo)
    return json_safe(run('SELECT * FROM ajustes_prioridad WHERE zona_codigo=%s ORDER BY creado_en DESC',(codigo,)))

@app.get('/zonas/{codigo}/ajustes/{ajusteId}')
def obtener_ajuste(codigo: str, ajusteId: UUID):
    row=run('SELECT * FROM ajustes_prioridad WHERE zona_codigo=%s AND id=%s',(codigo,ajusteId),one=True)
    if not row: fail(404,'Ajuste no encontrado')
    return json_safe(row)

@app.get('/zonas/{codigo}/historial')
def historial(codigo: str):
    ensure_zone(codigo)
    return json_safe(run('''SELECT h.id,h.tipo_accion,h.fecha_hora,h.codigo_alerta_origen,h.estado_anterior,
        h.estado_nuevo,h.ajuste_id,h.forma,h.nivel_elegido,h.puntaje_calculado,h.puntaje_ajustado,
        h.marca_id,h.texto_marca,h.texto,
        json_build_object('id',u.id,'nombre_completo',u.nombre_completo) AS autor
        FROM entradas_historial h JOIN usuarios u ON u.id=h.autor_id
        WHERE h.zona_codigo=%s ORDER BY h.fecha_hora DESC''',(codigo,)))

@app.get('/zonas/{codigo}/historial/{entradaId}')
def historial_entrada(codigo: str,entradaId: UUID):
    rows=run('''SELECT h.id,h.tipo_accion,h.fecha_hora,h.codigo_alerta_origen,h.estado_anterior,
        h.estado_nuevo,h.ajuste_id,h.forma,h.nivel_elegido,h.puntaje_calculado,h.puntaje_ajustado,
        h.marca_id,h.texto_marca,h.texto,
        json_build_object('id',u.id,'nombre_completo',u.nombre_completo) AS autor
        FROM entradas_historial h JOIN usuarios u ON u.id=h.autor_id
        WHERE h.zona_codigo=%s AND h.id=%s''',(codigo,entradaId),one=True)
    if not rows: fail(404,'Entrada de historial no encontrada')
    return json_safe(rows)

@app.get('/trabajos/{trabajoId}')
def obtener_trabajo(trabajoId: UUID):
    row=run('SELECT * FROM trabajos WHERE id=%s',(trabajoId,),one=True)
    if not row: fail(404,'Trabajo no encontrado')
    return json_safe(row)
