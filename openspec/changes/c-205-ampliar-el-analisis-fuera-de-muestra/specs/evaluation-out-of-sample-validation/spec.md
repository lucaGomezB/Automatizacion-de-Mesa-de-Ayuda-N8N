## ADDED Requirements

### Requirement: OOS-010 — Métricas globales y por clase del bloque fuera de muestra

El análisis fuera de muestra SHALL reportar, además de la exactitud estricta y laxa, la
macro-F1 sobre las cinco clases canónicas, y por cada clase la precisión, la
sensibilidad (`recall`), la F1 y el soporte, calculadas sobre el n efectivo. Las métricas
SHALL reutilizar las funciones puras de `evaluation/metrics.py` (`f1_macro`,
`precision_por_clase`, `sensibilidad_por_clase`, `f1_por_clase`, `soporte_por_clase`,
`matriz_confusion`); el análisis MUST NOT reimplementar el clasificador ni las métricas.
La macro-F1 SHALL declararse como la media aritmética de las cinco F1 por clase, incluida
toda clase de soporte cero.

#### Scenario: Macro-F1 y métricas por clase reproducidas

- **WHEN** el script de solo lectura procesa el bloque out-of-sample
- **THEN** informa la macro-F1 de las cinco clases y, por clase, precisión, sensibilidad, F1 y soporte
- **AND** los valores provienen de las funciones de `evaluation/metrics.py`, sin reimplementarlas

#### Scenario: Soporte cero declarado

- **WHEN** una clase tiene soporte cero en el n efectivo
- **THEN** su F1 y su contribución a la macro-F1 se reportan como `0.0` con su soporte explícito
- **AND** no se omite de la macro-F1

### Requirement: OOS-011 — Balanced accuracy del bloque fuera de muestra

El análisis SHALL reportar la *balanced accuracy* del clasificador sobre el n efectivo,
definida como la media aritmética de las sensibilidades por clase, y SHALL declarar su
relación con la exactitud estricta cuando las clases están desbalanceadas. La *balanced
accuracy* SHALL derivarse de `sensibilidad_por_clase` de `evaluation/metrics.py`.

#### Scenario: Balanced accuracy reportada

- **WHEN** se lee el resultado ampliado fuera de muestra
- **THEN** figura la *balanced accuracy* como media de las sensibilidades por clase
- **AND** se declara que difiere de la exactitud estricta por el desbalance de clases

### Requirement: OOS-012 — Kappa de Cohen del clasificador contra la referencia

El análisis SHALL calcular el kappa de Cohen del clasificador contra la referencia del n
efectivo (sector predicho principal contra sector de referencia), reutilizando
`evaluation/kappa.py::kappa_cohen` con los pares `(referencia, predicción)`. El resultado
SHALL acompañarse de `p_o`, `p_e`, PABAK, `n` y su IC, con las declaraciones de alcance de
`evaluation/kappa.py`. El kappa SHALL rotularse como concordancia del clasificador contra
la referencia humana y MUST NOT presentarse como fiabilidad inter-etiquetador.

#### Scenario: Kappa del clasificador registrado

- **WHEN** se procesa el bloque out-of-sample
- **THEN** se reporta el kappa del clasificador contra la referencia con `p_o`, `p_e`, PABAK, `n` y su IC
- **AND** se declara que mide concordancia clasificador-referencia, no acuerdo entre etiquetadores

### Requirement: OOS-013 — Matriz de confusión fuera de muestra

El análisis SHALL reportar la matriz de confusión `5x5` del bloque fuera de muestra (filas
= sector de referencia, columnas = sector predicho principal), reutilizando
`evaluation/metrics.py::matriz_confusion`. La matriz SHALL ser la base de las métricas por
clase y SHALL declarar explícitamente la frontera de confusión dominante de la clase
`Sistemas`.

#### Scenario: Matriz 5x5 reproducida

- **WHEN** se lee el resultado ampliado fuera de muestra
- **THEN** figura la matriz de confusión `5x5` con filas = referencia y columnas = predicción
- **AND** sus marginales reproducen el soporte por clase y la exactitud estricta

### Requirement: OOS-014 — Análisis de potencia y precisión con el n efectivo observado

