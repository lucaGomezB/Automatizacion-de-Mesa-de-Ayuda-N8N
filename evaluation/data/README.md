# evaluation/data/

Esta carpeta ya no contiene corpus. El corpus calibrado de 200 casos y su
script de generación fueron **eliminados permanentemente** en C-27.

## Estado actual

- **Corpus real**: `data/corpus_evaluacion_pseudonimizado.json` (raíz del repo,
  versionado en su forma pseudonimizada). Ver `data/README.md`.
- **Fixture de tests**: `evaluation/tests/fixtures/corpus_fixture.json`
  (sintético, mínimo, trackeado). Ver `evaluation/tests/fixtures/README.md`.
- **Esquema y contrato**: `evaluation/README.md`.

No se genera ni se trackea ningún CSV. Cualquier métrica histórica asociada al
corpus sintético (distribución 82/64/54, exactitud 92%, F1 ~0.919, Tabla 7)
queda **superada** por C-27.

## `sensibilidad_ajustes/` (c-142)

Artefactos **históricos** del análisis de sensibilidad frente a los ajustes del
clasificador (`python -m evaluation.sensibilidad_ajustes`). No son datos de
evaluación ni contienen datos personales; se versionan con fin de línea LF
(`.gitattributes`) para que sus SHA-256 coincidan en Windows y Linux.

- `keywords_pre_c71.json`: `KEYWORD_MAP` previo a c-71 (89 patrones), extraído
  del blob `858f1c6` (`git show 7925903:App/Backend/app/classifiers/keywords.py`).
- `prompt_gemini_pre_c72.txt`: prompt de Gemini previo a las reglas de frontera de
  c-72, blob `1daceb3` (`git show a76851e^:docs/prompt_gemini.txt`).
- `procedencia.json`: commit de origen, ruta, blob, fecha, comando de extracción y
  SHA-256 de cada archivo. Los tests verifican la integridad de ambos.
