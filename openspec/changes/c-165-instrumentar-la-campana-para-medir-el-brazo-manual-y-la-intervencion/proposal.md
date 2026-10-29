# Proposal: Instrumentar la campana para medir el brazo manual y la intervencion

## Why

Una auditoria CONEAU acoto el criterio de metodologia porque el repositorio CARECE de instrumentacion para medir (a) la exactitud de clasificacion del BRAZO MANUAL y (b) la TASA DE INTERVENCION HUMANA. Sin instrumento ni protocolo de campana, ninguno de los dos datasets es producible ni verificable. Este es el primero de cinco changes (c-165..c-169); c-169 documentara los resultados.

## What Changes

- **Captura del brazo manual**: instrumento para registrar la clasificacion del operador por caso, por etiquetadores independientes, comparable contra la verdad de consenso (`sector_asignado`).
- **Registro de intervencion humana ampliado**: persistir actor (empleado id), instante de validacion propio, ORIGEN de la intervencion (gate/review/sample/completado manual/reasignacion) y delta de sector antes/despues.
- **Protocolo de campana** (runbook en repo) para producir ambos datasets: quien etiqueta, cuantos casos, independencia, instrumento, aceptacion/verificacion.
- **Metrica de tasa de intervencion REAL** (no solo `requiere_revision_humana`).

## Capabilities

### New Capabilities

- `evaluation-campaign-instrumentation`: instrumento de captura del brazo manual, protocolo de campana registrado y medicion de la tasa de intervencion real.

### Modified Capabilities

- `sector-assignment`: se MODIFICA `ASG-005` para persistir los metadatos de la intervencion (actor, instante propio, origen, delta antes/despues) junto al conjunto validado.

## Impact

- `App/Backend/app/models/clasificacion_log.py`, `repositories/clasificacion_repository.py`, `routes/clasificaciones.py`, `services/incidente_service.py`
- Nueva migracion Alembic (extender `clasificacion_log` o tabla dedicada)
- `App/Backend/app/repositories/estadisticas_repository.py` y `services/estadisticas_service.py` (tasa de intervencion real)
- `docs/` (runbook de campana); `data/` solo lectura del corpus pseudonimizado
- Specs: `openspec/specs/sector-assignment/` (modificado) y `evaluation-campaign-instrumentation/` (nueva)

### Out of Scope

- Ejecutar la campana de campo (corre fuera del repo; c-169 documenta resultados).
- Datos de campo reales, cambios a `docs/Tesis/v9 (IA)/`, strings de categorias o numeros canonicos.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Mutar el esquema de auditoria sin revision | Med | Governance ALTA: confirmacion humana obligatoria antes de aplicar el schema (design) |
| Etiquetado no independiente contamina la exactitud | Med | Protocolo exige >=2 etiquetadores independientes y sin ver la prediccion |
| Metrica de intervencion mal definida | Med | Distinguir marco (`requiere_revision_humana`) de intervencion efectiva |

## Rollback Plan

Revertir la migracion (`alembic downgrade`), retirar columnas/tabla y endpoint del instrumento, y eliminar el runbook. La tabla `clasificacion_log` existente y el corpus no se destruyen; las columnas nuevas son NULL-ables.

## Dependencies

- c-166..c-169 (programa de medicion); corpus pseudonimizado (`data/corpus_evaluacion_pseudonimizado.json`) ya versionado.

## Success Criteria

- [ ] Existe instrumento documentado y ejecutable para capturar el brazo manual por caso.
- [ ] El registro de intervencion persiste actor, instante, origen y delta de sector.
- [ ] Existe runbook de campana que define sujetos, N, independencia, instrumento y verificacion.
- [ ] `openspec validate --strict` en verde.
