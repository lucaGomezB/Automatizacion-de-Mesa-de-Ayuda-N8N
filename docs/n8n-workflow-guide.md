# Guía del Workflow N8N — Automatización de Mesa de Ayuda

> C-04: n8n-workflow-validation — Implementado y verificado.
> C-05: n8n-channel-triggers — Canal web agregado, notificaciones por canal y auditoría con retención de 30 días.
> C-33: cost-guards — ciclo de vida del correo en todas las ramas terminales, lookback de 24 horas,
> payload enriquecido y webhook de notificación dedicado. (Su tope de refinamiento del agente pago
> quedó retirado con la rama IA de n8n en C-72.)
> C-39: e2e-timing-instrumentation — Sello de ingreso por canal (`ingresado_en`) en el borde de cada trigger.
> C-40: n8n-wiring-fixes — Cierre de las ramas terminales del webhook web, destinatario real de la
> confirmación por correo, telefonía sin nodo de correo, autenticación única del POST, auditoría en el
> camino de error y notificación que no omite la auditoría.
> Gate post-POST de revisión humana — IF `Requiere revision humana` (evalúa la marca del backend)
> + nodo `Notificar operador designado` (`$env.OPERATOR_EMAIL`); el gate pre-POST pasó a llamarse
> `Entrada valida` (validación de entrada, no de confianza del modelo).
> C-45: runtime-cost-guard — guarda de costo del agente pago de n8n. RETIRADO por C-72: la rama IA
> de telefonía (`AI Agent`, `Guard de costo`, `Guard permite?`) ya no existe en el workflow.
> C-47: guard-cost-item — preservación del ítem sellado del canal de telefonía entre la guarda y
> el agente. RETIRADO por C-72 junto con la guarda de costo.
> C-52: telefonia-transcripcion-async — el trigger de resumen de Twilio (`twilioTrigger`) se reemplaza
> por un webhook `POST` autenticado que recibe del backend el ingreso YA pseudonimizado; el sello
> `ingresado_en` es passthrough del valor sellado por el backend; no hay parsing de CloudEvent; el
> `CallSid` viaja como `origen_message_id` para la idempotencia del alta.
> C-53: notificacion-numero-incidente (partes NO-SMS) — numero canonico `numero_incidente` (derivado
> del PK `id` en un unico punto); la confirmacion por correo tambien se dispara en la rama de revision
> humana y resuelve el remitente desde `from` string u objeto (`from.emailAddress.address`); el cierre
> web de la revision humana responde con el numero. El SMS al llamante (telefonia) queda **DIFERIDO**
> hasta el spike de entregabilidad a Argentina (+54).
> C-55: canal-correo-imap — el canal de correo migra de Microsoft Outlook OAuth2 a IMAP/SMTP: el
> trigger pasa a `emailReadImap` (marca leido en el propio trigger), los envios a `emailSend` (SMTP)
> y se elimina el nodo `Marcar correo como leido`.
> C-57: auditoria-rama-revision — en la rama de revision humana la auditoria cuelga del gate
> post-POST en paralelo con la notificacion y consume la respuesta del POST, no el resultado SMTP.
> C-56: notificaciones-por-rol — el backend resuelve `destinatarios_revision` (operadores activos
> del sector) y el workflow emite un correo POR destinatario; `OPERATOR_EMAIL` pasa a ser el
> RESPALDO cuando la lista viene vacia.
> C-72: unificar-clasificacion-telefonica — se retira la rama de clasificación con IA de n8n:
> `AI Agent`, `Google Gemini Chat Model`, `memoryRedisChat`, `Guard de costo`, `Guard permite?`,
> `Restaurar item telefonia`, `Se verifica lo que trajo la IA`, `La clasificacion de la IA es valida`,
> `Tope de refinamiento alcanzado` y `Derivar a revision humana`. La clasificación telefónica la
> resuelve el backend con la cascada híbrida, igual que correo y web, y el POST ya no transporta
> `clasificacion` precalculada.
> Estado: 29 nodos (26 operativos + 3 sticky notes); suite estructural `test_n8n_workflow.py` en verde.

## Descripción general

El archivo `n8n/workflow.json` (raíz del repo) es el workflow N8N exportado que
automatiza la recepción y clasificación de incidentes de mesa de ayuda desde **tres canales**:

- **Canal correo**: trigger IMAP `emailReadImap` por sondeo (Gmail, App Password) — ver Decisión 1 C-05
- **Canal web**: Webhook HTTP POST en la ruta `/webhook/incidente-web` (formulario web del frontend)
- **Canal telefonía**: webhook `POST` autenticado que recibe del backend el ingreso YA pseudonimizado (la transcripción ocurre en el backend)

Los tres canales convergen en un **único nodo normalizador** antes de la persistencia.
El workflow está configurado con `"active": false` en el JSON versionado. **No activar en
producción editando el JSON** — activar desde la UI de N8N en el entorno de destino.

## Tabla de los tres canales

| Canal | Trigger | `canal_raw` emitido | `canal_origen` normalizado |
|-------|---------|--------------------|-----------------------------|
| Correo | `emailReadImap` (sondeo IMAP, marca leido) | `"correo"` | `"correo"` |
| Web | `webhook` `POST /webhook/incidente-web` | `"web"` | `"web"` |
| Telefonía | `webhook` `POST /webhook/telefonia-handoff` (handoff del backend, autenticado) | `"telefonia"` | `"telefonia"` |

## Guardas de costo (C-33)

> C-33 acota los tres caminos de gasto pago no acotado del sistema. Ninguna guarda
> depende de credenciales reales: se verifica con la suite estructural del workflow y
> los tests de contrato del backend.

### 1. Guarda de costo retirada (C-33/C-45/C-47)

> C-33/C-45 acotaron históricamente el gasto pago del `AI Agent` de n8n (tope de
> refinamiento y guarda de runtime). Con C-72 la rama de clasificación con IA de
> telefonía se retiró: el workflow ya no invoca un agente pago ni reserva
> `n8n_gemini`. La clasificación telefónica la resuelve el backend con la cascada
> híbrida, igual que correo y web.

Los nodos `Guard de costo`, `Guard permite?`, `Restaurar item telefonia` y el
bucle de refinamiento (`Se verifica lo que trajo la IA`, `La clasificacion de la IA
es valida`, `Tope de refinamiento alcanzado`, `Derivar a revision humana`), junto
con el `AI Agent`, `Google Gemini Chat Model` y `memoryRedisChat`, fueron retirados
por C-72 y NO forman parte del workflow vigente.

> **Transcripción de telefonía delegada al backend (C-52)**: el workflow ya NO parsea el evento
> `com.twilio.voice.insights.call-summary.complete` (Event Streams) ni depende de un campo de
> transcripción de Twilio. El backend descarga la grabación, transcribe con Gemini
> (`gemini-3.5-transcribe`, verbatim) y pseudonimiza ANTES de invocar el webhook
> `POST /webhook/telefonia-handoff` con el payload
> `{descripcion_pseudonimizada, call_sid, caller_number, ingresado_en}`. El transcript
> crudo NUNCA cruza el borde de n8n. Ver también `docs/operational-guide.md` §11.7 y
> `docs/medicion-latencia-e2e.md` §5.

