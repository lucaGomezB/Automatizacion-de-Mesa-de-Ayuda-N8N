## MODIFIED Requirements

### Requirement: Análisis estadístico de tiempos

El framework SHALL aplicar la prueba de Wilcoxon de rangos con signo sobre los pares (tiempo_manual, tiempo_automatizado) para contrastar la igualdad de medianas entre ambos flujos, y SHALL reportar el tamaño del efecto rank-biserial asociado, conforme a §4.7 y §7.1 de la tesis. El framework MUST declarar explícitamente la convención del estadístico de Wilcoxon empleado y MUST reportar ambos estadísticos de rango, `T+` (suma de rangos positivos) y `T−` (suma de rangos negativos), además del valor p. El tamaño del efecto MUST calcularse con la fórmula rank-biserial `r = (T+ − T−) / (n(n+1)/2)`, equivalente a `1 − 4W/(n(n+1))` cuando `W = T− = min(T+, T−)`; MUST NOT usarse `r = 1 − 2W/(n(n+1))`. El cálculo SHALL ser una función pura que recibe las dos series pareadas y devuelve, como mínimo, el estadístico de contraste, `T+`, `T−`, el valor p y el tamaño del efecto. Además, el framework SHALL contrastar la normalidad de cada serie sobre los pares pareados (tiempos manuales, tiempos automatizados y diferencias) mediante la prueba de Shapiro-Wilk, como función pura que devuelve el estadístico `W`, el valor `p` y el número de pares; el contraste de normalidad SHALL declararse no aplicable, en lugar de producir un valor, cuando la serie no alcance el mínimo de pares que exige la prueba.

#### Scenario: Diferencia sistemática produce p significativo

- **WHEN** el flujo automatizado es consistentemente más rápido que el manual en la mayoría de los pares
- **THEN** la prueba devuelve un valor p por debajo del nivel de significancia 0.05 y un tamaño del efecto de magnitud alta

#### Scenario: Series de distinta longitud son rechazadas

- **WHEN** se invoca la prueba con dos series de cantidad de elementos distinta
- **THEN** el framework lanza un error en lugar de producir un resultado inválido

#### Scenario: Convención de W y ambos estadísticos reportados

- **WHEN** el framework devuelve el resultado de la prueba de Wilcoxon
- **THEN** informa explícitamente la convención de `W` adoptada
- **AND** reporta `T+` y `T−` de forma diferenciada

#### Scenario: Fórmula rank-biserial correcta y rango verdadero

- **WHEN** se calcula el tamaño del efecto sobre los pares reales
- **THEN** el resultado es `(T+ − T−) / (n(n+1)/2)` (por ejemplo `0,9639` para `T+=19737`, `T−=363`, `n=200`)
- **AND** no se reporta el valor espurio `1,00` ni se documenta un rango `[-1,+1]` para `1 − 2W/(n(n+1))`

#### Scenario: Código y tesis usan la misma fórmula

- **WHEN** se compara la implementación del framework con la fórmula declarada en la tesis
- **THEN** ambas emplean la misma definición `r = (T+ − T−) / (n(n+1)/2)` (o su equivalente `1 − 4W/(n(n+1))`)
- **AND** no se emplea una aproximación distinta basada en el conteo de pares concordantes y discordantes sin ponderar por rango

#### Scenario: Normalidad de Shapiro-Wilk reportada por serie

- **WHEN** el framework contrasta la normalidad de las series pareadas sobre los pares del corpus
- **THEN** devuelve, por cada serie (manual, automatizado y diferencias), el estadístico `W`, el valor `p` y el número de pares
- **AND** aplica la prueba como función pura, sin I/O ni dependencia del corpus en disco

### Requirement: Runner de evaluación sobre el corpus

