## Why

`c-54-directorio-usuarios` dejo abierto el endurecimiento del directorio, la visibilidad de incidentes y la retencion: la tarea 7.5 (revision humana HIGH) sigue pendiente y bloquea activar datos reales; la purga por retencion registra SOLO un conteo (sin los ids de lo borrado); la cola `GET /clasificaciones/revision-pendiente` es GLOBAL multi-sector; no existe un rol que cubra la cola de revision; y el seed dev-only no tiene guardia de entorno. Este change cierra esos puntos sin reabrir el diseno ya aprobado de c-54.

## What Changes

- **Purga MANUAL y disparada por un operador** (rol `administrador_directorio`, via API y CLI). NO se introduce cron/scheduler ni automatizacion (compatibilidad).
- **El registro de la purga SHALL incluir los ids** de las filas eliminadas (ademas del conteo), sin datos personales.
- **Acotar `revision-pendiente` por sector**: un no administrador solo ve la cola de incidentes de su sector.
- **Modelo de visibilidad de incidentes por rol**: `ADMIN` es el rol existente `administrador_directorio` (ve todo); `MESA_DE_AYUDA` es un rol NUEVO que ve los incidentes **sin sector / que necesitan revision humana** (cola de revision); `usuario_final`/`operador` ven solo su sector; cuenta sin empleado/sector, alcance vacio.
- **Guardia de entorno SOLO en el seed** (rechaza correr fuera de development/test); NO aplica al runtime normal.
- **Cerrar las confirmaciones pendientes de c-54 7.5**: politica de retencion/ARCO, regla de visibilidad por rol y su alcance, evidencia de que NO hay PII real en repositorio/DB, y que NO se agrego clave de indice ciego.

### Out of scope

- Automatizacion de la purga (cron/scheduler) y borrado por retencion como camino por defecto.
- Notificaciones (c-53/c-56), transporte de correo (c-55), SMS.
- La parte FRONTEND de la visibilidad por rol (diferida, igual que en c-54).
- Cambios a clasificacion, a los cinco sectores canonicos o al cifrado Fernet del incidente.

## Capabilities

### New Capabilities

- None — las capacidades ya fueron introducidas por c-54 (ARCHIVADO 2026-10-01) y ya existen como specs principales en `openspec/specs/`; este change las endurece con deltas MODIFIED.

### Modified Capabilities

- `employee-directory`: retencion/purga manual (operador, sin cron) con ids auditados; guardia de entorno acotada al seed; evidencia de la revision 7.5 (retencion/ARCO, no-PII real, sin clave de indice ciego).
- `incident-visibility`: incorpora el rol `mesa_de_ayuda` y precisa el modelo de visibilidad por rol; acota la cola `revision-pendiente` por sector/rol.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/models/empleado.py` | Modified | `RolEmpleado` + CheckConstraint suman `mesa_de_ayuda` |
| `App/Backend/alembic/versions/012_*.py` | New | Migracion append-only (`down_revision = "011"`): actualiza el CHECK de `rol` |
| `App/Backend/app/services/incident_visibility.py` | Modified | `AlcanceIncidentes` suma el modo revision (`permite_incidente`) |
| `App/Backend/app/routes/clasificaciones.py` (+ servicio/repo) | Modified | `revision-pendiente` acotado por sector/rol |
| `App/Backend/app/services/directorio_service.py` | Modified | `purgar_vencidos` devuelve y audita ids |
| `App/Backend/app/routes/directorio.py`, `app/schemas/directorio.py` | Modified | Trigger manual de purga por operador (`administrador_directorio`) |
| `App/Backend/scripts/seed_directorio.py` | Modified | Guardia de entorno (solo seed) |
| `App/Backend/scripts/purgar_directorio.py` | Modified | Reporta ids purgados |
| `App/Backend/tests/test_*` | Modified/New | Unit + integration de visibilidad, purga y guardia |
| `docs/directorio-usuarios.md`, `docs/openapi.json` | Modified | Documentacion y contrato |

## Governance

**ALTO (HIGH)**: datos personales (Ley 25.326), reglas de visibilidad de incidentes, retencion/ARCO y PII. La implementacion queda gateada tras revision humana de la politica de retencion/ARCO y de la regla de visibilidad; NO se escribe codigo de produccion en esta fase (propose/design only).

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Fuga de incidentes entre sectores por el nuevo rol | Med | Alcance explicito por modo, tests de aislamiento, revision humana HIGH |
| Purga destructiva irreversible | Med | Manual, idempotente, con ids auditados y confirmacion del operador; nunca el camino por defecto |
| Rol nuevo rompe la restriccion CHECK existente | Med | Migracion append-only 012 (`down_revision = "011"`, tras c-70) sobre el constraint |
| Guardia de entorno mal ubicada frena runtime | Low | Guardia SOLO en el seed; test que verifica que el runtime normal no se gatea |
| Cruce con specs principales archivadas (c-54) y c-56 activo | Med | Deltas MODIFIED sobre las specs principales vigentes; c-56 compatible, no bloqueante |

## Rollback Plan

Revertir el commit elimina el rol `mesa_de_ayuda`, el alcance por modo, el acotamiento de la cola y la guardia del seed; `cd App/Backend; alembic downgrade -1` restaura el CHECK previo de `rol` (no hay datos de negocio que restaurar: las filas siguen siendo cargables). La purga manual deja de exponerse. c-54/c-56 NO dependen de c-60 para funcionar.

## Dependencies

- `c-54-directorio-usuarios` (directorio, roles, visibilidad base; ARCHIVADO 2026-10-01) — prerequisito.
- `c-56-notificaciones-por-rol` (consume roles/sector; sin archivar) — compatible, no bloqueante.

## Success Criteria

- [ ] La purga es manual (operador), NO programada, y audita los ids de las filas eliminadas.
- [ ] `revision-pendiente` solo devuelve, para un no administrador, la cola de su sector; `mesa_de_ayuda` ve la cola de revision global.
- [ ] El rol `mesa_de_ayuda` ve unicamente incidentes sin sector o en revision; `administrador_directorio` ve todo; un sector-bound ve solo su sector.
- [ ] El seed rechaza correr fuera de development/test y el runtime normal NO se gatea.
- [ ] Queda registrada la evidencia de la revision 7.5 (retencion/ARCO, ausencia de PII real, sin clave de indice ciego).
- [ ] `openspec validate --strict --changes c-60-directorio-endurecimiento` pasa.
