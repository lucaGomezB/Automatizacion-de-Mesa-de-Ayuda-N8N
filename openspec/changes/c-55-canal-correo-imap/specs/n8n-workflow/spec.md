# Delta for n8n-workflow

## MODIFIED Requirements

### Requirement: Normalización de canales a estructura unificada

El workflow N8N SHALL incluir un nodo de normalización que homogenice la entrada de cualquiera de los tres canales (correo electrónico, formulario web, telefonía con transcripción) en una estructura unificada con exactamente los campos `id`, `timestamp` (precisión al milisegundo), `canal_origen` (uno de `correo`, `web`, `telefonia`) y `descripcion`. Los nodos posteriores SHALL operar exclusivamente sobre esta estructura y no sobre la forma cruda de cada canal. Para el canal de correo, la normalización SHALL consumir los campos genéricos del mensaje IMAP (remitente, asunto, cuerpo de texto y fecha de recepción) y NO SHALL depender de campos propios de un proveedor.
(Previously: el escenario de correo referenciaba el disparador de Outlook y campos específicos de ese proveedor.)

#### Scenario: Correo electrónico normalizado

- **WHEN** el disparador IMAP recibe un correo y su carga pasa por el nodo de normalización
- **THEN** la salida contiene `id`, `timestamp` con precisión al milisegundo, `canal_origen = "correo"` y `descripcion` con el cuerpo del incidente

#### Scenario: Transcripción telefónica normalizada

- **WHEN** el AI Agent parsea la transcripción de una llamada Twilio y su salida pasa por el nodo de normalización
- **THEN** la salida contiene los mismos cuatro campos con `canal_origen = "telefonia"`

#### Scenario: Canal de origen inválido rechazado

- **WHEN** la normalización recibe una entrada cuyo canal no es `correo`, `web` ni `telefonia`
- **THEN** el flujo no produce una estructura unificada válida y deriva la entrada a revisión humana

### Requirement: Trigger del canal de correo identificado

El workflow N8N SHALL incluir un disparador de correo electrónico genérico (nodo `n8n-nodes-base.emailReadImap`) que sondee los mensajes no leídos de la casilla de mesa de ayuda con un lookback de 24 horas y marque como leído cada mensaje que recolecta, de modo que no requiera un nodo separado de marcado. La salida del disparador SHALL quedar marcada con `canal_raw = "correo"` de forma explícita antes de llegar al nodo de normalización, de modo que el normalizador asigne `canal_origen = "correo"` sin ambigüedad. El canal MUST NOT depender de Microsoft Entra OAuth2 ni de un registro de aplicación en la nube.
(Previously: el disparador era `microsoftOutlookTrigger` sobre Microsoft Entra OAuth2, sin marcado en el propio trigger.)

#### Scenario: El disparador de correo existe y alimenta el flujo

- **WHEN** se inspecciona el workflow exportado
- **THEN** existe un nodo `n8n-nodes-base.emailReadImap` cuya salida fluye, a través del nodo de validación de correo, hacia el nodo de normalización

#### Scenario: El canal de correo queda identificado como "correo"

- **WHEN** una entrada del disparador IMAP atraviesa el flujo hasta la normalización
- **THEN** el `canal_raw` propagado es `"correo"` y la estructura unificada resultante tiene `canal_origen = "correo"`

#### Scenario: El trigger recolecta solo correo no leído y lo marca leído

- **WHEN** el disparador IMAP sondea la casilla y encuentra mensajes no leídos dentro del lookback
- **THEN** los recolecta y los marca como leídos en el propio trigger, sin un nodo posterior de marcado

### Requirement: N8N-EMAIL-LIFECYCLE-001 — El correo se marca como leido en todas las ramas terminales

Para el canal de correo, el disparador IMAP SHALL marcar el mensaje como leído al recolectarlo, de modo que el marcado quede garantizado en TODAS las ramas terminales alcanzables (éxito, rechazo por validación y error o fallo) sin depender de la rama ejecutada. El nodo dedicado `Marcar correo como leido` SHALL eliminarse del workflow. Un mensaje cuyo incidente no se creó MUST NOT permanecer sin leer de modo que el trigger lo reprocese automáticamente.
(Previously: el marcado se resolvía mediante el nodo `Marcar correo como leido` en cada rama terminal.)

#### Scenario: Rama de exito marca el correo como leido

- **WHEN** un correo válido crea el incidente con exito
- **THEN** el mensaje queda marcado como leido

#### Scenario: Rama de rechazo marca el correo como leido

- **WHEN** un correo es rechazado por la validacion de datos
- **THEN** el mensaje queda marcado como leido y no se reprocesa cada ciclo de polling

#### Scenario: Rama de error o fallo marca el correo como leido

- **WHEN** el procesamiento de un correo falla antes o durante la persistencia del incidente
- **THEN** el mensaje igualmente queda marcado como leido porque el marcado ocurre en el trigger

#### Scenario: Un correo procesado no se re-procesa