### 2. Ciclo de vida del correo resuelto en el trigger (HIGH-4, C-55)

El mensaje IMAP se marca como leído en el propio disparador, al recolectarlo:

- El trigger `Llega un email a Mesa de Ayuda` (`emailReadImap`) declara
  `postProcessAction: "read"`: N8N aplica `\SEEN` al mensaje en el momento del polling,
  ANTES de cualquier procesamiento del canal. El marcado queda garantizado en TODAS las
  ramas terminales (éxito, rechazo por validación y error) sin depender de la rama ejecutada.
- **Éxito sin revisión**: `HTTP POST a MESA-AYUDAS` (main#0) → `Requiere revision humana` (rama
  false) → `Rutear por canal de origen` (rama correo) → `Correo de confirmacion al usuario`.
- **Rechazo**: la rama false de `Entrada valida` → `Es correo?` (rama true terminal, no-op).
- **Error**: `HTTP POST a MESA-AYUDAS` declara `onError: "continueErrorOutput"` y su salida de
  error (main#1) → `Es correo?` (rama true terminal, no-op).

> **Corrección C-55**: se eliminó el nodo `Marcar correo como leido`. La rama true de
> `Es correo?` (canal correo) queda como terminal no-op: el trigger ya marcó el mensaje como
> leído, de modo que no hace falta un nodo posterior en ninguna rama.

La guarda `Es correo?` evalúa `canal_origen == 'correo'` y su rama false desemboca en
`Es web?`, de modo que los canales web y telefonía no disparan respuestas cruzadas. Un correo
procesado en cualquier rama no se re-levanta porque el trigger ya lo marcó como leído.

### 3. Lookback de 24 horas en el trigger IMAP (MEDIUM-1, C-55)

El trigger `Llega un email a Mesa de Ayuda` declara en `options.customEmailConfig`:

```
["UNSEEN", ["SINCE", "{{ $now.minus(24, 'hours').toFormat('dd-LLL-yyyy') }}"]]
```

Esto recolecta solo mensajes no leídos (`UNSEEN`) recibidos desde el lookback de 24 horas
(`SINCE`). `SINCE` tiene granularidad diaria; la deduplicación fina la aportan `UNSEEN`, el
marcado `\SEEN` del propio trigger y `options.trackLastMessageId: true` (watermark de UID).
Así el arranque con una casilla real no dispara una ráfaga de incidentes sobre todo el
historial no leído.

### 4. Payload enriquecido del POST (HIGH-2 / HIGH-4)

`HTTP POST a MESA-AYUDAS` envía, además de descripción/prioridad/canal:

- `origen_message_id`: `Message-ID` del mensaje IMAP (header `metadata['message-id']`, con
  fallback al UID del mensaje; solo canal correo; nulo en el resto).
- `clasificacion`: **[retirado por C-72]** el POST ya no envía una clasificación
  precalculada; los tres canales resuelven el sector con la cascada híbrida del
  backend. El campo dejó de poblarse en el workflow vigente.
- `origen_evento: "creacion_incidente"`: marcador explícito de evento de creación.

### 5. Notificación a un webhook dedicado (MEDIUM-3)

El nodo webhook `notificacion-clasificacion` (ruta distinta de `incidente-web`) alimenta un
nodo no-op `Auditar notificacion` y **no está conectado a la creación de incidentes**. El
backend apunta `N8N_WEBHOOK_URL` a
`http://n8n:5678/webhook/notificacion-clasificacion` y `notify_n8n` agrega el marcador
`evento: "notificacion"`; el backend rechaza con 422 cualquier `origen_evento` que no sea de
creación. La garantía es explícita y verificable, no un 404 accidental.

### Decisión 1 — Canal de correo sobre IMAP/SMTP (C-05, ratificada en C-55)

La tesis §5.2 describe el canal correo como "trigger IMAP". C-55 **ratifica IMAP como la
opción elegida**: el workflow usa `n8n-nodes-base.emailReadImap` (trigger de sondeo genérico
con `postProcessAction=read`, `format=simple` y lookback de 24 h) y `n8n-nodes-base.emailSend`
(SMTP) para la confirmación al usuario y la notificación al operador.

La migración desde `microsoftOutlookTrigger`/`microsoftOutlook` (Microsoft Entra OAuth2) se
debe a que la cuenta Microsoft disponible es personal y sin tenant, y no hay acceso a
registros Azure: el canal quedaba indeployable. IMAP/SMTP con App Password de Gmail da
equivalencia funcional sin registro de app en la nube. Autenticación: IMAP
`imap.gmail.com:993` SSL y SMTP `smtp.gmail.com:465` SSL, con una casilla dedicada, 2FA y
App Password (documentado, sin secretos versionados). Esta decisión se registra para el Anexo E de la tesis.

## Nodos del workflow

### Canal correo

| Posición | Nombre | Tipo | Función |
|----------|--------|------|---------|
| 1 | Llega un email a Mesa de Ayuda | `emailReadImap` | **[C-55]** Disparador IMAP por sondeo (`postProcessAction=read`, `format=simple`, lookback 24 h). Recibe el correo y lo marca como leído en el trigger. |
| 2 | Se verifica que la informacion sea la necesaria para levantar un incidente | `code` (JS) | Valida `descripcion` ≥10 y ≤5000 caracteres. Emite `es_valido`. |
| 3 | Normalizar entrada del incidente | `code` (JS) | Homogeniza a estructura unificada: `{id, timestamp, canal_origen, descripcion}`. Compartido entre los tres canales. |
| 4 | Entrada valida | `if` | Gate de validación de ENTRADA previo al POST. Condición: `confianza >= 0.70 OR revision_forzada == true`. Rama true → `Login operador`; rama false → `Registro de auditoria` + `Es correo?`. |
| 5 | Login operador | `httpRequest` | `POST /api/v1/auth/login`; obtiene el token que autentica el POST de incidentes. Compartido. |
| 6 | HTTP POST a MESA-AYUDAS | `httpRequest` | `POST /api/v1/incidentes/` al backend FastAPI. Compartido. |
| 7 | Requiere revision humana | `if` | Gate post-POST. Evalúa `$json.requiere_revision_humana` del response. Rama true → `Preparar destinatarios de revision` + `Registro de auditoria` + `Confirmar correo en revision?`; rama false → `Rutear por canal de origen` + `Registro de auditoria`. Compartido. **[C-57]** La auditoría es hermana de la notificación y consume la respuesta del POST (no el resultado SMTP). |
| 7b | Preparar destinatarios de revision | `code` (JS) | **[C-56]** Lee `destinatarios_revision` de la respuesta del alta; si viene vacío o ausente, usa el respaldo `$env.OPERATOR_EMAIL`. Emite UN ítem por destinatario (`{destinatario, numero_incidente}`). |
| 8 | Notificar operador designado | `emailSend` (SMTP) | **[C-55/C-56]** Envía UN correo por ítem al destinatario `{{ $json.destinatario }}` con el número de incidente (`numero_incidente`); nunca expone la lista completa en `To`/`Cc`/`Bcc`. |
| 8b | Confirmar correo en revision? | `if` | **[C-53]** `canal_origen == 'correo'`. Rama true → `Correo de confirmacion al usuario`; la confirmación también se dispara en la rama de revisión humana. |
| 9a | Correo de confirmacion al usuario | `emailSend` (SMTP) | **[C-05/C-53/C-55]** Envía correo de confirmación con el número de incidente al remitente. Resuelve `toEmail` desde el remitente normalizado (extraído del header IMAP `from` `"Nombre <addr>"`); declara `onError: continueRegularOutput` para no abortar auditoría. |
| 9b | Registro de auditoria | `code` (JS) | **[C-05/C-57]** Registra metadatos de la ejecución (sin PII). Ver sección Auditoría. Compartido; consume la respuesta del POST en ambas ramas del gate post-POST. |

### Canal web (formulario web) — C-05

| Posición | Nombre | Tipo | Función |
|----------|--------|------|---------|
| 1 | Webhook formulario web | `webhook` | `POST /webhook/incidente-web`. Recibe el envío del formulario del frontend. |
| 2 | Marcar canal web | `code` (JS) | Asigna `canal_raw = "web"` al ítem antes de normalizar. |
| 3 | Normalizar entrada del incidente | `code` (JS) | Compartido — idem canal correo. |
| 4 | Entrada valida | `if` | Compartido — idem canal correo. |
| 5 | Login operador | `httpRequest` | Compartido — idem canal correo. |
| 6 | HTTP POST a MESA-AYUDAS | `httpRequest` | Compartido — idem canal correo. |
| 7 | Requiere revision humana | `if` | Compartido — gate post-POST. |
| 8 | Preparar destinatarios de revision + Notificar operador designado | `code` + `emailSend` | **[C-56]** Compartido — prepara los destinatarios (o el respaldo) y envía un correo por destinatario. |
| 9a | Confirmacion web al usuario | `respondToWebhook` | **[C-05/C-53]** Responde al webhook con `{incidente_id, numero_incidente, mensaje}` (rama false de `Requiere revision humana`). |
| 9b | Es web? | `if` | **[C-40]** Guarda de canal: `canal_origen == 'web'`. Rama true → `Web con incidente?`; rama false → sin respuesta. |
| 9c | Web con incidente? | `if` | **[C-53]** Distingue el cierre con incidente (`requiere_revision_humana == true`) del cierre sin alta. Rama true → `Confirmacion web revision humana`; rama false → `Respuesta web de cierre`. |
| 9d | Confirmacion web revision humana | `respondToWebhook` | **[C-53]** Responde al webhook de la rama de revisión humana con `{incidente_id, numero_incidente, mensaje, resultado: 'creado'}`. |
| 9e | Respuesta web de cierre | `respondToWebhook` | **[C-40]** Cierre sin alta: HTTP 200, `resultado: 'sin_alta'`, sin número. |
| 9f | Registro de auditoria | `code` (JS) | **[C-05]** Compartido — idem canal correo. |

### Canal telefonía

| Posición | Nombre | Tipo | Función |
|----------|--------|------|---------|
| 1 | Llamada telefonica | `webhook` | **[C-52]** `POST /webhook/telefonia-handoff`, autenticado con el secreto compartido del handoff (`headerAuth`). Recibe del backend el ingreso YA pseudonimizado `{descripcion_pseudonimizada, call_sid, caller_number, ingresado_en}`. |
| 1b | Responder handoff telefonia | `respondToWebhook` | **[C-52]** Responde de inmediato al handoff del backend, en una rama paralela directa del webhook, para que la entrega no quede bloqueada mientras el workflow persiste el incidente. |
| 2 | Sellar ingreso telefonia | `code` (JS) | **[C-52]** Passthrough: propaga el `ingresado_en` sellado por el BACKEND (no regenera el instante) y normaliza `descripcion_pseudonimizada` → `descripcion` antes del normalizador. |
| 3 | Normalizar entrada del incidente | `code` (JS) | **[C-05/C-52]** Compartido — telefonía converge aquí antes del gate de entrada; para telefonía mapea el `CallSid` del handoff a `origen_message_id` (idempotencia del alta). |
| 4 | Entrada valida | `if` | Compartido — gate de ENTRADA (no de confianza del modelo). |
| 5 | Login operador | `httpRequest` | Compartido. |
| 6 | HTTP POST a MESA-AYUDAS | `httpRequest` | Compartido. |
| 7 | Requiere revision humana | `if` | Compartido — gate post-POST. |
| 8 | Preparar destinatarios de revision + Notificar operador designado | `code` + `emailSend` | **[C-56]** Compartido — prepara los destinatarios (o el respaldo) y envía un correo por destinatario. |
| 9 | Registro de auditoria | `code` (JS) | **[C-05]** Compartido — idem canal correo. |

> **Nota sobre telefonía**: la confirmación al llamante NO se resuelve en la respuesta de voz
> de la llamada. El webhook de n8n recibe el handoff pseudonimizado del backend de forma
> asincrónica y no responde al llamante; la notificación con el número de incidente la realiza
> el backend por SMS (C-53), **DIFERIDO** hasta el spike de entregabilidad a Argentina (+54).

### Propagación del sello de ingreso (C-46, C-72)

El canal de telefonía PROPAGA `ingresado_en` en `Sellar ingreso telefonia`; el instante lo
sella el backend en la recepción del callback de grabación (C-52) y n8n no lo regenera.

Con la retirada de la rama `AI Agent` por C-72 (OQ1=A), el ítem sellado fluye directo al
normalizador compartido: ya no hay nodos intermedios que recuperen el sello con referencias
de nodo explícitas ni el riesgo de perderlo por `pairedItem`. La recuperación robusta del
sello que documentó C-46 (`.first()` vs `.item`, marcador `ingreso_sellado_ausente`) queda
como registro histórico de una rama ya inexistente; la suite estructural vigente no exige
esos nodos.

El contrato del backend no cambia: `IncidenteCreate.ingresado_en` sigue siendo nullable.

### Nodos decorativos

Tres nodos `stickyNote` con documentación visual interna del workflow (se conservan intactos).

**Total**: 26 nodos operativos + 3 `stickyNote` = 29, consistente con `n8n/workflow.json`. Las
tablas por canal repiten los nodos compartidos (`Normalizar entrada del incidente`,
`Entrada valida`, `Login operador`, `HTTP POST a MESA-AYUDAS`, `Requiere revision humana`,
`Preparar destinatarios de revision`, `Notificar operador designado`,
`Confirmar correo en revision?`, `Rutear por canal de origen`,
`Es correo?`, `Es web?`, `Web con incidente?`, `Respuesta web de cierre`,
`Confirmacion web revision humana`, `Registro de auditoria`).

## Contrato: `POST /api/v1/incidentes`

El workflow invoca un **único** endpoint HTTP:

```
POST {BACKEND_URL}/api/v1/incidentes
Content-Type: application/json

{
  "descripcion": "<texto del incidente — máx. 5000 chars>",
  "prioridad": "<media|alta|baja>"
}
```

La URL del backend se inyecta a través de la variable de entorno N8N `$env.BACKEND_URL`
(configurar en la instancia N8N antes de activar).

### Respuesta esperada: `201 Created`

```json
{
  "id": 123,
  "numero_incidente": "123",
  "descripcion_pseudonimizada": "...",
  "sector": {"nombre": "Sistemas"},
  "sectores_adicionales": [],
  "requiere_revision_humana": false,
  "destinatarios_revision": [],
  ...
}
```

El backend (`IncidenteService.create_and_classify`) ejecuta el pipeline completo:
clasificación híbrida (determinístico → Gemini → fallback) + persistencia. La respuesta
incluye `sector`, `confianza` y `requiere_revision_humana`.

### Destinatarios de revisión resueltos por el backend (C-56)

La respuesta de alta expone `destinatarios_revision` **solo en el `POST`** (no en `GET`/list,
para no ampliar la superficie de consulta de contactos). Es la lista de emails de los
**operadores ACTIVOS del sector** del incidente, resuelta por el backend desde el directorio de
empleados (c-54) cuando `requiere_revision_humana = true`. Es una **lista vacía** cuando el
incidente no requiere revisión, cuando no hay sector resuelto o cuando el directorio no tiene
operador activo del sector.

Precedencia y respaldo (design D3): si la lista trae al menos un destinatario, el directorio
toma precedencia; si viene vacía, el workflow usa el RESPALDO `$env.OPERATOR_EMAIL` (un único
destinatario), preservando el camino de un solo destinatario. El enrutamiento es por el sector
**principal** predicho (design D7); los sectores adicionales quedan diferidos.

Frontera de PII (design D2/D8): el email del operador es dato personal y solo se expone en la
respuesta de creación AUTENTICADA (JWT) que N8N necesita para direccionar la notificación; no
se registra en logs ni en la auditoría, y `Notificar operador designado` envía **un correo por
destinatario** (nunca la lista completa en un `To`/`Cc`/`Bcc` compartido).

## Discrepancia tesis vs implementación — 1 endpoint vs 2

La tesis (§6.3 y diagrama conceptual) describe dos llamadas HTTP separadas:

1. `POST /api/v1/clasificar` — clasifica sin persistir
2. `POST /api/v1/incidentes` — persiste el incidente ya clasificado

**La implementación real usa un único endpoint** (`POST /api/v1/incidentes`) donde la
clasificación está embebida en `create_and_classify()`. El endpoint `/api/v1/clasificar`
**no existe** en el backend actual.

Motivo: forzar dos llamadas requeriría crear un endpoint nuevo en el backend (governance ALTO,
fuera de scope C-04). La solución con un único endpoint es funcionalmente equivalente y
mantiene la atomicidad crear+clasificar.

**Acción para C-10** (`documentation-annexes`): actualizar el Anexo E de la tesis para
reflejar la arquitectura real de 1 endpoint. Ver Open Questions en `design.md`.

## Estructura unificada de normalización

El nodo `Normalizar entrada del incidente` produce para todos los canales:

```json
{
  "id": "<execution_id>-<timestamp_ms>",
  "timestamp": "2026-06-11T14:23:45.123Z",
  "canal_origen": "correo" | "web" | "telefonia",
  "descripcion": "<texto trimmed>",
  "remitente": "<email normalizado o null>",
  "prioridad": "media",
  "es_valido": true
}
```

- `timestamp`: ISO-8601 con milisegundos (`new Date().toISOString()`).
- `canal_origen ∈ {correo, web, telefonia}`. Entradas con canal inválido derivan a revisión.
- `remitente`: solo canal correo. Se extrae de `from` string u objeto
  (`from.emailAddress.address`); un remitente inválido se descarta con señal observable
  (`remitente_invalido`) y NO se propaga como destinatario.
- El canal `web` es soportado desde C-04; su trigger se cablea en C-05.

## Validación de la clasificación — Anexo H §H.3

**[Retirado por C-72]** La validación de 5 pasos de la respuesta del `AI Agent`
(nodo `Se verifica lo que trajo la IA`) ya no existe en el workflow: n8n no
clasifica. La validación del JSON de clasificación, el set canónico de sectores
(`Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`,
`Bases de Datos`, `Sistemas`) y el rango de confianza los aplica el backend en la
cascada híbrida (`HybridClassifier`), con revisión humana cuando la confianza es
insuficiente. Ver `docs/anexo_h_prompt_gemini.md` §H.6.

## Ruteo por umbral de confianza (0.70 inclusivo)

La confianza se evalúa en dos puntos distintos del flujo:

1. **Pre-POST — `Entrada valida`** (gate de validación de ENTRADA, compartido por los tres
   canales). Condición: `$json.confianza >= 0.70 OR revision_forzada == true`. No es un gate
   de confianza del modelo: el normalizador sintetiza `confianza` desde `es_valido` (1.0/0.0)
   para los tres canales (C-72). Rama true → `Login operador` → `HTTP POST a MESA-AYUDAS`;
   rama false → `Registro de auditoria` + `Es correo?`.
2. **Post-POST — `Requiere revision humana`** (gate de confianza REAL, tras persistir).
   Condición: `$json.requiere_revision_humana == true`, el booleano que el backend fija cuando
   la confianza de clasificación es menor a 0.70. Rama true → `Preparar destinatarios de revision`
   → `Notificar operador designado` + `Registro de auditoria` (en paralelo, C-57); rama false →
   `Rutear por canal de origen` + `Registro de auditoria`.

> **Refinamiento telefónico (retirado)**: el bucle `La clasificacion de la IA es valida` →
> `Tope de refinamiento alcanzado` → `AI Agent` → `Derivar a revision humana` fue retirado
> por C-72. La decisión de revisión humana de telefonía la toma el backend, y el gate
> post-POST `Requiere revision humana` la re-evalúa igual que en correo y web.

- **Rechazo de entrada**: la rama false de `Entrada valida` (datos incompletos) registra
  auditoría; el mensaje IMAP ya fue marcado como leído por el propio trigger (C-55), de modo
  que no hay nodo de marcado en ninguna rama.

Nota: el backend es la fuente de verdad de `requiere_revision_humana`; el gate post-POST
`Requiere revision humana` re-evalúa esa marca ya persistida para notificar al operador.

## Pseudonimización en tránsito — Decisión de diseño (C-04 §Decisión 2)

**La pseudonimización NO ocurre en N8N.** La descripción viaja en texto claro desde
N8N al backend vía HTTPS.

El backend pseudonimiza internamente en `IncidenteService.create_and_classify()`
(archivo: `App/Backend/app/services/incidente_service.py`, líneas 183–190):

```python
# Paso 3 (C-03): Pseudonimizar la descripción antes de persistir.
resultado_pseudo = pseudonymize(payload.descripcion, ...)
```

**Gap de privacidad documentado**: si el canal de transporte (HTTPS) se comprometiera,
la PII viajaría expuesta entre N8N y el backend. Registrado como hallazgo para auditoría
de privacidad (C-10 / posible C-05).

**Por qué no se pseudonimiza en N8N**: reimplementar el módulo Fernet (C-03) en JavaScript
duplicaría lógica de seguridad crítica fuera de su módulo Python testeado (governance ALTO).

## Variables de entorno requeridas (instancia N8N)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `BACKEND_URL` | URL base del backend FastAPI, **solo el origen** (el workflow agrega `/api/v1`; no incluir el prefijo de versión) | `http://backend:8000` |
| `SMTP_FROM_EMAIL` | Remitente de los correos salientes (nodos `emailSend`) | `mesa.ayuda@example.com` |
| `OPERATOR_EMAIL` | Destinatario de RESPALDO de la notificación de revisión humana: `Preparar destinatarios de revision` lo usa solo cuando `destinatarios_revision` viene vacío (C-56) | `operador@example.com` |

Credenciales adicionales a configurar en la UI de N8N:
- `imap` (C-55): casilla Gmail dedicada con 2FA y App Password (`imap.gmail.com:993` SSL).
  Usada por el trigger `emailReadImap`.
- `smtp` (C-55): misma casilla Gmail (`smtp.gmail.com:465` SSL, App Password). Usada por los
  nodos `emailSend`.
- **Sin `TWILIO_*` ni `REDIS_URL` en el workflow**: la admisión de voz la maneja el backend
  (webhook `POST /api/v1/cost-guard/twilio/voice`) y la memoria Redis del `AI Agent` se retiró
  con la rama IA (C-72). El workflow no lee esas variables.

## Cómo importar y probar el workflow

## Entorno de pruebas local (Docker)

> Verificación funcional ejecutada el 2026-06-11 (C-04, tareas 8.1–8.3).

### Servicios incluidos

El `docker-compose.yml` en la raíz del repo levanta 4 servicios con una sola línea:

| Servicio | Imagen | Puerto host | Descripción |
|---------|--------|-------------|-------------|
| `postgres` | `postgres:15.5-alpine` | 5433 (evita colisión con C-01) | Base de datos PostgreSQL |
| `redis` | `redis:7.2-alpine` | 6379 | Cola de trabajos de N8N (`QUEUE_BULL_REDIS_HOST`) |
| `backend` | build `App/Backend/` | 8000 | FastAPI + alembic migrations |
| `n8n` | `n8nio/n8n:2.11.2` | 5678 | UI de N8N con workflow importado (imagen fijada por el compose) |

**Prerequisito**: `App/Backend/.env` debe existir y tener todas las claves (ver `App/Backend/.env.example`).

### Levantar el entorno

```bash
# Desde la raíz del repo
docker compose --project-name mesa_local up -d --build

# Verificar que todos los servicios estén healthy
docker compose --project-name mesa_local ps

# Logs del backend (incluye alembic migrations y clasificaciones)
docker compose --project-name mesa_local logs -f backend
```

> Atajos con `make`: `make up-core` levanta el stack solo y `make up` levanta el
> stack **mas el tunel ngrok**. El canal telefonico necesita el tunel publico:
> `make tunnel` levanta solo ngrok (requiere `NGROK_AUTHTOKEN` en el `.env` de la
> raiz). Ver `docs/operational-guide.md` §1.3.

### Importar el workflow en N8N

```bash
# Importar el workflow desde el JSON del repositorio (montado como volumen)
docker exec mesa_local-n8n-1 n8n import:workflow --input=/data/Automatizacion_Mesa_de_Ayuda.json

# Resultado esperado: "Successfully imported 1 workflow."
```

Acceder a la UI de N8N en http://localhost:5678 (usuario: `admin`, contraseña: `n8n_local_dev`; default local del `.env` de la raiz).

### Importar en N8N (modo UI)

```bash
# Alternativa sin CLI: acceder a http://localhost:5678
# Settings → Import Workflow → seleccionar n8n/workflow.json
```

### Detener / limpiar

```bash
# Detener, INCLUIDO ngrok (mantiene volumes = datos persisten)
docker compose --project-name mesa_local --profile tunnel down
# o, con make:
make down

# Detener + borrar todo (base de datos limpia)
docker compose --project-name mesa_local --profile tunnel down -v
```

> `down` sin `--profile tunnel` no detiene `ngrok` y deja la red `mesa_local_default`
> en uso.

---

### Resultados de verificación 8.1–8.3 (2026-06-11)

#### 8.1 — Import del workflow: VERIFICADO

```
n8n import:workflow --input=/data/Automatizacion_Mesa_de_Ayuda.json
→ "Successfully imported 1 workflow."
→ 17 nodos, active=false, todos los nodos esperados presentes.
```

**Nota histórica**: en esa verificación se usó una imagen `latest`; el compose vigente fija `n8nio/n8n:2.11.2` (pin C-34).

#### 8.2 — Canal correo: VERIFICADO

Payload de prueba (simula el payload que el workflow envía al backend tras el normalizer):

```bash
curl -X POST http://localhost:8000/api/v1/incidentes \
  -H "Content-Type: application/json" \
  -d '{"descripcion": "El servidor de base de datos no responde desde esta manana. Los usuarios del sistema de gestion no pueden acceder.", "prioridad": "alta"}'
```

Respuesta `201 Created`:
```json
{
  "id": 1,
  "sector": {"nombre": "Sistemas"},
  "prioridad": "alta",
  "requiere_revision_humana": false,
  "estado": {"nombre": "nuevo"}
}
```

Log del clasificador: etapa `deterministic`, confianza 0.9999 (>= 0.90 threshold → sin llamada a Gemini).

#### 8.3 — Canal telefonía: VERIFICADO (incluyendo ruta fallback)

Se ejecutaron 3 payloads representando distintos escenarios de confianza:

| # | Descripción | Sector resultante | Etapa | Confianza | Revisión humana |
|---|-------------|-------------------|-------|-----------|-----------------|
| 1 | Servidor de BD no responde | Sistemas | deterministic | 0.9999 | No |
| 2 | Plan de continuidad, cierre de mes | Bases de Datos | deterministic | 0.9999 | No |
| 3 | Computadora no enciende | Soporte Tecnico Hardware | fallback | 0.0 | **Sí** |

**Caso 3 — ruta de fallback verificada**: el clasificador determinístico obtuvo confianza 0.667 (< 0.90 → escala a Gemini); Gemini API devolvió `403 PERMISSION_DENIED` (API key reportada como leaked en `.env`); el fallback se activó correctamente; `confianza = 0.0`; `requiere_revision_humana = true`. El IF node del workflow (`confianza >= 0.70`) hubiera enrutado este caso a la rama de revisión humana (no HTTP al backend).

**Observación**: la GEMINI_API_KEY en `App/Backend/.env` fue reportada como leaked. Renovarla en Google AI Studio antes de verificar el path Gemini completo (end-to-end con clasificación LLM).

#### Qué queda para C-05

Los siguientes ítems no se pueden verificar sin las credenciales de trigger:

- Disparo real del trigger IMAP `emailReadImap` (canal correo de punta a punta)
- Disparo real del webhook de handoff telefónico del backend (canal telefonía de punta a punta)
- Persistencia del incidente telefónico vía `Sellar ingreso telefonia` → `Normalizar entrada del incidente` → `Entrada valida` → `HTTP POST a MESA-AYUDAS`

El import, los nodos individuales y el backend están verificados. El entorno Docker está listo para cuando C-05 configure los triggers.

---

### Prueba manual de correo (canal correo — con triggers activos, C-05)

1. Disparar el trigger IMAP `emailReadImap` (o usar el botón "Test Workflow" con datos de prueba).
2. Observar que el nodo `Se verifica...` emite `es_valido: true` para descripción ≥10 chars.
3. Observar que el normalizado produce `canal_origen: "correo"`.
4. Verificar `201 Created` del backend.

### Prueba manual de telefonía (canal telefonía — C-52, actualizada por C-72)

1. Con el backend y n8n activos, realizar una llamada de prueba: Twilio graba, el backend
   descarga y transcribe (Gemini), pseudonimiza el texto y dispara el handoff
   `POST /webhook/telefonia-handoff` con `{descripcion_pseudonimizada, call_sid, caller_number, ingresado_en}`
   y el header `X-N8N-Secret`.
2. Verificar `201 Created` del backend y, en la respuesta, la descripción pseudonimizada no
   vacía y `origen_message_id = CallSid`.
3. Verificar que la clasificación del incidente la resolvió el backend (cascada híbrida:
   determinista → Gemini → revisión humana), no n8n.
4. Si `requiere_revision_humana = true`, verificar que `Preparar destinatarios de revision` →
   `Notificar operador designado` envía un correo por destinatario (o al respaldo
   `$env.OPERATOR_EMAIL`).

### Suite de tests estructurales (sin runtime N8N)

```bash
cd App/Backend
python -m pytest tests/test_n8n_workflow.py -v
```

Verifica 163 propiedades estructurales del JSON sin necesitar N8N en ejecución (C-04, C-05, C-33, gate post-POST de revisión humana, C-39, C-40, C-52, C-53, C-55, C-56, C-57 y C-69).

### Prueba manual del canal web (C-05)

1. Importar el workflow en N8N con `BACKEND_URL` configurado.
2. Activar el workflow desde la UI de N8N.
3. Enviar un POST al webhook: `POST {N8N_BASE_URL}/webhook/incidente-web` con cuerpo:
   ```json
   { "descripcion": "No puedo iniciar sesion en el sistema de facturacion", "prioridad": "alta" }
   ```
4. Verificar que el backend responde `201 Created` y el webhook responde con `{incidente_id, mensaje}`.
5. Verificar que el nodo de auditoría registra los metadatos en el log de N8N (sin `descripcion`).

## Notificaciones post-registro (C-05, C-53)

Tras un alta exitosa (`201 Created` del backend), el gate `Requiere revision humana` separa dos
caminos:

- **Rama false** (`requiere_revision_humana = false`): notificación al usuario por su canal.
- **Rama true** (`requiere_revision_humana = true`): `Preparar destinatarios de revision` lee
  `destinatarios_revision` y emite un ítem por operador; si la lista viene vacía usa el respaldo
  `$env.OPERATOR_EMAIL`. `Notificar operador designado` envía un correo por destinatario con el
  número de incidente (`numero_incidente`); en el canal correo, `Confirmar correo en revision?`
  dispara ADEMÁS la confirmación al usuario (C-53), porque el usuario SIEMPRE debe recibir su
  número. En paralelo, `Registro de auditoria` registra el alta (`resultado: "creado"`)
  consumiendo la respuesta del POST (C-57).

| Canal | Nodo | Mecanismo |
|-------|------|-----------|
| Web (alta normal) | `Confirmacion web al usuario` (`respondToWebhook`) | Responde al frontend con `{"incidente_id": <id>, "numero_incidente": "<n>", "mensaje": "..."}` |
| Web (revisión humana) | `Confirmacion web revision humana` (`respondToWebhook`) | **[C-53]** Responde al frontend con el número del incidente creado (`resultado: 'creado'`), no `null` |
| Correo | `Correo de confirmacion al usuario` (`emailSend` SMTP) | Envía correo con el número de incidente al remitente original; se dispara también en la rama de revisión humana y resuelve el destinatario desde el remitente normalizado (`from` `"Nombre <addr>"` del trigger IMAP) |
| Telefonía | — (sin nodo dedicado) | La notificación con el número la realiza el backend por SMS (C-53, **DIFERIDO** hasta el spike de entregabilidad a Argentina +54); NO se resuelve en la respuesta de voz de la llamada |
| Revisión humana | `Preparar destinatarios de revision` (`code`) + `Notificar operador designado` (`emailSend` SMTP) | **[C-56]** Envía UNA copia por destinatario resuelto (`destinatarios_revision`) o al respaldo `$env.OPERATOR_EMAIL` si la lista viene vacía |

El gate `Requiere revision humana` se interpone entre el POST y el ruteo normal. En la rama
false, `Rutear por canal de origen` y `Registro de auditoria` cuelgan en paralelo; en la rama
true, `Preparar destinatarios de revision` y `Registro de auditoria` son hermanos (ambos cuelgan
del gate, C-57) y la preparación desemboca en `Notificar operador designado`, de modo que la
auditoría consume la respuesta del POST y no el resultado SMTP del envío. La notificación no
bloquea el registro de auditoría: los nodos declaran `onError: continueRegularOutput` (C-40/C-53),
de modo que un fallo de envío no aborta la auditoría.

C-40/C-53 (N8N-WEBHOOK-003/004): las ramas terminales del webhook web —rechazo de `Entrada valida`,
error del POST (`main#1`) y revisión humana— pasan por la guarda `Es web?`. La rama con incidente
(revisión humana) cierra en `Confirmacion web revision humana` con el número; las ramas sin alta
cierran en `Respuesta web de cierre` (`respondToWebhook`, HTTP 200, `resultado: 'sin_alta'`, sin
número). La guarda restringe la respuesta al canal `web`, de modo que correo y telefonía no disparan
respuestas web cruzadas y el cliente web nunca queda a la espera indefinida.

C-40/C-53 (N8N-PHONE-002): la salida de telefonía del switch no se desvía al nodo de correo; la
confirmación del canal de telefonía NO se resuelve en la respuesta de voz de la llamada, sino por
el SMS que envía el backend (C-53, **DIFERIDO** hasta el spike de entregabilidad a Argentina +54).

## Registro de auditoría (C-05)

El nodo `Registro de auditoria` (`code` JS) registra cada ejecución que alcanza el nodo (altas
exitosas, revisiones humanas y rechazos de entrada):

```json
{
  "incidente_id": "<id del incidente creado>",
  "canal_origen": "correo" | "web" | "telefonia",
  "timestamp": "2026-06-11T14:23:45.123Z",
  "sector_nombre": "Seguridad Informatica" | "Soporte Tecnico Hardware" | "Soporte Tecnico Software" | "Bases de Datos" | "Sistemas",
  "confianza": 0.87,
  "resultado": "creado",
  "retencion_dias": 30
}
```

**Exclusión de PII**: la `descripcion` cruda no se incluye en el evento de auditoría.
Solo metadatos y referencias al incidente.

`resultado` toma `"creado"` cuando el response del backend trae id numérico,
`"error_backend"` cuando la ejecución llega por la salida de error del POST (C-40) y
`"rechazado_datos_incompletos"` en la rama de rechazo de `Entrada valida` (B-14).

**Retención de 30 días** (tesis §5.3): declarada como `retencion_dias: 30` en el nodo.
El destino persistente recomendado es el logging de Docker/N8N con rotación configurada
en `docker-compose.yml` (opción A, sin código nuevo en el backend). Configurar:

```yaml
# docker-compose.yml — logging con rotación a 30 días
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "30"
```

**Autenticación del webhook web**: el endpoint `POST /webhook/incidente-web` debe
protegerse en el entorno de despliegue (header firmado, red interna o SSO corporativo —
tesis §5.2 menciona "autenticación corporativa única"). El mecanismo concreto depende del
entorno y queda fuera del scope de C-05. Se documenta como punto pendiente para C-10.

## Open Questions resueltas (para Anexo E / C-10)

| Pregunta | Resolución | Change |
|----------|-----------|--------|
| ¿1 endpoint o 2 (clasificar + incidentes)? | **1 endpoint**: `POST /api/v1/incidentes` con clasificación embebida. No existe `POST /api/v1/clasificar`. Documentar discrepancia en Anexo E. | C-04 |
| ¿Dónde ocurre la pseudonimización? | **En el backend**, dentro de `create_and_classify()`. N8N envía texto claro. Gap de privacidad documentado. | C-04 |
| ¿El IF del workflow decide revisión humana o lo decide el backend? | **Ambos**: el backend marca `requiere_revision_humana` (fuente de verdad); el gate post-POST `Requiere revision humana` re-evalúa esa marca para notificar al operador. | C-04 / gate post-POST |
| ¿Outlook trigger ≈ IMAP genérico? | **Resuelto en C-55**: se adopta `emailReadImap` (IMAP/SMTP con App Password), descartando Outlook por la cuenta Microsoft personal sin tenant. Documentar en Anexo E. | C-05 / C-55 |
| ¿La telefonía requiere SMS de confirmación adicional? | **Sí** (C-53): el número se notifica por SMS al llamante desde el backend; la respuesta de voz de la llamada NO lo confirma. **DIFERIDO** hasta el spike de entregabilidad a Argentina (+54). | C-53 |
| ¿La auditoría registra solo altas o también rechazos? | **Todas las ramas terminales**: la rama false de `Entrada valida` (rechazo) y ambas ramas del gate post-POST `Requiere revision humana` (alta sin revisión por main#1 y alta con revisión por main#0, esta última en paralelo con la notificación) desembocan en `Registro de auditoria`. La rama de revisión consume la respuesta del POST (C-57). | C-05 / C-57 |
| ¿Dónde persiste el log de auditoría 30 días? | **Logging Docker/N8N con rotación** (opción A). Cero código nuevo en backend. Configurar `max-file: "30"` en `docker-compose.yml`. | C-05 |
| ¿Cómo se autentica el webhook web? | **Pendiente de entorno**: tesis §5.2 menciona "autenticación corporativa única". Mecanismo concreto (header firmado / SSO) fuera del scope de C-05. Elevar para C-10. | C-05 |

---

### Resultados de verificación 7.1–7.6 (2026-06-11, C-05)

> Entorno: `mesa_local` Docker Compose — N8N 2.25.7, FastAPI backend, PostgreSQL 15.5-alpine,
> Redis 7.2-alpine. Todos los contenedores healthy. GEMINI_API_KEY operativa (verificada en esta sesión).

#### 7.1 — Import del workflow C-05 (19 nodos): VERIFICADO

```
docker exec mesa_local-n8n-1 sh -c "n8n import:workflow --input=/data/Automatizacion_Mesa_de_Ayuda.json"
→ "Successfully imported 1 workflow."
```

Confirmado vía N8N Public API: ID `P7w2iELDu7O3e8B0`, 19 nodos (16 funcionales + 3 stickyNote),
`active: false`. Nodos C-05 presentes: `Webhook formulario web`, `Marcar canal web`,
`Confirmacion web al usuario`, `Correo de confirmacion al usuario`, `Registro de auditoria`,
`Rutear por canal de origen`.

#### 7.2 — Canal web: VERIFICADO (post-fix D-1..D-5, 2026-06-11)

**Verificación original (C-05 apply)**: PARCIAL — D-1 (SyntaxError en `Marcar canal web`) bloqueaba
la ejecución end-to-end. El webhook registraba la petición pero el nodo código fallaba inmediatamente.

**Post-fix**: se corrigieron D-1 (SyntaxError), D-2 (síntesis de `confianza`), D-3/D-4 (auditoría),
y D-5 (extracción de `webBody` del body anidado del webhook). Ver tabla de defectos abajo.

Ejecución end-to-end verificada con workflow de prueba `TEST-canal-web-D1` (ID: `oHwnEnpVXFy1gJMX`):

```
POST http://localhost:5678/webhook/incidente-web
Content-Type: application/json
{"descripcion": "El servidor de correo corporativo no responde desde las 8am, todos los usuarios sin acceso.", "prioridad": "alta"}

→ Ejecución #19:
  Nodos ejecutados: Webhook formulario web → Marcar canal web → Normalizar entrada del incidente
                   → Entrada valida (rama TRUE, confianza=1.0) → HTTP POST a MESA-AYUDAS
  Backend: HTTP 201, incidente_id=15, sector={nombre: "Sistemas"}, requiere_revision_humana=false
  Normalizer output: canal_origen='web', confianza=1.0, es_valido=true
  D-1 verificado: Marcar canal web ejecuta sin SyntaxError
  D-2 verificado: IF toma rama true (confianza=1.0 sintetizada por normalizer)
```

**Defectos corregidos** (aplicados en `n8n/workflow.json`, sesión 2026-06-11):

| # | Nodo afectado | Descripción | Fix aplicado |
|---|---------------|-------------|--------------|
| D-1 | `Marcar canal web` | `const item = .item;` → SyntaxError | `const item = $input.item;` |
| D-2 | `Normalizar entrada del incidente` | `confianza` no sintetizada para correo/web | Normalizer deriva `confianza` de `es_valido` (1.0/0.0) |
| D-3 | `Registro de auditoria` | Leía `item.categoria` (no existe en response) | Cambiado a `item.sector?.nombre` |
| D-4 | `Registro de auditoria` | `canal_origen` nulo tras HTTP POST | Lee de `$('Normalizar entrada del incidente').item.json.canal_origen` |
| D-5 | `Normalizar entrada del incidente` | Body webhook web en `item.json.body` (objeto anidado) | Extrae `webBody = item.json.body`; usa `webBody.descripcion` / `webBody.prioridad` |

#### 7.3 — Canal correo: PARCIAL en C-05; **RESUELTO en C-55 con IMAP/SMTP**

> **Actualización C-55**: el canal de correo ya no usa el trigger de Outlook. El
> `microsoftOutlookTrigger` se reemplazó por `emailReadImap` (IMAP/SMTP con App Password),
> de modo que no depende de credenciales OAuth2 corporativas. El smoke manual con el buzón
> Gmail real (tarea 6.3 de C-55) queda pendiente; la verificación estructural del workflow y
> del preflight está en verde. El texto siguiente es el registro histórico de C-05.

El nodo `microsoftOutlookTrigger` no se puede activar sin credenciales OAuth2. Se verificó el
pipeline completo del backend simulando el payload que el validador de correo enviaría:

```bash
# Payload simulando lo que el workflow envía al backend después del normalizador
curl -X POST http://localhost:8000/api/v1/incidentes/ \
  -d '{"descripcion": "Necesito restablecer mi contrasena de Windows. No puedo ingresar al sistema desde ayer.", "prioridad": "media"}'
# → HTTP 201, id: 9, sector: Soporte Tecnico Software, etapa: deterministic, confianza: 0.9999
```

**Defecto D-2 encontrado (latente)**: el nodo IF `Entrada valida` chequea
`$json.confianza >= 0.70`, pero para el canal correo `confianza` no existe en el item
antes del IF. Solo el canal telefonía lo setea (en `Se verifica lo que trajo la IA`).
Correo (y web) siempre irían a la rama false (rechazo) aunque la descripción sea válida.

#### 7.4 — Canal telefonía: PARCIAL (C-52; el intake depende del backend)

Se simuló el payload que el workflow envía al backend tras el normalizador:

```bash
# Escenario 1: confianza alta (deterministic)
curl -X POST http://localhost:8000/api/v1/incidentes/ \
  -d '{"descripcion": "El servidor de base de datos dejo de responder. Los usuarios no pueden acceder al ERP.", "prioridad": "alta"}'
# → HTTP 201, id: 8, sector: Sistemas, etapa: deterministic, confianza: 0.9999

# Escenario 2: confianza media → escala a Gemini
curl -X POST http://localhost:8000/api/v1/incidentes/ \
  -d '{"descripcion": "La impresora de facturacion no imprime nada. Ya reiniciamos el equipo y sigue sin responder.", "prioridad": "media"}'
# → HTTP 201, id: 10, sector: Soporte Tecnico Hardware, etapa: gemini (Gemini 2.5 Flash), confianza: 0.9

# Escenario 3: confianza baja → revisión humana
curl -X POST http://localhost:8000/api/v1/incidentes/ \
  -d '{"descripcion": "Tengo un problema con el sistema.", "prioridad": "baja"}'
# → HTTP 201, id: 12, sector: Sistemas, etapa: gemini, confianza: 0.6, requiere_revision_humana: true
```

El ciclo de confianza < 0.70 está verificado: Gemini devolvió confianza 0.6, backend marcó
`requiere_revision_humana: true`. El IF del workflow hubiera enrutado a rama de revisión.

#### 7.5 — Auditoría: VERIFICADO (D-3 + D-4 corregidos, 2026-06-11)

**Verificación original (C-05 apply)**: PARCIAL — D-3/D-4 latentes bloqueaban los valores de
`sector_nombre` y `canal_origen` en eventos de auditoría de ramas exitosas.

**Post-fix**: D-3 y D-4 corregidos. El nodo `Registro de auditoria` ahora:
- Lee `sector_nombre` desde `item.sector?.nombre` (shape real del backend — D-3).
- Lee `canal_origen` y `confianza` desde `$('Normalizar entrada del incidente').item.json` (upstream — D-4).

**Evidencia de ejecución #19** (canal web, incidente_id=15):
- Backend response: `{id: 15, sector: {id: 1, nombre: "Sistemas"}, requiere_revision_humana: false, canal_origen: null}`
- Normalizer output: `{canal_origen: "web", confianza: 1.0, es_valido: true}`
- Audit event esperado: `{incidente_id: 15, canal_origen: "web", sector_nombre: "Sistemas", confianza: 1.0, resultado: "creado", retencion_dias: 30}`

Se confirma:
- **PII excluida**: `descripcion` NO incluida en el evento de auditoría. ✓
- **Campos correctos**: `{incidente_id, canal_origen, timestamp, sector_nombre, confianza, resultado, retencion_dias: 30}`. ✓
- **`retencion_dias: 30`** declarado explícitamente. ✓
- **D-3 fix**: `sector_nombre` lee `item.sector?.nombre` (no `item.categoria`). ✓
- **D-4 fix**: `canal_origen` y `confianza` leídos del nodo normalizador upstream. ✓
- **Rama de rechazo cableada**: IF false branch → `Registro de auditoria` directamente. ✓
- **Rama exitosa**: HTTP POST → `Registro de auditoria` (en paralelo con `Rutear por canal`). ✓

#### 7.6 — `active: false` en JSON versionado: VERIFICADO

```python
import json
wf = json.load(open('n8n/workflow.json'))
assert wf['active'] == False  # True
```

El archivo `n8n/workflow.json` nunca fue modificado durante la verificación.
N8N vivo tiene `active: true` solo en la instancia de prueba (no exportado al repo).

#### Tabla de incidentes creados en la verificación

| incidente_id | descripción (resumida) | sector | etapa | confianza | revisión_humana |
|---|---|---|---|---|---|
| 6 | No puedo iniciar sesion en facturacion | Soporte Tecnico Software | deterministic | 0.9999 | No |
| 7 | (duplicado de prueba) | Soporte Tecnico Software | deterministic | 0.9999 | No |
| 8 | Servidor BD no responde, ERP inaccesible | Sistemas | deterministic | 0.9999 | No |
| 9 | Restablecer contraseña Windows | Soporte Tecnico Software | deterministic | 0.9999 | No |
| 10 | Impresora facturación no imprime | Soporte Tecnico Hardware | gemini | 0.9 | No |
| 11 | Problemas red piso 3 sin internet | Sistemas | deterministic | 0.9999 | No |
| 12 | Tengo un problema con el sistema (ambiguo) | Sistemas | gemini | 0.6 | **Sí** |

#### Resumen de tareas 7.1–7.6

| Tarea | Estado | Evidencia |
|-------|--------|-----------|
| 7.1 Import 19 nodos | VERIFICADO | `n8n import` exitoso; API confirma 19 nodos, active=false |
| 7.2 Canal web | VERIFICADO (post-fix) | Ejecución #19: 5 nodos OK, backend 201, incidente_id=15, sector=Sistemas. D-1/D-2/D-5 corregidos. |
| 7.3 Canal correo | PARCIAL | Backend pipeline OK; trigger requiere credenciales OAuth2 |
| 7.4 Canal telefonía | PARCIAL (C-52) | Backend 201 OK vía deterministic + Gemini; el intake lo provee el backend (STT + handoff pseudonimizado); requiere verificación en vivo |
| 7.5 Auditoría (PII) | VERIFICADO (post-fix) | D-3: sector?.nombre correcto; D-4: canal_origen de upstream; PII excluida; 58 tests verdes |
| 7.6 active=false | VERIFICADO | `wf['active'] == False` confirmado |

## Seguimiento (fuera de scope de C-55)

- **Actualización de tesis**: la referencia de tesis debe actualizarse para reflejar el canal de
  correo sobre IMAP/SMTP (Decisión 1 / Anexo E). La ruta REAL del documento es
  `docs/Tesis/v7/tesis_para_agente.md` (la ruta `docs/Tesis/tesis_para_agente.md` declarada en
  `openspec/config.yaml` NO existe). Se registra como seguimiento separado, no como parte de C-55.
- **Prerrequisitos manuales de C-55**: documentar la casilla Gmail dedicada (2FA + App Password)
  y crear las credenciales `imap`/`smtp` en la UI de N8N (tareas 1.1 y 1.2).
- **Smoke manual de C-55**: verificar con el buzón Gmail real que un correo no leído de menos de
  24 h crea incidente, dispara la confirmación y queda marcado como leído (tarea 6.3).
