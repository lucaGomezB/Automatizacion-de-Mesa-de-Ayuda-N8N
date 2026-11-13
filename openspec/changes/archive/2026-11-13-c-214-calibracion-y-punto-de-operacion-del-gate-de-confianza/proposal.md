## Why

El dictamen CONEAU sobre v1.3.0 (sección 6, viñeta «Revisión humana inoperante», y criterio 5 de
la rúbrica, peso 15) descuenta que «el umbral de confianza no derivó ningún caso a revisión en el
corpus; el mecanismo de supervisión previsto por diseño no actuó». La tesis lo explica dentro de
la muestra con una tabla por bandas (sección 7, `07-resultados.tex`, `tab:bandas`), pero no
informa métricas de calibración ni de discriminación, no evalúa ningún punto de operación
alternativo y la recomendación de recalibrar con ajuste fuera de la muestra (sección 10,
`10-recomendaciones.tex`, `subsec:calibracion-gate`) quedó como trabajo futuro, aunque hoy existe
un corpus independiente con predicciones del clasificador congelado. Este change ejecuta esa
recomendación con datos ya versionados y sin costo: convierte «el gate no actuó» en una medición
de por qué, de qué señal podría sostener una derivación y de si se confirma fuera de la muestra.

## What Changes

- **Fiabilidad y discriminación por etapa**, dentro y fuera de la muestra: tabla de fiabilidad
  por nivel de confianza observado, ECE (10 bandas de igual ancho), Brier, sobreconfianza media y
  AUROC de la confianza para separar aciertos de errores, con IC bootstrap de semilla fija.
- **Barrido de umbral y curva riesgo-cobertura** de la etapa Gemini sobre los niveles
  observados, con la carga de revisión que implicaría a nivel del sistema.
- **Selección de punto de operación sin ajuste sobre la prueba**: regla prerregistrada que elige
  el umbral en los 200 casos y lo evalúa en el bloque fuera de muestra (103), con resultado de
  tres vías.
- **Señales alternativas ante una confianza degenerada** (Gemini declara solo 4-5 valores, casi
  siempre ≥ 0,85): acuerdo entre etapas (sector de las reglas frente al de Gemini en los casos
  escalados) y `score_correctitud` de las reglas, ambos recomputables offline sin costo, con la
  misma regla de selección dentro y evaluación fuera de la muestra.
- **Gobernanza**: el resultado se informa; si una señal o umbral se confirma fuera de la
  muestra, el change deja una recomendación con su evidencia y NO cambia `openspec/config.yaml`,
  `settings.py` ni la conducta productiva (eso sería un change aparte, gobernanza HIGH). El
  clasificador evaluado `hybrid-v3` sigue reproducible.

## Capabilities

### New Capabilities

- `confidence-gate-calibration`: análisis versionado de la calibración y la discriminación de la confianza por etapa, del barrido de umbral y de señales alternativas de derivación, con selección dentro de la muestra y evaluación fuera de ella, sin cambio de configuración productiva.

### Modified Capabilities

(ninguna)

## Impact

- **Dictamen y rúbrica**: criterio 5 (Desarrollo técnico, peso 15: «la revisión humana por
  confianza no actuó en el corpus»), criterio 6 (Resultados y análisis, peso 10) y, en menor
  medida, criterio 4 (Metodología). Efecto esperado en `design.md` (D9).
- **Código nuevo** (TDD): `evaluation/calibracion_gate.py` (ECE, Brier, AUROC, riesgo-cobertura,
  regla de selección) y `evaluation/data/campana/analisis/analisis_calibracion_gate_c214.py` con
  sus pruebas; salidas `analisis_calibracion_gate_c214.{json,md}`.
- **Lectura sin edición**: cachés `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` y
  `evaluation/data/campana/predicciones_independiente.json`, corpus de 200 y bloque
  independiente, `App/Backend/app/classifiers/deterministic.py` (recómputo offline).
- **Sin costo, sin Docker, sin red.** Recompilación del PDF: autores con LaTeX.
- **Tesis**: sección 7 (`07-resultados.tex`, `subsec:calibracion`), sección 4
  (`04-marco-metodologico.tex`, definición de las métricas), sección 8 (`08-discusion.tex`),
  sección 9 (`09-conclusiones.tex`, fila del objetivo 6), sección 10 (`10-recomendaciones.tex`,
  `subsec:calibracion-gate`) y memo `docs/Tesis/Correcciones/numeros-canonicos.md`.
- **Dependencias**: independiente de c-208 (integridad de Engram) y de c-209/c-210 (línea de
  base clásica). Como secundarios opcionales: las predicciones de un brazo Gemini solo (un
  change futuro, no propuesto todavía; acuerdo entre etapas completo) y el corpus arbitrado de
  c-206 (más casos fuera de muestra; c-206 está a medias), si existen al aplicar. Se apila sobre
  c-205 y c-207 por el memo y, más adelante, por la prosa.
- **Alcance de esta aplicación**: se aplican las tareas 0 a 4, 5.1 y 6.1 a 6.3. NO se edita
  ningún `.tex` (hay otro PR abierto sobre las secciones 7, 8 y 9): la prosa (5.2) y la
  recompilación del PDF (5.3) quedan pendientes. Gobernanza: MEDIUM (análisis); cualquier cambio de umbral
  productivo, HIGH y fuera de alcance.
