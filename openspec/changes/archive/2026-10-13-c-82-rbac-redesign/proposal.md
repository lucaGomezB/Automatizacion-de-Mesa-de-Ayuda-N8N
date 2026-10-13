## Why

El modelo RBAC del sistema es inconsistente: hay cuatro roles con el conocimiento de rol duplicado en cinco lugares (enum, CHECK de la DB, `PRIVILEGED_ROLE_VALUES`, la cadena if/elif de `incident_visibility` y los guards de rutas), `operador` y `mesa_de_ayuda` se solapan, el sector es a la vez frontera de acceso y categoria de clasificacion, y un `usuario_final` NO puede ver los incidentes que el mismo reporto porque el incidente no tiene vinculo con el reportante. El change `c-81-frontend-rbac` hace que el frontend refleje el RBAC pero DEPENDE de que el backend lo redefina primero.

## What Changes

- **BREAKING**: el vocabulario de roles pasa a EXACTAMENTE TRES valores: `usuario_final` (alcance PROPIO), `mesa_de_ayuda` (GLOBAL, absorbe `operador`, privilegiado, NO gestiona el directorio) y `administrador_directorio` (GLOBAL, privilegiado, gestiona el directorio). El rol `operador` se ELIMINA.
- Se ELIMINA el aislamiento por sector. Los modos de visibilidad pasan a PROPIO/GLOBAL; el sector deja de ser frontera de acceso y queda solo como categoria de clasificacion del incidente.
- Se agrega un VINCULO DE REPORTANTE en el incidente (FK nullable a `directorio_empleado`), poblado por canal: web desde el `current_user` autenticado; correo/telefono resolviendo el remitente/llamante via `ContactResolutionService` (que hoy existe pero no esta cableado al alta).
- El `sector_id` de `directorio_empleado` pasa a ser dato organizacional OPCIONAL sin efecto en autorizacion; se elimina la coherencia rol/sector (`_validar_sector_por_rol`).
- Los destinatarios de la notificacion de revision pasan a ser TODOS los `mesa_de_ayuda` activos (reemplaza el lookup por sector).
- Se CENTRALIZA la politica de rol en un unico registro rol -> politica (fuente unica de verdad); el enum, el CHECK de la DB, `privilege_service`, `incident_visibility` y los guards de rutas leen de alli en vez de duplicar el conocimiento.
- Se actualiza el conjunto privilegiado (IAH-005): `operador` sale; `mesa_de_ayuda` y `administrador_directorio` permanecen; `usuario_final` no es privilegiado.
- Migracion Alembic append-only del CHECK del rol: `operador` se mapea a `mesa_de_ayuda`.

## Capabilities

### New Capabilities

- `role-policy`: registro canonico que mapea cada rol a su politica (`requires_sector`, modo de visibilidad, `privileged`, `manages_directory`, `notification_recipient`) y es la unica fuente de verdad de la que dependen el enum, el CHECK y los servicios.

### Modified Capabilities

- `incident-visibility`: VIS-001 y VIS-002 se reescriben al modelo PROPIO/GLOBAL (se elimina SECTOR/REVISION); se agregan requisitos de vinculo de reportante y su resolucion por canal.
- `employee-directory`: DIR-003 y DIR-004 se reescriben a los tres roles nuevos, con `sector_id` opcional sin coherencia rol/sector; se corrige el drift de DIR-003 (que hoy omite `mesa_de_ayuda`).
- `notification-routing`: NR-002 cambia el criterio de destinatarios de revision de "operador del sector" a "todos los `mesa_de_ayuda` activos".
- `identity-access-hardening`: IAH-005 actualiza el conjunto de roles privilegiados (sale `operador`, quedan `mesa_de_ayuda` y `administrador_directorio`).

## Impact

- **Backend (modelos/migraciones)**: `app/models/empleado.py` (enum + CHECK), `app/models/incidente.py` (FK reportante), nueva migracion Alembic `017` (CHECK del rol + columna reportante + backfill `operador -> mesa_de_ayuda`).
- **Backend (servicios/rutas)**: nuevo registro de politica (`role_policy`), `app/services/incident_visibility.py`, `app/services/privilege_service.py`, `app/services/directorio_service.py`, `app/services/notification_recipient_service.py`, `app/repositories/empleado_repository.py`, `app/routes/directorio.py`, `app/routes/incidentes.py`, `app/services/incidente_service.py` + `app/schemas/incidente.py`.
- **Contrato**: `docs/openapi.json` se regenera si cambian endpoints/schemas. Nuevos campos de alta (identificador de contacto del reportante). El sobre de error no cambia.
- **Dependencia**: `c-81-frontend-rbac` depende de este change (el backend redefine el RBAC primero); NO se reimplementa su trabajo de UI.
- **Governance**: CRITICAL/HIGH (auth/RBAC, directorio, datos personales y visibilidad) — requiere aprobacion humana antes de escribir codigo. Detalle en `design.md`.
- **Fuera de alcance (follow-up)**: `docs/knowledge-base/03_actores_y_roles.md` (documentacion, no software).
