## 1. Preparación y fuentes de verdad

- [ ] 1.1 Confirmar los valores de referencia del corpus real en `evaluation/report.md` (73,5 %, 0,5207, matriz 5x5) y en `data/corpus_evaluacion_pseudonimizado.json` (distribución 16/85/67/31/1; canales 66/53/81); verificar que coinciden con el registro `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- [ ] 1.2 Inventariar con `rg` los términos stale (Operaciones, 165, 18,2, 0,919, W=0, 92 %, tres sectores) en `docs/Tesis/v9 (IA)/paper/sections`; verificar que la lista cubre Cap. 4, 7, 8, 00, 01, 05 y 09.
- [ ] 1.3 Verificar la disponibilidad de XeLaTeX/`latexmk` en el entorno y registrar la alternativa (Overleaf) si no está local; dejar constancia del compilador a usar para regenerar `main.pdf`.

## 2. Capítulo 7 — Resultados

- [ ] 2.1 Reemplazar los estadísticos de tiempos por los reales: manual media 61,6 s (mediana 50,0; sd 44,9; rango 10–300) vs. auto media 14,8 s (mediana 12,4; sd 13,1; rango 0,525–65,834); reducción 75,9 %; verificar que Tabla~\ref{tab:tiempos} y su texto reflejan esos valores.
- [ ] 2.2 Reemplazar la prueba de Wilcoxon: reportar W=335, p=2,05e-32, r=0,983 y 12/200 pares invertidos; eliminar toda afirmación "W=0" / "sin una sola excepción"; verificar que la fórmula rank-biserial ya no usa W=0.
- [ ] 2.3 Reescribir la matriz de confusión como 5x5 con los valores de `evaluation/report.md`; verificar que filas y columnas son las cinco categorías canónicas y que los totales suman 200.
- [ ] 2.4 Actualizar métricas por clase y macro (macro-F1 0,5207, micro-F1 0,6654, subset accuracy 0,43, Hamming 0,3586, etapas deterministic 131 / Gemini 69); verificar coincidencia con el reporte.
- [ ] 2.5 Reescribir la distribución por sector (16/85/67/31/1) y el análisis de errores/confusiones con las confusiones reales de la matriz; verificar que no queda la categoría "Operaciones" ni los conteos sintéticos (82/64/54).

## 3. Capítulo 4 — Marco metodológico

- [ ] 3.1 Describir la construcción del corpus real: 200 casos pseudonimizados, cinco sectores canónicos y canales correo/web/teléfono; corregir la distribución por estratos a la real; verificar que no se mencionan "tres categorías" ni "Operaciones".
- [ ] 3.2 Declarar el procedimiento de medición de `tiempo_manual_s`: medición real en vivo durante la atención, cronometrada por el compañero de par, con redondeo hacia arriba; verificar que el texto de la Sección 4.2/4.6 describe el redondeo al alza.
- [ ] 3.3 Ajustar la operacionalización de variables y las referencias a "tres clases objetivo" a cinco clases; verificar que F1 macro y categoría asignada usan el conjunto de cinco sectores.

## 4. Otros capítulos que citan números

- [ ] 4.1 `00-resumen.tex`: actualizar resumen y abstract con tiempos reales (61,6/14,8 s, 75,9 %), exactitud 73,5 %, macro-F1 0,5207, W=335 y cinco sectores; verificar que no quedan 165,3/18,2/89 %/92 %/0,919.
- [ ] 4.2 `01-introduccion.tex`: reemplazar "tres sectores (Sistemas, Operaciones o Soporte Tecnico)" por las cinco categorías canónicas en objetivo, alcance y delimitaciones; verificar ausencia de "Operaciones".
- [ ] 4.3 `05-arquitectura.tex`: corregir la tabla de catálogo de sectores (de tres a cinco) y las menciones de distribución de etapas; verificar ausencia de "Operaciones".
- [ ] 4.4 `08-discusion.tex`: reemplazar reducción 89 %→75,9 %, exactitud 92 %→73,5 %, F1 0,919→0,5207 y los rangos/varianzas de tiempos por los reales; verificar coherencia con Cap. 7 y que no queda "Operaciones".
- [ ] 4.5 `09-conclusiones.tex`: actualizar exactitud global, F1 macro y reducción de tiempo; verificar que las cifras coinciden con el Cap. 7 corregido.

## 5. Anexos y documentación de soporte

- [ ] 5.1 Consolidar A1: verificar que `docs/anexo_f_corpus.md` declara la evaluación sobre el corpus real pseudonimizado y versionado, con nota histórica del sintético.
- [ ] 5.2 Consolidar A2/A3: verificar que `evaluation/README.md`, `evaluation/data/README.md` declaran el corpus versionado en su forma pseudonimizada y que `README.md` referencia `docs/anexo_h_prompt_gemini.md`.
- [ ] 5.3 `docs/anexo_h_prompt_gemini.md`: alinear la versión del modelo a `gemini-3.6-flash` (título y cuerpo); verificar que no se menciona "Gemini 2.5 Flash".
- [ ] 5.4 Verificar que `docs/Tesis/Correcciones/dictamen-correcciones.md` marca A1–A4 como aplicadas, P1.0/P1/P2 como pendientes y registra la decisión de no re-medir; actualizar el estado de P2 a aplicada tras 5.3.

## 6. Compilación y verificación final

- [ ] 6.1 Recompilar la tesis con `latexmk -xelatex main.tex` (o Overleaf XeLaTeX) desde `docs/Tesis/v9 (IA)/paper/`; verificar que `main.pdf` se regenera sin errores fatales.
- [ ] 6.2 Ejecutar `rg -n "Operaciones" "docs/Tesis/v9 (IA)/paper/sections"` y verificar cero coincidencias como sector; confirmar que el PDF no contiene la categoría.
- [ ] 6.3 Verificar con `rg` que no quedan números sintéticos ni afirmaciones W=0 en las secciones; confirmar la sustitución completa.
- [ ] 6.4 Ejecutar `openspec validate c-76-tesis-correcciones-dictamen --strict` y verificar que pasa sin errores.

## 7. T1 — Campaña experimental presentada como realizada

- [ ] 7.1 Barrer `07-resultados.tex` con `rg -n "trabajo futuro|pendiente|se propone|se realizar|a realizar|proxim|futur"` y verificar que ningún pasaje presenta la campaña como pendiente o futura; corregir el lenguaje si aparece.
- [ ] 7.2 Verificar que `docs/anexo_f_corpus.md` declara la campaña como realizada sobre el corpus real (A1) y que su texto no la ubica como trabajo futuro.

## 8. T2 — Anexo "Corpus de validación" apunta al corpus real

- [ ] 8.1 Reescribir la sección "Corpus de validación" de `12-anexos.tex` (l.41): remitir a `data/corpus_evaluacion_pseudonimizado.json` (JSON, pseudonimizado y versionado) y aclarar que `categoría predicha`/`confianza` viven en `evaluation/predicciones.json`; verificar que desaparece la promesa de un CSV de 7 columnas en `evaluation/data/`.
- [ ] 8.2 Ejecutar `rg -n "evaluation/data|7 columnas|siete columnas|formato CSV" "docs/Tesis/v9 (IA)/paper/sections"` y verificar cero coincidencias que declaren el corpus como CSV en `evaluation/data/`.

## 9. T3 — Datos incorrectos en caps 7.2 y 1.6

- [ ] 9.1 `07-resultados.tex` §Matriz de confusión y métricas: reemplazar 92 %, 0,919 y 3 clases por 73,5 %, 0,5207 y cinco clases; verificar coincidencia con `evaluation/report.md`.
- [ ] 9.2 `01-introduccion.tex`: sustituir "tres sectores (Sistemas, Operaciones o Soporte Tecnico)" (l.68) por las cinco categorías canónicas, "Gemini 2.5 Flash" (l.72) por `gemini-3.6-flash` y revisar/ajustar la fecha "junio de 2026"; verificar con `rg -n "tres sectores|Operaciones|Gemini 2.5 Flash"` en el archivo.

## 10. T4 — Distribución de etapas del pipeline y etapa fallback

- [ ] 10.1 `05-arquitectura.tex` (l.58): reemplazar "≈ 62 % / 38 %" por 65,5 % deterministic / 34,5 % Gemini; verificar que no queda "62" ni "38" como reparto de etapas.
- [ ] 10.2 `08-discusion.tex` (l.10): reemplazar "≈ 62 %" por 65,5 %; verificar coherencia con 05-arquitectura.
- [ ] 10.3 `09-conclusiones.tex` (l.12): reemplazar "seis de cada diez" por 65,5 %; verificar ausencia de la expresión stale.
- [ ] 10.4 Documentar la etapa fallback (0 casos) y el orden deterministic → Gemini → fallback en el capítulo de arquitectura; verificar que la etapa queda descrita y no solo omitida.
- [ ] 10.5 Ejecutar `rg -n "62~|38~|62 %|38 %|seis de cada diez|fallback"` en las secciones y verificar que no queda el reparto stale y que fallback aparece documentada.

## 11. T6 — Ventana temporal unificada y anti-Hawthorne

- [ ] 11.1 [RESUELTO] Ventana real confirmada por el autor (2026-10-09): flujo manual jun–ago 2026; automatizado sep–oct 2026 (design D9). Reemplazar en el texto las fechas stale (jul–sep 2025 y "tres días hábiles") por estas.
- [ ] 11.2 `04-marco-metodologico.tex`: unificar la ventana entre 4.4 (población/muestreo) y 4.5 (corrida automatizada) usando la ventana real (manual jun–ago 2026; automatizado sep–oct 2026); eliminar las fechas stale ("trimestre jul–sep 2025" y "tres días hábiles") y describir el diseño como secuencial pareado (mismos 200 casos, manual primero y automatizado después).
- [ ] 11.3 Reconciliar la afirmación anti-Hawthorne en 4.2 y `11-aspectos-legales.tex` (l.28) con el procedimiento efectivo (medición en vivo con conocimiento diferido + `debriefing`); verificar con `rg -n "no fue informado|naturalista|Hawthorne"` que no se sostiene que el operador ignoraba el cronometraje toda la campaña.
- [ ] 11.4 Verificar con `rg -n "trimestre|tres d|2025|julio|junio|agosto|septiembre|octubre|ventana"` en 04-marco-metodologico y 11-aspectos-legales que la ventana declarada es única (jun–ago 2026 / sep–oct 2026) y que no queda "jul–sep 2025".

## 12. T7 — Instrumento único de medición manual

- [ ] 12.1 Unificar la descripción de la planilla de cronometraje en `04-marco-metodologico.tex` (4.2, l.16 y 4.6, l.59): un solo relato (cronometraje en vivo por el par, redondeo al alza); verificar con `rg -n "estimad|exactitud al segundo|sin fracciones"` que no coexisten relatos incompatibles.
- [ ] 12.2 `07-resultados.tex` §Reducción de la intervención humana (7.3, l.84): dejar de derivar la intervención del flujo automatizado de la planilla del flujo manual; sustentarla en los registros del propio flujo automatizado y referir el instrumento manual de forma consistente con 4.6.
- [ ] 12.3 Verificar con `rg -n "planilla"` en `07-resultados.tex` que 7.3 no atribuye la medición de intervención automatizada a la planilla manual.

## 13. T5 — Cobertura cruzada de tiempos (sin acción nueva)

- [ ] 13.1 Verificar que las tareas de tiempo de los caps 7.1, 4.6 y 4.7 quedan cubiertas por las tareas 2.1/2.2/3.2 (P1.0/P1) y que no requieren requisito nuevo; dejar constancia en el registro de correcciones.

## 14. Verificación final extendida (T1–T7)

- [ ] 14.1 Ejecutar el barrido `rg -n "evaluation/data|62~|38~|seis de cada diez|exactitud al segundo|sin fracciones|tres sectores|Gemini 2.5 Flash|trabajo futuro" "docs/Tesis/v9 (IA)/paper/sections"` y verificar cero coincidencias stale del grupo T1–T7.
- [ ] 14.2 Recompilar `main.pdf` con XeLaTeX (Overleaf, no hay toolchain local) y verificar que no hay errores fatales y que el PDF refleja T1–T7.
- [ ] 14.3 Ejecutar `openspec validate c-76-tesis-correcciones-dictamen --strict` y verificar que pasa sin errores tras las extensiones.
