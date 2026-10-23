## Context

Ver `proposal.md` - Why. El estado actual que condiciona el diseno:

- `App/Backend/requirements.txt` fija los pins previos. El PR #33 de Dependabot propone la matriz objetivo completa (D1).
- El codigo importa `starlette` directo (`app/core/error_handlers.py`, `app/main.py`, `tests/test_c91_refresh_cookie.py`) y `uvicorn` directo (`tests/test_runtime_cost_guard.py:43` importa `uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware`).
- La unica introspeccion de `app.routes` en todo el backend esta en `tests/test_c86_comentarios.py:226-230`: `{(r.path, ...) for r in create_app().routes}`. Con FastAPI 0.143 / Starlette 1.8 el `app.routes` incluye objetos `_IncludedRouter` sin atributo `path`, y ese es el fallo confirmado en el CI del PR (`AttributeError: '_IncludedRouter' object has no attribute 'path'`).
- `App/Backend/app/core/database.py:48-54` construye `async_sessionmaker(..., autoflush=False, autocommit=False)`. `autocommit` es candidato a remocion/endurecimiento en SQLAlchemy 2.1.
- El generador canonico del OpenAPI es `App/Backend/scripts/export_openapi.py` (serializa con `sort_keys=True`; patron ya usado por c-97 para el fallout de FastAPI).

## Goals / Non-Goals

**Goals:**

- Definir la matriz exacta de versiones objetivo y las restricciones de compatibilidad que la vinculan.
- Determinar por adelantado la rotura confirmada y los candidatos a auditar por cada salto de major.
- Dejar explicito el plan de rollback y el criterio de fallback por dependencia.

**Non-Goals:**

- No se fija una version intermedia distinta de la que ya propone el PR, salvo que un salto resulte no viable (fallback por dependencia).
- No se adopta ninguna dependencia opcional nueva (p. ej. OpenTelemetry de FastAPI 0.143).
- No se toca el frontend ni los workflows de CI.
- No se convierte `requirements.txt` en un lock completo.

## Decisions

### D1 - Matriz de versiones objetivo

| Dependencia | Actual | Objetivo | Salto |
|-------------|--------|----------|-------|
| `fastapi` | `0.135.0` | `0.143.3` | minor |
| `starlette` | `1.3.1` | `1.8.0` | minor |
| `uvicorn[standard]` | `0.30.6` | `0.54.0` | minor |
| `asyncpg` | `0.29.0` | `0.32.0` | minor |
| `sqlalchemy[asyncio]` | `2.0.36` | `2.1.5` | **major** |
| `alembic` | `1.13.3` | `1.20.0` | minor |
| `pydantic` | `>=2.12.5,<3` | `>=2.14.1,<3` | minor |
| `pydantic-settings` | `2.5.2` | `2.16.0` | minor |
| `google-genai` | `>=2.20.0,<3` | `>=2.31.0,<3` | minor |
| `structlog` | `24.4.0` | `26.1.0` | **major** |
| `cryptography` | `>=43.0.0` | `>=50.0.2` | **major** |
| `python-jose[cryptography]` | `>=3.3.0,<4` | `>=3.5.0,<4` | minor |
| `bcrypt` | `>=4.0.0,<5` | `>=5.0.0,<6` | **major** |
| `pyotp` | `2.9.0` | `2.10.0` | minor |
| `aiosqlite` | `0.20.0` | `0.22.1` | minor |
| `pytest-cov` | `5.0.0` | `7.1.0` | **major** |

Sin cambios: `python-multipart==0.0.32`, `httpx==0.28.1`, `pytest==9.1.1`, `pytest-asyncio==1.4.0`. En `pydantic`, `google-genai`, `cryptography`, `python-jose` y `bcrypt` la forma es rango con cota superior (o marcador `no-upper-bound-ok` en `cryptography`), preservando la politica vigente de `supply-chain-security`.

### D2 - Rotura confirmada: introspeccion del router

`tests/test_c86_comentarios.py::test_api_no_existe_edicion_ni_borrado_de_comentarios` construye `create_app()` y recorre `app.routes` accediendo a `r.path`. Con FastAPI 0.143 / Starlette 1.8, `app.routes` incluye routers incluidos (`_IncludedRouter`) sin `path`. Adaptacion: filtrar por `getattr(r, "path", None)` (o recolectar solo rutas con `path`) sin cambiar la conducta verificada (no existen endpoints `.../comentarios/{id}`). Alternativa considerada: usar `app.router.routes` o `app.openapi()["paths"]`; se descarta por menor fidelidad al objeto que el test inspeccionaba.

