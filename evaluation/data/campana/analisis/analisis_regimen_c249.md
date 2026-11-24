# Recomputo por regimen y de la sonda (c-249)

Salida generada por `analisis_regimen_c249.py`. Analisis de solo lectura sobre los
artefactos versionados; no reclasifica ni modifica el corpus.

## Exactitud estricta por regimen

| Regimen | Aciertos | Total | Proporcion | IC 95 % |
|---|---|---|---|---|
| Regimen (a): correo y formulario web | 94 | 119 | 0.7899 | [0.7082; 0.8535] |
| Regimen (b): telefonia | 53 | 81 | 0.6543 | [0.5459; 0.7488] |

## Exactitud estricta por canal

| Canal | Aciertos | Total | Proporcion | IC 95 % |
|---|---|---|---|---|
| correo electrónico | 51 | 66 | 0.7727 | [0.6583; 0.8571] |
| formulario web | 43 | 53 | 0.8113 | [0.6864; 0.8941] |
| llamada telefónica | 53 | 81 | 0.6543 | [0.5459; 0.7488] |

## Intervencion manual sobre la derivacion

- Cambios de derivacion: 25 sobre 147 revisados.
- Sobre los 200 casos (regla prefijada): 0.1250 [0.0861; 0.1780].
- Sobre los 147 revisados (denominador post hoc): 0.1701 [0.1179; 0.2390].
- Binomial unilateral frente a 0.15 (H1: p > 0.15): p = 0.279583.

## Sonda de latencia del nivel 5 de N8N

- Corrida original: p95 = 3660.3724 ms.
- Corrida ampliada: p95 = 7545.7313 ms.
- Subconjunto deterministico de la ampliada: p95 = 5024.6799 ms.
- Techo de la regla: 5000.0 ms.

## Entradas

| Archivo | SHA-256 |
|---|---|
| `data/corpus_evaluacion_pseudonimizado.json` | `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb` |
| `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` | `89cf956e82f660dd8675a2d23b7b4d17efd62da542c0ba35bea28e0e54572ede` |
| `evaluation/data/campana/intervenciones.csv` | `eccc094d46d5ad301296428885114e298f52efb0666be4f61c2e6a266d340ba3` |
| `evaluation/evidence/load_test_inferencia_2026-11-17.json` | `08da89c6e3b21747afdf970112a3c18303b5567f6df0528027ea14f42e020c28` |
| `evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json` | `ef8c7ea698588e7c39d546e7c4ce1255550300804a8389319b53cfb5939219d9` |
