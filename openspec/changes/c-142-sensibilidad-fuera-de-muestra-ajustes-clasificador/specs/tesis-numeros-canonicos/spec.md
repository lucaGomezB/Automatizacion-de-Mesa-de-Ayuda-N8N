## ADDED Requirements

### Requirement: Registro de los valores de sensibilidad frente al ajuste con el corpus

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar, en una seccion propia, cada valor del analisis de sensibilidad frente al ajuste del clasificador con el corpus que la tesis cite o que sostenga su lectura: variante principal (casos, aciertos, exactitud, IC de Wilson y cobertura), descomposicion pareada, referencia historica y su control de fidelidad, exactitud global con Gemini fijo y contraste entre etapas con el vocabulario previo (o su declaracion de no computable), efecto de las reglas de frontera del prompt por nivel (o su declaracion de no cuantificado) y, si aplica, los resultados sobre el conjunto de preproduccion. Cada valor SHALL declarar su procedencia (linea de `evaluation/report_sensibilidad_ajustes.md`, archivo de un brazo de la ablacion o derivacion aritmetica explicita desde valores versionados), su estado (`vigente` como valor de sensibilidad, o `condicional` mientras su checkpoint siga abierto) y el rotulo "sensibilidad: no reemplaza valores canonicos". Las filas de `97/131` (`0,7405`) y de `88/130` (`0,6769`) SHALL llevar una nota que las califique como estimaciones dentro de la muestra y remita a esa seccion. La seccion de decisiones no resolubles SHALL registrar la no factibilidad de la variante por pliegues, la version del prompt de la cache FORCE-ESCALATE (o su indeterminacion) y el desenlace sobre el conjunto de preproduccion. El memo MUST NOT modificar ningun valor vigente previo.

#### Scenario: Valores con procedencia, estado y rotulo

- **WHEN** se recorre la seccion de sensibilidad del memo
- **THEN** cada valor declara una procedencia verificable, un estado en `{vigente, condicional}` y el rotulo de sensibilidad
- **AND** cada `archivo:linea` citado existe y contiene el valor

#### Scenario: Valores canonicos intactos

- **WHEN** se compara el memo antes y despues del change
- **THEN** ninguna celda de valor con estado `vigente` previo cambio
- **AND** los cambios en filas previas se limitan a notas agregadas

#### Scenario: Notas de estimacion dentro de la muestra

- **WHEN** se leen las filas de `97/131` y de `0,7405` frente a `0,6769`
- **THEN** cada una incluye la nota que la califica como estimacion dentro de la muestra y la remision a la seccion de sensibilidad

#### Scenario: Decisiones no resolubles registradas

- **WHEN** se lee la seccion de decisiones no resolubles
- **THEN** figuran la variante por pliegues como no factible con su motivo y su condicion de reversibilidad, la clasificacion de la version del prompt de la cache FORCE-ESCALATE y el desenlace sobre el conjunto de preproduccion

#### Scenario: Salidas no computables sin valores

- **WHEN** una salida del analisis no fue computable con los artefactos disponibles
- **THEN** el memo la registra como no computable, con su motivo
- **AND** no consigna ningun valor estimado para ella

### Requirement: Corridas de sensibilidad sin efecto sobre los valores canonicos

Una corrida de sensibilidad, sea la re-medicion offline con otra configuracion del clasificador o una ablacion que invoque al proveedor, MUST NOT sobrescribir las predicciones oficiales, `evaluation/report.md` ni ningun valor canonico vigente. Sus resultados SHALL escribirse en archivos separados, rotulados con la configuracion evaluada, el hash del prompt cuando corresponda y la fecha, y SHALL citarse en la tesis solo como sensibilidad. El reemplazo de un valor canonico por uno de sensibilidad SHALL requerir una decision explicita del usuario registrada en el memo.

#### Scenario: Archivos separados y rotulados

- **WHEN** se ejecuta una corrida de sensibilidad
- **THEN** sus salidas se escriben en archivos distintos de `evaluation/predicciones.json` y `evaluation/report.md`, rotulados con su configuracion y su fecha

#### Scenario: Canonicos sin cambio ante resultados distintos

- **WHEN** una corrida de sensibilidad produce valores distintos de los canonicos
- **THEN** los valores vigentes del memo y de la tesis no cambian
- **AND** la tesis presenta los valores de sensibilidad como tales, con remision a su seccion del memo
