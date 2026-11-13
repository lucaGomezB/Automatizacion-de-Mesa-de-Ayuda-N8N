# Tasks: Integrar el contraste de eficiencia solo-LLM en la tesis

Convenciones: `T/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`. El change es ADITIVO: no cambia ningún número canónico de las secciones `3.1`-`3.26`, ni el clasificador, ni el corpus, ni la referencia, ni el gate. NO se edita L2-L5 (referencia, gate y forma): eso es de `c-216`. NO se emite ninguna llamada nueva a Gemini (la corrida paga ya se hizo en c-215). `CHANGES.md` lo reconcilia el orquestador, fuera de estas tareas.

## 0. Preparación, prerregistro de la decisión y red de seguridad

- [ ] 0.1 Confirmar el estado: `openspec validate c-217-integrar-el-contraste-de-eficiencia-solo-llm --strict --no-interactive` en verde y `openspec status --change c-217-integrar-el-contraste-de-eficiencia-solo-llm --json` con `proposal`/`specs`/`design`/`tasks` presentes. Verificación: sin errores de validación.
- [ ] 0.2 Red de seguridad de la evaluación antes de tocar nada: `python -m pytest evaluation -q` y `python -m pytest evaluation/data/campana/analisis -q` desde la raíz; registrar el conteo base (se esperan fallas preexistentes por `ENTORNO_OFFLINE` y las pruebas del análisis; NO se corrigen aquí). Verificación: línea base anotada.
- [ ] 0.3 Congelar en el commit de la propuesta la decisión de referencia (design D1: opción (b)) y el costo declarado de la opción (a), antes de cualquier edición de prosa. Verificación: `design.md` con D1 y las cifras citadas.

## 1. Integración del contenido de c-215 en `main`

- [ ] 1.1 Crear la rama desde `main` e integrar la rama de c-215 con `git merge origin/change/c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia` (sin squash ni rebase). Verificación: el merge reporta los archivos en conflicto esperados y ningún archivo de `App/Backend/` cambia.
- [ ] 1.2 Resolver el conflicto de `C/numeros-canonicos.md`: descartar la sección `3.25` de c-215 (colisiona con la de c-206) y conservar la `3.26` vigente; la sección nueva se agrega en la tarea 3.1. Verificación: el memo conserva `3.25` (c-206) y `3.26` (c-213) intactas.
- [ ] 1.3 Resolver el conflicto de `C/dictamen-correcciones.md` conservando las entradas de `main` y posponiendo la entrada de c-217 a la tarea 3.2. Verificación: el registro conserva las entradas previas y no duplica encabezados.
- [ ] 1.4 Verificar que el código fusionado está presente y sin cambios respecto de la rama: `evaluation/brazo_gemini_solo.py`, `evaluation/tests/test_brazo_gemini_solo.py`, `evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.{py,json,md}` y `.SHA256SUMS.txt`, y `evaluation/data/campana/brazo_gemini_solo/cache_brazo_gemini_solo.jsonl`. Verificación: los SHA-256 de las salidas coinciden con los de la rama y el caché mantiene su blob.
- [ ] 1.5 Correr el subconjunto offline de las pruebas del brazo: `python -m pytest evaluation/tests/test_brazo_gemini_solo.py evaluation/data/campana/analisis/test_analisis_brazo_gemini_solo_c215.py -q` sin red ni clave. Verificación: mismas fallas/pasadas que la base de 0.2, sin llamadas a la API.
- [ ] 1.6 Regenerar el análisis de solo lectura y verificar determinismo: `python3 evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py` dos veces. Verificación: salidas idénticas byte a byte y el veredicto del bloque primario sigue siendo «no concluyente».
- [ ] 1.7 Verificar la deriva de H sobre los 103 compartidos entre el caché de c-215 (consenso) y `predicciones_arbitrado.json`. Verificación: se documenta si coinciden; si no, queda como limitación declarada en el memo (tarea 3.1), sin recalcular el veredicto.

## 2. Prosa de la tesis sobre el texto vigente de `main`

