## Why

La historia del repositorio se saneó (los SHAs de commit se reescribieron). El commit `ed4b386`
remapeó algunas citas pero omitió deliberadamente `auditorias/`, los `.txt` extraídos de la tesis y
`evaluation/` (código, tests y datos), dejando 69 citas con SHAs de la historia previa al saneo en 13
archivos. Además, `verificar_matriz_trazabilidad.py` reporta 4 fallas. Ambos son defectos de
integridad de la evidencia de la tesis: un SHA no alcanzable desde `HEAD` es evidencia falsa, y un
verificador en rojo deja el registro de trazabilidad inconsistente con su propio texto.

## What Changes

- Remapear los 14 SHAs de commit distintos de la historia previa al saneo a sus contrapartes de la
  historia saneada, en 13 archivos (69 ocurrencias): 6 dictámenes de `auditorias/`, 2 `.txt`
  extraídos de la tesis y 5 artefactos de `evaluation/` (código, tests y datos). Los SHAs de blob NO
  se remapean.
- Corregir las 4 fallas del verificador en `docs/Tesis/Correcciones/dictamen-correcciones.md`:
  alinear 3 filas de matriz (c-188 A2, c-190 Res. 11.3, c-195 C1/13) con el retexto de c-197 o
  marcarlas `SUPERADA por c-197`; y agregar una matriz de 7 columnas a la sección de c-197, que hoy
  no la tiene.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `tesis-document`: se modifica el requirement del verificador de la matriz de trazabilidad para
  exigir `fallas: 0` tras alinear las filas afectadas por c-197 y dotar de matriz a su sección; y se
  agrega un requirement que exige que las citas de commit de los dictámenes de `auditorias/` y de los
  `.txt` extraídos resuelvan a la historia saneada (ancestras de `HEAD`), sin tocar los SHAs de blob.
- `evaluation-framework`: se modifica el requirement de procedencia del análisis de sensibilidad para
  exigir que los SHAs de commit citados en `procedencia.json`, en `sensibilidad_ajustes.py` y en sus
  tests pertenezcan a la historia saneada, coherentes con la advertencia metodológica que ya cita los
  SHAs nuevos (`c8112d2`, `27f8d8c`, `bf5e099`).

## Impact

- Docs: `auditorias/*.md` (6), `docs/Tesis/v10 (IA)/tesis_*.txt` (2), `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- Código/tests/datos: `evaluation/sensibilidad_ajustes.py`, `evaluation/tests/test_sensibilidad_ajustes.py`,
  `evaluation/tests/test_sensibilidad_corpus.py`, `evaluation/tests/test_campana.py`,
  `evaluation/data/sensibilidad_ajustes/procedencia.json`.
- Specs: `openspec/specs/tesis-document/spec.md` y `openspec/specs/evaluation-framework/spec.md` (vía delta).
- Sin cambio de runtime. Fuera de alcance: `App/`, `n8n/`, las fuentes `.tex` (ya remapeadas por
  `ed4b386`), `main.pdf`, los SHAs de blob y cualquier recompilación.
