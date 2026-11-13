# evaluation-out-of-sample-validation Specification

## Purpose
Define el protocolo y los artefactos de la validación fuera de muestra del clasificador
CONGELADO sobre un corpus independiente de 150 casos: el alcance (solo clasificación), los
etiquetadores, la referencia por consenso, el muestreo estratificado con sobremuestreo y
ponderación, el n efectivo con su sesgo de exclusión y el versionado de los resultados, de
modo que la validación sea producible, registrada y verificable sin recalibrar el clasificador
ni tocar los artefactos congelados de la v9.

## Requirements

### Requirement: OOS-001 — Alcance: solo la validación de clasificación del clasificador congelado

La validación fuera de muestra SHALL medir únicamente la clasificación del clasificador
congelado sobre el corpus independiente. MUST NOT medir el brazo manual ni involucrar a los
operadores `O1`/`O2`, ni al efecto de orden, ni al cronometraje de las reasignaciones. El
resultado SHALL reportarse como el bloque out-of-sample de `evaluar_fuera_de_muestra`, sin
sustituir ni reemplazar las métricas in-sample.

#### Scenario: Alcance acotado a la clasificación

- **WHEN** se prepara la campaña de validación fuera de muestra
- **THEN** el protocolo y los artefactos declaran que la medición es solo de la clasificación del clasificador congelado
- **AND** no se registra ninguna etiqueta de brazo manual ni de operadores `O*` para el corpus independiente

#### Scenario: Bloque out-of-sample sin sustitución

- **WHEN** se ejecuta el análisis
- **THEN** el resultado fuera de muestra se reporta como un bloque rotulado `out-of-sample` con su n efectivo
- **AND** las métricas in-sample no se reemplazan ni se presentan como fuera de muestra

### Requirement: OOS-002 — Corpus independiente de 150 casos sin solape y pseudonimizado

El corpus independiente SHALL tener 150 casos nuevos con ids `I001..I150`, disjuntos de los
200 del corpus de ajuste, y SHALL pseudonimizarse con el mismo protocolo que el corpus de
ajuste mediante `scripts/corpus_ingest/pseudonymize_corpus.py`. El corpus final SHALL ser un
JSON con el esquema de `data/corpus_evaluacion_pseudonimizado.json` (las cinco cadenas de
sector canónicas, exactas y sin tildes) y SHALL pasar `verificar_no_solape` contra el corpus de
ajuste como paso previo obligatorio antes de clasificar.

#### Scenario: Sin solape de ids ni de descripciones

- **WHEN** se contrasta el corpus independiente con el de ajuste
- **THEN** `verificar_no_solape` no lanza `SolapeError`, todos los ids del candidato llevan el prefijo `I` y ninguna descripción normalizada coincide con una del corpus de ajuste

#### Scenario: Misma pseudonimización

- **WHEN** se pseudonimiza el corpus crudo
- **THEN** se usa `scripts/corpus_ingest/pseudonymize_corpus.py` con el mismo protocolo del corpus de ajuste y el pseudonimizador sale con exit code `0`

### Requirement: OOS-003 — Doble etiquetado con dos etiquetadores nuevos `E3` y `E4`

El corpus independiente SHALL doble-etiquetarse con la plantilla y el validador de la campaña
(`evaluation/data/plantilla_etiquetado.csv`, `evaluation/doble_etiquetado.py`), con exactamente
dos etiquetadores nuevos, alias `E3` y `E4`, distintos entre sí y de los analistas `A1`, de los
autores `T1`-`T3` y de los operadores `O1`/`O2`. El registro `evaluation/data/campana/registro_sujetos.csv`
SHALL registrar `E3` y `E4` con `rol = etiquetador` y un código `P<n>`, sin nombres, correos ni
legajos; la correspondencia alias-identidad SHALL custodiarse FUERA del repositorio. El
validador SHALL salir con exit code `0` o la limitación SHALL declararse.

#### Scenario: Dos etiquetadores nuevos e independientes

- **WHEN** se registran `E3` y `E4` en `registro_sujetos.csv`
- **THEN** cada uno tiene `rol = etiquetador` y una `persona` `P<n>` que no figura con ningún otro rol, distinta de las `persona` de `A1`, `T1`-`T3` y `O1`/`O2`
- **AND** ninguna fila contiene nombre, correo ni legajo

