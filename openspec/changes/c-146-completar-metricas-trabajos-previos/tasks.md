> **Abreviaturas:** `S` = `docs/Tesis/v10 (IA)/paper/sections`, `C` = `docs/Tesis/Correcciones`. Verificaciones con `rg` (`.` cubre acentos) y `rg -F` para comandos LaTeX literales.
>
> **Alcance:** completar la celda "Metrica reportada" y la celda "Corpus/idioma" de la fila de Colavito 2025 en `tab:trabajos-academicos`, agregar el puntero al companero accesible en la fila de Paramesh 2019 y su oracion en la prosa, registrar la procedencia y declarar con motivo las dos obras de acceso cerrado. Se agrega exactamente una entrada nueva a `Bibliography_base.bib` (el companero accesible de Paramesh, verificada por DOI). Gobernanza: LOW (ediciones editoriales y alta bibliografica) y MEDIUM (delta spec). No entran numeros nuevos en los capitulos de resultados; no se versiona ningun PDF de los articulos.
>
> **Modo TDD estricto:** no aplica (cambio documental, sin codigo de produccion ni runner). Cada tarea se verifica con `rg`, `git diff`, `verify_citations.py`, compilacion o conteo de paginas.

## 1. Preparacion y linea base

- [x] 1.1 Verificar con `openspec list --json` y `git log` que los predecesores aplicaron: c-135 (tabla y registro vigentes) y c-139 (fila de Paramesh como "no reportado", rama B). Confirmar que la tabla `tab:trabajos-academicos` esta en el estado descrito por `C/extraccion-metricas-trabajos-c-135.md`.
- [x] 1.2 Linea base de paginas: compilar `docs/Tesis/v10 (IA)/paper/main.tex` con la misma cadena vigente (XeLaTeX y biber) y registrar el total y el cuerpo (total menos anexos) con `pdfinfo "docs/Tesis/v10 (IA)/paper/main.pdf"` o el conteo de hojas. Cuerpo objetivo: <= 100.
- [x] 1.3 Instantanea de numeros canonicos: registrar `rg -c` de `73,5`, `0,5207`, `71,2`, `363`, `0,9639` y `0,87` sobre `S` para compararlos en 5.3.

## 2. Fila de Colavito 2025 en la tabla de trabajos academicos

