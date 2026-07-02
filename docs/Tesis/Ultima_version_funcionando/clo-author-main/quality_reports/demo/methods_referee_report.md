# Methods Referee Report
**Date:** 2026-04-10
**Paper:** The Effect of Large Language Model Adoption on Labor Market Outcomes: Evidence from ChatGPT's Staggered Rollout
**Paper type:** Reduced-form
**Design:** DiD (staggered rollout) + shift-share exposure measure
**Recommendation:** Major Revisions
**Overall Score:** 71/100

## Summary

This paper estimates the effect of LLM adoption on occupation-level employment, wages, and task composition using a difference-in-differences design that exploits variation in occupational exposure to ChatGPT capabilities. The exposure measure combines pre-period task content (from O*NET) with the timing of GPT model releases as a shift-share instrument. The question is timely and the data construction is impressive. However, the identification strategy has two fundamental concerns: the exposure measure conflates potential displacement with potential augmentation, and the parallel trends assumption is difficult to defend when high-exposure occupations were already on differential trends pre-2022.

## Dimension Scores
| Dimension | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Identification Strategy | 35% | 65 | Exposure measure conflates displacement/augmentation; pre-trends questionable |
| Estimation & Implementation | 25% | 72 | Shift-share implementation correct but Goldsmith-Pinkham et al. (2020) diagnostics missing |
| Statistical Inference | 20% | 78 | Clustering at occupation level appropriate; Adao et al. (2019) SEs needed for shift-share |
| Robustness & Sensitivity | 15% | 68 | No Oster bounds; no alternative exposure measures; no placebo with pre-LLM AI wave |
| Replication Readiness | 5% | 88 | CPS extracts documented; O*NET linkage replicable; GPT API access required for task scoring |
| **Weighted** | 100% | **71** | |

## Sanity Check Results
- **Sign:** Ambiguous. Paper finds negative employment effect, but recent evidence (Brynjolfsson et al. 2025) shows augmentation in high-exposure occupations. The sign depends entirely on which occupations drive the result.
- **Magnitude:** Questionable. 3.2pp employment decline in top-quintile exposure occupations over 18 months is large. This implies LLMs displaced workers faster than the PC revolution displaced typists. Need time-series decomposition.
- **Dynamics:** Concerning. Event study shows a downward pre-trend in high-exposure occupations starting 2019 — three years before ChatGPT. Authors attribute this to COVID but do not test this claim.
- **Consistency:** Fragile. Result is driven by 3 of 22 two-digit SOC codes (office/admin, legal support, translation). Excluding any one group reduces significance below conventional levels.

## Major Comments

1. **Exposure measure does not distinguish displacement from augmentation.**
   The Felten et al. (2023) AI occupational exposure index captures which tasks *can* be performed by LLMs, not which tasks *will be* displaced. An occupation with high exposure could see employment growth (if LLMs increase demand for the occupation's non-automatable tasks) or decline (if firms substitute AI for workers). The paper treats all exposure as displacement. This is an assumption, not an identification result.
   - **What would change my mind:** Decompose the exposure index into a "substitution" component (tasks where LLM output replaces human output) and a "complementarity" component (tasks where LLM output enhances human productivity). Eloundou et al. (2023) provide a framework for this. Show that displacement effects concentrate in high-substitution occupations and that high-complementarity occupations show augmentation. If the aggregate negative effect survives this decomposition, the finding is much more credible.

2. **Pre-trends invalidate the parallel trends assumption.**
   The event study in Figure 3 shows that high-exposure occupations were already declining in employment relative to low-exposure occupations from 2019 onward. The paper's explanation — that COVID differentially affected these occupations — is plausible but untested. If these occupations were on a differential trajectory for reasons unrelated to LLMs (e.g., ongoing automation via RPA, offshoring), the DiD estimate captures this trend, not the LLM effect.
   - **What would change my mind:** (a) Implement Rambachan & Roth (2023) sensitivity analysis showing how large a linear pre-trend violation would need to be to explain away the result. (b) Control for pre-period automation exposure (robots, RPA software adoption) interacted with time. (c) Show that the treatment effect *accelerates* after November 2022 (ChatGPT launch) relative to the pre-trend — a level shift on top of the trend would be more convincing than just continuing the trend.

3. **Shift-share diagnostics are missing.**
   The shift-share design uses pre-period O*NET task shares as weights and GPT release timing as shocks. Goldsmith-Pinkham, Sorkin & Swift (2020) show that identification in shift-share designs can come from either the shares or the shocks. The paper does not report: (a) which occupations have the largest Rotemberg weights, (b) whether the result is sensitive to dropping high-leverage occupations, or (c) the Adao, Kolesar & Morales (2019) standard errors that account for cross-occupation correlation in the shocks.
   - **What would change my mind:** Report the full Goldsmith-Pinkham et al. (2020) diagnostics. Show the top-5 Rotemberg weight occupations. Report results dropping each one. Implement Adao et al. (2019) SEs. If the top-weight occupations are sensible and the result survives leave-one-out, this concern is resolved.

## Minor Comments

1. The CPS sample excludes self-employed workers. If LLMs enable freelancing (writers, coders, designers shifting to self-employment), the employment decline in the CPS may overstate actual job destruction. Discuss this and, if possible, supplement with ACS data that captures self-employment.

2. Table 2 reports the exposure index quintile cutoffs but does not report which specific occupations fall in each quintile. Add an appendix table mapping quintiles to SOC codes with occupation names. Readers need to verify that the groupings make economic sense.

3. The GPT capability scores (used to construct the exposure index) are generated by GPT-4 itself. This circularity should be discussed. Webb (2020) uses patent-based measures as an alternative that avoids self-assessment bias.

4. The wage results (Table 4) show zero effect on hourly wages despite significant employment decline. This is inconsistent with a competitive labor market model. Either wages are sticky downward, composition effects mask the wage decline (displaced workers are lower-paid), or the employment result is spurious. The paper should discuss which interpretation it favors.

## Technical Suggestions

- Implement the Borusyak, Hull & Jaravel (2022) shift-share framework as the primary specification. This provides both the recentered instrument and the correct SEs for shift-share designs with potentially endogenous shares.
- Add a placebo test using the 2012-2018 pre-period: assign "treatment" based on 2023 exposure scores and estimate the same model. If you find effects during this period, the exposure index is capturing secular trends, not LLM-specific impacts.
- Consider a triple-difference design: high vs. low exposure occupations, before vs. after ChatGPT, in industries with high vs. low AI adoption rates (from the Census Business Trends survey). This third difference controls for occupation-specific trends.

## Questions for the Authors

1. The exposure index is constructed at the 6-digit SOC level but the analysis is at 2-digit SOC. How sensitive are results to the aggregation level? Do results hold at 4-digit SOC?
2. What happens to the employment result if you control for remote work feasibility (Dingel & Neiman 2020)? High-exposure occupations overlap substantially with remote-compatible occupations, which had independent labor market dynamics post-COVID.
3. The paper ends in 2024Q2. ChatGPT launched November 2022. This is 18 months of post-treatment data. Is this enough time for firm-level adoption decisions to translate into occupation-level employment changes? What does the technology adoption literature suggest about timing?
