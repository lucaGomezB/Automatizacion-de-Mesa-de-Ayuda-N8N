# Tasks: Respuestas del grupo a las 16 preguntas del tribunal (change c-198)

Convenciones: `D/` = `docs/defensa/`; `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` =
`docs/Tesis/Correcciones/`; `A/` = `auditorias/`. "Qn" remite a las preguntas de la Seccion 8 de
`A/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md`; "D-n" al `design.md`. Cada parrafo de
los `.tex` es una sola linea fisica y se localiza por texto (`rg -n`).

**Reglas para todos los grupos.** No commitear, no pushear, no cambiar de rama, no crear tags (la
release `v1.2.19` va aparte). No usar herramientas de engram/memoria. No inventar datos: lo que solo
saben los autores va como `% PENDIENTE-AUTORES(Qn): <que falta>` y el texto visible queda verdadero
sin ese dato. Toda cifra se verifica contra `C/numeros-canonicos.md` o se recalcula desde un
artefacto versionado antes de escribirla. Espanol neutro, sin emojis, sin atribucion a un modelo de
lenguaje. Formato espanol de numeros (`0{,}87` en modo matematico, `0,87` en texto, `~\%`, punto de
miles). Oraciones cortas, una idea por oracion. No cambiar `\label` existentes; remitir con
`\autoref{...}`. Cada grupo edita SOLO sus archivos. Equivalente de Strict TDD para prosa: cada
tarea tiene un grep de aceptacion que se corre ANTES (debe fallar o dar el estado previo) y DESPUES
(debe pasar); se reportan ambas salidas. Sin aserciones triviales.

**Skills del registro** (`.agents/SKILLS.md`): ninguna skill de dominio aplica a la redaccion
Markdown/LaTeX. Gobernanza: documento de respuestas MEDIUM; el bloque legal (Q15 y Q16) HIGH en lo
que afirma sobre hechos.

## 1. Grupo A — Documento de respuestas `D/respuestas-tribunal.md`

- [x] 1.1 D0 del grupo: verificar el estado de partida con `rg -n` sobre `S/04`, `S/07`, `S/08`, `S/11`, `S/12`, `C/numeros-canonicos.md` y `data/README.md`; confirmar que los hechos de D3 y D5 existen y que `D/respuestas-tribunal.md` NO existe todavia. Si un hecho no aparece, detener y reportar.
- [x] 1.2 Crear `D/respuestas-tribunal.md` con el encabezado, una nota de alcance (respuesta del grupo, sin atribucion a un modelo de lenguaje) y los cuatro bloques con sus 16 preguntas (`### Q1. ...` a `### Q16. ...`), sin respuestas todavia. Aceptacion: `rg -c "^### Q" D/respuestas-tribunal.md` -> 16; `rg -n -i "modelo de lenguaje|IA generativa" D/respuestas-tribunal.md` solo en la nota de alcance y en Q16.
- [x] 1.3 Redactar las respuestas del bloque 1 (Q1 a Q4) segun D3 y D5: (Q1) kappa 0,87 retirado, origen oversight sin planilla, remision a 4.4 y al Anexo I, con `% PENDIENTE-AUTORES(Q1)` si la fecha de etiquetado no consta; (Q2) cifras de julio de un corpus sintetico (3-7-2026); (Q3) 200 de ~2.646, periodo 16-06 a 10-09-2026, muestreo por conveniencia, margen 6,66 %; (Q4) `data/corpus_resultados_web_correo.json` (118/119; `R001`). Aceptacion: `rg -c "0\{?,\}?87" D/respuestas-tribunal.md` no aparece como evidencia; `rg -n "16-06|10-09|conveniencia" D/respuestas-tribunal.md` >= 1; `rg -n "corpus_resultados_web_correo" D/respuestas-tribunal.md` >= 1.
- [x] 1.4 Redactar las respuestas del bloque 2 (Q5 a Q9) segun D3: (Q5) 33,8 % a 79,7 % por operador y agregado 69,3 % (`brazo_manual.csv`); (Q6) tarea distinta entre campanas (decision de sector vs lectura, busqueda y carga); (Q7) Spearman 0,15 y -0,05, automatizado rho = 0,70; (Q8) 81 llamadas de 2026-10 recitadas por un autor y las de la campana complementaria por `O1`/`O2`, sin extrapolar; (Q9) tramos distintos (automatico desde el envio, manual desde la lectura). Aceptacion: `rg -n "33\{,\}8|79\{,\}7|69\{,\}3" D/respuestas-tribunal.md` >= 1; `rg -n "recit" D/respuestas-tribunal.md` >= 2; `rg -n "O1|O2" D/respuestas-tribunal.md` >= 1.
- [x] 1.5 Redactar las respuestas del bloque 3 (Q10 a Q14) segun D3: (Q10) exactitud contra el consenso 0,7971 (110/138) frente a 73,5 % (147/200), Wilson [0,7224; 0,8557]; (Q11) gate 0,70 derivo 0 casos, deterministic 131/200 y supervision por reportante no identificado e intervencion instrumentada; (Q12) 11 de 85 confirmaciones humanas incorrectas (`intervenciones.csv`); (Q13) regla de tres vias fijada despues de conocer los datos, no concluyente; (Q14) balance neto -18,5 a -43,9 h y `a*` = 77,7 %. Aceptacion: `rg -n "0\{,\}7971|110/138" D/respuestas-tribunal.md` >= 1; `rg -n "no concluyente|unilateral" D/respuestas-tribunal.md` >= 1; `rg -n "18\{,\}5|43\{,\}9" D/respuestas-tribunal.md` >= 1.
- [x] 1.6 Redactar las respuestas del bloque 4 (Q15 y Q16) segun D3 y D7: (Q15) no se suscribieron clausulas modelo ni consentimiento para la transferencia; solo llegaron descripciones pseudonimizadas (119) y audio recitado (81); (Q16) las autoevaluaciones del Anexo I se generaron con un modelo de lenguaje y el alcance de su uso en la redaccion queda como `% PENDIENTE-AUTORES(Q16)`. Aceptacion: `rg -n "no se suscribieron|no esta suscrito" D/respuestas-tribunal.md` >= 1; `rg -n "PENDIENTE-AUTORES\(Q16\)" D/respuestas-tribunal.md` >= 1.
- [x] 1.7 Verificacion del grupo: correr todos los greps de 1.2 a 1.6 y reportar antes/despues; confirmar que cada respuesta cita al menos un artefacto versionado (D3) y que ninguna reintroduce el kappa 0,87 como evidencia; `git status --porcelain` muestra solo `D/respuestas-tribunal.md`.

