# Code review: gestión de usuarios

## Alcance

Versión original: commit `6ef384d`. Se eligió [usuarios.py](../backend/app/routers/usuarios.py) frente a `consultas.py` y `auth.py`: reúne creación idempotente, transacciones, unicidad, cambios de rol, bloqueo concurrente y revocación de sesiones. La selección se basa en estas responsabilidades y dependencias, no en una medición de complejidad ciclomática. Flake8 no emitió `C901` con umbral 10.

Las líneas siguientes corresponden a `6ef384d`, no necesariamente a la versión modificada. Los fragmentos corregidos de los hallazgos 1 a 3 se aplicaron; los de 4 y 5 son propuestas pendientes.

## 1. Bloqueo global innecesario para cambios de nombre

**Original:** `backend/app/routers/usuarios.py:73-75`.

```python
coordinacion = db.query(conn, "SELECT id FROM usuarios WHERE rol='coordinacion' AND activo ORDER BY id FOR UPDATE")
actual = encontrado(db.query(conn, 'SELECT rol, activo FROM usuarios WHERE id=%s FOR UPDATE', (usuarioId,), one=True),
                    f'No existe el usuario {usuarioId}')
```

El bloqueo de todas las coordinaciones activas protege la regla de última coordinación, pero también se ejecuta cuando el único cambio es el nombre de una cuenta. Esos cambios no afectan la regla y pueden esperar por transacciones sobre otras cuentas. El riesgo es contención innecesaria; no se ha medido su impacto.

**Corrección aplicada:**

```python
coordinacion = []
if set(cambios) != {'nombre_completo'}:
    coordinacion = db.query(
        conn, "SELECT id FROM usuarios WHERE rol='coordinacion' "
              "AND activo ORDER BY id FOR UPDATE")
```

La fila objetivo sigue bloqueándose. Los cambios de rol o estado mantienen la consulta y el orden de bloqueo original. La prueba concurrente nueva mantiene bloqueada otra coordinación mientras cambia el nombre.

## 2. Cualquier violación de unicidad se presenta como correo duplicado

**Original:** `backend/app/routers/usuarios.py:37-43`.

```python
try:
    fila = db.query(conn, f'INSERT INTO usuarios (nombre_completo, correo, rol, password_hash) '
                          f'VALUES (%s, %s, %s, %s) RETURNING {USER_FIELDS}',
                    (body.nombre_completo, str(body.correo), body.rol, hashear(body.password_temporal)),
                    one=True)
except UniqueViolation:
    raise ApiError(409, 'CORREO_DUPLICADO', 'Ya existe una cuenta con ese correo') from None
```

El esquema también define la clave primaria de usuarios, además del índice `uq_usuarios_correo_ci` ([esquema](../S05_S06_A1/esquema_bd.sql)). Una colisión de otra restricción, improbable con UUID generado, se comunicaría erróneamente como conflicto de correo. El riesgo es diagnóstico falso y ocultación de un error interno.

**Corrección aplicada:**

```python
except UniqueViolation as exc:
    if exc.diag.constraint_name != 'uq_usuarios_correo_ci':
        raise
    raise ApiError(409, 'CORREO_DUPLICADO', 'Ya existe una cuenta con ese correo') from None
```

El conflicto de correo conserva su contrato 409. Las demás violaciones se propagan para su registro y tratamiento como error inesperado.

## 3. Identificadores SQL interpolados

**Original:** `backend/app/routers/usuarios.py:81-84`.

```python
# Los nombres de columna provienen del esquema (extra='forbid'), nunca del cliente.
asignaciones = ', '.join(f'{campo}=%s' for campo in cambios)
fila = db.query(conn, f'UPDATE usuarios SET {asignaciones} WHERE id=%s RETURNING {USER_FIELDS}',
                (*cambios.values(), usuarioId), one=True)
```

Los valores están parametrizados y los dos endpoints actuales derivan las claves de modelos que rechazan campos extra. Por tanto no se afirma una inyección explotable en esos endpoints. El helper acepta, sin embargo, cualquier `dict`; una futura llamada interna podría saltarse ese límite e interpolar identificadores arbitrarios.

**Corrección aplicada:**

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

La validación rechaza claves no editables y `Identifier` compone los nombres; los valores siguen parametrizados.

## 4. Hash costoso dentro de la transacción de creación

**Original:** `backend/app/routers/usuarios.py:33-43`.

```python
with db.transaction() as conn:
    previa = db.respuesta_previa(conn, clave, operacion, huella)
    if previa:
        return JSONResponse(previa['cuerpo_respuesta'], previa['estado_http'], {'Location': previa['location']})
    try:
        fila = db.query(conn, f'INSERT INTO usuarios (nombre_completo, correo, rol, password_hash) '
                              f'VALUES (%s, %s, %s, %s) RETURNING {USER_FIELDS}',
                        (body.nombre_completo, str(body.correo), body.rol, hashear(body.password_temporal)),
                        one=True)
    except UniqueViolation:
        raise ApiError(409, 'CORREO_DUPLICADO', 'Ya existe una cuenta con ese correo') from None
```

