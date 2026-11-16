## ADDED Requirements

### Requirement: Retiro de la validacion fuera de muestra del ejemplar

El documento SHALL quedar sin ninguna cifra, tabla, seccion ni afirmacion que dependa del corpus fuera de muestra retirado (los artefactos `corpus_independiente.json`, `corpus_independiente_arbitrado.json`, `doble_etiquetado_independiente.csv`, `doble_etiquetado_arbitrado.csv`, `arbitraje_tres_vias.json`, `predicciones_independiente.json`, `predicciones_arbitrado.json`, sus analisis derivados de `evaluation/data/campana/analisis/`, el bloque primario del brazo de modelo solo y el canario de 103 casos), salvo la declaracion de retiro de la nota de versiones (`subsec:nota-versiones`). En particular SHALL retirarse: el parrafo del corpus independiente de §4.4; los parrafos de §4.7 sobre la linea de base clasica, la sensibilidad a la referencia, el sesgo del vocabulario sobre el corpus arbitrado y el diseno de la validacion fuera de muestra, y la parte fuera de muestra de la calibracion y del brazo de modelo solo; las amenazas de §4.8 propias de esa validacion; las subsecciones `subsec:sesgo-corpus-referencia`, `subsec:validacion-fuera-muestra` y `subsec:ruido-referencia`; la linea de base clasica y el bloque primario del contraste con el modelo solo; las filas fuera de muestra de `tab:calibracion-gate`; las frases correspondientes del Resumen, el *Abstract*, §1.4, §1.7, el capitulo 5, §7.5, el capitulo 9, `tab:cumplimiento-objetivos`, el capitulo 11; los hitos del cronograma (Anexo A) y los apartados del Anexo J de las secciones `3.35` y `3.36` del memo. La clase `Sistemas` SHALL describirse con las cifras dentro de la muestra. El documento SHALL conservar sin cambio de valor las cifras canonicas del corpus de 200 casos y de la campana complementaria (`61,6 s`, `17,76 s`, `W = 363`, `73,5 %`, `0,6508`, `110/138`). Los cardinales que enumeran apartados, amenazas o limitaciones SHALL coincidir con lo enumerado, y ninguna referencia cruzada ni cita SHALL quedar sin destino. El retiro MUST NOT ser silencioso: el cuerpo SHALL remitir una vez a la nota de versiones al declarar que no se dispone de validacion fuera de muestra. El Resumen y el *Abstract* SHALL respetar el tope de 250 palabras con la regla de conteo de c-106.

#### Scenario: Cifras y alias retirados

- **WHEN** se ejecuta `rg -n "0,6893|0,7489|0,7467|0,7024|0,8447|0,8738|0,6055|142/206|147/206|compa.{1,2}a financiera|E3|E4|E5" "docs/Tesis/v10 (IA)/paper/sections"`
- **THEN** las unicas coincidencias estan en `subsec:nota-versiones`
- **AND** cada coincidencia restante se clasifica en el registro del change como declaracion de retiro

#### Scenario: Etiquetas retiradas sin referencias colgantes

- **WHEN** se buscan en `sections/*.tex` las etiquetas `subsec:validacion-fuera-muestra`, `subsec:ruido-referencia`, `subsec:sesgo-corpus-referencia`, `tab:fuera-de-muestra`, `tab:fuera-de-muestra-clases`, `tab:ruido-referencia`, `tab:linea-base-clasica`, `tab:robustez-linea-base`, `tab:sesgo-vocabulario` y `tab:sesgo-subconjuntos`
- **THEN** no existe ni su `\label` ni ningun `\ref`, `\autoref` o `\nameref` que las nombre
- **AND** una compilacion de verificacion no informa referencias ni citas indefinidas

#### Scenario: Conteos coherentes

- **WHEN** se leen la frase inicial del capitulo 8, el cardinal de amenazas de §4.8, el de limitaciones de §9.3 y la introduccion del Anexo J
- **THEN** cada cardinal coincide con los elementos enumerados
- **AND** las secciones del memo que el Anexo J dice condensar coinciden con sus apartados

#### Scenario: Cifras dentro de la muestra intactas

- **WHEN** se comparan las cifras del corpus de 200 casos y de la campana complementaria antes y despues del change
- **THEN** `61,6 s`, `17,76 s`, `W = 363`, `73,5 %`, `0,6508` y `110/138` no cambian
- **AND** la clase `Sistemas` se describe con las cifras dentro de la muestra

#### Scenario: Retiro declarado desde el cuerpo

- **WHEN** se lee la limitacion de §9.3 que trata las metricas dentro de la muestra (o §4.4)
- **THEN** declara que no se dispone de validacion fuera de muestra
- **AND** remite una sola vez a `subsec:nota-versiones`

#### Scenario: Resumen dentro del tope

- **WHEN** se cuentan las palabras del Resumen y del *Abstract* con la regla de c-106
- **THEN** cada uno tiene a lo sumo 250 palabras
- **AND** ninguno menciona la validacion fuera de muestra ni la linea de base

### Requirement: Declaracion de procedencia del retiro en la nota de versiones

