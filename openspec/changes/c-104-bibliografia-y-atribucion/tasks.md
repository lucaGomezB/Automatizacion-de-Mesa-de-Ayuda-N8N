# Tasks — c-104 — Bibliografía y atribución (item 14 + verificación B1-B3)

> Governance MEDIO/ALTO (ver `design.md`, D4). c-104 es `.bib`-only salvo que la
> verificación B1-B3 detecte una regresión. Se aplica en secuencia (D3). NO se
> editan `.tex` de prosa por este change.

## 0. Prerrequisitos (solo lectura)

- [x] 0.1 Confirmar con `openspec status --change c-104-bibliografia-y-atribucion --json` que proposal/design/specs están presentes, y que el árbol está limpio (`git status`).
- [x] 0.2 Registrar la línea base: contar entradas del `.bib` (`grep -cE '^@'`) — esperado 48 — y el conteo de páginas de partida (`main.pdf` = 103).
- [x] 0.3 Registrar el estado real del item 14: `grep -nE '^@(article|book)\{(Touvron2023_llama2|Jurafsky2023_speech_language)' "docs/Tesis/v9 (IA)/Bibliography_base.bib"`.

## 1. Item 14 — tipado de las entradas (D1)

- [x] 1.1 Retipar `Touvron2023_llama2` de `@article` a `@misc`: eliminar `journal = {arXiv preprint}`; agregar `howpublished = {arXiv preprint}`, `eprint = {2307.09288}`, `archivePrefix = {arXiv}`, `primaryClass = {cs.CL}`; conservar `author`, `title`, `year` y `doi = {10.48550/arXiv.2307.09288}`.
- [x] 1.2 Retipar `Jurafsky2023_speech_language` de `@book` a `@unpublished`; conservar `author`, `title` y `year`, y declarar el estado (Stanford University, borrador de la 3ra edicion) en `note`/`publisher`.
- [x] 1.3 Verificar que NO se alteró la autoría, el año, el título ni el DOI de ninguna entrada: `git diff --stat` acotado a las dos entradas y `grep -cE '^@'` sigue en 48.

## 2. Verificación B1-B3 (sin regresión) (D2)

- [x] 2.1 B1: `grep -rn "BERT\|91" "docs/Tesis/v9 (IA)/paper/sections/03-estado-del-arte.tex" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"` no atribuye BERT ni ~91 % a Revina; la clave citada es `Revina2020_it_tickets`.
- [x] 2.2 B2: confirmar las 12 claves 2023-2026 (`ahuja2023mega`, `lai2023okapi`, `zhang2023multilingual`, `xuan2025mmluprox`, `grandury2025laleaderboard`, `mayorrocher2026spanish`, `bernalbeltran2025mexicanspanish`, `ramonferrer2026tripletotext`, `paket2024itservice`, `liu2025tickit`, `zangari2023ticket`, `colavito2025benchmarking`) presentes en el `.bib`.
- [x] 2.3 B3: `Landis1977_kappa` presente (DOI 10.2307/2529310); `Stallings2017_computer_security` con Lawrie Brown; `OGC2011_itil` sin `edition = {2011}`; `04-marco-metodologico.tex` atribuye los rangos de Kappa a Landis & Koch y rotula `κ = 0,87` como "casi perfecto".
- [x] 2.4 Higiene de citas: correr el verificador de citas (`verify_citations.py` o el comando equivalente del repo) y registrar `orphan = 0`, `unused = 0`.
- [x] 2.5 Guardia de fabricadas: `grep -rn "Karchhud2024\|Mehdi2023" "docs/Tesis/v9 (IA)"` devuelve cero coincidencias en `.bib` y `.tex`.
- [x] 2.6 Registrar el resultado en este archivo. Si 2.1-2.5 revelan una regresión, abrir una tarea de corrección `.tex` SERIALIZADA según `design.md` D3 antes de cerrar.

## 3. Verificación de compilación (D5)

- [x] 3.1 Compilar con la imagen Docker: `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`.
- [x] 3.2 Verificar el log: cero "undefined reference" y cero "multiply defined label".
- [x] 3.3 Registrar `pdfinfo main.pdf | grep Pages` (base 103) y confirmar en el bloque de referencias que `Touvron2023_llama2` no se presenta como revista ni `Jurafsky2023_speech_language` como libro publicado.

## 4. Verificación global

- [x] 4.1 Ejecutar `openspec validate c-104-bibliografia-y-atribucion --strict` y confirmar que pasa.
- [x] 4.2 Confirmar que NO se tocaron los archivos de otras ramas (números canónicos, tildes, portada, figuras) ni se agregaron entradas bibliográficas nuevas.

## Resultados de verificación (2026-10-21)

- **0.2 / 1.3** — `grep -cE '^@'` = 48 (sin cambios; no se agregaron ni retiraron entradas).
- **2.1 B1** — `grep -in "bert"` en `03`/`08` solo coincide con la palabra "cobertura" (falso positivo); `grep -nw "BERT"` y `grep -n "91"` no devuelven coincidencias. Revina se cita en `03:28`, `08:28`, `08:30`, `08:32` sin BERT ni ~91 %. PASS.
- **2.2 B2** — las 12 claves 2023-2026 presentes en el `.bib` (1 cada una). PASS.
- **2.3 B3** — `Landis1977_kappa` con DOI `10.2307/2529310`; `Stallings2017_computer_security` con `Brown, Lawrie`; `OGC2011_itil` sin `edition = {2011}`; `04-marco-metodologico.tex` (líneas 55 y 87) atribuye los rangos a Landis & Koch y rotula `κ = 0,87` como "casi perfecto". PASS.
- **2.4 Higiene de citas** — `python3 verify_citations.py`: 48 entradas <-> 48 claves citadas, orphan = 0, unused = 0, STATUS PASS.
- **2.5 Guardia de fabricadas** — `grep -rn "Karchhud2024\|Mehdi2023"` en `docs/Tesis/v9 (IA)`: cero coincidencias. PASS.
- **3.1-3.3 Compilación** — Docker `texlive-thesis`, `latexmk main.tex`: 103 páginas; `main.log` sin "undefined" ni "multiply defined"; biber sin warnings. `Touvron2023_llama2` renderiza como preprint (`.bbl` tipo `misc`; salida: "... (2023). Llama 2: Open Foundation and Fine-Tuned Chat Models [arXiv:2307.09288]. https://doi.org/..."); `Jurafsky2023_speech_language` renderiza como borrador no publicado (`.bbl` tipo `unpublished`; salida: "... (2023). Speech and Language Processing: ... [Borrador de la 3ra edicion, disponible en el sitio de los autores]."). PASS.
- **4.1** — `openspec validate c-104-bibliografia-y-atribucion --strict` = "Change ... is valid".
- **4.2** — `git status --porcelain`: solo `Bibliography_base.bib` y sus artefactos de build (`main.aux`, `main.bbl`, `main.blg`, `main.pdf`); ningún `.tex` tocado.
- **Regresión B1-B3**: ninguna. No se editó ningún `.tex`.
