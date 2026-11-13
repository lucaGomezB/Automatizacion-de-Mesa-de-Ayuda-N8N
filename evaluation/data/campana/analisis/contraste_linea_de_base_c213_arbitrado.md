# Contraste pareado linea de base frente a hibrido (c-213)

Sobre los mismos 206 casos con consenso. Las cifras de este contraste son aditivas: no reemplazan ningun numero canonico de la tesis ni el clasificador de produccion. Comparan al hibrido congelado con un unico clasificador supervisado clasico entrenado con 200 casos, sobre los 206 casos con consenso; no es el brazo solo-LLM ni contrasta la hipotesis de eficiencia.

| Sistema | Aciertos estrictos |
|---|---|
| hibrido | 142/206 |
| balanceada | 101/206 |
| sin_repoderacion | 88/206 |

## Hibrido frente a linea de base `balanceada`

| | Linea de base acierta | Linea de base falla |
|---|---|---|
| Hibrido acierta | 81 | 61 |
| Hibrido falla | 20 | 44 |

- McNemar exacta bilateral: p = 5.656e-06; corregida por continuidad: p = 8.812e-06 (criterio de stats.py: corregido).
- Diferencia de exactitudes (hibrido - linea de base): 0.1990, IC 95 % bootstrap pareado [0.1165; 0.2767] (10000 remuestreos, semilla 20261021).

## Hibrido frente a linea de base `sin_repoderacion`

| | Linea de base acierta | Linea de base falla |
|---|---|---|
| Hibrido acierta | 73 | 69 |
| Hibrido falla | 15 | 49 |

- McNemar exacta bilateral: p = 1.938e-09; corregida por continuidad: p = 7.348e-09 (criterio de stats.py: corregido).
- Diferencia de exactitudes (hibrido - linea de base): 0.2621, IC 95 % bootstrap pareado [0.1845; 0.3398] (10000 remuestreos, semilla 20261021).

## Metricas globales (n = 206)

| Sistema | Exactitud estricta | Exactitud laxa | Macro-F1 | Balanced accuracy |
|---|---|---|---|---|
| hibrido | 142/206 (0.6893) | 162/206 (0.7864) | 0.7024 | 0.7177 |
| balanceada | 101/206 (0.4903) | 121/206 (0.5874) | 0.3884 | 0.4475 |
| sin_repoderacion | 88/206 (0.4272) | 104/206 (0.5049) | 0.2935 | 0.3805 |

### F1 por clase con soporte

| Sistema | Sector | Precision | Sensibilidad | F1 | Soporte |
|---|---|---|---|---|---|
| hibrido | Seguridad Informatica | 0.6452 | 0.6250 | 0.6349 | 32 |
| hibrido | Soporte Tecnico Hardware | 0.7857 | 0.8627 | 0.8224 | 51 |
| hibrido | Soporte Tecnico Software | 0.5789 | 0.7174 | 0.6408 | 46 |
| hibrido | Bases de Datos | 0.7778 | 0.8750 | 0.8235 | 16 |
| hibrido | Sistemas | 0.7045 | 0.5082 | 0.5905 | 61 |
| balanceada | Seguridad Informatica | 0.3455 | 0.5938 | 0.4368 | 32 |
| balanceada | Soporte Tecnico Hardware | 0.6250 | 0.7843 | 0.6957 | 51 |
| balanceada | Soporte Tecnico Software | 0.4638 | 0.6957 | 0.5565 | 46 |
| balanceada | Bases de Datos | 0.0000 | 0.0000 | 0.0000 | 16 |
| balanceada | Sistemas | 0.5556 | 0.1639 | 0.2532 | 61 |
| sin_repoderacion | Seguridad Informatica | 0.5000 | 0.2812 | 0.3600 | 32 |
| sin_repoderacion | Soporte Tecnico Hardware | 0.4839 | 0.8824 | 0.6250 | 51 |
| sin_repoderacion | Soporte Tecnico Software | 0.3579 | 0.7391 | 0.4823 | 46 |
| sin_repoderacion | Bases de Datos | 0.0000 | 0.0000 | 0.0000 | 16 |
| sin_repoderacion | Sistemas | 0.0000 | 0.0000 | 0.0000 | 61 |
