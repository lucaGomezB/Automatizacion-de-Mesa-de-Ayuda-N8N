## Context

Ver `proposal.md — Why`. Restricciones verificadas que moldean el enfoque:

- **`c-54` sin archivar.** Las capacidades `employee-directory` e `incident-visibility` viven solo como delta specs de `openspec/changes/c-54-directorio-usuarios/`; aun NO estan en `openspec/specs/`. Los deltas de c-60 se construyen sobre ese estado vigente (mismo patron que usan c-55/c-56 entre changes activos).
- **Rol almacenado como texto con CHECK.** `App/Backend/app/models/empleado.py` define `RolEmpleado` (3 valores) y `CheckConstraint("rol IN ('usuario_final','operador','administrador_directorio')")`. Agregar un rol exige actualizar el enum Y el constraint (migracion).
- **Visibilidad actual expresada solo por sector.** `app/services/incident_visibility.py` modela `AlcanceIncidentes(ver_todos, sector_id)` con `permite_sector(sector_id)`; `alcance_desde_empleado` distingue administrador (global), sector-bound y vacio. NO existe hoy un alcance que dependa de `requiere_revision_humana` ni de `sector_id IS NULL`: la regla actual no puede expresar "incidentes en revision".
- **La cola de revision es global.** `GET /api/v1/clasificaciones/revision-pendiente` (`app/routes/clasificaciones.py`) exige solo autenticacion y devuelve la cola multi-sector via `ClasificacionService.list_pending_review` -> `ClasificacionRepository.list_pending_review` (`requiere_revision_humana == True AND sector_id_validado IS NULL`, FIFO). `c-54` D16 la dejo explicitamente FUERA de su alcance.
- **La purga hoy no registra ids.** `DirectorioService.purgar_vencidos` (`app/services/directorio_service.py`) borra las filas vencidas y loguea SOLO `purgados=len(vencidos)`; `scripts/purgar_directorio.py` imprime solo el total. Es manual (script CLI), idempotente, sin cron.
- **No existe guardia de entorno.** `settings.environment` existe (`app/config/settings.py`, default `"production"`) pero el seed (`scripts/seed_directorio.py`) no lo consulta: puede correr contra produccion.
- **`administrador_directorio` es el ADMIN existente.** `app/routes/directorio.py` ya autoriza con `require_directorio_admin` (rol `administrador_directorio`).
- **Convenciones.** Capas `routes -> services -> repositories -> models`; async SQLAlchemy con `selectinload()`; migraciones append-only en `App/Backend/alembic/versions/` (ultima `010`); identificadores de dominio en español; errores con envelope estandar; no-PII en logs (DIR-006).
- **Governance HIGH.** Datos personales (Ley 25.326), visibilidad de incidentes, retencion/ARCO. No se implementa en esta fase.

## Goals / Non-Goals

**Goals:**

- Precisar el modelo de visibilidad de incidentes con un rol nuevo `mesa_de_ayuda` (revision) y dejar explicito ADMIN/sector/vacio.
- Acotar la cola `revision-pendiente` por sector/rol sin duplicar la derivacion rol -> alcance.
- Hacer la purga MANUAL (operador) y auditable con los **ids** de lo eliminado, sin automatizacion.
- Aplicar una guardia de entorno SOLO al seed.
- Registrar la evidencia de las confirmaciones de c-54 7.5 (retencion/ARCO, no-PII real, sin clave de indice ciego).

**Non-Goals:**

- Cron/scheduler de purga, o purga como camino operativo por defecto.
- UI/frontend de la visibilidad (diferida, igual que c-54).
- Notificaciones (c-53/c-56), transporte SMTP/IMAP (c-55), clasificacion, cinco sectores, cifrado Fernet.
- Implementar codigo en esta fase (propose/design only).

## Decisions

### D1: Rol nuevo `mesa_de_ayuda`, sin sector

Se agrega `mesa_de_ayuda` al enum `RolEmpleado` y al CHECK de `directorio_empleado` mediante una migracion append-only `011` (`down_revision = "010"`). El rol NO tiene sector (igual que `administrador_directorio`): es un revisor transversal de la cola de revision. Alternativa considerada: reutilizar `operador` sin sector — descartada porque DIR-004 exige sector a `operador` y romperlo debilitaria la regla. Alternativa considerada: `administrador_directorio` para revisar — descartada por minimo privilegio (el admin gestiona el directorio; no debe ser el unico revisor).

### D2: Modelo de visibilidad de incidentes (semantica por rol)

