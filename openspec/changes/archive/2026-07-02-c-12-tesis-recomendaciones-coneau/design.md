## Context

The thesis document (`docs/Tesis/v8 (IA)/paper/`) passed a post-defense CONEAU evaluation that identified 5 recommendations (R1-R5) and 1 critical integrity issue (R3). Change C-11 previously addressed prose quality, citation rendering, and structural deficiencies. This change (C-12) is the final polishing pass before formal submission. All edits are to LaTeX source files; no software code is modified.

**Existing state**: 34 references in Bibliography_base.bib, 11 section files, main.tex with 13 `\input` commands. References Karchhud2024 and Mehdi2023 have been verified as nonexistent via Google Scholar and Crossref API.

**Constraints**:
- All prose must remain in neutral academic Spanish (rioplatense)
- APA 7th edition citation style via biblatex-apa
- XeLaTeX is the canonical compilation engine
- `verify_citations.py` must report zero orphans after all edits
- No changes to technical claims or numerical results (only rephrasing of claims that lack supporting citations)

## Goals / Non-Goals

**Goals:**
1. Eliminate two fabricated references (Karchhud2024, Mehdi2023) from both .bib and all .tex citations
2. Rewrite paragraphs that cited fabricated references to flow naturally, using the thesis's own contributions and existing verifiable references as substitutes
3. Rename chapter 13-anexos to 12-anexos with corresponding main.tex update
4. Replace Pressman2020 with Galup2009 for ITSM process degradation claims
5. Replace Crispin2009 with Ladas2009 for Scrumban methodology (preserve Crispin2009 for testing pyramid)
6. Fix misleading CV argument in Chapter 8 discussion
7. Add post-hoc debriefing paragraph to Chapter 11 ethics

**Non-Goals:**
- R6 (additional polishing -- explicitly out of scope)
- Any modification to software code (backend, frontend, evaluation, N8N workflow)
- Any modification to OpenAPI spec, CI pipeline, or project documentation
- Adding new substantive content beyond what is required by the recommendations

## Decisions

### D1: Reference removal strategy for fabricated citations

**Decision**: Remove Karchhud2024 and Mehdi2023 entirely from Bibliography_base.bib and all .tex files. Replace unsupported quantitative claims with either the thesis's own empirical results or citations to verified references.

**Rationale**: These references do not exist in any academic database. Keeping them would constitute academic fraud. Partial retention (keeping the references but removing quantitative claims) is insufficient because the references themselves are fabricated.

**Alternatives considered**:
- *Replace with similar real references*: Rejected because the specific claims attributed to these references (Spanish language gap, quantitative baselines) cannot be attributed to real references that never made those claims.
- *Keep references flagged as unverified*: Rejected -- unacceptable for formal academic submission.

### D2: Substitute references for unsupported claims

**Decision**: Where Karchhud2024 was cited for the "brecha del espanol" (Spanish language gap) claim, replace with the thesis's own contribution -- the thesis itself demonstrates Spanish rioplatense performance is competitive. Where Mehdi2023 was cited for state-of-art baselines (40-60%, 35%, 60%), replace with Paramesh2019 and Revina2020 (already in bibliography) for general classification baselines.

**Rationale**: The thesis's empirical results (F1 ~0.88 for hybrid classifier) are verifiable within the document itself. Paramesh2019 and Revina2020 are real, verifiable references already present in the bibliography.

### D3: Ladas2009 BibTeX entry

**Decision**: Add Ladas2009 as the canonical reference for Scrumban methodology:

```bibtex
@book{Ladas2009_scrumban,
  author    = {Ladas, Corey},
  title     = {Scrumban: Essays on Kanban Systems for Lean Software Development},
  publisher = {Modus Cooperandi Press},
  year      = {2009},
}
```

**Rationale**: Ladas2009 is the foundational text on Scrumban. Crispin2009 (Agile Testing) is preserved for testing pyramid references in Chapter 6.

### D4: Chapter numbering fix

**Decision**: Rename `13-anexos.tex` to `12-anexos.tex` via filesystem rename. Update `\input{sections/13-anexos}` to `\input{sections/12-anexos}` in `main.tex`.

**Rationale**: The thesis has 12 chapters (not 13). The mismatch between the filename counter and actual chapter count was a numbering error.

### D5: CV argument fix strategy

**Decision**: Replace the misleading "sustancialmente mas predecible" claim about the automated CV with a discussion of absolute range compression. The actual numbers: automated time range 96-289s vs manual 11-31s. The argument shifts from CV percentages (which are nearly identical at 22.5% vs 23.4%) to absolute range: manual processing takes 11-31s (tight range because all tasks are simple form-filling) while automated processing ranges 96-289s (wider range because tasks vary from simple classification to full pipeline execution with external API calls).

**Rationale**: The absolute range argument is mathematically honest and better illustrates the genuine difference between the two approaches -- automated processing handles a wider variety of task complexities, leading to a naturally wider time range. The CV comparison was misleading.

### D6: Debriefing paragraph placement

**Decision**: Add the debriefing paragraph at the end of the existing ethics discussion in `11-aspectos-legales.tex`, after the informed consent section and before the chapter conclusion.

**Rationale**: The debriefing is a logical extension of the informed consent discussion. It closes the ethical loop: data was collected from operators, operators were later informed, and operators were given the right to withdraw.

## Risks / Trade-offs

- **Risk**: Paragraph rewrites around removed citations may introduce prose quality regression (mechanical transitions, repetitive structure)
  - **Mitigation**: Apply the same prose quality standards established in C-11. Review rewritten paragraphs for sentence rhythm variety and avoidance of formulaic transitions.

- **Risk**: Ladas2009 may not have a readily verifiable DOI (self-published via Modus Cooperandi Press)
  - **Mitigation**: Ladas2009 is a well-known, widely cited book in the agile community. The BibTeX entry uses standard fields. A Google Books or Amazon link can be provided if DOI is unavailable.

- **Risk**: Reference count change (34 -> 32) may break hardcoded expectations
  - **Mitigation**: Update the spec scenario to reflect the new count. `verify_citations.py` will confirm the exact count matches.

- **Risk**: File rename (13-anexos -> 12-anexos) could break git tracking
  - **Mitigation**: Use `git mv` to preserve file history. Update main.tex in the same commit.
