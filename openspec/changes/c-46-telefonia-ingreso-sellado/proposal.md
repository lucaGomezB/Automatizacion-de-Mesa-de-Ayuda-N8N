## Why

El canal de telefonía (el dominante en costo, porque pasa por el `AI Agent` pago) pierde SILENCIOSAMENTE el instante de ingreso `ingresado_en`. El nodo sellador `Sellar ingreso telefonia` lo fija antes del agente, pero el validador `Se verifica lo que trajo la IA` lo recupera con `$('Sellar ingreso telefonia').item.json.ingresado_en` dentro de un `try/catch` que devuelve `null`. La resolución `.item` depende de `pairedItem`; cuando el `item` corriente proviene del `AI Agent` (y del bucle de refinamiento), el pairing se rompe y la recuperación cae al `catch` sin error visible. Resultado: `latencia_e2e_ms` nula para el canal que más importa medir, sin ninguna señal de fallo. El verificador de C-39 ya registró esta desviación como HIGH #3 y recomendó `.first()` + un WARN explícito (`openspec/changes/archive/2026-09-20-c-39-e2e-timing-instrumentation/verify-report.md:207-219`).

## What Changes

- Recuperar el sello con `$('Sellar ingreso telefonia').first().json.ingresado_en` (no `.item`) en el validador `Se verifica lo que trajo la IA` y en el terminal `Derivar a revision humana`.
- Eliminar el silenciamiento (`catch`/`|| null`): si el sello aún no se puede resolver, el incidente MUST NOT abortarse ni perderse. Se emite un WARN estructurado y se marca `requiere_revision_humana=true` CONSERVANDO la creación del ticket (el backend honra el flag explícito).
- Extender las pruebas estructurales de `test_n8n_workflow.py` para asertar la referencia exacta al nodo de sello, el uso de `.first()` vs `.item`, y el comportamiento de sello ausente → revisión humana con ticket creado. Hoy solo verifican la subcadena `"ingresado_en"`.
- Backend SIN cambios: el contrato ya acepta `ingresado_en` nulo (`IncidenteCreate.ingresado_en`, nullable) y ya honra `clasificacion.requiere_revision_humana`.

Fuera de alcance (changes separados): el nodo `Guard de costo` que reemplaza el item (`c-47`), exponer tiempos en `IncidenteListItem` (`c-48`), carga del corpus (`c-49`) y cableado de tiempos del corpus (`c-50`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `n8n-workflow`: se agrega el requisito de recuperación ROBUSTA del sello de ingreso de telefonía a través del `AI Agent` y de derivación a revisión humana cuando el sello no se resuelve, con el ticket igualmente creado y sin silenciamiento.

`e2e-timing-instrumentation` fue evaluado y NO se modifica: el contrato backend (persistencia, validación, derivación de latencia y política de latencia negativa) permanece idéntico. El contrato aguas arriba del canal vive en `n8n-workflow` (N8N-TIMING-001/002, C-39), por lo que mantenerlo ahí evita dividir la fuente de verdad.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `n8n/workflow.json` — `Se verifica lo que trajo la IA` | Modified | `.first()` en la recuperación; WARN + `requiere_revision_humana=true` si el sello falta |
| `n8n/workflow.json` — `Derivar a revision humana` | Modified | Misma corrección `.first()` de la recuperación |
| `App/Backend/tests/test_n8n_workflow.py` | Modified | Pruebas estructurales que asertan nodo exacto, `.first()` y fallback a revisión humana |
| Backend (`schemas/`, `services/`, migraciones) | Sin cambios | Contrato `ingresado_en` nullable y flag de revisión ya existentes |
| `docs/n8n-workflow-guide.md` | Modified (si aplica) | Registrar la recuperación robusta y su caveat de verificación en runtime |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `.first()` tampoco resuelve en runtime (contrato de pairing de N8N) | Low | Es la recomendación del verificador C-39; se añade WARN + revisión humana como red de seguridad, de modo que un fallo no sea silencioso |
| Marcar revisión humana en exceso por falsos negativos de recuperación | Low | Solo se dispara cuando `ingresado_en` es nulo; el ticket nunca se pierde y el operador revisa |
| Las pruebas estructurales dan falsa confianza | Med | No hay harness de runtime N8N en CI; se documenta que la verificación en vivo es obligatoria y que los tests son guarda de regresión |
| Degradar el ruteo existente del canal de telefonía | Low | El cambio es acotado a dos nodos; se extienden las pruebas estructurales existentes sin alterar el contrato del POST |

## Rollback Plan

Revertir el commit del `workflow.json` restaura el patrón `.item` + `try/catch` previo. Las pruebas estructurales y la guía se revierten en el mismo commit. No hay migración de datos ni cambio de esquema: los incidentes ya creados con `ingresado_en` nulo permanecen intactos y el backend no se toca.

## Success Criteria

- [ ] El validador `Se verifica lo que trajo la IA` referencia el sello con `.first()` y no con `.item`.
- [ ] El terminal `Derivar a revision humana` referencia el sello con `.first()`.
- [ ] Ante sello no resoluble, el incidente se marca `requiere_revision_humana=true` y el ticket se crea igual; la ejecución nunca aborta ni se pierde.
- [ ] No queda ningún `catch`/`|| null` que silencie la ausencia del sello; se emite un WARN estructurado.
- [ ] Las pruebas estructurales asertan nodo exacto, `.first()` vs `.item`, y el fallback a revisión humana con ticket creado.
- [ ] `openspec validate --strict --changes c-46-telefonia-ingreso-sellado` pasa.