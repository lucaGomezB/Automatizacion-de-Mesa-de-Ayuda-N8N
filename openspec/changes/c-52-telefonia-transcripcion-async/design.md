## Context

Ver `proposal.md — Why`. Restricciones verificadas que moldean el enfoque:

- **Trigger actual sin transcripción**: el nodo `Llamada telefonica` es un `n8n-nodes-base.twilioTrigger` suscrito a `com.twilio.voice.insights.call-summary.complete`. Ese payload no expone un campo de transcripción; por eso el `AI Agent` interpola `$json.transcript || $json.body || $json.descripcion || $json.text || ''` y clasifica sobre cadena vacía (limitación heredada de C-45, documentada en el design de C-47).
- **Fuga latente de PII**: el prompt del `AI Agent` (`n8n/workflow.json:196-210`) interpola el transcript HACIA Gemini antes de cualquier pseudonimización. Aunque hoy el transcript llega vacío, la ruta es una fuga en cuanto el campo se pueble.
- **`<Record transcribe="true">`** (`app/cost_guard/twiml.py:19`) usa el reconocimiento de voz de Twilio, limitado a inglés estadounidense. El `<Say>` inmediatamente posterior a `<Record>` es INALCANZABLE: con `action` ausente, Twilio redirige a la URL del webhook original y no reproduce el segundo `<Say>`.
- **Cliente Gemini compartido**: `app/classifiers/gemini_classifier.py` crea un `genai.Client` perezoso a nivel de proceso (`get_genai_client()`) y lo cierra en el lifespan (`close_genai_client()`). Ese es el patrón a reutilizar. `thinking_budget=0` es obligatorio para Gemini 2.5 Flash; el modelo de transcripción es dedicado y puede no aplicar.
- **Cifrado at-rest**: `app/utils/encryption.py` expone `EncryptedText` (TypeDecorator de SQLAlchemy sobre Fernet, portable PostgreSQL/SQLite) con la clave de `settings.pseudonymization_encryption_key`.
- **Pseudonimización**: `app/utils/pseudonymizer.py` expone `pseudonymize(text, internal_domains) -> PseudonymizationResult`, determinística y sin efectos secundarios.
- **Guarda de costo**: superficies actuales `backend_gemini`, `n8n_gemini`, `twilio` (`app/cost_guard/constants.py`); el costo de `twilio` representa hoy una transcripción que este change elimina. `CostGuardService.reserve(provider, caller)` evalúa la bolsa global y el rate por origen.
- **Idempotencia del alta**: `incidente.origen_message_id` tiene índice único (`ix_incidente_origen_message_id`, migración 005) y se resuelve antes de clasificar (C-33).
- **Firma de Twilio**: `app/cost_guard/twilio_signature.py` implementa HMAC-SHA1 sobre la URL + parámetros ordenados; el webhook de voz ya la exige fail-closed.
- **Migraciones**: la última es `007_cost_guard_counters.py`; la nueva es `008`.

### Hechos técnicos verificados (a citar tal cual)

- **Transcripción dedicada de Gemini**: `client.interactions.create(model="gemini-3.5-transcribe", input=[{"type":"audio","uri":<Files API uri>,"mime_type":<...>}], generation_config={...}, store=False)`. Endpoint `POST https://generativelanguage.googleapis.com/v1beta/interactions`.
- **Config verbatim**: `generation_config.transcription_config.mode = {"type":"verbatim","timestamp_granularities":["word"]}`; `language_codes` (usar `["es-419"]` — español latinoamericano, cubre Argentina; `es-AR` NO está soportado — o `[]` para auto-detect); `diarization_mode` opcional. Docs: `https://ai.google.dev/gemini-api/docs/transcribe` y `/docs/generate-content/transcribe`.
- **Subida de audio**: `client.files.upload(file=...)` y luego `audio_file.uri` + `mime_type`.
- **SDK (RESUELTO)**: `google-genai==2.8.0` no tipa `transcription_config`; el tipado se agregó en `2.13.0` (`language_codes` en `2.15.0`, el enum de `mode` en `2.19/2.20`). Se actualiza el pin a `google-genai>=2.20.0` (última `2.25.0`) y se pasa como `generation_config.transcription_config` (NO top-level). El modelo dedicado `gemini-3.5-transcribe` está en estado Stable.
- **Twilio**: `<Record>` produce WAV MONO. Los form params de `recordingStatusCallback` son `AccountSid`, `CallSid`, `RecordingSid`, `RecordingUrl`, `RecordingStatus`, `RecordingDuration`, `RecordingChannels`, `RecordingSource` — NO incluye `From`. `RecordingUrl` se descarga con HTTP Basic (`AccountSid:AuthToken`) y admite `.wav` o `.mp3`. El callback de grabación es la señal confiable de "grabación disponible".
- **Twilio Batch Transcription** queda descartado: requiere grabaciones dual-channel y un flag de cuenta V3.

