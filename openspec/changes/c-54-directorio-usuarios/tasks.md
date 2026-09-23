## 1. Preparacion, decisiones y safety net

- [x] 1.1 Registrar en `design.md` las Open Questions RESUELTAS por decision humana (origen/seed, unicidad de campos, roles y sector, ambiguedad, indice ciego MOOT, retencion/ARCO) y actualizar `proposal.md` y los specs si alguna difiere. Verificacion: las seis OQ figuran como RESUELTAS en `design.md` y no queda decision bloqueante de diseno.
- [x] 1.2 Registrar el baseline de las suites afectadas: `cd App/Backend; pytest -m "not integration" tests/test_openapi_sync.py tests/test_auth.py` y anotar el conteo en verde. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificacion: conteo baseline anotado y sin fallos nuevos atribuibles al change.

## 2. Normalizacion y validacion de contacto

- [x] 2.1 RED: escribir `App/Backend/tests/test_contactos.py` que exija (a) normalizacion de email a minusculas/trim; (b) normalizacion de telefono a E.164; (c) validacion de formato de email y E.164. Verificacion: el test falla por modulo inexistente.
- [x] 2.2 GREEN: crear `App/Backend/app/utils/contactos.py` con los normalizadores y validadores puros. Verificacion: los tests de 2.1 pasan.
- [x] 2.3 TRIANGULATE: cubrir telefono invalido respecto de E.164 y email malformado (rechazo accionable), y que la normalizacion es idempotente. Verificacion: casos en verde.

## 3. Modelo, migracion y repositorio

- [x] 3.1 RED: escribir `App/Backend/tests/test_empleado_model.py` que exija la tabla `directorio_empleado` con EXACTAMENTE: `id`, `legajo` (NOT NULL, UNIQUE), `nombre` (NOT NULL), `email` (NOT NULL, UNIQUE, indexado), `telefono` (E.164, NULL, indexado, repetible), `sector_id` (FK nullable a `sector`), `rol` (enum de tres valores), `activo` (default true), `user_id` (FK nullable a `users`), `created_at`/`updated_at`; sin columnas cifradas ni de hash ciego. Verificacion: el test falla por modelo inexistente.
- [x] 3.2 GREEN: crear `App/Backend/app/models/empleado.py` (ORM con columnas en texto plano, enums `RolEmpleado`) y registrarlo en `app/models/__init__.py`. Verificacion: el test de 3.1 pasa en SQLite.
- [x] 3.3 GREEN: crear la migracion aditiva `App/Backend/alembic/versions/009_directorio_empleado.py` (revision `009`, `down_revision = "008"`) con la tabla, los indices (`UNIQUE` en `legajo`/`email`, indice en `telefono`/`sector_id`) y FKs (`ON DELETE SET NULL` para `user_id`). NO sembrar PII real (D9). Verificacion: `cd App/Backend; alembic upgrade head` y `alembic downgrade -1` corren sin error.
- [x] 3.4 RED: escribir `App/Backend/tests/test_empleado_repository.py` que exija busquedas por `email`, por `telefono` y por `user_id`, devolviendo solo empleados activos y usando `selectinload` para `sector` cuando se serializa. Verificacion: el test falla por repositorio inexistente.
- [x] 3.5 GREEN: crear `App/Backend/app/repositories/empleado_repository.py` con las busquedas por email/telefono/`user_id` y CRUD basico. Verificacion: el test de 3.4 pasa.
- [x] 3.6 TRIANGULATE: cubrir busqueda que devuelve multiples coincidencias por telefono (ambiguedad), empleado inactivo excluido, y sector nulo serializado sin lazy-load. Verificacion: casos en verde.
- [x] 3.7 INTEGRATION: agregar `App/Backend/tests/integration/test_directorio_postgres.py` marcado `@pytest.mark.integration` para verificar FK a `sector` y `users`, `UNIQUE` de `legajo`/`email`, indice de `telefono`, `ON DELETE SET NULL` e igualdad real. Verificacion: `cd App/Backend; pytest -m integration tests/integration/test_directorio_postgres.py` en verde contra la base desechable.

## 4. Servicio de directorio, autorizacion y auditoria

