## ADDED Requirements

### Requirement: N8N-WEBHOOK-003 — Cierre de todas las ramas terminales del webhook web

El webhook `Webhook formulario web`, configurado con `responseMode: responseNode`, SHALL alcanzar un nodo `respondToWebhook` en TODAS las ramas que atienden una petición del canal web: alta exitosa, rechazo por validación de entrada, error del backend y derivación a revisión humana. El workflow SHALL incluir una guarda de canal web que restrinja la respuesta de cierre a las peticiones cuyo `canal_origen` sea `web`, de modo que las ramas compartidas con correo y telefonía no disparen respuestas web. Ninguna petición web SHALL quedar a la espera indefinida de respuesta.

#### Scenario: El alta web exitosa responde con el identificador

- **WHEN** un incidente del canal web se crea con `201 Created`
- **THEN** el flujo alcanza un `respondToWebhook` que responde con el identificador del incidente

#### Scenario: El rechazo por validación responde al cliente web

- **WHEN** una petición del canal web es rechazada por la validación de entrada (rama falsa de `Entrada valida`)
- **THEN** el flujo alcanza un `respondToWebhook` de cierre y el cliente recibe una respuesta, sin espera indefinida

#### Scenario: El error del backend responde al cliente web

- **WHEN** el POST de persistencia de una petición web falla y emite por su salida de error (`main#1`)
- **THEN** el flujo alcanza un `respondToWebhook` de cierre y el cliente recibe una respuesta

#### Scenario: La revisión humana responde al cliente web

- **WHEN** el backend marca un incidente web con `requiere_revision_humana = true`
- **THEN** el flujo alcanza un `respondToWebhook` de cierre y el cliente recibe una respuesta

#### Scenario: La guarda de canal evita respuestas web cruzadas

- **WHEN** una rama compartida que no proviene del canal web evalúa la guarda `Es web?`
- **THEN** la guarda es falsa y el flujo no emite una respuesta de webhook web para ese canal

### Requirement: N8N-EMAIL-002 — Destinatario de confirmación resuelto desde el remitente original

El nodo `Correo de confirmacion al usuario` SHALL resolver `toRecipients` desde el remitente original propagado en la estructura normalizada (campo `remitente`) y MUST NOT depender del ítem corriente posterior al POST, que es la respuesta del backend y no expone `remitente` ni `from`. La estructura normalizada SHALL propagar `remitente` desde el payload del trigger de correo (`from`). El campo `remitente` MUST NOT agregarse al cuerpo del POST hacia el backend ni al registro de auditoría, por ser dato personal.

#### Scenario: Un correo con remitente produce destinatario no vacío

- **WHEN** un correo con remitente válido llega al nodo de confirmación por la rama del canal correo
- **THEN** `toRecipients` resuelve a una dirección no vacía tomada de la estructura normalizada

#### Scenario: La expresión referencia el nodo normalizador

- **WHEN** la suite estructural inspecciona `toRecipients` del nodo de confirmación
- **THEN** la expresión referencia `Normalizar entrada del incidente` (aguas arriba) y no solo el ítem corriente

#### Scenario: El remitente no contamina el payload ni la auditoría

- **WHEN** se inspecciona el cuerpo del POST de persistencia y el código del nodo de auditoría
- **THEN** ninguno de los dos incluye el campo `remitente`

### Requirement: N8N-PHONE-002 — La confirmación telefónica no usa el nodo de correo

Las salidas de telefonía y fallback del switch `Rutear por canal de origen` MUST NOT conectarse al nodo `Correo de confirmacion al usuario`. La confirmación del canal telefonía SHALL resolverse mediante la respuesta TwiML de la propia llamada y no SHALL requerir un nodo dedicado de correo. La salida del canal correo SHALL conservar su nodo de confirmación por correo.

#### Scenario: La salida de telefonía no alcanza el nodo de correo

- **WHEN** la suite estructural inspecciona los sucesores de la salida de telefonía del switch
- **THEN** `Correo de confirmacion al usuario` no es alcanzable desde esa salida

#### Scenario: El fallback no alcanza el nodo de correo

- **WHEN** la suite estructural inspecciona los sucesores de la salida fallback del switch
- **THEN** `Correo de confirmacion al usuario` no es alcanzable desde esa salida

#### Scenario: La salida de correo conserva su confirmación

- **WHEN** el canal normalizado es `correo`
- **THEN** el flujo alcanza el nodo `Correo de confirmacion al usuario`

### Requirement: N8N-MEMORY-001 — El nodo de memoria Redis declara credencial y parámetros

El nodo `memoryRedisChat` del `AI Agent` telefónico SHALL declarar una credencial `redis` no vacía y parámetros de sesión no vacíos, de modo que la memoria del agente no falle en runtime por configuración ausente. La suite estructural del workflow SHALL incluir el tipo `memoryRedisChat` entre los tipos de nodo que requieren credenciales.

#### Scenario: El nodo de memoria declara su credencial

- **WHEN** la suite estructural inspecciona el nodo `memoryRedisChat`
- **THEN** el nodo declara una entrada de credencial no vacía en su configuración

#### Scenario: El nodo de memoria declara parámetros de sesión

