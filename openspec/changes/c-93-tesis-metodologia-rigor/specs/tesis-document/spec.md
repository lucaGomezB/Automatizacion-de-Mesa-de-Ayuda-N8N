## ADDED Requirements

### Requirement: Cálculo reproducible del tamaño muestral

El capítulo de marco metodológico SHALL publicar la fórmula del tamaño muestral,
los insumos empleados (tamaño del universo `N`, nivel de confianza o `z`,
proporción esperada `p` y margen de error `e`) y el resultado, de modo que el
valor declarado sea reproducible aritméticamente. Si la corrección por finitud
se aplica, MUST declararse la variante de la fórmula usada. El valor declarado
del corpus (`n = 200`) MUST ser consistente con los insumos publicados; en caso
contrario, el documento MUST corregir el insumo que no lo reproduce (por ejemplo
el margen de error declarado) o el propio tamaño declarado.

#### Scenario: Fórmula e insumos publicados

- **WHEN** se lee la subsección de población, muestra y corpus
- **THEN** el texto enuncia la fórmula del tamaño muestral con la corrección por finitud
- **AND** declara `N`, `z` (o el nivel de confianza), `p` (o `p(1−p)`) y `e`

#### Scenario: Tamaño declarado reproducible

- **WHEN** se recalcula el tamaño muestral a partir de los insumos publicados
- **THEN** el resultado reproduce el tamaño declarado del corpus
- **AND** no se declara un margen de error que, con los demás insumos, arroje un tamaño distinto del publicado

### Requirement: Evidencia de cobertura de pruebas

Toda afirmación de cobertura de pruebas (por ejemplo «superior al 80 %» o
«87 %») SHALL estar respaldada por el reporte de cobertura y el comando que lo
genera. Si el reporte no se publica, la cifra MUST retirarse del documento. La
cifra declarada MUST ser consistente entre los capítulos que la mencionan.

#### Scenario: Cifra respaldada por reporte y comando

- **WHEN** se lee una afirmación de cobertura de pruebas unitarias
- **THEN** el documento publica (o referencia como anexo) el reporte de cobertura y el comando que lo genera
- **AND** la cifra declarada coincide con la del reporte

#### Scenario: Cifra retirada si no hay evidencia

- **WHEN** no existe reporte de cobertura publicado
- **THEN** el documento no afirma una cifra porcentual de cobertura
- **AND** las menciones de cobertura en los distintos capítulos son consistentes entre sí

### Requirement: Análisis de potencia estadística a priori

El capítulo de marco metodológico SHALL incluir un análisis de potencia
estadística a priori para el contraste principal, con los supuestos declarados
(nivel de significancia, potencia objetivo, tamaño del efecto asumido o mínimo
detectable y tamaño muestral) y la conclusión sobre la suficiencia del diseño.
El análisis MUST ser coherente con el reconocimiento del tamaño muestral como
amenaza a la validez de conclusión.

#### Scenario: Análisis de potencia presente

- **WHEN** se lee la subsección de análisis estadístico o de amenazas a la validez
- **THEN** existe un análisis de potencia a priori con sus supuestos declarados
- **AND** se reporta la potencia resultante o el efecto mínimo detectable para el tamaño muestral del estudio

#### Scenario: Coherencia con la amenaza de validez de conclusión

- **WHEN** se compara el análisis de potencia con la amenaza de tamaño muestral
- **THEN** ambos usan el mismo tamaño muestral
- **AND** la conclusión sobre la potencia no contradice el reconocimiento de la amenaza

### Requirement: Tratamiento honesto del confundido de la rotación de operadores

Cuando el documento declare rotación o contrabalanceo de operadores entre las
mitades del corpus, SHALL reconocer explícitamente si dicha rotación queda
confundida con el efecto del operador dado el número de operadores y de mitades
empleados. Si la rotación no elimina el confundido, el documento MUST NOT
presentarla como mitigación no calificada del efecto de aprendizaje.

#### Scenario: Confundido reconocido

