# Reporte de Evaluación del Clasificador (multietiqueta)

**Total de casos evaluados:** 206

**Procedencia de las predicciones:** `classifier_version` = `hybrid-v3`; `generated_at` = `2026-11-13T22:03:39.167991+00:00`.

## Etapas del pipeline

| Etapa | Casos |
|-------|-------|
| Deterministic | 115 |
| Gemini | 91 |
| Fallback | 0 |

## Exactitud

Definiciones (design D5): igualdad estricta del sector principal y
pertenencia del sector asignado al conjunto predicho.

- **Exactitud (estricta):** 0.6893 (68.9%)
- **Aciertos (estrictos):** 142 / 206
- **IC Wilson 95% (estricto):** [0.6231, 0.7486]
- **Exactitud (pertenencia):** 0.6893 (68.9%)
- **Aciertos (pertenencia):** 142 / 206
- **IC Wilson 95% (pertenencia):** [0.6231, 0.7486]

Exactitud laxa (c-131, D5): el sector predicho principal pertenece al conjunto de
verdad del caso (`sector_asignado` más `sectores_adicionales` del corpus). No es la
pertenencia, que mide el sector asignado dentro del conjunto predicho.

- **Exactitud (laxa):** 0.7864 (78.6%)
- **Aciertos (laxos):** 162 / 206
- **IC Wilson 95% (laxo):** [0.7255, 0.8369]

## Matriz de Confusión (primaria 5x5)

Filas = sector asignado | Columnas = sector predicho principal

| Asignado \ Predicho | Seguridad Informatica | Soporte Tecnico Hardware | Soporte Tecnico Software | Bases de Datos | Sistemas |
|---|---|---|---|---|---|
| **Seguridad Informatica** | 20 | 3 | 5 | 0 | 4 |
| **Soporte Tecnico Hardware** | 0 | 44 | 2 | 0 | 5 |
| **Soporte Tecnico Software** | 3 | 6 | 33 | 1 | 3 |
| **Bases de Datos** | 0 | 0 | 1 | 14 | 1 |
| **Sistemas** | 8 | 3 | 16 | 3 | 31 |

## Métricas por sector (one-vs-rest)

| Sector | Precisión | Sensibilidad | F1 | Soporte |
|--------|-----------|--------------|-----|---------|
| Seguridad Informatica | 0.6452 | 0.6250 | 0.6349 | 32 |
| Soporte Tecnico Hardware | 0.7857 | 0.8627 | 0.8224 | 51 |
| Soporte Tecnico Software | 0.5789 | 0.7174 | 0.6408 | 46 |
| Bases de Datos | 0.7778 | 0.8750 | 0.8235 | 16 |
| Sistemas | 0.7045 | 0.5082 | 0.5905 | 61 |

## Métricas de conjunto

- **Subset accuracy:** 0.5631
- **Hamming loss:** 0.3273
- **Micro-F1:** 0.6934
- **Macro-F1:** 0.7024
- **Jaccard (IoU) promedio:** 0.6727

## Exactitud por etapa del pipeline

Segmentación por la etapa que resolvió cada caso. Exactitud estricta (sector
principal igual al asignado) y laxa (sector principal dentro del conjunto de
verdad), cada una con su IC de Wilson al 95%. Una etapa sin casos se declara
"no aplicable".

| Etapa | Casos | Aciertos (estrictos) | Exactitud (estricta) | IC Wilson 95% (estricto) | Aciertos (laxos) | Exactitud (laxa) | IC Wilson 95% (laxo) |
|---|---|---|---|---|---|---|---|
| deterministic | 115 | 88 | 0.7652 | [0.6800, 0.8333] | 97 | 0.8435 | [0.7661, 0.8986] |
| gemini | 91 | 54 | 0.5934 | [0.4907, 0.6886] | 65 | 0.7143 | [0.6143, 0.7969] |
| fallback | 0 | 0 | no aplicable | no aplicable | 0 | no aplicable | no aplicable |

## Exactitud por canal de origen

Segmentación por el valor crudo de `canal_origen` del corpus, con el mismo orden
que el desglose por canal de tiempos. La composición sectorial y la proporción de
casos multietiqueta difieren entre canales: la comparación no aísla el efecto del canal.

