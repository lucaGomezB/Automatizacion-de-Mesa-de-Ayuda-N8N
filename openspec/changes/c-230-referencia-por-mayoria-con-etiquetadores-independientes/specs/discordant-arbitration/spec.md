## ADDED Requirements

### Requirement: ARB-009 — Referencia por mayoria de cinco etiquetadores independientes

La referencia de los casos del corpus fuera de muestra SHALL construirse por MAYORIA de cinco
etiquetadores independientes (`E3`, `E4`, `E6`, `E7`, `E8`) sobre el sector principal, en lugar de
por la regla del arbitro unico (`E5` cuando `E3` y `E4` difieren). La regla SHALL fijar un umbral de
mayoria de al menos `3` de los `5` etiquetadores y SHALL declararse de forma deterministica y
reproducible ANTES de ver cualquier etiqueta de `E6`, `E7` o `E8`; cambiarla despues de ver las
etiquetas invalida la referencia. La regla MUST NOT resolverse por consenso a posteriori de `E3` y
`E4`. Los casos sin mayoria absoluta SHALL marcarse de forma explicita (`sin_mayoria`), listarse con
sus etiquetas y resolverse con una regla de respaldo declarada de antemano (la referencia vigente de
arbitro unico, rotulada como respaldo), sin elegir una etiqueta «verdadera» ni promediar etiquetas.
El conjunto de verdad laxo SHALL derivarse de las etiquetas de los cinco etiquetadores con una regla
declarada, sin repetir el sector de la referencia. El conteo de casos `sin_mayoria` y el efecto de
su resolucion SHALL informarse sin ocultarse.

#### Scenario: Mayoria de cinco etiquetadores

- **WHEN** al menos `3` de los `5` etiquetadores asignan el mismo sector principal a un caso
- **THEN** la referencia de ese caso es ese sector mayoritario
- **AND** no se promedian ni se negocian las etiquetas de `E3` y `E4`

#### Scenario: Caso sin mayoria declarado

- **WHEN** ninguna etiqueta alcanza `3` de los `5` votos
- **THEN** el caso se marca `sin_mayoria` y se lista con sus etiquetas
- **AND** la referencia usa la regla de respaldo declarada, rotulada como respaldo, y el conteo se informa

#### Scenario: Regla declarada antes de ver las etiquetas

- **WHEN** se consulta el runbook de la referencia por mayoria
- **THEN** la regla de mayoria, la de respaldo y el tratamiento del conjunto laxo figuran declaradas con fecha anterior al etiquetado de `E6`-`E8`
- **AND** no se modificaron despues de ver las etiquetas

### Requirement: ARB-010 — Convocatoria, registro y consentimiento de `E6`, `E7` y `E8`

`evaluation/data/campana/registro_sujetos.csv` SHALL registrar `E6`, `E7` y `E8` con
`rol = etiquetador` y un codigo `P<n>` distinto (`P12`, `P13`, `P14`), sin nombres, correos ni
legajos. Cada uno SHALL ser una persona distinta de `E1`-`E5`, de los analistas originales `A1`, de
los autores `T1`-`T3` y de los operadores `O1`/`O2`; su `persona` MUST NOT figurar con ningun otro
rol y el solape SHALL verificarse con `validar_registro_sujetos`. La convocatoria SHALL ser de
personas no operadoras y no autoras. El consentimiento informado de `E6`, `E7` y `E8` SHALL
registrarse con la plantilla vigente (`docs/campana-medicion/confirmacion-posterior-consentimiento.md`),
que SHALL extenderse para admitir los alias nuevos; los originales firmados MUST NOT versionarse y la
correspondencia alias-identidad SHALL custodiarse FUERA del repositorio. Sin consentimiento registrado
el etiquetado de ese sujeto MUST NOT usarse en la referencia.

#### Scenario: Registro sin solape

- **WHEN** se agregan `E6`, `E7` y `E8` al registro
- **THEN** cada uno tiene `rol = etiquetador` y una `persona` distinta de las demas
- **AND** `validar_registro_sujetos` no reporta solape y ninguna fila contiene datos personales

#### Scenario: Consentimiento registrado sin identidad

- **WHEN** se revisa la plantilla y el registro de consentimiento
- **THEN** los alias `E6`, `E7` y `E8` figuran con su rol y sus fechas
- **AND** no figura ningun nombre real ni la correspondencia alias-identidad

#### Scenario: Sujeto sin consentimiento excluido

