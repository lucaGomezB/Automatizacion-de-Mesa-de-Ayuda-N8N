# Tasks — c-110 — Marco teórico (HITL) y protocolo de revisión de literatura

> Governance ALTO. Decisiones y reversibilidad en `design.md`. NO se editan los
> `.tex` fuera de `02-marco-teorico.tex` y `03-estado-del-arte.tex`, ni entradas
> del `.bib` fuera de las nuevas. Se aplica DESPUÉS de c-104.

> Modo de ejecución: Standard (Strict TDD no aplica — cambio documental, sin test
> runner para prosa/.bib; las compuertas son `verify_citations.py` y la compilación).

## 0. Prerrequisitos (solo lectura)

- [x] 0.1 Confirmar que `c-104-bibliografia-y-atribucion` está aplicado/archivado
  antes de tocar el `.bib`; si no, detener y aplicarlo primero (D7).
  — Confirmado: `openspec/changes/archive/2026-10-21-c-104-bibliografia-y-atribucion` existe.
- [x] 0.2 Registrar el conteo de páginas de partida (`main.pdf` = 103) y la fecha
  de verificación. — Baseline observado: `main.pdf` = **104** páginas
  (`pdfinfo`, 2026-10-21). Diferencia de +1 respecto de las 103 declaradas en el
  change; se usa 104 como referencia real.
- [x] 0.3 Confirmar con `git status` que el árbol está limpio antes de empezar.
  — `git status --porcelain` vacío al inicio.

## 1. Protocolo de revisión de literatura (ítem 11a, D3)

- [x] 1.1 `03-estado-del-arte.tex`: agregar el párrafo de metodología de revisión
  con bases (Scopus, IEEE Xplore, ACM DL, ACL Anthology, Google Scholar, arXiv),
  cadenas de búsqueda, criterios de inclusión/exclusión y período (2023-2026 para
  el estado del arte moderno). — Párrafo `\noindent\textbf{Protocolo de revisión.}`
  insertado tras el párrafo introductorio del capítulo (cadenas A1-A4 y B1).
- [x] 1.2 Crear la bitácora de búsqueda versionada en
  `docs/Tesis/Correcciones/` con una entrada por consulta (base, cadena, fecha,
  resultado) y la fecha de corte. — Creada
  `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md` (fecha de corte 21-10-2026).
- [x] 1.3 Verificar la consistencia texto–bitácora: cada base, cadena y criterio
  del texto existe en la bitácora y viceversa. — Bases {Scopus, IEEE Xplore, ACM
  DL, ACL Anthology, Google Scholar, arXiv} y cadenas {A1-A4, B1} coinciden en
  ambos artefactos; la bitácora define "resultado" y no registra consultas
  ausentes del texto.

## 2. Acotamiento de la vacancia (ítem 11b, D4)

- [x] 2.1 `03-estado-del-arte.tex` (afirmación de vacancia): reformular como
  relativa ("en las fuentes consultadas hasta la fecha de corte…"), citando bases,
  cadenas y fecha de corte; eliminar la inexistencia absoluta.
- [x] 2.2 `03-estado-del-arte.tex` (síntesis de la brecha, cierre del capítulo):
  alinear la mención reutilizada con el alcance declarado en 1.1. — Se agregó
  "en el alcance revisado en este capítulo y hasta la fecha de corte declarada".
- [x] 2.3 Verificar con búsqueda que no queda una formulación de vacancia sin
  acotar en el capítulo. — `grep -niI "no existe|inexistencia|hasta la fecha no|nunca se"`
  sobre `03-estado-del-arte.tex` → sin coincidencias.

## 3. Fuentes bibliográficas nuevas (D5)

- [x] 3.1 Agregar a `Bibliography_base.bib`, de forma aditiva, las entradas de
  HITL (Amershi 2019, Shneiderman 2020, Mosqueira-Rey 2023, Zanzotto 2019, Wu
  2022) con `author`, `title`, `year`, campo de publicación y `doi`, clave
  `ApellidoAnio_palabra_clave`. — 5 entradas nuevas; conteo `.bib` 48 → 53.
- [x] 3.2 Re-verificar cada DOI nuevo por Crossref o landing de editorial; retirar
  o reemplazar cualquier entrada que no resuelva. — Las 5 resuelven por Crossref
  (HTTP 200, metadatos coincidentes). Detalle en la bitácora.
