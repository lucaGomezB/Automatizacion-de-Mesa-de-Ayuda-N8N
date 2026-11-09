# Tasks: Atender el dictamen CONEAU sobre v1.2.12

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`B` = `docs/Tesis/v10 (IA)/Bibliography_base.bib`; `F/` = `docs/Tesis/v10 (IA)/paper/figures/`;
`D` = `auditorias/Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`. "inv. N" remite al
inventario de correcciones puntuales de `D`. Las anclas del dictamen están numeradas sobre el
tag `v1.2.12`: localizar siempre por el texto citado (`rg -n`). Numeración compilada: 4.x =
`04`, 5.x = `05`, 6.x = `06`, 7 = `11`, 8.x = `07`, 9.x = `08`, 10.x = `09`, 11.x = `10`. Línea
base: 118 páginas; resumen 239 y abstract 239 palabras (método sobre el `.tex`; 237 con la regla
de c-106), tope 250. No se edita código ni artefactos de `App/`, `n8n/`, `evaluation/` ni
`analisis/`. En la prosa del registro usar "sección N (`archivo.tex`)" (gitleaks).

## 0. Preparación y verificación (solo lectura; bloqueante)

- [ ] 0.1 Confirmar con `git fetch` que `origin/main` contiene el commit del hash de `v1.2.12` (`66dae6e`) y el archivo de c-188; trabajar en `change/c-190-dictamen-coneau-v1-2-12`. Si c-188 no está fusionado, detener y avisar.
- [ ] 0.2 Compilar la línea base en el entorno de registro (`MSYS_NO_PATHCONV=1 docker run --rm -v "<paper>":/workdir texlive-thesis latexmk main.tex`): anotar páginas, `Overfull` (cantidad y máximo) y estado de `verify_citations.py`; guardar `pdftotext` de las referencias en el scratchpad. Safety net: `python C/verificar_matriz_trazabilidad.py` → 0 fallas; `cd C/ && python -m unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` en verde.
- [ ] 0.3 Script descartable en el scratchpad (design D0) que reproduzca desde `evaluation/data/campana/` y el corpus: 147 intervenciones (66/81/0), 25 cambios (14/11/0) y 122 confirmaciones; 85 confirmaciones con consenso y 11 distintas del consenso; 13 cambios con consenso (9/1/3); web 10/53 frente a la referencia original y 7/40 frente al consenso; Wilson de 25/200, 25/147, 28/138 y 53/200; proporción de tiempo 0,5307 (`corpus_campana.json`, 191 casos, 2692,22 s) frente a 0,4811; laxa manual 130/151 (unión de adicionales de E1 y E2) frente a 128/151; `sector_predicho` del export como origen de la salida en vivo telefónica (sidecars telefónicos con sector nulo). **Si una cifra no se reproduce, detener esa recomendación y consultar a los autores.**
- [ ] 0.4 Leer `evaluation/data/campana/registro_sujetos.csv` y la sección "Sujetos" del README de la campaña: fijar quiénes operaron el brazo manual de 2026-10, su rol y si alguno es `T1` (insumo de D2). Leer `evaluation/campana.py` y `analisis/resultados.json:1154-1163,1326-1335` para fijar el `n` y la fórmula del MDE (insumo de D5; valor de control 0,2644 con n − 3 = 107).
- [ ] 0.5 **Decisiones de los autores** (design D1, D2, D5, D7, D9, D10, D11): estado de la sub-hipótesis 2 (A recomendada, B, C); enmascaramiento (A o B según 0.4); MDE (corregir o justificar); presupuesto de páginas; nivel de servicio de la Gemini API (gratuito o pago); Zanzotto (reformular o paginar); repositorios regionales (oración o residuo); glosario frente a desarrollo en el primer uso; procedimiento de consentimiento de E1, E2, O1 y O2. Registrar cada respuesta en `C/dictamen-correcciones.md` (sección de c-190). D1 bloquea el grupo 1; D2 el grupo 2; el nivel de servicio la tarea 9.5; D11 la tarea 8.8.

