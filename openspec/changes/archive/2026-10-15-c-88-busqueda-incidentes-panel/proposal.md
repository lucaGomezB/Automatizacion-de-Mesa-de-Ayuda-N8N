## Why

El Panel de Administracion solo permite filtrar incidentes por listas cerradas (estado, sector, prioridad). Encontrar un incidente por su contenido obliga a recorrer paginas a mano, que se vuelve inviable a medida que crece el historico. Se necesita una busqueda por texto libre para localizar incidentes por su descripcion o por su numero.

## What Changes

- Backend: nuevo parametro de consulta `q` en `GET /api/v1/incidentes` que realiza una busqueda parcial case-insensitive contra `descripcion_pseudonimizada` y, cuando `q` es numerico, coincidencia exacta por `id`. Se combina con los filtros existentes con AND y respeta el alcance de visibilidad por rol.
- Backend: la busqueda es parametrizada (ILIKE) con escape de comodines LIKE; nunca consulta `descripcion_original` (PII cifrada) ni saltea el alcance.
- Frontend: barra de busqueda en el Panel de Administracion, con debounce, minimo de caracteres, integrada a los filtros y a la paginacion (reinicio a pagina 1), cableada por `IncidenteListParams` -> `useIncidentes` -> `listarIncidentes`, con estado vacio cuando no hay resultados.
- Infra: migracion Alembic `020` (`down_revision = "019"`) que habilita `pg_trgm` y crea un indice GIN trigram sobre `descripcion_pseudonimizada` para sostener la busqueda por subcadena.
- Contrato: regenerar `docs/openapi.json` (guarda `tests/test_openapi_sync.py`).

No hay cambios rupturistas: `q` es opcional y su ausencia conserva el comportamiento actual.

## Capabilities

### New Capabilities

- `incident-search`: contrato de busqueda por texto libre en el listado de incidentes (parametro `q`, campos buscados, composicion con filtros y alcance, seguridad de la consulta).
- `frontend-incident-search`: comportamiento de la barra de busqueda del Panel de Administracion y su cableado por la capa de datos del frontend.

### Modified Capabilities

<!-- Ninguna: no cambian requisitos de capacidades existentes; la busqueda se agrega como condicion AND sin alterar visibilidad ni filtros vigentes. -->

## Impact

- Backend: `app/routes/incidentes.py` (parametro `q`), `app/services/incidente_service.py` (`list_incidentes`), `app/repositories/incidente_repository.py` (`list_filtered`), migracion Alembic nueva `020`.
- Contrato: `docs/openapi.json`.
- Frontend: `src/types/incidente.ts`, `src/services/incidentesService.ts`, `src/hooks/useIncidentes.ts`, `src/pages/Administracion/index.tsx` (y su tabla de tickets para el estado vacio).
- Tests: suite backend (unidad SQLite + integracion PostgreSQL) y suite frontend (Vitest).
- Dependencia blanda: c-86 (`gestion_incidentes`, alcance por sector). La busqueda se agrega como condicion ortogonal al alcance para componer con ese modelo sin asumir GLOBAL.
