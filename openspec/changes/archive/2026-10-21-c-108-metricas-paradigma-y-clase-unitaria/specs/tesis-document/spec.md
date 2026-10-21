## ADDED Requirements

### Requirement: Marco metrico unificado en los capitulos de la tesis

El capitulo de marco metodologico SHALL declarar si la tarea se evalua como
monoetiqueta o multietiqueta, y el capitulo de resultados SHALL presentar la
exactitud estricta, la macro-F1 (cinco clases y cuatro clases estimables), el
micro-F1, la subset accuracy y el Hamming loss dentro de un unico marco que
declare, para cada metrica, su referencia de verdad y su relacion con las demas.
El documento MUST NOT presentar el micro-F1 ni las metricas de conjunto como
equivalentes de la exactitud de etiqueta unica, y SHALL explicitar la
penalizacion estructural que subset accuracy y Hamming loss imponen sobre una
salida forzada a una etiqueta. La comparacion con la literatura SHALL declarar la
diferencia de tarea (monoetiqueta en la literatura frente a multietiqueta
referenciada en este trabajo) cuando se contrasten exactitudes.

#### Scenario: Paradigma declarado en metodologia

- **WHEN** se lee la subseccion de analisis de datos del marco metodologico
- **THEN** se declara que la referencia de verdad del corpus es multietiqueta y que la salida del clasificador es una etiqueta principal
- **AND** se enuncian las metricas primarias monoetiqueta y las secundarias multietiqueta

#### Scenario: Marco unico en resultados

- **WHEN** se lee la subseccion de metricas del capitulo de resultados
- **THEN** la exactitud estricta, la macro-F1, el micro-F1, la subset accuracy y el Hamming loss aparecen en un solo marco con su referencia declarada
- **AND** el micro-F1 no se presenta como equivalente de la exactitud estricta

#### Scenario: Comparacion con la literatura matizada por tarea

- **WHEN** se compara la exactitud propia (`73,5 %`) con exactitudes de la literatura
- **THEN** el texto declara la diferencia de tarea (monoetiqueta frente a multietiqueta referenciada)
- **AND** no presenta el micro-F1 como una exactitud directamente comparable

### Requirement: Intervalos de confianza del kappa y por clase en la tesis

El marco metodologico y el capitulo de resultados SHALL reportar el intervalo de
confianza del coeficiente kappa de doble etiquetado y los intervalos de confianza
de las metricas por clase (precision, sensibilidad, F1), declarando el nivel de
confianza y el procedimiento de estimacion. El documento SHALL declarar como no
estimable la clase con soporte unitario (`Bases de Datos`, `n = 1`) y SHALL
excluirla del macro-F1 de umbral, conservando el macro-F1 de cinco clases como
valor informativo. Cuando la incertidumbre del kappa no sea computable desde las
fuentes disponibles, el texto SHALL declararlo de forma explicita como limitacion.

#### Scenario: IC del kappa reportado

- **WHEN** se lee el pasaje del doble etiquetado en metodologia o discusion
- **THEN** el kappa `0,87` se acompana de su intervalo de confianza con el nivel y el metodo declarados, o de la declaracion de que no es computable desde las fuentes permitidas
- **AND** el rotulo interpretativo sigue siendo "casi perfecto" (Landis & Koch)

#### Scenario: IC por clase reportado

- **WHEN** se lee la tabla de metricas por clase en resultados
- **THEN** cada clase estimable reporta su IC de precision, sensibilidad y F1
- **AND** la clase `Bases de Datos` figura como no estimable y sin IC

#### Scenario: Exclusion de la clase no estimable del umbral

- **WHEN** se lee el macro-F1 asociado al umbral de clasificacion
- **THEN** el macro-F1 de umbral se reporta sobre las cuatro clases estimables (`0,6508`)
- **AND** el macro-F1 de cinco clases (`0,5207`) se conserva como valor informativo
- **AND** el `0,0000` de `Bases de Datos` no se presenta como evidencia de desempeno
