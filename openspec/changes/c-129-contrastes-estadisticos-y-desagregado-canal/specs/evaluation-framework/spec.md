## ADDED Requirements

### Requirement: Estadisticos descriptivos de tiempos global y por canal

El analisis de tiempos SHALL calcular, mediante funciones puras sin I/O, los estadisticos descriptivos de cada serie de tiempos (cantidad de pares, media, mediana, desvio estandar, minimo y maximo) y la reduccion relativa entre flujos, definida como `1 - media(automatizado) / media(manual)` para la media y `1 - mediana(automatizado) / mediana(manual)` para la mediana. El desvio estandar MUST calcularse con la convencion muestral (divisor `n - 1`) y MUST declararse no aplicable, en lugar de producir un valor, cuando la serie tenga menos de dos pares. La seccion "Tiempos" de `evaluation/report.md` SHALL emitir esos descriptivos para el brazo manual y el automatizado, la reduccion relativa y la cantidad de pares en que el flujo automatizado no fue mas rapido, en una fila global (todos los pares validos) y una fila por cada valor de `canal_origen`, con el mismo orden canonico de canales del desglose existente y con precision decimal fija.

#### Scenario: Descriptivos calculados sobre una serie conocida

- **WHEN** se calculan los descriptivos de la serie `[10, 20, 30, 40]`
- **THEN** se obtiene `n = 4`, media `25`, mediana `25`, minimo `10`, maximo `40` y desvio `12,9099` (divisor `n - 1`)
- **AND** no se usa el divisor `n` (que daria `11,1803`)

#### Scenario: Serie con un solo par declara el desvio no aplicable

- **WHEN** se calculan los descriptivos de una serie de un unico valor
- **THEN** la media, la mediana, el minimo y el maximo se informan
- **AND** el desvio se declara no aplicable sin fabricar un valor

#### Scenario: Reduccion relativa de media y mediana

- **WHEN** se calcula la reduccion relativa para manual `[100, 200, 600]` y automatizado `[20, 60, 70]`
- **THEN** la reduccion relativa de la media es `1 - 50/300 = 0,8333`
- **AND** la reduccion relativa de la mediana es `1 - 60/200 = 0,7000`, y cada una se declara no aplicable si la media o la mediana manual es cero

#### Scenario: Tabla de descriptivos global y por canal en el reporte

- **WHEN** el runner genera la seccion "Tiempos" para un corpus con mas de un canal
- **THEN** el reporte incluye una fila global y una fila por canal con los descriptivos del brazo manual y del automatizado, la reduccion relativa y los pares no mas rapidos
- **AND** las tablas preexistentes de la seccion (normalidad, Wilcoxon global, reduccion y desglose por canal) se conservan con sus cabeceras y filas sin cambios

### Requirement: Contraste direccional y tamano del efecto estandarizado

La prueba de Wilcoxon SHALL devolver, ademas del estadistico `W = min(T+, T-)`, de `T+`, `T-`, del valor p bilateral y del tamano del efecto rank-biserial, el valor p unilateral de la hipotesis direccional `manual > automatizado`, calculado con la variante `alternative="greater"` sobre las diferencias `manual - automatizado` y no por division del p bilateral. El estadistico `W`, el p bilateral y `r` MUST NOT cambiar respecto de su definicion vigente. El analisis SHALL calcular el tamano del efecto estandarizado de muestras pareadas `d_z = media(d) / desvio(d)` (divisor `n - 1`), declarado no aplicable con menos de dos pares o desvio nulo, y el efecto minimo detectable expresado en la misma escala `d_z` mediante la aproximacion normal `(z_{1-alfa/2} + z_{potencia}) / raiz(n * ARE)`, con nivel de significancia, potencia, lateralidad y eficiencia relativa asintotica (ARE) como parametros explicitos. La seccion "Tiempos" SHALL emitir, para el conjunto global y para cada canal, el p bilateral, el p unilateral, `d_z` y el efecto minimo detectable con `alfa = 0,05` bilateral y potencia `0,80`, sin ajuste (`ARE = 1`) y con la cota inferior de eficiencia de la prueba de rangos frente a la `t` pareada (`ARE = 0,864`), declarando esos supuestos en el propio reporte.

