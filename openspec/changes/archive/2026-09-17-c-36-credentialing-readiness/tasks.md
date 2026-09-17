## 0. Baseline, dependencias y gobernanza

- [x] 0.1 Registrar el baseline de las suites afectadas antes de tocar nada: `cd App/Backend; pytest -m "not integration" -q` y `cd evaluation; pytest -q`. Anotar la cantidad de tests en verde y confirmar que corren sin modificaciones. Verificacion: baseline anotado en el change. **Baseline 2026-09-17: backend SQLite `349 passed, 22 deselected, 1 xfailed`; evaluation `54 passed`.**
- [x] 0.2 Confirmar dependencias archivadas: `openspec list --json` y `ls openspec/changes/archive/ | grep -E "c-33|c-34"`. Verificacion: c-33 y c-34 aparecen archivadas; el preflight asume sus guardas. **Confirmado: `2026-09-17-c-33-cost-guards` y `2026-09-17-c-34-evaluation-prediction-cache` archivadas.**
- [x] 0.3 CHECKPOINT DE GOBERNANZA HIGH: antes de escribir `docker-compose.yml`, presentar el plan exacto (`EXECUTIONS_TIMEOUT: "300"` y `EXECUTIONS_TIMEOUT_MAX: "600"` en el environment del servicio `n8n`) y obtener aprobacion humana explicita; registrarla en el change. Verificacion: aprobacion registrada antes de empezar el grupo 6. **APROBADO por el usuario 2026-09-17: se autoriza agregar exactamente `EXECUTIONS_TIMEOUT: "300"` y `EXECUTIONS_TIMEOUT_MAX: "600"` al environment del servicio `n8n`, con comentario explicativo; ningun otro cambio en el compose.**
- [x] 0.4 Confirmar que c-36 NO modifica `n8n/workflow.json`: `git diff --stat n8n/workflow.json` debe quedar vacio al final del change. Verificacion: sin diferencias en el workflow. **Confirmado al cierre: `git diff --stat n8n/workflow.json` vacio.**

## 1. RED — Checks puros del preflight

- [x] 1.1 Crear `scripts/preflight/test_cost_readiness.py` con un fixture de workflow valido (copia del artefacto real) y otro mutado sin `options.maxIterations`; escribir el test que exige FAIL en el mutado y PASS en el valido. Verificacion: el test FALLA (RED) porque `cost_readiness` todavia no existe (fallo esperado de import para modulo nuevo).
- [x] 1.2 Escribir el test del lookback del trigger de Outlook (24 h + `readStatus=unread`) con un caso mutado sin lookback. Verificacion: RED por ausencia del modulo/funcion.
- [x] 1.3 Escribir el test de alcanzabilidad de `Marcar correo como leido` desde exito/rechazo/error con un caso mutado que corta la rama de rechazo. Verificacion: RED.
- [x] 1.4 Escribir el test del body enriquecido (`origen_message_id` + clasificacion precalculada + marcador de evento) con un caso mutado sin el bloque. Verificacion: RED.
- [x] 1.5 Escribir el test del webhook dedicado `notificacion-clasificacion` aislado de la creacion de incidentes. Verificacion: RED.
- [x] 1.6 Escribir el test de la guarda de reintentos: un nodo pago (`@n8n/n8n-nodes-langchain.agent` o `@n8n/n8n-nodes-langchain.lm*`) con `retryOnFail: true`/`maxTries` produce FAIL. Verificacion: RED.
- [x] 1.7 Escribir los tests del compose: imagen pineada (FAIL con `latest`), `N8N_WEBHOOK_URL` a la ruta dedicada, `EXECUTIONS_TIMEOUT` presente, y coherencia `MAX >= default`. Verificacion: RED.
- [x] 1.8 Escribir el test del contrato de salida: `exit_code` es 0 solo si todo es PASS y 1 si hay algun FAIL; el resumen nombra cada check. Verificacion: RED.
- [x] 1.9 Ejecutar `python -m pytest scripts/preflight/test_cost_readiness.py -q` y confirmar RED (fallo esperado por modulo ausente); registrar la evidencia. **RED confirmado: `ModuleNotFoundError: No module named 'cost_readiness'`.**

## 2. GREEN — Implementacion del preflight

