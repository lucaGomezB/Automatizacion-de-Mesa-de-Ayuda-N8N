## Context

Ver `proposal.md` — Why. Estado actual relevante:

- Backend: `GET /api/v1/clasificaciones/revision-pendiente` devuelve un array y acota por `limit` (default 50, máximo 200)/`offset`; el alcance se deriva en `ClasificacionService.list_pending_review` a partir de `AlcanceIncidentes` y se traduce a un filtro `reportante_empleado_id` pasado al repositorio. El repositorio ya concentra la definición de "pendiente" (`requiere_revision_humana == true` Y `sector_id_validado IS NULL`) y la política FIFO.
- Frontend: `useRevisionPendiente()` llama al listado sin parámetros; `Administracion/index.tsx` usa `clasificacionesPendientes.length` como badge y como contenido de la tabla, por lo que ambos quedan topeados en 50. La pestaña de tickets ya tiene un patrón de paginación offset-based reutilizable (`Paginacion` + estado de página).
- El diálogo de validación ya invalida la caché con `queryKey: [REVISION_PENDIENTE_QUERY_KEY]` (invalidación por prefijo de React Query).
- Restricciones: capas `routes -> services -> repositories`; SQLAlchemy async (nunca lazy-load de relationships serializados); español técnico neutro; sin cambio de auth/RBAC; TDD estricto con escenarios testeables.

## Goals / Non-Goals

**Goals:**

- Que el badge refleje el total real de pendientes del alcance, sin tope de página, usando un recurso de conteo aditivo que comparta la lógica de alcance y de "pendiente".
- Que la tabla de revisión sea navegable por páginas sin truncamiento silencioso.
- Corregir el aviso ámbar para que no dependa del nombre de un modelo.

**Non-Goals:**

- No se cambia la forma de la respuesta del listado (sigue siendo array): se evita romper el contrato asentado en `backend-integration-tests`.
- No se cambia autenticación/RBAC ni la derivación rol -> alcance (VIS-001/002).
- No se actualizan `docs/parameters_gemini.md` ni `docs/anexo_h_prompt_gemini.md` (follow-up de documentación).
- No se introduce paginación server-side con cursor; se mantiene offset-based.

## Decisions

### D1 — Recurso de conteo aditivo en lugar de envolver el listado

**Decisión:** agregar `GET /api/v1/clasificaciones/revision-pendiente/count` que responde `{ "total": <int> }`.

**Por qué:** el badge necesita un número exacto e ilimitado; el listado debe seguir paginado para no transferir toda la cola. Envolver el listado en un envelope paginado (`{ items, total }`) rompería el contrato de array que `backend-integration-tests` verifica y obligaría a tocar esa spec. El recurso de conteo es aditivo, no rompe consumidores y su semántica (total del alcance) es explícita.

**Alternativas consideradas:** (a) `X-Total-Count` header en el listado — menos descubrible y difícil de tipar en el cliente; (b) envelope en el listado — cambio de contrato rompiente; (c) traer todo sin límite — inviable con colas grandes.

### D2 — Ruta estática `.../revision-pendiente/count`

**Decisión:** declarar el endpoint de conteo en `routes/clasificaciones.py` como path estático, junto al listado.

**Por qué:** `/revision-pendiente` y `/revision-pendiente/count` son segmentos estáticos distintos; no hay `{path_param}` que colisione en ese prefijo (`/incidente/{id}` vive en otro segmento). No se requiere orden especial, pero se declara inmediatamente después del listado por legibilidad.

### D3 — Schema de respuesta explícito

**Decisión:** nuevo schema Pydantic v2 `RevisionPendienteCount` con un único campo `total: int` en `app/schemas/clasificacion.py`; `response_model=RevisionPendienteCount`.

**Por qué:** un contrato tipado permite testear el shape y consumirlo con tipos en el frontend (`{ total: number }`). Un entero pelado como body sería ambiguo y menos extensible.

### D4 — El servicio comparte la derivación de alcance (no la duplica)

**Decisión:** extraer un helper privado en `ClasificacionService` (p. ej. `_reportante_filtro(alcance) -> int | None | _VACIO`) que traduzca `AlcanceIncidentes` a: `None` (GLOBAL), `reportante_empleado_id` (PROPIO) o "cola vacía" (VACIO). Tanto `list_pending_review` como `count_pending_review` lo usan. Al recibir `VACIO`, `count_pending_review` devuelve `0` sin consultar la base. El nuevo método `count_pending_review(alcance)` delega en el repositorio.

**Por qué:** evita que listado y conteo diverjan. Es la misma regla que VIS-002, sin duplicar la derivación rol -> alcance (lo exige VIS-006).

### D5 — El repositorio cuenta con los MISMOS filtros de "pendiente"

**Decisión:** `ClasificacionRepository.count_pending_review(reportante_empleado_id: int | None) -> int` ejecuta `select(func.count()).select_from(ClasificacionLog)` con los `where` idénticos a `list_pending_review` (`requiere_revision_humana == true`, `sector_id_validado IS NULL`, y el filtro opcional por reportante vía `.has(...)`), sin `options()` ni `order_by`. `count_pending_review` NO carga relationships.

