# Balance neto recalculado con el costo medido (c-222)

Solo lectura, offline y determinista; sin red ni Gemini. Las cifras de este analisis son aditivas: van a la seccion nueva del memo y no reemplazan ningun valor de las secciones 3.1 a 3.32; no cambian el umbral de 85 %, el costo supuesto de la rejilla, los artefactos congelados ni el corpus.

## Anclajes reproducidos antes de escribir

- Costo medido: `c = 69,51` s (redondeado `69,51`).
- Celdas de la 3.21: 25,4, 18,7, 11,9.
- IC de la 3.21: [8,6000; 42,4000], [-15,0000; 52,5000], [-38,6000; 62,7000].
- Conteos: casos 138, errores del automatizado 28, errores manuales 26, derivaciones 151.

## Insumos

- `N = 2646`; `dt = 43,82` s.
- `e_aut = 0,2029` (consenso de E1 y E2 (28/138, por caso)); `e_man = 0,1722` (consenso de E1 y E2 (26/151, por derivacion)).
- `e_aut - e_man = 0,0307`, IC 95 % [-0,0460; 0,1070].
- `c = 69,51` s, IC 95 % [33,4169; 106,5644] (seccion 3.31 (c-220); composicion por suma de extremos).

## Escenario central con el costo medido

- `B = 30,6` horas-persona por trimestre; intervalo condicional (bootstrap percentil por caso al 95 % (empareja las derivaciones manuales con su caso) con c constante; recomputado, no interpolado) 95 % [26,7417; 34,5598]; signo positivo.
- `a* = 19,7` %; IC 95 % [13,4270; 25,7722] %.
- Intervalo combinado (suma de extremos: B en las cuatro esquinas (c x (e_aut - e_man)); cota exterior conservadora, no asume independencia) 95 % [23,8276; 35,8138]; signo positivo.

## Grilla superada (5, 10 y 15 minutos)

| `c` (min) | `B` (h-persona) | IC 95 % de `B` | Signo | `a*` (%) | IC 95 % de `a*` (%) | Estado |
|---|---|---|---|---|---|---|
| 5 | 25,4 | [8,6160; 42,3597] | positivo | 68,2 | [61,8639; 74,2091] | condicional |
| 10 | 18,7 | [-14,9757; 52,5117] | no fijado | 75,5 | [69,1673; 81,5125] | condicional |
| 15 | 11,9 | [-38,5674; 62,6637] | no fijado | 77,9 | [71,6017; 83,9469] | condicional |

- Rotulo: sensibilidad del supuesto superado (costo supuesto). Cifras conservadas; no es insumo vigente.

## Sensibilidad mixta de c-221 (no promovida)

- Con `e_aut` ponderada y el `c` medido: `28,2`; con `e_aut` cruda y el `c` medido: `25,1`.
- Promovida: False. sensibilidad que mezcla corpus y referencias (seccion 3.32); NO reemplaza el balance con referencia comun.

## Entradas (SHA-256)

- `analisis_costo_derivacion_c220.json`: `2de287514832044ed6a29b5d17a7110ca10af81e5ffc2696f730e67e5c231d1c`
- `analisis_dictamen_c207.json`: `1c35ebd572289d45bd4f098c10a70635e0beb13f959250a2695c4a88e11a826d`
- `analisis_propagacion_arbitraje_c221.json`: `2df409b1b6f6d6b9d490e40b5dbc30e1221a41b047aeff1f80511a51912a7e8c`
- `plantilla_etiquetado.csv`: `c35a58b60aca98dbc5fd03ad280fbba2f8baf2d56444ba7982ada0715f8ccd09`
- `predicciones_in_sample.json`: `89cf956e82f660dd8675a2d23b7b4d17efd62da542c0ba35bea28e0e54572ede`

