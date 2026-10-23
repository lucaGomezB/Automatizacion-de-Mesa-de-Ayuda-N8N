# Tasks: Migración a React 19 y actualización mayor del toolchain del frontend

## 1. Baseline y preparación

- [ ] 1.1 Registrar el baseline verde de `main` en `App/Frontend` (`npm ci`, `npm run lint`, `npm run build`, `npm run test`) — verificación: los cuatro comandos finalizan en 0 y sus salidas quedan registradas
- [ ] 1.2 Inventariar imports y configuración afectados por los mayores (React 19, react-router 7, ESLint 10, toolchain) — verificación: informe que lista archivos y puntos de contacto
- [ ] 1.3 Fijar la versión de Node soportada por el toolchain objetivo y alinearla en `App/Frontend/Dockerfile` y `.github/workflows/ci.yml` — verificación: ambos declaran la misma versión y no la mínima insuficiente

## 2. ESLint 10 y conflicto de peer

- [ ] 2.1 Actualizar `eslint` a 10.x, `@eslint/js` a 10.x y `eslint-plugin-react-hooks` a 7.x en `App/Frontend/package.json` — verificación: `npm ci` ya no aborta con `ERESOLVE` por el peer de `eslint-plugin-react`
- [ ] 2.2 Resolver `eslint-plugin-react` (retirarlo, dado que sus únicas reglas consumidas están en `off`, o reemplazarlo por uno compatible con ESLint 10) — verificación: `npm ci` completa sin `--force` ni `--legacy-peer-deps`
- [ ] 2.3 Ajustar `App/Frontend/eslint.config.js` (quitar plugin y `settings.react` obsoletos, conservar `rules-of-hooks: error` y `exhaustive-deps: warn`) — verificación: `npm run lint` finaliza en 0 con las mismas reglas efectivas

## 3. Auditoría React 19

- [ ] 3.1 Actualizar `react`, `react-dom` a 19.x y `@types/react`, `@types/react-dom` a 19.x — verificación: la instalación resuelve y `npm run test` arranca
- [ ] 3.2 Auditar y corregir las APIs de tipos removidas o cambiadas (`React.ElementRef` → `React.ComponentRef`, `useRef` con argumento, `children` implícito, namespace `JSX`) — verificación: `npm run build` (tsc) termina sin errores de tipos
- [ ] 3.3 Auditar las APIs legadas de runtime removidas en React 19 (`ReactDOM.render`, `findDOMNode`, `defaultProps`/`propTypes` en funciones, refs string) — verificación: no quedan usos pendientes y `npm run test` queda verde

## 4. Auditoría react-router 7

- [ ] 4.1 Actualizar `react-router-dom` a 7.x — verificación: los imports existentes (`BrowserRouter`, `Routes`, `Route`, `Navigate`, `NavLink`, `Link`, `useNavigate`) resuelven sin cambios
- [ ] 4.2 Retirar el prop `future` de `<BrowserRouter>` en `src/main.tsx` (los flags v7 son comportamiento por defecto) — verificación: `npm run build` sin error de tipos y los tests de enrutado verdes
- [ ] 4.3 Auditar APIs removidas o reestructuradas de react-router 7 (`json`/`defer`, data routers, `fallbackElement`) — verificación: sin usos afectados y los tests de routing verdes

## 5. Auditoría del toolchain de build y test

- [ ] 5.1 Actualizar `vite` a 8.x, `@vitejs/plugin-react` a 6.x, `vitest` a 5.x, `@vitest/coverage-v8` a 5.x, `happy-dom` a 21.x, `globals` a 17.x y `@types/node` a 26.x — verificación: la instalación del árbol completo resuelve sin conflicto de peers
- [ ] 5.2 Ajustar `vite.config.ts` y `vitest.config.ts` a las APIs de las nuevas versiones (alias, entorno, `testTimeout`, proveedor de cobertura) — verificación: `npm run build` y `npm run test` finalizan en 0
- [ ] 5.3 Revisar `src/test/setup.ts` frente a `happy-dom` 21 (stubs de APIs del navegador ya provistas o faltantes) — verificación: la suite pasa sin stubs redundantes ni errores de API faltante

## 6. Auditoría del stack de estilos (Tailwind 4 / tailwind-merge 3)

- [ ] 6.1 Actualizar `tailwindcss` a 4.x y `tailwind-merge` a 3.x; retirar `tailwindcss-animate` y `autoprefixer` si dejan de ser necesarios — verificación: la instalación resuelve y `cn()` sigue operativa
- [ ] 6.2 Migrar `postcss.config.cjs` al plugin `@tailwindcss/postcss` — verificación: `npm run build` genera el CSS esperado
- [ ] 6.3 Migrar `src/index.css` (`@import "tailwindcss"`) y el `tailwind.config.ts` (vía directiva `@config` o tema en CSS) — verificación: `npm run build` en 0 y los estilos base/tema aplicados
- [ ] 6.4 Verificar regresiones visuales de los defaults de v4 (color de borde, ancho de `ring`, escala de `shadow`, `outline-none`) en componentes de dominio — verificación: revisión de las vistas afectadas y suite DOM verde

## 7. Auditoría de dependencias de runtime y librería de test

- [ ] 7.1 Actualizar Radix UI, `@tanstack/react-query` (+ devtools), `axios`, `react-hook-form` y `recharts` — verificación: la instalación resuelve y la suite queda verde
- [ ] 7.2 Actualizar `lucide-react` a 1.x y auditar iconos renombrados o removidos — verificación: `npm run build` sin imports rotos
- [ ] 7.3 Actualizar `@testing-library/jest-dom` a 7.x, `@testing-library/react`, `@testing-library/dom` y `@testing-library/user-event`, y ajustar `src/test/setup.ts` si cambia el punto de registro de matchers — verificación: los matchers de DOM están disponibles y la suite pasa

## 8. Verificación integral

- [ ] 8.1 `npm ci` limpio (sin flags) en `App/Frontend` — verificación: código de salida 0
- [ ] 8.2 `npm run lint` — verificación: código de salida 0 con las mismas reglas efectivas
- [ ] 8.3 `npm run build` — verificación: código de salida 0 (chequeo de tipos + bundle) y artefacto en `dist/`
- [ ] 8.4 `npm run test` — verificación: suite verde con la misma cobertura funcional que el baseline
- [ ] 8.5 Job `frontend-tests` en `.github/workflows/ci.yml` — verificación: pasa en el pipeline (install + lint + cobertura)
- [ ] 8.6 Ejecutar `openspec validate c-128-migracion-react-19-frontend --strict` — verificación: PASS
