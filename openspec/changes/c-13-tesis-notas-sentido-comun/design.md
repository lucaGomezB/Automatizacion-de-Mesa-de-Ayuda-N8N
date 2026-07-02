## Context

The thesis document (`docs/Tesis/v8 (IA)/paper/`) uses 11 LaTeX section files compiled via XeLaTeX with APA 7th citations. Chapters 8 (Discussion) and 10 (Recommendations) are the insertion points. The three notes come from practitioner fieldwork observations about real-world help desk operations -- they are qualitative, not empirical. This change adds ~4 paragraphs total across two files with zero deletions and zero new references.

**Existing state**: 
- `08-discusion.tex` -- 52 lines. Section 8.4 has 3 paragraphs (practical benefits, traceability, economic analysis).
- `10-recomendaciones.tex` -- 32 lines. Six subsections (10.1 through 10.6).

**Constraints**:
- NO fabricated references. Frame all claims as author observation ("se observa que...", "la experiencia sugiere que..."), not as literature-backed claims.
- NO changes to empirical results, objectives, or hypothesis.
- Academic Spanish, formal impersonal tone (no "nosotros", no colloquialisms).
- Additive only -- preserve all existing content.
- UTF-8 encoding (direct accents: á, é, í, ó, ú, ñ).

## Goals / Non-Goals

**Goals:**
1. Add one paragraph about gradual change management to Section 8.4 (Discussion > Practical implications).
2. Expand Section 10.3 (Future Work > Monitoring dashboard) with one paragraph about organizational analytics.
3. Add new subsection 10.7 (Future Work > Knowledge base for self-service resolution).

**Non-Goals:**
- Note 1 (human escalation) -- already covered, no action.
- Any change to empirical results (F1 scores, time measurements, percentages).
- Any new citations or bibliography entries.
- Any deletion or rewriting of existing paragraphs.

## Decisions

### D1: Placement of Note 2 -- after economic paragraph in 8.4

**Decision**: Insert the gradual change management paragraph as the fourth paragraph of section 8.4, after the economic analysis paragraph (line 46) and before the `\subsection{Reflexiones sobre la generalizacion}` heading (line 48).

**Rationale**: The section flows from practical benefits → traceability → economics → adoption challenges. Adding the sociotechnical dimension at the end of "Implicancias practicas" provides a realistic closing note before transitioning to generalizability. The economic analysis quantifies ROI; the new paragraph qualifies that ROI is contingent on organizational adoption.

**Exact insertion point**: After line 46 (`...28 USD, un valor marginal frente a las 180 horas-persona liberadas.`) and before the blank line at line 47, followed by the new paragraph.

### D2: Content of Note 2 -- frame as practitioner knowledge

**Decision**: Frame as experiential observation, not literature-backed claim. Avoid phrases like "la literatura documenta" or "estudios muestran" -- use "la experiencia en entornos de mesa de ayuda sugiere" and "se observa que".

**Prose draft**:
```
Un aspecto que excede el alcance tecnico del sistema, pero condiciona su efectividad real, es la dimension sociocultural de la adopcion organizacional. La experiencia en entornos de mesa de ayuda indica que los empleados con mayor antiguedad en la organizacion suelen presentar resistencia al cambio de procesos. Esta resistencia no obedece a limitaciones tecnicas sino a la familiaridad con los procedimientos existentes y a la percepcion de que un nuevo sistema puede resultar complejo o invasivo. En consecuencia, la implementacion de una solucion como la propuesta se beneficia de una estrategia de despliegue gradual: comenzar con un grupo piloto reducido, extender progresivamente el alcance a sectores adicionales y acompanar cada etapa con instancias de capacitacion breves y contextualizadas. Un enfoque incremental reduce la friccion inicial, permite ajustar el sistema a las particularidades de cada sector y facilita la construccion de confianza en la herramienta por parte de los usuarios, condicion necesaria para que los beneficios tecnicos cuantificados en este trabajo se traduzcan en mejoras organizacionales efectivas.
```

### D3: Placement of Note 3 -- second paragraph in 10.3

**Decision**: Add a second paragraph to the existing 10.3 section, after the current single paragraph (line 18). The current paragraph covers system health monitoring; the new paragraph extends to organizational analytics.

**Rationale**: The section title "Panel de monitoreo en tiempo real" accommodates both meanings: monitoring the system AND monitoring the organization through the system's data. Adding as a second paragraph keeps the logical flow: first paragraph = system observability, second paragraph = business intelligence derived from that same data.

**Exact insertion point**: After line 18 (...puntos de datos necesarios para instrumentar esta capa de observabilidad.) and before the blank line at line 19.

### D4: Content of Note 3 -- ETL + analytics framing

