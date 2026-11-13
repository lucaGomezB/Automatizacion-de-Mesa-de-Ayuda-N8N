# Calibracion y punto de operacion del gate de confianza (c-214)

Solo lectura; reglas de seleccion prerregistradas en el docstring del generador. El prerregistro NO fue ciego. Sin red, sin Gemini. No modifica configuracion productiva.

## Reproduccion del recomputo de las reglas

- dentro_muestra: 131 cortocircuitados reproducidos de 200 casos
- fuera_muestra: 69 cortocircuitados reproducidos de 103 casos

## Calibracion y discriminacion por etapa

### dentro_muestra

- Referencia: etiquetado original del corpus (sector_asignado); n = 200; escalados a Gemini = 69; cortocircuitados = 131

**Gemini (confianza)**: n = 69, exactitud = 0.7246 IC Wilson [0.6095; 0.8161], senal media = 0.9114
- ECE = 0.1868 IC95 [0.1003; 0.2945]; Brier = 0.2362 IC95 [0.1581; 0.3242]
- Sobreconfianza = 0.1868 IC95 [0.0940; 0.2942]; AUROC = 0.5168 IC95 [0.3796; 0.6528]

**Determinista (confianza)**: n = 131, exactitud = 0.7405 IC Wilson [0.6593; 0.8079], senal media = 0.1514
- ECE = 0.6272 IC95 [0.5445; 0.7068]; Brier = 0.6216 IC95 [0.5495; 0.6908]
- Sobreconfianza = -0.5891 IC95 [-0.6756; -0.4924]; AUROC = 0.4718 IC95 [0.3744; 0.5705]

**Determinista (score_correctitud)**: n = 131, exactitud = 0.7405 IC Wilson [0.6593; 0.8079], senal media = 0.7970
- ECE = 0.1172 IC95 [0.0431; 0.1950]; Brier = 0.2129 IC95 [0.1655; 0.2628]
- Sobreconfianza = 0.0566 IC95 [-0.0203; 0.1376]; AUROC = 0.4160 IC95 [0.3252; 0.5050]

Distribucion de la confianza de Gemini: 0.85: 24, 0.9: 7, 0.95: 35, 0.98: 3

| Valor (Gemini) | Casos | Aciertos | Exactitud | IC Wilson |
|---|---|---|---|---|
| 0.85 | 24 | 18 | 0.7500 | [0.5510; 0.8800] |
| 0.90 | 7 | 4 | 0.5714 | [0.2505; 0.8418] |
| 0.95 | 35 | 25 | 0.7143 | [0.5495; 0.8367] |
| 0.98 | 3 | 3 | 1.0000 | [0.4385; 1.0000] |

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.7000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.8600 | 45 | 24 | 0.652 | 0.711 [0.566; 0.823] | 0.750 | 6 | 0.120 |
| 0.9100 | 38 | 31 | 0.551 | 0.737 [0.580; 0.850] | 0.710 | 9 | 0.155 |
| 0.9600 | 3 | 66 | 0.043 | 1.000 [0.439; 1.000] | 0.712 | 19 | 0.330 |
| 0.9900 | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |
| inf | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |

### fuera_muestra

- Referencia: consenso de E3 y E4 (sector_asignado de la cache independiente); n = 103; escalados a Gemini = 34; cortocircuitados = 69

**Gemini (confianza)**: n = 34, exactitud = 0.7647 IC Wilson [0.6000; 0.8756], senal media = 0.9156
- ECE = 0.1715 IC95 [0.0685; 0.3038]; Brier = 0.1935 IC95 [0.0881; 0.3051]
- Sobreconfianza = 0.1509 IC95 [0.0229; 0.2912]; AUROC = 0.7163 IC95 [0.5138; 0.9139]

**Determinista (confianza)**: n = 69, exactitud = 0.8841 IC Wilson [0.7875; 0.9401], senal media = 0.2134
- ECE = 0.6707 IC95 [0.5819; 0.7531]; Brier = 0.5952 IC95 [0.4973; 0.6871]
- Sobreconfianza = -0.6707 IC95 [-0.7531; -0.5819]; AUROC = 0.6629 IC95 [0.5119; 0.7679]

**Determinista (score_correctitud)**: n = 69, exactitud = 0.8841 IC Wilson [0.7875; 0.9401], senal media = 0.8034
- ECE = 0.0807 IC95 [0.0286; 0.1552]; Brier = 0.1150 IC95 [0.0714; 0.1606]
- Sobreconfianza = -0.0807 IC95 [-0.1552; -0.0032]; AUROC = 0.5748 IC95 [0.4423; 0.6855]

