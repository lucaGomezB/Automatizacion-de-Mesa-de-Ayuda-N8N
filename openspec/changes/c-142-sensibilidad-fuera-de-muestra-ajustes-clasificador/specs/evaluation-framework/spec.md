## ADDED Requirements

### Requirement: Analisis de sensibilidad de la etapa deterministica frente al vocabulario ajustado con el corpus

El framework SHALL ofrecer un analisis offline, sin invocar al proveedor de inferencia, que re-mida la etapa deterministica sobre el corpus de evaluacion con el vocabulario vigente antes de su ampliacion guiada por el corpus (c-71), versionado en `evaluation/` con su procedencia (commit, blob y SHA-256), en dos configuraciones: (a) **principal**, vocabulario previo con la logica de decision y el punto de operacion vigentes, leidos de `Settings`, de modo que solo cambie el vocabulario; y (b) **referencia historica**, vocabulario previo con la logica de decision de la epoca (confianza `w / (w + r + 1e-6)`, cortocircuito con confianza `>= 0,90`). Antes de reportar cualquier variante, el analisis SHALL reproducir por el mismo camino la configuracion evaluada (131 casos cortocircuitados y 97 aciertos estrictos, identicos caso por caso al clasificador de produccion). Para cada configuracion SHALL reportar casos cortocircuitados, aciertos estrictos, exactitud con su IC de Wilson al 95 % y cobertura sobre el corpus; para la principal, ademas, la descomposicion pareada frente a la configuracion evaluada. La referencia historica SHALL compararse con la linea base documentada por c-71 y el reporte SHALL declarar si coincide o difiere; la replica de la logica historica MUST NOT ajustarse a los datos. Cuando el repositorio no registre que casos motivaron cada patron agregado, el reporte SHALL declarar no factible la variante por pliegues y su motivo. El analisis MUST NOT modificar el codigo de `App/`, el vocabulario de produccion, `evaluation/report.md` ni las caches de predicciones, y su salida SHALL escribirse en `evaluation/report_sensibilidad_ajustes.md`.

#### Scenario: Configuracion evaluada reproducida antes de reportar

- **WHEN** el analisis clasifica el corpus con el vocabulario vigente por el camino de inyeccion de vocabulario
- **THEN** obtiene 131 casos cortocircuitados y 97 aciertos estrictos, con prediccion, confianza, score y estados de ausencia y empate identicos a los del clasificador de produccion en cada caso
- **AND** si alguna de esas condiciones no se cumple, el analisis falla con un error explicito y no reporta ninguna variante

#### Scenario: Variante principal con intervalo de Wilson

- **WHEN** se clasifica el corpus con el vocabulario previo y la logica y el punto de operacion vigentes
- **THEN** el reporte declara casos cortocircuitados `n`, aciertos `k`, exactitud `k / n`, el IC igual a `intervalo_wilson(k, n)` y la cobertura `n / 200`
- **AND** el umbral, los pesos del score y el conteo minimo de coincidencias usados son los de la configuracion evaluada

#### Scenario: Descomposicion pareada aditiva

- **WHEN** se compara la variante principal con la configuracion evaluada
- **THEN** el reporte separa los casos cortocircuitados por ambas, solo por la evaluada y solo por la variante, con casos y aciertos de cada vocabulario en cada segmento y el contraste pareado sobre los casos comunes
- **AND** los segmentos del lado de la configuracion evaluada suman 131 casos y 97 aciertos

#### Scenario: Referencia historica contra la linea base documentada

- **WHEN** se clasifica el corpus con el vocabulario y la logica previos a c-71
- **THEN** el reporte presenta, frente a los valores documentados por c-71, los reproducidos: casos cortocircuitados (72; 22, 14 y 36 por canal de correo, web y telefono), aciertos estrictos (37; 13, 7 y 17), aciertos laxos (55), casos sin coincidencias (119) y predicciones de Seguridad Informatica (126), cada uno con la marca "coincide" o "difiere"
- **AND** ninguna constante de la replica se modifica para hacer coincidir los valores

#### Scenario: Artefactos historicos verificables

- **WHEN** se leen el vocabulario y el prompt previos versionados en `evaluation/data/sensibilidad_ajustes/`
- **THEN** el SHA-256 de cada archivo coincide con el registrado en su manifiesto de procedencia
- **AND** cada lista del vocabulario previo esta contenida en la vigente, con las cinco claves canonicas en el mismo orden y 62 patrones de diferencia, y el prompt previo es el vigente sin el bloque de reglas de frontera

#### Scenario: Variante por pliegues declarada no factible

- **WHEN** el repositorio no registra que casos del corpus motivaron cada patron agregado por c-71
- **THEN** el reporte declara no factible la reconstruccion del vocabulario por pliegues y enuncia el motivo
- **AND** no reporta como estimacion ninguna asignacion de patrones a pliegues

#### Scenario: Sin efectos sobre los artefactos oficiales

- **WHEN** se ejecuta el analisis offline
- **THEN** no se invoca al proveedor de inferencia ni se escriben `evaluation/report.md`, `evaluation/predicciones.json` ni `evaluation/predicciones_calibracion.json`

#### Scenario: Reporte reproducible

- **WHEN** el analisis offline se ejecuta dos veces sobre el mismo commit y el mismo corpus
- **THEN** `evaluation/report_sensibilidad_ajustes.md` resulta identico byte a byte

### Requirement: Sensibilidad de la exactitud global y del contraste entre etapas con predicciones cacheadas