| Rol | Alcance de incidentes |
|-----|-----------------------|
| `administrador_directorio` (ADMIN) | TODOS (global) |
| `mesa_de_ayuda` | Incidentes SIN sector (`sector_id IS NULL`) O que requieren revision humana (`requiere_revision_humana = true`) |
| `usuario_final` / `operador` con sector S | Solo incidentes del sector S |
| Cuenta sin empleado o empleado sin sector | Vacio (no ve incidentes por esta via) |

El conjunto de `mesa_de_ayuda` se deriva del modelo vigente: es exactamente la poblacion que alimenta la cola de revision (`requiere_revision_humana=true`) mas los incidentes aun sin sector asignado, que son los que no tienen responsable sectorial. No es "todos": es el minimo necesario para revisar. Alternativa considerada: `mesa_de_ayuda` ve todo — descartada (viola minimo privilegio y la intencion de la decision humana). Alternativa considerada: que vea solo `requiere_revision_humana` — descartada porque un incidente sin sector y sin flag quedaria sin revisor.

### D3: `AlcanceIncidentes` con modos y `permite_incidente`

`AlcanceIncidentes` se generaliza a modos: `GLOBAL` (admin), `SECTOR` (sector_id), `REVISION` (mesa_de_ayuda) y `VACIO`. Se agrega `permite_incidente(incidente)` que decide segun el modo (en `REVISION`: `sector_id is None or requiere_revision_humana`). Se conserva `permite_sector` por compatibilidad con los call sites de c-54 que verifican por sector; donde la decision depende del incidente completo (`REVISION`), los call sites pasan a `permite_incidente`. `alcance_desde_empleado` mapea el rol al modo. Alternativa considerada: inferir el modo desde `(ver_todos, sector_id)` — descartada porque `REVISION` no es expresable con esos dos campos.

### D4: `revision-pendiente` acotado por sector/rol

La ruta inyecta el mismo `AlcanceIncidentes` (`get_alcance_incidentes`, reutilizado de incidentes) y lo propaga a `ClasificacionService.list_pending_review`. Semantica: `administrador_directorio` ve la cola completa; `mesa_de_ayuda` ve la cola completa (es su proposito: revisar lo que no tiene sector); un `usuario_final`/`operador` con sector S ve solo los pendientes cuyo incidente pertenece a S; una cuenta con alcance vacio ve una lista vacia. El repositorio agrega filtros opcionales (por sector y/o por condicion de revision) sin cambiar la semantica FIFO. Alternativa considerada: prohibir la cola a no administradores — descartada (la revision es trabajo del revisor, no del admin).

### D5: Purga manual disparada por operador, sin cron

Se expone `POST /api/v1/directorio/purga` (rol `administrador_directorio`) que ejecuta `DirectorioService.purgar_vencidos` y devuelve `{ "purgados": N, "ids": [...] }`; el script `scripts/purgar_directorio.py` sigue siendo el disparador CLI y ahora reporta los ids. NO se agrega scheduler, cron, ni worker en background: la invocacion es siempre explicita y humana. `purgar_vencidos` recolecta los ids antes de borrar, los incluye en el evento de auditoria/log (son identificadores internos, NO PII) y los devuelve. Sigue siendo idempotente: una segunda corrida devuelve `ids=[]`. Alternativa considerada: purga automatica por tiempo — descartada por decision humana (compatibilidad) y porque el borrado fisico no debe ser el camino por defecto.

### D6: Guardia de entorno SOLO en el seed

`scripts/seed_directorio.py` MUST rechazar la ejecucion (exit no-cero, sin tocar la base) cuando `settings.environment` no pertenezca al conjunto de desarrollo/test (p.ej. `development`, `local`, `test`). La guardia vive en el script/entrada del seed, NO en el runtime: ninguna ruta, servicio ni dependencia de la aplicacion consulta `environment` para autorizacion. Alternativa considerada: bloquear operaciones de escritura en produccion a nivel app — descartada (rompe la operacion normal de la mesa de ayuda).

### D7: Cierre de las confirmaciones de c-54 7.5

Se documentan y evidencian por tests/inspeccion:
1. **Retencion/ARCO**: `fecha_baja + 1 año`, desactivacion no borrado, borrado fisico solo por vencimiento manual o ARCO. Se confirma la politica (queda sujeta a aprobacion humana).
2. **Visibilidad por rol y su alcance**: el modelo de D2/D4, con tests de aislamiento (admin, mesa_de_ayuda, sector, vacio).
3. **Ausencia de PII real**: el seed usa datos sinteticos (`.test`); se agrega verificacion de que el repositorio/DB no contienen PII real (datos sinteticos y referencias estructurales).
4. **Sin clave de indice ciego**: DIR-005 se mantiene; test/inspeccion de que no se agrego `directory_blind_index_key` ni columna de hash.