La nota de versiones del Anexo I (`subsec:nota-versiones`) SHALL declarar, con el patron de la declaracion del corpus sintetico de julio (N-02), que las versiones 1.3.0 a 1.5.2 incluyeron una validacion fuera de muestra (150 casos mas 56 de refuerzo, etiquetados por `E3` y `E4` y arbitrados por `E5`) y los analisis que dependian de ella (linea de base clasica, bloque primario del brazo de modelo solo, calibracion fuera de muestra, sensibilidad a la referencia, sesgo del vocabulario y arbitraje por mayoria); que esa evidencia se retira del ejemplar; y por que: su procedencia no puede acreditarse como registro primario y los textos no eran incidentes extraidos de una organizacion, sino descripciones genericas de incidentes. Lo que la nota declare sobre como se produjeron los textos, las etiquetas y las marcas temporales SHALL limitarse a lo que los autores confirmen por escrito en el registro de correcciones; si no lo confirman, la nota SHALL declarar que no puede acreditarse, sin conjeturar. La nota MUST NOT atribuir el retiro a otra causa que la procedencia, MUST NOT afirmar hechos de procedencia no confirmados y MUST NOT describir el corpus como proveniente de una tercera organizacion. §7.3 (`11-aspectos-legales.tex`) SHALL ser exacta respecto de todos los textos y audios enviados a proveedores, incluidos los del corpus retirado si se enviaron, con su naturaleza confirmada por los autores. §7.5 MUST NOT conservar el parrafo sobre el consentimiento de `E3`, `E4` y `E5`.

#### Scenario: Declaracion presente

- **WHEN** se lee `subsec:nota-versiones`
- **THEN** figuran las versiones 1.3.0 a 1.5.2, la validacion fuera de muestra con sus analisis dependientes y la declaracion de su retiro
- **AND** el parrafo sigue al de la declaracion del corpus sintetico de julio

#### Scenario: Motivo no ocultado

- **WHEN** se lee el motivo del retiro en la nota
- **THEN** el texto declara que la procedencia no puede acreditarse como registro primario y que los textos no eran incidentes extraidos de una organizacion
- **AND** no atribuye el retiro a la extension, la legibilidad ni otra causa

#### Scenario: Sin hechos de procedencia no confirmados

- **WHEN** se compara cada frase factual de la nota, de §7.3 y de §7.5 con la tabla de compuertas del registro de correcciones
- **THEN** cada frase tiene una respuesta de los autores registrada con fecha
- **AND** donde no hay respuesta, el texto declara que no puede acreditarse

#### Scenario: Transferencias exactas en §7.3

- **WHEN** se lee §7.3
- **THEN** la descripcion de lo enviado al proveedor incluye los textos del corpus retirado si los autores confirman que se enviaron, con su naturaleza
- **AND** no afirma que solo llegaron 119 textos y 81 audios si hubo otras transferencias

#### Scenario: Sin tercera organizacion

- **WHEN** se buscan en `sections/*.tex` "compania financiera", "organizacion financiera" o fechas de ocurrencia de noviembre de 2025 a febrero de 2026
- **THEN** no hay coincidencias fuera de la nota de versiones
- **AND** la nota no describe el corpus como proveniente de una tercera organizacion

### Requirement: Validacion fuera de muestra propuesta como trabajo futuro con procedencia acreditable

La subseccion `subsec:corpus-independiente` de `10-recomendaciones.tex` SHALL proponer, como trabajo futuro, una validacion fuera de muestra sobre un corpus de procedencia acreditable: exportacion original del sistema de una organizacion con sus fechas, autorizacion escrita y encuadre legal documentados antes de su uso, etiquetado ciego por etiquetadores identificados en un registro de sujetos con marcas temporales registradas por la herramienta, cuotas por sector prefijadas, regla de arbitraje prefijada y, sobre el mismo corpus, la comparacion con una linea de base clasica y con el brazo de modelo solo. La propuesta SHALL declarar un criterio de exito. La subseccion MUST NOT informar cifras de la validacion retirada ni presentarla como realizada, y `subsec:frontera-sistemas` SHALL formular su linea con los datos dentro de la muestra.

#### Scenario: Trabajo futuro con requisitos de procedencia

- **WHEN** se lee `subsec:corpus-independiente`
- **THEN** figuran la exportacion original con fechas, la autorizacion documentada, el registro de etiquetadores, las marcas temporales registradas por la herramienta, las cuotas y la regla de arbitraje prefijadas
- **AND** figura un criterio de exito

#### Scenario: Comparaciones pendientes enumeradas

- **WHEN** se lee la propuesta
- **THEN** incluye la comparacion con una linea de base clasica y con el brazo de modelo solo sobre el corpus propuesto

#### Scenario: Sin cifras retiradas

- **WHEN** se buscan en `10-recomendaciones.tex` cifras de la validacion retirada o la expresion "se realizo sobre un corpus independiente"
- **THEN** no hay coincidencias

## MODIFIED Requirements

### Requirement: Contraste acotado de la hipotesis subsidiaria de eficiencia con salvedades declaradas

