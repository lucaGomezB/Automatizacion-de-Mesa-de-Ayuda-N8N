## Why

El PR #33 de Dependabot (`chore(deps): bump the backend-python group`) actualiza `App/Backend/requirements.txt` a versiones nuevas, incluyendo varias majors: FastAPI `0.135.0 -> 0.143.3`, Starlette `1.3.1 -> 1.8.0`, SQLAlchemy `2.0.36 -> 2.1.5`, structlog `24.4.0 -> 26.1.0`, cryptography `43.0.0 -> 50.0.2`, bcrypt `4.x -> 5.0.0`, uvicorn `0.30.6 -> 0.54.0`, alembic `1.13.3 -> 1.20.0` y pytest-cov `5.0.0 -> 7.1.0`. El CI del PR ya evidencia una rotura: `test_c86_comentarios.py::test_api_no_existe_edicion_ni_borrado_de_comentarios` falla con `AttributeError: '_IncludedRouter' object has no attribute 'path'` porque el test introspecciona `create_app().routes`. Como `AGENTS.md` y `openspec/config.yaml` fijan versiones exactas y exigen una suite verde, el bump no puede fusionarse sin una migracion deliberada.

## What Changes

- **Bump de pins (T)**: actualizar `App/Backend/requirements.txt` a las versiones objetivo del PR, revisando los comentarios de cada linea (motivo del pin, cotas superiores).
- **Auditoria de majors (T)**: evaluar cada salto de version mayor (FastAPI/Starlette, SQLAlchemy, structlog, cryptography, bcrypt, uvicorn, alembic, pytest-cov) leyendo el codigo real que usa cada libreria para determinar adaptaciones necesarias. Sin adivinar.
- **Adaptacion de codigo y tests (T)**: corregir la rotura confirmada (introspeccion del router en `tests/test_c86_comentarios.py`) y cualquier otra que la auditoria determine, sin refactors ajenos.
- **Sincronizacion OpenAPI (T)**: regenerar `docs/openapi.json` con el generador canonico si el schema cambia por efecto de las actualizaciones.
- **Verificacion (T)**: correr `pytest -m "not integration"`, `pytest -m integration`, `ruff check .` y `test_openapi_sync.py`, confirmando todo en verde.

### Out of scope (no-goals)

- NO se toca el frontend (la migracion a React 19 es el change `c-128`).
- NO se modifica la politica de Dependabot ni la de bloqueo del pipeline (eso es `c-129`).
- NO se agregan capacidades nuevas ni se adoptan dependencias opcionales de las majors (p. ej. OpenTelemetry de FastAPI 0.143).
- NO se refactoriza codigo ajeno a la rotura causada por las subidas.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `supply-chain-security`: se agrega un requisito que obliga a que la migracion de dependencias mayores del backend se ejecute en un unico change, con la matriz de versiones objetivo registrada, cada salto mayor auditado, y la suite completa (offline + integracion PostgreSQL + ruff + sincronizacion OpenAPI) en verde.

## Impact

- **Dependencias**: `App/Backend/requirements.txt` (16 actualizaciones; 9 con salto de major).
- **Codigo/tests backend**: `App/Backend/tests/test_c86_comentarios.py` (rotura confirmada) y los archivos que la auditoria de majors determine (`App/Backend/app/`, `App/Backend/tests/`).
- **Artefactos generados**: `docs/openapi.json` (regeneracion posible via `App/Backend/scripts/export_openapi.py`).
- **Sin cambios**: frontend, `.github/workflows/ci.yml`, politica de dependencias de Dependabot.
