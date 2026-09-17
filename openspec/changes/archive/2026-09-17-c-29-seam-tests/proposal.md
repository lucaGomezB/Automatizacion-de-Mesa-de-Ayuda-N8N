## Why

Las tres suites del proyecto están en verde (backend 267 passed / 18 skipped, frontend 112 passed) pero el sistema está roto end-to-end: los defectos viven en COSTURAS que los tests no cubren. La suite PostgreSQL de integración nunca corrió en verde — sin PostgreSQL se auto-saltea en silencio y con PostgreSQL falla con `RuntimeError: ... got Future ... attached to a different loop`. La suite SQLite no aplica `PRAGMA foreign_keys=ON`, por lo que oculta violaciones de FK. Y los contratos runtime de N8N y de la configuración frontend/Docker no tienen ninguna prueba que los ancle a la forma real del backend. Este change repara la infraestructura de pruebas y codifica el comportamiento CORRECTO como tests que HOY FALLAN (fase RED de TDD).

## What Changes

- **BREAKING (solo en la suite de tests)**: eliminar el auto-skip silencioso de la suite PostgreSQL de integración. PostgreSQL es un prerrequisito REAL de esa suite; su ausencia SHALL fallar con un mensaje accionable, no saltar.
- **BREAKING (solo en la suite de tests)**: revertir el requisito de `integration-tests-postgresql` que ordena saltar cuando PostgreSQL no está disponible; se reemplaza por fallo ruidoso.
- Reparar el scope del event loop para pytest-asyncio 0.24: declarar explícitamente `asyncio_default_fixture_loop_scope` en `pytest.ini` y/o `loop_scope` en los fixtures, de modo que las conexiones asyncpg no queden atadas a un loop distinto al de los tests.
- Habilitar `PRAGMA foreign_keys=ON` en el engine SQLite de tests para que las violaciones de FK se manifiesten en lugar de quedar ocultas.
- Registrar una línea base (safety net) de conteos de tests antes/después de tocar `conftest.py` y `pytest.ini`, para demostrar que no se rompió lo que ya pasaba.
- Agregar pruebas de contrato runtime de N8N (extienden `tests/test_n8n_workflow.py`): autenticación en el HTTP Request al backend, `canal_origen_id` en el body, índices numéricos del Switch en modo expresión con campos existentes en la respuesta real del backend, conexión `ai_languageModel` del AI Agent, prompt que interpola el payload del trigger, configuración del trigger de Outlook para leer la descripción, `respondToWebhook` alcanzable desde un webhook con `responseMode: responseNode`, y credenciales declaradas en nodos que las requieren.
- Agregar pruebas de integración PostgreSQL (marker `integration`): `GET /api/v1/estadisticas/tendencias` y `/resumen` devuelven 200 en PostgreSQL, y `PATCH /api/v1/incidentes/{id}` con una FK inexistente devuelve 4xx (no 500).
- Agregar pruebas de configuración frontend/Docker: `VITE_API_BASE_URL` sin sufijo `/api/v1` duplicado y reenviada como build arg, `ARG` correspondiente en el Dockerfile, y rutas del cliente alineadas con las rutas OpenAPI (trailing slash).

Fuera de alcance explícito:

- NO se modifica código de producción (`app/**`, `n8n/workflow.json`, `docker-compose.yml`, `App/Frontend/Dockerfile`, servicios frontend). Este change es exclusivamente infraestructura de tests + tests (fase RED).
- NO se corrigen los defectos que los tests descubren; se codifican como fallos. La corrección es un change posterior.
- NO se incluye alineación con el documento de tesis (la tesis es referencia, no objeto de trabajo).

## Capabilities

### New Capabilities

- `seam-test-infrastructure`: infraestructura de testing que cierra las costuras transversales: un único event loop compartido entre fixtures async y tests (pytest-asyncio 0.24), ausencia de skips silenciosos ante prerrequisitos de la suite, y enforcement de claves foráneas en el engine SQLite de tests.

### Modified Capabilities

- `integration-tests-postgresql`: el requisito "PostgreSQL unavailability triggers skip" se invierte a fallo ruidoso y accionable; se agregan requisitos de cobertura de los endpoints de estadísticas y del PATCH con FK inexistente contra PostgreSQL real.
- `n8n-workflow`: se agregan requisitos de contrato runtime verificable por pruebas estructurales sobre el JSON exportado (autenticación HTTP, `canal_origen_id`, Switch por índice numérico, acoplamiento del AI Agent a su modelo de lenguaje y al payload, trigger de Outlook, cierre del webhook, credenciales declaradas).
- `frontend-production-build`: se agrega el requisito de que `VITE_API_BASE_URL` sea una configuración de build de fuente única (build arg reenviado por compose, `ARG` declarado en el Dockerfile, valor sin `/api/v1` duplicado).
- `frontend-testing`: se agrega el requisito de alineación entre las rutas del cliente HTTP del frontend y las rutas declaradas en la especificación OpenAPI (trailing slash incluido).

## Impact

- **Tests backend**: `App/Backend/tests/conftest.py`, `App/Backend/tests/test_integration_postgresql.py`, `App/Backend/tests/test_n8n_workflow.py`, nuevos tests de configuración frontend/Docker.
- **Configuración de tests**: `App/Backend/pytest.ini` (loop scope explícito).
- **Tests frontend**: `App/Frontend/src/**/*.test.ts` (alineación de rutas con OpenAPI).
- **Sin cambios de producto**: no se toca `app/**`, `n8n/workflow.json`, `docker-compose.yml`, `App/Frontend/Dockerfile` ni servicios frontend.
- **Gobernanza**: MEDIA (infraestructura de pruebas y contratos; sin efecto sobre datos de producción, pero con capacidad de descubrir defectos de capas críticas).
- **Dependencias**: PostgreSQL disponible vía `docker compose up -d postgres` (host 5433, user/pass/db `mesa/mesa/mesa_de_ayuda`); `pytest-asyncio==0.24.0`; Docker Compose para leer la configuración.
