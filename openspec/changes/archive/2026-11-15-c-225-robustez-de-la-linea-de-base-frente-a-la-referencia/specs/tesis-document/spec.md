## ADDED Requirements

### Requirement: Robustez de la brecha frente a la referencia en resultados y discusión

`07-resultados.tex` SHALL incluir, junto a `tab:linea-base-clasica`, una tabla o párrafo que informe
la brecha híbrido menos línea de base clásica con su IC 95 % sobre los tres subconjuntos de
referencia: consenso `E3`/`E4` (`n = 142`), `150` originales sin exclusión (`n = 150`) y corpus
arbitrado completo (`n = 206`), con la fuente (`analisis_robustez_linea_de_base_c225.json`). El
bloque SHALL rotularse como sensibilidad o robustez y MUST NOT presentarse como una medición nueva.
`08-discusion.tex` SHALL leer el resultado en la limitación sobre la comparación con clasificadores
alternativos y SHALL declarar que la conclusión sobre la línea de base no depende de una sola
elección de referencia. La incorporación MUST NOT cambiar `0,6893/206`, `0,7024`, el veredicto del
umbral `0,85` ni ningún otro valor canónico, y su crecimiento neto de páginas SHALL registrarse en el
libro mayor de `dictamen-correcciones.md`.

#### Scenario: Brecha por subconjunto presente en resultados

- **WHEN** se lee `07-resultados.tex` junto a `tab:linea-base-clasica`
- **THEN** figura la brecha con su IC en los tres subconjuntos
- **AND** el bloque se rotula como sensibilidad o robustez y remite a su fuente

#### Scenario: Lectura acotada en la discusión

- **WHEN** se lee la limitación sobre la comparación con clasificadores alternativos en `08-discusion.tex`
- **THEN** el texto declara que la conclusión sobre la línea de base no depende de una sola referencia
- **AND** no presenta la lectura múltiple como una medición nueva

#### Scenario: Cifras canónicas intactas

- **WHEN** se comparan las cifras del bloque con el memo canónico
- **THEN** `0,6893/206`, `0,7024` y el veredicto del umbral `0,85` no cambian
- **AND** el crecimiento de páginas queda registrado en el libro mayor
