# evaluation/data/

Esta carpeta ya no contiene corpus. El corpus calibrado de 200 casos y su
script de generación fueron **eliminados permanentemente** en C-27.

## Estado actual

- **Corpus real**: `data/corpus_evaluacion_pseudonimizado.json` (raíz del repo,
  no trackeado en git por privacidad). Ver `data/README.md`.
- **Fixture de tests**: `evaluation/tests/fixtures/corpus_fixture.json`
  (sintético, mínimo, trackeado). Ver `evaluation/tests/fixtures/README.md`.
- **Esquema y contrato**: `evaluation/README.md`.

No se genera ni se trackea ningún CSV. Cualquier métrica histórica asociada al
corpus sintético (distribución 82/64/54, exactitud 92%, F1 ~0.919, Tabla 7)
queda **superada** por C-27.
