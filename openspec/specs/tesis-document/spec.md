# tesis-document Specification

## Purpose

Esta especificación define los criterios de calidad del documento de tesis en LaTeX: compilación a PDF, renderizado de citas, ecuaciones y tablas, eliminación de patrones de escritura generados por IA, profundidad de capítulos y consistencia de referencias.

## Requirements

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
- **THEN** it contains exactly the set of entries declared in `Bibliography_base.bib` (the count grows after c-78 and is not fixed at 33)
- **AND** each entry is formatted in APA 7th style

#### Scenario: Citation-bibliography cross-reference integrity
- **WHEN** a verification script cross-references all `\cite{}`, `\textcite{}`, and `\parencite{}` keys against `Bibliography_base.bib`
- **THEN** zero orphan citations are found (every citation key exists as a `@` entry in the .bib file)
- **AND** zero unused bibliography entries exist (every .bib entry is cited at least once in the text)
- **AND** all cited references are verifiable in at least one academic database (Google Scholar, Crossref, Scopus, or equivalent)

#### Scenario: Orphan-citation status documented
- **WHEN** the change is applied
- **THEN** the state of orphan citations and unused entries is documented in the tasks with the exact verification command and its output
- **AND** the two orphan citations of the audited v7 version are identified explicitly as Karchhud et al. (2024) and Mehdi et al. (2023), both VERIFIED AS FABRICATED (no matching article or author in Crossref/OpenAlex), already removed between v7 and v9
- **AND** the document MUST NOT reintroduce either fabricated reference
- **AND** the two claims those citations used to support (the "88 % a 94 %" range in `08-discusion.tex:20` and the AI-adoption claim in `03-estado-del-arte.tex:12`) are re-cited with real sources or removed/reformulated

#### Scenario: Every citation resolves by DOI or landing page
- **WHEN** each entry of `Bibliography_base.bib` is checked against DOI resolution or its publisher/ACL landing page
- **THEN** every citation resolves to a real publication
- **AND** any citation that cannot be resolved is removed or replaced (guard against the fabrication cluster identified in v7)

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

All tables defined in the LaTeX source SHALL render in the PDF with professional booktabs styling. Every table SHALL contain the correct number of rows and columns matching the source definition. Table composition SHALL be uniform across the document: every table SHALL declare its font size consistently and SHALL set prose columns to ragged-right so that text wraps without excessive inter-word spacing.

#### Scenario: Tables render with booktabs styling
- **WHEN** any page containing a `\begin{table}` environment in the source is inspected in the PDF
- **THEN** the table uses horizontal rules with proper booktabs spacing (`\toprule`, `\midrule`, `\bottomrule`)
- **AND** no ASCII grid characters or raw LaTeX table commands are visible

#### Scenario: Table structural integrity
- **WHEN** the row count of each rendered table is compared to its source definition
- **THEN** every table has at least one data row (no zero-row tables)
- **AND** column alignment matches the source declaration

#### Scenario: Uniform font size across tables
- **WHEN** the font declaration of all 9 tables in the thesis source is compared
- **THEN** every table either declares `\small` or explicitly declares its size following the same convention
- **AND** no table is left without a font-size declaration while its peers declare `\small`

#### Scenario: Prose columns are ragged-right
- **WHEN** the column specification of a table whose cells contain full sentences is inspected
- **THEN** the prose column uses `>{\raggedright\arraybackslash}p{...}` (or equivalent)
- **AND** no fixed-width prose column is left fully justified

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

The thesis SHALL contain an English abstract section immediately after the Spanish "Resumen" in `00-resumen.tex`. The abstract SHALL be at most 250 words, SHALL accurately summarize the thesis content, and SHALL be consistent with the reduced Spanish "Resumen" (same key figures, same category strings, same declared state of the principal hypothesis).

#### Scenario: English abstract present and positioned
- **WHEN** opening the compiled PDF
- **THEN** an "Abstract" section appears after the Spanish "Resumen" section
- **AND** the abstract title is formatted at the same heading level as "Resumen"

#### Scenario: English abstract length
- **WHEN** counting the words in the English abstract (prose body, excluding LaTeX commands and the keywords line)
- **THEN** the word count is at most 250 words

#### Scenario: English abstract content accuracy
- **WHEN** reading the English abstract
- **THEN** it covers the thesis problem, methodology, key results, and conclusions
- **AND** all technical terms are consistent with the Spanish text (same classifier names, tool names, category strings)
- **AND** the key figures match those of the reduced Spanish "Resumen" (200 paired cases, 61.6~s to 17.76~s, 71.2~\% reduction, \(W = 363\), \(r = 0.9639\), 73.5~\% accuracy, macro-F1 0.5207, Cohen's Kappa 0.87)

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

### Requirement: Alineacion de la tesis con el corpus real de evaluacion

La tesis SHALL reportar los resultados experimentales sobre el corpus real de 200
casos pseudonimizados (`data/corpus_evaluacion_pseudonimizado.json`), no sobre el
corpus sintetico descartado en C-27. El Capitulo 7 SHALL reportar: la distribucion
por sector del corpus real (Sistemas 16, Soporte Tecnico Hardware 85, Soporte
Tecnico Software 67, Seguridad Informatica 31, Bases de Datos 1), los canales de
origen (correo 66, formulario web 53, llamada telefonica 81), la exactitud estricta
73,5 % (147/200), macro-F1 0,5207, micro-F1 0,6654, subset accuracy 0,43, Hamming
loss 0,3586, las etapas deterministic 131 / Gemini 69, y la matriz de confusion 5x5
completa. El vocabulario de sectores reportado SHALL ser el conjunto canonico de
cinco categorias, SIN la categoria retirada "Operaciones". La tesis SHALL NOT
reportar como vigentes los valores del corpus sintetico (3 clases, distribucion
82/64/54, exactitud 92 %, F1 macro 0,919).

#### Scenario: Capitulo 7 reporta las metricas reales

- **WHEN** se lee el Capitulo 7 (Resultados) del PDF compilado
- **THEN** la exactitud reportada es 73,5 % (147/200) y el macro-F1 es 0,5207
- **AND** la matriz de confusion reportada es 5x5 sobre las cinco categorias canonicas

#### Scenario: Categoria retirada ausente

- **WHEN** se busca "Operaciones" como sector en cualquier archivo `.tex` y en el PDF compilado
- **THEN** no aparece como categoria responsable, ni en la distribucion, ni en la matriz de confusion

#### Scenario: Distribucion por sector coincide con el reporte de evaluacion

- **WHEN** se compara la distribucion por sector reportada en la tesis con `evaluation/report.md`
- **THEN** coinciden en las cinco categorias (16/85/67/31/1)
- **AND** los canales de origen reportados coinciden (66/53/81)

### Requirement: Divulgacion del procedimiento de medicion de tiempos y analisis de sensibilidad

La tesis SHALL declarar que `tiempo_manual_s` es una medicion real en vivo,
registrada durante la atencion de usuarios con redondeo hacia arriba (sesgo
sistematico de medicion), y SHALL reportar el tiempo manual como cota superior
junto con una cota inferior conservadora de sensibilidad. El claim primario de
reduccion SHALL apoyarse en la mediana y en estadisticos de rango, no solo en la
media. La prueba de Wilcoxon SHALL reportar el valor real con correccion por
empates (W=363, T+=19737, T−=363, p=3,08e-32, r=0,9639) y SHALL declarar el
numero real de pares en que el flujo automatizado no fue mas rapido (12 de 200),
sin afirmar "W=0" ni "sin excepcion".

#### Scenario: Redondeo declarado y sensibilidad reportada

- **WHEN** se leen el Capitulo 4 (metodologia) y el Capitulo 7 (resultados)
- **THEN** se declara el redondeo al alza de la medicion manual
- **AND** se reporta la reduccion como cota superior (71,2 %) junto a sus cotas inferiores conservadoras (68,6 % al descontar 5 s y 65,6 % al descontar 10 s a cada medicion manual)

#### Scenario: Estadistico de Wilcoxon real

- **WHEN** se lee la comparacion de tiempos de registro
- **THEN** el estadistico reportado es W=363 con T+=19737, T−=363, p=3,08e-32 y r=0,9639
- **AND** el texto no afirma W=0 ni "sin una sola excepcion"

#### Scenario: Pares invertidos declarados

- **WHEN** se leen los resultados de tiempos
- **THEN** se declara que en 12 de 200 pares el flujo automatizado no fue mas rapido que el manual

### Requirement: Consistencia de anexos, documentacion de soporte y PDF

La documentacion de soporte SHALL ser consistente con el corpus real:
`docs/anexo_f_corpus.md` SHALL declarar que la evaluacion se realiza sobre el
corpus real pseudonimizado y versionado; `evaluation/README.md` y
`evaluation/data/README.md` SHALL indicar que el corpus esta versionado en su
forma pseudonimizada; el `README.md` raiz SHALL referenciar
`docs/anexo_h_prompt_gemini.md`; y `docs/anexo_h_prompt_gemini.md` SHALL usar la
misma version de modelo que el codigo (`gemini-3.6-flash`). La tesis SHALL
recompilar `docs/Tesis/v9 (IA)/paper/main.pdf` de modo que refleje las
correcciones.

#### Scenario: Anexo H alineado con el codigo

- **WHEN** se leen el titulo y el cuerpo de `docs/anexo_h_prompt_gemini.md`
- **THEN** la version del modelo declarada coincide con `settings.gemini_model` (`gemini-3.6-flash`)
- **AND** no se menciona "Gemini 2.5 Flash"

#### Scenario: Anexo F y READMEs declaran el corpus real versionado

- **WHEN** se leen `docs/anexo_f_corpus.md`, `evaluation/README.md` y `evaluation/data/README.md`
- **THEN** declaran la evaluacion sobre el corpus real pseudonimizado
- **AND** indican que la version pseudonimizada esta versionada en el repositorio

#### Scenario: PDF recompilado

- **WHEN** se compila el proyecto LaTeX con XeLaTeX (`latexmk -xelatex main.tex`)
- **THEN** se produce `main.pdf` sin errores fatales de compilacion
- **AND** el PDF refleja las correcciones (sin la categoria "Operaciones" ni los valores sinteticos)

### Requirement: Trazabilidad del corpus real en el anexo de validacion

El anexo "Corpus de validacion" de la tesis SHALL remitir al corpus real
`data/corpus_evaluacion_pseudonimizado.json` (JSON, pseudonimizado y versionado)
y SHALL NOT declarar que el corpus se conserva como un CSV de siete columnas en
`evaluation/data/`. El anexo SHALL aclarar que la categoria predicha y la
confianza por caso viven en `evaluation/predicciones.json`, no dentro del corpus.
La tesis SHALL NOT afirmar la existencia de un corpus en `evaluation/data/`.

#### Scenario: El anexo apunta al JSON real

- **WHEN** se lee la seccion "Corpus de validacion" del Anexo de la tesis
- **THEN** referencia `data/corpus_evaluacion_pseudonimizado.json` como corpus real
- **AND** no describe un archivo CSV ni un corpus de siete columnas en `evaluation/data/`

#### Scenario: Sin corpus inexistente

- **WHEN** se busca "evaluation/data" o "CSV" como ubicacion del corpus en los `.tex` y en el PDF
- **THEN** no se afirma que el corpus resida alli

### Requirement: Divulgacion de las etapas del pipeline incluida la etapa fallback

La tesis SHALL describir el pipeline de clasificacion como tres etapas en el orden
deterministic -> Gemini -> fallback, y SHALL reportar la distribucion real de casos
por etapa: deterministic 131/200 (65,5 %), Gemini 69/200 (34,5 %) y fallback 0/200.
La tesis SHALL NOT reportar el reparto stale "~62 % / 38 %" ni "seis de cada diez"
como distribucion vigente.

#### Scenario: Distribucion de etapas real

- **WHEN** se leen los capitulos 5.5, 8.1 y 9.1 del PDF compilado
- **THEN** la primera etapa se reporta como 65,5 % y la segunda como 34,5 %
- **AND** no aparece "62 %", "38 %" ni "seis de cada diez" como reparto de etapas

#### Scenario: Etapa fallback documentada

- **WHEN** se describe el pipeline de clasificacion en la tesis
- **THEN** se documenta la etapa fallback (0 casos) y el orden deterministic -> Gemini -> fallback

### Requirement: Consistencia de la ventana temporal y reconciliacion anti-Hawthorne

La tesis SHALL declarar una unica ventana temporal para la recoleccion de datos de
la campana experimental, coherente entre los capitulos 4.2, 4.4, 4.5 y 11.5, y
SHALL NOT presentar simultaneamente un trimestre completo y una corrida de "tres
dias habiles consecutivos" como si fueran la misma ventana sin explicar su
relacion. La afirmacion anti-Hawthorne SHALL reconciliarse con el procedimiento
efectivo (medicion en vivo con conocimiento diferido del operador y `debriefing`),
sin afirmar que el operador ignoraba ser cronometrado durante toda la ventana.

#### Scenario: Ventana temporal unica

- **WHEN** se comparan los capitulos 4.2, 4.4, 4.5 y 11.5
- **THEN** la ventana temporal declarada es una sola y consistente
- **AND** el trimestre y la corrida automatizada se relacionan de forma explicita

#### Scenario: Anti-Hawthorne reconciliado

- **WHEN** se lee la afirmacion sobre el efecto Hawthorne
- **THEN** describe el procedimiento efectivo de medicion y su conocimiento diferido por parte del operador
- **AND** no sostiene que el operador desconocia el cronometraje durante toda la campana

### Requirement: Instrumento unico de medicion manual del tiempo

La tesis SHALL describir el instrumento de medicion manual (`planilla de
cronometraje`) de forma unica y consistente en los capitulos 4.2, 4.6 y 7.3: una
medicion en vivo durante la atencion, cronometrada por el companero de par, con
redondeo hacia arriba. La tesis SHALL NOT describirlo simultaneamente como
"estimados" y "cronometrados", ni como "con exactitud al segundo" y "sin
fracciones". La seccion de reduccion de intervencion humana (7.3) SHALL NOT
derivar la intervencion del flujo automatizado de la planilla del flujo manual.

#### Scenario: Relato unico del instrumento

- **WHEN** se comparan las descripciones de la planilla en 4.2, 4.6 y 7.3
- **THEN** describen el mismo procedimiento de cronometraje en vivo con redondeo al alza
- **AND** no coexisten "estimados" con "cronometrados" ni "exactitud al segundo" con "sin fracciones"

#### Scenario: Intervencion automatizada no derivada del instrumento manual

- **WHEN** se lee la seccion de reduccion de intervencion humana (7.3)
- **THEN** la intervencion del flujo automatizado se sustenta en registros del propio flujo automatizado
- **AND** no se deriva de la planilla de cronometraje del flujo manual

### Requirement: Campana experimental presentada como realizada

La tesis SHALL presentar la campana experimental como ejecutada sobre datos reales
a lo largo del Capitulo 7 y del Anexo de corpus, y SHALL NOT presentarla como
trabajo futuro, pendiente o propuesta.

#### Scenario: Sin lenguaje de trabajo futuro

- **WHEN** se lee el Capitulo 7 y el Anexo de corpus en el PDF compilado
- **THEN** la campana se reporta como realizada con datos reales
- **AND** ningun pasaje la describe como pendiente o futura

### Requirement: Coherencia de los datos en los capitulos 7.2 y 1.6

La tesis SHALL reportar en el Capitulo 7.2 las metricas reales (exactitud 73,5 %,
macro-F1 0,5207, cinco clases) y SHALL corregir en el Capitulo 1.6 la mencion a
"tres sectores (Sistemas, Operaciones y Soporte Tecnico)" por las cinco categorias
canonicas, "Gemini 2.5 Flash" por `gemini-3.6-flash` y revisar la fecha "junio de
2026".

#### Scenario: 7.2 usa metricas reales

- **WHEN** se lee el Capitulo 7.2
- **THEN** reporta exactitud 73,5 %, macro-F1 0,5207 y cinco clases
- **AND** no reporta 92 %, 0,919 ni tres clases

#### Scenario: 1.6 sin tres sectores ni modelo stale

- **WHEN** se lee el Capitulo 1.6 (alcance y delimitaciones)
- **THEN** menciona las cinco categorias canonicas y no "tres sectores" con "Operaciones"
- **AND** el modelo declarado es `gemini-3.6-flash`, no "Gemini 2.5 Flash"

### Requirement: Rigor inferencial del tamaño del efecto

El capítulo de marco metodológico y el de resultados SHALL declarar
explícitamente la convención del estadístico de Wilcoxon empleado, reportar
ambos estadísticos de rango (`T+` y `T−`) y calcular el tamaño del efecto con la
fórmula rank-biserial correcta. El documento MUST NOT presentar `W=0` ni un
tamaño del efecto igual a `1,00` como resultado del corpus real, y MUST declarar
el rango verdadero de la fórmula empleada.

#### Scenario: Convención de W declarada

- **WHEN** se lee la sección de análisis estadístico o de resultados que reporta la prueba de Wilcoxon
- **THEN** el texto enuncia si `W` denota `min(T+, T−)`, `T+` u otro estadístico
- **AND** reporta los valores de `T+` y `T−` además del estadístico de contraste

#### Scenario: Fórmula y rango correctos

- **WHEN** se lee la fórmula del tamaño del efecto
- **THEN** la fórmula es `r = (T+ − T−) / (n(n+1)/2)` (o su equivalente `1 − 4W/(n(n+1))` cuando `W=T−`)
- **AND** el rango declarado es coherente con la fórmula (no `[-1,+1]` como rango universal de `1 − 2W/(n(n+1))`)
- **AND** el valor reportado sobre el corpus real es `0,9639`, no `1,00`

#### Scenario: Sin W=0

- **WHEN** se busca `W = 0` en los archivos de sección
- **THEN** no aparece como resultado de la prueba sobre el corpus real
- **AND** el conteo de pares invertidos (12/200) es consistente con el estadístico reportado

### Requirement: Calibración de la confianza del clasificador

La tesis SHALL reportar la relación entre la confianza devuelta por el
clasificador y su exactitud. El capítulo de resultados MUST incluir al menos la
tabla de contingencia de confianza alta/baja contra acierto/error, y el capítulo
de discusión MUST interpretar su implicancia para el umbral de revisión humana
de 0,70.

#### Scenario: Tabla de contingencia o curva de calibración presente

- **WHEN** se lee el capítulo de resultados
- **THEN** existe una tabla o figura que cruza confianza con acierto/error
- **AND** se reportan al menos la precisión del segmento de confianza `>= 0,70` y la del segmento `< 0,70`

#### Scenario: Discusión de la anti-calibración

- **WHEN** se lee el capítulo de discusión
- **THEN** se reconoce que la precisión del segmento de confianza alta no supera a la del segmento de confianza baja (0,697 vs 0,758)
- **AND** se discute la implicancia de esta anti-calibración para el umbral de revisión humana de 0,70

### Requirement: Aritmética metodológica verificable

Toda proyección numérica del documento (horas-persona liberadas, universo trimestral, tiempos de registro) SHALL ser reproducible a partir de los datos
declarados. Cuando una proyección derive de una multiplicación o división, el
documento MUST mostrar el cálculo explícito (en el cuerpo o en una nota al pie).

#### Scenario: Proyección de horas-persona con cálculo explícito

- **WHEN** se lee cualquier afirmación de horas-persona liberadas por período
- **THEN** se exponen los factores usados (ahorro por incidente × volumen) y el resultado aritmético
- **AND** el valor es compatible con los tiempos y el volumen declarados (no una cifra que implique un ahorro por incidente inexistente)

#### Scenario: Universo trimestral reconciliado con el volumen diario

- **WHEN** se leen las afirmaciones de incidentes por día y por trimestre
- **THEN** el número de días del período está declarado (calendario o laborables)
- **AND** el volumen trimestral es aritméticamente compatible con el volumen diario y los días declarados

#### Scenario: Intervención humana con una única definición o ambas explícitas

- **WHEN** se lee la variable "intervención humana" en la tabla de operacionalización y en los resultados
- **THEN** la definición es una sola (proporción de tiempo o de casos) o se reportan ambas de forma rotulada
- **AND** el valor del capítulo de resultados es consistente con la definición declarada

### Requirement: Rótulo correcto de la dispersión

El documento SHALL rotular correctamente las medidas de dispersión. Cuando
compare desvíos estándar, MUST decir "desvío estándar" (o "desviación típica"),
no "varianza"; cuando compare varianzas, MUST decir "varianza".

#### Scenario: Dispersión rotulada según la medida comparada

- **WHEN** se lee un pasaje que compara la dispersión de los tiempos manual y automatizado
- **THEN** el término empleado coincide con la medida efectivamente comparada (desvío estándar vs varianza)
- **AND** la razón citada es coherente con la medida rotulada

### Requirement: Coherencia técnica entre la tesis y el sistema implementado

El documento SHALL describir el flujo de clasificación, los canales, los
mecanismos de resiliencia y el perímetro de seguridad de forma consistente con
el código y la configuración versionados. Toda funcionalidad declarada como
implementada MUST existir en el repositorio; en su defecto, MUST presentarse como
limitación o trabajo futuro. Los residuos de la alineación tecnológica previa
SHALL quedar cerrados y su registro de decisiones anexado.

#### Scenario: Flujo de clasificación y gate correctos

- **WHEN** se lee la descripción del flujo de orquestación en N8N
- **THEN** el gate de revisión humana se describe como posterior a la clasificación (se clasifica y luego se evalúa la confianza)
- **AND** no se describe ningún modelo de lenguaje actuando en el canal telefónico

#### Scenario: Mecanismos de resiliencia verificados

- **WHEN** el documento declara un mecanismo de reintento, retroceso exponencial o cola de respaldo
- **THEN** el mecanismo existe en `n8n/workflow.json` o en `App/Backend`
- **AND** si no existe, la afirmación se reformula como limitación conocida y trabajo futuro

#### Scenario: Perímetro de seguridad consistente

- **WHEN** el documento declara terminación TLS en el proxy inverso
- **THEN** la versión de protocolo declarada coincide con la configuración de `nginx/nginx.conf`
- **AND** si el proxy no forma parte del despliegue publicado, la afirmación se redacta de forma condicional

#### Scenario: Vocabulario de categorías unificado

- **WHEN** el documento enumera las categorías de clasificación
- **THEN** coincide con los cinco sectores canónicos usados por el prompt y el backend, sin la categoría retirada "Operaciones"
- **AND** no queda ninguna referencia a un prompt con un número distinto de categorías

#### Scenario: Punteros de repositorio válidos

- **WHEN** el documento referencia un tag o un artefacto del repositorio (por ejemplo el corpus o el flujo exportado)
- **THEN** el tag existe en el repositorio (y se registra su hash) o la referencia se corrige al tag/ruta real
- **AND** la ruta apunta a un artefacto existente

#### Scenario: Residuos de C-18 cerrados y log anexado

- **WHEN** se revisan los residuos de la alineación tecnológica (por ejemplo la mención a `IMAP` frente a Outlook/Graph API)
- **THEN** las secciones afectadas quedan alineadas con el estado real
- **AND** el registro de decisiones del dictamen se adjunta como anexo del documento

### Requirement: Trazabilidad de la pregunta de investigación sobre el criterio humano

El documento SHALL garantizar que cada sub-pregunta e hipótesis enunciada tenga
un tratamiento empírico correspondiente, y SHALL explicar el origen y la
relación entre las mediciones preliminares y experimentales de tiempo.

#### Scenario: Sub-pregunta humana medida o retirada

- **WHEN** se lee la pregunta de investigación y sus sub-preguntas
- **THEN** la sub-pregunta sobre la exactitud del clasificador frente al criterio humano está medida sobre el mismo corpus, o ha sido retirada y la hipótesis reformulada
- **AND** no permanece una sub-pregunta sin respuesta empírica en el documento

#### Scenario: Medición preliminar y experimental reconciliadas

- **WHEN** se lee el tiempo de registro manual reportado en la introducción y en los resultados
- **THEN** se explica la relación entre la medición preliminar y la medición experimental
- **AND** se identifica el registro que respalda el tiempo declarado, de modo que la coincidencia no quede sin justificar

### Requirement: Declaración del tiempo automatizado telefónico como cota inferior

El documento SHALL declarar que el tiempo automatizado del canal telefónico se deriva
sumando la duración de la llamada/grabación a la latencia end-to-end, y SHALL explicitar
que esa medición es una COTA INFERIOR de la duración real de la llamada por el tope de
45 s de la grabación. Los tiempos automatizados de los canales web y correo MUST NOT
presentarse como afectados por esta corrección.

#### Scenario: Cota inferior declarada

- **WHEN** se lee el tiempo automatizado del canal telefónico en resultados o en metodología
- **THEN** el texto declara que incorpora la duración de la llamada/grabación
- **AND** declara que es una cota inferior por el tope de 45 s de la grabación

#### Scenario: Web y correo sin cambio

- **WHEN** se leen los tiempos automatizados de web y correo
- **THEN** no se afirma que hayan cambiado por esta corrección
- **AND** la comparación manual/automatizada de esos canales permanece igual

### Requirement: Atribucion correcta de Revina et al. (2020)

El capitulo de estado del arte (seccion 3.3) y el de discusion (seccion 8.2) SHALL describir el aporte de Revina, Buza & Meister (2020) conforme al contenido real del articulo "IT Ticket Classification: The Simpler, the Better" (IEEE Access, vol. 8, pp. 193380-193395, 2020). El documento MUST NOT atribuir a ese articulo el uso de arquitecturas basadas en BERT, una exactitud cercana al 91 % ni la conclusion de que los modelos preentrenados transfieren conocimiento linguistico al dominio de tickets sin ajuste fino.

#### Scenario: Sin BERT ni 91 % atribuidos a Revina
- **WHEN** se lee la seccion 3.3 o la 8.2 en busca de las referencias a Revina et al. (2020)
- **THEN** no se le atribuye uso de BERT ni de modelos preentrenados
- **AND** no se le atribuye una exactitud cercana al 91 %
- **AND** no se le atribuye la conclusion de transferencia de modelos preentrenados al dominio

#### Scenario: Conclusion real de Revina et al. enunciada
- **WHEN** se lee la descripcion de Revina et al. (2020)
- **THEN** el texto enuncia que el articulo concluye que los metodos simples y explicables con un conjunto pequeno de rasgos linguisticos del dominio son competitivos para clasificar tickets de TI
- **AND** el texto enuncia que los embeddings preentrenados pueden rendir peor por el vocabulario especifico del dominio

#### Scenario: Tension incorporada en la discusion
- **WHEN** se lee la seccion 8.2 del capitulo de discusion
- **THEN** la evidencia contraria de Revina et al. se integra como una tension explicita para el enfoque basado en LLM del presente trabajo
- **AND** la discusion explica por que la evidencia contraria fortalece (no debilita) el analisis

### Requirement: Estado del arte modernizado con literatura arbitrada 2023-2026

El estado del arte SHALL incorporar al menos 12 articulos arbitrados publicados entre 2023 y 2026, verificables por DOI, que cubran al menos: (a) clasificacion de tickets y enrutamiento de mesa de servicio de TI con LLM o transformers; (b) evaluacion zero-shot / few-shot de LLM multilingues; (c) desempeno de LLM en espanol o en variantes de espanol de Iberoamerica. Toda afirmacion cuantitativa comparativa del estado del arte y de la discusion SHALL estar respaldada por una cita a una referencia verificable.

#### Scenario: Referencias 2023-2026 incorporadas
- **WHEN** se inspecciona `Bibliography_base.bib`
- **THEN** contiene al menos 12 entradas nuevas arbitradas con ano de publicacion entre 2023 y 2026
- **AND** cada una es verificable por DOI o URL de editorial/ACL Anthology

#### Scenario: Cobertura de las tres lineas tematicas
- **WHEN** se revisan los articulos incorporados
- **THEN** al menos uno aborda clasificacion de tickets o enrutamiento de mesa de servicio con LLM o transformers
- **AND** al menos uno aborda evaluacion zero-shot o few-shot multilingue
- **AND** al menos uno aborda el desempeno de LLM en espanol o en espanol de Iberoamerica

#### Scenario: Afirmaciones sin cita resueltas
- **WHEN** se lee la afirmacion "88 % a 94 % de exactitud" en `08-discusion.tex:20` o la afirmacion sobre literatura few-shot en `03-estado-del-arte.tex:30`
- **THEN** cada afirmacion cita una referencia verificable que la sostiene, o ha sido retirada o reformulada sin el rango numerico
- **AND** no queda ninguna afirmacion cuantitativa comparativa sin respaldo en el estado del arte ni en la discusion

#### Scenario: Brecha de Gemini en espanol declarada
- **WHEN** se presenta la contribucion del trabajo
- **THEN** el documento declara explicitamente que no existe un articulo arbitrado 2023-2026 que evalue Google Gemini especificamente sobre tickets de soporte en espanol
- **AND** no se fabrica ni se atribuye una referencia inexistente para cubrir esa brecha

### Requirement: Fuente de la interpretacion del coeficiente Kappa

El documento SHALL atribuir los rangos interpretativos del coeficiente Kappa a Landis & Koch (1977) y no a Cohen (1960). El valor obtenido (\(\kappa = 0{,}87\)) SHALL rotularse como "casi perfecto" conforme a esos rangos, tanto en la seccion de metodologia (4.4) como en la de amenazas a la validez (4.8).

#### Scenario: Landis y Koch citados para los rangos
- **WHEN** se lee el pasaje que interpreta el valor de Kappa en 4.4 o en 4.8
- **THEN** los rangos de interpretacion se atribuyen a Landis & Koch (1977)
- **AND** existe una entrada `Landis1977_kappa` en `Bibliography_base.bib` con DOI 10.2307/2529310
- **AND** Cohen (1960) permanece citado solo por la definicion del coeficiente

#### Scenario: Rotulo "casi perfecto"
- **WHEN** se lee la interpretacion de \(\kappa = 0{,}87\)
- **THEN** el texto lo rotula como "casi perfecto"
- **AND** no lo rotula como "sustancial"

### Requirement: Higiene de metadatos bibliograficos

Las entradas de `Bibliography_base.bib` SHALL reflejar la autoria, editorial y estado de publicacion reales de cada fuente. Las citas en el texto SHALL seguir el estilo APA 7 para el separador entre autor y ano en las citas con "et al.". El tipo de cada entrada (`@article`, `@book`, `@inproceedings`, `@misc`, `@online`, ...) SHALL corresponder a la naturaleza real de la fuente: una fuente preprint de arXiv MUST NOT tiparse como `@article` con un campo `journal` que la presente como publicacion periodica, y un borrador no publicado MUST NOT tiparse como `@book` con una editorial comercial como si fuera una obra publicada.

#### Scenario: Co-autoria y editorial corregidas

- **WHEN** se inspeccionan las entradas `Stallings2017_computer_security`, `OGC2011_itil` y `Jurafsky2023_speech_language`
- **THEN** `Stallings2017_computer_security` incluye a Lawrie Brown como co-autor
- **AND** `OGC2011_itil` refleja la autoria/editorial real de ITIL Service Operation (2011)
- **AND** `Jurafsky2023_speech_language` indica la editorial/estado correctos (Stanford University o borrador autopublicado), no Pearson

#### Scenario: Coma antes del ano en citas "et al."

- **WHEN** se inspecciona una cita con tres o mas autores en la tesis compilada
- **THEN** el separador entre el autor y el ano es la coma segun APA ("Revina et al., 2020")
- **AND** no aparece la forma sin coma ("Revina et al. 2020") en ninguna cita parentetica

#### Scenario: Nuevas entradas con metadatos completos

- **WHEN** se agregan las referencias de B2 y la entrada de Landis & Koch
- **THEN** cada entrada nueva incluye `author`, `title`, `year` y el campo de publicacion (`journal`, `booktitle` o `publisher`) mas `doi` o `url`
- **AND** las claves siguen la convencion `ApellidoAnio_palabra_clave` del archivo

#### Scenario: Tipado de la fuente preprint de arXiv

- **WHEN** se inspecciona la entrada `Touvron2023_llama2` en `Bibliography_base.bib`
- **THEN** la entrada NO es de tipo `@article` y NO declara `journal = {arXiv preprint}`
- **AND** se tipa como recurso preprint (`@misc`/`@online`) con `eprint`, `archivePrefix = {arXiv}` y `primaryClass` (o `howpublished`)
- **AND** el identificador `arXiv:2307.09288` y su DOI `10.48550/arXiv.2307.09288` se conservan
- **AND** la referencia compilada no presenta "arXiv preprint" como una publicacion periodica

#### Scenario: Tipado del borrador no publicado

- **WHEN** se inspecciona la entrada `Jurafsky2023_speech_language` en `Bibliography_base.bib`
- **THEN** la entrada NO es de tipo `@book` con una editorial comercial
- **AND** se tipa como manuscrito/borrador no publicado (`@misc`/`@unpublished`)
- **AND** el estado (Stanford University, borrador de la 3ra edicion) queda declarado en el campo de publicacion o en `note`

### Requirement: Plazo de conservacion declarado y consistente

La seccion 11.2 del Capitulo 11 (`11-aspectos-legales.tex`) SHALL declarar un plazo de
conservacion unico, explicito y justificado para los incidentes, coherente con la
retencion de logs de ejecucion declarada en `05-arquitectura.tex:44`. El documento MUST
NOT declarar "conservacion indefinida" para los incidentes ni presentar el bloqueo de
escritura sobre tickets cerrados como una politica de retencion. La seccion SHALL declarar
ademas una politica explicita de supresion/disposicion al vencer el plazo de conservacion
(borrado irreversible o anonimizacion).

#### Scenario: Sin conservacion indefinida

- **WHEN** se lee la seccion 11.2 en busca de la politica de retencion de incidentes
- **THEN** el texto declara un plazo de conservacion de 12 meses rodantes desde la creacion del
  incidente
- **AND** no declara "conservacion indefinida" ni "conservacion permanente" para los incidentes

#### Scenario: Consistencia con la retencion de logs

- **WHEN** se comparan la retencion de incidentes de 11.2 y la retencion de logs de ejecucion de `05-arquitectura.tex:44`
- **THEN** ambas retenciones son compatibles y no se contradicen entre si
- **AND** cualquier diferencia de plazo entre incidentes y logs queda justificada de forma explicita por la finalidad de cada conjunto de datos

#### Scenario: Bloqueo de tickets cerrados no es retencion

- **WHEN** se lee el pasaje que describe los incidentes en estado cerrado
- **THEN** el bloqueo de escritura (PATCH que devuelve 409, C-23) se presenta como control de integridad de auditoria
- **AND** no se presenta como la politica de conservacion ni como sustituto de un plazo de retencion

#### Scenario: Politica de supresion declarada

- **WHEN** se lee la politica de conservacion de incidentes en 11.2
- **THEN** el texto declara de forma explicita que los datos se anonimizan (anonimizacion irreversible) al vencer el plazo de 12 meses
- **AND** la afirmacion "registro auditable permanente" no se presenta como una retencion indefinida ni como una excepcion permanente al vencimiento del plazo

### Requirement: Base de licitud conforme a la Ley 25.326

La seccion 11.2 SHALL fundar la licitud del tratamiento operativo de los datos de
empleados en una base de la Ley 25.326, citando el articulo 5 inciso 2. El documento
MUST NOT invocar el "legitimo interes de la organizacion" como base autonoma de
licitud, por ser una figura del Reglamento General de Proteccion de Datos (art. 6.1.f)
que no existe como tal en la Ley 25.326.

#### Scenario: Base legal citada

- **WHEN** se lee el pasaje que enuncia el principio de licitud en 11.2
- **THEN** el texto cita la Ley 25.326 articulo 5 inciso 2, apartado d) (relacion contractual/laboral), como base del tratamiento de datos de empleados
- **AND** el pasaje distingue la base de licitud operativa del consentimiento que se discute para el corpus de investigacion en 11.5

