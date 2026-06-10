## Why

La utilidad `notify_n8n(incidente_id, result)` ya existe en `app/utils/n8n_webhook.py`, pero **nadie la llama**. Tras clasificar un incidente, el backend persiste el resultado pero nunca notifica a N8N, dejando incompleto el ciclo de orquestación descrito en §5.3 de la tesis: N8N debe recibir la clasificación para continuar el flujo (confirmar al usuario, actualizar MTM-SRU). Este es uno de los dos gaps funcionales del backend identificados en el roadmap (FASE 2, C-02).

## What Changes

- Invocar `notify_n8n(incidente_id, result)` desde `IncidenteService._apply_classification()` una vez aplicada la clasificación al incidente.
- La invocación es **fire-and-forget**: no bloquea ni demora la respuesta HTTP del endpoint que creó el incidente, y nunca propaga fallos de red de N8N al llamador. Cualquier falla de notificación se observa vía structlog (la utilidad ya lo hace internamente).
- Si `n8n_webhook_url` no está configurado, la notificación se omite silenciosamente (comportamiento ya soportado por la utilidad) — el sistema sigue operando en entornos sin N8N (desarrollo, tests).
- Agregar test unitario que verifique que `notify_n8n` se invoca con `incidente_id` y `result` correctos (mockeando la utilidad / httpx).
- Agregar test de integración del webhook contra un servidor HTTP mock, verificando el payload enviado y que un fallo del webhook no rompe la creación/clasificación del incidente.

## Capabilities

### New Capabilities
- `n8n-notification`: Notificación de retorno hacia N8N tras la clasificación de un incidente. Define el contrato de cuándo se notifica, qué payload se envía, y la garantía fire-and-forget (no bloqueante, no propaga fallos).

### Modified Capabilities
<!-- Ninguna. No cambian requisitos de capabilities existentes; `foundation-environment` permanece intacto. -->

## Impact

- **Código modificado**: `Gestion_Incidentes/app/services/incidente_service.py` — método `_apply_classification()` (agrega la llamada fire-and-forget a `notify_n8n`).
- **Código reutilizado (sin cambios de contrato)**: `Gestion_Incidentes/app/utils/n8n_webhook.py` (`notify_n8n`), `Gestion_Incidentes/app/config/settings.py` (`n8n_webhook_url`, `n8n_webhook_secret`).
- **Tests nuevos**: un test unitario y un test de integración del hook bajo `Gestion_Incidentes/tests/`.
- **APIs externas**: webhook HTTP de N8N (`POST` a `n8n_webhook_url`). No cambia el contrato REST público de la API (Tabla 5, §5.7); es una integración saliente aditiva.
- **Dependencias**: ninguna nueva; `httpx` ya es dependencia del proyecto.
- **Riesgo / Gobernanza**: BAJO — integración aditiva, sin impacto sobre datos persistidos ni sobre la respuesta al usuario; un fallo de N8N no degrada la operación principal.
