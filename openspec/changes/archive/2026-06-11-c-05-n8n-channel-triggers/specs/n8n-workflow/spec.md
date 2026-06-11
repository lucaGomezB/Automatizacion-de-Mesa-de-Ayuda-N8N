## ADDED Requirements

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
