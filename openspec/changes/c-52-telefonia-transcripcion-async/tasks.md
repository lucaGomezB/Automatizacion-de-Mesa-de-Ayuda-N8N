## 1. Preparación y safety net

- [ ] 1.1 Registrar el baseline de las suites afectadas: ejecutar `cd App/Backend; pytest -m "not integration" tests/test_runtime_cost_guard.py tests/test_n8n_workflow.py tests/test_openapi_sync.py` y anotar el conteo de tests en verde antes de tocar la guarda, el workflow y el OpenAPI. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change.
- [ ] 1.2 Aplicar la resolución de las Open Questions 1-3 (ya RESUELTAS en `design.md`): (a) subir el pin de `google-genai` a `>=2.20.0` en `App/Backend/requirements.txt` (el tipado de `transcription_config` llega en `2.13.0`; última `2.25.0`) y correr la suite del clasificador existente para descartar regresiones del upgrade (`cd App/Backend; pytest -m "not integration" tests/test_hybrid_classifier.py tests/test_gemini_validation.py tests/test_gemini_generation_config.py tests/test_gemini_casing_fix.py tests/test_deterministic_classifier.py`); (b) confirmar que `gemini-3.5-transcribe` está disponible; (c) usar `language_codes=["es-419"]` (es-AR NO soportado). Verificación: pin actualizado, suite del clasificador en verde, y el hallazgo registrado en `design.md`.

## 2. TwiML, settings y guarda de costo

- [ ] 2.1 RED: escribir `App/Backend/tests/test_twiml_record.py` que describa el TwiML admitido nuevo: `<Record>` mono con `recordingStatusCallback` y `action`, SIN `transcribe`, y un mensaje de cierre en el documento `action` que no prometa ticket inmediato. Verificar que falla contra el TwiML actual.
- [ ] 2.2 GREEN: editar `App/Backend/app/cost_guard/twiml.py` para cumplir el test, incluyendo `render_twiml_allowed()` con la grabación mono y callbacks y un render del documento `record-complete` con el `<Say>` alcanzable. Verificación: `pytest App/Backend/tests/test_twiml_record.py` en verde.
- [ ] 2.3 TRIANGULATE: agregar casos para la rama denegada (sigue con `<Say>` + `<Hangup/>`, sin grabar) y para la ausencia de `transcribe` en ambos documentos. Verificación: todos los casos pasan.
- [ ] 2.4 RED: agregar a `App/Backend/tests/test_runtime_cost_guard.py` (o archivo nuevo `test_cost_guard_backend_stt.py`) casos que exijan la superficie `backend_stt` en constantes y config con su costo unitario. Verificación: el test falla por superficie desconocida.
- [ ] 2.5 GREEN: agregar `PROVIDER_BACKEND_STT` a `App/Backend/app/cost_guard/constants.py` e incorporarlo a `PAID_PROVIDERS`, y agregar `cost_guard_unit_cost_backend_stt_usd` a `App/Backend/app/config/settings.py` y al mapa de `from_settings` en `App/Backend/app/cost_guard/config.py`. Verificación: los tests de 2.4 pasan.
- [ ] 2.6 TRIANGULATE: cubrir que el costo unitario de `twilio` queda re-estimado (ya no representa transcripción) y que `backend_stt` es una superficie distinta con su propio costo. Verificación: casos en verde.
- [ ] 2.7 Actualizar `App/Backend/.env.example` con `TWILIO_ACCOUNT_SID`, `GEMINI_STT_MODEL`, `BACKEND_PUBLIC_BASE_URL` y `COST_GUARD_UNIT_COST_BACKEND_STT_USD`, documentados como estimaciones. Verificación: las claves nuevas están presentes y los defaults coinciden con `settings.py`.

## 3. Modelo, migración y repositorio de ingreso

