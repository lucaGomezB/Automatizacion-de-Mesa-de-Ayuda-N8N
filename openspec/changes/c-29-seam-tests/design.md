## Context

Ver `proposal.md — Why` para la motivación. El estado actual relevante:

- Las tres suites están verdes y ese verde es engañoso: los defectos viven en costuras que ningún test ejercita.
- La suite PostgreSQL de integración (`App/Backend/tests/test_integration_postgresql.py`, marker `integration`) NUNCA corrió en verde. Sin PostgreSQL, el fixture `pg_engine` llama `pytest.skip` y la suite reporta éxito con N skips; con PostgreSQL, falla con `RuntimeError: ... got Future ... attached to a different loop`.
- `pg_engine` en `tests/conftest.py` es `@pytest_asyncio.fixture(scope="session")`. `pytest.ini` declara `asyncio_mode = auto` pero NO declara `asyncio_default_fixture_loop_scope`. La versión pinneada es `pytest-asyncio==0.24.0`.
- El engine SQLite de tests (`TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"`) NO habilita `PRAGMA foreign_keys=ON`; por defecto SQLite lo tiene OFF, por lo que las violaciones de FK pasan desapercibidas.
- `App/Backend/tests/test_n8n_workflow.py` tiene ~1510 líneas de pruebas estructurales del JSON exportado, pero ninguna verifica semántica runtime (autenticación HTTP, `canal_origen_id`, índices del Switch, acoplamiento del agente al modelo de lenguaje, etc.).
- `docker-compose.yml` define `VITE_API_BASE_URL: https://localhost/api/v1` bajo `environment` del servicio `frontend`, pero el contenedor sirve un `dist/` precompilado por Vite: las variables `VITE_*` se resuelven en BUILD time, no en runtime. `App/Frontend/Dockerfile` no declara `ARG VITE_API_BASE_URL`. Además `App/Frontend/src/services/api.ts` concatena `${API_BASE_URL}/api/v1`, produciendo `/api/v1/api/v1` con el valor actual.
- Las rutas del cliente frontend usan `/incidentes` (sin trailing slash) mientras la especificación OpenAPI declara `/api/v1/incidentes/`; a través del proxy nginx esto dispara un 307.

### Pre-finding crítico: la suite PostgreSQL nunca corrió en verde

Diagnóstico de la causa raíz del `RuntimeError: ... got Future ... attached to a different loop`:

- `asyncpg` ata cada conexión al event loop en el que fue creada; no admite reutilizarse desde otro loop.
- `pg_engine` es un fixture async de `scope="session"`. Con `pytest-asyncio==0.24.0` y `asyncio_mode = auto`, el loop por defecto de los fixtures async y el loop por defecto de los tests no están alineados de forma explícita (la opción `asyncio_default_fixture_loop_scope` está sin declarar).
- Resultado: el engine crea conexiones asyncpg en un loop y los tests las consumen en otro. Sin PostgreSQL el problema queda oculto por el `pytest.skip`; con PostgreSQL se manifiesta.
- Consecuencia metodológica: la suite reportó "éxito" durante todo el proyecto sin haber validado una sola vez el comportamiento específico de PostgreSQL (FK, cascadas, `Numeric`, `TIMESTAMPTZ`, índices). Ese verde falso es la razón por la que este change existe.

## Goals / Non-Goals

**Goals:**

- Hacer que la suite PostgreSQL de integración corra y pase de verdad, con un único event loop consistente entre fixtures y tests.
- Eliminar todo skip silencioso ante prerrequisitos obligatorios: la ausencia de PostgreSQL debe fallar con mensaje accionable.
- Hacer observable el enforcement de FK en SQLite para que los defectos de integridad referencial aparezcan en la suite rápida.
- Codificar como tests (que HOY FALLAN) los contratos runtime de N8N, los endpoints de estadísticas sobre PostgreSQL, el PATCH con FK inexistente y la configuración frontend/Docker.
- Registrar una línea base (safety net) de conteos de tests para demostrar que la infraestructura no rompió lo que ya pasaba.

**Non-Goals:**

- Corregir los defectos que los tests descubren. Este change es fase RED: los tests codifican el comportamiento correcto y fallan; la corrección es un change posterior.
- Modificar código de producción (`app/**`, `n8n/workflow.json`, `docker-compose.yml`, `App/Frontend/Dockerfile`, servicios frontend).
- Alinear el proyecto con el documento de tesis.
- Convertir la suite PostgreSQL en parte del camino rápido por defecto; sigue siendo opt-in con `-m integration`.

## Decisions

### D1 — Alinear el loop de fixtures async y tests al scope de función (pytest-asyncio 0.24)

