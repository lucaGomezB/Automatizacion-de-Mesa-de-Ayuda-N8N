# Tasks: Atender el dictamen CONEAU sobre v1.2.13

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` =
`docs/Tesis/Correcciones/`. "Observacion N" y "item 12" remiten al dictamen del 2026-11-09
sobre `v1.2.13` (`Dictamen v10 / v1.2.13`, todavia no versionado). Las anclas se localizan por
el texto citado (`rg -n`). Numeracion compilada: 8.x = `07-resultados.tex`, 9.x =
`08-discusion.tex`, 10 = `09-conclusiones.tex`, 6.x = `06-implementacion.tex`, 3.x =
`03-estado-del-arte.tex`, 1.6 = `01-introduccion.tex`, Anexos = `12-anexos.tex`. Linea base:
118 paginas; resumen y abstract <= 250 palabras. No se edita codigo ni artefactos de `App/`,
`n8n/`, `evaluation/` ni `analisis/`. En la prosa del registro usar "seccion N
(`archivo.tex`)" (gitleaks). Release `v1.2.14`.

## 0. Preparacion y verificacion (solo lectura; bloqueante)

- [x] 0.1 Confirmar con `git fetch` el estado de `origin/main` y de la rama `change/c-192-atender-el-dictamen-v1-2-13`; verificar que `.openspec.yaml` existe. Trabajar en esa rama.
- [x] 0.2 Compilar la linea base en el entorno de registro (`MSYS_NO_PATHCONV=1 docker run --rm -v "<paper>":/workdir texlive-thesis latexmk main.tex`): anotar paginas, `Overfull` (cantidad y maximo) y estado de `verify_citations.py`; guardar `pdftotext` del Anexo B en el scratchpad. Safety net: `python C/verificar_matriz_trazabilidad.py` -> 0 fallas; `cd C/ && python -m unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` en verde.
- [x] 0.3 Script descartable en el scratchpad (design D0): reproducir `tanh((z_{0,975}+z_{0,80})/sqrt(107*0,912)) = 0,276` y que 0,2834 sale con `sqrt(107*0,864)`; 122/200 = 61,0 % y 122/147 = 83,0 %; Wilson de 25/147 = [11,79 %; 23,90 %] y binomial (25/147, p = 0,15) -> p = 0,28; conjunto laxo manual por interseccion = 130/151 (union = 137) leyendo `evaluation/campana.py::construir_referencia` y `doble_etiquetado.csv`; kappa 0,5569 del par `E1`/`E2` frente al 0,87 del par autor/analista. **Si una cifra no se reproduce, detener esa recomendacion y consultar a los autores.**
- [x] 0.4 Leer `git show v1.2.13:"docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"` y el `pdftotext` del PDF etiquetado `v1.2.13`: confirmar que imprime el hash de la release previa (`7937efd`). Insumo de D1.
- [x] 0.5 **Decisiones de los autores** (design D2, D3, D6, D8): MDE (corregir a 0,276 o justificar); matiz del intervalo dentro o fuera del resumen; FrugalGPT (OpenReview TMLR o arXiv `2305.05176`); VIS (primer uso o glosario). Registrar cada respuesta en `C/dictamen-correcciones.md` (seccion de c-192).

## 1. Regla de hash de release en el Anexo B (observacion de proceso; critica)

- [x] 1.1 `S/12-anexos.tex` (Anexo B, ~linea 44-46): reemplazar el hash impreso por la oracion de reemplazo de design D1 ("El PDF compilado en el propio tag no imprime ese hash: el hash completo de la release v1.2.14 se consigna en el commit que sigue al tag en la rama principal, y los commits posteriores no modifican las fuentes de la tesis."). El texto SHALL explicar el mecanismo sin imprimir el hash de una release previa.
- [x] 1.2 Verificar que la oracion de reemplazo no contiene ningun hash (`rg -n "[0-9a-f]{40}" S/12-anexos.tex` = 0 en la oracion del tag).
- [x] 1.3 Registrar en `C/dictamen-correcciones.md` la causa raiz (el commit de contenido conservo el hash previo) y la regla adoptada, referenciando el patron c-188.
- [x] 1.4 (Orquestador) Tras el tag: commit siguiente que reemplaza la oracion por el hash completo del commit de contenido; `git diff --stat v1.2.14 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` = una linea.
- [x] 1.5 Verificacion: `pdftotext` del PDF etiquetado `v1.2.14` no contiene `7937efd` ni `f527722`; el Anexo B del PDF etiquetado muestra la oracion de reemplazo.

## 2. Item 12 - MDE del Spearman

- [x] 2.1 `S/07-resultados.tex:253` (8.7, "Efecto de posicion y de orden"): reemplazar 0,2834 por 0,276 y la formula `\tanh((z_{0,975}+z_{0,80})/\sqrt{107\cdot 0,864})` por `\tanh((z_{0,975}+z_{0,80})/\sqrt{107\cdot 0,912})`; reemplazar la ARE de Wilcoxon por la eficiencia de Spearman (9/pi^2 ≈ 0,912).
- [x] 2.2 `C/numeros-canonicos.md` (seccion 3.16, fila del MDE de posicion, ~linea 851): actualizar el valor a 0,276 y anotar la fuente y la correccion (el valor previo usaba la ARE de Wilcoxon). Declarar la discrepancia con `analisis/resultados.json` si conserva 0,2834; no editar el JSON.
- [x] 2.3 Verificacion: `rg -n "0,2834" S/ C/numeros-canonicos.md` = 0; recalculo del MDE impreso con la formula declarada coincide a cuatro decimales (0,276).

## 3. Segunda sub-hipotesis: veredicto, matiz y denominadores

- [x] 3.1 `S/07-resultados.tex:154` (8.3): conservar "refutada" (estimacion 17,0 % >= 0,15) y agregar el matiz (IC de Wilson [11,8 %; 23,9 %] contiene 0,15; binomial 25/147 con p = 0,15 da p = 0,28; lectura conservadora "no se puede descartar 0,15").
- [x] 3.2 `S/07-resultados.tex:154` (8.3): corregir "122 confirmaciones (61,0 %)" con ambos denominadores explicitos (122/200 = 61,0 %; 122/147 = 83,0 %).
- [x] 3.3 `S/09-conclusiones.tex:26` (Tabla 18, celda del OE4): retirar la contradiccion ("refutada ... sin medicion valida por la regla del reportante") y alinear la celda con el veredicto y el matiz.
- [x] 3.4 Segun D3: propagar el matiz a 9.1 (`S/08-discusion.tex`) solo si corresponde; si se incluye en resumen (`S/00-resumen.tex`) o abstract, compensar palabras (tope 250).
- [x] 3.5 `C/numeros-canonicos.md`: registrar 122/200 = 0,61 y 122/147 = 0,83 con su fuente, y el matiz (Wilson y binomial).
- [x] 3.6 Verificacion: `rg -n "122 confirmaciones|61,0" S/07-resultados.tex` acota el 61,0 % a 200; la Tabla 18 OE4 no contiene "sin medicion valida" junto a "refutada"; el veredicto es "refutada" en 8.3, 9.1 y la Tabla 18.

## 4. 1.6 - Atribucion del kappa

- [x] 4.1 `S/01-introduccion.tex:66` (1.6): separar los dos pares: el acuerdo moderado (0,5569; `p_o = 0,69`; `p_e = 0,30`) corresponde al doble etiquetado `E1`/`E2`; el par analista externo + analista autor tiene acuerdo 0,87 (sin intervalo). Sin datos personales.
- [x] 4.2 Verificar coherencia con 4.4, 8.7 ("Fiabilidad del doble etiquetado") y 9.3: ningun pasaje atribuye el 0,5569 al par autor/analista.
- [x] 4.3 Verificacion: `rg -n "0,5569|0,87" S/` -> cada aparicion atribuye el valor a su par.

## 5. Conjunto laxo del brazo manual

- [x] 5.1 `S/07-resultados.tex:251` (8.7, "Exactitud del brazo manual"): reemplazar "union de los sectores adicionales de ambos etiquetadores" por "interseccion de los sectores adicionales de ambos etiquetadores".
- [x] 5.2 (Opcional) Declarar en una nota que la union daria 137 y la interseccion 130, para trazabilidad; registrar en `C/numeros-canonicos.md` con la fuente (`construir_referencia`).
- [x] 5.3 Verificacion: `rg -n "union de los sectores adicionales" S/07-resultados.tex` = 0; la cifra laxa manual publicada sigue siendo 130/151.

## 6. Residuales menores

- [x] 6.1 `S/06-implementacion.tex:37` (6.3): "telefonia (trigger de Twilio)" -> "telefonia (callback de grabacion de Twilio)", alineado con 6.4.
- [x] 6.2 `S/03-estado-del-arte.tex:62` (3.1, Xiong): atenuar "poca capacidad para separar aciertos de errores" -> "predecir las fallas sigue siendo un desafio"; conservar sobreconfianza y concentracion en la parte alta (coherente con 2.5 y 9.2).
- [x] 6.3 VIS (segun D6): desarrollar en el primer uso en `S/07-resultados.tex:154` ("regla de visibilidad y derivacion por reportante no identificado (VIS-005)") o agregarla al glosario; garantizar uso de cada entrada del glosario.
- [x] 6.4 FrugalGPT (segun D6): conservar la entrada TMLR con la URL de OpenReview `cSimKw5p6R` como evidencia, o agregar el preprint arXiv `2305.05176` como respaldo; registrar la decision. No inventar venue.
- [x] 6.5 Paginas: registrar en el libro mayor de `C/dictamen-correcciones.md` que el exceso de 118 paginas sobre el tope de 100 es un residual declarado, sin reduccion en este change.
- [x] 6.6 Verificacion: `rg -n "trigger de Twilio" S/06-implementacion.tex` = 0; `rg -n "separar aciertos de errores" S/03-estado-del-arte.tex` = 0; VIS desarrollada o en el glosario con uso.

## 7. Registro, Anexo I y memo

- [x] 7.1 `C/dictamen-correcciones.md`: seccion "Dictamen v10 / v1.2.13 (2026-11-09) - c-192" con la matriz de 7 columnas (Rec | Sintesis | Change | Archivo:linea | Ancla | Fragmento verificable | Estado): una fila por observacion (1-4), el item 12 y cada residual; decisiones de D0.5 y de este design; libro mayor de paginas y palabras.
- [x] 7.2 `S/12-anexos.tex` (`sec:anexo-trazabilidad`): tabla de trazabilidad del dictamen del 9-11 sobre v1.2.13 (o actualizacion de la existente) con las secciones tocadas y `\autoref`; sin numeros de linea; `\small` y filas compactas para no agregar altura neta.
- [x] 7.3 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py` (no vacio).
- [x] 7.4 Verificacion: `python C/verificar_matriz_trazabilidad.py` -> 0 fallas; `cd C/ && python -m unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` en verde.

