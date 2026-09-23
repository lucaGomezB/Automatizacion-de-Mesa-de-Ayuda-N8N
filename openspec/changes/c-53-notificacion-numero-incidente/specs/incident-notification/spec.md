## Purpose

Definir el contrato de notificación del número de incidente al usuario final en los tres canales de ingreso (correo, formulario web y telefonía), incluyendo la captura y persistencia del número llamante, la garantía de entrega aun cuando el incidente se derive a revisión humana, y el comportamiento ante un contacto faltante.

## ADDED Requirements

### Requirement: Número de incidente canónico y legible

El sistema SHALL exponer un número de incidente único, estable y legible para el usuario final, derivado del identificador persistido del incidente. El número SHALL ser el mismo que el backend retorna en el alta y que el workflow de orquestación propaga en sus notificaciones. El sistema MUST NOT presentar identificadores distintos por canal para un mismo incidente. La personalización por prefijo configurable queda fuera de este contrato.

#### Scenario: El número es el identificador persistido

- **WHEN** un incidente se crea por cualquiera de los tres canales
- **THEN** el número notificado al usuario es el identificador persistido del incidente

#### Scenario: El mismo número en todos los canales

- **WHEN** un incidente se crea por un canal y se notifica al usuario
- **THEN** el número notificado coincide con el que el backend expone para ese incidente

### Requirement: Notificación de confirmación al usuario en el canal correo

El sistema SHALL enviar al remitente original un correo de confirmación que incluya el número de incidente, SIEMPRE que el incidente se haya creado, con independencia de que el incidente haya sido derivado a revisión humana. El destinatario SHALL resolverse a una dirección de correo válida a partir del remitente del mensaje entrante, admitiendo que el remitente llegue tanto como cadena como como objeto estructurado del proveedor de correo. La ausencia de un destinatario válido MUST NOT abortar el flujo de alta.

#### Scenario: Confirmación de correo en el alta normal

- **WHEN** un incidente del canal correo se crea sin requerir revisión humana
- **THEN** el workflow envía un correo de confirmación al remitente original con el número de incidente

#### Scenario: Confirmación de correo en revisión humana

- **WHEN** un incidente del canal correo se crea y requiere revisión humana
- **THEN** el workflow igualmente envía el correo de confirmación al remitente original con el número de incidente

#### Scenario: Remitente estructurado produce destinatario válido

- **WHEN** el remitente entrante es un objeto estructurado que anida la dirección de correo
- **THEN** el destinatario de la confirmación resuelve a la dirección de correo efectiva y no a una representación inválida

### Requirement: Notificación de confirmación al usuario en el canal web

El sistema SHALL responder al envío del formulario web con el número de incidente, SIEMPRE que el incidente se haya creado, con independencia de que el incidente haya sido derivado a revisión humana. La respuesta SHALL ser síncrona con la petición del formulario. Cuando no exista un incidente creado, la respuesta SHALL indicar de forma explícita que no hubo alta, sin presentar un número inexistente.

#### Scenario: Respuesta web con número en el alta normal

- **WHEN** un incidente del canal web se crea sin requerir revisión humana
- **THEN** la respuesta al formulario incluye el número de incidente creado

#### Scenario: Respuesta web con número en revisión humana

- **WHEN** un incidente del canal web se crea y requiere revisión humana
- **THEN** la respuesta al formulario incluye el número de incidente creado y no un valor nulo

#### Scenario: Respuesta web sin alta

- **WHEN** una petición del canal web no produce la creación de un incidente
- **THEN** la respuesta indica que no hubo alta y no presenta un número de incidente

### Requirement: Notificación por SMS al llamante en el canal de telefonía

El sistema SHALL enviar al número llamante un mensaje de texto con el número de incidente cuando un incidente originado en el canal de telefonía se cree. El envío SHALL realizarse mediante el proveedor de mensajería del canal telefónico y MUST NOT bloquear el alta ni la respuesta del backend. El SMS SHALL ser transaccional y SHALL limitarse al número de incidente y un texto breve de referencia; MUST NOT contener datos personales del incidente.

#### Scenario: SMS con el número tras el alta telefónica

- **WHEN** se crea un incidente originado en el canal de telefonía y el número llamante está disponible
- **THEN** el sistema envía al número llamante un SMS con el número de incidente

#### Scenario: El envío no bloquea el alta

- **WHEN** se crea un incidente de telefonía
- **THEN** la creación del incidente y la respuesta del backend no dependen del resultado del envío del SMS

#### Scenario: El SMS es transaccional y mínimo

- **WHEN** se inspecciona el contenido del SMS enviado
- **THEN** el contenido se limita al número de incidente y una referencia breve, sin datos personales del incidente

### Requirement: Captura y persistencia cifrada del número llamante

El sistema SHALL capturar el número llamante desde el webhook de voz del proveedor de telefonía y SHALL persistirlo asociado a la llamada (correlación por el identificador de llamada), porque el callback asíncrono posterior NO provee el número llamante. El número SHALL almacenarse cifrado en reposo y MUST NOT incluirse en el payload de handoff como dato en claro más allá de lo ya establecido, ni en el registro de auditoría. La persistencia del número MUST NOT alterar la idempotencia del ingreso ni la firma de seguridad del webhook.

#### Scenario: El número se captura en el webhook de voz

- **WHEN** el proveedor de telefonía invoca el webhook de voz de una llamada
- **THEN** el sistema registra el número llamante correlacionado con el identificador de llamada

#### Scenario: El número sobrevive al pipeline asíncrono

- **WHEN** transcurre la grabación y su callback posterior, que no provee el número llamante
- **THEN** el número capturado en el webhook de voz permanece disponible para la notificación al usuario

#### Scenario: El número se almacena cifrado

- **WHEN** se inspecciona la persistencia del número llamante
- **THEN** el número está cifrado en reposo y no aparece en claro en la auditoría

### Requirement: Comportamiento ante número llamante ausente

Cuando el número llamante no esté disponible, el sistema SHALL omitir el envío del SMS, SHALL registrar de forma observable la omisión, y MUST NOT fallar el alta del incidente ni la notificación de otros canales.

#### Scenario: Sin número no se envía SMS

- **WHEN** se crea un incidente de telefonía y el número llamante no está disponible
- **THEN** el sistema no envía SMS y registra la omisión de forma observable

#### Scenario: La omisión no afecta el alta

- **WHEN** el número llamante no está disponible
- **THEN** el incidente se crea y persiste con normalidad

### Requirement: Base de licitud y minimización del SMS

El envío del SMS SHALL sustentarse en que la persona contactó a la mesa de ayuda y proporcionó su número, y SHALL estar limitado a la finalidad transaccional de informar el número de su incidente. El sistema MUST NOT reutilizar el número para fines promocionales, de perfilado ni para notificaciones no relacionadas con el incidente.

#### Scenario: Uso limitado a la finalidad transaccional

- **WHEN** se inspecciona el uso del número llamante por el sistema
- **THEN** su uso se limita a notificar el número del incidente originado por su propia llamada

#### Scenario: Sin reutilización promocional

- **WHEN** se envía un SMS al llamante
- **THEN** el mensaje no contiene contenido promocional ni de perfilado