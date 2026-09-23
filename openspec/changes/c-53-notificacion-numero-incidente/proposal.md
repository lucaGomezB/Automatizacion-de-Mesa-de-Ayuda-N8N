## Why

El usuario final NO recibe de forma garantizada el número de incidente. El canal de correo no confirma cuando `requiere_revision_humana=true` y su destinatario puede resolverse inválido (el `from` de Outlook es típicamente un objeto `from.emailAddress.address`); el formulario web responde `incidente_id: null` en la rama de revisión humana; y la telefonía NO notifica: la salida de telefonía del switch no tiene sucesor y el `<Say>` de cierre no conoce el número porque el alta es asíncrona. Tampoco existe un número legible de incidente: solo el PK `id` (el frontend lo padea a 5 dígitos y n8n consume `$json.id`), y el prefijo configurable que menciona la tesis nunca se implementó. La documentación afirma además una confirmación telefónica por TwiML que no ocurre.

## What Changes

- **Telefonía**: SMS al número llamante con el número de incidente, vía Twilio Messaging. Se captura y persiste el `From` en el webhook de VOZ (correlacionado por `CallSid`), porque el callback de estado de grabación NO lo trae y el pipeline es asíncrono. Sin número: no se envía y se registra el evento. El SMS se reserva en la guarda de costo como superficie nueva `twilio_sms`.
- **Correo**: se corrige la extracción del remitente (soportar `from` string y objeto `from.emailAddress.address`) y se dispara el correo de confirmación también en la rama `requiere_revision_humana=true`.
- **Web**: la rama de revisión humana responde con el `incidente_id` real del incidente creado (no `null`); se conserva la respuesta síncrona.
- **Número de incidente**: se usa el PK `id` como número canónico; el prefijo configurable queda diferido (Open Question 1 del design).
- **Doc fix**: `docs/n8n-workflow-guide.md` deja de afirmar que la telefonía confirma por TwiML.

## Capabilities

### New Capabilities

- `incident-notification`: contrato de entrega del número de incidente al usuario final en los tres canales (correo, web, telefonía por SMS), incluida la captura y persistencia cifrada del llamante en el webhook de voz, la resolución del destinatario de correo, la garantía de entrega también en revisión humana, y el comportamiento ante número ausente.

### Modified Capabilities

- `n8n-workflow`: la confirmación telefónica deja de resolverse por TwiML y pasa a ser SMS; el correo de confirmación se dispara también en revisión humana y resuelve el remitente desde el objeto `from`; la respuesta web de la rama de revisión humana incluye el `incidente_id`; la guía del workflow refleja el estado real.
- `runtime-cost-guard`: nueva superficie paga `twilio_sms`, reservada antes de enviar el SMS, con costo unitario configurable y dentro de la bolsa global y el rate por origen.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `n8n/workflow.json` | Modified | Disparo de confirmación de correo en revisión humana, extracción del `from` objeto, respuesta web de revisión humana con `incidente_id` |
| `App/Backend/app/routes/cost_guard.py` | Modified | El webhook de voz persiste `CallSid` + `From` (correlación para el SMS) |
| `App/Backend/app/models/telefonia_ingreso.py` | Modified | Upsert de la fila de ingreso en el webhook de voz (caller antes del callback) |
| `App/Backend/app/repositories/telefonia_ingreso_repository.py` | Modified | Búsqueda/creación por `CallSid` desde el webhook de voz |
| `App/Backend/app/services/incidente_service.py` | Modified | Notificación SMS fire-and-forget al crear un incidente de telefonía |
| `App/Backend/app/clients/twilio_sms.py` | New | Cliente de Twilio Messaging (envío de SMS) |
| `App/Backend/app/services/telefonia_notification_service.py` | New | Resolución del llamante y envío del SMS con guarda de costo |
| `App/Backend/app/cost_guard/constants.py`, `config.py` | Modified | Superficie `twilio_sms` y su costo unitario |
| `App/Backend/app/config/settings.py`, `.env.example` | Modified | Credenciales/remitente SMS y costo unitario |
| `docs/n8n-workflow-guide.md`, `docs/openapi.json` | Modified | Doc fix y contrato sincronizado |
| `openspec/specs/*` | Modified | Deltas de las dos capacidades |

## Open Questions

1. **Número de incidente**: ¿se adopta el PK `id` (recomendado) o se agrega un número de negocio con prefijo configurable? Ver design.md D1.
2. **Consentimiento y costo del SMS (Ley 25.326)**: confirmar la postura transaccional y el tope de gasto. Ver design.md D5/D6.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SMS a número inválido o ausente | Med | No enviar sin `From`; log estructurado; guarda de rate por origen |
| Envío duplicado de SMS | Low | Idempotencia por `CallSid`/`incidente_id`; reserva y envío dentro de la misma tarea |
| Regresión de C-46/C-47/C-52 en el grafo N8N | Med | Pruebas estructurales de no regresión sobre el workflow |
| Fuga de PII (teléfono) | Med | Número cifrado at-rest; nunca en query string ni en auditoría |
| PII al proveedor SMS | Low | Twilio ya es proveedor autorizado del canal de voz |

## Rollback Plan

Revertir el commit restaura el `n8n/workflow.json` previo (reimportar en N8N desactiva el SMS y las confirmaciones nuevas), elimina el cliente y el servicio de SMS y revierte la superficie `twilio_sms`. Si se modificó el esquema de `telefonia_ingreso`, revertir la migración con `alembic downgrade -1`. No hay backfill: los incidentes ya creados no se tocan y los SMS no son recuperables. Los tests estructurales del workflow vuelven a su baseline.

## Success Criteria

- [ ] Los tres canales entregan el número de incidente al usuario final, incluida la rama de revisión humana.
- [ ] El correo resuelve un destinatario válido desde el `from` objeto y el string.
- [ ] La telefonía envía un SMS al llamante con el número; sin número, no envía y deja traza.
- [ ] El costo del SMS se reserva en la guarda antes del envío y es configurable.
- [ ] `openspec validate --strict --changes c-53-notificacion-numero-incidente` pasa.