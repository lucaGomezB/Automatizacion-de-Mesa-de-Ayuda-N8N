# tesis-numeros-canonicos Specification

## Purpose
Definir el contrato del memo canónico de números de la tesis: un registro único,
verificable y con procedencia por valor que fija los números y criterios que el
documento puede citar, declara la regla efectiva del gate de revisión humana y
resuelve —o declara explícitamente como no resolubles— las contradicciones
numéricas internas detectadas por el dictamen CONEAU. El memo actúa como Gate 0
antes de que cualquier rama reescriba el texto de la tesis.

## Requirements

### Requirement: Registro canónico con procedencia por valor

El proyecto SHALL mantener el memo `docs/Tesis/Correcciones/numeros-canonicos.md`
como fuente única de verdad numérica de la tesis. Cada valor citable SHALL
registrarse con su procedencia (archivo y línea de origen) y su estado, que SHALL
ser uno de `vigente`, `retirado` o `condicional`. El memo MUST NOT contener ningún
valor sin fuente verificable y MUST distinguir el valor vigente del valor retirado
cuando una corrección reemplace una cifra previa.

Todo margen de error que la tesis publique SHALL registrarse en el memo con su valor,
los insumos de la fórmula que lo producen (incluido el tamaño del universo `N`, el
nivel de confianza, la proporción esperada y el tamaño muestral), su procedencia y su
estado. Cuando el universo cambie, el memo SHALL marcar el margen anterior y su `N`
como `retirado` en la misma operación de upsert que registra el nuevo valor como
`vigente`. Toda referencia `archivo:línea` del memo a un `.tex` SHALL resolverse, en la
fecha de consolidación, a la línea que contiene el valor citado; el memo MUST NOT
conservar referencias desplazadas por ediciones posteriores.

#### Scenario: Todo valor tiene fuente y estado

- **WHEN** se recorre la tabla canónica del memo
- **THEN** cada fila declara el valor, el archivo y la línea de origen, y un estado en `{vigente, retirado, condicional}`
- **AND** la línea indicada existe en el archivo referenciado

#### Scenario: Valor retirado no se cita como vigente

- **WHEN** una cifra fue desmentida por la evidencia disponible
- **THEN** el memo la marca como `retirado` y el valor de reemplazo queda como `vigente`
- **AND** las ramas consumidoras no citan el valor retirado como resultado

#### Scenario: Margen de error registrado con su N

- **WHEN** la tesis publica un margen de error absoluto y su tamaño muestral
- **THEN** el memo registra el margen como `vigente` con el valor de `N`, los demas insumos de la fórmula y su procedencia
- **AND** el margen anterior y su `N` quedan marcados como `retirado`, sin borrarse

#### Scenario: Referencias de línea sin desplazamiento

- **WHEN** se verifica cada referencia `archivo:línea` del memo contra el `.tex` en la fecha de consolidación
- **THEN** la línea citada contiene el valor o el pasaje que el memo le atribuye
- **AND** no queda ninguna referencia desplazada por ediciones posteriores, incluidas las de `07-resultados.tex`

### Requirement: Regla del gate de intervención humana declarada y trazable

El memo SHALL declarar la regla exacta del gate de revisión humana implementada y
la tabla de contingencia `confianza × etapa × acierto` reconstruida desde
`evaluation/predicciones.json`. El memo SHALL explicar qué confianza asigna la
etapa determinística y por qué no dispara revisión. La proporción de intervención
humana SHALL registrarse como `vigente` únicamente si es derivable de una fuente
primaria permitida; en caso contrario SHALL registrarse como `retirado` y el aporte
operativo SHALL reformularse sin esa cifra.

#### Scenario: Contingencia publicada

- **WHEN** se lee la sección del gate en el memo
- **THEN** figura la tabla de contingencia de confianza contra acierto desagregada por etapa del pipeline
- **AND** se declara que los casos con confianza inferior a 0,70 corresponden a la etapa determinística

#### Scenario: Intervención no derivable se retira

- **WHEN** la proporción de intervención humana no puede derivarse de `evaluation/predicciones.json`, `evaluation/report.md` ni `data/`
- **THEN** el memo registra la cifra como `retirado`
- **AND** el memo reformula el aporte operativo sin esa cifra

