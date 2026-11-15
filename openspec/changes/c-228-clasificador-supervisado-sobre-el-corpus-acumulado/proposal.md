# Proposal: Clasificador supervisado sobre el corpus acumulado

## Why

La limitación 5 deja sin medir el escenario de mayor interés práctico: un
clasificador supervisado entrenado con el corpus que la organización acumula al
validar decisiones en `clasificacion_log`. La referencia fuera de muestra del
híbrido es `0,6893` (`142/206`), por debajo del umbral `0,85`, y ningún ajuste
incremental lo alcanza sobre esos `206` casos: harían falta `+34` aciertos, aun
corrigiendo los `30` errores de `Sistemas` se llega a `0,835` y el brazo manual
anota `0,8278` sobre la misma referencia. La fuente dominante de error es la
ambigüedad de la frontera `Sistemas`↔`Soporte Tecnico Software` (`16` de `64`
errores). La vía con recorrido real es acumular miles de decisiones validadas,
entrenar un modelo tipo BERT y fijar el codebook de esa frontera, validando sobre
un corpus de prevalencia natural. Las propias líneas de trabajo futuro de la tesis
(`subsec:clasificador-supervisado`, `subsec:frontera-sistemas`,
`subsec:evaluacion-modelos-abiertos`) lo enuncian pero no lo instrumentan.

Este change entrega la maquinaria y el registro honesto, no un modelo entrenado:
la línea **depende de datos que todavía no existen y de etiquetado humano con
consentimiento**, y sobre la referencia actual de `206` casos el umbral `0,85` **no
es alcanzable**.

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **A. Curación del corpus** | Pipeline de solo lectura que exporta y cura decisiones validadas de `clasificacion_log` (consentimiento y pseudonimización), deduplica contra los `206` y versiona un corpus inmutable con procedencia. | ALTA |
| **B. Partición y arnés** | Política de partición train/dev/test sin fuga (los `206` quedan retenidos) y arnés reproducible de entrenamiento tipo BERT más benchmark de modelos abiertos (Llama 3 / Mistral / Qwen) contra el híbrido. | ALTA |
| **C. Taxonomía y codebook** | Revisión de las definiciones de `Sistemas` y `Soporte Tecnico Software` y del criterio de frontera; medición de la proporción de casos asignados a una sola clase. Propone, sin aplicar, la actualización de `TAX-004`. | MEDIA |
| **D. Corpus de prevalencia natural** | Diseño y consumo de un corpus fresco, limpio y de prevalencia natural con cuotas prefijadas, con intervalos sobre el universo y sin excluir casos. Depende de c-229. | ALTA |
| **E. Tesis y memo** | Prosa honesta en `10-recomendaciones.tex` y en la limitación, y sección aditiva del memo canónico con los anclajes y el techo sobre los `206`. | BAJA/MEDIA |

**No objetivos.**

- No se modifica el clasificador de producción, el prompt vigente ni las cinco cadenas canónicas.
- No se entrena ni publica un modelo si el corpus no alcanza el volumen; se entrega la maquinaria y se registra el bloqueo.
- No cambian `0,6893`, el macro-F1 `0,7024` ni el veredicto del umbral `0,85`.
- No se reejecuta la campaña, no se invoca a Gemini y no hay llamadas pagas.
- No se duplican ni se reetiquetan los `206` casos de referencia.

## Capabilities

### New Capabilities

- `supervised-corpus-curation`: acumulación y curación de decisiones validadas de `clasificacion_log`, con consentimiento, pseudonimización, no solape con los `206` y corpus inmutable versionado.
- `supervised-classifier-benchmark`: partición disjunta sin fuga, entrenamiento de un modelo tipo BERT, benchmark de modelos abiertos, métricas por clase y comparación con el híbrido.
- `taxonomy-codebook-revision`: revisión del codebook de la frontera `Sistemas`↔`Soporte Tecnico Software` y medición de la ambigüedad de etiquetado.
- `natural-prevalence-evaluation-corpus`: corpus fresco de prevalencia natural, etiquetado limpio e independiente, evaluación sin exclusiones con intervalos sobre el universo.

### Modified Capabilities

