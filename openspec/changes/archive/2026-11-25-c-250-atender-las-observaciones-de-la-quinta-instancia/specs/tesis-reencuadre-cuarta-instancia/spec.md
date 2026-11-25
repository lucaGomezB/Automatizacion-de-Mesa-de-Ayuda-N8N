## ADDED Requirements

### Requirement: Cronología de la campaña manual en octubre 2026 referida al corpus vigente (C-01 de c-250)

El documento SHALL referir toda medición de la línea base manual al corpus **vigente** (200 casos) y
MUST NOT presentar el corpus sintético del 3 de julio (165,3 s) como base de medición: ese corpus
SHALL figurar únicamente como histórico/retirado en la Nota de versiones. La clasificación manual del
corpus **real** SHALL fecharse en **octubre 2026** (no "junio a agosto"): la ventana "junio a agosto"
de §4.2 (`04-marco-metodologico.tex:14`), §4.4 (`:46`), la Tabla 4 `tab:procedencia-numeros`
(`:78`) y §1.2 (`01-introduccion.tex:16`) SHALL reemplazarse por **octubre 2026**, referido a la
clasificación manual del corpus real. La evidencia fechada es: commit `68d06ec` (2026-06-11) versiona
el corpus **sintético**; commit `ea62576` (2026-10-09) versiona el corpus **real**. La declaración
honesta de cronología ("declaración de los autores sin registro fechado") SHALL conservarse. El
contenido MUST NOT inventarse.

#### Scenario: Corpus sintético solo histórico

- **WHEN** se ejecuta `rg -n "165,3|corpus sint.tico" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** la única aparición como base de medición no existe: el 165,3 s figura solo como histórico/retirado, y únicamente en la Nota de versiones (Anexo I.1)

#### Scenario: Ventana junio–agosto reemplazada por octubre 2026

- **WHEN** se ejecuta `rg -n "junio a agosto|junio y agosto|entre junio y agosto" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias fuera de la Nota de versiones; §4.2, §4.4, la Tabla 4 y §1.2 fechan la campaña vigente en octubre 2026

#### Scenario: Evidencia fechada citada

- **WHEN** se lee el pasaje que fundamenta la cronología de la campaña vigente
- **THEN** se citan los commits `68d06ec` (sintético) y `ea62576` (real) como evidencia fechada, y la declaración honesta sin registro fechado se conserva

### Requirement: Componente "~10 s de carga del ticket" retirado (C-02 de c-250)

El documento SHALL retirar el "~10 s de carga del ticket estimada": ese componente NO existe en los
datos. El tiempo manual SHALL describirse como **clasificación manual (lectura + decisión de
sector)**, sin componente E2E ni de carga. La fórmula "en el orden de 10 s, cuya magnitud exacta no
consta" SHALL retirarse de §4.4 (`04:89`), §4.8 octava amenaza (`04:131`), `12-anexos.tex:153`,
`07-resultados.tex:285`, `01-introduccion.tex:18`, el Resumen (`00-resumen.tex:13`), el Abstract
(`:29`), la Tabla 10 (`07:42`), la Tabla 23 (`09:14`) y `data/README.md`. La Tabla 3 (`04:31`) SHALL
dar una definición operacional **por brazo**: manual = clasificación (lectura + decisión de sector),
automatizado = E2E (recepción → persistencia); el brazo manual MUST NOT describirse como "hasta la
persistencia confirmada del ticket". El Anexo K (`12-anexos.tex:351,353,367`) SHALL CONSERVAR su
computo de −10 s → 51,6 s / 65,6 % como **sensibilidad de redondeo** (los valores se redondearon
ARRIBA a múltiplos de 5 s): MUST NOT re-relatarse como "remoción de un componente de carga".

#### Scenario: Fórmula de carga retirada

- **WHEN** se ejecuta `rg -n "en el orden de 10|carga del ticket" "docs/Tesis/v10 (IA)/paper/sections/" "data/README.md"`
- **THEN** no hay coincidencias de un componente de carga sumado al tiempo manual

#### Scenario: Definición operacional por brazo

- **WHEN** se lee la Tabla 3 (`04:31`)
- **THEN** cada brazo (manual, automatizado) tiene su definición operacional: manual = clasificación (lectura + decisión); automatizado = E2E, y el brazo manual no se describe como "hasta la persistencia confirmada del ticket"

#### Scenario: Anexo K permanece como sensibilidad de redondeo

