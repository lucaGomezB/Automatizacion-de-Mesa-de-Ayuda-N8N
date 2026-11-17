# Balance neto acotado con el termino de revision (c-236)

Solo lectura, offline y determinista; sin red ni Gemini. Las cifras de este analisis son aditivas: van a la seccion nueva del memo y no reemplazan ningun valor de las secciones 3.1 a 3.45; no cambian el umbral del 85 %, ni los artefactos de c-220 y c-222, ni el corpus. El signo del balance real no se declara fijado: depende del tramo de reanudacion no medido.

## Preregistro

- Fijado en el docstring antes de generar las salidas: True.
- Ciego: False. El metodo, la regla de eleccion de r (media) y los parametros se fijaron en el docstring antes de generar las salidas. El preregistro NO fue ciego: el valor central ya lo publico el tribunal y los anclajes de c-220 y c-222 ya se conocian; no se habia observado la distribucion bootstrap recomputada con el termino de revision.
- Remuestreos: 2000; semilla: 20261021; nivel: 0,95.

## Anclajes reproducidos antes de escribir

- Balance sin revision de c-222: `30,64` horas-persona por trimestre.
- Costo medido: `c = 69,51` s.
- `r` media: `22,06` s sobre `138` duraciones.
- Tasa de revision: `rho = 0,735` (`147/200`).

## Insumos

- `N = 2646`; `dt = 43,82` s.
- `e_aut = 0,2029`; `e_man = 0,1722`.
- `e_aut - e_man = 0,0307`, IC 95 % [-0,0460; 0,1070].
- `rho = 0,735` (147 de 200 casos revisados (regla VIS-005; 07-resultados.tex)).
- `r = 22,0632` s (media de 138 duraciones; seccion 3.31 (c-220); media de las 138 duraciones con duracion_s).
- `c = 69,51` s, IC 95 % [33,4169; 106,5644] (seccion 3.31 (c-220); tramo activo medido, cota inferior del costo).

## Lectura central (cota superior con el tramo activo medido)

- Forma: `B_r = (N/3.600) x [dt - rho x r - (e_aut - e_man) x c]`; `a*_r = 1 - e_man - (dt - rho x r) / c`.
- `B_r = 18,7` horas-persona por trimestre; intervalo condicional (bootstrap percentil al 95 % con c y rho fijos; remuestrea de forma independiente los casos de la referencia comun (emparejamiento de c-222) y las 138 duraciones) 95 % [12,9207; 24,0573].
- `a*_r = 43,1` %; IC 95 % [33,6195; 53,6940] %.
- Cota combinada 95 % [6,7319; 28,1881] (cota combinada del tramo activo medido (no del balance real)).
- Rotulo: cota superior respecto del tramo de reanudacion no medido.

## Costo de equilibrio y margen del tramo no medido

- `c* = 898,8` s (`15,0` min).
- Margen del tramo no medido: `829,2` s (`13,8` min).
- `c*` con `e_aut - e_man = 0,1070`: `258,0` s; margen `188,5` s.

## Sensibilidad al tramo no medido (rejilla de 5, 10 y 15 minutos con revision)

| `c` (min) | `B_r` (h-persona) | IC 95 % de `B_r` | `a*_r` (%) | IC 95 % de `a*_r` (%) | Estado |
|---|---|---|---|---|---|
| 5 | 13,52 | [-3,4074; 30,8519] | 73,58 | [67,0176; 79,8879] | condicional |
| 10 | 6,74 | [-26,9127; 40,8423] | 78,18 | [71,8205; 84,2418] | condicional |
| 15 | -0,03 | [-50,5207; 50,6906] | 79,71 | [73,3087; 85,8253] | condicional |

- Rotulo: sensibilidad al tramo no medido (reanudacion). No es la lectura central; depende del tramo no medido.

## Sensibilidades de `r` y de `rho`

- `r` mediana: `B_r = 25,26` (r mediana (subestima el total; solo sensibilidad)).
- `r` sin solapamiento: `B_r = 20,98` (r de las confirmaciones (D3; variante sin solapamiento)).
- `rho = 1`: `B_r = 14,42` (rho = 1 (aplica r a todo N; sobreestima la revision)).

## Entradas (SHA-256)

- `analisis_costo_derivacion_c220.json`: `2de287514832044ed6a29b5d17a7110ca10af81e5ffc2696f730e67e5c231d1c`
- `analisis_balance_neto_c222.json`: `6b600043ed6e6cea8853d3cf0dafe65d51ef35aa444a931a9c6fcabb2126ee0b`
- `intervenciones.csv`: `eccc094d46d5ad301296428885114e298f52efb0666be4f61c2e6a266d340ba3`
- `plantilla_etiquetado.csv`: `c35a58b60aca98dbc5fd03ad280fbba2f8baf2d56444ba7982ada0715f8ccd09`
- `predicciones_in_sample.json`: `89cf956e82f660dd8675a2d23b7b4d17efd62da542c0ba35bea28e0e54572ede`

