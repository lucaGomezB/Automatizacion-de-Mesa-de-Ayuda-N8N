## 1. Línea base (safety net)

- [x] 1.1 Capturar el conteo base del backend ejecutando `cd App/Backend; pytest -q` y registrarlo (passed/skipped/fallidos) en una nota del change; verificar que el conteo previo coincide con el reportado en el enunciado (267 passed / 18 skipped) o documentar la diferencia.
- [x] 1.2 Capturar el conteo base del frontend ejecutando `cd App/Frontend; npm run test` y registrarlo; verificar que el conteo previo coincide con el reportado (112 passed) o documentar la diferencia.
- [x] 1.3 Registrar la línea base en este change (sección de notas) y declarar explícitamente que cualquier test que pase de verde a rojo por una costura recién expuesta es un hallazgo RED intencional, no una regresión a silenciar.

## 2. Loop scope de pytest-asyncio

- [x] 2.1 Declarar `asyncio_default_fixture_loop_scope` de forma explícita en `App/Backend/pytest.ini` (valor compatible con `pytest-asyncio==0.24.0`, manteniendo `asyncio_mode = auto`); verificar leyendo `pytest.ini` que la opción queda declarada con un valor no vacío.
- [x] 2.2 Ajustar los fixtures PostgreSQL de `App/Backend/tests/conftest.py` (`pg_engine`, `pg_session`, `pg_client`, `seed_pg_catalogs`) para que fixture y test compartan el MISMO event loop segun la decisión D1; verificar ejecutando `docker compose up -d postgres` y luego `cd App/Backend; pytest -m integration -q` que NO se levanta `RuntimeError: ... got Future ... attached to a different loop`.

## 3. Fallo ruidoso sin skip silencioso

- [x] 3.1 Reemplazar el `pytest.skip` del probe de conexión de `pg_engine` por un fallo con mensaje accionable que nombre la URL efectiva (`_get_pg_url()`) y el comando `docker compose up -d postgres`; verificar que con PostgreSQL detenido `cd App/Backend; pytest -m integration -q` sale con exit code distinto de cero, no reporta skips y el mensaje nombra URL y comando.
- [x] 3.2 Verificar que la ausencia de PostgreSQL no afecta la suite SQLite: con PostgreSQL detenido, `cd App/Backend; pytest -q` (sin `-m integration`) ejecuta los tests SQLite sin fallos atribuibles a la conexión.

## 4. Enforcement de claves foráneas en SQLite

- [x] 4.1 Registrar en `App/Backend/tests/conftest.py` un listener sobre el evento `connect` del engine SQLite que ejecute `PRAGMA foreign_keys=ON` en cada conexión; verificar con un test que `PRAGMA foreign_keys` devuelve `1` sobre una conexión del engine compartido y sobre la conexión que abre el cliente ASGI.
- [x] 4.2 Agregar un test que verifique que una operación de escritura con FK inexistente sobre el engine SQLite falla por violación de integridad referencial; verificar que el test falla (RED) o expone el defecto hoy oculto, y documentar el hallazgo.

## 5. Pruebas de contrato runtime de N8N

