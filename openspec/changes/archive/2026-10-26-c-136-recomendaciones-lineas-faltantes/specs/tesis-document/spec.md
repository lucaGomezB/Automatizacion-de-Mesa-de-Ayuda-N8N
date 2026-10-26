## ADDED Requirements

### Requirement: Subseccion de calibracion del gate de confianza en el capitulo de recomendaciones

El capitulo de recomendaciones (`10-recomendaciones.tex`) SHALL incluir una subseccion propia para la calibracion del gate de confianza, rotulada `subsec:calibracion-gate` y ubicada antes de la subseccion del clasificador supervisado. La subseccion SHALL enunciar un diagnostico coherente con el analisis de calibracion por etapa del capitulo de resultados: el gate de 0,70 solo aplica a la etapa Gemini y a la etapa de reserva, la etapa deterministica se gobierna por su propio score de correctitud y la confianza autodeclarada de Gemini no discrimina aciertos de errores en su rango efectivo (0,85 a 1,00). La subseccion SHALL proponer: un conjunto de validacion propio disjunto del corpus de evaluacion; al menos tres senales independientes del puntaje, entre ellas la ambiguedad lexica entre categorias candidatas, el margen entre la primera y la segunda categoria y la revision por muestreo de casos de alta confianza; una recalibracion posterior del puntaje, declarando que corrige su nivel pero no crea capacidad de discriminacion; y la derivacion del umbral del gate a partir de una curva de cobertura y precision ajustada fuera de la muestra, con un criterio declarado de antemano, como el punto de operacion de la etapa deterministica. El texto MUST NOT reintroducir la "calibracion invertida" del clasificador en su conjunto, MUST NOT presentar la propuesta como resultado y MUST NOT agregar entradas a `Bibliography_base.bib`.

#### Scenario: Subseccion presente y ubicada entre las prioritarias

- **WHEN** se inspecciona `10-recomendaciones.tex`
- **THEN** existe una `\subsection` con `\label{subsec:calibracion-gate}`
- **AND** ese rotulo aparece antes de `\label{subsec:clasificador-supervisado}`

#### Scenario: Diagnostico coherente con la calibracion por etapa

- **WHEN** se compara la subseccion con el analisis de calibracion del capitulo de resultados
- **THEN** la falta de discriminacion se atribuye a la confianza autodeclarada de Gemini en su rango efectivo y no al clasificador en su conjunto
- **AND** el gate de 0,70 se describe como aplicable solo a la etapa Gemini y a la etapa de reserva

#### Scenario: Propuesta con senales independientes, recalibracion y umbral derivado

- **WHEN** se lee la propuesta de la subseccion
- **THEN** figuran el conjunto de validacion propio disjunto del corpus de evaluacion, al menos tres senales independientes del puntaje y una recalibracion posterior con la advertencia de que no crea capacidad de discriminacion
- **AND** el umbral del gate se deriva de una curva de cobertura y precision ajustada fuera de la muestra, con un criterio declarado de antemano

#### Scenario: Sin bibliografia nueva desde este change

- **WHEN** se compara `Bibliography_base.bib` antes y despues del change
- **THEN** no hay entradas nuevas atribuibles a este change
- **AND** toda cita de la subseccion apunta a una entrada existente o incorporada por el change dueno de la bibliografia, y `verify_citations.py` reporta PASS

### Requirement: Subseccion de correccion de la medicion de intervencion humana

El capitulo de recomendaciones SHALL incluir una subseccion propia, rotulada `subsec:medicion-intervencion` y ubicada inmediatamente despues de la subseccion del clasificador supervisado, que proponga un protocolo de registro primario de la intervencion humana por caso. El protocolo SHALL registrar, para cada intervencion, su ocurrencia y origen, la consigna de tiempo de inicio y de fin, el resultado (categoria confirmada o corregida) y el operador seudonimizado, y SHALL indicar como almacenamiento la ampliacion de `clasificacion_log` o una tabla dedicada vinculada al incidente. La definicion operacional SHALL alinearse con las dos formas rotuladas de la variable de intervencion humana de `tab:variables` y aplicarse de igual modo en ambos brazos, de modo que la sub-hipotesis de intervencion, hoy no contrastada por ausencia de registro primario, pueda contrastarse en una replicacion. La subseccion MUST NOT reportar ninguna proporcion de intervencion humana como resultado.

#### Scenario: Subseccion presente a continuacion del clasificador supervisado

- **WHEN** se inspecciona `10-recomendaciones.tex`
- **THEN** existe una `\subsection` con `\label{subsec:medicion-intervencion}`
- **AND** es la subseccion inmediatamente posterior a `subsec:clasificador-supervisado`

#### Scenario: Protocolo de registro primario por caso

