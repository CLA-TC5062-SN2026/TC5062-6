-- Datos de prueba controlados para las pruebas HTTP de lectura (backend/tests).
-- Idempotente: cada INSERT usa ON CONFLICT DO NOTHING, por lo que puede cargarse varias veces
-- y nunca modifica ni borra filas existentes. Solo se carga en bases cuyo nombre termina en _test.
-- Sin credenciales: password_hash es un texto que no corresponde a ninguna contrasena.

INSERT INTO usuarios (id, nombre_completo, correo, rol, activo, debe_cambiar_password, password_hash, creado_en) VALUES
 ('00000000-0000-4000-8000-000000000001', 'Ana Quispe Mamani', 'seed.ana@ecoalert.pe',  'analista_sig', true,  false, 'hash-de-prueba-no-valido', '2026-09-01 08:00:00+00'),
 ('00000000-0000-4000-8000-000000000002', 'Luis Condori',       'seed.luis@ecoalert.pe', 'coordinacion', false, false, 'hash-de-prueba-no-valido', '2026-09-01 08:05:00+00')
ON CONFLICT DO NOTHING;

INSERT INTO zonas_cambio (codigo, estado, creada_en, geometria, area_ha, nivel, puntaje_vigente) VALUES
 ('EA-2026-001', 'nueva', '2026-09-05 10:00:00+00', ST_GeomFromText('POLYGON((500000 8580000,500100 8580000,500100 8580100,500000 8580100,500000 8580000))', 32719), 2.00, 'alta', 75),
 ('EA-2026-002', 'nueva', '2026-09-16 10:00:00+00', ST_GeomFromText('POLYGON((501000 8580000,501050 8580000,501050 8580050,501000 8580050,501000 8580000))', 32719), 0.80, 'baja', 20)
ON CONFLICT DO NOTHING;

INSERT INTO alertas (fuente, codigo, fecha_deteccion, presente_en_ultima_carga, zona_codigo, area_ha, geometria) VALUES
 ('GeoBosques', 'A-1',      '2026-09-01', true,  'EA-2026-001', 1.20, ST_GeomFromText('POINT(500010 8580010)', 32719)),
 ('GeoBosques', 'A-2',      '2026-09-10', true,  'EA-2026-001', 0.80, ST_GeomFromText('POINT(500020 8580020)', 32719)),
 ('GeoBosques', 'A-3',      '2026-09-20', false, 'EA-2026-001', 0.00, ST_GeomFromText('POINT(500030 8580030)', 32719)),
 ('GeoBosques', 'B-1',      '2026-09-15', true,  'EA-2026-002', 0.80, ST_GeomFromText('POINT(501010 8580010)', 32719)),
 ('GeoBosques', 'SIN-AREA', '2026-09-26', true,  'EA-2026-001', NULL, ST_GeomFromText('POINT(500040 8580040)', 32719)),
 ('GeoBosques', 'SIN-ZONA', '2026-09-25', true,  NULL,          0.50, ST_GeomFromText('POINT(502000 8580000)', 32719))
ON CONFLICT DO NOTHING;

INSERT INTO cargas_alertas (id, fuente, fecha_corte, cargada_en, cargada_por, alertas_en_archivo, alertas_nuevas, alertas_existentes, alertas_fuera_ambito, alertas_ausentes, zonas_creadas, zonas_actualizadas, resumen) VALUES
 ('20000000-0000-4000-8000-000000000001', 'GeoBosques', '2026-09-20', '2026-09-22 10:15:00+00', '00000000-0000-4000-8000-000000000001', 120, 115, 0, 5, 0, 14, 0, '115 alertas nuevas, 0 ya existentes, 5 alertas fuera del ambito'),
 ('20000000-0000-4000-8000-000000000002', 'GeoBosques', '2026-10-01', '2026-10-02 09:00:00+00', '00000000-0000-4000-8000-000000000001', 10, 2, 8, 0, 1, 0, 2, NULL)
ON CONFLICT DO NOTHING;

