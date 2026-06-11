## Why

C-04 dejó el núcleo del workflow N8N funcional (normalización, validación Anexo H, ruteo por confianza, persistencia contra el backend), pero el flujo todavía no cumple la capa de canales de entrada ni el cierre del ciclo que describe la tesis (§5.2, §5.3, §6.3, §6.4). Hoy faltan: el **trigger del formulario web** (tercer canal de entrada exigido por §5.2, consumido por el frontend ya construido), los **nodos paralelos de notificación al usuario** post-registro y el **nodo de registro de auditoría** (log de ejecución conservado 30 días según §5.3). Sin estos elementos el sistema no confirma el alta al usuario por su canal ni deja la traza de auditoría requerida, y el canal web del frontend no tiene punto de entrada.

## What Changes

- **Trigger IMAP/Outlook de correo**: ratificar y dejar documentado el disparador de correo existente (`microsoftOutlookTrigger`, sondeo cada minuto) como el canal de correo del sistema, marcando su salida con `canal_raw = "correo"` de forma explícita para el normalizador.
- **Trigger Webhook para formulario web**: agregar un nodo `webhook` (POST, ruta dedicada) que reciba el JSON del formulario web del frontend, marque `canal_raw = "web"` y conecte al normalizador. Es el canal que hoy soporta el normalizador (C-04) pero no tiene disparador.
- **Trigger Webhook para transcripción de Twilio**: ratificar y documentar el disparador telefónico existente (`twilioTrigger`) como canal de telefonía, cableado al AI Agent → validación → normalizador.
- **Nodos paralelos de notificación al usuario** post-registro: tras un alta exitosa (HTTP 201 del backend), notificar al usuario por el canal correspondiente — respuesta de confirmación al webhook web (cuerpo con número de incidente) y correo de confirmación para el canal de correo. La telefonía confirma vía la respuesta del webhook/TwiML.
- **Nodo de registro de auditoría**: agregar un nodo que registre cada ejecución (id de incidente, canal de origen, timestamp, categoría, confianza, resultado) para conservación de 30 días según §5.3, sin transmitir PII en claro en el registro.
- **Cableado del flujo completo**: conectar los tres canales al normalizador único y, tras la persistencia, a la notificación y a la auditoría, de modo que el flujo cierre el ciclo descrito en §6.3.
- **Tests estructurales** (Strict TDD): extender `Gestion_Incidentes/tests/test_n8n_workflow.py` con casos que verifiquen, sobre el JSON exportado, la presencia y el cableado del webhook web, los nodos de notificación, el nodo de auditoría y la conservación de 30 días — sin requerir runtime N8N.
- **Documentación**: actualizar `docs/n8n-workflow-guide.md` con los tres triggers, las rutas de webhook, los nodos de notificación/auditoría y la verificación por canal.

## Capabilities

### New Capabilities
<!-- Ninguna capability nueva. C-05 extiende la capability n8n-workflow creada por C-04. -->

### Modified Capabilities
- `n8n-workflow`: se agregan requisitos para (1) el trigger del formulario web (canal `web`), (2) la identificación explícita del canal de origen en cada trigger, (3) los nodos paralelos de notificación al usuario post-registro, y (4) el nodo de registro de auditoría con retención de 30 días. Los requisitos existentes de C-04 (normalización, validación Anexo H, ruteo por confianza, persistencia, pseudonimización en tránsito, verificación estructural) se conservan sin cambios; C-05 los complementa con la capa de canales y el cierre del ciclo de §6.3.

## Impact

- **Archivo del workflow**: `Automatizacion_Mesa_de_Ayuda.json` — alta de 1 nodo `webhook` (canal web), 2–3 nodos de notificación (respuesta webhook + correo de confirmación), 1 nodo de auditoría/log, marcado explícito de `canal_raw` en los triggers y nuevo cableado triggers → normalizador → persistencia → notificación + auditoría. Sin cambios en los nodos de validación ni en el contrato HTTP definidos por C-04.
- **Tests**: extensión de `Gestion_Incidentes/tests/test_n8n_workflow.py` con casos estructurales nuevos. No altera la suite backend existente (112 passed / 1 skipped / 1 xfailed); solo agrega casos sobre el JSON.
- **Frontend (consumo, sin cambios en este change)**: el formulario web del frontend ya existe; el webhook que se agrega es su punto de entrada en N8N. La URL/ruta del webhook se documenta para que el frontend la consuma (la integración frontend↔webhook se confirma fuera de C-05).
- **Documentación**: actualización de `docs/n8n-workflow-guide.md`.
- **Dependencias externas**: N8N 1.62 (Docker autoalojado), backend FastAPI + PostgreSQL para verificación funcional; Twilio (TwiML/transcripción) y Microsoft Outlook para los canales telefónico y de correo; Redis para el AI Agent (ya presentes).
- **Pseudonimización**: el nodo de auditoría NO debe registrar PII en claro; se respeta la decisión de C-04 (pseudonimización en el backend) y no se reintroduce PII en el log del workflow.
- **Governance**: MEDIO — implementar con checkpoints; las decisiones no obvias (mecanismo de notificación por canal, formato y destino del log de auditoría, ruta del webhook web) se elevan en design.md.