## Goals / Non-Goals

**Goals:**

- Restaurar la clasificación del canal de telefonía con texto real, pseudonimizado y no vacío.
- Que el backend sea dueño de la descarga y la STT, y que el transcript crudo nunca cruce el borde hacia n8n.
- Sellar `ingresado_en` en el callback del backend para que la latencia incluya la STT.
- Acotar el gasto de la nueva superficie paga antes de descargar/transcribir.
- Reutilizar los contratos existentes (índice único de `origen_message_id`, guarda, trigger webhook) sin regresar C-46/C-47.
- Corregir el `<Say>` inalcanzable y eliminar `transcribe="true"`.

**Non-Goals:**

- No usar Twilio Batch Transcription ni Event Streams para obtener la transcripción.
- No agregar diarización, resumen hablado ni análisis de sentimiento del audio.
- No cambiar los cinco sectores canónicos ni el umbral 0.70.
- No reentrenar ni cambiar el clasificador híbrido existente.
- No persistencer audio crudo como parte de este change (se decide en Open Question 4).
- No implementar en este phase (propose only).

## Decisions

### D1: Absorber `c-51` y eliminar todo parsing de CloudEvent

El flujo nuevo no parsea `call-summary.complete` ni CloudEvents. El ingreso llega por webhooks de Twilio al backend (voz pre-llamada y estado de grabación) y por un handoff backend → n8n. Se descarta `c-51-twilio-payload-wiring`: no se abre y su alcance queda cubierto por el contrato del handoff.

### D2: El backend es dueño de la descarga y de la STT

El backend descarga la grabación (`RecordingUrl`, Basic auth) y transcribe con el motor dedicado de Gemini. Se descarta la transcripción embebida de Twilio (`transcribe="true"`, inglés EE.UU.) y Twilio Batch Transcription (dual-channel + flag V3). Alternativa considerada: un proveedor STT distinto (Whisper, Speech-to-Text de GCP) — descartada por coherencia con la credencial Gemini ya presente, por el modelo dedicado de transcripción y por evitar una credencial nueva.

### D3: Tabla de ingreso con doble representación y unicidad por `CallSid`

Nueva tabla `telefonia_ingreso` (migración 008) con: `call_sid` UNIQUE, `recording_sid`, `caller_cifrado`, `duracion_segundos`, `transcript_original` (`EncryptedText`), `descripcion_pseudonimizada` (Text), `ingresado_en`, `persistido_en`, `transcripcion_estado`, `incidente_id` FK nullable, `error_detalle`, `provider`, `model`, `created_at`/`updated_at`. Se elige tabla dedicada (y no reutilizar `incidente`) porque el ingreso puede existir sin incidente (fallo, denegación, reintento) y porque el transcript crudo no debe vivir en la tabla operativa expuesta por la API. Alternativa considerada: persistir solo en `incidente` — descartada: obliga a crear un incidente placeholder ante cada fallo y mezcla PII cruda con la tabla operativa.

### D4: `ingresado_en` se sella en el callback del backend

El instante de ingreso se fija al recibir `POST /api/v1/telefonia/recording-status`, antes de descargar/transcribir. n8n lo propaga como passthrough. Alternativa considerada: sellarlo en el borde de n8n (modelo C-39/C-46) — descartada: excluiría la STT y la descarga de la latencia, que es justamente el trabajo dominante del canal.

### D5: TwiML — grabación mono con callbacks, sin transcripción

`app/cost_guard/twiml.py` pasa a: `<Record maxLength="45" finishOnKey="#" playBeep="true" recordingStatusCallback="<BACKEND_PUBLIC_BASE_URL>/api/v1/telefonia/recording-status" action="<BACKEND_PUBLIC_BASE_URL>/api/v1/telefonia/record-complete" />`. Se elimina `transcribe="true"`. Mono es suficiente porque ya no se usa Batch Transcription. El segundo `<Say>` se reubica en el documento `action` (`/record-complete`) para que sea alcanzable, con un texto que NO prometa la creación inmediata del ticket. Alternativa considerada: mantener el `<Say>` tras `<Record>` en el mismo documento — descartada: con `action` declarado, Twilio redirige a la acción tras la grabación y el `<Say>` inline no se reproduce.