## 1. A1 — Sub-hipótesis 2 según el denominador de los casos revisables (inv. 1, 2)

- [ ] 1.1 `S/07-resultados.tex:154` (8.3, `subsec:reduccion-intervencion`): declarar que la revisión alcanzó 66 casos de correo y 81 de telefonía y ninguno de los 53 del formulario web, por la regla del reportante; reescribir el estado según D1 con el denominador y el IC de Wilson elegidos (25/147 = 17,0 % [11,8 %; 23,9 %] en la opción A, con 25/200 como dato secundario y su advertencia).
- [ ] 1.2 `S/07-resultados.tex` (8.3, inv. 2): una oración con el cotejo con el consenso (11 de 85 confirmaciones con sector incorrecto según el consenso; 13 cambios con consenso: 9 correcciones, 1 empeoramiento, 3 de error a error), sin lectura causal.
- [ ] 1.3 `S/00-resumen.tex:13` y abstract (inv. 1): estado de la sub-hipótesis 2 con magnitud y denominador; compensar palabras en el mismo resumen (tope 250).
- [ ] 1.4 `S/01-introduccion.tex:34` (1.4) y `S/04-marco-metodologico.tex` (4.7): estado idéntico.
- [ ] 1.5 `S/08-discusion.tex:8` (9.1): estado idéntico en el resumen de la hipótesis principal; revisar la lectura de la intervención en el resto de 9.1.
- [ ] 1.6 `S/09-conclusiones.tex`: párrafo inicial, Tabla 18 (filas del objetivo general y del OE4, `tab:cumplimiento-objetivos`) y síntesis del OE4: estado idéntico; grado del OE4 según D1 ("alcanzado parcialmente", acotado a tiempo y exactitud manual).
- [ ] 1.7 `S/10-recomendaciones.tex:18` (11.3): coherencia con el estado elegido (los requisitos nuevos de la medición van en 10.1).
- [ ] 1.8 `C/numeros-canonicos.md`: entradas nuevas 25/147 [0,1179; 0,2390], 28/138 [0,1443; 0,2776], 53/200 [0,2087; 0,3302], el cotejo con el consenso y el alcance de la revisión por canal, con su fuente; 25/200 se conserva con la advertencia del denominador.
- [ ] 1.9 Verificación: `rg -n "no concluyente" S/` sin coincidencias referidas a la sub-hipótesis 2 con 25/200 como único fundamento (opciones A y B); el mismo estado y denominador en resumen, abstract, 1.4, 4.7, 8.3, 9.1, capítulo 10, Tabla 18 y 11.3.

## 2. A2 — Enmascaramiento de los operadores (inv. 3, 4)

- [ ] 2.1 Según D2 (opción A): `S/04-marco-metodologico.tex:16` (4.2, `subsec:diseno-experimental`): el propósito comparativo se ocultó, a lo sumo, al operador externo; `T1`, autor, lo conocía. Sin datos personales.
- [ ] 2.2 `S/11-aspectos-legales.tex:32` (7.5, sesión de esclarecimiento) y la descripción de la sesión en 7.5: el *debriefing* alcanzó solo al operador que desconocía el propósito.
- [ ] 2.3 `S/04-marco-metodologico.tex:89` (4.8, amenazas) y `S/08-discusion.tex:22` (9.1, explicaciones rivales): incorporar la condición de autor de un operador a la amenaza del efecto Hawthorne, con la dirección del sesgo solo si hay evidencia; sin cálculos nuevos.
- [ ] 2.4 Si D2 resulta en la opción B: corregir en su lugar `S/04-marco-metodologico.tex:55` (4.4), 4.8 y `S/08-discusion.tex` (9.3), y conservar 4.2.
- [ ] 2.5 Verificación: `rg -n "esclarecimiento|debriefing|propósito comparativo" S/` → cada coincidencia es coherente con 4.4, 4.8 y 9.3; ninguna afirma que ambos operadores desconocían el propósito.

## 3. A3 — Nota de la Tabla 19 (inv. 5)

