# Proposal: Migración del canal de correo a IMAP/SMTP

## Why

El canal de correo depende de Microsoft Entra OAuth2 (`microsoftOutlookTrigger`, `microsoftOutlook`, credencial `microsoftOutlookOAuth2Api`), vía no provisionable: la cuenta Microsoft disponible es personal y sin tenant, y los registros Azure no están accesibles. El canal queda indeployable y la tesis lo marca PARCIAL. IMAP/SMTP con App Password de Gmail da equivalencia funcional sin registro de app en la nube, alineado con "Decisión 1 — C-05" de `docs/n8n-workflow-guide.md`.

## What Changes

- **BREAKING** (contrato del workflow exportado): el trigger `Llega un email a Mesa de Ayuda` pasa de `microsoftOutlookTrigger` a `n8n-nodes-base.emailReadImap` (Action = Mark as Read), conservando filtro de no leídos y lookback de 24 h.
- `Correo de confirmacion al usuario` y `Notificar operador designado` pasan a `n8n-nodes-base.emailSend` (SMTP).
- Se elimina `Marcar correo como leido` (el trigger IMAP marca leído).
- Los Code nodes que parsean `from.emailAddress`, `bodyPreview`, `receivedDateTime` se adaptan a campos IMAP (`from`, `text`, `date`).
- Credencial IMAP/SMTP Gmail, sin secretos versionados.
- Actualizar `docs/n8n-workflow-guide.md` (Decisión 1 / C-05, tablas, credenciales), la referencia de tesis (`docs/Tesis/tesis_para_agente.md` / Anexo E) si aplica, y `App/Backend/tests/test_n8n_workflow.py`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `n8n-workflow`: cambian los requisitos del canal de correo — trigger, nodos de envío, ciclo "marcar como leído", lookback, parsing, credenciales y conteos documentados.

`n8n-notification` NO cambia: gobierna la notificación backend→N8N (webhook y payload), no el transporte de correo.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `n8n/workflow.json` | Modificado | Trigger IMAP, dos `emailSend`, baja del nodo de marca, parsing |
| `docs/n8n-workflow-guide.md` | Modificado | Decisión 1 / C-05, tablas, credenciales |
| `docs/Tesis/tesis_para_agente.md` | Condicional | Anexo E / canal correo |
| `App/Backend/tests/test_n8n_workflow.py` | Modificado | Tipos de nodo y aserciones |
| Backend FastAPI | Sin cambios | Contrato de persistencia intacto |

## Risks

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Campos IMAP vs Outlook rompen parsing | Media | Tests estructurales + smoke manual |
| Conteos de nodos/pruebas desincronizados | Media | Actualizar la guía en el mismo commit |

## Rollback Plan

`git revert` del commit: restaura `workflow.json`, la guía y los tests al estado Outlook. Sin migraciones ni cambios de API, no hay rollback de backend. La credencial Outlook se conserva hasta validar el smoke de IMAP.

## Dependencies

- Casilla Gmail dedicada con 2FA y App Password (IMAP `imap.gmail.com:993`, SMTP `smtp.gmail.com:465`, ambos SSL). Solo se documenta. Sin secretos versionados.

## Success Criteria

- [ ] `n8n/workflow.json`: un `emailReadImap`, dos `emailSend`, sin nodos `microsoftOutlook*` ni `Marcar correo como leido`.
- [ ] `pytest tests/test_n8n_workflow.py` en verde.
- [ ] La guía declara conteos coincidentes con el workflow y la suite.
- [ ] Smoke manual: un correo no leído de menos de 24 h crea incidente, envía confirmación y queda leído.
