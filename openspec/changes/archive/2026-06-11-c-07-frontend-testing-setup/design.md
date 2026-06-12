## Context

El frontend (`Frontend/`) es una SPA React 18 + TypeScript estricto, empaquetada con Vite 5.4, con Tailwind, shadcn/ui (escrito a mano, sin CLI), React Query v5, React Router v6, React Hook Form y Axios. Hoy `Frontend/package.json` define solo `dev`, `build` (`tsc && vite build`) y `preview`: no hay runner de pruebas ni script `test`, y `node_modules` no contiene Vitest ni Testing Library. El contrato que las pruebas deben proteger ya está implementado y verificado contra el código actual:

- `IncidenteForm` arma el payload del POST con `canal_origen_id = CANAL_ORIGEN_IDS.FORMULARIO_WEB` (= 2, de `src/types/catalog.ts`) y `descripcion.trim()`; `nombre_usuario` y `sector_usuario` son campos de UX que **no** se envían. La validación de cliente exige ≥ 15 palabras (`validarMinimoPalabras`, `src/utils/validators.ts`).
- `ConfianzaIndicator` (`src/components/shared/`) define `UMBRAL_REVISION = 0.70` y muestra la etiqueta "Revisar" cuando `confianza < 0.70` (estricto: 0.70 NO pide revisión).
- `SectorBadge` mapea `Sistemas`/`Operaciones`/`Soporte Técnico` a variantes de color y muestra "Pendiente" si `nombre` es nulo/indefinido.
- Las tablas (`TicketsTable`, `RevisionHumanaTable`, ambas en `src/pages/Administracion/`) son presentacionales: reciben `incidentes`/`clasificaciones`, `isLoading`, `isError`, `error`, y callbacks (`onSelectIncidente`/`onValidar`, `onRefetch`). Manejan carga → `LoadingSpinner`, error → `ErrorAlert` (mensaje vía `extractApiErrorMessage`), vacío → `EmptyState`, datos → tabla.
- `SuccessCard` (`src/pages/ReportarIncidente/`) hace un `useQuery` a `listarClasificacionesPorIncidente` con `staleTime: Infinity` para mostrar la confianza, además del nº de ticket y el sector.
- Servicios (`src/services/`): `api.ts` (instancia Axios con `baseURL` `${VITE_API_BASE_URL ?? localhost:8000}/api/v1`, timeout 20s, y `extractApiErrorMessage`), `incidentesService.ts`, `clasificacionesService.ts`.

C-07 es de gobernanza BAJO y aditivo: no toca el código de aplicación, solo suma config de test, scripts y la suite. Strict TDD está activo a nivel proyecto, pero C-07 ES la introducción de la capa de pruebas: el "código de producción" que ya existe es el frontend; el RED/GREEN aplica al escribir cada test contra el comportamiento ya implementado (las pruebas codifican el contrato y deben pasar contra el código actual; cualquier test que falle revela una deriva real, no se "arregla" cambiando producción salvo que sea un bug genuino, que se reporta).

## Goals / Non-Goals

**Goals:**
- Instalar y configurar un runner de pruebas (Vitest) integrado con la config de Vite existente, con entorno DOM, alias `@/` y matchers de jest-dom.
- Cubrir las tres capas del frontend (servicios, hooks, componentes) con pruebas que verifiquen el **comportamiento observable**, no detalles de implementación.
- Superar el 70% de cobertura de líneas en `src/components/`, `src/hooks/` y `src/services/`.
- Codificar como aserciones los hechos de contrato (payload `canal_origen_id=2` sin `nombre_usuario`/`sector_usuario`, umbral 0.70, mapeo de errores) para que cualquier regresión quiebre la suite.

**Non-Goals:**
- No se configura el wiring de CI (GitHub Actions) — queda para un change posterior, aunque la suite quede lista para correr en CI.
- No se escriben pruebas E2E ni de integración real contra el backend (eso es la cima de la pirámide, fuera de alcance del frontend unitario).
- No se modifica el código de aplicación del frontend (componentes, hooks, servicios) salvo que una prueba revele un bug genuino, que se reportaría.
- No se prueban exhaustivamente los primitivos de `src/components/ui/` (shadcn) ni `src/components/layout/`; el objetivo de cobertura se mide sobre `components/` en conjunto y se alcanza cubriendo los componentes de dominio (`shared/`, páginas), que es donde vive la lógica.
- No se cubren `src/utils/` ni `src/types/` como objetivo formal (aunque `validators`/`formatters` quedan ejercitados indirectamente y pueden tener pruebas propias por bajo costo).

## Decisions

### Decisión 1: Vitest sobre Jest