- `tesis-document`: se agrega el requisito del estado honesto del clasificador supervisado como trabajo futuro dependiente de datos y de la no alcanzabilidad del `0,85` sobre los `206`.
- `tesis-numeros-canonicos`: se agrega el requisito de registro aditivo de los anclajes del clasificador supervisado y del techo sobre los `206`.

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/` | Nuevo | Curación del corpus y arnés de partición/entrenamiento (módulos y pruebas) |
| `evaluation/data/` | Nuevo | Corpus curado versionado y particiones |
| `App/Backend/app/models/clasificacion_log.py` | Posible (migración) | Solo si la curación exige metadatos nuevos; checkpoint humano |
| `evaluation/data/campana/codebook_doble_etiquetado.md` | Modificado | Definiciones de la frontera `Sistemas`↔`Software` |
| `openspec/specs/sector-taxonomy/spec.md` (`TAX-004`) | Diferido | Se propone la actualización; se aplica solo con aprobación de los autores |
| `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` | Modificado | Dependencia y no alcanzabilidad en las líneas futuras |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | Precisión de la limitación correspondiente |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Sección nueva con anclajes y procedencia |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |

Sin cambios en el prompt vigente, las cinco cadenas canónicas ni las predicciones congeladas. Cero llamadas a Gemini.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| El corpus acumulado no alcanza el volumen para entrenar | Alta | El change entrega la maquinaria y declara el bloqueo; el entrenamiento queda condicionado al volumen |
| Exportar datos sin consentimiento ni pseudonimización | Media | Bloque ALTA con checkpoint humano antes de tocar datos reales; se reutiliza el pseudonimizador vigente |
| Fuga de los `206` en el entrenamiento | Media | Partición disjunta verificada por prueba; los `206` y el corpus de prueba nunca entrenan |
| La revisión del codebook no reduce la ambigüedad | Media | Criterio de éxito medido (proporción de asignación a una sola clase); se reporta aunque no mejore |
| Sobreactuar sobre `206` presentándolo como validación | Alta | Rótulo explícito; se declara que `0,85` no es alcanzable sobre esa referencia |
| Crecer en páginas en la tesis | Media | Prosa acotada; verificación de `\@abspage@last` |

## Rollback Plan

`git revert` del commit del change: los módulos, corpus y particiones son aditivos; el codebook se revierte por archivo; la sección del memo se retira sin tocar las anteriores; la prosa y la trazabilidad se revierten por archivo. No se modifica el clasificador de producción ni ningún valor canónico vigente, de modo que el rollback no deja huecos numéricos.

## Dependencies

- `c-229-muestreo-probabilistico-del-universo-de-incidentes` (corpus de prevalencia natural).
- `c-227-monitorear-el-servicio-de-inferencia-y-la-deriva-del-modelo` (vigilancia en operación, relacionada).
- `evaluation/data/campana/codebook_doble_etiquetado.md` y `evaluation/data/campana/` (insumos de etiquetado).
- Líneas de trabajo futuro de `10-recomendaciones.tex` y `paket2024itservice` (BERT sobre LLM abiertos en clasificación de tickets).

## Success Criteria

- [ ] El pipeline de curación extrae solo decisiones validadas y consentidas, pseudonimiza, no solapa los `206` y emite un corpus inmutable con procedencia.
- [ ] La partición train/dev/test es disjunta, estratifica por sector y canal y retiene los `206`; una prueba demuestra que no hay fuga.
- [ ] El arnés entrena un modelo tipo BERT y evalúa modelos abiertos contra el híbrido, con métricas por clase y `n` de entrenamiento y de prueba separados.
- [ ] La revisión del codebook reduce o mide la ambigüedad de la frontera `Sistemas`↔`Software` con su proporción reportada.
- [ ] El corpus de prevalencia natural se evalúa sin exclusiones, con intervalos sobre el universo y su dependencia de c-229 declarada.
- [ ] `10-recomendaciones.tex` y la limitación declaran que la línea depende de datos inexistentes y de consentimiento, y que `0,85` no es alcanzable sobre los `206`.
- [ ] `openspec validate c-228-clasificador-supervisado-sobre-el-corpus-acumulado --strict` pasa.
