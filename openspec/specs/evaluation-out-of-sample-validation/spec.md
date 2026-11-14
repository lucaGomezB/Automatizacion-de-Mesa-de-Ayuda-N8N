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

### Requirement: OOS-018 — Resultado sobre los 150 casos arbitrados y métricas por clase estimables

Cuando la referencia del corpus independiente quede arbitrada por el tercer etiquetador
(`discordant-arbitration`), el bloque fuera de muestra SHALL reportarse sobre el corpus arbitrado
completo, formado por los `150` casos del diseño original más los casos de refuerzo de clases
chicas (`206` casos en total: `I001`..`I150` e `I151`..`I206`), sin exclusión por discordancia, y
SHALL declarar que el sesgo de exclusión de la etapa previa (n efectivo `103`) quedó removido. La
exactitud estricta cruda sobre el corpus arbitrado completo SHALL ser la cifra primaria. El
resultado sobre los `150` casos del diseño original (`I001`..`I150`) con referencia arbitrada, sin
exclusión por discordancia (n efectivo `150`), SHALL informarse con su intervalo de Wilson como
lectura complementaria (OOS-020). Las
métricas por clase de `Sistemas` y `Bases de Datos` SHALL reportarse como estimables con el
soporte ampliado, y la matriz de confusión `5x5` con precisión, sensibilidad, F1 y soporte por
clase SHALL recalcularse sobre el corpus arbitrado completo. El resultado anterior sobre `103`
SHALL conservarse rotulado como estimación con exclusión, sin reemplazarse silenciosamente.

#### Scenario: Resultado sobre los 150 casos

- **WHEN** se lee el bloque fuera de muestra tras el arbitraje
- **THEN** figura la exactitud estricta sobre los `150` casos del diseño original con referencia arbitrada, sin exclusión por discordancia (n efectivo `150`), con su intervalo de Wilson
- **AND** esa lectura se rotula como complementaria y no reemplaza a la cifra primaria sobre el corpus arbitrado completo
- **AND** se declara que el sesgo de exclusión de la etapa previa quedó removido

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

### Requirement: OOS-020 — Tres lecturas rotuladas de la exactitud fuera de muestra

El análisis de c-221 (`evaluation/data/campana/analisis/analisis_propagacion_arbitraje_c221.py`)
SHALL calcular sobre `predicciones_arbitrado.json` y `corpus_independiente_arbitrado.json` tres
lecturas de la exactitud estricta: (i) la cruda sobre el corpus arbitrado completo, con intervalo
de Wilson, rotulada como primaria; (ii) la ponderada por la composición por sector del corpus de
ajuste de `200` casos (suma de la sensibilidad de cada clase por su peso; los pesos SHALL leerse
del campo `sector_asignado` de `data/corpus_evaluacion_pseudonimizado.json` y MUST NOT fijarse como
constante sin procedencia, y el conteo leído SHALL coincidir con el vector esperado `Sistemas` 16,
`Soporte Tecnico Hardware` 85, `Soporte Tecnico Software` 67, `Seguridad Informatica` 31 y
`Bases de Datos` 1, suma 200, que funciona como anclaje), con intervalo bootstrap
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

#### Scenario: Pesos leídos del corpus de ajuste

- **WHEN** el análisis lee la composición por sector de `data/corpus_evaluacion_pseudonimizado.json`
- **THEN** obtiene `Sistemas` 16, `Soporte Tecnico Hardware` 85, `Soporte Tecnico Software` 67, `Seguridad Informatica` 31 y `Bases de Datos` 1 (suma 200) y usa ese conteo como pesos
- **AND** si el conteo leído difiere del vector esperado, termina con error sin escribir salidas

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

El desglose por origen de la referencia (consenso de `E3` y `E4`, `n = 142`, frente a arbitraje de
`E5`, `n = 64`) también lo produce c-219 en
`evaluation/data/campana/analisis/analisis_sesgo_corpus_referencia_c219.json` (claves
`subconjuntos.consenso` y `subconjuntos.arbitrado`). El análisis de c-221 SHALL conservar ese
cálculo, porque lo usa como anclaje y como base de las lecturas que c-219 no cubre (discordantes
originales, refuerzo, etapa y canal). Si el artefacto de c-219 está presente en el árbol, el
análisis SHALL comparar sus aciertos y su n por origen con los propios y MUST terminar con error
sin escribir salidas si difieren; en ese caso la cifra por origen no es una cifra nueva de c-221:
el memo y la tesis SHALL citarla desde la sección de c-219 y MUST NOT registrarla de nuevo como
valor propio de la sección de c-221. Si el artefacto no está presente al aplicar, la sección de
c-221 SHALL registrarla con la nota de que c-219 la produce también y de que se concilia cuando
c-219 entre a `main`.

