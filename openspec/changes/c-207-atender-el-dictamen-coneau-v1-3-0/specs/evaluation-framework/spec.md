## ADDED Requirements

### Requirement: IC bootstrap de la reducción relativa del tiempo de registro

El análisis de c-207 SHALL calcular la reducción relativa de la media
`R = 1 − media(automatizado) / media(manual)` sobre los pares válidos del corpus de evaluación
y su IC percentil al 95 % por bootstrap de pares con reemplazo, usando
`SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP` de `evaluation/metrics.py`. El valor puntual
SHALL reproducir el canónico (`0,7116`) y el cálculo SHALL ser determinista. El análisis SHALL
informar también el IC de la diferencia de medias en segundos.

#### Scenario: Reproducción del valor canónico

- **WHEN** el análisis corre sobre los 200 pares del corpus versionado
- **THEN** el valor puntual de `R` redondea a `0,7116`
- **AND** el IC contiene al valor puntual

#### Scenario: Determinismo

- **WHEN** el análisis corre dos veces con las mismas entradas
- **THEN** las salidas son idénticas byte a byte

#### Scenario: Caso sintético conocido

- **WHEN** todos los pares tienen la misma razón entre tiempos
- **THEN** el IC degenera en el valor puntual

### Requirement: Balance neto recalculado con una referencia común

El análisis de c-207 SHALL verificar contra qué referencia se mide cada tasa de error del
balance neto y SHALL declarar el resultado (`asimetria_confirmada`). Si la asimetría se
confirma, SHALL calcular `e_aut` y `e_man` contra la misma referencia a partir de artefactos
versionados, `B` y `a*` para los costos de 5, 10 y 15 minutos, y un IC por bootstrap por caso
de `e_aut − e_man` y de `B`. Las entradas que no se puedan igualar SHALL declararse en el
bloque como límites.

#### Scenario: Verificación registrada

- **WHEN** el análisis corre
- **THEN** el bloque declara la referencia de `e_aut` y de `e_man` del texto y el valor de `asimetria_confirmada`

#### Scenario: Recálculo con referencia común

- **WHEN** la asimetría está confirmada
- **THEN** el bloque trae `e_aut` y `e_man` contra la misma referencia, con sus conteos, `B`, `a*` y los IC

#### Scenario: Diferencia nula

- **WHEN** en un caso sintético `e_aut` es igual a `e_man`
- **THEN** `B` es igual al ahorro bruto para todo costo
