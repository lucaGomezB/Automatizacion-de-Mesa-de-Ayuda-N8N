## ADDED Requirements

### Requirement: Contrato runtime del nodo HTTP de persistencia

El nodo `httpRequest` que apunta a `POST /api/v1/incidentes` SHALL declarar autenticación configurada hacia el backend, y su cuerpo SHALL incluir `canal_origen_id` además de `descripcion` y `prioridad`, conforme al contrato `IncidenteCreate` que el backend resuelve por clave foránea. Las pruebas estructurales del workflow exportado SHALL verificar ambos extremos sin requerir una instancia N8N en ejecución.

#### Scenario: El nodo HTTP declara autenticación

- **WHEN** la suite de pruebas inspecciona el nodo `httpRequest` que apunta a `/api/v1/incidentes`
- **THEN** el nodo tiene un campo de autenticación configurado con un tipo distinto de vacío/`none`
- **AND** la configuración no queda reducida al default sin credencial

#### Scenario: El cuerpo del HTTP incluye canal_origen_id

- **WHEN** la suite de pruebas inspecciona el cuerpo (`body`) del nodo `httpRequest` de persistencia
- **THEN** el cuerpo contiene una entrada para `canal_origen_id`
- **AND** esa entrada es una expresión que resuelve a un valor del flujo, no una constante ajena al incidente

### Requirement: Switch en modo expresión devuelve índice numérico sobre campos existentes

Cada nodo `switch` en modo `expression` del workflow SHALL devolver un índice numérico de salida (posición 0-based de la rama) y NO el valor de un campo. Las expresiones del Switch SHALL referenciar únicamente campos que existen en la respuesta real del backend o en un nodo aguas arriba accesible por su nombre; NO SHALL referenciar campos que no existan en la respuesta del backend ni provengan de un nodo accesible.

#### Scenario: La salida del Switch es un índice numérico

- **WHEN** la suite de pruebas inspecciona un nodo `switch` con `mode: expression`
- **THEN** el campo de salida es una expresión que resuelve a un índice numérico dentro del rango de ramas definidas
- **AND** la salida NO es la expresión de un campo de datos (por ejemplo `$json.<campo>`)

#### Scenario: Los campos referenciados existen en la respuesta del backend

- **WHEN** la suite de pruebas extrae los campos referenciados por las condiciones y por la salida del Switch
- **THEN** cada campo referenciado existe en el schema de respuesta de `POST /api/v1/incidentes` o proviene de un nodo aguas arriba accesible por nombre
- **AND** no hay referencias a campos inexistentes en ambos orígenes

### Requirement: Acoplamiento del AI Agent a su modelo de lenguaje y al payload del trigger

Cada nodo `@n8n/n8n-nodes-langchain.agent` SHALL tener una conexión entrante de tipo `ai_languageModel` desde un nodo de modelo de lenguaje. El prompt del agente SHALL interpolar el payload recibido del trigger (por ejemplo `$json` o `$input`), de modo que el contenido de la llamada o del correo sea la entrada efectiva del agente.

#### Scenario: El agente tiene conexión ai_languageModel

- **WHEN** la suite de pruebas inspecciona las conexiones del workflow
- **THEN** cada nodo agente tiene al menos una conexión de tipo `ai_languageModel`
- **AND** el nodo origen de esa conexión es un nodo de modelo de lenguaje

#### Scenario: El prompt interpola el payload del trigger

- **WHEN** la suite de pruebas inspecciona el texto (`text` o `prompt`) del nodo agente
- **THEN** el texto contiene una expresión que referencia el payload de entrada del trigger (`$json` o `$input`)
- **AND** el prompt no es un texto estático sin datos del incidente

### Requirement: Trigger de Outlook entrega la descripción al validador

El nodo `microsoftOutlookTrigger` SHALL estar configurado de modo que su salida exponga el cuerpo del correo que el validador del canal de correo necesita leer. El validador lee la descripción desde `item.json.body`, `item.json.descripcion` o `item.json.text`; la configuración del trigger SHALL garantizar que al menos una de esas rutas esté disponible en la salida.

#### Scenario: La salida del trigger expone la descripción

- **WHEN** la suite de pruebas inspecciona la configuración del `microsoftOutlookTrigger`
- **THEN** la configuración incluye las opciones/filtros necesarios para que el cuerpo del correo esté disponible en la salida
- **AND** el nodo validador de correo puede resolver la descripción sin depender de un campo ausente

### Requirement: Cierre del ciclo del webhook con responseNode

Todo nodo `webhook` configurado con `responseMode: responseNode` SHALL tener un nodo `respondToWebhook` alcanzable desde la rama exitosa de su flujo. La suite de pruebas SHALL verificar la alcanzabilidad estructural desde el webhook hasta el `respondToWebhook` sin requerir runtime N8N.

#### Scenario: El respondToWebhook es alcanzable

- **WHEN** la suite de pruebas traza el cableado desde un `webhook` con `responseMode: responseNode`
- **THEN** existe al menos un camino de conexiones que llega a un nodo `respondToWebhook`
- **AND** el `respondToWebhook` no queda huérfano respecto de ese webhook

### Requirement: Credenciales declaradas en nodos que las requieren

Todo nodo del workflow que requiera credenciales para operar (por ejemplo los nodos de Outlook, el trigger de Twilio y el modelo de lenguaje del agente) SHALL declarar la credencial correspondiente en su configuración, de modo que el workflow exportado no dependa de credenciales implícitas o ausentes.

#### Scenario: Los nodos que requieren credenciales las declaran

- **WHEN** la suite de pruebas inspecciona los nodos que requieren credenciales por su tipo
- **THEN** cada uno declara una entrada de credencial no vacía en su configuración
- **AND** ningún nodo que requiera credencial queda sin declararla
