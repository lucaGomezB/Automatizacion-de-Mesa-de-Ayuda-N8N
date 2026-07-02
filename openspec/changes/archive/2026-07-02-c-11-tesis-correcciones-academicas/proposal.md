## Why

The thesis document (`docs/Tesis/v8 (IA)/1_Tesis_Mesa_Ayuda_UTN_COMPLETA.docx`) was evaluated against CONEAU-level academic standards and found to have critical formatting and rendering deficiencies. The DOCX is a flawed conversion artifact from LaTeX source -- it contains zero rendered citations, no bibliography section, raw LaTeX math equations (`$$...$$`), corrupted tables, and ASCII table grids instead of formatted tables. These defects would cause the thesis to fail a formal academic review. The LaTeX source at `docs/Tesis/v8 (IA)/paper/` is the authoritative version with 54 properly placed `\textcite{}`/`\parencite{}` commands and 34 BibLaTeX entries, but it has never been compiled to a proper PDF. Additionally, the LaTeX prose exhibits AI-generated writing patterns that need revision to meet the depth and voice expected of a "Trabajo Final de Carrera" at UTN FRM, Tecnicatura Universitaria en Programacion.

## What Changes

### TIER 1 -- Critical (blocking for thesis defense)
- **Generate a canonical PDF from LaTeX source**: Compile the existing LaTeX source via XeLaTeX to produce a rendered PDF with all 54 citations in APA 7th format, complete bibliography, proper math equations, and professionally formatted tables.
- **Verify PDF quality**: Confirm all citations resolve, bibliography is complete, cross-references work, tables are well-formatted with booktabs styling.
- **Establish PDF as the canonical thesis format**: The current DOCX is deprecated as a conversion artifact with known defects.

### TIER 2 -- Moderate (academic quality)
- **Remove AI writing patterns from 11 section files**: Address mechanical enumeration ("En relacion con el primer objetivo especifico..."), repetitive rhetorical formulas ("conviene reconocer explicitamente", "resulta pertinente destacar"), uniform sentence length, and shallow analysis. Add human analytical voice throughout.
- **Strengthen Chapter 6 (implementacion)**: Expand from 57 enumeration lines to a reasoned chapter explaining technology choices (FastAPI vs alternatives), N8N flow design rationale (12 nodes), integration challenges, and connection to the Scrumban agile process from Chapter 4.
- **Add English abstract**: Insert a ~200-250 word abstract in `00-resumen.tex` after the Spanish "Resumen" section.

### TIER 3 -- Nice to have
- **Generate secondary DOCX via pandoc**: Use `pandoc --citeproc` to produce an editable DOCX copy. Accept that pandoc output quality will be lower than the canonical PDF.

## Capabilities

### New Capabilities
- `tesis-document`: Thesis document quality -- the canonical PDF rendering, prose revision for academic standards, English abstract, and secondary DOCX output. Covers the thesis artifact at `docs/Tesis/v8 (IA)/paper/`.

### Modified Capabilities
<!-- No existing software specs are modified. The thesis is a documentation artifact separate from the tracked software system. -->

## Impact

- **Thesis LaTeX source**: `docs/Tesis/v8 (IA)/paper/sections/*.tex` (11 files) -- prose revisions, English abstract addition, Chapter 6 expansion. Files `01-introduccion.tex` through `11-aspectos-legales.tex` will be reviewed for AI patterns.
- **Bibliography**: `docs/Tesis/v8 (IA)/Bibliography_base.bib` -- MUST NOT be modified (already correct with 34 entries).
- **LaTeX preamble**: `docs/Tesis/v8 (IA)/paper/preambles/preamble.tex` -- MUST NOT be modified (already correct with biblatex APA7 config and proper `\printbibliography`).
- **PDF output**: `docs/Tesis/v8 (IA)/paper/main.pdf` -- to be created. This becomes the canonical thesis artifact.
- **DOCX output** (optional): `docs/Tesis/v8 (IA)/paper/tesis.docx` -- pandoc-generated secondary format.
- **No impact on**: Software system (backend, frontend, N8N, evaluation framework, CI pipeline). This change is exclusively thesis document editing.
- **Risk**: LaTeX compilation may fail due to missing fonts, package incompatibilities, or unresolved cross-references. The primary compilation strategy (Overleaf free tier) mitigates this by providing a pre-configured TeX environment.
