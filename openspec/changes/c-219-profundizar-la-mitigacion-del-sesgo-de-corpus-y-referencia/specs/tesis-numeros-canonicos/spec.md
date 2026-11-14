## ADDED Requirements

### Requirement: Registro aditivo de los valores de la mitigación del sesgo de corpus y referencia

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una sección nueva
(3.29) con una tabla de valores aditivos que incluya, como mínimo: los anclajes de la etapa
determinística (`115` cortocircuitados y `88` aciertos, `0,7652`) y del híbrido (`142/206`,
`0,6893`); para el vocabulario vigente `V1`, el vocabulario corpus-blind y el control `V0`, la
cobertura, el número de casos de cortocircuito y la precisión con IC de Wilson; y la exactitud
estricta del clasificador sobre el subconjunto de consenso (`n = 142`), el subconjunto arbitrado
(`n = 64`) y el total (`206`), con sus intervalos de Wilson. Cada valor SHALL llevar su archivo
fuente y el comando que lo produce, y la sección SHALL declarar que es aditiva. La sección MUST NOT
modificar ni reemplazar ningún valor ni estado `vigente` de las secciones 3.1 a 3.28.

#### Scenario: Sección aditiva con procedencia

- **WHEN** se lee la sección 3.29 del memo canónico
- **THEN** figuran los valores de la ablación de vocabulario y del análisis de subconjuntos con su archivo fuente y su comando
- **AND** la sección declara que no reemplaza ningún valor de las secciones 3.1 a 3.28

#### Scenario: Valores previos intactos

- **WHEN** se comparan los valores de las secciones 3.1 a 3.28 antes y después del change
- **THEN** cada valor conserva su cifra y su estado `vigente`, `condicional` o `superado`
- **AND** no se retira ningún número canónico