- **WHEN** se lee el Anexo K (`12-anexos.tex:351-367`)
- **THEN** el −10 s → 51,6 s / 65,6 % figura como sensibilidad de redondeo (valores redondeados hacia arriba), y NO como remoción de un componente de carga

### Requirement: Asimetría telefónica por brazo y sub-hipótesis 1 sin telefonía (C-03 de c-250)

El documento SHALL informar la mediana y la media de duración de las 81 grabaciones frente a la
lectura manual completa, distinguiendo explícitamente la grabación cruda `duracion_segundos` (mediana
7,0 s; media 7,26 s) del `t_e2e_s` automatizado de grabación+procesamiento (mediana 18,698 s), para
no confundir ambos constructos. La sexta amenaza (`04:127`) SHALL ampliarse con esta asimetría: en el
brazo automatizado de telefonía un autor recitó una paráfrasis con tope de 45 s, mientras el brazo
manual leyó en voz alta la descripción completa, de modo que las medias 87,2 s / 20,09 s comparan dos
textos de distinta extensión; y con el componente de carga retirado, la asimetría SHALL declararse aún
más fundamental (el 87,2 s manual es clasificación pura y el 20,09 s automatizado es E2E: distinto
alcance Y distinta entrada). La sub-hipótesis 1 SHALL informarse también **sin** telefonía: sobre
correo y formulario las medias pasan de ≈44,1 s a ≈16,2 s (≈63,3 % de reducción), recomputada por
pares con su intervalo. Todas las cifras SHALL provenir de `data/corpus_resultados_telefonia.json`,
`data/corpus_evaluacion_pseudonimizado.json` y la sección 3.8 del memo canónico, a través del script
de análisis con prueba automatizada, y MUST NOT copiarse del dictamen.

#### Scenario: Grabación vs. t_e2e distinguidos

- **WHEN** se lee el pasaje que informa la duración de las 81 grabaciones
- **THEN** la mediana de grabación+procesamiento (18,7 s) no se presenta como la duración de grabación; la duración cruda (mediana 7,0 s / media 7,26 s) se distingue explícitamente del `t_e2e_s`

#### Scenario: Sexta amenaza ampliada

- **WHEN** se lee la sexta amenaza (`04:127`)
- **THEN** contrasta el brazo manual (descripción completa leída en voz alta) contra el automatizado (paráfrasis recitada, tope 45 s), declarando la distinta extensión de entrada y la asimetría de alcance tras el retiro de la carga

#### Scenario: Sub-hipótesis 1 sin telefonía

- **WHEN** se lee el informe de la sub-hipótesis 1 (`07:10`, `08:8` o su sucesor) y la salida del script de análisis
- **THEN** figura la reducción sin telefonía (correo+formulario ≈44,1 s → ≈16,2 s, ≈63,3 %) con su intervalo por pares, y las cifras coinciden con el JSON versionado

#### Scenario: Cifras con generador versionado

- **WHEN** se ejecuta `pytest evaluation/data/campana/analisis/test_analisis_quinta_instancia_c250.py` y luego el script
- **THEN** la prueba pasa y el JSON contiene la desagregación sin telefonía, la reducción sin telefonía y sus intervalos

### Requirement: Estado del registro primario unificado (C-04 de c-250)

La redacción SHALL unificar el estado del registro primario: §8.1 (`07:38`) SHALL dejar de decir que
los 119 de correo y formulario están "sin registro primario conservado" mientras atribuye "con
registro" solo a los 81 telefónicos. El texto final SHALL decir que los 81 telefónicos están
respaldados por `corpus_resultados_telefonia.json` y que los 119 de correo/formulario están
respaldados por `corpus_resultados_web_correo.json` con 118 de 119 con registro versionado, siendo
R001 el único caso sin registro, coherente con §4.5 (`04:66`, `:79`), `12-anexos.tex:149` y
`data/README.md:40-47`. No cambia ningún dato ni ningún número canónico.

#### Scenario: Redacción coherente en §8.1

- **WHEN** se lee §8.1 (`07:38`) y se contrasta con §4.5 (`04:66`, `:79`), `12:149` y `data/README.md:40-47`
- **THEN** todos los pasajes describen el mismo estado: 81 telefónicos y 118/119 correo/formulario con registro versionado, R001 como único caso sin registro

#### Scenario: Sin cambio de datos

- **WHEN** se ejecuta `sha256sum data/corpus_resultados_web_correo.json data/corpus_resultados_telefonia.json data/corpus_evaluacion_pseudonimizado.json`
- **THEN** los hashes coinciden con los registrados en la línea base (el corpus no se editó)

