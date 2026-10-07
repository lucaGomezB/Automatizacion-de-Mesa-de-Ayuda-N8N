# Verification Report: c-73-pseudonimizacion-tarjeta

**Change**: `c-73-pseudonimizacion-tarjeta`
**Version**: N/A (delta for `data-pseudonymization`)
**Mode**: Strict TDD (agent-injected; `openspec/config.yaml` declares no `strict_tdd` key)
**Date**: 2026-10-07 (original verify) / 2026-10-07 (focused re-verification)
**Verifier**: independent sdd-verify (did not author the implementation)
**Governance**: HIGH (PII financiera, Ley 25.326)

---

## Verdict

**PASS** — 0 CRITICAL, 0 WARNING. (Original verify: PASS WITH WARNINGS, 0 CRITICAL, 15/16 scenarios.)

The implementation is behaviorally correct against **every** spec scenario. After the focused re-verification, all 42 unit tests pass, the full offline backend suite passes (1035), `ruff` is clean, and `openspec validate --strict` passes. Hard constraints are intact. The two warnings raised by the previous verify are fixed and independently confirmed: W1 (multiple cards sharing one trigger) is resolved, and W2 (audit-log scenario only partially asserted) is resolved — the previously-PARTIAL scenario #6 is now PROVEN (16/16). The remaining Strict-TDD process note (W3) was downgraded to a non-blocking SUGGESTION; see "Issues Found".

---

## Focused Re-verification (W1 + W2)

**Scope**: confirm the two warnings from the prior PASS-WITH-WARNINGS verify, re-run the four required commands, and adversarially re-check the offset/window logic and hard constraints.

### Command results (exact)

**`cd App/Backend; pytest tests/test_pseudonymizer.py -v`**: PASS

```
platform linux -- Python 3.12.3, pytest-8.3.3, pluggy-1.6.0
configfile: pytest.ini
collected 42 items
... 42 passed, 1 warning in 0.18s ...
======================== 42 passed, 1 warning in 0.18s =========================
```
(Was 40 before the fix; +2 new multi-card tests. The 1 warning is the pre-existing Starlette `import multipart` PendingDeprecationWarning.)

**`cd App/Backend; pytest tests/test_pseudonymization_integration.py::test_log_debug_cobertura_sin_pii -v`** (W2 target): PASS

```
tests/test_pseudonymization_integration.py::test_log_debug_cobertura_sin_pii PASSED [100%]
========================= 1 passed, 1 warning in 0.71s =========================
```

**`cd App/Backend; pytest -m "not integration"`**: PASS

```
=== 1035 passed, 39 deselected, 1 xfailed, 251 warnings in 128.64s (0:02:08) ===
```
(Was 1033 before the fix; +2 new tests. No failures; 39 deselected = PostgreSQL integration subset; 1 xfailed = expected-failure, not a regression.)

**`cd App/Backend; ruff check .`**: PASS — `All checks passed!` (`RUFF_EXIT=0`)

**`openspec validate c-73-pseudonimizacion-tarjeta --strict`**: PASS — `Change 'c-73-pseudonimizacion-tarjeta' is valid` (`VALIDATE_EXIT=0`)

### W1 — multiple cards sharing one trigger: RESOLVED

The pseudonymizer was refactored from a single combined `_RE_TARJETA` (trigger + lazy window + number, whose `subn` resumed scanning *after* the first number) into a two-step detector: `_RE_TRIGGER_TARJETA` (`\btarjetas?\b`) yields forward windows `(m.end(), m.end()+40)` computed on the **input** text, and `_RE_NUMERO_TARJETA` (`4-4-4-4` or contiguous 16, both digit-bounded) is substituted with a callback that masks **every** candidate whose `match.start()` falls in any window. `conteos["tarjeta"]` counts the actual replacements. Independent probes (executed against the installed module):