El documento SHALL declarar que la hipotesis subsidiaria de eficiencia del hibrido frente al brazo «Gemini solo» queda **sin contraste limpio**: el bloque primario prerregistrado (103 casos del corpus fuera de muestra) se retiro con la validacion fuera de muestra y MUST NOT citarse. El unico bloque que subsiste es el de 200 casos dentro de la muestra, que SHALL informarse como **descriptivo**, con su desviacion declarada: no es una prueba limpia porque el vocabulario del filtro y las reglas del prompt se ajustaron con ese corpus, 112 casos se reintentaron por una decision tomada despues de ver los resultados, la corrida es unica a temperatura 0,3 y el analisis no es ciego. Si los autores conservan `tab:gemini-solo`, el pasaje SHALL informar, rotuladas como descriptivas y con remision al memo canonico, la exactitud de cada brazo en ese bloque, la diferencia con su intervalo, el valor p si figura en el memo y la razon de llamadas, y MUST NOT aplicar la regla de decision de tres vias como veredicto. SHALL conservar como salvedades las cifras dentro de la muestra de la etapa de reglas (`0,7405`, 97/131, frente a Gemini con el cortocircuito deshabilitado, `0,6769`, 88/130, segun `docs/deterministic_calibration.md`), con remision a `subsec:sensibilidad-ajustes`, y que la latencia no se midio por etapa. La proporcion de casos que invocan al modelo (cerca de un tercio) SHALL presentarse solo como dato descriptivo de la arquitectura, no como contraste de la hipotesis. MUST NOT presentar ninguna cifra dentro de la muestra como contraste de eficiencia, confirmacion o no inferioridad, y MUST NOT afirmar que la exactitud del hibrido no es inferior. El change MUST NOT ejecutar llamadas pagas nuevas al proveedor: medir el brazo sobre un corpus acreditable queda como trabajo futuro (`subsec:corpus-independiente`).

#### Scenario: Bloque primario retirado

- **WHEN** se buscan `0,8738`, `0,8447` y el bloque de 103 casos en los pasajes de eficiencia de `sections/*.tex`
- **THEN** no hay coincidencias
- **AND** el texto declara que el bloque primario se retiro con la validacion fuera de muestra

#### Scenario: Bloque dentro de la muestra descriptivo

- **WHEN** se lee el pasaje del brazo de modelo solo en `07-resultados.tex`
- **THEN** las cifras de 200 casos figuran rotuladas como descriptivas, con la desviacion de los 112 reintentos y el ajuste con el mismo corpus declarados
- **AND** no se aplica la regla de tres vias como veredicto

#### Scenario: Estimacion dentro de la muestra

- **WHEN** se leen las cifras `0,7405` y `0,6769` en `08-discusion.tex`
- **THEN** el texto las califica como estimaciones dentro de la muestra y sin prueba pareada
- **AND** remite a `subsec:sensibilidad-ajustes`

#### Scenario: Sin llamadas pagas

- **WHEN** se revisa el registro de ejecucion del change
- **THEN** no hubo invocaciones nuevas a Gemini ni re-ejecucion del brazo

#### Scenario: Sin sobreventa de la no inferioridad

- **WHEN** se leen los pasajes de eficiencia en `01-introduccion.tex`, `04-marco-metodologico.tex`, `05-arquitectura.tex`, `07-resultados.tex`, `08-discusion.tex`, `09-conclusiones.tex` y `10-recomendaciones.tex`
- **THEN** ninguno afirma que el hibrido no es inferior en exactitud ni que la hipotesis se contrasto
- **AND** todos declaran que la hipotesis queda sin contraste limpio

#### Scenario: Cifras del contraste con procedencia

- **WHEN** se buscan `0,8738`, `0,8447` y las cifras del bloque primario de 103 casos en `07-resultados.tex`
- **THEN** no figuran como evidencia vigente
- **AND** el texto declara que el bloque primario se retiro con la validacion fuera de muestra y remite a la nota de versiones

#### Scenario: Salvedades presentes

- **WHEN** se lee el pasaje del brazo de modelo solo dentro de la muestra
- **THEN** declara la corrida unica a temperatura 0,3, el origen in-corpus de los ajustes, la latencia no medida por etapa, el analisis no ciego y el reintento de fallos tecnicos
- **AND** el estado se rotula "sin contraste limpio", no "confirmada" ni "no contrastada"

#### Scenario: Regla de decision con el vocabulario previo

- **WHEN** la variante del analisis de sensibilidad con el vocabulario previo al ajuste muestra que la etapa de reglas no supera a Gemini en exactitud sobre los casos que resuelve
- **THEN** esa variante se declara como salvedad
- **AND** la discusion no presenta la ventaja in-corpus como evidencia favorable ni declara un veredicto de eficiencia, que queda sin contraste limpio

#### Scenario: Prueba pareada condicionada al memo

- **WHEN** el bloque primario de 103 casos y la seccion `3.28` del memo canonico se retiran con la validacion fuera de muestra
- **THEN** el texto no cita ningun valor p para el contraste de eficiencia
- **AND** declara que la hipotesis queda sin contraste limpio

#### Scenario: Veredicto y ahorro informados

- **WHEN** se lee el pasaje de eficiencia en `07-resultados.tex`
- **THEN** no figuran el veredicto «no concluyente» ni las cifras fuera de muestra del contraste, retirados con la validacion
- **AND** se declara la hipotesis sin contraste limpio y la estimacion dentro de la muestra, rotulada como descriptiva

### Requirement: Estado declarado de las hipotesis subsidiarias

