## ADDED Requirements

### Requirement: Balance neto entre el ahorro de registro y el costo de las derivaciones erroneas

El capitulo de discusion (`08-discusion.tex`) SHALL incluir una subseccion con rotulo `subsec:balance-neto` que compute el balance neto trimestral entre el ahorro de tiempo de registro y el costo de las derivaciones erroneas adicionales del clasificador respecto del flujo manual. La subseccion SHALL enunciar de forma explicita las formulas del balance neto, `B = (N / 3.600) x [Delta t - (e_aut - e_man) x c]`, y de la exactitud minima de equilibrio, `a* = 1 - e_man - Delta t / c`, junto con la procedencia de cada insumo: universo trimestral `N ~ 2.646`, ahorro medio por incidente `Delta t = 43,82 s` (43,8 s en el texto), tasa de error estricta del clasificador `e_aut = 26,5 %` (53/200), tasa de derivacion erronea manual `e_man` (15 % preliminar) y costo por derivacion erronea `c` (10 a 15 minutos, estimacion propia). La subseccion SHALL incluir una tabla con rotulo `tab:balance-neto` que, para tasas manuales de 10 %, 15 %, 20 % y 26,5 % y costos de 5, 10 y 15 minutos, reporte la exactitud minima de equilibrio y el balance neto con la exactitud estricta, y SHALL contrastar la exactitud minima de equilibrio con la exactitud estricta observada y su intervalo de Wilson. Todo valor de la subseccion y de la tabla MUST coincidir con el registrado en `docs/Tesis/Correcciones/numeros-canonicos.md`.

#### Scenario: Formulas e insumos explicitos

- **WHEN** se lee la subseccion `subsec:balance-neto`
- **THEN** figuran las formulas del balance neto y de la exactitud minima de equilibrio con la definicion de `N`, `Delta t`, `e_aut`, `e_man` y `c`
- **AND** cada insumo remite a su origen en el documento (planteamiento del problema, objetivos especificos, interpretacion de los resultados o resultados)

#### Scenario: Calculo con los supuestos del propio documento

- **WHEN** se aplican las formulas con `e_man = 15 %` y `c` de 10 y 15 minutos
- **THEN** el texto informa del orden de 304 derivaciones erroneas adicionales por trimestre, un costo de 50,7 y 76,1 horas-persona y un balance neto de -18,5 y -43,9 horas-persona
- **AND** la exactitud minima de equilibrio informada para esos supuestos es 77,7 % y 80,1 %

#### Scenario: Tabla de escenarios con el punto de equilibrio

- **WHEN** se lee la tabla `tab:balance-neto`
- **THEN** contiene una fila por tasa manual (10 %, 15 %, 20 % y 26,5 %) y, para costos de 5, 10 y 15 minutos, la exactitud minima de equilibrio y el balance neto con la exactitud estricta
- **AND** cada celda coincide con el valor del memo canonico bajo la convencion de redondeo declarada en la nota de la tabla

#### Scenario: Incertidumbre muestral considerada

- **WHEN** se contrasta la exactitud minima de equilibrio con la exactitud estricta observada
- **THEN** el texto compara la exactitud minima de equilibrio con el intervalo de Wilson [67,0 %; 79,1 %]
- **AND** declara que, con una tasa manual del 15 % y 10 minutos por reasignacion, el signo del balance no queda determinado por la muestra

#### Scenario: Exactitud laxa sin cifras inventadas

- **WHEN** la exactitud laxa esta registrada en el memo canonico al momento de aplicar el cambio
- **THEN** la subseccion la compara con la exactitud minima de equilibrio e informa los escenarios en que el balance resulta positivo bajo esa lectura
- **AND** si no esta registrada, la subseccion no presenta ningun valor de exactitud laxa y declara que el 26,5 % es una cota superior de la tasa operativa de derivacion erronea atribuible al clasificador

#### Scenario: Remisiones resueltas

- **WHEN** se compila el documento con XeLaTeX tras incorporar la subseccion y la tabla
- **THEN** las remisiones a `subsec:balance-neto` y `tab:balance-neto` resuelven sin referencias indefinidas
- **AND** ambos rotulos son unicos en el documento

### Requirement: Exactitud del brazo manual declarada no medida y balance neto indeterminado

