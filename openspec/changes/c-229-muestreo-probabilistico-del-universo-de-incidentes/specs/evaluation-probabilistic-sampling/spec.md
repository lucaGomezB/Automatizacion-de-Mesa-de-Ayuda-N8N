## Purpose

Definir el muestreo probabilistico estratificado del universo de incidentes de la organizacion
(marco, estratos, cuotas prefijadas por canal y sector, denominadores y reglas de decision) y la
estimacion ponderada referida al universo (Horvitz-Thompson / post-estratificacion) con su efecto
de diseno, para que las metricas de clasificacion puedan estimarse sobre la poblacion y no solo
sobre la muestra por conveniencia, sin cambiar ningun valor canonico.

## ADDED Requirements

### Requirement: PS-001 — Universo y marco muestral definidos

El diseno SHALL definir el universo como la poblacion de incidentes informaticos registrados por la
mesa de ayuda de la organizacion en un periodo declarado, con su tamano aproximado `N` y la tasa de
incidencia de la que se deriva. SHALL definir el marco muestral como el registro operativo de
incidentes del periodo, con el procedimiento de inclusion verificable (de donde se extrae cada
unidad y como se enumera). El universo SHALL declararse con sus estratos: sector responsable, canal
de origen y complejidad del incidente, cada uno con su definicion operacional. Los estratos y el
marco SHALL registrarse ANTES de reunir la muestra, en el protocolo
`docs/campana-medicion/protocolo-muestreo-probabilistico.md`. El diseno MUST NOT reutilizar la
composicion del corpus de 200 casos como si fuera la del universo.

#### Scenario: Universo, marco y estratos declarados

- **WHEN** se lee el protocolo de muestreo probabilistico
- **THEN** figuran el universo con su periodo y su `N`, el marco muestral con su procedimiento de inclusion y los estratos de sector, canal y complejidad con su definicion operacional
- **AND** los estratos y el marco estan fijados antes de reunir la muestra

#### Scenario: Composicion del corpus no tomada como la del universo

- **WHEN** se define la distribucion de los estratos del universo
- **THEN** no se usa la composicion del corpus de 200 casos como sustituto
- **AND** si la distribucion del universo no esta disponible, se declara como no disponible y se fija el metodo para obtenerla

### Requirement: PS-002 — Diseno estratificado con cuotas prefijadas

La seleccion SHALL ser probabilistica y estratificada, con cuotas prefijadas por canal de origen y
por sector, y SHALL asignar probabilidades de inclusion conocidas y mayores que cero a cada unidad
del marco. Las cuotas, el tamano objetivo, los denominadores y las reglas de decision sobre la
estimacion SHALL fijarse ANTES de reunir la muestra y SHALL registrarse en el protocolo. Las reglas
de decision SHALL ser de tres vias (objetivo alcanzado, no alcanzado, no concluyente) cuando la
estimacion se contraste contra un umbral, y MUST NOT reajustarse despues de observar los datos. El
diseno SHALL declarar de forma explicita el tratamiento de la clase minoritaria y de los estratos de
soporte pequeno.

#### Scenario: Cuotas y reglas fijadas antes de la recoleccion

- **WHEN** se inicia la recoleccion de la muestra probabilistica
- **THEN** la asignacion por estrato de canal y sector, el tamano objetivo, los denominadores y la regla de decision estan decididos y registrados con su justificacion
- **AND** la asignacion no se modifica despues de ver los resultados

#### Scenario: Probabilidades de inclusion conocidas

- **WHEN** se calculan los pesos de la estimacion
- **THEN** cada unidad del marco tiene una probabilidad de inclusion conocida y mayor que cero
- **AND** los pesos se derivan de ella y no de la composicion observada de la muestra

### Requirement: PS-003 — Etiquetado independiente y consentimiento

La muestra probabilistica SHALL etiquetarse con al menos dos etiquetadores independientes, distintos
entre si, de los operadores del brazo manual y de los autores, sin acceso a las predicciones del
clasificador; los casos discordantes SHALL resolverse por consenso o por un tercer etiquetador. La
recoleccion SHALL contar con el consentimiento informado correspondiente y cumplir el tratamiento de
datos de la tesis (pseudonimizacion, minimizacion y disociacion). El registro de sujetos SHALL usar
alias y codigos, sin nombres, correos ni legajos, y la correspondencia alias-identidad SHALL
custodiarse FUERA del repositorio.

#### Scenario: Etiquetado independiente

- **WHEN** se etiqueta la muestra
- **THEN** cada caso tiene al menos dos etiquetas de etiquetadores independientes
- **AND** los etiquetadores no son operadores del brazo manual ni autores y no accedieron a las predicciones

#### Scenario: Consentimiento y pseudonimizacion

