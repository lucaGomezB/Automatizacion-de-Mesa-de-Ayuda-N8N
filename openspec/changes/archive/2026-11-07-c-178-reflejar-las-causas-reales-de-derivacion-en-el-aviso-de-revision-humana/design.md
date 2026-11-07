## Context

Ver `proposal.md` (Why). Estado actual y restricciones que condicionan el enfoque:

- El aviso vive en `App/Frontend/src/pages/Administracion/index.tsx` (~444-447), en un `<p>` dentro
  del bloque de la pestaña `revision`. Texto actual: "Estos incidentes fueron clasificados con una
  confianza inferior al 70%, umbral de revisión humana del clasificador. Revisá y confirmá el sector
  correcto para cada uno."
- La cola se filtra en el backend por `requiere_revision_humana == True AND sector_id_validado IS NULL`.
  El flag se activa por tres causas independientes: umbral de confianza de la etapa Gemini
  (`human_review = 0.70`, `openspec/config.yaml:42`), etapa `fallback` (siempre marcada) y reportante
  no identificado (VIS-005, `App/Backend/app/services/incidente_service.py:411-417`:
  `requiere_revision = bool(result.requiere_revision_humana) or (reportante_empleado_id is None)`).
- La etapa `deterministic` NUNCA marca por confianza (c-74/D1,
  `App/Backend/app/schemas/clasificacion.py:74-87`); el aviso no debe sugerir que toda confianza baja
  deriva a revisión.
- El requisito FRH-010 (`openspec/specs/frontend-revision-humana/spec.md:165-177`) fija el contrato
  del aviso y está cubierto por `App/Frontend/src/pages/Administracion/index.aviso.test.tsx`, que
  pinea el literal exacto (líneas 46-49) y usa un matcher por regex (línea 79).
- El frontend no recibe la causa de derivación por registro: no existe un campo que distinga, fila a
  fila, por qué un log quedó marcado.

## Goals / Non-Goals

**Goals:**

- Que el aviso comunique las tres causas reales de derivación y deje de implicar que la cola es solo
  "confianza < 70%".
- Mantener el texto agnóstico al modelo, en español técnico neutro, sin emojis, y con el cierre de
  validación.
- Corregir el contrato FRH-010 y la prueba que lo fija.

**Non-Goals:**

- No cambiar el filtro de la cola, el umbral (`0.70`), el flag ni ninguna lógica de backend.
- No introducir un indicador por fila de la causa de derivación.
- No tocar la etiqueta de la etapa del pipeline ni el texto del portal de reporte (contrato de
  `frontend-model-mentions`, c-176).

## Decisions

### D1 — Enumerar las tres causas en un solo párrafo

**Decisión: reescribir el `<p>` enumerando las tres causas.** Redacción propuesta (final):

> Estos incidentes requieren revisión humana: el clasificador no alcanzó el umbral de confianza
> (70%), la clasificación quedó en la etapa de respaldo, o el reportante no fue identificado. Revisá
> y confirmá el sector correcto para cada uno.

Fundamento:

1. El orden de las causas sigue el orden lógico de la cascada de clasificación (Gemini → fallback),
   con el reportante no identificado como condición transversal del servicio.
2. Conserva el cierre "Revisá y confirmá el sector correcto para cada uno", que es acción del
   operador y no cambia.
3. Es agnóstico al modelo (no nombra "Gemini" ni versión) y no cita la etapa `deterministic`.
4. Evita el vocablo "clasificados/con una confianza inferior" como sujeto único, que es justamente la
   afirmación falsa a corregir.

Alternativa considerada: texto genérico sin enumerar causas ("Estos incidentes fueron derivados
automáticamente a revisión humana..."). Se descarta porque pierde la explicación accionable: el
operador deja de saber por qué un incidente con alta confianza aparece en la cola, que es el problema
que este change corrige.

### D2 — Estrategia de prueba (TDD estricto)

**Decisión: actualizar `index.aviso.test.tsx` como prueba de contrato de componente.** El literal
`TEXTO_ESPERADO` (líneas 46-49) pasa a ser la nueva redacción; el matcher por regex (línea 79) se
cambia por un fragmento estable de la nueva redacción. Se añaden aserciones que verifican que el
aviso menciona la etapa de respaldo y el reportante no identificado, y que NO afirma que la confianza
sea el único criterio. Runner: `cd App/Frontend; npm run test src/pages/Administracion/index.aviso.test.tsx`.
Como `npm run build` ejecuta `tsc` y type-checkea también los tests, la verificación incluye
`npx tsc --noEmit`.

Alternativa considerada: crear un componente de aviso aislado y probarlo unitariamente. Se descarta
porque sería sobre-ingeniería para un cambio de texto: la prueba de componente existente ya cubre el
contrato FRH-010 y solo necesita reflejar la nueva redacción.

### D3 — Indicador por fila de la causa: fuera de alcance (mejora futura posible)

**Decisión: NO implementar un indicador por fila.** Requeriría que el backend exponga POR QUÉ cada
clasificación quedó marcada (p. ej. un campo `causa_revision` en el log o en la respuesta de la cola),
lo que implica cambios de esquema, servicio y esquemas de respuesta: fuera del alcance de este change
(frontend, governance LOW). Se registra como mejora futura: un campo `causa_revision` permitirá que la
cola muestre, por incidente, cuál de las tres causas aplicó, sustituyendo la explicación genérica del
aviso por información exacta.

## Risks / Trade-offs

- [El literal cambia y rompe aserciones en otros tests] → Mitigación: `grep` acota las referencias al
  fragmento previo antes de tocar; la única prueba que fija el literal es `index.aviso.test.tsx`.
- [Redacción demasiado larga para el banner de una línea] → Mitigación: se mantiene un único párrafo
  conciso (dos oraciones); el contenedor ya permite múltiples líneas (`flex items-start`).
- [Que la nueva redacción reintroduzca un nombre de modelo] → Mitigación: aserciones que prohíben
  "gemini"/"flash" se conservan en la prueba.

## Migration Plan

- No hay migración de datos ni de esquema. El cambio es textual y de spec, y se despliega con el
  bundle del frontend.
- Rollback: `git revert` del commit del change (ver `proposal.md`, Rollback Plan).

## Open Questions

Ninguna. La redacción final queda fijada en D1 (se resuelve ahora porque es el contrato que fija el
requisito FRH-010 y la prueba; no se difiere a apply).