**Por qué:** el conteo no serializa relaciones, así que no aplica el requisito de `selectinload` (no hay riesgo de lazy-load). Compartir literalmente las condiciones garantiza que `total` coincide con la lista sin paginar (escenario VIS-006 "el conteo coincide con el listado"). Considerar extraer las condiciones a un helper de statement si se prefiere DRY, pero mantener los `where` idénticos es lo crítico.

### D6 — Hook de conteo con clave prefijada por la cola

**Decisión:** `contarRevisionPendiente(): Promise<number>` en `clasificacionesService.ts` (GET del nuevo endpoint, retorna `data.total`) y hook `useRevisionPendienteCount()` en `useRevisionPendiente.ts` con `queryKey: [REVISION_PENDIENTE_QUERY_KEY, 'count']` y la misma política de refresco (`staleTime: 15s`, `refetchInterval: 60s`).

**Por qué:** la clave prefijada por `REVISION_PENDIENTE_QUERY_KEY` hace que el `invalidateQueries({ queryKey: [REVISION_PENDIENTE_QUERY_KEY] })` ya existente en `ValidarClasificacionDialog` invalide también el conteo, sin tocar el diálogo.

### D7 — Paginación de la tabla reutilizando el patrón existente

**Decisión:** en `Administracion/index.tsx`, agregar estado `paginaRevision` y llamar `useRevisionPendiente({ limit: PAGE_SIZE, offset: paginaRevision * PAGE_SIZE })`. Renderizar el componente `Paginacion` bajo la tabla de revisión, extendiéndolo con un prop opcional `total?: number`: cuando se provee, `haySiguiente = (pagina + 1) * pageSize < total` (exacto); sin `total`, se conserva la heurística actual (`totalEnPagina === pageSize`) para la pestaña de tickets (sin cambios de comportamiento allí). Al validar, si la página actual queda vacía tras refrescar (total <= pagina * pageSize y pagina > 0), retroceder a la última página con resultados.

**Por qué:** reutiliza el patrón ya probado, evita un componente nuevo y mejora la detección de "página siguiente" con el total exacto que ahora conocemos. El `total` se alimenta del hook de conteo.

### D8 — Aviso ámbar agnóstico al modelo

**Decisión:** reemplazar el texto por: "Estos incidentes fueron clasificados con una confianza inferior al 70%, umbral de revisión humana del clasificador. Revisá y confirmá el sector correcto para cada uno."

**Por qué:** el umbral es una constante del clasificador híbrido (`human_review_threshold = 0.70`), no un atributo de un modelo puntual. Nombrar un modelo concreto re-introduce la obsolescencia que este change corrige. Alternativa considerada: mencionar "Gemini 3.6 Flash" — rechazada por acoplar el aviso a un identificador que el frontend no puede leer de la config del backend y que volverá a quedar obsoleto en la próxima migración.

### D9 — Regenerar el OpenAPI estático

**Decisión:** tras agregar el endpoint, regenerar `docs/openapi.json` con el comando documentado en `AGENTS.md`.

**Por qué:** `tests/test_openapi_sync.py` compara el spec regenerado en memoria contra el archivo estático y falla si difieren. Es una tarea obligatoria del apply.

## Risks / Trade-offs

- [Conteo y listado divergen por condiciones copiadas] → Los `where` del conteo se mantienen idénticos a los del listado; el escenario VIS-006 se testea comparando `total` con `len(listado sin paginar)`.
- [Doble consulta por refresco (conteo + lista)] → Aceptable: la cola es de bajo volumen de tráfico de operadores y ambos comparten la política de refresco; el conteo es barato (COUNT sin joins de serialización).
- [Paginación desincronizada al validar la última fila de una página] → Reset de offset cuando la página queda fuera de rango tras el refetch (D7).
- [El conteo podría exponer un total fuera del alcance si se omite el filtro] → VIS-006 lo prohíbe y se cubre con escenarios por rol; el servicio comparte la derivación de alcance (D4).
- [Nueva ruta colisiona con `/revision-pendiente`] → Paths estáticos distintos; verificado en D2.

## Migration Plan

1. Backend: schema `RevisionPendienteCount` → helper de alcance + `ClasificacionService.count_pending_review` → `ClasificacionRepository.count_pending_review` → endpoint `.../revision-pendiente/count` → regenerar `docs/openapi.json`.
2. Frontend: tipo de conteo → `contarRevisionPendiente` → `useRevisionPendienteCount` → `Administracion/index.tsx` (badge, paginación, aviso).
3. Tests en cada paso (TDD estricto): RED → GREEN → triangulación.
4. Rollback: revertir el commit. El conteo es aditivo (endpoint + métodos), sin migraciones ni estado persistente; el frontend vuelve al badge por `length` y al aviso anterior, y `docs/openapi.json` se revierte también.

## Open Questions

Ninguna que afecte specs, enfoque o descomposición de tareas. El follow-up de documentación (`docs/parameters_gemini.md`, `docs/anexo_h_prompt_gemini.md`) queda registrado en el proposal y no condiciona este diseño.
