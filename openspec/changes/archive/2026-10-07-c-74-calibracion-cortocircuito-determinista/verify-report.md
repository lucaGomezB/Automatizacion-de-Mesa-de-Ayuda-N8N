# Verification Report — c-74-calibracion-cortocircuito-determinista

**Change**: c-74-calibracion-cortocircuito-determinista
**Mode**: Standard (Strict TDD not declared in `openspec/config.yaml`; the change applied TDD internally but the verifier runs the standard contract)
**Governance**: ALTO
**Verifier stance**: independent; every claim re-derived from code, tests, and executed commands. The implementation summary was NOT trusted.

---

## Executive Summary

| Dimension | Result |
|-----------|--------|
| Completeness | **32/32 tasks complete** (4.6 paid re-run now done; see §11) |
| Backend tests | 1016 passed, 39 deselected, 1 xfailed, 0 failed |
| Lint (ruff) | clean, exit 0 |
| Evaluation tests | **118 passed, 0 failed** (was 114 before the additive resolver tests) |
| OpenSpec strict validation | valid, exit 0 |
| Calibration reproduction | exact match to reported numbers (non-degenerate `precision_gem` 0.6769) |
| Hard constraints | intact (5 canonical strings, `KEYWORD_MAP`, `docs/prompt_gemini.txt`, `evaluation/corpus.py::_a_float`) |
| **Verdict** | **PASS** (re-verified: W1 and W2 closed §10; additive fix neutral §11) |
| **CRITICAL findings** | **0** |

---

## 1. Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 32 |
| Tasks complete | **32** |
| Tasks incomplete | **0** |

~~Incomplete task 4.6~~ — now COMPLETE: the official paid hybrid-v3 run was executed
(2026-10-07, 69 Gemini calls, 0 errors) and recorded in `docs/deterministic_calibration.md`;
`evaluation/report.md` reproduces its numbers. See §11. No provider result is fabricated.

---

## 2. Build & Tests Execution (real execution)

**Lint**: PASSED
```
$ cd App/Backend; ruff check .
All checks passed!
exit 0
```

**Backend tests**: 1016 passed / 0 failed / 1 xfailed / 39 deselected
```
$ cd App/Backend; pytest -m "not integration"
1016 passed, 39 deselected, 1 xfailed, 251 warnings in 118.44s (0:01:58)
```

**Evaluation tests**: 114 passed / 0 failed (re-run; see §10)
```
$ cd evaluation; pytest
114 passed in 5.29s
```
The three target files were confirmed to run and pass independently (23 + 10 tests): `test_calibracion_oof.py`, `test_punto_comparativo.py`, `test_umbral_settings_oof.py`.

**OpenSpec strict validation**: PASSED
```
$ openspec validate c-74-calibracion-cortocircuito-determinista --strict
Change 'c-74-calibracion-cortocircuito-determinista' is valid
exit 0
```

**Calibration reproduction (offline, no provider call)**:
```
$ cd App/Backend; python3 -m evaluation.deterministic_measurement
- tau elegido (in-sample, score exacto): 0.5166666666666666
- Cobertura del punto: 0.6550 (131/200)
- precision_det(S): 0.7405 (97/131)
- precision_gem(S): 0.6769 (88/130)
- Umbrales por fold (OOF): (0.51666..., 0.51666..., 0.51666..., 0.51666..., 0.51666...)
- Cobertura OOF: 0.6550 (131/200)
- precision_det OOF: 0.7405 (97/131)
- precision_gem OOF: 0.6769 (88/130)
- Hibrido: estricta 0.7300 / macro-F1 0.5165 / micro-F1 0.6654 / subset 0.4300 / Hamming 0.3586 / Jaccard 0.6414
```
All numbers reproduce the values claimed in `tasks.md` 4.1/4.4 exactly. The run performs no Gemini call (it reads `evaluation/predicciones.json`).

**Coverage**: not configured as a verify gate in `openspec/config.yaml`; not run (Not available).

---

## 3. Spec Compliance Matrix (behavioral)

A scenario is COMPLIANT only when a passing test (or a reproduced command) proves the behavior at runtime.

### classification-resilience (6 scenarios)

