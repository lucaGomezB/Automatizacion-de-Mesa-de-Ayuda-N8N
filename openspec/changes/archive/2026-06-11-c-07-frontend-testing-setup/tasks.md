## 1. Infraestructura y configuración

- [x] 1.1 Agregar a `Frontend/package.json` los `devDependencies` de testing (`vitest` ^2.1, `@vitest/coverage-v8` ^2.1, `@testing-library/react` ^16, `@testing-library/dom` ^10, `@testing-library/jest-dom` ^6, `@testing-library/user-event` ^14, `happy-dom` ^15) y los scripts `"test": "vitest run"`, `"test:watch": "vitest"`, `"test:coverage": "vitest run --coverage"`
- [x] 1.2 Ejecutar `npm install` en `Frontend/` y verificar que no haya conflictos `ERESOLVE`; si el registry ofrece un parche más nuevo dentro de Vitest 2.x, usarlo (no saltar a Vitest 3 sin verificar el peer de Vite 5)
- [x] 1.3 Crear `Frontend/vitest.config.ts` con `defineConfig` de `vitest/config`: `plugins: [react()]`, `resolve.alias` `@ → ./src` (espejo de `vite.config.ts`), `test.environment: 'happy-dom'`, `test.globals: true`, `test.setupFiles: ['./src/test/setup.ts']`, y `test.coverage` con `provider: 'v8'`, `include: ['src/components/**','src/hooks/**','src/services/**']`, `reporter: ['text','html']`
- [x] 1.4 Crear `Frontend/src/test/setup.ts` que importe `@testing-library/jest-dom/vitest`, registre limpieza de RTL entre pruebas, y agregue los stubs de happy-dom que Radix UI pueda necesitar (`Element.prototype.hasPointerCapture`, `scrollIntoView`, `matchMedia` si hace falta)
- [x] 1.5 Habilitar los tipos de Vitest y jest-dom en TypeScript (referencia a `vitest/globals` y `@testing-library/jest-dom` en `tsconfig.json` o vía `/// <reference />` en el setup) y verificar que `npm test` arranca sin errores con cero pruebas
- [x] 1.6 Crear el helper `Frontend/src/test/utils.tsx` con `renderWithClient` (wrapper `QueryClientProvider` que crea un `new QueryClient` por llamada con `queries.retry = false`) reutilizable por las pruebas de hooks y de componentes que usan React Query

## 2. Pruebas de la capa de servicios (Axios mockeado)

- [x] 2.1 `src/services/incidentesService.test.ts`: con Axios/`apiClient` mockeado, verificar que `crearIncidente` hace POST a `/incidentes` con el payload sin alterar y devuelve el body; `listarIncidentes` hace GET a `/incidentes` reenviando `params`; `obtenerIncidente(id)` hace GET a `/incidentes/{id}`; `verificarSaludApi` hace GET a `/health`
- [x] 2.2 `src/services/clasificacionesService.test.ts`: verificar `listarRevisionPendiente` (GET `/clasificaciones/revision-pendiente` con params), `listarClasificacionesPorIncidente(id)` (GET `/clasificaciones/incidente/{id}`) y `validarClasificacion(logId, payload)` (PATCH `/clasificaciones/{logId}/validar` con el payload)
- [x] 2.3 `src/services/api.test.ts`: cubrir `extractApiErrorMessage` con cada forma de error — `detail` string, `detail` array Pydantic (concatena `msg`), `error.message` propio del backend, códigos 404/422/500/503, `code: 'ECONNABORTED'` (timeout), error sin `response` (red), error no-Axios (mensaje genérico). Usar objetos con forma de AxiosError reconocibles por `axios.isAxiosError`

## 3. Pruebas de hooks (servicios mockeados + QueryClient aislado)

