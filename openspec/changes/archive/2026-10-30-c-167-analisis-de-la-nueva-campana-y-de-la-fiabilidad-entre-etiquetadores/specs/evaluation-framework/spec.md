## ADDED Requirements

### Requirement: Kappa de Cohen entre los etiquetadores nuevos con intervalos asintótico y bootstrap

El framework SHALL calcular, en `evaluation/kappa.py`, el coeficiente kappa de Cohen no
ponderado sobre la etiqueta primaria `sector_etiquetado` de las filas con
`tarea = doble_etiquetado` de la planilla de etiquetado, con las 5 clases de
`SECTORES_CANONICOS`. El cálculo MUST exigir exactamente dos `id_etiquetador` distintos, cada
uno con una etiqueta por caso, y MUST fallar con un error accionable que nombre los alias
encontrados en cualquier otro caso; el kappa de Fleiss para más de dos etiquetadores queda
fuera del alcance y la salida MUST declararlo. El resultado MUST incluir κ, p_o, p_e,
PABAK = (5·p_o − 1)/4, n, el IC asintótico calculado con la varianza bajo H1 de Fleiss, Cohen
y Everitt (1969), Var(κ) = [Σ_i p_ii (1 − (p_i. + p_.i)(1 − κ))² + (1 − κ)² Σ_{i≠j} p_ij
(p_.i + p_j.)² − (κ − p_e (1 − κ))²] / (n (1 − p_e)²), con límites recortados a [−1, 1], y el
IC bootstrap percentil 2,5 y 97,5 por casos con `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP`
de `evaluation/metrics.py`. Las remuestras con p_e = 1 MUST descartarse y contarse; si superan
el 5 % de los remuestreos, el IC bootstrap MUST declararse no computable con el conteo. La
salida MUST incluir el rótulo de Landis y Koch derivado del valor puntual y la nota de que el
rótulo del IC puede abarcar dos categorías, y MUST declarar que el kappa es de los
etiquetadores nuevos y no un intervalo del kappa 0,87 original.

#### Scenario: Oráculo de kappa y error estándar asintótico

- **WHEN** se calcula el kappa sobre la matriz de acuerdo [[20, 5, 0], [3, 15, 2], [0, 4, 11]] (n = 60) inmersa en las 5 clases canónicas
- **THEN** κ = 0,642553 y el error estándar asintótico es 0,083594 con tolerancia de 1e-6
- **AND** p_o = 0,766667, p_e = 0,347222, PABAK = 0,708333 y el IC asintótico del 95 % es [0,478711; 0,806395]
- **AND** el rótulo de Landis y Koch es "sustancial" y la salida señala que el IC abarca "moderado" y "sustancial"

#### Scenario: Diagonal perfecta

- **WHEN** ambos etiquetadores coinciden en todos los casos y usan más de un sector
- **THEN** κ = 1 y el IC asintótico es [1, 1]

#### Scenario: Acuerdo esperado igual a uno declara no estimable

- **WHEN** ambos etiquetadores asignan el mismo único sector a todos los casos, de modo que p_e = 1
- **THEN** el resultado declara el kappa no estimable y no devuelve valor numérico ni intervalo

#### Scenario: Límites recortados al rango válido

- **WHEN** κ ± z·SE excede 1 o queda por debajo de −1
- **THEN** el límite correspondiente del IC asintótico se recorta a 1 o a −1

#### Scenario: Bootstrap reproducible

- **WHEN** se recalcula el IC bootstrap con los mismos datos
- **THEN** el intervalo es idéntico y se obtuvo con `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP` importados de `evaluation/metrics.py`

#### Scenario: Remuestras degeneradas por encima del 5 %

- **WHEN** más del 5 % de las remuestras bootstrap tienen p_e = 1
- **THEN** el resultado declara "IC bootstrap no computable" con el conteo de remuestras degeneradas y no emite intervalo bootstrap

#### Scenario: Cantidad de etiquetadores distinta de dos

- **WHEN** las filas de `tarea = doble_etiquetado` tienen uno o más de dos `id_etiquetador` distintos
- **THEN** el cálculo falla con un error que nombra los alias encontrados y no reporta kappa

### Requirement: Exactitud del brazo manual con registro de sujetos y referencia declarada

