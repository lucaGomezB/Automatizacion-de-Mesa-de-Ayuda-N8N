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

El framework SHALL calcular, sobre la definicion de acierto primaria (igualdad estricta entre `sector_asignado` y `sector_predicho`), la exactitud primaria como la proporcion de aciertos sobre el total. Ademas SHALL calcular el subconjunto exacto y la perdida de Hamming conforme a la evaluacion multietiqueta. El framework SHALL estimar el intervalo de confianza al 95% mediante el metodo de Wilson sobre TRES definiciones de acierto: (a) igualdad estricta del sector principal; (b) pertenencia, es decir `sector_asignado` contenido en el conjunto predicho (`sector_predicho` mas `sectores_adicionales` predichos); y (c) acierto laxo, es decir `sector_predicho` contenido en el conjunto de verdad del caso (`sector_asignado` mas `sectores_adicionales` de verdad del corpus). El reporte SHALL rotular cada definicion con su enunciado explicito, de modo que la pertenencia no se confunda con la exactitud laxa. Un `sector_predicho` ausente, vacio o no canonico SHALL contar como error en las tres definiciones. El calculo SHALL ser una funcion pura.

#### Scenario: Exactitud como proporción de aciertos

- **WHEN** se clasifican N casos y K tienen `sector_predicho` igual a `sector_asignado`
- **THEN** la exactitud primaria es `K / N`

#### Scenario: Intervalo de Wilson contiene la proporción puntual

- **WHEN** se calcula el intervalo de Wilson al 95% para la proporcion de aciertos de cada una de las tres definiciones
- **THEN** el intervalo esta acotado en `[0, 1]`, su limite inferior no supera a la proporcion puntual y su limite superior no es inferior a ella

#### Scenario: Acierto por pertenencia es más laxo que el estricto

- **WHEN** `sector_asignado` no coincide con `sector_predicho` pero si aparece en `sectores_adicionales` predichos
- **THEN** la definicion de acierto por pertenencia cuenta el caso como acierto y la definicion estricta no

#### Scenario: Acierto laxo cuenta la prediccion principal dentro del conjunto de verdad

- **WHEN** `sector_predicho` no coincide con `sector_asignado` pero pertenece a los `sectores_adicionales` de verdad del caso en el corpus
- **THEN** la definicion laxa cuenta el caso como acierto y la definicion estricta no

#### Scenario: La exactitud laxa nunca es menor que la estricta

- **WHEN** se calculan los aciertos estrictos y laxos sobre las mismas predicciones y el mismo corpus
- **THEN** todo acierto estricto es tambien acierto laxo
- **AND** la cantidad de aciertos laxos es mayor o igual que la de aciertos estrictos

#### Scenario: Pertenencia y exactitud laxa se distinguen

- **WHEN** el `sector_predicho` de un caso no pertenece a su conjunto de verdad pero `sector_asignado` figura entre los `sectores_adicionales` predichos
- **THEN** el caso es acierto por pertenencia y no es acierto laxo
- **AND** el reporte enuncia por separado la definicion de cada metrica

#### Scenario: Prediccion ausente es error en las tres definiciones

- **WHEN** el `sector_predicho` de un caso es vacio o no pertenece a los cinco sectores canonicos
- **THEN** el caso no cuenta como acierto estricto, de pertenencia ni laxo

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

El framework SHALL reportar la calibracion de la confianza del clasificador: la relacion entre el valor de `confianza` devuelto por caso y la exactitud estricta de la prediccion. El reporte SHALL emitirlo el runner dentro de `evaluation/report.md` (MUST NOT agregarse a mano) e MUST incluir, como minimo, la precision del segmento de confianza `>= 0,70` y la del segmento `< 0,70`, la cantidad de casos y de errores con confianza `>= 0,90`, y una tabla de calibracion por bandas de confianza. Cada uno de esos elementos MUST reportarse en forma global y desagregado por etapa del pipeline (`deterministic`, `gemini`, `fallback`), porque las etapas emiten magnitudes de confianza de naturaleza distinta y la agregacion confunde la comparacion entre bandas con una comparacion entre etapas. Por etapa, el reporte SHALL incluir ademas la distribucion de los valores de confianza observados (casos y aciertos por valor) y el IC de Wilson al 95% de la exactitud de cada banda no vacia. El calculo SHALL ser una funcion pura sobre las predicciones ya recolectadas.

