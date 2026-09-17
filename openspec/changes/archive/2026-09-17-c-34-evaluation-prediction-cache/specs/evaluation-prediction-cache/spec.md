## Purpose

Cache de predicciones para el runner de evaluacion: evita re-invocar el clasificador cuando el corpus y la configuracion del clasificador no cambiaron entre ejecuciones, reduciendo el costo operativo de Gemini a cero en corridas repetidas.

## ADDED Requirements

### Requirement: Cache hit omite la clasificacion

Cuando `predicciones.json` existe y fue producido con el mismo corpus (mismo hash SHA-256 del archivo JSON y misma cantidad de casos) y la misma clave de version del clasificador, el runner SHALL cargar las predicciones del archivo y omitir por completo la invocacion al clasificador.

#### Scenario: Cache valido produce predicciones sin llamar al clasificador

- **WHEN** `predicciones.json` existe con metadata de cache que coincide con el corpus actual y la version del clasificador
- **THEN** el runner devuelve las predicciones cargadas del archivo y el clasificador no recibe ninguna llamada

#### Scenario: Cache valido produce el mismo reporte que una corrida completa

- **WHEN** se carga un cache valido y se genera el reporte
- **THEN** el reporte contiene las mismas metricas que si el clasificador hubiera sido invocado directamente

### Requirement: Invalidacion automatica del cache

El cache SHALL invalidarse automaticamente cuando el corpus cambia (hash SHA-256 o cantidad de casos diferente) o cuando la clave de version del clasificador cambia. El runner MUST re-invocar el clasificador completo en ese caso.

#### Scenario: Cambio en el corpus invalida el cache

- **WHEN** `predicciones.json` existe pero el hash SHA-256 del archivo de corpus actual difiere del hash almacenado en la metadata del cache
- **THEN** el runner invoca el clasificador sobre todos los casos y sobreescribe `predicciones.json`

#### Scenario: Cambio en la version del clasificador invalida el cache

- **WHEN** `predicciones.json` existe pero la clave de version del clasificador almacenada en la metadata difiere de la clave actual
- **THEN** el runner invoca el clasificador sobre todos los casos y sobreescribe `predicciones.json`

#### Scenario: Cantidad de casos distinta invalida el cache

- **WHEN** `predicciones.json` existe pero el campo `corpus_count` de la metadata no coincide con la cantidad de casos del corpus actual
- **THEN** el runner invoca el clasificador sobre todos los casos y sobreescribe `predicciones.json`

### Requirement: Opt-out obligatorio con flag --force / --no-cache

El runner SHALL exponer una opcion de linea de comandos (`--force` o `--no-cache`) que, cuando esta presente, bypasea la verificacion del cache y re-ejecuta la clasificacion completa independientemente del estado de `predicciones.json`. El cache resultante SHALL sobreescribirse al finalizar la corrida.

#### Scenario: Flag --force bypasea un cache valido

- **WHEN** `predicciones.json` existe con un cache valido y el runner se invoca con `--force`
- **THEN** el clasificador es invocado sobre todos los casos y `predicciones.json` es sobreescrito

#### Scenario: Flag --no-cache es equivalente a --force

- **WHEN** el runner se invoca con `--no-cache`
- **THEN** el comportamiento es identico al de `--force`: se omite el cache y se re-ejecuta la clasificacion

### Requirement: Formato del archivo predicciones.json con metadata de cache

`predicciones.json` SHALL contener un campo de nivel superior `cache_meta` con al menos los campos `corpus_hash` (string SHA-256 hex del archivo de corpus), `corpus_count` (entero con la cantidad de casos), `classifier_version` (string clave de version del clasificador) y `generated_at` (timestamp ISO-8601 UTC). El arreglo de predicciones SHALL residir bajo la clave `predictions`. El formato SHALL ser retrocompatible: si `cache_meta` esta ausente, el archivo se considera un cache invalido y se re-ejecuta la clasificacion.

#### Scenario: Archivo nuevo incluye metadata de cache

- **WHEN** el runner completa una clasificacion y persiste `predicciones.json`
- **THEN** el archivo contiene los campos `cache_meta.corpus_hash`, `cache_meta.corpus_count`, `cache_meta.classifier_version` y `cache_meta.generated_at`

#### Scenario: Archivo sin cache_meta se considera invalido

- **WHEN** `predicciones.json` existe pero no contiene el campo `cache_meta`
- **THEN** el runner trata el archivo como cache invalido y re-invoca el clasificador