- **WHEN** se lee la descripción del contrabalanceo del orden de procesamiento
- **THEN** el texto declara cuántos operadores y cuántas mitades intervinieron
- **AND** reconoce si la rotación de operadores queda confundida con el efecto del operador

#### Scenario: Mitigación no sobrevendida

- **WHEN** se lee la lista de amenazas a la validez y sus mitigaciones
- **THEN** la rotación de operadores no se presenta como mitigación no calificada si está confundida
- **AND** se declara la limitación resultante o el rediseño de la afirmación

### Requirement: Criterios de exclusión del corpus

El capítulo de marco metodológico SHALL declarar los criterios de exclusión de
incidentes del corpus (al menos duplicados, descripciones vacías o
insuficientes, y casos multicategoría), de forma coherente con los patrones de
error reportados en el análisis de errores.

#### Scenario: Criterios de exclusión declarados

- **WHEN** se lee la subsección de población, muestra y corpus
- **THEN** se enumeran los criterios de exclusión aplicados a los incidentes
- **AND** se indica cómo se trataron duplicados, descripciones vacías y casos multicategoría

#### Scenario: Coherencia con el análisis de errores

- **WHEN** se comparan los criterios de exclusión con los patrones de error del capítulo de resultados
- **THEN** los patrones de error dominantes (descripciones cortas, mezcla de categorías) están contemplados por los criterios de exclusión o su exclusión está justificada

### Requirement: Demarcación del método de investigación

El documento SHALL distinguir el método de investigación (diseño experimental,
muestreo, análisis) del método de construcción del artefacto (gestión del
proyecto). La descripción del marco de trabajo de construcción (por ejemplo
Scrumban) MUST NOT presentarse como la metodología de investigación ni quedar
indistinguible de ella.

#### Scenario: Método de investigación distinguible

- **WHEN** se lee el capítulo de marco metodológico
- **THEN** el método de investigación y el método de construcción del artefacto son distinguibles
- **AND** el marco de gestión del proyecto queda demarcado (reubicado o rotulado) como método de construcción, no como metodología de investigación

### Requirement: Declaración de los analistas etiquetadores

El documento SHALL declarar quiénes realizaron el etiquetado del corpus, su
independencia respecto de los autores del trabajo y si alguno de ellos participó
además como operador del brazo manual. Esta declaración MUST ser coherente con
el cómputo del acuerdo inter-evaluador.

#### Scenario: Analistas declarados

- **WHEN** se lee la descripción del doble etiquetado independiente
- **THEN** se declaran los analistas etiquetadores
- **AND** se declara su independencia (o dependencia) respecto de los autores

#### Scenario: Solapamiento con el brazo manual declarado

- **WHEN** un analista etiquetador también operó el brazo manual
- **THEN** el documento lo declara explícitamente
- **AND** se discute la implicancia para la independencia de la verdad fundamental

### Requirement: Criterio de exactitud sin zona de rechazo

El criterio del umbral de exactitud del clasificador (por ejemplo el 85 % del
segundo objetivo específico) SHALL formularse como un umbral de desempeño
verificable contra el resultado observado y su intervalo de confianza, sin
invocar la «zona de rechazo» de un contraste de hipótesis sobre tiempos. El
documento MUST NOT confundir el contraste `H0`/`H1` sobre la mediana de tiempos
con el umbral de exactitud.

#### Scenario: Criterio de exactitud reformulado

- **WHEN** se lee la fundamentación del umbral de exactitud
- **THEN** el criterio se expresa como umbral de desempeño (o pertenencia del intervalo de confianza al umbral)
- **AND** no se invoca una zona de rechazo de hipótesis para la exactitud

#### Scenario: Sin confusión con el contraste de tiempos

- **WHEN** se compara el criterio de exactitud con la formulación de `H0`/`H1`
- **THEN** ambos se refieren a variables distintas (exactitud vs. mediana de tiempo)
- **AND** no se reutiliza el vocabulario del contraste de tiempos para justificar el umbral de exactitud