#### Scenario: Tabla de calibración por bandas

- **WHEN** el framework procesa las predicciones con `confianza` y `sector_predicho`
- **THEN** produce una tabla de calibracion global con, al menos, las bandas `[0;0,5)`, `[0,5;0,7)`, `[0,7;0,85)`, `[0,85;0,95)` y `[0,95;1,0]`
- **AND** por cada banda reporta la cantidad de casos y la exactitud observada

#### Scenario: Contingencia alta/baja confianza

- **WHEN** el framework reporta la calibracion
- **THEN** informa la precision del segmento con confianza `>= 0,70` y la del segmento con confianza `< 0,70`, en forma global y por etapa
- **AND** informa la cantidad de casos y de errores entre las predicciones con confianza `>= 0,90`, en forma global y por etapa

#### Scenario: Calibracion desagregada por etapa

- **WHEN** las predicciones provienen de mas de una etapa del pipeline
- **THEN** el reporte incluye, para cada etapa, la tabla de bandas con casos, aciertos, exactitud e IC de Wilson de cada banda no vacia
- **AND** para cada banda, la suma de los casos y de los aciertos de las etapas coincide con los de la tabla global

#### Scenario: Etapa o banda vacia declarada no aplicable

- **WHEN** una etapa no tiene casos (por ejemplo, `fallback` con 0 casos) o una banda de una etapa queda vacia
- **THEN** el reporte la lista con 0 casos y la declara "no aplicable"
- **AND** no fabrica una exactitud ni un intervalo para ella

#### Scenario: Distribucion de valores de confianza por etapa

- **WHEN** el framework reporta la calibracion por etapa
- **THEN** lista, para cada etapa, los valores distintos de `confianza` observados en orden ascendente con la cantidad de casos y de aciertos de cada uno
- **AND** la suma de los casos de una etapa coincide con el total de casos de esa etapa

#### Scenario: El reporte no altera las métricas primarias

- **WHEN** se agrega el reporte de calibracion
- **THEN** las metricas primarias de clasificacion (exactitud, F1 macro/micro, matriz 5x5) no cambian de valor
- **AND** la calibracion se calcula como salida adicional sobre las mismas predicciones

#### Scenario: Calibracion emitida por el runner de forma reproducible

- **WHEN** se regenera `evaluation/report.md` dos veces sobre las mismas predicciones y el mismo corpus
- **THEN** la seccion de calibracion es identica en ambas corridas
- **AND** ninguna linea de las secciones preexistentes del reporte se elimina ni cambia de valor

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

### Requirement: Advertencia metodologica del framework coherente con el historial

`evaluation/README.md` SHALL describir la procedencia factual de los ajustes del clasificador realizados con el corpus de evaluacion (vocabulario del filtro deterministico, c-71, commit `1368fd8`; reglas de frontera del prompt, c-72, commit `a76851e`; punto de operacion del cortocircuito por validacion cruzada fuera de muestra, c-74, commit `d6bb474`), SHALL declarar que la mitigacion fuera de muestra cubre el punto de operacion pero no el vocabulario ni las reglas del prompt, SHALL calificar las metricas del reporte como estimaciones dentro de la muestra, SHALL declarar que no se dispuso de un corpus independiente de preproduccion y SHALL enunciar la regla vigente: el corpus de evaluacion se usa solo para diagnostico y todo ajuste posterior se mide sobre datos separados. La documentacion MUST NOT afirmar que el clasificador no fue ajustado sobre el corpus de evaluacion.

#### Scenario: Sin afirmacion de no ajuste

- **WHEN** se busca en `evaluation/README.md` una afirmacion de que el clasificador no fue ajustado sobre el corpus de evaluacion
- **THEN** no aparece ninguna

#### Scenario: Procedencia de los tres ajustes presente

- **WHEN** se lee la advertencia metodologica de `evaluation/README.md`
- **THEN** enumera los ajustes de c-71, c-72 y c-74 con su commit
- **AND** declara que la mitigacion fuera de muestra no cubre el vocabulario ni las reglas del prompt

