# Revisión del esquema SQL — EcoAlert Tambopata

**Artefacto revisado:** `esquema_bd.sql`  
**Referencias:** `diagrama_clases_equipo.puml`, `openapi_equipo.yaml` y SRS del equipo.  
**Motor:** PostgreSQL 17 + PostGIS.  
**Resultado:** se corrigió el SQL original **antes de ejecutarlo**. No se realizó ejecución en PostgreSQL/PostGIS; la validación aquí es estática.

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

**Estado: revisado y corregido estáticamente; pendiente de prueba de ejecución.** El esquema representa las entidades persistentes principales y las asociaciones del dominio sin transformar indiscriminadamente todos los DTO del diagrama en tablas. Se corrigieron incompatibilidades concretas con enumeraciones, patrones y reglas de negocio del OpenAPI. Antes de utilizarlo como esquema definitivo de producción, deben realizarse la ejecución real en PostgreSQL/PostGIS y las pruebas de integridad indicadas; especialmente, reforzar la inmutabilidad y las restricciones cruzadas.
