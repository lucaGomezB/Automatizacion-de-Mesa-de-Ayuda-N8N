## Why

El spec vivo de `local-bootstrap` quedo desactualizado respecto del codigo tras el merge del PR #36 (commit `5de674d`, ya en `main`). El codigo es el estado final: el spec debe reflejarlo. Dos requisitos divergen del comportamiento real de `scripts/up.sh` y `scripts/up.ps1`. Es un cambio DOC-ONLY: no toca codigo, solo la especificacion.

## What Changes

- **Requisito "Preflight de entorno con fallo ruidoso"**: el preflight verifica ahora CUATRO secretos requeridos, no tres. Se agrega `COST_GUARD_CALLER_HMAC_KEY` (obligatoria desde c-66: `App/Backend/app/config/settings.py` la declara sin default; el PR #36 la incorporo al preflight). **BREAKING** en terminos de contrato de spec (cambia el conjunto de variables exigidas).
- **Requisito "Recordatorio manual de configuracion de N8N"**: la salida ya no menciona "Outlook, Twilio y Gemini". Ahora indica crear las credenciales de N8N IMAP, SMTP, login del operador y secreto del webhook de telefonia (ver `docs/n8n-workflow-guide.md`), y aclara que Gemini se configura en el `.env` del backend, no en N8N.
- Sin cambios de codigo.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `local-bootstrap`: se actualizan dos requisitos (preflight de entorno y recordatorio manual de N8N) para alinearlos con el codigo mergeado.

## Impact

- `openspec/specs/local-bootstrap/spec.md` — spec vivo (se sincroniza al archivar).
- `openspec/changes/c-125-delta-local-bootstrap-spec/specs/local-bootstrap/spec.md` — delta de este change.
- Sin cambios en `scripts/up.sh`, `scripts/up.ps1` ni en el resto del arbol versionado.
