# evaluation-framework Specification

## Purpose
TBD - created by archiving change c-08-evaluation-framework. Update Purpose after archive.

## Requirements

### Requirement: Contrato y carga del corpus de evaluación

El framework SHALL definir un esquema explícito para el corpus de evaluación y cargarlo desde un archivo JSON. El esquema SHALL incluir, como mínimo, el `id` (identificador del caso), la `descripcion` (texto pseudonimizado del incidente), `sector_asignado` (etiqueta principal de verdad fundamental) y `sectores_adicionales` (arreglo de etiquetas adicionales, requerido). El sector asignado y cada sector adicional MUST pertenecer al conjunto exacto, sensible a mayúsculas y sin tildes, `{"Seguridad Informatica", "Soporte Tecnico Hardware", "Soporte Tecnico Software", "Bases de Datos", "Sistemas"}`. La carga MUST fallar con un error claro y accionable cuando el archivo no exista, falte un campo requerido, se viole una invariante multietiqueta, o un sector sea inválido; nunca SHALL continuar con datos malformados de forma silenciosa.

#### Scenario: Carga de un corpus válido

- **WHEN** se carga un JSON con `id`, `descripcion`, `sector_asignado` y `sectores_adicionales` y todos los sectores pertenecen al conjunto exacto
- **THEN** el framework devuelve la colección de casos con la misma cantidad de casos que el documento, preservando id, descripción y el conjunto de verdad de cada uno

#### Scenario: Archivo de corpus inexistente

- **WHEN** se solicita cargar el corpus desde una ruta que no existe
- **THEN** el framework lanza un error explícito que nombra la ruta faltante, sin producir una colección vacía silenciosa

#### Scenario: Columna requerida ausente

- **WHEN** se carga un corpus al que le falta `id`, `descripcion`, `sector_asignado` o `sectores_adicionales`
- **THEN** el framework lanza un error que identifica el campo faltante y el caso afectado

#### Scenario: Categoría fuera del conjunto válido

- **WHEN** un caso trae un sector que no pertenece al conjunto exacto (por ejemplo `"sistemas"` en minúscula, `"Operaciones"` o un valor con tilde)
- **THEN** el framework lanza un error que identifica el valor inválido y el caso afectado

### Requirement: Matriz de confusión

El framework SHALL calcular una matriz de confusión primaria 5x5 a partir de los sectores principales reales (`sector_asignado`) y predichos (`sector_predicho`), sobre el conjunto fijo y ordenado de las cinco clases canónicas. La celda `(real, predicho)` MUST contener la cantidad de casos cuyo sector asignado es la fila y cuyo sector predicho principal es la columna. El cálculo SHALL ser una función pura, sin I/O ni dependencias de red.

#### Scenario: Clasificación perfecta produce matriz diagonal

- **WHEN** los sectores predichos principales coinciden con los asignados en todos los casos
- **THEN** la matriz de confusión tiene todos los conteos sobre la diagonal y cero fuera de ella

#### Scenario: Errores se ubican fuera de la diagonal

- **WHEN** un caso con `sector_asignado = "Bases de Datos"` se predice con `sector_predicho = "Sistemas"`
- **THEN** la celda `(Bases de Datos, Sistemas)` se incrementa en uno y la celda diagonal `(Bases de Datos, Bases de Datos)` no cuenta ese caso

### Requirement: Métricas por clase y promedio macro

El framework SHALL calcular, por cada uno de los cinco sectores, la precisión, la sensibilidad (recall), la medida F1 y el soporte (support) en esquema one-vs-rest, y además los promedios micro y macro de F1. La precisión, la sensibilidad y el F1 MUST definirse de forma robusta ante denominador cero, devolviendo 0.0 en lugar de propagar una división por cero. El cálculo SHALL ser una función pura.

#### Scenario: F1 de una clase a partir de precisión y sensibilidad

- **WHEN** un sector tiene precisión y sensibilidad bien definidas y no nulas
- **THEN** su F1 es la media armónica `2 * P * R / (P + R)`

#### Scenario: Promedio macro pondera las clases por igual

- **WHEN** se calcula el F1 macro sobre los cinco sectores
- **THEN** el resultado es la media aritmética de los cinco F1 por sector, independiente de cuántos casos tenga cada sector

#### Scenario: Promedio micro agrega los aportes globales

- **WHEN** se calcula el F1 micro sobre las etiquetas de todos los casos
- **THEN** el resultado se computa sobre los verdaderos positivos, falsos positivos y falsos negativos acumulados de todas las etiquetas

#### Scenario: Clase sin predicciones no rompe el cálculo

- **WHEN** ninguna predicción cae en un sector determinado (denominador de precisión cero)
- **THEN** la precisión de ese sector es 0.0 y el cálculo continúa sin lanzar excepción

### Requirement: Exactitud global e intervalo de confianza de Wilson

