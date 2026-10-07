# Proposal: Calibracion del cortocircuito determinista por score de correctitud (c-74)

## Why

El cortocircuito determinista de la cascada se gobierna hoy por `confianza`, y esa
confianza NO predice correctitud. Medido OFFLINE sobre los 200 casos de
`data/corpus_evaluacion_pseudonimizado.json` (sin llamar a Gemini):

**Curva de calibracion (exactitud estricta por bucket de `confianza`)**

| Bucket `confianza` | n | Exactitud estricta |
|--------------------|---|--------------------|
| 0.0 | 90 | 0.7444 |
| 1/6 | 8 | 1.0000 |
| 0.5 | 26 | 0.7308 |
| 0.75 | 6 | 0.3333 |
| 1.0 | 1 | 1.0000 |

La relacion es NO monotona: el bucket 0.75 rinde 0.3333 y el 0.0 rinde 0.7444. Un
match unico (0.7444) es levemente MAS exacto que multi-match (0.7317), de modo que
el gate `min_matches >= 2` de c-71 es contraproducente.

**Metricas hibridas por politica de cortocircuito** (predicciones Gemini cacheadas,
recomputadas de forma identica a `run_evaluation.generar_reporte`):

| Politica | cortocircuitados | cobertura | strict | macro-F1 | micro-F1 | subset | hamming | jaccard |
|----------|------------------|-----------|--------|----------|----------|--------|---------|---------|
| A `conf >= 1.0` (vigente) | 1 | 0.005 | 0.6900 | 0.4605 | 0.6654 | 0.4100 | 0.3702 | 0.6298 |
| B cualquier prediccion no ambigua | 131 | 0.655 | 0.7300 | 0.5165 | 0.6654 | 0.4300 | 0.3586 | 0.6414 |
| C `max_score >= min_matches` (2) | 41 | 0.205 | 0.7050 | 0.4736 | 0.6654 | 0.4100 | 0.3686 | 0.6314 |

Sobre el subconjunto cortocircuitado el determinista supera a Gemini en TODOS los
buckets (p. ej. B: determinista 0.7405 vs Gemini 0.6794). El atajo determinista SI
aporta valor, pero el umbral de `confianza` no lo captura. Ningun umbral logra
cobertura alta Y el piso de precision 0.90 (OQ1 de c-71): en T=1.0 el cortocircuito
es nulo (1/200).

## What Changes

- Reemplazar la `confianza` ad-hoc como criterio de seleccion por un **score
  calibrado de correctitud** para el cortocircuito, ajustado con features
  deterministicas (score ganador, runner-up, margen, cantidad de matches, longitud
  del texto, senales por sector).
- Definir la **procedencia** de los datos de calibracion/validacion SIN fuga
  (README 8.1): conjunto held-out nuevo, split dev/test pre-registrado, o
  cross-fitting/conformal out-of-fold.
- Fijar un **punto de operacion** explicito (piso de precision y/o objetivo de
  cobertura) como decision del autor, que reemplaza/aumenta el piso 0.90.
- Reescribir, retirar o redefinir `deterministic_min_matches` dado que la evidencia
  lo muestra contraproducente.
- Mantener los disparadores de escalamiento `sin_prediccion` y `ambiguo` como estan.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `classification-resilience`: la decision de cortocircuito se gobierna por un score
  calibrado de correctitud y un punto de operacion, no por el umbral de `confianza`.
- `sector-assignment`: se redefine la confianza como medida de fuerza de senal (no de
  correctitud), se agrega el score calibrado de correctitud y la reevaluacion del
  gate de conteo minimo.
