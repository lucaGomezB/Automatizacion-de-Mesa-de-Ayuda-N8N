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
- **AND** the key figures match those of the reduced Spanish "Resumen" (200 paired cases, 61.6~s to 17.76~s, 71.2~\% reduction, \(W = 363\), \(r = 0.9639\), 73.5~\% accuracy, threshold macro-F1 0.6508 over the four estimable classes, Cohen's Kappa 0.87)
- **AND** the five-class macro-F1 (0.5207), if cited, is labelled as including the non-estimable single-case class

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
73,5 % (147/200), macro-F1 de umbral 0,6508 sobre las cuatro clases estimables (con
el de cinco clases, 0,5207, como valor informativo), micro-F1 0,6654, subset
accuracy 0,43, Hamming
loss 0,3586, las etapas deterministic 131 / Gemini 69, y la matriz de confusion 5x5
completa. El vocabulario de sectores reportado SHALL ser el conjunto canonico de
cinco categorias, SIN la categoria retirada "Operaciones". La tesis SHALL NOT
reportar como vigentes los valores del corpus sintetico (3 clases, distribucion
82/64/54, exactitud 92 %, F1 macro 0,919).

#### Scenario: Capitulo 7 reporta las metricas reales

- **WHEN** se lee el Capitulo 7 (Resultados) del PDF compilado
- **THEN** la exactitud reportada es 73,5 % (147/200) y el macro-F1 de umbral es 0,6508, con el de cinco clases (0,5207) rotulado como informativo
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
recompilar `docs/Tesis/v10 (IA)/paper/main.pdf` de modo que refleje las
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
macro-F1 de umbral 0,6508 sobre cuatro clases estimables, 0,5207 con las cinco
clases, y taxonomia de cinco clases) y SHALL corregir en el Capitulo 1.6 la mencion a
"tres sectores (Sistemas, Operaciones y Soporte Tecnico)" por las cinco categorias
canonicas, "Gemini 2.5 Flash" por `gemini-3.6-flash` y revisar la fecha "junio de
2026".

#### Scenario: 7.2 usa metricas reales

- **WHEN** se lee el Capitulo 7.2
- **THEN** reporta exactitud 73,5 %, macro-F1 de umbral 0,6508 (con el de cinco clases, 0,5207, rotulado) y la taxonomia de cinco clases
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

La tesis SHALL reportar la relacion entre la confianza devuelta por el clasificador y su exactitud DESAGREGADA POR ETAPA del pipeline, porque la etapa deterministica y la etapa Gemini emiten magnitudes de confianza de naturaleza distinta (definidas en el subsistema de clasificacion, `subsec:subsistema-clasificacion`). El capitulo de resultados MUST incluir la exactitud por banda de confianza separada por etapa (casos, aciertos y exactitud), la exactitud estricta de cada etapa con su IC de Wilson y la contingencia de confianza alta/baja en torno a 0,70 con su composicion por etapa. La conclusion sobre calibracion SHALL restringirse a la etapa Gemini y a su rango efectivo observado (0,85 a 1,00) y SHALL declarar que la etapa de reglas no emite una confianza utilizable como criterio de derivacion. La tesis MUST NOT caracterizar al clasificador en su conjunto como "anti-calibrado" ni como de "calibracion invertida". El capitulo de discusion MUST interpretar la implicancia de la lectura por etapa para el umbral de revision humana de 0,70.

#### Scenario: Tabla de contingencia o curva de calibración presente

- **WHEN** se lee el capitulo de resultados
- **THEN** existe una tabla que cruza las bandas de confianza con la etapa del pipeline y reporta casos, aciertos y exactitud por celda
- **AND** se reportan la precision del segmento de confianza `>= 0,70` y la del segmento `< 0,70` junto con su composicion por etapa (los 124 casos con confianza `< 0,70` son de la etapa deterministica; el segmento `>= 0,70` reune 7 casos deterministicos y los 69 de Gemini)

#### Scenario: Discusión de la anti-calibración

- **WHEN** se lee la interpretacion del contraste agregado entre confianza alta (0,697) y confianza baja (0,758)
- **THEN** se presenta como una comparacion entre la etapa de reglas y la etapa de modelo, no como evidencia sobre la calibracion de la confianza
- **AND** ninguna fuente `.tex` contiene las expresiones "anti-calibr" ni "calibracion invertida" (con o sin tilde)

#### Scenario: Conclusion restringida al rango efectivo de Gemini

- **WHEN** se lee la conclusion de la subseccion de calibracion
- **THEN** se reportan las exactitudes de la etapa Gemini en las bandas `[0,85; 0,95)` y `[0,95; 1,00]` con su IC de Wilson y se declara que la confianza autodeclarada por Gemini no discrimina aciertos de errores dentro del rango observado
- **AND** se declara que la etapa de reglas no emite una confianza utilizable como criterio de derivacion

#### Scenario: Discusion del umbral de 0,70

- **WHEN** se lee el capitulo de discusion
- **THEN** se interpreta la implicancia de la lectura por etapa para el umbral de revision humana de 0,70, de forma coherente con el alcance del gate declarado en el capitulo de arquitectura
- **AND** se conserva el hallazgo de que la etapa Gemini nunca devolvio una confianza inferior a 0,85 en el corpus

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

El capitulo de estado del arte (seccion 3.3) y el de discusion (seccion 8.2) SHALL describir el aporte de Revina, Buza & Meister (2020) conforme al contenido real del articulo "IT Ticket Classification: The Simpler, the Better" (IEEE Access, vol. 8, pp. 193380-193395, 2020). El documento MUST NOT atribuir a ese articulo el uso de arquitecturas basadas en BERT, una exactitud cercana al 91 % ni la conclusion de que los modelos preentrenados transfieren conocimiento linguistico al dominio de tickets sin ajuste fino. La posible degradacion de las representaciones preentrenadas ante el vocabulario del dominio SHALL presentarse como la razon de diseno por la que los autores excluyen los word embeddings, y MUST NOT presentarse como un hallazgo medido.

#### Scenario: Sin BERT ni 91 % atribuidos a Revina
- **WHEN** se lee la seccion 3.3 o la 8.2 en busca de las referencias a Revina et al. (2020)
- **THEN** no se le atribuye uso de BERT ni de modelos preentrenados
- **AND** no se le atribuye una exactitud cercana al 91 %
- **AND** no se le atribuye la conclusion de transferencia de modelos preentrenados al dominio

#### Scenario: Conclusion real de Revina et al. enunciada
- **WHEN** se lee la descripcion de Revina et al. (2020)
- **THEN** el texto enuncia que el articulo concluye que los metodos simples y explicables con un conjunto pequeno de rasgos linguisticos del dominio son competitivos para clasificar tickets de TI
- **AND** el texto presenta la posible degradacion de los embeddings preentrenados por el vocabulario especifico del dominio como argumento de diseno de los autores para excluirlos, no como resultado medido

#### Scenario: Ningun hallazgo medido sobre modelos preentrenados
- **WHEN** se leen las secciones 3.3, 8.1 y 8.2 en busca de afirmaciones sobre el rendimiento de los modelos preentrenados atribuidas a Revina et al. (2020)
- **THEN** ninguna las presenta como hallazgo, resultado u observacion empirica del articulo
- **AND** el argumento sobre los modelos preentrenados se enuncia una sola vez en la discusion, sin duplicarse en la comparacion con la literatura

#### Scenario: Tension incorporada en la discusion
- **WHEN** se lee la seccion 8.2 del capitulo de discusion
- **THEN** la evidencia de Revina et al. sobre la competitividad de los metodos simples y su argumento de diseno se integran como una tension explicita para el enfoque basado en LLM del presente trabajo
- **AND** la discusion explica por que esa tension fortalece (no debilita) el analisis

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

La seccion 1.7 SHALL enunciar los idiomas de los corpus de la literatura sobre clasificacion automatica de tickets solo en la medida en que los declaren las fuentes citadas o la tabla de trabajos academicos relevados (`tab:trabajos-academicos`). El documento MUST NOT atribuir a una fuente idiomas que esta no reporta, en particular corpus en aleman o portugues sin una fuente que los sostenga, y SHALL anclar la afirmacion en esa tabla o en una cita verificable que la sostenga. Las evaluaciones de LLM que incorporan el espanol SHALL describirse conforme a lo que esas obras evaluan.

#### Scenario: Afirmacion comparativa respaldada o reformulada
- **WHEN** se lee la seccion 1.7 del PDF compilado
- **THEN** la afirmacion sobre los idiomas de los corpus remite a la tabla de trabajos relevados o a una cita que la sostiene
- **AND** no queda una generalizacion sobre la literatura sin referencia

#### Scenario: Sin idiomas sin fuente
- **WHEN** se buscan menciones a corpus en aleman o en portugues en la seccion 1.7
- **THEN** no aparecen, o aparecen acompanadas de una cita que las sostiene
- **AND** `zangari2023ticket` y `colavito2025benchmarking` no se citan como respaldo de idiomas que sus resumenes no mencionan

#### Scenario: Coherencia con la tabla de trabajos relevados
- **WHEN** se compara la afirmacion de la seccion 1.7 con la columna de corpus e idioma de `tab:trabajos-academicos`
- **THEN** la afirmacion es coherente con lo que la tabla declara
- **AND** si la tabla incorpora un trabajo con corpus en espanol, la afirmacion se ajusta en consecuencia

#### Scenario: Sin duplicacion del trabajo bibliografico
- **WHEN** se revisa el diff del change
- **THEN** no se agregan ni modifican entradas de `Bibliography_base.bib`
- **AND** las referencias usadas ya existen por c-78

### Requirement: Atribucion editorial de ITIL Service Operation 2011

La seccion 2.2 SHALL atribuir la edicion de 2011 de ITIL Service Operation a The Stationery Office (TSO) por encargo del Cabinet Office, sin presentarla como una publicacion directa del Office of Government Commerce. La entrada `OGC2011_itil` de `Bibliography_base.bib` SHALL ser coherente con esa atribucion: autor corporativo Cabinet Office (o el que consigne el catalogo consultado, declarado en el registro de correcciones), editorial The Stationery Office y ninguna nota que atribuya el encargo al Office of Government Commerce. La clave `OGC2011_itil` MUST NOT renombrarse.

#### Scenario: Atribucion editorial correcta en el cuerpo
- **WHEN** se lee la seccion 2.2 del PDF compilado
- **THEN** la edicion de 2011 se atribuye a TSO/Cabinet Office
- **AND** no se afirma que el Office of Government Commerce sea el editor de la edicion de 2011

#### Scenario: Correccion bibliografica delegada
- **WHEN** se inspecciona la entrada `OGC2011_itil` y su referencia compilada
- **THEN** el autor corporativo, la editorial y la nota (si existe) son coherentes con la atribucion de la seccion 2.2
- **AND** ninguna nota atribuye el encargo de la edicion de 2011 al Office of Government Commerce

#### Scenario: Cita en el texto coherente con el autor
- **WHEN** se lee la cita de la seccion 2.2 en el PDF compilado
- **THEN** la cita muestra el autor corporativo de la entrada corregida
- **AND** la prosa conserva la mencion del Office of Government Commerce solo como titular historico

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

Toda afirmacion del §6.7 sobre la suite de integracion PostgreSQL SHALL declarar un
recuento igual al que devuelve `pytest -m integration --collect-only -q` sobre
`App/Backend` en el commit publicado, y SHALL describir el comportamiento ante la
ausencia de PostgreSQL tal como lo implementa `App/Backend/tests/conftest.py`: la suite
FALLA de forma ruidosa y MUST NOT declararse una omision automatica con `pytest.skip`.
Cuando la suite de frontend no pueda ejecutarse en el entorno documentado, el §6.7
SHALL omitir los recuentos numericos congelados y conservar la remision al reporte
vigente del pipeline, sin publicar un numero de pruebas ni de archivos que no se haya
reproducido.

#### Scenario: Sin afirmacion de pruebas e2e de N8N no verificable

- **WHEN** se busca en el repositorio una prueba que instancie N8N y ejecute el flujo completo hasta la persistencia
- **THEN** no existe ninguna prueba de ese tipo
- **AND** el §6.7 no afirma que tales pruebas existan o se hayan ejecutado

#### Scenario: Recuento y cobertura de frontend reproducibles

- **WHEN** se cuenta la suite de pruebas de frontend en HEAD y se genera el informe de cobertura con el comando documentado
- **THEN** las cifras declaradas en §6.7 coinciden con el resultado reproducible, o existe un informe de cobertura versionado que las respalda
- **AND** no queda publicada la cifra 89/98,6 % sin evidencia que la respalde

#### Scenario: Recuento de integracion PostgreSQL reproducible

- **WHEN** se ejecuta `cd App/Backend && pytest -m integration --collect-only -q` sobre el commit publicado
- **THEN** el recuento de pruebas de integracion que declara el §6.7 coincide con el total informado por el comando
- **AND** el §6.7 no describe una omision automatica con `pytest.skip` cuando PostgreSQL no esta disponible

#### Scenario: Comportamiento ante PostgreSQL ausente declarado

- **WHEN** se lee `App/Backend/tests/conftest.py` en el commit publicado
- **THEN** las fixtures de integracion fallan de forma ruidosa si PostgreSQL no esta disponible
- **AND** la tesis describe ese comportamiento y no el de una omision silenciosa

#### Scenario: Recuentos de frontend retirados si no son reproducibles

- **WHEN** la suite de frontend no puede ejecutarse en el entorno documentado por falta de dependencias instaladas
- **THEN** el §6.7 no publica recuentos numericos congelados de pruebas ni de archivos
- **AND** conserva la remision al reporte vigente del pipeline de integracion continua

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
clasificación (`73,5 %` de exactitud y macro-F1 de umbral `0,6508` sobre las cuatro
clases estimables, por debajo de `85 %` y `0,85`). El resumen MUST NOT permitir inferir una confirmación plena de la
hipótesis. La declaración SHALL distinguir las sub-hipótesis de tiempo,
intervención humana y exactitud o F1. La sub-hipótesis de intervención humana
SHALL declararse **no contrastada por ausencia de registro primario**, de forma coherente con
la retirada del `9,5 %` (c-107); el documento MUST NOT reintroducir esa cifra ni
presentarla como resultado. Las conclusiones SHALL declarar el estado por
sub-hipótesis: confirmada en tiempo, refutada en clasificación e intervención
humana no contrastada por ausencia de registro primario, junto con el estado de las
dos hipótesis subsidiarias.

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
- **THEN** la sub-hipótesis de intervención humana se declara no contrastada por ausencia de registro primario
- **AND** no se reporta el `9,5 %` de intervención humana como resultado vigente

#### Scenario: Estado por sub-hipótesis en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** se distingue explícitamente la sub-hipótesis confirmada (tiempo), la refutada (exactitud/F1) y la no contrastada (intervención humana)
- **AND** no se declara la hipótesis principal confirmada o refutada como bloque
- **AND** se declara el estado de las dos hipótesis subsidiarias

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

Los archivos `.tex` de `docs/Tesis/v10 (IA)/paper/sections/` SHALL presentar el
texto español acentuado conforme a las reglas ortográficas vigentes del español
(Ortografía de la lengua española, RAE-ASALE, 2010). La normalización SHALL
aplicarse a la prosa (cuerpo, encabezados, pies de página, pies de figura y tabla,
celdas de texto) incluyendo el texto dentro de argumentos de comandos portadores
de texto (`\section{}`, `\subsection{}`, `\caption{}`, `\textbf{}`, `\emph{}`,
`\item`, `\footnote{}`). El documento MUST NOT modificar tokens protegidos: las
cinco cadenas canónicas de categorías (`Seguridad Informatica`, `Soporte Tecnico
Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`), las claves
de `\label{}`/`\ref{}`/`\autoref{}`/`\cref{}`, las claves de
`\cite{}`/`\textcite{}`/`\parencite{}`, las rutas de
`\input{}`/`\includegraphics{}`/`\bibliography{}` y las rutas de repositorio en
prosa (`docs/Tesis/`, `evaluation/`, `data/`, `App/Backend`), el contenido de
`verbatim`/`lstlisting`/`\verb`, los argumentos de `\texttt{}`, las URLs y DOI, la
matemática, los nombres de comandos LaTeX, el resumen en inglés (desde
`\section*{Abstract}` hasta el fin de `00-resumen.tex`) y las palabras
correctamente acentuadas. Ninguna corrección SHALL des-acentuar una palabra
correctamente acentuada, duplicar tildes ni alterar cifras. Las tildes
improcedentes ---las diacríticas mal asignadas a un homógrafo (por ejemplo "hacía"
con valor de preposición o "fórmula" con valor verbal) y las de los demostrativos
y del adverbio "solo", que la ortografía vigente no prescribe--- SHALL retirarse
con justificación contextual registrada. La normalización MUST NOT editar
`Bibliography_base.bib` salvo las tildes del texto impreso en español de sus
campos `note` y `title`, sin alterar claves, autores, años, DOI, URL ni demás
metadatos.

#### Scenario: Prosa acentuada
- **WHEN** se busca en `sections/*.tex` una forma sin tilde de una palabra que la requiere (por ejemplo "clasificacion", "informacion", "metodologico", "Capitulo", "Introduccion", "erronea", "multiples")
- **THEN** no queda ninguna ocurrencia en prosa sin acentuar
- **AND** el texto correctamente acentuado permanece sin cambios (no se des-acentúa ni se duplica la tilde)

#### Scenario: Tildes improcedentes retiradas con justificación
- **WHEN** se inspeccionan las ocurrencias de "hacía", "fórmula", de los demostrativos con tilde y de "sólo" en `sections/*.tex`
- **THEN** "hacía" solo aparece como pretérito de "hacer", "fórmula" solo como sustantivo, y no quedan demostrativos con tilde ni "sólo"
- **AND** cada tilde retirada de un homógrafo consta con su justificación en el registro de decisiones de la revisión

#### Scenario: Tokens protegidos intactos
- **WHEN** se comparan antes y después las cinco cadenas canónicas de categorías, las claves de `\label`/`\ref`/`\autoref`, las claves de citas y las rutas de `\input`/`\includegraphics`
- **THEN** las claves y rutas forman un conjunto idéntico y ninguna ocurrencia previa de las cinco cadenas canónicas se altera
- **AND** ninguna cadena de categoría incorpora tilde

#### Scenario: Pares sensibles preservados
- **WHEN** se inspeccionan las ocurrencias de `hipótesis` y `síntesis`
- **THEN** se conservan exactamente acentuadas como corresponde
- **AND** no aparecen como `hipotesis`/`sintesis` ni con tilde duplicada

#### Scenario: Sin residuos de la herramienta
- **WHEN** se revisa el árbol de trabajo tras aplicar la normalización
- **THEN** no existen archivos `.tex.bak` nuevos
- **AND** ningún archivo de la tesis fuera de `paper/sections/`, `paper/main.tex`, `paper/preambles/preamble.tex`, `Bibliography_base.bib` y del render regenerado `tesis_para_agente.md` fue modificado por la normalización

### Requirement: Presupuesto de palabras del resumen en español

El resumen en español (`00-resumen.tex`) SHALL tener como máximo 250 palabras de
prosa. La reducción SHALL conservar el problema, el método y diseño (200 casos
pareados), los resultados clave (61,6~s a 17,76~s, reducción del 71,2~\%, \(W =
363\), \(r = 0,9639\), exactitud 73,5~\%, macro-F1 de umbral 0,6508 sobre las cuatro clases
estimables, Kappa de Cohen 0,87) y
la conclusión. El resumen MUST NOT reintroducir valores retirados por c-107 (la
intervención humana del 9,5~\% y el universo calendario 3.700) ni presentar la
hipótesis principal como plenamente confirmada. Si el resumen cita el macro-F1 de
cinco clases (0,5207), SHALL acompañarlo de su aclaración.

#### Scenario: Longitud del resumen
- **WHEN** se cuenta el número de palabras de prosa del cuerpo del resumen en español (excluyendo comandos LaTeX y la línea "Palabras clave")
- **THEN** el conteo es como máximo 250 palabras

#### Scenario: Cifras clave conservadas
- **WHEN** se lee el resumen reducido
- **THEN** aparecen 200 casos, 61,6~s, 17,76~s, 71,2~\%, \(W = 363\), \(r = 0,9639\), 73,5~\% y 0,6508 rotulado como macro-F1 de umbral
- **AND** el resumen no presenta la hipótesis principal como plenamente confirmada
- **AND** si aparece 0,5207, lo acompaña su aclaración

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

El change SHALL limitarse a `docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex`.
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

- **WHEN** se busca en `docs/Tesis/v10 (IA)/paper/sections/` y en el PDF compilado
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

### Requirement: Version de trabajo v10 y punteros activos consistentes

La version de trabajo vigente de la tesis SHALL ser `docs/Tesis/v10 (IA)/`, materializada como copia fiel de la version previamente publicada. Los punteros activos del proyecto —el campo `thesis:` de `openspec/config.yaml`, el estado actual declarado en `CHANGES.md`, las rutas activas de `openspec/specs/tesis-document/spec.md` y las rutas de trabajo de los changes dependientes de esta migracion— SHALL resolver a `docs/Tesis/v10 (IA)/`. La version previamente publicada `docs/Tesis/v9 (IA)/` SHALL conservarse intacta. Los registros historicos (entradas fechadas de `CHANGES.md`, dictamenes en `auditorias/`, bitacoras en `docs/Tesis/Correcciones/` y changes en `openspec/changes/archive/`) MUST NOT reescribirse para aparentar que apuntaban a v10.

#### Scenario: Existe la copia de trabajo v10 como espejo de v9

- **WHEN** se inspecciona el arbol de trabajo tras aplicar la migracion
- **THEN** existe el directorio `docs/Tesis/v10 (IA)/`
- **AND** contiene la fuente LaTeX `docs/Tesis/v10 (IA)/paper/main.tex`, la bibliografia `docs/Tesis/v10 (IA)/Bibliography_base.bib` y los textos extraidos `docs/Tesis/v10 (IA)/tesis_completa_extraida.txt` y `docs/Tesis/v10 (IA)/tesis_para_evaluacion.txt`
- **AND** la cantidad de archivos versionados de `docs/Tesis/v10 (IA)/` es igual a la de `docs/Tesis/v9 (IA)/`

#### Scenario: Los punteros activos resuelven a v10

- **WHEN** se inspeccionan los punteros activos del proyecto tras aplicar la migracion
- **THEN** el campo `thesis:` de `openspec/config.yaml` apunta a una ruta dentro de `docs/Tesis/v10 (IA)/`
- **AND** las entradas de estado actual de `CHANGES.md` designan `docs/Tesis/v10 (IA)/` como version de trabajo vigente
- **AND** las rutas activas de `docs/Tesis/v9 (IA)` en `openspec/specs/tesis-document/spec.md` fueron repuntadas a `docs/Tesis/v10 (IA)`, de modo que `grep -c "docs/Tesis/v9 (IA)" openspec/specs/tesis-document/spec.md` es 0

#### Scenario: La version publicada v9 permanece intacta

- **WHEN** se compara el arbol de `docs/Tesis/v9 (IA)/` con su estado previo a la migracion
- **THEN** no hay archivos agregados, modificados ni borrados bajo `docs/Tesis/v9 (IA)/`
- **AND** `git status` no reporta cambios para esa ruta

#### Scenario: Los registros historicos no se reescriben

- **WHEN** se inspeccionan los registros historicos que referencian v9 (entradas fechadas de `CHANGES.md`, archivos de `auditorias/`, archivos de `docs/Tesis/Correcciones/` y directorios de `openspec/changes/archive/`)
- **THEN** conservan sus referencias a `docs/Tesis/v9 (IA)` tal como estaban
- **AND** ninguna entrada fechada previa a la migracion fue reescrita para designar v10

### Requirement: Consistencia del parrafo introductorio con las columnas de la tabla comparativa del estado del arte