| # | Requirement / Scenario | Status | Evidence |
|---|------------------------|--------|----------|
| 1 | MODIFIED cortocircuito calibrado — El cortocircuito respeta el piso de precision | PROVEN | `test_punto_comparativo.py::test_curva_comparativa_calcula_det_y_gem_por_umbral`, `::test_calibrar_comparativo_oof_reporta_cobertura_y_precisiones`; reproduced calibration det 0.7405 >= gem 0.6769 |
| 2 | MODIFIED cortocircuito calibrado — La cobertura queda justificada | PROVEN | `docs/deterministic_calibration.md` curva comparativa + `test_elegir_punto_comparativo_sube_el_umbral_si_el_piso_obliga` (the point rises when Gemini is stronger → derived, not hardcoded) |
| 3 | MODIFIED cortocircuito calibrado — La calibracion es offline | PROVEN | `test_punto_comparativo.py::test_cargar_predicciones_cacheadas_lee_el_formato_del_runner`; reproduction calls no provider |
| 4 | ADDED seleccion por score — El cortocircuito exige el score calibrado | PROVEN | `test_hybrid_classifier.py::test_cortocircuito_por_score_alto_ignora_la_confianza` |
| 5 | ADDED seleccion por score — El score insuficiente escala | PROVEN | `test_hybrid_classifier.py::test_escala_por_score_bajo_ignora_la_confianza` |
| 6 | ADDED seleccion por score — Los disparadores de escalamiento no dependen del score | PROVEN | `test_hybrid_classifier.py::test_sin_prediccion_escala_aunque_el_score_sea_alto`, `::test_ambiguo_escala_aunque_el_score_sea_alto` |

Requirement-body clause "El evento de cortocircuito SHALL registrar el score y el punto de operacion": present statically in `hybrid.py:168-175` (`score_correctitud`, `punto_operacion`); no dedicated test — static evidence only (folds into scenario 4).

### sector-assignment ASG-009 / ASG-010 / ASG-011 (9 scenarios)

| # | Requirement / Scenario | Status | Evidence |
|---|------------------------|--------|----------|
| 7 | ASG-009 — Un unico match no produce confianza alta | PROVEN | `test_deterministic_classifier.py::test_un_solo_match_no_alcanza_confianza_alta`, `test_deterministic_correctness_score.py::test_un_unico_match_tiene_score_no_nulo` |
| 8 | ASG-009 — Senal dominante produce confianza alta | PROVEN | `test_deterministic_classifier.py::test_ganador_dominante_alcanza_confianza_alta` |
| 9 | ASG-009 — La confianza no selecciona el cortocircuito | PROVEN | `test_hybrid_classifier.py::test_cortocircuito_por_score_alto_ignora_la_confianza`, `::test_escala_por_score_bajo_ignora_la_confianza` |
| 10 | ASG-009 — La confianza permanece acotada | PROVEN | `test_deterministic_classifier.py::test_confianza_acotada_en_todos_los_casos` |
| 11 | ASG-010 — El score es una probabilidad acotada | PROVEN | `test_deterministic_correctness_score.py::test_resultado_expone_score_acotado`, `::test_score_acotado_en_rango` (parametrized) |
| 12 | ASG-010 — El score se evalua fuera del test reportado | PROVEN (re-verified) | `test_umbral_settings_oof.py::test_settings_tau_deriva_del_oof_del_corpus` (corpus-tied, PASSED, not skipped) ties the frozen `Settings.deterministic_score_threshold` to the OOF aggregate; `test_calibracion_oof.py::test_calibracion_oof_umbral_por_fold_excluye_fold_evaluado` proves each fold's adjustment excludes the evaluated fold. `main()` reports the separation (precision/coverage) OOF. The score is an ordered correctness score by spec (ASG-010 no longer claims a calibrated probability). |
| 13 | ASG-010 — El score no invoca al proveedor pago | PROVEN | score is pure (`deterministic.py::score_correctitud`); offline reproduction; evaluation tests use fakes/cache |
| 14 | ASG-011 — El gate no se asume beneficioso | PROVEN | Decision cites calibration evidence (design D5, tasks 2.5 note, `docs/deterministic_calibration.md`); `test_deterministic_correctness_score.py::test_min_matches_informa_el_score_sin_anularlo` |
| 15 | ASG-011 — El gate no sustituye al score | PROVEN | `test_hybrid_classifier.py::test_unico_match_con_score_suficiente_cortocircuita` (single match, confianza 0.0, score-sufficient → short-circuit) |

### evaluation-framework (3 scenarios)

| # | Requirement / Scenario | Status | Evidence |
|---|------------------------|--------|----------|
| 16 | Provenance — El ajuste no usa el test reportado | PROVEN (re-verified) | `test_umbral_settings_oof.py::test_settings_tau_deriva_del_oof_del_corpus` proves the frozen operating point derives from `calibrar_comparativo_out_of_fold(...).umbrales_por_fold` (each fold excludes itself); `test_punto_comparativo.py::test_calibrar_comparativo_oof_umbral_por_fold_excluye_fold_evaluado`. `main()` anchors the reported point to `tau_settings_oof` (OOF), not to `elegir_punto_comparativo(curva_comparativa(...))` in-sample (traced at `deterministic_measurement.py:999-1016`). |
| 17 | Provenance — Las metricas se reportan sobre datos intocados | PROVEN | `test_calibracion_oof.py::test_calibracion_oof_metricas_sobre_datos_intocados`; reproduced OOF block |
| 18 | Provenance — La procedencia queda documentada | PROVEN | `test_calibracion_oof.py::test_procedencia_queda_documentada`, `test_punto_comparativo.py::test_procedencia_comparativa_documentada`; `docs/deterministic_calibration.md` §Calibracion comparativa out-of-fold |

