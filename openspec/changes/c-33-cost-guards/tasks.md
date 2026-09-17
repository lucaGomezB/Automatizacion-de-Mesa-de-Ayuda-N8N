## 0. Baseline, dependencias y gobernanza

- [ ] 0.1 Registrar el baseline de las suites afectadas antes de tocar nada: `cd App/Backend; pytest -m "not integration"` y `cd evaluation; pytest`. Anotar la cantidad de tests en verde y confirmar que corren sin modificaciones.
- [ ] 0.2 Confirmar el estado de las dependencias con `openspec status --change c-30-bugfix-seams --json`, `--change c-31-dry-run-harness` y `--change c-32-disposable-test-db`; registrar si estan aplicadas, porque el contrato del workflow y la base descartable las asumen.
- [ ] 0.3 CHECKPOINT DE GOBERNANZA ALTA: antes de escribir `n8n/workflow.json` o la migracion, presentar el plan de nodos/campos exacto y obtener aprobacion humana explicita; registrar la aprobacion en el change. Ninguna tarea de los grupos 3 y 6 comienza sin este checkpoint.

## 1. RED — Contratos estructurales del workflow N8N

- [ ] 1.1 En `App/Backend/tests/test_n8n_workflow.py`, escribir el test del tope de refinamiento: el nodo `AI Agent` declara un tope explicito y existe un IF de tope con una rama terminal que NO reingresa al agente. Verificar que el test FALLA (RED) por ausencia de la configuracion.
- [ ] 1.2 En `App/Backend/tests/test_n8n_workflow.py`, escribir el test de la salida terminal: el nodo terminal fija `confianza=0.0` y `requiere_revision_humana=true` y alcanza el nodo HTTP de persistencia. Verificar RED.
- [ ] 1.3 En `App/Backend/tests/test_n8n_workflow.py`, escribir el test del ciclo de vida del correo: `Marcar correo como leido` es alcanzable desde las ramas de exito, rechazo y error, cada una con guarda de canal. Verificar RED.
- [ ] 1.4 En `App/Backend/tests/test_n8n_workflow.py`, escribir el test del lookback: el trigger de Outlook declara un filtro de fecha `receivedDateTime` con 24 horas. Verificar RED.
- [ ] 1.5 En `App/Backend/tests/test_n8n_workflow.py`, escribir el test del payload enriquecido: `HTTP POST a MTM-SRU` envia `origen_message_id`, la clasificacion precalculada y un marcador explicito de origen. Verificar RED.
- [ ] 1.6 En `App/Backend/tests/test_n8n_workflow.py`, escribir el test del webhook dedicado de notificacion: existe una ruta distinta de `incidente-web` que no esta conectada a la creacion de incidentes. Verificar RED.
- [ ] 1.7 Ejecutar `cd App/Backend; pytest tests/test_n8n_workflow.py -q` y confirmar que los tests nuevos fallan por asercion (no por error de coleccion); registrar la evidencia RED.

## 2. RED — Contratos backend de intake y notificacion

