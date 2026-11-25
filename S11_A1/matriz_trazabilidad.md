# Matriz de trazabilidad requerimientos → implementación

**EcoAlert Tambopata · Equipo 6 · TC5062 · S11-A1, Parte 2**

| | |
|---|---|
| Requerimientos | [`S03_A1/SRS_equipo.md`](../S03_A1/SRS_equipo.md), línea base v1.0: 39 RF (17 Must, 13 Should, 9 Could) |
| Historias de usuario | [`S03_A1/backlog_completo.md`](../S03_A1/backlog_completo.md): 15 HU en 5 épicas |
| Endpoints | [`backend/docs/openapi_integrado.yaml`](../backend/docs/openapi_integrado.yaml) v1.3.0: 39 operaciones, 20 implementadas |
| Pruebas | `backend/tests/` y `S05_S06_A2/pruebas/` (pytest, **234/234**), `frontend/src/**/*.test.*` (Vitest, **39/39**), E2E [`evidencias/flujo_e2e.cjs`](evidencias/flujo_e2e.cjs) (Playwright) |
| Corte | Rama `feat/S11_A1-documentacion-final`, 24/11/2026. Cada resultado se reprodujo en esa fecha; las salidas están en [`evidencias/`](evidencias/). |

## 1. Cómo se clasificó cada requerimiento

| Estado | Criterio |
|---|---|
| ✅ **Completo** | Todos los criterios de aceptación (`RF-XX-AC-Y`) del RF están implementados y cada uno tiene al menos una prueba que pasa. |
| 🟡 **Parcial** | Hay endpoints implementados y probados para una parte del RF (en este proyecto, siempre la **lectura**), pero faltan las operaciones que crean o modifican los datos. |
| ❌ **No implementado** | No hay código que cumpla el RF. Si el contrato ya define sus endpoints, se indican como *diseñados*. |

Dos reglas para no inflar el estado:

1. **Una prueba sobre datos sembrados no prueba que el sistema genere esos datos.** Las lecturas de marcas, ajustes e
   historial se prueban contra `backend/tests/sql/semilla.sql`; mientras no existan las operaciones que los crean, el RF
   queda en 🟡.
2. **Una prueba de la API no cubre un criterio de interfaz.** Los criterios marcados *(Prueba E2E de interfaz)* en el
   SRS se cuentan solo si hay una prueba de frontend o E2E.

## 2. Resumen

| Prioridad | RF | ✅ Completo | 🟡 Parcial | ❌ No implementado |
|---|---:|---:|---:|---:|
| Must (MVP) | 17 | 2 (RF-01, RF-02) | 4 (RF-04, RF-11, RF-12, RF-13) | 11 |
| Should | 13 | 0 | 0 | 13 |
| Could | 9 | 0 | 0 | 9 |
| **Total** | **39** | **2** | **4** | **33** |

