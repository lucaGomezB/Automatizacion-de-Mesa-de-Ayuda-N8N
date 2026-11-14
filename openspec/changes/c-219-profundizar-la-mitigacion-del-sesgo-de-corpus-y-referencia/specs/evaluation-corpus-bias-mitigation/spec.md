## Purpose

Medir de forma offline y reproducible dos amenazas de diseño del criterio 4 del dictamen CONEAU:
el sesgo del vocabulario del filtro determinístico ajustado con el mismo corpus con el que se lo
evalúa, y la dependencia del resultado respecto de la fragilidad de la referencia de verdad, sin
cambiar ningún valor canónico, sin reclasificar, sin reentrenar y sin corrida paga por defecto.

## ADDED Requirements

### Requirement: CBM-001 — Alcance, entradas versionadas y operación offline

El análisis SHALL medir solo (a) el efecto del vocabulario del filtro determinístico sobre la
cobertura, la precisión y el conjunto de cortocircuito de la etapa determinística, y (b) la
dependencia de la exactitud estricta respecto de la robustez de la referencia de verdad. SHALL leer
exclusivamente artefactos versionados: `evaluation/data/campana/corpus_independiente_arbitrado.json`,
`evaluation/data/campana/predicciones_arbitrado.json`,
`evaluation/data/campana/doble_etiquetado_arbitrado.csv` y
`evaluation/data/campana/arbitraje_tres_vias.json`. MUST NOT invocar a Gemini, a la red ni a un
servicio externo, MUST NOT modificar el corpus, las predicciones, el vocabulario vigente ni ningún
valor canónico, y MUST NOT requerir trabajo de campo. Antes de medir, el análisis SHALL reproducir
los anclajes canónicos: la etapa determinística cortocircuita `115` casos con `88` aciertos
(`0,7652`) sobre los `206`, y el híbrido congelado `hybrid-v3` acierta `142/206` (`0,6893`) en
exactitud estricta; si no los reproduce, SHALL abortar sin escribir salidas.

#### Scenario: Anclajes reproducidos

- **WHEN** el análisis se ejecuta sobre los cuatro artefactos versionados
- **THEN** reproduce `115` casos de cortocircuito con `88` aciertos de la etapa determinística y `142/206` del híbrido antes de medir
- **AND** registra el SHA-256 de cada entrada leída

#### Scenario: Inconsistencia detectada

- **WHEN** el conteo de casos, el número de arbitrados, los de tres vías o los anclajes no coinciden con los artefactos
- **THEN** el análisis termina con error y no escribe archivos de salida

#### Scenario: Sin red ni escritura fuera de su carpeta

- **WHEN** el análisis corre dos veces seguidas
- **THEN** no se realiza ninguna llamada de red ni a Gemini y `git status` no muestra archivos modificados por la ejecución

### Requirement: CBM-002 — Vocabulario corpus-blind fijado antes de medir

El análisis SHALL derivar un vocabulario alternativo a partir de una fuente externa documentada —la
taxonomía sectorial canónica más un glosario público de mesa de ayuda— sin leer las descripciones del
corpus de evaluación, y SHALL fijarlo y versionarlo en un artefacto propio **antes** de medir, con la
fuente, el procedimiento de derivación y el SHA-256. La independencia del vocabulario respecto del
corpus SHALL declararse como **procedimental** (no se inspeccionó el corpus al derivarlo), no como
propiedad de su contenido. El vocabulario corpus-blind SHALL cubrir las cinco clases canónicas
exactas, sin tildes, y el análisis MUST NOT reemplazar el vocabulario vigente `V1` ni el clasificador
de producción.

#### Scenario: Vocabulario versionado antes de medir

- **WHEN** se lee el artefacto del vocabulario corpus-blind
- **THEN** figura su fuente externa, el procedimiento de derivación y su SHA-256
- **AND** el vocabulario se fijó en un commit anterior a la corrida que produce las mediciones

#### Scenario: Independencia procedimental declarada

- **WHEN** se lee el método del análisis
- **THEN** se declara que el vocabulario se derivó sin inspeccionar las descripciones del corpus
- **AND** no se afirma que sus términos no aparezcan en el corpus

### Requirement: CBM-003 — Re-medición de la etapa determinística y cuantificación del sesgo

