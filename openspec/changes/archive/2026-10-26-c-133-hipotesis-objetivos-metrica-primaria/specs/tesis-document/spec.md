## ADDED Requirements

### Requirement: Grados de cumplimiento de los objetivos acotados a la evidencia

La tabla `tab:cumplimiento-objetivos` de `09-conclusiones.tex` SHALL asignar a cada objetivo el grado "Alcanzado" solo cuando cada componente exigido por su enunciado literal en `01-introduccion.tex` este evidenciado en la version evaluada; "Alcanzado parcialmente" cuando al menos un componente este evidenciado y al menos otro no se cumpla o no se haya medido; y "No alcanzado" cuando no se cumpla el criterio del objetivo. Toda fila "Alcanzado parcialmente" SHALL nombrar en su evidencia el componente no cumplido o no medido. Los objetivos especificos 1, 3 y 4 SHALL figurar como "Alcanzado parcialmente" mientras falte la evidencia de, respectivamente, la comunicacion asincronica y el cifrado verificado en la instancia publicada; la calidad de clasificacion por canal; y la exactitud del brazo manual y la proporcion de intervencion humana. El objetivo general SHALL desglosarse en sus tres componentes (tiempo de registro, calidad de la clasificacion y proporcion de intervencion humana) con estado individual, y su grado global SHALL ser coherente con ese desglose. El documento MUST NOT reformular el enunciado de un objetivo para ajustarlo a lo construido o medido, y la prosa de las conclusiones SHALL ser coherente con la tabla.

#### Scenario: Objetivos 1, 3 y 4 parcialmente alcanzados

- **WHEN** se leen las filas de los objetivos especificos 1, 3 y 4 en `tab:cumplimiento-objetivos`
- **THEN** cada una declara "Alcanzado parcialmente"
- **AND** su evidencia nombra el componente faltante: invocacion sincronica y TLS no verificado (1); calidad por canal no medida (3); exactitud del brazo manual e intervencion humana no medidas (4)

#### Scenario: Objetivo general desglosado

- **WHEN** se lee la fila del objetivo general
- **THEN** figuran el tiempo de registro como alcanzado, la calidad de la clasificacion como evaluada por debajo del umbral y la intervencion humana como no medida
- **AND** el grado global es "Alcanzado parcialmente"

#### Scenario: Enunciados de objetivos sin reformular

- **WHEN** se comparan los enunciados del objetivo general y de los objetivos especificos en `01-introduccion.tex` con los de la version previa al change
- **THEN** los enunciados no cambian
- **AND** solo cambia su grado de cumplimiento en la tabla

#### Scenario: Reversion condicionada a evidencia

- **WHEN** se dispone de evidencia nueva para un componente faltante del objetivo 1 o del objetivo 3 (por ejemplo, la que aporte c-140 para el objetivo 1) y se propone elevar su grado
- **THEN** el grado solo pasa a "Alcanzado" si la tabla cita evidencia para cada componente faltante (TLS verificado y comunicacion asincronica para el 1; calidad por canal sin evidencia de degradacion y decision del autor sobre la complejidad percibida para el 3)
- **AND** si la evidencia es posterior a la validacion experimental, la celda lo declara

#### Scenario: Objetivo 6 con evidencia ampliada

- **WHEN** se lee la fila del objetivo especifico 6
- **THEN** su grado sigue la regla de esta tabla y su evidencia cita el analisis de errores, la calibracion por etapa y el analisis de sensibilidad de los ajustes (`subsec:sensibilidad-ajustes`)
- **AND** si alguna de esas piezas no esta disponible, el grado no es "Alcanzado" sin declarar el componente faltante

#### Scenario: Prosa coherente con la tabla

- **WHEN** se leen los parrafos de las conclusiones que tratan el objetivo general y los objetivos 1, 3 y 4
- **THEN** ninguno afirma un cumplimiento pleno que la tabla declare parcial
- **AND** el primer parrafo declara cumplido parcialmente el objetivo general

### Requirement: Segunda sub-hipotesis con fraccion esperada explicita

