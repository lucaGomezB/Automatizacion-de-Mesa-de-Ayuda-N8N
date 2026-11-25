## ADDED Requirements

### Requirement: Cronologia de la campana manual acreditada o declarada no verificable (C-01)

El documento SHALL explicar en el Anexo I.1 (`12-anexos.tex`, `subsec:nota-versiones`) que los
165,3 s de la version del 3 de julio de 2026 no provienen de un cronometraje sino del parametro de
media del generador del corpus sintetico (`evaluation/generate_corpus.py`, commit `41430a21`), y el
origen de esa cifra en el borrador de junio segun la respuesta registrada de los autores (OQ-01 de
c-250). Si los autores aportan evidencia fechada de que los 200 tiempos manuales se cronometraron
entre junio y agosto de 2026, §4.2, §4.4, la Tabla 4 (`tab:procedencia-numeros`) y §4.8 SHALL
citarla con su fecha y su alcance (casos y fechas que cubre). Si no la aportan, esos cuatro lugares
y la fuente de la figura `fig:cronograma` (`docs/diagrams/cronograma.md`) SHALL declarar que la
fecha de la campana manual es una declaracion de los autores no verificable, y la primera amenaza
SHALL mencionar el rastro fechado mas temprano de los 200 tiempos que conste en el repositorio. El
documento MUST NOT afirmar la ventana junio-agosto sin una de esas dos calificaciones, MUST NOT
inventar fechas ni evidencia y MUST NOT describir como no conservado un original que los autores
declaren existente. Sin la respuesta registrada, las tareas quedan bloqueadas.

#### Scenario: Origen de los 165,3 s explicado

- **WHEN** se lee la entrada de la version del 3 de julio en el Anexo I.1
- **THEN** se declara que los 165,3 s fueron el parametro de un generador sintetico y no un cronometraje
- **AND** el origen de la cifra del borrador de junio coincide con la respuesta OQ-01 registrada en la seccion c-250 de `dictamen-correcciones.md`

#### Scenario: Ventana calificada en los cuatro lugares

- **WHEN** se ejecuta `rg -n "jun--ago|junio y agosto" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex"`
- **THEN** cada coincidencia referida a la campana manual lleva la evidencia fechada (rama a) o la clausula de declaracion no verificable (rama b)

#### Scenario: Cronograma coherente

- **WHEN** se lee la fila "Campana manual" de `docs/diagrams/cronograma.md`
- **THEN** su fuente coincide con la rama aplicada en el capitulo de metodo

#### Scenario: Sin respuesta de autores

- **WHEN** la tabla de compuertas de c-250 no contiene la respuesta OQ-01
- **THEN** las tareas gated por OQ-01 permanecen sin marcar y no se escribe prosa sobre la cronologia

### Requirement: Componente estimado del tiempo manual declarado y propagado (C-02)

La Tabla 3 (`tab:variables`) SHALL dar una definicion operacional del tiempo de registro por brazo:
para el brazo manual, la lectura cronometrada por el par (con redondeo hacia arriba a 5 s) mas un
componente de carga del ticket estimado y no medido, sin persistencia en una base de datos; para el
automatizado, la latencia hasta la persistencia confirmada (correo y formulario) o la duracion de
la grabacion mas la latencia posterior al cuelgue (telefonia). El valor del componente SHALL
declararse segun la respuesta registrada de los autores (OQ-02 de c-250): el valor exacto si fue
una constante, la regla si vario, o la declaracion de magnitud desconocida; en este ultimo caso el
documento MUST NOT llamarlo "fijo" sin declarar la tension con los cuatro casos de 10 s. El
componente estimado SHALL mencionarse en el Resumen, el Abstract, §1.2, §8.1 y las Tablas 10 y 23,
sin superar 250 palabras de prosa en el Resumen ni en el Abstract. La frase "midio el tiempo de
registro incidente por incidente con cronometraje en vivo" SHALL retirarse.

#### Scenario: Definicion por brazo

- **WHEN** se lee la fila del tiempo de registro en `tab:variables`
- **THEN** hay una definicion rotulada por brazo y la del brazo manual no menciona la persistencia en la base de datos