#### Scenario: Tramo de alta confianza verificado

- **WHEN** el texto vigente cita un tramo de casos con confianza alta y su número de errores
- **THEN** el memo registra el valor recalculado desde `evaluation/predicciones.json`
- **AND** declara si ese tramo se deduce o no de la tabla de bandas publicada

### Requirement: Criterio único de universo y proyección horaria

El memo SHALL fijar un único criterio para el universo de incidentes (días
calendario o días hábiles), coherente con el origen de la tasa diaria declarada.
El memo SHALL registrar el universo y la proyección horaria resultantes bajo ese
criterio, y SHALL declarar la propagación obligatoria a los capítulos que citan
ambos valores. Las dos lecturas SHALL quedar documentadas, con una marcada como
`vigente` y la otra como `retirado`.

#### Scenario: Criterio único declarado

- **WHEN** se lee la sección del universo en el memo
- **THEN** se declara explícitamente si el universo se computa sobre días calendario o hábiles
- **AND** la tasa diaria usada es coherente con el criterio elegido

#### Scenario: Proyección horaria recalculada y propagada

- **WHEN** se adopta el criterio de días hábiles
- **THEN** el memo registra el universo recalculado y la proyección de horas-persona recalculada con el ahorro medio por incidente
- **AND** declara los archivos de la tesis que deben propagar el valor vigente

### Requirement: Paradigma métrico definido y reproducible

El memo SHALL definir si la tarea se evalúa como monoetiqueta o multietiqueta y
SHALL fijar el set métrico final, distinguiendo las métricas primarias de las
secundarias. El memo SHALL documentar el procedimiento de recálculo desde
`evaluation/predicciones.json` sin re-ejecutar el sistema. Las métricas
multietiqueta SHALL reportarse contra una referencia multietiqueta declarada y
MUST NOT presentarse como equivalentes de la exactitud de etiqueta única.

#### Scenario: Paradigma y set métrico declarados

- **WHEN** se lee la sección de métricas del memo
- **THEN** se declara si la referencia de verdad es monoetiqueta o multietiqueta
- **AND** se listan las métricas primarias y secundarias con su definición

#### Scenario: Recálculo reproducible sin re-ejecutar

- **WHEN** se sigue el procedimiento de recálculo documentado en el memo
- **THEN** las métricas se reproducen desde `evaluation/predicciones.json`
- **AND** no se requiere invocar el clasificador ni servicios externos

### Requirement: Tratamiento de la clase con soporte unitario

El memo SHALL declarar como no estimable toda clase cuya frecuencia en el corpus
sea de un solo caso, y SHALL reportar el efecto de su exclusión sobre la métrica
de umbral. El memo MUST NOT presentar el valor métrico de una clase con n=1 como
evidencia de desempeño del clasificador.

#### Scenario: Clase con n=1 declarada no estimable

- **WHEN** se lee la sección de métricas por clase del memo
- **THEN** la clase con soporte 1 se declara no estimable
- **AND** se reporta el valor de la métrica de umbral con y sin esa clase

### Requirement: Decisiones no resolubles declaradas con decisión editorial

El memo SHALL incluir una sección "Decisiones no resolubles" en la que cada punto
que la evidencia disponible no permita cerrar SHALL declararse de forma explícita,
junto con la decisión editorial adoptada y su condición de reversibilidad.

#### Scenario: Punto no resoluble documentado

- **WHEN** una contradicción numérica no puede reconciliarse con las fuentes permitidas
- **THEN** el memo la declara en "Decisiones no resolubles"
- **AND** registra la decisión editorial adoptada y la condición bajo la cual se revisaría

### Requirement: Gate 0 como prerrequisito de las ramas consumidoras

Este contrato SHALL actuar como Gate 0: ninguna rama que reescriba los capítulos
de la tesis SHALL fijar números nuevos sin citar el valor vigente del memo. Toda
rama consumidora MUST consumir la tabla canónica y MUST NOT redefinir sus valores
por separado.

#### Scenario: Rama consumidora cita el memo

