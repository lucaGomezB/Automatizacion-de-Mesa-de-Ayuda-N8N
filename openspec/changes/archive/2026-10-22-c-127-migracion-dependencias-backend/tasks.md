# Tasks: c-127 — Migracion de dependencias del backend

> **Leer antes**
> - `proposal.md` y `design.md` de este change (matriz de versiones en D1, rotura confirmada en D2, criterio de auditoria en D3, fallback en D5).
> - `App/Backend/requirements.txt` (pins previos; 16 actualizaciones).
> - `App/Backend/tests/test_c86_comentarios.py` (lines 226-230: introspeccion de `app.routes`, rotura confirmada del PR #33).
> - `App/Backend/app/core/database.py` (`async_sessionmaker(..., autocommit=False)`, candidato SQLAlchemy 2.1).
> - `App/Backend/scripts/export_openapi.py` y `AGENTS.md` (procedimiento canonico de regeneracion OpenAPI).
> - `openspec/specs/supply-chain-security/spec.md` (politica de pinning vigente).
>
> **Convencion de rutas**: `R = App/Backend/requirements.txt`.
> **Governance MEDIO**: implementar con checkpoints; registrar en las notas de apply cualquier decision no obvia.
> **Fallback valido (D5)**: si una major no es viable sin rotura desproporcionada, conservar su pin previo, registrar la conclusion con evidencia y dejar seguimiento revisado. No forzar una major rota.

## 1. Safety net y baseline

- [x] 1.1 Registrar la linea base pre-change: `cd App/Backend; pytest -m "not integration" -q` con los pins VIEJOS; anotar el conteo de tests (safety net). Verificacion: la corrida termina en verde y el conteo queda registrado.
- [x] 1.2 Confirmar disponibilidad de PostgreSQL para el subconjunto de integracion (`docker compose up -d postgres`; `pytest -m integration`). Si no hay PostgreSQL, registrar la limitacion y delegar la cobertura a CI. Verificacion: el subconjunto pasa o la limitacion queda documentada.

## 2. Bump de requirements.txt

- [x] 2.1 Editar `R` con la matriz de D1 (16 actualizaciones), actualizando el comentario de cada linea para registrar el motivo del pin y las cotas superiores. Verificacion: `pip install -r App/Backend/requirements.txt` resuelve sin conflicto y `python -m pip check` no reporta incompatibilidades.
- [x] 2.2 Confirmar las versiones efectivamente instaladas de las majors: `cd App/Backend; python -c "import fastapi, starlette, sqlalchemy, structlog, cryptography, bcrypt, alembic, pydantic; print(fastapi.__version__, starlette.__version__, sqlalchemy.__version__, structlog.__version__, cryptography.__version__, bcrypt.__version__, alembic.__version__, pydantic.__version__)"`. Verificacion: coinciden con la matriz D1.

## 3. Auditoria de cada salto de version mayor

- [x] 3.1 Auditar FastAPI `0.135.0 -> 0.143.3` y Starlette `1.3.1 -> 1.8.0`: revisar los puntos de import directo de starlette (`app/core/error_handlers.py`, `app/main.py`, `tests/test_c91_refresh_cookie.py`) y la introspeccion de `app.routes`. Determinar si requiere adaptacion (D2). Verificacion: conclusion registrada (requiere/no requiere) con la evidencia de la corrida.
- [x] 3.2 Auditar SQLAlchemy `2.0.36 -> 2.1.5`: revisar `app/core/database.py` (candidato `autocommit=False` en `async_sessionmaker`), el uso de `selectinload` y `DeclarativeBase`, y `alembic/env.py`. Determinar adaptaciones. Verificacion: conclusion registrada; candidatos resueltos o descartados.
- [x] 3.3 Auditar structlog `24.4.0 -> 26.1.0`: revisar `app/core/logging.py` (cadena de `ProcessorFormatter`, `structlog.types`, `structlog.dev`) y `structlog.testing.capture_logs` en tests. Determinar adaptaciones. Verificacion: conclusion registrada.
- [x] 3.4 Auditar cryptography `43.0.0 -> 50.0.2`: revisar `app/utils/encryption.py` (`Fernet`/`MultiFernet`) y `tests/test_c63c_fernet_rotation.py`, `tests/test_encryption.py`. Determinar adaptaciones. Verificacion: conclusion registrada.
- [x] 3.5 Auditar bcrypt `4.x -> 5.0.0`: revisar `app/services/auth_service.py`, `app/services/mfa_service.py` y `app/utils/password_policy.py` (`hashpw`/`checkpw`/`gensalt`). Determinar adaptaciones. Verificacion: conclusion registrada.
- [x] 3.6 Auditar uvicorn `0.30.6 -> 0.54.0`: revisar el constructor `ProxyHeadersMiddleware(app, trusted_hosts=...)` en `tests/test_runtime_cost_guard.py:1489`. Determinar adaptaciones. Verificacion: conclusion registrada.
- [x] 3.7 Auditar alembic `1.13.3 -> 1.20.0`: revisar `alembic/env.py` y las migraciones `alembic/versions/` (`async_engine_from_config`, `context.configure`). Determinar adaptaciones. Verificacion: conclusion registrada.
- [x] 3.8 Auditar pytest-cov `5.0.0 -> 7.1.0`: revisar el comportamiento de medicion de cobertura sobre `app.routes`, `app.services`, `app.repositories`. Determinar adaptaciones. Verificacion: conclusion registrada.

## 4. Adaptacion de codigo y tests

- [x] 4.1 Corregir la rotura confirmada en `tests/test_c86_comentarios.py:226-230`: adaptar la recoleccion de rutas para considerar solo las que exponen `path` (p. ej. `getattr(r, "path", None)`), preservando la conducta verificada (ausencia de endpoints de edicion/borrado de comentarios). Verificacion: el test pasa con los pins nuevos.
- [x] 4.2 Aplicar las adaptaciones que determine la auditoria del grupo 3 (codigo de aplicacion y/o tests). Sin refactors ajenos a la rotura. Verificacion: cada adaptacion queda justificada por un fallo reproducible y la suite avanza.
- [x] 4.3 Si una major resulta no viable (D5), conservar su pin previo, registrar la conclusion con evidencia en las notas de apply y dejar seguimiento revisado. Verificacion: el pin previo queda restaurado y la limitacion documentada.

## 5. Regeneracion del esquema OpenAPI

- [x] 5.1 Si el esquema cambia por efecto de las actualizaciones, regenerar `docs/openapi.json` con el generador canonico: `cd App/Backend; python scripts/export_openapi.py`. Verificacion: `pytest tests/test_openapi_sync.py -v` pasa. Si el esquema no cambia, registrar que no requirio regeneracion.

## 6. Verificacion de la suite completa

- [x] 6.1 `cd App/Backend; pytest -m "not integration" -q`: verde, con el mismo conteo de la linea base 1.1 (o mayor, sin fallos). Verificacion: sin fallos ni errores de coleccion.
- [x] 6.2 `cd App/Backend; pytest -m integration`: verde (o limitacion de entorno documentada si no hay PostgreSQL). Verificacion: sin fallos.
- [x] 6.3 `cd App/Backend; ruff check .`: sin hallazgos nuevos respecto de la linea base. Verificacion: el paso completa segun la configuracion versionada.
- [x] 6.4 `cd App/Backend; pytest tests/test_openapi_sync.py -v`: verde. Verificacion: el esquema versionado esta sincronizado con el codigo.

## 7. Cierre

- [x] 7.1 Correr `openspec validate --strict c-127-migracion-dependencias-backend`. Verificacion: 0 fallos.
- [x] 7.2 Registrar en las notas de apply la matriz final de versiones efectivamente instaladas, las adaptaciones aplicadas y cualquier fallback. Verificacion: la matriz final coincide con lo instalado.

## Notas de apply (2026-10-22)

### Matriz final efectivamente instalada

Todas las versiones objetivo de D1 existen en PyPI y resolvieron sin conflicto.
Instaladas (verificadas por import):

| Dependencia | Instalada |
|-------------|-----------|
| fastapi | 0.143.3 |
| starlette | 1.8.0 |
| sqlalchemy | 2.1.5 |
| structlog | 26.1.0 |
| cryptography | 50.0.2 |
| bcrypt | 5.0.0 |
| alembic | 1.20.0 |
| pydantic | 2.14.1 |
| pydantic-settings | 2.16.0 |
| google-genai | 2.32.0 (>= 2.31.0) |
| uvicorn | 0.54.0 |
| asyncpg | 0.32.0 |
| aiosqlite | 0.22.1 |
| pytest-cov | 7.1.0 |
| pyotp | 2.10.0 |
| python-jose | >= 3.5.0,<4 resuelto |

### Adaptaciones aplicadas

- **Unica adaptacion de codigo**: D2 en `App/Backend/tests/test_c86_comentarios.py`
  (filtrado de `app.routes` a las rutas que exponen `path`). La conducta verificada
  (ausencia de endpoints de edicion/borrado de comentarios) se preserva intacta.
- **FastAPI/Starlette**: adaptado (D2). Los puntos de import directo de starlette
  (`app/core/error_handlers.py`, `app/main.py`, `tests/test_c91_refresh_cookie.py`)
  no requirieron cambios.
- **SQLAlchemy 2.1**: auditado, NO requirio adaptacion. `async_sessionmaker(...,
  autocommit=False)` sigue aceptado (reproducido en el repr del objeto); `selectinload`
  y `DeclarativeBase` sin cambios.
- **uvicorn 0.54**: auditado, NO requirio adaptacion (`ProxyHeadersMiddleware(app,
  trusted_hosts=...)` intacto).
- **structlog 26**: auditado, NO requirio adaptacion (cadena `ProcessorFormatter`/
  `structlog.types` estable).
- **cryptography 50**: auditado, NO requirio adaptacion (`Fernet`/`MultiFernet` intactos).
- **bcrypt 5**: auditado, NO requirio adaptacion (`hashpw`/`checkpw`/`gensalt` intactos).
- **alembic 1.20**: auditado, NO requirio adaptacion. Emite un `DeprecationWarning`
  por `path_separator` en la config (no bloqueante; fuera de alcance de este change).
- **pytest-cov 7.1.0**: auditado, NO requirio adaptacion; la medicion sobre
  `app.services`/`app.repositories` reporta normalmente.

### OpenAPI

El esquema generado NO cambio por efecto de las actualizaciones:
`tests/test_openapi_sync.py` pasa (5/5) sin regenerar `docs/openapi.json`.

### Fallback (D5)

Ninguna major resulto no viable: NO se aplico fallback. La matriz D1 avanzo completa.

### Desviacion de entorno

`python` no existe en el entorno; se uso `python3`. La instalacion requirio
`--user --break-system-packages` (PEP 668). `pip check` reporta unicamente
`sqlmodel 0.0.39 requires SQLAlchemy<2.1.0`, paquete ajeno al proyecto (no figura
en `requirements.txt` ni se importa en `App/Backend/`), preexistente en el sitio del
usuario; no afecta la suite.
