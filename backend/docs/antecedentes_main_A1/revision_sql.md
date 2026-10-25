# Revisión del esquema SQL — EcoAlert Tambopata

**Artefacto revisado:** `esquema_bd.sql`  
**Referencias:** `diagrama_clases_equipo.puml`, `openapi_equipo.yaml` y SRS del equipo.  
**Motor:** PostgreSQL 17 + PostGIS.  
**Resultado:** se corrigió el SQL original **antes de ejecutarlo** y después se importó en PostgreSQL 17.5 + PostGIS 3.5.2 **sin errores** (sección 7). Las correcciones al código de servicios están en la sección 8.

## 1. Criterio de correspondencia con el diagrama

El diagrama consolidado representa **62 schemas OpenAPI** (entidades, DTO de solicitudes y respuestas, enumeraciones, vistas y tipos auxiliares). Por tanto, **no corresponde crear 62 tablas**: `UsuarioCrear`, `ZonaResumen`, `FeatureCollection`, `ListaZonas` o `AjusteSolicitud`, por ejemplo, son contratos de intercambio y no entidades con ciclo de vida independiente.

El SQL revisado incluye **21 tablas** de persistencia: `usuarios`, `sesiones`, `archivos_temporales`, `capas_referencia`, `versiones_capa`, `elementos_capa`, `cargas_alertas`, `zonas_cambio`, `alertas`, `carga_alerta_detalle`, `prioridades`, `factores_prioridad`, `ajustes_prioridad`, `marcas`, `entradas_historial`, `contextos_territoriales`, `superposiciones`, `analisis`, `fuentes_usadas`, `resultados_zona` y `trabajos`.

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

**Estado: revisado, corregido e importado sin errores (sección 7).** El esquema representa las entidades persistentes principales y las asociaciones del dominio sin transformar indiscriminadamente todos los DTO del diagrama en tablas. Se corrigieron incompatibilidades concretas con enumeraciones, patrones y reglas de negocio del OpenAPI. Antes de utilizarlo como esquema definitivo de producción deben realizarse las pruebas de integridad indicadas en la sección 5; especialmente, reforzar la inmutabilidad y las restricciones cruzadas.

## 7. Importación del esquema y verificación de tablas

**Entorno:** imagen `postgis/postgis:17-3.5` (PostgreSQL 17.5, PostGIS 3.5.2) levantada con `backend/docker-compose.yml`, que monta `esquema_bd.sql` en `/docker-entrypoint-initdb.d/`. Fecha: 24/10/2026.

**Resultado:** el script se ejecutó completo **sin errores** (el log del contenedor no registra ningún `ERROR`). `\dt` muestra las **21 tablas** del esquema; `spatial_ref_sys` es la tabla de sistemas de referencia que crea PostGIS.

```
ecoalert=# \dt public.*
 public | ajustes_prioridad       | table | ecoalert
 public | alertas                 | table | ecoalert
 public | analisis                | table | ecoalert
 public | archivos_temporales     | table | ecoalert
 public | capas_referencia        | table | ecoalert
 public | carga_alerta_detalle    | table | ecoalert
 public | cargas_alertas          | table | ecoalert
 public | contextos_territoriales | table | ecoalert
 public | elementos_capa          | table | ecoalert
 public | entradas_historial      | table | ecoalert
 public | factores_prioridad      | table | ecoalert
 public | fuentes_usadas          | table | ecoalert
 public | marcas                  | table | ecoalert
 public | prioridades             | table | ecoalert
 public | resultados_zona         | table | ecoalert
 public | sesiones                | table | ecoalert
 public | superposiciones         | table | ecoalert
 public | trabajos                | table | ecoalert
 public | usuarios                | table | ecoalert
 public | versiones_capa          | table | ecoalert
 public | zonas_cambio            | table | ecoalert
```

Restricciones creadas (`pg_constraint`, esquema `public`): **21 PRIMARY KEY, 32 FOREIGN KEY, 4 UNIQUE y 57 CHECK**, más **56 índices** (`pg_indexes`), entre ellos el índice único `uq_usuarios_correo_ci` sobre `lower(correo)` y los índices GIST de las geometrías.

Para reproducirlo: `cd backend && cp .env.example .env && docker compose --env-file .env up -d`, y luego `docker exec ecoalert_db psql -U ecoalert -d ecoalert -c '\dt'`.

## 8. Correcciones al código generado

**Código revisado:** `backend/app/main.py` generado por el agente en S05-S06-A1 (commit `9f5070d`), contrastado contra `openapi_equipo.yaml` (rutas, métodos, códigos y schemas).

