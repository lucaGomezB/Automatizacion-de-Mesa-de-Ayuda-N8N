## Why

El workflow N8N ya fue corregido y commiteado (`5efce4b`): la compuerta de revisión humana dejó de evaluarse antes del POST y pasó a evaluarse después, sobre el flag `requiere_revision_humana` que devuelve el backend. Sin embargo, `openspec/specs/n8n-workflow/spec.md` todavía describe la compuerta vieja (un `if` pre-POST sobre `confianza >= 0.70`). Esta spec desactualizada es la única fuente de verdad formal, así que el comportamiento real y el documentado divergen.

## What Changes

- Se formaliza el gate de dos capas implementado en `5efce4b`:
  - **Pre-POST `Entrada valida`**: validación de entrada (longitud de texto para correo/web; validez de la respuesta IA para telefonía) con la condición `confianza >= 0.70 OR revision_forzada == true`. NO es una compuerta de confianza del modelo.
  - **Post-POST `Requiere revision humana`**: evalúa el flag `requiere_revision_humana` del response del backend (verdadero cuando `confianza < 0.70`).
- Se documenta la rama verdadera del gate post-POST: notifica al operador designado vía `$env.OPERATOR_EMAIL` (nodo `Notificar operador designado`) y registra auditoría; para el canal correo, además marca el mensaje como leído.
- Se documenta la rama falsa: continúa con las confirmaciones por canal.
- Se documenta que los nodos HTTP resuelven el host del backend con `$env.BACKEND_URL`, sin host hardcodeado.
- Se actualiza el delta de `n8n-workflow` para que la spec archivada refleje este comportamiento.

## Capabilities

### New Capabilities

- (ninguna)

### Modified Capabilities

- `n8n-workflow`: el requerimiento "Ruteo por umbral de confianza" pasa a describir la compuerta de dos capas (validación de entrada pre-POST y gate de revisión post-POST sobre el flag del backend). Se agregan los requerimientos "Notificacion al operador designado" y "URLs del backend configurables por entorno".

## Impact

- `openspec/specs/n8n-workflow/spec.md` — sincronización del requerimiento y alta de los nuevos.
- `n8n/workflow.json` — ya implementado (commit `5efce4b`); este change no lo modifica.
- `docker-compose.yml` y `.env.example` — ya exponen `BACKEND_URL` y `OPERATOR_EMAIL`; no se modifican.
- `docs/n8n-workflow-guide.md` — ya actualizado en `5efce4b`; no se modifica.
- `App/Backend/tests/test_n8n_workflow.py` — ya cubre el gate, la notificación y las URLs por entorno; no se modifica.
