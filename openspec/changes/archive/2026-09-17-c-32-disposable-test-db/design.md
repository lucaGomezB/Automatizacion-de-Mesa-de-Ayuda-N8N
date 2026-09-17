## Context

Ver `proposal.md — Why` para la motivación. Estado actual relevante del código:

- `App/Backend/tests/conftest.py::_get_pg_url()` resuelve `TEST_PG_URL` o, en su defecto, `postgresql+asyncpg://mesa:mesa@localhost:5433/mesa_de_ayuda`, que es la base de la aplicación del `docker-compose.yml`.
- `pg_schema` (scope session) es el único dueño del DDL: `SELECT 1` de probe, luego `drop_all`, luego `create_all`, siembra el catálogo una sola vez, y en el teardown `drop_all`. El probe falla ruidosamente (c-29 D2). `pg_engine`, `pg_session`, `pg_client` y `seed_pg_catalogs` derivan de `pg_schema` y no aplican DDL.
- El engine SQLite (`engine`) registra un listener `connect` que ejecuta `PRAGMA foreign_keys=ON` (c-29 D3). Eso no se toca.
- `docker-compose.yml` define `POSTGRES_USER: mesa`, `POSTGRES_PASSWORD: mesa`, `POSTGRES_DB: mesa_de_ayuda`, puerto host `5433`. Las credenciales de desarrollo son superusuario del servidor, por lo que pueden `CREATE DATABASE`/`DROP DATABASE`.
- El CI (`.github/workflows/ci.yml`) usa un service container `postgres:15.5-alpine` con `POSTGRES_DB: mesa_de_ayuda` y define `TEST_PG_URL: postgresql+asyncpg://mesa:mesa@localhost:5432/mesa_de_ayuda` en el step de integración. La `DATABASE_URL` del job es un dummy (`ci_dummy`) que nunca conecta.
- `AGENTS.md` afirma que el backend corre offline y que no requiere Docker para los tests; la sección de testing de `openspec/config.yaml` solo menciona SQLite in-memory.

Restricción central: la suite debe seguir funcionando en el CI sin cambios, conservar el fallo ruidoso de c-29, y hacer imposible que una corrida por defecto destruya `mesa_de_ayuda`.

## Goals / Non-Goals

**Goals:**

- Aislar físicamente el DDL destructivo de la base de datos de la aplicación.
- Hacer que ningún camino de resolución por defecto produzca la base de la aplicación.
- Agregar una guardia determinista que aborte el DDL destructivo cuando el destino coincida con la base de la aplicación.
- Mantener intacto el contrato de la suite: prerrequisito obligatorio (fallo ruidoso), aislamiento entre tests, catálogo sembrado, tests PG existentes en verde.
- Dejar la documentación de desarrollo consistente con la realidad operativa.

**Non-Goals:**

- Cambiar el CI o `docker-compose.yml`.
- Cambiar código de producción.
- Introducir un runner de base de datos nuevo (testcontainers, etc.) o dependencias nuevas.
- Corregir defectos de producto descubiertos por la suite.
- Cambiar el shape del esquema o las migraciones Alembic.

## Decisions

### D1 — Estrategia de descarte: base de datos dedicada (elegida) frente a esquema único por corrida

Se aprovisiona una base de datos dedicada y efímera como destino de la suite. La fixture de sesión se conecta a la base de mantenimiento (`postgres`) del mismo servidor con las credenciales provistas, ejecuta `CREATE DATABASE` al inicio y `DROP DATABASE` al final. Todo el DDL destructivo ocurre dentro de esa base.