### Requirement: Consentimiento separado, sin originales con identificadores y licitud por disociación (C-05 de c-250)

En el capítulo legal (`11-aspectos-legales.tex`, rendido Cap. 7), el documento SHALL retirar la
afirmación de que "los originales no versionados contenían los nombres reales de sus sistemas + ID
USUARIO" (`:18` y `data/README.md:55-63`): el corpus fue SIEMPRE genérico ("sistema principal" /
"sistema secundario") y no hay originales con identificadores ni custodio ni fecha de destrucción que
declarar. El documento SHALL separar el consentimiento de los colaboradores (autores + A1) del de los
TITULARES (los reportantes del círculo), y MUST NOT sostener en `:46` que "los titulares de los datos
y los responsables del tratamiento son las mismas personas". La licitud SHALL fundarse en la
disociación citando los artículos **2 y 28** de la Ley 25.326 (el art. 28 es una adición neta; hoy
solo se cita el art. 2 en `:12`). La "notificación a los integrantes del grupo" SHALL definirse como
**verbal el 2026-09-30** (corrige el 01/10 anterior): se les comunicó que se utilizarían sus
incidentes en forma pseudonimizada y disociada, construidos a partir de sus descripciones. El
contenido MUST NOT inventarse y MUST NOT contener nombres reales ni la correspondencia
alias-identidad.

#### Scenario: Sin originales con identificadores

- **WHEN** se ejecuta `rg -n "nombres reales|ID USUARIO|SISTEMA PRINCIPAL|custodi|destrucci.n" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex" "data/README.md"`
- **THEN** no hay coincidencias que sostengan la existencia de originales con identificadores ni de custodia o destrucción que declarar

#### Scenario: Consentimiento y titularidad separados

- **WHEN** se ejecuta `rg -n "titulares.*responsables.*mismas personas" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias; el consentimiento de colaboradores (autores + A1) y el de los titulares (reportantes del círculo) se tratan por separado

#### Scenario: Licitud fundada en disociación (arts. 2 y 28)

- **WHEN** se ejecuta `rg -n "art.*28|art.culo 28|disociaci.n" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** el art. 28 y el art. 2 se citan juntos como fundamento de la licitud por disociación

#### Scenario: Notificación verbal del 30/09 definida

- **WHEN** se lee `:32` del capítulo legal
- **THEN** la notificación a los integrantes del grupo figura como verbal el 2026-09-30, y especifica que se usarían sus incidentes en forma pseudonimizada y disociada, construidos a partir de sus descripciones

### Requirement: Empleadores disueltos, reencuadre de procedencia y deber de confidencialidad (C-06 de c-250)

