## Why

Three practical insights from real-world help desk operations -- identified during author fieldwork -- are absent from the thesis Discussion (Ch. 8) and Future Work (Ch. 10) chapters. These are qualitative, common-sense observations about organizational adoption, data-driven analytics, and self-service resolution. Integrating them adds practitioner depth to the thesis without altering any empirical claims or adding unverifiable references.

## What Changes

- **Note 2 -- Gradual change management**: Add one paragraph to section 8.4 "Implicancias practicas" (08-discusion.tex). Acknowledges that technical success depends on organizational adoption, and that gradual rollouts with targeted training help overcome resistance -- particularly among long-tenured employees. Positioned after the economic analysis paragraph.
- **Note 3 -- Organizational analytics**: Add one paragraph to section 10.3 "Panel de monitoreo en tiempo real" (10-recomendaciones.tex). Extends the concept from system health monitoring (Prometheus/Grafana) to business intelligence: ETL pipelines on accumulated incident data for trend analysis, recurring failure identification, and executive dashboards.
- **Note 4 -- Knowledge base for self-service**: Add a new subsection 10.7 (10-recomendaciones.tex). Proposes a knowledge base that enables the system to resolve simple incidents automatically (password resets, session restarts, email config) -- not just classify and route them. Connects to active learning (10.4) and open-source LLM evaluation (10.6).
- **Note 1 (human escalation) -- no action**: Already well-covered in section 8.1 (human in the loop at 9.5%).

## Capabilities

### New Capabilities

None. This change addresses the existing thesis document only.

### Modified Capabilities

- `tesis-document`: Adds 3 new requirements for qualitative content additions to Chapters 8 and 10. No existing requirements are modified or removed.

## Impact

- **Files modified**: 2 files in `docs/Tesis/v8 (IA)/paper/sections/`
  - `08-discusion.tex` -- add 1 paragraph to section 8.4 (after line 46, before line 48 blank line)
  - `10-recomendaciones.tex` -- add 1 paragraph to section 10.3 (after line 18) + new section 10.7 (after line 31)
- **Content preserved**: All existing paragraphs remain untouched. Only additions, no removals or alterations.
- **No new references**: All claims are framed as author observations or practical recommendations; no fabricated citations.
- **Compilation**: XeLaTeX + Biber cycle expected to succeed (additive changes only).
