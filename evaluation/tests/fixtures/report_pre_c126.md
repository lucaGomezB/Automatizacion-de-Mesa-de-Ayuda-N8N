# Reporte de Evaluación del Clasificador (multietiqueta)

**Total de casos evaluados:** 9

## Etapas del pipeline

| Etapa | Casos |
|-------|-------|
| Deterministic | 5 |
| Gemini | 4 |
| Fallback | 0 |

## Exactitud

Definiciones (design D5): igualdad estricta del sector principal y
pertenencia del sector asignado al conjunto predicho.

- **Exactitud (estricta):** 0.6667 (66.7%)
- **Aciertos (estrictos):** 6 / 9
- **IC Wilson 95% (estricto):** [0.3542, 0.8794]
- **Exactitud (pertenencia):** 0.6667 (66.7%)
- **Aciertos (pertenencia):** 6 / 9
- **IC Wilson 95% (pertenencia):** [0.3542, 0.8794]

## Matriz de Confusión (primaria 5x5)

Filas = sector asignado | Columnas = sector predicho principal

| Asignado \ Predicho | Seguridad Informatica | Soporte Tecnico Hardware | Soporte Tecnico Software | Bases de Datos | Sistemas |
|---|---|---|---|---|---|
| **Seguridad Informatica** | 1 | 0 | 1 | 0 | 0 |
| **Soporte Tecnico Hardware** | 0 | 1 | 0 | 0 | 1 |
| **Soporte Tecnico Software** | 0 | 0 | 1 | 0 | 0 |
| **Bases de Datos** | 0 | 0 | 0 | 2 | 0 |
| **Sistemas** | 0 | 0 | 0 | 1 | 1 |

## Métricas por sector (one-vs-rest)

| Sector | Precisión | Sensibilidad | F1 | Soporte |
|--------|-----------|--------------|-----|---------|
| Seguridad Informatica | 1.0000 | 0.5000 | 0.6667 | 2 |
| Soporte Tecnico Hardware | 1.0000 | 0.5000 | 0.6667 | 2 |
| Soporte Tecnico Software | 0.5000 | 1.0000 | 0.6667 | 1 |
| Bases de Datos | 0.6667 | 1.0000 | 0.8000 | 2 |
| Sistemas | 0.5000 | 0.5000 | 0.5000 | 2 |

## Métricas de conjunto

- **Subset accuracy:** 0.4444
- **Hamming loss:** 0.4074
- **Micro-F1:** 0.6087
- **Macro-F1:** 0.6600
- **Jaccard (IoU) promedio:** 0.5926
## Tiempos

Análisis sobre los pares (tiempo_manual_s, tiempo_automatizado_s) del corpus cargado.
Pares válidos: 9; excluidos por tiempo nulo: 0.

### Normalidad (Shapiro-Wilk)

| Conjunto | n | W | p |
|---|---|---|---|
| Manual | 9 | 0.9902 | 0.996 |
| Automatizado | 9 | 0.9777 | 0.951 |
| Diferencias | 9 | 0.9861 | 0.988 |

### Prueba de Wilcoxon (rangos con signo)

Convención: W = min(T+, T−) (dos colas); tamaño del efecto rank-biserial r = (T+ − T−) / (n(n+1)/2).

| n | W | T+ | T− | p | r |
|---|---|---|---|---|---|
| 9 | 0.0000 | 45.0000 | 0.0000 | 0.00391 | 1.0000 |

### Reducción de tiempos

`tiempo_manual_s` se midió en vivo con redondeo al alza (sesgo sistemático), por lo
que su valor real no es mayor que el reportado. Se reporta la reducción sobre los
valores reportados y una cota conservadora que descuenta 1 s al manual por caso.

| Métrica | Reportada (s) | Conservadora (s) |
|---|---|---|
| Reducción media | 183.67 | 182.67 |
| Reducción mediana | 182.00 | 181.00 |

- Pares en que el flujo automatizado no fue más rápido (invertidos/empatados): 0.
- Casos excluidos por tiempo nulo: 0.

### Desglose por canal

Segmentación por el valor crudo de `canal_origen` del corpus.

