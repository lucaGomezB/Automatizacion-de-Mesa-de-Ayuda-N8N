## MODIFIED Requirements

### Requirement: Intervalos de confianza del kappa y por clase en la tesis

El marco metodologico y el capitulo de resultados SHALL reportar el intervalo de
confianza del coeficiente kappa de doble etiquetado y los intervalos de confianza
de las metricas por clase (precision, sensibilidad, F1), declarando el nivel de
confianza y el procedimiento de estimacion. Una vez recuperada la tabla primaria de
doble etiquetado, la tesis SHALL reportar el IC del kappa junto al valor puntual
`0,87`, calculado por bootstrap con semilla fija, declarando metodo y semilla; ya no
SHALL declarar el IC del kappa como no computable. El documento SHALL declarar como
no estimable la clase con soporte unitario (`Bases de Datos`, `n = 1`) y SHALL
excluirla del macro-F1 de umbral, conservando el macro-F1 de cinco clases como
valor informativo.

#### Scenario: IC del kappa reportado

- **WHEN** se lee el pasaje del doble etiquetado en metodologia o discusion
- **THEN** el kappa `0,87` se acompana de su intervalo de confianza con el nivel y el metodo declarados (bootstrap con semilla fija)
- **AND** el rotulo interpretativo sigue siendo "casi perfecto" (Landis & Koch)

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

La tesis SHALL reportar el intervalo de confianza del coeficiente kappa (`0,87`)
calculandolo por bootstrap con semilla fija sobre la tabla primaria de doble
etiquetado producida por la campana (c-168), declarando el metodo y la semilla. La
decision y el valor computado SHALL quedar registrados en el memo canonico
(`docs/Tesis/Correcciones/numeros-canonicos.md`). Si la tabla primaria no estuviera
disponible, la tesis SHALL conservar la declaracion explicita de no computabilidad,
sin fabricar un intervalo.

#### Scenario: Tabla recuperable

- **WHEN** la tabla de acuerdo observado/esperado o las etiquetas por caso de ambos analistas estan disponibles
- **THEN** la tesis reporta el intervalo de confianza del kappa junto al valor puntual 0,87
- **AND** declara el metodo y la semilla empleados

#### Scenario: Tabla no recuperable

- **WHEN** la tabla primaria de doble etiquetado no esta disponible en las fuentes del repositorio
- **THEN** la tesis declara de forma explicita que el intervalo de confianza del kappa es no computable por ausencia de la tabla primaria
- **AND** no se fabrica ni se estima un intervalo
- **AND** el rotulo interpretativo "casi perfecto" (Landis y Koch) se conserva

### Requirement: Declaracion del estado de la hipótesis principal

El resumen, la discusión y las conclusiones SHALL declarar el estado de la
hipótesis principal como parcialmente confirmada (reducción del tiempo de registro)
y parcialmente refutada (umbral de clasificación: `73,5 %` de exactitud y macro-F1 de
umbral `0,6508` sobre las cuatro clases estimables, por debajo de `85 %` y `0,85`),
y SHALL distinguir las sub-hipótesis de tiempo, intervención humana y exactitud o F1.
Una vez medida la intervención humana, la sub-hipótesis de intervención SHALL
declararse **contrastada** con la tasa de intervención observada y su intervalo de
confianza; el documento MUST NOT conservar la declaración de "no contrastada por
ausencia de registro primario" ni reintroducir el `9,5 %` retirado (c-107). Las
conclusiones SHALL declarar el estado por sub-hipótesis — confirmada en tiempo,
refutada en clasificación y contrastada en intervención humana — junto con el estado
de las dos hipótesis subsidiarias. El resumen MUST NOT permitir inferir una
confirmación plena de la hipótesis.

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
- **THEN** la sub-hipótesis de intervención humana se declara contrastada con la tasa de intervención medida
- **AND** no se reporta el `9,5 %` de intervención humana como resultado vigente
- **AND** no se conserva la declaración de "no contrastada por ausencia de registro primario"