## 2. Grupo B — Memo de numeros canonicos `C/numeros-canonicos.md`

- [x] 2.1 Recorrer `D/respuestas-tribunal.md` y listar cada cifra de resultado; compararlas con los valores vigentes de `C/numeros-canonicos.md`. Aceptacion: la lista queda registrada en el reporte del grupo con la seccion del memo donde ya figura cada una o la marca de "nueva".
- [x] 2.2 Registrar en `C/numeros-canonicos.md`, en una seccion nueva numerada de forma consecutiva, cada valor de resultado de las respuestas que no figure ya en el memo, con valor, procedencia `archivo:linea`, comando o derivacion reproducible y estado. Aceptacion: `rg -n "respuestas-tribunal" C/numeros-canonicos.md` >= 1; `openspec validate` sigue en verde.
- [x] 2.3 Verificacion del grupo: confirmar que ningun valor vigente previo del memo cambio de valor ni de estado. Aceptacion: `git diff C/numeros-canonicos.md` solo agrega filas o secciones nuevas; ningun valor `vigente` previo se modifica.

## 3. Grupo C — Anexo J en `S/12-anexos.tex`

- [x] 3.1 D0 del grupo: localizar por texto el final del Anexo I (`sec:anexo-trazabilidad`) en `S/12-anexos.tex` y confirmar que no existe `sec:anexo-respuestas-tribunal`. Aceptacion: `rg -c "sec:anexo-respuestas-tribunal" S/12-anexos.tex` -> 0 antes.
- [x] 3.2 Agregar, despues del Anexo I, `\section{Respuestas del grupo a las preguntas del tribunal}\label{sec:anexo-respuestas-tribunal}` con una introduccion breve y los cuatro bloques (`\subsection`) y sus 16 respuestas (`\paragraph` o `description`), reproduciendo `D/respuestas-tribunal.md` sin cambios de fondo (D2 y D6). Aceptacion: `rg -c "sec:anexo-respuestas-tribunal" S/12-anexos.tex` >= 1; la seccion queda despues de `sec:anexo-trazabilidad`.
- [x] 3.3 Rutas y tablas del anexo: usar `\path{}` para rutas largas y columnas de prosa `>{\raggedright\arraybackslash}p{}`; evitar lineas `Overfull \hbox` (D6). Aceptacion: la compilacion de la tarea 4.1 no reporta `Overfull \hbox` originada en las lineas del Anexo J.
- [x] 3.4 Verificacion del grupo: confirmar que la serie de anexos llega a J (Anexo I intacto, Anexo J ultimo) y que no se introdujeron cifras ausentes del memo. Aceptacion: `rg -n "Anexo J|Anexo~J" S/12-anexos.tex` >= 1; `git diff S/12-anexos.tex` solo agrega el bloque del Anexo J.

## 4. Grupo D — Compilacion y registro

- [ ] 4.1 Recompilar la tesis con XeLaTeX y biber (`latexmk -xelatex main.tex` desde `docs/Tesis/v10 (IA)/paper/`) y confirmar `main.pdf` sin errores fatales ni referencias o citas indefinidas. Aceptacion: compilacion exitosa; `python verify_citations.py` (desde `docs/Tesis/v10 (IA)/`) reporta `STATUS: PASS`.
- [ ] 4.2 Regenerar `paper/compilacion.md` con `docs/Tesis/Correcciones/resumir_registro_compilacion.py` y consignar el total de paginas y el SHA-256 del PDF. Aceptacion: `sha256sum main.pdf` coincide con el valor consignado; el resumen se genera sin edicion manual.
- [x] 4.3 Registrar el change en `C/dictamen-correcciones.md`; si se abre una seccion `## ... - c-198`, incluir la matriz de 7 columnas con encabezado "Fragmento verificable". Aceptacion: `python -I docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` termina con codigo 0.
- [x] 4.4 Agregar la fase de c-198 en `CHANGES.md` (estado, scope, dependencias, gobernanza, "Leer antes"). Aceptacion: `rg -n "c-198|respuestas-a-las-preguntas-del-tribunal" CHANGES.md` >= 1.
- [x] 4.5 Verificacion final del change: `openspec validate c-198-respuestas-a-las-preguntas-del-tribunal --strict` en verde; correr los greps de aceptacion de todos los grupos y reportar antes/despues; confirmar que no se crearon tags ni artefactos de release y que no se toco `App/`, `n8n/`, `docker/` ni `evaluation/`.