#### Scenario: Sin legitimo interes como base autonoma

- **WHEN** se busca la expresion "legitimo interes" en la seccion 11.2
- **THEN** la expresion no aparece como base de licitud del tratamiento
- **AND** el texto no atribuye a la Ley 25.326 una base de licitud que la ley no contempla

### Requirement: Alcance de la adecuacion europea

La seccion 11.1 SHALL citar el instrumento de adecuacion de la Union Europea respecto de
Argentina (Decision 2003/490/CE, de 30 de junio de 2003) y su revalidacion de enero de
2024. El documento MUST NOT describir los flujos transfronterizos como "bidireccionales"
ni sugerir que la adecuacion habilita la transferencia de Argentina hacia Estados Unidos.

#### Scenario: Instrumento de adecuacion citado

- **WHEN** se lee el pasaje de 11.1 que menciona la adecuacion europea
- **THEN** el texto nombra la Decision 2003/490/CE y su revalidacion de enero de 2024
- **AND** el texto incluye una cita o referencia verificable al instrumento

#### Scenario: Direccion de la adecuacion correcta

- **WHEN** se lee la descripcion del alcance de la adecuacion
- **THEN** el texto afirma que la adecuacion cubre el flujo UE -> Argentina
- **AND** el texto afirma que la transferencia Argentina -> Estados Unidos (Gemini, Twilio) no esta amparada por la adecuacion y requiere un instrumento propio
- **AND** el texto no describe los flujos como "bidireccionales"

### Requirement: Transferencia telefonica previa a la pseudonimizacion

La seccion 11.3 SHALL nombrar al proveedor de telefonia (Twilio) y declarar que el audio
crudo del llamante y su numero telefonico se transfieren a un proveedor con sede en
Estados Unidos antes de cualquier pseudonimizacion. El documento SHALL describir el orden
real (grabar -> transferir/transcribir -> pseudonimizar) y SHALL citar el instrumento de
transferencia internacional del articulo 12 de la Ley 25.326 (consentimiento o clausulas
contractuales modelo). El acuerdo de procesamiento de datos (DPA) MUST NOT presentarse
como sustituto de ese instrumento.

#### Scenario: Twilio y audio crudo declarados

- **WHEN** se lee la seccion 11.3 sobre transferencia internacional
- **THEN** el texto nombra a Twilio como proveedor de telefonia con sede en Estados Unidos
- **AND** el texto declara que el audio crudo del llamante y su numero telefonico se transfieren antes de la pseudonimizacion

#### Scenario: Orden del flujo correcto

- **WHEN** se lee la descripcion del tratamiento del canal telefonico
- **THEN** el orden descrito es grabar, transferir o transcribir, y luego pseudonimizar
- **AND** el texto no afirma una "pseudonimizacion previa a la transmision" para el canal telefonico

#### Scenario: Instrumento del articulo 12 citado

- **WHEN** se lee la justificacion de la transferencia internacional
- **THEN** el texto cita el articulo 12 de la Ley 25.326 y el instrumento aplicable (consentimiento o clausulas contractuales modelo)
- **AND** el DPA del proveedor se menciona como complemento, no como sustituto del instrumento de transferencia

### Requirement: Plazo de respuesta ARCO

Si el Capitulo 11 declara un plazo para el ejercicio de los derechos de rectificacion, actualizacion o supresion, ese plazo SHALL corresponder a cinco dias habiles conforme al
articulo 16 de la Ley 25.326. El documento MUST NOT declarar el plazo como "cinco dias
corridos".

#### Scenario: Plazo ARCO correcto cuando se declara

- **WHEN** se lee el pasaje que describe los plazos de respuesta a los derechos ARCO
- **THEN** el plazo de rectificacion, actualizacion o supresion se expresa como cinco dias habiles
- **AND** no se expresa como cinco dias corridos

### Requirement: Vigencia de las fuentes juridicas citadas

Las secciones 11.1-11.3 SHALL citar unicamente normas vigentes a la fecha de revision.
SHALL revisarse la vigencia de la Ley 25.326 y su decreto reglamentario, de las
disposiciones/resoluciones vigentes de la AAIP, del Reglamento General de Proteccion de
Datos (RGPD), del estado de la Decision 2003/490/CE y de los instrumentos de transferencia
del articulo 12. El documento MUST NOT citar normas superadas o derogadas y MUST registrar
la fecha de la revision legal.

#### Scenario: Fuentes vigentes y sin normas superadas

- **WHEN** se revisan las referencias legales de las secciones 11.1-11.3
- **THEN** cada norma citada esta vigente a la fecha de revision declarada
- **AND** no se cita ninguna norma superada o derogada

#### Scenario: Fecha de revision registrada

- **WHEN** se revisa el registro de la revision legal del Capitulo 11
- **THEN** queda registrada la fecha en que se verifico la vigencia de las fuentes

### Requirement: Profundidad conceptual del eje de modelos de lenguaje grandes

La seccion 2.4 del marco teorico SHALL tratar de forma explicita los conceptos de
prompting (incluidas las modalidades zero-shot y few-shot), calibracion de la
confianza, alucinacion, sensibilidad al idioma y evaluacion de modelos de lenguaje
grandes. El texto SHALL definirlos y vincularlos con el uso que la tesis hace de
ellos en los capitulos 4, 6, 7 y 8. La seccion SHALL apoyarse en al menos tres
referencias adicionales verificables respecto de las citadas actualmente en 2.4, y
SHALL NOT limitar el tratamiento del eje a la descripcion de la arquitectura
Transformer y del aprendizaje en contexto.

#### Scenario: Conceptos operativos definidos antes de su uso

- **WHEN** se lee la seccion 2.4 del PDF compilado
- **THEN** se definen prompting, calibracion de la confianza, alucinacion, sensibilidad al idioma y evaluacion de LLM
- **AND** cada concepto se relaciona con la forma en que la tesis lo utiliza en los capitulos posteriores

#### Scenario: Respaldo bibliografico suficiente del eje central

- **WHEN** se cuentan las referencias citadas en la seccion 2.4
- **THEN** hay al menos tres referencias adicionales verificables respecto de la version auditada
- **AND** al menos una de ellas es posterior a 2022

### Requirement: Definicion multiclase de la exactitud

La seccion 2.7 SHALL definir la exactitud global directamente para problemas
multiclase, como la proporcion de predicciones correctas sobre el total de
predicciones, en coherencia con la matriz de confusion 5x5 del Capitulo 7. La
tesis SHALL NOT presentar la formula binaria `(TP+TN)/(TP+TN+FP+FN)` como
definicion principal de la exactitud global ni corregirla en una oracion
posterior.

#### Scenario: Formula binaria ausente como definicion principal

- **WHEN** se busca la formula `(TP+TN)/(TP+TN+FP+FN)` en el capitulo 2
- **THEN** no aparece como definicion principal de la exactitud
- **AND** la exactitud se define una sola vez, en clave multiclase

#### Scenario: Coherencia con la evaluacion multiclase

- **WHEN** se compara la definicion de exactitud de 2.7 con la matriz de confusion y las metricas del Capitulo 7
- **THEN** ambas describen un problema de cinco clases
- **AND** la definicion no introduce verdaderos negativos como parte del calculo global

### Requirement: Alcance real del reconocimiento automatico del habla

