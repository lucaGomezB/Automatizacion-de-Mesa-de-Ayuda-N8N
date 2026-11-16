# Tasks: Actualizar las respuestas al tribunal y cerrar la entrega

Al final de cada tarea, entre parentesis, el requisito que cumple (nombre corto). `TF` (`tesis-defensa`): «16 respuestas», «Cifras», «Anexo», «Tercera instancia», «Coherencia», «Cotejo». `TD` (`tesis-document`): «Trazabilidad T3», «Cierre», «Condiciones». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Se aplica **al final**, con `c-235`, `c-236`, `c-237` y `c-238` ya aplicados. Gobernanza **MEDIA** (documentacion y prosa) + **ALTA** (tag, push, publicacion y respuestas de procedencia y autoria). Unico codigo nuevo: el script de cotejo (Strict TDD). Cero llamadas a Gemini. No tocar `App/`, `n8n/`, `evaluation/`, `data/` ni `.engram/`. Solo alias, nunca nombres reales. Nada se commitea, taguea ni pushea sin OK expreso de los autores.

## 0. Precondiciones, linea base y decisiones de autores

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D11) y los dos specs delta; releer `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md` (secciones 5, 7 y 8) y `docs/defensa/respuestas-tribunal.md`.
- [ ] 0.2 **Precondicion (D1):** `openspec list --json` y `openspec status --change <c-235..c-238>` (o su presencia en `openspec/changes/archive/`) confirman que `c-235`, `c-236`, `c-237` y `c-238` estan aplicados. Si alguno no lo esta, **detener** y reportar.
- [ ] 0.3 Registrar las salidas de esos changes que este change consume: texto vigente de la nota de versiones I.1 y del §7.3 (`c-235`); cifras del balance (B como cota superior, termino de revision, tasa, `r`, `c`) y su seccion del memo (`c-236`); subseccion `subsec:declaracion-uso-ia` y la seccion 6 de `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` como texto fuente de Q16 (`c-237`); tabla primaria del cap. 8, Anexo K, metodo y lineas base de conteo de su D4 y D6 (`c-238`). Cada valor con su `archivo:linea`.
- [ ] 0.4 Linea base: `git status`, `git rev-parse HEAD`, `git describe --tags`, `compilacion.md` (paginas y SHA-256) y modificaciones preexistentes ajenas (no tocarlas).
- [ ] 0.5 **Red de seguridad:** `cd "docs/Tesis/v10 (IA)" && python verify_citations.py` (`STATUS: PASS`), `python -I docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` (0 fallas) y `python -m pytest docs/Tesis/Correcciones "docs/Tesis/v10 (IA)" -q` (todas en verde). Si algo falla, reportarlo como falla preexistente y no corregirlo aqui.
- [ ] 0.6 Registrar las respuestas de los autores a OQ1 (version), OQ2 (confirmacion del destino de `c-228`/`c-229`/`c-230`/`c-232`: adaptados y posteriores a la entrega, o archivar), OQ5 (versionar la devolucion) y OQ7 (alcance de `knowledge-base/`). Las que falten quedan como pendientes que bloquean solo sus tareas.

## 1. Cotejo de cifras (Strict TDD)