#### Scenario: Naturaleza dentro de la muestra y ausencia de corpus independiente

- **WHEN** se lee la advertencia metodologica
- **THEN** las metricas del reporte se califican como estimaciones dentro de la muestra
- **AND** se declara que no se dispuso de un corpus independiente de preproduccion
- **AND** la validacion sobre un corpus independiente figura como linea de trabajo futuro

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

### Requirement: Desglose de exactitud por etapa del pipeline

El framework SHALL reportar en `evaluation/report.md`, para cada etapa del pipeline en el orden `deterministic`, `gemini`, `fallback`, la cantidad de casos, los aciertos estrictos y laxos, y la exactitud estricta y laxa, cada una con su IC de Wilson al 95%. Una etapa sin casos SHALL listarse con 0 casos y declararse "no aplicable", sin fabricar exactitud ni intervalo. La suma de los casos y de los aciertos de las etapas MUST coincidir con los totales globales del reporte. El calculo SHALL ser una funcion pura sobre las predicciones ya recolectadas.

#### Scenario: Exactitud por etapa con intervalo de Wilson

- **WHEN** las predicciones incluyen casos resueltos por la etapa `deterministic` y por la etapa `gemini`
- **THEN** el reporte lista, por etapa, casos, aciertos estrictos, exactitud estricta e IC de Wilson, y aciertos laxos, exactitud laxa e IC de Wilson
- **AND** el IC de cada etapa coincide con `intervalo_wilson(aciertos, casos)`

#### Scenario: Aditividad del desglose por etapa

- **WHEN** se suman los casos y los aciertos estrictos y laxos de todas las etapas
- **THEN** las sumas coinciden con el total de casos y con los aciertos estrictos y laxos globales

#### Scenario: Etapa sin casos

- **WHEN** ninguna prediccion corresponde a la etapa `fallback`
- **THEN** la fila de `fallback` reporta 0 casos y "no aplicable" en exactitud e intervalo

### Requirement: Desglose de exactitud por canal de origen

El framework SHALL reportar en `evaluation/report.md`, por cada valor de `canal_origen` presente en el corpus cargado, la cantidad de casos, su composicion por etapa del pipeline, los aciertos estrictos y laxos, y la exactitud estricta y laxa, cada una con su IC de Wilson al 95%. El canal SHALL tomarse del corpus y asociarse a cada prediccion por `caso_id`; si el identificador de una prediccion no coincide con el del caso correspondiente, el runner MUST fallar con un error claro en lugar de reportar un desglose desalineado. El orden de los canales SHALL ser el mismo que el del desglose por canal de la seccion de tiempos (conteo descendente, desempate alfabetico). La suma de casos y de aciertos de los canales MUST coincidir con los totales globales. El calculo SHALL ser una funcion pura.

#### Scenario: Exactitud y composicion por canal

- **WHEN** el corpus contiene casos de mas de un canal de origen
- **THEN** el reporte lista, por canal, casos, cantidad de casos por etapa, aciertos estrictos y laxos, exactitud estricta y laxa e IC de Wilson de cada una
- **AND** los canales aparecen en el mismo orden que en el desglose por canal de la seccion de tiempos

#### Scenario: Aditividad del desglose por canal

- **WHEN** se suman los casos y los aciertos estrictos y laxos de todos los canales
- **THEN** las sumas coinciden con el total de casos y con los aciertos estrictos y laxos globales

#### Scenario: Predicciones desalineadas con el corpus

- **WHEN** el `caso_id` de una prediccion no coincide con el `id` del caso del corpus en la misma posicion
- **THEN** la generacion del reporte falla con un error que identifica la posicion y ambos identificadores
- **AND** no se escribe un desglose por canal desalineado

### Requirement: Procedencia de las predicciones declarada en el reporte

Cuando las predicciones provengan de un archivo con `cache_meta` (cache hit) o de una corrida que lo genera, `evaluation/report.md` SHALL declarar la version del clasificador (`classifier_version`) y la fecha de generacion (`generated_at`) de las predicciones usadas, de modo que el reporte de una corrida de reproduccion no pueda confundirse con el de la corrida oficial. Cuando no haya metadata disponible, la linea SHALL omitirse sin error y el resto del reporte SHALL generarse igual.

