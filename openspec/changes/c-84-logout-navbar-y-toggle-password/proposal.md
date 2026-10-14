## Why

Dos huecos de usabilidad en el chrome de sesión del frontend: (1) el usuario autenticado no tiene forma de cerrar sesión desde la navegación global — la barra de encabezado (Header) nunca renderiza una acción de logout, de modo que la sesión queda atrapada hasta expirar el token; y (2) el campo de contraseña del login no ofrece confirmación visual de lo tipeado, lo que incrementa errores de tipeo en un formulario crítico. Ambos son ajustes de interfaz acotados, sin lógica de autenticación nueva.

## What Changes

- El Header global renderiza un botón "Cerrar sesión" al extremo derecho de la barra, visible para TODO usuario autenticado (independiente de `alcance.modo`), que invoca el `logout()` ya existente de `AuthContext` y navega a `/login`. Hoy la columna derecha solo se renderiza cuando `alcance.modo === 'GLOBAL'` (indicador de salud de la API); el logout debe renderizarse para todos los alcances autenticados.
- El campo de contraseña del login incorpora un control de visibilidad (icono de ojo) dentro del input: por defecto la contraseña queda oculta (`type="password"`); al alternar pasa a `type="text"`. El control es un `button` real, operable por teclado, con `aria-label` que refleja el estado ("Mostrar contraseña" / "Ocultar contraseña").
- No se introducen cambios de lógica de autenticación, endpoints, schemas ni dependencias externas. Frontend únicamente.

## Capabilities

### New Capabilities

- `frontend-session-ui`: chrome de sesión del frontend — affordances de interfaz ligadas a la sesión del usuario en la navegación global (acción de cerrar sesión accesible para cualquier usuario autenticado) y en el formulario de acceso (control de visibilidad de la contraseña), sin alterar la lógica de autenticación.

### Modified Capabilities

- Ninguna. El comportamiento de alcance/RBAC (`frontend-rbac`) no cambia: el logout es global a todo autenticado y no altera la navegación por modo. Los contratos de datos (`frontend-data-layer`) y de testing (`frontend-testing`) no cambian.

## Impact

- `App/Frontend/src/components/layout/Header.tsx` — agrega el botón de cierre de sesión al extremo derecho; deja de condicionar la columna derecha a `esGlobal` para el logout.
- `App/Frontend/src/pages/LoginPage/index.tsx` — agrega el estado de visibilidad y el control de ojo al input de contraseña.
- `App/Frontend/src/pages/LoginPage/LoginPage.test.tsx` — nuevos casos para el toggle de visibilidad y su accesibilidad.
- Posible nuevo test del Header (`App/Frontend/src/components/layout/Header.test.tsx`) o extensión de su suite si existiera. Nota: `src/components/layout/**` está EXCLUIDO de cobertura; el test es deseable por comportamiento, no por umbral.
- Reutiliza `logout()` de `App/Frontend/src/contexts/AuthContext.tsx` (ya existe, línea ~226) y `useNavigate` de `react-router-dom`. Iconos `LogOut`, `Eye` y `EyeOff` de `lucide-react` (ya en uso en el proyecto).
- Sin cambios en backend, N8N, migraciones ni dependencias.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|-----------|
| Romper el layout de 3 columnas del Header al agregar un elemento a la derecha | Media | Mantener la columna derecha como `flex justify-end gap-*` que aloja salud + logout; el logout va después del indicador |
| El checkbox de visibilidad filtra la contraseña de forma no intencional | Baja | Estado local por defecto oculto; el tipo solo cambia con la acción explícita del usuario; test que afirma `type="password"` inicial |
| Control de ojo inaccesible (solo icono) | Baja | `button` real con `aria-label` dinámico y operable por teclado |
| Logout disparado sin confirmación accidental | Baja | Se alinea con el patrón existente del proyecto (no hay diálogos de confirmación de logout); no se introduce uno nuevo |

## Rollback Plan

Revertir el commit del change. Al ser frontend puro, sin endpoints, esquemas ni migraciones, no hay estado persistente que revertir. Header y LoginPage vuelven a su versión anterior.

## Dependencies

- Ninguna nueva. Se reutilizan `logout()` (`AuthContext`), `useNavigate` (`react-router-dom`) y los iconos de `lucide-react` ya presentes.

## Success Criteria

- [ ] Todo usuario autenticado ve el botón "Cerrar sesión" al extremo derecho del Header, en cualquier `alcance.modo`.
- [ ] Accionar el botón invoca el `logout()` existente y navega a `/login`.
- [ ] El input de contraseña del login está oculto por defecto y alterna a texto visible mediante un control accesible (aria-label dinámico, operable por teclado).
- [ ] La lógica de login/credenciales no cambia; la suite Vitest del frontend pasa.

## Open Questions

1. **Estilo del botón de logout: RESUELTO.** Icono `LogOut` + texto visible "Cerrar sesión", alineado con el estilo de los botones de navegación del Header (variante ghost sobre fondo primario), al extremo derecho.
2. **Confirmación de logout: RESUELTO.** NO se agrega diálogo de confirmación: no existe un patrón de confirmación de logout en el proyecto y el `logout()` actual es inmediato. Mantener consistencia.
3. **Toggle de contraseña: RESUELTO.** Iconos `Eye`/`EyeOff` de `lucide-react` dentro del input; el estado y su accesibilidad se describen en R2 del spec.
4. **Alcance de la spec: RESUELTO.** Una sola capability nueva `frontend-session-ui` con dos requisitos (R1 logout en navbar, R2 toggle de contraseña). No se modelan capacidades existentes como modificadas porque su comportamiento no cambia.
