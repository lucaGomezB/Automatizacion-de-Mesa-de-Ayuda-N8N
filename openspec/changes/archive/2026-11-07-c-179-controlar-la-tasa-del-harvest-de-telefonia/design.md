# Design: Controlar la tasa del harvest de telefono

## Context

Ver `proposal.md` (Why) para la motivacion. El estado actual que condiciona el diseno:

- El harness de telefonia (`scripts/corpus_ingest/ingest_telefonia_corpus.py`) emite UN `GET /api/v1/telefonia/ingresos` por caso mediante `recover_telefonia_case` (`:160-190`) y los encadena en el loop principal (`:391-407`) sin pausa. El loop destructivo de `--replace` (`:409-432`) encadena de la misma forma los `DELETE`.
- El retry compartido es `ingest_corpus.py::_request_with_retry` (`:392-424`), con `MAX_ATTEMPTS = 3` (`:78`) y `BACKOFF_BASE_S = 1.0` (`:79`). Reintenta solo 5xx y timeouts; devuelve los 4xx de inmediato.
- nginx limita `/api/v1/telefonia/` (`location` en `nginx/nginx.conf:127`) con `limit_req zone=webhook_limit burst=20 nodelay` (`nginx/nginx.conf:128`, verificado; el limite de la zona `webhook_limit` esta en `nginx/nginx.conf:17`). `burst=20 nodelay` absorbe una rafaga de hasta 20 requests pero el ritmo sostenido del bucket es 1 r/s.
- Los harnesses hermanos ya tienen throttle: `ingest_via_n8n.py --sleep` (default `0.5`, `:1335`) e `ingest_corpus.py --sleep` (default `0.5`, `:514`). El harness de telefonia nunca lo recibio.
- El workaround de la campana en vivo (monkeypatch de `requests.Session.request` con `time.sleep(1.1)` via `runpy`) no esta versionado; este change lo reemplaza por una capacidad del propio harness.

## Goals / Non-Goals

**Goals:**

- Que el harvest de telefonia corra como lo documenta el runbook y respete el limite de nginx out-of-the-box.
- Robustez acotada ante 429 transitorios sin fabricar mediciones.
- Mantener la coherencia de nombre/semantica con los harnesses hermanos y cero cambios de comportamiento para los demas consumidores del retry.

**Non-Goals:**

- NO cambiar `webhook_limit` de nginx ni ningun control de infraestructura/seguridad (gobernanza mayor, c-62).
- NO cambiar `derive_telefonia_metric`, el write-back ni el formato del sidecar.
- NO agregar `--resume` al harness de telefonia (mejora futura posible, fuera de alcance).

## Decisions

**D1 - `--sleep` con default `1.1 s`, nombre y semantica iguales a los hermanos.**
El limite es `60r/m` = `1 r/s` sostenido. Un intervalo `S` da un ritmo `60/S r/m`; para quedar bajo 60 r/m hace falta `S > 1.0 s`. Se elige `1.1 s` (~54.5 r/m): deja margen para jitter de red y para el request de login y los `DELETE` de `--replace`, y `burst=20 nodelay` absorbe el arranque. Alternativas: `1.0 s` (justo en el limite, sin margen), `0.5 s` (default hermano; daria 120 r/m, excede el limite), `2.0 s` (seguro pero casi duplica el tiempo de los ~81 casos, ~160 s). Se mantiene `float` en segundos y el nombre `--sleep` por consistencia con `ingest_via_n8n.py:1335` e `ingest_corpus.py:514`. La pausa se aplica entre iteraciones del loop (`if index > 1 and sleep > 0`), como los hermanos: no espera antes del primer request.

**D2 - 429 como extension OPT-IN del helper compartido.**
Se agrega a `ic._request_with_retry` un parametro keyword-only nuevo (p. ej. `retry_statuses: Collection[int] | None = None`) que por defecto es `None` y preserva EXACTAMENTE la rama actual (5xx + timeouts, sin 4xx). Cuando el status de la respuesta esta en `retry_statuses`, se reintenta con backoff; si hay header `Retry-After`, se respeta su valor (segundos enteros, con tope `MAX_RETRY_AFTER_S` para no colgar la corrida) en lugar del backoff exponencial. Acotado por `max_attempts` (`MAX_ATTEMPTS = 3`). Agotados los intentos, se DEVUELVE la respuesta (no se levanta excepcion), igual que la rama 5xx actual: el caller ya mapea `>= 400` a una etiqueta de error, de modo que un 429 persistente se reporta sin fabricar `t_e2e_s`/`t_espera_s`/`t_pipeline_s`. El modulo de telefonia opta pasando `retry_statuses={429}` tanto en `recover_telefonia_case` como en `delete_previos`. Alternativa considerada: un wrapper local en el modulo de telefonia; se descarta porque duplica la logica de backoff y `Retry-After` y crea dos politicas de reintento que pueden divergir. Alternativa descartada: reintentar 429 globalmente en el helper; rompe la regla documentada "los 4xx no se reintentan" para los demas harnesses.

**D3 - Aplicacion de la pausa a nivel de loop, no dentro del caso.**
Cada caso emite un solo request HTTP (la recuperacion) y, con `--replace`, un `DELETE` adicional. Poner la pausa entre iteraciones del loop de recuperacion y entre iteraciones del loop de `--replace` cubre "entre requests consecutivos" sin meter `sleep` en la firma de `recover_telefonia_case`/`delete_previos` (que quedan testeables sin temporizacion). Coincide con el patron de los hermanos.

**D4 - Documentacion desde la fuente unica.**
`scripts/corpus_ingest/README.md` documenta el `--sleep` de telefonia en su tabla de flags (`:388-399`) y la robustez ante 429 en la seccion de telefonia (`:336-440`). El runbook (`docs/campana-medicion/runbook-campana-contrabalanceada.md`, seccion 5, item 4 de Telefonia, `:161-177`) y la guia (`docs/campana-medicion/guia-ejecucion-campana.md`, seccion 1.5.1, `:193-206`) agregan `--sleep` a los ejemplos del harvest. Se elimina toda referencia a un wrapper ad-hoc.

## Risks / Trade-offs

- **`Retry-After` enorme cuelga la corrida** -> tope `MAX_RETRY_AFTER_S` al sleep de 429, ademas del numero acotado de intentos.
- **La corrida tarda mas** (~89 s minimo para 81 casos con `1.1 s`) -> trade-off aceptado por reproducibilidad; el autor puede bajar `--sleep` a sabiendas del 429.
- **El parametro nuevo del helper compartido cambia a otros callers** -> keyword-only con default `None`; la rama por defecto no se toca y se cubre con un test de regresion en `test_ingest_corpus.py`.
- **`Retry-After` tambien aplica a 503** -> el parametro es una coleccion de codigos; la implementacion honra `Retry-After` para cualquier status reintentable, no solo 429 (sin efecto si el header no viene).

## Migration Plan

Sin migracion de datos. Despliegue: mergear el flag `--sleep`, el parametro opt-in del helper y la documentacion. Rollback: quitar el flag y su aplicacion, revertir el helper a la rama 5xx-only y deshacer los cambios de docs; el contrato del sidecar y la metrica no cambian, asi que el rollback no deja residuo.

## Open Questions

Ninguna que cambie specs, enfoque o tareas. La eventual reanudacion (`--resume`) del harness de telefonia queda declarada como mejora futura fuera de alcance.
