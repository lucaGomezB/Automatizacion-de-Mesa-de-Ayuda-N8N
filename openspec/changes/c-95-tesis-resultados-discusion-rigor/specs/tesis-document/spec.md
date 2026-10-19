## ADDED Requirements

### Requirement: Reporte de normalidad Shapiro-Wilk

La tesis SHALL reportar de forma completa la prueba de normalidad que justifica
el uso de Wilcoxon. La Sección~4.7 MUST informar el estadístico \(W\) y el valor
\(p\) de Shapiro-Wilk para el flujo manual, el flujo automatizado y las
diferencias pareadas, con una precisión suficiente para reproducir el resultado.
La Sección~7.1 SHALL referenciar ese reporte al presentar la prueba de Wilcoxon.
`evaluation/report.md` MUST registrar los valores, el comando reproducible y la
identificación del corpus sobre el que se calcularon. Los valores MUST
recalcularse después de cualquier corrección del corpus que altere los tiempos,
en particular la corrección telefónica de c-77 (E3).

#### Scenario: Estadístico y p por grupo y por diferencias

- **WHEN** se lee la Sección~4.7 de la tesis
- **THEN** aparecen el estadístico \(W\) y el valor \(p\) de Shapiro-Wilk para el flujo manual, el flujo automatizado y las diferencias pareadas
- **AND** no se afirma únicamente "ambos grupos rechazan la normalidad con \(p < 0{,}01\)" sin reportar los valores

#### Scenario: Trazabilidad del cálculo

- **WHEN** se revisa `evaluation/report.md`
- **THEN** figuran los valores de \(W\) y \(p\), el comando o función reproducible que los generó y la identificación o hash del corpus usado
- **AND** los valores del reporte coinciden con los de la tesis

#### Scenario: Recalculo tras cambiar los tiempos del corpus

- **WHEN** c-77 modifica los tiempos automatizados telefónicos
- **THEN** los valores de Shapiro-Wilk se recalculan sobre el corpus corregido
- **AND** no se copian los valores calculados antes de esa corrección

### Requirement: Interrogación crítica de los resultados

El Capítulo~8 SHALL interrogar los resultados además de interpretarlos. La
Sección~8.1 MUST incluir una lectura crítica que explicite al menos tres
explicaciones rivales de la reducción del tiempo de registro, la evidencia
disponible a favor o en contra de cada una, la condición que permitiría
descartarla y el grado de incertidumbre que persiste. La lectura crítica MUST
explicar por qué la categoría Sistemas se confunde sistemáticamente con otras
categorías, apoyándose en la matriz de confusión 5x5 real y en las métricas por
clase. La interpretación MUST NOT presentar la hipótesis de trabajo como
confirmada de forma concluyente cuando las explicaciones rivales no puedan
descartarse.

#### Scenario: Explicaciones rivales presentes

- **WHEN** se lee la Sección~8.1
- **THEN** se identifican al menos tres explicaciones rivales de la reducción de tiempo (por ejemplo, asimetría del instrumento de medición, simplificación de la tarea o mezcla de canales, novedad o efecto Hawthorne, y selección de la muestra)
- **AND** por cada una se declara qué evidencia la sostiene o la debilita y qué observación permitiría descartarla

#### Scenario: Confusión de Sistemas explicada

- **WHEN** se lee la explicación de la confusión de la categoría Sistemas
- **THEN** la explicación se apoya en la matriz 5x5 y en las métricas por clase reales
- **AND** distingue la ambigüedad léxica o taxonómica de la falta de contexto en la descripción del incidente
- **AND** no se limita a atribuir el patrón a una limitación genérica del modelo

#### Scenario: Sin confirmación concluyente

- **WHEN** la Sección~8.1 evalúa la hipótesis de trabajo
- **THEN** el texto distingue entre resultados consistentes con la hipótesis y resultados que la confirman de forma concluyente
- **AND** no afirma que la hipótesis queda validada si alguna explicación rival permanece abierta

### Requirement: Trazabilidad y alcance del baseline TF-IDF+SVM

Toda comparación de la tesis contra un clasificador supervisado clásico SHALL ser
trazable o SHALL estar explícitamente acotada como exploratoria. Si se reporta un
resultado de TF-IDF+SVM, la tesis MUST documentar el procedimiento, la partición
de entrenamiento y evaluación, el tamaño \(n\) del subconjunto evaluado y la
ubicación del código o de los artefactos reproducibles. Si esos elementos no
están preservados, la cifra MUST retirarse como resultado y el chequeo MUST
declararse exploratorio, no reproducible y no comparable. En ningún caso la tesis
MUST afirmar una ganancia sustantiva sobre un baseline cuyos números no puedan
verificarse.

#### Scenario: Baseline documentado o acotado

- **WHEN** se lee la limitación sobre la comparación con clasificadores alternativos en la Sección~8.3
- **THEN** o bien se documentan procedimiento, partición, \(n\) y código/artefactos del baseline TF-IDF+SVM
- **AND** o bien se declara explícitamente que el chequeo fue exploratorio, que la partición y el \(n\) no se preservaron y que no se reporta como resultado comparable

#### Scenario: Sin cifras no verificables

- **WHEN** se busca en la tesis la exactitud del baseline y su F1 macro
- **THEN** no aparecen "78~%" ni "0,764" presentados como resultados si no existe el procedimiento y el artefacto que los respalde

