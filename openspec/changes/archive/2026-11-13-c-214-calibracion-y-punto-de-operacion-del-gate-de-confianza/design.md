## Context

Ver `proposal.md` (Why). Hechos verificados en el repositorio al proponer (2026-11-13):

- **Confianzas por caso disponibles para los dos corpus**, en las cachés versionadas
  `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` (200 casos) y
  `evaluation/data/campana/predicciones_independiente.json` (103 casos), con `confianza`,
  `etapa`, `sector_predicho` y `sector_asignado`. La etapa de reserva no registró casos en
  ninguno de los dos.
- **La confianza de Gemini es degenerada.** Dentro de la muestra (69 casos escalados) toma solo
  los valores 0,85, 0,90, 0,95 y 0,98, nunca menos de 0,85: por eso el gate de 0,70 no derivó
  nada. Fuera de la muestra (34 casos escalados) toma 0,65, 0,85, 0,90, 0,95 y 0,98; un caso
  quedó por debajo de 0,70, es decir que fuera de la muestra el gate habría derivado 1 caso.
- **La confianza de la etapa determinística** es una fuerza de señal discreta que no gobierna la
  derivación (sección 5, `05-arquitectura.tex`); lo que gobierna el cortocircuito es
  `score_correctitud ≥ 0,5166` (`App/Backend/app/config/settings.py:134`, derivado out-of-fold
  en c-74). Ese puntaje no está en las cachés, pero se recomputa offline y sin costo con
  `DeterministicClassifier` (función `score_correctitud` en
  `App/Backend/app/classifiers/deterministic.py`). Lo mismo vale para el sector que las reglas
  habrían propuesto en los casos que escalaron a Gemini.
- **Funciones existentes**: `evaluation/metrics.py` (`calibracion_por_bandas`,
  `contingencia_confianza`, `intervalo_wilson`, `percentil_intervalo`, `remuestreos_indices`,
  `SEMILLA_BOOTSTRAP`, `REMUESTREOS_BOOTSTRAP`). No hay implementación de ECE, Brier ni AUROC en
  `evaluation/`.
- **Antecedente en la tesis**: `tab:bandas` y la lectura por etapa (sección 7) ya muestran, dentro
  de la muestra, exactitudes de 0,710 y 0,737 en las bandas altas de Gemini. La recomendación de
  la sección 10 propone: señales independientes del puntaje (desacuerdo entre etapas, margen),
  recalibración isotónica y umbral derivado de una curva cobertura-precisión con ajuste fuera de
  la muestra y piso declarado de antemano (exactitud de la revisión humana o el 85 %).
- **Memoria del proyecto**: sin decisiones previas en engram sobre calibración o umbral de
  confianza más allá de lo que documenta la tesis.

**Declaración de no ceguera.** Para comprobar la factibilidad, quien propuso este change tabuló
la distribución de confianzas y los aciertos por nivel en ambos corpus. Las reglas de abajo se
fijan por principio (las recomendaciones ya publicadas en la sección 10), no por lo que esa
tabulación sugiera, y se informan todos los resultados, favorables o no. Esta exposición previa
se declara en el memo canónico como amenaza a la validez del prerregistro.

## Goals / Non-Goals

**Goals:**

- Medir calibración (nivel) y discriminación (orden) de la confianza por etapa, dentro y fuera de
  la muestra, con IC.
- Elegir un punto de operación con una regla fijada de antemano en los 200 casos y evaluarlo en
  el bloque fuera de muestra.
- Evaluar, con la misma disciplina, señales alternativas recomputables sin costo.
- Dejar una recomendación con evidencia, sin tocar la configuración productiva.

**Non-Goals:**

- Cambiar `human_review: 0.70`, `deterministic_score: 0.5166`, el prompt, el contrato de salida o
  el código del clasificador.
- Pedir a Gemini puntajes por categoría o un margen (exige cambiar el contrato, Anexo H).
- Revisión por muestreo, aprendizaje activo o una campaña nueva con operadores.
- Corridas pagas: este change no llama a Gemini.

