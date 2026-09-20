## Context

Ver `proposal.md` — Why. Este documento fija el "cómo" de los ocho defectos de cableado del workflow N8N encontrados en la auditoría de readiness.

Estado actual relevante de `n8n/workflow.json`:

- El webhook `Webhook formulario web` usa `responseMode: responseNode` (`n8n/workflow.json:325`).
- El nodo `Es correo?` (`n8n/workflow.json:640-673`) tiene su salida `main#0` cableada a `Marcar correo como leido` y su `main#1` vacía.
- La salida de error (`main#1`) de `HTTP POST a MTM-SRU` va solo a `Es correo?` (`n8n/workflow.json:837-843`).
- `Notificar operador designado` desemboca en `Registro de auditoria` (`n8n/workflow.json:874-884`).
- El switch `Rutear por canal de origen` (`n8n/workflow.json:885-921`) conecta las salidas telefonía (`:906-912`) y fallback (`:913-919`) a `Correo de confirmacion al usuario`.
- El nodo `memoryRedisChat` no declara credencial ni parámetros (`n8n/workflow.json:284-294`).
- `HTTP POST a MTM-SRU` declara autenticación por credencial `httpHeaderAuth` (`n8n/workflow.json:115-116,135-140`) y además un header `Authorization` explícito (`:118-125`).
- La guía declara "29 nodos" (`docs/n8n-workflow-guide.md:10`), "94 propiedades" (`:463`) y una excepción obsoleta sobre la rama de revisión (`:65-67`).

Restricciones:

- La suite estructural es `App/Backend/tests/test_n8n_workflow.py`; sus tipos que requieren credenciales no cubren `memoryRedisChat` (`:1552-1556`).
- `IncidenteRead` (`App/Backend/app/schemas/incidente.py:179-203`) no expone `remitente` ni `from`.
- El contrato `IncidenteCreate` no admite campos ajenos; el remitente no debe agregarse al POST.
- Dependencia con `c-39-e2e-timing-instrumentation`: ambos editan `n8n/workflow.json`. Ver proposal.md — Dependencia con c-39.

## Goals / Non-Goals

**Goals:**

- Que cada rama terminal del webhook web responda al cliente.
- Que la confirmación por correo tenga destinatario real.
- Que la confirmación telefónica no se desvíe al nodo de correo.
- Que el nodo de memoria Redis sea estructuralmente configurable.
- Que el nodo de persistencia no pueda inyectar dos cabeceras `Authorization`.
- Que el camino de error del backend quede auditado.
- Que un fallo de notificación no omita la auditoría.
- Que la guía del workflow coincida con el JSON y la suite.

**Non-Goals:**

- Instrumentación de timing extremo a extremo (c-39).
- Hipótesis de Voice Insights / transcripción telefónica (Fase 2).
- Instalación de credenciales reales o ejecución de flujos pagos.
- Lógica del clasificador o compuerta de confianza.
- Diferenciar el código HTTP de la respuesta de cierre web por rama (se usa una respuesta de cierre genérica; ver Decision 1).

## Decisions

### Decision 1 — Cierre web con guard `Es web?` y un único `respondToWebhook` de cierre

Se agregan dos nodos:

- `Es web?` (`n8n-nodes-base.if`): condición `$('Normalizar entrada del incidente').item.json.canal_origen == 'web'`.
- `Respuesta web de cierre` (`n8n-nodes-base.respondToWebhook`): `respondWith: json`, `options.responseCode: 200`, cuerpo `{ incidente_id: null, mensaje: <texto>, resultado: 'sin_alta' }`.

Cableado:

- `Es correo?` `main#1` -> `Es web?` (hoy vacía).
- `Es web?` `main#0` -> `Respuesta web de cierre`.
- `Es web?` `main#1` -> sin conexión (telefonía/otros; su confirmación es TwiML).

Así, las tres ramas que hoy mueren en `Es correo?` `main#1` (rechazo de `Entrada valida`, error del POST y revisión humana) alcanzan un `respondToWebhook` cuando el canal es web.