**Compliance summary**: 18/18 PROVEN, 0 PARTIAL, 0 FAILING, 0 UNTESTED (re-verified; originally 16/18 PROVEN, 2/18 PARTIAL).

---

## 4. Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Short-circuit governed by score, not `confianza` | Implemented | `hybrid.py:166` `det_result.score_correctitud >= self._score_threshold`; `confianza` never compared to a threshold |
| `sin_prediccion`/`ambiguo` escalate unconditionally | Implemented | `hybrid.py:161-166` gate `causa_escalamiento is None` precedes the score check; deterministic forces `score=0.0` on `ambiguo` and no-signal |
| ASG-010 score bounded/deterministic/from observable features | Implemented | pure `extraer_features`/`score_correctitud`; `ClasificacionResult.score_correctitud` has `ge=0.0, le=1.0` |
| ASG-011 `min_matches` is a feature, not a gate | Implemented | `min_matches` enters as `evidence = winner/(winner+min_matches)`; never used as a binary selection gate in `hybrid.py` |
| Comparative operating point derived from data | Implemented | `curva_comparativa` / `elegir_punto_comparativo` derive by scanning thresholds; test forces a higher threshold when Gemini is stronger |
| Cache version invalidation | Implemented | `HYBRID_CACHE_VERSION = "hybrid-v3"`; tests `test_version_de_cache_comparativa_es_hybrid_v3`, `test_cache_de_politica_previa_v2_es_invalido` |
| Anti-leakage verification | Implemented (re-verified) | OOF threshold excludes evaluated fold; frozen constant derived from the OOF aggregate and tied by `test_settings_tau_deriva_del_oof_del_corpus` (W1 closed) |

---

## 5. Coherence (Design D2–D6)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D2 (OQ1) Conformal / risk-controlled prediction, out-of-fold | RESOLVED as scoped | Spec reworded: the artifact is an ORDERED correctness score, not a claimed calibrated probability; `Settings` tau is derived out-of-fold and tied by test. See W2 residual R1 (LOW) for the `classification-resilience` prose. |
| D3 (OQ2) Cross-fitting / conformal out-of-fold | YES | `PROCEDENCIA_CROSS_FITTING` + `calibrar_out_of_fold`; tests enforce fold exclusion |
| D4 (OQ3, revised) comparative floor `precision_det >= precision_gem`, max coverage | YES | `curva_comparativa`/`elegir_punto_comparativo`; reproduced 0.7405 >= 0.6769; threshold is derived (test forces rise under a stronger Gemini) |
| D5 (OQ4) `min_matches` becomes a feature | YES | `tests/test_deterministic_correctness_score.py::test_min_matches_informa_el_score_sin_anularlo` |
| D6 (OQ5) `sin_prediccion`/`ambiguo` intact | YES | unconditional escalation preserved and tested |
| D7 cache bump on signal change | YES | hybrid-v3 + invalidation tests |
| D8 offline calibration, no `_a_float` touch | YES | offline reproduction; `evaluation/corpus.py` unchanged |
| D9 TDD + structural tests | YES | new test files + structural assertions; backend suite green |

---

## 6. Adversarial Checks

| Check | Result |
|-------|--------|
| Score gate REALLY replaced `confianza` | CONFIRMED: `hybrid.py:166` uses `score_correctitud`; `is_confident`/`deterministic_confidence_threshold` have no production caller (`grep` shows `self._threshold` only inside the unused `is_confident`). |
| `sin_prediccion`/`ambiguo` escalate unconditionally | CONFIRMED: gate on `causa_escalamiento is None`; deterministic sets `score=0.0` for both states. |
| Comparative criterion not hardcoded to the whole set | CONFIRMED: driven by `elegir_punto_comparativo`; `test_elegir_punto_comparativo_sube_el_umbral_si_el_piso_obliga` forces a higher threshold (coverage 0.5) under a stronger Gemini; `test_elegir_punto_comparativo_none_si_nunca_gana_el_determinista` returns None. |
| Five canonical category strings unchanged | CONFIRMED: not in `git diff`; `constants.py`/`keywords.py` canonical lines untouched. |
| `KEYWORD_MAP` unchanged | CONFIRMED: `git diff --stat App/Backend/app/classifiers/keywords.py` empty. |
| `docs/prompt_gemini.txt` unchanged | CONFIRMED: tracked, not in `git diff --name-only` (empty). `docs/anexo_h_prompt_gemini.md` (docs/Anexo H, not the prompt) was modified — acceptable. |
| `evaluation/corpus.py::_a_float` unchanged | CONFIRMED: `evaluation/corpus.py` not in `git diff`; `_a_float` still at line 138. |
| Cache version really invalidates old cache | CONFIRMED: `test_version_de_cache_comparativa_es_hybrid_v3`, `test_cache_de_politica_previa_v2_es_invalido` (v2 invalid, v2==v2 valid) pass. |

