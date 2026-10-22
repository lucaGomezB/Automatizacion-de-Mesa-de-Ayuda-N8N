## Why

`main` está en rojo en CI por un único test de integración PostgreSQL: `test_patch_incidente_nonexistent_fk_returns_4xx` (`App/Backend/tests/test_integration_postgresql.py:528`) falla con `TypeError: 'NoneType' object is not subscriptable` al leer `created["sector"]["id"]`. La causa: el test crea el incidente vía API y la fixture `pg_client` inyecta el `HybridClassifier` REAL (solo `notify_n8n` está mockeado). `create_and_classify` asigna el sector desde el resultado del clasificador, no desde el payload. Con `GEMINI_API_KEY=ci-dummy-key` el determinista no encuentra señal, escala a Gemini, la llamada falla (`gemini_retry_terminal ClientError`) y el pipeline cae a `fallback` con `sector_predicho=None`; por eso `created["sector"]` es `None`. Localmente pasa porque `App/Backend/.env` tiene una clave real. La suite queda dependiente de un servicio externo, lo que contradice el aislamiento que la suite SQLite ya aplica.

## What Changes

- Nueva fixture `make_pg_client_with_classifier(pg_engine)` en `App/Backend/tests/conftest.py` (sección PostgreSQL): factoría de cliente HTTP respaldado por PostgreSQL que inyecta el clasificador como doble determinista, replicando `make_client_with_classifier` pero atada a `pg_engine`.
- `test_patch_incidente_nonexistent_fk_returns_4xx` usa esa factoría con un `ClasificacionResult` cuyo `sector_predicho` es un sector sembrado (`"Sistemas"`), de modo que el incidente obtiene un sector no nulo y determinista.
- Sin cambios de producción. Sin debilitar aserciones, sin `skip`/`xfail`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `backend-integration-tests`: se agrega un requisito de aislamiento del clasificador en la suite de integración PostgreSQL, con escenarios de sector determinista y de independencia de Gemini bajo clave ficticia.

## Impact

- `App/Backend/tests/conftest.py`: nueva fixture (sección PostgreSQL, junto a `pg_client`/`seed_pg_catalogs`).
- `App/Backend/tests/test_integration_postgresql.py`: reescritura de un único test (setup + lectura del sector).
- Sin cambios en `app/` (producción), migraciones, OpenAPI ni categorías canónicas.

## Rollback

Revertir los dos archivos de test con `git checkout <commit-previo> -- App/Backend/tests/conftest.py App/Backend/tests/test_integration_postgresql.py`. El cambio no toca producción, por lo que no hay migración ni despliegue que deshacer.

## Success Criteria

- [ ] `GEMINI_API_KEY=ci-dummy-key pytest -m integration tests/test_integration_postgresql.py::test_patch_incidente_nonexistent_fk_returns_4xx` pasa (condiciones de CI).
- [ ] El mismo test pasa localmente con la clave real de `App/Backend/.env`.
- [ ] Las aserciones originales se conservan: PATCH con `estado_id` inexistente devuelve 4xx y el incidente mantiene su sector previo.
- [ ] Ningún test de la suite PostgreSQL contacta la API real de Gemini para crear incidentes a través de la nueva factoría.
