## 1. Verificar el delta contra el codigo existente

- [ ] 1.1 Confirmar en `scripts/up.sh` que `check_cost_preflight` y `check_gemini_preflight` existen y que `main` los invoca despues de `check_env_file` y antes de `ensure_certificates`; verificar con `grep -n "check_env_file\|check_cost_preflight\|check_gemini_preflight\|ensure_certificates" scripts/up.sh` y revisando el orden de `main`.
- [ ] 1.2 Confirmar en `scripts/up.ps1` que `Invoke-CostPreflight` e `Invoke-GeminiPreflight` existen y que el bloque de entrada los invoca despues de `Test-EnvPreflight` y antes de `Invoke-EnsureCertificates`; verificar con `grep -n "Test-EnvPreflight\|Invoke-CostPreflight\|Invoke-GeminiPreflight\|Invoke-EnsureCertificates" scripts/up.ps1`.
- [ ] 1.3 Confirmar el contrato de salida de `scripts/preflight/cost_readiness.py` y `scripts/preflight/gemini_readiness.py`: `exit_code` es 0 si y solo si todos los checks estan en PASS, sin red y sin leer secretos; verificar leyendo `exit_code`/`main` y ejecutando `python3 scripts/preflight/cost_readiness.py; echo $?` y `python3 scripts/preflight/gemini_readiness.py; echo $?`.
- [ ] 1.4 Confirmar los bypass `UP_SKIP_COST_PREFLIGHT=1` y `UP_SKIP_GEMINI_PREFLIGHT=1` con advertencia explicita en ambos scripts; verificar con `grep -n "UP_SKIP_COST_PREFLIGHT\|UP_SKIP_GEMINI_PREFLIGHT" scripts/up.sh scripts/up.ps1`.

## 2. Verificar el delta de especificacion

- [ ] 2.1 Confirmar que el delta contiene exactamente dos requisitos bajo `## ADDED Requirements` con los encabezados esperados y sin `## Purpose` (capacidad existente); verificar con `grep -n "^## \|^### Requirement:" openspec/changes/c-126-gap-preflights-cost-gemini/specs/local-bootstrap/spec.md`.
- [ ] 2.2 Confirmar que cada requisito tiene al menos un escenario y que todos usan exactamente cuatro almohadillas; verificar con `grep -c "^#### Scenario:" openspec/changes/c-126-gap-preflights-cost-gemini/specs/local-bootstrap/spec.md` (esperado: 10 escenarios, 5 por requisito).
- [ ] 2.3 Confirmar que el delta no usa `MODIFIED`, `REMOVED` ni `RENAMED`; verificar con `grep -n "MODIFIED\|REMOVED\|RENAMED" openspec/changes/c-126-gap-preflights-cost-gemini/specs/local-bootstrap/spec.md` (sin resultados).

## 3. Sincronizar el spec vivo

- [ ] 3.1 Aplicar el delta al spec vivo `openspec/specs/local-bootstrap/spec.md` al archivar o por sincronizacion; verificar que los dos requisitos nuevos quedan agregados y que los 7 existentes permanecen intactos (`grep -c "^### Requirement:" openspec/specs/local-bootstrap/spec.md` pasa de 7 a 9).
- [ ] 3.2 Validar el spec vivo con `openspec validate local-bootstrap --strict` y confirmar PASS.
- [ ] 3.3 Confirmar que el change solo modifico artefactos bajo `openspec/`; verificar con `git status --porcelain` (sin cambios en `scripts/`, `App/`, `n8n/` ni `docker-compose.yml`).