- **WHEN** un correo ya fue procesado por cualquiera de las ramas terminales
- **THEN** el trigger no lo vuelve a levantar como no leido

#### Scenario: El nodo dedicado de marcado ya no existe

- **WHEN** la suite estructural inspecciona los nodos del workflow exportado
- **THEN** no existe un nodo `Marcar correo como leido` y el marcado se resuelve en el disparador IMAP

### Requirement: N8N-BACKLOG-001 — Lookback acotado en el trigger de correo

El disparador IMAP SHALL acotar los mensajes elegibles a los recibidos dentro de las últimas 24 horas, de modo que el arranque del sistema no procese todo el historial no leído. El valor del lookback SHALL quedar declarado en la configuración del trigger en el workflow exportado.
(Previously: el filtro de fecha se aplicaba sobre el campo `receivedDateTime` del trigger de Outlook.)

#### Scenario: Solo los mensajes recientes son elegibles

- **WHEN** el trigger IMAP evalua los mensajes no leidos
- **THEN** los mensajes recibidos antes del lookback no son procesados

#### Scenario: El lookback queda declarado en el workflow

- **WHEN** la suite estructural inspecciona el trigger IMAP
- **THEN** existe un filtro explicito con un lookback de 24 horas

### Requirement: N8N-EMAIL-001 — Extraccion del cuerpo del correo en modo simple

El disparador IMAP SHALL exponer el cuerpo del correo en texto plano en el campo genérico `text`. El flujo SHALL extraer la descripcion desde ese campo, de modo que el validador de correo reciba una descripcion no vacia sin depender de campos propios de un proveedor.
(Previously: la extraccion dependia del modo de salida `simple` del trigger de Outlook.)

#### Scenario: Correo valido produce descripcion

- **WHEN** llega un correo con cuerpo de texto
- **THEN** la validacion de correo extrae la descripcion del campo `text` y la marca como valida si cumple el minimo

#### Scenario: El cuerpo no se pierde por el modo de salida

- **WHEN** el disparador IMAP entrega un mensaje cuyo cuerpo no esta disponible en la raiz del payload
- **THEN** el flujo obtiene el texto desde el campo generico `text` de la ruta efectiva del payload del trigger, sin depender de un campo exclusivo de Outlook

### Requirement: N8N-INTAKE-001 — El POST al backend envia Message-ID, clasificacion precalculada y origen

El nodo HTTP de persistencia SHALL enviar al backend, ademas de la descripcion y el canal, la clasificacion ya producida por el agente cuando este disponible (sector predicho y confianza), el `Message-ID` del mensaje IMAP cuando el canal sea correo, y un marcador explicito de origen/evento. El workflow MUST NOT descartar la clasificacion ya producida cuando el backend puede aceptarla sin reclasificar.
(Previously: el `Message-ID` se tomaba del mensaje de Outlook.)

#### Scenario: El POST telefonico incluye la clasificacion precalculada

- **WHEN** un incidente telefonico clasificado por el agente llega al nodo HTTP de persistencia
- **THEN** el cuerpo enviado al backend incluye el sector predicho y la confianza producidos por el agente

#### Scenario: El POST de correo incluye el Message-ID de origen

- **WHEN** un incidente del canal correo llega al nodo HTTP de persistencia
- **THEN** el cuerpo enviado al backend incluye el `origen_message_id` tomado del mensaje IMAP

#### Scenario: El marcador de origen es explicito

- **WHEN** se inspecciona el cuerpo que el nodo HTTP envia al backend
- **THEN** contiene un marcador explicito de origen/evento que identifica al canal emisor

### Requirement: N8N-TIMING-001 — Captura del instante de ingreso en el borde del trigger

Cada trigger del workflow SHALL capturar el instante de ingreso en su borde, antes de cualquier procesamiento del canal. En el canal de telefonia la captura SHALL ocurrir ANTES del nodo `AI Agent`. En el canal de correo la captura SHALL ocurrir al INICIO del flujo del disparador IMAP, en el instante en que el poller recoge el mensaje, y MUST NOT reinterpretar la fecha de recepción del mensaje (`date`) como instante de ingreso. En el canal web la captura SHALL usar el instante de recepcion del webhook. El valor SHALL propagarse al normalizador y SHALL estar disponible para el nodo HTTP de persistencia.
(Previously: el requisito nombraba el trigger de Outlook y prohibía usar su `receivedDateTime`.)

#### Scenario: Telefonia captura antes del agente

- **WHEN** la suite estructural inspecciona el workflow
- **THEN** el nodo que captura el ingreso de telefonia esta aguas arriba del `AI Agent`

#### Scenario: Correo sella al recoger el mensaje

- **WHEN** el disparador IMAP recoge un mensaje
- **THEN** el ingreso capturado para ese mensaje es el instante de inicio del flujo del trigger (recogida del poller), no la fecha `date` del mensaje

#### Scenario: Web usa el instante de recepcion