- [x] 4.1 RED: escribir `App/Backend/tests/test_directorio_service.py` que exija: alta con validacion de campos (legajo/nombre/email obligatorios; telefono opcional), email unico, telefono repetible, rol valido, E.164, y sector obligatorio cuando el rol es `usuario_final`/`operador` y nulo para `administrador_directorio`; desactivacion en lugar de borrado y borrado fisico solo por ARCO. Verificacion: el test falla por servicio inexistente.
- [x] 4.2 GREEN: crear `App/Backend/app/services/directorio_service.py` con CRUD, reglas de activo/rol, alta de borrado ARCO y validaciones. Verificacion: los tests de 4.1 pasan.
- [x] 4.3 TRIANGULATE: cubrir rol invalido (rechazo), email duplicado (rechazo), `usuario_final`/`operador` sin sector (rechazo), administrador con sector (rechazo), sector inexistente (rechazo), telefono compartido permitido, y reactivacion. Verificacion: casos en verde.
- [x] 4.4 RED: escribir un test que exija que el email/telefono en claro NO aparezca en los logs estructurados ni en la auditoria de una operacion de alta, consulta, desactivacion o borrado, y que la operacion quede registrada con actor/resultado. Verificacion: el test falla contra el logging ingenuo.
- [x] 4.5 GREEN: ajustar los eventos de log/auditoria del servicio para emitir solo identificadores internos y resultado, nunca el dato en claro. Verificacion: el test de 4.4 pasa.

## 5. Resolucion de contactos (seam c-53)

- [x] 5.1 RED: escribir `App/Backend/tests/test_contact_resolution_service.py` que describa `resolver_por_telefono`, `resolver_por_email` y `resolver_por_usuario`, con un `ResultadoResolucion` que distinga encontrado / no encontrado / ambiguo. Verificacion: el test falla por servicio inexistente.
- [x] 5.2 GREEN: crear `App/Backend/app/services/contact_resolution_service.py` con dependencias inyectadas (repositorio) y el modelo de resultado. Verificacion: los tests de 5.1 pasan.
- [x] 5.3 TRIANGULATE: cubrir telefono desconocido, email desconocido, usuario sin empleado vinculado, empleado inactivo, y coincidencia multiple por telefono (ambigua => no concluyente). Verificacion: casos en verde.
- [x] 5.4 TRIANGULATE: cubrir que la resolucion NO envia notificaciones (sin SMS/correo) y que registra trazabilidad (canal + resultado) sin PII en claro. Verificacion: casos en verde.
- [x] 5.5 Verificar el contrato de enganche: test que instancie la resolucion con un directorio vacio y confirme que devuelve "no encontrado" sin excepcion, de modo que c-53 conserve su resolucion directa (RES-005). Verificacion: el test pasa.

## 6. API de gestion, visibilidad por rol, seed y documentacion

