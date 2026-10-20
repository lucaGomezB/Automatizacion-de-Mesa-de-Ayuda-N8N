# Delta for evaluation-framework

## ADDED Requirements

### Requirement: Divulgacion del redondeo de la medicion manual y analisis de sensibilidad

La evaluacion de tiempos SHALL declarar la naturaleza de la medicion de
`tiempo_manual_s` (medicion real en vivo con redondeo hacia arriba, sesgo
sistematico) y SHALL reportar, junto a la reduccion calculada sobre los valores
reportados, una cota inferior conservadora de sensibilidad. El analisis de
tiempos SHALL reportar el numero de pares en que el flujo automatizado no fue mas
rapido, y el estadistico de Wilcoxon SHALL usar la correccion por empates en
lugar de asumir ausencia de pares invertidos.

#### Scenario: Redondeo y sensibilidad declarados en el reporte

- **WHEN** se presenta la seccion de tiempos de la evaluacion o `evaluation/report.md`
- **THEN** se declara que `tiempo_manual_s` es una medicion redondeada al alza
- **AND** se reporta la reduccion conservadora ademas de la reduccion sobre los valores reportados

#### Scenario: Pares invertidos visibles

- **WHEN** se comparan los tiempos pareados manual y automatizado
- **THEN** se reporta la cantidad de pares en que el flujo automatizado no fue mas rapido (12 de 200)
- **AND** el estadistico de Wilcoxon reportado no asume cero pares invertidos

### Requirement: Divulgacion de la distribucion de etapas del pipeline (incluida fallback)

La evaluacion SHALL reportar la distribucion de casos por etapa del pipeline como
deterministic 131/200 (65,5 %), Gemini 69/200 (34,5 %) y fallback 0/200, e SHALL
documentar la etapa fallback y el orden deterministic -> Gemini -> fallback. La
documentacion de evaluacion SHALL NOT reportar el reparto stale "~62 % / 38 %".

#### Scenario: Etapas y fallback en el reporte

- **WHEN** se presenta `evaluation/report.md` o la seccion de etapas del pipeline
- **THEN** reporta deterministic 131, Gemini 69 y fallback 0
- **AND** documenta el orden deterministic -> Gemini -> fallback

### Requirement: Trazabilidad del corpus real en la documentacion de evaluacion

La documentacion de evaluacion SHALL declarar que el corpus real reside en
`data/corpus_evaluacion_pseudonimizado.json` (JSON, pseudonimizado y versionado)
y SHALL NOT declarar un corpus en `evaluation/data/` ni un esquema CSV de siete
columnas como ubicacion vigente del corpus.

#### Scenario: evaluacion/data no aloja el corpus

- **WHEN** se leen `evaluation/README.md` y `evaluation/data/README.md`
- **THEN** remiten al corpus real en `data/corpus_evaluacion_pseudonimizado.json`
- **AND** no declaran que el corpus resida en `evaluation/data/` como CSV