#### Scenario: Estado por sub-hipótesis en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** se distingue explícitamente la sub-hipótesis confirmada (tiempo), la refutada (exactitud/F1) y la contrastada (intervención humana)
- **AND** no se declara la hipótesis principal confirmada o refutada como bloque
- **AND** se declara el estado de las dos hipótesis subsidiarias

### Requirement: Intervención humana por gate declarada no medida

La tesis SHALL reportar la tasa de intervención humana medida por caso durante la
campaña, con su definición rotulada y su intervalo de confianza, en lugar de
declararla no medida. El texto MUST NOT presentar el `9,5 %` retirado (c-107) como
resultado vigente. La afirmación de que el flujo automatizado corrió "sin
intervención humana" SHALL reconciliarse con la definición de las dos dimensiones
rotuladas de la variable y con el registro de intervención de la campaña.

#### Scenario: Cifra retirada ausente

- **WHEN** se busca "9,5 %" o "19 casos" como intervención humana en el PDF compilado
- **THEN** no aparece la cifra del 9,5 % presentada como resultado de intervención
- **AND** la tasa de intervención reportada proviene del registro de la campaña

#### Scenario: Aporte operativo reformulado

- **WHEN** se lee la subsección de reducción de la intervención humana y la discusión
- **THEN** el texto reporta la tasa de intervención medida con su intervalo de confianza y su definición rotulada
- **AND** no conserva la declaración de que la intervención por gate no fue medida

#### Scenario: Coherencia con "sin intervención humana"

- **WHEN** se compara la afirmación del protocolo de pruebas con la subsección de reducción de intervención humana
- **THEN** ambas describen la misma definición rotulada de la variable
- **AND** no se sostiene simultáneamente que hubo 9,5 % de intervención y que el flujo corrió sin intervención humana

### Requirement: Tratamiento honesto del confundido de la rotación de operadores

Cuando el documento declare rotación o contrabalanceo de operadores entre las
mitades del corpus, SHALL declarar cuántos operadores y cuántas mitades
intervinieron y SHALL reconocer explícitamente si la rotación queda confundida con
el efecto del operador. El diseño contrabalanceado de la campaña (c-166) SHALL
reportarse de modo que el efecto de orden sea separable, o SHALL declarar la
limitación residual si no lo es. El documento MUST NOT presentar la rotación como
mitigación no calificada del efecto de aprendizaje.

#### Scenario: Confundido reconocido

- **WHEN** se lee la descripción del contrabalanceo del orden de procesamiento
- **THEN** el texto declara cuántos operadores y cuántas mitades intervinieron
- **AND** reconoce si la rotación de operadores queda confundida con el efecto del operador

#### Scenario: Mitigación no sobrevendida

- **WHEN** se lee la lista de amenazas a la validez y sus mitigaciones
- **THEN** la rotación de operadores no se presenta como mitigación no calificada si está confundida
- **AND** se declara la limitación resultante o el rediseño de la afirmación

### Requirement: Procedencia declarada de los ajustes realizados sobre el corpus de validacion

La tesis SHALL declarar en la discusion (`subsec:interpretacion-resultados`) que el
vocabulario del filtro deterministico (c-71), las reglas de frontera del prompt
(c-72) y el punto de operacion del cortocircuito (c-74) se derivaron de casos y
errores observados en el corpus de validacion de 200 casos; SHALL acotar que la
mitigacion fuera de muestra de c-74 (validacion cruzada de cinco pliegues para el
punto de operacion) NO cubre la ampliacion del vocabulario ni las reglas del prompt;
SHALL declarar el resultado de la validacion fuera de muestra sobre el corpus
independiente de la campana (c-166) si este se dispuso, o, en su defecto, que no se
dispuso de un corpus independiente de preproduccion; y SHALL calificar las metricas
de clasificacion como estimaciones dentro de la muestra cuando no se haya validado
fuera de muestra. Las demas secciones que afirman la ausencia de exposicion al
corpus (`05-arquitectura.tex`, `06-implementacion.tex`, Anexo H) SHALL alinearse con
esa declaracion o remitir a ella. La tesis MUST NOT afirmar separacion estricta entre
datos de construccion y de validacion ni desempeno sobre datos no vistos que la
evidencia no sustente; MUST NOT afirmar la existencia de un conjunto de
aproximadamente 100 incidentes de preproduccion ni remitir a
`docs/prompt_gemini_history/`; y MUST NOT alterar ningun valor numerico por esta
declaracion.

