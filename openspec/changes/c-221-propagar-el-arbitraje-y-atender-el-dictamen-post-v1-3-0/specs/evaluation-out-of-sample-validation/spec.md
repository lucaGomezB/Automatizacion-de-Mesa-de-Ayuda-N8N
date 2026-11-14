## MODIFIED Requirements

### Requirement: OOS-018 — Resultado sobre los 150 casos arbitrados y métricas por clase estimables

Cuando la referencia del corpus independiente quede arbitrada por el tercer etiquetador
(`discordant-arbitration`), el bloque fuera de muestra SHALL reportarse sobre el corpus arbitrado
completo, formado por los `150` casos del diseño original más los casos de refuerzo de clases
chicas (`206` casos en total: `I001`..`I150` e `I151`..`I206`), sin exclusión por discordancia, y
SHALL declarar que el sesgo de exclusión de la etapa previa (n efectivo `103`) quedó removido. La
exactitud estricta cruda sobre el corpus arbitrado completo SHALL ser la cifra primaria. Las
métricas por clase de `Sistemas` y `Bases de Datos` SHALL reportarse como estimables con el
soporte ampliado, y la matriz de confusión `5x5` con precisión, sensibilidad, F1 y soporte por
clase SHALL recalcularse sobre el corpus arbitrado completo. El resultado anterior sobre `103`
SHALL conservarse rotulado como estimación con exclusión, sin reemplazarse silenciosamente.

#### Scenario: Resultado sobre el corpus arbitrado completo

- **WHEN** se lee el bloque fuera de muestra tras el arbitraje
- **THEN** figura el n efectivo del corpus arbitrado completo, sin exclusión por discordancia, con la cantidad de casos originales y de refuerzo
- **AND** se declara que el sesgo de exclusión de la etapa previa quedó removido
- **AND** la exactitud estricta cruda sobre ese corpus figura como cifra primaria

#### Scenario: Clases chicas estimables

- **WHEN** se leen las métricas por clase del corpus arbitrado
- **THEN** `Sistemas` y `Bases de Datos` figuran como estimables con su soporte ampliado
- **AND** la matriz de confusión `5x5` está calculada sobre el corpus arbitrado completo

#### Scenario: Estimación previa conservada

- **WHEN** se compara con el resultado de c-191
- **THEN** la estimación sobre los `103` casos con exclusión se conserva rotulada como tal
- **AND** no se elimina ni se presenta como si fuera la del corpus arbitrado

## ADDED Requirements

### Requirement: OOS-020 — Tres lecturas rotuladas de la exactitud fuera de muestra

El análisis de c-221 (`evaluation/data/campana/analisis/analisis_propagacion_arbitraje_c221.py`)
SHALL calcular sobre `predicciones_arbitrado.json` y `corpus_independiente_arbitrado.json` tres
lecturas de la exactitud estricta: (i) la cruda sobre el corpus arbitrado completo, con intervalo
de Wilson, rotulada como primaria; (ii) la ponderada por la composición por sector del corpus de
ajuste de `200` casos (suma de la sensibilidad de cada clase por su peso), con intervalo bootstrap
percentil por caso de `2000` remuestreos y semilla `20261021`, que informe cuántas réplicas se
descartaron por falta de alguna clase; y (iii) la de los casos del diseño original (`I001`..`I150`)
con referencia arbitrada, con intervalo de Wilson. La ponderada y la de `150` SHALL rotularse como
complementarias y SHALL citar como antecedente de la ponderación el diseño de c-191 y el de c-206.
Para cada lectura el análisis SHALL informar si el límite superior del intervalo queda por debajo
de `0,85`. Antes de escribir salidas, el análisis SHALL verificar que la función de ponderación
reproduce el valor vigente `0,8146` sobre los `103` casos con consenso y que la cruda reproduce
`142/206`; si un anclaje no coincide, MUST terminar con error sin escribir archivos. Las cifras que
figuran en el design como recomputo exploratorio MUST NOT copiarse a la tesis sin que el script las
produzca.

#### Scenario: Tres lecturas con su rótulo

- **WHEN** se ejecuta el análisis
- **THEN** el JSON contiene la lectura cruda primaria, la ponderada con su intervalo bootstrap y la de los casos originales con su intervalo de Wilson
- **AND** cada lectura declara si su límite superior queda por debajo de `0,85`

#### Scenario: Ponderación validada contra un valor vigente

