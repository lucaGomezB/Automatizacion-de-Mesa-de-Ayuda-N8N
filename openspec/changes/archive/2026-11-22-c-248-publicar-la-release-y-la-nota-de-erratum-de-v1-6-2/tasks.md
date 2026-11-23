# Tasks: Publicar la release siguiente a v1.6.2 y la nota de erratum

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`. Requisito nuevo: `TD` = `tesis-document`
(«Nota de erratum de una release con PDF de tag de hash ajeno», «Verificacion de flotantes en la release»).

**Gobernanza HIGH**: toca el ejemplar defendido y publica un tag. Ningun `.tex` del ejemplar ni ningun
tag se escribe o crea sin OK expreso de los autores. No se toca `App/`, `n8n/`, `evaluation/`, `data/`
ni el corpus. `v1.6.2` no se mueve, borra ni reapunta. El merge a `main` se hace con **merge commit**,
nunca squash ni rebase. El change de release NO reescribe el contenido (lo cerro c-247).

## 0. Precondiciones y linea base

- [x] 0.1 Leer la instruccion de release de c-247 (`docs/Tesis/Correcciones/dictamen-correcciones.md`,
  tarea 8.1) y el design (D1 a D6). **OQ-1/2/3 resueltas (2026-11-22).** Verificacion:
  `v1.6.3`; merge y copia de entrega en este change; erratum solo en `dictamen-correcciones.md`.
- [x] 0.2 **Linea base**: `git status` limpio, `git rev-parse HEAD`, `git describe --tags`,
  `git rev-parse v1.6.2^{commit}` = `e7013127b565faa8f67a75284756cd4abe5c148f`. (TD)
- [x] 0.3 **Red de seguridad**: `python "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS;
  `openspec validate --all --strict` = 0 fallos; `sha256sum data/corpus_evaluacion_pseudonimizado.json`
  = `1fd17d7e a90d418b b060b57b c3a645fa a4a753c7 c0c26424 c06c58d8 84dac5cb`.
- [x] 0.4 Confirmar que el host **no** tiene LaTeX: la compilacion se hace por Docker (`texlive-thesis`,
  `latexmk main.tex`).

## 1. Bump de version y fecha de portada

- [x] 1.1 `S/00-portada.tex`: reemplazar el marcador `[FECHA PENDIENTE]` por la **fecha de la release** y
  la version `v1.6.3`. Verificacion: `rg -n "FECHA PENDIENTE" S/00-portada.tex` sin coincidencias.
- [x] 1.2 Propagar la version a `README.md`, el Anexo B (`S/12-anexos.tex`, `sec:anexo-repositorio`),
  `knowledge-base/` e `inventario-uso-asistentes-ia.md`. Verificacion: `rg` de `v1.6.2` -> `v1.6.3`
  salvo los registros historicos de releases previas.
- [x] 1.3 Actualizar el conteo de commits del Anexo I.3 al de la referencia de la entrega `v1.6.3`
  (como en las releases previas: se recomputa sobre la ref de la entrega). Verificacion: el conteo
  coincide con `git rev-list --count <ref>`.

## 2. Anexo B sin hash (C3) y nota de erratum

- [x] 2.1 `S/12-anexos.tex` (`sec:anexo-repositorio`): para la release `v1.6.3`, el Anexo B **no imprime
  ningun hash**; remite al tag y a `compilacion.md`. Verificacion: el Anexo B no imprime un hash de
  commit (evita el defecto de `v1.6.2`). (TD)
- [x] 2.2 `docs/Tesis/Correcciones/dictamen-correcciones.md`: **consolidar la nota de erratum de
  `v1.6.2`** (texto de la instruccion de c-247 8.1: identifica `17aa6d21` impreso y `e7013127` del
  commit de contenido; el tag no se mueve). Verificacion: la nota existe y el tag `v1.6.2` sigue igual. (TD)
- [x] 2.3 **[OQ-3]** **Resuelta**: la nota de erratum va **solo en `dictamen-correcciones.md`**, no en el Anexo I. (TD)

## 3. Recompilacion (C3) y derivados

- [x] 3.1 Recompilar la tesis (Docker `texlive-thesis`, `latexmk main.tex`). Verificacion: `main.pdf`
  generado, 0 errores fatales, 0 referencias/citas indefinidas, biber sin advertencias.
- [x] 3.2 Regenerar `docs/Tesis/v10 (IA)/paper/compilacion.md`
  (`docs/Tesis/Correcciones/resumir_registro_compilacion.py`). Verificacion: nombra el commit compilado. (TD)
- [x] 3.3 Regenerar los derivados (`tesis_para_evaluacion.txt`, `tesis_*.txt`) y la copia de entrega
  `docs/Tesis/tesis_ultima_version.pdf` con los metodos de registro. Verificacion: coinciden con el PDF.

## 4. Verificacion

- [x] 4.1 **Flotantes**: verificar que cada figura y tabla quede dentro de su seccion/anexo y que ninguna
  desborde el margen; registrar el resultado. Verificacion: lista de desbordes vacia. (TD)
- [x] 4.2 Cifras canonicas intactas; `verify_citations.py` PASS; `openspec validate --all --strict` 0 fallos.
- [x] 4.3 Prosa del Resumen y del Abstract <= 250 palabras (regla de la spec `tesis-document`).

## 5. C3: commit y tag

- [x] 5.1 Commit **C3** (contenido + PDF recompilado, con el Anexo B sin hash). Verificacion: `HEAD` = C3.
- [x] 5.2 Tag anotado **`v1.6.3`** sobre C3. Verificacion: `git cat-file -t v1.6.3` devuelve `tag` y apunta
  a C3. (Gobernanza HIGH: OK expreso previo.)
- [x] 5.3 Publicar la rama y el tag en `origin`.

## 6. C4: consignar el hash

- [x] 6.1 Anexo B: consignar el **hash del commit de contenido C3** (coincidente con
  `git rev-parse v1.6.3^{commit}`) y registrarlo en `dictamen-correcciones.md`.
- [x] 6.2 Recompilar y actualizar derivados; commit **C4**; publicar en `origin`.
- [x] 6.3 Verificar que `v1.6.3` continua apuntando a C3 (C4 no mueve el tag) y que el PDF del arbol del
  tag imprime el hash correcto.

## 7. Cierre

- [x] 7.1 **Merge a `main`** con merge commit (nunca squash/rebase). Verificacion:
  `git merge-base --is-ancestor v1.6.3 origin/main` = verdadero y `v1.6.2` sigue siendo ancestro.
- [x] 7.2 Actualizar `docs/Tesis/tesis_ultima_version.pdf` y `README.md` a `v1.6.3`.
- [x] 7.3 `openspec validate --all --strict`; registrar la release en `CHANGES.md`; **archivar** el change.
