## Why

El proyecto esta a punto de conectar credenciales reales (Outlook personal, Gemini, Twilio), y hoy existen caminos verificados en los que un error de usuario o un fallo de red hace que el sistema gaste creditos pagos sin control: el workflow N8N reintenta indefinidamente la clasificacion paga del canal telefonico, el backend puede volver a llamar a Gemini sobre un incidente que N8N ya clasifico, y un correo no leido o un webhook reenviado se reprocesa cada minuto. Auditar el costo antes de conectar las credenciales es mas barato que descubrirlo con la factura.

## What Changes

**Alto — bucles y reproceso de trabajo pago**

- HIGH-1: acotar el refinamiento del `AI Agent` en el canal telefonico a un maximo de 2 intentos. Al agotarse, el flujo SHALL derivar a un nodo terminal que persiste el incidente con `requiere_revision_humana=true` en lugar de volver a invocar al agente pago. El refinamiento dentro del tope se conserva.
- HIGH-4: marcar el correo como leido en TODAS las ramas terminales (exito, rechazo y error), no solo en la rama de exito del correo, para que un fallo o rechazo no se reprocese cada minuto.
- HIGH-4: idempotencia por `Message-ID` de Outlook. Se agrega una columna `origen_message_id` UNIQUE y nullable a `Incidente`, con su migracion Alembic; N8N envia el `Message-ID`; el backend cortocircuita un duplicado antes de clasificar, sin llamada paga.
- HIGH-2: extender el contrato de alta para aceptar una clasificacion precalculada (sector predicho + confianza + origen explicito). Cuando viene presente y valida, el backend omite la reclasificacion (sin llamada paga) y registra que provino de N8N. Se conserva la clasificacion server-side cuando el resultado no viene (formulario web).
- MEDIUM-3: apuntar la notificacion del backend a un webhook N8N dedicado que no crea incidentes (o llevar un flag explicito de origen), y documentar el acoplamiento para que la seguridad sea explicita y no accidental.

**Medio — backlog inicial**

- MEDIUM-1: acotar la rafaga inicial de correos con un filtro `receivedDateTime` (lookback de 24 h como valor elegido y documentado en el workflow).

**Fuera de alcance**

- Doble transcripcion de Twilio (`<Record transcribe="true">` + Voice Insights call-summary): requiere confirmar la cuenta de Twilio.
- Fijar la version de la imagen `n8nio/n8n`.
- Limpiar variables `TWILIO_*` sin uso de `.env.example`.
- Agrupacion por fecha UTC en `EstadisticasRepository._period_expression` (fix separado).

## Capabilities

### New Capabilities

- `incident-intake-guards`: guardas del contrato de alta del backend que evitan trabajo pago redundante e incidentes duplicados: creacion idempotente por `origen_message_id` (columna UNIQUE nullable + migracion), aceptacion de una clasificacion precalculada con origen explicito que omite la reclasificacion pagada, y un flag explicito de origen/evento para que eventos de notificacion nunca creen incidentes. Cubre HIGH-4, HIGH-2 y MEDIUM-3 del lado backend.

### Modified Capabilities

- `n8n-workflow`: tope de intentos del agente pago con salida terminal a revision humana, marcado de correo como leido en todas las ramas terminales, filtro de lookback `receivedDateTime`, y envio del `Message-ID` y de la clasificacion precalculada con origen explicito en el POST al backend. Cubre HIGH-1, HIGH-4, HIGH-2 y MEDIUM-1.
- `n8n-notification`: la notificacion hacia N8N apunta a una superficie dedicada que no crea incidentes y declara explicitamente el acoplamiento; un evento de notificacion MUST NOT poder crear un incidente. Cubre MEDIUM-3.

## Impact

- **N8N**: `n8n/workflow.json` (nodo `AI Agent`, nodo IF `La clasificacion de la IA es valida`, ramas de correo, trigger Outlook, nodos de persistencia y notificacion), `docs/n8n-workflow-guide.md`.
- **Backend**: `App/Backend/app/models/incidente.py`, `App/Backend/app/schemas/incidente.py`, `App/Backend/app/services/incidente_service.py`, `App/Backend/app/repositories/incidente_repository.py`, `App/Backend/app/utils/n8n_webhook.py`, `App/Backend/alembic/versions/` (nueva migracion), `App/Backend/app/config/settings.py`.
- **Infra**: `docker-compose.yml` (`N8N_WEBHOOK_URL` deja de apuntar a la base del webhook sin ruta).
- **Tests**: `App/Backend/tests/test_n8n_workflow.py` (contratos estructurales del workflow), `App/Backend/tests/test_api_incidentes.py` (idempotencia y clasificacion precalculada), tests de migracion.
- **Gobernanza**: ALTA para `n8n/workflow.json` (cambia comportamiento que afecta datos de usuario) y para la migracion de esquema; el apply de esas areas requiere checkpoint de aprobacion humana antes de escribir.
- **Dependencias**: `c-30-bugfix-seams` (contrato del workflow y login dinamico ya corregidos), `c-31-dry-run-harness` (validacion local de costo cero del tramo compartido), `c-32-disposable-test-db` (suite PostgreSQL sobre base descartable).