La segunda sub-hipotesis (`01-introduccion.tex`, `subsec:hipotesis-trabajo`) SHALL enunciarse con una fraccion esperada numerica explicita, derivada de un criterio fijado a priori en el propio documento (en esta version, una proporcion de casos con accion manual de un operador no superior a `0,15`, complemento del umbral de exactitud del 85 %), junto con su contraste (proporcion con intervalo de confianza de Wilson) y su criterio de falsacion. El texto SHALL declarar que la formulacion original, referida al proceso manual y sin fraccion esperada especificada, no era contrastable, y que la cota se explicita en esta version. Mientras no exista registro primario de intervencion por caso, la sub-hipotesis SHALL declararse "no contrastada por ausencia de registro primario" en el resumen, la introduccion, los resultados y las conclusiones. El documento MUST NOT presentar las derivaciones del gate de revision (ninguna en el corpus) como contraste o confirmacion de esta sub-hipotesis y MUST NOT cuantificar la proporcion. Toda remision desde la sub-hipotesis SHALL apuntar a una seccion que declare la ausencia de registro primario; si remite a la lista de limitaciones del estudio (`subsec:limitaciones-estudio`), esa lista SHALL incluir la proporcion de intervencion humana no medida y su oracion introductoria SHALL declarar el numero real de limitaciones listadas.

#### Scenario: Fraccion esperada y criterio de falsacion explicitos

- **WHEN** se lee la segunda sub-hipotesis en `01-introduccion.tex`
- **THEN** declara la cota numerica, su derivacion del umbral fijado a priori, el contraste con intervalo de Wilson y el criterio de falsacion
- **AND** la cota figura en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Formulacion original declarada no contrastable

- **WHEN** se lee la segunda sub-hipotesis
- **THEN** el texto declara que la comparacion con el proceso manual, donde la intervencion es total por definicion, no era contrastable sin fraccion esperada
- **AND** declara que la cota se explicita en esta version

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

### Requirement: Estado declarado de las hipotesis subsidiarias

Las dos hipotesis subsidiarias de `01-introduccion.tex` SHALL tener un estado declarado y coherente en la introduccion, la discusion y las conclusiones. La de integracion multicanal sin cuellos de botella SHALL declararse "no contrastada" mientras no se mida la capacidad bajo carga concurrente. La de mayor eficiencia del esquema hibrido frente a un esquema solo de modelo SHALL declararse "contrastada de forma acotada" solo si el texto informa el contraste acotado con sus salvedades y el analisis de sensibilidad de los ajustes del clasificador no lo contradice; en caso contrario SHALL declararse "no contrastada". La discusion MUST NOT afirmar consistencia con la hipotesis de eficiencia apoyandose solo en la proporcion de casos resueltos sin invocar al modelo.

#### Scenario: Estados declarados en los tres capitulos

- **WHEN** se leen la introduccion, la discusion y las conclusiones
- **THEN** cada hipotesis subsidiaria tiene un estado explicito
- **AND** el estado es el mismo en los tres capitulos

#### Scenario: Frase de consistencia sin sustento retirada

- **WHEN** se busca en `08-discusion.tex` la afirmacion de consistencia con la hipotesis subsidiaria de eficiencia
- **THEN** no aparece apoyada solo en el 65,5 % de casos resueltos sin el modelo
- **AND** en su lugar figura el contraste acotado con sus salvedades, o el rotulo "no contrastada"

#### Scenario: Subsidiaria multicanal no contrastada

- **WHEN** se leen las conclusiones sobre la integracion de los tres canales
- **THEN** el texto no afirma que la integracion "confirmo" la ausencia de dispersion operativa o de cuellos de botella
- **AND** declara que la hipotesis subsidiaria de integracion multicanal no se contrasto

### Requirement: Contraste acotado de la hipotesis subsidiaria de eficiencia con salvedades declaradas