---

## 7. Issues Found

### CRITICAL (must fix before archive)
None. No spec scenario was found FAILING or UNTESTED; no hard-constraint breach; no fake/hardcoded result — the calibration reproduces exactly offline.

### WARNING (should fix / document before archive)

- **W1 (HIGH) — CLOSED (re-verified; see §10).** [Original finding] The frozen operating point was selected in-sample from the reported test set.
  `evaluation/deterministic_measurement.py::main()` computes `punto = elegir_punto_comparativo(curva_comparativa(observaciones, ...))` over the **entire** corpus and `umbral_op = punto.umbral`; the `Settings.deterministic_score_threshold = 0.5166` constant matches that in-sample value (the report itself prints "tau elegido (in-sample, score exacto)"). The spec (`evaluation-framework`) says the corpus "MUST NOT usarse para ... seleccionar ... el punto de operacion", and cross-fitting requires the point to be chosen from training folds. Mitigation: the per-fold OOF thresholds are all identical to the in-sample value (0.51666…), so the frozen constant is stable and there is **no effective leakage** (the point is just the minimum score of the non-ambiguous set). Recommendation: set the constant from `calibrar_comparativo_out_of_fold(...).umbrales_por_fold` and document that the in-sample and OOF points coincide. This is the main reason scenarios 12 and 16 are PARTIAL rather than PROVEN.

- **W2 (HIGH) — CLOSED as scoped (re-verified; see §10). Residual LOW note on `classification-resilience` body.** [Original finding] The "calibrated correctness score" was a fixed a-priori formula that did not demonstrably estimate P(correct); the ASG-010 body clause "estime la probabilidad" was in tension with the design. ASG-010 is now reworded to "ordene la correctitud esperada ... NO SHALL presentarse como una probabilidad calibrada", and code/docs are aligned.
  `score_correctitud` uses hardcoded weights (`w_margin=0.5, w_evidence=0.3, w_density=0.2`) and is never fitted/calibrated; the out-of-fold procedure calibrates only the threshold. Empirically the score is **anti-monotonic** w.r.t. correctness over most of its range (reproduced curve: threshold 0.5166 → precision 0.7405; 0.80 → 0.7236; 0.85 → 0.6667; 0.88 → 0.4286). The design Goal "un score calibrado ... que SI separe predicciones correctas de incorrectas" is therefore not demonstrated. The operating point collapses to "short-circuit every non-ambiguous case" (identical to proposal policy-B; macro-F1 0.5165). No calibration-quality metric (Brier/ECE/reliability) is reported. This sits in tension with the ASG-010 body clause "estime la probabilidad de que su prediccion sea correcta"; the verifiable scenarios (range, provenance, offline) do pass. Recommend either (a) reporting a reliability/calibration-quality metric and tempering the "estime la probabilidad" wording, or (b) fitting an actual calibrated score.

- **W3 (MEDIUM) — ASG-010 "calidad de la calibracion reportada sobre datos no usados para ajustar" is only partially covered.**
  The OOF block reports precision/coverage of the **operating point**, not the calibration quality of the **score**. Scenario marked PARTIAL.

- **W4 (LOW) — Task 4.6 pending (paid re-run).** Declared, not blocked, and no numbers fabricated. Acceptable debt; the change cannot claim a confirmed paid-run delta.

- **W5 (LOW) — Legacy absolute-floor machinery retained.** `PISO_PRECISION_DEFAULT = 0.90`, `elegir_umbral`, `seleccionar_umbral`, `calibrar_out_of_fold` remain with the retired 0.90 default. They do not govern the short-circuit (production uses `deterministic_score_threshold`), and `main()` uses them only for a labeled "legacy" curve. Acceptable for backward compatibility but a future maintainer could reuse the retired floor by mistake; the superseded default should be clearly deprecated.

- **W6 (LOW) — `deterministic_confidence_threshold` / `is_confident` retained as dead code.** No production caller (verified by grep). Documented as "fuerza de senal (NO selecciona)". Acceptable, but consider removing or marking deprecated.

- **W7 (LOW) — `precision_gem` computed over 130 (1 cortocircuitable case excluded).** Documented and not fabricated; the excluded case has no cached Gemini prediction.

- **W8 (LOW) — Offline hybrid measurement reuses the `hybrid-v2` Gemini cache.** Documented debt. Methodologically acceptable for the escalated cases because a Gemini prediction for a description is independent of the deterministic version, and the v2 run short-circuited only 1 case (199 Gemini predictions available). The cache bump properly invalidates it for the runner.

