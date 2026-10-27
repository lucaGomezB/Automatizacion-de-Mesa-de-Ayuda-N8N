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

### Requirement: Idempotencia del alta bajo reintentos concurrentes

Para un mismo `origen_message_id`, cualquier entrelazado de altas ---replay secuencial despues del commit, altas concurrentes o un reintento del orquestador mientras el intento previo aun no confirmo--- SHALL producir exactamente una fila de `incidente` y exactamente un registro de `clasificacion_log` para ese identificador, y todas las respuestas exitosas SHALL devolver el mismo incidente. La serializacion SHALL apoyarse en la restriccion UNIQUE de `origen_message_id`: la insercion perdedora MUST resolverse devolviendo la fila ganadora, sin propagar el error de unicidad al llamador. Cuando ambas altas concurrentes completan con exito, el clasificador MUST invocarse una sola vez. Si el intento previo aborta su transaccion sin confirmar, el intento siguiente SHALL crear el incidente una unica vez. El comportamiento SHALL verificarse contra PostgreSQL, porque la espera por bloqueo del indice no es observable en SQLite.

#### Scenario: Dos altas concurrentes con el mismo identificador

- **WHEN** dos peticiones `POST /api/v1/incidentes/` con el mismo `origen_message_id` se ejecutan de forma concurrente contra PostgreSQL con un clasificador que tarda en responder
- **THEN** ambas responden HTTP 201 con el mismo `id`
- **AND** existe una sola fila de `incidente` y un solo registro de `clasificacion_log` para ese identificador
- **AND** el clasificador se invoco una sola vez

#### Scenario: Reintento despues de un commit tardio

- **WHEN** un primer intento confirma el alta despues de que el orquestador ya envio un segundo intento con el mismo `origen_message_id`
- **THEN** el segundo intento devuelve el incidente confirmado por el primero y no crea una segunda fila

#### Scenario: Reintento despues de un intento abortado

- **WHEN** el primer intento falla y revierte su transaccion antes de confirmar, y luego llega un reintento con el mismo `origen_message_id`
- **THEN** el reintento crea el incidente una sola vez y lo clasifica

### Requirement: Equivalencia observable de la respuesta de replay

La respuesta de un replay idempotente SHALL ser observablemente equivalente a la del alta original para el orquestador: el mismo `id`, `numero_incidente`, sector y `requiere_revision_humana` persistidos. Cuando el incidente existente requiere revision humana, el servicio SHALL re-resolver `destinatarios_revision` con la misma lectura del alta original antes de responder, de modo que el orquestador no caiga al destinatario de respaldo por el solo hecho de haber reintentado. El replay MUST NOT reclasificar, MUST NOT re-despachar la notificacion a N8N, MUST NOT persistir los destinatarios y MUST NOT cambiar el contrato OpenAPI.

#### Scenario: Replay de un incidente que requiere revision

- **WHEN** llega un replay de un incidente persistido con `requiere_revision_humana = true` y existen destinatarios de revision configurados
- **THEN** la respuesta incluye en `destinatarios_revision` los mismos destinatarios que resolveria el alta original

#### Scenario: Replay de un incidente sin revision

- **WHEN** llega un replay de un incidente persistido con `requiere_revision_humana = false`
- **THEN** la respuesta incluye `destinatarios_revision` vacio, igual que el alta original

#### Scenario: El replay no tiene efectos laterales

- **WHEN** ocurre cualquier replay idempotente
- **THEN** el clasificador no se invoca, la notificacion a N8N no se despacha y no se escribe ninguna fila nueva

### Requirement: Trazabilidad de los replays del alta

Cada replay idempotente que alcanza el backend SHALL emitir un evento estructurado que distinga el cortocircuito por identificador ya confirmado (`incidente_idempotente`) de la resolucion por carrera de unicidad (`incidente_idempotente_carrera`), con el `origen_message_id` y el `incidente_id`. Los eventos MUST NOT contener la descripcion ni otra PII. `clasificacion_log` SHALL conservar exactamente un registro por clasificacion efectivamente ejecutada: un replay MUST NOT agregar registros.

#### Scenario: El replay deja un evento sin PII

- **WHEN** ocurre un replay idempotente por cualquiera de los dos caminos
- **THEN** se emite el evento correspondiente con `origen_message_id` e `incidente_id`, sin la descripcion del incidente

#### Scenario: El registro de clasificacion no crece con los replays

- **WHEN** un mismo `origen_message_id` recibe una alta y luego N replays
- **THEN** el incidente conserva un unico registro en `clasificacion_log`
