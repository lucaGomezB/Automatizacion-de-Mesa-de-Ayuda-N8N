## ADDED Requirements

### Requirement: Registro aditivo de las cifras de la propagación del arbitraje

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar la sección de c-221
para las cifras de c-221, con el primer número de sección libre al aplicar, y con una tabla de
valores aditivos que incluya, como mínimo: las tres lecturas de la exactitud fuera de muestra con
sus intervalos y su rótulo (primaria o complementaria); el desglose por bloque, por etapa y por
canal; las métricas por clase y la matriz del corpus arbitrado; la sensibilidad y los destinos de
error de `Sistemas`; la calibración descriptiva de la etapa Gemini sobre el corpus arbitrado; el
balance neto de sensibilidad con la tasa fuera de muestra; y los controles de reproducibilidad.
La exactitud por origen de la referencia (consenso de `E3` y `E4` frente a arbitraje de `E5`)
SHALL figurar como remisión a la sección de c-219 cuando esta exista en el memo, sin registrar de
nuevo su valor; solo si la sección de c-219 no existe al aplicar, se registra en la sección de
c-221 con la nota de conciliación de OOS-021. Cada valor SHALL llevar su archivo fuente y el
comando que lo produce. La sección SHALL declarar que es aditiva y MUST NOT modificar ni reemplazar
ningún valor ni estado de las secciones previas del memo. Ninguna cifra de c-221 SHALL entrar a la
tesis antes de figurar en esta sección.

#### Scenario: Sección aditiva con procedencia

- **WHEN** se lee la sección de c-221
- **THEN** cada valor tiene archivo fuente y comando
- **AND** la sección declara que no reemplaza valores de las secciones previas del memo

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones previas del memo antes y después del change
- **THEN** ninguna cifra ni estado cambió

#### Scenario: Orden de incorporación

- **WHEN** se revisa el historial del change
- **THEN** la sección de c-221 se registró antes que cualquier edición de `sections/*.tex` que use sus cifras
