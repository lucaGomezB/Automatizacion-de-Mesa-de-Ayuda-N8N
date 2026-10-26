## ADDED Requirements

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
