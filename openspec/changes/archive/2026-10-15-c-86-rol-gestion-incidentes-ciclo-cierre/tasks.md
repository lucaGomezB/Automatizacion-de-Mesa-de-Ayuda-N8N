## 1. Migracion y modelos (rol, campos y tablas nuevas)

- [x] 1.1 Agregar `RolEmpleado.gestion_incidentes` en `App/Backend/app/models/empleado.py` y ampliar el CHECK `ck_directorio_empleado_rol` a cuatro valores; verificar que el modelo importa sin errores (`cd App/Backend; python -c "from app.models.empleado import RolEmpleado; print([r.value for r in RolEmpleado])"`)
- [x] 1.2 Crear la migracion `alembic/versions/018_gestion_incidentes_ciclo_cierre.py` que recrea el CHECK a cuatro valores y crea `incidente_cierre_sector`, `incidente_evento` e `incidente_comentario` (FKs e indices); verificar `cd App/Backend; alembic upgrade head` y luego `alembic downgrade -1 && alembic upgrade head`
- [x] 1.3 RED: escribir tests de modelo/migracion que afirmen el CHECK de cuatro valores, la PK compuesta de `incidente_cierre_sector` y las FKs (CASCADE/SET NULL/RESTRICT); confirmar que fallan antes de la migracion
- [x] 1.4 GREEN: ajustar la migracion y los modelos nuevos (`app/models/asociaciones.py` o `app/models/incidente.py`) hasta que los tests de 1.3 pasen
- [x] 1.5 TRIANGULAR: agregar el caso de downgrade que reasigna `gestion_incidentes -> usuario_final` antes de restaurar el CHECK de tres valores y confirmar que el `downgrade` no deja datos que violen el CHECK

## 2. Registro canonico de politica y coherencia (role-policy)

