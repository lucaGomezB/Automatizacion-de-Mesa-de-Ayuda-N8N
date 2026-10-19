# Proposal: c-95 — Rigor de Resultados y Discusión, y límites del Capítulo 9

## Why

La auditoría de la tesis detectó que los capítulos 7, 8 y 9 describen resultados
sin la evidencia que exigen: la prueba de normalidad que justifica Wilcoxon no
reporta estadístico ni p (A-15), la discusión interpreta pero no interroga los
resultados ni explica la confusión sistemática de Sistemas (A-20), el único
contraste metodológico contra TF-IDF+SVM se enuncia en una sola frase sin
procedimiento, partición, n ni código (A-21), la tipología de errores no publica
ningún ejemplo textual (M-10), los costos operativos no tienen fuente (M-16), y
el Capítulo 9 introduce una interpretación estadística que pertenece al Capítulo
8 (A-25) y una afirmación general sobre LLM frente a clasificadores supervisados
que la evidencia no sostiene (A-23). Corregir esto es un requisito de integridad
académica y de rigor metodológico, y no solapa con los changes que ya corrigen
números, calibración, bibliografía o forma.

## What Changes

- **A-15 (Alta) — Normalidad reportada**: §4.7 SHALL reportar el estadístico
  \(W\) y el valor \(p\) de Shapiro-Wilk para el flujo manual, el automatizado y
  las diferencias pareadas; §7.1 SHALL referenciar el resultado. Los valores se
  recalculan sobre el corpus real después de c-77 (E3) y se registran en
  `evaluation/report.md` con el comando reproducible.
- **A-20 (Alta) — Interrogación crítica en §8.1**: agregar una lectura crítica
  de los resultados con hipótesis alternativas y explicaciones rivales de la
  reducción de tiempo, condiciones que las debilitarían y límites de la
  inferencia; explicar por qué Sistemas se confunde sistemáticamente con otras
  categorías a partir de la matriz 5x5 real y sus métricas por clase.
- **A-21 (Alta) — Baseline TF-IDF+SVM**: retirar como resultado la cifra
  "78 %, F1 0,764" y declarar el chequeo como exploratorio, no reproducible y no
  comparable (partición y \(n\) no preservados); eliminar la afirmación de
  superioridad sustantiva sobre el baseline. La reproducción sistemática queda
  fuera de alcance y se declara como trabajo futuro.
- **M-10 (Media) — Ejemplos textuales**: §7.4 SHALL incluir 2–3 ejemplos
  textuales anonimizados de incidentes mal clasificados, con texto, sector
  asignado, sector predicho y confianza, tomados de
  `evaluation/predicciones.json` y verificados contra el corpus.
- **M-16 (Media) — Costos con fuente**: §8.4 SHALL sustentar el costo de
  infraestructura y el costo por invocación en fuentes públicas verificables
  (lista de precios oficial del proveedor de inferencia y de infraestructura,
  con fecha de consulta) o, en su defecto, acotar la estimación como orden de
  magnitud con supuestos explícitos. No se mantienen cifras sin fuente.
- **A-23 (Alta, parcial) — Límite de la afirmación general**: §9.2 MUST dejar de
  afirmar como contribución general que los LLM invocados por instrucciones
  superan a los clasificadores supervisados clásicos sobre representaciones
  estáticas. La afirmación se acota al corpus, al dominio y a la comparación
  efectivamente realizada; se coordina con la tensión de evidencia contraria que
  introduce c-78 (B1) sin duplicarla.
- **A-25 (Alta, parcial) — Interpretación estadística fuera de Conclusions**:
  §9.1 MUST dejar de introducir la interpretación de \(W=0\) ("poco frecuente",
  "interpretada con cautela"); la interpretación inferencial vive en el Capítulo
  8 y la referencia a la prueba, en el Capítulo 7. Se coordina con c-77 (A1), que
  elimina \(W=0\), sin reintroducirlo.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: incorpora requisitos de reporte de normalidad, interrogación
  crítica de resultados, trazabilidad y alcance del baseline, evidencia textual
  anonimizada de errores, fuentes y cotas de costos, y delimitación de las
  afirmaciones del Capítulo 9.

## Impact

Documentación y artefactos (SIN tocar `App/**`):

- `docs/Tesis/v9 (IA)/paper/sections/04-marco-metodologico.tex` (§4.7)
- `docs/Tesis/v9 (IA)/paper/sections/07-resultados.tex` (§7.1, §7.4, Tabla 9)
- `docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex` (§8.1, §8.3, §8.4)
- `docs/Tesis/v9 (IA)/paper/sections/09-conclusiones.tex` (§9.1, §9.2)
- `evaluation/report.md` (sección de normalidad Shapiro-Wilk)
- `docs/Tesis/Correcciones/dictamen-correcciones.md` (registro de A-15, A-20,
  A-21, M-10, M-16, A-23 y A-25)
- `main.pdf` (recompilación en Overleaf, no en este repo)

No se modifican `App/**`, `data/corpus_evaluacion_pseudonimizado.json`,
`evaluation/stats.py`, `CHANGES.md`, ni los artefactos de c-76, c-77, c-78 o
c-80. La fuente de verdad numérica sigue siendo el corpus real y
`evaluation/report.md`.

## Rollback Plan

`git checkout --` sobre los `.tex`, `evaluation/report.md` y el registro de
correcciones afectados, o `git revert` del commit del change. Los artefactos OPSX
se descartan con el directorio del change.

## Success Criteria

- [ ] §4.7 reporta \(W\) y \(p\) de Shapiro-Wilk para manual, automatizado y
      diferencias; §7.1 lo referencia; `evaluation/report.md` registra el comando
      reproducible y los valores recalculados tras c-77.
- [ ] §8.1 contiene una interrogación crítica con al menos tres explicaciones
      rivales de la reducción y una explicación de la confusión de Sistemas
      basada en la matriz 5x5 y las métricas por clase.
- [ ] La cifra "78 % / 0,764" del baseline TF-IDF+SVM se retira o se declara
      explícitamente no reproducible y no comparable; no queda una afirmación de
      superioridad sustantiva sobre ese baseline.
- [ ] §7.4 incluye 2–3 ejemplos textuales anonimizados con asignado, predicho y
      confianza, verificados contra `evaluation/predicciones.json`.
- [ ] Los costos de §8.4 tienen fuente pública con fecha de consulta o una cota
      explícita con supuestos; no quedan "50–100 USD/mes" ni "0,02 USD" sin
      respaldo.
- [ ] §9.2 no afirma como resultado general la superioridad de LLM sobre
      clasificadores supervisados; la afirmación queda acotada al corpus y al
      contraste disponible.
- [ ] §9.1 no introduce interpretación de \(W=0\); no reaparece "poco frecuente"
      ni "interpretada con cautela" en Conclusiones.
- [ ] Barridos `rg` sin residuos; `main.pdf` recompilado en Overleaf sin errores
      fatales; `openspec validate c-95-tesis-resultados-discusion-rigor --strict`
      pasa.
