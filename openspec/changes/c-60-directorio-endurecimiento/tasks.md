## 1. Preparacion, decisiones y safety net

- [x] 1.1 Registrar en `design.md` las decisiones de c-60 (rol `mesa_de_ayuda` sin sector, modelo de visibilidad D2, cola acotada D4, purga manual con ids D5, guardia solo seed D6, evidencia 7.5 D7, migracion 012 D8) y confirmar que `proposal.md` y los delta specs no difieren. Verificacion: las decisiones figuran en `design.md` y `openspec validate --strict --changes c-60-directorio-endurecimiento` pasa.
- [x] 1.2 Registrar el baseline de las suites afectadas: `cd App/Backend; pytest -m "not integration" tests/test_incident_visibility.py tests/test_clasificacion_visibility.py tests/test_directorio_service.py` y anotar el conteo en verde. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificacion: conteo baseline anotado y sin fallos nuevos atribuibles al change.

## 2. Rol `mesa_de_ayuda`: modelo y migracion

- [x] 2.1 RED: extender `App/Backend/tests/test_empleado_model.py` para exigir que `RolEmpleado` incluya `mesa_de_ayuda` y que el CHECK de `rol` acepte los cuatro valores. Verificacion: el test falla contra el modelo vigente (tres valores).
- [x] 2.2 GREEN: agregar `mesa_de_ayuda` a `RolEmpleado` y al `CheckConstraint` en `App/Backend/app/models/empleado.py`. Verificacion: el test de 2.1 pasa en SQLite.
- [x] 2.3 GREEN: crear la migracion append-only `App/Backend/alembic/versions/012_directorio_rol_mesa_ayuda.py` (`down_revision = "011"`, tras c-70) que recrea el CHECK con los cuatro valores. Verificacion: `alembic upgrade head` y `alembic downgrade -1` corren sin error.
- [x] 2.4 TRIANGULATE: cubrir que `mesa_de_ayuda` NO requiere sector (se persiste con `sector_id` nulo) y que el vocabulario previo sigue aceptado. Verificacion: casos en verde.
- [x] 2.5 INTEGRATION: agregar/extender `@pytest.mark.integration` para verificar el CHECK real de `rol` en PostgreSQL (acepta `mesa_de_ayuda`, rechaza un valor fuera del vocabulario). Verificacion: `cd App/Backend; pytest -m integration` en verde contra la base desechable.

## 3. Visibilidad de incidentes por rol (`AlcanceIncidentes`)

- [x] 3.1 RED: extender `App/Backend/tests/test_incident_visibility.py` para exigir los modos `GLOBAL` (administrador), `SECTOR`, `REVISION` (`mesa_de_ayuda`) y `VACIO`, y `permite_incidente(incidente)` que en `REVISION` acepte `sector_id is None` o `requiere_revision_humana` verdadero. Verificacion: el test falla por modos/`permite_incidente` inexistentes.
- [x] 3.2 GREEN: generalizar `App/Backend/app/services/incident_visibility.py` a modos y mapear el rol en `alcance_desde_empleado` (`mesa_de_ayuda` -> `REVISION`), conservando `permite_sector` por compatibilidad. Verificacion: los tests de 3.1 pasan.
- [x] 3.3 GREEN: aplicar `permite_incidente` en los call sites donde la decision depende del incidente completo (lectura/listado y clasificaciones), reutilizando el servicio de visibilidad sin duplicar la derivacion rol -> alcance. Verificacion: los tests de visibilidad de c-54 siguen en verde.
- [x] 3.4 TRIANGULATE: cubrir `mesa_de_ayuda` que NO ve un incidente con sector asignado y sin revision; un incidente sin sector visible para `mesa_de_ayuda`; administrador ve todo; cuenta vacia no ve nada. Verificacion: casos en verde.

## 4. Cola `revision-pendiente` acotada por sector y rol

- [x] 4.1 RED: extender `App/Backend/tests/test_clasificacion_visibility.py` para exigir que `GET /api/v1/clasificaciones/revision-pendiente` se acote por alcance: administrador y `mesa_de_ayuda` ven la cola completa; `usuario_final`/`operador` con sector S ven solo los pendientes de S; alcance vacio ve lista vacia; anonimo 401. Verificacion: el test falla por cola global.
- [x] 4.2 GREEN: agregar filtros opcionales por sector/revision en `App/Backend/app/repositories/clasificacion_repository.py`, propagarlos en `ClasificacionService.list_pending_review` e inyectar `AlcanceIncidentes` en la ruta. Verificacion: los tests de 4.1 pasan.
- [x] 4.3 TRIANGULATE: preservar FIFO y la definicion de pendiente (`requiere_revision_humana` verdadero y sin validacion); cubrir un pendiente de otro sector que NO aparece. Verificacion: casos en verde.

## 5. Purga manual con ids auditados