El framework SHALL calcular, sobre la definición de acierto primaria (igualdad estricta entre `sector_asignado` y `sector_predicho`), la exactitud primaria como la proporción de aciertos sobre el total. Además SHALL calcular el subconjunto exacto y la pérdida de Hamming conforme a la evaluación multietiqueta. El framework SHALL estimar el intervalo de confianza al 95% mediante el método de Wilson sobre DOS definiciones de acierto: (a) igualdad estricta del sector principal, y (b) pertenencia, es decir `sector_asignado` contenido en el conjunto predicho (`sector_predicho` más `sectores_adicionales`). El cálculo SHALL ser una función pura.

#### Scenario: Exactitud como proporción de aciertos

- **WHEN** se clasifican N casos y K tienen `sector_predicho` igual a `sector_asignado`
- **THEN** la exactitud primaria es `K / N`

#### Scenario: Intervalo de Wilson contiene la proporción puntual

- **WHEN** se calcula el intervalo de Wilson al 95% para la proporción de aciertos de cada definición
- **THEN** el intervalo está acotado en `[0, 1]`, su límite inferior no supera a la proporción puntual y su límite superior no es inferior a ella

#### Scenario: Acierto por pertenencia es más laxo que el estricto

- **WHEN** `sector_asignado` no coincide con `sector_predicho` pero sí aparece en `sectores_adicionales`
- **THEN** la definición de acierto por pertenencia cuenta el caso como acierto y la definición estricta no

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

### Requirement: Métricas de conjunto para evaluación multietiqueta

El framework SHALL calcular métricas que evalúen el conjunto completo de etiquetas de cada caso: exactitud de subconjunto (subset accuracy, coincidencia exacta del conjunto predicho con el conjunto de verdad), pérdida de Hamming (proporción de etiquetas mal clasificadas sobre el total de etiquetas) y, opcionalmente, similitud de Jaccard (intersección sobre unión entre conjunto de verdad y conjunto predicho). El conjunto predicho de un caso SHALL ser `sectores_adicionales` unido con `sector_predicho`, y el conjunto de verdad SHALL ser `sectores_adicionales` de verdad unido con `sector_asignado`. El cálculo SHALL ser una función pura.

#### Scenario: Subconjunto exacto en coincidencia perfecta

- **WHEN** el conjunto predicho de un caso es igual a su conjunto de verdad
- **THEN** el caso cuenta como acierto de subconjunto exacto

#### Scenario: Pérdida de Hamming cuenta etiquetas erróneas

- **WHEN** un caso tiene etiquetas de verdad y predichas parcialmente solapadas
- **THEN** la pérdida de Hamming es la proporción de etiquetas del universo del caso que no coinciden, en el rango `[0, 1]`

#### Scenario: Jaccard entre conjuntos

- **WHEN** se comparan el conjunto de verdad y el predicho de un caso
- **THEN** la similitud de Jaccard es `|intersección| / |unión|` y vale 1.0 cuando coinciden y 0.0 cuando son disjuntos

### Requirement: Provenance de los datos de calibracion (anti data leakage)

El sistema SHALL separar estrictamente los datos usados para ajustar o calibrar el score de seleccion del cortocircuito de los datos usados para reportar metricas. El corpus de evaluacion (`data/corpus_evaluacion_pseudonimizado.json`) SHALL considerarse el conjunto de test reportado y MUST NOT usarse para derivar, ajustar o seleccionar el score ni el punto de operacion. La estrategia de procedencia SHALL adoptar una de las siguientes y documentarla con su tradeoff: (i) un conjunto held-out etiquetado nuevo, (ii) un split dev/test pre-registrado del corpus, reportando sobre la particion de test intocada, o (iii) cross-fitting/conformal, donde la calibracion se ajusta en folds que excluyen el fold evaluado y se reporta out-of-fold. El sistema SHALL hacer verificable que la entrada del ajuste no es el test reportado, de modo que las metricas reportadas no queden invalidadas por fuga.

#### Scenario: El ajuste no usa el test reportado

- **WHEN** se ajusta el score o se elige el punto de operacion
- **THEN** el corpus de evaluacion usado como test set reportado no participa del ajuste ni de la seleccion

#### Scenario: Las metricas se reportan sobre datos intocados

- **WHEN** se reportan las metricas del cortocircuito calibrado
- **THEN** se calculan sobre una particion que no fue usada para ajustar el score, o sobre predicciones out-of-fold

#### Scenario: La procedencia queda documentada

- **WHEN** se declara la estrategia de calibracion
- **THEN** queda documentada la procedencia de los datos (held-out, split pre-registrado o cross-fitting) junto con su tradeoff

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

### Requirement: Divulgacion de la distribucion de etapas del pipeline (incluida fallback)

La evaluacion SHALL reportar la distribucion de casos por etapa del pipeline como
deterministic 131/200 (65,5 %), Gemini 69/200 (34,5 %) y fallback 0/200, e SHALL
documentar la etapa fallback y el orden deterministic -> Gemini -> fallback. La
documentacion de evaluacion SHALL NOT reportar el reparto stale "~62 % / 38 %".

#### Scenario: Etapas y fallback en el reporte

