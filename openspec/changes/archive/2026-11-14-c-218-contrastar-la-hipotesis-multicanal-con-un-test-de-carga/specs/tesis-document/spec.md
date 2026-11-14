## MODIFIED Requirements

### Requirement: Estado declarado de las hipotesis subsidiarias

Las dos hipotesis subsidiarias de `01-introduccion.tex` SHALL tener un estado declarado y coherente en la introduccion, la metodologia, la discusion y las conclusiones. La de integracion multicanal sin cuellos de botella SHALL declararse "contrastada en su dimension de capacidad" porque se midio con un test de carga de costo cero sobre el tramo compartido: el estado SHALL informar el resultado medido (latencia p50/p95, throughput y tasa de error por nivel de concurrencia) y SHALL declarar que la complejidad operativa percibida permanece sin instrumento, de modo que el estado MUST NOT presentarse como un contraste total de la hipotesis. La de mayor eficiencia del esquema hibrido frente a un esquema solo de modelo SHALL declararse "contrastada: no concluyente" en todos los capitulos, porque se midio con el brazo «Gemini solo» bajo una regla de decision prerregistrada y el resultado fue no concluyente: el ahorro de llamadas y de costo se cumplio, pero la no inferioridad de la exactitud no se establecio. MUST NOT declararse "no contrastada" ni "confirmada". La discusion y las conclusiones MUST NOT afirmar consistencia con la hipotesis de eficiencia apoyandose solo en la proporcion de casos resueltos sin invocar al modelo, ni afirmar que la integracion multicanal elimino la complejidad operativa percibida.

#### Scenario: Estados declarados en los tres capitulos

- **WHEN** se leen la introduccion, la discusion y las conclusiones
- **THEN** cada hipotesis subsidiaria tiene un estado explicito
- **AND** la de eficiencia figura como "contrastada: no concluyente" en los tres capitulos
- **AND** la de integracion multicanal figura como "contrastada en su dimension de capacidad" en los tres capitulos

#### Scenario: Frase de consistencia sin sustento retirada

- **WHEN** se busca en `08-discusion.tex` la afirmacion de consistencia con la hipotesis subsidiaria de eficiencia
- **THEN** no aparece apoyada solo en el 65,5 % de casos resueltos sin el modelo
- **AND** en su lugar figura el contraste medido con su veredicto no concluyente

#### Scenario: Subsidiaria multicanal no contrastada

- **WHEN** se leen las conclusiones sobre la integracion de los tres canales
- **THEN** el texto informa el resultado del test de carga con su veredicto de tres vias
- **AND** no afirma que la integracion "confirmo" la ausencia de dispersion operativa ni la complejidad percibida
- **AND** declara que la dimension de capacidad quedo contrastada y la de complejidad percibida no se midio

#### Scenario: Estado no presentado como contraste total

- **WHEN** se lee el estado de la subsidiaria multicanal en cualquier capitulo
- **THEN** no se presenta como un contraste completo de la hipotesis
- **AND** declara explicitamente que la complejidad percibida quedo fuera de la medicion

## ADDED Requirements

### Requirement: Declaracion del contraste de capacidad de la integracion multicanal

El documento SHALL informar el contraste de la hipotesis subsidiaria de integracion multicanal como un test de carga sobre el tramo compartido donde convergen los canales, con un criterio de decision de tres vias fijado antes de observar datos (techo absoluto de p95, tolerancia de throughput y tasa de error cero). El pasaje SHALL declarar, con remision a la tabla correspondiente y al memo canonico: el entorno desechable y de costo cero, los niveles de concurrencia, la latencia p50/p95, el throughput y la tasa de error por nivel, el veredicto de tres vias, y los limites del contraste (medicion en una sola maquina, camino determinístico sin inferencia paga, y que los canales de correo y telefonia quedaron fuera de la inyeccion concurrente por sondado y por costo respectivamente). MUST NOT presentar el resultado como prueba de que la integracion elimina la complejidad operativa percibida ni como validacion en produccion, y MUST NOT extrapolar la capacidad a hardware distinto del medido.

#### Scenario: Resultado de capacidad con procedencia

- **WHEN** se leen las cifras del test de carga en los resultados
- **THEN** coinciden con el reporte del arnes y con la seccion `3.29` del memo canonico
- **AND** cada cifra figura en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Limites presentes

- **WHEN** se lee el pasaje del contraste de capacidad
- **THEN** declara el entorno desechable, el camino determinístico de costo cero, la medicion en una sola maquina y la exclusion de los canales de correo y telefonia
- **AND** el estado se rotula "contrastada en su dimension de capacidad", no "confirmada" ni "no contrastada"

#### Scenario: Sin sobreventa del resultado

- **WHEN** se leen los pasajes de la subsidiaria multicanal en la metodologia, la discusion y las conclusiones
- **THEN** ninguno afirma que la integracion elimina la complejidad operativa percibida
- **AND** ninguno extrapola la capacidad medida a otro hardware o a produccion