#### Scenario: Planilla válida con la plantilla y el validador existentes

- **WHEN** se valida la planilla unida de `E3` y `E4` contra el corpus independiente
- **THEN** `python -m evaluation.doble_etiquetado --tarea doble_etiquetado` sale con exit code `0`
- **AND** no se define un esquema ni un validador propios

### Requirement: OOS-004 — Referencia por consenso y conjunto de verdad laxo

La referencia SHALL ser el consenso de `E3` y `E4` sobre `sector_etiquetado` para el mismo
`id_caso` (`consenso_doble_etiquetado`). El conjunto de verdad laxo SHALL ser el sector
consensuado más la INTERSECCIÓN de los sectores adicionales que ambos etiquetadores marcaron.
Los casos discordantes SHALL EXCLUIRSE de la referencia y SHALL informarse con la advertencia
de sesgo hacia casos fáciles.

#### Scenario: Consenso como referencia

- **WHEN** `E3` y `E4` asignan el mismo `sector_etiquetado` a un caso
- **THEN** ese sector es la referencia estricta y el conjunto laxo suma la intersección de los adicionales de ambos
- **AND** el conjunto laxo nunca incluye un adicional marcado por un solo etiquetador

#### Scenario: Discordantes excluidos y reportados

- **WHEN** `E3` y `E4` asignan distinto `sector_etiquetado` a un caso
- **THEN** el caso queda fuera de la referencia
- **AND** el resultado informa cuántos casos se excluyeron y la advertencia de sesgo hacia casos fáciles

### Requirement: OOS-005 — Clasificador congelado y runner reutilizado

La clasificación SHALL ejecutarse con el clasificador CONGELADO: `classifier_version` idéntica
a la del in-sample (`hybrid-v3`) y commit `bf5e099`, sin recalibrar tau, el prompt, el
`KEYWORD_MAP` ni el vocabulario de sectores después de ver el corpus. La corrida SHALL
reutilizar `evaluar_fuera_de_muestra` y el guard `--confirm-paid` de
`evaluation/run_evaluation.py`, con `--corpus`, `--predicciones` y `--reporte` propios del
corpus independiente, sin escribir sobre los artefactos congelados de la v9.

#### Scenario: Congelamiento verificado

- **WHEN** se registra el control de clasificador congelado
- **THEN** `git diff bf5e099 HEAD` sobre el clasificador, el prompt y las constantes solo admite diferencias ajenas a la clasificación
- **AND** el resultado del control y el commit se registran en `evaluation/data/campana/README.md`

#### Scenario: Sin recalibración posterior

- **WHEN** aparece un defecto después de ver el corpus o sus predicciones
- **THEN** el protocolo prohíbe corregirlo y volver a medir sobre los mismos casos
- **AND** el defecto se informa como hallazgo y, de corregirse, se reúne un corpus independiente nuevo

#### Scenario: Rutas propias y guard de costo

- **WHEN** se clasifica el corpus independiente
- **THEN** `evaluar_fuera_de_muestra` y `--confirm-paid` se reutilizan y las predicciones quedan en `evaluation/data/campana/predicciones_independiente.json`
- **AND** `evaluation/predicciones.json` y `evaluation/report.md` no cambian

### Requirement: OOS-006 — Muestreo estratificado con sobremuestreo y ponderación

La selección de los 150 casos SHALL ser estratificada por canal de origen (correo, formulario
web, telefonía) y por sector, con sobremuestreo de la clase minoritaria (`Bases de Datos`, n=1
en el corpus de 200) y ponderación de las estimaciones globales por la distribución del
universo. Los estratos exactos SHALL fijarse y registrarse ANTES de reunir el corpus.

#### Scenario: Estratos definidos antes de reunir

- **WHEN** se inicia la recolección del corpus independiente
- **THEN** la asignación por estrato de canal y sector está decidida y registrada con su justificación
- **AND** la clase minoritaria está sobremuestreada respecto de su proporción en el corpus de 200

#### Scenario: Estimaciones globales ponderadas

- **WHEN** se calculan las métricas globales del corpus independiente
- **THEN** se informan con la ponderación por la distribución del universo, además del valor sin ponderar

