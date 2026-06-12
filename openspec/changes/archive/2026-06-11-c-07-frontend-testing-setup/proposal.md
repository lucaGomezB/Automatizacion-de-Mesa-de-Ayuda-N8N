## Why

El frontend React (`Frontend/`) es la cara visible del sistema —el formulario de reporte del usuario final (`/`) y el panel del operador (`/admin`)— y hoy **no tiene ninguna prueba automatizada**: `Frontend/package.json` ni siquiera declara un runner de tests ni el script `test`. El §6.5 de la tesis describe una pirámide de pruebas (Crispin y Gregory, 2009) y reporta 87% de cobertura en el módulo Python, pero la base de esa pirámide para la capa de presentación está vacía: cualquier regresión en la lógica de UI (umbral de confianza, payload del POST, manejo de errores de API, estados de carga/vacío/error de las tablas) pasaría desapercibida. C-07 instala la infraestructura de testing del frontend y escribe la suite que verifica el comportamiento de componentes, hooks y servicios, cerrando esa brecha y dejando la cobertura de la capa cliente auditable como la del backend.

Restricción central verificada contra el código actual: el contrato del frontend que las pruebas deben proteger ya está implementado y es estable —el formulario fija `canal_origen_id = 2` (`CANAL_ORIGEN_IDS.FORMULARIO_WEB`) y NO envía `nombre_usuario`/`sector_usuario` a la API; el umbral de revisión humana `0.70` está hardcodeado en `ConfianzaIndicator.tsx`; `IncidenteListItem` no incluye `descripcion`. Las pruebas codifican estos hechos como aserciones para que cualquier deriva futura quiebre la suite, no la producción.

## What Changes

- **Infraestructura de testing** en `Frontend/`: se agregan Vitest + `@testing-library/react` + `@testing-library/jest-dom` + `happy-dom` como `devDependencies`, sin tocar las dependencias de runtime. No es BREAKING: el build (`tsc && vite build`) y el `dev` server no cambian.
- **Configuración** (`Frontend/vitest.config.ts`): entorno `happy-dom`, alias `@/` espejando `vite.config.ts`, archivo de setup que registra los matchers de `@testing-library/jest-dom`, y reporte de cobertura con el proveedor `v8`.
- **Script `test`** (y `test:coverage`) en `Frontend/package.json`.
- **Tests de servicios** (`api.ts`, `incidentesService.ts`, `clasificacionesService.ts`): Axios mockeado en el límite de red (`vi.mock`); verifican rutas, métodos, payloads y el mapeo de errores de `extractApiErrorMessage` (detail string, array Pydantic, formato `error.message`, 404/422/500/503, timeout `ECONNABORTED`, error de red sin response).
- **Tests de hooks** (`useReportarIncidente`, `useIncidentes`, `useRevisionPendiente`): renderizados con un `QueryClient` fresco por test, servicio mockeado; verifican que cada hook invoca el servicio con los parámetros correctos y expone `data`/`error` esperados.
- **Tests de componentes** (`IncidenteForm`, `SuccessCard`, `TicketsTable`, `RevisionHumanaTable`, `SectorBadge`, `ConfianzaIndicator`): consultas por rol/etiqueta/texto accesible (no por detalles de implementación); verifican el contrato visible —validación de mínimo de palabras, payload con `canal_origen_id = 2`, semáforo y etiqueta "Revisar" del umbral 0.70, variantes de `SectorBadge`, y los estados carga/error/vacío/datos de las tablas.
- **Objetivo de cobertura**: > 70% de líneas en `src/components/`, `src/hooks/` y `src/services/`, medido con `vitest --coverage`.

No hay cambios BREAKING ni modificación del código de aplicación del frontend: C-07 es **aditivo** (config de test + suite). Solo se edita `package.json` para sumar devDependencies y scripts.

## Capabilities

### New Capabilities
- `frontend-testing`: define el contrato de la infraestructura de pruebas del frontend (runner Vitest, entorno DOM, alias, cobertura) y los comportamientos observables que la suite verifica en las tres capas de la UI —servicios (acceso HTTP y normalización de errores), hooks (integración con React Query) y componentes (formulario de reporte, tarjeta de éxito, tablas de administración e indicadores compartidos)—, incluyendo el umbral mínimo de cobertura del 70%.

### Modified Capabilities
<!-- Ninguna. C-07 es aditivo: no modifica requisitos de capacidades existentes
     (data-pseudonymization, evaluation-framework, foundation-environment,
     n8n-notification, n8n-workflow). Las capacidades de backend/datos/N8N no
     tienen un spec del frontend que C-07 deba alterar. -->

## Impact

- **Código nuevo**: `Frontend/vitest.config.ts`, `Frontend/src/test/setup.ts` (registro de matchers jest-dom), y archivos `*.test.tsx` / `*.test.ts` colocados junto a cada unidad bajo prueba en `src/services/`, `src/hooks/`, `src/components/shared/`, `src/pages/ReportarIncidente/` y `src/pages/Administracion/`.
- **Edición mínima**: `Frontend/package.json` (devDependencies de testing + scripts `test`, `test:coverage`). Sin cambios en `dependencies` ni en el código de aplicación.
- **Dependencias nuevas** (solo dev, no runtime): `vitest`, `@vitest/coverage-v8`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `happy-dom` — fijadas a versiones compatibles con Vite 5 / React 18 (Vitest 2.x). La selección exacta de versiones se documenta en design.md.
- **Sin impacto en el backend**: la suite mockea Axios; no levanta el servidor FastAPI ni la base de datos. No afecta la suite de pruebas Python del backend.
- **CI**: habilita ejecutar la suite del frontend en GitHub Actions (§6.5), aunque el wiring de CI no es parte de C-07.
- **Tesis**: la base de la pirámide de pruebas (§6.5) queda cubierta también para la capa de presentación, con cobertura medible y reproducible por comando.
