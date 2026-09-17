## Context

Ver `proposal.md — Why` para la motivacion. Estado actual y restricciones que moldean el enfoque:

- `docker-compose.yml` declara el servicio `n8n` con `image: n8nio/n8n:2.11.2` (pineada por c-34) y en su environment tiene `EXECUTIONS_DATA_PRUNE` / `EXECUTIONS_DATA_MAX_AGE`, pero NO declara `EXECUTIONS_TIMEOUT` ni `EXECUTIONS_TIMEOUT_MAX`. Una ejecucion colgada (por ejemplo, esperando un webhook pago) no tiene cota superior.
- `n8n/workflow.json` YA contiene las guardas de c-33: `AI Agent` con `options.maxIterations=2`; trigger de Outlook con `readStatus=unread` y `custom` con lookback de 24 h sobre `receivedDateTime`; `Marcar correo como leido` alcanzable desde exito/rechazo/error; body de `HTTP POST a MTM-SRU` con `origen_message_id`, bloque `clasificacion` y `origen_evento`; webhook `notificacion-clasificacion` aislado; y ningun nodo con `retryOnFail`/`maxTries`. c-36 NO modifica el workflow: lo verifica.
- El repo tiene el precedente `scripts/dry_run/` (c-31): `checks.py` con logica pura, `Check` + codigos de salida 0/1, y tests en `scripts/dry_run/test_*.py` que se ejecutan con pytest. El nuevo preflight es un hermano estatico (no levanta Docker).
- `evaluation/run_evaluation.py` expone `main_con_corpus_real(corpus_path, classifier, report_path, predicciones_path, force)` y un CLI `main()` con `--force`/`--no-cache`. El cache de c-34 vive en `main_con_corpus_real`: si el cache es valido y `force=False`, carga predicciones y no invoca al clasificador. `evaluation/tests/conftest.py` inyecta `FakeClassifier`, por lo que los tests existentes no deben exigir confirmacion.
- **Gobernanza**: `docker-compose.yml` es HIGH (servicio N8N en ejecucion); el apply MUST obtener checkpoint humano explicito antes de escribir esa area. `evaluation/run_evaluation.py`, el script nuevo, los tests y los docs son LOW/MEDIUM.

## Goals / Non-Goals

**Goals:**

- Cerrar los tres riesgos de costo pendientes sin credenciales reales: ejecucion N8N sin tope, guardas de costo no verificables, corrida paga de evaluacion sin opt-in.
- Que cada guarda sea verificable de forma estatica (sin red, sin Docker, sin credenciales) y que el preflight sea reutilizable como test.
- Mantener intacto el comportamiento de cache de c-34 y la semantica de `--force`/`--no-cache`.
- Dejar la documentacion de operacion consistente con el estado real antes de credentialear.

**Non-Goals:**

- No se modifica `n8n/workflow.json` (las guardas ya existen).
- No se configura ninguna credencial real.
- No se implementa el doble transcribe de Twilio ni el build de produccion del frontend ni backups automaticos.
- No se integra el preflight a CI/Make en este change (se deja el script ejecutable; el wiring es un follow-up).
- No se define una politica de precios autoritativa: la estimacion es orientativa.

## Decisions

### D1 — `EXECUTIONS_TIMEOUT=300` y `EXECUTIONS_TIMEOUT_MAX=600` en el servicio `n8n`

Se agregan al environment del servicio `n8n` en `docker-compose.yml`: `EXECUTIONS_TIMEOUT: "300"` (cota por defecto, 5 minutos) y `EXECUTIONS_TIMEOUT_MAX: "600"` (techo configurable, 10 minutos). Se declaran como strings, igual que el resto de las variables del servicio.

