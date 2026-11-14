## ADDED Requirements

### Requirement: Registro aditivo de las cifras de la propagación del arbitraje

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar la sección 3.29
para las cifras de c-218, con una tabla de valores aditivos que incluya, como mínimo: las tres
lecturas de la exactitud fuera de muestra con sus intervalos y su rótulo (primaria o
complementaria); el desglose por origen de la referencia, por bloque y por etapa; las métricas por
clase y la matriz del corpus arbitrado; la sensibilidad y los destinos de error de `Sistemas`; la
calibración descriptiva de la etapa Gemini sobre el corpus arbitrado; el balance neto de
sensibilidad con la tasa fuera de muestra; y los controles de reproducibilidad. Cada valor SHALL
llevar su archivo fuente y el comando que lo produce. La sección SHALL declarar que es aditiva y
MUST NOT modificar ni reemplazar ningún valor ni estado de las secciones 3.1 a 3.28. Ninguna cifra
de c-218 SHALL entrar a la tesis antes de figurar en esta sección.

#### Scenario: Sección aditiva con procedencia

- **WHEN** se lee la sección 3.29
- **THEN** cada valor tiene archivo fuente y comando
- **AND** la sección declara que no reemplaza valores de las secciones 3.1 a 3.28

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones 3.1 a 3.28 antes y después del change
- **THEN** ninguna cifra ni estado cambió

#### Scenario: Orden de incorporación

- **WHEN** se revisa el historial del change
- **THEN** la sección 3.29 se registró antes que cualquier edición de `sections/*.tex` que use sus cifras
