# n8n-workflow Specification

## Purpose
Specifies the end-to-end N8N workflow for automated help desk incident classification, covering all three input channels (Outlook email, web form webhook, Twilio call transcription), validation, categorization via Gemini AI, notification by channel, audit logging, and persistence via a FastAPI backend. Combines the foundation from C-04 (normalization, validation, routing) with channel-layer infrastructure from C-05 (explicit channel identification, per-channel triggers, post-registration notifications, audit trails).

## Requirements

### Requirement: Normalización de canales a estructura unificada

El workflow N8N SHALL incluir un nodo de normalización que homogenice la entrada de cualquiera de los tres canales (correo electrónico, formulario web, telefonía con transcripción) en una estructura unificada con exactamente los campos `id` (identificador único), `timestamp` (marca temporal con precisión al milisegundo), `canal_origen` (uno de `correo`, `web`, `telefonia`) y `descripcion` (texto del incidente). Los nodos posteriores SHALL operar exclusivamente sobre esta estructura unificada y no sobre la forma cruda de cada canal.

#### Scenario: Correo electrónico normalizado

- **WHEN** el disparador de Outlook recibe un correo y su carga pasa por el nodo de normalización
- **THEN** la salida contiene `id`, `timestamp` con precisión al milisegundo, `canal_origen = "correo"` y `descripcion` con el cuerpo del incidente

#### Scenario: Transcripción telefónica normalizada

- **WHEN** el AI Agent parsea la transcripción de una llamada Twilio y su salida pasa por el nodo de normalización
- **THEN** la salida contiene los mismos cuatro campos con `canal_origen = "telefonia"`

#### Scenario: Canal de origen inválido rechazado

- **WHEN** la normalización recibe una entrada cuyo canal no es `correo`, `web` ni `telefonia`
- **THEN** el flujo no produce una estructura unificada válida y deriva la entrada a revisión humana

### Requirement: Validación de entrada del canal de correo según Anexo H

El nodo `code` del canal de correo SHALL reemplazar la lógica placeholder por una validación de los campos requeridos para levantar un incidente. SHALL verificar que la descripción exista, no esté en blanco y tenga al menos 10 caracteres. Si la validación falla, el flujo SHALL rutear hacia el nodo que solicita al usuario reenviar los datos faltantes y NO SHALL intentar crear el incidente.

#### Scenario: Correo con datos completos pasa la validación

- **WHEN** el nodo de validación recibe un correo con una descripción de 10 o más caracteres
- **THEN** marca la entrada como válida y el flujo continúa hacia la normalización y clasificación

#### Scenario: Correo con datos faltantes pide reenvío

- **WHEN** el nodo de validación recibe un correo sin descripción o con menos de 10 caracteres
- **THEN** marca la entrada como inválida y el nodo `if` rutea hacia el envío de un mensaje al usuario solicitando los datos faltantes

### Requirement: Validación de la respuesta de clasificación según Anexo H §H.3

El nodo `code` del canal telefónico SHALL validar la respuesta de clasificación aplicando, en orden, los pasos del Anexo H §H.3: (1) parseo JSON válido; (2) presencia de los campos `sector_predicho` y `confianza`; (3) `sector_predicho` exactamente en `{"Seguridad Informatica", "Soporte Tecnico Hardware", "Soporte Tecnico Software", "Bases de Datos", "Sistemas"}` (case-sensitive, sin tildes); (4) `confianza` numérica en el rango `[0.0, 1.0]`; (5) si el campo `sectores_adicionales` está presente, cada uno de sus valores MUST pertenecer al mismo conjunto canónico. Ante el fallo de cualquier paso, SHALL registrar el error, fijar `confianza = 0.0` y marcar el incidente para revisión humana, sin propagar estados inconsistentes.

#### Scenario: Respuesta válida aceptada