- **WHEN** la suite estructural inspecciona los parámetros del nodo `memoryRedisChat`
- **THEN** sus parámetros no están vacíos e incluyen la configuración de sesión requerida por el nodo

#### Scenario: La suite cubre el tipo de nodo de memoria

- **WHEN** la suite estructural clasifica los nodos que requieren credenciales por su tipo
- **THEN** `memoryRedisChat` está incluido en el conjunto de tipos verificados

### Requirement: N8N-AUTH-002 — El nodo de persistencia autentica con un único mecanismo

El nodo `HTTP POST a MTM-SRU` SHALL declarar exactamente un mecanismo de autenticación hacia el backend. Cuando autentique con el header explícito `Authorization: Bearer` cuyo token se resuelve dinámicamente desde `Login operador`, MUST NOT declarar simultáneamente `authentication`/`genericAuthType` con `httpHeaderAuth` ni una credencial `httpHeaderAuth`, de modo que no se inyecten dos cabeceras `Authorization`. El token MUST NOT ser un valor estático.

#### Scenario: Un solo mecanismo de autenticación

- **WHEN** la suite estructural inspecciona el nodo `HTTP POST a MTM-SRU`
- **THEN** el nodo no combina la autenticación por credencial `httpHeaderAuth` con un header `Authorization` explícito

#### Scenario: El header usa el token dinámico del login

- **WHEN** la suite estructural inspecciona el header `Authorization` del nodo de persistencia
- **THEN** su valor referencia el token obtenido de `Login operador`

#### Scenario: El nodo no declara credencial httpHeaderAuth en conflicto

- **WHEN** la suite estructural inspecciona las credenciales declaradas por el nodo de persistencia
- **THEN** el nodo no declara una credencial `httpHeaderAuth` junto al header explícito

### Requirement: N8N-AUDIT-002 — La auditoría corre también en el camino de error del backend

El nodo `Registro de auditoria` SHALL ser alcanzable desde la salida de error (`main#1`) del nodo `HTTP POST a MTM-SRU`, en paralelo a la guarda de canal, de modo que un fallo del backend quede auditado. El registro de la rama de error SHALL distinguir ese resultado de un alta exitosa y MUST NOT registrarlo como `creado`.

#### Scenario: La salida de error alcanza la auditoría

- **WHEN** la suite estructural inspecciona los sucesores de la salida de error del POST de persistencia
- **THEN** `Registro de auditoria` es alcanzable desde esa salida

#### Scenario: La salida de error conserva la guarda de canal

- **WHEN** la suite estructural inspecciona los sucesores de la salida de error del POST
- **THEN** la guarda `Es correo?` sigue siendo alcanzable desde esa salida (sin regresión del ciclo del correo)

#### Scenario: El error del backend no se audita como alta

- **WHEN** una ejecución llega a la auditoría por la salida de error del POST
- **THEN** el registro resultante tiene un `resultado` distinto de `creado`

### Requirement: N8N-AUDIT-003 — El fallo de notificación no omite la auditoría

El nodo `Notificar operador designado` SHALL declarar manejo de error (`onError: continueRegularOutput` o `continueErrorOutput`) de modo que un fallo en el envío de la notificación no aborte la ejecución antes de `Registro de auditoria`. La auditoría de la rama de revisión humana SHALL ser alcanzable aun cuando la notificación falle.

#### Scenario: El nodo de notificación declara manejo de error

- **WHEN** la suite estructural inspecciona el nodo `Notificar operador designado`
- **THEN** el nodo declara un `onError` de continuación distinto del default de detención

#### Scenario: La auditoría sigue siendo alcanzable tras un fallo de notificación

- **WHEN** el envío de la notificación al operador falla
- **THEN** la ejecución continúa y alcanza `Registro de auditoria`

#### Scenario: La rama de revisión conserva la notificación

- **WHEN** el backend marca un incidente con `requiere_revision_humana = true`
- **THEN** el flujo sigue notificando al operador designado (sin regresión)

### Requirement: N8N-DOC-001 — La guía del workflow refleja el estado real

`docs/n8n-workflow-guide.md` SHALL declarar un conteo de nodos y un conteo de pruebas estructurales que coincidan con `n8n/workflow.json` y con la suite `App/Backend/tests/test_n8n_workflow.py` respectivamente. La guía MUST NOT contener excepciones conocidas obsoletas, en particular la afirmación de que la rama de revisión humana no marca el correo como leído cuando el cableado actual sí lo hace.

#### Scenario: El conteo de nodos coincide con el JSON

- **WHEN** se compara el conteo de nodos declarado en la guía contra `n8n/workflow.json`
- **THEN** ambos conteos coinciden

#### Scenario: El conteo de pruebas coincide con la suite

- **WHEN** se compara el conteo de pruebas estructurales declarado en la guía contra la suite `test_n8n_workflow.py`
- **THEN** ambos conteos coinciden

#### Scenario: No queda la excepción obsoleta de la rama de revisión

- **WHEN** se inspecciona la sección de ciclo de vida del correo de la guía
- **THEN** la guía no afirma que la rama de revisión humana deja el correo sin marcar como leído
