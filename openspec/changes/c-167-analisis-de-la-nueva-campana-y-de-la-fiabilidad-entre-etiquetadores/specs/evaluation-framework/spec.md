## ADDED Requirements

### Requirement: Analisis de exactitud del brazo manual contra la verdad de consenso

El framework SHALL analizar las clasificaciones del brazo manual registradas por la campana
(c-165) contra la verdad de consenso del corpus (`sector_asignado`), calculando la exactitud
estricta y la exactitud laxa por etiquetador y de forma agregada. Cada exactitud MUST
acompanarse de su intervalo de confianza de Wilson con el nivel de confianza declarado. El
calculo SHALL ser una funcion pura sobre los registros ya cargados y MUST reutilizar las
definiciones de exactitud estricta, exactitud laxa e intervalo de Wilson vigentes en el
framework, sin redefinirlas. Una etiqueta ausente para un caso MUST contabilizarse como
error, nunca excluirse en silencio.

#### Scenario: Exactitud por etiquetador y agregada

- **WHEN** se analiza un dataset con dos etiquetadores sobre los mismos casos
- **THEN** el resultado reporta exactitud estricta y laxa para cada etiquetador y para el conjunto
- **AND** cada valor incluye su intervalo de Wilson y el nivel de confianza usado

#### Scenario: Exactitud laxa no menor que la estricta

- **WHEN** se calculan ambas exactitudes sobre el mismo conjunto de etiquetas
- **THEN** la exactitud laxa es mayor o igual que la estricta para cada etiquetador

#### Scenario: Etiqueta manual ausente se cuenta como error

- **WHEN** un caso del corpus no tiene etiqueta registrada por un etiquetador
- **THEN** ese caso cuenta como error en la exactitud de ese etiquetador y el resultado declara cuantos casos faltan

### Requirement: Analisis de la tasa de intervencion humana con intervalos de confianza

El framework SHALL calcular la tasa de intervencion humana segun la definicion operativa de
la tesis (seccion 11.3), reportando la proporcion de casos intervenidos y la proporcion del
tiempo de proceso atribuible a intervencion. Cada proporcion MUST acompanarse de su intervalo
de confianza de Wilson y MUST derivarse de intervenciones efectivamente registradas, no de
casos elegibles marcados para revision. El analisis SHALL declarar el conteo de casos y de
intervenciones usado como denominador y numerador.

#### Scenario: Proporcion de casos y de tiempo reportadas

- **WHEN** se analiza un dataset de intervencion con casos intervenidos y no intervenidos
- **THEN** el resultado reporta la proporcion de casos intervenidos y la proporcion de tiempo de proceso, cada una con su intervalo de Wilson

#### Scenario: Casos elegibles no intervenidos no cuentan

- **WHEN** un caso esta marcado para revision pero no registra intervencion
- **THEN** no se cuenta en el numerador de la tasa de intervencion

#### Scenario: Dataset sin intervenciones declara el limite inferior

- **WHEN** el dataset no registra ninguna intervencion
- **THEN** la tasa reportada es cero con su intervalo de Wilson, sin error de division por cero

### Requirement: Analisis del efecto de orden del run contrabalanceado

El framework SHALL analizar el efecto de orden del run contrabalanceado (c-166) contrastando
el desempeno de la primera mitad contra la segunda mitad, o mediante un termino de orden,
segun la asignacion registrada. El resultado MUST reportar el contraste pareado con su
estadistico, su valor p y el tamano del efecto estandarizado, reutilizando las funciones de
contraste vigentes. Cuando no existan pares suficientes para el contraste, el analisis MUST
declararlo como no aplicable en lugar de producir un valor silencioso.

#### Scenario: Contraste entre mitades reportado

- **WHEN** el dataset contrabalanceado tiene pares suficientes por posicion
- **THEN** el resultado reporta el estadistico del contraste, el valor p y el tamano del efecto
- **AND** declara cuantos pares se usaron

#### Scenario: Pares insuficientes declara no aplicable

- **WHEN** el dataset no alcanza el minimo de pares para el contraste
- **THEN** el resultado marca el analisis de orden como no aplicable sin emitir un valor de efecto

### Requirement: Evaluacion out-of-sample del corpus independiente en ambas etapas

El framework SHALL evaluar el corpus independiente (c-166) con las funciones de metrica
vigentes para la etapa deterministica y la etapa semantica, reportando las metricas
out-of-sample separadas de las metricas in-sample. El reporte MUST identificar el corpus
evaluado y la etapa de cada conjunto de metricas, y MUST fallar con un error explicito cuando
el corpus independiente o sus predicciones no esten disponibles, sin sustituirlos por los
datos in-sample.

#### Scenario: Ambas etapas reportadas sobre el corpus independiente

- **WHEN** se evalua el corpus independiente con predicciones de las dos etapas
- **THEN** el resultado reporta las metricas de cada etapa identificando el corpus como independiente

#### Scenario: Metricas in-sample y out-of-sample separadas

- **WHEN** el reporte incluye ambos conjuntos de metricas
- **THEN** las metricas out-of-sample y las in-sample aparecen en secciones distinguibles y no se mezclan

#### Scenario: Corpus independiente ausente no cae a in-sample

- **WHEN** falta el corpus independiente o sus predicciones
- **THEN** el analisis lanza un error que nombra el artefacto faltante y no reporta metricas in-sample en su lugar

### Requirement: Fiabilidad entre etiquetadores con kappa e intervalo de confianza

El framework SHALL calcular el coeficiente kappa de Cohen sobre el dataset de doble
etiquetado (c-168) y MUST reportar su intervalo de confianza con el nivel declarado, usando
al menos un metodo de bootstrap con semilla fija y un metodo asintotico. El valor de kappa
MUST pertenecer al rango `[-1, 1]`; el analisis MUST declarar como no estimable el caso en
que el acuerdo esperado haga indeterminado el denominador, sin devolver un valor inventado.
Cuando el muestreo bootstrap no alcance a producir un intervalo estable, el resultado MUST
declarar el intervalo como no computable.

#### Scenario: Kappa y su intervalo se reportan juntos

- **WHEN** se analiza un dataset de doble etiquetado con ambos etiquetadores completos
- **THEN** el resultado reporta el valor de kappa y su intervalo de confianza con el nivel y el metodo declarados

#### Scenario: Bootstrap reproducible por semilla

- **WHEN** se recalcula el intervalo por bootstrap con la misma semilla y los mismos datos
- **THEN** el intervalo resultante es identico

#### Scenario: Acuerdo esperado indeterminado declara no estimable

- **WHEN** las marginales del dataset hacen indeterminado el denominador del kappa
- **THEN** el resultado declara el kappa como no estimable y no devuelve un valor numerico

### Requirement: Ejecucion offline y determinista del analisis de campana

El modulo de analisis de campana SHALL ejecutarse sin acceso a red ni a servicios externos y
MUST producir resultados identicos sobre las mismas entradas. Sus pruebas MUST correr sobre
fixtures sinteticos, de modo que la suite pase sin datasets de campo ni credenciales.

#### Scenario: Analisis sin red

- **WHEN** se ejecuta el analisis sobre un fixture sintetico en un entorno sin red
- **THEN** el analisis completa y produce su resultado sin intentar conexiones externas

#### Scenario: Reproducibilidad sobre las mismas entradas

- **WHEN** se ejecuta dos veces el mismo analisis con la misma semilla
- **THEN** los valores numericos y los intervalos reportados son identicos
