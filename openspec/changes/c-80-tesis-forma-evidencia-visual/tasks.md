# Tasks: c-80 — Forma y evidencia visual

> Convencion de rutas: `S = docs/Tesis/v9 (IA)/paper/sections`;
> `F = docs/Tesis/v9 (IA)/paper/figures`; `D = docs/diagrams`.
> Verificacion de texto: `rg` sobre `S` (sin compilador LaTeX local; los `.bak` no
> se editan ni se cuentan).
> Recompilacion: Overleaf (tarea final). No se edita `App/**`, ni c-76/c-77/c-78,
> ni `CHANGES.md`, ni `docs/Tesis/Correcciones/dictamen-correcciones.md`.
>
> **Orden de aplicacion (D-ORDER):** ejecutar este change DESPUES de c-76, c-77 y
> c-78. Comparte `S/08-discusion.tex` y `S/09-conclusiones.tex` con ellos.

## 1. F1 — Ortografia y portada

- [ ] 1.1 Sustituir contextualmente `diseñó` -> `diseño` (21 casos) en `S`; verificar con `rg -n "diseñó" S` sin coincidencias.
- [ ] 1.2 Sustituir `completó` -> `completo` (13 casos adjetivales) en `S`; verificar con `rg -n "completó" S` sin coincidencias.
- [ ] 1.3 Sustituir `aquéllos` -> `aquellos` (7 casos) en `S`; verificar con `rg -n "aquéllos" S` sin coincidencias.
- [ ] 1.4 Sustituir los sustantivos `desarrolló` -> `desarrollo` en `S` (incluye `00-resumen.tex:9`, `04-marco-metodologico.tex:8,87,98`, `06-implementacion.tex:8`, `08-discusion.tex:16`, `12-anexos.tex:25,27,47`) PRESERVANDO los 2 verbos legitimos `00-resumen.tex:11` y `06-implementacion.tex:87`. Verificar con `rg -n "desarrolló" S` = exactamente 2 coincidencias, ambas en contexto "se desarrolló".
- [ ] 1.5 Corregir tildes de la portada `S/00-portada.tex` en lineas 8, 11, 13, 19 y 27 ("TECNOLOGICA", "Programacion", "Automatizacion", "Tecnico"/"Programacion", "Republica"). Verificar con `rg -n "TECNOLOGICA|Programacion|Automatizacion|Republica" S/00-portada.tex` sin coincidencias sin tilde.
- [ ] 1.6 Normalizar tildes de los titulos de seccion (`\section`/`\subsection`) de los `.tex` de `S` (p. ej. `Introduccion` -> `Introducción`). Verificar listando `rg -n "^\\(section|subsection)\{" S` y revisando cada titulo.

## 2. F6 — Version de N8N consistente

- [ ] 2.1 Retirar en `S/05-arquitectura.tex:21` el parentetico "version estable mas reciente; la version 1.62 no se encuentra disponible en Docker Hub al momento del despliegue" y dejar "Motor N8N~2.11.2 desplegado en contenedor Docker autoalojado". Verificar con `rg -n "1\.62|Docker Hub" S/05-arquitectura.tex` sin coincidencias.
- [ ] 2.2 Retirar en `S/06-implementacion.tex:10` la misma acotacion y dejar "N8N~2.11.2" en la lista de versiones. Verificar con `rg -n "1\.62|Docker Hub" S/06-implementacion.tex` sin coincidencias.
- [ ] 2.3 Reconciliar la version: confirmar que 5, 6 y `S/12-anexos.tex:37` citan `2.11.2`. Verificar con `rg -n "2\.11\.2|1\.62" S` (solo 2.11.2, cero 1.62).
- [ ] 2.4 Actualizar `D/despliegue.md`: retirar Redis (fuera del stack desde c-62) y confirmar N8N 2.11.2 antes de renderizar la figura 1. Verificar con `rg -n "Redis|2\.11\.2" D/despliegue.md`.

## 3. F4 — Composicion uniforme de tablas

- [ ] 3.1 Agregar `\small` a las tablas que carecen de el: `tab:capas` (`S/05-arquitectura.tex:12`), `tab:api` (`:92`), `tab:tiempos` (`S/07-resultados.tex:12`), `tab:matriz` (`:42`) y `tab:metricas` (`:61`). Verificar con `rg -c "\\\\begin\{table\}" S` y `rg -c "\\\\small" S` (iguales por archivo).
- [ ] 3.2 Poner en `raggedright` la primera columna de prosa de `tab:capas` (`S/05-arquitectura.tex:16`) y las columnas `p{}` planas con texto de `tab:comparativa` (`S/03-estado-del-arte.tex:40`), `tab:variables` (`S/04-marco-metodologico.tex:26`), `tab:tiempos` (`S/07-resultados.tex:16`). Verificar con `rg -n "raggedright" S/05-arquitectura.tex S/03-estado-del-arte.tex S/04-marco-metodologico.tex S/07-resultados.tex`.
- [ ] 3.3 Revisar que las columnas numericas de `tab:matriz` y `tab:metricas` (`S/07-resultados.tex`) mantengan su consistencia y que sus encabezados de texto no queden justificados. Verificar por inspeccion del fuente.

