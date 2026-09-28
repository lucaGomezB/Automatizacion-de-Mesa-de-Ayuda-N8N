# Proposal: Notificaciones de incidente con destinatarios resueltos por rol

## Why

Hoy el destinatario de la notificación de revisión humana está fijado en N8N como una única casilla (`$env.OPERATOR_EMAIL`). c-54 creó un directorio de empleados con roles y sector, pero nadie lo usa para enrutar notificaciones. Con más de un operador, la mesa de ayuda no puede avisar al operador del sector correcto: el aviso queda atado a una variable de entorno y a una sola persona. La resolución de QUIÉN recibe la notificación debe vivir en el backend, que conoce el directorio (fuente de verdad de roles/emails) y el sector del incidente, y luego indicarle a N8N los destinatarios resueltos.

## What Changes

- El backend resuelve los destinatarios de la notificación de revisión humana desde `directorio_empleado`: empleados ACTIVOS con `rol=operador` cuyo sector coincide con el sector predicho principal del incidente.
- La respuesta de alta (`POST /api/v1/incidentes`) expone `destinatarios_revision` (lista de emails), poblada solo cuando `requiere_revision_humana=true`. El contrato elegido (respuesta de alta vs webhook de notificación) y su alternativa rechazada se documentan en `design.md` D2.
- N8N `Notificar operador designado` envía una copia a cada destinatario resuelto. Si la lista llega vacía (directorio vacío, sin operador del sector, o backend previo a c-56), cae al fallback actual `$env.OPERATOR_EMAIL` (un único destinatario): el camino de un solo destinatario se preserva.
- Un correo por destinatario; NUNCA se expone la lista completa en un `To`/`Cc` compartido (minimización de PII).
- Fire-and-forget intacto: la resolución es una lectura indexada acotada al caso de revisión y el envío del correo sigue ocurriendo en N8N después de la respuesta. No bloquea ni altera el alta.
- Sin migración Alembic: reutiliza `directorio_empleado` (c-54) y su seam de resolución; no agrega tablas ni columnas.

## Scope boundaries

- **NO es parte de c-55**: c-55 migra el TRANSPORTE de correo a IMAP/SMTP. c-56 cambia QUIÉN recibe la notificación, no cómo se envía.
- Fuera de alcance: sectores adicionales (solo el principal), notificar a `administrador_directorio` o `usuario_final`, UI de administración del directorio, SMS de telefonía (c-53, diferido), y el canal de confirmación al reportante (su destinatario es el remitente, no un rol).

## Capabilities

### New Capabilities

- `notification-routing`: resolución backend-side de destinatarios de notificación desde el directorio por rol y sector; precedencia del directorio sobre el fallback; contrato backend->n8n; un correo por destinatario; privacidad y no-bloqueo.

### Modified Capabilities

- `n8n-workflow`: el nodo `Notificar operador designado` deja de apuntar fijo a `$env.OPERATOR_EMAIL` y resuelve la lista de destinatarios desde el payload, con fallback al entorno; un envío por destinatario; `OPERATOR_EMAIL` pasa a ser exclusivamente el fallback.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `App/Backend/app/repositories/empleado_repository.py` | Modificado | Nuevo `listar_operadores_por_sector` (activos) |
| `App/Backend/app/services/notification_recipient_service.py` | Nuevo | Enumeración de operadores por sector, reutilizando el directorio c-54 |
| `App/Backend/app/services/incidente_service.py` | Modificado | Resolver destinatarios en el alta cuando hay revisión |
| `App/Backend/app/schemas/incidente.py` | Modificado | `destinatarios_revision` en la respuesta de alta |
| `n8n/workflow.json` | Modificado | Nodo `Preparar destinatarios de revision` (Code) + envío por destinatario |
| `App/Backend/tests/test_notification_recipients.py` | Nuevo | RED/GREEN de la resolución |
| `App/Backend/tests/test_n8n_workflow.py` | Modificado | Aserciones estructurales del cableado nuevo |
| `docs/n8n-workflow-guide.md`, `docs/openapi.json` | Modificado | Contrato, fallback, conteos |

## Risks

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| PII: emails de operadores cruzan a N8N (necesario para enviar) | Media | Canal autenticado, sin emails en logs ni auditoría, campo solo en revisión; governance ALTO |
| Regresión estructural N8N (c-38/c-40/c-53/c-55) | Media | Tests estructurales de no regresión sobre el workflow |
| Directorio vacío o desactualizado | Media | Fallback `$env.OPERATOR_EMAIL` preserva el comportamiento actual |
| `docs/openapi.json` desincronizado | Baja | Regenerar y correr `test_openapi_sync.py` |

## Rollback Plan

Revertir el commit: el backend deja de exponer/poblar `destinatarios_revision` y N8N vuelve a `$env.OPERATOR_EMAIL` (sin reimportar, el workflow previo se restaura con el revert). No hay migración ni backfill: los incidentes ya creados no se tocan.

## Dependencies

- `c-54-directorio-usuarios` (directorio, roles, sector, seam de resolución) — debe archivarse ANTES.
- `c-55-canal-correo-imap` (nodos `emailSend`/SMTP del operador) — antes.
- `c-53-notificacion-numero-incidente` (`numero_incidente` mostrado en la notificación) — antes.
- `c-38` (gate `Requiere revision humana`).

## Governance

**ALTO (HIGH)**: enruta notificaciones y hace cruzar emails (PII) al orquestador; requiere revisión humana antes de activar datos reales en el directorio.

## Success Criteria

- [ ] Con un operador activo en el sector X, un incidente del sector X que requiere revisión notifica a ese operador y NO al fallback.
- [ ] Sin operador del sector o con el directorio vacío, la notificación cae al fallback `$env.OPERATOR_EMAIL` (un destinatario).
- [ ] Un incidente sin revisión humana no dispara la notificación al operador.
- [ ] Se envía un correo por destinatario, sin exponer la lista completa entre destinatarios.
- [ ] `pytest tests/test_n8n_workflow.py` y `test_openapi_sync.py` en verde; `openspec validate --strict --changes c-56-notificaciones-por-rol` pasa.
- [ ] Smoke manual con la casilla Gmail de c-55 (manual): un incidente de revisión notifica al operador resuelto.
