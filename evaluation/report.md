# Reporte de Evaluación del Clasificador (multietiqueta)

**Total de casos evaluados:** 200

## Etapas del pipeline

| Etapa | Casos |
|-------|-------|
| Deterministic | 131 |
| Gemini | 69 |
| Fallback | 0 |

## Exactitud

Definiciones (design D5): igualdad estricta del sector principal y
pertenencia del sector asignado al conjunto predicho.

- **Exactitud (estricta):** 0.7350 (73.5%)
- **Aciertos (estrictos):** 147 / 200
- **IC Wilson 95% (estricto):** [0.6698, 0.7913]
- **Exactitud (pertenencia):** 0.7350 (73.5%)
- **Aciertos (pertenencia):** 147 / 200
- **IC Wilson 95% (pertenencia):** [0.6698, 0.7913]

## Matriz de Confusión (primaria 5x5)

Filas = sector asignado | Columnas = sector predicho principal

| Asignado \ Predicho | Seguridad Informatica | Soporte Tecnico Hardware | Soporte Tecnico Software | Bases de Datos | Sistemas |
|---|---|---|---|---|---|
| **Seguridad Informatica** | 15 | 2 | 11 | 2 | 1 |
| **Soporte Tecnico Hardware** | 1 | 77 | 3 | 0 | 4 |
| **Soporte Tecnico Software** | 0 | 11 | 48 | 1 | 7 |
| **Bases de Datos** | 0 | 0 | 1 | 0 | 0 |
| **Sistemas** | 2 | 0 | 5 | 2 | 7 |

## Métricas por sector (one-vs-rest)

| Sector | Precisión | Sensibilidad | F1 | Soporte |
|--------|-----------|--------------|-----|---------|
| Seguridad Informatica | 0.8333 | 0.4839 | 0.6122 | 31 |
| Soporte Tecnico Hardware | 0.8556 | 0.9059 | 0.8800 | 85 |
| Soporte Tecnico Software | 0.7059 | 0.7164 | 0.7111 | 67 |
| Bases de Datos | 0.0000 | 0.0000 | 0.0000 | 1 |
| Sistemas | 0.3684 | 0.4375 | 0.4000 | 16 |

## Métricas de conjunto

- **Subset accuracy:** 0.4300
- **Hamming loss:** 0.3586
- **Micro-F1:** 0.6654
- **Macro-F1:** 0.5207
- **Jaccard (IoU) promedio:** 0.6414
## Tiempos

Análisis sobre los pares (tiempo_manual_s, tiempo_automatizado_s) del corpus cargado.
Pares válidos: 200; excluidos por tiempo nulo: 0.

### Normalidad (Shapiro-Wilk)

| Conjunto | n | W | p |
|---|---|---|---|
| Manual | 200 | 0.8031 | 3.71e-15 |
| Automatizado | 200 | 0.9022 | 3.47e-10 |
| Diferencias | 200 | 0.8225 | 2.37e-14 |

### Prueba de Wilcoxon (rangos con signo)

Convención: W = min(T+, T−) (dos colas); tamaño del efecto rank-biserial r = (T+ − T−) / (n(n+1)/2).

| n | W | T+ | T− | p | r |
|---|---|---|---|---|---|
| 200 | 363.0000 | 19737.0000 | 363.0000 | 3.08e-32 | 0.9639 |

### Reducción de tiempos

`tiempo_manual_s` se midió en vivo con redondeo al alza (sesgo sistemático), por lo
que su valor real no es mayor que el reportado. Se reporta la reducción sobre los
valores reportados y una cota conservadora que descuenta 1 s al manual por caso.

| Métrica | Reportada (s) | Conservadora (s) |
|---|---|---|
| Reducción media | 43.82 | 42.82 |
| Reducción mediana | 31.57 | 30.57 |

- Pares en que el flujo automatizado no fue más rápido (invertidos/empatados): 12.
- Casos excluidos por tiempo nulo: 0.

### Desglose por canal

Segmentación por el valor crudo de `canal_origen` del corpus.

| Canal | Pares válidos | W | T+ | T− | p | r |
|---|---|---|---|---|---|---|
| llamada telefónica | 81 | 0.0000 | 3321.0000 | 0.0000 | 5.36e-15 | 1.0000 |
| correo electrónico | 66 | 189.0000 | 2022.0000 | 189.0000 | 4.78e-09 | 0.8290 |
| formulario web | 53 | 0.0000 | 1431.0000 | 0.0000 | 2.39e-10 | 1.0000 |

- **SHA-256 del corpus:** `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`

---
_Generado automáticamente por `evaluation/run_evaluation.py`_