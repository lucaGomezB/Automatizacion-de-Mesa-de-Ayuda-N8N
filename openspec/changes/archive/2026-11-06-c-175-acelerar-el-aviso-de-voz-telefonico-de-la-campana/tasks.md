# Tasks: Acelerar el aviso de voz telefónico de la campaña

> Strict TDD activo. Cada grupo de implementación respeta Safety Net → RED → GREEN →
> TRIANGULATE → REFACTOR. No se escribe código de producción antes de su test.

## 1. Tasa de locución en el TwiML (Strict TDD)

- [x] 1.1 Safety Net: ejecutar `cd App/Backend; pytest tests/test_twiml_record.py -q` y registrar la línea base (tests de TwiML y PRIV-003 en verde)
- [x] 1.2 RED: agregar en `tests/test_twiml_record.py` un test que exija que `render_twiml_allowed(rate="125%")` envuelva el contenido del `<Say>` en `<prosody rate="125%">` sin cambiar el texto; verificar que falla
- [x] 1.3 GREEN: agregar el parámetro opcional `rate` a `render_twiml_allowed` en `app/cost_guard/twiml.py` y envolver el `<Say>` solo cuando hay tasa; verificar que `pytest tests/test_twiml_record.py -q` pasa
- [x] 1.4 TRIANGULATE: agregar tests de (a) salida byte-idéntica sin tasa, (b) clamp fuera de rango (500%→200%, 5%→20%) y (c) formato inválido ignorado sin inyección; verificar que pasan
- [x] 1.5 REFACTOR: centralizar la validación/clamp en un helper privado de `twiml.py`; verificar que los tests siguen en verde

## 2. Tasa en el webhook de voz (Strict TDD)

- [x] 2.1 Safety Net: ejecutar `cd App/Backend; pytest tests/test_runtime_cost_guard.py -q` y registrar la línea base
- [x] 2.2 RED: agregar un test que exija que el webhook de voz lea `tts_rate` y devuelva el `<Say>` envuelto en `<prosody>`; verificar que falla
- [x] 2.3 GREEN: agregar el `Form(alias="tts_rate")` a `twilio_voice_webhook` en `app/routes/cost_guard.py` y pasarlo a `render_twiml_allowed`; verificar que el test pasa
- [x] 2.4 TRIANGULATE: agregar un test que confirme que, sin `tts_rate`, la respuesta del webhook no cambia; verificar que pasa

## 3. Softphone (Strict TDD)

- [x] 3.1 Safety Net: ejecutar `cd scripts/voip_softphone; python -m pytest test_softphone_html.py -q` y registrar la línea base
- [x] 3.2 RED: actualizar `test_page_sends_corpus_case_id_only_when_selected` y agregar un test que exija que la rama con caso envíe `tts_rate` y que la rama sin caso NO lo envíe; verificar que fallan
- [x] 3.3 GREEN: agregar `tts_rate` (constante `TTS_RATE = "125%"`) al `device.connect({ params: ... })` de la rama con caso en `softphone.html`; verificar que los tests pasan
- [x] 3.4 Verificar que la rama sin caso conserva `device.connect()` y que los tests de ciclo de vida (`test_page_wires_webrtc_call_lifecycle`) siguen en verde

## 4. Sincronización documental

- [x] 4.1 Regenerar `docs/openapi.json` con `cd App/Backend; python scripts/export_openapi.py` y verificar que `pytest tests/test_openapi_sync.py -q` pasa
- [x] 4.2 Actualizar el docstring del webhook para mencionar `tts_rate` y verificar que `cd App/Backend; ruff check .` queda limpio

## 5. Verificación

- [x] 5.1 Ejecutar la suite backend aplicable (al menos `cd App/Backend; pytest -m "not integration"`) y verificar verde (en el apply final se ejecuto el conjunto dirigido de cost-guard/TwiML/OpenAPI: 140 passed, por alcance del orquestador)
- [x] 5.2 Ejecutar la suite del softphone (`cd scripts/voip_softphone; python -m pytest -q`) y verificar verde
- [x] 5.3 Ejecutar `openspec validate "c-175-acelerar-el-aviso-de-voz-telefonico-de-la-campana" --strict` y verificar PASS
- [x] 5.4 Confirmar por inspección que el texto del aviso y los atributos/callbacks del `<Record>` no cambiaron (PRIV-003 intacta)