Distribucion de la confianza de Gemini: 0.65: 1, 0.85: 8, 0.9: 2, 0.95: 22, 0.98: 1

| Valor (Gemini) | Casos | Aciertos | Exactitud | IC Wilson |
|---|---|---|---|---|
| 0.65 | 1 | 1 | 1.0000 | [0.2065; 1.0000] |
| 0.85 | 8 | 3 | 0.3750 | [0.1368; 0.6943] |
| 0.90 | 2 | 2 | 1.0000 | [0.3424; 1.0000] |
| 0.95 | 22 | 19 | 0.8636 | [0.6667; 0.9525] |
| 0.98 | 1 | 1 | 1.0000 | [0.2065; 1.0000] |

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.7000 | 33 | 1 | 0.971 | 0.758 [0.590; 0.872] | 1.000 | 0 | 0.010 |
| 0.8600 | 25 | 9 | 0.735 | 0.880 [0.700; 0.958] | 0.444 | 5 | 0.087 |
| 0.9100 | 23 | 11 | 0.676 | 0.870 [0.679; 0.955] | 0.545 | 5 | 0.107 |
| 0.9600 | 1 | 33 | 0.029 | 1.000 [0.207; 1.000] | 0.758 | 8 | 0.320 |
| 0.9900 | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |
| inf | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |

### control_consenso_e1_e2

- Referencia: consenso de E1 y E2 (138 casos; discordantes excluidos); n = 138; escalados a Gemini = 44; cortocircuitados = 94

**Gemini (confianza)**: n = 44, exactitud = 0.7727 IC Wilson [0.6301; 0.8716], senal media = 0.9100
- ECE = 0.1373 IC95 [0.0425; 0.2716]; Brier = 0.1923 IC95 [0.0995; 0.3014]
- Sobreconfianza = 0.1373 IC95 [0.0232; 0.2673]; AUROC = 0.5794 IC95 [0.4048; 0.7568]

**Determinista (confianza)**: n = 94, exactitud = 0.8085 IC Wilson [0.7175; 0.8753], senal media = 0.1285
- ECE = 0.6800 IC95 [0.5922; 0.7660]; Brier = 0.6560 IC95 [0.5719; 0.7403]
- Sobreconfianza = -0.6800 IC95 [-0.7660; -0.5922]; AUROC = 0.5603 IC95 [0.4530; 0.6600]

**Determinista (score_correctitud)**: n = 94, exactitud = 0.8085 IC Wilson [0.7175; 0.8753], senal media = 0.7971
- ECE = 0.0421 IC95 [0.0192; 0.1239]; Brier = 0.1643 IC95 [0.1164; 0.2129]
- Sobreconfianza = -0.0115 IC95 [-0.0878; 0.0717]; AUROC = 0.5055 IC95 [0.4039; 0.5958]

Distribucion de la confianza de Gemini: 0.85: 16, 0.9: 5, 0.95: 20, 0.98: 3

| Valor (Gemini) | Casos | Aciertos | Exactitud | IC Wilson |
|---|---|---|---|---|
| 0.85 | 16 | 12 | 0.7500 | [0.5050; 0.8982] |
| 0.90 | 5 | 3 | 0.6000 | [0.2307; 0.8824] |
| 0.95 | 20 | 16 | 0.8000 | [0.5840; 0.9193] |
| 0.98 | 3 | 3 | 1.0000 | [0.4385; 1.0000] |

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.7000 | 44 | 0 | 1.000 | 0.773 [0.630; 0.872] | n/d | 0 | 0.000 |
| 0.8600 | 28 | 16 | 0.636 | 0.786 [0.605; 0.898] | 0.750 | 4 | 0.116 |
| 0.9100 | 23 | 21 | 0.523 | 0.826 [0.629; 0.930] | 0.714 | 6 | 0.152 |
| 0.9600 | 3 | 41 | 0.068 | 1.000 [0.439; 1.000] | 0.756 | 10 | 0.297 |
| 0.9900 | 0 | 44 | 0.000 | n/d  | 0.773 | 10 | 0.319 |
| inf | 0 | 44 | 0.000 | n/d  | 0.773 | 10 | 0.319 |

## Politicas de derivacion (seleccion dentro, evaluacion fuera de la muestra)

