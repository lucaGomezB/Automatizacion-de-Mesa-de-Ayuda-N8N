## 1. Corrección de hermeticidad del test de evaluación

- [x] 1.1 Agregar `monkeypatch.setenv("COST_GUARD_CALLER_HMAC_KEY", "dummy-cost-guard-caller-hmac-key")` en `test_settings_tau_deriva_del_oof_del_corpus` (`evaluation/tests/test_umbral_settings_oof.py`), junto a las cuatro variables ya inyectadas. Verificación: el test pasa en aislamiento sin `COST_GUARD_CALLER_HMAC_KEY` en el entorno del proceso — `python3 -m pytest tests/test_umbral_settings_oof.py::test_settings_tau_deriva_del_oof_del_corpus -v` → PASSED.
- [x] 1.2 Confirmar que la suite de evaluación completa queda verde. Verificación: `cd evaluation; pytest -q` → **142 passed, 0 failed** (contra **141 passed, 1 failed** antes del fix; el fallo previo era `test_settings_tau_deriva_del_oof_del_corpus` con `pydantic ValidationError: cost_guard_caller_hmac_key Field required`).

## 2. Alineación de la documentación de agente

- [x] 2.1 Agregar la línea `COST_GUARD_CALLER_HMAC_KEY=ci-dummy-cost-guard-caller-hmac-key # gitleaks:allow` al bloque "CI dummies" de `AGENTS.md` (sección "Env Vars and Secrets"). Verificación: cross-check contra `.github/workflows/ci.yml:46-51`, que define la variable; la documentación deja de omitirla.
- [x] 2.2 Agregar también `JWT_SECRET_KEY=ci-dummy-jwt-secret-key-for-testing-only # gitleaks:allow` al mismo bloque (era otro campo obligatorio de `Settings`, `settings.py:263`, que la lista omitía). Verificación: el bloque queda con las 5 variables que provee `.github/workflows/ci.yml:46-51`, en el mismo orden.

## 3. Registro de evidencia y observaciones

- [x] 3.1 Dejar registrada la evidencia antes/después en los artefactos. La observación inicial de que `JWT_SECRET_KEY` faltaba en la lista "CI dummies" de `AGENTS.md` quedó cerrada por la tarea 2.2 dentro de este change (misma alineación documental).
