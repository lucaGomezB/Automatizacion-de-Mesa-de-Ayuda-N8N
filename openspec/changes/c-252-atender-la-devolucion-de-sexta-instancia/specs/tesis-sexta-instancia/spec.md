## ADDED Requirements

### Requirement: Compuertas de autores de la sexta instancia registradas antes de editar

Los hechos que solo los autores pueden declarar SHALL resolverse mediante cinco compuertas registradas en la
sección c-252 de `docs/Tesis/Correcciones/dictamen-correcciones.md`, cada una con respuesta literal, fecha y
responsable: OQ-01 (cronología día por día de la campaña 2026-10 y autoría de los 165,3 s), OQ-02 (si
`tiempo_manual_s` incluye o no un componente de carga de unos 10 s), OQ-03 (ámbito laboral del régimen (a),
originales "crudos" y visto bueno escrito del director sobre la procedencia), OQ-04 (cronometraje "por
pares" desde el domicilio) y OQ-05 (composición del tiempo manual telefónico). Ninguna tarea que dependa de
una compuerta SHALL ejecutarse antes de que su respuesta esté registrada, y el contenido de una respuesta
MUST NOT inferirse ni completarse por el agente.

#### Scenario: Compuerta abierta bloquea la edición

- **WHEN** una tarea marcada GATED OQ-0n se intenta aplicar y la fila de OQ-0n no tiene respuesta registrada
- **THEN** la tarea no se ejecuta y el `.tex` correspondiente no cambia

#### Scenario: Compuertas cerradas antes de la release

- **WHEN** se lee la sección c-252 de `dictamen-correcciones.md` antes del tag `v1.6.6`
- **THEN** las cinco compuertas figuran con respuesta literal, fecha y responsable, y ninguna queda pendiente

### Requirement: Cronología día por día de la campaña 2026-10 (D-01)

El documento SHALL presentar una cronología día por día de la recolección, la redacción disociada, el doble
etiquetado con consenso, el cronometraje manual (por mitad y por operador) y las corridas automatizadas (02/10
para los 119 casos de correo y formulario; 05 y 06/10 para los 81 telefónicos), con la evidencia de cada
fecha (commit, archivo versionado o "declaración de los autores"). §4.2, §4.4, la Tabla 4 y la Figura 11
SHALL declarar que la fecha del cronometraje manual es una declaración de los autores acotada por el commit
`ea62576` del 09/10/2026, y la barra de la campaña manual de la Figura 11 MUST NOT extenderse más allá de esa
cota. Si la respuesta de OQ-01 no sostiene que el flujo manual precedió al automatizado para los 119 casos,
§4.2, la primera amenaza de §4.8 y la tercera explicación rival de §9.1 SHALL corregirse en consecuencia. El
Anexo I.1 SHALL decir quién midió o generó los 165,3 s de la versión del 3 de julio y sobre qué textos.

#### Scenario: Cronología con evidencia por fecha

- **WHEN** se lee la cronología de la campaña 2026-10 en el ejemplar
- **THEN** cada etapa tiene una fecha o intervalo y una evidencia nombrada, y las que no tienen registro fechado se rotulan como declaración de los autores

#### Scenario: Cota del 09/10 declarada

- **WHEN** se ejecuta `rg -n "ea62576|9-10-2026|09/10" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"`
- **THEN** §4.2, §4.4, la Tabla 4 y el pie de la Figura 11 remiten a la cota del commit del 09/10 como límite de la fecha declarada del cronometraje manual

#### Scenario: Barra de la Figura 11 acotada

- **WHEN** se lee la línea de la campaña manual en `docs/diagrams/cronograma.md`
- **THEN** su fecha final no es posterior al 2026-10-09 (o a la cota menor que registre OQ-01) y `cronograma.png` está regenerado

#### Scenario: Orden de los brazos coherente con OQ-01

- **WHEN** OQ-01 registra que el flujo automatizado precedió al manual en todos o parte de los 119 casos
- **THEN** `04-marco-metodologico.tex` (§4.2 y primera amenaza) y `08-discusion.tex` (tercera explicación rival) ya no afirman que el manual precedió al automatizado para esos casos ni que el orden sesga en contra de la hipótesis

#### Scenario: Autoría de los 165,3 s

- **WHEN** se lee la entrada de la versión del 3 de julio en el Anexo I.1
- **THEN** dice quién midió o generó los 165,3 s y sobre qué textos, conforme a OQ-01

### Requirement: Definición del tiempo manual con su historia registrada (D-02)

El documento SHALL declarar cuál de las dos descripciones del tiempo manual es la correcta (la de la v1.6.4,
lectura más una carga estimada de unos 10 s ya incluida en `tiempo_manual_s`, o la de la v1.6.5, sin
componente de carga), conforme a OQ-02, y por qué la otra figuró en una versión entregada al tribunal. El
Anexo I.1 SHALL registrarlo con el mismo criterio que los retiros anteriores. El texto MUST NOT sugerir un
cambio en los valores que no ocurrió: "retirado el componente de carga" y "componente que la presente
versión ya no contempla" SHALL reemplazarse. Si OQ-02 declara que la carga se sumó, la cifra primaria de la
sub-hipótesis 1 SHALL ser la del descuento de 10 s (65,6 %) y no 71,2 %, propagada a Resumen, Abstract,
Tablas 3, 10, 12, 23 y 29, octava amenaza, §8.1, §9.1, Conclusiones y `numeros-canonicos.md`.

#### Scenario: Frases que sugieren un cambio de datos retiradas

- **WHEN** se ejecuta `rg -n "retirado el componente de carga|ya no contempla" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias

#### Scenario: Nota de versiones del componente de carga

- **WHEN** se lee el Anexo I.1
- **THEN** registra qué decía la v1.6.4 sobre la carga, qué dice la versión vigente, cuál es la correcta y por qué la otra figuró en una versión entregada

#### Scenario: Cifra primaria según la rama de OQ-02

- **WHEN** OQ-02 registra que la carga se sumó
- **THEN** la Tabla 10, el Resumen y el Abstract presentan 65,6 % como cifra primaria y 71,2 % solo como lectura con la carga incluida, con valores tomados de una salida versionada

#### Scenario: Cifra primaria sin cambio en la rama B

- **WHEN** OQ-02 registra que la carga nunca se sumó
- **THEN** la cifra primaria sigue en 71,2 % y el Anexo I.1 declara inexacta la descripción de la v1.6.4

### Requirement: Procedencia del régimen (a) sin rastros de versiones anteriores (D-03)

El documento SHALL declarar, conforme a OQ-03, si los incidentes del régimen (a) ocurrieron en el ámbito
laboral de quienes los reportaron; si fue así, el capítulo legal SHALL mencionar el deber de
confidencialidad del art. 10 de la Ley 25.326 respecto de esos ámbitos. "del sector servicios y con sede en la
provincia de Mendoza" aplicado a las personas del círculo SHALL retirarse o explicarse en §1.2 y en las
Conclusiones. §4.4 SHALL explicar una sola vez el léxico corporativo del corpus («cliente», «sucursal»,
«estado de cuenta», «sistema principal»), los casos de trabajo citados en §8.5 y los sectores de la Tabla 18,
y SHALL decir que la composición 119/81 descansa en la declaración de los autores. El Anexo I.1 SHALL
registrar el cambio de origen respecto de la v1.6.4. La afirmación de que no existen originales SHALL quedar
conciliada con el registro del commit `ea625764` ("mantener los crudos fuera"). El visto bueno escrito del
director sobre la procedencia declarada SHALL incorporarse y citarse. Las ediciones del capítulo legal SHALL
mostrarse a los autores antes de escribirse.

#### Scenario: Caracterización organizacional retirada o explicada

- **WHEN** se ejecuta `rg -n "con sede en la provincia de Mendoza" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias aplicadas a las personas del círculo, o cada coincidencia tiene la explicación registrada en OQ-03

#### Scenario: Ámbito laboral y confidencialidad

- **WHEN** OQ-03 registra que los incidentes del régimen (a) ocurrieron en el ámbito laboral de los reportantes
- **THEN** §4.4 lo dice una sola vez y `11-aspectos-legales.tex` cita el art. 10 de la Ley 25.326 respecto de esos ámbitos

#### Scenario: Cambio de origen en la Nota de versiones

- **WHEN** se lee el Anexo I.1
- **THEN** registra que la v1.6.4 atribuía el régimen (a) a otro origen y que la versión vigente lo atribuye al círculo de los autores, con el motivo

#### Scenario: Visto bueno del director citado

- **WHEN** se busca la constancia del visto bueno del director sobre la procedencia
- **THEN** existe un documento fechado en el repositorio o en el expediente, y el Anexo I.1 lo cita

### Requirement: Extensión de las descripciones y composición del tiempo telefónico (D-04)

Un script versionado `evaluation/data/campana/analisis/analisis_sexta_instancia_c252.py`, con su prueba
`test_analisis_sexta_instancia_c252.py` escrita antes que el código, SHALL calcular la extensión media de las
descripciones en palabras y en caracteres por canal y por régimen, y el tiempo manual medio y por palabra por
canal, a partir de `data/corpus_evaluacion_pseudonimizado.json`, con salidas `.json`, `.md` y
`SHA256SUMS.txt`. La regla que asigna régimen a cada caso SHALL ser un parámetro explícito. §4.4, la sexta
amenaza, §8.1 y la Tabla 12 SHALL informar esas cifras y declarar qué parte de los 87,2 s es lectura y qué
parte es decisión, conforme a OQ-05; si no se midieron por separado, SHALL decirlo.

#### Scenario: Prueba primero

- **WHEN** se ejecuta `pytest evaluation/data/campana/analisis/test_analisis_sexta_instancia_c252.py` antes de crear el módulo
- **THEN** falla porque el módulo no existe

#### Scenario: Cifras por canal y régimen versionadas

- **WHEN** se ejecuta el script sobre el corpus
- **THEN** el JSON de salida contiene, para cada canal y cada régimen, el número de casos, la media de palabras, la media de caracteres y el tiempo manual medio, y su SHA-256 coincide con `SHA256SUMS.txt`

#### Scenario: Prosa con la composición declarada

- **WHEN** se lee la sexta amenaza y §8.1
- **THEN** informan la extensión media de las descripciones telefónicas y la composición de los 87,2 s según OQ-05, sin cifras que no provengan de la salida del script

### Requirement: Propagación al Resumen, Abstract y Tabla 10, y trazabilidad en I.1 e I.2 (D-05)

El Resumen, el Abstract y la Tabla 10 SHALL decir que el brazo manual midió solo la clasificación (no el
registro) e informar la reducción sin telefonía (63,3 %, o la que fije OQ-02). El texto MUST NOT describir
la medición manual como "registro manual". El Anexo I.1 SHALL registrar el cambio de fechas de la campaña
manual (junio-agosto a octubre, con la cota de D-01) y el del componente de carga (D-02). El Anexo I.2 SHALL
incluir la devolución de quinta instancia (25/11/2026) y la de sexta instancia (26/11/2026). El Resumen y el
Abstract SHALL conservar el tope de 250 palabras de prosa.

#### Scenario: Resumen y Abstract con el alcance del brazo manual

- **WHEN** se leen `00-resumen.tex` (Resumen y Abstract)
- **THEN** ambos dicen que el brazo manual midió solo la clasificación e informan la reducción sin telefonía, y cada uno tiene a lo sumo 250 palabras de prosa

#### Scenario: Tabla 10 con el alcance

- **WHEN** se lee la fila del tiempo de registro de `tab:sintesis-resultados`
- **THEN** indica que el brazo manual midió la clasificación e incluye la reducción sin telefonía

#### Scenario: Devoluciones listadas en I.2

- **WHEN** se lee la subsección "Revisiones que originaron las correcciones" del Anexo I
- **THEN** lista la devolución de quinta instancia del 25 de noviembre de 2026 y la de sexta instancia del 26 de noviembre de 2026

### Requirement: Coherencia y redacción de la sexta instancia (D-06)

El documento SHALL aclarar, conforme a OQ-04, cómo A1 y T1 se cronometraron por pares trabajando en el
domicilio de cada analista; SHALL unificar la atribución de las reconstrucciones del Anexo F con la de §4.4
("por uno de los autores"); SHALL reemplazar en §8.1 "respaldados por" por la fórmula de §4.5 (el registro
respalda la existencia y la procedencia de los incidentes, no la medición de extremo a extremo); SHALL
corregir en §7.5 que los titulares sean "distintos de los autores", porque los autores también son
reportantes; y SHALL reemplazar "registro histórico/retirado" por una forma sin barra.

#### Scenario: Fórmulas residuales retiradas

- **WHEN** se ejecuta `rg -n "respaldados por|distintos de los autores|hist.rico/retirado|redactadas por los autores" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias

#### Scenario: Domicilio y pares aclarados

- **WHEN** se lee el pasaje de §4.4 sobre el cronometraje de A1 y T1
- **THEN** describe dónde y cómo se cronometraron conforme a OQ-04, sin contradicción con "por pares"

### Requirement: Respuestas escritas a las diez preguntas de la sexta instancia

`docs/Tesis/Correcciones/respuestas-tribunal-sexta-instancia.md` SHALL responder, en orden, las diez
preguntas de la sección 6 de la devolución de sexta instancia, con el formato de
`respuestas-tribunal-quinta-instancia.md`: cada hecho remite a un artefacto versionado o se rotula como
declaración de los autores; solo alias; sin atribución a un modelo de lenguaje. Las preguntas 1 a 4 SHALL
estar respondidas antes de la release. Las cifras SHALL coincidir con el ejemplar `v1.6.6` según
`docs/Tesis/Correcciones/cotejar_cifras_respuestas.py`. `docs/defensa/respuestas-tribunal.md` SHALL quedar
alineado.

#### Scenario: Diez respuestas presentes

- **WHEN** se lee `respuestas-tribunal-sexta-instancia.md`
- **THEN** contiene diez respuestas numeradas, y la 1 a la 4 no tienen marcas de pendiente

#### Scenario: Cifras cotejadas

- **WHEN** se ejecuta el cotejo de cifras sobre el documento y el ejemplar
- **THEN** no reporta cifras ausentes del ejemplar ni valores retirados

### Requirement: Autoverificación previa a la versión de defensa

Antes del tag `v1.6.6` SHALL ejecutarse una autoverificación estilo CONEAU sobre el PDF compilado: cada frase
que la devolución de sexta instancia cita como defecto SHALL buscarse con `rg` en las fuentes; las fechas de
corridas SHALL cotejarse con los commits; la Figura 11 SHALL cotejarse con el texto; el visto bueno escrito
del director a la versión de defensa SHALL constar. El resultado SHALL registrarse en la sección c-252.

#### Scenario: Barrido de frases citadas

- **WHEN** se ejecuta el barrido de las frases citadas por la devolución (D-01 a D-06)
- **THEN** cada una está corregida o justificada en la sección c-252

#### Scenario: Visto bueno del director a la versión de defensa

- **WHEN** se prepara el tag `v1.6.6`
- **THEN** la sección c-252 cita la constancia fechada del visto bueno escrito del director a esa versión