### confianza_gemini / piso_0.85 (piso 0.85)

- Umbral seleccionado dentro de la muestra: ninguno
- Veredicto fuera de la muestra: sin umbral seleccionado
- AUROC dentro = 0.5168 IC95 [0.3796; 0.6528]; fuera = 0.7163 IC95 [0.5138; 0.9139]
- la senal no sostiene un umbral con el piso fijado: ningun candidato alcanza 0.85 con al menos 10 aceptados dentro de la muestra; fuera de la muestra el barrido se informa solo como descripcion

Barrido dentro de la muestra:

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.7000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.8600 | 45 | 24 | 0.652 | 0.711 [0.566; 0.823] | 0.750 | 6 | 0.120 |
| 0.9100 | 38 | 31 | 0.551 | 0.737 [0.580; 0.850] | 0.710 | 9 | 0.155 |
| 0.9600 | 3 | 66 | 0.043 | 1.000 [0.439; 1.000] | 0.712 | 19 | 0.330 |
| 0.9900 | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |
| inf | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |

Barrido fuera de la muestra (descriptivo; no se elige con el):

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.7000 | 33 | 1 | 0.971 | 0.758 [0.590; 0.872] | 1.000 | 0 | 0.010 |
| 0.8600 | 25 | 9 | 0.735 | 0.880 [0.700; 0.958] | 0.444 | 5 | 0.087 |
| 0.9100 | 23 | 11 | 0.676 | 0.870 [0.679; 0.955] | 0.545 | 5 | 0.107 |
| 0.9600 | 1 | 33 | 0.029 | 1.000 [0.207; 1.000] | 0.758 | 8 | 0.320 |
| 0.9900 | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |
| inf | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |

### confianza_gemini / piso_0.8278 (piso 0.8278)

- Umbral seleccionado dentro de la muestra: ninguno
- Veredicto fuera de la muestra: sin umbral seleccionado
- AUROC dentro = 0.5168 IC95 [0.3796; 0.6528]; fuera = 0.7163 IC95 [0.5138; 0.9139]
- la senal no sostiene un umbral con el piso fijado: ningun candidato alcanza 0.8278 con al menos 10 aceptados dentro de la muestra; fuera de la muestra el barrido se informa solo como descripcion

Barrido dentro de la muestra:

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.7000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.8600 | 45 | 24 | 0.652 | 0.711 [0.566; 0.823] | 0.750 | 6 | 0.120 |
| 0.9100 | 38 | 31 | 0.551 | 0.737 [0.580; 0.850] | 0.710 | 9 | 0.155 |
| 0.9600 | 3 | 66 | 0.043 | 1.000 [0.439; 1.000] | 0.712 | 19 | 0.330 |
| 0.9900 | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |
| inf | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |

Barrido fuera de la muestra (descriptivo; no se elige con el):

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.7000 | 33 | 1 | 0.971 | 0.758 [0.590; 0.872] | 1.000 | 0 | 0.010 |
| 0.8600 | 25 | 9 | 0.735 | 0.880 [0.700; 0.958] | 0.444 | 5 | 0.087 |
| 0.9100 | 23 | 11 | 0.676 | 0.870 [0.679; 0.955] | 0.545 | 5 | 0.107 |
| 0.9600 | 1 | 33 | 0.029 | 1.000 [0.207; 1.000] | 0.758 | 8 | 0.320 |
| 0.9900 | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |
| inf | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |

### s1_acuerdo_entre_etapas / piso_0.85 (piso 0.85)

- Umbral seleccionado dentro de la muestra: ninguno
- Veredicto fuera de la muestra: sin umbral seleccionado
- AUROC dentro = 0.5000 IC95 [0.5000; 0.5000]; fuera = 0.5000 IC95 [0.5000; 0.5000]
- la senal no sostiene un umbral con el piso fijado: ningun candidato alcanza 0.85 con al menos 10 aceptados dentro de la muestra; fuera de la muestra el barrido se informa solo como descripcion

Barrido dentro de la muestra:

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 1.0000 | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |
| inf | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |

Barrido fuera de la muestra (descriptivo; no se elige con el):

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| 1.0000 | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |
| inf | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |

### s1_acuerdo_entre_etapas / piso_0.8278 (piso 0.8278)