- [ ] 3.1 RED: escribir `App/Backend/tests/test_telefonia_ingreso_model.py` que instancie el modelo y exija los campos, la unicidad de `call_sid`, el uso de `EncryptedText` para `transcript_original` y la nulabilidad de `incidente_id`. Verificación: falla por modelo inexistente.
- [ ] 3.2 GREEN: crear `App/Backend/app/models/telefonia_ingreso.py` con `call_sid` UNIQUE, `recording_sid`, `caller_cifrado`, `duracion_segundos`, `transcript_original` (`EncryptedText`), `descripcion_pseudonimizada`, `ingresado_en`, `persistido_en`, `transcripcion_estado`, `incidente_id` FK nullable, `error_detalle`, `provider`, `model` y timestamps. Verificación: el test pasa.
- [ ] 3.3 TRIANGULATE: verificar que el transcript crudo almacenado es ilegible sin la clave y que se descifra al leer por el ORM, y que dos filas con el mismo `call_sid` colisionan. Verificación: casos en verde.
- [ ] 3.4 Crear `App/Backend/alembic/versions/008_telefonia_ingreso.py` y verificar `cd App/Backend; alembic upgrade head` y luego `alembic downgrade -1` sin error. Verificación: upgrade/downgrade idempotentes contra la base descartable.
- [ ] 3.5 RED: escribir `App/Backend/tests/test_telefonia_ingreso_repository.py` para `get_by_call_sid`, `create` y `link_incidente`. Verificación: falla por repositorio inexistente.
- [ ] 3.6 GREEN: crear `App/Backend/app/repositories/telefonia_ingreso_repository.py`. Verificación: el test pasa.
- [ ] 3.7 TRIANGULATE: cubrir recuperación de un ingreso existente por `CallSid` y el vínculo al incidente. Verificación: casos en verde.

## 4. Cliente STT y descarga de media

- [ ] 4.1 RED: escribir `App/Backend/tests/test_gemini_stt.py` con el cliente STT inyectado, exigiendo: modelo configurable (`gemini-3.5-transcribe`), modo verbatim con granularidad de palabra, `language_codes=["es-419"]`, `store=False`, y `transcription_config` pasado por `generation_config` (camino resuelto en 1.2, con `google-genai>=2.20.0`). Verificación: falla por cliente inexistente.
- [ ] 4.2 GREEN: crear `App/Backend/app/clients/gemini_stt.py` que reutilice `get_genai_client()` y suba el audio con `client.files.upload(...)`. Verificación: los tests pasan (sin red real; cliente simulado).
- [ ] 4.3 TRIANGULATE: cubrir el fallo de transcripción (excepción del cliente) y la respuesta vacía, sin abortar en silencio. Verificación: casos en verde.
- [ ] 4.4 RED: escribir `App/Backend/tests/test_twilio_media.py` para la descarga con HTTP Basic (`AccountSid:AuthToken`), la construcción de la URL `.wav`/`.mp3` y el error de descarga. Verificación: falla por módulo inexistente.
- [ ] 4.5 GREEN: crear `App/Backend/app/utils/twilio_media.py` con la descarga autenticada usando un cliente HTTP inyectable. Verificación: el test pasa con transporte simulado.
- [ ] 4.6 TRIANGULATE: cubrir código de estado no exitoso y timeout. Verificación: casos en verde.

## 5. Servicio de ingreso de telefonía

- [ ] 5.1 RED: escribir `App/Backend/tests/test_telefonia_service.py` que describa el orden del flujo: idempotencia por `CallSid` → sellado de `ingresado_en` → reserva `backend_stt` (estimada por duración, cap 45 s) → descarga → STT → pseudonimización → persistencia → handoff. Verificación: falla por servicio inexistente.
- [ ] 5.2 GREEN: crear `App/Backend/app/services/telefonia_service.py` con las dependencias inyectadas (guarda, cliente STT, descarga, repositorio, notificador n8n). Verificación: los tests pasan.
- [ ] 5.3 TRIANGULATE: cubrir (a) `CallSid` repetido no descarga ni reserva; (b) guarda denegada persiste ingreso con estado explícito y no descarga; (c) fallo de STT persiste estado de error sin abortar; (d) pseudonimización antes del handoff. Verificación: todos los casos en verde.
- [ ] 5.4 RED: escribir `App/Backend/tests/test_telefonia_handoff.py` que exija el payload exacto `{descripcion_pseudonimizada, call_sid, caller, ingresado_en}` con secreto compartido y sin transcript crudo. Verificación: falla.
- [ ] 5.5 GREEN: implementar el handoff en el servicio (o en `app/utils/n8n_webhook.py` como variante dedicada) con el secreto compartido. Verificación: el test pasa.
- [ ] 5.6 TRIANGULATE: verificar que el payload no expone PII cruda y que la falta de secreto no produce un handoff silencioso. Verificación: casos en verde.

