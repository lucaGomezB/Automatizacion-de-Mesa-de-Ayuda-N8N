## Why

Las suites del proyecto estan en verde (backend, frontend y evaluacion) pero el sistema no funciona de extremo a extremo. Una auditoria con ejecucion de tests y revision de codigo confirmo 33 bugs reales mas unas 15 sospechas: el workflow N8N no envia el header `Authorization` (401 en todos los canales), el nodo `AI Agent` no tiene Chat Model conectado, el prompt del agente no interpola el payload del trigger, el contrato de salida del agente no coincide con el validador del backend, el `Switch` de canal esta mal configurado y varios endpoints devuelven 500 donde deberian devolver 4xx. Este change DEFINE el trabajo de correccion, priorizado por severidad y en formato TDD (los tests que fallan se escriben en `c-29-seam-tests`).

## What Changes

El trabajo se organiza por severidad. La implementacion no ocurre en este change: aqui solo se declaran requirements, decisiones y tareas.

**Blocker — flujo N8N y backend roto**

- B-01: obtener el JWT con un nodo de login dinamico (`POST /api/v1/auth/login`) y enviar el header `Authorization` (JWT Bearer) en los nodos HTTP que llaman al backend, alineado con `C-15`.
- B-02: conectar un Chat Model al nodo `AI Agent`.
- B-03: interpolar el payload del trigger en el prompt del agente (dejar de tener prompt estatico).
- B-04: alinear el contrato de salida del agente (JSON con `sector_predicho` y `confianza`) con el validador del backend.
- B-05: reconfigurar el `Switch` `Rutear por canal de origen` para operar en modo reglas/fallbackOutput sobre el canal normalizado, no sobre la respuesta del backend.
- B-06: corregir el `responseMode` del webhook para que el `respondToWebhook` sea alcanzable.
- B-07: extraer el cuerpo del correo desde el trigger de Outlook (`simple` no expone `body`).
- BE B1: eliminar `func.strftime` (solo SQLite) de `estadisticas_service.py`; `/api/v1/estadisticas/tendencias` responde en PostgreSQL.
- FE 1: unificar la base URL del API y hacer efectivo `VITE_API_BASE_URL` dentro de Docker.

**Alto**

- B-08: incluir `canal_origen_id` en el body normalizado (evita canal NULL).
- B-09: el formulario web usa el webhook N8N para el alta de incidentes (nunca directo a la API del backend); eliminar el webhook queda fuera de alcance.
- B-10: alinear `TwiML` (`transcribeCallback`) con Event Streams y eliminar el dominio placeholder.
- B-11: reemplazar `$env.BACKEND_URL` por una construccion compatible con N8N v2.
- B-12: eliminar el nodo de reenvio vacio conectado en bucle.
- BE B2: validar la existencia de la FK al hacer PATCH (evitar 500 y corrupcion silenciosa).
- BE B3: mapear `CanalOrigenNotFoundError` a 4xx con handler dedicado.
- BE B4: el pseudonimizador conserva terminos tecnicos/marcas (`Windows Server`, `Active Directory`, `SQL Server`, `Google Chrome`) en lugar de mascararlos como `[PERSONA]`.
- FE 2: corregir la barra final faltante (307 por el proxy que pierde `Authorization` y body).

**Medio**

- N8N B-13: corregir expresiones `.id` invalidas.
- N8N B-14: el auditor reporta los rechazos como creados.
- N8N B-15: los fallos del validador IA se reetiquetan como `correo`.
- N8N B-16: la rama falsa del telefono no regresa al agente.
- BE B5: unificar el envelope de error (422/401 hoy usan `detail`).
- BE B6: conservar referencia de la tarea `asyncio.create_task` fire-and-forget.
- BE B7: no instanciar `genai.Client` por request sin cierre.
- BE B8: corregir violaciones de disciplina de capas (routes -> services -> repositories -> models).

**Bajo**

- N8N B-17: barra final faltante en la URL del backend.
- FE 3: invalidacion de query del detalle del ticket.
- FE 4: contador de revision humana limitado a la pagina.
- FE 5: fechas del dashboard calculadas en UTC.
- FE 6: estado de carga con AND en lugar de OR.
- FE 7: volumenes de hot-reload inutiles.
- FE 8: fuga de red en los tests del frontend.

**Verificacion de sospechas (no confirmadas)**

