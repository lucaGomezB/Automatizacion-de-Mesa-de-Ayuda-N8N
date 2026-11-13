# Analisis ampliado fuera de muestra (c-205)

Solo lectura; reutiliza `evaluation/metrics.py`, `evaluation/kappa.py` y `evaluation/stats.py`. Sin red, sin Gemini.

## Resultado base (n efectivo)

- n efectivo: 103; excluidos: 47 (de 150)
- Exactitud estricta: 87/103 = 0.8447 IC Wilson [0.7625; 0.9021]
- Exactitud laxa: 90/103 = 0.8738 IC Wilson [0.7960; 0.9247]

## Macro-F1 y metricas por clase

- Macro-F1 (cinco clases): 0.7447. media aritmetica de las cinco F1 por clase, incluida toda clase de soporte cero (F1 = 0.0); NO es equivalente de la exactitud estricta de etiqueta unica.

| Sector | Precision | Sensibilidad | F1 | Soporte |
|---|---|---|---|---|
| Seguridad Informatica | 1.0000 | 0.7143 | 0.8333 | 21 |
| Soporte Tecnico Hardware | 0.8636 | 0.9500 | 0.9048 | 40 |
| Soporte Tecnico Software | 0.7692 | 0.8333 | 0.8000 | 24 |
| Bases de Datos | 0.9286 | 1.0000 | 0.9630 | 13 |
| Sistemas | 0.2500 | 0.2000 | 0.2222 | 5 |

- Balanced accuracy (media aritmetica de las sensibilidades por clase): 0.7395; difiere de la exactitud estricta (0.8447) en -0.1051 por el desbalance de clases.

## Kappa del clasificador contra la referencia

- concordancia del clasificador contra la referencia humana (E3/E4); NO es fiabilidad inter-etiquetador
- kappa = 0.7862; p_o = 0.8447; p_e = 0.2734; PABAK = 0.8058; n = 103
- IC asintotico 95 %: [0.6919; 0.8805]; IC bootstrap 95 % (semilla 20261021, 2000 remuestreos): [0.6903; 0.8768]
- Rotulo de Landis y Koch: sustancial

## Matriz de confusion 5x5 (filas = referencia, columnas = prediccion)

| Referencia / Prediccion | Seguridad Informatica | Soporte Tecnico Hardware | Soporte Tecnico Software | Bases de Datos | Sistemas |
|---|---|---|---|---|---|
| Seguridad Informatica | 15 | 3 | 2 | 0 | 1 |
| Soporte Tecnico Hardware | 0 | 38 | 1 | 0 | 1 |
| Soporte Tecnico Software | 0 | 3 | 20 | 0 | 1 |
| Bases de Datos | 0 | 0 | 0 | 13 | 0 |
| Sistemas | 0 | 0 | 3 | 1 | 1 |

- Mayor celda fuera de la diagonal: 3 casos de Sistemas predichos como Soporte Tecnico Software.
- Sistemas: 1/5 aciertos; errores por prediccion: Seguridad Informatica 0; Soporte Tecnico Hardware 0; Soporte Tecnico Software 3; Bases de Datos 1

## Potencia y precision del n efectivo

- Semi-ancho de Wilson observado (n = 103): 6.98 pts; objetivo D1 de c-191: 8.4 pts; cumple: si.
- MDE (d_z) = 0.2760 con alfa = 0.05, potencia = 0.8, bilateral.
- precision alcanzada con el n efectivo, no tamano muestral elegido; el objetivo D1 de c-191 (~8,4 pts) fue aceptado, no un requisito.

## Sesgo de exclusion de los discordantes (sensibilidad, no medicion)

- analisis de sensibilidad; no es una medicion del clasificador sobre los excluidos.
- Peor caso: 87/150 = 0.5800
- Mejor caso: 134/150 = 0.8933
- Cota (los excluidos aciertan a la tasa del limite inferior del IC de Wilson 95 % del n efectivo): tasa 0.7625; 122.84/150 = 0.8189
- Aciertos minimos entre los 47 excluidos para alcanzar 0.85 sobre 150: 41 (tasa 0.8723).
- Regla de decision: El umbral 0.85 se sostiene sin condiciones solo si el peor caso lo alcanza. El peor caso (87/150 = 0.5800) queda por debajo del umbral: la exactitud sobre el n efectivo NO puede presentarse como superacion del umbral sin el arbitraje de los 47 discordantes.

## Balance neto con la tasa de error fuera de muestra (condicional)

- e_aut fuera de muestra = 16/103 = 0.1553; ahorro bruto 32.2 h/trimestre.
- Formula: B = (N / 3600) * [dt - (e_aut - e_man) * c]; a* = 1 - e_man - dt / c.

| e_man | c (min) | B (h) | a* (%) |
|---|---|---|---|
| 0.10 | 5 | 20.0 | 75.4 |
| 0.10 | 10 | 7.8 | 82.7 |
| 0.10 | 15 | -4.4 | 85.1 |
| 0.15 | 5 | 31.0 | 70.4 |
| 0.15 | 10 | 29.9 | 77.7 |
| 0.15 | 15 | 28.7 | 80.1 |
| 0.20 | 5 | 42.1 | 65.4 |
| 0.20 | 10 | 51.9 | 72.7 |
| 0.20 | 15 | 61.8 | 75.1 |
| 0.265 | 5 | 56.4 | 58.9 |
| 0.265 | 10 | 80.6 | 66.2 |
| 0.265 | 15 | 104.7 | 68.6 |

- No computable: ahorro de tiempo por incidente (dt) medido en el corpus independiente. los artefactos fuera de muestra (corpus_independiente.json, predicciones_independiente.json, doble_etiquetado_independiente.csv) no registran tiempos de resolucion; dt se toma como supuesto condicional del in-sample.
- No computable: tasa de derivacion erronea manual (e_man) y costo por derivacion (c). no se midieron en el corpus independiente; se mantienen las rejillas condicional de la Seccion 3.11.

