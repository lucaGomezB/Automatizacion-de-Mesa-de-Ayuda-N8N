# Proposal: Contrabalanceo del diseño y corpus independiente

## Why

La auditoría CONEAU acotó el criterio de metodología por dos razones que el repositorio hoy no puede refutar: (d) el diseño pareado es SECUENCIAL y NO CONTRABALANCEADO, por lo que el efecto de orden no es estimable (`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:14`), y (c) NO existe un corpus INDEPENDIENTE/out-of-sample, por lo que las métricas de clasificación son in-sample (`08-discusion.tex:18`). El efecto de orden que importa es el del **operador humano**: la tesis (04:14) lo enmarca como "efecto de aprendizaje del operador humano" y la KB (`knowledge-base/11_evaluacion_experimental.md:56`) define el contrabalanceo como "mitad procesada primero manual, la otra primero automatizada". Reordenar el envío del brazo automatizado no produce ese efecto (una máquina no aprende ni se fatiga): lo que hace falta es un **plan de campaña por caso** que asigne a cada caso su posición, su mitad y qué brazo va primero, y que lo sigan tanto el operador manual como los harnesses. La revisión previa al apply (`docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md`, T3 y sección c-166) marcó además que las corridas de campaña, con los defaults actuales, pisarían los tiempos canónicos y que `run_evaluation.py` sobrescribiría el cache de predicciones si se lo apunta a otro corpus. Segundo de cinco changes (c-165..c-169); c-169 documentará los resultados.

## What Changes

- **Plan de campaña por caso (contrabalanceo de CONDICIÓN)**: módulo nuevo `evaluation/plan_campana.py` con `ordenar_casos(casos, modo, seed)` (modos `directo|inverso|alternado|aleatorio`) y `generar_plan_campana(casos, modo, seed) -> list[AsignacionCaso]`, que asigna por caso `id_caso, posicion, mitad, brazo_primero, modo, seed` de modo que en cada mitad la mitad de los casos se procese manual-primero y la otra mitad automatizado-primero. Se exporta a `evaluation/data/campana/plan_campana.csv`. El plan guía al brazo manual (fuera del repo), a los harnesses de ingesta y al operador del softphone.
- **Harnesses siguen el plan**: `ingest_via_n8n.py` e `ingest_corpus.py` aceptan `--plan <csv>` (envían en el orden del plan) y `--orden/--seed` como atajo que genera el plan al vuelo; `ingest_telefonia_corpus.py` **no ingesta** (recupera mediciones por `corpus_case_id`; el orden de las llamadas lo decide el operador del softphone) y con `--plan` solo copia `posicion/mitad/brazo_primero` al sidecar. `CaseResult` y `CorpusResult` ganan al final, con default `None`, `orden`, `posicion`, `mitad`, `brazo_primero`, `id_corrida`. Cambio **aditivo**: los sidecars históricos siguen leyéndose.
- **Protección de lo congelado en los harnesses**: con `--plan` (o `--orden`) el harness exige `--sidecar` propio de la corrida y `--json` apuntando a la copia de campaña `evaluation/data/campana/corpus_campana.json`, y aborta antes de enviar nada si apuntan a archivos versionados (`data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json`). `--limit` se aplica antes del orden.
- **Protocolo de campaña contrabalanceada** (`docs/campana-medicion/runbook-campana-contrabalanceada.md`): reparto por `brazo_primero`, cómo el operador manual sigue el plan, qué registra la planilla de c-168 con `tarea=brazo_manual` y criterio de aceptación (contrabalanceo efectivo registrado por caso). La estimación del efecto de orden es de c-167.
- **Corpus independiente**: `evaluation/no_solape.py::verificar_no_solape(ajuste, candidato)` (prefijo `I` obligatorio, ids disjuntos, SHA-256 de la descripción normalizada, advertencia opcional por similitud Jaccard; declara que no detecta paráfrasis); flags nuevos `--corpus`, `--predicciones`, `--reporte` en `evaluation/run_evaluation.py` con protección de `evaluation/predicciones.json` y `evaluation/report.md`; runbook `docs/campana-medicion/runbook-corpus-independiente.md` (clasificador congelado, sin recalibración, plantilla y validador de c-168, `--confirm-paid`). El reporte out-of-sample NO es de este change: lo hace c-167 (`evaluar_fuera_de_muestra`).
- **CI**: job nuevo en `.github/workflows/ci.yml` que corre las suites de `scripts/corpus_ingest/` (hoy fuera del gate: CI solo corre `evaluation/`, el backend y `scripts/preflight`).

## Capabilities

### New Capabilities

- `evaluation-campaign-instrumentation`: c-166 AGREGA ECM-004..ECM-007 a la capability que también escriben c-165 (ECM-001..003) y c-168 (ECM-008..010). Se fusionan al archivar; el archive es seguro en cualquier orden (sin ADDED repetidos, sin MODIFIED). El `## Purpose` de la capability se completa a mano después del primer archive.

### Modified Capabilities

- None. El plan de campaña se modela como instrumentación de campaña (ECM), no como cambio de contrato de `corpus-n8n-ingest`, `telefonia-corpus-medicion` ni `evaluation-framework`: los flags nuevos son opcionales y los defaults conservan la conducta actual.

## Impact

