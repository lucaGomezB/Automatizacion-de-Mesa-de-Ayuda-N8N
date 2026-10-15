## Why

El sistema no ofrece hoy ninguna forma de RETIRAR de circulacion un incidente erroneo, duplicado o cargado por error: no existen columnas de borrado logico y el unico borrado disponible en el repositorio (`hard_delete`) es fisico y solo lo usa una herramienta interna, no una operacion de negocio con control de rol. A la vez, el ciclo de cierre introducido por `c-86-rol-gestion-incidentes-ciclo-cierre` sumara una pestaña "Historial de Incidentes Cerrados" que, sin un marcador de borrado, seguiria mostrando filas retiradas. Se necesita un borrado LOGICO gobernado por rol que preserve la fila (auditoria, Ley 25.326) y la oculte de toda superficie de lectura.

## What Changes

- El modelo `Incidente` gana dos columnas nullable: `deleted_at` (datetime) y `deleted_by` (FK a `directorio_empleado.id`). Un borrado logico las setea ambas; la fila se conserva.
- Nueva operacion `DELETE /api/v1/incidentes/{incidente_id}` que ejecuta el borrado LOGICO (no fisico) y registra la atribucion del actor.
- La autorizacion se enforca server-side mediante el registro canonico de politica de rol (`app/services/role_policy.py`): SOLO `administrador_directorio` puede borrar. Un rol no administrador recibe 403; un incidente fuera del alcance del llamante se comporta como no encontrado (404), consistente con la semantica de alcance vigente.
- Los incidentes borrados logicamente quedan EXCLUIDOS de todas las superficies de lectura: listado `GET /incidentes`, detalle `GET /incidentes/{id}` (404), colas de error/revision donde aplique, y la futura pestaña "Historial de Incidentes Cerrados". Nunca se exponen en la UI.
- El Panel de Administracion gana una accion EXCLUSIVA de `administrador_directorio` para borrar logicamente un incidente (desde el dialogo de detalle del ticket y/o por fila), con un paso de confirmacion. No se expone a otros roles.
- Se regenera `docs/openapi.json` (lo guarda `tests/test_openapi_sync.py`).
- No hay migracion de datos destructiva: las filas existentes quedan con `deleted_at`/`deleted_by` en NULL (no borradas).

## Capabilities

### New Capabilities

- `incident-soft-delete`: modelo de borrado logico del incidente (columnas `deleted_at`/`deleted_by`), el endpoint `DELETE /api/v1/incidentes/{id}` que lo ejecuta, la autorizacion exclusiva de `administrador_directorio` y la atribucion del actor.

### Modified Capabilities

- `role-policy`: agrega un atributo de politica `can_delete_incident` al registro canonico (RP-005), verdadero solo para `administrador_directorio`, del que deriva el guard del endpoint de borrado logico.
- `incident-visibility`: agrega un requisito (VIS-009) que excluye a los incidentes borrados logicamente de todas las superficies de lectura (listado, detalle, colas de revision y pestaña de historial de cerrados), sin revelar su existencia.
- `frontend-rbac`: agrega un requisito (FR-RBAC-006) para que la accion de borrado logico sea visible y ejecutable unicamente por `administrador_directorio`, con confirmacion, y oculta para el resto de los roles.

## Impact

- Backend:
  - `App/Backend/app/models/incidente.py` — columnas `deleted_at` y `deleted_by` (FK nullable a `directorio_empleado.id`, `ON DELETE SET NULL`).
  - `App/Backend/alembic/versions/` — migracion aditiva `019` (`down_revision = "018"`) de las dos columnas.
  - `App/Backend/app/repositories/incidente_repository.py` — filtro de exclusion por defecto (`deleted_at IS NULL`) en `list_filtered`/`get_with_relations`, y un metodo de borrado logico (p. ej. `soft_delete`) que setea `deleted_at`/`deleted_by`. NO se reutiliza `hard_delete`.
  - `App/Backend/app/services/role_policy.py` — atributo `can_delete_incident` en `PoliticaRol` y su derivacion.
  - `App/Backend/app/services/incidente_service.py` — metodo `soft_delete_incidente(incidente_id, actor, alcance)` que verifica alcance + existencia y delega en el repositorio.
  - `App/Backend/app/routes/incidentes.py` — endpoint `DELETE /{incidente_id}` con guard de rol derivado de `role_policy`, respuesta 204.
  - `docs/openapi.json` — regenerar (existe `tests/test_openapi_sync.py`).
