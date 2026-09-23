## MODIFIED Requirements

### Requirement: Notificación al usuario post-registro por canal

Tras un alta exitosa del incidente (respuesta `201 Created` del backend), el workflow N8N SHALL notificar al usuario por el canal correspondiente, mediante nodos de notificación posteriores al nodo `httpRequest` de persistencia: una respuesta de confirmación al webhook web (con el número de incidente) para el canal `web`, un correo de confirmación para el canal `correo` y una notificación por SMS al número llamante para el canal de telefonía. La notificación SHALL ocurrir también cuando el incidente se crea con `requiere_revision_humana = true`, porque el usuario SIEMPRE debe recibir el número. La confirmación del canal de telefonía MUST NOT resolverse mediante la respuesta TwiML de la llamada, porque el alta es asíncrona y el TwiML de cierre desconoce el número. La notificación SHALL ocurrir solo cuando la creación del incidente fue exitosa y NO SHALL bloquear el registro de auditoría.

#### Scenario: Confirmación web tras alta exitosa

- **WHEN** un incidente del canal `web` se crea con `201 Created`
- **THEN** el workflow responde al webhook web con una confirmación que incluye el identificador del incidente

#### Scenario: Confirmación por correo tras alta exitosa

- **WHEN** un incidente del canal `correo` se crea con `201 Created`, con o sin revisión humana
- **THEN** el workflow envía un correo de confirmación al usuario del canal de correo con el número de incidente

#### Scenario: Notificación telefónica por SMS tras alta exitosa

- **WHEN** un incidente del canal `telefonía` se crea con `201 Created` y el número llamante está disponible
- **THEN** el usuario recibe el número de incidente por SMS y no mediante el TwiML de la llamada

#### Scenario: Sin notificación cuando no hubo alta

- **WHEN** la creación del incidente no resulta en `201 Created` (validación fallida)
- **THEN** el workflow no emite la notificación de confirmación de alta al usuario

### Requirement: N8N-EMAIL-002 — Destinatario de confirmación resuelto desde el remitente original

El nodo `Correo de confirmacion al usuario` SHALL resolver `toRecipients` desde el remitente original propagado en la estructura normalizada (campo `remitente`) y MUST NOT depender del ítem corriente posterior al POST, que es la respuesta del backend y no expone `remitente` ni `from`. La estructura normalizada SHALL propagar `remitente` desde el payload del trigger de correo (`from`), admitiendo que el remitente llegue tanto como cadena de texto como como objeto estructurado que anida la dirección (`from.emailAddress.address`); la normalización SHALL extraer la dirección de correo efectiva en ambos casos y SHALL descartar, con señal observable, un remitente que no resuelva a una dirección válida. El campo `remitente` MUST NOT agregarse al cuerpo del POST hacia el backend ni al registro de auditoría, por ser dato personal.

#### Scenario: Un correo con remitente produce destinatario no vacío

- **WHEN** un correo con remitente válido llega al nodo de confirmación por la rama del canal correo
- **THEN** `toRecipients` resuelve a una dirección no vacía tomada de la estructura normalizada

#### Scenario: Remitente en forma de objeto resuelve la dirección

- **WHEN** el `from` del mensaje entrante es un objeto estructurado con la dirección anidada
- **THEN** la normalización extrae la dirección de correo efectiva y `toRecipients` la usa

#### Scenario: Remitente inválido no produce destinatario inválido

- **WHEN** el remitente entrante no puede resolverse a una dirección válida
- **THEN** la normalización lo descarta con una señal observable y no propaga una representación inválida como destinatario

#### Scenario: La expresión referencia el nodo normalizador

- **WHEN** la suite estructural inspecciona `toRecipients` del nodo de confirmación
- **THEN** la expresión referencia `Normalizar entrada del incidente` (aguas arriba) y no solo el ítem corriente

#### Scenario: El remitente no contamina el payload ni la auditoría

- **WHEN** se inspecciona el cuerpo del POST de persistencia y el código del nodo de auditoría
- **THEN** ninguno de los dos incluye el campo `remitente`

