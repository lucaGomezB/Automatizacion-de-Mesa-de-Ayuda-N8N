# Tasks: Migración del frontend a React 19 y react-router 7 (alcance reducido)

## 1. Baseline y preparación

- [x] 1.1 Registrar el baseline verde en `App/Frontend` (`npm ci`, `npm run lint`, `npm run build`, `npm run test`) — verificación: los cuatro comandos finalizan en 0
- [x] 1.2 Auditoría de código fuente previa a la migración: confirmar 0 ocurrencias de APIs legadas de React 19 (`ReactDOM.render`/`hydrate`, `findDOMNode`, `createFactory`, contexto legacy, refs string, `defaultProps`/`propTypes` en funciones, `React.FC`, `children` implícito, namespace `JSX`) y que todo `useRef` pasa argumento — verificación: informe que lista archivos y puntos de contacto

## 2. React 19 (tipos y runtime)

- [x] 2.1 Actualizar `react`, `react-dom` a 19.x y `@types/react`, `@types/react-dom` a 19.x en `App/Frontend/package.json` — verificación: la instalación resuelve sin conflicto de peers
- [x] 2.2 Confirmar que React 19 no exige cambios de runtime (auditoría de 1.2) — verificación: `npm run test` verde
- [x] 2.3 Migrar las 13 ocurrencias de `React.ElementRef` → `React.ComponentRef` en `src/components/ui/` (dialog.tsx 4, select.tsx 7, separator.tsx 1, label.tsx 1) — verificación: `npm run build` (tsc) sin errores de tipos

## 3. react-router 7 (retiro del prop `future`)

- [x] 3.1 Actualizar `react-router-dom` a 7.x en `App/Frontend/package.json` — verificación: los imports existentes (`BrowserRouter`, `Routes`, `Route`, `Navigate`, `NavLink`, `Link`, `useNavigate`) resuelven sin cambios
- [x] 3.2 Retirar el prop `future` de `<BrowserRouter>` en `src/main.tsx:116` — verificación: `npm run build` sin error de tipos y los tests de enrutado verdes

## 4. Node 20 → 24

- [x] 4.1 Bump de `node:20-alpine` → `node:24-alpine` en `App/Frontend/Dockerfile` — verificación: el stage de build usa Node 24
- [x] 4.2 Bump de `node-version: "20"` → `"24"` y del nombre/comentario del job ("Node 20" → "Node 24") en `.github/workflows/ci.yml` (jobs `frontend-tests` y `security-scan`) — verificación: ambos jobs declaran Node 24

## 5. Sincronización de documentación y versión

- [x] 5.1 `openspec/config.yaml:26` — `framework: React 18 + TypeScript + Vite` → React 19 — verificación: el stack declarado dice React 19
- [x] 5.2 `knowledge-base/02_descripcion_general.md:15` y `knowledge-base/08_arquitectura_propuesta.md:35` — React 18 → React 19 — verificación: la KB declara React 19
- [x] 5.3 `docs/Tesis/v10 (IA)/paper/sections/06-implementacion.tex:87` — "React 18" → "React 19" — verificación: la fuente LaTeX declara React 19
- [x] 5.4 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con su build script (`python "docs/Tesis/v10 (IA)/build_tesis_para_agente.py" > "docs/Tesis/v10 (IA)/tesis_para_agente.md"` desde la raíz) — verificación: el md regenerado refleja la fuente y corrige el drift del tag de jurado (queda `v1.1.1`, alineado con `12-anexos.tex:19`)
- [x] 5.5 `docs/diagrams/despliegue.md:17` — "Frontend React 18 + Vite" → React 19 — verificación: el diagrama declara React 19
- [x] 5.6 `AGENTS.md:52` — "React 18 + TypeScript + Vite" → React 19 — verificación: AGENTS.md declara React 19
- [x] 5.7 NO tocar `docs/Tesis/v8`, `docs/Tesis/v9` (históricos) ni `openspec/changes/archive/**` — verificación: `git status` no muestra cambios en esas rutas
- [x] 5.8 NO editar `CHANGES.md` (reescrito por el PR #40 abierto) — verificación: queda registrado como follow-up en la propuesta

## 6. Verificación integral

- [x] 6.1 `npm ci` limpio (sin flags) en `App/Frontend` — verificación: código de salida 0
- [x] 6.2 `npm run lint` — verificación: código de salida 0 con las mismas reglas efectivas
- [x] 6.3 `npm run build` — verificación: código de salida 0 (chequeo de tipos + bundle) y artefacto en `dist/`
- [x] 6.4 `npm run test` — verificación: suite verde con la misma cobertura funcional que el baseline
- [x] 6.5 `openspec validate c-128-migracion-react-19-frontend --strict` — verificación: PASS