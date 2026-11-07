# Tasks: Controlar la tasa del harvest de telefono

TDD estricto (RED -> GREEN -> TRIANGULATE -> REFACTOR). Cada tarea RED escribe el test y lo ejecuta fallando por la razon esperada; cada GREEN escribe el minimo y lo ejecuta en verde; cada TRIANGULATE agrega un caso con otra entrada; cada REFACTOR re-ejecuta la suite. Alcance acotado: SOLO `scripts/corpus_ingest/ingest_telefonia_corpus.py`, `scripts/corpus_ingest/ingest_corpus.py` (parametro opt-in en `_request_with_retry`), sus tests y los tres documentos de `docs`/`README`. NO se tocan nginx, backend, DB, N8N, `evaluation/`, la metrica, el write-back ni el formato del sidecar.

Comandos de verificacion (desde la raiz del repo; la suite corre offline, ver `.github/workflows/ci.yml` job `corpus-ingest-tests`):

- Suite de telefonia: `python -m pytest scripts/corpus_ingest/test_ingest_telefonia_corpus.py -q`
- Suite del helper compartido: `python -m pytest scripts/corpus_ingest/test_ingest_corpus.py -q`
- Suite completa del harness: `python -m pytest scripts/corpus_ingest -q`

## 0. Safety net

- [x] 0.1 Ejecutar `python -m pytest scripts/corpus_ingest/test_ingest_telefonia_corpus.py -q` y registrar el baseline ("N passed"). Verificacion: todo en verde; si algo falla, frenar y reportarlo como falla preexistente sin arreglarlo.
- [x] 0.2 Ejecutar `python -m pytest scripts/corpus_ingest/test_ingest_corpus.py -q` y registrar el baseline. Verificacion: todo en verde (red de seguridad para el cambio del helper compartido).
- [x] 0.3 Identificar en los tests existentes los fakes reutilizables (`FakeSession`/`FakeResponse` en `test_ingest_telefonia_corpus.py:40-61`) y el patron de monkeypatch de red (`itc.recover_telefonia_case`, `ivn.login`). Verificacion: los tests nuevos los reutilizan sin duplicar infraestructura.

## 1. RED — 429 opt-in en el helper compartido (`test_ingest_corpus.py`)

- [x] 1.1 RED: test de que `ic._request_with_retry` con el parametro opt-in de reintento de 4xx (p. ej. `retry_statuses={429}`), ante una respuesta 429 seguida de una 200, reintenta y devuelve la respuesta 200; con un fake de sesion que cuenta llamadas y `monkeypatch.setattr(ic.time, "sleep", ...)` que registra los sleeps. Verificacion: falla porque el parametro no existe / el 429 se devuelve de inmediato.
- [x] 1.2 RED: test de que un 429 PERSISTENTE (todas las respuestas 429) con opt-in agota los intentos, DEVUELVE la respuesta 429 (no levanta excepcion) y no infiere ninguna medicion. Verificacion: falla por el comportamiento actual.
- [x] 1.3 RED (regresion): test de que sin opt-in (default) un 429 se devuelve de inmediato con una sola llamada al fake de sesion, preservando la regla "los 4xx no se reintentan". Verificacion: falla mientras 1.1-1.2 no esten implementados o si el cambio altera el default.
- [x] 1.4 RED (`Retry-After`): test de que cuando la respuesta 429 trae header `Retry-After: 2`, el sleep registrado es `2` (no el backoff exponencial) y que un `Retry-After` desmesurado se recorta al tope. Verificacion: falla porque hoy no se honra el header.

## 2. GREEN — Implementar el opt-in en `ic._request_with_retry`

- [x] 2.1 GREEN: agregar a `_request_with_retry` (`ingest_corpus.py:392-424`) un parametro keyword-only `retry_statuses: Collection[int] | None = None`; cuando el status este en la coleccion, reintentar con backoff acotado por `max_attempts`. Verificacion: 1.1, 1.2 y 1.3 en verde.
- [x] 2.2 GREEN (`Retry-After`): parsear el header `Retry-After` (segundos enteros) y usarlo como sleep, recortado a un tope `MAX_RETRY_AFTER_S`; ausente o no parseable -> backoff exponencial. Verificacion: 1.4 en verde.
- [x] 2.3 GREEN (default intacto): con `retry_statuses=None` la rama 5xx/timeout queda identica a la previa y los 4xx se devuelven de inmediato. Verificacion: 1.3 en verde y baseline de 0.2 sin regresiones.

## 3. RED — throttle `--sleep` en el harness de telefonia (`test_ingest_telefonia_corpus.py`)

- [x] 3.1 RED: test de que `itc.parse_args([])` expone `--sleep` con default `1.1` (float) y que acepta un valor explicito. Verificacion: falla porque el flag no existe.
- [x] 3.2 RED: test de que, al procesar dos o mas casos de recuperacion con `--sleep S > 0`, se registra una pausa de `S` entre requests consecutivos y NO antes del primer request. Monkeypatch de `itc.time.sleep` (o inyeccion) que registra los valores; fake de recuperacion que cuenta llamadas. Verificacion: falla porque hoy no hay pausa.
- [x] 3.3 RED: test de que en el loop de `--replace` (con `--confirm-replace`) la pausa tambien se aplica entre los `DELETE` consecutivos. Verificacion: falla porque hoy no hay pausa.
- [x] 3.4 RED: test de que `recover_telefonia_case` y `delete_previos` reintentan un 429 (opt-in) usando el helper compartido con el codigo 429 habilitado. Fake de sesion que devuelve 429 y luego 200 (recuperacion) y 429 y luego 200 (DELETE). Verificacion: falla porque hoy el 429 no se reintenta.

