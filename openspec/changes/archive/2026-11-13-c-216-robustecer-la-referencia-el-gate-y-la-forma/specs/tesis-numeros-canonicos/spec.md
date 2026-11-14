## ADDED Requirements

### Requirement: Registro aditivo de los valores del análisis de ruido de referencia

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una sección
nueva para los valores del análisis de ruido de referencia de c-216, con una tabla de valores
aditivos que incluya, como mínimo: el kappa `E3`/`E4` `0,6055` y el acuerdo observado `0,6867`
usados como calibración; los `64` casos arbitrados por `E5` y los `6` casos de tres vías; la
intensidad de ruido `λ` calibrada; la mediana y los percentiles `2,5`/`97,5` de la exactitud
estricta y de la macro-F1 bajo referencias alternativas; la fracción `δ` y las cotas inferior y
superior de la exactitud estricta; y la descomposición entre error atribuible a la referencia y
error robusto. Cada valor SHALL llevar su archivo fuente y el comando que lo produce, y la
sección SHALL declarar que es aditiva. La sección MUST NOT modificar ni reemplazar ningún valor
ni estado `vigente` de las secciones 3.1 a 3.26.

#### Scenario: Sección aditiva con procedencia

- **WHEN** se lee la sección nueva del memo canónico
- **THEN** figuran los valores del análisis con su archivo fuente y su comando
- **AND** la sección declara que no reemplaza ningún valor de las secciones 3.1 a 3.26

#### Scenario: Valores previos intactos

- **WHEN** se comparan los valores de las secciones 3.1 a 3.26 antes y después del change
- **THEN** cada valor conserva su cifra y su estado `vigente`, `condicional` o `superado`
- **AND** no se retira ningún número canónico