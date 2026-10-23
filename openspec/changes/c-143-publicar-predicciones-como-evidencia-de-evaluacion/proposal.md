# Proposal: Publicar las predicciones como evidencia versionada

## Why

Las predicciones por caso (`evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json`) son la evidencia primaria de las métricas del Capítulo 7 y de la auditoría CONEAU: permiten recalcular cualquier métrica observada caso por caso. Hoy están excluidas del repositorio por `.gitignore`, con la justificación "derivan del corpus real, PII". Esa justificación es inexacta: el corpus pseudonimizado `data/corpus_evaluacion_pseudonimizado.json` SÍ se versiona y su `README` declara descripciones "sin PII residual", y el campo `descripcion` de las predicciones es byte-idéntico al del corpus (200/200 casos). Las predicciones no aportan PII nueva. A la vez, el archivo es un cache por spec (`evaluation-prediction-cache`): regenerable, con `cache_meta` y autoinvalidación, por lo que tampoco debe tratarse como fuente viva versionada. La decisión del owner es conservar el cache vivo gitignoreado y publicar una copia congelada como evidencia.

## What Changes

- Se publica una copia congelada de las predicciones bajo `evaluation/evidence/`, con nombres descriptivos que incluyen la versión del clasificador y la fecha de generación.
- Se documenta en `evaluation/evidence/README.md` qué es cada archivo, su `classifier_version`, `corpus_hash` y `generated_at`, cómo recalcular métricas por caso sin invocar Gemini (join por `caso_id` con el corpus público) y la advertencia de que el snapshot de calibración documenta un `corpus_hash` que NO coincide con el corpus actual.
- El cache vivo (`evaluation/predicciones.json`, `evaluation/predicciones_calibracion.json`) permanece gitignoreado y sin cambios; `.gitignore` NO se modifica.
- Se agrega un requisito a la capacidad `evaluation-prediction-cache` que declara la coexistencia de cache vivo (gitignoreado) y snapshot de evidencia versionado (copia byte-idéntica al cache en el momento de publicación).

## Capabilities

### New Capabilities

- (ninguna)

### Modified Capabilities

- `evaluation-prediction-cache`: se agrega el requisito de snapshot de evidencia versionado, byte-idéntico al archivo de cache en el momento de publicación, con el cache vivo permaneciendo gitignoreado.

## Impact

- `.gitignore` — SIN CAMBIOS (se preserva la exclusión del cache vivo).
- `evaluation/evidence/**` — nuevo (copia congelada + README).
- `openspec/specs/evaluation-prediction-cache/spec.md` — requisito nuevo vía delta spec.

## Follow-up pendiente

- `CHANGES.md` no se toca en este cambio: está siendo reescrito por el PR #40 y editarlo aquí produciría un conflicto. La incorporación de c-143 al roadmap queda como tarea de seguimiento una vez mergeado el PR.
