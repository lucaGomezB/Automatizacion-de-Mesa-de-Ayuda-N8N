# evaluation-prediction-cache — Delta Spec

## Purpose

Extiende la capacidad de cache de predicciones para declarar que, junto al cache vivo (regenerable y gitignoreado), el repositorio versiona un snapshot congelado de las predicciones como evidencia de evaluación, sin alterar la naturaleza de cache del archivo original.

## ADDED Requirements

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