### Requirement: OOS-007 — n efectivo y sesgo de exclusión declarados

El resultado SHALL declarar el n efectivo (casos con consenso) y el número de casos excluidos
por discordancia, junto con el IC de Wilson de la exactitud estricta. La exactitud estricta
del corpus independiente SHALL reportarse como estimación sobre el n efectivo, con la
advertencia de que la exclusión de los discordantes sesga la referencia hacia los casos más
fáciles.

#### Scenario: n efectivo explícito

- **WHEN** se lee el resultado fuera de muestra
- **THEN** figura el n efectivo y el conteo de casos excluidos por discordancia
- **AND** la exactitud estricta se reporta con su IC de Wilson sobre el n efectivo

#### Scenario: Advertencia de sesgo presente

- **WHEN** se reporta la exactitud fuera de muestra
- **THEN** el texto declara que excluir los discordantes sesga la referencia hacia los casos más fáciles

### Requirement: OOS-008 — Artefactos versionados con SHA-256

Los artefactos de la validación fuera de muestra SHALL versionarse en
`evaluation/data/campana/` con su SHA-256 en `evaluation/data/campana/README.md`: el corpus
independiente (`corpus_independiente.json`), las predicciones
(`predicciones_independiente.json`), la tabla del doble etiquetado independiente
(`doble_etiquetado_independiente.csv`), el registro de sujetos (`registro_sujetos.csv`), las
salidas de análisis y el resultado del control de clasificador congelado con su commit. Los
artefactos de la v9 SHALL quedar sin cambios.

#### Scenario: Hash y procedencia registrados

- **WHEN** se versionan los artefactos
- **THEN** el README registra el SHA-256 de cada archivo y el commit con que se generó el cache
- **AND** `git status` no muestra modificados `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json` ni `evaluation/report.md`

#### Scenario: Cache con procedencia completa

- **WHEN** se inspecciona `predicciones_independiente.json`
- **THEN** su `cache_meta` trae `corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`, `commit` y `pines`

### Requirement: OOS-009 — Protocolo y registro de decisiones versionados

El proyecto SHALL versionar el protocolo actualizado de la campaña independiente en
`docs/campana-medicion/runbook-corpus-independiente.md` y `runbook-doble-etiquetado.md`, que
SHALL nombrar a los etiquetadores `E3` y `E4`, el muestreo estratificado con sobremuestreo y
ponderación, la referencia por consenso con su sesgo de exclusión y el criterio de aceptación.
El protocolo SHALL ser ejecutable por los autores sin conocimiento tácito.

#### Scenario: Protocolo ejecutable y sin tácito

- **WHEN** un autor sigue los runbooks para la campaña independiente
- **THEN** los runbooks indican `E3` y `E4` como etiquetadores, la estratificación y ponderación, la referencia por consenso y el criterio de aceptación
- **AND** cada paso tiene su comando o su artefacto verificable

#### Scenario: Decisión de estratos registrada

- **WHEN** se consulta la decisión de muestreo
- **THEN** figura registrada la asignación por estrato decidida por los autores antes de reunir el corpus

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

### Requirement: OOS-019 — Acuerdo entre los etiquetadores E3 y E4

El análisis de c-207 SHALL calcular, sobre los casos del doble etiquetado independiente, la
proporción de acuerdo observada entre `E3` y `E4` en el sector principal y el kappa de Cohen
con sus IC asintótico y bootstrap mediante `evaluation/kappa.py::kappa_cohen`. La cantidad de
casos concordantes SHALL coincidir con el n efectivo declarado por c-191 (`103` de `150`); si
no coincide, el análisis MUST fallar y no producir salidas. El valor SHALL rotularse como
fiabilidad entre etiquetadores, distinto del kappa del clasificador contra la referencia.

#### Scenario: Concordancia con el n efectivo

- **WHEN** el análisis lee `doble_etiquetado_independiente.csv`
- **THEN** cuenta `103` casos concordantes de `150` y reporta el kappa con sus IC

#### Scenario: Inconsistencia detectada

- **WHEN** la cantidad de concordantes difiere del n efectivo de c-191
- **THEN** el análisis termina con error y no escribe los archivos de salida