- **WHEN** la validación recibe `{"sector_predicho": "Soporte Tecnico Software", "confianza": 0.95, "sectores_adicionales": ["Bases de Datos"]}`
- **THEN** la marca como válida y conserva el sector predicho, los sectores adicionales y la confianza para el ruteo por umbral

#### Scenario: Categoría fuera del conjunto permitido

- **WHEN** la validación recibe una respuesta con `sector_predicho` igual a `"operaciones"` (minúscula), `"Operaciones"` o cualquier valor fuera del conjunto exacto
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: Sector adicional inválido

- **WHEN** la validación recibe un `sectores_adicionales` con un valor fuera del conjunto canónico
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: JSON malformado

- **WHEN** la validación recibe un texto que no parsea como JSON
- **THEN** registra el error, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: Confianza fuera de rango

- **WHEN** la validación recibe una `confianza` igual a `1.5` o no numérica
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

### Requirement: Ruteo por umbral de confianza

Los nodos `if` del workflow SHALL evaluar la condición `confianza >= 0.70`. Cuando la condición es verdadera, el flujo SHALL rutear hacia la creación directa del incidente. Cuando es falsa (o la validación previa fijó `confianza = 0.0`), el flujo SHALL marcar el incidente para revisión humana. Las condiciones de los nodos `if` NO SHALL quedar vacías.

#### Scenario: Confianza por encima del umbral crea el incidente

- **WHEN** un nodo `if` evalúa una entrada con `confianza = 0.85`
- **THEN** la condición `confianza >= 0.70` es verdadera y el flujo rutea hacia la persistencia del incidente

#### Scenario: Confianza por debajo del umbral deriva a revisión humana

- **WHEN** un nodo `if` evalúa una entrada con `confianza = 0.60`
- **THEN** la condición es falsa y el flujo marca el incidente para revisión humana

#### Scenario: Confianza en el límite exacto

- **WHEN** un nodo `if` evalúa una entrada con `confianza = 0.70`
- **THEN** la condición `confianza >= 0.70` es verdadera y el flujo rutea hacia la persistencia (el umbral es inclusivo)

### Requirement: Persistencia del incidente vía backend FastAPI

El nodo HTTP de persistencia SHALL invocar `POST /api/v1/incidentes` del backend FastAPI con un cuerpo JSON conforme al schema `IncidenteCreate` (`descripcion`, `prioridad`, `canal`). El workflow SHALL consumir la respuesta del backend (que incluye `sector`, `confianza` y el indicador de revisión humana producidos por `create_and_classify`) como resultado de la clasificación, sin invocar un endpoint de clasificación independiente.

#### Scenario: Creación exitosa devuelve 201

- **WHEN** el nodo HTTP envía un `IncidenteCreate` válido a `POST /api/v1/incidentes`
- **THEN** el backend responde `201 Created` con la representación del incidente clasificado y el flujo lo registra como creado

#### Scenario: El payload respeta el contrato del backend

- **WHEN** se inspecciona el cuerpo que el nodo HTTP envía
- **THEN** contiene el campo `descripcion` (string pseudonimizado de 10 a 5000 caracteres) y la prioridad, sin campos ajenos al schema `IncidenteCreate`

### Requirement: Descripción pseudonimizada en tránsito

El workflow SHALL garantizar que la `descripcion` enviada al backend ya esté pseudonimizada conforme al módulo de pseudonimización (C-03), de modo que no se transmita información personal identificable en claro hacia el subsistema de clasificación. El flujo NO SHALL enviar PII en claro en el campo `descripcion`.

#### Scenario: Descripción pseudonimizada antes de persistir

- **WHEN** una descripción contiene datos personales (nombre, email, teléfono) y atraviesa el flujo hasta el nodo HTTP de persistencia
- **THEN** el valor del campo `descripcion` enviado al backend no contiene la PII en claro, sino su forma pseudonimizada

### Requirement: Workflow exportado verificable por estructura

