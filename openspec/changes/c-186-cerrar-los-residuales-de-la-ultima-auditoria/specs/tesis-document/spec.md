## MODIFIED Requirements

### Requirement: Atribuciones del eje de modelos de lenguaje conformes al contenido de las fuentes

El eje de procesamiento de lenguaje natural y modelos de lenguaje grandes del marco teorico (seccion 2.4) y el estado del arte multilingue del capitulo 3 SHALL atribuir a cada fuente solo lo que esa fuente sostiene, contrastado con su texto completo cuando es de acceso abierto o con el resumen de la pagina del editor. El documento MUST NOT citar Xuan et al. (2025) como fuente de calibracion de la confianza, MUST NOT citar Lai et al. (2023) como evidencia de sensibilidad a la redaccion del prompt, MUST NOT citar Zhang et al. (2023) como evidencia de generalizacion fuera del ingles, y MUST NOT atribuir a Mayor-Rocher et al. (2026) ni a Grandury et al. (2025) diferencias de desempeno por dialecto que esas obras no reportan. La fundamentacion bibliografica de la calibracion SHALL provenir de fuentes que estudien la calibracion (incorporadas por c-138); hasta entonces el parrafo MUST NOT conservar una cita que no la trate. En la seccion 3.3, la afirmacion de que el rendimiento de CLASIFICACION depende del idioma SHALL apoyarse en un benchmark que incluya tareas de clasificacion (MEGA, `ahuja2023mega`); Xuan et al. (2025), cuyos resultados provienen de un benchmark de razonamiento de opcion multiple (MMLU-ProX), MUST NOT citarse como evidencia de clasificacion y SHALL citarse solo por la brecha de desempeno multilingue. El agrupamiento de citas de 3.3 SHALL separar la atribucion de clasificacion (MEGA) de la de rendimiento multilingue (Xuan et al.).

#### Scenario: Calibracion sin atribucion a un benchmark de rendimiento

- **WHEN** se lee el parrafo de la seccion 2.4 que define la calibracion de la confianza
- **THEN** el parrafo no cita `xuan2025mmluprox`
- **AND** ninguna fuente citada en ese parrafo es una obra que no trate la calibracion

#### Scenario: Xuan et al. citado por lo que sostiene

- **WHEN** se buscan todas las citas de `xuan2025mmluprox` en las secciones de la tesis
- **THEN** cada una le atribuye solo resultados de rendimiento multilingue (benchmark de 29 idiomas, caida del desempeno en los idiomas con menos recursos, resultados desagregados por idioma)
- **AND** ninguna le atribuye resultados sobre calibracion, confianza o incertidumbre

#### Scenario: Diseno del prompt respaldado por la fuente adecuada

- **WHEN** se lee el parrafo de la seccion 2.4 sobre el diseno del prompt
- **THEN** Lai et al. (2023) no se cita como evidencia de sensibilidad a la redaccion del prompt
- **AND** Ahuja et al. (2023) se cita solo por su comparacion de estrategias de prompting entre idiomas
- **AND** no se afirma un efecto del orden o de la seleccion de los ejemplos sin una fuente que lo estudie

#### Scenario: Idiomas, alternancia de codigo y variedades del espanol

- **WHEN** se leen las citas de Lai et al. (2023), Zhang et al. (2023), Grandury et al. (2025) y Mayor-Rocher et al. (2026)
- **THEN** Lai et al. se cita por el ajuste por instrucciones de modelos abiertos concentrado en el ingles y en pocos idiomas, Zhang et al. por el rendimiento ante textos con alternancia de codigo, Grandury et al. por su tabla de clasificacion de variedades del espanol y Mayor-Rocher et al. por su evaluacion con pruebas de espanol como lengua extranjera
- **AND** a ninguna se le atribuyen diferencias de desempeno atribuibles al dialecto que la obra no reporte

#### Scenario: Agrupamientos de citas coherentes

- **WHEN** se lee un comando de cita con varias claves en el estado del arte multilingue del capitulo 3
- **THEN** cada clave del agrupamiento sostiene la afirmacion a la que se adjunta
- **AND** Lai et al. y Zhang et al. no respaldan la afirmacion de que el rendimiento favorece a los idiomas con mas recursos

#### Scenario: Clasificacion acotada a MEGA en la seccion 3.3

- **WHEN** se lee la seccion 3.3 en busca de la afirmacion de que el rendimiento de clasificacion depende del idioma del corpus
- **THEN** la afirmacion de clasificacion se respalda con un benchmark que incluye tareas de clasificacion (MEGA, `ahuja2023mega`)
- **AND** `xuan2025mmluprox` no se cita como benchmark de clasificacion, solo por la brecha de desempeno multilingue

### Requirement: Punteros exactos y residuos registrados del dictamen del 22 de octubre en el Anexo I

