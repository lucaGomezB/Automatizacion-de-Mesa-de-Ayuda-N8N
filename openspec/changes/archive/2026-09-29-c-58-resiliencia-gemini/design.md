## Context

Ver `proposal.md — Why` para la motivación. Restricciones verificadas que moldean el enfoque:

- El camino pago del backend es de UN intento: `GeminiClassifier.classify` (`App/Backend/app/classifiers/gemini_classifier.py:374-385`) envuelve `generate_content` en `asyncio.wait_for(timeout=self._timeout)` y mapea cualquier excepción a `GeminiUnavailableError` (`:407-410`); `TimeoutError` a `GeminiTimeoutError` (`:400-405`); JSON inválido a `self._fallback` sin propagar (`:391-398`).
- `HybridClassifier.classify` (`App/Backend/app/classifiers/hybrid.py:158-210`) evalúa la guarda de costo una vez (`:162-169`), invoca a Gemini (`:170`) y, ante `GeminiTimeoutError`/`GeminiUnavailableError`, devuelve `etapa=fallback, confianza=0.0, requiere_revision_humana=true` (`:195-210`).
- La guarda de costo (`App/Backend/app/cost_guard/guard.py:84-134`) permite dimensionar el costo reservado con el parámetro `amount` (`:109`, `unit_cost * factor`), ya usado por la superficie STT (c-52). `calls_delta` permanece en 1 sin importar `amount` (`:152-165`), así que `amount` escala el costo pero NO el rate de llamadas.
- El nodo `Google Gemini Chat Model` (`n8n/workflow.json:500-518`) declara `parameters: {"options": {}}` y NO fija `modelName`; el `AI Agent` (`n8n/workflow.json:184-197`) tiene `onError: continueRegularOutput` y NO declara `retryOnFail`/`maxTries`. Ningún nodo pago declara reintentos.
- El preflight estático `_check_paid_retries` (`scripts/preflight/cost_readiness.py:283-294`) FALLA si cualquier nodo `@n8n/n8n-nodes-langchain.agent` o `...lm*` declara `retryOnFail=true` o `maxTries` numérico. Habilitar el reintento sin reformar esta guarda deja el CI en rojo.
- Spec `cost-readiness` — Requirement "Definicion de nodo pago para la guarda de reintentos" (`openspec/specs/cost-readiness/spec.md:61-73`) exige prohibir todo reintento pago.
- Spec `n8n-workflow` — Requirement "N8N-REFINE-001 — Tope de refinamiento del agente pago" (`openspec/specs/n8n-workflow/spec.md:270-292`) limita a 2 los intentos de clasificación/refinamiento.
- Spec `runtime-cost-guard` — Requirement "Costo unitario por superficie paga" (`openspec/specs/runtime-cost-guard/spec.md:32-45`) dice que cada llamada paga concede exactamente el costo unitario.
- `google-genai` se usa con un `genai.Client` compartido de proceso (`gemini_classifier.py:52-71`), cerrado en shutdown.
- Docs n8n: "Retry On Fail: When an execution fails, the node reruns until it succeeds" (node-level). El sub-nodo LM se ejecuta dentro de la ejecución del nodo agente; una falla del sub-nodo falla el nodo, por lo que el `retryOnFail` del `AI Agent` reejecuta al agente y a su modelo.

## Goals / Non-Goals

**Goals:**

- Sobrevivir fallas transitorias de Gemini (503/429/5xx/timeout) con un reintento acotado, con backoff exponencial + jitter y presupuesto de latencia total.
- Mantener los errores terminales (400/401/403, JSON inválido) sin reintento, conservando la semántica de fallback actual.
- Mantener el comportamiento determinista del pipeline y su testeo OFFLINE (cliente genai mockeado, sin red ni costo).
- Que la resiliencia NO abra un agujero en la guarda de costo: una reserva por clasificación, dimensionada al peor caso, sin reservas por reintento.
- Que la superficie Gemini de n8n quede explícita (modelo pineado) y resiliente (reintento acotado del agente), con verificación estática en el preflight.

**Non-Goals:**

- No se cambia la taxonomía de sectores, los umbrales 0.90/0.70 ni el contrato de la API de incidentes.
- No se introduce un circuit breaker ni un caché de respuestas de Gemini.
- No se reescribe el bucle de refinamiento del canal telefónico (N8N-REFINE-001 se conserva).
- No se agrega una sonda viva de disponibilidad de Gemini en CI (ver D6).
- No se toca el corpus de evaluación ni el frontend.

## Decisions

### D1 — El reintento es propio del `GeminiClassifier`, no delegado al SDK