## 8. Compilacion

- [x] 8.1 Recompilar en el entorno de registro: 0 errores, 0 referencias o citas indefinidas, 0 `multiply defined`, `main.blg` sin WARN/ERROR, 0 `??` en `pdftotext`, `Overfull` no mayor que la linea base; `verify_citations.py` PASS.
- [x] 8.2 Paginas <= 118 y resumen y abstract <= 250 palabras; si se supera, recortar prosa en los parrafos tocados y recompilar; si aun asi no, detener y consultar. Registrar el libro mayor en `C/dictamen-correcciones.md`.
- [x] 8.3 Generar `docs/Tesis/v10 (IA)/paper/compilacion.md` con `C/resumir_registro_compilacion.py` y comprobar que su SHA-256 coincide con `sha256sum main.pdf`.

## 9. Release y archivo

- [x] 9.1 `openspec validate c-192-atender-el-dictamen-v1-2-13 --strict --no-interactive`.
- [x] 9.2 (Tarea no bloqueante) Cuando Gonzalo entregue el archivo `auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md`, versionarlo (`git add`); si la release ya cerro, commit posterior. **No bloquea la release.**
- [x] 9.3 (Orquestador) Commit de contenido de la release en `change/c-192-atender-el-dictamen-v1-2-13` con la oracion de reemplazo del Anexo B, y tag anotado `v1.2.14`; commit del hash que reemplaza la oracion por el hash del commit de contenido (design D1).
- [x] 9.4 (Orquestador) Verificacion de la regla de hash: `git diff --stat v1.2.14 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` = una linea; `pdftotext` del PDF etiquetado `v1.2.14` sin `7937efd` ni `f527722`.
- [x] 9.5 (Orquestador) `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` (nunca `--all`), commit de `.engram/` y PR contra `main` (nunca push directo); push del tag con confirmacion del usuario.
