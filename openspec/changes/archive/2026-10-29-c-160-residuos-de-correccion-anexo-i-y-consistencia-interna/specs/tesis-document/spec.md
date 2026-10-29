## ADDED Requirements

### Requirement: Cuerpo de la tesis sin residuos del proceso de correccion del manuscrito

Las secciones del cuerpo de la tesis (`docs/Tesis/v10 (IA)/paper/sections/00-*.tex` a `11-*.tex`) SHALL describir el estudio y el sistema en su estado vigente y MUST NOT narrar la historia de revision del manuscrito: cifras previas retiradas, estimaciones de versiones anteriores del texto, formulaciones anteriores de hipotesis, umbrales o ramas del diseno retirados presentados como antecedente, ni afirmaciones sobre la estabilidad de los valores del registro canonico. En particular, el cuerpo MUST NOT contener la nota sobre la "cifra previa de 180 horas-persona" (9.1), la estimacion "entre veinte y treinta veces superior" al precio de lista (9.4), la oracion sobre el reemplazo del umbral de 0,90 del diseno inicial (5.5), la frase de que la rama de clasificacion basada en LangChain "fue retirada" (6.3), la narracion de la formulacion original de la segunda sub-hipotesis (1.4), la frase "Ningún valor canónico cambia" (8.5) ni la afirmacion de que la cobertura real del gate es menor que la que sugiere la proporcion de casos escalados (9.1). Cada texto retirado SHALL conservarse literal, con su ubicacion previa, en `docs/Tesis/Correcciones/dictamen-correcciones.md`; los que documentan decisiones de diseno del sistema (c-72, c-74 y c-82) SHALL figurar ademas en el parrafo de decisiones del Anexo I. La descripcion de la configuracion vigente en cada corrida de la campana (procedencia de los datos en 4.5 y tabla de configuracion evaluada frente a entregada), incluidos el cortocircuito por confianza de la version `hybrid-v1` y el agente LLM de N8N de la clasificacion telefonica previa a c-72, describe el estudio y no constituye un residuo en el sentido de este requisito. La discusion del gate en 9.1 SHALL declarar que en el corpus la regla de 0,70 no derivo ningun caso, porque los 124 casos con confianza registrada inferior a 0,70 pertenecen a la etapa deterministica, a la que la regla no se aplica, y la etapa Gemini nunca declaro una confianza inferior a 0,85. Las correcciones MUST NOT cambiar ningun valor numerico.

#### Scenario: Residuos ausentes del cuerpo

- **WHEN** se buscan con `grep` en `docs/Tesis/v10 (IA)/paper/sections/0*.tex`, `10-recomendaciones.tex` y `11-aspectos-legales.tex` las cadenas "180 horas-persona", "veinte y treinta veces", "Sustituyó al umbral de 0,90", "LangChain fue retirada", "formulación original", "no era contrastable", "Ningún valor canónico" y "cobertura real"
- **THEN** cada busqueda devuelve cero coincidencias
- **AND** `05-arquitectura.tex` no contiene "umbral de 0,90" y `06-implementacion.tex` no contiene "LangChain"

#### Scenario: Calculos y argumentos conservados

- **WHEN** se leen la nota de 9.1, la nota de costo de 9.4, el criterio de cortocircuito de 5.5 y el parrafo de sensibilidad de 8.5
- **THEN** se conservan el calculo de 32,2 horas-persona brutas, el calculo de aproximadamente 7 x 10^-4 USD por invocacion, el criterio vigente de cortocircuito con su punto de operacion y la oracion "El análisis estima la sensibilidad de las métricas y no sustituye la medición del sistema evaluado"
- **AND** ningun valor numerico difiere del registrado en `docs/Tesis/Correcciones/numeros-canonicos.md`

#### Scenario: Gate sin derivaciones descrito sin proporcion de escalados

- **WHEN** se lee el parrafo de 9.1 sobre la intervencion humana por gate
- **THEN** declara que la regla de 0,70 no derivo ningun caso del corpus y su causa por etapa
- **AND** no compara la cobertura del gate con una proporcion de casos escalados

#### Scenario: Residuos trasladados al registro

- **WHEN** se lee la seccion del dictamen del 2026-10-28 de c-160 en `docs/Tesis/Correcciones/dictamen-correcciones.md`
- **THEN** figuran los siete textos retirados, literales, con su archivo y linea previos y su destino
- **AND** el parrafo de decisiones del Anexo I menciona c-72, c-74 y c-82

### Requirement: Naturaleza de los dictamenes declarada en el Anexo I

