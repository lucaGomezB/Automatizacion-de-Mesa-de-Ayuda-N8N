## ADDED Requirements

### Requirement: Registro de las métricas ampliadas fuera de muestra

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar, en una sección
nueva posterior a la 3.19, cada cifra del análisis ampliado fuera de muestra: la macro-F1
de las cinco clases, la precisión, la sensibilidad, la F1 y el soporte por clase, la
*balanced accuracy*, el kappa de Cohen del clasificador contra la referencia con `p_o`,
`p_e`, PABAK, `n` y su IC, la matriz de confusión `5x5`, el semi-ancho del IC de Wilson
observado con el n efectivo y su comparación con el objetivo de diseño, y los escenarios
de sensibilidad de la exclusión (peor caso, mejor caso y cota) con la regla de decisión.
Cada valor SHALL declararse con su procedencia `archivo` (la salida del script de solo
lectura, `analisis/analisis_fuera_de_muestra_c205.json`), el comando reproducible que lo
produce y su estado en `{vigente, retirado, condicional}`. La sección SHALL declarar que
los escenarios de exclusión son `condicional` (sensibilidad, no medición) y SHALL anunciar
la numeración consecutiva de la Sección 3 en el encabezado del memo. La incorporación MUST
NOT cambiar el valor ni el estado de ningún valor `vigente` de las Secciones 3.1 a 3.19.

#### Scenario: Cifras ampliadas con procedencia y estado

- **WHEN** se recorre la sección nueva del memo
- **THEN** cada cifra (macro-F1, por clase con soporte, *balanced accuracy*, kappa, matriz, potencia y escenarios de exclusión) declara su procedencia, su comando y un estado en `{vigente, retirado, condicional}`
- **AND** ninguna cifra queda sin fuente verificable

#### Scenario: Escenarios de exclusión rotulados condicionales

- **WHEN** se leen las entradas del sesgo de exclusión
- **THEN** el peor caso, el mejor caso y la cota llevan estado `condicional` con la nota de que son sensibilidad, no medición
- **AND** la regla de decisión figura explícita

#### Scenario: Valores vigentes intactos

- **WHEN** se compara el memo antes y después del change
- **THEN** ningún valor `vigente` de las Secciones 3.1 a 3.19 cambia de valor ni de estado
- **AND** la sección nueva ocupa el siguiente número libre y la numeración de la Sección 3 queda consecutiva y sin duplicados

#### Scenario: Encabezado con el upsert

- **WHEN** se lee el encabezado del memo
- **THEN** figura la entrada de upsert de c-205 que anuncia la sección nueva
- **AND** se declara que no modifica ningún valor `vigente` previo
