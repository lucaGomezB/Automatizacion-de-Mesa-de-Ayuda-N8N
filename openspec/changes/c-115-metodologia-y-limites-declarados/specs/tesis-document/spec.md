## MODIFIED Requirements

### Requirement: Cálculo reproducible del tamaño muestral

El capítulo de marco metodológico SHALL publicar la fórmula del tamaño muestral,
los insumos empleados (tamaño del universo `N`, nivel de confianza o `z`,
proporción esperada `p` y margen de error `e`) y el resultado, de modo que el
valor declarado sea reproducible aritméticamente. Si la corrección por finitud
se aplica, MUST declararse la variante de la fórmula usada. El valor declarado
del corpus (`n = 200`) MUST ser consistente con los insumos publicados; en caso
contrario, el documento MUST corregir el insumo que no lo reproduce (por ejemplo
el margen de error declarado) o el propio tamaño declarado. El insumo `N` SHALL
ser el universo vigente de días hábiles (`N ≈ 2.646`), no el universo calendario
retirado (`N = 3.700`); con `N ≈ 2.646`, `z = 1,96`, `p = 0,5` y la corrección por
finitud, el margen que reproduce `n = 200` SHALL ser `e ≈ 6,66 %`. El texto MUST
NOT declarar el margen previo de `6,74 %` calculado con `N = 3.700`. El capítulo
SHALL declarar de forma explícita si el tamaño del corpus se fijó a priori por la
fórmula o si se fijó por disponibilidad operativa; cuando el tamaño se fijó por
disponibilidad operativa, el margen `e ≈ 6,66 %` SHALL presentarse como la
precisión que ese tamaño fijo implica con los restantes insumos, y MUST NOT
presentarse como un margen elegido para reproducir el corpus ya construido. La
presentación del margen MUST NOT invertir la secuencia del muestreo (fijar el
margen para obtener un tamaño ya conocido).

#### Scenario: Fórmula e insumos publicados

- **WHEN** se lee la subsección de población, muestra y corpus
- **THEN** el texto enuncia la fórmula del tamaño muestral con la corrección por finitud
- **AND** declara `N`, `z` (o el nivel de confianza), `p` (o `p(1−p)`) y `e`

#### Scenario: Tamaño declarado reproducible

- **WHEN** se recalcula el tamaño muestral a partir de los insumos publicados
- **THEN** el resultado reproduce el tamaño declarado del corpus
- **AND** no se declara un margen de error que, con los demás insumos, arroje un tamaño distinto del publicado

#### Scenario: Insumo N actualizado al universo vigente

- **WHEN** se lee el insumo `N` de la fórmula en el marco metodológico
- **THEN** `N` es `≈ 2.646` (días hábiles)
- **AND** el margen declarado es `e ≈ 6,66 %`
- **AND** no aparece `N = 3.700` ni el margen `6,74 %` asociado a ese universo

#### Scenario: Criterio de fijación del tamaño declarado

- **WHEN** se lee la subsección de población, muestra y corpus
- **THEN** el texto declara explícitamente si el tamaño del corpus se fijó a priori o por disponibilidad operativa
- **AND** el margen `6,66 %` se presenta como la precisión implicada por el tamaño fijo, no como el valor elegido para reproducir el corpus
- **AND** la secuencia del muestreo no se describe como la calibración del margen sobre un tamaño ya obtenido

## ADDED Requirements

### Requirement: Propagación de la dependencia entre etiquetadores y operadores

La tesis SHALL reflejar en las conclusiones la dependencia declarada en el marco
metodológico entre los analistas etiquetadores de la verdad de referencia y los
operadores del brazo manual (las mismas personas). Esa dependencia SHALL figurar
entre las limitaciones del estudio en la discusión, no solo entre las amenazas a
la validez del capítulo metodológico. Las conclusiones MUST NOT calificar el
diseño experimental como «riguroso» ni presentarlo como plenamente independiente
sin matizar la dependencia entre etiquetadores y operadores; la afirmación de
aporte empírico SHALL quedar acotada por la independencia limitada del referente
de comparación.

#### Scenario: Limitación declarada en la discusión

- **WHEN** se lee la subsección de limitaciones del estudio de la discusión
- **THEN** la dependencia entre los etiquetadores de la verdad de referencia y los operadores del brazo manual figura entre las limitaciones
- **AND** la limitación es coherente con la declaración de la misma dependencia en el capítulo metodológico

#### Scenario: Limitación reflejada en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** la dependencia entre etiquetadores y operadores se refleja como un límite del diseño
- **AND** la afirmación de aporte empírico queda acotada por la independencia limitada del referente de comparación

#### Scenario: Sin sobreafirmación de rigor del diseño

- **WHEN** se busca en las conclusiones un calificativo de rigor sobre el diseño experimental
- **THEN** el diseño no se describe como «riguroso» ni como plenamente independiente sin el matiz de la dependencia entre etiquetadores y operadores
- **AND** el sobreclaim señalado por la dimensión 7 del dictamen no subsiste