El JSON exportado del workflow (`Automatizacion_Mesa_de_Ayuda.json`) SHALL ser verificable mediante un conjunto de pruebas automatizadas que validen su estructura sin requerir una instancia N8N en ejecución. Las pruebas SHALL comprobar: la presencia de los nodos esperados, que las condiciones de los nodos `if` no estén vacías, que los nodos `code` no contengan la lógica placeholder `myNewField = 1`, y que el nodo HTTP de persistencia apunte a la ruta `/api/v1/incidentes`.

#### Scenario: Ausencia de placeholders

- **WHEN** la suite de pruebas inspecciona el código de los nodos `code` del workflow exportado
- **THEN** ningún nodo `code` contiene la cadena `myNewField = 1`

#### Scenario: Condiciones IF configuradas

- **WHEN** la suite de pruebas inspecciona los nodos `if` del workflow exportado
- **THEN** cada nodo `if` tiene al menos una condición no vacía que referencia la confianza y el umbral 0.70

#### Scenario: Nodo HTTP de persistencia apunta al endpoint correcto

- **WHEN** la suite de pruebas inspecciona los nodos `httpRequest` del workflow exportado
- **THEN** existe un nodo cuyo destino es la ruta `/api/v1/incidentes`

### Requirement: Trigger del canal de correo identificado

El workflow N8N SHALL incluir un disparador de correo electrónico (nodo `microsoftOutlookTrigger`, monitoreo de la casilla institucional de mesa de ayuda) como vía de entrada del canal de correo, conforme a la tesis §5.2. La salida del disparador de correo SHALL quedar marcada con `canal_raw = "correo"` de forma explícita antes de llegar al nodo de normalización, de modo que el normalizador asigne `canal_origen = "correo"` sin ambigüedad.

#### Scenario: El disparador de correo existe y alimenta el flujo

- **WHEN** se inspecciona el workflow exportado
- **THEN** existe un nodo `microsoftOutlookTrigger` cuya salida fluye, a través del nodo de validación de correo, hacia el nodo de normalización

#### Scenario: El canal de correo queda identificado como "correo"

- **WHEN** una entrada del disparador de correo atraviesa el flujo hasta la normalización
- **THEN** el `canal_raw` propagado es `"correo"` y la estructura unificada resultante tiene `canal_origen = "correo"`

### Requirement: Trigger Webhook para el formulario web

El workflow N8N SHALL incluir un nodo disparador `webhook` (método `POST`, con una ruta dedicada) que reciba el envío del formulario web del frontend como tercer canal de entrada (tesis §5.2). La salida del webhook web SHALL quedar marcada con `canal_raw = "web"` y SHALL conectarse al nodo de normalización, de modo que el normalizador asigne `canal_origen = "web"`. La ruta del webhook SHALL ser estable y documentada para que el frontend la consuma.

#### Scenario: El webhook del formulario web existe

- **WHEN** se inspecciona el workflow exportado
- **THEN** existe un nodo de tipo `webhook` con método `POST` y una ruta (`path`) no vacía destinado al formulario web

#### Scenario: El webhook web alimenta la normalización con canal "web"

- **WHEN** el webhook web recibe un envío del formulario y su salida atraviesa el flujo
- **THEN** el `canal_raw` propagado es `"web"`, la salida está cableada al nodo de normalización y la estructura unificada resultante tiene `canal_origen = "web"`

### Requirement: Trigger Webhook para la transcripción de Twilio

El workflow N8N SHALL incluir un disparador `twilioTrigger` (webhook posterior al cuelgue) que reciba la transcripción de la llamada telefónica como canal de telefonía (tesis §5.2 y §6.4). La salida del disparador telefónico SHALL fluir hacia el AI Agent y, tras la validación de la respuesta de clasificación, hacia el nodo de normalización con `canal_raw = "telefonia"`, de modo que el normalizador asigne `canal_origen = "telefonia"`.

#### Scenario: El disparador telefónico existe y alimenta el flujo