Las dos hipotesis subsidiarias de `01-introduccion.tex` SHALL tener un estado declarado y coherente en la introduccion, la metodologia, la discusion y las conclusiones. La de integracion multicanal sin cuellos de botella SHALL declararse "contrastada en su dimension de capacidad" porque se midio con un test de carga de costo cero sobre el tramo compartido: el estado SHALL informar el resultado medido (latencia p50/p95, throughput y tasa de error por nivel de concurrencia) y SHALL declarar que la complejidad operativa percibida permanece sin instrumento, de modo que el estado MUST NOT presentarse como un contraste total de la hipotesis. La de mayor eficiencia del esquema hibrido frente a un esquema solo de modelo SHALL declararse "sin contraste limpio" en todos los capitulos, porque el bloque primario prerregistrado se retiro con la validacion fuera de muestra y el unico bloque que subsiste, dentro de la muestra, no es una prueba limpia. MUST NOT declararse "contrastada: no concluyente", "confirmada" ni "refutada". La discusion y las conclusiones MUST NOT afirmar consistencia con la hipotesis de eficiencia apoyandose en la proporcion de casos resueltos sin invocar al modelo, ni afirmar que la integracion multicanal elimino la complejidad operativa percibida.

#### Scenario: Estados declarados en los tres capitulos

- **WHEN** se leen la introduccion, la discusion y las conclusiones
- **THEN** cada hipotesis subsidiaria tiene un estado explicito
- **AND** la de eficiencia figura como "sin contraste limpio" en los tres capitulos
- **AND** la de integracion multicanal figura como "contrastada en su dimension de capacidad" en los tres capitulos

#### Scenario: Frase de consistencia sin sustento retirada

- **WHEN** se busca en `08-discusion.tex` la afirmacion de consistencia con la hipotesis subsidiaria de eficiencia
- **THEN** no aparece apoyada en el porcentaje de casos resueltos sin el modelo
- **AND** en su lugar figura la declaracion de que la hipotesis queda sin contraste limpio

#### Scenario: Subsidiaria multicanal no contrastada

- **WHEN** se leen las conclusiones sobre la integracion de los tres canales
- **THEN** el texto informa el resultado del test de carga con su veredicto de tres vias
- **AND** no afirma que la integracion "confirmo" la ausencia de dispersion operativa ni la complejidad percibida
- **AND** declara que la dimension de capacidad quedo contrastada y la de complejidad percibida no se midio

#### Scenario: Estado no presentado como contraste total

- **WHEN** se lee el estado de la subsidiaria multicanal en cualquier capitulo
- **THEN** no se presenta como un contraste completo de la hipotesis
- **AND** declara explicitamente que la complejidad percibida quedo fuera de la medicion

### Requirement: Afirmaciones acotadas a lo medido

`05-arquitectura.tex` MUST NOT afirmar que el diseno compositivo reduce la latencia y el costo de inferencia sin remitir a lo medido y sin declarar que la latencia se midio solo como cota inferior; si remite a `tab:gemini-solo`, SHALL presentar su bloque como descriptivo dentro de la muestra. `09-conclusiones.tex` SHALL matizar la viabilidad del modelo de lenguaje para la clasificacion con la exactitud por etapa dentro de la muestra y con la salvedad de que la etapa Gemini recibe los casos que las reglas no resuelven, y MUST NOT citar una exactitud por etapa fuera de muestra. `01-introduccion.tex` SHALL precisar que lo excluido del alcance es un modelo supervisado afinado con el corpus acumulado en operacion y MUST NOT presentar una linea de base clasica como referencia de comparacion vigente.

#### Scenario: Latencia y costo con respaldo

- **WHEN** se busca «reduce la latencia y el costo de inferencia» en `05-arquitectura.tex`
- **THEN** no hay coincidencias sin remision a lo medido
- **AND** si se cita `tab:gemini-solo`, se la rotula como descriptiva dentro de la muestra

#### Scenario: Alcance precisado

- **WHEN** se lee el alcance en `01-introduccion.tex`
- **THEN** la exclusion nombra el modelo supervisado afinado con el corpus de operacion
- **AND** no se presenta una linea de base clasica como comparacion vigente

### Requirement: Consistencia interna del veredicto de la intervencion humana y de la validacion fuera de muestra

El documento SHALL presentar de forma consistente el veredicto de la segunda sub-hipotesis (intervencion humana) entre el resumen, la introduccion y los capitulos de resultados y discusion. El resumen SHALL acompanar la cifra `147 / 17,0 %` con el mismo calificador que el cuerpo ("no concluyente, con estimacion puntual por encima de la cota"). La introduccion SHALL distinguir la **tasa de derivacion erronea a priori del 15 %** (declarada preliminar y **no re-medida**) de la **exactitud estricta del brazo manual medida** en la campana complementaria (`0,8278` = `125/151`, de la que se deriva `e_man = 26/151 = 0,1722`); MUST NOT afirmar de forma plana que la tasa de error manual "no fue re-medida" sin reconocer esa medicion. La introduccion SHALL presentar la validacion de la clasificacion como estimacion **dentro de la muestra** y MUST NOT declarar una validacion fuera de muestra, cuyas cifras se retiraron del ejemplar (nota de versiones). La introduccion SHALL rotular `82,78 %` como **exactitud estricta del brazo manual**, no como tasa de error.

#### Scenario: Resumen con el calificador del cuerpo

- **WHEN** se lee el resumen en `00-resumen.tex`
- **THEN** la cifra `147 / 17,0 %` aparece con el calificador "no concluyente, con estimacion puntual por encima de la cota"
- **AND** el calificador coincide con el de `08-discusion.tex`, `04-marco-metodologico.tex` y `07-resultados.tex`

#### Scenario: Tasa a priori y medicion del brazo manual distinguidas

