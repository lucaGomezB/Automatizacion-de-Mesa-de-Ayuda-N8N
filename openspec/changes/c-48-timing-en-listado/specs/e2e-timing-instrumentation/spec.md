## MODIFIED Requirements

### Requirement: Derivacion de la latencia end-to-end

La latencia SHALL derivarse como `latencia_e2e_ms = persistido_en - ingresado_en` expresada en milisegundos. El sistema SHALL exponer `latencia_e2e_ms` en la representacion de lectura del incidente. La latencia SHALL ser nula cuando falte cualquiera de los dos instantes. El sistema MUST NOT persistir la latencia como columna denormalizada, para no duplicar la fuente de verdad.

La exposicion SHALL alcanzar AMBAS representaciones de lectura del incidente: el detalle y la proyeccion de listado. La proyeccion de listado SHALL exponer ademas los dos instantes fuente (`ingresado_en`, `persistido_en`) y SHALL derivar `latencia_e2e_ms` con la misma logica que el detalle, de modo que ambas representaciones devuelvan el mismo valor para un mismo incidente. Un incidente con instantes ausentes SHALL listarse igualmente con `latencia_e2e_ms` nulo, sin fallar la serializacion.

#### Scenario: Derivacion correcta

- **WHEN** el incidente tiene `ingresado_en` y `persistido_en` no nulos
- **THEN** `latencia_e2e_ms` es la diferencia entre ambos instantes

#### Scenario: Latencia nula si falta un instante

- **WHEN** falta `ingresado_en` o `persistido_en`
- **THEN** `latencia_e2e_ms` es nulo

#### Scenario: Unidades en milisegundos

- **WHEN** la diferencia entre `persistido_en` e `ingresado_en` es de 12.5 segundos
- **THEN** `latencia_e2e_ms` es 12500

#### Scenario: Proyeccion de listado expone los instantes y la latencia

- **WHEN** se consulta el listado de incidentes y un incidente tiene `ingresado_en` y `persistido_en` no nulos
- **THEN** cada item del listado incluye ambos instantes fuente y `latencia_e2e_ms` con un valor no nulo

#### Scenario: Proyeccion de listado con instantes ausentes

- **WHEN** un incidente del listado tiene `ingresado_en` o `persistido_en` nulo
- **THEN** el item expone `latencia_e2e_ms` nulo y el listado se serializa sin error

#### Scenario: Paridad de derivacion entre detalle y listado

- **WHEN** un mismo incidente se lee por el endpoint de detalle y por el endpoint de listado
- **THEN** `latencia_e2e_ms` coincide en ambas representaciones al milisegundo

### Requirement: Politica de latencia negativa

Cuando `latencia_e2e_ms` resulte menor que cero, el sistema SHALL NOT reportarlo como una medicion valida. El valor SHALL marcarse como anomalo y SHALL excluirse del corpus y del analisis; el sistema MUST NOT aceptarlo en silencio. La anomalia SHALL quedar registrada para diagnostico (por ejemplo, ingreso futuro dentro de la tolerancia o skew de relojes). La marca de anomalia SHALL ser observable en toda representacion de lectura que exponga la latencia, incluida la proyeccion de listado.

#### Scenario: Latencia negativa marcada como anomalia

- **WHEN** `persistido_en - ingresado_en` es menor que cero
- **THEN** `latencia_e2e_ms` se marca como anomalo y no como medicion valida

#### Scenario: Excluida del corpus y del analisis

- **WHEN** se construye el corpus o el analisis de latencias
- **THEN** los casos con `latencia_e2e_ms` negativo se excluyen

#### Scenario: Nunca aceptada en silencio

- **WHEN** se deriva una latencia negativa
- **THEN** el sistema no la reporta como valida sin marcar la anomalia

#### Scenario: Anomalia visible en la proyeccion de listado

- **WHEN** un incidente del listado tiene `persistido_en` anterior a `ingresado_en`
- **THEN** el item expone `latencia_e2e_ms` nulo y la marca de anomalia en verdadero