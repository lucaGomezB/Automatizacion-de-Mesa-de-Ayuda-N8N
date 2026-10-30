## MODIFIED Requirements

### Requirement: Incertidumbre del kappa y de las metricas por clase

El memo canonico SHALL registrar la incertidumbre de cada coeficiente kappa de doble
etiquetado y los intervalos de confianza de las metricas por clase (precision,
sensibilidad y F1 una contra el resto), junto con el procedimiento de estimacion
empleado y su nivel de confianza. El kappa `0,87` de la campaña 2026-10 SHALL
conservarse con estado `vigente (sin IC)`: su entrada "no computable" SHALL cerrarse
con la nota "no estimable; superado por la entrada 3.N del kappa de la campaña"
(con el numero real de la entrada nueva) y MUST NOT reemplazarse por un intervalo del
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
- **THEN** el `0,87` figura con estado `vigente (sin IC)` y su entrada "no computable" cerrada con la nota que remite a la entrada nueva
- **AND** el kappa de la campaña de medicion figura en una entrada propia con su intervalo asintotico y bootstrap, metodo, semilla y nivel declarados, o con la declaracion de intervalo no estimable y su causa

#### Scenario: Sin intervalo atribuido al 0,87

- **WHEN** se busca en el memo un intervalo de confianza asociado al `0,87`
- **THEN** no aparece ninguno
- **AND** el intervalo del kappa de la campaña de medicion no se presenta como el del `0,87`

### Requirement: Regla del gate de intervención humana declarada y trazable

El memo SHALL declarar la regla exacta del gate de revisión humana implementada y
la tabla de contingencia `confianza × etapa × acierto` reconstruida desde
`evaluation/predicciones.json`. El memo SHALL explicar qué confianza asigna la
etapa determinística y por qué no dispara revisión. La proporción de intervención
humana de la campaña 2026-10 SHALL permanecer `retirado` (el `9,5 %`), porque no es
derivable de `evaluation/predicciones.json`, `evaluation/report.md` ni `data/`. La
`tasa_intervencion_humana` de la campaña de medición SHALL registrarse como entrada
nueva solo si es derivable del export `evaluation/data/campana/intervenciones.csv`
(versionado con SHA-256) a través de las salidas de c-167 en
`evaluation/data/campana/analisis/`, con estado `vigente`, o como "no contrastada:
registro incompleto" si el export no cubre la corrida. La métrica de backend
`tasa_intervencion_backend` MUST NOT registrarse como valor citable de la tesis.

#### Scenario: Contingencia publicada

- **WHEN** se lee la sección del gate en el memo
- **THEN** figura la tabla de contingencia de confianza contra acierto desagregada por etapa del pipeline
- **AND** se declara que los casos con confianza inferior a 0,70 corresponden a la etapa determinística

#### Scenario: Intervención no derivable se retira

- **WHEN** la proporción de intervención humana de la campaña 2026-10 no puede derivarse de `evaluation/predicciones.json`, `evaluation/report.md` ni `data/`
- **THEN** el memo registra el `9,5 %` como `retirado`
- **AND** el memo reformula el aporte operativo de esa campaña sin esa cifra

#### Scenario: Intervención de la campaña de medición registrada

- **WHEN** las salidas de c-167 derivan la `tasa_intervencion_humana` de `intervenciones.csv`
- **THEN** el memo registra la proporción de casos con `n`, estimación, ambos límites de Wilson, desglose por origen y veredicto frente a `0,15` (compatible, refutada o no concluyente), y la proporción del tiempo con su intervalo bootstrap o como "no estimable", con procedencia `archivo:línea`
- **AND** si el export no cubre la corrida, el memo registra "no contrastada: registro incompleto" sin valor numérico

#### Scenario: Tramo de alta confianza verificado

- **WHEN** el texto vigente cita un tramo de casos con confianza alta y su número de errores
- **THEN** el memo registra el valor recalculado desde `evaluation/predicciones.json`
- **AND** declara si ese tramo se deduce o no de la tabla de bandas publicada

## ADDED Requirements

### Requirement: Registro de los valores de la campaña de medicion con procedencia por valor