#### Scenario: Sin afirmación de superioridad

- **WHEN** se lee la comparación del esquema híbrido con el baseline
- **THEN** no se afirma que el esquema propuesto "confirma" o "aporta" una ganancia sustantiva sobre el baseline
- **AND** la comparación se presenta como pendiente de una evaluación sistemática sobre el corpus completo

### Requirement: Evidencia textual anonimizada de errores

La Sección~7.4 SHALL incluir evidencia textual de los errores de clasificación,
no solo su tipificación agregada. MUST presentar entre dos y tres ejemplos de
incidentes mal clasificados, con el texto anonimizado de la descripción, el
sector asignado, el sector predicho y la confianza reportada. Los ejemplos MUST
provenir de `evaluation/predicciones.json` y MUST ser consistentes con la matriz
de confusión y la tipología de errores. La anonimización MUST preservar la
utilidad analítica del ejemplo sin exponer datos personales.

#### Scenario: Ejemplos textuales presentes

- **WHEN** se lee la Sección~7.4
- **THEN** aparecen entre dos y tres ejemplos de descripciones de incidentes mal clasificados
- **AND** cada ejemplo indica el sector asignado, el sector predicho y la confianza

#### Scenario: Consistencia con las predicciones

- **WHEN** se compara cada ejemplo con `evaluation/predicciones.json`
- **THEN** el par asignado/predicho y la confianza coinciden con el registro
- **AND** el ejemplo pertenece a uno de los patrones de error descritos en la tipología

#### Scenario: Anonimización suficiente

- **WHEN** se revisan los textos citados
- **THEN** no contienen nombres de personas, direcciones, correos, teléfonos ni identificadores internos que permitan reidentificación
- **AND** la descripción conserva el rasgo que explica el error

### Requirement: Fuentes y cotas de costos operativos

La Sección~8.4 SHALL sustentar las estimaciones económicas en fuentes
verificables o en cotas explícitas. El costo por invocación MUST citar la lista
de precios oficial del proveedor de inferencia, indicar el modelo y la fecha de
consulta, y declarar los supuestos de tokens por invocación. El costo de
infraestructura MUST citar una lista de precios pública de un proveedor
identificado o presentarse como una cota de orden de magnitud con la composición
de rubros y los supuestos de capacidad y horas de uso. No se admiten cifras
monetarias sin fuente ni rango declarado.

#### Scenario: Costo de inferencia con fuente

- **WHEN** se lee la estimación del costo por invocación en la Sección~8.4
- **THEN** se identifica el proveedor, el modelo y la lista de precios oficial consultada con su fecha
- **AND** se declaran los supuestos de tokens de entrada y salida usados para llegar al valor

#### Scenario: Costo de infraestructura con fuente o cota

- **WHEN** se lee la estimación del costo mensual de infraestructura
- **THEN** se identifica el proveedor y la lista de precios consultada, o se presenta una cota con los rubros incluidos (cómputo, almacenamiento, respaldo, transferencia)
- **AND** la estimación se declara como orden de magnitud y no como una cotización

#### Scenario: Sin cifras desnudas

- **WHEN** se busca en la Sección~8.4 "50--100 USD/mes" u "0,02 USD por invocación"
- **THEN** toda aparición está acompañada por la fuente o por la cota y los supuestos que la justifican
- **AND** no queda ninguna cifra monetaria sin respaldo

### Requirement: Delimitación de las afirmaciones del Capítulo 9

El Capítulo~9 SHALL limitarse a sintetizar resultados ya presentados y
argumentados en los capítulos precedentes. La Sección~9.1 MUST NOT introducir
interpretación estadística nueva, en particular la lectura de \(W=0\) como
resultado "poco frecuente" o que "merece interpretarse con cautela"; esa
interpretación corresponde al Capítulo~8 y la referencia a la prueba al
Capítulo~7. La Sección~9.2 MUST acotar cualquier afirmación general sobre el
desempeño de los LLM frente a clasificadores supervisados al corpus, al dominio y
al contraste efectivamente realizado, y MUST NOT presentarla como una conclusión
general del campo.

#### Scenario: Sin interpretación estadística nueva en Conclusiones

- **WHEN** se lee la Sección~9.1
- **THEN** no aparece la interpretación de \(W=0\) como resultado poco frecuente ni la recomendación de interpretarlo con cautela
- **AND** cualquier referencia a la prueba de Wilcoxon remite al Capítulo~7 o al Capítulo~8 sin repetir su interpretación

#### Scenario: Afirmación general acotada

- **WHEN** se lee la afirmación de la Sección~9.2 sobre LLM y clasificadores supervisados
- **THEN** la afirmación se limita al corpus, al dominio y al contraste disponible en este trabajo
- **AND** no se sostiene que los LLM invocados por instrucciones superen de forma general a los clasificadores supervisados clásicos sobre representaciones estáticas

#### Scenario: Coordinación sin reintroducir correcciones ajenas

- **WHEN** se aplica este change después de c-77 y c-78
- **THEN** no se reintroduce \(W=0\) ni la atribución corregida de Revina et al. (2020)
- **AND** la tensión de evidencia contraria que incorpora c-78 permanece en el Capítulo~8 sin duplicarse en el Capítulo~9
