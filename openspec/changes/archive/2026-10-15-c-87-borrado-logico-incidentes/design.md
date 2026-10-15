## Context

Ver `proposal.md` — Why. Estado actual relevante (verificado):

- `Incidente` (`app/models/incidente.py`) NO tiene columnas de borrado. `TimestampMixin` aporta `created_at`/`updated_at`. Las FKs de dominio usan `directorio_empleado.id` (patron de `reportante_empleado_id`, c-82) con `ON DELETE SET NULL`.
- `IncidenteRepository` (`app/repositories/incidente_repository.py`) tiene `get_with_relations`, `list_filtered` y un `hard_delete` fisico (solo usado por una herramienta interna, no por una ruta de negocio). No existe camino de borrado logico.
- La autorizacion de rol vive en `role_policy.py` (`PoliticaRol` + `ROLE_POLICY`); `administrador_directorio` es el unico rol con `manages_directory=True`. Los guards de ruta derivan de ese registro (patron de `routes/directorio.py`, `require_directorio_admin`).
- El alcance de visibilidad (VIS-001) se aplica en `IncidenteService.get_by_id` / `list_incidentes` via `AlcanceIncidentes`; un incidente fuera de alcance se comporta como 404.
- El frontend ya conoce el rol y el alcance del usuario (FR-RBAC-001) y tiene `TicketDetailDialog.tsx` para el detalle del ticket.
- Restricciones: capas `routes -> services -> repositories`; SQLAlchemy async (nunca lazy-load de relationships serializados); español tecnico neutro; sin emojis; TDD estricto con escenarios testeables.

## Goals / Non-Goals

**Goals:**

- Borrado LOGICO reversible por diseño (la fila persiste) con `deleted_at`/`deleted_by` y atribucion del actor.
- Exclusion de los incidentes borrados en un PUNTO UNICO de la capa de datos, para que ninguna consulta de lectura los exponga.
- Autorizacion exclusiva de `administrador_directorio` derivada de `role_policy` (fuente unica), con semantica 403 / 404 consistente con el alcance vigente.
- Endpoint `DELETE /api/v1/incidentes/{id}` que responde 204 y ejecuta borrado logico.
- Accion de UI admin-only con confirmacion.

**Non-Goals:**

- No se implementa la pestaña "Historial de Incidentes Cerrados" (pertenece a `c-86`); solo se condiciona su exclusion.
- No se hace borrado fisico ni purga de datos: el `hard_delete` existente queda fuera del camino de negocio.
- No se agrega "deshacer borrado" (restaurar) en este change.
- No se cambia el contrato del listado (sigue siendo un array).

## Decisions

### D1 — Columnas `deleted_at` y `deleted_by` en `Incidente`

**Decision:** agregar `deleted_at: datetime | None` (`DateTime(timezone=True), nullable=True`) y `deleted_by: int | None` (FK a `directorio_empleado.id`, `ondelete="SET NULL"`, `nullable=True`, indexada). Migracion aditiva (revision 019, `down_revision = "018"`). No se agrega `Index` compuesto.

**Por que:** la semantica nullable NULL = activo es la mas simple y consistente con `fecha_baja` de `Empleado`. `deleted_by` como FK a `directorio_empleado` sigue el patron de `reportante_empleado_id` (c-82) y `ON DELETE SET NULL` evita que un borrado ARCO del actor elimine el incidente.

**Alternativas consideradas:** (a) un flag booleano `is_deleted` sin actor — pierde la atribucion exigida por R1/R4; (b) FK a `users` en lugar de `directorio_empleado` — rompe la consistencia con el dominio (el resto de la trazabilidad usa empleado); (c) tabla de auditoria separada `incidente_borrado` — sobre-ingenieria para una operacion booleana.

### D2 — Exclusion en un unico punto: el repositorio

**Decision:** agregar una condicion por defecto `Incidente.deleted_at.is_(None)` en las consultas de lectura del repositorio (`get_with_relations`, `list_filtered` y cualquier consulta de conteo/cola que agregue `c-87`). `get_by_id` (usado por `update_fields`/PATCH) hereda la exclusion al apoyarse en `get_with_relations`; si una actualizacion necesita leer la fila, el servicio reconsulta el detalle activo y se comporta como 404 si esta borrada.

**Por que:** concentrar el filtro evita que una consulta nueva lo omita (causa raiz del riesgo de fuga). Es la misma disciplina que ya usa el alcance por rol (defensa en el repositorio + confirmacion en el servicio).

**Alternativas consideradas:** (a) filtrar en el servicio — facil de olvidar en un metodo nuevo; (b) un `VIEW`/soft-delete global de SQLAlchemy — mas invasivo y con sorpresas en async.

### D3 — Camino NUEVO de borrado logico; `hard_delete` no se reutiliza

**Decision:** agregar `IncidenteRepository.soft_delete(incidente_id, *, deleted_by, deleted_at) -> int` que ejecuta un `UPDATE` Core seteando `deleted_at` y `deleted_by` y devuelve las filas afectadas. NO se invoca `hard_delete`.

