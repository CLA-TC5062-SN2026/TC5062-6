# Refactorización de usuarios

Base original: commit `6ef384d`. Los tres cambios fueron aprobados antes de editar el backend. Las ubicaciones originales son de ese commit.

## 1. Evitar bloqueo global en cambios exclusivos de nombre

**Hallazgo y ubicación:** [code review, hallazgo 1](code_review.md), `backend/app/routers/usuarios.py:73`.

Antes:

```python
coordinacion = db.query(conn, "SELECT id FROM usuarios WHERE rol='coordinacion' AND activo ORDER BY id FOR UPDATE")
```

Después:

```python
coordinacion = []
if set(cambios) != {'nombre_completo'}:
    coordinacion = db.query(
        conn, "SELECT id FROM usuarios WHERE rol='coordinacion' "
              "AND activo ORDER BY id FOR UPDATE")
```

El cambio de nombre no puede desactivar ni retirar el rol de una coordinación. El bloqueo de la fila objetivo se mantiene; el orden de bloqueo global no cambia para las demás actualizaciones. Archivos: [usuarios.py](../backend/app/routers/usuarios.py) y [test_api_usuarios.py](../backend/tests/test_api_usuarios.py).

**Verificación:** la nueva prueba mantiene bloqueada otra coordinación y comprueba que el PATCH de nombre termina antes de liberar ese bloqueo. Las pruebas existentes de la última coordinación y desactivaciones simultáneas siguen pasando.

## 2. Clasificar correctamente los conflictos de unicidad

**Hallazgo y ubicación:** [code review, hallazgo 2](code_review.md), `backend/app/routers/usuarios.py:42-43`.

Antes:

```python
except UniqueViolation:
    raise ApiError(409, 'CORREO_DUPLICADO', 'Ya existe una cuenta con ese correo') from None
```

Después:

```python
except UniqueViolation as exc:
    if exc.diag.constraint_name != 'uq_usuarios_correo_ci':
        raise
    raise ApiError(409, 'CORREO_DUPLICADO', 'Ya existe una cuenta con ese correo') from None
```

Solo el índice de correo produce el 409 documentado. Las demás violaciones no se disfrazan como error de entrada y se propagan al manejador general. Archivos: [usuarios.py](../backend/app/routers/usuarios.py) y [test_usuarios_unit.py](../backend/tests/test_usuarios_unit.py).

**Verificación:** la prueba unitaria cubre el índice de correo, otra restricción y una restricción sin nombre; la prueba HTTP existente confirma el 409 para correo duplicado.

## 3. Limitar y componer los identificadores SQL

**Hallazgo y ubicación:** [code review, hallazgo 3](code_review.md), `backend/app/routers/usuarios.py:82-84`.

Antes:

```python
asignaciones = ', '.join(f'{campo}=%s' for campo in cambios)
fila = db.query(conn, f'UPDATE usuarios SET {asignaciones} WHERE id=%s RETURNING {USER_FIELDS}',
                (*cambios.values(), usuarioId), one=True)
```

Después:

```python
if not cambios or not cambios.keys() <= (
    UsuarioActualizar.model_fields.keys()
):
    raise ValueError(
        'Los cambios deben contener únicamente campos editables'
    )
# Dentro de la transacción:
asignaciones = sql.SQL(', ').join(
    sql.SQL('{}=%s').format(sql.Identifier(campo)) for campo in cambios)
sentencia = sql.SQL(
    'UPDATE usuarios SET {} WHERE id=%s RETURNING {}'
).format(asignaciones, sql.SQL(USER_FIELDS))
fila = db.query(conn, sentencia,
                (*cambios.values(), usuarioId), one=True)
```

La lista permitida proviene del modelo que ya gobierna PATCH y los identificadores se componen con Psycopg. No se cambia la parametrización de valores. Los endpoints ya impedían claves extra; esta defensa cubre también llamadas internas futuras. Archivos: [usuarios.py](../backend/app/routers/usuarios.py) y [test_usuarios_unit.py](../backend/tests/test_usuarios_unit.py).

**Verificación:** la prueba unitaria rechaza un diccionario vacío, un campo inmutable y una clave con sintaxis SQL antes de abrir la transacción. Las pruebas HTTP existentes cubren PUT, PATCH y campos extra.

## Resultados

La primera ejecución aislada de la versión original aprobó 226 pruebas con una advertencia; la ejecución focalizada posterior aprobó 51. La ejecución final completa aprobó 233 pruebas con la misma advertencia. Los registros completos, incluida la tentativa inicial sin base accesible, están en [pytest inicial](output_pytest_inicial.txt) y [pytest final](output_pytest_final.txt).

El análisis estático posterior dejó 200 `E501` y 13 diagnósticos mypy, frente a 203 y 13 inicialmente. Ambos comandos terminan con código 1. El archivo [output_linter.txt](output_linter.txt) conserva las ejecuciones, incluida la intermedia. Las cifras no son una medida de defectos funcionales.
