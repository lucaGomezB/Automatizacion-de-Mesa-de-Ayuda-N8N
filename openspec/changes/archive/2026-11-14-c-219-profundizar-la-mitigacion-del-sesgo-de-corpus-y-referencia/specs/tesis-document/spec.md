## ADDED Requirements

### Requirement: Mitigación del sesgo de corpus y de la fragilidad de la referencia en la tesis

`04-marco-metodologico.tex` SHALL definir el método de las dos mediciones: la ablación con un
vocabulario derivado de una fuente externa al corpus, con su independencia declarada como
procedimental, y el análisis del subconjunto de consenso `E3 = E4` frente al arbitrado por `E5`,
con sus supuestos y límites. `07-resultados.tex` SHALL incluir una subsección nueva, con etiqueta
`subsec:sesgo-corpus-referencia`, que informe la cobertura y la precisión de la etapa determinística
bajo el vocabulario vigente, el corpus-blind y el control de ablación, y la exactitud estricta sobre
el subconjunto de consenso (`109/142`), el arbitrado (`33/64`) y el total (`142/206`), con sus
intervalos de Wilson, rotulando el conjunto `E3` = `E4` = `E5` como vacío por construcción.
`08-discusion.tex` SHALL leer ambos resultados como sensibilidad que acota —sin eliminar— las
amenazas «ajuste y evaluación sobre el mismo corpus» y «referencia de verdad frágil» del criterio 4.
La incorporación MUST NOT cambiar `142/206`, `0,6893`, `0,7024` ni ningún otro valor canónico, y su
crecimiento neto de páginas SHALL ser de a lo sumo dos páginas, registrado en el libro mayor de
`dictamen-correcciones.md`.

#### Scenario: Subsección, método y lectura de discusión

- **WHEN** se lee `07-resultados.tex`
- **THEN** existe `subsec:sesgo-corpus-referencia` con la tabla de cobertura/precisión por vocabulario y la tabla de exactitud por subconjunto
- **AND** el capítulo 4 define la ablación con vocabulario externo y el análisis de subconjuntos
- **AND** `08-discusion.tex` remite a la subsección y la rotula como sensibilidad

#### Scenario: Anclajes canónicos y ausencia de sobreafirmación

- **WHEN** se comparan las cifras de la subsección con el memo canónico
- **THEN** la exactitud total es `142/206` (`0,6893`) y el texto no presenta la ablación ni el análisis de subconjuntos como medición de una exactitud verdadera ni como causalidad de la referencia
- **AND** se declara que el subconjunto `E3` = `E4` = `E5` es vacío por construcción

#### Scenario: Crecimiento de páginas acotado y registrado

- **WHEN** se compara el total de páginas del PDF con el de la release de partida
- **THEN** el crecimiento neto es de a lo sumo dos páginas
- **AND** el libro mayor registra el delta y su causa
