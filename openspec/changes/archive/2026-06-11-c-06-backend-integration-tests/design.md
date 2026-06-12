## Context

El backend `Gestion_Incidentes/` ya tiene una infraestructura de test madura en `tests/conftest.py`: motor SQLite in-memory (`scope=session`), fixture `db_session` con rollback por test, y fixture `client` que monta la app FastAPI con `httpx.ASGITransport` y sobrescribe `get_db_session` para usar la base de test. La suite actual (~134 tests) cubre clasificadores, pseudonimización, cifrado, settings y el contrato de `notify_n8n`, pero **no ejercita las rutas HTTP de extremo a extremo**.

Restricciones verificadas leyendo el código:

1. **`IncidenteService.create_and_classify` resuelve catálogos por nombre.** Busca el `Estado` "nuevo" (`_ESTADO_NUEVO`) y, tras clasificar, resuelve la categoría a un `Sector` por `nombre`. Sin esos registros sembrados, la creación falla con `EstadoNotFoundError`. El catálogo NO se siembra en `conftest.py` (las tablas se crean vacías con `Base.metadata.create_all`).
2. **El clasificador es inyectable.** `IncidenteService(session, classifier=...)` acepta un `HybridClassifier | None`. El endpoint lo construye vía `get_service(session)` que llama `IncidenteService(session)` (sin classifier → usa el real). Para inyectar un doble hay que sobrescribir la dependencia `get_service` del módulo de rutas, no `get_db_session`.
3. **`notify_n8n` es fire-and-forget vía `asyncio.create_task`.** Se importa como referencia local en `app.services.incidente_service`. El patrón ya probado en `test_incidente_notify_n8n.py` es `patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock)` + `await asyncio.sleep(0)` para drenar el loop.
4. **El prefijo `/api/v1`** lo agrega `register_routes()`; las rutas reales son `/api/v1/incidentes`, `/api/v1/clasificaciones/...`, `/api/v1/health`.
5. **`pytest-cov` NO está en `requirements.txt`.** La medición de cobertura objetivo (>85%) requiere agregar `pytest-cov` a las dependencias de desarrollo.
6. **`pytest.ini` usa `asyncio_mode = auto`**, pero los tests existentes marcan explícitamente `@pytest.mark.asyncio`. Se mantiene esa convención por consistencia.
7. **Errores 404** se serializan como `{"error": {"code": "NOT_FOUND", ...}}` por `register_error_handlers` (`EntityNotFoundError` → 404). Los 422 los produce la validación de Pydantic automáticamente.

## Goals / Non-Goals

**Goals:**
- Materializar el nivel intermedio de la pirámide de pruebas (tesis §6.5): integración rutas → servicios → repositorios → ORM sobre SQLite in-memory.
- Cubrir los 7 grupos de endpoints del scope con sus caminos felices y de error (201/200/404/422, filtros, paginación, FIFO, validación humana).
- Alcanzar cobertura > 85% sobre `app/routes/`, `app/services/`, `app/repositories/`, medible con un solo comando.
- Reusar la infraestructura existente de `conftest.py` sin romper los ~134 tests actuales.

**Non-Goals:**
- NO probar contra PostgreSQL real ni levantar el `docker-compose.yml` (eso es el nivel E2E de C-05, ya verificado).
- NO probar el clasificador híbrido en sí (cubierto por C-01/C-04: `test_deterministic_classifier`, `test_hybrid_classifier`, `test_gemini_*`). Aquí el clasificador es un doble.
- NO probar el contrato del payload de `notify_n8n` (cubierto por `test_incidente_notify_n8n.py`). Aquí solo se neutraliza.
- NO probar la lógica de pseudonimización (cubierta por C-03). El pipeline la ejecuta, pero los asserts no la verifican.
- NO modificar código de producción de `app/`.

## Decisions

### Decisión 1: Inyectar el clasificador vía `dependency_overrides` sobre `get_service`, no monkeypatch

El endpoint obtiene el servicio con `Depends(get_service)`, y `get_service` construye `IncidenteService(session)` con el clasificador real. Para inyectar un doble se sobrescribe la dependencia:

```python
app.dependency_overrides[get_service] = lambda: IncidenteService(session, classifier=fake_classifier)
```

El fake es un `AsyncMock` cuyo `.classify` devuelve un `ClasificacionResult` controlado por el test. Esto respeta la regla del proyecto "no usar monkeypatch para DB session — usar dependency_overrides" y la extiende al servicio.

**Alternativa descartada:** parchear `HybridClassifier.classify` globalmente con monkeypatch. Más frágil (acopla al nombre interno) y no permite variar el resultado por test con la misma claridad que un fake inyectado. Para que el fake comparta la **misma sesión** que el `client`, la fixture de override del servicio debe construirse de modo que el `IncidenteService` use la sesión de la request; la implementación concreta (fixture parametrizable o factory) se decide en el apply, pero el contrato es: el clasificador es un doble inyectado.

