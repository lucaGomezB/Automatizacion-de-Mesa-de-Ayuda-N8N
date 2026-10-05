# Delta for sector-taxonomy

## MODIFIED Requirements

### Requirement: TAX-002 — Redistribucion de keywords del clasificador determinista

El clasificador determinista SHALL exponer exactamente los cinco sectores canonicos como vocabulario de salida, derivado de un mapa de keywords redistribuido que cubra los cinco sectores. El mapa SHALL incluir sinonimos, variantes morfologicas y frases representativas por sector, de modo que Hardware y Software (los sectores con mayor soporte real del corpus) tengan cobertura suficiente y NO queden sub-representados. El clasificador MUST NOT emitir `Operaciones` en ninguna circunstancia y MUST NOT quedar sin terminos para ningun sector canonico. Las claves del mapa MUST ser exactamente los cinco strings canonicos, verificable por una invariante estructural (`set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)`), y MUST NOT alterar los cinco strings canonicos ni sus acentos.

#### Scenario: Todos los sectores tienen terminos

- **WHEN** se inspecciona el mapa de keywords del clasificador determinista
- **THEN** cada uno de los cinco sectores canonicos tiene al menos un termino asociado

#### Scenario: Termino de hardware clasifica como Soporte Tecnico Hardware

- **WHEN** el clasificador determinista procesa una descripcion con terminos de hardware de equipos
- **THEN** la prediccion pertenece a `Soporte Tecnico Hardware` y no a `Operaciones`

#### Scenario: Ningun termino produce Operaciones

- **WHEN** el clasificador determinista procesa descripciones representativas de todos los sectores
- **THEN** ninguna prediccion resultante es `Operaciones`

#### Scenario: La invariante de claves se preserva tras ampliar el vocabulario

- **WHEN** se amplia el vocabulario con nuevos sinonimos o frases
- **THEN** las claves del mapa siguen siendo exactamente los cinco sectores canonicos y el assert estructural no se rompe

#### Scenario: Hardware y Software tienen cobertura ampliada

- **WHEN** se inspecciona el vocabulario de `Soporte Tecnico Hardware` y `Soporte Tecnico Software`
- **THEN** cada uno expone un conjunto de terminos mayor o igual al que tenia antes del endurecimiento, guiado por las misclasificaciones del corpus

## ADDED Requirements

### Requirement: Cobertura medida del vocabulario determinista

El sistema SHALL medir la cobertura del vocabulario determinista sobre el corpus de evaluacion, definida como la fraccion de casos en que al menos un termino del mapa hace match. El endurecimiento SHALL reducir la tasa de casos sin match respecto de la linea base y la sobre-prediccion del sector por defecto (linea base: 126 predicciones de `Seguridad Informatica` vs 31 reales en 200 casos) y SHALL reportar la cobertura por sector, de modo que la ampliacion del vocabulario sea verificable con datos y no por inspeccion subjetiva. La medicion MUST ser offline (sin invocar a Gemini) y MUST NOT modificar `evaluation/corpus.py::_a_float`.

#### Scenario: Cobertura reportada por sector

- **WHEN** se corre la medicion offline del vocabulario sobre el corpus
- **THEN** el reporte expone la cobertura global y por sector, y la cantidad de casos sin match

#### Scenario: La cobertura sube respecto de la linea base

- **WHEN** se compara la cobertura tras ampliar el vocabulario contra la linea base medida
- **THEN** la cantidad de casos sin senal es estrictamente menor y ningun sector pierde terminos

#### Scenario: La medicion no invoca al proveedor pago

- **WHEN** se ejecuta la medicion de cobertura
- **THEN** no se realiza ninguna llamada a Gemini y el resultado depende solo del corpus y del mapa de keywords
