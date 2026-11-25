# Respuestas probables del tribunal — Devolución de quinta instancia (2026-11-25)

Preparación para la defensa. Las respuestas se redactaron a partir de la tesis (`docs/Tesis/v10 (IA)`)
y de las decisiones de los autores registradas en el change
`c-250-atender-las-observaciones-de-la-quinta-instancia` y en
`docs/Tesis/Correcciones/dictamen-correcciones.md` (sección c-250, con las compuertas OQ-01 a OQ-05
cerradas). Responden, en orden, a las diez preguntas de la Sección 6 de la devolución de quinta
instancia (`auditorias/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.md`). Estado: borrador para
revisión de los autores y del director.

**Nota de alcance.** Cada respuesta enuncia la pregunta y la responde de forma autónoma. Las respuestas
son del grupo de autores: el documento no se atribuye a un modelo de lenguaje ni a ninguna herramienta
de IA. Cada hecho afirmado remite a un artefacto versionado del repositorio (un `.tex`, un archivo de
`data/`, un commit o un SHA-256) o se marca explícitamente como «declaración de los autores» cuando no
existe registro fechado que lo respalde. Toda cifra de resultado coincide con un valor canónico de
`docs/Tesis/Correcciones/numeros-canonicos.md` o con la salida versionada del script
`evaluation/data/campana/analisis/analisis_quinta_instancia_c250.py`. Los colaboradores se citan solo
por alias (`A1`, `T1`, `E1`, `E2`, `O1`, `O2`); nunca se escribe un nombre real.

---

## 1. ¿Quién cronometró los 165,3 s de la versión del 3 de julio y sobre qué textos? ¿Cómo convive esa medición con la del corpus vigente en el mismo período?

Los 165,3 s —junto con la exactitud de 92 %, `W = 0` y el kappa `0,87` de aquella versión— provienen del
**corpus sintético** de 200 casos generado durante el desarrollo, alrededor de julio de 2026, no de
incidentes reales. Ese corpus sintético se descartó y se eliminó del repositorio: se versionó con el
commit `68d06ec` (2026-06-11, «corpus sintetico provisional (200 casos) + primera corrida del
framework») y se retiró el 2026-09-11; su valor `165,3 s` figura hoy únicamente en la Nota de versiones
(Anexo I.1) como histórico/retirado, nunca como base de medición.

No «convive» con el corpus vigente: son corpus distintos y sucesivos. El corpus vigente —el real,
disociado— se versionó con el commit `ea62576` (2026-10-09); su tiempo manual es **61,6 s** (clasificación
manual), no los 165,3 s del sintético. Quién operó el cronometraje de aquella era sintética no se
reconstruye aquí porque el artefacto ya no forma parte del ejemplar; lo que el trabajo declara es que
esas cifras pertenecen a una etapa de desarrollo superada y que no se presentan como resultado.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I.1, `subsec:nota-versiones`);
`docs/anexo_f_corpus.md`; `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.1);
commit `68d06ec` (2026-06-11, corpus sintético); commit `ea62576` (2026-10-09, corpus real).

## 2. ¿Qué evidencia fechada prueba que los 200 casos vigentes se cronometraron entre junio y agosto?

Ninguna. La cronología vigente es **octubre de 2026**: la clasificación manual del corpus **real** (los
200 casos vigentes) ocurrió en octubre de 2026. La ventana «junio–agosto» era un artefacto de la era
sintética y quedó retirada del texto (se reemplazó por octubre 2026 en `04-marco-metodologico.tex`,
`01-introduccion.tex` y la Tabla 4). El cronometraje manual del corpus real no cuenta con registro
fechado de procedencia por caso: la planilla original no se conservó. Es una **declaración de los
autores**, sin registro fechado por caso. La única evidencia fechada que obra en el repositorio es el
versionado del corpus real (commit `ea62576`, 2026-10-09), que acredita la procedencia de los 200 casos
vigentes, no la fecha exacta de cada cronometraje.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.2 y §4.4);
commit `ea62576` (2026-10-09). La fecha de la campaña manual es declaración de los autores.

## 3. ¿Cuánto vale exactamente la carga estimada que se sumó a cada tiempo manual, y por qué el mínimo es 10 s?

No hubo carga estimada que sumar: ese «~10 s de carga del ticket» era un error de descripción, no un
dato, y se retiró del texto. El tiempo manual de la campaña 2026-10 es **clasificación manual** —la
lectura de la descripción y la decisión de sector—, sin componente de carga ni de búsqueda. Así lo fija
la definición de `tiempo_manual_s` en `data/README.md` y en `docs/anexo_f_corpus.md:99` («Tiempo de
clasificación manual en segundos»); el archivo congelado
`data/corpus_evaluacion_pseudonimizado.json` (SHA-256 `1fd17d7e…`) no tiene columna de carga. El mínimo
de **10 s** del rango (10–300 s) es una clasificación rápida, no «lectura 0 s + 10 s de carga».

Fuentes: `data/README.md`; `docs/anexo_f_corpus.md:99`;
`data/corpus_evaluacion_pseudonimizado.json` (SHA-256 `1fd17d7e…`);
`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (Tabla 3: definición operacional por
brazo, y octava amenaza).

