## Why

El backend ya expone la API completa del directorio de empleados (`/api/v1/directorio`, change c-54/c-60), pero no existe ninguna superficie en el frontend para operarla: hoy solo se puede gestionar el directorio por API/CLI. El `administrador_directorio` no puede dar de alta, editar, activar/desactivar, borrar por ARCO ni disparar la purga desde la interfaz. Esta change cierra esa brecha sin tocar el backend.

## What Changes

- Nueva pagina `/directorio` (React Router) que consume los endpoints EXISTENTES del directorio: listar, crear, editar, activar/desactivar, borrado ARCO y purga por retencion.
- Guard de ruta por ROL (no solo por modo): accesible SOLO a `administrador_directorio`. El alcance `GLOBAL` tambien incluye a `mesa_de_ayuda`, por lo que el modo por si solo no alcanza.
- Entrada de navegacion en el `Header` visible unicamente para `administrador_directorio`.
- Formulario de empleado con seleccion de rol (incluye `gestion_incidentes` y el campo de sector condicional) y validacion de campos.
- Confirmaciones para acciones destructivas (borrado ARCO, purga) con copy en espanol neutro; estados de carga/error/vacio consistentes con el resto de la app.
- NO se esperan cambios de backend: el rol del usuario ya viaja en `GET /auth/me` (`rol`) y lo expone `AuthContext`. No se agregan endpoints ni se regenera `docs/openapi.json`.

## Capabilities

### New Capabilities
- `frontend-directorio`: superficie de administracion del directorio de empleados (alta, listado con filtro activo/inactivo, edicion, activar/desactivar, borrado ARCO, purga por retencion) sobre la API existente.

### Modified Capabilities
- `frontend-rbac`: se agrega navegacion y guard de ruta basados en el ROL `administrador_directorio`, mas alla del modo de alcance (`GLOBAL`/`PROPIO`).

## Impact

- `App/Frontend/src/pages/Directorio/` (nueva pagina y componentes), `App/Frontend/src/hooks/useDirectorio.ts` (nuevo), `App/Frontend/src/services/directorioService.ts` (nuevo), `App/Frontend/src/types/directorio.ts` (nuevo).
- `App/Frontend/src/main.tsx` (ruta `/directorio`), `App/Frontend/src/components/layout/Header.tsx` (entrada de navegacion), `App/Frontend/src/components/auth/ProtectedRoute.tsx` (guard por rol).
- Sin cambios de backend, sin migraciones, sin regenerar `docs/openapi.json`.
- Dependencia dura: el rol `gestion_incidentes` y su requisito de sector los introduce la change hermana c-86 (enum + CHECK + policy + schema). c-89 solo lo refleja en la UI.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `gestion_incidentes` no existe aun en el backend (c-86 pendiente) y su alta seria rechazada | Alta | Marcar c-86 como prerequisito en tareas; el catalogo de roles de la UI es fuente unica y condiciona el campo sector; task de verificacion de c-86 |
| El guard por rol podria debilitar el RBAC existente | Baja | Guard ADITIVO: no altera rutas `GLOBAL`/`PROPIO`; se conserva la frontera de seguridad en el backend |
| Confirmaciones destructivas incompletas | Baja | Escenarios de spec y tests Vitest para ARCO y purga |

## Rollback Plan

Revertir el commit de c-89: eliminar la pagina `Directorio/`, el servicio/hook/tipos, y las tres ediciones de ruta/nav/guard. El backend no cambia, por lo que no hay migracion ni dato que revertir.

## Success Criteria

- [ ] `/directorio` es accesible SOLO a `administrador_directorio`; `mesa_de_ayuda` (GLOBAL) y `usuario_final` (PROPIO) son redirigidos.
- [ ] La UI ejecuta las seis operaciones (listar/crear/editar/activar-desactivar/ARCO/purga) contra los endpoints existentes.
- [ ] La nav de `/directorio` se muestra solo a `administrador_directorio`.
- [ ] Escenarios de destructivos con confirmacion; estados de carga/error/vacio consistentes.
- [ ] `openspec validate c-89-ui-directorio-administrador --strict` pasa; suite Vitest verde.