El parrafo introductorio de la tabla comparativa de soluciones (`\label{tab:comparativa}` en `03-estado-del-arte.tex`) SHALL declarar como dimensiones de comparacion exactamente las columnas de la tabla distintas de la clave de fila (`Solucion`), en un numero igual al de esas columnas, y SHALL NOT enunciar como dimension la clave de fila ni una propiedad que no tenga columna propia. La tabla SHALL conservar sus cuatro columnas (Solucion como clave de fila; Despliegue, Clasificacion automatica y Modelo de costo como dimensiones) y su rotulo. La sintesis comparativa posterior a la tabla SHALL NOT afirmar que las soluciones revisadas carecen de una propiedad que la tabla no releva; una propiedad sin columna que se conserve en la prosa SHALL presentarse como rasgo de la propuesta o del contexto y no como resultado de la comparacion.

#### Scenario: Dimensiones declaradas coinciden con las columnas

- **WHEN** se lee el parrafo introductorio de `tab:comparativa` y se cuentan las columnas de la tabla
- **THEN** el numero de dimensiones enunciadas es igual al numero de columnas menos la clave de fila (tres)
- **AND** ni "la solucion considerada" ni otra denominacion de la clave de fila figura entre las dimensiones enumeradas

#### Scenario: Sintesis respaldada por las columnas de la tabla

- **WHEN** se lee la sintesis comparativa posterior a `tab:comparativa`
- **THEN** cada propiedad que la sintesis declara ausente en las soluciones revisadas corresponde a una columna de la tabla
- **AND** el soporte de canales multiples con telefonia y transcripcion automatica no se afirma como carencia de las soluciones revisadas mientras la tabla no tenga una columna que lo releve

#### Scenario: Propiedades sin columna conservadas como prosa

- **WHEN** se leen el parrafo introductorio, la sintesis y el parrafo de posicionamiento posteriores a la tabla
- **THEN** las propiedades relevantes sin columna (por ejemplo, la soberania sobre los datos o el canal telefonico con transcripcion automatica) se mantienen en la prosa circundante como rasgos de la propuesta o del contexto
- **AND** no se elimina del texto ninguna propiedad sustantiva ni se la presenta como resultado de la comparacion

### Requirement: Hallazgo del gate de clasificacion presentado como resultado propio

La tesis SHALL presentar la conducta observada del gate de clasificacion en el corpus como un hallazgo empirico con valor propio sobre el comportamiento del clasificador en el dominio evaluado, ademas de su uso como justificacion de la sub-hipotesis no contrastada: la etapa Gemini nunca devolvio una confianza inferior a 0,85 en los 69 casos que resolvio, de modo que el gate de revision, que solo alcanza a esa etapa y a la de reserva, no derivo ningun caso; los 131 casos de la etapa deterministica no estan sujetos al gate. El hallazgo SHALL enunciarse en el capitulo de discusion y/o en la subseccion de intervencion humana de resultados (`subsec:reduccion-intervencion`), MUST NOT atribuirse a los 200 casos del corpus y MUST NOT introducir valores numericos distintos de los ya canonicos. La valoracion del hallazgo (fiabilidad o sobreconfianza del modelo) SHALL ser coherente con el analisis de calibracion por etapa.

#### Scenario: Hallazgo enunciado con su alcance correcto

- **WHEN** se lee el capitulo de discusion y/o la subseccion de intervencion humana de resultados
- **THEN** se declara que la etapa Gemini nunca devolvio una confianza inferior a 0,85 en los 69 casos que resolvio
- **AND** no se afirma que esa conducta abarque los 200 casos del corpus

#### Scenario: Hallazgo enunciado como resultado positivo

- **WHEN** se lee la enunciacion del hallazgo
- **THEN** se presenta como resultado empirico propio sobre el clasificador y no solo como motivo de la no contraste de la sub-hipotesis
- **AND** su valoracion no contradice la conclusion del analisis de calibracion por etapa

#### Scenario: Sin numeros nuevos

- **WHEN** se revisa el texto agregado para el hallazgo del gate
- **THEN** no aparece ningun valor numerico que no figure ya en `docs/Tesis/Correcciones/numeros-canonicos.md`
- **AND** el umbral 0,85 y el umbral 0,70 del gate se citan con el mismo valor y sentido que en el resto del documento

### Requirement: Cobertura bibliografica formal de las plataformas comerciales

Toda mencion a las plataformas comerciales Zendesk, Freshdesk y ServiceNow en `01-introduccion.tex` SHALL acompanarse de una entrada bibliografica formal en `Bibliography_base.bib` y de su cita en el texto. Cada entrada nueva SHALL tiparse como `@online` e incluir entidad autora, titulo, ano, `url` y `urldate`, siguiendo el patron de las entradas `DigitalOcean2026_pricing` y `Google2026_vertex_pricing`. La fecha de consulta SHALL declararse una sola vez, en `urldate`; la `note`, cuando exista, SHALL declarar la pagina de documentacion de la plataforma y MUST NOT repetir la fecha. El documento MUST NOT introducir cifras de precio no verificables: cuando no exista una figura comprobable, la `note` SHALL declarar la pagina de documentacion de la plataforma y la prosa SHALL mantenerse como observacion de relevamiento.

#### Scenario: Entradas y citas incorporadas
- **WHEN** se inspecciona `Bibliography_base.bib` y `01-introduccion.tex`
- **THEN** existen entradas `@online` para Zendesk, Freshdesk y ServiceNow con `url`, `urldate = {2026-10-19}` y una `note` que declara la pagina de documentacion sin repetir la fecha
- **AND** la mencion a las tres plataformas en la introduccion se acompana de `\parencite` a esas entradas

#### Scenario: Fecha de consulta impresa una sola vez
- **WHEN** se lee la bibliografia compilada
- **THEN** cada una de las cinco entradas `@online` (DigitalOcean, Google Cloud, Zendesk, Freshdesk y ServiceNow) imprime la fecha de consulta una sola vez
- **AND** ninguna `note` de esas entradas contiene la fecha de consulta

#### Scenario: Sin cifras de precio fabricadas
- **WHEN** se revisa la prosa y la `note` de las entradas nuevas
- **THEN** no se afirma ninguna cifra de precio o de capacidad que no pueda verificarse contra la pagina de documentacion citada
- **AND** la formulacion se mantiene como observacion de relevamiento propio declarado

#### Scenario: Correspondencia citas-bibliografia preservada
- **WHEN** se ejecuta la verificacion de citas contra `Bibliography_base.bib` tras agregar las entradas
- **THEN** no se introduce ninguna cita huerfana
- **AND** no queda ninguna entrada nueva sin usar

### Requirement: Etiqueta de la release v1.1.0 y trazabilidad del hash

La version de trabajo de la tesis `docs/Tesis/v10 (IA)/` SHALL publicarse mediante un tag anotado `v1.1.0` creado sobre el commit que cierra la migracion a v10 (c-122) y las tres observaciones del dictamen (este change). El manuscrito (`sections/12-anexos.tex`, `sec:anexo-repositorio`) SHALL identificar la version entregada con el tag `v1.1.0` y consignar el hash completo de 40 caracteres del commit etiquetado, coincidente con `git rev-parse v1.1.0^{commit}`. Los tags previos `v1.0.0` y `v1.0.1` MUST NOT moverse.

#### Scenario: Tag anotado v1.1.0 sobre el commit de cierre

- **WHEN** se ejecuta `git cat-file -t v1.1.0` y `git rev-parse v1.1.0^{commit}`
- **THEN** el tag existe, es anotado (devuelve `tag`, no `commit`) y apunta a un commit posterior a la aplicacion de c-122 y c-121
- **AND** el tag esta publicado en `origin` (`git ls-remote --tags origin v1.1.0` lo devuelve)

#### Scenario: Hash consignado y coherente con el tag

- **WHEN** se lee `sec:anexo-repositorio` en `12-anexos.tex` y se compara con `git rev-parse v1.1.0^{commit}`
- **THEN** figura el tag `v1.1.0` y el hash completo de 40 caracteres del commit etiquetado
- **AND** el hash coincide en los 40 caracteres y tambien figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Tags previos inmutables

- **WHEN** se comparan `git rev-parse v1.0.0^{commit}` y `git rev-parse v1.0.1^{commit}` con sus valores previos
- **THEN** `v1.0.0` sigue en `61a6b117dd1321fbee25f9792d9f29b884e5ac8d` y `v1.0.1` sigue en `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`
- **AND** ningun tag existente fue reescrito o re-creado

### Requirement: URL explicita del repositorio en el anexo de codigo fuente

El Anexo B de la tesis (`sec:anexo-repositorio` en `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`) SHALL mostrar de forma explicita la URL del repositorio publico del proyecto, ademas de la cita bibliografica existente, de modo que el lector no deba reconstruir la direccion desde la seccion de Referencias. La URL SHALL ser `https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N` y SHALL presentarse como enlace visible (no solo como destino de hipervinculo). El anexo SHALL conservar la prosa introductoria y la cita `\parencite{Gomez2026_repositorio}`.

#### Scenario: La URL aparece en el cuerpo del anexo

- **GIVEN** el PDF compilado de la tesis
- **WHEN** se lee el Anexo B, seccion "Repositorio de codigo fuente" (`sec:anexo-repositorio`)
- **THEN** la URL `https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N` figura de forma explicita en el cuerpo del anexo
- **AND** la URL se renderiza como texto visible y clicable, sin depender de la seccion de Referencias

#### Scenario: Cita y prosa existentes preservadas

- **WHEN** se comparan el Anexo B modificado y su version previa al change
- **THEN** la cita `\parencite{Gomez2026_repositorio}` permanece en el anexo
- **AND** la prosa introductoria del repositorio se conserva sin eliminar ninguna oracion sustantiva

### Requirement: Coherencia de la version bibliografica con la release publicada

La entrada `Gomez2026_repositorio` de `docs/Tesis/v10 (IA)/Bibliography_base.bib` SHALL declarar en su titulo la misma version que la release publicada en el manuscrito. El titulo SHALL enunciar `(Version 1.1.1)` y SHALL NOT conservar la version obsoleta `(Version 1.0.0)`. Los demas campos de la entrada (autoria, ano, `url` y `note`) SHALL conservarse y la referencia SHALL seguir imprimiendose en la seccion de Referencias.

#### Scenario: Version bibliografica alineada con la release

- **WHEN** se inspecciona la entrada `Gomez2026_repositorio` en `Bibliography_base.bib`
- **THEN** el campo `title` enuncia `(Version 1.1.1)`
- **AND** no conserva la cadena `(Version 1.0.0)`

#### Scenario: Integridad de la entrada preservada

- **WHEN** se ejecuta la verificacion de citas contra `Bibliography_base.bib`
- **THEN** la entrada sigue existiendo y sigue siendo referenciada por la cita del anexo
- **AND** sus campos `author`, `year`, `url` y `note` se mantienen, sin introducir citas huerfanas ni entradas sin usar

### Requirement: Etiqueta de la release v1.1.1 y trazabilidad del hash

La version de trabajo de la tesis `docs/Tesis/v10 (IA)/` SHALL publicarse mediante un tag anotado `v1.1.1` creado sobre el commit que cierra las ediciones de este change. El manuscrito (`sections/12-anexos.tex`, `sec:anexo-repositorio`) SHALL identificar la version entregada con el tag `v1.1.1` y consignar el hash completo de 40 caracteres del commit etiquetado, coincidente con `git rev-parse v1.1.1^{commit}`; ese mismo hash SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El tag SHALL crearse SOLO despues de aplicar las ediciones de contenido y recompilar el PDF. Los tags previos `v1.0.0`, `v1.0.1` y `v1.1.0` MUST NOT moverse.

#### Scenario: Tag anotado v1.1.1 sobre el commit de cierre

- **WHEN** se ejecuta `git cat-file -t v1.1.1` y `git rev-parse v1.1.1^{commit}`
- **THEN** el tag existe, es anotado (devuelve `tag`, no `commit`) y apunta a un commit posterior a la aplicacion de este change
- **AND** el tag esta publicado en `origin` (`git ls-remote --tags origin v1.1.1` lo devuelve)

#### Scenario: Hash consignado y coherente con el tag

- **WHEN** se lee `sec:anexo-repositorio` en `12-anexos.tex` y se compara con `git rev-parse v1.1.1^{commit}`
- **THEN** figura el tag `v1.1.1` y el hash completo de 40 caracteres del commit etiquetado
- **AND** el hash coincide en los 40 caracteres y tambien figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Tags previos inmutables

- **WHEN** se comparan `git rev-parse v1.0.0^{commit}`, `git rev-parse v1.0.1^{commit}` y `git rev-parse v1.1.0^{commit}` con sus valores previos
- **THEN** `v1.0.0` sigue en `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` sigue en `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0` y `v1.1.0` sigue en `7103b649d8c4f51737ad6ad4095dad22c9406400`
- **AND** ningun tag existente fue reescrito o re-creado

### Requirement: Procedencia declarada de los ajustes realizados sobre el corpus de validacion

La tesis SHALL declarar en la discusion (`subsec:interpretacion-resultados`) que el vocabulario del filtro deterministico (c-71), las reglas de frontera del prompt (c-72) y el punto de operacion del cortocircuito (c-74) se derivaron de casos y errores observados en el corpus de validacion de 200 casos; SHALL acotar que la mitigacion fuera de muestra de c-74 (validacion cruzada de cinco pliegues para el punto de operacion) NO cubre la ampliacion del vocabulario ni las reglas del prompt; SHALL declarar que no se dispuso de un corpus independiente de preproduccion; y SHALL calificar las metricas de clasificacion como estimaciones dentro de la muestra cuya confirmacion exige un corpus independiente. Las demas secciones que afirman la ausencia de exposicion al corpus (`05-arquitectura.tex`, `06-implementacion.tex`, Anexo H) SHALL alinearse con esa declaracion o remitir a ella. La tesis MUST NOT afirmar separacion estricta entre datos de construccion y de validacion, ausencia de exposicion al corpus ni desempeno sobre datos no vistos; MUST NOT afirmar la existencia de un conjunto de aproximadamente 100 incidentes de preproduccion ni remitir a `docs/prompt_gemini_history/`; y MUST NOT alterar ningun valor numerico por esta declaracion.

#### Scenario: Procedencia de los tres ajustes declarada

- **WHEN** se lee `subsec:interpretacion-resultados` en el PDF compilado
- **THEN** se declaran los ajustes del vocabulario del filtro deterministico, de las reglas de frontera del prompt y del punto de operacion realizados sobre el corpus de validacion
- **AND** las metricas de clasificacion se califican como estimaciones dentro de la muestra

#### Scenario: Mitigacion fuera de muestra acotada

- **WHEN** se lee la declaracion de procedencia
- **THEN** la mitigacion fuera de muestra de c-74 se acota al punto de operacion
- **AND** se declara expresamente que esa mitigacion no cubre el vocabulario ni las reglas del prompt

#### Scenario: Sin corpus independiente de preproduccion

- **WHEN** se busca en `sections/*.tex` una afirmacion sobre un corpus independiente de incidentes de preproduccion
- **THEN** se declara que no se dispuso de un corpus de esas caracteristicas
- **AND** no se afirma la existencia de un conjunto de aproximadamente 100 incidentes de preproduccion

#### Scenario: Sin afirmacion de no exposicion

- **WHEN** se buscan en `sections/*.tex` las afirmaciones "sin exposicion a" (el corpus o los 200 casos de validacion), "sin acceso al corpus", "datos no vistos" y "separacion estricta"
- **THEN** ninguna aparece como afirmacion vigente sobre la version evaluada

#### Scenario: Numeros intactos

- **WHEN** se comparan las metricas de clasificacion del PDF antes y despues de la declaracion
- **THEN** no cambia ningun valor numerico

### Requirement: Ubicacion veraz de las versiones historicas del prompt en el Anexo H

El Anexo H (`12-anexos.tex`) y su documento fuente `docs/anexo_h_prompt_gemini.md` SHALL ubicar las versiones historicas del prompt en el historial de versiones del repositorio para `docs/prompt_gemini.txt` y MUST NOT remitir a `docs/prompt_gemini_history/`, que no existe en el repositorio. `docs/anexo_h_prompt_gemini.md` MUST NOT afirmar que el prompt se ajusto sin exposicion al corpus de validacion ni sobre aproximadamente 100 incidentes de preproduccion, y SHALL declarar que las reglas de frontera de la version evaluada se incorporaron a partir de errores observados en ese corpus.

#### Scenario: Sin remision a un directorio inexistente

- **WHEN** se busca `docs/prompt_gemini_history` en `sections/*.tex` y en `docs/anexo_h_prompt_gemini.md`
- **THEN** no aparece ninguna coincidencia

#### Scenario: Ubicacion correcta en el historial de versiones

- **WHEN** se lee la seccion de iteracion del prompt del Anexo H (`12-anexos.tex`) y de `docs/anexo_h_prompt_gemini.md`
- **THEN** ambas remiten al historial de versiones de `docs/prompt_gemini.txt`
- **AND** existe `git log -- docs/prompt_gemini.txt` con las versiones historicas

#### Scenario: Documento fuente alineado con la tesis

- **WHEN** se lee la seccion de iteracion del prompt de `docs/anexo_h_prompt_gemini.md`
- **THEN** no afirma ausencia de exposicion al corpus de validacion ni la existencia de un conjunto de incidentes de preproduccion
- **AND** declara el origen de las reglas de frontera y la ubicacion de las versiones historicas del prompt

### Requirement: Definicion de la confianza por etapa y del puntaje de correctitud

La tesis SHALL definir una sola vez, en la subseccion del subsistema de clasificacion de `05-arquitectura.tex` (`subsec:subsistema-clasificacion`), las dos magnitudes que emite la etapa deterministica: la confianza, como indice de fuerza de senal en [0;1] que vale 0 cuando el sector ganador reune menos de dos patrones coincidentes, y el puntaje de correctitud (`score_correctitud`), que ordena la correctitud esperada. La tesis SHALL declarar que ninguna de las dos es una probabilidad de acierto, que la confianza deterministica no es comparable con la confianza autodeclarada por el modelo de la etapa Gemini y que la etapa de reserva fija la confianza en 0,0 por construccion. Los capitulos `02`, `06`, `07`, `08` y `11` MUST usar las mismas denominaciones y MUST NOT atribuir a la decision del filtro deterministico una "alta certeza" o una "alta confianza".

#### Scenario: Dos magnitudes definidas

- **WHEN** se lee `subsec:subsistema-clasificacion` en el PDF compilado
- **THEN** se definen la confianza deterministica como indice de fuerza de senal en [0;1] y el puntaje de correctitud como criterio que ordena la correctitud esperada
- **AND** se declara que ninguna de las dos magnitudes es una probabilidad de acierto

#### Scenario: Confianza no comparable entre etapas

- **WHEN** se leen el eje human-in-the-loop de `02-marco-teorico.tex` y el subsistema de clasificacion de `05-arquitectura.tex`
- **THEN** la confianza de la etapa Gemini se denomina autodeclarada por el modelo
- **AND** se declara que la confianza deterministica no se compara con el umbral de revision

#### Scenario: Sin certeza atribuida al filtro

- **WHEN** se busca en `sections/*.tex` una atribucion de "alta certeza" o "alta confianza" a la decision del filtro deterministico
- **THEN** no aparece ninguna

### Requirement: Alcance del gate de revision humana declarado por etapa

La tesis SHALL declarar que la regla `requiere_revision_humana = (confianza < 0,70)` se evalua solo sobre la salida de la etapa Gemini, que la etapa de reserva deriva siempre a revision con confianza 0,0 y que la etapa deterministica no deriva a revision por su confianza. La descripcion del flujo en `06-implementacion.tex` SHALL enumerar las condiciones con que el backend activa el indicador de revision humana, incluida la derivacion por reportante no identificado en el directorio de empleados. Ningun capitulo MUST afirmar que el umbral de 0,70 alcanza a todos los casos ni que es el unico disparador automatico de revision humana.

#### Scenario: Grado de autonomia acotado por etapa en el marco teorico

- **WHEN** se lee `subsec:human-in-the-loop` en `02-marco-teorico.tex`
- **THEN** el grado adoptado por el sistema se describe como revision selectiva acotada por etapa
- **AND** no se afirma que todo caso con confianza inferior a 0,70 escala a revision humana

#### Scenario: Disparadores enumerados en la implementacion

- **WHEN** se lee la etapa de evaluacion del flujo en `06-implementacion.tex`
- **THEN** se enumeran la confianza de Gemini inferior a 0,70, la intervencion de la etapa de reserva y el reportante no identificado como condiciones del indicador
- **AND** no aparece la afirmacion de que el umbral de 0,70 es el unico disparador automatico de revision humana

#### Scenario: Coherencia entre capitulos

- **WHEN** se recorren las menciones al umbral de 0,70 en `02`, `05`, `06`, `07`, `08`, `11` y `12`
- **THEN** ninguna aplica el umbral a la etapa deterministica
- **AND** ninguna describe la cola de revision como destinada a los "casos de baja confianza" sin calificar

### Requirement: Criterio de cortocircuito y procedencia del punto de operacion

La tesis SHALL describir el cortocircuito de la etapa deterministica por su criterio vigente: senal dominante, sin ausencia de coincidencias ni empate, y puntaje de correctitud mayor o igual al punto de operacion 0,5166. La tesis SHALL declarar la procedencia del punto de operacion (validacion cruzada de cinco pliegues sobre el corpus con un piso comparativo: precision del filtro no inferior a la de la etapa Gemini sobre el conjunto que resuelve, 0,7405 frente a 0,6769), su equivalencia en el corpus (resolver los 131 casos con senal dominante) y el retiro del umbral de 0,90 sobre la confianza del diseno inicial. La tesis MUST NOT afirmar que el filtro decide cuando su confianza supera el 90 % y MUST NOT presentar el piso comparativo como garantia independiente de exactitud.

#### Scenario: Criterio vigente descrito

- **WHEN** se lee `subsec:subsistema-clasificacion` y la tabla `tab:capas`
- **THEN** el cortocircuito se describe por la senal dominante y el punto de operacion 0,5166 del puntaje de correctitud
- **AND** no aparece "superior al 90" ni "umbral de confianza preestablecido" como criterio de cortocircuito

#### Scenario: Procedencia y equivalencia declaradas

- **WHEN** se lee la descripcion del punto de operacion
- **THEN** se declara su derivacion por validacion cruzada de cinco pliegues sobre el corpus con el piso comparativo frente a Gemini
- **AND** se declara que en el corpus equivale a resolver los 131 casos con senal dominante

#### Scenario: Valores tomados del memo canonico

- **WHEN** se cotejan 0,5166, 0,7405, 0,6769 y 131 con `docs/Tesis/Correcciones/numeros-canonicos.md`
- **THEN** cada valor figura como `vigente` con su procedencia

### Requirement: Casos bajo el umbral no escalados consignados en resultados

La subseccion de intervencion humana del capitulo de resultados (`subsec:reduccion-intervencion`) SHALL consignar que 124 de los 200 casos (62 %) tuvieron una confianza registrada inferior a 0,70 sin ser escalados, que todos pertenecen a la etapa deterministica y que su confianza mide fuerza de senal y no se compara con el umbral; que los 69 casos de la etapa Gemini declararon siempre una confianza de al menos 0,85; que la etapa de reserva no se activo; y que sobre el 65,5 % de los casos no existio derivacion automatica por caso basada en la clasificacion. La subseccion MUST conservar su rotulo y MUST NOT introducir valores ausentes del memo canonico.

#### Scenario: Cifra de casos no escalados consignada

- **WHEN** se lee `subsec:reduccion-intervencion` en el PDF compilado
- **THEN** aparecen los 124 de 200 casos (62 %) con confianza inferior a 0,70 sin escalamiento
- **AND** se los atribuye a la etapa deterministica con la causa por la que no se comparan con el umbral

#### Scenario: Etapas Gemini y de reserva descritas

- **WHEN** se lee la misma subseccion
- **THEN** se declara que los 69 casos de la etapa Gemini declararon siempre una confianza de al menos 0,85
- **AND** se declara que la etapa de reserva no se activo