#### Scenario: Cache hit declara la procedencia

- **WHEN** el runner genera el reporte a partir de un `predicciones.json` valido con `cache_meta`
- **THEN** el reporte declara el `classifier_version` y el `generated_at` contenidos en ese `cache_meta`

#### Scenario: Corrida nueva declara su propia procedencia

- **WHEN** el runner clasifica el corpus y persiste un `cache_meta` nuevo
- **THEN** el reporte declara la version del clasificador y la fecha de generacion de esa corrida

#### Scenario: Sin metadata se omite la linea

- **WHEN** se invoca `generar_reporte` sin metadata de procedencia
- **THEN** el reporte no incluye la linea de procedencia
- **AND** las demas secciones se generan sin cambios

### Requirement: Contraste pareado de McNemar entre etapas del pipeline

El framework SHALL proveer una funcion pura que, dadas dos secuencias pareadas de aciertos (mismos casos, mismo orden), construya la tabla 2x2 de aciertos y compute el contraste de McNemar: los discordantes `b` (acierta solo la primera) y `c` (acierta solo la segunda), el estadistico chi-cuadrado con correccion de continuidad `max(0, |b - c| - 1)^2 / (b + c)` con su valor p (1 grado de libertad) y el valor p binomial exacto bilateral con `X ~ Bin(b + c; 0,5)`. El p primario SHALL ser el exacto cuando `b + c < 25` y el corregido en otro caso, y el resultado SHALL declarar el criterio aplicado. Sin discordancias, el contraste SHALL declararse "no aplicable" sin fabricar estadistico ni p. Secuencias de distinta longitud MUST producir un error claro. El framework SHALL ademas ensamblar, para el conjunto cortocircuitable `S` del reporte comparativo offline, los pares de aciertos estrictos de la etapa deterministica y de Gemini sobre los casos de `S` con prediccion de ambas etapas, excluyendo y contando los que no la tienen, e imprimir el resultado en ese reporte.

#### Scenario: Tabla 2x2 y discordancias

- **WHEN** se pasan dos secuencias pareadas de aciertos de igual longitud
- **THEN** la tabla reporta los casos con acierto de ambas, solo de la primera (`b`), solo de la segunda (`c`) y de ninguna, y su suma es la cantidad de pares

#### Scenario: Pocas discordancias usan el p exacto

- **WHEN** `b = 10` y `c = 2`
- **THEN** el estadistico corregido es 4,0833 con p 0,0433 y el p exacto es 0,0386
- **AND** el p primario es el exacto porque `b + c < 25`

#### Scenario: Muchas discordancias usan el chi-cuadrado corregido

- **WHEN** `b = 30` y `c = 15`
- **THEN** el estadistico corregido es 4,3556 con p 0,0369 y el p exacto es 0,0357
- **AND** el p primario es el del chi-cuadrado corregido porque `b + c >= 25`

#### Scenario: Sin discordancias

- **WHEN** `b + c = 0`
- **THEN** el contraste se declara "no aplicable" y no se informa estadistico ni valor p

#### Scenario: Ensamblado sobre S con exclusiones

- **WHEN** un caso de `S` no tiene prediccion de Gemini en la cache FORCE-ESCALATE y otro caso no pertenece a `S`
- **THEN** el primero se excluye de los pares y se informa su identificador, y el segundo se ignora
- **AND** solo se aparean predicciones de cache con `etapa == "gemini"`

### Requirement: Analisis de sensibilidad de la etapa deterministica frente al vocabulario ajustado con el corpus

