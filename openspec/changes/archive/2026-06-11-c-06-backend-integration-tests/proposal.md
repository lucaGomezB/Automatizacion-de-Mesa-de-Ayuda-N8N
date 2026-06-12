## Why

La tesis §6.5 declara una pirámide de pruebas con un nivel intermedio de **pruebas de integración** que verifican la interacción entre el módulo Python y la base de datos, y reporta una cobertura del 87% medida con coverage.py. Hoy ese nivel intermedio **no existe en el repositorio**: la suite actual (~134 tests) cubre clasificadores, pseudonimización, cifrado, settings y el contrato de `notify_n8n` en aislamiento (capa unitaria y de servicio), pero **ningún test ejercita los endpoints HTTP de extremo a extremo** a través de la app ASGI con persistencia real (SQLite in-memory). Sin esa capa, la integración rutas → servicios → repositorios → ORM no es verificable de forma automatizada y el número de cobertura de la tesis no es auditable sobre los módulos `routes/`. C-06 construye esa capa intermedia: la suite de pruebas de integración de la API REST de `Gestion_Incidentes/`.

## What Changes

- **Tests de integración para `POST /api/v1/incidentes`** (`tests/test_api_incidentes.py`): creación + clasificación automática. Verifica HTTP 201, el contrato de `IncidenteRead`, la asignación de sector desde la clasificación, la marca `requiere_revision_humana`, y los errores de validación de payload (422). El `HybridClassifier` se inyecta como mock vía `dependency_overrides` (jamás se invoca Gemini real); `notify_n8n` se neutraliza con `patch` (fire-and-forget de C-02).
- **Tests de integración para `GET /api/v1/incidentes`** (mismo módulo): listado con filtros combinables (`sector_id`, `estado_id`, `prioridad`, `requiere_revision_humana`, `desde`, `hasta`), paginación (`limit`/`offset`), orden por fecha descendente y proyección ligera `IncidenteListItem`.
- **Tests de integración para `GET /api/v1/incidentes/{id}`**: detalle completo (200) y caso inexistente (404 con cuerpo `{"error": {"code": "NOT_FOUND", ...}}`).
- **Tests de integración para `PATCH /api/v1/incidentes/{id}`**: actualización parcial (PATCH semántico: solo campos no nulos), y 404 al actualizar un incidente inexistente.
- **Tests de integración para `GET /api/v1/clasificaciones/revision-pendiente`** (`tests/test_api_clasificaciones.py`): cola FIFO (más antiguo primero), filtrado por `requiere_revision_humana == True` y `sector_id_validado IS NULL`, paginación.
- **Tests de integración para `PATCH /api/v1/clasificaciones/{id}/validar`** (mismo módulo): validación humana que asigna `sector_id_validado`, retira el registro de la cola pendiente, y 404 ante log o sector inexistente.
- **Tests de integración para `GET /api/v1/health`** (`tests/test_api_health.py`): liveness probe (200 con `status` y `version`) y readiness `GET /api/v1/health/db` (200 con `database: reachable`).
- **Fixtures de catálogo sembrado** en `tests/conftest.py`: una fixture nueva que inserta los catálogos mínimos (`Estado "nuevo"`, los tres `Sector`, los `CanalOrigen`) que el `IncidenteService` resuelve por nombre, sin la cual la creación de incidentes falla con `EstadoNotFoundError`. Reusa el `client` ASGI y el `engine` SQLite in-memory ya existentes.
- **Cobertura objetivo**: > 85% en `app/routes/`, `app/services/` y `app/repositories/`, medida con `pytest --cov`.

No hay cambios **BREAKING**: C-06 es puramente aditivo (solo agrega archivos de test y fixtures). No modifica el código de producción de `Gestion_Incidentes/app/` ni la API.

## Capabilities

### New Capabilities
- `backend-integration-tests`: define el contrato de la suite de pruebas de integración de la API REST del backend — qué endpoints se ejercitan de extremo a extremo a través de la app ASGI con persistencia SQLite in-memory, qué comportamientos observables se verifican (códigos HTTP, contratos de respuesta, filtros, paginación, cola FIFO, validación humana, errores 404/422), el aislamiento obligatorio de los servicios externos (clasificador híbrido y webhook N8N siempre mockeados) y el umbral de cobertura sobre `routes/`, `services/` y `repositories/`.

### Modified Capabilities
<!-- Ninguna. C-06 es aditivo: no modifica los requisitos de capacidades existentes
     (data-pseudonymization, n8n-notification, n8n-workflow, evaluation-framework,
     foundation-environment). Solo verifica comportamiento ya especificado. -->

## Impact

- **Código nuevo**: módulos de test bajo `Gestion_Incidentes/tests/` (`test_api_incidentes.py`, `test_api_clasificaciones.py`, `test_api_health.py`) y fixtures de catálogo en `tests/conftest.py`. Sin cambios en `Gestion_Incidentes/app/`.
- **Infraestructura reusada**: `conftest.py` existente (motor SQLite in-memory `scope=session`, fixture `client` con `ASGITransport` y `app.dependency_overrides[get_db_session]`). C-06 agrega una fixture de catálogo sembrado y un patrón de override del clasificador, sin alterar las fixtures actuales.
- **Servicios externos aislados**: el `HybridClassifier` se inyecta mockeado por `IncidenteService(session, classifier=...)` vía `dependency_overrides` sobre `get_service`; `notify_n8n` se neutraliza con `patch` en `app.services.incidente_service.notify_n8n`. Nunca se contactan Gemini, Twilio, Outlook ni MTM-SRU.
- **Dependencias**: ninguna nueva. Usa `pytest`, `pytest-asyncio`, `httpx` (ya presentes). La cobertura se mide con el plugin `pytest-cov` (verificar presencia en `requirements*.txt` durante el apply; si falta, agregarlo a las dependencias de desarrollo).
- **Tesis**: materializa el nivel intermedio de la pirámide de pruebas de §6.5 y vuelve auditable la cobertura reportada sobre los módulos de rutas, servicios y repositorios.
- **Suite de tests**: incrementa el conteo actual (~134 passed) sin tocar los tests existentes; la corrida completa debe seguir verde.
