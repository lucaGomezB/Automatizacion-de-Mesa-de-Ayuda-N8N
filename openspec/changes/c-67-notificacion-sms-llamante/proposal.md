## Why

El canal de telefonía NO notifica al llamante el número de incidente. El `<Say>` de cierre del TwiML desconoce el número porque el alta del incidente es asíncrona y la salida de telefonía del workflow no tiene sucesor de notificación. Además, el webhook de VOZ es el único punto donde el proveedor provee el `From`; el callback de estado de grabación NO lo trae, de modo que hoy el número llamante no se persiste y no hay forma de notificar al llamante.

Este alcance se separó de `c-53-notificacion-numero-incidente` porque su habilitación está **bloqueada por OQ3** (entregabilidad de Twilio SMS a Argentina +54, bajo un spike externo en curso) y porque el manejo del número llamante y el marco de consentimiento/transferencia internacional son **propiedad del change `C-66` (privacidad-transferencias)**, que aún no existe. `c-67` CONSUME ese marco; no lo redefine.

## What Changes

- **Telefonía**: SMS al número llamante con el número de incidente, vía Twilio Messaging. Se captura y persiste el `From` en el webhook de VOZ (correlacionado por `CallSid`), porque el callback de estado de grabación NO lo trae y el pipeline es asíncrono. Sin número: no se envía y se registra el evento. El SMS se reserva en la guarda de costo como superficie nueva `twilio_sms`.
- **Privacidad (consumida de `C-66`)**: la base de licitud del tratamiento del número llamante, su minimización y el instrumento de transferencia internacional los define/provee `C-66` (privacidad-transferencias). Estados Unidos NO es un país con nivel adecuado de protección, por lo que la transferencia al proveedor de mensajería requiere el instrumento que provea `C-66`. `c-67` MUST NOT redefinir ese marco.

## Capabilities

### New Capabilities

- `incident-notification`: porción de SMS del contrato de entrega del número de incidente al usuario final (canal telefonía), incluida la captura y persistencia cifrada del llamante en el webhook de voz, el comportamiento ante número ausente y la base de licitud/minimización del SMS (consumida de `C-66`).

### Modified Capabilities

- `runtime-cost-guard`: nueva superficie paga `twilio_sms`, reservada antes de enviar el SMS, con costo unitario configurable y dentro de la bolsa global y el rate por origen.
- `n8n-workflow`: la confirmación telefónica no se resuelve por TwiML; el workflow solo garantiza la rama de telefonía que dispara el alta con `origen_message_id = CallSid` (ya existente), y la notificación SMS la realiza el backend.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `App/Backend/app/cost_guard/constants.py`, `config.py` | Modified | Superficie `twilio_sms` y su costo unitario |
| `App/Backend/app/config/settings.py`, `.env.example` | Modified | Credenciales/remitente SMS y costo unitario |
| `App/Backend/app/clients/twilio_sms.py` | New | Cliente de Twilio Messaging (envío de SMS) |
| `App/Backend/app/routes/cost_guard.py` | Modified | El webhook de voz persiste `CallSid` + `From` (correlación para el SMS) |
| `App/Backend/app/models/telefonia_ingreso.py` | Modified | Upsert de la fila de ingreso en el webhook de voz (caller antes del callback) |
| `App/Backend/app/repositories/telefonia_ingreso_repository.py` | Modified | Búsqueda/creación por `CallSid` desde el webhook de voz |
| `App/Backend/app/services/telefonia_notification_service.py` | New | Resolución del llamante y envío del SMS con guarda de costo |
| `App/Backend/app/services/incidente_service.py` | Modified | Notificación SMS fire-and-forget al crear un incidente de telefonía |
| `openspec/specs/*` | Modified | Deltas de las capacidades |

## Open Questions

1. **OQ3 — Entregabilidad del SMS a Argentina (ABIERTA)**: la entregabilidad de Twilio SMS a +54 está bajo un spike externo. Todo este change queda BLOQUEADO hasta que el spike devuelva resultado.
2. **C-66 — Marco de privacidad**: la base de licitud, la minimización y el instrumento de transferencia internacional son provistos por `C-66` (privacidad-transferencias), que aún no existe. `c-67` depende de su definición.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SMS no entregable a +54 (OQ3) | High | Bloqueo explícito: no se habilita el envío hasta cerrar el spike |
| Transferencia internacional sin instrumento (C-66 inexistente) | High | Dependencia declarada de `C-66`; no se habilita credencial real sin el instrumento |
| SMS a número inválido o ausente | Med | No enviar sin `From`; log estructurado; guarda de rate por origen |
| Envío duplicado de SMS | Low | Idempotencia por `CallSid`/`incidente_id`; reserva y envío dentro de la misma tarea |
| Fuga de PII (teléfono) | Med | Número cifrado at-rest; nunca en query string ni en auditoría |

## Rollback Plan

Revertir el commit elimina el cliente y el servicio de SMS, revierte la superficie `twilio_sms` y el upsert del caller en el webhook de voz. Si se modificó el esquema de `telefonia_ingreso`, revertir la migración con `alembic downgrade -1`. No hay backfill: los incidentes ya creados no se tocan y los SMS no son recuperables.

## Success Criteria

- [ ] La telefonía envía un SMS al llamante con el número de incidente; sin número, no envía y deja traza.
- [ ] El costo del SMS se reserva en la guarda antes del envío y es configurable.
- [ ] El marco de licitud/minimización y el instrumento de transferencia internacional provistos por `C-66` se consumen sin redefinirse.
- [ ] `openspec validate --strict --changes c-67-notificacion-sms-llamante` pasa.

## Governance

- **Governance**: ALTO (datos personales — Ley 25.326; mensajería saliente paga; transferencia internacional de datos).