## 4. F5 — Deduplicacion de parrafos

- [ ] 4.1 Par 1.1/2.1: reducir el parrafo ITSM de `S/01-introduccion.tex:8,10` a contextualizacion breve con remision al Capitulo~2; el marco teorico `S/02-marco-teorico.tex:10,12` es el dueno de la definicion de Galup2009. Verificar con `rg -n "alinear la operacion tecnologica con los objetivos del negocio" S/02-marco-teorico.tex` presente y ausente en `S/01-introduccion.tex`.
- [ ] 4.2 Par 5.3/6.3: el cap5 describe la orquestacion conceptualmente y remite a 6.3; quitar de `S/05-arquitectura.tex:44` la descripcion operativa duplicada de `S/06-implementacion.tex:39,41`. Verificar comparando ambos parrafos.
- [ ] 4.3 Frase "camino de clasificacion unico": conservarla una sola vez (`S/05-arquitectura.tex:60`) y dejar que `S/06-implementacion.tex:44` remita. Verificar con `rg -n "camino de clasificacion" S` = 1 coincidencia.
- [ ] 4.4 Par 8.1/9.1: reescribir `S/09-conclusiones.tex:12,24` para sintetizar sin repetir frases de `S/08-discusion.tex:8,10,14` (articular con 5.7). Verificar comparando ambos parrafos.

## 5. F7 — Afirmaciones respaldadas por la evidencia

- [ ] 5.1 En `S/08-discusion.tex:8` rebajar "superan ampliamente" a la evidencia (89~% y 92~%, `07:10,40`). Verificar con `rg -ni "superan ampliamente" S/08-discusion.tex` sin coincidencias.
- [ ] 5.2 En `S/08-discusion.tex:10` reformular "valida la hipotesis subsidiaria" -> "es consistente con la hipotesis subsidiaria". Verificar con `rg -ni "valida la hipotesis" S/08-discusion.tex` sin coincidencias.
- [ ] 5.3 En `S/08-discusion.tex:12` reformular "consecuencia deseable" -> "consecuencia observada de la automatizacion". Verificar con `rg -ni "consecuencia deseable" S/08-discusion.tex` sin coincidencias.
- [ ] 5.4 En `S/08-discusion.tex:14` reformular "materializa el esquema human in the loop buscado" -> "es consistente con el esquema human in the loop" (9,5~%, `07:86`). Verificar con `rg -ni "materializa el esquema" S/08-discusion.tex` sin coincidencias.
- [ ] 5.5 En `S/08-discusion.tex:16` reformular "garantia metodologica que no todos los trabajos del area documentan..." a la practica propia sin comparar con terceros. Verificar con `rg -ni "no todos los trabajos" S/08-discusion.tex` sin coincidencias.
- [ ] 5.6 En `S/09-conclusiones.tex:6,12,16,18` retirar/rebajar "cumplido satisfactoriamente", "supero con holgura", "no deja espacio para la duda razonable", "resultado poco frecuente", "trasciende lo meramente estadistico" y "activo que excede" a formulaciones sostenidas por `07:30,34,40,59,86`. Verificar con `rg -ni "satisfactoriamente|con holgura|duda razonable|poco frecuente|trasciende lo meramente|activo que excede" S/09-conclusiones.tex` sin coincidencias.
- [ ] 5.7 Confirmar que las cifras y citas conservadas son exactas y que no se introducen referencias nuevas (eso es c-78). Verificar con `rg -n "92~\\\\?%|89~\\\\?%|0,919|9,5~\\\\?%" S/08-discusion.tex S/09-conclusiones.tex`.

## 6. F2 — Figuras (las 8)