- **WHEN** se inspecciona el workflow exportado
- **THEN** existe un nodo `twilioTrigger` cuya salida fluye hacia el AI Agent y, tras la validación, hacia el nodo de normalización

#### Scenario: El canal telefónico queda identificado como "telefonia"

- **WHEN** una transcripción telefónica atraviesa el flujo hasta la normalización
- **THEN** el `canal_raw` propagado es `"telefonia"` y la estructura unificada resultante tiene `canal_origen = "telefonia"`

### Requirement: Los tres canales convergen en el normalizador único

El workflow N8N SHALL cablear los tres disparadores (correo, web, telefonía) de modo que todas las entradas converjan en el único nodo de normalización definido por C-04, antes de la persistencia. Ningún canal SHALL crear incidentes salteándose la normalización ni el ruteo por umbral de confianza.

#### Scenario: Convergencia de canales en la normalización

- **WHEN** se traza el cableado del workflow desde cada uno de los tres disparadores
- **THEN** cada ruta alcanza el nodo de normalización antes de llegar al nodo `httpRequest` de persistencia

### Requirement: Notificación al usuario post-registro por canal

Tras un alta exitosa del incidente (respuesta `201 Created` del backend), el workflow N8N SHALL notificar al usuario por el canal correspondiente, mediante nodos de notificación posteriores al nodo `httpRequest` de persistencia: una respuesta de confirmación al webhook web (con el número de incidente) para el canal `web` y un correo de confirmación para el canal `correo`. La confirmación del canal de telefonía SHALL resolverse mediante la respuesta del webhook/TwiML. La notificación SHALL ocurrir solo cuando la creación del incidente fue exitosa y NO SHALL bloquear el registro de auditoría.

#### Scenario: Confirmación web tras alta exitosa

- **WHEN** un incidente del canal `web` se crea con `201 Created`
- **THEN** el workflow responde al webhook web con una confirmación que incluye el identificador del incidente

#### Scenario: Confirmación por correo tras alta exitosa

- **WHEN** un incidente del canal `correo` se crea con `201 Created`
- **THEN** el workflow envía un correo de confirmación al usuario del canal de correo

#### Scenario: Sin notificación cuando no hubo alta

- **WHEN** la creación del incidente no resulta en `201 Created` (validación fallida o ruteo a revisión humana)
- **THEN** el workflow no emite la notificación de confirmación de alta al usuario

### Requirement: Registro de auditoría con retención de 30 días

El workflow N8N SHALL incluir un nodo de registro de auditoría que, por cada ejecución, registre al menos el identificador del incidente, el `canal_origen`, el `timestamp`, el sector predicho, sus sectores adicionales, la confianza y el resultado (creado / derivado a revisión / rechazado), conforme a la conservación de 30 días que establece la tesis §5.3. El registro de auditoría NO SHALL contener la descripción con PII en claro; SHALL limitarse a metadatos de la ejecución y referencias al incidente. La política de retención de 30 días SHALL quedar declarada de forma verificable en el workflow o su documentación.

#### Scenario: La ejecución queda registrada en auditoría

- **WHEN** una ejecución del workflow completa el procesamiento de un incidente
- **THEN** el nodo de auditoría registra `id`, `canal_origen`, `timestamp`, sector predicho, sectores adicionales, confianza y resultado de esa ejecución

#### Scenario: El registro de auditoría no contiene PII en claro

- **WHEN** se inspecciona el contenido que el nodo de auditoría registra
- **THEN** el registro no incluye la descripción cruda con datos personales en claro, solo metadatos y referencias

#### Scenario: Retención de 30 días declarada

- **WHEN** se inspecciona el nodo de auditoría o la guía del workflow
- **THEN** la conservación de los registros de ejecución por 30 días queda declarada explícitamente

### Requirement: Estructura de canales y cierre de ciclo verificable por pruebas