## 4. GREEN — Implementar `--sleep` y el opt-in 429 en telefonia

- [x] 4.1 GREEN: agregar `parser.add_argument("--sleep", type=float, default=1.1)` a `parse_args` (`ingest_telefonia_corpus.py:267-304`) con ayuda en espanol que explique el respeto de `webhook_limit`. Verificacion: 3.1 en verde.
- [x] 4.2 GREEN: aplicar la pausa entre iteraciones del loop de recuperacion (`:391-407`) y del loop de `--replace` (`:409-432`), con la guarda `index > 1 and args.sleep > 0` (mismo patron que `ingest_corpus.py:604-605`). Verificacion: 3.2 y 3.3 en verde.
- [x] 4.3 GREEN: pasar el opt-in de 429 al helper compartido en `recover_telefonia_case` (`:177-185`) y `delete_previos` (`:213-221`) sin alterar las firmas publicas salvo el codigo a reintentar. Verificacion: 3.4 en verde y baseline de 0.1 sin regresiones.

## 5. TRIANGULATE — Casos adicionales por escenario

- [x] 5.1 TRIANGULATE: `--sleep 0` no genera ninguna llamada a `time.sleep`; un unico caso seleccionado tampoco espera (no hay par consecutivo). Verificacion: en verde.
- [x] 5.2 TRIANGULATE: 429 agotado en telefonia produce la etiqueta de error (`http429...`) y el sidecar/write-back no escribe `t_e2e_s`/`t_espera_s`/`t_pipeline_s` para ese caso. Verificacion: en verde.
- [x] 5.3 TRIANGULATE: sin header `Retry-After`, el helper usa backoff exponencial (`backoff_base * 2**(attempt-1)`). Verificacion: en verde.
- [x] 5.4 TRIANGULATE (no regresion de otros callers): `login` y `post_incidente` siguen devolviendo un 4xx de inmediato (sin opt-in). Verificacion: en verde en `test_ingest_corpus.py`.

## 6. REFACTOR

- [x] 6.1 REFACTOR: actualizar el docstring del modulo de telefonia, el `--help` de `--sleep` y el docstring de `_request_with_retry` para declarar el throttle y la robustez ante 429; extraer el parseo de `Retry-After` a un helper puro y testeable. Verificacion: `python -m pytest scripts/corpus_ingest -q` en verde.
- [x] 6.2 REFACTOR: confirmar por lectura que `derive_telefonia_metric`, `write_back` y la semantica de `--replace` no cambiaron de comportamiento. Verificacion: `git diff` no muestra cambios de logica en esas funciones.

## 7. Documentacion

- [x] 7.1 Documentar en `scripts/corpus_ingest/README.md`: `--sleep` de telefonia en la tabla de flags (`:388-399`) y un parrafo de throttle + robustez ante 429 en la seccion de telefonia (`:336-440`), con el default `1.1` y el motivo (`60r/m`, `burst=20`). Verificacion: el README menciona `--sleep` y `429` en la seccion de telefonia.
- [x] 7.2 Actualizar el runbook (`docs/campana-medicion/runbook-campana-contrabalanceada.md`, seccion 5, item 4 de Telefonia, `:161-177`) y la guia (`docs/campana-medicion/guia-ejecucion-campana.md`, seccion 1.5.1, `:193-206`) para incluir `--sleep` en los ejemplos del harvest y explicar el respeto del limite. Verificacion: los ejemplos de telefonia documentan el throttle.
- [x] 7.3 Eliminar de la documentacion toda dependencia de un wrapper ad-hoc externo al repositorio para el harvest de telefonia. Verificacion: `rg -i "runpy|monkeypatch.*Session.request|wrapper.*sleep" docs/campana-medicion scripts/corpus_ingest/README.md` sin coincidencias que describan el procedimiento vigente.

## 8. Validacion y cierre

- [x] 8.1 Ejecutar `openspec validate c-179-controlar-la-tasa-del-harvest-de-telefonia --strict --no-interactive`. Verificacion: en verde.
- [x] 8.2 Re-ejecutar `python -m pytest scripts/corpus_ingest -q` y confirmar los baselines de 0.1 y 0.2 sin regresiones. Verificacion: en verde.
- [x] 8.3 Confirmar con `git diff --stat` que SOLO se tocaron `scripts/corpus_ingest/ingest_telefonia_corpus.py`, `scripts/corpus_ingest/ingest_corpus.py`, los tests de `scripts/corpus_ingest/`, los dos runbooks de `docs/campana-medicion/` y `scripts/corpus_ingest/README.md`, mas los artefactos OPSX del change. Verificacion: sin nginx, backend, DB, N8N ni `evaluation/` en el diff.