- **WHEN** se lee `01-introduccion.tex` en el pasaje del 15 %
- **THEN** el texto declara que ese 15 % es preliminar y no re-medido
- **AND** remite a la medicion del brazo manual de la campana complementaria (`0,8278`; `e_man = 26/151 = 0,1722`) que si mide esa exactitud

#### Scenario: Validacion fuera de muestra declarada en la introduccion

- **WHEN** se lee la contribucion en `01-introduccion.tex`
- **THEN** la introduccion declara que la validacion fuera de muestra se retiro del ejemplar y remite a la nota de versiones
- **AND** la validacion presentada es la dentro de la muestra, rotulada como tal, y no figuran `0,6893` ni `0,7489` como evidencia

#### Scenario: Rotulo de la exactitud del brazo manual

- **WHEN** se busca "82,78" en los archivos de seccion
- **THEN** aparece rotulado como "exactitud estricta del brazo manual"
- **AND** no aparece rotulado como "tasa de error manual medida"

### Requirement: Procedencia declarada de los ajustes realizados sobre el corpus de validacion

La tesis SHALL declarar en la discusion (`subsec:interpretacion-resultados`) que el vocabulario del filtro deterministico (c-71), las reglas de frontera del prompt (c-72) y el punto de operacion del cortocircuito (c-74) se derivaron de casos y errores observados en el corpus de validacion de 200 casos; SHALL acotar que la mitigacion de c-74 (validacion cruzada de cinco pliegues para el punto de operacion) NO cubre la ampliacion del vocabulario ni las reglas del prompt; SHALL declarar que no se dispuso de un corpus independiente de preproduccion para la campana 2026-10; y SHALL calificar las metricas de clasificacion de los 200 casos (`73,5 %`, `0,6508` y derivadas) como estimaciones dentro de la muestra, sin validacion fuera de muestra vigente en el ejemplar (la informada en las versiones 1.3.0 a 1.5.2 se retiro; ver la nota de versiones). Las demas secciones que afirman la ausencia de exposicion al corpus (`05-arquitectura.tex`, `06-implementacion.tex`, Anexo H) SHALL alinearse con esa declaracion o remitir a ella. La tesis MUST NOT afirmar separacion estricta entre datos de construccion y de validacion, ausencia de exposicion al corpus ni desempeno sobre datos no vistos; MUST NOT afirmar la existencia de un conjunto de aproximadamente 100 incidentes de preproduccion ni remitir a `docs/prompt_gemini_history/`; y MUST NOT alterar ningun valor numerico por esta declaracion.

#### Scenario: Procedencia de los tres ajustes declarada

- **WHEN** se lee `subsec:interpretacion-resultados` en el PDF compilado
- **THEN** se declaran los ajustes del vocabulario del filtro deterministico, de las reglas de frontera del prompt y del punto de operacion realizados sobre el corpus de validacion
- **AND** las metricas de clasificacion de los 200 casos se califican como estimaciones dentro de la muestra

#### Scenario: Mitigacion fuera de muestra acotada

- **WHEN** se lee la declaracion de procedencia
- **THEN** la mitigacion de c-74 se acota al punto de operacion
- **AND** se declara expresamente que esa mitigacion no cubre el vocabulario ni las reglas del prompt

#### Scenario: Sin corpus independiente de preproduccion

- **WHEN** se busca en `sections/*.tex` una afirmacion sobre un corpus independiente de incidentes de preproduccion
- **THEN** se declara que la campana 2026-10 no dispuso de un corpus de esas caracteristicas
- **AND** no se afirma la existencia de un conjunto de aproximadamente 100 incidentes de preproduccion

#### Scenario: Sin afirmacion de no exposicion

- **WHEN** se buscan en `sections/*.tex` las afirmaciones "sin exposicion a" (el corpus o los 200 casos de validacion), "sin acceso al corpus", "datos no vistos" y "separacion estricta"
- **THEN** ninguna aparece como afirmacion vigente sobre la version evaluada
- **AND** no queda ninguna mencion de desempeno fuera de muestra como evidencia vigente; solo la nota de versiones que declara su retiro y el trabajo futuro de `subsec:corpus-independiente`

#### Scenario: Numeros intactos

- **WHEN** se comparan las metricas de clasificacion del PDF antes y despues de la declaracion
- **THEN** no cambia ningun valor numerico

### Requirement: Versión entregada identificable y con la evidencia vigente

La portada (`00-portada.tex`), la entrada bibliográfica del repositorio (`Bibliography_base.bib`, entrada del repositorio) y el Anexo B (`12-anexos.tex`, `sec:anexo-repositorio`) SHALL identificar la misma versión nueva del documento, cuyo tag SHALL contener el texto y los artefactos de evidencia que la tesis cita. El Anexo B MUST NOT afirmar que los commits posteriores al tag no modifican las fuentes si eso no es verificable; SHALL declarar que el commit posterior al tag solo consigna su hash. El Anexo B SHALL desambiguar de forma explícita la `versión entregada` del documento (el tag del manuscrito) de la `configuración entregada` del software (el tag `v1.3.0`), de modo que la misma palabra no designe dos objetos distintos. El commit etiquetado SHALL llevar en el Anexo B la oración de reemplazo sin imprimir el hash de una release previa, y el commit inmediatamente posterior SHALL reemplazarla por el hash completo del commit etiquetado. El cronograma SHALL registrar los hitos con la precisión de su evidencia y MUST NOT presentar como hitos vigentes la validación fuera de muestra, el arbitraje ni la línea de base retirados (c-235); si se conservan como historia, SHALL rotularse como retirados. `paper/compilacion.md` SHALL regenerarse con la compilación final. La creación y la publicación del tag MUST NOT realizarse sin confirmación expresa de los autores.

