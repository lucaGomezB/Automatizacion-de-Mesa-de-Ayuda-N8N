## Context

See `proposal.md` - Why. The backend directory API is complete (c-54/c-60): prefix `/api/v1/directorio` with alta/listado/detalle/PATCH/DELETE/purga, guarded by `require_directorio_admin` (`manages_directory`) and `require_directorio_lectura` (`can_read_directory`). The frontend has NO directory surface today.

Existing frontend constraints that shape the approach:
- `AuthContext` already exposes `rol` (from `GET /auth/me`, mirrored in `src/types/auth.ts` `IdentidadActual`), so a role-aware guard needs no backend change.
- Routing/nav live in `src/main.tsx` and `src/components/layout/Header.tsx`, driven by `alcance.modo` (`GLOBAL`/`PROPIO`/`VACIO`). `GLOBAL` includes `mesa_de_ayuda`, so mode alone cannot gate `/directorio`.
- `ProtectedRoute` centralizes route decisions in the pure function `resolverRedireccion` (`src/components/auth/ProtectedRoute.tsx`).
- Established patterns to mirror: `services/incidentesService.ts` + `hooks/useIncidentes.ts` (React Query, query-key const), `hooks/useSectores.ts` for the sector catalog, and `components/shared/{LoadingSpinner,ErrorAlert,EmptyState}` for states.
- `RolEmpleado` in the backend currently has THREE values; `gestion_incidentes` is introduced by sibling change c-86 (not yet in the repo).

## Goals / Non-Goals

**Goals:**
- A `/directorio` page gated by ROLE (`administrador_directorio`) consuming the existing endpoints only.
- Header nav entry visible only to `administrador_directorio`.
- Consistent loading/error/empty states and confirmations for destructive actions.

**Non-Goals:**
- No backend changes, migrations, or `docs/openapi.json` regeneration.
- No change to the role vocabulary, CHECK, or `role-policy` (owned by c-86).
- No server-side pagination (the endpoint is unpaginated and stays that way).

## Decisions

### D1 - Guard mechanism: extend `ProtectedRoute` with an optional `requiereRol`
Add `requiereRol?: string` to `ProtectedRoute` and extend the pure `resolverRedireccion({ isAuthenticated, modo, requiere, rol, requiereRol })`. Order: anonymous -> `/login`; if `requiereRol` set -> admit only `rol === requiereRol`, else redirect to `/`; else existing `requiere` mode logic unchanged.
- Alternatives: a separate wrapper component (more surface, duplicated 401 wiring); gating inside the page (mixes routing with page concerns, harder to test). Chosen because `AuthContext.rol` already exists and keeps a single pure, TDD-friendly decision function, and it is additive (existing behavior untouched).

### D2 - No backend change; role comes from existing `/auth/me`
`AuthContext` resolves `rol` via `obtenerIdentidad()` and `IdentidadActual` already includes it. Confirmed: no endpoint or OpenAPI change. The parenthetical in the requirement ("expose the role if only modo were exposed") resolves to NO CHANGE.

### D3 - Data layer mirrors existing services/hooks
- `src/types/directorio.ts`: `Empleado`, `EmpleadoCreate`, `EmpleadoUpdate`, `PurgaResultado`, `RolEmpleado`.
- `src/services/directorioService.ts`: `listarEmpleados({ soloActivos })`, `crearEmpleado`, `actualizarEmpleado`, `borrarEmpleadoArco`, `purgarDirectorio`.
- `src/hooks/useDirectorio.ts`: `useEmpleadosDirectorio(soloActivos)` query keyed `['directorio-empleados', soloActivos]`, plus mutations that invalidate that key on success.
- Alternatives: ad-hoc axios calls in the page (rejected - breaks the layered pattern and testability).

### D4 - Single role catalog with conditional sector
A single TS constant `ROLES_EMPLEADO: { value; label; requiresSector }[]` lists the four roles; `gestion_incidentes` sets `requiresSector: true`. The form shows the sector `Select` (options from existing `useSectores()`) and marks it required only when the selected role declares `requiresSector`. Sector stays optional for all other roles.
- Alternatives: per-role conditional logic scattered in the form (rejected - duplicates the role vocabulary). This mirrors the backend `requires_sector` policy attribute.

### D5 - Client-side pagination
The list endpoint returns an unpaginated array, so the page paginates the filtered list client-side with a fixed page size (20), reusing the `Paginacion` pattern from `Administracion/index.tsx`.
- Alternatives: no pagination (rejected for long directories); server pagination (rejected - would force a backend change, out of scope).

### D6 - Confirmations via the existing Dialog primitive
Reuse `src/components/ui/dialog.tsx` for ARCO-delete and purge confirmations, with neutral Spanish copy and an explicit irreversibility warning for ARCO.
- Alternative: `window.confirm` (rejected - inconsistent with the app and not testable with Testing Library patterns).

### D7 - Form fields and validation
Fields: legajo (required), nombre (required), email (required, format-checked in the UI), telefono (optional), rol (required via catalog), sector (conditional). Backend remains authoritative (unique legajo/email, E.164, role/sector coherence); backend errors are surfaced without clearing input.
- Alternatives: rely solely on backend validation (rejected - worse UX). Note: the UI validates for UX only; the backend is the source of truth.

## Risks / Trade-offs

- `gestion_incidentes` requires c-86 (enum + CHECK + policy + schema) -> Mitigation: record c-86 as a hard prerequisite in tasks; the role catalog is the single source; if c-86 has not landed, the backend rejects the alta and the UI surfaces the error. c-89 does NOT modify the vocabulary.
- Client-side pagination loads the full list -> acceptable for expected directory sizes; revisit only if the directory grows materially.
- Role guard is UX, not security -> the backend guards (`require_directorio_admin`) remain the enforcement boundary; FDIR-001 covers the 403 path.

## Migration Plan

- Pure frontend addition: no DB migrations, no env vars, no API changes. Deploy via the normal frontend build.
- Rollback: revert the c-89 commit (remove the page/service/hook/types and the three edits to route/nav/guard). No data to revert.

## Open Questions

None deferred. Resolved during design:
- Guard mechanism -> D1 (requireRol on the pure decision function).
- Backend role exposure -> D2 (already present; no change).
- Form fields/validation -> D7.
- Sector when required by role -> D4.
- Pagination -> D5 (client-side, page size 20).
- Confirmations -> D6.
- Dependency on `gestion_incidentes` -> recorded as a hard prerequisite (c-86).
