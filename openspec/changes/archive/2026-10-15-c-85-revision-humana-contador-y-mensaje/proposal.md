## Why

La pestaña "Revisión Humana" del Panel de Administración comunica un estado incorrecto en dos frentes. (1) El badge de la pestaña se calcula como `clasificacionesPendientes.length` sobre una consulta que, sin parámetros de paginación, el backend acota a un máximo de 50 filas (`limit: int = Query(50, ...)` en `GET /api/v1/clasificaciones/revision-pendiente`): con 50 o más pendientes el contador queda congelado en 50 y la tabla solo expone las primeras 50 filas, en contradicción con el comentario del código que declara que "el contador debe reflejar el total". (2) El aviso ámbar de la pestaña afirma que el umbral fue "definido en la especificación Gemini 2.5 Flash", un modelo que ya no está disponible para cuentas nuevas y fue reemplazado por Gemini 3.6 Flash (`settings.gemini_model = "gemini-3.6-flash"`; `settings.human_review_threshold = 0.70`). Ambos defectos erosionan la confianza del operador en la cola de revisión y, al ser parte de la evidencia de la tesis, deben corregirse.

## What Changes

- El contador de la pestaña "Revisión Humana" pasa a reflejar el TOTAL REAL de clasificaciones pendientes del alcance del usuario, sin tope de 50. Mecanismo: un endpoint de conteo liviano y aditivo en el backend que reutiliza la misma lógica de alcance de la cola; el badge consume ese total.
- La tabla de revisión deja de truncarse silenciosamente: la cola se pagina en el frontend (`limit`/`offset`) con un control de paginación, y el total del conteo determina la existencia de páginas adicionales.
- El aviso ámbar se reescribe para no referenciar un modelo retirado; se redacta de forma agnóstica al modelo, aludiendo al umbral de revisión humana del clasificador (70%).
- Sin cambios de autenticación/RBAC. El endpoint de listado existente mantiene su forma de array (no se rompe `backend-integration-tests`); el conteo es un recurso nuevo.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `frontend-revision-humana`: agrega requisitos para que el contador de la pestaña refleje el total real del alcance (FRH-008), la cola sea paginable sin truncamiento silencioso (FRH-009) y el aviso de criterio no referencie un modelo retirado (FRH-010).
- `incident-visibility`: agrega un requisito para que el endpoint de conteo de la cola de revisión pendiente aplique exactamente el mismo alcance que el listado (VIS-006), reutilizando el servicio de visibilidad sin duplicar la derivación rol -> alcance.

## Impact

- Backend:
  - `App/Backend/app/routes/clasificaciones.py` — nuevo endpoint aditivo `GET /clasificaciones/revision-pendiente/count`.
  - `App/Backend/app/services/clasificacion_service.py` — nuevo método `count_pending_review(alcance)`.
  - `App/Backend/app/repositories/clasificacion_repository.py` — nuevo `count_pending_review(reportante_empleado_id)` con los mismos filtros de "pendiente".
  - `App/Backend/app/schemas/clasificacion.py` — nuevo schema de respuesta del conteo.
  - `docs/openapi.json` — regenerar (existe `tests/test_openapi_sync.py`).
- Frontend:
  - `App/Frontend/src/pages/Administracion/index.tsx` — badge con el total del conteo; paginación de la cola; aviso corregido.
  - `App/Frontend/src/hooks/useRevisionPendiente.ts` — hook/consulta de conteo y parámetros de paginación de la tabla.
  - `App/Frontend/src/services/clasificacionesService.ts` — nueva función que consume el conteo.
  - `App/Frontend/src/types/clasificacion.ts` — tipo de la respuesta del conteo.
  - `App/Frontend/src/pages/Administracion/RevisionHumanaTable.tsx` — soporte de paginación (el control puede vivir en la página).
- Tests: backend (unit SQLite + integración PostgreSQL), frontend (Vitest), sincronización OpenAPI.
- Documentación FUERA DE ALCANCE (seguimiento opcional): `docs/parameters_gemini.md` y `docs/anexo_h_prompt_gemini.md` siguen refiriendo `gemini-2.5-flash`; actualizarlos es un follow-up de documentación, no forma parte de este change de código.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|-----------|
| Duplicar la lógica de alcance entre listado y conteo (divergencia) | Media | El conteo reutiliza `AlcanceIncidentes` + la misma derivación de `reportante_empleado_id` del servicio; el repositorio comparte los `where` de "pendiente" con el listado |
| El conteo y la lista discrepan por una respuesta de conteo mal formada | Baja | Schema explícito (`total: int`) y test de contrato que compara el total del conteo con `len()` de la lista sin paginar |
| Paginación del frontend rompe el refresh tras validar | Baja | Al validar con éxito ya se refresca `revision-pendiente`; extender el refresh al conteo y resetear offset si la página queda vacía |
| Regenerar `docs/openapi.json` desincronizado | Baja | El test `test_openapi_sync.py` falla si no se regenera; incluido como tarea de apply |
| Rutas `/revision-pendiente` vs `/revision-pendiente/count` colisionan | Baja | Son paths estáticos distintos; no hay path param en conflicto. Verificar orden de declaración |

## Rollback Plan

Revertir el commit del change. El conteo es aditivo (nuevo endpoint + nuevo método de servicio/repositorio): revertirlo no deja estado persistente ni migraciones. El frontend vuelve al badge basado en `length` y al aviso anterior. Sin cambios de esquema de base de datos.

## Success Criteria

- [ ] Con 50 o más pendientes, el badge de "Revisión Humana" muestra el total real, no 50.
- [ ] El badge respeta el alcance: un `usuario_final` ve el total de sus propios pendientes; alcance vacío ve 0.
- [ ] La tabla de revisión permite ver/paginar más allá de la primera página sin truncamiento silencioso.
- [ ] El aviso ámbar no menciona "Gemini 2.5 Flash" ni ningún modelo retirado.
- [ ] El endpoint de listado conserva su forma de array; la suite backend (SQLite + integración), la suite frontend y el test de sincronización OpenAPI pasan.

## Open Questions

1. **Mecanismo del contador: RESUELTO.** Endpoint aditivo de conteo (`GET .../revision-pendiente/count`, respuesta `{ "total": int }`) en lugar de envolver el listado en un envelope paginado, para no romper el contrato de array asentado en `backend-integration-tests`.
2. **Paginación de la tabla: RESUELTO.** Se pagina con `limit`/`offset` reutilizando el patrón `Paginacion` ya presente en la pestaña de tickets; el total del conteo alimenta la detección de páginas adicionales.
3. **Texto del aviso: RESUELTO.** Se redacta agnóstico al modelo (no nombra ningún modelo de Gemini) para evitar que el aviso vuelva a quedar obsoleto ante futuros cambios de modelo; menciona el umbral de revisión humana del clasificador (70%).
4. **Alcance de la spec: RESUELTO.** Dos deltas: `frontend-revision-humana` (comportamiento del tab) e `incident-visibility` (VIS-006, alcance del conteo). No se crea capability nueva.
5. **Docs obsoletas (`parameters_gemini.md`, `anexo_h_prompt_gemini.md`): ABIERTO / FUERA DE ALCANCE.** Registrado como follow-up de documentación; no se edita en este change de código.
