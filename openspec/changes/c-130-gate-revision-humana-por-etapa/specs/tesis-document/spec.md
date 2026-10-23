## ADDED Requirements

### Requirement: Definicion de la confianza por etapa y del puntaje de correctitud

La tesis SHALL definir una sola vez, en la subseccion del subsistema de clasificacion de `05-arquitectura.tex` (`subsec:subsistema-clasificacion`), las dos magnitudes que emite la etapa deterministica: la confianza, como indice de fuerza de senal en [0;1] que vale 0 cuando el sector ganador reune menos de dos patrones coincidentes, y el puntaje de correctitud (`score_correctitud`), que ordena la correctitud esperada. La tesis SHALL declarar que ninguna de las dos es una probabilidad de acierto, que la confianza deterministica no es comparable con la confianza autodeclarada por el modelo de la etapa Gemini y que la etapa de reserva fija la confianza en 0,0 por construccion. Los capitulos `02`, `06`, `07`, `08` y `11` MUST usar las mismas denominaciones y MUST NOT atribuir a la decision del filtro deterministico una "alta certeza" o una "alta confianza".

#### Scenario: Dos magnitudes definidas

- **WHEN** se lee `subsec:subsistema-clasificacion` en el PDF compilado
- **THEN** se definen la confianza deterministica como indice de fuerza de senal en [0;1] y el puntaje de correctitud como criterio que ordena la correctitud esperada
- **AND** se declara que ninguna de las dos magnitudes es una probabilidad de acierto

#### Scenario: Confianza no comparable entre etapas

- **WHEN** se leen el eje human-in-the-loop de `02-marco-teorico.tex` y el subsistema de clasificacion de `05-arquitectura.tex`
- **THEN** la confianza de la etapa Gemini se denomina autodeclarada por el modelo
- **AND** se declara que la confianza deterministica no se compara con el umbral de revision

#### Scenario: Sin certeza atribuida al filtro

- **WHEN** se busca en `sections/*.tex` una atribucion de "alta certeza" o "alta confianza" a la decision del filtro deterministico
- **THEN** no aparece ninguna

### Requirement: Alcance del gate de revision humana declarado por etapa

La tesis SHALL declarar que la regla `requiere_revision_humana = (confianza < 0,70)` se evalua solo sobre la salida de la etapa Gemini, que la etapa de reserva deriva siempre a revision con confianza 0,0 y que la etapa deterministica no deriva a revision por su confianza. La descripcion del flujo en `06-implementacion.tex` SHALL enumerar las condiciones con que el backend activa el indicador de revision humana, incluida la derivacion por reportante no identificado en el directorio de empleados. Ningun capitulo MUST afirmar que el umbral de 0,70 alcanza a todos los casos ni que es el unico disparador automatico de revision humana.

#### Scenario: Grado de autonomia acotado por etapa en el marco teorico

- **WHEN** se lee `subsec:human-in-the-loop` en `02-marco-teorico.tex`
- **THEN** el grado adoptado por el sistema se describe como revision selectiva acotada por etapa
- **AND** no se afirma que todo caso con confianza inferior a 0,70 escala a revision humana

#### Scenario: Disparadores enumerados en la implementacion

- **WHEN** se lee la etapa de evaluacion del flujo en `06-implementacion.tex`
- **THEN** se enumeran la confianza de Gemini inferior a 0,70, la intervencion de la etapa de reserva y el reportante no identificado como condiciones del indicador
- **AND** no aparece la afirmacion de que el umbral de 0,70 es el unico disparador automatico de revision humana

#### Scenario: Coherencia entre capitulos

- **WHEN** se recorren las menciones al umbral de 0,70 en `02`, `05`, `06`, `07`, `08`, `11` y `12`
- **THEN** ninguna aplica el umbral a la etapa deterministica
- **AND** ninguna describe la cola de revision como destinada a los "casos de baja confianza" sin calificar

### Requirement: Criterio de cortocircuito y procedencia del punto de operacion

La tesis SHALL describir el cortocircuito de la etapa deterministica por su criterio vigente: senal dominante, sin ausencia de coincidencias ni empate, y puntaje de correctitud mayor o igual al punto de operacion 0,5166. La tesis SHALL declarar la procedencia del punto de operacion (validacion cruzada de cinco pliegues sobre el corpus con un piso comparativo: precision del filtro no inferior a la de la etapa Gemini sobre el conjunto que resuelve, 0,7405 frente a 0,6769), su equivalencia en el corpus (resolver los 131 casos con senal dominante) y el retiro del umbral de 0,90 sobre la confianza del diseno inicial. La tesis MUST NOT afirmar que el filtro decide cuando su confianza supera el 90 % y MUST NOT presentar el piso comparativo como garantia independiente de exactitud.