**Elección:** Vitest como runner. **Por qué:** el proyecto ya usa Vite 5.4; Vitest reutiliza la misma config (plugins, alias, transform de TS/JSX vía esbuild) sin un pipeline de transformación paralelo como el que exigiría Jest (ts-jest/babel-jest + mapeo manual de `@/`). Es el runner recomendado por el ecosistema Vite y el indicado explícitamente en el scope de C-07. **Alternativa descartada:** Jest — funcionaría, pero duplicaría configuración (transformers, moduleNameMapper, ESM) y diverge de la toolchain Vite del repo.

### Decisión 2: `happy-dom` como entorno DOM

**Elección:** `happy-dom` (indicado en el scope). **Por qué:** más liviano y rápido que jsdom para suites de componentes, suficiente para Testing Library (queries por rol/texto, eventos). **Alternativa:** jsdom — más completo en APIs de navegador exóticas, pero más pesado; ninguna prueba del alcance lo requiere. Si en el apply surge una API faltante en happy-dom, migrar a jsdom es un cambio de una línea en `environment`.

### Decisión 3: Versiones — Vitest 2.1.x compatible con Vite 5.4 / React 18

**Elección (objetivo, a fijar exacto en apply):**
- `vitest` `^2.1.0` y `@vitest/coverage-v8` `^2.1.0` — la línea 2.x es la estable que declara peer `vite@^5` (la 3.x es más nueva y no se justifica para Vite 5.4; mantener mismo major que el resto del tooling reduce riesgo).
- `@testing-library/react` `^16.x` — soporta React 18; requiere `@testing-library/dom` como peer explícito.
- `@testing-library/dom` `^10.x` — peer de RTL 16.
- `@testing-library/jest-dom` `^6.x`.
- `@testing-library/user-event` `^14.x` — para interacciones (clic en filas, submit del form) con semántica realista.
- `happy-dom` `^15.x`.

**Por qué:** alinear el major de Vitest con Vite 5 evita conflictos de peer dependencies (la causa de fricción más común al instalar Vitest). RTL 16 separó `@testing-library/dom` como peer, por eso se instala explícito. **En apply:** correr `npm install` y verificar que no haya `ERESOLVE`; si el registry ofrece una 2.x más reciente, usar el último parche de 2.x. No saltar a Vitest 3 sin verificar el peer de Vite.

### Decisión 4: `vitest.config.ts` separado, importando el alias de Vite

**Elección:** archivo `Frontend/vitest.config.ts` propio (no fundir en `vite.config.ts`) que use `defineConfig` de `vitest/config`, con `plugins: [react()]`, `resolve.alias` con `@ → ./src` (idéntico a `vite.config.ts`), y bloque `test`:
- `environment: 'happy-dom'`
- `globals: true` (para que `describe/it/expect` y los matchers de jest-dom estén disponibles sin importar en cada archivo; requiere `"types": ["vitest/globals", "@testing-library/jest-dom"]` o equivalente — ver Decisión 6)
- `setupFiles: ['./src/test/setup.ts']`
- `coverage: { provider: 'v8', include: ['src/components/**', 'src/hooks/**', 'src/services/**'], reporter: ['text', 'html'] }`

**Por qué un archivo separado:** mantiene la config de build limpia y evita que las opciones de test contaminen `vite build`. El alias se duplica (3 líneas) en lugar de extraer un módulo compartido, por simplicidad (KISS) — la fuente de verdad sigue siendo `vite.config.ts` y design documenta que deben mantenerse en espejo. **Alternativa:** un único `vite.config.ts` con `/// <reference types="vitest" />` y bloque `test` — válida, pero mezcla responsabilidades; se prefiere separar.

### Decisión 5: Mock de Axios en el límite de red

**Elección:** en las pruebas de servicios, mockear el módulo Axios / la instancia `apiClient` con `vi.mock`, verificando ruta + método + payload sin red. Para `extractApiErrorMessage`, construir errores de Axios sintéticos (usar `axios.isAxiosError` real con objetos que tengan la forma `{ isAxiosError: true, response?, code? }`) y aseverar el string devuelto. En las pruebas de hooks, mockear la **capa de servicios** (`vi.mock('@/services/...')`), no Axios, para aislar el hook de la red y del cliente HTTP. **Por qué dos niveles:** los servicios son el punto donde se toca Axios → se mockea ahí; los hooks dependen de los servicios → se mockean los servicios, manteniendo cada prueba en su frontera natural. **Alternativa descartada:** MSW (Mock Service Worker) — interceptor de red más realista, pero agrega una dependencia y setup de servidor que excede el alcance unitario de C-07.

### Decisión 6: `QueryClient` fresco por prueba + wrapper de render

