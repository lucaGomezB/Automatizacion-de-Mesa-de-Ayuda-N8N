## Why

A post-defense CONEAU-level evaluation of the thesis document identified 5 structural and bibliographic deficiencies plus 1 critical integrity issue: two references cited across 4 chapters (Karchhud2024, Mehdi2023) are LLM-hallucinated fabrications that do not exist in any academic database. These must be removed before final submission. Four additional recommendations address chapter numbering, weak bibliographic references, a misleading statistical argument, and missing ethics documentation.

## What Changes

- **CRITICAL**: Remove two fabricated references (Karchhud2024, Mehdi2023) from Bibliography_base.bib and all .tex files. Rewrite affected paragraphs to flow naturally without unsupported quantitative claims.
- **R1**: Rename Chapter 13 from `13-anexos.tex` to `12-anexos.tex` with corresponding `\input` update in `main.tex`.
- **R2**: Replace weak bibliographic references: Pressman2020 with Galup2009 for ITSM process degradation; Crispin2009 with Ladas2009 for Scrumban methodology (keep Crispin2009 for testing pyramid usage).
- **R4**: Fix misleading CV argument in Chapter 8 (discussion) that implied automated CV was substantially more predictable when actual values are nearly identical (22.5% vs 23.4%). Replace with arguments about absolute range compression.
- **R5**: Add post-hoc debriefing discussion to Chapter 11 (ethics/legal) regarding operators whose times were measured without their knowledge during data collection.
- **R6**: Out of scope -- not addressed in this change.

## Capabilities

### New Capabilities

None. This change addresses the existing thesis document only.

### Modified Capabilities

- `tesis-document`: Adds CONEAU recommendation requirements (R1-R5) as new scenarios. Modifies existing citation integrity requirement to account for the verified reference count after Karchhud2024/Mehdi2023 removal and Ladas2009 addition.

## Impact

- **Files modified**: 11 files across `docs/Tesis/v8 (IA)/paper/`
  - `Bibliography_base.bib` (remove 2 entries, add 1 entry)
  - `sections/01-introduccion.tex` (remove fabricated citations, rewrite claims)
  - `sections/02-marco-teorico.tex` (replace Pressman -> Galup)
  - `sections/03-estado-del-arte.tex` (remove fabricated citations)
  - `sections/04-marco-metodologico.tex` (replace Crispin -> Ladas for Scrumban)
  - `sections/06-implementacion.tex` (replace Crispin -> Ladas where Scrumban)
  - `sections/08-discusion.tex` (fix CV argument, remove fabricated citation)
  - `sections/10-recomendaciones.tex` (remove fabricated citation)
  - `sections/11-aspectos-legales.tex` (add debriefing paragraph)
  - `sections/13-anexos.tex` -> renamed to `sections/12-anexos.tex`
  - `main.tex` (update `\input` for renamed file)
- **Verification**: `verify_citations.py` must report zero orphans and exact reference count after all edits
- **Compilation**: XeLaTeX + biber cycle must produce clean PDF with zero fatal errors
