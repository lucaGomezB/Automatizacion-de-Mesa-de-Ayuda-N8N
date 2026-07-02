# Code Audit — LLM Adoption and Labor Market Outcomes
**Date:** 2026-04-10
**Reviewer:** coder-critic
**Paper type:** Reduced-form
**Score:** 82/100
**Mode:** Full

## Code-Strategy Alignment: DEVIATION
Strategy memo specifies shift-share design with Adao et al. (2019) exposure-robust standard errors. Code implements the shift-share estimator correctly via `fixest::feols()` but computes standard errors using conventional occupation-level clustering. This understates SEs in the presence of correlated exposure shocks.

## Paper-to-Code Map: PRESENT
```
Paper symbol    → Code variable        → Script
E_ot (employ)   → emp_share            → 02_build_panel.R:67
alpha_o (expos) → aioe_score           → 01_build_exposure.R:143
Post_t          → post_chatgpt         → 02_build_panel.R:89
tau (ATT)       → coef_exposure_post   → 03_estimate.R:52
X_ot (controls) → controls_mat         → 02_build_panel.R:102
```

## Sanity Checks: CONCERNS
- Sign: PASS — negative employment coefficient for high-exposure occupations, directionally consistent with displacement hypothesis
- Magnitude: FLAG — 3.2pp decline in 18 months exceeds historical automation displacement rates by ~3x
- Zero counts: PASS — no occupation-quarters with zero employment in sample
- Sample size: PASS — N=36,800 occupation-quarters (460 SOC codes x 80 months)
- Balance: FLAG — exposure quintiles are not balanced on pre-period employment levels; Q5 occupations have 40% lower baseline employment

## Numerical Discipline: PASS
- No float comparisons with `==`
- Exposure index bounded [0,1] with explicit `clamp()` after GPT scoring
- Log transformation uses `log(emp + 1)` to handle small cells — acceptable but discuss sensitivity to the +1 choice

## Robustness: Incomplete
Strategy memo requires 7 robustness checks. Code implements 4 of 7.
- [x] Alternative exposure measure (Webb 2020 patent-based)
- [x] Dropping top/bottom 1% of exposure distribution
- [x] Quarterly vs. monthly CPS aggregation
- [x] Controlling for remote work feasibility (Dingel & Neiman 2020)
- [ ] Rambachan & Roth (2023) sensitivity — NOT IMPLEMENTED
- [ ] Placebo test (2012-2018 with 2023 exposure) — NOT IMPLEMENTED
- [ ] Leave-one-out by SOC group — NOT IMPLEMENTED

## Code Quality

| # | Category | Status | Issues |
|---|----------|--------|--------|
| 1 | Project layout | OK | Scripts numbered 01-05, clear pipeline |
| 2 | Script headers | OK | Purpose, inputs, outputs, runtime estimates documented |
| 3 | Console output | OK | Progress bars via `cli::cli_progress_bar()`; no raw `print()` |
| 4 | Reproducibility | OK | `set.seed(20250301)` in `01_build_exposure.R`; `here()` for all paths |
| 5 | Numerical discipline | OK | Exposure clamped; no float `==`; log(x+1) documented |
| 6 | Function design | OK | `compute_aioe()` modular; `estimate_did()` reused across specifications |
| 7 | Figure quality | WARN | Event study plot uses `ggtitle("Event Study: Employment")` — violates INV-12, title belongs in LaTeX `\caption{}` |
| 8 | Table quality | OK | Bare `tabular` via `modelsummary`; no `\begin{table}` wrapper (INV-13 compliant) |
| 9 | RDS/checkpoint | FAIL | No RDS save after `01_build_exposure.R` which calls GPT API (45 min, $12.40). Re-running `03_estimate.R` requires full rebuild including API calls |
| 10 | Comment quality | OK | Key methodology decisions annotated with paper references |
| 11 | Error handling | OK | `stopifnot(all(aioe_score >= 0 & aioe_score <= 1))` after API scoring; retry logic for API timeouts |
| 12 | Prohibited patterns | OK | No `setwd()`, `rm(list=ls())`, `install.packages()`, `attach()` |

## Score Breakdown
```
Starting:                                100
Code-strategy alignment (missing SEs):    -8   [Adao et al. SEs not implemented]
Missing robustness (Rambachan & Roth):    -3   [critical for identification]
Missing robustness (placebo):             -2   [important for interpretation]
Missing robustness (leave-one-out):       -2   [needed for shift-share diagnostics]
Figure title in ggplot (INV-12):          -3   [event_study_employment.R:78]
No RDS checkpoint after API calls:        -5   [45 min + $12.40 lost on re-run]
Magnitude flag (3x historical rate):     +5   [advisory, flagged in sanity check]
                                        -----
Final:                                 82/100   [WARN: strategy alignment deduction
                                                 increases if Adao SEs change significance]
```

## Escalation Status: None (Strike 0 of 3)

## Recommendations
1. **[CRITICAL]** Add Adao et al. (2019) SEs via `ShiftShareSE` package. Three lines of code: `library(ShiftShareSE); reg_ss <- ivreg_ss(...); summary(reg_ss)`. This resolves the strategy alignment deduction and may change inference.
2. **[MAJOR]** Add `saveRDS(exposure_panel, here("data/cleaned/exposure_index.rds"))` at end of `01_build_exposure.R`. This prevents re-running 45 minutes of GPT API calls (and spending $12.40) every time downstream scripts change.
3. **[MAJOR]** Implement the three missing robustness checks. The Rambachan & Roth analysis is 10 lines with `HonestDiD`. The placebo is a copy of `03_estimate.R` with a date filter. The leave-one-out is a loop over `unique(soc2)`.
4. **[MINOR]** Replace `ggtitle()` with empty string in all figure scripts. Panel labels inside facets are fine per INV-12.