#### Scenario: Procedencia de los tres ajustes declarada

- **WHEN** se lee `subsec:interpretacion-resultados` en el PDF compilado
- **THEN** se declaran los ajustes del vocabulario del filtro deterministico, de las reglas de frontera del prompt y del punto de operacion realizados sobre el corpus de validacion
- **AND** las metricas de clasificacion se califican como estimaciones dentro de la muestra o como validadas fuera de muestra segun la evidencia

#### Scenario: Mitigacion fuera de muestra acotada

- **WHEN** se lee la declaracion de procedencia
- **THEN** la mitigacion fuera de muestra de c-74 se acota al punto de operacion
- **AND** se declara expresamente que esa mitigacion no cubre el vocabulario ni las reglas del prompt

#### Scenario: Sin corpus independiente de preproduccion

- **WHEN** se busca en `sections/*.tex` una afirmacion sobre un corpus independiente de incidentes de preproduccion
- **THEN** se declara si se dispuso de un corpus independiente de la campana y su resultado, o que no se dispuso de un corpus de esas caracteristicas
- **AND** no se afirma la existencia de un conjunto de aproximadamente 100 incidentes de preproduccion

#### Scenario: Sin afirmacion de no exposicion

- **WHEN** se buscan en `sections/*.tex` las afirmaciones "sin exposicion a" (el corpus o los 200 casos de validacion), "sin acceso al corpus", "datos no vistos" y "separacion estricta"
- **THEN** ninguna aparece como afirmacion vigente sobre la version evaluada

#### Scenario: Numeros intactos

- **WHEN** se comparan las metricas de clasificacion del PDF antes y despues de la declaracion
- **THEN** no cambia ningun valor numerico

### Requirement: Priorización de las líneas de trabajo futuro sobre los defectos medidos

El capítulo de recomendaciones (`10-recomendaciones.tex`) SHALL priorizar
explícitamente las líneas de trabajo futuro que atacan los defectos medidos en el
estudio. Una vez medida la intervención humana, la corrección de su medición deja de
figurar entre las líneas futuras y SHALL permanecer priorizada la calibración del
gate de confianza y la incorporación de un clasificador supervisado con corpus
propio. La priorización SHALL distinguir esas líneas de las extensiones genéricas
(canales adicionales, paneles, base de conocimientos) y SHALL ser coherente con las
limitaciones reconocidas en la discusión.

#### Scenario: Líneas prioritarias declaradas

- **WHEN** se lee la introducción o el cierre del capítulo de recomendaciones
- **THEN** el texto declara explícitamente cuáles líneas futuras son prioritarias
- **AND** entre ellas figuran la calibración del gate y el clasificador supervisado, sin la corrección de la medición de intervención ya saldada

#### Scenario: Distinción respecto de las líneas genéricas

- **WHEN** se leen las líneas de canales adicionales, paneles o base de conocimientos
- **THEN** se presentan como extensiones no prioritarias o subordinadas a las líneas que atacan los defectos medidos
- **AND** la priorización es coherente con las limitaciones de la discusión

## REMOVED Requirements

### Requirement: Rotulo de la sub-hipotesis de intervencion humana como no contrastada

**Reason**: La sub-hipotesis de intervencion humana deja de ser "no contrastada por
ausencia de registro primario" una vez que la campana mide la tasa de intervencion por
caso; el rotulo y el retitulado que este requisito imponia quedan superados.