- [ ] 1.1 RED: crear `docs/Tesis/Correcciones/test_cotejar_cifras_respuestas.py` con pruebas que importan `cotejar_cifras_respuestas` (aun inexistente): extraccion de `0,7971`, `73,5 %`, `110/138`, `−0,05` y `2.646`; exclusion de texto entre comillas invertidas, `Q14`, `P3`, `E1`, `O2` y numeros de seccion con `§`; normalizacion de `0{,}5569` y `−`. Ejecutar y ver fallar. (TF «Cotejo»)
- [ ] 1.2 GREEN: crear `docs/Tesis/Correcciones/cotejar_cifras_respuestas.py` (solo lectura, biblioteca estandar) con lo minimo para pasar 1.1. Ejecutar y ver pasar. (TF «Cotejo»)
- [ ] 1.3 TRIANGULAR: pruebas de cifra presente en el ejemplar, cifra ausente (falla con linea), cifra en lista blanca, valor retirado fuera de oracion de retiro (falla) y dentro de oracion de retiro (pasa), resto LaTeX `~\%` (falla), codigo de salida 0/1; generalizar hasta verde. (TF «Cotejo»)
- [ ] 1.4 REFACTOR con pruebas en verde tras cada paso; agregar la CLI (`--respuestas`, `--ejemplar`, `--lista-blanca`) y la docstring de uso, en el estilo de `verificar_matriz_trazabilidad.py`. (TF «Cotejo»)
- [ ] 1.5 Crear `docs/defensa/cotejo-lista-blanca.tsv` (cifra, justificacion) solo con entradas justificadas (fechas y cifras que reproducen el enunciado de una pregunta del tribunal). Correr el cotejo sobre el documento **actual** y el extracto vigente y guardar el informe de linea base (debe marcar Q14, Q15 y los restos LaTeX). (TF «Cotejo»)

## 2. Respuestas a la segunda instancia (M-04)

- [ ] 2.1 Encabezado y nota de alcance: nombrar las dos devoluciones (11-11 sobre `v1.2.18`; 16-11 sobre `v1.5.2`) y la version del ejemplar cotejado; conservar "sin atribucion a un modelo de lenguaje". (TF «16 respuestas»)
- [ ] 2.2 Reescribir Q14 con el balance vigente de `c-236` (c como cota inferior del tramo activo, B como cota superior con el termino de revision, lectura condicional, sin "signo fijado" ni "viabilidad operativa positiva") y la recomendacion al adoptante; verificar que `-18,5`, `-43,9` y `+30,6` no quedan como vigentes. (TF «Coherencia»)
- [ ] 2.3 Reescribir Q15 conciliada con el §7.3 y la nota de versiones I.1 del ejemplar corregido (todas las transferencias que el ejemplar declare); verificar que no afirma "solo 119 y 81" si el ejemplar declara otras. (TF «Coherencia»)
- [ ] 2.4 Reescribir Q16 con el texto fuente de la seccion 6 del inventario de `c-237` y la remision a `subsec:declaracion-uso-ia`; verificar que no queda la oracion de la declaracion reemplazada. (TF «Coherencia»)
- [ ] 2.5 Revisar Q1 a Q13 contra el ejemplar corregido: cada cifra dentro de la muestra (p. ej. `0,7971` = `110/138`, `0,5569`, `147`, `25/147`, `p = 0,28`, `17,0 %`) sigue vigente; cualquier mencion fuera de muestra se retira. (TF «Cifras»)
- [ ] 2.6 Limpiar restos LaTeX (`~\%`, `{,}`, y cualquier `\texttt`/`\ref`) en todo el documento. (TF «Coherencia»)
- [ ] 2.7 Normalizar las lineas "Fuentes:" a la numeracion de capitulos del PDF (D5: `11-aspectos-legales` = cap. 7, `07-resultados` = cap. 8, `08-discusion` = cap. 9, `09-conclusiones` = cap. 10, `10-recomendaciones` = cap. 11) contra `main.toc` o el indice del PDF; corregir Q8, Q9 y Q15. (TF «Coherencia»)

## 3. Respuestas a la tercera instancia (P1 a P12)

