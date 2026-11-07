# Proposal: Controlar la tasa del harvest de telefono

## Why

El harvest del corpus de telefonia (`scripts/corpus_ingest/ingest_telefonia_corpus.py`) NO respeta el limite de tasa del API: recupera una medicion por caso con un solo `GET /api/v1/telefonia/ingresos` (`recover_telefonia_case`, `:160-190`) y el loop principal (`:391-407`) emite esos requests SIN ninguna pausa entre ellos. nginx limita `/api/v1/telefonia/` con `limit_req zone=webhook_limit burst=20 nodelay` (`nginx/nginx.conf:128`) y `webhook_limit` es `60r/m` (`nginx/nginx.conf:17`), de modo que barrer los ~81 casos del plan telefonia en rafaga excede la tasa y devuelve `429`. El retry compartido `_request_with_retry` (`scripts/corpus_ingest/ingest_corpus.py:392-424`) reintenta SOLO 5xx y timeouts de red: un 4xx (incluido el 429) se devuelve de inmediato y se convierte en la etiqueta de error del caso, asi que correr el harvest como lo documenta el runbook FALLA con 429 y la medicion se pierde. El trabajo ad-hoc que se uso en la campana en vivo (un wrapper que monkeypatcheaba `requests.Session.request` con `time.sleep(1.1)` via `runpy`) NUNCA se consolido en la herramienta ni quedo versionado: la reproducibilidad de la tesis depende de que el harvest funcione out-of-the-box.

## What Changes

- **Throttle (`--sleep`)**: agregar a `ingest_telefonia_corpus.py` un flag `--sleep` (float, segundos) aplicado entre requests HTTP CONSECUTIVOS, tanto en el loop de recuperacion (`:391-407`) como en el loop de `--replace`/`--confirm-replace` (`:409-432`). Default SEGURO `1.1 s` (ver design: `60 r/m = 1 r/s` mas `burst=20 nodelay`), con la misma semantica y nombre que el `--sleep` hermano de `ingest_via_n8n.py` (`:1335`, default `0.5`) e `ingest_corpus.py` (`:514`).
- **429 robusto (opt-in en el helper compartido)**: extender `ic._request_with_retry` con un parametro opcional de codigos a reintentar (por defecto `None` = solo 5xx, comportamiento actual intacto) que, ante un 429, reintenta con backoff exponencial y HONRA el header `Retry-After` si esta presente, hasta un numero acotado de intentos; agotados, devuelve la respuesta 429 para que el caso se reporte como etiqueta de error SIN fabricar `t_e2e_s`/`t_espera_s`/`t_pipeline_s`. Solo el modulo de telefonia opta por reintentar 429; los demas callers NO cambian.
- **Docs**: quitar la necesidad del wrapper ad-hoc y documentar el throttle en el harness de telefonia, en el runbook de campana (`docs/campana-medicion/runbook-campana-contrabalanceada.md`, seccion 5, item 4 de Telefonia: `:161-177`) y en la guia (`docs/campana-medicion/guia-ejecucion-campana.md`, seccion 1.5.1: `:193-206`), y documentar el nuevo `--sleep` de telefonia en `scripts/corpus_ingest/README.md` (seccion de telefonia, tabla de flags: `:388-399`).
- **Tests**: extender `scripts/corpus_ingest/test_ingest_telefonia_corpus.py` (y `test_ingest_corpus.py` si se toca el helper compartido) cubriendo (a) que el `--sleep` se aplica ENTRE requests y (b) que un 429 se reintenta con backoff y termina en exito o en un error acotado sin metrica fabricada.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `telefonia-corpus-medicion`: nueva exigencia de respeto de la tasa del API durante el harvest de telefonia (throttle `--sleep` entre requests consecutivos de recuperacion y de `--replace`), robustez ante 429 (reintento con backoff que honra `Retry-After`, acotado, sin fabricar medicion) y documentacion del throttle en el runbook y el README. No cambia la metrica canonica, el write-back, el formato del sidecar ni la semantica de `--replace`.

## Impact

- **Codigo**: `scripts/corpus_ingest/ingest_telefonia_corpus.py` (flag `--sleep`, aplicacion entre requests, opt-in de 429) y `scripts/corpus_ingest/ingest_corpus.py` (parametro opcional nuevo en `_request_with_retry`, sin cambio de comportamiento por defecto).
- **Docs**: `docs/campana-medicion/runbook-campana-contrabalanceada.md`, `docs/campana-medicion/guia-ejecucion-campana.md`, `scripts/corpus_ingest/README.md`.
- **Tests**: `scripts/corpus_ingest/test_ingest_telefonia_corpus.py`, `scripts/corpus_ingest/test_ingest_corpus.py`.
- **Sin cambios**: nginx/`webhook_limit` (control de infraestructura y seguridad de c-62), el backend, la base de datos, N8N, `evaluation/`, la logica de `derive_telefonia_metric`, el write-back y el formato del sidecar.

## Out of Scope

- NO se cambia el limite de tasa de nginx (`webhook_limit`) ni ningun control de infraestructura/seguridad; ese es un artefacto de endurecimiento de c-62 y cambiarlo seria una decision de gobernanza mayor.
- NO se cambia la logica de la metrica (`derive_telefonia_metric`), el write-back ni el formato de los sidecares de la campana.
- Agregar `--resume` al harness de telefonia queda FUERA DE ALCANCE (mejora futura posible); este change no lo requiere.

## Risks

| Riesgo | Probabilidad | Mitigacion |
|--------|--------------|------------|
| Honorar un `Retry-After` enorme cuelga la corrida | Baja | Tope al sleep de 429 (constante) ademas del numero acotado de intentos |
| El parametro nuevo del helper cambia la conducta de otros callers | Baja | Parametro opcional con default `None`; la rama 5xx/solo-timeout queda identica |
| Un default de `--sleep` mas agresivo alarga la corrida | Media | `1.1 s` es el minimo seguro bajo 60 r/m; el autor puede bajarlo consciente del 429 |

## Rollback Plan

Revertir el flag `--sleep` y su aplicacion entre requests, quitar el parametro opcional de `_request_with_retry` (volver a la rama 5xx-only) y deshacer los cambios de documentacion. Sin migracion de datos ni cambios de contrato del sidecar.

## Dependencies

- c-70 (archivado): dueno del harness de recuperacion de telefonia (`telefonia-corpus-medicion`).
- c-62 (archivado): dueno del limite de tasa de nginx (`webhook_limit`) que este change respeta sin modificar.

## Success Criteria

- [ ] `ingest_telefonia_corpus.py --sleep` existe con default `1.1` y se aplica ENTRE requests consecutivos en recuperacion y en `--replace`.
- [ ] Un 429 se reintenta con backoff honrando `Retry-After`, acotado; agotado, el caso se reporta como error sin metrica fabricada.
- [ ] Los demas callers de `_request_with_retry` conservan su comportamiento (5xx/timeout, sin reintento de 4xx).
- [ ] El runbook y el README documentan el throttle sin depender del wrapper ad-hoc.
- [ ] `openspec validate --strict` y la suite `scripts/corpus_ingest` en verde.
