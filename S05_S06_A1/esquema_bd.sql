-- EcoAlert Tambopata | PostgreSQL 17 + PostGIS 3.5
-- Base: SRS_equipo.md, diagrama_clases_equipo.puml, openapi_equipo.yaml.
-- MODELO DE PERSISTENCIA: el UML consolidado contiene 62 schemas API, muchos de ellos
-- DTOs, enumeraciones, uniones, paginaciones y vistas (no entidades persistentes).
-- Esos tipos NO se convierten artificialmente en tablas. Se persisten sus entidades
-- y asociaciones; la capa FastAPI construye las respuestas del OpenAPI.
-- Extensiones y tipos
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE rol_usuario AS ENUM ('analista_sig', 'coordinacion');
CREATE TYPE tipo_capa AS ENUM ('limite_reserva','zona_amortiguamiento','rios','catastro_minero');
CREATE TYPE estado_zona AS ENUM ('nueva','en_revision','requiere_verificacion','revisada','descartada');
CREATE TYPE nivel_vigente AS ENUM ('alta','media','baja','no_disponible');
CREATE TYPE tipo_factor AS ENUM ('ubicacion','persistencia_crecimiento','cercania_rios','superficie','recencia');

-- Usuarios y sesiones: password_hash nunca se devuelve en el API.
CREATE TABLE usuarios (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 nombre_completo TEXT NOT NULL CHECK (btrim(nombre_completo) <> ''),
 correo TEXT NOT NULL CHECK (position('@' in correo) > 1 AND correo = btrim(correo)),
 rol rol_usuario NOT NULL,
 activo BOOLEAN NOT NULL DEFAULT TRUE,
 debe_cambiar_password BOOLEAN NOT NULL DEFAULT TRUE,
 password_hash TEXT NOT NULL,
 creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX uq_usuarios_correo_ci ON usuarios (lower(correo));
CREATE INDEX ix_usuarios_nombre ON usuarios (lower(nombre_completo));
CREATE INDEX ix_usuarios_rol_activo ON usuarios (rol, activo);

CREATE TABLE sesiones (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
 token_hash TEXT NOT NULL UNIQUE,
 creada_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 ultima_actividad TIMESTAMPTZ NOT NULL DEFAULT now(),
 revocada_en TIMESTAMPTZ,
 CHECK (ultima_actividad >= creada_en),
 CHECK (revocada_en IS NULL OR revocada_en >= creada_en)
);
CREATE INDEX ix_sesiones_usuario_actividad ON sesiones (usuario_id, ultima_actividad DESC);

-- Archivos temporales inspeccionados, con caducidad.
CREATE TABLE archivos_temporales (
 archivo_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 nombre TEXT NOT NULL,
 formato TEXT NOT NULL,
 src_origen TEXT,
 tipo_geometria TEXT,
 num_elementos INTEGER NOT NULL DEFAULT 0 CHECK (num_elementos >= 0),
 columnas JSONB NOT NULL DEFAULT '[]'::jsonb,
 expira_en TIMESTAMPTZ NOT NULL,
 ruta_interna TEXT NOT NULL,
 subido_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT
);
CREATE INDEX ix_archivos_expira ON archivos_temporales(expira_en);

CREATE TABLE capas_referencia (
 tipo tipo_capa PRIMARY KEY,
 nombre TEXT NOT NULL,
 geometria_esperada TEXT NOT NULL,
 atributos_destino JSONB NOT NULL DEFAULT '[]'::jsonb
);
CREATE TABLE versiones_capa (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 tipo tipo_capa NOT NULL REFERENCES capas_referencia(tipo) ON DELETE RESTRICT,
 fuente TEXT NOT NULL,
 fecha_corte DATE NOT NULL,
 cargada_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 cargada_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
 num_elementos INTEGER NOT NULL DEFAULT 0 CHECK (num_elementos >= 0),
 vigente BOOLEAN NOT NULL DEFAULT FALSE,
 archivo_id UUID REFERENCES archivos_temporales(archivo_id) ON DELETE SET NULL,
 mapeo_columnas JSONB,
 UNIQUE (tipo, fuente, fecha_corte)
);
CREATE UNIQUE INDEX uq_version_vigente_por_tipo ON versiones_capa(tipo) WHERE vigente;
CREATE INDEX ix_versiones_tipo_fecha ON versiones_capa(tipo, fecha_corte DESC);

-- Elementos de cada version: geometria UTM 19S en metros para distancias/areas.
-- Los atributos propios del catastro/rios/areas se conservan en JSONB.
CREATE TABLE elementos_capa (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 version_capa_id UUID NOT NULL REFERENCES versiones_capa(id) ON DELETE RESTRICT,
 codigo_origen TEXT,
 nombre TEXT,
 tipo_derecho TEXT,
 estado_derecho TEXT,
 atributos JSONB NOT NULL DEFAULT '{}'::jsonb,
 geometria geometry(Geometry,32719) NOT NULL,
 UNIQUE (version_capa_id, codigo_origen)
);
CREATE INDEX ix_elementos_version ON elementos_capa(version_capa_id);
CREATE INDEX ix_elementos_geom ON elementos_capa USING GIST(geometria);

CREATE TABLE cargas_alertas (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 fuente TEXT NOT NULL CHECK (btrim(fuente) <> ''),
 fecha_corte DATE NOT NULL,
 cargada_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 cargada_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
 archivo_id UUID REFERENCES archivos_temporales(archivo_id) ON DELETE SET NULL,
 mapeo_columnas JSONB,
 alertas_en_archivo INTEGER NOT NULL DEFAULT 0 CHECK (alertas_en_archivo >= 0),
 alertas_nuevas INTEGER NOT NULL DEFAULT 0 CHECK (alertas_nuevas >= 0),
 alertas_existentes INTEGER NOT NULL DEFAULT 0 CHECK (alertas_existentes >= 0),
 alertas_fuera_ambito INTEGER NOT NULL DEFAULT 0 CHECK (alertas_fuera_ambito >= 0),
 alertas_ausentes INTEGER NOT NULL DEFAULT 0 CHECK (alertas_ausentes >= 0),
 zonas_creadas INTEGER NOT NULL DEFAULT 0 CHECK (zonas_creadas >= 0),
 zonas_actualizadas INTEGER NOT NULL DEFAULT 0 CHECK (zonas_actualizadas >= 0),
 resumen TEXT
);
CREATE INDEX ix_cargas_fuente_corte ON cargas_alertas(fuente,fecha_corte DESC);

-- ZonaDetalle y ZonaResumen son proyecciones de una misma entidad: zonas_cambio.
CREATE TABLE zonas_cambio (
 codigo VARCHAR(20) PRIMARY KEY CHECK (codigo ~ '^EA-[0-9]{4}-[0-9]{3}$'),
 estado estado_zona NOT NULL DEFAULT 'nueva',
 creada_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 fecha_ultimo_cambio_estado TIMESTAMPTZ,
 geometria geometry(Geometry,32719) NOT NULL,
 area_ha NUMERIC(18,2) NOT NULL CHECK (area_ha >= 0),
 -- Campos derivados de calculos/ajustes; NULL si aun no disponibles.
 nivel nivel_vigente NOT NULL DEFAULT 'no_disponible',
 puntaje_vigente SMALLINT CHECK (puntaje_vigente BETWEEN 0 AND 100),
 puntaje_texto TEXT
);
CREATE INDEX ix_zonas_geom ON zonas_cambio USING GIST(geometria);
CREATE INDEX ix_zonas_estado_nivel ON zonas_cambio(estado,nivel);
CREATE INDEX ix_zonas_puntaje ON zonas_cambio(puntaje_vigente DESC NULLS LAST);

CREATE TABLE alertas (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 fuente TEXT NOT NULL,
 codigo TEXT NOT NULL,
 fecha_deteccion DATE NOT NULL,
 fecha_ingesta TIMESTAMPTZ NOT NULL DEFAULT now(),
 presente_en_ultima_carga BOOLEAN NOT NULL DEFAULT TRUE,
 zona_codigo VARCHAR(20) REFERENCES zonas_cambio(codigo) ON DELETE RESTRICT,
 area_ha NUMERIC(18,2) CHECK (area_ha >= 0),
 geometria geometry(Geometry,32719) NOT NULL,
 UNIQUE (fuente,codigo)
);
CREATE INDEX ix_alertas_zona_fecha ON alertas(zona_codigo,fecha_deteccion DESC);
CREATE INDEX ix_alertas_fecha ON alertas(fecha_deteccion DESC);
CREATE INDEX ix_alertas_geom ON alertas USING GIST(geometria);
-- Permite documentar cada importacion sin duplicar una alerta ya conocida.
CREATE TABLE carga_alerta_detalle (
 carga_id UUID NOT NULL REFERENCES cargas_alertas(id) ON DELETE RESTRICT,
 alerta_id UUID NOT NULL REFERENCES alertas(id) ON DELETE RESTRICT,
 PRIMARY KEY (carga_id,alerta_id)
);
CREATE INDEX ix_carga_alerta_alerta ON carga_alerta_detalle(alerta_id);

-- Historial de calculos y los cinco factores explicables de cada calculo.
CREATE TABLE prioridades (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 zona_codigo VARCHAR(20) NOT NULL REFERENCES zonas_cambio(codigo) ON DELETE RESTRICT,
 puntaje SMALLINT CHECK (puntaje BETWEEN 0 AND 100),
 nivel nivel_vigente NOT NULL,
 fecha_referencia DATE NOT NULL,
 version_pesos INTEGER NOT NULL CHECK (version_pesos > 0),
 calculado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 texto_desglose TEXT NOT NULL,
 CHECK ((puntaje IS NULL AND nivel = 'no_disponible') OR (puntaje IS NOT NULL AND nivel <> 'no_disponible'))
);
CREATE INDEX ix_prioridades_zona_fecha ON prioridades(zona_codigo,calculado_en DESC);
CREATE TABLE factores_prioridad (
 prioridad_id UUID NOT NULL REFERENCES prioridades(id) ON DELETE RESTRICT,
 factor tipo_factor NOT NULL,
 peso SMALLINT NOT NULL CHECK (peso BETWEEN 0 AND 100),
 disponible BOOLEAN NOT NULL,
 valor_normalizado NUMERIC(12,6) CHECK (valor_normalizado BETWEEN 0 AND 1),
 aporte NUMERIC(12,6),
 aporte_texto TEXT,
 texto_explicativo TEXT NOT NULL,
 CHECK ((disponible AND valor_normalizado IS NOT NULL AND aporte IS NOT NULL) OR
        (NOT disponible AND valor_normalizado IS NULL AND aporte IS NULL)),
 PRIMARY KEY (prioridad_id,factor)
);

CREATE TABLE ajustes_prioridad (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 zona_codigo VARCHAR(20) NOT NULL REFERENCES zonas_cambio(codigo) ON DELETE RESTRICT,
 forma TEXT NOT NULL CHECK (forma IN ('por_puntaje','por_nivel')),
 nivel_elegido nivel_vigente,
 puntaje_ajustado SMALLINT NOT NULL CHECK (puntaje_ajustado BETWEEN 0 AND 100),
 puntaje_calculado_al_ajustar SMALLINT CHECK (puntaje_calculado_al_ajustar BETWEEN 0 AND 100),
 justificacion TEXT NOT NULL CHECK (btrim(justificacion) <> ''),
 estado TEXT NOT NULL DEFAULT 'vigente' CHECK (estado IN ('vigente','reemplazado','retirado')),
 creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 creado_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
 retirado_en TIMESTAMPTZ,
 retirado_por UUID REFERENCES usuarios(id) ON DELETE RESTRICT,
 justificacion_retiro TEXT,
 CHECK ((estado IN ('vigente','reemplazado') AND retirado_en IS NULL AND retirado_por IS NULL AND justificacion_retiro IS NULL)
     OR (estado = 'retirado' AND retirado_en IS NOT NULL AND retirado_por IS NOT NULL
         AND nullif(btrim(justificacion_retiro),'') IS NOT NULL AND retirado_en >= creado_en)),
 CHECK ((forma = 'por_puntaje' AND nivel_elegido IS NULL) OR
        (forma = 'por_nivel' AND nivel_elegido IN ('alta','media','baja')))
);
CREATE UNIQUE INDEX uq_ajuste_vigente_zona ON ajustes_prioridad(zona_codigo) WHERE estado='vigente';
CREATE INDEX ix_ajustes_zona_fecha ON ajustes_prioridad(zona_codigo,creado_en DESC);

CREATE TABLE marcas (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 zona_codigo VARCHAR(20) NOT NULL REFERENCES zonas_cambio(codigo) ON DELETE RESTRICT,
 tipo TEXT NOT NULL CHECK (tipo IN ('area_pequena','posible_dinamica_fluvial','marca_analista')),
 origen TEXT NOT NULL CHECK (origen IN ('automatica','analista')),
 rotulo TEXT,
 texto TEXT NOT NULL,
 activa BOOLEAN NOT NULL DEFAULT TRUE,
 creada_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 creada_por UUID REFERENCES usuarios(id) ON DELETE RESTRICT,
 retirada_en TIMESTAMPTZ,
 retirada_por UUID REFERENCES usuarios(id) ON DELETE RESTRICT,
 motivo_retiro TEXT,
 CHECK ((origen = 'analista' AND tipo = 'marca_analista' AND creada_por IS NOT NULL) OR
        (origen = 'automatica' AND tipo IN ('area_pequena','posible_dinamica_fluvial') AND creada_por IS NULL)),
 CHECK (btrim(texto) <> ''),
 CHECK ((activa AND retirada_en IS NULL AND retirada_por IS NULL AND motivo_retiro IS NULL)
     OR (NOT activa AND retirada_en IS NOT NULL AND retirada_por IS NOT NULL
         AND nullif(btrim(motivo_retiro),'') IS NOT NULL AND retirada_en >= creada_en))
);
CREATE INDEX ix_marcas_zona_activa ON marcas(zona_codigo,activa);

-- Eventos auditables; autor se persiste como FK y puede exponerse como objeto UsuarioRef.
CREATE TABLE entradas_historial (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 zona_codigo VARCHAR(20) NOT NULL REFERENCES zonas_cambio(codigo) ON DELETE RESTRICT,
 tipo_accion TEXT NOT NULL CHECK (btrim(tipo_accion) <> ''),
 fecha_hora TIMESTAMPTZ NOT NULL DEFAULT now(),
 autor_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
 codigo_alerta_origen TEXT,
 estado_anterior estado_zona,
 estado_nuevo estado_zona,
 ajuste_id UUID REFERENCES ajustes_prioridad(id) ON DELETE RESTRICT,
 forma TEXT,
 nivel_elegido nivel_vigente,
 puntaje_calculado SMALLINT CHECK (puntaje_calculado BETWEEN 0 AND 100),
 puntaje_ajustado SMALLINT CHECK (puntaje_ajustado BETWEEN 0 AND 100),
 marca_id UUID REFERENCES marcas(id) ON DELETE RESTRICT,
 texto_marca TEXT,
 texto TEXT
);
CREATE INDEX ix_historial_zona_fecha ON entradas_historial(zona_codigo,fecha_hora DESC);

-- ContextoTerritorial, RioCercano y Superposicion son resultados espaciales derivados.
-- Persistimos un snapshot opcional por zona con fuentes y elementos de referencia.
CREATE TABLE contextos_territoriales (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 zona_codigo VARCHAR(20) NOT NULL REFERENCES zonas_cambio(codigo) ON DELETE RESTRICT,
 calculado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 mensaje_superposiciones TEXT,
 rio_disponible BOOLEAN,
 rio_distancia_m NUMERIC(14,2) CHECK (rio_distancia_m >= 0),
 rio_nombre TEXT,
 rio_texto TEXT,
 rio_fecha_corte DATE,
 rio_mensaje TEXT
);
CREATE INDEX ix_contextos_zona_fecha ON contextos_territoriales(zona_codigo,calculado_en DESC);
CREATE TABLE superposiciones (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 contexto_id UUID NOT NULL REFERENCES contextos_territoriales(id) ON DELETE RESTRICT,
 elemento_capa_id UUID REFERENCES elementos_capa(id) ON DELETE RESTRICT,
 clase TEXT NOT NULL CHECK (clase IN ('area','minera')),
 capa TEXT NOT NULL,
 codigo TEXT,
 nombre TEXT,
 tipo_derecho TEXT,
 estado TEXT,
 fecha_corte DATE
);
CREATE INDEX ix_superposiciones_contexto ON superposiciones(contexto_id);

-- AnalisisResumen y Analisis representan el mismo analisis; periodos A/B como columnas.
CREATE TABLE analisis (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 ejecutado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 ejecutado_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
 periodo_a_inicio DATE NOT NULL,
 periodo_a_fin DATE NOT NULL,
 periodo_b_inicio DATE NOT NULL,
 periodo_b_fin DATE NOT NULL,
 estado TEXT NOT NULL CHECK (estado IN ('concluido','incompleto','sin_datos')),
 mensaje TEXT,
 limitaciones JSONB NOT NULL DEFAULT '[]'::jsonb,
 CHECK (periodo_a_inicio <= periodo_a_fin),
 CHECK (periodo_b_inicio <= periodo_b_fin),
 CHECK (periodo_a_fin < periodo_b_inicio),
 CHECK (jsonb_typeof(limitaciones) = 'array')
);
CREATE INDEX ix_analisis_fecha ON analisis(ejecutado_en DESC);
CREATE INDEX ix_analisis_usuario_fecha ON analisis(ejecutado_por,ejecutado_en DESC);

-- FuenteUsada se asocia a calculos, contextos o analisis (sin polimorfismo FK).
CREATE TABLE fuentes_usadas (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 capa TEXT NOT NULL,
 fuente TEXT NOT NULL,
 fecha_corte DATE NOT NULL,
 analisis_id UUID REFERENCES analisis(id) ON DELETE RESTRICT,
 prioridad_id UUID REFERENCES prioridades(id) ON DELETE RESTRICT,
 contexto_id UUID REFERENCES contextos_territoriales(id) ON DELETE RESTRICT,
 CHECK (num_nonnulls(analisis_id,prioridad_id,contexto_id) = 1)
);
CREATE INDEX ix_fuentes_analisis ON fuentes_usadas(analisis_id);
CREATE INDEX ix_fuentes_prioridad ON fuentes_usadas(prioridad_id);
CREATE INDEX ix_fuentes_contexto ON fuentes_usadas(contexto_id);

-- Snapshot inmutable de resultados, independiente de cambios futuros en zonas.
CREATE TABLE resultados_zona (
 analisis_id UUID NOT NULL REFERENCES analisis(id) ON DELETE RESTRICT,
 codigo_zona VARCHAR(20) NOT NULL REFERENCES zonas_cambio(codigo) ON DELETE RESTRICT,
 alertas_a INTEGER NOT NULL CHECK (alertas_a >= 0),
 alertas_b INTEGER NOT NULL CHECK (alertas_b >= 0),
 area_a_ha NUMERIC(18,2) NOT NULL CHECK (area_a_ha >= 0),
 area_b_ha NUMERIC(18,2) NOT NULL CHECK (area_b_ha >= 0),
 diferencia_ha NUMERIC(18,2) NOT NULL,
 presencia TEXT NOT NULL CHECK (presencia IN ('solo_a','solo_b','en_ambos')),
 nivel nivel_vigente NOT NULL,
 puntaje SMALLINT CHECK (puntaje BETWEEN 0 AND 100),
 estado estado_zona NOT NULL,
 PRIMARY KEY (analisis_id,codigo_zona)
);
CREATE INDEX ix_resultados_codigo ON resultados_zona(codigo_zona);

-- Cola sencilla de trabajos asíncronos: el worker consulta esta tabla.
CREATE TABLE trabajos (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 tipo TEXT NOT NULL CHECK (tipo IN ('carga_capa','ingesta_alertas')),
 estado TEXT NOT NULL CHECK (estado IN ('pendiente','en_proceso','completado','fallido')),
 creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
 mensaje_estado TEXT,
 resultado JSONB,
 error JSONB,
 CHECK (actualizado_en >= creado_en),
 CHECK (estado <> 'fallido' OR error IS NOT NULL)
);
CREATE INDEX ix_trabajos_estado_fecha ON trabajos(estado,creado_en);

-- Vistas/DTOs OpenAPI NO son tablas independientes:
-- UsuarioRef, CredencialesLogin, SesionCreada, SesionActual, CambioPassword,
-- UsuarioCrear, UsuarioActualizar, InspeccionArchivo (archivos_temporales),
-- AtributoDestino (JSONB en capas_referencia), CargaVersionCapa,
-- CargaAlertasSolicitud, PaginaAlertas, CapaMapa, Geometria, Feature,
-- FeatureCollection, ZonaResumen, ConteosZonas, ListaZonas, ZonaDetalle,
-- AjusteVigente, CambioEstadoSolicitud, AjusteSolicitud, AjustePorPuntaje,
-- AjustePorNivel, RetiroAjusteSolicitud, MarcaResumen, MarcaAnalistaSolicitud,
-- RetiroMarcaSolicitud, ComparacionSolicitud, Periodo (columnas A/B),
-- AnalisisResumen, ListaAnalisis, Error, Pagina, SuperposicionArea,
-- SuperposicionMinera, RioCercano. Enumeraciones y CodigoZona son tipos/valores.
-- Inmutabilidad de historiales y snapshots debe reforzarse con permisos SQL
-- o triggers y validarse en el backend; no se implementa aqui un bloqueo global
-- que impida cerrar un analisis mientras se insertan sus resultados.
-- Regla de negocio: fecha_corte mas reciente = version vigente; se implementa
-- transaccionalmente desde FastAPI/worker, apoyada por uq_version_vigente_por_tipo.
-- Regla de negocio: expiracion de sesion tras 30 min sin actividad, validada por API.

-- Validaciones cruzadas no expresables con CHECK de una sola fila:
-- 1. Prioridad: cinco factores distintos, suma de pesos y umbrales de nivel.
-- 2. Version vigente: la fecha_corte maxima, gestionada transaccionalmente.
-- 3. Inmutabilidad de resultados_zona/entradas_historial: aplicar permisos o triggers.
-- 4. Referencias a la misma zona entre entradas_historial, ajuste_id y marca_id.
-- 5. Reemplazo de ajustes: cerrar vigente previo y abrir nuevo en transaccion.
-- 6. Fecha de deteccion, union espacial, distancia <=500 m / <=90 dias: backend/PostGIS.
