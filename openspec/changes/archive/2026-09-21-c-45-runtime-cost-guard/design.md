## Context

Ver `proposal.md — Why` para la motivación. Restricciones verificadas que moldean el enfoque:

- No existe ningún tope de gasto/rate/quota en runtime. El único control es el preflight ESTÁTICO `scripts/preflight/cost_readiness.py`, de solo lectura, que verifica cableado y NO limita gasto ni corre por petición (ver `openspec/specs/cost-readiness/spec.md`).
- Superficies pagas (tres): (1) Gemini en el backend vía `HybridClassifier` (una llamada por incidente, sin reintentos; cortocircuito determinístico en `App/Backend/app/classifiers/hybrid.py:115-123`); (2) el nodo `AI Agent` de n8n (`options.maxIterations=2` más el bucle de refinamiento existente); (3) la transcripción de Twilio por llamada, configurada a nivel TwiML (`n8n/twilio/twiml.xml:12-17`, `<Record transcribe="true">`). Outlook y el formulario web son gratuitos.
- Punto de invocación paga del backend: `IncidenteService._resolve_classification` (`App/Backend/app/services/incidente_service.py:287-300`) llama a `HybridClassifier.classify`, que a su vez invoca `GeminiClassifier.classify`. La clasificación precalculada (`payload.clasificacion`, líneas 298-299) y el cortocircuito determinístico ya evitan la llamada paga.
- La transcripción de Twilio ocurre ANTES de n8n. El nodo `Llamada telefonica` de n8n es un Trigger sobre `com.twilio.voice.insights.call-summary.complete` (`n8n/workflow.json:258-277`): cuando llega el evento, el gasto de transcripción ya se produjo. Bloquear el gasto de Twilio exige un webhook de voz PRE-llamada (TwiML) que Twilio consulta antes de grabar/transcribir.
- El número de origen (`From`) NO se captura hoy: ni el workflow lo mapea ni el backend tiene campo de teléfono. Está disponible como parámetro estándar del webhook de voz pre-llamada y en el payload del evento call-summary.
- Infraestructura disponible: PostgreSQL en `docker-compose.yml:33-55` (backend con Alembic; revisión más reciente "006", la nueva será "007"), Redis en `docker-compose.yml:57-67` (hoy usado SOLO por la memoria del agente n8n, NO por el backend), FastAPI, `structlog`, `pydantic-settings` `Settings` (`App/Backend/app/config/settings.py`) y Alembic.
- Fallback existente reutilizable: ante `GeminiTimeoutError`/`GeminiUnavailableError`, `HybridClassifier` ya devuelve la categoría determinística con `confianza=0.0` y `requiere_revision_humana=True` (`hybrid.py:135-150`). La degradación por costo sigue ese mismo patrón.
- CI/dev deben permanecer offline y sin costo: los tests usan mocks/fakes.

## Goals / Non-Goals

**Goals:**

- Acotar en runtime el gasto de las TRES superficies pagas (Gemini backend, Gemini n8n, transcripción Twilio) con un presupuesto GLOBAL compartido en USD y un costo unitario por superficie.
- Aplicar además un rate limit por número de origen (llamadas por teléfono) sobre la superficie de telefonía.
- Enforcar la guarda antes de cada llamada paga, con degradación segura que nunca invoque al proveedor pago al excederse.
- Bloquear de forma REAL el gasto de Twilio mediante un webhook de voz pre-llamada que devuelve TwiML de permiso o de rechazo.
- Emitir observabilidad estructurada del disparo y de la indisponibilidad del almacén, y registrar la postura efectiva al arranque.
- Registrar el número de origen CRUDO con fines de atribución anti-abuso, acotado a los logs/almacén de la guarda y explícitamente fuera del corpus de evaluación.
- Dejar la guarda evaluable offline con almacén y reloj inyectados.

**Non-Goals:**

- No se modifica el preflight estático ni la capacidad `cost-readiness`.
- No se cambia la lógica de clasificación ni los umbrales (0.90 / 0.70) ni el contrato de la API de incidentes.
- No se introduce un gateway/proxy de red ni se reescribe el flujo de n8n más allá del nodo de guarda y su ruteo.
- No se agrega el número de teléfono al corpus de evaluación ni a las tablas de negocio del incidente.

## Decisions

### D1 — Capacidad nueva `runtime-cost-guard`, no extensión de `cost-readiness`