```
multi espacios   | tarjeta=2 tel=0 | digits_left='' | 'mis tarjetas [TARJETA] y [TARJETA]'
multi contiguo   | tarjeta=2 tel=0 | digits_left='' | 'mi tarjeta [TARJETA] y [TARJETA]'
newline cross    | tarjeta=1 tel=0 | digits_left='' | 'mi tarjeta\n[TARJETA]'
num before trig  | tarjeta=0 tel=1 | digits_left='7890' | '[TELEFONO] 7890 mi tarjeta'
40 gap           | tarjeta=1 tel=0 | digits_left='' | 'mi tarjeta xxxx...(38) [TARJETA]'
41 gap           | tarjeta=0 tel=1 | digits_left='7890' | 'mi tarjeta xxxx...(39) [TELEFONO] 7890'
R067 22 digits   | tarjeta=0 tel=1 | digits_left='010' | '...axm010[TELEFONO]...'
no trigger       | tarjeta=0 tel=1 | digits_left='010' | 'el codigo 010[TELEFONO] fue registrado'
```

**Offset/window adversarial check (the specific risk named in the task)**: windows and candidate runs are both computed on the same pre-replacement `text`, and `re.sub`'s callback receives offsets on that original text — so masking the first number does **not** shift/hide the second. The `multi espacios`/`multi contiguo` probes (second card inside the same window, masked as `[TARJETA]`, `tarjeta=2`, zero digits remaining) prove the offsets are original-text-based and correct. No regression of any negative case:

- Number beyond 40 chars NOT masked: `41 gap` → `tarjeta=0`.
- 16 digits inside a longer digit run NOT masked: `R067 22 digits` → `tarjeta=0` (boundaries `(?<!\d)`/`(?!\d)` hold).
- 16 digits without a "tarjeta" mention NOT masked: `no trigger` → `tarjeta=0`.
- Trigger preserved, label exact `[TARJETA]`, `conteos["tarjeta"]` counts each masked number: confirmed by the probes and by `test_pseudonymize_multiples_tarjetas_con_un_solo_disparador` / `..._contiguas_con_un_disparador`.

Two new tests lock this behavior: `test_pseudonymize_multiples_tarjetas_con_un_solo_disparador` (asserts exact output `"mis tarjetas [TARJETA] y [TARJETA]"`, count 2, no visible digits) and `test_pseudonymize_multiples_tarjetas_contiguas_con_un_disparador` (contiguous triangulation). Both pass.

### W2 — audit DEBUG test: RESOLVED (non-vacuous)