Se declara `asyncio_default_fixture_loop_scope` de forma explícita en `pytest.ini` y se convierte `pg_engine` a scope de función (junto con los fixtures que dependen de él), de modo que el engine, sus conexiones asyncpg y cada test vivan en el MISMO evento de loop. Se mantiene `asyncio_mode = auto`.

- **Razón**: el modo determinista y de menor radio de impacto es que fixture y test compartan exactamente el scope de loop por defecto (función). Un fixture de scope session con un test de scope función nunca puede garantizar la coincidencia de loop sin forzar un loop de session global.
- **Alternativas consideradas**: (a) declarar el fixture como `scope="session", loop_scope="session"` y forzar además que los tests corran en un loop de session mediante un override del fixture `event_loop` — funciona pero cambia la semántica de loop de TODA la suite SQLite, con riesgo de efectos colaterales y mayor superficie de regresión; (b) no declarar nada y solo reducir el scope del fixture — silencia el error de loop pero deja la configuración implícita y dependiente del default de la librería. Se prefiere (D1) por ser explícita y acotada.
- **Trade-off**: recrear el engine y el schema por test agrega costo; aceptable para ~30 tests de integración.

### D2 — Fallo ruidoso y accionable en lugar de skip

El probe de conexión de `pg_engine` deja de llamar `pytest.skip`. Si PostgreSQL no es alcanzable, se levanta un fallo con un mensaje que nombra la URL efectiva (`_get_pg_url()`) y el comando de remediación `docker compose up -d postgres`. La suite SQLite (sin marker `integration`) no debe verse afectada.

- **Razón**: PostgreSQL es un prerrequisito obligatorio de la suite de integración. Saltar convierte un fallo de infraestructura en un falso verde y fue la causa directa de que la suite nunca corriera.
- **Alternativas consideradas**: mantener el skip pero con `-W error` o un resumen al final — sigue reportando éxito y puede ignorarse; no cierra la costura.

### D3 — Enforcement de FK en SQLite vía listener de conexión

Se registra un listener sobre el evento `connect` del pool del engine SQLite que ejecuta `PRAGMA foreign_keys=ON` en cada conexión nueva. El listener se registra sobre el engine compartido (`engine`), que es el mismo que consumen `db_session`, `client`, `make_client_with_classifier` y `seed_catalogs`.

- **Razón**: aiosqlite/SQLAlchemy no habilita FK por URL de forma confiable; el listener garantiza el PRAGMA en toda conexión, incluida la que abre el cliente ASGI por request.
- **Alternativas consideradas**: `?foreign_keys=on` en la URL — dependiente del driver y frágil; ejecutar el PRAGMA una sola vez tras crear el engine — insuficiente si el pool abre conexiones nuevas.
- **Efecto esperado**: los tests existentes que hoy pasan por FK no aplicadas pueden empezar a fallar. Eso es el OBJETIVO (exponer la costura), no una regresión; se reporta como hallazgo RED y no se debilita ningún test para forzar el verde.

### D4 — Pruebas de contrato runtime de N8N como tests estructurales extendidos

Se extiende `App/Backend/tests/test_n8n_workflow.py` reutilizando sus helpers `load_workflow()` e `index_nodes()`. Las nuevas pruebas verifican semántica runtime sobre el JSON exportado, sin instancia N8N:

- Autenticación del nodo `httpRequest` que apunta a `/api/v1/incidentes`.
- Presencia de `canal_origen_id` en el `body` del nodo HTTP.
- Switch en modo `expression`: la salida SHALL ser un índice numérico 0-based de rama, y los campos referenciados SHALL existir en el schema de respuesta real del backend o en un nodo aguas arriba accesible.
- Cada nodo `@n8n/n8n-nodes-langchain.agent` SHALL tener conexión `ai_languageModel` y su prompt SHALL interpolar el payload del trigger.
- El `microsoftOutlookTrigger` SHALL exponer el cuerpo del correo que lee el validador.
- Un `webhook` con `responseMode: responseNode` SHALL tener un `respondToWebhook` alcanzable.
- Nodos que requieren credenciales SHALL declararlas.

- **Razón**: el JSON actual incumple todos estos puntos (el HTTP no declara autenticación; el body sólo tiene `descripcion` y `prioridad`; el Switch devuelve `$json.canal_origen`, que no existe en la respuesta del backend; el agente sólo tiene conexión `ai_memory`; el prompt es estático; etc.), por lo que los tests nacen en rojo. Ese rojo es la codificación del contrato correcto.
- **Alternativas consideradas**: validar con una instancia N8N real — descartado por costo y no determinismo; el proyecto ya adoptó la verificación estructural del JSON exportado.

### D5 — Pruebas de integración PostgreSQL para estadísticas y PATCH con FK inexistente

