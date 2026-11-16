# Rango de robustez de los tiempos (c-226)

Solo lectura, offline y determinista; sin red ni Gemini. Lectura de sensibilidad/reinterpretacion: el rango de robustez reune escenarios ya calculados y no es una medicion nueva; la cifra primaria 71,2 % y su intervalo [67,2 %; 74,6 %] no cambian. Registro aditivo en la seccion 3.37 del memo.

## Rango del estimando primario

| Descuento | Media manual ajustada (s) | Reduccion de la media | Rol |
|---|---|---|---|
| 0 s | 61,585 | 71,16 % | cifra primaria (cota superior) |
| 5 s | 56,585 | 68,61 % | cota inferior |
| 10 s | 51,585 | 65,57 % | minimo del estimando primario |

Rango del estimando primario: [65,57 %; 71,16 %]; el minimo es el descuento de 10 s.

## Cota de alcance: por canal (intra-canal, no comparable)

| Canal | n | Reduccion de la media |
|---|---|---|
| correo electrónico (minimo intra-canal) | 66 | 51,07 % |
| llamada telefónica | 81 | 76,98 % |
| formulario web | 53 | 93,44 % |

## Cota de alcance: por operador (campana complementaria, no comparable)

| Operador | n | Manual (s) | Automatizado (s) | Reduccion de la media |
|---|---|---|---|---|
| O1 | 110 | 20,1 | 13,3 | 33,8 % |
| O2 | 110 | 76,6 | 15,5 | 79,7 % |
| Agregado | 200 | 47,6 | 14,6 | 69,3 % |

## Efecto de posicion (Spearman) y cota del instrumento

| Operador | rho | p | MDE (rho) | Significativo |
|---|---|---|---|---|
| O1 | -0,0628 | 0,51465 | 0,276 | no |
| O2 | -0,3604 | 0,00011 | 0,276 | si |

Granularidad del redondeo manual: multiplos de 5 s 199/200; de 10 s 180/200. Telefonia: la grabacion esta acotada a un maximo de 45 s, de modo que el tiempo automatizado medido de la llamada es una cota inferior de su duracion real y su reduccion medida es una cota superior de la reduccion telefonica real.

**Nota de no comparabilidad.** Las cotas de alcance (por canal, por operador, efecto de posicion y cota del instrumento) NO son el mismo estimando que el rango primario y no se comparan entre si: son sensibilidad o reinterpretacion, no una medicion nueva.