- **WHEN** una rama de corrección reescribe un capítulo que cita números
- **THEN** los valores usados coinciden con el valor vigente del memo
- **AND** toda divergencia se resuelve actualizando el memo, no el capítulo de forma aislada

### Requirement: Obligación de propagación de las ramas consumidoras

Toda rama que reescriba los capítulos de la tesis SHALL propagar los valores
`vigente` del memo canónico y MUST NOT reintroducir los valores `retirado`. La rama
SHALL registrar en su `design.md` la lista de objetivos de propagación con la
palabra textual ANTES y DESPUÉS, y SHALL declarar la condición de reversibilidad
de cada decisión editorial que aplique. La rama SHALL dejar el documento sin
ninguna ocurrencia del valor `retirado` que reemplace.

#### Scenario: Rama consumidora propaga los valores vigentes

- **WHEN** una rama reescribe un capítulo que cita un valor `retirado`
- **THEN** el capítulo pasa a citar el valor `vigente` del memo
- **AND** el valor `retirado` no queda en ningún pasaje como resultado

#### Scenario: Reversibilidad declarada

- **WHEN** la rama aplica una decisión editorial del memo (por ejemplo retirar la proporción de intervención humana)
- **THEN** la rama declara en su `design.md` la condición bajo la cual esa decisión se revisaría
- **AND** la decisión no se fija como irreversible si el memo la marca reversible

### Requirement: Incertidumbre del kappa y de las metricas por clase

El memo canonico SHALL registrar el intervalo de confianza del coeficiente kappa
de doble etiquetado y los intervalos de confianza de las metricas por clase
(precision, sensibilidad y F1 una contra el resto), junto con el procedimiento de
estimacion empleado y su nivel de confianza. El memo SHALL declarar como no
estimable toda clase con soporte unitario y SHALL excluirla de los estimadores
agregados de umbral. Cuando una incertidumbre no sea computable a partir de las
fuentes primarias permitidas, el memo SHALL declararlo de forma explicita con la
condicion de reversibilidad, en lugar de presentar el valor puntual como si
tuviera incertidumbre cuantificada.

#### Scenario: IC por clase registrado con procedimiento

- **WHEN** se lee la seccion de metricas del memo
- **THEN** cada clase estimable declara su IC de precision, sensibilidad y F1
- **AND** se declara el metodo de estimacion (por ejemplo Wilson o bootstrap percentil) y el nivel de confianza

#### Scenario: Clase con soporte unitario sin IC

- **WHEN** se recorre la tabla de metricas por clase del memo
- **THEN** la clase con `n = 1` (`Bases de Datos`) se declara no estimable y sin IC
- **AND** su valor puntual NO se presenta como evidencia de desempeno del clasificador

#### Scenario: IC del kappa registrado o declarado no estimable

- **WHEN** se lee el registro de incertidumbre del kappa de doble etiquetado
- **THEN** figura su IC con el procedimiento de estimacion, o bien la declaracion explicita de que no es computable desde las fuentes permitidas y la condicion bajo la cual se incorporaria

### Requirement: Marco metrico unificado mono y multietiqueta

El memo canonico SHALL presentar la exactitud estricta, la macro-F1 (cinco y
cuatro clases estimables), el micro-F1, la subset accuracy y el Hamming loss
dentro de un unico marco que declare, para cada metrica, la tarea de referencia
(monoetiqueta o multietiqueta) y su relacion con las demas. El memo MUST NOT
presentar el micro-F1 ni las metricas de conjunto como equivalentes de la
exactitud de etiqueta unica, y SHALL explicitar la penalizacion estructural que
las metricas de conjunto imponen sobre una salida forzada a una etiqueta.

#### Scenario: Marco unico con referencia declarada

- **WHEN** se lee la seccion de metricas del memo
- **THEN** cada metrica declara si su referencia de verdad es monoetiqueta o multietiqueta
- **AND** se enuncian las metricas primarias (monoetiqueta) y las secundarias (multietiqueta) en una sola tabla o marco

#### Scenario: No equivalencia de micro-F1 y exactitud