**Decisión:** introducir una capacidad nueva `runtime-cost-guard` en lugar de modificar `cost-readiness`.

**Rationale:** `cost-readiness` está acotada al preflight estático, de solo lectura, sin red ni credenciales. El enforcement en runtime tiene otro ciclo de vida (corre por petición, mantiene estado, degrada el flujo) y otros escenarios (ventana, límite, disparo, fail-closed, webhook). Extender `cost-readiness` mezclaría verificación estática con enforcement dinámico.

**Alternativas consideradas:** agregar un requisito "runtime" a `cost-readiness` — contamina una capacidad cuya promesa es "sin red ni credenciales" y complica el rollback.

### D2 — Guarda como wrapper del punto de llamada paga, con almacén y reloj inyectables

**Decisión:** implementar un componente de guarda con una función de decisión pura (`permitir` / `denegar` + causa) evaluada ANTES de invocar al proveedor pago, y una operación atómica de reserva en el almacén. Se cablea en los tres puntos de llamada paga (backend, n8n vía endpoint, Twilio vía webhook pre-llamada), no dispersando chequeos por la capa de rutas. El almacén de contadores y la fuente de tiempo se inyectan como protocolos, con adaptador PostgreSQL y un fake en memoria para tests.

**Rationale:** envolver el punto de llamada paga concentra el enforcement donde ocurre el gasto. La inyección de almacén y reloj hace la guarda determinista y offline-testeable. El patrón de inyección ya se usa en el proyecto (`HybridClassifier` acepta sub-clasificadores; `IncidenteService` acepta un classifier).

**Alternativas consideradas:** chequeos inline en `_resolve_classification` — se saltean si otro caller invoca Gemini; un middleware HTTP — no ve las llamadas internas del backend ni las de n8n.

### D3 — Presupuesto GLOBAL compartido en USD con costo unitario por superficie

**Decisión:** modelar el gasto como UNA bolsa global de USD por ventana, compartida por las tres superficies. Cada llamada paga reserva el costo unitario de su superficie. Los contadores mantienen, además, la cantidad de llamadas para el rate limit. La decisión es una función pura sobre (contadores, configuración, instante).

**Rationale:** una bolsa única refleja el objetivo real ("no gastar más de X por semana en total") y evita que una superficie agote por separado un presupuesto que las otras podrían usar. El costo real depende de tokens/modelo/duración; un costo unitario configurable da un tope determinista, offline-testeable y ajustable. La tasa se acota por cantidad de llamadas, la unidad que el operador controla.

**Alternativas consideradas:** presupuesto por superficie — fragmenta el tope y no expresa el límite global deseado; medición de tokens reales — precisa pero no determinista offline y más compleja.

### D4 — Degradación reutiliza el patrón de fallback existente, con política configurable

**Decisión:** cuando la guarda deniega, el punto de llamada lanza un error tipado de costo (`CostGuardTrippedError`), análogo a `GeminiTimeoutError`/`GeminiUnavailableError`. El `HybridClassifier` lo captura y aplica la política configurada: (a) degradar a determinístico + `requiere_revision_humana=True` (RESUELTO: política elegida), o (b) bloqueo duro con señal explícita. En ningún caso se invoca al proveedor pago.

**Rationale:** el manejo de fallo de Gemini ya existe y está probado; reutilizarlo minimiza el diff y garantiza que la degradación preserve la mejor estimación determinística. La degradación por costo es la MISMA que la degradación por store caído (fail-closed): determinístico + revisión humana.

**Alternativas consideradas:** encolar el incidente para revisión asíncrona — requiere infraestructura de colas inexistente; bloquear la creación del incidente — pierde el registro del incidente.

### D5 — Observabilidad con structlog y postura efectiva al arranque

**Decisión:** emitir dos eventos estructurados con campos estables:
- `cost_guard_tripped`: `cause` (`budget` | `rate` | `caller_rate`), `provider` (superficie paga), `window` (inicio de ventana ISO-8601 UTC), `limit` (valor configurado), `caller` (número crudo, solo si aplica). Sin secretos.
- `cost_guard_store_unavailable`: `cause` (`store_unavailable`), `provider`, `window`, `limit`, `caller`, `error_class`. Sin secretos.

