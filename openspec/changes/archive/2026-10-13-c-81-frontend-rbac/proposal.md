## Why

La GUI de incidentes es role-blind: el modelo RBAC se aplica SOLO en el backend y el frontend ni conoce ni refleja el rol/alcance del usuario. Con `c-82-rbac-redesign` ya implementado y archivado, el RBAC quedo redefinido a TRES roles (`usuario_final`, `mesa_de_ayuda`, `administrador_directorio`) y a los modos PROPIO/GLOBAL/VACIO, con el aislamiento por sector ELIMINADO. Los artefactos originales de este change asumian cuatro roles (incluido `operador`) y modos SECTOR/REVISION ya inexistentes: la UI quedo desalineada. Este change reconcilia la interfaz al modelo VIGENTE sin debilitar la defensa en profundidad del servidor.

## What Changes

- Nuevo endpoint autenticado de identidad/alcance `GET /api/v1/auth/me` que devuelve `username`, `rol` y `alcance:{modo}` (PROPIO | GLOBAL | VACIO), recomputado por request desde el directorio. ADITIVO: no toca login/refresh/logout.
- El frontend consume `rol` + `alcance.modo` en el `AuthContext` y lo expone a la UI.
- Guard de rutas por modo: GLOBAL -> superficie operativa (listado de tickets + cola de revision); PROPIO -> vista "Mis incidentes"; VACIO -> redireccion al portal.
- Navegacion (`Header`) que renderiza enlaces por `alcance.modo`, no por pathname.
- Vista "Mis incidentes" para `usuario_final` que consume el `GET /api/v1/incidentes/` existente (el backend ya acota el alcance PROPIO): NO requiere endpoint nuevo.
- El filtro de sector del panel queda como filtro de CONVENIENCIA de UI, NO como frontera de seguridad: el sector dejo de ser limite de acceso.
- El backend NO cambia su enforcement: `incident_visibility` / `role_policy` siguen siendo la unica fuente de verdad.

## Capabilities

### New Capabilities

- `frontend-rbac`: la UI refleja el rol y el modo de alcance autenticado (consumo de `rol`/`alcance.modo`, guard de rutas, navegacion por modo, vista "Mis incidentes", filtro de sector como conveniencia). Es UX y least-surprise, NO el limite de seguridad.

### Modified Capabilities

- `identity-access-hardening`: se agrega el requisito IAH-012 (endpoint aditivo y de solo lectura de identidad/alcance actual, con modos PROPIO/GLOBAL/VACIO). Los requisitos IAH-001..IAH-011 no cambian.

## Impact

- Backend: nuevo `GET /api/v1/auth/me` en `App/Backend/app/routes/auth.py` + schema en `app/schemas/auth.py`; reutiliza `EmpleadoRepository.get_by_user_id` y `alcance_desde_empleado`/`role_policy` (sin duplicar el mapeo rol -> alcance). `docs/openapi.json` se regenera.
- Frontend: `src/contexts/AuthContext.tsx`, `src/main.tsx` (ProtectedRoute), `src/components/layout/Header.tsx`, `src/pages/Administracion/index.tsx`, nueva vista `src/pages/MisIncidentes/`, `src/hooks/useIncidentes.ts`, `src/services/incidentesService.ts`, `src/types/incidente.ts`.
- Contrato: aditivo. No rompe clientes de login/refresh existentes. Error envelope sin cambios.
- Governance: CRITICAL (superficie auth/RBAC) — el endpoint backend requiere aprobacion humana antes de implementarse. Detalle en `design.md`.
- Dependencia: `c-82-rbac-redesign` (backend RBAC), COMPLETA y archivada. Este change ya no depende de trabajo pendiente.