**Prose draft**:
```
Mas alla del monitoreo operativo del sistema, los datos acumulados de incidentes constituyen una fuente de inteligencia organizacional cuyo valor excede el alcance inmediato de la mesa de ayuda. El registro sistematico de cada incidente ---incluyendo tipo, sector de destino, tiempo de resolucion y decision del clasificador--- habilita la construccion de tuberias ETL (\emph{Extract, Transform, Load}) que alimenten procesos de analisis de datos orientados a la mejora organizacional. A partir de estos datos es posible identificar patrones recurrentes de fallas, detectar areas organizacionales con mayor demanda de soporte, cuantificar el impacto de cambios en la infraestructura o en los procesos internos, y generar indicadores trimestrales que orienten decisiones de inversion en capacitacion o en renovacion de equipamiento. La exposicion de estos analisis mediante paneles orientados al nivel directivo ---complementarios del panel de monitoreo tecnico descrito previamente--- transforma la mesa de ayuda de un centro de costo operativo en un nodo de informacion estrategica para la organizacion.
```

### D5: Placement of Note 4 -- new subsection 10.7

**Decision**: Add a new `\subsection{Base de conocimientos para resolucion automatica}` as the seventh subsection of Chapter 10, after 10.6 and before `\newpage`. This is a natural extension: the thesis builds classification/routing capability; self-service resolution is the logical next step on that foundation.

**Rationale**: The thesis's arc in Chapter 10 moves from incremental improvements (10.1-10.4) to broader research (10.5-10.6). Self-service resolution is a forward-looking feature that connects to active learning (10.4 -- resolved cases feed the KB) and open-source LLMs (10.6 -- local models could power KB-driven responses). Placing it last positions it as an aspirational goal synthesizing earlier threads.

**Exact insertion point**: After line 31 (end of 10.6) and before `\newpage` at line 32.

### D6: Content of Note 4 -- KB for self-service resolution

**Prose draft** (3 paragraphs):
```
\subsection{Base de conocimientos para resolucion automatica}

El sistema propuesto en este trabajo se concentra en la clasificacion y derivacion de incidentes hacia los sectores responsables, pero no aborda la resolucion automatica de aquellos casos que admiten soluciones estandarizadas. Se recomienda, como linea de trabajo futuro, la incorporacion de una base de conocimientos que permita al sistema no solo categorizar el incidente sino tambien proponer ---o incluso ejecutar--- una resolucion cuando el problema detectado coincida con patrones documentados.

La base de conocimientos operaria como un repositorio estructurado de soluciones verificadas, organizado por tipo de incidente, sintoma y sector responsable. Ante un nuevo incidente, el sistema consultaria la base tras la clasificacion inicial y, en caso de hallar una coincidencia de alta confianza, ofreceria al usuario una respuesta clara y concisa con los pasos necesarios para resolver el problema sin intervencion del personal tecnico. Este mecanismo de autoservicio reduciria la carga sobre los sectores de soporte al absorber los casos simples y repetitivos ---como reinicios de sesion, restablecimiento de contrasenas o configuraciones basicas de correo electronico--- que actualmente representan una fraccion no despreciable del volumen de incidentes en organizaciones medianas.

La construccion de esta base de conocimientos puede articularse con el mecanismo de aprendizaje activo descrito en la Seccion~10.4: cada caso resuelto por un operador humano y validado como correcto constituye un candidato para ser incorporado a la base, previa curacion editorial que garantice la claridad y la precision de las instrucciones. La viabilidad tecnica de este enfoque se ve reforzada por la creciente capacidad de los modelos de lenguaje para generar respuestas estructuradas a partir de documentacion tecnica, linea de investigacion que conecta naturalmente con la evaluacion de modelos de codigo abierto propuesta en la Seccion~10.6.
```

## Risks / Trade-offs

- **Risk**: New paragraphs may disrupt the existing text flow or feel tacked on.
  - **Mitigation**: Each insertion is at a natural seam (end of section, end of paragraph). Prose is drafted to match the existing academic tone and vocabulary of the surrounding text.

- **Risk**: Gradual change management paragraph may sound like it's citing literature when it isn't.
  - **Mitigation**: Explicitly use experiential framing ("la experiencia... indica", "se observa que"). Avoid any phrase that implies external sourcing.

- **Risk**: Note 4 may imply capabilities (KB-driven resolution) that the thesis didn't build or evaluate.
  - **Mitigation**: Section is explicitly under "Recomendaciones y lineas de trabajo futuro" -- the whole chapter describes what COULD be done, not what WAS done. The conditional tense ("operaria", "ofreceria", "reduciria") makes this clear.

- **Risk**: "Tuberias ETL" in Note 3 may introduce technical jargon inconsistent with the thesis's level of abstraction.
  - **Mitigation**: The thesis already uses terms like "endpoints de salud", "Prometheus", "Grafana", and "active learning" -- ETL is at the same level. The term is defined inline (`\emph{Extract, Transform, Load}`).