### D6: Guarda de costo — superficie `backend_stt` reservada en el callback

Se agrega `PROVIDER_BACKEND_STT = "backend_stt"` a `constants.py`, su costo unitario a `config.py`/`settings.py`/`.env.example`, y la reserva en el callback ANTES de la descarga. La reserva se estima con la duración informada por Twilio, acotada a un cap de 45 s (consistente con `maxLength`). El costo unitario de `twilio` se re-estima porque ya no representa transcripción. Alternativa considerada: reservar en el webhook de voz una estimación fija de STT — descartada: la duración se desconoce al inicio y sub/sobre-estimaría.

### D7: Handoff autenticado y webhook n8n

El backend invoca un webhook de n8n con `{descripcion_pseudonimizada, call_sid, caller, ingresado_en}` y secreto compartido. En `n8n/workflow.json`, `Llamada telefonica` (`twilioTrigger`) se reemplaza por un nodo `webhook` POST. `Sellar ingreso telefonia` pasa a passthrough del `ingresado_en` del handoff. `Guard de costo`, `Restaurar item telefonia`, `Guard permite?`, `AI Agent`, `Se verifica lo que trajo la IA`, `Derivar a revision humana` y el normalizador SE CONSERVAN. `origen_message_id = CallSid` reutiliza el índice único existente. Alternativa considerada: que n8n haga el polling del estado pendiente — descartada: agrega complejidad y acoplamiento; el webhook es el mecanismo natural.

### D8: Idempotencia en dos capas

(1) La tabla de ingreso impone UNIQUE sobre `call_sid`; un callback repetido no descarga, no transcribe ni reserva de nuevo. (2) El alta reutiliza el índice único de `incidente.origen_message_id` con el `CallSid`; un handoff repetido devuelve el incidente existente. La verificación del ingreso ocurre ANTES de la reserva paga. Alternativa considerada: idempotencia solo en el alta — descartada: el costo de STT se pagaría igual en callbacks repetidos.

### D9: Frontera de PII — pseudonimizar antes del handoff

El backend pseudonimiza con `pseudonymize()` inmediatamente después de la STT y entrega SOLO la versión pseudonimizada. Esto cierra la fuga latente del prompt del `AI Agent`. El transcript crudo queda cifrado en la tabla de ingreso, accesible solo para auditoría fuera de los contratos REST normales. Alternativa considerada: pseudonimizar en n8n — descartada: viola la frontera de PII (el crudo cruzaría el borde) y pierde el cifrado at-rest centralizado.

### D10: Cliente STT nuevo que reutiliza el patrón de cliente compartido

`app/clients/gemini_stt.py` usa `get_genai_client()` (proceso-wide, cierre en lifespan). El modelo se configura por `settings.gemini_stt_model` (default `gemini-3.5-transcribe`). Se aísla la llamada en un cliente propio para no acoplar el clasificador híbrido a la transcripción y facilitar inyección en tests.

### D11: Manejo de fallos sin pérdida silenciosa

Ante denegación de la guarda, fallo de descarga o fallo de STT, se persiste el ingreso con `transcripcion_estado` y `error_detalle`, y NO se aborta en silencio. La decisión de crear un incidente placeholder con revisión humana o de retener para reintento se difiere (Open Question 5). Lo que NO se difiere es la obligación de dejar rastro observable.

### D12: Semántica temporal

La latencia de telefonía pasa a incluir la STT. Se actualiza el caveat en `e2e-timing-instrumentation` y la redacción de N8N-TIMING-001/003. C-46 (recuperación `.first()` del sello) y C-47 (restauración del item tras la guarda) no deben regresar.

### D13: Nuevos módulos backend

`app/models/telefonia_ingreso.py`, `app/repositories/telefonia_ingreso_repository.py`, `app/schemas/telefonia.py`, `app/clients/gemini_stt.py`, `app/services/telefonia_service.py`, `app/routes/telefonia.py`, `app/utils/twilio_media.py`, alembic `008`. Registro del router en `app/routes/__init__.py`. Ediciones en `cost_guard/twiml.py`, `cost_guard/constants.py`, `cost_guard/config.py`, `config/settings.py`, `.env.example`.

## Risks / Trade-offs

