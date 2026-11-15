## ADDED Requirements

### Requirement: LBP-04 — Robustez de la brecha frente a la elección de referencia

El sistema SHALL reportar la brecha híbrido menos línea de base clásica, con su intervalo de
confianza, sobre los tres subconjuntos de la referencia que la tesis informa por separado:
consenso `E3`/`E4` (`n = 142`, casos con `origen == "consenso_e3_e4"` en `arbitraje_tres_vias.json`),
los `150` casos del diseño original sin exclusión por discordancia (ids `I001`..`I150` del corpus
arbitrado) y el corpus arbitrado completo (`n = 206`). El cálculo SHALL reutilizar las predicciones
por caso versionadas de ambos clasificadores (línea de base reconstruida con
`evaluation.linea_de_base.predecir` y semilla `42`; híbrido leído de
`evaluation/data/campana/predicciones_arbitrado.json`) y las funciones puras de `evaluation.stats`
y `evaluation.metrics`, sin red, sin Gemini y sin API paga. El contraste por subconjunto y por
variante SHALL usar la misma convención que LBP-01 (tabla 2×2, McNemar con `p` exacta y corregida,
diferencia `(b − c)/n` con IC bootstrap percentil pareado de semilla fija). El artefacto SHALL
declarar que es aditivo, que las tres lecturas son descriptivas y no se corrigen por multiplicidad,
y que no reemplazan ningún número canónico. El script MUST NOT modificar el script ni las salidas de
c-213.

#### Scenario: Brecha reportada en los tres subconjuntos

- **WHEN** se ejecuta el análisis de robustez sobre los artefactos versionados
- **THEN** el artefacto contiene la brecha y su IC 95 % para el subconjunto de consenso `E3`/`E4`, para los `150` originales y para el corpus arbitrado completo, en cada variante de la línea de base
- **AND** cada lectura declara su `n`, sus aciertos y el criterio de McNemar aplicado

#### Scenario: Subconjuntos derivados de los artefactos

- **WHEN** el análisis deriva los subconjuntos
- **THEN** el consenso `E3`/`E4` se toma de `origen == "consenso_e3_e4"` y tiene `142` casos
- **AND** los `150` originales se toman de los ids `I001`..`I150` y tienen `150` casos
- **AND** el corpus arbitrado completo tiene `206` casos
- **AND** si alguna cardinalidad difiere, el análisis termina con error y no escribe salidas

### Requirement: LBP-05 — Anclas verificadas y carácter aditivo del análisis de robustez

Antes de escribir salidas, el análisis de robustez SHALL verificar que los aciertos estrictos
reconstruidos coinciden con los agregados versionados: híbrido `142/206` sobre el arbitrado completo,
`109/142` sobre el consenso `E3`/`E4` y `112/150` sobre los `150` originales; línea de base
balanceada `101/206` y sin re-ponderación `88/206`. Si un ancla no coincide, MUST terminar con error
sin escribir archivos. El análisis SHALL ser determinista (dos corridas producen JSON y MD idénticos
byte a byte, LF, UTF-8 sin BOM, con `SHA256SUMS`) y SHALL registrar el SHA-256 de cada entrada.

#### Scenario: Anclas reproducidas antes de calcular

- **WHEN** el análisis reconstruye las predicciones y reproduce `142/206`, `109/142`, `112/150`, `101/206` y `88/206`
- **THEN** escribe el artefacto con las anclas declaradas y el contraste por subconjunto

#### Scenario: Ancla no reproducida

- **WHEN** alguno de los aciertos reconstruidos difiere del agregado versionado
- **THEN** el análisis termina con error, informa la diferencia y no escribe salidas

#### Scenario: Dos corridas idénticas

- **WHEN** el análisis se ejecuta dos veces sobre los mismos insumos
- **THEN** los SHA-256 de las salidas coinciden
- **AND** los SHA-256 de los insumos no cambian