El memo canonico SHALL registrar cada valor de la campaña de medicion que la tesis
incorpora como entrada `3.N` consecutiva (la siguiente seccion libre de la Seccion 3
al aplicar), con: valor; procedencia `archivo:línea` en la salida de c-167 bajo
`evaluation/data/campana/analisis/`; comando reproducible de solo lectura; metodo
(intervalo asintotico de Fleiss, Cohen y Everitt 1969 y bootstrap percentil con
`B = 2000` y semilla `20261021` para el kappa y los agregados por caso; Wilson al
95 % para proporciones por operador y para la intervencion); SHA-256 de la tabla
primaria de la que deriva (`doble_etiquetado.csv`, `plan_campana.csv`,
`intervenciones.csv`, `predicciones_independiente.json`); fecha y configuracion de la
campaña; y estado en `{vigente, retirado, condicional}`. Los valores comprendidos son:
kappa de la campaña de medicion y sus estadisticos; exactitud estricta y laxa del
brazo manual por operador y agregada, con el contraste de McNemar; exactitud de v9
contra la referencia de la campaña de medicion (entrada propia, que no reemplaza el
`73,5 %` ni ningun valor canonico de v9); tasa de derivacion
erronea manual derivada y exactitud minima de equilibrio recalculada (estado
`condicional` al costo por derivacion erronea); `tasa_intervencion_humana` y su
proporcion del tiempo, con la estimacion, ambos limites y el veredicto (compatible,
refutada o no concluyente); efectos de orden de condicion (entre grupos
independientes) y de posicion, cada uno con el efecto minimo detectable que informe
c-167, sin valores fijados a priori; y metricas fuera de muestra por etapa. Cada estado negativo
("no medida: operadores no independientes", "no contrastada: registro incompleto",
"no estimable", "limitacion residual", "sin corpus independiente declarado") SHALL
registrarse como entrada con su causa y su condicion de reversibilidad, sin valor
numerico.

#### Scenario: Valores de la campaña registrados con procedencia

- **WHEN** se recorren las entradas de la campaña de medicion en el memo
- **THEN** cada valor declara procedencia `archivo:línea`, comando, metodo, SHA-256 de la tabla primaria, fecha, configuracion y estado
- **AND** la linea citada existe en la salida de c-167 referenciada y ninguno queda sin fuente

#### Scenario: Estados negativos registrados

- **WHEN** la campaña de medicion deja un item sin medir, sin contrastar o no estimable
- **THEN** el memo registra la entrada con el rotulo del estado negativo, su causa y su condicion de reversibilidad
- **AND** la tesis cita ese mismo rotulo en todas las secciones que tratan el item

#### Scenario: Numeracion consecutiva

- **WHEN** se listan los encabezados de la Seccion 3 del memo despues de aplicar el change
- **THEN** la seccion de la campaña de medicion ocupa el siguiente numero libre y la secuencia `3.N` sigue siendo consecutiva y sin duplicados
- **AND** la nota de cierre de la entrada "no computable" del `0,87` remite al numero real de la entrada del kappa nuevo

### Requirement: Valores canonicos vigentes intactos ante la campaña de medicion

La incorporacion de la campaña de medicion MUST NOT cambiar el valor ni el estado de
ningun valor canonico vigente de la campaña 2026-10, en particular `61,6 s`,
`17,76 s`, `W = 363`, `73,5 %`, `0,6508` y el kappa `0,87` (este ultimo con estado
`vigente (sin IC)`). La campaña de medicion SHALL registrarse como un conjunto de datos
adicional, rotulado con su fecha y su configuracion (Anexo B), en una seccion propia
del memo. La cabecera del memo SHALL registrar el agregado de la seccion nueva y la
release que la consolida.

#### Scenario: Valores vigentes sin cambios

- **WHEN** se comparan las secciones previas del memo antes y despues de aplicar el change
- **THEN** ningun valor existente cambio de valor ni de estado, salvo el cierre con nota de la entrada "no computable" del kappa, cuyo valor `0,87` y rotulo se conservan
- **AND** la cabecera del memo registra la seccion nueva de la campaña de medicion

#### Scenario: Campaña de medicion rotulada como conjunto adicional

- **WHEN** se lee la seccion de la campaña de medicion del memo
- **THEN** declara su fecha, su commit de configuracion y su `n`
- **AND** ninguna de sus entradas se presenta como reemplazo de un valor de la campaña 2026-10