El primer parrafo del Anexo I (`12-anexos.tex`, `sec:anexo-trazabilidad`) SHALL explicar la naturaleza de los dictamenes cuyas correcciones traza: que son revisiones evaluativas previas a la defensa, solicitadas por los autores; el instrumento con que se elaboraron, tal como consta en el repositorio (perfil de evaluador con criterios de la CONEAU versionado en `docs/Tesis/Correcciones/Prompt2.docx` y su modo de aplicacion); la serie y sus fechas (del 20 al 28 de octubre de 2026) y los dictamenes que el anexo traza (22 de octubre, sobre `v1.1.0`, y 28 de octubre, sobre `v1.2.5`); su alcance segun consta en cada dictamen; su caracter no vinculante; y su ubicacion en `auditorias/` junto con la ruta del registro `docs/Tesis/Correcciones/dictamen-correcciones.md`. El parrafo MUST NOT atribuir los dictamenes al jurado, a la direccion, a la catedra ni a la CONEAU, ni presentarlos como revision por pares humana si el repositorio no lo respalda. La decision de conservar el Anexo I en el PDF, con su extension medida en paginas, SHALL registrarse en el registro de correcciones.

#### Scenario: Naturaleza explicada al inicio

- **WHEN** se lee el primer parrafo del Anexo I en el PDF compilado
- **THEN** declara que los dictamenes son revisiones previas a la defensa, solicitadas por los autores, no vinculantes, y nombra el instrumento y su ubicacion en el repositorio
- **AND** identifica los dictamenes del 22 y del 28 de octubre de 2026 con la version examinada por cada uno

#### Scenario: Sin atribucion indebida

- **WHEN** se busca en el Anexo I la atribucion de los dictamenes a un jurado, a la direccion, a la catedra o a la CONEAU
- **THEN** no aparece ninguna

#### Scenario: Conservacion documentada

- **WHEN** se lee la seccion de c-160 del registro de correcciones
- **THEN** figura la decision de conservar el Anexo I con su extension medida en paginas y las alternativas evaluadas

### Requirement: Punteros exactos y residuos registrados del dictamen del 22 de octubre en el Anexo I

La tabla del dictamen del 22 de octubre de 2026 en el Anexo I (`tab:anexo-trazabilidad`) SHALL remitir, para cada recomendacion, a secciones o tablas que contengan efectivamente lo atendido y SHALL nombrar todos los changes que la atendieron. En particular: B6 SHALL remitir a una seccion o tabla que contenga el macro-F1 de umbral (0,6508) y no a la tabla de metricas por clase (`tab:metricas`); B8 SHALL remitir a la seccion donde se define la exactitud laxa (`subsec:analisis-estadistico`) y no a `subsec:metricas-instrumentos`; B12 SHALL incluir `subsec:amenazas-validez`; B10 SHALL incluir `c-146`; y A5 SHALL incluir `c-154`. Las filas A1, B4, B9, B14 y B16 SHALL registrar sus residuos verificados, cada uno con una remision a la fila del dictamen del 28 de octubre que lo atiende o con la declaracion de que queda pendiente. El anexo MUST NOT contener numeros de linea de las fuentes.

#### Scenario: Punteros corregidos

- **WHEN** se leen las filas A5, B6, B8, B10 y B12 de `tab:anexo-trazabilidad` en las fuentes
- **THEN** B6 no remite a `tab:metricas` y remite a una ubicacion que contiene 0,6508
- **AND** B8 remite a `subsec:analisis-estadistico`, B12 incluye `subsec:amenazas-validez`, B10 incluye `c-146` y A5 incluye `c-154`

#### Scenario: Residuos registrados

- **WHEN** se leen las filas A1, B4, B9, B14 y B16 del dictamen del 22 de octubre
- **THEN** cada una registra su residuo y quien lo atiende o su estado pendiente
- **AND** ninguna remite a un numero de linea de las fuentes

### Requirement: Estructura comun del Anexo I para los dictamenes del 22 y del 28 de octubre

El Anexo I SHALL organizarse, en este orden, en: el parrafo de naturaleza de los dictamenes; la tabla del dictamen del 22 de octubre de 2026 con su parrafo introductorio; una tabla del dictamen del 28 de octubre de 2026, con las mismas tres columnas (recomendacion, change y secciones de la tesis), que reuna las filas A1 a A4 atendidas por c-158 y c-159 y las filas B5 a B8 atendidas por c-160; y un parrafo de decisiones de diseno con su trazabilidad a los changes (c-72, c-74 y c-82). Las filas de ambos dictamenes MUST NOT mezclarse en una misma tabla, porque sus rotulos de recomendacion no son equivalentes. Las referencias a secciones SHALL hacerse con `\autoref` o `\ref` y la remision a la seccion de implementacion SHALL usar `\autoref{sec:implementacion}` en lugar de un numero de capitulo fijo. Las etiquetas `sec:anexo-trazabilidad` y `tab:anexo-trazabilidad` SHALL conservarse.