- [ ] 3.1 Crear la segunda parte con los cuatro bloques y los 12 encabezados `### Pn. <pregunta>` (5, 3, 2 y 2); verificar `rg -c "^### P" docs/defensa/respuestas-tribunal.md` = 12 y `rg -c "^### Q"` = 16. (TF «Tercera instancia»)
- [ ] 3.2 P6 y P7: respuesta desde el ejemplar corregido (que mide y que no mide `c`; el termino de revision incorporado a B por `c-236`), con fuentes. (TF «Tercera instancia»)
- [ ] 3.3 P8: el balance con la exactitud fuera de muestra ya no es una lectura del ejemplar (validacion retirada); balance vigente como cota superior condicional y recomendacion al adoptante coherente con Q14. (TF «Tercera instancia»)
- [ ] 3.4 P9 y P10: conclusion de eficiencia acotada segun el ejemplar corregido y aporte de la etapa de reglas con cifras dentro de la muestra vigentes; P10 explica, en los terminos de la nota I.1 y de la acotacion que fije `c-235`, que pasa con la comparacion 103/206 tras el retiro. (TF «Tercera instancia»)
- [ ] 3.5 **[COMPUERTA DE AUTORES]** P1 a P5: borrador limitado a "la validacion fuera de muestra se retiro del ejemplar y por que" en los terminos de la nota I.1, seguido de `PENDIENTE-AUTORES(Pn): <dato que falta>`; no afirmar quienes son `E3`/`E4`/`E5`, como se produjeron las marcas, de donde vienen los textos, autorizacion ni correspondencia de sectores. (TF «Tercera instancia»)
- [ ] 3.6 **[COMPUERTA DE AUTORES]** P11 y P12: borrador que remite a la declaracion de `subsec:declaracion-uso-ia` y al inventario de `c-237` con `PENDIENTE-AUTORES(P11)` y `PENDIENTE-AUTORES(P12)`; no atribuir trabajo a ningun autor ni a ningun asistente sin confirmacion. (TF «Tercera instancia»)
- [ ] 3.7 Con el insumo escrito de los autores (OQ3), registrar fecha y texto en el inventario `PENDIENTE-AUTORES` (grupo 4) y redactar la respuesta definitiva de cada P desbloqueada, retirando su marca; cada afirmacion se apoya en el insumo o en el ejemplar. Si el insumo contradice lo que la tesis afirmaba del corpus, la respuesta lo declara de forma directa. Sin insumo, la P queda marcada. (TF «Tercera instancia»)
- [ ] 3.8 Verificar que el documento no contiene nombres reales (buscar los nombres de la ficha de la devolucion) ni atribucion de autoria a un modelo de lenguaje. (TF «Tercera instancia», «16 respuestas»)

## 4. Trazabilidad de la tercera instancia y Anexo I.2

- [ ] 4.1 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la seccion `## Dictamen v10 / v1.5.2 (2026-11-16) - c-239 (devolucion de tercera instancia)` con: change, fecha, observaciones atendidas, archivos afectados, sin cambios, verificacion. (TD «Trazabilidad T3»)
- [ ] 4.2 Matriz `T3/...` de 7 columnas con al menos una fila por K-01, K-02, A-01, A-02, A-03, M-01, M-02, M-03, M-04, B-01, B-02 y B-03 (change `c-235`..`c-239`, `archivo:linea`, ancla, fragmento del texto final, estado); A-02 y B-02 (y M-02 si corresponde) como "no aplica por retiro (c-235)" con fragmento del texto del retiro. (TD «Trazabilidad T3»)
- [ ] 4.3 Filas de estado final de N-07 y N-15 con el change que las cerro; conciliar las filas de la tabla de c-196 (`dictamen-correcciones.md:4530` y `:4538`) con "SUPERADA por c-239" o nota de cierre, sin borrar historia. (TD «Trazabilidad T3»)
- [ ] 4.4 Inventario `PENDIENTE-AUTORES` de P1-P5, P11, P12 con estado y, si lo hubo, fecha y texto del insumo. (TD «Trazabilidad T3», TF «Tercera instancia»)
- [ ] 4.5 `12-anexos.tex:239` (Anexo I.2): agregar la devolucion de tercera instancia del tribunal del 16 de noviembre de 2026 a la enumeracion de revisiones (re-localizar la linea: `c-237` retira el parrafo de L241); no tocar la declaracion de IA de `subsec:declaracion-uso-ia`. Fila de matriz para este cambio. (TD «Trazabilidad T3»)
- [ ] 4.6 Verificar que `12-anexos.tex` no contiene `sec:anexo-respuestas-tribunal` (anexo de respuestas retirado, OQ3 de c-221). (TF «Anexo»)
- [ ] 4.7 Correr `python -I docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py`: 0 fallas e incluye filas de c-239. (TD «Trazabilidad T3»)

