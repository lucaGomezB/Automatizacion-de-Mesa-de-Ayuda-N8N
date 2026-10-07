# Tareas — c-74-calibracion-cortocircuito-determinista

> Governance: ALTO. Modo TDD estricto (RED-GREEN-TRIANGULATE-REFACTOR) en todo el codigo.
> Cada tarea de codigo que modifica un archivo existente arranca con una safety net (correr los tests actuales del area y registrar la linea base; si algo falla, reportarlo como fallo pre-existente y NO corregirlo).
> Los gates de la seccion 0 los resuelve el autor; las tareas dependientes NO se ejecutan hasta que su gate este resuelto.
> Restricciones duras: NO cambiar los cinco strings canonicos, `KEYWORD_MAP`, el prompt de Gemini ni `evaluation/corpus.py::_a_float`. El corpus de evaluacion es el test reportado y NO se usa para ajustar la senal.

## 0. Prerequisitos y gates de decision (autor)

- [x] 0.1 (Gate OQ1) RESUELTO por el autor (2026-10-07): **Conformal / risk-controlled prediction** con calibracion out-of-fold. Criterio de la seccion 1.
- [x] 0.2 (Gate OQ2) RESUELTO por el autor (2026-10-07): **(iii) cross-fitting / conformal out-of-fold**. La senal se ajusta en folds que excluyen el fold evaluado y las metricas se reportan out-of-fold; el test reportado nunca se usa para ajustar. Criterio de la seccion 2.
- [x] 0.3 (Gate OQ3) RESUELTO por el autor (2026-10-07): prioridad en precision con **piso objetivo 0.85**, derivado de la curva de calibracion sobre datos de calibracion (dev/OOF) y fijado ANTES de observar el test. Reemplaza el piso 0.90. Criterio de la seccion 4.
- [x] 0.4 (Gate OQ4) RESUELTO por el autor (2026-10-07): **convertir `deterministic_min_matches` en feature del score** (no como gate binario). Ver ASG-011; NO debe ser el criterio de seleccion. Criterio de las secciones 1 y 3.
- [x] 0.5 (OQ5, confirmado) Los disparadores `sin_prediccion` y `ambiguo` se mantienen sin cambios; este change solo toca la condicion de cortocircuito con senal dominante.
- [x] 0.6 Safety net global: corrido. Baseline: backend `pytest -m "not integration"` 991 passed (39 deselected, 1 xfailed); evaluation 79 passed; calibracion offline actual umbral 1.0 / cobertura 0.005 (1/200), curva con tau=0 -> 131 cortocircuitados precision 0.7405 cobertura 0.6550. Sin fallos pre-existentes.

## 1. Score calibrado de correctitud (TDD)

- [x] 1.1 Safety net: 48 passed en `test_deterministic_classifier.py` + `test_hybrid_classifier.py`. Sin fallos.
- [x] 1.2 (RED) Tests del contrato del score (ASG-010) en `tests/test_deterministic_correctness_score.py`; fallaron por ImportError (`FeaturesDeterministas`) contra la implementacion previa.
- [x] 1.3 (GREEN, gate OQ1) `extraer_features` + `score_correctitud` puros en `deterministic.py`; parametros en `settings.py`; campo aditivo `score_correctitud` en `ClasificacionResult`. 20 passed.
- [x] 1.4 (TRIANGULATE) Casos: un match, multi-match, margen cero, margen maximo, texto vacio y largo. 20 passed.
- [x] 1.5 (REFACTOR) Funciones puras extraidas; 20 passed.

## 2. Procedencia y calibracion anti-fuga (TDD)

- [x] 2.1 Safety net: evaluation 79 passed; curva vigente registrada (umbral 1.0, cobertura 0.005). Sin fallos.
- [x] 2.2 (RED) Test estructural de procedencia en `evaluation/tests/test_calibracion_oof.py`; fallo por ImportError (`PROCEDENCIA_CROSS_FITTING`).
- [x] 2.3 (GREEN, gate OQ2) `asignar_folds`, `seleccionar_umbral`, `calibrar_out_of_fold` en `evaluation/deterministic_measurement.py` (cross-fitting OOF; sin Gemini; sin tocar `_a_float`). 11 passed.
- [x] 2.4 (TRIANGULATE) Cubre particion por defecto, piso inalcanzable y ajuste en complemento del fold. 11 passed.
- [x] 2.5 (REFACTOR) Helpers de curva compartidos; 11 passed.

> BLOQUEO detectado al cerrar la seccion 2 (afecta la seccion 4 / OQ3): ningun score alcanza el piso 0.85 con cobertura util. Ver nota de desviacion al final.

## 3. Seleccion del cortocircuito por score (TDD)

- [x] 3.1 Safety net: 68 passed (`test_deterministic_classifier.py` + `test_hybrid_classifier.py` + `test_deterministic_correctness_score.py`). Sin fallos.
- [x] 3.2 (RED) Test del cortocircuito gobernado por el score vs el punto de operacion comparativo. 4 tests fallaron (gate por score ausente).
- [x] 3.3 (GREEN) `hybrid.py` consume `score_correctitud` vs el punto de operacion; `sin_prediccion`/`ambiguo` escalan incondicional. 73 passed.
- [x] 3.4 (TRIANGULATE) Score alto/bajo, `sin_prediccion`, ambiguo y match unico. Tests en verde.
- [x] 3.5 (REFACTOR) Condicion de cortocircuito limpiada. Tests en verde.
- [x] 3.6 (Gate OQ4) `deterministic_min_matches` es feature (no gate); test ASG-011 en verde.

