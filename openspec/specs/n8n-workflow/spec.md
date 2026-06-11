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

El nodo `code` del canal telefónico SHALL validar la respuesta de clasificación aplicando, en orden, los cinco pasos del Anexo H §H.3: (1) parseo JSON válido; (2) presencia de los campos `categoría` y `confianza`; (3) `categoría` exactamente en `{"Sistemas", "Operaciones", "Soporte Técnico"}` (case-sensitive); (4) `confianza` numérica en el rango `[0.0, 1.0]`. Ante el fallo de cualquier paso, SHALL registrar el error, fijar `confianza = 0.0` y marcar el incidente para revisión humana, sin propagar estados inconsistentes.

#### Scenario: Respuesta válida aceptada

- **WHEN** la validación recibe `{"categoría": "Sistemas", "confianza": 0.95}`
- **THEN** la marca como válida y conserva la categoría y la confianza para el ruteo por umbral

#### Scenario: Categoría fuera del conjunto permitido

- **WHEN** la validación recibe una respuesta con `categoría` igual a `"sistemas"` (minúscula) o cualquier valor fuera del conjunto exacto
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

El workflow N8N SHALL incluir un nodo de registro de auditoría que, por cada ejecución, registre al menos el identificador del incidente, el `canal_origen`, el `timestamp`, la categoría, la confianza y el resultado (creado / derivado a revisión / rechazado), conforme a la conservación de 30 días que establece la tesis §5.3. El registro de auditoría NO SHALL contener la descripción con PII en claro; SHALL limitarse a metadatos de la ejecución y referencias al incidente. La política de retención de 30 días SHALL quedar declarada de forma verificable en el workflow o su documentación.

#### Scenario: La ejecución queda registrada en auditoría

- **WHEN** una ejecución del workflow completa el procesamiento de un incidente
- **THEN** el nodo de auditoría registra `id`, `canal_origen`, `timestamp`, categoría, confianza y resultado de esa ejecución

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