Cuando el documento sostenga la hipotesis subsidiaria de eficiencia del esquema hibrido, SHALL hacerlo con cifras ya documentadas en el repositorio (sobre los 131 casos que resuelve la etapa de reglas: exactitud de la etapa de reglas `0,7405`, 97/131, frente a Gemini ejecutado sobre 130 de esos casos con el cortocircuito deshabilitado, `0,6769`, 88/130, segun `docs/deterministic_calibration.md`) y SHALL declarar en el mismo pasaje: que las cifras son estimaciones dentro de la muestra, con remision al analisis de sensibilidad de los ajustes del clasificador (`subsec:sensibilidad-ajustes`); si se aplico o no una prueba pareada; que la comparacion se hace sobre el mismo corpus con que se ajustaron el vocabulario, las reglas del prompt y el punto de operacion del filtro; y que la latencia no se midio por etapa, salvo que otro change la reporte. Si la variante de ese analisis con el vocabulario previo al ajuste muestra que la etapa de reglas no supera a Gemini en exactitud sobre los casos que resuelve, la hipotesis SHALL rotularse "no contrastada". La prueba pareada (McNemar exacta) SHALL citarse solo si figura registrada en el memo canonico, computada fuera de linea sobre los pares por caso de la cache de calibracion por el change dueno de esa cache. El change MUST NOT ejecutar llamadas pagas al proveedor ni presentar el contraste acotado como confirmacion de la hipotesis.

#### Scenario: Cifras del contraste con procedencia

- **WHEN** se leen las cifras del contraste en `08-discusion.tex`
- **THEN** coinciden con `docs/deterministic_calibration.md` (97/131 = 0,7405 y 88/130 = 0,6769)
- **AND** figuran en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Salvedades presentes

- **WHEN** se lee el pasaje del contraste
- **THEN** declara la ausencia (o el resultado) de la prueba pareada, el origen in-corpus de los ajustes del clasificador y la latencia no medida por etapa
- **AND** el estado de la hipotesis se rotula "contrastada de forma acotada", no "confirmada"

#### Scenario: Estimacion dentro de la muestra

- **WHEN** se leen las cifras 0,7405 y 0,6769 en `08-discusion.tex`
- **THEN** el texto las califica como estimaciones dentro de la muestra
- **AND** remite a `subsec:sensibilidad-ajustes`

#### Scenario: Regla de decision con el vocabulario previo

- **WHEN** la variante del analisis de sensibilidad con el vocabulario previo al ajuste muestra que la etapa de reglas no supera a Gemini en exactitud sobre los casos que resuelve
- **THEN** la hipotesis subsidiaria de eficiencia se rotula "no contrastada" en la introduccion, la discusion y las conclusiones
- **AND** la discusion no presenta el contraste acotado como evidencia favorable

#### Scenario: Prueba pareada condicionada al memo

- **WHEN** el memo canonico no registra la prueba pareada (por ejemplo, porque la cache `evaluation/predicciones_calibracion.json` no se recupero)
- **THEN** el texto declara que la diferencia no se sometio a una prueba pareada
- **AND** no se cita ningun valor p para este contraste

#### Scenario: Sin llamadas pagas

- **WHEN** se revisa el registro de ejecucion del change
- **THEN** no hubo invocaciones a Gemini ni re-ejecucion del clasificador
- **AND** toda cifra nueva proviene de documentos o caches ya versionados o recuperados

### Requirement: Metrica primaria unica del F1 macro

El documento SHALL usar el macro-F1 de umbral sobre las cuatro clases estimables (`0,6508`) como metrica primaria y unico referente del umbral `0,85` en el resumen, el abstract, la tercera sub-hipotesis, la tabla de cumplimiento de objetivos, la metodologia, los resultados y la discusion. Toda aparicion del macro-F1 de cinco clases (`0,5207`) SHALL acompanarse de su aclaracion (incluye Bases de Datos, con un unico caso y no estimable). La metodologia SHALL definir el macro-F1 de umbral excluyendo las clases con soporte unitario. Los resultados SHALL declarar por que se excluye la clase no estimable y que la eleccion no altera el veredicto, porque ambos valores quedan por debajo de `0,85`. El memo canonico SHALL registrar `0,6508` como `vigente`.

#### Scenario: Primario en resumen y abstract

- **WHEN** se lee `00-resumen.tex`
- **THEN** el resumen y el abstract citan 0,6508 (0.6508) rotulado como macro-F1 de umbral sobre las cuatro clases estimables
- **AND** no citan 0,5207 sin su aclaracion

#### Scenario: Primario en la hipotesis y en la tabla de objetivos

- **WHEN** se leen la tercera sub-hipotesis y la fila del objetivo especifico 2 de `tab:cumplimiento-objetivos`
- **THEN** ambas citan 0,6508 como macro-F1 de umbral
- **AND** si la fila cita 0,5207, lo acompana su aclaracion

#### Scenario: Cada aparicion rotulada

