## ADDED Requirements

### Requirement: OOS-018 — Resultado sobre los 150 casos arbitrados y métricas por clase estimables

Cuando la referencia del corpus independiente quede arbitrada por el tercer etiquetador
(`discordant-arbitration`), el bloque fuera de muestra SHALL reportarse sobre los `150`
casos (n efectivo `150`), sin exclusión por discordancia, y SHALL declarar que el sesgo de
exclusión de la etapa previa (n efectivo `103`) quedó removido. Las métricas por clase de
`Sistemas` y `Bases de Datos` SHALL reportarse como estimables con el soporte ampliado, y
la matriz de confusión `5x5` SHALL recalcularse sobre los `150` casos. El resultado
anterior sobre `103` SHALL conservarse rotulado como estimación con exclusión, sin
reemplazarse silenciosamente.

#### Scenario: Resultado sobre los 150 casos

- **WHEN** se lee el bloque fuera de muestra tras el arbitraje
- **THEN** figura el n efectivo `150` sin exclusión por discordancia
- **AND** se declara que el sesgo de exclusión de la etapa previa quedó removido

#### Scenario: Clases chicas estimables

- **WHEN** se leen las métricas por clase del corpus arbitrado
- **THEN** `Sistemas` y `Bases de Datos` figuran como estimables con su soporte ampliado
- **AND** la matriz de confusión `5x5` está calculada sobre los `150` casos

#### Scenario: Estimación previa conservada

- **WHEN** se compara con el resultado de c-191
- **THEN** la estimación sobre los `103` casos con exclusión se conserva rotulada como tal
- **AND** no se elimina ni se presenta como si fuera la del corpus arbitrado