- **Módulos nuevos (en CI)**: `evaluation/plan_campana.py`, `evaluation/no_solape.py`; tests `evaluation/tests/test_plan_campana.py`, `evaluation/tests/test_no_solape.py`.
- **`evaluation/run_evaluation.py`**: `main()` (:1523) gana `--corpus`, `--predicciones`, `--reporte` cableados a `main_con_corpus_real` (:1376, que ya acepta las rutas); protección contra `PREDICCIONES_PATH`/`REPORT_PATH` (:82-83) cuando el corpus no es `CORPUS_REAL_PATH` (:81); test en `evaluation/tests/test_run_evaluation.py`.
- **Harnesses**: `scripts/corpus_ingest/ingest_via_n8n.py` (`parse_args` :1145, `select_cases` :575, `CaseResult` :519-541, `write_sidecar_json` :728, `run` :1213), `scripts/corpus_ingest/ingest_corpus.py` (`CorpusResult` :190-205, `write_sidecar_json` :358, `parse_args` :485, `_select_cases` :507), `scripts/corpus_ingest/ingest_telefonia_corpus.py` (`build_telefonia_result` :115, `write_back` :229, `parse_args` :260, `run` :314). Sus suites viven junto al código: `scripts/corpus_ingest/test_ingest_via_n8n.py`, `scripts/corpus_ingest/test_ingest_corpus.py`, `scripts/corpus_ingest/test_ingest_telefonia_corpus.py` (no hay subcarpeta `tests/`).
- **CI**: `.github/workflows/ci.yml` gana el job `corpus-ingest-tests`, de modo que el TDD de este change queda en el gate.
- **Datos**: carpeta nueva `evaluation/data/campana/` (README con SHA-256, patrón `evaluation/evidence/`) para el plan, la copia de campaña del corpus, los sidecars por corrida y las predicciones del corpus independiente (`predicciones_independiente.json`); actualizar `evaluation/data/README.md`.
- **Docs**: `docs/campana-medicion/runbook-campana-contrabalanceada.md`, `docs/campana-medicion/runbook-corpus-independiente.md`.
- **Sin cambios**: `docs/Tesis/v9 (IA)/` (congelada), cadenas de categorías (`evaluation/corpus.py:52-58`), números canónicos, `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json`, `evaluation/predicciones.json`, `evaluation/report.md`, el cross-fitting within-corpus de tau.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Mitad y orden de condición confundidos | Med | `brazo_primero` alterna por posición dentro de cada mitad; `verificar_balance` falla si la diferencia supera 1 caso |
| Una corrida de campaña pisa los tiempos canónicos o un sidecar versionado | Med | Abort en código, con test, si `--json`/`--sidecar` apuntan a archivos versionados; sidecar propio por corrida |
| `run_evaluation.py` contra otro corpus sobrescribe el cache o el reporte v9 | Med | Con `--corpus` no canónico, `--predicciones` y `--reporte` son obligatorios y no pueden ser los canónicos |
| Corpus "independiente" solapa el de ajuste | Med | `verificar_no_solape` como paso previo obligatorio (también dentro de `run_evaluation.py`); se declara que no detecta paráfrasis |
| Plan aleatorio no reproducible | Low | `aleatorio` exige `--seed`; la semilla queda en cada fila del plan |
| Campos nuevos rompen consumidores de sidecars | Low | Campos al final con default `None`; test con sidecar histórico |

## Rollback Plan

Revertir los flags `--plan/--orden/--seed/--id-corrida` y `--corpus/--predicciones/--reporte`, retirar los campos nuevos de `CaseResult`/`CorpusResult` (los consumidores ignoran claves desconocidas), quitar `evaluation/plan_campana.py`, `evaluation/no_solape.py`, el job de CI y los runbooks. No hay migración de datos; el corpus versionado, los sidecars versionados y los números canónicos no se tocan en ningún camino.

## Dependencies

- **c-165**: comparte la capability `evaluation-campaign-instrumentation`; c-166 no depende de su migración ni del checkpoint de gobernanza ALTA.
- **c-168**: dueño de la plantilla `evaluation/data/plantilla_etiquetado.csv` y del validador `evaluation/doble_etiquetado.py::validar_doble_etiquetado`, que el runbook de corpus independiente usa (ECM-006) y que el runbook contrabalanceado referencia para `tarea=brazo_manual`.
- **c-167**: consume el plan y los sidecars para estimar el efecto de orden (pareo por caso entre corridas, posición desde el plan) y es dueño de `evaluar_fuera_de_muestra` y del reporte con bloques in-sample/out-of-sample.
- **c-169**: documenta los resultados en la tesis v10.

## Success Criteria

- [ ] `generar_plan_campana` produce un plan reproducible y balanceado por mitad, exportado a CSV, con tests en `evaluation/tests/` (en CI).
- [ ] `ingest_via_n8n.py` e `ingest_corpus.py` siguen `--plan` y registran `posicion/mitad/brazo_primero/id_corrida` por caso; `ingest_telefonia_corpus.py` copia el plan al sidecar; los tres abortan ante archivos versionados.
- [ ] `run_evaluation.py` acepta `--corpus/--predicciones/--reporte` y protege `evaluation/predicciones.json` y `evaluation/report.md`.
- [ ] `verificar_no_solape` existe en `evaluation/no_solape.py` con tests.
- [ ] Existen los dos runbooks bajo `docs/campana-medicion/`.
- [ ] Las suites de `scripts/corpus_ingest/` corren en CI.
- [ ] `openspec validate --strict` en verde y `git diff --stat` sin los archivos congelados.