#### Scenario: Rotulo de la subseccion preservado

- **WHEN** se inspecciona `07-resultados.tex`
- **THEN** existe `\label{subsec:reduccion-intervencion}`
- **AND** las referencias cruzadas a esa subseccion resuelven sin advertencias

### Requirement: Alcance real de la salvaguarda de supervision humana en el capitulo legal

El capitulo de consideraciones eticas y legales (`11-aspectos-legales.tex`, subseccion `subsec:consentimiento-derechos`) SHALL declarar que el umbral de 0,70 solo alcanza a la etapa semantica y a la de reserva; que sobre el 65,5 % de los casos, resueltos por la etapa deterministica, no existe derivacion automatica por caso basada en la clasificacion; y que para esa fraccion la salvaguarda se limita al criterio de diseno con que se fijo el punto de operacion, estimado sobre el corpus de validacion, y a la reasignacion trazable del incidente, con la salvedad de su exposicion en la interfaz web. El capitulo MUST NOT presentar el umbral de 0,70 como salvaguarda de todos los casos ni el criterio comparativo como garantia independiente, y SHALL remitir la capacidad discriminante de la confianza del modelo al analisis de calibracion sin afirmar su resultado.

#### Scenario: Alcance de la salvaguarda declarado

- **WHEN** se lee la subseccion de supervision humana del capitulo legal
- **THEN** se declara que el umbral de 0,70 solo alcanza a la etapa semantica y a la de reserva
- **AND** se declara que sobre el 65,5 % de los casos no existe derivacion automatica por caso basada en la clasificacion

#### Scenario: Mitigaciones sin sobreafirmar

- **WHEN** se leen las mitigaciones declaradas para la etapa deterministica
- **THEN** el criterio de diseno del punto de operacion se califica como estimado sobre el corpus de validacion
- **AND** la reasignacion trazable se acompana de la salvedad sobre su exposicion en la interfaz web

#### Scenario: Remision a la calibracion

- **WHEN** se lee la oracion sobre la capacidad discriminante de la confianza
- **THEN** remite a `subsec:calibracion`
- **AND** no afirma por si misma una conclusion de calibracion

<!-- c-144 (archivado el 2026-10-23 en main) ya incorporo al spec vivo el requisito "Procedencia declarada de los ajustes realizados sobre el corpus de validacion"; este change solo verifica el texto resultante. -->

### Requirement: Umbral de revision humana en la especificacion del Anexo H

La tabla de parametros de configuracion del Anexo H (`tab:anexo_gemini_params`) SHALL incluir el umbral de revision humana (0,70) y declarar su alcance: se aplica a la confianza de la respuesta del modelo y no a la etapa deterministica. La fila MUST NOT desbordar la primera columna de la tabla.

#### Scenario: Fila del umbral presente

- **WHEN** se lee `tab:anexo_gemini_params` en el PDF compilado
- **THEN** existe una fila del umbral de revision humana con valor 0,70
- **AND** su justificacion declara que no se aplica a la etapa deterministica

#### Scenario: Sin desborde

- **WHEN** se revisa el registro de compilacion
- **THEN** no hay advertencias `Overfull \hbox` atribuibles a la fila agregada

### Requirement: Atribucion de roles del equipo coherente con la autoria registrada en el repositorio

La declaracion de la distribucion de roles del equipo en `04-marco-metodologico.tex` (parrafo de roles de la seccion 4.9) SHALL atribuir a cada integrante un rol que la historia del repositorio respalde. Quien no registre commits de desarrollo en el repositorio MUST NOT declararse autor del modulo Python ni del modelado de la base de datos; Carla Bustos SHALL presentarse como revisora de la tesis y colaboradora en los anexos y en la corroboracion de las fuentes utilizadas, o figurar entre los agradecimientos. Los roles de desarrollo (modulo Python y modelado de la base de datos, configuracion del flujo N8N e integracion telefonica) SHALL coincidir con la autoria real de cada componente segun el historial del repositorio, y la supervision academica del director SHALL conservarse.

#### Scenario: Roles de desarrollo coherentes con la autoria del repositorio

- **WHEN** se compara la distribucion de roles declarada en `04-marco-metodologico.tex` con la autoria de los componentes en la historia del repositorio
- **THEN** cada rol de desarrollo declarado corresponde a quien el repositorio registra como autor de ese componente
- **AND** la supervision academica del director se conserva

#### Scenario: Sin atribucion de desarrollo a quien no contribuyo al codigo

- **WHEN** se busca en `sections/*.tex` una atribucion del desarrollo del modulo Python o del modelado de la base de datos a Carla Bustos
- **THEN** no aparece ninguna
- **AND** Carla Bustos figura como revisora de la tesis y colaboradora en anexos y corroboracion de fuentes, o entre los agradecimientos

### Requirement: Tabla de tiempos por canal con brazo manual y contraste intra-canal

La tabla de tiempos por canal de origen (`\label{tab:tiempos-canal}` en `07-resultados.tex`) SHALL presentar, para cada canal (llamada telefonica, correo electronico, formulario web) y para el total, la cantidad de casos, la media y la mediana del tiempo manual, la media y la mediana del tiempo automatizado, la reduccion relativa de la media, la cantidad de pares en que el flujo automatizado no fue mas rapido, el valor p del contraste de Wilcoxon intra-canal sobre los pares del canal (bajo la convencion declarada) y el tamano del efecto estandarizado `d_z`. Todos los valores MUST coincidir con la seccion "Tiempos" de `evaluation/report.md` regenerada y con el valor vigente de `docs/Tesis/Correcciones/numeros-canonicos.md`. Los estadisticos de rango por canal (`W`, `T+`, `T-`, `r`) SHALL quedar disponibles en `evaluation/report.md` y la tabla o su nota SHALL remitir a ese reporte; la tabla y el texto MUST NOT presentar `W = 0` ni un tamano del efecto rank-biserial `r = 1,00` como resultado del contraste, en coherencia con el requisito "Rigor inferencial del tamano del efecto" (en los canales sin pares desfavorables el texto lo expresa como "el flujo automatizado fue mas rapido en todos los pares del canal"). El tamano del efecto `d_z` SHALL rotularse siempre como `d_z`, de modo que su valor global (1,00) no se confunda con el rank-biserial. La fila telefonica SHALL conservar su rotulo de cota inferior y la tabla SHALL conservar su linea de fuente. Toda afirmacion de la discusion sobre reducciones por canal SHALL remitir a esta tabla y MUST NOT presentar el contraste intra-canal apareado como un analisis pendiente.

#### Scenario: Brazo manual y contraste presentes por canal

- **WHEN** se lee `tab:tiempos-canal` en el PDF compilado
- **THEN** cada canal y el total muestran casos, media y mediana manual, media y mediana automatizada, reduccion relativa, pares no mas rapidos, p y `d_z`
- **AND** la fila "Global" reproduce los valores de `tab:tiempos` (61,6 s y 17,76 s de media)

#### Scenario: Sin W = 0 ni r = 1,00 en la tesis

- **WHEN** se buscan en las secciones de la tesis los resultados del contraste por canal
- **THEN** no aparece `W = 0` ni un rank-biserial `r = 1,00` presentado como resultado
- **AND** la ausencia de pares desfavorables en telefonia y formulario web se expresa con el conteo de pares no mas rapidos (0) y la remision al reporte, y todo `d_z` aparece rotulado como tal

#### Scenario: Afirmacion de la discusion verificable desde el texto

- **WHEN** se lee en `08-discusion.tex` la explicacion rival de la mezcla de canales
- **THEN** la afirmacion de reducciones positivas en los tres canales remite a `tab:tiempos-canal` y al contraste de Wilcoxon intra-canal ya realizado
- **AND** el texto no afirma que la explicacion "se descartaria con un contraste intra-canal apareado" como si ese contraste no existiera

#### Scenario: Valores trazables al reporte y al memo

- **WHEN** se compara cada celda numerica de `tab:tiempos-canal` con `evaluation/report.md` y con `numeros-canonicos.md`
- **THEN** cada valor coincide con el reporte regenerado (con el redondeo declarado) y figura en el memo con su procedencia y estado `vigente`
- **AND** la tabla declara su linea de fuente y la fila telefonica conserva el rotulo de cota inferior

### Requirement: Convencion declarada del valor p frente a la hipotesis direccional de tiempos

Cuando la primera sub-hipotesis de tiempos se formule con una alternativa direccional (`H1: M_manual > M_automatizado`), la tesis SHALL declarar explicitamente la convencion de los valores p que reporta para los contrastes de tiempos: los valores p reportados son bilaterales (variante de dos colas de `scipy.stats.wilcoxon`, coherente con `W = min(T+, T-)`) y, por lo tanto, conservadores respecto de la hipotesis direccional. La tesis SHALL informar al menos una vez el valor p unilateral del contraste global (`1,54e-32`), calculado por el framework con la variante direccional, en el capitulo de marco metodologico y en el enunciado de la sub-hipotesis. Los valores p bilaterales vigentes (`3,08e-32` global, escenarios de sensibilidad y contrastes por canal) MUST NOT cambiar de valor, y ningun valor p de tiempos MUST quedar sin convencion declarada.

#### Scenario: Convencion declarada en metodologia y en la hipotesis

- **WHEN** se leen la subseccion de analisis estadistico de `04-marco-metodologico.tex` y el enunciado de la primera sub-hipotesis en `01-introduccion.tex`
- **THEN** ambos declaran que el p reportado es bilateral y conservador frente a la alternativa direccional
- **AND** ambos informan el p unilateral global `1,54e-32`, igual al valor vigente del memo

#### Scenario: Valores bilaterales preservados

- **WHEN** se buscan los valores p de tiempos en `01-introduccion.tex` y `07-resultados.tex`
- **THEN** el p global bilateral sigue siendo `3,08e-32` con `W = 363`, `T+ = 19.737` y `T- = 363`
- **AND** los p de los escenarios de sensibilidad y de los contrastes por canal quedan cubiertos por la misma convencion declarada

### Requirement: Comparacion de potencia homogenea sobre el tamano del efecto d_z

El analisis de potencia del marco metodologico SHALL comparar el efecto minimo detectable, expresado como tamano del efecto estandarizado de muestras pareadas `d_z`, con el `d_z` observado, calculado como la media de las diferencias pareadas dividida por su desvio estandar muestral. El texto MUST NOT comparar el efecto minimo detectable con la reduccion relativa (71,2 %) ni con ninguna otra magnitud no estandarizada. SHALL declarar los supuestos del efecto minimo detectable (alfa, lateralidad, potencia, `n` y la eficiencia relativa asintotica usada para el ajuste de la prueba de rangos) y, cuando se citen contrastes por canal, SHALL comparar el `d_z` de cada canal con el efecto minimo detectable para su propio `n`.

#### Scenario: d_z observado frente al minimo detectable

- **WHEN** se lee el analisis de potencia en `04-marco-metodologico.tex`
- **THEN** el efecto minimo detectable (`d_z` aproximadamente 0,20; 0,21 con la eficiencia relativa asintotica declarada) se compara con el `d_z` observado de 1,00
- **AND** la reduccion relativa del 71,2 % no aparece como termino de esa comparacion

#### Scenario: Supuestos y valores trazables

- **WHEN** se verifican los valores de potencia citados
- **THEN** alfa, lateralidad, potencia, `n` y la eficiencia relativa asintotica estan declarados en el texto
- **AND** el `d_z` observado y los efectos minimos detectables global y por canal figuran en `numeros-canonicos.md` con procedencia en el reporte regenerado

### Requirement: Verificabilidad del muestreo y de la asignacion por sector

La descripcion del muestreo en `04-marco-metodologico.tex` SHALL ser verificable con la informacion que el documento aporta. Si la distribucion del universo por sector esta disponible, la tesis SHALL reportarla junto a la distribucion de la muestra para que la proporcionalidad sea comprobable. Si no esta disponible, la tesis SHALL declarar que la composicion por sector de la muestra refleja la distribucion observada en el periodo relevado y que su proporcionalidad respecto del universo no es verificable, y MUST NOT afirmar una proporcionalidad respecto del universo que el documento no permite comprobar. En ambos casos la tesis SHALL discutir la consecuencia de la asignacion resultante para Bases de Datos (`n = 1`, clase no estimable) y la alternativa de una asignacion no proporcional con sobremuestreo de las clases minoritarias para replicaciones. El resumen y el abstract MUST describir el muestreo de forma coherente con el capitulo 4.

#### Scenario: Universo por sector disponible

- **WHEN** el autor aporta la distribucion del universo por sector
- **THEN** el capitulo 4 la reporta junto a la distribucion muestral (85/67/31/16/1)
- **AND** cada cifra nueva figura en `numeros-canonicos.md` con su procedencia

#### Scenario: Universo por sector no disponible

- **WHEN** la distribucion del universo por sector no esta disponible
- **THEN** el capitulo 4 declara que la composicion de la muestra refleja la distribucion observada en el periodo relevado y que la proporcionalidad frente al universo no es verificable
- **AND** el texto no afirma un muestreo proporcional al universo sin respaldo

#### Scenario: Asignacion de Bases de Datos discutida

- **WHEN** se lee la descripcion del muestreo
- **THEN** se explica que la asignacion dejo a Bases de Datos con un unico caso, no estimable para la inferencia por clase
- **AND** se menciona la asignacion no proporcional con sobremuestreo de clases minoritarias como alternativa para replicaciones

#### Scenario: Resumen y abstract coherentes

- **WHEN** se comparan `00-resumen.tex` (resumen y abstract) con el capitulo 4
- **THEN** la caracterizacion del muestreo es la misma en los tres lugares
- **AND** el abstract no conserva "proportional stratified sampling" si el capitulo 4 declara la proporcionalidad como no verificable

### Requirement: Procedimiento de cronometraje precisado y compatible con la mitigacion del efecto Hawthorne

La tesis SHALL describir el procedimiento de cronometraje manual de forma unica y precisa en `04-marco-metodologico.tex` (diseno experimental e instrumentos), `08-discusion.tex` (explicacion rival del efecto Hawthorne) y `11-aspectos-legales.tex` (sesion de esclarecimiento): quien cronometro, que conocia el operador cronometrado durante la campana, que aspecto concreto no se anuncio y que se informo en el debriefing. El texto MUST NOT afirmar a la vez que el cronometraje no fue anunciado al operador y que un companero lo cronometraba en vivo sin explicar como ambas afirmaciones son compatibles. SHALL declarar la granularidad observada de los registros manuales (valores multiplos de 5 s y mayormente de 10 s, verificable en el corpus) y su relacion con los escenarios de sensibilidad de 5 s y 10 s. Si el procedimiento no elimina el efecto Hawthorne, la tesis SHALL presentarlo como atenuado y residual, no como mitigado por completo.

#### Scenario: Sin contradiccion entre medicion no anunciada y cronometraje en vivo

- **WHEN** se leen la subseccion de diseno experimental y la de instrumentos de `04-marco-metodologico.tex`
- **THEN** el texto explica que conocia el operador y que aspecto de la medicion no se anuncio
- **AND** no subsisten juntas, sin explicacion, "no fue anunciado en tiempo real" y "lo cronometro en vivo el companero"

#### Scenario: Relato consistente entre capitulos

- **WHEN** se comparan `04-marco-metodologico.tex`, `08-discusion.tex` y `11-aspectos-legales.tex`
- **THEN** los tres describen el mismo procedimiento y el mismo alcance del conocimiento diferido
- **AND** el efecto Hawthorne figura como atenuado y residual si el procedimiento no lo elimina

#### Scenario: Granularidad declarada y verificable

- **WHEN** se lee la descripcion del instrumento manual
- **THEN** declara que los registros son multiplos de 5 s (199 de 200) y mayormente de 10 s (180 de 200)
- **AND** esas cifras coinciden con la granularidad emitida por el reporte de evaluacion y figuran en `numeros-canonicos.md`

### Requirement: Convencion unica del desvio estandar y correspondencia de los estadisticos de tiempo declarados

Todos los desvios estandar de tiempos que la tesis reporte SHALL usar la misma convencion que el framework de evaluacion (desvio muestral, divisor `n - 1`). El desvio del flujo automatizado SHALL reportarse como 13,52 s, y el valor 13,48 s (convencion poblacional) MUST NOT aparecer en las fuentes. Los estadisticos de tiempo que el marco metodologico declara como parte de la metrica de tiempo MUST coincidir con los que el capitulo de resultados efectivamente reporta.

#### Scenario: Desvio automatizado unificado

- **WHEN** se buscan los desvios estandar de tiempos en `07-resultados.tex` y `08-discusion.tex`
- **THEN** el desvio automatizado es 13,52 s y el manual 44,9 s, ambos con divisor `n - 1`
- **AND** `13,48` no aparece en ninguna seccion y figura como `retirado` en `numeros-canonicos.md`

#### Scenario: Estadisticos declarados igual a reportados

- **WHEN** se compara la definicion de la metrica de tiempo en `04-marco-metodologico.tex` con `tab:tiempos` y `tab:tiempos-canal`
- **THEN** cada estadistico declarado (media, mediana, desvio, minimo, maximo y los que se agreguen) se reporta en resultados
- **AND** no se declara un intervalo de confianza del tiempo medio que el capitulo de resultados no informe

### Requirement: Exactitud por etapa del pipeline en resultados

El capitulo de resultados SHALL reportar la exactitud estricta de cada etapa del pipeline con su IC de Wilson al 95% ---etapa deterministica `97/131`, etapa Gemini `50/69`, etapa fallback sin casos--- y, cuando se disponga de predicciones por caso, tambien su exactitud laxa. La mencion de la distribucion de casos por etapa (131/69/0) SHALL conservarse. Todo valor por etapa MUST figurar en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia.

#### Scenario: Exactitud por etapa presente

- **WHEN** se lee el capitulo de resultados
- **THEN** se reporta la exactitud estricta de la etapa deterministica (0,7405; 97/131) y de la etapa Gemini (0,7246; 50/69), cada una con su IC de Wilson al 95%
- **AND** se declara que la etapa fallback no registro casos

#### Scenario: Valores por etapa trazables

- **WHEN** se compara cada valor por etapa citado en la tesis con el memo de numeros canonicos
- **THEN** cada valor figura en el memo con procedencia y estado `vigente`

### Requirement: Exactitud laxa reportada junto a la estricta

El marco metodologico SHALL definir la exactitud laxa como la proporcion de casos cuyo sector predicho principal pertenece al conjunto de sectores de verdad del caso (sector asignado o sectores adicionales), como metrica secundaria operativa distinta de la exactitud estricta. El capitulo de resultados SHALL reportarla con su IC de Wilson al 95% junto a la exactitud estricta, y la discusion SHALL leerla como la proporcion de derivaciones operativamente aceptables. La exactitud laxa MUST NOT presentarse como metrica primaria ni como cumplimiento del umbral del segundo objetivo especifico: el estado de ese objetivo lo fija la metrica primaria declarada. Si no se dispone de predicciones por caso para calcularla, la tesis SHALL declararla no computable con los artefactos disponibles y MUST NOT consignar un valor estimado.

#### Scenario: Definicion en el marco metodologico

- **WHEN** se lee el analisis estadistico del marco metodologico
- **THEN** la exactitud laxa se define como la pertenencia del sector predicho principal al conjunto de sectores de verdad del caso
- **AND** se la distingue de la exactitud estricta y se la rotula como metrica secundaria

#### Scenario: Valor con intervalo en resultados

- **WHEN** se lee la subseccion de metricas de clasificacion
- **THEN** la exactitud laxa figura con sus aciertos, su proporcion y su IC de Wilson junto a la exactitud estricta
- **AND** su valor no es inferior al de la exactitud estricta (147/200)

#### Scenario: Sin reemplazo de la metrica primaria

- **WHEN** se leen la discusion y las conclusiones
- **THEN** la exactitud laxa no se presenta como metrica primaria ni como evidencia de cumplimiento del umbral del 85% del segundo objetivo especifico

#### Scenario: Exactitud laxa no computable declarada

- **WHEN** las predicciones por caso no estan disponibles al aplicar el change
- **THEN** la tesis declara que la exactitud laxa no es computable con los artefactos disponibles
- **AND** no consigna ningun valor estimado de exactitud laxa

### Requirement: Exactitud de clasificacion por canal de origen

El capitulo de resultados SHALL reportar la exactitud estricta y laxa de clasificacion por canal de origen (llamada telefonica, correo electronico y formulario web), con la cantidad de casos por canal y su IC de Wilson al 95%, en una tabla compacta que reuna los desgloses por etapa y por canal. La discusion SHALL leerla como evidencia de la dimension de calidad del tercer objetivo especifico y del efecto potencial de la transcripcion telefonica, y SHALL advertir que la comparacion entre canales no aisla ese efecto porque la composicion sectorial y la proporcion de casos multietiqueta difieren entre canales. La tesis MUST NOT atribuir causalmente a la transcripcion una diferencia entre canales. Si no se dispone de predicciones por caso, SHALL declararla no computable sin consignar valores.

#### Scenario: Tabla por canal presente

- **WHEN** se lee la subseccion de metricas de clasificacion
- **THEN** una tabla reporta, para cada canal de origen (81, 66 y 53 casos), la exactitud estricta y la laxa con su IC de Wilson
- **AND** la suma de los casos por canal es 200

#### Scenario: Salvedad de composicion entre canales

- **WHEN** se lee la interpretacion de la exactitud por canal en la discusion
- **THEN** se advierte que la composicion sectorial y la proporcion multietiqueta difieren entre canales
- **AND** no se atribuye a la transcripcion telefonica, como causa, una diferencia de exactitud entre canales

#### Scenario: Exactitud por canal no computable declarada

- **WHEN** las predicciones por caso no estan disponibles al aplicar el change
- **THEN** la tesis declara que la exactitud por canal no es computable con los artefactos disponibles
- **AND** no consigna ningun valor de exactitud por canal

### Requirement: Propagacion de la lectura de calibracion por etapa

Los capitulos de discusion (`08-discusion.tex`), conclusiones (`09-conclusiones.tex`) y aspectos eticos y legales (`11-aspectos-legales.tex`) SHALL reflejar la lectura de calibracion por etapa: donde citen el analisis de calibracion o el umbral de 0,70 como salvaguarda, SHALL restringir la afirmacion de no discriminacion a la confianza de la etapa Gemini dentro de su rango observado y declarar que la etapa de reglas no emite una confianza utilizable para derivar. Los rotulos `subsec:calibracion`, `tab:bandas` y `subsec:matriz-metricas` SHALL conservarse, porque otros capitulos los referencian. El change MUST NOT editar la tabla de cumplimiento de objetivos, la tabla de tiempos por canal ni el capitulo de recomendaciones, que pertenecen a otros changes del plan de correccion.

#### Scenario: Discusion y capitulo legal coherentes con la lectura por etapa

- **WHEN** se leen los pasajes de `08-discusion.tex` y `11-aspectos-legales.tex` que citan el analisis de calibracion o el umbral de 0,70
- **THEN** la afirmacion de no discriminacion se restringe a la confianza de la etapa Gemini dentro de su rango observado
- **AND** se declara que la etapa de reglas no emite una confianza utilizable como criterio de derivacion

#### Scenario: Conclusiones con la exactitud por etapa

- **WHEN** se lee el parrafo de conclusiones sobre el clasificador hibrido
- **THEN** se cita la exactitud estricta de cada etapa y, si fueron computables, la exactitud laxa y la exactitud por canal

#### Scenario: Rotulos preservados

- **WHEN** se compila el documento tras el change
- **THEN** los rotulos `subsec:calibracion`, `tab:bandas` y `subsec:matriz-metricas` existen y no hay referencias indefinidas

#### Scenario: Limites con los changes hermanos

- **WHEN** se inspecciona el diff del change sobre las fuentes `.tex`
- **THEN** no se modifican las filas de `tab:cumplimiento-objetivos`, la tabla `tab:tiempos-canal` ni `10-recomendaciones.tex`

### Requirement: Impacto de paginas de las metricas por etapa, canal y exactitud laxa