## Decisions

### D1 — Conjuntos y referencia

Selección: los 200 casos (referencia original, la primaria de la tesis; el consenso `E1`/`E2`
sobre 138 como control). Evaluación: bloque fuera de muestra de 103 casos (consenso `E3`/`E4`).
Secundario condicional (no ejecutado en esta aplicación: el corpus arbitrado de c-206 todavía no existe): si existe el corpus arbitrado de c-206 con predicciones del clasificador
congelado, se repite la evaluación sobre él. Acierto = exactitud estricta; la laxa se informa
aparte.

### D2 — Métricas de calibración y discriminación

Por etapa (Gemini; determinística con su `confianza` y con su `score_correctitud`) y por corpus:

- Tabla de fiabilidad por valor observado de confianza (casos, aciertos, exactitud, Wilson).
- ECE con 10 bandas de igual ancho en [0; 1] (fijado ahora; con valores discretos el número de
  bandas no altera el resultado), Brier y sobreconfianza media (confianza media − exactitud).
- AUROC de la señal para separar aciertos de errores (Mann-Whitney con empates a 0,5).
- IC95 bootstrap percentil por caso con `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP`.

Implementadas como funciones puras nuevas en `evaluation/calibracion_gate.py`, reutilizando
`metrics.py` donde aplique.

### D3 — Barrido y riesgo-cobertura

Para la etapa Gemini, umbrales candidatos `T = {0,70 (vigente); 0,86; 0,91; 0,96; 0,99; ∞}`
(entre los niveles observados; «acepta si confianza ≥ t»; `∞` = derivar todo lo escalado). Para
cada `t`: cobertura (aceptados / escalados), exactitud selectiva de los aceptados (Wilson),
errores atrapados en los derivados y carga de revisión a nivel del sistema (derivados / total de
casos del corpus).

### D4 — Regla prerregistrada de selección del umbral

- Piso primario `φ = 0,85` (criterio del segundo objetivo, anterior a estos datos); secundario
  `φ' = 0,8278` (exactitud estricta del brazo manual contra el consenso, `analisis/resultados.json`),
  informado aparte.
- Selección en los 200: `t*` = el menor `t ∈ T \ {∞}` cuya exactitud selectiva de los aceptados
  sea `≥ φ` con al menos 10 casos aceptados. Si ninguno cumple, `t* = ninguno`.
- Evaluación en los 103:
  - si `t*` existe: *confirmado* si la exactitud selectiva fuera de muestra es `≥ φ` y la de los
    derivados es menor que la de los aceptados; *no confirmado* si la exactitud selectiva es
    `< φ`; *no estimable* si hay menos de 10 aceptados o ningún derivado.
  - si `t* = ninguno`: el resultado es «la confianza autodeclarada no sostiene un umbral con el
    piso fijado»; fuera de la muestra se informan el barrido completo y el AUROC solo como
    descripción, sin elegir umbral con esos datos.
- Recalibración monótona (isotónica, ajustada en los 200) se informa solo como corrección de nivel
  (ECE/Brier fuera de muestra); se declara que no cambia el orden ni, por lo tanto, la curva
  riesgo-cobertura.

### D5 — Señales alternativas (costo cero), con la misma regla

- **S1, acuerdo entre etapas**: en los casos escalados, ¿coincide el sector que habrían dado las
  reglas (ganador por debajo de `τ`) con el de Gemini? Categorías: acuerdo / desacuerdo / sin
  predicción de las reglas. Política candidata: aceptar si hay acuerdo, derivar si no.
- **S2, `score_correctitud` de las reglas** sobre los casos escalados, como señal continua de
  dificultad (barrido con cuantiles fijados en los 200).
- Selección en los 200 y evaluación en los 103 con las mismas condiciones de D4 (piso, mínimo de
  10 aceptados, tres vías).
- **Secundario condicional** (no ejecutado: requiere las predicciones de un brazo Gemini solo, un change futuro no propuesto todavía): S1
  extendido a todos los casos y chequeo fuera de muestra del punto de operación `τ = 0,5166`
  (exactitud de las reglas frente a Gemini en los casos cortocircuitados), con McNemar exacto.