- [ ] 3.1 `S/12-anexos.tex:78` (nota de `tab:configuracion-evaluada-entregada`): reemplazar "solo `docker-compose.yml` difiere, por la imagen derivada de N8N" por la formulación de design D3 (pines sin cambios; cambian `docker-compose.yml`, `docker/n8n/` y 20 archivos del backend y del frontend ajenos a la clasificación), sin agregar altura neta.
- [ ] 3.2 `C/conteos-canonicos-tecnicos.md`: registrar `git diff --stat cda7712 v1.2.12 -- App/ n8n/ docker/ docker-compose.yml` (24 archivos, 1323 inserciones, 75 supresiones) y el `git diff --stat` vacío sobre `App/Backend/requirements.txt`, `App/Frontend/package-lock.json`, `n8n/workflow.json` y `App/Backend/app/config/settings.py`.
- [ ] 3.3 Verificación: `rg -n "solo .*docker-compose" S/12-anexos.tex` = 0.

## 4. B1 — Canal telefónico y modelo de transcripción (inv. 6-9)

- [ ] 4.1 `S/05-arquitectura.tex:50` (5.2, inv. 6): Twilio graba y notifica la grabación al backend, que la transcribe con la Gemini API; retirar "transcrita automáticamente por el servicio de reconocimiento del habla del proveedor y enviada al flujo N8N mediante webhook".
- [ ] 4.2 `S/06-implementacion.tex:74` (6.6, etapa 4, inv. 7): "el webhook de transcripción" → callback de grabación y transcripción en el backend.
- [ ] 4.3 Inv. 8: declarar `gemini-3.5-transcribe` en `S/06-implementacion.tex:50` (6.4), en una fila de la Tabla 19 (valores de `d6bb474` y `cda7712` verificados con `git show`; "no registrado" si no existe) y en el Anexo H; registrar en `C/conteos-canonicos-tecnicos.md`.
- [ ] 4.4 `S/08-discusion.tex` (9.5): declarar que el costo de la transcripción queda fuera del cálculo económico y por qué (una oración).
- [ ] 4.5 Inv. 9: `docs/diagrams/despliegue.md`, arista backend → Gemini API rotulada "clasificación y transcripción"; regenerar `F/despliegue.png` con `npx -y @mermaid-js/mermaid-cli@12.0.0 -i <tmp>.mmd -o <tmp>.png -b white -s 2` (bloque extraído fuera del repo); inspección visual; relación alto/ancho no mayor que la previa en más de un 5 %; registrar versión y dimensiones en `C/conteos-canonicos-tecnicos.md`.
- [ ] 4.6 `S/05-arquitectura.tex:44` (leyenda de `fig:despliegue`): "red Docker" → las redes que la figura dibuja.
- [ ] 4.7 Verificación: `rg -n "reconocimiento del habla del proveedor|webhook de transcripción|red Docker\b" S/` = 0; `rg -n "gemini-3.5-transcribe" S/06-implementacion.tex S/12-anexos.tex` ≥ 1 en cada uno (6.4, Tabla 19 y Anexo H).

## 5. B2 — Procedencia de las cifras de la campaña y MDE (inv. 10-12)

- [ ] 5.1 `S/07-resultados.tex:156` (8.3, inv. 10): declarar que el denominador de la proporción de tiempo (0,5307) usa los tiempos automatizados de la campaña complementaria (`corpus_campana.json`, 191 casos) y resolver el anacoluto en la misma reescritura (C1).
- [ ] 5.2 `S/07-resultados.tex:249` (8.7, inv. 11): origen de la salida en vivo telefónica (`sector_predicho` del export de intervenciones; sidecars con sector nulo), predicción que usa el McNemar (caché) y definición del conjunto laxo del brazo manual (consenso + unión de adicionales de E1 y E2).
- [ ] 5.3 `S/07-resultados.tex:251` (8.7, inv. 12): MDE del Spearman según D5 (0,264 con n = 110 si 0.4 lo confirma, o 0,2834 con el `n` y la fórmula que lo producen); actualizar `C/numeros-canonicos.md:851` con la fuente; no editar `analisis/resultados.json` (declarar la discrepancia si la hay).
- [ ] 5.4 `S/08-discusion.tex` (9.6, Tabla 16): unificar el Δt del balance laxo máximo (+138,0 con 43,8 frente a +138,1 con 43,82) con el que la tabla declara usar; registrar el redondeo en `C/numeros-canonicos.md`.
- [ ] 5.5 Verificación: `rg -n "corpus_campana|sector\\\\_predicho" S/07-resultados.tex` ≥ 1; recálculo del MDE impreso con la fórmula declarada coincide a cuatro decimales.