Al arranque (lifespan de FastAPI), registrar la postura efectiva (habilitada/deshabilitada, presupuesto USD, ventana, costo unitario por superficie, rate global, rate por caller, política de degradación, política de store). Una llamada permitida no emite evento de disparo.

**Rationale:** `structlog` ya es el mecanismo de logging del proyecto; un evento con campos estables es consultable y testeable. La postura al arranque permite verificar la configuración sin leer código. El evento `cost_guard_store_unavailable` cumple la notificación del fail-closed.

**Alternativas consideradas:** solo una alerta externa — no hay canal de alertas definido; log en texto libre — no consultable.

### D6 — Almacén en PostgreSQL con migración Alembic 007 (RESUELTO)

**Decisión:** persistir los contadores de la guarda en PostgreSQL, en una tabla nueva `costo_guarda_contador`, creada por la migración `007_cost_guard_counters.py` (down_revision "006"). El backend ya usa PostgreSQL y Alembic; no se agrega un cliente Redis al backend.

Esquema de la tabla:

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `Integer` PK autoincrement | |
| `ambito` | `String(16)` NOT NULL | `global` \| `surface` \| `caller` |
| `clave` | `String(64)` NOT NULL | `global`; nombre de superficie; o número E.164 CRUDO para `caller` |
| `ventana_inicio` | `DateTime(timezone=True)` NOT NULL | inicio de la ventana (bucket tumbling) |
| `llamadas` | `Integer` NOT NULL default 0 | cantidad de llamadas reservadas |
| `costo_usd` | `Numeric(12, 6)` NOT NULL default 0 | gasto acumulado de la ventana |
| `created_at` / `updated_at` | `DateTime(timezone=True)` | vía `TimestampMixin` |

Restricción única: `(ambito, clave, ventana_inicio)`. Índice por `ventana_inicio` para purga de ventanas viejas. El `upgrade` crea la tabla; el `downgrade` la dropea. Docstring con la nota "Aprobacion humana explicita (gobernanza ALTA)", siguiendo el estilo de `006_add_timing_instrumentation.py`.

**Operación atómica de reserva:** el adaptador ejecuta, en su PROPIA sesión/transacción (fuera de la transacción del incidente), un `INSERT ... ON CONFLICT (ambito, clave, ventana_inicio) DO UPDATE SET llamadas = costo_guarda_contador.llamadas + 1, costo_usd = costo_guarda_contador.costo_usd + :costo RETURNING ...` para las filas `global`, `surface` y (si hay caller) `caller`. Con los valores resultantes evalúa la función pura; si deniega, hace ROLLBACK (la reserva no cuenta porque no hubo llamada); si permite, COMMIT. Esta secuencia evita la carrera "ambos chequean y ambos pasan" y no arrastra la transacción del incidente.

**Rationale:** sin dependencia nueva; transaccional y durable; auditable; el `UPSERT` atómico implementa el incremento concurrente de forma correcta. La ventana es un bucket tumbling de duración configurable anclado a epoch (por defecto 604800 s = 7 días), determinista y simple de reiniciar.

**Alternativas consideradas:** Redis (Opción A previa) — el backend no lo usa hoy y agregaría un servicio a su ruta; TTL más simple, pero se descartó por la decisión humana de PostgreSQL.

### D7 — Webhook de voz pre-llamada de Twilio (enforcement REAL de Twilio)

**Decisión:** exponer un endpoint público de cara a Twilio (sin JWT de operador), p. ej. `POST /api/v1/cost-guard/twilio/voice`, que Twilio consulta al recibir la llamada ANTES de ejecutar `<Record transcribe="true">`. El endpoint:

1. Recibe los parámetros estándar del webhook de voz (ver "Verificación del contrato de Twilio"): `From`, `To`, `CallSid`, `AccountSid`, `CallStatus`, `Direction`, entre otros.
2. Consulta la guarda: bolsa global (reserva 1 x `cost_guard_unit_cost_twilio_transcription_usd`) y rate por caller (clave = `From` crudo).
3. Responde TwiML (`Content-Type: text/xml`):
   - PERMITIDO: `<Response><Say ...>...</Say><Record maxLength="45" finishOnKey="#" transcribe="true" playBeep="true"/><Say ...>...</Say></Response>` (se traslada aquí el contenido hoy en `n8n/twilio/twiml.xml`).
   - DENEGADO: `<Response><Say voice="Polly.Mia-Neural" language="es-US">El servicio no está disponible en este momento. Intente más tarde.</Say><Hangup/></Response>`.