El change SHALL dejar el PDF compilado en 101 paginas o menos. La reestructuracion de `tab:bandas` SHALL reemplazar la tabla de bandas vigente en lugar de agregar una tabla nueva de bandas, y los desgloses por etapa y por canal SHALL reunirse en una unica tabla compacta. Si tras las compensaciones previstas el PDF supera las 101 paginas, el exceso SHALL registrarse con su causa y la decision final del tope SHALL delegarse al change de integracion de la release (c-141). El change MUST NOT eliminar contenido cientifico, numeros canonicos, figuras ni tablas con linea de fuente para compensar paginas.

#### Scenario: Tope de paginas respetado o exceso registrado

- **WHEN** se compila `main.tex` tras aplicar el change y se cuenta el total de paginas
- **THEN** el total es 101 o menos
- **AND** si es mayor, el exceso y su causa quedan registrados para c-141 sin haberse eliminado contenido cientifico

#### Scenario: Sin tabla de bandas duplicada

- **WHEN** se buscan las tablas de bandas de confianza en `07-resultados.tex`
- **THEN** existe una unica tabla de bandas (`tab:bandas`), desagregada por etapa

### Requirement: Analisis de sensibilidad frente al ajuste del clasificador con el corpus en resultados

El capitulo de resultados (`07-resultados.tex`) SHALL incluir la subseccion `subsec:sensibilidad-ajustes`, que: enuncia el metodo (re-medicion de la etapa deterministica sin invocar al modelo con el vocabulario previo a su ampliacion con el corpus, conservando la logica de decision y el punto de operacion evaluados, y referencia con la logica de entonces junto con el resultado de su control de fidelidad); declara no factible la reconstruccion del vocabulario por pliegues y su motivo; presenta una tabla compacta `tab:sensibilidad-ajustes` con la configuracion evaluada y las variantes (casos resueltos por la etapa y exactitud con su IC de Wilson al 95 %, y la exactitud global con Gemini fijo solo si es computable); informa el efecto de las reglas de frontera del prompt con el mayor nivel de evidencia disponible o declara que no se cuantifico; y lee los resultados segun las reglas pre-registradas en el diseno del change. Todo valor citado SHALL coincidir con el memo de numeros canonicos. La subseccion MUST NOT afirmar la ausencia de sesgo, MUST NOT presentar metricas obtenidas sobre el corpus como estimaciones fuera de la muestra y MUST NOT modificar ningun valor canonico.

#### Scenario: Subseccion y tabla presentes

- **WHEN** se compila el documento y se lee el capitulo de resultados
- **THEN** existe `subsec:sensibilidad-ajustes` con la tabla `tab:sensibilidad-ajustes`, que incluye la configuracion evaluada (131 casos, 0,7405 con su IC) y las variantes con casos, exactitud e IC
- **AND** las referencias a ambos rotulos resuelven sin advertencias

#### Scenario: Valores trazables al memo

- **WHEN** se coteja cada valor de la subseccion con `docs/Tesis/Correcciones/numeros-canonicos.md`
- **THEN** cada valor figura en la seccion de sensibilidad del memo con su procedencia

#### Scenario: Lectura de una exactitud menor como cota pesimista

- **WHEN** la exactitud de la variante principal es menor que 0,7405
- **THEN** la diferencia se presenta como cota pesimista del sesgo atribuible al vocabulario, con la razon por la que lo es
- **AND** no se la presenta como estimacion puntual del sesgo

#### Scenario: Lectura de una exactitud no menor

- **WHEN** la exactitud de la variante principal no es menor que 0,7405
- **THEN** se declara que el analisis no detecta un sesgo atribuible al vocabulario, sin descartarlo, por la diferencia entre los conjuntos de casos comparados

#### Scenario: Efecto del prompt informado o declarado

- **WHEN** se lee la subseccion
- **THEN** el efecto de las reglas de frontera sobre los 69 casos de la etapa Gemini figura con su nivel de evidencia y su contraste pareado, o se declara no cuantificado

#### Scenario: Columna global solo si es computable

- **WHEN** la exactitud global con Gemini fijo no fue computable
- **THEN** la tabla no incluye esa columna ni su nota

### Requirement: Sesgo optimista acotado en las limitaciones y en la evidencia del objetivo especifico 6

La subseccion `subsec:limitaciones-estudio` de `08-discusion.tex` SHALL incluir una limitacion que declare que el vocabulario del filtro deterministico y las reglas de frontera del prompt se ajustaron con errores observados en el corpus de evaluacion, que las metricas de clasificacion son estimaciones dentro de la muestra, la cota que aporta el analisis de sensibilidad con remision a `subsec:sensibilidad-ajustes`, y que solo un corpus independiente permitiria estimar el desempeno fuera de la muestra. El cardinal de la oracion introductoria de esa subseccion SHALL coincidir con la cantidad de limitaciones enumeradas. El parrafo de procedencia de los datos de ajuste en `subsec:interpretacion-resultados` SHALL remitir a `subsec:sensibilidad-ajustes`. La celda de evidencia del objetivo especifico 6 en `tab:cumplimiento-objetivos` SHALL incluir la referencia a `subsec:sensibilidad-ajustes` y la salvedad de estimacion dentro de la muestra; este requisito MUST NOT alterar el estado de ningun objetivo.

#### Scenario: Limitacion presente y cardinal coherente

- **WHEN** se lee `subsec:limitaciones-estudio`
- **THEN** una limitacion declara el ajuste con el corpus, la naturaleza dentro de la muestra de las metricas y la cota del analisis de sensibilidad, con remision a la subseccion
- **AND** el cardinal de la oracion introductoria coincide con la cantidad de items de la lista

#### Scenario: Remision desde la interpretacion

- **WHEN** se lee el parrafo de procedencia de los datos de ajuste en `subsec:interpretacion-resultados`
- **THEN** remite a `subsec:sensibilidad-ajustes` sin repetir sus valores

#### Scenario: Evidencia del objetivo 6 sin cambio de estado

- **WHEN** se lee la fila del objetivo especifico 6 en `tab:cumplimiento-objetivos`
- **THEN** su evidencia incluye `subsec:sensibilidad-ajustes` y la salvedad de estimacion dentro de la muestra
- **AND** su estado es el que fijen los autores y el change dueno de los estados, sin cambio introducido por este requisito

### Requirement: Calificacion dentro de la muestra de la exactitud deterministica y del contraste entre etapas

Toda aparicion en `sections/*.tex` de la exactitud de la etapa deterministica (`97/131`, `0,7405`) y de la comparacion entre etapas sobre el conjunto cortocircuitable (`0,7405` frente a `0,6769`; `88/130`) SHALL figurar en una oracion o parrafo que la califique como estimacion dentro de la muestra o que remita a `subsec:sensibilidad-ajustes`. La cuantificacion del sesgo SHALL residir solo en `subsec:sensibilidad-ajustes`; los demas pasajes SHALL limitarse a calificar o remitir. Este requisito MUST NOT cambiar ningun valor numerico.

#### Scenario: Cada aparicion calificada

- **WHEN** se listan con `grep` las apariciones de `0,7405`, `97/131`, `97 de 131`, `0,6769` y `88/130` en `sections/*.tex`
- **THEN** cada una esta en una oracion o parrafo que la califica como estimacion dentro de la muestra o que remite a `subsec:sensibilidad-ajustes`

#### Scenario: Cuantificacion en un unico lugar

- **WHEN** se buscan los valores del analisis de sensibilidad fuera de `subsec:sensibilidad-ajustes`
- **THEN** solo aparecen en la limitacion del capitulo de discusion, que remite a la subseccion
- **AND** ningun otro pasaje repite la tabla ni su lectura

#### Scenario: Valores sin cambio

- **WHEN** se comparan los valores numericos de la tesis antes y despues de agregar las calificaciones
- **THEN** no cambia ninguno

<!-- c-144 (archivado el 2026-10-23 en main) ya incorporo al spec vivo el requisito "Ubicacion veraz de las versiones historicas del prompt en el Anexo H"; este change solo verifica el texto resultante. -->

### Requirement: Impacto de paginas del analisis de sensibilidad

El change SHALL registrar el conteo de paginas del PDF compilado tras aplicarlo y su diferencia con el conteo de partida, para la decision de tope de la release. El analisis SHALL presentarse con una unica tabla compacta. Si el conteo supera el tope vigente registrado por el gate G0, SHALL aplicar las compensaciones declaradas en su diseno en el orden previsto y registrar el exceso remanente y su causa; MUST NOT eliminar contenido cientifico, numeros canonicos ni la linea de fuente de la tabla para compensar paginas, aunque SHALL poder trasladar la tabla a un anexo si la regla de G0 limita solo el cuerpo.

#### Scenario: Conteo registrado

- **WHEN** se compila `main.tex` tras aplicar el change
- **THEN** el conteo de paginas y su diferencia con el de partida quedan registrados en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Compensacion sin perdida de contenido

- **WHEN** el conteo supera el tope vigente
- **THEN** se aplican las compensaciones declaradas en el diseno y el exceso remanente se registra para el change de integracion
- **AND** no se elimina ningun valor de la subseccion ni la linea de fuente de la tabla

### Requirement: Balance neto entre el ahorro de registro y el costo de las derivaciones erroneas

El capitulo de discusion (`08-discusion.tex`) SHALL incluir una subseccion con rotulo `subsec:balance-neto` que compute el balance neto trimestral entre el ahorro de tiempo de registro y el costo de las derivaciones erroneas adicionales del clasificador respecto del flujo manual. La subseccion SHALL enunciar de forma explicita las formulas del balance neto, `B = (N / 3.600) x [Delta t - (e_aut - e_man) x c]`, y de la exactitud minima de equilibrio, `a* = 1 - e_man - Delta t / c`, junto con la procedencia de cada insumo: universo trimestral `N ~ 2.646`, ahorro medio por incidente `Delta t = 43,82 s` (43,8 s en el texto), tasa de error estricta del clasificador `e_aut = 26,5 %` (53/200), tasa de derivacion erronea manual `e_man` (15 % preliminar) y costo por derivacion erronea `c` (10 a 15 minutos, estimacion propia). La subseccion SHALL incluir una tabla con rotulo `tab:balance-neto` que, para tasas manuales de 10 %, 15 %, 20 % y 26,5 % y costos de 5, 10 y 15 minutos, reporte la exactitud minima de equilibrio y el balance neto con la exactitud estricta, y SHALL contrastar la exactitud minima de equilibrio con la exactitud estricta observada y su intervalo de Wilson. Todo valor de la subseccion y de la tabla MUST coincidir con el registrado en `docs/Tesis/Correcciones/numeros-canonicos.md`.

#### Scenario: Formulas e insumos explicitos

- **WHEN** se lee la subseccion `subsec:balance-neto`
- **THEN** figuran las formulas del balance neto y de la exactitud minima de equilibrio con la definicion de `N`, `Delta t`, `e_aut`, `e_man` y `c`
- **AND** cada insumo remite a su origen en el documento (planteamiento del problema, objetivos especificos, interpretacion de los resultados o resultados)

#### Scenario: Calculo con los supuestos del propio documento

- **WHEN** se aplican las formulas con `e_man = 15 %` y `c` de 10 y 15 minutos
- **THEN** el texto informa del orden de 304 derivaciones erroneas adicionales por trimestre, un costo de 50,7 y 76,1 horas-persona y un balance neto de -18,5 y -43,9 horas-persona
- **AND** la exactitud minima de equilibrio informada para esos supuestos es 77,7 % y 80,1 %

#### Scenario: Tabla de escenarios con el punto de equilibrio

- **WHEN** se lee la tabla `tab:balance-neto`
- **THEN** contiene una fila por tasa manual (10 %, 15 %, 20 % y 26,5 %) y, para costos de 5, 10 y 15 minutos, la exactitud minima de equilibrio y el balance neto con la exactitud estricta
- **AND** cada celda coincide con el valor del memo canonico bajo la convencion de redondeo declarada en la nota de la tabla

#### Scenario: Incertidumbre muestral considerada

- **WHEN** se contrasta la exactitud minima de equilibrio con la exactitud estricta observada
- **THEN** el texto compara la exactitud minima de equilibrio con el intervalo de Wilson [67,0 %; 79,1 %]
- **AND** declara que, con una tasa manual del 15 % y 10 minutos por reasignacion, el signo del balance no queda determinado por la muestra

#### Scenario: Exactitud laxa sin cifras inventadas

- **WHEN** la exactitud laxa esta registrada en el memo canonico al momento de aplicar el cambio
- **THEN** la subseccion la compara con la exactitud minima de equilibrio e informa los escenarios en que el balance resulta positivo bajo esa lectura
- **AND** si no esta registrada, la subseccion no presenta ningun valor de exactitud laxa y declara que el 26,5 % es una cota superior de la tasa operativa de derivacion erronea atribuible al clasificador

#### Scenario: Remisiones resueltas

- **WHEN** se compila el documento con XeLaTeX tras incorporar la subseccion y la tabla
- **THEN** las remisiones a `subsec:balance-neto` y `tab:balance-neto` resuelven sin referencias indefinidas
- **AND** ambos rotulos son unicos en el documento

### Requirement: Exactitud del brazo manual declarada no medida y balance neto indeterminado

La tesis SHALL declarar que la exactitud del brazo manual sobre el corpus no se midio, con sus dos razones: el corpus no registra por caso la derivacion efectuada por el operador del brazo manual, y esos operadores son los mismos analistas que fijaron la referencia, por lo que una medicion sobre este corpus estaria sesgada hacia el acuerdo. La tesis SHALL declarar que la tasa de derivacion erronea manual cercana al 15 % es una estimacion preliminar de la misma naturaleza que los 2 minutos 45 segundos luego corregidos a 61,6 s, y que, en consecuencia, el balance neto es indeterminado con el diseno actual. El documento MUST NOT presentar ninguna exactitud o tasa de derivacion erronea del flujo manual como medida, y MUST NOT enunciar el signo del balance neto como resultado.

#### Scenario: Declaracion en la discusion

- **WHEN** se leen la subseccion `subsec:balance-neto` y la sexta limitacion de `subsec:limitaciones-estudio`
- **THEN** se declara que la exactitud del brazo manual no se midio y se enuncian las dos razones
- **AND** se concluye que el balance neto es indeterminado con el diseno actual, indicando la condicion bajo la cual seria positivo

#### Scenario: Declaracion en el planteamiento del problema

- **WHEN** se lee el planteamiento del problema en `01-introduccion.tex`
- **THEN** la tasa de derivacion erronea del 15 % se califica como estimacion preliminar no re-medida, de la misma naturaleza que los 2 minutos 45 segundos
- **AND** el parrafo remite a `subsec:balance-neto`

#### Scenario: Sin tasa manual presentada como medida

- **WHEN** se recorren las secciones de la tesis en busca de una exactitud o tasa de derivacion erronea del flujo manual
- **THEN** el unico valor atribuido al flujo manual es el 15 % preliminar, rotulado como tal, y las demas tasas de la tabla de escenarios se rotulan como supuestos de sensibilidad
- **AND** ningun pasaje presenta una tasa manual como resultado de la campana experimental ni afirma que el balance neto sea positivo o negativo

### Requirement: Viabilidad operativa presentada como condicional

El resumen (en espanol y en ingles), la justificacion de la introduccion, la discusion y las conclusiones SHALL presentar la viabilidad tecnica y la economica como sostenidas por la evidencia y la viabilidad operativa como condicional a que la exactitud efectiva supere la exactitud minima de equilibrio, sea por mejora del clasificador o porque la revision humana del sector responsable reduzca la tasa o el costo efectivos de las derivaciones erroneas. El documento MUST NOT afirmar que los hallazgos confirman la viabilidad "tecnica, economica y operativa" (ni la "technical, economic, and operational feasibility"). El ahorro de 32,2 horas-persona por trimestre SHALL presentarse como ahorro bruto de registro, sin cambiar su valor. El parrafo de conclusion del resumen en espanol y del abstract MUST NOT aumentar su conteo de palabras respecto de la version previa.

#### Scenario: Resumen y abstract con viabilidad operativa condicional

- **WHEN** se leen los parrafos de conclusion del resumen y del abstract en `00-resumen.tex`
- **THEN** la viabilidad tecnica y economica se presentan como confirmadas y la operativa como condicional, con el balance neto frente a las derivaciones erroneas declarado indeterminado
- **AND** el parrafo en espanol tiene a lo sumo 34 palabras y el parrafo en ingles a lo sumo 31

#### Scenario: Conclusiones con los tres planos de viabilidad

- **WHEN** se lee el parrafo inicial de `09-conclusiones.tex`
- **THEN** el sistema se declara tecnicamente viable y economicamente accesible, y su viabilidad operativa se declara condicionada al balance neto con remision a `subsec:balance-neto`
- **AND** no queda una afirmacion de viabilidad incondicional del sistema en su conjunto

#### Scenario: Justificacion sin mejora neta cuantificada

- **WHEN** se lee la dimension organizacional de la justificacion en `01-introduccion.tex`
- **THEN** la evidencia del trabajo se presenta como cuantificacion del ahorro bruto de registro y del punto de equilibrio frente al costo de las derivaciones erroneas
- **AND** no se afirma como cuantificada una mejora neta ni una reduccion del tiempo de respuesta percibido por los usuarios

#### Scenario: Ahorro de 32,2 horas-persona calificado como bruto

- **WHEN** se lee cualquier mencion de las 32,2 horas-persona por trimestre en la introduccion, la discusion o las conclusiones
- **THEN** la mencion la califica como ahorro bruto o remite al balance neto de `subsec:balance-neto`
- **AND** el valor 32,2 y su calculo (`43,8 s x 2.646 / 3.600`) se conservan sin cambios

#### Scenario: Composicion del costo economico coherente con la discusion

- **WHEN** se lee en las conclusiones la descripcion del costo monetario de operacion del sistema
- **THEN** la descripcion es coherente con las cifras de la discusion (infraestructura de 24 a 32 USD por mes frente a inferencia del orden de 1 USD por trimestre)
- **AND** no se afirma que el costo de operacion este dominado por el consumo de la API de inferencia

### Requirement: Retiro de la afirmacion de preservacion del juicio humano

La discusion MUST NOT contener la afirmacion "El sistema absorbe la carga rutinaria sin sustituir el juicio humano en los casos que verdaderamente lo demandan" ni la afirmacion de que el equilibrio entre automatizacion y supervision "preserva la calidad del servicio", porque el gate de revision no derivo ningun caso del corpus y su aporte se declara no medido. El documento MUST NOT atribuir al sistema una preservacion del juicio humano que no fue medida. El parrafo de `subsec:interpretacion-resultados` SHALL conservar la proyeccion de 32,2 horas-persona con su nota de calculo.

#### Scenario: Frases retiradas

- **WHEN** se buscan en las secciones de la tesis las cadenas "absorbe la carga rutinaria" y "preserva la calidad del servicio"
- **THEN** no aparece ninguna ocurrencia
- **AND** el parrafo de `subsec:interpretacion-resultados` conserva la proyeccion de 32,2 horas-persona y su nota al pie

#### Scenario: Sin afirmaciones equivalentes

- **WHEN** se leen la discusion y las conclusiones
- **THEN** ningun pasaje afirma que el sistema preserva el juicio humano en los casos que lo demandan
- **AND** las menciones al gate de revision son coherentes con la declaracion de que su aporte no fue medido

### Requirement: Registro canonico del balance neto y sus supuestos

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar, en una seccion propia, los insumos, las formulas y los valores de la tabla del balance neto, cada uno con su procedencia (archivo y linea de origen, o recalculo con formula explicita) y su estado. Los valores que dependen de la tasa manual, del costo por derivacion erronea o de la rejilla de sensibilidad SHALL registrarse con estado `condicional` y con su condicion de reversibilidad. La seccion SHALL incluir un comando de recalculo reproducible y declarar la convencion de redondeo. El registro MUST NOT modificar ningun valor canonico existente.

#### Scenario: Insumos con procedencia y estado

- **WHEN** se lee la seccion del balance neto en el memo canonico
- **THEN** cada insumo declara valor, procedencia y estado: `vigente` para el universo, el ahorro medio por incidente y la tasa de error estricta; `condicional` para la tasa manual, el costo por derivacion erronea y la rejilla de sensibilidad
- **AND** cada linea de origen citada existe en el archivo referenciado

#### Scenario: Valores reproducibles

- **WHEN** se ejecuta el comando de recalculo de la seccion
- **THEN** reproduce la exactitud minima de equilibrio y el balance neto de cada celda de la tabla, y los valores del escenario central
- **AND** la convencion de redondeo y la diferencia respecto del calculo con 43,8 s quedan declaradas

#### Scenario: Valores canonicos existentes intactos

- **WHEN** se comparan las secciones previas del memo antes y despues del cambio
- **THEN** ningun valor existente cambio de valor ni de estado
- **AND** la cabecera del memo registra el agregado de la seccion nueva

### Requirement: Linea futura de medicion de la exactitud manual y del costo de reasignacion

El capitulo de recomendaciones SHALL incluir, en `subsec:estudios-replicacion`, la recomendacion de que toda replicacion registre por caso la derivacion efectuada en el brazo manual, con etiquetadores distintos de los operadores, y cronometre cada reasignacion, de modo de medir la exactitud manual y el costo de la derivacion erronea y cerrar el balance neto. La subseccion `subsec:balance-neto` SHALL remitir a esa recomendacion, y el capitulo MUST NOT duplicarla en otra subseccion.

#### Scenario: Recomendacion presente y conectada

- **WHEN** se lee `subsec:estudios-replicacion`
- **THEN** recomienda registrar por caso la derivacion del brazo manual con etiquetadores distintos de los operadores y cronometrar las reasignaciones
- **AND** remite a `subsec:balance-neto`, que a su vez remite a esta subseccion

#### Scenario: Sin duplicacion en recomendaciones

- **WHEN** se recorre el capitulo de recomendaciones
- **THEN** la medicion de la exactitud del flujo manual se recomienda una sola vez
- **AND** no existe una subseccion adicional que repita esa recomendacion

### Requirement: Grados de cumplimiento de los objetivos acotados a la evidencia

La tabla `tab:cumplimiento-objetivos` de `09-conclusiones.tex` SHALL asignar a cada objetivo el grado "Alcanzado" solo cuando cada componente exigido por su enunciado literal en `01-introduccion.tex` este evidenciado en la version evaluada; "Alcanzado parcialmente" cuando al menos un componente este evidenciado y al menos otro no se cumpla o no se haya medido; y "No alcanzado" cuando no se cumpla el criterio del objetivo. Toda fila "Alcanzado parcialmente" SHALL nombrar en su evidencia el componente no cumplido o no medido. Los objetivos especificos 1, 3 y 4 SHALL figurar como "Alcanzado parcialmente" mientras falte la evidencia de, respectivamente, la comunicacion asincronica y el cifrado verificado en la instancia publicada; la calidad de clasificacion por canal; y la exactitud del brazo manual y la proporcion de intervencion humana. El objetivo general SHALL desglosarse en sus tres componentes (tiempo de registro, calidad de la clasificacion y proporcion de intervencion humana) con estado individual, y su grado global SHALL ser coherente con ese desglose. El documento MUST NOT reformular el enunciado de un objetivo para ajustarlo a lo construido o medido, y la prosa de las conclusiones SHALL ser coherente con la tabla.

#### Scenario: Objetivos 1, 3 y 4 parcialmente alcanzados

- **WHEN** se leen las filas de los objetivos especificos 1, 3 y 4 en `tab:cumplimiento-objetivos`
- **THEN** cada una declara "Alcanzado parcialmente"
- **AND** su evidencia nombra el componente faltante: invocacion sincronica y TLS no verificado (1); calidad por canal no medida (3); exactitud del brazo manual e intervencion humana no medidas (4)

#### Scenario: Objetivo general desglosado

- **WHEN** se lee la fila del objetivo general
- **THEN** figuran el tiempo de registro como alcanzado, la calidad de la clasificacion como evaluada por debajo del umbral y la intervencion humana como no medida
- **AND** el grado global es "Alcanzado parcialmente"