El análisis SHALL re-medir la etapa determinística sobre los `206` casos arbitrados con el
vocabulario corpus-blind y con un control de ablación de los términos derivados del corpus
(equivalente a `V0`, reusando la evidencia de c-142), y SHALL informar para cada vocabulario la
cobertura (casos con al menos un match), el número de casos de cortocircuito, la precisión estricta
sobre los casos cortocircuitados con su intervalo de Wilson y la diferencia de cobertura y de
precisión frente a `V1`. El análisis SHALL rotular el delta como **sensibilidad al ajuste del
vocabulario**, no como exactitud corregida, y SHALL declarar que las cifras se calculan sobre
conjuntos de casos distintos cuando corresponda.

#### Scenario: Métricas por vocabulario informadas

- **WHEN** se lee la salida de la ablación
- **THEN** figuran, para `V1`, el vocabulario corpus-blind y el control `V0`, la cobertura, el cortocircuito, la precisión con IC de Wilson y el delta frente a `V1`
- **AND** el delta se rotula como sensibilidad, no como medición de una exactitud verdadera

#### Scenario: Vocabulario vigente intacto

- **WHEN** se compara el vocabulario vigente `V1` antes y después del change
- **THEN** `App/Backend/app/classifiers/keywords.py` no cambia
- **AND** el clasificador de producción no se modifica

### Requirement: CBM-004 — Análisis del subconjunto de alto acuerdo de la referencia

El análisis SHALL construir, desde `arbitraje_tres_vias.json`, el subconjunto de **consenso**
(`origen = consenso_e3_e4`, `n = 142`) y el subconjunto **arbitrado** (`origen = arbitraje_e5`,
`n = 64`), y SHALL informar la exactitud estricta del clasificador congelado en cada uno y en el
total de `206`, con su intervalo de Wilson. SHALL informar además el subconjunto de discordancia de
tres vías (`tres_vias = true`, `n = 6`). El análisis SHALL declarar que el subconjunto literal donde
`E3`, `E4` y `E5` coinciden es **vacío por construcción**, porque `E5` solo etiquetó los casos
discordantes, y MUST NOT elegir una etiqueta verdadera ni presentar la diferencia entre subconjuntos
como causalidad de la referencia.

#### Scenario: Exactitud por subconjunto informada

- **WHEN** se lee la salida del análisis de subconjuntos
- **THEN** figuran la exactitud estricta del consenso (`n = 142`), del arbitrado (`n = 64`) y del total (`206`), cada una con su IC de Wilson
- **AND** figuran los `6` casos de tres vías como subconjunto propio

#### Scenario: Conjunto vacío declarado y sin causalidad

- **WHEN** se lee el método y la lectura del análisis
- **THEN** se declara que el subconjunto `E3` = `E4` = `E5` es vacío por construcción
- **AND** no se afirma que la referencia cause la diferencia de exactitud entre subconjuntos

### Requirement: CBM-005 — Salidas versionadas, determinismo y registro canónico

El análisis SHALL implementarse como un script de solo lectura en
`evaluation/data/campana/analisis/analisis_sesgo_corpus_referencia_c219.py` y SHALL escribir
`analisis_sesgo_corpus_referencia_c219.json`, `analisis_sesgo_corpus_referencia_c219.md` y
`analisis_sesgo_corpus_referencia_c219.SHA256SUMS.txt` en esa misma carpeta, en UTF-8 sin BOM y LF.
Dos corridas con las mismas entradas SHALL producir salidas idénticas byte a byte y el script SHALL
imprimir el SHA-256 de cada salida. Cada cifra que llegue a la tesis SHALL registrarse en una sección
nueva del memo canónico con su archivo fuente y el comando que la produce. El change MUST NOT
modificar ningún valor ni estado `vigente` de las secciones anteriores del memo.

#### Scenario: Reproducibilidad byte a byte

- **WHEN** el script se ejecuta dos veces sobre los mismos artefactos
- **THEN** el JSON, el Markdown y el archivo de sumas son idénticos byte a byte
- **AND** el script imprime el SHA-256 de cada salida

#### Scenario: Registro con procedencia

- **WHEN** se buscan en el memo canónico las cifras del análisis
- **THEN** cada una figura con su archivo fuente y el comando que la produce
- **AND** los valores `vigente` de las secciones anteriores conservan su valor y su estado
