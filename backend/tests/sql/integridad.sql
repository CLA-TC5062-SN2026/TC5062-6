-- Pruebas de integridad del esquema EcoAlert (PostgreSQL 17 + PostGIS 3.5).
-- SQL puro: se ejecuta dentro de una transaccion que se revierte, asi que no deja datos.
-- Resultado: una fila PASS/FAIL por prueba. Ejecucion: pytest (tests/test_integridad_sql.py) o
--   docker exec -i ecoalert_db psql -U ecoalert -d ecoalert_test -v ON_ERROR_STOP=1 < tests/sql/integridad.sql
-- Los identificadores (EA-2099-*, ffffffff-...) no chocan con tests/sql/semilla.sql.
BEGIN;

CREATE TEMP TABLE resultado_pruebas (n serial, estado text, prueba text, detalle text);

CREATE FUNCTION pg_temp.ok(p_prueba text, p_sql text) RETURNS void LANGUAGE plpgsql AS $f$
BEGIN
  EXECUTE p_sql;
  INSERT INTO resultado_pruebas(estado, prueba) VALUES ('PASS', p_prueba);
EXCEPTION WHEN OTHERS THEN
  INSERT INTO resultado_pruebas(estado, prueba, detalle) VALUES ('FAIL', p_prueba, SQLSTATE || ' ' || SQLERRM);
END $f$;

CREATE FUNCTION pg_temp.rechaza(p_prueba text, p_sql text, p_sqlstate text) RETURNS void LANGUAGE plpgsql AS $f$
BEGIN
  EXECUTE p_sql;
  INSERT INTO resultado_pruebas(estado, prueba, detalle) VALUES ('FAIL', p_prueba, 'no hubo error; se esperaba ' || p_sqlstate);
EXCEPTION WHEN OTHERS THEN
  IF p_sqlstate = '*' OR SQLSTATE = p_sqlstate THEN
    INSERT INTO resultado_pruebas(estado, prueba, detalle) VALUES ('PASS', p_prueba, 'SQLSTATE ' || SQLSTATE);
  ELSE
    INSERT INTO resultado_pruebas(estado, prueba, detalle) VALUES ('FAIL', p_prueba, SQLSTATE || ' (esperado ' || p_sqlstate || ') ' || SQLERRM);
  END IF;
END $f$;

CREATE FUNCTION pg_temp.valor(p_prueba text, p_sql text, p_esperado text) RETURNS void LANGUAGE plpgsql AS $f$
DECLARE v text;
BEGIN
  EXECUTE p_sql INTO v;
  IF v IS NOT DISTINCT FROM p_esperado THEN
    INSERT INTO resultado_pruebas(estado, prueba) VALUES ('PASS', p_prueba);
  ELSE
    INSERT INTO resultado_pruebas(estado, prueba, detalle) VALUES ('FAIL', p_prueba, 'obtenido ' || coalesce(v, 'NULL') || ', esperado ' || p_esperado);
  END IF;
EXCEPTION WHEN OTHERS THEN
  INSERT INTO resultado_pruebas(estado, prueba, detalle) VALUES ('FAIL', p_prueba, SQLSTATE || ' ' || SQLERRM);
END $f$;