- **[Upgrade del SDK]** subir `google-genai` de `2.8.0` a `>=2.20.0` (última `2.25.0`) es ~17 versiones → Mitigación: bump del pin en `requirements.txt` + correr la suite del clasificador existente (`gemini_classifier`) para descartar regresiones; el tipado de `transcription_config` llega en `2.13.0`.
- **[Costo]** `gemini-3.5-transcribe` cuesta ~USD 0.005/min (input USD 2/1M a 25 tok/s + output USD 12/1M) ≈ USD 0.0038 por llamada de 45 s; ~2.5x el audio de `2.5-flash` pero AÚN por debajo de Whisper (USD 0.006/min) → Mitigación: `cost_guard_unit_cost_backend_stt_usd` configurable; es estimación, no contabilidad exacta.
- **[Calidad/idioma]** `es-AR` NO está soportado → se usa `es-419` (español latinoamericano, cubre Argentina); fallback a `[]` (auto-detect) o `es-MX` → Mitigación: validar calidad sobre corpus rioplatense en la verificación en vivo.
- **[Fidelidad]** el modo `verbatim` del modelo dedicado evita el riesgo de resumen/alucinación del `generate_content` prompt-based → es la razón de elegir el modelo dedicado.
- **[Cargo duplicado]** reintentos del callback → Mitigación: idempotencia por `CallSid` antes de la reserva + UNIQUE en persistencia.
- **[PII en repsoso]** transcript crudo cifrado → Mitigación: `EncryptedText` + frontera de handoff; retención del audio se decide en Open Question 4.
- **[Regresión de C-46/C-47]** editar el mismo grafo → Mitigación: passthrough del sello sin tocar la recuperación `.first()` ni la restauración de la guarda; pruebas estructurales de no regresión.
- **[Verificación estructural, no runtime]** no hay harness N8N en CI → Mitigación: pruebas estructurales + verificación en vivo documentada como obligatoria.

## Migration Plan

1. Alembic `008` crea `telefonia_ingreso`; rollback con `alembic downgrade -1`.
2. Implementar módulos backend en orden de dependencia (utils → clients → models → repositories → schemas → services → routes) con TDD.
3. Editar `twiml.py`, guarda y settings/`.env.example`.
4. Regenerar `docs/openapi.json` y actualizar `docs/n8n-workflow-guide.md`.
5. Editar `n8n/workflow.json` (webhook, passthrough, caller del handoff) y reimportar en N8N.
6. Verificación en vivo con una llamada de prueba; documentar el resultado.
7. Rollback: revertir el commit + `alembic downgrade -1` + reimportar el workflow previo. No hay backfill.

## Open Questions

1. **RESUELTO — Tipado de `transcription_config`**: se actualiza `google-genai` a `>=2.20.0` (última `2.25.0`; el tipado llega en `2.13.0`). Se pasa como `generation_config.transcription_config` (NO top-level). Requiere bump del pin + correr la suite del clasificador existente para descartar regresiones.
2. **RESUELTO — Modelo y precio**: `gemini-3.5-transcribe` está en estado Stable y es el modelo dedicado de STT. Precio ~USD 0.005/min (input USD 2/1M a 25 tok/s + output USD 12/1M) ≈ USD 0.0038 por 45 s; ~2.5x el audio de `2.5-flash` pero por debajo de Whisper (USD 0.006/min). Se mantiene `gemini-3.5-transcribe` por fidelidad (`verbatim`) + features (timestamps, diarización), aun siendo más caro que el `generate_content` prompt-based.
3. **RESUELTO — Idioma**: `es-AR` NO está soportado; se usa `language_codes=["es-419"]` (español latinoamericano, cubre Argentina). Fallback a `[]` (auto-detect) o `es-MX`. Validar calidad sobre corpus rioplatense en la verificación en vivo.
4. **Retención del audio y del transcript crudo**: decidir si el audio se descarta tras transcribir y cuál es la retención del transcript crudo cifrado; alinear con la retención de grabaciones de Twilio.
5. **Comportamiento ante fallo de STT o denegación de la guarda**: decidir entre crear un incidente con descripción placeholder + revisión humana, o retener el ingreso para reintento sin crear incidente.
6. **Suscripción a Event Streams `call-summary`**: decidir si se elimina por completo la suscripción al evento de resumen de Twilio, ya que el flujo nuevo no la usa.
7. **Redacción del `<Say>` de voz**: definir el texto de confirmación/cierre que acompaña la llamada una vez que la creación del incidente pasa a ser asíncrona (no prometer un ticket inmediato).