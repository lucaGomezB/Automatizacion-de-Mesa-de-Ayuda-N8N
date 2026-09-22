## Why

El canal de telefonía clasifica hoy sobre una descripción VACÍA. El disparador `com.twilio.voice.insights.call-summary.complete` no expone la transcripción en su payload y `<Record transcribe="true">` usa el reconocimiento de voz de Twilio, limitado a inglés estadounidense. Además de la pérdida funcional, existe una fuga latente de PII: el prompt del `AI Agent` de n8n interpola `$json.transcript` crudo hacia Gemini antes de cualquier pseudonimización. Este change reemplaza la transcripción de Twilio por speech-to-text ejecutado EN EL BACKEND con Google Gemini, de modo que el canal de telefonía vuelva a clasificar y que el texto crudo nunca cruce el borde de n8n. Absorbe el change cancelado `c-51-twilio-payload-wiring` (no se abre; no existe parsing de CloudEvent en el nuevo flujo).

## What Changes

- **BREAKING** Reemplaza el disparador `Llamada telefonica` (`twilioTrigger`, evento `call-summary.complete`) por un nodo `webhook` que recibe el texto YA pseudonimizado desde el backend. El canal de telefonía deja de depender de la transcripción de Twilio.
- **Nuevo webhook de estado de grabación** `POST /api/v1/telefonia/recording-status`: verifica `X-Twilio-Signature` fail-closed, sella `ingresado_en` en la recepción del backend, aplica idempotencia por `CallSid`, reserva la superficie paga `backend_stt` ANTES de descargar/transcribir, descarga la grabación (`RecordingUrl`, Basic auth `AccountSid:AuthToken`), transcribe con Gemini (verbatim, `es-419`) y pseudonimiza INMEDIATAMENTE.
- **BREAKING** El backend pasa a ser el dueño de la STT y de la descarga de la grabación de Twilio.
- **Nueva tabla de ingreso** `telefonia_ingreso` con doble representación del transcript: `transcript_original` cifrado (Fernet/`EncryptedText`) y `descripcion_pseudonimizada` en claro, más metadatos de trazabilidad e `incidente_id` nullable. Migración Alembic `008`.
- El `<Record>` conserva la grabación pero pasa a MONO (ya no se usa Twilio Batch Transcription), agrega `recordingStatusCallback` + `action`, y ELIMINA `transcribe="true"`. Se corrige además el `<Say>` post-grabación, hoy inalcanzable.
- **BREAKING** `ingresado_en` de telefonía se sella en el BACKEND (recepción del callback), NO en el borde de n8n. La latencia end-to-end ahora INCLUYE la STT + pseudonimización + handoff.
- **Nuevo webhook de handoff** backend → n8n con `{descripcion_pseudonimizada, call_sid, caller, ingresado_en}` autenticado por secreto compartido. n8n recibe solo texto pseudonimizado.
- **Nueva superficie paga** `backend_stt` en la guarda de costo, reservada al recibir el callback y estimada por duración (cap 45 s). Se re-estima el costo unitario de `twilio`, que hoy representa una transcripción que ya no se usa.
- Reutiliza el índice único existente de `origen_message_id` para la idempotencia del alta, con `origen_message_id = CallSid`.
- Actualiza `docs/openapi.json`, `docs/n8n-workflow-guide.md`, `.env.example` y el caveat de telefonía del contrato de medición.

## Capabilities

### New Capabilities

- `telefonia-stt-intake`: ingesta asíncrona de telefonía propiedad del backend — webhooks de Twilio (voz pre-llamada y estado de grabación), verificación de firma, idempotencia por `CallSid`, descarga autenticada de la grabación, transcripción Gemini verbatim, pseudonimización inmediata, persistencia cifrada del ingreso, y handoff autenticado a n8n.

### Modified Capabilities