- **WHEN** un etiquetador nuevo no tiene consentimiento registrado
- **THEN** sus etiquetas no entran en la referencia por mayoria
- **AND** la limitacion se declara

### Requirement: ARB-011 — Cobertura y cegado del etiquetado de la referencia por mayoria

El etiquetado de `E6`, `E7` y `E8` SHALL realizarse a ciegas con los instrumentos existentes: la hoja
ciega (`id_caso` y descripcion pseudonimizada), una copia vacia de
`evaluation/data/plantilla_etiquetado.csv` y el codebook congelado. Los etiquetadores MUST NOT ver
ninguna etiqueta de `E3`, `E4` o `E5`, la referencia ni las predicciones del clasificador. El diseno
RECOMENDADO es etiquetar el corpus completo de `206` casos, de modo que la mayoria sea estimable en
todos y el kappa multievaluador se calcule sobre el corpus completo; el MINIMO viable es etiquetar
solo los `64` casos divergentes para reemplazar al arbitro unico. La cobertura efectivamente
alcanzada SHALL declararse y la referencia de los casos no etiquetados por los nuevos SHALL conservar
la de la etapa vigente, rotulada. Si no se consiguen los etiquetadores independientes o la
independencia no se acredita, el protocolo SHALL registrar la limitacion y el resultado MUST NOT
presentarse como ciego.

#### Scenario: Etiquetado ciego con los instrumentos existentes

- **WHEN** se entrega el paquete a `E6`, `E7` o `E8`
- **THEN** recibe la hoja ciega, la plantilla vacia y el codebook congelado
- **AND** no recibe etiquetas de `E3`/`E4`/`E5`, la referencia ni las predicciones

#### Scenario: Cobertura declarada

- **WHEN** se reporta la referencia por mayoria
- **THEN** figura la cobertura efectiva (corpus completo de `206` o solo los `64` divergentes)
- **AND** los casos sin etiquetar por los nuevos conservan la referencia de la etapa vigente, rotulada

#### Scenario: Limitacion declarada sin independencia

- **WHEN** no se consiguen los etiquetadores independientes o su independencia no se acredita
- **THEN** el protocolo registra la limitacion
- **AND** el resultado no se presenta como etiquetado ciego

### Requirement: ARB-012 — Artefactos versionados de la referencia por mayoria

Los artefactos de la referencia por mayoria SHALL versionarse en `evaluation/data/campana/` con su
SHA-256 en el README de la campana: la planilla unida del etiquetado de los cinco etiquetadores, el
JSON del corpus de referencia por mayoria, un sidecar con el origen de cada referencia y la bandera
`sin_mayoria`, el resultado del acuerdo multievaluador y el registro de sujetos actualizado. El
contrato de exactamente dos etiquetadores de la tarea `doble_etiquetado` (`evaluation/doble_etiquetado.py`)
y el de tres etiquetadores del arbitraje (`evaluation/arbitraje.py`) MUST NOT modificarse; la
referencia por mayoria SHALL construirse en un modulo propio que los reutilice. Los artefactos
congelados de la v9 y el corpus de ajuste SHALL quedar sin cambios.

#### Scenario: Hash y procedencia registrados

- **WHEN** se versionan los artefactos de la referencia por mayoria
- **THEN** el README registra el SHA-256 de cada archivo y el commit del clasificador congelado
- **AND** `git status` no muestra modificados el corpus de ajuste, `evaluation/report.md` ni los artefactos congelados

#### Scenario: Contratos de dos y de tres etiquetadores intactos

- **WHEN** se ejecutan las pruebas de `evaluation/doble_etiquetado.py` y de `evaluation/arbitraje.py`
- **THEN** sus contratos de cantidad de etiquetadores no cambiaron
- **AND** la referencia por mayoria vive en un modulo nuevo que los reutiliza

## MODIFIED Requirements

### Requirement: ARB-001 — Alcance: tercer etiquetador de arbitraje, no consenso a posteriori

El change original resolvio la discordancia de los casos entre `E3` y `E4` mediante un TERCER
etiquetador independiente `E5` y prohibio el consenso a posteriori de `E3` y `E4`. Ese arbitraje
unico SHALL quedar reemplazado, como referencia primaria del corpus fuera de muestra, por la regla de
mayoria de cinco etiquetadores independientes (ARB-009). La referencia de arbitro unico (`E5` cuando
`E3` y `E4` difieren) SHALL conservarse como referencia de comparacion y como regla de respaldo de
los casos sin mayoria, rotulada como tal. El protocolo MUST seguir prohibiendo el consenso a
posteriori de `E3` y `E4` y MUST NOT alterar las etiquetas ni la referencia del corpus de ajuste.