`test_log_debug_cobertura_sin_pii` now uses `structlog.testing.capture_logs` (the repo's established pattern for structlog events; `caplog` did not reliably surface them, which made the old absence-only assertion vacuous). It now asserts the event is emitted, is `log_level == "debug"`, contains the `tarjeta` key, and contains all five categories, while keeping the no-PII assertions (email, phone, and the full original text absent). The test passes. Independent mechanism check (capture_logs sees a `pseudonimizacion_cobertura` event carrying `tarjeta`):

```
captured: [{'email': 0, 'telefono': 0, 'tarjeta': 0, 'host': 0, 'persona': 0, 'event': 'pseudonimizacion_cobertura', 'log_level': 'debug'}]
W2 non-vacuous mechanism CONFIRMED
```
The service forwards the counts as top-level event kwargs: `logger.debug("pseudonimizacion_cobertura", **resultado_pseudo.conteos)` (`incidente_service.py` L292-295). The assertion is genuine, not tautological.

### Prior-PARTIAL scenario #6 → PROVEN

Spec scenario "El log DEBUG registra conteos incluyendo `tarjeta` sin texto" was the lone PARTIAL. It is now backed by a passing test that asserts the event and the `tarjeta` key. Compliance moves from 15/16 to **16/16 PROVEN**.

### Newline-crossing nuance — ACCEPTED (not a warning)

The window is character-based over the whole string and no longer a non-DOTALL regex, so a trigger can reach a card across a newline (`'mi tarjeta\n4517 6712 3456 7890'` → `tarjeta=1`). This is the **safe direction**: it masks strictly more contextual PII within the same 40-char proximity, never less, and the spec says "una ventana de proximidad de 40 caracteres DESPUÉS del disparador" without a same-line constraint. No negative-case change (context-free runs, out-of-window runs, and R067 are all unaffected). Accepted as intended behavior; recorded as a note, not a defect.

### Hard constraints — UNCHANGED

`git diff --name-only HEAD`:
```
App/Backend/app/utils/pseudonymizer.py
App/Backend/tests/test_pseudonymization_integration.py
App/Backend/tests/test_pseudonymizer.py
openspec/changes/c-73-pseudonimizacion-tarjeta/tasks.md
```
`git diff HEAD -- App/Backend/app/constants.py docs/prompt_gemini.txt evaluation/corpus.py App/Backend/app/classifiers/keywords.py` is empty. The five canonical strings remain exact, case-sensitive, accent-free (`constants.py` L18-22: `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`). `KEYWORD_MAP`, `docs/prompt_gemini.txt`, and `evaluation/corpus.py::_a_float` untouched.

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 23 |
| Tasks complete | 23 |
| Tasks incomplete | 0 |

All 23 checkboxes in `tasks.md` are `[x]` (verified via `git diff HEAD -- .../tasks.md`: 23 insertions / 23 deletions, all `[ ]` to `[x]`). No task is claimed complete without a corresponding artifact:
- Tasks 3.1/3.2: `_LABEL_TARJETA`, `_CARD_CONTEXT_WINDOW_CHARS`, and the contextual card detection (`_RE_TRIGGER_TARJETA` + `_RE_NUMERO_TARJETA`, applied in order) present in `pseudonymizer.py`.
- Task 3.3: full-dict test updated (`test_pseudonymize_texto_sin_pii_devuelve_texto_intacto_y_conteos_en_cero`, lines 38-44).
- Tasks 4.x/5.x: all triangulation and non-regression tests present and passing.
- Task 6.3: `test_pseudonymization_integration.py` needs no change (it does not compare the full `conteos` dict); confirmed by reading it.

---

## Build & Tests Execution

**Build**: N/A (pure Python module; no build artifact). `ruff check .` acts as the static gate.

**`cd App/Backend; pytest tests/test_pseudonymizer.py -v`**: PASS

```
platform linux -- Python 3.12.3, pytest-8.3.3, pluggy-1.6.0
configfile: pytest.ini
collected 42 items
... 42 passed, 1 warning in 0.18s ...
======================== 42 passed, 1 warning in 0.18s =========================
```
(1 warning is a pre-existing Starlette `PendingDeprecationWarning` on `import multipart`; unrelated.)

**`cd App/Backend; pytest -m "not integration"`**: PASS

```
=== 1035 passed, 39 deselected, 1 xfailed, 251 warnings in 128.64s (0:02:08) ===
```
(No failures. `1 xfailed` is an expected-failure test, not a regression. 39 deselected = the PostgreSQL integration subset.)

**`cd App/Backend; ruff check .`**: PASS

```
All checks passed!
EXIT=0
```

**`openspec validate c-73-pseudonimizacion-tarjeta --strict`**: PASS

```
Change 'c-73-pseudonimizacion-tarjeta' is valid
EXIT=0
```

**Coverage** (`pytest tests/test_pseudonymizer.py --cov=app.utils.pseudonymizer`):

```
Name                         Stmts   Miss  Cover   Missing
----------------------------------------------------------
app/utils/pseudonymizer.py      69      1    99%   339
TOTAL                           69      1    99%
```

99% line coverage (re-verified; up from 98% since the added logic is exercised by the multi-card tests). The only uncovered line (339) is the `[`-label early-return inside `_replace_persona`, pre-existing from c-30 and unrelated to this change. All newly added CARD code paths are exercised.

---

## Strict TDD Compliance

### TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | WARN | No `sdd/c-73-pseudonimizacion-tarjeta/apply-progress` artifact with a "TDD Cycle Evidence" table was found in Engram. Reconstructed from `tasks.md` (explicit RED to GREEN to TRIANGULATE to REFACTOR blocks) and independent execution. |
| All tasks have tests | OK | 23/23 tasks map to artifacts; every behavior task has at least one test. |
| RED confirmed (tests exist) | OK | All new tests exist in `tests/test_pseudonymizer.py` and reference production behavior. RED itself is not re-runnable post-implementation. |
| GREEN confirmed (tests pass) | OK | 42/42 pass on independent execution. |
| Triangulation adequate | OK | Variants parametrized (4), window both ways (2), boundaries, determinism, combination, R067/R169 — multiple distinct expected values. |
| Safety Net for modified files | WARN | `tasks.md` 1.1 records the baseline; not independently reconstructable because the pre-change run was not persisted. |

**TDD Compliance**: 4/6 checks fully passed, 2 process-evidence gaps (see W3 — downgraded to a non-blocking SUGGESTION on re-verification).

### Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 42 | `tests/test_pseudonymizer.py` | pytest 8.3.3 |
| Integration | 1 (audit-log scenario) | `tests/test_pseudonymization_integration.py` | pytest-asyncio |
| E2E | 0 | — | not installed |
| **Total** | **43** | | |

### Changed File Coverage

| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `App/Backend/app/utils/pseudonymizer.py` | 99% | n/a (no branch plugin) | L339 (pre-existing) | Excellent |

**Average changed file coverage**: 99%

### Assertion Quality

Scan of `tests/test_pseudonymizer.py` (42 tests, new Section 8-10 for c-73):

- No tautologies (`assert True`, `assert 1 == 1`).
- No empty-collection-only assertions; negative tests are paired with positive tests for the same behavior.
- No type-only assertions used alone.
- Every assertion calls `pseudonymize(...)` (production code) and asserts on the returned text / `conteos`.
- No ghost loops; no smoke-test-only assertions.
- Negative tests use distinct, meaningful expected values (e.g. `"[TARJETA]" not in resultado.texto`, `conteos["tarjeta"] == 0`), not just empty checks.

**Assertion quality**: all assertions verify real behavior (0 CRITICAL, 0 WARNING).

### Quality Metrics

**Linter**: No errors (`ruff check .` — all checks passed).
**Type Checker**: Not available/configured for this module.

---

## Spec Compliance Matrix

Delta `specs/data-pseudonymization/spec.md` — 5 requirements, 16 scenarios.

| # | Requirement | Scenario | Test (file > name) | Result |
|---|-------------|----------|--------------------|--------|
| 1 | MODIFIED: Funcion pura con conteo de cobertura | La pseudonimizacion es deterministica | `test_pseudonymizer.py > test_pseudonymize_es_determinista`; `> test_pseudonymize_determinista_con_tarjeta` | PROVEN |
| 2 | MODIFIED: Funcion pura con conteo de cobertura | Texto sin datos personales: texto intacto y conteos en cero (incl. `tarjeta`) | `test_pseudonymizer.py > test_pseudonymize_texto_sin_pii_devuelve_texto_intacto_y_conteos_en_cero` | PROVEN |
| 3 | MODIFIED: Orden de aplicacion libre de colisiones | Email no se fragmenta como nombre propio | `test_pseudonymizer.py > test_pseudonymize_email_no_se_fragmenta_como_persona` | PROVEN |
| 4 | MODIFIED: Orden de aplicacion libre de colisiones | El numero de tarjeta no se fragmenta como telefono | `test_pseudonymizer.py > test_pseudonymize_tarjeta_no_se_fragmenta_como_telefono` | PROVEN |
| 5 | MODIFIED: Orden de aplicacion libre de colisiones | Combinacion de varias categorias de PII | `test_pseudonymizer.py > test_pseudonymize_combinacion_todas_las_categorias`; `> test_pseudonymize_combinacion_con_tarjeta` | PROVEN |
| 6 | MODIFIED: Auditoria de cobertura sin fuga de PII | El log DEBUG registra conteos **incluyendo `tarjeta`** sin texto | `test_pseudonymization_integration.py > test_log_debug_cobertura_sin_pii` (now asserts the emitted DEBUG event + `tarjeta` key + all five categories, and absence of PII) | PROVEN |
| 7 | MODIFIED: Auditoria de cobertura sin fuga de PII | Ningun log INFO expone el texto crudo | `test_pseudonymization_integration.py > test_log_debug_cobertura_sin_pii` | PROVEN |
| 8 | ADDED: Reemplazo de numeros de tarjeta con disparador contextual | Tarjeta agrupada con espacios se reemplaza | `test_pseudonymizer.py > test_pseudonymize_reemplaza_tarjeta_agrupada_con_espacios` | PROVEN |
| 9 | ADDED: ... disparador contextual | Tarjeta agrupada con guiones se reemplaza | `test_pseudonymizer.py > test_pseudonymize_reemplaza_tarjeta_agrupada_con_guiones` | PROVEN |
| 10 | ADDED: ... disparador contextual | Tarjeta contigua de 16 digitos se reemplaza | `test_pseudonymizer.py > test_pseudonymize_reemplaza_tarjeta_contigua_de_16_digitos` | PROVEN |
| 11 | ADDED: ... disparador contextual | La etiqueta es exactamente `[TARJETA]` en mayusculas | `test_pseudonymizer.py > test_pseudonymize_etiqueta_tarjeta_es_exactamente_mayusculas` | PROVEN |
| 12 | ADDED: ... disparador contextual | Variantes de disparador activan la regla | `test_pseudonymizer.py > test_pseudonymize_variantes_de_disparador_activan_tarjeta[tarjeta de credito/debito/numero de tarjeta/tarjetas]` (4 cases) | PROVEN |
| 13 | ADDED: ... disparador contextual | Un numero de 16 digitos fuera de la ventana no se enmascara | `test_pseudonymizer.py > test_pseudonymize_numero_a_mas_de_40_chars_no_se_enmascara` | PROVEN |
| 14 | ADDED: ... disparador contextual | Un numero de 16 digitos sin mencion de tarjeta no se enmascara | `test_pseudonymizer.py > test_pseudonymize_16_digitos_sin_mencion_no_se_enmascara` | PROVEN |
| 15 | ADDED: No regresion de corridas sin contexto | El identificador de DLL de R067 no se clasifica como tarjeta | `test_pseudonymizer.py > test_pseudonymize_r067_dll_no_se_clasifica_como_tarjeta` | PROVEN |
| 16 | ADDED: No regresion de corridas sin contexto | La mencion de tarjeta sin digitos (R169) no altera el texto | `test_pseudonymizer.py > test_pseudonymize_r169_mencion_sin_digitos_no_altera_texto` | PROVEN |

**Compliance summary**: 16/16 PROVEN, 0 PARTIAL, 0 FAILING, 0 UNTESTED. (Re-verified: scenario #6 upgraded from PARTIAL to PROVEN.)

---

## Adversarial Checks (independent probes)

All probes executed directly against the installed module (`python3` from `App/Backend`).

### 1. CARD runs BEFORE `_RE_TELEFONO` — CONFIRMED

`pseudonymizer.py` order is EMAIL (L284), TARJETA (L293), TELEFONO (L297), HOST, PERSONA. A card with context is fully consumed as `[TARJETA]` and `conteos["telefono"] == 0`:

```
in : 'mi tarjeta numero 4517 6712 3456 7890 vencio'
out: 'mi tarjeta numero [TARJETA] vencio'
counts: {'email': 0, 'telefono': 0, 'tarjeta': 1, 'host': 0, 'persona': 0}
```

### 2. Digit boundaries — CONFIRMED

A 16-digit substring inside a longer digit run with context is NOT masked as `[TARJETA]` (boundaries `(?<!\d)` / `(?!\d)` work):

```
in : 'mi tarjeta axm0102301239999320002302 fin'      (22-digit R067 run + trigger)
out: 'mi tarjeta axm010[TELEFONO] fin'
counts: {'...': ..., 'tarjeta': 0, 'telefono': 1, ...}

in : 'mi tarjeta 12345678901234567 fin'              (17-digit run + trigger)
out: 'mi tarjeta 1[TELEFONO] fin'
counts: {'...': ..., 'tarjeta': 0, 'telefono': 1, ...}
```

`conteos["tarjeta"] == 0` in both cases. (The residual `[TELEFONO]` fragmentation is the pre-existing TELEFONO false positive, explicitly OUT OF SCOPE per proposal/design — not worsened by this change.)

### 3. 40-char window enforced both ways — CONFIRMED

```
exactly 40 gap : out = 'mi tarjeta xxxx...(38) [TARJETA]'      tarjeta=1
41 gap         : out = 'mi tarjeta xxxx...(39) [TELEFONO] 7890' tarjeta=0
```
The number at exactly 40 chars is masked; at 41 it is not. Matches the two dedicated tests and the design's measured-from-end-of-trigger semantics.

### 4. Trigger variants / no-trigger — CONFIRMED

```
'mis tarjetas 4517 6712 3456 7890 vencen'  -> 'mis tarjetas [TARJETA] vencen'      tarjeta=1
'el codigo 4517 6712 3456 7890 vence'      -> 'el codigo [TELEFONO] 7890 vence'   tarjeta=0
```
Plural `tarjetas` works; a 16-digit run without any "tarjeta" mention is not masked by the card rule (it may still be consumed by the pre-existing phone rule).

### 5. Label exact + trigger preserved — CONFIRMED

```
in : 'mi tarjeta numero 4517 6712 3456 7890 vencio'
out: 'mi tarjeta numero [TARJETA] vencio'
```
The trigger (and its prefix/window) is preserved verbatim; only the number is replaced. Label is uppercase `[TARJETA]`.

### 6. Other categories unchanged, function pure/deterministic — CONFIRMED

- EMAIL / TELEFONO / HOST / PERSONA tests all still pass (full suite 1035 passed).
- Module source does NOT import `app.classifiers` or `app.services` (only `app.constants.SECTORES_CANONICOS`); no I/O, no logging in the module.
- Determinism probe: two invocations of a card-context text produced identical `texto` and `conteos` (`determinism: True`).

### 7. `conteos` includes `"tarjeta"` and full-dict test updated — CONFIRMED

`conteos` initialized as `{email, telefono, tarjeta, host, persona}` (L281-287); the full-dict test (L38-44) expects `"tarjeta": 0`. Passes.

### 8. Hard constraints unchanged — CONFIRMED

`git diff --name-only HEAD` returns exactly:
```
App/Backend/app/utils/pseudonymizer.py
App/Backend/tests/test_pseudonymization_integration.py
App/Backend/tests/test_pseudonymizer.py
openspec/changes/c-73-pseudonimizacion-tarjeta/tasks.md
```
- `git diff HEAD -- App/Backend/app/constants.py docs/prompt_gemini.txt evaluation/corpus.py App/Backend/app/classifiers/keywords.py` is empty.
- `SECTORES_CANONICOS` still the five exact strings, case-sensitive, no accents (`constants.py` L18-22).
- `KEYWORD_MAP` lives in `app/classifiers/keywords.py` — untouched.
- `evaluation/corpus.py::_a_float` — untouched.

### Additional edge probe (W1 — now FIXED)

```
'mis tarjetas 1111 1111 1111 1111 y 2222 2222 2222 2222'
  -> 'mis tarjetas [TARJETA] y [TARJETA]'   tarjeta=2, telefono=0
```
A single trigger now masks **both** subsequent cards inside its forward window; the trigger phrase is preserved and no digits remain. See the W1 resolution in "Focused Re-verification".

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Pure function with `tarjeta` in `conteos` | Implemented | `pseudonymizer.py` L281-287; dataclass frozen; deterministic. |
| Order CARD before TELEFONO | Implemented | L289/L293/L318; documented in module + function docstrings (5 categories). |
| 40-char module constant | Implemented | `_CARD_CONTEXT_WINDOW_CHARS = 40` (L67). |
| Contextual trigger `tarjetas?` + window + boundaries | Implemented | `_RE_TRIGGER_TARJETA` (L94) + `_RE_NUMERO_TARJETA` (L96-99); forward windows computed pre-substitution (L299-302); callback `_replace_numero_tarjeta` (L306-312) masks every run whose start falls in a window. |
| Audit log enumerates `tarjeta` | Implemented and asserted | `incidente_service.py` L292-295 forwards `**resultado_pseudo.conteos`; asserted by `test_log_debug_cobertura_sin_pii` (W2 resolved). |
| No Luhn / no non-16 lengths | Implemented | No Luhn logic; only 16-digit grouped/contiguous forms. |
| Non-regression for context-free digit runs | Implemented | Boundary lookarounds prevent partial 16-of-N capture; R067 stays `tarjeta: 0`. |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1: `[TARJETA]` label + `tarjeta` count | Yes | Exact uppercase label; count key initialized to 0. |
| D2: EMAIL, CARD, TELEFONO, HOST, PERSONA | Yes | Verified by source order and probes. |
| D3: contextual trigger, forward 40-char window, module constant | Yes | Window enforced both ways; forward-only (number-before-trigger not masked, as designed). |
| D4: single combined regex + function replacement | Deviated (valid improvement) | Implementation splits into `_RE_TRIGGER_TARJETA` + `_RE_NUMERO_TARJETA` with a position-based callback. Necessary to fix W1: a single `subn` over a combined pattern masks only the first number per trigger. Same observable contract; module constant, label, and order preserved. |
| D5: purity, no injected parameter | Yes | Signature unchanged; no I/O/settings/logging. |
| Docstrings updated to 5 categories | Yes | Module + function docstrings list `[TARJETA]` and the new order. |
| Non-goals respected (no Luhn, no Amex 15) | Yes | Confirmed absent. |

---

## Issues Found

**CRITICAL** (must fix before archive):
- None.

**WARNING** (should fix / surface):
- None. W1 and W2 (raised in the original verify) were fixed and independently confirmed in the focused re-verification; W3 was downgraded to a non-blocking SUGGESTION (see below).

**RESOLVED since the original verify**:
- **W1 — Multiple cards sharing one trigger: FIXED.** The two-step detector now masks every card within the trigger's forward window (probe: `'mis tarjetas 1111 1111 1111 1111 y 2222 2222 2222 2222'` → `'mis tarjetas [TARJETA] y [TARJETA]'`, `tarjeta=2`, no visible digits). New tests `test_pseudonymize_multiples_tarjetas_con_un_solo_disparador` and `test_pseudonymize_multiples_tarjetas_contiguas_con_un_disparador` lock it. Negative cases unchanged (out-of-window, longer digit run, no-trigger, R067 all `tarjeta=0`).
- **W2 — Audit-log scenario: FIXED.** `test_log_debug_cobertura_sin_pii` now uses `structlog.testing.capture_logs` and asserts the emitted DEBUG event, `log_level == "debug"`, the `tarjeta` key, and all five categories, while keeping the no-PII assertions. Passes; non-vacuous (verified independently).

**SUGGESTION** (nice to have):
- **W3 — Strict-TDD process evidence gap (downgraded from WARNING)**: no `sdd/c-73.../apply-progress` artifact with a "TDD Cycle Evidence" table exists in Engram, and `openspec/config.yaml` has no `strict_tdd` key. Functional TDD substance IS independently verified (tests exist, are triangulated, and pass; `tasks.md` documents explicit RED→GREEN→TRIANGULATE→REFACTOR blocks). The gap is a persistence/traceability artifact, not evidence of skipped TDD, so it does not block archive. Persisting the apply-progress table would close it.
- **S1 — Grouped form with trailing separators**: the 4-4-4-4 alternative requires a non-digit after the 4th group, so `"mi tarjeta 1234 5678 9012 3456 78"` becomes `[TARJETA] 78` (synthetic, not a real 16-digit card, not spec'd). Consider whether a trailing-boundary rule on the grouped branch is desirable.
- **S2 — Symmetric window**: design explicitly defers "number ... de mi tarjeta" (trigger after the number). A number placed before the trigger is currently not card-masked; documented as future work.

**NOTE (accepted nuance, not a defect)**:
- The window is character-based over the whole string, so a trigger can reach a card across a newline (`'mi tarjeta\n4517 6712 3456 7890'` → masked). This is the safe direction (masks more contextual PII, never less) and the spec does not constrain the window to a single line. Accepted as intended.

---

## Residual Notes

- The residual TELEFONO fragmentation of long context-free digit runs (R067 becoming `axm010[TELEFONO]`) is a PRE-EXISTING behavior explicitly declared OUT OF SCOPE; this change neither introduces nor worsens it (`tarjeta` stays 0).
- `test_pseudonymization_integration.py` WAS edited in the W2 fix (the previous report's claim that it required no edit was superseded); the change is confined to `test_log_debug_cobertura_sin_pii`.
- One unrelated pre-existing warning appears in test output (Starlette `import multipart` deprecation).

---

## Status

**PASS** — implementation is complete (23/23), behaviorally compliant with **16/16 spec scenarios PROVEN** (scenario #6 upgraded from PARTIAL), all targeted and full offline suites green (42 focused / 1035 offline), linter and strict validation clean, hard constraints untouched. No CRITICAL or WARNING issue blocks archive; W1/W2 are resolved and W3 is a non-blocking process traceability note.