- `_RE_TELEFONO` podria dejar un digito orfano.
- `_validate_gemini_response` podria aceptar booleanos.
- Cache de rotacion de la clave de cifrado.
- JWT sin `exp` obligatorio.
- Correos duplicados sin dedupe.
- `typeVersions` hardcodeados en N8N vs la imagen `latest`.

Fuera de alcance: alineacion con el documento de tesis (la tesis es referencia, no criterio de aceptacion); eliminacion del webhook N8N o cambio del formulario web para llamar directo a la API. No se implementan correcciones en este change.

## Capabilities

### New Capabilities

- `backend-error-contract`: envelope de error uniforme en toda la API, validacion de existencia de FKs de catalogo antes de persistir, y mapeo explicito de errores de dominio (`CanalOrigenNotFoundError`, etc.) a codigos 4xx. Cubre BE B2, B3, B5 y la disciplina de capas BE B8.
- `frontend-data-layer`: resolucion unica de la base URL del API (una sola fuente de verdad, `VITE_API_BASE_URL` efectivo en Docker), uso consistente de barra final para evitar el 307 del proxy, invalidacion de queries del detalle de ticket, contador de revision humana sobre el total y no sobre la pagina, manejo de fechas del dashboard sin desfase UTC, y estado de carga compuesto. Cubre FE 1, 2, 3, 4, 5 y 6.

### Modified Capabilities

- `n8n-workflow`: login dinamico y header `Authorization` en nodos HTTP, Chat Model del agente, prompt dinamico, contrato JSON del agente, `Switch` de canal en modo reglas, `responseMode` alcanzable, extraccion del body de Outlook, `canal_origen_id`, alta del formulario web por el webhook, rama falsa de telefono, auditoria precisa, etiqueta de fallos de validacion IA, expresiones `.id` validas, nodo de reenvio sin bucle, y barra final en la URL del backend. Cubre B-01 a B-17.
- `dashboard-analytics`: el endpoint de tendencias agrupa por periodo con SQL portable (PostgreSQL y SQLite), eliminando `func.strftime`.
- `data-pseudonymization`: el reemplazo de nombres propios excluye terminos tecnicos, productos y marcas para no degradar la clasificacion.
- `frontend-production-build`: el build de Docker propaga `VITE_API_BASE_URL` en tiempo de build; los volumenes de hot-reload del entorno de desarrollo quedan coherentes con lo que ejecuta el contenedor.
- `frontend-testing`: los tests del frontend quedan aislados de la red (sin fugas de requests reales).
- `integration-tests-postgresql`: la costura SQLite de los tests aplica `PRAGMA foreign_keys=ON` para que las violaciones de integridad referencial se detecten tambien en el entorno rapido, y la suite PostgreSQL deja de depender de un scope de event loop incorrecto.
- `n8n-notification`: la notificacion fire-and-forget conserva una referencia a la tarea para que el recolector de basura no la cancele antes de completarse.

## Impact

- **N8N**: `n8n/workflow.json`, `n8n/twilio/twiml.xml`, `n8n/twilio/README.md`, `docs/n8n-workflow-guide.md`.
- **Backend**: `App/Backend/app/services/estadisticas_service.py`, `App/Backend/app/services/incidente_service.py`, `App/Backend/app/core/error_handlers.py`, `App/Backend/app/utils/pseudonymizer.py`, `App/Backend/app/utils/n8n_webhook.py`, `App/Backend/app/classifiers/gemini_classifier.py`, `App/Backend/app/repositories/`, `App/Backend/tests/conftest.py`, `App/Backend/tests/test_schemas_pseudonimizacion.py` (cierre del skip restante).
- **Frontend**: `App/Frontend/src/services/api.ts`, `App/Frontend/src/hooks/`, `App/Frontend/src/pages/`, `App/Frontend/src/components/`, `App/Frontend/Dockerfile`, `docker-compose.yml`.
- **Contratos**: no cambian los strings canonicos de sector ni el contrato multietiqueta de C-27. Los cambios de error envelope y validacion de FK son retrocompatibles en exito.
- **Gobernanza**: N8N y servicios backend son ALTA; los cambios de auth (login dinamico del workflow, JWT) son CRITICA y requieren aprobacion humana explicita (aprobacion otorgada 2026-09-16); cambios de pseudonimizacion son ALTA (datos personales, Ley 25.326); frontend e infra de tests son MEDIA/BAJA.
- **Dependencia**: este change depende de `c-29-seam-tests`, que escribe los tests que fallan (TDD RED) y definen el comportamiento objetivo. La implementacion de las correcciones (TDD GREEN) vive en este change.
