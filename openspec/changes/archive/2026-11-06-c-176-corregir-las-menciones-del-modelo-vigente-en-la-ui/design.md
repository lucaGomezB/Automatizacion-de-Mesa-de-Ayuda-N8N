## Context

Ver `proposal.md` (Why). Estado actual y restricciones que condicionan el enfoque:

- El modelo vigente del backend es `gemini-3.6-flash` (`App/Backend/app/config/settings.py:78`,
  `Settings.gemini_model`), consumido por `App/Backend/app/classifiers/gemini_classifier.py`.
- El frontend tiene la versión retirada hardcodeada en dos lugares de la UI
  (`utils/formatters.ts:70`, `pages/ReportarIncidente/index.tsx:77`) y en dos comentarios
  (`utils/formatters.ts:10`, `utils/validators.ts:10`).
- La etapa del pipeline es un valor de enum estable: `deterministic | gemini | fallback`
  (`tips/clasificacion`). La etiqueta se centraliza en `formatearEtapa` (`utils/formatters.ts`).
- `frontend-revision-humana` FRH-003/FRH-004 ya exigen mostrar "etapa del pipeline"; FRH-010 ya
  exige que el AVISO de la pestaña "Revisión Humana" sea agnóstico al modelo (y ya cumple). La
  etiqueta de etapa y el texto del portal NO tenían contrato propio.
- No existe un canal automático entre `Settings.gemini_model` (backend, Python) y el frontend
  (SPA React empacada); el nombre del modelo no viaja en ninguna respuesta del API.

## Goals / Non-Goals

**Goals:**

- Que la UI deje de presentar una versión retirada del modelo como vigente.
- Que la corrección sea robusta frente a futuros cambios de modelo (que no vuelva a quedar obsoleta).
- Preservar intactas las menciones históricas rotuladas.

**Non-Goals:**

- No cambiar el modelo ni los parámetros del backend.
- No introducir un endpoint ni un contrato API para exponer el nombre del modelo al frontend.
- No modificar el banner de "Revisión Humana" (FRH-010, ya cumplido).
- No tocar textos históricos (knowledge-base, settings.py, evaluation, foundation-environment, CHANGES.md).

## Decisions

### D1 — Etiqueta de la UI: agnóstica (Approach A) frente a nombre vigente (Approach B)

**Decisión: Approach A — agnóstico a la versión.** La etapa `gemini` se rotula "Gemini" y el texto
del portal deja de nombrar una versión.

Fundamento:

1. La etapa del pipeline es un valor de enum. La etiqueta debe describir la ETAPA, no una versión
   de un modelo. Las otras dos etiquetas ("Determinístico", "Sin clasificar") no nombran versiones;
   "Gemini" es la etiqueta paralela correcta.
2. No existe sincronización automática posible dentro del alcance: el nombre del modelo vive en
   `Settings.gemini_model` (Python) y el frontend se empaca como SPA. Approach B exigiría o bien
   duplicar el literal en el frontend (reintroduciendo la deriva que este change corrige) o bien
   agregar un endpoint/build-time env (fuera de alcance y comportamiento nuevo).
3. Es consistente con el espíritu de FRH-010: un cambio de modelo no debe dejar el texto obsoleto.

Alternativa considerada — **Approach B (nombre vigente desde una única fuente):** mostrar
"Gemini 3.6 Flash" tomado de una fuente única. Única fuente posible dentro del alcance:
`openspec/config.yaml` (`stack.inference.model`), que ya declara el valor y se verifica por
coincidencia con `Settings.gemini_model` (DOC-005). Trade-off: aunque evita la duplicación dentro
del repo, el frontend NO puede leer `openspec/config.yaml` en runtime (es configuración de
herramientas, no un artefacto servido), de modo que habría que copiar el literal a una constante
del frontend o generarla en build. Cualquiera de las dos copias puede divergir de
`Settings.gemini_model` sin que nada lo detecte (la barrera `docs_stack_sync` vigila documentación
y `requirements.txt`, no el bundle del frontend). Se descarta por alto riesgo de re-deriva y por
introducir una dependencia de build no prevista.

### D2 — Dónde vive el contrato: nueva capability frente a modificar `frontend-revision-humana`

**Decisión: nueva capability `frontend-model-mentions`.**

Fundamento:

- El contrato abarca dos superficies de capabilities distintas: la etiqueta de etapa (mayormente
  en las superficies de revisión humana) y el texto del portal de reporte (formulario de usuario
  final), que NO pertenece a `frontend-revision-humana`.
- FRH-010 ya cubre el banner y permanece sin cambios; no se modifica una capability existente.
- Una capability dedicada da un único hogar semántico ("menciones del modelo en la UI") y evita
  estirar el alcance de `frontend-revision-humana` hacia el portal de reporte.

Alternativa considerada: agregar una FRH-011 a `frontend-revision-humana` (como hizo c-85 con
FRH-010). Se descarta porque la superficie del portal de reporte quedaría fuera de alcance de esa
capability, generando una discrepancia nombre-contenido.

### D3 — Menciones históricas preservadas

**Decisión: no tocar las menciones históricas.** La calibración de parámetros sobre Gemini 2.5 Flash
(DD-04) y su rastro en `settings.py:73`, `evaluation/**`, `tests/test_gemini_generation_config.py`,
`foundation-environment/spec.md` y `CHANGES.md` son hechos rotulados y se conservan. `CHANGES.md:2242`
prohíbe el reemplazo ciego "2.5" -> "3.6"; el alcance se limita a las menciones que la UI presenta
como VIGENTES.

### D4 — Estrategia de prueba (TDD estricto)

**Decisión: TDD con la etiqueta como contrato primario.** La etiqueta se prueba a nivel unitario
sobre `formatearEtapa` (función pura) y a nivel de componente en las dos pruebas que hoy fijan el
literal. El texto del portal se prueba en `ReportarIncidente/index.test.tsx` (ya existe y renderiza
la página). Runner: `cd App/Frontend; npm run test` (Vitest).

## Risks / Trade-offs

- [Deriva futura del nombre del modelo en otras superficies no cubiertas] -> Mitigación: el `grep`
  de alcance en la tarea 1.2 y la redacción agnóstica evitan el literal; si aparece una superficie
  nueva, cae bajo el mismo contrato de la capability.
- [Que un reviewer prefiera el nombre vigente visible (Approach B)] -> Mitigación: D1 documenta el
  trade-off; revertir a B es un cambio textual acotado, pero reabre el riesgo de deriva.
- [Falsos positivos de `grep` que arrastren menciones históricas] -> Mitigación: lista explícita de
  archivos fuera de alcance en el proposal, confirmada por tarea 5.1.

## Migration Plan

- No hay migración de datos ni de esquema. El cambio es textual y se despliega con el bundle del
  frontend.
- Rollback: `git revert` del commit del change (ver proposal.md, Rollback Plan).

## Open Questions

- Redacción final del texto del portal: mantener "(Gemini)" sin versión o eliminar por completo la
  mención al proveedor y describir solo "clasificación automática". Es una decisión editorial que no
  altera el contrato (agnóstico a la versión) ni el desglose de tareas; se resuelve en apply.
