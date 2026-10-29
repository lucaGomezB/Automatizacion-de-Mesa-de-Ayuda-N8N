## Purpose

Extiende el instrumento y los protocolos de la campana de campo (introducidos por c-165) con el control de orden/brazo necesario para un diseno CONTRABALANCEADO y con el protocolo y la ruta de harness para una validacion sobre un corpus INDEPENDIENTE (out-of-sample), de modo que el efecto de orden sea estimable y las metricas de clasificacion puedan reportarse fuera de muestra.

## ADDED Requirements

### Requirement: ECM-004 — Control de orden y contrabalanceo en los harnesses de ingesta

Los harnesses de ingesta del corpus (`ingest_via_n8n.py`, `ingest_corpus.py`, `ingest_telefonia_corpus.py`) SHALL aceptar un parametro de orden `--orden` con al menos los valores `directo`, `inverso`, `alternado` y `aleatorio`, que determine el orden en que los casos son procesados dentro de la corrida. El valor por defecto SHALL ser `directo`, preservando el comportamiento previo. El modo `aleatorio` SHALL requerir una semilla (`--seed`) y con la misma semilla y el mismo conjunto de casos MUST producir el mismo orden. El harness SHALL registrar, por caso, el orden efectivamente aplicado en el sidecar de trazabilidad como un campo aditivo y NULL-able, sin romper consumidores existentes. El cambio MUST NOT requerir conexion a servicios externos para operar (los harnesses siguen siendo ejecutables/verificables offline en su subconjunto determinista).

#### Scenario: Orden directo preserva el orden del corpus

- **WHEN** el harness corre con `--orden directo`
- **THEN** procesa los casos en el orden en que aparecen en el corpus y registra `orden` por caso en el sidecar

#### Scenario: Orden inverso invierte la secuencia

- **WHEN** el harness corre con `--orden inverso`
- **THEN** procesa los casos en orden inverso al del corpus y registra `orden` por caso en el sidecar

#### Scenario: Orden alternado interleala las mitades

- **WHEN** el harness corre con `--orden alternado`
- **THEN** los casos de la primera y la segunda mitad se procesan de forma intercalada segun la regla documentada del modo

#### Scenario: Aleatorio reproducible por semilla

- **WHEN** el harness corre dos veces con `--orden aleatorio --seed S` sobre el mismo conjunto de casos
- **THEN** ambas corridas producen exactamente el mismo orden de procesamiento

#### Scenario: El sidecar registra el orden sin romper consumidores

- **WHEN** se inspecciona el sidecar tras una corrida con cualquier `--orden`
- **THEN** cada entrada de caso expone un campo `orden` con el valor aplicado y las entradas y campos previos se conservan

### Requirement: ECM-005 — Protocolo de campana contrabalanceada registrado

El proyecto SHALL incluir un runbook versionado que defina, para una campana contrabalanceada: como se reparte el corpus en mitades o brazos y que orden se asigna a cada uno, como se estima el efecto de orden (por ejemplo comparando primera contra segunda mitad, o ajustando un termino de orden), y un criterio explicito de aceptacion del diseno. El runbook SHALL ser ejecutable por los autores sin conocimiento tacito y MUST NOT depender de datos de campo ya recolectados.

#### Scenario: El runbook define asignacion de mitades y orden

- **WHEN** se lee el runbook de contrabalanceo
- **THEN** especifica como se asignan las mitades o brazos y que orden recibe cada uno

#### Scenario: El runbook define la estimacion del efecto de orden

- **WHEN** un autor consulta como estimar el efecto de orden
- **THEN** el runbook describe el procedimiento de comparacion o de ajuste y su criterio de aceptacion

### Requirement: ECM-006 — Ruta de harness y verificacion de corpus independiente sin solape

El proyecto SHALL proveer una ruta de harness y un protocolo para medir sobre un corpus INDEPENDIENTE cuyo contenido MUST NOT solaparse con el corpus de ajuste (los 200 casos). La verificacion de no solape SHALL comparar los identificadores y las descripciones de ambos corpus y MUST fallar de forma accionable si detecta cualquier interseccion, impidiendo reportar como out-of-sample un caso ya usado. El corpus independiente SHALL producirse con el mismo protocolo de pseudonimizacion y la misma exigencia de doble etiquetado que el corpus de ajuste.

#### Scenario: Verificacion de no solape bloquea la corrida

- **WHEN** un caso del corpus candidato comparte identificador o descripcion con el corpus de ajuste
- **THEN** la verificacion falla con un error que identifica el caso y no permite continuar la validacion out-of-sample

#### Scenario: Corpus independiente sin solape habilita la medision

- **WHEN** el corpus candidato no comparte identificadores ni descripciones con el corpus de ajuste
- **THEN** la verificacion pasa y el harness procede a medir sobre el corpus independiente

#### Scenario: Mismo protocolo de pseudonimizacion y doble etiquetado

- **WHEN** se prepara el corpus independiente
- **THEN** se aplica el mismo procedimiento de pseudonimizacion y la misma exigencia de doble etiquetado que el corpus de ajuste

### Requirement: ECM-007 — Reporte out-of-sample de las metricas de ambas etapas

El sistema SHALL producir un reporte que exponga las metricas de las dos etapas (clasificacion) calculadas sobre el corpus INDEPENDIENTE, distinguidas de las calculadas in-sample sobre el corpus de ajuste. El reporte SHALL etiquetar cada conjunto de metricas como in-sample u out-of-sample y MUST NOT mezclar en un mismo agregado casos de ajuste con casos independientes.

#### Scenario: El reporte separa in-sample de out-of-sample

- **WHEN** se genera el reporte de la campana
- **THEN** las metricas del corpus de ajuste y las del corpus independiente aparecen etiquetadas por separado y no se agregan juntas

#### Scenario: Ambas etapas reportadas sobre el corpus independiente

- **WHEN** se inspecciona el reporte out-of-sample
- **THEN** estan presentes las metricas de las dos etapas sobre el corpus independiente, con su origen declarado
