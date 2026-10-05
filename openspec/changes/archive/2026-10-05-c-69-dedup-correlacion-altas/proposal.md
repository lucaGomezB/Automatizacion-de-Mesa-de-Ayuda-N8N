## Why

Dos brechas acopladas alrededor de la identidad de un alta (`origen_message_id`):

1. **Dedup web ausente** (decision del autor sobre OQ2 de c-68): el canal web envia `origen_message_id = null`. El backend ya tiene el indice unico de `origen_message_id` (migracion 005) para el alta idempotente de correo (Message-ID/UID) y telefonia (CallSid), pero web lo esquiva. Reingestar el mismo caso web (por ejemplo, el harness del corpus) crea incidentes duplicados.
2. **Correlacion imposible** (OQ6 de c-68): `IncidenteRead` NO expone `origen_message_id` y el listado no lo expone ni filtra por el, forzando heuristicas fragiles de ventana temporal para atar un item enviado al incidente persistido.

Este change es PREREQUISITO de C-68: sin dedup web y sin correlacion exacta, el harness no puede re-ejecutar ni correlacionar de forma confiable.

## What Changes

- **Web siempre lleva `origen_message_id`**: el normalizador de `n8n/workflow.json` deja de forzar `null` en la rama web. Acepta un id deterministico provisto por el llamador (el harness envia `corpus-<ID>`) y, para el formulario web real, genera un id unico (derivado de la ejecucion/caso) que no colisiona entre usuarios distintos. La rama correo/telefonia NO cambia.
- **Alta idempotente de web server-side**: la restriccion unica existente deduplica el alta web sin cambios de esquema.
- **Contrato de lectura expone `origen_message_id`**: se agrega a `IncidenteRead` y se habilita un filtro exacto opcional `origen_message_id` en el listado, para que el harness correlacione por identidad exacta en vez de por ventana. Los replays idempotentes conservan la medicion original (no re-miden), en linea con `docs/medicion-latencia-e2e.md` §6.
- **Sin backfill**: las filas web legacy quedan con `origen_message_id` nulo (OQ-D).
- Tests TDD (RED/GREEN/TRIANGULATE/REFACTOR) de schemas, repositorio/servicio/ruta y del nodo normalizador.

## Capabilities

### New Capabilities

- `incident-origin-correlation`: contrato de lectura que expone `origen_message_id` y permite filtrar el listado por coincidencia exacta, habilitando la correlacion determinista item-enviado ↔ incidente-persistido y la exclusion de replays idempotentes.

### Modified Capabilities

- `incident-intake-guards`: el alta web pasa a declarar SIEMPRE un `origen_message_id` (provisto o generado), de modo que el indice unico deduplique el canal web igual que correo y telefonia; los emisores sin identificador dejan de ser el caso web.
- `n8n-workflow`: el nodo "Normalizar entrada del incidente" construye `origen_message_id` para el canal web (acepta id deterministico del llamador, genera uno unico para el formulario real) en lugar de forzar `null`.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/schemas/incidente.py` | Modified | `IncidenteRead` expone `origen_message_id` |
| `App/Backend/app/routes/incidentes.py` | Modified | Filtro exacto opcional `origen_message_id` en el listado |
| `App/Backend/app/services/incidente_service.py` | Modified | Propagacion del filtro en `list_incidentes` |
| `App/Backend/app/repositories/incidente_repository.py` | Modified | Condicion exacta en `list_filtered` |
| `App/Backend/tests/` | Modified | Tests de contrato de lectura y del filtro |
| `n8n/workflow.json` | Modified | Rama web de `origenMessageId` (no mas `null`) |
| `docs/medicion-latencia-e2e.md` | Config | Referencia a la correlacion exacta (§6) |
| `App/Frontend/` | Sin cambios | El formulario real no envia id; n8n lo genera (verificar) |

## Open Questions

Ninguna. Las OQ-A..OQ-D quedaron RESUELTAS por el autor (decisiones registradas en `design.md` §Decisions y §Resolved Open Questions):

- **OQ-A (RESUELTA) — Origen del id web**: n8n es la fuente PRIMARIA. El nodo web acepta un id deterministico provisto por el llamador (`webBody.origen_message_id`, p.ej. el harness envia `corpus-<case_id>`) y, cuando falta, genera un id unico por ejecucion (`web-<execution.id>-<timestamp>`). El default UUID del backend es opcional/secundario. La unicidad jamas rechaza a un usuario real distinto.
- **OQ-B (RESUELTA) — Superficie de lectura**: se expone `origen_message_id` en `IncidenteRead` Y se agrega el filtro exacto opcional `origen_message_id` en el listado (routes -> service -> repository), respetando el alcance por rol VIS-001.
- **OQ-C (RESUELTA) — Formulario real**: el formulario web real NO envia id; n8n lo genera. Sin cambios en el frontend.
- **OQ-D (RESUELTA) — Backfill**: NO hay backfill. Las filas web legacy conservan `origen_message_id` nulo. Sin migracion.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Colision de ids generados para usuarios reales | Low | Id derivado de ejecucion/caso (unico); nunca un hash de la descripcion |
| Romper la rama correo/telefonia al tocar el ternario | Med | Preservar las ramas existentes; tests estructurales del workflow |
| Regresion del listado/schema | Med | Tests de contrato; `pytest` backend y `test_openapi_sync` |
| Divergencia de correlacion por formato de id | Low | Normalizar corchetes/espacios en ambos extremos |

## Rollback Plan

Revertir el commit restaura el ternario web a `null`, quita el campo y el filtro del contrato de lectura. No hay migracion de esquema (el indice unico 005 ya existe): el rollback es codigo + JSON del workflow. Las filas web con id generado permanecen validas (columnas nullable) y no requieren limpieza.

## Success Criteria

- [ ] Dos altas web con el mismo `origen_message_id` devuelven el incidente existente sin crear fila ni re-clasificar (idempotencia server-side).
- [ ] El formulario web real genera un id unico por envio; el harness puede enviar `corpus-<ID>` deterministico.
- [ ] `IncidenteRead` expone `origen_message_id` y el listado filtra por el de forma exacta.
- [ ] Las ramas correo y telefonia del normalizador no cambian su comportamiento.
- [ ] `pytest -m "not integration"` y `openspec validate --strict --changes c-69-dedup-correlacion-altas` pasan.

## Governance

- **Governance**: MEDIO (contrato de lectura del backend + ingreso/identidad en N8N). Las OQ-A..OQ-D estan RESUELTAS por el autor; el change queda apply-ready.
