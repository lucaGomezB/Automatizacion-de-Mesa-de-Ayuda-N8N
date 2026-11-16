## ADDED Requirements

### Requirement: Referencia por mayoria de la muestra probabilistica divulgada solo en una version posterior a la defensa

Este requisito SHALL aplicarse solo en una version de la tesis posterior a la defensa y solo si la
referencia por mayoria de la muestra probabilistica se construyo (`evaluation-majority-reference`,
MR-006) con el acta de procedencia (MR-003) y la documentacion etica y legal (MR-004) cerradas, y si
la muestra se incorpora a la tesis por el requisito correspondiente de `c-229`. Si alguna condicion
falta, la tesis MUST NOT describir la referencia por mayoria como realizada. Cumplidas las
condiciones: el metodo SHALL describir el protocolo (numero de etiquetadores, umbral, tratamiento de
`sin_mayoria` sin arbitro unico, cegado, herramienta con marcas temporales propias y constancia de la
regla en custodia del director); los resultados SHALL informar el kappa de Fleiss con su IC y la
matriz de Cohen por pares, rotulados como fiabilidad entre los etiquetadores de esa muestra, y el
conteo de `sin_mayoria` con su efecto como rango; la limitacion de fiabilidad de la referencia de
`subsec:limitaciones-estudio` SHALL conservar el kappa `0,5569` del corpus de 200 casos y MUST NOT
afirmar que la referencia de esa muestra mejora o reemplaza la del corpus de 200; y
`subsec:consentimiento-derechos` SHALL declarar, solo por alias y codigos `P<n>`, que los
etiquetadores nuevos firmaron un consentimiento escrito previo cuyos originales custodia el director.
El texto MUST NOT reintroducir cifras, alias de etiquetadores ni descripciones del corpus retirado del
ejemplar, MUST NOT contener nombres reales ni la correspondencia alias-identidad y MUST NOT introducir
identificadores `c-NNN` en el cuerpo.

#### Scenario: Sin referencia construida, la tesis no cambia

- **WHEN** falta la referencia, el acta de procedencia o la documentacion etica y legal
- **THEN** ninguna seccion describe la referencia por mayoria como realizada

#### Scenario: Fiabilidad rotulada por muestra

- **WHEN** se leen los resultados de esa version
- **THEN** el kappa de Fleiss y la matriz por pares figuran como fiabilidad entre los etiquetadores de la muestra probabilistica
- **AND** el kappa `0,5569` del corpus de 200 se conserva en la limitacion, sin presentarse como superado

#### Scenario: Consentimiento por alias

- **WHEN** se lee `subsec:consentimiento-derechos` de esa version
- **THEN** figura el consentimiento escrito previo de los etiquetadores nuevos por alias y codigo `P<n>`
- **AND** no figura ningun nombre real

#### Scenario: Sin evidencia retirada

- **WHEN** se busca en `sections/*.tex` de esa version alguna cifra o alias de etiquetador de la evidencia retirada fuera de la nota de versiones
- **THEN** no hay coincidencias atribuibles a este change