**Decisión:** implementar el bucle de reintento en `GeminiClassifier.classify`, y desactivar/inactivar el auto-retry del SDK `google-genai` en el cliente compartido para que exista UNA sola fuente de política de reintento.

**Rationale:** el SDK oculta cuántos intentos hace, con qué backoff y contra qué códigos; su auto-retry ya fue observado encadenando reintentos ante 503 (nota en `settings.py:78-79`). Superponer nuestro bucle sobre el del SDK multiplica intentos y latencia de forma no acotada ni testeable. Tomar propiedad hace el comportamiento determinista, mockeable y compatible con el presupuesto total.

**Alternativas consideradas:** (a) confiar en el auto-retry del SDK — opaco, difícil de acotar y de testear; (b) bucle propio SIN desactivar el del SDK — intentos multiplicativos y p99 impredecible.

**Riesgo de la decisión:** desactivar el auto-retry del SDK cambia el comportamiento global del cliente (afecta también al STT). Se mitiga verificando en apply que el STT no dependa del auto-retry y que el bucle propio cubra sus errores transitorios; el STT queda fuera de alcance salvo por esta regresión, que la suite debe detectar.

### D2 — Taxonomía de errores: transitorio vs terminal

**Decisión:** reintentar SOLO:
- `google.genai.errors.ServerError` (5xx, incluido 503 y 500/502/504); y
- errores de cliente con estado HTTP 429 (rate limit transitorio).

NO reintentar (terminal, cae directo al manejo actual):
- `ClientError` con 400/401/403/404 (petición inválida, auth, no encontrado);
- `GeminiResponseInvalidError` (JSON/schema inválido) → `_fallback` sin propagar, como hoy.

Los timeouts (`asyncio.wait_for`) SÍ se reintentan y, agotados, se propagan como `GeminiTimeoutError` hacia el fallback de `HybridClassifier`.

**Rationale:** reintentar un 400 o un 401 es inútil (el error es determinista) y reintentar una respuesta con schema inválido no mejora con backoff. Solo 429/5xx/timeout representan indisponibilidad transitoria del proveedor.

**Alternativas consideradas:** reintentar "cualquier excepción" — reintentaría errores de contrato y multiplicaría costo sin beneficio; no reintentar 429 — el 429 es explícitamente transitorio.

**Nota de implementación:** la clasificación de estado HTTP se resuelve por atributo del error del SDK (`code`/`status_code`) con un helper puro y testeable; se cubre la incertidumbre sobre la clase exacta de 429 en el SDK en Open Questions.

### D3 — Latencia acotada: timeout por intento + presupuesto total

**Decisión:** cada intento conserva `gemini_timeout_seconds` (default 30 s). Se agrega `gemini_total_timeout_seconds` (default 60 s) como presupuesto de reloj de pared para TODA la operación de clasificación. El bucle deja de reintentar cuando (a) se agotan `gemini_max_retries`, o (b) el tiempo restante del presupuesto es insuficiente para otro intento con su backoff. El delay de backoff se calcula como `min(base * 2**(n-1), max_delay)` con jitter y se recorta al presupuesto restante.

**Rationale:** sin un presupuesto total, `max_retries × timeout` puede exceder cualquier SLO. Con per-intento 30 s y total 60 s, por defecto caben hasta dos intentos completos; los 503 rápidos permiten más. Es configurable por entorno.

**Alternativas consideradas:** un único timeout global — pierde la cota por intento; reintentar sin considerar el presupuesto — p99 sin techo.

### D4 — Guarda de costo: UNA reserva por clasificación, dimensionada al peor caso

**Decisión:** `HybridClassifier` evalúa la guarda UNA vez antes de invocar a Gemini, pasando `amount = gemini_max_retries + 1` (número máximo de intentos). Los reintentos NO consultan la guarda ni reservan de nuevo. La reserva cubre el peor caso de gasto pago de esa clasificación.

**Rationale:** (1) mantiene la guarda en el borde del pipeline, sin filtrarla al bucle de reintento (responsabilidad única); (2) es fail-safe/fail-closed: si el peor caso no cabe, se niega ANTES de gastar; (3) reutiliza el parámetro `amount` ya existente (precedente STT c-52); (4) no infla el contador de rate, que sigue contando 1 llamada por clasificación. El costo unitario es una ESTIMACIÓN de tope, no contabilidad exacta, así que reservar el peor caso es coherente con el propósito de la guarda.

