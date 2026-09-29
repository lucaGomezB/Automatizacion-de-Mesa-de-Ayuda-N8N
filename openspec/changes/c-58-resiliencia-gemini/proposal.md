## Why

La ejecución #9 de N8N (2026-09-29T18:08) muestra que el backend recibió un `HTTP 503` transitorio de `gemini-3.6-flash` ("This model is currently experiencing high demand... temporary") y el incidente terminó en `etapa=fallback, confianza=0.0, requiere_revision_humana=true`. La causa es que `GeminiClassifier.classify` hace **un solo intento** (`App/Backend/app/classifiers/gemini_classifier.py:374-385`) con un `except Exception -> GeminiUnavailableError` genérico (`:407-410`): una falla transitoria del proveedor se trata como falla dura. La credencial es válida (se listaron 61 modelos y `gemini-3.6-flash` está presente), así que NO es auth ni quota. El canal telefónico tiene el mismo hueco: el `AI Agent` de n8n aborta ante un error del sub-nodo de modelo y el nodo `Google Gemini Chat Model` ni siquiera fija su modelo (`parameters: {"options": {}}` hereda el default del nodo).

## What Changes

- **Backend — reintento acotado ante fallas transitorias**: reintentos con backoff exponencial + jitter SOLO para fallas transitorias (HTTP 503/429 y 5xx, y timeouts). Los errores terminales (400 petición inválida, 401/403 auth, JSON de respuesta inválido) NO se reintentan y conservan la semántica actual. Agotados los reintentos, aplica el fallback existente (`etapa=fallback`, `confianza=0.0`, `requiere_revision_humana=true`).
- **Backend — knobs de configuración**: nuevas settings con defaults seguros y override por entorno (`gemini_max_retries`, `gemini_retry_base_delay_seconds`, `gemini_retry_max_delay_seconds`, `gemini_retry_jitter_ratio`, `gemini_total_timeout_seconds`), documentadas junto a las `gemini_*` existentes. El presupuesto de latencia total acota la suma de intentos.
- **Guarda de costo — política de reserva**: UNA reserva por clasificación que cubre el peor caso de intentos (vía el factor `amount` ya soportado), evaluada UNA vez antes de invocar al clasificador. Los reintentos NO disparan reservas adicionales ni pueden escapar del tope.
- **N8N — superficie Gemini**: fijar el `modelName` explícito en el nodo `Google Gemini Chat Model` (paridad con `settings.gemini_model`) y agregar una política de reintento acotada (`retryOnFail`, `maxTries`, `waitBetweenTries`) al `AI Agent` del canal telefónico, para que una falla transitoria del modelo no aborte la clasificación.
- **Preflight — guarda de reintentos y chequeo de superficie**: la guarda actual prohíbe TODO reintento en nodos pagos (`scripts/preflight/cost_readiness.py:283-294`); se reformula para EXIGIR un reintento acotado y explícito, y se agrega un chequeo estático que reporta el estado de la superficie Gemini (modelo explícito presente + reintento acotado configurado). Sin sonda viva en CI.
- **Tests (TDD, RED primero)**: cliente genai mockeado para simular 503→éxito, 503 persistente, error terminal sin reintento y timeout→fallback; más la política de reserva de la guarda y la estructura del workflow.

## Capabilities

### New Capabilities

- `classification-resilience`: contrato de resiliencia de la clasificación con Gemini — taxonomía transitorio/terminal, reintento acotado con backoff+jitter, parámetros configurables, fallback tras agotar intentos, observabilidad, semántica de reintento acotado del agente de n8n y chequeo estático de la superficie Gemini.

### Modified Capabilities

- `runtime-cost-guard`: la reserva de una superficie paga con reintentos acotados pasa a cubrir el peor caso de intentos por invocación aceptada, evaluada una sola vez (los reintentos no reservan de nuevo).
- `n8n-workflow`: el sub-nodo de modelo declara un modelo explícito y el `AI Agent` declara un reintento acotado ante fallas transitorias, reconciliado con el tope de refinamiento N8N-REFINE-001.
- `cost-readiness`: la guarda de reintentos de nodos pagos deja de prohibir todo reintento y pasa a exigir un reintento acotado y explícito; se agrega el chequeo de superficie Gemini.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `App/Backend/app/classifiers/gemini_classifier.py` | Modified | Bucle de reintento, taxonomía de errores, backoff+jitter, presupuesto total |
| `App/Backend/app/config/settings.py` + `.env.example` | Modified | Nuevas settings `gemini_retry_*` y `gemini_total_timeout_seconds` |
| `App/Backend/app/classifiers/hybrid.py` | Modified | Pasa `amount = max_attempts` a la guarda (peor caso) |
| `App/Backend/app/cost_guard/` | Reused | Sin cambios de API; usa `amount` ya existente (precedente c-52) |
| `App/Backend/tests/` | New | Tests de reintento/taxonomía/fallback/reserva y estructura del workflow |
| `n8n/workflow.json` | Modified | `modelName` explícito en el LM + reintento acotado en el `AI Agent` |
| `scripts/preflight/` | Modified/New | Guarda de reintentos reformulada + `gemini_readiness` estático |
| `App/Frontend/`, `evaluation/` | Out of scope | Sin cambios |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Reintentos multiplican el costo pago | Med | Reintento acotado (default 2) + reserva de peor caso; sin reintento en errores terminales |
| El SDK de `google-genai` reintenta por su cuenta y duplica intentos | Med | Tomar propiedad del reintento desactivando el auto-retry del SDK; verificar en apply |
| La latencia p99 del endpoint crece | Med | Presupuesto total configurable; per-intento sigue acotado por `gemini_timeout_seconds` |
| El `retryOnFail` del `AI Agent` no cubra fallas del sub-nodo LM | Med | Verificación empírica en apply contra n8n 2.11.2; plan de respaldo (error workflow / bucle Wait) incluido en tasks |
| La guarda de preflight de nodos pagos rompe el CI al habilitar reintentos | High | Se reformula en el MISMO change y se actualiza el test de preflight |
| La reserva de peor caso dispara la guarda antes de tiempo | Low | Costos unitarios son estimaciones de tope; max attempts chico; documentado |

## Rollback Plan

Backend: `gemini_max_retries=0` desactiva los reintentos sin revertir código (comportamiento equivalente al actual). Revertir `settings.py`, `gemini_classifier.py`, `hybrid.py` y `.env.example`. N8N: revertir `n8n/workflow.json` y re-importar en la UI. Preflight: revertir la guarda de reintentos y quitar `gemini_readiness`. Sin migraciones de base de datos ni cambios de contrato de API.

## Success Criteria

- [ ] Un 503 transitorio seguido de éxito NO produce fallback: `etapa=gemini` con la clasificación del proveedor.
- [ ] Un 503 persistente produce fallback tras exactamente N intentos configurados, con `requiere_revision_humana=true`.
- [ ] Un 400/401/403 NO se reintenta (exactamente 1 llamada) y cae al fallback conservando la semántica actual.
- [ ] Un timeout se reintenta y, si persiste, cae al fallback.
- [ ] La guarda de costo registra UNA sola reserva por clasificación, dimensionada al peor caso de intentos.
- [ ] El nodo `Google Gemini Chat Model` declara `modelName` explícito, en paridad con `settings.gemini_model`.
- [ ] El `AI Agent` telefónico declara reintento acotado y el preflight lo verifica (PASS), sin prohibir todo reintento.
- [ ] `openspec validate c-58-resiliencia-gemini --strict` pasa.
