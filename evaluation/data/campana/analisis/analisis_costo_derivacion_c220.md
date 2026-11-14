# Costo de la derivacion erronea: descomposicion medida y cota anclada (c-220)

Sobre `eccc094d46d5...` (intervenciones) y `25ef12ba7e4c...` (brazo manual). Las cifras de este analisis son aditivas: van a la seccion 3.31 del memo y no reemplazan ningun valor `vigente` de las secciones 3.1 a 3.30; no cambian el umbral de 85 %, el balance neto `B`, `a*` ni los artefactos congelados.

## Preregistro

- Fijado en el docstring antes de generar las salidas: True.
- Ciego: False. El metodo y la regla de decision se fijaron antes de generar las salidas. El preregistro NO fue ciego: los conteos y los agregados ya se conocian; no se habia observado la distribucion bootstrap.
- Remuestreos: 2000; semilla: 20261021; nivel: 0.95.

## Cobertura de duraciones

- Total de intervenciones: 147; con duracion: 138 (0.9388).
- Casos sin duracion (no imputados): R166, R181, R029, R036, R195, R123, R058, R069, R154.

## Duraciones por `cambio_sector`

| Grupo | n | Media (s) | Mediana (s) | Desvio (s) | IC 95 % media (s) | IC 95 % mediana (s) |
|---|---|---|---|---|---|---|
| `cambio_sector=true` | 24 | 41.8954 | 18.9450 | 54.1217 | [22.7535; 65.6066] | [12.6480; 32.0200] |
| `cambio_sector=false` | 114 | 17.8880 | 8.9425 | 39.5430 | [11.9369; 26.2618] | [8.3030; 9.9825] |

- Diferencia de medias (costo incremental de corregir en la compuerta): 24.0074 s, IC 95 % [3.4169; 50.0644].
- costo incremental de corregir en la compuerta (regimen corto): tiempo adicional de las intervenciones que cambian el sector respecto de las que lo confirman.

## Proxy de rediagnostico (brazo manual)

| Ambito | n | Media (s) | Mediana (s) | IC 95 % mediana (s) |
|---|---|---|---|---|
| Agrupado | 220 | 48.3591 | 45.5000 | [30.0000; 56.5000] |
| `O1` | 110 | 20.1000 | 18.0000 | [16.0000; 19.0000] |
| `O2` | 110 | 76.6182 | 73.0000 | [71.5000; 75.5000] |

- No se elige el operador conveniente: el agrupado es la estimacion y el operador lento es una cota superior de sensibilidad.

## Composicion de `c`

- Metodo de propagacion: propagacion por suma de extremos de los intervalos bootstrap de cada tramo (cota exterior conservadora; no asume independencia).
- Tramo activo medido: correccion en la compuerta (24.0074 s) + re-decision proxy (45.5000 s).
- Tramo anclado (reanudacion): estado `no medido`, cota `no disponible`. no se mide en este corpus; la fuente de interrupcion no se pudo verificar contra su texto completo offline (regla D4.3).
- Escenario bajo (solo medido): punto 69.5074 s, intervalo 95 % [33.4169; 106.5644] s.

## Compuerta de decision D5

- Intervalo compuesto comparado con la banda canonica [600; 900] s.
- Relacion: excluida; rama: B.
- El intervalo [33.4169; 106.5644] s excluye la banda: el valor previo (`10 a 15 min`) no es tiempo-persona activo.
- Se remite a DECISION DEL DUENO; este analisis no recalcula `B` ni `a*`.

## Justificacion del umbral del 85 % (D6)

- Paridad medida `1 - e_man` con `e_man = 0.1722`: 0.8278. El umbral es mas exigente.
- Costo marginal por punto de exactitud: 0.5109 horas-persona por trimestre (`N * 0,01 * c / 3600`, c = 69.5074 s).

## Termino de revision (D7)

- `r` (media de `duracion_s`, 138 casos): 22.0632 s; mediana 9.9565 s.
- Efecto aditivo sobre `B`: 16.2164 horas-persona por trimestre. sensibilidad separada y aditiva (D7): el flujo automatizado SI agrega tiempo de revision, en contra del supuesto del balance; NO se incorpora a `B` ni reescribe 08

## Entradas y SHA-256

| Archivo | SHA-256 |
|---|---|
| `intervenciones.csv` | `eccc094d46d5ad301296428885114e298f52efb0666be4f61c2e6a266d340ba3` |
| `brazo_manual.csv` | `25ef12ba7e4c27ba5489d3daff099c697416d996858299e25ffa57dfa2a4d46f` |
| `resultados.json` | `0604a2b12b5de7b1025438ef8273da34a0b06b5c792f4ad07e08f38c5f658af1` |