#### Scenario: Valor o desconocimiento declarado

- **WHEN** se leen el protocolo de §4.5 y la octava amenaza de §4.8
- **THEN** el valor del componente, su regla o su desconocimiento coincide con la respuesta OQ-02 registrada

#### Scenario: Propagacion al resumen y a las tablas

- **WHEN** se buscan menciones del componente estimado en `00-resumen.tex`, §1.2, §8.1, `tab:sintesis-resultados` y `tab:cumplimiento-objetivos`
- **THEN** cada lugar lo menciona
- **AND** el Resumen y el Abstract tienen como maximo 250 palabras de prosa cada uno

#### Scenario: Sin respuesta de autores

- **WHEN** la tabla de compuertas de c-250 no contiene la respuesta OQ-02
- **THEN** no se escribe el valor del componente ni se retira o conserva "fijo"

### Requirement: Reduccion sin el componente y sin telefonia recomputada por pares (C-02, C-03)

Las cifras nuevas de tiempo SHALL producirse con un script de analisis de solo lectura,
determinista y versionado (`evaluation/data/campana/analisis/analisis_quinta_instancia_c250.py`),
escrito con su prueba primero, sobre `data/corpus_evaluacion_pseudonimizado.json`,
`data/corpus_resultados_telefonia.json` y `data/corpus_resultados_web_correo.json`. El script SHALL
calcular por pares, para los 200 pares, los 119 de correo y formulario y los 81 telefonicos, la
reduccion de la media con descuentos de 0, 5 y 10 s (y el valor declarado en OQ-02 si existe), con
IC bootstrap percentil al 95 % por pares (semilla `20261021`, 2000 remuestreos) y la prueba de
Wilcoxon, y la duracion de las 81 grabaciones frente a la lectura manual por par. SHALL abortar sin
escribir si no reproduce las anclas canonicas (71,16 %, 68,61 %, 65,57 %, IC `[0,6716; 0,7459]`,
87,25 s, 20,09 s, 77,0 %, 61,585 s, 17,76 s). La prosa y el Anexo K SHALL tomar las cifras de su
salida y MUST NOT copiar las aproximaciones del tribunal.

#### Scenario: Prueba primero

- **WHEN** se inspecciona el historial del apply
- **THEN** `test_analisis_quinta_instancia_c250.py` fallo antes de existir el modulo y pasa despues, con al menos dos casos por funcion

#### Scenario: Anclas reproducidas

- **WHEN** se ejecuta el script desde la raiz del repositorio
- **THEN** reproduce las anclas canonicas y escribe `.json`, `.md` y `.SHA256SUMS.txt` identicos en dos corridas

#### Scenario: Anexo K con IC por pares

- **WHEN** se leen las filas nuevas de `tab:rango-robustez-tiempos`
- **THEN** cada reduccion sin el componente figura con su IC por pares y coincide con el JSON

### Requirement: Asimetria de entradas en telefonia declarada (C-03)

La sexta amenaza a la validez SHALL declarar que en telefonia el brazo manual leyo en voz alta la
descripcion completa y el automatizado proceso una paráfrasis recitada con grabacion acotada a 45 s,
e informar la duracion media de las 81 grabaciones frente a la lectura manual, con cifras del script.
§8.1 SHALL informar la sub-hipotesis 1 tambien sobre los 119 pares de correo y formulario, con IC y
Wilcoxon, y rotular la reduccion telefonica como contraste de entradas no equivalentes. El rotulo
del veredicto de la sub-hipotesis 1 SHALL ser el ratificado por los autores (OQ-06 de c-250) y MUST
NOT cambiarse sin esa respuesta.

#### Scenario: Sexta amenaza ampliada

- **WHEN** se lee la sexta amenaza en §4.8
- **THEN** nombra la asimetria de entradas y la duracion media de las grabaciones del JSON

#### Scenario: Sub-hipotesis 1 sin telefonia

- **WHEN** se lee §8.1 junto a `tab:tiempos-canal`
- **THEN** figura la reduccion de los 119 pares de correo y formulario con su IC y su Wilcoxon