**Reserva con duración desconocida:** al inicio de la llamada no se conoce la duración. El modelo es "cantidad de llamadas x costo unitario por superficie", así que se reserva EXACTAMENTE una unidad del costo unitario de transcripción por llamada concedida, independientemente de la duración. Esto es consistente con el modelo y está acotado por `maxLength="45"` (la transcripción no puede exceder ese tope). Si la llamada se concede, la transcripción se ejecuta y el costo se incurre; no hay ajuste posterior por duración.

**Seguridad (corregida post-verify):** el webhook de voz de Twilio se autentica EXCLUSIVAMENTE con la firma `X-Twilio-Signature` (HMAC-SHA1 sobre la URL completa más los parámetros de formulario ordenados, en base64), porque Twilio Programmable Voice NO puede adjuntar headers personalizados a la petición del webhook: exigir `X-Cost-Guard-Secret` lo tornaría inalcanzable (todo request sería 401). La firma se exige SIEMPRE que `TWILIO_AUTH_TOKEN` esté configurado. Cuando el token NO está configurado, el webhook rechaza con HTTP 401 (fail-closed) y el arranque emite `cost_guard_twilio_token_missing`: antes de cargar la credencial Twilio no está configurado para llamar al endpoint, y al cargarla la validación de firma se activa sin ningún otro cambio. El secreto por query string NO se usa (quedaría registrado en logs/proxies). El nombre del header y el algoritmo se confirmaron contra la documentación autoritativa de Twilio y contra el SDK oficial (ver "Verificación del contrato de Twilio"). El header `X-Cost-Guard-Secret` se reserva para el endpoint de reserva de n8n (`POST /reserve`), que sí puede enviar headers personalizados.

**Rationale:** es el ÚNICO punto capaz de bloquear el gasto de Twilio, porque la transcripción ocurre antes de n8n. Devolver `<Say>` + `<Hangup>` rechaza sin grabar ni transcribir.

**Alternativas consideradas:** interceptar en el nodo n8n — llega tarde, el gasto ya ocurrió; deshabilitar `transcribe` — elimina la funcionalidad en lugar de acotarla.

### D8 — Enforcement del `AI Agent` de n8n mediante endpoint de guarda

**Decisión:** modificar `n8n/workflow.json` para insertar, entre `Sellar ingreso telefonia` y `AI Agent`, un nodo HTTP Request ("Guard de costo") que llama a un endpoint del backend (p. ej. `POST /api/v1/cost-guard/reserve` con `provider="n8n_gemini"` y el caller si está disponible), y un nodo IF que rutea:
- PERMITIDO → `AI Agent` (flujo actual).
- DENEGADO → `Derivar a revision humana` (nodo terminal existente: `confianza=0.0`, `requiere_revision_humana=true`, SIN re-invocar al `AI Agent`).

Esto requiere cambios en `workflow.json`: nodos nuevos y re-cableado de conexiones (`Sellar ingreso telefonia` → guard → IF → {`AI Agent` | `Derivar a revision humana`}).

El costo unitario `n8n_gemini` es una estimación POR EJECUCIÓN que cubre el número acotado de invocaciones del agente (hasta `maxIterations=2` más la invocación del bucle de refinamiento). Se reserva una sola vez por ejecución de telefonía; la cota de invocaciones queda documentada como supuesto de la estimación.

**Rationale:** es el único punto que puede evitar el gasto de Gemini del agente antes de invocarlo. El nodo terminal de derivación ya existe y no vuelve a invocar al agente.

**Alternativas consideradas:** guardar antes de cada invocación del agente (dos nodos) — más robusto pero duplica ruteo; se documenta como mejora futura.

### D9 — Captura y registro del número de origen CRUDO (atribución)

**Decisión:** capturar `From` en el webhook pre-llamada (verificado como parámetro estándar) y, cuando esté disponible, `from.caller` del evento call-summary. El número CRUDO:
- se usa como clave del contador `caller` (rate por origen) en la tabla de la guarda;
- se emite en los eventos estructurados `cost_guard_tripped` / `cost_guard_store_unavailable`;
- NO se agrega a las tablas de negocio del incidente;
- NO se agrega al corpus de evaluación de la tesis (exclusión explícita);
- su retención queda acotada a la ventana del rate limit (el contador `caller` se purga al vencer la ventana).

