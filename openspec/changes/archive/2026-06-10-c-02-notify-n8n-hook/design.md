## Context

El backend ya clasifica incidentes y persiste el resultado en `IncidenteService._apply_classification()` (`app/services/incidente_service.py`, líneas 223-264). La utilidad `notify_n8n(incidente_id, result)` (`app/utils/n8n_webhook.py`) está completa: arma el payload, agrega el header de autenticación opcional `X-N8N-Secret`, hace `POST` con timeout de 5 s, y captura toda excepción registrándola como `logger.warning("n8n_notification_failed", ...)`. **El único gap es que `_apply_classification()` nunca la invoca.**

Restricciones del entorno:
- FastAPI 0.115 + SQLAlchemy 2.0 async (asyncpg); todo el camino es `async def`.
- `create_and_classify()` corre dentro de la transacción de DB de la request; la sesión se commitea en la dependencia `get_db_session` (ver `conftest.py` `override_db`).
- La utilidad ya es internamente segura ante fallos (try/except total), pero **`notify_n8n` es `async`**: si se la `await`-ea directamente, su latencia (hasta 5 s de timeout) se suma a la respuesta HTTP, lo que viola la garantía no-bloqueante de la spec.
- Gobernanza: BAJO (integración aditiva, sin impacto en datos ni en respuesta al usuario).

## Goals / Non-Goals

**Goals:**
- Invocar `notify_n8n(incidente.id, result)` desde `_apply_classification()` tras aplicar la clasificación.
- Garantizar fire-and-forget real: la respuesta HTTP no debe esperar ni demorarse de forma observable por la notificación, y ningún fallo de N8N propaga ni rompe la creación del incidente.
- Cubrir con tests: (a) unitario — se llama a `notify_n8n` con los parámetros correctos; (b) integración — el webhook recibe el payload esperado y un fallo del webhook no rompe el flujo.

**Non-Goals:**
- No se modifica el contrato ni el cuerpo de `notify_n8n` (payload, headers, timeout permanecen como están).
- No se agregan reintentos, cola de mensajes, ni persistencia de notificaciones pendientes (fuera de alcance; posible mejora futura).
- No se cambia el contrato REST público ni el flujo de N8N (Anexo E).
- No se introduce un task scheduler ni dependencias nuevas.

## Decisions

### Decisión 1 — Mecanismo fire-and-forget: `asyncio.create_task` con captura de excepción

**Elegido:** dentro de `_apply_classification()`, al final, programar la notificación como tarea independiente:

```python
import asyncio
from app.utils.n8n_webhook import notify_n8n

# ... al final de _apply_classification, tras el logger.info("incidente_classified", ...)
asyncio.create_task(notify_n8n(incidente.id, result))
```

`notify_n8n` ya envuelve todo su cuerpo en try/except y nunca relanza, por lo que la tarea no puede dejar una excepción sin recoger ("Task exception was never retrieved"). Esto mantiene el método no bloqueante: `create_task` agenda la corrutina en el event loop y retorna de inmediato; la respuesta HTTP no espera el `POST` a N8N.

**Alternativas consideradas:**
- **`await notify_n8n(...)` directo** — descartado: suma hasta 5 s (timeout) a cada respuesta HTTP cuando N8N está lento/caído. Viola la garantía no-bloqueante de la spec aunque no propague el fallo.
- **FastAPI `BackgroundTasks`** — descartado: requiere inyectar `BackgroundTasks` desde el handler de la ruta hasta el service, atravesando las capas (route → service) solo para esto. Acopla la capa de servicio a un objeto de FastAPI, contradiciendo la regla "service must never import from API handlers". Se ejecuta después de enviar la respuesta, lo cual es correcto, pero el costo de plomería no se justifica frente a `create_task`.
- **`asyncio.ensure_future` / pool de tareas con tracking** — descartado: complejidad innecesaria (KISS) para una notificación aditiva sin garantía de entrega.

**Trade-off asumido:** `create_task` no garantiza que la tarea termine si el proceso/loop muere justo después de responder. Es aceptable: la notificación es best-effort por diseño (la spec ya define que su fallo no degrada nada), y N8N es la integración aditiva, no la fuente de verdad.

### Decisión 2 — Punto de invocación: dentro de `_apply_classification()`

**Elegido:** invocar dentro de `_apply_classification()`, después de `logger.info("incidente_classified", ...)`. En ese punto el incidente ya tiene `id`, sector aplicado, `clasificacion_log` creado, y `result` está disponible. Es exactamente donde el roadmap lo indica.

**Alternativa:** invocar en `create_and_classify()` tras `_apply_classification()`. Descartada para alinear con el scope del roadmap y porque `_apply_classification` es el dueño semántico del "ya quedó clasificado".

**Nota sobre testabilidad / inyección de I/O:** `notify_n8n` se importa a nivel de módulo en `incidente_service.py` y se referencia como `notify_n8n(...)`. Los tests lo mockean parcheando el símbolo **en el módulo de servicio** (`app.services.incidente_service.notify_n8n`), no en el de origen, porque el `import` crea una referencia local. Esto mantiene el I/O mockeable sin cambiar la firma del service.