El análisis SHALL comparar el semi-ancho del IC de Wilson observado de la exactitud
estricta, con el n efectivo (`103`) y la proporción observada, contra el objetivo de diseño
declarado en el design D1 de c-191 (`~8,4` puntos porcentuales), y SHALL reportar la
precisión alcanzada y la potencia/MDE declarada. El semi-ancho SHALL derivarse de
`evaluation/metrics.py::intervalo_wilson`; la potencia/MDE SHALL derivarse de
`evaluation/stats.py::efecto_minimo_detectable` sin reimplementar la fórmula. El resultado
SHALL declarar si la precisión observada cumple el objetivo de diseño.

#### Scenario: Semi-ancho observado frente al de diseño

- **WHEN** se lee el análisis de potencia
- **THEN** figura el semi-ancho del IC de Wilson observado con `n` efectivo `103`
- **AND** se compara contra el objetivo de diseño D1 de c-191 y se declara si lo cumple

#### Scenario: Potencia/MDE declarada

- **WHEN** se lee el análisis de potencia
- **THEN** figura la potencia o el MDE declarado con sus supuestos (nivel de significancia, potencia objetivo o MDE)
- **AND** el cálculo reutiliza `efecto_minimo_detectable`

### Requirement: OOS-015 — Análisis de sesgo de la exclusión de los discordantes

El análisis SHALL cuantificar el efecto de excluir los `47` casos discordantes sobre la
exactitud reportada mediante al menos tres escenarios: peor caso, mejor caso y una cota
acotada por la incertidumbre de las etiquetas ausentes. El análisis SHALL declarar una
**regla de decisión explícita** que ligue el peor caso (y la cota) a la exactitud
reportada, de modo que un lector pueda concluir si el resultado sostiene o no el umbral
declarado. El escenario SHALL declararse como análisis de sensibilidad y MUST NOT
presentarse como una medición del clasificador sobre los `47` casos.

#### Scenario: Escenarios peor, mejor y cota

- **WHEN** se lee el análisis de sesgo de exclusión
- **THEN** figuran el peor caso, el mejor caso y una cota de la exactitud bajo supuestos declarados sobre los `47` excluidos
- **AND** se rotulan como sensibilidad, no como medición

#### Scenario: Regla de decisión explícita

- **WHEN** se lee el análisis de sesgo de exclusión
- **THEN** figura una regla de decisión que ata el peor caso o la cota a la exactitud reportada
- **AND** la regla permite concluir si el resultado sostiene el umbral

### Requirement: OOS-016 — Extensión del balance neto y de costo al corpus independiente

El análisis SHALL extender el balance neto de derivaciones erróneas (hoy in-sample) a la
tasa de error estricta fuera de muestra, donde los artefactos versionados lo permitan,
manteniendo los insumos de costo y de ahorro bruto como supuestos con estado `condicional`.
Cuando un insumo no sea derivable de los artefactos fuera de muestra, el análisis SHALL
declararlo como no computable con su motivo, sin fijar un valor estimado.

#### Scenario: Balance neto con la tasa fuera de muestra

- **WHEN** los artefactos fuera de muestra permiten derivar la tasa de error estricta
- **THEN** el balance neto se recalcula con esa tasa y se rotula `condicional`
- **AND** los insumos de costo y ahorro bruto conservan su estado `condicional`

#### Scenario: Insumo no derivable declarado

- **WHEN** un insumo del balance no es derivable de los artefactos fuera de muestra
- **THEN** el análisis lo declara como no computable con su motivo
- **AND** no consigna ningún valor estimado para él

### Requirement: OOS-017 — Script de solo lectura y reproducibilidad determinística

Las métricas ampliadas SHALL producirse por un script de solo lectura bajo
`evaluation/data/campana/analisis/`, que consuma los artefactos versionados de c-191 y
escriba sus salidas en el mismo directorio (JSON y Markdown). El script SHALL ser
determinístico (dos corridas producen salidas idénticas byte a byte), MUST NOT escribir
fuera de su directorio, MUST NOT modificar `data/`, el corpus congelado, las predicciones
ni ningún valor canónico, y SHALL imprimir el SHA-256 de cada salida.

#### Scenario: Solo lectura y determinismo

- **WHEN** se ejecuta el script dos veces seguidas
- **THEN** ambas salidas son idénticas byte a byte
- **AND** `git status` no muestra archivos modificados por la ejecución

#### Scenario: Rutas de entrada versionadas

- **WHEN** se inspecciona el script
- **THEN** sus entradas son los artefactos versionados de c-191 (`corpus_independiente.json`, `predicciones_independiente.json`, la tabla primaria del doble etiquetado)
- **AND** no invoca al clasificador, a Gemini ni a la red
