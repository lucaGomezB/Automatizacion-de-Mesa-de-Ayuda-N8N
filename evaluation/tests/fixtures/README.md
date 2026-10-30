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
