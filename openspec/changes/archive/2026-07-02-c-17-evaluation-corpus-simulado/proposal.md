## Why

El framework de evaluacion en `evaluation/` esta completo (runner, metricas, reportes, tests) pero solo tiene un fixture sintetico de 9 casos. La tesis (Capitulo 4, Seccion 4.4) afirma un corpus de validacion de 200 incidentes con distribucion estratificada (41% Sistemas, 32% Operaciones, 27% Soporte Tecnico). El corpus real de 200 casos no existe en el repositorio. Este change construye un corpus simulado de 200 casos realistas, pseudonimizados, que permite ejercitar el pipeline de evaluacion completo antes de la defensa.

## What Changes

- Se crea un corpus simulado de 200 incidentes en `evaluation/data/corpus_evaluacion.csv`
- Cada caso incluye descripcion realista en espanol rioplatense, categoria real (ground truth), y canal de origen
- La distribucion respeta exactamente la de la tesis: 82/64/54
- Las descripciones incluyen variaciones de estilo, jerga local, y errores de tipeo realistas (~10%)
- Se incluye un script de generacion reproducible (`evaluation/generate_corpus.py`) con seed fijo
- Se agrega documentacion en `evaluation/data/README.md` explicando el origen simulado del corpus

## Capabilities

### New Capabilities

- `evaluation-corpus`: Corpus simulado de 200 casos para ejercitar el pipeline de evaluacion del clasificador hibrido. Incluye script de generacion reproducible, CSV con datos pseudonimizados, y documentacion.

### Modified Capabilities

Ninguna. Este change introduce un artefacto nuevo, no modifica funcionalidad existente.

## Impact

- **Archivos nuevos**: `evaluation/data/corpus_evaluacion.csv`, `evaluation/data/README.md`, `evaluation/generate_corpus.py`
- **Archivos modificados**: Ninguno
- **Tests**: Se agregan tests de validacion del corpus generado en `evaluation/tests/test_corpus_generated.py`
- **Dependencias**: Ninguna nueva. El script usa solo `csv` y `random` de la biblioteca estandar
- **Rompe algo?**: No. El corpus real se sigue esperando en `data/corpus_evaluacion_pseudonimizado.csv`. Este corpus simulado vive en `evaluation/data/` y es independiente
