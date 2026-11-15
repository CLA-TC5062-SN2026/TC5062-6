from contextlib import nullcontext
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import Response
from psycopg.errors import UniqueViolation

from app import db
from app.errors import ApiError
from app.routers import usuarios
from app.schemas import UsuarioCrear


class ViolacionUnicidad(UniqueViolation):
    def __init__(self, restriccion):
        super().__init__('violacion de unicidad')
        self.restriccion = restriccion

    @property
    def diag(self):
        return SimpleNamespace(constraint_name=self.restriccion)


@pytest.mark.parametrize('restriccion', ['uq_usuarios_correo_ci', 'usuarios_pkey', None])
def test_solo_el_conflicto_de_correo_se_traduce_a_409(monkeypatch, restriccion):
    error = ViolacionUnicidad(restriccion)
    monkeypatch.setattr(db, 'transaction', lambda: nullcontext(object()))
    monkeypatch.setattr(db, 'respuesta_previa', lambda *args: None)
    monkeypatch.setattr(usuarios, 'hashear', lambda _: 'hash-de-prueba')

    def fallar(*args, **kwargs):
        raise error

    monkeypatch.setattr(db, 'query', fallar)
    body = UsuarioCrear(nombre_completo='Nombre', correo='prueba@example.org',
                        rol='analista_sig', password_temporal='valor-de-prueba')
    esperado = ApiError if restriccion == 'uq_usuarios_correo_ci' else ViolacionUnicidad
    with pytest.raises(esperado) as capturado:
        usuarios.insertar_usuario(body, None, Response(), uuid4(), uuid4())
    if restriccion == 'uq_usuarios_correo_ci':
        assert capturado.value.status == 409
        assert capturado.value.codigo == 'CORREO_DUPLICADO'
    else:
        assert capturado.value is error


@pytest.mark.parametrize('cambios', [{}, {'correo': 'otro@example.org'}, {'activo; DROP TABLE usuarios': True}])
def test_aplicar_cambios_rechaza_campos_no_editables_antes_de_abrir_transaccion(monkeypatch, cambios):
    def transaccion_inesperada():
        pytest.fail('No debe abrir una transaccion con campos invalidos')

    monkeypatch.setattr(db, 'transaction', transaccion_inesperada)
    with pytest.raises(ValueError, match='campos editables'):
        usuarios.aplicar_cambios(uuid4(), cambios)
