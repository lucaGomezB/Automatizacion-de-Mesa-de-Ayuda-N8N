## ADDED Requirements

### Requirement: Destino de notificacion que no crea incidentes

La notificacion saliente del backend SHALL apuntar a un webhook N8N dedicado, distinto del webhook de alta de incidentes (`incidente-web`), que MUST NOT crear incidentes. El payload de notificacion SHALL declarar explicitamente su evento/origen como una notificacion de clasificacion. La garantia de que la notificacion no puede crear incidentes SHALL quedar documentada de forma explicita y MUST NOT depender de un 404 accidental ni de la ausencia de configuracion.

#### Scenario: La URL configurada apunta a un webhook dedicado

- **WHEN** se inspecciona la configuracion de la notificacion del backend
- **THEN** la URL apunta a un webhook dedicado distinto de `incidente-web`

#### Scenario: El payload declara su evento como notificacion

- **WHEN** el backend emite una notificacion de clasificacion
- **THEN** el cuerpo enviado incluye un marcador explicito de evento/origen de notificacion

#### Scenario: El webhook dedicado no crea incidentes

- **WHEN** el webhook dedicado recibe una notificacion de clasificacion
- **THEN** el flujo asociado no crea ni persiste un incidente

#### Scenario: El acoplamiento queda documentado

- **WHEN** un operador consulta la documentacion del workflow o del webhook
- **THEN** encuentra la declaracion explicita de que la notificacion no puede crear incidentes y por que