### D3 - Auditoria antes de adaptar (no adivinar)

Cada salto de major se audita leyendo el uso real de la libreria antes de tocar codigo. Candidatos identificados al proponer:

- **SQLAlchemy 2.1**: `async_sessionmaker(autocommit=False)` en `app/core/database.py:53` — probable remocion del kwarg; ajustar si la corrida falla.
- **uvicorn 0.54**: constructor `ProxyHeadersMiddleware(app, trusted_hosts=...)` en `tests/test_runtime_cost_guard.py:1489` — verificar firma.
- **structlog 26**: cadena de `ProcessorFormatter`/`structlog.types` en `app/core/logging.py` — verificar estabilidad de la API usada.
- **cryptography 50**: `Fernet`/`MultiFernet` en `app/utils/encryption.py` y tests de rotacion — verificar.
- **bcrypt 5.0**: `hashpw`/`checkpw`/`gensalt` en `app/services/auth_service.py`, `mfa_service.py`, `password_policy.py` — verificar (passlib figura solo en docstrings).
- **alembic 1.20**: `alembic/env.py` usa `async_engine_from_config` y `context.configure` — verificar.
- **pytest-cov 7.1.0**: comportamiento de medicion/cobertura — verificar que la suite con cobertura sigue reportando las capas objetivo.

La suite completa es el veredicto: si un candidato no rompe, no se toca.

### D4 - Sincronizacion OpenAPI

Si FastAPI 0.143 cambia el schema generado, se regenera `docs/openapi.json` con `cd App/Backend; python scripts/export_openapi.py` (mismo procedimiento de c-97) y se confirma `tests/test_openapi_sync.py`. No se edita el JSON a mano.

### D5 - Fallback por dependencia

Si un salto mayor NO es viable sin rotura desproporcionada, se conserva el pin previo de esa dependencia, se registra la conclusion con evidencia en `design.md`/notas de apply y se deja seguimiento revisado. El resto de la matriz avanza. No se fuerza una major rota.

## Risks / Trade-offs

- [SQLAlchemy 2.1 remueve `autocommit` u otra API usada] -> Ajuste acotado en `app/core/database.py`; verificar con la suite offline.
- [`app.routes` cambia de forma y rompe otro test] -> El unico consumidor de `app.routes` es `test_c86_comentarios.py`; la correccion de D2 lo cubre.
- [OpenAPI cambia y rompe `test_openapi_sync.py`] -> Regenerar con el generador canonico (D4).
- [structlog/cryptography/bcrypt/uvicorn remueven APIs poco usadas] -> Auditoria previa (D3); fallback por dependencia (D5) si la rotura no es acotada.
- [Resolucion transitiva inestable de pip] -> Se respetan las cotas superiores ya declaradas; `cryptography` mantiene su excepcion documentada.

## Migration Plan

1. Baseline: `cd App/Backend; pytest -m "not integration" -q` y registrar el conteo (safety net) antes de tocar pins.
2. Editar `App/Backend/requirements.txt` con la matriz D1 y actualizar los comentarios de pin.
3. `pip install -r App/Backend/requirements.txt` y `python -m pip check`.
4. Auditar cada major (D3) y corregir el fallout acotado (D2 y demas).
5. Regenerar `docs/openapi.json` si el schema cambio (D4).
6. Verificar: `pytest -m "not integration"`, `pytest -m integration`, `ruff check .`, `pytest tests/test_openapi_sync.py`.
7. `openspec validate --strict`.

**Rollback**: revertir `App/Backend/requirements.txt` a los pins previos de la matriz D1, reinstalar y, si se regenero, revertir `docs/openapi.json`. El punto de retorno conocido-bueno es el commit previo al change. Fallback parcial: conservar solo los pins previos de las dependencias no viables (D5).

## Open Questions

- Si el subconjunto PostgreSQL es ejecutable en el entorno local durante el apply; si no lo es, se registra la limitacion y se delega la cobertura a CI (no cambia specs ni tareas).
- Si alguna major exige una adaptacion mayor que el fallback por dependencia; se decide en el apply con la evidencia de la corrida.
