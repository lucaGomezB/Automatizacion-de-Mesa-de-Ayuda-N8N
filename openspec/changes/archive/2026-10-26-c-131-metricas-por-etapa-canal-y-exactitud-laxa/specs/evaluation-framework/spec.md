## MODIFIED Requirements

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

## ADDED Requirements

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