El JSON exportado del workflow (`Automatizacion_Mesa_de_Ayuda.json`) SHALL ser verificable mediante la suite de pruebas estructurales existente (sin runtime N8N) respecto de la capa de canales y el cierre del ciclo. Las pruebas SHALL comprobar: la presencia del disparador `webhook` del formulario web con método `POST` y ruta no vacía, la presencia de los tres disparadores con su `canal_raw` correspondiente, la presencia de los nodos de notificación posteriores a la persistencia, la presencia del nodo de auditoría con sus campos de metadatos, y la declaración de la retención de 30 días.

#### Scenario: Presencia del webhook del formulario web

- **WHEN** la suite de pruebas inspecciona los disparadores del workflow exportado
- **THEN** existe un nodo `webhook` con método `POST` y una ruta no vacía para el formulario web

#### Scenario: Presencia de los nodos de notificación

- **WHEN** la suite de pruebas inspecciona el workflow exportado
- **THEN** existen nodos de notificación cableados después del nodo `httpRequest` de persistencia

#### Scenario: Presencia del nodo de auditoría

- **WHEN** la suite de pruebas inspecciona el workflow exportado
- **THEN** existe un nodo de auditoría/log con los campos de metadatos esperados y la retención de 30 días declarada

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

### Requirement: N8N-AUTH-001 — Nodos HTTP autentican al backend con un JWT obtenido por login dinamico

El workflow SHALL obtener el JWT con un nodo de login que invoque `POST /api/v1/auth/login` con las credenciales del operador almacenadas como credencial de N8N (MUST NOT incluir el token ni las credenciales en `n8n/workflow.json`). El nodo que crea el incidente SHALL enviar `Authorization: Bearer <token>` con el token extraido de la respuesta del login. El token MUST NOT ser un valor estatico de larga vida, porque el JWT del backend expira (`JWT_EXPIRE_MINUTES=1440`). La ausencia de un token valido MUST NOT producir una ejecucion exitosa silenciosa; el nodo SHALL propagar el error HTTP.

#### Scenario: El alta de incidente llega autenticada al backend

- **WHEN** se ejecuta el flujo completo que invoca `POST /api/v1/incidentes`
- **THEN** el workflow obtiene el token via `POST /api/v1/auth/login` y la solicitud incluye `Authorization: Bearer <token>` y el backend responde 201, no 401

#### Scenario: El token se renueva en cada ejecucion

- **WHEN** transcurre mas de la vida util del JWT entre dos ejecuciones del workflow
- **THEN** el workflow vuelve a ejecutar el login y obtiene un token vigente en lugar de reutilizar uno expirado

#### Scenario: Sin credencial valida el nodo falla visiblemente

- **WHEN** las credenciales de login son invalidas o el token esta ausente
- **THEN** el nodo registra el error HTTP 401 y el workflow no continua como si hubiera creado el incidente

### Requirement: N8N-AGENT-001 — AI Agent con Chat Model conectado

El nodo `AI Agent` SHALL tener un Chat Model conectado y configurado, de modo que la ejecucion del agente produzca una salida real. Un nodo agente sin modelo MUST NOT considerarse configurado.

#### Scenario: El agente produce salida con el modelo conectado

- **WHEN** el workflow llega al nodo `AI Agent`
- **THEN** el agente ejecuta contra el Chat Model conectado y devuelve una respuesta no vacia

### Requirement: N8N-AGENT-002 — Prompt dinamico con el payload del trigger

El prompt del `AI Agent` SHALL interpolar la descripcion del incidente proveniente del payload del trigger, en lugar de ser un texto estatico. La descripcion SHALL llegar pseudonimizada al agente cuando corresponda.

#### Scenario: El prompt contiene la descripcion del trigger

- **WHEN** el trigger recibe una entrada con descripcion `"Servidor de correo caido"`
- **THEN** la ejecucion del agente incluye esa descripcion en el prompt, no un texto fijo

### Requirement: N8N-AGENT-003 — Contrato JSON del agente compatible con el validador