#### Scenario: Rotulo ratificado

- **WHEN** se comparan los rotulos de la sub-hipotesis 1 en `tab:sintesis-resultados`, `tab:cumplimiento-objetivos`, las conclusiones y el Resumen
- **THEN** son identicos y coinciden con la respuesta OQ-06 registrada

### Requirement: Estado unico del registro primario (C-04)

§4.5, la Tabla 4 y §8.1 SHALL describir con la misma formula el registro primario de cada conjunto
de tiempos: 118 de los 119 tiempos automatizados de correo y formulario con registro de las marcas
de la base (sin `R001`), que respalda la existencia de los incidentes y no la medicion de extremo a
extremo; los 81 telefonicos con registro primario; los 200 manuales con el registro pseudonimizado
de la hoja de campana. El conteo SHALL provenir del script.

#### Scenario: Una sola formula

- **WHEN** se ejecuta `rg -n "sin registro primario conservado" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias
- **AND** `04-marco-metodologico.tex` (§4.5 y Tabla 4) y `07-resultados.tex` (§8.1) dan el mismo estado

### Requirement: Consentimiento de colaboradores separado y licitud por disociacion (C-05)

El capitulo legal SHALL distinguir el consentimiento de los colaboradores (los autores y `A1`) del
de los titulares de los incidentes, SHALL retirar la afirmacion de que titulares y responsables del
tratamiento son las mismas personas y la que presenta el consentimiento del 2026-10-02 como
refutacion de lo dicho en v1.6.0 sobre los titulares, SHALL fundar la licitud del tratamiento del
corpus en la disociacion (arts. 2 y 28 de la Ley 25.326), SHALL definir la "notificacion a los
integrantes del grupo" del 2026-10-01 y SHALL declarar quien guarda los originales con
identificadores y cuando se destruyen. Todo SHALL provenir de la respuesta registrada de los autores
(OQ-03 de c-250), con el texto mostrado antes de escribir (HIGH), y MUST NOT contener nombres reales
ni la correspondencia alias-identidad. Las actas firmadas MUST NOT reescribirse: se agregan anexos de
revision fechados.

#### Scenario: Afirmaciones retiradas

- **WHEN** se ejecuta `rg -n "mismas personas|v1.6.0 afirm" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias referidas a titulares del regimen (a)

#### Scenario: Licitud y custodia declaradas

- **WHEN** se lee el capitulo legal
- **THEN** la licitud del corpus se funda en la disociacion citando los articulos 2 y 28
- **AND** figuran quien guarda los originales con identificadores y cuando se destruyen, segun OQ-03

#### Scenario: Sin respuesta de autores

- **WHEN** la tabla de compuertas de c-250 no contiene la respuesta OQ-03
- **THEN** las tareas gated por OQ-03 permanecen sin marcar

### Requirement: Empleadores informados o aval del director (C-06)

La afirmacion de que no se requirio autorizacion de las organizaciones empleadoras SHALL llevar el
aval escrito del director o la declaracion de si los empleadores fueron informados, con mencion del
deber de confidencialidad (art. 10 de la Ley 25.326), segun la respuesta registrada de autores y
director (OQ-04 de c-250). Sin esa respuesta, la tarea queda bloqueada.

#### Scenario: Afirmacion respaldada

- **WHEN** se lee el parrafo de los empleadores reales en §7.2
- **THEN** figura el aval del director o la declaracion sobre los empleadores, y el articulo 10

### Requirement: Coherencia y redaccion de quinta instancia (C-07)

La Tabla 26 (`tab:declaracion-uso-ia`) SHALL tener una fila sobre la redaccion del corpus que
declare la correccion de erratas de la conversion del 2026-09-16 y, segun OQ-05 de c-250, si se uso
un asistente de IA para reescribir las 119 descripciones. I.3 SHALL atribuir el etiquetado a `A1`,
`T1`, `E1` y `E2`. Las 81 reconstrucciones SHALL atribuirse a un autor en todo el documento. §7.5
SHALL mencionar Gemini 3.1 para la validacion retirada. La frase "dispositivo de dimensionamiento y
no el lugar de recoleccion" SHALL aparecer una sola vez; "corpus propio de la organizacion" SHALL
retirarse; "en su domicilio" SHALL aclararse segun OQ-01 de c-250.