La tesis SHALL declarar que la exactitud del brazo manual sobre el corpus no se midio, con sus dos razones: el corpus no registra por caso la derivacion efectuada por el operador del brazo manual, y esos operadores son los mismos analistas que fijaron la referencia, por lo que una medicion sobre este corpus estaria sesgada hacia el acuerdo. La tesis SHALL declarar que la tasa de derivacion erronea manual cercana al 15 % es una estimacion preliminar de la misma naturaleza que los 2 minutos 45 segundos luego corregidos a 61,6 s, y que, en consecuencia, el balance neto es indeterminado con el diseno actual. El documento MUST NOT presentar ninguna exactitud o tasa de derivacion erronea del flujo manual como medida, y MUST NOT enunciar el signo del balance neto como resultado.

#### Scenario: Declaracion en la discusion

- **WHEN** se leen la subseccion `subsec:balance-neto` y la sexta limitacion de `subsec:limitaciones-estudio`
- **THEN** se declara que la exactitud del brazo manual no se midio y se enuncian las dos razones
- **AND** se concluye que el balance neto es indeterminado con el diseno actual, indicando la condicion bajo la cual seria positivo

#### Scenario: Declaracion en el planteamiento del problema

- **WHEN** se lee el planteamiento del problema en `01-introduccion.tex`
- **THEN** la tasa de derivacion erronea del 15 % se califica como estimacion preliminar no re-medida, de la misma naturaleza que los 2 minutos 45 segundos
- **AND** el parrafo remite a `subsec:balance-neto`

#### Scenario: Sin tasa manual presentada como medida

- **WHEN** se recorren las secciones de la tesis en busca de una exactitud o tasa de derivacion erronea del flujo manual
- **THEN** el unico valor atribuido al flujo manual es el 15 % preliminar, rotulado como tal, y las demas tasas de la tabla de escenarios se rotulan como supuestos de sensibilidad
- **AND** ningun pasaje presenta una tasa manual como resultado de la campana experimental ni afirma que el balance neto sea positivo o negativo

### Requirement: Viabilidad operativa presentada como condicional

El resumen (en espanol y en ingles), la justificacion de la introduccion, la discusion y las conclusiones SHALL presentar la viabilidad tecnica y la economica como sostenidas por la evidencia y la viabilidad operativa como condicional a que la exactitud efectiva supere la exactitud minima de equilibrio, sea por mejora del clasificador o porque la revision humana del sector responsable reduzca la tasa o el costo efectivos de las derivaciones erroneas. El documento MUST NOT afirmar que los hallazgos confirman la viabilidad "tecnica, economica y operativa" (ni la "technical, economic, and operational feasibility"). El ahorro de 32,2 horas-persona por trimestre SHALL presentarse como ahorro bruto de registro, sin cambiar su valor. El parrafo de conclusion del resumen en espanol y del abstract MUST NOT aumentar su conteo de palabras respecto de la version previa.

#### Scenario: Resumen y abstract con viabilidad operativa condicional

- **WHEN** se leen los parrafos de conclusion del resumen y del abstract en `00-resumen.tex`
- **THEN** la viabilidad tecnica y economica se presentan como confirmadas y la operativa como condicional, con el balance neto frente a las derivaciones erroneas declarado indeterminado
- **AND** el parrafo en espanol tiene a lo sumo 34 palabras y el parrafo en ingles a lo sumo 31

#### Scenario: Conclusiones con los tres planos de viabilidad

- **WHEN** se lee el parrafo inicial de `09-conclusiones.tex`
- **THEN** el sistema se declara tecnicamente viable y economicamente accesible, y su viabilidad operativa se declara condicionada al balance neto con remision a `subsec:balance-neto`
- **AND** no queda una afirmacion de viabilidad incondicional del sistema en su conjunto

#### Scenario: Justificacion sin mejora neta cuantificada

- **WHEN** se lee la dimension organizacional de la justificacion en `01-introduccion.tex`
- **THEN** la evidencia del trabajo se presenta como cuantificacion del ahorro bruto de registro y del punto de equilibrio frente al costo de las derivaciones erroneas
- **AND** no se afirma como cuantificada una mejora neta ni una reduccion del tiempo de respuesta percibido por los usuarios

#### Scenario: Ahorro de 32,2 horas-persona calificado como bruto

- **WHEN** se lee cualquier mencion de las 32,2 horas-persona por trimestre en la introduccion, la discusion o las conclusiones
- **THEN** la mencion la califica como ahorro bruto o remite al balance neto de `subsec:balance-neto`
- **AND** el valor 32,2 y su calculo (`43,8 s x 2.646 / 3.600`) se conservan sin cambios

#### Scenario: Composicion del costo economico coherente con la discusion

