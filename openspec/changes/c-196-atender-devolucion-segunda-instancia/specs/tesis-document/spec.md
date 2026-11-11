## MODIFIED Requirements

### Requirement: Verificacion de integridad y atribucion bibliografica (B1-B3)

La tesis SHALL sostener, tras las ramas posteriores que editan los sitios de cita, las correcciones bibliograficas B1-B3 aplicadas por c-78: la atribucion correcta de Revina, Buza & Meister (2020) sin BERT ni una exactitud cercana al 91 %; la cobertura de al menos 12 articulos arbitrados publicados entre 2023 y 2026; la atribucion de los rangos interpretativos de Kappa a Landis & Koch (1977); y la higiene de citas (cero citas huerfanas, cero entradas sin usar y toda entrada resoluble por DOI o landing de editorial). El documento MUST NOT reintroducir las citas fabricadas Karchhud et al. (2024) ni Mehdi et al. (2023).

#### Scenario: Atribucion de Revina sin BERT ni 91 %

- **WHEN** se buscan "BERT" y "91" junto a las menciones de Revina et al. (2020) en `03-estado-del-arte.tex` y `08-discusion.tex`
- **THEN** no se atribuye a ese articulo el uso de BERT ni de modelos preentrenados
- **AND** no se le atribuye una exactitud cercana al 91 %
- **AND** la entrada citada conserva la clave correcta (`Revina2020_it_tickets`)

#### Scenario: Cobertura 2023-2026 sostenida

- **WHEN** se cuentan las entradas arbitradas del `.bib` con ano entre 2023 y 2026
- **THEN** son al menos 12 y siguen presentes las claves incorporadas por B2
- **AND** cada una es verificable por DOI o URL de editorial/ACL Anthology

#### Scenario: Kappa atribuido a Landis & Koch

- **WHEN** se leen los pasajes que interpretan el coeficiente Kappa en `04-marco-metodologico.tex`
- **THEN** los rangos interpretativos se atribuyen a Landis & Koch (1977)
- **AND** el rotulo se aplica al kappa de 0,5569 ("moderado") y el `κ = 0,87` no se rotula ni se presenta como evidencia de fiabilidad

#### Scenario: Cero citas huerfanas y cero entradas sin usar

- **WHEN** se cruzan todas las claves citadas contra `Bibliography_base.bib`
- **THEN** no hay citas huerfanas ni entradas sin usar
- **AND** toda entrada resuelve por DOI o landing de editorial

#### Scenario: Sin citas fabricadas

- **WHEN** se buscan las claves `Karchhud2024` y `Mehdi2023` en el arbol de la tesis
- **THEN** no aparecen ni en `Bibliography_base.bib` ni en ningun `.tex`

### Requirement: Intervalos de confianza del kappa y por clase en la tesis

El marco metodologico y el capitulo de resultados SHALL reportar la incertidumbre del
acuerdo inter-evaluador y los intervalos de confianza de las metricas por clase
(precision, sensibilidad, F1), declarando el nivel de confianza y el procedimiento de
estimacion. El kappa `0,87` del doble etiquetado original MUST NOT presentarse como evidencia
de fiabilidad ni recibir un intervalo; su unica mencion en el cuerpo (4.4) declara que
sus planillas no se conservaron (devolucion del tribunal del 11-11-2026, N-01). El kappa de la campaña de medición
SHALL reportarse como un valor distinto ("fiabilidad del doble etiquetado de la campaña
de medición", etiquetadores `E1` y `E2`, `n` casos, etiqueta primaria, cinco clases, no
ponderado), con su intervalo asintótico (varianza de Fleiss, Cohen y Everitt, 1969) y
su intervalo bootstrap percentil (`B = 2000`, semilla `20261021`), `p_o`, `p_e` y PABAK,
y con su propio rótulo de Landis y Koch derivado del valor puntual, señalando si el
intervalo abarca dos categorías; si c-167 declara el intervalo no estimable (`p_e = 1`
o remuestras degeneradas), la tesis SHALL declararlo así sin fabricar un intervalo. El
documento SHALL declarar como no estimable la clase con soporte unitario (`Bases de
Datos`, `n = 1`) y SHALL excluirla del macro-F1 de umbral, conservando el macro-F1 de
cinco clases como valor informativo.

#### Scenario: IC del kappa reportado

- **WHEN** se lee el pasaje del doble etiquetado en metodologia, resultados o discusion
- **THEN** el kappa `0,87` no figura como evidencia ni con intervalo; solo 4.4 lo menciona para declarar que sus planillas no se conservaron
- **AND** el kappa de la campaña de medicion figura, con `n`, etiquetadores `E1`/`E2`, intervalo asintotico e intervalo bootstrap con semilla, o con la declaracion de intervalo no estimable, y con su propio rotulo de Landis y Koch

#### Scenario: Intervalo que abarca dos categorias

- **WHEN** el intervalo del kappa de la campaña de medicion cruza un limite de los rangos de Landis y Koch
- **THEN** el texto rotula el kappa por su valor puntual y declara que el intervalo abarca dos categorias
- **AND** no presenta el rotulo puntual como certeza

#### Scenario: IC por clase reportado

- **WHEN** se lee la tabla de metricas por clase en resultados
- **THEN** cada clase estimable reporta su IC de precision, sensibilidad y F1
- **AND** la clase `Bases de Datos` figura como no estimable y sin IC

#### Scenario: Exclusion de la clase no estimable del umbral

- **WHEN** se lee el macro-F1 asociado al umbral de clasificacion
- **THEN** el macro-F1 de umbral se reporta sobre las cuatro clases estimables (`0,6508`)
- **AND** el macro-F1 de cinco clases (`0,5207`) se conserva como valor informativo
- **AND** el `0,0000` de `Bases de Datos` no se presenta como evidencia de desempeno

### Requirement: Presupuesto de palabras del resumen en español

El resumen en español (`00-resumen.tex`) SHALL tener como máximo 250 palabras de
prosa. La reducción SHALL conservar el problema, el método y diseño (200 casos
pareados), los resultados clave (61,6~s a 17,76~s, reducción del 71,2~\%, \(W =
363\), \(r = 0,9639\), exactitud 73,5~\%, macro-F1 de umbral 0,6508 sobre las cuatro clases
estimables, kappa del doble etiquetado independiente 0,5569 con su IC [0,4725; 0,6413]) y
la conclusión. El resumen MUST NOT reintroducir valores retirados por c-107 (la
intervención humana del 9,5~\% y el universo calendario 3.700) ni presentar la
hipótesis principal como plenamente confirmada. El resumen y el abstract MUST NOT
informar el kappa de 0,87 del doble etiquetado original (devolución del tribunal del
11-11-2026, N-01). Si el resumen cita el macro-F1 de
cinco clases (0,5207), SHALL acompañarlo de su aclaración.

#### Scenario: Longitud del resumen
- **WHEN** se cuenta el número de palabras de prosa del cuerpo del resumen en español (excluyendo comandos LaTeX y la línea "Palabras clave")
- **THEN** el conteo es como máximo 250 palabras

#### Scenario: Cifras clave conservadas
- **WHEN** se lee el resumen reducido
- **THEN** aparecen 200 casos, 61,6~s, 17,76~s, 71,2~\%, \(W = 363\), \(r = 0,9639\), 73,5~\% y 0,6508 rotulado como macro-F1 de umbral
- **AND** el resumen no presenta la hipótesis principal como plenamente confirmada
- **AND** si aparece 0,5207, lo acompaña su aclaración
- **AND** figura 0,5569 con su IC y no figura 0,87

