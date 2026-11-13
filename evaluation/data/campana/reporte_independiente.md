# Reporte de Evaluación del Clasificador (multietiqueta)

**Total de casos evaluados:** 103

**Procedencia de las predicciones:** `classifier_version` = `hybrid-v3`; `generated_at` = `2026-11-12T23:58:14.687248+00:00`.

## Etapas del pipeline

| Etapa | Casos |
|-------|-------|
| Deterministic | 69 |
| Gemini | 34 |
| Fallback | 0 |

## Exactitud

Definiciones (design D5): igualdad estricta del sector principal y
pertenencia del sector asignado al conjunto predicho.

- **Exactitud (estricta):** 0.8447 (84.5%)
- **Aciertos (estrictos):** 87 / 103
- **IC Wilson 95% (estricto):** [0.7625, 0.9021]
- **Exactitud (pertenencia):** 0.8447 (84.5%)
- **Aciertos (pertenencia):** 87 / 103
- **IC Wilson 95% (pertenencia):** [0.7625, 0.9021]

Exactitud laxa (c-131, D5): el sector predicho principal pertenece al conjunto de
verdad del caso (`sector_asignado` más `sectores_adicionales` del corpus). No es la
pertenencia, que mide el sector asignado dentro del conjunto predicho.

- **Exactitud (laxa):** 0.8738 (87.4%)
- **Aciertos (laxos):** 90 / 103
- **IC Wilson 95% (laxo):** [0.7960, 0.9247]

## Matriz de Confusión (primaria 5x5)

Filas = sector asignado | Columnas = sector predicho principal

| Asignado \ Predicho | Seguridad Informatica | Soporte Tecnico Hardware | Soporte Tecnico Software | Bases de Datos | Sistemas |
|---|---|---|---|---|---|
| **Seguridad Informatica** | 15 | 3 | 2 | 0 | 1 |
| **Soporte Tecnico Hardware** | 0 | 38 | 1 | 0 | 1 |
| **Soporte Tecnico Software** | 0 | 3 | 20 | 0 | 1 |
| **Bases de Datos** | 0 | 0 | 0 | 13 | 0 |
| **Sistemas** | 0 | 0 | 3 | 1 | 1 |

## Métricas por sector (one-vs-rest)

| Sector | Precisión | Sensibilidad | F1 | Soporte |
|--------|-----------|--------------|-----|---------|
| Seguridad Informatica | 1.0000 | 0.7143 | 0.8333 | 21 |
| Soporte Tecnico Hardware | 0.8636 | 0.9500 | 0.9048 | 40 |
| Soporte Tecnico Software | 0.7692 | 0.8333 | 0.8000 | 24 |
| Bases de Datos | 0.9286 | 1.0000 | 0.9630 | 13 |
| Sistemas | 0.2500 | 0.2000 | 0.2222 | 5 |

## Métricas de conjunto

- **Subset accuracy:** 0.7476
- **Hamming loss:** 0.1893
- **Micro-F1:** 0.8145
- **Macro-F1:** 0.7447
- **Jaccard (IoU) promedio:** 0.8107

## Exactitud por etapa del pipeline

Segmentación por la etapa que resolvió cada caso. Exactitud estricta (sector
principal igual al asignado) y laxa (sector principal dentro del conjunto de
verdad), cada una con su IC de Wilson al 95%. Una etapa sin casos se declara
"no aplicable".

| Etapa | Casos | Aciertos (estrictos) | Exactitud (estricta) | IC Wilson 95% (estricto) | Aciertos (laxos) | Exactitud (laxa) | IC Wilson 95% (laxo) |
|---|---|---|---|---|---|---|---|
| deterministic | 69 | 61 | 0.8841 | [0.7875, 0.9401] | 62 | 0.8986 | [0.8051, 0.9500] |
| gemini | 34 | 26 | 0.7647 | [0.6000, 0.8756] | 28 | 0.8235 | [0.6649, 0.9165] |
| fallback | 0 | 0 | no aplicable | no aplicable | 0 | no aplicable | no aplicable |

## Exactitud por canal de origen

Segmentación por el valor crudo de `canal_origen` del corpus, con el mismo orden
que el desglose por canal de tiempos. La composición sectorial y la proporción de
casos multietiqueta difieren entre canales: la comparación no aísla el efecto del canal.

| Canal | Casos | Deterministic | Gemini | Fallback | Aciertos (estrictos) | Exactitud (estricta) | IC Wilson 95% (estricto) | Aciertos (laxos) | Exactitud (laxa) | IC Wilson 95% (laxo) |
|---|---|---|---|---|---|---|---|---|---|---|
| Telefono | 45 | 32 | 13 | 0 | 39 | 0.8667 | [0.7382, 0.9374] | 42 | 0.9333 | [0.8214, 0.9771] |
| Correo | 34 | 24 | 10 | 0 | 27 | 0.7941 | [0.6320, 0.8965] | 27 | 0.7941 | [0.6320, 0.8965] |
| Formulario Web | 24 | 13 | 11 | 0 | 21 | 0.8750 | [0.6900, 0.9566] | 21 | 0.8750 | [0.6900, 0.9566] |