**Rationale:** el humano aceptó explícitamente el registro crudo para identificar llamadores abusivos en una etapa inicial, acotado a la guarda. Se documenta como desvío deliberado y acotado del tratamiento de pseudonimización del proyecto, fuera del corpus.

**Alternativas consideradas:** hashear el caller para el contador — reduce PII pero impide la identificación directa pedida; se puede migrar a hash en una etapa posterior.

### D10 — Fail-closed con notificación ante almacén no disponible

**Decisión:** si el almacén de contadores no responde durante una evaluación, la guarda aplica `fail_closed`: DENIEGA la llamada paga y emite el evento estructurado `cost_guard_store_unavailable` (campos de D5). La degradación del flujo es la misma de D4 (backend: determinístico + `requiere_revision_humana=True`; n8n: derivar a revisión humana; Twilio: `<Say>` + `<Hangup>`). La notificación es el evento estructurado de nivel ERROR; MAY además notificarse por el webhook N8N existente (`n8n_webhook_url`) si está configurado. La política es configurable: el default RESUELTO es `fail_closed`; `fail_open` está implementado (permite la llamada sin tope cuando el almacén cae) pero NO es el default y cualquier valor distinto de `fail_open` se trata como `fail_closed`. `cost_guard_alert_enabled` controla la notificación externa adicional (webhook N8N), mientras que el evento estructurado obligatorio se emite SIEMPRE (post-verify).

**Rationale:** fail-closed garantiza que un store caído no produzca gasto descontrolado; el humano eligió explícitamente este default. La notificación evita que la indisponibilidad pase silenciosa.

**Alternativas consideradas:** fail-open — permite gastar sin tope durante una caída; rechazado por decisión humana.

## Decisiones resueltas (registro)

Las 6 preguntas abiertas de la versión previa de este documento quedan RESUELTAS por decisión humana. Valores concretos:

| # | Pregunta | Decisión resuelta |
|---|----------|-------------------|
| 1 | Magnitud y ventana del presupuesto | Bolsa GLOBAL compartida de **USD 10 por semana** para las TRES superficies. Ventana tumbling de 7 días (`cost_guard_budget_window_seconds = 604800`), configurable. Se convierte a un costo unitario en USD por superficie. |
| 2 | Puntos de enforcement | **Las TRES superficies**: Gemini backend, Gemini n8n (`AI Agent`) y transcripción Twilio. Twilio se bloquea de forma REAL con webhook de voz pre-llamada, además de detección/log/alerta. |
| 3 | Política de degradación | **Fallback a determinístico + revisión humana** (`requiere_revision_humana=True`), reutilizando el patrón de `hybrid.py:135-150`. Nunca se invoca al proveedor pago. |
| 4 | Almacén y fail-safe | **PostgreSQL** (tabla nueva + migración Alembic 007). Ante almacén no disponible: **fail-closed** (deniega) CON notificación (evento estructurado + alerta). Degrada a determinístico + revisión humana. |
| 5 | Alcance de Twilio | **Entra**. Se intercepta con un **webhook de voz pre-llamada** (TwiML) en el backend; se actualiza `n8n/twilio/twiml.xml` y la configuración del número en la consola de Twilio. |
| 6 | Estado por defecto | **HABILITADA conservadora**: presupuesto USD 10/semana, fail-closed, con override explícito por `.env`/`Settings`. Debe funcionar aunque solo falte la credencial real de Twilio (el humano la cargará y apuntará la consola/TwiML al endpoint). |

Valores de configuración concretos (nombres tentativos, se fijan en apply manteniendo los campos estables):

