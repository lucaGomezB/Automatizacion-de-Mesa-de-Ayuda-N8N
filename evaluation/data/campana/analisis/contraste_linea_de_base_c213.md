# Contraste pareado linea de base frente a hibrido (c-213)

Sobre los mismos 103 casos con consenso. Las cifras de este contraste son aditivas: no reemplazan ningun numero canonico de la tesis ni el clasificador de produccion. Comparan al hibrido congelado con un unico clasificador supervisado clasico entrenado con 200 casos, sobre los 103 casos con consenso; no es el brazo solo-LLM ni contrasta la hipotesis de eficiencia.

| Sistema | Aciertos estrictos |
|---|---|
| hibrido | 87/103 |
| balanceada | 67/103 |
| sin_repoderacion | 60/103 |

## Hibrido frente a linea de base `balanceada`

| | Linea de base acierta | Linea de base falla |
|---|---|---|
| Hibrido acierta | 60 | 27 |
| Hibrido falla | 7 | 9 |

- McNemar exacta bilateral: p = 0.0008; corregida por continuidad: p = 0.0011 (criterio de stats.py: corregido).
- Diferencia de exactitudes (hibrido - linea de base): 0.1942, IC 95 % bootstrap pareado [0.0874; 0.3010] (10000 remuestreos, semilla 20261021).

## Hibrido frente a linea de base `sin_repoderacion`

| | Linea de base acierta | Linea de base falla |
|---|---|---|
| Hibrido acierta | 56 | 31 |
| Hibrido falla | 4 | 12 |

- McNemar exacta bilateral: p = 3.465e-06; corregida por continuidad: p = 1.109e-05 (criterio de stats.py: corregido).
- Diferencia de exactitudes (hibrido - linea de base): 0.2621, IC 95 % bootstrap pareado [0.1650; 0.3592] (10000 remuestreos, semilla 20261021).
