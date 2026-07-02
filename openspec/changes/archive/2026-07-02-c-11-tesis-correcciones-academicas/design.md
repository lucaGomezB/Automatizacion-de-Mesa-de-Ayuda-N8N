## Context

The thesis document for the "Trabajo Final de Carrera" (UTN FRM, Tecnicatura Universitaria en Programacion) exists in two forms:

1. **LaTeX source** at `docs/Tesis/v8 (IA)/paper/` -- the authoritative version with 54 properly placed citation commands (`\textcite{}`, `\parencite{}`), 34 BibLaTeX entries in `Bibliography_base.bib`, proper math equations, and booktabs-styled tables. This source has never been compiled to PDF.

2. **DOCX** at `docs/Tesis/v8 (IA)/1_Tesis_Mesa_Ayuda_UTN_COMPLETA.docx` -- a conversion artifact with 0 rendered citations, no bibliography section, raw LaTeX math (`$$...$$`), corrupted tables, and ASCII table grids. This is what was evaluated and found deficient.

The project root is a software repository (`Automatizacion-de-Mesa-de-Ayuda-N8N`) with 9 tracked spec capabilities for backend, frontend, N8N workflows, evaluation framework, and CI pipeline. The thesis lives in `docs/Tesis/` and is not part of the software system tracked by openspec.

**Constraints:**
- No Docker available on this Windows machine
- No MiKTeX or XeLaTeX currently installed
- pandoc 3.8 is installed (can convert LaTeX to DOCX, but quality will be moderate)
- Python 3.13.12 with python-docx 1.2.0 is available for verification scripts
- The LaTeX source files (.tex) are the single source of truth for content
- The .bib file and preamble must NOT be modified (already correct)
- The user has authorized AI-assisted (clo-author) prose revision

## Goals / Non-Goals

**Goals:**
- Produce a properly compiled PDF from the existing LaTeX source where all 54 citations render in APA 7th format, the bibliography contains all 34 references, math equations display correctly, and tables are professionally formatted with booktabs styling
- Remove AI-generated writing patterns from the 11 section .tex files, replacing mechanical enumeration, repetitive rhetorical formulas, and uniform sentence structure with varied rhythm and genuine analytical depth
- Expand Chapter 6 (implementacion) from a 57-line component list to a reasoned chapter covering technology choices, N8N flow rationale, integration challenges, and agile process connection
- Add a ~200-250 word English abstract after the Spanish "Resumen" section
- Optionally produce a pandoc-generated DOCX for editable format needs

**Non-Goals:**
- Rewriting the entire thesis from scratch
- Adding new chapters or changing the overall thesis structure
- Modifying the software system (backend, frontend, N8N, evaluation framework, CI)
- Altering the .bib bibliography database or the LaTeX preamble configuration
- Achieving perfect DOCX fidelity from pandoc (this is accepted as lower quality)
- Installing a full TeX distribution as the primary strategy (Overleaf is preferred)
- Translator-level English abstract quality (acceptable academic English, not native-proofed)

## Decisions

### D1: LaTeX as single source of truth; PDF as canonical output

**Choice**: Use the existing LaTeX source at `docs/Tesis/v8 (IA)/paper/` as the authoritative thesis representation. Generate a compiled PDF (`main.pdf`) as the canonical deliverable format.

**Rationale**: The LaTeX source already has correct citations, bibliography, math, and table markup. The DOCX is a broken conversion artifact. Fixing the DOCX would require reverse-engineering ~54 citation insertions and rebuilding tables from scratch -- error-prone and wasteful when the source is already correct. The PDF format is the standard for academic thesis submission and rendering fidelity is controlled by the TeX engine, not by a word processor converter.

**Alternatives considered**:
- *Fix the DOCX directly*: Rejected because it requires manually inserting 54 citations, rebuilding bibliography, fixing equation rendering, and recreating 5 tables. Equivalent to redoing the entire formatting from scratch with no guarantee of correctness.
- *Generate DOCX as primary, PDF as secondary*: Rejected because pandoc LaTeX-to-DOCX conversion loses citation formatting fidelity and table styling. PDF must be the gold standard.

### D2: Overleaf as primary compilation environment; local TeX installation as fallback

**Choice**: Upload the LaTeX project to Overleaf (free tier) for PDF compilation. If Overleaf is unavailable, install MiKTeX locally and run `latexmk -xelatex`.

**Rationale**: Overleaf provides a pre-configured TeX Live environment with all standard packages (biblatex, biblatex-apa, booktabs, xelatex), eliminating package dependency resolution. It provides immediate compilation feedback with error logging. The free tier is sufficient for a ~60-page thesis. Local MiKTeX installation is a viable fallback but introduces download time (~2-4 GB) and potential package incompatibility debugging.

**Alternatives considered**:
- *pandoc --pdf-engine=xelatex*: Rejected because pandoc native PDF output does not support the full LaTeX preamble (custom styles, biblatex-apa configuration, XeLaTeX fontspec). It would require significant preamble rewriting.
- *Docker with texlive image*: Rejected because Docker is not available on this machine.