#### Scenario: Orden y separacion por dictamen

- **WHEN** se lee el Anexo I en el PDF compilado
- **THEN** aparecen, en orden, el parrafo de naturaleza, la tabla del 22 de octubre, la tabla del 28 de octubre y el parrafo de decisiones de diseno
- **AND** ninguna tabla mezcla recomendaciones de los dos dictamenes

#### Scenario: Filas B5 a B8 del dictamen del 28 de octubre

- **WHEN** se leen las filas B5, B6, B7 y B8 de la tabla del 28 de octubre
- **THEN** cada una nombra a c-160 y las secciones de la tesis donde se atendio
- **AND** las filas A1 a A4 agregadas por c-158 y c-159 siguen presentes y con el mismo formato

#### Scenario: Remisiones sin numeros fijos

- **WHEN** se busca "Capítulo~6" en `12-anexos.tex`
- **THEN** no aparece
- **AND** el parrafo de decisiones remite a la seccion de implementacion con `\autoref{sec:implementacion}`

### Requirement: Calificacion dentro de la muestra de las metricas de clasificacion en el resumen y el abstract

El resumen en espanol y el abstract (`00-resumen.tex`) SHALL calificar la exactitud estricta (73,5 %) y el macro-F1 de umbral (0,6508) como estimaciones dentro de la muestra, sin cambiar ninguna cifra. El resumen en espanol SHALL conservar como maximo 250 palabras de prosa segun la regla de c-106 (comandos LaTeX excluidos, matematica en linea como una palabra, `~` como separador salvo antes de un digito, linea de palabras clave excluida) y SHALL conservar las cifras clave exigidas por el requisito de presupuesto de palabras del resumen. El abstract SHALL conservar como maximo 250 palabras con la misma regla.

#### Scenario: Calificacion presente en ambos idiomas

- **WHEN** se leen el resumen y el abstract
- **THEN** la exactitud estricta y el macro-F1 de umbral figuran calificados como estimaciones dentro de la muestra ("dentro de la muestra" en espanol; "in-sample" en ingles)
- **AND** las cifras 73,5 %, 0,6508, 61,6 s, 17,76 s, 71,2 %, W = 363 y r = 0,9639 no cambian

#### Scenario: Presupuesto de palabras respetado

- **WHEN** se cuentan las palabras de prosa con la regla de c-106 antes y despues de la edicion
- **THEN** el resumen en espanol no supera 250 palabras ni el conteo de la linea base medido con la misma herramienta
- **AND** el abstract no supera 250 palabras

### Requirement: Remisiones internas exactas de la vision general, del analisis de sensibilidad y del anexo de documentacion operativa

La vision general de la arquitectura (`05-arquitectura.tex`, `subsec:vision-general`) SHALL remitir a los resultados mediante `\autoref{sec:resultados}` y MUST NOT citar un numero de capitulo fijo; su remision a la prueba de humo SHALL apuntar a la seccion que la describe (`subsec:pruebas-automatizadas`), al anexo de documentacion operativa (`sec:anexo-documentacion-operativa`) y al anexo del despliegue (`sec:anexo-diagrama-arquitectura`), y MUST NOT remitir al anexo del repositorio (`sec:anexo-repositorio`), que no la documenta. El anexo de documentacion operativa SHALL nombrar el runbook de la prueba de humo y de la verificacion del borde TLS (`docs/runbook-smoke-stack-referencia.md`). La subseccion de sensibilidad (`07-resultados.tex`, `subsec:sensibilidad-ajustes`) SHALL citar para el nivel a (48 de 66) la linea de `evaluation/report_sensibilidad_ajustes.md` que lo contiene.

#### Scenario: Vision general sin numero de capitulo ni anexo equivocado

- **WHEN** se lee `subsec:vision-general` en las fuentes
- **THEN** no aparecen "Capítulo 7" ni la remision de la prueba de humo al Anexo B
- **AND** la remision usa `\autoref{sec:resultados}`, `subsec:pruebas-automatizadas` y los Anexos A y G

#### Scenario: Runbook de humo nombrado en el Anexo G

- **WHEN** se lee `sec:anexo-documentacion-operativa`
- **THEN** nombra `docs/runbook-smoke-stack-referencia.md`
- **AND** ese archivo existe en el repositorio

#### Scenario: Linea del reporte verificable

