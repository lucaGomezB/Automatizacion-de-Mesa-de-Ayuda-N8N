# Design: Clasificador supervisado sobre el corpus acumulado

## Context

La referencia fuera de muestra del híbrido congelado es `0,6893` (`142/206`,
Sección 3.25 del memo) y ningún ajuste incremental alcanza el umbral `0,85` sobre
esos `206` casos: harían falta `+34` aciertos, corregir los `30` errores de
`Sistemas` deja el techo en `0,835` y el brazo manual anota `0,8278` (estudio de
mejora del clasificador). La fuente dominante de error es la frontera
`Sistemas`↔`Soporte Tecnico Software` (`16` de `64` errores, `08-discusion.tex`).
La organización acumula decisiones validadas en `clasificacion_log`
(`sector_id_validado`, `sectores_validados`, `validado_por_empleado_id`,
`intervencion_inicio_en`, `validado_en`, `origen_intervencion`; migración `024`),
que constituyen el activo informacional del escenario de mayor interés práctico
(limitación 5; `10-recomendaciones.tex::subsec:clasificador-supervisado`).

**Hechos del estado actual:**

- Los `206` casos (corpus arbitrado) son la referencia retenida; el corpus de
  ajuste son los `200` in-sample. No hay corpus supervisado propio.
- El codebook de etiquetado está congelado en
  `evaluation/data/campana/codebook_doble_etiquetado.md`, con la taxonomía de
  `openspec/specs/sector-taxonomy/spec.md` (`TAX-001`, `TAX-004`).
- El pipeline de inferencia de producción y el prompt vigente no se tocan.
- La línea **depende de datos que todavía no existen** (volumen acumulado) y de
  etiquetado humano con consentimiento; el volumen indicativo es el de la Sección
  de implicancias prácticas (orden de `5.000`, referencia indicativa, no derivada).

## Goals / Non-Goals

**Goals:**

- Entregar la maquinaria reproducible: curación del corpus acumulado, política de
  partición sin fuga, arnés de entrenamiento tipo BERT y benchmark de modelos
  abiertos, revisión del codebook de la frontera y protocolo del corpus de
  prevalencia natural.
- Dejar el registro honesto: la línea depende de datos inexistentes y de
  consentimiento, y `0,85` no es alcanzable sobre la referencia de `206`.
- Dejar cada artefacto con procedencia, prueba y comando reproducible.

**Non-Goals:**

- Entrenar y publicar un modelo de producción si el corpus no alcanza el volumen.
- Cambiar el clasificador de producción, el prompt vigente o las cinco cadenas
  canónicas (`TAX-001`).
- Cambiar `0,6893`, el macro-F1 `0,7024` ni el veredicto del umbral `0,85`.
- Reejecutar la campaña, invocar a Gemini o ejecutar llamadas pagas.
- Resolver las limitaciones que exigen otra organización o más etiquetadores
  independientes.

## Decisions

### D1 — Dos horizontes: maquinaria ahora, entrenamiento condicionado

El change entrega la **maquinaria** (curación, partición, arnés, codebook,
protocolo) y el **registro honesto**, no un modelo entrenado. El entrenamiento
real queda condicionado a que el corpus acumulado alcance el volumen y el
consentimiento; el arnés se prueba con un fixture sintético reducido y con las
particiones del corpus disponible. Alternativa descartada: entrenar y publicar un
modelo ahora, porque el corpus no existe y presentaría sobre `206` un resultado
que la propia tesis declara no alcanzable.

### D2 — Contrato de curación desde `clasificacion_log`

Un exportador de solo lectura emite un corpus candidato con, por caso:

| Campo | Origen | Regla |
|---|---|---|
| `texto` | `incidente.descripcion` | pseudonimizado con `scripts/corpus_ingest/pseudonymize_corpus.py` |
| `sector_validado` | `clasificacion_log.sector_id_validado` | solo no nulo |
| `sectores_validados` | `clasificacion_sector_validado` | multietiqueta validada |
| `etapa`, `confianza` | `clasificacion_log` | se descartan `fallback` y `confianza = 0.0` |
| `origen_intervencion` | `clasificacion_log` | `gate` \| `muestreo` \| `rederivacion` \| `completado_manual` |
| metadatos | `intervencion_inicio_en`, `validado_en` | trazabilidad, pseudonimizados |

El corpus curado es **inmutable y versionado** (JSON con `schema_version` y
`metadata`, UTF-8 sin BOM, LF). Se deduplica contra los `206` con
`evaluation.no_solape.verificar_no_solape` y se descartan duplicados internos por
texto normalizado. Si se requiere una tabla o columna nueva, es una migración con
checkpoint humano (Bloque A, ALTA). Cumple `supervised-corpus-curation`.

### D3 — Partición disjunta sin fuga, con los `206` retenidos

Partición `train`/`dev`/`test` con: agrupamiento por texto casi duplicado (un
mismo incidente no cae en dos particiones), estratificación por sector y canal, y
**retención permanente de los `206`** (nunca entrenan). `dev` solo para parada
temprana y selección; `test` se usa una vez. Una prueba demuestra que la
intersección de textos entre particiones es vacía y que ningún id de los `206`
aparece en `train`/`dev`/`test`. Función pura con prueba sintética antes de
implementar. Cumple `supervised-classifier-benchmark` (SCB-001).

