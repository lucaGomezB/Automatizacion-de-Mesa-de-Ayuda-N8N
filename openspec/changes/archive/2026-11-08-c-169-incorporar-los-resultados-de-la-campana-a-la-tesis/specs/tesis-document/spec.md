## RENAMED Requirements

- FROM: `### Requirement: Intervención humana por gate declarada no medida`
- TO: `### Requirement: Intervención humana reportada según el registro de la campaña de medición`

- FROM: `### Requirement: Exactitud del brazo manual declarada no medida y balance neto indeterminado`
- TO: `### Requirement: Exactitud del brazo manual y balance neto según la campaña de medición`

## MODIFIED Requirements

### Requirement: Intervención humana reportada según el registro de la campaña de medición

La tesis SHALL NOT reportar la proporción de intervención humana del `9,5 %` como
resultado vigente (c-107). Para la campaña 2026-10 la intervención por gate SHALL
seguir declarándose no medida, porque no existe registro por caso en
`evaluation/predicciones.json`, `evaluation/report.md` ni `data/`, y porque el gate
implementado (`requiere_revision_humana = (confianza < 0,70)`) no disparó revisión
en ningún caso del corpus. Para la campaña de medición, la tesis SHALL reportar la
`tasa_intervencion_humana` calculada por c-167 a partir del export
`evaluation/data/campana/intervenciones.csv` (vocabulario de origen
`gate|muestreo|rederivacion|completado_manual`): proporción de casos con su `n`, su
intervalo de Wilson al 95 % y su desglose por origen y por cambio de sector, y la
proporción del tiempo con su intervalo bootstrap del cociente o la declaración
"no estimable" cuando la cobertura de las consignas de inicio y fin sea inferior al
80 %. Si el export no cubre la corrida de la campaña, la tesis SHALL declarar la
intervención "no contrastada: registro incompleto" y MUST NOT cuantificarla. La
métrica de backend `tasa_intervencion_backend` (c-165) MUST NOT presentarse como la
métrica de la tesis. El resumen, los resultados, la discusión, las conclusiones y
las recomendaciones MUST NOT conservar la cifra retirada. La afirmación de que el
flujo automatizado corrió "sin intervención humana" SHALL reconciliarse con la
definición de las dos dimensiones rotuladas de la variable y quedar acotada a la
captura de la campaña 2026-10.

#### Scenario: Cifra retirada ausente

- **WHEN** se busca "9,5 %" o "19 casos" como intervención humana en el PDF compilado
- **THEN** no aparece la cifra del 9,5 % presentada como resultado de intervención
- **AND** toda tasa de intervención reportada proviene de `evaluation/data/campana/intervenciones.csv` a través de las salidas de c-167 y de su entrada en el memo canónico

#### Scenario: Aporte operativo reformulado

- **WHEN** se lee la subsección de intervención humana de resultados y la discusión
- **THEN** el aporte operativo del gate en la campaña 2026-10 se declara no medido, explicando que el gate implementado no escaló casos en el corpus
- **AND** el aporte de la campaña de medición se formula solo con la tasa medida y su intervalo, o con la declaración "no contrastada: registro incompleto", sin afirmar una reducción porcentual no sustentada

#### Scenario: Intervención de la campaña de medición reportada

- **WHEN** el export de intervenciones cubre la corrida de la campaña y se lee la subsección de intervención humana de resultados
- **THEN** se reporta la proporción de casos con su `n`, su intervalo de Wilson y su desglose por origen y por cambio de sector
- **AND** la proporción del tiempo se reporta con su intervalo bootstrap o se declara "no estimable" por cobertura de inicio y fin inferior al 80 %

#### Scenario: Registro incompleto declarado

- **WHEN** el export de intervenciones no cubre la corrida de la campaña de medición
- **THEN** la subsección de intervención humana declara "no contrastada: registro incompleto"
- **AND** no se cuantifica ninguna proporción de intervención como resultado

#### Scenario: Campaña 2026-10 sin intervención medida

- **WHEN** se lee la subsección de intervención humana respecto de la campaña 2026-10
- **THEN** el texto conserva que el gate no derivó ningún caso y que la intervención de esa campaña no se midió
- **AND** no atribuye a la campaña 2026-10 la tasa medida en la campaña de medición

#### Scenario: Coherencia con "sin intervención humana"

- **WHEN** se compara la afirmación del protocolo de pruebas con la subsección de intervención humana
- **THEN** ambas describen la misma definición rotulada de la variable y distinguen la campaña 2026-10 de la campaña de medición
- **AND** no se sostiene simultáneamente que hubo 9,5 % de intervención y que el flujo corrió sin intervención humana

### Requirement: Exactitud del brazo manual y balance neto según la campaña de medición

La tesis SHALL declarar que la exactitud del brazo manual de la campaña 2026-10 no
se midió, con sus dos razones: el corpus no registra por caso la derivación del
operador, y esos operadores son los mismos analistas que fijaron la referencia. Para
la campaña de medición, la tesis SHALL reportar la exactitud estricta y laxa del
brazo manual calculada por c-167 contra la referencia del consenso del doble
etiquetado nuevo (casos con coincidencia `E1 = E2`; los discordantes se informan
aparte), por operador (`O1`, `O2`) con intervalo de Wilson y agregada con intervalo
bootstrap por caso, junto con el contraste de McNemar entre el brazo manual y el
automatizado sobre los mismos casos, siempre que `evaluation/data/campana/registro_sujetos.csv`
no muestre solape entre los operadores y quienes produjeron la referencia. Si hay
solape, la tesis SHALL declarar la exactitud manual "no medida: operadores no
independientes" y MUST NOT cuantificarla. Con la exactitud medida, la tasa de
derivación errónea manual SHALL presentarse como `1 - exactitud estricta del brazo
manual` de la campaña de medición, con su intervalo, y la exactitud mínima de
equilibrio SHALL recalcularse con esa tasa, conservando el costo por derivación
errónea como estimación propia (10 a 15 minutos) y, por lo tanto, el balance neto
como `condicional` a ese costo; el 15 % preliminar SHALL conservarse rotulado como
estimación preliminar y como fila de la grilla de sensibilidad. El documento MUST NOT
enunciar el signo del balance neto como resultado salvo que el intervalo del balance,
evaluado en todo el rango de costos declarado, quede íntegramente de un lado de cero;
en ese caso SHALL declararlo con el rango de costos que lo sostiene.

#### Scenario: Declaracion en la discusion

- **WHEN** la exactitud manual de la campaña de medición fue medida y se leen `subsec:balance-neto` y la limitación sobre etiquetadores y operadores de `subsec:limitaciones-estudio`
- **THEN** se declara que la campaña 2026-10 no midió la exactitud manual y que la campaña de medición la midió con operadores independientes de la referencia, con su valor e intervalo
- **AND** la exactitud mínima de equilibrio se informa con la tasa manual medida y el balance neto se declara condicional al costo por derivación errónea, salvo el caso de signo determinado en todo el rango de costos

#### Scenario: Exactitud manual no medida por falta de independencia

- **WHEN** `registro_sujetos.csv` muestra solape entre los operadores y los productores de la referencia
- **THEN** la tesis declara la exactitud manual "no medida: operadores no independientes"
- **AND** el balance neto se declara indeterminado con el diseño de ambas campañas y se conserva el 15 % preliminar como único valor atribuido al flujo manual

#### Scenario: Declaracion en el planteamiento del problema

- **WHEN** se lee el planteamiento del problema en `01-introduccion.tex`
- **THEN** la tasa de derivación errónea del 15 % se califica como estimación preliminar, de la misma naturaleza que los 2 minutos 45 segundos
- **AND** el párrafo remite a `subsec:balance-neto`, donde figura la tasa medida o la declaración de no medida

#### Scenario: Sin tasa manual presentada como medida

- **WHEN** se recorren las secciones de la tesis en busca de una exactitud o tasa de derivación errónea del flujo manual
- **THEN** solo se presenta como medida la de la campaña de medición, rotulada con su campaña, sus operadores y su referencia
- **AND** ningún pasaje atribuye una exactitud manual medida a la campaña 2026-10 ni afirma un signo del balance neto que su intervalo no sostenga

### Requirement: Intervalos de confianza del kappa y por clase en la tesis

