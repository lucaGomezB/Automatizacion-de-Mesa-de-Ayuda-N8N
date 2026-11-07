# Proposal: Corregir las menciones del modelo vigente en la UI

## Why

El frontend muestra el nombre de un modelo RETIRADO. El modelo vigente del proyecto es
`gemini-3.6-flash` (`App/Backend/app/config/settings.py:78`, `Settings.gemini_model`), pero la
UI etiqueta la etapa del pipeline como "Gemini 2.5 Flash" y el portal de reporte nombra ese
mismo modelo en su texto informativo. Esto contradice el principio ya fijado por
`frontend-revision-humana` FRH-010 (el texto de la UI debe ser agnóstico al modelo) y la
coherencia documental de `project-documentation` DOC-005: el valor vigente declarado SHALL ser
`gemini-3.6-flash` y los hechos históricos SHALL permanecer rotulados. Un cambio de modelo no
debe dejar la UI obsoleta.

## What Changes

- Reemplazar la etiqueta "Gemini 2.5 Flash" de `formatearEtapa('gemini')` por una etiqueta
  agnóstica a la versión ("Gemini"). Surte efecto en `DetalleIncidente.tsx`,
  `RevisionHumanaTable.tsx` y `ReportarIncidente/SuccessCard.tsx`.
- Corregir el texto informativo del portal de reporte (`ReportarIncidente/index.tsx`) para que
  no nombre una versión del modelo.
- Actualizar los dos comentarios que arrastran la mención retirada (`utils/formatters.ts:10`,
  `utils/validators.ts:10`).
- Actualizar las dos pruebas que fijan la etiqueta (`DetalleIncidente.test.tsx:70`,
  `ValidarClasificacionDialog.test.tsx:140`).
- Sin cambios de comportamiento, backend, endpoints ni esquemas.

**Fuera de alcance (histórico, se preserva rotulado como antecedente):**
`knowledge-base/09_decisiones_y_supuestos.md` (DD-04), `settings.py:73`,
`tests/test_gemini_generation_config.py`, `evaluation/run_evaluation.py:96`,
`evaluation/tests/test_sensibilidad_ajustes.py`, `openspec/specs/foundation-environment/spec.md:10`
y `CHANGES.md`. Se prohíbe el reemplazo ciego "2.5" -> "3.6".

## Capabilities

### New Capabilities

- `frontend-model-mentions`: contrato de la UI para que las menciones del modelo de clasificación
  (la etiqueta de la etapa del pipeline y el texto del portal de reporte) identifiquen la etapa o
  al proveedor de forma agnóstica a la versión y no presenten una versión retirada como vigente.

### Modified Capabilities

- None. FRH-010 (`frontend-revision-humana`) ya cubre el AVISO de la pestaña "Revisión Humana"
  (el banner), que ya cumple y NO se modifica. Esta propuesta distingue el banner (FRH-010) de la
  etiqueta de la etapa del pipeline y del texto del portal, que no tenían contrato propio.

## Approach

Approach A (agnóstico al modelo): la etiqueta de la etapa pasa a "Gemini" (sin versión) y el
texto del portal deja de nombrar una versión. Ver `design.md` (D1) para la comparación con
Approach B (nombre vigente desde una única fuente). Motivo: la etapa del pipeline es un valor de
enum estable (`deterministic | gemini | fallback`) y no existe un mecanismo automático que
sincronice `Settings.gemini_model` (backend) con el frontend; nombrar la versión reintroduce la
deriva que este change corrige.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `App/Frontend/src/utils/formatters.ts` | Modified | Etiqueta de `formatearEtapa` y comentario de cabecera |
| `App/Frontend/src/pages/ReportarIncidente/index.tsx` | Modified | Texto informativo del portal |
| `App/Frontend/src/utils/validators.ts` | Modified | Comentario de cabecera |
| `App/Frontend/src/pages/Administracion/DetalleIncidente.test.tsx` | Modified | Aserción de la etiqueta |
| `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.test.tsx` | Modified | Aserción de la etiqueta |
| `App/Frontend/src/utils/formatters.etapa.test.ts` | New | Prueba unitaria de la etiqueta (TDD) |

Sin cambios en backend, API, esquemas, Docker ni N8N.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Reemplazo ciego de menciones históricas | Low | Lista explícita de archivos fuera de alcance; revisión contra `CHANGES.md:2242` |
| Otras superficies dependan del literal retirado | Low | `grep -rn "Gemini 2.5\|2.5 Flash" App/Frontend/src` acota el conjunto real antes de tocar |

## Rollback Plan

Revertir el commit del change (puramente textual). No hay migraciones, cambios de esquema ni
efectos de datos. Alternativa puntual: restaurar el literal "Gemini 2.5 Flash" en la etiqueta,
el texto del portal y las dos aserciones.

## Success Criteria

- [ ] Ninguna mención vigente de "Gemini 2.5 Flash" en la UI del frontend (etiqueta ni texto del portal).
- [ ] Las menciones históricas listadas permanecen intactas y rotuladas.
- [ ] `cd App/Frontend; npm run test` en verde.
- [ ] `openspec validate "c-176-corregir-las-menciones-del-modelo-vigente-en-la-ui" --strict` en PASS.