- [x] 2.1 Crear `scripts/preflight/cost_readiness.py` con `Check`, `check_workflow(path)`, `check_compose(path)`, `run_preflight(...)`, `exit_code(checks)` y `format_summary(checks)`, usando `yaml.safe_load` para el compose y `json` para el workflow; sin acceso a red ni Docker. Verificacion: los tests 1.1-1.8 pasan (GREEN). **GREEN: 24 passed.**
- [x] 2.2 Implementar el CLI (`--workflow`, `--compose`) que imprime la lista PASS/FAIL y sale 0/1. Verificacion: `python scripts/preflight/cost_readiness.py` sale 0 contra los artefactos actuales y sale 1 al apuntar a un workflow mutado. **CLI verificado: workflow real + compose fixture -> 0; workflow mutado -> 1. Contra el repo antes de 6.1 sale 1 por `EXECUTIONS_TIMEOUT` ausente (esperado; 6.2 lo confirma en 0).**
- [x] 2.3 Crear `scripts/preflight/requirements.txt` declarando PyYAML y hacer que la importacion ausente de `yaml` produzca un FAIL accionable, nunca un falso PASS. Verificacion: test que simula `yaml` ausente y exige FAIL con mensaje que nombra la dependencia. **Test `test_yaml_missing_produces_actionable_fail` en verde.**
- [x] 2.4 TRIANGULATE: agregar al menos un caso mutado por guarda (workflow y compose) y confirmar que cada mutacion produce exactamente un FAIL nombrando la guarda. Verificacion: suite del preflight en verde. **24 casos: cada guarda tiene al menos una mutacion; `_assert_single_named_fail` exige un unico FAIL nombrado.**
- [x] 2.5 REFACTOR: extraer helpers de navegacion del workflow (busqueda por nombre/tipo, BFS de alcanzabilidad, deteccion de nodos pagos) sin cambiar comportamiento; re-ejecutar la suite. Verificacion: `python -m pytest scripts/preflight/test_cost_readiness.py -q` en verde tras cada refactor. **BFS unificado en `_bfs_first`; 24 passed; `ruff check` limpio.**

## 3. RED — Gate de corrida paga de la evaluacion

- [x] 3.1 En `evaluation/tests/test_run_evaluation.py`, escribir el test de cache miss sin confirmacion: con corpus fixture y `classifier=None` (o un clasificador real simulado) y sin `confirm_paid`, el runner lanza `PaidRunNotConfirmedError` y NO invoca al clasificador. Verificacion: el test FALLA (RED) porque el gate no existe.
- [x] 3.2 Escribir el test de cache hit sin confirmacion: con cache valido y sin `confirm_paid`, el runner carga del cache y no lanza ni invoca al clasificador. Verificacion: RED o verde si el comportamiento ya existe; si ya pasa, dejarlo como regresion.
- [x] 3.3 Escribir el test de confirmacion por `confirm_paid=True` (flag) y por entorno (`EVALUATION_CONFIRM_PAID=1`) en el CLI: ambas permiten la corrida paga. Verificacion: RED.
- [x] 3.4 Escribir el test de clasificador inyectado: con `FakeClassifier` y sin confirmacion, el runner clasifica sin exigir confirmacion. Verificacion: RED o regresion (debe quedar verde tras GREEN).
- [x] 3.5 Escribir el test de `--force` ortogonal: `force=True` con clasificador real y sin confirmacion rechaza la corrida paga. Verificacion: RED.
- [x] 3.6 Escribir el test de la estimacion: antes de la corrida paga se imprime la cantidad de casos y el costo estimado; con cache hit no se imprime costo pago. Verificacion: RED.
- [x] 3.7 Ejecutar `cd evaluation; pytest tests/test_run_evaluation.py -q` y confirmar RED por asercion; registrar la evidencia. **RED: 9 failed / 16 passed por asercion (sin invocar Gemini; el clasificador real se sustituye por un spy).**

## 4. GREEN — Gate y estimacion de costo