### Decisión 3 — Contrato de parámetros: `incidente.id` + `result`

`_apply_classification(self, incidente, result)` ya recibe ambos:
- `incidente.id: int` — el ID persistido. Coincide con el primer parámetro `incidente_id: int` de `notify_n8n`.
- `result: ClasificacionResult` — coincide con el segundo parámetro `result: ClasificacionResult`.

No hace falta transformar nada: la utilidad deriva `categoria`, `confianza`, `etapa`, `requiere_revision_humana` desde `result`. El payload queda determinado por la utilidad (no se duplica la lógica de payload en el service).

### Decisión 4 — Estrategia de tests

**(a) Test unitario** (`tests/test_incidente_notify_n8n.py`, capa servicio):
- Parchear `app.services.incidente_service.notify_n8n` con `AsyncMock` y `app.classifiers.hybrid.HybridClassifier.classify` (o inyectar un classifier mock vía el parámetro `classifier=` del constructor) con un `ClasificacionResult` conocido.
- Usar la fixture `db_session` (SQLite in-memory) y sembrar los catálogos mínimos necesarios (`estado="nuevo"`, sector) que `create_and_classify`/`_apply_classification` resuelven.
- Llamar `create_and_classify(payload)` y, tras dar oportunidad al loop de drenar la tarea (`await asyncio.sleep(0)`), assert: `notify_n8n` fue llamado una vez con `(incidente.id, result_esperado)`.
- Triangulación: segundo caso con otro `ClasificacionResult` (p. ej. `etapa="fallback"`, `requiere_revision_humana=True`) para verificar que el `result` se pasa tal cual (no hardcodeado). Caso borde: con `n8n_webhook_url` vacío igual se llama a `notify_n8n` (la decisión de no-op es de la utilidad, no del service) — confirma el contrato de invocación.

**(b) Test de integración** (`tests/test_incidente_notify_n8n.py` o módulo aparte, contra `notify_n8n` real):
- Levantar un servidor HTTP mock local. Preferencia: `pytest-httpx` (mock del cliente `httpx`) si está disponible; si no, un handler ASGI/WSGI mínimo o `respx`. Configurar `n8n_webhook_url` a esa URL vía override de settings (`get_settings.cache_clear()` + monkeypatch de env, o instanciar `Settings` de prueba).
- Caso feliz: `notify_n8n(incidente_id, result)` real → el mock recibe un `POST` cuyo JSON contiene `incidente_id`, `categoria`, `confianza`, `etapa`, `requiere_revision_humana` con los valores esperados (cubre la spec "Payload de notificación").
- Caso de fallo: el mock responde 500 (o se simula excepción de red) → `notify_n8n` NO relanza (retorna `None`) y se registra `n8n_notification_failed`. Verifica el aislamiento de fallos a nivel de utilidad.
- Verificar antes qué librerías de mock HTTP están disponibles en el entorno (`pytest-httpx` / `respx`); si ninguna, usar un servidor ASGI mínimo con `httpx.ASGITransport` apuntando a una app FastAPI/Starlette de un solo endpoint que capture el request.

**Patrón de mocking async:** `AsyncMock` para corrutinas; nunca `Mock` para `notify_n8n` (es `async`). AAA en cada test. Un comportamiento por test, nombres `test_<unidad>_<escenario>_<esperado>`.

## Risks / Trade-offs

- **[Tarea no esperada al apagar el proceso]** Si el worker se reinicia inmediatamente tras responder, una notificación en vuelo puede perderse. → Mitigación: aceptable por diseño best-effort; N8N es aditivo. Reintentos/cola quedan como mejora futura explícita (Non-Goal).
- **[`create_task` y el ciclo de vida de la sesión DB]** La tarea NO debe tocar `self._session` (podría cerrarse al terminar la request). → Mitigación: `notify_n8n` solo recibe `incidente.id` (int) y `result` (DTO Pydantic) — valores planos, sin ORM ni sesión. No hay lazy-load ni acceso a DB en la tarea.
- **[Flakiness del test unitario por timing del event loop]** La tarea creada con `create_task` puede no haber corrido cuando se hace el assert. → Mitigación: dado que `notify_n8n` está mockeado con `AsyncMock`, drenar el loop con `await asyncio.sleep(0)` antes del assert; el mock no hace I/O real, por lo que un solo yield basta.
- **[Parcheo del símbolo equivocado]** Mockear `app.utils.n8n_webhook.notify_n8n` en vez de `app.services.incidente_service.notify_n8n` no interceptaría la llamada (referencia local por el import). → Mitigación: documentado en Decisión 2; el test parchea el símbolo en el módulo de servicio.
- **[Disponibilidad de librería de mock HTTP en CI]** El test de integración depende de `pytest-httpx`/`respx` o de un servidor ASGI local. → Mitigación: verificar disponibilidad en `pyproject`/entorno durante apply; fallback a app Starlette mínima vía `httpx.ASGITransport`.