| Variable (`Settings`) | Default | Nota |
|----------------------|---------|------|
| `cost_guard_enabled` | `True` | habilitada por defecto |
| `cost_guard_budget_usd` | `10.0` | bolsa global semanal |
| `cost_guard_budget_window_seconds` | `604800` | 7 días |
| `cost_guard_unit_cost_backend_gemini_usd` | `0.0005` | ESTIMACIÓN configurable; a ajustar por el operador contra precios vigentes (no verificada) |
| `cost_guard_unit_cost_n8n_gemini_usd` | `0.0015` | ESTIMACIÓN por ejecución (cubre iteraciones acotadas); no verificada |
| `cost_guard_unit_cost_twilio_transcription_usd` | `0.05` | ESTIMACIÓN por llamada (`maxLength=45 s`); no verificada |
| `cost_guard_rate_limit_calls` | `30` | rate global de llamadas pagas |
| `cost_guard_rate_window_seconds` | `3600` | ventana del rate global |
| `cost_guard_caller_rate_limit_calls` | `3` | rate por número de origen |
| `cost_guard_caller_rate_window_seconds` | `3600` | ventana del rate por caller |
| `cost_guard_degradation_policy` | `deterministic_review` | vs `hard_block` |
| `cost_guard_store_failure_policy` | `fail_closed` | vs `fail_open` |
| `cost_guard_alert_enabled` | `True` | dispara la notificación externa adicional (webhook N8N) del fail-closed; el evento estructurado se emite siempre |

## Verificación del contrato de Twilio

Verificado contra documentación autoritativa de Twilio:

- **Parámetros estándar del webhook de voz** (fuente: `https://www.twilio.com/docs/voice/twiml#request-parameters`): `CallSid`, `AccountSid`, `From`, `To`, `CallStatus`, `ApiVersion`, `Direction`, `ForwardedFrom`, `CallerName`, `ParentCallSid`, `CallToken`, y datos geográficos (`FromCity`, `FromState`, `FromZip`, `FromCountry`, `ToCity`, etc.). `From`/`To` llegan en E.164 cuando es posible.
- **Respuesta del webhook de voz** (fuente: `https://www.twilio.com/docs/voice/twiml#data-formats`): se interpreta como TwiML con `Content-Type: text/xml` (también `application/xml` o `text/html`). Verbos `<Say>`, `<Hangup>`, `<Record>` confirmados.
- **`<Record transcribe="true">`** (fuente: `https://www.twilio.com/docs/voice/twiml/record`): la transcripción es una **feature paga** (se cobra si se incluye `transcribe`). Solo soporta inglés americano. Está limitada a grabaciones de duración **> 2 s y < 120 s**; fuera de ese rango Twilio escribe un warning en el debug log en lugar de transcribir. Esto refuerza que la transcripción es el gasto a acotar y que `maxLength="45"` está dentro del rango.
- **Call Summary (Voice Insights)** (fuente: `https://www.twilio.com/docs/voice/voice-insights/api/call/call-summaries-resource`): propiedades de nivel superior `account_sid`, `call_sid`, `call_state`, `call_type`, `processing_state`, `created_time`, `start_time`, `end_time`, `duration`, `connect_duration`, `from` (objeto con `caller`), `to` (objeto con `callee`), `tags`, `properties`, `trust`, etc.

NO verificado (se explicita en lugar de inventar):