- [ ] 2.1 `T/04-marco-metodologico.tex`: insertar el `\paragraph{Brazo de modelo de lenguaje solo.}` tras el párrafo de calibración del gate (`subsec:metricas-instrumentos`), con el margen `0,05`, la regla de tres vías, el control de deriva, el análisis no ciego y la desviación por el reintento. Verificación: el párrafo figura y no altera los párrafos vecinos.
- [ ] 2.2 `T/07-resultados.tex`: agregar el párrafo del contraste frente al brazo solo, la tabla `tab:gemini-solo` y los párrafos de eficiencia, bloque secundario, control de deriva y desviación, después del contraste pareado frente a la línea de base. Verificación: la tabla y el párrafo citan las cifras de c-215 (`87/103`, `90/103`, `p = 0,5078`, `−0,0291` `[−0,0874; 0,0291]`, razón de llamadas `0,3301`) y el veredicto «no concluyente».
- [ ] 2.3 `T/08-discusion.tex`: reemplazar «no se contrastó» / «sigue sin contrastarse» por el contraste con resultado no concluyente en los tres pasajes (interpretación, cascadas, alternativas), sin perder las cifras dentro de la muestra `0,7405`/`0,6769` ni su carácter in-corpus. Verificación: los tres pasajes declaran «no concluyente» y ninguno afirma no inferioridad.
- [ ] 2.4 `T/09-conclusiones.tex`: reemplazar «Las dos hipótesis subsidiarias no se contrastaron» y los pasajes de estrategia compositiva y de aportes por «contrastada: no concluyente» (ahorro ~1/3, sin diferencia de exactitud detectada, sin establecer no inferioridad). Verificación: la eficiencia figura como contrastada no concluyente y la multicanal como no contrastada.
- [ ] 2.5 `T/01-introduccion.tex`: cambiar «Ninguna de las dos se somete a un contraste formal» por el estado real (la de eficiencia se contrastó con resultado no concluyente; la multicanal no se contrasta), con remisión a `tab:gemini-solo`. Verificación: el enunciado de la hipótesis queda separado del veredicto y coherente con `09`.
- [ ] 2.6 `T/10-recomendaciones.tex`: actualizar el pasaje de trabajo futuro para proponer repetir el contraste con más casos fuera de muestra y corridas repetidas, y reconocer que el brazo solo ya se midió. Verificación: la recomendación no afirma que el esquema solo-modelo «no se midió».
- [ ] 2.7 Verificar que no queda ninguna afirmación de eficiencia «sin contrastar» ni de no inferioridad en `T/01`, `T/04`, `T/07`, `T/08`, `T/09` y `T/10`. Verificación: `rg -n "no se contrastó|sigue sin contrastarse|no se contrastaron"` sobre esas secciones solo devuelve la hipótesis multicanal.

## 3. Registro aditivo

- [ ] 3.1 `C/numeros-canonicos.md`: agregar la sección `3.27` con las cifras del contraste (bloque primario `vigente (nuevo)`; secundario y deriva `condicional`; desviación y amenaza a la validez), procedencia por valor, comando y SHA-256 de las salidas, y la remisión que supera las frases previas «sin contrastar». Verificación: la sección es la última, no cambia ningún valor de `3.1`-`3.26` y cada fila declara estado.
- [ ] 3.2 `C/dictamen-correcciones.md`: agregar una entrada de c-217 que documente el veredicto honesto (no concluyente), la decisión de referencia (103 previa / 206 complemento) y su costo, y la matriz de trazabilidad de los pasajes `C17/*`. Verificación: la entrada existe, es aditiva y remite a `3.27`.
- [ ] 3.3 Verificar la coherencia memo↔prosa: cada cifra citada en `T/07` figura en `3.27` con su procedencia y estado. Verificación: muestreo de al menos las cifras de exactitud, McNemar, diferencia, razones y veredicto.

## 4. Validación y cierre

- [ ] 4.1 `openspec validate c-217-integrar-el-contraste-de-eficiencia-solo-llm --strict --no-interactive` en verde. Verificación: sin errores ni advertencias.
- [ ] 4.2 Verificar que no se tocó L2-L5: `git diff` sobre la referencia, el gate (`subsec:calibracion-gate`) y la forma no muestra cambios ajenos a este change. Verificación: sin cambios fuera de los archivos declarados en `proposal.md`.
- [ ] 4.3 Confirmar costo cero: `git diff --stat` no incluye nuevos artefactos de corrida paga ni cambios en el caché. Verificación: el único artefacto de corrida es el caché de c-215, sin modificar.
- [ ] 4.4 [AUTORES] Recompilar `main.pdf` y revisar la paginación de `tab:gemini-solo` (LaTeX puede no estar disponible en esta máquina; queda pendiente como en c-215). Verificación: compilación sin errores fatales y sin referencias indefinidas.