- [x] 6.1 RED: escribir `App/Backend/tests/test_api_directorio.py` que exija: escritura con rol `administrador_directorio` (exito), escritura con otro rol (403), acceso anonimo (401), y lectura autorizada. Verificacion: el test falla por rutas inexistentes.
- [x] 6.2 GREEN: crear `App/Backend/app/schemas/directorio.py`, `App/Backend/app/routes/directorio.py` y la dependencia de autorizacion acotada al directorio; registrar el router. Verificacion: los tests de 6.1 pasan.
- [x] 6.3 TRIANGULATE: cubrir que las respuestas y los errores no incluyen datos personales innecesarios y que la auditoria de accesos a la API queda registrada sin PII. Verificacion: casos en verde.
- [x] 6.4 RED: escribir `App/Backend/tests/test_incident_visibility.py` que exija: `administrador_directorio` ve incidentes de todos los sectores; `usuario_final`/`operador` con sector S ve solo los de S; cuenta sin sector ve un alcance vacio; acceso puntual a un incidente fuera de sector responde como no encontrado. Verificacion: el test falla por filtro inexistente.
- [x] 6.5 GREEN: implementar el filtro de visibilidad por rol en la capa de API/servicio de incidentes (D7), sin tocar clasificacion ni notificaciones. Verificacion: los tests de 6.4 pasan.
- [x] 6.6 GREEN: crear el seed dev-only idempotente (un usuario sintetico por rol, con contacto util) que cree AMBAS filas `users` (login) y `directorio_empleado` enlazadas por `user_id`, incluyendo el primer administrador (OQ1); sin PII real. Verificacion: reejecutar el seed no duplica filas y deja un administrador operativo.
- [x] 6.7 Regenerar `docs/openapi.json` con el comando documentado y ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v`. Verificacion: el test de sincronizacion pasa.
- [x] 6.8 Documentar el directorio (campos, roles, resolucion, texto plano + minimizacion, retencion/ARCO, visibilidad por rol y el punto de enganche con c-53), sin PII de ejemplo real y dejando explicito que el frontend de visibilidad se difiere. Verificacion: documentacion verificable y coherente con los specs.

## 7. Verificacion final

- [x] 7.1 Ejecutar la suite offline: `cd App/Backend; pytest -m "not integration"`. Verificacion: sin regresiones respecto del baseline de 1.2.
- [x] 7.2 Ejecutar la suite de integracion del directorio: `cd App/Backend; pytest -m integration`. Verificacion: en verde contra la base desechable, sin tocar la base de aplicacion.
- [x] 7.3 Ejecutar lint: `cd App/Backend; ruff check .`. Verificacion: sin errores E nuevos.
- [x] 7.4 Ejecutar `openspec validate --strict --changes c-54-directorio-usuarios`. Verificacion: validacion estricta sin errores.
- [ ] 7.5 Revision humana (HIGH): confirmar la politica de retencion/ARCO, la regla de visibilidad de incidentes por rol y su alcance, y que no hay PII real en el repositorio ni en la base; confirmar que no se agrego clave de indice ciego. Verificacion: aprobacion registrada antes de activar datos reales. PENDIENTE DE REVISION HUMANA (no ejecutada por el agente): la implementacion usa datos SINTETICOS; activar datos reales queda bloqueado hasta esta aprobacion.

## 8. Fixes de la verificacion adversarial (W1-W3 + nits)

- [x] 8.1 RED/GREEN (W1): test que exige que un 422 de schema NO refleje el valor enviado; sanear el envelope global (`_sanitize_validation_errors`) conservando solo `loc`/`msg`/`type`. Verificacion: `tests/test_validation_error_sanitization.py` y `tests/test_api_directorio.py::test_error_de_schema_no_refleja_el_telefono` en verde.
- [x] 8.2 RED/GREEN (W2 modelo): agregar `fecha_baja` nullable al modelo y la migracion append-only `010` (`down_revision = "009"`); actualizar el test de columnas exactas. Verificacion: `tests/test_empleado_model.py` y `tests/test_migration_010_fecha_baja.py` en verde.
- [x] 8.3 RED/GREEN (W2 retencion): sellar `fecha_baja` al desactivar y limpiarla al reactivar; `retencion_vencida` pura; `DirectorioService.purgar_vencidos` idempotente que borra `activo=false AND fecha_baja + 1 año <= ahora` y loggea el conteo sin PII; script CLI `scripts/purgar_directorio.py`. Verificacion: tests de retencion (baja < 1 año conservada, > 1 año purgada, activo conservado) y del script en verde.
- [x] 8.4 (W2 docs): actualizar `design.md` (D6b/D8/D9/D14/D15 y plan de migracion), el spec DIR-002/DIR-007, `docs/directorio-usuarios.md`, la tabla de `fecha_baja` en la tesis v8 y este `tasks.md`. Verificacion: la retencion queda implementada y documentada, no aspiracional.
- [x] 8.5 RED/GREEN (W3): propagar `alcance` a `update_incidente` y a la ruta PATCH; un no administrador que muta un incidente fuera de sector recibe 404 y el incidente NO se modifica; el administrador si puede. Verificacion: tests de visibilidad de escritura en verde.
- [x] 8.6 (N1): test HTTP de acceso puntual por ID con alcance vacio (sin empleado) que responde 404, tanto GET como PATCH. Verificacion: en verde.
- [x] 8.7 (N3): `EmpleadoRepository.get_by_user_id` robusto ante duplicados (`first()` determinista) con test. Verificacion: en verde.
- [x] 8.8 (N2): test de caracterizacion de que el rol del directorio no altera la clasificacion. Verificacion: en verde.
- [x] 8.9 Verificacion final: `pytest -m "not integration"`, `pytest -m integration`, `ruff check .`, `pytest tests/test_openapi_sync.py -v` y `openspec validate --strict --changes c-54-directorio-usuarios`. Verificacion: todo en verde, sin regresiones.
- [x] 8.10 RED/GREEN (W1 completo): un 422 no debe reflejar el valor sometido NI por `msg` — se reescriben con mensaje generico (sin interpolar el valor) los validadores custom de `origen_evento`/`sector_predicho`/`sectores_adicionales` (incidente) y `sector_validado`/`sectores_adicionales` (clasificacion); el `loc` conserva la identificacion del campo y el saneador global queda como defensa en profundidad. Triangulacion: 5 validadores custom + 1 restriccion built-in (max_length). Verificacion: `tests/test_validation_error_sanitization.py` (7) y `tests/test_api_directorio.py::test_error_de_schema_no_refleja_el_telefono` en verde; ningun 422 representativo refleja el valor.