El marco metodologico y el capitulo de resultados SHALL reportar la incertidumbre del
acuerdo inter-evaluador y los intervalos de confianza de las metricas por clase
(precision, sensibilidad, F1), declarando el nivel de confianza y el procedimiento de
estimacion. Para el kappa `0,87` de la campaña 2026-10, la tesis SHALL declarar que su
intervalo de confianza no es computable porque la tabla primaria del doble etiquetado
no se conservó, y MUST NOT atribuirle un intervalo. El kappa de la campaña de medición
SHALL reportarse como un valor distinto ("fiabilidad del doble etiquetado de la campaña
de medición", etiquetadores `E1` y `E2`, `n` casos, etiqueta primaria, cinco clases, no
ponderado), con su intervalo asintótico (varianza de Fleiss, Cohen y Everitt, 1969) y
su intervalo bootstrap percentil (`B = 2000`, semilla `20261021`), `p_o`, `p_e` y PABAK,
y con su propio rótulo de Landis y Koch derivado del valor puntual, señalando si el
intervalo abarca dos categorías; si c-167 declara el intervalo no estimable (`p_e = 1`
o remuestras degeneradas), la tesis SHALL declararlo así sin fabricar un intervalo. El
documento SHALL declarar como no estimable la clase con soporte unitario (`Bases de
Datos`, `n = 1`) y SHALL excluirla del macro-F1 de umbral, conservando el macro-F1 de
cinco clases como valor informativo.

#### Scenario: IC del kappa reportado

- **WHEN** se lee el pasaje del doble etiquetado en metodologia, resultados o discusion
- **THEN** el kappa `0,87` figura como valor de la campaña 2026-10, sin intervalo y con la declaracion de que la tabla primaria no se conservó, y su rotulo sigue siendo "casi perfecto" (Landis & Koch)
- **AND** el kappa de la campaña de medicion figura como valor distinto, con `n`, etiquetadores `E1`/`E2`, intervalo asintotico e intervalo bootstrap con semilla, o con la declaracion de intervalo no estimable, y con su propio rotulo de Landis y Koch

#### Scenario: Intervalo que abarca dos categorias

- **WHEN** el intervalo del kappa de la campaña de medicion cruza un limite de los rangos de Landis y Koch
- **THEN** el texto rotula el kappa por su valor puntual y declara que el intervalo abarca dos categorias
- **AND** no presenta el rotulo puntual como certeza

#### Scenario: IC por clase reportado

- **WHEN** se lee la tabla de metricas por clase en resultados
- **THEN** cada clase estimable reporta su IC de precision, sensibilidad y F1
- **AND** la clase `Bases de Datos` figura como no estimable y sin IC

#### Scenario: Exclusion de la clase no estimable del umbral

- **WHEN** se lee el macro-F1 asociado al umbral de clasificacion
- **THEN** el macro-F1 de umbral se reporta sobre las cuatro clases estimables (`0,6508`)
- **AND** el macro-F1 de cinco clases (`0,5207`) se conserva como valor informativo
- **AND** el `0,0000` de `Bases de Datos` no se presenta como evidencia de desempeno

### Requirement: Declaracion del intervalo de confianza del kappa

La tesis SHALL tratar por separado los dos coeficientes kappa. El kappa `0,87` de la
campaña 2026-10 SHALL conservarse como valor historico, con su rotulo "casi perfecto"
(Landis y Koch) y con la declaracion explicita, elevada al cuerpo, de que su intervalo
de confianza no es computable porque la tabla primaria de doble etiquetado no se
conservó; la tesis MUST NOT fabricar ni estimar ese intervalo ni presentar el
intervalo del kappa nuevo como si fuera el del `0,87`. El kappa de la campaña de
medicion SHALL calcularse por c-167 sobre `evaluation/data/campana/doble_etiquetado.csv`
(tabla versionada con SHA-256) y reportarse con su intervalo asintotico y su intervalo
bootstrap con semilla fija declarada, o con la declaracion de intervalo no estimable.
La decision y los valores SHALL quedar registrados en el memo canonico
(`docs/Tesis/Correcciones/numeros-canonicos.md`) y en el diseno del cambio.

#### Scenario: Tabla recuperable

- **WHEN** la tabla primaria del doble etiquetado de la campaña de medicion esta versionada en `evaluation/data/campana/doble_etiquetado.csv` con su SHA-256
- **THEN** la tesis reporta el kappa de la campaña de medicion con su intervalo asintotico y su intervalo bootstrap, declarando metodo y semilla, o declara el intervalo no estimable si c-167 asi lo informa
- **AND** el kappa `0,87` permanece sin intervalo, como valor de la campaña 2026-10

#### Scenario: Tabla no recuperable

- **WHEN** se lee la declaracion sobre el kappa `0,87` de la campaña 2026-10
- **THEN** la tesis declara de forma explicita que su intervalo de confianza es no computable por ausencia de la tabla primaria
- **AND** no se fabrica ni se estima un intervalo para el `0,87`
- **AND** el rotulo interpretativo "casi perfecto" (Landis y Koch) se conserva

### Requirement: Declaración del estado de la hipótesis principal

El resumen, la discusión y las conclusiones SHALL declarar el estado de la
hipótesis principal como parcialmente confirmada y parcialmente refutada: se
confirma en la reducción del tiempo de registro y se refuta en el umbral de
clasificación (`73,5 %` de exactitud y macro-F1 de umbral `0,6508` sobre las cuatro
clases estimables, por debajo de `85 %` y `0,85`). El resumen MUST NOT permitir
inferir una confirmación plena de la hipótesis. La declaración SHALL distinguir las
sub-hipótesis de tiempo, intervención humana y exactitud o F1. La sub-hipótesis de
intervención humana SHALL declararse con el estado que fije la campaña de medición:
**contrastada: compatible** si el límite superior del intervalo de Wilson de la
`tasa_intervencion_humana` es menor que `0,15`; **contrastada: refutada** si la
estimación puntual es mayor o igual que `0,15`; **contrastada: no concluyente** si la
estimación puntual es menor que `0,15` pero el límite superior es mayor o igual que
`0,15`; o **no contrastada: registro incompleto** si el export de intervenciones no
cubre la corrida. La estimación y ambos límites son los que entregue c-167. En ningún estado el documento SHALL conservar la
declaración "no contrastada por ausencia de registro primario" como estado vigente, ni
reintroducir el `9,5 %` retirado (c-107). Las conclusiones SHALL declarar el estado por
sub-hipótesis —confirmada en tiempo, refutada en clasificación y el estado que
corresponda en intervención humana— junto con el estado de las dos hipótesis
subsidiarias.

#### Scenario: Estado parcial declarado en el resumen

- **WHEN** se lee el resumen en español y el abstract
- **THEN** se declara que la hipótesis principal se confirma en tiempo y se refuta en clasificación
- **AND** no se presenta el umbral de clasificación como alcanzado

#### Scenario: Estado parcial declarado en discusión y conclusiones

- **WHEN** se leen la discusión y las conclusiones
- **THEN** el estado de la hipótesis principal se declara parcialmente confirmado y parcialmente refutado
- **AND** la refutación se ancla en las métricas de clasificación reportadas

#### Scenario: Sub-hipótesis de intervención humana declarada no medida

- **WHEN** se lee el estado de la hipótesis principal en el resumen y las conclusiones
- **THEN** la sub-hipótesis de intervención humana se declara con uno de los cuatro estados de la campaña de medición ("contrastada: compatible", "contrastada: refutada", "contrastada: no concluyente" o "no contrastada: registro incompleto"), idéntico en ambas secciones
- **AND** no se reporta el `9,5 %` de intervención humana como resultado vigente ni se conserva "no contrastada por ausencia de registro primario"

#### Scenario: Sub-hipótesis de intervención contrastada y compatible

- **WHEN** el límite superior del intervalo de Wilson de la `tasa_intervencion_humana` de la campaña de medición es menor que `0,15`
- **THEN** el resumen, la introducción, los resultados y las conclusiones declaran la sub-hipótesis "contrastada: compatible" con la tasa, su `n` y su intervalo
- **AND** no se reporta el `9,5 %` como resultado vigente

#### Scenario: Sub-hipótesis de intervención contrastada y refutada

- **WHEN** la estimación puntual de la `tasa_intervencion_humana` es mayor o igual que `0,15`
- **THEN** las cuatro secciones declaran la sub-hipótesis "contrastada: refutada" con la tasa, su `n` y su intervalo
- **AND** la hipótesis principal se declara confirmada en tiempo y refutada en clasificación y en intervención humana

#### Scenario: Sub-hipótesis de intervención contrastada y no concluyente

