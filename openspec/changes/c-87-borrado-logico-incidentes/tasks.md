## 1. Modelo y migración

- [x] 1.1 Agregar `deleted_at` (`DateTime(timezone=True)`, nullable) y `deleted_by` (FK a `directorio_empleado.id`, `ondelete="SET NULL"`, nullable, indexada) a `Incidente` en `app/models/incidente.py`; verificar que el import de `Incidente` y las relaciones existentes siguen cargando (`pytest -m "not integration"` mínimo de smoke del módulo)
- [x] 1.2 Generar la migración aditiva `019_soft_delete_incidente.py` (`down_revision = "018"`) con `alembic revision --autogenerate -m "add soft delete columns to incidente"`; verificar que el `upgrade` agrega solo las dos columnas y el `downgrade` las elimina
- [x] 1.3 Aplicar la migración contra PostgreSQL y verificar que `incidente.deleted_at` y `deleted_by` existen con los tipos/nullability esperados (`alembic upgrade head`)

## 2. Repositorio: borrado lógico y exclusión

- [x] 2.1 RED: escribir tests de `soft_delete` (setea `deleted_at`/`deleted_by`, no elimina la fila, devuelve 1 fila afectada) y de exclusión (`get_with_relations` y `list_filtered` no devuelven incidentes con `deleted_at` no nulo); ejecutar y confirmar que fallan
- [x] 2.2 GREEN: implementar `IncidenteRepository.soft_delete(incidente_id, *, deleted_by, deleted_at) -> int` con `UPDATE` Core; verificar que los tests de 2.1 pasan
- [x] 2.3 GREEN: agregar la condición por defecto `Incidente.deleted_at.is_(None)` en `get_with_relations` y `list_filtered`; verificar que los tests de exclusión pasan
- [x] 2.4 TRIANGULAR: cubrir casos borde (incidente inexistente devuelve 0 filas; incidente borrado no aparece en ningún filtro del listado; incidente activo sí aparece) y verificar que pasan
- [x] 2.5 REFACTOR: extraer la condición de exclusión a un helper reutilizable del repositorio si reduce duplicación; re-ejecutar los tests de exclusión y confirmar que siguen verdes

## 3. Política de rol

- [x] 3.1 RED: escribir tests de `role_policy` que exijan `can_delete_incident` verdadero solo para `administrador_directorio` y la derivación `roles_con_borrado_incidentes()`; ejecutar y confirmar que fallan
- [x] 3.2 GREEN: agregar `can_delete_incident` a `PoliticaRol` y a cada entrada de `ROLE_POLICY`, más la derivación `roles_con_borrado_incidentes()`; verificar que los tests pasan
- [x] 3.3 TRIANGULAR: verificar que el test de coherencia de vocabulario existente (RP-003) sigue pasando y que ningún rol fuera de `administrador_directorio` habilita el borrado

## 4. Servicio

- [x] 4.1 RED: escribir tests de `IncidenteService.soft_delete_incidente` (incidente visible y activo se marca con `deleted_by` = actor y `deleted_at` no nulo; incidente inexistente lanza `EntityNotFoundError`; incidente borrado lanza `EntityNotFoundError`; incidente fuera de alcance lanza `EntityNotFoundError`); ejecutar y confirmar que fallan
- [x] 4.2 GREEN: implementar `soft_delete_incidente(incidente_id, *, actor_empleado_id, alcance)` reutilizando `get_by_id(..., alcance=...)` y delegando en `repo.soft_delete`; verificar que los tests de 4.1 pasan
- [x] 4.3 TRIANGULAR: cubrir que la operación NO borra físicamente (la fila sigue existiendo con `deleted_at` no nulo) y que un segundo borrado se comporta como no encontrado; verificar que pasan

## 5. Endpoint y OpenAPI

- [x] 5.1 RED: escribir tests de API de `DELETE /api/v1/incidentes/{id}` (admin borra y recibe 204 sin cuerpo; `mesa_de_ayuda` y `usuario_final` reciben 403; incidente fuera de alcance o ya borrado recibe 404; sin token 401; la fila persiste tras el 204); ejecutar y confirmar que fallan
- [x] 5.2 GREEN: agregar la dependencia `require_borrado_incidentes` (derivada de `can_delete_incident`) y el endpoint `DELETE /{incidente_id}` con `status_code=204`; verificar que los tests de 5.1 pasan
- [x] 5.3 TRIANGULAR: verificar que un administrador no puede ver un incidente borrado en el listado ni en el detalle (404) tras borrarlo; confirmar que pasa
- [x] 5.4 Regenerar `docs/openapi.json` con el comando documentado y verificar que `pytest tests/test_openapi_sync.py -v` pasa

## 6. Frontend

- [x] 6.1 RED: escribir tests de Vitest de la acción admin-only (visible con rol `administrador_directorio`, oculta para `mesa_de_ayuda`/`usuario_final`, exige confirmación, cancelación no invoca el backend, éxito invalida el listado, 403/404 se maneja sin exponer el recurso); ejecutar y confirmar que fallan
- [x] 6.2 GREEN: agregar el cliente `DELETE` (servicio), el hook de mutación con invalidación de listados y la acción con confirmación en `TicketDetailDialog.tsx` condicionada al rol; verificar que los tests de 6.1 pasan
- [x] 6.3 TRIANGULAR: cubrir que tras el borrado exitoso el incidente desaparece de la vista y que el estado de error no muestra datos del recurso; verificar que pasan
- [x] 6.4 Ejecutar `npm run lint` y `npm run test` en `App/Frontend/` y confirmar que pasan
  - Nota: por el alcance de verificación acordado (targeted, no full-suite) se ejecutaron `npm run lint`, `npx tsc --noEmit` y SOLO los archivos Vitest nuevos/afectados (`TicketDetailDialog.test.tsx`, `incidentesService.test.ts`), no la suite completa.

## 7. Verificación integral

- [x] 7.1 Ejecutar `pytest -m "not integration"` en `App/Backend/` y confirmar que pasa el subconjunto SQLite
  - Ejecutado durante el cierre de c-86 (misma suite, mismo estado de código, c-87 ya commiteado): 1379 passed, 46 deselected, 1 xfailed.
- [x] 7.2 Ejecutar `pytest -m integration` en `App/Backend/` con PostgreSQL disponible y confirmar que pasa el subconjunto de integración (incluida la migración)
  - Ejecutado durante el cierre de c-86: 46 passed con PostgreSQL (base descartable provisionada y eliminada). Adicionalmente la migración 019 se había verificado con `upgrade`/`downgrade` contra PostgreSQL en la fase de apply.
- [x] 7.3 Ejecutar `openspec validate c-87-borrado-logico-incidentes --strict` y confirmar que pasa sin errores
