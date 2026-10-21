# Proposal: c-110 — Marco teórico (human-in-the-loop) y protocolo de revisión de literatura

## Why

El dictamen CONEAU 2026-10-20 (dimensiones 4 y 5; recomendaciones 11 y 12)
observa dos déficits de fundamentación. Primero, el estado del arte no declara
protocolo de revisión —bases consultadas, cadenas de búsqueda, criterios de
inclusión ni período—, de modo que la afirmación de vacancia ("no existe artículo
arbitrado 2023-2026 que evalúe Gemini sobre tickets en español") se usa dos veces
como motivación sin ser verificable. Segundo, "human-in-the-loop" (HITL) estructura
el resumen, las palabras clave y el aporte, pero nunca se define ni se fundamenta
en el marco teórico. Sin protocolo ni definición, la contribución descansa en una
declaración de inexistencia no acotada y en un término operativo sin respaldo.

## What Changes

- **Item 11 — protocolo de revisión.** Agregar en `03-estado-del-arte.tex` un
  párrafo de metodología de revisión (bases, cadenas, criterios de inclusión y
  exclusión, período y fecha de corte) y acotar la afirmación de vacancia a lo
  efectivamente buscado, con formulación relativa ("en las fuentes consultadas…").
- **Item 12 — HITL.** Agregar en `02-marco-teorico.tex` una subsección teórica
  sobre human-in-the-loop con definición, grados de autonomía y fuentes; ajustar
  el recuento de ejes del párrafo introductorio del capítulo y la mención del
  resumen si corresponde.
- **Bibliografía.** Incorporar de forma aditiva las entradas nuevas (HITL y
  protocolo) en `Bibliography_base.bib`, cada una verificada por DOI. No se editan
  las entradas existentes.
- **Compilación.** Recompilar la tesis con la imagen Docker `texlive-thesis` y
  registrar el conteo de páginas.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: se agregan tres requisitos (protocolo de revisión trazable,
  acotamiento verificable de la vacancia y subsección teórica de HITL con fuentes).

## Impact

- Texto de la tesis en `docs/Tesis/v9 (IA)/paper/sections/` (`02-marco-teorico.tex`,
  `03-estado-del-arte.tex`) y `docs/Tesis/v9 (IA)/Bibliography_base.bib`.
- Registro de la revisión (bitácora de búsqueda) bajo `docs/Tesis/Correcciones/`.
- No se toca código, API ni runtime. No se edita el memo canónico.
- Coordinación con `c-104-bibliografia-y-atribucion`: ambos tocan el `.bib`; c-110
  solo AGREGA entradas y se aplica DESPUÉS de c-104.
- Governance: ALTO. La vacancia es una afirmación de inexistencia que sostiene la
  contribución, y el `.bib` es compartido con c-104.