#### Scenario: Referencia primaria por mayoria, no por arbitro unico

- **WHEN** se prepara la referencia del corpus fuera de muestra
- **THEN** la referencia primaria se decide por la mayoria de los cinco etiquetadores
- **AND** la referencia de arbitro unico se conserva solo como comparacion y como respaldo rotulado

#### Scenario: Consenso a posteriori sigue prohibido

- **WHEN** `E3` y `E4` difieren en un caso
- **THEN** la referencia no se resuelve promediando, negociando ni consensuando sus etiquetas
- **AND** se aplican la mayoria de los cinco etiquetadores y la regla de respaldo

#### Scenario: Arbitraje por tercero, no por consenso

- **WHEN** se prepara la resolucion de los casos discordantes
- **THEN** la referencia primaria se decide por la mayoria de los cinco etiquetadores y el arbitro unico `E5` queda como referencia de comparacion y de respaldo
- **AND** no se resuelve promediando, negociando ni consensuando las etiquetas de `E3` y `E4`

### Requirement: ARB-002 — Registro del tercer etiquetador `E5`/`P11`

El registro de sujetos SHALL incorporar, ademas de `E5` con `rol = etiquetador` y codigo `P11`, a los
etiquetadores independientes `E6`, `E7` y `E8` con codigo `P12`, `P13` y `P14`. Cada uno SHALL ser una
persona distinta de las demas personas registradas (incluidos `E1`-`E5`, `A1`, `T1`-`T3` y
`O1`/`O2`) y su `persona` MUST NOT figurar con ningun otro rol. Ninguna fila SHALL contener nombres,
correos ni legajos y la correspondencia alias-identidad SHALL custodiarse FUERA del repositorio.

#### Scenario: `E5` y los nuevos etiquetadores registrados sin solape

- **WHEN** se agregan `E5`, `E6`, `E7` y `E8` al registro de sujetos
- **THEN** cada uno tiene `rol = etiquetador` y una `persona` distinta de las demas
- **AND** ninguna fila contiene nombre, correo ni legajo

#### Scenario: `E5` registrado sin solape

- **WHEN** se revisa el registro de sujetos
- **THEN** `E5` tiene `rol = etiquetador`, `persona = P11` y ninguna fila contiene datos personales
- **AND** `E6`, `E7` y `E8` tienen personas `P12`, `P13` y `P14` distintas de las demas

### Requirement: ARB-004 — Regla de arbitraje de la discordancia de tres vías

La regla SHALL declararse de forma explicita y deterministica ANTES de ver las etiquetas. Para la
referencia por mayoria, la regla SHALL definir el umbral (`>= 3` de `5`), el tratamiento de los casos
sin mayoria (`sin_mayoria`, con regla de respaldo declarada) y el del conjunto de verdad laxo. La
regla de arbitro unico original (`E3` y `E4` difieren: decide `E5`; tres etiquetas distintas: decide
`E5` con bandera `tres_vias`) SHALL conservarse como respaldo y como referencia de comparacion. La
regla SHALL quedar registrada en el runbook y MUST ser reproducible.

#### Scenario: Discordancia de dos o de tres resuelta por mayoria

- **WHEN** `E3` y `E4` difieren en un caso y los cinco etiquetadores etiquetan el caso
- **THEN** la referencia es el sector mayoritario si alcanza `3` de `5`
- **AND** si no alcanza mayoria, el caso se marca `sin_mayoria` y se aplica la regla de respaldo declarada

#### Scenario: Regla registrada y reproducible

- **WHEN** se lee el runbook de la referencia por mayoria
- **THEN** figuran el umbral, el tratamiento de `sin_mayoria`, el conjunto laxo y la regla de respaldo
- **AND** la regla produce un resultado reproducible

#### Scenario: Discordancia de dos resuelta por `E5`

- **WHEN** `E3` y `E4` difieren en un caso y los cinco etiquetadores no alcanzan mayoria
- **THEN** la referencia usa la regla de respaldo del arbitro unico y el caso se marca `sin_mayoria`
- **AND** el caso entra en la referencia con su rotulo de respaldo

#### Scenario: Discordancia de tres declarada

- **WHEN** los cinco etiquetadores asignan tres o mas sectores distintos sin mayoria
- **THEN** se aplica la regla declarada (marca `sin_mayoria` y respaldo del arbitro unico)
- **AND** la regla esta registrada en el runbook y produce un resultado reproducible