- [x] 3.3 Confirmar que no se editó ninguna entrada existente ni de c-104. —
  `git diff` de `Bibliography_base.bib` muestra solo adiciones (bloque HITL).

## 4. Subsección teórica de human-in-the-loop (ítem 12, D2)

- [x] 4.1 `02-marco-teorico.tex`: insertar la subsección de HITL después de
  `subsec:automatizacion-orquestacion` con definición y grados de autonomía
  (revisión total, revisión selectiva por confianza, operación autónoma con
  auditoría). — `\subsection{Human-in-the-loop y grados de autonomía}\label{subsec:human-in-the-loop}`.
- [x] 4.2 Fundamentar cada aserción con `\textcite{}`/`\parencite{}` de las
  entradas de la Sección 3; aterrizar el concepto en el gate
  `requiere_revision_humana = (confianza < 0,70)`. — Citas a Mosqueira-Rey 2023,
  Zanzotto 2019, Amershi 2019, Shneiderman 2020 y Wu 2022; cierre sobre el gate.
- [x] 4.3 Actualizar el párrafo introductorio del capítulo: "siete ejes" ->
  "ocho ejes".
- [x] 4.4 Si el resumen o las palabras clave mencionan HITL, alinear la redacción
  con la definición incorporada (sin cifras nuevas). — No-op: las palabras clave
  ("human in the loop" / "Human-in-the-loop" en el resumen y el abstract) ya
  mencionan el término; la definición incorporada en 4.1 lo respalda y no se
  requieren cifras nuevas. `00-resumen.tex` queda fuera del conjunto de archivos
  editables de este change, por lo que no se modificó.

## 5. Verificación de integridad de citas (D6)

- [x] 5.1 Ejecutar
  `python "docs/Tesis/v9 (IA)/verify_citations.py"` y registrar la salida.
- [x] 5.2 Confirmar `0` citas huérfanas y `0` entradas sin usar tras agregar las
  entradas nuevas.
- [x] 5.3 Registrar la salida del script en `tasks.md` como evidencia. — Salida:
  `Found 53 bibliography entries.` / `Summary: 53 bib entries, 53 unique keys
  cited, 98 total citation commands` / `Orphan citations: 0` / `Unused entries: 0`
  / `STATUS: PASS`.

## 6. Compilación y verificación visual

- [x] 6.1 Compilar con la imagen Docker `texlive-thesis`:
  `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
- [x] 6.2 Confirmar `0` errores fatales y `0` referencias indefinidas en
  `main.log`. — `undefined: 0`, `multiply defined: 0`; sin "Rerun".
- [x] 6.3 Verificar en el PDF que la subsección de HITL y el protocolo de revisión
  se renderizan y que las citas nuevas aparecen. — Verificado con `pdftotext`:
  "2.4 Human-in-the-loop y grados de autonomía", "Protocolo de revisión", y
  referencias a Amershi, Shneiderman, Mosqueira-Rey, Zanzotto y Wu.
- [x] 6.4 Registrar el conteo de páginas final y aplicar la mitigación de D8 si
  creció de forma excesiva. — Final: **105** páginas (baseline 104, +1). Se aplicó
  D8: se recortó redundancia en los párrafos agregados (de +2 a +1). Intermedios
  no versionados eliminados (`main.fdb_latexmk`, `main.fls`, `main.xdv`).

## 7. Registro y cierre

- [x] 7.1 Registrar en `CHANGES.md` la entrada de c-110 y su estado. — NO-OP:
  convertida en confirmación no-op por conflicto con los Non-Goals de `design.md`
  (prohíben editar `CHANGES.md`). Registro en roadmap diferido; no se editó el
  archivo.
- [x] 7.2 Ejecutar `openspec validate c-110-marco-teorico-hitl-y-literatura --strict`.
  — Salida: `Change 'c-110-marco-teorico-hitl-y-literatura' is valid`.
- [x] 7.3 Anotar en `docs/Tesis/Correcciones/dictamen-correcciones.md` el estado
  de los ítems 11 y 12. — NO-OP: convertida en confirmación no-op por conflicto
  con los Non-Goals de `design.md` (prohíben editar `dictamen-correcciones.md`).
  Registro en el dictamen diferido; no se editó el archivo.