- **WHEN** la función de ponderación se aplica a los `103` casos con consenso
- **THEN** reproduce `0,8146`
- **AND** si no lo reproduce, el análisis termina con error y no escribe salidas

### Requirement: OOS-021 — Desglose por origen de la referencia, por bloque y por etapa

El análisis SHALL informar aciertos, n, exactitud e intervalo de Wilson por origen de la
referencia según `arbitraje_tres_vias.json` (consenso de `E3` y `E4` frente a arbitraje de `E5`),
por bloque (discordantes del diseño original, casos de refuerzo, casos con consenso del diseño
original), por etapa de la cascada (determinística y Gemini) y por canal. SHALL informar además,
para `Sistemas`, la sensibilidad, la precisión, la F1 y el destino de cada error, en total y
separado entre casos originales y de refuerzo, y la composición por sector y por canal de los
casos originales y de los de refuerzo. Los conjuntos SHALL derivarse de los archivos, y el
análisis SHALL verificar que los arbitrados son `64`, los discordantes originales `47`, los casos
de refuerzo `56` (ninguno presente en `predicciones_independiente.json`) y los de tres vías `6`.

#### Scenario: Discordantes originales medidos

- **WHEN** se lee el desglose por bloque
- **THEN** figura la cantidad de aciertos del clasificador sobre los `47` discordantes originales arbitrados

#### Scenario: Conjuntos inconsistentes

- **WHEN** alguna cardinalidad derivada de los archivos difiere de las declaradas
- **THEN** el análisis termina con error y no escribe salidas

### Requirement: OOS-022 — Sensibilidad del balance neto con la tasa fuera de muestra

El análisis SHALL calcular el balance neto trimestral
`B = (N/3600)·[Δt − (e_aut − e_man)·c]` con `N = 2.646`, `Δt = 43,82` s, `e_man = 26/151` y `c` de
5, 10 y 15 minutos, usando como `e_aut` la tasa de error complementaria de la lectura ponderada y
la tasa cruda sobre el corpus arbitrado. Antes de calcular, SHALL reproducir con la misma función
la celda `+6,9` de `tab:balance-neto` y los valores `+25,4`, `+18,7` y `+11,9` de la referencia
común. El resultado SHALL rotularse como sensibilidad que mezcla corpus y referencias, y MUST NOT
reemplazar el balance con referencia común.

#### Scenario: Balance de sensibilidad rotulado

- **WHEN** se leen las salidas del balance neto de c-221
- **THEN** figuran los tres costos para la tasa ponderada y para la cruda
- **AND** el rótulo dice que es una sensibilidad y no una medición con referencia común

### Requirement: OOS-023 — Controles de reproducibilidad entre corridas

El análisis SHALL comparar `predicciones_independiente.json` con `predicciones_arbitrado.json` en
los casos comunes e informar cuántos difieren en sector, en etapa y en confianza, con sus
identificadores. SHALL registrar el `commit` declarado por cada archivo y si existe en el
historial del repositorio, y, cuando no exista, el commit que efectivamente versionó el archivo.
El análisis MUST NOT modificar ninguno de los dos archivos.

#### Scenario: Variación de la confianza declarada

- **WHEN** se ejecuta el control sobre los casos comunes
- **THEN** el JSON lista los casos de la etapa Gemini cuya confianza difiere entre corridas y confirma si el sector y la etapa coinciden

#### Scenario: Commit inexistente documentado

- **WHEN** el `commit` declarado en un archivo de predicciones no existe en el historial
- **THEN** la salida lo declara y nombra el commit que versionó el archivo, sin reescribir el archivo

### Requirement: OOS-024 — Script de c-221 de solo lectura y determinista

El script de c-221 SHALL ejecutarse sin red ni Gemini, SHALL escribir solo
`analisis_propagacion_arbitraje_c221.json`, `.md` y `.SHA256SUMS.txt` en
`evaluation/data/campana/analisis/` (UTF-8 sin BOM, LF), SHALL registrar el SHA-256 de cada entrada
y SHALL producir salidas idénticas byte a byte en dos corridas. Sus funciones puras SHALL tener
pruebas que ejerciten comportamiento con casos sintéticos, escritas antes de la implementación.

#### Scenario: Determinismo

- **WHEN** el script se ejecuta dos veces sobre las mismas entradas
- **THEN** las tres salidas tienen el mismo SHA-256
- **AND** `git status` no muestra cambios fuera de la carpeta de análisis