- **WHEN** se lee la subseccion
- **THEN** el protocolo enumera la ocurrencia y el origen de la intervencion, la consigna de tiempo de inicio y de fin, el resultado y el operador seudonimizado
- **AND** indica como almacenamiento la ampliacion de `clasificacion_log` o una tabla dedicada vinculada al incidente

#### Scenario: Definicion alineada con la tabla de variables y contrastabilidad

- **WHEN** se compara la subseccion con `tab:variables` y con la sub-hipotesis de intervencion de `subsec:hipotesis-trabajo`
- **THEN** la definicion operacional usa las mismas dos formas rotuladas (proporcion de casos y proporcion del tiempo del proceso) aplicadas a ambos brazos
- **AND** la subseccion explica que registro permitiria contrastar la sub-hipotesis en la formulacion vigente

#### Scenario: Sin proporcion de intervencion reportada

- **WHEN** se buscan en el capitulo de recomendaciones cifras de proporcion de intervencion humana
- **THEN** no aparece ninguna presentada como resultado
- **AND** no aparece el 9,5 % retirado

### Requirement: Aprendizaje activo condicionado a la calibracion de la confianza

La subseccion de aprendizaje activo (`subsec:aprendizaje-activo`) SHALL NOT proponer la priorizacion de casos por baja confianza declarada como criterio incondicional. SHALL apoyar la seleccion de casos en las senales independientes del puntaje de `subsec:calibracion-gate` y SHALL condicionar el uso de la confianza declarada como criterio de prioridad a una recalibracion validada segun esa subseccion. El texto MUST NOT presuponer que el gate deriva casos a revision. El rotulo `subsec:aprendizaje-activo` SHALL conservarse y la subseccion de base de conocimientos SHALL seguir remitiendo a el.

#### Scenario: Criterio de seleccion independiente del puntaje

- **WHEN** se lee la subseccion de aprendizaje activo
- **THEN** remite con `\autoref` a `subsec:calibracion-gate`
- **AND** la baja confianza declarada no figura como criterio de prioridad sin la condicion de una recalibracion validada

#### Scenario: Sin presuponer derivaciones del gate

- **WHEN** se lee la subseccion de aprendizaje activo
- **THEN** no afirma que la intervencion humana ocurre en los casos derivados a revision por el gate
- **AND** las revisiones que alimentan el ajuste incremental se vinculan con el registro de `subsec:medicion-intervencion`

#### Scenario: Remision de la base de conocimientos preservada

- **WHEN** se lee la subseccion de base de conocimientos
- **THEN** sigue remitiendo con `\autoref` a `subsec:aprendizaje-activo`
- **AND** el rotulo `subsec:aprendizaje-activo` se conserva sin cambios

### Requirement: Replicaciones con exactitud del flujo manual y asignacion muestral no proporcional

La subseccion de estudios de replicacion (`subsec:estudios-replicacion`) SHALL recomendar medir la exactitud del flujo manual sobre el mismo corpus, con etiquetadores distintos de los operadores del brazo manual, y SHALL recomendar una asignacion muestral no proporcional que sobremuestree las clases minoritarias y pondere las estimaciones globales por la distribucion del universo. La subseccion SHALL conservar su rotulo y los contextos de replicacion que ya enuncia.

#### Scenario: Exactitud del flujo manual con etiquetadores independientes

- **WHEN** se lee la subseccion de estudios de replicacion
- **THEN** recomienda medir la exactitud del flujo manual sobre el mismo corpus
- **AND** exige que los etiquetadores de la referencia sean distintos de los operadores del brazo manual

#### Scenario: Asignacion no proporcional ponderada

- **WHEN** se lee la subseccion de estudios de replicacion
- **THEN** recomienda sobremuestrear las clases minoritarias y ponderar las estimaciones globales por la distribucion del universo
- **AND** si menciona la clase Bases de Datos, lo hace con el soporte canonico de un caso

#### Scenario: Rotulo y contextos preservados

- **WHEN** se inspecciona la subseccion de estudios de replicacion
- **THEN** conserva `\label{subsec:estudios-replicacion}`
- **AND** mantiene los contextos de replicacion del sector publico, del sector industrial y de organizaciones de mayor tamano

### Requirement: Correspondencia entre el parrafo de priorizacion y las subsecciones del capitulo

El parrafo introductorio del capitulo de recomendaciones SHALL referenciar con `\autoref` la subseccion propia de cada linea anunciada como prioritaria (calibracion del gate de confianza, clasificador supervisado con corpus propio y correccion de la medicion de intervencion humana), y cada una de esas lineas SHALL existir como `\subsection` con `\label`. Las tres subsecciones prioritarias SHALL preceder al resto de las subsecciones del capitulo. El parrafo SHALL clasificar cada subseccion del capitulo en un nivel de prioridad, y su remision al analisis de errores SHALL apuntar a `subsec:analisis-errores`. El capitulo MUST NOT anunciar una linea prioritaria sin desarrollo propio.