- `evaluation-framework`: se agrega el requisito de procedencia anti-fuga de los datos
  de calibracion y validacion.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/classifiers/deterministic.py` | Modified | Emite features de senal y el score calibrado; `min_matches` redefinido/retirado |
| `App/Backend/app/classifiers/hybrid.py` | Modified | Seleccion por score calibrado y punto de operacion |
| `App/Backend/app/config/settings.py` | Modified | Parametros del score y del punto de operacion |
| `App/Backend/app/constants.py` | Modified | `HYBRID_CACHE_VERSION` (invalidar cache si cambia la senal) |
| `evaluation/deterministic_measurement.py` | Modified | Calibracion con procedencia anti-fuga; `PISO_PRECISION_DEFAULT` revisado |
| `evaluation/` (runner, README, tests) | Modified | Reporte sobre el test set intocado; procedencia documentada |
| `App/Backend/tests/`, `evaluation/tests/` | Modified/New | TDD estricto y tests estructurales |
| `docs/deterministic_calibration.md`, `docs/` | Modified | Nuevo punto de operacion y procedencia |

## Governance

ALTO. El rediseno de la senal de confianza y el punto de operacion son decisiones del
autor (seccion OQ en `tasks.md`). El cambio alimenta las metricas de la tesis y, si
mueve el cortocircuito, altera la mezcla determinista/Gemini y su F1. No toca auth,
esquema persistente ni infraestructura. Rige la regla anti-fuga de datos: el corpus de
evaluacion es el conjunto de test reportado y NO puede usarse para ajustar la senal.

## Open Questions (autor)

- **OQ1**: enfoque del score de seleccion (seleccion/risk-controlled prediction vs
  modelo de calibracion: regresion logistica / isotonic / conformal).
- **OQ2**: procedencia de los datos de calibracion/validacion (held-out nuevo vs split
  dev/test pre-registrado vs cross-fitting/conformal out-of-fold) y su tradeoff.
- **OQ3**: punto de operacion objetivo (piso de precision y/o objetivo de cobertura),
  reemplazando/aumentando el piso 0.90 vigente.
- **OQ4**: destino de `deterministic_min_matches` (mantener / retirar / redefinir),
  dado que la evidencia lo muestra contraproducente.
- **OQ5**: confirmar que los disparadores `sin_prediccion` y `ambiguo` se mantienen
  sin cambios (restriccion, no decision abierta).

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Tuning sobre el corpus de evaluacion (data leakage) | Med | Procedencia anti-fuga obligatoria; test set intocado |
| El punto de operacion baja cobertura y sube costo Gemini | Med | Tradeoff explicito de OQ3; curva precision/cobertura documentada |
| El score calibrado no generaliza fuera de muestra | Med | Validacion out-of-fold; reportar en datos no usados para ajustar |
| Definir features usa informacion no disponible en runtime | Baja | Features derivables solo de la descripcion y el vocabulario |
| Tocar strings canonicos, keywords, prompt o `_a_float` | Baja | Prohibido por constraints; tests estructurales lo verifican |

## Rollback Plan

Revertir el commit restaura `deterministic.py`, `hybrid.py`, `settings.py` y
`constants.py` al comportamiento de c-71/c-72; si cambio `HYBRID_CACHE_VERSION`, el
cache de evaluacion previo vuelve a ser valido con la version anterior. Sin migraciones
ni cambios de esquema persistente: el rollback es puramente de codigo mas la version de
cache y no requiere pasos de datos.

## Dependencies

- `C-71` (archivado): determinista endurecido, no-match/empate y contrato de resultado.
- `C-72` (aplicado): unificacion telefonica a la cascada; comparte la senal de
  cortocircuito del backend.
- `C-34`/`C-58` (archivados): cache de predicciones (`HYBRID_CACHE_VERSION`) y
  resiliencia Gemini.
- Corpus `data/corpus_evaluacion_pseudonimizado.json` (200 casos, no trackeado).

## Success Criteria

- [ ] Existe un score calibrado de correctitud para el cortocircuito y su procedencia
      de datos NO es el corpus de evaluacion usado como test set reportado.
- [ ] El punto de operacion (piso de precision y/o cobertura) es una decision explicita
      del autor y esta documentado con su tradeoff.
- [ ] `deterministic_min_matches` queda justificado (mantenido, retirado o redefinido)
      con evidencia, no por inercia.
- [ ] Los disparadores `sin_prediccion` y `ambiguo` no cambian.
- [ ] La mezcla determinista/Gemini y su F1 quedan re-medidas sobre el corpus con la
      nueva senal, o la re-medicion queda declarada pendiente sin fabricar numeros.
- [ ] `openspec validate c-74-calibracion-cortocircuito-determinista --strict` pasa;
      tests TDD y estructurales en verde.