- **WHEN** se ejecuta `grep -n "0[,.]5207"` y `grep -n "0[,.]6508"` sobre `paper/sections/*.tex`
- **THEN** cada linea con 0,5207 contiene su aclaracion (cinco clases, no estimable o equivalente)
- **AND** cada linea con 0,6508 lo rotula como de umbral o sobre cuatro clases estimables

#### Scenario: Definicion metodologica coherente

- **WHEN** se leen la fila del F1 macro en `tab:variables` y el analisis estadistico de `04-marco-metodologico.tex`
- **THEN** el F1 macro de umbral excluye las clases con soporte unitario
- **AND** no se define el F1 macro de umbral sobre los cinco sectores

#### Scenario: Robustez de la eleccion declarada

- **WHEN** se lee la oracion del macro-F1 en `07-resultados.tex`
- **THEN** declara que el umbral 0,85 se evalua contra el macro-F1 de umbral y por que se excluye la clase no estimable
- **AND** declara que ambos valores quedan por debajo del criterio

#### Scenario: Memo coherente

- **WHEN** se lee `docs/Tesis/Correcciones/numeros-canonicos.md`
- **THEN** el macro-F1 de cuatro clases figura como `vigente` y primario de umbral
- **AND** el macro-F1 de cinco clases figura como informativo

### Requirement: Procedencia canonica de las cifras de hipotesis, objetivos y metrica primaria

Toda cifra que las correcciones de hipotesis, objetivos y metrica primaria introduzcan en las fuentes LaTeX SHALL figurar en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia (archivo y linea) y su estado antes de citarse en el texto. Ninguna cifra MUST fabricarse ni derivarse de una fuente no versionada. Las correcciones MUST NOT reintroducir valores `retirado`, en particular la intervencion humana del `9,5 %`.

#### Scenario: Cifras nuevas registradas

- **WHEN** se listan las cifras nuevas que cita el texto (por ejemplo 0,15; 97/131; 0,7405; 88/130; 0,6769; 65,5 %)
- **THEN** cada una figura en el memo canonico con procedencia y estado
- **AND** el valor del texto coincide con el del memo

#### Scenario: Sin valores retirados

- **WHEN** se busca "9,5" como proporcion de intervencion humana en las fuentes tras las correcciones
- **THEN** no aparece como resultado
- **AND** el memo conserva su estado `retirado`

### Requirement: Neutralidad de paginas y palabras de las correcciones de hipotesis, objetivos y metrica primaria

Las correcciones de hipotesis, objetivos y metrica primaria MUST NOT aumentar el total de paginas del PDF compilado respecto del estado compilado inmediatamente anterior a su aplicacion, ni desplazar las paginas de inicio de los capitulos, salvo que, agotadas las compensaciones dentro de los parrafos propios, el exceso quede documentado en `docs/Tesis/Correcciones/dictamen-correcciones.md` para su resolucion en el gate de paginas de la integracion final, que fija el tope global. El exceso MUST NOT compensarse recortando parrafos asignados a otros changes. El resumen y el abstract MUST NOT aumentar su numero de palabras de prosa (regla de conteo de c-106) y SHALL quedar en 250 palabras o menos.

#### Scenario: Paginas sin aumento

- **WHEN** se compila el PDF antes y despues de aplicar las correcciones
- **THEN** el total de paginas despues es menor o igual que antes
- **AND** las paginas de inicio de la introduccion, la discusion, las conclusiones y las recomendaciones no cambian, o el exceso queda documentado

#### Scenario: Palabras del resumen sin aumento

- **WHEN** se cuentan las palabras de prosa del resumen y del abstract antes y despues de las correcciones
- **THEN** el conteo posterior no supera al anterior
- **AND** ambos quedan en 250 palabras o menos

## MODIFIED Requirements

### Requirement: English abstract

The thesis SHALL contain an English abstract section immediately after the Spanish "Resumen" in `00-resumen.tex`. The abstract SHALL be at most 250 words, SHALL accurately summarize the thesis content, and SHALL be consistent with the reduced Spanish "Resumen" (same key figures, same category strings, same declared state of the principal hypothesis).

#### Scenario: English abstract present and positioned
- **WHEN** opening the compiled PDF
- **THEN** an "Abstract" section appears after the Spanish "Resumen" section
- **AND** the abstract title is formatted at the same heading level as "Resumen"

