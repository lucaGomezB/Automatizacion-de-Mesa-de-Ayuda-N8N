# incident-origin-correlation Specification

## Purpose
Define el contrato de lectura que expone el identificador de origen de un incidente (`origen_message_id`) y permite filtrar el listado por coincidencia exacta, habilitando la correlacion determinista entre un item enviado y el incidente persistido, y preservando la exclusion de replays idempotentes de la medicion.

## Requirements

### Requirement: Exposicion del identificador de origen en el contrato de lectura

El detalle de un incidente (`IncidenteRead`) SHALL exponer el campo `origen_message_id` (nullable) ademas de los campos ya expuestos. El campo SHALL ser un identificador de correlacion y MUST NOT contener la descripcion ni PII. Una fila legacy sin identificador SHALL serializar el campo con valor nulo sin fallar. La exposicion en `IncidenteListItem` NO es requisito de este change (puede agregarse de forma aditiva si simplifica la correlacion).

#### Scenario: El detalle expone el identificador de origen

- **WHEN** se consulta `GET /api/v1/incidentes/{id}` de un incidente con `origen_message_id` persistido
- **THEN** la respuesta incluye `origen_message_id` con el valor persistido

#### Scenario: Una fila legacy serializa el identificador nulo

- **WHEN** se consulta el detalle de un incidente cuyo `origen_message_id` es nulo
- **THEN** la respuesta incluye `origen_message_id = null` sin error de validacion

### Requirement: Filtrado exacto del listado por identificador de origen

El listado de incidentes SHALL aceptar un filtro opcional `origen_message_id` que devuelva unicamente los incidentes cuyo identificador coincide EXACTAMENTE con el valor provisto. El filtro SHALL combinarse con los demas filtros con AND logico y SHALL aplicarse respetando el alcance de visibilidad por rol vigente. La ausencia del filtro SHALL conservar el comportamiento actual del listado.

#### Scenario: El filtro devuelve el incidente correlacionado

- **WHEN** se consulta `GET /api/v1/incidentes/?origen_message_id=corpus-R001` y existe un incidente con ese identificador dentro del alcance del usuario
- **THEN** el listado devuelve unicamente ese incidente

#### Scenario: El filtro con un valor inexistente devuelve vacio

- **WHEN** se consulta el listado con un `origen_message_id` que no existe
- **THEN** el listado devuelve una lista vacia, sin error

#### Scenario: Sin filtro el listado no cambia

- **WHEN** se consulta el listado sin `origen_message_id`
- **THEN** el resultado y el orden son los mismos que antes de este change

#### Scenario: El filtro respeta el alcance por rol

- **WHEN** un usuario no administrador filtra por el identificador de un incidente fuera de su sector
- **THEN** el listado no lo devuelve, consistente con la visibilidad por rol

### Requirement: Correlacion determinista y exclusion de replays idempotentes

La correlacion de un item enviado con su incidente persistido SHALL poder resolverse de forma determinista por el `origen_message_id` exacto, sin depender de heuristicas de ventana temporal. Un replay con el mismo `origen_message_id` SHALL devolver el incidente existente y SHALL conservar `ingresado_en` y `persistido_en` del alta original, de modo que la medicion NO se vuelva a realizar ni se cree una segunda fila.

#### Scenario: Correlacion exacta sin ventana temporal

- **WHEN** un emisor necesita localizar el incidente de un item enviado
- **THEN** puede filtrar el listado por el `origen_message_id` exacto y obtener el incidente, sin usar una ventana de tiempo

#### Scenario: El replay conserva la medicion original

- **WHEN** llega una segunda alta con un `origen_message_id` ya registrado
- **THEN** el sistema devuelve la fila existente y sus instantes `ingresado_en` `persistido_en` no cambian

#### Scenario: El replay no crea una fila nueva

- **WHEN** ocurre un replay idempotente por `origen_message_id`
- **THEN** la cantidad de filas de incidente para ese identificador no aumenta
