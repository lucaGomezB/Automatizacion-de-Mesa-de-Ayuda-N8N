## Why

El dictamen CONEAU (2026-10-20, dimensión 4, segundo déficit) señala que, en la
subsección "Trabajos académicos previos sobre clasificación de tickets" de
`03-estado-del-arte.tex`, varios trabajos se agrupan en una sola oración con una
afirmación genérica, sin reportar corpus, métricas ni condiciones, lo que impide
juzgar su comparabilidad. La recomendación es convertir esos agrupamientos en una
tabla comparativa de trabajos académicos. Es la última recomendación del dictamen
sin cubrir.

## What Changes

- Agregar una tabla comparativa de trabajos académicos (`tab:trabajos-academicos`)
  en la subsección `subsec:trabajos-academicos`, que reemplaza la oración agrupada
  de la línea `03:32`.
- Columnas: `trabajo | enfoque | corpus/idioma | métrica reportada | condición`.
- Cada celda proviene de la prosa de la tesis y de `Bibliography_base.bib`; los
  datos faltantes se investigan para completarlos sin fabricar. Cuando un dato no
  puede establecerse, la celda se marca "no reportado en el alcance revisado"
  (regla acotada de c-110).
- Neutralidad de páginas: el total del PDF debe permanecer en <= 100 páginas; la
  tabla se compensa retirando redundancia en el mismo capítulo.
- Sin nuevas entradas `.bib` salvo que la fuente resuelva por DOI.
- Sin **BREAKING** changes. Sólo se edita `03-estado-del-arte.tex`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: se agregan requisitos de tabla comparativa de trabajos
  académicos de clasificación de tickets, de procedencia de datos y regla de dato
  no reportado, y de neutralidad de páginas al incorporar la tabla.

## Impact

- `docs/Tesis/v9 (IA)/paper/sections/03-estado-del-arte.tex` (único `.tex` editado).
- `main.pdf` recompilado: debe permanecer <= 100 páginas (compilación verifica más
  adelante con la imagen `texlive-thesis`).
- No se tocan `preambles/`, `main.tex`, `Bibliography_base.bib` (salvo DOI nuevo),
  el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`.
- Secuencia: debe aprobarse y aplicarse ANTES de `c-111` (versionado y tag).