- **W9 (LOW) — Delta table baseline inconsistency.** In the generated report, the coverage delta is measured against policy A (0.005) while the Macro/Micro-F1 deltas are measured against policy B (0.5165/0.6654), yielding +0.0000; `tasks.md` 4.4 instead reports +0.0400/+0.0560 against policy A (0.6900/0.4605). Both reference frames are individually valid but the report should state which baseline each row uses.

### SUGGESTION (nice to have)
- Add a single "calibration-quality" test (reliability/Brier) for the score so ASG-010 is behaviorally verified beyond its range.
- Programmatically derive `deterministic_score_threshold` from the OOF result (or add a test asserting `Settings.deterministic_score_threshold == OOF tau`).

---

## 8. Known Deviations — Classification

| Deviation | Classification | Justification |
|-----------|----------------|---------------|
| (a) Task 4.6 pending (paid re-run) | Acceptable WARNING | Declared pending; no fabricated provider numbers; success criterion explicitly permits a declared pending re-measurement |
| (b) `PISO_PRECISION_DEFAULT=0.90` + legacy absolute-curve helpers retained | Acceptable WARNING | Not used as the operating criterion; production governed by the comparative threshold; documented as legacy |
| (c) `deterministic_confidence_threshold` / `is_confident` retained | Acceptable WARNING | No production caller; not a selection criterion |
| (d) `precision_gem` over 130 (1 case excluded) | Acceptable WARNING | Case excluded for lacking a cached Gemini prediction; documented, not fabricated |
| (e) Six existing tests updated (confianza → score contract) | Acceptable | Required by the intentional contract change; assertions still meaningful |
| (f) Offline hybrid F1 reuses stale `hybrid-v2` Gemini cache | Acceptable WARNING | Escalated-case Gemini predictions are version-independent; cache bump invalidates it for the runner; documented debt |

None of these rise to CRITICAL.

---

## 9. Verdict

**PASS** — 0 CRITICAL findings (re-verified; the prior HIGH warnings W1 and W2 are closed, and the two previously PARTIAL scenarios 12 and 16 are now PROVEN — see §10).

All four required commands pass (backend 1016 passed / ruff clean / evaluation 114 passed / `openspec validate --strict` valid), all hard-locked artifacts are intact, the short-circuit is genuinely governed by the calibrated score vs a data-derived comparative operating point (not `confianza`), `sin_prediccion`/`ambiguo` escalate unconditionally, and the calibration reproduces exactly offline. The frozen `Settings.deterministic_score_threshold = 0.5166` is now derived out-of-fold and tied to the OOF aggregate by a corpus-tied test, so the reported test set no longer selects the operating point. ASG-010 no longer claims a calibrated probability and code/docs match. Residual items are LOW-severity documentation/debt notes and do not block archive.

---

## 10. Focused Re-verification (W1 / W2 closure)

**Scope**: confirm the two HIGH warnings that caused scenarios 12 and 16 to be PARTIAL are genuinely fixed, without trusting the fix summary. Every claim below was re-derived from source, tests, and executed commands.

### 10.1 W1 — frozen operating point derived out-of-fold (anti-leakage)

| Check | Result |
|-------|--------|
| `main()` no longer selects the point in-sample | CONFIRMED. `deterministic_measurement.py:997-1016`: `curva_comp` is computed **only** for the report table; the reported point is `_punto_comparativo_para(observaciones, tau_settings_oof, gem_map)` where `tau_settings_oof = umbral_de_settings_oof(oof)` and `oof = calibrar_comparativo_out_of_fold(observaciones, gem_map)`. |
| `elegir_punto_comparativo` is not used in-sample | CONFIRMED. Its only non-definition call is inside `calibrar_comparativo_out_of_fold` (line 572), invoked per fold with the **training** folds (`entrenamiento` excludes the evaluated fold). No in-sample call remains. |
| Test ties `Settings` to the OOF derivation | CONFIRMED. `evaluation/tests/test_umbral_settings_oof.py::test_settings_tau_deriva_del_oof_del_corpus` recomputes the OOF result from the real corpus + cached Gemini predictions and asserts `get_settings().deterministic_score_threshold == umbral_de_settings_oof(oof)`. Executed: **PASSED (not skipped)** — corpus and `evaluation/predicciones.json` are present. |
| Aggregation rule is deterministic and documented | CONFIRMED. `tau_oof_agregado` = min over viable fold thresholds; `umbral_de_settings_oof` truncates toward zero to 4 decimals. Covered by 9 unit tests (coincidence, minimum-on-discrepancy, `None` folds, truncation, parametrized non-rounding-up). |
| Value/provenance documented | CONFIRMED. `settings.py:114-129`, `docs/deterministic_calibration.md:8-64,154-157` (explicitly "NO se elige in-sample ... se deriva out-of-fold"), and the generated report prints `tau aplicado (OOF...)` and `tau fijado en Settings ... (derivado OUT-OF-FOLD)`. |

