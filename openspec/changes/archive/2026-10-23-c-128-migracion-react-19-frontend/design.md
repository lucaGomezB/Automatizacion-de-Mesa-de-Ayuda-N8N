# Design: Migración del frontend a React 19 y react-router 7 (alcance reducido)

## Context

Ver `proposal.md` (Why). El estado actual es React 18 + react-router 6 + Vite 5 + Vitest 2 + ESLint 9 + Tailwind 3, todo verde en `main`. El grupo `frontend-npm` de Dependabot (PR #34) no instala porque, en su alcance completo, pide `eslint ^10` mientras `eslint-plugin-react@7.37.5` declara peer hasta `^9.7`. Este change adopta SOLO React 19 y react-router 7, dejando el toolchain en sus mayores actuales.

## Goals / Non-Goals

**Goals**
- Adoptar React 19 (+ tipos) y react-router 7 con `npm ci` / `lint` / `build` / `test` en verde y sin flags de escape.
- Mantener el toolchain actual (Vite 5, Vitest 2, ESLint 9, Tailwind 3) sin cambios.
- Preservar el comportamiento observable validado por la suite existente.
- Alinear la versión de Node a una con soporte vigente por fin de vida de Node 20.

**Non-Goals**
- No se actualizan los mayores del toolchain (diferidos; ver proposal).
- No se cambia comportamiento funcional, contratos de API ni rutas del frontend.
- No se adopta el modo data-router de react-router 7 (se mantiene el modo declarativo).

## Decisions

### D1 — Alcance reducido: React 19 y react-router 7 están desacoplados del toolchain

React 19 no exige ningún mayor del toolchain. Evidencia de peers verificada:

- `@vitejs/plugin-react@4.7.0` declara peer `vite ^4.2 || ^5 || ^6 || ^7` → React 19 corre sobre Vite 5 sin bump.
- `vitest@2` no declara peer de React.
- `@testing-library/react@16` declara peer `react ^18 || ^19`.
- `recharts@3` incluye `^19` en su peer de React.
- `lucide-react@1` declara peer `react ^16.5.1 || ^17 || ^18 || ^19`.

Los mayores del toolchain están acoplados SOLO entre sí (ver D3), no con React. Por eso se pueden adoptar React 19 y react-router 7 de forma aislada.

### D2 — D-NODE: Node 20 → 24, motivado por fin de vida

Node 20 alcanzó su fin de vida el 2026-04-30 (verificado en endoflife.date). El bump a Node 24 en `App/Frontend/Dockerfile` y `.github/workflows/ci.yml` responde EXCLUSIVAMENTE a esa obsolescencia: NO lo exige React 19 ni react-router 7 (ambos corren sobre Node 20 sin problema). Se elige Node 24 por ser la LTS vigente. El cambio se limita a la imagen base del `Dockerfile`, al `node-version` del job `frontend-tests` y al `node-version` del job `security-scan`.

### D3 — D-DEFER: por qué los mayores del toolchain se difieren

Los mayores diferidos están acoplados entre ellos, no con React:

- `@vitejs/plugin-react` 6 exige `vite ^8`.
- `@vitest/coverage-v8` 5 exige `vitest 5`.
- `tailwind-merge` 3 apunta a Tailwind 4.
- `eslint-plugin-react-hooks` 7 exige `eslint 10`.

Adoptarlos exige un salto coordinado de cuatro ecosistemas (build/test, lint, estilos, tipos), cada uno con su propia superficie de rotura. Al RETAENER ESLint 9, `eslint-plugin-react@7.37.5` sigue siendo válido y el conflicto `ERESOLVE` del PR #34 desaparece sin tocar el lint. Esto es lo que convierte esta migración en un cambio de bajo riesgo y lo que justifica separar los mayores en un change aparte (número TBD).

### D4 — Auditoría de código fuente: una sola edición obligatoria

React 19 NO requiere ninguna edición de código fuente en este repositorio. La auditoría verificó 0 ocurrencias de: `ReactDOM.render`/`hydrate`, `findDOMNode`, `createFactory`, contexto legacy, refs string, `defaultProps`/`propTypes` sobre funciones, `React.FC`, `children` implícito y namespace global `JSX`; además, todas las llamadas a `useRef` pasan un argumento.

La ÚNICA edición obligatoria es retirar el prop `future` de `<BrowserRouter>` en `src/main.tsx:116`: en react-router 7 esos flags (`v7_startTransition`, `v7_relativeSplatPath`) son comportamiento por defecto y `future` deja de ser una prop válida. El resto de la API declarativa usada (`BrowserRouter`, `Routes`, `Route`, `Navigate`, `NavLink`, `Link`, `useNavigate`) sigue disponible sin cambios de import.

### D5 — `React.ElementRef` → `React.ComponentRef` (opcional)

`React.ElementRef` sigue existiendo como alias deprecado en `@types/react` 19, por lo que su uso NO bloquea el build. Se migran igualmente las 13 ocurrencias a `React.ComponentRef` (el reemplazo recomendado) por higiene de tipos y bajo riesgo: dialog.tsx (4), select.tsx (7), separator.tsx (1), label.tsx (1).

### D6 — Contrato de aceptación

La migración se considera completa solo cuando `npm ci`, `npm run lint`, `npm run build` y `npm run test` finalizan en 0 sobre el árbol actualizado, sin `--force`/`--legacy-peer-deps`, y `openspec validate c-128-migracion-react-19-frontend --strict` pasa.

## Risks / Trade-offs

- **Tipos de React 19** → `npm run build` (tsc) como detector; la auditoría (D4) confirma que no hay APIs legadas en uso.
- **`react-router` 7 rompe el prop `future`** → única edición obligatoria (D4); los tests de enrutado validan el comportamiento.
- **Regresión silenciosa en el enrutado** → la suite existente es la red de seguridad; no se retira ni deshabilita cobertura.
- **Nombre de scenario desactualizado en la spec de `ci-pipeline`** → OpenSpec 1.10.0 rechaza el renombre de un scenario en un requirement MODIFIED (pérdida por nombre exacto). Se conserva el nombre "El job de frontend corre sobre Node 20" y se actualiza su cuerpo a Node 24. Trade-off aceptado: la herramienta prioriza la estabilidad del identificador del scenario sobre la coincidencia literal del texto.

## Migration Plan

1. Registrar baseline verde de `main` (4 comandos).
2. Actualizar `package.json` (react, react-dom, @types/react, @types/react-dom, react-router-dom) + `npm install` sin flags; regenerar lockfile.
3. Editar `src/main.tsx` (retirar `future`) y, opcionalmente, `React.ElementRef` → `React.ComponentRef`.
4. Bump de Node 20 → 24 en `Dockerfile` y `ci.yml`.
5. Sincronizar documentación y versión (config, KB, tesis, AGENTS.md).
6. Verificar las cuatro compuertas + `openspec validate --strict`.
7. **Rollback**: revertir la rama del change (`git checkout main -- App/Frontend` y restaurar `package-lock.json`). Sin migraciones de datos ni cambios de esquema.

## Open Questions

- Ninguna que cambie specs, enfoque o desglose de tareas. El número del change que absorberá los mayores del toolchain queda por definir (TBD) cuando se proponga.