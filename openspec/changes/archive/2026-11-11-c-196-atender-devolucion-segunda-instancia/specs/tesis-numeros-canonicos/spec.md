## MODIFIED Requirements

### Requirement: Incertidumbre del kappa y de las metricas por clase

El memo canonico SHALL registrar la incertidumbre de cada coeficiente kappa de doble
etiquetado y los intervalos de confianza de las metricas por clase (precision,
sensibilidad y F1 una contra el resto), junto con el procedimiento de estimacion
empleado y su nivel de confianza. El kappa `0,87` del doble etiquetado original SHALL
registrarse con estado `retirado como evidencia (sin respaldo)`: sus planillas no se
conservaron y el valor ya figuraba en la version de julio de 2026, antes del corpus real
(devolucion del tribunal del 11-11-2026, N-01); su entrada "no computable" conserva la nota
que remite a la entrada del kappa de la campaña y MUST NOT reemplazarse por un intervalo del
`0,87`. El kappa de la campaña de medicion SHALL registrarse en una entrada nueva y
distinta, con su `n`, sus etiquetadores `E1` y `E2`, `p_o`, `p_e`, PABAK, su intervalo
asintotico (varianza de Fleiss, Cohen y Everitt, 1969), su intervalo bootstrap
percentil (`B = 2000`, semilla `20261021`), su rotulo de Landis y Koch derivado del
valor puntual y la indicacion de si el intervalo abarca dos categorias, o con la
declaracion de intervalo no estimable si c-167 asi lo informa. El memo SHALL declarar
como no estimable toda clase con soporte unitario y SHALL excluirla de los
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

- **WHEN** se lee el registro de incertidumbre de los coeficientes kappa
- **THEN** el `0,87` figura con estado `retirado como evidencia (sin respaldo)` y su entrada "no computable" cerrada con la nota que remite a la entrada nueva
- **AND** el kappa de la campaña de medicion figura en una entrada propia con su intervalo asintotico y bootstrap, metodo, semilla y nivel declarados, o con la declaracion de intervalo no estimable y su causa

#### Scenario: Sin intervalo atribuido al 0,87

- **WHEN** se busca en el memo un intervalo de confianza asociado al `0,87`
- **THEN** no aparece ninguno
- **AND** el intervalo del kappa de la campaña de medicion no se presenta como el del `0,87`

### Requirement: Valores canonicos vigentes intactos ante la campaña de medicion

La incorporacion de la campaña de medicion MUST NOT cambiar el valor ni el estado de
ningun valor canonico vigente de la campaña 2026-10, en particular `61,6 s`,
`17,76 s`, `W = 363`, `73,5 %` y `0,6508`. El kappa `0,87` deja de ser valor canonico
vigente: su estado pasa a `retirado como evidencia (sin respaldo)` (devolucion del tribunal
del 11-11-2026, N-01). La campaña de medicion SHALL registrarse como un conjunto de datos
adicional, rotulado con su fecha y su configuracion (Anexo B), en una seccion propia
del memo. La cabecera del memo SHALL registrar el agregado de la seccion nueva y la
release que la consolida.

#### Scenario: Valores vigentes sin cambios

- **WHEN** se comparan las secciones previas del memo antes y despues de aplicar el change
- **THEN** ningun valor existente cambio de valor ni de estado, salvo el estado del kappa `0,87`, que pasa a `retirado como evidencia (sin respaldo)` sin cambiar su valor
- **AND** la cabecera del memo registra la seccion nueva de la campaña de medicion

#### Scenario: Campaña de medicion rotulada como conjunto adicional

- **WHEN** se lee la seccion de la campaña de medicion del memo
- **THEN** declara su fecha, su commit de configuracion y su `n`
- **AND** ninguna de sus entradas se presenta como reemplazo de un valor de la campaña 2026-10

### Requirement: Registro de la proporcion de intervenciones con cambio de derivacion

