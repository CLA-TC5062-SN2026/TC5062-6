# Revisión del esquema SQL — EcoAlert Tambopata

**Artefacto revisado:** `esquema_bd.sql`  
**Referencias:** `diagrama_clases_equipo.puml`, `openapi_equipo.yaml` y SRS del equipo.  
**Motor:** PostgreSQL 17 + PostGIS.  
**Resultado:** se corrigió el SQL original **antes de ejecutarlo** (secciones 1 a 6, validación estática). El 25/10/2026 se ejecutó por primera vez en PostgreSQL/PostGIS real y esa ejecución descubrió un defecto adicional; ver la sección 7.

## 1. Criterio de correspondencia con el diagrama

El diagrama consolidado representa **62 schemas OpenAPI** (entidades, DTO de solicitudes y respuestas, enumeraciones, vistas y tipos auxiliares). Por tanto, **no corresponde crear 62 tablas**: `UsuarioCrear`, `ZonaResumen`, `FeatureCollection`, `ListaZonas` o `AjusteSolicitud`, por ejemplo, son contratos de intercambio y no entidades con ciclo de vida independiente.

El SQL revisado incluye **22 tablas** de persistencia (las 21 del diseño original más `claves_idempotencia`, sección 7.4): `usuarios`, `sesiones`, `archivos_temporales`, `capas_referencia`, `versiones_capa`, `elementos_capa`, `cargas_alertas`, `zonas_cambio`, `alertas`, `carga_alerta_detalle`, `prioridades`, `factores_prioridad`, `ajustes_prioridad`, `marcas`, `entradas_historial`, `contextos_territoriales`, `superposiciones`, `analisis`, `fuentes_usadas`, `resultados_zona` y `trabajos`.

Las representaciones compuestas del API se reconstruyen mediante consultas y lógica de aplicación: `ZonaDetalle` y `ZonaResumen` desde zonas, prioridades, alertas, contexto y marcas; `AnalisisResumen` desde `analisis`; `Periodo` desde las columnas de cada periodo; `SesionActual` desde `sesiones` y `usuarios`. Los campos calculados, como `num_alertas`, `fecha_alerta_mas_reciente`, `texto_frescura`, `conteos` y `puntaje_calculado`, no requieren duplicarse como columnas persistentes. Los campos `fuentes`, `factores`, `superposiciones` y `resultados` se reconstruyen desde tablas relacionadas.

**Advertencia de modelado:** el diagrama de la Parte 0 es primordialmente un **diagrama de schemas API**, no un diagrama entidad–relación físico. Algunas tablas necesarias (`sesiones`, `elementos_capa`, `archivos_temporales`, `carga_alerta_detalle`) son entidades técnicas o asociaciones derivadas de las operaciones y del dominio, aunque no tengan una clase homónima. Esto es una decisión explícita de diseño, no una correspondencia literal tabla-clase.

## 2. Correcciones aplicadas al SQL

