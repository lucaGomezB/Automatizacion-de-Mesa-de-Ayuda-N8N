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
- **THEN** it contains exactly 34 entries matching all references declared in `Bibliography_base.bib`
- **AND** each entry is formatted in APA 7th style

#### Scenario: Citation-bibliography cross-reference integrity
- **WHEN** a verification script cross-references all `\cite{}`, `\textcite{}`, and `\parencite{}` keys against `Bibliography_base.bib`
- **THEN** zero orphan citations are found (every citation key exists as a `@` entry in the .bib file)
- **AND** zero unused bibliography entries exist (every .bib entry is cited at least once in the text)

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