- `n8n-workflow`: el trigger de Twilio se reemplaza por un webhook que recibe texto pseudonimizado; `Sellar ingreso telefonia` pasa a propagar el `ingresado_en` sellado por el backend; los nodos `Guard de costo`, `Restaurar item telefonia`, `Guard permite?`, `AI Agent`, validador y normalizador se conservan.
- `runtime-cost-guard`: nueva superficie paga `backend_stt` reservada en el callback; re-estimación del costo unitario de `twilio`.
- `e2e-timing-instrumentation`: el ingreso de telefonía se sella en el callback del backend y la latencia incluye la STT; se actualiza el caveat de telefonía.
- `data-pseudonymization`: se refuerza el borde de PII — el transcript crudo nunca transita n8n y se pseudonimiza antes del handoff.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `App/Backend/app/routes/telefonia.py` | New | Endpoints `recording-status` y handoff a n8n |
| `App/Backend/app/services/telefonia_service.py` | New | Orquestación del flujo de ingreso (idempotencia, reserva, STT, persistencia, handoff) |
| `App/Backend/app/clients/gemini_stt.py` | New | Cliente STT dedicado (Gemini, verbo verbatim) |
| `App/Backend/app/utils/twilio_media.py` | New | Descarga autenticada de la grabación (Basic auth) |
| `App/Backend/app/models/telefonia_ingreso.py` | New | Tabla de ingreso con transcript cifrado + pseudonimizado |
| `App/Backend/app/repositories/telefonia_ingreso_repository.py` | New | Acceso a datos del ingreso |
| `App/Backend/app/schemas/telefonia.py` | New | Contratos de request/response del canal |
| `App/Backend/alembic/versions/008_*.py` | New | Migración de la tabla de ingreso |
| `App/Backend/app/cost_guard/twiml.py` | Modified | `<Record>` mono + callbacks, sin `transcribe`; `<Say>` post-grabación corregido |
| `App/Backend/app/cost_guard/constants.py` | Modified | Nueva superficie `backend_stt` |
| `App/Backend/app/cost_guard/config.py` | Modified | Costo unitario de `backend_stt` |
| `App/Backend/app/config/settings.py`, `.env.example` | Modified | `twilio_account_sid`, `gemini_stt_model`, `backend_public_base_url`, costos unitarios |
| `App/Backend/app/routes/__init__.py` | Modified | Registrar el router de telefonía |
| `n8n/workflow.json` | Modified | Trigger webhook, passthrough del sello, sin parsing de CloudEvent |
| `docs/openapi.json`, `docs/n8n-workflow-guide.md` | Modified | Especificación y guía sincronizadas |
| `openspec/specs/*` | Modified | Deltas de las cuatro capacidades |
| Gemini | New dependency usage | Modelo dedicado de transcripción (`gemini-3.5-transcribe`, Stable) vía Interactions API; upgrade de `google-genai` a `>=2.20.0` |
| PostgreSQL | Migration | Nueva tabla `telefonia_ingreso` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `google-genai==2.8.0` no tipa `transcription_config` | Resuelto | Upgrade del pin a `>=2.20.0` (última `2.25.0`); el tipado llega en `2.13.0`. Correr la suite del clasificador existente para descartar regresiones |
| Precio de `gemini-3.5-transcribe` distinto al estimado | Resuelto | Modelo Stable; ~USD 0.005/min (≈ USD 0.0038 por 45 s), por debajo de Whisper (USD 0.006/min); costo unitario configurable |
| `language_codes=["es-AR"]` no soportado | Resuelto | Se usa `es-419` (español latinoamericano, cubre Argentina); fallback a auto-detect `[]` o `es-MX`; validar calidad en corpus rioplatense |
| Cargo duplicado por reintentos del callback de Twilio | Med | Idempotencia por `CallSid` ANTES de la reserva y restricción única en la tabla de ingreso |
| Fuga de PII hacia n8n | Low | El transcript crudo nunca cruza el borde; n8n recibe solo la versión pseudonimizada con secreto compartido |
| Regresión de C-46/C-47 en la rama de telefonía | Med | Los nodos de sellado, guarda y restauración se conservan; pruebas estructurales de no regresión |
| STT falla o la guarda deniega | Med | El ingreso se conserva con `transcripcion_estado` para reintento/revisión (open question sobre alta placeholder) |

## Rollback Plan

Revertir el commit elimina los endpoints, el cliente STT, el modelo y la migración `008`, restaura el `twilioTrigger` y el `<Record transcribe="true">`, y revierte los costos unitarios. La migración `008` se revierte con `alembic downgrade -1`; no hay backfill de datos. Reimportar `n8n/workflow.json` restaura el flujo previo en runtime. Los incidentes ya creados no se tocan.

## Success Criteria

- [ ] El canal de telefonía clasifica sobre una descripción NO vacía y pseudonimizada.
- [ ] El transcript crudo nunca abandona el backend; n8n recibe solo texto pseudonimizado.
- [ ] `ingresado_en` de telefonía se sella en el callback del backend y la latencia incluye la STT.
- [ ] La reserva de `backend_stt` ocurre ANTES de descargar y transcribir; la idempotencia por `CallSid` evita cargos duplicados.
- [ ] `origen_message_id = CallSid` reutiliza el índice único para la idempotencia del alta.
- [ ] `openspec validate --strict --changes c-52-telefonia-transcripcion-async` pasa.