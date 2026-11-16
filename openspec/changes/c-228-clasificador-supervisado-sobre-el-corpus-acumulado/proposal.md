# Proposal: Clasificador supervisado sobre el corpus acumulado

## Adaptación a la devolución de tercera instancia (16/11/2026)

Este change lo propuso un coautor el 15/11/2026, un día antes de la devolución de
tercera instancia (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`),
con 0 tareas aplicadas. Se reformula; no se crea de cero.

**Premisa que cayó.** La versión anterior se apoyaba en la validación fuera de
muestra (corpus independiente de 150 casos más 56 de refuerzo, 206 en total,
etiquetado por E3/E4 y arbitrado por E5): usaba como ancla `0,6893` (`142/206`),
el macro-F1 `0,7024`, el techo `+34` / `0,835` sobre los 206, los `30 errores` y
los `16 de 64` de `Sistemas`; retenía los 206 como conjunto de prueba y hasheaba
`doble_etiquetado_arbitrado.csv`. Los autores **retiran** esa evidencia del
ejemplar; el motivo y el alcance del retiro los fija `c-235` (no se reformulan
aquí). Todas esas cifras y artefactos quedan **retirados** y este change ya no los
usa como ancla, insumo, conjunto retenido ni comparador. Tampoco sostiene la
afirmación de que el brazo manual anota `0,8278` «sobre la misma referencia» que
los 206: ese valor se midió contra el consenso E1/E2 de la campaña complementaria
(`07-resultados.tex:383`, 125 de 151 derivaciones sobre 138 casos únicos), es
decir, sobre otra referencia; se retira de este change porque no es un anclaje
del clasificador supervisado.

**Qué se conserva.** El núcleo sobre `clasificacion_log`: curación (SCC),
partición y arnés (SCB), revisión del codebook de la frontera
`Sistemas`↔`Soporte Tecnico Software` (TCR) y consumo del corpus de `c-229` (NPE).

**Qué cambia.**

- El conjunto de prueba retenido es el **corpus probabilístico acreditado** que
  entrega `c-229` con la referencia por mayoría de `c-230`. Mientras no exista,
  solo se admite una partición retenida de `clasificacion_log`, rotulada como
  **interna** (no es una validación externa).
- Se agregan dos compuertas previas a todo dato nuevo: **procedencia (K-01)** y
  **ética y legal (K-02)**, y la declaración de dónde corre cada modelo.
- La línea base de la frontera sale del doble etiquetado E1/E2 sobre los 200
  casos; el «después» exige etiquetado nuevo bajo compuertas.
- El trabajo hecho con asistentes de IA se registra en el inventario de `c-237`
  (A-03).
- La sección del memo conserva el número reservado `3.41` y registra solo
  resultados con compuertas cerradas.

**Búsqueda de control de cifras y alias retirados** (tarea 6.3 y criterio de
aceptación de esta adaptación):
`rg -n "206|0,6893|0,7489|0,7024|0,835|142/206|16 de 64|E3|E4|E5|arbitrado|fuera de muestra|corpus independiente" <ruta>`.
Sobre este change solo debe devolver líneas de esta sección o del bloque
equivalente de `design.md`.

**Alcance respecto de la entrega.** Por defecto (decisión abierta a los autores,
OQ7) este change **no modifica el ejemplar que se defiende**. Se ejecuta después del
cierre de la entrega (`c-235` → `c-236` → `c-237` → `c-238` → `c-239`), en el orden
`c-229` → `c-230` → `c-228` → `c-232`. Hasta entonces la tesis lo menciona solo como
trabajo futuro, en los términos que fija `c-235` (requisito «Validacion fuera de
muestra propuesta como trabajo futuro con procedencia acreditable»). El tribunal
no pidió un clasificador supervisado y declaró que ninguna corrección exige código
nuevo; este change no responde a ninguna observación de la devolución.

## Why

La tesis enuncia como trabajo futuro un clasificador supervisado entrenado con las
decisiones validadas que la organización acumula en `clasificacion_log`
(`10-recomendaciones.tex`, `subsec:clasificador-supervisado`), la medición de la
frontera `Sistemas`↔`Soporte Tecnico Software` (`subsec:frontera-sistemas`) y la
evaluación de modelos abiertos (`subsec:evaluacion-modelos-abiertos`), pero no los
instrumenta.

Lo verificado sobre el corpus de 200 casos (`data/corpus_evaluacion_pseudonimizado.json`)
explica por qué la línea depende de datos nuevos:

- La composición por sector es `Soporte Tecnico Hardware` 85, `Soporte Tecnico
  Software` 67, `Seguridad Informatica` 31, `Sistemas` 16 y `Bases de Datos` 1. Con
  16 casos de `Sistemas` y 1 de `Bases de Datos` no hay soporte para entrenar ni
  para medir esas clases.
- En el doble etiquetado E1/E2 (`evaluation/data/campana/doble_etiquetado.csv`) hay
  62 casos discordantes sobre 200, y 29 de ellos enfrentan exactamente `Sistemas`
  con `Soporte Tecnico Software`: la frontera es ambigua ya entre etiquetadores
  humanos.
- El híbrido se ajustó, en parte, con ese mismo corpus (`10-recomendaciones.tex:26`):
  toda lectura sobre los 200 es una estimación dentro de la muestra y **no** sirve
  para evaluar un clasificador nuevo ni para compararlo con el híbrido.

Este change entrega la maquinaria y el registro honesto, no un modelo entrenado:
la línea **depende de datos que todavía no existen**, de su **procedencia
acreditable** y de **autorización institucional y consentimiento**.

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **0. Compuertas** | Compuerta de procedencia (K-01) y compuerta ética y legal (K-02) previas a todo dato nuevo; declaración de dónde corre cada modelo y de todo envío de texto a terceros. | ALTA |
| **A. Curación del corpus** | Pipeline de solo lectura que cura decisiones validadas de un export crudo acreditado de `clasificacion_log` (pseudonimización), deduplica contra el corpus de 200 y contra el conjunto retenido, y versiona un corpus inmutable con procedencia. | ALTA |
| **B. Partición y arnés** | Partición train/dev/test sin fuga con el conjunto retenido fuera del entrenamiento; arnés reproducible tipo BERT y benchmark de modelos abiertos (Llama 3 / Mistral / Qwen) ejecutados localmente. | ALTA |
| **C. Taxonomía y codebook** | Revisión de la frontera `Sistemas`↔`Soporte Tecnico Software`; línea base de ambigüedad desde E1/E2 sobre los 200; «después» con etiquetado nuevo bajo compuertas. Propone, sin aplicar, la actualización de `TAX-004`. | MEDIA |
| **D. Corpus probabilístico acreditado** | Consumo del corpus de `c-229` con la referencia por mayoría de `c-230` como único conjunto de prueba retenido admisible. | ALTA |
| **E. Memo y tesis posterior** | Sección `3.41` del memo con resultados de compuertas cerradas; prosa de la tesis solo en una versión posterior a la defensa. Registro en el inventario de IA de `c-237`. | BAJA/MEDIA |

**No objetivos.**

- No se modifica el ejemplar que se defiende (salvo decisión contraria de los autores, OQ7).
- No se modifica el clasificador de producción, el prompt vigente ni las cinco cadenas canónicas.
- No se entrena ni publica un modelo si el corpus no alcanza el volumen o si alguna compuerta está abierta.
- No se usa ninguna cifra ni artefacto retirado por `c-235`.
- No se presenta una lectura sobre el corpus de 200 como evaluación del clasificador supervisado.
- No se invoca a Gemini ni se envía texto a terceros sin la compuerta K-02 cerrada.

## Capabilities

### New Capabilities

- `supervised-corpus-curation`: curación de decisiones validadas de un export crudo acreditado de `clasificacion_log`, con compuertas de procedencia y ética, pseudonimización, no solape con el corpus de 200 y con el conjunto retenido, y corpus inmutable versionado.
- `supervised-classifier-benchmark`: partición disjunta sin fuga, entrenamiento tipo BERT y benchmark de modelos abiertos ejecutados localmente, métricas por clase y contraste con el híbrido solo sobre el conjunto retenido admisible.
- `taxonomy-codebook-revision`: revisión del codebook de la frontera `Sistemas`↔`Soporte Tecnico Software`, con línea base E1/E2 sobre los 200 y medición posterior con etiquetado nuevo bajo compuertas.
- `natural-prevalence-evaluation-corpus`: consumo del corpus probabilístico acreditado de `c-229` con la referencia por mayoría de `c-230`, evaluación sin exclusiones e intervalos sobre el universo.

### Modified Capabilities

- `tesis-document`: se agrega el requisito de no modificar el ejemplar de la defensa por este change y de informar resultados del clasificador supervisado solo en una versión posterior y con compuertas cerradas.
- `tesis-numeros-canonicos`: se agrega el registro aditivo en la sección reservada `3.41`, limitado a valores con compuertas cerradas.

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/` | Nuevo | Curación, partición y arnés (módulos y pruebas con fixtures rotulados como sintéticos) |
| `evaluation/data/` | Nuevo (condicionado) | Corpus curado y particiones, solo con compuertas cerradas; hash SHA-256 del export crudo |
| `App/Backend/app/models/clasificacion_log.py` | Posible (migración) | Solo si la curación exige metadatos nuevos; checkpoint humano |
| `evaluation/data/campana/codebook_doble_etiquetado.md` | Modificado | Definiciones de la frontera `Sistemas`↔`Software` |
| `openspec/specs/sector-taxonomy/spec.md` (`TAX-004`) | Diferido | Se propone; se aplica solo con aprobación de los autores |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo (condicionado) | Sección reservada `3.41` |
| `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` | Aditivo | Registro A-03 del trabajo con asistentes de IA (archivo de `c-237`) |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |
| `docs/Tesis/v10 (IA)/paper/sections/*.tex` | Sin cambios en la entrega | Solo en una versión posterior a la defensa y con compuertas cerradas |

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Datos nuevos de procedencia no acreditable (repetir K-01) | Media | Compuerta de procedencia: export crudo, constancia de la organización en custodia del director, SHA-256, verificación previa del director |
| Uso de datos sin autorización ni base de licitud (repetir K-02) | Media | Compuerta ética y legal antes de extraer; declaración de dónde corre cada modelo y de todo envío a terceros |
| `clasificacion_log` sin filas reales de producción | Alta | OQ1; sin filas reales, el entrenamiento queda bloqueado y se registra |
| El corpus acumulado no alcanza el volumen | Alta | Se entrega la maquinaria y se declara el bloqueo |
| Leer el corpus de 200 como evaluación del supervisado | Alta | Rótulo explícito: el híbrido se ajustó con ese corpus; solo contraste descriptivo, nunca validación |
| Fuga del conjunto retenido al entrenamiento | Media | Partición disjunta verificada por prueba |
| Agregar evidencia nueva a la tesis sin poder acreditarla (el motivo de la baja de nota) | Alta | El ejemplar de la defensa no cambia; la prosa solo en versión posterior con compuertas cerradas |
| Fixtures sintéticos confundidos con datos reales | Media | Rotulado en nombre de archivo, cabecera y salida |

## Rollback Plan

`git revert` del commit del change: módulos, corpus y particiones son aditivos; el
codebook se revierte por archivo; la sección `3.41` del memo se retira sin tocar las
anteriores. No se modifica el clasificador de producción, ningún valor canónico
vigente ni el ejemplar de la defensa.

## Dependencies

- `c-235` a `c-239` cerrados (fin de la entrega), salvo decisión contraria de los autores (OQ7).
- `c-229-muestreo-probabilistico-del-universo-de-incidentes` (diseño, estimador y corpus probabilístico acreditado, con sus compuertas K-01 y K-02).
- `c-230-referencia-por-mayoria-con-etiquetadores-independientes` (funciones de mayoría y kappa de Fleiss y protocolo de referencia por mayoría para ese corpus).
- `c-237-declarar-de-forma-completa-el-uso-de-asistentes-de-ia` (inventario donde se registra A-03).
- `c-227-monitorear-el-servicio-de-inferencia-y-la-deriva-del-modelo` (relacionado; su canario no se usa como referencia, ver `c-235` OQ6).
- `evaluation/data/campana/codebook_doble_etiquetado.md` y `evaluation/data/campana/doble_etiquetado.csv` (E1/E2).
- `paket2024itservice` (BERT frente a LLM abiertos en clasificación de tickets).

## Success Criteria

- [ ] Las compuertas K-01 y K-02 quedan registradas como cerradas (con su evidencia) o como abiertas (con el bloqueo declarado) antes de tocar datos reales.
- [ ] El pipeline de curación extrae solo decisiones validadas de un export crudo acreditado, pseudonimiza, no solapa con el corpus de 200 ni con el conjunto retenido, y emite un corpus inmutable con procedencia.
- [ ] La partición es disjunta, estratifica por sector y canal y deja el conjunto retenido fuera del entrenamiento; una prueba demuestra que no hay fuga.
- [ ] Cada modelo declara dónde corre; ningún texto se envía a terceros sin K-02 cerrada.
- [ ] La línea base de ambigüedad de la frontera sale de E1/E2 sobre los 200; el «después» solo con etiquetado nuevo bajo compuertas.
- [ ] Ninguna cifra ni artefacto retirado por `c-235` aparece en Requirements, Scenarios ni tareas ejecutables.
- [ ] El trabajo con asistentes de IA queda registrado en el inventario de `c-237`.
- [ ] `openspec validate c-228-clasificador-supervisado-sobre-el-corpus-acumulado --strict` pasa.

## Open Questions (autores)

Ver `design.md`, sección Open Questions (OQ1 a OQ8).
