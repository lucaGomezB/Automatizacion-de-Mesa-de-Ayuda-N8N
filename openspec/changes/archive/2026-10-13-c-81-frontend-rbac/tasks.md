## 1. Aprobacion y preparacion

- [x] 1.1 Confirmar la aprobacion humana del change (governance CRITICAL: superficie auth/RBAC) antes de escribir el endpoint backend; registrar la aprobacion en el change. APROBADO por el autor ("Arranca con el apply") — 2026-10-13.
- [x] 1.2 Cargar el SKILL.md de los skills de dominio aplicables (python-testing / pytest-coverage / react-dev) y confirmar convenciones de capas y de tests antes de codificar. Cargados: python-testing-patterns, python-design-patterns, tailwind-design-system (caveat v3), fastapi, react-dev. Capas routes -> services -> repositories -> models confirmadas; tests siguen el patron de tests/test_incident_visibility.py y Vitest con Testing Library.

## 2. Backend: endpoint de identidad y alcance (TDD)

- [x] 2.1 (RED) Escribir en `App/Backend/tests/` los tests del endpoint `GET /api/v1/auth/me` siguiendo el patron de `tests/test_incident_visibility.py`: autenticado con empleado `administrador_directorio` -> `GLOBAL`; `mesa_de_ayuda` -> `GLOBAL`; `usuario_final` -> `PROPIO`; sin empleado -> rol nulo + `VACIO`; anonimo -> 401 con envelope estandar. Verificar que fallan por endpoint ausente. Hecho en `tests/test_auth_me.py` (5 fallos por 404).
- [x] 2.2 (GREEN) Agregar el schema de respuesta en `App/Backend/app/schemas/auth.py` (`username`, `rol` y `alcance` con `modo`) y el endpoint en `App/Backend/app/routes/auth.py`, reutilizando `EmpleadoRepository.get_by_user_id` + `alcance_desde_empleado` (que lee `role_policy`) sin duplicar el mapeo rol -> alcance. Verificar que los tests de 2.1 pasan. 5/5 verdes.
- [x] 2.3 (TRIANGULATE) Agregar un caso que cambie el rol del empleado entre dos llamadas y verifique que el modo de alcance se recomputa (sin re-login); verificar que pasa. Confirmar ademas que la respuesta NO incluye sector, `ver_todos` ni `revision`. 7/7 verdes.
- [x] 2.4 Verificar que el contrato de login/refresh/logout no cambia: correr los tests existentes de auth y confirmar que siguen verdes (aditividad). 70 tests de auth verdes; ruff limpio.

## 3. Frontend: el contexto conoce rol y alcance (TDD)

- [x] 3.1 (RED) Escribir tests Vitest de `AuthContext` que verifiquen que tras login/MFA el estado expone `rol` y `alcance.modo` obtenidos del backend, y que una cuenta sin empleado expone alcance `VACIO`. Verificar que fallan. 4 fallos (rol undefined).
- [x] 3.2 (GREEN) Extender `App/Frontend/src/contexts/AuthContext.tsx` (tipos + consumo de `GET /auth/me`) y `App/Frontend/src/services/` para exponer `rol`/`alcance`. Verificar que los tests de 3.1 pasan. 9/9 verdes; nuevos `types/auth.ts` y `services/authService.ts`.
- [x] 3.3 (TRIANGULATE) Agregar un caso de re-resolucion del alcance (refresh de identidad) con un modo distinto; verificar que pasa. `refreshIdentidad()` cubierto (GLOBAL -> PROPIO).

## 4. Frontend: guard de rutas por alcance (TDD)

- [x] 4.1 (RED) Escribir tests Vitest del guard: `GLOBAL` accede a la superficie operativa; `PROPIO` accede a "Mis incidentes" y es redirigido desde la superficie operativa; `VACIO` redirige al portal; anonimo redirige a `/login`. Verificar que fallan. `src/components/auth/ProtectedRoute.test.tsx` (10 casos: pura + componente).
- [x] 4.2 (GREEN) Adaptar `ProtectedRoute` en `App/Frontend/src/main.tsx` para evaluar el modo de alcance ademas de `isAuthenticated`, agregar la ruta `/mis-incidentes` (guard PROPIO) y redirigir la superficie operativa `/admin` (guard GLOBAL) segun el modo. Verificar que los tests de 4.1 pasan. Guard extraido a `src/components/auth/ProtectedRoute.tsx`; `/admin` exige GLOBAL. La ruta `/mis-incidentes` se cablea en 6.2 junto con su pagina (evita import roto).