#### Scenario: Enunciados de objetivos sin reformular

- **WHEN** se comparan los enunciados del objetivo general y de los objetivos especificos en `01-introduccion.tex` con los de la version previa al change
- **THEN** los enunciados no cambian
- **AND** solo cambia su grado de cumplimiento en la tabla

#### Scenario: Reversion condicionada a evidencia

- **WHEN** se dispone de evidencia nueva para un componente faltante del objetivo 1 o del objetivo 3 (por ejemplo, la que aporte c-140 para el objetivo 1) y se propone elevar su grado
- **THEN** el grado solo pasa a "Alcanzado" si la tabla cita evidencia para cada componente faltante (TLS verificado y comunicacion asincronica para el 1; calidad por canal sin evidencia de degradacion y decision del autor sobre la complejidad percibida para el 3)
- **AND** si la evidencia es posterior a la validacion experimental, la celda lo declara

#### Scenario: Objetivo 6 con evidencia ampliada

- **WHEN** se lee la fila del objetivo especifico 6
- **THEN** su grado sigue la regla de esta tabla y su evidencia cita el analisis de errores, la calibracion por etapa y el analisis de sensibilidad de los ajustes (`subsec:sensibilidad-ajustes`)
- **AND** si alguna de esas piezas no esta disponible, el grado no es "Alcanzado" sin declarar el componente faltante

#### Scenario: Prosa coherente con la tabla

- **WHEN** se leen los parrafos de las conclusiones que tratan el objetivo general y los objetivos 1, 3 y 4
- **THEN** ninguno afirma un cumplimiento pleno que la tabla declare parcial
- **AND** el primer parrafo declara cumplido parcialmente el objetivo general

### Requirement: Segunda sub-hipotesis con fraccion esperada explicita

La segunda sub-hipotesis (`01-introduccion.tex`, `subsec:hipotesis-trabajo`) SHALL enunciarse con una fraccion esperada numerica explicita, derivada de un criterio fijado a priori en el propio documento (en esta version, una proporcion de casos con accion manual de un operador no superior a `0,15`, complemento del umbral de exactitud del 85 %), junto con su contraste (proporcion con intervalo de confianza de Wilson) y su criterio de falsacion. El texto SHALL declarar que la formulacion original, referida al proceso manual y sin fraccion esperada especificada, no era contrastable, y que la cota se explicita en esta version. Mientras no exista registro primario de intervencion por caso, la sub-hipotesis SHALL declararse "no contrastada por ausencia de registro primario" en el resumen, la introduccion, los resultados y las conclusiones. El documento MUST NOT presentar las derivaciones del gate de revision (ninguna en el corpus) como contraste o confirmacion de esta sub-hipotesis y MUST NOT cuantificar la proporcion. Toda remision desde la sub-hipotesis SHALL apuntar a una seccion que declare la ausencia de registro primario; si remite a la lista de limitaciones del estudio (`subsec:limitaciones-estudio`), esa lista SHALL incluir la proporcion de intervencion humana no medida y su oracion introductoria SHALL declarar el numero real de limitaciones listadas.

#### Scenario: Fraccion esperada y criterio de falsacion explicitos

- **WHEN** se lee la segunda sub-hipotesis en `01-introduccion.tex`
- **THEN** declara la cota numerica, su derivacion del umbral fijado a priori, el contraste con intervalo de Wilson y el criterio de falsacion
- **AND** la cota figura en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Formulacion original declarada no contrastable

- **WHEN** se lee la segunda sub-hipotesis
- **THEN** el texto declara que la comparacion con el proceso manual, donde la intervencion es total por definicion, no era contrastable sin fraccion esperada
- **AND** declara que la cota se explicita en esta version

#### Scenario: Sin confirmacion espuria por el gate

- **WHEN** se leen la introduccion y la subseccion `subsec:reduccion-intervencion` de resultados
- **THEN** la ausencia de derivaciones del gate no se presenta como contraste ni como confirmacion de la sub-hipotesis
- **AND** el texto explica que esas derivaciones no operacionalizan la proporcion de casos con accion manual

#### Scenario: Estado propagado

- **WHEN** se busca el rotulo de la segunda sub-hipotesis en `00-resumen.tex`, `01-introduccion.tex`, `07-resultados.tex` y `09-conclusiones.tex`
- **THEN** en los cuatro aparece "no contrastada por ausencia de registro primario"
- **AND** ninguno informa una proporcion de intervencion humana como resultado

#### Scenario: Remision coherente con su destino

- **WHEN** se sigue la remision `\autoref` de la segunda sub-hipotesis en `01-introduccion.tex`
- **THEN** la seccion de destino declara que la proporcion de intervencion humana no se midio por ausencia de registro primario
- **AND** si el destino es `subsec:limitaciones-estudio`, la lista incluye esa limitacion y el conteo de su oracion introductoria coincide con el numero de limitaciones listadas

### Requirement: Estado declarado de las hipotesis subsidiarias

Las dos hipotesis subsidiarias de `01-introduccion.tex` SHALL tener un estado declarado y coherente en la introduccion, la discusion y las conclusiones. La de integracion multicanal sin cuellos de botella SHALL declararse "no contrastada" mientras no se mida la capacidad bajo carga concurrente. La de mayor eficiencia del esquema hibrido frente a un esquema solo de modelo SHALL declararse "contrastada de forma acotada" solo si el texto informa el contraste acotado con sus salvedades y el analisis de sensibilidad de los ajustes del clasificador no lo contradice; en caso contrario SHALL declararse "no contrastada". La discusion MUST NOT afirmar consistencia con la hipotesis de eficiencia apoyandose solo en la proporcion de casos resueltos sin invocar al modelo.

#### Scenario: Estados declarados en los tres capitulos

- **WHEN** se leen la introduccion, la discusion y las conclusiones
- **THEN** cada hipotesis subsidiaria tiene un estado explicito
- **AND** el estado es el mismo en los tres capitulos

#### Scenario: Frase de consistencia sin sustento retirada

- **WHEN** se busca en `08-discusion.tex` la afirmacion de consistencia con la hipotesis subsidiaria de eficiencia
- **THEN** no aparece apoyada solo en el 65,5 % de casos resueltos sin el modelo
- **AND** en su lugar figura el contraste acotado con sus salvedades, o el rotulo "no contrastada"

#### Scenario: Subsidiaria multicanal no contrastada

- **WHEN** se leen las conclusiones sobre la integracion de los tres canales
- **THEN** el texto no afirma que la integracion "confirmo" la ausencia de dispersion operativa o de cuellos de botella
- **AND** declara que la hipotesis subsidiaria de integracion multicanal no se contrasto

### Requirement: Contraste acotado de la hipotesis subsidiaria de eficiencia con salvedades declaradas

Cuando el documento sostenga la hipotesis subsidiaria de eficiencia del esquema hibrido, SHALL hacerlo con cifras ya documentadas en el repositorio (sobre los 131 casos que resuelve la etapa de reglas: exactitud de la etapa de reglas `0,7405`, 97/131, frente a Gemini ejecutado sobre 130 de esos casos con el cortocircuito deshabilitado, `0,6769`, 88/130, segun `docs/deterministic_calibration.md`) y SHALL declarar en el mismo pasaje: que las cifras son estimaciones dentro de la muestra, con remision al analisis de sensibilidad de los ajustes del clasificador (`subsec:sensibilidad-ajustes`); si se aplico o no una prueba pareada; que la comparacion se hace sobre el mismo corpus con que se ajustaron el vocabulario, las reglas del prompt y el punto de operacion del filtro; y que la latencia no se midio por etapa, salvo que otro change la reporte. Si la variante de ese analisis con el vocabulario previo al ajuste muestra que la etapa de reglas no supera a Gemini en exactitud sobre los casos que resuelve, la hipotesis SHALL rotularse "no contrastada". La prueba pareada (McNemar exacta) SHALL citarse solo si figura registrada en el memo canonico, computada fuera de linea sobre los pares por caso de la cache de calibracion por el change dueno de esa cache. El change MUST NOT ejecutar llamadas pagas al proveedor ni presentar el contraste acotado como confirmacion de la hipotesis.

#### Scenario: Cifras del contraste con procedencia

- **WHEN** se leen las cifras del contraste en `08-discusion.tex`
- **THEN** coinciden con `docs/deterministic_calibration.md` (97/131 = 0,7405 y 88/130 = 0,6769)
- **AND** figuran en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Salvedades presentes

- **WHEN** se lee el pasaje del contraste
- **THEN** declara la ausencia (o el resultado) de la prueba pareada, el origen in-corpus de los ajustes del clasificador y la latencia no medida por etapa
- **AND** el estado de la hipotesis se rotula "contrastada de forma acotada", no "confirmada"

#### Scenario: Estimacion dentro de la muestra

- **WHEN** se leen las cifras 0,7405 y 0,6769 en `08-discusion.tex`
- **THEN** el texto las califica como estimaciones dentro de la muestra
- **AND** remite a `subsec:sensibilidad-ajustes`

#### Scenario: Regla de decision con el vocabulario previo

- **WHEN** la variante del analisis de sensibilidad con el vocabulario previo al ajuste muestra que la etapa de reglas no supera a Gemini en exactitud sobre los casos que resuelve
- **THEN** la hipotesis subsidiaria de eficiencia se rotula "no contrastada" en la introduccion, la discusion y las conclusiones
- **AND** la discusion no presenta el contraste acotado como evidencia favorable

#### Scenario: Prueba pareada condicionada al memo

- **WHEN** el memo canonico no registra la prueba pareada (por ejemplo, porque la cache `evaluation/predicciones_calibracion.json` no se recupero)
- **THEN** el texto declara que la diferencia no se sometio a una prueba pareada
- **AND** no se cita ningun valor p para este contraste

#### Scenario: Sin llamadas pagas

- **WHEN** se revisa el registro de ejecucion del change
- **THEN** no hubo invocaciones a Gemini ni re-ejecucion del clasificador
- **AND** toda cifra nueva proviene de documentos o caches ya versionados o recuperados

### Requirement: Metrica primaria unica del F1 macro

El documento SHALL usar el macro-F1 de umbral sobre las cuatro clases estimables (`0,6508`) como metrica primaria y unico referente del umbral `0,85` en el resumen, el abstract, la tercera sub-hipotesis, la tabla de cumplimiento de objetivos, la metodologia, los resultados y la discusion. Toda aparicion del macro-F1 de cinco clases (`0,5207`) SHALL acompanarse de su aclaracion (incluye Bases de Datos, con un unico caso y no estimable). La metodologia SHALL definir el macro-F1 de umbral excluyendo las clases con soporte unitario. Los resultados SHALL declarar por que se excluye la clase no estimable y que la eleccion no altera el veredicto, porque ambos valores quedan por debajo de `0,85`. El memo canonico SHALL registrar `0,6508` como `vigente`.

#### Scenario: Primario en resumen y abstract

- **WHEN** se lee `00-resumen.tex`
- **THEN** el resumen y el abstract citan 0,6508 (0.6508) rotulado como macro-F1 de umbral sobre las cuatro clases estimables
- **AND** no citan 0,5207 sin su aclaracion

#### Scenario: Primario en la hipotesis y en la tabla de objetivos

- **WHEN** se leen la tercera sub-hipotesis y la fila del objetivo especifico 2 de `tab:cumplimiento-objetivos`
- **THEN** ambas citan 0,6508 como macro-F1 de umbral
- **AND** si la fila cita 0,5207, lo acompana su aclaracion

#### Scenario: Cada aparicion rotulada

- **WHEN** se ejecuta `grep -n "0[,.]5207"` y `grep -n "0[,.]6508"` sobre `paper/sections/*.tex`
- **THEN** cada linea con 0,5207 contiene su aclaracion (cinco clases, no estimable o equivalente)
- **AND** cada linea con 0,6508 lo rotula como de umbral o sobre cuatro clases estimables

#### Scenario: Definicion metodologica coherente

- **WHEN** se leen la fila del F1 macro en `tab:variables` y el analisis estadistico de `04-marco-metodologico.tex`
- **THEN** el F1 macro de umbral excluye las clases con soporte unitario
- **AND** no se define el F1 macro de umbral sobre los cinco sectores

#### Scenario: Robustez de la eleccion declarada

- **WHEN** se lee la oracion del macro-F1 en `07-resultados.tex`
- **THEN** declara que el umbral 0,85 se evalua contra el macro-F1 de umbral y por que se excluye la clase no estimable
- **AND** declara que ambos valores quedan por debajo del criterio

#### Scenario: Memo coherente

- **WHEN** se lee `docs/Tesis/Correcciones/numeros-canonicos.md`
- **THEN** el macro-F1 de cuatro clases figura como `vigente` y primario de umbral
- **AND** el macro-F1 de cinco clases figura como informativo

### Requirement: Procedencia canonica de las cifras de hipotesis, objetivos y metrica primaria

Toda cifra que las correcciones de hipotesis, objetivos y metrica primaria introduzcan en las fuentes LaTeX SHALL figurar en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia (archivo y linea) y su estado antes de citarse en el texto. Ninguna cifra MUST fabricarse ni derivarse de una fuente no versionada. Las correcciones MUST NOT reintroducir valores `retirado`, en particular la intervencion humana del `9,5 %`.

#### Scenario: Cifras nuevas registradas

- **WHEN** se listan las cifras nuevas que cita el texto (por ejemplo 0,15; 97/131; 0,7405; 88/130; 0,6769; 65,5 %)
- **THEN** cada una figura en el memo canonico con procedencia y estado
- **AND** el valor del texto coincide con el del memo

#### Scenario: Sin valores retirados

- **WHEN** se busca "9,5" como proporcion de intervencion humana en las fuentes tras las correcciones
- **THEN** no aparece como resultado
- **AND** el memo conserva su estado `retirado`

### Requirement: Neutralidad de paginas y palabras de las correcciones de hipotesis, objetivos y metrica primaria

Las correcciones de hipotesis, objetivos y metrica primaria MUST NOT aumentar el total de paginas del PDF compilado respecto del estado compilado inmediatamente anterior a su aplicacion, ni desplazar las paginas de inicio de los capitulos, salvo que, agotadas las compensaciones dentro de los parrafos propios, el exceso quede documentado en `docs/Tesis/Correcciones/dictamen-correcciones.md` para su resolucion en el gate de paginas de la integracion final, que fija el tope global. El exceso MUST NOT compensarse recortando parrafos asignados a otros changes. El resumen y el abstract MUST NOT aumentar su numero de palabras de prosa (regla de conteo de c-106) y SHALL quedar en 250 palabras o menos.

#### Scenario: Paginas sin aumento

- **WHEN** se compila el PDF antes y despues de aplicar las correcciones
- **THEN** el total de paginas despues es menor o igual que antes
- **AND** las paginas de inicio de la introduccion, la discusion, las conclusiones y las recomendaciones no cambian, o el exceso queda documentado

#### Scenario: Palabras del resumen sin aumento

- **WHEN** se cuentan las palabras de prosa del resumen y del abstract antes y despues de las correcciones
- **THEN** el conteo posterior no supera al anterior
- **AND** ambos quedan en 250 palabras o menos

### Requirement: Extension del protocolo de revision para calibracion y cascadas

El parrafo de protocolo de revision de `03-estado-del-arte.tex` SHALL declarar, ademas de las cadenas A1-A4 y B1, una extension con dos cadenas de busqueda: C1 (calibracion y estimacion de la confianza en clasificadores y modelos de lenguaje) y C2 (cascadas, enrutamiento y esquemas hibridos con criterio de costo-exactitud), ejecutadas sobre las mismas seis bases, con criterios de inclusion y exclusion propios del grupo C, una regla de seleccion declarada y una fecha de corte propia posterior al 21 de octubre de 2026. La bitacora `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md` SHALL registrar cada consulta de la extension (base, cadena, fecha y resultado) y MUST coincidir con el texto en bases, cadenas, criterios y fecha de corte. Las cadenas A1-A4 y B1, sus criterios y su fecha de corte MUST permanecer sin cambios.

#### Scenario: Cadenas C1 y C2 declaradas en el capitulo

- **WHEN** se lee el parrafo de protocolo de revision en `03-estado-del-arte.tex`
- **THEN** enuncia las cadenas C1 y C2 completas, las seis bases, los criterios de inclusion y exclusion del grupo C y la fecha de corte de la extension
- **AND** la formulacion permite a un lector reproducir la busqueda

#### Scenario: Bitacora consistente con la extension

- **WHEN** se compara la seccion del grupo C de la bitacora con el parrafo de protocolo
- **THEN** cada consulta registra base, cadena, fecha y resultado (claves incorporadas o ausencia de incorporaciones)
- **AND** las cadenas, bases, criterios y fecha de corte coinciden con los del capitulo, y la bitacora no registra consultas que el texto no mencione

#### Scenario: Protocolo original preservado

- **WHEN** se compara el parrafo de protocolo despues del change con la version previa
- **THEN** las cadenas A1-A4 y B1, sus criterios y la fecha de corte del 21 de octubre de 2026 permanecen identicos
- **AND** la afirmacion de vacancia sobre Google Gemini y tickets de soporte en espanol conserva su alcance original

### Requirement: Verificacion individual de las fuentes de calibracion y cascadas

Toda fuente incorporada por la extension C1-C2 SHALL verificarse antes de citarse en tres compuertas: existencia (el DOI resuelve hacia la editorial o, para sedes sin DOI, la pagina oficial de la sede responde), metadatos (titulo, autores, sede, ano y paginas coinciden con Crossref o con los metadatos oficiales de la sede) y contenido (lectura del texto completo y registro de cada afirmacion atribuida con su seccion o pagina). Las fuentes SHALL ser arbitradas y los preprints sin version arbitrada MUST excluirse. Una fuente que no supere alguna compuerta MUST NOT citarse, y ninguna oracion agregada MUST atribuir a una fuente mas de lo que esta sostiene.

#### Scenario: Existencia y metadatos registrados

- **WHEN** se inspecciona la tabla de verificacion del grupo C en la bitacora
- **THEN** cada fuente incorporada registra su DOI o URL oficial, el resultado de la resolucion y el cotejo de metadatos
- **AND** ninguna fuente incorporada carece de alguno de esos registros

#### Scenario: Correspondencia afirmacion-fuente

- **WHEN** se toma cualquier oracion agregada por el change que cite una fuente nueva
- **THEN** la bitacora registra esa afirmacion con la seccion o pagina de la fuente que la sostiene
- **AND** la oracion no atribuye a la fuente resultados que esta no reporta, como resultados sobre Gemini, sobre tickets de soporte o sobre una primera etapa de reglas

#### Scenario: Fuente no verificada o no arbitrada excluida

- **WHEN** una fuente candidata no resuelve, no coincide en metadatos, no trata lo que se le atribuiria o carece de version arbitrada
- **THEN** no aparece citada en ningun `.tex` ni como entrada de `Bibliography_base.bib`
- **AND** la bitacora la registra como excluida con su motivo

### Requirement: Fundamentacion de la calibracion de la confianza con fuentes que la tratan

La seccion del marco teorico sobre procesamiento de lenguaje natural y modelos de lenguaje grandes (`subsec:nlp-llm`) SHALL fundamentar el concepto de calibracion de la confianza con al menos dos fuentes verificadas que efectivamente lo traten, cubriendo su medicion, su correccion posterior y la confianza verbalizada por modelos de lenguaje consultados como servicio. Las oraciones agregadas MUST NOT citar `xuan2025mmluprox` como fuente de calibracion. La seccion SHALL vincular el esquema hibrido del sistema con la nocion de cascada de modelos mediante al menos una fuente verificada.

#### Scenario: Calibracion sostenida por fuentes que la tratan

- **WHEN** se leen en el PDF compilado las oraciones de `subsec:nlp-llm` sobre calibracion
- **THEN** el concepto, su medicion y la confianza verbalizada se apoyan en al menos dos fuentes verificadas de la extension C1-C2
- **AND** ninguna de esas oraciones cita a Xuan et al. (2025)

#### Scenario: Esquema hibrido vinculado con la literatura de cascadas

- **WHEN** se lee la oracion de `subsec:nlp-llm` que presenta el esquema hibrido entre clasificador supervisado y modelo de lenguaje grande
- **THEN** describe la combinacion como una cascada en la que el componente mas economico resuelve los casos para los que su senal de fiabilidad alcanza un umbral y deriva los restantes al mas costoso
- **AND** cita al menos una fuente verificada sobre cascadas de modelos

### Requirement: Estado del arte sobre calibracion de la confianza y cascadas de modelos

El capitulo de estado del arte SHALL contener una subseccion con rotulo `subsec:calibracion-cascadas` que revise la literatura sobre (a) calibracion de la confianza en clasificadores y en modelos de lenguaje grandes, incluidas la confianza verbalizada y el sesgo de etiquetas en la clasificacion por instrucciones, y (b) cascadas de modelos con criterio de costo-exactitud, citando las fuentes verificadas de la extension C1-C2. La oracion introductoria del capitulo SHALL enumerar esta area. Toda afirmacion de vacancia de la subseccion SHALL formularse relativa a las cadenas C1-C2, a las bases consultadas y a la fecha de corte de la extension, y MUST omitirse si la busqueda no la confirma.

#### Scenario: Ambos ejes cubiertos

- **WHEN** se lee la subseccion de calibracion y cascadas en el PDF compilado
- **THEN** al menos una fuente verificada sostiene cada eje (calibracion de la confianza; cascadas de modelos)
- **AND** cada fuente se describe por lo que efectivamente estudia y encuentra

#### Scenario: Vacancia acotada o ausente

- **WHEN** la subseccion enuncia que no se identifico un trabajo con determinadas caracteristicas
- **THEN** la afirmacion declara las cadenas C1-C2 y la fecha de corte de la extension y no se presenta como inexistencia absoluta
- **AND** la bitacora no registra ningun trabajo incorporado o examinado que la refute

#### Scenario: Introduccion del capitulo coherente

- **WHEN** se lee la oracion introductoria de `03-estado-del-arte.tex`
- **THEN** el numero de areas enunciadas coincide con las areas que el capitulo revisa
- **AND** la calibracion de la confianza y las cascadas de modelos figuran entre ellas

### Requirement: Lectura del hallazgo de calibracion y del esquema hibrido a la luz de la literatura

La subseccion de comparacion con la literatura de la discusion (`subsec:comparacion-literatura`) SHALL contrastar con las fuentes verificadas de calibracion y cascadas el hallazgo sobre la confianza autodeclarada, tal como lo formula por etapa del pipeline el capitulo de resultados, y el esquema hibrido de reglas y modelo. El parrafo MUST NOT introducir valores numericos ausentes de `docs/Tesis/Correcciones/numeros-canonicos.md`, salvo cifras de terceros citadas textualmente con su pagina; MUST NOT reintroducir la lectura de "calibracion invertida" del clasificador en su conjunto; y MUST NOT presentar como demostrada la eficiencia del esquema hibrido.

#### Scenario: Hallazgo contrastado con la literatura

- **WHEN** se lee la subseccion de comparacion con la literatura
- **THEN** relaciona el comportamiento de la confianza de la etapa del modelo de lenguaje con lo que la literatura documenta sobre la confianza verbalizada
- **AND** relaciona la derivacion entre etapas del esquema hibrido con el criterio de derivacion de las cascadas de modelos

#### Scenario: Coherencia con el capitulo de resultados

- **WHEN** se compara el parrafo con la subseccion de calibracion del capitulo de resultados (`subsec:calibracion`)
- **THEN** describe el hallazgo por etapa del pipeline y en los mismos terminos que ese capitulo
- **AND** no afirma "calibracion invertida" ni "anti-calibracion" del clasificador en su conjunto

#### Scenario: Sin numeros nuevos ni eficiencia afirmada

- **WHEN** se revisan los valores numericos y las conclusiones del parrafo agregado
- **THEN** todo valor figura en `numeros-canonicos.md` o es una cifra de terceros citada textualmente con su pagina
- **AND** el parrafo no afirma que la eficiencia del esquema hibrido frente a una alternativa basada solo en el modelo haya sido contrastada