El framework SHALL calcular en `evaluation/campana.py` la exactitud estricta y laxa del brazo
manual por operador (`tarea = brazo_manual`, operadores fijos `O1` y `O2`,
`claves = id_etiquetador`) sobre los casos que ese operador etiquetó, reutilizando
`resumen_exactitud` y `desglose_exactitud`, con IC de Wilson por operador y con la misma
definición de acierto estricto y laxo que el brazo automatizado (la laxa evalúa la etiqueta
primaria del operador dentro del conjunto de verdad). Como la planilla exige que cada caso
tenga al menos un operador y no que ambos cubran todos los casos, la salida MUST declarar la
cobertura de cada operador (casos etiquetados, casos compartidos y casos exclusivos). La
exactitud agregada MUST calcularse como aciertos sobre etiquetas de la unión de casos con IC
bootstrap por caso (se remuestrean casos y cada caso aporta las etiquetas de los operadores que
lo etiquetaron) y MUST NOT usar Wilson sobre el total de etiquetas. La referencia por defecto
MUST ser el consenso del doble etiquetado nuevo: casos donde `E1` y `E2` coinciden en
`sector_etiquetado`, con conjunto de verdad formado por el sector consensuado y la intersección
de sus sectores adicionales. Los casos discordantes MUST excluirse de la exactitud y la salida
MUST declarar cuántos casos quedaron excluidos por discordancia, con la advertencia de que la
exclusión sesga la referencia hacia casos fáciles. El `sector_asignado` original del corpus
SHALL admitirse como referencia alternativa parametrizable, y toda salida MUST declarar la
referencia usada. El análisis MUST recibir el `registro_sujetos`
(`evaluation/data/campana/registro_sujetos.csv`, columnas `alias, rol, persona`, con rol en
`etiquetador`, `operador`, `analista_original`, `autor` y `persona` un seudónimo estable
`P<n>`) y MUST fallar si una misma `persona` figura con más de un rol, si un alias tiene más de
un rol o de una persona, si un alias de la planilla no figura en el registro o tiene un rol
incompatible con su tarea, o si la persona de un alias de la planilla tiene rol
`analista_original` o `autor`. Por cada operador, el análisis MUST reportar el contraste manual
vs automatizado con `contraste_mcnemar`, pareado por `(id_caso, id_etiquetador)`, entre el
acierto estricto del operador y el de la predicción v9 del mismo caso, leída de
`evaluation/predicciones.json` en solo lectura.

#### Scenario: Exactitud por operador y agregada contra el consenso nuevo

- **WHEN** se analizan `O1` y `O2` con la referencia por defecto
- **THEN** el resultado reporta exactitud estricta y laxa de cada operador sobre sus casos etiquetados, con su IC de Wilson y nivel de confianza, y la cobertura de cada operador
- **AND** la agregada sobre la unión de casos trae un IC bootstrap por caso con `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP`
- **AND** la salida declara `referencia_usada = consenso_doble_etiquetado`

#### Scenario: Operadores con coberturas distintas

- **WHEN** `O1` etiquetó casos que `O2` no etiquetó, y viceversa
- **THEN** la exactitud de cada operador se calcula solo sobre sus casos, ningún caso no etiquetado se cuenta como error, y la salida declara casos compartidos y exclusivos

#### Scenario: Casos discordantes del doble etiquetado

- **WHEN** `E1` y `E2` difieren en `sector_etiquetado` para uno o más casos
- **THEN** esos casos no entran en la exactitud del brazo manual
- **AND** la salida declara el conteo y la lista de casos excluidos por discordancia con la advertencia de sesgo hacia casos fáciles

#### Scenario: Referencia alternativa rotulada

- **WHEN** se pide la referencia `consenso_original`
- **THEN** la exactitud se calcula contra el `sector_asignado` y el conjunto de verdad del corpus y la salida declara `referencia_usada = consenso_original`

#### Scenario: Misma persona con más de un rol

- **WHEN** el `registro_sujetos` asigna a una misma `persona` los roles `operador` y `etiquetador` mediante dos alias distintos, o la persona de un alias de la planilla tiene rol `analista_original` o `autor`
- **THEN** el análisis falla con un error que nombra la persona, los alias y los roles, sin reportar exactitud