- **Razón**: el modo de falla a eliminar es "una corrida por defecto destruye la base de la aplicación". Compartir la base —aunque sea con un `search_path` distinto— deja viva la superficie que causó el incidente: un `search_path` mal aplicado, un `DROP` sin calificar, o una conexión que cae en `public` alcanzan los objetos de la aplicación. Una base separada hace la separación FÍSICA, no convencional.
- **Alternativa considerada — esquema único por corrida sobre la base de la aplicación** (por ejemplo `CREATE SCHEMA test_<uuid>; SET search_path`): ventaja, no requiere privilegio `CREATE DATABASE` ni conexión de mantenimiento, y varias corridas en paralelo quedan aisladas. Desventaja decisiva: la conexión sigue siendo a la base de la aplicación y el aislamiento depende por completo de que `search_path` se aplique correctamente en TODAS las conexiones (incluidas las que abre el cliente ASGI y los engines efímeros). Es exactamente el tipo de supuesto frágil que produjo el incidente; un objeto creado sin calificar o un `DROP SCHEMA ... CASCADE` mal dirigido puede afectar la aplicación. Se descarta.
- **Alternativa considerada — truncar tablas en lugar de `drop_all`**: reduce el daño pero sigue apuntando a la base de la aplicación y no crea una frontera. Se descarta.
- **Trade-off**: `DROP DATABASE` no puede ejecutarse con conexiones activas a la base descartable, por lo que el teardown debe disponer todos los engines antes de intentar el drop (ver D4). Además, `CREATE DATABASE` exige privilegio y una base de mantenimiento alcanzable; el fallback de D4 cubre el caso de privilegio insuficiente sin comprometer la seguridad.

### D2 — Nombre de la base descartable: `mesa_de_ayuda_test` fijo

La base descartable por defecto se llama `mesa_de_ayuda_test`, derivada del prefijo de la base de la aplicación más el marcador `_test`.

- **Razón**: el nombre fijo es predecible, fácil de inspeccionar y hace evidente el marcador `_test` que la guardia de D3 puede exigir. El sufijo único por corrida agrega complejidad (la URL por defecto tendría que componerse en runtime) sin resolver un problema real: la suite se ejecuta de a una por máquina/CI.
- **Trade-off**: dos corridas simultáneas contra el mismo servidor colisionan sobre el mismo nombre. Mitigación: el nombre es configurable vía `TEST_PG_URL` para entornos que necesiten paralelismo; el flujo documentado es secuencial.

### D3 — Guardia: comparar el nombre de la base destino contra el de la aplicación

Antes de aplicar DDL destructivo, la suite compara el nombre de base destino con el de la base de la aplicación (derivada de `DATABASE_URL`). Si coinciden, aborta con mensaje accionable y exit code distinto de cero, salvo que el operador declare explícitamente `TEST_PG_ALLOW_APP_DB=1` (habilitación inequívoca para entornos dedicados y efímeros).

- **Razón**: la comparación por NOMBRE de base —no por host/puerto— es la que atrapa el incidente: el desarrollo local resuelve `mesa_de_ayuda` contra `localhost:5433`, y un `TEST_PG_URL` explícito hacia la app también lleva ese nombre. La guardia es independiente de que el default se haya corregido: aun si alguien fija `TEST_PG_URL` a la base de la aplicación, la suite se niega.
- **Compatibilidad con CI**: en el CI, `DATABASE_URL` es el dummy `ci_dummy` y `TEST_PG_URL` apunta a `mesa_de_ayuda` en el service container. Los nombres difieren, por lo que la guardia NO bloquea el CI y no necesita la habilitación explícita. Esto mantiene el CI sin cambios.
- **Alternativa considerada — exigir siempre un marcador `_test` en el nombre**: rompería el CI, cuyo contenedor usa `mesa_de_ayuda`. La comparación contra la base de la aplicación logra el objetivo sin ese costo.
- **Alternativa considerada — solo corregir el default sin guardia**: deja el footgun activo ante un `TEST_PG_URL` mal copiado. Se descarta.

### D4 — Ciclo de vida del aprovisionamiento y orden del teardown

La fixture de sesión que ya posee el esquema (`pg_schema`) pasa a apoyarse en un paso de aprovisionamiento previo: crear la base descartable vía conexión de mantenimiento (base `postgres`, mismo host/puerto/credenciales que el destino, reemplazando el nombre de base de la URL por `postgres`), luego ejecutar `drop_all` + `create_all` + seed sobre la base descartable, y en el teardown `drop_all` seguido de `DROP DATABASE`.