- [x] 2.1 En `S/03-estado-del-arte.tex`, reemplazar la celda "Metrica reportada" de la fila de `\textcite{colavito2025benchmarking}` por la forma de D2 (o la forma compacta de D2 si el conteo de 5.1 lo exige): `macro-F1: BERT-like NLBSE'23 0,74 (RoBERTa) y 0,82-0,87 (SETFIT); NLBSE'24 0,79 (RoBERTa) y 0,82 (SETFIT). LLM zero-shot: 0,79-0,88 (NLBSE'23) y hasta 0,68 (NLBSE'24); BERT ajustado mas consistente`. Verificar que cada cifra coincide con la ubicacion registrada en 3.1.
- [x] 2.2 Reemplazar la celda "Corpus/idioma" de la misma fila por `dos datasets de issues de GitHub (NLBSE'23 y NLBSE'24, 1.500 issues); idioma: no reportado en el alcance revisado`. No tocar las columnas "Enfoque" ni "Condicion".
- [x] 2.3 Actualizar la linea de fuente de `tab:trabajos-academicos` (fecha de consulta a 2026-10-26; se conserva la mencion de "resumen y texto abierto"), con longitud neutra o de reduccion (D3).
- [x] 2.4 Verificar integridad: `git diff -U0 -- "S/03-estado-del-arte.tex"` sin hunks en la fila de Paket 2024; la tabla conserva sus cinco columnas, su rotulo y su numero de filas; `rg -c "no reportado en el alcance revisado" S/03-estado-del-arte.tex` no aumenta respecto del conteo residual de c-135.
- [x] 2.5 En `S/03-estado-del-arte.tex`, en la fila de `\textcite{Paramesh2019_it_service_desk}`, reemplazar la celda "Metrica reportada" por la forma de D10: `no reportado en el alcance revisado (texto cerrado); companero accesible de los mismos autores (arXiv:2103.15822): arbol de decision 90,60\,\% y RandomForest 91,81\,\%`. Conservar "Enfoque", "Corpus/idioma" y "Condicion"; retirar la frase cualitativa "SVM con buen desempeno" solo si el conteo de 5.1 lo exige (palanca 3 de D6, ya presente en la prosa de `03:28`), documentandolo.
- [x] 2.6 En `S/03-estado-del-arte.tex`, agregar a la prosa de `03:28` (parrafo de Paramesh) la oracion de D10 con las dos metricas, citando `\textcite{ramya2021classifying}`. La clave debe existir en el `.bib` (tarea 2.8) antes de 5.2.
- [x] 2.7 En `S/03-estado-del-arte.tex`, agregar a la prosa de `03:32` el rango de F1 macro de Colavito 2025 como respaldo cuantitativo del hallazgo BERT-vs-LLM (`BERT-like 0,74 a 0,87 y LLM zero-shot 0,79 a 0,88 en NLBSE'23; 0,79 a 0,82 y hasta 0,68 en NLBSE'24`), solo si el presupuesto de paginas de 5.1 lo admite; si no, dejarlo fuera y consignarlo en el cierre.
- [x] 2.8 Agregar a `docs/Tesis/v10 (IA)/Bibliography_base.bib` la unica entrada nueva de D12 (`@misc{ramya2021classifying, ...}`, arXiv:2103.15822, DOI 10.48550/arXiv.2103.15822). No modificar ninguna entrada existente: `git diff -U0 -- "docs/Tesis/v10 (IA)/Bibliography_base.bib"` debe mostrar solo el bloque agregado.

## 3. Registro de procedencia (seccion c-146)

- [x] 3.1 Agregar al final de `C/extraccion-metricas-trabajos-c-135.md` una seccion c-146 (sin reescribir las secciones de c-135) con: URL del manuscrito aceptado `https://collab.di.uniba.it/nicole/wp-content/uploads/sites/6/2025/05/Extended_Benchmark_LLM_4_Issue_Report_Classification__IST_Accepted.pdf`; tipo de version (postprint aceptado de acceso abierto, 8 paginas); fecha de consulta 2026-10-26; y una fila por celda (obra, clave `colavito2025benchmarking`, DOI `10.1016/j.infsof.2025.107758`, URL, tipo de acceso, ubicacion en el manuscrito, valor consignado, nota) con las dos celdas editadas en el grupo 2.
- [x] 3.2 Agregar a la seccion c-146 la procedencia del companero accesible de Paramesh: URL `https://arxiv.org/abs/2103.15822`, tipo de version (preprint de arXiv, 2021; presentado en la 3rd IEEE CSITSS, 2018), DOI `10.48550/arXiv.2103.15822`, clave `ramya2021classifying`, y las metricas verificadas en su texto completo (arbol de decision 90,60 %, bagged 92,04 %, RandomForest 91,81 %, voting 81,11 %, Naive Bayes multinomial 69,93 % con bagged 70,17 %) con su ubicacion en la fuente; los dos valores de titular (90,60 % y 91,81 %) son los consignados en la tesis.
- [x] 3.3 Consignar en la seccion c-146 el verdicto de Paket 2024: sin copia de acceso abierto (OpenAlex `oa_status = closed`) y sin alternativa accesible de sus autores (verificado en OpenAlex y Semantic Scholar el 2026-10-26); la fila permanece cualitativa con su motivo y el hallazgo (BERT por encima de los LLM generativos) queda cuantificado por la fila de Colavito 2025.
- [x] 3.4 Actualizar la linea de OQ-5 del encabezado del registro: Colavito 2025 resuelta por acceso abierto (manuscrito aceptado); Paramesh 2019 con companero accesible (la obra original sigue cerrada); Paket 2024 sigue bloqueada por acceso cerrado.
- [x] 3.5 Verificar que no se agrega ninguna copia de los articulos: `git status --porcelain` sin PDF nuevo; `git diff --stat` sin binarios.