#### Scenario: Tag coherente con el documento

- **WHEN** se compara el hash del Anexo B con `git rev-parse <tag>^{commit}`
- **THEN** coinciden
- **AND** `git show <tag>:` encuentra los artefactos de evidencia citados por la tesis
- **AND** la portada, la entrada del repositorio y el Anexo B nombran la misma versión

#### Scenario: El tag contiene la evidencia nueva

- **WHEN** se ejecuta `git merge-base --is-ancestor <commit-de-c-223> <tag>` y la verificación análoga para `c-224`, `c-225` y `c-226`
- **THEN** los cuatro commits son ancestros del tag
- **AND** `git show <tag>:docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` contiene el anexo nuevo de números canónicos

#### Scenario: Desambiguación de documento y software

- **WHEN** se lee `sec:anexo-repositorio` en el Anexo B
- **THEN** la `versión entregada` designa el tag del documento de tesis y la `configuración entregada` designa el tag del software
- **AND** las dos expresiones se declaran como objetos distintos

#### Scenario: Sin hash ajeno en el PDF etiquetado

- **WHEN** se extrae el texto del PDF compilado en el tag y se busca el hash de la release previa (`v1.4.1`)
- **THEN** el PDF etiquetado no contiene ese hash
- **AND** el Anexo B del PDF etiquetado muestra la oración de reemplazo

#### Scenario: Cronograma actualizado

- **WHEN** se lee `docs/diagrams/cronograma.md`
- **THEN** figuran los hitos de noviembre de 2026 con su evidencia
- **AND** los hitos de la validación fuera de muestra, el arbitraje y la línea de base no figuran como vigentes

### Requirement: Balance neto entre el ahorro de registro y el costo de las derivaciones erroneas

El capitulo de discusion (`08-discusion.tex`) SHALL incluir una subseccion con rotulo `subsec:balance-neto` que compute el balance neto trimestral entre el ahorro de tiempo de registro y el costo de las derivaciones erroneas adicionales del clasificador respecto del flujo manual. La subseccion SHALL enunciar de forma explicita las formulas del balance neto, `B = (N / 3.600) x [Delta t - (e_aut - e_man) x c]`, y de la exactitud minima de equilibrio, `a* = 1 - e_man - Delta t / c`, junto con la procedencia de cada insumo: universo trimestral `N ~ 2.646`, ahorro medio por incidente `Delta t = 43,82 s` (43,8 s en el texto), tasas de error del clasificador y del brazo manual medidas contra la referencia comun de la seccion 3.21 del memo (`e_aut = 28/138 = 0,2029`; `e_man = 26/151 = 0,1722`) y costo por derivacion erronea `c = 69,51 s`, IC 95 % `[33,42; 106,56] s`, de la seccion 3.31 (c-220). La subseccion SHALL incluir una tabla con rotulo `tab:balance-neto` que, para el `c` medido y para la rejilla historica de 5, 10 y 15 minutos, reporte la exactitud minima de equilibrio y el balance neto, y SHALL contrastar la exactitud minima de equilibrio con la exactitud estricta observada y su intervalo de Wilson. La fila o columna del `c` medido SHALL identificarse como lectura central; la rejilla de 5, 10 y 15 minutos SHALL rotularse como sensibilidad del supuesto superado y MUST NOT presentarse como insumo vigente. La subseccion SHALL informar el intervalo de `B` con el metodo de propagacion declarado y MUST NOT enunciar el signo si el intervalo no lo fija. La subseccion MUST NOT incluir sensibilidades calculadas con la tasa de error fuera de muestra del corpus retirado (la sensibilidad mixta de c-221 se retiro con la validacion fuera de muestra, c-235). Todo valor de la subseccion y de la tabla MUST coincidir con el registrado en `docs/Tesis/Correcciones/numeros-canonicos.md`. La misma lectura del balance SHALL aparecer en `00-resumen.tex`, `09-conclusiones.tex` y `12-anexos.tex`, tablas incluidas.

#### Scenario: Formulas e insumos explicitos

- **WHEN** se lee la subseccion `subsec:balance-neto`
- **THEN** figuran las formulas del balance neto y de la exactitud minima de equilibrio con la definicion de `N`, `Delta t`, `e_aut`, `e_man` y `c`
- **AND** cada insumo remite a su origen en el documento o a la seccion del memo canonico que lo mide

#### Scenario: Lectura central con el costo medido

- **WHEN** se leen el texto y `tab:balance-neto`
- **THEN** el escenario con `c = 69,51 s` y su intervalo `[33,42; 106,56] s` figura como lectura central
- **AND** el balance y la exactitud minima de equilibrio se informan con su intervalo

#### Scenario: Grilla previa rotulada como superada

- **WHEN** se busca «10 a 15 minutos» como insumo del balance
- **THEN** la subseccion declara que ese supuesto fue reemplazado por el `c` medido
- **AND** la rejilla de 5, 10 y 15 minutos figura rotulada como sensibilidad del supuesto superado, con sus cifras conservadas