#### Scenario: Cada linea prioritaria tiene subseccion

- **WHEN** se extraen los `\autoref` del parrafo introductorio y los `\label` de las subsecciones del capitulo
- **THEN** `subsec:calibracion-gate`, `subsec:clasificador-supervisado` y `subsec:medicion-intervencion` aparecen en ambos conjuntos
- **AND** no queda ninguna linea anunciada como prioritaria sin subseccion propia

#### Scenario: Orden de las subsecciones prioritarias

- **WHEN** se comparan las posiciones de los rotulos de subseccion en `10-recomendaciones.tex`
- **THEN** los tres rotulos prioritarios aparecen antes que cualquier otro rotulo de subseccion del capitulo

#### Scenario: Todas las subsecciones clasificadas y remision correcta

- **WHEN** se compara el parrafo introductorio con la lista de subsecciones del capitulo
- **THEN** cada subseccion figura en uno de los niveles de prioridad enunciados
- **AND** la remision al analisis de errores apunta a `subsec:analisis-errores` y no a `subsec:calibracion`

### Requirement: Destino de las referencias anticipadas al capitulo de recomendaciones

Toda remision a `sec:recomendaciones` desde otro capitulo que anuncie una evolucion o un trabajo futuro SHALL encontrar esa linea mencionada en el capitulo de recomendaciones. En particular, la calibracion de los parametros de inferencia, la autenticacion unica corporativa (SSO), el prefijo configurable del numero de incidente y la migracion a Kubernetes SHALL figurar en el capitulo.

#### Scenario: Referencias anticipadas con destino

- **WHEN** se listan las remisiones a `sec:recomendaciones` en los demas archivos de `paper/sections/`
- **THEN** cada tema anunciado por esas remisiones aparece en `10-recomendaciones.tex`
- **AND** ninguna remision queda sin una linea correspondiente en el capitulo

### Requirement: Neutralidad numerica de las lineas de trabajo futuro

El texto nuevo o reescrito del capitulo de recomendaciones SHALL limitarse a valores numericos que ya figuran en el documento o que tienen estado `vigente` en `docs/Tesis/Correcciones/numeros-canonicos.md`: el umbral del gate (0,70), el rango efectivo de confianza de Gemini (0,85 a 1,00), el umbral del 85 % del segundo objetivo especifico, el tamano del corpus (200 casos), el soporte de un caso de Bases de Datos y los valores que el capitulo ya contenia antes del change. El texto MUST NOT reintroducir cifras con estado `retirado` ni introducir valores sin procedencia.

#### Scenario: Cifras del texto agregado en la lista blanca

- **WHEN** se extraen los numeros de las lineas agregadas o reescritas en `10-recomendaciones.tex`
- **THEN** cada uno figura en la lista de valores admitidos o tiene estado `vigente` en `numeros-canonicos.md`
- **AND** ninguna cifra con estado `retirado` reaparece en el capitulo

### Requirement: Impacto de paginas acotado del capitulo de recomendaciones

Tras el change, el capitulo de recomendaciones SHALL ocupar a lo sumo cinco paginas del PDF compilado (cuatro en la release v1.1.1), medidas como la diferencia entre la pagina de inicio de las referencias bibliograficas y la pagina de inicio del capitulo en `main.toc`. El crecimiento SHALL compensarse dentro del capitulo condensando las subsecciones del agente conversacional telefonico y de la base de conocimientos, sin perder los elementos exigidos por los requisitos vigentes ni los elementos tecnicos de la justificacion del agente. El delta de paginas medido SHALL registrarse para la verificacion global del change de integracion.

#### Scenario: Extension del capitulo acotada

- **WHEN** se compila el PDF tras el change y se leen en `main.toc` las paginas de inicio del capitulo y de las referencias bibliograficas
- **THEN** la diferencia es de cinco paginas o menos
- **AND** el delta respecto de la release v1.1.1 queda registrado en la entrada de trazabilidad del change

#### Scenario: Condensacion sin perdida de elementos exigidos

- **WHEN** se leen las subsecciones condensadas
- **THEN** la del agente conversacional conserva Twilio Media Streams, la madurez de las interfaces de audio bidireccional, la transcodificacion mu-law a PCM, la gestion de turnos de habla, el modelo de costo por minuto y la recomendacion de una prueba de concepto con la grabacion actual como respaldo
- **AND** la de base de conocimientos conserva al menos dos parrafos, los ejemplos de incidentes simples, las remisiones a aprendizaje activo y a modelos abiertos y la ausencia de citas

#### Scenario: Partes protegidas sin cambios

- **WHEN** se compara el capitulo con su version previa al change
- **THEN** el primer parrafo de `subsec:panel-monitoreo` y el texto de `subsec:clasificador-supervisado` no fueron modificados por este change
- **AND** `subsec:evaluacion-modelos-abiertos` conserva su contenido
