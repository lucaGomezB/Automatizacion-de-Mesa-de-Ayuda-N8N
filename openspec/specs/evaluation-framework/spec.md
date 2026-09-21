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

El framework SHALL aplicar la prueba de Wilcoxon de rangos con signo sobre los pares (tiempo_manual, tiempo_automatizado) para contrastar la igualdad de medianas entre ambos flujos, y SHALL reportar el tamaño del efecto rank-biserial asociado, conforme a §4.7 y §7.1 de la tesis. El cálculo SHALL ser una función pura que recibe las dos series pareadas y devuelve el estadístico, el valor p y el tamaño del efecto.

#### Scenario: Diferencia sistemática produce p significativo

- **WHEN** el flujo automatizado es consistentemente más rápido que el manual en todos los pares
- **THEN** la prueba devuelve un valor p por debajo del nivel de significancia 0.05 y un tamaño del efecto de magnitud alta

#### Scenario: Series de distinta longitud son rechazadas

- **WHEN** se invoca la prueba con dos series de cantidad de elementos distinta
- **THEN** el framework lanza un error en lugar de producir un resultado inválido

### Requirement: Runner de evaluación sobre el corpus

El framework SHALL proveer un runner que, dado un corpus, invoque el clasificador híbrido caso por caso recolectando para cada uno el sector predicho principal, los sectores adicionales predichos, la confianza y la etapa del pipeline (`deterministic`, `gemini` o `fallback`), y produzca las métricas de clasificación multietiqueta y un reporte en `evaluation/report.md`. El runner MUST ser ejecutable como una operación de un solo comando cuando el corpus real esté presente en `data/corpus_evaluacion_pseudonimizado.json`, y MUST aislar la recolección de predicciones del cálculo de métricas (inyección del clasificador) para permitir pruebas con un clasificador simulado. El runner MUST negarse a invocar el clasificador real sin confirmación explícita del operador, abortando con un error claro cuando la confirmación está ausente. La documentación del runner (`evaluation/README.md`) MUST describir ese gate de corrida paga junto al comando único de corrida y a la configuración de `GEMINI_API_KEY`: MUST nombrar las dos formas de confirmación (`--confirm-paid` y `EVALUATION_CONFIRM_PAID=1`), MUST indicar que sin confirmación la corrida aborta sin invocar el clasificador real, y MUST indicar que al confirmar se imprime una estimación de costo.

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
