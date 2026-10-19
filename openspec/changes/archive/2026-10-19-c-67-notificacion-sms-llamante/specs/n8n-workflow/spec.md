## ADDED Requirements

### Requirement: N8N-SMS-001 — Notificación por SMS al llamante tras el alta telefónica

La confirmación del canal de telefonía SHALL resolverse mediante el SMS al número llamante y MUST NOT depender de la respuesta TwiML de la llamada, que no conoce el número porque el alta es asíncrona. Las salidas de telefonía y fallback del switch `Rutear por canal de origen` MUST NOT conectarse al nodo `Correo de confirmacion al usuario`. El workflow SHALL garantizar que la rama de telefonía dispare el alta del incidente con `origen_message_id = CallSid`, de modo que el backend pueda correlacionar el ingreso y notificar al llamante. El envío efectivo del SMS lo realiza el backend, no un nodo del workflow.

#### Scenario: Notificación telefónica por SMS tras alta exitosa

- **WHEN** un incidente del canal `telefonía` se crea con `201 Created` y el número llamante está disponible
- **THEN** el usuario recibe el número de incidente por SMS y no mediante el TwiML de la llamada

#### Scenario: La confirmación telefónica no es TwiML

- **WHEN** se inspecciona el mecanismo de confirmación del canal de telefonía en el workflow
- **THEN** no existe un cierre TwiML que presente el número de incidente como mecanismo de confirmación

#### Scenario: La rama de telefonía dispara el alta correlacionable

- **WHEN** la rama de telefonía del switch procesa una llamada
- **THEN** el alta del incidente llega al backend con `origen_message_id = CallSid` y el backend puede correlacionar el ingreso persistido
