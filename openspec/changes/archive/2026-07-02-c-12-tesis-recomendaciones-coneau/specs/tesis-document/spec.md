## ADDED Requirements

### Requirement: Chapter numbering consistency

The thesis LaTeX project SHALL use consistent chapter numbering where the filename prefix matches the actual chapter position in the document. The final chapter SHALL be numbered 12 (Anexos), not 13.

#### Scenario: Annex chapter file is numbered 12
- **WHEN** listing the section files in `paper/sections/`
- **THEN** the annex file exists as `12-anexos.tex`
- **AND** no file named `13-anexos.tex` exists

#### Scenario: main.tex references the correct annex file
- **WHEN** reading `paper/main.tex`
- **THEN** the `\input` command for the annex chapter references `sections/12-anexos`
- **AND** no `\input` command references `sections/13-anexos`

---

### Requirement: Bibliographic reference quality

The thesis bibliography SHALL use the most authoritative and specific reference for each claim. Weak or generic references SHALL be replaced with domain-appropriate sources.

#### Scenario: ITSM degradation claims use Galup2009
- **WHEN** reading any paragraph in 01-introduccion.tex or 02-marco-teorico.tex that discusses ITSM process degradation
- **THEN** the citation uses Galup2009 (not Pressman2020)
- **AND** Galup2009 exists as a verified entry in Bibliography_base.bib

#### Scenario: Scrumban methodology uses Ladas2009
- **WHEN** reading any paragraph in 04-marco-metodologico.tex or 06-implementacion.tex that discusses the Scrumban methodology choice
- **THEN** the citation uses Ladas2009 (not Crispin2009)
- **AND** Ladas2009 exists as a verified entry in Bibliography_base.bib with author Ladas, Corey, year 2009, publisher Modus Cooperandi Press

#### Scenario: Crispin2009 preserved for testing pyramid
- **WHEN** reading 06-implementacion.tex where the testing pyramid or testing methodology is discussed
- **THEN** Crispin2009 is still cited for those testing-specific claims
- **AND** Crispin2009 remains in Bibliography_base.bib

---

### Requirement: Reference authenticity

All references cited in the thesis SHALL be verifiable in at least one academic database (Google Scholar, Crossref, Scopus, or equivalent). No fabricated or hallucinated references SHALL remain in the document.

#### Scenario: Fabricated references removed from bibliography
- **WHEN** inspecting Bibliography_base.bib
- **THEN** no entry exists for Karchhud2024
- **AND** no entry exists for Mehdi2023

#### Scenario: Fabricated reference citations removed from text
- **WHEN** searching all .tex files for "\cite{Karchhud2024}", "\textcite{Karchhud2024}", "\parencite{Karchhud2024}"
- **THEN** zero matches are found
- **AND** when searching all .tex files for "\cite{Mehdi2023}", "\textcite{Mehdi2023}", "\parencite{Mehdi2023}"
- **THEN** zero matches are found

#### Scenario: Unsupported quantitative claims removed
- **WHEN** reading any .tex file
- **THEN** no paragraph contains unsupported quantitative claims previously attributed to Karchhud2024 or Mehdi2023 (e.g., "40-60%", "35%", "60%" used as external baselines)
- **AND** the thesis's own empirical results are used where quantitative evidence is needed

#### Scenario: Affected paragraphs flow naturally
- **WHEN** reading paragraphs that previously contained Karchhud2024 or Mehdi2023 citations
- **THEN** the text reads as coherent academic prose without abrupt jumps or orphaned connectors
- **AND** no paragraph ends with an incomplete sentence or dangling clause

---

### Requirement: Discussion chapter CV argument accuracy

The discussion chapter (08-discusion.tex) SHALL present statistical arguments that are mathematically accurate and not misleading. Claims about predictability SHALL be supported by the data presented.

#### Scenario: Misleading CV comparison removed
- **WHEN** reading 08-discusion.tex
- **THEN** the text does NOT claim that automated processing is "sustancialmente mas predecible" based on CV comparison
- **AND** the text does NOT directly compare the automated CV (22.5%) against the manual CV (23.4%) as evidence of a substantial difference

#### Scenario: Absolute range compression argument present
- **WHEN** reading the discussion of processing time variability in 08-discusion.tex
- **THEN** the text discusses the absolute time ranges: manual 11-31s vs automated 96-289s
- **AND** the text explains that the wider automated range reflects genuine task complexity variation (simple classification vs full pipeline with external API calls)
- **AND** the text notes that manual processing shows a tight range because all manual tasks are uniform form-filling operations

---

### Requirement: Ethics chapter operator debriefing

The ethics/legal chapter (11-aspectos-legales.tex) SHALL document the post-hoc debriefing process for operators whose task execution times were measured during data collection.

#### Scenario: Debriefing paragraph present
- **WHEN** reading 11-aspectos-legales.tex
- **THEN** a paragraph exists describing the debriefing of operators
- **AND** the paragraph states that operators were informed after data collection was complete

#### Scenario: Debriefing content completeness
- **WHEN** reading the debriefing paragraph
- **THEN** it explains that the purpose of the time measurement was described to operators
- **AND** it states that operators were given the opportunity to withdraw their data
- **AND** it notes whether any operator chose to withdraw (or that none did)

## MODIFIED Requirements

### Requirement: Bibliography is complete

The bibliography section at the end of the PDF SHALL contain exactly 32 entries matching all references declared in Bibliography_base.bib after the removal of Karchhud2024 and Mehdi2023 and the addition of Ladas2009.

#### Scenario: Bibliography is complete
- **WHEN** the bibliography section at the end of the PDF is inspected
- **THEN** it contains exactly 32 entries matching all references declared in `Bibliography_base.bib`
- **AND** each entry is formatted in APA 7th style

### Requirement: Citation-bibliography cross-reference integrity

A verification script SHALL confirm that all citation keys in the .tex files have corresponding entries in Bibliography_base.bib and that all .bib entries are cited at least once. After reference changes, the script SHALL report 32 references, zero orphan citations, and zero unused bibliography entries.

#### Scenario: Citation-bibliography cross-reference integrity
- **WHEN** a verification script cross-references all `\cite{}`, `\textcite{}`, and `\parencite{}` keys against `Bibliography_base.bib`
- **THEN** zero orphan citations are found (every citation key exists as a `@` entry in the .bib file)
- **AND** zero unused bibliography entries exist (every .bib entry is cited at least once in the text)
- **AND** the total reference count is exactly 32