### D6 — Gobernanza del resultado

El change informa; no cambia configuración. Si alguna política queda *confirmada* fuera de la
muestra, el memo y la sección 10 recomiendan adoptarla con su evidencia y su límite (n chico), y
se anota como candidato a un change posterior de gobernanza HIGH (umbral en
`openspec/config.yaml` y `settings.py`, con su propia validación). Si ninguna se confirma, la
tesis declara que la derivación por confianza autodeclarada no es reparable por recalibración en
este corpus y que la supervisión debe apoyarse en otra señal o en muestreo.

### D7 — Script, salidas y registro

`evaluation/calibracion_gate.py` + `evaluation/tests/test_calibracion_gate.py`;
`evaluation/data/campana/analisis/analisis_calibracion_gate_c214.py` + test hermano; salidas
`analisis_calibracion_gate_c214.{json,md}` (LF, UTF-8 sin BOM, determinísticas, SHA-256 en
`analisis/README.md` y `SHA256SUMS.txt`); el recómputo de `score_correctitud` y del sector de las
reglas se persiste en `evaluation/data/campana/senales_reglas_c214.csv` para que el análisis no
dependa del backend en tiempo de lectura. Cifras al memo canónico en una sección nueva.

### D8 — Prosa

La sección 7 incorpora ECE, Brier, AUROC y el barrido dentro y fuera de la muestra, con el caso
fuera de la muestra por debajo de 0,70; la sección 10 pasa de proponer la curva a informar su
resultado y deja como futuro solo lo que exige cambiar el contrato o configuración; la sección 9
actualiza la fila del objetivo 6.

### D9 — Efecto esperado en la calificación (honesto) y esfuerzo

Base 7,83. El change no hace que el gate actúe en el corpus ya medido; convierte la observación
en una medición con evaluación fuera de la muestra.

- **Alguna política confirmada fuera de la muestra**: criterio 5 de 9 a 9,5 (+0,07), criterio 6
  de 8 a 8,5 (+0,05), criterio 4 algo (+0 a +0,05): ≈ **+0,10 a +0,15**.
- **Ninguna confirmada** (probable, por n = 34 escalados fuera de la muestra): la limitación
  queda medida y explicada; criterio 6 sube, criterio 5 casi no: ≈ **+0,03 a +0,08**.
- **Riesgo**: un tribunal puede leer el hallazgo como confirmación de que el diseño de
  supervisión por confianza no funciona; ya está declarado en la tesis, por lo que el riesgo neto
  es bajo.

Esfuerzo: código y pruebas ~1 día-persona; análisis, memo y prosa ~0,5-1 día. Sin pago, sin
Docker. LaTeX: autores.

## Risks / Trade-offs

- [Prerregistro no ciego] → declaración explícita (Context) y reglas tomadas de la sección 10 ya
  publicada.
- [n fuera de muestra chico: 34 escalados] → resultado de tres vías con «no estimable»; el corpus
  arbitrado de c-206 se suma si existe (no ejecutado en esta aplicación).
- [Confianza discreta: ECE y AUROC con muchos empates] → se informa la tabla por valor observado
  junto a las métricas resumen.
- [Tentación de ajustar el umbral con el bloque fuera de muestra] → la regla D4 prohíbe elegir con
  esos datos; cualquier lectura adicional se rotula exploratoria.
- [Deriva del clasificador determinístico respecto de `bf5e099`] → el recómputo offline debe
  reproducir exactamente el enrutamiento y el sector de los casos cortocircuitados de las cachés;
  si no, se detiene.

## Migration Plan

Apply en el orden de `tasks.md`. Rollback: revertir los módulos, artefactos, la sección nueva del
memo y las fuentes `.tex`. Sin cambio productivo.

## Open Questions

- Si el sector de las reglas en un caso escalado tiene empate, S1 lo cuenta como «sin predicción»;
  se confirma en la prueba de RED de S1.
