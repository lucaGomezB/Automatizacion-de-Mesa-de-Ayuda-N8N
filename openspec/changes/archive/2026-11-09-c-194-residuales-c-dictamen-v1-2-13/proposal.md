# Proposal: Atender los residuales C1 y C2 del dictamen CONEAU sobre v1.2.13

## Why

El dictamen CONEAU del 2026-11-09 sobre `v1.2.13` dejo tres residuales de forma y bibliografia
sin cerrar tras `v1.2.15`: la fila "Lim." del Anexo I como secuencia temporal (C1), la nota de
`Zendesk2026_help_desk` (C2) y la atribucion a Zanzotto en 2.4 (C1). No cambian cifras ni
resultados; la release `v1.2.16` los cierra y alinea la version entregada.

## What Changes

- **Fila "Lim." del Anexo I (`12-anexos.tex`)**: secuencia temporal explicita ---primero
  `c-169` resolvio dos de los cinco limites y dejo sin concluir la intervencion humana; despues
  `c-190` la refuto y corrigio la exactitud laxa---; el efecto de orden no se resolvio y la
  validacion fuera de muestra queda como limitacion negativa. La columna Change pasa a
  `\texttt{c-169}, \texttt{c-190}`; se conservan los `\autoref`, sin numeros de linea ni
  altura neta.
- **Nota de Zendesk (`Bibliography_base.bib`)**: describe la pagina de producto de software de
  servicio al cliente; se retira "precios" y se conservan autor, titulo, URL y `urldate`.
- **Zanzotto (`02-marco-teorico.tex`, 2.4)**: la oracion se parte en dos; la primera queda como
  inferencia de los autores (rol activo ante la ambiguedad semantica y responsabilidad de la
  decision); la segunda atribuye a `\textcite{Zanzotto2019_human_in_the_loop}` el paradigma
  HitAI (retribuir a quienes producen el conocimiento y sostener la supervision humana). Sin
  cambio de significado.
- **Consistencia de version**: la configuracion entregada pasa de `v1.2.15` a `v1.2.16` en
  `05-arquitectura.tex`, `06-implementacion.tex`, `11-aspectos-legales.tex` y `12-anexos.tex`;
  las dos referencias historicas al dictamen sobre `v1.2.12` quedan intactas.
- **Registro y release**: seccion c-194, FASE 59, regeneracion de `tesis_para_agente.md` y
  `compilacion.md`, y release `v1.2.16` con el patron de hash del Anexo B de c-188.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: requisitos sobre la secuencia temporal de la fila "Lim.", la
  consistencia de version entregada, la etiqueta de `v1.2.16` y su neutralidad de paginas; se
  modifican los de fidelidad bibliografica y trazabilidad del dictamen del 9-11 para cubrir C1
  y C2.

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/` (`12-anexos.tex`, `02-marco-teorico.tex`,
  `05-arquitectura.tex`, `06-implementacion.tex`, `11-aspectos-legales.tex`) y
  `Bibliography_base.bib`.
- `dictamen-correcciones.md`, `CHANGES.md`, `tesis_para_agente.md` y `compilacion.md`; tag
  anotado `v1.2.16` y commit posterior del hash.
- Gobernanza: MEDIUM (prosa y bibliografia; sin datos personales ni codigo).

## Rollback Plan

Revertir las fuentes y el registro al commit previo; no hay codigo ni datos que revertir.

## Success Criteria

- [ ] `openspec validate c-194-residuales-c-dictamen-v1-2-13 --strict --no-interactive` pasa.
- [ ] La fila "Lim." declara la secuencia temporal y su columna Change es `c-169`, `c-190`.
- [ ] La nota de Zendesk no contiene "precios"; Zanzotto son dos oraciones con atribucion
  correcta.
- [ ] El PDF de `v1.2.16` no supera 118 paginas ni imprime el hash de una release previa.