### Requirement: Higiene bibliografica de las fuentes de calibracion y cascadas

Las entradas que incorpora la extension C1-C2 SHALL agregarse a `Bibliography_base.bib` en un bloque aditivo comentado, con `author`, `title`, `year`, el campo de publicacion (`booktitle` o `journal`) y `doi` o `url` oficial, con claves `ApellidoAnio_palabra_clave` y con el tipo que corresponde a la naturaleza real de la fuente (`@inproceedings` para actas, `@article` para revistas). Ninguna entrada existente MUST modificarse, ninguna clave MUST duplicarse y toda entrada nueva SHALL citarse al menos una vez en el texto.

#### Scenario: Entradas completas y bien tipadas

- **WHEN** se inspeccionan las entradas del bloque de calibracion y cascadas
- **THEN** cada una incluye autor, titulo, ano, campo de publicacion y `doi` o `url` oficial
- **AND** las actas se tipan `@inproceedings` y la revista TMLR `@article`, sin presentar un preprint como publicacion arbitrada

#### Scenario: Correspondencia citas-bibliografia preservada

- **WHEN** se ejecuta `verify_citations.py` despues del change
- **THEN** reporta cero citas huerfanas y cero entradas sin usar
- **AND** cada clave nueva aparece una sola vez como entrada en `Bibliography_base.bib`

#### Scenario: Entradas existentes intactas

- **WHEN** se inspecciona el diff de `Bibliography_base.bib`
- **THEN** solo contiene lineas agregadas en el bloque nuevo
- **AND** ninguna entrada previa cambia de clave ni de campos

### Requirement: Impacto de paginas de la cobertura de calibracion y cascadas medido y acotado

El change SHALL registrar el numero de paginas del PDF compilado antes y despues de aplicarse, medido sobre el documento completo, y el aumento atribuible a sus inserciones MUST NOT superar tres paginas. Si lo supera, SHALL aplicarse la contingencia declarada en el diseno (reduccion del parrafo de discusion y retiro de fuentes en el orden declarado) antes de cerrar el change. El conteo resultante SHALL quedar registrado para la verificacion final del tope de paginas de la release.

#### Scenario: Conteo registrado antes y despues

- **WHEN** se compila `main.tex` antes y despues de aplicar el change
- **THEN** ambos conteos, medidos sobre el PDF completo, quedan registrados en `tasks.md`
- **AND** se identifica que capitulos o secciones crecieron

#### Scenario: Aumento acotado

- **WHEN** se calcula la diferencia de paginas atribuible al change
- **THEN** es de tres paginas o menos
- **AND** si inicialmente la excedia, la contingencia del diseno se aplico y el conteo final la respeta

### Requirement: Subseccion de calibracion del gate de confianza en el capitulo de recomendaciones

El capitulo de recomendaciones (`10-recomendaciones.tex`) SHALL incluir una subseccion propia para la calibracion del gate de confianza, rotulada `subsec:calibracion-gate` y ubicada antes de la subseccion del clasificador supervisado. La subseccion SHALL enunciar un diagnostico coherente con el analisis de calibracion por etapa del capitulo de resultados: el gate de 0,70 solo aplica a la etapa Gemini y a la etapa de reserva, la etapa deterministica se gobierna por su propio score de correctitud y la confianza autodeclarada de Gemini no discrimina aciertos de errores en su rango efectivo (0,85 a 1,00). La subseccion SHALL proponer: un conjunto de validacion propio disjunto del corpus de evaluacion; al menos tres senales independientes del puntaje, entre ellas la ambiguedad lexica entre categorias candidatas, el margen entre la primera y la segunda categoria y la revision por muestreo de casos de alta confianza; una recalibracion posterior del puntaje, declarando que corrige su nivel pero no crea capacidad de discriminacion; y la derivacion del umbral del gate a partir de una curva de cobertura y precision ajustada fuera de la muestra, con un criterio declarado de antemano, como el punto de operacion de la etapa deterministica. El texto MUST NOT reintroducir la "calibracion invertida" del clasificador en su conjunto, MUST NOT presentar la propuesta como resultado y MUST NOT agregar entradas a `Bibliography_base.bib`.

#### Scenario: Subseccion presente y ubicada entre las prioritarias

- **WHEN** se inspecciona `10-recomendaciones.tex`
- **THEN** existe una `\subsection` con `\label{subsec:calibracion-gate}`
- **AND** ese rotulo aparece antes de `\label{subsec:clasificador-supervisado}`

#### Scenario: Diagnostico coherente con la calibracion por etapa

- **WHEN** se compara la subseccion con el analisis de calibracion del capitulo de resultados
- **THEN** la falta de discriminacion se atribuye a la confianza autodeclarada de Gemini en su rango efectivo y no al clasificador en su conjunto
- **AND** el gate de 0,70 se describe como aplicable solo a la etapa Gemini y a la etapa de reserva

#### Scenario: Propuesta con senales independientes, recalibracion y umbral derivado

- **WHEN** se lee la propuesta de la subseccion
- **THEN** figuran el conjunto de validacion propio disjunto del corpus de evaluacion, al menos tres senales independientes del puntaje y una recalibracion posterior con la advertencia de que no crea capacidad de discriminacion
- **AND** el umbral del gate se deriva de una curva de cobertura y precision ajustada fuera de la muestra, con un criterio declarado de antemano

#### Scenario: Sin bibliografia nueva desde este change

- **WHEN** se compara `Bibliography_base.bib` antes y despues del change
- **THEN** no hay entradas nuevas atribuibles a este change
- **AND** toda cita de la subseccion apunta a una entrada existente o incorporada por el change dueno de la bibliografia, y `verify_citations.py` reporta PASS

### Requirement: Subseccion de correccion de la medicion de intervencion humana

El capitulo de recomendaciones SHALL incluir una subseccion propia, rotulada `subsec:medicion-intervencion` y ubicada inmediatamente despues de la subseccion del clasificador supervisado, que proponga un protocolo de registro primario de la intervencion humana por caso. El protocolo SHALL registrar, para cada intervencion, su ocurrencia y origen, la consigna de tiempo de inicio y de fin, el resultado (categoria confirmada o corregida) y el operador seudonimizado, y SHALL indicar como almacenamiento la ampliacion de `clasificacion_log` o una tabla dedicada vinculada al incidente. La definicion operacional SHALL alinearse con las dos formas rotuladas de la variable de intervencion humana de `tab:variables` y aplicarse de igual modo en ambos brazos, de modo que la sub-hipotesis de intervencion, hoy no contrastada por ausencia de registro primario, pueda contrastarse en una replicacion. La subseccion MUST NOT reportar ninguna proporcion de intervencion humana como resultado.

#### Scenario: Subseccion presente a continuacion del clasificador supervisado

- **WHEN** se inspecciona `10-recomendaciones.tex`
- **THEN** existe una `\subsection` con `\label{subsec:medicion-intervencion}`
- **AND** es la subseccion inmediatamente posterior a `subsec:clasificador-supervisado`

#### Scenario: Protocolo de registro primario por caso

- **WHEN** se lee la subseccion
- **THEN** el protocolo enumera la ocurrencia y el origen de la intervencion, la consigna de tiempo de inicio y de fin, el resultado y el operador seudonimizado
- **AND** indica como almacenamiento la ampliacion de `clasificacion_log` o una tabla dedicada vinculada al incidente

#### Scenario: Definicion alineada con la tabla de variables y contrastabilidad

- **WHEN** se compara la subseccion con `tab:variables` y con la sub-hipotesis de intervencion de `subsec:hipotesis-trabajo`
- **THEN** la definicion operacional usa las mismas dos formas rotuladas (proporcion de casos y proporcion del tiempo del proceso) aplicadas a ambos brazos
- **AND** la subseccion explica que registro permitiria contrastar la sub-hipotesis en la formulacion vigente

#### Scenario: Sin proporcion de intervencion reportada

- **WHEN** se buscan en el capitulo de recomendaciones cifras de proporcion de intervencion humana
- **THEN** no aparece ninguna presentada como resultado
- **AND** no aparece el 9,5 % retirado

### Requirement: Aprendizaje activo condicionado a la calibracion de la confianza

La subseccion de aprendizaje activo (`subsec:aprendizaje-activo`) SHALL NOT proponer la priorizacion de casos por baja confianza declarada como criterio incondicional. SHALL apoyar la seleccion de casos en las senales independientes del puntaje de `subsec:calibracion-gate` y SHALL condicionar el uso de la confianza declarada como criterio de prioridad a una recalibracion validada segun esa subseccion. El texto MUST NOT presuponer que el gate deriva casos a revision. El rotulo `subsec:aprendizaje-activo` SHALL conservarse y la subseccion de base de conocimientos SHALL seguir remitiendo a el.

#### Scenario: Criterio de seleccion independiente del puntaje

- **WHEN** se lee la subseccion de aprendizaje activo
- **THEN** remite con `\autoref` a `subsec:calibracion-gate`
- **AND** la baja confianza declarada no figura como criterio de prioridad sin la condicion de una recalibracion validada

#### Scenario: Sin presuponer derivaciones del gate

- **WHEN** se lee la subseccion de aprendizaje activo
- **THEN** no afirma que la intervencion humana ocurre en los casos derivados a revision por el gate
- **AND** las revisiones que alimentan el ajuste incremental se vinculan con el registro de `subsec:medicion-intervencion`

#### Scenario: Remision de la base de conocimientos preservada

- **WHEN** se lee la subseccion de base de conocimientos
- **THEN** sigue remitiendo con `\autoref` a `subsec:aprendizaje-activo`
- **AND** el rotulo `subsec:aprendizaje-activo` se conserva sin cambios

### Requirement: Replicaciones con exactitud del flujo manual y asignacion muestral no proporcional

La subseccion de estudios de replicacion (`subsec:estudios-replicacion`) SHALL recomendar medir la exactitud del flujo manual sobre el mismo corpus, con etiquetadores distintos de los operadores del brazo manual, y SHALL recomendar una asignacion muestral no proporcional que sobremuestree las clases minoritarias y pondere las estimaciones globales por la distribucion del universo. La subseccion SHALL conservar su rotulo y los contextos de replicacion que ya enuncia.

#### Scenario: Exactitud del flujo manual con etiquetadores independientes

- **WHEN** se lee la subseccion de estudios de replicacion
- **THEN** recomienda medir la exactitud del flujo manual sobre el mismo corpus
- **AND** exige que los etiquetadores de la referencia sean distintos de los operadores del brazo manual

#### Scenario: Asignacion no proporcional ponderada

- **WHEN** se lee la subseccion de estudios de replicacion
- **THEN** recomienda sobremuestrear las clases minoritarias y ponderar las estimaciones globales por la distribucion del universo
- **AND** si menciona la clase Bases de Datos, lo hace con el soporte canonico de un caso

#### Scenario: Rotulo y contextos preservados

- **WHEN** se inspecciona la subseccion de estudios de replicacion
- **THEN** conserva `\label{subsec:estudios-replicacion}`
- **AND** mantiene los contextos de replicacion del sector publico, del sector industrial y de organizaciones de mayor tamano

### Requirement: Correspondencia entre el parrafo de priorizacion y las subsecciones del capitulo

El parrafo introductorio del capitulo de recomendaciones SHALL referenciar con `\autoref` la subseccion propia de cada linea anunciada como prioritaria (calibracion del gate de confianza, clasificador supervisado con corpus propio y correccion de la medicion de intervencion humana), y cada una de esas lineas SHALL existir como `\subsection` con `\label`. Las tres subsecciones prioritarias SHALL preceder al resto de las subsecciones del capitulo. El parrafo SHALL clasificar cada subseccion del capitulo en un nivel de prioridad, y su remision al analisis de errores SHALL apuntar a `subsec:analisis-errores`. El capitulo MUST NOT anunciar una linea prioritaria sin desarrollo propio.

#### Scenario: Cada linea prioritaria tiene subseccion

- **WHEN** se extraen los `\autoref` del parrafo introductorio y los `\label` de las subsecciones del capitulo
- **THEN** `subsec:calibracion-gate`, `subsec:clasificador-supervisado` y `subsec:medicion-intervencion` aparecen en ambos conjuntos
- **AND** no queda ninguna linea anunciada como prioritaria sin subseccion propia

#### Scenario: Orden de las subsecciones prioritarias

- **WHEN** se comparan las posiciones de los rotulos de subseccion en `10-recomendaciones.tex`
- **THEN** los tres rotulos prioritarios aparecen antes que cualquier otro rotulo de subseccion del capitulo

#### Scenario: Todas las subsecciones clasificadas y remision correcta

- **WHEN** se compara el parrafo introductorio con la lista de subsecciones del capitulo
- **THEN** cada subseccion figura en uno de los niveles de prioridad enunciados
- **AND** la remision al analisis de errores apunta a `subsec:analisis-errores` y no a `subsec:calibracion`

### Requirement: Destino de las referencias anticipadas al capitulo de recomendaciones

Toda remision a `sec:recomendaciones` desde otro capitulo que anuncie una evolucion o un trabajo futuro SHALL encontrar esa linea mencionada en el capitulo de recomendaciones. En particular, la calibracion de los parametros de inferencia, la autenticacion unica corporativa (SSO), el prefijo configurable del numero de incidente y la migracion a Kubernetes SHALL figurar en el capitulo.

#### Scenario: Referencias anticipadas con destino

- **WHEN** se listan las remisiones a `sec:recomendaciones` en los demas archivos de `paper/sections/`
- **THEN** cada tema anunciado por esas remisiones aparece en `10-recomendaciones.tex`
- **AND** ninguna remision queda sin una linea correspondiente en el capitulo

### Requirement: Neutralidad numerica de las lineas de trabajo futuro

El texto nuevo o reescrito del capitulo de recomendaciones SHALL limitarse a valores numericos que ya figuran en el documento o que tienen estado `vigente` en `docs/Tesis/Correcciones/numeros-canonicos.md`: el umbral del gate (0,70), el rango efectivo de confianza de Gemini (0,85 a 1,00), el umbral del 85 % del segundo objetivo especifico, el tamano del corpus (200 casos), el soporte de un caso de Bases de Datos y los valores que el capitulo ya contenia antes del change. El texto MUST NOT reintroducir cifras con estado `retirado` ni introducir valores sin procedencia.

#### Scenario: Cifras del texto agregado en la lista blanca

- **WHEN** se extraen los numeros de las lineas agregadas o reescritas en `10-recomendaciones.tex`
- **THEN** cada uno figura en la lista de valores admitidos o tiene estado `vigente` en `numeros-canonicos.md`
- **AND** ninguna cifra con estado `retirado` reaparece en el capitulo

### Requirement: Impacto de paginas acotado del capitulo de recomendaciones

Tras el change, el capitulo de recomendaciones SHALL ocupar a lo sumo cinco paginas del PDF compilado (cuatro en la release v1.1.1), medidas como la diferencia entre la pagina de inicio de las referencias bibliograficas y la pagina de inicio del capitulo en `main.toc`. El crecimiento SHALL compensarse dentro del capitulo condensando las subsecciones del agente conversacional telefonico y de la base de conocimientos, sin perder los elementos exigidos por los requisitos vigentes ni los elementos tecnicos de la justificacion del agente. El delta de paginas medido SHALL registrarse para la verificacion global del change de integracion.

#### Scenario: Extension del capitulo acotada

- **WHEN** se compila el PDF tras el change y se leen en `main.toc` las paginas de inicio del capitulo y de las referencias bibliograficas
- **THEN** la diferencia es de cinco paginas o menos
- **AND** el delta respecto de la release v1.1.1 queda registrado en la entrada de trazabilidad del change

#### Scenario: Condensacion sin perdida de elementos exigidos

- **WHEN** se leen las subsecciones condensadas
- **THEN** la del agente conversacional conserva Twilio Media Streams, la madurez de las interfaces de audio bidireccional, la transcodificacion mu-law a PCM, la gestion de turnos de habla, el modelo de costo por minuto y la recomendacion de una prueba de concepto con la grabacion actual como respaldo
- **AND** la de base de conocimientos conserva al menos dos parrafos, los ejemplos de incidentes simples, las remisiones a aprendizaje activo y a modelos abiertos y la ausencia de citas

#### Scenario: Partes protegidas sin cambios

- **WHEN** se compara el capitulo con su version previa al change
- **THEN** el primer parrafo de `subsec:panel-monitoreo` y el texto de `subsec:clasificador-supervisado` no fueron modificados por este change
- **AND** `subsec:evaluacion-modelos-abiertos` conserva su contenido

### Requirement: Atribuciones del eje de modelos de lenguaje conformes al contenido de las fuentes

El eje de procesamiento de lenguaje natural y modelos de lenguaje grandes del marco teorico (seccion 2.4) y el estado del arte multilingue del capitulo 3 SHALL atribuir a cada fuente solo lo que esa fuente sostiene, contrastado con su texto completo cuando es de acceso abierto o con el resumen de la pagina del editor. El documento MUST NOT citar Xuan et al. (2025) como fuente de calibracion de la confianza, MUST NOT citar Lai et al. (2023) como evidencia de sensibilidad a la redaccion del prompt, MUST NOT citar Zhang et al. (2023) como evidencia de generalizacion fuera del ingles, y MUST NOT atribuir a Mayor-Rocher et al. (2026) ni a Grandury et al. (2025) diferencias de desempeno por dialecto que esas obras no reportan. La fundamentacion bibliografica de la calibracion SHALL provenir de fuentes que estudien la calibracion (incorporadas por c-138); hasta entonces el parrafo MUST NOT conservar una cita que no la trate.

#### Scenario: Calibracion sin atribucion a un benchmark de rendimiento

- **WHEN** se lee el parrafo de la seccion 2.4 que define la calibracion de la confianza
- **THEN** el parrafo no cita `xuan2025mmluprox`
- **AND** ninguna fuente citada en ese parrafo es una obra que no trate la calibracion

#### Scenario: Xuan et al. citado por lo que sostiene

- **WHEN** se buscan todas las citas de `xuan2025mmluprox` en las secciones de la tesis
- **THEN** cada una le atribuye solo resultados de rendimiento multilingue (benchmark de 29 idiomas, caida del desempeno en los idiomas con menos recursos, resultados desagregados por idioma)
- **AND** ninguna le atribuye resultados sobre calibracion, confianza o incertidumbre

#### Scenario: Diseno del prompt respaldado por la fuente adecuada

- **WHEN** se lee el parrafo de la seccion 2.4 sobre el diseno del prompt
- **THEN** Lai et al. (2023) no se cita como evidencia de sensibilidad a la redaccion del prompt
- **AND** Ahuja et al. (2023) se cita solo por su comparacion de estrategias de prompting entre idiomas
- **AND** no se afirma un efecto del orden o de la seleccion de los ejemplos sin una fuente que lo estudie

#### Scenario: Idiomas, alternancia de codigo y variedades del espanol

- **WHEN** se leen las citas de Lai et al. (2023), Zhang et al. (2023), Grandury et al. (2025) y Mayor-Rocher et al. (2026)
- **THEN** Lai et al. se cita por el ajuste por instrucciones de modelos abiertos concentrado en el ingles y en pocos idiomas, Zhang et al. por el rendimiento ante textos con alternancia de codigo, Grandury et al. por su tabla de clasificacion de variedades del espanol y Mayor-Rocher et al. por su evaluacion con pruebas de espanol como lengua extranjera
- **AND** a ninguna se le atribuyen diferencias de desempeno atribuibles al dialecto que la obra no reporte

#### Scenario: Agrupamientos de citas coherentes

- **WHEN** se lee un comando de cita con varias claves en el estado del arte multilingue del capitulo 3
- **THEN** cada clave del agrupamiento sostiene la afirmacion a la que se adjunta
- **AND** Lai et al. y Zhang et al. no respaldan la afirmacion de que el rendimiento favorece a los idiomas con mas recursos

### Requirement: Sintesis del estado del arte y recomendaciones coherentes con la evidencia comparativa citada

Las afirmaciones de sintesis del estado del arte, de la discusion y de las recomendaciones SHALL ser coherentes con los resultados de las fuentes en que se apoyan. El documento MUST NOT afirmar que la literatura reciente confirma un desplazamiento del enfoque clasico hacia los LLM cuando sus fuentes comparativas (Paket et al., 2024; Colavito et al., 2025) encuentran que los modelos tipo BERT igualan o superan a los LLM generativos, y MUST NOT citar Touvron et al. (2023) como evidencia de que los LLM desplegados localmente son competitivos en clasificacion mediante prompts. Toda caracterizacion de una obra citada en estas secciones SHALL poder contrastarse con su resumen o con su texto completo.

#### Scenario: Sintesis del estado del arte sin desplazamiento contrario a la evidencia

- **WHEN** se lee la oracion de sintesis que precede a la tabla `tab:trabajos-academicos`
- **THEN** no afirma que la literatura confirme un desplazamiento hacia arquitecturas basadas en LLM
- **AND** refleja que en las comparaciones directas relevadas los modelos tipo BERT igualan o superan a los LLM generativos, con cita explicita a `paket2024itservice` y `colavito2025benchmarking`

#### Scenario: Llama 2 citado por la disponibilidad de pesos abiertos

- **WHEN** se lee la recomendacion sobre el clasificador supervisado y los modelos de codigo abierto en el capitulo de recomendaciones
- **THEN** `Touvron2023_llama2` se cita solo por la disponibilidad de modelos de pesos abiertos aptos para despliegue local
- **AND** la competitividad en clasificacion no se le atribuye
- **AND** se consigna que en clasificacion de tickets con muchas clases los modelos tipo BERT superaron a LLM abiertos como Llama y Mistral (`paket2024itservice`)

#### Scenario: Caracterizaciones contrastables con la fuente

- **WHEN** se contrastan las citas de Colavito et al. (2025) en el marco teorico y de Jurafsky y Martin en la seccion 2.4 con el resumen o el indice de la version citada
- **THEN** cada caracterizacion se limita a lo que esa evidencia sostiene
- **AND** las inferencias propias de los autores no se presentan como resultados de la fuente

#### Scenario: Cobertura del espanol en la discusion respaldada

- **WHEN** se lee el parrafo de la discusion sobre el desempeno en espanol rioplatense frente a idiomas de mayor cobertura
- **THEN** la afirmacion de que diversos trabajos senalan la menor cobertura de los idiomas distintos del ingles cita fuentes que la sostienen
- **AND** no se menciona un desempeno reportado para el aleman sin una fuente que lo reporte

### Requirement: Cifras de Paramesh y Shreedhara (2019) localizadas o reformuladas

Toda cifra atribuida a Paramesh y Shreedhara (2019) (tamano del corpus, idioma, representacion textual o exactitud) SHALL acompanarse de la pagina del capitulo de la que proviene, o bien SHALL dejar de atribuirse si no puede localizarse en el texto completo. En ausencia de verificacion, la descripcion de la obra SHALL limitarse a lo que sostiene su resumen (comparacion de Naive Bayes multinomial, regresion logistica, k vecinos mas cercanos y SVM sobre tickets reales de una mesa de servicio de infraestructura de TI, con SVM como el clasificador de mejor desempeno) y las celdas de la tabla de trabajos academicos SHALL declarar "no reportado en el alcance revisado". La autoria MUST corresponder a la registrada en Crossref (Paramesh, S. P., y Shreedhara, K. S.).

#### Scenario: Cifras con pagina

- **WHEN** la tesis atribuye a `Paramesh2019_it_service_desk` el tamano del corpus, el idioma, la representacion TF-IDF o una exactitud
- **THEN** cada cita que acompana esas cifras indica la pagina del capitulo
- **AND** cada cifra coincide con la que figura en esa pagina

#### Scenario: Cifras no verificables retiradas

- **WHEN** las cifras no pueden localizarse en el texto completo
- **THEN** ninguna seccion atribuye a la obra 10.000 tickets, el idioma ingles, la representacion TF-IDF ni una exactitud de 87 %
- **AND** la fila de la obra en `tab:trabajos-academicos` declara "no reportado en el alcance revisado" para el corpus y la metrica, con el resultado cualitativo que sostiene el resumen

