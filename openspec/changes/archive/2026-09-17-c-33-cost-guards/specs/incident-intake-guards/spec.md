## Purpose

Guardas del contrato de alta de incidentes que evitan trabajo pago redundante y duplicados: idempotencia por identificador de mensaje de origen, aceptacion de clasificaciones precalculadas con origen explicito, y rechazo de eventos que no corresponden a la creacion de un incidente.

## ADDED Requirements

### Requirement: Idempotencia de alta por identificador de mensaje de origen

El contrato de alta SHALL aceptar un identificador opcional de mensaje de origen (`origen_message_id`) y el sistema SHALL garantizar que un mismo identificador no produzca mas de un incidente. La persistencia SHALL imponer una restriccion de unicidad sobre `origen_message_id`, que SHALL ser nullable para no obligar a los emisores que no lo proveen. Cuando llega un identificador ya registrado, el sistema SHALL responder de forma idempotente con el incidente existente y MUST NOT volver a ejecutar la clasificacion ni emitir una nueva notificacion. La verificacion de idempotencia SHALL resolverse ANTES de invocar cualquier componente de clasificacion pago.

#### Scenario: Alta nueva registra el identificador de origen

- **WHEN** una solicitud de alta incluye un `origen_message_id` que no existe en la base de datos
- **THEN** se crea un incidente nuevo y el identificador queda persistido asociado a ese incidente

#### Scenario: Reintento del mismo identificador no duplica ni reclasifica

- **WHEN** una segunda solicitud de alta repite un `origen_message_id` ya registrado
- **THEN** el sistema devuelve el incidente existente sin crear otro, sin ejecutar la clasificacion y sin emitir una notificacion nueva

#### Scenario: Alta sin identificador de origen sigue funcionando

- **WHEN** una solicitud de alta no incluye `origen_message_id`
- **THEN** el incidente se crea normalmente y el identificador queda nulo

#### Scenario: Identificadores distintos producen incidentes distintos

- **WHEN** dos solicitudes de alta incluyen identificadores de origen diferentes
- **THEN** se crean dos incidentes distintos, uno por cada identificador

#### Scenario: La unicidad es efectiva a nivel de persistencia

- **WHEN** dos altas con el mismo `origen_message_id` intentan persistirse de forma concurrente
- **THEN** la persistencia impide registrar dos filas con el mismo identificador y el sistema resuelve la colision devolviendo un unico incidente

### Requirement: Aceptacion de clasificacion precalculada con origen explicito

El contrato de alta SHALL aceptar opcionalmente una clasificacion precalculada con los campos sector predicho, sectores adicionales, confianza, un marcador explicito de origen y un marcador explicito de revision humana. El sector predicho, la confianza y el marcador de revision humana SHALL ser opcionales dentro de la clasificacion precalculada; su ausencia NO SHALL considerarse invalida. Cuando la clasificacion precalculada esta presente y es valida, el sistema SHALL persistirla y SHALL omitir la clasificacion server-side, de modo que MUST NOT invocar al proveedor pago. El sector ausente SHALL persistirse como nulo. Cuando la clasificacion precalculada esta ausente, el sistema SHALL conservar la clasificacion server-side. El origen explicito de la clasificacion SHALL quedar registrado para auditoria. Cuando el sector predicho viene presente, SHALL pertenecer al conjunto canonico de cinco sectores; cuando la confianza viene presente, SHALL estar en `[0.0, 1.0]`. Una clasificacion precalculada que viole estas restricciones SHALL rechazarse con error de validacion, sin invocar al clasificador pago.

#### Scenario: Clasificacion precalculada valida evita la llamada paga

- **WHEN** una solicitud de alta incluye sector predicho, confianza y origen de una fuente valida
- **THEN** el incidente se persiste con esa clasificacion, el origen queda registrado y no se invoca al clasificador pago

#### Scenario: Clasificacion precalculada forzada a revision humana sin sector

- **WHEN** una solicitud de alta incluye un marcador de revision humana y confianza `0.0` sin sector predicho
- **THEN** el incidente se persiste con revision humana activada, sector nulo, sin invocar al clasificador pago

#### Scenario: Sin clasificacion precalculada el backend clasifica server-side

- **WHEN** una solicitud de alta no incluye clasificacion precalculada
- **THEN** el backend ejecuta su clasificacion server-side y persiste el resultado como hasta ahora

#### Scenario: Sector precalculado invalido se rechaza sin costo

- **WHEN** la clasificacion precalculada incluye un sector presente que no pertenece al conjunto canonico de cinco sectores
- **THEN** la solicitud se rechaza con un error de validacion accionable y no se invoca al clasificador pago

#### Scenario: Confianza precalculada fuera de rango se rechaza sin costo

- **WHEN** la clasificacion precalculada incluye una confianza presente fuera de `[0.0, 1.0]` o no numerica
- **THEN** la solicitud se rechaza con un error de validacion accionable y no se invoca al clasificador pago

#### Scenario: El origen de la clasificacion es auditable

- **WHEN** un incidente se persiste con una clasificacion precalculada
- **THEN** el sistema permite distinguir que la clasificacion provino del emisor y no del pipeline server-side

### Requirement: Origen de evento explicito que impide crear incidentes desde notificaciones

El contrato de alta SHALL aceptar un marcador explicito de origen/evento. El endpoint de creacion SHALL rechazar con error de validacion todo payload cuyo marcador corresponda a un evento que no sea la creacion de un incidente (por ejemplo, una notificacion de clasificacion). Un payload sin marcador SHALL tratarse como un alta directa y conservar el comportamiento actual.

#### Scenario: Evento de creacion crea el incidente

- **WHEN** un payload declara un origen/evento de creacion de incidente
- **THEN** el incidente se crea y el origen declarado queda registrado

#### Scenario: Evento de notificacion no crea incidente

- **WHEN** un payload declara un origen/evento de notificacion de clasificacion
- **THEN** el sistema rechaza la solicitud con un error de validacion y no se crea ningun incidente

#### Scenario: Payload sin marcador conserva el alta directa

- **WHEN** un payload de alta no declara origen/evento
- **THEN** el comportamiento es el de un alta directa sin cambios