**Por que:** R4 exige explicitamente preferir un camino nuevo y justificar la reutilizacion; el borrado fisico destruye la evidencia de auditoria. Un `UPDATE` Core evita lazy-load de relaciones en async, igual que el patron de `hard_delete`.

### D4 — Atributo `can_delete_incident` en `role_policy`

**Decision:** agregar `can_delete_incident: bool` a `PoliticaRol`; `True` solo en `administrador_directorio`, `False` en los demas. Exponer una derivacion `roles_con_borrado_incidentes()` analoga a `roles_gestion_directorio()`.

**Por que:** RP-002 exige que los guards deriven del registro sin listas de rol duplicadas; R2 lo pide explicitamente. El guard de la ruta consulta `politica_de_rol(empleado.rol).can_delete_incident`.

**Alternativas consideradas:** reutilizar `manages_directory` — semantica equivocada (permiso del directorio, no de incidentes) y acoplaria dos dominios.

### D5 — Guard de ruta y semantica 403 / 404

**Decision:** en `routes/incidentes.py`, una dependencia `require_borrado_incidentes` (patron de `require_directorio_admin`) resuelve el empleado del usuario y exige `can_delete_incident`; si no, 403. El endpoint delega en el servicio, que primero resuelve el incidente con `alcance` (404 si no existe, borrado o fuera de alcance) y luego ejecuta el borrado logico. Sin token -> 401 (dependencia `get_current_user` existente).

**Por que:** es la semantica ya asentada de VIS-001 (fuera de alcance = 404) y la de directorio (rol no autorizado = 403). No revela existencia de recursos fuera de alcance.

### D6 — Atribucion del actor en el servicio

**Decision:** `IncidenteService.soft_delete_incidente(incidente_id, *, actor_empleado_id, alcance)` valida existencia+alcance via `get_by_id(...)`, marca `deleted_at=utcnow()` y `deleted_by=actor_empleado_id` a traves del repositorio y retorna sin cuerpo. La ruta pasa el id del empleado resuelto por el guard.

**Por que:** mantiene la capa de servicio como unico orquestador de la regla de dominio y no deja reglas en la ruta.

### D7 — Frontend: accion admin-only con confirmacion

**Decision:** en `TicketDetailDialog.tsx`, renderizar la accion solo si el rol del usuario autenticado es `administrador_directorio`; al activarla, abrir un dialogo de confirmacion (patron de la UI); al confirmar, invocar el servicio `DELETE` y, en exito, invalidar las consultas de listado de incidentes y cerrar el detalle. La mutacion maneja 403/404 como estado de acceso denegado/no encontrado (FR-RBAC-005).

**Por que:** cumple R5 (admin-only, con confirmacion) y reutiliza el conocimiento de rol ya expuesto (FR-RBAC-001), sin duplicar logica de seguridad.

### D8 — Regenerar `docs/openapi.json`

**Decision:** tras agregar el endpoint, regenerar el spec estatico con el comando documentado en `AGENTS.md`.

**Por que:** `tests/test_openapi_sync.py` compara el spec regenerado en memoria con el archivo estatico y falla si difieren. Tarea obligatoria del apply.

## Risks / Trade-offs

- [Una consulta de lectura nueva omite el filtro `deleted_at IS NULL`] → El filtro vive en el repositorio (punto unico, D2); VIS-009 testea cada superficie.
- [Se reutiliza `hard_delete` por error] → El design fija un camino nuevo (D3); un test verifica que la fila sigue existiendo tras el 204.
- [La accion de UI se filtra a roles no admin] → Condicionada al rol expuesto (D7) y el backend responde 403 (D5).
- [Revertir la migracion pierde los marcadores] → Documentado en el Rollback Plan del proposal: el rollback recomendado conserva las columnas.
- [El historial de cerrados (c-86) no filtra borrados] → VIS-009 lo exige como escenario explicito; c-86 debe consumir la misma consulta filtrada del repositorio.
- [Idempotencia mal definida del segundo DELETE] → Un segundo borrado se comporta como 404 (el recurso ya no es visible), cubierto por escenario de SD-002.

## Migration Plan

1. Backend: migracion aditiva 019 (`down_revision = "018"`) de columnas → modelo → repositorio (`soft_delete` + filtro de exclusion) → `role_policy` (`can_delete_incident`) → servicio (`soft_delete_incidente`) → ruta `DELETE` → regenerar `docs/openapi.json`.
2. Frontend: tipo → servicio DELETE → hook de mutacion → `TicketDetailDialog.tsx` (accion + confirmacion).
3. Tests en cada paso (TDD estricto): RED → GREEN → triangulacion.
4. Rollback: revertir el commit del codigo. La migracion es aditiva; el rollback recomendado conserva las columnas para no perder marcadores existentes. Si se decide revertir tambien la migracion, las filas marcadas vuelven a ser visibles (sin perdida de datos de negocio).

## Open Questions

Ninguna que afecte specs, enfoque o descomposicion de tareas. Secundario pero explicitado: la implementacion final de la pestaña "Historial de Incidentes Cerrados" corresponde a `c-86`; este change solo fija su requisito de exclusion (VIS-009).