#### Scenario: Umbral del 85 % sin cifra no localizada

- **WHEN** se lee la justificacion del umbral de exactitud del 85 % en la introduccion
- **THEN** su primer criterio no se apoya en una cifra de Paramesh y Shreedhara que no haya sido localizada con pagina
- **AND** el criterio sigue declarando su fuente

#### Scenario: Autoria y caracterizacion de la obra

- **WHEN** se inspecciona la entrada `Paramesh2019_it_service_desk` y se lee su descripcion en el estado del arte
- **THEN** la entrada conserva los autores Paramesh y Shreedhara
- **AND** el texto no presenta la obra como uno de los primeros trabajos exhaustivos del area ni la nombra "Paramesh y Ramya"

### Requirement: Entradas bibliograficas de las normas y marcos del capitulo de cumplimiento

Las normas y marcos que el capitulo 11 declara adoptados SHALL tener entrada propia en `Bibliography_base.bib` y cita en el texto: ISO/IEC 27001:2022, ISO/IEC 27002:2022, ISO/IEC 27701 en su edicion vigente, NIST CSF 2.0 y el Decreto 1558/2001 reglamentario de la Ley 25.326. Cada entrada SHALL verificarse antes de agregarse contra la ficha oficial del organismo (ISO, NIST, InfoLEG) o su DOI, e incluir organismo autor, titulo, ano, identificador (numero de norma, numero de documento o de decreto) y `doi` o `url`, con `urldate` cuando se cita por URL. El documento MUST NOT citar como marco adoptado una edicion retirada (ISO/IEC 27701:2019, retirada el 2025-10-14) y MUST NOT incorporar datos no verificados. Las afirmaciones del capitulo que la cita formal vuelve contrastables SHALL coincidir con las normas citadas.

#### Scenario: Entradas presentes y verificadas

- **WHEN** se inspecciona `Bibliography_base.bib`
- **THEN** existen las entradas `ISO27001_2022`, `ISO27002_2022`, `ISO27701_2025`, `NIST2024_csf` y `Decreto1558_2001`, con autor institucional, titulo, ano e identificador
- **AND** `NIST2024_csf` declara el DOI `10.6028/NIST.CSWP.29` y las demas una `url` de la ficha oficial con `urldate`
- **AND** las claves contienen solo letras, digitos y guiones bajos

#### Scenario: Edicion vigente de ISO/IEC 27701

- **WHEN** se lee la enumeracion de marcos adoptados del capitulo 11 y su cita
- **THEN** ISO/IEC 27701 se identifica con su edicion vigente (2025) y se describe como norma de gestion de la privacidad
- **AND** no se cita la edicion 2019 como marco adoptado

#### Scenario: Citas en el capitulo de cumplimiento

- **WHEN** se lee el capitulo 11
- **THEN** la primera mencion de cada norma o marco adoptado lleva su cita y el decreto reglamentario de la Ley 25.326 se cita junto a su mencion
- **AND** no hay citas dentro de titulos de seccion, leyendas de tabla ni lineas de fuente de tabla

#### Scenario: Afirmaciones contrastables con las normas citadas

- **WHEN** se leen la introduccion de la tabla de alineacion ISO y la del perfil NIST
- **THEN** los controles se ubican en ISO/IEC 27002:2022 y en el Anexo A de ISO/IEC 27001:2022, no en un Anexo A de ISO/IEC 27002:2022
- **AND** la escala de madurez de 0 a 4 se declara propia del relevamiento y no se presenta como definida por NIST CSF 2.0

### Requirement: Referencias metodologicas primarias de los procedimientos estadisticos

La prueba de rangos con signo, el analisis de potencia a priori y el bootstrap percentil SHALL respaldarse en el marco metodologico con una referencia primaria verificada, ademas de la referencia de implementacion (SciPy): Wilcoxon (1945), *Biometrics Bulletin*, 1(6), 80-83, DOI 10.2307/3001968; Cohen (1988), *Statistical Power Analysis for the Behavioral Sciences*, 2.a ed.; y Efron y Tibshirani (1993), *An Introduction to the Bootstrap*. Las entradas MUST NOT declarar un DOI que corresponda a otra edicion o reedicion de la obra.

#### Scenario: Citas en el marco metodologico

- **WHEN** se lee el capitulo 4 donde se declaran la prueba de Wilcoxon, el bootstrap percentil y el analisis de potencia
- **THEN** cada procedimiento cita su referencia primaria (`Wilcoxon1945_individual_comparisons`, `Efron1993_bootstrap`, `Cohen1988_power_analysis`)
- **AND** `Virtanen2020_scipy` sigue citada como referencia de implementacion

#### Scenario: Metadatos de las referencias de metodo verificados

- **WHEN** se inspeccionan las tres entradas nuevas
- **THEN** Wilcoxon (1945) figura en la revista *Biometrics Bulletin*, volumen 1, numero 6, con su DOI resoluble
- **AND** Efron y Tibshirani (1993) declaran un DOI que resuelve a la edicion de 1993, y Cohen (1988) no declara el DOI de la reedicion de 2013

### Requirement: Metadatos bibliograficos coherentes con catalogos y editores (dictamen v1.1.0)

Las entradas senaladas por el dictamen v1.1.0 SHALL corregirse conforme a Crossref, a la ficha del editor o a un catalogo, y los anos de los libros SHALL seguir un criterio uniforme: el ano de copyright de la obra (criterio APA 7), o el de la version consultada en el caso de un borrador vivo. `Paramesh2019_it_service_desk` SHALL declarar el titulo del libro, su subtitulo, los editores y la serie; `Jurafsky2023_speech_language` SHALL declarar la URL del borrador y la fecha de la version consultada; `liu2025tickit` SHALL declarar la sede FSE Companion 2025. Toda entrada `@manual`, `@misc` u `@online` citada por URL SHALL tener `urldate`, y la fecha de consulta MUST NOT imprimirse dos veces. Ninguna `note` SHALL usar punto y coma, que el estilo suprime al imprimir. Las claves existentes MUST NOT renombrarse.

#### Scenario: Capitulo de libro con sus metadatos completos

- **WHEN** se inspecciona `Paramesh2019_it_service_desk`
- **THEN** declara el libro *Data Analytics and Learning* (*Proceedings of DAL 2018*), los editores Nagabhushan, Guru, Shekar y Sharath Kumar, la serie Lecture Notes in Networks and Systems, el volumen 43 y las paginas 331-346
- **AND** la referencia compilada ya no presenta el nombre de la serie como titulo del libro

#### Scenario: Anos con criterio uniforme

- **WHEN** se inspeccionan `Stallings2017_computer_security`, `Date2003_database` y `Russell2021_ai_modern`
- **THEN** sus anos son 2018, 2004 y 2021, respectivamente, cada uno confirmado como ano de copyright en la ficha del editor o en un catalogo
- **AND** las claves no se renombran y las citas en el texto muestran el ano corregido

#### Scenario: Borrador vivo con URL y version

- **WHEN** se inspecciona `Jurafsky2023_speech_language`
- **THEN** declara la URL `https://web.stanford.edu/~jurafsky/slp3/`, la fecha de la version del borrador consultada y su `urldate`
- **AND** conserva el tipo de borrador no publicado

#### Scenario: Fechas de consulta completas y no duplicadas

- **WHEN** se compila la bibliografia
- **THEN** las nueve entradas `@manual`/`@misc` con URL (`Apache2024_airflow`, `n8n2024_docs`, `PostgreSQL2024_docs`, `Tiangolo2024_fastapi`, `Wiggins2017_12factor`, `Ley25326_2000`, `SEPyME2026_mipyme`, `APA2017`, `Gomez2026_repositorio`) tienen `urldate`
- **AND** ninguna entrada imprime la fecha de consulta dos veces
- **AND** ninguna `note` contiene punto y coma

#### Scenario: Sede, seudonimo y enlace corregidos

- **WHEN** se inspeccionan `liu2025tickit`, `Tiangolo2024_fastapi` y `GDPR2016`
- **THEN** `liu2025tickit` identifica las actas de FSE Companion 2025
- **AND** `Tiangolo2024_fastapi` no imprime el seudonimo como apellido y `GDPR2016` declara su URL oficial con `urldate`, salvo que el usuario excluya expresamente estos dos ajustes

### Requirement: Rotulo correcto del conteo global de claves en el verificador de citas

El script `docs/Tesis/v10 (IA)/verify_citations.py` SHALL informar como "unique citation keys" el numero de claves distintas citadas en el conjunto de las secciones, y no la suma de las claves unicas de cada archivo; si conserva esa suma, SHALL rotularla de forma que no se confunda con el conteo global. El calculo SHALL estar cubierto por una prueba unitaria co-ubicada que se ejecute sin dependencias externas. El veredicto PASS/FAIL MUST NOT cambiar.

#### Scenario: Conteo global en el mensaje de verificacion

- **WHEN** se ejecuta `python verify_citations.py` sobre la tesis con todas las citas resueltas
- **THEN** la salida informa "N bibliography entries <-> N unique citation keys", con N igual al numero de claves distintas citadas
- **AND** ese N coincide con el de la linea de resumen "unique keys cited" y el estado es PASS

#### Scenario: Suma por archivo con rotulo propio

- **WHEN** una misma clave se cita en mas de un archivo
- **THEN** el conteo global la cuenta una sola vez
- **AND** la suma por archivo, si se informa, lleva un rotulo distinto del conteo global

#### Scenario: Prueba unitaria del conteo

- **WHEN** se ejecuta `python -m unittest test_verify_citations -v` desde `docs/Tesis/v10 (IA)/`
- **THEN** las pruebas pasan
- **AND** cubren claves compartidas entre archivos, claves disjuntas, la ausencia de citas y el mensaje impreso por `main()`

### Requirement: Impacto de paginas cuantificado con cuerpo neutral

Las ediciones de texto del change SHALL ser neutrales en paginas para el cuerpo: la pagina en que empieza "Referencias bibliograficas" MUST NOT cambiar respecto de la linea base tomada inmediatamente antes de aplicar el change. El crecimiento de la bibliografia por las entradas nuevas y los metadatos SHALL medirse (paginas totales y paginas de la bibliografia, antes y despues) y registrarse junto con las palancas de compensacion disponibles, para la verificacion final del presupuesto en c-141. El change MUST NOT editar el preambulo LaTeX ni eliminar contenido cientifico, numeros canonicos, figuras o tablas para compensar.

#### Scenario: Cuerpo neutral

- **WHEN** se compila la tesis antes y despues de aplicar el change
- **THEN** "Referencias bibliograficas" empieza en la misma pagina en ambas compilaciones

#### Scenario: Delta bibliografico registrado

- **WHEN** se cierra el change
- **THEN** quedan registrados el total de paginas y las paginas de inicio y fin de la bibliografia antes y despues
- **AND** quedan registradas las palancas de compensacion con su rendimiento estimado para c-141

#### Scenario: Sin compensacion destructiva

- **WHEN** se revisa el diff del change
- **THEN** el preambulo LaTeX no cambia
- **AND** no se eliminaron numeros canonicos, figuras ni tablas

### Requirement: Trazabilidad de las correcciones de correspondencia texto-fuente