- [ ] 2.1 En `App/Backend/tests/test_api_incidentes.py`, escribir el test de idempotencia: un alta con `origen_message_id` crea el incidente y un reintento con el mismo identificador devuelve el mismo incidente sin volver a invocar al clasificador (spy/mock de `HybridClassifier`). Verificar RED.
- [ ] 2.2 En `App/Backend/tests/test_api_incidentes.py`, escribir los tests de alta sin identificador (funciona) y de identificadores distintos (crean incidentes distintos). Verificar RED.
- [ ] 2.3 En `App/Backend/tests/test_api_incidentes.py`, escribir el test de clasificacion precalculada valida: el incidente se persiste con la clasificacion provista y el clasificador inyectado NO es invocado. Verificar RED.
- [ ] 2.4 En `App/Backend/tests/test_api_incidentes.py`, escribir el test de ausencia de clasificacion precalculada: el backend clasifica server-side como hasta ahora. Verificar RED.
- [ ] 2.5 En `App/Backend/tests/test_api_incidentes.py`, escribir los tests de rechazo: sector precalculado fuera del vocabulario y confianza fuera de rango responden 422 sin invocar al clasificador. Verificar RED.
- [ ] 2.6 En `App/Backend/tests/test_api_incidentes.py`, escribir el test del marcador de evento: un `origen_evento` de notificacion responde 422 y no crea incidente; sin marcador el alta funciona. Verificar RED.
- [ ] 2.7 En `App/Backend/tests/test_api_incidentes.py`, escribir el test de clasificacion forzada a revision: bloque precalculado con `requiere_revision_humana=true` y sin sector persiste el incidente con sector nulo y revision humana, sin invocar al clasificador. Verificar RED.
- [ ] 2.8 Crear `App/Backend/tests/test_migration_origen_message_id.py` y escribir el test de la migracion `005`: la columna `origen_message_id` existe, es nullable y unica, `upgrade`/`downgrade` son reversibles y la migracion `001` no fue mutada. Verificar RED.
- [ ] 2.9 En `App/Backend/tests/test_incidente_notify_n8n.py`, escribir el test del payload de notificacion: incluye el marcador explicito de evento de notificacion. Verificar RED.
- [ ] 2.10 Ejecutar `cd App/Backend; pytest tests/test_api_incidentes.py tests/test_migration_origen_message_id.py tests/test_incidente_notify_n8n.py -q` y confirmar RED por asercion; registrar la evidencia.

## 3. GREEN — Migracion, modelo y repositorio

- [ ] 3.1 Crear `App/Backend/alembic/versions/005_add_origen_message_id.py` con la columna nullable, `unique` e indexada; verificar `upgrade` y `downgrade` contra la base descartable de c-32 y que `001` queda intacta (test 2.8 verde).
- [ ] 3.2 Agregar `origen_message_id: Mapped[str | None]` al modelo en `App/Backend/app/models/incidente.py`; verificar el test de migracion/modelo en verde.
- [ ] 3.3 Agregar `get_by_origen_message_id` en `App/Backend/app/repositories/incidente_repository.py`; verificar con un test de repositorio que devuelve la fila o `None`.
- [ ] 3.4 Ejecutar `cd App/Backend; pytest tests/test_migration_origen_message_id.py tests/test_modelo_doble_representacion.py -q` y confirmar verde.

## 4. GREEN — Schemas, servicio y auditoria

- [ ] 4.1 Extender `ClasificacionEtapa` con `"precalculada"` en `App/Backend/app/schemas/clasificacion.py`; verificar que los tests de clasificacion existentes siguen verdes.
- [ ] 4.2 Agregar `origen_message_id`, `origen_evento` y el bloque `ClasificacionPrecalculada` a `IncidenteCreate` en `App/Backend/app/schemas/incidente.py`, con validadores de vocabulario canonico, rango de confianza y marcador de evento; verificar los tests 2.5, 2.6 y 2.7 en verde.
- [ ] 4.3 Implementar el cortocircuito idempotente al inicio de `IncidenteService.create_and_classify` (buscar por `origen_message_id` antes de pseudonimizar/clasificar y re-consultar ante `IntegrityError`); verificar 2.1 y 2.2 en verde.
- [ ] 4.4 Implementar la rama de clasificacion precalculada: construir `ClasificacionResult` con `etapa="precalculada"`, omitir `HybridClassifier`, persistir el origen en `respuesta_raw` y derivar `requiere_revision_humana`; verificar 2.3, 2.4 y 2.7 en verde.
- [ ] 4.5 Ejecutar `cd App/Backend; pytest tests/test_api_incidentes.py tests/test_hybrid_classifier.py tests/test_asociacion_sectores.py -q` y confirmar verde sin regresiones.

## 5. GREEN — Notificacion dedicada (backend)

