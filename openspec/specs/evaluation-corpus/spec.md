# evaluation-corpus Specification

## Purpose
TBD - created by archiving change c-17-evaluation-corpus-simulado. Update Purpose after archive.

## Requirements

### Requirement: CORPUS-009 — Estructura del documento JSON

El corpus SHALL ser un objeto JSON con `schema_version` (entero), un objeto `metadata` (con al menos `descripcion` y `total_casos`) y un arreglo `casos`. El campo `schema_version` MUST permitir evolucionar el esquema; `total_casos` MUST coincidir con la cantidad de elementos de `casos`.

#### Scenario: Documento JSON bien formado

- **WHEN** se carga un corpus con `schema_version`, `metadata` y `casos`
- **THEN** el loader valida la estructura y devuelve un caso por cada elemento de `casos`

#### Scenario: total_casos inconsistente es rechazado

- **WHEN** `metadata.total_casos` no coincide con la cantidad real de `casos`
- **THEN** el loader reporta un error de consistencia

### Requirement: CORPUS-012 — Campos requeridos del caso

Cada caso del corpus MUST contener los campos `id`, `descripcion`, `canal_origen`, `sector_asignado`, `sectores_adicionales`, `tiempo_manual_s` y `tiempo_automatizado_s`. El campo `categoria_real` MUST dejar de existir. El corpus SHALL ser cargable por el framework de evaluacion existente (`evaluation.corpus.cargar_corpus()`), que MUST validar los campos requeridos y los sectores canonicos antes de devolver los casos.

#### Scenario: Framework carga el corpus sin errores

- **WHEN** el modulo `evaluation.corpus.cargar_corpus()` procesa un corpus JSON valido
- **THEN** no se lanza ninguna excepcion
- **AND** cada caso expone `sector_asignado` y `sectores_adicionales`
- **AND** los valores de `tiempo_manual_s` y `tiempo_automatizado_s` son numericos validos

#### Scenario: Campo requerido ausente produce error accionable

- **WHEN** un caso del corpus omite `sectores_adicionales`, `sector_asignado` o `id`
- **THEN** el loader lanza un error que identifica el campo faltante y el caso afectado

### Requirement: CORPUS-010 — Invariantes de la verdad multietiqueta

`sector_asignado` MUST ser un unico string canonico. `sectores_adicionales` MUST estar presente en todos los casos (arreglo vacio `[]` cuando no hay sectores adicionales) y MUST NOT incluir el valor de `sector_asignado`. Todos los valores, tanto de `sector_asignado` como de `sectores_adicionales`, MUST pertenecer al conjunto canonico de cinco sectores.

#### Scenario: Sector asignado no se repite en adicionales

- **WHEN** un caso repite su `sector_asignado` dentro de `sectores_adicionales`
- **THEN** el loader rechaza el caso con un error de invariante

#### Scenario: Sector adicional invalido es rechazado

- **WHEN** un caso contiene en `sectores_adicionales` un valor fuera del conjunto canonico
- **THEN** el loader lanza un error que identifica el valor invalido y el caso afectado

#### Scenario: Ausencia de sectores adicionales es valida

- **WHEN** un caso declara `sectores_adicionales: []`
- **THEN** el caso es valido y su conjunto de verdad es el de `sector_asignado` unicamente

### Requirement: CORPUS-011 — Corpus real y eliminacion del corpus sintetico

El repositorio MUST NOT contener el corpus sintetico provisional ni su generador; la unica fuente de evaluacion SHALL ser el corpus real en formato JSON, cuya ruta canonica es `data/corpus_evaluacion_pseudonimizado.json` (ignorada por git y provista externamente). El fixture de pruebas del framework SHALL vivir en JSON con las etiquetas canonicas.

#### Scenario: El corpus sintetico ya no existe en el repositorio

- **WHEN** se inspecciona el arbol del repositorio
- **THEN** no existen `evaluation/data/corpus_evaluacion.csv`, `evaluation/generate_corpus.py`, `data/corpus_sintetico_provisional.csv` ni `scripts/gen_corpus.py`

#### Scenario: Corpus real ausente no rompe el framework

- **WHEN** se ejecuta el runner y `data/corpus_evaluacion_pseudonimizado.json` no esta presente
- **THEN** el runner termina con un error claro indicando que debe colocarse el corpus real, sin inventar datos