#### Scenario: p unilateral exacto en una serie pequena

- **WHEN** se contrastan las diferencias `+10, +20, +30, +40, -50` (rangos 1 a 5, `T+ = 10`, `T- = 5`)
- **THEN** el p bilateral sigue siendo `0,625` y `W = 5`
- **AND** el p unilateral es `10/32 = 0,3125`

#### Scenario: p unilateral en la direccion opuesta

- **WHEN** se contrastan las diferencias `-10, -20, -30, -40, +50` (`T+ = 5`)
- **THEN** el p unilateral es `25/32 = 0,78125`, mayor que `0,5`
- **AND** el p bilateral no cambia respecto de la serie simetrica (`0,625`)

#### Scenario: d_z calculado a mano

- **WHEN** se calcula `d_z` para manual `[3, 5, 7]` y automatizado `[1, 2, 3]` (diferencias `2, 3, 4`)
- **THEN** el resultado es `3,0`
- **AND** para diferencias `1, -1, 2, 0` el resultado es `0,5 / 1,2910 = 0,3873`

#### Scenario: d_z no aplicable

- **WHEN** las diferencias son todas iguales (desvio nulo) o hay menos de dos pares
- **THEN** `d_z` se declara no aplicable
- **AND** no se emite un valor infinito ni una division por cero

#### Scenario: Efecto minimo detectable reproducible

- **WHEN** se calcula el efecto minimo detectable con `alfa = 0,05` bilateral, potencia `0,80` y `n = 200`
- **THEN** el resultado es `0,1981` sin ajuste y `0,2131` con `ARE = 0,864`
- **AND** con `n = 81` el resultado sin ajuste es `0,3113` y en la variante unilateral con `n = 200` es `0,1758`

#### Scenario: Contraste direccional en el reporte

- **WHEN** el runner genera la seccion "Tiempos"
- **THEN** existe una tabla con una fila global y una por canal que informa n, p bilateral, p unilateral, `d_z`, efecto minimo detectable sin ajuste y con `ARE = 0,864`
- **AND** el reporte declara alfa, potencia, lateralidad y ARE usados para el efecto minimo detectable

### Requirement: Escenarios de sensibilidad del redondeo manual y granularidad de la medicion

El analisis de tiempos SHALL calcular, como funcion pura, escenarios de sensibilidad que descuentan una cantidad fija de segundos a cada tiempo manual y SHALL reportar, por escenario, la media manual ajustada, la reduccion relativa de la media, el p bilateral, el p unilateral y el tamano del efecto rank-biserial del contraste de Wilcoxon sobre los pares ajustados. La seccion "Tiempos" SHALL emitir los escenarios de 5 s y 10 s, ademas de la reduccion conservadora de 1 s ya existente, y SHALL emitir la granularidad de `tiempo_manual_s`: la cantidad de valores que son multiplos exactos de 5 s y de 10 s sobre el total de pares validos.

#### Scenario: Escenario de descuento calculado a mano

- **WHEN** se aplica un descuento de 5 s a manual `[30, 40, 50]` con automatizado `[10, 10, 10]`
- **THEN** la media manual ajustada es `35` y la reduccion relativa de la media es `1 - 10/35 = 0,7143`
- **AND** el contraste de Wilcoxon se calcula sobre las diferencias ajustadas `15, 25, 35`

#### Scenario: Granularidad de la medicion manual

- **WHEN** se calcula la granularidad de los tiempos manuales `[10, 15, 20, 23]`
- **THEN** se informan 3 de 4 valores multiplos de 5 s y 2 de 4 multiplos de 10 s
- **AND** la granularidad se emite en la seccion "Tiempos" del reporte

#### Scenario: Escenarios presentes en el reporte

