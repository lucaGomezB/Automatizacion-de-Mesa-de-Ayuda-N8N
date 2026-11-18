# Design: Clasificador supervisado sobre el corpus acumulado

## Adaptación a la devolución de tercera instancia (16/11/2026)

- **Premisa que cayó.** La versión del 15/11/2026 tomaba como referencia retenida
  los 206 casos del corpus independiente (150 más 56 de refuerzo, etiquetados por
  E3/E4 y arbitrados por E5) y como anclas `0,6893` (`142/206`), macro-F1 `0,7024`,
  `+34`, techo `0,835`, `30 errores` y `16 de 64` de `Sistemas`; la línea de base
  hasheaba `doble_etiquetado_arbitrado.csv`. Todo eso queda **retirado** del
  ejemplar por decisión de los autores; el motivo y el inventario del retiro están
  en `c-235` (proposal, design D2, D9, D10, OQ6, OQ8) y no se reformulan aquí.
- **Corrección de un hecho.** El `0,8278` del brazo manual se midió contra el
  consenso E1/E2 de la campaña complementaria (`07-resultados.tex:383`; memo
  `numeros-canonicos.md:786`), no «sobre la misma referencia» que los 206. El valor
  sobrevive en la tesis, pero no es un anclaje de este change y se quita de él.
- **Qué se conserva.** D2 (curación), D3 (partición), D4 (arnés y benchmark),
  D5 (codebook), D6 (consumo de `c-229`), D8 (checkpoints).
- **Qué cambia.** Conjunto retenido (D3, D6), compuertas K-01 y K-02 (D0), lugar de
  ejecución de los modelos (D4), línea base de la frontera (D5), memo con número
  reservado `3.41` y sin anclas retiradas (D7), registro A-03 (D9), alcance (D10).
- **Alcance respecto de la entrega.** Por defecto no se modifica el ejemplar que se
  defiende; el change se ejecuta después de `c-239`, en el orden `c-229` → `c-230`
  → `c-228` → `c-232` (OQ7).
- **Criterio del tribunal que se respeta.** La nota bajó porque en cinco días se
  agregó evidencia nueva que no pudo acreditarse; el tribunal no pidió un
  clasificador supervisado ni código nuevo. Este change no agrega evidencia al
  ejemplar de la defensa.

## Estado: DETENIDO (18/11/2026)

El change queda **detenido** y se conserva como trabajo futuro la maquinaria offline del horizonte 1 (curacion, particion y arnes con fixtures sinteticos rotulados), documentada y sin entrenamiento ni medicion. Las tareas quedan **sin marcar**; nada se aplico.

**Motivo.** Faltan los dos insumos que comparte la familia post-entrega: un marco poblacional completo (por el que `c-229` quedo detenido) y un `clasificacion_log` real acumulado (alrededor de 153 filas de prototipo y campana, 3 validadas en el repositorio), mas el consentimiento escrito de etiquetadores independientes nuevos (desde `E6`) y la decision K-02 sobre el envio de textos nuevos a la Gemini API.

**Reapertura.** Solo con un periodo real de operacion del prototipo como mesa de ayuda del equipo y la exportacion completa de la tabla `incidente` (marco para `c-229` y log real para este change), con el consentimiento escrito de los etiquetadores independientes y la decision K-02.

## Context

La organización acumula decisiones validadas en `clasificacion_log`
(`sector_id_validado`, `validado_por_empleado_id`, `intervencion_inicio_en`,
`validado_en`, `origen_intervencion`; `App/Backend/app/models/clasificacion_log.py`),
que constituyen el activo informacional de `subsec:clasificador-supervisado`
(`10-recomendaciones.tex:12-14`).

**Hechos del estado actual (verificados el 16/11/2026):**

- El corpus de 200 casos (`data/corpus_evaluacion_pseudonimizado.json`) es el
  corpus de ajuste del híbrido: el vocabulario del filtro determinístico y las
  reglas de frontera del prompt se ajustaron, en parte, con él
  (`10-recomendaciones.tex:26`). Su composición por `sector_asignado` es Hardware
  85, Software 67, Seguridad 31, Sistemas 16, Bases de Datos 1 (comando en tareas
  0.2). No hay corpus supervisado propio ni conjunto de prueba retenido acreditado.
