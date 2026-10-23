# Proposal: Migración del frontend a React 19 y react-router 7 (alcance reducido)

## Why

El grupo `frontend-npm` de Dependabot (PR #34) propone 36 actualizaciones del frontend, entre ellas React 19 y react-router 7. El alcance original de este change las empaquetaba junto con cuatro mayores de toolchain (Vite 8, Vitest 5, Tailwind 4, ESLint 10) y un bump de Node, lo que elevaba el riesgo y encadenaba cambios no relacionados. La revisión del árbol de peers muestra que React 19 y react-router 7 están DESACOPLADOS de esos mayores: React 19 corre sobre el Vite 5 / Vitest 2 / ESLint 9 actuales sin conflictos, y conservar ESLint 9 hace desaparecer por completo el conflicto `ERESOLVE` que hoy impide instalar el grupo (el peer de `eslint-plugin-react@7.37.5` sí cubre ESLint 9). Reducir el alcance a React 19 + react-router 7 convierte la migración en un cambio de bajo riesgo y verificación acotada.

## What Changes

- **BREAKING** — `react` y `react-dom` 18.3.1 → 19.x; `@types/react` y `@types/react-dom` 18 → 19.
- **BREAKING** — `react-router-dom` 6.x → 7.x (peer `react >=18`; compatible con React 19).
- Retirar el prop `future` de `<BrowserRouter>` en `src/main.tsx:116` (en v7 esos flags ya son comportamiento por defecto y dejan de ser props válidas). Es la ÚNICA edición de código fuente obligatoria.
- Node 20 → 24 en `App/Frontend/Dockerfile` y `.github/workflows/ci.yml`, JUSTIFICADO SOLO por el fin de vida de Node 20 (2026-04-30), NO por un requisito de React 19 ni de react-router 7.
- Migrar las 13 ocurrencias de `React.ElementRef` → `React.ComponentRef` en `src/components/ui/` (dialog, select, separator, label). Opcional y de bajo riesgo: `React.ElementRef` sigue existiendo como alias deprecado en `@types/react` 19, por lo que no bloquea el build.
- Sincronización de documentación y versión (stack declarado como React 19 en config, KB, tesis y AGENTS.md).
- Se regenera `App/Frontend/package-lock.json`. Contrato de aceptación: `npm ci`, `npm run lint`, `npm run build` y `npm run test` pasan sin flags.

## Out of Scope (diferido)

Los siguientes mayores quedan EXPLÍCITAMENTE fuera de este change y se abordarán en un change separado (número TBD):

- Toolchain de build/test: `vite` 8, `@vitejs/plugin-react` 6, `vitest` 5, `@vitest/coverage-v8` 5, `happy-dom` 21, `globals` 17, `@types/node` 26.
- Lint: `eslint` 10, `@eslint/js` 10, `eslint-plugin-react-hooks` 7.
- Estilos: `tailwindcss` 4, `tailwind-merge` 3.
- Librería de test: `@testing-library/jest-dom` 7.
- Retiro de `eslint-plugin-react`, `tailwindcss-animate` y `autoprefixer`.

Estos mayores están acoplados SOLO entre sí (plugin-react 6 exige vite ^8; coverage-v8 5 exige vitest 5; tailwind-merge 3 apunta a Tailwind 4; react-hooks 7 exige eslint 10), NO con React. Con ESLint 9 retenido, `eslint-plugin-react@7.37.5` permanece y el `ERESOLVE` desaparece. Por eso la migración a React 19 pasa a ser de bajo riesgo.

## Follow-ups

- `CHANGES.md` NO se edita en este change: está siendo reescrito por el PR #40 abierto. La sincronización del roadmap queda como follow-up una vez fusionado el PR.
- El change de mayores del toolchain (número TBD) absorberá las actualizaciones diferidas.

## Capabilities

### New Capabilities

- `frontend-dependencies`: contrato de resolubilidad e instalación reproducible del conjunto de dependencias del frontend, compatibilidad interna del toolchain (lint/build/test) sin flags de escape, y preservación del comportamiento observable tras la actualización de React 19 y react-router 7.

### Modified Capabilities

- `foundation-environment`: el stack tecnológico declarado en `openspec/config.yaml` pasa de "React 18 + TypeScript + Vite" a "React 19 + TypeScript + Vite".
- `ci-pipeline`: los jobs `frontend-tests` y `security-scan` pasan de Node 20 a Node 24.

## Impact

- `App/Frontend/package.json`, `App/Frontend/package-lock.json`
- `App/Frontend/src/main.tsx` (prop `future`), `App/Frontend/src/components/ui/**` (`React.ElementRef`)
- `App/Frontend/Dockerfile`, `.github/workflows/ci.yml` (versión de Node)
- `openspec/config.yaml`, `knowledge-base/02_descripcion_general.md`, `knowledge-base/08_arquitectura_propuesta.md`
- `docs/Tesis/v10 (IA)/paper/sections/06-implementacion.tex`, `docs/Tesis/v10 (IA)/tesis_para_agente.md` (regenerado)
- `docs/diagrams/despliegue.md`, `AGENTS.md`