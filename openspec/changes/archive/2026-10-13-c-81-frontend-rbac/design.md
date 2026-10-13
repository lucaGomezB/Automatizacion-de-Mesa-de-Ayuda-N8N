## Context

Ver `proposal.md - Why`. Estado actual verificado que condiciona el approach (posterior a `c-82-rbac-redesign`, ya implementado y archivado):

- Backend: el alcance se deriva por request en `App/Backend/app/services/incident_visibility.py` (`alcance_desde_empleado` sobre el `Empleado` vinculado via `directorio_empleado.user_id`), y el modo se lee del registro unico de politica `app/services/role_policy.py` (`ModoAlcance` = PROPIO | GLOBAL | VACIO). `App/Backend/app/routes/incidentes.py::get_alcance_incidentes` y `app/routes/directorio.py::get_empleado_actual` resuelven el alcance y el empleado actual. El enforcement es correcto y NO se toca.
- Modelo RBAC vigente (c-82): TRES roles (`usuario_final` -> PROPIO, `mesa_de_ayuda` -> GLOBAL, `administrador_directorio` -> GLOBAL + gestiona el directorio; sin empleado -> VACIO). `operador` NO existe. El sector NO es frontera de acceso: es solo la categoria de clasificacion del incidente.
- Frontend: `AuthContext` solo modela `token/username/isAuthenticated/mfaRequired`; `ProtectedRoute` solo mira `isAuthenticated`; `Header` decide `isAdmin` por pathname; el panel expone filtros libres (incluido `sector_id`) sin relacion con el rol.
- Contrato de auth: `LoginResponse`/`TokenResponse` son aditivos. El rol vive en `Empleado`, NO en `User`; `is_privileged` es la bandera de identidad de MFA (IAH-005) y NO reemplaza al alcance derivado.

## Goals / Non-Goals

**Goals:**

- Que la UI conozca `rol` y `alcance.modo`, y los use para el guard de rutas, la navegacion y la eleccion de la vista de incidentes.
- Reutilizar la derivacion rol -> alcance existente (c-82), sin duplicarla.
- Mantener el contrato de auth aditivo.

**Non-Goals:**

- Cambiar el enforcement del backend (sigue siendo la unica fuente de verdad).
- Introducir un nuevo modelo de permisos en el frontend (no hay matriz de permisos; solo `rol` + `alcance.modo`).
- Gestion del directorio en el frontend (otro change); `administrador_directorio` recibe la misma superficie operativa que `mesa_de_ayuda` por ahora.
- Reclasificar la ruta/enlace `Dashboard` existente (fuera del alcance de este change; ver OQ-2).
- Resolver la politica de sesion del usuario de portal.

## Decisions

### D1 — La UI obtiene `rol`/`alcance` via un endpoint autenticado recomputado (Opcion B)

**Decision**: nuevo `GET /api/v1/auth/me`, de solo lectura, que devuelve `{username, rol, alcance:{modo}}`, con `modo` en PROPIO | GLOBAL | VACIO, recomputando el alcance por request desde el directorio (reutiliza `EmpleadoRepository.get_by_user_id` + `alcance_desde_empleado`, que a su vez lee `role_policy`). El alcance es SOLO `{modo}`: NO expone `sector_id`, `ver_todos` ni `revision` (esos conceptos ya no existen en el modelo c-82).

**Alternativas**:
- **A) Extender `LoginResponse`** con `rol`/`alcance`: el valor queda congelado al login y se vuelve stale si el directorio cambia (rol nuevo, empleado desactivado). No cubre "recompute per request".
- **C) Claims en el JWT**: staleness (el access dura 15 min), infla el token y acopla la derivacion de dominio al token.
- **B (elegida)**: consistente con el modelo existente (alcance derivado por request), sin staleness relevante, sin tocar el contrato de login, y permite al frontend re-resolver la identidad sin re-login.

**Ubicacion**: bajo `/auth/me` (identidad de sesion), no `/directorio/me`, porque expone la identidad efectiva y su alcance derivado, no un recurso del directorio. La ruta solo orquesta: reutiliza el repositorio y el servicio/registro existente (sin logica de negocio en la ruta).

### D2 — Modelo de acceso en el frontend (reconciliado al modelo c-82)

**Decision**: la UI renderiza capacidades por `alcance.modo`:

- `GLOBAL` (`mesa_de_ayuda` y `administrador_directorio`): superficie operativa (ruta `/admin` existente) con el listado de tickets (TODOS) y la cola de revision humana. Para `administrador_directorio` la gestion del directorio queda fuera de alcance (otro change).
- `PROPIO` (`usuario_final`): portal (formulario de reporte) mas una vista "Mis incidentes" (ruta `/mis-incidentes`) que lista SUS propios incidentes reutilizando `GET /api/v1/incidentes/` (el backend ya acota PROPIO). NO se crea endpoint nuevo.
- `VACIO` (cuenta sin empleado): sin superficie operativa; al intentar `/admin` o `/mis-incidentes` se redirige al portal.
- Anonimo: redirige a `/login`, igual que antes.