- El nombre EXACTO del campo que transporta el texto de la transcripción en el evento `com.twilio.voice.insights.call-summary.complete` de Event Streams. El recurso Call Summary NO incluye el texto de la transcripción (la transcripción es un recurso separado); el workflow actual lee `$json.transcript`, pero ese campo no pudo confirmarse contra la documentación del evento de Event Streams. A confirmar en apply antes de depender de él.
- RESUELTO en apply: el header de firma de webhook de Twilio es `X-Twilio-Signature` y el algoritmo es HMAC-SHA1 (URL completa + parámetros de formulario ordenados alfabéticamente, concatenados como `nombre+valor`, codificados en base64 con el auth token como clave). Verificado contra la documentación autoritativa de Twilio (https://www.twilio.com/docs/usage/webhooks/webhooks-security) y contra la implementación de referencia del SDK oficial `twilio-python` (`twilio/request_validator.py`); el SHA-256 mencionado allí corresponde al hash del cuerpo JSON (`bodySHA256`), NO a la firma. Implementado en `App/Backend/app/cost_guard/twilio_signature.py` y validado con el vector de prueba del SDK (token `12345`, URL `https://mycompany.com/myapp.php?foo=1&bar=2`, firma `RSOYDt4T1cUTdK1PDd93/VVr8B8=`). La validación se exige SIEMPRE que `TWILIO_AUTH_TOKEN` esté configurado; si el token falta, el webhook responde 401 (fail-closed). Es el ÚNICO mecanismo de autenticación que Twilio ofrece: Programmable Voice no puede enviar headers personalizados.

## Opciones evaluadas (registro histórico)

- **Opción A — Guarda in-process con contadores en Redis:** RECOMENDADA en la versión previa; DESCARTADA por decisión humana. El backend no usa Redis hoy y agregaría un servicio a su ruta.
- **Opción B — Proxy/gateway delante de los proveedores pagos:** descartada. Infraestructura nueva, mayor superficie de fallo y latencia, difícil de testear offline.
- **Opción C — Contadores en PostgreSQL:** ELEGIDA (ver D6). Sin dependencia nueva; transaccional y durable; auditable.
- **Opción D — Kill-switch binario:** descartada como solución; puede existir como complemento de emergencia (`cost_guard_enabled=False`), no como tope.

## Risks / Trade-offs

- [Elegir mal monto/ventana y bloquear operación legítima] → monto y ventana configurables; default conservador resuelto (USD 10/semana); override por `.env`.
- [PostgreSQL caído en la ruta de la guarda] → fail-closed con evento `cost_guard_store_unavailable` y degradación a determinístico + revisión humana; nunca falla en silencio.
- [El costo unitario configurable no refleja el costo real] → es un tope de seguridad, no contabilidad exacta; se documenta como estimación y se ajusta por configuración. Los defaults de costo unitario NO están verificados contra precios vigentes.
- [La reserva por llamada no conoce la duración] → el modelo es por llamada, no por segundo; la duración está acotada por `maxLength=45`; no hay ajuste posterior.
- [El endpoint de Twilio es público y puede ser abusado] → resuelto en post-verify: el endpoint de reserva de n8n exige el secreto compartido en header `X-Cost-Guard-Secret` (nunca por query); el webhook de voz de Twilio se autentica con `X-Twilio-Signature`, exigida siempre que `TWILIO_AUTH_TOKEN` esté configurado y con 401 fail-closed si falta; rate por caller y fail-closed; el arranque advierte si faltan el secreto o el token de Twilio.
- [El evento call-summary no trae el caller o la transcripción] → el caller es opcional para el rate por origen (la bolsa global sigue aplicando); el campo de transcripción está marcado como NO verificado.
- [Acoplar tests a PostgreSQL/Gemini reales] → almacén y reloj inyectables; fake en memoria; CI/dev offline.
- [Desliz de alcance hacia el preflight estático] → Non-Goal explícito y capacidad separada (D1).
- [Registrar el caller crudo roza la privacidad] → aceptado explícitamente y acotado a logs/almacén de la guarda; fuera del corpus; retención por ventana.

## Migration Plan

1. Agregar configuración de la guarda a `Settings` con los defaults resueltos (D6, tabla de valores concretos).
2. Crear la migración Alembic `007_cost_guard_counters.py` (down_revision "006") con la tabla `costo_guarda_contador`; docstring con la nota de aprobación humana (gobernanza ALTA).
3. Implementar el modelo ORM y el adaptador PostgreSQL detrás de protocolos, con fake en memoria.
4. Implementar la función de decisión pura y la operación atómica de reserva.
5. Cablear el enforcement antes de Gemini en el backend y el manejo de `CostGuardTrippedError` en `HybridClassifier`.
6. Exponer el endpoint de guarda para n8n y el webhook de voz pre-llamada de Twilio; actualizar `n8n/twilio/twiml.xml` y `n8n/workflow.json`.
7. Registrar la postura efectiva en el lifespan y documentar variables y comportamiento operativo.
8. Rollback: `alembic downgrade 006` dropea la tabla (los contadores son efímeros, no hay datos de negocio que restaurar); revertir el commit de la guarda y de los cambios de workflow/twiml. Operativamente, deshabilitar la guarda por configuración (`cost_guard_enabled=False`) es el rollback inmediato.

**Gobernanza:** HIGH. La implementación NO debe comenzar hasta que la aprobación humana explícita del plan quede registrada (tarea 0.2). Las decisiones de diseño (sección "Decisiones resueltas") ya están registradas.

## Open Questions (diferibles, no bloqueantes)

- Ubicación exacta del módulo de la guarda dentro de `App/Backend/app/` (por ejemplo `app/cost_guard/` o `app/services/`): se decide en apply sin alterar el contrato de la spec.
- Nombres definitivos de las variables de configuración y de los eventos de log: se fijan en apply manteniendo los campos estables.
- Canal de alerta externo además del evento estructurado: hoy el evento ERROR es la señal canónica; se puede sumar el webhook N8N existente.