- **WHEN** se lee la linea citada para el nivel a en `subsec:sensibilidad-ajustes` y se ejecuta `sed -n '<linea>p' evaluation/report_sensibilidad_ajustes.md`
- **THEN** la linea obtenida contiene "sin los motivadores 48/66"

### Requirement: Registro de la trazabilidad de las recomendaciones B5 a B8 del dictamen del 28 de octubre

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL contener una seccion "## Dictamen v10 / v1.2.5 (2026-10-28) - c-160" con: el origen, la fecha y el commit base; una matriz de una fila por parte de las recomendaciones B5 a B8 con las columnas de la matriz de la FASE 36 (recomendacion, sintesis, change, `archivo:linea`, `\label` ancla, fragmento verificable y estado), con lineas validas en el arbol al cierre del change; la tabla de los residuos trasladados desde el cuerpo, con su texto literal, su ubicacion previa y su destino; las decisiones del change, incluida la del Anexo I con su conteo de paginas; y la compilacion, las paginas y las palabras del resumen. El libro mayor de paginas SHALL recibir la fila de c-160. El registro MUST NOT contener emojis y su prosa nueva MUST NOT reproducir el patron que el escaneo de secretos marca como falso positivo (la palabra "capitulo" sin tilde seguida de coma o dos puntos y un nombre de archivo).

#### Scenario: Matriz verificable

- **WHEN** para cada fila de la matriz se ejecuta `sed -n '<linea>p' <archivo>` sobre el arbol al cierre de c-160
- **THEN** la linea contiene el fragmento verificable registrado
- **AND** el `\label` ancla existe en el mismo archivo

#### Scenario: Residuos y decisiones registrados

- **WHEN** se lee la seccion de c-160
- **THEN** figuran los siete residuos retirados con su texto literal y su destino
- **AND** figuran la decision sobre el Anexo I con su extension medida, la formulacion canonica del gate, el tratamiento del disparador por directorio y la forma de la comparacion de 5.5

#### Scenario: Libro mayor actualizado

- **WHEN** se lee el libro mayor de paginas
- **THEN** existe la fila de c-160 con total, cuerpo sin anexos, anexos, deltas y el exceso frente al tope de 100 paginas declarado

### Requirement: Verificacion de compilacion, render y citas al cierre de c-160

Al cierre de c-160, el render `docs/Tesis/v10 (IA)/tesis_para_agente.md` SHALL regenerarse desde las fuentes con `build_tesis_para_agente.py` y no quedar vacio; el PDF SHALL recompilarse en el entorno Docker de registro (`texlive-thesis`, `latexmk main.tex`) con codigo de salida 0, cero errores (`grep -c "^!" main.log` = 0), cero referencias indefinidas, cero etiquetas definidas mas de una vez, cero `??` en el texto extraido del PDF y una cantidad de avisos `Overfull \hbox` no mayor que la de la linea base medida antes de las ediciones; y `verify_citations.py` SHALL emitir PASS. El total de paginas SHALL medirse y registrarse conforme al requisito de presupuesto de paginas.

#### Scenario: Compilacion limpia

- **WHEN** se compila `main.tex` con Docker al cierre del change
- **THEN** el codigo de salida es 0, `grep -c "^!" main.log` es 0 y no hay referencias indefinidas ni etiquetas multiplemente definidas
- **AND** `pdftotext` del PDF no contiene `??` y los avisos `Overfull \hbox` no superan la linea base

#### Scenario: Render y citas

- **WHEN** se regenera el render y se ejecuta `python "docs/Tesis/v10 (IA)/verify_citations.py"`
- **THEN** el render no esta vacio y refleja las ediciones del change
- **AND** el verificador de citas emite PASS

## MODIFIED Requirements

### Requirement: Criterio de cortocircuito y procedencia del punto de operacion

La tesis SHALL describir el cortocircuito de la etapa deterministica por su criterio vigente: senal dominante, sin ausencia de coincidencias ni empate, y puntaje de correctitud mayor o igual al punto de operacion 0,5166. La tesis SHALL declarar la procedencia del punto de operacion (validacion cruzada de cinco pliegues sobre el corpus con un piso comparativo: precision del filtro no inferior a la de la etapa Gemini sobre el conjunto que resuelve, expresada sobre los mismos casos, 96/130 = 0,7385 frente a 88/130 = 0,6769 en los 130 casos con prediccion de ambas etapas, calificada como estimacion dentro de la muestra) y su equivalencia en el corpus (resolver los 131 casos con senal dominante). La comparacion MUST NOT mezclar denominadores distintos (por ejemplo, 97/131 frente a 88/130). La descripcion del subsistema de clasificacion (`subsec:subsistema-clasificacion`) MUST NOT narrar el reemplazo del umbral de 0,90 sobre la confianza del diseno inicial; esa decision de diseno SHALL constar en el parrafo de decisiones del Anexo I (c-74) y en el registro de correcciones, y la configuracion de las corridas que aun usaban ese umbral (version `hybrid-v1`) se declara en la procedencia de los datos y en la tabla de configuracion evaluada frente a entregada. La tesis MUST NOT afirmar que el filtro de la configuracion entregada o de la corrida de clasificacion (`hybrid-v3`) decide cuando su confianza supera el 90 % y MUST NOT presentar el piso comparativo como garantia independiente de exactitud.

