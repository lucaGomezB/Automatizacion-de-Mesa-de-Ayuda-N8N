# Tasks: Residuales de forma y bibliografia del dictamen CONEAU sobre v1.2.10

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`B` = `docs/Tesis/v10 (IA)/Bibliography_base.bib`. Cada lugar se identifica por etiqueta y
texto citado; los numeros de linea (medidos en la rama de c-187) son orientativos: relocalizar
con `rg -n "<texto>"`. Numeracion compilada: 4.x = `04`, 6.x = `06`, 7 = `11`, 8.x = `07`,
9.x = `08`. Linea base: PDF del tag `v1.2.11` = 118 paginas; resumen y abstract no se tocan.
No se edita codigo de `App/`, `n8n/` ni `evaluation/`.

## 0. Preparacion (bloqueante)

- [x] 0.1 Confirmar que el PR #72 (c-187, `v1.2.11`) esta fusionado en `main` (`git fetch`; `git log origin/main` contiene el commit del hash de `v1.2.11`); cortar una rama nueva `change/c-188-...` desde `origin/main`. Si no esta fusionado, detener y avisar.
- [x] 0.2 Compilar la linea base en el entorno de registro (`MSYS_NO_PATHCONV=1 docker run ... texlive-thesis latexmk main.tex`) y anotar paginas, `Overfull` y estado de `verify_citations.py`; guardar `pdftotext` de las referencias en el scratchpad para comparar en el grupo 7.
- [x] 0.3 Leer `.agents/SKILLS.md`; para los grupos 3 cargar `python-testing-patterns` (pruebas) y aplicar Strict TDD.

## 1. B4 — Metricas multietiqueta y ejemplos del prompt

- [x] 1.1 Verificar de nuevo (script descartable en el scratchpad) que la evidencia tiene 8 casos con `sectores_adicionales`, todos `deterministic`, y que las metricas dan 0,43 / 0,35858 / 0,66544 con adicionales y 0,44 / 0,35275 / Hamming(5) 0,182 sin ellos (design D1).
- [x] 1.2 `S/04-marco-metodologico.tex` `subsec:analisis-estadistico` (texto "las secundarias, multietiqueta (subset accuracy, Hamming loss y micro-F1)", ~`:79`): una oracion con el conjunto predicho (principal + adicionales, 8 casos de la etapa deterministica) y la normalizacion de la Hamming loss por la union de etiquetas del caso (equivalente a 1 − Jaccard), no por las cinco clases.
- [x] 1.3 `S/07-resultados.tex` `subsec:matriz-metricas` (texto "penalizan estructuralmente una salida forzada a una sola etiqueta", ~`:130`): reemplazar por la descripcion exacta y remitir a `subsec:analisis-estadistico`; cifras intactas.
- [x] 1.4 `C/numeros-canonicos.md`: entrada de verificacion con las cifras alternativas y su comando; ningun valor reemplazado.
- [x] 1.5 `S/05-arquitectura.tex` `subsec:subsistema-clasificacion` ("ejemplos representativos balanceados", ~`:68`) y `S/08-discusion.tex` `subsec:implicancias-practicas` ("ejemplos balanceados", ~`:66`): "un unico ejemplo representativo por sector"; confirmar contra `docs/prompt_gemini.txt` (5 ejemplos) y el Anexo H (`subsec:anexo-estructura-prompt`).
- [x] 1.6 Verificacion: `rg -n "forzada a una sola etiqueta|balanceados" S/` = 0 coincidencias referidas a esas metricas o al prompt.

## 2. B5 — Capturas, despliegue y matriz duplicada