La tabla del dictamen del 22 de octubre de 2026 en el Anexo I (`tab:anexo-trazabilidad`) SHALL remitir, para cada recomendacion, a secciones o tablas que contengan efectivamente lo atendido y SHALL nombrar todos los changes que la atendieron. En particular: B6 SHALL remitir a una seccion o tabla que contenga el macro-F1 de umbral (0,6508) y no a la tabla de metricas por clase (`tab:metricas`); B8 SHALL remitir a la seccion donde se define la exactitud laxa (`subsec:analisis-estadistico`) y no a `subsec:metricas-instrumentos`; B12 SHALL incluir `subsec:amenazas-validez`; B10 SHALL incluir `c-146`; y A5 SHALL incluir `c-154`. Las filas A1, B4, B9, B14 y B16 SHALL registrar el estado vigente de sus residuos: cada una SHALL consignar los changes posteriores que los cerraron o, cuando el residuo subsista como limitacion declarada, SHALL enunciarlo como limitacion y no como pendiente abierto. En particular, B14 SHALL declarar cerradas las erratas de figuras y el `seudonimizado` (c-159 y c-163); B16 SHALL declarar cerrada la fecha de consulta de una referencia (c-163); y B9 SHALL declarar la no recuperabilidad de las fechas de las iteraciones Scrumban como limitacion explicita, coherente con `06-implementacion.tex` y `docs/diagrams/cronograma.md`. Ninguna fila MUST conservar la palabra "pendiente" para un residuo ya cerrado o ya declarado como limitacion. El anexo MUST NOT contener numeros de linea de las fuentes.

#### Scenario: Punteros corregidos

- **WHEN** se leen las filas A5, B6, B8, B10 y B12 de `tab:anexo-trazabilidad` en las fuentes
- **THEN** B6 no remite a `tab:metricas` y remite a una ubicacion que contiene 0,6508
- **AND** B8 remite a `subsec:analisis-estadistico`, B12 incluye `subsec:amenazas-validez`, B10 incluye `c-146` y A5 incluye `c-154`

#### Scenario: Residuos registrados

- **WHEN** se leen las filas A1, B4, B9, B14 y B16 del dictamen del 22 de octubre
- **THEN** B14 y B16 no dicen "pendiente" para las erratas de figuras, el `seudonimizado` ni la fecha de consulta de una referencia, ya cerrados por c-159 y c-163
- **AND** B9 declara la no recuperabilidad de las fechas de las iteraciones como limitacion explicita, coherente con `06-implementacion.tex` y `docs/diagrams/cronograma.md`, y no como pendiente
- **AND** ninguna fila remite a un numero de linea de las fuentes

### Requirement: Cierre de los items (a) a (e) del dictamen v1.2.5 con propagacion verificable

Al aplicar este change, cada item (a) exactitud del brazo manual, (b) intervencion
humana real, (c) efecto de orden, (d) validacion fuera de muestra y (e) IC del kappa
SHALL quedar en uno de sus dos estados (positivo o negativo declarado) en el resumen,
la introduccion, el marco metodologico, los resultados, la discusion, las conclusiones,
las recomendaciones y el memo, con el mismo estado en todos ellos. Tras la propagacion,
la busqueda de "no medid", "no contrastad", "no estimable" y "no computable" en
`sections/*.tex` SHALL devolver solo los restos legitimos listados en `tasks.md`
(declaraciones sobre la campaña 2026-10, la clase `Bases de Datos`, las hipotesis
subsidiarias, la latencia por etapa, la carga concurrente, la complejidad percibida y
los estados negativos que la campaña de medicion haya dejado). La fila `Lím.` del Anexo I
SHALL enunciar el estado real de cada uno de los cinco limites estructurales que el
dictamen consigno: los que la campaña de medicion cerro y el item (d) validacion fuera de
muestra, que esa campaña declaro como NEGATIVO por ausencia de un corpus independiente.
La fila MUST NOT presentar los cinco limites como cerrados; SHALL declarar que (d)
permanece como limitacion declarada y negativa, y MUST NOT fabricarse un cierre para (d).

#### Scenario: Estado unico por item

- **WHEN** se comparan los pasajes que tratan cada item (a)-(e) en las secciones enumeradas y en el memo
- **THEN** cada item declara el mismo estado en todos los pasajes
- **AND** ningun pasaje conserva el estado previo a la campaña de medicion si esta lo supero

#### Scenario: Restos legitimos

- **WHEN** se ejecuta la busqueda de las cuatro frases sobre `sections/*.tex` despues de aplicar el change
- **THEN** cada coincidencia figura en la lista de restos legitimos de `tasks.md` o corresponde a un estado negativo declarado por la campaña de medicion
- **AND** no queda ninguna coincidencia sin clasificar

#### Scenario: (d) declarado negativo en la fila Lim. del Anexo I

- **WHEN** se lee la fila `Lím.` de la tabla del dictamen del 28 de octubre en el Anexo I
- **THEN** declara que el item (d) validacion fuera de muestra quedo como negativo declarado por ausencia de un corpus independiente
- **AND** no afirma que los cinco limites estructurales se cierren

### Requirement: Sintesis del estado del arte y recomendaciones coherentes con la evidencia comparativa citada

