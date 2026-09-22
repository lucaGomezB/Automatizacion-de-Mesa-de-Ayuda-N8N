## MODIFIED Requirements

### Requirement: Trigger Webhook para la transcripción de Twilio

El workflow N8N SHALL incluir un disparador `webhook` (método `POST`, con una ruta dedicada) que reciba del backend el ingreso telefónico YA pseudonimizado, como canal de telefonía. El disparador MUST NOT ser un `twilioTrigger` de resumen post-llamada y el workflow MUST NOT parsear CloudEvents de Twilio ni depender del evento `call-summary.complete`. La salida del webhook SHALL fluir hacia el `AI Agent` y, tras la validación de la respuesta de clasificación, hacia el nodo de normalización con `canal_raw = "telefonia"`, de modo que el normalizador asigne `canal_origen = "telefonia"`. El webhook SHALL estar autenticado con el secreto compartido del handoff.

#### Scenario: El disparador telefónico existe y alimenta el flujo

- **WHEN** se inspecciona el workflow exportado
- **THEN** existe un nodo `webhook` con método `POST` y ruta no vacía cuya salida fluye hacia el AI Agent, y no existe un nodo `twilioTrigger` de resumen post-llamada

#### Scenario: No hay parsing de CloudEvent

- **WHEN** se inspecciona el workflow exportado en busca de parsing del evento de resumen de Twilio
- **THEN** ningún nodo parsea el evento `call-summary.complete` ni una carga CloudEvent

#### Scenario: El canal telefónico queda identificado como "telefonia"

- **WHEN** un ingreso telefónico pseudonimizado atraviesa el flujo hasta la normalización
- **THEN** el `canal_raw` propagado es `"telefonia"` y la estructura unificada resultante tiene `canal_origen = "telefonia"`

### Requirement: N8N-TIMING-001 — Captura del instante de ingreso en el borde del trigger

Cada trigger del workflow SHALL propagar el instante de ingreso antes de cualquier procesamiento del canal. En el canal de telefonía el instante de ingreso SHALL ser el sellado por el BACKEND en la recepción del callback de grabación y SHALL propagarse SIN ser re-sellado por n8n, de modo que la latencia incluya la descarga, la transcripción, la pseudonimización y el handoff del backend. En el canal de correo la captura SHALL ocurrir al INICIO del flujo del trigger de Outlook, en el instante en que el poller recoge el mensaje, y MUST NOT usar el `receivedDateTime` del mensaje. En el canal web la captura SHALL usar el instante de recepción del webhook. El valor SHALL propagarse al normalizador y SHALL estar disponible para el nodo HTTP de persistencia.

#### Scenario: Telefonia captura antes del agente

- **WHEN** la suite estructural inspecciona el workflow
- **THEN** el `ingresado_en` propagado para telefonía se sella en el backend y está aguas arriba del `AI Agent`

#### Scenario: Telefonía propaga el sello del backend

- **WHEN** el webhook de telefonía recibe el handoff del backend
- **THEN** el `ingresado_en` propagado es el valor sellado por el backend y no un instante calculado en n8n

#### Scenario: Correo sella al recoger el mensaje

- **WHEN** el trigger de Outlook recoge un mensaje
- **THEN** el ingreso capturado para ese mensaje es el instante de inicio del flujo del trigger (recogida del poller), no su `receivedDateTime`

#### Scenario: Web usa el instante de recepcion

- **WHEN** el webhook del formulario web recibe un envio
- **THEN** el ingreso capturado es el instante de recepción del webhook

#### Scenario: Propagacion al normalizador

- **WHEN** una entrada atraviesa el nodo de normalizacion
- **THEN** la estructura normalizada contiene el campo `ingresado_en`

### Requirement: N8N-GUARD-002 — El caller de la guarda usa el item corriente, sin referencia frágil

El cuerpo del nodo `Guard de costo` SHALL resolver el número de origen llamante (`caller`) desde el item corriente del propio nodo (el payload del handoff, campo `caller`) y MUST NOT usar la referencia `$('Sellar ingreso telefonia').item`, que depende de la resolución de `pairedItem` y puede devolver `null` sin señal. Como el nodo de sellado es la entrada directa de la guarda, el item corriente YA contiene el `caller` entregado por el backend, por lo que no se requiere una referencia cruzada entre nodos. La ausencia del número de origen MUST NOT impedir la evaluación de la guarda: `caller` es opcional y la reserva SHALL continuar.

#### Scenario: El cuerpo de la guarda usa el item corriente y ninguna referencia cruzada

- **WHEN** la suite estructural inspecciona el body del nodo `Guard de costo`
- **THEN** el body resuelve `caller` desde `$json` y NO referencia `$('Sellar ingreso telefonia')` (ni por `.item` ni por `.first()`)

#### Scenario: La ausencia del caller no impide la guarda

- **WHEN** el item sellado no expone un número de origen
- **THEN** el body resuelve `caller` a `null` y la guarda igual evalúa la reserva, sin abortar el flujo

## ADDED Requirements

### Requirement: N8N-PHONE-003 — La rama telefónica consume el handoff pseudonimizado del backend

El webhook del canal de telefonía SHALL aceptar exactamente el payload del handoff del backend con la descripción pseudonimizada, el `CallSid`, el número llamante y el `ingresado_en` sellado. El `AI Agent` SHALL recibir como entrada la descripción pseudonimizada y MUST NOT recibir el transcript crudo. El nodo HTTP de persistencia SHALL enviar el `CallSid` como `origen_message_id`, de modo que reutilice el índice único existente para la idempotencia del alta. El workflow MUST NOT recalcular ni re-sellar el instante de ingreso.

#### Scenario: El webhook recibe el payload del handoff

- **WHEN** el backend invoca el webhook de telefonía
- **THEN** el payload contiene la descripción pseudonimizada, el `CallSid`, el llamante y el `ingresado_en`

#### Scenario: El AI Agent consume la descripción pseudonimizada

- **WHEN** el flujo de telefonía alcanza el `AI Agent`
- **THEN** el prompt del agente interpola la descripción pseudonimizada del handoff y no un transcript crudo

#### Scenario: El CallSid se envía como identificador de origen

- **WHEN** el nodo HTTP de persistencia envía el alta de un incidente telefónico
- **THEN** el cuerpo incluye `origen_message_id` con el `CallSid` del handoff

### Requirement: N8N-PHONE-004 — El sello de ingreso de telefonía es un passthrough del backend

El nodo que sella el ingreso de telefonía SHALL comportarse como un passthrough del `ingresado_en` entregado por el backend y MUST NOT generar un instante nuevo con el reloj de n8n. El valor propagado SHALL ser el del handoff, de modo que la latencia end-to-end incluya el trabajo de transcripción del backend.

#### Scenario: El sello no se regenera en n8n

- **WHEN** se inspecciona el código del nodo que sella el ingreso de telefonía
- **THEN** el código propaga el `ingresado_en` del payload y no construye un instante nuevo

#### Scenario: El valor propagado es el del backend

- **WHEN** el handoff trae un `ingresado_en` con zona horaria
- **THEN** ese mismo valor llega al nodo de normalización y al POST de persistencia