**Alternativas consideradas:**
- **Reserva por intento** (re-evaluar la guarda en cada reintento): contabilidad más fina, pero requiere inyectar `CostGuard` en `GeminiClassifier` (acoplamiento cruzado de capas), agrega una reserva atómica por intento en el camino caliente y permite que la guarda corte a mitad de una clasificación con estado parcial. RECHAZADA.
- **Reserva de una unidad e ignorar reintentos**: subcuenta el gasto real y debilita el tope. RECHAZADA.

**Consecuencia en n8n:** la reserva de la superficie `n8n_gemini` (una por ejecución) cubre igualmente los intentos acotados del `AI Agent`; el costo unitario `cost_guard_unit_cost_n8n_gemini_usd` se documenta como cobertura del peor caso, sin reservas por reintento.

### D5 — n8n: modelo explícito + reintento acotado del agente, reconciliado con N8N-REFINE-001

**Decisión:**
- El nodo `Google Gemini Chat Model` declara `parameters.modelName` explícito e igual a `settings.gemini_model` (default `gemini-3.6-flash`), en lugar de heredar el default del nodo.
- El nodo `AI Agent` declara `retryOnFail: true`, `maxTries` acotado (default propuesto 2 = 1 reintento) y `waitBetweenTries` (default propuesto 2000 ms). Se aplica SOLO al nodo agente; el sub-nodo LM NO declara reintento propio.
- N8N-REFINE-001 (tope de refinamiento por VALIDACIÓN) se conserva. Los reintentos de TRANSPORTE (error transitorio del modelo) y los refinamientos (respuesta inválida) son ortogonales. El total de invocaciones pagas por incidente telefónico queda acotado por el PRODUCTO `maxTries × intentos_de_refinamiento` (con defaults 2 × 2 = 4), que se documenta y se verifica.

**Rationale:** un 503 del sub-nodo LM hace FALLAR el nodo agente (no produce salida inválida), por lo que el bucle de refinamiento NO lo captura: sin `retryOnFail` el incidente telefónico se pierde. El reintento a nivel de nodo es el mecanismo de n8n documentado ("the node reruns until it succeeds"). Acotarlo y no reintentar en el sub-nodo mantiene el tope de gasto.

**Alternativas consideradas:**
- **Bucle Wait/IF manual de reintento en el workflow**: control explícito del backoff, pero agrega nodos, más superficie de fallo y duplica el bucle de refinamiento. RECHAZADA salvo que D5 no se cumpla (ver abajo).
- **No tocar n8n y delegar todo al backend**: no aplica: el canal telefónico clasifica en n8n, no en el backend.

**Verificación pendiente:** confirmar empíricamente en n8n 2.11.2 que `retryOnFail` del `AI Agent` cubre la falla del sub-nodo `lmChatGoogleGemini`. La doc indica que el nodo se reejecuta ante fallo de ejecución y el sub-nodo corre dentro de esa ejecución, así que se espera que SÍ. Si no se cumple, el plan de respaldo es un par de nodos Wait/IF alrededor del agente, y la tarea correspondiente ya está prevista en `tasks.md`.

### D6 — Readiness estática, sin sonda viva en CI

**Decisión:** agregar un chequeo estático (`scripts/preflight/gemini_readiness.py`, mismo patrón que `cost_readiness.py`: `Check`, `run_*`, `exit_code`, `format_summary`, CLI) que reporta: (a) el nodo `lmChatGoogleGemini` declara `modelName` no vacío; (b) el `AI Agent` declara `retryOnFail=true` con `maxTries` y `waitBetweenTries` numéricos y acotados. NO se hace sonda de red. Opcional y diferido: un script MANUAL de disponibilidad que lea la clave de entorno, NO la imprima y no corra en CI.

**Rationale:** una sonda viva (1) exige la clave y arriesga filtrarla en logs/CI, (2) es no determinista y puede colgar el arranque local/CI, (3) no predice la disponibilidad en el momento de clasificar — el reintento + fallback ya cubren la transitoriedad en runtime. El chequeo estático sí detecta la causa raíz accionable (modelo no pineado, sin reintento).

**Alternativas consideradas:** sonda viva en CI — acopla el pipeline a la disponibilidad de un tercero y a un secreto; sonda viva en el arranque local — misma objeción de secreto y latencia. RECHAZADAS para CI/arranque; la sonda manual queda como mejora opcional fuera de alcance.

### D7 — Reforma de la guarda de preflight en el MISMO change

**Decisión:** modificar `_check_paid_retries` para que en vez de prohibir todo reintento exija un reintento ACOTADO y explícito en el nodo agente: `retryOnFail=true` acompañado de `maxTries` numérico dentro de un tope y `waitBetweenTries` numérico con un mínimo; y siga prohibiendo `retryOnFail`/`maxTries` en los nodos de modelo (`...lm*`) y en cualquier otro nodo pago. La spec `cost-readiness` se modifica en consecuencia.

