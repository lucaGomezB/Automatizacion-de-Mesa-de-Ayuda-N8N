# Tasks — c-102 — Congelar números canónicos de la tesis (Gate 0)

## 0. Prerrequisitos y fuentes (solo lectura)

- [ ] 0.1 Confirmar que las fuentes existen y son legibles: `evaluation/report.md`,
  `evaluation/predicciones.json`, `data/corpus_evaluacion_pseudonimizado.json`, y
  las secciones `docs/Tesis/v9 (IA)/paper/sections/04-marco-metodologico.tex`,
  `07-resultados.tex`, `08-discusion.tex`, `09-conclusiones.tex`.
- [ ] 0.2 Registrar en el memo el SHA-256 del corpus
  (`1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`) y la fecha
  de verificación.
- [ ] 0.3 Confirmar que NO se edita ningún `.tex` y que no se ejecuta el clasificador
  (sin llamadas a Gemini/N8N/Twilio).

## 1. Reconstrucción del gate de intervención (ítem 1 del alcance)

- [ ] 1.1 Recalcular desde `evaluation/predicciones.json` la tabla de bandas de
  confianza (casos, aciertos, exactitud) y verificar que reproduce la Tabla 7.5 de
  `07-resultados.tex:150-159` (`98/26/6/31/39`).
- [ ] 1.2 Construir la tabla de contingencia `confianza (<0,70 vs ≥0,70) × etapa
  (deterministic/gemini) × acierto` y volcarla en el memo.
- [ ] 1.3 Documentar la regla efectiva del gate que los datos soportan: los `124`
  casos con confianza < 0,70 son todos `deterministic`; la etapa `gemini` asigna
  `confianza ∈ {0,85, 0,90, 0,95, 0,98}`; explicar qué confianza asigna la etapa
  determinística y por qué no dispara revisión.
- [ ] 1.4 Verificar si el `9,5 %` (19 casos) es derivable de `predicciones.json`,
  `evaluation/report.md` o `data/`. Documentar el resultado (esperado: no derivable).
- [ ] 1.5 Proponer y registrar la decisión editorial: RETIRAR el `9,5 %` y reformular
  el aporte operativo como no medido (salvo aporte posterior del autor); dejar el
  punto en la sección "decisiones no resolubles".

## 2. Coherencia de etapas y bandas (ítems 2 y 3 del alcance)

- [ ] 2.1 Documentar la distribución de etapas `deterministic 131` / `gemini 69` /
  `fallback 0` y su relación con la confianza por etapa (los 124 casos < 0,70 son
  determinísticos; Gemini nunca < 0,85).
- [ ] 2.2 Verificar el tramo "46 casos con confianza ≥ 0,90 y 13 errores": recalcular
  sobre `predicciones.json` y registrar el resultado (esperado: reproducible).
- [ ] 2.3 Registrar explícitamente que el tramo 46/13 NO se deduce de la Tabla 7.5
  publicada tal como está, y anotar la corrección textual necesaria en el consumidor
  (`07-resultados.tex:165`).

## 3. Universo y proyección horaria (ítem 4 del alcance)

- [ ] 3.1 Recalcular el universo con criterio calendario (`42 × 88 ≈ 3.700`) y con
  criterio de días hábiles (≈ 63 días → ≈ 2.646); registrar ambos.
- [ ] 3.2 Recalcular la proyección horaria con el ahorro medio de `43,82 s`
  (`43,82 × N / 3.600`): `≈ 45,0 h` con 3.700 y `≈ 32,2 h` con ≈ 2.646.
- [ ] 3.3 Fijar el criterio canónico propuesto (días hábiles) y marcar el valor
  calendario como `retirado`; declarar la propagación obligatoria a `04:45`,
  `08:14` y `09:24`.

## 4. Paradigma métrico y clase n=1 (ítems 5 y 6 del alcance)

- [ ] 4.1 Determinar si la referencia es mono o multietiqueta: contar los casos con
  `sectores_adicionales` no vacío (esperado: 8) y documentar que el clasificador
  emite una sola etiqueta principal.
- [ ] 4.2 Definir el set métrico final: primario monoetiqueta (exactitud estricta
  `0,7350`, macro-F1 `0,5207`); secundario multietiqueta (subset accuracy `0,43`,
  Hamming `0,3586`, micro-F1 `0,6654` con la advertencia de penalización estructural).
- [ ] 4.3 Documentar el procedimiento de recálculo desde `evaluation/predicciones.json`
  (comando y campos usados) para que las métricas sean reproducibles sin re-ejecutar
  el sistema.
- [ ] 4.4 Registrar la decisión sobre "Bases de Datos" (n=1): declarar no estimable,
  excluirla del macro-F1 de umbral, y reportar el umbral 0,85 sobre métricas sin esa
  clase; conservar el macro-F1 de cinco clases como valor informativo.

## 5. Tabla canónica final (ítem 7 del alcance)

- [ ] 5.1 Construir la tabla canónica con TODOS los números citables y su fuente
  (archivo y línea): `61,6 s`; `17,76 s`; `71,2 %`; `W=363`; `p=3,08e-32`;
  `r=0,9639`; `188/200`; `73,5 %` (147/200); `macro-F1 0,5207`; intervención
  (`9,5 %` retirado o vigente); universo (`3.700` o `≈2.646`); proyección
  (`45,0 h` o `≈32,2 h`); `IC Wilson [67,0 %, 79,1 %]`; `micro-F1 0,6654`;
  `subset accuracy 0,43`; `Hamming 0,3586`.
- [ ] 5.2 Asignar a cada valor su estado (`vigente` / `retirado` / `condicional`) y
  su procedencia exacta.
- [ ] 5.3 Redactar la sección "Decisiones no resolubles" con la decisión editorial
  adoptada por cada punto que la evidencia no cierre (al menos: el `9,5 %`).

## 6. Redacción y consistencia del memo

- [ ] 6.1 Escribir `docs/Tesis/Correcciones/numeros-canonicos.md` con la estructura:
  propósito, tabla canónica, decisiones por ítem, evidencia (archivo y línea), y
  "Decisiones no resolubles".
- [ ] 6.2 Verificar que todo número citado en la tabla tenga una fuente existente y
  que la línea indicada exista en el archivo referenciado.
- [ ] 6.3 Declarar en el encabezado del memo que es la fuente única de verdad
  numérica y que c-104 (y cualquier rama que reescriba `04/07/08/09`) MUST citar
  solo valores de esta tabla.

## 7. Verificación del change

- [ ] 7.1 Ejecutar `openspec validate c-102-congelar-numeros-canonicos-tesis --strict`
  y confirmar que no reporta errores.
- [ ] 7.2 Ejecutar `openspec status --change c-102-congelar-numeros-canonicos-tesis --json`
  y confirmar que todos los artefactos figuran en estado `done` y que `applyRequires`
  está completo.
- [ ] 7.3 Confirmar con `git status` que no se modificó ningún `.tex`, ni `CHANGES.md`,
  ni `docs/Tesis/Correcciones/dictamen-correcciones.md`.