## ADDED Requirements

### Requirement: N8N-TIMING-001 — Captura del instante de ingreso en el borde del trigger

Cada trigger del workflow SHALL capturar el instante de ingreso en su borde, antes de cualquier procesamiento del canal. En el canal de telefonia la captura SHALL ocurrir ANTES del nodo `AI Agent`, de modo que la latencia incluya el tiempo del agente pago. En el canal de correo la captura SHALL ocurrir al INICIO del flujo del trigger de Outlook, en el instante en que el poller recoge el mensaje, y MUST NOT usar el `receivedDateTime` del mensaje. En el canal web la captura SHALL usar el instante de recepcion del webhook. El valor SHALL propagarse al normalizador y SHALL estar disponible para el nodo HTTP de persistencia.

#### Scenario: Telefonia captura antes del agente

- **WHEN** la suite estructural inspecciona el workflow
- **THEN** el nodo que captura el ingreso de telefonia esta aguas arriba del `AI Agent`

#### Scenario: Correo sella al recoger el mensaje

- **WHEN** el trigger de Outlook recoge un mensaje
- **THEN** el ingreso capturado para ese mensaje es el instante de inicio del flujo del trigger (recogida del poller), no su `receivedDateTime`

#### Scenario: Web usa el instante de recepcion

- **WHEN** el webhook del formulario web recibe un envio
- **THEN** el ingreso capturado es el instante de recepcion del webhook

#### Scenario: Propagacion al normalizador

- **WHEN** una entrada atraviesa el nodo de normalizacion
- **THEN** la estructura normalizada contiene el campo `ingresado_en`

### Requirement: N8N-TIMING-002 — El POST de persistencia envia el instante de ingreso

El body del nodo HTTP de persistencia SHALL incluir `ingresado_en` con la expresion que resuelve al instante capturado en el borde del trigger. El valor SHALL estar en formato ISO-8601 con zona horaria. El host del backend SHALL seguir resolviendose con `$env.BACKEND_URL` y el body MUST NOT incluir credenciales.

#### Scenario: El body incluye ingresado_en

- **WHEN** la suite estructural inspecciona el body del nodo `HTTP POST a MTM-SRU`
- **THEN** el body contiene una entrada `ingresado_en` resuelta por expresion, no una constante

#### Scenario: Formato ISO-8601 con zona horaria

- **WHEN** se inspecciona el valor capturado para `ingresado_en`
- **THEN** el valor es un instante ISO-8601 con sufijo `Z` u offset explicito

#### Scenario: Sin hardcodeo de host ni credenciales

- **WHEN** se inspecciona la URL y el body del nodo HTTP de persistencia
- **THEN** el host se resuelve con `$env.BACKEND_URL` y no hay tokens ni credenciales embebidas