- **WHEN** la estimación puntual es menor que `0,15` y el límite superior del intervalo de Wilson es mayor o igual que `0,15`
- **THEN** el resumen, la introducción, los resultados, las conclusiones y el memo declaran la sub-hipótesis "contrastada: no concluyente" con la tasa, su `n` y su intervalo
- **AND** no se la presenta como confirmada ni como refutada, y la hipótesis principal se declara confirmada en tiempo, refutada en clasificación y no concluyente en intervención humana

#### Scenario: Sub-hipótesis de intervención no contrastada por registro incompleto

- **WHEN** el export de intervenciones no cubre la corrida de la campaña de medición
- **THEN** las cuatro secciones declaran la sub-hipótesis "no contrastada: registro incompleto" sin cuantificar la proporción
- **AND** no se conserva la declaración "no contrastada por ausencia de registro primario" como estado vigente

#### Scenario: Estado por sub-hipótesis en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** se distingue explícitamente la sub-hipótesis confirmada (tiempo), la refutada (exactitud/F1) y el estado de la de intervención humana fijado por la campaña de medición
- **AND** no se declara la hipótesis principal confirmada o refutada como bloque
- **AND** se declara el estado de las dos hipótesis subsidiarias

### Requirement: Segunda sub-hipotesis con fraccion esperada explicita