- Doble etiquetado E1/E2 (`evaluation/data/campana/doble_etiquetado.csv`, 400 filas,
  200 casos por etiquetador): 62 casos discordantes, 29 de ellos con el par exacto
  `Sistemas`/`Soporte Tecnico Software`.
- La limitación de `Sistemas` dentro de la muestra (`08-discusion.tex:26`): de los
  16 casos, 7 correctos; errores hacia Software (5), Bases de Datos (2) y Seguridad (2).
  `c-235` reescribe esa sección y `subsec:frontera-sistemas`; este change no las toca.
- El codebook está en `evaluation/data/campana/codebook_doble_etiquetado.md`, con
  la taxonomía de `openspec/specs/sector-taxonomy/spec.md` (`TAX-001`, `TAX-004`).
- **No verificado:** si `clasificacion_log` contiene filas de operación real o solo
  de corridas de evaluación y demostración (OQ1); si existe autorización
  institucional para extraerlas (OQ2).

## Goals / Non-Goals

**Goals:**

- Entregar la maquinaria reproducible: compuertas, curación, partición sin fuga,
  arnés tipo BERT y benchmark de modelos abiertos ejecutados localmente, revisión
  del codebook y consumo del corpus probabilístico acreditado.
- Dejar el registro honesto: la línea depende de datos inexistentes, de procedencia
  acreditable y de autorización; el corpus de 200 no evalúa el supervisado.

**Non-Goals:**

- Modificar el ejemplar que se defiende (OQ7).
- Entrenar y publicar un modelo si falta volumen o alguna compuerta está abierta.
- Cambiar el clasificador de producción, el prompt vigente o las cinco cadenas.
- Usar cifras o artefactos retirados por `c-235`.
- Enviar texto a Gemini u otro tercero sin K-02 cerrada.

## Decisions

### D0 — Compuertas previas a todo dato nuevo

**Compuerta de procedencia (K-01).** Ningún dato nuevo (export de
`clasificacion_log`, etiquetado humano de la frontera, etiquetas del conjunto
retenido) entra al análisis sin:

1. el **registro crudo exportado del sistema**, con las marcas temporales que el
   sistema registra, nunca reconstruidas ni completadas a mano;
2. una **constancia de la organización** sobre la extracción (qué, cuándo, quién,
   con qué consulta), con el original en custodia del director;
3. el **hash SHA-256 del export crudo** versionado en el repositorio (el contenido
   se versiona solo si K-02 lo permite);
4. la regla de que **ningún texto redactado por los autores ni generado o asistido
   por IA** entra como dato de entrenamiento o de prueba presentado como real;
5. la **verificación del director** contra la evidencia primaria, registrada con
   fecha, antes de habilitar el análisis.

Para etiquetado humano: planillas originales tal como se completaron, con los
metadatos del archivo, marcas temporales registradas por la herramienta, y
etiquetadores identificados por alias en `registro_sujetos.csv` con consentimiento.

Los **fixtures sintéticos** son válidos solo para pruebas y se rotulan como
sintéticos en el nombre del archivo (`*_sintetico*`), en la cabecera
(`"naturaleza": "sintetico"`) y en cualquier salida derivada.

**Compuerta ética y legal (K-02).** Antes de extraer `clasificacion_log`:
autorización institucional escrita; base de licitud bajo la Ley 25.326 y
consentimiento o información a los empleados cuyos textos y decisiones se usan;
declaración de **dónde corre cada modelo** (D4) y de **todo envío de texto** a la
Gemini API u otro tercero. Sin K-02 cerrada no se extrae ni se envía nada.

Las dos compuertas son tareas bloqueantes (grupo 0); su estado se registra en
`dictamen-correcciones.md`.

### D1 — Dos horizontes: maquinaria ahora, entrenamiento condicionado

Se entrega la **maquinaria** y el **registro honesto**, no un modelo entrenado. Lo
que no requiere datos nuevos (funciones puras de curación y partición, arnés con
fixtures sintéticos rotulados) puede construirse con TDD; el entrenamiento real
queda condicionado a volumen y a K-01/K-02 cerradas.

### D2 — Contrato de curación desde un export crudo de `clasificacion_log`

El exportador opera sobre el **export crudo acreditado** (D0), no sobre una base de
desarrollo. Por caso:

| Campo | Origen | Regla |
|---|---|---|
| `texto` | `incidente.descripcion` | pseudonimizado con `scripts/corpus_ingest/pseudonymize_corpus.py` |
| `sector_validado` | `clasificacion_log.sector_id_validado` | solo no nulo |
| `sectores_validados` | `clasificacion_sector_validado` | multietiqueta validada |
| `etapa`, `confianza` | `clasificacion_log` | se descartan `fallback` y `confianza = 0.0` |
| `origen_intervencion` | `clasificacion_log` | `gate` \| `muestreo` \| `rederivacion` \| `completado_manual` |
| `sector_predicho`, versión | `clasificacion_log` + trazabilidad de `c-227` | predicción del híbrido registrada en operación |
| metadatos | `intervencion_inicio_en`, `validado_en` | tal como los registró el sistema; pseudonimizados |

Exclusiones obligatorias: filas generadas por corridas de evaluación o
demostración, y toda fila cuyo texto coincida con un texto versionado en el
repositorio (corpus de 200, material retirado por `c-235`, fixtures). El corpus es
**inmutable y versionado** (JSON con `schema_version` y `metadata`, UTF-8 sin BOM,
LF). Se deduplica con `evaluation.no_solape.verificar_no_solape` contra el corpus de
200 y contra el conjunto retenido que exista. Cumple `supervised-corpus-curation`.

### D3 — Partición disjunta sin fuga, con el conjunto retenido fuera del entrenamiento

Partición `train`/`dev`/`test` agrupada por texto casi duplicado y estratificada
por sector y canal. El **conjunto retenido admisible** es, en orden:

1. el **corpus probabilístico acreditado** de `c-229` con la referencia por mayoría
   de `c-230` (único admisible como evaluación);
2. mientras no exista, una partición `test` de `clasificacion_log` rotulada como
   **interna** («partición retenida interna, no validación externa»).

El corpus de 200 nunca es conjunto de prueba del supervisado (es el corpus de
ajuste del híbrido). `dev` solo para parada temprana; `test` se usa una vez. Función
pura con prueba sintética previa. Cumple `supervised-classifier-benchmark` (SCB-001).

### D4 — Modelo tipo BERT, modelos abiertos y lugar de ejecución

- Encoder BERT de español o multilingüe (`BETO` o `xlm-roberta`, OQ3).
- Modelos abiertos (`Llama 3`, `Mistral`, `Qwen`) con `prompts` y, si el volumen lo
  permite, `LoRA`.
- **Lugar de ejecución (por defecto):** todos los modelos corren **localmente**,
  con pesos descargados una vez y fijados por hash, sin red durante la inferencia.
  Cualquier uso de una API de terceros para estos modelos exige K-02 y se declara
  por modelo (OQ4).
- **Comparador híbrido:** sus predicciones se toman de `sector_id_predicho` ya
  registrado en `clasificacion_log` (sin llamadas nuevas), con la versión del
  proveedor registrada. Si el conjunto retenido no tiene predicciones registradas,
  obtenerlas exige una corrida nueva contra la Gemini API, que solo se hace con
  K-02 cerrada y declarada (OQ4).
- Métricas con `evaluation/metrics.py`; `n` de entrenamiento y de prueba separados.
- Sobre el corpus de 200 solo se admite un contraste **descriptivo** rotulado
  «dentro de la muestra; el híbrido se ajustó con este corpus; no evalúa el
  supervisado». Cumple SCB-002 y SCB-003.

### D5 — Revisión del codebook de la frontera `Sistemas`↔`Software`

- **Antes:** línea base desde el doble etiquetado E1/E2 sobre los 200 (62
  discordantes; 29 del par `Sistemas`/`Soporte Tecnico Software`), reproducida por
  comando al aplicar.
- **Después:** etiquetado nuevo de casos limítrofes con el codebook revisado, por
  etiquetadores registrados, bajo K-01 y K-02. Sin ese etiquetado no hay «después» y
  se declara.
- Los ejemplos limítrofes del codebook se toman de textos versionados y
  acreditados (corpus de 200 o export acreditado), nunca redactados por los autores
  ni generados por IA.
- `TAX-004` se propone y solo se aplica con aprobación de los autores. Cumple
  `taxonomy-codebook-revision`.

### D6 — Corpus probabilístico acreditado