### D4 — Modelo tipo BERT y benchmark de modelos abiertos

- Encoder BERT de dominio español/multilingüe (`BETO` o `xlm-roberta`) ajustado
  por clasificación de secuencia.
- Modelos abiertos (`Llama 3`, `Mistral`, `Qwen`) evaluados con `prompts` y, si el
  volumen lo permite, con `LoRA`; contra el híbrido congelado como base.
- Métricas: exactitud estricta y laxa, macro-F1 y P/R/F1 por clase con soporte,
  reutilizando `evaluation/metrics.py`; `n` de entrenamiento y de prueba separados.
- Lectura sobre los `206` solo como contraste descriptivo, con el rótulo de que
  `0,85` **no** es alcanzable sobre esa referencia. Balanza por prevalencia
  natural cuando corresponda. Cumple `supervised-classifier-benchmark` (SCB-002,
  SCB-003).

### D5 — Revisión del codebook de la frontera `Sistemas`↔`Software`

Se revisan las definiciones de `Sistemas` y `Soporte Tecnico Software` en
`evaluation/data/campana/codebook_doble_etiquetado.md` y el criterio de frontera.
El criterio de éxito es la **proporción de casos asignados a una sola clase**
tras la revisión (menor ambigüedad), medida sobre una muestra de casos limítrofes
del corpus disponible. La actualización de `TAX-004` (reglas del prompt) se
**propone** y solo se aplica con aprobación de los autores; no se cambian las
cinco cadenas canónicas. Cumple `taxonomy-codebook-revision`.

### D6 — Corpus de prevalencia natural

El corpus de evaluación fresco se **consume** de `c-229` (muestreo probabilístico
del universo): cuotas prefijadas por canal y sector, etiquetado limpio e
independiente, sin solape con el corpus de ajuste. La evaluación no excluye casos
y reporta intervalos sobre el universo (`evaluation/stats.py`). Si `c-229` no
entrega el corpus, esta tarea queda bloqueada y se registra. Cumple
`natural-prevalence-evaluation-corpus`.

### D7 — Prosa de la tesis y memo aditivo

- `10-recomendaciones.tex::subsec:clasificador-supervisado` y
  `subsec:frontera-sistemas`: declarar que la línea depende de datos que no
  existen y de consentimiento, y que `0,85` no es alcanzable sobre los `206`; el
  umbral de volumen sigue declarado como referencia indicativa (requisito vigente).
- `08-discusion.tex` (limitación correspondiente): precisar el alcance.
- `numeros-canonicos.md`: sección aditiva `3.41` (primera libre tras la `3.37`) con
  los anclajes (`0,6893/206`, `+34`, techo `0,835`, manual `0,8278`, frontera
  `16/64`), su procedencia y su estado (`reinterpretación`/`condicional`); declara
  que no mide de nuevo y que no cambia valores vigentes.

### D8 — Gobernanza y checkpoints

Bloque ALTA (datos nuevos, datos personales y entrenamiento). Checkpoints
humanos obligatorios antes de: (1) tocar el esquema de `clasificacion_log` o crear
tablas; (2) exportar o etiquetar datos reales (consentimiento); (3) entrenar o
publicar cualquier modelo. Sin bloque LOW. Cero llamadas pagas.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| El corpus no alcanza el volumen | El change entrega la maquinaria y declara el bloqueo; el entrenamiento queda condicionado |
| Exportar datos sin consentimiento | Bloque ALTA con checkpoint antes de datos reales; reutiliza el pseudonimizador vigente |
| Fuga de los `206` en el entrenamiento | Prueba de partición disjunta; los `206` y `test` nunca entrenan |
| La revisión del codebook no mejora | Criterio de éxito medido; se reporta aunque no reduzca la ambigüedad |
| Leer `206` como validación del supervisado | Rótulo explícito; no alcanzabilidad del `0,85` declarada |
| Deriva del corpus acumulado | Corpus inmutable versionado con SHA-256 y procedencia |
| Crecimiento de páginas | Prosa acotada; verificar `\@abspage@last` |

## Migration Plan

1. Preparación y línea de base (tareas 0).
2. Curación del corpus (tareas 1), con checkpoint de esquema/consentimiento.
3. Partición y arnés (tareas 2).
4. Taxonomía y codebook (tareas 3).
5. Corpus de prevalencia natural (tareas 4, condicionado a `c-229`).
6. Prosa y memo (tareas 5).
7. Verificación de cierre (tareas 6).

Rollback: `git revert` del commit; todos los artefactos son aditivos y no se toca
el clasificador de producción ni valores canónicos vigentes.

## Open Questions

- **OQ1 (autores, aplica a tareas 1-2)**: ¿cuál es el volumen mínimo del corpus
  acumulado para habilitar el entrenamiento real y qué modelo base se elige
  (`BETO` vs `xlm-roberta`)? Se resuelve al aplicar, no cambia specs ni aprobación.
- **OQ2 (autores, aplica a tarea 3)**: ¿se aplica la actualización de `TAX-004`
  dentro de este change o se difiere a un change propio tras la revisión del
  codebook? Por defecto se propone y se difiere.
- **OQ3 (aplicación, tarea 4)**: ¿entrega `c-229` el corpus de prevalencia natural
  a tiempo? Si no, la tarea queda bloqueada y se registra.