- **Razón**: mantener el DDL en una única fixture de session conserva el aprendizaje de c-29 (evitar el bloqueo de locks por test) y concentra la responsabilidad destructiva en un solo punto auditable.
- **Orden**: `DROP DATABASE` requiere que ninguna conexión permanezca abierta a la base descartable. El teardown debe disponer los engines (`pg_engine` por test ya lo hace; el engine efímero del setup también) antes del drop. El `drop_all` previo es opcional si sigue un `DROP DATABASE`, pero se conserva por claridad y por el caso de fallback.
- **Fallback de aprovisionamiento**: si `CREATE DATABASE` no es posible (sin privilegio o sin base de mantenimiento) y el destino resuelto NO es la base de la aplicación, la suite continúa con el ciclo de vida de esquema sobre el destino resuelto y emite una advertencia visible. Nunca continúa si el destino es la base de la aplicación.
- **Alternativa considerada — una fixture separada `pg_database` de scope session que `pg_schema` consume**: más explícita en responsabilidades, pero agrega un fixture cuyo único consumidor es `pg_schema`. Se prefiere el paso de aprovisionamiento dentro de `pg_schema` salvo que la implementación revele necesidad de reutilización.

### D5 — Preservación explícita de las garantías de c-29

El change no relaja ninguna garantía previa:

- El probe de conexión sigue fallando ruidosamente, con la URL efectiva y el comando de remediación; nunca `pytest.skip`.
- El listener `PRAGMA foreign_keys=ON` del engine SQLite queda intacto.
- `asyncio_default_fixture_loop_scope` y el scope de función de `pg_engine` quedan intactos.
- Los tests de integración existentes deben seguir pasando contra la base descartable.

- **Razón**: el incidente ocurrió justamente porque una suite destructiva se volvió alcanzable por defecto; si además se debilitara el fallo ruidoso, el fix introduciría un falso verde. La red de seguridad de c-29 (fallo ruidoso + baseline de tests) se conserva.

### D6 — Corrección documental acotada

Se corrigen `AGENTS.md` (secciones de comandos y de env/tests) y la descripción de testing de `openspec/config.yaml`. Se revisan y corrigen, si repiten la afirmación, `CLAUDE.md` y `README.md`.

- **Razón**: la afirmación "backend tests run OFFLINE / No Docker required" es la que hace que un desarrollador ejecute `pytest` completo sin saber que disparará el subconjunto destructivo de integración. La corrección documental es parte del fix, no un extra.
- **Contenido**: declarar que el subconjunto `integration` requiere PostgreSQL; documentar el destino descartable y el comando del flujo local seguro; acotar la afirmación de offline a la suite SQLite.

## Risks / Trade-offs

- **[`DROP DATABASE` falla por conexiones activas]** → disponer todos los engines antes del drop; si el drop falla, la suite reporta la base residual y el comando manual de limpieza.
- **[Privilegio insuficiente para `CREATE DATABASE`]** → fallback de D4 con advertencia, siempre que el destino no sea la base de la aplicación; alternativa documentada: definir `TEST_PG_URL` a una instancia donde el usuario pueda crear bases.
- **[La guardia bloquea un entorno legítimo cuyo nombre casualmente coincide]** → habilitación explícita `TEST_PG_ALLOW_APP_DB=1` para entornos dedicados y efímeros, documentada como excepción.
- **[Colisión de nombre entre corridas paralelas]** → flujo documentado secuencial; `TEST_PG_URL` permite aislar entornos paralelos.
- **[Expectativa de que el default eluda la guardia]** → no es un riesgo sino el objetivo: la guardia es independiente del default y no puede auto-habilitarse.
- **[Docs desincronizadas respecto del código]** → los scenarios de documentación exigen que `AGENTS.md` y `openspec/config.yaml` reflejen la realidad; se incluyen tareas de verificación.

## Migration Plan

1. Registrar la línea base de conteos de la suite (SQLite + integración) antes de tocar `conftest.py` (red de seguridad de c-29).
2. Reparar la resolución de la URL: `_get_pg_url()` → `TEST_PG_URL` o `mesa_de_ayuda_test`; nunca la base de la aplicación.
3. Agregar la guardia de D3 y el aprovisionamiento/descarte de D4 en `pg_schema`.
4. Verificar con PostgreSQL levantado que la suite `-m integration` pasa contra la base descartable y que la base de la aplicación queda intacta (inspección de conteo de incidentes antes/después).
5. Verificar el camino de fallo: PostgreSQL ausente → fallo ruidoso; destino igual a la app → aborto.
6. Corregir la documentación (D6).
7. Registrar la línea base posterior.
8. Rollback: revertir `conftest.py` y los documentos; la base descartable se elimina sola en el teardown. No hay migración de datos ni cambio de producción.

## Open Questions

Ninguna que afecte specs, enfoque o desglose de tareas.