- **WHEN** el runner genera la seccion "Tiempos"
- **THEN** el reporte incluye los escenarios de 5 s y 10 s con media ajustada, reduccion relativa, p bilateral, p unilateral y `r`
- **AND** la fila de reduccion conservadora de 1 s preexistente no cambia

### Requirement: Regeneracion de la seccion de tiempos sin predicciones

El runner SHALL ofrecer un modo de solo tiempos (`python -m evaluation.run_evaluation --solo-tiempos`) que cargue el corpus, calcule la seccion "Tiempos" y reemplace en `evaluation/report.md` unicamente el bloque que comienza en el encabezado `## Tiempos` y termina antes del siguiente encabezado de nivel 2 o del pie del reporte. Ese modo MUST NOT leer ni escribir el cache de predicciones, MUST NOT construir ni invocar el clasificador y MUST NOT requerir la confirmacion de corrida paga. El resto del reporte MUST conservarse byte a byte, incluidas las secciones que otros changes agreguen fuera del bloque de tiempos, y el bloque regenerado MUST ser identico al que produce la corrida completa sobre el mismo corpus. Si `evaluation/report.md` no existe, el modo SHALL terminar con un error claro sin crear un reporte parcial. `evaluation/README.md` SHALL documentar el modo y su caracter no pago.

#### Scenario: Reemplazo del bloque sin tocar la clasificacion

- **WHEN** se ejecuta el modo de solo tiempos sobre un reporte con secciones de clasificacion y un bloque de tiempos desactualizado
- **THEN** el bloque "## Tiempos" queda reemplazado por el recalculado
- **AND** las secciones de clasificacion quedan identicas byte a byte

#### Scenario: Idempotencia frente a la corrida completa

- **WHEN** se genera el reporte completo con un clasificador simulado y luego se ejecuta el modo de solo tiempos con el mismo corpus
- **THEN** el reporte resultante es identico byte a byte al de la corrida completa
- **AND** una segunda ejecucion del modo de solo tiempos no cambia el archivo

#### Scenario: Secciones ajenas posteriores preservadas

- **WHEN** el reporte contiene una seccion de nivel 2 posterior al bloque de tiempos (por ejemplo, agregada por otro change)
- **THEN** el reemplazo termina antes de esa seccion
- **AND** esa seccion se conserva sin cambios

#### Scenario: Sin clasificador, sin cache y sin gate pago

- **WHEN** se ejecuta el modo de solo tiempos sin `GEMINI_API_KEY`, sin `predicciones.json` y sin confirmacion de corrida paga
- **THEN** la ejecucion termina con exito sin construir ni invocar el clasificador
- **AND** no se lee ni se escribe ningun archivo de predicciones

#### Scenario: Reporte ausente

- **WHEN** se ejecuta el modo de solo tiempos y `evaluation/report.md` no existe
- **THEN** el runner termina con un error claro que indica generar primero el reporte completo
- **AND** no se crea un reporte parcial

### Requirement: Huella del corpus independiente del fin de linea

La huella SHA-256 del corpus que el runner emite en la seccion "Tiempos" y usa para validar el cache de predicciones SHALL calcularse sobre el contenido del archivo con los fines de linea normalizados a LF, de modo que una copia con CRLF (por ejemplo, un checkout de Windows con `core.autocrlf=true`) y una copia con LF produzcan la misma huella, igual a la del blob versionado. Una diferencia de contenido distinta del fin de linea MUST producir una huella distinta.

#### Scenario: CRLF y LF producen la misma huella

- **WHEN** se calcula la huella de dos copias del mismo corpus, una con fines de linea CRLF y otra con LF
- **THEN** ambas huellas son iguales
- **AND** coinciden con el SHA-256 del contenido con fines de linea LF

#### Scenario: Cambio de contenido cambia la huella

- **WHEN** se modifica un valor del corpus manteniendo el fin de linea
- **THEN** la huella cambia
- **AND** un cache de predicciones con la huella anterior se considera invalido