- **WHEN** se compara el micro-F1 con la exactitud estricta en el memo
- **THEN** el memo declara que no son equivalentes y explica por que difieren (`0,6654` frente a `0,7350`)
- **AND** no deja el micro-F1 rotulado como exactitud multietiqueta

### Requirement: Registro canonico del gate por etapa y del punto de operacion del cortocircuito

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar, con archivo y linea de origen y estado, los valores que la tesis cita para describir el gate de revision por etapa y el cortocircuito de la etapa deterministica: los casos con confianza inferior a 0,70 sin escalamiento (`124/200`, `62,0 %`, todos de la etapa deterministica), la confianza minima declarada por la etapa Gemini (`0,85` en sus `69` casos), el punto de operacion del cortocircuito (`0,5166`, derivado por validacion cruzada de cinco pliegues), su cobertura (`131/200`), la precision del filtro sobre el conjunto cortocircuitable (`97/131`, `0,7405`) y la de la etapa Gemini sobre ese conjunto (`88/130`, `0,6769`). El memo SHALL declarar que ambas precisiones son estimaciones dentro de la muestra, que `88/130` proviene de la cache FORCE-ESCALATE con un caso excluido por no tener prediccion de Gemini, y SHALL registrar en "Decisiones no resolubles" la procedencia no documentada de esa cache con su condicion de reversibilidad. El memo MUST NOT modificar ningun valor vigente previo.

#### Scenario: Filas con procedencia y estado

- **WHEN** se lee la seccion del gate por etapa del memo
- **THEN** cada uno de los valores `124/200`, `62,0 %`, `0,85`, `0,5166`, `131/200`, `97/131`, `0,7405`, `88/130` y `0,6769` declara un archivo y una linea de origen que existen, y el estado `vigente`
- **AND** ningun valor vigente de las Secciones 3.1 a 3.6 cambia

#### Scenario: Salvedades declaradas

- **WHEN** se leen las notas de `97/131` y `88/130`
- **THEN** se declara que son estimaciones dentro de la muestra
- **AND** se declara la exclusion del caso sin prediccion de Gemini y la fuente de la cache FORCE-ESCALATE

#### Scenario: Procedencia de la cache registrada como no resoluble

- **WHEN** no puede verificarse desde fuentes versionadas la fecha ni la version del prompt de la cache FORCE-ESCALATE
- **THEN** la Seccion 7 del memo lo declara con la decision editorial adoptada
- **AND** registra que se revisa si el autor aporta el `cache_meta` de la cache

#### Scenario: Consumo por la tesis

- **WHEN** la tesis cita 124, 62 %, 0,85, 0,5166, 131, 0,7405 o 0,6769 en el contexto del gate o del cortocircuito
- **THEN** el valor coincide con el valor vigente del memo

### Requirement: Registro de las metricas por etapa, por canal y de la exactitud laxa

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar, en una seccion propia, la exactitud estricta y laxa por etapa del pipeline y por canal de origen con sus IC de Wilson, la descomposicion por etapa de las bandas de confianza y del tramo de confianza `>= 0,90`, la distribucion de valores de confianza por etapa y el contraste pareado de McNemar entre la etapa deterministica y Gemini sobre el conjunto cortocircuitable ---o su declaracion de no computable---, rotulado como insumo de c-133 y c-142 y acompanado de sus salvedades (otra corrida y otra version que la oficial; contraste en muestra). Cada valor SHALL registrarse con su procedencia verificable ---linea del reporte regenerado o derivacion aritmetica explicita desde valores ya canonicos--- y con su estado. Los valores ya canonicos de la calibracion (bandas `98/26/6/31/39` con `75/19/2/22/29` aciertos, contingencia `76/53` y `124/94`, tramo `46/13`) SHALL conservarse sin cambio de valor, y su lectura SHALL anotarse como efecto de composicion entre etapas. La lectura de "anti-calibracion" del clasificador en su conjunto SHALL registrarse como retirada.

#### Scenario: Valores nuevos con procedencia y estado

