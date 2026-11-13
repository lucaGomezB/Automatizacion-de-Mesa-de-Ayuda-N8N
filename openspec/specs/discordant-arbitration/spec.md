# discordant-arbitration Specification

## Purpose
Define el protocolo, los instrumentos y los artefactos del arbitraje de los casos
discordantes del corpus independiente por un tercer etiquetador `E5` (código `P11`) y del
refuerzo de las clases chicas, de modo que la referencia cubra los `150` casos y se levante
el sesgo de exclusión sin resolver la discordancia por consenso a posteriori.

## Requirements

### Requirement: ARB-001 — Alcance: tercer etiquetador de arbitraje, no consenso a posteriori

El arbitraje SHALL resolver la discordancia de los `47` casos entre `E3` y `E4` mediante un
TERCER etiquetador independiente `E5`, y MUST NOT resolverse por consenso a posteriori de
`E3` y `E4` (el protocolo de la campaña lo prohíbe, porque sesgaría el kappa y la
referencia). El arbitraje SHALL operar sobre la referencia del corpus independiente y MUST
NOT alterar las etiquetas ni la referencia del corpus de ajuste.

#### Scenario: Arbitraje por tercero, no por consenso

- **WHEN** se prepara la resolución de los `47` casos discordantes
- **THEN** la referencia se decide con la etiqueta del tercer etiquetador `E5`
- **AND** no se resuelve promediando, negociando ni consensuando las etiquetas de `E3` y `E4`

### Requirement: ARB-002 — Registro del tercer etiquetador `E5`/`P11`

`evaluation/data/campana/registro_sujetos.csv` SHALL registrar `E5` con `rol = etiquetador`
y un código `P11`, sin nombres, correos ni legajos. `E5` SHALL ser una persona distinta de
`E1`-`E4`, de los analistas originales `A1`, de los autores `T1`-`T3` y de los operadores
`O1`/`O2`; su `persona` MUST NOT figurar con ningún otro rol. La correspondencia
alias-identidad SHALL custodiarse FUERA del repositorio.

#### Scenario: `E5` registrado sin solape

- **WHEN** se agrega `E5` al registro de sujetos
- **THEN** tiene `rol = etiquetador` y `persona = P11`, distinta de las demás `persona`
- **AND** ninguna fila contiene nombre, correo ni legajo

### Requirement: ARB-003 — Etiquetado ciego de los casos discordantes con el codebook congelado

El tercer etiquetador `E5` SHALL etiquetar los casos discordantes a ciegas: SHALL ver solo
la hoja ciega (`id_caso` y descripción pseudonimizada), la plantilla `C1`
(`evaluation/data/plantilla_etiquetado.csv`) y el codebook congelado. `E5` MUST NOT ver la
etiqueta de `E3`, la de `E4`, la referencia ni la predicción del clasificador. Si no se
consigue un etiquetador independiente, la limitación SHALL declararse
(`estado_cegado: limitacion_declarada`) y el resultado MUST NOT presentarse como ciego.

#### Scenario: Cegado de `E5`

- **WHEN** se entrega el paquete a `E5`
- **THEN** recibe la hoja ciega, la plantilla `C1` y el codebook congelado
- **AND** no recibe la etiqueta de `E3`, la de `E4`, la referencia ni las predicciones

#### Scenario: Limitación declarada sin independencia

- **WHEN** no se consigue un tercer etiquetador independiente
- **THEN** el protocolo registra `estado_cegado: limitacion_declarada`
- **AND** el resultado no se presenta como etiquetado ciego

### Requirement: ARB-004 — Regla de arbitraje de la discordancia de tres vías

El protocolo SHALL declarar la regla de arbitraje de forma explícita antes de ver las
etiquetas de `E5`. La referencia de un caso donde `E3` y `E4` difieren SHALL ser la etiqueta
de `E5`. La regla SHALL definir el tratamiento del caso en que las tres etiquetas
(`E3`, `E4`, `E5`) son distintas y el del conjunto de verdad laxo en los casos arbitrados.
La regla SHALL ser determinística y reproducible, y SHALL quedar registrada en el runbook.

#### Scenario: Discordancia de dos resuelta por `E5`

- **WHEN** `E3` y `E4` difieren en un caso y `E5` lo etiqueta
- **THEN** la referencia de ese caso es la etiqueta de `E5`
- **AND** el caso entra en la referencia

#### Scenario: Discordancia de tres declarada

