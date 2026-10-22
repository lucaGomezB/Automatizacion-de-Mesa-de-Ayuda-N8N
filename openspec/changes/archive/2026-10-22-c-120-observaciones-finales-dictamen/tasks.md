## 1. Rotulo de la sub-hipotesis de intervencion humana (obs 1)

- [x] 1.1 En `sections/00-resumen.tex`, `sections/01-introduccion.tex`, `sections/07-resultados.tex` y `sections/09-conclusiones.tex`, reformular las menciones a la sub-hipotesis de intervencion humana para que declaren "no contrastada por ausencia de registro primario" (espanol); alinear la frase del abstract en `sections/00-resumen.tex` a "not tested due to the absence of a primary record"; verificar `grep -rc "no contrastada por ausencia de registro primario" sections/` >= 4 y que no se altera ningun numero canonico. NOTA (reconciliacion post-verificacion): el spec REQ-01 exige la formula en cuatro secciones (resumen, introduccion, resultados y conclusiones); la version inicial omitio resultados y solo la parafraseaba en `07-resultados.tex:138`. Se incorporo la formula exacta alli; el PDF la exhibe en las cuatro secciones.
- [x] 1.2 En `sections/07-resultados.tex:134`, retitular `\subsection{Reducción de la intervención humana}` a `\subsection{Intervención humana en el flujo automatizado}` conservando el label `subsec:reduccion-intervencion`; verificar `grep -c "Reducción de la intervención humana" sections/07-resultados.tex` == 0 y que la entrada del indice refleja el titulo nuevo

## 2. Afirmaciones comerciales y precios (obs 2)

- [x] 2.1 En `sections/03-estado-del-arte.tex` (lineas 12, 14, 22 y la nota de la linea 79) y `sections/01-introduccion.tex:68`, reformular las descripciones de capacidades de plataformas comerciales (Zendesk, Freshdesk, Jira Service Management, ServiceNow, osTicket) como observacion propia declarada del relevamiento, sin inventar referencias academicas; verificar que ninguna afirmacion de capacidad queda enunciada como cita externa sin respaldo
- [x] 2.2 Agregar en `Bibliography_base.bib` las entradas `@online` `DigitalOcean2026_pricing` y `Google2026_vertex_pricing` con `url`, `urldate = {2026-10-19}` y `note` de fecha de consulta; en `sections/08-discusion.tex:58`, citarlas con `\parencite` conservando el calculo de la nota al pie; verificar con `python3 verify_citations.py` cero citas huerfanas y cero entradas sin usar
- [x] 2.3 Verificar el impacto en paginas de 2.1 y 2.2: compilar y confirmar que el total no supera las 101 paginas; si lo supera, aplicar el fallback de D2b (reformular tambien los precios como observacion propia y retirar las dos entradas nuevas) antes de cerrar la tarea

## 3. Umbral de 5.000 casos (obs 4)

- [x] 3.1 En `sections/10-recomendaciones.tex:12`, `sections/08-discusion.tex:56` y `sections/12-anexos.tex:139`, elevar la formulacion del umbral de 5.000 casos a "referencia indicativa de orden de magnitud, no derivada del corpus actual ni de un calculo de potencia estadistica"; verificar `grep -c "5\.000" sections/*.tex` == 3 (sin ocurrencias nuevas) y que las tres quedan rotuladas como indicativas

## 4. Recorte del eje de ASR (obs 5)

- [x] 4.1 En `sections/02-marco-teorico.tex:56-62`, comprimir los tres parrafos del eje de reconocimiento automatico del habla a un unico parrafo que conserve la nocion conceptual, las citas `Rabiner1993_speech_recognition` y `Radford2023_whisper`, y la declaracion de que la transcripcion la provee un servicio externo; verificar `grep -c "Rabiner1993\|Radford2023" sections/02-marco-teorico.tex` == 2 y que `verify_citations.py` sigue sin entradas sin usar

## 5. Fuente del umbral del 85 por ciento (obs 7)

- [x] 5.1 En `sections/01-introduccion.tex:48`, reformular el segundo criterio del umbral del 85~\% para declarar la estimacion de 10 a 15 minutos de reasignacion como estimacion propia de los autores, sin apelar a "mediciones preliminares de la organización" sin fuente; verificar `grep -c "mediciones preliminares de la organización" sections/01-introduccion.tex` == 0 y que no se introduce ningun numero nuevo

## 6. Numeracion del capitulo legal (obs 6)

- [x] 6.1 En `sections/11-aspectos-legales.tex`, degradar la segunda `\section{Cumplimiento normativo y alineación con estándares}` (linea 36) a `\subsection` con label propio y sus cinco `\subsection` (lineas 38, 42, 66, 92, 96) a `\subsubsection` conservando todos los labels; verificar `grep -c "^\\\\section{" sections/11-aspectos-legales.tex` == 1
- [x] 6.2 Actualizar los comentarios internos de numeracion en `sections/11-aspectos-legales.tex:2` y en `main.tex:57-70` para que declaren la posicion real de cada capitulo en el documento compilado; verificar que el PDF numera Resultados como capitulo 8 y Conclusiones como capitulo 10, sin desplazamiento

## 7. Intervalo de confianza del kappa (obs 3, verificacion)

- [x] 7.1 Confirmar que la tabla primaria de doble etiquetado no es recuperable: revisar `docs/Tesis/Correcciones/numeros-canonicos.md` seccion 3.6 y las columnas de `data/Corpus Tesis - Hoja 1.csv` y `data/corpus_evaluacion_pseudonimizado.json`; verificar que no existen columnas de doble etiquetado por analista ni registro por caso en `evaluation/`
- [x] 7.2 Verificar que la tesis declara la no computabilidad del intervalo de confianza del kappa en `sections/04-marco-metodologico.tex:55` (y su consistencia en la linea 87 y en `sections/00-resumen.tex:11`); si la declaracion falta o es ambigua, ajustarla en el `.tex` correspondiente; verificar que no aparece ningun IC numerico del kappa. Si el autor aporta la tabla primaria, calcular el IC por bootstrap con semilla fija y actualizarlo

## 8. Compilacion y verificacion global

- [x] 8.1 Compilar con `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex` y verificar ausencia de errores fatales y de referencias indefinidas en el `.log`
- [x] 8.2 Verificar el presupuesto de paginas: el total del PDF MUST ser <= 101 paginas (criterio duro); registrar el conteo obtenido
- [x] 8.3 Confirmar que no se modifico contenido cientifico, numeros canonicos, las cinco cadenas de categoria, `evaluation/` ni `CHANGES.md`, y que `v1.0.0` no se movio (`git tag -l v1.0.0` y `git diff --stat`)
