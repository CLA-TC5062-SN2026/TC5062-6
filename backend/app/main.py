"""EcoAlert: API REST con autenticación JWT y control de acceso por rol.

Implementa un subconjunto del contrato `openapi_equipo.yaml`; ver README para el alcance.
"""
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Request

from app import db
from app.config import get_settings
from app.dependencies import autenticar
from app.errors import registrar_manejadores
from app.routers import auth, consultas, usuarios

PREFIJO_API = '/api/v1'
# OWASP REST Security Cheat Sheet: cabeceras para respuestas de API que no deben cachearse ni renderizarse.
CABECERAS_SEGURIDAD = {
    'Cache-Control': 'no-store',
    'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer',
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.abrir(get_settings().database_url.get_secret_value())
    try:
        yield
    finally:
        db.cerrar()


def crear_app() -> FastAPI:
    cfg = get_settings()
    docs = {} if cfg.api_docs else {'docs_url': None, 'redoc_url': None, 'openapi_url': None}
    app = FastAPI(title='EcoAlert Tambopata - API', version='0.2.0', lifespan=lifespan,
                  description='Implementación parcial del contrato OpenAPI; ver README para límites.', **docs)
    registrar_manejadores(app)

    @app.middleware('http')
    async def cabeceras_seguridad(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith(PREFIJO_API):
            for nombre, valor in CABECERAS_SEGURIDAD.items():
                response.headers.setdefault(nombre, valor)
        return response

    @app.get('/salud', tags=['Operación'])
    def salud():
        # Fuera de /api/v1 y sin datos de negocio: lo consulta el healthcheck de Docker sin token.
        return {'estado': 'ok', 'base_datos': bool(db.run('SELECT 1 AS ok', one=True))}

    api = APIRouter(prefix=PREFIJO_API)
    api.include_router(auth.publico)
    # Denegación por defecto: todo lo que se monte aquí exige un token válido.
    protegidas = APIRouter(dependencies=[Depends(autenticar)])
    protegidas.include_router(auth.protegido)
    protegidas.include_router(usuarios.router)
    protegidas.include_router(consultas.router)
    api.include_router(protegidas)
    app.include_router(api)
    return app


app = crear_app()
