# Proposal: c-103 — Portada formal y remisiones cruzadas (Gate 0)

## Why

La tesis v9 (103 páginas) abre las correcciones del dictamen CONEAU con dos
defectos de forma que bloquean toda edición posterior: (1) la portada no acredita
la identidad institucional —falta el logo UTN-FRM, el rótulo "Trabajo Final de
Carrera" y el segundo director—; (2) las remisiones cruzadas están escritas a mano
("Capítulo 7", "Sección 4.4") en lugar de resolverse con `\ref`, lo que ya produjo
un error real: la cota de 45 s remite a 4.4 cuando se enuncia en 4.6. Si las ramas
paralelas (c-104 bibliografía, c-105 reubicación del capítulo 11, c-106 tildes)
empiezan a mover secciones con remisiones duras, cada movimiento rompe referencias.
Este change es el **Gate 0 serial**: fija la identidad del documento y la
infraestructura de referencias ANTES de que las ramas toquen contenido.

## What Changes

- **Portada** (`sections/00-portada.tex`): insertar `assets/logo-utn-frm.png`
  (332×62 RGBA); rótulo "Trabajo Final de Carrera"; autores Luca Gomez, Carla
  Bustos, Gonzalo Sevilla; directores "Prof. Alberto Cortez y Prof. Ariel Enferrel"
  (orden indicado); fecha con `\today`. No agrega páginas: el PDF sigue en 103.
- **Metadatos** (`preambles/preamble.tex`): `pdfsubject` → "Trabajo Final —
  Tecnicatura Universitaria en Programación"; revisar `pdftitle`/`pdfauthor`/`pdfkeywords`.
- **Nomenclatura**: renombrar las 6 ocurrencias de "Tesis de Grado" y documentar la
  excepción de la ruta real `docs/Tesis/` (no se altera).
- **Referencias**: `\label` en cada `\section`/`\subsection`; convertir las 71
  remisiones duras a `\ref`/`\autoref`; corregir 07-resultados 4.4→4.6;
  estandarizar "Sección"; conservar `\documentclass{article}`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: agrega requisitos de identidad institucional de la portada,
  coherencia de metadatos PDF, nomenclatura "Trabajo Final" e integridad de
  referencias cruzadas (labels/refs, cero remisiones duras, cero referencias
  indefinidas, presupuesto de páginas preservado).

## Impact

- `docs/Tesis/v9 (IA)/paper/`: `main.tex`, `preambles/preamble.tex`, `sections/*.tex`
  (12 archivos), consume `assets/logo-utn-frm.png`.
- Cero cambios de contenido científico; cero tildes (c-106); no se toca
  `Bibliography_base.bib` (c-104).
- Habilita c-105 (mover el capítulo 11 sin romper referencias).

## Risks

- Migración masiva de referencias en un commit → verificar el log sin referencias
  indefinidas antes de cerrar.
- Logo de 332 px insuficiente para impresión a 300 dpi → no bloquea; se solicitará
  una versión ≥1200 px o vectorial.
- Conflicto con c-104/c-105 si introducen remisiones nuevas.

## Rollback

`git revert` del commit único del change restaura portada, preamble y secciones;
las remisiones duras vuelven con el archivo. Sin migraciones de datos ni estado externo.

## Success Criteria

- [ ] `openspec validate --strict` pasa.
- [ ] Cero remisiones duras y cero referencias indefinidas en el log de compilación.
- [ ] PDF en 103 páginas (±0).
- [ ] Portada con logo UTN-FRM y dos directores; metadatos PDF coherentes con "Trabajo Final".