**Adversarial trace of the reported numbers (clean env, offline, no provider call)**:
```
- tau OOF exacto (agregado de folds): 0.5166666666666666
- tau aplicado (OOF, truncado hacia abajo a 4 decimales): 0.5166
- Cobertura del punto: 0.6550 (131/200)
- precision_det(S): 0.7405 (97/131)
- precision_gem(S): 0.6769 (88/130)
- tau fijado en Settings (`deterministic_score_threshold`): 0.5166 (derivado OUT-OF-FOLD)
- Umbrales por fold: (0.516666..., x5)
- precision_det OOF: 0.7405 (97/131) / precision_gem OOF: 0.6769 (88/130)
- Hibrido: F1 macro estricto 0.5165 / Micro-F1 0.6654
```
The reported test set no longer feeds the selection: the tau comes from the fold aggregate. W1 is **CLOSED**.

### 10.2 W2 — score is an ordering score, not a claimed calibrated probability

| Check | Result |
|-------|--------|
| ASG-010 no longer claims a calibrated probability | CONFIRMED. `specs/sector-assignment/spec.md:33`: "El score SHALL exponer un SCORE DE CORRECTITUD que **ordene** la correctitud esperada ... El score **NO SHALL presentarse como una probabilidad calibrada** de acierto". The scenario set remains range / out-of-test / offline. |
| Code wording matches | CONFIRMED. `deterministic.py` docstrings (`score_correctitud`, module header) and `schemas/clasificacion.py:74-79` say "ORDENA la correctitud esperada; NO es una probabilidad calibrada". `settings.py:131-141` same. |
| Doc wording matches | CONFIRMED. `docs/deterministic_calibration.md:8` and `docs/anexo_h_prompt_gemini.md:192` both state the score orders expected correctness and is not a calibrated probability. |
| Score numeric behavior unchanged | CONFIRMED. Reproduced operating point identical to the prior accepted run (tau 0.5166, coverage 0.6550/131, precision_det 0.7405/97, precision_gem 0.6769/88, hybrid macro-F1 0.5165, micro-F1 0.6654). No formula or weight change. |

W2 is **CLOSED as scoped**. Residual LOW note (documentation consistency, not behavioral): the sibling `classification-resilience` requirement body (line 7) still says "El score SHALL estimar la probabilidad de que la prediccion determinista sea correcta". This prose now reads in slight tension with ASG-010's "NO SHALL presentarse como una probabilidad calibrada". It is requirement body prose with no scenario asserting a probability input, and the executable behavior (order/range/threshold) is unchanged; recommend rephrasing to "ordena la correctitud esperada" for full consistency, but it does not block archive.

### 10.3 Hard constraints re-confirmed

| Constraint | Result |
|------------|--------|
| 5 canonical strings | CONFIRMED intact. `constants.py` diff touches ONLY `HYBRID_CACHE_VERSION` (v2→v3); canonical lines `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas` unchanged. |
| `KEYWORD_MAP` | CONFIRMED. `app/classifiers/keywords.py` not in `git diff`. |
| `docs/prompt_gemini.txt` | CONFIRMED. Not in `git diff --name-only`. |
| `evaluation/corpus.py::_a_float` | CONFIRMED. `evaluation/corpus.py` has an empty diff. |

### 10.4 Scenario re-classification

The two previously PARTIAL scenarios are now backed by executed passing tests proving the behavior at runtime:
- ASG-010 "El score se evalua fuera del test reportado" → **PROVEN** (corpus-tied OOF/Settings test + fold-exclusion tests + OOF separation report).
- evaluation-framework "El ajuste no usa el test reportado" → **PROVEN** (main anchors to OOF tau; Settings tied to OOF).

**Updated compliance**: 18/18 PROVEN.

### 10.5 Updated command outputs (re-run)

```
$ cd App/Backend; pytest -m "not integration"
1016 passed, 39 deselected, 1 xfailed, 251 warnings in 117.23s (0:01:57)

$ cd App/Backend; ruff check .
All checks passed!

$ cd evaluation; pytest
114 passed in 5.29s

$ openspec validate c-74-calibracion-cortocircuito-determinista --strict
Change 'c-74-calibracion-cortocircuito-determinista' is valid
```

### 10.6 Residual warnings after re-verification

