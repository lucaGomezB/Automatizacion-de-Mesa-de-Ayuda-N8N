# Proposal: Ocultar la respuesta raw de la clasificación en la UI

## Why

El componente compartido de detalle (`DetalleIncidente`) renderiza hoy un bloque rotulado "Respuesta
raw de Gemini" con el JSON crudo del clasificador (`respuesta_raw`) dentro de un `<pre>`. Ese bloque
se muestra en las DOS superficies de detalle (validación humana y detalle del ticket) por ser un
componente de solo lectura reutilizado. El operador no necesita el JSON crudo para decidir el sector
correcto y su exposición agrega ruido y una mención de proveedor en la interfaz. La decisión de
alcance es ocultarlo en AMBAS superficies, no solo en el diálogo de validación.

## What Changes

- Eliminar el bloque "Respuesta raw de Gemini" de
  `App/Frontend/src/pages/Administracion/DetalleIncidente.tsx` (~líneas 200-210). El resto de la
  sección de clasificación (sector predicho, confianza, etapa del pipeline, sector validado,
  sectores adicionales predichos y validados) permanece intacto.
- Al quitar el bloque del componente compartido, la respuesta raw deja de renderizarse a la vez en
  `ValidarClasificacionDialog` (línea ~225) y en `TicketDetailDialog` (línea ~107), que lo reutilizan
  (FRH-004). No se toca ningún otro campo.
- Actualizar las pruebas que hoy afirman que la respuesta raw SE muestra para que afirmen que NO se
  muestra, conservando las aserciones del resto del bloque de clasificación:
  - `App/Frontend/src/pages/Administracion/DetalleIncidente.test.tsx` (aserción sobre
    `/"sector_predicho"/` y caso "omite la respuesta raw…").
  - `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.test.tsx` (mock con
    `respuesta_raw` y prueba "muestra la clasificacion completa incluida la respuesta raw").
  - `App/Frontend/src/pages/Administracion/TicketDetailDialog.test.tsx` (mock con `respuesta_raw` y
    aserción sobre `/"sector_predicho"/`).

**Fuera de alcance (documentado, no se implementa):**

- NO se elimina el campo `respuesta_raw` del tipo `ClasificacionLogRead` ni de la API. El dato sigue
  disponible para auditoría vía la API; solo se deja de RENDERIZAR en la interfaz.
- NO se cambia ningún comportamiento de backend, datos, DB ni esquema de respuesta.

## Capabilities

### Modified Capabilities

- `frontend-revision-humana`: se modifica el requisito FRH-003 ("El flujo de validacion expone el
  resultado completo de la clasificacion") para que el diálogo de validación SHALL mostrar el
  resultado de la clasificación SIN la respuesta raw. Se retira `respuesta_raw` del conjunto de
  campos exhibidos y se convierte el escenario "La clasificacion tiene respuesta raw" en la
  afirmación inversa (el campo existe pero NO se muestra). FRH-004 no cambia: su escenario enumera
  campos de detalle del incidente (no del bloque de clasificación) y la consistencia entre superficies
  se preserva porque ambas comparten el mismo componente.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `App/Frontend/src/pages/Administracion/DetalleIncidente.tsx` | Modified | Se elimina el bloque `respuesta_raw` (~200-210); nada más cambia |
| `App/Frontend/src/pages/Administracion/DetalleIncidente.test.tsx` | Modified | Aserciones de raw invertidas; resto del bloque intacto |
| `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.test.tsx` | Modified | Aserciones de raw invertidas |
| `App/Frontend/src/pages/Administracion/TicketDetailDialog.test.tsx` | Modified | Aserciones de raw invertidas |
| `App/Frontend/src/types/clasificacion.ts` | Sin cambios | `respuesta_raw` permanece en el tipo |
| `openspec/specs/frontend-revision-humana/spec.md` | Modified (vía delta) | FRH-003 actualizado |

Sin cambios en backend, API, esquemas de respuesta, Docker, N8N, DB ni datos.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Que la firma/etiqueta de la prueba quede referenciando el bloque retirado | Low | Se localizan todas las referencias a "respuesta raw" y `"sector_predicho"` antes de editar |
| Que se retire por error algún campo legítimo del bloque de clasificación | Low | El diff se acota al bloque ~200-210; el resto de `DetalleIncidente` queda intacto |
| Confundir alcance y tocar el tipo/endpoint | Low | Fuera de alcance explícito: `respuesta_raw` sigue en `ClasificacionLogRead` y en la API |

## Rollback Plan

Revertir el commit del change (puramente de presentación y de spec). No hay migraciones, cambios de
esquema, efectos de datos ni cambios de comportamiento de API. Alternativa puntual: restaurar el
bloque retirado y sus aserciones.

## Success Criteria

- [ ] `DetalleIncidente` no renderiza la respuesta raw ni la etiqueta "Respuesta raw de Gemini".
- [ ] El bloque de clasificación conserva sector predicho, confianza, etapa, sector validado y sectores adicionales predichos/validados.
- [ ] El campo `respuesta_raw` sigue existiendo en `ClasificacionLogRead` y en la API (sin cambios).
- [ ] `cd App/Frontend; npm run test` en verde, sin aserciones del bloque retirado.
- [ ] `cd App/Frontend; npx tsc --noEmit` sin errores.
- [ ] `openspec validate "c-180-ocultar-la-respuesta-raw-de-la-clasificacion-en-la-ui" --strict` en PASS.