## 5. Cierre de la entrega

- [ ] 5.1 Bump a la version de OQ1 en `00-portada.tex:31`, `12-anexos.tex:58` y `:62` (oracion de reemplazo del hash, sin hash de una release previa) y `Bibliography_base.bib:919`; verificar con `rg -n "1\.5\.2"` que no queda mencion vigente en esos loci. (TD «Cierre»)
- [ ] 5.2 Recompilar: `docker run --rm -v "$PWD/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`; 0 errores fatales, 0 referencias o citas indefinidas, 0 etiquetas duplicadas, sin `??` en el PDF. (TD «Cierre»)
- [ ] 5.3 Regenerar `paper/compilacion.md` con `python3 -I docs/Tesis/Correcciones/resumir_registro_compilacion.py --log ... --blg ... --pdf ... --fuente "<descripcion>" --salida ...` (no a mano); `python verify_citations.py` -> `STATUS: PASS`. (TD «Cierre»)
- [ ] 5.4 Conteo de palabras (D8): aplicar el metodo unico de `c-238` (`A` prosa limpia, `B` `wc -w` crudo, `C` paginas y pagina de inicio de los anexos) a la compilacion de cierre frente a la linea base `v1.5.2` (43.241; 50.532; 164); agregar la lectura de comparacion `pdftotext -layout` (cap. 1 hasta antes de "Anexos") sobre `v1.5.2` y el cierre; recontar oraciones de mas de 60 palabras con `sent_c197.py` y `list_long_c197.py`; registrar metodo, valores, variacion y diferencia con el tribunal (~51.900; 85) en el libro mayor de paginas y palabras de la seccion de c-239, sin afirmar que se reproduce el metodo del tribunal. (TD «Cierre»)
- [ ] 5.4b Re-ejecutar `docs/Tesis/Correcciones/contar_uso_asistentes.py` (`c-237`) sobre la ref declarada (D8b: el commit anterior al de contenido de la entrega); si las cifras cambian, actualizar el inventario y `subsec:declaracion-uso-ia` **antes** de la recompilacion de 5.2 y repetir 5.2-5.3. (TD «Cierre»)
- [ ] 5.5 Regenerar `tesis_completa_extraida.txt` y `tesis_para_evaluacion.txt` desde el `main.pdf` de cierre (UTF-8; saltos de pagina = paginas) y `tesis_para_agente.md` con `build_tesis_para_agente.py <version>`; copiar `main.pdf` a `docs/Tesis/tesis_ultima_version.pdf` y verificar SHA-256 iguales. (TD «Cierre»)
- [ ] 5.6 **Cotejo final:** correr `cotejar_cifras_respuestas.py` sobre el documento final y el extracto regenerado: 0 fallas; registrar el resultado en la seccion de c-239. (TF «Cotejo», «Cifras»)
- [ ] 5.7 `README.md:7` a la version nueva; `knowledge-base/11_evaluacion_experimental.md` y `knowledge-base/README.md` segun OQ7 y la spec `project-documentation` (sin cifras fuera de muestra presentadas como vigentes; valores iguales al memo). (TD «Cierre»)
- [ ] 5.8 Registrar el destino confirmado en OQ2 para `c-228`, `c-229`, `c-230` y `c-232`: por defecto quedan activos, adaptados y sin tareas aplicadas, para ejecutarse despues de la entrega; solo si los autores descartan alguno, `openspec archive <name> --skip-specs` con nota "NO REALIZADO: premisas retiradas por K-01". Comprobar que ninguno aplico tareas ni toco el ejemplar; verificar con `openspec list --json`. (TD «Cierre»)
- [ ] 5.9 `CHANGES.md`: verificar que existen y estan al dia las entradas `### [C-235]` a `### [C-238]` (cada change agrega la suya; completar solo lo que falte, p. ej. el estado final), agregar `### [C-239]` (patron C-227..C-234: estado, objetivo, scope, specs, dependencias, governance, leer antes), el destino de c-228/c-229/c-230/c-232 y una linea "Actualizacion <fecha> (entrega <version>, tercera instancia)"; sin emojis ni marcas de verificacion. (TD «Cierre»)

