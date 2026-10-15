## 1. Backend — Conteo de la cola acotado por alcance (VIS-006)

- [x] 1.1 Agregar el schema Pydantic v2 `RevisionPendienteCount` (`total: int`) en `App/Backend/app/schemas/clasificacion.py` y verificar que importa sin errores (`cd App/Backend; python -c "from app.schemas.clasificacion import RevisionPendienteCount"`)
- [x] 1.2 RED: escribir test de repositorio para `count_pending_review` en `App/Backend/tests/` (cuenta solo `requiere_revision_humana == true` y `sector_id_validado IS NULL`; excluye validadas y de alta confianza; respeta el filtro por reportante) y confirmar que falla porque el método no existe
- [x] 1.3 GREEN: implementar `ClasificacionRepository.count_pending_review(reportante_empleado_id)` con `func.count()` y los `where` idénticos a `list_pending_review` en `App/Backend/app/repositories/clasificacion_repository.py`; ejecutar el test de 1.2 y confirmar que pasa (`cd App/Backend; pytest tests/ -k count_pending`)
- [x] 1.4 TRIANGULAR (repositorio): agregar casos con mezcla de filas (validadas, alta confianza, otro reportante, alcance global) y confirmar que el conteo coincide con `len(list_pending_review sin paginar)`
- [x] 1.5 RED: escribir test de servicio para `count_pending_review(alcance)` (GLOBAL → total; PROPIO → solo del reportante; VACIO → 0 sin tocar el repositorio) y confirmar que falla
- [x] 1.6 GREEN: extraer el helper de derivación de alcance (`_reportante_filtro`) y reutilizarlo en `list_pending_review` y en `count_pending_review` en `App/Backend/app/services/clasificacion_service.py`; ejecutar los tests de servicio y confirmar que pasan
- [x] 1.7 TRIANGULAR (servicio): verificar que `list_pending_review` conserva su comportamiento tras la extracción del helper (suite existente de clasificaciones verde: `cd App/Backend; pytest tests/ -k "clasificacion or revision"`)
- [x] 1.8 RED: escribir test de API (SQLite, `make_client_with_classifier`) para `GET /api/v1/clasificaciones/revision-pendiente/count` (200 con `{"total": N}`; total coincide con el listado sin paginar; 401 sin autenticación) y confirmar que falla con 404
- [x] 1.9 GREEN: agregar el endpoint `GET /clasificaciones/revision-pendiente/count` con `response_model=RevisionPendienteCount` en `App/Backend/app/routes/clasificaciones.py`, delegando en el servicio y aplicando `AlcanceDep`; ejecutar el test de 1.8 y confirmar que pasa
- [x] 1.10 TRIANGULAR (API): agregar casos por rol (admin/mesa → total global; `usuario_final` → solo propios; cuenta sin empleado → 0) y confirmar el total real con más de 50 pendientes (no topeado)
- [x] 1.11 Agregar un test de integración PostgreSQL (`@pytest.mark.integration`) que compare el total del conteo con `len(listado sin paginar)` para el mismo alcance, y verificar con `cd App/Backend; pytest -m integration -k revision`
- [x] 1.12 Regenerar `docs/openapi.json` y verificar la sincronización (`cd App/Backend; pytest tests/test_openapi_sync.py -v`)

## 2. Frontend — Conteo y badge con el total real (FRH-008)

- [x] 2.1 Agregar el tipo de respuesta del conteo (`RevisionPendienteCount { total: number }`) en `App/Frontend/src/types/clasificacion.ts` y verificar el typecheck (`cd App/Frontend; npx tsc --noEmit`)
- [x] 2.2 RED: escribir test de `contarRevisionPendiente()` en `App/Frontend/src/services/` (mock de Axios: llama a `/clasificaciones/revision-pendiente/count` y retorna `data.total`) y confirmar que falla
- [x] 2.3 GREEN: implementar `contarRevisionPendiente(): Promise<number>` en `App/Frontend/src/services/clasificacionesService.ts`; ejecutar el test de 2.2 y confirmar que pasa
- [x] 2.4 RED: escribir test del hook `useRevisionPendienteCount()` (retorna el total; `queryKey` prefijada por `REVISION_PENDIENTE_QUERY_KEY` para que la invalidación existente del diálogo lo alcance) y confirmar que falla
- [x] 2.5 GREEN: implementar `useRevisionPendienteCount()` en `App/Frontend/src/hooks/useRevisionPendiente.ts` (`queryKey: [REVISION_PENDIENTE_QUERY_KEY, 'count']`, misma política de refresco); confirmar que el test de 2.4 pasa
- [x] 2.6 RED: escribir test de la pestaña (Vitest + Testing Library) que afirme que el badge muestra el total del conteo cuando supera 50 y que se oculta cuando el total es 0; confirmar que falla
- [x] 2.7 GREEN: reemplazar `totalPendientes = clasificacionesPendientes?.length` por el total del hook de conteo en `App/Frontend/src/pages/Administracion/index.tsx`; confirmar que el test de 2.6 pasa y que el resto de la suite sigue verde
- [x] 2.8 TRIANGULAR: agregar casos de alcance en el test de la pestaña (total PROPIO menor que el global; total 0 sin badge) y confirmar que pasan