| Prioridad | Hallazgo en el SQL original | Corrección realizada | Fundamento |
|---|---|---|---|
| Alta | `ajustes_prioridad.forma` admitía `puntaje`/`nivel`, distintos de OpenAPI. | Se cambió a `por_puntaje`/`por_nivel`. | Schemas `AjustePrioridad`, `AjusteVigente`. |
| Alta | El ajuste solo admitía `vigente`/`retirado`. | Se incorporó `reemplazado`, con reglas de cierre diferenciadas del retiro. | Schema `AjustePrioridad`. |
| Alta | No se comprobaba que `nivel_elegido` correspondiera con la forma. | `por_puntaje` exige `nivel_elegido IS NULL`; `por_nivel` exige `alta`/`media`/`baja`. | `AjustePrioridad` y `NivelPrioridad`. |
| Alta | El código de zona aceptaba cualquier número de dígitos tras el año. | Se restringió a `EA-AAAA-NNN` (exactamente tres dígitos). | `CodigoZona` del OpenAPI. |
| Alta | `marcas.tipo` aceptaba cualquier texto. | Se limitó a `area_pequena`, `posible_dinamica_fluvial` y `marca_analista`. | Schema `Marca`. |
| Alta | Podían mezclarse marca automática y marca del analista. | Se validó la correspondencia `origen`–`tipo` y la presencia/ausencia de autor. | RF-13 / `Marca`. |
| Alta | `trabajos.tipo`, `trabajos.estado`, `resultados_zona.presencia` y `analisis.estado` eran textos libres. | Se añadieron `CHECK` con los valores enumerados por OpenAPI. | Schemas `Trabajo`, `ResultadoZona`, `AnalisisResumen`. |
| Media | Un cálculo podía guardar `puntaje NULL` con nivel disponible o viceversa. | Se agregó coherencia entre `prioridades.puntaje` y `prioridades.nivel`. | Schema `Prioridad`. |
| Media | Un factor podía declararse disponible sin valor ni aporte. | Se exigió valor y aporte cuando `disponible=true`, y `NULL` cuando no lo está; se exigió explicación. | Schema `Factor`. |
| Media | No se controlaba la secuencia temporal de ciertos eventos. | Se añadieron controles sobre actividad de sesión, retiro de ajustes, retiro de marcas y actualización de trabajos. | Integridad temporal básica. |
| Media | Las superficies estaban a seis decimales aunque las respuestas exigen múltiplos de 0.01. | Se adoptó `NUMERIC(18,2)` para áreas expuestas y diferencias de análisis. | Schemas `Alerta`, `ZonaDetalle`, `ResultadoZona`. |
| Baja | Correo podía contener espacios laterales y `tipo_accion` estar vacío. | Se reforzaron validaciones de correo y acción no vacía. | Calidad de datos. |

## 3. Revisión de llaves y cardinalidades

- **Usuarios 1:N sesiones, versiones, cargas, ajustes, marcas de analista, historial y análisis:** FKs hacia `usuarios(id)`. No se permite eliminar físicamente al usuario referenciado; se usa `activo`.
- **Capa de referencia 1:N versiones; versión 1:N elementos:** FK `versiones_capa.tipo → capas_referencia.tipo` y `elementos_capa.version_capa_id → versiones_capa.id`. Solo una versión `vigente` por tipo mediante índice único parcial.
- **Zona 1:N alertas, prioridades, ajustes, marcas, historial y contextos:** FKs a `zonas_cambio(codigo)`. `alertas.zona_codigo` es opcional en persistencia para ingestiones pendientes de agrupación; el API debe exponer el dato cuando corresponda.
- **Carga N:M alertas:** tabla puente `carga_alerta_detalle` con PK compuesta. Permite deduplicación global por `(fuente,codigo)` y trazabilidad de cargas sucesivas.
- **Prioridad 1:N factores, pero máximo un factor de cada tipo por cálculo:** PK `(prioridad_id,factor)`.
- **Contexto 1:N superposiciones:** FK `superposiciones.contexto_id`. La referencia a `elementos_capa` es opcional para conservar una instantánea descriptiva aun si el elemento no se identifica.
- **Análisis 1:N resultados y fuentes:** FKs desde `resultados_zona` y `fuentes_usadas`. La PK compuesta impide duplicar la misma zona dentro de un análisis.
- **Fuente usada pertenece exactamente a uno entre análisis, prioridad o contexto:** `CHECK (num_nonnulls(...) = 1)`; evita una FK polimórfica sin integridad.

**Puntos no resueltos solo con FK:** las FKs de `entradas_historial.ajuste_id` y `.marca_id` validan existencia, pero no garantizan que pertenezcan a la **misma zona** de la entrada. Esto requiere FKs compuestas adicionales o validación transaccional. También deben controlarse los cambios de estado permitidos, el vínculo entre trabajo y su resultado y la prohibición de modificar snapshots cerrados.