- Umbral seleccionado dentro de la muestra: ninguno
- Veredicto fuera de la muestra: sin umbral seleccionado
- AUROC dentro = 0.5000 IC95 [0.5000; 0.5000]; fuera = 0.5000 IC95 [0.5000; 0.5000]
- la senal no sostiene un umbral con el piso fijado: ningun candidato alcanza 0.8278 con al menos 10 aceptados dentro de la muestra; fuera de la muestra el barrido se informa solo como descripcion

Barrido dentro de la muestra:

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 1.0000 | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |
| inf | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |

Barrido fuera de la muestra (descriptivo; no se elige con el):

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| 1.0000 | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |
| inf | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |

### s2_score_reglas / piso_0.85 (piso 0.85)

- Umbral seleccionado dentro de la muestra: ninguno
- Veredicto fuera de la muestra: sin umbral seleccionado
- AUROC dentro = 0.5000 IC95 [0.5000; 0.5000]; fuera = 0.5000 IC95 [0.5000; 0.5000]
- la senal no sostiene un umbral con el piso fijado: ningun candidato alcanza 0.85 con al menos 10 aceptados dentro de la muestra; fuera de la muestra el barrido se informa solo como descripcion

Barrido dentro de la muestra:

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| inf | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |

Barrido fuera de la muestra (descriptivo; no se elige con el):

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| inf | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |

### s2_score_reglas / piso_0.8278 (piso 0.8278)

- Umbral seleccionado dentro de la muestra: ninguno
- Veredicto fuera de la muestra: sin umbral seleccionado
- AUROC dentro = 0.5000 IC95 [0.5000; 0.5000]; fuera = 0.5000 IC95 [0.5000; 0.5000]
- la senal no sostiene un umbral con el piso fijado: ningun candidato alcanza 0.8278 con al menos 10 aceptados dentro de la muestra; fuera de la muestra el barrido se informa solo como descripcion

Barrido dentro de la muestra:

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| 0.0000 | 69 | 0 | 1.000 | 0.725 [0.610; 0.816] | n/d | 0 | 0.000 |
| inf | 0 | 69 | 0.000 | n/d  | 0.725 | 19 | 0.345 |

Barrido fuera de la muestra (descriptivo; no se elige con el):

| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | Exactitud derivados | Errores atrapados | Carga de revision |
|---|---|---|---|---|---|---|---|
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| 0.0000 | 34 | 0 | 1.000 | 0.765 [0.600; 0.876] | n/d | 0 | 0.000 |
| inf | 0 | 34 | 0.000 | n/d  | 0.765 | 8 | 0.330 |

## S1: Gemini por categoria de acuerdo con las reglas

- dentro_muestra / sin_prediccion_reglas: 69 casos, 50 aciertos (0.7246)
- fuera_muestra / sin_prediccion_reglas: 34 casos, 26 aciertos (0.7647)

## Recalibracion isotonica (solo nivel)

- ECE fuera de la muestra: 0.1715 -> 0.0435; Brier: 0.1935 -> 0.1796; AUROC: 0.7163 -> 0.7043
- correccion de nivel solamente: la transformacion es monotona no decreciente y no invierte el orden; si agrupa niveles vecinos introduce empates y el AUROC puede cambiar

## Secundarios

- brazo_gemini_solo: no ejecutado: requiere las predicciones de un brazo Gemini solo (change futuro, no propuesto todavia)
- corpus_arbitrado_c206: no ejecutado: el corpus arbitrado de c-206 todavia no existe

## Gobernanza

- cambia_configuracion: false
- ninguna politica quedo confirmada fuera de la muestra: la derivacion por confianza autodeclarada no es reparable por recalibracion en este corpus; la supervision debe apoyarse en otra senal o en muestreo
- el change informa; openspec/config.yaml, settings.py, el prompt y el clasificador no se modifican

## Entradas (SHA-256)

- `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`: `3fb5bacd04f2e9d303f580e4cf2ac4b4c6f2eab628a4fff80a6e1238029cd8fd`
- `evaluation/data/campana/predicciones_independiente.json`: `d5ee19f7b0bf2b56a00026a1bd33a2e11ffeb9b224b6a8efa553460895a915a4`
- `evaluation/data/campana/plantilla_etiquetado.csv`: `c35a58b60aca98dbc5fd03ad280fbba2f8baf2d56444ba7982ada0715f8ccd09`
- `evaluation/data/campana/senales_reglas_c214.csv`: `a7d4a703e2c5b70c3fc898a1c55c50fbad971255285b5e3630cf65f0c983c56a`