## 3. Frontend — Paginación de la tabla de revisión (FRH-009)

- [x] 3.1 RED: escribir/ampliar test de la pestaña que afirme que la consulta de la cola usa `limit=PAGE_SIZE` y `offset=pagina * PAGE_SIZE`, y que al accionar "Siguiente" cambia el offset; confirmar que falla
- [x] 3.2 GREEN: agregar el estado `paginaRevision` y pasar `{ limit: PAGE_SIZE, offset: paginaRevision * PAGE_SIZE }` a `useRevisionPendiente` en `App/Frontend/src/pages/Administracion/index.tsx`; confirmar que el test de 3.1 pasa
- [x] 3.3 RED: escribir test del componente `Paginacion` extendido (con `total` provisto: `haySiguiente = (pagina + 1) * pageSize < total`; sin `total`: conserva la heurística `totalEnPagina === pageSize`); confirmar que falla
- [x] 3.4 GREEN: agregar el prop opcional `total?: number` a `Paginacion` en `App/Frontend/src/pages/Administracion/index.tsx` y renderizarlo bajo la tabla de revisión alimentado por el total del conteo; confirmar que el test de 3.3 pasa
- [x] 3.5 TRIANGULAR: agregar caso "validar la última fila de la última página retrocede a una página con resultados o muestra cola vacía" y confirmar que pasa (reset de offset cuando la página queda fuera de rango tras el refetch)
- [x] 3.6 Verificar que la pestaña de tickets conserva su comportamiento de paginación (suite existente de `Administracion` verde: `cd App/Frontend; npm run test -- Administracion`)

## 4. Frontend — Corrección del aviso ámbar (FRH-010)

- [x] 4.1 RED: escribir/ampliar test de la pestaña que afirme que el aviso NO contiene "Gemini 2.5 Flash" ni ningún nombre de modelo, y que comunica el umbral del 70%; confirmar que falla
- [x] 4.2 GREEN: reemplazar el texto del aviso en `App/Frontend/src/pages/Administracion/index.tsx` por "Estos incidentes fueron clasificados con una confianza inferior al 70%, umbral de revisión humana del clasificador. Revisá y confirmá el sector correcto para cada uno."; confirmar que el test de 4.1 pasa
- [x] 4.3 Corregir el comentario/docstring del hook y de la tabla que atribuye el umbral a `parameters_gemini.md`, dejándolo agnóstico y coherente con el aviso (`App/Frontend/src/hooks/useRevisionPendiente.ts`, `App/Frontend/src/pages/Administracion/RevisionHumanaTable.tsx`) y confirmar que lint pasa (`cd App/Frontend; npm run lint`)

## 5. Verificación integral

- [x] 5.1 Ejecutar la suite backend offline y confirmar verde (`cd App/Backend; pytest -m "not integration"`)
- [x] 5.2 Ejecutar lint backend y confirmar verde (`cd App/Backend; ruff check .`)
- [x] 5.3 Ejecutar la suite frontend con coverage y confirmar verde (`cd App/Frontend; npm run test:coverage`)
- [x] 5.4 Ejecutar lint frontend y typecheck y confirmar verdes (`cd App/Frontend; npm run lint && npm run build`)
- [x] 5.5 Confirmar visualmente/manualmente que con >50 pendientes el badge muestra el total real y que la tabla permite navegar más allá de la primera página (revisar el render del panel de administración)