## 4. Tipos de datos y atributos

| OpenAPI | PostgreSQL | Evaluación |
|---|---|---|
| `string` con `format: uuid` | `UUID` | Correcto. |
| `string` con `format: date` | `DATE` | Correcto. |
| `string` con `format: date-time` | `TIMESTAMPTZ` | Correcto; conservar zona horaria de presentación en la aplicación. |
| `integer` | `INTEGER`/`SMALLINT` | Correcto para conteos, pesos y puntajes 0–100. |
| `number`/`double` | `NUMERIC` | Correcto para cálculo decimal y superficies; la serialización al API debe respetar precisión requerida. |
| `boolean` | `BOOLEAN` | Correcto. |
| `object`/`array` | `JSONB` o tablas hijas | Correcto según la naturaleza del dato. |
| Enum OpenAPI | Enum PostgreSQL o `CHECK` | Correcto tras correcciones. |
| Geometría GeoJSON | `geometry(Geometry,32719)` | Coherente con el SRS para cálculo en metros; convertir a EPSG:4326 al exportar. |

**Campos no almacenados literalmente:** `cargada_por`, `creado_por`, `autor`, `ejecutado_por` son objetos `UsuarioRef` en la API y FKs `*_id` en SQL; `version_vigente`, `ajuste_vigente`, `prioridad`, `contexto`, `rio_cercano` y `geometria` GeoJSON son relaciones o proyecciones. `password_hash`, `token_hash`, `ruta_interna` y las geometrías espaciales son campos internos necesarios que **no deben exponerse** en respuestas públicas.

## 5. Restricciones y pruebas todavía pendientes

1. **Inmutabilidad:** proteger `entradas_historial` y resultados de análisis cerrados contra `UPDATE`/`DELETE` mediante permisos o triggers; el SQL actual solo la documenta.
2. **Versiones de capas:** comprobar en una transacción que la vigente es la de `fecha_corte` más reciente. El índice parcial garantiza unicidad, **no** garantiza recencia.
3. **Prioridad:** comprobar que existan exactamente cinco factores por cálculo, que los pesos correspondan a la versión configurada, que se renormalicen los disponibles y que se respeten umbrales de nivel (alta ≥70, media 40–69, baja <40).
4. **Ajustes:** reemplazar el ajuste vigente anterior y crear el nuevo de forma atómica; registrar autor y justificación, impedir retiros incompletos.
5. **Geometrías:** validar geometrías, tipo geométrico por capa, SRID 32719, topología, agrupación a ≤500 m y ≤90 días; generar exportaciones RFC 7946 en EPSG:4326.
6. **Comparaciones:** mantener instantáneas reproducibles de zonas, puntajes y fuentes; evitar modificación de resultados una vez concluido el análisis.
7. **Consistencia entre zonas y eventos:** asegurar que ajustes/marcas vinculados al historial pertenezcan a la misma zona.
8. **Seguridad:** expiración por 30 minutos de inactividad, revocación y control de permisos en FastAPI; nunca almacenar contraseñas ni tokens en texto plano.
9. **Datos de prueba:** crear un usuario, una capa con dos versiones, una carga repetida, una zona con alertas, cinco factores, un ajuste reemplazado, una marca retirada y un análisis con dos periodos; probar fallos esperados de `CHECK`, `UNIQUE` y `FOREIGN KEY`.

## 6. Resultado y decisión

**Estado: revisado y corregido estáticamente; ejecutado y verificado parcialmente en PostgreSQL/PostGIS real (sección 7).** El esquema representa las entidades persistentes principales y las asociaciones del dominio sin transformar indiscriminadamente todos los DTO del diagrama en tablas. Se corrigieron incompatibilidades concretas con enumeraciones, patrones y reglas de negocio del OpenAPI. Antes de utilizarlo como esquema definitivo de producción deben completarse las pruebas pendientes de la sección 7; especialmente, reforzar la inmutabilidad y las restricciones cruzadas.