El framework SHALL proveer un runner que, dado un corpus, invoque el clasificador híbrido caso por caso recolectando para cada uno el sector predicho principal, los sectores adicionales predichos, la confianza y la etapa del pipeline (`deterministic`, `gemini` o `fallback`), y produzca las métricas de clasificación multietiqueta y un reporte en `evaluation/report.md`. El runner MUST ser ejecutable como una operación de un solo comando cuando el corpus real esté presente en `data/corpus_evaluacion_pseudonimizado.json`, y MUST aislar la recolección de predicciones del cálculo de métricas (inyección del clasificador) para permitir pruebas con un clasificador simulado. El runner MUST negarse a invocar el clasificador real sin confirmación explícita del operador, abortando con un error claro cuando la confirmación está ausente. La documentación del runner (`evaluation/README.md`) MUST describir ese gate de corrida paga junto al comando único de corrida y a la configuración de `GEMINI_API_KEY`: MUST nombrar las dos formas de confirmación (`--confirm-paid` y `EVALUATION_CONFIRM_PAID=1`), MUST indicar que sin confirmación la corrida aborta sin invocar el clasificador real, y MUST indicar que al confirmar se imprime una estimación de costo. Además, el runner SHALL emitir en `evaluation/report.md` una sección "Tiempos" ADITIVA, derivada de los campos `tiempo_manual_s` y `tiempo_automatizado_s` del corpus cargado, que SHALL incluir el contraste de normalidad, la prueba de Wilcoxon con el estadístico de contraste, `T+`, `T−`, el valor `p` y el tamaño del efecto rank-biserial, y el desglose por canal. La generación del reporte SHALL ser determinista y reproducible: regenerar el reporte MUST NOT perder la sección de tiempos ni degradar o alterar las métricas de clasificación.

#### Scenario: Recolección de predicciones por caso

- **WHEN** el runner procesa un corpus con un clasificador inyectado
- **THEN** por cada caso del corpus se registra exactamente una predicción con sector predicho, sectores adicionales, confianza y etapa

#### Scenario: Generación del reporte de métricas

- **WHEN** el runner finaliza el procesamiento de un corpus
- **THEN** escribe `evaluation/report.md` con la matriz de confusión 5x5, la exactitud primaria, el subconjunto exacto, la pérdida de Hamming, los F1 micro y macro y la tabla por sector

#### Scenario: Corpus real ausente no rompe el framework

- **WHEN** se ejecuta el runner y el archivo `data/corpus_evaluacion_pseudonimizado.json` no está presente
- **THEN** el runner termina con un error claro indicando que debe colocarse el corpus real, sin inventar datos ni producir un reporte con resultados ficticios

#### Scenario: Gate de corrida paga documentado junto al comando

- **WHEN** se lee la documentación del runner en `evaluation/README.md`
- **THEN** el gate de corrida paga se describe junto al comando único de corrida y a la configuración de `GEMINI_API_KEY`
- **AND** nombra `--confirm-paid` y `EVALUATION_CONFIRM_PAID=1` como las formas de confirmación
- **AND** indica que sin confirmación la corrida aborta sin invocar el clasificador real y que al confirmar se imprime una estimación de costo

#### Scenario: Sección de tiempos generada por el runner

- **WHEN** el runner finaliza el procesamiento de un corpus con tiempos cargados
- **THEN** `evaluation/report.md` incluye una sección "Tiempos" con la normalidad, el estadístico de contraste `W`, `T+`, `T−`, el valor `p` y el tamaño del efecto rank-biserial
- **AND** la sección se calcula a partir de los campos de tiempo del corpus, no se agrega a mano

#### Scenario: Regeneración reproducible conserva la sección de tiempos

- **WHEN** se regenera `evaluation/report.md` volviendo a correr el runner
- **THEN** la sección "Tiempos" (incluida la normalidad) sigue presente y sus valores son idénticos a los de la corrida anterior
- **AND** no se pierde ningún contenido estadístico que antes se editaba manualmente

#### Scenario: El reporte de tiempos no altera las métricas de clasificación