**Ejecución:** el servidor se levantó con `uvicorn` contra la base de la sección 7 y la conexión funcionó (`GET /salud` → `{"estado":"ok","base_datos":true}`). Resultados de las operaciones probadas:

| Operación | Esperado (contrato) | Obtenido | ¿Coincide? |
|---|---|---|---|
| `POST /usuarios` | 201 + `Usuario` | 201, sin contraseña ni hash en la respuesta | ✅ |
| `GET /usuarios/{usuarioId}` | 200 + `Usuario` | 200 | ✅ |
| `PATCH /usuarios/{usuarioId}` | 200 + `Usuario` | 200, cambia solo el campo enviado | ✅ |
| `POST /usuarios` con correo repetido | 409 | 409 | ✅ |
| `GET /usuarios/{id}` inexistente | 404 | 404 | ✅ |
| `GET /alertas` | 200 + `PaginaAlertas` | 200, pero con un arreglo | ❌ (ver C-12) |
| `DELETE /usuarios/{usuarioId}` | 405, la cuenta sigue existiendo (RF-02-AC-7) | 405 | ✅ (formato de error, ver C-03) |

No hubo errores 500 durante la ejecución.

### 8.1 Divergencias corregidas

Corregidas en el backend durante S05-S06-A2 (commit `32bc06b`), con pruebas automatizadas en `backend/tests/`:

| ID | Divergencia con el contrato | Código generado | Corrección |
|---|---|---|---|
| C-01 | `servers` declara el prefijo `/api/v1` | Rutas en la raíz (`/usuarios`) | Todas las rutas bajo `/api/v1` |
| C-02 | `UsuarioCrear.password_temporal` con `minLength: 12` (PS-15, RF-02-AC-3) | Aceptaba 8 caracteres | Mínimo 12 y máximo 72 bytes (límite de bcrypt) |
| C-03 | Errores `application/problem+json` con códigos estables (`NO_ENCONTRADO`, `VALIDACION`, `CORREO_DUPLICADO`) | `application/json` con `HTTP_404`, `DATOS_INVALIDOS`, `Recurso duplicado`; los 404 y 405 del framework salían como `{"detail": ...}` | Manejadores RFC 9457 para todos los errores, con los códigos del contrato |
| C-04 | Respuestas 201 con cabecera `Location` | No se enviaba | `Location: /api/v1/usuarios/{id}` |
| C-05 | `format: date-time` (RFC 3339) | `str(datetime)` producía `2026-10-25 05:29:40+00:00` | `isoformat()`: `2026-10-25T05:29:40+00:00` |
| C-06 | `PATCH` con cuerpo vacío → 422 | 400 | 422 `VALIDACION` |
| C-07 | `nombre_completo` con `maxLength: 120` | Sin límite | `max_length=120` |
| C-08 | `PATCH` responde 409 si deja sin cuentas activas de Coordinación (RF-02-AC-8) y cierra sesiones al desactivar | No se validaba | Transacción con `FOR UPDATE` y revocación de sesiones |
| C-09 | Conexión por variables de entorno documentadas en `.env.example` | El archivo no existía y `DATABASE_URL` tenía credenciales por defecto en el código | `.env.example` creado; `DATABASE_URL` obligatoria y sin valor por defecto |
| C-10 | 401/403 en las rutas protegidas | Sin autenticación (fuera del alcance de S05-S06-A1 por instrucción) | Implementado en S05-S06-A2 (ver `S05_S06_A2/revision_seguridad.md`) |

### 8.2 Divergencias pendientes

Siguen abiertas en el código actual y deben resolverse antes de dar por cumplido el contrato:

| ID | Divergencia | Situación actual |
|---|---|---|
| C-11 | `POST /usuarios` exige `Idempotency-Key` | La cabecera no se valida ni se almacena |
| C-12 | `GET /alertas` devuelve `PaginaAlertas` (`alertas`, `total`, `limite`, `desplazamiento`) y acepta los filtros `zona` y `presente_en_ultima_carga` | Devuelve un arreglo sin paginación ni filtros |
| C-13 | `cargada_por` (`CargaAlertas`), `creado_por`/`retirado_por` (`AjustePrioridad`) y `creada_por`/`retirada_por` (`Marca`) son objetos `UsuarioRef` | Se devuelven como UUID; marcas y ajustes usan `SELECT *` y exponen además la columna interna `zona_codigo` |
| C-14 | `PATCH /usuarios/{usuarioId}` exige `Content-Type: application/merge-patch+json` (415 si no) | Acepta también `application/json` |
