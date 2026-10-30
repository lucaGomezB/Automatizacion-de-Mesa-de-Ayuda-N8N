## Why

El CLI de análisis de campaña `evaluation/analisis_campana.py` lee de una sola carpeta
`--entrada` ocho nombres canónicos fijos. Dos de ellos **no los produce ningún runbook de la
campaña**, así que el paso de análisis de la FASE 52 fallaría al ejecutarse (la campaña aún no
corrió, por lo que no hay daño en producción; el defecto es de completitud de la
instrumentación). Evidencia:

- GAP 1 — `plantilla_etiquetado.csv`: el CLI la define en `evaluation/analisis_campana.py:55`
  (`NOMBRE_PLANILLA = "plantilla_etiquetado.csv"`) y la lee de `--entrada` en
  `evaluation/analisis_campana.py:152`, esperando la hoja C1 con las filas de ambas tareas
  (`tarea = doble_etiquetado` y `tarea = brazo_manual`). Los runbooks versionan **dos** archivos
  C1 separados: `evaluation/data/campana/doble_etiquetado.csv`
  (`docs/campana-medicion/runbook-doble-etiquetado.md:215-250`, sección 7) y
  `evaluation/data/campana/brazo_manual.csv`
  (`docs/campana-medicion/runbook-brazo-manual-e-intervencion.md:257-265`, sección 4.3). Ningún
  paso los une. El contrato C1 de c-167 ya declara la entrada como una única hoja
  `plantilla_etiquetado.csv` (`openspec/changes/archive/2026-10-30-c-167-.../design.md:42`).
- GAP 2 — `predicciones_in_sample.json`: el CLI la define en
  `evaluation/analisis_campana.py:60` (`NOMBRE_PREDICCIONES_IN_SAMPLE = "predicciones_in_sample.json"`)
  y la lee de `--entrada` en `evaluation/analisis_campana.py:157`. Ningún runbook la produce. La
  referencia in-sample es el cache congelado
  `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`
  (`evaluation/data/campana/README.md:106-108`, "Referencia in-sample").

El README del análisis ya declara ambas entradas como esperadas
(`evaluation/data/campana/analisis/README.md:37` y `:42`) sin que exista el paso que las
materializa.

## What Changes

- Nuevo módulo/CLI puro `evaluation/preparar_entradas_analisis.py` (offline, TDD) que ensambla
  las dos entradas que faltan en `evaluation/data/campana/`:
  - `plantilla_etiquetado.csv` = unión de `doble_etiquetado.csv` + `brazo_manual.csv` (un único
    encabezado C1, LF), re-validada con `evaluation/doble_etiquetado.py::validar_doble_etiquetado`
    por tarea.
  - `predicciones_in_sample.json` = copia byte a byte del cache congelado
    `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` (fuente de solo lectura; nunca
    se regenera v9).
- El módulo imprime el SHA-256 de cada salida, se niega a sobrescribir artefactos congelados y no
  se puede saltar en silencio (es el paso documentado).
- Actualización de los runbooks afectados, `evaluation/data/campana/README.md` (tabla SHA-256 +
  procedencia) y `evaluation/data/campana/analisis/README.md` para hacer explícita la procedencia
  de las dos entradas.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `evaluation-campaign-instrumentation`: se agregan requisitos (ECM-011..ECM-013) para que la
  campaña produzca de forma reproducible y verificable las dos entradas que consume el CLI de
  análisis, con su SHA-256 declarado y protección de los artefactos congelados.

## Impact

- **Nuevo**: `evaluation/preparar_entradas_analisis.py`, `evaluation/tests/test_preparar_entradas_analisis.py`.
- **Datos versionados (después de la campaña)**: `evaluation/data/campana/plantilla_etiquetado.csv`,
  `evaluation/data/campana/predicciones_in_sample.json` (+ SHA-256 en su README).
- **Docs**: `docs/campana-medicion/runbook-doble-etiquetado.md`,
  `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`,
  `evaluation/data/campana/README.md`, `evaluation/data/campana/analisis/README.md`.
- **No tocado**: `evaluation/analisis_campana.py` (c-167, ya verificado), ningún change archivado
  c-165..c-168, c-169, ni `App/**` / `n8n/**`.
- Dependencias: ninguna nueva (stdlib + `evaluation.doble_etiquetado`).
