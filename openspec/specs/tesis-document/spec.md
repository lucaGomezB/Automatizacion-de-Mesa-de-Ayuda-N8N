## ADDED Requirements

### Requirement: Thesis PDF compilation

The thesis document SHALL compile from LaTeX source to PDF via XeLaTeX without fatal errors. The compilation SHALL produce a single `main.pdf` file at `docs/Tesis/v8 (IA)/paper/main.pdf`.

#### Scenario: Successful compilation
- **WHEN** the LaTeX project is compiled with `latexmk -xelatex main.tex` (or equivalent on Overleaf)
- **THEN** a PDF file is produced without fatal compilation errors
- **AND** the PDF contains all pages from the 11 section files in correct order

#### Scenario: Compilation failure recovery
- **WHEN** a compilation error occurs (missing package, undefined reference, font not found)
- **THEN** the error is diagnosed from the .log file
- **AND** the fix is applied to either the preamble or the affected .tex file
- **AND** recompilation succeeds

---

### Requirement: Citation rendering

All citation commands in the 11 section files SHALL render correctly in the compiled PDF. Every `\textcite{}` and `\parencite{}` command SHALL produce a properly formatted in-text citation in APA 7th edition style. Every cited reference SHALL appear in the final bibliography section.

#### Scenario: In-text citations render
- **WHEN** the PDF is opened and any page with a citation command in the source is inspected
- **THEN** the citation displays as APA 7th formatted text (e.g., "Author (Year)" for `\textcite`, "(Author, Year)" for `\parencite`)
- **AND** no raw LaTeX citation commands are visible in the rendered text

#### Scenario: Bibliography is complete
- **WHEN** the bibliography section at the end of the PDF is inspected
- **THEN** it contains exactly 33 entries matching all references declared in `Bibliography_base.bib`
- **AND** each entry is formatted in APA 7th style

#### Scenario: Citation-bibliography cross-reference integrity
- **WHEN** a verification script cross-references all `\cite{}`, `\textcite{}`, and `\parencite{}` keys against `Bibliography_base.bib`
- **THEN** zero orphan citations are found (every citation key exists as a `@` entry in the .bib file)
- **AND** zero unused bibliography entries exist (every .bib entry is cited at least once in the text)
- **AND** the total reference count is exactly 33
- **AND** all cited references are verifiable in at least one academic database (Google Scholar, Crossref, Scopus, or equivalent)

---

### Requirement: Math equation rendering

All LaTeX math environments (`$$...$$`, `$...$`, `\begin{equation}...\end{equation}`) in the source SHALL render as properly typeset mathematical expressions in the PDF.

#### Scenario: Display math equations render correctly
- **WHEN** any page containing a `$$...$$` or `\begin{equation}` block in the source is inspected in the PDF
- **THEN** the equation is rendered with proper mathematical typography (operators, fractions, summations)
- **AND** no raw `$$` or LaTeX math commands are visible in the rendered text

#### Scenario: Inline math renders correctly
- **WHEN** any paragraph containing `$...$` inline math in the source is inspected in the PDF
- **THEN** the math expression is rendered inline with the surrounding text
- **AND** the expression uses proper mathematical typography consistent with display equations

---

### Requirement: Table formatting

All tables defined in the LaTeX source SHALL render in the PDF with professional booktabs styling. Every table SHALL contain the correct number of rows and columns matching the source definition.

#### Scenario: Tables render with booktabs styling
- **WHEN** any page containing a `\begin{table}` environment in the source is inspected in the PDF
- **THEN** the table uses horizontal rules with proper booktabs spacing (`\toprule`, `\midrule`, `\bottomrule`)
- **AND** no ASCII grid characters or raw LaTeX table commands are visible

#### Scenario: Table structural integrity
- **WHEN** the row count of each rendered table is compared to its source definition
- **THEN** every table has at least one data row (no zero-row tables)
- **AND** column alignment matches the source declaration

---

### Requirement: AI writing pattern removal

The thesis prose across all 11 section files SHALL be revised to eliminate AI-generated writing patterns. The revision SHALL NOT alter technical claims, numerical data, or factual content.