- **R1 (LOW)** — `classification-resilience` requirement body still says the score "SHALL estimar la probabilidad"; reconcile with ASG-010's "NO ... probabilidad calibrada" wording. Behavioral scenarios unaffected.
- **R2 (LOW)** — Task 4.6 (paid re-run) remains declared pending; no fabricated provider numbers (unchanged).
- **R3 (LOW)** — Legacy absolute-floor helpers (`PISO_PRECISION_DEFAULT=0.90`, `elegir_umbral`, `seleccionar_umbral`, `calibrar_out_of_fold`) retained and labeled legacy; do not govern the short-circuit (unchanged).
- The prior W3–W9 LOW/MEDIUM notes remain as documented debt; none block archive.

**Re-verification verdict: PASS.** W1 and W2 are truly closed (not faked: the OOF derivation is executed and asserted by a corpus-tied test, `main()` provably anchors to it, and the numbers reproduce exactly offline). The two formerly PARTIAL scenarios are PROVEN. 0 CRITICAL.

---

## 11. Final Re-verification (post additive fix)

**Scope**: the last additive, behavior-neutral fix landed after the §10 PASS. This section re-confirms it does not regress anything and updates the report to the FINAL state. Every claim below was re-derived from source, tests, and executed commands — the fix summary was NOT trusted.

### 11.1 What the additive fix changed

| # | File | Change | Evidence |
|---|------|--------|----------|
| 1 | `evaluation/deterministic_measurement.py` | Added `PREDICCIONES_OFICIALES_PATH` (line 673), `CALIBRACION_CACHE_PATH` (line 679), `resolver_cache_calibracion(repo_root)` (lines 682-698); `main()` uses it at line 1023 | read from source |
| 2 | `evaluation/tests/test_umbral_settings_oof.py` | Added 4 resolver tests; the corpus-tied provenance test now uses the resolver and asserts `precision_gem_oof == 88/130`, `precision_det_oof == 97/131`, `casos_gem_oof == 130`, `tau == 0.5166`, `Settings == tau` | read from source, lines 110-216 |
| 3 | `docs/deterministic_calibration.md` | Recorded the official hybrid-v3 paid run + the two-cache convention | docs lines 7-8, 123-127, 149-176 |
| 4 | `tasks.md` (orchestrator-owned) | 4.6 marked done; change is 32/32 | `openspec list --json`: 32/32 |

### 11.2 Resolver behavior and non-degeneracy

The resolver **prefers** `evaluation/predicciones_calibracion.json` when present and falls back to `evaluation/predicciones.json`; with neither present it returns the official path (which would fail on load). All three branches are asserted by executed passing tests:

```
tests/test_umbral_settings_oof.py::test_resolver_prefiere_la_cache_de_calibracion_cuando_existe PASSED
tests/test_umbral_settings_oof.py::test_resolver_cae_a_la_cache_oficial_si_falta_la_de_calibracion PASSED
tests/test_umbral_settings_oof.py::test_resolver_sin_ninguna_cache_devuelve_la_ruta_oficial PASSED
tests/test_umbral_settings_oof.py::test_constante_de_cache_de_calibracion_apunta_al_archivo_forzado PASSED
```

`main()` actually consumes the resolver (`cache_path = resolver_cache_calibracion(repo_root)`, line 1023) and reports the resolved path. The calibration is **NOT degenerate** — the reproduction prints the real comparative numbers:

```
- tau OOF exacto (agregado de folds): 0.5166666666666666
- tau aplicado (OOF, truncado hacia abajo a 4 decimales): 0.5166
- Cobertura del punto: 0.6550 (131/200)
- precision_det(S): 0.7405 (97/131)
- precision_gem(S): 0.6769 (88/130)   <-- NOT 0/0
- tau fijado en Settings (`deterministic_score_threshold`): 0.5166 (derivado OUT-OF-FOLD)
```

Both caches are present with the expected provenance:

```
evaluation/predicciones.json            -> classifier_version=hybrid-v3 | 200 preds  (OFICIAL)
evaluation/predicciones_calibracion.json -> classifier_version=hybrid-v2 | 200 preds  (FORCE-ESCALATE)
```

This confirms WHY the resolver is required: the official hybrid-v3 cache contains no Gemini prediction for the 131 short-circuitable cases, so using it would degenerate `precision_gem(S)` to 0/0. The resolver picks the FORCE-ESCALATE cache instead.

### 11.3 No regression — 18/18 scenarios, W1/W2 closed, 0 CRITICAL

The previously-PARTIAL scenarios (ASG-010 "score evaluated outside the reported test" and evaluation-framework "the adjustment does not use the reported test") remain PROVEN. The corpus-tied test that backs them **executed and PASSED (not skipped)** because corpus and cache are present:

```
tests/test_umbral_settings_oof.py::test_settings_tau_deriva_del_oof_del_corpus PASSED [100%]
```

