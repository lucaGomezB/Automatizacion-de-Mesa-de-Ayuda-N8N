# Design: Migración del canal de correo a IMAP/SMTP

## Context

Ver `proposal.md` — Why. Hoy: `microsoftOutlookTrigger` (`readStatus=unread` + `receivedDateTime ge now-24h`, `output=fields`) y tres `microsoftOutlook`. El normalizador resuelve `origen_message_id = item.json.id`, `descripcion = item.json.body || item.json.text` y `remitente` desde `from` string u objeto `from.emailAddress.address`. `Marcar correo como leido` se alcanza desde `Rutear por canal de origen[1]` y `Es correo?[0]`.

Contratos verificados contra n8n (no supuestos):
- `n8n-nodes-base.emailReadImap` v2.x: credencial `imap`; params `mailbox`, `postProcessAction` (`read|nothing`), `downloadAttachments`, `format` (`simple|raw|resolved`), `options.customEmailConfig` (JSON, default `["UNSEEN"]`), `options.trackLastMessageId` (default true). Formato `simple` emite: `textHtml`, `textPlain`, `attributes.uid`, `metadata` (headers no top-level) y headers top-level `cc|date|from|subject|to`. **No emite `id`**; `from` es el header decodificado `"Nombre <addr>"`.
- `n8n-nodes-base.emailSend` v2.x: credencial `smtp`; params `fromEmail`, `toEmail`, `subject`, `emailFormat` (`text|html|both`), `text`, `html`, `options`.
- Los headers IMAP de `metadata` van en minúsculas (libmime); `Message-ID` → `metadata['message-id']`.

## Goals / Non-Goals

**Goals:** trigger IMAP con lookback de 24 h y marcado automático; dos envíos SMTP; normalizador adaptado a los campos IMAP; conteos y tests sincronizados.

**Non-Goals:** cambios de backend/API (el contrato de `origen_message_id` no cambia); adjuntos; SMS de telefonía; reescritura del arnés de dry-run.

## Decisions

### D1 — Trigger: `emailReadImap`, formato `simple`

| Opción | Trade-off | Decisión |
|--------|-----------|----------|
| `format=resolved` | mailparser: `from.value[0].address` estructurado, pero descarga el source completo y adjuntos | Rechazada |
| `format=simple` | Liviano, `textPlain`/`textHtml` listos; `from` es string a parsear | **Elegida** |

Params: `mailbox: "INBOX"`, `postProcessAction: "read"`, `downloadAttachments: false`, `format: "simple"`, `options.customEmailConfig: "=[\"UNSEEN\", [\"SINCE\", \"{{ $now.minus(24, 'hours').toFormat('dd-LLL-yyyy') }}\"]]"`, `options.trackLastMessageId: true`. `SINCE` es diario (no por instante); la dedupe fina la aportan `UNSEEN` + `\\SEEN` + watermark UID.

### D2 — Envíos: `emailSend` (SMTP, `emailFormat=text`)

`Correo de confirmacion al usuario`: `fromEmail: "={{ $env.SMTP_FROM_EMAIL }}"`, `toEmail: "={{ $('Normalizar entrada del incidente').item.json.remitente || '' }}"`, `subject`, `text` (mismo texto actual). `Notificar operador designado`: `toEmail: "={{ $env.OPERATOR_EMAIL }}"`. Se documenta `SMTP_FROM_EMAIL` (sin secreto) en la guía y el entorno de n8n.

### D3 — Remitente: parsear `"Nombre <addr>"`

`normalizarRemitente` ya acepta string simple y objeto. Se agrega extracción del address entre `<>` (regex) antes de validar con `EMAIL_RE`; si no hay `<>`, cae al string desnudo. Un `from` sin address válido se descarta con la señal observable existente.

### D4 — `origen_message_id`: `metadata['message-id']` con fallback `uid`

En la rama correo: `item.json.metadata?.['message-id'] || (item.json.attributes?.uid != null ? String(item.json.attributes.uid) : null)`. Preserva la semántica idempotente del Message-ID; el UID evita null cuando el header falta. `item.json.id` deja de existir.

### D5 — Descripción: añadir `textPlain`/`textHtml`

Cadena correo: `item.json.descripcion || item.json.textPlain || item.json.textHtml || item.json.text || item.json.body || ''`.

### D6 — Ciclo "marcar como leído": eliminar nodo y destino huérfano

Se elimina `Marcar correo como leido`. `Rutear por canal de origen[1]` queda con `Correo de confirmacion al usuario` (se quita la lista compartida). `Es correo?[0]` (true) queda **sin destino** (terminal no-op: el trigger ya aplicó `\\SEEN`); `[1]` conserva `Es web?`. Conteo 38 → 37 (34 operativos + 3 sticky). Rechazada: eliminar también `Es correo?` (daría 36 y rompe el contrato del proposal).

### D7 — Credenciales y guardas

Los nodos declaran `credentials.imap` / `credentials.smtp` (id+nombre, nunca secretos). `microsoftOutlookOAuth2Api` se conserva hasta validar el smoke. `scripts/preflight/cost_readiness.py` fija `OUTLOOK_TRIGGER_TYPE` y valida `receivedDateTime`/`readStatus`, y `_check_mark_read_reachable`: ambos deben migrar a `emailReadImap` + `customEmailConfig` (`SINCE` + `hours`) y neutralizarse. `scripts/preflight/test_cost_readiness.py` también.

## Risks / Trade-offs

- [`SINCE` diario vs lookback exacto] → `UNSEEN` + `\\SEEN` + watermark UID.
- [Gmail exige App Password y IMAP habilitado] → documentado; la cuenta dedicada es prerequisito.
- [Parsing de `from` con display-name codificado o multi-address] → regex `<>` + validación fail-safe.
- [Guardas preflight desincronizadas] → incluidas en el mismo cambio.

## File Changes

| File | Acción | Descripción |
|------|--------|-------------|
| `n8n/workflow.json` | Modificar | Trigger IMAP, 2 `emailSend`, baja de mark-read, rewiring, normalizador |
| `App/Backend/tests/test_n8n_workflow.py` | Modificar | Constantes/tipos, parámetros IMAP/SMTP, remitente y `origen_message_id`, conteo 37, ausencia de `microsoftOutlook*` |
| `scripts/preflight/cost_readiness.py` | Modificar | Guardas del trigger y mark-read |
| `scripts/preflight/test_cost_readiness.py` | Modificar | Tests de esas guardas |
| `docs/n8n-workflow-guide.md` | Modificar | Decisión 1 (IMAP como elegido), tablas, ciclo de vida, conteos, `SMTP_FROM_EMAIL` |
| `docs/Tesis/tesis_para_agente.md` | No aplica | La ruta no existe (solo `docs/Tesis/v7/tesis_para_agente.md`); seguimiento separado |

## Testing Strategy

| Layer | Qué | Cómo |
|-------|-----|------|
| Unit/estructural (pytest offline) | Tipos IMAP/SMTP, params, normalizador, conteo, sin Outlook | `pytest tests/test_n8n_workflow.py` + `pytest scripts/preflight/test_cost_readiness.py` |
| Smoke manual | Correo < 24 h crea incidente, confirma y queda leído | Buzón Gmail real |

## Migration / Rollout

`git revert` restaura el estado Outlook (sin migración de datos/API). La credencial Outlook se conserva hasta el smoke verde. Verificación: suite estructural + preflight en verde, luego smoke manual.

## Open Questions

- Ninguna que bloquee el diseño. Queda como seguimiento no bloqueante decidir si `Es correo?` se colapsa en un change posterior (36 nodos).