Alternativas consideradas:

- (a) Un `respondToWebhook` por cada rama de muerte: requiere separar el merge en `Es correo?`, multiplicando nodos o duplicando guardas. Descartada por invasiva.
- (b) Diferenciar el `responseCode` por expresión según el ítem: frágil (depende de la forma del ítem de error de N8N) y no aporta al defecto. Se difiere como follow-up.
- (c) Cambiar el webhook a `responseMode: lastNode`: descartada porque rompe el contrato vigente y la respuesta con el id del incidente.

El `responseCode` fijo 200 con `resultado: 'sin_alta'` en el cuerpo permite al frontend distinguir una respuesta sin alta; la diferenciación de status HTTP por rama queda como no-goal.

### Decision 2 — El remitente viaja en la estructura normalizada, no en el POST

El nodo normalizador agrega `remitente: item.json.remitente || item.json.from || null`. El nodo `Correo de confirmacion al usuario` resuelve `toRecipients` como `={{ $('Normalizar entrada del incidente').item.json.remitente || '' }}`.

Alternativas consideradas:

- (a) Agregar `remitente` al cuerpo del POST: viola el contrato `IncidenteCreate` (campos ajenos) y colisiona con el campo de timestamp de c-39. Descartada.
- (b) Referenciar directamente el trigger `Llega un email a Mesa de Ayuda` desde el nodo de confirmación: funciona para correo, pero falla en runtime si el nodo de confirmación se alcanza desde otro canal. Descartada en favor de la estructura normalizada, que es channel-agnóstica y además es la fuente que ya usan el switch y la auditoría.
- (c) Mantener `$json.remitente || $json.from` (ítem corriente): es exactamente el defecto; el ítem corriente tras el POST es la respuesta del backend y no expone ninguno de los dos.

El remitente no se agrega al cuerpo del POST ni al registro de auditoría (PII).

### Decision 3 — Telefonía y fallback sin nodo de correo

Se eliminan las conexiones de las salidas telefonía (`index 2`) y fallback (`index 3`) del switch hacia `Correo de confirmacion al usuario`. La salida correo (`index 1`) conserva `Marcar correo como leido` y `Correo de confirmacion al usuario`; la salida web (`index 0`) conserva `Confirmacion web al usuario`.

Alternativa considerada: dejar la salida fallback apuntando a un nodo no-op. Descartada porque un canal desconocido no tiene destinatario de confirmación; terminar la rama es correcto.

### Decision 4 — Memoria Redis con credencial y parámetros declarados

El nodo `memoryRedisChat` declara una credencial `redis` con placeholder (consistente con el resto de credenciales del JSON: `REPLACE_WITH_*`) y parámetros de sesión no vacíos según el schema del nodo (clave de sesión y ventana de contexto). Se extiende `CREDENTIAL_REQUIRING_NODE_TYPES` (`App/Backend/tests/test_n8n_workflow.py:1552-1556`) para incluir `@n8n/n8n-nodes-langchain.memoryRedisChat`.

Alternativa considerada: eliminar el nodo de memoria por no ser necesario para una clasificación de un solo turno. Descartada porque cambia el comportamiento del agente y excede el alcance del defecto (configuración ausente). Se documenta como posible follow-up.

Nota: los nombres exactos de los parámetros se confirman contra el schema del nodo durante apply; el test estructural verifica parámetros no vacíos y credencial no vacía, sin fijar claves frágiles.

### Decision 5 — Un único mecanismo de autenticación en el nodo de persistencia

Se elimina de `HTTP POST a MTM-SRU` el campo `authentication: genericCredentialType`, `genericAuthType: httpHeaderAuth` y la credencial `credentials.httpHeaderAuth`. Se conserva `sendHeaders: true` con el header explícito `Authorization: =Bearer {{ $('Login operador').item.json.access_token }}`, que es el mecanismo exigido por N8N-AUTH-001 (token dinámico por login).