#### Scenario: Calculo con los supuestos del propio documento

- **WHEN** se aplican las formulas con la grilla superada de 15 % manual y 10 y 15 minutos
- **THEN** el texto informa del orden de 304 derivaciones erroneas adicionales por trimestre, un costo de 50,7 y 76,1 horas-persona y un balance neto de -18,5 y -43,9 horas-persona
- **AND** rotula esos valores como sensibilidad del supuesto superado y no como lectura vigente

#### Scenario: Tabla de escenarios con el punto de equilibrio

- **WHEN** se lee la tabla `tab:balance-neto`
- **THEN** contiene el escenario con el `c` medido como lectura central y, como sensibilidad superada, una fila por tasa manual (10 %, 15 %, 20 % y 26,5 %) y costos de 5, 10 y 15 minutos
- **AND** cada celda coincide con el valor del memo canonico bajo la convencion de redondeo declarada en la nota de la tabla

#### Scenario: Incertidumbre muestral considerada

- **WHEN** se contrasta la exactitud minima de equilibrio con la exactitud estricta observada
- **THEN** el texto compara la exactitud minima de equilibrio del escenario medido con el intervalo de Wilson observado y declara el signo solo si el intervalo de `B` lo fija
- **AND** para la grilla superada declara que, con una tasa manual del 15 % y 10 minutos por reasignacion, el signo del balance no queda determinado por la muestra

#### Scenario: Exactitud laxa sin cifras inventadas

- **WHEN** la exactitud laxa esta registrada en el memo canonico al momento de aplicar el cambio
- **THEN** la subseccion la compara con la exactitud minima de equilibrio e informa los escenarios en que el balance resulta positivo bajo esa lectura
- **AND** si no esta registrada, la subseccion no presenta ningun valor de exactitud laxa y declara que el 26,5 % es una cota superior de la tasa operativa de derivacion erronea atribuible al clasificador

#### Scenario: Incertidumbre y signo

- **WHEN** se contrasta el intervalo de `B` con cero
- **THEN** el texto enuncia el signo solo si el intervalo lo fija
- **AND** declara el metodo de propagacion y el limite que no se iguala

#### Scenario: Sensibilidad mixta no promovida

- **WHEN** se busca en `subsec:balance-neto` una sensibilidad calculada con la tasa de error fuera de muestra
- **THEN** no figura
- **AND** los insumos del balance provienen del corpus de 200 casos y de la campana complementaria

#### Scenario: Lectura unica del balance

- **WHEN** se compara la calificacion del balance en `00-resumen.tex`, `08-discusion.tex`, `09-conclusiones.tex` y `12-anexos.tex`
- **THEN** los cuatro usan la misma lectura y el mismo signo
- **AND** el conteo de palabras del resumen y del abstract no aumenta

#### Scenario: Remisiones resueltas

- **WHEN** se compila el documento con XeLaTeX tras incorporar la subseccion y la tabla
- **THEN** las remisiones a `subsec:balance-neto` y `tab:balance-neto` resuelven sin referencias indefinidas
- **AND** ambos rotulos son unicos en el documento

## REMOVED Requirements

### Requirement: Reporte de la validacion fuera de muestra
**Reason**: La validacion fuera de muestra se retira del ejemplar (K-01, opcion 2 de la devolucion de tercera instancia del 16-11-2026): su procedencia no puede acreditarse como registro primario.
**Migration**: Ver "Retiro de la validacion fuera de muestra del ejemplar" y "Declaracion de procedencia del retiro en la nota de versiones"; `subsec:corpus-independiente` pasa a "Validacion fuera de muestra propuesta como trabajo futuro con procedencia acreditable".

### Requirement: Validación fuera de muestra declarada como realizada con su resultado y sus límites
**Reason**: La validacion deja de informarse como realizada porque se retira del ejemplar (K-01).
**Migration**: La nota de versiones declara que se informo en las versiones 1.3.0 a 1.5.2 y que se retira; el cuerpo declara que no se dispone de validacion fuera de muestra ("Retiro de la validacion fuera de muestra del ejemplar").

### Requirement: Trazabilidad del cierre de la validación fuera de muestra en el registro y el Anexo I
**Reason**: El cierre del dock "validacion fuera de muestra no realizada" se revierte con el retiro (K-01).
**Migration**: El registro de correcciones agrega la entrada de c-235 (K-01 por retiro) y el Anexo I.1 declara el retiro ("Declaracion de procedencia del retiro en la nota de versiones").

### Requirement: Reporte de las métricas ampliadas fuera de muestra y del sesgo de exclusión
**Reason**: Las metricas ampliadas dependen del corpus fuera de muestra retirado (K-01).
**Migration**: Se retiran del ejemplar; los valores quedan en el memo con estado `retirado` (requisito aditivo de `tesis-numeros-canonicos`).

### Requirement: Declaracion explicita de la clase medida mas debil
**Reason**: La cifra de `Sistemas` (F1 0,2222 sobre 5 casos) proviene del corpus fuera de muestra retirado (K-01).
**Migration**: La clase `Sistemas` se describe con las cifras dentro de la muestra ("Retiro de la validacion fuera de muestra del ejemplar").

### Requirement: La validacion fuera de muestra no se informa como trabajo futuro
**Reason**: Sin validacion vigente, la validacion fuera de muestra vuelve a ser trabajo futuro (K-01).
**Migration**: Ver "Validacion fuera de muestra propuesta como trabajo futuro con procedencia acreditable".

