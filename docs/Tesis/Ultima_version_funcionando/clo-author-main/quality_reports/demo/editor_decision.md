# Editorial Decision
**Date:** 2026-04-10
**Journal:** Quarterly Journal of Economics
**Paper:** The Effect of Large Language Model Adoption on Labor Market Outcomes: Evidence from ChatGPT's Staggered Rollout
**Decision:** Major Revisions

## Editor's Assessment

This paper tackles perhaps the most pressing question in labor economics right now: what happens to workers when firms gain access to large language models? The question alone warrants serious attention. The data construction — linking O*NET task descriptions to GPT capability assessments to construct an occupation-level exposure index, then tracking CPS employment outcomes — is creative and well-executed. I can see this becoming a standard approach in the AI-and-labor literature.

That said, both referees converge on a fundamental concern that I share: the paper cannot distinguish displacement from augmentation using its current design. The exposure measure captures which occupations *could* be affected by LLMs, not how they are affected. The negative employment result could reflect displacement, but it could equally reflect compositional shifts (firms hiring fewer but more productive workers in these occupations) or pre-existing trends (these occupations were already declining). The Methods Referee's suggestion to decompose exposure into substitution and complementarity components is, in my view, essential — not just for this paper, but for the entire literature that will follow it.

The pre-trends concern is serious but not fatal. If the authors can show a clear acceleration after November 2022 on top of the existing trend, and if the Rambachan & Roth (2023) sensitivity analysis shows the result survives reasonable violations, I would be satisfied. The Domain Referee is right that the paper should engage with Brynjolfsson et al. (2025) and the growing augmentation evidence — the paper currently reads as if augmentation doesn't exist.

## Referee Summary

**Domain Referee (Structuralist):** 73/100 — Major Revisions
Finds the question first-order important but the theoretical framework underdeveloped. Wants a simple model distinguishing displacement from augmentation before going to the data. Concerned that the paper doesn't engage with the augmentation evidence and will age poorly if the employment effects reverse.

**Methods Referee (Credibility Revolution):** 71/100 — Major Revisions
Core shift-share design is competently executed but missing standard diagnostics (Goldsmith-Pinkham et al. 2020, Adao et al. 2019). Three major concerns: exposure measure conflates displacement/augmentation, pre-trends start in 2019, and result is driven by 3 of 22 SOC groups. All addressable with specified remedies.

## Concerns Classification

### MUST Address
1. **[FATAL if unaddressed]** Decompose the exposure index into substitution and complementarity components. Show which component drives the employment decline. Without this, the paper's headline finding is uninterpretable. *(Methods Referee, Major #1; Domain Referee, Major #1)*

2. **[ADDRESSABLE]** Implement Rambachan & Roth (2023) sensitivity analysis to quantify how large a pre-trend violation would need to be to explain the result. Show whether the treatment effect accelerates after November 2022 rather than merely continuing the 2019+ trend. *(Methods Referee, Major #2)*

3. **[ADDRESSABLE]** Report the full suite of Goldsmith-Pinkham et al. (2020) shift-share diagnostics: Rotemberg weights, leave-one-out sensitivity, and Adao et al. (2019) standard errors. The result being driven by 3 SOC codes needs to be confronted directly. *(Methods Referee, Major #3)*

### SHOULD Address
4. **[ADDRESSABLE]** Engage seriously with the augmentation evidence (Brynjolfsson et al. 2025, Noy & Zhang 2023, Peng et al. 2023). The paper currently presents a displacement-only narrative. At minimum, discuss why occupation-level results might differ from the firm-level augmentation findings. *(Domain Referee, Major #2)*

5. **[ADDRESSABLE]** Add a placebo test using the 2012-2018 period with 2023 exposure scores. If the exposure index predicts employment changes before LLMs existed, the identifying variation is contaminated. *(Methods Referee, Technical Suggestions)*

6. **[ADDRESSABLE]** Discuss the zero wage effect alongside the negative employment effect. These are jointly inconsistent under standard models and the paper needs to take a position on why. *(Methods Referee, Minor #4)*

### MAY Push Back
7. **[TASTE]** Domain Referee wants a formal model with displacement and augmentation equilibria. I do not require this — a clear conceptual framework with testable predictions is sufficient. A full model risks overwhelming a paper whose contribution is empirical. Authors may include one in an appendix if they wish.

8. **[TASTE]** Domain Referee suggests restricting the sample to 2022-2024 to avoid the pre-trends issue. This sacrifices the pre-period event study entirely. I prefer keeping the full sample with the Rambachan & Roth approach.

## Where Referees Disagree

The Domain Referee wants a structural model motivating the empirical design. The Methods Referee wants cleaner reduced-form identification. These are not contradictory — a conceptual framework that generates the substitution/complementarity decomposition would satisfy both. The decomposition is the key revision. I recommend the authors frame it as: "our exposure index has two components; here is how to think about each; here is what we find for each." This addresses the Domain Referee's theoretical concern and the Methods Referee's identification concern simultaneously.

The Domain Referee also argues the paper should present firm-level evidence to complement the occupation-level analysis. I agree this would strengthen the paper but do not require it for this revision. If occupation-level data from the CPS is the contribution, that is sufficient — but the limitations relative to firm-level studies must be discussed honestly.

## Revision Timeline

I expect to receive the revision within 6 months. The decomposition of the exposure index is the critical revision — if it substantially changes the results (e.g., negative effects concentrate in high-complementarity rather than high-substitution occupations), please contact me before submitting the full revision to discuss reframing.