#### Scenario: Discordantes originales medidos

- **WHEN** se lee el desglose por bloque
- **THEN** figura la cantidad de aciertos del clasificador sobre los `47` discordantes originales arbitrados

#### Scenario: Desglose por origen anclado en c-219

- **WHEN** `analisis_sesgo_corpus_referencia_c219.json` está presente y el análisis calcula la exactitud por origen de la referencia
- **THEN** compara los aciertos y el n de `subconjuntos.consenso` y `subconjuntos.arbitrado` con los propios
- **AND** si difieren, termina con error y no escribe salidas

#### Scenario: Cifra por origen sin doble registro

- **WHEN** la sección de c-219 figura en el memo canónico y se lee la sección de c-221
- **THEN** la exactitud por origen de la referencia figura como remisión a la sección de c-219 y no como valor propio de c-221

#### Scenario: Conjuntos inconsistentes

- **WHEN** alguna cardinalidad derivada de los archivos difiere de las declaradas
- **THEN** el análisis termina con error y no escribe salidas

### Requirement: OOS-022 — Sensibilidad del balance neto con la tasa fuera de muestra

El análisis SHALL calcular el balance neto trimestral
`B = (N/3600)·[Δt − (e_aut − e_man)·c]` con `N = 2.646`, `Δt = 43,82` s, `e_man = 26/151` y `c` de
5, 10 y 15 minutos, usando como `e_aut` la tasa de error complementaria de la lectura ponderada y
la tasa cruda sobre el corpus arbitrado. La rejilla de `c` es propia de c-221 y no depende de
c-220: si al aplicar el memo canónico ya registra un costo por derivación errónea fijado por c-220
con su procedencia, el análisis SHALL agregarlo como escenario adicional (o usarlo como central,
con la rejilla como sensibilidad); si no, corre solo con la rejilla. Antes de calcular, SHALL reproducir con la misma función
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
identificadores. SHALL registrar el `commit` declarado por cada archivo y si es alcanzable desde
`origin/main`, determinado con `git merge-base --is-ancestor <commit> origin/main`: código `0`,
alcanzable; código `1`, no alcanzable; cualquier otro código (por ejemplo `128`, cuando el objeto
no está en el clon), también no alcanzable, con la indicación de que el objeto no está presente en
el clon donde se ejecutó. Cuando no sea alcanzable, SHALL registrar el commit que versionó el
archivo según `git log --diff-filter=A --format=%h -- <archivo>`. MUST NOT usar la presencia local
del objeto (`git cat-file -t`) como prueba de pertenencia al historial: un commit colgante puede
existir como objeto en el clon donde se hizo la corrida y faltar en otro, porque no viaja con
`fetch` ni con `clone`. Para que las salidas sean idénticas entre clones, el JSON SHALL registrar
la alcanzabilidad y el commit que versionó el archivo, y la presencia local del objeto SHALL
informarse solo en la salida de consola. El análisis MUST NOT modificar ninguno de los dos
archivos.

#### Scenario: Variación de la confianza declarada

- **WHEN** se ejecuta el control sobre los casos comunes
- **THEN** el JSON lista los casos de la etapa Gemini cuya confianza difiere entre corridas y confirma si el sector y la etapa coinciden

#### Scenario: Commit no alcanzable desde main documentado

- **WHEN** `git merge-base --is-ancestor` devuelve un código distinto de `0` para el `commit` declarado en un archivo de predicciones
- **THEN** la salida declara que ese commit no es alcanzable desde `main` y nombra el commit que versionó el archivo, sin reescribir el archivo

#### Scenario: Objeto ausente del clon

- **WHEN** el código de `git merge-base --is-ancestor` no es `0` ni `1`
- **THEN** el commit se registra como no alcanzable desde `main`
- **AND** la consola indica que el objeto no está presente en este clon, sin que eso cambie el JSON

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