Las afirmaciones de sintesis del estado del arte, de la discusion y de las recomendaciones SHALL ser coherentes con los resultados de las fuentes en que se apoyan. El documento MUST NOT afirmar que la literatura reciente confirma un desplazamiento del enfoque clasico hacia los LLM cuando sus fuentes comparativas (Paket et al., 2024; Colavito et al., 2025) encuentran que los modelos tipo BERT igualan o superan a los LLM generativos, y MUST NOT citar Touvron et al. (2023) como evidencia de que los LLM desplegados localmente son competitivos en clasificacion mediante prompts. Toda caracterizacion de una obra citada en estas secciones SHALL poder contrastarse con su resumen o con su texto completo. En la subseccion de comparacion con la literatura de la discusion (9.2), la declaracion de que los resultados no admiten una comparacion directa con la literatura y la comparacion con el F1 macro reportado para el ingles SHALL reconciliarse: la comparacion con el ingles SHALL presentarse de forma explicitamente calificada como indirecta y no comparable con las cifras de etiqueta unica, coherente con esa declaracion, o SHALL retirarse. El documento MUST NOT presentar una comparacion directa sin calificar junto a la declaracion de no comparabilidad.

#### Scenario: Sintesis del estado del arte sin desplazamiento contrario a la evidencia

- **WHEN** se lee la oracion de sintesis que precede a la tabla `tab:trabajos-academicos`
- **THEN** no afirma que la literatura confirme un desplazamiento hacia arquitecturas basadas en LLM
- **AND** refleja que en las comparaciones directas relevadas los modelos tipo BERT igualan o superan a los LLM generativos, con cita explicita a `paket2024itservice` y `colavito2025benchmarking`

#### Scenario: Llama 2 citado por la disponibilidad de pesos abiertos

- **WHEN** se lee la recomendacion sobre el clasificador supervisado y los modelos de codigo abierto en el capitulo de recomendaciones
- **THEN** `Touvron2023_llama2` se cita solo por la disponibilidad de modelos de pesos abiertos aptos para despliegue local
- **AND** la competitividad en clasificacion no se le atribuye
- **AND** se consigna que en clasificacion de tickets con muchas clases los modelos tipo BERT superaron a LLM abiertos como Llama y Mistral (`paket2024itservice`)

#### Scenario: Caracterizaciones contrastables con la fuente

- **WHEN** se contrastan las citas de Colavito et al. (2025) en el marco teorico y de Jurafsky y Martin en la seccion 2.4 con el resumen o el indice de la version citada
- **THEN** cada caracterizacion se limita a lo que esa evidencia sostiene
- **AND** las inferencias propias de los autores no se presentan como resultados de la fuente

#### Scenario: Cobertura del espanol en la discusion respaldada

- **WHEN** se lee el parrafo de la discusion sobre el desempeno en espanol rioplatense frente a idiomas de mayor cobertura
- **THEN** la afirmacion de que diversos trabajos senalan la menor cobertura de los idiomas distintos del ingles cita fuentes que la sostienen
- **AND** no se menciona un desempeno reportado para el aleman sin una fuente que lo reporte

#### Scenario: Comparabilidad con el ingles calificada en 9.2

- **WHEN** se lee la subseccion de comparacion con la literatura de la discusion (9.2)
- **THEN** la comparacion con el F1 macro reportado para el ingles se presenta como calificada e indirecta, coherente con la afirmacion de que los resultados no admiten comparacion directa
- **AND** no coexiste una comparacion directa sin calificar junto a la declaracion de no comparabilidad

## ADDED Requirements

### Requirement: Atribucion no confirmatoria de Sokolova y Lapalme (2009)

La obra de Sokolova y Lapalme (2009) (`Sokolova2009_performance_measures`) SHALL citarse unicamente como fuente de las DEFINICIONES de las metricas de evaluacion (precision, sensibilidad, F1, valores macro promediados) y de la advertencia sobre el desbalanceo de clases, y MUST NOT presentarse como fuente que confirma, respalda o valida resultados propios de este trabajo. En particular, la oracion de la seccion de resultados que atribuye a esa obra la confirmacion del desempeno desigual entre clases SHALL reformularse para citarla por la definicion de las metricas, sin verbo de confirmacion.

#### Scenario: Sokolova citada por las definiciones

- **WHEN** se buscan las citas de `Sokolova2009_performance_measures` en las secciones de la tesis
- **THEN** cada cita la usa para las definiciones de las metricas o la advertencia de desbalanceo, no para confirmar un resultado propio del trabajo
- **AND** la oracion de resultados sobre el desempeno desigual entre clases no atribuye su confirmacion a Sokolova y Lapalme (2009)

#### Scenario: Verbos de confirmacion retirados

- **WHEN** se lee el pasaje de la seccion de resultados que cita `Sokolova2009_performance_measures`
- **THEN** no usa "confirman", "confirma", "respaldan" ni "validan" para atribuirle un resultado propio
- **AND** el resultado se presenta como hallazgo propio, con la fuente citada para la definicion de la metrica
