## Why

La suite de integración PostgreSQL del backend es DESTRUCTIVA contra la base de datos de desarrollo en vivo. `App/Backend/tests/conftest.py::_get_pg_url()` usa por defecto `postgresql+asyncpg://mesa:mesa@localhost:5433/mesa_de_ayuda` — la base de datos de la aplicación del `docker-compose.yml` — y el fixture `pg_schema` ejecuta `drop_all` + `create_all` (y `drop_all` otra vez en el teardown). Como el change `c-29-seam-tests` eliminó el "skip cuando PostgreSQL no está disponible" (directiva de fallo ruidoso), la suite completa del backend ahora SIEMPRE ejercita estos tests destructivos.

Durante la verificación esto destruyó realmente el esquema del compose:

> "There is a verified incident: during verification the compose schema was actually wiped. Incidents 1-23 were lost and the schema had to be restored with `DROP TABLE alembic_version; alembic upgrade head`."

Además, `AGENTS.md` afirma que "backend tests run OFFLINE — the conftest forces SQLite in-memory" y "No Docker required", lo cual es INEXACTO para la porción de integración. El CI está a salvo (usa un service container `postgres:15.5-alpine` dedicado con `TEST_PG_URL` explícito), pero el flujo local puede destruir datos reales.

## What Changes

- **BREAKING (solo en la infraestructura de tests)**: `_get_pg_url()` deja de usar por defecto la base de datos de la aplicación. La resolución por defecto apunta a una base descartable dedicada (`mesa_de_ayuda_test`) o exige `TEST_PG_URL`; NINGÚN camino por defecto puede resolver a `mesa_de_ayuda`.
- La suite de integración provisiona y descarta su propia base descartable: creación vía conexión de mantenimiento (`CREATE DATABASE`) y eliminación al finalizar la sesión (`DROP DATABASE`). Se evalúan y documentan el tradeoff frente a la alternativa de un esquema único por corrida.
- Se agrega una guardia de seguridad: el DDL destructivo solo se ejecuta si el nombre de la base destino NO coincide con el de la base de aplicación, o si se declara una habilitación explícita. Por defecto, un test no puede destruir la base de la aplicación.
- Se conservan TODAS las garantías de `c-29-seam-tests`: PostgreSQL sigue siendo prerrequisito OBLIGATORIO de la suite de integración (fallo ruidoso con mensaje accionable, nunca skip silencioso), el enforcement de `PRAGMA foreign_keys=ON` en SQLite permanece, y los tests de integración PostgreSQL existentes siguen en verde.
- El CI permanece funcional y sin cambios: `TEST_PG_URL` apunta al service container dedicado y la guardia no lo bloquea.
- Se corrige `AGENTS.md` (y cualquier documento que repita la afirmación) para declarar con exactitud que el backend requiere una instancia PostgreSQL para el subconjunto de integración, cómo apuntarlo a una base descartable y cuál es el flujo local seguro.

Fuera de alcance explícito:

- NO se modifica código de producción (`app/**`, `n8n/workflow.json`, `docker-compose.yml`, servicios frontend). El change es exclusivamente infraestructura de tests.
- NO se implementa nada en este change: solo se definen requirements, diseño y tareas.
- NO se incluye alineación con el documento de tesis (la tesis es referencia, no objeto de trabajo).
- NO se cambia el comportamiento del CI ni su configuración.

## Capabilities

### New Capabilities

- `disposable-test-database`: resolución, aprovisionamiento y descarte de la base de datos descartable de la suite de integración; política de URL por defecto que nunca apunta a la base de aplicación; guardia de seguridad que impide DDL destructivo sobre la base de aplicación; compatibilidad con el CI; y documentación del flujo local seguro.

### Modified Capabilities

- `integration-tests-postgresql`: se agrega el requisito de que la suite de integración se ejecute contra la base descartable provista por `disposable-test-database`, conservando el fallo ruidoso ante PostgreSQL ausente y sin afectar la suite SQLite.

## Impact

- **Tests backend**: `App/Backend/tests/conftest.py` (`_get_pg_url()`, `pg_schema`, fixtures `pg_engine`/`pg_session`/`pg_client`).
- **Documentación**: `AGENTS.md` (sección "Env Vars and Secrets" y "Exact Developer Commands" sobre el prerequisito PostgreSQL), y cualquier documento que repita la afirmación de "offline / no Docker".
- **Configuración OPSX**: `openspec/config.yaml` (`testing` describe la estrategia SQLite in-memory; debe reflejar el subconjunto de integración PostgreSQL).
- **Sin cambios de producto**: no se toca `app/**` ni `docker-compose.yml`.
- **CI**: sin cambios; `TEST_PG_URL` explícito al service container dedicado sigue siendo honrado.
- **Gobernanza**: ALTA (toca infraestructura de tests con capacidad de destruir la base de datos de desarrollo; el requisito central es impedir la pérdida de datos).
- **Dependencias**: `c-29-seam-tests` (fallo ruidoso y fixture de esquema), `c-30-bugfix-seams` (suite PostgreSQL en verde de forma aislada).
