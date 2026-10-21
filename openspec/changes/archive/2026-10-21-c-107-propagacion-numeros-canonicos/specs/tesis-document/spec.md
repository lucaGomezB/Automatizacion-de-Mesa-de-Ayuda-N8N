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
NOT declarar el margen previo de `6,74 %` calculado con `N = 3.700`.

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

## ADDED Requirements

### Requirement: Universo de días hábiles y proyección horaria vigente

La tesis SHALL computar el universo de incidentes sobre días hábiles
(`≈ 2.646 = 42 × 63`) y SHALL reportar la proyección de horas-persona liberadas
como `≈ 32,2 h` por trimestre. El documento MUST NOT presentar el universo
calendario retirado (`3.700 = 42 × 88`) ni la proyección `45,0 h` como resultado
vigente. La proyección SHALL ser reproducible con el ahorro medio por incidente
(`43,82 s`) sobre el universo adoptado. El criterio de días hábiles SHALL
declararse coherente con el origen de la tasa diaria de `42` incidentes, tomada de
una semana laboral.

#### Scenario: Universo en días hábiles

- **WHEN** se lee la subsección de población, muestra y corpus y el resumen
- **THEN** el universo declarado es `≈ 2.646` incidentes, obtenido de `42 × 63` días hábiles
- **AND** no se declara `3.700` como universo vigente

#### Scenario: Proyección horaria reproducible

- **WHEN** se lee la proyección de horas-persona liberadas en el resumen, la introducción y la discusión
- **THEN** la proyección declarada es `≈ 32,2 h` por trimestre
- **AND** el cálculo reproduce `43,82 s × 2.646 / 3.600 ≈ 32,2 h`
- **AND** no se declara `45,0 h` como valor vigente

### Requirement: Intervención humana por gate declarada no medida

La tesis SHALL NOT reportar la proporción de intervención humana del `9,5 %` como
resultado vigente. El aporte operativo asociado al gate de revisión humana SHALL
reformularse como no medido, porque no existe registro por caso de la intervención
en `evaluation/predicciones.json`, `evaluation/report.md` ni `data/`, y porque el
gate implementado (`requiere_revision_humana = (confianza < 0,70)`) no dispara
revisión en ningún caso del corpus. El resumen, los resultados, la discusión, las
conclusiones y las recomendaciones MUST NOT conservar la cifra retirada. La
afirmación de que el flujo automatizado corrió "sin intervención humana" SHALL
reconciliarse con la definición de las dos dimensiones rotuladas de la variable.

#### Scenario: Cifra retirada ausente

- **WHEN** se busca "9,5 %" o "19 casos" como intervención humana en el PDF compilado
- **THEN** no aparece la cifra del 9,5 % presentada como resultado de intervención
- **AND** el aporte operativo se declara no medido con la evidencia disponible

#### Scenario: Aporte operativo reformulado

- **WHEN** se lee la subsección de reducción de la intervención humana y la discusión
- **THEN** el texto declara que la intervención por gate no fue medida
- **AND** explica que el gate implementado no escala casos en el corpus, en lugar de afirmar una reducción porcentual no sustentada

#### Scenario: Coherencia con "sin intervención humana"

- **WHEN** se compara la afirmación del protocolo de pruebas con la subsección de reducción de intervención humana
- **THEN** ambas describen la misma definición rotulada de la variable
- **AND** no se sostiene simultáneamente que hubo 9,5 % de intervención y que el flujo corrió sin intervención humana

### Requirement: Declaración del estado de la hipótesis principal

El resumen, la discusión y las conclusiones SHALL declarar el estado de la
hipótesis principal como parcialmente confirmada y parcialmente refutada: se
confirma en la reducción del tiempo de registro y se refuta en el umbral de
clasificación (`73,5 %` de exactitud y macro-F1 `0,5207`, por debajo de `85 %` y
`0,85`). El resumen MUST NOT permitir inferir una confirmación plena de la
hipótesis. La declaración SHALL distinguir las sub-hipótesis de tiempo,
intervención humana y exactitud o F1.

#### Scenario: Estado parcial declarado en el resumen

- **WHEN** se lee el resumen en español y el abstract
- **THEN** se declara que la hipótesis principal se confirma en tiempo y se refuta en clasificación
- **AND** no se presenta el umbral de clasificación como alcanzado

#### Scenario: Estado parcial declarado en discusión y conclusiones

- **WHEN** se leen la discusión y las conclusiones
- **THEN** el estado de la hipótesis principal se declara parcialmente confirmado y parcialmente refutado
- **AND** la refutación se ancla en las métricas de clasificación reportadas

### Requirement: Costo de API consistente con el universo vigente

La estimación del costo de inferencia en la discusión SHALL recalcularse sobre el
universo vigente de días hábiles (`≈ 2.646` incidentes trimestrales), no sobre el
universo calendario retirado (`3.700`). El costo declarado SHALL conservar la cota
superior de `2 USD` por trimestre y declarar el porcentaje de casos que requieren
inferencia externa (`34,5 %`).

#### Scenario: Costo recalculado sobre el universo vigente

- **WHEN** se lee la estimación de costo de API en la discusión
- **THEN** el volumen declarado es `≈ 2.646` incidentes trimestrales
- **AND** el costo se recalcula con ese volumen y el porcentaje `34,5 %` de inferencia externa
- **AND** no se declara el costo con el volumen retirado de `3.700`