- [x] 2.1 **Decision del usuario** sobre las capturas de 6.8 (design D3: A recomendada, B recapturar). Registrar en `C/dictamen-correcciones.md`.
- [x] 2.2 Segun D3-A: `S/06-implementacion.tex` `subsec:dashboard-analitica`, leyendas de `fig:panel_admin` y `fig:dashboard` (y, si hace falta, la oracion "la pestaña de revisión humana para los casos derivados por el backend"): procedencia (instancia local de desarrollo, captura del 21-10-2026 por c-80, rotulo v1.0.0, 145 incidentes del 2 al 13-10-2026) y explicacion de los 94 casos / 64,8 % como indicador registrado por el backend en esa base, distinto de la regla de confianza evaluada fuera de linea, con `\autoref{subsec:reduccion-intervencion}`. Sin atribuir los 94 a una regla concreta.
- [x] 2.3 `docs/diagrams/despliegue.md`: nodo `FE` → bundle Vite servido por `nginx:alpine` :3000 (sin puerto host); nodo `N8N` → imagen derivada 2.11.2 + parche IMAP (c-182); redes de `docker-compose.yml` (`edge`, `data` interna, automatizacion) en lugar de `mesa_local_default` si cabe sin agrandar la figura (design D4); alinear el texto introductorio.
- [x] 2.4 Regenerar `figures/despliegue.png` con `npx -y @mermaid-js/mermaid-cli@12.0.0 -i <tmp>.mmd -o <tmp>.png -b white -s 2` (bloque extraido a un `.mmd` fuera del repo; design D4); inspeccion visual (sin `\n` literales); relacion alto/ancho no mayor que la previa (1568x1712) en mas de un 5 %; registrar version y dimensiones en `C/conteos-canonicos-tecnicos.md` (seccion de `fig:despliegue`).
- [x] 2.5 `S/07-resultados.tex` `subsec:matriz-metricas`: retirar el entorno `figure` de `fig:matriz_confusion` (~`:101-106`) y "y en la Figura~\ref{fig:matriz_confusion}" (~`:76`); conservar `tab:matriz`. Anotar en `C/conteos-canonicos-tecnicos.md` que `scripts/figures/matriz_confusion.py` y `figures/matriz_confusion.pdf` quedan como artefacto no embebido.
- [x] 2.6 Verificacion: `rg -n "matriz_confusion|Vite dev server" S/ docs/diagrams/despliegue.md` = 0; `rg -c "includegraphics" S/` = 11 (antes 12, incluido el logo).

## 3. B7 — Resumen de compilacion y verificador de trazabilidad (Strict TDD)

- [x] 3.1 **Decision del usuario (no bloqueante)** sobre la forma del registro (design D5: A por defecto). Registrar.
- [x] 3.2 Safety net: `cd C/ && python -m unittest test_verificar_matriz_trazabilidad -v` → 11/11 en verde; `python C/verificar_matriz_trazabilidad.py` desde la raiz → anotar "Filas: 41; fallas: 22" como linea base.
- [x] 3.3 RED: crear `C/test_resumir_registro_compilacion.py` con pruebas de las funciones puras (design D5): conteo de errores `^!`, referencias y citas indefinidas, `multiply defined`, `Overfull` (cantidad y maximo pt), paginas de "Output written on main.xdv (N pages", version del motor y de biber, `WARN`/`ERROR` del `.blg`, SHA-256 de bytes conocidos, salida Markdown determinista; dos casos por comportamiento (limpio / con defectos). Ejecutar: fallan por modulo inexistente.
- [x] 3.4 GREEN + TRIANGULATE + REFACTOR: crear `C/resumir_registro_compilacion.py` (funciones puras + `main(argv)` con `--log --blg --pdf --fuente --salida`, sin red ni subprocesos); pruebas en verde tras cada paso.
- [x] 3.5 RED (verificador, design D6): agregar pruebas para (a) parsear todas las matrices de 7 columnas con "Fragmento verificable" en cualquier seccion (reemplaza la prueba que excluia "Siguiente seccion"), (b) fragmento en otra linea → pasa con aviso "desplazada N -> M", (c) `--estricto` → esa fila falla, (d) fragmento ausente del archivo → falla, (e) estado "SUPERADA por c-NNN" → omitida, (f) resumen por seccion. Ejecutar: las nuevas fallan, las conservadas pasan.
- [x] 3.6 GREEN + TRIANGULATE + REFACTOR en `C/verificar_matriz_trazabilidad.py` (docstring actualizado: cubre los dictamenes del 22-10, 28-10 y 8-11); conservar `--rev` y `--reubicar`; pruebas en verde tras cada paso.
- [x] 3.7 Correr el verificador sobre el arbol; por cada falla, en `C/dictamen-correcciones.md`: actualizar el fragmento al texto vigente que sostiene la misma correccion, o marcar "SUPERADA por c-NNN" si un change posterior reescribio el parrafo a proposito (con la fila del change nuevo cubriendo la recomendacion). Meta: 0 fallas.
- [x] 3.8 `C/dictamen-correcciones.md`: crear la matriz de 7 columnas del dictamen del 8-11 (Rec | Sintesis | Change | Archivo:linea | Ancla | Fragmento verificable | Estado) con filas de c-187 (A1-A5, B1, B2, B3, B6) y de c-188 (B4, B5, B7, C1-C5); completar las de c-188 al final del grupo 10.
- [x] 3.9 Verificacion: `python -m unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` (desde `C/`) en verde; tabla de evidencia TDD (tarea, archivo de prueba, safety net, RED, GREEN, TRIANGULATE, REFACTOR) en el resumen del apply.