#### Scenario: English abstract length
- **WHEN** counting the words in the English abstract (prose body, excluding LaTeX commands and the keywords line)
- **THEN** the word count is at most 250 words

#### Scenario: English abstract content accuracy
- **WHEN** reading the English abstract
- **THEN** it covers the thesis problem, methodology, key results, and conclusions
- **AND** all technical terms are consistent with the Spanish text (same classifier names, tool names, category strings)
- **AND** the key figures match those of the reduced Spanish "Resumen" (200 paired cases, 61.6~s to 17.76~s, 71.2~\% reduction, \(W = 363\), \(r = 0.9639\), 73.5~\% accuracy, threshold macro-F1 0.6508 over the four estimable classes, Cohen's Kappa 0.87)
- **AND** the five-class macro-F1 (0.5207), if cited, is labelled as including the non-estimable single-case class

### Requirement: Alineacion de la tesis con el corpus real de evaluacion

La tesis SHALL reportar los resultados experimentales sobre el corpus real de 200
casos pseudonimizados (`data/corpus_evaluacion_pseudonimizado.json`), no sobre el
corpus sintetico descartado en C-27. El Capitulo 7 SHALL reportar: la distribucion
por sector del corpus real (Sistemas 16, Soporte Tecnico Hardware 85, Soporte
Tecnico Software 67, Seguridad Informatica 31, Bases de Datos 1), los canales de
origen (correo 66, formulario web 53, llamada telefonica 81), la exactitud estricta
73,5 % (147/200), macro-F1 de umbral 0,6508 sobre las cuatro clases estimables (con
el de cinco clases, 0,5207, como valor informativo), micro-F1 0,6654, subset
accuracy 0,43, Hamming
loss 0,3586, las etapas deterministic 131 / Gemini 69, y la matriz de confusion 5x5
completa. El vocabulario de sectores reportado SHALL ser el conjunto canonico de
cinco categorias, SIN la categoria retirada "Operaciones". La tesis SHALL NOT
reportar como vigentes los valores del corpus sintetico (3 clases, distribucion
82/64/54, exactitud 92 %, F1 macro 0,919).

#### Scenario: Capitulo 7 reporta las metricas reales

- **WHEN** se lee el Capitulo 7 (Resultados) del PDF compilado
- **THEN** la exactitud reportada es 73,5 % (147/200) y el macro-F1 de umbral es 0,6508, con el de cinco clases (0,5207) rotulado como informativo
- **AND** la matriz de confusion reportada es 5x5 sobre las cinco categorias canonicas

#### Scenario: Categoria retirada ausente

- **WHEN** se busca "Operaciones" como sector en cualquier archivo `.tex` y en el PDF compilado
- **THEN** no aparece como categoria responsable, ni en la distribucion, ni en la matriz de confusion

#### Scenario: Distribucion por sector coincide con el reporte de evaluacion

- **WHEN** se compara la distribucion por sector reportada en la tesis con `evaluation/report.md`
- **THEN** coinciden en las cinco categorias (16/85/67/31/1)
- **AND** los canales de origen reportados coinciden (66/53/81)

### Requirement: Coherencia de los datos en los capitulos 7.2 y 1.6

La tesis SHALL reportar en el Capitulo 7.2 las metricas reales (exactitud 73,5 %,
macro-F1 de umbral 0,6508 sobre cuatro clases estimables, 0,5207 con las cinco
clases, y taxonomia de cinco clases) y SHALL corregir en el Capitulo 1.6 la mencion a
"tres sectores (Sistemas, Operaciones y Soporte Tecnico)" por las cinco categorias
canonicas, "Gemini 2.5 Flash" por `gemini-3.6-flash` y revisar la fecha "junio de
2026".

#### Scenario: 7.2 usa metricas reales

- **WHEN** se lee el Capitulo 7.2
- **THEN** reporta exactitud 73,5 %, macro-F1 de umbral 0,6508 (con el de cinco clases, 0,5207, rotulado) y la taxonomia de cinco clases
- **AND** no reporta 92 %, 0,919 ni tres clases

#### Scenario: 1.6 sin tres sectores ni modelo stale

- **WHEN** se lee el Capitulo 1.6 (alcance y delimitaciones)
- **THEN** menciona las cinco categorias canonicas y no "tres sectores" con "Operaciones"
- **AND** el modelo declarado es `gemini-3.6-flash`, no "Gemini 2.5 Flash"

### Requirement: Declaración del estado de la hipótesis principal

El resumen, la discusión y las conclusiones SHALL declarar el estado de la
hipótesis principal como parcialmente confirmada y parcialmente refutada: se
confirma en la reducción del tiempo de registro y se refuta en el umbral de
clasificación (`73,5 %` de exactitud y macro-F1 de umbral `0,6508` sobre las cuatro
clases estimables, por debajo de `85 %` y `0,85`). El resumen MUST NOT permitir inferir una confirmación plena de la
hipótesis. La declaración SHALL distinguir las sub-hipótesis de tiempo,
intervención humana y exactitud o F1. La sub-hipótesis de intervención humana
SHALL declararse **no contrastada por ausencia de registro primario**, de forma coherente con
la retirada del `9,5 %` (c-107); el documento MUST NOT reintroducir esa cifra ni
presentarla como resultado. Las conclusiones SHALL declarar el estado por
sub-hipótesis: confirmada en tiempo, refutada en clasificación e intervención
humana no contrastada por ausencia de registro primario, junto con el estado de las
dos hipótesis subsidiarias.

#### Scenario: Estado parcial declarado en el resumen

- **WHEN** se lee el resumen en español y el abstract
- **THEN** se declara que la hipótesis principal se confirma en tiempo y se refuta en clasificación
- **AND** no se presenta el umbral de clasificación como alcanzado

#### Scenario: Estado parcial declarado en discusión y conclusiones

- **WHEN** se leen la discusión y las conclusiones
- **THEN** el estado de la hipótesis principal se declara parcialmente confirmado y parcialmente refutado
- **AND** la refutación se ancla en las métricas de clasificación reportadas

#### Scenario: Sub-hipótesis de intervención humana declarada no medida

- **WHEN** se lee el estado de la hipótesis principal en el resumen y las conclusiones
- **THEN** la sub-hipótesis de intervención humana se declara no contrastada por ausencia de registro primario
- **AND** no se reporta el `9,5 %` de intervención humana como resultado vigente

#### Scenario: Estado por sub-hipótesis en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** se distingue explícitamente la sub-hipótesis confirmada (tiempo), la refutada (exactitud/F1) y la no contrastada (intervención humana)
- **AND** no se declara la hipótesis principal confirmada o refutada como bloque
- **AND** se declara el estado de las dos hipótesis subsidiarias

### Requirement: Presupuesto de palabras del resumen en español

El resumen en español (`00-resumen.tex`) SHALL tener como máximo 250 palabras de
prosa. La reducción SHALL conservar el problema, el método y diseño (200 casos
pareados), los resultados clave (61,6~s a 17,76~s, reducción del 71,2~\%, \(W =
363\), \(r = 0,9639\), exactitud 73,5~\%, macro-F1 de umbral 0,6508 sobre las cuatro clases
estimables, Kappa de Cohen 0,87) y
la conclusión. El resumen MUST NOT reintroducir valores retirados por c-107 (la
intervención humana del 9,5~\% y el universo calendario 3.700) ni presentar la
hipótesis principal como plenamente confirmada. Si el resumen cita el macro-F1 de
cinco clases (0,5207), SHALL acompañarlo de su aclaración.

#### Scenario: Longitud del resumen
- **WHEN** se cuenta el número de palabras de prosa del cuerpo del resumen en español (excluyendo comandos LaTeX y la línea "Palabras clave")
- **THEN** el conteo es como máximo 250 palabras

#### Scenario: Cifras clave conservadas
- **WHEN** se lee el resumen reducido
- **THEN** aparecen 200 casos, 61,6~s, 17,76~s, 71,2~\%, \(W = 363\), \(r = 0,9639\), 73,5~\% y 0,6508 rotulado como macro-F1 de umbral
- **AND** el resumen no presenta la hipótesis principal como plenamente confirmada
- **AND** si aparece 0,5207, lo acompaña su aclaración

#### Scenario: Sin valores retirados
- **WHEN** se busca "9,5 %" o "3.700" en el resumen y el abstract
- **THEN** no aparecen como resultado vigente
- **AND** el texto es coherente con los valores canónicos propagados por c-107