Se agregan tests con marker `integration` que usan `pg_client` + `seed_pg_catalogs`:

- `GET /api/v1/estadisticas/tendencias` (por día y por mes) y `/resumen` SHALL responder 200 con datos. Hoy `/tendencias` responde 500 en PostgreSQL porque `app/services/estadisticas_service.py` usa `func.strftime`, función SQLite-only.
- `PATCH /api/v1/incidentes/{id}` con `estado_id`/`sector_id` inexistente SHALL responder 4xx. Hoy, con el enforcement de FK de PostgreSQL, la violación escala como error de servidor (500); con PRAGMA off en SQLite el defecto quedaba oculto.

- **Razón**: son las dos costuras del backend que la suite verde no veía. El test de estadísticas ancla el soporte real de PostgreSQL; el de PATCH ancla el manejo de FK inválida en el borde HTTP.
- **Nota**: no se corrige `func.strftime` ni el manejo del PATCH; solo se codifica el comportamiento correcto como test en rojo.

### D6 — Pruebas de configuración frontend/Docker

Se agregan pruebas de configuración que leen archivos sin construir imágenes:

- `docker-compose.yml`: el servicio `frontend` SHALL reenviar `VITE_API_BASE_URL` bajo `build.args` (no sólo `environment` de runtime), y el valor NO SHALL terminar en `/api/v1`.
- `App/Frontend/Dockerfile`: SHALL declarar `ARG VITE_API_BASE_URL` antes de `npm run build`.
- Alineación de rutas: las rutas del cliente frontend SHALL coincidir con `docs/openapi.json` (trailing slash incluido), evitando el 307.

- **Ubicación decidida**: las aserciones sobre `docker-compose.yml` y el Dockerfile viven en un módulo de tests del backend (lectura de archivos y YAML, sin red). La alineación de rutas cliente/OpenAPI vive en la suite Vitest del frontend, leyendo `docs/openapi.json`.
- **Razón**: mantiene cada aserción en la suite que ya domina ese artefacto (backend estructural vs. Vitest de servicios) y evita introducir un runner nuevo.
- **Alternativas consideradas**: poner todo en Vitest — descartado por el acceso a YAML y a la raíz del repo desde el entorno DOM; poner todo en Python — descartado porque la capa cliente es responsabilidad de la suite frontend.

### D7 — Línea base de tests como red de seguridad

Antes de tocar `conftest.py`/`pytest.ini` se registra el conteo de passed/skipped de backend y frontend; se vuelve a registrar después. La diferencia se documenta. Cualquier test que pase de verde a rojo por una costura recién expuesta se reporta como hallazgo RED intencional, nunca se silencia ni se debilita.

- **Razón**: habilita distinguir "rompí algo" de "destapé un defecto preexistente", que es exactamente el propósito del change.

## Risks / Trade-offs

- **[Más tests rojos de los esperados al habilitar FK en SQLite]** → es el objetivo del change. Mitigación: reportarlos como hallazgos RED con su causa raíz; NO debilitar aserciones para alcanzar verde.
- **[El cambio de scope de `pg_engine` a función ralentiza la suite de integración]** → recrea engine y schema por test. Mitigación: alcance acotado (~30 tests); si el costo crece, mover la creación de schema a un fixture sync de scope session y mantener sólo las conexiones async por test.
- **[Pruebas de contrato N8N acopladas a supuestos de schema]** → si un campo esperado no existe realmente en la respuesta del backend, el test sería incorrecto. Mitigación: derivar los nombres de campos de `docs/openapi.json` y del schema `IncidenteRead`, no de memoria.
- **[Pruebas de Docker sobre-constriñen el formato]** → asertar formato exacto del YAML/`Dockerfile` rompe ante reformateos legítimos. Mitigación: verificar presencia y orden semántico (build args, ARG antes del build), no formato.
- **[Dependencia de PostgreSQL en CI]** → la suite requiere el servicio. Mitigación: documentar `docker compose up -d postgres` en el mensaje de fallo y en las tareas; la suite SQLite sigue offline.

## Migration Plan

1. Capturar línea base de conteos de tests (backend y frontend).
2. Modificar `pytest.ini` (loop scope explícito) y `conftest.py` (scope de fixtures PG, fallo ruidoso, PRAGMA FK).
3. Verificar con PostgreSQL levantado (`docker compose up -d postgres`) que la suite `-m integration` corre y pasa.
4. Agregar las pruebas de contrato N8N, las de estadísticas/PATCH-FK y las de configuración frontend/Docker; confirmar que fallan (RED) por las razones esperadas.
5. Registrar línea base posterior y documentar hallazgos.
6. Rollback: revertir los archivos de test y `pytest.ini`. No hay estado persistente, migración de datos ni cambio de producción involucrado.