DO $$
BEGIN
  -- PostGIS
  PERFORM pg_temp.valor('PostGIS: reproyeccion EPSG:4326 a 32719', $q$SELECT ST_AsText(ST_SnapToGrid(ST_Transform(ST_SetSRID(ST_MakePoint(-69.60,-12.80),4326),32719),1))$q$, 'POINT(434882 8584906)');
  PERFORM pg_temp.valor('PostGIS: area de un cuadrado de 100 m = 1.00 ha', $q$SELECT round((ST_Area(ST_GeomFromText('POLYGON((500000 8580000,500100 8580000,500100 8580100,500000 8580100,500000 8580000))',32719))/10000.0)::numeric,2)::text$q$, '1.00');

  -- usuarios
  PERFORM pg_temp.ok('usuarios: insert valido', $q$INSERT INTO usuarios(id,nombre_completo,correo,rol,password_hash) VALUES ('ffffffff-ffff-4fff-8fff-ffffffffff01','Prueba Integridad','integridad.p0@ecoalert.pe','analista_sig','hash-de-prueba-no-valido')$q$);
  PERFORM pg_temp.rechaza('usuarios: correo duplicado sin distinguir mayusculas', $q$INSERT INTO usuarios(nombre_completo,correo,rol,password_hash) VALUES ('Otra','INTEGRIDAD.P0@ECOALERT.PE','analista_sig','x')$q$, '23505');
  PERFORM pg_temp.rechaza('usuarios: rol fuera del enum', $q$INSERT INTO usuarios(nombre_completo,correo,rol,password_hash) VALUES ('Otra','integridad.otra@ecoalert.pe','superadmin','x')$q$, '22P02');
  PERFORM pg_temp.rechaza('usuarios: nombre solo espacios', $q$INSERT INTO usuarios(nombre_completo,correo,rol,password_hash) VALUES ('   ','integridad.otra@ecoalert.pe','analista_sig','x')$q$, '23514');
  PERFORM pg_temp.rechaza('usuarios: correo sin arroba', $q$INSERT INTO usuarios(nombre_completo,correo,rol,password_hash) VALUES ('Otra','sinarroba','analista_sig','x')$q$, '23514');

  -- zonas y alertas
  PERFORM pg_temp.ok('zonas_cambio: insert valido (geometria SRID 32719)', $q$INSERT INTO zonas_cambio(codigo,geometria,area_ha) VALUES ('EA-2099-001', ST_GeomFromText('POLYGON((600000 8680000,600100 8680000,600100 8680100,600000 8680100,600000 8680000))',32719), 1.00)$q$);
  PERFORM pg_temp.rechaza('zonas_cambio: codigo con formato invalido', $q$INSERT INTO zonas_cambio(codigo,geometria,area_ha) VALUES ('EA-2099-1', ST_GeomFromText('POINT(600000 8680000)',32719), 1.00)$q$, '23514');
  PERFORM pg_temp.rechaza('zonas_cambio: geometria SRID 4326 en columna 32719', $q$INSERT INTO zonas_cambio(codigo,geometria,area_ha) VALUES ('EA-2099-002', ST_GeomFromText('POLYGON((-69.6 -12.8,-69.5 -12.8,-69.5 -12.7,-69.6 -12.7,-69.6 -12.8))',4326), 1.00)$q$, '*');
  PERFORM pg_temp.rechaza('alertas: zona inexistente (FK)', $q$INSERT INTO alertas(fuente,codigo,fecha_deteccion,zona_codigo,area_ha,geometria) VALUES ('INT','INT-0',DATE '2026-09-01','EA-2098-999',0.16,ST_GeomFromText('POINT(600010 8680010)',32719))$q$, '23503');
  PERFORM pg_temp.ok('alertas: insert valido', $q$INSERT INTO alertas(fuente,codigo,fecha_deteccion,zona_codigo,area_ha,geometria) VALUES ('INT','INT-1',DATE '2026-09-01','EA-2099-001',0.16,ST_GeomFromText('POLYGON((600010 8680010,600050 8680010,600050 8680050,600010 8680050,600010 8680010))',32719))$q$);
  PERFORM pg_temp.rechaza('alertas: (fuente,codigo) duplicado', $q$INSERT INTO alertas(fuente,codigo,fecha_deteccion,zona_codigo,area_ha,geometria) VALUES ('INT','INT-1',DATE '2026-09-02','EA-2099-001',0.16,ST_GeomFromText('POINT(600020 8680020)',32719))$q$, '23505');
  PERFORM pg_temp.valor('PostGIS: la alerta intersecta su zona (consulta espacial con GiST)', $q$SELECT count(*)::text FROM zonas_cambio z JOIN alertas a ON ST_Intersects(z.geometria, a.geometria) WHERE z.codigo = 'EA-2099-001'$q$, '1');

  -- ajustes de prioridad
  PERFORM pg_temp.ok('ajustes_prioridad: primer ajuste vigente (por_puntaje)', $q$INSERT INTO ajustes_prioridad(zona_codigo,forma,puntaje_ajustado,justificacion,creado_por) VALUES ('EA-2099-001','por_puntaje',80,'prueba','ffffffff-ffff-4fff-8fff-ffffffffff01')$q$);
  PERFORM pg_temp.rechaza('ajustes_prioridad: segundo ajuste vigente en la misma zona (indice parcial)', $q$INSERT INTO ajustes_prioridad(zona_codigo,forma,puntaje_ajustado,justificacion,creado_por) VALUES ('EA-2099-001','por_puntaje',50,'otra','ffffffff-ffff-4fff-8fff-ffffffffff01')$q$, '23505');
  PERFORM pg_temp.rechaza('ajustes_prioridad: por_nivel con nivel_elegido NULL (hallazgo H-1)', $q$INSERT INTO ajustes_prioridad(zona_codigo,forma,nivel_elegido,puntaje_ajustado,justificacion,estado,creado_por,retirado_en,retirado_por,justificacion_retiro) VALUES ('EA-2099-001','por_nivel',NULL,50,'x','retirado','ffffffff-ffff-4fff-8fff-ffffffffff01',now(),'ffffffff-ffff-4fff-8fff-ffffffffff01','x')$q$, '23514');
  PERFORM pg_temp.ok('ajustes_prioridad: por_nivel con nivel_elegido alta (valido)', $q$INSERT INTO ajustes_prioridad(zona_codigo,forma,nivel_elegido,puntaje_ajustado,justificacion,estado,creado_por,retirado_en,retirado_por,justificacion_retiro) VALUES ('EA-2099-001','por_nivel','alta',70,'x','retirado','ffffffff-ffff-4fff-8fff-ffffffffff01',now(),'ffffffff-ffff-4fff-8fff-ffffffffff01','x')$q$);
  PERFORM pg_temp.rechaza('ajustes_prioridad: por_nivel con no_disponible', $q$INSERT INTO ajustes_prioridad(zona_codigo,forma,nivel_elegido,puntaje_ajustado,justificacion,estado,creado_por,retirado_en,retirado_por,justificacion_retiro) VALUES ('EA-2099-001','por_nivel','no_disponible',50,'x','retirado','ffffffff-ffff-4fff-8fff-ffffffffff01',now(),'ffffffff-ffff-4fff-8fff-ffffffffff01','x')$q$, '23514');
  PERFORM pg_temp.rechaza('ajustes_prioridad: por_puntaje con nivel_elegido alta', $q$INSERT INTO ajustes_prioridad(zona_codigo,forma,nivel_elegido,puntaje_ajustado,justificacion,estado,creado_por,retirado_en,retirado_por,justificacion_retiro) VALUES ('EA-2099-001','por_puntaje','alta',70,'x','retirado','ffffffff-ffff-4fff-8fff-ffffffffff01',now(),'ffffffff-ffff-4fff-8fff-ffffffffff01','x')$q$, '23514');
  PERFORM pg_temp.rechaza('ajustes_prioridad: puntaje 101', $q$INSERT INTO ajustes_prioridad(zona_codigo,forma,puntaje_ajustado,justificacion,estado,creado_por,retirado_en,retirado_por,justificacion_retiro) VALUES ('EA-2099-001','por_puntaje',101,'x','retirado','ffffffff-ffff-4fff-8fff-ffffffffff01',now(),'ffffffff-ffff-4fff-8fff-ffffffffff01','x')$q$, '23514');

  -- marcas, referencias, trabajos y analisis
  PERFORM pg_temp.rechaza('marcas: origen analista con tipo automatico', $q$INSERT INTO marcas(zona_codigo,tipo,origen,texto,creada_por) VALUES ('EA-2099-001','area_pequena','analista','x','ffffffff-ffff-4fff-8fff-ffffffffff01')$q$, '23514');
  PERFORM pg_temp.rechaza('usuarios: borrar un usuario referenciado (ON DELETE RESTRICT)', $q$DELETE FROM usuarios WHERE id='ffffffff-ffff-4fff-8fff-ffffffffff01'$q$, '23503');
  PERFORM pg_temp.rechaza('trabajos: estado fallido sin error', $q$INSERT INTO trabajos(tipo,estado) VALUES ('ingesta_alertas','fallido')$q$, '23514');
  PERFORM pg_temp.rechaza('analisis: periodos superpuestos', $q$INSERT INTO analisis(ejecutado_por,periodo_a_inicio,periodo_a_fin,periodo_b_inicio,periodo_b_fin,estado) VALUES ('ffffffff-ffff-4fff-8fff-ffffffffff01','2026-06-01','2026-06-30','2026-06-15','2026-07-15','concluido')$q$, '23514');

  -- historial (autor Sistema y enumeraciones)
  PERFORM pg_temp.ok('historial: zona_creada sin autor (Sistema)', $q$INSERT INTO entradas_historial(zona_codigo,tipo_accion,codigo_alerta_origen) VALUES ('EA-2099-001','zona_creada','INT-1')$q$);
  PERFORM pg_temp.ok('historial: cambio_estado con autor usuario', $q$INSERT INTO entradas_historial(zona_codigo,tipo_accion,autor_id,estado_anterior,estado_nuevo) VALUES ('EA-2099-001','cambio_estado','ffffffff-ffff-4fff-8fff-ffffffffff01','nueva','en_revision')$q$);
  PERFORM pg_temp.rechaza('historial: cambio_estado SIN autor', $q$INSERT INTO entradas_historial(zona_codigo,tipo_accion,estado_anterior,estado_nuevo) VALUES ('EA-2099-001','cambio_estado','nueva','en_revision')$q$, '23514');
  PERFORM pg_temp.rechaza('historial: tipo_accion fuera de los 6 valores', $q$INSERT INTO entradas_historial(zona_codigo,tipo_accion,autor_id) VALUES ('EA-2099-001','otra_accion','ffffffff-ffff-4fff-8fff-ffffffffff01')$q$, '23514');
  PERFORM pg_temp.rechaza('historial: tipo_accion vacio', $q$INSERT INTO entradas_historial(zona_codigo,tipo_accion,autor_id) VALUES ('EA-2099-001','','ffffffff-ffff-4fff-8fff-ffffffffff01')$q$, '23514');
  PERFORM pg_temp.rechaza('historial: forma invalida', $q$INSERT INTO entradas_historial(zona_codigo,tipo_accion,autor_id,forma) VALUES ('EA-2099-001','ajuste_fijado','ffffffff-ffff-4fff-8fff-ffffffffff01','por_otra')$q$, '23514');
  PERFORM pg_temp.ok('historial: ajuste_fijado por_nivel', $q$INSERT INTO entradas_historial(zona_codigo,tipo_accion,autor_id,forma,nivel_elegido,puntaje_ajustado) VALUES ('EA-2099-001','ajuste_fijado','ffffffff-ffff-4fff-8fff-ffffffffff01','por_nivel','alta',70)$q$);

  -- idempotencia
  PERFORM pg_temp.ok('claves_idempotencia: insert valido', $q$INSERT INTO claves_idempotencia(clave,operacion,huella,estado_http,cuerpo_respuesta,location) VALUES ('11111111-1111-4111-8111-111111111111','crearUsuario','abc',201,'{"id":"x"}','/api/v1/usuarios/x')$q$);
  PERFORM pg_temp.rechaza('claves_idempotencia: clave repetida', $q$INSERT INTO claves_idempotencia(clave,operacion,huella,estado_http,cuerpo_respuesta,location) VALUES ('11111111-1111-4111-8111-111111111111','crearUsuario','abc',201,'{}','/x')$q$, '23505');
  PERFORM pg_temp.rechaza('claves_idempotencia: estado_http 500 (solo se guardan 2xx)', $q$INSERT INTO claves_idempotencia(clave,operacion,huella,estado_http,cuerpo_respuesta,location) VALUES ('22222222-2222-4222-8222-222222222222','crearUsuario','abc',500,'{}','/x')$q$, '23514');
END $$;

SELECT estado, prueba, coalesce(detalle, '') AS detalle FROM resultado_pruebas ORDER BY n;

ROLLBACK;