El MVP del SRS **no está completo**: se construyó la capa de acceso y administración (RF-01, RF-02), la consulta de los
datos y el contrato completo de la API, pero no el núcleo geoespacial (ingesta, agrupación, prioridad, mapa,
comparación y exportación). La [retrospectiva](retrospectiva_proyecto.md#b2-qué-partes-del-problema-no-se-resolvieron)
explica por qué.

## 3. Matriz completa (RF → HU → endpoint → prueba)

Rutas relativas a `/api/v1`. Abreviaturas de pruebas: **[A2]** `S05_S06_A2/pruebas/`, **[BE]** `backend/tests/`,
**[FE]** `frontend/src/`, **[E2E]** `S11_A1/evidencias/flujo_e2e.cjs`.

### 3.1 Must (RF-01 a RF-17)

| RF | Requerimiento | HU | Endpoint implementado | Prueba | Estado | Justificación |
|---|---|---|---|---|---|---|
| RF-01 | Autenticación y sesión | HU-E1-1 | `POST /auth/login` · `GET /auth/me` · `POST /auth/logout` | [A2] `test_auth.py::test_RF_01_AC_1..6`; [FE] `ProtectedRoute.test.jsx`; [E2E] pasos 1–3 | ✅ | Los 7 criterios tienen prueba (detalle en §4.1). La sesión vive en la tabla `sesiones`: se revoca al cerrar sesión y expira a los 30 min sin actividad. |
| RF-02 | Gestión de usuarios y roles | HU-E1-2 | `GET/POST /usuarios` · `GET/PUT/PATCH /usuarios/{id}` · `POST /auth/register` · `PUT /auth/password` | [A2] `test_RF_02_AC_2..9`; [BE] `test_api_usuarios.py` (45), `test_api_lecturas.py::test_RF_02_AC_6_…`; [FE] `UsuariosPage.test.jsx`, `CambiarPasswordPage.test.jsx`; [E2E] pasos 5–13 | ✅ | Los 10 criterios tienen prueba (§4.2). La interfaz de S11 cerró AC-4 (cambio de contraseña temporal desde la UI) y AC-10 (menú oculto a Analista SIG). |
| RF-03 | Carga de capas de referencia | HU-E2-1 | — *(diseñados: `POST /archivos`, `GET/POST /capas-referencia/…`)* | — | ❌ | Era el compromiso del Sprint 1 y no se construyó: las actividades siguientes del curso pidieron CRUD, autenticación y frontend, y el equipo priorizó entregarlas. Solo existen las tablas (`capas_referencia`, `versiones_capa`) en el esquema. |
| RF-04 | Ingesta de alertas GeoBosques | HU-E2-2 | `GET /alertas` · `GET /cargas-alertas` · `GET /cargas-alertas/{id}` · `GET /trabajos/{id}` *(pendiente: `POST /archivos`, `POST /cargas-alertas`)* | [BE] `test_api_lecturas.py::test_alertas_*`, `test_cargas_*`, `test_trabajos_*`; [FE] `AlertasPage.test.jsx`; [E2E] paso 4 | 🟡 | Se consultan alertas y cargas con paginación y filtros, pero no se pueden **ingerir**: las 24 alertas de la demo vienen de `scripts/sembrar_demo.py`. Ningún criterio RF-04-AC-1 a AC-7 se cumple todavía. |
| RF-05 | Agrupación en zonas de cambio | HU-E3-1 | — *(diseñado: efecto de `POST /cargas-alertas`, `GET /zonas/{codigo}`)* | — | ❌ | Depende de la ingesta (RF-04). Es la historia de mayor riesgo técnico (13 SP, lógica espacial con PostGIS). |
| RF-06 | Mapa con capas | HU-E3-2 | — *(diseñados: `GET /mapa/capas[/…]`)* | — | ❌ | Sin zonas ni capas cargadas no hay qué dibujar; además no se eligió biblioteca de mapas en el frontend. |
| RF-07 | Frescura de las fuentes | HU-E2-3 | — *(dato disponible: `fecha_corte` en `GET /cargas-alertas`)* | — | ❌ | La fecha de corte se guarda y se expone, pero no existe el aviso de "posiblemente desactualizadas" (> 30 días) ni el panel de capas. |
| RF-08 | Contexto territorial de la zona | HU-E3-3 | — *(diseñado: `GET /zonas/{codigo}`)* | — | ❌ | Requiere zonas (RF-05) y capas (RF-03). |
| RF-09 | Priorización explicada | HU-E4-1 | — *(diseñados: `GET /zonas`, `GET /zonas/{codigo}`)* | — | ❌ | Es el valor central del producto y no está construido. El esquema guarda `nivel` y `puntaje_vigente`, pero los valores de la demo son sembrados, no calculados. |
| RF-10 | Lista priorizada de zonas | HU-E4-2 | — *(diseñado: `GET /zonas`)* | — | ❌ | Ordena por el puntaje de RF-09. |
| RF-11 | Ajuste manual de prioridad | HU-E4-2 | `GET /zonas/{codigo}/ajustes` · `GET /zonas/{codigo}/ajustes/{id}` *(pendiente: `POST …/ajustes`, `PATCH …/ajustes/{id}`)* | [BE] `test_api_lecturas.py::test_ajustes_lista_mas_reciente_primero_y_detalle` | 🟡 | Se consulta el historial de ajustes (relacionado con AC-6 y AC-13) sobre datos sembrados; no se puede fijar ni retirar un ajuste. |
| RF-12 | Estados de revisión e historial | HU-E4-3 | `GET /zonas/{codigo}/historial` · `GET /zonas/{codigo}/historial/{id}` *(pendiente: `POST …/cambios-estado`)* | [BE] `test_historial_cronologico_con_autor_sistema`, `test_zona_inexistente_404` | 🟡 | La lectura cubre la forma de AC-19 (primera entrada "zona creada" por "Sistema") y AC-20 (lista cronológica), pero no hay transiciones de estado: AC-1 a AC-16 no se cumplen. |
| RF-13 | Marcas de confianza | **sin HU** | `GET /zonas/{codigo}/marcas` · `GET /zonas/{codigo}/marcas/{id}` *(pendiente: `POST …/marcas`, `PATCH …/marcas/{id}`)* | [BE] `test_marcas_solo_activas_por_defecto_e_incluye_retiradas_si_se_pide`, `test_marca_automatica_no_tiene_autor_y_el_detalle_coincide` | 🟡 | Se leen marcas automáticas y del analista (con retiro y motivo) sobre datos sembrados; no se calculan las automáticas ni se registran las del analista. **Hueco de trazabilidad:** el backlog no tiene una historia para este RF Must (§5). |
| RF-14 | Comparación de dos periodos | HU-E5-1 | — *(diseñados: `POST /analisis`, `GET /analisis/{id}`)* | — | ❌ | Depende de zonas y puntaje. |
| RF-15 | Consulta de análisis anteriores | HU-E5-1 | — *(diseñados: `GET /analisis[/{id}]`)* | — | ❌ | Depende de RF-14. |
| RF-16 | Exportación CSV | HU-E5-2 | — *(diseñado: `GET /exportaciones/zonas`)* | — | ❌ | Depende de la lista de zonas (RF-10). |
| RF-17 | Exportación GeoJSON | HU-E5-2 | — *(diseñado: `GET /exportaciones/zonas`)* | — | ❌ | Depende de zonas (RF-05). |

### 3.2 Should y Could (RF-18 a RF-39)

Ninguno está implementado ni tiene endpoints en el contrato: el contrato v1.3.0 cubre solo los 166 criterios Must
(`backend/tests/test_contrato.py` lo verifica). Todos quedaron fuera del alcance porque el MVP no se completó.

| RF | Requerimiento | Prioridad | HU | Estado | Justificación |
|---|---|---|---|---|---|
| RF-18 | Comparación visual de imágenes (Sentinel-2 vía GEE) | Should | — | ❌ | Depende de RF-14 y de una integración con Google Earth Engine. |
| RF-19 | Ingesta RADD y confirmación multifuente | Should | — | ❌ | Depende de RF-04. |
| RF-20 | Reapertura automática de zonas | Should | — | ❌ | Depende de RF-05 y RF-12. |
| RF-21 | Configuración de pesos | Should | — | ❌ | Depende de RF-09. |
| RF-22 | Exportación GeoPackage y KML | Should | — | ❌ | Depende de RF-17. |
| RF-23 | Ficha de zona en PDF | Should | — | ❌ | Depende de RF-08 y RF-09. |
| RF-24 | Bitácora de auditoría | Should | HU-E5-3 | ❌ | No existe tabla de solo inserción ni registro de eventos. |
| RF-25 | Segundo factor TOTP y bloqueo por intentos | Should | HU-E1-3 | ❌ | No hay TOTP ni bloqueo tras 5 intentos; el login responde 401 genérico sin límite de intentos (riesgo documentado en `S05_S06_A2/revision_seguridad.md`). |
| RF-26 | Zonas manuales | Should | — | ❌ | Depende de RF-05. |
| RF-27 | Candidatos por NDVI | Could | — | ❌ | Depende de RF-18. |
| RF-28 | Fusión de zonas | Could | — | ❌ | Depende de RF-05. |
| RF-29 | Zonas nuevas desde la última revisión | Could | — | ❌ | Depende de RF-05 y RF-12. |
| RF-30 | Sectores de trabajo | Could | — | ❌ | Depende de RF-05. |
| RF-31 | Notas de discrepancia | Could | — | ❌ | Depende de RF-08. |
| RF-32 | Formatos y vistas adicionales | Could | — | ❌ | Depende de RF-16 y RF-18. |
| RF-33 | Reportes de campo | Could | — | ❌ | Fuera del alcance; implicaría datos personales (RD-12, TA-03). |
| RF-34 | Observaciones de la zona | Should | — | ❌ | Depende de RF-12. |
| RF-35 | Capa de comunidades nativas | Should | — | ❌ | Depende de RF-03; fuente oficial pendiente (TA-05). |
| RF-36 | Filtros y orden adicionales | Should | — | ❌ | Depende de RF-10. |
| RF-37 | Exportación Shapefile | Should | HU-E5-2 | ❌ | Depende de RF-17. |
| RF-38 | Selección manual para exportar | Could | — | ❌ | Depende de RF-16 y RF-17. |
| RF-39 | Responsable de la zona | Could | — | ❌ | Depende de RF-05. |

## 4. Detalle por criterio de los RF completos

### 4.1 RF-01 — Autenticación y sesión

| Criterio | Qué se verifica | Prueba |
|---|---|---|
| RF-01-AC-1 | Credenciales correctas → sesión y acceso según el rol | [A2] `test_auth.py::test_RF_01_AC_1_login_exitoso_entrega_jwt_con_expiracion_explicita`; [FE] `ProtectedRoute.test.jsx` "login exitoso redirige a la ruta protegida que se había pedido"; [E2E] paso 3 |
| RF-01-AC-2 | Contraseña incorrecta → 401 "Usuario o contraseña incorrectos" | [A2] `test_RF_01_AC_2_password_incorrecta_responde_401_generico`; [FE] `ProtectedRoute.test.jsx` "muestra el error del servidor cuando las credenciales son incorrectas"; [E2E] paso 2 |
| RF-01-AC-3 | Cuenta inexistente → el mismo 401 | [A2] `test_RF_01_AC_3_cuenta_inexistente_responde_igual_que_password_incorrecta` |
| RF-01-AC-4 | 31 min sin actividad → 401 | [A2] `test_RF_01_AC_4_sesion_inactiva_31_minutos_responde_401` |
| RF-01-AC-5 | Actividad hace 29 min → se atiende | [A2] `test_RF_01_AC_5_sesion_con_actividad_hace_29_minutos_sigue_vigente` |
| RF-01-AC-6 | Token reutilizado tras cerrar sesión → 401 | [A2] `test_RF_01_AC_6_token_no_sirve_despues_de_logout` |
| RF-01-AC-7 *(E2E)* | Sin sesión, una pantalla protegida redirige al login | [FE] `ProtectedRoute.test.jsx` "sin sesión, una ruta protegida redirige al login"; [E2E] paso 1 |

### 4.2 RF-02 — Gestión de usuarios y roles

| Criterio | Qué se verifica | Prueba |
|---|---|---|
| RF-02-AC-1 | Coordinación crea una cuenta de analista activa | [BE] `test_api_usuarios.py::test_post_crea_usuario_y_persiste`; [FE] `UsuariosPage.test.jsx` "crea una cuenta con Idempotency-Key…"; [E2E] paso 7 |
| RF-02-AC-2 | Rol inválido → rechazo con los roles válidos | [A2] `test_auth.py::test_RF_02_AC_2_rol_invalido_responde_422`; [BE] `test_post_rechaza_cuerpos_invalidos_con_422` |
| RF-02-AC-3 | Contraseña temporal de 11 caracteres → rechazo | [A2] `test_RF_02_AC_3_password_de_11_caracteres_responde_422`; [FE] `UsuariosPage.test.jsx` "rechaza en el cliente una contraseña temporal de 11 caracteres"; [E2E] paso 6 |
| RF-02-AC-4 | Primer ingreso → debe cambiar la contraseña antes de cualquier otra función | [A2] `test_RF_02_AC_4_password_temporal_bloquea_todo_salvo_me_password_y_logout`; [BE] `test_integracion_auth.py` (rutas de A1 con contraseña temporal); [FE] `CambiarPasswordPage.test.jsx` (3 pruebas); [E2E] pasos 10–11 |
| RF-02-AC-5 | Cuenta desactivada → no inicia sesión | [A2] `test_RF_02_AC_5_cuenta_desactivada_no_inicia_sesion`; [BE] `test_desactivar_cierra_las_sesiones_abiertas`; [E2E] pasos 12–13 |
| RF-02-AC-6 | El autor desactivado sigue en el historial | [BE] `test_api_lecturas.py::test_RF_02_AC_6_autor_desactivado_sigue_apareciendo_en_el_historial` (nueva en S11; falla si la consulta omite autores inactivos) |
| RF-02-AC-7 | `DELETE` de una cuenta no existe (404/405) | [A2] `test_proteccion_rutas.py::test_RF_02_AC_7_borrar_cuenta_no_existe`; [BE] `test_delete_fisico_no_existe_405`, `test_contrato.py` |
| RF-02-AC-8 | No se desactiva la última Coordinación | [A2] `test_RF_02_AC_8_no_se_desactiva_la_ultima_coordinacion` y variante `PUT`; [BE] `test_protege_la_ultima_cuenta_de_coordinacion`, `test_desactivaciones_simultaneas_nunca_dejan_cero_coordinaciones`; [FE] `UsuariosPage.test.jsx`; [E2E] paso 9 |
| RF-02-AC-9 | Analista SIG en gestión de usuarios → 403 | [A2] `test_RF_02_AC_9_analista_en_gestion_de_usuarios_responde_403`, `test_RF_02_AC_9_register_con_rol_analista_responde_403` |
| RF-02-AC-10 *(E2E)* | Analista SIG no ve la opción en el menú | [FE] `UsuariosPage.test.jsx` "un Analista SIG no ve la opción en el menú…" y "Coordinación sí ve la opción…"; [E2E] paso 10 |

## 5. Huecos de trazabilidad encontrados al construir la matriz

| # | Hallazgo | Consecuencia | Acción |
|---|---|---|---|
| H-1 | **RF-13 (Must) no tiene historia de usuario.** El backlog lo menciona solo de paso en el CA3 de HU-E4-3. | Un requerimiento del MVP habría quedado sin estimar ni planificar. | Registrar una HU propia en el siguiente refinamiento. |
| H-2 | **RF-02-AC-6 no tenía prueba** hasta esta actividad. | El RF figuraba como completo sin evidencia para uno de sus criterios. | Se agregó `test_RF_02_AC_6_…` y se verificó que falla con una mutación del código. |
| H-3 | La actividad pide citar las pruebas manuales "documentadas en S09-A1", pero **`S09_A1/` no contiene un plan de pruebas manuales**: es una auditoría de calidad. | No hay una fuente única de pruebas manuales. | Se citan las pruebas manuales existentes (`S05_S06_A2/pruebas/pruebas_manuales.sh`, `S05_S06_A2/evidencias/`) y el E2E automatizado de esta actividad, que reemplaza la verificación manual del flujo de la demo. |
| H-4 | `S09_A1/*.md` enlazan a `output_pytest_inicial.txt`, `output_pytest_final.txt`, `backend/.flake8` y `backend/mypy.ini`, que **no están en el repositorio**. | Esos enlaces están rotos. La cifra final de S09 (233 pruebas) sí se reprodujo: 233 + la prueba nueva de H-2 = 234. | Pedir al autor de S09-A1 que suba esos archivos. |
| H-5 | El SRS pide nombrar cada prueba como `test_RF_XX_AC_Y`. Solo la suite de A2 lo sigue; la de A1 usa nombres descriptivos. | La trazabilidad de las pruebas de A1 se reconstruyó a mano para esta matriz. | Adoptar la convención en las pruebas nuevas, como se hizo con la de H-2. |

## 6. Requerimientos no funcionales relacionados con lo implementado

| RNF | Estado | Evidencia |
|---|---|---|
| RNF-01 Todo exige autenticación | ✅ | [A2] `test_proteccion_rutas.py`: 401 sin token o con token inválido en **todas** las rutas montadas, según los `x-roles` del contrato. `levantar.sh` comprueba el 401 en el despliegue. |
| RNF-02 Control de acceso en el servidor (403) | ✅ para las rutas implementadas | [A2] `test_proteccion_rutas.py`: matriz rol × ruta; la interfaz oculta lo que el rol no puede usar, pero el servidor responde 403 de todos modos. |
| RNF-03 TLS y contraseñas con bcrypt/Argon2 | 🟡 | Argon2id verificado en la base ([A2] `test_security.py`). El Codespace sirve HTTPS a través del proxy de GitHub; no hay configuración TLS propia (no hay VPS). |
| RNF-06 Sin código ni comandos; todo en español | 🟡 | Lo construido se usa desde la interfaz y en español. Pero la carga de datos (RF-03, RF-04) todavía exige un script (`sembrar_demo.py`). |
| RNF-10 Despliegue con un solo comando | 🟡 | `bash .devcontainer/levantar.sh` levanta todo en un Codespace o en Linux con Docker. No hay un `docker compose up` que incluya API y frontend. |