- **Razon**: 300 s cubre holgadamente el tramo mas largo (Outlook + login + agente pago acotado a 2 iteraciones + POST + notificacion) y es el mismo orden que un timeout HTTP con reintentos; 600 s deja margen para picos sin permitir que una ejecucion quede viva indefinidamente. `MAX >= default` mantiene la coherencia exigida por la spec.
- **Alternativas consideradas**: (a) 120 s — descartado por riesgo de cortar ejecuciones legitimas del agente con red lenta; (b) 900 s — descartado por ser demasiado permisivo para una ejecucion que podria estar esperando un recurso pago colgado; (c) no declarar `EXECUTIONS_TIMEOUT_MAX` — descartado porque el techo es lo que impide que un override de workflow anule la cota.
- **Gobernanza HIGH**: el apply MUST presentar el plan exacto (claves y valores) y obtener aprobacion humana antes de escribir `docker-compose.yml`.

### D2 — Preflight en `scripts/preflight/cost_readiness.py`, logica pura y reutilizable

El script separa la logica pura (funciones que reciben rutas y devuelven `list[Check]`) del punto de entrada CLI. Funciones: `check_workflow(path)`, `check_compose(path)`, `run_preflight(workflow_path, compose_path)`, `exit_code(checks)` y `format_summary(checks)`. Cada `Check` lleva `name`, `status` (`PASS`/`FAIL`) y `detail`. El CLI imprime la lista y la sintesis, y sale 0 si y solo si todo es PASS; 1 si algo falla. No hay acceso a red ni a Docker.

- **Razon**: el precedente `scripts/dry_run/checks.py` demuestra que la logica pura es testeable sin efectos; el preflight estatico puede compartir el patron sin arrastrar la orquestacion de Docker del dry-run. Separar CLI de checks permite que `scripts/preflight/test_cost_readiness.py` pruebe guardas presentes y ausentes con fixtures, y que el preflight sea reutilizable como test estructural.
- **Alternativas consideradas**: (a) extender `scripts/dry_run/` — descartado porque el dry-run levanta el stack y no es costo-cero en el sentido de "sin Docker"; el preflight debe correr sin stack; (b) un test de pytest sin CLI — descartado porque el operador necesita un comando de preflight ejecutable antes de credentialear; (c) parsear `docker-compose.yml` a mano con expresiones regulares — descartado por fragilidad; se usa `yaml.safe_load` (PyYAML disponible en el entorno; el preflight falla ruidosamente si falta, nunca da falso PASS).

### D3 — Definicion de "nodo pago" para la guarda de reintentos

Se consideran pagos los nodos que ejecutan inferencia externa metrada: `@n8n/n8n-nodes-langchain.agent` y cualquier tipo que comience con `@n8n/n8n-nodes-langchain.lm` (el modelo de lenguaje, hoy `lmChatGoogleGemini`). La guarda falla si alguno declara `retryOnFail: true` o un `maxTries` numerico.

- **Razon**: el costo de Gemini se dispara por invocacion del agente/modelo; un reintento automatico multiplica llamadas pagas sin control. Excluir triggers (Outlook/Twilio) mantiene la guarda precisa: no son inferencia metrada por reintento del nodo.
- **Alternativas consideradas**: (a) incluir cualquier nodo con `retryOnFail` — descartado por falsos positivos en nodos no pagos; (b) solo el `AI Agent` — descartado porque el modelo puede reintentar por su cuenta si se configura en su nodo.

### D4 — Gate de corrida paga: `--confirm-paid` + `EVALUATION_CONFIRM_PAID`, condicionado al clasificador real

`main_con_corpus_real` recibe `confirm_paid: bool = False`. La logica del gate: si la corrida va a invocar al clasificador (cache invalido/ausente o `force=True`) **y** `classifier is None` (es decir, se resolveria el `HybridClassifier` real) **y** `confirm_paid` es falso, entonces se lanza `PaidRunNotConfirmedError` con un mensaje accionable y NO se invoca al clasificador. El CLI `main()` agrega `--confirm-paid` y lee `EVALUATION_CONFIRM_PAID` (valor verdadero = `1`/`true`/`yes`, case-insensitive); si el gate rechaza, imprime el mensaje y sale con codigo 2. Un cache hit nunca dispara el gate. Un clasificador inyectado (tests) nunca dispara el gate.

