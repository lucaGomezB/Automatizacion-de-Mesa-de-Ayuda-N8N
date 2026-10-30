# Fixtures de prueba — SINTÉTICO

**AVISO: Este corpus es SINTÉTICO y fue creado únicamente para los tests automatizados.**

NO es el corpus de evaluación de la tesis (que se encuentra en
`data/corpus_evaluacion_pseudonimizado.json` y no está trackeado en git por privacidad).

## Contenido de `corpus_fixture.json`

- Esquema JSON (`schema_version` / `metadata` / `casos`) con 9 casos.
- Etiquetas canónicas del vocabulario de 5 sectores (sin tildes):
  `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`,
  `Bases de Datos`, `Sistemas`.
- Cada caso incluye `sectores_adicionales` y los tiempos `tiempo_manual_s` /
  `tiempo_automatizado_s`.
- Los textos de descripción son ilustrativos y no provienen de datos reales.

## Contenido de `campana/corpus_independiente_fixture.json` (c-166) — SINTÉTICO

**AVISO: Este corpus es SINTÉTICO** y existe solo para los tests de `evaluation/no_solape.py` y de
los flags `--corpus`/`--predicciones`/`--reporte` de `run_evaluation.py`.

- 4 casos con ids `I001`..`I004` (prefijo `I` del corpus independiente), con sectores
  canónicos y los dos tiempos en `null`.
- Sus descripciones no coinciden con las de `corpus_fixture.json` (ni siquiera con
  similitud Jaccard alta): es un candidato **disjunto** del corpus de ajuste de prueba.
- Los tests derivan de él, en `tmp_path`, los candidatos con una infracción (descripción
  repetida con otro id, id sin prefijo).

## Contenido de `campana/doble_etiquetado_fixture.csv` (c-168) — SINTÉTICO

**AVISO: Esta planilla es SINTÉTICA.** No contiene etiquetas de personas reales ni
datos de campo, y NO es la tabla primaria del doble etiquetado (esa, cuando exista,
se versiona en `evaluation/data/campana/doble_etiquetado.csv`).

- Esquema de siete columnas de `evaluation/data/plantilla_etiquetado.csv`, con
  `tarea = doble_etiquetado`.
- 18 filas: los 9 casos de `corpus_fixture.json` (ids `1..9`) x `E1` y `E2`.
- Incluye un caso discordante (`6`), un caso con adicionales `Sistemas|Bases de Datos`,
  casos con adicionales vacíos y filas con `inicio` informado y vacío.
- Los tests de `test_doble_etiquetado.py` lo usan como planilla válida de base y
  derivan de él las planillas con una ofensa.

## Contenido de `campana/corpus_brazo_manual_fixture.json`, `campana/plan_campana_brazo_manual_fixture.csv` y `campana/brazo_manual_fixture.csv` (c-165) — SINTÉTICO

**AVISO: Estos tres archivos son SINTÉTICOS.** No contienen etiquetas de personas reales ni
datos de campo, y NO son la planilla del brazo manual de la campaña (esa, cuando exista, se
versiona en `evaluation/data/campana/` y se valida con
`python -m evaluation.doble_etiquetado --tarea brazo_manual`). Existen solo para los tests de
`evaluation/brazo_manual.py` (`tests/test_brazo_manual.py`).

- `corpus_brazo_manual_fixture.json`: 6 casos con ids `R001`..`R006`, sectores canónicos y los
  dos tiempos en `null`. Las descripciones empiezan con "Sintetico:" y no provienen de datos
  reales. Es disjunto en ids del corpus de `corpus_fixture.json` (ids `1..9`).
- `plan_campana_brazo_manual_fixture.csv`: plan de c-166 sobre esos 6 casos, tal como lo escribe
  `python -m evaluation.plan_campana generar --modo aleatorio --seed 4` (columnas
  `id_caso,posicion,mitad,brazo_primero,modo,seed`). El orden por `posicion` no coincide con el
  orden de los ids, para que un test no pase por casualidad si ordena por `id_caso`.
- `brazo_manual_fixture.csv`: planilla de siete columnas de c-168 con `tarea = brazo_manual`.
  `O1` clasifica los 3 casos de la mitad 1 y `O2` los 3 de la mitad 2, y `R002` lo clasifican
  ambos (doble cobertura): 7 filas. Cada operador sigue el orden que el runbook de c-166 le pide
  al brazo manual (mitad por mitad y, dentro de cada una, primero los casos `manual`-primero y
  después los `automatizado`-primero), de modo que la posición real coincide con la planeada y no
  hay desvíos. Las filas están ordenadas por `id_caso` y no por `inicio`, a propósito, y todos los
  instantes llevan zona `-03:00`.
- Los tests de `test_brazo_manual.py` los usan como base válida (el corpus se copia a `tmp_path`
  antes de cargarlo, porque `cargar_corpus` puede reescribir `metadata.total_casos`) y derivan de
  ellos las planillas con un caso sin operador, un registro duplicado, una fila sin `inicio` o un
  desvío de posición.