#### Scenario: Sin valores retirados
- **WHEN** se busca "9,5 %" o "3.700" en el resumen y el abstract
- **THEN** no aparecen como resultado vigente
- **AND** el texto es coherente con los valores canónicos propagados por c-107

### Requirement: Subseccion de resultados de la campaña de medicion

El capitulo de resultados (`07-resultados.tex`, Seccion 8) SHALL incluir una
subseccion nueva, con `\label{subsec:resultados-campana-medicion}`, que reporte como
conjunto de datos adicional, rotulado con su fecha y su configuracion (Anexo B), los
resultados de la campaña de medicion: fiabilidad del doble etiquetado (kappa con
intervalo), exactitud del brazo manual, intervencion humana, efecto de orden y
validacion fuera de muestra, cada uno con el estado que fijen las salidas de c-167.
La subseccion SHALL declarar que sus valores no reemplazan los valores canonicos
vigentes de la campaña 2026-10 (`61,6 s`, `17,76 s`, `W = 363`, `73,5 %`, `0,6508`)
y SHALL citar solo valores registrados en el memo canonico. Como el
documento ya llama "campañas" a las corridas manual y automatizada de 2026 (cronograma
`docs/diagrams/cronograma.md`, `fig:cronograma`), la tesis SHALL definir una sola vez,
en 4.2 (`subsec:diseno-experimental`), una denominacion distintiva para la campaña de
medicion de este programa (por ejemplo, "campaña complementaria de medición") y SHALL
usarla de forma uniforme en todos los capitulos, el resumen y el abstract.

#### Scenario: Subseccion presente y rotulada

- **WHEN** se inspecciona `07-resultados.tex`
- **THEN** existe una `\subsection` con `\label{subsec:resultados-campana-medicion}` que declara fecha, configuracion y `n` de la campaña de medicion
- **AND** cada valor que cita figura en `numeros-canonicos.md` con estado `vigente` o `condicional`

#### Scenario: Denominacion distintiva de la campaña

- **WHEN** se buscan en `sections/*.tex` las menciones de la campaña de medicion de este programa
- **THEN** todas usan la denominacion definida en `subsec:diseno-experimental`
- **AND** ninguna se confunde con las campañas manual y automatizada de 2026 del cronograma

#### Scenario: Valores canonicos vigentes intactos

- **WHEN** se comparan las cifras de la campaña 2026-10 en el PDF antes y despues de aplicar el change
- **THEN** `61,6 s`, `17,76 s`, `W = 363`, `73,5 %` y `0,6508` no cambian de valor ni de estado
- **AND** el kappa `0,87` no figura en 8.7 (retirado como evidencia, devolucion del 11-11-2026, N-01)
- **AND** ningun valor de la campaña de medicion se presenta como sustituto de esas cifras

#### Scenario: Tiempos de la campaña de medicion acotados al efecto de orden

- **WHEN** la subseccion cita tiempos del brazo manual medidos en la campaña de medicion
- **THEN** los presenta rotulados con su campaña, como insumo del efecto de orden y en la tabla `tab:tiempos-manual-complementaria` (devolucion del 11-11-2026, N-03)
- **AND** el contraste por operador usa el automatizado de la corrida de la campaña complementaria y no el `17,76 s`, y no reemplaza el contraste de Wilcoxon principal

### Requirement: Reducción sin pérdida de contenido científico

La reducción de páginas SHALL preservar la integridad científica del documento.
El change MUST NOT eliminar ni alterar: contenido científico (afirmaciones,
argumentos, interpretaciones y análisis), las figuras y tablas requeridas por el
conjunto de changes (incluidas las ocho figuras de c-80 y las tablas con su línea
de fuente), los números canónicos (exactitud 73,5 %, macro-F1 0,5207, reducción
71,2 %, W=363, r=0,9639, universo 2.646, horas-persona 32,2 h), ni las
referencias bibliográficas. El κ = 0,87 dejó de ser número canónico: se retiró como evidencia de fiabilidad (devolución del tribunal del 11-11-2026, N-01). Las palancas admisibles son de forma: pasajes
duplicados, leyendas sobre-extendidas, listas redundantes, tamaño del glosario,
espaciado y compactación de anexos. La reduccion SHALL organizarse en tres fases: **Fase A** (forma), que puede reubicar figuras del cuerpo en el Anexo A con precedente documentado (c-139), reemplazar un flotante `[p]` por `[htbp]` cuando la tabla quepa en el texto, y compactar los `Overfull \hbox` mayores a 10pt; **Fase B** (de-duplicacion), que reemplaza pasajes repetidos por una remision `\autoref` a su seccion primaria sin perder la afirmacion original; y **Fase C** (condensacion de los capitulos 4 y 6), que SHALL aplicarse solo con decision explicita del autor. Una reubicacion a un anexo MUST conservar la figura, su pie y su fuente, y actualizar el inventario del anexo y el indice de figuras. Las siguientes palancas estan PROHIBIDAS: alterar el interlineado o los margenes del preambulo (APA 7 y 2,54~cm estan congelados; la palanca P8 no se aplica), reducir la fuente de la bibliografia (ya esta en `\footnotesize`) y retirar los `\newpage` de capitulo.

#### Scenario: Cifras canónicas intactas

- **WHEN** se busca en el PDF reducido cada número canónico (73,5 %, 0,5207, 71,2 %, W=363, 0,9639, 2.646, 32,2 h)
- **THEN** todos siguen presentes con el mismo valor
- **AND** no se introducen cifras nuevas ni se retiran las existentes

#### Scenario: Figuras y tablas requeridas preservadas

- **WHEN** se inspecciona el PDF reducido
- **THEN** las ocho figuras y las nueve tablas del change set siguen renderizando
- **AND** ninguna figura o tabla requerida fue eliminada ni recortada

#### Scenario: Correcciones previas no revertidas

- **WHEN** se compara el manuscrito reducido contra la versión de partida
- **THEN** las correcciones de c-102..c-115 (números canónicos, cifras retiradas, acentuación, orden de capítulos, glosario y marco teórico) permanecen aplicadas
- **AND** no se reintroduce ningún valor retirado (9,5 %, 3.700, "Operaciones", W=0)

#### Scenario: Reubicacion a anexo preserva figura y remision

- **WHEN** una figura del cuerpo se mueve al Anexo A (por ejemplo `fig:componentes` o `fig:secuencia`)
- **THEN** la figura, su pie y su fuente siguen presentes en el Anexo A
- **AND** el inventario del Anexo A, el indice de figuras y toda remision del cuerpo a la figura quedan actualizados y resueltos
- **AND** la `\autoref` que la referenciaba sigue dando un destino valido

#### Scenario: De-duplicacion conserva la afirmacion primaria

- **WHEN** un pasaje repetido en otro capitulo se reemplaza por `\autoref` a su seccion primaria
- **THEN** la afirmacion, el numero canonico y la cita siguen presentes en la seccion primaria
- **AND** ningun pasaje queda huerfano sin su remision ni se pierde informacion no repetida en la seccion primaria

#### Scenario: Palancas prohibidas no aplicadas

- **WHEN** se revisa el diff del change
- **THEN** el preambulo no cambia su interlineado (sigue `\doublespacing`) ni sus margenes (siguen 2,54~cm)
- **AND** la fuente de la bibliografia no baja de su valor vigente (`\footnotesize`)
- **AND** ningun `\newpage` de capitulo fue retirado

#### Scenario: Fase C solo con decision del autor

- **WHEN** se revisa el diff del change respecto de los capitulos 4 y 6
- **THEN** cualquier condensacion de esos capitulos esta respaldada por una decision explicita y registrada del autor
- **AND** sin esa decision, los capitulos 4 y 6 permanecen sin cambios