#### Scenario: Alias de la planilla sin registrar

- **WHEN** un `id_etiquetador` de la planilla no figura en el `registro_sujetos`
- **THEN** el análisis falla con un error que nombra el alias

#### Scenario: Agregada sin pseudo-replicación

- **WHEN** se calcula la exactitud agregada sobre casos etiquetados por ambos operadores
- **THEN** su intervalo proviene del bootstrap por caso y no coincide con `intervalo_wilson` aplicado al total de etiquetas

#### Scenario: Contraste manual vs automatizado por operador

- **WHEN** se dispone de la predicción v9 de cada caso de la referencia
- **THEN** el resultado reporta, por operador, el contraste de McNemar pareado por `(id_caso, id_etiquetador)` con sus pares concordantes y discordantes, su valor p y su criterio
- **AND** `evaluation/predicciones.json` queda byte a byte igual

### Requirement: Tasa de intervención humana de campaña con contraste contra la cota de la sub-hipótesis

El framework SHALL calcular `tasa_intervencion_humana` (métrica offline de campaña, distinta
de `tasa_intervencion_backend` de c-165) a partir del export
`evaluation/data/campana/intervenciones.csv`, según la definición operativa de
`subsec:medicion-intervencion`, como la proporción de casos de la corrida con al menos una
intervención vinculada, con IC de Wilson, desglosada por `origen_intervencion` y por
`cambio_sector`. Como el export contiene solo filas intervenidas, el denominador (casos de la
corrida) MUST tomarse de `plan_campana.csv` o del sidecar de la corrida y MUST NOT derivarse
del export. Las filas con `id_caso` nulo MUST contarse como no vinculables y quedar fuera de la
tasa; un `id_caso` fuera de la corrida MUST producir un error accionable. `actor_alias` (HMAC
truncado) MUST NOT usarse como clave de análisis ni de agrupación. La tasa MUST
contrastarse con la cota 0,15: límite superior de Wilson menor que 0,15 rotula "compatible" y
mayor o igual rotula "no compatible", reportando la estimación y ambos límites. La proporción
de tiempo SHALL calcularse como Σ `duracion_s` / Σ (`tiempo_automatizado_s` + `duracion_s`)
sobre los casos del plan con tiempo conocido (los no intervenidos aportan duración 0) y MUST
llevar IC bootstrap por caso del cociente, nunca Wilson. Si algún caso intervenido carece de
duración, MUST reportarse la cobertura (k de m) y, con cobertura menor al 80 %, la proporción
de tiempo MUST declararse no estimable con el motivo. El denominador MUST rotularse "tiempo de
registro automatizado" y declararse como limitación.

#### Scenario: Tasa compatible con la cota

- **WHEN** 20 de 200 casos del plan registran intervención
- **THEN** la tasa es 0,10 con IC de Wilson [0,065670; 0,149406] y el contraste rotula "compatible"

#### Scenario: Tasa no compatible con la cota

- **WHEN** 26 de 200 casos del plan registran intervención
- **THEN** la tasa es 0,13 con IC de Wilson [0,090282; 0,183664] y el contraste rotula "no compatible", con la estimación y ambos límites en la salida

#### Scenario: Desglose por origen y por cambio de sector

- **WHEN** el export tiene intervenciones de distintos `origen_intervencion` y con y sin `cambio_sector`
- **THEN** el resultado reporta la proporción de casos de cada origen y de cada valor de `cambio_sector` con su IC de Wilson, y declara que un caso puede figurar en más de un origen

#### Scenario: Sin intervenciones

- **WHEN** ningún caso del plan registra intervención
- **THEN** la tasa es cero con su IC de Wilson, la proporción de tiempo es cero y no hay error de división por cero

#### Scenario: Proporción de tiempo con bootstrap

- **WHEN** todos los casos intervenidos tienen `duracion_s`
- **THEN** la proporción de tiempo se reporta con IC bootstrap por caso del cociente, con la semilla y los remuestreos declarados, y con el denominador rotulado "tiempo de registro automatizado"

#### Scenario: Cobertura de duración insuficiente

- **WHEN** solo 3 de 4 casos intervenidos tienen `duracion_s` (cobertura del 75 %)
- **THEN** la proporción de tiempo se declara no estimable con el motivo y la cobertura, y la tasa de casos se reporta igual