La segunda sub-hipotesis (`01-introduccion.tex`, `subsec:hipotesis-trabajo`) SHALL
enunciarse con una fraccion esperada numerica explicita, derivada de un criterio
fijado a priori en el propio documento (en esta version, una proporcion de casos con
accion manual de un operador no superior a `0,15`, complemento del umbral de
exactitud del 85 %), junto con su contraste (proporcion con intervalo de confianza de
Wilson) y su criterio de decision: compatible si el limite superior es menor que
`0,15`, refutada si la estimacion puntual es mayor o igual que `0,15` y no concluyente
si la estimacion es menor que `0,15` pero el limite superior no lo es. El texto
SHALL presentar la sub-hipotesis solo en su formulacion vigente y MUST NOT narrar
formulaciones anteriores del manuscrito; esa historia SHALL constar en el registro de
correcciones. El estado de la sub-hipotesis SHALL ser el que fije la campaña de
medicion ("contrastada: compatible", "contrastada: refutada", "contrastada: no
concluyente" o "no contrastada: registro incompleto") y SHALL propagarse de forma identica al resumen, la
introduccion, los resultados y las conclusiones. El contraste SHALL apoyarse
exclusivamente en la `tasa_intervencion_humana` de la campaña de medicion (c-167); el
documento MUST NOT presentar las derivaciones del gate de la campaña 2026-10 (ninguna
en el corpus) como contraste o confirmacion, y MUST NOT cuantificar la proporcion en
el estado "no contrastada: registro incompleto". Toda remision desde la sub-hipotesis
SHALL apuntar a una seccion que informe el resultado de la campaña de medicion o su
ausencia; si remite a `subsec:limitaciones-estudio`, la oracion introductoria de esa
lista SHALL declarar el numero real de limitaciones listadas.

#### Scenario: Fraccion esperada y criterio de falsacion explicitos

- **WHEN** se lee la segunda sub-hipotesis en `01-introduccion.tex`
- **THEN** declara la cota numerica, su derivacion del umbral fijado a priori, el contraste con intervalo de Wilson y el criterio de falsacion
- **AND** la cota figura en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Formulacion vigente sin narrar la anterior

- **WHEN** se lee la segunda sub-hipotesis
- **THEN** no aparecen "formulación original", "no era contrastable" ni "tampoco esta se contrasta"
- **AND** el registro de correcciones conserva literal el texto retirado con su ubicacion previa

#### Scenario: Formulacion original declarada no contrastable

- **WHEN** se busca en el cuerpo de la tesis la formulacion original de la segunda sub-hipotesis (comparacion con el proceso manual, donde la intervencion es total por definicion)
- **THEN** el cuerpo no la narra ni declara que no era contrastable
- **AND** esa formulacion original y su no contrastabilidad constan solo en el registro de correcciones y en el Anexo I

#### Scenario: Sin confirmacion espuria por el gate

- **WHEN** se leen la introduccion y la subseccion `subsec:reduccion-intervencion` de resultados
- **THEN** la ausencia de derivaciones del gate en la campaña 2026-10 no se presenta como contraste ni como confirmacion de la sub-hipotesis
- **AND** el contraste, si existe, se apoya solo en la tasa de la campaña de medicion

#### Scenario: Estado propagado

- **WHEN** se busca el rotulo de la segunda sub-hipotesis en `00-resumen.tex`, `01-introduccion.tex`, `07-resultados.tex` y `09-conclusiones.tex`
- **THEN** en los cuatro aparece el mismo estado de la campaña de medicion ("contrastada: compatible", "contrastada: refutada", "contrastada: no concluyente" o "no contrastada: registro incompleto")
- **AND** ninguno conserva "no contrastada por ausencia de registro primario" ni cuantifica la proporcion en el estado de registro incompleto

#### Scenario: Remision coherente con su destino

- **WHEN** se sigue la remision `\autoref` de la segunda sub-hipotesis en `01-introduccion.tex`
- **THEN** la seccion de destino informa la tasa de la campaña de medicion con su intervalo, o declara el registro incompleto
- **AND** si el destino es `subsec:limitaciones-estudio`, el conteo de su oracion introductoria coincide con el numero de limitaciones listadas

### Requirement: Tratamiento honesto del confundido de la rotación de operadores

Cuando el documento declare rotación o contrabalanceo de operadores entre las
mitades del corpus, SHALL reconocer explícitamente si dicha rotación queda
confundida con el efecto del operador dado el número de operadores y de mitades
empleados. Para la campaña 2026-10, la rotación de dos operadores entre dos mitades
SHALL seguir declarándose confundida con el efecto del operador. Para la campaña de
medición, el documento SHALL describir el contrabalanceo de condición del plan
`evaluation/data/campana/plan_campana.csv` (`posicion`, `mitad`, `brazo_primero`) y
SHALL reportar el efecto de orden de condición (tiempo manual con `brazo_primero`
manual frente a automatizado) y el de posición (Spearman y mitad 1 frente a mitad 2),
con el efecto mínimo detectable que c-167 informe para cada análisis (el de condición,
entre grupos independientes), si c-167 los declara estimados; en caso contrario
SHALL declarar la limitación residual. Si la rotación no elimina el confundido, el
documento MUST NOT presentarla como mitigación no calificada del efecto de
aprendizaje.

#### Scenario: Confundido reconocido

- **WHEN** se lee la descripción del contrabalanceo del orden de procesamiento
- **THEN** el texto declara cuántos operadores y cuántas mitades intervinieron en cada campaña
- **AND** reconoce si la rotación de operadores queda confundida con el efecto del operador

#### Scenario: Mitigación no sobrevendida

- **WHEN** se lee la lista de amenazas a la validez y sus mitigaciones
- **THEN** la rotación de operadores no se presenta como mitigación no calificada si está confundida
- **AND** se declara la limitación resultante, el efecto de orden estimado por la campaña de medición o la limitación residual

### Requirement: Procedencia declarada de los ajustes realizados sobre el corpus de validacion

La tesis SHALL declarar en la discusion (`subsec:interpretacion-resultados`) que el
vocabulario del filtro deterministico (c-71), las reglas de frontera del prompt (c-72)
y el punto de operacion del cortocircuito (c-74) se derivaron de casos y errores
observados en el corpus de validacion de 200 casos; SHALL acotar que la mitigacion
fuera de muestra de c-74 (validacion cruzada de cinco pliegues para el punto de
operacion) NO cubre la ampliacion del vocabulario ni las reglas del prompt; SHALL
declarar que no se dispuso de un corpus independiente de preproduccion para la
campaña 2026-10; y SHALL calificar las metricas de clasificacion de los 200 casos
(`73,5 %`, `0,6508` y derivadas) como estimaciones dentro de la muestra, aun cuando la
campaña de medicion aporte una validacion fuera de muestra (que se reporta aparte,
segun el requisito "Reporte de la validacion fuera de muestra"). Las demas secciones
que afirman la ausencia de exposicion al corpus (`05-arquitectura.tex`,
`06-implementacion.tex`, Anexo H) SHALL alinearse con esa declaracion o remitir a
ella. La tesis MUST NOT afirmar separacion estricta entre datos de construccion y de
validacion, ausencia de exposicion al corpus ni desempeno sobre datos no vistos que no
provenga del corpus independiente de la campaña de medicion; MUST NOT afirmar la
existencia de un conjunto de aproximadamente 100 incidentes de preproduccion ni
remitir a `docs/prompt_gemini_history/`; y MUST NOT alterar ningun valor numerico por
esta declaracion.

#### Scenario: Procedencia de los tres ajustes declarada

- **WHEN** se lee `subsec:interpretacion-resultados` en el PDF compilado
- **THEN** se declaran los ajustes del vocabulario del filtro deterministico, de las reglas de frontera del prompt y del punto de operacion realizados sobre el corpus de validacion
- **AND** las metricas de clasificacion de los 200 casos se califican como estimaciones dentro de la muestra

#### Scenario: Mitigacion fuera de muestra acotada

- **WHEN** se lee la declaracion de procedencia
- **THEN** la mitigacion fuera de muestra de c-74 se acota al punto de operacion
- **AND** se declara expresamente que esa mitigacion no cubre el vocabulario ni las reglas del prompt

#### Scenario: Sin corpus independiente de preproduccion

- **WHEN** se busca en `sections/*.tex` una afirmacion sobre un corpus independiente de incidentes de preproduccion
- **THEN** se declara que la campaña 2026-10 no dispuso de un corpus de esas caracteristicas
- **AND** no se afirma la existencia de un conjunto de aproximadamente 100 incidentes de preproduccion

#### Scenario: Sin afirmacion de no exposicion

- **WHEN** se buscan en `sections/*.tex` las afirmaciones "sin exposicion a" (el corpus o los 200 casos de validacion), "sin acceso al corpus", "datos no vistos" y "separacion estricta"
- **THEN** ninguna aparece como afirmacion vigente sobre la version evaluada
- **AND** la unica mencion admisible de desempeno fuera de muestra remite al corpus independiente de la campaña de medicion

#### Scenario: Numeros intactos

- **WHEN** se comparan las metricas de clasificacion del PDF antes y despues de la declaracion
- **THEN** no cambia ningun valor numerico

### Requirement: Priorización de las líneas de trabajo futuro sobre los defectos medidos

El capítulo de recomendaciones (`10-recomendaciones.tex`) SHALL priorizar
explícitamente las líneas de trabajo futuro que atacan los defectos medidos en el
estudio: la calibración del gate de confianza y la incorporación de un clasificador
supervisado con corpus propio. La corrección de la medición de intervención humana
SHALL figurar como línea prioritaria solo si la sub-hipótesis de intervención quedó
"no contrastada: registro incompleto"; si quedó contrastada (compatible, refutada o no concluyente),
SHALL dejar de figurar como prioritaria y la subsección `subsec:medicion-intervencion`
SHALL reclasificarse según el requisito "Subseccion de correccion de la medicion de
intervencion humana". La priorización SHALL distinguir esas líneas de las extensiones
genéricas (canales adicionales, paneles, base de conocimientos) y SHALL ser coherente
con las limitaciones reconocidas en la discusión.

#### Scenario: Líneas prioritarias declaradas

- **WHEN** se lee la introducción o el cierre del capítulo de recomendaciones
- **THEN** el texto declara explícitamente cuáles líneas futuras son prioritarias, entre ellas la calibración del gate y el clasificador supervisado
- **AND** la corrección de la medición de intervención figura como prioritaria solo en el estado "no contrastada: registro incompleto"

#### Scenario: Distinción respecto de las líneas genéricas

- **WHEN** se leen las líneas de canales adicionales, paneles o base de conocimientos
- **THEN** se presentan como extensiones no prioritarias o subordinadas a las líneas que atacan los defectos medidos
- **AND** la priorización es coherente con las limitaciones de la discusión

### Requirement: Correspondencia entre el parrafo de priorizacion y las subsecciones del capitulo

El parrafo introductorio del capitulo de recomendaciones SHALL referenciar con
`\autoref` la subseccion propia de cada linea anunciada como prioritaria (calibracion
del gate de confianza, clasificador supervisado con corpus propio y, solo en el estado
"no contrastada: registro incompleto" de la sub-hipotesis de intervencion, correccion
de la medicion de intervencion humana), y cada una de esas lineas SHALL existir como
`\subsection` con `\label`. Las subsecciones prioritarias SHALL preceder al resto de
las subsecciones del capitulo; `subsec:medicion-intervencion` SHALL conservar su
rotulo y su posicion inmediatamente despues de `subsec:clasificador-supervisado` en
todos los estados. El parrafo SHALL clasificar cada subseccion del capitulo en un
nivel de prioridad, y su remision al analisis de errores SHALL apuntar a
`subsec:analisis-errores`. El capitulo MUST NOT anunciar una linea prioritaria sin
desarrollo propio.

#### Scenario: Cada linea prioritaria tiene subseccion

- **WHEN** se extraen los `\autoref` del parrafo introductorio y los `\label` de las subsecciones del capitulo
- **THEN** `subsec:calibracion-gate` y `subsec:clasificador-supervisado` aparecen en ambos conjuntos, y `subsec:medicion-intervencion` aparece como prioritaria solo en el estado de registro incompleto
- **AND** no queda ninguna linea anunciada como prioritaria sin subseccion propia

#### Scenario: Orden de las subsecciones prioritarias

- **WHEN** se comparan las posiciones de los rotulos de subseccion en `10-recomendaciones.tex`
- **THEN** los rotulos prioritarios aparecen antes que cualquier otro rotulo de subseccion no prioritario, con la salvedad de `subsec:medicion-intervencion`, que conserva su posicion aunque se reclasifique
- **AND** `subsec:medicion-intervencion` sigue inmediatamente a `subsec:clasificador-supervisado`

#### Scenario: Todas las subsecciones clasificadas y remision correcta

- **WHEN** se compara el parrafo introductorio con la lista de subsecciones del capitulo
- **THEN** cada subseccion figura en uno de los niveles de prioridad enunciados
- **AND** la remision al analisis de errores apunta a `subsec:analisis-errores` y no a `subsec:calibracion`

### Requirement: Subseccion de correccion de la medicion de intervencion humana

El capitulo de recomendaciones SHALL incluir una subseccion propia, rotulada
`subsec:medicion-intervencion` y ubicada inmediatamente despues de la subseccion del
clasificador supervisado, cuyo contenido y titulo dependen del estado de la
sub-hipotesis de intervencion fijado por la campaña de medicion. En el estado "no
contrastada: registro incompleto", la subseccion SHALL proponer el protocolo de
registro primario por caso (ocurrencia y origen, consigna de tiempo de inicio y de
fin, resultado y operador seudonimizado, almacenado en `clasificacion_log` ampliado o
en una tabla dedicada vinculada al incidente) y explicar por que la corrida no quedo
cubierta. En los estados "contrastada: compatible", "contrastada: refutada" o "contrastada:
no concluyente", la
subseccion SHALL retitularse para no prometer una correccion ya realizada (por
ejemplo, "Medición continua de la intervención humana en operación"), SHALL declarar
que el protocolo se implemento en la campaña de medicion (c-165) con remision a
`subsec:reduccion-intervencion`, y SHALL recomendar su continuidad en operacion para
estimar la cobertura efectiva del gate y el costo de las reasignaciones (en el estado
no concluyente, ademas, con un tamano muestral que permita resolver el contraste
frente a `0,15`). En todos los
estados la definicion operacional SHALL alinearse con las dos formas rotuladas de la
variable de `tab:variables`, aplicadas de igual modo en ambos brazos, y la subseccion
MUST NOT reportar ninguna proporcion de intervencion humana como resultado propio (la
cifra vive en resultados).

#### Scenario: Subseccion presente a continuacion del clasificador supervisado

- **WHEN** se inspecciona `10-recomendaciones.tex`
- **THEN** existe una `\subsection` con `\label{subsec:medicion-intervencion}`
- **AND** es la subseccion inmediatamente posterior a `subsec:clasificador-supervisado`

#### Scenario: Protocolo de registro primario por caso

- **WHEN** la sub-hipotesis quedo "no contrastada: registro incompleto" y se lee la subseccion
- **THEN** el protocolo enumera la ocurrencia y el origen de la intervencion, la consigna de tiempo de inicio y de fin, el resultado y el operador seudonimizado
- **AND** indica como almacenamiento la ampliacion de `clasificacion_log` o una tabla dedicada vinculada al incidente

#### Scenario: Subseccion retitulada tras el contraste

- **WHEN** la sub-hipotesis quedo contrastada (compatible, refutada o no concluyente) y se lee la subseccion
- **THEN** el titulo no anuncia una "Corrección de la medición" ya realizada y el texto remite a `subsec:reduccion-intervencion`
- **AND** recomienda la continuidad del registro en operacion para la cobertura del gate y el costo de las reasignaciones

#### Scenario: Definicion alineada con la tabla de variables y contrastabilidad

- **WHEN** se compara la subseccion con `tab:variables` y con la sub-hipotesis de intervencion de `subsec:hipotesis-trabajo`
- **THEN** la definicion operacional usa las mismas dos formas rotuladas (proporcion de casos y proporcion del tiempo del proceso) aplicadas a ambos brazos
- **AND** la subseccion es coherente con el estado de la sub-hipotesis declarado en la introduccion

#### Scenario: Sin proporcion de intervencion reportada

- **WHEN** se buscan en el capitulo de recomendaciones cifras de proporcion de intervencion humana
- **THEN** no aparece ninguna presentada como resultado propio del capitulo
- **AND** no aparece el 9,5 % retirado

### Requirement: Linea futura de medicion de la exactitud manual y del costo de reasignacion

El capitulo de recomendaciones SHALL incluir, en `subsec:estudios-replicacion`, la
recomendacion de que toda replicacion registre por caso la derivacion efectuada en el
brazo manual, con etiquetadores distintos de los operadores, y cronometre cada
reasignacion. Si la campaña de medicion midio la exactitud manual, la recomendacion
SHALL presentar ese diseno como ya aplicado en la campaña de medicion (con remision a
resultados) y SHALL conservar como pendiente el cronometraje de las reasignaciones,
necesario para cerrar el balance neto; si la exactitud manual quedo "no medida:
operadores no independientes", SHALL conservar la recomendacion completa. La
subseccion `subsec:balance-neto` SHALL remitir a esa recomendacion, y el capitulo MUST
NOT duplicarla en otra subseccion.

#### Scenario: Recomendacion presente y conectada

- **WHEN** se lee `subsec:estudios-replicacion`
- **THEN** recomienda registrar por caso la derivacion del brazo manual con etiquetadores distintos de los operadores y cronometrar las reasignaciones, o declara aplicada la primera parte en la campaña de medicion y pendiente la segunda
- **AND** remite a `subsec:balance-neto`, que a su vez remite a esta subseccion

#### Scenario: Sin duplicacion en recomendaciones

- **WHEN** se recorre el capitulo de recomendaciones
- **THEN** la medicion de la exactitud del flujo manual se recomienda una sola vez
- **AND** no existe una subseccion adicional que repita esa recomendacion

### Requirement: Replicaciones con exactitud del flujo manual y asignacion muestral no proporcional

La subseccion de estudios de replicacion (`subsec:estudios-replicacion`) SHALL
recomendar medir la exactitud del flujo manual sobre el mismo corpus, con
etiquetadores distintos de los operadores del brazo manual, presentandola como ya
realizada en la campaña de medicion cuando la exactitud manual fue medida (y como
pendiente cuando quedo "no medida: operadores no independientes"), y SHALL recomendar
una asignacion muestral no proporcional que sobremuestree las clases minoritarias y
pondere las estimaciones globales por la distribucion del universo. La subseccion
SHALL conservar su rotulo y los contextos de replicacion que ya enuncia.

#### Scenario: Exactitud del flujo manual con etiquetadores independientes

- **WHEN** se lee la subseccion de estudios de replicacion
- **THEN** recomienda medir la exactitud del flujo manual sobre el mismo corpus, o la declara realizada en la campaña de medicion con remision a resultados
- **AND** exige que los etiquetadores de la referencia sean distintos de los operadores del brazo manual

#### Scenario: Asignacion no proporcional ponderada

- **WHEN** se lee la subseccion de estudios de replicacion
- **THEN** recomienda sobremuestrear las clases minoritarias y ponderar las estimaciones globales por la distribucion del universo
- **AND** si menciona la clase Bases de Datos, lo hace con el soporte canonico de un caso

#### Scenario: Rotulo y contextos preservados

- **WHEN** se inspecciona la subseccion de estudios de replicacion
- **THEN** conserva `\label{subsec:estudios-replicacion}`
- **AND** mantiene los contextos de replicacion del sector publico, del sector industrial y de organizaciones de mayor tamano

### Requirement: Grados de cumplimiento de los objetivos acotados a la evidencia

La tabla `tab:cumplimiento-objetivos` de `09-conclusiones.tex` SHALL asignar a cada objetivo el grado "Alcanzado" solo cuando cada componente exigido por su enunciado literal en `01-introduccion.tex` este evidenciado en la version evaluada o en la campaña de medicion; "Alcanzado parcialmente" cuando al menos un componente este evidenciado y al menos otro no se cumpla o no se haya medido; y "No alcanzado" cuando no se cumpla el criterio del objetivo. Toda fila "Alcanzado parcialmente" SHALL nombrar en su evidencia el componente no cumplido o no medido. Los objetivos especificos 1, 3 y 6 SHALL figurar como "Alcanzado parcialmente" mientras falte la evidencia de, respectivamente, la comunicacion asincronica (el alta sigue siendo sincronica, con reintentos idempotentes); la complejidad operativa percibida por los usuarios (la latencia y la exactitud por canal ya estan medidas); y la recalibracion de la confianza, con el analisis de errores y las bandas de confianza estimados dentro de la muestra. El objetivo especifico 4 SHALL figurar como "Alcanzado" solo si la campaña de medicion midio la exactitud del brazo manual (con el contraste de McNemar) y contrasto la intervencion humana (compatible, refutada o no concluyente); en otro caso SHALL figurar como "Alcanzado parcialmente" nombrando el componente faltante ("exactitud manual no medida: operadores no independientes" o "intervencion no contrastada: registro incompleto"). La verificacion de TLS SHALL declararse igual en la celda del objetivo 1 y en la prosa de las conclusiones: realizada despues de la campana, sobre el despliegue de referencia de la version entregada, y no sobre la configuracion evaluada ni sobre la instancia operativa. El objetivo general SHALL desglosarse en sus tres componentes (tiempo de registro, calidad de la clasificacion y proporcion de intervencion humana) con estado individual, y su grado global SHALL ser coherente con ese desglose. El documento MUST NOT reformular el enunciado de un objetivo para ajustarlo a lo construido o medido, y la prosa de las conclusiones SHALL ser coherente con la tabla.

#### Scenario: Objetivos 1, 3 y 4 parcialmente alcanzados

- **WHEN** se leen las filas de los objetivos especificos 1, 3 y 4 en `tab:cumplimiento-objetivos`
- **THEN** las filas 1 y 3 declaran "Alcanzado parcialmente" y la fila 4 lo declara salvo que la campaña de medicion haya medido la exactitud manual y contrastado la intervencion
- **AND** su evidencia nombra el componente faltante: alta sincronica y TLS verificado solo despues de la campana en el despliegue de referencia (1); complejidad percibida no medida, con latencia y exactitud por canal medidas (3); el estado negativo de la campaña de medicion que corresponda (4)

#### Scenario: Objetivo 4 segun la campaña de medicion

- **WHEN** se lee la fila del objetivo especifico 4 en `tab:cumplimiento-objetivos`
- **THEN** declara "Alcanzado" si la exactitud manual fue medida con su contraste de McNemar y la intervencion quedo contrastada, citando ambas evidencias de la campaña de medicion
- **AND** en otro caso declara "Alcanzado parcialmente" y nombra el componente faltante con el rotulo del estado negativo correspondiente

#### Scenario: Objetivo 6 parcialmente alcanzado

- **WHEN** se lee la fila del objetivo especifico 6 en `tab:cumplimiento-objetivos`
- **THEN** declara "Alcanzado parcialmente"
- **AND** su evidencia nombra el componente faltante: confianza no recalibrada y analisis estimado dentro de la muestra

#### Scenario: Objetivo general desglosado

- **WHEN** se lee la fila del objetivo general
- **THEN** figuran el tiempo de registro como alcanzado, la calidad de la clasificacion como evaluada por debajo del umbral y la intervencion humana con el estado fijado por la campaña de medicion (compatible, refutada, no concluyente o no contrastada por registro incompleto)
- **AND** el grado global es "Alcanzado parcialmente"

#### Scenario: Enunciados de objetivos sin reformular

- **WHEN** se comparan los enunciados del objetivo general y de los objetivos especificos en `01-introduccion.tex` con los de la version previa al change
- **THEN** los enunciados no cambian
- **AND** solo cambia su grado de cumplimiento en la tabla

#### Scenario: Reversion condicionada a evidencia

- **WHEN** se dispone de evidencia nueva para un componente faltante del objetivo 1, del objetivo 3, del objetivo 4 o del objetivo 6 y se propone elevar su grado
- **THEN** el grado solo pasa a "Alcanzado" si la tabla cita evidencia para cada componente faltante (comunicacion asincronica, ademas del TLS ya verificado despues de la campana, para el 1; calidad por canal sin evidencia de degradacion y decision del autor sobre la complejidad percibida para el 3; exactitud manual medida e intervencion contrastada para el 4; confianza recalibrada y evaluada fuera de la muestra para el 6)
- **AND** si la evidencia es posterior a la validacion experimental, la celda lo declara

#### Scenario: Objetivo 6 con evidencia ampliada

- **WHEN** se lee la fila del objetivo especifico 6
- **THEN** su grado es "Alcanzado parcialmente" y su evidencia cita el analisis de errores, la calibracion por etapa, el analisis de sensibilidad de los ajustes (`subsec:sensibilidad-ajustes`) y la linea futura de calibracion del gate (`subsec:calibracion-gate`)
- **AND** la celda nombra la recalibracion no realizada y la estimacion dentro de la muestra como componentes faltantes, aun si la campaña de medicion aporto una validacion fuera de muestra de las metricas

#### Scenario: Prosa coherente con la tabla

- **WHEN** se leen los parrafos de las conclusiones que tratan el objetivo general y los objetivos 1, 3, 4 y 6
- **THEN** ninguno afirma un cumplimiento pleno que la tabla declare parcial, ni un cumplimiento parcial que la tabla declare pleno
- **AND** la prosa sobre TLS coincide con la celda del objetivo 1 y la del objetivo 3 lo declara alcanzado parcialmente, sin "solo en su construcción"
- **AND** el primer parrafo declara cumplido parcialmente el objetivo general

### Requirement: Parrafo introductorio del capitulo de resultados coherente con sus subsecciones

El parrafo introductorio de `07-resultados.tex` SHALL enumerar exactamente las subsecciones del capitulo, en su orden y con denominaciones coherentes con sus titulos, incluida la subseccion de resultados de la campaña de medicion, y SHALL NOT anunciar como dimension de los resultados una magnitud que el propio capitulo declara no medida o no contrastada. Si el parrafo usa un cardinal, este MUST coincidir con el numero de subsecciones.

#### Scenario: Enumeracion igual a las subsecciones

- **WHEN** se cuentan los `\subsection` de `07-resultados.tex` y las dimensiones enumeradas en su parrafo introductorio
- **THEN** ambos conjuntos coinciden en numero y en orden, incluida la subseccion de la campaña de medicion
- **AND** el cardinal "seis apartados" se actualiza al numero real de subsecciones

#### Scenario: Intervencion humana sin reduccion afirmada

- **WHEN** se lee el parrafo introductorio del capitulo de resultados
- **THEN** la dimension correspondiente se denomina "intervencion humana" o con otra denominacion neutra coherente con el titulo de su subseccion
- **AND** no se anuncia una "reduccion de la intervencion humana" salvo que la sub-hipotesis haya quedado "contrastada: compatible" y el titulo de la subseccion lo refleje

### Requirement: Viabilidad operativa presentada como condicional

El resumen (en espanol y en ingles), la justificacion de la introduccion, la discusion y las conclusiones SHALL presentar la viabilidad tecnica y la economica como sostenidas por la evidencia y la viabilidad operativa como condicional a que la exactitud efectiva supere la exactitud minima de equilibrio, sea por mejora del clasificador o porque la revision humana del sector responsable reduzca la tasa o el costo efectivos de las derivaciones erroneas. Cuando la campaña de medicion haya medido la exactitud manual, la condicion SHALL expresarse con la exactitud minima de equilibrio recalculada con la tasa manual medida y el balance neto SHALL declararse condicional al costo por derivacion erronea, salvo que su intervalo quede de un lado de cero en todo el rango de costos declarado; en ese caso la viabilidad operativa SHALL declararse con el signo y el rango que la sostienen. El documento MUST NOT afirmar que los hallazgos confirman la viabilidad "tecnica, economica y operativa" (ni la "technical, economic, and operational feasibility") como bloque incondicional. El ahorro de 32,2 horas-persona por trimestre SHALL presentarse como ahorro bruto de registro, sin cambiar su valor. El parrafo de conclusion del resumen en espanol y del abstract MUST NOT aumentar su conteo de palabras respecto de la version previa.

#### Scenario: Resumen y abstract con viabilidad operativa condicional

- **WHEN** se leen los parrafos de conclusion del resumen y del abstract en `00-resumen.tex`
- **THEN** la viabilidad tecnica y economica se presentan como confirmadas y la operativa como condicional, con el balance neto frente a las derivaciones erroneas declarado indeterminado, condicional al costo o con el signo que su intervalo sostenga
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

### Requirement: Declaración de los analistas etiquetadores

El documento SHALL declarar quiénes realizaron el etiquetado del corpus, su
independencia respecto de los autores del trabajo y si alguno de ellos participó
además como operador del brazo manual, para cada campaña. Para la campaña 2026-10
SHALL declarar que los dos analistas que fijaron la referencia fueron también los
operadores del brazo manual. Para la campaña de medición SHALL declarar a los
etiquetadores `E1` y `E2` y a los operadores `O1` y `O2` por alias seudonimizado y su
independencia mutua, respecto de los analistas originales y respecto de los autores,
según `evaluation/data/campana/registro_sujetos.csv`, o declarar el solape que ese
registro muestre. Esta declaración MUST ser coherente con el cómputo de cada acuerdo
inter-evaluador y MUST NOT incluir datos personales.

#### Scenario: Analistas declarados

- **WHEN** se lee la descripción del doble etiquetado independiente
- **THEN** se declaran los analistas etiquetadores de la campaña 2026-10 y los etiquetadores `E1`/`E2` de la campaña de medición
- **AND** se declara su independencia (o dependencia) respecto de los autores

#### Scenario: Solapamiento con el brazo manual declarado

- **WHEN** un etiquetador también operó el brazo manual en alguna de las dos campañas
- **THEN** el documento lo declara explícitamente para esa campaña
- **AND** se discute la implicancia para la independencia de la verdad fundamental

#### Scenario: Independencia de la campaña de medición

- **WHEN** `registro_sujetos.csv` no muestra solape entre `E1`, `E2`, `O1`, `O2`, los analistas originales y los autores
- **THEN** el documento declara que la campaña de medición resolvió la dependencia entre etiquetadores y operadores de la campaña 2026-10
- **AND** la declaración se acompaña de la remisión al registro de sujetos, sin datos personales

### Requirement: Propagación de la dependencia entre etiquetadores y operadores

La tesis SHALL reflejar en las conclusiones la dependencia declarada en el marco
metodológico entre los analistas etiquetadores de la verdad de referencia de la
campaña 2026-10 y los operadores del brazo manual de esa campaña (las mismas
personas), que sigue afectando a la referencia de las métricas de clasificación de
los 200 casos (`73,5 %`, `0,6508`). Esa dependencia SHALL figurar entre las
limitaciones del estudio en la discusión, no solo entre las amenazas a la validez del
capítulo metodológico, y SHALL acompañarse de su resolución por la campaña de
medición (sujetos independientes) o de la declaración de que la campaña de medición
no la resolvió. Las conclusiones MUST NOT calificar el diseño experimental como
«riguroso» ni presentarlo como plenamente independiente sin matizar esa dependencia;
la afirmación de aporte empírico SHALL quedar acotada por la independencia limitada
del referente de comparación de la campaña 2026-10.

#### Scenario: Limitación declarada en la discusión

- **WHEN** se lee la subsección de limitaciones del estudio de la discusión
- **THEN** la dependencia entre los etiquetadores de la verdad de referencia y los operadores del brazo manual de la campaña 2026-10 figura entre las limitaciones, con su resolución o no resolución por la campaña de medición
- **AND** la limitación es coherente con la declaración de la misma dependencia en el capítulo metodológico

#### Scenario: Limitación reflejada en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** la dependencia entre etiquetadores y operadores de la campaña 2026-10 se refleja como un límite del diseño
- **AND** la afirmación de aporte empírico queda acotada por la independencia limitada del referente de comparación de esa campaña

#### Scenario: Sin sobreafirmación de rigor del diseño

- **WHEN** se busca en las conclusiones un calificativo de rigor sobre el diseño experimental
- **THEN** el diseño no se describe como «riguroso» ni como plenamente independiente sin el matiz de la dependencia entre etiquetadores y operadores
- **AND** el sobreclaim señalado por la dimensión 7 del dictamen no subsiste

### Requirement: Tabla de configuracion evaluada frente a entregada

El Anexo B (`sec:anexo-repositorio`, `12-anexos.tex`) SHALL incluir una tabla con etiqueta `tab:configuracion-evaluada-entregada` y tres columnas de configuracion: "Configuracion evaluada" (commit `d6bb474`, 7-10-2026), "Configuracion de la campaña de medicion" (el commit sobre el que corrio la campaña de medicion, con c-165 a c-168 aplicados y el clasificador congelado, consignado en el README de `evaluation/data/campana/`) y "Configuracion entregada" (el tag que identifica el Anexo B en la release que cierra c-169). La tabla SHALL consignar solo valores verificados con `git show <revision>:<archivo>` o con los changes archivados: versiones de FastAPI, Uvicorn, SQLAlchemy, google-genai, pytest, pytest-cov y React; el flujo N8N versionado; los reintentos del tramo de alta (c-140); el disparador de revision por reportante no identificado en el directorio (c-82); la prueba de humo de extremo a extremo y la verificacion automatizada de TLS (c-140); la instrumentacion de intervencion (c-165) y la version del clasificador (`classifier_version`), que SHALL coincidir entre la configuracion evaluada y la de la campaña de medicion; y los componentes sin cambios. Cada valor SHALL registrarse en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md` con su comando de verificacion. La tabla MUST NOT incluir valores no verificados.

#### Scenario: Valores verificados contra ambas revisiones

- **WHEN** se compara cada celda de la tabla con `git show d6bb474:App/Backend/requirements.txt`, con el mismo archivo en el commit de la campaña de medicion y en el tag entregado, con los `package.json`/`package-lock.json` y con `n8n/workflow.json` de las tres revisiones
- **THEN** cada version de la columna evaluada coincide con la registrada (FastAPI 0.115.0, Uvicorn 0.30.6, SQLAlchemy 2.0.36, google-genai >=2.20.0, pytest 8.3.3, pytest-cov 5.0.0, React 18.3.1) y las de las otras dos columnas coinciden con `git show` de su revision
- **AND** las capacidades posteriores figuran como ausentes en la columna evaluada y presentes en las columnas posteriores con su change, incluida la instrumentacion de intervencion de c-165

#### Scenario: Clasificador congelado entre la evaluacion y la campaña de medicion

- **WHEN** se compara la fila de la version del clasificador entre la configuracion evaluada y la de la campaña de medicion
- **THEN** ambas declaran el mismo `classifier_version` y los mismos umbral, prompt y vocabulario
- **AND** si difieren, la tabla lo declara y las metricas de la campaña de medicion se rotulan como de otra configuracion del clasificador

#### Scenario: Etiqueta estable para otros changes

- **WHEN** otro change (c-159) remite a la tabla desde las leyendas de las Figuras 1 y 4
- **THEN** la referencia `\ref{tab:configuracion-evaluada-entregada}` resuelve sin advertencias de referencia indefinida

#### Scenario: Registro en el memo de conteos tecnicos

- **WHEN** se lee `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`
- **THEN** figura una seccion con cada valor de la tabla, su revision y su comando de verificacion, incluida la columna de la campaña de medicion

## REMOVED Requirements

### Requirement: Rotulo de la sub-hipotesis de intervencion humana como no contrastada

**Reason**: El rotulo "no contrastada por ausencia de registro primario" queda
superado por la campaña de medicion, que aporta un registro primario de intervencion
por caso (`evaluation/data/campana/intervenciones.csv`). Su estado pasa a ser uno de
cuatro valores condicionales ("contrastada: compatible", "contrastada: refutada",
"contrastada: no concluyente" o "no contrastada: registro incompleto"), incompatibles con el rotulo fijo que este
requisito imponia.

**Migration**: El estado y su propagacion al resumen, la introduccion, los
resultados y las conclusiones quedan regidos por los requisitos modificados
"Declaración del estado de la hipótesis principal" y "Segunda sub-hipotesis con
fraccion esperada explicita"; el titulo de `subsec:reduccion-intervencion` y la
denominacion en el parrafo introductorio de resultados, por "Parrafo introductorio
del capitulo de resultados coherente con sus subsecciones" y por el requisito
agregado "Reporte de la tasa de intervencion humana de la campaña de medicion".

## ADDED Requirements

### Requirement: Subseccion de resultados de la campaña de medicion

El capitulo de resultados (`07-resultados.tex`, Seccion 8) SHALL incluir una
subseccion nueva, con `\label{subsec:resultados-campana-medicion}`, que reporte como
conjunto de datos adicional, rotulado con su fecha y su configuracion (Anexo B), los
resultados de la campaña de medicion: fiabilidad del doble etiquetado (kappa con
intervalo), exactitud del brazo manual, intervencion humana, efecto de orden y
validacion fuera de muestra, cada uno con el estado que fijen las salidas de c-167.
La subseccion SHALL declarar que sus valores no reemplazan los valores canonicos
vigentes de la campaña 2026-10 (`61,6 s`, `17,76 s`, `W = 363`, `73,5 %`, `0,6508`,
kappa `0,87`) y SHALL citar solo valores registrados en el memo canonico. Como el
documento ya llama "campañas" a las corridas manual y automatizada de 2026 (cronograma
`docs/diagrams/cronograma.md`, `fig:cronograma`), la tesis SHALL definir una sola vez,
en 4.2 (`subsec:diseno-experimental`), una denominacion distintiva para la campaña de
medicion de este programa (por ejemplo, "campaña complementaria de medición") y SHALL
usarla de forma uniforme en todos los capitulos, el resumen y el abstract.

#### Scenario: Subseccion presente y rotulada

- **WHEN** se inspecciona `07-resultados.tex`
- **THEN** existe una `\subsection` con `\label{subsec:resultados-campana-medicion}` que declara fecha, configuracion y `n` de la campaña de medicion
- **AND** cada valor que cita figura en `numeros-canonicos.md` con estado `vigente` o `condicional`

#### Scenario: Denominacion distintiva de la campaña

- **WHEN** se buscan en `sections/*.tex` las menciones de la campaña de medicion de este programa
- **THEN** todas usan la denominacion definida en `subsec:diseno-experimental`
- **AND** ninguna se confunde con las campañas manual y automatizada de 2026 del cronograma

#### Scenario: Valores canonicos vigentes intactos

- **WHEN** se comparan las cifras de la campaña 2026-10 en el PDF antes y despues de aplicar el change
- **THEN** `61,6 s`, `17,76 s`, `W = 363`, `73,5 %`, `0,6508` y kappa `0,87` no cambian de valor ni de estado
- **AND** ningun valor de la campaña de medicion se presenta como sustituto de esas cifras

#### Scenario: Tiempos de la campaña de medicion acotados al efecto de orden

- **WHEN** la subseccion cita tiempos del brazo manual medidos en la campaña de medicion
- **THEN** los presenta solo como insumo del analisis de efecto de orden, rotulados con su campaña
- **AND** no rehace el contraste de Wilcoxon principal ni compara esos tiempos con `17,76 s` como si fueran la misma medicion

### Requirement: Reporte de la exactitud del brazo manual de la campaña de medicion

La tesis SHALL reportar, en el marco metodologico (4.4 y 4.6) y en
`subsec:resultados-campana-medicion`, la exactitud estricta y laxa del brazo manual de
la campaña de medicion contra la referencia del consenso del doble etiquetado nuevo
(coincidencia `E1 = E2`; discordantes informados aparte): por operador (`O1`, `O2`)
con intervalo de Wilson al 95 %, agregada con intervalo bootstrap por caso
(`B = 2000`, semilla `20261021`) y con el contraste de McNemar frente al brazo
automatizado sobre los mismos casos. El brazo automatizado de ese contraste es la
exactitud de v9 (predicciones congeladas del clasificador evaluado) contra la
referencia nueva, un numero nuevo producido por c-167: SHALL rotularse como "exactitud
de v9 contra la referencia de la campaña de medicion", SHALL registrarse en el memo
como entrada propia y MUST NOT reemplazar el `73,5 %` ni ningun otro valor canonico de
v9. Si
`registro_sujetos.csv` muestra solape entre los operadores y quienes produjeron la
referencia, la tesis SHALL declarar la exactitud manual "no medida: operadores no
independientes" y MUST NOT cuantificarla.

#### Scenario: Exactitud manual reportada con IC

- **WHEN** la exactitud manual fue medida y se lee `subsec:resultados-campana-medicion`
- **THEN** se reporta la exactitud estricta y laxa por operador con intervalo de Wilson, la agregada con intervalo bootstrap, el `n` de casos de referencia y el numero de discordantes excluidos
- **AND** se reporta el contraste de McNemar entre el brazo manual y el automatizado con su estadistico y su valor p

#### Scenario: Exactitud manual no medida por falta de independencia

- **WHEN** `registro_sujetos.csv` muestra solape entre operadores y productores de la referencia
- **THEN** el marco metodologico, los resultados, la discusion, las conclusiones y el memo declaran "no medida: operadores no independientes"
- **AND** no se cuantifica ninguna exactitud del brazo manual

#### Scenario: Exactitud automatizada frente a la referencia nueva rotulada

- **WHEN** la subseccion informa la exactitud de v9 contra el consenso de `E1`/`E2`
- **THEN** la rotula como "exactitud de v9 contra la referencia de la campaña de medicion" y cita su entrada propia del memo
- **AND** no la presenta como reemplazo ni como correccion del `73,5 %` ni de otro valor canonico de v9

### Requirement: Reporte de la tasa de intervencion humana de la campaña de medicion

La tesis SHALL reportar en el marco metodologico (4.6 y 4.7) y en
`subsec:reduccion-intervencion` la `tasa_intervencion_humana` de la campaña de
medicion (c-167): proporcion de casos con `n` e intervalo de Wilson al 95 %, desglose
por origen (`gate`, `muestreo`, `rederivacion`, `completado_manual`) y por cambio de
sector, contraste con la cota `0,15` con la estimacion y ambos limites que entregue
c-167 (limite superior menor que `0,15`: compatible; estimacion mayor o igual que
`0,15`: refutada; estimacion menor que `0,15` con limite superior mayor o igual:
no concluyente) y proporcion del tiempo con intervalo bootstrap del
cociente o la declaracion "no estimable" por cobertura de inicio y fin inferior al
80 %. El titulo de `subsec:reduccion-intervencion` SHALL ser coherente con el estado
de la sub-hipotesis. Si el export no cubre la corrida, SHALL declarar "no contrastada:
registro incompleto".

#### Scenario: Tasa de intervencion reportada

- **WHEN** el export cubre la corrida y se lee `subsec:reduccion-intervencion`
- **THEN** se reporta la proporcion de casos con su `n`, su estimacion, ambos limites de Wilson, su desglose por origen y por cambio de sector y el veredicto frente a `0,15` (compatible, refutada o no concluyente)
- **AND** la proporcion del tiempo figura con su intervalo bootstrap o como "no estimable" con la cobertura observada

#### Scenario: Titulo coherente con el estado

- **WHEN** se inspecciona el titulo de `subsec:reduccion-intervencion` y su entrada en el indice
- **THEN** el titulo no promete una reduccion salvo en el estado "contrastada: compatible"
- **AND** el rotulo `subsec:reduccion-intervencion` se conserva

#### Scenario: Registro incompleto

- **WHEN** el export no cubre la corrida de la campaña de medicion
- **THEN** la subseccion declara "no contrastada: registro incompleto" y no cuantifica la proporcion
- **AND** el estado se propaga identico al resumen, la introduccion, las conclusiones y el memo

### Requirement: Reporte del efecto de orden de la campaña de medicion

La tesis SHALL describir en 4.2 (`subsec:diseno-experimental`) y 4.5
(`subsec:protocolo-pruebas`) el contrabalanceo de condicion de la campaña de medicion
(plan `evaluation/data/campana/plan_campana.csv`: `posicion`, `mitad`,
`brazo_primero`), el analisis en 4.7 (`subsec:analisis-estadistico`) y SHALL reportar
en `subsec:resultados-campana-medicion` el efecto de orden de condicion (tiempo manual
con `brazo_primero` manual frente a automatizado) y el de posicion (Spearman y mitad 1
frente a mitad 2), cada uno con el efecto minimo detectable que c-167 informe para
ese analisis, cuando c-167 los declare estimados. El efecto de condicion se estima
entre grupos independientes (casos con `brazo_primero` manual frente a automatizado),
no de forma pareada; la tesis MUST NOT citar para el un efecto minimo detectable
pareado ni ningun valor de efecto minimo detectable fijado a priori en este change. Si no son estimables (pares insuficientes o plan no cumplido), SHALL
declarar la limitacion residual en 4.8, en resultados y en la discusion. La discusion
(`08-discusion.tex`, explicaciones rivales) SHALL actualizar la frase que remite el
descarte del efecto de orden a "un diseno contrabalanceado".

#### Scenario: Efecto de orden estimado

- **WHEN** c-167 declara estimados los efectos de orden y de posicion
- **THEN** la subseccion reporta el estadistico, su resultado, el tamano de cada grupo o el numero de pares y el efecto minimo detectable que c-167 informa para cada analisis
- **AND** el efecto de condicion se presenta como contraste entre grupos independientes, sin un efecto minimo detectable pareado
- **AND** la discusion deja de remitir el descarte del efecto de orden a un diseno contrabalanceado futuro

#### Scenario: Limitacion residual declarada

- **WHEN** c-167 declara no estimable el efecto de orden o de posicion
- **THEN** 4.8, resultados y discusion declaran la limitacion residual con su causa
- **AND** el contrabalanceo no se presenta como mitigacion efectiva

### Requirement: Reporte de la validacion fuera de muestra

La tesis SHALL reportar en `subsec:resultados-campana-medicion` las metricas fuera de
muestra por etapa del clasificador congelado sobre el corpus independiente
(`evaluation/data/campana/predicciones_independiente.json`, reporte in-sample frente a
out-of-sample de c-167), con su `n` e intervalos, contrastadas con las estimaciones
dentro de la muestra, y SHALL actualizar `08-discusion.tex` (parrafo de procedencia de
los datos de ajuste) y `subsec:corpus-independiente` en consecuencia. Si no existe
`predicciones_independiente.json`, la tesis SHALL declarar "sin corpus independiente
declarado" y que las metricas permanecen como estimaciones dentro de la muestra. La
procedencia de los ajustes y la calificacion dentro de la muestra de los 200 casos se
rigen por el requisito "Procedencia declarada de los ajustes realizados sobre el corpus
de validacion"; este requisito solo agrega el resultado fuera de muestra.

#### Scenario: Validacion fuera de muestra reportada

- **WHEN** existe `predicciones_independiente.json` y se lee `subsec:resultados-campana-medicion`
- **THEN** se reportan las metricas por etapa sobre el corpus independiente con su `n` y sus intervalos, junto a las estimaciones dentro de la muestra
- **AND** `subsec:corpus-independiente` se retitula como replicacion sobre corpus adicionales y remite a resultados

#### Scenario: Sin corpus independiente declarado

- **WHEN** no existe `predicciones_independiente.json`
- **THEN** la tesis declara "sin corpus independiente declarado" en resultados, discusion y memo
- **AND** `subsec:corpus-independiente` conserva la recomendacion de construir ese corpus

### Requirement: Cierre de los items (a) a (e) del dictamen v1.2.5 con propagacion verificable

Al aplicar este change, cada item (a) exactitud del brazo manual, (b) intervencion
humana real, (c) efecto de orden, (d) validacion fuera de muestra y (e) IC del kappa
SHALL quedar en uno de sus dos estados (positivo o negativo declarado) en el resumen,
la introduccion, el marco metodologico, los resultados, la discusion, las conclusiones,
las recomendaciones y el memo, con el mismo estado en todos ellos. Tras la propagacion,
la busqueda de "no medid", "no contrastad", "no estimable" y "no computable" en
`sections/*.tex` SHALL devolver solo los restos legitimos listados en `tasks.md`
(declaraciones sobre la campaña 2026-10, la clase `Bases de Datos`, las hipotesis
subsidiarias, la latencia por etapa, la carga concurrente, la complejidad percibida y
los estados negativos que la campaña de medicion haya dejado).

#### Scenario: Estado unico por item

- **WHEN** se comparan los pasajes que tratan cada item (a)-(e) en las secciones enumeradas y en el memo
- **THEN** cada item declara el mismo estado en todos los pasajes
- **AND** ningun pasaje conserva el estado previo a la campaña de medicion si esta lo supero

#### Scenario: Restos legitimos

- **WHEN** se ejecuta la busqueda de las cuatro frases sobre `sections/*.tex` despues de aplicar el change
- **THEN** cada coincidencia figura en la lista de restos legitimos de `tasks.md` o corresponde a un estado negativo declarado por la campaña de medicion
- **AND** no queda ninguna coincidencia sin clasificar