- **WHEN** se agrega la sección "Tiempos" al reporte
- **THEN** las métricas de clasificación (exactitud, matriz 5x5, F1 macro/micro, subset accuracy y Hamming loss) no cambian de valor
- **AND** la sección de tiempos se calcula como salida adicional sobre el mismo corpus ya cargado

### Requirement: Divulgacion del redondeo de la medicion manual y analisis de sensibilidad

La evaluacion de tiempos SHALL declarar la naturaleza de la medicion de
`tiempo_manual_s` (medicion real en vivo con redondeo hacia arriba, sesgo
sistematico) y SHALL reportar, junto a la reduccion calculada sobre los valores
reportados, una cota inferior conservadora de sensibilidad. El analisis de
tiempos SHALL reportar el numero de pares en que el flujo automatizado no fue mas
rapido, y el estadistico de Wilcoxon SHALL usar la correccion por empates en
lugar de asumir ausencia de pares invertidos. Estas divulgaciones SHALL emitirse
en la seccion de tiempos de `evaluation/report.md` generada por el runner, de
modo que la evidencia sea reproducible end-to-end y no dependa de que la tesis
las agregue a mano.

#### Scenario: Redondeo y sensibilidad declarados en el reporte

- **WHEN** se lee la seccion de tiempos de `evaluation/report.md`
- **THEN** se declara que `tiempo_manual_s` es una medicion redondeada al alza
- **AND** se reporta la reduccion conservadora ademas de la reduccion sobre los valores reportados

#### Scenario: Pares invertidos visibles

- **WHEN** se comparan los tiempos pareados manual y automatizado
- **THEN** se reporta la cantidad de pares en que el flujo automatizado no fue mas rapido (12 de 200)
- **AND** el estadistico de Wilcoxon reportado no asume cero pares invertidos

## ADDED Requirements

### Requirement: Segmentación por canal del análisis de tiempos

El análisis de tiempos del runner SHALL segmentar por el valor de `canal_origen` presente en el corpus y reportar, por cada canal, la cantidad de pares válidos y el resultado de la prueba de Wilcoxon (estadístico de contraste, `T+`, `T−`, valor `p` y tamaño del efecto rank-biserial). Un par SHALL considerarse válido solo cuando ambos tiempos (`tiempo_manual_s` y `tiempo_automatizado_s`) son numéricos. Cuando un canal no alcance el mínimo de pares que exige la prueba, el reporte SHALL declarar explícitamente que la prueba no es aplicable para ese canal, reportando únicamente la cantidad de pares, en lugar de fabricar un resultado. La segmentación SHALL preservar la comparabilidad por canal documentada en `docs/medicion-latencia-e2e.md` (los puntos de ingreso no son homogéneos); el resultado global SHALL acompañarse del desglose por canal y MUST NOT sustituirlo.

#### Scenario: Desglose por canal presente en el reporte

- **WHEN** el corpus contiene casos de más de un canal, cada uno con al menos dos pares válidos
- **THEN** la sección de tiempos reporta, por cada canal, la cantidad de pares y el resultado de Wilcoxon (estadístico, `T+`, `T−`, `p` y tamaño del efecto)
- **AND** el resultado global de tiempos sigue presente junto al desglose

#### Scenario: Canal con pares insuficientes declara no aplicable

- **WHEN** un canal tiene menos pares válidos que el mínimo que exige la prueba de Wilcoxon
- **THEN** la sección de tiempos declara que la prueba no es aplicable para ese canal
- **AND** reporta la cantidad de pares observados sin fabricar un estadístico ni un valor p

#### Scenario: Pares con tiempo ausente se excluyen del canal

- **WHEN** un caso tiene `tiempo_manual_s` o `tiempo_automatizado_s` no numérico (nulo)
- **THEN** ese caso no entra en la serie pareada de su canal
- **AND** su exclusión no impide el análisis de los casos válidos del mismo canal