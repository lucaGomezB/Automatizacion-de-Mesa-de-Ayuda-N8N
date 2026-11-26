# Respuestas probables del tribunal — Devolución de sexta instancia (2026-11-26)

Preparación para la defensa. Las respuestas se redactaron a partir de la tesis (`docs/Tesis/v10 (IA)`)
y de las decisiones de los autores registradas en el change
`c-252-atender-las-observaciones-de-la-sexta-instancia` y en
`docs/Tesis/Correcciones/dictamen-correcciones.md` (sección c-252, con las compuertas OQ-01 a OQ-04
resueltas). Responden, en orden, a las diez preguntas de la Sección 6 de la devolución de sexta
instancia (`auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md`). Estado: borrador para
revisión de los autores y del director.

**Nota de alcance.** Cada respuesta enuncia la pregunta y la responde de forma autónoma. Las respuestas
son del grupo de autores: el documento no se atribuye a un modelo de lenguaje ni a ninguna herramienta
de IA. Cada hecho afirmado remite a un artefacto versionado del repositorio (un `.tex`, un archivo de
`data/`, un commit o un SHA-256) o se marca explícitamente como «declaración de los autores» cuando no
existe registro fechado que lo respalde. Toda cifra de resultado coincide con un valor canónico de
`docs/Tesis/Correcciones/numeros-canonicos.md` o con la salida versionada del script
`evaluation/data/campana/analisis/analisis_sexta_instancia_c252.py`. Los colaboradores se citan solo
por alias (`A1`, `T1`, `E1`, `E2`, `O1`, `O2`); nunca se escribe un nombre real.

---

## 1. ¿En qué días exactos se recolectaron, redactaron, etiquetaron y cronometraron los 119 casos de correo y formulario, si la corrida automatizada fue el 02/10 y la notificación al círculo, el 01/10?

La cronología día por día, que es una declaración de los autores, es la siguiente. El 01/10 se notificó
verbalmente al círculo que se utilizarían sus incidentes. Entre el 01 y el 02/10 se recolectaron y
redactaron de forma disociada los 119 casos de correo y formulario (tareas simultáneas). El 02/10 se
prestó el consentimiento verbal de los colaboradores y corrió el flujo automatizado sobre los 119 casos.
El 05 y 06/10 corrió la telefónica (81 casos, recitados). Entre el 06 y el 09/10 se hizo el doble
etiquetado con consenso supervisado. El 09/10 se cronometró manualmente por pares (A1 y T1), posterior
al etiquetado, y el mismo 09/10 se versionó el corpus real con `tiempo_manual_s` (commit `ea62576`). El
orden real fue, por lo tanto, automatizado primero (02/10) y manual después (09/10); el flujo manual no
precedió al automatizado.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.2 y §4.4, `subsec:diseno-experimental`
y `subsec:poblacion-muestra-corpus`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I.1,
`subsec:nota-versiones`); commit `ea62576` (2026-10-09). La cronología día por día es declaración de los
autores, acotada por el commit `ea62576`.

## 2. ¿Por qué la v1.6.4 ubicaba la campaña manual entre junio y agosto, y la v1.6.5 en octubre? ¿Qué cambió en la evidencia?

La ventana «junio–agosto» era un artefacto de la era del corpus sintético: pertenecía a la etapa de
desarrollo en que los incidentes se generaban de forma artificial, y no respondía a una medición real. Al
reencuadrar la procedencia y adoptar el corpus real (los 200 casos en su forma disociada), la campaña
manual se refechó en **octubre de 2026**. Lo que cambió no fue una medición: cambió la base de la que
provenían las fechas. El cambio quedó registrado en la Nota de versiones como reemplazo de la ventana
«junio a agosto de 2026» por «octubre de 2026» (C-01).

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I.1, `subsec:nota-versiones`);
`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.2); commit `ea62576` (2026-10-09).

## 3. ¿Quién cronometró los 165,3 s de la versión del 3 de julio y sobre qué textos?

Los 165,3 s —junto con la exactitud de 92 %, `W = 0` y el kappa `0,87` de aquella versión— provienen del
**corpus sintético** de 200 casos generado durante el desarrollo, alrededor de julio de 2026, no de
incidentes reales. Ese corpus se versionó con el commit `68d06ec` (2026-06-11, «corpus sintetico
provisional») y se descartó y eliminó del repositorio. No provienen de un cronometraje real del corpus
vigente ni cabe atribuirlos a un operador real: son un valor simulado de una etapa de desarrollo
superada. Hoy figuran únicamente en la Nota de versiones como histórico, nunca como base de medición.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I.1, `subsec:nota-versiones`);
commit `68d06ec` (2026-06-11, corpus sintético); `docs/Tesis/Correcciones/numeros-canonicos.md`
(sección 3.1).

## 4. ¿Los valores de `tiempo_manual_s` incluyen o no unos 10 s de carga? Si no los incluyen, ¿por qué la versión anterior declaraba que sí?

**No los incluyen.** `tiempo_manual_s` es la clasificación manual pura: la lectura de la descripción y la
decisión de sector, sin componente de carga ni de búsqueda. La descripción de la v1.6.4, que declaraba una
carga estimada «en el orden de 10 s», era **inexacta**: ese componente nunca se sumó a los valores. Por
eso la cifra primaria de la sub-hipótesis 1 se mantiene en **71,2 %** (no baja al 65,6 % del descuento), y
la Nota de versiones registra que la v1.6.4 describía mal la tarea. El descuento de `10 s` del Anexo K es
el escenario adverso que el tribunal pidió cuantificar en la quinta instancia (C-02) cuando la descripción
aún incluía la carga; es una lectura contrafáctica de robustez, no la remoción de un valor que hubiera
existido.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (Tabla 3, `tab:variables`, y
§4.8, octava amenaza); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I.1, `subsec:nota-versiones`,
y Anexo K); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.8).

## 5. ¿Los incidentes del régimen (a) ocurrieron en el trabajo de quienes los reportaron? ¿Por qué el corpus habla de «clientes», «sucursales» y «estados de cuenta»?

Sí. Los incidentes del régimen (a) provienen del **ámbito laboral** de los reportantes —los autores y las
personas de su círculo (familiares y amigos)— y se **disociaron de forma irreversible desde la
recolección**: nunca se registró un original con identificador. El léxico «cliente», «sucursal», «estado
de cuenta» o «sistema principal» es un registro narrativo en tercera persona, propio del estilo del
equipo, usado para describir el tipo de incidente sin identificar a persona ni a sistema alguno; no
implica que los reportara un tercero. Como los incidentes provienen de ámbitos laborales, corresponde el
deber de confidencialidad del artículo 10 de la Ley 25.326, que se incorpora a los principios generales
del capítulo legal.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.4,
`subsec:poblacion-muestra-corpus`); `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex`
(§7.2 y el deber de confidencialidad del art. 10); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`
(Anexo I.1, `subsec:nota-versiones`). El origen laboral y la disociación irreversible son declaración de
los autores.