## 7. Ejecución real y correcciones posteriores (25/10/2026)

### 7.1 Ejecución del esquema

Entorno: Docker Engine 29.8.0, imagen `postgis/postgis:17-3.5` (PostgreSQL 17.5, PostGIS 3.5.2), contenedor `ecoalert_db`, base `ecoalert`. `esquema_bd.sql` se importó con `psql -v ON_ERROR_STOP=1` **sin errores**. Resultado verificado en el catálogo (estado previo a agregar `claves_idempotencia`, sección 7.4; el esquema vigente tiene **22 tablas y 22 PK**): 21 tablas del proyecto más `spatial_ref_sys` (auxiliar de PostGIS), 5 tipos enum, 21 PK, 32 FK (30 `RESTRICT`, 2 `SET NULL`), 4 `UNIQUE`, 57 `CHECK` y 56 índices (3 GiST sobre geometrías en SRID 32719).

### 7.2 Hallazgo H-1: `CHECK` de `ajustes_prioridad` aceptaba `por_nivel` sin nivel

| Elemento | Detalle |
|---|---|
| Problema original | La restricción `ajustes_prioridad_check1` aceptaba `forma = 'por_nivel'` con `nivel_elegido` nulo. La corrección 3 de la sección 2 declaraba lo contrario («por_nivel exige alta/media/baja»), pero era incompleta. |
| Causa | Lógica trivalente de SQL: `NULL IN ('alta','media','baja')` es `NULL`, y un `CHECK` solo rechaza cuando el resultado es `FALSE`. La rama `por_nivel` evaluaba `TRUE AND NULL = NULL`, así que la disyunción no fallaba. |
| Corrección | Se agregó `nivel_elegido IS NOT NULL` a la rama `por_nivel` y se nombró la restricción `ck_ajuste_forma_nivel` (antes, nombre automático `ajustes_prioridad_check1`). |
| Justificación | RF-11: «Por nivel: elige alta, media o baja» y «el historial registra la forma usada»; en el contrato, `AjustePorNivel` exige `nivel` y `AjustePrioridad.nivel_elegido` solo es nulo cuando la forma es `por_puntaje`. La base de datos es la segunda barrera si la capa de aplicación falla. |
| Archivo actualizado | `esquema_bd.sql`, tabla `ajustes_prioridad` (restricción con nombre explícito). |

Migración aplicada a la base existente, sin recrear contenedor, volumen ni base (la tabla estaba vacía):

```sql
BEGIN;
ALTER TABLE ajustes_prioridad DROP CONSTRAINT ajustes_prioridad_check1;
ALTER TABLE ajustes_prioridad ADD CONSTRAINT ck_ajuste_forma_nivel CHECK (
  (forma = 'por_puntaje' AND nivel_elegido IS NULL) OR
  (forma = 'por_nivel' AND nivel_elegido IS NOT NULL AND nivel_elegido IN ('alta','media','baja')));
COMMIT;
```

**Evidencia de ejecución** (transacción de prueba revertida, `INSERT` de un ajuste retirado válido salvo la columna evaluada):

| Caso | Antes de la migración | Después de la migración |
|---|---|---|
| `por_nivel` con `nivel_elegido` nulo | **Aceptado** (defecto) | Rechazado, SQLSTATE `23514` |
| `por_nivel` con `alta` | Aceptado | Aceptado |
| `por_nivel` con `no_disponible` | Rechazado | Rechazado |
| `por_puntaje` con `alta` | Rechazado | Rechazado |

Tras la migración se repitieron las 22 pruebas de integridad: 22 aprobadas, 0 fallidas, y las tablas quedaron sin filas tras el `ROLLBACK`.

### 7.3 Cambios SQL derivados de la conformidad con el contrato (F-13 y F-16)

