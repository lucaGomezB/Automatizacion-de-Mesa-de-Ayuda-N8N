## MODIFIED Requirements

### Requirement: Runner de evaluación sobre el corpus

El framework SHALL proveer un runner que, dado un corpus, invoque el clasificador híbrido caso por caso recolectando para cada uno el sector predicho principal, los sectores adicionales predichos, la confianza y la etapa del pipeline (`deterministic`, `gemini` o `fallback`), y produzca las métricas de clasificación multietiqueta y un reporte en `evaluation/report.md`. El runner MUST ser ejecutable como una operación de un solo comando cuando el corpus real esté presente en `data/corpus_evaluacion_pseudonimizado.json`, y MUST aislar la recolección de predicciones del cálculo de métricas (inyección del clasificador) para permitir pruebas con un clasificador simulado. El runner MUST negarse a invocar el clasificador real sin confirmación explícita del operador, abortando con un error claro cuando la confirmación está ausente. La documentación del runner (`evaluation/README.md`) MUST describir ese gate de corrida paga junto al comando único de corrida y a la configuración de `GEMINI_API_KEY`: MUST nombrar las dos formas de confirmación (`--confirm-paid` y `EVALUATION_CONFIRM_PAID=1`), MUST indicar que sin confirmación la corrida aborta sin invocar el clasificador real, y MUST indicar que al confirmar se imprime una estimación de costo.

#### Scenario: Recolección de predicciones por caso

- **WHEN** el runner procesa un corpus con un clasificador inyectado
- **THEN** por cada caso del corpus se registra exactamente una predicción con sector predicho, sectores adicionales, confianza y etapa

#### Scenario: Generación del reporte de métricas

- **WHEN** el runner finaliza el procesamiento de un corpus
- **THEN** escribe `evaluation/report.md` con la matriz de confusión 5x5, la exactitud primaria, el subconjunto exacto, la pérdida de Hamming, los F1 micro y macro y la tabla por sector

#### Scenario: Corpus real ausente no rompe el framework

- **WHEN** se ejecuta el runner y el archivo `data/corpus_evaluacion_pseudonimizado.json` no está presente
- **THEN** el runner termina con un error claro indicando que debe colocarse el corpus real, sin inventar datos ni producir un reporte con resultados ficticios

#### Scenario: Gate de corrida paga documentado junto al comando

- **WHEN** se lee la documentación del runner en `evaluation/README.md`
- **THEN** el gate de corrida paga se describe junto al comando único de corrida y a la configuración de `GEMINI_API_KEY`
- **AND** nombra `--confirm-paid` y `EVALUATION_CONFIRM_PAID=1` como las formas de confirmación
- **AND** indica que sin confirmación la corrida aborta sin invocar el clasificador real y que al confirmar se imprime una estimación de costo