Cuando la cache FORCE-ESCALATE (`evaluation/predicciones_calibracion.json`) este disponible y verificada, el framework SHALL calcular, sin invocar al proveedor: (a) la exactitud global del pipeline con el vocabulario vigente y con el vocabulario previo, usando en ambos lados las predicciones de la etapa Gemini de esa misma cache para todo caso escalado, sobre el mismo conjunto de casos y con el contraste pareado de McNemar; y (b) el contraste pareado entre la etapa deterministica con el vocabulario previo y la etapa Gemini sobre los casos que ese vocabulario cortocircuita. Las entradas de la cache con `etapa` distinta de `gemini` SHALL tratarse como ausentes, y un caso que requiera una prediccion ausente SHALL excluirse de ambos lados del contraste y listarse en el reporte. Sin la cache, el reporte SHALL declarar ambas salidas "no computable con los artefactos disponibles" y MUST NOT estimarlas por otra via.

#### Scenario: Exactitud global pareada con una sola fuente de predicciones

- **WHEN** la cache FORCE-ESCALATE esta disponible y se simula el pipeline con ambos vocabularios
- **THEN** el reporte declara los aciertos globales de cada configuracion sobre el mismo conjunto de casos y el resultado del contraste de McNemar
- **AND** todas las predicciones de la etapa Gemini de ambos lados provienen de esa cache

#### Scenario: Entradas no semanticas tratadas como ausentes

- **WHEN** un caso escalado por una configuracion solo tiene en la cache una entrada con `etapa` distinta de `gemini`
- **THEN** el caso se excluye de ambos lados del contraste y figura en la lista de excluidos del reporte

#### Scenario: Contraste entre etapas con el vocabulario previo

- **WHEN** se dispone de la cache y de las observaciones del vocabulario previo
- **THEN** el reporte declara, sobre los casos que el vocabulario previo cortocircuita y que tienen prediccion de Gemini, la exactitud de cada etapa y el contraste pareado

#### Scenario: Sin cache, salidas no computables

- **WHEN** la cache FORCE-ESCALATE no esta disponible o no paso su verificacion
- **THEN** el reporte declara la exactitud global con Gemini fijo y el contraste entre etapas como no computables
- **AND** no consigna ningun valor estimado para ellos

### Requirement: Sensibilidad de la etapa semantica frente a las reglas de frontera del prompt

El framework SHALL permitir acotar el efecto de las reglas de frontera del prompt sobre los casos que la configuracion evaluada escala a la etapa Gemini (los que no cortocircuita; 69 en el corpus vigente), por niveles: (a) exactitud de esa etapa con y sin los casos motivadores documentados de las reglas, a partir de la cache oficial; (b) comparacion pareada con una corrida historica cuyo prompt anteceda a las reglas, solo si su fecha de generacion es anterior a la propuesta de las reglas; y (c) ablacion controlada en dos brazos, prompt vigente y prompt sin reglas de frontera, sobre los mismos casos y en una misma sesion. La ablacion SHALL invocar al proveedor solo con confirmacion explicita, evaluada antes de construir el clasificador; SHALL verificar, antes de la primera invocacion, que el SHA-256 del prompt cargado coincide con el esperado para el brazo; SHALL escribir cada brazo en un archivo propio con metadatos de brazo, hash y origen del prompt, modelo, temperatura, version del clasificador, hash del corpus, casos, fecha y cantidad de respuestas de reserva; SHALL contar una respuesta de reserva como error; y MUST NOT escribir las predicciones ni el reporte oficiales. El reporte SHALL presentar cada nivel disponible y declarar los no disponibles.

#### Scenario: Corrida paga sin confirmacion

- **WHEN** se solicita un brazo de la ablacion sin `--confirm-paid` ni la variable de confirmacion
- **THEN** la ejecucion falla con un error de corrida paga no confirmada antes de construir el clasificador real
- **AND** no se realiza ninguna invocacion al proveedor

#### Scenario: Prompt verificado antes de invocar

- **WHEN** el prompt cargado por el backend para un brazo no tiene el SHA-256 esperado para ese brazo
- **THEN** la ejecucion falla antes de la primera invocacion y no escribe ningun archivo de salida

#### Scenario: Brazos sobre los mismos casos y en archivos separados

- **WHEN** se ejecutan ambos brazos con confirmacion
- **THEN** cada brazo clasifica exactamente los casos que la configuracion evaluada no cortocircuita y escribe su propio archivo con los metadatos requeridos
- **AND** `evaluation/predicciones.json` y `evaluation/report.md` no cambian

#### Scenario: Comparacion pareada entre brazos

- **WHEN** existen las predicciones de ambos brazos
- **THEN** el reporte declara los aciertos estrictos de cada brazo sobre los mismos casos, las respuestas de reserva contadas como error y el contraste pareado de McNemar
- **AND** si la cache oficial esta disponible, declara tambien la deriva del brazo vigente frente a la corrida oficial

#### Scenario: Version del prompt de una corrida historica

- **WHEN** se evalua el nivel (b) con una corrida historica
- **THEN** su prompt se clasifica como "previa confirmada", "probablemente previa", "posterior" o "indeterminada" segun su fecha de generacion frente a la propuesta y a la aplicacion de las reglas de frontera
- **AND** solo la clase "previa confirmada" habilita el uso del nivel (b) fuera del reporte

<!-- c-144 (archivado el 2026-10-23 en main) ya incorporo al spec vivo el requisito "Advertencia metodologica del framework coherente con el historial"; este change solo verifica el texto resultante. -->