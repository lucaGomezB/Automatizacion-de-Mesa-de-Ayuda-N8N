## Purpose

Definir el contrato de notificación del número de incidente al usuario final por el canal de telefonía (SMS al llamante), incluyendo la captura y persistencia cifrada del número llamante en el webhook de voz, el comportamiento ante un contacto faltante, y la base de licitud/minimización consumida del change `C-66` (privacidad-transferencias). Porción de SMS separada de `c-53-notificacion-numero-incidente`.

## ADDED Requirements

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

### Requirement: Marco de licitud y transferencia internacional provisto por C-66

La base de licitud del tratamiento del número llamante, su minimización y el instrumento de transferencia internacional de datos SHALL ser definidos y provistos por el change `C-66` (privacidad-transferencias), que es dueño del manejo del número llamante y del marco de consentimiento/transferencia. Este change SHALL consumir ese marco y MUST NOT redefinirlo. El envío del SMS al llamante SHALL quedar condicionado a que `C-66` provea el instrumento de transferencia, dado que Estados Unidos NO es un país con nivel adecuado de protección.

#### Scenario: El marco de privacidad se consume, no se redefine

- **WHEN** el sistema determina la base de licitud y la transferencia internacional del número llamante
- **THEN** usa el marco provisto por `C-66` y no define uno propio

#### Scenario: La transferencia requiere el instrumento de C-66

- **WHEN** el envío del SMS implicaría transferir el número a un proveedor en un país sin nivel adecuado de protección
- **THEN** el envío queda condicionado al instrumento de transferencia provisto por `C-66`