- [x] 5.1 RED: extender `App/Backend/tests/test_directorio_service.py` (y/o `test_purgar_directorio`) para exigir que `purgar_vencidos` devuelva los **ids** de las filas eliminadas, los incluya en el evento de auditoria/log (sin PII) y que una segunda corrida devuelva `ids` vacios. Verificacion: el test falla contra el retorno actual (solo conteo).
- [x] 5.2 GREEN: modificar `DirectorioService.purgar_vencidos` en `App/Backend/app/services/directorio_service.py` para recolectar y devolver los ids y auditarlos. Verificacion: los tests de 5.1 pasan.
- [x] 5.3 GREEN: exponer el disparo MANUAL por operador `POST /api/v1/directorio/purga` (rol `administrador_directorio`) en `App/Backend/app/routes/directorio.py` + schema, devolviendo `{ "purgados": N, "ids": [...] }`; actualizar `App/Backend/scripts/purgar_directorio.py` para reportar ids. Verificacion: test de API (admin sucede, otro rol 403, anonimo 401) en verde.
- [x] 5.4 Verificar que NO se agrega cron/scheduler/worker: test/inspeccion de que la purga solo se dispara por invocacion humana explicita. Verificacion: no existe mecanismo automatico de purga en el codigo.
- [x] 5.5 TRIANGULATE: cubrir baja vencida purgada con su id, baja reciente conservada, activo conservado, e idempotencia (segunda corrida sin ids). Verificacion: casos en verde.
- [x] 5.6 Regenerar `docs/openapi.json` y ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v`. Verificacion: el test de sincronizacion pasa.

## 6. Guardia de entorno acotada al seed

- [x] 6.1 RED: escribir `App/Backend/tests/test_seed_directorio_guard.py` que exija que el seed rechace ejecutarse con `environment=production` (aborta sin tocar la base) y proceda con `environment` en dev/test. Verificacion: el test falla contra el seed actual (sin guardia).
- [x] 6.2 GREEN: agregar la guardia de entorno UNICAMENTE en `App/Backend/scripts/seed_directorio.py` (entrada dev-only), sin cambiarla en rutas/servicios/dependencias. Verificacion: los tests de 6.1 pasan.
- [x] 6.3 Verificar que el runtime normal NO se gatea: test que opera la API/resolucion/visibilidad con `environment=production` y confirma comportamiento normal. Verificacion: el test pasa y la guardia no interviene fuera del seed.

## 7. Evidencia y cierre de las confirmaciones de c-54 7.5 (HIGH)

- [x] 7.1 Confirmar y documentar la politica de retencion/ARCO (relacion activa + 1 año; borrado fisico por vencimiento manual o ARCO; desactivacion no borrado), referenciando DIR-007. Verificacion: documento y tests coherentes con la politica.
- [x] 7.2 RED/GREEN: agregar test/inspeccion de que NO hay PII real en repositorio ni en base (los contactos son sinteticos/estructurales) y que NO existe clave de indice ciego ni columna de hash (DIR-005/DIR-009). Verificacion: los tests pasan y no hay clave `directory_blind_index_key`.
- [x] 7.3 Documentar la regla de visibilidad por rol y su alcance (D2/D4): administrador, `mesa_de_ayuda`, sector-bound y vacio. Verificacion: la documentacion coincide con los specs VIS-001/VIS-002.
- [x] 7.4 Registrar la revision humana HIGH como PENDIENTE de aprobacion: activar datos reales queda bloqueado; la implementacion usa datos sinteticos. Verificacion: la aprobacion queda explicitamente pendiente en `tasks.md`/docs y NO se activan datos reales. — REGISTRADO (2026-10-06): la aprobacion humana HIGH sigue PENDIENTE; real data permanece bloqueado; sin PII real (ver `docs/directorio-evidencia-cumplimiento.md`).

## 8. Documentacion y verificacion final

- [x] 8.1 Actualizar `docs/directorio-usuarios.md` (rol `mesa_de_ayuda`, visibilidad, cola acotada, purga manual con ids, guardia del seed, evidencia 7.5) sin PII real. Verificacion: documentacion verificable y coherente con los specs.
- [x] 8.2 Ejecutar la suite offline: `cd App/Backend; pytest -m "not integration"`. Verificacion: sin regresiones respecto del baseline de 1.2.
- [x] 8.3 Ejecutar la suite de integracion: `cd App/Backend; pytest -m integration`. Verificacion: en verde contra la base desechable, sin tocar la base de aplicacion.
- [x] 8.4 Ejecutar lint: `cd App/Backend; ruff check .` y `cd App/Backend; pytest tests/test_openapi_sync.py -v`. Verificacion: sin errores E nuevos y OpenAPI sincronizado.
- [x] 8.5 Ejecutar `openspec validate --strict --changes c-60-directorio-endurecimiento`. Verificacion: validacion estricta sin errores.
- [x] 8.6 Considerar la actualizacion de `CHANGES.md` para registrar c-60 (entrada, dependencias c-54/c-56, governance ALTO, "Leer antes") — fuera de los artefactos OPSX del change. Verificacion: entrada registrada o pendiente anotada para el orquestador.