## 4. C1 — Fidelidad bibliografica (e item 32)

- [x] 4.1 Galup et al. (2009): `S/01-introduccion.tex` `subsec:planteamiento-problema` ("advierten que los procesos de soporte no automatizados tienden a degradarse ... impacto desproporcionado", ~`:22`) y `S/02-marco-teorico.tex` `subsec:mesa-ayuda-itil` ("advierten que los procesos manuales de soporte tienden a degradarse", ~`:12`): reformular como inferencia de los autores (o citar la pagina si se accede al texto y la afirmacion figura; registrar). Conservar la cita de caracterizacion de `subsec:gestion-servicios-ti` (~`:10`).
- [x] 4.2 Item 32: `S/03-estado-del-arte.tex` ("ha recibido una atención notablemente menor", ~`:56`): rotular como inferencia de los autores a partir de las obras citadas.
- [x] 4.3 Verificar Opitz y Burst (2019), arXiv:1911.03347 (autores, titulo, que definen y distinguen las dos formulas del F1 macro); agregar la entrada a `B` con `eprint`, `url`, `urldate`.
- [x] 4.4 F1 macro: 2.8 (`S/02-marco-teorico.tex`, parrafo de `Sokolova2009_performance_measures`, ~`:78`), `S/04-marco-metodologico.tex` `subsec:metricas-instrumentos` ("media aritmética de los valores F1 de cada clase estimable", ~`:69`) y, si corresponde, `subsec:matriz-metricas`: atribuir la variante empleada a Opitz y Burst y dejar a Sokolova y Lapalme para el promedio macro, con la salvedad de las dos formulas (una frase).
- [x] 4.5 Efecto Hawthorne: verificar en Crossref o catalogo una candidata de design D7 (McCambridge et al., 2014; Adair, 1984; Roethlisberger y Dickson, 1939); agregarla a `B` y citarla en `S/04-marco-metodologico.tex` `subsec:diseno-experimental` (~`:16`); decidir si `HernandezSampieri2018_metodologia` sigue citada alli (si sigue, verificar que se cita en otro lugar o retirarla del `.bib` si queda sin uso).
- [x] 4.6 Verificacion: `rg -n "desproporcionado" S/` sin `Galup2009_itsm`; `rg -n "Opitz" S/ B` >= 1 en cada uno; la cita de Hawthorne resuelve a la entrada nueva.

## 5. C2 — Fuentes de proveedores y normativa

- [x] 5.1 Abrir y verificar cada URL candidata de design D8 (Gemini API terms y, si hace falta, audio; Twilio Programmable Voice; Docker; Jira Service Management; osTicket; Decreto 1558/2001; Disposicion DNPDP 60-E/2016 o la norma vigente de la AAIP), anotando titulo exacto, autor institucional y fecha de consulta. Lo no verificable se omite y se registra.
- [x] 5.2 Agregar las entradas verificadas a `B` (`@online`/`@misc`, `url`, `urldate`), con el estilo de las entradas `@online` existentes; sin inventar datos.
- [x] 5.3 `S/03-estado-del-arte.tex` `subsec:soluciones-comerciales` y Tabla 2 (`tab:comparativa`): citar Jira Service Management y osTicket con `\parencite` como las otras tres plataformas y reemplazar la lista de URL de la nota de fuente por las citas.
- [x] 5.4 `S/11-aspectos-legales.tex` `subsec:marco-normativo` y `subsec:transferencia-internacional`: citar la Gemini API y Twilio Programmable Voice donde se describen las transferencias; precisar (si la redaccion lo deja ambiguo) que Twilio graba y la Gemini API transcribe; citar la normativa del art. 12 en la oracion del instrumento requerido.
- [x] 5.5 `S/06-implementacion.tex` `subsec:entorno-despliegue` (Docker) y `subsec:integracion-canal-telefonico` (Twilio): una cita cada uno, sin agregar prosa.
- [x] 5.6 Registrar en `C/dictamen-correcciones.md` la tabla de fuentes (clave, URL, fecha de consulta, verificada/omitida) y la pregunta abierta Vertex AI frente a Gemini API (design D8).
- [x] 5.7 Verificacion: `python verify_citations.py` (desde `docs/Tesis/v10 (IA)/`) PASS; `rg -n "atlassian.com|osticket.com" S/03-estado-del-arte.tex` = 0.

