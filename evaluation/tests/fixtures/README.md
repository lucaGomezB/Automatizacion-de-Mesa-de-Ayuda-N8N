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

## Contenido de los fixtures del análisis de campaña (c-167) — SINTÉTICO

**AVISO: Todos los archivos de esta sección son SINTÉTICOS.** No contienen etiquetas de personas reales ni datos de campo, y NO son los datos de la campaña (esos se versionan en `evaluation/data/campana/`). Existen solo para los tests de `evaluation/kappa.py`, `evaluation/campana.py` y `evaluation/analisis_campana.py` (`tests/test_fixtures_campana.py`, `test_kappa.py`, `test_campana.py` y `test_analisis_campana.py`). Respetan los contratos que c-167 consume: C1 (planilla de etiquetado, c-168), C2 (registro de sujetos), C5 (export de intervención, c-165), C6 (plan de campaña, c-166) y C9 (predicciones del corpus independiente, c-166). Los comparte el módulo auxiliar `tests/helpers_campana.py`. El corpus se carga siempre desde una copia en `tmp_path` (`cargar_corpus` puede reescribir `metadata.total_casos`).

- `corpus_campana.json`: 24 casos `S01`..`S24` con los cinco sectores canónicos y algunos `sectores_adicionales`. `tiempo_automatizado_s` vale 20,0 en 22 casos y es `null` en `S23` y `S24`; `tiempo_manual_s` es siempre `null`. Hace de copia de campaña (para el tiempo de registro automatizado) y de corpus de ajuste (para `verificar_no_solape` y la referencia `consenso_original`).
- `plan_campana.csv`: plan de c-166 sobre esos 24 casos, tal como lo escribe `generar_plan_campana(ids, "aleatorio", 167)` (columnas `id_caso,posicion,mitad,brazo_primero,modo,seed`): 6 casos por condición y por mitad. El orden por `posicion` no coincide con el de los ids.
- `plantilla_etiquetado.csv`: planilla de siete columnas de C1 con las dos tareas juntas (los tests la parten por `tarea` y cada mitad valida con `validar_doble_etiquetado`).
  - `doble_etiquetado`: `E1` y `E2` sobre los 24 casos, 20 concordantes y 4 discordantes (`S04`, `S11`, `S17`, `S21`). En `S07` los adicionales de `E1` y `E2` difieren (la intersección es vacía) y en `S08` y `S15` el consenso nuevo difiere del `sector_asignado` original. `E2` no informa `inicio`.
  - `brazo_manual`: `O1` etiqueta `S01`..`S18` y `O2` etiqueta `S07`..`S24` (12 casos compartidos y 6 exclusivos de cada operador), con `inicio` y `timestamp` en todas las filas (zona `-03:00`). Cada operador sigue el orden del runbook de c-166 salvo `O2`, que invierte `S12` y `S19` (dos desvíos). Las duraciones están construidas para que `O1` tenga un efecto de condición marcado (los casos con `brazo_primero = manual` tardan unos 40 s más) y `O2` ningún efecto. Las filas están ordenadas por `id_caso` y no por `inicio`.
- `registro_sujetos.csv`: C2 válido (`alias,rol,persona`): `E1`/`E2` etiquetadores, `O1`/`O2` operadores, `AN1`/`AN2` analistas originales y `AU1`/`AU2` autores, cada uno con una persona `P1`..`P8` distinta.
- `registro_sujetos_solape.csv`: igual que el anterior, pero `E2` es la persona `P3`, la misma que `O1`: una misma persona con los roles `etiquetador` y `operador` bajo dos alias.
- `intervenciones.csv`: export C5 con solo filas intervenidas (7 filas, 5 casos): orígenes `gate`, `muestreo` y `rederivacion`, con y sin `cambio_sector`, un caso (`S13`) con dos intervenciones de origen distinto, una fila con `id_caso` vacío (no vinculable) y una con `duracion_s` vacío (`S16`, sin inicio). `actor_alias` es un valor arbitrario de 12 hexadecimales.
- `predicciones_in_sample.json`: caché de predicciones como el de v9 (`cache_meta` con `corpus_hash`, `corpus_count`, `classifier_version` = `hybrid-v3` y `generated_at`; sin `commit` ni `pines`) sobre los 24 casos, con las tres etapas de la cascada (8 `deterministic`, 12 `gemini`, 4 `fallback`).
- `corpus_independiente.json`: 12 casos `I001`..`I012` (prefijo `I`), con descripciones distintas de las de `corpus_campana.json`.
- `predicciones_independiente.json`: caché del corpus independiente (`cache_meta` con `classifier_version` = `hybrid-v3`, `commit` y `pines` = `{"google_genai": "2.34.0", "modelo": "gemini-3.6-flash"}`) con las tres etapas.
- `predicciones_independiente_pines_distintos.json`: igual al anterior pero con otro `modelo` en los `pines` (`gemini-3.5-flash`).
- `predicciones_independiente_version_distinta.json`: igual a `predicciones_independiente.json` pero con `classifier_version` = `hybrid-v4`.
- `corpus_independiente_solape.json`: `corpus_independiente.json` con la descripción de `I012` copiada de la del caso `S05` de `corpus_campana.json` (un solape que `verificar_no_solape` debe rechazar).

Valores de la validación fuera de muestra de los fixtures (en la campaña real salen del README de `evaluation/data/campana/` y de `openspec/config.yaml`): `pines_in_sample` = `{"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}` (el `google_genai` es un rango declarado, no una versión instalada) y pin vigente de `google-genai` = `>=2.33,<3`. Las demás variantes que necesitan los tests (versión instalada fuera del rango, `commit` distinto, etc.) las derivan ellos mismos en `tmp_path`.
