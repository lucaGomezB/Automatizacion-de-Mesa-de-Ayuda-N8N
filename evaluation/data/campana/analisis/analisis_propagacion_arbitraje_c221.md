# Propagacion del arbitraje fuera de muestra (c-221)

Solo lectura, offline y determinista; sin red ni Gemini. Las cifras de este analisis son aditivas: van a la seccion 3.32 del memo y no reemplazan ningun valor `vigente` de las secciones 3.1 a 3.31; no cambian el umbral de 85 %, el balance neto `B`, `a*` ni los artefactos congelados.

## Anclajes reproducidos antes de escribir

- Exactitud estricta cruda del corpus arbitrado: 142/206; macro-F1 0,7024.
- Lectura con exclusion (etapa previa): 87/103; ponderada 0,8146.
- ECE 0,1715 y Brier 0,1935 sobre los 34 casos Gemini con consenso.
- Cardinalidades: arbitrados 64, discordantes originales 47, refuerzo 56, tres vias 6.
- Balance: celda +6,9 reproducida (6,9); referencia comun [25.4, 18.7, 11.9].

## Tres lecturas de la exactitud estricta fuera de muestra

| Lectura | Rotulo | Aciertos | n | Exactitud | IC 95 % | Limite superior < 0,85 |
|---|---|---|---|---|---|---|
| Cruda (arbitrado) | primaria | 142 | 206 | 0,6893 | [0,6231; 0,7486] | True |
| Ponderada | complementaria | - | 206 | 0,7489 | [0,6822; 0,8099] | True |
| 150 originales sin exclusion | complementaria | 112 | 150 | 0,7467 | [0,6715; 0,8095] | True |

- Replicas descartadas por falta de alguna clase en la ponderada: 0.

## Desglose por origen, bloque, etapa y canal

### Por origen

| Grupo | Aciertos | n | Exactitud | IC 95 % Wilson |
|---|---|---|---|---|
| arbitraje_e5 | 33 | 64 | 0,5156 | [0,3958; 0,6337] |
| consenso_e3_e4 | 109 | 142 | 0,7676 | [0,6916; 0,8295] |

### Por bloque

| Grupo | Aciertos | n | Exactitud | IC 95 % Wilson |
|---|---|---|---|---|
| consenso_diseno_original | 87 | 103 | 0,8447 | [0,7625; 0,9021] |
| discordantes_diseno_original | 25 | 47 | 0,5319 | [0,3923; 0,6667] |
| refuerzo | 30 | 56 | 0,5357 | [0,4070; 0,6598] |

### Por etapa

| Grupo | Aciertos | n | Exactitud | IC 95 % Wilson |
|---|---|---|---|---|
| deterministic | 88 | 115 | 0,7652 | [0,6800; 0,8333] |
| gemini | 54 | 91 | 0,5934 | [0,4907; 0,6886] |

### Por canal

| Grupo | Aciertos | n | Exactitud | IC 95 % Wilson |
|---|---|---|---|---|
| Correo | 50 | 78 | 0,6410 | [0,5303; 0,7385] |
| Formulario Web | 36 | 58 | 0,6207 | [0,4920; 0,7344] |
| Telefono | 56 | 70 | 0,8000 | [0,6918; 0,8770] |

## Sistemas con soporte ampliado

- Soporte: 61 (21 originales, 40 de refuerzo); sensibilidad 0,5082; F1 0,5905.
- Destinos de error: {'Soporte Tecnico Software': 16, 'Seguridad Informatica': 8, 'Bases de Datos': 3, 'Soporte Tecnico Hardware': 3}.

## Calibracion descriptiva (etapa Gemini)

- Arbitrado (n = 91): exactitud 0,5934, confianza media 0,9055, ECE 0,3209, Brier 0,3258, AUROC 0,6912. Umbral seleccionado: None.
- Contraste de 34 con consenso: ECE 0,1715; Brier 0,1935.

## Balance neto de sensibilidad

- Rotulo: sensibilidad. sensibilidad que mezcla corpus y referencias; NO reemplaza el balance con referencia comun de la seccion 3.21
- Formula: B = (N/3600) * [dt - (e_aut - e_man) * c]; N = 2646; dt = 43,82 s; e_man = 0,1722.
- e_aut ponderada (0,2511): 5 min: 14,8, 10 min: -2,6, 15 min: -20,0; c medido 69,51 s: 28,2.
- e_aut cruda (0,3107): 5 min: 1,7, 10 min: -28,9, 15 min: -59,4; c medido 69,51 s: 25,1.

## Reproducibilidad

- Diferencias entre corridas en 103 casos comunes: sector [], etapa [], confianza ['I026', 'I043', 'I050', 'I055', 'I067', 'I084', 'I085'].
- `predicciones_arbitrado.json`: commit 1b62fdb, alcanzable desde main True, versionado por None.
- `predicciones_independiente.json`: commit 561b3c4, alcanzable desde main False, versionado por 1b17e55.

## Cuotas observadas y ventana del refuerzo

- Canal de los 150: {'Correo': 50, 'Formulario Web': 40, 'Telefono': 60}; canal del refuerzo: {'Correo': 28, 'Formulario Web': 18, 'Telefono': 10}.
- Sector del refuerzo: {'Sistemas': 40, 'Soporte Tecnico Hardware': 2, 'Bases de Datos': 2, 'Soporte Tecnico Software': 8, 'Seguridad Informatica': 4}.
- Ventana del refuerzo: 2026-11-13T12:12:44-03:00 a 2026-11-13T18:12:03-03:00 (129 filas).

## Entradas (SHA-256)

- `corpus_independiente_arbitrado.json`: `cb2874e649fb932c00b536100025c0a0137b3314ab12d45234e4c29049adc67e`
- `predicciones_arbitrado.json`: `cb8aba6089dde9868c61740fba713fb75923ee32317370c46e0daeb52a01d5d5`
- `predicciones_independiente.json`: `d5ee19f7b0bf2b56a00026a1bd33a2e11ffeb9b224b6a8efa553460895a915a4`
- `arbitraje_tres_vias.json`: `4c85ab43bf28cac228caa35a6aaf3863deb327767cba31fbe850b43d2efe6a61`
- `doble_etiquetado_arbitrado.csv`: `7993f3ffda7ae7b380833a41b226ed3a6b4f6aaa36f3fbed66fb52682a61d2a4`
- `corpus_evaluacion_pseudonimizado.json`: `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`