- **Razon**: condicionar el gate a `classifier is None` es lo que preserva todos los tests existentes de c-34 (inyectan `FakeClassifier`) y lo que distingue con precision el camino realmente pago del simulado. `--confirm-paid` es explicito y no interactivo (apto para CI); la variable de entorno permite el mismo opt-in sin cambiar la linea de comandos. El codigo de salida 2 distingue "rechazado por politica de costo" de un error de ejecucion (1).
- **Alternativas consideradas**: (a) prompt interactivo — descartado por romper CI y scripts; (b) confirmar siempre que `force=True` — descartado porque un clasificador inyectado en tests no es pago y romperia la suite; (c) un flag `--yes` generico — descartado por ambiguo; `--confirm-paid` nombra exactamente lo que se autoriza.
- **Compatibilidad**: `--force`/`--no-cache` conservan su semantica de cache. En el camino real, `--force` ahora ademas requiere confirmacion; en tests (clasificador inyectado) no cambia nada.

### D5 — Estimacion de costo orientativa

Se define `ESTIMATED_COST_PER_CALL_USD` (constante documentada, orden de magnitud para Gemini 2.5 Flash con un perfil de ~1.500 tokens de entrada y ~200 de salida por caso) y `estimated_cost_usd(corpus_count)`. Antes de invocar al clasificador pago se imprime: cantidad de casos, costo por llamada asumido y total estimado, con la aclaracion de que es orientativo y no una factura. El CLI permite override con `--estimated-cost-per-call`.

- **Razon**: el usuario necesita una nocion del gasto antes de confirmar; una constante explicita y overrideable evita hardcodear una verdad de facturacion y deja el supuesto a la vista. Se imprime solo cuando la corrida paga procede (un cache hit no reporta costo pago).
- **Alternativas consideradas**: (a) calcular tokens reales con un tokenizer — descartado por dependencia y por imprecision del perfil; (b) no estimar y solo exigir confirmacion — descartado porque el pedido incluye la estimacion.

### D6 — Limites de capacidad: nueva `cost-readiness` y delta de `evaluation-prediction-cache`

Se crea la capacidad nueva `cost-readiness` con el contrato del preflight, las guardas verificadas del workflow y del compose, y el tope de ejecucion del servicio N8N. El gate de corrida paga y la estimacion se agregan como requisitos de `evaluation-prediction-cache` (delta con `## ADDED Requirements`), no de `cost-readiness`.

- **Razon**: el gate de corrida paga pertenece al mismo runner cuyo comportamiento de cache ya gobierna `evaluation-prediction-cache`; mantener juntos el cache y el opt-in pago deja todo el comportamiento de costo del runner en una sola spec y evita que un lector tenga que cruzar dos capacidades para entender `run_evaluation.py`. `cost-readiness` agrupa lo que se verifica estaticamente antes de credentialear (preflight + tope de ejecucion N8N), que es una preocupacion distinta y de infraestructura. El `--force` existente no cambia de semantica de cache, por lo que se usa `ADDED` (nueva preocupacion) y no `MODIFIED`.
- **Alternativas consideradas**: (a) poner todo en `cost-readiness` — descartado porque fragmenta el contrato del runner de evaluacion entre dos specs; (b) extender `n8n-workflow` con el tope de ejecucion — descartado porque el tope es del servicio de compose, no del grafo del workflow; (c) `skip_specs` — descartado porque hay comportamiento verificable nuevo.

### D7 — Test de regresion de reintentos pagos en la suite estructural del workflow

El test que prohibe `retryOnFail`/`maxTries` en nodos pagos vive en `App/Backend/tests/test_n8n_workflow.py` (junto a las demas guardas estructurales de c-33, que CI ejecuta), ademas de ser un check del preflight. El preflight no importa la suite de backend ni viceversa; cada superficie lee `n8n/workflow.json` por su cuenta.

- **Razon**: el test en la suite del backend queda cubierto por CI (job `backend-tests`); el preflight cubre la ejecucion manual del operador. Duplicar la lectura del JSON es preferible a acoplar `scripts/preflight/` con `App/Backend/tests/`.
- **Alternativas consideradas**: (a) que el test importe el modulo del preflight — descartado por acoplamiento entre arboles; (b) solo el check del preflight — descartado porque el preflight no corre en CI.

