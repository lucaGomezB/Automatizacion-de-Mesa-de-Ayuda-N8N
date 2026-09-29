# Tasks: Auditoría correcta en la rama de revisión humana

## 1. Tests (RED)

- [x] 1.1 En `App/Backend/tests/test_n8n_workflow.py`, invertir `test_notificar_operador_reaches_audit`: pasa a exigir que `Registro de auditoria` NO sea sucesor de `Notificar operador designado` y que sea sucesor directo de `Requiere revision humana[main#0]`. Verificar que FALLA contra el workflow actual (fase RED).
- [x] 1.2 En el mismo archivo, invertir `test_c40_notificar_operador_still_reaches_audit` con el mismo contrato (auditoría hermana del gate, no descendiente de la notificación). Verificar RED.
- [x] 1.3 Agregar `test_c57_audit_receives_post_response_on_review_branch`: la rama verdadera de `Requiere revision humana` alimenta `Registro de auditoria` con la respuesta del POST (sucesor directo y ancestro `HTTP POST a MESA-AYUDAS`). Verificar RED.
- [x] 1.4 Agregar `test_c57_audit_does_not_depend_on_smtp_item`: el `jsCode` de `Registro de auditoria` no referencia `Notificar operador designado` y conserva la derivación `item.error -> error_backend`, `item.es_valido === false -> rechazado_datos_incompletos`, `typeof item.id === 'number' -> creado`. Verificar RED/triangulación.
- [x] 1.5 Agregar `test_c57_audit_no_double_execution_on_review_branch`: `Notificar operador designado` no figura como origen de `Registro de auditoria` en las conexiones. Verificar RED.
- [x] 1.6 Ejecutar `cd App/Backend; pytest tests/test_n8n_workflow.py` y confirmar que las aserciones nuevas/invertidas fallan por el cableado actual (RED documentado), sin fallos ajenos al change.

## 2. Workflow (GREEN)

- [x] 2.1 En `n8n/workflow.json`, agregar la arista `Requiere revision humana[main#0] -> Registro de auditoria` y quitar `Notificar operador designado[main#0] -> Registro de auditoria`. Verificar que las tareas 1.1–1.5 pasan.
- [x] 2.2 Actualizar el comentario de ramas del `jsCode` de `Registro de auditoria` para reflejar que la rama de revisión recibe la respuesta del POST (sin cambiar la lógica). Verificar que la suite estructural sigue verde.
- [x] 2.3 Confirmar que el conteo de nodos permanece en 37 (sin nodos nuevos/eliminados) y que no quedan nodos ejecutables huérfanos (`test_no_orphan_executable_nodes`).

## 3. Documentación

- [x] 3.1 En `docs/n8n-workflow-guide.md`, actualizar las tablas de wiring del gate post-POST: la rama verdadera conecta `Notificar operador designado` Y `Registro de auditoria` en paralelo; eliminar la frase que dice que la notificación desemboca en la auditoría.
- [x] 3.2 Actualizar la FAQ de auditoría y el conteo de pruebas estructurales declarado (`Verifica N propiedades estructurales`) para que coincida con la suite. Verificar con `test_c40_guide_test_count_matches_suite`.

## 4. Verificación

- [x] 4.1 Ejecutar `cd App/Backend; pytest tests/test_n8n_workflow.py` y verificar verde completo.
- [x] 4.2 Ejecutar `cd App/Backend; pytest -m "not integration"` y verificar que no hay regresiones en el subconjunto offline.
- [x] 4.3 Smoke manual en N8N: un alta con `requiere_revision_humana = true` (correo o web) registra en `Registro de auditoria` `resultado = "creado"` con `incidente_id` numérico y no `rechazado_datos_incompletos`. Satisfecho: ejecucion n8n #30 (workflow JYizNfNZXuhCr8Z7, 2026-09-29T19:17:18Z) creo el incidente #12 con requiere_revision_humana=true (clasificacion_log etapa=gemini confianza=0.20). El nodo Registro de auditoria, alimentado por el gate 'Requiere revision humana' (src del run), registro {incidente_id: 12, resultado: 'creado', sector_nombre: 'Soporte Tecnico Software'} — antes del fix registraba rechazado_datos_incompletos con incidente_id null.
- [x] 4.4 Verificar que el canal de rechazo conserva `rechazado_datos_incompletos` y el camino de error del POST conserva `error_backend` (sin regresión de N8N-AUDIT-002).