- **WHEN** se lee en las conclusiones la descripcion del costo monetario de operacion del sistema
- **THEN** la descripcion es coherente con las cifras de la discusion (infraestructura de 24 a 32 USD por mes frente a inferencia del orden de 1 USD por trimestre)
- **AND** no se afirma que el costo de operacion este dominado por el consumo de la API de inferencia

### Requirement: Retiro de la afirmacion de preservacion del juicio humano

La discusion MUST NOT contener la afirmacion "El sistema absorbe la carga rutinaria sin sustituir el juicio humano en los casos que verdaderamente lo demandan" ni la afirmacion de que el equilibrio entre automatizacion y supervision "preserva la calidad del servicio", porque el gate de revision no derivo ningun caso del corpus y su aporte se declara no medido. El documento MUST NOT atribuir al sistema una preservacion del juicio humano que no fue medida. El parrafo de `subsec:interpretacion-resultados` SHALL conservar la proyeccion de 32,2 horas-persona con su nota de calculo.

#### Scenario: Frases retiradas

- **WHEN** se buscan en las secciones de la tesis las cadenas "absorbe la carga rutinaria" y "preserva la calidad del servicio"
- **THEN** no aparece ninguna ocurrencia
- **AND** el parrafo de `subsec:interpretacion-resultados` conserva la proyeccion de 32,2 horas-persona y su nota al pie

#### Scenario: Sin afirmaciones equivalentes

- **WHEN** se leen la discusion y las conclusiones
- **THEN** ningun pasaje afirma que el sistema preserva el juicio humano en los casos que lo demandan
- **AND** las menciones al gate de revision son coherentes con la declaracion de que su aporte no fue medido

### Requirement: Registro canonico del balance neto y sus supuestos

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar, en una seccion propia, los insumos, las formulas y los valores de la tabla del balance neto, cada uno con su procedencia (archivo y linea de origen, o recalculo con formula explicita) y su estado. Los valores que dependen de la tasa manual, del costo por derivacion erronea o de la rejilla de sensibilidad SHALL registrarse con estado `condicional` y con su condicion de reversibilidad. La seccion SHALL incluir un comando de recalculo reproducible y declarar la convencion de redondeo. El registro MUST NOT modificar ningun valor canonico existente.

#### Scenario: Insumos con procedencia y estado

- **WHEN** se lee la seccion del balance neto en el memo canonico
- **THEN** cada insumo declara valor, procedencia y estado: `vigente` para el universo, el ahorro medio por incidente y la tasa de error estricta; `condicional` para la tasa manual, el costo por derivacion erronea y la rejilla de sensibilidad
- **AND** cada linea de origen citada existe en el archivo referenciado

#### Scenario: Valores reproducibles

- **WHEN** se ejecuta el comando de recalculo de la seccion
- **THEN** reproduce la exactitud minima de equilibrio y el balance neto de cada celda de la tabla, y los valores del escenario central
- **AND** la convencion de redondeo y la diferencia respecto del calculo con 43,8 s quedan declaradas

#### Scenario: Valores canonicos existentes intactos

- **WHEN** se comparan las secciones previas del memo antes y despues del cambio
- **THEN** ningun valor existente cambio de valor ni de estado
- **AND** la cabecera del memo registra el agregado de la seccion nueva

### Requirement: Linea futura de medicion de la exactitud manual y del costo de reasignacion

El capitulo de recomendaciones SHALL incluir, en `subsec:estudios-replicacion`, la recomendacion de que toda replicacion registre por caso la derivacion efectuada en el brazo manual, con etiquetadores distintos de los operadores, y cronometre cada reasignacion, de modo de medir la exactitud manual y el costo de la derivacion erronea y cerrar el balance neto. La subseccion `subsec:balance-neto` SHALL remitir a esa recomendacion, y el capitulo MUST NOT duplicarla en otra subseccion.

#### Scenario: Recomendacion presente y conectada

- **WHEN** se lee `subsec:estudios-replicacion`
- **THEN** recomienda registrar por caso la derivacion del brazo manual con etiquetadores distintos de los operadores y cronometrar las reasignaciones
- **AND** remite a `subsec:balance-neto`, que a su vez remite a esta subseccion

#### Scenario: Sin duplicacion en recomendaciones

- **WHEN** se recorre el capitulo de recomendaciones
- **THEN** la medicion de la exactitud del flujo manual se recomienda una sola vez
- **AND** no existe una subseccion adicional que repita esa recomendacion
