# Analisis del dictamen CONEAU v1.3.0 (c-207)

Solo lectura; reutiliza `evaluation/metrics.py`, `evaluation/kappa.py` y `evaluation/campana.py`. Sin red, sin Gemini.

## IC de la reduccion relativa del tiempo (rec. 6)

- Pares: 200; reduccion = 0.7116; IC95 [0.6716; 0.7459]
- Diferencia de medias = 43.82 s; IC95 [37.93; 50.33] s
- Metodo: bootstrap percentil remuestreando pares (casos) con reemplazo; semilla 20261021; B = 2000

## Acuerdo entre E3 y E4 (rec. 1)

- fiabilidad inter-etiquetador E3/E4 sobre el sector principal de los 150 casos
- Concordantes 103 de 150 (discordantes 47); acuerdo observado = 0.6867
- kappa de Cohen = 0.6055; IC asintotico [0.5186; 0.6924]; IC bootstrap [0.5175; 0.6839]; p_e = 0.2058; PABAK = 0.6083; rotulo de Landis y Koch: sustancial

## Balance neto con referencia comun (rec. 5)

- Formula: B = (N / 3600) * [dt - (e_aut - e_man) * c]; a* = 1 - e_man - dt / c; N = 2646; dt = 43.82 s; ahorro bruto = 32.21 h-persona por trimestre.
- Verificacion: e_aut del texto = 53/200 (etiquetado original del corpus (sector_asignado)); e_man del texto = 26/151 (consenso de E1 y E2 (138 casos; discordantes excluidos)); e_aut contra el consenso = 28/138.
- asimetria_confirmada: true

### referencia_consenso: consenso de E1 y E2 (138 casos; discordantes excluidos)

- e_aut = 28/138 = 0.2029; e_man = 26/151 = 0.1722
- e_aut - e_man = 0.0307 IC95 [-0.0460; 0.1070] (bootstrap percentil por caso (empareja las derivaciones manuales con su caso); semilla 20261021; B = 2000)

| c (min) | B (h-persona) | IC95 de B | Signo por IC | a* | IC95 de a* |
|---|---|---|---|---|---|
| 5 | 25.4 | [8.6; 42.4] | positivo | 0.6817 | [0.6186; 0.7421] |
| 10 | 18.7 | [-15.0; 52.5] | no fijado | 0.7548 | [0.6917; 0.8151] |
| 15 | 11.9 | [-38.6; 62.7] | no fijado | 0.7791 | [0.7160; 0.8395] |

### referencia_original: etiquetado original del corpus (sector_asignado)

- e_aut = 53/200 = 0.2650; e_man = 77/220 = 0.3500
- e_aut - e_man = -0.0850 IC95 [-0.1600; -0.0129] (bootstrap percentil por caso (empareja las derivaciones manuales con su caso); semilla 20261021; B = 2000)

| c (min) | B (h-persona) | IC95 de B | Signo por IC | a* | IC95 de a* |
|---|---|---|---|---|---|
| 5 | 51.0 | [35.1; 67.5] | positivo | 0.5039 | [0.4373; 0.5709] |
| 10 | 69.7 | [37.9; 102.8] | positivo | 0.5770 | [0.5103; 0.6440] |
| 15 | 88.4 | [40.7; 138.0] | positivo | 0.6013 | [0.5346; 0.6683] |

### Limites no igualables

- unidad de conteo: e_aut se cuenta por caso y e_man por derivacion de operador (13 casos de la referencia de consenso y 20 del corpus completo tienen doble cobertura); el bootstrap empareja las derivaciones con su caso, pero la unidad no se iguala.
- origen del ahorro de tiempo: dt = 43,82 s proviene de la campana 2026-10 (cronometraje con carga del ticket); el brazo manual de la campana complementaria mide solo la decision de sector. dt se trata como constante y su incertidumbre no entra en el IC de B.
- cobertura de la referencia de consenso: la referencia de consenso excluye los casos discordantes entre E1 y E2, que tienden a ser los mas dificiles; ambas tasas quedan acotadas a los casos faciles.
- costo por derivacion erronea: c (5, 10 o 15 min) es un supuesto propio: la campana no cronometra reasignaciones.
- referencia original para el brazo manual: contra el etiquetado original, el acierto estricto del brazo manual es bajo porque el 53,5 % de los casos admite mas de un sector (la comparacion es estricta contra el sector asignado); se informa como segunda referencia comun, no como la principal.

## Entradas (SHA-256)

- `data/corpus_evaluacion_pseudonimizado.json`: `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`
- `evaluation/data/campana/plantilla_etiquetado.csv`: `c35a58b60aca98dbc5fd03ad280fbba2f8baf2d56444ba7982ada0715f8ccd09`
- `evaluation/data/campana/predicciones_in_sample.json`: `89cf956e82f660dd8675a2d23b7b4d17efd62da542c0ba35bea28e0e54572ede`
- `evaluation/data/campana/corpus_campana.json`: `99bbe84b90b6ba66b34aae08c85bd318cd0e9600ad540e58b1a4bd8eccec06a5`
- `evaluation/data/campana/doble_etiquetado_independiente.csv`: `94dc2d739390a4c874e4ecfa70bf8b52266b752ec20d1e47801f2a93a562f6f7`
- `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json`: `6d8d8d017ff80244e24e7677c804da8094f19015d73fb9560ba1ccc8bd2f6846`