La salida del `AI Agent` SHALL solicitarse y validarse como un JSON con exactamente los campos `sector_predicho` (uno de los cinco sectores canonicos, sin tildes) y `confianza` (numero entre 0 y 1). El validador SHALL aceptar el contrato del agente y MUST NOT fallar por un formato incompatible.

#### Scenario: Salida del agente validada correctamente

- **WHEN** el agente responde con `{"sector_predicho": "Sistemas", "confianza": 0.82}`
- **THEN** el validador acepta la respuesta y el flujo continua con ese sector y confianza

#### Scenario: Salida con sector fuera del vocabulario es rechazada

- **WHEN** el agente responde con un sector que no pertenece al conjunto canonico de cinco sectores
- **THEN** el validador rechaza la respuesta y el flujo deriva a revision humana

### Requirement: N8N-ROUTE-001 — Switch de canal en modo reglas sobre el canal normalizado

El nodo `Rutear por canal de origen` SHALL operar en modo de reglas (no en modo expresion) con reglas explicitas y `fallbackOutput` definido. Las reglas SHALL evaluar el canal normalizado (`correo`, `web`, `telefonia`) y la salida SHALL ser un indice de salida valido, no el resultado de evaluar la respuesta del backend.

#### Scenario: Cada canal rutea a su rama

- **WHEN** el canal normalizado es `correo`, `web` o `telefonia`
- **THEN** el switch produce el indice de salida correspondiente a esa rama

#### Scenario: Canal desconocido usa el fallback

- **WHEN** el canal no coincide con ninguna regla
- **THEN** el switch usa el `fallbackOutput` configurado en lugar de fallar o continuar sin salida

### Requirement: N8N-WEBHOOK-001 — responseMode con respondToWebhook alcanzable

El webhook de entrada SHALL configurar su `responseMode` de modo que el nodo `respondToWebhook` sea alcanzable en todas las ramas que deben responder al cliente. MUST NOT existir un `respondToWebhook` inalcanzable ni un webhook que quede sin respuesta.

#### Scenario: El webhook responde al cliente

- **WHEN** llega una peticion al webhook con un canal valido
- **THEN** el cliente recibe la respuesta emitida por el nodo `respondToWebhook` con un cuerpo y codigo definidos

#### Scenario: Ninguna rama queda sin respuesta

- **WHEN** se recorren las ramas del flujo que atienden el webhook
- **THEN** toda rama que deba responder alcanza `respondToWebhook` y ninguna queda en espera indefinida

### Requirement: N8N-WEBHOOK-002 — El alta del formulario web pasa por el webhook N8N

El formulario web SHALL crear incidentes a traves del webhook de N8N (con middleware si hiciera falta) y MUST NOT llamar directamente a `POST /api/v1/incidentes` para el alta. El webhook de N8N MUST NOT eliminarse como parte de este change.

#### Scenario: El formulario usa el webhook y no la API directa

- **WHEN** un usuario envia el formulario web de alta de incidente
- **THEN** la peticion llega al webhook de N8N y no directamente al endpoint de incidentes del backend

#### Scenario: El webhook permanece como punto de entrada del canal web

- **WHEN** se inspecciona el workflow y el cliente del formulario
- **THEN** el webhook de N8N sigue existiendo y es el punto de entrada del alta web

### Requirement: N8N-EMAIL-001 — Extraccion del cuerpo del correo en modo simple

El trigger de Outlook SHALL exponer el cuerpo del correo en el formato configurado. Cuando el modo de salida sea `simple`, el workflow SHALL extraer la descripcion desde la ubicacion de texto disponible, de modo que el validador de correo reciba una descripcion no vacia.

#### Scenario: Correo valido produce descripcion

- **WHEN** llega un correo con cuerpo de texto
- **THEN** la validacion de correo extrae la descripcion del campo disponible y la marca como valida si cumple el minimo

