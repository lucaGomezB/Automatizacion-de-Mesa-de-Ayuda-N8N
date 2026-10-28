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

### Requirement: CORPUS-012 — Contratos separados del caso (clasificacion y tiempos)

Cada caso del corpus MUST declarar el contrato de CLASIFICACION: `id`, `descripcion`, `canal_origen`, `sector_asignado` y `sectores_adicionales`. Los campos de TIEMPO `tiempo_manual_s` y `tiempo_automatizado_s` SHALL ser OPCIONALES: un caso MAY omitirlos o declararlos `null` (el corpus real pseudonimizado tiene 56 casos sin `tiempo_automatizado_s`). Cuando un campo de tiempo este presente y no sea `null`, MUST ser numerico; un valor no numerico MUST seguir rechazandose con un error accionable, de modo que la estrictez de `_a_float` se conserve para los campos que valida y no se relaje a los fines de admitir la ausencia. El campo `categoria_real` MUST dejar de existir.

`evaluation.corpus.cargar_corpus()` SHALL ser el unico loader del corpus: MUST validar el contrato de clasificacion (campos presentes, sectores canonicos e invariante multietiqueta) y el contrato de tiempos (numerico cuando presente y no nulo) antes de devolver los casos. Un loader tolerante duplicado MUST NOT existir; la carga del corpus real (incluido el que tiene tiempos nulos) SHALL usar el mismo `cargar_corpus()`.

#### Scenario: Corpus real con tiempos nulos cargado por el unico loader

- **WHEN** `evaluation.corpus.cargar_corpus()` procesa un corpus con casos cuyo `tiempo_automatizado_s` es `null` o esta ausente
- **THEN** no se lanza ninguna excepcion
- **AND** cada caso expone `sector_asignado`, `sectores_adicionales` y sus campos de clasificacion
- **AND** `tiempo_manual_s` y `tiempo_automatizado_s` quedan en `None`

#### Scenario: Un tiempo presente pero no numerico se rechaza

- **WHEN** un caso declara `tiempo_manual_s: "n/a"` (o un valor booleano)
- **THEN** el loader lanza un error que identifica el campo y el caso afectado
- **AND** no normaliza el valor a `None` de forma silenciosa

#### Scenario: Un campo del contrato de clasificacion ausente produce error accionable

- **WHEN** un caso omite `id`, `descripcion`, `canal_origen`, `sector_asignado` o `sectores_adicionales`
- **THEN** el loader lanza un error que identifica el campo faltante y el caso afectado

#### Scenario: Sector invalido es rechazado por el unico loader

- **WHEN** un caso declara un `sector_asignado` o un `sectores_adicionales` fuera del conjunto canonico
- **THEN** el loader lanza un error que identifica el valor invalido y el caso afectado

#### Scenario: El loader tolerante duplicado deja de existir

- **WHEN** se busca `cargar_corpus_tolerante` en `evaluation/`
- **THEN** no aparece como funcion de carga independiente
- **AND** los ex consumidores (`evaluation/run_evaluation.py` y `evaluation/deterministic_measurement.py`) cargan el corpus con `cargar_corpus()`

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
