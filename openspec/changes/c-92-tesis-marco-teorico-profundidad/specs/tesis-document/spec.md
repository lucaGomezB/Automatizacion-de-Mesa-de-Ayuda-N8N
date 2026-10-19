# Delta for tesis-document

## ADDED Requirements

### Requirement: Profundidad conceptual del eje de modelos de lenguaje grandes

La seccion 2.4 del marco teorico SHALL tratar de forma explicita los conceptos de
prompting (incluidas las modalidades zero-shot y few-shot), calibracion de la
confianza, alucinacion, sensibilidad al idioma y evaluacion de modelos de lenguaje
grandes. El texto SHALL definirlos y vincularlos con el uso que la tesis hace de
ellos en los capitulos 4, 6, 7 y 8. La seccion SHALL apoyarse en al menos tres
referencias adicionales verificables respecto de las citadas actualmente en 2.4, y
SHALL NOT limitar el tratamiento del eje a la descripcion de la arquitectura
Transformer y del aprendizaje en contexto.

#### Scenario: Conceptos operativos definidos antes de su uso

- **WHEN** se lee la seccion 2.4 del PDF compilado
- **THEN** se definen prompting, calibracion de la confianza, alucinacion, sensibilidad al idioma y evaluacion de LLM
- **AND** cada concepto se relaciona con la forma en que la tesis lo utiliza en los capitulos posteriores

#### Scenario: Respaldo bibliografico suficiente del eje central

- **WHEN** se cuentan las referencias citadas en la seccion 2.4
- **THEN** hay al menos tres referencias adicionales verificables respecto de la version auditada
- **AND** al menos una de ellas es posterior a 2022

### Requirement: Definicion multiclase de la exactitud

La seccion 2.7 SHALL definir la exactitud global directamente para problemas
multiclase, como la proporcion de predicciones correctas sobre el total de
predicciones, en coherencia con la matriz de confusion 5x5 del Capitulo 7. La
tesis SHALL NOT presentar la formula binaria `(TP+TN)/(TP+TN+FP+FN)` como
definicion principal de la exactitud global ni corregirla en una oracion
posterior.

#### Scenario: Formula binaria ausente como definicion principal

- **WHEN** se busca la formula `(TP+TN)/(TP+TN+FP+FN)` en el capitulo 2
- **THEN** no aparece como definicion principal de la exactitud
- **AND** la exactitud se define una sola vez, en clave multiclase

#### Scenario: Coherencia con la evaluacion multiclase

- **WHEN** se compara la definicion de exactitud de 2.7 con la matriz de confusion y las metricas del Capitulo 7
- **THEN** ambas describen un problema de cinco clases
- **AND** la definicion no introduce verdaderos negativos como parte del calculo global

### Requirement: Alcance real del reconocimiento automatico del habla

La seccion 2.5 SHALL distinguir entre el estado del arte del reconocimiento
automatico del habla y la tecnologia efectivamente utilizada por el sistema. La
tesis SHALL NOT afirmar que los modelos preentrenados de Whisper facilitan o
habilitan la integracion del canal telefonico del sistema propuesto. Si Whisper se
conserva como antecedente teorico, el texto SHALL marcarlo como no utilizado en la
implementacion y SHALL remitir a la transcripcion nativa de Twilio descrita en la
seccion 6.4.

#### Scenario: Whisper no se presenta como componente del sistema

- **WHEN** se lee la seccion 2.5 del PDF compilado
- **THEN** no se afirma que Whisper se integre al canal telefonico del sistema
- **AND** se indica que la transcripcion efectiva la provee el servicio nativo de Twilio

#### Scenario: Antecedente teorico correctamente delimitado

- **WHEN** la seccion 2.5 menciona Whisper
- **THEN** lo presenta como antecedente del estado del arte del ASR
- **AND** aclara que no forma parte de la implementacion desarrollada

### Requirement: Justificacion de la persistencia frente a alternativas concretas

La seccion 2.6 SHALL justificar la eleccion de PostgreSQL comparandola con al menos
dos alternativas tecnologicas concretas, entre ellas un motor de documentos y un
motor clave-valor. La justificacion SHALL apoyarse en requisitos del dominio
(integridad referencial, transacciones, consultas relacionales y auditoria) y SHALL
NOT limitarse a una contraposicion generica entre modelos relacionales y no
relacionales.

#### Scenario: Alternativas concretas consideradas

- **WHEN** se lee la seccion 2.6 del PDF compilado
- **THEN** se nombran al menos dos alternativas concretas a PostgreSQL
- **AND** se explica por que no satisfacen los requisitos del dominio

#### Scenario: Justificacion anclada en requisitos del dominio

- **WHEN** se lee la justificacion de PostgreSQL
- **THEN** se vinculan integridad referencial, transacciones y auditoria con las necesidades de la mesa de ayuda
- **AND** no se sostiene la eleccion solo con la expresion generica "alternativas no relacionales"

### Requirement: Respaldo de la afirmacion sobre idiomas del corpus

La seccion 1.7 SHALL respaldar con al menos una cita verificable la afirmacion de
que la mayoria de los estudios publicados sobre clasificacion automatica de tickets
utilizan corpus en ingles, aleman o portugues, o bien SHALL reformular la
afirmacion para que no requiera un respaldo cuantitativo no provisto. Las citas
utilizadas SHALL provenir de las referencias incorporadas por c-78; este change
SHALL NOT duplicar la modernizacion bibliografica ni editar
`Bibliography_base.bib`.

#### Scenario: Afirmacion comparativa respaldada o reformulada

- **WHEN** se lee la seccion 1.7 del PDF compilado
- **THEN** la afirmacion sobre los idiomas de los corpus esta respaldada por al menos una cita verificable de c-78, o bien fue reformulada sin el alcance cuantitativo
- **AND** no queda una generalizacion sobre la literatura sin referencia

#### Scenario: Sin duplicacion del trabajo bibliografico

- **WHEN** se revisa el diff del change
- **THEN** no se agregan ni modifican entradas de `Bibliography_base.bib`
- **AND** las referencias usadas ya existen por c-78

### Requirement: Atribucion editorial de ITIL Service Operation 2011

La seccion 2.2 SHALL atribuir la edicion de 2011 de ITIL Service Operation a The
Stationery Office (TSO) por encargo del Cabinet Office, sin presentarla como una
publicacion directa del Office of Government Commerce. La correccion del campo
bibliografico `OGC2011_itil` SHALL quedar a cargo de c-78 (B3); este change SHALL
NOT editar la entrada `.bib`.

#### Scenario: Atribucion editorial correcta en el cuerpo

- **WHEN** se lee la seccion 2.2 del PDF compilado
- **THEN** la edicion de 2011 se atribuye a TSO/Cabinet Office
- **AND** no se afirma que el Office of Government Commerce sea el editor de la edicion de 2011

#### Scenario: Correccion bibliografica delegada

- **WHEN** se revisa el alcance del change
- **THEN** el texto remite a la correccion de metadatos de c-78
- **AND** no se modifica `Bibliography_base.bib`
