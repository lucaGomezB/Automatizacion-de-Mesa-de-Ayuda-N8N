## ADDED Requirements

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
