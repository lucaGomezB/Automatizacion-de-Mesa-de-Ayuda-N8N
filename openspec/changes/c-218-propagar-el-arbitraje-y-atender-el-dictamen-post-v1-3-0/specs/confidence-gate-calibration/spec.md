## ADDED Requirements

### Requirement: CAL-007 — Complemento descriptivo sobre el corpus arbitrado

Sobre los casos resueltos por la etapa Gemini en `predicciones_arbitrado.json` (corpus arbitrado
completo), el análisis de c-218 SHALL calcular, reutilizando las funciones puras de
`evaluation/calibracion_gate.py`, la exactitud, la confianza media, la sobreconfianza, el ECE con
10 bandas de igual ancho, el puntaje de Brier y el AUROC con intervalo bootstrap percentil por caso
(2000 remuestreos, semilla fija), y la descripción del barrido de los umbrales candidatos
(casos aceptados y exactitud selectiva). Antes de calcular SHALL reproducir, con las mismas
funciones, el ECE `0,1715` y el Brier `0,1935` de los `34` casos con consenso. El resultado SHALL
presentarse como complemento descriptivo junto a la fila de `34` casos, que se conserva, y MUST
NOT seleccionar, confirmar ni modificar un umbral: la regla prerregistrada elige solo con los `200`
casos de ajuste. La tesis SHALL declarar junto al análisis que la confianza de Gemini varió entre
corridas en casos comunes, con la cantidad que informe el control de reproducibilidad.

#### Scenario: Fila descriptiva sin re-elección del umbral

- **WHEN** se lee `tab:calibracion-gate`
- **THEN** figuran la fila dentro de la muestra, la de `34` casos con consenso y una fila descriptiva del corpus arbitrado
- **AND** la nota dice que el umbral no se eligió con datos fuera de la muestra

#### Scenario: Reutilización validada

- **WHEN** el análisis aplica las funciones de `calibracion_gate.py` a los `34` casos con consenso
- **THEN** reproduce el ECE `0,1715` y el Brier `0,1935`
- **AND** si no los reproduce, termina con error sin escribir salidas

#### Scenario: Inestabilidad declarada

- **WHEN** se lee el análisis de calibración en `07-resultados.tex`
- **THEN** se declara cuántos casos de la etapa Gemini cambiaron de confianza entre las dos corridas fuera de muestra