El framework SHALL ofrecer un analisis offline, sin invocar al proveedor de inferencia, que re-mida la etapa deterministica sobre el corpus de evaluacion con el vocabulario vigente antes de su ampliacion guiada por el corpus (c-71), versionado en `evaluation/` con su procedencia (commit, blob y SHA-256), en dos configuraciones: (a) **principal**, vocabulario previo con la logica de decision y el punto de operacion vigentes, leidos de `Settings`, de modo que solo cambie el vocabulario; y (b) **referencia historica**, vocabulario previo con la logica de decision de la epoca (confianza `w / (w + r + 1e-6)`, cortocircuito con confianza `>= 0,90`). Antes de reportar cualquier variante, el analisis SHALL reproducir por el mismo camino la configuracion evaluada (131 casos cortocircuitados y 97 aciertos estrictos, identicos caso por caso al clasificador de produccion). Para cada configuracion SHALL reportar casos cortocircuitados, aciertos estrictos, exactitud con su IC de Wilson al 95 % y cobertura sobre el corpus; para la principal, ademas, la descomposicion pareada frente a la configuracion evaluada. La referencia historica SHALL compararse con la linea base documentada por c-71 y el reporte SHALL declarar si coincide o difiere; la replica de la logica historica MUST NOT ajustarse a los datos. Cuando el repositorio no registre que casos motivaron cada patron agregado, el reporte SHALL declarar no factible la variante por pliegues y su motivo. El analisis MUST NOT modificar el codigo de `App/`, el vocabulario de produccion, `evaluation/report.md` ni las caches de predicciones, y su salida SHALL escribirse en `evaluation/report_sensibilidad_ajustes.md`.

#### Scenario: Configuracion evaluada reproducida antes de reportar

- **WHEN** el analisis clasifica el corpus con el vocabulario vigente por el camino de inyeccion de vocabulario
- **THEN** obtiene 131 casos cortocircuitados y 97 aciertos estrictos, con prediccion, confianza, score y estados de ausencia y empate identicos a los del clasificador de produccion en cada caso
- **AND** si alguna de esas condiciones no se cumple, el analisis falla con un error explicito y no reporta ninguna variante

#### Scenario: Variante principal con intervalo de Wilson

- **WHEN** se clasifica el corpus con el vocabulario previo y la logica y el punto de operacion vigentes
- **THEN** el reporte declara casos cortocircuitados `n`, aciertos `k`, exactitud `k / n`, el IC igual a `intervalo_wilson(k, n)` y la cobertura `n / 200`
- **AND** el umbral, los pesos del score y el conteo minimo de coincidencias usados son los de la configuracion evaluada

#### Scenario: Descomposicion pareada aditiva

- **WHEN** se compara la variante principal con la configuracion evaluada
- **THEN** el reporte separa los casos cortocircuitados por ambas, solo por la evaluada y solo por la variante, con casos y aciertos de cada vocabulario en cada segmento y el contraste pareado sobre los casos comunes
- **AND** los segmentos del lado de la configuracion evaluada suman 131 casos y 97 aciertos

#### Scenario: Referencia historica contra la linea base documentada

- **WHEN** se clasifica el corpus con el vocabulario y la logica previos a c-71
- **THEN** el reporte presenta, frente a los valores documentados por c-71, los reproducidos: casos cortocircuitados (72; 22, 14 y 36 por canal de correo, web y telefono), aciertos estrictos (37; 13, 7 y 17), aciertos laxos (55), casos sin coincidencias (119) y predicciones de Seguridad Informatica (126), cada uno con la marca "coincide" o "difiere"
- **AND** ninguna constante de la replica se modifica para hacer coincidir los valores

#### Scenario: Artefactos historicos verificables

- **WHEN** se leen el vocabulario y el prompt previos versionados en `evaluation/data/sensibilidad_ajustes/`
- **THEN** el SHA-256 de cada archivo coincide con el registrado en su manifiesto de procedencia
- **AND** cada lista del vocabulario previo esta contenida en la vigente, con las cinco claves canonicas en el mismo orden y 62 patrones de diferencia, y el prompt previo es el vigente sin el bloque de reglas de frontera

#### Scenario: Variante por pliegues declarada no factible

- **WHEN** el repositorio no registra que casos del corpus motivaron cada patron agregado por c-71
- **THEN** el reporte declara no factible la reconstruccion del vocabulario por pliegues y enuncia el motivo
- **AND** no reporta como estimacion ninguna asignacion de patrones a pliegues

#### Scenario: Sin efectos sobre los artefactos oficiales

- **WHEN** se ejecuta el analisis offline
- **THEN** no se invoca al proveedor de inferencia ni se escriben `evaluation/report.md`, `evaluation/predicciones.json` ni `evaluation/predicciones_calibracion.json`

