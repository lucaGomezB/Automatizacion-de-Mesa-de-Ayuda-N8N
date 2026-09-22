## Why

El nodo `Guard de costo` que C-45 introdujo en el canal de telefonía es un `httpRequest`: su salida REEMPLAZA el item por el cuerpo de la respuesta del backend (`{allowed, ...}`). Como consecuencia, cuando `Guard permite?` rutea hacia el `AI Agent`, el agente recibe solo `{allowed: true}` y PIERDE la transcripción/descripcion del incidente que necesita para clasificar. El prompt del agente interpola `$json.transcript || $json.body || $json.descripcion || $json.text`, todos ausentes tras la guarda; la clasificación queda vacía o inválida y el canal dominante en costo se degrada en silencio. Además, el mismo nodo conserva la referencia frágil `$('Sellar ingreso telefonia').item.json.From` (`n8n/workflow.json:779`), que depende de `pairedItem` y puede resolver `null` sin señal, el MISMO defecto que C-46 ya corrigió en el validador y en el terminal con `.first()`.

## What Changes

- Preservar el item de telefonía a través del nodo `Guard de costo` mediante un nodo `code` de restauración que recupera el item sellado con `$('Sellar ingreso telefonia').first()` —el patrón robusto de C-46— y le re-inyecta la decisión de la guarda (`allowed`), de modo que el `AI Agent` vuelva a recibir la transcripción/descripcion y que `Guard permite?` siga leyendo `$json.allowed`.
- Reemplazar la referencia frágil `$('Sellar ingreso telefonia').item` del body del nodo `Guard de costo` (`caller`) por el item corriente del propio nodo (`$json.From || $json.from`), eliminando la dependencia de `pairedItem` sin introducir una referencia cruzada entre nodos. El nodo de restauración D1 sigue usando `$('Sellar ingreso telefonia').first()`, donde sí es necesario.
- NO regresar el comportamiento de C-46 en el nodo terminal `Derivar a revision humana`: se conserva el WARN estructurado + `revision_forzada=true` + `requiere_revision_humana=true` y la creación del ticket cuando el sello no resuelve.
- NO cambiar la semántica de costo de la guarda (monto, ventana, rate, costos unitarios, fail-closed, endpoint o backend): el cambio es de propagación del item y robustez de referencia, no de política de costo.
- Extender la suite estructural `App/Backend/tests/test_n8n_workflow.py` con pruebas de regresión para la preservación del item a través de la guarda y para el uso de `$json` (item corriente) en el body de la guarda.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `n8n-workflow`: se agrega el requisito de que la guarda de costo NO destruya el item del canal de telefonía (el `AI Agent` debe recibir la descripción/transcripción original) y de que el `caller` de la guarda resuelva desde el item corriente (`$json`) en lugar de la referencia frágil `.item`, sin regresar la recuperación robusta del sello de C-46.

`runtime-cost-guard` fue evaluado y NO se modifica: sus requisitos describen el tope de gasto, la decisión `permitir`/`denegar`, el rate, el fail-closed, la degradación y la observabilidad, todos intactos. Lo que falla es el cableado de items del workflow que consume esa decisión, un contrato aguas arriba del canal que vive en `n8n-workflow` (igual que C-46 mantuvo allí N8N-TIMING-001/002/003). Mantenerlo ahí evita dividir la fuente de verdad.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `n8n/workflow.json` — nodo nuevo de restauración entre `Guard de costo` y `Guard permite?` | New | Recupera `$('Sellar ingreso telefonia').first()` y re-inyecta `allowed`; el `AI Agent` recupera la transcripción/descripcion |
| `n8n/workflow.json` — `Guard de costo` (body `caller`) | Modified | `.item` → `$json.From || $json.from` (item corriente, sin referencia cruzada ni `pairedItem`) |
| `n8n/workflow.json` — conexiones `Guard de costo` → `Guard permite?` | Modified | Se intercala el nodo de restauración |
| `n8n/workflow.json` — `Derivar a revision humana` (C-46) | Sin cambios | Se preserva el comportamiento N8N-TIMING-003; se verifica que no regrese |
| `n8n/workflow.json` — `Se verifica lo que trajo la IA` (C-46) | Sin cambios | Ya usa `.first()` |
| `App/Backend/tests/test_n8n_workflow.py` | Modified | Pruebas estructurales de preservación del item y de `$json` (sin referencia cruzada) en la guarda |
| `docs/n8n-workflow-guide.md` | Modified (si aplica) | Documentar la restauración del item y actualizar el conteo declarado de propiedades estructurales |
| Backend (`app/`, `alembic/`, endpoints de la guarda) | Sin cambios | Contrato, endpoint `/reserve` y política de costo intactos |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| La restauración altera el ruteo de la guarda (`$json.allowed`) | Low | El nodo de restauración re-inyecta `allowed` en el item resultante; `Guard permite?` conserva su condición `$json.allowed == true` y las pruebas estructurales lo verifican |
| Regresar C-46 en `Derivar a revision humana` | Low | El nodo terminal no se toca; se agrega una prueba de no regresión que exige `.first()` y el WARN estructurado |
| Solapamiento con el diffs de C-46 en el mismo terminal | Low | C-47 no edita ese nodo; solo verifica su contrato. Revisar el diff del nodo al integrar |
| Falsa confianza por verificación estructural sin runtime N8N | Med | No hay harness de runtime en CI; se documenta que la verificación en vivo es obligatoria y que la suite es guarda de regresión |
| Duplicación de la recuperación del item (restauración + terminal) | Low | Es idempotente: ambos fusionan el mismo item sellado; el terminal ya recupera por su cuenta para su propia rama de entrada |

## Rollback Plan

Revertir el commit del `workflow.json` restaura el cableado previo (`Guard de costo` → `Guard permite?`), la referencia `.item` en el body y elimina el nodo de restauración. Las pruebas estructurales y la guía se revierten en el mismo commit. No hay migración de datos, cambio de backend ni de configuración de la guarda: los incidentes y contadores existentes permanecen intactos.

## Success Criteria

- [ ] El `AI Agent` recibe la descripción/transcripción del incidente aunque el flujo pase por `Guard de costo`.
- [ ] `Guard permite?` sigue leyendo la decisión `allowed` de la guarda y el ruteo true/false no cambia.
- [ ] El body del nodo `Guard de costo` resuelve `caller` desde el item corriente (`$json`) y NO usa la referencia frágil `.item`.
- [ ] El comportamiento N8N-TIMING-003 de C-46 en `Derivar a revision humana` se preserva (WARN + revisión forzada, ticket creado).
- [ ] No hay cambios en el endpoint `/reserve`, en la política de costo ni en el backend.
- [ ] `openspec validate --strict --changes c-47-guard-costo-item` pasa.