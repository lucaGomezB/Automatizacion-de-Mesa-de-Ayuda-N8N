# Proposal: Publicar la release siguiente a v1.6.2 y la nota de erratum

## Why

El dictamen CONEAU del 2026-11-20 sobre `v1.6.2` dejo una cuarta condicion de release: el PDF del arbol del tag imprime, en el Anexo B, el hash `17aa6d21` (del candidato previo) en lugar del hash del commit de contenido `e7013127`. El change c-247 (aplicado y archivado el 2026-11-22) respondio las tres aclaraciones de procedencia y, por la compuerta OQ-04, dejo la instruccion de release **opcion (A)**: `v1.6.2` queda inmutable y se registra como superada con una nota de erratum; la proxima release compila un PDF cuyo Anexo B **no imprime ningun hash** (remite al tag y a `compilacion.md`) y el commit siguiente consigna el hash. c-247 dejo ademas la portada con un marcador `[FECHA PENDIENTE]` y el cuerpo listo para recompilar. Falta ejecutar el tramo de release.

## What Changes

- **Recompilar** la tesis con el arbol de c-247 (Docker `texlive-thesis`, `latexmk main.tex`).
- **Version**: bump a **`v1.6.3`** (portada, `README.md`, Anexo B, knowledge-base, inventario I.3).
- **Fecha de portada** (hoy el marcador `[FECHA PENDIENTE]`).
- **Anexo B**: el PDF del commit de contenido (C3) no imprime hash; el commit C4 consigna el hash y recompila (patron C3/C4 vigente).
- **Nota de erratum de `v1.6.2`**: consolidar en `dictamen-correcciones.md` (ya registrada por c-247); no se reitera en el Anexo I.
- **Derivados**: regenerar `tesis_para_evaluacion.txt`, los extractos `tesis_*.txt` y `docs/Tesis/tesis_ultima_version.pdf`.
- **`compilacion.md`**: nombrar el commit compilado.
- **Verificacion de flotantes** en el PDF (tarea 6.6 de c-247).
- **Tag anotado `v1.6.3`** publicado en `origin` y **merge a `main`** con merge commit.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: se AGREGA el requisito de la **nota de erratum de una release cuyo PDF de tag imprime un hash ajeno** y la **verificacion de flotantes de release** (el patron C3/C4 se conserva).

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/main.pdf`, `compilacion.md` | Regenerado | PDF recompilado (sin hash en el Anexo B en C3) |
| `.../sections/00-portada.tex`, `12-anexos.tex`, `Bibliography_base.bib` | Modificado | Fecha, version `v1.6.3`, hash del Anexo B en C4 |
| `docs/Tesis/tesis_ultima_version.pdf`, `docs/Tesis/v10 (IA)/tesis_*.txt` | Regenerado | Copia de entrega y extractos |
| `README.md`, `knowledge-base/`, `inventario-uso-asistentes-ia.md` | Modificado | Propagacion de la version `v1.6.3` |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Nota de erratum de `v1.6.2` y registro del release |

Fuera de alcance: el contenido de la tesis (lo cerro c-247); `App/`, `n8n/`, `evaluation/` y el corpus; los changes detenidos (c-228, c-229, c-230, c-232).

**Gobernanza HIGH**: toca el ejemplar defendido y publica un tag; ningun `.tex` ni tag sin OK expreso de los autores.
