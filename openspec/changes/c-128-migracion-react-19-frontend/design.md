# Design: Migración a React 19 y actualización mayor del toolchain del frontend

## Context

Ver `proposal.md` (Why). El estado actual es React 18 + Vite 5 + Vitest 2 + ESLint 9, todo verde en `main`. El PR #34 agrupa 36 actualizaciones en el grupo `frontend-npm` y no instala (`ERESOLVE`). El frontend usa el runtime moderno (`createRoot`), modo declarativo de react-router, flat config de ESLint y un stack de estilos shadcn/ui + Tailwind. La suite (Vitest/happy-dom + Testing Library) es la principal red de seguridad de comportamiento.

## Goals / Non-Goals

**Goals**
- Adoptar el conjunto objetivo del grupo `frontend-npm` de PR #34, con `npm ci` / `lint` / `build` / `test` en verde.
- Resolver el conflicto de peer eslint 10 ↔ `eslint-plugin-react` sin flags de escape.
- Preservar el comportamiento observable validado por la suite existente.

**Non-Goals**
- No se cambia comportamiento funcional, contratos de API ni rutas del frontend.
- No se adopta el modo data-router de react-router 7 (se mantiene el modo declarativo).
- No se aborda el endurecimiento de reglas de ESLint diferido desde C-09.

## Decisions

### D1 — Alcance: se adopta el conjunto completo del grupo `frontend-npm`
Las versiones están acopladas por peers (`@vitejs/plugin-react` 6 exige Vite 6+; `@vitest/coverage-v8` 5 exige Vitest 5; `tailwind-merge` 3 apunta a Tailwind 4). Adoptarlas por separado rompería el árbol. Se auditan explícitamente los tres ecosistemas de titular (React 19, react-router 7, ESLint 10) y los acoplamientos mayores (toolchain de build/test y stack de estilos).
- Alternativa considerada: dividir Tailwind 4 en un change aparte. Se descarta para no dejar un manifiesto intermedio no resolubles; queda como palanca de rollback si el volumen resulta excesivo.

### D2 — Resolución del conflicto ESLint 10 ↔ `eslint-plugin-react`
`eslint-plugin-react@7.37.5` no soporta ESLint 10 (sin release compatible). En `eslint.config.js` las únicas reglas consumidas del plugin (`react/react-in-jsx-scope`, `react/prop-types`) están en `off`; el valor real lo aportan `eslint-plugin-react-hooks` (`rules-of-hooks: error`, `exhaustive-deps: warn`) y `typescript-eslint`. Se retira `eslint-plugin-react` y su `settings.react`, conservando las mismas reglas efectivas.
- Alternativas: adoptar `@eslint-react/eslint-plugin` (diferido; aportaría reglas nuevas no requeridas) o fijar ESLint 9 (rechazado; incumple el objetivo).

### D3 — react-router 7 en modo declarativo
`react-router-dom` 7 reexporta todo desde `react-router`; `BrowserRouter`/`MemoryRouter`/`Routes`/`Route`/`Navigate`/`NavLink`/`Link`/`useNavigate` siguen disponibles, por lo que los imports no cambian. El único ajuste es retirar el prop `future` de `<BrowserRouter>` en `main.tsx`, porque en v7 esos flags ya son comportamiento por defecto y dejan de ser props válidas.

### D4 — Tailwind 4 con mínima superficie de cambio
Se migra `postcss.config.cjs` al plugin `@tailwindcss/postcss` (y se retira `autoprefixer`, absorbido por el pipeline de v4), se reemplazan las directivas `@tailwind base/components/utilities` por `@import "tailwindcss"` en `src/index.css` y se mantiene el `tailwind.config.ts` vía la directiva `@config` (menor churn que migrar el tema a `@theme`). Se retira `tailwindcss-animate` (declarado pero no registrado en `plugins`) por incompatibilidad con v4.
- Se asume como riesgo los cambios de defaults visuales de v4 (color de borde, ancho de `ring`, escala de `shadow`, `outline-none`).

### D5 — Versión de Node alineada
El toolchain objetivo (Vite 8 / `@vitejs/plugin-react` 6) exige Node ≥ 20.19 (o ≥ 22.12). Se alinea `App/Frontend/Dockerfile` y `.github/workflows/ci.yml` (hoy `node:20-alpine` / `node-version: "20"`) a una versión soportada y consistente; si `node:20` no alcanza el mínimo, se sube a la siguiente versión LTS.

### D6 — Contrato de aceptación
La migración se considera completa solo cuando `npm ci`, `npm run lint`, `npm run build` y `npm run test` finalizan en 0 sobre el árbol actualizado, sin `--force`/`--legacy-peer-deps`.

## Risks / Trade-offs

- **Volumen del change (muchos mayores acoplados)** → grupos de tareas escenificados con compuertas por grupo; palanca de rollback (D1) para aislar Tailwind 4 si es necesario.
- **Regresiones visuales de Tailwind 4** (borde/ring/shadow/outline) → suite DOM verde + revisión de los componentes de dominio; no hay snapshots visuales.
- **Tipos de React 19** (`React.ElementRef` deprecado/removido, `children` implícito, `JSX`) → `npm run build` (tsc) como detector; migrar `React.ElementRef` → `React.ComponentRef` donde los tipos 19 lo exijan.
- **Compatibilidad TypeScript 7 ↔ `typescript-eslint` 8.71** → verificar con `npm ci` y el build; si hay peer mismatch, ajustar el pin de `typescript-eslint`.
- **`lucide-react` mayor (0.441 → 1.58)** con iconos renombrados/removidos → el build detecta imports rotos.
- **Node insuficiente en la base `node:20-alpine`** → bump explícito de Node (D5).

## Migration Plan

1. Registrar baseline verde de `main` (4 comandos).
2. Actualizar manifiesto + regenerar lockfile; resolver el conflicto ESLint (D2) para que `npm ci` pase.
3. Adaptar por grupo: React 19, react-router 7, toolchain de build/test, stack de estilos, dependencias de runtime.
4. Verificar las cuatro compuertas y el job `frontend-tests` de CI.
5. **Rollback**: revertir la rama del change (`git checkout main -- App/Frontend` y restaurar `package-lock.json`). Sin migraciones de datos ni cambios de esquema.

## Open Questions

- Ninguna que cambie specs, enfoque o desglose de tareas. La versión exacta de Node (20.19 vs 22 LTS) y la estrategia de Tailwind (`@config` vs `@theme`) se deciden durante el apply según lo que exija el árbol resuelto.
