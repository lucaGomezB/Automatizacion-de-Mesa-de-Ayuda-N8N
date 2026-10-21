## Why

El dictamen CONEAU 2026-10-20 (dimensión 5, Marco teórico) observa que varios
conceptos rectores se enuncian por aserción sin fuente, que la atribución jurídica
de la "soberanía digital" a la Ley 25.326 es imprecisa, que la definición de
"alucinación" carece de cita canónica, que el eje de reconocimiento automático del
habla se desarrolla y luego se admite no utilizado, y que persiste el defecto de
redacción "trazabilidad auditiva" por "auditable". c-110 ya cubrió la subsección
human-in-the-loop y el protocolo de revisión de literatura; este change cierra los
déficits restantes del mismo apartado sin duplicarlo.

## What Changes

- `02-marco-teorico.tex` §2.3: fundamentar con cita verificable, o reformular como
  glosa propia, las definiciones de "automatización de procesos empresariales" (BPA)
  y de "plataformas de integración como servicio" (iPaaS).
- `02-marco-teorico.tex` §2.4: añadir una cita canónica a la definición de
  "alucinación".
- `02-marco-teorico.tex` §2.5: recortar el eje de reconocimiento automático del habla
  o justificar explícitamente su inclusión como marco del canal telefónico.
- `02-marco-teorico.tex` §2.3: corregir "trazabilidad auditiva" por "trazabilidad
  auditable".
- `01-introduccion.tex` §1.7: sustituir el "principio de soberanía digital promovido
  por la Ley 25.326" por la formulación jurídica exacta, sin atribuir a una ley de
  protección de datos un principio que no enuncia.
- `Bibliography_base.bib`: agregar de forma aditiva las entradas nuevas (alucinación
  y las que resulten de la fundamentación de BPA/iPaaS), verificadas por DOI. No se
  editan entradas existentes.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: se agregan requisitos sobre fundamentación de conceptos enunciados
  por aserción (BPA/iPaaS), cita canónica de la alucinación, formulación jurídica exacta
  de la soberanía sobre los datos, alcance justificado del eje de ASR y corrección del
  término "auditable".

## Impact

- `docs/Tesis/v9 (IA)/paper/sections/01-introduccion.tex`
- `docs/Tesis/v9 (IA)/paper/sections/02-marco-teorico.tex`
- `docs/Tesis/v9 (IA)/Bibliography_base.bib` (solo aditivo; compartido, se aplica en
  secuencia con los demás changes de tesis)
- Recompilación con la imagen Docker `texlive-thesis`; el presupuesto de páginas debe
  respetar el techo de 100 (c-116 ejecuta la reducción de páginas DESPUÉS, por lo que
  este change no debe introducir crecimiento neto de páginas).
- Sin cambios de código, API ni runtime.
- Governance: MEDIO/ALTO (texto académico y `.bib` compartido; el `.bib` es aditivo).
