## ADDED Requirements

### Requirement: ECM-011 — Ensamblado de la planilla C1 unificada que consume el analisis

El proyecto SHALL proveer el modulo/CLI `evaluation/preparar_entradas_analisis.py`, ejecutable
offline y de solo lectura sobre sus fuentes, que construye
`evaluation/data/campana/plantilla_etiquetado.csv` como la union, bajo un unico encabezado C1 en
el orden `id_caso,id_etiquetador,tarea,sector_etiquetado,sectores_adicionales_etiquetados,inicio,timestamp`,
de las filas de `evaluation/data/campana/doble_etiquetado.csv` (`tarea = doble_etiquetado`) y de
`evaluation/data/campana/brazo_manual.csv` (`tarea = brazo_manual`), preservando el orden de
origen. El archivo de salida MUST versionarse con fin de linea LF y UTF-8 sin BOM, para que su
SHA-256 coincida entre sistemas. Antes de escribir, el modulo MUST re-validar la union por tarea
con `validar_doble_etiquetado` de `evaluation/doble_etiquetado.py` contra
`data/corpus_evaluacion_pseudonimizado.json` (una validacion por `tarea`) y MUST abortar sin
escribir con un error accionable que nombre el archivo fuente y la `tarea` ofendida si alguna
fuente falta o no pasa el validador. El modulo MUST imprimir el SHA-256 del archivo producido. Con
las mismas fuentes, dos corridas MUST producir el archivo byte a byte identico.

#### Scenario: Union de las dos planillas en una sola hoja C1

- **WHEN** existen `doble_etiquetado.csv` y `brazo_manual.csv` validos en `evaluation/data/campana/`
- **THEN** `plantilla_etiquetado.csv` contiene un unico encabezado C1 seguido de las filas de ambas tareas, con las filas de `doble_etiquetado` (`E1`/`E2`) y de `brazo_manual` (`O1`/`O2`) juntas

#### Scenario: Validacion por tarea antes de escribir

- **WHEN** una fila de `brazo_manual.csv` no pasa el validador bajo `--tarea brazo_manual`
- **THEN** el modulo termina con error accionable que nombra el archivo y la `tarea`, y no escribe `plantilla_etiquetado.csv`

#### Scenario: Fuente ausente no produce una planilla parcial

- **WHEN** falta `doble_etiquetado.csv` o `brazo_manual.csv`
- **THEN** el modulo falla nombrando el archivo faltante y no escribe una planilla con solo una de las tareas

#### Scenario: Reproducibilidad byte a byte

- **WHEN** se ejecuta el modulo dos veces sobre las mismas fuentes
- **THEN** `plantilla_etiquetado.csv` es identico en ambas corridas y su SHA-256 coincide

### Requirement: ECM-012 — Staging de la referencia in-sample que consume el analisis

El proyecto SHALL proveer, en el mismo modulo/CLI, el paso que materializa
`evaluation/data/campana/predicciones_in_sample.json` como copia **byte a byte** del cache
congelado `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`. La fuente MUST tratarse
como de solo lectura y el modulo MUST NOT regenerar predicciones ni escribir en
`evaluation/evidence/`. El modulo MUST imprimir el SHA-256 del archivo producido y MUST declarar
la procedencia (fuente y hash de la fuente) en la salida. Con la misma fuente, dos corridas MUST
producir la copia identica.

#### Scenario: Copia byte a byte del cache congelado

- **WHEN** se ejecuta el paso de staging
- **THEN** `predicciones_in_sample.json` tiene exactamente el mismo contenido y SHA-256 que `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`

#### Scenario: Fuente de solo lectura

- **WHEN** el modulo corre sobre la fuente congelada
- **THEN** el archivo de `evaluation/evidence/` queda byte a byte igual y no se invoca ningun camino que regenere predicciones de v9

#### Scenario: Reproducibilidad de la copia

- **WHEN** se ejecuta el paso de staging dos veces
- **THEN** la copia producida es identica en ambas corridas y su SHA-256 coincide con el de la fuente

### Requirement: ECM-013 — Proteccion de artefactos congelados y procedencia de las entradas ensambladas

El modulo SHALL negarse a escribir sobre cualquier artefacto congelado (via `es_archivo_congelado`
de `evaluation/plan_campana.py`) ni sobre sus propias fuentes (`doble_etiquetado.csv`,
`brazo_manual.csv`, `evaluation/evidence/**`), abortando con error accionable antes de escribir.
El paso SHALL ser el unico camino documentado para producir las dos entradas y MUST NOT poder
saltarse en silencio. La procedencia de cada entrada producida (`plantilla_etiquetado.csv` y
`predicciones_in_sample.json`) SHALL registrarse con su SHA-256 en
`evaluation/data/campana/README.md`. Los runbooks y
`evaluation/data/campana/analisis/README.md` SHALL documentar el paso y la procedencia, de modo
que la campana sea ejecutable sin conocimiento tacito.

#### Scenario: Rechazo de un destino congelado

- **WHEN** el destino del modulo coincide con un artefacto congelado del corpus o con `evaluation/evidence/`
- **THEN** el modulo termina con error accionable y no modifica el archivo congelado

#### Scenario: Procedencia registrada en el README

- **WHEN** se versionan `plantilla_etiquetado.csv` y `predicciones_in_sample.json`
- **THEN** `evaluation/data/campana/README.md` declara el SHA-256 de cada uno y de que fuente proviene

#### Scenario: Paso documentado en los runbooks

- **WHEN** un autor sigue el runbook de la campana
- **THEN** el runbook indica ejecutar `evaluation/preparar_entradas_analisis.py` y explica que el analisis de c-167 lee esas dos entradas de `evaluation/data/campana/`