| Hallazgo | Problema original | Corrección | Justificación | Evidencia |
|---|---|---|---|---|
| F-13 | `entradas_historial.autor_id` era `NOT NULL`: no se podía registrar al autor «Sistema». | `autor_id` admite `NULL`, protegido por `ck_historial_autor`: solo `zona_creada` puede carecer de autor. | RF-12-AC-19: la primera entrada es «zona creada» con usuario «Sistema». El contrato define `autor.tipo = sistema` con `id` nulo. No se sembró un usuario «Sistema» en `usuarios` para no contaminar la gestión de cuentas (RF-02) ni el conteo de coordinación. | `zona_creada` sin autor aceptada; `cambio_estado` sin autor rechazado (`23514`). |
| F-16 | `tipo_accion` y `forma` eran texto libre, aunque la sección 4 declaraba los enums «correctos». | `ck_historial_tipo_accion` (6 valores de `EntradaHistorial.tipo_accion`) y `ck_historial_forma` (`por_puntaje`, `por_nivel`). | RF-12 (creación, cambios de estado), RF-11 (ajustes y retiros, «el historial registra la forma usada») y RF-13 (marcas y retiros) son exactamente esos 6 tipos. | Tipo inexistente, tipo vacío y forma inválida rechazados (`23514`). |

```sql
BEGIN;
ALTER TABLE entradas_historial ALTER COLUMN autor_id DROP NOT NULL;
ALTER TABLE entradas_historial DROP CONSTRAINT entradas_historial_tipo_accion_check;
ALTER TABLE entradas_historial ADD CONSTRAINT ck_historial_tipo_accion CHECK (tipo_accion IN
  ('zona_creada','cambio_estado','ajuste_fijado','ajuste_retirado','marca_registrada','marca_retirada'));
ALTER TABLE entradas_historial ADD CONSTRAINT ck_historial_forma CHECK (forma IN ('por_puntaje','por_nivel'));
ALTER TABLE entradas_historial ADD CONSTRAINT ck_historial_autor CHECK (autor_id IS NOT NULL OR tipo_accion = 'zona_creada');
-- ... más la tabla claves_idempotencia de la sección 7.4, en la misma transacción.
COMMIT;
```

### 7.4 Persistencia adicional para la idempotencia (cambio e impacto)

El contrato exige que todo `POST` de creación reciba `Idempotency-Key` (UUID) y que, durante 24 h, repetir la clave con el mismo cuerpo devuelva la respuesta original (mismo estado, cuerpo y `Location`) sin repetir la operación; la misma clave con otro cuerpo responde `422 IDEMPOTENCIA_CONFLICTO`. Una caché en memoria no cumple esto (se pierde al reiniciar y no se comparte entre procesos), por lo que se agregó **una tabla**.

| Aspecto | Detalle |
|---|---|
| Cambio | Nueva tabla `claves_idempotencia` (clave UUID, operación, huella del cuerpo, estado HTTP 2xx, cuerpo de la respuesta, `Location`, fecha) e índice por fecha. Pasan a ser **22 tablas del proyecto**. No se modifica ninguna tabla existente por este motivo. |
| Naturaleza | Infraestructura de la API, no entidad de dominio (como `sesiones`): no cambia el OpenAPI ni el diagrama de clases. |
| Flujo | En la misma transacción de la creación: bloqueo consultivo por clave (serializa reintentos concurrentes), purga de filas de más de 24 h, búsqueda de la clave, ejecución de la operación y registro de la respuesta. Si la operación falla, la transacción se revierte y no queda clave. |
| Impacto | Una fila por `POST` exitoso, una escritura y una purga por `POST`, índice por `creada_en`. Reversible con `DROP TABLE claves_idempotencia`. |
| Decisiones | Solo se guardan respuestas 2xx (un 409 o 422 se revalúa en cada reintento y es determinista). La clave es global: reutilizarla en otra operación es un conflicto. La huella (`huella`) es un **HMAC-SHA256 del JSON canónico del cuerpo completo** (claves ordenadas, sin espacios, UTF-8), calculado con el secreto `IDEMPOTENCY_SECRET`. Sin ese secreto la huella no permite verificar ni derivar la contraseña temporal; el secreto vive en una variable de entorno, no en Git (`.env.example` solo trae un marcador) y la API no arranca sin él. |
| Limitación declarada | Ninguna respecto del contrato: cualquier cambio del cuerpo, incluida solo la contraseña temporal, responde `422 IDEMPOTENCIA_CONFLICTO`. Rotar el secreto invalida la comparación de las claves de las últimas 24 h (sus reintentos responderían 422). Este punto reemplaza la excepción que excluía la contraseña de la huella en la primera versión de esta sección. |
| Alcance | Solo `POST /usuarios`, la única operación de creación implementada. Las demás se acoplarán al mismo mecanismo al implementarlas. |

