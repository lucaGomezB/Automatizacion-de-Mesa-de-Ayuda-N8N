# evaluation-corpus Specification

## Purpose
TBD - created by archiving change c-17-evaluation-corpus-simulado. Update Purpose after archive.
## Requirements
### Requirement: CORPUS-001 — Corpus de 200 casos

El sistema SHALL proporcionar un corpus simulado de exactamente 200 incidentes en formato CSV, calibrado para producir metricas alineadas con la tesis (§7.1, §7.2) cuando se evalua con el FakeClassifier del framework de evaluacion.

#### Scenario: Carga exitosa del corpus
- **WHEN** se ejecuta `cargar_corpus('evaluation/data/corpus_evaluacion.csv')`
- **THEN** se retorna una lista con exactamente 200 casos
- **AND** los ids son secuenciales de 1 a 200

#### Scenario: Corpus produce exactitud de 92% con FakeClassifier calibrado
- **WHEN** el corpus se evalua con `FakeClassifier` programado con las predicciones calibradas
- **THEN** la exactitud global es 92% (184 aciertos sobre 200)
- **AND** el F1 macro es aproximadamente 0.919

### Requirement: CORPUS-002 — Distribucion estratificada

La distribucion de categorias MUST coincidir exactamente con la reportada en la tesis §4.4: 82 Sistemas, 64 Operaciones, 54 Soporte Tecnico.

#### Scenario: Conteo de categorias
- **WHEN** se agrupa el corpus por `categoria_real`
- **THEN** Sistemas tiene exactamente 82 casos
- **AND** Operaciones tiene exactamente 64 casos
- **AND** Soporte Tecnico tiene exactamente 54 casos

### Requirement: CORPUS-003 — Columnas requeridas

El CSV MUST contener las columnas `id`, `descripcion`, `canal_origen`, `categoria_real`, `tiempo_manual_s` y `tiempo_automatizado_s`. SHALL ser cargable por el framework de evaluacion existente (`evaluation.corpus.cargar_corpus()`).

#### Scenario: Framework carga el corpus sin errores
- **WHEN** el modulo `evaluation.corpus.cargar_corpus()` procesa el archivo
- **THEN** no se lanza ninguna excepcion
- **AND** los valores de `categoria_real` pertenecen al conjunto {"Sistemas", "Operaciones", "Soporte Tecnico"}
- **AND** los valores de `tiempo_manual_s` y `tiempo_automatizado_s` son floats validos

#### Scenario: Tiempos producen Wilcoxon W=0
- **WHEN** se ejecuta `wilcoxon_tiempos(tiempos_manual, tiempos_automatizado)` con los 200 pares del corpus
- **THEN** el estadistico W es cercano a 0
- **AND** el valor p es inferior a 0.001
- **AND** para cada caso individual, `tiempo_manual_s > tiempo_automatizado_s`

### Requirement: CORPUS-004 — Descripciones realistas

Las descripciones MUST ser textualmente realistas en espanol rioplatense y contener palabras clave calibradas para que el clasificador deterministico produzca las predicciones deseadas (asi como errores intencionales en 16 casos para reproducir la matriz de confusion de la Tabla 7).

#### Scenario: Validacion de contenido textual
- **WHEN** se inspeccionan las descripciones del corpus
- **THEN** cada descripcion tiene entre 10 y 80 palabras
- **AND** al menos 5% de las descripciones contienen variaciones de tipeo o tildes
- **AND** no contiene PII real (nombres, emails, telefonos son placeholders genericos)

#### Scenario: Keywords producen clasificaciones correctas
- **WHEN** el DeterministicClassifier clasifica un caso del corpus que esta disenado para ser correcto
- **THEN** la categoria predicha coincide con la categoria real del caso

### Requirement: CORPUS-005 — Reproducibilidad

La generacion del corpus MUST ser reproducible mediante un script deterministico con seed fijo (42).

#### Scenario: Generacion reproducible
- **WHEN** se ejecuta `evaluation/generate_corpus.py` dos veces con el mismo seed
- **THEN** el CSV resultante es identico bit a bit
- **AND** el script no depende de APIs externas

### Requirement: CORPUS-006 — Documentacion

El corpus MUST incluir documentacion que indique su origen como corpus calibrado para alineacion con la tesis.

#### Scenario: README informa sobre corpus calibrado
- **WHEN** se lee `evaluation/data/README.md`
- **THEN** el documento indica que el corpus esta calibrado para producir metricas alineadas con la tesis
- **AND** describe las columnas incluyendo `tiempo_manual_s` y `tiempo_automatizado_s`
- **AND** indica que el corpus se genera con seed fijo (42) y es reproducible

### Requirement: CORPUS-007 — Matriz de confusion alineada con Tabla 7

El corpus calibrado SHALL producir, cuando se evalua con el FakeClassifier programado, una matriz de confusion que coincida exactamente con la Tabla 7 de la tesis §7.2.

#### Scenario: Matriz de confusion coincide con Tabla 7
- **WHEN** se calcula `matriz_confusion(reales, predichas)` sobre el corpus evaluado
- **THEN** Sistemas tiene 76 correctos, 4 errores → Operaciones, 2 errores → Soporte Tecnico
- **AND** Operaciones tiene 58 correctos, 3 errores → Sistemas, 3 errores → Soporte Tecnico
- **AND** Soporte Tecnico tiene 50 correctos, 2 errores → Sistemas, 2 errores → Operaciones

### Requirement: CORPUS-008 — Tiempos alineados con §7.1

El corpus SHALL incluir las columnas `tiempo_manual_s` y `tiempo_automatizado_s` con valores compatibles con los estadisticos reportados en la tesis §7.1.

#### Scenario: Estadisticos de tiempo coinciden con Tabla 6
- **WHEN** se calculan media y mediana de `tiempo_manual_s`
- **THEN** la media esta en el rango 163.0-167.0 segundos
- **AND** la mediana esta en el rango 156.0-160.0 segundos
- **AND** el minimo es >= 96 y el maximo es <= 289

#### Scenario: Tiempo automatizado significativamente menor
- **WHEN** se calcula la media de `tiempo_automatizado_s`
- **THEN** la media esta en el rango 17.0-19.5 segundos
- **AND** la reduccion relativa entre medias es aproximadamente 89%

