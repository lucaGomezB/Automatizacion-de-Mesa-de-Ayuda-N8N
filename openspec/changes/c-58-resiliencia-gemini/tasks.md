## 0. Gate de decisiones humanas (gobernanza HIGH — bloquea lo demas)

- [x] 0.1 Confirmar con el humano las decisiones de gobernanza ALTA de `design.md`: (a) politica de reserva = UNA reserva por clasificacion dimensionada al peor caso de intentos (D4); (b) reforma de la guarda de preflight de nodos pagos en el mismo change (D7); (c) valores default propuestos (`gemini_max_retries=2`, base 0.5 s, max 8 s, jitter 0.5, presupuesto total 60 s; `maxTries=2`, `waitBetweenTries=2000 ms`). Registrar las respuestas con su valor concreto en la seccion "Decisiones resueltas" de `design.md`. Verificacion: cada decision figura resuelta en `design.md`.
- [x] 0.2 Obtener aprobacion humana explicita del plan antes de escribir codigo o editar `n8n/workflow.json`; registrar la aprobacion en la sesion. Verificacion: la aprobacion queda registrada y las tareas 1+ se autorizan.

## 1. RED — Red de seguridad y tests que fallan primero (offline, sin red ni costo)

- [x] 1.1 Ejecutar la suite offline como linea base y registrar el numero de tests pasando: `cd App/Backend; pytest -m "not integration" -q`. Ademas `cd evaluation; pytest -q` y `cd App/Backend; pytest tests/test_gemini_stt.py tests/test_gemini_generation_config.py tests/test_gemini_validation.py -q` como red de seguridad de la superficie que el auto-retry del SDK podria afectar. Verificacion: baseline registrada, 0 fallos preexistentes.
- [x] 1.2 Crear `App/Backend/tests/test_gemini_retry.py` con un test que simule (con `_client.aio.models.generate_content` mockeado) un `ServerError` 503 en el primer intento y exito en el segundo, exigiendo `etapa=gemini` y exactamente 2 llamadas; ejecutar `cd App/Backend; pytest tests/test_gemini_retry.py -q` y confirmar RED.
- [x] 1.3 Agregar el test de 503 persistente: exige exactamente `gemini_max_retries+1` llamadas, resultado `etapa=fallback`, `confianza=0.0`, `requiere_revision_humana=True`; confirmar RED.
- [x] 1.4 Agregar el test de error terminal: un 400 (y un 403) producen UNA sola llamada (sin reintento) y caen al fallback; confirmar RED.
- [x] 1.5 Agregar el test de timeout: un `TimeoutError` por intento se reintenta y, agotados los intentos, cae al fallback; confirmar RED.
- [x] 1.6 Agregar el test de respuesta JSON invalida: no se reintenta (una sola llamada) y aplica `_fallback`; confirmar RED.
- [x] 1.7 Agregar el test de presupuesto de latencia total: con un cliente que tarda cerca del budget, el bucle deja de reintentar antes de agotar `max_retries`, usando un reloj/sleep inyectado o mockeado; confirmar RED.
- [x] 1.8 Agregar el test de configuracion por entorno: `gemini_max_retries` y `gemini_retry_base_delay_seconds` se leen de Settings y el default es seguro; confirmar RED.
- [x] 1.9 Extender `App/Backend/tests/test_hybrid_classifier.py` con un test que exija que, al escalar a Gemini, la guarda de costo reciba `amount == gemini_max_retries + 1` y que una sola evaluacion cubra todos los reintentos (el fake no registra una segunda reserva); confirmar RED.
- [x] 1.10 Extender `App/Backend/tests/test_n8n_workflow.py` con tests estructurales que exijan: (a) el nodo `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` declara `parameters.modelName` explicito igual a `get_settings().gemini_model`; (b) el nodo `AI Agent` declara `retryOnFail=True` con `maxTries` y `waitBetweenTries` numericos y acotados; confirmar RED (el `workflow.json` actual no los declara).
- [x] 1.11 Crear `scripts/preflight/test_gemini_readiness.py` con tests que exijan PASS sobre un workflow con modelo explicito + reintento acotado y FAIL si falta el modelo o el reintento; confirmar RED (el modulo no existe).
- [x] 1.12 Actualizar `scripts/preflight/test_cost_readiness.py`: el caso "nodo pago con reintento acotado del agente" debe pasar y los casos "reintento en nodo LM" / "retryOnFail sin cotas" / "maxTries fuera del tope" deben fallar; ejecutar `cd scripts/preflight; pytest -q` y confirmar RED.

## 2. GREEN — Taxonomia y bucle de reintento en el clasificador

- [x] 2.1 Implementar un helper PURO de taxonomia en `App/Backend/app/classifiers/gemini_classifier.py` que clasifique una excepcion como transitoria (5xx/429/timeout) o terminal (400/401/403); testearlo con errores sinteticos. Verificacion: GREEN de 1.4.
- [x] 2.2 Implementar en `GeminiClassifier.classify` el bucle de reintento acotado con backoff exponencial + jitter y presupuesto total, preservando la semantica actual de `_fallback` para JSON invalido y la propagacion de `GeminiTimeoutError`/`GeminiUnavailableError` al agotar intentos. Verificacion: GREEN de 1.2, 1.3, 1.5, 1.6.
- [x] 2.3 Implementar la observabilidad estructurada (`gemini_retry_scheduled`, `gemini_retry_exhausted`, `gemini_retry_terminal`) sin clave ni PII. Verificacion: los tests de eventos pasan y ningun payload contiene la clave ni la descripcion.
- [x] 2.4 Tomar propiedad del reintento: desactivar el auto-retry del SDK en el cliente compartido (`get_genai_client`) si la version lo permite, o documentar la imposibilidad y bajar `max_retries`; verificar que la suite de STT (`test_gemini_stt.py`) sigue GREEN. Verificacion: `cd App/Backend; pytest tests/test_gemini_stt.py tests/test_gemini_retry.py -q`.