- **WHEN** se presenta `evaluation/report.md` o la seccion de etapas del pipeline
- **THEN** reporta deterministic 131, Gemini 69 y fallback 0
- **AND** documenta el orden deterministic -> Gemini -> fallback

### Requirement: Trazabilidad del corpus real en la documentacion de evaluacion

La documentacion de evaluacion SHALL declarar que el corpus real reside en
`data/corpus_evaluacion_pseudonimizado.json` (JSON, pseudonimizado y versionado)
y SHALL NOT declarar un corpus en `evaluation/data/` ni un esquema CSV de siete
columnas como ubicacion vigente del corpus.

#### Scenario: evaluacion/data no aloja el corpus

- **WHEN** se leen `evaluation/README.md` y `evaluation/data/README.md`
- **THEN** remiten al corpus real en `data/corpus_evaluacion_pseudonimizado.json`
- **AND** no declaran que el corpus resida en `evaluation/data/` como CSV

### Requirement: Reporte de calibración de la confianza del clasificador

El framework SHALL reportar la calibración de la confianza del clasificador: la
relación entre el valor de `confianza` devuelto por caso y la exactitud estricta
de la predicción. El reporte MUST incluir, como mínimo, la precisión del segmento
de confianza `>= 0,70` y la del segmento `< 0,70`, la cantidad de errores con
confianza `>= 0,90`, y una tabla de calibración por bandas de confianza. El
cálculo SHALL ser una función pura sobre las predicciones ya recolectadas.

#### Scenario: Tabla de calibración por bandas

- **WHEN** el framework procesa las predicciones con `confianza` y `sector_predicho`
- **THEN** produce una tabla de calibración con, al menos, las bandas `[0;0,5)`, `[0,5;0,7)`, `[0,7;0,85)`, `[0,85;0,95)` y `[0,95;1,0]`
- **AND** por cada banda reporta la cantidad de casos y la exactitud observada

#### Scenario: Contingencia alta/baja confianza

- **WHEN** el framework reporta la calibración
- **THEN** informa la precisión del segmento con confianza `>= 0,70` y la del segmento con confianza `< 0,70`
- **AND** informa la cantidad de errores entre las predicciones con confianza `>= 0,90`

#### Scenario: El reporte no altera las métricas primarias

- **WHEN** se agrega el reporte de calibración
- **THEN** las métricas primarias de clasificación (exactitud, F1 macro/micro, matriz 5x5) no cambian de valor
- **AND** la calibración se calcula como salida adicional sobre las mismas predicciones

### Requirement: Veracidad de la descripción del corpus de evaluación

La descripción de metadata del corpus de evaluación (`metadata.descripcion` en `data/corpus_evaluacion_pseudonimizado.json`) SHALL describir fielmente su
contenido medido. Cuando los tiempos automatizados estén medidos end-to-end, la
descripción MUST NOT declararlos pendientes de medición; SHOULD distinguir los
tiempos automatizados (medidos) de los tiempos manuales (de clasificación manual).
La corrección SHALL limitarse a la cadena descriptiva y MUST NOT alterar ningún
valor numérico del corpus.

#### Scenario: Descripción sin cláusulas falsas

- **WHEN** se lee `metadata.descripcion` del corpus de evaluación
- **THEN** no declara los tiempos automatizados como pendientes de medición
- **AND** declara que los 200 tiempos automatizados están medidos end-to-end y que los tiempos manuales son los de clasificación manual

#### Scenario: Corrección sin alterar los datos

- **WHEN** se corrige la descripción de metadata
- **THEN** ningún valor numérico del corpus (tiempos, total de casos) cambia
- **AND** el archivo sigue siendo un JSON válido con los mismos 200 casos

### Requirement: Medición comparable del tiempo automatizado telefónico

El framework SHALL derivar el tiempo automatizado del canal telefónico de forma
comparable con el tiempo manual del mismo canal, incorporando la duración de la
llamada/grabación. La derivación MUST ser
`tiempo_automatizado_s = duracion_segundos + latencia_e2e_ms/1000`, donde
`duracion_segundos` es la duración de la grabación provista por Twilio. El framework
MUST declarar explícitamente que este valor es una COTA INFERIOR de la duración real de
la llamada, porque la grabación está acotada a 45 s (`<Record maxLength="45">`). Los
tiempos automatizados de los canales web y correo MUST NOT modificarse.

#### Scenario: Tiempo telefónico incluye la duración de la llamada

- **WHEN** se deriva el tiempo automatizado de un caso telefónico
- **THEN** el valor es `duracion_segundos + latencia_e2e_ms/1000`
- **AND** se declara que es una cota inferior de la duración real por el tope de 45 s de la grabación

#### Scenario: Web y correo sin cambio

- **WHEN** se deriva el tiempo automatizado de un caso de web o de correo
- **THEN** el valor permanece igual al de la medición end-to-end previa
- **AND** no se suma ninguna duración de llamada

#### Scenario: Duración de grabación ausente

- **WHEN** un caso telefónico no tiene `duracion_segundos`
- **THEN** la derivación maneja el ausente sin romperse ni sumar un valor ficticio
- **AND** el caso queda identificable para su revisión

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
