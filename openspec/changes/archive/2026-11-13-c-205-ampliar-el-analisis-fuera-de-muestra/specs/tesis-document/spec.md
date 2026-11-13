## ADDED Requirements

### Requirement: Reporte de las métricas ampliadas fuera de muestra y del sesgo de exclusión

La tesis SHALL reportar, además de la exactitud estricta y laxa fuera de muestra ya
declaradas, la macro-F1 de las cinco clases, las métricas por clase con su soporte, la
*balanced accuracy* y el kappa de Cohen del clasificador contra la referencia, tomadas del
memo canónico. `07-resultados.tex` SHALL presentar estas métricas en el bloque fuera de
muestra, rotuladas como estimaciones sobre el n efectivo. `08-discusion.tex` SHALL tratar
explícitamente el sesgo de la exclusión de los discordantes: SHALL declarar los escenarios
de peor caso, mejor caso y la cota, y SHALL enunciar la regla de decisión que ata el peor
caso a la exactitud reportada. La tesis MUST NOT presentar los escenarios de exclusión como
una medición del clasificador sobre los casos excluidos, ni la macro-F1 fuera de muestra
como equivalente de la exactitud de etiqueta única. Los valores SHALL tomarse del memo
canónico y MUST NOT fijarse por separado.

#### Scenario: Métricas ampliadas en Resultados

- **WHEN** se lee el bloque fuera de muestra de `07-resultados.tex`
- **THEN** figuran la macro-F1, las métricas por clase con soporte, la *balanced accuracy* y el kappa del clasificador
- **AND** se rotulan como estimaciones sobre el n efectivo

#### Scenario: Sesgo de exclusión tratado en Discusión

- **WHEN** se lee `08-discusion.tex` en el tratamiento de la validación fuera de muestra
- **THEN** figuran los escenarios de peor caso, mejor caso y cota de la exclusión y la regla de decisión asociada
- **AND** los escenarios se rotulan como sensibilidad, no como medición

#### Scenario: Sin equivalencia ni sobreafirmación

- **WHEN** se lee la presentación de la macro-F1 fuera de muestra
- **THEN** no se la presenta como equivalente de la exactitud estricta
- **AND** no se afirma confirmación fuerte del resultado

#### Scenario: Valores tomados del memo

- **WHEN** se comparan las cifras de la tesis con el memo canónico
- **THEN** cada cifra coincide con el valor `vigente` o `condicional` del memo
- **AND** ninguna cifra se fija por separado del memo