## 3. GREEN — Configuracion de resiliencia

- [x] 3.1 Agregar a `App/Backend/app/config/settings.py`, junto a las `gemini_*` existentes, los campos `gemini_max_retries: int = 2`, `gemini_retry_base_delay_seconds: float = 0.5`, `gemini_retry_max_delay_seconds: float = 8.0`, `gemini_retry_jitter_ratio: float = 0.5`, `gemini_total_timeout_seconds: int = 60`, con docstring que explique el peor caso y el override por entorno; verificar que `Settings` instancia con los dummies de test.
- [x] 3.2 Reflejar los nuevos campos en `App/Backend/.env.example` con comentarios y valores default. Verificacion: GREEN de 1.8.

## 4. GREEN — Politica de reserva de costo (peor caso, una sola evaluacion)

- [x] 4.1 Cablear en `App/Backend/app/classifiers/hybrid.py` la evaluacion de la guarda con `amount = settings.gemini_max_retries + 1`, sin cambiar la API de `CostGuard`. Verificacion: GREEN de 1.9.
- [x] 4.2 Verificar que los reintentos NO re-evaluan la guarda ni reservan de nuevo y que el rate cuenta una sola llamada por clasificacion. Verificacion: el fake de la guarda registra exactamente una reserva por clasificacion, dimensionada al peor caso.

## 5. GREEN — Superficie Gemini de N8N (`n8n/workflow.json`)

- [x] 5.1 En `n8n/workflow.json`, fijar `parameters.modelName` en el nodo `Google Gemini Chat Model` (`@n8n/n8n-nodes-langchain.lmChatGoogleGemini`) al valor de `settings.gemini_model` (`gemini-3.6-flash`), en lugar de `{"options": {}}`. Verificacion: GREEN de 1.10(a).
- [x] 5.2 En `n8n/workflow.json`, agregar al nodo `AI Agent` (`@n8n/n8n-nodes-langchain.agent`) `retryOnFail: true`, `maxTries: 2` y `waitBetweenTries: 2000` (SOLO en el nodo agente, no en el sub-nodo LM). Verificacion: GREEN de 1.10(b).
- [x] 5.3 Re-importar el workflow en la instancia local de n8n y confirmar que el workflow sigue `active=false` en el JSON versionado. Verificacion: `n8n/workflow.json` con `active=false` y los tests estructurales GREEN.

## 6. GREEN — Preflight: guarda reformulada + chequeo de superficie Gemini

- [x] 6.1 Reformular `_check_paid_retries` en `scripts/preflight/cost_readiness.py` para exigir reintento acotado y explicito en el agente y prohibirlo en nodos LM / sin cotas / fuera del tope. Verificacion: GREEN de 1.12.
- [x] 6.2 Crear `scripts/preflight/gemini_readiness.py` siguiendo el contrato de `cost_readiness.py` (`Check`, `run_*`, `exit_code`, `format_summary`, CLI, `REPO_ROOT`), sin red ni credenciales. Verificacion: GREEN de 1.11.
- [x] 6.3 Cablear el chequeo de superficie Gemini al preflight y a los caminos de arranque/CI existentes (mismo punto donde corre `cost_readiness.py`), sin duplicar la sonda ni usar la clave. Verificacion: `cd scripts/preflight; pytest -q` GREEN y el CLI `python scripts/preflight/gemini_readiness.py` devuelve exit 0 sobre el workflow actualizado.

## 7. Verificacion empirica de n8n y plan de respaldo

- [x] 7.1 Confirmar empiricamente en n8n 2.11.2 que `retryOnFail` del `AI Agent` reejecuta el nodo ante una falla del sub-nodo `lmChatGoogleGemini` (por ejemplo, forzando un 503 con una credencial/endpoint de prueba controlado, sin tocar produccion). Registrar el hallazgo en `verify-report.md`. Verificacion: el hallazgo queda documentado con la evidencia.
- [x] 7.2 Si `retryOnFail` NO cubre la falla del sub-nodo, implementar el plan de respaldo acotado (par de nodos Wait/IF alrededor del agente, con tope de intentos y camino terminal a `requiere_revision_humana=true`) y actualizar los tests estructurales. Verificacion: el respaldo queda implementado y testeado, o el punto 7.1 confirma que no es necesario.

## 8. Cierre

- [x] 8.1 Correr la suite completa offline y confirmar 0 regresiones: `cd App/Backend; pytest -m "not integration" -q` y `cd scripts/preflight; pytest -q`.
- [x] 8.2 Actualizar la documentacion operativa de la superficie Gemini (modelo pineado, reintento acotado, nuevas settings y su default) en los documentos que el proyecto use para ello. Verificacion: la documentacion lista los nuevos campos y su default.
- [x] 8.3 Ejecutar `openspec validate c-58-resiliencia-gemini --strict` y confirmar que pasa. Verificacion: salida sin errores.
