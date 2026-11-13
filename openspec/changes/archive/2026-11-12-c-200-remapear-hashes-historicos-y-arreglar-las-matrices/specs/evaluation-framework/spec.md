## MODIFIED Requirements

### Requirement: Analisis de sensibilidad de la etapa deterministica frente al vocabulario ajustado con el corpus

El framework SHALL ofrecer un analisis offline, sin invocar al proveedor de inferencia, que re-mida la etapa deterministica sobre el corpus de evaluacion con el vocabulario vigente antes de su ampliacion guiada por el corpus (c-71), versionado en `evaluation/` con su procedencia (commit, blob y SHA-256), en dos configuraciones: (a) **principal**, vocabulario previo con la logica de decision y el punto de operacion vigentes, leidos de `Settings`, de modo que solo cambie el vocabulario; y (b) **referencia historica**, vocabulario previo con la logica de decision de la epoca (confianza `w / (w + r + 1e-6)`, cortocircuito con confianza `>= 0,90`). Antes de reportar cualquier variante, el analisis SHALL reproducir por el mismo camino la configuracion evaluada (131 casos cortocircuitados y 97 aciertos estrictos, identicos caso por caso al clasificador de produccion). Para cada configuracion SHALL reportar casos cortocircuitados, aciertos estrictos, exactitud con su IC de Wilson al 95 % y cobertura sobre el corpus; para la principal, ademas, la descomposicion pareada frente a la configuracion evaluada. La referencia historica SHALL compararse con la linea base documentada por c-71 y el reporte SHALL declarar si coincide o difiere; la replica de la logica historica MUST NOT ajustarse a los datos. Cuando el repositorio no registre que casos motivaron cada patron agregado, el reporte SHALL declarar no factible la variante por pliegues y su motivo. El analisis MUST NOT modificar el codigo de `App/`, el vocabulario de produccion, `evaluation/report.md` ni las caches de predicciones, y su salida SHALL escribirse en `evaluation/report_sensibilidad_ajustes.md`. Los SHAs de commit que la procedencia cita (`evaluation/data/sensibilidad_ajustes/procedencia.json`, `evaluation/sensibilidad_ajustes.py` y sus pruebas) SHALL pertenecer a la historia saneada del repositorio (ancestros de `HEAD`), coherentes con la advertencia metodologica de `evaluation/README.md`, que ya cita `c8112d2`, `27f8d8c` y `bf5e099`. Los SHAs de blob citados por la misma procedencia MUST NOT remapearse.

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

#### Scenario: Procedencia con SHAs de la historia saneada

- **WHEN** se ejecutan las pruebas de `evaluation/tests/test_sensibilidad_ajustes.py`, `test_sensibilidad_corpus.py` y `test_campana.py` tras este change
- **THEN** pasan en verde y las aserciones sobre SHAs de commit esperan los valores de la historia saneada (`c8112d20`, `27f8d8c2`, `0fe5e08a`, `bf5e099c`, `5f21a258`)
- **AND** los SHAs de blob que la procedencia cita (`858f1c67`, `334a8edb`, `49267f4a`, `1daceb38`, `e69de29b`) conservan su valor
