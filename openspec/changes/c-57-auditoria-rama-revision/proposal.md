# Proposal: Auditoría correcta en la rama de revisión humana

## Why

El smoke de c-55 (ejecución n8n #24, workflow `JYizNfNZXuhCr8Z7`, 2026-09-29T18:08:45Z) creó el incidente #9, pero el nodo `Registro de auditoria` quedó con `{"incidente_id": null, "resultado": "rechazado_datos_incompletos", ...}`. Causa raíz: cableado. En la rama de revisión humana la auditoría es sucesora de `Notificar operador designado`, por lo que recibe el resultado SMTP (objeto con `accepted/rejected`, sin `id`) en vez de la respuesta del POST. Con ese item, `item.id` es `undefined` y el `jsCode` cae al fallback `rechazado_datos_incompletos`. El defecto quedó oculto hasta que c-55 corrigió el body del POST y se ejercitó por primera vez el camino éxito+revisión (antes la auditoría de ese camino solo se alcanzaba por la salida de error del POST, que registraba `error_backend`).

## What Changes

- **Rewiring de la rama de revisión**: agregar la arista `Requiere revision humana[main#0] -> Registro de auditoria` y quitar la arista `Notificar operador designado[main#0] -> Registro de auditoria`. Así la auditoría de la rama de revisión recibe la respuesta de `HTTP POST a MESA-AYUDAS` (item con `id` numérico) y no el resultado SMTP.
- `Notificar operador designado` pasa a ser terminal en la rama de revisión; la auditoría queda en **paralelo** con la notificación, de modo que un fallo de notificación no la omite.
- **Sin cambios al `jsCode` de auditoría**: con la entrada correcta el código ya distingue `creado` (`typeof item.id === 'number'`), `rechazado_datos_incompletos` (`item.es_valido === false`) y `error_backend` (`item.error`). El arreglo es de topología, no de lógica.
- **Tests estructurales**: invertir las dos aserciones que fijaban la arista SMTP→auditoría (`test_notificar_operador_reaches_audit`, `test_c40_notificar_operador_still_reaches_audit`) y agregar aserciones que fijen la nueva topología y la independencia del item SMTP.
- **Documentación**: actualizar `docs/n8n-workflow-guide.md` (tablas de wiring, FAQ de auditoría, conteo de pruebas estructurales).

### Fuera de alcance / follow-up (NO se aborda en este change)

- La descripción del catálogo `canal_origen` id 1 aún dice "Incidente recibido vía trigger de Microsoft Outlook en N8N", obsoleta tras la migración IMAP de c-55.
- El spec main `openspec/specs/n8n-workflow/spec.md` conserva menciones a "Outlook" (Purpose y texto histórico) que no reflejan IMAP.

Ambos se registran como seguimiento separado (documentación/catálogo, sin cambio de comportamiento) y no se incluyen como tareas de c-57.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `n8n-workflow`: la auditoría de la rama de revisión humana registra el alta creada (`resultado: "creado"` con `incidente_id` numérico) al consumir la respuesta del POST. Se ajustan: N8N-AUDIT-001 (resultado por rama, incluido el camino éxito+revisión), N8N-AUDIT-003 (la auditoría cuelga del gate post-POST en paralelo, no de la notificación), el requisito "Notificacion al operador designado" (sin orden estricto notificación→auditoría) y se agrega N8N-AUDIT-004 (contracto estructural: la auditoría no consume la salida de la notificación).

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `n8n/workflow.json` | Modificado | Alta de la arista gate→auditoría; baja de la arista notificación→auditoría. Sin nodos nuevos/eliminados (conteo 37 intacto). |
| `App/Backend/tests/test_n8n_workflow.py` | Modificado | Invertir 2 aserciones; agregar tests de topología y de independencia del item SMTP. |
| `docs/n8n-workflow-guide.md` | Modificado | Tablas de wiring, FAQ de auditoría y conteo de pruebas. |
| Backend FastAPI | Sin cambios | Contrato de persistencia y auditoría backend intactos. |
| n8n-notification | Sin cambios | No gobierna el cableado interno del workflow de alta. |

## Risks

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| La auditoría se ejecute dos veces en la misma corrida (gate y notificación) | Baja | Se elimina la arista SMTP→auditoría; las salidas del gate son mutuamente excluyentes. |
| Un fallo de la notificación aborte la ejecución antes de la rama de auditoría | Baja | La auditoría es hermana (paralela) del nodo de notificación y este conserva `onError: continueRegularOutput`. |
| Regresión del camino exitoso sin revisión | Baja | El test `test_audit_reachable_from_success_branch` y los tests de no-regresión cubren la rama `main#1`. |
| Conteo de pruebas de la guía desincronizado | Media | Actualizar el conteo en el mismo commit; `test_c40_guide_test_count_matches_suite` lo verifica. |

## Rollback Plan

`git revert` del commit restaura el cableado anterior (`Notificar operador designado -> Registro de auditoria`), los tests y la guía. Sin migraciones ni cambios de API/backend, no hay rollback de datos.

## Dependencies

- Ninguna nueva. Se apoya en el gate post-POST `Requiere revision humana` y en `Notificar operador designado` (c-55) ya presentes.

## Success Criteria

- [ ] `Registro de auditoria` es sucesor directo de `Requiere revision humana[main#0]` y NO es sucesor de `Notificar operador designado`.
- [ ] El `jsCode` de auditoría no referencia el nodo de notificación y conserva la distinción `creado` / `rechazado_datos_incompletos` / `error_backend`.
- [ ] `pytest tests/test_n8n_workflow.py` en verde (backend, SQLite).
- [ ] La guía declara el conteo de pruebas coincidente con la suite.
- [ ] Smoke manual: un alta con `requiere_revision_humana = true` registra `resultado: "creado"` con `incidente_id` numérico.
