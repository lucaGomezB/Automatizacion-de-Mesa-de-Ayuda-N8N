# evaluation/data/

Esta carpeta ya no contiene corpus (hoy aloja la plantilla de etiquetado,
`campana/` y `sensibilidad_ajustes/`; `campana/` guarda también el plan de la campaña
y las predicciones del corpus independiente, ver `campana/README.md`). El corpus calibrado de 200 casos y su
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
- La hoja unificada de `campana/`, `plantilla_etiquetado.csv` (unión C1 de
  `doble_etiquetado.csv` + `brazo_manual.csv`) y la copia in-sample
  `predicciones_in_sample.json` las ensambla `evaluation/preparar_entradas_analisis.py`
  (c-170), offline, a partir de las fuentes versionadas. Son las dos entradas que lee
  `evaluation/analisis_campana.py` (c-167).

## `campana/`: plan, sidecars y corpus independiente (c-166)

`campana/` aloja además los artefactos de la **campaña contrabalanceada** y de la
**clasificación del corpus independiente**: el plan por caso (`plan_campana.csv`) y sus
sub-planes, la copia de campaña del corpus (`corpus_campana.json`, con los tiempos en
`null`), un sidecar propio por corrida, el corpus independiente pseudonimizado (ids
`I001..`) y sus predicciones (`predicciones_independiente.json`, con `commit` y `pines`
en el `cache_meta`). Cada archivo se versiona con su SHA-256, declarado en
`evaluation/data/campana/README.md`, que indica además qué ruta ocupa cada uno y cuál es
la referencia in-sample (`classifier_version`, `commit_in_sample` y `pines_in_sample`).
Los protocolos están en `docs/campana-medicion/runbook-campana-contrabalanceada.md` y
`docs/campana-medicion/runbook-corpus-independiente.md`. Ninguno de estos artefactos
reemplaza ni modifica `data/corpus_evaluacion_pseudonimizado.json`,
`data/corpus_resultados*.json`, `evaluation/predicciones.json` ni `evaluation/report.md`.

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