La seccion 2.5 SHALL distinguir entre el estado del arte del reconocimiento
automatico del habla y la tecnologia efectivamente utilizada por el sistema. La
tesis SHALL NOT afirmar que los modelos preentrenados de Whisper facilitan o
habilitan la integracion del canal telefonico del sistema propuesto. Si Whisper se
conserva como antecedente teorico, el texto SHALL marcarlo como no utilizado en la
implementacion y SHALL remitir a la transcripcion nativa de Twilio descrita en la
seccion 6.4.

#### Scenario: Whisper no se presenta como componente del sistema

- **WHEN** se lee la seccion 2.5 del PDF compilado
- **THEN** no se afirma que Whisper se integre al canal telefonico del sistema
- **AND** se indica que la transcripcion efectiva la provee el servicio nativo de Twilio

#### Scenario: Antecedente teorico correctamente delimitado

- **WHEN** la seccion 2.5 menciona Whisper
- **THEN** lo presenta como antecedente del estado del arte del ASR
- **AND** aclara que no forma parte de la implementacion desarrollada

### Requirement: Justificacion de la persistencia frente a alternativas concretas

La seccion 2.6 SHALL justificar la eleccion de PostgreSQL comparandola con al menos
dos alternativas tecnologicas concretas, entre ellas un motor de documentos y un
motor clave-valor. La justificacion SHALL apoyarse en requisitos del dominio
(integridad referencial, transacciones, consultas relacionales y auditoria) y SHALL
NOT limitarse a una contraposicion generica entre modelos relacionales y no
relacionales.

#### Scenario: Alternativas concretas consideradas

- **WHEN** se lee la seccion 2.6 del PDF compilado
- **THEN** se nombran al menos dos alternativas concretas a PostgreSQL
- **AND** se explica por que no satisfacen los requisitos del dominio

#### Scenario: Justificacion anclada en requisitos del dominio

- **WHEN** se lee la justificacion de PostgreSQL
- **THEN** se vinculan integridad referencial, transacciones y auditoria con las necesidades de la mesa de ayuda
- **AND** no se sostiene la eleccion solo con la expresion generica "alternativas no relacionales"

### Requirement: Respaldo de la afirmacion sobre idiomas del corpus

La seccion 1.7 SHALL respaldar con al menos una cita verificable la afirmacion de
que la mayoria de los estudios publicados sobre clasificacion automatica de tickets
utilizan corpus en ingles, aleman o portugues, o bien SHALL reformular la
afirmacion para que no requiera un respaldo cuantitativo no provisto. Las citas
utilizadas SHALL provenir de las referencias incorporadas por c-78; este change
SHALL NOT duplicar la modernizacion bibliografica ni editar
`Bibliography_base.bib`.

#### Scenario: Afirmacion comparativa respaldada o reformulada

- **WHEN** se lee la seccion 1.7 del PDF compilado
- **THEN** la afirmacion sobre los idiomas de los corpus esta respaldada por al menos una cita verificable de c-78, o bien fue reformulada sin el alcance cuantitativo
- **AND** no queda una generalizacion sobre la literatura sin referencia

#### Scenario: Sin duplicacion del trabajo bibliografico

- **WHEN** se revisa el diff del change
- **THEN** no se agregan ni modifican entradas de `Bibliography_base.bib`
- **AND** las referencias usadas ya existen por c-78

### Requirement: Atribucion editorial de ITIL Service Operation 2011

La seccion 2.2 SHALL atribuir la edicion de 2011 de ITIL Service Operation a The
Stationery Office (TSO) por encargo del Cabinet Office, sin presentarla como una
publicacion directa del Office of Government Commerce. La correccion del campo
bibliografico `OGC2011_itil` SHALL quedar a cargo de c-78 (B3); este change SHALL
NOT editar la entrada `.bib`.

#### Scenario: Atribucion editorial correcta en el cuerpo

- **WHEN** se lee la seccion 2.2 del PDF compilado
- **THEN** la edicion de 2011 se atribuye a TSO/Cabinet Office
- **AND** no se afirma que el Office of Government Commerce sea el editor de la edicion de 2011

#### Scenario: Correccion bibliografica delegada

- **WHEN** se revisa el alcance del change
- **THEN** el texto remite a la correccion de metadatos de c-78
- **AND** no se modifica `Bibliography_base.bib`

### Requirement: Cálculo reproducible del tamaño muestral

El capítulo de marco metodológico SHALL publicar la fórmula del tamaño muestral,
los insumos empleados (tamaño del universo `N`, nivel de confianza o `z`,
proporción esperada `p` y margen de error `e`) y el resultado, de modo que el
valor declarado sea reproducible aritméticamente. Si la corrección por finitud
se aplica, MUST declararse la variante de la fórmula usada. El valor declarado
del corpus (`n = 200`) MUST ser consistente con los insumos publicados; en caso
contrario, el documento MUST corregir el insumo que no lo reproduce (por ejemplo
el margen de error declarado) o el propio tamaño declarado. El insumo `N` SHALL
ser el universo vigente de días hábiles (`N ≈ 2.646`), no el universo calendario
retirado (`N = 3.700`); con `N ≈ 2.646`, `z = 1,96`, `p = 0,5` y la corrección por
finitud, el margen que reproduce `n = 200` SHALL ser `e ≈ 6,66 %`. El texto MUST
NOT declarar el margen previo de `6,74 %` calculado con `N = 3.700`. El capítulo
SHALL declarar de forma explícita si el tamaño del corpus se fijó a priori por la
fórmula o si se fijó por disponibilidad operativa; cuando el tamaño se fijó por
disponibilidad operativa, el margen `e ≈ 6,66 %` SHALL presentarse como la
precisión que ese tamaño fijo implica con los restantes insumos, y MUST NOT
presentarse como un margen elegido para reproducir el corpus ya construido. La
presentación del margen MUST NOT invertir la secuencia del muestreo (fijar el
margen para obtener un tamaño ya conocido).

#### Scenario: Fórmula e insumos publicados

- **WHEN** se lee la subsección de población, muestra y corpus
- **THEN** el texto enuncia la fórmula del tamaño muestral con la corrección por finitud
- **AND** declara `N`, `z` (o el nivel de confianza), `p` (o `p(1−p)`) y `e`

#### Scenario: Tamaño declarado reproducible

- **WHEN** se recalcula el tamaño muestral a partir de los insumos publicados
- **THEN** el resultado reproduce el tamaño declarado del corpus
- **AND** no se declara un margen de error que, con los demás insumos, arroje un tamaño distinto del publicado

#### Scenario: Insumo N actualizado al universo vigente

- **WHEN** se lee el insumo `N` de la fórmula en el marco metodológico
- **THEN** `N` es `≈ 2.646` (días hábiles)
- **AND** el margen declarado es `e ≈ 6,66 %`
- **AND** no aparece `N = 3.700` ni el margen `6,74 %` asociado a ese universo

#### Scenario: Criterio de fijación del tamaño declarado

- **WHEN** se lee la subsección de población, muestra y corpus
- **THEN** el texto declara explícitamente si el tamaño del corpus se fijó a priori o por disponibilidad operativa
- **AND** el margen `6,66 %` se presenta como la precisión implicada por el tamaño fijo, no como el valor elegido para reproducir el corpus
- **AND** la secuencia del muestreo no se describe como la calibración del margen sobre un tamaño ya obtenido

### Requirement: Evidencia de cobertura de pruebas

Toda afirmación de cobertura de pruebas (por ejemplo «superior al 80 %» o «87 %») SHALL estar respaldada por el reporte de cobertura y el comando que lo
genera. Si el reporte no se publica, la cifra MUST retirarse del documento. La
cifra declarada MUST ser consistente entre los capítulos que la mencionan.

#### Scenario: Cifra respaldada por reporte y comando

- **WHEN** se lee una afirmación de cobertura de pruebas unitarias
- **THEN** el documento publica (o referencia como anexo) el reporte de cobertura y el comando que lo genera
- **AND** la cifra declarada coincide con la del reporte

#### Scenario: Cifra retirada si no hay evidencia

- **WHEN** no existe reporte de cobertura publicado
- **THEN** el documento no afirma una cifra porcentual de cobertura
- **AND** las menciones de cobertura en los distintos capítulos son consistentes entre sí

### Requirement: Análisis de potencia estadística a priori

El capítulo de marco metodológico SHALL incluir un análisis de potencia
estadística a priori para el contraste principal, con los supuestos declarados
(nivel de significancia, potencia objetivo, tamaño del efecto asumido o mínimo
detectable y tamaño muestral) y la conclusión sobre la suficiencia del diseño.
El análisis MUST ser coherente con el reconocimiento del tamaño muestral como
amenaza a la validez de conclusión.

#### Scenario: Análisis de potencia presente

- **WHEN** se lee la subsección de análisis estadístico o de amenazas a la validez
- **THEN** existe un análisis de potencia a priori con sus supuestos declarados
- **AND** se reporta la potencia resultante o el efecto mínimo detectable para el tamaño muestral del estudio

#### Scenario: Coherencia con la amenaza de validez de conclusión

- **WHEN** se compara el análisis de potencia con la amenaza de tamaño muestral
- **THEN** ambos usan el mismo tamaño muestral
- **AND** la conclusión sobre la potencia no contradice el reconocimiento de la amenaza

### Requirement: Tratamiento honesto del confundido de la rotación de operadores

Cuando el documento declare rotación o contrabalanceo de operadores entre las mitades del corpus, SHALL reconocer explícitamente si dicha rotación queda
confundida con el efecto del operador dado el número de operadores y de mitades
empleados. Si la rotación no elimina el confundido, el documento MUST NOT
presentarla como mitigación no calificada del efecto de aprendizaje.

#### Scenario: Confundido reconocido

- **WHEN** se lee la descripción del contrabalanceo del orden de procesamiento
- **THEN** el texto declara cuántos operadores y cuántas mitades intervinieron
- **AND** reconoce si la rotación de operadores queda confundida con el efecto del operador

#### Scenario: Mitigación no sobrevendida

- **WHEN** se lee la lista de amenazas a la validez y sus mitigaciones
- **THEN** la rotación de operadores no se presenta como mitigación no calificada si está confundida
- **AND** se declara la limitación resultante o el rediseño de la afirmación

### Requirement: Criterios de exclusión del corpus

El capítulo de marco metodológico SHALL declarar los criterios de exclusión de
incidentes del corpus (al menos duplicados, descripciones vacías o
insuficientes, y casos multicategoría), de forma coherente con los patrones de
error reportados en el análisis de errores.

#### Scenario: Criterios de exclusión declarados

- **WHEN** se lee la subsección de población, muestra y corpus
- **THEN** se enumeran los criterios de exclusión aplicados a los incidentes
- **AND** se indica cómo se trataron duplicados, descripciones vacías y casos multicategoría

#### Scenario: Coherencia con el análisis de errores

- **WHEN** se comparan los criterios de exclusión con los patrones de error del capítulo de resultados
- **THEN** los patrones de error dominantes (descripciones cortas, mezcla de categorías) están contemplados por los criterios de exclusión o su exclusión está justificada

### Requirement: Demarcación del método de investigación

El documento SHALL distinguir el método de investigación (diseño experimental,
muestreo, análisis) del método de construcción del artefacto (gestión del
proyecto). La descripción del marco de trabajo de construcción (por ejemplo
Scrumban) MUST NOT presentarse como la metodología de investigación ni quedar
indistinguible de ella.

#### Scenario: Método de investigación distinguible

- **WHEN** se lee el capítulo de marco metodológico
- **THEN** el método de investigación y el método de construcción del artefacto son distinguibles
- **AND** el marco de gestión del proyecto queda demarcado (reubicado o rotulado) como método de construcción, no como metodología de investigación

### Requirement: Declaración de los analistas etiquetadores

El documento SHALL declarar quiénes realizaron el etiquetado del corpus, su
independencia respecto de los autores del trabajo y si alguno de ellos participó
además como operador del brazo manual. Esta declaración MUST ser coherente con
el cómputo del acuerdo inter-evaluador.

#### Scenario: Analistas declarados

- **WHEN** se lee la descripción del doble etiquetado independiente
- **THEN** se declaran los analistas etiquetadores
- **AND** se declara su independencia (o dependencia) respecto de los autores

#### Scenario: Solapamiento con el brazo manual declarado

- **WHEN** un analista etiquetador también operó el brazo manual
- **THEN** el documento lo declara explícitamente
- **AND** se discute la implicancia para la independencia de la verdad fundamental

### Requirement: Criterio de exactitud sin zona de rechazo

El criterio del umbral de exactitud del clasificador (por ejemplo el 85 % del segundo objetivo específico) SHALL formularse como un umbral de desempeño
verificable contra el resultado observado y su intervalo de confianza, sin
invocar la «zona de rechazo» de un contraste de hipótesis sobre tiempos. El
documento MUST NOT confundir el contraste `H0`/`H1` sobre la mediana de tiempos
con el umbral de exactitud.

#### Scenario: Criterio de exactitud reformulado

- **WHEN** se lee la fundamentación del umbral de exactitud
- **THEN** el criterio se expresa como umbral de desempeño (o pertenencia del intervalo de confianza al umbral)
- **AND** no se invoca una zona de rechazo de hipótesis para la exactitud

#### Scenario: Sin confusión con el contraste de tiempos

- **WHEN** se compara el criterio de exactitud con la formulación de `H0`/`H1`
- **THEN** ambos se refieren a variables distintas (exactitud vs. mediana de tiempo)
- **AND** no se reutiliza el vocabulario del contraste de tiempos para justificar el umbral de exactitud

### Requirement: Verificabilidad de las afirmaciones de pruebas del Capitulo 6

La tesis SHALL afirmar unicamente lo que el repositorio permite verificar. El §6.7
SHALL NOT declarar pruebas de extremo a extremo que instancien N8N y ejecuten el flujo
completo desde el envio de un correo simulado hasta la persistencia del ticket, porque
ninguna prueba del repositorio instancia N8N. El §6.7 SHALL describir lo que existe
(pruebas estructurales del `n8n/workflow.json`, pruebas de API y pruebas de integracion
contra PostgreSQL) o retraer la afirmacion. El recuento y la cobertura de la suite de
frontend declarados en §6.7 SHALL ser reproducibles contra el estado del repositorio en
el momento de la correccion, o SHALL acompanarse de un informe de cobertura versionado
como evidencia; la tesis SHALL NOT publicar cifras de pruebas o de cobertura que el
repositorio no reproduzca.

#### Scenario: Sin afirmacion de pruebas e2e de N8N no verificable

- **WHEN** se busca en el repositorio una prueba que instancie N8N y ejecute el flujo completo hasta la persistencia
- **THEN** no existe ninguna prueba de ese tipo
- **AND** el §6.7 no afirma que tales pruebas existan o se hayan ejecutado

#### Scenario: Recuento y cobertura de frontend reproducibles

- **WHEN** se cuenta la suite de pruebas de frontend en HEAD y se genera el informe de cobertura con el comando documentado
- **THEN** las cifras declaradas en §6.7 coinciden con el resultado reproducible, o existe un informe de cobertura versionado que las respalda
- **AND** no queda publicada la cifra 89/98,6 % sin evidencia que la respalde

### Requirement: Atribuibilidad de la latencia telefonica del §6.4

El §6.4 SHALL NOT informar una latencia telefonica de extremo a extremo como observacion
operativa atribuible al flujo publicado sin declarar el tamano de muestra, la dispersion
y el procedimiento de medicion. Dado que C-17 establece que el agente telefonico no puede
ejecutarse como esta publicado, las observaciones de latencia del §6.4 SHALL retraerse o
reformularse con evidencia real y atribuible. La reformulacion SHALL ser coherente con la
medicion de tiempo telefonico definida en c-77 (Grupo E), sin duplicar su alcance.

#### Scenario: Latencia sin atribucion no se publica

- **WHEN** se lee el §6.4 del PDF compilado
- **THEN** no se declara una latencia de 12 a 15 s como observacion operativa del flujo publicado sin `n`, sin dispersion y sin procedimiento
- **AND** la afirmacion se retrae o se reformula con evidencia real y atribuible

#### Scenario: Coherencia con la medicion de tiempo de c-77

- **WHEN** se compara la formulacion de latencia telefonica del §6.4 con la metrica de tiempo telefonico de c-77
- **THEN** ambas son consistentes y no se contradicen
- **AND** c-94 no redefine la metrica que c-77 posee

### Requirement: Hipoteticidad declarada del ejemplo del dashboard

El §6.8 SHALL presentar el ejemplo de los veinte usuarios que reportan la rotura de
auriculares como un escenario hipotetico, y SHALL NOT presentarlo como «caso concreto» ni
como una observacion realizada. La captura del dashboard SHALL provenir de c-80 (tarea
6.6); c-94 no agrega capturas ni duplica esa evidencia.

#### Scenario: Ejemplo marcado como hipotetico

- **WHEN** se lee el cierre del §6.8
- **THEN** el ejemplo del dashboard se presenta como hipotetico
- **AND** no se afirma que sea un «caso concreto» ni un hecho observado

### Requirement: Alcance declarado de la preparacion para Kubernetes

El §6.1 SHALL NOT declarar que el despliegue esta «preparado para migracion a un cluster
Kubernetes 1.30» sin un manifiesto que lo respalde en el repositorio. La afirmacion SHALL
retraerse o acotarse explicitamente como trabajo futuro o como intencion de diseno, sin
presentarla como una capacidad implementada.

#### Scenario: Sin manifiesto no se declara preparacion implementada

- **WHEN** se busca en el repositorio un manifiesto de Kubernetes para el despliegue
- **THEN** no existe ningun manifiesto de ese tipo
- **AND** el §6.1 no declara la preparacion para Kubernetes como capacidad implementada

### Requirement: Parametros de inferencia sin calificativo no respaldado

El §5.4 SHALL NOT calificar los parametros de inferencia (temperatura, top-p, max tokens,
timeout) como «optimizados para exactitud y latencia» sin describir el procedimiento de
optimizacion ni los valores alternativos evaluados. El calificativo SHALL retirarse o el
procedimiento SHALL documentarse.

#### Scenario: Sin procedimiento no se afirma optimizacion

- **WHEN** se lee el §5.4 del PDF compilado
- **THEN** no se afirma que los parametros de inferencia esten «optimizados» sin un procedimiento de optimizacion descrito
- **AND** el calificativo se retira o el procedimiento se documenta con los valores alternativos evaluados

### Requirement: Completitud y no exhaustividad de la Tabla 5 de puntos de entrada REST

La Tabla 5 (`tab:api`, §5.7) SHALL reflejar los grupos de puntos de entrada reales de la
API —al menos autenticacion, incidentes (con su PATCH), clasificaciones (GET y PATCH),
estadisticas y salud— y SHALL declarar de forma explicita que no es exhaustiva, con
remision al contrato completo en el Anexo D/OpenAPI. La tabla SHALL NOT presentarse como
el listado completo de la API.

#### Scenario: Grupos de entrada presentes

- **WHEN** se compara la Tabla 5 con las rutas de `docs/openapi.json`
- **THEN** la tabla incluye los grupos de autenticacion, incidentes, clasificaciones, estadisticas y salud
- **AND** incluye el PATCH sobre incidentes y las operaciones GET y PATCH de clasificaciones

#### Scenario: No exhaustividad declarada

- **WHEN** se lee la Tabla 5 y su texto circundante
- **THEN** se declara que la tabla no es exhaustiva
- **AND** se remite al contrato completo en el Anexo D/OpenAPI

### Requirement: Coherencia del nombre del modelo en el cuerpo de la tesis

El cuerpo de la tesis SHALL nombrar el modelo de inferencia con el identificador real
configurado y desplegado, `gemini-3.6-flash`, en todas sus menciones. El texto SHALL NOT
usar «Gemini 2.5 Flash», «Gemini~2.5» ni cualquier otra variante del identificador
obsoleto en los archivos de seccion del cuerpo. La alineacion SHALL comprender, como
minimo, `00-resumen.tex`, `05-arquitectura.tex`, `06-implementacion.tex`,
`08-discusion.tex`, `09-conclusiones.tex`, `10-recomendaciones.tex`,
`11-aspectos-legales.tex` y `12-anexos.tex`. El §1.6 de `01-introduccion.tex` y
`docs/anexo_h_prompt_gemini.md` ya fueron alineados por c-76 y SHALL permanecer bajo su
titularidad; c-94 SHALL NOT reescribirlos ni duplicar esa correccion. La fuente de verdad
del identificador es `App/Backend/app/config/settings.py` (`gemini_model =
"gemini-3.6-flash"`), consistente con `App/Backend/.env.example`, `README.md` y el propio
Anexo H.

#### Scenario: Cuerpo alineado al identificador real

- **WHEN** se ejecuta `rg -n "Gemini[ ~]*2\.5"` sobre los ocho archivos de seccion del cuerpo
- **THEN** no hay coincidencias
- **AND** todas las menciones del modelo usan `gemini-3.6-flash`

#### Scenario: Coherencia con la configuracion desplegada

- **WHEN** se compara el nombre del modelo citado en el cuerpo con `App/Backend/app/config/settings.py`, `App/Backend/.env.example`, `README.md` y `docs/anexo_h_prompt_gemini.md`
- **THEN** todos coinciden en `gemini-3.6-flash`
- **AND** no queda ninguna mencion de «Gemini 2.5 Flash» en el cuerpo

#### Scenario: Alcance de c-76 sin duplicacion

- **WHEN** se revisa la titularidad de §1.6 de `01-introduccion.tex` y `docs/anexo_h_prompt_gemini.md`
- **THEN** ambos quedan como los dejo c-76 y c-94 no los re-edita
- **AND** c-94 solo cubre las menciones del modelo fuera de ese alcance

