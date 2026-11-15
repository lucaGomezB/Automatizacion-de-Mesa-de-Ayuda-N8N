## ADDED Requirements

### Requirement: Referencia por mayoria divulgada en metodo, resultados y limitaciones

`04-marco-metodologico.tex` SHALL describir la referencia del corpus fuera de muestra como la mayoria
de cinco etiquetadores independientes (`E3`, `E4`, `E6`, `E7`, `E8`), con el umbral (`>= 3` de `5`),
la regla de respaldo para los casos sin mayoria y el conteo `sin_mayoria`; y SHALL retirar la
descripcion de la referencia como la decision de un unico tercer etiquetador. `07-resultados.tex`
SHALL informar la exactitud estricta y las metricas por clase bajo la referencia por mayoria y bajo la
referencia vigente de arbitro unico, con sus intervalos de Wilson, el delta entre ambas y el veredicto
del umbral por lectura, rotulados; MUST NOT presentar una sola lectura como si la otra no existiera ni
ocultar el cambio de la cifra primaria. El kappa de Fleiss del acuerdo entre los cinco etiquetadores
SHALL figurar junto al kappa de Cohen ya reportado, rotulado como acuerdo multi-evaluador y distinto
del acuerdo del clasificador contra la referencia. `08-discusion.tex` SHALL acotar la limitacion de
fiabilidad de la referencia: SHALL declarar que la referencia ya no depende de un unico arbitro en el
`31 %` de los casos, SHALL informar la cobertura efectiva y el conteo `sin_mayoria`, y MUST NOT
afirmar que la independencia de los etiquetadores elimina por completo la fragilidad de la referencia
ni la dificultad de las clases de frontera. El texto MUST respetar el limite de paginas y no
introducir identificadores internos de cambio `c-NNN` en el cuerpo.

#### Scenario: Metodo describe la mayoria de cinco

- **WHEN** se lee la descripcion de la referencia fuera de muestra en `04-marco-metodologico.tex`
- **THEN** figura la mayoria de cinco etiquetadores, el umbral, la regla de respaldo y el conteo `sin_mayoria`
- **AND** no figura la referencia como decision de un unico tercer etiquetador

#### Scenario: Resultados informan las dos referencias

- **WHEN** se leen los resultados de la validacion fuera de muestra
- **THEN** figuran la exactitud estricta y las metricas por clase bajo la referencia por mayoria y bajo la referencia vigente, con sus intervalos de Wilson y el delta
- **AND** el veredicto del umbral se informa por lectura y no se oculta el cambio de la cifra primaria

#### Scenario: Acuerdo multi-evaluador rotulado

- **WHEN** se busca el kappa de Fleiss en los resultados o en el metodo
- **THEN** figura rotulado como acuerdo entre los cinco etiquetadores
- **AND** se distingue del kappa del clasificador contra la referencia

#### Scenario: Limitacion acotada sin sobreafirmar

- **WHEN** se lee la limitacion de fiabilidad de la referencia en `08-discusion.tex`
- **THEN** declara que la referencia ya no depende de un unico arbitro en el `31 %` de los casos y su cobertura efectiva
- **AND** no afirma que la independencia elimina por completo la fragilidad de la referencia

### Requirement: Registro y consentimiento de los etiquetadores independientes de la referencia por mayoria

El documento SHALL declarar a los etiquetadores independientes `E6`, `E7` y `E8` por alias
pseudonimizado, su rol de etiquetador y su independencia respecto de los autores, de los operadores y
de los demas etiquetadores, segun `evaluation/data/campana/registro_sujetos.csv`. La seccion 7
(`11-aspectos-legales.tex`, `subsec:consentimiento-derechos`) SHALL declarar que `E6`, `E7` y `E8`
fueron informados verbalmente antes de etiquetar del proposito, del caracter pseudonimizado, de la
voluntariedad y del derecho a retirarse, y que firmaron la confirmacion escrita posterior, cuyos
originales custodia el director y no se versionan. El repositorio SHALL conservar la plantilla de
confirmacion extendida para los alias nuevos y el registro de que fue obtenida. El texto MUST NOT
contener nombres reales ni la correspondencia alias-identidad: solo alias y codigos `P<n>`, y MUST
ser coherente con el registro de sujetos.

#### Scenario: Etiquetadores nuevos declarados

- **WHEN** se lee la descripcion del etiquetado de la referencia por mayoria
- **THEN** figuran `E6`, `E7` y `E8` por alias con su independencia segun el registro de sujetos
- **AND** la declaracion no incluye datos personales

#### Scenario: Consentimiento declarado

- **WHEN** se lee `subsec:consentimiento-derechos`
- **THEN** figuran la informacion verbal previa, la confirmacion escrita posterior y la custodia fisica para `E6`, `E7` y `E8`
- **AND** solo figuran alias y codigos `P<n>`

### Requirement: Trabajo futuro actualizado tras ejecutar la referencia por mayoria

La linea de `10-recomendaciones.tex` que proponia conseguir «mas etiquetadores independientes» para
estimar la mayoria sin depender de un unico tercer etiquetador SHALL retirarse como trabajo futuro
pendiente, porque este change la ejecuta. La subseccion SHALL reformularse hacia el siguiente paso
faltante (por ejemplo, ampliar la referencia por mayoria a nuevas campanas o a un corpus de
composicion natural), declarar su criterio de exito y MUST NOT proponer como proximo paso lo ya
realizado. La linea de `subsec:frontera-sistemas` SHALL conservar su criterio de exito y MUST NOT
reabrir la discusion de un unico arbitro ya resuelta.

#### Scenario: Linea ya ejecutada retirada

- **WHEN** se leen las lineas de trabajo futuro del capitulo de recomendaciones
- **THEN** ninguna propone conseguir mas etiquetadores independientes como proximo paso
- **AND** cada linea declara un criterio de exito

#### Scenario: Criterio de exito presente

- **WHEN** se lee la subseccion reformulada
- **THEN** declara su criterio de exito y su alcance
- **AND** no propone como pendiente la referencia por mayoria ya construida
