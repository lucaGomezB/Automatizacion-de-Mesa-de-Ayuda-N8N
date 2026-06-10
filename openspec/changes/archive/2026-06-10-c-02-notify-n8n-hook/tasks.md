# Tasks — c-02-notify-n8n-hook

> Strict TDD: cada cambio de producción va precedido de un test que falla (RED), seguido del mínimo código que lo hace pasar (GREEN), luego triangulación y refactor. No escribir producción sin un test en rojo.

## 1. Safety net y preparación

- [x] 1.1 Correr la suite existente del backend para capturar baseline (`cd Gestion_Incidentes && pytest -q`). Anotar "N tests passing". Si algo falla antes de tocar nada, reportar como fallo preexistente y detenerse.
- [x] 1.2 Verificar qué librerías de mock HTTP hay disponibles para el test de integración (`pytest-httpx`, `respx`) inspeccionando `Gestion_Incidentes/pyproject.toml` / entorno. Decidir: usar la disponible, o fallback a app Starlette/FastAPI mínima vía `httpx.ASGITransport`. Registrar la decisión.
- [x] 1.3 Crear el archivo de test `Gestion_Incidentes/tests/test_incidente_notify_n8n.py` con los imports base (`pytest`, `asyncio`, `unittest.mock.AsyncMock`, `ClasificacionResult`, helpers para sembrar catálogos `estado="nuevo"` y un `sector`). Revisar `tests/conftest.py` para reusar la fixture `db_session`.

## 2. Test unitario — la llamada a notify_n8n (RED → GREEN → TRIANGULATE)

- [x] 2.1 RED: escribir `test_create_and_classify_invokes_notify_n8n_with_correct_args` — parchear `app.services.incidente_service.notify_n8n` con `AsyncMock`, inyectar un classifier mock (parámetro `classifier=` del `IncidenteService`) que devuelva un `ClasificacionResult` conocido, sembrar catálogos en `db_session`, llamar `create_and_classify(payload)`, drenar el loop con `await asyncio.sleep(0)`, y asertar que `notify_n8n` fue llamado exactamente una vez con `(incidente.id, result_esperado)`. Ejecutar → debe FALLAR (aún no se invoca notify_n8n). Marca el símbolo correcto: parchear en `incidente_service`, no en `app.utils.n8n_webhook`.
- [x] 2.2 GREEN: en `app/services/incidente_service.py`, importar `asyncio` y `from app.utils.n8n_webhook import notify_n8n`; al final de `_apply_classification()` (tras `logger.info("incidente_classified", ...)`) agregar `asyncio.create_task(notify_n8n(incidente.id, result))`. Ejecutar el test → debe PASAR.
- [x] 2.3 TRIANGULATE: agregar `test_notify_n8n_receives_actual_classification_result` con un `ClasificacionResult` distinto (p. ej. `etapa="fallback"`, `confianza=0.0`, `requiere_revision_humana=True`) y asertar que ese `result` exacto se pasó a `notify_n8n` (prueba que no está hardcodeado). Ejecutar → PASA.
- [x] 2.4 TRIANGULATE (borde): agregar `test_notify_n8n_called_even_when_webhook_url_empty` — con `n8n_webhook_url=""`, asertar que `notify_n8n` (mockeado) igual se invoca desde el service (la decisión de no-op vive en la utilidad, no en el service). Ejecutar → PASA.

## 3. Aislamiento de fallos — fire-and-forget (RED → GREEN)

- [x] 3.1 RED: escribir `test_create_and_classify_succeeds_when_notify_n8n_raises` — configurar el `AsyncMock` de `notify_n8n` con `side_effect=RuntimeError("boom")`, llamar `create_and_classify(payload)`, y asertar que (a) NO se propaga la excepción y (b) el incidente retornado existe y quedó clasificado en `db_session`. Ejecutar → verificar comportamiento (con `create_task`, la excepción queda en la tarea y no rompe el flujo). Ajustar el assert/drenaje del loop según el mecanismo.
- [x] 3.2 GREEN: confirmar que el incidente y su `clasificacion_log` persisten pese al fallo de la tarea; si el test revela propagación, asegurar que la notificación corre desacoplada (`create_task`) tal que ningún `await` del fallo llegue al llamador. Ejecutar → PASA.

## 4. Test de integración — webhook real contra servidor mock (RED → GREEN → TRIANGULATE)

- [x] 4.1 RED: escribir `test_notify_n8n_posts_expected_payload_to_webhook` usando `notify_n8n` REAL contra el mock HTTP elegido en 1.2. Configurar `n8n_webhook_url` apuntando al mock (override de settings: `get_settings.cache_clear()` + monkeypatch de entorno, o `Settings` de prueba). Asertar que el mock recibió un `POST` cuyo JSON contiene `incidente_id`, `categoria`, `confianza`, `etapa`, `requiere_revision_humana` con los valores esperados. Ejecutar → confirmar (este test ejercita la utilidad real; sirve de contrato del payload, spec "Payload de notificación").
- [x] 4.2 GREEN: si el test falla por configuración de URL/cliente, ajustar el override de settings y el cliente mock hasta que el `POST` se capture correctamente. Ejecutar → PASA.
- [x] 4.3 TRIANGULATE (fallo del webhook): agregar `test_notify_n8n_swallows_error_on_webhook_500` — el mock responde 500 (o simula excepción de red); asertar que `notify_n8n` retorna `None` sin relanzar y que se registró el log de advertencia `n8n_notification_failed` (capturar logs con `caplog`/`structlog` testing capsys según el setup del proyecto). Ejecutar → PASA.

## 5. Refactor y cierre

- [x] 5.1 REFACTOR: revisar nombres de tests, extraer helpers de seed de catálogos a una función/fixture si hay duplicación, asegurar AAA en cada test y un solo comportamiento por test. Ejecutar tests tras cada paso → siguen verdes.
- [x] 5.2 Correr la suite completa del backend (`cd Gestion_Incidentes && pytest -q`) y confirmar que el conteo es baseline (1.1) + tests nuevos, sin regresiones. Opcional: `pytest --cov=app` para verificar que la cobertura no cae por debajo del umbral del proyecto.
- [x] 5.3 Verificación final contra las specs: confirmar que cada Scenario de `specs/n8n-notification/spec.md` (notificación disparada, webhook no configurado, no bloqueante, aislamiento de fallos, incidente persiste, payload) tiene un test que lo cubre. Anotar cualquier desviación.
