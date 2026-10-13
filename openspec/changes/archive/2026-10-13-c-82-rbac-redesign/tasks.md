## 1. Registro central de politica de rol (RP-001, RP-002, RP-003)

- [x] 1.1 RED: escribir `tests/test_role_policy.py` con la tabla completa `rol -> {requires_sector=False, visibilidad, privileged, manages_directory, notification_recipient}` y un caso por atributo (RP-001); verificar que falla porque el modulo no existe.
- [x] 1.2 GREEN: crear `app/services/role_policy.py` con `ROLES_VALIDOS`, `PoliticaRol` (frozen) y `ROLE_POLICY` para los tres roles; verificar que `pytest tests/test_role_policy.py` pasa.
- [x] 1.3 TRIANGULATE: agregar el test de coherencia (RP-003) que falla si el enum, el CHECK del modelo y el registro divergen; verificar que pasa con el vocabulario de tres roles.
- [x] 1.4 REFACTOR: derivar `PRIVILEGED_ROLE_VALUES`, el modo de visibilidad, los guards y el criterio de destinatarios del registro; verificar que la suite del cambio sigue verde sin listas de rol duplicadas.

## 2. Vocabulario de roles y migracion append-only (DIR-003, D1, D5)

- [x] 2.1 RED: escribir la actualizacion de `tests/test_directorio_service.py` (u homonimo) y un test de enum que exija exactamente tres roles y el rechazo de `operador`; verificar que falla.
- [x] 2.2 GREEN: actualizar `RolEmpleado` en `app/models/empleado.py` (quitar `operador`) y el `CheckConstraint` a los tres valores derivados de `ROLES_VALIDOS`; verificar que los tests de modelo/enum pasan.
- [x] 2.3 RED: escribir `tests/test_migration_017_rbac.py` (patron `test_migration_*.py`) que verifique la columna `reportante_empleado_id` (FK nullable) y el CHECK de tres valores sobre SQLite en archivo.
- [x] 2.4 GREEN: crear `alembic/versions/017_rbac_redesign.py` (`down_revision="016"`): agregar `reportante_empleado_id` + indice, backfill `UPDATE ... SET rol='mesa_de_ayuda' WHERE rol='operador'` ANTES del CHECK nuevo (OQ-2; escenario de filas legacy de DIR-003), y recrear el CHECK con `batch_alter_table`; verificar `openspec`/`alembic upgrade` + el test 2.3.
- [x] 2.5 TRIANGULATE: agregar el test de `downgrade` que restaura el CHECK de cuatro valores y elimina la columna, sin re-marcar filas; verificar ida y vuelta.
- [x] 2.6 RED: extender `tests/test_migration_017_rbac.py` para exigir el empleado sintetico `administrador_directorio` de la cuenta `admin` (OQ-3/D9): legajo determinista `SYS-ADMIN`, `email` sintetico no nulo con dominio reservado (`sys-admin@example.test`; el esquema exige email NOT NULL/UNIQUE), `telefono` nulo, sin PII real, insercion condicional a que el usuario `admin` exista y no tenga empleado, idempotente; y que la cuenta `admin` resuelva alcance GLOBAL, no VACIO (VIS-001); verificar que falla.
- [x] 2.7 GREEN: agregar a `alembic/versions/017_rbac_redesign.py` la insercion condicional del empleado sintetico de `admin` con SQL crudo (sin importar modelos), respetando la regla "Alembic no siembra PII real"; verificar 2.6 y la idempotencia (segunda corrida no duplica).

## 3. Visibilidad PROPIO/GLOBAL (VIS-001, VIS-002, D1)

- [x] 3.1 RED: reescribir `tests/test_incident_visibility.py` al modelo PROPIO/GLOBAL/VACIO (sin sector): `usuario_final` ve solo lo reportado, `mesa_de_ayuda` y `administrador_directorio` ven todo, sin empleado -> vacio; verificar que falla.
- [x] 3.2 GREEN: actualizar `app/services/incident_visibility.py` (`ModoAlcance` PROPIO/GLOBAL/VACIO, `alcance_desde_empleado` lee el registro de politica y no el sector); verificar el test 3.1.
- [x] 3.3 TRIANGULATE: extender `tests/test_clasificacion_visibility.py` para 404 fuera de alcance en lectura y validacion (ambos roles), preservando 401 anonimo; verificar.
- [x] 3.4 Verificar que el filtrado de `list_incidentes` no aplica filtro por sector como frontera y que la cola FIFO de `revision-pendiente` respeta el alcance.

## 4. Privilegio de identidad (IAH-005, D2)

- [x] 4.1 RED: actualizar `tests/test_c63b_privilege.py` para que el conjunto privilegiado sea `mesa_de_ayuda` + `administrador_directorio`, sin `operador`; verificar que falla.
- [x] 4.2 GREEN: hacer que `PRIVILEGED_ROLE_VALUES`/`is_privileged_role` en `app/services/privilege_service.py` deriven del registro de politica; verificar el test 4.1 y la sincronizacion al vincular/degradar un empleado.