- [x] 4.1 Definir `PaidRunNotConfirmedError`, `ESTIMATED_COST_PER_CALL_USD` y `estimated_cost_usd(corpus_count)` en `evaluation/run_evaluation.py`. Verificacion: los tests 3.5 y 3.6 pasan.
- [x] 4.2 Agregar `confirm_paid: bool = False` a `main_con_corpus_real` e implementar el gate condicionado a que la corrida invoque al clasificador y `classifier is None`; imprimir la estimacion antes de clasificar. Verificacion: tests 3.1-3.6 en verde.
- [x] 4.3 Agregar `--confirm-paid` al CLI y la lectura de `EVALUATION_CONFIRM_PAID` (verdadero = `1`/`true`/`yes`, case-insensitive); capturar `PaidRunNotConfirmedError` e imprimir mensaje accionable saliendo con codigo 2. Verificacion: tests 3.3 en verde; `python -m evaluation.run_evaluation` sin corpus real falla claro y no invoca Gemini. **Tests de CLI en verde; el rechazo sale con codigo 2 y nombra `--confirm-paid`.**
- [x] 4.4 Confirmar la no-regresion del cache de c-34: `cd evaluation; pytest tests/test_run_evaluation.py -q` completo en verde (incluidos hit, invalidacion y `--force` con `FakeClassifier`). **25 passed.**
- [x] 4.5 REFACTOR: extraer la impresion de la estimacion a un helper puro y re-ejecutar la suite. Verificacion: `cd evaluation; pytest -q` en verde. **`format_cost_estimation` puro; suite completa `67 passed`; `ruff check` limpio.**

## 5. RED — Regresion de reintentos pagos en la suite estructural

- [x] 5.1 En `App/Backend/tests/test_n8n_workflow.py`, agregar el test que falla si un nodo pago (`@n8n/n8n-nodes-langchain.agent` o `@n8n/n8n-nodes-langchain.lm*`) declara `retryOnFail: true` o `maxTries`. Verificacion: el test pasa sobre el workflow actual (caracterizacion) y FALLA al inyectar `retryOnFail: true` en una copia temporal del JSON (triangulacion que prueba que la guarda realmente guarda). **Guardas + 2 tests de mutacion en verde; la mutacion inyectada es detectada.**
- [x] 5.2 Ejecutar `cd App/Backend; pytest tests/test_n8n_workflow.py -q` y confirmar la suite completa en verde. Verificacion: sin regresiones en los contratos estructurales de c-33. **`83 passed, 1 xfailed`; `ruff check .` limpio.**

## 6. HIGH — Tope de ejecucion del servicio N8N (con checkpoint del 0.3)

- [x] 6.1 Con la aprobacion del 0.3 registrada, agregar `EXECUTIONS_TIMEOUT: "300"` y `EXECUTIONS_TIMEOUT_MAX: "600"` al environment del servicio `n8n` en `docker-compose.yml`, con un comentario que explique el proposito. Verificacion: `docker compose config` resuelve ambas variables y no hay cambios fuera de `docker-compose.yml`. **Aplicado con comentario; `docker compose config` resuelve `EXECUTIONS_TIMEOUT=300` y `EXECUTIONS_TIMEOUT_MAX=600`; imagen `n8nio/n8n:2.11.2`.**
- [x] 6.2 Ejecutar el preflight contra el compose editado: `python scripts/preflight/cost_readiness.py` sale 0. Verificacion: los checks de compose (imagen pineada, webhook dedicado, timeout presente y coherente) reportan PASS. **`RESULT: 10/10 guardas en PASS`, exit 0.**

## 7. Docs y config

- [x] 7.1 (Resuelto ANTES del apply en un commit chore, para no duplicar) Actualizar `docs/por_implementar.md`: encabezado vigente y seccion 4.1 / fila de prioridad de n8n marcadas como resueltas por C-34.
- [x] 7.2 (Resuelto ANTES del apply en un commit chore) Actualizar `openspec/config.yaml`: `orchestration.tool` a "N8N 2.11.2 (Docker autoalojado, imagen pinneada)" y `migrations` con la 005.
- [x] 7.3 Verificar consistencia entre specs, design y artefactos: nombres de claves (`EXECUTIONS_TIMEOUT`, `EXECUTIONS_TIMEOUT_MAX`), rutas (`notificacion-clasificacion`) y flags (`--confirm-paid`, `EVALUATION_CONFIRM_PAID`). Verificacion: coinciden literalmente con los tests implementados. **Verificado por barrido de tokens: las claves aparecen en spec/design/tasks/codigo/tests/compose; las flags en spec-eval/design/tasks/runner/tests.**

## 8. Verificacion final

