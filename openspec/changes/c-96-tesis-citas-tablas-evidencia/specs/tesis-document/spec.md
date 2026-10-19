## ADDED Requirements

### Requirement: Fuente y trazabilidad de las tablas

Todas las tablas del documento SHALL declarar su fuente conforme al estilo APA~7,
ya sea como elaboracion propia ("Fuente: elaboracion propia") o como la
referencia de la que provienen los datos. La Tabla~1 del Capitulo~3
(`tab:comparativa`) SHALL ademas respaldar cada fila de solucion comercial con una
cita verificable, una linea de fuente y una fecha de consulta, y MUST NOT
autoevaluar la propuesta del trabajo dentro de la misma grilla comparativa.

#### Scenario: Linea de fuente en las nueve tablas
- **WHEN** se inspecciona cualquiera de las nueve tablas del documento (`tab:comparativa` en 03; `tab:variables` en 04; `tab:capas`, `tab:entidades` y `tab:api` en 05; `tab:tiempos`, `tab:matriz`, `tab:metricas` y `tab:errores` en 07)
- **THEN** cada tabla declara una linea de fuente APA~7 ("Fuente: elaboracion propia" o la referencia correspondiente)
- **AND** la linea de fuente no rompe la composicion de la tabla definida por c-80

#### Scenario: Tabla 1 con citas y fecha de consulta por fila
- **WHEN** se lee la Tabla~1 del Capitulo~3
- **THEN** cada fila de solucion comercial (Zendesk Suite, Freshdesk, Jira Service Management, ServiceNow ITSM, osTicket) tiene una cita verificable y una fecha de consulta asociada
- **AND** la tabla declara su linea de fuente

#### Scenario: Sin autoevaluacion en la grilla comparativa
- **WHEN** se lee la Tabla~1 del Capitulo~3
- **THEN** la fila "Propuesta" ya no se evalua con los mismos criterios que las soluciones de terceros dentro de la tabla
- **AND** la comparacion de la propuesta contra las soluciones comerciales se desarrolla en prosa con respaldo, no como autoevaluacion en la misma grilla

### Requirement: Atribucion de la definicion de empresa mediana y del marco etico

Las afirmaciones que atribuyen una definicion o un marco normativo a una fuente
externa SHALL citar esa fuente y contar con la entrada bibliografica
correspondiente. En particular, la definicion de empresa mediana atribuida a la
Secretaria de la Pequena y Mediana Empresa en la seccion 1.1 y la justificacion
etica del debriefing en la seccion 11.5 SHALL quedar respaldadas o reformuladas
sin atribucion.

#### Scenario: Definicion de empresa mediana con cita
- **WHEN** se lee la seccion 1.1 (`01-introduccion.tex`) donde se define a la empresa mediana por el rango de 50 a 200 trabajadores en el sector servicios
- **THEN** la afirmacion cita la Secretaria de la Pequena y Mediana Empresa (SEPyME)
- **AND** existe una entrada bibliografica correspondiente en `Bibliography_base.bib`
- **AND** no queda una atribucion a una fuente sin cita ni entrada

#### Scenario: Cita huerfana del marco etico resuelta
- **WHEN** se busca la cita "(APA, 2017)" en la seccion 11.5 (`11-aspectos-legales.tex`)
- **THEN** la cita fue resuelta: o existe la entrada `APA2017` en `Bibliography_base.bib`, o la cita fue retirada y el argumento se sostiene sin ella
- **AND** el documento no contiene citas huerfanas (ninguna cita sin entrada en el `.bib`)

### Requirement: Exactitud de la licencia de herramientas de terceros

El documento SHALL describir la licencia de las herramientas de terceros con
exactitud. N8N MUST NOT presentarse como "codigo abierto" sin matiz; su licencia
oficial (Sustainable Use, fair-code) SHALL quedar explicitada o la herramienta
SHALL retirarse de toda enumeracion que la rotule como codigo abierto.

#### Scenario: N8N fuera de la enumeracion de codigo abierto
- **WHEN** se lee la seccion 1.7 (`01-introduccion.tex`) donde se enumeran "herramientas de bajo costo y codigo abierto"
- **THEN** N8N no aparece rotulado como codigo abierto sin matiz
- **AND** su licencia Sustainable Use queda explicitada o la herramienta se retira de esa enumeracion

#### Scenario: N8N fuera del "exclusivamente codigo abierto"
- **WHEN** se lee la seccion 6.1 (`06-implementacion.tex`) donde se afirma que la implementacion uso "exclusivamente tecnologias de codigo abierto"
- **THEN** la afirmacion ya no incluye implicitamente a N8N como codigo abierto
- **AND** la licencia Sustainable Use de N8N queda explicitada en el capitulo

#### Scenario: Consistencia con el estado del arte
- **WHEN** se comparan los pasajes corregidos con las secciones 3.2 y 6.3
- **THEN** la descripcion de la licencia de N8N es consistente con "licencia Sustainable Use" y "fair-code" ya usadas en esas secciones

### Requirement: Consistencia de la descripcion de la organizacion adoptante

La organizacion adoptante SHALL describirse de forma consistente a lo largo del
documento: la misma denominacion y los mismos atributos (una unica organizacion
mediana del sector servicios, aproximadamente 120 usuarios internos, cinco areas
funcionales, con sede en la provincia de Mendoza) en todos los pasajes que la
mencionan.

#### Scenario: Denominacion unificada
- **WHEN** se leen las secciones 1.2 y 1.8 (`01-introduccion.tex`)
- **THEN** ambos pasajes describen a la organizacion adoptante con la misma denominacion
- **AND** no alternan entre "una organizacion mediana" y "una unica organizacion" como si fueran caracterizaciones distintas

#### Scenario: Atributos consistentes
- **WHEN** se compara la caracterizacion de la organizacion en 1.2 y 1.8
- **THEN** los atributos coinciden (sector servicios, aproximadamente 120 usuarios, cinco areas, Mendoza)
- **AND** no se introduce un nombre propio no autorizado ni atributos contradictorios

### Requirement: Cobertura y densidad de citas por capitulo

Las afirmaciones que se apoyan en literatura SHALL citar una referencia
verificable en el punto donde se formulan. El documento MUST NOT introducir
referencias nuevas fuera de las dos entradas requeridas para la definicion de
empresa mediana y el marco etico; la bibliografia moderna 2023-2026 incorporada
por c-78 SHALL reutilizarse, sin duplicar su trabajo.

#### Scenario: Capitulo 7 con citas donde corresponde
- **WHEN** se leen las afirmaciones del Capitulo~7 (`07-resultados.tex`) que se apoyan en literatura o en metodos de terceros
- **THEN** esas afirmaciones citan una referencia verificable
- **AND** el capitulo deja de tener cero citas sobre afirmaciones propias que requieren respaldo

#### Scenario: Capitulo 6 y Capitulo 3 con respaldo
- **WHEN** se revisan las afirmaciones metodologicas del Capitulo~6 (`06-implementacion.tex`) y la comparacion del Capitulo~3
- **THEN** las afirmaciones apoyadas en literatura citan una referencia verificable
- **AND** la Tabla~1 del Capitulo~3 deja de sostener su comparacion sin citas

#### Scenario: Sin duplicar la bibliografia de c-78
- **WHEN** se inspecciona `Bibliography_base.bib` despues de este change
- **THEN** las unicas entradas agregadas son las dos de la definicion de empresa mediana y del marco etico
- **AND** las referencias 2023-2026 usadas provienen de las ya incorporadas por c-78
- **AND** no se crean entradas duplicadas ni citas huerfanas nuevas
