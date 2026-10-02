## 1. Preparación, decisiones y safety net

- [x] 1.1 Resolver las Open Questions del `design.md` con el humano antes de escribir código: (a) Open Question 1 — confirmar el PK `id` como número canónico (recomendado) o un número de negocio con prefijo. Verificación: decisión registrada en `design.md` (Open Question marcada RESUELTA) o documento de decisión adjunto. **OQ1 RESUELTA.** Las Open Questions de consentimiento/costo del SMS (OQ2) y de entregabilidad AR +54 (OQ3) se movieron al change `c-67-notificacion-sms-llamante`.
- [x] 1.2 Registrar el baseline de las suites afectadas: `cd App/Backend; pytest -m "not integration" tests/test_n8n_workflow.py tests/test_openapi_sync.py tests/test_incidentes.py tests/test_telefonia_service.py tests/test_runtime_cost_guard.py` y anotar el conteo en verde. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificación: conteo baseline anotado y sin fallos nuevos atribuibles al change. **Baseline: offline 676 passed / 26 deselected / 1 xfailed; archivos afectados 216 passed / 1 xfailed.**

## 4. Número canónico y verificación de contrato

- [x] 4.7 Verificar el contrato OpenAPI si cambió el webhook de voz: regenerar `docs/openapi.json` y ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v`. Verificación: el test de sincronización pasa. **El webhook de voz no cambió; `docs/openapi.json` se regeneró por el nuevo campo de respuesta `numero_incidente` y `test_openapi_sync.py` pasa (5/5).**
- [x] 4.8 Verificar la implementación del número canónico de incidente (`numero_incidente`) expuesto en el contrato de alta y propagado por las notificaciones: el backend lo deriva del identificador persistido y todos los canales exponen el mismo valor. Commit de implementación `a7f9477`. Verificación: `docs/openapi.json` incluye `numero_incidente` y `cd App/Backend; pytest tests/test_openapi_sync.py -v` pasa (5/5).

## 5. Cableado N8N: correo y cierre web

- [x] 5.1 RED: extender `App/Backend/tests/test_n8n_workflow.py` para exigir: (a) la normalización extrae el remitente desde `from` string y desde `from.emailAddress.address`; (b) el nodo `Correo de confirmacion al usuario` es alcanzable desde la rama de revisión humana del canal correo; (c) la rama de revisión humana del web responde con `incidente_id` no nulo cuando el incidente fue creado. Verificación: los tests fallan contra el workflow actual.
- [x] 5.2 GREEN: editar `n8n/workflow.json` para (a) normalizar el `remitente` en ambos formatos, (b) conectar la confirmación de correo también en la rama `requiere_revision_humana = true` del canal correo con `onError: continueRegularOutput`, y (c) incluir el `incidente_id` en el cierre web de la rama de revisión humana. Verificación: los tests de 5.1 pasan.
- [x] 5.3 TRIANGULATE: prueba de no regresión de c-46/c-47/c-52 (el sello `.first()`, `Restaurar item telefonia` entre `Guard de costo` y `Guard permite?`, y la salida de telefonía del switch siguen sin desviarse al nodo de correo). Verificación: casos en verde.
- [x] 5.4 TRIANGULATE: verificar que las ramas web sin incidente siguen declarando `sin_alta` sin número y que la guarda `Es web?` restringe la respuesta al canal web. Verificación: casos en verde.
- [x] 5.5 Actualizar `docs/n8n-workflow-guide.md`: eliminar la afirmación de confirmación telefónica por TwiML (`<Say>`), documentar la confirmación de correo en revisión humana y el cierre web con número, y ajustar los conteos de nodos y de pruebas. Verificación: `cd App/Backend; pytest tests/test_n8n_workflow.py -v` en verde y conteos coincidentes.

## 6. Documentación y verificación final

- [x] 6.2 Ejecutar la suite backend offline: `cd App/Backend; pytest -m "not integration"`. Verificación: sin regresiones respecto del baseline de 1.2. **693 passed / 26 deselected / 1 xfailed.**
- [x] 6.3 Ejecutar lint: `cd App/Backend; ruff check .`. Verificación: sin errores E nuevos. **All checks passed.**
- [x] 6.5 Ejecutar `openspec validate --strict --changes c-53-notificacion-numero-incidente`. Verificación: validación estricta sin errores.

> El alcance de SMS al llamante se movió a `c-67-notificacion-sms-llamante` (dependiente de OQ3 y C-66).
