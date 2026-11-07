# Proposal: Reflejar las causas reales de derivación en el aviso de revisión humana

## Why

El aviso explicativo de la pestaña "Revisión Humana" afirma que la cola contiene únicamente
incidentes clasificados con confianza inferior al 70%. Eso es FALSO: la cola se filtra por el flag
`requiere_revision_humana == True AND sector_id_validado IS NULL`, y ese flag se activa por TRES
causas independientes — confianza por debajo del umbral en la etapa Gemini, clasificación resuelta
en la etapa de respaldo (fallback) y reportante no identificado (VIS-005), esta última forzada con
independencia de la confianza. Evidencia de la campaña en vivo: hay casos en cola con confianza 0.98
(todos por reportante anónimo). El texto actual induce a error al operador sobre por qué un incidente
requiere su revisión.

## What Changes

- Reescribir el texto del aviso de la pestaña "Revisión Humana"
  (`App/Frontend/src/pages/Administracion/index.tsx`, `<p>` en ~444-447) para que describa las TRES
  causas reales de derivación: (1) confianza del clasificador por debajo del umbral del 70%,
  (2) clasificación resuelta en la etapa de respaldo, (3) reportante no identificado. Conserva el
  cierre "Revisá y confirmá el sector correcto para cada uno".
- Actualizar la prueba que fija el literal del aviso
  (`App/Frontend/src/pages/Administracion/index.aviso.test.tsx`, FRH-010): el literal esperado y el
  matcher por regex.
- Sin cambios de comportamiento, backend, endpoints, esquemas, umbral ni lógica del flag. El cambio
  es exclusivamente de texto en el frontend.

**Fuera de alcance (documentado, no se implementa):**

- Un indicador POR FILA de la causa de derivación: exigiría que el backend exponga POR QUÉ cada log
  quedó marcado. Se registra como mejora futura posible (ver `design.md`, D3). No se toca el filtro
  de la cola, el umbral (`human_review = 0.70`) ni ninguna lógica de backend.
- El cortocircuito determinístico (c-74/D1): la etapa `deterministic` NUNCA marca por confianza; el
  aviso no debe sugerir que toda confianza baja deriva a revisión.

## Capabilities

### Modified Capabilities

- `frontend-revision-humana`: se modifica el requisito FRH-010 ("El aviso de criterio no referencia
  un modelo retirado") para que el aviso SHALL describir TODAS las causas reales de derivación
  (confianza por debajo del 70%, etapa de respaldo, reportante no identificado), manteniendo el texto
  agnóstico al modelo, en español técnico neutro y sin emojis.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `App/Frontend/src/pages/Administracion/index.tsx` | Modified | Texto del `<p>` del aviso (FRH-010) |
| `App/Frontend/src/pages/Administracion/index.aviso.test.tsx` | Modified | Literal esperado y matcher por regex del aviso |
| `openspec/specs/frontend-revision-humana/spec.md` | Modified (vía delta) | FRH-010 actualizado al describir todas las causas |

Sin cambios en backend, API, esquemas, Docker, N8N ni en el umbral de derivación.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Que el texto vuelva a reducir la cola a un solo criterio | Low | FRH-010 exige describir las tres causas; prueba de componente que fija el literal |
| Que se deslice un nombre de modelo en el texto | Low | Aserción existente que prohíbe "gemini"/"flash"; redacción agnóstica al modelo |
| Cambio de backend por confusión del alcance | Low | Fuera de alcance explícito; el diff se limita a dos archivos de frontend y el delta de spec |

## Rollback Plan

Revertir el commit del change (puramente textual y de spec). No hay migraciones, cambios de esquema,
efectos de datos ni cambios de comportamiento. Alternativa puntual: restaurar el literal previo del
aviso y su aserción.

## Success Criteria

- [ ] El aviso describe las tres causas reales de derivación y no afirma que la cola sea solo "confianza < 70%".
- [ ] El aviso permanece agnóstico al modelo, en español técnico neutro, sin emojis, y conserva el cierre de validación.
- [ ] `cd App/Frontend; npm run test src/pages/Administracion/index.aviso.test.tsx` en verde.
- [ ] `cd App/Frontend; npx tsc --noEmit` sin errores.
- [ ] `openspec validate "c-178-reflejar-las-causas-reales-de-derivacion-en-el-aviso-de-revision-humana" --strict` en PASS.