- **WHEN** se recorre la seccion nueva del memo
- **THEN** cada valor por etapa, por canal y de exactitud laxa declara su procedencia (archivo y linea, o derivacion explicita) y un estado en `{vigente, retirado, condicional}`
- **AND** ningun valor carece de fuente verificable

#### Scenario: Descomposicion por etapa consistente con los canonicos

- **WHEN** se suman, banda por banda, los casos y aciertos de la etapa deterministica y de la etapa Gemini
- **THEN** las sumas reproducen la tabla de bandas canonica (`98/26/6/31/39` casos y `75/19/2/22/29` aciertos)
- **AND** los totales por etapa reproducen `131/97` y `69/50`

#### Scenario: Lectura retirada anotada

- **WHEN** se lee la entrada de la contingencia de confianza o de las bandas en el memo
- **THEN** se anota que el contraste agregado `0,697` frente a `0,758` es un efecto de composicion entre etapas
- **AND** la lectura de anti-calibracion del clasificador en su conjunto figura como retirada

#### Scenario: Contraste de McNemar registrado o declarado no computable

- **WHEN** se lee la seccion nueva del memo
- **THEN** figura el contraste de McNemar (pares, `b`, `c`, estadistico, p primario y criterio) con procedencia en `docs/deterministic_calibration.md` y sus salvedades, o la declaracion de que no es computable con los artefactos disponibles
- **AND** se lo rotula como insumo de c-133 y c-142

### Requirement: Procedencia de las predicciones por caso y politica de deriva

Los valores canonicos de clasificacion SHALL provenir de la corrida oficial del clasificador (`hybrid-v3`, predicciones generadas el 2026-10-07), identificada en el memo por su `cache_meta` y por el SHA-256 del archivo de predicciones. Antes de usar como fuente un archivo de predicciones recuperado, su metadata (hash del corpus, cantidad de casos y version del clasificador) y su huella agregada (exactitud `147/200`, etapas `131/69/0`, bandas, contingencia y tramo `>= 0,90` canonicos) MUST coincidir con los valores canonicos. Una corrida de reproduccion (nueva invocacion al proveedor) MUST NOT sobrescribir las predicciones oficiales, `evaluation/report.md` ni ningun valor canonico vigente: sus resultados SHALL escribirse en archivos separados, rotularse con su version y fecha, y acompanarse de la deriva cuantificada respecto de los agregados oficiales de la etapa Gemini. El reemplazo de los canonicos por una corrida nueva SHALL requerir una decision explicita del usuario registrada en el memo.

#### Scenario: Archivo recuperado con huella coincidente

- **WHEN** se recupera un `evaluation/predicciones.json` cuya metadata y cuya huella agregada coinciden con los valores canonicos
- **THEN** el archivo se acepta como fuente de los valores nuevos
- **AND** su `cache_meta` y su SHA-256 quedan registrados en el memo

#### Scenario: Archivo recuperado con huella discrepante

- **WHEN** la metadata o algun agregado de la huella de un archivo recuperado difiere de los valores canonicos
- **THEN** el archivo se rechaza como fuente de valores canonicos
- **AND** la discrepancia se registra sin modificar ningun valor vigente

#### Scenario: Corrida de reproduccion rotulada y separada

- **WHEN** el usuario autoriza una corrida de reproduccion porque las predicciones oficiales no pudieron recuperarse
- **THEN** sus predicciones y su reporte se escriben en archivos distintos de `evaluation/predicciones.json` y `evaluation/report.md`, con su version y fecha
- **AND** el memo registra la deriva de la etapa Gemini frente a los agregados oficiales (`50/69` aciertos, bandas `31/22` y `38/28`, tramo `>= 0,90` de `45` casos con `13` errores)

#### Scenario: Sin reemplazo silencioso de los canonicos

- **WHEN** una corrida de reproduccion produce agregados distintos de los oficiales
- **THEN** los valores canonicos vigentes del memo y de la tesis no cambian
- **AND** solo una decision explicita del usuario, registrada en el memo, habilita su reemplazo