### D8 — Ediciones de consistencia en docs y config

`docs/por_implementar.md`: se reemplaza el encabezado stale ("26 changes completos (C-01 a C-26). 309 tests pasando.") por una referencia vigente sin conteo hardcodeado, y se elimina la seccion "4.1 N8N usa imagen latest" junto con la fila "Baja | Pinear version N8N" de la tabla de prioridades, por estar resueltas en c-34. `openspec/config.yaml`: `orchestration.tool` pasa de "N8N 1.62 (Docker autoalojado)" a "N8N 2.11.2 (Docker autoalojado)".

- **Razon**: el conteo de tests y el pendiente del pin son afirmaciones verificables y hoy falsas; antes de credentialear inducen a error. Quitar el conteo (en vez de actualizarlo) evita que vuelva a rotar. Las ediciones son minimas y factuales; no se reescribe el documento.
- **Alternativas consideradas**: (a) actualizar el conteo a un numero nuevo — descartado porque vuelve a quedar stale; (b) borrar el documento — descartado por fuera de alcance.

## Risks / Trade-offs

- **[Valores de timeout arbitrarios]** 300/600 s son una eleccion operativa, no medida con carga real. -> Mitigacion: quedan declarados y verificables; si la operacion real los requiere distintos, es un cambio de una linea en el compose.
- **[PyYAML no declarado como dependencia]** El preflight usa `yaml.safe_load`; hoy PyYAML 6.0.1 esta disponible en el entorno pero no figura en un `requirements.txt`. -> Mitigacion: el modulo falla ruidosamente con mensaje accionable si falta (nunca falso PASS); se declara PyYAML en `scripts/preflight/requirements.txt`.
- **[Falso sentido de seguridad del preflight]** El preflight verifica estructura estatica, no comportamiento runtime. -> Mitigacion: su salida es explicita sobre que verifica; el arnés de c-31 sigue cubriendo el comportamiento end-to-end.
- **[El gate de corrida paga bloquea una corrida legitima]** Un usuario con cache invalido y sin confirmacion no corre. -> Mitigacion: el mensaje de rechazo nombra el flag y la variable de entorno; el codigo de salida 2 es distinguible.
- **[Estimacion imprecisa]** El costo por llamada es un orden de magnitud y puede desviarse del real. -> Mitigacion: se declara como orientativa, con supuestos visibles y override por CLI.
- **[Duplicacion del check de reintentos]** La guarda vive en la suite y en el preflight. -> Mitigacion: aceptada a cambio de desacoplar arboles; ambas leen la misma fuente (`n8n/workflow.json`).

## Migration Plan

1. Agregar `scripts/preflight/` (script, tests, `requirements.txt`) sin tocar el stack.
2. Agregar el gate y la estimacion en `evaluation/run_evaluation.py`, con sus tests.
3. CHECKPOINT HIGH: aprobar el plan exacto del environment de `n8n`; luego escribir `EXECUTIONS_TIMEOUT`/`EXECUTIONS_TIMEOUT_MAX` en `docker-compose.yml`.
4. Agregar el test de regresion en `App/Backend/tests/test_n8n_workflow.py`.
5. Actualizar `docs/por_implementar.md` y `openspec/config.yaml`.
6. Verificar con `openspec validate c-36-credentialing-readiness --strict`.

**Rollback**: revertir el commit revierte las ediciones de compose y docs; el preflight y el gate son aditivos y no afectan el runtime. Quitar las dos claves de environment deja el servicio como antes (sin tope), que es exactamente el estado a evitar, por lo que el rollback del compose debe ser una decision consciente.

## Open Questions

- Perfil exacto de tokens y precio vigente de Gemini 2.5 Flash para afinar `ESTIMATED_COST_PER_CALL_USD` (no cambia specs, enfoque ni tareas: la constante es orientativa y overrideable).
- Si conviene cablear el preflight a CI o al Makefile (fuera de alcance; follow-up).
- Si `EXECUTIONS_TIMEOUT=300` es el valor optimo una vez medidos los tiempos reales del tramo compartido (ajustable en una linea, sin cambio de spec).
