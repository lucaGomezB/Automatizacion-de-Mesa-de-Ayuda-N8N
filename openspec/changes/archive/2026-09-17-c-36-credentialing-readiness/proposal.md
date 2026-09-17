## Why

El proyecto esta por conectar credenciales reales (Gemini, Twilio, Outlook). c-33 acoto los bucles de gasto pago y c-34 abarato la evaluacion, pero quedan tres riesgos que se cierran SIN credenciales: una ejecucion N8N colgada no tiene tope de tiempo; no hay verificacion de que las guardas de costo esten cableadas; y la corrida paga del runner de evaluacion arranca sin opt-in ni estimacion. Ademas, dos documentos de operacion quedaron desactualizados.

## What Changes

- **Tope de ejecucion N8N**: `EXECUTIONS_TIMEOUT=300` y `EXECUTIONS_TIMEOUT_MAX=600` en el environment del servicio `n8n` de `docker-compose.yml`. Gobernanza HIGH: el apply MUST obtener checkpoint humano antes de escribir.
- **Preflight de costo cero**: nuevo `scripts/preflight/cost_readiness.py` (+ tests) que verifica guardas en `n8n/workflow.json` (tope del `AI Agent`; lookback de 24 h y `readStatus=unread`; `Marcar correo como leido` alcanzable desde exito/rechazo/error; body del `HTTP POST a MTM-SRU` con `origen_message_id` + clasificacion precalculada + marcador de evento; webhook `notificacion-clasificacion` aislado; ningun nodo pago con `retryOnFail`/`maxTries`) y en `docker-compose.yml` (imagen N8N pineada; `N8N_WEBHOOK_URL` a la ruta dedicada; `EXECUTIONS_TIMEOUT` presente). Reporta PASS/FAIL y sale no-cero si falta una guarda; sin red ni Docker.
- **Gate de corrida paga**: `evaluation/run_evaluation.py` exige `--confirm-paid` o `EVALUATION_CONFIRM_PAID`, imprime una estimacion de costo y rechaza por defecto la corrida paga cuando no hay cache valido. Conserva `--force`/`--no-cache` y el cache de c-34.
- **Test de regresion**: en `App/Backend/tests/test_n8n_workflow.py`, ningun nodo pago habilita `retryOnFail`/`maxTries`.
- **Docs/config**: `docs/por_implementar.md` (quitar conteo stale y pendiente "N8N usa latest", resuelto en c-34) y `openspec/config.yaml` (N8N 1.62 -> 2.11.2).

**Fuera de alcance**: doble transcripcion de Twilio; build de produccion del frontend y backups; credenciales reales; modificar `n8n/workflow.json` (c-36 solo lo verifica).

## Capabilities

### New Capabilities

- `cost-readiness`: preflight de costo cero sobre los artefactos del repo (guardas del workflow y del compose, lista PASS/FAIL, codigo de salida, sin red) y tope de ejecucion declarado del servicio N8N.

### Modified Capabilities

- `evaluation-prediction-cache`: la corrida paga del runner exige opt-in explicito e imprime una estimacion de costo antes de invocar el clasificador real; el comportamiento de cache de c-34 no cambia.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `docker-compose.yml` | Modified | Servicio `n8n`: `EXECUTIONS_TIMEOUT=300`, `EXECUTIONS_TIMEOUT_MAX=600`. Gobernanza HIGH |
| `scripts/preflight/cost_readiness.py` + tests | New | Preflight estatico PASS/FAIL, sin red ni Docker |
| `evaluation/run_evaluation.py` + tests | Modified | Gate de opt-in pago y estimacion; `--force`/`--no-cache` intactos |
| `App/Backend/tests/test_n8n_workflow.py` | Modified | Regresion: nodos pagos sin reintentos |
| `docs/por_implementar.md`, `openspec/config.yaml` | Modified | Consistencia documental del estado real |

- **Gobernanza**: HIGH en `docker-compose.yml` (servicio en ejecucion). LOW/MEDIUM en el resto.
- **Dependencias**: `c-33-cost-guards` (guardas que el preflight verifica) y `c-34-evaluation-prediction-cache` (cache y pin asumidos). Ambas archivadas.
