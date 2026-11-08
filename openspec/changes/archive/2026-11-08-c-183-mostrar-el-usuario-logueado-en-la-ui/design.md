## Context

Ver `proposal.md` (Why). Estado actual y restricciones que condicionan el enfoque:

- El Header (`App/Frontend/src/components/layout/Header.tsx`) ya renderiza el control "Cerrar sesión" (FSU-001) y consume `const { alcance, rol, logout } = useAuth();` (línea 24). NO lee `username`.
- El contexto de autenticación (`App/Frontend/src/contexts/AuthContext.tsx`) YA expone `username: string | null`, resuelto vía `resolverIdentidad()` -> `obtenerIdentidad()` (`/auth/me`). El endpoint `GET /api/v1/auth/me` ya devuelve `{ username, rol, alcance.modo }` (c-81, IAH-012). No hay cambio de backend.
- La spec `frontend-session-ui` ya existe con FSU-001 (cierre de sesión) y FSU-002 (visibilidad de contraseña). Este change AGREGA FSU-003.
- El frontend es una SPA React 19 + TypeScript + Vite con primitivas shadcn. Tailwind es v3.4.11 (NO v4).
- El deploy del frontend es una imagen horneada: los cambios de UI solo se ven tras un rebuild y un hard refresh.

## Goals / Non-Goals

**Goals:**

- Mostrar el `username` autenticado en la zona de sesión del Header.
- Ubicar el nombre ARRIBA del botón "Cerrar sesión" (pila vertical).
- Consumir solo el `username` de `useAuth()`; cero lógica de autenticación nueva, cero llamadas al backend.

**Non-Goals:**

- No cambiar `AuthContext`, `authService`, `GET /auth/me`, ni el contrato de RBAC.
- No modificar FSU-001 (posición y comportamiento del botón de cierre de sesión) ni FSU-002.
- No agregar rol/alcance, avatar ni desplegable de perfil.

## Decisions

### D1 — Delta ADDED: requisito nuevo FSU-003, sin tocar FSU-001

**Decisión: agregar FSU-003 como requisito nuevo (`## ADDED Requirements`) en la capability existente `frontend-session-ui`; FSU-001 queda intacto.**

Fundamento: mostrar la identidad es una capacidad de presentación distinta del cierre de sesión. FSU-001 describe el botón y su posición (extremo derecho, después del indicador de salud); agregar el nombre encima no lo contradice, porque la pila completa sigue al extremo derecho. Modificar FSU-001 forzaría un delta MODIFIED del texto completo sin necesidad y aumentaría el riesgo de deriva. El ID FSU-003 continúa el esquema existente (FSU-001, FSU-002).

Alternativa considerada: MODIFIED FSU-001 para mencionar la pila vertical. Se descarta por ser un cambio de alcance innecesario sobre un requisito ya cumplido.

### D2 — Fuente de la identidad: `useAuth().username` (sin backend)

**Decisión: leer `username` del contexto existente. No se agrega endpoint ni campo.**

Fundamento: el dato ya viaja en `/auth/me` y ya vive en el contexto (c-81). Reutilizarlo mantiene el cambio frontend-only y evita nuevo acoplamiento. Es el mismo patrón que ya usan `alcance` y `rol` en el Header.

### D3 — Layout: pila vertical en la zona de sesión (Tailwind v3)

**Decisión: convertir la zona de sesión de la columna derecha en un contenedor vertical, con el nombre en una línea superior y el botón "Cerrar sesión" debajo.**

Enfoque: mantener el `div` de la derecha con `flex items-center justify-end gap-2 sm:gap-4`; envolver la parte de sesión (nombre + botón) en un `flex flex-col items-end` (o `items-end` en móvil) para apilar los dos elementos. El nombre se renderiza como un `span`/`p` con `text-xs sm:text-sm text-white/75 whitespace-nowrap`, condicionado a que `username` no sea nulo. Se usan solo utilidades Tailwind v3 (sin sintaxis v4). El orden del DOM (nombre antes que botón) garantiza la ubicación "arriba" y es el contrato que verifica la prueba.

### D4 — Pruebas: `Header.test.tsx` con `useAuth` mockeado

**Decisión: extender `Header.test.tsx` (que ya mockea `useAuth` y su helper `authState` ya incluye `username`).**

Casos: (a) con `username` dado, el nombre se renderiza; (b) el elemento del nombre precede al botón "Cerrar sesión" en el orden del documento (`compareDocumentPosition` / orden del contenedor); (c) con `username` nulo no aparece texto de nombre y el botón sigue presente; (d) el `username` mostrado coincide con el provisto por el contexto (triangulación con otro valor). Runner: `cd App/Frontend; npm run test src/components/layout/Header.test.tsx` (Vitest + Testing Library). Nota de cobertura: `src/components/layout/**` está excluido de cobertura (`AGENTS.md`), por lo que la cobertura no es un criterio de aceptación aquí.

## Risks / Trade-offs

- [Bundle cacheado tras el cambio] -> Mitigación: rebuild obligatorio (`docker compose up -d --build frontend`) + hard refresh; se documenta en tasks. Antecedente: un incidente reciente de imagen obsoleta servida en la instancia de campaña.
- [`username` nulo deja una línea vacía] -> Mitigación: render condicional + caso de prueba dedicado.
- [Falsa sensación de seguridad: el nombre es solo contexto visual] -> Mitigación: el backend sigue siendo el límite de seguridad; la UI no habilita superficie alguna por el nombre.

## Migration Plan

- Cambio puramente de presentación en el bundle del frontend. Sin migración de datos ni de esquema.
- Rollback: `git revert` del commit del change (ver `proposal.md`).
- Deploy: `docker compose up -d --build frontend` y hard refresh del navegador (paso manual).

## Open Questions

None.
