# Clasificación del análisis estático inicial

Base: commit `6ef384d`, antes de cambios de código. La salida completa y las versiones están en [output_linter.txt](output_linter.txt). Flake8 se ejecutó con su configuración predeterminada y `--max-complexity=10`; mypy utilizó el intérprete de dependencias del backend sin configuración de proyecto adicional. Ambos terminaron con código 1. No se suprimieron diagnósticos.

La severidad refleja el impacto evaluado aquí, no el nombre `error` de mypy. Las advertencias de tipos pueden describir limitaciones de inferencia, no necesariamente fallos en ejecución.

## Críticos

Ninguno de los diagnósticos emitidos demuestra por sí solo un fallo crítico. Esto no equivale a certificar la ausencia de vulnerabilidades.

## Importantes

| Archivo y línea original | Regla | Impacto y justificación |
|---|---|---|
| `backend/app/cli.py:46` | mypy `index` | Se indexa el resultado opcional de `fetchone()`. El `INSERT ... RETURNING` normalmente devuelve una fila, pero el código no expresa ni comprueba ese supuesto; una ausencia inesperada produciría una excepción. |
| `backend/app/dependencies.py:63` | mypy `union-attr` | Las credenciales son opcionales para el analizador. `_no_autenticado` siempre lanza una excepción, pero carece de anotación `NoReturn`; el flujo es seguro en el código actual y no se ha demostrado una omisión de autenticación. La falta de información de flujo dificulta verificar código de seguridad. |
| `backend/app/routers/auth.py:55` | mypy `arg-type`, dos diagnósticos | `Identidad` declara `usuario` como `dict` y `ultima_actividad` como `object`, mientras `SesionActual` declara `Usuario` y `datetime`. Pydantic acepta datos de entrada y valida en ejecución, pero los tipos actuales no permiten comprobar estáticamente que la fila de sesión tenga la estructura requerida. |

## Menores

| Archivo y línea original | Regla | Impacto y justificación |
|---|---|---|
| `backend/app/config.py:41` | mypy `call-arg`, tres diagnósticos | `Settings()` obtiene los campos obligatorios del entorno mediante `BaseSettings`. Mypy sin soporte específico no infiere esa carga; no se demuestra una ausencia real de configuración. |
| `backend/app/db.py:56` | mypy `union-attr` | El analizador conserva el tipo opcional del secreto global. El módulo ya lanza `RuntimeError` al importarse si falta; el diagnóstico refleja una limitación de inferencia del invariante. |
| `backend/app/routers/consultas.py:65` | mypy `arg-type` | La lista de parámetros comienza vacía y se infiere a partir de la inserción de una cadena, aunque también recibe un booleano. Psycopg admite parámetros heterogéneos; conviene declarar su tipo para hacer comprobable el código. |
| `backend/app/main.py:39` | mypy `arg-type`, cuatro diagnósticos | El diccionario `docs` expandido con `**` pierde la relación entre nombres y tipos de argumentos de `FastAPI`. No se demuestra un fallo de arranque; el patrón reduce la precisión del análisis. |
| Archivos y líneas enumerados abajo | flake8 `E501` | Líneas de más de 79 caracteres: perjudican lectura y revisión, sin demostrar por sí mismas un defecto funcional. |

### Ubicaciones completas de `E501`

En cada fila la regla y el impacto son los de `E501` indicados arriba. Todas las columnas son 80; los largos exactos figuran en la salida original.

| Archivo | Líneas originales |
|---|---|
| `backend/app/cli.py` | 1, 3, 4, 5, 32, 35, 36, 37, 38, 39, 42, 44, 52 |
| `backend/app/config.py` | 3, 10, 16, 20, 33, 35 |
| `backend/app/db.py` | 1, 20, 25, 54, 55, 56, 60, 61, 62, 63, 64, 65, 66, 70, 71, 73 |
| `backend/app/dependencies.py` | 1, 3, 4, 23, 26, 27, 36, 53, 55, 59, 69, 70, 78, 83, 84, 86, 88 |
| `backend/app/errors.py` | 1, 14, 16, 29, 30, 34, 54, 56, 64, 68, 69, 70, 73, 78, 79, 81, 82, 87, 88 |
| `backend/app/main.py` | 1, 3, 16, 37, 38, 39, 52, 53 |
| `backend/app/routers/auth.py` | 1, 12, 15, 23, 24, 26, 27, 30, 35, 36, 38, 40, 41, 45, 47, 48, 51, 55, 60, 61, 65, 67, 70, 72, 74, 76, 78 |
| `backend/app/routers/consultas.py` | 1, 10, 16, 20, 22, 25, 26, 30, 31, 32, 34, 35, 37, 39, 41, 42, 43, 44, 50, 54, 58, 68, 69, 70, 71, 74, 79, 81, 84, 88, 92, 95, 99, 102, 105, 107, 111, 112, 116, 119, 122, 126, 128, 129 |
| `backend/app/routers/usuarios.py` | 1, 12, 16, 18, 22, 23, 26, 27, 29, 36, 38, 39, 40, 43, 45, 46, 53, 59, 60, 65, 70, 72, 73, 74, 78, 80, 81, 83, 86, 96 |
| `backend/app/schemas.py` | 1, 6, 10, 11, 15, 16, 40, 50 |
| `backend/app/security.py` | 3, 4, 5, 29, 30, 38, 39, 41, 42, 44, 48, 53, 58, 61, 65 |

Flake8 emitió 203 diagnósticos `E501` y ningún `C901` con el umbral indicado. Mypy emitió 13 diagnósticos en 7 archivos. Estos resultados describen exclusivamente la versión original.

La ejecución final con [configuración de flake8](../backend/.flake8) y [configuración de mypy](../backend/mypy.ini) registró 200 `E501` y 13 diagnósticos mypy, ambos con código 1. Sus líneas actuales y la ejecución intermedia están identificadas por separado en [output_linter.txt](output_linter.txt). Mypy usa los valores predeterminados y no comprueba por completo las funciones sin anotaciones.
