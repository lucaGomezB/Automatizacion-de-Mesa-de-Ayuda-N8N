## Why

El pseudonimizador de produccion (`App/Backend/app/utils/pseudonymizer.py`) sobreenmascara texto no-PII: `_RE_PERSONA` acepta cualquier secuencia de 2+ palabras capitalizadas y `_is_excluded_persona` solo cubre una lista corta. Evidencia:

- `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv` (salida del modulo) tiene 9 etiquetas: 1 `[TELEFONO]` sobre un codigo DLL y 8 `[PERSONA]`, todas falsos positivos.
- El corpus evaluado `data/corpus_evaluacion_pseudonimizado.json` tiene 0 etiquetas y es equivalente byte a byte al crudo `data/Corpus Tesis - Hoja 1.csv` (0 diferencias ignorando espacios finales); los falsos positivos se restauraron antes del commit `ea62576`.
- `evaluation/data/campana/corpus_campana.json` tiene 0 etiquetas y descripciones identicas al corpus evaluado.
- Produccion enmascara antes de clasificar (`App/Backend/app/services/incidente_service.py:345-347`), mientras el corpus evaluado esta limpio: existe una brecha produccion/evaluacion.

## What Changes

- Endurecer la heuristica de persona con tres reglas: (a) un determinante, articulo o posesivo inicial (`El`, `La`, `Los`, `Las`, `Un`, `Una`, `Su`, `Sus`, `Este`, `Esta`, `Ese`, `Esa`, `Mi`, `Tu`, ...) no convierte la frase en persona; (b) exclusion de sectores canonicos insensible a tildes, para cubrir `Seguridad Informática`; (c) ampliacion de la allowlist de productos, areas y frases observadas (`Adobe PDF Reader`, `Microsoft Vision`, `.NET Framework`, `Recursos Humanos`, `Acceso Denegado`, ...).
- Cubrir cada falso positivo con un test y agregar regresiones que prueben que nombres reales (con tildes y ñ), emails, telefonos, hosts y tarjetas se siguen enmascarando.
- Regenerar `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv` con el modulo corregido para que coincida con el JSON evaluado (0 etiquetas).
- Documentar la frontera (que se enmascara y que no) y las reglas de determinante y sector en `docs/pseudonymization.md`.
- Dejar asentado que NINGUNA metrica reportada cambia: el corpus evaluado es igual a la salida del modulo corregido; repetir la corrida es un no-op.

**Fuera de alcance:** `app/classifiers/`, `docs/prompt_gemini.txt`, los umbrales de `constants.py`, el clasificador, el JSON del corpus evaluado, la redaccion de la tesis (change B) y cualquier corrida paga de Gemini.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `data-pseudonymization`: se redefine la frontera de la heuristica de persona (determinante inicial, sectores insensibles a tildes, allowlist ampliada) y se agrega la invariante de no regresion de cobertura de PII genuina; el corpus publicado debe quedar sin falsos positivos.

## Impact

- Codigo: `App/Backend/app/utils/pseudonymizer.py`.
- Tests: `App/Backend/tests/test_pseudonymizer.py`; si corresponde, `scripts/corpus_ingest/test_pseudonymize_corpus.py`.
- Datos: `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv` regenerado; `data/corpus_evaluacion_pseudonimizado.json` sin cambios.
- Documentacion: `docs/pseudonymization.md`.
- Gobernanza: ALTO/CRITICO (PII y seguridad). Restriccion dura: solo puede reducir falsos positivos; no puede debilitar la cobertura de PII genuina y la suite debe probarlo.
- Metricas: sin cambios; no se requiere re-ejecutar la evaluacion.