## 6. C3 — Terminologia y Tabla 1

- [x] 6.1 `S/08-discusion.tex` `subsec:reflexiones-generalizacion` ("condiciones de minimización y pseudonimización", ~`:101`): "minimización y disociación".
- [x] 6.2 Leer el texto abierto de Zangari et al. (2023, doi:10.1016/j.eswa.2023.119984): si informa el idioma de los datasets, consignarlo en la Tabla 1 (`tab:trabajos-academicos`, ~`:46`); si no, "idioma no reportado"; retirar "(texto inaccesible)".
- [x] 6.3 Tabla 1, fila de Paramesh y Shreedhara (~`:44`): "compañero accesible de dos de los tres autores (arXiv:2103.15822)"; verificar los autores de ambas obras.
- [x] 6.4 `Ley25326_2000`: confirmar `date = {2000-10-04}` (sancion) y que ningun `.tex` consigna otra fecha para la ley sin rotularla como promulgacion.
- [x] 6.5 Verificacion: `rg -n "texto inaccesible|de los mismos autores" S/03-estado-del-arte.tex` = 0; `rg -n "pseudonimizaci" S/08-discusion.tex` sin atribucion a la Ley 25.326.

## 7. C4 — Forma de la lista de referencias

- [x] 7.1 **Decision del usuario**: grafia del apellido ("Gomez", recomendado, o "Gómez"); aplicarla a `Gomez2026_repositorio` o a la portada para que coincidan. Registrar.
- [x] 7.2 EMNLP: `booktitle` con el anio en `ahuja2023mega`, `zhang2023multilingual` ("EMNLP 2023") y `xuan2025mmluprox` ("EMNLP 2025"), como `Tian2023_verbalized_confidence` y `Varshney2022_model_cascading`.
- [x] 7.3 PMLR: `Guo2017_calibration`, `Zhao2021_calibrate_before_use` y `Radford2023_whisper` impresas como *Proceedings of Machine Learning Research*, volumen (70, 139, 202 a verificar en proceedings.mlr.press) y paginas, con `url` de PMLR (design D9); comprobar la salida de `biblatex-apa`.
- [x] 7.4 `MosqueiraRey2023_human_in_the_loop`: "{A} state of the art"; `Jurafsky2023_speech_language`: "3.ª"; `mayorrocher2026spanish`: `note = {Publicación anticipada en línea}`.
- [x] 7.5 URL verificadas: `Brown2020_few_shot` y `Vaswani2017_attention` (proceedings.neurips.cc), `Radford2023_whisper` (7.3), `Pedregosa2011_scikit_learn` (jmlr.org), `Powers2011_evaluation` (URL o DOI estable verificado; si no existe, registrarlo).
- [x] 7.6 Comprobar en el PDF que "Şenerkek" (Paket et al.) se imprime; si falta el glifo, corregir la entrada o la fuente.
- [x] 7.7 Verificacion sobre `pdftotext` de las referencias (comparar con 0.2): EMNLP con anio en todas, "Proceedings of Machine Learning Research" con volumen, "A state of the art", "3.ª", "Publicación anticipada en línea", sin "Artículo en prensa"; biber sin advertencias; `verify_citations.py` PASS.

## 8. C5 — Glosario

- [x] 8.1 Verificar las expansiones (NLBSE en la fuente citada en 3; PABAK; RGPD; UTC; GPT; CONEAU) y su uso con `rg -w` en `S/` fuera del glosario y de comentarios.
- [x] 8.2 `S/00-glosario.tex`: agregar CONEAU, NLBSE, PABAK, RGPD, UTC y GPT; retirar UML, FRM y UTN; reordenar las dos columnas conservando el orden alfabetico descendente; actualizar el comentario de cabecera (79 → 82 entradas, siglas agregadas y retiradas por c-188).
- [x] 8.3 Verificacion: cada `\textbf{SIGLA}` del glosario tiene uso en el cuerpo; las seis nuevas existen y las tres retiradas no.

## 9. Item 36 — Cronograma

- [x] 9.1 `docs/diagrams/cronograma.md`, fila "Campaña complementaria de medición" de la tabla de procedencia (~`:74`): "las tablas primarias entre el 2026-11-04 y el 2026-11-08" con remision a `git log -- evaluation/data/campana` (`38392c1`, 8-11). No regenerar `cronograma.png` (la barra es de mes; el texto cambiado no esta en el bloque Mermaid).
- [x] 9.2 Verificacion: `rg -n "2026-11-04 y el 2026-11-06" docs/diagrams/cronograma.md` = 0.