## 4. Punto de operacion, re-medicion y documentacion

- [x] 4.1 (Gate OQ3, comparativo) Punto de operacion fijado: tau = 0.5166; cobertura 0.6550 (131/200); precision_det 0.7405 >= precision_gem 0.6769 (OOF, Gemini cacheado). Piso absoluto retirado como criterio.
- [x] 4.2 (RED) Test de invalidacion de cache por bump de version; `hybrid-v2` ahora invalida. 
- [x] 4.3 (GREEN) `HYBRID_CACHE_VERSION` bumpeado `hybrid-v2` -> `hybrid-v3`.
- [x] 4.4 (Medicion) Hibrido (offline, Gemini cacheado): estricta 0.7300, macro-F1 0.5165, micro-F1 0.6654, subset 0.4300, Hamming 0.3586, Jaccard 0.6414. Delta vs baseline (0.6900/0.4605): +0.0400/+0.0560; cobertura 0.005 -> 0.655. Sin Gemini, sin tocar `_a_float`.
- [x] 4.5 Documentado en `docs/deterministic_calibration.md` y Anexo H (punto comparativo, procedencia, delta).
- [x] 4.6 (Medicion paga) Corrida paga hybrid-v3 ejecutada (2026-10-07, autor confirmo): exit 0, 69 llamadas Gemini (131 cortocircuitos), 0 errores, ~USD 0.0138. Oficial: estricta 0.7350 (147/200, IC [0.6698, 0.7913]), macro-F1 0.5207, micro-F1 0.6654, subset 0.4300, Hamming 0.3586, Jaccard 0.6414; etapas det 131 / gemini 69 / fallback 0. `cache_meta` = hybrid-v3.

## 5. Verificacion final

- [x] 5.1 `pytest -m "not integration"` 1016 passed; `ruff check .` limpio.
- [x] 5.2 `cd evaluation; pytest` 118 passed.
- [x] 5.3 Strings canonicos, `KEYWORD_MAP`, prompt de Gemini y `_a_float` intactos (sin diff; tests estructurales en verde).
- [x] 5.4 `openspec validate ... --strict` pasa.

## Notas de desviacion

- (Se completa durante el apply: decision de cada OQ, valores medidos, cualquier deuda detectada.)
- **BLOQUEO (2026-10-07, fin de Fase A):** el piso OQ3 de 0.85 es inalcanzable con cobertura util. Score a priori: a precision>=0.85 solo 1/200 (cobertura 0.005). Modelos aprendidos OOF (k=5): LogisticRegression KFold precision>=0.85 -> cobertura 0.060 (12/200); HistGradientBoosting e Isotonic no alcanzan 0.85 en ningun umbral. Curva alcanzable (LogReg): >=0.80 -> cobertura ~0.33-0.45; >=0.75 -> ~0.625; >=0.70 -> 0.655. Causa: ruido de etiqueta (34/131 cortocircuitables incorrectos, precision base 0.740) y solo 8 features runtime. PENDIENTE: revision de OQ3 por el autor antes de la seccion 3/4.
- **RESOLUCION OQ3 (autor, 2026-10-07):** criterio COMPARATIVO. El determinista (0.740) supera a Gemini (0.677) en el conjunto cortocircuitable; se maximiza cobertura sujeto a `precision_det >= precision_gem` OOF. Resultado: tau=0.5166, cobertura 0.655 (131/200), hibrido macro-F1 0.5165 (delta +0.056 vs cache hybrid-v2). Se retira el piso absoluto. `PISO_PRECISION_DEFAULT` (0.90) y los helpers de curva absoluta se conservan por compatibilidad de tests de la Fase A; el punto de operacion se gobierna solo por el criterio comparativo. `precision_gem=0.6769` sobre 130 (1 caso cortocircuitable sin prediccion Gemini cacheada, excluido, no fabricado).
- **Corrida paga oficial (2026-10-07):** hybrid-v3, 69 llamadas Gemini, 0 errores. Oficial macro-F1 0.5207 / estricta 0.7350 (vs offline 0.5165 / 0.7300). Delta vs baseline hybrid-v2 off (0.4605): +0.0602 macro.
- **Convencion de dos caches (resuelta):** `evaluation/predicciones.json` = cache de la corrida OFICIAL (hybrid-v3, escrito por `run_evaluation.py`); `evaluation/predicciones_calibracion.json` = cache FORCE-ESCALATE (hybrid-v2, umbral 1.0 -> 199 Gemini) que la calibracion comparativa necesita. `evaluation/deterministic_measurement.py` resuelve con `resolver_cache_calibracion` (prefiere el de calibracion, fallback al oficial). Re-correr la calibracion reproduce `precision_gem 0.6769 (88/130)` y tau 0.5166.