## 6. Endpoints y seguridad

- [ ] 6.1 RED: escribir `App/Backend/tests/test_api_telefonia.py` que exija `POST /api/v1/telefonia/recording-status` con firma fail-closed: firma válida procesa, firma ausente/inválida devuelve 401, token no configurado devuelve 401. Verificación: falla por router inexistente.
- [ ] 6.2 GREEN: crear `App/Backend/app/routes/telefonia.py` y registrarlo en `App/Backend/app/routes/__init__.py`. Verificación: los tests pasan usando el cliente ASGI y firma calculada.
- [ ] 6.3 TRIANGULATE: cubrir que el callback no requiere `From`, que un `CallSid` repetido responde de forma idempotente, y que un fallo de descarga/STT no devuelve 500 que pierda el ingreso. Verificación: casos en verde.
- [ ] 6.4 Crear los schemas de request/response en `App/Backend/app/schemas/telefonia.py` y verificar que `test_api_telefonia.py` los consume. Verificación: sin `AttributeError` ni campos extra.
- [ ] 6.5 Verificar la sincronización del contrato: regenerar `docs/openapi.json` y ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v`. Verificación: el test de sincronización pasa.

## 7. Cableado de N8N

- [ ] 7.1 RED: extender `App/Backend/tests/test_n8n_workflow.py` para exigir: (a) no existe `twilioTrigger` de resumen post-llamada; (b) existe un `webhook` POST de telefonía autenticado; (c) no hay parsing de `call-summary.complete`/CloudEvent; (d) el POST de persistencia envía `origen_message_id` con el `CallSid`. Verificación: los tests fallan contra el workflow actual.
- [ ] 7.2 GREEN: editar `n8n/workflow.json` reemplazando `Llamada telefonica` por el nodo `webhook` y cableando el handoff. Verificación: los tests de 7.1 pasan.
- [ ] 7.3 RED: agregar tests que exijan que `Sellar ingreso telefonia` sea passthrough del `ingresado_en` (sin `new Date()`), que el `Guard de costo` resuelva `caller` desde `$json` (sin referencia a `$('Sellar ingreso telefonia')`) y que el `AI Agent` reciba la descripción pseudonimizada, no un transcript crudo. Verificación: fallan contra el workflow actual.
- [ ] 7.4 GREEN: ajustar `n8n/workflow.json` (passthrough del sello y `caller` del handoff). Verificación: los tests de 7.3 pasan.
- [ ] 7.5 TRIANGULATE: prueba de no regresión de C-46 (el validador y el terminal siguen referenciando `$('Sellar ingreso telefonia').first()` y emitiendo el WARN de sello ausente) y de C-47 (`Restaurar item telefonia` sigue entre `Guard de costo` y `Guard permite?`). Verificación: casos en verde.
- [ ] 7.6 Actualizar `docs/n8n-workflow-guide.md` (conteo de nodos, conteo de pruebas estructurales, flujo telefónico asincrónico) y ejecutar `cd App/Backend; pytest tests/test_n8n_workflow.py -v`. Verificación: la guía y la suite coinciden en conteos.

## 8. Documentación y verificación final

- [ ] 8.1 Actualizar el caveat de telefonía del contrato de medición en la documentación afectada y verificar que `App/Backend/tests/` cubre la semántica de latencia con STT. Verificación: los tests de timing en verde.
- [ ] 8.2 Ejecutar la suite backend offline: `cd App/Backend; pytest -m "not integration"`. Verificación: sin regresiones respecto del baseline de 1.1.
- [ ] 8.3 Ejecutar lint: `cd App/Backend; ruff check .`. Verificación: sin errores E nuevos.
- [ ] 8.4 Ejecutar la verificación en vivo documentada: una llamada de prueba que produzca grabación, transcriba, pseudonimice, cree el incidente y registre la latencia. Verificación: el incidente existe con descripción pseudonimizada no vacía, `origen_message_id = CallSid` e `ingresado_en` anterior a la STT; documentar el resultado.
- [ ] 8.5 Ejecutar `openspec validate --strict --changes c-52-telefonia-transcripcion-async`. Verificación: validación estricta sin errores.