| Canal | Casos | Deterministic | Gemini | Fallback | Aciertos (estrictos) | Exactitud (estricta) | IC Wilson 95% (estricto) | Aciertos (laxos) | Exactitud (laxa) | IC Wilson 95% (laxo) |
|---|---|---|---|---|---|---|---|---|---|---|
| Correo | 78 | 44 | 34 | 0 | 50 | 0.6410 | [0.5303, 0.7385] | 60 | 0.7692 | [0.6644, 0.8487] |
| Telefono | 70 | 46 | 24 | 0 | 56 | 0.8000 | [0.6918, 0.8770] | 62 | 0.8857 | [0.7904, 0.9409] |
| Formulario Web | 58 | 25 | 33 | 0 | 36 | 0.6207 | [0.4920, 0.7344] | 40 | 0.6897 | [0.5620, 0.7938] |

## Calibración de la confianza

Relación entre la confianza devuelta por caso y la exactitud estricta. La etapa
determinística y la etapa Gemini emiten magnitudes de confianza distintas: una
banda agregada compara etapas, no mide la calibración del modelo. Se reporta en
forma global y desagregada por etapa.

### Bandas de confianza (global)

| Banda | Casos | Aciertos | Exactitud |
|---|---|---|---|
| [0.00, 0.50) | 80 | 59 | 0.7375 |
| [0.50, 0.70) | 27 | 21 | 0.7778 |
| [0.70, 0.85) | 8 | 8 | 1.0000 |
| [0.85, 0.95) | 42 | 16 | 0.3810 |
| [0.95, 1.00] | 49 | 38 | 0.7755 |

### Contingencia en el umbral 0,70

Confianza `>= 0,70` frente a `< 0,70`, global y por etapa.

| Ámbito | Casos >= 0,70 | Aciertos >= 0,70 | Exactitud >= 0,70 | Casos < 0,70 | Aciertos < 0,70 | Exactitud < 0,70 |
|---|---|---|---|---|---|---|
| Global | 99 | 62 | 0.6263 | 107 | 80 | 0.7477 |
| deterministic | 9 | 9 | 1.0000 | 106 | 79 | 0.7453 |
| gemini | 90 | 53 | 0.5889 | 1 | 1 | 1.0000 |
| fallback | 0 | 0 | no aplicable | 0 | 0 | no aplicable |

### Tramo de confianza >= 0,90

Casos y errores (predicción estricta distinta de la asignada) con confianza `>= 0,90`.

| Ámbito | Casos | Errores |
|---|---|---|
| Global | 56 | 14 |
| deterministic | 1 | 0 |
| gemini | 55 | 14 |
| fallback | 0 | 0 |

### Bandas de confianza por etapa

Exactitud por banda dentro de cada etapa, con IC de Wilson al 95%. La suma de las
etapas reproduce la tabla global. Una banda sin casos se declara "no aplicable".

| Etapa | Banda | Casos | Aciertos | Exactitud | IC Wilson 95% |
|---|---|---|---|---|---|
| deterministic | [0.00, 0.50) | 80 | 59 | 0.7375 | [0.6318, 0.8214] |
| deterministic | [0.50, 0.70) | 26 | 20 | 0.7692 | [0.5795, 0.8897] |
| deterministic | [0.70, 0.85) | 8 | 8 | 1.0000 | [0.6756, 1.0000] |
| deterministic | [0.85, 0.95) | 0 | 0 | no aplicable | no aplicable |
| deterministic | [0.95, 1.00] | 1 | 1 | 1.0000 | [0.2065, 1.0000] |
| gemini | [0.00, 0.50) | 0 | 0 | no aplicable | no aplicable |
| gemini | [0.50, 0.70) | 1 | 1 | 1.0000 | [0.2065, 1.0000] |
| gemini | [0.70, 0.85) | 0 | 0 | no aplicable | no aplicable |
| gemini | [0.85, 0.95) | 42 | 16 | 0.3810 | [0.2500, 0.5319] |
| gemini | [0.95, 1.00] | 48 | 37 | 0.7708 | [0.6346, 0.8669] |
| fallback | [0.00, 0.50) | 0 | 0 | no aplicable | no aplicable |
| fallback | [0.50, 0.70) | 0 | 0 | no aplicable | no aplicable |
| fallback | [0.70, 0.85) | 0 | 0 | no aplicable | no aplicable |
| fallback | [0.85, 0.95) | 0 | 0 | no aplicable | no aplicable |
| fallback | [0.95, 1.00] | 0 | 0 | no aplicable | no aplicable |

### Distribución de valores de confianza por etapa

Valores distintos de confianza observados (redondeados a 4 decimales), en orden
ascendente, con sus casos y aciertos estrictos.