- **WHEN** se recolecta la muestra del universo
- **THEN** se registra el consentimiento informado y la pseudonimizacion
- **AND** ninguna fila del registro de sujetos contiene nombre, correo ni legajo

### Requirement: PS-004 — Estimacion ponderada referida al universo

La estimacion de las metricas de clasificacion SHALL ponderarse por el inverso de la probabilidad de
inclusion (estimador de Horvitz-Thompson) y, cuando se calibre a los totales conocidos de los
estratos, por post-estratificacion a la distribucion del universo. Las metricas ponderadas SHALL
referirse al universo y SHALL informarse con su intervalo de confianza estimado sobre el universo
COMPLETO, sin excluir casos por discordancia u otra causa. La lectura sin ponderar SHALL informarse
junto a la ponderada, rotulada, y MUST NOT presentarse como la estimacion poblacional. La ponderacion
SHALL declarar la procedencia de sus pesos y MUST NOT usar la composicion del corpus de 200 casos como
si fuera la del universo.

#### Scenario: Pesos y referencia al universo

- **WHEN** se calcula la exactitud estricta ponderada
- **THEN** los pesos provienen de la probabilidad de inclusion o de la post-estratificacion a los totales del universo
- **AND** la metrica se rotula como referida al universo y no como la del corpus de 200

#### Scenario: Intervalo de confianza sobre el universo completo

- **WHEN** se estima el intervalo de confianza de la metrica ponderada
- **THEN** se calcula sobre el universo completo, sin excluir casos
- **AND** se declara el metodo y el nivel de confianza

### Requirement: PS-005 — Efecto de diseno reportado

La estimacion SHALL reportar el efecto de diseno del estimador ponderado (efecto de Kish, cociente
entre la varianza del estimador bajo el diseno y la de un muestreo aleatorio simple del mismo
tamano), junto con la exactitud estricta ponderada. Cuando el efecto de diseno no sea computable
porque la muestra probabilistica aun no existe, la estimacion SHALL declararlo de forma explicita con
su motivo y su estado `condicional`, sin fijar un valor estimado. El efecto de diseno de la
post-estratificacion aplicada a una muestra por conveniencia MUST NOT presentarse como el efecto de
diseno del diseno probabilistico.

#### Scenario: Efecto de diseno con su procedencia

- **WHEN** se lee el resultado de la estimacion ponderada
- **THEN** figura el efecto de diseno con el metodo de calculo y la procedencia de sus pesos
- **AND** se distingue el efecto de diseno del diseno probabilistico del de una post-estratificacion sobre una muestra por conveniencia

#### Scenario: Efecto de diseno no computable declarado

- **WHEN** la muestra probabilistica no existe todavia
- **THEN** el efecto de diseno se declara no computable con su motivo y su estado `condicional`
- **AND** no se consigna ningun valor estimado como si fuera el del diseno

### Requirement: PS-006 — Herramienta de estimacion offline, determinista y de solo lectura

Las funciones de ponderacion y de efecto de diseno SHALL producirse por un script de solo lectura bajo
`evaluation/data/campana/analisis/`, con pruebas de sus funciones puras escritas ANTES de la
implementacion. El script MUST NOT invocar a Gemini, a la red ni a un servicio externo, MUST NOT
modificar el corpus, las predicciones ni ningun valor canonico, y SHALL producir salidas identicas
byte a byte en dos corridas. Antes de escribir, SHALL reproducir la lectura ponderada vigente `0,7489`
(lectura complementaria del corpus arbitrado, ponderada por la composicion por sector del corpus de
200, bootstrap `[0,6822; 0,8099]`) sobre los artefactos versionados; si no la reproduce, SHALL
terminar con un codigo distinto de cero sin escribir salidas. La reproduccion de `0,7489` es un
anclaje de la funcion de ponderacion y MUST NOT presentarse como el efecto de diseno del diseno
probabilistico.

#### Scenario: Anclaje reproducido antes de escribir

- **WHEN** el script corre sobre los artefactos versionados
- **THEN** reproduce la lectura ponderada vigente `0,7489` y su intervalo bootstrap antes de escribir salidas
- **AND** si no la reproduce, termina con codigo distinto de cero sin escribir

#### Scenario: Solo lectura, determinismo y sin red

- **WHEN** el script se ejecuta dos veces seguidas
- **THEN** ambas salidas son identicas byte a byte
- **AND** no se realiza ninguna llamada de red o a Gemini y `git status` no muestra archivos modificados por la ejecucion

#### Scenario: Funciones puras probadas antes de implementar

- **WHEN** se revisa el desarrollo del script
- **THEN** las pruebas de las funciones de ponderacion y de efecto de diseno existieron antes que el modulo
- **AND** los casos cubren al menos un escenario de pesos desiguales y uno de cuotas proporcionales