#### Scenario: Reporte reproducible

- **WHEN** el analisis offline se ejecuta dos veces sobre el mismo commit y el mismo corpus
- **THEN** `evaluation/report_sensibilidad_ajustes.md` resulta identico byte a byte

### Requirement: Sensibilidad de la exactitud global y del contraste entre etapas con predicciones cacheadas

Cuando la cache FORCE-ESCALATE (`evaluation/predicciones_calibracion.json`) este disponible y verificada, el framework SHALL calcular, sin invocar al proveedor: (a) la exactitud global del pipeline con el vocabulario vigente y con el vocabulario previo, usando en ambos lados las predicciones de la etapa Gemini de esa misma cache para todo caso escalado, sobre el mismo conjunto de casos y con el contraste pareado de McNemar; y (b) el contraste pareado entre la etapa deterministica con el vocabulario previo y la etapa Gemini sobre los casos que ese vocabulario cortocircuita. Las entradas de la cache con `etapa` distinta de `gemini` SHALL tratarse como ausentes, y un caso que requiera una prediccion ausente SHALL excluirse de ambos lados del contraste y listarse en el reporte. Sin la cache, el reporte SHALL declarar ambas salidas "no computable con los artefactos disponibles" y MUST NOT estimarlas por otra via.

#### Scenario: Exactitud global pareada con una sola fuente de predicciones

- **WHEN** la cache FORCE-ESCALATE esta disponible y se simula el pipeline con ambos vocabularios
- **THEN** el reporte declara los aciertos globales de cada configuracion sobre el mismo conjunto de casos y el resultado del contraste de McNemar
- **AND** todas las predicciones de la etapa Gemini de ambos lados provienen de esa cache

#### Scenario: Entradas no semanticas tratadas como ausentes

- **WHEN** un caso escalado por una configuracion solo tiene en la cache una entrada con `etapa` distinta de `gemini`
- **THEN** el caso se excluye de ambos lados del contraste y figura en la lista de excluidos del reporte

#### Scenario: Contraste entre etapas con el vocabulario previo

- **WHEN** se dispone de la cache y de las observaciones del vocabulario previo
- **THEN** el reporte declara, sobre los casos que el vocabulario previo cortocircuita y que tienen prediccion de Gemini, la exactitud de cada etapa y el contraste pareado

#### Scenario: Sin cache, salidas no computables

- **WHEN** la cache FORCE-ESCALATE no esta disponible o no paso su verificacion
- **THEN** el reporte declara la exactitud global con Gemini fijo y el contraste entre etapas como no computables
- **AND** no consigna ningun valor estimado para ellos

### Requirement: Sensibilidad de la etapa semantica frente a las reglas de frontera del prompt

El framework SHALL permitir acotar el efecto de las reglas de frontera del prompt sobre los casos que la configuracion evaluada escala a la etapa Gemini (los que no cortocircuita; 69 en el corpus vigente), por niveles: (a) exactitud de esa etapa con y sin los casos motivadores documentados de las reglas, a partir de la cache oficial; (b) comparacion pareada con una corrida historica cuyo prompt anteceda a las reglas, solo si su fecha de generacion es anterior a la propuesta de las reglas; y (c) ablacion controlada en dos brazos, prompt vigente y prompt sin reglas de frontera, sobre los mismos casos y en una misma sesion. La ablacion SHALL invocar al proveedor solo con confirmacion explicita, evaluada antes de construir el clasificador; SHALL verificar, antes de la primera invocacion, que el SHA-256 del prompt cargado coincide con el esperado para el brazo; SHALL escribir cada brazo en un archivo propio con metadatos de brazo, hash y origen del prompt, modelo, temperatura, version del clasificador, hash del corpus, casos, fecha y cantidad de respuestas de reserva; SHALL contar una respuesta de reserva como error; y MUST NOT escribir las predicciones ni el reporte oficiales. El reporte SHALL presentar cada nivel disponible y declarar los no disponibles.

#### Scenario: Corrida paga sin confirmacion