### Requirement: Registro de los valores de sensibilidad frente al ajuste con el corpus

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar, en una seccion propia, cada valor del analisis de sensibilidad frente al ajuste del clasificador con el corpus que la tesis cite o que sostenga su lectura: variante principal (casos, aciertos, exactitud, IC de Wilson y cobertura), descomposicion pareada, referencia historica y su control de fidelidad, exactitud global con Gemini fijo y contraste entre etapas con el vocabulario previo (o su declaracion de no computable), efecto de las reglas de frontera del prompt por nivel (o su declaracion de no cuantificado) y, si aplica, los resultados sobre el conjunto de preproduccion. Cada valor SHALL declarar su procedencia (linea de `evaluation/report_sensibilidad_ajustes.md`, archivo de un brazo de la ablacion o derivacion aritmetica explicita desde valores versionados), su estado (`vigente` como valor de sensibilidad, o `condicional` mientras su checkpoint siga abierto) y el rotulo "sensibilidad: no reemplaza valores canonicos". Las filas de `97/131` (`0,7405`) y de `88/130` (`0,6769`) SHALL llevar una nota que las califique como estimaciones dentro de la muestra y remita a esa seccion. La seccion de decisiones no resolubles SHALL registrar la no factibilidad de la variante por pliegues, la version del prompt de la cache FORCE-ESCALATE (o su indeterminacion) y el desenlace sobre el conjunto de preproduccion. El memo MUST NOT modificar ningun valor vigente previo.

#### Scenario: Valores con procedencia, estado y rotulo

- **WHEN** se recorre la seccion de sensibilidad del memo
- **THEN** cada valor declara una procedencia verificable, un estado en `{vigente, condicional}` y el rotulo de sensibilidad
- **AND** cada `archivo:linea` citado existe y contiene el valor

#### Scenario: Valores canonicos intactos

- **WHEN** se compara el memo antes y despues del change
- **THEN** ninguna celda de valor con estado `vigente` previo cambio
- **AND** los cambios en filas previas se limitan a notas agregadas

#### Scenario: Notas de estimacion dentro de la muestra

- **WHEN** se leen las filas de `97/131` y de `0,7405` frente a `0,6769`
- **THEN** cada una incluye la nota que la califica como estimacion dentro de la muestra y la remision a la seccion de sensibilidad

#### Scenario: Decisiones no resolubles registradas

- **WHEN** se lee la seccion de decisiones no resolubles
- **THEN** figuran la variante por pliegues como no factible con su motivo y su condicion de reversibilidad, la clasificacion de la version del prompt de la cache FORCE-ESCALATE y el desenlace sobre el conjunto de preproduccion

#### Scenario: Salidas no computables sin valores

- **WHEN** una salida del analisis no fue computable con los artefactos disponibles
- **THEN** el memo la registra como no computable, con su motivo
- **AND** no consigna ningun valor estimado para ella

### Requirement: Corridas de sensibilidad sin efecto sobre los valores canonicos

Una corrida de sensibilidad, sea la re-medicion offline con otra configuracion del clasificador o una ablacion que invoque al proveedor, MUST NOT sobrescribir las predicciones oficiales, `evaluation/report.md` ni ningun valor canonico vigente. Sus resultados SHALL escribirse en archivos separados, rotulados con la configuracion evaluada, el hash del prompt cuando corresponda y la fecha, y SHALL citarse en la tesis solo como sensibilidad. El reemplazo de un valor canonico por uno de sensibilidad SHALL requerir una decision explicita del usuario registrada en el memo.

#### Scenario: Archivos separados y rotulados

- **WHEN** se ejecuta una corrida de sensibilidad
- **THEN** sus salidas se escriben en archivos distintos de `evaluation/predicciones.json` y `evaluation/report.md`, rotulados con su configuracion y su fecha

#### Scenario: Canonicos sin cambio ante resultados distintos

- **WHEN** una corrida de sensibilidad produce valores distintos de los canonicos
- **THEN** los valores vigentes del memo y de la tesis no cambian
- **AND** la tesis presenta los valores de sensibilidad como tales, con remision a su seccion del memo

### Requirement: Consolidacion de los valores de la familia de correcciones del dictamen v10 antes de la release

