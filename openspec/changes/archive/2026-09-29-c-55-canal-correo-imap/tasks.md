# Tasks: Migración del canal de correo a IMAP/SMTP

## 1. Prerrequisitos de proveedor (manual)

- [x] 1.1 Documentar casilla Gmail dedicada con 2FA y App Password (IMAP `imap.gmail.com:993` SSL, SMTP `smtp.gmail.com:465` SSL); verificar IMAP habilitado en la cuenta. Satisfecho: la casilla y su operación quedaron documentadas en `docs/n8n-workflow-guide.md`; IMAP/SMTP funcionan en runtime.
- [x] 1.2 Crear en n8n las credenciales `imap` y `smtp` (host, usuario, App Password); verificar que ambas conectan al probarlas. Satisfecho: credenciales `Mesa de Ayuda - IMAP` id `Shs4FcEo2YVhEXeZ` y `Mesa de Ayuda - SMTP` id `AzMbxBkG3wQ79k0s`; el correo real se recibió y la confirmación salió por SMTP.

## 2. Tests (RED)

- [x] 2.1 En `App/Backend/tests/test_n8n_workflow.py`: reemplazar constantes `microsoftOutlookTrigger` por `emailReadImap`, aserciones de trigger (`postProcessAction=read`, `format=simple`, `customEmailConfig` con `UNSEEN`+`SINCE`/24 h), ausencia de `microsoftOutlook*` y `Marcar correo como leido`, conteo 37. Verificar RED contra el workflow actual.
- [x] 2.2 En el mismo archivo: adaptar envíos a `n8n-nodes-base.emailSend` (asunto/texto/destino preservados, `credentials.smtp`), remitente `"Nombre <addr>"`, `origen_message_id` desde `metadata['message-id']` con fallback `attributes.uid`, `canal_raw="correo"` y descripción desde `textPlain`/`text`. Verificar RED.
- [x] 2.3 En `scripts/preflight/test_cost_readiness.py`: migrar la guarda a `emailReadImap` + `customEmailConfig` (SINCE/24 h) y neutralizar los tests de `Marcar correo como leido`. Verificar RED.

## 3. Workflow (GREEN)

- [x] 3.1 En `n8n/workflow.json`: reemplazar el trigger por `n8n-nodes-base.emailReadImap` con `mailbox=INBOX`, `postProcessAction=read`, `downloadAttachments=false`, `format=simple`, `customEmailConfig` `["UNSEEN",["SINCE","{{ $now.minus(24,'hours').toFormat('dd-LLL-yyyy') }}"]]`, `trackLastMessageId=true` y `credentials.imap`. Verificar 2.1.
- [x] 3.2 Reemplazar `Correo de confirmacion al usuario` y `Notificar operador designado` por `emailSend` conservando asunto/cuerpo/destinos; `fromEmail={{ $env.SMTP_FROM_EMAIL }}`, usuario `remitente || ''`, operador `{{ $env.OPERATOR_EMAIL }}`, `emailFormat=text`, `credentials.smtp`. Verificar 2.2.
- [x] 3.3 Eliminar `Marcar correo como leido` y rewiring: `Rutear por canal de origen[1]` solo a confirmación; `Es correo?[0]` terminal no-op y `[1]` a `Es web?`; sin destinos huérfanos. Verificar conteo 37. Verificar 2.1.
- [x] 3.4 Adaptar Code nodes: `canal_raw="correo"` explícito; remitente extraído entre `<>` validado con `EMAIL_RE`; `origen_message_id = metadata['message-id'] || String(attributes.uid)`; descripción `descripcion || textPlain || textHtml || text || body`. Verificar 2.2.

## 4. Guardas de preflight (GREEN)

- [x] 4.1 En `scripts/preflight/cost_readiness.py`: cambiar `OUTLOOK_TRIGGER_TYPE` a `emailReadImap`, reemplazar `readStatus`/`receivedDateTime` por `customEmailConfig` (`UNSEEN`+`SINCE`/24 h) y neutralizar `_check_mark_read_reachable`. Verificar 2.3.

## 5. Documentación

- [x] 5.1 En `docs/n8n-workflow-guide.md`: actualizar Decisión 1 (C-05) a IMAP elegido, tablas de nodos, ciclo de vida (marcado en trigger), conteo 37 y credenciales IMAP/SMTP Gmail + `SMTP_FROM_EMAIL`, sin secretos.
- [x] 5.2 Registrar como seguimiento separado la actualización de tesis, apuntando a la ruta real `docs/Tesis/v7/tesis_para_agente.md` (la de `config.yaml` no existe).

## 6. Verificación

- [x] 6.1 Ejecutar `pytest tests/test_n8n_workflow.py` en `App/Backend` y verificar verde.
- [x] 6.2 Ejecutar `pytest scripts/preflight/test_cost_readiness.py` y verificar verde offline.
- [x] 6.3 Smoke manual con el buzón Gmail real: un correo no leído de menos de 24 h crea incidente, dispara confirmación y queda leído (no reprocesa). Satisfecho: ejecución n8n #24 del workflow `JYizNfNZXuhCr8Z7` creó el incidente #9 el 2026-09-29T18:08:46Z; confirmación y notificación al operador enviadas; el trigger marcó leído y no reprocesó.