INSERT INTO ajustes_prioridad (id, zona_codigo, forma, nivel_elegido, puntaje_ajustado, puntaje_calculado_al_ajustar, justificacion, estado, creado_en, creado_por, retirado_en, retirado_por, justificacion_retiro) VALUES
 ('40000000-0000-4000-8000-000000000003', 'EA-2026-002', 'por_puntaje', NULL,   10, 20, 'sombra de nube',           'retirado',    '2026-09-18 08:00:00+00', '00000000-0000-4000-8000-000000000001', '2026-09-19 08:00:00+00', '00000000-0000-4000-8000-000000000002', 'visita de campo'),
 ('40000000-0000-4000-8000-000000000001', 'EA-2026-001', 'por_puntaje', NULL,   60, 45, 'frente activo',            'reemplazado', '2026-09-26 08:00:00+00', '00000000-0000-4000-8000-000000000001', NULL, NULL, NULL),
 ('40000000-0000-4000-8000-000000000002', 'EA-2026-001', 'por_nivel',   'alta', 70, 45, 'avance hacia la quebrada', 'vigente',     '2026-09-27 08:00:00+00', '00000000-0000-4000-8000-000000000001', NULL, NULL, NULL)
ON CONFLICT DO NOTHING;

INSERT INTO marcas (id, zona_codigo, tipo, origen, rotulo, texto, activa, creada_en, creada_por, retirada_en, retirada_por, motivo_retiro) VALUES
 ('30000000-0000-4000-8000-000000000001', 'EA-2026-002', 'area_pequena',  'automatica', NULL, 'area pequena', true, '2026-09-17 11:00:00+00', NULL, NULL, NULL, NULL),
 ('30000000-0000-4000-8000-000000000003', 'EA-2026-001', 'marca_analista', 'analista', 'Marca del analista', 'pozas', false, '2026-09-25 11:00:00+00', '00000000-0000-4000-8000-000000000001', '2026-09-28 11:00:00+00', '00000000-0000-4000-8000-000000000001', 'pozas descartadas en campo'),
 ('30000000-0000-4000-8000-000000000002', 'EA-2026-001', 'marca_analista', 'analista', 'Marca del analista', 'posible actividad minera', true, '2026-09-30 11:00:00+00', '00000000-0000-4000-8000-000000000001', NULL, NULL, NULL)
ON CONFLICT DO NOTHING;

INSERT INTO entradas_historial (id, zona_codigo, tipo_accion, fecha_hora, autor_id, codigo_alerta_origen, estado_anterior, estado_nuevo, ajuste_id, forma, nivel_elegido, puntaje_calculado, puntaje_ajustado, marca_id, texto_marca, texto) VALUES
 ('50000000-0000-4000-8000-000000000001', 'EA-2026-001', 'zona_creada',      '2026-09-05 10:00:00+00', NULL, 'A-1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
 ('50000000-0000-4000-8000-000000000002', 'EA-2026-001', 'cambio_estado',    '2026-09-06 09:00:00+00', '00000000-0000-4000-8000-000000000001', NULL, 'nueva', 'en_revision', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
 ('50000000-0000-4000-8000-000000000003', 'EA-2026-001', 'ajuste_fijado',    '2026-09-27 08:00:00+00', '00000000-0000-4000-8000-000000000001', NULL, NULL, NULL, '40000000-0000-4000-8000-000000000002', 'por_nivel', 'alta', 45, 70, NULL, NULL, 'avance hacia la quebrada'),
 ('50000000-0000-4000-8000-000000000004', 'EA-2026-001', 'marca_registrada', '2026-09-30 11:00:00+00', '00000000-0000-4000-8000-000000000001', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '30000000-0000-4000-8000-000000000002', 'posible actividad minera', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO trabajos (id, tipo, estado, creado_en, actualizado_en, mensaje_estado, resultado, error) VALUES
 ('60000000-0000-4000-8000-000000000001', 'ingesta_alertas', 'completado', '2026-09-22 10:00:00+00', '2026-09-22 10:00:30+00', 'Ingesta terminada', '{"carga_alertas_id": "20000000-0000-4000-8000-000000000001"}', NULL),
 ('60000000-0000-4000-8000-000000000002', 'carga_capa', 'fallido', '2026-09-23 10:00:00+00', '2026-09-23 10:00:05+00', NULL, NULL, '{"codigo": "GEOMETRIA_NO_VALIDA", "mensaje": "La capa de rios exige geometrias de tipo linea"}')
ON CONFLICT DO NOTHING;