Cada correccion de atribucion, alta bibliografica y ajuste de metadatos del change SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md` con su ubicacion, la fuente, la atribucion previa, lo que la fuente sostiene, la evidencia (URL y nivel: texto completo, resumen o ficha oficial) y la correccion aplicada. Las decisiones que se apartan de la letra del dictamen SHALL declararse con su fundamento.

#### Scenario: Registro por hallazgo

- **WHEN** se lee el grupo del change en `dictamen-correcciones.md`
- **THEN** cada hallazgo de A4, B15 y B16 tiene una fila con su evidencia y su correccion

#### Scenario: Desviaciones declaradas

- **WHEN** una correccion difiere de lo que propone el dictamen
- **THEN** el registro declara la diferencia y su fundamento (por ejemplo, la edicion vigente de ISO/IEC 27701, el ano de copyright de Russell y Norvig o la autoria de Paramesh y Shreedhara)

### Requirement: Inventario reproducible de tildes de la tesis

El repositorio SHALL incluir `docs/Tesis/v10 (IA)/revision_tildes.py`, implementado solo con la biblioteca estandar de Python y cubierto por pruebas automatizadas en `docs/Tesis/v10 (IA)/test_revision_tildes.py`. Ejecutado sin opciones, el script MUST NOT modificar ningun archivo y SHALL emitir un inventario determinista de candidatos de tilde faltante o improcedente en `paper/sections/*.tex`, con archivo, linea, columna, token, forma sugerida, clase y zona. La clase SHALL ser `INEQUIVOCO` cuando la forma encontrada no es una palabra valida del espanol en ese contexto (por ejemplo "erronea", "multiples") o cuando la ortografia vigente no admite la tilde (demostrativos y adverbio "solo" con tilde), y `AMBIGUO` cuando ambas formas existen (pares diacriticos como "esta"/"está", "hacia"/"hacía", y homografos verbo/sustantivo/adjetivo como "formula"/"fórmula", "continua"/"continúa", "asigno"/"asignó"). La zona SHALL ser `prosa`, `tabla` (cuerpo de entornos `tabular`) o `cita` (texto entre comillas). El inventario MUST excluir las zonas protegidas: las cinco cadenas canonicas exactas (`Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`), los argumentos de `\texttt`, `\url`, `\path`, el destino de `\href`, las claves de `\label`, `\ref`, `\autoref`, `\cref`, `\eqref`, `\pageref` y de los comandos de cita, las rutas de `\input`, `\include` e `\includegraphics`, los entornos `lstlisting`, `verbatim` y `minted`, `\verb` y `\lstinline`, la matematica, los comentarios, los nombres de comandos LaTeX y el resumen en ingles (desde `\section*{Abstract}` hasta el fin de `00-resumen.tex`).

#### Scenario: Ejecucion por defecto sin efectos

- **WHEN** se ejecuta `python "docs/Tesis/v10 (IA)/revision_tildes.py"` sin opciones
- **THEN** ningun archivo del repositorio cambia (`git status --short` es identico antes y despues)
- **AND** la salida lista los candidatos ordenados por archivo, linea y columna, y dos ejecuciones consecutivas producen exactamente la misma salida

#### Scenario: Zonas protegidas excluidas

- **WHEN** el inventario procesa un fragmento que contiene `Seguridad Informatica`, `\texttt{categoria}`, `\label{sec:introduccion}`, `\url{https://example.org/version}`, un entorno `lstlisting` con "JSON invalido", una expresion matematica, un comentario con "erronea" y un Abstract en ingles con "version"
- **THEN** no reporta ningun candidato dentro de esas zonas
- **AND** ninguna de las cinco cadenas canonicas recibe una sugerencia de tilde

#### Scenario: Clasificacion de candidatos

- **WHEN** el inventario procesa en prosa "derivación erronea", "tareas heterogeneas", "multiples canales" y "más alla del caso"
- **THEN** los reporta como `INEQUIVOCO` con las sugerencias "errónea", "heterogéneas", "múltiples" y "allá"
- **AND** reporta como `AMBIGUO` "sesgos hacía una clase", "la forma en que se fórmula la instrucción", "el flujo continua automáticamente", "el indicador esta activo", "no este vacía" y "La distribución de roles asigno la coordinación"

#### Scenario: Usos legitimos sin reporte

- **WHEN** el inventario procesa en prosa "mejora continua", "integración continua", "mediante la fórmula clásica", "el registro manual" y "derivación de incidentes hacia los sectores"
- **THEN** no reporta ningun candidato en esos fragmentos

#### Scenario: Deteccion completa de la linea base

- **WHEN** se ejecuta la prueba de regresion con las oraciones de la linea base v1.1.1 (las erratas de la muestra del dictamen y los hallazgos adicionales "multiples", "alla", "escaner" y "por si mismo")
- **THEN** cada errata se reporta con la clase esperada
- **AND** ningun uso legitimo incluido en la misma prueba (adjetivos "continua", sustantivos "fórmula", "aun" con valor de "incluso", verbos "valida" y "publica") recibe una correccion automatica

### Requirement: Aplicacion en dos pasos de las correcciones de tildes

`revision_tildes.py --diff` SHALL mostrar, sin escribir, el diff unificado de las correcciones `INEQUIVOCO` en zona `prosa`, y `revision_tildes.py --apply` SHALL escribir exactamente esas correcciones. Los candidatos `AMBIGUO` y los candidatos en zonas `tabla` o `cita` MUST NOT corregirse automaticamente, y ningun candidato con decision `mantener` en el registro de decisiones MUST aplicarse. La aplicacion SHALL preservar la capitalizacion (inicial mayuscula y todo mayusculas), la codificacion UTF-8 y los terminadores de linea (CRLF o LF) de cada archivo, MUST NOT crear archivos de respaldo (`.bak`) y SHALL ser idempotente.

#### Scenario: Diff revisable sin escritura

- **WHEN** se ejecuta `revision_tildes.py --diff`
- **THEN** la salida es un diff unificado que contiene solo correcciones `INEQUIVOCO` en zona `prosa`
- **AND** ningun archivo cambia

#### Scenario: Aplicacion limitada a inequivocos

- **WHEN** se ejecuta `--apply` sobre un fragmento con "derivación erronea" en prosa, "sesgos hacía una clase" en prosa y la celda de tabla `telefono`
- **THEN** solo "erronea" pasa a "errónea"
- **AND** las lineas con "hacía" y con `telefono` quedan identicas byte a byte

#### Scenario: Preservacion de forma

- **WHEN** se ejecuta `--apply` sobre un archivo con terminadores CRLF que contiene "Erronea" y "ERRONEA"
- **THEN** el resultado contiene "Errónea" y "ERRÓNEA"
- **AND** los terminadores CRLF y el resto de los bytes del archivo no cambian, y no se crea ningun archivo `.bak`

#### Scenario: Idempotencia

- **WHEN** se ejecuta `--apply` por segunda vez sobre el mismo arbol
- **THEN** ningun archivo cambia
- **AND** `--diff` no muestra ninguna correccion pendiente

### Requirement: Revision humana de homografos con registro de decisiones

Cada candidato que no se corrige automaticamente (`AMBIGUO`, o ubicado en zona `tabla` o `cita`) SHALL resolverse uno por uno y registrarse en `docs/Tesis/Correcciones/revision-tildes-decisiones.tsv` (UTF-8, separado por tabuladores) con archivo, token, contexto, decision (`corregir` o `mantener`), forma final y justificacion basada en la categoria gramatical del token en su contexto. Las decisiones SHALL seguir la ortografia vigente (RAE-ASALE, 2010): "hacia" preposicion sin tilde; "formula" verbo sin tilde y "fórmula" sustantivo con tilde; "continúa" verbo con tilde y "continua" adjetivo sin tilde; "está"/"esté" formas de "estar" con tilde y "esta"/"este" determinantes sin tilde; preteritos de tercera persona con tilde ("asignó", "gestionó"); "aún" (todavia) con tilde y "aun" (incluso) sin tilde; "sí" pronombre con tilde; demostrativos y adverbio "solo" sin tilde. Los identificadores de datos (nombres de columnas, campos o valores literales) y las citas textuales de incidentes del corpus MUST conservarse tal como estan. Las tablas que contienen alguna de las cinco cadenas canonicas MUST NOT editarse en esta revision, salvo la unificacion de nombres de sector confirmada por el usuario; sus candidatos SHALL registrarse como hallazgos.

#### Scenario: Cada candidato con decision registrada

- **WHEN** se cruza el inventario final con el registro de decisiones
- **THEN** todo candidato no automatico tiene una fila con decision y justificacion no vacia
- **AND** toda fila con decision `corregir` esta aplicada en el texto

#### Scenario: Homografos resueltos por categoria gramatical

- **WHEN** se leen los pasajes de la linea base que contenian "sesgos hacía una clase", "se fórmula la instrucción", "el flujo continua automáticamente", "el indicador esta activo", "cuando no lo esta,", "no este vacía", "la grabación esta acotada", "roles asigno" y "se gestiono"
- **THEN** se leen "sesgos hacia una clase", "se formula la instrucción", "el flujo continúa automáticamente", "el indicador está activo", "cuando no lo está,", "no esté vacía", "la grabación está acotada", "roles asignó" y "se gestionó"
- **AND** "mejora continua", "integración continua" y "mediante la fórmula clásica" permanecen sin cambios

#### Scenario: Datos y citas literales preservados

- **WHEN** se revisan las celdas de tabla que contienen identificadores (por ejemplo la columna `telefono` del modelo de datos) y las citas de incidentes del corpus entre comillas
- **THEN** no se agrega ni se quita ninguna tilde en identificadores ni en citas
- **AND** cada uno de esos candidatos consta en el registro con decision `mantener` y su justificacion

### Requirement: Ausencia de las erratas de tildes senaladas por el dictamen v1.1.0

Tras la revision, `docs/Tesis/v10 (IA)/paper/sections/*.tex` SHALL contener cero ocurrencias, fuera de zonas protegidas, de: "hacía" con valor de preposicion; "fórmula" con valor verbal; "continua" con valor verbal; "esta" y "este" con valor de verbo "estar"; "heterogeneas", "erronea", "erroneas", "antiguedad", "perimetro", "inequivocos", "enganosa", "simultanea" (adjetivo), "aquéllas", "asigno" y "gestiono" (preteritos); y de los hallazgos adicionales "multiples", "alla", "escaner" y "por si mismo". Los criterios de aceptacion SHALL expresarse por categoria gramatical y no por conteo bruto: los usos adjetivales de "continua" y nominales de "fórmula" MUST conservarse.

#### Scenario: Formas inequivocas en cero

- **WHEN** se ejecuta `grep -o -w` de cada una de las formas "heterogeneas", "erronea", "erroneas", "antiguedad", "perimetro", "inequivocos", "enganosa", "aquéllas", "asigno", "gestiono", "multiples", "alla" y "escaner" sobre `paper/sections/*.tex`
- **THEN** cada conteo es 0
- **AND** si una edicion previa a la pasada introdujo alguna de esas formas dentro de una zona protegida (por ejemplo un termino en ingles o un identificador), la ocurrencia consta en el registro de decisiones con decision `mantener` y su justificacion

#### Scenario: Homografos de la muestra resueltos

- **WHEN** se buscan en `paper/sections/*.tex` los contextos de la linea base "sesgos hacía", "concreta hacía", "incidentes hacía", "textuales hacía", "se fórmula", "incidentes continua", "flujo continua", "experto continua", "indicador esta", "lo esta,", "no este vacía", "grabación esta acotada", "presencia simultanea" y "por si mismo"
- **THEN** cada busqueda devuelve 0 ocurrencias

#### Scenario: Usos legitimos preservados

- **WHEN** se cuentan "mejora continua", "integración continua" y "la fórmula" antes y despues de la pasada
- **THEN** los conteos posteriores son iguales a los previos a la pasada

#### Scenario: Herramienta sin pendientes

- **WHEN** se ejecuta `python "docs/Tesis/v10 (IA)/revision_tildes.py" --check` al cerrar la pasada
- **THEN** el codigo de salida es 0

### Requirement: Cadenas visibles y bibliografia impresa acentuadas

Las cadenas visibles en el PDF que se definen fuera de `paper/sections/` SHALL llevar sus tildes: en `paper/main.tex`, "Índice general", "Índice de tablas", "Índice de figuras" y el titulo "Referencias bibliográficas" de `\printbibliography`; en `paper/preambles/preamble.tex`, el encabezado de pagina "AUTOMATIZACIÓN DE MESA DE AYUDA", la cadena `bibliography` de `\DefineBibliographyStrings` ("Referencias bibliográficas") y los metadatos `pdftitle` y `pdfkeywords`. En `Bibliography_base.bib`, el texto impreso en espanol de los campos `note` SHALL acentuarse con la notacion de escape LaTeX que ya usa el archivo (por ejemplo `Documentaci{\'o}n t{\'e}cnica oficial`); las claves, autores, anos, DOI, URL y demas metadatos MUST NOT cambiar. Los comentarios LaTeX quedan fuera de alcance.

#### Scenario: Encabezados y titulos con tildes

- **WHEN** se buscan "Indice general", "Indice de tablas", "Indice de figuras", "Referencias bibliograficas" y "AUTOMATIZACION" en las lineas no comentadas de `paper/main.tex` y `paper/preambles/preamble.tex`
- **THEN** no queda ninguna ocurrencia
- **AND** el indice general del PDF compilado muestra "Referencias bibliográficas" y el encabezado de pagina muestra "AUTOMATIZACIÓN DE MESA DE AYUDA"

#### Scenario: Metadatos del PDF con tildes

- **WHEN** se leen `pdftitle` y `pdfkeywords` en `paper/preambles/preamble.tex`
- **THEN** contienen "Automatización", "automatización", "clasificación" y "español"

#### Scenario: Notas de la bibliografia con tildes y metadatos intactos

- **WHEN** se buscan "Documentacion", "tecnica" y "edicion" en los campos `note` de `Bibliography_base.bib` y se compara el conjunto de claves `@tipo{clave` con el previo a la pasada
- **THEN** no queda ninguna ocurrencia y el conjunto de claves es identico
- **AND** `verify_citations.py` reporta PASS y el registro de Biber no contiene advertencias ni errores

### Requirement: Coherencia de los nombres de sector con su definicion canonica

Las menciones de los cinco sectores que la tesis presenta como "sectores canonicos" SHALL escribirse con la cadena canonica exacta, sin tildes, que la propia tesis define como string del clasificador (`05-arquitectura.tex`, `12-anexos.tex`), salvo que el usuario decida conservar en esos pasajes la forma legible con tildes; en ese caso la convencion y los pasajes afectados SHALL constar en el registro de la revision. En cualquiera de los dos casos, las ocurrencias previas de las cinco cadenas canonicas MUST NOT alterarse.

#### Scenario: Convencion canonica aplicada

- **WHEN** el usuario confirma la unificacion y se buscan "Seguridad Informática", "Soporte Técnico Hardware" y "Soporte Técnico Software" en `paper/sections/*.tex`
- **THEN** no queda ninguna ocurrencia en los pasajes que enumeran los "sectores canonicos"
- **AND** cada mencion unificada coincide byte a byte con una de las cinco cadenas canonicas

#### Scenario: Excepcion documentada

- **WHEN** el usuario decide conservar la forma con tildes en esos pasajes
- **THEN** los pasajes quedan sin cambios
- **AND** el registro de la revision consigna la convencion (nombre legible con tildes en prosa, cadena canonica sin tildes como dato del clasificador) y la lista de pasajes

### Requirement: Neutralidad de la revision ortotipografica

Todas las modificaciones que esta revision introduce en archivos de la tesis SHALL ser puramente diacriticas: cada linea modificada MUST ser igual a su version previa al normalizar tildes, dieresis y eñe (incluidas las secuencias de escape LaTeX de acentos del `.bib`), y la cantidad de lineas de cada archivo MUST conservarse. En consecuencia la revision MUST NOT alterar cifras, claves de `\label`/`\ref`/citas ni rutas. El PDF SHALL compilar con XeLaTeX sin errores fatales ni referencias indefinidas y con el mismo numero de paginas que la compilacion previa a la pasada, dentro del presupuesto de 101 paginas. `verify_citations.py` SHALL reportar PASS y `tesis_para_agente.md` SHALL regenerarse desde las fuentes corregidas.

#### Scenario: Diff puramente diacritico

- **WHEN** se ejecuta `revision_tildes.py --base <copia de paper/sections previa a la pasada>`
- **THEN** el codigo de salida es 0 y no se reporta ninguna linea con cambios no diacriticos
- **AND** la comparacion equivalente de `paper/main.tex`, `paper/preambles/preamble.tex` y `Bibliography_base.bib` contra el commit base tambien resulta puramente diacritica

#### Scenario: Cadenas canonicas sin alteraciones

- **WHEN** se cuenta cada una de las cinco cadenas canonicas en `paper/sections/*.tex` antes y despues de la pasada
- **THEN** el conteo posterior es igual al previo mas las menciones unificadas por la decision de coherencia de nombres de sector (cero si no se unifica)
- **AND** ninguna ocurrencia previa cambia ni incorpora tilde

#### Scenario: Conteo de paginas invariante

- **WHEN** se compila el PDF despues de la pasada con el mismo entorno que la compilacion previa
- **THEN** el numero de paginas es igual al previo y no supera 101
- **AND** el registro de compilacion no contiene errores fatales, referencias indefinidas ni advertencias nuevas de altura de encabezado

#### Scenario: Integridad de citas y render

- **WHEN** se ejecuta `verify_citations.py` y se regenera `tesis_para_agente.md`
- **THEN** la verificacion reporta PASS
- **AND** el render regenerado no contiene ninguna de las formas erroneas corregidas en las secciones

### Requirement: Pasada corta repetible para la integracion

`revision_tildes.py --check` SHALL terminar con codigo 0 si y solo si no quedan candidatos `INEQUIVOCO` en zona `prosa` y todo candidato restante tiene decision `mantener` en el registro de decisiones; en caso contrario SHALL terminar con codigo distinto de 0 y listar los candidatos pendientes con archivo, linea, token y forma sugerida. La correspondencia entre candidato y decision SHALL basarse en archivo, token y contexto normalizado, y MUST NOT depender del numero de linea. El procedimiento SHALL quedar documentado para que c-141 lo ejecute despues de cualquier edicion tardia de la prosa.

#### Scenario: Check limpio al cerrar la pasada

- **WHEN** se ejecuta `--check` con todas las correcciones aplicadas y las decisiones registradas
- **THEN** el codigo de salida es 0

#### Scenario: Errata reintroducida detectada

- **WHEN** una edicion posterior agrega "derivación erronea" en prosa y se ejecuta `--check`
- **THEN** el codigo de salida es distinto de 0
- **AND** la salida lista el archivo, la linea, el token y la sugerencia "errónea"

#### Scenario: Homografo nuevo sin decision

- **WHEN** una edicion posterior agrega "el flujo continua sin cambios" sin fila en el registro y se ejecuta `--check`
- **THEN** el codigo de salida es distinto de 0
- **AND** tras registrar la decision y aplicarla, `--check` termina con codigo 0

#### Scenario: Decisiones robustas a desplazamientos de linea

- **WHEN** se insertan lineas antes de un candidato con decision `mantener` y se ejecuta `--check`
- **THEN** la decision se sigue reconociendo y el candidato no se informa como pendiente

### Requirement: Registro de la revision ortotipografica y neutralizacion de la causa raiz

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incorporar una seccion de la recomendacion B14 con: commit base de la pasada, conteos por forma antes y despues, correcciones por clase, cantidad de decisiones y ruta del registro de decisiones, discrepancias con los conteos del dictamen ("fórmula" y "continua" con valor verbal), hallazgos fuera de la muestra, decision sobre los nombres de sector, causa raiz y procedimiento de la pasada corta. `docs/Tesis/acentuar_tesis.py` y `docs/Tesis/acentuar_tesis_v9.py` SHALL declarar en su cabecera que estan deprecados para la tesis v10, con el motivo y la herramienta que los reemplaza, sin cambios en su logica. El lexico de correcciones automaticas de `revision_tildes.py` MUST NOT contener correcciones incondicionales de homografos.

#### Scenario: Registro completo

- **WHEN** se lee la seccion B14 de `dictamen-correcciones.md`
- **THEN** contiene el commit base, los conteos antes y despues, las correcciones por clase, la ruta del registro de decisiones, las discrepancias con el dictamen, la causa raiz y la decision sobre los nombres de sector
- **AND** documenta el uso de `revision_tildes.py --check` como pasada corta para c-141

#### Scenario: Utilidades previas deprecadas

- **WHEN** se ejecuta `grep -c "DEPRECADO"` sobre `docs/Tesis/acentuar_tesis.py` y `docs/Tesis/acentuar_tesis_v9.py`
- **THEN** cada archivo devuelve al menos 1
- **AND** ambos compilan con `python -m py_compile` y su diff solo modifica el docstring de cabecera

#### Scenario: Lexico sin correcciones incondicionales de homografos

- **WHEN** una prueba unitaria inspecciona el lexico de correcciones automaticas de `revision_tildes.py`
- **THEN** ninguna de las claves "hacia", "formula", "continua", "esta", "este", "aquellas", "aquellos", "desarrollo", "completo", "registro", "valida" y "publica" figura como correccion `INEQUIVOCO`

### Requirement: Publicacion de una release de correccion sin mover tags publicados

Cuando una release publicada contenga afirmaciones que el repositorio desmienta, el
proyecto SHALL publicar una release de correccion nueva (por ejemplo `v1.2.1`) en lugar
de mover el tag existente. El tag de correccion SHALL ser anotado y SHALL crearse sobre
el commit C3, que contiene el texto corregido y el PDF recompilado. Ese commit C3 SHALL
actualizar el tag del Anexo B y retirar el hash de la release anterior, pero MUST NOT
intentar consignar su propio hash. Un commit posterior C4 SHALL consignar el hash
completo de 40 caracteres de C3 en el Anexo B y la nota de trazabilidad en
`docs/Tesis/Correcciones/dictamen-correcciones.md`. El tag superado SHALL registrarse
como superado y MUST NOT borrarse, recrearse ni reapuntarse.

#### Scenario: Tag de correccion anotado sobre el texto corregido

- **WHEN** se ejecutan `git cat-file -t v1.2.1` y `git rev-parse v1.2.1^{commit}`
- **THEN** el tag existe, es anotado (devuelve `tag`) y apunta al commit que contiene el texto corregido y el PDF recompilado
- **AND** el tag esta publicado en `origin`

#### Scenario: Tag publicado inmutable

- **WHEN** se compara `git rev-parse v1.2.0^{commit}` con el valor registrado antes de este change (`a49d035c67b32ae17e633ec04b09ecdd2781aac6`)
- **THEN** el valor no cambio
- **AND** el registro declara `v1.2.0` como superada por `v1.2.1`

#### Scenario: Hash en el commit posterior al tag

- **WHEN** se lee `sec:anexo-repositorio` en el commit C4 y se compara con `git rev-parse v1.2.1^{commit}`
- **THEN** figura el tag `v1.2.1` y el hash completo de 40 caracteres de C3
- **AND** el hash coincide en los 40 caracteres y figura tambien en la nota de trazabilidad del registro

### Requirement: Cronologia unica y fechada del estudio y de la construccion del artefacto

La tesis SHALL presentar una cronologia unica, en una figura (`\label{fig:cronograma}`) generada desde una fuente Mermaid versionada (`docs/diagrams/cronograma.md`), que feche los periodos de actividad de la construccion bajo Scrumban, la campana de medicion del flujo manual, la campana del flujo automatizado y la integracion de la version del modelo evaluada. Toda mencion textual de esos periodos en `01-introduccion.tex`, `04-marco-metodologico.tex`, `06-implementacion.tex` y `08-discusion.tex` SHALL coincidir con la cronologia. Cada fecha SHALL tener procedencia registrada en la fuente (evidencia verificable del repositorio o confirmacion explicita de los autores, con su fecha) y MUST NOT inventarse, interpolarse ni expresarse con mas precision que su evidencia. La tesis SHALL NOT fijar un numero de iteraciones ni fechas individuales de iteracion mientras no exista fuente primaria o confirmacion de los autores; en ese caso SHALL representar la construccion con la precision disponible (barras de mes).

#### Scenario: Figura de cronograma con fuente reproducible

- **WHEN** se inspeccionan `paper/figures/`, `docs/diagrams/` y las secciones de la tesis
- **THEN** existe `cronograma.png`, generada desde el bloque Mermaid de `docs/diagrams/cronograma.md` y embebida en un entorno `figure` con `\caption` y `\label{fig:cronograma}`
- **AND** la leyenda declara la precision de las fechas y su fuente

#### Scenario: Procedencia de cada fecha

- **WHEN** se revisa la tabla de procedencia de `docs/diagrams/cronograma.md`
- **THEN** cada elemento del cronograma tiene fecha o intervalo, precision (dia o mes) y evidencia (commit, pull request, change archivado o confirmacion de los autores con su fecha)
- **AND** ningun elemento carece de evidencia ni se dibuja con una precision mayor que la de su evidencia

#### Scenario: Menciones textuales conciliadas

- **WHEN** se comparan con la figura las menciones de periodos de `01-introduccion.tex`, `04-marco-metodologico.tex`, `06-implementacion.tex` y `08-discusion.tex`
- **THEN** todas coinciden con la cronologia
- **AND** no subsisten rotulos relativos ("Semanas 1--2" a "Semanas 11--12") ni una duracion total ("12 semanas") que la cronologia no respalde

#### Scenario: Version del modelo fechada en la campana automatizada

- **WHEN** se leen la limitacion sobre la version del modelo en `08-discusion.tex` y la delimitacion temporal de `01-introduccion.tex`
- **THEN** la version evaluada (`gemini-3.6-flash`) se ubica en el periodo de la campana automatizada
- **AND** "junio de 2026" no aparece como fecha de la version evaluada

#### Scenario: Relacion entre iteraciones y campanas explicita

- **WHEN** se lee la seccion de conexion con el proceso Scrumban de `06-implementacion.tex`
- **THEN** se declara que la campana automatizada corresponde a la etapa de validacion experimental y que la campana manual no forma parte de las etapas de construccion
- **AND** ninguna descripcion de iteracion afirma un orden temporal o una condicion incompatible con la cronologia fechada (por ejemplo, ajustes del clasificador declarados sin exposicion al corpus pero fechados despues de su procesamiento)

#### Scenario: Entregable de iteración coherente con la fecha de su artefacto

- **WHEN** se leen la lista de iteraciones de `06-implementacion.tex` (subsec:conexion-scrumban) y la lista de §4.9 de `04-marco-metodologico.tex`
- **THEN** cada entregable concreto atribuido a una iteración existe y su fecha de creación o de archivo (según `docs/diagrams/cronograma.md` y la historia de `openspec/changes/archive/`) cae dentro de la ventana declarada de esa iteración
- **AND** ningún artefacto creado después de la ventana (en particular el documento de arquitectura de `knowledge-base/` del 2026-06-10 y el contrato OpenAPI estático del 2026-06-11) se atribuye a la iteración 1

### Requirement: Parrafo introductorio del capitulo de resultados coherente con sus subsecciones

El parrafo introductorio de `07-resultados.tex` SHALL enumerar exactamente las subsecciones del capitulo, en su orden y con denominaciones coherentes con sus titulos, y SHALL NOT anunciar como dimension de los resultados una magnitud que el propio capitulo declara no medida. Si el parrafo usa un cardinal, este MUST coincidir con el numero de subsecciones.

#### Scenario: Enumeracion igual a las subsecciones

- **WHEN** se cuentan los `\subsection` de `07-resultados.tex` y las dimensiones enumeradas en su parrafo introductorio
- **THEN** ambos conjuntos coinciden en numero y en orden
- **AND** ninguna subseccion queda sin mencion

#### Scenario: Intervencion humana sin reduccion afirmada

- **WHEN** se lee el parrafo introductorio del capitulo de resultados
- **THEN** la dimension correspondiente se denomina "intervencion humana" o con otra denominacion neutra coherente con el titulo de su subseccion
- **AND** no se anuncia una "reduccion de la intervencion humana"

### Requirement: Completitud de las metricas de la tabla de trabajos academicos

La tabla `tab:trabajos-academicos` SHALL consignar en la columna "Metrica reportada" de cada trabajo la cifra principal que su resumen o su texto completo accesible reporten textualmente (nombre de la metrica, valor y modelo o condicion), y en "Corpus/idioma" el tamano y el idioma cuando la fuente los establezca. La leyenda "no reportado en el alcance revisado" SHALL quedar solo en las celdas cuya fuente accesible no consigne el dato, acompanada de su motivo abreviado. Cada celda completada SHALL tener su procedencia (DOI o URL consultada, fecha de consulta y ubicacion en la fuente) registrada en `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`. El documento MUST NOT recalcular, promediar ni inferir cifras, y MUST NOT agregar entradas a `Bibliography_base.bib`.

#### Scenario: Metricas completadas desde la fuente

- **WHEN** se contrasta cada celda de metrica de `tab:trabajos-academicos` con su registro de procedencia
- **THEN** el valor consignado coincide textualmente con el de la fuente registrada
- **AND** la celda identifica la metrica, el valor y el modelo o la condicion a que corresponde

#### Scenario: Residuo no reportado justificado

- **WHEN** una celda conserva "no reportado en el alcance revisado"
- **THEN** el registro de procedencia documenta que el resumen no consigna el dato y que el texto completo no fue accesible o tampoco lo consigna
- **AND** la celda declara ese motivo de forma abreviada

#### Scenario: Sin altas bibliograficas ni citas huerfanas

- **WHEN** se ejecuta `verify_citations.py` y se inspecciona el diff de `Bibliography_base.bib` tras completar la tabla
- **THEN** no hay citas huerfanas ni entradas sin usar
- **AND** `Bibliography_base.bib` no tiene cambios atribuibles a este cambio

### Requirement: Salvedad de cota inferior del tiempo telefonico en las conclusiones

Toda mencion del tiempo automatizado del canal telefonico en `09-conclusiones.tex` SHALL acompanarse de la salvedad de que el valor es una cota inferior de la duracion real de la llamada por el tope de 45 s de la grabacion, en coherencia con `04-marco-metodologico.tex` (`subsec:metricas-instrumentos`), `06-implementacion.tex` y `07-resultados.tex`. El valor reportado (20,1 s) MUST NOT cambiar.

#### Scenario: Cota inferior declarada en las conclusiones

- **WHEN** se lee la mencion del canal telefonico en `09-conclusiones.tex`
- **THEN** el texto declara que los 20,1 s son una cota inferior por el tope de 45 s de grabacion
- **AND** el valor coincide con el de `tab:tiempos-canal` redondeado (20,09 s)

#### Scenario: Coherencia entre capitulos

- **WHEN** se comparan las menciones del tiempo telefonico en metodologia, implementacion, resultados y conclusiones
- **THEN** todas declaran la condicion de cota inferior
- **AND** ninguna presenta el valor como la duracion completa de la llamada

### Requirement: Coherencia del Anexo H con el capitulo 5 sobre los parametros de inferencia

La descripcion de los parametros de inferencia en el Anexo H (`subsec:anexo-parametros-config` y `tab:anexo_gemini_params` de `12-anexos.tex`) SHALL ser coherente con la de `05-arquitectura.tex` (`subsec:capa-procesamiento`): los parametros SHALL presentarse como la configuracion adoptada para el despliegue y SHALL NOT calificarse como optimizados mientras no se documente un procedimiento de optimizacion con los valores alternativos evaluados. El cambio MUST NOT alterar los valores de los parametros salvo el tiempo de espera, que se rige por el requisito "Tiempo de espera de la inferencia coherente con la configuracion vigente durante la campana", ni introducir otras cifras.

#### Scenario: Sin calificativo de optimizacion en el Anexo H

- **WHEN** se leen la prosa de `subsec:anexo-parametros-config`, la leyenda y las filas de `tab:anexo_gemini_params`
- **THEN** no se afirma que los parametros esten optimizados ni que un valor optimice la latencia, la exactitud o el costo
- **AND** los parametros se describen como configuracion adoptada, en coherencia con `subsec:capa-procesamiento`

#### Scenario: Valores sin cambios salvo el tiempo de espera

- **WHEN** se comparan los valores de `tab:anexo_gemini_params` antes y despues del cambio
- **THEN** los valores de temperatura, top_p, max_tokens, candidate_count, safety_settings y version del SDK permanecen iguales
- **AND** el unico valor modificado es el del tiempo de espera, y no se agrega ninguna otra cifra a la prosa ni a la tabla

### Requirement: Tiempo de espera de la inferencia coherente con la configuracion vigente durante la campana

Las menciones del tiempo de espera de la inferencia con Gemini en `05-arquitectura.tex` (`subsec:capa-procesamiento`) y en la fila `timeout` de `tab:anexo_gemini_params` (`12-anexos.tex`) SHALL coincidir con la configuracion vigente durante la campana automatizada, determinada por `App/Backend/app/config/settings.py` y su historia en git: 30 s por intento (`gemini_timeout_seconds`, desde el commit `11036be`, 2026-09-24) y 60 s de presupuesto total por clasificacion (`gemini_total_timeout_seconds`, desde el commit `429f2c9`, 2026-09-29), salvo que los autores declaren un override aplicado durante la campana, que prevalece y se registra. El valor de 10 s MUST NOT presentarse como el del sistema evaluado. La procedencia SHALL registrarse en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`. El cambio MUST NOT introducir cifras que no surjan de `settings.py`, de la historia del repositorio o de la declaracion registrada de los autores.

#### Scenario: Tiempo de espera alineado en el capitulo 5 y en el Anexo H

- **WHEN** se leen `subsec:capa-procesamiento` en `05-arquitectura.tex` y la fila `timeout` de `tab:anexo_gemini_params`
- **THEN** ambas declaran el tiempo de espera por intento y el presupuesto total vigentes durante la campana (30 s y 60 s, salvo override registrado)
- **AND** ninguna mencion de la tesis presenta 10 s como el tiempo de espera del sistema evaluado

#### Scenario: Procedencia registrada en el memo de conteos tecnicos

- **WHEN** se revisa `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`
- **THEN** figuran como `vigente` el tiempo de espera por intento y el presupuesto total, con archivo y linea de `settings.py` y el commit que los introdujo, y el valor de 10 s como `retirado`
- **AND** la seccion de alineacion lista los cambios de `05-arquitectura.tex` y `12-anexos.tex` (ANTES y DESPUES)

#### Scenario: Reintentos del modelo distinguidos de la invocacion de N8N

- **WHEN** se lee la descripcion del tiempo de espera por intento junto con la seccion de desafios de integracion de `06-implementacion.tex`
- **THEN** queda claro que los intentos se refieren a la invocacion del backend al modelo
- **AND** la descripcion no contradice la afirmacion de que la invocacion de N8N al backend no tiene reintentos

#### Scenario: Archivos de configuracion de agentes sin cambios

- **WHEN** se inspecciona el diff del cambio
- **THEN** `CLAUDE.md` y `openspec/config.yaml` no tienen modificaciones atribuibles a este cambio
- **AND** la nota de coordinacion con c-130 sobre esos archivos figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

### Requirement: Neutralidad de paginas de las correcciones de cronologia y consistencia

La aplicacion de este cambio SHALL ser neutral en paginas: el total del PDF compilado despues del cambio MUST ser menor o igual que el total medido inmediatamente antes de aplicarlo, contado sobre el documento completo. La figura de cronograma SHALL compensarse con palancas de forma admitidas (condensar la lista redundante de iteraciones de la seccion Scrumban de `04-marco-metodologico.tex`, limitar el alto de la figura, redacciones de longitud neutra) sin eliminar contenido cientifico.

#### Scenario: Total de paginas sin aumento

- **WHEN** se compila `main.tex` antes y despues del cambio con la misma cadena (XeLaTeX y biber) y se cuentan las paginas del PDF completo
- **THEN** el total posterior es menor o igual que el anterior
- **AND** ambos conteos quedan registrados en las tareas

#### Scenario: Compensacion sin perdida de contenido

- **WHEN** se compara la seccion Scrumban de `04-marco-metodologico.tex` antes y despues del cambio
- **THEN** la lista de iteraciones condensada remite a la seccion de conexion con Scrumban y a la figura, donde se conserva el detalle de cada iteracion
- **AND** la demarcacion entre el metodo de investigacion y el metodo de construccion permanece

#### Scenario: Compilacion sin errores

- **WHEN** se compila con `latexmk` (XeLaTeX)
- **THEN** se produce `main.pdf` sin errores fatales
- **AND** el registro no contiene referencias indefinidas ni etiquetas definidas mas de una vez
