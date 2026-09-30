## ADDED Requirements

### Requirement: El texto crudo de telefonía nunca transita el borde de N8N

El sistema SHALL pseudonimizar el transcript de telefonía INMEDIATAMENTE después de obtenerlo y ANTES de cualquier entrega a n8n. La única representación del texto que cruce el borde hacia n8n SHALL ser la pseudonimizada. El transcript crudo MUST NOT transmitirse a n8n bajo ninguna ruta ni incluirse en el payload del handoff.

#### Scenario: El handoff lleva solo texto pseudonimizado

- **WHEN** el backend entrega el ingreso telefónico a n8n
- **THEN** el texto entregado contiene las etiquetas de pseudonimización y no contiene PII en claro

#### Scenario: El transcript crudo no cruza el borde

- **WHEN** se inspecciona el payload que el backend envía a n8n
- **THEN** no contiene el transcript original con datos personales

### Requirement: La IA de N8N consume únicamente la descripción pseudonimizada de telefonía

El sistema SHALL garantizar que el `AI Agent` del canal de telefonía reciba como entrada ÚNICAMENTE la descripción pseudonimizada. El prompt del agente MUST NOT interpolar un transcript crudo. El texto enviado al proveedor de inferencia desde n8n NO SHALL contener datos personales originales de la llamada. Esta regla corrige la fuga latente de la ruta previa, donde el prompt interpolaba el transcript crudo antes de cualquier pseudonimización.

#### Scenario: El prompt del agente no interpola transcript crudo

- **WHEN** se inspecciona la entrada del `AI Agent` en el canal de telefonía
- **THEN** el texto interpolado en el prompt es la descripción pseudonimizada y no un transcript crudo

#### Scenario: La inferencia externa no recibe PII original

- **WHEN** el `AI Agent` invoca al proveedor de inferencia para un incidente telefónico
- **THEN** el contenido enviado contiene las etiquetas de pseudonimización y no los datos personales originales