#### Scenario: Denominador tomado de la corrida y no del export

- **WHEN** el export de intervención contiene 20 filas intervenidas y el plan de la corrida tiene 200 casos
- **THEN** el denominador de la tasa es 200, tomado del plan o del sidecar de la corrida, y `actor_alias` no interviene en ningún agrupamiento

#### Scenario: Intervención no vinculable o fuera del plan

- **WHEN** una fila tiene `id_caso` nulo, u otra tiene un `id_caso` que no está en el plan
- **THEN** la primera se cuenta como no vinculable fuera de la tasa y la segunda produce un error que nombra el caso

### Requirement: Efecto de orden de condición y de posición del operador del brazo manual

El framework SHALL estimar el efecto de orden con respuesta primaria la duración del brazo
manual `duracion_s = timestamp − inicio`, en segundos, por `(id_caso, id_etiquetador)` de las
filas de la planilla con `tarea = brazo_manual`, y respuesta secundaria el acierto estricto,
por operador y sobre los casos que cada operador etiquetó, tomando `posicion`, `mitad` y
`brazo_primero` del plan de campaña. El `tiempo_manual_s` del corpus (canónico de la campaña
2026-10) MUST NOT usarse como respuesta ni modificarse. Una duración negativa MUST producir un
error accionable que nombre el caso y el operador. El efecto de orden de
condición MUST compararse entre casos con `brazo_primero = manual` y `automatizado` con
Mann-Whitney bilateral y r rank-biserial cuando el plan no cruza casos, y con Wilcoxon pareado
por caso (con r y d_z) solo cuando el plan cruza los mismos casos en dos corridas. El efecto de
posición MUST estimarse con la correlación de Spearman entre la duración y la posición real
de cada caso para el operador, y con Mann-Whitney entre mitad 1 y mitad 2 del plan con r. La
posición real y los desvíos respecto del plan MUST obtenerse importando
`reconstruir_posicion_real` y `desvios_respecto_del_plan` de `evaluation/brazo_manual.py`
(c-165), sin reimplementarlas, y la salida MUST declarar la cantidad de desvíos. Cada contraste MUST exigir al menos 6 casos por
grupo (o 6 pares) y, si no se alcanza, MUST declararse no aplicable sin valor de efecto. Cada
contraste MUST reportar el efecto mínimo detectable con `efecto_minimo_detectable` y
`ARE_WILCOXON_MINIMA` (n de pares en escala d_z; n efectivo n_a·n_b/(n_a + n_b) en escala d
para grupos independientes). Un resultado no significativo MUST NOT rotularse como ausencia de
efecto. El contraste pareado MUST envolver `wilcoxon_tiempos_detallado` con nombres neutros
(`grupo_a`, `grupo_b`) y MUST capturar el caso en que todas las diferencias son cero como no
aplicable. El acierto estricto MUST contrastarse con `contraste_mcnemar` en el diseño cruzado y
con Wilson por grupo y la prueba exacta de Fisher en grupos independientes.

#### Scenario: Orden de condición entre grupos independientes

- **WHEN** el plan asigna a cada caso una sola condición y cada grupo tiene al menos 6 casos con tiempo
- **THEN** el resultado reporta, por operador, U de Mann-Whitney, el valor p bilateral, r rank-biserial, n de cada grupo y el MDE en escala d

#### Scenario: Orden de condición en diseño cruzado

- **WHEN** el plan cruza los mismos casos en dos corridas con condición opuesta
- **THEN** el contraste es Wilcoxon pareado por caso con estadístico, p, r, d_z y el MDE en escala d_z

#### Scenario: Efecto de posición

- **WHEN** el operador tiene al menos 6 casos con duración en cada mitad
- **THEN** el resultado reporta el rho de Spearman entre duración y posición real (obtenida con `reconstruir_posicion_real` de `evaluation/brazo_manual.py`) con su p, el contraste mitad 1 vs mitad 2 con U, p y r, y la cantidad de desvíos respecto del plan

#### Scenario: Grupo por debajo del mínimo

- **WHEN** algún grupo del contraste tiene menos de 6 casos (o hay menos de 6 pares)
- **THEN** ese contraste se declara no aplicable sin estadístico ni efecto