### D3: Chapter-by-chapter prose revision with clo-author and human review gates

**Choice**: Revise each `.tex` file independently, applying a consistent set of anti-pattern rules (see D4). Each chapter's revision is a discrete task. A human review gate follows each revision before the next chapter proceeds.

**Rationale**: The 11 section files vary in length and defect density. Chapter 6 (~57 lines) and Chapter 9 (mechanical enumeration) need the most work. Batch revision would obscure which change caused which effect. Per-chapter revision with review gates prevents cascading errors and allows the human reviewer to calibrate expectations after seeing the first revised chapter.

**Alternatives considered**:
- *Single-pass global find/replace*: Rejected because AI patterns are context-dependent. Mechanical word substitution ("conviene reconocer explicitamente" -> shorter equivalent) works but deeper issues (sentence rhythm, analytical depth) require per-paragraph judgment.
- *Rewrite everything from scratch*: Rejected per Non-Goals. The existing thesis structure and core content are sound; only the AI-authored surface patterns need correction.

### D4: Anti-pattern catalog for AI writing detection

**Choice**: Apply the following anti-pattern rules during prose revision:

| Pattern | Example | Fix Strategy |
|---------|---------|-------------|
| Mechanical enumeration | "En relacion con el primer objetivo... En relacion con el segundo..." | Restructure as flowing narrative linking objectives to findings |
| Repetitive rhetorical formulas | "conviene reconocer explicitamente", "resulta pertinente destacar", "es dable senalar" | Replace with direct, concise statements; vary opening phrases |
| Uniform sentence length | Paragraphs of 4+ subordinated clauses all of similar length | Vary rhythm: mix short declarative sentences with longer analytical ones |
| Shallow analysis | "Los resultados muestran que el sistema funciona correctamente" | Interpret: WHY it works, what constraints emerged, what surprised the author |
| Ghost enumeration | "En primer lugar... en segundo lugar... por ultimo..." appearing in every paragraph | Reserve enumeration for genuinely ordered content; use narrative transitions elsewhere |

### D5: Citation verification via cross-reference script

**Choice**: Write a Python verification script that extracts all `\cite{}`, `\textcite{}`, and `\parencite{}` keys from the 11 section files and cross-references against all `@` entry keys in `Bibliography_base.bib`. Flag any orphan citations or unused bibliography entries.

**Rationale**: Manual verification of 54 citations against 34 bibliography entries is error-prone. A script provides deterministic, repeatable verification that survives future thesis edits.

**Alternatives considered**: Manual grep + visual inspection. Rejected as not repeatable.

## Risks / Trade-offs

- **[R1] LaTeX compilation fails on Overleaf**: Missing packages, font errors, or encoding issues prevent successful PDF generation.
  - **Mitigation**: Overleaf shows compilation errors inline. Debug cycle: check .log file, verify preamble loads required packages, test with a minimal .tex file first, escalate to MiKTeX local install if Overleaf-specific issues arise.
  - **Likelihood**: Low (the preamble already has `\usepackage` declarations for all required packages).

- **[R2] XeLaTeX font not found**: The preamble may reference a font (e.g., via `\setmainfont`) that is not available on Overleaf or MiKTeX.
  - **Mitigation**: Replace with a universally available equivalent (e.g., Latin Modern, TeX Gyre Termes) that matches the UTN formatting requirements. Verify font substitution is visually acceptable.

- **[R3] Prose revision introduces factual errors**: Changing wording unintentionally alters the meaning of a technical claim (e.g., classifier F1 score, N8N node count, Scrumban iteration details).
  - **Mitigation**: All technical numbers, measurements, and claims must be preserved exactly. Prose changes are stylistic only. Each revised chapter must be diffed against the original and reviewed for unintended semantic changes.

- **[R4] English abstract quality is substandard**: ~200-250 words written by AI may contain unnatural phrasing, false cognates, or grammatical errors that would embarrass the thesis.
  - **Mitigation**: The abstract must accurately reflect the Spanish original (not be a translation of it -- it can be a summary of the same content in different words). Accept that academic English from an AI is adequate for a "Tecnicatura" level but will not pass native-speaker review. Flag this as an acceptable quality tier.

- **[R5] pandoc DOCX conversion loses formatting**: Tables become misaligned, citation formatting degrades, LaTeX custom commands break.
  - **Mitigation**: This is accepted as a known limitation. The DOCX is a secondary format. The canonical artifact is PDF. The DOCX header will include a note: "Generated from LaTeX source via pandoc. For the authoritative version, refer to main.pdf."

## Open Questions

1. **Font**: What font does the UTN FRM thesis format require? If a specific font is mandated, it may need to be downloaded/installed. Default: TeX Gyre Termes (Times New Roman equivalent) unless otherwise specified.
2. **Overleaf account**: Does the user have an Overleaf account, or do we need to create a free-tier account? Can the user provide credentials or handle the upload manually?
3. **Reviewer availability**: Who will perform the human review gate after each chapter revision? If the user is the sole reviewer, establish a lightweight review protocol (diff check + one-pass read).