## 4. ¿Qué queda de la reducción del 71,2 % si se quita la carga estimada y se excluye la telefonía?

No hay carga que quitar: la carga nunca fue un dato, así que no procede restarla. Lo que sí está
computado es la sub-hipótesis 1 **sin telefonía**, sobre correo electrónico y formulario web (119 casos
del régimen (a)): la media manual pasa de 44,12 s a una media automatizada de 16,18 s, con una reducción
del **63,3 %** y un intervalo de confianza del 95 % por pares de **[56,1 %; 69,6 %]** (Wilcoxon pareado,
p ≈ 4,5·10⁻¹⁸). Estos valores reproducen el recálculo de solo lectura del script
`evaluation/data/campana/analisis/analisis_quinta_instancia_c250.py`, cuya salida se versiona en
`analisis_quinta_instancia_c250.json` y `.md`. La sensibilidad de redondeo del Anexo K (−10 s → media
manual 51,6 s y reducción ≈65,6 %) se conserva como cota de redondeo (los tiempos se redondearon al alza
a múltiplos de 5 s), no como «remoción de la carga»: la carga nunca existió.

Fuentes: `evaluation/data/campana/analisis/analisis_quinta_instancia_c250.json` (y `.md`);
`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo K, sensibilidad de redondeo).

## 5. ¿Por qué leer en voz alta una descripción llevó unos 77 s en el brazo manual y la llamada recitada menos de 20 s?

Por una **asimetría de entrada** (sexta amenaza, declarada en §4.8): los dos brazos no procesaron ni el
mismo texto ni el mismo tramo. En el brazo manual, el operador leyó la **descripción completa** en voz
alta (clasificación manual, media 87,2 s en telefonía, Tabla 12). En el brazo automatizado, un autor
recitó una **paráfrasis** de la descripción, con la grabación acotada a 45 s, más el procesamiento de
extremo a extremo que sigue al cuelgue; la mediana de grabación más procesamiento (`t_e2e_s`) fue 18,7 s
y la media 20,09 s. Los dos constructos se separan en los datos: la grabación cruda
(`duracion_segundos`) tiene mediana 7,0 s / media 7,26 s, y el `t_e2e_s` mediana 18,7 s / media 20,09 s.
La reducción telefónica del 77,0 % (87,2 s → 20,09 s) compara, por lo tanto, una descripción completa
leída en voz alta contra una paráfrasis recitada, en tramos de alcance distinto. No hay un «77 s» que
reconciliar: ese descuento provenía del componente de carga que se retiró (véase la respuesta 3).

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.8, sexta amenaza);
`docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (Tabla 12, `tab:tiempos-canal`);
`data/corpus_resultados_telefonia.json` (SHA-256 `7f8c9d…`);
`evaluation/data/campana/analisis/analisis_quinta_instancia_c250.json`.

## 6. ¿Se usó un asistente de IA para reescribir las 119 descripciones del régimen (a)?

