## Why

Una auditoría de readiness del workflow N8N encontró ocho defectos de cableado que dejan ramas sin terminar: el cliente del formulario web espera indefinidamente en las ramas de rechazo/error, el correo de confirmación se envía sin destinatario, la confirmación telefónica se desvía al nodo de correo, el nodo de memoria Redis falla en runtime, el POST de persistencia puede inyectar dos cabeceras `Authorization`, el camino de error del backend no se audita, un fallo de notificación puede omitir la auditoría y la guía del workflow quedó desactualizada. Sin corregirlos, los tres canales no cierran su ciclo de forma confiable y la tesis no puede sostener el comportamiento documentado.

## What Changes

- **WEB DEAD-END**: agregar un guard `Es web?` y un nodo `respondToWebhook` de cierre, alcanzable desde las ramas de rechazo de validación, error del backend y revisión humana, de modo que el webhook con `responseMode: responseNode` siempre responda al cliente.
- **EMAIL CONFIRMATION RECIPIENT**: propagar el remitente original como `remitente` en la estructura normalizada y resolver `toRecipients` del nodo de confirmación desde el nodo normalizador aguas arriba, en lugar del ítem corriente (que es la respuesta del backend y no expone `remitente`/`from`).
- **TELEPHONY MIS-ROUTE**: quitar la conexión de las salidas telefonía y fallback del switch hacia `Correo de confirmacion al usuario`; la confirmación telefónica queda en la respuesta TwiML, sin nodo dedicado.
- **REDIS MEMORY**: declarar la credencial `redis` y parámetros de sesión no vacíos en el nodo `memoryRedisChat`, y extender la lista de tipos que requieren credenciales de la suite estructural para cubrirlo.
- **DUPLICATE AUTHORIZATION**: dejar un único mecanismo de autenticación en `HTTP POST a MTM-SRU` (header explícito `Bearer` con el token de `Login operador`), removiendo la autenticación por credencial `httpHeaderAuth` que duplicaba la cabecera.
- **NO AUDIT ON BACKEND-ERROR PATH**: cablear `Registro de auditoria` como sucesor de la salida de error (`main#1`) del POST de persistencia, en paralelo a `Es correo?`.
- **NOTIFICATION FAILURE SKIP AUDIT**: declarar manejo de error en `Notificar operador designado` (`onError: continueRegularOutput`) para que un fallo de notificación no aborte el registro de auditoría.
- **DOC DRIFT**: actualizar `docs/n8n-workflow-guide.md` (conteo de nodos, cantidad de tests, excepción conocida obsoleta de la rama de revisión) para que refleje el workflow real.

## Capabilities

### New Capabilities

- (ninguna)

### Modified Capabilities

- `n8n-workflow`: se agregan requerimientos para el cierre de todas las ramas terminales del webhook web, la resolución del destinatario de confirmación desde el remitente original, la confirmación telefónica por TwiML sin nodo de correo, la credencial y parámetros del nodo de memoria Redis, el mecanismo único de autenticación del nodo de persistencia, la auditoría en el camino de error del backend, la no-omisión de auditoría ante fallo de notificación, y la consistencia de la guía del workflow con el JSON exportado.

## Impact

- `n8n/workflow.json` — cableado de nodos, expresiones y credenciales de los ocho defectos.
- `App/Backend/tests/test_n8n_workflow.py` — extensión de la suite estructural y actualización de los tests que codificaban el cableado defectuoso (autenticación duplicada y ruteo telefónico).
- `docs/n8n-workflow-guide.md` — sincronización con el workflow real.
- Sin cambios en el backend, el frontend ni el clasificador. No se instalan credenciales ni se ejecutan flujos pagos.

## Dependencia con c-39

`c-40-n8n-wiring-fixes` DEPENDE de `c-39-e2e-timing-instrumentation` porque ambos editan `n8n/workflow.json`. c-39 agrega un campo de timestamp de ingreso al payload del POST y su columna/migración en el backend; c-40 no redefine ni duplica ese contrato. Para el fix del destinatario, c-40 propaga `remitente` dentro del ítem normalizado (contexto N8N) y NO lo agrega al payload del POST, de modo que no colisiona con el campo de c-39 ni con el contrato `IncidenteCreate`. La implementación de c-40 debe rebasarse sobre el `n8n/workflow.json` resultante de c-39.
