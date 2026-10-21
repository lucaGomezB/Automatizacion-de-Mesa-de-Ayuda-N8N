# Proposal: c-104 — Bibliografía y atribución (item 14 + verificación B1-B3)

## Why

El dictamen CONEAU (2026-10-20), en su §9, deja una observación abierta de la
dimensión bibliográfica: el tipado de las entradas `Touvron2023_llama2` (declarada
`@article` con `journal = {arXiv preprint}`, que biblatex/APA renderiza como si
fuera una publicación periódica) y `Jurafsky2023_speech_language` (declarada
`@book`, siendo un borrador no publicado). Las correcciones B1 (misatribución de
Revina, Buza & Meister 2020), B2 (modernización 2023-2026) y B3 (higiene de
metadatos) ya fueron aplicadas por el change c-78 (archivado 2026-10-20), pero no
se re-verificaron después de las ramas que tocaron los sitios de cita (c-92..c-96,
c-102, c-103, c-107). c-104 cierra el item 14 y re-verifica B1-B3 sin duplicar la
modernización bibliográfica.

## What Changes

- **Item 14 — tipado de entradas (BREAKING formal, no de contenido)**:
  retipar `Touvron2023_llama2` como preprint de arXiv (`@misc`/`@online` con
  `eprint`, `archivePrefix`, `primaryClass`, `howpublished` y `doi`) para que no se
  renderice "arXiv preprint" como revista; retipar `Jurafsky2023_speech_language`
  como borrador no publicado (`@misc`/`@unpublished`), conservando `publisher` y
  `note` correctos (Stanford University, borrador de la 3ra edición).
- **Verificación B1-B3 (sin regresión)**: confirmar por comando que Revina et al.
  (2020) sigue sin BERT ni ~91 %; que el `.bib` conserva al menos 12 artículos
  arbitrados 2023-2026; que los rangos de Kappa se atribuyen a Landis & Koch
  (1977) y `κ = 0,87` se rotula "casi perfecto"; que hay cero citas huérfanas y
  cero entradas sin usar; y que las 48 entradas resuelven por DOI o landing.
- Sin cambios de contenido científico. No se agregan ni retiran entradas: solo se
  retipan dos.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: endurece el requisito "Higiene de metadatos bibliográficos"
  con el tipado correcto de fuentes preprint/borrador (item 14) y agrega un
  requisito de verificación de integridad y atribución bibliográfica (B1-B3).

## Impact

- `docs/Tesis/v9 (IA)/Bibliography_base.bib` (2 entradas: solo `@type` y campos de
  tipo; sin alterar autoría, año ni título).
- `docs/Tesis/v9 (IA)/paper/sections/` solo si la verificación B1-B3 detecta una
  regresión (sitios de cita en `02`, `03`, `04`, `08`).
- Recompilación con la imagen Docker `texlive-thesis`; se espera 103 páginas y 0
  referencias indefinidas.
- Secuencia: comparte los archivos `.tex` de la tesis con c-105/c-106/c-107 y las
  ramas siguientes (c-108/c-109/c-110); se aplica en el orden declarado en
  `design.md`.