### Decisión 2: Fixture de catálogo sembrado nueva en `conftest.py`, sin tocar las existentes

Se agrega una fixture (p. ej. `seed_catalogs`) que, usando el `engine` de test, inserta el `Estado` "nuevo", los tres `Sector` y los `CanalOrigen`, y hace commit para que estén disponibles a través del `client` (que abre su propia sesión por request). Debe sembrarse **vía el engine compartido** (no vía `db_session`, que hace rollback), porque el `client` usa una sesión distinta de `db_session`. Para preservar el aislamiento, la fixture limpia las tablas de catálogo e incidentes al finalizar, o se apoya en que cada test siembra lo que necesita.

**Alternativa descartada:** sembrar dentro de cada test. Genera duplicación; una fixture compartida es más DRY y explícita sobre la precondición.

**Trade-off de aislamiento:** el motor es `scope=session` y compartido. Los tests de listado/cola que cuentan filas deben crear sus propios datos y no asumir una base vacía global, o la fixture debe garantizar limpieza. La estrategia concreta de limpieza (truncate por fixture function-scoped vs. conteo relativo) se fija en el apply siguiendo el principio "ningún test comparte estado mutable con otro".

### Decisión 3: Neutralizar `notify_n8n` con el patrón ya probado

Se reusa `patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock)` + `await asyncio.sleep(0)`. Para los tests de API esto puede encapsularse en una fixture (autouse acotada a los módulos de incidentes) que parchea la referencia local y drena el loop, garantizando cero peticiones salientes. El contrato de payload de N8N NO se re-verifica aquí.

### Decisión 4: Organización en tres módulos de test por recurso

- `test_api_incidentes.py` — POST, GET lista, GET detalle, PATCH (y sus 422/404).
- `test_api_clasificaciones.py` — GET revisión-pendiente (FIFO, filtros, paginación), PATCH validar (acierto, corrección, 404 log, 404 sector).
- `test_api_health.py` — health y health/db.

Espeja la estructura de rutas (`routes/incidentes.py`, `routes/clasificaciones.py`, `routes/health.py`) y la convención de nombres existente (`test_<unidad>_<escenario>_<esperado>`), patrón AAA y `@pytest.mark.asyncio`.

### Decisión 5: Cobertura con `pytest-cov`, agregado a requirements

Se agrega `pytest-cov` a `requirements.txt` (sección Development/Testing). El comando reproducible será:

```
pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing
```

ejecutado desde `Gestion_Incidentes/`. El umbral >85% se verifica leyendo el reporte e iterando sobre líneas faltantes (skill `pytest-coverage`). Se evalúa fijar `--cov-fail-under=85` en el comando de CI; no se fija en `pytest.ini` global para no romper la corrida de los tests rápidos sin cobertura.

## Risks / Trade-offs

- **[Estado global del motor `scope=session` filtra datos entre tests]** → Cada test crea sus propios incidentes y la fixture de catálogo limpia al finalizar; los tests de listado/cola usan asserts relativos (los registros que creó el test) en lugar de asumir base vacía. Regla dura: ningún test comparte estado mutable con otro.
- **[El fake del clasificador podría no compartir la sesión de la request, rompiendo la transacción]** → La fixture de override construye el `IncidenteService` con la sesión inyectada por el `client`; se valida en el primer test verde (creación con clasificación) antes de escalar.
- **[`asyncio.create_task(notify_n8n)` deja tareas colgando si no se drena el loop]** → Patrón `await asyncio.sleep(0)` ya probado; encapsulado en fixture para no olvidarlo. El `AsyncMock` evita cualquier I/O real.
- **[Divergencia SQLite vs PostgreSQL]** → Aceptada: el nivel de integración valida la lógica de aplicación y el ORM, no las particularidades del dialecto. El comportamiento específico de PostgreSQL se valida en el nivel E2E con docker-compose (fuera de scope).
- **[`pytest-cov` ausente bloquea la medición]** → Se agrega a `requirements.txt` como primer paso del apply.
- **[Llegar a >85% en `repositories/` puede requerir tests que no son de API pura]** (p. ej. ramas de `list_filtered` con todos los filtros) → Se cubren ejercitando el endpoint de listado con cada combinación de filtros; si queda una rama sin cubrir vía HTTP, se documenta y se decide si amerita un test de repositorio directo.

## Migration Plan

No aplica despliegue ni rollback: C-06 solo agrega archivos de test y una dependencia de desarrollo. El "rollback" es revertir el commit. La verificación de éxito es la corrida de la suite completa en verde con la cobertura objetivo alcanzada.

## Open Questions

- Ninguna que bloquee el apply. La estrategia exacta de limpieza/aislamiento de la fixture de catálogo (truncate function-scoped vs. conteo relativo) se resuelve durante la implementación TDD según cuál produzca tests más independientes; ambas satisfacen la spec.
