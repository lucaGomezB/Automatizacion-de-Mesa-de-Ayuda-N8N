> Convenciones: T01-T07 son los objetivos de propagacion de `design.md` (texto ANTES/DESPUES exacto). Las rutas `sections/` se resuelven desde `docs/Tesis/v10 (IA)/paper/`. No aplica modo TDD estricto (change documental, sin codigo nuevo); la verificacion es por `rg`/`grep`, recompilacion, regeneracion del render y `openspec validate`. No se modifica ningun valor numerico ni rotulo.

## 1. Linea base y verificacion de evidencia

- [x] 1.1 Confirmar la inexistencia del directorio de historial del prompt: `test ! -d docs/prompt_gemini_history` (exito), `git log --all --oneline -- docs/prompt_gemini_history` (sin salida), `git ls-files | rg prompt_gemini_history` (sin salida) y `git branch -a --contains` sin coincidencias; registrar el resultado
- [x] 1.2 Confirmar la procedencia de los ajustes: verificar que `1368fd8` (c-71) amplio el vocabulario, `a76851e` (c-72) agrego las reglas de frontera y `d6bb474` (c-74) fijo el punto de operacion, y que no existe ningun conjunto de ~100 incidentes independientes (`rg -l "incidentes de preproduccion" data/ evaluation/` sin resultados); registrar la evidencia y el desenlace "no existen / no se localizan"
- [x] 1.3 Registrar la linea base del PDF: `grep "abspage@last" "docs/Tesis/v10 (IA)/paper/main.aux"`; anotar el valor y el commit de partida en el grupo c-144 de `docs/Tesis/Correcciones/dictamen-correcciones.md`
- [x] 1.4 Checkpoint de autores sobre el texto final (Open Questions 1 y 2 de `design.md`); registrar la decision antes de aplicar el bloque 2

## 2. Tesis: procedencia real y ubicacion del historial del prompt

- [x] 2.1 Aplicar T01 en `sections/05-arquitectura.tex:78`; verificar `rg -c "sin acceso al corpus de validación" sections/05-arquitectura.tex` == 0 y `rg -c "La procedencia de los datos empleados" sections/05-arquitectura.tex` == 1
- [x] 2.2 Aplicar T02 en `sections/06-implementacion.tex:75`, solo sobre la segunda oracion del item; verificar `rg -c "sin exposición al corpus de validación" sections/06-implementacion.tex` == 0 y `rg -c "no se dispuso de un conjunto independiente de incidentes de preproducción" sections/06-implementacion.tex` == 1
- [x] 2.3 Aplicar T03 (parrafo completo) en `sections/08-discusion.tex:18`; verificar `rg -c "datos no vistos" sections/08-discusion.tex` == 0, `rg -c "separación estricta" sections/08-discusion.tex` == 0 y `rg -c "estimaciones dentro de la muestra" sections/08-discusion.tex` >= 1
- [x] 2.4 Aplicar T04 (parrafo completo) en `sections/12-anexos.tex:135`; verificar `rg -c "prompt_gemini_history" "docs/Tesis/v10 (IA)/paper/sections/"` == 0, `rg -c "100 incidentes representativos" sections/12-anexos.tex` == 0 y `rg -c "historial de versiones del repositorio" sections/12-anexos.tex` == 1
- [x] 2.5 Barrido: `rg -n "sin exposición a|sin acceso al corpus|datos no vistos|separación estricta|prompt_gemini_history" "docs/Tesis/v10 (IA)/paper/sections/"` sin resultados (la frase "sin exposición de valores" de `12-anexos.tex:45`, si existe, es ajena al tema)

## 3. Documentacion de soporte: Anexo H y advertencia del framework

- [x] 3.1 Aplicar T05 en `docs/anexo_h_prompt_gemini.md:160` y `:162`; verificar `rg -c "sin exposición al corpus de validación" docs/anexo_h_prompt_gemini.md` == 0, `rg -c "prompt_gemini_history" docs/anexo_h_prompt_gemini.md` == 0 y `rg -c "historial de versiones de \`docs/prompt_gemini.txt\`" docs/anexo_h_prompt_gemini.md` == 1
- [x] 3.2 Aplicar T06 en `evaluation/README.md:192-204`; verificar `rg -c "El clasificador NO fue ajustado" evaluation/README.md` == 0, `rg -c "1368fd8|a76851e|d6bb474" evaluation/README.md` >= 3 y `rg -c "estimaciones dentro de la muestra" evaluation/README.md` == 1
- [x] 3.3 Aplicar T07 en `sections/10-recomendaciones.tex` (subseccion nueva antes de `\subsection{Estudios de replicación}`); verificar `rg -c "label{subsec:corpus-independiente}" sections/10-recomendaciones.tex` == 1 y `rg -c "no se dispuso de un corpus de preproducción" sections/10-recomendaciones.tex` == 1

## 4. Registro del checkpoint y trazabilidad

- [x] 4.1 Registrar en `docs/Tesis/Correcciones/numeros-canonicos.md` (Seccion 7, "Decisiones no resolubles", hoy `:330`) el desenlace "no existen / no se localizan" del conjunto de ~100 incidentes de preproduccion y la dependencia del Anexo H; verificar `rg -c "no existen / no se localizan" docs/Tesis/Correcciones/numeros-canonicos.md` == 1
- [x] 4.2 Registrar en `docs/Tesis/Correcciones/dictamen-correcciones.md` el grupo "Dictamen c-144 - Procedencia real y ausencia de preproduccion": mapeo de T01-T07, evidencia (commits `1368fd8`, `a76851e`, `d6bb474`; directorio inexistente) y la seccion de reconciliacion con c-130/c-142; verificar que cada T01-T07 figura en el grupo

## 5. Render, compilacion y validacion

- [x] 5.1 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `python "docs/Tesis/v10 (IA)/build_tesis_para_agente.py"` desde la raiz del repositorio; verificar que el render no contiene "100 incidentes representativos", "sin exposición al corpus de validación" ni "prompt_gemini_history"
- [x] 5.2 Compilar desde `docs/Tesis/v10 (IA)/paper/` con `latexmk -xelatex main.tex`; verificar ausencia de errores fatales y `grep -c "undefined" main.log` == 0 para referencias y citas
- [x] 5.3 Registrar el conteo de paginas (`\@abspage@last` en `main.aux`) y su diferencia con la linea base de 1.3 en `dictamen-correcciones.md`, para la decision de tope de la release
- [x] 5.4 Ejecutar `openspec validate c-144-declarar-procedencia-real-y-ausencia-de-preproduccion --strict` sin errores
