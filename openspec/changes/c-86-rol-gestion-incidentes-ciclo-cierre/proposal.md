## Why

El sistema tiene tres roles y un alcance PROPIO/GLOBAL donde el sector NO es frontera de acceso. Falta el rol operativo `gestion_incidentes`, que atienda y cierre los incidentes de SU sector, y falta por completo el ciclo de cierre: hoy no existe cierre por sector, reapertura, ni registro de QUIEN cierra o cambia el estado (el validador humano tampoco registra el actor). Tampoco hay historial de incidentes cerrados ni un canal de comentarios duradero. Sin esto la mesa de ayuda no puede operar el cierre con trazabilidad, lo que bloquea la operacion real y la evidencia de la tesis.

## What Changes

- **BREAKING** Cuarto rol `gestion_incidentes`: requiere sector, alcance nuevo `SECTOR`, no privilegiado, no gestiona directorio; cierra y edita el estado de los incidentes de su sector; NO crea, NO borra, NO valida clasificaciones.
- Alcance `SECTOR` en el registro de politica; visibilidad acotada server-side por pertenencia al CONJUNTO de sectores del incidente (`{sector principal} U adicionales`) y por no-cerrado.
- Ciclo de cierre: tabla `incidente_cierre_sector` (un cierre por sector y por incidente), cierre GLOBAL de `mesa_de_ayuda` (cierra todos los sectores), transicion terminal a `cerrado` cuando TODOS los sectores cerraron, y `REHABILITAR` (reapertura) exclusiva de `mesa_de_ayuda`.
- Edicion de estado (`en proceso`/`en espera`/`resuelto`) por los roles con permiso; `cerrado` se alcanza solo por el modelo de cierre, nunca fijandolo directo.
- Log de comentarios APPEND-ONLY (`incidente_comentario`) con formato `HH:MM:SS DD/MM/AAAA : {texto}` y separador `----------`, permissionado por visibilidad (cualquier rol con acceso al incidente).
- Auditoria de ciclo de vida (`incidente_evento`): actor + fecha en cierre, reapertura y cambio de estado.
- Nueva notificacion post-revision a los `gestion_incidentes` de los sectores del incidente, por correo via el mecanismo N8N existente.
- Nueva pestaña "Historial de Incidentes Cerrados" en el panel de administracion con las reglas de visibilidad por rol.
- Migracion Alembic 018: amplia el CHECK del rol a cuatro valores y crea las tablas nuevas.

## Capabilities

### New Capabilities

- `incident-lifecycle`: cierre por sector, cierre global, transicion terminal a `cerrado`, reapertura/rehabilitar y edicion de estado, con atribucion de actor.
- `incident-comments`: log de comentarios append-only con formato de visualizacion y permisos derivados de la visibilidad.
- `frontend-incidentes-historial`: pestaña "Historial de Incidentes Cerrados", listado activo por sector y visualizacion de comentarios en el panel de administracion.

### Modified Capabilities

- `employee-directory`: DIR-003 pasa de tres a cuatro roles; DIR-004 admite que `gestion_incidentes` requiera sector.
- `role-policy`: RP-001/002/003 incorporan el cuarto rol, el modo `SECTOR`, `requires_sector` verdadero y el criterio del destinatario del aviso post-revision.
- `incident-visibility`: agrega el alcance `SECTOR` (filtrado server-side por conjunto de sectores y no-cerrado) y las reglas de visibilidad del historial.
- `notification-routing`: agrega la resolucion de destinatarios post-revision (`gestion_incidentes` de los sectores del incidente).
- `frontend-rbac`: la UI conoce el alcance `SECTOR`, habilita la superficie operativa para `gestion_incidentes` y adapta guard y navegacion.

## Impact

Backend: `app/models/empleado.py`; `app/models/asociaciones.py` (o `incidente.py`) + modelos nuevos `incidente_cierre_sector`, `incidente_evento`, `incidente_comentario`; `app/services/role_policy.py`, `incident_visibility.py`, `incidente_service.py`, `clasificacion_service.py`, `notification_recipient_service.py`; `app/repositories/incidente_repository.py`, `empleado_repository.py` (+ repos nuevos); `app/routes/incidentes.py`, `clasificaciones.py`; `app/schemas/incidente.py`; migracion `alembic/versions/018_*.py`; `docs/openapi.json`.

Frontend: `src/pages/Administracion/index.tsx` + `HistorialTable`/comentarios; `src/hooks/` (`useHistorialCerrados`, `useComentarios`, `useCicloIncidente`); `src/services/` (incidentes); `src/types/`; estado de autenticacion para exponer `SECTOR`.

