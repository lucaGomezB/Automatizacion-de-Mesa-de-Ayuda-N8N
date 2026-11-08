# Proposal: Mostrar el usuario logueado en la UI

## Why

Hoy el Header global solo ofrece "Cerrar sesión": el usuario autenticado no ve en ningún momento con qué nombre de usuario está operando. La identidad ya existe en el contexto de autenticación (`username` resuelto por `/auth/me`, c-81/IAH-012) y se consume para RBAC, pero nunca se renderiza. Mostrarla reduce el riesgo de operar bajo una sesión equivocada y da contexto inmediato en una aplicación multiusuario con roles y alcances distintos.

## What Changes

- Renderizar el `username` del usuario autenticado en el Header global, en la zona de sesión del extremo derecho.
- Ubicar el nombre ARRIBA del control "Cerrar sesión" (FSU-001): la zona de sesión pasa a ser una pila vertical (nombre en la línea superior, botón debajo).
- Consumir exclusivamente el `username` ya expuesto por `useAuth()`; sin lógica de autenticación nueva ni llamadas adicionales al backend.
- Actualizar las pruebas del Header (`Header.test.tsx`) para fijar el render del nombre y su posición relativa al botón.
- Sin cambios de backend, contrato de API, esquemas ni migraciones.

**Fuera de alcance:** mostrar rol/alcance o un avatar/desplegable de perfil; cualquier cambio en `AuthContext`, en `authService` o en `GET /auth/me`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `frontend-session-ui`: se AGREGA un requisito nuevo de presentación (identidad del usuario en el Header). El requisito existente FSU-001 (cierre de sesión) no cambia: el botón conserva su posición al extremo derecho; solo se le agrega el nombre encima.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `App/Frontend/src/components/layout/Header.tsx` | Modified | Lee `username` de `useAuth()` y lo renderiza sobre el botón |
| `App/Frontend/src/components/layout/Header.test.tsx` | Modified | Pruebas del render del nombre y de su posición |
| `App/Frontend/src/contexts/AuthContext.tsx` | Unchanged | Ya expone `username`; no se toca |

Sin cambios en backend, API, esquemas, migraciones, Docker ni N8N.

Nivel de gobernanza: LOW (texto de UI en un componente existente).

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| El bundle servido sigue cacheado y el nombre no aparece tras el cambio | Med | Rebuild (`docker compose up -d --build frontend`) + hard refresh (Ctrl+Shift+R); se documenta como paso obligatorio de deploy |
| `username` nulo (identidad sin resolver) renderiza una línea vacía | Low | El requisito y las pruebas cubren el caso `null`: no se renderiza texto de nombre |
| El cambio de layout rompe el apilado responsive del Header | Low | La zona de sesión ya es un `div` flex; se apila en vertical con utilidades Tailwind v3 existentes |

## Rollback Plan

`git revert` del commit del change: es puramente textual en un componente del frontend. No hay migraciones ni efectos de datos. Como el frontend corre desde una imagen horneada, revertir requiere reconstruir la imagen del frontend.

## Success Criteria

- [ ] El Header muestra el `username` del usuario autenticado en la zona de sesión.
- [ ] El nombre aparece ARRIBA del botón "Cerrar sesión" (pila vertical; el nombre precede al botón en el orden del DOM).
- [ ] Con `username` nulo no se renderiza texto de nombre.
- [ ] FSU-001 sigue cumpliéndose: el botón "Cerrar sesión" sigue visible para todo autenticado y cierra la sesión.
- [ ] `cd App/Frontend; npm run test` y `npm run lint` en verde.
- [ ] `openspec validate "c-183-mostrar-el-usuario-logueado-en-la-ui" --strict` en PASS.