## 6. ¿Por qué la v1.6.4 atribuía el régimen (a) a los empleadores de los autores y la v1.6.5 a familiares y amigos?

La atribución a «los empleadores» era parte de la presentación original del corpus como registro de una
organización, que el tribunal autorizó a reencuadrar en la cuarta instancia: el escenario del estudio es
un escenario de referencia ficticio construido por los autores. La v1.6.5 declara el origen real del
régimen (a) —los autores y las personas de su círculo (familiares y amigos), en el ámbito laboral de los
reportantes— y retira la presentación anterior. El cambio de origen queda registrado en la Nota de
versiones como corrección de veracidad (D-03).

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I.1, `subsec:nota-versiones`);
`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.4); `docs/Tesis/Correcciones/dictamen-correcciones.md`
(sección c-252, OQ-03).

## 7. ¿Cuántas palabras tienen en promedio las 81 descripciones telefónicas? ¿Cómo se explica que leerlas llevara 87 s y recitarlas, 7 s?

Las descripciones telefónicas promedian **11,79 palabras y 57,70 caracteres** (81 casos), y la extensión
es similar y breve en los tres canales (correo electrónico: 11,30 palabras y 56,65 caracteres; formulario
web: 9,28 palabras y 45,66 caracteres), según el recálculo de solo lectura
`evaluation/data/campana/analisis/analisis_sexta_instancia_c252.json`. La brecha entre 87,2 s y 7,26 s no
proviene de la extensión del texto, sino de qué se midió en cada brazo: en el manual, el operador leyó en
voz alta la descripción completa y decidió el sector, de modo que el 87,2 s combina lectura en voz alta y
decisión; en el automatizado, un autor recitó una paráfrasis desde el `softphone` y el 7,26 s es solo la
recitación, sin decisión.

Fuentes: `evaluation/data/campana/analisis/analisis_sexta_instancia_c252.json` (y `.md`);
`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.4 y §4.8, sexta amenaza);
`docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (Tabla 12, `tab:tiempos-canal`).

## 8. ¿Cómo se cronometraron A1 y T1 «por pares» si cada uno trabajó en su domicilio?

La premisa de la pregunta no era exacta en la v1.6.5: el texto decía «en el domicilio de cada analista»,
lo cual sugería domicilios distintos y contradecía «por pares». La redacción se corrigió (OQ-04): A1 y T1
cronometraron **juntos, en un único domicilio —el de uno de los autores—**, y se cronometraron mutuamente
porque estaban físicamente reunidos. «Por pares» describe el cronometraje mutuo en esa reunión, no un
trabajo en domicilios separados.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.4,
`subsec:poblacion-muestra-corpus`); `docs/Tesis/Correcciones/dictamen-correcciones.md` (sección c-252,
OQ-04). El domicilio único es declaración de los autores.

## 9. Sin registro de procedencia por caso ni originales, ¿qué evidencia, además de la declaración de los autores, distingue un caso real de uno redactado?

La composición 119/81 es, efectivamente, una declaración de los autores: no existe un registro de
procedencia por caso ni originales con identificadores, porque el corpus se disoció de forma irreversible
desde la redacción. Lo que el repositorio sí conserva y acredita es la identidad del corpus sobre el que se
midió todo: una única huella SHA-256 (`1fd17d7e…`) que fija los 200 casos, sus descripciones y sus
etiquetas, de modo que no hay ambigüedad sobre qué se clasificó. La coautoría sobre los datos se declara
como limitación (séptima amenaza) y acota la independencia de la medición; no se presenta un original por
caso porque no existe.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.4 y §4.8, séptima amenaza);
`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo F, `sec:anexo-corpus`);
`data/corpus_evaluacion_pseudonimizado.json` (SHA-256 `1fd17d7e…`).

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
`docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.3, `subsec:limitaciones-estudio`);
`docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.2, exactitud estricta).