## Calibración de la confianza

Relación entre la confianza devuelta por caso y la exactitud estricta. La etapa
determinística y la etapa Gemini emiten magnitudes de confianza distintas: una
banda agregada compara etapas, no mide la calibración del modelo. Se reporta en
forma global y desagregada por etapa.

### Bandas de confianza (global)

| Banda | Casos | Aciertos | Exactitud |
|---|---|---|---|
| [0.00, 0.50) | 45 | 38 | 0.8444 |
| [0.50, 0.70) | 18 | 17 | 0.9444 |
| [0.70, 0.85) | 7 | 7 | 1.0000 |
| [0.85, 0.95) | 10 | 5 | 0.5000 |
| [0.95, 1.00] | 23 | 20 | 0.8696 |

### Contingencia en el umbral 0,70

Confianza `>= 0,70` frente a `< 0,70`, global y por etapa.

| Ámbito | Casos >= 0,70 | Aciertos >= 0,70 | Exactitud >= 0,70 | Casos < 0,70 | Aciertos < 0,70 | Exactitud < 0,70 |
|---|---|---|---|---|---|---|
| Global | 40 | 32 | 0.8000 | 63 | 55 | 0.8730 |
| deterministic | 7 | 7 | 1.0000 | 62 | 54 | 0.8710 |
| gemini | 33 | 25 | 0.7576 | 1 | 1 | 1.0000 |
| fallback | 0 | 0 | no aplicable | 0 | 0 | no aplicable |

### Tramo de confianza >= 0,90

Casos y errores (predicción estricta distinta de la asignada) con confianza `>= 0,90`.

| Ámbito | Casos | Errores |
|---|---|---|
| Global | 25 | 3 |
| deterministic | 0 | 0 |
| gemini | 25 | 3 |
| fallback | 0 | 0 |

### Bandas de confianza por etapa

Exactitud por banda dentro de cada etapa, con IC de Wilson al 95%. La suma de las
etapas reproduce la tabla global. Una banda sin casos se declara "no aplicable".

| Etapa | Banda | Casos | Aciertos | Exactitud | IC Wilson 95% |
|---|---|---|---|---|---|
| deterministic | [0.00, 0.50) | 45 | 38 | 0.8444 | [0.7122, 0.9225] |
| deterministic | [0.50, 0.70) | 17 | 16 | 0.9412 | [0.7302, 0.9895] |
| deterministic | [0.70, 0.85) | 7 | 7 | 1.0000 | [0.6457, 1.0000] |
| deterministic | [0.85, 0.95) | 0 | 0 | no aplicable | no aplicable |
| deterministic | [0.95, 1.00] | 0 | 0 | no aplicable | no aplicable |
| gemini | [0.00, 0.50) | 0 | 0 | no aplicable | no aplicable |
| gemini | [0.50, 0.70) | 1 | 1 | 1.0000 | [0.2065, 1.0000] |
| gemini | [0.70, 0.85) | 0 | 0 | no aplicable | no aplicable |
| gemini | [0.85, 0.95) | 10 | 5 | 0.5000 | [0.2366, 0.7634] |
| gemini | [0.95, 1.00] | 23 | 20 | 0.8696 | [0.6787, 0.9546] |
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
| deterministic | 0.0000 | 41 | 34 |
| deterministic | 0.1667 | 3 | 3 |
| deterministic | 0.3750 | 1 | 1 |
| deterministic | 0.5000 | 16 | 15 |
| deterministic | 0.6000 | 1 | 1 |
| deterministic | 0.7500 | 7 | 7 |
| gemini | 0.6500 | 1 | 1 |
| gemini | 0.8500 | 8 | 3 |
| gemini | 0.9000 | 2 | 2 |
| gemini | 0.9500 | 22 | 19 |
| gemini | 0.9800 | 1 | 1 |
| fallback | no aplicable | 0 | 0 |

## Tiempos

Análisis sobre los pares (tiempo_manual_s, tiempo_automatizado_s) del corpus cargado.
Pares válidos: 0; excluidos por tiempo nulo: 103.

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
- Casos excluidos por tiempo nulo: 103.

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

- **SHA-256 del corpus:** `8cdbec6fc06be3f7c4535f0213919d6d90b69d36e7d820ff97a84b9180cef56d`

---
_Generado automáticamente por `evaluation/run_evaluation.py`_