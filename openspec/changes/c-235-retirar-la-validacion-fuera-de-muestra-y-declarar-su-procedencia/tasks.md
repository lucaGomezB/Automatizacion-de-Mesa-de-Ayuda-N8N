# Tasks: Retirar la validacion fuera de muestra y declarar su procedencia

Al final de cada tarea, entre parentesis, el requisito del change que cumple (nombre corto). Nombres cortos: `TD` (`tesis-document`) «Retiro», «Procedencia» (declaracion en la nota de versiones), «Trabajo futuro», «Eficiencia» (contraste y estado de la hipotesis), «Consistencia», «Ajustes», «Acotadas», «Version», «Balance»; `DV` (`tesis-dictamen-v1-3-0`) «Conclusiones»; `TLB` (`tesis-baseline-integration`) «TLB-04»; `NC` (`tesis-numeros-canonicos`) «Retiro memo», «Robustez»; `OOS` (`evaluation-out-of-sample-validation`) «OOS-026». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Este change **no escribe codigo**: es prosa LaTeX y documentacion. El ciclo TDD estricto NO aplica (no hay logica nueva); la red de seguridad es `verify_citations.py`, la bateria de `rg`, la compilacion de verificacion en un directorio temporal, `sha256sum -c` y la suite de `evaluation/` en verde.