## 6. B3 — Rótulos temporales y matiz de 4.5 (inv. 13-15)

- [ ] 6.1 `S/04-marco-metodologico.tex:65` (4.5, inv. 13): matizar "clasificador congelado … métricas comparables" con la regla del reportante activa y las 13 diferencias entre la salida en vivo y la caché; "comparables" se acota a las métricas sobre la caché.
- [ ] 6.2 Inv. 14: "posterior a las corridas de la campaña" → "posterior a la campaña 2026-10" en `S/02-marco-teorico.tex` (2.4), `S/05-arquitectura.tex:68` (5.5), `S/06-implementacion.tex:40` (6.3) y `S/11-aspectos-legales.tex:36` (7.5).
- [ ] 6.3 Inv. 15: editar las fuentes Mermaid de `componentes` y `secuencia` en `docs/diagrams/` ("posterior a la campaña de medición" / "posterior a la campaña" → "posterior a la campaña 2026-10") y regenerar `F/componentes.png` y `F/secuencia.png` con el pipeline de 4.5; inspección visual y control de relación alto/ancho.
- [ ] 6.4 `C/dictamen-correcciones.md`: corregir la afirmación previa (c-187/c-188) de que esos rótulos estaban solo en las leyendas.
- [ ] 6.5 Verificación: `rg -n "posterior a las corridas de la campaña|posterior a la campaña de medición" S/ docs/diagrams/` = 0.

## 7. B4 — Formulaciones coherentes con la evidencia (inv. 16-18)

- [ ] 7.1 `S/01-introduccion.tex:66` (1.6, inv. 16): reemplazar "validación rigurosa … doble etiquetado independiente" por una formulación coherente con 4.4 y 9.3 (dentro de la muestra; analista autor; acuerdo moderado).
- [ ] 7.2 `S/00-resumen.tex:15` y abstract (inv. 17): "confirman" → "respaldan"; "confirm" → "support".
- [ ] 7.3 `S/09-conclusiones.tex:23` (Tabla 18, OE1, inv. 18): "reintentos idempotentes de la configuración entregada".
- [ ] 7.4 Verificación: `rg -n "validación rigurosa|confirman la viabilidad|confirm the" S/` = 0.

## 8. C1 — Forma del documento (inv. 19-25 y residuos de la sección 1 del dictamen)

