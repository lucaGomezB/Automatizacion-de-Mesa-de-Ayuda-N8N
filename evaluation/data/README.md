# evaluation/data/

Esta carpeta ya no contiene corpus (hoy aloja la plantilla de etiquetado,
`campana/` y `sensibilidad_ajustes/`). El corpus calibrado de 200 casos y su
script de generación fueron **eliminados permanentemente** en C-27.

## Estado actual

- **Corpus real**: `data/corpus_evaluacion_pseudonimizado.json` (raíz del repo,
  versionado en su forma pseudonimizada). Ver `data/README.md`.
- **Fixture de tests**: `evaluation/tests/fixtures/corpus_fixture.json`
  (sintético, mínimo, trackeado). Ver `evaluation/tests/fixtures/README.md`.
- **Esquema y contrato**: `evaluation/README.md`.

No se genera ni se trackea ningún CSV **de corpus ni de resultados**. Las únicas
excepciones son la plantilla vacía del doble etiquetado y, después de la campaña, su
tabla primaria (ver más abajo). Cualquier métrica histórica asociada al
corpus sintético (distribución 82/64/54, exactitud 92%, F1 ~0.919, Tabla 7)
queda **superada** por C-27.

## `plantilla_etiquetado.csv` y `campana/` (c-168)

- `plantilla_etiquetado.csv`: plantilla **solo con encabezado** (sin filas, sin
  PII) del esquema único de toda planilla etiquetador x caso de la campaña:
  `id_caso,id_etiquetador,tarea,sector_etiquetado,sectores_adicionales_etiquetados,inicio,timestamp`.
  La usan el doble etiquetado y el brazo manual; la valida
  `python -m evaluation.doble_etiquetado`. Se versiona con fin de línea LF.
- `campana/`: procedencia (`README.md`) y, **después de la campaña**, la tabla
  primaria `doble_etiquetado.csv` con su SHA-256 y el `registro_sujetos.csv`. Hoy
  solo contiene el README: el etiquetado real corre fuera del repositorio. Ver
  `evaluation/data/campana/README.md` y
  `docs/campana-medicion/runbook-doble-etiquetado.md`.

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
