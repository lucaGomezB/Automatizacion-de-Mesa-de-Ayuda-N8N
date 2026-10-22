## ADDED Requirements

### Requirement: Migracion de dependencias mayores del backend con suite verde

El repositorio SHALL poder migrar las dependencias del backend (`App/Backend/requirements.txt`) a versiones mayores nuevas manteniendo la suite del backend en verde. La migracion MUST aplicarse en un unico change, MUST registrar en el `design.md` la matriz de versiones objetivo de cada dependencia bumpeada (version actual y version objetivo) y la restriccion de compatibilidad que las vincula, y MUST auditar cada salto de version mayor leyendo el codigo real que usa la libreria para determinar las adaptaciones de codigo y de tests necesarias. Tras la migracion, MUST pasar la suite SQLite offline (`pytest -m "not integration"`), el subconjunto de integracion PostgreSQL (`pytest -m integration`), el lint del backend (`ruff check .`) y la verificacion de sincronizacion del esquema OpenAPI (`tests/test_openapi_sync.py`). Cuando el esquema OpenAPI cambie por efecto de las actualizaciones, `docs/openapi.json` MUST regenerarse con el generador canonico (`App/Backend/scripts/export_openapi.py`). Cuando un salto mayor NO sea viable sin una rotura desproporcionada, el `design.md` MUST registrar esa conclusion con evidencia y la dependencia afectada PUEDE mantenerse en su pin previo con un seguimiento revisado.

#### Scenario: La matriz de versiones objetivo queda registrada

- **WHEN** se lee el `design.md` del change
- **THEN** registra, para cada dependencia bumpeada de `App/Backend/requirements.txt`, la version actual y la version objetivo, la restriccion de compatibilidad que las vincula y el plan de rollback

#### Scenario: Cada salto de version mayor queda auditado

- **WHEN** se revisan las tareas de auditoria del change
- **THEN** existe una tarea por cada salto de version mayor (FastAPI/Starlette, SQLAlchemy, structlog, cryptography, bcrypt, uvicorn, alembic, pytest-cov) que evalua el uso real de la libreria en `App/Backend/app/` y `App/Backend/tests/` y registra si requiere adaptacion

#### Scenario: La suite completa queda verde tras la migracion

- **WHEN** se ejecutan `pytest -m "not integration"`, `pytest -m integration`, `ruff check .` y `tests/test_openapi_sync.py` con los pins actualizados
- **THEN** todas las corridas pasan sin fallos

#### Scenario: El esquema OpenAPI se mantiene sincronizado

- **WHEN** las actualizaciones producen un cambio en el esquema OpenAPI generado
- **THEN** `docs/openapi.json` se regenera con el generador canonico y `tests/test_openapi_sync.py` vuelve a pasar

#### Scenario: La introspeccion del router se adapta a la version nueva

- **WHEN** un test recorre `create_app().routes` y la version nueva de FastAPI/Starlette expone routers incluidos sin atributo `path`
- **THEN** el test se adapta para considerar solo las rutas que exponen `path`, preservando exactamente la conducta que verificaba (ausencia de endpoints de edicion/borrado de comentarios)

#### Scenario: Fallback documentado cuando el salto mayor no es viable

- **WHEN** un salto de version mayor resulta NO viable sin una rotura desproporcionada
- **THEN** el `design.md` registra esa conclusion con evidencia y la dependencia afectada conserva su pin previo con un seguimiento revisado, sin declarar completada la migracion de esa dependencia
