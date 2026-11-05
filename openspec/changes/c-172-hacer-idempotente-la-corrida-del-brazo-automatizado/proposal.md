# Proposal: Corrida idempotente y reanudable del brazo automatizado

## Why

El harness de ingesta del brazo automatizado (`scripts/corpus_ingest/ingest_via_n8n.py`, canales web y correo) NO es idempotente ni reanudable: `write_sidecar_json` se invoca una sola vez al final (`:1386`), asi que una corrida interrumpida crea incidentes SIN sidecar y pierde toda la trazabilidad; y `run` reenvia todos los casos seleccionados (`:1331-1382`). El reenvio es patologico porque el backend deduplica por `origen_message_id` (`incidente_service.py:315-393`) y devuelve la fila EXISTENTE con `ingresado_en` INMUTABLE: en correo el guard `min_ingresado_en` rechaza el incidente viejo (`timeout_correlacion`, `:1152`) y en web la correlacion por `incidente_id` da una espera NEGATIVA que marca el caso `anomalo` en silencio (`derive_metric`, `:162-198`).

## What Changes

- **A (siempre activo)**: escribir el sidecar de forma INCREMENTAL tras cada caso dentro del loop, reutilizando el merge por `case_id` sin cambiar su semantica. Al arrancar, cargar el sidecar de la MISMA `id_corrida` y SALTAR los `case_id` con entrada VALIDA (`_should_write_metric`), reutilizando la medicion guardada.
- **B (tras `--resume`)**: sondear la existencia ANTES de enviar con el filtro exacto de c-69 (`GET /api/v1/incidentes/?origen_message_id=<key>`). Si el incidente ya existe: con entrada valida en el sidecar, saltar; sin ella (residuo de una corrida matada), registrar `error="incidente_preexistente_sin_t_envio"` SIN reenviar y SIN fabricar `t_e2e_s`/`espera` (politica B1: excluir y declarar, nunca inventar una medicion).
- Sin `--resume` el comportamiento por defecto NO cambia; las corridas de campana usan `--resume`. Se MANTIENE el guard `min_ingresado_en` y NO se adopta un id de correlacion por corrida (crearia incidentes duplicados y romperia el invariante de dedup de c-69).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `corpus-n8n-ingest`: nueva exigencia de reanudacion idempotente de la corrida del brazo automatizado (ledger incremental, skip por sidecar, sonda de pre-envio, politica B1).
- `evaluation-campaign-instrumentation`: nueva exigencia ECM-014 — reanudacion idempotente de la corrida de campana del brazo automatizado (flag `--resume`, ledger del sidecar por `id_corrida`).

## Impact

- Solo `scripts/corpus_ingest/ingest_via_n8n.py` y `scripts/corpus_ingest/test_ingest_via_n8n.py`. NO se tocan backend, DB, n8n ni `evaluation/`; NO cambia la semantica de merge de `write_sidecar_json`.
- **Dato existente**: los 17 incidentes creados por la corrida interrumpida tienen `ingresado_en` INMUTABLE y no se pueden "refrescar". Con B1 una re-corrida los encuentra, no los reenvia y los registra como preexistentes/no medibles. El plan de campana es RESETEAR la DB a un estado limpio antes de la corrida definitiva.
- TDD: la suite `test_ingest_via_n8n.py` es la red de seguridad. El test `test_un_sidecar_existente_con_el_mismo_id_corrida_se_reanuda` (`:2448`) documenta el contrato previo (reenvio de todos los casos) y sigue valido como caso "sin `--resume`"; el change agrega tests NUEVOS para el skip, la sonda y el ledger incremental.

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Un GET extra por caso frena la corrida | Med | Solo con `--resume`; reutiliza el filtro exacto indexado de c-69 |
| Un sidecar de otra `id_corrida` se salta por error | Low | El skip se limita a la `id_corrida` actual; se conserva `verificar_sidecar_de_corrida` |
| Un residuo se reporta como medible | Low | B1: se registra `error`, nunca un `t_e2e_s` inventado |

## Rollback Plan

Revertir el flag `--resume`, la sonda de pre-envio, el skip por sidecar y la escritura incremental (volver a llamar `write_sidecar_json` solo al final). Sin migracion de datos; el merge del sidecar y el guard `min_ingresado_en` no cambian.

## Dependencies

- c-166 (archivado): dueno de la instrumentacion de campana (`id_corrida`, sidecar por corrida).
- c-69 (archivado): dueno del filtro exacto `origen_message_id` y de la dedup de altas.

## Success Criteria

- [ ] Una corrida interrumpida tras N casos deja N entradas validas en el sidecar.
- [ ] Una re-corrida con `--resume` NO reenvia casos ya medidos y procesa los nuevos.
- [ ] Un incidente preexistente no se reenvia ni se marca `timeout_correlacion`/`anomalo`; se registra `incidente_preexistente_sin_t_envio`.
- [ ] Sin `--resume` la conducta por defecto no cambia; `openspec validate --strict` en verde.