## 6. Condiciones del tribunal, checkpoint y release

- [ ] 6.1 Checklist de condiciones (D9) en la seccion de c-239: K-01 (busquedas de `0,6893`, `142/206`, `206 casos`, `fuera de muestra` sobre `sections/*.tex` y el extracto: solo en la nota de versiones I.1), K-02 (§7.3 con todas las transferencias; textos de la tercera organizacion fuera de la tesis; destino en el repositorio publico segun `c-235`) y comunicacion al director como dato de autores (OQ6). (TD «Condiciones»)
- [ ] 6.2 Si OQ5 lo autoriza, preparar el versionado de la devolucion de tercera instancia (`.md` y `.pdf`) para el commit de contenido. (TD «Trazabilidad T3»)
- [ ] 6.3 **[CHECKPOINT ALTA]** Presentar a los autores: diff, compilacion, conteos, checklist 6.1, inventario `PENDIENTE-AUTORES` y OQ4. Solicitar autorizacion expresa para commitear y cortar el tag anotado. Registrar la decision literal. (TD «Cierre», «Condiciones»)
- [ ] 6.4 Con autorizacion: commit de contenido (bump + recompilacion + derivados), tag anotado sobre ese commit; commit siguiente que consigna el hash completo en el Anexo B, recompila, regenera `compilacion.md`, extractos y la copia de entrega (byte a byte igual a `main.pdf`); verificar `git rev-parse <tag>^{commit}` contra el Anexo B y que ningun tag previo se movio (`git tag -l "v1.*"`). Sin autorizacion, cerrar sin tag y registrarlo. (TD «Cierre»)

## 7. Verificacion de cierre

- [ ] 7.1 `git diff --stat` (o `git diff --name-only <base>..HEAD`): no cambiaron `App/`, `n8n/`, `evaluation/`, `data/` ni `.engram/`; solo los archivos del Impact.
- [ ] 7.2 `python -m pytest docs/Tesis/Correcciones "docs/Tesis/v10 (IA)" -q` en verde (incluye `test_cotejar_cifras_respuestas.py`); `verify_citations.py` PASS; `verificar_matriz_trazabilidad.py` 0 fallas; cotejo 0 fallas.
- [ ] 7.3 `rg -c "^### Q" docs/defensa/respuestas-tribunal.md` = 16, `rg -c "^### P"` = 12; `rg -n "~\\\\%|\{,\}" docs/defensa/respuestas-tribunal.md` sin coincidencias; inventario `PENDIENTE-AUTORES` coherente con las marcas del documento.
- [ ] 7.4 `openspec validate c-239-actualizar-las-respuestas-al-tribunal-y-cerrar-la-entrega --strict` pasa (registrar el codigo de salida).
- [ ] 7.5 No pushear ni publicar sin instruccion de los autores; `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` (nunca `--all`) queda a cargo del orquestador.
- [ ] 7.6 Guardar en Engram el resumen del apply (`opsx/c-239-actualizar-las-respuestas-al-tribunal-y-cerrar-la-entrega/apply`): version, conteos, cotejo, matriz, pendientes de autores y decision del tag.