El documento SHALL retirar la afirmación de `11-aspectos-legales.tex:18` ("los empleadores reales de
los autores" y "no se requirió autorización de esas organizaciones"): el origen real es **familiares y
amigos (el círculo)**. Con la disolución de los "empleadores reales", MUST NOT existir una tarea de
"obtener el aval escrito del director" (la afirmación que respaldaba desapareció). El documento SHALL
agregar el deber de confidencialidad del **art. 10** de la Ley 25.326 a los principios generales del
capítulo legal (junto a la tríada CIA, hoy en `:40`). El reencuadre de procedencia SHALL retirar
"integrantes del entorno operativo del propio equipo" de toda mención de procedencia
(`01:16,48,72`, `04:46`, `08:22,42,50`, `09:52`, `11:16,46,54`, Resumen) y dejar la procedencia como
"los autores y las personas de su círculo (familiares y amigos)", CONSERVANDO el escenario ficticio
("organización mediana del sector servicios / 120 usuarios / 42 diarios", dispositivo de
dimensionamiento explícitamente no-real por R-01) y la "organización adoptante" (despliegue futuro).
El reencuadre SHALL registrarse en la Nota de versiones como corrección de veracidad (estilo R-01 a
R-07). El contenido MUST NOT inventarse.

#### Scenario: Empleadores reales retirados, sin aval del director

- **WHEN** se ejecuta `rg -n "empleadores reales|no se requiri. autorizaci.n de esas organizaciones|aval escrito del director" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias que sostengan la existencia de empleadores reales ni la necesidad de un aval del director por C-06

#### Scenario: Deber de confidencialidad citado

- **WHEN** se ejecuta `rg -n "art.*10|art.culo 10|confidencialidad" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** el art. 10 y el deber de confidencialidad se mencionan entre los principios generales del capítulo, junto a la tríada CIA

#### Scenario: Procedencia del círculo, sin "entorno operativo"

- **WHEN** se ejecuta `rg -n "integrantes del entorno operativo del propio equipo|entorno operativo" "docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex" "docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex" "docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex" "docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias en mención de procedencia; la procedencia dice "los autores y las personas de su círculo (familiares y amigos)"

#### Scenario: Escenario ficticio y organización adoptante conservados

- **WHEN** se ejecuta `rg -n "120 usuarios|42 diarios|organizaci.n adoptante" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** el escenario ficticio sigue presente como dispositivo de dimensionamiento (no-real, por R-01) y la "organización adoptante" sigue presente como despliegue futuro

### Requirement: Coherencia y redacción de la quinta instancia (C-07 de c-250)

La Tabla 26 (`tab:declaracion-uso-ia`, `12-anexos.tex:257-277`) SHALL agregar una fila sobre la
redacción del corpus que diga **"sin IA"** (no se usó un asistente de IA para reescribir las 119
descripciones del régimen (a)). La declaración I.3 (`12:279`) SHALL corregir que el etiquetado "es de
los autores": lo hicieron A1, T1, E1 y E2. La atribución de autoría de las reconstrucciones SHALL
unificarse entre "por los autores" (I.1 `12:241`), "por ese autor" (§4.4 `04:46`) y "uno de ellos"
(`09:25`), conforme a la decisión de autoría registrada en c-250. §7.5 (`11:54`) SHALL mencionar
"Gemini 3.1" para la validación retirada, como en I.1 (`12:243`). La frase "dispositivo de
dimensionamiento y no el lugar de recolección" SHALL aparecer exactamente una vez (hoy 8×). "Corpus
propio de la organización" (`09:48`) SHALL retirarse. "En su domicilio" (`04:46`) SHALL aclararse
indicando de quién es el domicilio.

#### Scenario: Fila "sin IA" en Tabla 26

- **WHEN** se lee la Tabla 26 (`tab:declaracion-uso-ia`)
- **THEN** figura una fila sobre la redacción del corpus que declara "sin IA" (no se usó IA en las 119 descripciones)

#### Scenario: Etiquetado corregido en I.3

- **WHEN** se ejecuta `rg -n "etiquetado.*de los autores" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"`
- **THEN** no hay coincidencias; el texto atribuye el etiquetado a A1, T1, E1 y E2

#### Scenario: Atribución de autoría unificada

- **WHEN** se ejecuta `rg -n "por (los autores|ese autor)|uno de ellos" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** las reconstrucciones se atribuyen de la misma manera en todo el documento, conforme a la decisión registrada

#### Scenario: Frase de "dispositivo de dimensionamiento" una sola vez

- **WHEN** se ejecuta `rg -c "dispositivo de dimensionamiento y no el lugar de recolecci.n" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** el conteo total es exactamente 1

#### Scenario: "corpus propio de la organización" retirado y domicilio aclarado

- **WHEN** se ejecuta `rg -n "corpus propio de la organizaci.n" "docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex"` y se lee `04:46`
- **THEN** no hay coincidencias de "corpus propio de la organización", y "en su domicilio" indica de quién es el domicilio

#### Scenario: Gemini 3.1 en §7.5

- **WHEN** se ejecuta `rg -n "Gemini 3\.1" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** hay al menos una coincidencia referida a la validación retirada

### Requirement: Registro de decisiones y verificación de c-250

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL tener una sección c-250 con la tabla de
decisiones OQ-01 a OQ-05 (decisión literal, fecha, responsable), las tablas ANTES/DESPUES de cada
tarea de edición, el resultado de la coherencia y la release. Las cinco compuertas SHALL figurar como
CERRADAS (ninguna "EN CURSO" ni pendiente de autores). El encabezado de c-249 SHALL dejar de decir
"EN CURSO" si sigue en curso.

#### Scenario: Sección c-250 completa

- **WHEN** se lee la sección c-250 de `dictamen-correcciones.md`
- **THEN** figuran las cinco decisiones con respuesta, fecha y responsable, y una fila ANTES/DESPUES por tarea aplicada
- **AND** `rg -n "^## c-249.*EN CURSO" docs/Tesis/Correcciones/dictamen-correcciones.md` no devuelve coincidencias
- **AND** `rg -n "OQ-0[1-5].*(EN CURSO|pendiente|compuerta)" docs/Tesis/Correcciones/dictamen-correcciones.md` no devuelve coincidencias de una compuerta abierta