- Frontend:
  - `App/Frontend/src/pages/Administracion/TicketDetailDialog.tsx` — accion de borrado logico con confirmacion, condicionada al rol `administrador_directorio`.
  - `App/Frontend/src/services/incidentesService.ts` (o equivalente) — cliente del endpoint `DELETE`.
  - `App/Frontend/src/hooks/` — hook de mutacion + invalidacion de listados.
  - `App/Frontend/src/types/incidente.ts` — tipo del resultado del borrado.
- Tests: backend (unit SQLite + integracion PostgreSQL), frontend (Vitest), sincronizacion OpenAPI.
- Dependencia blanda: la pestaña "Historial de Incidentes Cerrados" pertenece a `c-86-rol-gestion-incidentes-ciclo-cierre`; este change NO la implementa, pero su requisito de exclusion (VIS-009) la condiciona.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|-----------|
| Filas borradas se filtran por una consulta que no excluye `deleted_at` | Media | El filtro de exclusion vive en el repositorio (punto unico) para `list_filtered` y `get_with_relations`; escenarios de VIS-009 lo cubren por superficie |
| Reutilizar `hard_delete` por error borra la fila | Baja | El change define explicitamente un camino NUEVO de borrado logico; `hard_delete` queda sin uso en la ruta de negocio |
| La autorizacion se duplica con listas de rol en la ruta | Baja | El guard deriva de `role_policy.can_delete_incident` (fuente unica), como exige RP-002 |
| La accion de UI se filtra a roles no administradores | Media | Se condiciona al rol del usuario autenticado ya expuesto por la UI (FR-RBAC-001); el backend igualmente responde 403 |
| `docs/openapi.json` desincronizado | Baja | `test_openapi_sync.py` falla si no se regenera; tarea obligatoria del apply |
| Incidentes ya cerrados en el historial no se ocultan | Baja | VIS-009 exige la exclusion tambien en la pestaña de historial; escenario explicito por superficie |

## Rollback Plan

Revertir el commit del change. La migracion es ADITIVA (dos columnas nullable): revertirla elimina las columnas sin perdida de datos de negocio (ninguna fila se borro fisicamente). El endpoint y el guard desaparecen; el frontend vuelve a no ofrecer la accion. Si se revierte la migracion con filas ya marcadas, el marcador se pierde y esas filas vuelven a ser visibles: por eso el rollback recomendado conserva las columnas y solo revierte el codigo.

## Success Criteria

- [ ] `DELETE /api/v1/incidentes/{id}` con `administrador_directorio` marca la fila (`deleted_at` y `deleted_by`) y responde 204 sin borrarla fisicamente.
- [ ] Un rol distinto de `administrador_directorio` recibe 403; no modifica ninguna fila.
- [ ] Un incidente fuera del alcance del llamante responde 404 y no se modifica.
- [ ] Un incidente borrado no aparece en el listado, responde 404 en el detalle y no aparece en la cola de revision ni en el historial de cerrados.
- [ ] La accion de UI solo es visible/ejecutable para `administrador_directorio` y exige confirmacion.
- [ ] La suite backend (SQLite + integracion), la suite frontend y el test de sincronizacion OpenAPI pasan.

## Open Questions

1. **UX de confirmacion: RESUELTO.** Paso de confirmacion modal antes de ejecutar la accion (patron de dialogo de confirmacion ya presente en la UI); la accion se ofrece desde el detalle del ticket y, opcionalmente, por fila.
2. **Respuesta del endpoint: RESUELTO.** HTTP 204 No Content sin cuerpo (operacion idempotente sobre el recurso).
3. **Referencia de `deleted_by`: RESUELTO.** FK a `directorio_empleado.id` (empleado), por consistencia con el vinculo de reportante de c-82 (`reportante_empleado_id`), con `ON DELETE SET NULL` para no perder el incidente si el empleado se borra por ARCO.
4. **Reutilizar `hard_delete`: RESUELTO.** NO. Se implementa un camino nuevo de borrado logico; `hard_delete` no se usa en la ruta de negocio.
5. **Idempotencia del borrado repetido: RESUELTO.** Un segundo `DELETE` sobre un incidente ya borrado responde 404 (el incidente ya no es visible), consistente con VIS-009.