## 5. Directorio: sector opcional y guards por politica (DIR-004, DIR-006)

- [x] 5.1 RED: actualizar `tests/test_directorio_service.py` y `tests/test_api_directorio.py` para que cualquier rol pueda tener o no sector y se elimine la coherencia rol/sector; verificar que fallan.
- [x] 5.2 GREEN: eliminar `_validar_sector_por_rol`/`_ROLES_CON_SECTOR` en `app/services/directorio_service.py` y validar `sector_id` solo como FK opcional al catalogo; verificar los tests.
- [x] 5.3 GREEN: derivar `require_directorio_admin` (gestiona) y `require_directorio_lectura` (`can_read_directory`) en `app/routes/directorio.py` del registro de politica; verificar `tests/test_api_directorio.py` y 403/401.
- [x] 5.4 RED: agregar a `tests/test_api_directorio.py` el conjunto de lectura del directorio (OQ-4/RP-004): `mesa_de_ayuda` -> 200, `administrador_directorio` -> 200, `usuario_final` -> 403, cuenta sin empleado -> 403; verificar que falla contra el guard de lista negra actual (`app/routes/directorio.py:71-78`).
- [x] 5.5 GREEN: reemplazar el guard de lista negra `require_directorio_lectura` por una lista blanca derivada de `can_read_directory` del registro de politica (ningun rol habilitado por omision); verificar 5.4.

## 6. Destinatarios de notificacion de revision (NR-002, D4)

- [x] 6.1 RED: actualizar `tests/test_notification_recipients.py` para que los destinatarios sean todos los `mesa_de_ayuda` activos sin filtro de sector y se excluyan `usuario_final`/`administrador_directorio`/inactivos; verificar que falla.
- [x] 6.2 GREEN: reemplazar `EmpleadoRepository.listar_operadores_por_sector` por `listar_mesa_de_ayuda_activos` (sin sector) en `app/repositories/empleado_repository.py` y quitar el parametro de sector en `NotificationRecipientService.resolver_destinatarios_revision`; actualizar el call site en `app/services/incidente_service.py`; verificar el test 6.1.

## 7. Vinculo de reportante y resolucion por canal (VIS-003, VIS-004, VIS-005, D3, D10)

- [x] 7.1 RED: escribir `tests/test_reporter_link.py` con casos web (via `user_id`), correo (via email del remitente), telefonia (via telefono del llamante), no encontrado -> NULL, ambiguo -> NULL, y no-bloqueo del alta; verificar que falla.
- [x] 7.2 GREEN: agregar `reportante_empleado_id` al modelo `Incidente` y al `create` del repositorio, y un campo opcional de contacto del reportante (`reportante_email`/`reportante_telefono`) en `IncidenteCreate`; verificar el modelo/test.
- [x] 7.3 GREEN: resolver el reportante en `app/routes/incidentes.py` (web: `resolver_por_usuario`; correo/telefonia: `resolver_por_email`/`resolver_por_telefono`) y propagar el id a `IncidenteService.create_and_classify(payload, reportante_empleado_id=...)`, persistiendo NULL ante no encontrado/ambiguo; verificar el test 7.1.
- [x] 7.4 TRIANGULATE: cubrir que el reportante NO altera la clasificacion/sector y que las filas legacy sin reportante son visibles solo para roles GLOBAL; verificar.
- [x] 7.5 RED: extender `tests/test_reporter_link.py` con la derivacion a revision humana (VIS-005/OQ-1): sin contacto de canal -> `requiere_revision_humana=true`; contacto no resoluble -> true; cuenta web sin empleado -> true; OR con el clasificador (una revision ya marcada no se quita); reportante identificado + clasificador sin revision -> false; verificar que falla.
- [x] 7.6 GREEN: aplicar el OR en `IncidenteService.create_and_classify` (`requiere_revision_humana = (confianza < 0.70) OR (reportante no identificado)`), persistiendo NULL y sin bloquear el alta; verificar 7.5.

## 8. Contrato y documentacion tecnica (D3, D7)

- [x] 8.1 Regenerar `docs/openapi.json` con el comando del proyecto y verificar `pytest tests/test_openapi_sync.py -v`.
- [x] 8.2 Verificar que el sobre de error no cambia y que `app/schemas/incidente.py` serializa el nuevo campo de reportante solo donde corresponde.

## 9. Verificacion integrada (todos)

- [x] 9.1 Ejecutar `cd App/Backend; pytest -m "not integration"` y verificar verde (subset SQLite offline).
- [x] 9.2 Ejecutar `cd App/Backend; pytest -m integration` con PostgreSQL y verificar el CHECK nuevo y la FK del reportante.
- [x] 9.3 Buscar duplicacion residual de conocimiento de rol (listas/cadenas de rol fuera del registro) y confirmar que el registro es la fuente unica.
- [x] 9.4 Reconciliar el texto de `openspec/specs/n8n-workflow/spec.md` que afirma `requiere_revision_humana = confianza < 0.70` con el OR de VIS-005 (follow-up documental; el gate post-POST de N8N solo lee el flag booleano y su comportamiento no cambia).