### Requirement: N8N-PHONE-002 — La confirmación telefónica no usa el nodo de correo

Las salidas de telefonía y fallback del switch `Rutear por canal de origen` MUST NOT conectarse al nodo `Correo de confirmacion al usuario`. La confirmación del canal telefonía SHALL resolverse mediante el SMS al número llamante y MUST NOT depender de la respuesta TwiML de la llamada, que no conoce el número porque el alta es asíncrona. La salida del canal correo SHALL conservar su nodo de confirmación por correo.

#### Scenario: La salida de telefonía no alcanza el nodo de correo

- **WHEN** la suite estructural inspecciona los sucesores de la salida de telefonía del switch
- **THEN** `Correo de confirmacion al usuario` no es alcanzable desde esa salida

#### Scenario: El fallback no alcanza el nodo de correo

- **WHEN** la suite estructural inspecciona los sucesores de la salida fallback del switch
- **THEN** `Correo de confirmacion al usuario` no es alcanzable desde esa salida

#### Scenario: La salida de correo conserva su confirmación

- **WHEN** el canal normalizado es `correo`
- **THEN** el flujo alcanza el nodo `Correo de confirmacion al usuario`

#### Scenario: La confirmación telefónica no es TwiML

- **WHEN** se inspecciona el mecanismo de confirmación del canal de telefonía en el workflow
- **THEN** no existe un cierre TwiML que presente el número de incidente como mecanismo de confirmación

### Requirement: N8N-WEBHOOK-003 — Cierre de todas las ramas terminales del webhook web

El webhook `Webhook formulario web`, configurado con `responseMode: responseNode`, SHALL alcanzar un nodo `respondToWebhook` en TODAS las ramas que atienden una petición del canal web: alta exitosa, rechazo por validación de entrada, error del backend y derivación a revisión humana. En las ramas que derivan a revisión humana con el incidente YA creado, la respuesta SHALL incluir el número del incidente creado y MUST NOT presentar un identificador nulo. En las ramas donde no hubo alta, la respuesta SHALL declarar explícitamente que no hubo alta, sin presentar un número inexistente. El workflow SHALL incluir una guarda de canal web que restrinja la respuesta de cierre a las peticiones cuyo `canal_origen` sea `web`, de modo que las ramas compartidas con correo y telefonía no disparen respuestas web. Ninguna petición web SHALL quedar a la espera indefinida de respuesta.

#### Scenario: El alta web exitosa responde con el identificador

- **WHEN** un incidente del canal web se crea con `201 Created`
- **THEN** el flujo alcanza un `respondToWebhook` que responde con el identificador del incidente

#### Scenario: La revisión humana responde al cliente web

- **WHEN** el backend marca un incidente web con `requiere_revision_humana = true`
- **THEN** el flujo alcanza un `respondToWebhook` de cierre y el cliente recibe una respuesta

#### Scenario: La revisión humana web responde con el identificador

- **WHEN** el backend crea un incidente web con `requiere_revision_humana = true`
- **THEN** el flujo alcanza un `respondToWebhook` que responde con el identificador del incidente creado y no con un valor nulo

#### Scenario: El rechazo por validación responde al cliente web

- **WHEN** una petición del canal web es rechazada por la validación de entrada (rama falsa de `Entrada valida`)
- **THEN** el flujo alcanza un `respondToWebhook` de cierre que declara que no hubo alta y el cliente recibe una respuesta, sin espera indefinida

#### Scenario: El error del backend responde al cliente web

- **WHEN** el POST de persistencia de una petición web falla y emite por su salida de error (`main#1`)
- **THEN** el flujo alcanza un `respondToWebhook` de cierre y el cliente recibe una respuesta

#### Scenario: La guarda de canal evita respuestas web cruzadas

- **WHEN** una rama compartida que no proviene del canal web evalúa la guarda `Es web?`
- **THEN** la guarda es falsa y el flujo no emite una respuesta de webhook web para ese canal

