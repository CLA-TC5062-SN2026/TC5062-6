# Deuda técnica de EcoAlert Tambopata

## Evidencia y medición

| Deuda observada | Evidencia | Medición propuesta |
|---|---|---|
| Cobertura funcional incompleta del contrato | [README del backend](../backend/README.md), sección Alcance: 20 de 39 operaciones implementadas; el resto se enumera como pendiente. | Comparar operaciones OpenAPI con rutas implementadas usando `tests/test_contrato.py`, registrar pendientes por historia y aceptación, sin presentar cobertura de contrato como cobertura funcional completa. |
| Diagnósticos estáticos abiertos | [Salida inicial y final](output_linter.txt): 203 y 200 `E501`, respectivamente; 13 diagnósticos mypy en ambas versiones. | Registrar códigos, archivos y tendencias por ejecución reproducible. Separar diagnósticos que reflejan tipos dinámicos de fallos demostrados; no fijar una reducción ficticia como objetivo. |
| Acoplamiento de reglas de cuentas a HTTP y PostgreSQL | [Review SOLID](code_review.md): `usuarios.py:26-47` y `:69-87` originales. | Contar pruebas de reglas que requieren PostgreSQL y tiempo de ejecución; documentar dependencias del servicio cuando se extraiga. El número de clases por sí solo no mide calidad. |
| Consulta de usuarios sin paginación | `backend/app/routers/usuarios.py:52-54` original devuelve todas las coincidencias; el contrato actual describe una lista. | Medir cantidad de filas, tamaño de respuesta y latencia con datos sintéticos a distintos volúmenes. Cualquier paginación requiere acordar compatibilidad de API y contrato. |
| Hash dentro de una transacción idempotente | `backend/app/routers/usuarios.py:33-43` original, [review, hallazgo 4](code_review.md). | Medir duración de transacción, espera de bloqueos y coste de reintentos idénticos bajo carga sintética. No se dispone de esas mediciones en esta auditoría. |
| Pruebas que modifican la base | [base_pruebas.py](../backend/tests/base_pruebas.py) prepara bases; [conftest de A2](../S05_S06_A2/pruebas/conftest.py) trunca tablas con `CASCADE`. El sufijo `_test` no demuestra propiedad exclusiva de la base. | Verificar en CI que cada ejecución dispone de una instancia efímera propia; contabilizar fallos de preparación y tiempo de suite. Nunca dirigirla a bases compartidas. |
| Advertencia de dependencias de pruebas | [pytest final](output_pytest_final.txt) registra `StarletteDeprecationWarning` sobre `httpx` y `TestClient`. | Registrar versión y advertencia en cada actualización, comprobar compatibilidad antes de cambiar dependencias y retirar la alerta solo cuando deje de reproducirse. |

## Deuda consciente e involuntaria

La implementación parcial de operaciones está documentada explícitamente en el README como alcance y pendientes: es una limitación conocida y planificable. La documentación no demuestra qué integrante la decidió ni que se aceptara expresamente como deuda para acelerar una entrega.

Como ejemplo involuntario, el `except UniqueViolation` original convertía cualquier restricción de unicidad en conflicto de correo, aunque el esquema también tiene una clave primaria. No hay evidencia de que se pretendiera ocultar otros conflictos; se corrigió en esta actividad. Los falsos positivos de tipado por inferencia también pueden acumularse sin una decisión explícita, pero no deben confundirse con errores funcionales confirmados.

## Integración en SCRUM y Definition of Done

1. **Refinamiento:** vincular cada operación OpenAPI pendiente o defecto reproducido a una historia con riesgo, evidencia, responsable del equipo, prioridad y criterio de aceptación. Estimar coste de solución en planificación; no inventar horas para esta auditoría.
2. **Planificación:** reservar capacidad para deuda priorizada junto a funcionalidad. Revisar tendencia de diagnósticos y tiempos de pruebas, no solo el total bruto.
3. **Durante la historia:** ejecutar flake8 y mypy con versiones y configuración acordadas, sin ocultar diagnósticos; añadir pruebas de comportamiento y regresión para cambios de reglas. En reglas transaccionales, probar concurrencia con PostgreSQL/PostGIS aislado.
4. **Code review:** exigir una revisión de otra persona con referencia a contrato, manejo de errores, datos sensibles, límites transaccionales y riesgos SOLID aplicables. Documentar explícitamente los principios que no se pueden evaluar, en lugar de inventar infracciones.
5. **CI y Definition of Done:** usar una instancia PostGIS efímera por ejecución, credenciales temporales y separación de bases para A1 y A2. Publicar comandos, versiones, salida y código de salida de pytest, flake8 y mypy. Las pruebas relevantes deben pasar; los diagnósticos existentes deben quedar vinculados a incidencias y no aumentar sin justificación revisada. Para convertir flake8 y mypy en bloqueos absolutos primero debe acordarse y resolver su línea base actual, no suprimirla.
6. **Revisión y retrospectiva:** demostrar el comportamiento aceptado, revisar deuda pendiente y actualizar prioridades, incluidos resultados de rendimiento cuando existan datos. Una historia no queda terminada si modifica el contrato sin documentarlo o deja sin ejecutar una verificación obligatoria sin una excepción explícita del equipo.

No se encontró un directorio `.github/workflows` en la inspección; la integración CI anterior es una propuesta, no una automatización existente verificada.
