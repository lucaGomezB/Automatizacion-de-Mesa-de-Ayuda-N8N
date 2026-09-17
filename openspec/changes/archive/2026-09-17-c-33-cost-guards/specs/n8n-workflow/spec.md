## ADDED Requirements

### Requirement: N8N-REFINE-001 — Tope de refinamiento del agente pago

El canal telefonico SHALL limitar a un maximo de 2 el numero de intentos de clasificacion/refinamiento del `AI Agent`. El workflow SHALL contabilizar los intentos y, al agotarse el tope sin una clasificacion valida, SHALL derivar el incidente a un nodo terminal que lo persiste con `requiere_revision_humana=true` y `confianza=0.0`, MUST NOT volver a invocar al agente pago. El refinamiento dentro del tope SHALL conservarse.

#### Scenario: Un fallo dentro del tope reintenta una vez

- **WHEN** la validacion de la respuesta del agente falla en el primer intento y el tope aun no se agoto
- **THEN** el flujo reingresa al `AI Agent` para un unico intento adicional

#### Scenario: Al agotar el tope no se reinvoca al agente pago

- **WHEN** el refinamiento alcanza el tope de 2 intentos sin una clasificacion valida
- **THEN** el flujo NO reingresa al `AI Agent`, persiste el incidente con `requiere_revision_humana=true` y termina

#### Scenario: Clasificacion valida dentro del tope sigue el flujo normal

- **WHEN** el agente produce una clasificacion valida dentro del tope
- **THEN** el flujo continua hacia la normalizacion y el ruteo por umbral como hasta ahora

#### Scenario: El tope es verificable en el workflow exportado

- **WHEN** la suite estructural inspecciona el nodo `AI Agent` y sus conexiones de refinamiento
- **THEN** existe un tope explicito de intentos (por ejemplo `maxIterations` o un contador) y una ruta terminal que no reinvoca al agente

### Requirement: N8N-EMAIL-LIFECYCLE-001 — El correo se marca como leido en todas las ramas terminales

Para el canal de correo, el workflow SHALL marcar el mensaje como leido en TODAS las ramas terminales alcanzables: exito, rechazo por validacion y error o fallo. Un mensaje cuyo incidente no se creo MUST NOT permanecer sin leer de modo que el trigger lo reprocese automaticamente.

#### Scenario: Rama de exito marca el correo como leido

- **WHEN** un correo valido crea el incidente con exito
- **THEN** el mensaje queda marcado como leido

#### Scenario: Rama de rechazo marca el correo como leido

- **WHEN** un correo es rechazado por la validacion de datos
- **THEN** el mensaje queda marcado como leido y no se reprocesa cada minuto

#### Scenario: Rama de error o fallo marca el correo como leido

- **WHEN** el procesamiento de un correo falla antes o durante la persistencia del incidente
- **THEN** el flujo alcanza un camino que marca el mensaje como leido

#### Scenario: Un correo procesado no se re-procesa

- **WHEN** un correo ya fue procesado por cualquiera de las ramas terminales
- **THEN** el trigger no lo vuelve a levantar como no leido

### Requirement: N8N-BACKLOG-001 — Lookback acotado en el trigger de correo

El trigger de Outlook SHALL acotar los mensajes elegibles con un filtro de fecha sobre `receivedDateTime`, con un lookback de 24 horas, de modo que el arranque del sistema no procese todo el historial no leido. El valor del lookback SHALL quedar declarado en el workflow exportado.

#### Scenario: Solo los mensajes recientes son elegibles

- **WHEN** el trigger de Outlook evalua los mensajes no leidos
- **THEN** los mensajes con `receivedDateTime` anterior al lookback no son procesados

#### Scenario: El lookback queda declarado en el workflow

- **WHEN** la suite estructural inspecciona el trigger de Outlook
- **THEN** existe un filtro de fecha explicito con un lookback de 24 horas

### Requirement: N8N-INTAKE-001 — El POST al backend envia Message-ID, clasificacion precalculada y origen

El nodo HTTP de persistencia SHALL enviar al backend, ademas de la descripcion y el canal, la clasificacion ya producida por el agente cuando este disponible (sector predicho y confianza), el `Message-ID` de Outlook cuando el canal sea correo, y un marcador explicito de origen/evento. El workflow MUST NOT descartar la clasificacion ya producida cuando el backend puede aceptarla sin reclasificar.

#### Scenario: El POST telefonico incluye la clasificacion precalculada

- **WHEN** un incidente telefonico clasificado por el agente llega al nodo HTTP de persistencia
- **THEN** el cuerpo enviado al backend incluye el sector predicho y la confianza producidos por el agente

#### Scenario: El POST de correo incluye el Message-ID de origen

- **WHEN** un incidente del canal correo llega al nodo HTTP de persistencia
- **THEN** el cuerpo enviado al backend incluye el `origen_message_id` tomado del mensaje de Outlook

#### Scenario: El marcador de origen es explicito

- **WHEN** se inspecciona el cuerpo que el nodo HTTP envia al backend
- **THEN** contiene un marcador explicito de origen/evento que identifica al canal emisor
