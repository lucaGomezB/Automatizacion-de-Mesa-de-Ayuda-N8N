## Context

Ver `proposal.md` — Why. Estado actual relevante:

- El Header (`App/Frontend/src/components/layout/Header.tsx`) es un grid de 3 columnas: identidad, navegación principal y una columna derecha (`flex justify-end`). La columna derecha HOY solo renderiza contenido cuando `esGlobal` (`alcance.modo === 'GLOBAL'`): el indicador de salud de la API. No existe ninguna acción de logout en la navegación.
- `AuthContext` (`App/Frontend/src/contexts/AuthContext.tsx`) ya expone `logout()` (línea ~226): revoca el refresh token fire-and-forget, limpia el estado local y deja `isAuthenticated = false`. No requiere cambios.
- `useAuth()` ya se consume en el Header para `alcance`.
- El login (`App/Frontend/src/pages/LoginPage/index.tsx`) tiene un único input de contraseña (`type="password"`, `id="password"`), con `Label` asociada. Ya importa iconos de `lucide-react` (`LogIn`, `ShieldCheck`).
- `Input` (`components/ui/input.tsx`) es un `forwardRef` que reenvía `type` y acepta `className`; no incluye slot para adornos, por lo que el control de ojo se compone en el contenedor del login.
- `Button` (`components/ui/button.tsx`) usa `class-variance-authority` con variantes `ghost`, `outline`, etc. y tamaño `icon`.
- Rutas en `main.tsx`: `/login` existe y es pública. La navegación post-logout a `/login` ya es un destino válido.
- Estilos de la barra: fondo `bg-primary text-primary-foreground`; los NavLinks usan variantes de `bg-white/20` / `hover:bg-white/10`. Tailwind v3.4.11 (NO usar sintaxis v4).

## Goals / Non-Goals

**Goals:**
- Logout visible y accesible para todo usuario autenticado, al extremo derecho del Header, sin depender del `alcance.modo`.
- Control de visibilidad de contraseña accesible en el login, oculto por defecto, sin tocar la lógica de credenciales.
- Cambios mínimos y localizados; sin nuevas dependencias ni lógica de autenticación.

**Non-Goals:**
- No se modifica `AuthContext`, ni `logout()`, ni la lógica de login/credenciales.
- No se refactoriza el grid del Header más allá de lo necesario para alojar el botón.
- No se agrega diálogo de confirmación de logout (no existe ese patrón hoy).
- No se cambia el backend ni rutas.

## Decisions

### D1 — El logout se aloja en la columna derecha, fuera del condicional `esGlobal`

El botón de logout se agrega dentro de la columna derecha existente (`<div className="flex justify-end">`), en un contenedor `flex items-center gap-*`, ubicado DESPUÉS del bloque del indicador de salud. A diferencia del indicador (que permanece condicionado a `esGlobal`), el botón de logout se renderiza siempre.

- **Rationale**: la columna derecha ya es el punto de anclaje natural para acciones del chrome; colocarlo allí después del indicador satisface FSU-001 (extremo derecho, visible para todos) sin reestructurar el grid de 3 columnas.
- **Alternativas consideradas**:
  - **Agregarlo en la columna central (navegación)**: NO — rompe la semántica de navegación (un `NavLink` es una ruta; el logout es una acción) y no queda al extremo derecho.
  - **Cuarta columna**: rechazada — el logout no justifica cambiar `grid-cols-[auto_1fr_auto]`, y complicaría el responsive.

### D2 — El botón reutiliza `logout()` + `useNavigate`, sin estado propio

El handler del botón es `() => { logout(); navigate('/login'); }`. No se guarda estado ni se duplica la lógica de limpieza. El Header ya consume `useAuth()`; se agrega `logout` a la desestructuración y `useNavigate` de `react-router-dom`.

- **Rationale**: FSU-001 exige reutilizar el `logout()` existente; el `logout()` ya limpia tokens y estado. Navegar después garantiza que, si el usuario estaba en una ruta protegida, no quede en una pantalla sin sesión (aunque `ProtectedRoute` también redirige, la navegación explícita hace el comportamiento determinista y testeable).

### D3 — Estilo del botón alineado con el chrome del Header