Antes de etiquetar la release que cierra el dictamen CONEAU del 2026-10-22 sobre la tesis v10 / `v1.1.0`, el memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar cada valor numerico de resultado que la familia c-130..c-142 (c-130 a c-140 y c-142) incorpore a la tesis (por ejemplo, exactitud por etapa con su intervalo de Wilson, exactitud por canal, exactitud laxa con su intervalo, contraste pareado entre etapas, tiempos manuales por canal y contraste intra-canal, valor p unilateral, d_z, distribucion del universo por sector, escenarios del balance neto, valores de sensibilidad fuera de muestra y la designacion de la metrica primaria), cada uno con su procedencia (archivo y linea de origen) y su estado (`vigente`, `retirado` o `condicional`). Ningun numero de resultado agregado a `sections/*.tex` por la familia MUST quedar sin fila en el memo. Todo valor que no pueda derivarse de las fuentes permitidas (por ejemplo, por caches de predicciones no recuperadas o por una corrida paga no autorizada) SHALL declararse en "Decisiones no resolubles" con su condicion de reversibilidad, y la tesis MUST NOT presentarlo como resultado medido. Las secciones del memo SHALL tener numeracion unica y consecutiva, asignada por orden de aplicacion de los changes, y toda remision cruzada entre secciones SHALL resolver. Ninguna corrida de sensibilidad MUST reemplazar un valor canonico vigente. El encabezado del memo SHALL identificar la version de trabajo (v10), la release (`v1.2.0`) y la fecha de consolidacion. `evaluation/report.md` y `evaluation/report_sensibilidad_ajustes.md` SHALL coincidir con los valores del memo que reportan.

#### Scenario: Valores de la familia registrados con procedencia

- **WHEN** se recorre el memo despues de aplicar la familia
- **THEN** cada valor de resultado introducido por c-130..c-140 y c-142 figura con archivo y linea de origen y con un estado en `{vigente, retirado, condicional}`
- **AND** la linea indicada existe en el archivo referenciado

#### Scenario: Tesis sin numeros huerfanos

- **WHEN** se comparan los numeros de resultado agregados por la familia en `sections/*.tex` (diff entre `v1.1.1` y el arbol del commit C1) contra el memo
- **THEN** cada uno figura en el memo como `vigente` o `condicional`
- **AND** ninguno existe solo en la tesis

#### Scenario: Valores sin procedencia declarados

- **WHEN** un valor previsto por la familia no puede derivarse de `evaluation/`, `data/` ni de las caches de predicciones disponibles, o depende de una corrida paga no autorizada
- **THEN** el memo lo declara en "Decisiones no resolubles" con la decision editorial y la condicion bajo la cual se revisaria
- **AND** la tesis no lo presenta como resultado medido

#### Scenario: Numeracion unica de las secciones del memo

- **WHEN** se listan los encabezados de la Seccion 3 del memo despues de aplicar la familia
- **THEN** cada numero `3.N` aparece una sola vez y la secuencia es consecutiva
- **AND** toda nota del tipo "ver seccion 3.N" del memo, del registro y de los artefactos archivados de la familia apunta a una seccion existente con el contenido citado

#### Scenario: Valores canonicos vigentes sin cambios por la sensibilidad

- **WHEN** se compara el memo con su estado previo a la aplicacion de c-142
- **THEN** ningun valor `vigente` cambio por efecto de una corrida de sensibilidad
- **AND** los valores de sensibilidad figuran en una seccion propia, con notas cruzadas en las filas de `97/131` y `0,7405`/`0,6769`

#### Scenario: Encabezado del memo actualizado

- **WHEN** se lee el encabezado del memo en el commit etiquetado
- **THEN** identifica la version de trabajo v10, la release `v1.2.0` y la fecha de consolidacion
- **AND** conserva el SHA-256 del corpus `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`

#### Scenario: Reportes de evaluacion coherentes con el memo

- **WHEN** se comparan los valores de `evaluation/report.md` y de `evaluation/report_sensibilidad_ajustes.md` con los valores del memo
- **THEN** coinciden en todos los valores que ambos reportan
- **AND** `evaluation/report.md` conserva sus secciones de normalidad (Shapiro-Wilk), Wilcoxon y desglose por canal
