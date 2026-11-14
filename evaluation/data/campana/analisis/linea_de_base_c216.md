# Línea de base de c-216 (evidencia de partida)

Capturada antes de editar, desde la raíz del repositorio y sobre el árbol de trabajo.

- HEAD: `42bb0dc91967471caa20b80e0196c011cd8efdc7`
- `git status` al inicio: limpio

## Entradas versionadas y conteos (tarea 1.1)

| Archivo | SHA-256 |
|---|---|
| `corpus_independiente_arbitrado.json` | `cb2874e649fb932c00b536100025c0a0137b3314ab12d45234e4c29049adc67e` |
| `predicciones_arbitrado.json` | `cb8aba6089dde9868c61740fba713fb75923ee32317370c46e0daeb52a01d5d5` |
| `doble_etiquetado_arbitrado.csv` | `7993f3ffda7ae7b380833a41b226ed3a6b4f6aaa36f3fbed66fb52682a61d2a4` |
| `arbitraje_tres_vias.json` | `4c85ab43bf28cac228caa35a6aaf3863deb327767cba31fbe850b43d2efe6a61` |

- Casos del corpus: `206`
- Filas de etiquetado: `476`
- Arbitrados por E5: `64`
- Casos de tres vías: `6`

## Regla de forma `sent_c197.py` (tarea 1.2)

```
# Regla D1 c-197 — docs/Tesis/v10 (IA)/paper/sections
Archivo                      Oraciones   >40   >60  de modo que   max
00-glosario.tex                      1     0     0            0    17
00-portada.tex                       1     1     1            0    81
00-resumen.tex                      23     1     0            0    51
01-introduccion.tex                 98    17     0            1    59
02-marco-teorico.tex               103    26     1            0    62
03-estado-del-arte.tex              56    19     2            0    96
04-marco-metodologico.tex          204    35     0            3    56
05-arquitectura.tex                 65    14     1            0    62
06-implementacion.tex              114    27     2            0    84
07-resultados.tex                  224    35     3            4    85
08-discusion.tex                   201    28     3            0    91
09-conclusiones.tex                 54     5     2            0    72
10-recomendaciones.tex              62    20     5            1    98
11-aspectos-legales.tex             74    26     3            1    65
12-anexos.tex                      243    32     1            4    76
---------------------------------------------------------------------
TOTAL                             1523   286    24           14      
Porcentaje de oraciones de mas de 40 palabras: 18.78 %
```

## Repeticiones en prosa de las cifras fuera de muestra (tarea 1.2)

| Cifra | Archivo:línea | Tipo |
|---|---|---|
| `0,8447` | `07-resultados.tex:312` | prosa |
| `0,8447` | `07-resultados.tex:316` | prosa |
| `0,8447` | `07-resultados.tex:332` | tabla |
| `0,8447` | `08-discusion.tex:8` | prosa |
| `0,8447` | `08-discusion.tex:20` | prosa |
| `0,8447` | `08-discusion.tex:60` | prosa |
| `0,8447` | `09-conclusiones.tex:24` | tabla |
| `0,6893` | `07-resultados.tex:316` | prosa |
| `0,6893` | `07-resultados.tex:342` | tabla |
| `0,6893` | `07-resultados.tex:350` | prosa |
| `0,6893` | `07-resultados.tex:362` | tabla |
| `0,6893` | `09-conclusiones.tex:24` | tabla |
| `0,6893` | `09-conclusiones.tex:37` | prosa |

## Párrafos de `11-aspectos-legales.tex` (tarea 1.2)

| Línea | Caracteres |
|---|---|
| 10 | 1756 |
| 14 | 2441 |
| 18 | 1404 |
| 28 | 1121 |
| 36 | 1024 |
| 38 | 1527 |
| 42 | 1907 |

## PDF vigente y estado de compilación (tarea 1.2)

- Páginas: `147`
- SHA-256 de `main.pdf`: `6ac2ef52ce9a990341864bac32f1c41675fdc4cedd52a65c8113fee1f8f0e81c`
- `compilacion.md` vigente: 0 errores fatales, 0 referencias indefinidas, 0 citas indefinidas, 0 etiquetas duplicadas, 14 `Overfull \hbox` (máximo 52,5 pt).
- Motor: XeTeX (TeX Live 2026); Biber 2.22.

Esta línea de base es la referencia contra la que la tarea 8.4 verifica que ningún número canónico, corpus, predicción, configuración ni artefacto congelado cambió.