Se usa `Button` variante `ghost` (o una clase equivalente sobre fondo primario) con icono `LogOut` (lucide) + texto visible "Cerrar sesión". Si el ancho es limitado en móvil, el texto puede ocultarse (`hidden sm:inline`) conservando el icono, siguiendo el patrón del indicador de salud (punto en móvil, texto en tablet+).

- **Rationale**: consistencia visual con los botones de navegación (`text-white/75 hover:bg-white/10 hover:text-white`); el proyecto no usa emojis y el texto debe ser español neutro sin tildes problemáticas — usar "Cerrar sesión" (con tilde es válido en UI copy; el código/DOM conserva el texto tal cual).

### D4 — El toggle de contraseña vive en el contenedor del login, con estado local

Se agrega un estado `showPassword` (default `false`) en `LoginPage`. El input usa `type={showPassword ? 'text' : 'password'}`. El control es un `button` `type="button"` (para no disparar el submit) posicionado con `relative` en el contenedor y `absolute` en el botón; muestra `Eye`/`EyeOff`.

- **Rationale**: el componente `Input` es un primitivo sin slot de adorno; agregar el adorno en el contenedor del login evita modificar el primitivo compartido (que está excluido de cobertura y es shadcn). `type="button"` es crítico para no enviar el form.
- **Alternativas consideradas**:
  - **Modificar `Input` para aceptar un `endAdornment`**: rechazada — agranda el alcance del change tocando un primitivo compartido sin necesidad.
  - **Extender el input con `pr-*`**: aceptada como detalle de implementación para que el texto no quede debajo del icono.

### D5 — Accesibilidad del toggle (FSU-002)

El botón lleva `aria-label` dinámico ("Mostrar contraseña" cuando está oculta, "Ocultar contraseña" cuando está visible) y `aria-pressed` si se desea reflejar estado. Es un `button` real, por lo que es operable por teclado por defecto. El icono es decorativo (`aria-hidden`).

- **Rationale**: FSU-002 exige un control accesible con `aria-label` que refleje el estado; un `button` nativo cubre la operabilidad por teclado sin handlers extra.

### D6 — Testing (Vitest)

- `LoginPage.test.tsx`: extender con casos de toggle (oculta por defecto, alternar a texto, alternar de nuevo a password, `aria-label` dinámico, el valor enviado no cambia). El test ya mockea `useAuth` y `useHealthCheck`.
- Header: crear/extender un test que afirme que el botón "Cerrar sesión" aparece con `alcance.modo = 'PROPIO'` (no solo GLOBAL) y que accionarlo invoca `logout()` y navega a `/login`. Nota: `src/components/layout/**` está EXCLUIDO de cobertura; el test es deseable por comportamiento, no por umbral.

## Risks / Trade-offs

- **El botón desborda el ancho en móvil** → ocultar el texto y conservar el icono (`hidden sm:inline`), igual que el indicador de salud.
- **El toggle dispara el submit accidentalmente** → `type="button"` explícito en el control de ojo.
- **`Input` no expone ref/estado para el adorno** → el toggle es un botón hermano posicionado en el contenedor, no una modificación del primitivo.
- **Regresión en el test existente de LoginPage** → mantener los `aria-label`/roles actuales y agregar casos sin romper los existentes (`getByLabelText('Contraseña')` debe seguir funcionando con la `Label` asociada al input).
- **Test del Header sin impacto en cobertura** → se documenta la exclusión; el valor del test es de comportamiento.

## Migration Plan

1. `Header.tsx`: agregar `useNavigate`, desestructurar `logout` de `useAuth`, e insertar el botón "Cerrar sesión" al final de la columna derecha (siempre renderizado).
2. `LoginPage/index.tsx`: agregar estado `showPassword`, envolver el input de contraseña en un contenedor `relative` y agregar el `button` de ojo con `aria-label` dinámico y `type="button"`.
3. Tests: extender `LoginPage.test.tsx` (toggle) y crear/extender el test del Header (visibilidad por alcance + handler).
4. `npm run lint`, `npm run test`, `npm run build` en `App/Frontend/`.

Rollback: revertir el commit. Frontend puro, sin migraciones ni estado persistente.

## Open Questions

- Ninguna pendiente. Las decisiones de estilo (D3), confirmación (no hay diálogo, ver `proposal.md` OQ2) y accesibilidad (D5) quedaron resueltas para no bloquear el apply.
