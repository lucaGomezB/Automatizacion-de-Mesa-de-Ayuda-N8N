# Sensibilidad a referencias alternativas plausibles (c-216)

Sobre los 206 casos de la referencia arbitrada. Las cifras de este analisis son aditivas: no reemplazan ningun numero canonico de la tesis (seccion 3.27 del memo), no cambian el corpus, las predicciones ni los artefactos congelados, y la simulacion se rotula como sensibilidad, no como medicion de la verdad latente.

## Preregistro

- Fijado en el docstring antes de generar las salidas: True.
- Ciego: False. El metodo y los parametros se fijaron antes de generar las salidas. El prerregistro NO fue ciego: el corpus, las predicciones y los agregados canonicos ya se conocian; no se habia observado la distribucion simulada.

## Anclajes canonicos

| Indicador | Valor observado |
|---|---|
| Exactitud estricta | 142/206 (0.6893) |
| Macro-F1 | 0.7024 |
| Acuerdo E3/E4 (primeros 150 casos) | 103/150 (p_o = 0.6867) |
| Kappa E3/E4 | 0.6055 |

## Kernel empirico

Suavizado de Laplace: 0.5. Soporte por fila: Seguridad Informatica = 73, Soporte Tecnico Hardware = 113, Soporte Tecnico Software = 110, Bases de Datos = 35, Sistemas = 145.

## Calibracion de lambda

- lambda* = 0.231391
- kappa esperado = 0.605500 (objetivo 0.6055; tolerancia 0.0050)
- p_o esperado = 0.696107; p_o observado = 0.686667
- Verificacion simulada: kappa medio = 0.605313; desvio = 0.041223; dentro de tolerancia = True

## Distribucion bajo referencias alternativas

2000 replicas, semilla 20261021.

| Indicador | Observado | Mediana | q2,5 | q97,5 |
|---|---|---|---|---|
| Exactitud estricta | 0.6893 | 0.5097 | 0.4515 | 0.5631 |
| Macro-F1 | 0.7024 | 0.5109 | 0.4513 | 0.5692 |

- Proporcion de replicas con exactitud mayor o igual a 0,6893: 0.0000.

## Descomposicion del error

- Errores observados: 64.
- Intervalo de errores bajo referencias alternativas: [90.0000; 113.0000].
- Error robusto (extremo favorable): 90.0000.
- Error atribuible a la referencia: -26.0000. sensibilidad, no causalidad ni verdad latente; un componente negativo significa que el error observado es menor que el extremo favorable simulado.

## Cotas distribution-free

- delta = 0.369817; m = 76.
- Cotas de exactitud estricta: [0.3204; 1.0000].
- cotas de sensibilidad bajo un presupuesto de error de referencia, no mediciones.

## Casos de tres vias

| Caso | E3 | E4 | E5 | Referencia | Acierto | Rango de exactitud |
|---|---|---|---|---|---|---|
| I033 | Soporte Tecnico Software | Sistemas | Soporte Tecnico Hardware | Soporte Tecnico Hardware | False | [142/206; 143/206] |
| I042 | Seguridad Informatica | Sistemas | Bases de Datos | Bases de Datos | False | [142/206; 142/206] |
| I056 | Soporte Tecnico Software | Sistemas | Seguridad Informatica | Seguridad Informatica | False | [142/206; 143/206] |
| I130 | Soporte Tecnico Software | Sistemas | Seguridad Informatica | Seguridad Informatica | False | [142/206; 143/206] |
| I194 | Bases de Datos | Sistemas | Soporte Tecnico Hardware | Soporte Tecnico Hardware | False | [142/206; 143/206] |
| I198 | Sistemas | Soporte Tecnico Software | Seguridad Informatica | Seguridad Informatica | False | [142/206; 143/206] |

Rango agregado: 142/206 a 147/206 (0.6893 a 0.7136). No se elige una etiqueta verdadera: el rango es el resultado.

## Entradas y SHA-256

| Archivo | SHA-256 |
|---|---|
| `corpus_independiente_arbitrado.json` | `cb2874e649fb932c00b536100025c0a0137b3314ab12d45234e4c29049adc67e` |
| `predicciones_arbitrado.json` | `cb8aba6089dde9868c61740fba713fb75923ee32317370c46e0daeb52a01d5d5` |
| `doble_etiquetado_arbitrado.csv` | `7993f3ffda7ae7b380833a41b226ed3a6b4f6aaa36f3fbed66fb52682a61d2a4` |
| `arbitraje_tres_vias.json` | `4c85ab43bf28cac228caa35a6aaf3863deb327767cba31fbe850b43d2efe6a61` |

