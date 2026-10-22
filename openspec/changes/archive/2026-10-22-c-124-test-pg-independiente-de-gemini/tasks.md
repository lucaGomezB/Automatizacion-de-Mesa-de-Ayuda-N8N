## 1. Red de seguridad y reproduccion del RED

- [x] 1.1 Ejecutar la suite PostgreSQL existente como red de seguridad antes de tocar nada: `cd App/Backend && pytest -m integration -q`; registrar el baseline (numero de tests) y confirmar que el unico fallo es `test_patch_incidente_nonexistent_fk_returns_4xx` bajo condiciones de CI. Verificacion: baseline anotado en la bitacora de la sesion
- [x] 1.2 Reproducir el RED bajo condiciones de CI: `cd App/Backend && GEMINI_API_KEY=ci-dummy-key pytest -m integration tests/test_integration_postgresql.py::test_patch_incidente_nonexistent_fk_returns_4xx -q`; confirmar el `TypeError: 'NoneType' object is not subscriptable` en la linea de `created["sector"]["id"]` y la secuencia `classifier_escalate_to_gemini` -> `gemini_retry_terminal` -> `fallback` en los logs. Verificacion: fallo observado y capturado

## 2. Fixture `make_pg_client_with_classifier(pg_engine)`

- [x] 2.1 En `App/Backend/tests/conftest.py`, seccion PostgreSQL (junto a `pg_client` y `seed_pg_catalogs`), agregar la fixture `make_pg_client_with_classifier(pg_engine)`: factoria async que construye un `AsyncClient` con `ASGITransport` sobre `create_app()`, sobrescribiendo `get_db_session` (motor PostgreSQL con commit/rollback por request), `get_incidente_service` (`IncidenteService` con `AsyncMock.classify` devolviendo el `ClasificacionResult` recibido), `get_current_user`, `get_alcance_incidentes` (GLOBAL) y `get_cost_guard` (None), y mockeando `notify_n8n`; replica el patron de `make_client_with_classifier` pero atada a `pg_engine` (decisiones D1 y D4 de `design.md`). Verificacion: la fixture se importa sin error y `pytest --collect-only -q tests/test_integration_postgresql.py` no reporta errores de coleccion
- [x] 2.2 Confirmar que la fixture drena las tareas fire-and-forget (`await asyncio.sleep(0)` antes de salir del contexto) y que no introduce ninguna dependencia del clasificador real ni de red externa. Verificacion: revision del codigo de la fixture contra los overrides de `pg_client`

## 3. Test determinista `test_patch_incidente_nonexistent_fk_returns_4xx`

- [x] 3.1 Reescribir `test_patch_incidente_nonexistent_fk_returns_4xx` en `App/Backend/tests/test_integration_postgresql.py` para recibir `make_pg_client_with_classifier` y `seed_pg_catalogs`, construir `ClasificacionResult(sector_predicho="Sistemas", confianza=0.95, etapa="deterministic", requiere_revision_humana=False)` (decision D2) y crear el incidente dentro del contexto de la factoria; conservar EXACTAMENTE las dos aserciones: el `PATCH` con `estado_id=99999` devuelve 4xx y el sector previo del incidente no cambia (decision D3). Verificacion: lectura del diff confirma que no se relaja ninguna asercion y no se agrega `skip`/`xfail`
- [x] 3.2 GREEN bajo condiciones de CI: `cd App/Backend && GEMINI_API_KEY=ci-dummy-key pytest -m integration tests/test_integration_postgresql.py::test_patch_incidente_nonexistent_fk_returns_4xx -q`; debe pasar. Verificacion: salida `1 passed`
- [x] 3.3 TRIANGULACION (clave real local): `cd App/Backend && pytest -m integration tests/test_integration_postgresql.py::test_patch_incidente_nonexistent_fk_returns_4xx -q` sin la variable de entorno; debe pasar de forma identica. Verificacion: salida `1 passed` en ambos entornos

## 4. Verificacion global

- [x] 4.1 Correr la suite PostgreSQL completa bajo condiciones de CI: `cd App/Backend && GEMINI_API_KEY=ci-dummy-key pytest -m integration -q`; no debe haber fallos ni regresiones en los demas tests que usan `pg_client` (`test_patch_updates_estado`, `test_estadisticas_tendencias_200_on_postgresql`, `test_estadisticas_resumen_200_on_postgresql`, `test_c90_prioridad_critica_integration.py::test_cuenta_sin_empleado_critica_403`). Verificacion: salida sin `failed`
- [x] 4.2 Correr el subconjunto SQLite (offline) para descartar regresiones por la nueva fixture: `cd App/Backend && pytest -m "not integration" -q`; verificar que sigue en verde. Verificacion: salida sin `failed`
- [x] 4.3 Lint: `cd App/Backend && ruff check .`; sin hallazgos. Verificacion: salida limpia
- [x] 4.4 Confirmar que el cambio se limita a tests: `git status --short` muestra unicamente `App/Backend/tests/conftest.py` y `App/Backend/tests/test_integration_postgresql.py` (mas los artefactos del change). Verificacion: ningun archivo bajo `App/Backend/app/`, migraciones ni `docs/openapi.json` modificado