### Requirement: Verificabilidad del muestreo y de la asignacion por sector

La descripcion del muestreo en `04-marco-metodologico.tex` SHALL ser verificable con la informacion que el documento aporta y SHALL nombrarlo como muestreo no probabilistico por conveniencia (devolucion del tribunal del 11-11-2026, N-04). Si la distribucion del universo por sector esta disponible, la tesis SHALL reportarla junto a la distribucion de la muestra para que la proporcionalidad sea comprobable. Si no esta disponible, la tesis SHALL declarar que la composicion por sector de la muestra refleja la distribucion observada en el periodo relevado y que su proporcionalidad respecto del universo no es verificable, y MUST NOT afirmar una proporcionalidad respecto del universo que el documento no permite comprobar. En ambos casos la tesis SHALL discutir la consecuencia de la asignacion resultante para Bases de Datos (`n = 1`, clase no estimable) y la alternativa de una asignacion no proporcional con sobremuestreo de las clases minoritarias para replicaciones. El resumen y el abstract MUST describir el muestreo de forma coherente con el capitulo 4.

#### Scenario: Universo por sector disponible

- **WHEN** el autor aporta la distribucion del universo por sector
- **THEN** el capitulo 4 la reporta junto a la distribucion muestral (85/67/31/16/1)
- **AND** cada cifra nueva figura en `numeros-canonicos.md` con su procedencia

#### Scenario: Universo por sector no disponible

- **WHEN** la distribucion del universo por sector no esta disponible
- **THEN** el capitulo 4 declara que la composicion de la muestra refleja la distribucion observada en el periodo relevado y que la proporcionalidad frente al universo no es verificable
- **AND** el texto no afirma un muestreo proporcional al universo sin respaldo

#### Scenario: Asignacion de Bases de Datos discutida

- **WHEN** se lee la descripcion del muestreo
- **THEN** se explica que la asignacion dejo a Bases de Datos con un unico caso, no estimable para la inferencia por clase
- **AND** se menciona la asignacion no proporcional con sobremuestreo de clases minoritarias como alternativa para replicaciones

#### Scenario: Resumen y abstract coherentes

- **WHEN** se comparan `00-resumen.tex` (resumen y abstract) con el capitulo 4
- **THEN** la caracterizacion del muestreo es la misma en los tres lugares
- **AND** el abstract no conserva "stratified sampling" y nombra la muestra por conveniencia ("convenience sample")

### Requirement: Cuerpo de la tesis sin residuos del proceso de correccion del manuscrito

Las secciones del cuerpo de la tesis (`docs/Tesis/v10 (IA)/paper/sections/00-*.tex` a `11-*.tex`) SHALL describir el estudio y el sistema en su estado vigente y MUST NOT narrar la historia de revision del manuscrito: cifras previas retiradas, estimaciones de versiones anteriores del texto, formulaciones anteriores de hipotesis, umbrales o ramas del diseno retirados presentados como antecedente, ni afirmaciones sobre la estabilidad de los valores del registro canonico. En particular, el cuerpo MUST NOT contener la nota sobre la "cifra previa de 180 horas-persona" (9.1), la estimacion "entre veinte y treinta veces superior" al precio de lista (9.4), la oracion sobre el reemplazo del umbral de 0,90 del diseno inicial (5.5), la frase de que la rama de clasificacion basada en LangChain "fue retirada" (6.3), la narracion de la formulacion original de la segunda sub-hipotesis (1.4), la frase "Ningún valor canónico cambia" (8.5) ni la afirmacion de que la cobertura real del gate es menor que la que sugiere la proporcion de casos escalados (9.1). Cada texto retirado SHALL conservarse literal, con su ubicacion previa, en `docs/Tesis/Correcciones/dictamen-correcciones.md`; los que documentan decisiones de diseno del sistema (c-72, c-74 y c-82) SHALL figurar ademas en el parrafo de decisiones del Anexo I. La descripcion de la configuracion vigente en cada corrida de la campana (procedencia de los datos en 4.5 y tabla de configuracion evaluada frente a entregada), incluidos el cortocircuito por confianza de la version `hybrid-v1` y el agente LLM de N8N de la clasificacion telefonica previa a c-72, describe el estudio y no constituye un residuo en el sentido de este requisito. La discusion del gate en 9.1 SHALL declarar que en el corpus la regla de 0,70 no derivo ningun caso, porque los 124 casos con confianza registrada inferior a 0,70 pertenecen a la etapa deterministica, a la que la regla no se aplica, y la etapa Gemini nunca declaro una confianza inferior a 0,85. Las correcciones MUST NOT cambiar ningun valor numerico. Son excepcion a este requisito las declaraciones de procedencia que exige la devolucion del tribunal del 11-11-2026, siempre breves y con remision a la nota de versiones del Anexo I (`subsec:nota-versiones`): la declaracion de 4.4 de que las planillas del kappa de 0,87 no se conservaron y que ese valor no se presenta como evidencia (N-01), y la declaracion de 1.4 y 8.3 de que el denominador de 147 casos y la lectura de la regla de la segunda sub-hipotesis se fijaron despues de conocer los datos (N-09). La historia de las versiones del manuscrito se narra solo en el Anexo I.

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

#### Scenario: Declaraciones de procedencia acotadas

- **WHEN** se buscan menciones de versiones anteriores del manuscrito en `paper/sections/0*.tex` a `11-*.tex`
- **THEN** solo aparecen las de 4.4 (kappa de 0,87) y las de 1.4 y 8.3 (lectura posterior de la regla)
- **AND** cada una remite a `subsec:nota-versiones` o al Anexo I

#### Scenario: Residuos trasladados al registro

- **WHEN** se lee la seccion del dictamen del 2026-10-28 de c-160 en `docs/Tesis/Correcciones/dictamen-correcciones.md`
- **THEN** figuran los siete textos retirados, literales, con su archivo y linea previos y su destino
- **AND** el parrafo de decisiones del Anexo I menciona c-72, c-74 y c-82

### Requirement: Fuente de la interpretacion del coeficiente Kappa

El documento SHALL atribuir los rangos interpretativos del coeficiente Kappa a Landis & Koch (1977) y no a Cohen (1960). El rotulo interpretativo SHALL aplicarse al kappa del doble etiquetado independiente de la campaña complementaria (\(\kappa = 0{,}5569\), "moderado"), que es el que la tesis presenta como estimacion de la fiabilidad de la referencia, en la seccion de metodologia (4.4) y en la de amenazas a la validez (4.8). El valor \(\kappa = 0{,}87\) del doble etiquetado original MUST NOT rotularse ni presentarse como evidencia de fiabilidad (devolucion del tribunal del 11-11-2026, N-01).

#### Scenario: Landis y Koch citados para los rangos
- **WHEN** se lee el pasaje que interpreta el valor de Kappa en 4.4 o en 4.8
- **THEN** los rangos de interpretacion se atribuyen a Landis & Koch (1977)
- **AND** existe una entrada `Landis1977_kappa` en `Bibliography_base.bib` con DOI 10.2307/2529310
- **AND** Cohen (1960) permanece citado solo por la definicion del coeficiente

#### Scenario: Rotulo del kappa vigente
- **WHEN** se lee la interpretacion del kappa en 4.4 y 4.8
- **THEN** el rotulo "moderado" acompaña al 0,5569
- **AND** el 0,87 no lleva rotulo "casi perfecto" ni se presenta como respaldo de la fiabilidad