### Requirement: Alineacion textual del residuo de C-18 sin duplicacion

La alineacion textual del residuo de C-18 —Tabla 4 con `canal_origen_id` en lugar de `id_canal`, y §5.3 con un unico `POST /api/v1/incidentes` que clasifica y persiste en vez de dos llamadas— SHALL permanecer bajo la titularidad de c-77 C3. c-94 SHALL referenciar y
verificar esa alineacion, y SHALL NOT reescribirla ni duplicar su alcance.

#### Scenario: Residuo de C-18 referenciado, no duplicado

- **WHEN** se revisa el alcance de c-94 frente a c-77 C3
- **THEN** c-94 referencia la alineacion de Tabla 4 y §5.3 sin reescribirla
- **AND** no existen dos tareas en changes distintos que editen las mismas lineas del mismo archivo con el mismo objetivo

### Requirement: Reporte de normalidad Shapiro-Wilk

La tesis SHALL reportar de forma completa la prueba de normalidad que justifica
el uso de Wilcoxon. La Sección~4.7 MUST informar el estadístico \(W\) y el valor
\(p\) de Shapiro-Wilk para el flujo manual, el flujo automatizado y las
diferencias pareadas, con una precisión suficiente para reproducir el resultado.
La Sección~7.1 SHALL referenciar ese reporte al presentar la prueba de Wilcoxon.
`evaluation/report.md` MUST registrar los valores, el comando reproducible y la
identificación del corpus sobre el que se calcularon. Los valores MUST
recalcularse después de cualquier corrección del corpus que altere los tiempos,
en particular la corrección telefónica de c-77 (E3).

#### Scenario: Estadístico y p por grupo y por diferencias

- **WHEN** se lee la Sección~4.7 de la tesis
- **THEN** aparecen el estadístico \(W\) y el valor \(p\) de Shapiro-Wilk para el flujo manual, el flujo automatizado y las diferencias pareadas
- **AND** no se afirma únicamente "ambos grupos rechazan la normalidad con \(p < 0{,}01\)" sin reportar los valores

#### Scenario: Trazabilidad del cálculo

- **WHEN** se revisa `evaluation/report.md`
- **THEN** figuran los valores de \(W\) y \(p\), el comando o función reproducible que los generó y la identificación o hash del corpus usado
- **AND** los valores del reporte coinciden con los de la tesis

#### Scenario: Recalculo tras cambiar los tiempos del corpus

- **WHEN** c-77 modifica los tiempos automatizados telefónicos
- **THEN** los valores de Shapiro-Wilk se recalculan sobre el corpus corregido
- **AND** no se copian los valores calculados antes de esa corrección

### Requirement: Interrogación crítica de los resultados

El Capítulo~8 SHALL interrogar los resultados además de interpretarlos. La
Sección~8.1 MUST incluir una lectura crítica que explicite al menos tres
explicaciones rivales de la reducción del tiempo de registro, la evidencia
disponible a favor o en contra de cada una, la condición que permitiría
descartarla y el grado de incertidumbre que persiste. La lectura crítica MUST
explicar por qué la categoría Sistemas se confunde sistemáticamente con otras
categorías, apoyándose en la matriz de confusión 5x5 real y en las métricas por
clase. La interpretación MUST NOT presentar la hipótesis de trabajo como
confirmada de forma concluyente cuando las explicaciones rivales no puedan
descartarse.

#### Scenario: Explicaciones rivales presentes

- **WHEN** se lee la Sección~8.1
- **THEN** se identifican al menos tres explicaciones rivales de la reducción de tiempo (por ejemplo, asimetría del instrumento de medición, simplificación de la tarea o mezcla de canales, novedad o efecto Hawthorne, y selección de la muestra)
- **AND** por cada una se declara qué evidencia la sostiene o la debilita y qué observación permitiría descartarla

#### Scenario: Confusión de Sistemas explicada

- **WHEN** se lee la explicación de la confusión de la categoría Sistemas
- **THEN** la explicación se apoya en la matriz 5x5 y en las métricas por clase reales
- **AND** distingue la ambigüedad léxica o taxonómica de la falta de contexto en la descripción del incidente
- **AND** no se limita a atribuir el patrón a una limitación genérica del modelo

#### Scenario: Sin confirmación concluyente

- **WHEN** la Sección~8.1 evalúa la hipótesis de trabajo
- **THEN** el texto distingue entre resultados consistentes con la hipótesis y resultados que la confirman de forma concluyente
- **AND** no afirma que la hipótesis queda validada si alguna explicación rival permanece abierta

### Requirement: Trazabilidad y alcance del baseline TF-IDF+SVM

Toda comparación de la tesis contra un clasificador supervisado clásico SHALL ser
trazable o SHALL estar explícitamente acotada como exploratoria. Si se reporta un
resultado de TF-IDF+SVM, la tesis MUST documentar el procedimiento, la partición
de entrenamiento y evaluación, el tamaño \(n\) del subconjunto evaluado y la
ubicación del código o de los artefactos reproducibles. Si esos elementos no
están preservados, la cifra MUST retirarse como resultado y el chequeo MUST
declararse exploratorio, no reproducible y no comparable. En ningún caso la tesis
MUST afirmar una ganancia sustantiva sobre un baseline cuyos números no puedan
verificarse.

#### Scenario: Baseline documentado o acotado

- **WHEN** se lee la limitación sobre la comparación con clasificadores alternativos en la Sección~8.3
- **THEN** o bien se documentan procedimiento, partición, \(n\) y código/artefactos del baseline TF-IDF+SVM
- **AND** o bien se declara explícitamente que el chequeo fue exploratorio, que la partición y el \(n\) no se preservaron y que no se reporta como resultado comparable

#### Scenario: Sin cifras no verificables

- **WHEN** se busca en la tesis la exactitud del baseline y su F1 macro
- **THEN** no aparecen "78~%" ni "0,764" presentados como resultados si no existe el procedimiento y el artefacto que los respalde

#### Scenario: Sin afirmación de superioridad

- **WHEN** se lee la comparación del esquema híbrido con el baseline
- **THEN** no se afirma que el esquema propuesto "confirma" o "aporta" una ganancia sustantiva sobre el baseline
- **AND** la comparación se presenta como pendiente de una evaluación sistemática sobre el corpus completo

### Requirement: Evidencia textual anonimizada de errores

La Sección~7.4 SHALL incluir evidencia textual de los errores de clasificación,
no solo su tipificación agregada. MUST presentar entre dos y tres ejemplos de
incidentes mal clasificados, con el texto anonimizado de la descripción, el
sector asignado, el sector predicho y la confianza reportada. Los ejemplos MUST
provenir de `evaluation/predicciones.json` y MUST ser consistentes con la matriz
de confusión y la tipología de errores. La anonimización MUST preservar la
utilidad analítica del ejemplo sin exponer datos personales.

#### Scenario: Ejemplos textuales presentes

- **WHEN** se lee la Sección~7.4
- **THEN** aparecen entre dos y tres ejemplos de descripciones de incidentes mal clasificados
- **AND** cada ejemplo indica el sector asignado, el sector predicho y la confianza

#### Scenario: Consistencia con las predicciones

- **WHEN** se compara cada ejemplo con `evaluation/predicciones.json`
- **THEN** el par asignado/predicho y la confianza coinciden con el registro
- **AND** el ejemplo pertenece a uno de los patrones de error descritos en la tipología

#### Scenario: Anonimización suficiente

- **WHEN** se revisan los textos citados
- **THEN** no contienen nombres de personas, direcciones, correos, teléfonos ni identificadores internos que permitan reidentificación
- **AND** la descripción conserva el rasgo que explica el error

### Requirement: Fuentes y cotas de costos operativos

La Sección~8.4 SHALL sustentar las estimaciones económicas en fuentes
verificables o en cotas explícitas. El costo por invocación MUST citar la lista
de precios oficial del proveedor de inferencia, indicar el modelo y la fecha de
consulta, y declarar los supuestos de tokens por invocación. El costo de
infraestructura MUST citar una lista de precios pública de un proveedor
identificado o presentarse como una cota de orden de magnitud con la composición
de rubros y los supuestos de capacidad y horas de uso. No se admiten cifras
monetarias sin fuente ni rango declarado.

#### Scenario: Costo de inferencia con fuente

- **WHEN** se lee la estimación del costo por invocación en la Sección~8.4
- **THEN** se identifica el proveedor, el modelo y la lista de precios oficial consultada con su fecha
- **AND** se declaran los supuestos de tokens de entrada y salida usados para llegar al valor

#### Scenario: Costo de infraestructura con fuente o cota

- **WHEN** se lee la estimación del costo mensual de infraestructura
- **THEN** se identifica el proveedor y la lista de precios consultada, o se presenta una cota con los rubros incluidos (cómputo, almacenamiento, respaldo, transferencia)
- **AND** la estimación se declara como orden de magnitud y no como una cotización

#### Scenario: Sin cifras desnudas

- **WHEN** se busca en la Sección~8.4 "50--100 USD/mes" u "0,02 USD por invocación"
- **THEN** toda aparición está acompañada por la fuente o por la cota y los supuestos que la justifican
- **AND** no queda ninguna cifra monetaria sin respaldo

### Requirement: Delimitación de las afirmaciones del Capítulo 9

El Capítulo~9 SHALL limitarse a sintetizar resultados ya presentados y
argumentados en los capítulos precedentes. La Sección~9.1 MUST NOT introducir
interpretación estadística nueva, en particular la lectura de \(W=0\) como
resultado "poco frecuente" o que "merece interpretarse con cautela"; esa
interpretación corresponde al Capítulo~8 y la referencia a la prueba al
Capítulo~7. La Sección~9.2 MUST acotar cualquier afirmación general sobre el
desempeño de los LLM frente a clasificadores supervisados al corpus, al dominio y
al contraste efectivamente realizado, y MUST NOT presentarla como una conclusión
general del campo.

#### Scenario: Sin interpretación estadística nueva en Conclusiones

- **WHEN** se lee la Sección~9.1
- **THEN** no aparece la interpretación de \(W=0\) como resultado poco frecuente ni la recomendación de interpretarlo con cautela
- **AND** cualquier referencia a la prueba de Wilcoxon remite al Capítulo~7 o al Capítulo~8 sin repetir su interpretación

#### Scenario: Afirmación general acotada

- **WHEN** se lee la afirmación de la Sección~9.2 sobre LLM y clasificadores supervisados
- **THEN** la afirmación se limita al corpus, al dominio y al contraste disponible en este trabajo
- **AND** no se sostiene que los LLM invocados por instrucciones superen de forma general a los clasificadores supervisados clásicos sobre representaciones estáticas

#### Scenario: Coordinación sin reintroducir correcciones ajenas

- **WHEN** se aplica este change después de c-77 y c-78
- **THEN** no se reintroduce \(W=0\) ni la atribución corregida de Revina et al. (2020)
- **AND** la tensión de evidencia contraria que incorpora c-78 permanece en el Capítulo~8 sin duplicarse en el Capítulo~9

### Requirement: Fuente y trazabilidad de las tablas

Todas las tablas del documento SHALL declarar su fuente conforme al estilo APA~7,
ya sea como elaboracion propia ("Fuente: elaboracion propia") o como la
referencia de la que provienen los datos. La Tabla~1 del Capitulo~3
(`tab:comparativa`) SHALL ademas respaldar cada fila de solucion comercial con una
cita verificable, una linea de fuente y una fecha de consulta, y MUST NOT
autoevaluar la propuesta del trabajo dentro de la misma grilla comparativa.

#### Scenario: Linea de fuente en las nueve tablas
- **WHEN** se inspecciona cualquiera de las nueve tablas del documento (`tab:comparativa` en 03; `tab:variables` en 04; `tab:capas`, `tab:entidades` y `tab:api` en 05; `tab:tiempos`, `tab:matriz`, `tab:metricas` y `tab:errores` en 07)
- **THEN** cada tabla declara una linea de fuente APA~7 ("Fuente: elaboracion propia" o la referencia correspondiente)
- **AND** la linea de fuente no rompe la composicion de la tabla definida por c-80

#### Scenario: Tabla 1 con citas y fecha de consulta por fila
- **WHEN** se lee la Tabla~1 del Capitulo~3
- **THEN** cada fila de solucion comercial (Zendesk Suite, Freshdesk, Jira Service Management, ServiceNow ITSM, osTicket) tiene una cita verificable y una fecha de consulta asociada
- **AND** la tabla declara su linea de fuente

#### Scenario: Sin autoevaluacion en la grilla comparativa
- **WHEN** se lee la Tabla~1 del Capitulo~3
- **THEN** la fila "Propuesta" ya no se evalua con los mismos criterios que las soluciones de terceros dentro de la tabla
- **AND** la comparacion de la propuesta contra las soluciones comerciales se desarrolla en prosa con respaldo, no como autoevaluacion en la misma grilla

### Requirement: Atribucion de la definicion de empresa mediana y del marco etico

Las afirmaciones que atribuyen una definicion o un marco normativo a una fuente externa SHALL citar esa fuente y contar con la entrada bibliografica
correspondiente. En particular, la definicion de empresa mediana atribuida a la
Secretaria de la Pequena y Mediana Empresa en la seccion 1.1 y la justificacion
etica del debriefing en la seccion 11.5 SHALL quedar respaldadas o reformuladas
sin atribucion.

#### Scenario: Definicion de empresa mediana con cita
- **WHEN** se lee la seccion 1.1 (`01-introduccion.tex`) donde se define a la empresa mediana por el rango de 50 a 200 trabajadores en el sector servicios
- **THEN** la afirmacion cita la Secretaria de la Pequena y Mediana Empresa (SEPyME)
- **AND** existe una entrada bibliografica correspondiente en `Bibliography_base.bib`
- **AND** no queda una atribucion a una fuente sin cita ni entrada

#### Scenario: Cita huerfana del marco etico resuelta
- **WHEN** se busca la cita "(APA, 2017)" en la seccion 11.5 (`11-aspectos-legales.tex`)
- **THEN** la cita fue resuelta: o existe la entrada `APA2017` en `Bibliography_base.bib`, o la cita fue retirada y el argumento se sostiene sin ella
- **AND** el documento no contiene citas huerfanas (ninguna cita sin entrada en el `.bib`)

### Requirement: Exactitud de la licencia de herramientas de terceros

El documento SHALL describir la licencia de las herramientas de terceros con
exactitud. N8N MUST NOT presentarse como "codigo abierto" sin matiz; su licencia
oficial (Sustainable Use, fair-code) SHALL quedar explicitada o la herramienta
SHALL retirarse de toda enumeracion que la rotule como codigo abierto.

#### Scenario: N8N fuera de la enumeracion de codigo abierto
- **WHEN** se lee la seccion 1.7 (`01-introduccion.tex`) donde se enumeran "herramientas de bajo costo y codigo abierto"
- **THEN** N8N no aparece rotulado como codigo abierto sin matiz
- **AND** su licencia Sustainable Use queda explicitada o la herramienta se retira de esa enumeracion

#### Scenario: N8N fuera del "exclusivamente codigo abierto"
- **WHEN** se lee la seccion 6.1 (`06-implementacion.tex`) donde se afirma que la implementacion uso "exclusivamente tecnologias de codigo abierto"
- **THEN** la afirmacion ya no incluye implicitamente a N8N como codigo abierto
- **AND** la licencia Sustainable Use de N8N queda explicitada en el capitulo

#### Scenario: Consistencia con el estado del arte
- **WHEN** se comparan los pasajes corregidos con las secciones 3.2 y 6.3
- **THEN** la descripcion de la licencia de N8N es consistente con "licencia Sustainable Use" y "fair-code" ya usadas en esas secciones

### Requirement: Consistencia de la descripcion de la organizacion adoptante

La organizacion adoptante SHALL describirse de forma consistente a lo largo del
documento: la misma denominacion y los mismos atributos (una unica organizacion
mediana del sector servicios, aproximadamente 120 usuarios internos, cinco areas
funcionales, con sede en la provincia de Mendoza) en todos los pasajes que la
mencionan.

#### Scenario: Denominacion unificada
- **WHEN** se leen las secciones 1.2 y 1.8 (`01-introduccion.tex`)
- **THEN** ambos pasajes describen a la organizacion adoptante con la misma denominacion
- **AND** no alternan entre "una organizacion mediana" y "una unica organizacion" como si fueran caracterizaciones distintas

#### Scenario: Atributos consistentes
- **WHEN** se compara la caracterizacion de la organizacion en 1.2 y 1.8
- **THEN** los atributos coinciden (sector servicios, aproximadamente 120 usuarios, cinco areas, Mendoza)
- **AND** no se introduce un nombre propio no autorizado ni atributos contradictorios

### Requirement: Cobertura y densidad de citas por capitulo

Las afirmaciones que se apoyan en literatura SHALL citar una referencia
verificable en el punto donde se formulan. El documento MUST NOT introducir
referencias nuevas fuera de las dos entradas requeridas para la definicion de
empresa mediana y el marco etico; la bibliografia moderna 2023-2026 incorporada
por c-78 SHALL reutilizarse, sin duplicar su trabajo.

#### Scenario: Capitulo 7 con citas donde corresponde
- **WHEN** se leen las afirmaciones del Capitulo~7 (`07-resultados.tex`) que se apoyan en literatura o en metodos de terceros
- **THEN** esas afirmaciones citan una referencia verificable
- **AND** el capitulo deja de tener cero citas sobre afirmaciones propias que requieren respaldo

#### Scenario: Capitulo 6 y Capitulo 3 con respaldo
- **WHEN** se revisan las afirmaciones metodologicas del Capitulo~6 (`06-implementacion.tex`) y la comparacion del Capitulo~3
- **THEN** las afirmaciones apoyadas en literatura citan una referencia verificable
- **AND** la Tabla~1 del Capitulo~3 deja de sostener su comparacion sin citas

#### Scenario: Sin duplicar la bibliografia de c-78
- **WHEN** se inspecciona `Bibliography_base.bib` despues de este change
- **THEN** las unicas entradas agregadas son las dos de la definicion de empresa mediana y del marco etico
- **AND** las referencias 2023-2026 usadas provienen de las ya incorporadas por c-78
- **AND** no se crean entradas duplicadas ni citas huerfanas nuevas

### Requirement: Identidad institucional de la portada

La portada de la tesis (`sections/00-portada.tex`) SHALL acreditar la identidad
institucional del trabajo: el logo de la UTN Facultad Regional Mendoza, el rótulo
"Trabajo Final de Carrera", los tres autores (Luca Gomez, Carla Bustos, Gonzalo
Sevilla) y los dos directores ("Prof. Alberto Cortez y Prof. Ariel Enferrel", en
ese orden, ambos con el tratamiento "Prof."). La portada SHALL tomar la fecha de
compilación mediante `\today` y MUST NOT hardcodear el año.

#### Scenario: Portada con logo y directores

- **WHEN** se inspecciona la primera página del PDF compilado
- **THEN** aparece el logo UTN-FRM y el rótulo "Trabajo Final de Carrera"
- **AND** figuran los autores Luca Gomez, Carla Bustos y Gonzalo Sevilla
- **AND** figuran los directores "Prof. Alberto Cortez y Prof. Ariel Enferrel"

#### Scenario: Fecha de compilación no hardcodeada

- **WHEN** se compila el documento con babel spanish
- **THEN** la fecha de la portada se genera con `\today` (p. ej. "20 de octubre de 2026")
- **AND** el archivo fuente no contiene un año fijo en la portada

### Requirement: Presupuesto de páginas preservado

La reducción de páginas SHALL llevar el total del PDF a un máximo de **100
páginas**, medido con `pdfinfo main.pdf` sobre el documento completo (portada,
índices, glosario, cuerpo, referencias y anexos). El conteo MUST ser de 100
páginas o menos y MUST NOT exceder el tope vigente del plan de correcciones. La
portada SHALL seguir ocupando exactamente una página.

#### Scenario: Conteo de páginas sin cambios

- **WHEN** se compila `main.tex` tras el change y se ejecuta `pdfinfo main.pdf | grep Pages`
- **THEN** el total de páginas es 100 o menos
- **AND** la portada sigue ocupando exactamente una página

#### Scenario: Tope medido sobre el total

- **WHEN** se cuenta el total de páginas del PDF
- **THEN** el conteo incluye portada, índices, glosario, referencias y anexos
- **AND** no se computa un subconjunto (solo el cuerpo) para dar por cumplido el tope

### Requirement: Coherencia de metadatos PDF

Los metadatos del PDF (`preambles/preamble.tex`) SHALL ser coherentes con la
denominación "Trabajo Final". `pdfsubject` SHALL declarar "Trabajo Final —
Tecnicatura Universitaria en Programación" y `pdftitle`, `pdfauthor` y
`pdfkeywords` SHALL ser consistentes con esa denominación y con la autoría real.

#### Scenario: Metadatos coherentes

- **WHEN** se leen las propiedades del PDF compilado o el `\hypersetup` del preamble
- **THEN** `pdfsubject` es "Trabajo Final — Tecnicatura Universitaria en Programación"
- **AND** `pdfauthor` lista Luca Gomez, Carla Bustos y Gonzalo Sevilla
- **AND** no queda "Tesis de Grado" en los metadatos

### Requirement: Nomenclatura "Trabajo Final" en el documento

El documento SHALL usar la denominación "Trabajo Final" en lugar de "Tesis de
Grado" en el cuerpo del manuscrito y el preámbulo. La ruta real
`docs/Tesis/Correcciones/` MUST NOT alterarse, porque es una ruta de repositorio
válida.

#### Scenario: Sin "Tesis de Grado" en el manuscrito

