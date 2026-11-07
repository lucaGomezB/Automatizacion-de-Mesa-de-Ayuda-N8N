# Proposal: Rotular la etapa Gemini como "Análisis por IA"

## Why

La UI etiqueta la etapa del pipeline `gemini` como "Gemini". Nombrar al proveedor reintroduce la
deriva que el change c-176 corrigió parcialmente: si el clasificador cambia de proveedor o de
modelo, la etiqueta vuelve a quedar obsoleta. La etapa del pipeline es un valor de enum estable
(`deterministic | gemini | fallback`) y su etiqueta debe describir la ETAPA de análisis, no al
proveedor. Se busca una etiqueta plenamente agnóstica al proveedor y a la versión: "Análisis por IA".

## What Changes

- Cambiar la etiqueta de la etapa `gemini` en `formatearEtapa` (`App/Frontend/src/utils/formatters.ts`)
  de "Gemini" a exactamente "Análisis por IA". Las etiquetas de `deterministic` ("Determinístico") y
  `fallback` ("Sin clasificar") permanecen SIN cambios; una etapa desconocida se devuelve tal cual.
- El cambio de etiqueta surte efecto en todas las superficies que renderizan la etapa del pipeline:
  `DetalleIncidente.tsx`, `RevisionHumanaTable.tsx`, `ValidarClasificacionDialog.tsx` y la tarjeta de
  confirmación del portal de reporte (`SuccessCard.tsx`), todas vía `formatearEtapa`.
- Actualizar el texto informativo del portal de reporte (`App/Frontend/src/pages/ReportarIncidente/index.tsx`,
  línea ~77) para que NO nombre al proveedor: se elimina el paréntesis "(Gemini)". La nota informativa
  sobre el umbral de revisión humana del 70% se conserva intacta y con el mismo significado.
- Actualizar las pruebas que fijan el literal "Gemini" en la UI: `formatters.etapa.test.ts`,
  `DetalleIncidente.test.tsx`, `ValidarClasificacionDialog.test.tsx` y `ReportarIncidente/index.test.tsx`.
- Sin cambios de comportamiento, backend, endpoints ni esquemas.

**Fuera de alcance (se preserva sin tocar):** la etiqueta "Sector Asignado por IA" de
`ReportarIncidente/SuccessCard.tsx`; el banner de "Revisión Humana" (cubierto por `frontend-revision-humana`
FRH-010); y toda mención histórica rotulada (knowledge-base, `settings.py`, `evaluation/**`,
`foundation-environment/spec.md`, `CHANGES.md`).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `frontend-model-mentions`: el requisito "La etiqueta de la etapa del pipeline es agnóstica a la
  versión del modelo" pasa de exigir "Gemini" (agnóstico a la versión) a exigir "Análisis por IA"
  (agnóstico al proveedor y a la versión, sin nombre de proveedor ni de modelo).

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `App/Frontend/src/utils/formatters.ts` | Modified | Etiqueta de `formatearEtapa('gemini')` |
| `App/Frontend/src/pages/ReportarIncidente/index.tsx` | Modified | Texto informativo del portal (quita "(Gemini)") |
| `App/Frontend/src/utils/formatters.etapa.test.ts` | Modified | Aserción de la etiqueta |
| `App/Frontend/src/pages/Administracion/DetalleIncidente.test.tsx` | Modified | Aserción de la etiqueta |
| `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.test.tsx` | Modified | Aserción de la etiqueta |
| `App/Frontend/src/pages/ReportarIncidente/index.test.tsx` | Modified | Aserción del texto del portal |

Sin cambios en backend, API, esquemas, migraciones, Docker ni N8N.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Otra superficie renderice el literal "Gemini" fuera de `formatearEtapa` | Low | `grep` de alcance en la tarea 1.2 acota el conjunto real antes de tocar |
| Que un reviewer prefiera mantener el nombre del proveedor visible | Low | `design.md` (D1) documenta el trade-off; revertir es textual y acotado |

## Rollback Plan

Revertir el commit del change (puramente textual). No hay migraciones ni efectos de datos.
Alternativa puntual: restaurar el literal "Gemini" en la etiqueta, el texto del portal y las
aserciones.

## Success Criteria

- [x] `formatearEtapa('gemini')` devuelve exactamente "Análisis por IA" (con acento) y no contiene
      nombre de proveedor ni de versión.
- [x] Las etiquetas de `deterministic` y `fallback` permanecen "Determinístico" y "Sin clasificar".
- [x] Ni la etiqueta de la etapa del pipeline ni el texto del portal de reporte muestran el nombre
      del proveedor. FUERA de alcance por decisión (2026-11-07): el aviso legal de Privacidad que
      nombra "Gemini" (deber de información de transferencia internacional, Ley 25.326 art. 6) y la
      etiqueta de auditoría admin "Respuesta raw de Gemini" (se conservan sin cambios).
- [x] La nota informativa del portal conserva el umbral de revisión humana del 70%.
- [x] `cd App/Frontend; npm run test` en verde (60 archivos / 391 pruebas).
- [x] `openspec validate "c-177-rotular-la-etapa-gemini-como-analisis-por-ia" --strict` en PASS.