#### Scenario: Criterio vigente descrito

- **WHEN** se lee `subsec:subsistema-clasificacion` y la tabla `tab:capas`
- **THEN** el cortocircuito se describe por la senal dominante y el punto de operacion 0,5166 del puntaje de correctitud
- **AND** no aparece "superior al 90" ni "umbral de confianza preestablecido" como criterio de cortocircuito

#### Scenario: Procedencia y equivalencia declaradas

- **WHEN** se lee la descripcion del punto de operacion
- **THEN** se declara su derivacion por validacion cruzada de cinco pliegues sobre el corpus con el piso comparativo frente a Gemini, expresado sobre los mismos 130 casos
- **AND** se declara que en el corpus equivale a resolver los 131 casos con senal dominante

#### Scenario: Valores tomados del memo canonico

- **WHEN** se cotejan 0,5166, 0,7385 (96/130), 0,6769 (88/130) y 131 con `docs/Tesis/Correcciones/numeros-canonicos.md`
- **THEN** cada valor figura como `vigente` con su procedencia

#### Scenario: Umbral retirado fuera de la descripcion del subsistema

- **WHEN** se busca "umbral de 0,90" en `05-arquitectura.tex` y "Sustituyó al umbral de 0,90" en las secciones `00-*.tex` a `11-*.tex`
- **THEN** ninguna busqueda devuelve coincidencias
- **AND** el parrafo de decisiones del Anexo I atribuye a c-74 el reemplazo del umbral de 0,90 por el punto de operacion del puntaje de correctitud

### Requirement: Segunda sub-hipotesis con fraccion esperada explicita

La segunda sub-hipotesis (`01-introduccion.tex`, `subsec:hipotesis-trabajo`) SHALL enunciarse con una fraccion esperada numerica explicita, derivada de un criterio fijado a priori en el propio documento (en esta version, una proporcion de casos con accion manual de un operador no superior a `0,15`, complemento del umbral de exactitud del 85 %), junto con su contraste (proporcion con intervalo de confianza de Wilson) y su criterio de falsacion. El texto SHALL presentar la sub-hipotesis solo en su formulacion vigente y MUST NOT narrar formulaciones anteriores del manuscrito (por ejemplo, que una formulacion original referida al proceso manual no era contrastable); esa historia SHALL constar en el registro de correcciones. Mientras no exista registro primario de intervencion por caso, la sub-hipotesis SHALL declararse "no contrastada por ausencia de registro primario" en el resumen, la introduccion, los resultados y las conclusiones. El documento MUST NOT presentar las derivaciones del gate de revision (ninguna en el corpus) como contraste o confirmacion de esta sub-hipotesis y MUST NOT cuantificar la proporcion. Toda remision desde la sub-hipotesis SHALL apuntar a una seccion que declare la ausencia de registro primario; si remite a la lista de limitaciones del estudio (`subsec:limitaciones-estudio`), esa lista SHALL incluir la proporcion de intervencion humana no medida y su oracion introductoria SHALL declarar el numero real de limitaciones listadas.

#### Scenario: Fraccion esperada y criterio de falsacion explicitos

- **WHEN** se lee la segunda sub-hipotesis en `01-introduccion.tex`
- **THEN** declara la cota numerica, su derivacion del umbral fijado a priori, el contraste con intervalo de Wilson y el criterio de falsacion
- **AND** la cota figura en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Formulacion vigente sin narrar la anterior

- **WHEN** se lee la segunda sub-hipotesis
- **THEN** no aparecen "formulación original", "no era contrastable" ni "tampoco esta se contrasta"
- **AND** el registro de correcciones conserva literal el texto retirado con su ubicacion previa

#### Scenario: Formulacion original declarada no contrastable

- **WHEN** se busca en el cuerpo de la tesis la formulacion original de la segunda sub-hipotesis (comparacion con el proceso manual, donde la intervencion es total por definicion)
- **THEN** el cuerpo no la narra ni declara que no era contrastable
- **AND** esa formulacion original y su no contrastabilidad constan solo en el registro de correcciones y en el Anexo I