- **WHEN** `E3`, `E4` y `E5` asignan tres sectores distintos a un caso
- **THEN** se aplica la regla declarada para ese caso
- **AND** la regla está registrada en el runbook y produce un resultado reproducible

### Requirement: ARB-005 — n efectivo de `150` y remoción del sesgo de exclusión

Con el arbitraje de los `47` casos, la referencia SHALL cubrir los `150` casos del corpus
independiente y el n efectivo SHALL ser `150`. La exclusión por discordancia (que sesgaba la
referencia hacia los casos fáciles, c-191) SHALL quedar remoción: el resultado SHALL
reportarse sobre los `150` casos y MUST NOT seguir declarando un n efectivo menor.

#### Scenario: Referencia sobre los `150`

- **WHEN** se construye la referencia arbitrada
- **THEN** cubre los `150` casos del corpus independiente
- **AND** el n efectivo del resultado es `150`

#### Scenario: Sesgo de exclusión removido

- **WHEN** se reporta el resultado del corpus independiente arbitrado
- **THEN** la exclusión por discordancia deja de aplicarse
- **AND** el texto no declara el sesgo hacia casos fáciles de la etapa anterior

### Requirement: ARB-006 — Refuerzo de las clases chicas

El protocolo SHALL incorporar casos nuevos para las clases de soporte chico del consenso
anterior (`Sistemas` con `5` y `Bases de Datos` con `13`, sobremuestreada), etiquetados con
el mismo procedimiento (doble etiquetado `E3`/`E4` y arbitraje `E5` cuando corresponda), de
modo que sus métricas por clase queden estimables. Los casos de refuerzo SHALL pasar
`verificar_no_solape` contra el corpus de ajuste como los demás.

#### Scenario: Clases chicas reforzadas

- **WHEN** se incorporan casos de refuerzo para `Sistemas` y `Bases de Datos`
- **THEN** sus métricas por clase quedan estimables con el soporte ampliado
- **AND** los casos de refuerzo no solapan el corpus de ajuste

### Requirement: ARB-007 — Validador, no solape y control de clasificador congelado

La planilla del arbitraje SHALL validarse con un validador que admita los tres etiquetadores
`E3`, `E4` y `E5` para la tarea de arbitraje, sin cambiar el contrato de exactamente dos
etiquetadores de la tarea `doble_etiquetado` existente; el validador SHALL salir con exit
code `0`. El corpus arbitrado SHALL pasar `verificar_no_solape` contra el corpus de ajuste
como paso previo obligatorio. La clasificación SHALL ejecutarse con el clasificador
CONGELADO (`classifier_version` idéntica a la del in-sample, sin recalibrar) y su control
`git diff bf5e099 HEAD` SHALL registrarse.

#### Scenario: Planilla de arbitraje válida

- **WHEN** se valida la planilla del arbitraje con `E3`, `E4` y `E5`
- **THEN** el validador sale con exit code `0`
- **AND** no se cambia el contrato de dos etiquetadores de la tarea `doble_etiquetado`

#### Scenario: No solape y clasificador congelado

- **WHEN** se prepara la corrida del corpus arbitrado
- **THEN** `verificar_no_solape` no lanza `SolapeError`
- **AND** el control `git diff bf5e099 HEAD` sobre el clasificador solo admite diferencias ajenas a la clasificación y queda registrado

### Requirement: ARB-008 — Artefactos versionados con SHA-256

Los artefactos del arbitraje SHALL versionarse en `evaluation/data/campana/` con su SHA-256
en `evaluation/data/campana/README.md`: la tabla primaria del arbitraje, el JSON final del
corpus arbitrado, las predicciones y el reporte del clasificador congelado, el registro de
sujetos actualizado y el resultado del control de clasificador congelado con su commit. Los
artefactos de la v9 y el corpus de ajuste SHALL quedar sin cambios.

#### Scenario: Hash y procedencia registrados

- **WHEN** se versionan los artefactos del arbitraje
- **THEN** el README registra el SHA-256 de cada archivo y el commit del cache
- **AND** `git status` no muestra modificados el corpus de ajuste, sus resultados ni `evaluation/report.md`

#### Scenario: Protocolo versionado

- **WHEN** se lee `docs/campana-medicion/runbook-arbitraje-discordantes.md`
- **THEN** figuran el tercer etiquetador `E5`, el cegado, la regla de tres vías, el refuerzo de clases y el criterio de aceptación
- **AND** cada paso tiene su comando o su artefacto verificable
