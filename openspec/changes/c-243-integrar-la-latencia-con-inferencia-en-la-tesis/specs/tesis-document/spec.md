## MODIFIED Requirements

### Requirement: Estado declarado de las hipotesis subsidiarias

Las dos hipotesis subsidiarias de `01-introduccion.tex` SHALL tener un estado declarado y coherente en la introduccion, la metodologia, la discusion y las conclusiones. La de integracion multicanal sin cuellos de botella SHALL declararse "contrastada en su dimension de capacidad" porque se midio con un test de carga de costo cero sobre el tramo compartido: el estado SHALL informar el resultado medido (latencia p50/p95, throughput y tasa de error por nivel de concurrencia) y SHALL declarar que la complejidad operativa percibida permanece sin instrumento, de modo que el estado MUST NOT presentarse como un contraste total de la hipotesis. El estado SHALL distinguir la evidencia de capacidad, que proviene del test deterministico de costo cero, de la sonda acotada con inferencia incluida: la sonda SHALL informarse como evidencia ancilar de dos corridas complementarias, MUST NOT alterar el estado de la hipotesis y MUST NOT presentarse como contraste de capacidad. La de mayor eficiencia del esquema hibrido frente a un esquema solo de modelo SHALL declararse "sin contraste limpio" en todos los capitulos, porque el bloque primario prerregistrado se retiro con la validacion fuera de muestra y el unico bloque que subsiste, dentro de la muestra, no es una prueba limpia. MUST NOT declararse "contrastada: no concluyente", "confirmada" ni "refutada". La discusion y las conclusiones MUST NOT afirmar consistencia con la hipotesis de eficiencia apoyandose en la proporcion de casos resueltos sin invocar al modelo, ni afirmar que la integracion multicanal elimino la complejidad operativa percibida.

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

#### Scenario: Sonda distinguida de la capacidad

- **WHEN** se lee el estado de la subsidiaria multicanal junto al pasaje de la sonda con inferencia
- **THEN** el veredicto de capacidad figura referido al test deterministico de costo cero
- **AND** la sonda figura como evidencia ancilar que no modifica el estado de la hipotesis
- **AND** ninguna oracion presenta la sonda como confirmacion ni como refutacion de la capacidad

### Requirement: Declaracion del contraste de capacidad de la integracion multicanal

El documento SHALL informar el contraste de la hipotesis subsidiaria de integracion multicanal como un test de carga sobre el tramo compartido donde convergen los canales, con un criterio de decision de tres vias fijado antes de observar datos (techo absoluto de p95, tolerancia de throughput y tasa de error cero). El pasaje SHALL declarar, con remision a la tabla correspondiente y al memo canonico: el entorno desechable y de costo cero, los niveles de concurrencia, la latencia p50/p95, el throughput y la tasa de error por nivel, el veredicto de tres vias, y los limites del contraste (medicion en una sola maquina, camino deterministico sin inferencia paga, y que los canales de correo y telefonia quedaron fuera de la inyeccion concurrente por sondado y por costo respectivamente). El pasaje SHALL declarar de forma explicita que sus cifras corresponden al camino deterministico de costo cero y que la latencia con inferencia incluida se informa por separado en una sonda acotada de dos corridas complementarias, la cual MUST NOT presentarse como resultado de capacidad ni como refutacion de este veredicto. MUST NOT presentar el resultado como prueba de que la integracion elimina la complejidad operativa percibida ni como validacion en produccion, y MUST NOT extrapolar la capacidad a hardware distinto del medido.

#### Scenario: Resultado de capacidad con procedencia

- **WHEN** se leen las cifras del test de carga en los resultados
- **THEN** coinciden con el reporte del arnes y con la seccion `3.29` del memo canonico
- **AND** cada cifra figura en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Limites presentes

- **WHEN** se lee el pasaje del contraste de capacidad
- **THEN** declara el entorno desechable, el camino deterministico de costo cero, la medicion en una sola maquina y la exclusion de los canales de correo y telefonia
- **AND** el estado se rotula "contrastada en su dimension de capacidad", no "confirmada" ni "no contrastada"
- **AND** remite a la sonda con inferencia incluida como evidencia distinta y le asigna el caracter de ancilar

#### Scenario: Sin sobreventa del resultado

- **WHEN** se leen los pasajes de la subsidiaria multicanal en la metodologia, la discusion y las conclusiones
- **THEN** ninguno afirma que la integracion elimina la complejidad operativa percibida
- **AND** ninguno extrapola la capacidad medida a otro hardware o a produccion
- **AND** ninguno presenta la sonda con inferencia como contraste de capacidad