**Rationale:** el requisito actual existe para acotar el gasto, no para impedir la resiliencia. El CI quedaría rojo si se habilita el reintento sin reformar la guarda; ambos cambios deben ir juntos.

**Alternativas consideradas:** dejar la guarda como está y no tocar n8n — incumple el objetivo de resiliencia telefónica; hacer una excepción hardcodeada al nodo agente — menos verificable que una regla de "reintento acotado".

## Risks / Trade-offs

- **Costo pago vs disponibilidad** → reintento acotado (default 2) + reserva de peor caso + sin reintento en terminales. El peor caso por incidente de backend queda en `unit_cost × (max_retries+1)`.
- **Doble reintento (SDK + propio)** → D1 desactiva el auto-retry del SDK; verificación en apply y test con cliente mockeado.
- **Regresión del STT por desactivar el auto-retry global** → suite de STT como red de seguridad; el STT puede recibir su propio reintento en un change futuro si lo necesita.
- **p99 del endpoint** → presupuesto total configurable; por defecto 60 s.
- **`retryOnFail` no cubre la falla del sub-nodo** → verificación empírica + plan de respaldo Wait/IF en tasks.
- **La reserva de peor caso consume presupuesto de intentos que no ocurren** → aceptado: la guarda es un tope conservador con costos unitarios estimados; `max_attempts` chico.
- **La guarda de preflight rompe el CI al habilitar el reintento** → se reforma en el mismo change (D7) y se actualiza su test estructural.
- **Deriva de paridad de modelo** → un test de backend compara `settings.gemini_model` contra el `modelName` del workflow (fuente única de verdad).

## Migration Plan

1. Backend: agregar settings (defaults habilitan el reintento con `gemini_max_retries=2`; `gemini_max_retries=0` restaura el comportamiento actual). Sin migración de BD.
2. Implementar el bucle de reintento y la taxonomía; cablear `amount` en `HybridClassifier`.
3. N8N: editar `n8n/workflow.json` (modelo explícito + reintento del agente), reformar la guarda de preflight y re-importar el workflow en la UI de n8n (el JSON del repo no se auto-activa; `active=false`).
4. Rollback: `gemini_max_retries=0` en backend; revertir `workflow.json`, la guarda de preflight y `gemini_readiness`; re-importar el workflow previo. Sin datos que restaurar.

## Open Questions

- ¿Qué clase/atributo exacto expone `google-genai` para un 429 y para 5xx en la versión fijada? Se resuelve en apply inspeccionando el SDK y se cubre con fakes; no cambia specs ni tasks (el helper de taxonomía se testea con errores sintéticos).
- ¿El `genai.Client` compartido auto-reintenta 5xx por defecto en la versión fijada, y cómo se desactiva (`HttpOptions.retry_options`)? El default del diseño es desactivarlo; si la versión no lo permite, se documenta el riesgo de multiplicación y se ajusta `max_retries` a la baja. No cambia specs ni tasks.
- ¿El auto-retry del STT depende del mismo cliente? Si al desactivarlo se degrada el STT, se le da su propio reintento en un change posterior. El alcance NO cambia (STT fuera de alcance salvo regresión detectada por la suite).

## Decisiones resueltas (tasks 0.1 / 0.2)

Aprobadas explícitamente por el humano antes de escribir código o editar `n8n/workflow.json`:

- **(a) Política de reserva (D4)**: UNA reserva por clasificación dimensionada al peor caso
  de intentos (`amount = gemini_max_retries + 1`). Los reintentos NO re-evalúan la guarda
  ni reservan de nuevo; el rate cuenta una sola llamada por clasificación.
- **(b) Reforma de la guarda de preflight en el MISMO change (D7)**: `_check_paid_retries`
  pasa de prohibir todo reintento a EXIGIR un reintento acotado y explícito en el nodo
  agente, y a seguir prohibiendo `retryOnFail`/`maxTries` en nodos `...lm*` y en cualquier
  otro nodo pago (sin cotas).
- **(c) Defaults**: backend `gemini_max_retries=2`, `gemini_retry_base_delay_seconds=0.5`,
  `gemini_retry_max_delay_seconds=8.0`, `gemini_retry_jitter_ratio=0.5`,
  `gemini_total_timeout_seconds=60`; n8n `retryOnFail=true`, `maxTries=2`,
  `waitBetweenTries=2000`. `gemini_max_retries=0` restaura el comportamiento de un solo
  intento.

