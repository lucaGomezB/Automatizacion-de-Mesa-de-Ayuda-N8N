## MODIFIED Requirements

### Requirement: Incertidumbre del kappa y de las metricas por clase

El memo canonico SHALL registrar el intervalo de confianza del coeficiente kappa
de doble etiquetado y los intervalos de confianza de las metricas por clase
(precision, sensibilidad y F1 una contra el resto), junto con el procedimiento de
estimacion empleado y su nivel de confianza. Una vez recuperada la tabla primaria de
doble etiquetado, el memo SHALL registrar el IC del kappa computado por bootstrap con
semilla fija, con su metodo, semilla y nivel declarados, y SHALL retirar la
declaracion de no computabilidad por ausencia de la tabla primaria. El memo SHALL
declarar como no estimable toda clase con soporte unitario y SHALL excluirla de los
estimadores agregados de umbral. Cuando una incertidumbre no sea computable a partir
de las fuentes primarias permitidas, el memo SHALL declararlo de forma explicita con
la condicion de reversibilidad, en lugar de presentar el valor puntual como si
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
- **THEN** figura su IC con el procedimiento de estimacion (bootstrap, semilla fija) y el nivel declarados
- **AND** no subsiste la declaracion de no computabilidad por ausencia de la tabla primaria cuando esta fue aportada por la campana

## ADDED Requirements

### Requirement: Registro de los valores de la campana con procedencia por valor

El memo canonico SHALL registrar, con procedencia y estado, los valores producidos
por la campana de campo que la tesis incorpora: la exactitud del brazo manual y su IC,
la tasa de intervencion humana y su IC, el IC del coeficiente kappa y el efecto de
orden. Cada valor SHALL citar la fuente (artefacto de la campana o el analisis de
c-167) y SHALL figurar con estado `vigente`, sin presentar valores huerfanos.

#### Scenario: Valores de la campana registrados con procedencia

- **WHEN** se recorren las entradas de la campana en el memo
- **THEN** cada valor (exactitud manual, tasa de intervencion, IC del kappa y efecto de orden) declara su procedencia y su estado
- **AND** ninguno queda sin fuente

#### Scenario: IC del kappa actualizado en el memo

- **WHEN** se lee la entrada del IC del kappa en el memo
- **THEN** figura el IC computado con su metodo y semilla
- **AND** se retira la declaracion "no computable" que regia por ausencia de la tabla primaria