### 7.5 F-14 evaluado y no aplicado

La restricción de `marcas` exige `retirada_por` cuando la marca no está activa, de modo que el sistema no puede desactivar una marca automática. **No se confirma impacto respecto del SRS:** RF-13 dice que las marcas automáticas «se recalculan» y que solo las del analista «se retiran con motivo» y dejan huella en el historial; el contrato añade que las automáticas «no se retiran manualmente». El recálculo se puede resolver reemplazando filas, y las marcas automáticas no se referencian desde `entradas_historial`. Se mantiene el `CHECK`. Si el equipo decide conservar el historial de marcas automáticas inactivas, habrá que permitir `retirada_por` nulo cuando `origen = 'automatica'`.

### 7.6 Correcciones al backend (salida del agente frente a código corregido)

Fuentes de verdad: `openapi_equipo.yaml` y `SRS_equipo.md`. El código original era un único `main.py`; ahora se divide en `main.py` (rutas), `schemas.py`, `errors.py` y `db.py`. Se eliminaron los modelos de solicitud sin uso (cambio de estado, marcas y ajustes) y los imports sobrantes.

| Hallazgo | Código original | Corrección | Evidencia de ejecución |
|---|---|---|---|
| Prefijo (P0) | Rutas sin `/api/v1`. | `APIRouter(prefix='/api/v1')`; `/salud` queda fuera. | `/usuarios` sin prefijo responde 404. |
| F-02 | `GET /alertas` devolvía una lista sin filtros ni paginación. | `PaginaAlertas {total, limite, desplazamiento, alertas}` con `zona`, `presente_en_ultima_carga`, `limite` (1 a 500, por defecto 100) y `desplazamiento`. Solo publica alertas con zona y área, porque el contrato exige ambas. | Total, páginas, filtros y combinaciones sobre 6 alertas sembradas (2 omitidas); `limite=0`, `limite=501`, `zona` mal formada y booleano inválido responden 400. |
| F-03 | Contraseña temporal con `min_length=8`. | `min_length=12` (PS-15, RF-02-AC-3). | 11 caracteres: 422 con `Debe tener al menos 12 caracteres`. |
| F-07 | Historial con `ORDER BY fecha_hora DESC`. | Orden ascendente (`fecha_hora, id`). | Cuatro entradas insertadas fuera de orden salen como `zona_creada`, `cambio_estado`, `ajuste_fijado`, `marca_registrada`. |
| F-08 | `POST` sin `Location` ni `Idempotency-Key`. | `Location` generado desde la ruta `obtener_usuario`; `Idempotency-Key` obligatorio con persistencia (sección 7.4). | Reintento: mismo estado, cuerpo y `Location`, una sola fila; 10 solicitudes simultáneas con la misma clave dejan una fila; clave de 25 h expirada y purgada. |
| F-09 | `json_safe` convertía `datetime`, `Decimal` y `UUID` en `str`; `SELECT *` devolvía UUID en lugar de `UsuarioRef` y columnas sobrantes. | Modelos de respuesta por schema; `UsuarioRef` mediante `JOIN`; columnas explícitas; `float` para áreas; se omiten los nulos que el schema no admite. | `creado_en` en ISO 8601 con `T`; `area_ha` numérico; todas las respuestas validadas contra `Usuario`, `PaginaAlertas`, `CargaAlertas`, `Marca`, `AjustePrioridad`, `EntradaHistorial`, `Trabajo` y `Error`. |
| F-10 | Códigos `HTTP_404` y `DATOS_INVALIDOS`, `Content-Type: application/json`, mensajes de Pydantic en inglés, 404 y 405 de ruta sin el formato del contrato. | `application/problem+json` con `codigo` y `mensaje` del contrato (`NO_ENCONTRADO`, `VALIDACION`, `CORREO_DUPLICADO`, `SOLICITUD_MAL_FORMADA`, `ULTIMA_COORDINACION`, `IDEMPOTENCIA_CONFLICTO`, `ERROR_INTERNO`), mensajes en español y manejador para 404 y 405. | Todos los errores observados cumplen el schema `Error`. |
| F-11 | `CHECK` y FK mapeados a 400; `PATCH {}` respondía 400; un nombre en blanco llegaba a la base; JSON ilegible respondía 422. | 400 para JSON ilegible y parámetros de ruta, query o cabecera inválidos; 422 para cuerpo legible que incumple el esquema; nombre recortado de 1 a 120 caracteres; se retiró el mapeo de `CHECK` y FK, porque la validación lo previene. | Nombre en blanco, de 121 caracteres, valor nulo, rol inválido y campo desconocido: 422 sin modificar la fila; JSON ilegible: 400. |
| F-12 | `PATCH` sin regla de última coordinación, sin `415` y sin cierre de sesiones. | `409 ULTIMA_COORDINACION` (desactivar o quitar el rol), con bloqueo `FOR UPDATE` de las coordinaciones activas; `415` si no es `application/merge-patch+json`; al desactivar se cierran las sesiones abiertas. | 6 rondas de dos bajas simultáneas: una 200 y una 409, siempre queda 1 coordinación activa; 2 sesiones abiertas quedan revocadas. |
| F-13 | `JOIN` interno con `usuarios` y `autor {id, nombre_completo}`. | `LEFT JOIN`; `autor {tipo, id, nombre}`, con `{tipo: sistema, nombre: Sistema}` cuando `autor_id` es nulo. | Primera entrada del historial con autor Sistema; las demás con autor usuario. |
| API-13 (PUT) | El contrato 1.1.0 solo tenía `PATCH /usuarios/{usuarioId}`; la rúbrica exige POST, GET y PUT o DELETE. | `PUT /usuarios/{usuarioId}` (contrato 1.2.0): `nombre_completo`, `rol` y `activo` obligatorios, sin cambiar el correo. Reutiliza `aplicar_cambios` (misma transacción, regla de última coordinación, cierre de sesiones). PATCH se mantiene; no hay DELETE (RF-02-AC-7). Propuesta adoptada para cumplir la actividad, sin aprobación formal de todos los integrantes. | `test_api_usuarios.py`: PUT completo y persistido, 422 por campo faltante, no editable o inválido, 404, 400, 409 `ULTIMA_COORDINACION` (desactivar y quitar el rol), sesiones revocadas y 5 rondas de PUT simultáneos con resultado `[200, 409]`. |