- **WHEN** se buscan las ocurrencias de "Tesis de Grado" en `main.tex`, `preambles/preamble.tex` y `sections/*.tex`
- **THEN** no queda ninguna ocurrencia de "Tesis de Grado"
- **AND** la ruta `docs/Tesis/Correcciones/dictamen-correcciones.md` permanece intacta

### Requirement: Integridad de referencias cruzadas

Toda `\section` y `\subsection` de `sections/*.tex` SHALL tener un `\label`. Las
remisiones a capítulos y secciones SHALL resolverse con `\ref`/`\autoref` (o
`\cref` si el paquete ya está disponible) y MUST NOT escribirse a mano con números
fijos. La compilación SHALL producir cero referencias indefinidas y la prosa SHALL
denominar "Sección" (no "Capítulo"). El documento MUST conservar
`\documentclass{article}`.

#### Scenario: Cero remisiones duras

- **WHEN** se busca en `sections/*.tex` el patrón "Capítulo N" o "Sección N.N" en prosa
- **THEN** no queda ninguna remisión dura
- **AND** cada remisión se resuelve mediante una etiqueta `\label`

#### Scenario: Cero referencias indefinidas

- **WHEN** se compila el documento con XeLaTeX
- **THEN** el log no contiene advertencias de "undefined reference" ni "multiply defined label"
- **AND** toda `\ref`/`\autoref` apunta a una etiqueta existente

#### Scenario: Remisión de la cota de 45 s corregida

- **WHEN** se lee la remisión de la cota de 45 s en `07-resultados.tex`
- **THEN** apunta a la sección de métricas e instrumentos (4.6), donde la cota se enuncia
- **AND** no apunta a la sección 4.4 (población, muestra y corpus)

#### Scenario: Reubicación del capítulo 11 segura

- **WHEN** el capítulo 11 se mueve de posición (c-105)
- **THEN** ninguna referencia cruzada queda indefinida, porque todas usan etiquetas
- **AND** la numeración se recalcula automáticamente

### Requirement: Universo de días hábiles y proyección horaria vigente

La tesis SHALL computar el universo de incidentes sobre días hábiles
(`≈ 2.646 = 42 × 63`) y SHALL reportar la proyección de horas-persona liberadas
como `≈ 32,2 h` por trimestre. El documento MUST NOT presentar el universo
calendario retirado (`3.700 = 42 × 88`) ni la proyección `45,0 h` como resultado
vigente. La proyección SHALL ser reproducible con el ahorro medio por incidente
(`43,82 s`) sobre el universo adoptado. El criterio de días hábiles SHALL
declararse coherente con el origen de la tasa diaria de `42` incidentes, tomada de
una semana laboral.

#### Scenario: Universo en días hábiles

- **WHEN** se lee la subsección de población, muestra y corpus y el resumen
- **THEN** el universo declarado es `≈ 2.646` incidentes, obtenido de `42 × 63` días hábiles
- **AND** no se declara `3.700` como universo vigente

#### Scenario: Proyección horaria reproducible

- **WHEN** se lee la proyección de horas-persona liberadas en el resumen, la introducción y la discusión
- **THEN** la proyección declarada es `≈ 32,2 h` por trimestre
- **AND** el cálculo reproduce `43,82 s × 2.646 / 3.600 ≈ 32,2 h`
- **AND** no se declara `45,0 h` como valor vigente

### Requirement: Intervención humana por gate declarada no medida

La tesis SHALL NOT reportar la proporción de intervención humana del `9,5 %` como
resultado vigente. El aporte operativo asociado al gate de revisión humana SHALL
reformularse como no medido, porque no existe registro por caso de la intervención
en `evaluation/predicciones.json`, `evaluation/report.md` ni `data/`, y porque el
gate implementado (`requiere_revision_humana = (confianza < 0,70)`) no dispara
revisión en ningún caso del corpus. El resumen, los resultados, la discusión, las
conclusiones y las recomendaciones MUST NOT conservar la cifra retirada. La
afirmación de que el flujo automatizado corrió "sin intervención humana" SHALL
reconciliarse con la definición de las dos dimensiones rotuladas de la variable.

#### Scenario: Cifra retirada ausente

- **WHEN** se busca "9,5 %" o "19 casos" como intervención humana en el PDF compilado
- **THEN** no aparece la cifra del 9,5 % presentada como resultado de intervención
- **AND** el aporte operativo se declara no medido con la evidencia disponible

#### Scenario: Aporte operativo reformulado

- **WHEN** se lee la subsección de reducción de la intervención humana y la discusión
- **THEN** el texto declara que la intervención por gate no fue medida
- **AND** explica que el gate implementado no escala casos en el corpus, en lugar de afirmar una reducción porcentual no sustentada

#### Scenario: Coherencia con "sin intervención humana"

- **WHEN** se compara la afirmación del protocolo de pruebas con la subsección de reducción de intervención humana
- **THEN** ambas describen la misma definición rotulada de la variable
- **AND** no se sostiene simultáneamente que hubo 9,5 % de intervención y que el flujo corrió sin intervención humana

### Requirement: Declaración del estado de la hipótesis principal

El resumen, la discusión y las conclusiones SHALL declarar el estado de la
hipótesis principal como parcialmente confirmada y parcialmente refutada: se
confirma en la reducción del tiempo de registro y se refuta en el umbral de
clasificación (`73,5 %` de exactitud y macro-F1 `0,5207`, por debajo de `85 %` y
`0,85`). El resumen MUST NOT permitir inferir una confirmación plena de la
hipótesis. La declaración SHALL distinguir las sub-hipótesis de tiempo,
intervención humana y exactitud o F1. La sub-hipótesis de intervención humana
SHALL declararse **no medida** con la evidencia disponible, de forma coherente con
la retirada del `9,5 %` (c-107); el documento MUST NOT reintroducir esa cifra ni
presentarla como resultado. Las conclusiones SHALL declarar el estado por
sub-hipótesis: confirmada en tiempo, refutada en clasificación e intervención
humana no medida.

#### Scenario: Estado parcial declarado en el resumen

- **WHEN** se lee el resumen en español y el abstract
- **THEN** se declara que la hipótesis principal se confirma en tiempo y se refuta en clasificación
- **AND** no se presenta el umbral de clasificación como alcanzado

#### Scenario: Estado parcial declarado en discusión y conclusiones

- **WHEN** se leen la discusión y las conclusiones
- **THEN** el estado de la hipótesis principal se declara parcialmente confirmado y parcialmente refutado
- **AND** la refutación se ancla en las métricas de clasificación reportadas

#### Scenario: Sub-hipótesis de intervención humana declarada no medida

- **WHEN** se lee el estado de la hipótesis principal en el resumen y las conclusiones
- **THEN** la sub-hipótesis de intervención humana se declara no medida con la evidencia disponible
- **AND** no se reporta el `9,5 %` de intervención humana como resultado vigente

#### Scenario: Estado por sub-hipótesis en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** se distingue explícitamente la sub-hipótesis confirmada (tiempo), la refutada (exactitud/F1) y la no medida (intervención humana)
- **AND** no se declara la hipótesis principal confirmada o refutada como bloque

### Requirement: Costo de API consistente con el universo vigente

La estimación del costo de inferencia en la discusión SHALL recalcularse sobre el
universo vigente de días hábiles (`≈ 2.646` incidentes trimestrales), no sobre el
universo calendario retirado (`3.700`). El costo declarado SHALL conservar la cota
superior de `2 USD` por trimestre y declarar el porcentaje de casos que requieren
inferencia externa (`34,5 %`).

#### Scenario: Costo recalculado sobre el universo vigente

- **WHEN** se lee la estimación de costo de API en la discusión
- **THEN** el volumen declarado es `≈ 2.646` incidentes trimestrales
- **AND** el costo se recalcula con ese volumen y el porcentaje `34,5 %` de inferencia externa
- **AND** no se declara el costo con el volumen retirado de `3.700`

### Requirement: Verificacion de integridad y atribucion bibliografica (B1-B3)

La tesis SHALL sostener, tras las ramas posteriores que editan los sitios de cita, las correcciones bibliograficas B1-B3 aplicadas por c-78: la atribucion correcta de Revina, Buza & Meister (2020) sin BERT ni una exactitud cercana al 91 %; la cobertura de al menos 12 articulos arbitrados publicados entre 2023 y 2026; la atribucion de los rangos interpretativos de Kappa a Landis & Koch (1977); y la higiene de citas (cero citas huerfanas, cero entradas sin usar y toda entrada resoluble por DOI o landing de editorial). El documento MUST NOT reintroducir las citas fabricadas Karchhud et al. (2024) ni Mehdi et al. (2023).

#### Scenario: Atribucion de Revina sin BERT ni 91 %

- **WHEN** se buscan "BERT" y "91" junto a las menciones de Revina et al. (2020) en `03-estado-del-arte.tex` y `08-discusion.tex`
- **THEN** no se atribuye a ese articulo el uso de BERT ni de modelos preentrenados
- **AND** no se le atribuye una exactitud cercana al 91 %
- **AND** la entrada citada conserva la clave correcta (`Revina2020_it_tickets`)

#### Scenario: Cobertura 2023-2026 sostenida

- **WHEN** se cuentan las entradas arbitradas del `.bib` con ano entre 2023 y 2026
- **THEN** son al menos 12 y siguen presentes las claves incorporadas por B2
- **AND** cada una es verificable por DOI o URL de editorial/ACL Anthology

#### Scenario: Kappa atribuido a Landis & Koch

- **WHEN** se leen los pasajes que interpretan el coeficiente Kappa en `04-marco-metodologico.tex`
- **THEN** los rangos interpretativos se atribuyen a Landis & Koch (1977)
- **AND** el valor `κ = 0,87` se rotula "casi perfecto", no "sustancial"

#### Scenario: Cero citas huerfanas y cero entradas sin usar

- **WHEN** se cruzan todas las claves citadas contra `Bibliography_base.bib`
- **THEN** no hay citas huerfanas ni entradas sin usar
- **AND** toda entrada resuelve por DOI o landing de editorial

#### Scenario: Sin citas fabricadas

- **WHEN** se buscan las claves `Karchhud2024` y `Mehdi2023` en el arbol de la tesis
- **THEN** no aparecen ni en `Bibliography_base.bib` ni en ningun `.tex`

### Requirement: Ubicación del capítulo de consideraciones éticas y legales

El capítulo de consideraciones éticas y legales SHALL ubicarse dentro del flujo
argumental del cuerpo, antes del capítulo de resultados, y MUST NOT quedar
después de conclusiones y recomendaciones. La reubicación SHALL realizarse
reordenando la línea `\input` correspondiente en `main.tex`, sin renombrar el
archivo fuente. La numeración del capítulo y de los capítulos posteriores SHALL
recalcularse automáticamente, y toda remisión cruzada SHALL seguir resolviéndose
por `\label`/`\autoref`, sin edición manual de números.

#### Scenario: Capítulo legal antes de resultados

- **WHEN** se lee el orden de los `\input` de `sections/` en `main.tex`
- **THEN** `sections/11-aspectos-legales.tex` aparece después de
  `sections/06-implementacion.tex` y antes de `sections/07-resultados.tex`
- **AND** no aparece después de `sections/09-conclusiones.tex` ni de
  `sections/10-recomendaciones.tex`

#### Scenario: Numeración recalculada y referencias intactas

- **WHEN** se compila el documento tras la reubicación
- **THEN** el capítulo legal recibe la numeración correspondiente a su nueva
  posición y los capítulos posteriores se renumeran
- **AND** el log no contiene "undefined reference" ni "multiply defined label"
- **AND** las remisiones a `\autoref{sec:aspectos-legales}` siguen resolviendo,
  sin edición manual de números

#### Scenario: Capítulo fuera de la condición de apéndice encubierto

- **WHEN** se lee el índice general del PDF compilado
- **THEN** el capítulo de consideraciones éticas y legales figura antes de
  resultados
- **AND** no figura como último capítulo del cuerpo, después de las conclusiones
  y las recomendaciones

### Requirement: Glosario de siglas y acrónimos

El documento SHALL incluir una sección "Glosario de siglas y acrónimos" en el
material preliminar, después de los índices y antes del cuerpo. El glosario
SHALL listar en orden alfabético cada sigla o acrónimo usado en el cuerpo con su
expansión completa. Toda sigla presente en `sections/*.tex` SHALL tener una
entrada en el glosario y toda entrada SHALL corresponder a una sigla efectivamente
usada en el cuerpo.

#### Scenario: Cobertura completa del glosario

- **WHEN** se comparan las siglas relevantes del cuerpo (`sections/*.tex`) con
  las entradas del glosario
- **THEN** no queda ninguna sigla del cuerpo sin entrada
- **AND** no queda ninguna entrada del glosario sin uso en el cuerpo

#### Scenario: Ubicación y formato del glosario

- **WHEN** se lee el índice general y el material preliminar del PDF
- **THEN** el glosario aparece listado después de los índices
- **AND** cada entrada presenta la sigla y su expansión completa, en orden
  alfabético

#### Scenario: Glosario sin romper la compilación ni el presupuesto de referencias

- **WHEN** se compila el documento con el glosario agregado
- **THEN** el log no contiene "undefined reference" ni "multiply defined label"
- **AND** no se introducen glosarios automáticos que requieran un paso de build
  adicional fuera del `latexmk` vigente

### Requirement: Marco metrico unificado en los capitulos de la tesis

El capitulo de marco metodologico SHALL declarar si la tarea se evalua como
monoetiqueta o multietiqueta, y el capitulo de resultados SHALL presentar la
exactitud estricta, la macro-F1 (cinco clases y cuatro clases estimables), el
micro-F1, la subset accuracy y el Hamming loss dentro de un unico marco que
declare, para cada metrica, su referencia de verdad y su relacion con las demas.
El documento MUST NOT presentar el micro-F1 ni las metricas de conjunto como
equivalentes de la exactitud de etiqueta unica, y SHALL explicitar la
penalizacion estructural que subset accuracy y Hamming loss imponen sobre una
salida forzada a una etiqueta. La comparacion con la literatura SHALL declarar la
diferencia de tarea (monoetiqueta en la literatura frente a multietiqueta
referenciada en este trabajo) cuando se contrasten exactitudes.

#### Scenario: Paradigma declarado en metodologia

- **WHEN** se lee la subseccion de analisis de datos del marco metodologico
- **THEN** se declara que la referencia de verdad del corpus es multietiqueta y que la salida del clasificador es una etiqueta principal
- **AND** se enuncian las metricas primarias monoetiqueta y las secundarias multietiqueta

#### Scenario: Marco unico en resultados

- **WHEN** se lee la subseccion de metricas del capitulo de resultados
- **THEN** la exactitud estricta, la macro-F1, el micro-F1, la subset accuracy y el Hamming loss aparecen en un solo marco con su referencia declarada
- **AND** el micro-F1 no se presenta como equivalente de la exactitud estricta

#### Scenario: Comparacion con la literatura matizada por tarea

- **WHEN** se compara la exactitud propia (`73,5 %`) con exactitudes de la literatura
- **THEN** el texto declara la diferencia de tarea (monoetiqueta frente a multietiqueta referenciada)
- **AND** no presenta el micro-F1 como una exactitud directamente comparable

### Requirement: Intervalos de confianza del kappa y por clase en la tesis

El marco metodologico y el capitulo de resultados SHALL reportar el intervalo de
confianza del coeficiente kappa de doble etiquetado y los intervalos de confianza
de las metricas por clase (precision, sensibilidad, F1), declarando el nivel de
confianza y el procedimiento de estimacion. El documento SHALL declarar como no
estimable la clase con soporte unitario (`Bases de Datos`, `n = 1`) y SHALL
excluirla del macro-F1 de umbral, conservando el macro-F1 de cinco clases como
valor informativo. Cuando la incertidumbre del kappa no sea computable desde las
fuentes disponibles, el texto SHALL declararlo de forma explicita como limitacion.

#### Scenario: IC del kappa reportado

- **WHEN** se lee el pasaje del doble etiquetado en metodologia o discusion
- **THEN** el kappa `0,87` se acompana de su intervalo de confianza con el nivel y el metodo declarados, o de la declaracion de que no es computable desde las fuentes permitidas
- **AND** el rotulo interpretativo sigue siendo "casi perfecto" (Landis & Koch)

#### Scenario: IC por clase reportado

- **WHEN** se lee la tabla de metricas por clase en resultados
- **THEN** cada clase estimable reporta su IC de precision, sensibilidad y F1
- **AND** la clase `Bases de Datos` figura como no estimable y sin IC

#### Scenario: Exclusion de la clase no estimable del umbral

- **WHEN** se lee el macro-F1 asociado al umbral de clasificacion
- **THEN** el macro-F1 de umbral se reporta sobre las cuatro clases estimables (`0,6508`)
- **AND** el macro-F1 de cinco clases (`0,5207`) se conserva como valor informativo
- **AND** el `0,0000` de `Bases de Datos` no se presenta como evidencia de desempeno

### Requirement: Conteo unico de entidades del modelo de datos

La tesis SHALL declarar un unico numero de entidades principales del modelo de
datos, igual a **siete**, en todos los pasajes que lo mencionan
(`05-arquitectura.tex`, `06-implementacion.tex`, `12-anexos.tex` y la Tabla
`tab:entidades`). El numero canonico SHALL derivarse de la Tabla `tab:entidades` y
del ORM versionado, que incluye `directorio_empleado`. El texto MUST NOT declarar
"seis entidades" en ningun pasaje.

#### Scenario: Conteo unico de entidades en el cuerpo

- **WHEN** se busca "seis entidades" o "siete entidades" en los `.tex` y en el PDF compilado
- **THEN** la unica declaracion vigente es "siete entidades principales"
- **AND** no queda ninguna ocurrencia de "seis entidades" como conteo del modelo final

#### Scenario: Coherencia con la tabla de entidades

- **WHEN** se compara el conteo declarado con las filas de la Tabla `tab:entidades`
- **THEN** el numero de filas de entidades principales es siete
- **AND** incluye `incidente`, `sector`, `estado`, `canal_origen`, `clasificacion_log`, `users` y `directorio_empleado`

### Requirement: Conteo unico de etapas y nodos del flujo N8N

La tesis SHALL declarar un unico numero de etapas funcionales del flujo N8N, igual
a **siete**, derivado de la agrupacion funcional de `n8n/workflow.json`, en
`06-implementacion.tex` y `12-anexos.tex`. Cuando el texto describa el patron de
procesamiento por canal, SHALL rotularlo explicitamente como tal y MUST NOT
presentarlo como el conteo total de etapas del flujo. La tesis SHALL declarar el
conteo de nodos como **29 operativos mas 3 notas adhesivas (32 nodos totales)**.
El texto MUST NOT declarar "26 operativos" ni presentar "29" como el total de
nodos.

#### Scenario: Conteo unico de etapas del flujo

- **WHEN** se leen el Capitulo 6 y el Anexo del flujo en el PDF compilado
- **THEN** ambos declaran siete etapas funcionales del flujo
- **AND** no se presenta "cinco etapas" como el conteo total de etapas del flujo

#### Scenario: Conteo de nodos operativos y totales

- **WHEN** se busca el conteo de nodos del flujo en los `.tex` y en el PDF compilado
- **THEN** el conteo declarado es 29 nodos operativos mas 3 notas adhesivas, es decir 32 nodos totales
- **AND** no aparece "26 operativos" ni "29 nodos" presentado como el total

#### Scenario: Conteo verificable contra el flujo exportado

- **WHEN** se cuentan los nodos de `n8n/workflow.json` por tipo
- **THEN** el total es 32, de los cuales 3 son `stickyNote` y 29 son operativos
- **AND** el conteo declarado en la tesis coincide con ese resultado

### Requirement: Nombre canonico del SDK de Google

La tesis SHALL nombrar el paquete del SDK de Google como **`google-genai`** (SDK
unificado) en todos sus pasajes, incluido el Anexo de parametros de inferencia. El
documento MUST NOT presentar `google-generativeai` como el paquete utilizado. La
fuente de verdad del nombre y del rango de version es
`App/Backend/requirements.txt` (`google-genai>=2.20.0,<3`).

#### Scenario: Nombre unico del SDK

- **WHEN** se busca `google-generativeai` o `google-genai` en los `.tex` y en el PDF compilado
- **THEN** la unica denominacion vigente del paquete usado es `google-genai`
- **AND** no queda `google-generativeai` presentado como el SDK invocado

#### Scenario: Coherencia con requirements.txt

- **WHEN** se compara el paquete declarado en la tesis con `App/Backend/requirements.txt`
- **THEN** ambos coinciden en `google-genai`
- **AND** el rango de version declarado es compatible con `>=2.20.0,<3`

### Requirement: Protocolo de revisión de literatura declarado y trazable

El capítulo de estado del arte (`03-estado-del-arte.tex`) SHALL declarar el
protocolo con el que se construyó la revisión: bases de datos o repositorios
consultados, cadenas de búsqueda, criterios de inclusión y de exclusión, período
cubierto y fecha de corte. El protocolo SHALL registrarse además en una bitácora
de búsqueda versionada bajo `docs/Tesis/Correcciones/`, con una entrada por
consulta (base, cadena, fecha y resultado). El protocolo descrito en el texto MUST
ser consistente con la bitácora: no puede declararse una base, cadena o criterio
que la bitácora no registre, y la bitácora MUST NOT contener entradas que el texto
no mencione.

#### Scenario: Protocolo presente en el capítulo

- **WHEN** se lee la revisión de literatura en `03-estado-del-arte.tex`
- **THEN** el texto enuncia las bases o repositorios consultados, las cadenas de búsqueda, los criterios de inclusión y exclusión, el período y la fecha de corte
- **AND** la formulación permite a un lector reproducir la búsqueda