## 5. Frontend: navegacion por alcance (TDD)

- [x] 5.1 (RED) Escribir tests Vitest de `Header`: enlace operativo visible solo en `GLOBAL`; enlace "Mis incidentes" visible solo en `PROPIO`; portal visible para todo autenticado; en `VACIO` ninguno de los dos enlaces operativos. Verificar que fallan. `src/components/layout/Header.test.tsx` (2 fallos).
- [x] 5.2 (GREEN) Reemplazar el chequeo por pathname `isAdmin` en `App/Frontend/src/components/layout/Header.tsx` por una decision basada en `alcance.modo`. Verificar que los tests de 5.1 pasan. 3/3 verdes; tsc limpio.

## 6. Frontend: vista "Mis incidentes" (TDD)

- [x] 6.1 (RED) Escribir tests Vitest de la vista "Mis incidentes" (`App/Frontend/src/pages/MisIncidentes/`): lista los incidentes devueltos por `GET /api/v1/incidentes/` sin introducir un endpoint nuevo ni reconstruir datos en el cliente. Verificar que fallan. `index.test.tsx` (modulo ausente -> fallo).
- [x] 6.2 (GREEN) Implementar la vista y el hook reutilizando `useIncidentes.ts`/`incidentesService.ts` existentes; confirmar que no se crea superficie de API nueva en el backend. Verificar que los tests de 6.1 pasan. 3/3 verdes; ruta `/mis-incidentes` (guard PROPIO) cableada en `main.tsx`; sin endpoint backend nuevo.

## 7. Frontend: filtro de sector como conveniencia (TDD)

- [x] 7.1 (RED) Escribir tests Vitest del panel (`App/Frontend/src/pages/Administracion/index.tsx`): el filtro de sector esta disponible para roles con acceso al listado y su cambio/limpieza NO altera el conjunto de datos autorizado (no actua como frontera). Verificar que fallan. `index.sector-filter.test.tsx` (4 casos).
- [x] 7.2 (GREEN) Mantener el filtro de sector como filtro de conveniencia (no RBAC); documentar en el codigo que la seguridad reside en el backend. Verificar que los tests de 7.1 pasan. Comportamiento ya correcto (approval tests verdes); documentado en el docstring del panel y en `handleFiltroChange`.
- [x] 7.3 Verificar el manejo de denegaciones del backend: ante 403/404 por recurso fuera de alcance, la UI no expone el recurso ni concede datos por su cuenta (test del flujo de error). Cubierto en `index.sector-filter.test.tsx` (404 y 403: alerta de error, sin filas).

## 8. Sincronizacion de contratos y verificacion final

- [x] 8.1 Regenerar `docs/openapi.json` tras el nuevo endpoint y verificar con `cd App/Backend; pytest tests/test_openapi_sync.py -v`. 5/5 verdes; 26 rutas exportadas.
- [x] 8.2 Correr el subset offline del backend (`cd App/Backend; pytest -m "not integration"`) y confirmar verde. 1253 passed, 1 xfailed, 44 deselected.
- [x] 8.3 Correr el subset PostgreSQL integration (`cd App/Backend; pytest -m integration`) con la base descartable y confirmar verde. 44 passed.
- [x] 8.4 Correr `cd App/Backend; ruff check .` y confirmar limpio. All checks passed.
- [x] 8.5 Correr `cd App/Frontend; npm run test` y `npm run lint`, y confirmar verde. 157 tests verdes (33 archivos); ESLint 0 errores (2 warnings preexistentes en src/components/ui/).
- [x] 8.6 Verificar que la documentacion del change (proposal/design/specs/tasks) y el estado de OpenSpec quedan consistentes (`openspec validate c-81-frontend-rbac --type change --strict`). Change valido.