## 10. Anexo I y registro

- [x] 10.1 `S/12-anexos.tex` `tab:anexo-trazabilidad-0811`: reemplazar la fila "B4, B5, B7, C1 a C5 & Change posterior..." por filas `c-188`: B4 (`subsec:analisis-estadistico`, `subsec:matriz-metricas`, `subsec:subsistema-clasificacion`, `subsec:implicancias-practicas`), B5 (`subsec:dashboard-analitica`, `fig:despliegue`, `tab:matriz`), B7 (registro de compilacion y verificador, en el repositorio; remitir a `sec:anexo-repositorio` si corresponde), C1 (`subsec:planteamiento-problema`, `subsec:mesa-ayuda-itil`, `subsec:metricas-instrumentos`, `subsec:diseno-experimental`), C2 (`tab:comparativa`, `subsec:transferencia-internacional`, `subsec:entorno-despliegue`), C3 (`subsec:reflexiones-generalizacion`, `tab:trabajos-academicos`), C4 (Referencias), C5 (Glosario). Ajustar el caption y el parrafo introductorio para nombrar `c-187` y `c-188`. Sin numeros de linea; sin agregar altura neta (fusionar filas si hace falta).
- [x] 10.2 `C/dictamen-correcciones.md`: seccion "Dictamen v10 / v1.2.10 (2026-11-08) - c-188" con la matriz recomendacion → ubicacion → correccion (B4, B5, B7, C1-C5, item 36), las decisiones del usuario (2.1, 3.1, 7.1), la tabla de fuentes de 5.6, el libro mayor de paginas y la remision a `paper/compilacion.md`; completar las filas de c-188 de la matriz de 3.8.
- [x] 10.3 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py` (no vacio).
- [x] 10.4 Verificacion: `rg -n "Change posterior" S/12-anexos.tex` = 0; `python C/verificar_matriz_trazabilidad.py` → 0 fallas.

## 11. Compilacion y release

- [x] 11.1 Recompilar en el entorno de registro (`MSYS_NO_PATHCONV=1 docker run --rm -v "<paper>":/workdir texlive-thesis latexmk main.tex`): 0 errores, 0 referencias o citas indefinidas, 0 `multiply defined`, `main.blg` sin WARN/ERROR, 0 `??` en `pdftotext`, `Overfull` no mayor que la linea base de 0.2; `verify_citations.py` PASS.
- [x] 11.2 Paginas <= 118 (design D10); si se supera, recortar prosa en los parrafos tocados y recompilar; si aun asi no, detener y consultar al usuario. Registrar el libro mayor en `C/dictamen-correcciones.md`. Confirmar que `S/00-resumen.tex` no cambio.
- [x] 11.3 Generar `docs/Tesis/v10 (IA)/paper/compilacion.md` con `resumir_registro_compilacion.py` (`--fuente "arbol de trabajo sobre <hash corto>"`) y comprobar que su SHA-256 coincide con `sha256sum main.pdf`.
- [x] 11.4 `openspec validate c-188-residuales-de-forma-y-bibliografia-del-dictamen-v1-2-10 --strict --no-interactive`.
- [x] 11.5 (Orquestador) Commit de contenido de la release en la rama de c-188 y tag anotado `v1.2.12` sobre ese commit; `python C/verificar_matriz_trazabilidad.py --rev v1.2.12` → 0 fallas. Hecho: tag anotado `v1.2.12` sobre `7937efd063955f787a4fed6c10168b4744de8905` (2026-11-09).
- [ ] 11.6 (Orquestador) Commit del hash (patron D7-A de c-187): consignar el hash completo de `v1.2.12` en el Anexo B y la version 1.2.12 en `Gomez2026_repositorio` si corresponde, recompilar, regenerar `compilacion.md` para el PDF de ese commit, registrar en `C/dictamen-correcciones.md` y en `CHANGES.md` (entrada de c-188); verificar con `git diff --stat v1.2.12 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` que solo cambia la linea del hash. **En curso por el orquestador** (pendiente fuera de este archivo).
- [ ] 11.7 (Orquestador) `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"`, commit de `.engram/` y PR contra `main` (nunca push directo); push del tag con confirmacion del usuario. **En curso por el orquestador** (pendiente fuera de este archivo).