#### Scenario: Todas las diferencias pareadas son cero

- **WHEN** en el diseño cruzado todas las diferencias de tiempo son cero
- **THEN** el contraste pareado se declara no aplicable en lugar de propagar el error de scipy

#### Scenario: Resultado no significativo

- **WHEN** un contraste de orden da p ≥ 0,05
- **THEN** la salida lo rotula "no significativo; efectos menores que el MDE no son detectables" junto al MDE, y no lo rotula como ausencia de efecto

#### Scenario: Duración del brazo manual derivada de la planilla

- **WHEN** las filas de `tarea = brazo_manual` traen `inicio` y `timestamp` ISO-8601
- **THEN** la respuesta de cada `(id_caso, id_etiquetador)` es `timestamp − inicio` en segundos y el `tiempo_manual_s` del corpus no interviene en el contraste

#### Scenario: Duración negativa

- **WHEN** una fila de `tarea = brazo_manual` tiene `timestamp` anterior a `inicio`
- **THEN** el análisis de orden falla con un error que nombra el `id_caso` y el `id_etiquetador`

#### Scenario: Plan de campaña ausente

- **WHEN** no se dispone del plan de campaña
- **THEN** la sección de efecto de orden se declara "no se obtuvo" con el motivo y las demás secciones del análisis se reportan igual

### Requirement: Evaluación fuera de muestra con clasificador congelado y bloques rotulados

El framework SHALL evaluar, con `evaluar_fuera_de_muestra`, las predicciones del corpus
independiente (`evaluation/data/campana/predicciones_independiente.json`, generadas por c-166)
junto al bloque in-sample leído de `evaluation/predicciones.json` en solo lectura, reportando
para cada bloque la exactitud global con Wilson y el desglose por etapa en cascada con
`desglose_exactitud` en el orden de `ETAPAS_PIPELINE`, en bloques rotulados in-sample y
out-of-sample que no se mezclan. Las predicciones MUST leerse solo con `cargar_predicciones` y
`cargar_cache_meta`, y MUST NOT invocarse `main()` ni ningún camino que llame a Gemini. El
análisis MUST abortar si la `classifier_version` del `cache_meta` in-sample difiere de la
del independiente, o si el parámetro obligatorio `pines_in_sample` (versión de `google-genai`
y modelo, tomados del README de `evaluation/data/campana/` que escribe c-166, porque el cache de
v9 no los registra) difiere de los `pines` del `cache_meta` independiente; sin
`pines_in_sample`, la sección MUST fallar con un error accionable. El commit del
clasificador MUST compararse solo cuando ambos bloques lo traen, abortando si difiere; si falta
en el in-sample (la copia congelada de v9 no lo registró), el análisis MUST NOT abortar y la
salida MUST declarar como limitación "commit in-sample no registrado; comparabilidad verificada por versión y pines". El parámetro `commit_in_sample` es opcional y,
si se provee, se usa como commit del bloque in-sample. El análisis MUST re-ejecutar `verificar_no_solape` de `evaluation/no_solape.py` antes de
reportar y abortar si informa solape, y MUST NOT regenerar `evaluation/report.md`. Si el
corpus independiente o sus predicciones no existen, la sección MUST declararse "no se obtuvo"
nombrando el artefacto faltante, sin sustituirla por datos in-sample.

#### Scenario: Bloques in-sample y out-of-sample con desglose por etapa

- **WHEN** existen predicciones de ambos bloques con la misma `classifier_version`, `pines` del cache independiente iguales a `pines_in_sample` y sin solape
- **THEN** el resultado reporta un bloque rotulado in-sample y otro out-of-sample, cada uno con exactitud global e IC de Wilson y el desglose por etapa en el orden de `ETAPAS_PIPELINE`

#### Scenario: Versión o pines del clasificador distintos

- **WHEN** la `classifier_version` del cache independiente difiere de la del cache in-sample, o sus `pines` difieren de `pines_in_sample`
- **THEN** el análisis aborta con un error que muestra ambos valores y no reporta métricas fuera de muestra

#### Scenario: Pines in-sample no provistos

- **WHEN** se invoca la evaluación fuera de muestra sin `pines_in_sample`
- **THEN** la sección falla con un error que indica tomarlos del README de `evaluation/data/campana/`