- [ ] 5.1 Agregar el marcador explicito de evento de notificacion al payload de `notify_n8n` en `App/Backend/app/utils/n8n_webhook.py`; verificar el test 2.9 en verde.
- [ ] 5.2 Apuntar `N8N_WEBHOOK_URL` en `docker-compose.yml` a la ruta del webhook dedicado; verificar con `docker compose config` que la variable resuelve la URL esperada.
- [ ] 5.3 Ejecutar `cd App/Backend; pytest tests/test_incidente_notify_n8n.py tests/test_api_incidentes.py -q` y confirmar verde.

## 6. GREEN — Workflow N8N (gobernanza ALTA, con checkpoint del 0.3)

- [ ] 6.1 Configurar `maxIterations` en las `options` del nodo `AI Agent` e incrementar `intento_agente` en `Se verifica lo que trajo la IA`; verificar el test 1.1.
- [ ] 6.2 Agregar el IF `Tope de refinamiento alcanzado` y el nodo terminal `Derivar a revision humana`, con la ruta de persistencia para revision que no reingresa al agente; verificar los tests 1.1 y 1.2.
- [ ] 6.3 Agregar la guarda `Es correo?` y cablear `Marcar correo como leido` desde las ramas de rechazo y error; verificar el test 1.3.
- [ ] 6.4 Configurar `onError: "continueErrorOutput"` en los nodos de persistencia del canal correo y cablear la salida de error a la rama de marcado; verificar el test 1.3.
- [ ] 6.5 Agregar el filtro `receivedDateTime` con 24 horas de lookback al trigger de Outlook; verificar el test 1.4.
- [ ] 6.6 Extender el body de `HTTP POST a MTM-SRU` con `origen_message_id`, la clasificacion precalculada y el marcador de origen; verificar el test 1.5.
- [ ] 6.7 Agregar el webhook dedicado `notificacion-clasificacion` sin conexion a la creacion de incidentes; verificar el test 1.6.
- [ ] 6.8 Ejecutar `cd App/Backend; pytest tests/test_n8n_workflow.py -q` completo y confirmar todos verdes; verificar con `git status --porcelain` que no hay cambios fuera de los archivos previstos.

## 7. REFACTOR y documentacion

- [ ] 7.1 Extraer la logica repetida de los nodos Code nuevos (conteo de intentos y guarda de correo) a helpers dentro del mismo `jsCode` sin cambiar el comportamiento; re-ejecutar `tests/test_n8n_workflow.py` y confirmar verde.
- [ ] 7.2 Actualizar `docs/n8n-workflow-guide.md` con el tope de refinamiento, el ciclo de vida del correo, el lookback de 24 horas y el acoplamiento de la notificacion; verificar que no se toca `docs/Tesis/**`.
- [ ] 7.3 Verificar la consistencia entre las specs y los artefactos implementados (nombres de nodos, rutas y campos) y confirmar que no se modifico el `tasks.md` de ningun otro change.

## 8. Verificacion final e integracion

- [ ] 8.1 Ejecutar `cd App/Backend; pytest -m "not integration"` y confirmar el subconjunto SQLite en verde.
- [ ] 8.2 Ejecutar `cd App/Backend; pytest -m integration` contra la base descartable de c-32 y confirmar que `mesa_de_ayuda` no fue objetivo (sin la guardia de escape).
- [ ] 8.3 Ejecutar `cd App/Backend; pytest` completo (con PostgreSQL disponible) y confirmar verde.
- [ ] 8.4 Ejecutar `cd App/Backend; pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing` y confirmar que la cobertura de los modulos tocados no baja.
- [ ] 8.5 Si el schema de la API cambio, regenerar `docs/openapi.json` y ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v` en verde.
- [ ] 8.6 Ejecutar el arnés de costo cero de c-31 (o su preflight equivalente) contra el stack `mesa_local` y confirmar persistencia sin llamadas pagas; registrar la evidencia.
- [ ] 8.7 Ejecutar `openspec validate c-33-cost-guards --strict` y confirmar PASS; confirmar con `git status --porcelain` que no quedan artefactos temporales ni secretos.