El memo SHALL registrar como entrada nueva de la campaña complementaria la proporcion de
intervenciones que cambiaron la derivacion (25 de 200 = 0,125) con su intervalo de Wilson
al 95 % ([0,086; 0,178], recomputado con la misma funcion de Wilson del analisis), su
procedencia (`evaluation/data/campana/intervenciones.csv`, `cambio_sector = true`) y su
veredicto frente a la cota de 0,15 ("no concluyente"). SHALL registrar ademas la proporcion
sobre los 147 casos revisados (25 de 147 = 0,170; Wilson [0,118; 0,239]; binomial contra 0,15
p = 0,28 unilateral y 0,49 bilateral) con el veredicto vigente "no concluyente, con estimación
puntual por encima de la cota" y la nota de que el denominador de 147 y su lectura se fijaron
despues de conocer los datos; el estado "refutada" de c-190 a c-195 SHALL figurar solo como
superado (devolucion del tribunal del 11-11-2026, N-09). SHALL registrar el desglose de
las 147 intervenciones por canal (66 de 66 correo, 81 de 81 telefonia, 0 de 53
formulario web) con su fuente (sidecars de la corrida). La entrada MUST NOT reemplazar la
tasa bruta (147/200) ni ningun valor canonico vigente.

#### Scenario: Entrada nueva registrada

- **WHEN** se lee la seccion de la campaña complementaria del memo
- **THEN** figura 25/200 = 0,125 con IC de Wilson [0,086; 0,178], su procedencia y el veredicto "no concluyente"
- **AND** figura el desglose por canal de las 147 intervenciones con su fuente
- **AND** figura 25/147 = 0,170 con Wilson [0,118; 0,239], p = 0,28 unilateral y el veredicto "no concluyente, con estimación puntual por encima de la cota"

#### Scenario: Tasa bruta conservada

- **WHEN** se compara la entrada de la tasa bruta de intervencion antes y despues del change
- **THEN** 147/200 y su IC [0,6698; 0,7913] se conservan
- **AND** la entrada nueva no figura como reemplazo

## ADDED Requirements

### Requirement: Registro de los valores de la devolucion de segunda instancia

El memo canonico SHALL registrar, con procedencia (script de recalculo y archivo versionado) y
estado, los valores que la tesis incorpora por la devolucion del tribunal del 11-11-2026: los
tiempos manuales de la campaña complementaria por operador y agregados (O1: 110 casos, 20,1 s
(9,2), mediana 18,0 s, automatizado 13,3 s, 33,8 %, p = 9,8 × 10⁻⁷, r = 0,54; O2: 110, 76,6 s
(21,4), 73,0 s, 15,5 s, 79,7 %, 9,0 × 10⁻²⁰, 1,00; agregado: 200, 47,6 s (28,7), 49,0 s, 14,6 s,
69,3 %, 3,0 × 10⁻²⁸, 0,90), el registro de 0 s (R025), los 20 casos de doble cobertura y las
correlaciones entre campañas; la exactitud contra el consenso independiente (110/138 = 0,797
[0,722; 0,856]; laxa 117/138 = 0,848 [0,779; 0,898]), la de la referencia original sobre los
mismos 138 (109/138 = 0,790 [0,714; 0,850]; laxa 125/138 = 0,906 [0,846; 0,944]), los 62 casos
sin consenso (38/62 = 0,613) y el macro-F1 contra el consenso (0,757); y la cobertura de
sentencias del backend con su commit, fecha y comando, si se midio. Ninguno MUST reemplazar un
valor canonico vigente de la campaña 2026-10.

#### Scenario: Valores de la devolucion registrados

- **WHEN** se lee el memo despues del apply de c-196
- **THEN** figuran los tiempos por operador, la exactitud contra el consenso y, si se midio, la cobertura del backend, cada uno con procedencia y estado
- **AND** `61,6 s`, `17,76 s`, `W = 363`, `73,5 %` y `0,6508` no cambian