**Elección:** un helper de test (`renderWithClient` o un `wrapper` con `QueryClientProvider`) que cree un `new QueryClient` por prueba con `defaultOptions.queries.retry = false` (para que los errores se propaguen de inmediato sin reintentos que ralenticen la suite) y `gcTime`/`staleTime` que no interfieran. **Por qué:** React Query cachea por `QueryClient`; compartir uno entre pruebas filtraría estado. `retry: false` es clave para que las pruebas de error de hooks no esperen reintentos. Los componentes que usan `useQuery` internamente (`SuccessCard`) se renderizan con el mismo wrapper.

### Decisión 7: Ubicación de los archivos de prueba — colocados (co-located)

**Elección:** cada `*.test.ts(x)` junto a su unidad (`src/services/api.test.ts`, `src/components/shared/ConfianzaIndicator.test.tsx`, etc.), más `src/test/setup.ts` para el setup global. **Por qué:** descubrimiento trivial por Vitest, cercanía al código que prueban, convención dominante en proyectos Vite/RTL. **Alternativa:** carpeta `tests/` espejo — añade navegación sin beneficio aquí.

### Decisión 8: Estrategia de aserción Testing-Library-first

**Elección:** consultar por rol accesible, etiqueta (`getByLabelText`), placeholder o texto visible; interactuar con `user-event`; aseverar sobre lo que el usuario ve. Para verificar el payload del form se aserta sobre el mock de la mutación/servicio (qué argumentos recibió), no sobre estado interno del componente. **Por qué:** las pruebas resisten refactors internos y documentan el contrato de usuario. Para `SectorBadge`/`ConfianzaIndicator` se asevera sobre texto ("Revisar", "Pendiente", el porcentaje) en lugar de clases CSS, que son detalle de presentación.

## Risks / Trade-offs

- **[Conflictos de peer dependencies al instalar Vitest/RTL]** → Mitigación: fijar el major de Vitest al compatible con Vite 5 (2.x), instalar `@testing-library/dom` explícito (peer de RTL 16), y verificar `npm install` sin `ERESOLVE` en el apply antes de escribir tests.
- **[happy-dom carece de alguna API de navegador]** (p. ej. `IntersectionObserver`, `matchMedia`, APIs de Radix UI usadas por shadcn `Select`/`Dialog`) → Mitigación: agregar stubs puntuales en `src/test/setup.ts`; si la carencia es estructural, cambiar `environment` a `jsdom` (cambio de una línea). Radix `Select` en particular puede requerir polyfills (`hasPointerCapture`, `scrollIntoView`) en el setup.
- **[Cobertura por debajo del 70% por contar `components/ui/` y `layout/`]** → Mitigación: el `coverage.include` apunta a `src/components/**`, `src/hooks/**`, `src/services/**`; si los primitivos shadcn no cubiertos hunden el número, acotar `include`/`exclude` para enfocar en el código de dominio (objetivo real del scope), documentándolo.
- **[Probar Radix `Select` en `IncidenteForm` es frágil]** (el dropdown se teletransporta y depende de pointer events) → Mitigación: para el caso del payload, el camino mínimo es verificar la rama por defecto (`prioridad: 'media'`, sector default) sin abrir el `Select`, o disparar el submit directamente; reservar la interacción con el `Select` solo si aporta cobertura necesaria.
- **[Strict TDD vs. código ya existente]** → las pruebas se escriben contra comportamiento ya implementado; el ciclo RED se cumple porque el test referencia aserciones que aún no existen y debe pasar (GREEN) contra el código actual. Un test que no pase y no sea un bug genuino indica una aserción mal escrita, no autoriza tocar producción.
- **[Deriva del contrato]** (memoria del proyecto pudo desactualizarse) → Mitigación ya aplicada: los hechos (payload `canal_origen_id=2` sin campos UX, umbral 0.70 estricto, `IncidenteListItem` sin `descripcion`) se verificaron leyendo el código actual durante el propose; coinciden con la memoria. No hay deriva detectada.

## Migration Plan

C-07 es aditivo y sin estado: no hay migración de datos ni rollback complejo. Pasos de despliegue:
1. Agregar devDependencies y scripts a `Frontend/package.json`; `npm install`.
2. Crear `vitest.config.ts` y `src/test/setup.ts`; verificar que `npm test` arranca en vacío.
3. Escribir la suite capa por capa (servicios → hooks → componentes), corriendo `npm test` tras cada unidad.
4. Generar cobertura (`npm run test:coverage`) y confirmar > 70% en las tres capas.

Rollback: revertir la edición de `package.json` y borrar los archivos de test/config — no afecta build ni runtime.

## Open Questions

- Ninguna que bloquee el apply. La única decisión que puede requerir ajuste empírico es si Radix UI (shadcn `Select`/`Dialog`) obliga a migrar de `happy-dom` a `jsdom`; se resuelve durante la implementación sin necesidad de input del usuario (gobernanza BAJO).