- [ ] 6.1 Figura 1 (despliegue): renderizar `D/despliegue.md` con `mmdc -i ... -o F/despliegue.png -b white -s 2`. Verificar que `F/despliegue.png` existe y no muestra `\n` visibles.
- [ ] 6.2 Figura 2 (secuencia): renderizar `D/secuencia.md` a `F/secuencia.png`. Verificar existencia y legibilidad.
- [ ] 6.3 Figura 3 (ER): crear `D/er_modelo_datos.md` con `erDiagram` de las 7 entidades y renderizar a `F/er_modelo_datos.png`. Verificar que las 7 entidades y sus relaciones figuran.
- [ ] 6.4 Figura 4 (flujo N8N): capturar la UI N8N (`:5678`) con `n8n/workflow.json` importado y guardar `F/flujo_n8n.png`. Contingencia: diagrama esquematico rotulado como reconstruccion.
- [ ] 6.5 Figura 5 (panel admin): capturar `App/Frontend` (panel de administracion) a `F/panel_admin.png`. Verificar que se distingue listado/cola de revision.
- [ ] 6.6 Figura 6 (dashboard): capturar el dashboard ReCharts de `App/Frontend` a `F/dashboard.png`. Verificar que se ven las visualizaciones.
- [ ] 6.7 Figura 7 (boxplot): crear `scripts/figures/boxplot_tiempos.py` que lea `data/corpus_evaluacion_pseudonimizado.json` (`tiempo_manual_s`, `tiempo_automatizado_s`) y emita `F/boxplot_tiempos.pdf`; verificar que `n` y medianas son coherentes con `07:10`. Si los tiempos automaticos estan vacios, usar la fuente alternativa de `design.md` D-F2 y documentarlo.
- [ ] 6.8 Figura 8 (matriz de confusion): crear `scripts/figures/matriz_confusion.py` que grafique la matriz `[[76,4,2],[3,58,3],[2,2,50]]` a `F/matriz_confusion.pdf`; verificar totales 82/64/54 y 200.
- [ ] 6.9 Incrustar las 8 figuras con entornos `figure` (`\includegraphics`, `\caption`, `\label`) en sus ubicaciones: 1-2 -> 5.1/Anexo A; 3 -> 5.6/Anexo C; 4 -> 6.3/Anexo E; 5-6 -> 6.8; 7 -> 7.1; 8 -> 7.2. Verificar con `rg -c "includegraphics" S` (>= 9: 1 previa + 8 nuevas, segun reutilizacion).

## 7. F3 — Anexos con contenido real

- [ ] 7.1 Anexo A (`S/12-anexos.tex:5`): embeber las figuras de despliegue y secuencia; corregir la nota falsa "se mantienen en formato editable (.drawio)" (son Mermaid en `D/`). Verificar con `rg -n "includegraphics|drawio" S/12-anexos.tex`.
- [ ] 7.2 Anexo B (`:17`): agregar un `lstlisting`/`verbatim` con el arbol de directorios del repositorio. Verificar con `rg -n "lstlisting|verbatim|tree" S/12-anexos.tex`.
- [ ] 7.3 Anexo C (`:23`): embeber la figura ER y/o una `table` con las 7 entidades derivada de `docs/anexo_c_esquema_bd.md`. Verificar con `rg -n "er_modelo_datos|begin\{table\}" S/12-anexos.tex`.
- [ ] 7.4 Anexo D (`:29`): incluir un extracto representativo de `docs/openapi.json` (resumen o ruta+esquema), no el archivo completo. Verificar con `rg -n "openapi|OpenAPI" S/12-anexos.tex`.
- [ ] 7.5 Anexo E (`:35`): embeber la figura 4 y una `table` con los 29 nodos agrupados por etapa. Verificar con `rg -n "flujo_n8n|begin\{table\}" S/12-anexos.tex`.
- [ ] 7.6 Anexo F (`:39`): embeber la tabla de campos del corpus (derivada de `docs/anexo_f_corpus.md`) o un extracto JSON y declarar los 200 casos. Verificar con `rg -n "begin\{table\}|200" S/12-anexos.tex`.
- [ ] 7.7 Anexo G (`:45`): incluir tabla de contenidos o extracto del runbook (`docs/operational-guide.md`). Verificar con `rg -n "verbatim|lstlisting|begin\{table\}" S/12-anexos.tex`.
- [ ] 7.8 Anexo H (NUEVO): incorporar `docs/anexo_h_prompt_gemini.md` (H.1-H.7) como `\section{Especificacion del prompt de Gemini 2.5 Flash}` y referenciarlo desde el texto principal. Verificar con `rg -n "prompt de Gemini|Anexo~H|Anexo H" S`.

## 8. Verificacion final y recompilacion

- [ ] 8.1 Barrido de control: `rg -ni "diseñó|completó|aquéllos|1\.62|superan ampliamente|con holgura|duda razonable" S` sin residuos (salvo los 2 `desarrolló` legitimos).
- [ ] 8.2 Confirmar que las 8 figuras existen en `F/` y que cada una tiene su `\includegraphics`; listar los archivos agregados.
- [ ] 8.3 Recompilar la tesis en Overleaf (`main.tex`, XeLaTeX): PDF sin errores fatales, las 8 figuras renderizan, los anexos A-H aparecen completos, y la longitud no supera las 100 paginas. Registrar el conteo de paginas.
- [ ] 8.4 Ejecutar `openspec validate c-80-tesis-forma-evidencia-visual --strict` y confirmar que pasa.