No. Las 119 descripciones del régimen (a) se registraron en forma disociada y sin asistente de
inteligencia artificial. La declaración de uso de asistentes lo deja constancia en la Tabla 26
(`tab:declaracion-uso-ia`), cuya fila de redacción del corpus figura como «sin IA». El único empleo de
Gemini 3.1 en una tarea de redacción corresponde a la validación fuera de muestra que se retiró del
ejemplar (§7.5), no al corpus vigente.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Tabla 26, `tab:declaracion-uso-ia`);
`docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (§7.5, Gemini 3.1 para la validación
retirada).

## 7. ¿Quién conserva los originales con identificadores y cuándo se destruyen?

No existen originales con identificadores que custodiar ni destruir. El corpus fue **disociado desde su
redacción**, en léxico genérico («sistema principal»/«sistema secundario»), sin nombres reales de
sistemas ni identificadores de usuario. Lo que se conserva y se transfiere son descripciones disociadas,
sin datos personales; no hay un original previo con identificadores en poder de los autores ni de
terceros. La afirmación anterior que decía que «existían originales no versionados con nombres reales de
sistemas e identificadores de usuario» se retiró.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (§7.1 a §7.3, disociación según
arts. 2 y 28 de la Ley 25.326); `data/README.md`. Que el corpus se redactó disociado desde su origen es
declaración de los autores.

## 8. ¿Los empleadores de los autores saben que incidentes de su operación forman parte del corpus?

No hay empleadores de por medio, de modo que no hay una organización empleadora a la que informar. El
origen del régimen (a) son los **autores y las personas de su círculo (familiares y amigos)**; el
régimen (b) tiene su origen en llamadas telefónicas de personas del círculo (familiares y amigos),
reconstruidas por uno de los autores. La referencia a «los empleadores reales de los autores» de
versiones anteriores se retiró, y con ella la cuestión del aval de esas organizaciones. El deber de
confidencialidad del art. 10 de la Ley 25.326 se incorporó a los principios generales del capítulo legal.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (§7.2, régimen (a) y (b), y §7.4,
deber de confidencialidad). Es declaración de los autores que el círculo (familiares y amigos) es el
origen real de ambos regímenes.

## 9. ¿Qué consentimiento dieron las personas del círculo de los autores que reportaron incidentes del régimen (a)?

Se les **notificó verbalmente el 2026-09-30** que se utilizarían sus incidentes en forma pseudonimizada y
disociada, construidos a partir de sus descripciones. No se requirió consentimiento, porque el contenido
es disociado y, conforme a los arts. 2 y 28 de la Ley 25.326, no constituye dato personal. El
consentimiento de los **colaboradores** (los autores y A1), prestado verbalmente el 2026-10-02 y
documentado en el acta (`docs/seguridad/acta-consentimiento-t2.md`, redactada el 2026-11-17 y firmada el
2026-11-20), es un acto distinto: cubre su participación en el estudio y no el contenido del corpus.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (§7.2, §7.3 y §7.5);
`docs/seguridad/acta-consentimiento-t2.md`. Que la notificación fue verbal el 2026-09-30 es declaración
de los autores, constatada en el texto del capítulo legal.

## 10. Si los autores redactaron los 200 casos y ajustaron las reglas sobre ellos, ¿qué parte del 73,5 % puede atribuirse al clasificador?

La coautoría sobre los datos y sobre el criterio (séptima amenaza) acota lo atribuible. El **73,5 %**
(147/200, exactitud estricta) es una cifra dentro de la muestra, calculada sobre el corpus tal como los
autores lo redactaron y sobre reglas ajustadas contra ese mismo corpus; no puede atribuirse por entero al
clasificador, porque no existe un corpus redactado por terceros que aísle la redacción del desempeño. La
magnitud del sesgo de coautoría se declara no estimada y se conserva la lectura de sensibilidad al
vocabulario como cota pesimista, no como medición. En consecuencia, la pretensión de generalización se
acota: el 73,5 % se reporta como estimación dentro de la muestra, probablemente optimista, y no como una
propiedad del clasificador independiente del corpus.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.8, séptima amenaza);
`docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.3, limitaciones);
`docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.2, exactitud estricta).