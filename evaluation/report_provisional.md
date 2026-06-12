> **ADVERTENCIA: CORPUS SINTETICO PROVISIONAL**
>
> Este reporte fue generado con el corpus sintetico `corpus_sintetico_provisional.csv`
> (200 casos generados por Claude para validar el pipeline de evaluacion).
> Los numeros aqui reportados **NO son validos para el Capitulo 7** de la tesis.
> El Capitulo 7 requiere el corpus real pseudonimizado (`corpus_evaluacion_pseudonimizado.csv`).
>
> Proposito de esta corrida: validacion y calibracion del pipeline de evaluacion.

# Reporte de Evaluación del Clasificador

**Total de casos evaluados:** 200

## Etapas del pipeline

| Etapa | Casos |
|-------|-------|
| Deterministic | 101 |
| Gemini | 4 |
| Fallback | 95 |

## Exactitud Global

- **Exactitud:** 0.6300 (63.0%)
- **Aciertos:** 126 / 200
- **IC Wilson 95%:** [0.5612, 0.6939]

## Matriz de Confusión

Filas = categoría real | Columnas = categoría predicha

| Real \ Predicho | Sistemas | Operaciones | Soporte Técnico |
|---|---|---|---|
| **Sistemas** | 78 | 0 | 4 |
| **Operaciones** | 42 | 19 | 3 |
| **Soporte Técnico** | 21 | 4 | 29 |

## Métricas por Clase

| Clase | Precisión | Sensibilidad | F1 |
|-------|-----------|--------------|-----|
| Sistemas | 0.5532 | 0.9512 | 0.6996 |
| Operaciones | 0.8261 | 0.2969 | 0.4368 |
| Soporte Técnico | 0.8056 | 0.5370 | 0.6444 |

**F1 Macro:** 0.5936

---
_Generado automáticamente por `evaluation/run_evaluation.py`_