#### Scenario: Sin confirmacion espuria por el gate

- **WHEN** se leen la introduccion y la subseccion `subsec:reduccion-intervencion` de resultados
- **THEN** la ausencia de derivaciones del gate no se presenta como contraste ni como confirmacion de la sub-hipotesis
- **AND** el texto explica que esas derivaciones no operacionalizan la proporcion de casos con accion manual

#### Scenario: Estado propagado

- **WHEN** se busca el rotulo de la segunda sub-hipotesis en `00-resumen.tex`, `01-introduccion.tex`, `07-resultados.tex` y `09-conclusiones.tex`
- **THEN** en los cuatro aparece "no contrastada por ausencia de registro primario"
- **AND** ninguno informa una proporcion de intervencion humana como resultado

#### Scenario: Remision coherente con su destino

- **WHEN** se sigue la remision `\autoref` de la segunda sub-hipotesis en `01-introduccion.tex`
- **THEN** la seccion de destino declara que la proporcion de intervencion humana no se midio por ausencia de registro primario
- **AND** si el destino es `subsec:limitaciones-estudio`, la lista incluye esa limitacion y el conteo de su oracion introductoria coincide con el numero de limitaciones listadas

### Requirement: Alcance del gate de revision humana declarado por etapa

La tesis SHALL declarar que la regla `requiere_revision_humana = (confianza < 0,70)` se evalua solo sobre la salida de la etapa Gemini, que la etapa de reserva deriva siempre a revision con confianza 0,0 y que la etapa deterministica no deriva a revision por su confianza. Toda descripcion del alcance del gate en 2.4 (`02-marco-teorico.tex`), 5.5 (`05-arquitectura.tex`), 6.3 (`06-implementacion.tex`), 7.5 (`11-aspectos-legales.tex`), 8.3 (`07-resultados.tex`), 11.1 (`10-recomendaciones.tex`) y el Anexo H (`12-anexos.tex`) SHALL usar esa formulacion canonica y MUST NOT describir la regla de 0,70 como aplicable a la etapa Gemini y a la etapa de reserva. La descripcion del flujo en `06-implementacion.tex` SHALL enumerar las condiciones con que el backend activa el indicador de revision humana, incluida la derivacion por reportante no identificado en el directorio de empleados. Esa derivacion SHALL figurar en 2.4, 5.5, 6.3, 7.5 y el Anexo H con su fecha de incorporacion (13 de octubre de 2026) y la aclaracion de que es posterior a las corridas de la campana y no forma parte de la configuracion evaluada. Ningun capitulo MUST afirmar que el umbral de 0,70 alcanza a todos los casos ni que es el unico disparador automatico de revision humana.

#### Scenario: Grado de autonomia acotado por etapa en el marco teorico

- **WHEN** se lee `subsec:human-in-the-loop` en `02-marco-teorico.tex`
- **THEN** el grado adoptado por el sistema se describe como revision selectiva acotada por etapa
- **AND** no se afirma que todo caso con confianza inferior a 0,70 escala a revision humana

#### Scenario: Disparadores enumerados en la implementacion

- **WHEN** se lee la etapa de evaluacion del flujo en `06-implementacion.tex`
- **THEN** se enumeran la confianza de Gemini inferior a 0,70, la intervencion de la etapa de reserva y el reportante no identificado como condiciones del indicador
- **AND** el reportante no identificado figura con su fecha de incorporacion, posterior a la campana
- **AND** no aparece la afirmacion de que el umbral de 0,70 es el unico disparador automatico de revision humana

#### Scenario: Coherencia entre capitulos

- **WHEN** se recorren las menciones al umbral de 0,70 en `02`, `05`, `06`, `07`, `08`, `11` y `12`
- **THEN** ninguna aplica el umbral a la etapa deterministica
- **AND** ninguna describe la cola de revision como destinada a los "casos de baja confianza" sin calificar

#### Scenario: Formulacion canonica en todas las menciones

- **WHEN** se leen las descripciones del alcance del gate en 2.4, 5.5, 6.3, 7.5, 8.3, 11.1 y el Anexo H
- **THEN** todas declaran que la regla de 0,70 se evalua solo sobre la salida de Gemini y que la reserva deriva siempre
- **AND** `grep` de "y a la etapa de reserva", "Gemini y la etapa de reserva" y "y a la de reserva" sobre `02-marco-teorico.tex`, `05-arquitectura.tex`, `06-implementacion.tex`, `07-resultados.tex`, `10-recomendaciones.tex`, `11-aspectos-legales.tex` y `12-anexos.tex` devuelve cero coincidencias