| Etapa | Confianza | Casos | Aciertos |
|---|---|---|---|
| deterministic | 0.0000 | 72 | 52 |
| deterministic | 0.1667 | 7 | 6 |
| deterministic | 0.3750 | 1 | 1 |
| deterministic | 0.5000 | 25 | 19 |
| deterministic | 0.6000 | 1 | 1 |
| deterministic | 0.7500 | 8 | 8 |
| deterministic | 1.0000 | 1 | 1 |
| gemini | 0.6000 | 1 | 1 |
| gemini | 0.8500 | 35 | 12 |
| gemini | 0.9000 | 7 | 4 |
| gemini | 0.9500 | 43 | 34 |
| gemini | 0.9800 | 5 | 3 |
| fallback | no aplicable | 0 | 0 |

## Tiempos

Análisis sobre los pares (tiempo_manual_s, tiempo_automatizado_s) del corpus cargado.
Pares válidos: 0; excluidos por tiempo nulo: 206.

### Normalidad (Shapiro-Wilk)

| Conjunto | n | W | p |
|---|---|---|---|
| Manual | 0 | no aplicable | no aplicable |
| Automatizado | 0 | no aplicable | no aplicable |
| Diferencias | 0 | no aplicable | no aplicable |

### Prueba de Wilcoxon (rangos con signo)

Convención: W = min(T+, T−) (dos colas); tamaño del efecto rank-biserial r = (T+ − T−) / (n(n+1)/2).

| n | W | T+ | T− | p | r |
|---|---|---|---|---|---|
| 0 | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable |

### Reducción de tiempos

`tiempo_manual_s` se midió en vivo con redondeo al alza (sesgo sistemático), por lo
que su valor real no es mayor que el reportado. Se reporta la reducción sobre los
valores reportados y una cota conservadora que descuenta 1 s al manual por caso.

| Métrica | Reportada (s) | Conservadora (s) |
|---|---|---|
| Reducción media | 0.00 | 0.00 |
| Reducción mediana | 0.00 | 0.00 |

- Pares en que el flujo automatizado no fue más rápido (invertidos/empatados): 0.
- Casos excluidos por tiempo nulo: 206.

### Desglose por canal

Segmentación por el valor crudo de `canal_origen` del corpus.

| Canal | Pares válidos | W | T+ | T− | p | r |
|---|---|---|---|---|---|---|

### Descriptivos global y por canal

Desvío estándar con la convención muestral (divisor n − 1). La reducción relativa es
1 − media(automatizado) / media(manual) (y su análoga con la mediana). "No más
rápidos" cuenta los pares con `automatizado >= manual`.

| Ámbito | n | Manual media (s) | Manual mediana (s) | Manual desvío (s) | Manual mín (s) | Manual máx (s) | Automatizado media (s) | Automatizado mediana (s) | Automatizado desvío (s) | Automatizado mín (s) | Automatizado máx (s) | Reducción de la media (%) | Reducción de la mediana (%) | No más rápidos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Global | 0 | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable |

### Contraste direccional y tamaño del efecto estandarizado

El p bilateral corresponde a la convención W = min(T+, T−); el p unilateral contrasta
H1: manual > automatizado (`alternative="greater"` sobre manual − automatizado).
d_z = media(d) / desvío(d) con d = manual − automatizado (desvío muestral).
El efecto mínimo detectable (MDE, en escala d_z) usa la aproximación normal
(z_(1−alfa/2) + z_potencia) / raíz(n · ARE) con alfa = 0.05 (bilateral),
potencia = 0.80 y ARE = 1 (sin ajuste) o ARE = 0.864 (cota inferior de la eficiencia de la prueba de rangos frente a la t pareada).

| Ámbito | n | p bilateral | p unilateral | d_z | MDE (ARE = 1) | MDE (ARE = 0.864) |
|---|---|---|---|---|---|---|
| Global | 0 | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable |

### Escenarios de sensibilidad del redondeo manual

Se descuenta una cantidad fija de segundos a cada `tiempo_manual_s` y se recalcula el
contraste de Wilcoxon sobre los pares ajustados (conjunto global).

| Descuento al manual (s) | Media manual ajustada (s) | Reducción de la media (%) | p bilateral | p unilateral | r |
|---|---|---|---|---|---|
| 5 | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable |
| 10 | no aplicable | no aplicable | no aplicable | no aplicable | no aplicable |

- Granularidad de `tiempo_manual_s`: 0 / 0 valores múltiplos de 5 s; 0 / 0 múltiplos de 10 s.

- **SHA-256 del corpus:** `cb2874e649fb932c00b536100025c0a0137b3314ab12d45234e4c29049adc67e`

---
_Generado automáticamente por `evaluation/run_evaluation.py`_