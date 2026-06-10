## ADDED Requirements

### Requirement: Notificación a N8N tras la clasificación
El sistema SHALL notificar a N8N el resultado de la clasificación de un incidente inmediatamente después de aplicar la clasificación al incidente dentro de `IncidenteService._apply_classification()`. La notificación SHALL realizarse invocando la utilidad `notify_n8n(incidente_id, result)` con el ID del incidente recién clasificado y el `ClasificacionResult` producido por el clasificador híbrido.

#### Scenario: Incidente clasificado dispara la notificación
- **WHEN** `IncidenteService.create_and_classify()` completa la clasificación de un incidente
- **THEN** se invoca `notify_n8n` exactamente una vez con `incidente_id` igual al ID del incidente persistido y `result` igual al `ClasificacionResult` aplicado

#### Scenario: Webhook no configurado
- **WHEN** `n8n_webhook_url` está vacío en la configuración
- **THEN** no se realiza ninguna llamada HTTP saliente y la creación/clasificación del incidente concluye normalmente

### Requirement: Notificación fire-and-forget no bloqueante
La notificación a N8N SHALL ser fire-and-forget: NO SHALL bloquear, demorar de forma observable, ni alterar la respuesta HTTP del endpoint que creó el incidente. El incidente persistido y clasificado SHALL retornarse al llamador independientemente del estado de la notificación a N8N.

#### Scenario: La respuesta no espera el resultado de N8N
- **WHEN** un incidente se crea y clasifica correctamente
- **THEN** `create_and_classify()` retorna el incidente completo sin que su valor de retorno dependa de la respuesta del webhook de N8N

### Requirement: Aislamiento de fallos de la notificación
Un fallo de la notificación a N8N (timeout, error de red, código HTTP de error, o cualquier excepción) NO SHALL propagarse al llamador ni impedir la creación, clasificación y persistencia del incidente. El fallo SHALL registrarse mediante logging estructurado (structlog) como advertencia, preservando la observabilidad sin degradar la operación principal.

#### Scenario: El webhook de N8N falla
- **WHEN** la llamada a `notify_n8n` falla (excepción de red, timeout o respuesta HTTP de error)
- **THEN** `create_and_classify()` igualmente retorna el incidente creado y clasificado sin propagar la excepción, y se emite un log de advertencia que registra el fallo

#### Scenario: El incidente persiste pese al fallo de N8N
- **WHEN** la notificación a N8N falla después de que el incidente fue clasificado
- **THEN** el incidente y su `clasificacion_log` permanecen persistidos en la base de datos sin alteración

### Requirement: Payload de notificación
El payload enviado a N8N SHALL incluir los campos mínimos para que N8N continúe el flujo de orquestación: `incidente_id`, `categoria`, `confianza`, `etapa` y `requiere_revision_humana`, derivados del `incidente_id` y del `ClasificacionResult`.

#### Scenario: Contenido del payload enviado al webhook
- **WHEN** `n8n_webhook_url` está configurado y se notifica una clasificación
- **THEN** el cuerpo JSON de la solicitud `POST` contiene `incidente_id`, `categoria`, `confianza`, `etapa` y `requiere_revision_humana` con los valores del incidente clasificado
