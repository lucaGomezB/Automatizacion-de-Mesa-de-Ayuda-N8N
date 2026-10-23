## ADDED Requirements

### Requirement: Hash del corpus independiente de la plataforma de checkout

El hash SHA-256 del corpus que valida el cache de predicciones (y que el reporte imprime) SHALL calcularse sobre un archivo cuyo contenido no dependa de la plataforma ni de la configuracion de fin de linea del checkout. El repositorio SHALL declarar en `.gitattributes` que `data/corpus_evaluacion_pseudonimizado.json` se normaliza y se extrae con fin de linea LF en toda plataforma, de modo que el SHA-256 de la copia de trabajo coincida con el del blob versionado (`1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb` para el corpus vigente). Si se versionan archivos de predicciones del framework de evaluacion, SHALL aplicarseles la misma regla. La declaracion MUST NOT modificar el contenido del blob del corpus.

#### Scenario: Checkout en Windows con autocrlf produce el hash canonico

- **WHEN** se clona el repositorio en Windows con `core.autocrlf=true` y se calcula el SHA-256 de `data/corpus_evaluacion_pseudonimizado.json` en la copia de trabajo
- **THEN** el hash es `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`
- **AND** coincide con el hash calculado en un checkout Linux del mismo commit

#### Scenario: Cache generado en otra maquina es valido

- **WHEN** se coloca en `evaluation/predicciones.json` un cache generado en otra maquina con el mismo corpus, la misma cantidad de casos y la misma version del clasificador
- **THEN** el runner lo reconoce como cache valido y no invoca al clasificador

#### Scenario: El contenido versionado del corpus no cambia

- **WHEN** se agrega la regla de fin de linea en `.gitattributes` y se refresca la copia de trabajo
- **THEN** `git diff` no muestra cambios de contenido en `data/corpus_evaluacion_pseudonimizado.json`
- **AND** el blob versionado del corpus conserva su identificador