#### Scenario: Mechanical enumeration removed from conclusions
- **WHEN** reading Chapter 9 (conclusiones)
- **THEN** the text does NOT contain sequential phrases like "En relacion con el primer objetivo especifico... En relacion con el segundo..."
- **AND** the relationship between objectives and findings is expressed through flowing narrative rather than numbered enumeration

#### Scenario: Repetitive rhetorical formulas eliminated
- **WHEN** reading any chapter
- **THEN** phrases like "conviene reconocer explicitamente", "resulta pertinente destacar", and "es dable senalar" do NOT appear more than once in the entire thesis
- **AND** opening phrases across paragraphs exhibit variety in structure and vocabulary

#### Scenario: Sentence rhythm varies
- **WHEN** analyzing sentence length distribution across a chapter
- **THEN** the text contains a mix of short declarative sentences (under 20 words), medium analytical sentences (20-35 words), and longer subordinated sentences (35+ words)
- **AND** no paragraph consists exclusively of long subordinated sentences

#### Scenario: Analytical depth beyond description
- **WHEN** reading any results or discussion section
- **THEN** the text goes beyond describing what happened
- **AND** includes interpretation of WHY results occurred, what constraints emerged, what tradeoffs were encountered, and what surprised the author

#### Scenario: Technical claims preserved
- **WHEN** comparing the revised text against the original source
- **THEN** all numerical values (F1 scores, node counts, iteration numbers, percentages) are identical
- **AND** all technical claims about the software system remain factually accurate

---

### Requirement: Chapter 6 (implementation) depth

Chapter 6 (`06-implementacion.tex`) SHALL be expanded beyond its current 57-line component enumeration to provide reasoned justification for technology choices, N8N flow design, and integration challenges.

#### Scenario: Technology choices justified
- **WHEN** reading Chapter 6
- **THEN** the choice of FastAPI is explained with reference to at least one alternative considered (e.g., Flask, Django REST)
- **AND** the rationale for each major technology selection is stated explicitly

#### Scenario: N8N flow design explained
- **WHEN** reading the N8N section of Chapter 6
- **THEN** the 12-node flow design is described with rationale for node selection and arrangement
- **AND** the integration with the FastAPI backend via webhooks is explained

#### Scenario: Agile process connection
- **WHEN** reading Chapter 6
- **THEN** the implementation is connected to the Scrumban iterations described in Chapter 4
- **AND** at least one specific example ties an iteration to its resulting implementation artifact

#### Scenario: Integration challenges addressed
- **WHEN** reading Chapter 6
- **THEN** at least one integration challenge encountered during implementation is described
- **AND** the solution approach for that challenge is explained

---

### Requirement: English abstract

The thesis SHALL contain an English abstract section immediately after the Spanish "Resumen" in `00-resumen.tex`. The abstract SHALL be approximately 200-250 words and accurately summarize the thesis content.

#### Scenario: English abstract present and positioned
- **WHEN** opening the compiled PDF
- **THEN** an "Abstract" section appears after the Spanish "Resumen" section
- **AND** the abstract title is formatted at the same heading level as "Resumen"

#### Scenario: English abstract length
- **WHEN** counting the words in the English abstract
- **THEN** the word count is between 180 and 280 words

#### Scenario: English abstract content accuracy
- **WHEN** reading the English abstract
- **THEN** it covers the thesis problem, methodology, key results, and conclusions
- **AND** all technical terms are consistent with the Spanish text (same classifier names, tool names, category strings)

---

### Requirement: Secondary DOCX generation

If TIER 3 is executed, a secondary DOCX file SHALL be generated from the LaTeX source via pandoc with citation processing. The DOCX quality SHALL be accepted as lower than the canonical PDF.

#### Scenario: pandoc DOCX generation succeeds
- **WHEN** `pandoc main.tex --bibliography=../Bibliography_base.bib --citeproc -o tesis.docx` is executed
- **THEN** a `tesis.docx` file is produced without fatal errors
- **AND** the DOCX contains rendered citations and a bibliography section

#### Scenario: DOCX limitations documented
- **WHEN** the DOCX is delivered
- **THEN** a note accompanies it stating it was generated from LaTeX source via pandoc
- **AND** the canonical PDF (`main.pdf`) is identified as the authoritative version

---

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

---