### Requirement: Declaracion del intervalo de confianza del kappa

La tesis SHALL tratar por separado los dos coeficientes kappa. El kappa `0,87` del doble
etiquetado original MUST NOT presentarse como evidencia de fiabilidad: sus planillas no se
conservaron y el valor ya figuraba en la version de julio de 2026, antes de que existiera el
corpus real. El cuerpo SHALL mencionarlo una sola vez, en 4.4 (`subsec:poblacion-muestra-corpus`),
para declarar que las planillas no se conservaron, que el valor informado en versiones anteriores
no puede respaldarse con registros y que por eso no se presenta como evidencia, con remision a la
nota de versiones del Anexo I (`subsec:nota-versiones`); la tesis MUST NOT fabricar ni estimar un
intervalo para el `0,87` ni presentar el intervalo del kappa nuevo como si fuera el del `0,87`. El
kappa de la campaña de medicion SHALL calcularse por c-167 sobre
`evaluation/data/campana/doble_etiquetado.csv` (tabla versionada con SHA-256) y reportarse con su
intervalo asintotico y su intervalo bootstrap con semilla fija declarada, o con la declaracion de
intervalo no estimable. La decision y los valores SHALL quedar registrados en el memo canonico
(`docs/Tesis/Correcciones/numeros-canonicos.md`) y en el diseno del cambio.

#### Scenario: Tabla recuperable

- **WHEN** la tabla primaria del doble etiquetado de la campaña de medicion esta versionada en `evaluation/data/campana/doble_etiquetado.csv` con su SHA-256
- **THEN** la tesis reporta el kappa de la campaña de medicion con su intervalo asintotico y su intervalo bootstrap, declarando metodo y semilla, o declara el intervalo no estimable si c-167 asi lo informa

#### Scenario: Kappa original retirado como evidencia

- **WHEN** se busca `0{,}87` o `0,87` referido al kappa en `sections/*.tex`
- **THEN** aparece una sola vez, en 4.4, junto a la declaracion de que sus planillas no se conservaron y de que no se presenta como evidencia
- **AND** no se fabrica ni se estima un intervalo para el `0,87`
- **AND** el pasaje remite a `subsec:nota-versiones`

### Requirement: Fiabilidad de la referencia de verdad discutida

La tesis SHALL reportar en el resumen y el abstract el kappa del doble etiquetado independiente
de la campaña complementaria (0,5569; moderado; IC del 95 % [0,4725; 0,6413]; tabla primaria
conservada con SHA-256) y MUST NOT informar el 0,87 del doble etiquetado original (devolucion del
11-11-2026, N-01). La seccion 9.4 (`08-discusion.tex`, limitaciones) SHALL incluir una limitacion
sobre la fiabilidad de la referencia de verdad de las metricas primarias, con la concordancia del
consenso `E1 = E2` con la referencia original (116 de 138, 84,1 %), y SHALL declarar que el doble
etiquetado original no conserva registro y no permite contraste. La segunda contribucion de 10.2
(`09-conclusiones.tex`, "doble etiquetado") SHALL matizarse con el kappa moderado de la campaña
complementaria. El capitulo 10 SHALL incluir una conclusion sobre el kappa moderado y sobre el
efecto de posicion significativo para `O2`.

#### Scenario: Kappa nuevo en el resumen

- **WHEN** se lee el resumen y el abstract
- **THEN** figura 0,5569 con su rotulo moderado y su IC [0,4725; 0,6413]
- **AND** no figura el 0,87

#### Scenario: Limitacion de la referencia en 9.4

- **WHEN** se leen las limitaciones de la discusion (9.4)
- **THEN** una limitacion declara la fiabilidad moderada de la referencia nueva y la concordancia de 116 de 138 (84,1 %) con la referencia original
- **AND** declara que las metricas primarias se calculan contra la referencia original y heredan su incertidumbre
- **AND** declara que el doble etiquetado original no conserva registro, sin citar el 0,87

#### Scenario: Contribucion matizada y conclusiones completas

- **WHEN** se lee el capitulo 10
- **THEN** la segunda contribucion menciona el kappa moderado de la campaña complementaria
- **AND** el capitulo concluye sobre el efecto de posicion significativo para `O2`

### Requirement: Atribucion separada del kappa de 1.6 y del doble etiquetado de la campana

La introduccion (`01-introduccion.tex`, contribuciones y alcance) SHALL atribuir el acuerdo
moderado de 0,5569 (`p_o = 0,69`; `p_e = 0,30`) al doble etiquetado independiente de la campaña
complementaria realizado por `E1` y `E2`. La introduccion MUST NOT informar el 0,87 del doble
etiquetado original (devolucion del 11-11-2026, N-01); el unico pasaje del cuerpo que lo menciona
es 4.4. La tesis MUST NOT atribuir el 0,5569 al par analista externo + analista autor ni presentar
ambos valores como el mismo acuerdo. La descripcion MUST NOT incluir datos personales: solo
codigos y roles.

#### Scenario: Atribucion del kappa nuevo

- **WHEN** se lee la introduccion y se comparan sus menciones con 4.4, 8.7 y 9.3
- **THEN** el 0,5569 figura atribuido al par `E1`/`E2`
- **AND** ningun pasaje atribuye el 0,5569 al par autor/analista
- **AND** la introduccion no contiene el 0,87

### Requirement: Estado de la segunda sub-hipotesis coherente con la variable medida

El estado de la segunda sub-hipotesis SHALL quedar fijado como "no concluyente, con estimación
puntual por encima de la cota" (devolucion del tribunal del 11-11-2026, N-09), con el denominador
de los casos que tuvieron oportunidad de revision humana. El texto SHALL declarar la estimacion de
25 de 147 casos revisados (17,0 %; IC de Wilson [11,8 %; 23,9 %]), que el intervalo contiene 0,15
y que la prueba binomial contra 0,15 da p = 0,28 UNILATERAL (H1: proporcion > 0,15; 0,49
bilateral). El texto SHALL declarar en 1.4 (`subsec:hipotesis-trabajo`) y en 8.3
(`subsec:reduccion-intervencion`) que la eleccion del denominador de 147 casos revisados y la
lectura de la regla se fijaron despues de conocer los datos, y que la aplicacion prefijada al
denominador de 200 (25 de 200, 12,5 %; IC [8,6 %; 17,8 %]) daba tambien "no concluyente". El texto
MUST NOT declarar refutada la segunda sub-hipotesis ni reducir el matiz a "un valor cercano al
umbral". El texto SHALL declarar que la revision humana de la campaña complementaria alcanzo solo
los canales de correo (66) y telefonia (81) por la regla de derivacion por reportante no
identificado, y que los 53 casos del formulario web no tuvieron revision. Las confirmaciones SHALL
informarse con ambos denominadores explicitos: 122 de 200 (61,0 %) y 122 de 147 (83,0 %); MUST NOT
quedar un "122 (61,0 %)" adyacente al denominador de 147 que pueda leerse como 122 de 147. Ese
estado SHALL ser identico donde el veredicto se enuncia: el resumen y el abstract, 1.4, 4.7, 8.3,
9.1, el capitulo 10 (incluida la Tabla 18, `tab:cumplimiento-objetivos`, filas del objetivo
general y del objetivo especifico 4), el capitulo 11 y el Anexo I (que puede narrar que una
version intermedia la declaro refutada). El conteo de sub-hipotesis SHALL ser: una corroborada
(tiempo), una no concluyente (intervencion humana) y una refutada (exactitud y macro-F1). La
seccion 8.3 MUST NOT contener "Medirla en condiciones validas": la limitacion de la revision SHALL
expresarse como condicion de generalizacion, con remision a `subsec:medicion-intervencion`. El
resumen (`00-resumen.tex`) y el abstract MUST NOT superar 250 palabras cada uno.

