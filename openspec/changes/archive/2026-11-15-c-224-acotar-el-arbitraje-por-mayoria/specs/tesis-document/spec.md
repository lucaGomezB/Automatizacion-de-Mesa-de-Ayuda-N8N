## ADDED Requirements

### Requirement: Acotación del arbitraje por mayoría en la limitación y los resultados

`08-discusion.tex` SHALL precisar en la limitación 8 que la regla vigente (consenso de `E3` y
`E4`; `E5` cuando difieren) coincide con la etiqueta mayoritaria de `{E3, E4, E5}` en `200` de
`206` casos, y que los `6` casos sin mayoría acotan la exactitud estricta entre `0,6893`
(`142/206`) y `0,7136` (`147/206`). `07-resultados.tex` SHALL registrar ese rango en el párrafo
del arbitraje de `subsec:validacion-fuera-muestra`, rotulado como sensibilidad, y remitir a la
sección del memo canónico que lo registra, sin cambiar las cifras vigentes del párrafo
(`0,6893`, `0,7864`, `0,7489`, `0,7467`, `31/61`). El change MUST NOT cambiar `0,6893`,
`0,7024`, el umbral de `0,85` ni el veredicto del umbral.

#### Scenario: Limitación 8 acotada

- **WHEN** se busca «200 de 206» en `08-discusion.tex`
- **THEN** la línea de la limitación 8 contiene la coincidencia y el rango
- **AND** la fragilidad de la referencia se conserva como limitación de fondo

#### Scenario: Rango en resultados

- **WHEN** se busca «147/206» en `07-resultados.tex`
- **THEN** la línea del párrafo del arbitraje contiene el rango rotulado como sensibilidad
- **AND** las cifras vigentes del párrafo (`0,6893`, `0,7864`, `0,7489`, `0,7467`, `31/61`) no cambian

## MODIFIED Requirements

### Requirement: Trabajos futuros reformulados a partir de lo ejecutado

`10-recomendaciones.tex` MUST NOT proponer como trabajo futuro el sobremuestreo de `Sistemas` con
doble etiquetado y arbitraje por un tercer etiquetador, ni fijar como criterio de éxito que el
arbitraje se ejecute antes de reportar, porque ambas cosas se ejecutaron. La línea de
`subsec:frontera-sistemas` SHALL orientarse al análisis de la taxonomía con los casos disponibles
y SHALL tener criterio de éxito; la de `subsec:corpus-independiente` SHALL proponer un corpus de
composición natural, con cuotas prefijadas y más etiquetadores independientes, y MUST NOT
proponer «arbitraje por mayoría de tres etiquetadores» como mecanismo faltante.

#### Scenario: Líneas ya ejecutadas retiradas

- **WHEN** se leen `subsec:frontera-sistemas` y `subsec:corpus-independiente`
- **THEN** ninguna propone como próximo paso lo ya realizado
- **AND** cada una declara un criterio de éxito

#### Scenario: Mayoría de tres no se propone como faltante

- **WHEN** se busca «mayoría de tres» en `10-recomendaciones.tex`
- **THEN** no hay coincidencias
- **AND** `subsec:corpus-independiente` propone más etiquetadores independientes