### Requirement: Discussion chapter -- gradual change management

Section 8.4 "Implicancias practicas" of the Discussion chapter (08-discusion.tex) SHALL include a paragraph acknowledging the sociotechnical dimension of organizational adoption. The paragraph SHALL be positioned after the economic analysis and before section 8.5.

#### Scenario: Gradual change paragraph present
- **WHEN** reading section 8.4 of 08-discusion.tex
- **THEN** a fourth paragraph exists after the economic analysis paragraph
- **AND** the paragraph addresses organizational adoption challenges
- **AND** the paragraph references gradual rollout strategies (pilot group, progressive expansion, targeted training)

#### Scenario: Gradual change paragraph framed as practitioner knowledge
- **WHEN** reading the new paragraph
- **THEN** claims are framed as experiential observation (e.g., "la experiencia... sugiere", "se observa que")
- **AND** the paragraph does NOT contain any `\cite{}`, `\textcite{}`, or `\parencite{}` commands
- **AND** the paragraph does NOT use phrases like "la literatura documenta" or "estudios demuestran"

#### Scenario: No existing content altered
- **WHEN** comparing the modified 08-discusion.tex against the version prior to this change
- **THEN** all pre-existing paragraphs, headings, and blank lines are preserved in their original form
- **AND** the only difference is the insertion of the new paragraph after the economic analysis paragraph

---

### Requirement: Future work -- organizational analytics expansion

Section 10.3 "Panel de monitoreo en tiempo real" of the Recommendations chapter (10-recomendaciones.tex) SHALL be expanded with a second paragraph about organizational analytics derived from accumulated incident data.

#### Scenario: Analytics paragraph present
- **WHEN** reading section 10.3 of 10-recomendaciones.tex
- **THEN** the section contains at least two paragraphs
- **AND** the second paragraph discusses using incident data for business intelligence beyond system health monitoring
- **AND** the paragraph mentions ETL pipelines, trend analysis, or executive-level dashboards

#### Scenario: Analytics paragraph properly framed as recommendation
- **WHEN** reading the new paragraph
- **THEN** it uses future-oriented or conditional language consistent with Chapter 10 ("habilita", "es posible", "transforma")
- **AND** it does NOT introduce new empirical claims or unsupported quantitative assertions
- **AND** it does NOT contain fabricated references

#### Scenario: Existing monitoring paragraph preserved
- **WHEN** reading the first paragraph of section 10.3
- **THEN** it still discusses Prometheus, Grafana, and system-level observability metrics
- **AND** no text from the original paragraph has been removed or altered

---

### Requirement: Future work -- knowledge base for self-service resolution

The Recommendations chapter (10-recomendaciones.tex) SHALL include a new subsection 10.7 "Base de conocimientos para resolucion automatica" proposing a knowledge base for automatic resolution of simple incidents.

#### Scenario: New subsection 10.7 exists
- **WHEN** reading 10-recomendaciones.tex
- **THEN** a `\subsection{Base de conocimientos para resolucion automatica}` exists after section 10.6
- **AND** the subsection contains at least two paragraphs

#### Scenario: Knowledge base concept explained
- **WHEN** reading the new subsection
- **THEN** the first paragraph explains that the current system focuses on classification/routing and that self-service resolution is proposed as future work
- **AND** the subsection describes how a knowledge base would match incident patterns to documented solutions
- **AND** the subsection mentions simple incident types (password resets, session restarts, email configuration)

#### Scenario: Knowledge base connects to existing sections
- **WHEN** reading the new subsection
- **THEN** it references Section 10.4 (active learning) as a mechanism to feed the knowledge base from resolved cases
- **AND** it references Section 10.6 (open-source LLM evaluation) as enabling technology for generating structured KB responses

#### Scenario: No fabricated references in knowledge base subsection
- **WHEN** reading the new subsection 10.7
- **THEN** it does NOT contain any `\cite{}`, `\textcite{}`, or `\parencite{}` commands
- **AND** no bibliography changes are required for this subsection

#### Scenario: Existing sections preserved
- **WHEN** comparing the modified 10-recomendaciones.tex against the version prior to this change
- **THEN** sections 10.1 through 10.6 are unchanged in content
- **AND** no text has been removed from any existing section