- [ ] 8.1 `S/08-discusion.tex:42` (9.3, inv. 19): "siete limitaciones" → "ocho" (o el número que resulte tras 2.4).
- [ ] 8.2 `S/09-conclusiones.tex:26` (Tabla 18, OE4, inv. 20): quitar la repetición de "exactitud del brazo manual".
- [ ] 8.3 `S/00-glosario.tex` (inv. 21): según D10, agregar TI, URL, E2E, MDE y NB, LR, DT (Tabla 1) y desarrollar en el primer uso VIS, HS256 y CA, o agregarlas todas; unificar TI/IT; mantener el orden de las columnas y actualizar el comentario de cabecera (81 → N entradas). Verificar con `rg -w` que cada sigla agregada tiene uso y que ninguna queda sin definir.
- [ ] 8.4 `S/00-portada.tex:30` (inv. 22): fecha de la release `v1.2.13`.
- [ ] 8.5 Inv. 23: retirar `F/matriz_confusion.pdf` del directorio de figuras (con `git rm`); anotar en `C/conteos-canonicos-tecnicos.md` que `scripts/figures/matriz_confusion.py` puede regenerarlo fuera de `figures/`; verificar `rg -n "matriz_confusion" S/` = 0.
- [ ] 8.6 `S/12-anexos.tex` (Anexo B, inv. 24): una oración que nombre `paper/compilacion.md` y `C/verificar_matriz_trazabilidad.py`, que la Tabla 23 atribuye al anexo (cierra además el residuo B7: `main.log` no versionado, cubierto por `compilacion.md`).
- [ ] 8.7 `S/07-resultados.tex:156` (8.3): confirmar que el anacoluto quedó resuelto en 5.1.
- [ ] 8.8 `S/11-aspectos-legales.tex:34` (7, inv. 25): según D11, describir cómo se informó y consintió a E1, E2, O1 y O2, o declarar que no se registró; sin datos personales.
- [ ] 8.9 Presupuesto de páginas (sección 1 del dictamen): según D7, entrada fechada en el libro mayor de `C/dictamen-correcciones.md` con el total, el exceso sobre 100 y la decisión de los autores.
- [ ] 8.10 Verificación: `rg -n "siete limitaciones" S/` = 0; `rg -n "8 de noviembre de 2026" S/00-portada.tex` = 0; `ls F/matriz_confusion.pdf` falla.

## 9. C2 — Bibliografía y fuente de precios (inv. 26-30)

- [ ] 9.1 `S/02-marco-teorico.tex` (2.4, inv. 26): según D9, reformular la atribución a Zanzotto (2019) como inferencia de los autores apoyada en *HitAI*, o citar la página exacta si se accede al texto completo; registrar.
- [ ] 9.2 `S/02-marco-teorico.tex` (2.5) y `S/08-discusion.tex` (9.2, inv. 27): "discrimina poco" → "predecir las fallas sigue siendo un desafío"; conservar sobreconfianza y concentración en la parte alta.
- [ ] 9.3 `S/02-marco-teorico.tex:12` (2.1, inv. 28): punto único de contacto con `OGC2011_itil`; Galup queda solo para la caracterización de ITSM.
- [ ] 9.4 `S/08-discusion.tex:66` (9.5, inv. 29): verificar la página de precios de la Gemini API (título, URL, fecha de consulta, precios de `gemini-3.6-flash`: 0,75/3,75 USD por millón hasta el 31-12-2026; 1,50/7,50 desde el 1-1-2027), agregarla a `B` y citarla; retirar `Google2026_vertex_pricing` si queda sin uso.
- [ ] 9.5 `S/11-aspectos-legales.tex` (7, inv. 29): declarar el nivel de servicio de la Gemini API (dato de los autores, 0.5) y su consecuencia sobre el uso de los datos transferidos según la página citada; si fue gratuito, propagar a la transferencia internacional y a 9.6 si corresponde.
- [ ] 9.6 `B` (inv. 30): URL de `Zendesk2026_help_desk` (ficha de Zendesk Suite, verificada) y del Decreto 1558/2001 (argentina.gob.ar); `Ramya` en IEEE CSITSS 2018, pp. 221-227, con DOI verificado en Crossref; Kerby (2014) con localizador 3:11.IT.3.1; Efron y Tibshirani con año y DOI de la misma edición (Crossref); FrugalGPT en TMLR solo si OpenReview lo confirma (si no, arXiv). Cada cambio con su verificación en la tabla de fuentes del registro.
- [ ] 9.7 Verificación: `python verify_citations.py` (desde `docs/Tesis/v10 (IA)/`) PASS; `main.blg` sin WARN/ERROR; `rg -n "Galup2009_itsm" S/02-marco-teorico.tex` no junto a "punto único de contacto"; `rg -n "vertex" -i S/08-discusion.tex` = 0.

## 10. Residuos sin recomendación propia

