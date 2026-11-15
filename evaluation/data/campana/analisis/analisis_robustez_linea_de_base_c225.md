# Robustez de la brecha hibrido menos linea de base (c-225)

Solo lectura, offline y determinista; sin red ni Gemini. Lectura de sensibilidad/robustez: las tres brechas son descriptivas, se reportan juntas y no se corrigen por multiplicidad. No son una medicion nueva ni reemplazan ningun numero canonico: la cifra primaria 0,6893/206, el macro-F1 0,7024 y el veredicto del umbral 0,85 no cambian. Registro aditivo en la seccion 3.36 del memo.

## Metodo

- Subconjuntos: consenso `E3`/`E4` (`n = 142`), `150` originales sin exclusion (`n = 150`) y corpus arbitrado completo (`n = 206`).
- Linea de base: TF-IDF + regresion logistica, semilla 42, entrenada con 200 casos; variante primaria `balanceada`.
- IC 95 % bootstrap percentil pareado con 10000 remuestreos y semilla 20261021; McNemar con `p` exacta y corregida por continuidad.
- Las particiones de contexto son `arbitraje_e5` (64 casos) y `tres_vias` (6 casos); no son subconjuntos de contraste.

## Brecha con la linea de base balanceada

| Subconjunto | n | Aciertos hibrido | Aciertos linea de base | Solo hibrido (b) | Solo linea de base (c) | Brecha | IC 95 % | McNemar |
|---|---|---|---|---|---|---|---|---|
| consenso_e3_e4 | 142 | 109 | 76 | 43 | 10 | 0,2324 | [0,1408; 0,3239] | p = 1,105e-05 (corregido) |
| original_150 | 150 | 112 | 87 | 39 | 14 | 0,1667 | [0,0733; 0,2600] | p = 0,0010 (corregido) |
| arbitrado_completo | 206 | 142 | 101 | 61 | 20 | 0,1990 | [0,1165; 0,2767] | p = 8,812e-06 (corregido) |

## Brecha con la linea de base sin reponderacion

| Subconjunto | n | Aciertos hibrido | Aciertos linea de base | Solo hibrido (b) | Solo linea de base (c) | Brecha | IC 95 % | McNemar |
|---|---|---|---|---|---|---|---|---|
| consenso_e3_e4 | 142 | 109 | 63 | 51 | 5 | 0,3239 | [0,2324; 0,4085] | p = 1,817e-09 (corregido) |
| original_150 | 150 | 112 | 80 | 42 | 10 | 0,2133 | [0,1267; 0,3000] | p = 1,716e-05 (corregido) |
| arbitrado_completo | 206 | 142 | 88 | 69 | 15 | 0,2621 | [0,1845; 0,3398] | p = 7,348e-09 (corregido) |

## Anclas verificadas

| Sistema | consenso_e3_e4 | original_150 | arbitrado_completo |
|---|---|---|---|
| hibrido | 109/142 | 112/150 | 142/206 |
| balanceada | 76/142 | 87/150 | 101/206 |
| sin_repoderacion | 63/142 | 80/150 | 88/206 |

Las lineas de base solo tienen ancla sobre el corpus completo (101/206 y 88/206); sobre los subconjuntos se reportan sin ancla externa y su lectura es descriptiva.

