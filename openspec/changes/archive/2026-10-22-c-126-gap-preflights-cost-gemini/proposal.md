## Why

El spec vivo de `local-bootstrap` representa 7 requisitos, pero NO representa dos gates que el arranque local ejecuta en su punto de entrada antes de tocar Docker: el preflight de preparacion de costo (`check_cost_preflight`) y el preflight de preparacion de Gemini (`check_gemini_preflight`). Ambos estan implementados y cableados en `scripts/up.sh` (`main`, invocados tras el preflight de entorno y antes de `ensure_certificates`) y en su par `scripts/up.ps1` (`Invoke-CostPreflight`, `Invoke-GeminiPreflight`), y ambos bloquean el arranque con exit code distinto de cero si fallan. Es un GAP de especificacion: el codigo ya es el estado final y el spec debe reflejarlo. Es un cambio DOC-ONLY (specs): no toca codigo.

## What Changes

- **Capacidad `local-bootstrap`**: se AGREGAN dos requisitos que hoy no existen en el spec.
  - `Preflight de preparacion de costo antes del arranque`: verificacion estatica de las guardas de costo cableadas en `n8n/workflow.json` y `docker-compose.yml`; su fallo NO arranca el stack (exit distinto de cero); bypass unico y ruidoso `UP_SKIP_COST_PREFLIGHT=1`; sin red ni credenciales y nunca imprime secretos.
  - `Preflight de preparacion de Gemini antes del arranque`: verificacion estatica de la superficie Gemini del workflow (modelo pineado + reintento acotado del agente); su fallo NO arranca el stack; bypass unico y ruidoso `UP_SKIP_GEMINI_PREFLIGHT=1`; sin red y nunca lee ni imprime `GEMINI_API_KEY`.
  - Ambos gates se especifican preservando la equivalencia multiplataforma (`scripts/up.sh` + `scripts/up.ps1`).
- Sin cambios de codigo.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `local-bootstrap`: se AGREGAN dos requisitos (preflight de costo y preflight de Gemini) que representan gates ya implementados pero no especificados.

## Impact

- `openspec/changes/c-126-gap-preflights-cost-gemini/specs/local-bootstrap/spec.md` — delta de este change (`## ADDED Requirements`).
- `openspec/specs/local-bootstrap/spec.md` — spec vivo (se sincroniza al archivar).
- Sin cambios en `scripts/up.sh`, `scripts/up.ps1`, `scripts/preflight/*` ni en el resto del arbol versionado.