#### Scenario: Commit distinto cuando ambos bloques lo registran

- **WHEN** ambos `cache_meta` traen `commit` (o se provee `commit_in_sample`) y los valores difieren
- **THEN** el análisis aborta con un error que muestra ambos commits

#### Scenario: Commit in-sample ausente declara limitación sin abortar

- **WHEN** el `cache_meta` in-sample no trae `commit`, no se provee `commit_in_sample`, `classifier_version` coincide y los `pines` del cache independiente son iguales a `pines_in_sample`
- **THEN** el análisis reporta ambos bloques sin abortar
- **AND** la salida declara como limitación "commit in-sample no registrado; comparabilidad verificada por versión y pines"

#### Scenario: Verificación de no solape fallida

- **WHEN** `verificar_no_solape` informa casos compartidos entre el corpus independiente y el corpus de evaluación
- **THEN** el análisis aborta nombrando los casos en solape y no reporta métricas fuera de muestra

#### Scenario: Corpus independiente ausente

- **WHEN** falta el corpus independiente o sus predicciones
- **THEN** la sección fuera de muestra se declara "no se obtuvo" nombrando el artefacto faltante y no reporta métricas in-sample en su lugar

#### Scenario: Sin llamadas a Gemini ni reescritura de artefactos v9

- **WHEN** se ejecuta la evaluación fuera de muestra
- **THEN** no se invoca `run_evaluation.main()` y `evaluation/report.md` y `evaluation/predicciones.json` quedan byte a byte iguales

### Requirement: Ejecución offline, determinista y de solo lectura del análisis de campaña

El análisis de campaña SHALL ejecutarse sin red ni servicios externos mediante el CLI
`evaluation/analisis_campana.py`, que MUST limitarse a leer las entradas (planilla C1,
`registro_sujetos`, export C5, plan C6, predicciones C9 y corpus), re-verificar lo mínimo con
error accionable que nombre archivo y columna, delegar en funciones puras y escribir solo en
`evaluation/data/campana/analisis/` los archivos `resultados.json`, `resultados.md` y
`SHA256SUMS.txt` (SHA-256 de cada salida y de cada entrada leída), con un README de
procedencia. Cada sección MUST ejecutarse de forma independiente: un dataset ausente marca su
sección "no se obtuvo" sin abortar las demás. Los resultados MUST ser idénticos sobre las
mismas entradas. Los helpers de bootstrap MUST ser los públicos `percentil_intervalo` y
`remuestreos_indices` de `evaluation/metrics.py`, promovidos sin cambio de comportamiento. Las
pruebas MUST correr sobre fixtures sintéticos de `evaluation/tests/fixtures/campana/`, marcados
como SINTÉTICOS en su README.

#### Scenario: Análisis sin red sobre fixtures sintéticos

- **WHEN** se ejecuta el CLI sobre los fixtures sintéticos con las conexiones de red bloqueadas
- **THEN** el análisis completa todas las secciones sin intentar conexiones externas

#### Scenario: Reproducibilidad

- **WHEN** se ejecuta dos veces el CLI con las mismas entradas
- **THEN** `resultados.json` y `SHA256SUMS.txt` son idénticos en ambas corridas

#### Scenario: Escritura acotada a la carpeta de salida

- **WHEN** el CLI termina
- **THEN** solo existen archivos nuevos o modificados dentro de la carpeta de salida indicada

#### Scenario: Dataset ausente no aborta las demás secciones

- **WHEN** falta el export de intervención pero existen la planilla y el registro de sujetos
- **THEN** la sección de intervención se declara "no se obtuvo" y las secciones de kappa y exactitud manual se reportan

#### Scenario: Helpers de bootstrap compartidos

- **WHEN** se inspeccionan los módulos de kappa y de campaña
- **THEN** usan `percentil_intervalo` y `remuestreos_indices` importados de `evaluation/metrics.py` y los IC bootstrap existentes de `intervalos_por_clase` no cambian

#### Scenario: Columna faltante en una entrada

- **WHEN** una entrada no tiene una columna exigida por su contrato
- **THEN** el CLI falla en esa sección con un error que nombra el archivo y la columna faltante
