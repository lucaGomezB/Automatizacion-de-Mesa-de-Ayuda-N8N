# Proposal: Contrabalanceo del diseno y corpus independiente

## Why

La auditoria CONEAU acoto el criterio de metodologia por dos razones que el repositorio hoy no puede refutar: (d) el diseno pareado es SECUENCIAL y NO CONTRABALANCEADO, por lo que el efecto de orden no es estimable (`04-marco-metodologico.tex:14`), y (c) NO existe un corpus INDEPENDIENTE/out-of-sample, por lo que las metricas de clasificacion son in-sample (`08-discusion.tex:18`). Sin codigo ni protocolo que habiliten una corrida contrabalanceada y una validacion sobre corpus independiente, esas objeciones no pueden contestarse con evidencia. Segundo de cinco changes (c-165..c-169); c-169 documentara los resultados.

## What Changes

- **Control de orden/brazo en los harnesses de ingesta**: parametro `--orden {directo,inverso,alternado,aleatorio}` (con `--seed` para reproducibilidad) aplicado en `select_cases`/orden de procesamiento, y campo `orden` por caso en el sidecar. **BREAKING** menor: el sidecar gana un campo (consumidores que validen claves exactas deben tolerarlo).
- **Protocolo de campana contrabalanceada** (runbook versionado): asignacion de mitades, forma de estimar el efecto de orden (primera vs segunda mitad, o termino de orden) y criterio de aceptacion.
- **Protocolo + ruta de harness para corpus INDEPENDIENTE**: sin solape con el corpus de ajuste (200 casos), mismo protocolo de pseudonimizacion y doble etiquetado, y reporte out-of-sample de las metricas de ambas etapas.

## Capabilities

### New Capabilities

- `evaluation-campaign-instrumentation`: c-166 AGREGA requisitos ECM-004.. al instrumento/protocolo que c-165 introduce (ECM-001..003). Ambos changes escriben la misma capability; se fusionan al archivar. Secuencia: c-165 primero.

### Modified Capabilities

- None. El control de orden se modela como instrumentacion de campana (ECM), no como cambio de contrato de `corpus-n8n-ingest`.

## Impact

- `scripts/corpus_ingest/ingest_via_n8n.py` (CLI, `select_cases`, `CaseResult`, sidecar), `ingest_corpus.py`, `ingest_telefonia_corpus.py` y sus suites `scripts/corpus_ingest/test_*.py`.
- `docs/` (runbook de contrabalanceo + runbook de corpus independiente).
- `evaluation/` (reporte out-of-sample; se conserva el cross-fitting within-corpus de tau, no se toca).
- Sin cambios: strings de categorias, numeros canonicos, `docs/Tesis/v9 (IA)/`.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Confundir orden con canal/brazo (colinealidad residual) | Med | Aleatorizar/contrabalancear por mitad y registrar `orden` por caso |
| Sidecar rompe consumidores por campo nuevo | Low | Campo aditivo NULL-able; tests de compatibilidad |
| Corpus "independiente" solapa el de ajuste | Med | Protocolo exige verificacion explicita de no solape de ids/descripciones |
| Aleatorio no reproducible | Low | `--seed` obligatorio en modo aleatorio |

## Rollback Plan

Revertir el parametro `--orden`/`--seed`, retirar el campo `orden` del sidecar (los consumidores ignoran claves desconocidas) y eliminar los runbooks. No hay migracion de datos ni datos de campo; el corpus versionado y los numeros canonicos no se tocan.

## Dependencies

- c-165 (introduce `evaluation-campaign-instrumentation`); corpus pseudonimizado versionado; c-167..c-169 consumen el instrumento.

## Success Criteria

- [ ] Los tres harnesses aceptan `--orden` (y `--seed`) y registran `orden` por caso en el sidecar, con TDD en sus suites.
- [ ] Existe runbook que define asignacion de mitades y estimacion del efecto de orden.
- [ ] Existe protocolo + ruta de harness para un corpus independiente con verificacion de no solape y reporte out-of-sample.
- [ ] `openspec validate --strict` en verde.