- [x] 2.1 RED: extender `App/Backend/tests/test_role_policy.py` (o equivalente) para exigir cuatro roles, el modo `SECTOR`, `requires_sector` verdadero solo en `gestion_incidentes` y los atributos `post_review_recipient`/`edita_estado`/`cierra_sector`/`cierra_global`/`reabre`; confirmar que falla
- [x] 2.2 GREEN: agregar `ModoAlcance.SECTOR`, extender `PoliticaRol` y `ROLE_POLICY` con el cuarto rol en `App/Backend/app/services/role_policy.py`; confirmar que 2.1 pasa
- [x] 2.3 TRIANGULAR: agregar el test de coherencia RP-003 (CHECK/enum/registro coinciden en cuatro valores; un rol SECTOR exige `requires_sector`) y confirmar que pasa (`cd App/Backend; pytest tests/ -k "role_policy or coheren"))

## 3. Visibilidad del alcance SECTOR (incident-visibility)

- [x] 3.1 RED: escribir tests de `incident_visibility` para la derivacion SECTOR (con sector -> SECTOR con `sector_id`; `gestion_incidentes` sin sector -> VACIO) y para `permite_incidente` (pertenece por principal, por adicional, no pertenece, cierre por sector) y confirmar que fallan
- [x] 3.2 GREEN: extender `AlcanceIncidentes` (campo `sector_id`), `alcance_desde_empleado` y `permite_incidente` en `App/Backend/app/services/incident_visibility.py`; confirmar que 3.1 pasa
- [x] 3.3 RED: escribir test de repositorio para el filtrado SECTOR (pertenencia al conjunto por principal o adicional, exclusion de cerrados para el sector y de `estado=cerrado`) en `App/Backend/tests/`; confirmar que falla
- [x] 3.4 GREEN: implementar el filtro SECTOR (subconsulta a `incidente_sector_adicional` + `NOT EXISTS` contra `incidente_cierre_sector`) en `App/Backend/app/repositories/incidente_repository.py`, reutilizado por `list_filtered`; confirmar que 3.3 pasa
- [x] 3.5 TRIANGULAR: tests de API por rol (gestion ve solo su sector; no ve otro sector -> 404; sin sector -> vacio) y de clasificaciones por incidente con alcance SECTOR; confirmar verdes
- [x] 3.6 Agregar un test de integracion PostgreSQL (`@pytest.mark.integration`) del filtrado SECTOR con multiples sectores y cierres, y verificar `cd App/Backend; pytest -m integration -k sector`

## 4. Ciclo de cierre: por sector, global y terminal (incident-lifecycle)

- [x] 4.1 RED: escribir tests de servicio para el cierre por sector (inserta fila con actor; idempotente; saca de la vista activa; agregado al historial del sector) y confirmar que fallan
- [x] 4.2 GREEN: implementar el cierre por sector (repositorio + servicio) y el endpoint `POST /api/v1/incidentes/{id}/cierre-sector` en `App/Backend/app/routes/incidentes.py`; confirmar que 4.1 pasa
- [x] 4.3 RED: escribir tests de servicio para el cierre global (cierra todos los sectores; fija `cerrado`; incidente sin sector) y confirmar que fallan
- [x] 4.4 GREEN: implementar el cierre global y el endpoint `POST /api/v1/incidentes/{id}/cierre-global`; confirmar que 4.3 pasa
- [x] 4.5 RED: escribir tests de la transicion terminal (todos los sectores cerrados -> `cerrado`; cierre parcial -> no `cerrado`; `cerrado` no se fija por edicion) y confirmar que fallan
- [x] 4.6 GREEN: implementar la verificacion "todos los sectores cerrados" y la transicion terminal; confirmar que 4.5 pasa
- [x] 4.7 TRIANGULAR: tests de API de autorizacion (gestion no cierra global; mesa de ayuda cierra global; gestion no cierra fuera de su sector -> 404; anonimo -> 401) y confirmar verdes

## 5. Reapertura y edicion de estado (incident-lifecycle)

- [x] 5.1 RED: escribir tests de servicio para la reapertura (limpia cierres; `en proceso`; registra `incidente_evento`; rechaza si no esta cerrado; solo mesa de ayuda) y confirmar que fallan
- [x] 5.2 GREEN: implementar la reapertura y el endpoint `POST /api/v1/incidentes/{id}/rehabilitar`; confirmar que 5.1 pasa
- [x] 5.3 RED: escribir tests de la edicion de estado (`en proceso`/`en espera`/`resuelto`; `cerrado` -> 422; gestion solo su sector; usuario_final y administrador -> 403) y confirmar que fallan
- [x] 5.4 GREEN: implementar la edicion de estado y el endpoint `PATCH /api/v1/incidentes/{id}/estado`; confirmar que 5.3 pasa
- [x] 5.5 TRIANGULAR: test de que el incidente reabierto vuelve a la vista activa de su sector y de que la reapertura por un rol no autorizado no muta nada; confirmar verdes

## 6. Auditoria de ciclo de vida (incident-lifecycle)

- [x] 6.1 RED: escribir tests que exijan un `incidente_evento` con tipo, actor y fecha en cierre por sector, cierre global, reapertura y cambio de estado, y que la trazabilidad no incluya PII; confirmar que fallan
- [x] 6.2 GREEN: implementar la escritura de `incidente_evento` en los servicios de ciclo y el repositorio correspondiente; confirmar que 6.1 pasa
- [x] 6.3 TRIANGULAR: test de que el borrado ARCO de un empleado (SET NULL) preserva el evento sin PII y de que no se duplican eventos por reintentos idempotentes; confirmar verdes

## 7. Comentarios append-only (incident-comments)

- [x] 7.1 RED: escribir tests de servicio/repositorio de alta y listado de comentarios (append-only, sin numeracion, orden cronologico, permiso por visibilidad, fuera de alcance -> 404) y confirmar que fallan
- [x] 7.2 GREEN: implementar `incidente_comentario` (repositorio + servicio) y los endpoints `GET`/`POST /api/v1/incidentes/{id}/comentarios`; confirmar que 7.1 pasa
- [x] 7.3 RED: escribir el test del formato de presentacion (`HH:MM:SS DD/MM/AAAA : {texto}`, separador `----------`, zona `America/Argentina/Buenos_Aires` independiente del servidor) y confirmar que falla
- [x] 7.4 GREEN: implementar el formateo reutilizando `app/utils/business_time.py`; confirmar que 7.3 pasa
- [x] 7.5 TRIANGULAR: tests por rol (usuario_final propio; gestion su sector; GLOBAL cualquiera; anonimo 401) y de que no existe endpoint de edicion/borrado; confirmar verdes

## 8. Historial de cerrados (incident-visibility)

- [x] 8.1 RED: escribir tests de servicio/repositorio del historial por alcance (GLOBAL -> `cerrado`; SECTOR -> cierre de su sector inmediato; PROPIO -> propios cerrados; excluye eliminados) y confirmar que fallan
- [x] 8.2 GREEN: implementar el filtrado del historial en `incidente_repository`/servicio y el endpoint `GET /api/v1/incidentes/historial-cerrados` declarado ANTES de `GET /{id}`; confirmar que 8.1 pasa
- [x] 8.3 TRIANGULAR: test de API por rol y de que un incidente cerrado solo por un sector aparece en el historial de ese sector y no en el de otro; confirmar verdes

## 9. Aviso post-revision (notification-routing)

- [x] 9.1 RED: escribir tests de `NotificationRecipientService.resolver_destinatarios_gestion(sector_ids)` (gestion activos de los sectores; sin duplicados; otros roles excluidos; lista vacia no fatal) y confirmar que fallan
- [x] 9.2 GREEN: agregar `EmpleadoRepository.listar_activos_por_rol_y_sectores` y el metodo de resolucion en `App/Backend/app/services/notification_recipient_service.py`; confirmar que 9.1 pasa
- [x] 9.3 RED: escribir test que afirme que la validacion exitosa dispara (fire-and-forget) el aviso con `destinatarios_gestion` y no altera la respuesta; confirmar que falla
- [x] 9.4 GREEN: implementar `notify_n8n_post_revision(incidente_id, sectores, destinatarios)` en `App/Backend/app/utils/n8n_webhook.py` y el disparo en `ClasificacionService.validate`; confirmar que 9.3 pasa
- [x] 9.5 TRIANGULAR: test sin destinatarios (`destinatarios_gestion: []`, sin excepcion) y de no-PII en logs; confirmar verdes
- [x] 9.6 Actualizar `n8n/workflow.json` para entregar el correo del aviso post-revision a `destinatarios_gestion` y documentar el marcador `incidente_validado_gestion`; verificar la importacion del workflow sin romper los flujos existentes

## 10. Contrato OpenAPI

- [x] 10.1 Regenerar `docs/openapi.json` con el comando documentado en `AGENTS.md` y verificar la sincronizacion (`cd App/Backend; pytest tests/test_openapi_sync.py -v`)

## 11. Frontend: alcance SECTOR, historial, ciclo y comentarios

- [x] 11.1 RED: escribir test de que el estado de autenticacion expone el alcance `SECTOR` y de que el guard/navegacion admiten `SECTOR` en la superficie operativa; confirmar que falla
- [x] 11.2 GREEN: actualizar tipos, contexto de autenticacion, guard y navegacion para `SECTOR`; confirmar que 11.1 pasa
- [x] 11.3 RED: escribir test de servicio/hook del historial (`useHistorialCerrados`) que consuma `GET /incidentes/historial-cerrados`; confirmar que falla
- [x] 11.4 GREEN: implementar el tipo, el servicio y el hook del historial; confirmar que 11.3 pasa
- [x] 11.5 RED: escribir test de la pestana "Historial de Incidentes Cerrados" (estado mostrado "Cerrado"; respeta el alcance; no muestra eliminados) y confirmar que falla
- [x] 11.6 GREEN: agregar `TabActiva = 'tickets' | 'revision' | 'historial'` y `HistorialTable` en `App/Frontend/src/pages/Administracion/`; confirmar que 11.5 pasa
- [x] 11.7 RED: escribir tests de las acciones de ciclo en el detalle (cerrar por sector/global, reabrir, editar estado; gestion no ve cierre global/reabrir) y confirmar que fallan
- [x] 11.8 GREEN: implementar los hooks/servicios de mutacion y las acciones en el detalle con permisos por alcance; confirmar que 11.7 pasa
- [x] 11.9 RED: escribir test de la seccion de comentarios (formato `HH:MM:SS DD/MM/AAAA : {texto}`, separador `----------`, alta de comentario) y confirmar que falla
- [x] 11.10 GREEN: implementar la seccion de comentarios en el detalle; confirmar que 11.9 pasa
- [x] 11.11 TRIANGULAR: test de manejo de 403/404 en las acciones y de que la UI no amplia el alcance del backend; confirmar verdes

## 12. Verificacion integral

- [x] 12.1 Ejecutar la suite backend offline y confirmar verde (`cd App/Backend; pytest -m "not integration"`) — 1379 passed, 46 deselected, 1 xfailed
- [x] 12.2 Ejecutar la interseccion PostgreSQL y confirmar verde (`cd App/Backend; pytest -m integration`) — 46 passed (DB descartable provisionada y eliminada)
- [x] 12.3 Ejecutar lint backend y confirmar verde (`cd App/Backend; ruff check .`) — sin violaciones
- [x] 12.4 Ejecutar la suite frontend con coverage y confirmar verde (`cd App/Frontend; npm run test:coverage`) — 44 files / 261 tests verdes en re-corrida; la primera corrida tuvo 2 timeouts de 5000ms en IncidenteForm.test.tsx bajo carga concurrente (flaky under load, no defecto funcional)
- [x] 12.5 Ejecutar lint y build del frontend y confirmar verdes (`cd App/Frontend; npm run lint && npm run build`) — cumplido con `npm run lint` + `npx tsc --noEmit` (regla dura del proyecto: no buildear tras cambios); 0 errores lint, 0 type errors
- [x] 12.6 Ejecutar `openspec validate c-86-rol-gestion-incidentes-ciclo-cierre --strict` y confirmar que pasa — valido
