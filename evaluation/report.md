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

### Descriptivos global y por canal

Desvío estándar con la convención muestral (divisor n − 1). La reducción relativa es
1 − media(automatizado) / media(manual) (y su análoga con la mediana). "No más
rápidos" cuenta los pares con `automatizado >= manual`.

| Ámbito | n | Manual media (s) | Manual mediana (s) | Manual desvío (s) | Manual mín (s) | Manual máx (s) | Automatizado media (s) | Automatizado mediana (s) | Automatizado desvío (s) | Automatizado mín (s) | Automatizado máx (s) | Reducción de la media (%) | Reducción de la mediana (%) | No más rápidos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Global | 200 | 61.5850 | 50.0000 | 44.8961 | 10.0000 | 300.0000 | 17.7606 | 17.4710 | 13.5164 | 0.5250 | 65.8340 | 71.16 | 65.06 | 12 |
| llamada telefónica | 81 | 87.2469 | 72.0000 | 48.8985 | 30.0000 | 220.0000 | 20.0883 | 18.6980 | 6.0246 | 14.0270 | 59.1500 | 76.98 | 74.03 | 0 |
| correo electrónico | 66 | 56.5152 | 50.0000 | 35.8090 | 20.0000 | 300.0000 | 27.6546 | 25.8180 | 14.2000 | 8.9700 | 65.8340 | 51.07 | 48.36 | 12 |
| formulario web | 53 | 28.6792 | 20.0000 | 16.4419 | 10.0000 | 100.0000 | 1.8823 | 1.2650 | 1.2662 | 0.5250 | 4.1620 | 93.44 | 93.67 | 0 |

### Contraste direccional y tamaño del efecto estandarizado

El p bilateral corresponde a la convención W = min(T+, T−); el p unilateral contrasta
H1: manual > automatizado (`alternative="greater"` sobre manual − automatizado).
d_z = media(d) / desvío(d) con d = manual − automatizado (desvío muestral).
El efecto mínimo detectable (MDE, en escala d_z) usa la aproximación normal
(z_(1−alfa/2) + z_potencia) / raíz(n · ARE) con alfa = 0.05 (bilateral),
potencia = 0.80 y ARE = 1 (sin ajuste) o ARE = 0.864 (cota inferior de la eficiencia de la prueba de rangos frente a la t pareada).

| Ámbito | n | p bilateral | p unilateral | d_z | MDE (ARE = 1) | MDE (ARE = 0.864) |
|---|---|---|---|---|---|---|
| Global | 200 | 3.08e-32 | 1.54e-32 | 1.0004 | 0.1981 | 0.2131 |
| llamada telefónica | 81 | 5.36e-15 | 2.68e-15 | 1.3674 | 0.3113 | 0.3349 |
| correo electrónico | 66 | 4.78e-09 | 2.39e-09 | 0.7345 | 0.3449 | 0.3710 |
| formulario web | 53 | 2.39e-10 | 1.19e-10 | 1.6147 | 0.3848 | 0.4140 |

### Escenarios de sensibilidad del redondeo manual

Se descuenta una cantidad fija de segundos a cada `tiempo_manual_s` y se recalcula el
contraste de Wilcoxon sobre los pares ajustados (conjunto global).

| Descuento al manual (s) | Media manual ajustada (s) | Reducción de la media (%) | p bilateral | p unilateral | r |
|---|---|---|---|---|---|
| 5 | 56.5850 | 68.61 | 4.87e-30 | 2.44e-30 | 0.9286 |
| 10 | 51.5850 | 65.57 | 1.8e-26 | 8.98e-27 | 0.8683 |

- Granularidad de `tiempo_manual_s`: 199 / 200 valores múltiplos de 5 s; 180 / 200 múltiplos de 10 s.

- **SHA-256 del corpus:** `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`

---
_Generado automáticamente por `evaluation/run_evaluation.py`_