### Requirement: N8N-DOC-001 — La guía del workflow refleja el estado real

`docs/n8n-workflow-guide.md` SHALL declarar un conteo de nodos y un conteo de pruebas estructurales que coincidan con `n8n/workflow.json` y con la suite `App/Backend/tests/test_n8n_workflow.py` respectivamente. La guía MUST NOT contener excepciones conocidas obsoletas, en particular la afirmación de que la rama de revisión humana no marca el correo como leído cuando el cableado actual sí lo hace, y MUST NOT afirmar que la confirmación del canal de telefonía ocurre en la respuesta TwiML o en un `<Say>` de cierre, porque la notificación telefónica se realiza por SMS.

#### Scenario: El conteo de nodos coincide con el JSON

- **WHEN** se compara el conteo de nodos declarado en la guía contra `n8n/workflow.json`
- **THEN** ambos conteos coinciden

#### Scenario: El conteo de pruebas coincide con la suite

- **WHEN** se compara el conteo de pruebas estructurales declarado en la guía contra la suite `test_n8n_workflow.py`
- **THEN** ambos conteos coinciden

#### Scenario: No queda la excepción obsoleta de la rama de revisión

- **WHEN** se inspecciona la sección de ciclo de vida del correo de la guía
- **THEN** la guía no afirma que la rama de revisión humana deja el correo sin marcar como leído

#### Scenario: La guía no afirma confirmación telefónica por TwiML

- **WHEN** se inspecciona la sección de notificación al usuario de la guía
- **THEN** la guía no afirma que la confirmación telefónica ocurre en la respuesta TwiML ni en el `<Say>` de cierre

## ADDED Requirements

### Requirement: N8N-EMAIL-003 — Confirmación de correo en la rama de revisión humana del canal correo

El workflow SHALL disparar el nodo `Correo de confirmacion al usuario` en la rama de correo tanto cuando `requiere_revision_humana = false` como cuando `requiere_revision_humana = true`, de modo que el usuario del canal correo reciba siempre el número de incidente. El envío SHALL ser tolerante a fallos (`onError: continueRegularOutput`) para no abortar el registro de auditoría ni el marcado del correo como leído.

#### Scenario: La rama de revisión humana del correo alcanza la confirmación

- **WHEN** un incidente del canal correo se deriva a revisión humana
- **THEN** el flujo de la rama de revisión humana alcanza el nodo `Correo de confirmacion al usuario`

#### Scenario: La rama normal del correo conserva la confirmación

- **WHEN** un incidente del canal correo se crea sin revisión humana
- **THEN** el flujo de la rama normal alcanza el nodo `Correo de confirmacion al usuario`

#### Scenario: El fallo de envío no aborta la auditoría

- **WHEN** el envío del correo de confirmación falla
- **THEN** el workflow continúa y el registro de auditoría y el marcado del correo como leído no se ven interrumpidos

### Requirement: N8N-WEBHOOK-004 — Distinción entre cierre con alta y cierre sin alta

El workflow SHALL distinguir, en las respuestas de cierre del webhook web, entre una petición que produjo un incidente (aun derivado a revisión humana) y una que no lo produjo. La respuesta de cierre de una petición sin incidente SHALL declarar la ausencia de alta; la respuesta de cierre de una petición con incidente creado SHALL incluir el número. La guarda de canal web SHALL seguir restringiendo estas respuestas al canal `web`.

#### Scenario: Revisión humana con incidente responde con el número

- **WHEN** la rama de revisión humana del canal web tiene un incidente creado
- **THEN** la respuesta de cierre incluye el número del incidente

#### Scenario: Sin incidente responde sin número

- **WHEN** una rama terminal del canal web no produjo un incidente
- **THEN** la respuesta de cierre declara que no hubo alta y no incluye un número

#### Scenario: La guarda de canal se mantiene

- **WHEN** una rama de cierre evalúa la guarda de canal web
- **THEN** solo las peticiones del canal `web` reciben la respuesta de cierre