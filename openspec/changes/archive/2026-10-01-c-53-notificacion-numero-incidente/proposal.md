## Why

El usuario final NO recibe de forma garantizada el número de incidente en los canales de correo y formulario web. El canal de correo no confirma cuando `requiere_revision_humana=true` y su destinatario puede resolverse inválido (el `from` de Outlook es típicamente un objeto `from.emailAddress.address`); el formulario web responde `incidente_id: null` en la rama de revisión humana. Tampoco existe un número legible de incidente: solo el PK `id` (el frontend lo padea a 5 dígitos y n8n consume `$json.id`), y el prefijo configurable que menciona la tesis nunca se implementó. La documentación afirma además una confirmación telefónica por TwiML que no ocurre.

El alcance de SMS al llamante (telefonía) se movió a `c-67-notificacion-sms-llamante` (dependiente de OQ3 y C-66).

## What Changes

- **Correo**: se corrige la extracción del remitente (soportar `from` string y objeto `from.emailAddress.address`) y se dispara el correo de confirmación también en la rama `requiere_revision_humana=true`.
- **Web**: la rama de revisión humana responde con el `incidente_id` real del incidente creado (no `null`); se conserva la respuesta síncrona.
- **Número de incidente**: se usa el PK `id` como número canónico; el prefijo configurable queda diferido (Open Question 1 del design).
- **Doc fix**: `docs/n8n-workflow-guide.md` deja de afirmar que la telefonía confirma por TwiML.

## Capabilities

### New Capabilities

- `incident-notification`: contrato de entrega del número de incidente al usuario final en los canales de correo y formulario web, incluida la resolución del destinatario de correo, la garantía de entrega también en revisión humana, y el comportamiento ante contacto ausente.

### Modified Capabilities

- `n8n-workflow`: el correo de confirmación se dispara también en revisión humana y resuelve el remitente desde el objeto `from`; la respuesta web de la rama de revisión humana incluye el `incidente_id`; la confirmación telefónica no se resuelve por TwiML; la guía del workflow refleja el estado real.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `n8n/workflow.json` | Modified | Disparo de confirmación de correo en revisión humana, extracción del `from` objeto, respuesta web de revisión humana con `incidente_id` |
| `App/Backend/app/schemas/*` | Modified | Campo de respuesta `numero_incidente` (número canónico) |
| `docs/n8n-workflow-guide.md`, `docs/openapi.json` | Modified | Doc fix y contrato sincronizado |
| `openspec/specs/*` | Modified | Deltas de las capacidades |

## Open Questions

1. **Número de incidente**: ¿se adopta el PK `id` (recomendado) o se agrega un número de negocio con prefijo configurable? Ver design.md D1.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Regresión de C-46/C-47/C-52 en el grafo N8N | Med | Pruebas estructurales de no regresión sobre el workflow |

## Rollback Plan

Revertir el commit restaura el `n8n/workflow.json` previo (reimportar en N8N desactiva las confirmaciones nuevas) y revierte el campo de respuesta `numero_incidente`. No hay backfill: los incidentes ya creados no se tocan. Los tests estructurales del workflow vuelven a su baseline.

## Success Criteria

- [x] El correo resuelve un destinatario válido desde el `from` objeto y el string.
- [x] La rama de revisión humana del canal web responde con el número de incidente creado.
- [x] El número de incidente canónico (`numero_incidente`) se expone en el contrato de alta. Commit `a7f9477`.
- [x] `openspec validate --strict --changes c-53-notificacion-numero-incidente` pasa.
