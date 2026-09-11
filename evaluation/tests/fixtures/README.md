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