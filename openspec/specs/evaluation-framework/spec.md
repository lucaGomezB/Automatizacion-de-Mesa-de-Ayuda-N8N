# evaluation-framework Specification

## Purpose
TBD - created by archiving change c-08-evaluation-framework. Update Purpose after archive.
## Requirements
### Requirement: Contrato y carga del corpus de evaluación

El framework SHALL definir un esquema explícito para el corpus de evaluación y cargarlo desde un archivo CSV. El esquema SHALL incluir, como mínimo, las columnas `id` (identificador del caso), `descripcion` (texto pseudonimizado del incidente) y `categoria_real` (etiqueta de verdad fundamental). La categoría real de cada caso MUST pertenecer al conjunto exacto, sensible a mayúsculas, `{"Sistemas", "Operaciones", "Soporte Técnico"}`. La carga MUST fallar con un error claro y accionable cuando el archivo no exista, falte una columna requerida, o una categoría sea inválida; nunca SHALL continuar con datos malformados de forma silenciosa.

#### Scenario: Carga de un corpus válido

- **WHEN** se carga un CSV con columnas `id`, `descripcion`, `categoria_real` y todas las categorías pertenecen al conjunto exacto
- **THEN** el framework devuelve la colección de casos con la misma cantidad de filas que el CSV, preservando id, descripción y categoría real de cada uno

#### Scenario: Archivo de corpus inexistente

- **WHEN** se solicita cargar el corpus desde una ruta que no existe
- **THEN** el framework lanza un error explícito que nombra la ruta faltante, sin producir una colección vacía silenciosa

#### Scenario: Columna requerida ausente

- **WHEN** se carga un CSV al que le falta una de las columnas requeridas (`id`, `descripcion` o `categoria_real`)
- **THEN** el framework lanza un error que identifica la columna faltante

#### Scenario: Categoría fuera del conjunto válido

- **WHEN** un caso del CSV trae una categoría que no pertenece al conjunto exacto (por ejemplo `"sistemas"` en minúscula o `"Redes"`)
- **THEN** el framework lanza un error que identifica el valor inválido y el caso afectado

### Requirement: Matriz de confusión

El framework SHALL calcular la matriz de confusión a partir de las listas pareadas de categorías reales y predichas, sobre el conjunto fijo y ordenado de las tres clases objetivo (`Sistemas`, `Operaciones`, `Soporte Técnico`). La celda `(real, predicho)` MUST contener la cantidad de casos cuya categoría real es la fila y cuya categoría predicha es la columna. El cálculo SHALL ser una función pura, sin I/O ni dependencias de red.

#### Scenario: Clasificación perfecta produce matriz diagonal

- **WHEN** las categorías predichas coinciden con las reales en todos los casos
- **THEN** la matriz de confusión tiene todos los conteos sobre la diagonal y cero fuera de ella

#### Scenario: Errores se ubican fuera de la diagonal

- **WHEN** un caso real `Sistemas` se predice como `Operaciones`
- **THEN** la celda `(Sistemas, Operaciones)` se incrementa en uno y la celda diagonal `(Sistemas, Sistemas)` no cuenta ese caso

### Requirement: Métricas por clase y promedio macro

El framework SHALL calcular, por cada una de las tres clases, la precisión, la sensibilidad (recall) y la medida F1, y además el promedio macro de cada métrica (media aritmética simple sobre las tres clases, con igual peso por clase). La precisión, la sensibilidad y el F1 MUST definirse de forma robusta ante denominador cero (cuando una clase no tiene predicciones o no tiene casos reales), devolviendo 0.0 en lugar de propagar una división por cero. El cálculo SHALL ser una función pura.

#### Scenario: F1 de una clase a partir de precisión y sensibilidad

- **WHEN** una clase tiene precisión y sensibilidad bien definidas y no nulas
- **THEN** su F1 es la media armónica `2 * P * R / (P + R)`

#### Scenario: Promedio macro pondera las clases por igual

- **WHEN** se calcula el F1 macro sobre las tres clases
- **THEN** el resultado es la media aritmética de los tres F1 por clase, independiente de cuántos casos tenga cada clase

#### Scenario: Clase sin predicciones no rompe el cálculo

- **WHEN** ninguna predicción cae en una clase determinada (denominador de precisión cero)
- **THEN** la precisión de esa clase es 0.0 y el cálculo continúa sin lanzar excepción

### Requirement: Exactitud global e intervalo de confianza de Wilson

El framework SHALL calcular la exactitud global como la proporción de casos correctamente clasificados sobre el total, y SHALL estimar el intervalo de confianza al 95% de esa proporción mediante el método de Wilson (§4.7). El cálculo SHALL ser una función pura.

#### Scenario: Exactitud como proporción de aciertos

- **WHEN** se clasifican N casos y K coinciden con la categoría real
- **THEN** la exactitud global es `K / N`

#### Scenario: Intervalo de Wilson contiene la proporción puntual

- **WHEN** se calcula el intervalo de Wilson al 95% para una proporción de aciertos
- **THEN** el intervalo está acotado en `[0, 1]`, su límite inferior no supera a la proporción puntual y su límite superior no es inferior a ella

### Requirement: Análisis estadístico de tiempos

El framework SHALL aplicar la prueba de Wilcoxon de rangos con signo sobre los pares (tiempo_manual, tiempo_automatizado) para contrastar la igualdad de medianas entre ambos flujos, y SHALL reportar el tamaño del efecto rank-biserial asociado, conforme a §4.7 y §7.1 de la tesis. El cálculo SHALL ser una función pura que recibe las dos series pareadas y devuelve el estadístico, el valor p y el tamaño del efecto.

#### Scenario: Diferencia sistemática produce p significativo

- **WHEN** el flujo automatizado es consistentemente más rápido que el manual en todos los pares
- **THEN** la prueba devuelve un valor p por debajo del nivel de significancia 0.05 y un tamaño del efecto de magnitud alta

#### Scenario: Series de distinta longitud son rechazadas

- **WHEN** se invoca la prueba con dos series de cantidad de elementos distinta
- **THEN** el framework lanza un error en lugar de producir un resultado inválido

### Requirement: Runner de evaluación sobre el corpus

El framework SHALL proveer un runner que, dado un corpus, invoque el clasificador híbrido caso por caso recolectando para cada uno la categoría predicha, la confianza y la etapa del pipeline (`deterministic`, `gemini` o `fallback`), y produzca las métricas de clasificación y un reporte en `evaluation/report.md`. El runner MUST ser ejecutable como una operación de un solo comando cuando el corpus real esté presente en `data/corpus_evaluacion_pseudonimizado.csv`, y MUST aislar la recolección de predicciones del cálculo de métricas (inyección del clasificador) para permitir pruebas con un clasificador simulado.

#### Scenario: Recolección de predicciones por caso

- **WHEN** el runner procesa un corpus con un clasificador inyectado
- **THEN** por cada caso del corpus se registra exactamente una predicción con categoría, confianza y etapa

#### Scenario: Generación del reporte de métricas

- **WHEN** el runner finaliza el procesamiento de un corpus
- **THEN** escribe `evaluation/report.md` con la matriz de confusión, la exactitud global y las métricas por clase y macro

#### Scenario: Corpus real ausente no rompe el framework

- **WHEN** se ejecuta el runner y el archivo `data/corpus_evaluacion_pseudonimizado.csv` no está presente
- **THEN** el runner termina con un error claro indicando que debe colocarse el corpus real, sin inventar datos ni producir un reporte con resultados ficticios