#### Scenario: El cuerpo no se pierde por el modo de salida

- **WHEN** el trigger opera en modo `simple` y el campo `body` no esta disponible en la raiz
- **THEN** el flujo obtiene el texto desde la ruta efectiva del payload del trigger

### Requirement: N8N-NORM-001 — El payload al backend incluye canal_origen_id

La estructura normalizada enviada al backend SHALL incluir `canal_origen_id` correspondiente al canal de origen, ademas de `id`, `timestamp`, `canal_origen` y `descripcion`. El incidente persistido MUST NOT quedar con canal `NULL`.

#### Scenario: El incidente creado tiene canal

- **WHEN** el workflow crea un incidente desde cualquiera de los tres canales
- **THEN** el body enviado al backend incluye `canal_origen_id` y el incidente persistido tiene canal de origen distinto de `NULL`

### Requirement: N8N-PHONE-001 — La rama falsa del telefono regresa al agente

En el canal telefonico, la rama que no cumple la condicion del nodo de decision SHALL regresar al agente o a un camino que complete el flujo. MUST NOT quedar como rama terminal sin salida.

#### Scenario: Condicion falsa del telefono no termina el flujo

- **WHEN** una transcripcion telefonica no cumple la condicion evaluada
- **THEN** el flujo reingresa al agente o a un camino que produce un resultado, sin terminar en un nodo sin continuacion

### Requirement: N8N-AUDIT-001 — La auditoria reporta rechazos como rechazos

El registro de auditoria SHALL distinguir creados de rechazados segun el resultado real del flujo. Un incidente rechazado por validacion o por el validador IA MUST NOT registrarse como creado.

#### Scenario: Un rechazo no se audita como alta

- **WHEN** una entrada es rechazada por validacion
- **THEN** el registro de auditoria refleja el rechazo y no un alta exitosa

### Requirement: N8N-VALID-001 — Los fallos del validador IA conservan su causa

Cuando el validador IA rechaza una salida, el flujo SHALL conservar la causa del rechazo y MUST NOT reetiquetar el incidente con un canal distinto (por ejemplo `correo`) por el mero hecho de haber fallado la validacion.

#### Scenario: Un fallo de validacion IA no cambia el canal

- **WHEN** el validador IA rechaza la salida del agente para una entrada del canal web
- **THEN** el canal registrado sigue siendo `web` y no se reetiqueta como `correo`

### Requirement: N8N-EXPR-001 — Expresiones de nodo validas y sin bucles vacios

Las expresiones de los nodos SHALL referenciar campos existentes del payload (MUST NOT usar `.id` ni otros campos inexistentes). MUST NOT existir un nodo de reenvio vacio conectado en bucle.

#### Scenario: Las expresiones referencian campos existentes

- **WHEN** se inspeccionan las expresiones de los nodos
- **THEN** cada campo referenciado existe en el payload de entrada y ninguna expresion referencia un `.id` inexistente

#### Scenario: No hay nodo vacio en bucle

- **WHEN** se inspecciona el grafo del workflow
- **THEN** no existe un nodo de reenvio vacio conectado en bucle consigo mismo

### Requirement: N8N-URL-001 — URLs del backend con la forma correcta

Las URLs del backend usadas por los nodos HTTP SHALL incluir la barra final y el prefijo de version correctos (`/api/v1/`), de modo que no se disparen redirecciones 307 ni 404 por barra faltante. La referencia a la URL base SHALL ser compatible con N8N v2 (sin depender de `$env` bloqueado).

#### Scenario: La llamada al backend no redirige

- **WHEN** un nodo HTTP invoca un endpoint del backend
- **THEN** la URL termina en el prefijo `/api/v1/` correcto y la respuesta no es un 307 por redireccion

#### Scenario: La URL base se resuelve en N8N v2

- **WHEN** el workflow se ejecuta en N8N v2
- **THEN** la URL base del backend se resuelve sin depender de una variable de entorno bloqueada
