## Why

El dictamen CONEAU v1.3.0 califico el criterio 4 (metodologia, peso 20) con 7/10 y fue
explicito: "Un puntaje mayor en el criterio 4 exige evidencia nueva (arbitraje de los 47
discordantes, linea de base), no redaccion." Una de las limitaciones listadas es "Sin linea
de base. No hay comparacion con el modelo de lenguaje solo ni con un clasificador supervisado
clasico." El arbitraje de los discordantes lo cubre c-206; esta change cubre la mitad de la
linea de base: el desarrollo de un clasificador supervisado clasico reproducible. La
evidencia es ADITIVA: no cambia ningun numero canonico ni el clasificador de produccion.

## What Changes

- **Nuevo modulo** `evaluation/linea_de_base.py`: clasificador supervisado clasico
  (TF-IDF de palabras y caracteres + regresion logistica regularizada de scikit-learn) que
  se entrena con los `200` casos in-sample del corpus de ajuste y predice los `103` casos
  fuera de muestra con referencia por consenso (`E3`/`E4`), el mismo conjunto efectivo que
  usan c-191 y c-205. Semilla fija y ejecucion totalmente offline.
- **Pruebas TDD** en `evaluation/tests/test_linea_de_base.py`: estructura del documento,
  metricas sobre entradas sinteticas, soporte por clase, determinismo byte a byte y
  ausencia de red/Gemini/API paga.
- **Contrato de metricas**: exactitud estricta, exactitud laxa, macro-F1, *balanced
  accuracy* y F1 por clase con soporte, reutilizando las funciones puras de
  `evaluation/metrics.py` para que las cifras sean comparables con las de c-205.
- **Sin medicion final**: esta change entrega el script y sus pruebas. La ejecucion, los
  artefactos versionados y la comparacion con el hibrido son c-210.

## Capabilities

### New Capabilities

- `evaluation-linea-de-base-clasica`: desarrollo reproducible de un clasificador supervisado
  clasico como linea de base, con metricas comparables, determinismo y ejecucion offline.

### Modified Capabilities

(none)

## Impact

- Nuevo: `evaluation/linea_de_base.py` y `evaluation/tests/test_linea_de_base.py`.
- Sin cambios en `App/`, `n8n/`, el clasificador de produccion, los corpus congelados, los
  numeros canonicos ni la tesis. Sin red, sin Gemini y sin API paga.
- Dependencia ya declarada en `evaluation/requirements.txt` (`scikit-learn>=1.4`); no se
  agrega ninguna dependencia nueva. Verificado en el entorno: `scikit-learn 1.9.1`.
- Gobernanza: LOW (herramienta de evaluacion de solo lectura, sin datos productivos).
- Non-goals: no se ejecuta la medicion (c-210), no se arbitran los `47` discordantes (c-206),
  no se edita la tesis ni el memo canonico.