## ADDED Requirements

### Requirement: Reporte de la sonda acotada de latencia con inferencia incluida

El documento SHALL informar, en una subseccion de resultados posterior a la del contraste de capacidad y con remision a sus artefactos de evidencia versionados, la sonda acotada de latencia con inferencia real incluida ejecutada sobre el tramo compartido (capa del backend y capa del \emph{webhook} de N8N). La sonda SHALL combinar DOS corridas segun la decision de los autores: los niveles 1 y 5 concurrencia provenientes de la corrida ampliada (`evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json`; 60 solicitudes por nivel, 3 repeticiones; n = 90 escalados por subconjunto y capa) y los niveles 10 y 20 provenientes de la corrida original (`evaluation/evidence/load_test_inferencia_2026-11-17.json`; 20 solicitudes por nivel, 1 repeticion; n = 10 escalados por subconjunto y capa). El criterio SHALL ser el de tres vias del contraste de capacidad mas una condicion de degradacion por inferencia: el cociente entre el p95 del subconjunto escalado y el p95 del subconjunto deterministico del mismo nivel no supera T = 4. La subseccion SHALL presentar una tabla por capa y nivel de concurrencia con p50, p95, p99, throughput, tasa de error, fraccion escalada, cociente de inferencia y veredicto del nivel, y SHALL rotular **por fila** su corrida de origen y su n escalado. La subseccion SHALL declarar tres veredictos nombrando el nivel y la condicion violados. SHALL declarar que la evidencia primaria de capacidad sigue siendo el test deterministico de costo cero y que la sonda es ancilar. MUST NOT presentar la sonda como resultado de capacidad, como refutacion del veredicto de capacidad ni como validacion en produccion. MUST NOT omitir los limites: dos corridas complementarias con su n y repeticiones por fila, una sola maquina, entorno desechable, gasto registrado solo en la corrida ampliada con procedencia `tokens_calculado`, deriva posible de proveedor y modelo, potencia no comparable con la corrida canonica de capacidad y no extrapolacion a produccion.

#### Scenario: Tabla combinada con procedencia y rotulo por fila

- **WHEN** se leen la subseccion y su tabla
- **THEN** cada cifra coincide con el artefacto de evidencia citado en la nota para su corrida de origen
- **AND** cada fila rotula su corrida de origen (`ampl.` / `orig.`) y su n escalado
- **AND** la nota de la tabla identifica ambos artefactos y el comando que la reproduce

#### Scenario: Tres veredictos declarados

- **WHEN** se leen los veredictos de la sonda
- **THEN** figura el del backend, el del \emph{webhook} de N8N y el global (el de la peor capa)
- **AND** cada veredicto nombra el nivel y la condicion violados

#### Scenario: Veredicto del backend por condicion relativa

- **WHEN** se lee el veredicto de la capa del backend
- **THEN** declara que la condicion violada es la tolerancia de degradacion por inferencia **solo en el nivel de 1 concurrente** (cociente 5,05)
- **AND** declara que el nivel de 5 concurrentes cumple (cociente 3,74) y que el techo absoluto de p95 y la tolerancia de throughput se cumplen en los cuatro niveles
- **AND** no presenta el veredicto como saturacion del backend

#### Scenario: Veredicto del webhook por techo absoluto

- **WHEN** se lee el veredicto de la capa del \emph{webhook} de N8N
- **THEN** declara que la condicion violada es el techo absoluto de p95 en los niveles de 5, 10 y 20 concurrentes
- **AND** declara que el cociente de degradacion por inferencia se mantiene dentro de T = 4 en los cuatro niveles

#### Scenario: Primacia de la evidencia deterministica

- **WHEN** se comparan la subseccion de capacidad y la de la sonda
- **THEN** el test de costo cero figura como evidencia primaria de capacidad
- **AND** la sonda figura como evidencia ancilar, acotada y de dos corridas combinadas

#### Scenario: Limites presentes

- **WHEN** se lee la subseccion de la sonda
- **THEN** figuran los siete limites declarados, con el n y las repeticiones por corrida
- **AND** ninguno se omite ni se suaviza

#### Scenario: Sin extrapolacion

- **WHEN** se leen la discusion y las conclusiones
- **THEN** no extrapolan la sonda a produccion ni a otro hardware
- **AND** no la presentan como validacion de capacidad