#### Scenario: Disparador por directorio fechado

- **WHEN** se leen 2.4, 5.5, 6.3, 7.5 y la fila del umbral del Anexo H
- **THEN** cada una menciona la derivacion por reportante no identificado en el directorio con la fecha 13 de octubre de 2026
- **AND** declara que es posterior a las corridas de la campana

### Requirement: Alcance real de la salvaguarda de supervision humana en el capitulo legal

El capitulo de consideraciones eticas y legales (`11-aspectos-legales.tex`, subseccion `subsec:consentimiento-derechos`) SHALL declarar que la regla de 0,70 se evalua solo sobre la salida de la etapa semantica (Gemini), que la etapa de reserva deriva siempre a revision y que, desde el 13 de octubre de 2026, con posterioridad a la campana, tambien se deriva el incidente cuyo reportante no se identifica en el directorio de empleados; que sobre el 65,5 % de los casos, resueltos por la etapa deterministica, no existe derivacion automatica por caso basada en la clasificacion; y que para esa fraccion la salvaguarda se limita al criterio de diseno con que se fijo el punto de operacion, estimado sobre el corpus de validacion, y a la reasignacion trazable del incidente, con la salvedad de su exposicion en la interfaz web. El capitulo MUST NOT presentar el umbral de 0,70 como salvaguarda de todos los casos ni el criterio comparativo como garantia independiente, y SHALL remitir la capacidad discriminante de la confianza del modelo al analisis de calibracion sin afirmar su resultado.

#### Scenario: Alcance de la salvaguarda declarado

- **WHEN** se lee la subseccion de supervision humana del capitulo legal
- **THEN** se declara que la regla de 0,70 se evalua solo sobre la salida de la etapa semantica y que la etapa de reserva deriva siempre
- **AND** se declara que sobre el 65,5 % de los casos no existe derivacion automatica por caso basada en la clasificacion
- **AND** la derivacion por reportante no identificado figura con su fecha, posterior a la campana

#### Scenario: Mitigaciones sin sobreafirmar

- **WHEN** se leen las mitigaciones declaradas para la etapa deterministica
- **THEN** el criterio de diseno del punto de operacion se califica como estimado sobre el corpus de validacion
- **AND** la reasignacion trazable se acompana de la salvedad sobre su exposicion en la interfaz web

#### Scenario: Remision a la calibracion

- **WHEN** se lee la oracion sobre la capacidad discriminante de la confianza
- **THEN** remite a `subsec:calibracion`
- **AND** no afirma por si misma una conclusion de calibracion

### Requirement: Grados de cumplimiento de los objetivos acotados a la evidencia

La tabla `tab:cumplimiento-objetivos` de `09-conclusiones.tex` SHALL asignar a cada objetivo el grado "Alcanzado" solo cuando cada componente exigido por su enunciado literal en `01-introduccion.tex` este evidenciado en la version evaluada; "Alcanzado parcialmente" cuando al menos un componente este evidenciado y al menos otro no se cumpla o no se haya medido; y "No alcanzado" cuando no se cumpla el criterio del objetivo. Toda fila "Alcanzado parcialmente" SHALL nombrar en su evidencia el componente no cumplido o no medido. Los objetivos especificos 1, 3, 4 y 6 SHALL figurar como "Alcanzado parcialmente" mientras falte la evidencia de, respectivamente, la comunicacion asincronica (el alta sigue siendo sincronica, con reintentos idempotentes); la complejidad operativa percibida por los usuarios (la latencia y la exactitud por canal ya estan medidas); la exactitud del brazo manual y la proporcion de intervencion humana; y la recalibracion de la confianza, con el analisis de errores y las bandas de confianza estimados dentro de la muestra. La verificacion de TLS SHALL declararse igual en la celda del objetivo 1 y en la prosa de las conclusiones: realizada despues de la campana, sobre el despliegue de referencia de la version entregada, y no sobre la configuracion evaluada ni sobre la instancia operativa. El objetivo general SHALL desglosarse en sus tres componentes (tiempo de registro, calidad de la clasificacion y proporcion de intervencion humana) con estado individual, y su grado global SHALL ser coherente con ese desglose. El documento MUST NOT reformular el enunciado de un objetivo para ajustarlo a lo construido o medido, y la prosa de las conclusiones SHALL ser coherente con la tabla.

#### Scenario: Objetivos 1, 3 y 4 parcialmente alcanzados