#### Scenario: Veredicto unico de la sub-hipotesis 2

- **WHEN** se comparan el resumen, el abstract, 1.4, 4.7, 8.3, 9.1, el capitulo 10, la Tabla 18, el capitulo 11 y el Anexo I
- **THEN** todos declaran la sub-hipotesis 2 "no concluyente, con estimación puntual por encima de la cota" con 25 de 147
- **AND** ninguno la declara refutada como estado vigente
- **AND** la tercera sub-hipotesis sigue declarada refutada

#### Scenario: Lectura posterior y p unilateral declaradas

- **WHEN** se leen 1.4 y 8.3
- **THEN** ambas declaran que el denominador de 147 y la lectura de la regla se fijaron despues de conocer los datos
- **AND** `07-resultados.tex` y `08-discusion.tex` califican p = 0,28 como unilateral

#### Scenario: Condicion de generalizacion en 8.3

- **WHEN** se busca "Medirla en condiciones válidas" en `07-resultados.tex`
- **THEN** no hay coincidencias
- **AND** 8.3 declara que extender la conclusion al formulario web y a reportantes identificados exige una corrida con revision en todos los canales

#### Scenario: Denominadores del 122 explicitos

- **WHEN** se lee la oracion de las confirmaciones en 8.3
- **THEN** figura 122 de 200 (61,0 %) y 122 de 147 (83,0 %) con ambos denominadores explicitos

#### Scenario: Alcance de la revision declarado

- **WHEN** se lee 8.3
- **THEN** se declara que la revision humana alcanzo 66 casos de correo y 81 de telefonia y ninguno de los 53 del formulario web

#### Scenario: Conteo de sub-hipotesis

- **WHEN** se busca un conteo del tipo "dos de las tres sub-hipótesis" en `sections/*.tex`
- **THEN** no quedan conteos que sumen dos refutadas
- **AND** el estado se enuncia como una corroborada, una no concluyente y una refutada

### Requirement: Propagacion del dictamen sobre v1.2.16 en el metodo, los resultados y el memo

