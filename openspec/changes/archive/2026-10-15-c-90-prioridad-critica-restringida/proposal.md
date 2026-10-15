## Why

La prioridad `critica` no se ofrece en el formulario web, pero el backend la acepta sin restricción de rol en `POST /incidentes` y `PATCH /incidentes/{id}`. Un usuario no autorizado puede fijar o conservar `critica` con una llamada directa a la API. La restricción debe ser server-side (no solo una omisión en la UI) y derivar del registro canónico de política de rol.

## What Changes

- **Nuevo permiso en el registro de política**: `PoliticaRol` gana `puede_asignar_prioridad_critica` (verdadero para `mesa_de_ayuda` y `administrador_directorio`). El guard de las rutas deriva de ese atributo; sin listas de rol duplicadas.
- **Enforcement server-side en alta y edición**: `POST /incidentes` y `PATCH /incidentes` rechazan con HTTP 403 cuando un llamante SIN el permiso asigna (alta) o conserva/cambia a (edición) `critica`. Asignar `baja|media|alta` sigue sin restricción.
- **Regla segura para llamantes no interactivos** (webhook n8n): n8n se autentica como operador y hoy NUNCA envía `critica`; la ingesta no se rompe. Un llamante sin permiso que envíe `critica` recibe 403 (no se degrada silenciosamente).
- **Frontend**: el formulario de reporte NO ofrece `critica` (sin cambios de comportamiento, se agrega cobertura). El panel de administración permite a los roles autorizados (`mesa_de_ayuda` y `administrador_directorio`) asignar prioridad, incluida `critica`, solo cuando el rol lo permite. Los badges de prioridad renderizan `critica` de forma distinta (hoy cae a estilo por defecto).
- **Sin migración de base**: el permiso es código/política puro.

## Capabilities

### New Capabilities
- None: no se introduce ninguna capability nueva.

### Modified Capabilities
- `role-policy`: nuevo requisito **RP-006** — permiso `puede_asignar_prioridad_critica` en el registro canónico (ADD; NO toca RP-001/002/003 que modificó `c-86`, ya archivado).
- `frontend-rbac`: nuevo requisito **FR-RBAC-009** — control de asignación de prioridad visible/ejecutable solo para los roles autorizados (`mesa_de_ayuda` y `administrador_directorio`).

## Impact

- Backend: `app/services/role_policy.py`, `app/routes/incidentes.py`, `app/services/incidente_service.py`, `app/schemas/incidente.py` (si aplica validación), `app/core/error_handlers.py` (403 ya existente).
- Frontend: `App/Frontend/src/pages/Administracion/` (`TicketsTable.tsx`, `TicketDetailDialog.tsx`, `DetalleIncidente.tsx`), equivalente en `MisIncidentes`, `src/types/incidente.ts`, `src/utils/formatters.ts`.
- Contrato: `docs/openapi.json` se regenera solo si cambia el contrato HTTP (nuevo 403 documentado), guardado por `tests/test_openapi_sync.py`.
- Sin migración Alembic. El change hermano `c-86` (aplicado y archivado el 2026-10-15) no se clobbea: RP-006 es un requisito ADICIONAL.