- [ ] 10.1 `S/10-recomendaciones.tex` (11.3, `subsec:medicion-intervencion`; sección 8 del dictamen): agregar los dos requisitos de design D8 (revisión de todos los canales o muestra aleatoria por canal; cotejo con referencia independiente), compactos.
- [ ] 10.2 Repositorios regionales (sección 4 del dictamen): según D9, una oración en el protocolo de revisión de `S/03-estado-del-arte.tex` que declare la ausencia de SciELO, Redalyc y JAIIO como limitación, o registro como residuo aceptado en `C/dictamen-correcciones.md`.
- [ ] 10.3 ISBN (sección 9 del dictamen): registrar en `C/dictamen-correcciones.md` la decisión de no agregarlos (APA 7 no los exige), salvo que los autores decidan lo contrario.
- [ ] 10.4 Verificación: `rg -n "todos los canales|referencia independiente" S/10-recomendaciones.tex` ≥ 1.

## 11. Registro y Anexo I

- [ ] 11.1 `C/dictamen-correcciones.md`: sección "Dictamen v10 / v1.2.12 (2026-11-09) - c-190" con la matriz de 7 columnas (Rec | Síntesis | Change | Archivo:línea | Ancla | Fragmento verificable | Estado): una fila por A1-A3, B1-B4, C1-C2 y por cada ítem 1-30 del inventario, más los residuos del grupo 10; decisiones de 0.5; tabla de fuentes de 9.4-9.6; libro mayor de páginas y palabras.
- [ ] 11.2 `S/12-anexos.tex` (`sec:anexo-trazabilidad`): frase de cabecera "seis dictámenes … hasta el 8 de noviembre" → siete, hasta el 9 de noviembre de 2026; cuarta tabla `tab:anexo-trazabilidad-0911` (Rec. | Change | Secciones) con A1-A3, B1-B4 y C1-C2 (`c-190`, con `\autoref` a las secciones y tablas tocadas); sin números de línea; `\small` y filas de una línea para no agregar altura neta.
- [ ] 11.3 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py` (no vacío).
- [ ] 11.4 Verificación: `python C/verificar_matriz_trazabilidad.py` → 0 fallas; `cd C/ && python -m unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` en verde.

## 12. Compilación y release

- [ ] 12.1 Recompilar en el entorno de registro: 0 errores, 0 referencias o citas indefinidas, 0 `multiply defined`, `main.blg` sin WARN/ERROR, 0 `??` en `pdftotext`, `Overfull` no mayor que la línea base de 0.2; `verify_citations.py` PASS.
- [ ] 12.2 Páginas ≤ 118 y resumen y abstract ≤ 250 palabras (regla de c-106 y método sobre el `.tex`); si se supera, recortar prosa en los párrafos tocados y recompilar; si aun así no, detener y consultar. Registrar el libro mayor en `C/dictamen-correcciones.md`.
- [ ] 12.3 Generar `docs/Tesis/v10 (IA)/paper/compilacion.md` con `C/resumir_registro_compilacion.py` (`--fuente "arbol de trabajo sobre <hash corto>"`) y comprobar que su SHA-256 coincide con `sha256sum main.pdf`.
- [ ] 12.4 `openspec validate c-190-atender-el-dictamen-coneau-v1-2-12 --strict --no-interactive`.
- [ ] 12.5 (Orquestador) Commit de contenido de la release en `change/c-190-dictamen-coneau-v1-2-12` (el dictamen `D` ya quedó versionado en el commit de la propuesta de c-190), y tag anotado `v1.2.13` sobre ese commit; `python C/verificar_matriz_trazabilidad.py --rev v1.2.13` → 0 fallas; `git ls-tree v1.2.13 auditorias/` lista `D`.
- [ ] 12.6 (Orquestador) Commit del hash (patrón D7-A de c-187, como `7937efd` → `66dae6e`): consignar el hash completo de `v1.2.13` en el Anexo B y la versión 1.2.13 en `Gomez2026_repositorio` si corresponde, recompilar, regenerar `compilacion.md` para el PDF de ese commit, registrar en `C/dictamen-correcciones.md` y en `CHANGES.md`; verificar con `git diff --stat v1.2.13 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` que solo cambia la línea del hash.
- [ ] 12.7 (Orquestador) `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` (nunca `--all`), commit de `.engram/` y PR contra `main` (nunca push directo); push del tag con confirmación del usuario.
