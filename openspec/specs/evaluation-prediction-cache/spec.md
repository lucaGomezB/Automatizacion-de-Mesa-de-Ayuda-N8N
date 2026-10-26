# evaluation-prediction-cache Specification

## Purpose
Cache de predicciones para el runner de evaluacion: evita re-invocar el clasificador cuando el corpus y la configuracion del clasificador no cambiaron entre ejecuciones, reduciendo el costo operativo de Gemini a cero en corridas repetidas.
## Requirements
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

### Requirement: Confirmacion obligatoria de la corrida paga

El runner SHALL rechazar por defecto una corrida que invoque un clasificador pago real cuando no exista un cache valido o cuando se bypasee el cache, salvo que el usuario confirme explicitamente la corrida paga mediante el flag `--confirm-paid` o la variable de entorno `EVALUATION_CONFIRM_PAID`. Un cache hit MUST NOT requerir confirmacion, porque no invoca al clasificador. Un clasificador inyectado por parametro (uso en pruebas) MUST NOT requerir confirmacion. El rechazo SHALL ser explicito y accionable, con codigo de salida no-cero, y MUST NOT invocar al clasificador pago.

#### Scenario: Cache hit sin confirmacion

- **WHEN** existe un cache valido y no se aporta confirmacion de corrida paga
- **THEN** el runner carga las predicciones del cache, no invoca al clasificador y no exige confirmacion

#### Scenario: Cache miss sin confirmacion

- **WHEN** no existe un cache valido y no se aporta confirmacion de corrida paga
- **THEN** el runner rechaza la corrida sin invocar al clasificador y termina con codigo de salida no-cero

#### Scenario: Confirmacion por flag

- **WHEN** no existe un cache valido y se invoca el runner con `--confirm-paid`
- **THEN** el runner invoca el clasificador real

#### Scenario: Confirmacion por variable de entorno

- **WHEN** no existe un cache valido y `EVALUATION_CONFIRM_PAID` tiene un valor verdadero
- **THEN** el runner invoca el clasificador real

#### Scenario: Clasificador inyectado en pruebas

- **WHEN** se inyecta un clasificador por parametro y no existe un cache valido
- **THEN** el runner clasifica sin exigir confirmacion de corrida paga

#### Scenario: Bypass de cache no implica confirmacion

- **WHEN** se usa `--force` con un clasificador pago real y sin confirmacion
- **THEN** el runner rechaza la corrida paga; el bypass de cache no sustituye la confirmacion

### Requirement: Estimacion de costo antes de la corrida paga

El runner SHALL imprimir, antes de invocar un clasificador pago real, una estimacion del costo de la corrida derivada de la cantidad de casos del corpus y un costo estimado por llamada, para que el usuario decida con informacion. La estimacion SHALL ser orientativa y SHALL declarar sus supuestos; MUST NOT presentarse como una factura.

#### Scenario: Estimacion impresa antes de clasificar

- **WHEN** una corrida paga procede
- **THEN** antes de invocar al clasificador se imprime la cantidad de casos del corpus y el costo estimado total de la corrida

#### Scenario: Cache hit no reporta costo pago

- **WHEN** existe un cache valido y se usa
- **THEN** el runner no imprime una estimacion de costo pago

### Requirement: Snapshot de evidencia versionado junto al cache vivo

El repositorio SHALL publicar un snapshot congelado de las predicciones del cache bajo el directorio `evaluation/evidence/`, como copia byte-idéntica al archivo de cache en el momento de su publicación. El archivo de cache vivo (`evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json`) MUST permanecer excluido del control de versiones en `.gitignore`; el snapshot versionado MUST residir en una ruta NO ignorada. El snapshot SHALL conservar el bloque `cache_meta` completo (`corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`) del archivo de origen.

#### Scenario: Snapshot versionado fuera de la exclusión

- **WHEN** se inspecciona el snapshot bajo `evaluation/evidence/`
- **THEN** el archivo existe en el repositorio y NO está afectado por ninguna regla de `.gitignore`

#### Scenario: Cache vivo permanece gitignoreado

- **WHEN** se consulta el estado de ignorados de `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json`
- **THEN** ambos archivos siguen siendo ignorados por Git

#### Scenario: Copia byte-idéntica

- **WHEN** se compara el snapshot versionado contra el archivo de cache del que deriva, tomado en el momento de la publicación
- **THEN** ambos archivos tienen el mismo contenido byte a byte

### Requirement: Metadatos de la evidencia documentados

Cada snapshot de evidencia SHALL estar documentado con su `classifier_version`, `corpus_hash` y `generated_at`. Cuando el `corpus_hash` del snapshot NO coincida con el hash del corpus actualmente versionado, la documentación MUST declararlo explícitamente para que el snapshot no se interprete como representativo del estado vigente del corpus.

#### Scenario: Documentación de metadatos por snapshot

- **WHEN** se revisa `evaluation/evidence/README.md`
- **THEN** figura para cada snapshot su `classifier_version`, `corpus_hash` y `generated_at`

#### Scenario: Divergencia de corpus declarada

- **WHEN** un snapshot fue generado sobre un `corpus_hash` distinto del corpus actual
- **THEN** su documentación indica explícitamente esa divergencia y advierte que documenta un estado anterior del corpus

### Requirement: Recálculo por caso sin invocar Gemini

El snapshot de evidencia SHALL permitir recalcular métricas por caso sin invocar al clasificador pagado. La evidencia MUST poder unirse con el corpus pseudonimizado público por identificador de caso (`caso_id` en las predicciones y `id` en el corpus).

#### Scenario: Join por identificador de caso

- **WHEN** se unen las predicciones del snapshot con los casos del corpus público por identificador
- **THEN** cada predicción queda asociada a su caso de corpus sin requerir ninguna llamada al clasificador

#### Scenario: Sin invocación al clasificador

- **WHEN** se recomputan métricas a partir del snapshot versionado
- **THEN** no se realiza ninguna invocación al clasificador pagado

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