Tests: backend SQLite unit + `@pytest.mark.integration` PostgreSQL; frontend Vitest; sincronizacion OpenAPI.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Divergencia entre el CHECK de rol, el enum y el registro de politica | Media | Test de coherencia RP-003 extendido a cuatro valores; migracion amplia el CHECK de forma aditiva |
| Filtrado `SECTOR` que filtra de menos y expone otro sector | Media | Filtro server-side sobre el conjunto de sectores + tests por rol; la UI nunca es el limite |
| Ambiguedad entre cierre parcial y cierre global | Media | Reglas explicitas de vista activa vs historial; transicion terminal solo cuando todos cerraron |
| La reapertura pierde el estado previo al cierre | Baja | `incidente_evento` registra actor, estado anterior y nuevo; reapertura devuelve a `en proceso` de forma deterministica |
| Notificacion post-revision acoplada a la validacion | Baja | Fire-and-forget con degradacion; N8N aplica respaldo; sin PII en logs |
| Desincronizacion de `docs/openapi.json` | Baja | Regenerar el spec y correr `tests/test_openapi_sync.py` |

## Rollback Plan

Revertir el commit del change y ejecutar `alembic downgrade` sobre la migracion 018. El `downgrade` revierte el CHECK al vocabulario de tres valores DESPUES de reasignar las filas `gestion_incidentes` a `usuario_final` (least privilege) y elimina las tablas nuevas, sin dejar el esquema inconsistente. El frontend vuelve a las pestanas `tickets`/`revision` y al guard por alcance PROPIO/GLOBAL. `docs/openapi.json` se revierte con el commit.

## Success Criteria

- [ ] El cuarto rol `gestion_incidentes` existe en el enum, el CHECK y el registro de politica, con coherencia verificada por test.
- [ ] Un `gestion_incidentes` lista y accede UNICAMENTE a incidentes de su sector no cerrados; sin sector, su alcance es VACIO.
- [ ] El cierre por sector lo saca de la vista activa y lo incorpora de inmediato al historial de ese sector.
- [ ] El cierre de `mesa_de_ayuda` es global y lleva el incidente a `cerrado`; la reapertura lo devuelve a `en proceso` y lo hace visible segun las reglas normales.
- [ ] Todo cierre, reapertura y cambio de estado registra actor y fecha.
- [ ] Los comentarios son append-only y se muestran con el formato `HH:MM:SS DD/MM/AAAA : {texto}` separados por `----------`.
- [ ] La pestaña "Historial de Incidentes Cerrados" respeta las reglas de visibilidad por rol.
- [ ] Los `gestion_incidentes` de los sectores del incidente reciben el aviso post-revision.

## Open Questions

1. **Semantica exacta de reapertura: RESUELTA.** `REHABILITAR` es exclusiva de `mesa_de_ayuda` (rol privilegiado GLOBAL). Elimina las filas de `incidente_cierre_sector` del incidente, fija el estado en `en proceso` de forma deterministica y registra un `incidente_evento` con actor, estado anterior (`cerrado`) y nuevo (`en proceso`). El incidente vuelve a ser visible segun las reglas normales.
2. **Filtrado SQL del alcance `SECTOR`: RESUELTA.** La vista activa usa `(incidente.sector_id = S OR incidente.id IN (SELECT incidente_id FROM incidente_sector_adicional WHERE sector_id = S)) AND NOT EXISTS (SELECT 1 FROM incidente_cierre_sector WHERE incidente_id = incidente.id AND sector_id = S) AND estado != 'cerrado'`. La verificacion puntual reutiliza la misma condicion.
3. **Almacenamiento y formato de comentarios: RESUELTA.** Tabla `incidente_comentario` (id, incidente_id FK CASCADE, autor_empleado_id FK SET NULL, texto, created_at timestamptz). Sin numeracion; append-only (sin endpoints de edicion/borrado). Render en `America/Argentina/Buenos_Aires` con el formato `HH:MM:SS DD/MM/AAAA : {texto}` y separador visual `----------`.
4. **Payload y disparador de la notificacion post-revision: RESUELTA.** Se dispara al finalizar con exito `ClasificacionService.validate` (el incidente deja de requerir revision), resolviendo los `gestion_incidentes` ACTIVOS cuyo sector pertenece al conjunto validado del incidente. El payload agrega `destinatarios_gestion` (lista, posiblemente vacia) junto a `incidente_id` y un marcador de evento; envio fire-and-forget por N8N con respaldo y sin PII en logs.
5. **Cableado de la nueva pestaña: RESUELTA.** `TabActiva` pasa a `'tickets' | 'revision' | 'historial'`; un hook `useHistorialCerrados` consume `GET /api/v1/incidentes/historial-cerrados` (respeta el alcance) y la tabla muestra estado normalizado "Cerrado"; los comentarios viven en el detalle del incidente.
6. **Historial para roles GLOBAL: RESUELTA.** Los roles GLOBAL ven los incidentes GLOBALMENTE cerrados (`estado = cerrado`); `gestion_incidentes` ve los cerrados de su sector (incluidos los cerrados solo por su sector); `usuario_final` ve solo los suyos cerrados. El historial excluye incidentes eliminados.
