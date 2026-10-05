# Delta for incident-intake-guards

## ADDED Requirements

### Requirement: WEB-ORIGIN-001 — El canal web declara siempre un identificador de origen

El alta proveniente del canal web SHALL declarar SIEMPRE un `origen_message_id` no nulo, sea provisto de forma determinista por el llamador o generado de forma unica por el workflow N8N. La generacion SHALL ser responsabilidad PRIMARIA de N8N: un identificador deterministico provisto por el llamador (`body.origen_message_id`, p.ej. `corpus-<case_id>` del harness) o, en su ausencia, un identificador unico derivado de la ejecucion (`web-<execution.id>-<timestamp>`). Un default UUID del backend es OPCIONAL y secundario (defensa en profundidad), nunca la fuente primaria. La unicidad SHALL NOT rechazar a un usuario real distinto: dos envios web legitimos distintos SIEMPRE obtienen identificadores distintos. Con ello el canal web SHALL quedar cubierto por la misma garantia de idempotencia por `origen_message_id` que correo y telefonia, apoyada en la restriccion de unicidad existente, de modo que reingestar el mismo caso web MUST NOT crear un segundo incidente, MUST NOT reclasificar y MUST NOT emitir una nueva notificacion. Los emisores que no proveen identificador siguen siendo el caso de las altas directas por API, no el del canal web.

#### Scenario: Reingesta del mismo caso web no duplica

- **WHEN** dos altas web llegan con el mismo `origen_message_id` no nulo
- **THEN** el sistema crea un unico incidente y la segunda alta devuelve el incidente existente sin reclasificar

#### Scenario: Dos casos web distintos no colisionan

- **WHEN** dos altas web distintas llegan con identificadores de origen diferentes (por ejemplo `corpus-R001` y `corpus-R002`)
- **THEN** se crean dos incidentes distintos, uno por cada identificador

#### Scenario: La unicidad es efectiva a nivel de persistencia para web

- **WHEN** dos altas web con el mismo identificador intentan persistirse de forma concurrente
- **THEN** el indice unico impide registrar dos filas y el sistema resuelve la colision devolviendo un unico incidente

#### Scenario: Las altas directas sin identificador conservan su comportamiento

- **WHEN** una solicitud de alta directa no incluye `origen_message_id`
- **THEN** el incidente se crea normalmente con el identificador nulo, sin cambios respecto del comportamiento previo