La llamada a `respuesta_previa` toma un bloqueo consultivo transaccional ([db.py:61](../backend/app/db.py#L61)); `hashear` ejecuta Argon2 antes de liberar la conexión y ese bloqueo. En concurrencia, solicitudes con la misma clave esperan durante el hash. No se midió el impacto.

**Alternativa no aplicada:** calcular el hash antes de abrir la transacción, conservando la consulta idempotente dentro de ella:

```python
password_hash = hashear(body.password_temporal)
with db.transaction() as conn:
    previa = db.respuesta_previa(conn, clave, operacion, huella)
    if previa:
        return JSONResponse(previa['cuerpo_respuesta'], previa['estado_http'], {'Location': previa['location']})
    # El INSERT existente recibe password_hash como cuarto parámetro.
```

Esta alternativa reduce el tiempo bajo bloqueo, pero también calcula el hash en cada reintento exitoso. Antes de adoptarla hay que medir ambos casos y evaluar una doble comprobación idempotente; no se cambió el comportamiento en esta auditoría.

## 5. Orden no determinista entre nombres iguales

**Original:** `backend/app/routers/usuarios.py:52-54`.

```python
def listar_usuarios(activo: bool | None = None):
    return db.run(f'SELECT {USER_FIELDS} FROM usuarios WHERE (%s::boolean IS NULL OR activo=%s) ORDER BY nombre_completo',
                  (activo, activo))
```

El esquema no exige nombres únicos. Cuando dos filas comparten nombre, SQL no garantiza su orden relativo; un cliente puede ver cambios de orden entre lecturas sin que hayan cambiado esas cuentas. La consulta tampoco pagina, lo que se registra como deuda independiente.

**Propuesta no aplicada:** añadir un desempate estable por clave primaria.

```python
return db.run(
    f'SELECT {USER_FIELDS} FROM usuarios '
    'WHERE (%s::boolean IS NULL OR activo=%s) '
    'ORDER BY nombre_completo, id',
    (activo, activo))
```

La propuesta modifica el orden de los empates, por lo que requiere acordarlo y probarlo antes de incorporarla.

## SOLID

El análisis se refiere a la versión original y a sus colaboraciones, no presupone que todo principio deba aplicarse mediante herencia.

| Principio | Evaluación | Evidencia y explicación | Propuesta |
|---|---|---|---|
| SRP | Parcialmente | `usuarios.py:26-47` mezcla HTTP, idempotencia, hash, persistencia y conversión de errores. `usuarios.py:69-87` mezcla reglas de negocio y SQL. Hay responsabilidades relacionadas, pero cambios de infraestructura y reglas pueden afectar las mismas funciones. | Separar gradualmente la operación de cuentas de sus adaptadores HTTP y SQL, conservando la transacción como unidad. |
| OCP | Parcialmente | `usuarios.py:75-86` codifica la regla de última coordinación y revocación; añadir otras reglas de actualización exige modificar la función. Eso es razonable en un dominio pequeño, pero concentra cambios. | Si aparecen nuevas reglas, extraer validaciones de dominio con pruebas y mantener una transacción explícita; no introducir una jerarquía anticipadamente. |
| LSP | No evaluable con esta evidencia | `schemas.py:68` define `Usuario(UsuarioRef)` agregando campos obligatorios, pero en el módulo revisado no se observa sustitución de un `UsuarioRef` por un `Usuario` en un consumidor polimórfico. La herencia por sí sola no demuestra ni cumplimiento general ni infracción. | Sin corrección exigible; evaluar un consumidor concreto y sus contratos si se introduce sustitución polimórfica. |
| ISP | No evaluable directamente | `usuarios.py:8-13` importa funciones de DB y seguridad, pero no se identificó una interfaz propia que obligue a un cliente a depender de operaciones que no usa. El acoplamiento al adaptador concreto se analiza en DIP, no demuestra una infracción de ISP. | Sin corrección exigible; si se introducen interfaces, evaluar qué operaciones requiere cada cliente. |
| DIP | No | `usuarios.py:8-13` y `:33-46` dependen directamente del módulo `db`, Psycopg y FastAPI. La regla de negocio no depende de un puerto independiente. | Inyectar un repositorio o unidad de trabajo explícita al extraer el servicio, sin perder atomicidad ni bloqueos. |

## Verificación y límites

Las pruebas existentes verifican conflicto de correo, idempotencia, PUT/PATCH, revocación y concurrencia. Las pruebas nuevas cubren el bloqueo de nombre, la clasificación de restricciones y claves no editables. Véanse [refactorización](refactorizacion.md), [pytest inicial](output_pytest_inicial.txt) y [pytest final](output_pytest_final.txt). No se hizo una evaluación de carga ni se afirma ausencia de vulnerabilidades.