### Requirement: Análisis de sensibilidad a la referencia de verdad en resultados y método
**Reason**: El analisis se calcula sobre el corpus arbitrado de 206 casos y el kappa `E3`/`E4`, retirados (K-01).
**Migration**: Se retiran `subsec:ruido-referencia`, `tab:ruido-referencia` y el parrafo metodologico; el memo marca sus valores como `retirado`.

### Requirement: Repetición de cifras acotada y remisión a la tabla fuera de muestra
**Reason**: Las cifras `0,8447` y `0,6893` y la tabla `tab:fuera-de-muestra` se retiran (K-01).
**Migration**: La busqueda de cifras retiradas de "Retiro de la validacion fuera de muestra del ejemplar" reemplaza el conteo de repeticiones.

### Requirement: Declaracion de la relacion de referencias del contraste de eficiencia
**Reason**: El bloque de 103 casos y la referencia arbitrada de 206 se retiran (K-01, M-02).
**Migration**: Ver "Contraste acotado de la hipotesis subsidiaria de eficiencia con salvedades declaradas" (MODIFIED): la hipotesis queda sin contraste limpio.

### Requirement: Mitigación del sesgo de corpus y de la fragilidad de la referencia en la tesis
**Reason**: El analisis del sesgo del vocabulario y de los subconjuntos `E3`/`E4`/`E5` se calcula sobre el corpus retirado (K-01).
**Migration**: Se retiran `subsec:sesgo-corpus-referencia` y el parrafo metodologico; las amenazas de ajuste con el mismo corpus y de referencia fragil se conservan como limitaciones sin esa sensibilidad.

### Requirement: Propagación del resultado arbitrado a la discusión, las conclusiones y las recomendaciones
**Reason**: El resultado arbitrado se retira (K-01).
**Migration**: Ver "Retiro de la validacion fuera de muestra del ejemplar".

### Requirement: Clase Sistemas descrita con el soporte del corpus arbitrado
**Reason**: El soporte de 61 casos y sus metricas provienen del corpus arbitrado retirado (K-01).
**Migration**: La clase `Sistemas` se describe con las cifras dentro de la muestra ("Retiro de la validacion fuera de muestra del ejemplar").

### Requirement: Trabajos futuros reformulados a partir de lo ejecutado
**Reason**: El doble etiquetado, el arbitraje y el refuerzo que la reformulacion daba por ejecutados se retiran (K-01).
**Migration**: Ver "Validacion fuera de muestra propuesta como trabajo futuro con procedencia acreditable", que incluye `subsec:frontera-sistemas`.

### Requirement: Subsecciones propias para la validación fuera de muestra y las comparaciones
**Reason**: `subsec:validacion-fuera-muestra`, `tab:fuera-de-muestra`, `tab:fuera-de-muestra-clases` y `tab:linea-base-clasica` se retiran (K-01).
**Migration**: Ver "Retiro de la validacion fuera de muestra del ejemplar" (etiquetas retiradas y conteo de apartados); `tab:gemini-solo` se trata en el contraste de eficiencia (MODIFIED).

### Requirement: Apartado metodológico del diseño fuera de muestra
**Reason**: El diseno de la validacion fuera de muestra y sus amenazas se retiran de §4.7 y §4.8 (K-01).
**Migration**: Ver "Retiro de la validacion fuera de muestra del ejemplar" (conteo de amenazas) y "Declaracion de procedencia del retiro en la nota de versiones".

### Requirement: Resumen con la evidencia fuera de muestra
**Reason**: El Resumen y el *Abstract* dejan de mencionar la exactitud fuera de muestra y la linea de base (K-01).
**Migration**: Ver el escenario "Resumen dentro del tope" de "Retiro de la validacion fuera de muestra del ejemplar"; la lectura del balance la fija `c-236`.

### Requirement: Balance neto con sensibilidad fuera de muestra
**Reason**: La sensibilidad del balance con la tasa de error fuera de muestra depende del corpus retirado (K-01).
**Migration**: Se quita de `subsec:balance-neto` (`08-discusion.tex` L119 y L125); el resto de §9.5 lo reescribe `c-236` sobre "Balance neto entre el ahorro de registro y el costo de las derivaciones erroneas" (MODIFIED aqui solo en esa clausula).

### Requirement: Reproducibilidad declarada
**Reason**: Las declaraciones sobre las dos corridas fuera de muestra y la preservacion de su commit se retiran de la tesis con la validacion (K-01).
**Migration**: La preservacion por tag sigue documentada en el README de campana, rotulada como material retirado (requisito OOS-026 de `evaluation-out-of-sample-validation`); OOS-025 no cambia.

### Requirement: Acotación del arbitraje por mayoría en la limitación y los resultados
**Reason**: El arbitraje de `E5` y el rango `142/206` a `147/206` se retiran (K-01).
**Migration**: Se retiran la limitacion correspondiente, el parrafo de resultados y el apartado 3.35 del Anexo J.

### Requirement: Robustez de la brecha frente a la referencia en resultados y discusión
**Reason**: La brecha hibrido menos linea de base se calcula sobre el corpus retirado (K-01).
**Migration**: Se retiran `tab:robustez-linea-base`, su lectura en §9.3 y el apartado 3.36 del Anexo J; ver TLB-04 (MODIFIED) en `tesis-baseline-integration`.
