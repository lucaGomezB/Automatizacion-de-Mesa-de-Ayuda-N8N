## ADDED Requirements

### Requirement: Incertidumbre del kappa y de las metricas por clase

El memo canonico SHALL registrar el intervalo de confianza del coeficiente kappa
de doble etiquetado y los intervalos de confianza de las metricas por clase
(precision, sensibilidad y F1 una contra el resto), junto con el procedimiento de
estimacion empleado y su nivel de confianza. El memo SHALL declarar como no
estimable toda clase con soporte unitario y SHALL excluirla de los estimadores
agregados de umbral. Cuando una incertidumbre no sea computable a partir de las
fuentes primarias permitidas, el memo SHALL declararlo de forma explicita con la
condicion de reversibilidad, en lugar de presentar el valor puntual como si
tuviera incertidumbre cuantificada.

#### Scenario: IC por clase registrado con procedimiento

- **WHEN** se lee la seccion de metricas del memo
- **THEN** cada clase estimable declara su IC de precision, sensibilidad y F1
- **AND** se declara el metodo de estimacion (por ejemplo Wilson o bootstrap percentil) y el nivel de confianza

#### Scenario: Clase con soporte unitario sin IC

- **WHEN** se recorre la tabla de metricas por clase del memo
- **THEN** la clase con `n = 1` (`Bases de Datos`) se declara no estimable y sin IC
- **AND** su valor puntual NO se presenta como evidencia de desempeno del clasificador

#### Scenario: IC del kappa registrado o declarado no estimable

- **WHEN** se lee el registro de incertidumbre del kappa de doble etiquetado
- **THEN** figura su IC con el procedimiento de estimacion, o bien la declaracion explicita de que no es computable desde las fuentes permitidas y la condicion bajo la cual se incorporaria

### Requirement: Marco metrico unificado mono y multietiqueta

El memo canonico SHALL presentar la exactitud estricta, la macro-F1 (cinco y
cuatro clases estimables), el micro-F1, la subset accuracy y el Hamming loss
dentro de un unico marco que declare, para cada metrica, la tarea de referencia
(monoetiqueta o multietiqueta) y su relacion con las demas. El memo MUST NOT
presentar el micro-F1 ni las metricas de conjunto como equivalentes de la
exactitud de etiqueta unica, y SHALL explicitar la penalizacion estructural que
las metricas de conjunto imponen sobre una salida forzada a una etiqueta.

#### Scenario: Marco unico con referencia declarada

- **WHEN** se lee la seccion de metricas del memo
- **THEN** cada metrica declara si su referencia de verdad es monoetiqueta o multietiqueta
- **AND** se enuncian las metricas primarias (monoetiqueta) y las secundarias (multietiqueta) en una sola tabla o marco

#### Scenario: No equivalencia de micro-F1 y exactitud

- **WHEN** se compara el micro-F1 con la exactitud estricta en el memo
- **THEN** el memo declara que no son equivalentes y explica por que difieren (`0,6654` frente a `0,7350`)
- **AND** no deja el micro-F1 rotulado como exactitud multietiqueta