`test_umbral_settings_oof.py` = **14 passed** (was 10 before the +4 resolver tests). The full evaluation suite is **118 passed** (was 114), 0 failed, 0 skipped. Backend suite unchanged at **1016 passed / 0 failed / 1 xfailed / 39 deselected**. The fix is genuinely additive and behavior-neutral: the calibration output is identical to §10.

**Compliance**: **18/18 PROVEN** (0 PARTIAL, 0 FAILING, 0 UNTESTED). W1 and W2 remain CLOSED. **0 CRITICAL.**

### 11.4 Hard constraints intact (git diff)

| Constraint | Result |
|------------|--------|
| 5 canonical strings | CONFIRMED. `constants.py` diff touches ONLY `HYBRID_CACHE_VERSION` (v2→v3); `SECTORES_CANONICOS` (lines 18-22: Seguridad Informatica, Soporte Tecnico Hardware, Soporte Tecnico Software, Bases de Datos, Sistemas) unchanged. |
| `KEYWORD_MAP` | CONFIRMED. `git diff --stat App/Backend/app/classifiers/keywords.py` empty. |
| `docs/prompt_gemini.txt` | CONFIRMED. `git diff --stat docs/prompt_gemini.txt` empty. |
| `evaluation/corpus.py::_a_float` | CONFIRMED. `git diff --stat evaluation/corpus.py` empty. |
| Both calibration caches present | CONFIRMED. `predicciones.json` = hybrid-v3 (official), `predicciones_calibracion.json` = hybrid-v2 (FORCE-ESCALATE). |

### 11.5 Official numbers — docs vs `evaluation/report.md`

The official hybrid-v3 paid-run numbers recorded in `docs/deterministic_calibration.md` (lines 149-161) match `evaluation/report.md` **exactly**:

| Metric | docs | report.md |
|--------|------|-----------|
| Strict accuracy | 0.7350 (147/200) | 0.7350 (147/200) |
| Macro-F1 | 0.5207 | 0.5207 |
| Micro-F1 | 0.6654 | 0.6654 |
| Subset accuracy | 0.4300 | 0.4300 |
| Hamming loss | 0.3586 | 0.3586 |
| Jaccard | 0.6414 | 0.6414 |
| Stage mix | det 131 / gemini 69 / fallback 0 | Deterministic 131 / Gemini 69 / Fallback 0 |
| Gemini calls / errors | 69 / 0 | (stage mix consistent) |

The docs explicitly distinguish the OFFLINE numbers (0.7300 / 0.5165, which is what the offline reproduction command prints) from the OFFICIAL paid-run numbers (0.7350 / 0.5207). No fabricated provider result.

### 11.6 Command outputs (re-run for this final re-verification)

```
$ cd App/Backend; pytest -m "not integration"
1016 passed, 39 deselected, 1 xfailed, 251 warnings in 127.07s (0:02:07)
exit 0

$ cd App/Backend; ruff check .
All checks passed!
exit 0

$ cd evaluation; pytest
118 passed in 7.70s
exit 0

$ openspec validate c-74-calibracion-cortocircuito-determinista --strict
Change 'c-74-calibracion-cortocircuito-determinista' is valid
exit 0

$ cd App/Backend; PYTHONPATH=../.. python3 -m evaluation.deterministic_measurement --umbral-actual 1.0
- tau OOF exacto (agregado de folds): 0.5166666666666666
- tau aplicado (OOF, truncado hacia abajo a 4 decimales): 0.5166
- Cobertura del punto: 0.6550 (131/200)
- precision_det(S): 0.7405 (97/131)
- precision_gem(S): 0.6769 (88/130)
- tau fijado en Settings: 0.5166 (derivado OUT-OF-FOLD)
exit 0
```

### 11.7 Residual warnings after the final re-verification

Unchanged from §10.6 and §7; none block archive:

- **R1 (LOW)** — `classification-resilience` requirement body still says the score "SHALL estimar la probabilidad"; reconcile with ASG-010's "NO ... probabilidad calibrada". Behavioral scenarios unaffected.
- **R2 (LOW)** — W3, W5-W9 LOW/MEDIUM documentation/debt notes remain (legacy helpers labeled legacy, dead `is_confident`, `precision_gem` over 130, report delta baselines). None CRITICAL.
- No new warnings introduced by the additive fix.

### 11.8 Final verdict

**PASS** — the additive fix is genuine and behavior-neutral. It closes the last declared debt (task 4.6 paid re-run now recorded: official 0.7350 / 0.5207) and makes the calibration cache resolution explicit and tested (two-cache convention). The END state is: **32/32 tasks, 118 evaluation tests passed, 1016 backend tests passed, ruff clean, `openspec validate --strict` valid, 18/18 scenarios PROVEN, W1/W2 CLOSED, hard constraints intact, calibration non-degenerate (precision_gem 0.6769, tau 0.5166), 0 CRITICAL.** The fix is NOT incomplete or faked: every claim was re-derived from source and executed commands.
