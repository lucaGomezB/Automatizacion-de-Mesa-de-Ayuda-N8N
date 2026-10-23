# Proposal: Migración a React 19 y actualización mayor del toolchain del frontend

## Why

El grupo `frontend-npm` de Dependabot (PR #34) propone 36 actualizaciones del frontend, entre ellas React 19, react-router 7 y eslint 10. La propuesta NO es instalable: `npm ci` falla con `ERESOLVE` porque `eslint-plugin-react@7.37.5` declara peer `eslint ^3 || ... || ^9.7` mientras el manifiesto pide `eslint ^10.13.0`. Hoy en `main` el frontend instala, lintea, compila y testea; queremos adoptar las versiones objetivo resolviendo los quiebres reales, en lugar de quedar fijados a React 18.

## What Changes

- **BREAKING** — React 18.3.1 → 19.3.1 y `react-dom` en sincronía; `@types/react` y `@types/react-dom` 18 → 19 (cambian tipos legados).
- **BREAKING** — `react-router-dom` 6.30.3 → 7.18.4; los flags `future` v7 dejan de ser props válidas (`v7_startTransition`, `v7_relativeSplatPath`).
- **BREAKING** — `eslint` 9 → 10; se resuelve el conflicto de peer retirando/reemplazando `eslint-plugin-react` (todas sus reglas consumidas ya están en `off`).
- **BREAKING** — toolchain mayor acoplado: `vite` 5 → 8, `@vitejs/plugin-react` 4 → 6, `vitest` 2 → 5, `@vitest/coverage-v8` 2 → 5, `happy-dom` 15 → 21, `globals` 15 → 17, `@types/node` 22 → 26.
- **BREAKING** — `tailwindcss` 3 → 4 y `tailwind-merge` 2 → 3 (plugin de PostCSS, directivas CSS y defaults visuales).
- Actualizaciones menores/mayores restantes: Radix UI, `@tanstack/react-query`, `axios`, `react-hook-form`, `recharts`; `lucide-react` 0.441 → 1.58 (mayor); `@testing-library/*` y `@eslint/js`.
- Se regenera `App/Frontend/package-lock.json`. Contrato de aceptación: `npm ci`, `npm run lint`, `npm run build` y `npm run test` pasan.

## Capabilities

### New Capabilities

- `frontend-dependencies`: contrato de resolubilidad e instalación reproducible, compatibilidad interna del toolchain (lint/build/test) y preservación del comportamiento observable del frontend tras una actualización mayor de dependencias.

### Modified Capabilities

- (ninguna)

## Impact

- `App/Frontend/package.json`, `App/Frontend/package-lock.json`
- `App/Frontend/eslint.config.js`, `postcss.config.cjs`, `tailwind.config.ts`, `src/index.css`
- `App/Frontend/vite.config.ts`, `vitest.config.ts`, `src/test/setup.ts`
- `App/Frontend/src/main.tsx` (prop `future`), `src/components/ui/**` (`React.ElementRef`)
- `App/Frontend/Dockerfile`, `.github/workflows/ci.yml` (versión de Node)