#### Scenario: Criterio vigente descrito

- **WHEN** se lee `subsec:subsistema-clasificacion` y la tabla `tab:capas`
- **THEN** el cortocircuito se describe por la senal dominante y el punto de operacion 0,5166 del puntaje de correctitud
- **AND** no aparece "superior al 90" ni "umbral de confianza preestablecido" como criterio de cortocircuito

#### Scenario: Procedencia y equivalencia declaradas

- **WHEN** se lee la descripcion del punto de operacion
- **THEN** se declara su derivacion por validacion cruzada de cinco pliegues sobre el corpus con el piso comparativo frente a Gemini
- **AND** se declara que en el corpus equivale a resolver los 131 casos con senal dominante

#### Scenario: Valores tomados del memo canonico

- **WHEN** se cotejan 0,5166, 0,7405, 0,6769 y 131 con `docs/Tesis/Correcciones/numeros-canonicos.md`
- **THEN** cada valor figura como `vigente` con su procedencia

### Requirement: Casos bajo el umbral no escalados consignados en resultados

La subseccion de intervencion humana del capitulo de resultados (`subsec:reduccion-intervencion`) SHALL consignar que 124 de los 200 casos (62 %) tuvieron una confianza registrada inferior a 0,70 sin ser escalados, que todos pertenecen a la etapa deterministica y que su confianza mide fuerza de senal y no se compara con el umbral; que los 69 casos de la etapa Gemini declararon siempre una confianza de al menos 0,85; que la etapa de reserva no se activo; y que sobre el 65,5 % de los casos no existio derivacion automatica por caso basada en la clasificacion. La subseccion MUST conservar su rotulo y MUST NOT introducir valores ausentes del memo canonico.

#### Scenario: Cifra de casos no escalados consignada

- **WHEN** se lee `subsec:reduccion-intervencion` en el PDF compilado
- **THEN** aparecen los 124 de 200 casos (62 %) con confianza inferior a 0,70 sin escalamiento
- **AND** se los atribuye a la etapa deterministica con la causa por la que no se comparan con el umbral

#### Scenario: Etapas Gemini y de reserva descritas

- **WHEN** se lee la misma subseccion
- **THEN** se declara que los 69 casos de la etapa Gemini declararon siempre una confianza de al menos 0,85
- **AND** se declara que la etapa de reserva no se activo

#### Scenario: Rotulo de la subseccion preservado

- **WHEN** se inspecciona `07-resultados.tex`
- **THEN** existe `\label{subsec:reduccion-intervencion}`
- **AND** las referencias cruzadas a esa subseccion resuelven sin advertencias

### Requirement: Alcance real de la salvaguarda de supervision humana en el capitulo legal

El capitulo de consideraciones eticas y legales (`11-aspectos-legales.tex`, subseccion `subsec:consentimiento-derechos`) SHALL declarar que el umbral de 0,70 solo alcanza a la etapa semantica y a la de reserva; que sobre el 65,5 % de los casos, resueltos por la etapa deterministica, no existe derivacion automatica por caso basada en la clasificacion; y que para esa fraccion la salvaguarda se limita al criterio de diseno con que se fijo el punto de operacion, estimado sobre el corpus de validacion, y a la reasignacion trazable del incidente, con la salvedad de su exposicion en la interfaz web. El capitulo MUST NOT presentar el umbral de 0,70 como salvaguarda de todos los casos ni el criterio comparativo como garantia independiente, y SHALL remitir la capacidad discriminante de la confianza del modelo al analisis de calibracion sin afirmar su resultado.

#### Scenario: Alcance de la salvaguarda declarado

- **WHEN** se lee la subseccion de supervision humana del capitulo legal
- **THEN** se declara que el umbral de 0,70 solo alcanza a la etapa semantica y a la de reserva
- **AND** se declara que sobre el 65,5 % de los casos no existe derivacion automatica por caso basada en la clasificacion

#### Scenario: Mitigaciones sin sobreafirmar

- **WHEN** se leen las mitigaciones declaradas para la etapa deterministica
- **THEN** el criterio de diseno del punto de operacion se califica como estimado sobre el corpus de validacion
- **AND** la reasignacion trazable se acompana de la salvedad sobre su exposicion en la interfaz web

#### Scenario: Remision a la calibracion

- **WHEN** se lee la oracion sobre la capacidad discriminante de la confianza
- **THEN** remite a `subsec:calibracion`
- **AND** no afirma por si misma una conclusion de calibracion

### Requirement: Procedencia declarada de los ajustes realizados sobre el corpus de validacion