Gobernanza **ALTA**. Cada tarea marcada **[COMPUERTA]** no se ejecuta sin la respuesta escrita de los autores registrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` (tabla de compuertas de c-235, con fecha). Ninguna tarea escribe un hecho de procedencia que los autores no hayan confirmado. Cero llamadas a Gemini. No se tocan `.engram/`, `CHANGES.md`, `c-228`, `c-229`, `c-230` ni `c-232`. Los numeros de linea son de v1.5.2; si una edicion previa del mismo archivo los desplaza, se repuntan por contenido.

## 0. Preparacion y linea base

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D12) y los cinco specs delta; leer las secciones 2, 4, 5, 7 y 8 de `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`; confirmar que no se toca `App/`, `n8n/`, el corpus de 200 casos ni el codigo de `evaluation/`.
- [ ] 0.2 Capturar la linea base: `git status`, `git rev-parse HEAD`, `git describe --tags` (esperado sobre `v1.5.2`), y el conteo de paginas de `docs/Tesis/v10 (IA)/paper/compilacion.md`. Registrar modificaciones preexistentes ajenas (por ejemplo, los archivos de `auditorias/` sin versionar) y no tocarlas.
- [ ] 0.3 **Red de seguridad:** `cd "docs/Tesis/v10 (IA)" && python verify_citations.py` (`STATUS: PASS`); `python -m pytest evaluation -q` (registrar el conteo de pruebas en verde); `sha256sum -c` de `evaluation/data/campana/analisis/SHA256SUMS.txt` y de `evaluation/data/canario/canario.SHA256SUMS.txt` (todo `OK`).
- [ ] 0.4 Inventario de partida: correr `rg -n "fuera de (la )?muestra|arbitrad|\\texttt\{E[345]\}|\b206\b|modelo solo|l[ií]nea de base|corpus independiente|compa[ñn][ií]a financiera|refuerzo" "docs/Tesis/v10 (IA)/paper/sections"` y guardar el listado por archivo:linea; marcar como falsos positivos `03-estado-del-arte.tex` L8, L30, L46, L58, L64 ("arbitrada" = literatura con referato). Este listado es el contrato del retiro.
- [ ] 0.5 Releer los encabezados `3.N` de `docs/Tesis/Correcciones/numeros-canonicos.md` y fijar el primer numero libre (esperado `3.45`). (NC «Retiro memo»)

## 1. Compuertas de autores (CHECKPOINT de gobernanza ALTA)

- [ ] 1.1 **[COMPUERTA]** Presentar a los autores las preguntas P1 a P8 de `design.md` (Open Questions) y registrar sus respuestas literales, con fecha, en la tabla de compuertas de c-235 en `dictamen-correcciones.md`. Sin respuesta a una pregunta, la tarea que depende de ella queda bloqueada y se registra como tal. (TD «Procedencia»)
- [ ] 1.2 **[COMPUERTA]** Registrar la decision OQ2 sobre los artefactos: conservar y re-rotular (A, por defecto) o eliminar (B). (OOS «OOS-026»)
- [ ] 1.3 **[COMPUERTA]** Registrar OQ3 (conservar la fila de 200 casos de `tab:gemini-solo` como descriptiva, o retirar la tabla) y OQ5 (etiqueta del estado de la hipotesis de eficiencia; por defecto "sin contraste limpio"). Si OQ5 cambia la etiqueta, actualizar los deltas de `tesis-document` y `tesis-dictamen-v1-3-0` y volver a correr `openspec validate --strict` antes de seguir. (TD «Eficiencia»)
- [ ] 1.4 **[COMPUERTA]** Registrar OQ4 (mencionar o no las cifras retiradas en la nota de versiones) y aprobar la plantilla de D3.2 con la redaccion final. (TD «Procedencia»)
- [ ] 1.5 **[COMPUERTA]** Registrar OQ8: para cada uno de `c-228`, `c-229`, `c-230` y `c-232`, la decision de los autores (reformular la premisa al corpus de 200 casos, o archivar sin aplicar). No editar esos changes en este change; solo registrar la decision y su responsable.
- [ ] 1.6 Registrar OQ6 (canario de deriva) y OQ7 (terminos de la linea de base en el capitulo 2 y el glosario) con la decision de los autores o la propuesta por defecto (canario rotulado; terminos conservados solo si siguen citados). (OOS «OOS-026»)

## 2. Retiro en el marco metodologico (capitulo 4)

- [ ] 2.1 `04-marco-metodologico.tex` L60: borrar `\paragraph{Corpus independiente de validacion}` completo; verificar que L48 y L88 ("un solo corpus congelado") siguen exactas sin cambios. (TD «Retiro»)
- [ ] 2.2 §4.7: borrar L113 (linea de base supervisada clasica), L117 (sensibilidad a la referencia, kappa 0,6055), L119 (sesgo del vocabulario sobre los 206) y L123 (`\paragraph{Diseno de la validacion fuera de muestra}`); verificar con `rg` que no quedan esos parrafos. (TD «Retiro», TLB «TLB-04»)
- [ ] 2.3 §4.7 L115 (calibracion): quitar la parte "por corpus"/fuera de muestra y conservar la definicion sobre los 200 casos; verificar que el piso, la regla prerregistrada y las metricas (ECE, Brier, AUROC) quedan intactos. (TD «Retiro»)
- [ ] 2.4 §4.7 L121 (brazo de modelo solo): describir solo el bloque dentro de la muestra como descriptivo, con la desviacion de los 112 reintentos y sin regla de tres vias como veredicto; segun OQ3, o retirar el parrafo. (TD «Eficiencia»)
- [ ] 2.5 §4.8: borrar la septima (L141, sesgo de seleccion del refuerzo) y la octava (L143, arbitro unico e inestabilidad de la confianza entre corridas); cambiar "ocho amenazas" (L127) por el cardinal real (esperado "seis") y verificar los ordinales. (TD «Retiro»)

## 3. Retiro en resultados (capitulo 8)

- [ ] 3.1 §8.4 (`subsec:calibracion`): quitar las filas L235-236 de `tab:calibracion-gate`, la mencion fuera de muestra del pie (L240) y las frases fuera de muestra de L222, L243, L245, L247, L249 y L251; verificar que la lectura dentro de la muestra (69 casos, AUROC 0,5168, ningun umbral) no cambia. (TD «Retiro»)
- [ ] 3.2 §8.6: borrar `subsec:sesgo-corpus-referencia` completa (L277-320, `tab:sesgo-vocabulario`, `tab:sesgo-subconjuntos`). (TD «Retiro»)
- [ ] 3.3 §8.9: borrar `subsec:validacion-fuera-muestra` completa (L387-450, `tab:fuera-de-muestra`, `tab:fuera-de-muestra-clases`). (TD «Retiro»)
- [ ] 3.4 §8.10: borrar la linea de base clasica (L454-496: `tab:linea-base-clasica`, contraste pareado, `tab:robustez-linea-base`). (TD «Retiro», TLB «TLB-04»)
- [ ] 3.5 §8.10, contraste con el modelo solo (L499-521, `tab:gemini-solo`): segun OQ3, quitar la fila "Primario (fuera de muestra)" (L511) y la prosa del bloque primario (L499, L519), y reescribir L521 para presentar la fila de 200 casos como descriptiva con su desviacion; o retirar la tabla. Decidir (OQ9) si `subsec:comparacion-alternativas` se renombra o se funde. (TD «Eficiencia»)
- [ ] 3.6 §8.12: borrar `subsec:ruido-referencia` completa (L556-585, `tab:ruido-referencia`). (TD «Retiro»)
- [ ] 3.7 L6: recontar los apartados del capitulo 8 y reescribir la frase inicial ("doce apartados") con el cardinal y la lista reales. (TD «Retiro»)

## 4. Retiro en la discusion (capitulo 9)

- [ ] 4.1 §9.1: quitar las cifras y lecturas fuera de muestra de L8, L10 (eficiencia: "sin contraste limpio"), L20 (procedencia de los ajustes: sin validacion fuera de muestra vigente), L28 (clase `Sistemas` con cifras dentro de la muestra) y L40 (calibracion solo dentro de la muestra). (TD «Retiro», «Eficiencia», «Ajustes»)
- [ ] 4.2 §9.3: reescribir la quinta limitacion (L56) sin la linea de base (comparacion con clasificadores alternativos: realizada y retirada, ver nota de versiones; queda como trabajo futuro) y la octava (L62) sin el doble etiquetado `E3`/`E4`; borrar los parrafos L66 (sensibilidad a la referencia) y L68 (sesgo de corpus); en la septima (L60) agregar la remision unica a `subsec:nota-versiones` ("no se dispone de validacion fuera de muestra"). Verificar que "nueve limitaciones" (L46) coincide con lo enumerado y que la novena sigue rotulada como superada. (TD «Retiro», TLB «TLB-04»)
- [ ] 4.3 §9.5: quitar solo las sensibilidades con la tasa fuera de muestra (L119 en la parte que corresponda y L125); no tocar el resto de §9.5 (lo reescribe `c-236`). (TD «Balance»)

## 5. Retiro en introduccion, arquitectura, conclusiones, recomendaciones y resumen

- [ ] 5.1 `01-introduccion.tex`: L38 (§1.4) acotar la hipotesis de eficiencia a "sin contraste limpio" sin remitir al bloque primario; L66 (§1.7) quitar la validacion fuera de muestra de la contribucion y rotular la validacion como dentro de la muestra; verificar que L72 y L76 (§1.8) siguen coherentes (una sola organizacion). (TD «Consistencia», «Eficiencia», «Acotadas»)
- [ ] 5.2 `05-arquitectura.tex` L68: re-anclar "cerca de un tercio de las llamadas" al bloque dentro de la muestra (69 de 200) como dato descriptivo, o quitarlo segun OQ3; verificar que no queda una reduccion de latencia y costo sin remision a lo medido. (TD «Acotadas», «Eficiencia»)
- [ ] 5.3 `09-conclusiones.tex`: L6, L37 y L47 sin cifras fuera de muestra y con la eficiencia "sin contraste limpio"; `tab:cumplimiento-objetivos` fila L24 (OE2) sin "fuera de muestra, 0,6893..." y fila L28 (OE6) sin la calibracion fuera de muestra; verificar que ningun estado de objetivo cambia por este retiro. (TD «Retiro», «Eficiencia», DV «Conclusiones»)
- [ ] 5.4 `10-recomendaciones.tex`: L6 (introduccion del capitulo) y L10 (calibracion: confirmacion en un corpus independiente como trabajo futuro, no como hecho); L14 acotar la eficiencia; L18 (`subsec:frontera-sistemas`) con cifras dentro de la muestra; L38 coherente. (TD «Trabajo futuro», «Eficiencia»)
- [ ] 5.5 `10-recomendaciones.tex` §11.5 (`subsec:corpus-independiente`, L24-26): reescribir como trabajo futuro con procedencia acreditable (exportacion original con fechas, autorizacion documentada, registro de etiquetadores, marcas temporales registradas por la herramienta, cuotas y arbitraje prefijados, comparacion con linea de base y modelo solo, criterio de exito); conservar la etiqueta. (TD «Trabajo futuro», TLB «TLB-04»)
- [ ] 5.6 `00-resumen.tex`: quitar la frase fuera de muestra de L13 (Resumen) y L29 (Abstract); contar palabras con la regla de c-106 y verificar `<= 250` en ambos. No cambiar la lectura del balance (la fija `c-236`). (TD «Retiro», DV «Conclusiones»)

## 6. Capitulo legal y declaracion de procedencia (BLOQUEADO por el grupo 1)

- [ ] 6.1 `11-aspectos-legales.tex` L48: borrar el parrafo del consentimiento de `E3`, `E4` y `E5`; verificar que §7.5 queda coherente para `E1`, `E2`, `O1`, `O2`. (TD «Procedencia»)
- [ ] 6.2 **[COMPUERTA P4]** `11-aspectos-legales.tex` L30 (§7.3): con la respuesta de P4, dejar exacta la descripcion de lo enviado a proveedores (119 textos y 81 audios del corpus de 200, mas los textos del corpus retirado si se enviaron, con su naturaleza confirmada), o remitir a la nota de versiones; no resolver por omision. (TD «Procedencia»)
- [ ] 6.3 **[COMPUERTA P1-P7]** `12-anexos.tex` §I.1 (`subsec:nota-versiones`, L233-235): agregar, despues del parrafo de N-02, la declaracion de D3.2 con la redaccion aprobada en 1.4: versiones 1.3.0 a 1.5.2, la validacion y sus analisis dependientes, el retiro, el motivo (procedencia no acreditable; textos que no eran incidentes extraidos de una organizacion) y solo lo que los autores confirmaron sobre textos, etiquetas y marcas temporales (o la declaracion de que no puede acreditarse). (TD «Procedencia», TLB «TLB-04»)
- [ ] 6.4 Verificar la declaracion: cada frase factual de §I.1, §7.3 y §7.5 tiene su respuesta registrada en la tabla de compuertas; el texto no atribuye el retiro a otra causa y no describe una tercera organizacion. (TD «Procedencia»)

## 7. Anexos, cronograma, referencias y bibliografia

- [ ] 7.1 Anexo A (`12-anexos.tex` L52, `fig:cronograma`) y `docs/diagrams/cronograma.md`: retirar los hitos de noviembre de la validacion fuera de muestra, el arbitraje, el refuerzo y la linea de base, o rotularlos como retirados; verificar el pie de la figura. (TD «Version»)
- [ ] 7.2 Anexo J: borrar `\paragraph` de la acotacion del arbitraje por mayoria (L291-311) y de la robustez de la brecha (L313-334); ajustar la introduccion (L245, "secciones 3.31, 3.33, 3.35 y 3.36"). Verificar que Anexo H L225 sigue coherente. (TD «Retiro»)
- [ ] 7.3 Referencias colgantes: `rg -n "subsec:validacion-fuera-muestra|subsec:ruido-referencia|subsec:sesgo-corpus-referencia|tab:fuera-de-muestra|tab:ruido-referencia|tab:linea-base-clasica|tab:robustez-linea-base|tab:sesgo-vocabulario|tab:sesgo-subconjuntos" "docs/Tesis/v10 (IA)/paper"` sin coincidencias (y `subsec:comparacion-alternativas` y `tab:gemini-solo` segun OQ3/OQ9). (TD «Retiro»)
- [ ] 7.4 Bibliografia: correr `python verify_citations.py`; si quedan entradas sin cita por el retiro, quitarlas de `Bibliography_base.bib` o justificar su permanencia segun OQ7; `STATUS: PASS`. (TD «Retiro»)
- [ ] 7.5 Compilacion de verificacion: copiar `docs/Tesis/v10 (IA)` a un directorio temporal y compilar alli con la imagen `texlive-thesis` (`latexmk main.tex`); verificar 0 errores fatales, 0 referencias/citas indefinidas y 0 etiquetas duplicadas; anotar el conteo de paginas como provisorio. No versionar el PDF ni regenerar `compilacion.md` (lo hace `c-239`). (TD «Retiro»)
- [ ] 7.6 Bateria de cifras retiradas: `rg -n "0,6893|0,7489|0,7467|0,7024|0,8447|0,8738|0,6055|142/206|147/206|compa.{1,2}a financiera|E3|E4|E5" "docs/Tesis/v10 (IA)/paper/sections"` solo devuelve lineas de `subsec:nota-versiones`; clasificar cada una en el registro. Verificar ademas que `61,6`, `17,76`, `W = 363`, `73,5`, `0,6508` y `110/138` siguen presentes sin cambio. (TD «Retiro»)

## 8. Memo, registro y documentos de la tesis

- [ ] 8.1 `numeros-canonicos.md`: agregar la seccion aditiva (numero fijado en 0.5) con causa, fecha de la decision, lista de secciones y valores afectados y estado "sin contraste limpio" de la eficiencia; marcar por upsert como `retirado`, con remision, cada valor de `3.19`, `3.20`, `3.22`, `3.23`, `3.25`, `3.26`, `3.27`, `3.30`, `3.32`, `3.34`, `3.35`, `3.36` y la parte fuera de muestra de `3.14`, `3.21`, `3.24`, `3.28` y `3.33` (verificar cada una contra el memo antes de marcarla); agregar la entrada de upsert en el encabezado. Verificar numeracion consecutiva y cifras intactas. (NC «Retiro memo», «Robustez»)
- [ ] 8.2 `dictamen-correcciones.md`: agregar la entrada de c-235 (patron de c-234, siguiente prefijo libre) con la tabla de compuertas (P1-P8, OQ2-OQ9: respuesta, fecha, responsable) y filas por observacion: K-01 (retiro, archivo:linea), K-02 (sin datos de terceros segun autores; §7.3 y §7.5), A-02 y B-02 ("no aplica por retiro"), M-02 (conclusion acotada), con fragmento verificable; anotar el conteo provisorio de paginas de 7.5. Verificar que las entradas previas quedan intactas.
- [ ] 8.3 `knowledge-base/11_evaluacion_experimental.md`: marcar como retirada la validacion fuera de muestra y sus analisis, sin borrar historia, y remitir a la seccion del memo del retiro. (OOS «OOS-026»)
- [ ] 8.4 Regenerar los extractos `tesis_para_agente.md`, `tesis_completa_extraida.txt` y `tesis_para_evaluacion.txt` con `build_tesis_para_agente.py` si el script trabaja sobre la fuente `.tex`; si requiere el PDF recompilado, dejarlo registrado para `c-239`.

## 9. Artefactos del repositorio (BLOQUEADO por 1.1 y 1.2)

- [ ] 9.1 **[COMPUERTA OQ2 = A]** `evaluation/data/campana/README.md`: rotular las secciones del corpus independiente (L99), su corrida (L124), el arbitraje (L180), la campana contrabalanceada y el corpus independiente (L228) y la referencia in-sample de la validacion (L298) como material retirado de la tesis (c-235), no evidencia, procedencia no acreditada; corregir "del organismo" y afines solo con lo confirmado en 1.1. No tocar ninguna tabla de SHA-256. (OOS «OOS-026»)
- [ ] 9.2 **[COMPUERTA OQ6]** `evaluation/data/canario/README.md` y `docs/operational-guide.md` (L842): rotular el canario de 103 casos como insumo tecnico sin referencia acreditada. (OOS «OOS-026»)
- [ ] 9.3 **[COMPUERTA P1, P2, P8]** `docs/campana-medicion/runbook-corpus-independiente.md`, `runbook-arbitraje-discordantes.md` y `confirmacion-posterior-consentimiento.md`: marcar como retirados y corregir las afirmaciones de procedencia y de consentimiento segun las respuestas registradas; si una afirmacion no se sostiene, declararlo sin reescribir la historia. (OOS «OOS-026»)
- [ ] 9.4 **[COMPUERTA OQ2 = B, solo si los autores eligen eliminar]** En un commit propio: eliminar los artefactos elegidos, ajustar `evaluation/tests/test_linea_de_base.py`, `evaluation/tests/test_calibracion_gate.py` (L396-399), `evaluation/monitoreo/test_monitor_deriva.py` (L203-226) y las sumas SHA-256, y verificar la suite verde. Registrar que la historia de git conserva los archivos. (OOS «OOS-026»)
- [ ] 9.5 Verificar `sha256sum -c` de las sumas fijadas (todo `OK` con la opcion A) y `python -m pytest evaluation -q` con el mismo conteo que 0.3. (OOS «OOS-026»)

## 10. Verificacion de cierre

- [ ] 10.1 `git diff --stat`: confirmar que no cambiaron `App/`, `n8n/`, el corpus de 200 casos, el codigo de `evaluation/` (salvo 9.4 si se eligio B), `.engram/`, `CHANGES.md`, ni los directorios de `c-228`, `c-229`, `c-230`, `c-232`, `c-237`.
- [ ] 10.2 Repetir 7.3, 7.6 y `verify_citations.py`; confirmar `STATUS: PASS` y la ausencia de cifras, alias y etiquetas retiradas fuera de la nota de versiones.
- [ ] 10.3 Confirmar coherencia del estado de la hipotesis de eficiencia ("sin contraste limpio" u OQ5) en `01`, `04`, `05`, `07`, `08`, `09` y `10`, y que ninguna frase afirma no inferioridad. (TD «Eficiencia»)
- [ ] 10.4 Confirmar que el retiro no es silencioso: la nota de versiones existe con su motivo y el cuerpo remite a ella una sola vez. (TD «Procedencia», «Retiro»)
- [ ] 10.5 Correr `openspec validate c-235-retirar-la-validacion-fuera-de-muestra-y-declarar-su-procedencia --strict` y registrar el resultado.
- [ ] 10.6 No commitear, pushear ni sincronizar Engram sin instruccion de los autores; guardar en Engram el resumen del apply (`opsx/c-235-retirar-la-validacion-fuera-de-muestra-y-declarar-su-procedencia/apply`) con compuertas resueltas, decisiones y verificaciones.
