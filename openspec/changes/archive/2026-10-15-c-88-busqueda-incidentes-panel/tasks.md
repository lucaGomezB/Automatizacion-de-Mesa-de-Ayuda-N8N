## 1. Backend: busqueda por texto libre (TDD)

- [x] 1.1 Escribir los tests unitarios (SQLite) de IS-001: coincidencia parcial, case-insensitive, busqueda por id numerico, combinacion AND con estado/sector/prioridad, lista vacia sin coincidencias, `q` corto/vacio ignorado y comodines (`%`, `_`) tratados como literales. Verificar que fallan en RED porque `q` aun no existe.
- [x] 1.2 Implementar el helper de escape de comodines LIKE (escapa `\`, `%`, `_`) con sus tests unitarios directos y verificar GREEN del helper.
- [x] 1.3 Agregar `q` a `IncidenteRepository.list_filtered` como condicion OR (`descripcion_pseudonimizada` ILIKE parcial OR `id ==` cuando es numerico), usando bind de parametros y el helper de escape. Verificar GREEN de 1.1.
- [x] 1.4 Propagar `q` por `IncidenteService.list_incidentes` y exponerlo como query param opcional (`max_length=200`) en `GET /api/v1/incidentes`; verificar con un test de API que `GET /api/v1/incidentes/?q=...` filtra y que sin `q` el resultado no cambia.
- [x] 1.5 Escribir y verificar los tests de IS-002: alcance PROPIO no devuelve incidentes ajenos aunque `q` coincida, alcance VACIO devuelve lista vacia, y un termino presente solo en `descripcion_original` no devuelve el incidente.
- [x] 1.6 Escribir y verificar un test de integracion PostgreSQL (`@pytest.mark.integration`) que replica la busqueda contra la base desechable, y correr `pytest -m integration`.

## 2. Migracion: indice trigram

- [x] 2.1 Crear la migracion Alembic `020` (`down_revision = "019"`) que ejecuta `CREATE EXTENSION IF NOT EXISTS pg_trgm` y crea un indice GIN `gin_trgm_ops` sobre `descripcion_pseudonimizada`; el `downgrade` elimina el indice. Verificar `alembic upgrade head` y `alembic downgrade 019` contra la base desechable.
- [x] 2.2 Verificar que el subset de unidad no depende de la migracion ni de `pg_trgm`: correr `pytest -m "not integration"` y confirmar que pasa sin PostgreSQL.

## 3. Contrato OpenAPI

- [x] 3.1 Regenerar `docs/openapi.json` desde la app y verificar `pytest tests/test_openapi_sync.py -v`.
- [x] 3.2 Agregar o ajustar un test que confirme que el parametro `q` aparece en el esquema del endpoint de listado y verificar GREEN.

## 4. Frontend: barra de busqueda (TDD)

- [x] 4.1 Agregar `q?: string` a `IncidenteListParams` y verificar el typecheck (`npm run build` en `App/Frontend`).
- [x] 4.2 Escribir los tests del hook `useDebouncedValue` con fake timers (el valor se actualiza recien tras 300 ms), verificar RED, implementar el hook y verificar GREEN.
- [x] 4.3 Escribir y verificar los tests de `useIncidentes`/panel que comprueban que `q` viaja al servicio `listarIncidentes` y que cambiar el termino reinicia la paginacion a la primera pagina.
- [x] 4.4 Implementar el input de busqueda en `Administracion/index.tsx` con debounce de 300 ms, minimo 2 caracteres, combinado con los filtros existentes y reinicio de pagina; verificar con tests de componente (Testing Library).
- [x] 4.5 Ajustar el copy del `EmptyState` de `TicketsTable` para contemplar busqueda y filtros; verificar el test de estado vacio (lista vacia muestra mensaje neutro y no estado de error).
- [x] 4.6 Verificar la limpieza: el control "Limpiar filtros" vacia tambien `q` y vuelve a la primera pagina, cubierto por test.

## 5. Verificacion final

- [x] 5.1 Correr la verificacion backend completa en `App/Backend`: `ruff check .`, `pytest -m "not integration"` y `pytest -m integration`.
- [x] 5.2 Correr la verificacion frontend en `App/Frontend`: `npm run test` y `npm run lint`.
- [x] 5.3 Validar el change: `openspec validate c-88-busqueda-incidentes-panel --strict`.