#### Scenario: Bitácora de búsqueda reproducible

- **WHEN** se lee la bitácora de búsqueda bajo `docs/Tesis/Correcciones/`
- **THEN** cada consulta registra base, cadena, fecha y resultado
- **AND** el conjunto de bases, cadenas y criterios coincide con los declarados en el capítulo

### Requirement: Afirmación de vacancia acotada al alcance revisado

Toda afirmación de vacancia o inexistencia en el estado del arte (en particular
"no existe artículo arbitrado 2023-2026 que evalúe Google Gemini sobre tickets de
soporte en español") SHALL formularse de manera relativa al alcance efectivamente
revisado: SHALL declarar las fuentes o bases consultadas, las cadenas empleadas y
la fecha de corte, y SHALL enmarcarse como "en las fuentes consultadas hasta la
fecha de corte". El documento MUST NOT presentar la vacancia como una inexistencia
absoluta ni global. Cuando la vacancia se reutilice como motivación en otra
sección, esa mención SHALL remitir al alcance declarado en el estado del arte.

#### Scenario: Vacancia relativa y con alcance declarado

- **WHEN** se lee la afirmación de vacancia en `03-estado-del-arte.tex`
- **THEN** declara las bases consultadas, las cadenas de búsqueda y la fecha de corte
- **AND** la formula como relativa al alcance revisado, no como inexistencia absoluta

#### Scenario: Reutilización de la vacancia acotada

- **WHEN** la vacancia se usa como motivación en otra sección del documento
- **THEN** la mención remite al alcance declarado en el estado del arte
- **AND** no repite la vacancia como una afirmación de inexistencia sin acotar

### Requirement: Subsección teórica de human-in-the-loop con fuentes

El marco teórico (`02-marco-teorico.tex`) SHALL incluir una subsección sobre
human-in-the-loop que defina el concepto, distinga grados de autonomía (desde la
supervisión total hasta la operación autónoma con revisión selectiva) y fundamente
cada aserción con al menos una fuente citada. Al menos una fuente SHALL abordar la
interacción humano-IA o el aprendizaje con intervención humana. El texto MUST NOT
introducir el término sin definición ni sostener los grados de autonomía como
aseveración propia sin respaldo.

#### Scenario: Definición y grados de autonomía

- **WHEN** se lee la subsección de human-in-the-loop en `02-marco-teorico.tex`
- **THEN** el texto define el concepto
- **AND** distingue al menos dos grados de autonomía de forma explícita

#### Scenario: Aserciones respaldadas por fuentes

- **WHEN** se lee la subsección de human-in-the-loop
- **THEN** la definición y los grados de autonomía se apoyan en al menos una cita por aserción principal
- **AND** cada clave citada existe como entrada en `Bibliography_base.bib` y resuelve por DOI o página de aterrizaje

#### Scenario: Recuento de ejes consistente

- **WHEN** se lee el párrafo introductorio del marco teórico
- **THEN** el número de ejes temáticos declarado coincide con el número de subsecciones presentes
- **AND** la subsección de human-in-the-loop queda incluida en ese recuento

### Requirement: Acentuación normalizada del manuscrito

Los 14 archivos `.tex` de `docs/Tesis/v9 (IA)/paper/sections/` SHALL presentar el
texto español acentuado conforme a las reglas ortográficas del español. La
normalización SHALL aplicarse a la prosa (cuerpo, encabezados, pies de página,
pies de figura y tabla, celdas de texto) incluyendo el texto dentro de argumentos
de comandos portadores de texto (`\section{}`, `\subsection{}`, `\caption{}`,
`\textbf{}`, `\emph{}`, `\item`, `\footnote{}`). El documento MUST NOT modificar
tokens protegidos: las cinco cadenas canónicas de categorías (`Seguridad
Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de
Datos`, `Sistemas`), las claves de `\label{}`/`\ref{}`/`\autoref{}`/`\cref{}`,
las claves de `\cite{}`/`\textcite{}`/`\parencite{}`, las rutas de
`\input{}`/`\includegraphics{}`/`\bibliography{}` y las rutas de repositorio en
prosa (`docs/Tesis/`, `evaluation/`, `data/`, `App/Backend`), el contenido de
`verbatim`/`lstlisting`/`\verb`, las URLs y DOI, la matemática, los nombres de
comandos LaTeX y las palabras ya acentuadas. Ninguna corrección SHALL
des-acentuar texto, duplicar tildes ni alterar cifras. El cambio MUST NOT editar
`Bibliography_base.bib`.

#### Scenario: Prosa acentuada
- **WHEN** se busca en `sections/*.tex` una forma sin tilde de una palabra que la requiere (por ejemplo "clasificacion", "informacion", "metodologico", "Capitulo", "Introduccion")
- **THEN** no queda ninguna ocurrencia en prosa sin acentuar
- **AND** el texto ya acentuado permanece sin cambios (no se des-acentúa ni se duplica la tilde)

#### Scenario: Tokens protegidos intactos
- **WHEN** se comparan antes y después las cinco cadenas canónicas de categorías, las claves de `\label`/`\ref`/`\autoref`, las claves de citas y las rutas de `\input`/`\includegraphics`
- **THEN** el conjunto de tokens es idéntico
- **AND** ninguna cadena de categoría incorpora tilde

#### Scenario: Pares sensibles preservados
- **WHEN** se inspeccionan las ocurrencias de `hipótesis` y `síntesis`
- **THEN** se conservan exactamente acentuadas como corresponde
- **AND** no aparecen como `hipotesis`/`sintesis` ni con tilde duplicada

#### Scenario: Sin residuos de la herramienta
- **WHEN** se revisa el árbol de trabajo tras aplicar la normalización
- **THEN** no existen archivos `.tex.bak` nuevos
- **AND** ningún archivo fuera de `docs/Tesis/v9 (IA)/paper/sections/` fue modificado

### Requirement: Presupuesto de palabras del resumen en español

El resumen en español (`00-resumen.tex`) SHALL tener como máximo 250 palabras de
prosa. La reducción SHALL conservar el problema, el método y diseño (200 casos
pareados), los resultados clave (61,6~s a 17,76~s, reducción del 71,2~\%, \(W =
363\), \(r = 0,9639\), exactitud 73,5~\%, macro-F1 0,5207, Kappa de Cohen 0,87) y
la conclusión. El resumen MUST NOT reintroducir valores retirados por c-107 (la
intervención humana del 9,5~\% y el universo calendario 3.700) ni presentar la
hipótesis principal como plenamente confirmada.

#### Scenario: Longitud del resumen
- **WHEN** se cuenta el número de palabras de prosa del cuerpo del resumen en español (excluyendo comandos LaTeX y la línea "Palabras clave")
- **THEN** el conteo es como máximo 250 palabras

#### Scenario: Cifras clave conservadas
- **WHEN** se lee el resumen reducido
- **THEN** aparecen 200 casos, 61,6~s, 17,76~s, 71,2~\%, \(W = 363\), \(r = 0,9639\), 73,5~\% y 0,5207
- **AND** el resumen no presenta la hipótesis principal como plenamente confirmada

#### Scenario: Sin valores retirados
- **WHEN** se busca "9,5 %" o "3.700" en el resumen y el abstract
- **THEN** no aparecen como resultado vigente
- **AND** el texto es coherente con los valores canónicos propagados por c-107

### Requirement: Desdoblamiento de la hipótesis principal en sub-hipótesis contrastables

La introducción (`01-introduccion.tex`, §Hipótesis de trabajo) SHALL formular la
hipótesis principal desdoblada en tres sub-hipótesis contrastables: (a) tiempo de
registro, (b) proporción de intervención humana y (c) exactitud o F1 macro. Cada
sub-hipótesis SHALL enunciar su propio contraste y su criterio de falsación
explícito. El contraste de la sub-hipótesis temporal SHALL ser el contraste no
paramétrico `H0`/`H1` sobre las medianas del tiempo de registro. El de exactitud o
F1 SHALL formularse como umbral de desempeño verificado contra la exactitud
observada y su intervalo de confianza de Wilson, sin invocar la zona de rechazo
del contraste de tiempos. El documento MUST NOT presentar la hipótesis principal
como una conjunción indivisible que se confirme o refute como bloque.

#### Scenario: Tres sub-hipótesis con contraste propio

- **WHEN** se lee la subsección de hipótesis de trabajo en `01-introduccion.tex`
- **THEN** se distinguen tres sub-hipótesis: tiempo, intervención humana y exactitud/F1
- **AND** cada una enuncia su propio contraste

#### Scenario: Criterio de falsación explícito por sub-hipótesis

- **WHEN** se lee cada sub-hipótesis
- **THEN** declara la condición que la falsaría
- **AND** la sub-hipótesis de exactitud/F1 usa el umbral `85 %`/`0,85` como criterio de desempeño verificado contra el intervalo de confianza, no como zona de rechazo

#### Scenario: Sin conjunción indivisible

- **WHEN** se lee la formulación de la hipótesis principal
- **THEN** no se enuncia como una única conjunción de mecanismo y umbral de desempeño
- **AND** no se declara confirmada o refutada en bloque

### Requirement: Reformulación del objetivo general como evaluación de viabilidad y desempeño

El objetivo general (`01-introduccion.tex`, §Objetivo general) SHALL formularse en
términos de evaluar la viabilidad y el desempeño de la automatización del registro
inicial de incidentes, y SHALL presentar el desarrollo e implementación del sistema
como el medio para esa evaluación, no como el objetivo. El documento MUST NOT
formular el objetivo general en clave exclusiva de desarrollo ("desarrollar e
implementar").

#### Scenario: Objetivo general en clave de evaluación

- **WHEN** se lee el objetivo general en `01-introduccion.tex`
- **THEN** se enuncia en términos de evaluar viabilidad y desempeño
- **AND** no se enuncia como "desarrollar e implementar"

#### Scenario: Desarrollo como medio

- **WHEN** se lee la relación entre el objetivo y la construcción del sistema
- **THEN** el desarrollo y la implementación se presentan como medio para la evaluación
- **AND** no como el objetivo declarado

### Requirement: Separación entre la implementación y el umbral de desempeño del segundo objetivo

El segundo objetivo específico (`01-introduccion.tex`, §Objetivos específicos)
SHALL separar la acción de implementar el clasificador automático del umbral de
desempeño (`exactitud ≥ 85 %`, `F1 macro ≥ 0,85`), que SHALL presentarse como
criterio de éxito contingente verificable contra el resultado observado y su
intervalo de confianza, no como parte constitutiva del objetivo. El documento
MUST NOT enunciar el umbral como una meta que el objetivo incluya por definición.

#### Scenario: Acción de implementación separada del umbral

- **WHEN** se lee el segundo objetivo específico
- **THEN** la acción de implementar el clasificador se enuncia separada del umbral de desempeño
- **AND** el umbral no figura como parte definitoria del objetivo

#### Scenario: Umbral como criterio de éxito contingente

- **WHEN** se lee el tratamiento del umbral `85 %`/`0,85`
- **THEN** se presenta como criterio de éxito verificable contra la exactitud observada y su intervalo de confianza
- **AND** su estado no alcanzado se declara en las conclusiones

### Requirement: Quinto objetivo verificable y reproducible

El quinto objetivo específico (`01-introduccion.tex`, §Objetivos específicos)
SHALL reescribirse en clave verificable y reproducible: documentar la arquitectura,
los procedimientos de despliegue y los resultados de modo que una tercera parte
pueda replicarlos. El documento MUST NOT conservar el calificador "exhaustivamente"
ni formulaciones cuyo cumplimiento no admita verificación.

#### Scenario: Sin "exhaustivamente"

- **WHEN** se lee el quinto objetivo específico
- **THEN** no contiene el término "exhaustivamente" ni otro calificador no contrastable
- **AND** su cumplimiento es verificable

#### Scenario: En clave reproducible

- **WHEN** se lee el quinto objetivo específico
- **THEN** se enuncia en términos de reproducibilidad de los artefactos y procedimientos
- **AND** es coherente con el aporte documental descrito en las conclusiones

### Requirement: Objetivo específico de análisis de errores y calibración de la confianza

La introducción SHALL agregar un objetivo específico referido al análisis de los
errores de clasificación y a la calibración de la confianza de las predicciones,
alineado con los aportes del Capítulo de resultados (tipología de errores y bandas
de confianza). El objetivo SHALL ser verificable contra los artefactos del
repositorio.

#### Scenario: Objetivo agregado

- **WHEN** se leen los objetivos específicos
- **THEN** existe uno referido al análisis de errores y a la calibración de la confianza
- **AND** es verificable contra los artefactos del repositorio

#### Scenario: Alineado con el Capítulo de resultados

- **WHEN** se compara el objetivo con los aportes del Capítulo de resultados
- **THEN** se corresponde con la tipología de errores y las bandas de confianza
- **AND** no introduce una línea de trabajo ajena a la evidencia presentada

### Requirement: Tabla de objetivos, cumplimiento y evidencia en las conclusiones

Las conclusiones (`09-conclusiones.tex`) SHALL incluir una tabla que enumere cada
objetivo (general y específicos), su grado de cumplimiento y la evidencia que lo
respalda (sección o métrica). La tabla SHALL declarar el segundo objetivo como no
alcanzado y SHALL ser coherente con el estado declarado de la hipótesis principal.

#### Scenario: Tabla presente

- **WHEN** se leen las conclusiones
- **THEN** se incluye una tabla de objetivos, cumplimiento y evidencia
- **AND** abarca el objetivo general y todos los específicos

#### Scenario: Cumplimiento y evidencia por objetivo

- **WHEN** se lee cada fila de la tabla
- **THEN** declara el grado de cumplimiento y la evidencia (sección o métrica) que lo respalda
- **AND** el segundo objetivo figura como no alcanzado

#### Scenario: Coherencia con el estado de la hipótesis

- **WHEN** se compara la tabla con la declaración del estado de la hipótesis principal
- **THEN** ambos son coherentes (tiempo confirmado, clasificación refutada)
- **AND** no se declara alcanzado el umbral de clasificación

### Requirement: Fundamentación de los conceptos de BPA e iPaaS

El capítulo de marco teórico (`02-marco-teorico.tex`, sección 2.3) SHALL fundamentar
con una cita verificable, o reformular de forma explícita como glosa propia, las
definiciones de "automatización de procesos empresariales" (BPA) y de "plataformas de
integración como servicio" (iPaaS). El texto MUST NOT presentar esas definiciones como
aserciones sin fuente. Toda cita nueva SHALL existir como entrada en
`Bibliography_base.bib` y resolver por DOI o página de aterrizaje del editor.

#### Scenario: Definiciones fundamentadas o reformuladas como glosa propia

- **WHEN** se lee la sección 2.3 del PDF compilado
- **THEN** la definición de BPA y la de iPaaS están respaldadas por una cita verificable o rotuladas explícitamente como glosa propia
- **AND** ninguna de las dos queda enunciada como afirmación sin fuente ni como atribución a un tercero sin cita

#### Scenario: Citas nuevas verificables

- **WHEN** se inspeccionan las citas incorporadas en la sección 2.3
- **THEN** cada clave citada existe como entrada en `Bibliography_base.bib`
- **AND** cada entrada nueva incluye `author`, `title`, `year` y el campo de publicación más `doi` o `url`, y resuelve por DOI o página de aterrizaje

### Requirement: Formulación jurídica exacta de la soberanía sobre los datos

La sección 1.7 (`01-introduccion.tex`) SHALL sustituir la atribución del "principio de
soberanía digital" a la Ley 25.326 por la formulación jurídica que la ley efectivamente
enuncia (control sobre los datos personales y su tratamiento conforme a la normativa de
protección de datos). El texto MUST NOT afirmar que la Ley 25.326 promueve la "soberanía
digital", por ser un principio que una ley de protección de datos no enuncia.

#### Scenario: Atribución imprecisa eliminada

- **WHEN** se busca la expresión "soberanía digital" en `01-introduccion.tex` y en el PDF compilado
- **THEN** no aparece atribuida a la Ley 25.326 como principio promovido por esa norma
- **AND** el pasaje enuncia el control sobre los datos personales y su tratamiento conforme a la normativa de protección de datos

#### Scenario: Formulación coherente con la fuente legal citada

- **WHEN** se lee el pasaje corregido de la sección 1.7
- **THEN** la formulación jurídica exacta se apoya en la entrada vigente `Ley25326_2000`
- **AND** no se atribuye a la ley un principio que su texto no contiene

### Requirement: Cita canónica de la definición de alucinación

La sección 2.4 (`02-marco-teorico.tex`) SHALL respaldar la definición de "alucinación"
con una cita canónica verificable sobre el fenómeno en modelos generativos de lenguaje.
La cita SHALL existir como entrada en `Bibliography_base.bib` y resolver por DOI. El
texto MUST NOT presentar la definición como aserción sin fuente.

#### Scenario: Definición con cita canónica

- **WHEN** se lee la definición de "alucinación" en la sección 2.4 del PDF compilado
- **THEN** la definición cita una referencia canónica sobre el fenómeno
- **AND** la afirmación no queda sostenida como aserción sin fuente

#### Scenario: Entrada verificable por DOI

- **WHEN** se inspecciona la entrada incorporada para la definición de alucinación
- **THEN** la entrada existe en `Bibliography_base.bib` con metadatos completos
- **AND** su DOI resuelve a la publicación real

### Requirement: Alcance acotado y justificado del eje de reconocimiento automático del habla

La sección 2.5 (`02-marco-teorico.tex`) SHALL recortarse al mínimo conceptual necesario
o SHALL justificar explícitamente por qué se conserva el eje de reconocimiento
automático del habla (ASR) pese a que la transcripción efectiva la provee un servicio
externo. Si el eje se conserva, el texto SHALL declarar su función como marco conceptual
del canal telefónico y SHALL NOT desarrollarlo como si fuera un componente integrado a
la implementación. El texto MUST NOT presentar el ASR como un eje que el sistema
efectivamente integra.

#### Scenario: Eje recortado o justificado

- **WHEN** se lee la sección 2.5 del PDF compilado
- **THEN** el eje se recorta al mínimo conceptual o el texto justifica explícitamente su permanencia como marco del canal telefónico
- **AND** se declara que la transcripción efectiva la provee un servicio externo y no el sistema desarrollado

#### Scenario: Sin desarrollo desproporcionado respecto de su uso

- **WHEN** se compara la extensión del eje de ASR con la de los ejes efectivamente usados en la implementación
- **THEN** el eje no se desarrolla como un componente del sistema propuesto
- **AND** no se afirma que el ASR permita automatizar la captura del canal telefónico del sistema

### Requirement: Terminología correcta de la trazabilidad

El documento SHALL emplear el término "trazabilidad auditable". Ningún archivo de sección
de `paper/sections/` MUST contener la expresión "trazabilidad auditiva".

#### Scenario: Término corregido en todo el cuerpo

- **WHEN** se busca la expresión "trazabilidad auditiva" en `paper/sections/*.tex` y en el PDF compilado
- **THEN** no hay coincidencias
- **AND** donde correspondía se emplea "trazabilidad auditable"

### Requirement: Afirmaciones sobre plataformas comerciales respaldadas o reformuladas como observación propia

Toda afirmación de contexto sobre el mercado o la adopción de plataformas
comerciales de mesa de ayuda en el estado del arte (`03-estado-del-arte.tex`)
SHALL estar respaldada por una referencia formal verificable o, en su defecto,
reformulada como observación propia documentada que explicite su base (por
ejemplo, la documentación pública de las plataformas consultada en una fecha
declarada). El documento MUST NOT presentar como hecho establecido, sin respaldo,
afirmaciones de dominancia de mercado, crecimiento de la adopción o superioridad
de una solución sobre el segmento. Cuando la afirmación se respalde con un informe
de mercado, su entrada bibliográfica SHALL agregarse de forma aditiva en
`Bibliography_base.bib` y SHALL resolver por DOI o página de aterrizaje; el
documento MUST NOT alterar entradas existentes ni las tipadas por c-104.

#### Scenario: Afirmación de dominancia de mercado acotada

- **WHEN** se lee en `03-estado-del-arte.tex` la afirmación sobre el segmento de soluciones comerciales ("dominado por plataformas integrales")
- **THEN** la afirmación cita una referencia formal verificable o se enuncia como observación propia con su base declarada
- **AND** no queda formulada como hecho de mercado sin respaldo

#### Scenario: Afirmación de crecimiento de la adopción acotada

- **WHEN** se lee la afirmación sobre el crecimiento sostenido de la adopción de capacidades de IA en plataformas comerciales
- **THEN** la afirmación cita una referencia formal verificable o se reformula como observación propia acotada a lo documentado
- **AND** no se sostiene como tendencia cuantitativa sin fuente

#### Scenario: Entrada bibliográfica nueva aditiva y resoluble

- **WHEN** se agrega un informe de mercado para respaldar una afirmación comercial
- **THEN** la entrada se agrega sin modificar entradas existentes y sigue la convención de claves `ApellidoAnio_palabra_clave`
- **AND** resuelve por DOI o página de aterrizaje

### Requirement: Umbral de migración a clasificador supervisado justificado o declarado indicativo

Toda mención del umbral de casos necesarios para migrar a un clasificador
supervisado entrenado con corpus propio SHALL estar justificada por un cálculo de
potencia o por una referencia a un régimen de aprendizaje documentado, o bien
SHALL declararse explícitamente como valor indicativo y no como umbral derivado.
El tratamiento SHALL ser consistente en todas las apariciones del documento
(`10-recomendaciones.tex`, `08-discusion.tex` y `12-anexos.tex`). El documento
MUST NOT repetir una cifra concreta como umbral fundado sin justificación
empírica.

#### Scenario: Umbral justificado o declarado indicativo

- **WHEN** se lee la recomendación de migración a un clasificador supervisado
- **THEN** el umbral se justifica con un cálculo de potencia o una referencia documentada, o se declara como valor indicativo
- **AND** no se presenta como umbral fundado sin sustento

#### Scenario: Consistencia entre las apariciones del umbral

- **WHEN** se comparan las menciones del umbral en `10-recomendaciones.tex`, `08-discusion.tex` y `12-anexos.tex`
- **THEN** todas emplean el mismo tratamiento (justificado o indicativo)
- **AND** no queda una mención con una formulación distinta de las demás

### Requirement: Priorización de las líneas de trabajo futuro sobre los defectos medidos

El capítulo de recomendaciones (`10-recomendaciones.tex`) SHALL priorizar
explícitamente las líneas de trabajo futuro que atacan los defectos medidos en el
estudio: la calibración del gate de confianza, la incorporación de un clasificador
supervisado con corpus propio y la corrección de la medición de intervención
humana. La priorización SHALL distinguir esas líneas de las extensiones genéricas
(canales adicionales, paneles, base de conocimientos) y SHALL ser coherente con
las limitaciones reconocidas en la discusión.

#### Scenario: Líneas prioritarias declaradas

- **WHEN** se lee la introducción o el cierre del capítulo de recomendaciones
- **THEN** el texto declara explícitamente cuáles líneas futuras son prioritarias
- **AND** entre ellas figuran la calibración del gate, el clasificador supervisado y la corrección de la medición de intervención

#### Scenario: Distinción respecto de las líneas genéricas

- **WHEN** se leen las líneas de canales adicionales, paneles o base de conocimientos
- **THEN** se presentan como extensiones no prioritarias o subordinadas a las líneas que atacan los defectos medidos
- **AND** la priorización es coherente con las limitaciones de la discusión

### Requirement: Propagación de la dependencia entre etiquetadores y operadores

La tesis SHALL reflejar en las conclusiones la dependencia declarada en el marco
metodológico entre los analistas etiquetadores de la verdad de referencia y los
operadores del brazo manual (las mismas personas). Esa dependencia SHALL figurar
entre las limitaciones del estudio en la discusión, no solo entre las amenazas a
la validez del capítulo metodológico. Las conclusiones MUST NOT calificar el
diseño experimental como «riguroso» ni presentarlo como plenamente independiente
sin matizar la dependencia entre etiquetadores y operadores; la afirmación de
aporte empírico SHALL quedar acotada por la independencia limitada del referente
de comparación.

#### Scenario: Limitación declarada en la discusión

- **WHEN** se lee la subsección de limitaciones del estudio de la discusión
- **THEN** la dependencia entre los etiquetadores de la verdad de referencia y los operadores del brazo manual figura entre las limitaciones
- **AND** la limitación es coherente con la declaración de la misma dependencia en el capítulo metodológico

#### Scenario: Limitación reflejada en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** la dependencia entre etiquetadores y operadores se refleja como un límite del diseño
- **AND** la afirmación de aporte empírico queda acotada por la independencia limitada del referente de comparación

#### Scenario: Sin sobreafirmación de rigor del diseño

- **WHEN** se busca en las conclusiones un calificativo de rigor sobre el diseño experimental
- **THEN** el diseño no se describe como «riguroso» ni como plenamente independiente sin el matiz de la dependencia entre etiquetadores y operadores
- **AND** el sobreclaim señalado por la dimensión 7 del dictamen no subsiste

### Requirement: Reducción sin pérdida de contenido científico

La reducción de páginas SHALL preservar la integridad científica del documento.
El change MUST NOT eliminar ni alterar: contenido científico (afirmaciones,
argumentos, interpretaciones y análisis), las figuras y tablas requeridas por el
conjunto de changes (incluidas las ocho figuras de c-80 y las tablas con su línea
de fuente), los números canónicos (exactitud 73,5 %, macro-F1 0,5207, reducción
71,2 %, W=363, r=0,9639, κ=0,87, universo 2.646, horas-persona 32,2 h), ni las
referencias bibliográficas. Las palancas admisibles son de forma: pasajes
duplicados, leyendas sobre-extendidas, listas redundantes, tamaño del glosario,
espaciado y compactación de anexos.

#### Scenario: Cifras canónicas intactas

- **WHEN** se busca en el PDF reducido cada número canónico (73,5 %, 0,5207, 71,2 %, W=363, 0,9639, 0,87, 2.646, 32,2 h)
- **THEN** todos siguen presentes con el mismo valor
- **AND** no se introducen cifras nuevas ni se retiran las existentes

#### Scenario: Figuras y tablas requeridas preservadas

- **WHEN** se inspecciona el PDF reducido
- **THEN** las ocho figuras y las nueve tablas del change set siguen renderizando
- **AND** ninguna figura o tabla requerida fue eliminada ni recortada

#### Scenario: Correcciones previas no revertidas

- **WHEN** se compara el manuscrito reducido contra la versión de partida
- **THEN** las correcciones de c-102..c-115 (números canónicos, cifras retiradas, acentuación, orden de capítulos, glosario y marco teórico) permanecen aplicadas
- **AND** no se reintroduce ningún valor retirado (9,5 %, 3.700, "Operaciones", W=0)

### Requirement: Verificación de compilación tras la reducción

La reducción SHALL verificarse sobre el PDF compilado. La compilación con XeLaTeX
SHALL producir `main.pdf` sin errores fatales, con cero referencias indefinidas y
cero etiquetas duplicadas en el registro. El conteo de páginas y la ausencia de
referencias indefinidas SHALL registrarse como evidencia de la verificación.

#### Scenario: Compilación sin errores fatales

- **WHEN** se compila `main.tex` con `latexmk -xelatex` (imagen `texlive-thesis`)
- **THEN** se produce `main.pdf` sin errores fatales
- **AND** el registro no contiene "undefined reference" ni "multiply defined label"

#### Scenario: Evidencia de verificación registrada

- **WHEN** se cierra el change
- **THEN** el conteo de páginas (`pdfinfo`) y el resultado de la verificación de referencias quedan registrados en las tareas
- **AND** el conteo es 100 o menos con cero referencias indefinidas

### Requirement: Tabla comparativa de trabajos académicos de clasificación de tickets

La subsección "Trabajos académicos previos sobre clasificación de tickets"
(`\label{subsec:trabajos-academicos}`) de `03-estado-del-arte.tex` SHALL presentar
una tabla comparativa de trabajos académicos con las columnas `trabajo | enfoque |
corpus/idioma | métrica reportada | condición`. La tabla SHALL reemplazar la
oración que agrupa varios trabajos en `03:32` (Paket et al., Liu et al., Zangari et
al., Colavito et al.) o complementarla, de modo que la información de corpus,
métrica y condición de cada trabajo quede expuesta en la grilla. La tabla MUST NOT
duplicar la tabla comercial `tab:comparativa`, que compara soluciones comerciales
(Zendesk, Freshdesk, Jira, ServiceNow, osTicket) y no trabajos académicos. Cada
fila SHALL reportar corpus, métrica y condición cuando la fuente documentada las
establezca.

#### Scenario: Tabla con las columnas requeridas

- **WHEN** se lee la subsección `subsec:trabajos-academicos` en el PDF compilado
- **THEN** existe una tabla con las columnas trabajo, enfoque, corpus/idioma, métrica reportada y condición
- **AND** la tabla tiene una fila por cada trabajo académico incluido, con al menos una fila de datos

#### Scenario: Los agrupamientos quedan expuestos

- **WHEN** se comparan los trabajos agrupados en `03:32` contra las filas de la tabla
- **THEN** cada trabajo de ese agrupamiento aparece como una fila propia con su corpus/idioma, métrica y condición
- **AND** la afirmación genérica que los agrupaba deja de ser la única fuente de su comparación

#### Scenario: Sin duplicar la tabla comercial

- **WHEN** se inspeccionan las dos tablas del Capítulo 3
- **THEN** `tab:comparativa` sigue comparando soluciones comerciales
- **AND** la tabla nueva compara trabajos académicos y no repite las filas comerciales

### Requirement: Procedencia de datos y regla de dato no reportado

Toda celda de la tabla comparativa SHALL provenir de la prosa de la tesis, de una
entrada de `Bibliography_base.bib` o de una fuente verificable accesible por DOI o
página de aterrizaje. Donde un dato (corpus, idioma, métrica o condición) no pueda
establecerse con una fuente, la celda MUST declararse explícitamente como "no
reportado en el alcance revisado", en consistencia con la regla de vacancia acotada
de c-110. El documento MUST NOT fabricar corpus, métricas ni condiciones, ni
atribuir a un trabajo un resultado que su fuente no reporte. El change MUST NOT
agregar entradas nuevas a `Bibliography_base.bib` salvo que la fuente nueva resuelva
por DOI.

#### Scenario: Dato no establecido marcado como no reportado

- **WHEN** se lee una celda de la tabla cuya fuente no explicita el dato
- **THEN** la celda dice "no reportado en el alcance revisado"
- **AND** no se completa con un valor estimado, inferido sin fuente ni supuesto

#### Scenario: Sin fabricación ni atribución indebida

- **WHEN** se contrasta cada valor de la tabla contra su fuente declarada
- **THEN** todo valor numérico coincide con el reportado por la fuente
- **AND** no se introduce ningún corpus, métrica o condición inexistente en la fuente

#### Scenario: Bibliografía sin altas indebidas

- **WHEN** se inspecciona `Bibliography_base.bib` tras el change
- **THEN** no hay entradas nuevas, salvo una fuente nueva que resuelva por DOI
- **AND** todas las claves citadas en la tabla existen como entradas del `.bib`

### Requirement: Neutralidad de páginas al incorporar la tabla

La incorporación de la tabla comparativa SHALL ser neutral en páginas: el total del
PDF MUST permanecer en 100 páginas o menos, medido con `pdfinfo main.pdf` sobre el
documento completo. El texto redundante que la tabla reemplaza (en particular la
oración agrupada de `03:32` y la repetición de corpus/métrica en la prosa de la
misma subsección) SHALL retirarse o condensarse en el mismo capítulo para compensar
el espacio de la tabla. El change MUST NOT exceder el tope de páginas vigente.

#### Scenario: Total de páginas dentro del tope

- **WHEN** se compila `main.tex` con la imagen `texlive-thesis` y se ejecuta `pdfinfo main.pdf | grep Pages`
- **THEN** el total es 100 páginas o menos
- **AND** la portada sigue ocupando exactamente una página

#### Scenario: Compensación en el mismo capítulo

- **WHEN** se compara la prosa de la subsección antes y después del change
- **THEN** la redundancia que la tabla reemplaza fue retirada o condensada en el Capítulo 3
- **AND** no se trasladó contenido científico requerido a otra sección ni se eliminó una afirmación sustantiva

#### Scenario: Compilación sin errores fatales

- **WHEN** se compila `main.tex` con `latexmk -xelatex`
- **THEN** se produce `main.pdf` sin errores fatales
- **AND** el registro no contiene "undefined reference" ni "multiply defined label"

### Requirement: Alcance del archivo y secuencia respecto de c-111

El change SHALL limitarse a `docs/Tesis/v9 (IA)/paper/sections/03-estado-del-arte.tex`.
El change MUST NOT editar `preambles/`, `main.tex`, el memo canónico, `CHANGES.md`
ni `dictamen-correcciones.md`. La tabla SHALL preexistir al change de versionado y
etiquetado: este change MUST aprobarse y aplicarse antes de `c-111`.

#### Scenario: Un solo archivo fuente editado

- **WHEN** se inspecciona el diff del change
- **THEN** el único archivo `.tex` modificado es `03-estado-del-arte.tex`
- **AND** no se modifican el preámbulo, `main.tex` ni los documentos de gobierno

#### Scenario: Secuencia respecto del tag

- **WHEN** se planifica el orden de aplicación
- **THEN** este change figura antes de `c-111`
- **AND** el tag de `c-111` no se crea hasta que la tabla esté aplicada y verificada

### Requirement: Capitulo de cumplimiento normativo ISO/NIST

La tesis SHALL incluir un capitulo/seccion de cumplimiento que presente el mapeo de
ISO/IEC 27001:2022 + ISO/IEC 27002:2022 y de NIST CSF 2.0, con el estado actual de
alineacion, las brechas identificadas y la hoja de ruta. El capitulo SHALL declarar
los estandares de referencia adoptados (ISO/IEC 27001:2022, ISO/IEC 27002:2022,
NIST CSF 2.0, ISO/IEC 27701 y Ley 25.326). El mapeo ISO SHALL agrupar los controles
por tema (Organizacional 5.x, Personas 6.x, Fisico 7.x, Tecnologico 8.x) y el perfil
NIST SHALL cubrir las seis funciones (GV, ID, PR, DE, RS, RC) con su nivel de
madurez. Cada tabla del capitulo SHALL declarar su linea de fuente.

#### Scenario: Capitulo de cumplimiento presente

- **WHEN** se busca en `docs/Tesis/v9 (IA)/paper/sections/` y en el PDF compilado
  contenido sobre ISO 27001/27002 y NIST CSF 2.0
- **THEN** existe una seccion de cumplimiento con el mapeo ISO y el perfil NIST
- **AND** la seccion declara los estandares adoptados y su estado actual, brechas y hoja de ruta

#### Scenario: Mapeo ISO por tema

- **WHEN** se lee la tabla de mapeo ISO/IEC 27002:2022 del capitulo
- **THEN** los controles se agrupan por tema (Organizacional, Personas, Fisico, Tecnologico)
- **AND** cada grupo declara su estado de alineacion y la evidencia o brecha principal
- **AND** la tabla no reproduce los 93 controles uno por uno

#### Scenario: Perfil NIST CSF 2.0 con las seis funciones

- **WHEN** se lee el perfil de alineacion con NIST CSF 2.0
- **THEN** figuran las seis funciones GV, ID, PR, DE, RS y RC
- **AND** cada funcion declara una subcategoria representativa y su nivel de madurez

### Requirement: Regla de lenguaje de alineacion sin certificacion

El capitulo de cumplimiento SHALL usar el vocabulario "alineado con" y "controles
mapeados a" (o "grado de alineacion" y "brecha identificada"). El documento MUST NOT
declarar "certificado", "certificacion", "compliant", "conforme" ni "cumple ISO/NIST".
El capitulo SHALL declarar de forma explicita que la evaluacion identifica alineacion y
brechas y que no constituye una certificacion ni una auditoria de conformidad.

#### Scenario: Terminos de certificacion ausentes

- **WHEN** se busca en los `.tex` del capitulo y en el PDF compilado las palabras
  "certificado", "certificacion", "compliant" y "conforme"
- **THEN** no aparecen como una declaracion de conformidad del sistema
- **AND** el capitulo usa "alineado con" y "controles mapeados a"

#### Scenario: Descargo de certificacion presente

- **WHEN** se lee la introduccion del capitulo de cumplimiento
- **THEN** el texto declara que es una evaluacion de alineacion, no una certificacion
- **AND** no afirma que exista una auditoria de certificacion

### Requirement: Neutralidad de paginas del contenido de cumplimiento

El capitulo de cumplimiento SHALL ser neutral en paginas: el total del PDF compilado
MUST NOT superar las 100 paginas. El capitulo SHALL absorber o reemplazar contenido
existente para compensar su extension, en particular la narracion de la subseccion
11.4 "Seguridad tecnica" de `11-aspectos-legales.tex`, cuya evidencia de control se
pliega al mapeo ISO. El change MUST NOT eliminar contenido cientifico, numeros
canonicos, figuras, tablas con linea de fuente ni ninguna correccion de c-102 a c-117.

#### Scenario: Tope de paginas preservado

- **WHEN** se compila `main.tex` con la imagen `texlive-thesis` y se ejecuta
  `pdfinfo main.pdf | grep Pages`
- **THEN** el total de paginas es 100 o menos
- **AND** el conteo no aumenta respecto del estado de partida

#### Scenario: Reemplazo de la narracion de seguridad tecnica

- **WHEN** se compara `11-aspectos-legales.tex` con el estado previo al change
- **THEN** la prosa de la subseccion 11.4 "Seguridad tecnica" fue condensada o plegada al mapeo de controles
- **AND** su evidencia tecnica permanece en la tabla de mapeo ISO

#### Scenario: Contenido canonico preservado

- **WHEN** se revisa el PDF compilado tras el change
- **THEN** el numero de figuras sigue siendo 8
- **AND** los numeros canonicos de la tesis no cambiaron
- **AND** las tablas conservan su linea de fuente

#### Scenario: Cero referencias indefinidas

- **WHEN** se revisa el log de compilacion con XeLaTeX
- **THEN** no hay advertencias de "undefined reference" ni "multiply defined label"

### Requirement: Coherencia del capitulo de cumplimiento con el marco legal

El capitulo de cumplimiento SHALL ser coherente con el Capitulo de aspectos legales
(`11-aspectos-legales.tex`). SHALL remitir a las subsecciones legales mediante
`\autoref` y MUST NOT duplicar ni contradecir su narrativa juridica (Ley 25.326,
transferencia internacional, derechos ARCO, base de licitud).

#### Scenario: Remision sin duplicacion

- **WHEN** se lee el capitulo de cumplimiento
- **THEN** remite al marco legal del Capitulo 11 mediante referencias cruzadas
- **AND** no reproduce en extenso el marco normativo ya expuesto en 11.1-11.5

#### Scenario: Coherencia de cifras y hechos legales

- **WHEN** se comparan las menciones legales del capitulo de cumplimiento con las de 11.3 y 11.5
- **THEN** las referencias a la Ley 25.326, la transferencia internacional y los plazos ARCO son consistentes
- **AND** no se introducen afirmaciones juridicas contradictorias

### Requirement: Trazabilidad de los controles a los changes archivados

El mapeo del capitulo de cumplimiento SHALL vincular cada control implementado con el
change archivado que lo cerro (C-61 a C-66) o con el artefacto versionado del
repositorio que lo evidencia. Las brechas residuales de tipo organizacional SHALL
declararse como responsabilidad de la organizacion adoptante, fuera del alcance del
repositorio.

#### Scenario: Controles trazables a los changes archivados

- **WHEN** se lee la hoja de ruta del capitulo de cumplimiento
- **THEN** los controles cerrados se asocian a los changes C-61 a C-66 o a su artefacto
- **AND** se distinguen de las brechas residuales

#### Scenario: Brechas organizacionales atribuidas al adoptante

- **WHEN** se leen las brechas residuales del capitulo
- **THEN** las de tipo organizacional (personas 6.x, fisicos 7.x, revision independiente) se declaran responsabilidad de la organizacion adoptante
- **AND** no se presentan como controles implementados en el repositorio

### Requirement: Correccion ortografica y de portada

El documento SHALL estar libre de las cuatro formas ortograficas erroneas detectadas por la auditoria. La correccion MUST ser contextual y MUST NOT alterar verbos legitimos. La portada y los titulos de seccion SHALL contener las tildes correctas del espanol.

#### Scenario: Formas sustantivas corregidas
- **WHEN** se busca en los archivos `.tex` de `paper/sections/` las formas `diseñó`, `completó` y `aquéllos`
- **THEN** cero apariciones de esas formas permanecen
- **AND** las apariciones sustantivas de `desarrolló` (por ejemplo "el desarrolló del modulo") fueron reemplazadas por `desarrollo`

#### Scenario: Verbos legitimos preservados
- **WHEN** se inspeccionan `00-resumen.tex:11` ("el estudio se desarrolló") y `06-implementacion.tex:87` ("el frontend se desarrolló")
- **THEN** ambos usos verbales de `desarrolló` permanecen intactos
- **AND** no se sustituyo el verbo conjugado por el sustantivo

#### Scenario: Portada y titulos con tildes
- **WHEN** se lee la portada (`00-portada.tex`) y los titulos de seccion del documento
- **THEN** las palabras que requieren tilde ("TECNOLOGICA", "Programacion", "Automatizacion", "Republica", "Introduccion", "Conclusiones", entre otras) aparecen con su tilde correcta
- **AND** no queda ninguna ocurrencia de esas palabras sin tilde

#### Scenario: Conteo de errores resuelto
- **WHEN** se cuenta el total de ocurrencias de las cuatro formas en las secciones activas (excluyendo archivos `.bak`)
- **THEN** las 52 apariciones reportadas por la auditoria se resuelven en 50 correcciones (dos verbos legitimos preservados)
- **AND** el barrido de control no devuelve residuos incorrectos

### Requirement: Evidencia visual del sistema y de los resultados

La tesis SHALL incluir las 8 figuras requeridas, embebidas mediante `\includegraphics` dentro de un entorno `figure` con `\caption` y `\label`, en sus ubicaciones naturales. Cada figura SHALL provenir de una fuente reproducible (diagrama Mermaid versionado, script de generacion o captura manual identificada).

#### Scenario: Las ocho figuras existen y estan embebidas
- **WHEN** se listan los archivos de `paper/figures/` y se buscan los comandos `\includegraphics` en `paper/sections/`
- **THEN** existen los archivos de las 8 figuras: diagrama de despliegue, diagrama de secuencia, diagrama entidad-relacion, captura del flujo N8N, captura del panel de administracion, captura del dashboard, boxplot de tiempos y matriz de confusion
- **AND** cada figura esta referenciada por un `\includegraphics` dentro de un `figure`

#### Scenario: Ubicacion natural de cada figura
- **WHEN** se revisa el capitulo donde se discute el artefacto correspondiente
- **THEN** el diagrama de despliegue y el de secuencia aparecen en el Capitulo 5 o el Anexo A
- **AND** el diagrama entidad-relacion aparece en la seccion 5.6 o el Anexo C
- **AND** la captura del flujo N8N aparece en la seccion 6.3 o el Anexo E
- **AND** las capturas del panel de administracion y del dashboard aparecen en la seccion 6.8
- **AND** el boxplot de tiempos aparece en la seccion 7.1 y la matriz de confusion en la seccion 7.2

#### Scenario: Figuras con fuente reproducible
- **WHEN** se inspecciona una figura generada a partir de un diagrama
- **THEN** existe la fuente Mermaid correspondiente en `docs/diagrams/` o en el repositorio
- **AND** las figuras de resultados (boxplot y matriz) fueron generadas por un script reproducible a partir de los datos del corpus o de la matriz reportada
- **AND** las capturas de interfaz se identifican como tales en el texto

#### Scenario: Boxplot de latencias reportado por canal
- **WHEN** se inspecciona la figura del boxplot de tiempos (seccion 7.1)
- **THEN** la figura reporta las latencias POR CANAL (formulario web, correo y telefonia) en paneles separados o en un layout agrupado por canal, en lugar de un unico boxplot que mezcle los tres puntos de ingreso
- **AND** cada canal compara `tiempo_manual_s` contra `tiempo_automatizado_s` dentro del mismo canal
- **AND** la separacion por canal es consistente con la regla de comparabilidad de `docs/medicion-latencia-e2e.md` (los puntos de ingreso no son homogeneos)

#### Scenario: Panel de telefonia con metrica corregida
- **WHEN** se inspecciona el panel de telefonia del boxplot
- **THEN** el valor automatizado usa la metrica corregida de `tiempo_automatizado_s` que incluye la duracion de la llamada/grabacion (correccion de c-77 "Opcion A")
- **AND** si la correccion de c-77 no esta aplicada, el panel se rotula "automatizado = solo post-procesamiento de la llamada (cota inferior)"

### Requirement: Anexos con contenido real

Los anexos A a G SHALL contener contenido real embebido (figura, tabla, listado de codigo o bloque de datos) en lugar de unicamente describirlo en prosa. El Anexo H (especificacion del prompt de Gemini) SHALL incorporarse al documento como una seccion de anexo.

#### Scenario: Cada anexo A-G embebe su artefacto
- **WHEN** se lee cada una de las secciones de `12-anexos.tex`
- **THEN** el Anexo A embebe el diagrama de arquitectura (figura), el Anexo C embebe el esquema de base de datos (tabla o diagrama ER), el Anexo D embebe la especificacion OpenAPI (bloque de codigo o listado), el Anexo E embebe la configuracion del flujo N8N y el Anexo F embebe la estructura o declaracion del corpus
- **AND** cada anexo deja de ser exclusivamente un parrafo descriptivo sin contenido embebido

#### Scenario: Anexo H incorporado
- **WHEN** se busca el Anexo H en los archivos `.tex`
- **THEN** existe una seccion que incorpora el contenido de `docs/anexo_h_prompt_gemini.md` (estructura del prompt y parametros de configuracion)
- **AND** el Anexo H esta referenciado desde el texto principal del documento

#### Scenario: Contenido real y no meramente descriptivo
- **WHEN** se inspecciona un anexo convertido
- **THEN** contiene al menos un entorno `figure`, `table`, `lstlisting` o `verbatim` con contenido
- **AND** el anexo mantiene la prosa introductoria que lo contextualiza

### Requirement: Ausencia de duplicaciones sustantivas

El documento SHALL NOT repetir de forma casi verbatim parrafos equivalentes entre capitulos. El material compartido SHALL aparecer una sola vez en el capitulo que le corresponde, con referencias cruzadas donde sea necesario.

#### Scenario: Par introduccion / marco teorico
- **WHEN** se comparan `01-introduccion.tex:8,10` con `02-marco-teorico.tex:10,12`
- **THEN** la descripcion de Galup2009 no se repite casi verbatim en ambos capitulos
- **AND** cada afirmacion sobre ITSM aparece una sola vez o remite por referencia cruzada

#### Scenario: Par arquitectura / implementacion
- **WHEN** se comparan `05-arquitectura.tex:44` con `06-implementacion.tex:39,41` y se buscan las ocurrencias de "camino de clasificacion unico" (`05:60` y `06:44`)
- **THEN** la descripcion del flujo de orquestacion no se repite en ambos capitulos
- **AND** la afirmacion del camino de clasificacion unico aparece una sola vez, con remision a la otra seccion

#### Scenario: Par discusion / conclusiones
- **WHEN** se comparan `08-discusion.tex:8,10,14` con `09-conclusiones.tex:12,24`
- **THEN** la discusion y las conclusiones no repiten los mismos enunciados
- **AND** la discusion interpreta y las conclusiones sintetizan sin duplicar frases

### Requirement: Consistencia de la version de N8N

La version de N8N citada en el documento SHALL ser unica y consistente con la version realmente desplegada (2.11.2). El documento MUST NOT contener acotaciones obsoletas sobre indisponibilidad de imagenes en Docker Hub.

#### Scenario: Acotacion obsoleta retirada
- **WHEN** se busca en las secciones `.tex` la cadena "1.62" o "no se encuentra disponible en Docker Hub"
- **THEN** cero apariciones permanecen en `05-arquitectura.tex` y `06-implementacion.tex`
- **AND** la version de N8N alli citada es consistente con la del Anexo E

#### Scenario: Version reconciliada
- **WHEN** se comparan las menciones de la version de N8N en 5, 6 y el Anexo E
- **THEN** todas refieren la misma version (2.11.2)
- **AND** no queda ninguna contradiccion interna sobre la version desplegada

### Requirement: Afirmaciones respaldadas por la evidencia

Las afirmaciones de la discusion (8.1) y de las conclusiones (9.1) SHALL estar sostenidas por la evidencia empirica reportada en el Capitulo 7 (resultados) o por la literatura citada. Los juicios de valor no respaldados SHALL ser retirados o reformulados en terminos de la evidencia disponible.

#### Scenario: Juicios de valor sin respaldo retirados de la discusion
- **WHEN** se lee la seccion 8.1 de `08-discusion.tex`
- **THEN** expresiones como "superan ampliamente", "valida la hipotesis subsidiaria", "consecuencia deseable" y "materializa el esquema human in the loop buscado" no se presentan como hechos no medidos
- **AND** toda magnitud afirmada remite a los valores corregidos del Capitulo 7 (reduccion de tiempo 71,2~% con cota conservadora 65,6~% con -10~s y 68,6~% con -5~s, y exactitud 73,5~%)

#### Scenario: Juicios de valor sin respaldo retirados de las conclusiones
- **WHEN** se lee la seccion 9.1 de `09-conclusiones.tex`
- **THEN** expresiones como "cumplido satisfactoriamente", "supero con holgura", "no deja espacio para la duda razonable", "resultado poco frecuente", "trasciende lo meramente estadistico" y "activo que excede" fueron retiradas o reformuladas
- **AND** las conclusiones se sustentan en los resultados de la prueba de Wilcoxon (\(W = 363\), \(p = 3{,}08 \times 10^{-32}\), \(r = 0{,}9639\), cifras corregidas por c-76) y en las metricas de clasificacion reportadas (exactitud 73,5~%, macro-F1 0,5207)

#### Scenario: La afirmacion de garantia metodologica queda acotada
- **WHEN** se lee el parrafo de rigor metodologico en `08-discusion.tex:16`
- **THEN** la afirmacion de que la separacion de datos constituye una garantia que "no todos los trabajos del area documentan con el mismo nivel de explicitacion" se reformula sin la comparacion no verificada contra la literatura
- **AND** se describe la practica propia (aislamiento del corpus de validacion) sin adjudicar a terceros una carencia no medida

### Requirement: Etiqueta de la version evaluada

El repositorio SHALL identificar la version evaluada de la tesis mediante un tag
anotado `v1.0.0` que apunte al commit cuya fuente compila el PDF evaluado. El tag
SHALL crearse SOLO despues de que los changes de contenido c-104, c-105, c-106,
c-107, c-108, c-109 y c-110 esten aplicados y el manuscrito recompilado, de modo
que la etiqueta refleje la fuente final corregida y no una intermedia. El tag
SHALL publicarse en el remoto `origin`.

#### Scenario: Tag existente y anotado

- **WHEN** se ejecuta `git tag -l` y `git cat-file -t v1.0.0` en el repositorio
- **THEN** el tag `v1.0.0` existe
- **AND** `git cat-file -t v1.0.0` devuelve `tag` (tag anotado, no lightweight)

#### Scenario: Tag sobre la fuente final

- **WHEN** se verifica el commit al que apunta `v1.0.0` (`git rev-parse v1.0.0^{commit}`)
- **THEN** ese commit es posterior a la aplicacion de c-104..c-110
- **AND** su fuente compila el PDF evaluado
- **AND** el tag esta publicado en `origin` (`git ls-remote --tags origin v1.0.0` lo devuelve)

#### Scenario: Sin tag sobre fuente intermedia

- **WHEN** se intenta cerrar el change antes de archivar algunos de c-104..c-110
- **THEN** la tarea de creacion del tag no se marca completa
- **AND** no se crea el tag sobre una fuente intermedia

### Requirement: Trazabilidad del hash del commit evaluado

El manuscrito SHALL consignar el hash completo de 40 caracteres del commit al que
apunta el tag `v1.0.0`, de modo que el documento bajo revision sea trazable a una
revision concreta del repositorio. El Anexo B (`sections/12-anexos.tex`,
`sec:anexo-repositorio`) SHALL reemplazar el lenguaje de "accion pendiente" por la
referencia al tag y su hash, y ese mismo hash SHALL registrarse en el registro de
trazabilidad `docs/Tesis/Correcciones/dictamen-correcciones.md`. El hash consignado
MUST coincidir con el del commit etiquetado.

#### Scenario: Hash consignado en el manuscrito

- **WHEN** se lee el Anexo B del PDF compilado (o `sections/12-anexos.tex`)
- **THEN** figura el tag `v1.0.0` y el hash completo de 40 caracteres del commit evaluado
- **AND** no permanece la frase que declara la creacion del tag como "accion pendiente"

#### Scenario: Hash coherente con el tag

- **WHEN** se compara el hash consignado en el manuscrito con `git rev-parse v1.0.0^{commit}`
- **THEN** coinciden en los 40 caracteres
- **AND** el hash tambien figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Nota de version legible en el PDF

- **WHEN** se compila `main.tex` con la imagen `texlive-thesis` y se inspecciona el PDF
- **THEN** la nota de version y trazabilidad aparece renderizada sin errores fatales
- **AND** el conteo de paginas no aumenta respecto de la version corregida de partida

### Requirement: Correccion de defectos residuales de forma y consistencia del PDF

La documentacion LaTeX de la tesis SHALL renderizar sin artefactos de forma visibles y con rotulos y referencias cruzadas consistentes. En particular: no MUST imprimirse ningun fragmento del preambulo tabular como texto; toda celda de tabla MUST estar sintacticamente completa; las remisiones a tablas MUST resolverse por `\ref{}` y no por numeros literales; los anexos MUST rotularse en espanol; el vocabulario de servicios internos MUST corresponder al despliegue real; y la entrada de las referencias bibliograficas MUST presentarse como nivel de seccion en el indice. Estas correcciones SHALL preservar el contenido y los numeros canonicos, sin alterar el presupuesto de paginas del cuerpo.

#### Scenario: Sin fragmento de preambulo tabular visible

- **WHEN** se extrae el texto del PDF compilado y se busca el literal "aggedright"
- **THEN** no aparece ninguna ocurrencia (el preambulo de columna `\raggedright\arraybackslash` esta restaurado en una sola linea)
- **AND** la tabla de tiempos conserva exactamente su contenido y sus anchos de columna

#### Scenario: Celda de la tabla de cumplimiento cerrada

- **WHEN** se lee la fila del objetivo especifico 2 en la tabla de cumplimiento del Capitulo 9
- **THEN** el intervalo de confianza se muestra como `IC [67,0 %, 79,1 %]` con el corchete cerrado
- **AND** el macro-F1 0,5207 queda fuera del intervalo, como texto separado

#### Scenario: Remision a la tabla de endpoints resuelta

- **WHEN** se lee la remision a los puntos de entrada REST en el Anexo de especificacion OpenAPI
- **THEN** el numero de tabla se resuelve mediante `\ref` al rotulo real del contrato REST (`tab:api`)
- **AND** no queda ningun `Tabla~N` literal que apunte a un numero incorrecto

#### Scenario: Anexos rotulados en espanol

- **WHEN** se inspecciona el indice general y la pagina de anexos del PDF compilado
- **THEN** el rotulo de anexos aparece en espanol, coherente con el termino usado en el cuerpo ("Anexo"/"Anexos")
- **AND** no queda el rotulo "Appendices" en ingles

#### Scenario: Redis ausente de los servicios internos

- **WHEN** se lee la descripcion de la comunicacion interna entre servicios en el Capitulo 5
- **THEN** la enumeracion de servicios internos incluye N8N, backend y PostgreSQL
- **AND** no incluye Redis, retirado en el change c-62

#### Scenario: Entrada de referencias bibliograficas en el indice

- **WHEN** se inspecciona la entrada "Referencias bibliograficas" en el indice general
- **THEN** figura como entrada de nivel de seccion y su destino hipervinculo no reutiliza el ancla de la ultima subseccion del capitulo anterior
- **AND** si la unica anomalia restante es el destino del hipervinculo, se documenta como limitacion cosmetica aceptada sin alterar el nivel visible de la entrada

### Requirement: Afirmaciones cuantitativas respaldadas por medicion

Toda afirmacion cuantitativa de la tesis SHALL estar respaldada por una medicion reproducible presente en el repositorio (por ejemplo, en `evaluation/`). Una afirmacion cuantitativa sin medicion de respaldo MUST reformularse de forma cualitativa o retirarse, y MUST NOT conservar el valor numerico.

#### Scenario: Sin puntos porcentuales de F1 sin medicion

- **WHEN** se busca en los archivos de seccion afirmaciones de puntos porcentuales de F1 atribuidas al enriquecimiento del prompt
- **THEN** no aparece el valor "4 puntos porcentuales de F1" ni otro numero inventado
- **AND** la afirmacion se expresa de forma cualitativa ("mejoro la robustez ... sobre transcripciones automaticas")

### Requirement: Rotulo de la sub-hipotesis de intervencion humana como no contrastada

La tesis SHALL rotular la sub-hipotesis de intervencion humana de forma explicita como "no contrastada por ausencia de registro primario" en el resumen, la introduccion, los resultados y las conclusiones, y SHALL retitular la subseccion homonima del capitulo de resultados para que su titulo no prometa un resultado que la tesis no entrega. El texto MUST NOT presentar esa sub-hipotesis como una laguna sin declarar, ni dejar un titulo que afirme una reduccion no medida.

#### Scenario: Rotulo explicito en las cuatro secciones

- **WHEN** se lee la sub-hipotesis de intervencion humana en el resumen, la introduccion, los resultados y las conclusiones
- **THEN** en las cuatro se declara que la sub-hipotesis es "no contrastada por ausencia de registro primario"
- **AND** no se la presenta como no medida sin explicar la causa, ni como confirmada o refutada

#### Scenario: Subseccion de resultados retitulada

- **WHEN** se inspecciona el titulo de la subseccion de intervencion humana del capitulo de resultados
- **THEN** el titulo no promete una "Reduccion de la intervencion humana" no entregada
- **AND** la entrada correspondiente del indice refleja el nuevo titulo

### Requirement: Trazabilidad bibliografica de afirmaciones sobre plataformas comerciales y precios

Toda afirmacion de la tesis sobre productos comerciales, plataformas o precios (por ejemplo Zendesk, Freshdesk, ServiceNow, DigitalOcean, Vertex AI) SHALL apoyarse en una referencia bibliografica formal presente en `Bibliography_base.bib`, o bien reformularse de forma explicita como observacion propia de los autores. El documento MUST NOT sostener afirmaciones comerciales citables apoyadas unicamente en URLs al pie o en la documentacion publica sin entrada bibliografica.

#### Scenario: Referencias formales o reformulacion propia

- **WHEN** se leen las afirmaciones sobre plataformas comerciales y precios en los capitulos que las contienen (estado del arte, introduccion y discusion)
- **THEN** cada afirmacion citable se respalda con una entrada bibliografica formal en `Bibliography_base.bib`
- **AND** las afirmaciones no citables se reformulan como observacion propia declarada
- **AND** no queda ninguna afirmacion comercial apoyada solo en una URL al pie

#### Scenario: Correspondencia citas-bibliografia preservada

- **WHEN** se agregan las entradas nuevas a `Bibliography_base.bib`
- **THEN** cada entrada nueva incluye autor o entidad, titulo, ano y campo de publicacion mas `url` o `doi`
- **AND** no se introduce ninguna cita huerfana ni ninguna entrada sin usar

### Requirement: Declaracion del intervalo de confianza del kappa

La tesis SHALL reportar el intervalo de confianza del coeficiente kappa (0,87) si la tabla de doble etiquetado es recuperable, calculandolo por bootstrap con semilla fija. Si la tabla primaria no es recuperable, la tesis SHALL conservar y elevar al cuerpo una declaracion explicita de no computabilidad, sin fabricar un intervalo. La decision SHALL quedar registrada en el diseno del cambio.

#### Scenario: Tabla recuperable

- **WHEN** la tabla de acuerdo observado/esperado o las etiquetas por caso de ambos analistas estan disponibles
- **THEN** la tesis reporta el intervalo de confianza del kappa junto al valor puntual 0,87
- **AND** declara el metodo y la semilla empleados

#### Scenario: Tabla no recuperable

- **WHEN** la tabla primaria de doble etiquetado no esta disponible en las fuentes del repositorio
- **THEN** la tesis declara de forma explicita que el intervalo de confianza del kappa es no computable por ausencia de la tabla primaria
- **AND** no se fabrica ni se estima un intervalo
- **AND** el rotulo interpretativo "casi perfecto" (Landis y Koch) se conserva

### Requirement: Umbral de migracion como referencia indicativa de orden de magnitud

El umbral de "5.000 casos" para migrar a un clasificador supervisado propio SHALL presentarse como una referencia indicativa explicita de orden de magnitud, no como un valor derivado del corpus. El documento MUST NOT presentarlo como un valor calculado ni como una condicion tecnica exacta.

#### Scenario: Umbral rotulado como indicativo

- **WHEN** se lee el pasaje de recomendaciones sobre el clasificador supervisado propio
- **THEN** el umbral de 5.000 casos se declara como referencia indicativa de orden de magnitud
- **AND** se aclara que no deriva del corpus actual ni de un calculo de potencia estadistica

### Requirement: Acotacion del eje de reconocimiento automatico del habla

El eje de reconocimiento automatico del habla (ASR) del marco teorico SHALL acotarse al minimo conceptual necesario para el canal telefonico, dado que el sistema delega la transcripcion en un servicio externo y no integra un motor de ASR. El documento SHALL conservar unicamente la nocion conceptual y la aclaracion de que la transcripcion efectiva la provee un servicio externo.

#### Scenario: Eje de ASR reducido

- **WHEN** se lee la subseccion de reconocimiento automatico del habla del marco teorico
- **THEN** su extension se limita al minimo conceptual necesario para situar el canal telefonico
- **AND** se declara que el sistema no integra un motor de ASR y que la transcripcion la provee un servicio externo
- **AND** la reduccion no introduce paginas netas al cuerpo

### Requirement: Numeracion limpia del capitulo de aspectos legales

El capitulo de consideraciones eticas y aspectos legales SHALL presentar una unica seccion de nivel superior, de modo que no incremente en uno la numeracion de los capitulos siguientes. Los comentarios internos de numeracion de los archivos `.tex` SHALL reflejar la posicion real de cada capitulo en el documento.

#### Scenario: Unica seccion de nivel superior

- **WHEN** se inspecciona la estructura de secciones del capitulo de aspectos legales
- **THEN** el capitulo contiene una sola seccion de nivel superior
- **AND** las subsecciones previamente bajo la segunda seccion pasan a depender de la unica seccion superior sin perder contenido
- **AND** la numeracion de los capitulos posteriores no se desplaza

#### Scenario: Comentarios de numeracion coherentes

- **WHEN** se revisan los comentarios de numeracion en la cabecera de los archivos `.tex` y en `main.tex`
- **THEN** cada comentario declara la posicion real del capitulo en el documento compilado
- **AND** no queda ningun comentario que asigne al capitulo legal un numero de posicion incorrecto

### Requirement: Fuente del criterio del umbral del 85 por ciento

La justificacion del umbral de exactitud del 85~\% SHALL declarar la fuente de cada uno de sus criterios convergentes. El criterio que hoy se apoya en "mediciones organizacionales preliminares" SHALL citarse con una fuente formal, o bien reformularse de forma explicita como estimacion propia de los autores sin presentarla como medicion de respaldo. El documento MUST NOT atribuir a mediciones organizacionales preliminares una precision que no esta citada ni declarada como propia.

#### Scenario: Fuente declarada o reformulacion propia

- **WHEN** se lee la justificacion del umbral de exactitud del 85~\% en el capitulo de introduccion
- **THEN** cada uno de los criterios convergentes declara su fuente
- **AND** el criterio apoyado en mediciones organizacionales preliminares se cita con una referencia formal o se reformula como estimacion propia declarada
- **AND** no queda ninguna medicion organizacional preliminar presentada como respaldo sin fuente
