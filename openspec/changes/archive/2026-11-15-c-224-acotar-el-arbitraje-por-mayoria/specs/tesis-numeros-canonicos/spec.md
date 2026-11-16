## ADDED Requirements

### Requirement: Registro aditivo de las cifras del arbitraje por mayoría

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar la sección de
c-224 con el primer número de sección libre al aplicar, y con una tabla de valores aditivos que
incluya, como mínimo: la coincidencia entre la regla vigente (consenso de `E3` y `E4`; `E5`
cuando difieren) y la etiqueta mayoritaria de `{E3, E4, E5}` (`200` de `206` casos); los `6`
casos sin mayoría con sus identificadores y sus tres etiquetas; el rango de exactitud estricta
(`142/206` a `147/206`); y las métricas por clase en ambos extremos. Cada valor SHALL llevar su
archivo fuente, la clave del JSON y el comando que lo produce. La sección SHALL declarar que es
aditiva y MUST NOT modificar ni reemplazar ningún valor ni estado de las secciones previas del
memo.

#### Scenario: Sección aditiva con procedencia

- **WHEN** se lee la sección de c-224
- **THEN** cada valor tiene archivo fuente, clave y comando
- **AND** la sección declara que no reemplaza valores de las secciones previas del memo

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones previas del memo antes y después del change
- **THEN** ninguna cifra ni estado cambió