La seccion 4.2 (`04-marco-metodologico.tex`, protocolo de medicion en vivo) SHALL declarar que,
por el cronometraje mutuo de los pares de la campana 2026-10, el observador de `A1` fue `T1`,
autor del trabajo, lo que debilita la atenuacion del efecto Hawthorne atribuida a `A1`. La
seccion 8.7 (`07-resultados.tex`, "Exactitud del brazo manual") SHALL declarar que
`predicciones_in_sample.json` y `predicciones_hybrid-v3_2026-10-07.json` contienen las mismas 200
predicciones. `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar el estado de la
segunda sub-hipotesis como "no concluyente, con estimación puntual por encima de la cota" (25/147
= 0,170; Wilson [0,118; 0,239]; binomial p = 0,28 unilateral; 25/200 = 0,125 como aplicacion al
denominador prefijado), con la nota de que c-190 la habia declarado refutada y c-196 la corrige;
SHALL describir el conjunto laxo del brazo manual por la INTERSECCION de los adicionales (130/151;
la union daria 137) y SHALL conservar la fila del MDE del Spearman y las huellas SHA-256 vigentes.

#### Scenario: Observador de A1 declarado

- **WHEN** se lee el protocolo de medicion en vivo de 4.2
- **THEN** figura que el observador de `A1` fue el autor `T1` y que eso debilita la atenuacion del efecto Hawthorne

#### Scenario: Caches identicas declaradas

- **WHEN** se lee el parrafo "Exactitud del brazo manual" de 8.7
- **THEN** declara que las dos caches del 7-10 contienen las mismas 200 predicciones

#### Scenario: Memo con el estado vigente

- **WHEN** se buscan en `numeros-canonicos.md` el estado de la segunda sub-hipotesis y la definicion del laxo manual
- **THEN** el estado vigente es "no concluyente, con estimación puntual por encima de la cota" y "refutada" figura solo como estado superado
- **AND** "unión" no figura como criterio del laxo

### Requirement: Formulaciones residuales del dictamen sobre v1.2.16

La seccion 8.3 SHALL presentar la regla de derivacion por reportante no identificado como
requisito de la especificacion de visibilidad de incidentes (`VIS-005`), de modo que el lector no
dependa de un identificador interno sin explicar, y MUST NOT nombrar el identificador del change
que la introdujo (devolucion del 11-11-2026, N-07). La introduccion del capitulo 11
(`10-recomendaciones.tex`) SHALL describir el estado de la segunda sub-hipotesis con el veredicto
vigente y MUST NOT decir que la campaña complementaria refuto la medicion.

#### Scenario: VIS-005 presentado

- **WHEN** se lee la mencion de `VIS-005` en 8.3
- **THEN** figura como requisito de la especificacion de visibilidad de incidentes
- **AND** no figura `c-82`

#### Scenario: Capitulo 11 con el veredicto vigente

- **WHEN** se lee el primer parrafo de `sec:recomendaciones`
- **THEN** la segunda sub-hipotesis figura como no concluyente y no como refutada

### Requirement: Trazabilidad de los controles a los changes archivados

El mapeo del capitulo de cumplimiento SHALL vincular cada control implementado con el artefacto
versionado del repositorio que lo evidencia y con una remision unica al Anexo I
(`sec:anexo-trazabilidad`), donde consta el change archivado que lo cerro. El cuerpo del capitulo
(`11-aspectos-legales.tex`) MUST NOT nombrar identificadores de cambio (`C-61` a `C-66`,
`C-63a/b`, `C-156`, `c-165` a `c-168`) ni la palabra "changes" (devolucion del 11-11-2026, N-07).
Las brechas residuales de tipo organizacional SHALL declararse como responsabilidad de la
organizacion adoptante, fuera del alcance del repositorio.

#### Scenario: Controles trazables sin identificadores en el cuerpo

- **WHEN** se lee la hoja de ruta del capitulo de cumplimiento
- **THEN** los controles cerrados se asocian a su artefacto y remiten al Anexo I
- **AND** `rg -n "\b[cC]-[0-9]{2,3}[ab]?\b|changes" 11-aspectos-legales.tex` no devuelve coincidencias fuera de comentarios

#### Scenario: Brechas organizacionales atribuidas al adoptante

- **WHEN** se leen las brechas residuales del capitulo
- **THEN** las de tipo organizacional (personas 6.x, fisicos 7.x, revision independiente) se declaran responsabilidad de la organizacion adoptante
- **AND** no se presentan como controles implementados en el repositorio

### Requirement: Coherencia de los nombres de sector con su definicion canonica

En la prosa, los nombres de sector SHALL escribirse con tilde ("Seguridad Informática", "Soporte
Técnico Hardware", "Soporte Técnico Software"); donde la tesis cita la cadena exacta del sistema
(tablas de datos, matriz de confusion, prompt, definicion del string del clasificador) SHALL
escribirse en monoespaciado y sin tilde (`\texttt{Seguridad Informatica}`), coincidiendo byte a
byte con `App/Backend/app/constants.py` (devolucion del 11-11-2026, N-15). La convencion y los
pasajes afectados SHALL constar en el registro de la revision. Las ocurrencias de las cinco
cadenas canonicas en codigo, prompt y datos MUST NOT alterarse, y ningun reemplazo SHALL hacerse a
ciegas.

#### Scenario: Prosa con tilde

- **WHEN** se buscan "Seguridad Informatica", "Soporte Tecnico Hardware" y "Soporte Tecnico Software" fuera de `\texttt{}` en `paper/sections/*.tex`
- **THEN** no quedan ocurrencias en prosa

#### Scenario: Cadena del sistema en monoespaciado

- **WHEN** se lee un pasaje que cita la cadena exacta del clasificador
- **THEN** la cadena va en `\texttt{}` y coincide byte a byte con una de las cinco cadenas canonicas
- **AND** el registro de la revision consigna la convencion y la lista de pasajes

## ADDED Requirements

### Requirement: Regla de tres vias con lectura posterior declarada

Donde se define la regla de tres vias de la segunda sub-hipotesis, en 1.4
(`01-introduccion.tex`, `subsec:hipotesis-trabajo`) y en 4.7 (`04-marco-metodologico.tex`,
parrafo "Analisis de la campana complementaria de medicion"), el texto SHALL distinguir la regla
prefijada y su aplicacion al denominador prefijado (25 de 200: no concluyente) de la eleccion
posterior del denominador de 147 casos revisados y de la lectura de la regla, ambas fijadas
despues de conocer los datos. Con 147, el texto SHALL aplicar la lectura estadistica: el intervalo
de Wilson [11,8 %; 23,9 %] contiene 0,15 y la estimacion puntual (17,0 %) queda por encima, por lo
tanto el veredicto es "no concluyente, con estimación puntual por encima de la cota". El texto
MUST NOT definir "refutada" como una estimacion puntual que alcanza la cota, porque esa lectura
convierte en refutacion un resultado cuyo intervalo incluye la cota. La redaccion exacta de la
regla en 1.4 y 4.7 SHALL ser la que confirme el orquestador (design de c-196, D-N09).

#### Scenario: Regla y lectura posterior en la definicion

- **WHEN** se leen las definiciones de la regla de tres vias en 1.4 y en 4.7
- **THEN** ambas distinguen la aplicacion prefijada (200) de la lectura posterior (147)
- **AND** ninguna define "refutada" por la sola estimacion puntual que alcanza la cota

#### Scenario: Resumen dentro del tope

- **WHEN** se cuentan las palabras de `00-resumen.tex` con la regla registrada (c-106)
- **THEN** el resumen y el abstract tienen a lo sumo 250 palabras cada uno

### Requirement: Nota de versiones y trazabilidad de la auditoria del tribunal en el Anexo I

El Anexo I (`sec:anexo-trazabilidad`, `12-anexos.tex`) SHALL comenzar con una subseccion breve
"Nota de versiones" con `\label{subsec:nota-versiones}`, de media pagina como maximo, que declare
que la version del 3 de julio de 2026 informo una reduccion del tiempo medio de 165,3 s a 18,2 s
(89,0 %), exactitud de 92 %, W = 0 y κ = 0,87; que los tiempos, la exactitud y el estadistico
provenian de un corpus sintetico de 200 casos generado durante el desarrollo, descartado y
eliminado del repositorio; que la version actual los reemplaza por los del corpus real
pseudonimizado (61,6 s a 17,76 s, 71,2 %; 73,5 %; W = 363); y que el κ = 0,87 figuraba en esa
version, sus planillas no se conservan y ya no se presenta como evidencia. La nota MUST NOT
afirmar que el 0,87 provenia del corpus sintetico. La trazabilidad SHALL tener como primera fila o
bloque la auditoria integral del tribunal del 4 de agosto de 2026 (105 hallazgos, 28 criticos,
3,9/10; archivo en `auditorias/`), que origino la reformulacion con datos reales, y SHALL
distinguir (a) esa auditoria, (b) las nueve autoevaluaciones internas generadas con un modelo de
lenguaje y (c) la devolucion de segunda instancia del tribunal del 11 de noviembre de 2026. El
Anexo I SHALL cerrar con la tabla `tab:trazabilidad-devolucion-segunda-instancia` con una fila por
observacion N-01 a N-16 (observacion en 4 a 8 palabras, seccion corregida con `\autoref`, estado
"Atendida", "Atendida en parte; resta dato de los autores" o "Pendiente"), sin numeros de linea.
La confirmacion escrita del consentimiento (A1) SHALL figurar como atendida el 10 de noviembre de
2026, segun `docs/campana-medicion/confirmacion-posterior-consentimiento.md`.

#### Scenario: Nota de versiones presente

- **WHEN** se buscan "sintétic", "subsec:nota-versiones" y "165,3" en `12-anexos.tex`
- **THEN** cada busqueda devuelve al menos una coincidencia
- **AND** la nota no atribuye el 0,87 al corpus sintetico

#### Scenario: Auditoria del 4 de agosto como primera fila

- **WHEN** se lee la trazabilidad del Anexo I
- **THEN** la primera fila o bloque es la auditoria del tribunal del 4 de agosto de 2026
- **AND** la serie distingue la auditoria, las autoevaluaciones con modelo de lenguaje y la devolucion del 11-11

#### Scenario: Tabla de la devolucion

- **WHEN** se compila y se lee el Anexo I
- **THEN** figura `tab:trazabilidad-devolucion-segunda-instancia` con N-01 a N-16 y sus `\autoref` resueltos
- **AND** N-16 figura "Pendiente"; N-01, N-02, N-04, N-05 y N-13 "Atendida en parte; resta dato de los autores"; el resto "Atendida"

#### Scenario: Consentimiento actualizado

- **WHEN** se busca "diferida" referido a A1 en `12-anexos.tex`
- **THEN** no hay coincidencias
- **AND** A1 figura atendida el 10 de noviembre de 2026

### Requirement: Tiempos manuales de la campana complementaria por operador

La seccion 8.7 (`07-resultados.tex`, `subsec:resultados-campana-medicion`) SHALL incluir el
parrafo "Tiempos del brazo manual por operador" y la tabla `tab:tiempos-manual-complementaria`
con, por fila (O1, O2 y agregado por caso), casos, media y desvio manual, mediana manual, media
automatizada de los mismos casos, reduccion, p de Wilcoxon pareado y r rank-biserial: O1 110,
20,1 s (9,2), 18,0 s, 13,3 s, 33,8 %, 9,8 × 10⁻⁷, 0,54; O2 110, 76,6 s (21,4), 73,0 s, 15,5 s,
79,7 %, 9,0 × 10⁻²⁰, 1,00; agregado 200, 47,6 s (28,7), 49,0 s, 14,6 s, 69,3 %, 3,0 × 10⁻²⁸,
0,90; con fuente (elaboracion propia sobre `brazo_manual.csv` y `corpus_campana.json`). El texto
SHALL declarar que el automatizado es el de la corrida de la campaña complementaria (no el 17,76 s
canonico), el registro de 0 s (R025, O1; sin el, 20,3 s y 34,3 %), los 20 casos de doble cobertura
(20,1 s O1 y 92,8 s O2), las correlaciones de Spearman entre campañas (0,15 y −0,05 para el manual;
0,70 para el automatizado), que esos tiempos miden la decision de sector y no reemplazan el
contraste principal, y que el 69,3 % agregado es del mismo orden que el 71,2 %. La seccion 4.5
(`subsec:protocolo-pruebas`) SHALL definir la tarea manual de la campaña complementaria y declarar
que difiere de la de la campaña 2026-10. La seccion 9.1 (`subsec:interpretacion-resultados`) SHALL
agregar la dependencia del operador como explicacion rival (33,8 % a 79,7 %), con el conteo de
rivales actualizado. Cada cifra SHALL figurar en `numeros-canonicos.md`.

#### Scenario: Tabla y remisiones

- **WHEN** se busca `tab:tiempos-manual-complementaria` en `07-resultados.tex` y `04-marco-metodologico.tex`
- **THEN** aparece el `\label` en 8.7 y al menos una remision en 8.7 y otra en 4.5
- **AND** la tabla contiene 76,6 y 20,1 con sus filas

#### Scenario: Tareas distintas declaradas

- **WHEN** se lee 4.5
- **THEN** la tarea manual de la campaña complementaria se define como la decision de sector y se declara distinta de la de la campaña 2026-10

#### Scenario: Dependencia del operador como rival

- **WHEN** se lee 9.1
- **THEN** figura la dependencia del operador como explicacion rival con el rango de 33,8 % a 79,7 %

### Requirement: Registro primario de los tiempos automatizados declarado

La seccion 4.5 (`04-marco-metodologico.tex`) SHALL declarar que los 119 tiempos automatizados de
correo (66) y formulario (53) no tienen registro primario conservado, que constan solo como
valores del corpus versionado, que `data/corpus_resultados.json` corresponde a otra corrida y no
los respalda, y que los 81 telefonicos coinciden con su registro
(`data/corpus_resultados_telefonia.json`). La seccion 8.1 (`07-resultados.tex`) SHALL declarar,
donde presenta la comparacion de tiempos, que la media automatizada combina 81 tiempos con
registro primario y 119 sin el, con remision a `subsec:protocolo-pruebas`. El Anexo F
(`sec:anexo-corpus`) MUST NOT contradecir esa declaracion. El origen de los 119 tiempos MUST NOT
redactarse como hecho mientras los autores no lo aporten.

#### Scenario: Declaracion en 4.5 y 8.1

- **WHEN** se busca "registro primario" en `04-marco-metodologico.tex` y en `07-resultados.tex`
- **THEN** hay al menos una coincidencia en cada archivo
- **AND** 4.5 lleva el marcador `PENDIENTE-AUTORES(N-05)`

### Requirement: Llamadas recitadas declaradas como amenaza y explicacion rival

La seccion 4.8 (`subsec:amenazas-validez`) SHALL incluir como amenaza a la validez que un autor
que conocia el caso y el sistema recito las 81 llamadas del canal telefonico parafraseando la
descripcion pseudonimizada, que un locutor asi habla mas claro y mas breve que un usuario real, lo
que favorece el tiempo medido, que hubo dos configuraciones (25 casos el 5-10 y 56 el 6-10) y la
version del dia 6 no consta, y que no se estimo la magnitud. El texto MUST NOT afirmar como hecho
que la recitacion favorecio la exactitud; SHALL decir que pudo favorecer la transcripcion y que aun
asi el canal obtuvo la exactitud mas baja. El conteo de amenazas SHALL actualizarse. La seccion
9.1 SHALL agregar la procedencia de las llamadas como explicacion rival y declarar que las cifras
telefonicas no se extrapolan a usuarios reales. Las conclusiones SHALL mencionar que el tiempo
telefonico se midio con llamadas recitadas.

#### Scenario: Recitacion en 4.8 y 9.1

- **WHEN** se busca "recit" en `04-marco-metodologico.tex` y en `08-discusion.tex`
- **THEN** hay al menos dos coincidencias en el primero y una en el segundo
- **AND** ninguna afirma como hecho que la recitacion mejoro la exactitud

### Requirement: Seleccion de los casos por conveniencia declarada

La seccion 4.4 (`subsec:poblacion-muestra-corpus`) SHALL describir una sola forma de seleccion de
los 200 casos: muestreo no probabilistico por conveniencia (disponibilidad), siendo los 200 casos
los incidentes cronometrados en la campaña manual; la formula de tamaño muestral SHALL informarse
como margen de error implicado y no como diseño. La tesis MUST NOT describir el corpus como
muestreo estratificado ni con asignacion proporcional en `04-marco-metodologico.tex`, el resumen,
el abstract ("convenience sample") ni la discusion. La seccion 4.8 SHALL incluir el sesgo de
seleccion como amenaza a la validez externa. Las fechas del periodo relevado y el criterio de
seleccion MUST NOT inventarse: quedan marcados `PENDIENTE-AUTORES(N-04)` hasta que los autores
los aporten.

#### Scenario: Una sola descripcion

- **WHEN** se busca "estratificad" o "stratified" en `00-resumen.tex`, `04-marco-metodologico.tex` y `08-discusion.tex`
- **THEN** no hay coincidencias afirmativas (una negacion explicita se cuenta aparte)
- **AND** 4.4 y el abstract nombran el muestreo por conveniencia

#### Scenario: Sesgo de seleccion en 4.8

- **WHEN** se lee `subsec:amenazas-validez`
- **THEN** figura el sesgo de seleccion como amenaza a la validez externa

### Requirement: Exactitud contra el consenso independiente en la tabla de exactitud

La Tabla 12 (`tab:exactitud-etapa-canal`, `07-resultados.tex`) SHALL incluir dos filas: "Casos con
consenso E1 = E2, referencia original" (109/138 = 0,790; Wilson [0,714; 0,850]; laxa 125/138 =
0,906 [0,846; 0,944]) y "Mismos casos, referencia de consenso E1 = E2" (110/138 = 0,797; Wilson
[0,722; 0,856]; laxa 117/138 = 0,848 [0,779; 0,898]), con nota sobre los 62 casos sin consenso
(38/62 = 0,613 contra el original) y sobre la definicion de la laxa contra el consenso. La seccion
8.2 SHALL explicarlas en pocas oraciones. El veredicto de la tercera sub-hipotesis SHALL
mantenerse sobre la referencia primaria prefijada (el etiquetado original), y el texto SHALL
declarar que, contra el consenso independiente, el limite superior del intervalo de la exactitud
(0,856) supera el umbral de 0,85 y con esa referencia el criterio de exactitud quedaria no
concluyente, mientras el macro-F1 (0,757) sigue por debajo del umbral. La seccion 9.3 SHALL
reflejarlo en una oracion.

#### Scenario: Filas nuevas en la Tabla 12

- **WHEN** se lee `tab:exactitud-etapa-canal`
- **THEN** figuran 110/138 con [0,722; 0,856] y 109/138 con [0,714; 0,850]
- **AND** `07-resultados.tex` contiene "0{,}856" o "0,856"

#### Scenario: Veredicto sobre la referencia primaria y transparencia

- **WHEN** se leen 8.2 y 9.3
- **THEN** la tercera sub-hipotesis sigue refutada sobre la referencia original
- **AND** se declara que contra el consenso el criterio de exactitud quedaria no concluyente

### Requirement: Cuerpo sin identificadores de cambio y con oraciones acotadas

Las fuentes `.tex` del cuerpo, sus tablas y sus epigrafes, fuera del Anexo I
(`sec:anexo-trazabilidad`), MUST NOT contener identificadores internos de cambio (`c-NNN`,
`C-NN`, `C-63a` y similares) ni la palabra "changes"; SHALL reemplazarlos por la descripcion de lo
que el cambio hizo o por una remision unica a `\autoref{sec:anexo-trazabilidad}` (devolucion del
11-11-2026, N-07). Los comentarios LaTeX (`%`) no cuentan. El contenido rasterizado de las figuras
queda fuera de este requisito, salvo en las figuras que el change regenera. Este requisito
prevalece sobre los requisitos anteriores que pedian nombrar un change en el cuerpo, una tabla o un
epigrafe fuera del Anexo I. Los capitulos 1, 4, 8 y 9 (`01-introduccion.tex`,
`04-marco-metodologico.tex`, `07-resultados.tex`, `08-discusion.tex`) MUST NOT contener oraciones
de mas de 60 palabras segun el script de conteo del change, salvo excepciones justificadas en el
registro (falsos positivos por notas al pie o tablas); partir una oracion MUST NOT cambiar cifras
ni citas.

#### Scenario: Sin identificadores fuera del Anexo I

- **WHEN** se ejecuta `rg -n -E "\b[cC]-[0-9]{2,3}[ab]?\b"` sobre `paper/sections/*.tex`, excluyendo comentarios y el rango del Anexo I
- **THEN** no hay coincidencias

#### Scenario: Oraciones acotadas

- **WHEN** se ejecuta el script de conteo de oraciones sobre 01, 04, 07 y 08
- **THEN** informa 0 oraciones de mas de 60 palabras o cada excepcion figura justificada en el registro

### Requirement: Cobertura del backend informada con su procedencia

La seccion 6.7 (`06-implementacion.tex`) SHALL informar la cobertura de sentencias de la suite
unitaria sobre rutas, servicios y repositorios con su valor, el commit y la fecha de la medicion,
y SHALL imprimir el mismo comando que ejecuta el CI (`pytest -m "not integration"
--cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing`). Si el
valor no se midio, el texto MUST NOT imprimir una cifra y SHALL dejar el marcador
`PENDIENTE-AUTORES(N-10)`. El valor SHALL registrarse en `numeros-canonicos.md`.

#### Scenario: Cobertura con valor y comando del CI

- **WHEN** se lee 6.7
- **THEN** figura el porcentaje con commit y fecha, y el comando incluye `-m "not integration"`
- **AND** el valor coincide con el registrado en `numeros-canonicos.md`

#### Scenario: Sin valor medido

- **WHEN** el orquestador no entrego el valor
- **THEN** 6.7 no contiene una cifra de cobertura del backend y lleva el marcador `PENDIENTE-AUTORES(N-10)`

### Requirement: Conclusiones sin valoraciones sin respaldo

El capitulo 10 (`09-conclusiones.tex`) MUST NOT contener valoraciones sin respaldo: "prácticamente
útil", "económicamente accesible", "mayor desafío técnico", "aisló la complejidad" ni "rasgo más
relevante". SHALL sintetizar sin repetir en la prosa las cifras del capitulo 8, que quedan en la
tabla de objetivos con remision `\autoref`. SHALL mencionar que el tiempo telefonico se midio con
llamadas recitadas (remision a `subsec:amenazas-validez`) y SHALL mantener el grado de
cumplimiento de cada objetivo con el estado vigente de cada sub-hipotesis.

#### Scenario: Valoraciones retiradas

- **WHEN** se buscan "prácticamente útil" y "económicamente accesible" en `09-conclusiones.tex`
- **THEN** no hay coincidencias

### Requirement: Instrumento del articulo 12 de la Ley 25.326 durante el estudio

La seccion 7.3 (`11-aspectos-legales.tex`) SHALL declarar que durante el estudio no se
suscribieron clausulas contractuales modelo (Disposicion 60-E/2016) ni se recabo consentimiento de
titulares para la transferencia internacional, que a los proveedores llegaron descripciones
pseudonimizadas como texto y como audio recitado por uno de los autores a partir de esas
descripciones, y que el instrumento queda como requisito previo del adoptante antes de operar con
datos reales. MUST NOT llamar "suscripto" a un acuerdo que no consta firmado; SHALL hablar de las
condiciones de servicio aceptadas. La confirmacion de los autores queda marcada
`PENDIENTE-AUTORES(N-13)`.

#### Scenario: Instrumento declarado

- **WHEN** se busca "no se suscribieron" o "no se celebr" en `11-aspectos-legales.tex`
- **THEN** hay al menos una coincidencia
- **AND** el instrumento figura como requisito del adoptante

### Requirement: Figuras legibles a tamano de impresion

Las Figuras 2, 7, 8 y 10 del PDF (numeracion de `v1.2.18`) SHALL regenerarse desde sus fuentes
versionadas en `docs/diagrams/*.md` de modo que su texto no quede por debajo de 6 puntos en A4,
mediante orientacion apaisada o division por capas. La integracion en los `.tex` SHALL hacerla el
grupo dueño del archivo y MUST NOT dejar referencias sin resolver.

#### Scenario: Texto legible

- **WHEN** se mide el tamaño de texto de las figuras regeneradas con el script de medicion del change
- **THEN** ningun rotulo queda por debajo de 6 pt a tamaño de impresion A4

### Requirement: Datos de los autores marcados y no redactados como hecho

Todo dato que solo los autores pueden aportar (origen y fecha del kappa de 0,87, periodo y
criterio de seleccion de los 200 casos, registro de los 119 tiempos automatizados, instrumentos
firmados con Google o Twilio, version leida de Mayor-Rocher et al. y copia de Paket et al.,
declaracion del uso de modelos de lenguaje en la redaccion) MUST NOT redactarse como hecho. SHALL
dejarse un comentario LaTeX `% PENDIENTE-AUTORES(N-xx): <qué falta>` en la linea anterior al
pasaje (en el `.bib`, en una linea propia antes de la entrada), y el texto visible SHALL quedar
verdadero sin ese dato. El registro (`dictamen-correcciones.md`) SHALL inventariar los marcadores.

#### Scenario: Inventario de marcadores

- **WHEN** se ejecuta `rg -n "PENDIENTE-AUTORES" "docs/Tesis/v10 (IA)/paper/sections" "docs/Tesis/v10 (IA)/Bibliography_base.bib"`
- **THEN** figuran al menos los marcadores N-01, N-02, N-04, N-05, N-13, N-16 y P16
- **AND** cada uno figura en el inventario del registro

### Requirement: Trazabilidad de la devolucion de segunda instancia en el registro

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion "Dictamen v10 /
v1.2.18 (2026-11-11) - c-196 (devolucion de segunda instancia)" con una matriz de 7 columnas (Rec | Sintesis |
Change | Archivo:linea | Ancla | Fragmento verificable | Estado) con una fila por N-01 a N-16,
fragmentos tomados del texto final y estado; las decisiones del design de c-196; el inventario de
`PENDIENTE-AUTORES`; y el libro mayor de paginas y palabras. Las filas de matrices anteriores cuyo
parrafo reescribe c-196 SHALL marcarse "SUPERADA por c-196". `verificar_matriz_trazabilidad.py`
SHALL reportar 0 fallas y la compilacion SHALL cumplir el requisito "Thesis PDF compilation" (0
errores, 0 referencias o citas indefinidas, `verify_citations.py` PASS, `compilacion.md` con el
SHA-256 del PDF).

#### Scenario: Matriz de c-196 verificada

- **WHEN** se ejecuta `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` desde la raiz
- **THEN** el resumen informa filas de la seccion de c-196 y 0 fallas

## REMOVED Requirements

### Requirement: Regla de tres vias declarada como asimetrica en su definicion

**Reason**: la devolucion de segunda instancia del tribunal del 11-11-2026 (N-09) observa que la
regla de decision de la segunda sub-hipotesis se fijo despues de ver los datos y que, con 25/147,
IC [11,8 %; 23,9 %] y p = 0,28 unilateral, la lectura estadistica correcta es "no concluyente con
estimacion puntual sobre la cota". Una regla que llama "refutada" a una estimacion puntual que
alcanza la cota contradice ese veredicto.
**Migration**: requisito "Regla de tres vias con lectura posterior declarada" (ADDED en c-196) y
requisito "Estado de la segunda sub-hipotesis coherente con la variable medida" (MODIFIED en c-196).