- [x] 8.1 Ejecutar `cd App/Backend; pytest -m "not integration" -q` y confirmar el subconjunto SQLite en verde (incluye la guarda de reintentos). **`352 passed, 22 deselected, 1 xfailed` (baseline 349 + 3 nuevos).**
- [x] 8.2 Ejecutar `cd evaluation; pytest -q` y confirmar la suite de evaluacion en verde (gate, estimacion y cache de c-34). **`67 passed` (baseline 54 + 13 nuevos).**
- [x] 8.3 Ejecutar `python -m pytest scripts/preflight/test_cost_readiness.py -q` y confirmar el preflight en verde. **`24 passed`.**
- [x] 8.4 Ejecutar `python scripts/preflight/cost_readiness.py` contra el repo final y confirmar codigo de salida 0 con todas las guardas en PASS. **`RESULT: 10/10 guardas en PASS`, exit 0.**
- [x] 8.5 Ejecutar `openspec validate c-36-credentialing-readiness --strict` y confirmar PASS. **`Change 'c-36-credentialing-readiness' is valid`.**
- [x] 8.6 Confirmar con `git status --porcelain` que no quedan artefactos temporales ni secretos, y que `n8n/workflow.json` no fue modificado. **`git diff --stat n8n/workflow.json` vacio; solo los 4 archivos previstos + `scripts/preflight/` + el change. Compose: exactamente las 2 variables aprobadas + comentario.**

## 9. Fixes post-verificacion (W1/W2/W3)

- [x] 9.1 (W-1) Endurecer `_check_executions_timeout_coherent` en `scripts/preflight/cost_readiness.py`: ambas cotas son obligatorias. Un compose sin `EXECUTIONS_TIMEOUT_MAX` ahora produce FAIL nombrando la clave (antes devolvia PASS "no evaluable: falta una de las cotas"); la ausencia de `EXECUTIONS_TIMEOUT` la sigue reportando `_check_executions_timeout_present` para no duplicar el FAIL; con ambas presentes se mantiene la coherencia `MAX >= default`. Verificacion: RED previo (`test_compose_missing_executions_timeout_max_fails_named` fallaba con 0 FAILs), GREEN con `26 passed`; el test de coherencia existente sigue verde.
- [x] 9.2 (W-1) TRIANGULATE: agregar `test_compose_missing_both_timeouts_fails_without_false_pass` (sin ambas cotas: un unico FAIL y exit 1). Verificacion: `python3 -m pytest scripts/preflight/test_cost_readiness.py -q` -> `26 passed`.
- [x] 9.3 (W-2) Reemplazar el encabezado con conteos hardcodeados de `docs/por_implementar.md` por una referencia vigente sin numeros (`openspec list`, `openspec/changes/archive/` y CI como fuentes de verdad), fechada. Verificacion: el encabezado ya no contiene `349`/`54`/`121`/`35 changes`; el resto del documento queda intacto.
- [x] 9.4 (W-3) Resolver el clasificador real de forma perezosa en `evaluation/run_evaluation.py`: `_version_clasificador_real()` lee la clave de version desde el modulo liviano `app.constants` (nueva constante `HYBRID_CACHE_VERSION`, unica fuente de verdad que `HybridClassifier.CACHE_VERSION` reutiliza) sin importar `app.classifiers` (que arrastra `app.core.database` -> `get_settings()`); el gate + `_resolver_clasificador_real()` se evaluan solo cuando la corrida paga va a clasificar (cache miss o `--force`). Un cache hit con `classifier=None` ya no exige `GEMINI_API_KEY`. Verificacion: RED previo (`test_cache_hit_no_resuelve_clasificador_real` fallaba porque el runner llamaba al resolver real antes del cache), GREEN con `26 passed` en `tests/test_run_evaluation.py` y triangulacion manual del camino real sin credenciales.
- [x] 9.4b (W-3, desvio necesario) Extraer la version a `app.constants.HYBRID_CACHE_VERSION` y hacer que `HybridClassifier.CACHE_VERSION` la referencie: importar `app.classifiers.hybrid` ejecuta `app.core.database` -> `get_settings()` al importar, por lo que leer el atributo de clase no era libre de credenciales. Guarda de consistencia en `App/Backend/tests/test_hybrid_classifier.py` (`test_cache_version_es_unica_fuente_compartida`). Verificacion: backend SQLite `353 passed` (baseline 352 + 1).
- [x] 9.5 (W-3) Preservar la semantica de c-34/c-36: `_resolver_a` fija tambien la version del clasificador para los tests con `classifier=None`; `--force`, `--confirm-paid`, `PaidRunNotConfirmedError`, exit 2 y la estimacion siguen verdes. Verificacion: `cd evaluation; pytest -q` -> `69 passed` (67 baseline + 2 nuevos).
- [x] 9.6 Verificacion final de los fixes: backend SQLite, evaluation, preflight, CLI del preflight (exit 0), ruff y `openspec validate --strict` en verde. Verificacion: comandos de cierre registrados en el reporte del apply.
