## Why

`test_settings_tau_deriva_del_oof_del_corpus` (`evaluation/tests/test_umbral_settings_oof.py`) NO era hermético. Construía `Settings` desde el entorno del proceso con cuatro variables inyectadas vía `monkeypatch.setenv`, pero `Settings.cost_guard_caller_hmac_key` es un campo OBLIGATORIO (sin default, `App/Backend/app/config/settings.py:219`), introducido por c-66. El test dependía entonces de que `COST_GUARD_CALLER_HMAC_KEY` ya estuviera presente en el entorno: pasaba en CI (el job la define en `.github/workflows/ci.yml:51`) y fallaba localmente sin ella, con un `ValidationError` de pydantic (`cost_guard_caller_hmac_key Field required`). Un test que solo pasa por contaminación del entorno no verifica lo que dice verificar. Además, la lista "CI dummies" de `AGENTS.md` omitía esa misma variable, de modo que la documentación para agentes no reflejaba la configuración real de CI.

## What Changes

- Agregar `monkeypatch.setenv("COST_GUARD_CALLER_HMAC_KEY", "dummy-cost-guard-caller-hmac-key")` en `test_settings_tau_deriva_del_oof_del_corpus`, junto a las otras cuatro variables ya inyectadas, para que el test sea autocontenido.
- Agregar la variable `COST_GUARD_CALLER_HMAC_KEY` a la lista "CI dummies" del bloque "Env Vars and Secrets" de `AGENTS.md`, alineándola con lo que el job de CI realmente provee.
- Sin cambio de comportamiento de producción y sin cambio de contrato observable: es un ajuste de hermeticidad de test y de documentación de agente.

### Non-goals (fuera de alcance)

- NO se le da valor por defecto a `cost_guard_caller_hmac_key` ni se relaja su obligatoriedad: el campo DEBE seguir siendo obligatorio.
- NO se modifica ningún otro test de la suite de evaluación ni de backend.
- NO se corrige en este change la omisión de `JWT_SECRET_KEY` en la lista "CI dummies" de `AGENTS.md` (hueco preexistente, no introducido por c-100; se registra como observación).

## Capabilities

### New Capabilities

- Ninguna. El change no introduce capacidad ni comportamiento observable nuevo.

### Modified Capabilities

- Ninguna. Ningún requisito de spec cambia: se trata de hermeticidad de un test y de documentación de agente, no de comportamiento del sistema. Por eso este change NO produce delta spec y su `.openspec.yaml` declara `skip_specs: true` (el único caso permitido para un change de cero deltas, según la regla de validación del schema).

## Impact

- **Test de evaluación**: `evaluation/tests/test_umbral_settings_oof.py` (`test_settings_tau_deriva_del_oof_del_corpus`).
- **Documentación de agente**: `AGENTS.md` (bloque "CI dummies" en "Env Vars and Secrets").
- **Referencia (sin cambios)**: `App/Backend/app/config/settings.py`, `.github/workflows/ci.yml`.
- **Sin cambios**: código de producción, clasificador, API, esquema de base de datos, workflow N8N.

## Governance: BAJO

Cambio de tooling de test y documentación, sin impacto en producción ni en datos. No toca autenticación, facturación, seguridad ni inyección en archivos del usuario. Se implementa con autonomía plena y se reporta la evidencia de la suite.
