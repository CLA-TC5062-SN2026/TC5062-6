"""La configuración rechaza secretos débiles y tokens sin expiración (fail-fast al arrancar)."""
import pytest
from pydantic import ValidationError

from app.config import Settings

BASE = {'database_url': 'postgresql://u:p@localhost/db', 'jwt_secret': 'x' * 32, 'jwt_expiration': 3600}


@pytest.mark.parametrize('cambio', [
    {'jwt_secret': 'corto'},
    {'jwt_secret': 'CAMBIAR_por_un_secreto_aleatorio_de_al_menos_32_bytes'},
    {'jwt_expiration': 0},
    {'jwt_expiration': -1},
    {'jwt_expiration': 86_401},
])
def test_configuracion_insegura_impide_arrancar(cambio):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{**BASE, **cambio})


@pytest.mark.parametrize('faltante', ['jwt_secret', 'jwt_expiration', 'database_url'])
def test_variables_obligatorias_sin_valor_por_defecto(faltante, monkeypatch):
    monkeypatch.delenv(faltante.upper(), raising=False)
    datos = {k: v for k, v in BASE.items() if k != faltante}
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **datos)


def test_configuracion_valida():
    assert Settings(_env_file=None, **BASE).jwt_expiration == 3600