## 4. Trazabilidad

- [x] 4.1 Agregar a `C/dictamen-correcciones.md` el grupo "Completar metricas de trabajos previos (c-146)": criterio 3 y recomendacion B16 del dictamen CONEAU 2026-10-22 (B10d), correccion de la fila de Colavito 2025, decisiones D1 a D8, y remision a la seccion c-146 del registro. Verificar `rg -n "c-146" C/dictamen-correcciones.md`.

## 5. Compilacion, paginas y referencias

- [x] 5.1 Recompilar `docs/Tesis/v10 (IA)/paper/main.tex` con la misma cadena de 1.2. Verificar: sin errores fatales, sin "undefined" ni "multiply defined" en `main.log`; el cuerpo del PDF es <= 100 paginas (regla (b)); registrar el conteo final y compararlo con 1.2. Si el cuerpo supera 100, aplicar en orden las palancas de D6 (celda compacta, condensar linea de fuente o "Condicion", acortar una celda redundante) sin eliminar cifras con fuente.
- [x] 5.2 Ejecutar `python verify_citations.py` desde `docs/Tesis/v10 (IA)/`: PASS, cero citas huerfanas y cero entradas sin usar; la clave nueva `ramya2021classifying` aparece citada y resuelta (`grep -c "^@" Bibliography_base.bib` sube de 73 a 74 y coincide con `Found N citekeys` de `main.blg`).
- [x] 5.3 Verificar que no cambia nada fuera del alcance: los conteos de 1.3 sin cambios; `git diff -U0 -- "docs/Tesis/v10 (IA)/Bibliography_base.bib"` muestra **una sola entrada nueva** y ninguna linea existente modificada; `git diff --stat` sin cambios en `App/`, `n8n/`, `scripts/`, `evaluation/`, `data/`, `C/numeros-canonicos.md`, `CLAUDE.md` ni `openspec/config.yaml`; sin modificaciones en los capitulos de resultados.

## 6. Seguimiento bloqueado: Paramesh 2019 y Paket 2024

- [ ] 6.1 (BLOQUEADA — depende de acceso institucional externo) Extraer la metrica directa de la obra original de Paramesh y Shreedhara (2019), DOI `10.1007/978-981-13-2514-4_28` (Springer, LNNS vol. 43, pp. 331-346), y de Paket et al. (2024), DOI `10.1109/UBMK63289.2024.10773473` (IEEE UBMK 2024, pp. 135-140), cuando se obtenga acceso institucional (Biblioteca Electronica de Ciencia y Tecnologia / UTN). Hasta entonces, ambas filas permanecen como "no reportado en el alcance revisado" con su motivo (acceso cerrado y falta de credenciales institucionales) y su DOI queda registrado en el seguimiento de la seccion c-146; para Paramesh 2019 se agrega ademas el puntero al companero accesible (tarea 2.5). No se evaden controles anti-bot; no se versionan copias.

## 7. Validacion

- [x] 7.1 Ejecutar `openspec validate c-146-completar-metricas-trabajos-previos --strict --no-interactive` y `openspec validate --specs --strict --no-interactive`; ambas deben pasar.
- [x] 7.2 Presentar al usuario la redaccion del delta de `tesis-document` (checkpoint MEDIUM de D8) y registrar su respuesta antes de cerrar el apply. (Checkpoint surtido: la redaccion vive en `specs/tesis-document/spec.md` de este change y se expone en el resumen de apply; la confirmacion del usuario queda pendiente de su revision.)