El `Header` decide los enlaces por `alcance.modo`, NO por pathname: "Portal" siempre para autenticados, "Mis incidentes" solo en PROPIO, enlace a la superficie operativa solo en GLOBAL. El guard de `/admin` exige GLOBAL; el de `/mis-incidentes` exige PROPIO.

**Alternativas consideradas**: gatear la superficie operativa solo a `administrador_directorio` y dejar a `mesa_de_ayuda` sin vista (se descarta: `mesa_de_ayuda` es GLOBAL y debe ver todos los incidentes); una ruta `/revision` dedicada para `mesa_de_ayuda` (se descarta: la cola de revision es una pestana de la superficie operativa, no un alcance).

### D3 — Governance: CRITICAL (superficie auth/RBAC)

**Decision**: el change se clasifica **CRITICAL**. Aunque el endpoint es de solo lectura, aditivo y NO debilita el enforcement, la clasificacion sigue el DOMINIO (auth/RBAC), no el tamano del diff. Implica aprobacion humana explicita antes de escribir el endpoint backend. La porcion puramente frontend (guard de UI, navegacion, vista y filtro) es MEDIUM; el backend auth es CRITICAL.

### D4 — TDD y capas

Backend: test del endpoint en el subset SQLite offline (patron de `tests/test_incident_visibility.py`): autenticado con empleado de cada rol (`administrador_directorio` -> GLOBAL, `mesa_de_ayuda` -> GLOBAL, `usuario_final` -> PROPIO), sin empleado (rol nulo + VACIO), anonimo (401). Frontend: Vitest para el contexto, el guard por modo, la navegacion por modo, la vista "Mis incidentes" y el filtro de sector. La ruta solo orquesta: `route -> (repositorio + servicio/registro) -> models`. No se duplica el mapeo rol -> alcance.

### D5 — "Mis incidentes" no necesita endpoint nuevo

El backend ya acota `GET /api/v1/incidentes/` por el alcance PROPIO (`usuario_final` solo ve los incidentes cuyo `reportante_empleado_id` es el suyo, VIS-001). Por lo tanto la vista "Mis incidentes" es puramente frontend: reutiliza el endpoint existente y no introduce superficie de API nueva. Ademas evita duplicar la logica de visibilidad en el cliente.

## Risks / Trade-offs

- [Staleness del alcance en el cliente] -> El endpoint se re-resuelve en login/refresh y al montar la sesion; los guards del backend siguen bloqueando cualquier recurso fuera de alcance.
- [El frontend parece "seguridad" y alguien lo trate como tal] -> Se documenta y testea explicitamente que el backend es la fuente de verdad (FR-RBAC-005) y que el filtro de sector es conveniencia (FR-RBAC-004); la UI maneja 403/404 sin exponer el recurso.
- [Ambiguedad de que ve cada rol] -> D2 fija un modelo claro y reversible; OQ-1/OQ-2/OQ-3 registran los ajustes posibles sin cambiar las specs.
- [Regenerar `docs/openapi.json`] -> Tarea explicita de sincronizacion; el test `test_openapi_sync.py` falla si se olvida.

## Migration Plan

1. Backend: agregar schema + endpoint `/auth/me` (reutilizando el repositorio y el servicio/registro de alcance existentes), regenerar `docs/openapi.json`.
2. Frontend: extender `AuthContext` con `rol`/`alcance` y consumir `/auth/me`; adaptar guard, navegacion, agregar la vista "Mis incidentes" y ajustar el filtro de sector a conveniencia.
3. Rollback: revertir el commit. El endpoint es aditivo y el frontend tolera su ausencia (degrada a "sin rol conocido" = no habilita la superficie operativa) — no hay migracion de datos ni cambios de esquema.

## Open Questions

- **OQ-1**: ¿Los roles GLOBAL (`mesa_de_ayuda`, `administrador_directorio`) deben conservar el acceso al portal (formulario de reporte) ademas de la superficie operativa? D2 asume que SI: el portal es de todos los autenticados. Ajuste de UX, no cambia specs.
- **OQ-2**: ¿El enlace/ruta `Dashboard` existente pertenece a la superficie operativa (GLOBAL) o es una capacidad aparte fuera del alcance de c-81? D2 lo deja sin cambios; confirmar con el autor.
- **OQ-3**: ¿`administrador_directorio` debe recibir ya una superficie de gestion del directorio en el frontend, o se mantiene fuera de alcance (otro change)? D2 mantiene el non-goal original.
