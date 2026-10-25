# Reporte de Evaluación del Clasificador (multietiqueta)

**Total de casos evaluados:** 200

**Procedencia de las predicciones:** `classifier_version` = `hybrid-v3`; `generated_at` = `2026-10-07T22:22:01.947873+00:00`.

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

Exactitud laxa (c-131, D5): el sector predicho principal pertenece al conjunto de
verdad del caso (`sector_asignado` más `sectores_adicionales` del corpus). No es la
pertenencia, que mide el sector asignado dentro del conjunto predicho.

- **Exactitud (laxa):** 0.8950 (89.5%)
- **Aciertos (laxos):** 179 / 200
- **IC Wilson 95% (laxo):** [0.8448, 0.9303]

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

## Exactitud por etapa del pipeline

Segmentación por la etapa que resolvió cada caso. Exactitud estricta (sector
principal igual al asignado) y laxa (sector principal dentro del conjunto de
verdad), cada una con su IC de Wilson al 95%. Una etapa sin casos se declara
"no aplicable".

| Etapa | Casos | Aciertos (estrictos) | Exactitud (estricta) | IC Wilson 95% (estricto) | Aciertos (laxos) | Exactitud (laxa) | IC Wilson 95% (laxo) |
|---|---|---|---|---|---|---|---|
| deterministic | 131 | 97 | 0.7405 | [0.6593, 0.8079] | 119 | 0.9084 | [0.8467, 0.9468] |
| gemini | 69 | 50 | 0.7246 | [0.6095, 0.8161] | 60 | 0.8696 | [0.7703, 0.9298] |
| fallback | 0 | 0 | no aplicable | no aplicable | 0 | no aplicable | no aplicable |

## Exactitud por canal de origen

Segmentación por el valor crudo de `canal_origen` del corpus, con el mismo orden
que el desglose por canal de tiempos. La composición sectorial y la proporción de
casos multietiqueta difieren entre canales: la comparación no aísla el efecto del canal.

| Canal | Casos | Deterministic | Gemini | Fallback | Aciertos (estrictos) | Exactitud (estricta) | IC Wilson 95% (estricto) | Aciertos (laxos) | Exactitud (laxa) | IC Wilson 95% (laxo) |
|---|---|---|---|---|---|---|---|---|---|---|
| llamada telefónica | 81 | 58 | 23 | 0 | 53 | 0.6543 | [0.5459, 0.7488] | 70 | 0.8642 | [0.7730, 0.9224] |
| correo electrónico | 66 | 34 | 32 | 0 | 51 | 0.7727 | [0.6583, 0.8571] | 61 | 0.9242 | [0.8346, 0.9672] |
| formulario web | 53 | 39 | 14 | 0 | 43 | 0.8113 | [0.6864, 0.8941] | 48 | 0.9057 | [0.7975, 0.9590] |

## Calibración de la confianza

Relación entre la confianza devuelta por caso y la exactitud estricta. La etapa
determinística y la etapa Gemini emiten magnitudes de confianza distintas: una
banda agregada compara etapas, no mide la calibración del modelo. Se reporta en
forma global y desagregada por etapa.

### Bandas de confianza (global)

| Banda | Casos | Aciertos | Exactitud |
|---|---|---|---|
| [0.00, 0.50) | 98 | 75 | 0.7653 |
| [0.50, 0.70) | 26 | 19 | 0.7308 |
| [0.70, 0.85) | 6 | 2 | 0.3333 |
| [0.85, 0.95) | 31 | 22 | 0.7097 |
| [0.95, 1.00] | 39 | 29 | 0.7436 |

### Contingencia en el umbral 0,70

Confianza `>= 0,70` frente a `< 0,70`, global y por etapa.

| Ámbito | Casos >= 0,70 | Aciertos >= 0,70 | Exactitud >= 0,70 | Casos < 0,70 | Aciertos < 0,70 | Exactitud < 0,70 |
|---|---|---|---|---|---|---|
| Global | 76 | 53 | 0.6974 | 124 | 94 | 0.7581 |
| deterministic | 7 | 3 | 0.4286 | 124 | 94 | 0.7581 |
| gemini | 69 | 50 | 0.7246 | 0 | 0 | no aplicable |
| fallback | 0 | 0 | no aplicable | 0 | 0 | no aplicable |

### Tramo de confianza >= 0,90

Casos y errores (predicción estricta distinta de la asignada) con confianza `>= 0,90`.

| Ámbito | Casos | Errores |
|---|---|---|
| Global | 46 | 13 |
| deterministic | 1 | 0 |
| gemini | 45 | 13 |
| fallback | 0 | 0 |

### Bandas de confianza por etapa

Exactitud por banda dentro de cada etapa, con IC de Wilson al 95%. La suma de las
etapas reproduce la tabla global. Una banda sin casos se declara "no aplicable".

| Etapa | Banda | Casos | Aciertos | Exactitud | IC Wilson 95% |
|---|---|---|---|---|---|
| deterministic | [0.00, 0.50) | 98 | 75 | 0.7653 | [0.6724, 0.8382] |
| deterministic | [0.50, 0.70) | 26 | 19 | 0.7308 | [0.5392, 0.8630] |
| deterministic | [0.70, 0.85) | 6 | 2 | 0.3333 | [0.0968, 0.7000] |
| deterministic | [0.85, 0.95) | 0 | 0 | no aplicable | no aplicable |
| deterministic | [0.95, 1.00] | 1 | 1 | 1.0000 | [0.2065, 1.0000] |
| gemini | [0.00, 0.50) | 0 | 0 | no aplicable | no aplicable |
| gemini | [0.50, 0.70) | 0 | 0 | no aplicable | no aplicable |
| gemini | [0.70, 0.85) | 0 | 0 | no aplicable | no aplicable |
| gemini | [0.85, 0.95) | 31 | 22 | 0.7097 | [0.5341, 0.8390] |
| gemini | [0.95, 1.00] | 38 | 28 | 0.7368 | [0.5799, 0.8503] |
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
| deterministic | 0.0000 | 90 | 67 |
| deterministic | 0.1667 | 8 | 8 |
| deterministic | 0.5000 | 26 | 19 |
| deterministic | 0.7500 | 6 | 2 |
| deterministic | 1.0000 | 1 | 1 |
| gemini | 0.8500 | 24 | 18 |
| gemini | 0.9000 | 7 | 4 |
| gemini | 0.9500 | 35 | 25 |
| gemini | 0.9800 | 3 | 3 |
| fallback | no aplicable | 0 | 0 |

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