Se **consume** de `c-229` (diseño, cuotas y compuertas propias) con la referencia y
el acuerdo multi-evaluador de `c-230`. La evaluación no excluye casos y reporta
intervalos sobre el universo con el estimador de `c-229`. Si no existe, la tarea
queda bloqueada; no se sustituye por muestreo de conveniencia ni por material
retirado. Cumple `natural-prevalence-evaluation-corpus`.

### D7 — Memo y tesis

- `numeros-canonicos.md`: sección **`3.41`** (número reservado; `c-235` declara
  `3.39`-`3.42` reservadas y toma `3.45`). Registra solo valores producidos con
  compuertas cerradas (volumen, `n`, métricas sobre el conjunto retenido con su
  rótulo, ambigüedad antes y después), cada uno con procedencia, ámbito y estado.
- La tesis no cambia en la entrega. En una versión posterior a la defensa, y solo
  con compuertas cerradas, se informan los resultados respetando lo que `c-235`
  fija en `subsec:clasificador-supervisado`, `subsec:frontera-sistemas`,
  `subsec:corpus-independiente` y la limitación de `Sistemas`.

### D8 — Gobernanza y checkpoints

Gobernanza ALTA. Checkpoints humanos: (A) esquema de `clasificacion_log`;
(B) compuertas K-01/K-02 antes de exportar o etiquetar datos reales; (C) antes de
entrenar o publicar un modelo; (D) antes de cualquier envío de texto a terceros.

### D9 — Registro del uso de asistentes de IA (A-03)

Toda tarea de este change hecha con un asistente de IA (código, análisis, prosa) se
registra en `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (archivo de
`c-237`), con la herramienta y cómo verificaron los autores cada cifra.

### D10 — Alcance y orden

Por defecto se aplica después de cerrar `c-239`, tras `c-229` y `c-230`. Las
tareas que no requieren datos (grupos 1 y 2 hasta REFACTOR) pueden adelantarse solo
si los autores lo deciden (OQ7), y aun así sin tocar el ejemplar.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| Procedencia no acreditable del dato nuevo | D0 (K-01) con verificación del director antes del análisis |
| Uso sin autorización o envío a terceros no declarado | D0 (K-02); D4 lugar de ejecución por defecto local |
| `clasificacion_log` sin filas reales | OQ1; bloqueo declarado |
| Lectura del corpus de 200 como evaluación | Rótulo obligatorio (D4) |
| Fuga del conjunto retenido | Prueba de partición disjunta |
| Fixtures sintéticos tomados por reales | Rotulado triple (D0) |
| Contradicción con el texto que fija `c-235` | La tesis no cambia en la entrega (D7) |

## Migration Plan

1. Compuertas y línea de base (grupo 0).
2. Curación (grupo 1): funciones puras con TDD; ejecución real tras K-01/K-02.
3. Partición y arnés (grupo 2).
4. Codebook (grupo 3).
5. Corpus probabilístico acreditado (grupo 4, tras `c-229`/`c-230`).
6. Memo y registro (grupo 5).
7. Verificación de cierre (grupo 6).

Rollback: `git revert`; artefactos aditivos.

## Open Questions

- **OQ1 (autores):** ¿`clasificacion_log` tiene filas de operación real de la
  organización, o solo de corridas de evaluación y demostración? ¿Cuántas
  validadas? Sin filas reales, el entrenamiento queda bloqueado.
- **OQ2 (autores):** ¿la organización autoriza por escrito la extracción y el uso de
  esos textos y decisiones? ¿Con qué base de licitud y cómo se informa a los
  empleados?
- **OQ3 (autores):** volumen mínimo para habilitar el entrenamiento real y modelo
  base (`BETO` vs `xlm-roberta`).
- **OQ4 (autores):** confirmar que todos los modelos corren localmente; si se
  admite alguna API de terceros (incluida una corrida nueva del híbrido contra la
  Gemini API), cuál y con qué autorización.
- **OQ5 (autores):** ¿se aplica `TAX-004` aquí o en un change propio? Por defecto se
  difiere.
- **OQ6 (aplicación):** ¿entrega `c-229` el corpus acreditado? Si no, el grupo 4 queda
  bloqueado.
- **OQ7 (autores):** ¿quieren ejecutar algo de este change antes de la defensa? Por
  defecto, nada; y en ningún caso se modifica el ejemplar.
- **OQ8 (autores):** ¿confirman esta adaptación (posterior a la entrega) o
  prefieren archivar el change sin aplicar? El destino lo registra `c-239` (D11).
