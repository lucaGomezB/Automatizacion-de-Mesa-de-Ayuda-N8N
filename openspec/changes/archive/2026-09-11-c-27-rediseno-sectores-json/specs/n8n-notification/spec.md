## MODIFIED Requirements

### Requirement: Payload de notificación
El payload enviado a N8N SHALL incluir los campos mínimos para que N8N continúe el flujo de orquestación: `incidente_id`, `sector_predicho`, `sectores_adicionales`, `confianza`, `etapa` y `requiere_revision_humana`, derivados del `incidente_id` y del `ClasificacionResult`. El campo `categoria` MUST dejar de existir en el payload. `sectores_adicionales` SHALL ser una lista, posiblemente vacía.

#### Scenario: Contenido del payload enviado al webhook
- **WHEN** `n8n_webhook_url` está configurado y se notifica una clasificación
- **THEN** el cuerpo JSON de la solicitud `POST` contiene `incidente_id`, `sector_predicho`, `sectores_adicionales`, `confianza`, `etapa` y `requiere_revision_humana` con los valores del incidente clasificado
- **AND** no contiene el campo `categoria`