- **WHEN** se solicita un brazo de la ablacion sin `--confirm-paid` ni la variable de confirmacion
- **THEN** la ejecucion falla con un error de corrida paga no confirmada antes de construir el clasificador real
- **AND** no se realiza ninguna invocacion al proveedor

#### Scenario: Prompt verificado antes de invocar

- **WHEN** el prompt cargado por el backend para un brazo no tiene el SHA-256 esperado para ese brazo
- **THEN** la ejecucion falla antes de la primera invocacion y no escribe ningun archivo de salida

#### Scenario: Brazos sobre los mismos casos y en archivos separados

- **WHEN** se ejecutan ambos brazos con confirmacion
- **THEN** cada brazo clasifica exactamente los casos que la configuracion evaluada no cortocircuita y escribe su propio archivo con los metadatos requeridos
- **AND** `evaluation/predicciones.json` y `evaluation/report.md` no cambian

#### Scenario: Comparacion pareada entre brazos

- **WHEN** existen las predicciones de ambos brazos
- **THEN** el reporte declara los aciertos estrictos de cada brazo sobre los mismos casos, las respuestas de reserva contadas como error y el contraste pareado de McNemar
- **AND** si la cache oficial esta disponible, declara tambien la deriva del brazo vigente frente a la corrida oficial

#### Scenario: Version del prompt de una corrida historica

- **WHEN** se evalua el nivel (b) con una corrida historica
- **THEN** su prompt se clasifica como "previa confirmada", "probablemente previa", "posterior" o "indeterminada" segun su fecha de generacion frente a la propuesta y a la aplicacion de las reglas de frontera
- **AND** solo la clase "previa confirmada" habilita el uso del nivel (b) fuera del reporte

<!-- c-144 (archivado el 2026-10-23 en main) ya incorporo al spec vivo el requisito "Advertencia metodologica del framework coherente con el historial"; este change solo verifica el texto resultante. -->

### Requirement: Portabilidad del CLI de sensibilidad entre versiones de Python 3.12

El CLI `python -m evaluation.sensibilidad_ajustes` SHALL aceptar los nombres exactos de
sus opciones con independencia de la política de abreviaturas del módulo `argparse` de
la versión de parche de Python 3.12. El parser de nivel superior SHALL deshabilitar la
resolución por prefijo (`allow_abbrev=False`), de modo que `prompt --brazo vigente` se
interprete siempre como la opción del subcomando y no como una abreviatura ambigua de
`--brazo-vigente` o `--brazo-sin-reglas`. La suite SHALL incluir una prueba de regresión
que fije ese comportamiento y que pase en Python 3.12.3 y en Python 3.12.15.

El modo `python -m evaluation.run_evaluation --solo-tiempos` SHALL informar la ausencia
del reporte con un error de línea de comandos legible y un código de salida distinto de
cero, sin propagar una traza cruda de `FileNotFoundError`.

#### Scenario: Abreviatura ambigua no se resuelve por prefijo

- **WHEN** se ejecuta `python -m evaluation.sensibilidad_ajustes prompt --brazo vigente` en Python 3.12.3
- **THEN** el parser reconoce `--brazo` como opción del subcomando `prompt`
- **AND** no falla con `error: ambiguous option: --brazo`

#### Scenario: Opciones de nivel superior con nombre exacto

- **WHEN** se ejecuta el CLI con `--brazo-vigente` o `--brazo-sin-reglas`
- **THEN** el parser las reconoce por su nombre exacto
- **AND** un prefijo no exacto que colisione con ambas no se resuelve silenciosamente

#### Scenario: Prueba de regresión en la suite

- **WHEN** se ejecuta `cd evaluation && pytest tests/test_sensibilidad_ajustes.py -q` en Python 3.12.3
- **THEN** las pruebas del CLI pasan sin fallos
- **AND** existe una prueba que falla si se elimina `allow_abbrev=False` del parser de nivel superior

#### Scenario: Reporte ausente en modo solo tiempos

- **WHEN** se ejecuta `python -m evaluation.run_evaluation --solo-tiempos` sin un `report.md` previo
- **THEN** el proceso termina con un código distinto de cero
- **AND** imprime un mensaje de error legible sin una traza cruda de `FileNotFoundError`