- [x] 5.1 Extender `App/Backend/tests/test_n8n_workflow.py` con un test que exija autenticación configurada en el nodo `httpRequest` que apunta a `/api/v1/incidentes`; verificar que el test falla (RED) porque el nodo no declara autenticación.
- [x] 5.2 Agregar un test que exija `canal_origen_id` en el `body` del nodo `httpRequest` de persistencia; verificar que falla (RED) porque el body actual sólo contiene `descripcion` y `prioridad`.
- [x] 5.3 Agregar tests que exijan que cada nodo `switch` en `mode: expression` devuelva un índice numérico de rama y que los campos referenciados existan en el schema de respuesta real del backend o en un nodo aguas arriba accesible; verificar que fallan (RED) porque la salida actual es `$json.canal_origen`, ausente en la respuesta de `POST /api/v1/incidentes`.
- [x] 5.4 Agregar un test que exija conexión `ai_languageModel` en cada nodo `@n8n/n8n-nodes-langchain.agent`; verificar que falla (RED) porque el agente actual sólo tiene conexión `ai_memory`.
- [x] 5.5 Agregar un test que exija que el prompt del agente interpole el payload del trigger (`$json`/`$input`); verificar que falla (RED) porque el prompt actual es un texto estático sin datos del incidente.
- [x] 5.6 Agregar un test que exija que el `microsoftOutlookTrigger` quede configurado para exponer el cuerpo del correo que lee el validador (`body`/`descripcion`/`text`); verificar que falla (RED) según la configuración actual del trigger.
- [x] 5.7 Agregar un test que exija que todo `webhook` con `responseMode: responseNode` tenga un `respondToWebhook` alcanzable desde su rama exitosa; verificar el resultado (RED/PASS) y documentarlo.
- [x] 5.8 Agregar un test que exija que los nodos que requieren credenciales (Outlook, trigger de Twilio, modelo de lenguaje del agente) declaren su credencial; verificar que falla (RED) para los nodos sin credencial declarada.

## 6. Pruebas de integración PostgreSQL (estadísticas y PATCH con FK inexistente)

- [x] 6.1 Agregar tests con marker `integration` que exijan `GET /api/v1/estadisticas/tendencias` (por día y por mes) HTTP 200 contra PostgreSQL con al menos un incidente creado; verificar que el test de `/tendencias` falla (RED) con 500 en PostgreSQL por el uso de `func.strftime`.
- [x] 6.2 Agregar un test con marker `integration` que exija `GET /api/v1/estadisticas/resumen` HTTP 200 contra PostgreSQL; verificar el resultado (RED/PASS) y documentarlo.
- [x] 6.3 Agregar un test con marker `integration` que exija que `PATCH /api/v1/incidentes/{id}` con `estado_id`/`sector_id` inexistente devuelva 4xx (no 500) y que el incidente conserve sus referencias previas; verificar que falla (RED) con 500 en PostgreSQL.

## 7. Pruebas de configuración frontend/Docker

- [x] 7.1 Agregar un test (suite backend, lectura de archivos) que exija que el servicio `frontend` de `docker-compose.yml` reenvíe `VITE_API_BASE_URL` bajo `build.args` y que el valor no termine en `/api/v1`; verificar que falla (RED) porque hoy sólo aparece bajo `environment` y el valor termina en `/api/v1`.
- [x] 7.2 Agregar un test que exija que `App/Frontend/Dockerfile` declare `ARG VITE_API_BASE_URL` antes de `npm run build`; verificar que falla (RED) porque el `ARG` no existe.
- [x] 7.3 Agregar un test en la suite Vitest del frontend que compare las rutas del cliente (`incidentesService.ts`, etc.) contra las rutas de `docs/openapi.json` incluyendo trailing slash; verificar que falla (RED) porque el cliente usa `/incidentes` y la especificación declara `/api/v1/incidentes/`.

## 8. Verificación de integración y cierre

- [x] 8.1 Ejecutar `cd App/Backend; pytest -q` y comparar contra la línea base de 1.1; verificar que las únicas diferencias son los tests nuevos en rojo y documentar cada hallazgo con su causa raíz.
- [x] 8.2 Ejecutar `docker compose up -d postgres` y `cd App/Backend; pytest -m integration -q`; verificar que los tests PostgreSQL preexistentes pasan (infraestructura reparada) y que los nuevos tests de costura quedan en rojo por las razones esperadas.
- [x] 8.3 Ejecutar `cd App/Frontend; npm run test` y comparar contra la línea base de 1.2; verificar que las únicas diferencias son el test nuevo en rojo de alineación de rutas.
- [x] 8.4 Verificar que no se modificó código de producción: `git status --short` y `git diff --stat` no muestran cambios en `app/**`, `n8n/workflow.json`, `docker-compose.yml` ni `App/Frontend/Dockerfile`; solo archivos de test y `pytest.ini`.