### D8: Migracion append-only 011

`011_directorio_rol_mesa_ayuda.py` con `down_revision = "010"`: dropea el CHECK `ck_directorio_empleado_rol` y lo recrea con los cuatro valores. No edita `009`/`010`. Downgrade restaura el CHECK de tres valores (falla si existieran filas `mesa_de_ayuda`, comportamiento documentado y aceptable en rollback sin datos reales).

### D9: Estrategia de tests

- **Unit (SQLite, `-m "not integration"`)**: `alcance_desde_empleado` por rol; `permite_incidente` (sin sector, con revision, sector-bound, admin); `revision-pendiente` acotado (admin/mesa_de_ayuda/sector/vacio); `purgar_vencidos` devuelve ids y audita ids sin PII; guardia del seed (rechaza produccion, acepta dev).
- **Integration (PostgreSQL, `-m integration`)**: CHECK de `rol` acepta `mesa_de_ayuda`; igualdad real del filtro de cola por sector.
- **Verificacion de cierre 7.5**: inspeccion/test de no-PII real y ausencia de clave de indice ciego.

### D10: Governance

Gobierno **HIGH**: el rol nuevo, la visibilidad, la cola acotada y la purga afectan datos personales, visibilidad cross-sector y retencion/ARCO. La implementacion requiere revision humana de la politica de retencion/ARCO y de la regla de visibilidad antes de activar datos reales. No se escribe codigo en esta fase.

## Risks / Trade-offs

- **[Fuga cross-sector con `mesa_de_ayuda`]** el revisor ve incidentes sin sector/revision de todos los sectores → Mitigacion: el conjunto es el minimo (sin sector o en revision), no "todos"; tests de aislamiento; revision humana HIGH.
- **[Purga destructiva]** borrado fisico manual → Mitigacion: trigger explicito de operador, ids auditados, idempotencia, nunca por defecto.
- **[Rol nuevo rompe el CHECK]** desalineacion modelo/migracion → Mitigacion: migracion 011 append-only + test de migracion + test integration del constraint.
- **[Guardia mal ubicada]** frenar runtime normal → Mitigacion: guardia SOLO en la entrada del seed; test de que el runtime no se gatea.
- **[Deltas sobre changes sin archivar]** c-54/c-56 → Mitigacion: deltas base sobre el estado vigente; orden de archivado c-54 -> c-60 y c-56 compatible.

## Migration Plan

1. `models/empleado.py`: sumar `mesa_de_ayuda` al enum y al CHECK; migracion `011` append-only con tests de migracion.
2. `services/incident_visibility.py`: modos de `AlcanceIncidentes` + `permite_incidente` + mapeo de rol; tests.
3. `repositories/clasificacion_repository.py` + `services/clasificacion_service.py` + `routes/clasificaciones.py`: filtros de la cola por alcance; tests.
4. `services/directorio_service.py` + `routes/directorio.py` + `schemas/directorio.py`: purga manual por operador con ids; `scripts/purgar_directorio.py` reporta ids; tests.
5. `scripts/seed_directorio.py`: guardia de entorno (solo seed); tests.
6. Evidencia c-54 7.5 (retencion/ARCO, no-PII real, sin indice ciego) en docs/tests; actualizar `docs/directorio-usuarios.md` y regenerar `docs/openapi.json`.
7. Verificacion: `pytest -m "not integration"`, `pytest -m integration`, `ruff check .`, `test_openapi_sync.py`, `openspec validate --strict`.
8. Rollback: revertir el commit y `cd App/Backend; alembic downgrade -1` (restaura el CHECK de tres valores).

## Open Questions

1. **Pertenencia sectorial de `mesa_de_ayuda`**: este design asume SIN sector (revisor transversal). Confirmar en la revision humana HIGH; si debiera tener sector, cambia D1/D2.
2. **Conjunto exacto de `mesa_de_ayuda`**: asumido `sector_id IS NULL OR requiere_revision_humana = true`. Confirmar que un incidente sin sector y sin flag debe ser visible al revisor (hoy se incluye).
3. **Confirmacion de la politica de retencion/ARCO** (tarea c-54 7.5): es una aprobacion HUMANA; el design no la resuelve por si mismo.
4. **Valores permitidos de entorno para el seed**: se proponen `development`/`local`/`test` (default `production`); confirmar la lista exacta.