- **WHEN** se leen las filas de los objetivos especificos 1, 3 y 4 en `tab:cumplimiento-objetivos`
- **THEN** cada una declara "Alcanzado parcialmente"
- **AND** su evidencia nombra el componente faltante: alta sincronica y TLS verificado solo despues de la campana en el despliegue de referencia (1); complejidad percibida no medida, con latencia y exactitud por canal medidas (3); exactitud del brazo manual e intervencion humana no medidas (4)

#### Scenario: Objetivo 6 parcialmente alcanzado

- **WHEN** se lee la fila del objetivo especifico 6 en `tab:cumplimiento-objetivos`
- **THEN** declara "Alcanzado parcialmente"
- **AND** su evidencia nombra el componente faltante: confianza no recalibrada y analisis estimado dentro de la muestra

#### Scenario: Objetivo general desglosado

- **WHEN** se lee la fila del objetivo general
- **THEN** figuran el tiempo de registro como alcanzado, la calidad de la clasificacion como evaluada por debajo del umbral y la intervencion humana como no medida
- **AND** el grado global es "Alcanzado parcialmente"

#### Scenario: Enunciados de objetivos sin reformular

- **WHEN** se comparan los enunciados del objetivo general y de los objetivos especificos en `01-introduccion.tex` con los de la version previa al change
- **THEN** los enunciados no cambian
- **AND** solo cambia su grado de cumplimiento en la tabla

#### Scenario: Reversion condicionada a evidencia

- **WHEN** se dispone de evidencia nueva para un componente faltante del objetivo 1, del objetivo 3 o del objetivo 6 y se propone elevar su grado
- **THEN** el grado solo pasa a "Alcanzado" si la tabla cita evidencia para cada componente faltante (comunicacion asincronica, ademas del TLS ya verificado despues de la campana, para el 1; calidad por canal sin evidencia de degradacion y decision del autor sobre la complejidad percibida para el 3; confianza recalibrada y evaluada fuera de la muestra para el 6)
- **AND** si la evidencia es posterior a la validacion experimental, la celda lo declara

#### Scenario: Objetivo 6 con evidencia ampliada

- **WHEN** se lee la fila del objetivo especifico 6
- **THEN** su grado es "Alcanzado parcialmente" y su evidencia cita el analisis de errores, la calibracion por etapa, el analisis de sensibilidad de los ajustes (`subsec:sensibilidad-ajustes`) y la linea futura de calibracion del gate (`subsec:calibracion-gate`)
- **AND** la celda nombra la recalibracion no realizada y la estimacion dentro de la muestra como componentes faltantes

#### Scenario: Prosa coherente con la tabla

- **WHEN** se leen los parrafos de las conclusiones que tratan el objetivo general y los objetivos 1, 3, 4 y 6
- **THEN** ninguno afirma un cumplimiento pleno que la tabla declare parcial
- **AND** la prosa sobre TLS coincide con la celda del objetivo 1 y la del objetivo 3 lo declara alcanzado parcialmente, sin "solo en su construcción"
- **AND** el primer parrafo declara cumplido parcialmente el objetivo general

### Requirement: Calificacion dentro de la muestra de la exactitud deterministica y del contraste entre etapas

Toda aparicion en `sections/*.tex` de la exactitud de la etapa deterministica (`97/131`, `0,7405`) y de la comparacion entre etapas sobre el conjunto cortocircuitable (`0,7385` frente a `0,6769`; `96/130`; `88/130`) SHALL figurar en una oracion o parrafo que la califique como estimacion dentro de la muestra o que remita a `subsec:sensibilidad-ajustes`. La cuantificacion del sesgo SHALL residir solo en `subsec:sensibilidad-ajustes`; los demas pasajes SHALL limitarse a calificar o remitir. Este requisito MUST NOT cambiar ningun valor numerico.

#### Scenario: Cada aparicion calificada

- **WHEN** se listan con `grep` las apariciones de `0,7405`, `97/131`, `97 de 131`, `0,7385`, `96/130`, `0,6769` y `88/130` en `sections/*.tex`
- **THEN** cada una esta en una oracion o parrafo que la califica como estimacion dentro de la muestra o que remite a `subsec:sensibilidad-ajustes`

#### Scenario: Cuantificacion en un unico lugar

- **WHEN** se buscan los valores del analisis de sensibilidad fuera de `subsec:sensibilidad-ajustes`
- **THEN** solo aparecen en la limitacion del capitulo de discusion, que remite a la subseccion
- **AND** ningun otro pasaje repite la tabla ni su lectura

#### Scenario: Valores sin cambio

- **WHEN** se comparan los valores numericos de la tesis antes y despues de agregar las calificaciones
- **THEN** no cambia ninguno