**Observación sobre el contrato (sin modificar):** varios schemas combinan `allOf` con `nullable: true` (p. ej. `AjustePrioridad.nivel_elegido` y `retirado_por`). En OpenAPI 3.0.3 `nullable` solo es efectivo junto a `type`, de modo que un validador estricto rechaza el `null` que el propio contrato exige (`nivel_elegido` es obligatorio y nulo en ajustes por puntaje). Las pruebas lo validaron expandiendo esos schemas. Conviene corregirlo en una versión menor del contrato; requiere decisión del equipo.

### 7.7 Pruebas ejecutadas y pendientes

**Ejecutadas el 25/10/2026 contra PostgreSQL 17.5 y PostGIS 3.5.2 reales:**

| Prueba | Resultado |
|---|---|
| Importación limpia del `esquema_bd.sql` actualizado en una base vacía (`ecoalert_test`) con `ON_ERROR_STOP=1` | 0 errores; 22 tablas del proyecto y 1 auxiliar de PostGIS. |
| Comparación del catálogo (columnas, restricciones, índices y enums) entre esa importación y la base `ecoalert` migrada con `ALTER TABLE` | 396 líneas, idénticas. |
| Integridad SQL (`backend/tests/sql/integridad.sql`, transacción revertida, sin datos persistidos; ejecutada por `pytest` y verificada con `psql`) | 35 de 35: `UNIQUE`, `CHECK`, `FOREIGN KEY`, enum, SRID, índice parcial de ajuste vigente, `ON DELETE RESTRICT`, historial e idempotencia; reproyección, área e intersección con PostGIS. Además, 22 tablas, 22 PK, 32 FK y 3 columnas geométricas en EPSG:32719 en el catálogo. Las tablas quedan con el mismo conteo de filas tras la prueba. |
| Suite `pytest` completa (`backend/tests/`: SQL, contrato, lecturas, usuarios) contra uvicorn real | 76 de 76 en la base existente `ecoalert_test` y 76 de 76 en una base nueva (`ecoalert_limpia_test`) creada, importada con `esquema_bd.sql` y sembrada por la propia suite. Incluye POST, GET, PUT y PATCH con verificación directa en PostgreSQL (hash Argon2 y filas), idempotencia HMAC (cambio solo de contraseña: 422), concurrencia, regla de última coordinación y cierre de sesiones. |
| Contrato (`test_contrato.py`) | OpenAPI 1.2.0 válido; 38 operaciones; PUT presente y sin DELETE de usuarios; 166 criterios Must del SRS cubiertos en `x-acceptance-criteria` y `x-e2e-support`; 62 schemas = 62 clases del UML con los mismos atributos; las 15 rutas del backend están en el contrato. |
| Colección Postman con Newman (`S05_S06_A1/postman/`, entorno `EcoAlert_pruebas`, API en 8001 sobre `ecoalert_test`) | 31 requests (34 solicitudes HTTP con 3 comprobaciones internas), 68 aserciones, 0 fallos; repetida de inmediato sobre la base ya poblada con el mismo resultado. |

La base `ecoalert` (la de la demostración) no recibió filas de prueba. La suite HTTP, la siembra controlada (`semilla.sql`) y las pruebas SQL ahora están versionadas en `backend/tests/` junto con `requirements-test.txt`; las instrucciones para ejecutarlas desde VS Code están en `backend/README.md`. Las cifras de ejecuciones anteriores (32 comprobaciones SQL, 115 HTTP y 23 requests de Postman) correspondían a scripts temporales que no se versionaron y quedan sustituidas por las de esta tabla.

**Pendientes:**

- Las pruebas de la sección 5 (inmutabilidad, vigencia de capas, prioridad, reemplazo atómico de ajustes, geometrías, comparaciones).
- Operaciones no implementadas (23 de 38) y, con ellas, la escritura de marcas, ajustes e historial.
- La colección se ejecutó con Newman; falta correrla en la aplicación de Postman y grabar el video.
- Rendimiento (RNF-04) y seguridad (la entrega no incluye autenticación).
- Criterios abiertos para el equipo: ocultar alertas sin zona o sin área (F-15), tipos y límites menores del esquema (F-17), versión del OpenAPI frente a su historial de cambios (F-20) y la observación sobre `allOf` con `nullable`.
