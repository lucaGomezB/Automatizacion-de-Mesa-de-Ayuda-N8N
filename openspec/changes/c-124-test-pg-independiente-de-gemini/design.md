## Context

El problema y su motivación están en `proposal.md` (Why). Estado verificado del código (solo lectura, más una reproducción empírica):

- `App/Backend/tests/conftest.py:411-458` (`pg_client`): sobrescribe `get_db_session` (motor PostgreSQL), autenticación, `get_alcance_incidentes` y `get_cost_guard`; solo mockea `notify_n8n`. El clasificador es el `HybridClassifier` REAL, construido dentro de `IncidenteService`.
- `App/Backend/app/services/incidente_service.py:123` (`classifier or HybridClassifier(...)`) y `:607-609` (`_apply_classification`): el sector del incidente se resuelve por NOMBRE desde `result.sector_predicho`; el `sector_id` del payload NO determina el sector del alta.
- `App/Backend/tests/conftest.py:668-735` (`make_client_with_classifier`): factoría que inyecta `AsyncMock.classify` devolviendo un `ClasificacionResult`, pero está atada al `engine` SQLite. Existe `make_client_with_spy_classifier` (`:738-811`) con el mismo acoplamiento.
- `App/Backend/tests/conftest.py:817-855` (`seed_pg_catalogs`): expone el catálogo ya sembrado por `pg_schema`, incluido `sector_sistemas` ("Sistemas").
- Reproducción confirmada con `GEMINI_API_KEY=ci-dummy-key`: `deterministic_no_match` → `classifier_escalate_to_gemini` → `gemini_retry_terminal ClientError` → `gemini_fallback_triggered` → `etapa=fallback`, `sector_predicho=None` → `TypeError` en `test_integration_postgresql.py:544`.

Consumidores de `pg_client` en la suite actual (verificados): `test_patch_updates_estado` (solo afirma `estado`), `test_estadisticas_tendencias_200_on_postgresql` y `test_estadisticas_resumen_200_on_postgresql` (solo afirman HTTP 200) y `test_c90_prioridad_critica_integration.py::test_cuenta_sin_empleado_critica_403` (corta con 403 antes de invocar el servicio). Ninguno depende de la salida del clasificador real.

## Goals / Non-Goals

**Goals:**

- Hacer determinista e independiente de Gemini al test `test_patch_incidente_nonexistent_fk_returns_4xx`.
- Mantener intactas las aserciones (PATCH con FK inexistente devuelve 4xx y preserva el sector previo).
- Pasar en CI (clave Gemini ficticia) y localmente (clave real).

**Non-Goals:**

- No modificar el comportamiento de producción (`app/`).
- No debilitar, saltar ni marcar `xfail` ninguna aserción.
- No agregar ninguna llamada de red externa.
- No cambiar la fixture compartida `pg_client` para todos los tests PostgreSQL (evaluado y diferido; ver D1).

## Decisions

### D1 - Fixture dedicada `make_pg_client_with_classifier(pg_engine)` en lugar de ampliar `pg_client`

Se agrega una factoría en la sección PostgreSQL de `conftest.py` que replica los overrides de `pg_client` (auth, alcance GLOBAL, `cost_guard=None`, `notify_n8n` mockeado) y añade el override de `get_service` (alias `get_incidente_service`) para construir `IncidenteService` con un clasificador doble, siguiendo el patrón de `make_client_with_classifier` pero con `pg_engine`.

Razón: el blast radius es mínimo — solo cambia el test que falla. No se altera la semántica de una fixture compartida por otros cinco tests.

**Alternativa considerada (ampliar `pg_client` para inyectar un doble determinista en TODA la suite PostgreSQL).** Se verificó que HOY sería seguro (ningún consumidor actual depende del clasificador real) y que eliminaría la dependencia oculta de Gemini en los otros tests de creación, acelerando CI. Se difiere porque: (a) cambia la semántica de una fixture compartida y cualquier test futuro que quiera ejercitar el camino determinista real obtendría en silencio un resultado enlatado; (b) el alcance pedido es el test que falla. Queda registrado como mejora futura (ver Risks).

### D2 - Resultado del doble: `sector_predicho="Sistemas"`, confianza 0.95, etapa `deterministic`

El doble devuelve `ClasificacionResult(sector_predicho="Sistemas", confianza=0.95, etapa="deterministic", requiere_revision_humana=False)`. "Sistemas" es un sector sembrado por `pg_schema` y el mismo que el helper `_crear_incidente_via_pg_api` ya envía en el payload, por lo que el sector asignado coincide con `catalogs["sector_sistemas"].id` y `created["sector"]["id"]` es no nulo. La alta confianza mantiene el caso simple (no marca revisión).

**Alternativa considerada (usar el `sector_id` del payload).** No aplica: el servicio resuelve el sector desde el clasificador y no desde el payload en el alta (`incidente_service.py:607-609`).

### D3 - Preservar exactamente las aserciones del test

La reescritura solo cambia el setup (factoría + resultado doble) y la lectura del sector. Se conservan la aserción de rango 4xx sobre el `PATCH` y la verificación de que el sector previo no cambia. No se introduce `skip`, `xfail` ni relajación de rangos.

### D4 - Reutilizar el patrón de `make_client_with_classifier` sin parametrizarlo

Se crea una factoría nueva en vez de parametrizar por motor la existente, para no tocar el factory SQLite que consumen numerosos tests. La duplicación de la lógica de overrides es acotada y explícita; extraer un helper común queda como refactor futuro sin cambio de comportamiento.

## Risks / Trade-offs

- **[Los otros tests PostgreSQL que crean incidentes siguen intentando Gemini (pasan por `fallback`)]** → Fuera de alcance; el test que falla queda aislado. Mejora futura documentada: ampliar el aislamiento a `pg_client` (D1, alternativa).
- **[Duplicación de la lógica de overrides entre la factoría SQLite y la PostgreSQL]** → Aceptable y explícita; refactor futuro (helper común) sin cambio de comportamiento.
- **[El doble fija el nombre "Sistemas"]** → Si el vocabulario sembrado cambiara, el test fallaría de forma explícita y temprana; el seed es canónico (C-27), por lo que el fallo sería deseable.
- **[Riesgo de debilitar la verificación al no requerir sector no nulo]** → Se descarta la opción de tolerar `sector=None`: debilitaría la aserción de "preservar referencias previas". El doble garantiza un sector no nulo y determinista.
- **[`test_patch_updates_estado` sigue con el clasificador real]** → No lee el sector y pasa por el camino de `fallback`; verificado que no se ve afectado.

## Migration Plan

1. Agregar `make_pg_client_with_classifier(pg_engine)` en `App/Backend/tests/conftest.py` (sección PostgreSQL).
2. Reescribir `test_patch_incidente_nonexistent_fk_returns_4xx` para usar la factoría con el `ClasificacionResult` de D2, conservando las aserciones.
3. Verificar el test bajo condiciones de CI (clave ficticia) y localmente (clave real), y correr la suite PostgreSQL completa.

Rollback: revertir los dos archivos de test (`git checkout <commit-previo> -- App/Backend/tests/conftest.py App/Backend/tests/test_integration_postgresql.py`). Sin despliegue ni migración.

## Open Questions

Ninguna.