Esto obliga a actualizar el test existente `test_c29_incidentes_http_node_declares_authentication`, que hoy exige `parameters.authentication` no vacío. El test pasa a verificar el contrato corregido: existe exactamente un mecanismo, el header explícito referencia `Login operador`, y no coexiste con una credencial `httpHeaderAuth`.

Alternativa considerada: conservar la credencial y eliminar el header explícito. Descartada porque el token dejaría de resolverse dinámicamente desde `Login operador` y se rompería N8N-AUTH-001.

### Decision 6 — Auditoría en el camino de error del backend

Se agrega `Registro de auditoria` como sucesor de `HTTP POST a MTM-SRU` `main#1`, en paralelo a `Es correo?`. El nodo de auditoría ya tolera ítems sin respuesta HTTP (usa el normalizador aguas arriba). Se refina su detección de resultado para que un ítem de error de backend (`item.error`) se registre con `resultado` distinto de `creado`.

Alternativa considerada: insertar un nodo code intermedio que marque el error. Descartada por agregar un nodo sin necesidad; el propio nodo de auditoría puede detectar la forma de error.

### Decision 7 — Fallo de notificación no omite la auditoría

Se declara `onError: "continueRegularOutput"` en `Notificar operador designado`, manteniendo la arista `Notificar operador designado -> Registro de auditoria`. Así, si el envío falla, el nodo continúa y la auditoría se ejecuta.

Alternativa considerada: cablear `Registro de auditoria` como sucesor directo de `Requiere revision humana` `main#0` en paralelo a la notificación. Produciría doble auditoría cuando la notificación tiene éxito. Descartada.

### Decision 8 — Guía sincronizada y verificable

Se actualizan en `docs/n8n-workflow-guide.md`: el conteo de nodos (`:10`), el conteo de propiedades de la suite (`:463`) y la excepción obsoleta de la rama de revisión (`:65-67`). Un test estructural parsea el conteo declarado y lo compara con `len(workflow["nodes"])` y con el número de funciones `test_` de la suite, de modo que la guía no vuelva a divergir en silencio.

## Risks / Trade-offs

- [El `Es correo?` `main#1` es compartido por las tres ramas] -> La guarda `Es web?` restringe la respuesta al canal web; el test verifica que un canal no-web no dispare la respuesta.
- [La respuesta de cierre web es un 200 genérico aun en rechazo/error] -> El cuerpo incluye `resultado: 'sin_alta'` para que el frontend no lo trate como alta; la diferenciación de status HTTP queda como follow-up.
- [Detectar el error de backend por `item.error` depende de la forma del ítem de error de N8N] -> El defecto principal (que la auditoría no corre) se corrige por cableado; si la detección del resultado falla, cae a un valor distinto de `creado` y nunca registra un alta falsa.
- [`onError: continueRegularOutput` en la notificación silencia el fallo del envío] -> La auditoría registra la rama de revisión; el objetivo del defecto es priorizar la auditoría sobre la notificación.
- [Quitar `authentication` del nodo HTTP puede parecer una regresión de seguridad] -> El token sigue siendo dinámico y obligatorio por header; el test actualizado lo verifica y elimina la ambigüedad de doble cabecera.
- [c-39 también edita `n8n/workflow.json`] -> c-40 se rebasa sobre el resultado de c-39 y no toca el contrato de timing; el conteo de nodos de la guía se recalcula tras el rebase.

## Migration Plan

1. Implementar c-40 sobre el `n8n/workflow.json` resultante de c-39.
2. Aplicar los cambios de cableado y expresiones en `n8n/workflow.json`.
3. Extender/actualizar `App/Backend/tests/test_n8n_workflow.py` y correr la suite (`pytest tests/test_n8n_workflow.py`).
4. Actualizar `docs/n8n-workflow-guide.md` con los conteos reales.
5. Rollback: revertir el commit de c-40; el workflow y la suite vuelven al estado de c-39. No hay migración de datos ni cambios de backend.

## Open Questions

- Ninguna que bloquee specs, enfoque o desglose de tareas. La diferenciación del status HTTP por rama web y la eventual remoción del nodo de memoria Redis se registran como follow-ups fuera de alcance.