#### Scenario: Frases unificadas

- **WHEN** se ejecutan `rg -c "dispositivo de dimensionamiento y no el lugar"`, `rg -n "corpus propio de la organizaci"` y `rg -n "redactadas por los autores"` sobre las secciones
- **THEN** la primera suma 1 y las otras dos no devuelven coincidencias

#### Scenario: Fila del corpus en la Tabla 26

- **WHEN** se lee `tab:declaracion-uso-ia`
- **THEN** existe la fila del corpus y su contenido coincide con OQ-05

### Requirement: Respuestas escritas a las preguntas probables del tribunal

El repositorio SHALL contener `docs/Tesis/Correcciones/respuestas-tribunal-quinta-instancia.md` con
una respuesta escrita a cada una de las diez preguntas de la seccion 6 de la devolucion, redactada
desde la tesis, el script de c-250 y las respuestas registradas de las compuertas. Una respuesta que
dependa de una compuerta sin respuesta SHALL quedar marcada como pendiente y MUST NOT afirmar el
hecho. Las cifras SHALL cotejarse con `cotejar_cifras_respuestas.py` contra el texto extraido de la
version de defensa.

#### Scenario: Diez respuestas cotejadas

- **WHEN** se cuenta y se coteja el archivo de respuestas
- **THEN** tiene diez secciones y el cotejo termina con codigo de salida 0

### Requirement: Transcripcion de la devolucion de quinta instancia

`auditorias/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.md` SHALL transcribir el PDF homonimo
con el formato de la transcripcion de tercera instancia: encabezado que declara que es una
transcripcion extraida con `pdftotext -layout` y que el PDF es la evidencia de referencia, seguido
del texto sin parafrasear, en UTF-8 sin BOM y con fines de linea LF.

#### Scenario: Transcripcion fiel

- **WHEN** se compara la transcripcion con el PDF
- **THEN** contiene las observaciones C-01 a C-07 y las diez preguntas con el texto del tribunal
- **AND** el encabezado remite al PDF como evidencia

### Requirement: Release de defensa con visto bueno del director

La version de defensa SHALL publicarse como `v1.6.5` (o la version que fijen autores y director en
OQ-07 de c-250) con la regla de tags vigente (tag anotado sobre el commit de contenido con el PDF
recompilado y hash consignado en el commit siguiente, sin mover tags publicados), con una entrada en
la Nota de versiones (Anexo I.1), el total de paginas registrado en el libro mayor con la decision de
los autores y los derivados regenerados. La version SHALL incorporar C-01 a C-04; C-05 a C-07 SHALL
incorporarse o quedar diferidas por decision registrada. La entrega al tribunal SHALL esperar el
visto bueno escrito del director, registrado con fecha, medio y version.

#### Scenario: Tag y PDF coherentes

- **WHEN** se ejecutan `git cat-file -t v1.6.5` y se compara el SHA-256 de `docs/Tesis/tesis_ultima_version.pdf` con el de `main.pdf` del tag
- **THEN** el tag es anotado y los SHA-256 coinciden

#### Scenario: Visto bueno antes de la entrega

- **WHEN** se lee la tabla de compuertas de c-250
- **THEN** la fila G-DIR tiene fecha anterior o igual a la entrega de la version al tribunal

### Requirement: Registro de compuertas y verificacion de c-250

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL tener una seccion c-250 con la tabla de
compuertas OQ-01 a OQ-07 y G-DIR (respuesta literal, fecha y responsable), la evidencia del
repositorio usada para acotarlas, las tablas ANTES/DESPUES de cada tarea de prosa, las cifras del
script con sus diferencias respecto de las aproximaciones del tribunal y el registro de la release.

#### Scenario: Seccion completa

- **WHEN** se lee la seccion c-250
- **THEN** figuran las ocho filas de compuertas, las tablas ANTES/DESPUES y la release
