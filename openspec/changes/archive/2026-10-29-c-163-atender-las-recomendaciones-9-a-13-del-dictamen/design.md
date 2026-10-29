## Context

Change docs-only sobre la tesis v10 (`docs/Tesis/v10 (IA)/`). Ver `proposal.md` para la motivacion. Restricciones que condicionan el enfoque:

- El cuerpo de la tesis esta en el tope de 100 paginas (total 111); casi todas las correcciones son de forma y MUST NOT introducir contenido cientifico nuevo.
- La fuente de verdad de la version de trabajo es `docs/Tesis/v10 (IA)/paper/`; `docs/Tesis/v9 (IA)/` esta congelada.
- El toolchain de compilacion y de figuras ya existe en el repositorio (`texlive-thesis` en Docker, `mmdc` para Mermaid); las fuentes Mermaid de las figuras viven en `docs/diagrams/`.
- Las recomendaciones 9-13 y el inventario del dictamen del 28-10-2026 fijan la ubicacion exacta (`archivo:linea`) de cada correccion.
- Los changes c-158 a c-162 ya atendieron A1-A4, 5-8, Q1-Q8, Nginx y el contacto del reportante; este change no los re-edita.

## Goals / Non-Goals

**Goals:**

- Atender las recomendaciones 9 a 13 y las filas pertinentes del inventario del dictamen.
- Mantener la tesis compilando sin referencias indefinidas ni etiquetas duplicadas, con `verify_citations.py` en PASS.
- Preservar numeros canonicos, las cinco cadenas de categoria y el tope de paginas.
- Dejar declarado, para cada figura no regenerable, el motivo, sin erratas residuales.

**Non-Goals:**

- No agregar mediciones de campo ni recalcular resultados.
- No tocar `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml` ni `docs/Tesis/v9 (IA)/`.
- No reescribir las correcciones de c-158 a c-162.
- No cambiar el estilo de cita global a un formato distinto de APA 7.

## Decisions

- **D1. Una sola capability (`tesis-document`) con delta ADDED + MODIFIED.** Todas las correcciones son criterios de calidad del documento. Alternativa: abrir una capability nueva por rec; descartada porque fragmenta el contrato ya existente.
- **D2. MODIFIED solo donde hay conflicto normativo con el spec vigente.** Se modifican **dos** requirements: la hipotesis nula de Wilcoxon (contradice "medianas") y la densidad de citas (contradice "no introducir referencias nuevas"). El resto se expresa como ADDED para no duplicar bloques ni escenarios. La fecha de portada NO se modifica: por decision del autor (OQ-1 = B, 2026-10-29) se difiere hasta contar con la fecha de entrega firme, de modo que `00-portada.tex` no se toca en este change. Alternativa: MODIFIED para todo; descartada por bloat del delta.
- **D3. Preferir ADDED para correcciones sin conflicto.** Glosario, figuras y forma ya estan cubiertos por requirements genericos vigentes (p. ej. "Glosario de siglas y acronimos", "Correccion de defectos residuales de forma"), por lo que su correccion es implementacion de esos requirements y no necesita delta propio.
- **D4. Regenerar figuras desde Mermaid en `docs/diagrams/`.** Se regeneran las Figuras 2, 3, 8, 9 y 11 con `mmdc` dentro del toolchain existente. Si una figura no se puede regenerar fielmente, se declara en el registro y se corrige la errata de forma manual como minimo.
- **D5. Fecha de portada: DIFERIDA (OQ-1 = B).** El autor decidio (2026-10-29) no fijar aun la fecha de entrega; `00-portada.tex` conserva `\today` y este change NO lo modifica. La correccion queda como item abierto a atender cuando la fecha de entrega sea firme (idealmente antes de finales de noviembre de 2026). No requiere delta de spec: el requirement de portada del spec vigente no se toca.
- **D6. Registro central.** Cada correccion y su verificacion se consignan en `docs/Tesis/Correcciones/dictamen-correcciones.md`; la FASE 50 se abre en `CHANGES.md`.
- **D7. Redaccion en el lugar.** Las adiciones de texto se redactan para no empujar el cuerpo por encima del tope; se mide el delta de paginas y, si hace falta, se aplican palancas de forma (indices, espaciado).

## Risks / Trade-offs

- [El crecimiento bibliografico por las fuentes primarias empuja el cuerpo sobre el tope] -> Medir el delta de paginas; las entradas van a la bibliografia (fuera del cuerpo); compensar con palancas de forma si el inicio de "Referencias" se corre de pagina.
- [Una figura no se regenera fielmente con el toolchain] -> Declararla en el registro y corregir la errata manualmente como minimo; no dejar la errata.
- [La rec 10 toca material legal sensible] -> Governance MEDIUM: cambios acotados a la terminologia y a los plazos verificables contra la ley; sin interpretacion juridica nueva.
- [Efecto en la compilacion por nuevas citas] -> Recompilar y correr `verify_citations.py`; el delta de citas debe seguir en cero huerfanas y cero entradas sin usar.

## Open Questions

- **OQ-1 (fecha de entrega) — RESUELTA (opcion B, 2026-10-29).** El autor no fija la fecha de entrega todavia; `00-portada.tex` queda con `\today` y la correccion se difiere. No cambia el approach, los specs ni el desglose de tareas (la tarea de portada queda diferida).
- **OQ-2 (figuras regenerables) — CONFIRMADA (2026-10-29).** Las figuras con erratas se regeneran desde su fuente (Mermaid para la Figura 3 `despliegue.md` y la Figura 11 `flujo_n8n.md`; `scripts/figures/boxplot_tiempos.py` y `scripts/figures/matriz_confusion.py` para las Figuras 8 y 9); la Figura 2 ya la regenero c-159. Si alguna no se regenera fielmente, se declara explicitamente en el registro. No cambia el approach.