**Migration**: La declaracion del estado de la sub-hipotesis se rige por el requisito
"No contrastada por ausencia de registro primario" reemplazado en este mismo change
(ver "Declaracion del estado de la hipótesis principal" y "Intervención humana por
gate declarada no medida"): la sub-hipotesis se declara contrastada con la tasa
medida, y el titulo de la subseccion de resultados pasa a reflejar el resultado
medido en lugar de evitar prometer una reduccion no entregada.

## ADDED Requirements

### Requirement: Reporte de la exactitud del brazo manual con su intervalo de confianza

La tesis SHALL reportar la exactitud del brazo manual (el etiquetado humano de
referencia) medida por la campana (c-165), con su tamano muestral y su intervalo de
confianza de Wilson, en el marco metodologico (4.7) y en el capitulo de resultados
(8.x). El documento MUST NOT presentar la exactitud manual como un supuesto no
medido.

#### Scenario: Exactitud manual reportada con IC

- **WHEN** se lee la subseccion de resultados sobre el brazo manual
- **THEN** se reporta la exactitud del etiquetado humano con su `n` y su intervalo de confianza
- **AND** se declara el instrumento y el procedimiento de medicion empleados

#### Scenario: Sin supuesto no medido

- **WHEN** se busca en la tesis una declaracion de que la exactitud del brazo manual no fue medida
- **THEN** no subsiste ninguna afirmacion de ese tipo respecto de la version evaluada

### Requirement: Reporte de la tasa de intervencion humana medida por caso

La tesis SHALL reportar la tasa de intervencion humana medida por caso durante la
campana, con su definicion rotulada, su tamano muestral y su intervalo de confianza,
en el marco metodologico (4.7) y en el capitulo de resultados. El documento MUST NOT
reportar el `9,5 %` retirado (c-107) ni declarar la intervencion como no medida.

#### Scenario: Tasa de intervencion reportada

- **WHEN** se lee la subseccion de reduccion de la intervencion humana
- **THEN** se reporta la tasa de intervencion medida con su `n`, su definicion rotulada y su intervalo de confianza
- **AND** la cifra proviene del registro de intervencion de la campana

#### Scenario: Cifra retirada ausente

- **WHEN** se busca "9,5 %" o "19 casos" como intervencion humana en el PDF compilado
- **THEN** no aparece la cifra del 9,5 % presentada como resultado vigente

### Requirement: Reporte del efecto de orden del contrabalanceo

La tesis SHALL reportar el analisis del efecto de orden derivado del diseno
contrabalanceado (c-166) en el marco metodologico (4.8) y en el capitulo de
resultados, declarando el estadistico empleado y su resultado, o bien la limitacion
residual si el efecto no fuera separable.

#### Scenario: Efecto de orden reportado

- **WHEN** se lee la subseccion de resultados sobre el orden de procesamiento
- **THEN** se reporta el analisis del efecto de orden con el estadistico y el resultado obtenidos
- **AND** se declara la coherencia con el diseno contrabalanceado descrito en metodologia

#### Scenario: Limitacion residual declarada

- **WHEN** el efecto de orden no es separable del efecto de operador
- **THEN** la tesis declara la limitacion residual en lugar de sobrevender el contrabalanceo

### Requirement: Reporte de la validacion fuera de muestra

La tesis SHALL reportar el resultado de la validacion fuera de muestra sobre el
corpus independiente de la campana (c-166) en el capitulo de resultados, comparando
las metricas de clasificacion fuera de muestra con las estimaciones dentro de la
muestra, o bien declarando que no se dispuso de corpus independiente y que las
metricas permanecen dentro de la muestra.

#### Scenario: Validacion fuera de muestra reportada

- **WHEN** se lee la subseccion de resultados sobre la validacion fuera de muestra
- **THEN** se reportan las metricas sobre el corpus independiente con su `n` y su intervalo de confianza
- **AND** se contrastan con las estimaciones dentro de la muestra

#### Scenario: Sin corpus independiente declarado

- **WHEN** no se dispuso de un corpus independiente
- **THEN** la tesis declara que las metricas de clasificacion permanecen como estimaciones dentro de la muestra
- **AND** no afirma desempeno sobre datos no vistos
