## 1. Verificacion del delta contra el codigo mergeado

- [ ] 1.1 Confirmar que `scripts/up.sh` define `REQUIRED_SECRETS` con las cuatro variables (incluida `COST_GUARD_CALLER_HMAC_KEY`) y que `scripts/up.ps1` define `$RequiredSecrets` igual; verificar con `grep -n "REQUIRED_SECRETS\|RequiredSecrets" scripts/up.sh scripts/up.ps1`
- [ ] 1.2 Confirmar que `App/Backend/app/config/settings.py` declara `cost_guard_caller_hmac_key: str` sin default; verificar con `grep -n "cost_guard_caller_hmac_key" App/Backend/app/config/settings.py`
- [ ] 1.3 Confirmar que ambos scripts imprimen el recordatorio nuevo (IMAP, SMTP, login del operador, secreto del webhook de telefonia; Gemini en el `.env` del backend); verificar con `grep -n "telephony webhook secret\|webhook de telefonia" scripts/up.sh scripts/up.ps1`

## 2. Verificacion del delta en si

- [ ] 2.1 Confirmar que `specs/local-bootstrap/spec.md` contiene los dos requisitos bajo `## MODIFIED Requirements` con el encabezado textual `### Requirement: Preflight de entorno con fallo ruidoso` y `### Requirement: Recordatorio manual de configuracion de N8N`; verificar con `openspec validate c-125-delta-local-bootstrap-spec --strict`
- [ ] 2.2 Confirmar que cada escenario usa exactamente `#### Scenario:` y que cada requisito modificado tiene al menos un escenario; cubierto por el mismo `openspec validate --strict`

## 3. Sincronizacion del spec vivo

- [ ] 3.1 Aplicar el delta al spec vivo (`openspec/specs/local-bootstrap/spec.md`) al archivar el change o via `openspec sync`; verificar que los dos requisitos quedan actualizados y los otros cinco intactos
- [ ] 3.2 Verificar el spec vivo tras el sync con `openspec validate local-bootstrap --strict` (debe pasar)
- [ ] 3.3 Confirmar que no se modifico ningun archivo de codigo en el change; verificar con `git status --short` (solo artefactos bajo `openspec/`)
