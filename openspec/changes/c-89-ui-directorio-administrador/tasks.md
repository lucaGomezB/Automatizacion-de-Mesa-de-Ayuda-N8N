## 1. Prerequisites and foundations

- [x] 1.1 Confirm the role vocabulary prerequisite c-86: verify `gestion_incidentes` exists in `App/Backend/app/models/empleado.py` (enum + CHECK) and `App/Backend/app/services/role_policy.py` with `requires_sector=true`. Command: `grep -rn "gestion_incidentes" App/Backend/app`. If absent, record it as a blocking dependency in the change notes (the alta of that role will fail until c-86 lands); the rest of the change proceeds.
- [x] 1.2 Create `App/Frontend/src/types/directorio.ts` with `RolEmpleado`, `Empleado`, `EmpleadoCreate`, `EmpleadoUpdate`, `PurgaResultado` and the single `ROLES_EMPLEADO` catalog (`value`, `label`, `requiresSector`; `gestion_incidentes` -> `requiresSector: true`). Verify `npm run build` typechecks clean.
- [x] 1.3 Confirm no backend change is required: verify `App/Frontend/src/types/auth.ts` `IdentidadActual` and `AuthContext` already expose `rol`; document that `/auth/me` and `docs/openapi.json` are untouched.

## 2. Data layer (TDD: service + hook)

- [x] 2.1 Write `App/Frontend/src/services/directorioService.test.ts` (RED) for `listarEmpleados({ soloActivos })`, `crearEmpleado`, `actualizarEmpleado`, `borrarEmpleadoArco`, `purgarDirectorio` hitting the exact `/directorio/...` paths and `solo_activos` param; then implement `App/Frontend/src/services/directorioService.ts` (GREEN). Verify `npm run test -- directorioService` passes and mock call args match the endpoints.
- [x] 2.2 Write `App/Frontend/src/hooks/useDirectorio.test.tsx` (RED) for `useEmpleadosDirectorio(soloActivos)` returning list data and for each mutation invalidating the `['directorio-empleados', soloActivos]` query on success; then implement `App/Frontend/src/hooks/useDirectorio.ts` (GREEN). Verify `npm run test -- useDirectorio` passes.
- [x] 2.3 TRIANGULATE with an error-path case (list query failure and a rejected mutation) so the hook exposes `isError`/error without throwing. Verify tests pass.

## 3. Role-aware guard (TDD: pure decision function)

- [x] 3.1 Extend the `App/Frontend/src/components/auth/ProtectedRoute.test.tsx` suite (RED) for the new `resolverRedireccion({ isAuthenticated, modo, requiere, rol, requiereRol })`: admits matching `rol`, redirects a non-matching authenticated role to `/`, redirects anonymous to `/login`, and leaves existing `GLOBAL`/`PROPIO` behavior unchanged. Then extend `resolverRedireccion` + add `requiereRol?: string` to `ProtectedRoute` in `App/Frontend/src/components/auth/ProtectedRoute.tsx` (GREEN). Verify `npm run test -- ProtectedRoute` passes.
- [x] 3.2 TRIANGULATE role-gating with `administrador_directorio` (admit) vs `mesa_de_ayuda` with `modo=GLOBAL` (redirect). Verify tests pass.

## 4. Directory page: listing (TDD: page/component)

- [x] 4.1 Write `App/Frontend/src/pages/Directorio/index.test.tsx` (RED) asserting the page renders the employee list (legajo, nombre, email, sector, rol, estado) from `useDirectorio`, shows `LoadingSpinner` while loading, `ErrorAlert` with retry on error, and `EmptyState` on empty; then implement `App/Frontend/src/pages/Directorio/index.tsx` and the list/table component (GREEN). Verify `npm run test -- Directorio` passes.
- [x] 4.2 Add the activo/inactivo filter with options "todos" (default) and "solo activos" mapped to `solo_activos`, and client-side pagination (page size 20) reusing the `Paginacion` pattern. Verify tests cover filter switching and page navigation.

## 5. Directory page: create/edit form (TDD: form)

- [x] 5.1 Write form tests (RED) for required-field validation (legajo/nombre/email) and email format, and for the conditional sector rule: selecting `gestion_incidentes` marks sector required and blocks submit; a non-sector role allows submit without sector. Then implement the form component (GREEN). Verify `npm run test -- Directorio` passes.
- [x] 5.2 Wire create (`POST /directorio/empleados`) and edit (`PATCH /directorio/empleados/{id}`) through the hook mutations, surfacing backend errors without clearing input. Verify tests cover a backend rejection path (e.g. duplicate email).

## 6. Directory page: activate/deactivate, ARCO delete, purge (TDD + confirmations)

- [x] 6.1 Write tests (RED) for activate/deactivate sending `activo=true|false` via PATCH and refreshing the list; then implement (GREEN). Verify `npm run test -- Directorio` passes.
- [x] 6.2 Write tests (RED) for the ARCO-delete confirmation dialog (irreversible warning, cancel does not call the service, confirm calls `borrarEmpleadoArco`) and for the purge confirmation (confirm calls `purgarDirectorio` and shows the returned `purgados` count). Then implement using `src/components/ui/dialog.tsx` (GREEN). Verify `npm run test -- Directorio` passes.

## 7. Navigation and routing wiring

- [x] 7.1 Add the `/directorio` route in `App/Frontend/src/main.tsx` wrapped in `ProtectedRoute` with `requiereRol="administrador_directorio"`; verify the route admits only that role.
- [x] 7.2 Add a role-gated nav entry to `/directorio` in `App/Frontend/src/components/layout/Header.tsx` (visible only to `administrador_directorio`); extend `Header` tests to assert `mesa_de_ayuda` (GLOBAL) does NOT see it. Verify `npm run test -- Header` passes.

## 8. Integration and verification

- [x] 8.1 Run the full frontend suite: `cd App/Frontend; npm run test` and `npm run lint`; verify green with no regressions in existing RBAC tests.
- [x] 8.2 Run `cd App/Frontend; npm run build` to confirm TypeScript typecheck and production build succeed.
- [x] 8.3 Run `openspec validate c-89-ui-directorio-administrador --strict` and confirm it passes.
