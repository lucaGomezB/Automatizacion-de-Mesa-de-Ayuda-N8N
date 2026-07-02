# Delta Spec: evaluation-corpus

## ADDED Requirements

### Requirement: CORPUS-001 — Corpus de 200 casos

El sistema SHALL proporcionar un corpus simulado de exactamente 200 incidentes en formato CSV.

#### Scenario: Carga exitosa del corpus
- **WHEN** se ejecuta `cargar_corpus('evaluation/data/corpus_evaluacion.csv')`
- **THEN** se retorna un DataFrame con exactamente 200 filas
- **AND** los ids son secuenciales de 1 a 200

### Requirement: CORPUS-002 — Distribucion estratificada

La distribucion de categorias MUST coincidir exactamente con la reportada en la tesis: 82 Sistemas, 64 Operaciones, 54 Soporte Tecnico.

#### Scenario: Conteo de categorias
- **WHEN** se agrupa el corpus por `categoria_real`
- **THEN** Sistemas tiene exactamente 82 casos
- **AND** Operaciones tiene exactamente 64 casos
- **AND** Soporte Tecnico tiene exactamente 54 casos

### Requirement: CORPUS-003 — Columnas requeridas

El CSV MUST contener las columnas `id`, `descripcion`, `canal_origen`, `categoria_real` y SHALL ser cargable por el framework de evaluacion existente.

#### Scenario: Framework carga el corpus sin errores
- **WHEN** el modulo `evaluation.corpus.cargar_corpus()` procesa el archivo
- **THEN** no se lanza ninguna excepcion
- **AND** los valores de `categoria_real` pertenecen al conjunto {"Sistemas", "Operaciones", "Soporte Tecnico"}

### Requirement: CORPUS-004 — Descripciones realistas

Las descripciones MUST ser textualmente realistas para simular incidentes de mesa de ayuda, con texto en espanol rioplatense y variedad de registros.

#### Scenario: Validacion de contenido textual
- **WHEN** se inspeccionan las descripciones del corpus
- **THEN** cada descripcion tiene entre 10 y 80 palabras
- **AND** al menos 5% de las descripciones contienen variaciones de tipeo o tildes
- **AND** no contiene PII real (nombres, emails, telefonos son placeholders genericos)

### Requirement: CORPUS-005 — Reproducibilidad

La generacion del corpus MUST ser reproducible mediante un script deterministico con seed fijo.

#### Scenario: Generacion reproducible
- **WHEN** se ejecuta `evaluation/generate_corpus.py` dos veces con el mismo seed
- **THEN** el CSV resultante es identico bit a bit
- **AND** el script no depende de APIs externas

### Requirement: CORPUS-006 — Documentacion

El corpus MUST incluir documentacion que indique su origen simulado y prevenga malentendidos.

#### Scenario: README informa sobre origen simulado
- **WHEN** se lee `evaluation/data/README.md`
- **THEN** el documento indica explicitamente que el corpus es simulado
- **AND** advierte que NO debe usarse para reportar metricas en la tesis
- **AND** describe las columnas y la distribucion
