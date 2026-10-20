## Context

Ver `proposal.md` - Why para la motivación. Restricciones que moldean el enfoque:

- `Settings` (pydantic-settings, `App/Backend/app/config/settings.py`) valida cada campo al construir y exige `cost_guard_caller_hmac_key` SIN default. El test construye `Settings` a través de `get_settings()`, que lee el entorno del proceso.
- La suite de evaluación corre offline (no invoca Gemini ni PostgreSQL reales), por lo que las credenciales solo deben ser valores de relleno válidos para la validación de tipos.
- La obligatoriedad de `cost_guard_caller_hmac_key` es una guarda de seguridad (identificador no reversible de origen, c-66) y NO debe debilitarse.

## Goals / Non-Goals

**Goals:**

- Que `test_settings_tau_deriva_del_oof_del_corpus` pase tanto con la variable presente como ausente en el entorno del proceso.
- Que la lista "CI dummies" de `AGENTS.md` deje de omitir `COST_GUARD_CALLER_HMAC_KEY`.

**Non-Goals:**

- No cambiar el contrato de `Settings` ni dar valores por defecto a secretos.
- No cerrar la omisión de `JWT_SECRET_KEY` en `AGENTS.md` (observación separada, no introducida por c-100).

## Decisions

- **Decisión: inyectar `COST_GUARD_CALLER_HMAC_KEY` con `monkeypatch.setenv` dentro del test.** Es la forma mínima y local que hace al test hermético: `monkeypatch` restaura el entorno al finalizar, no contamina otros tests y no debilita el contrato de `Settings` (que debe seguir exigiendo la clave en producción).
  - **Alternativas consideradas**: (a) dar un default vacío al campo en `Settings` — descartado, debilita la guarda de costo y cambia el contrato por conveniencia de un test; (b) una fixture `autouse` que setee la variable para toda la suite de evaluación — descartado por ser más amplio que el defecto y porque oculta dependencias de entorno que conviene que cada test declare.
- **Decisión: alinear `AGENTS.md` agregando la variable a la lista "CI dummies".** El documento es la guía operativa de los agentes; su lista estaba desalineada con `.github/workflows/ci.yml`, que sí define la variable. Alinear la lista evita que el próximo test (o el próximo agente) repita la suposición de que el entorno la trae.

## Risks / Trade-offs

- **[Riesgo] `AGENTS.md` sigue incompleto**: `JWT_SECRET_KEY`, también obligatoria, no figura en la lista "CI dummies" (hueco preexistente). → **Mitigación**: se registra como observación explícita; no se amplía el alcance de c-100 porque no forma parte del defecto encontrado.
- **[Trade-off] El test permanece condicional**: un `skipif` lo saltea si el corpus pseudonimizado y la cache de calibración locales no existen (no trackeados en git). → Es comportamiento previo y deseado (solo corre con datos reales); no se modifica.
- **[Riesgo] Falso verde en CI**: CI define la variable, así que el defecto era invisible allí. → **Mitigación**: el fix garantiza que el test también pase en un entorno local limpio, que es donde se manifestaba.
