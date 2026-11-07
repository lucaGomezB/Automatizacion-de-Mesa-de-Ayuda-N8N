## Context

Ver `proposal.md` (Why). Estado actual y restricciones que condicionan el enfoque:

- La etiqueta de la etapa del pipeline se centraliza en `formatearEtapa`
  (`App/Frontend/src/utils/formatters.ts:67`). La etapa es un valor de enum estable:
  `deterministic | gemini | fallback`. Hoy `gemini` se rotula "Gemini" (fijado por c-176).
- Todas las superficies que muestran la etapa la obtienen de `formatearEtapa`: `DetalleIncidente.tsx`,
  `RevisionHumanaTable.tsx`, `ValidarClasificacionDialog.tsx` y `ReportarIncidente/SuccessCard.tsx`.
  No hay etiquetas de etapa hardcodeadas fuera de `formatearEtapa`.
- El texto informativo del portal de reporte (`App/Frontend/src/pages/ReportarIncidente/index.tsx:77`)
  menciona hoy al proveedor entre paréntesis: "inteligencia artificial (Gemini)".
- La capability `frontend-model-mentions` ya existe (creada por c-176) y cubre la etiqueta de etapa y
  el texto del portal. Este change MODIFICA esos dos requisitos; no crea capability nueva.
- El frontend es una SPA React empacada; el nombre del proveedor/modelo no viaja en ninguna respuesta
  del API. No existe canal automático entre `Settings.gemini_model` (backend) y la UI.

## Goals / Non-Goals

**Goals:**

- Que la etiqueta de la etapa `gemini` sea plenamente agnóstica al proveedor y a la versión
  ("Análisis por IA"), para que ni un cambio de modelo ni de proveedor deje la UI obsoleta.
- Que el texto del portal deje de nombrar al proveedor, sin alterar el aviso del umbral del 70%.
- Preservar "Determinístico" y "Sin clasificar" (paralelismo semántico: describen la etapa, no un
  proveedor) y el comportamiento de etapa desconocida (devolver tal cual).

**Non-Goals:**

- No cambiar el valor del enum `etapa` ni el contrato del backend/API.
- No introducir un endpoint ni un contrato para exponer el modelo al frontend.
- No tocar el banner de "Revisión Humana" (FRH-010, ya cumplido) ni la etiqueta "Sector Asignado por IA".
- No tocar menciones históricas rotuladas (knowledge-base, `settings.py`, `evaluation/**`,
  `foundation-environment/spec.md`, `CHANGES.md`).

## Decisions

### D1 — Etiqueta de la etapa `gemini`: "Análisis por IA"

**Decisión: rotular la etapa `gemini` como "Análisis por IA" (con acento).**

Fundamento:

1. El objetivo es la máxima agnosticidad: el rótulo describe la ETAPA de análisis, no al proveedor ni
   al modelo. "Gemini" seguía dependiendo de que el proveedor no cambie; "Análisis por IA" no.
2. Coherencia interna: `deterministic` -> "Determinístico" y `fallback` -> "Sin clasificar" describen
   la etapa/mecanismo, no un producto; "Análisis por IA" es la etiqueta paralela para la etapa `gemini`.
3. Sin acoplamiento de build: no requiere leer configuración del backend ni generar constantes en
   build (el problema de sincronización documentado por c-176 D1 sigue vigente).

Alternativas consideradas:

- **Mantener "Gemini" (c-176):** se descarta porque sigue nombrando al proveedor y reabre la deriva si
  el proveedor cambia.
- **"Análisis por IA" vs "Clasificación por IA" vs "IA":** "Análisis por IA" es descriptiva y no
  colisiona con otras etiquetas de la UI ("clasificación automática" ya se usa en textos del portal y
  del detalle, por lo que "Análisis por IA" evita ambigüedad); "IA" sola es demasiado escueta.

### D2 — Texto del portal: eliminar "(Gemini)" en lugar de reemplazarlo por otra mención

**Decisión: quitar por completo el paréntesis "(Gemini)"** del texto de `ReportarIncidente/index.tsx`,
de modo que diga "...lo clasificará automáticamente mediante inteligencia artificial." sin nombrar
proveedor.

Fundamento:

1. Reemplazar "(Gemini)" por otra frase neutral ("un modelo de IA") duplicaría "inteligencia artificial"
   ya presente en la misma oración.
2. Eliminar la mención es la opción más simple y consistente con el objetivo de agnosticidad al proveedor.
3. El aviso del umbral del 70% vive en la nota informativa separada (`data-testid="nota-clasificacion"`)
   y NO se modifica.

Alternativa considerada: conservar "(Gemini)" sin versión (estado actual de c-176). Se descarta por el
objetivo del change.

### D3 — Pruebas: TDD estricto sobre la función pura + aserciones de componente

**Decisión: TDD con la etiqueta como contrato primario.** `formatearEtapa` es una función pura; se
prueba a nivel unitario (happy path + triángulo con las otras dos etapas y etapa desconocida). Las
aserciones de componente que hoy fijan "Gemini" (`DetalleIncidente.test.tsx`, `ValidarClasificacionDialog.test.tsx`)
se actualizan a "Análisis por IA". El texto del portal se prueba en `ReportarIncidente/index.test.tsx`
(invierte las aserciones actuales `/Gemini/` y `/\(Gemini\)/` a que NO nombren proveedor). Runner:
`cd App/Frontend; npm run test <path>` (Vitest).

Nota de cobertura: `App/Frontend/vitest.config.ts` excluye de cobertura `src/components/ui/**` y
`src/components/layout/**` (quirk documentado en `AGENTS.md`). Los archivos de este change
(`utils/formatters.ts` y `pages/ReportarIncidente/index.tsx`) NO están excluidos, por lo que sus
ramas quedan cubiertas por las pruebas.

## Risks / Trade-offs

- [Otra superficie hardcodea "Gemini" fuera de `formatearEtapa`] -> Mitigación: `grep` de alcance en la
  tarea 1.2 acota el conjunto real antes de tocar; verificación final en la tarea 5.2.
- [El cambio de etiqueta rompe aserciones existentes] -> Mitigación: las pruebas que fijan el literal se
  actualizan dentro del mismo change (tareas 3.x y 4.x).
- [Pérdida de información para el usuario (ya no ve que usa IA de un proveedor reconocido)] -> Mitigación:
  se conserva "inteligencia artificial" en el texto del portal y "Sector Asignado por IA" en la tarjeta;
  la agnosticidad al proveedor es una decisión editorial deliberada.

## Migration Plan

- Cambio puramente textual en el bundle del frontend. No hay migración de datos ni de esquema.
- Rollback: `git revert` del commit del change (ver `proposal.md`, Rollback Plan).
- Despliegue: como el frontend corre desde una imagen horneada, el rótulo se vuelve visible con
  `docker compose up -d --build frontend` (tarea de deploy, manual).

## Open Questions

None.