- **WHEN** el webhook del formulario web recibe un envio
- **THEN** el ingreso capturado es el instante de recepcion del webhook

#### Scenario: Propagacion al normalizador

- **WHEN** una entrada atraviesa el nodo de normalizacion
- **THEN** la estructura normalizada contiene el campo `ingresado_en`

### Requirement: Notificacion al operador designado

Cuando el backend marca un incidente con `requiere_revision_humana = true`, el workflow SHALL notificar a un operador designado mediante un correo electrónico enviado por el nodo `Notificar operador designado` (`n8n-nodes-base.emailSend` sobre SMTP), dirigido a la dirección configurada en la variable de entorno `OPERATOR_EMAIL`. La notificación SHALL conservar el asunto, el cuerpo y el destinatario vigentes, SHALL ocurrir en la rama verdadera del gate post-POST `Requiere revision humana`, antes del registro de auditoría, y NO SHALL emitirse cuando el flag es falso.
(Previously: el envío usaba el nodo `microsoftOutlook` sobre Microsoft Entra OAuth2.)

#### Scenario: Se notifica al operador cuando el backend pide revisión

- **WHEN** el response del backend tiene `requiere_revision_humana = true`
- **THEN** el nodo `Notificar operador designado` envía un correo por SMTP a la dirección de `$env.OPERATOR_EMAIL` y luego se registra la auditoría

#### Scenario: No se notifica cuando no hace falta revisión

- **WHEN** el response del backend tiene `requiere_revision_humana = false`
- **THEN** el flujo no envía la notificación al operador y continúa con las confirmaciones por canal

#### Scenario: La rama de revisión marca el correo como leído

- **WHEN** un incidente del canal correo requiere revisión humana
- **THEN** el mensaje ya quedó marcado como leído por el disparador IMAP, de modo que el trigger no lo reprocesa

#### Scenario: La notificación no depende de Entra OAuth2

- **WHEN** la suite estructural inspecciona el nodo `Notificar operador designado`
- **THEN** el nodo es de tipo `n8n-nodes-base.emailSend` y no declara credenciales `microsoftOutlook*`

## ADDED Requirements

### Requirement: Envío de correo saliente por SMTP

El workflow SHALL enviar tanto la confirmación al usuario (`Correo de confirmacion al usuario`) como la notificación al operador designado (`Notificar operador designado`) mediante nodos `n8n-nodes-base.emailSend` sobre SMTP, conservando los asuntos, los cuerpos y los destinatarios vigentes. Los nodos de envío MUST NOT depender de Microsoft Entra OAuth2 ni de un registro de aplicación en la nube.

#### Scenario: La confirmación al usuario sale por SMTP

- **WHEN** un incidente del canal correo se crea con `201 Created`
- **THEN** el nodo `Correo de confirmacion al usuario` envía el correo por SMTP al remitente original

#### Scenario: La notificación al operador sale por SMTP

- **WHEN** el backend marca un incidente con `requiere_revision_humana = true`
- **THEN** el nodo `Notificar operador designado` envía el correo por SMTP a `$env.OPERATOR_EMAIL`

#### Scenario: El envío saliente no usa nodos de Outlook

- **WHEN** la suite estructural inspecciona los nodos de envío de correo del workflow exportado
- **THEN** no existen nodos de tipo `microsoftOutlook` y ambos envíos son `n8n-nodes-base.emailSend`

### Requirement: Autenticación IMAP/SMTP sin secretos versionados

El canal de correo SHALL autenticarse con una credencial IMAP/SMTP (host, usuario y App Password) declarada por el disparador IMAP y por los nodos de envío. El workflow exportado MUST NOT contener secretos ni credenciales embebidas, y MUST NOT declarar credenciales `microsoftOutlookOAuth2Api`.

#### Scenario: La credencial IMAP/SMTP queda declarada

- **WHEN** la suite estructural inspecciona el disparador IMAP y los nodos `emailSend`
- **THEN** cada uno declara una entrada de credencial IMAP/SMTP no vacía en su configuración

#### Scenario: El workflow no versiona secretos

- **WHEN** se inspecciona `n8n/workflow.json`
- **THEN** no contiene contraseñas, App Passwords ni secretos embebidos, solo la referencia a la credencial

#### Scenario: El canal no depende de Entra

- **WHEN** la suite estructural busca credenciales de Microsoft en el workflow exportado
- **THEN** no existe ninguna credencial `microsoftOutlookOAuth2Api` ni nodo `microsoftOutlook*`

## REMOVED Requirements

### Requirement: Trigger de Outlook entrega la descripción al validador

**Reason**: el disparador `microsoftOutlookTrigger` se reemplaza por el disparador IMAP genérico; la disponibilidad de la descripción para el validador queda cubierta por el requisito "Trigger del canal de correo identificado" y por N8N-EMAIL-001.
**Migration**: usar el disparador `n8n-nodes-base.emailReadImap` y extraer la descripción desde el campo genérico `text` del mensaje, que el validador ya contempla.
