## MODIFIED Requirements

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