| Canal | Pares válidos | W | T+ | T− | p | r |
|---|---|---|---|---|---|---|
| correo | 4 | 0.0000 | 10.0000 | 0.0000 | 0.125 | 1.0000 |
| formulario | 3 | 0.0000 | 6.0000 | 0.0000 | 0.25 | 1.0000 |
| llamada | 2 | 0.0000 | 3.0000 | 0.0000 | 0.5 | 1.0000 |

### Descriptivos global y por canal

Desvío estándar con la convención muestral (divisor n − 1). La reducción relativa es
1 − media(automatizado) / media(manual) (y su análoga con la mediana). "No más
rápidos" cuenta los pares con `automatizado >= manual`.

| Ámbito | n | Manual media (s) | Manual mediana (s) | Manual desvío (s) | Manual mín (s) | Manual máx (s) | Automatizado media (s) | Automatizado mediana (s) | Automatizado desvío (s) | Automatizado mín (s) | Automatizado máx (s) | Reducción de la media (%) | Reducción de la mediana (%) | No más rápidos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Global | 9 | 196.6667 | 195.0000 | 24.3670 | 160.0000 | 240.0000 | 13.0000 | 13.0000 | 1.9365 | 10.0000 | 16.0000 | 93.39 | 93.33 | 0 |
| correo | 4 | 183.7500 | 187.5000 | 17.9699 | 160.0000 | 200.0000 | 12.2500 | 12.5000 | 1.7078 | 10.0000 | 14.0000 | 93.33 | 93.33 | 0 |
| formulario | 3 | 206.6667 | 210.0000 | 15.2753 | 190.0000 | 220.0000 | 14.0000 | 14.0000 | 2.0000 | 12.0000 | 16.0000 | 93.23 | 93.33 | 0 |
| llamada | 2 | 207.5000 | 207.5000 | 45.9619 | 175.0000 | 240.0000 | 13.0000 | 13.0000 | 2.8284 | 11.0000 | 15.0000 | 93.73 | 93.73 | 0 |

### Contraste direccional y tamaño del efecto estandarizado

El p bilateral corresponde a la convención W = min(T+, T−); el p unilateral contrasta
H1: manual > automatizado (`alternative="greater"` sobre manual − automatizado).
d_z = media(d) / desvío(d) con d = manual − automatizado (desvío muestral).
El efecto mínimo detectable (MDE, en escala d_z) usa la aproximación normal
(z_(1−alfa/2) + z_potencia) / raíz(n · ARE) con alfa = 0.05 (bilateral),
potencia = 0.80 y ARE = 1 (sin ajuste) o ARE = 0.864 (cota inferior de la eficiencia de la prueba de rangos frente a la t pareada).

| Ámbito | n | p bilateral | p unilateral | d_z | MDE (ARE = 1) | MDE (ARE = 0.864) |
|---|---|---|---|---|---|---|
| Global | 9 | 0.00391 | 0.00195 | 8.1329 | 0.9339 | 1.0047 |
| correo | 4 | 0.125 | 0.0625 | 10.5352 | 1.4008 | 1.5070 |
| formulario | 3 | 0.25 | 0.125 | 14.4681 | 1.6175 | 1.7401 |
| llamada | 2 | 0.5 | 0.25 | 4.5093 | 1.9810 | 2.1312 |

### Escenarios de sensibilidad del redondeo manual

Se descuenta una cantidad fija de segundos a cada `tiempo_manual_s` y se recalcula el
contraste de Wilcoxon sobre los pares ajustados (conjunto global).

| Descuento al manual (s) | Media manual ajustada (s) | Reducción de la media (%) | p bilateral | p unilateral | r |
|---|---|---|---|---|---|
| 5 | 191.6667 | 93.22 | 0.00391 | 0.00195 | 1.0000 |
| 10 | 186.6667 | 93.04 | 0.00391 | 0.00195 | 1.0000 |

- Granularidad de `tiempo_manual_s`: 9 / 9 valores múltiplos de 5 s; 7 / 9 múltiplos de 10 s.

---
_Generado automáticamente por `evaluation/run_evaluation.py`_