La tesis SHALL declarar en la discusion (`subsec:interpretacion-resultados`) que las reglas de frontera del prompt y la ampliacion del vocabulario del filtro deterministico de la version evaluada se incorporaron a partir de errores observados en el corpus de validacion, y que el punto de operacion del cortocircuito se derivo por validacion cruzada sobre ese corpus; y SHALL calificar las metricas de clasificacion reportadas como estimaciones dentro de la muestra cuya confirmacion exige un corpus independiente. Las demas secciones que afirman la ausencia de exposicion al corpus (`05-arquitectura.tex`, `06-implementacion.tex`, Anexo H) SHALL alinearse con esa declaracion o remitir a ella. La tesis MUST NOT afirmar separacion estricta entre datos de construccion y de validacion, ausencia de exposicion al corpus ni desempeno sobre datos no vistos mientras el repositorio registre esos ajustes, y MUST NOT alterar ningun valor numerico por esta declaracion.

#### Scenario: Sin afirmacion de no exposicion

- **WHEN** se buscan en `sections/*.tex` las afirmaciones "sin exposición a" (el corpus o los 200 casos de validacion), "sin acceso al corpus", "datos no vistos" y "separación estricta"
- **THEN** ninguna aparece como afirmacion vigente sobre la version evaluada

#### Scenario: Procedencia declarada en la discusion

- **WHEN** se lee `subsec:interpretacion-resultados`
- **THEN** se declaran los ajustes del prompt, del vocabulario y del punto de operacion realizados sobre el corpus
- **AND** las metricas de clasificacion se califican como estimaciones dentro de la muestra

#### Scenario: Numeros intactos

- **WHEN** se comparan las metricas de clasificacion del PDF antes y despues de la declaracion
- **THEN** no cambia ningun valor numerico

### Requirement: Umbral de revision humana en la especificacion del Anexo H

La tabla de parametros de configuracion del Anexo H (`tab:anexo_gemini_params`) SHALL incluir el umbral de revision humana (0,70) y declarar su alcance: se aplica a la confianza de la respuesta del modelo y no a la etapa deterministica. La fila MUST NOT desbordar la primera columna de la tabla.

#### Scenario: Fila del umbral presente

- **WHEN** se lee `tab:anexo_gemini_params` en el PDF compilado
- **THEN** existe una fila del umbral de revision humana con valor 0,70
- **AND** su justificacion declara que no se aplica a la etapa deterministica

#### Scenario: Sin desborde

- **WHEN** se revisa el registro de compilacion
- **THEN** no hay advertencias `Overfull \hbox` atribuibles a la fila agregada

## MODIFIED Requirements

### Requirement: Hallazgo del gate de clasificacion presentado como resultado propio

La tesis SHALL presentar la conducta observada del gate de clasificacion en el corpus como un hallazgo empirico con valor propio sobre el comportamiento del clasificador en el dominio evaluado, ademas de su uso como justificacion de la sub-hipotesis no contrastada: la etapa Gemini nunca devolvio una confianza inferior a 0,85 en los 69 casos que resolvio, de modo que el gate de revision, que solo alcanza a esa etapa y a la de reserva, no derivo ningun caso; los 131 casos de la etapa deterministica no estan sujetos al gate. El hallazgo SHALL enunciarse en el capitulo de discusion y/o en la subseccion de intervencion humana de resultados (`subsec:reduccion-intervencion`), MUST NOT atribuirse a los 200 casos del corpus y MUST NOT introducir valores numericos distintos de los ya canonicos. La valoracion del hallazgo (fiabilidad o sobreconfianza del modelo) SHALL ser coherente con el analisis de calibracion por etapa.

#### Scenario: Hallazgo enunciado con su alcance correcto

- **WHEN** se lee el capitulo de discusion y/o la subseccion de intervencion humana de resultados
- **THEN** se declara que la etapa Gemini nunca devolvio una confianza inferior a 0,85 en los 69 casos que resolvio
- **AND** no se afirma que esa conducta abarque los 200 casos del corpus

#### Scenario: Hallazgo enunciado como resultado positivo

- **WHEN** se lee la enunciacion del hallazgo
- **THEN** se presenta como resultado empirico propio sobre el clasificador y no solo como motivo de la no contraste de la sub-hipotesis
- **AND** su valoracion no contradice la conclusion del analisis de calibracion por etapa

#### Scenario: Sin numeros nuevos

- **WHEN** se revisa el texto agregado para el hallazgo del gate
- **THEN** no aparece ningun valor numerico que no figure ya en `docs/Tesis/Correcciones/numeros-canonicos.md`
- **AND** el umbral 0,85 y el umbral 0,70 del gate se citan con el mismo valor y sentido que en el resto del documento
