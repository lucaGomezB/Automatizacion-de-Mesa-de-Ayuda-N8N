# Proposal: Plantilla y protocolo de doble etiquetado

## Why

El kappa `0,87` se reporta SIN intervalo de confianza porque la tabla primaria de
acuerdo no se conservo: solo existe el consenso `sector_asignado`, sin etiquetas por
etiquetador (`numeros-canonicos.md:198-209`). Sin plantilla ni protocolo que
reconstruyan esa tabla, el IC del kappa no es computable y la tesis no puede cerrar la
limitacion. Cuarto de cinco changes (c-165..c-169); el etiquetado real corre fuera del
repositorio.

## What Changes

- **Plantilla de doble etiquetado**: esquema CSV/JSON con `id_caso`, `id_etiquetador`,
  `sector_asignado`, `sectores_adicionales` y `timestamp`, mas una herramienta offline
  minima que registra y valida dos etiquetados independientes por caso (cobertura
  completa, celdas sin faltantes, strings de categoria exactos).
- **Protocolo (runbook)**: elegibilidad de etiquetadores, cegado (sin ver el consenso ni
  al otro etiquetador), mismo codebook, tamano de muestra (re-etiquetar los 200 casos o
  un subconjunto justificado) y criterios de aceptacion.
- **Ruta de recuperacion opcional**: si reaparece data parcial por etiquetador original,
  se valida y se registra; el camino por defecto sigue siendo el re-etiquetado.
- Salida consumible por c-167 (`evaluation/kappa.py`), que calcula kappa + IC.

## Capabilities

### New Capabilities

- `evaluation-campaign-instrumentation`: c-168 AGREGA requisitos ECM-008.. al
  instrumento/protocolo introducido por c-165 (ECM-001..003) y extendido por c-166
  (ECM-004..007). Varios changes escriben la misma capability; se fusionan al archivar.
  Secuencia: c-165, c-166, luego c-168.

### Modified Capabilities

- None. El doble etiquetado se modela como instrumentacion de campana (ECM), no como
  cambio de contrato de `evaluation-framework` (que c-167 modifica).

## Impact

- `evaluation/` (plantilla + validador offline) y `evaluation/tests/` (tests sin red).
- `docs/` (runbook de doble etiquetado independiente).
- Sin cambios a `docs/Tesis/v9 (IA)/`, strings de categorias (LOCKED) ni numeros
  canonicos. Sin datos de campo en el repositorio: solo la plantilla y el protocolo.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Etiquetadores no independientes | Med | Protocolo exige cegado y agentes distintos; validador rechaza duplicados de etiquetador |
| Consenso contamina el re-etiquetado | Med | El protocolo prohibe exponer `sector_asignado` antes de etiquetar |
| Cobertura parcial del corpus | Med | Validador exige una celda por etiquetador y caso; falla accionable |
| Derivar strings de categoria | Baja | Validador compara contra las cinco cadenas canonicas exactas |

## Rollback Plan

Eliminar la plantilla, el validador offline, sus tests y el runbook. No hay migraciones
ni cambios de esquema; el corpus versionado, c-167 y los numeros canonicos quedan
intactos.

## Dependencies

- `evaluation-campaign-instrumentation` (c-165, c-166); corpus pseudonimizado
  `data/corpus_evaluacion_pseudonimizado.json`; c-167 consume la tabla resultante.

## Success Criteria

- [ ] Existe plantilla con `id_caso`, `id_etiquetador`, sector(es) y timestamp.
- [ ] Existe validador offline que verifica dos etiquetados por caso y cobertura total.
- [ ] Existe runbook de doble etiquetado independiente con criterios de aceptacion.
- [ ] `openspec validate --strict` en verde.