- [x] 3.1 `src/hooks/useReportarIncidente.test.ts`: con `crearIncidente` mockeado (`vi.mock('@/services/incidentesService')`), montar con `renderWithClient`, ejecutar `mutate` con un payload y aseverar que el servicio recibió ese payload y que `data` expone el `IncidenteRead` resuelto (usar `waitFor`)
- [x] 3.2 `src/hooks/useIncidentes.test.ts`: con `listarIncidentes` mockeado, montar con parámetros de filtro y aseverar que el servicio fue llamado con esos params y que `data` expone la lista; un segundo caso con params distintos confirma que la query key varía
- [x] 3.3 `src/hooks/useRevisionPendiente.test.ts`: con `listarRevisionPendiente` mockeado, aseverar invocación del servicio y exposición de la lista de clasificaciones pendientes

## 4. Pruebas de indicadores compartidos

- [x] 4.1 `src/components/shared/ConfianzaIndicator.test.tsx`: confianza < 0.70 muestra "Revisar" y el porcentaje; confianza == 0.70 y > 0.70 NO muestran "Revisar" (caso límite explícito); verificar el porcentaje formateado de al menos dos valores distintos
- [x] 4.2 `src/components/shared/SectorBadge.test.tsx`: con un nombre de sector válido muestra ese nombre; con `null` y con `undefined` muestra "Pendiente"

## 5. Pruebas del formulario de reporte y la tarjeta de éxito

- [x] 5.1 `src/pages/ReportarIncidente/IncidenteForm.test.tsx` — validación: completar nombre y una descripción de menos de 15 palabras, enviar, y aseverar que aparece el mensaje de mínimo de palabras y que la mutación (`useReportarIncidente` mockeado) NO se invocó
- [x] 5.2 `IncidenteForm.test.tsx` — payload: completar datos válidos (descripción ≥ 15 palabras) y enviar; aseverar que la mutación se invocó con un payload que incluye `canal_origen_id: 2` y que NO incluye `nombre_usuario` ni `sector_usuario` (verificar sobre el argumento del mock; tomar la rama por defecto de prioridad para no depender de abrir el Radix Select)
- [x] 5.3 `src/pages/ReportarIncidente/SuccessCard.test.tsx`: renderizar con `renderWithClient` y `listarClasificacionesPorIncidente` mockeado; aseverar nº de ticket y badge del sector; un segundo caso con `requiere_revision_humana: true` muestra la nota de revisión manual

## 6. Pruebas de las tablas de administración

- [x] 6.1 `src/pages/Administracion/TicketsTable.test.tsx`: estado `isLoading` muestra el spinner; estado `isError` muestra el mensaje (vía `extractApiErrorMessage`) y el reintento invoca `onRefetch`; lista vacía muestra `EmptyState`; con datos renderiza una fila por incidente y el clic en una fila invoca `onSelectIncidente` con el id correcto
- [x] 6.2 `src/pages/Administracion/RevisionHumanaTable.test.tsx`: estados carga/error/vacío análogos; con datos, una clasificación sin validar muestra el botón "Validar" que invoca `onValidar` con esa clasificación, y una ya validada muestra el indicador de validada en lugar del botón

## 7. Cobertura y cierre

- [x] 7.1 Ejecutar `npm run test:coverage` y confirmar cobertura de líneas > 70% en `src/components/`, `src/hooks/` y `src/services/`; si los primitivos shadcn/layout hunden el número, acotar `coverage.include`/`exclude` al código de dominio y documentarlo
- [x] 7.2 Si alguna prueba revela que happy-dom no soporta una API requerida por Radix UI, agregar el stub correspondiente en `src/test/setup.ts` o, como último recurso, cambiar `environment` a `jsdom`
- [x] 7.3 Verificar que toda la suite pasa con `npm test`, que no quedan pruebas con `.only`/`.skip` y que las aserciones son significativas (no tautológicas)
- [x] 7.4 Si alguna prueba falla por un bug genuino del código de aplicación (no por una aserción mal escrita), NO modificar producción: reportarlo como hallazgo para decidir su corrección por separado
