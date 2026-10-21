## Context

Ver `proposal.md` — Why. La tesis v9 tiene contradicciones numéricas internas que
el dictamen CONEAU (2026-10-20, `auditorias/Dictamen_Tesis_v9_CONEAU_2026-10-20.md`)
declara bloqueantes para la defensa. El cambio produce un memo canónico en
`docs/Tesis/Correcciones/numeros-canonicos.md` y NO edita ningún `.tex`.

Estado de fuentes (verificado por lectura directa en esta sesión):

- `evaluation/report.md`: exactitud estricta `0,7350` (147/200); IC Wilson
  `[0,6698, 0,7913]`; macro-F1 `0,5207`; micro-F1 `0,6654`; subset accuracy
  `0,43`; Hamming loss `0,3586`; etapas `deterministic 131`, `gemini 69`,
  `fallback 0`; Wilcoxon `W=363`, `T+=19737`, `T−=363`, `p=3,08e-32`, `r=0,9639`;
  reducción media `43,82 s`; SHA-256 del corpus
  `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`.
- `evaluation/predicciones.json`: 200 predicciones, `deterministic 131` + `gemini 69`.
  Recomputado en esta sesión: bandas `[0;0,50) 98`, `[0,50;0,70) 26`,
  `[0,70;0,85) 6`, `[0,85;0,95) 31`, `[0,95;1] 39` — coincide EXACTO con la
  Tabla 7.5 de `07-resultados.tex`. Los `124` casos con `confianza < 0,70` son
  **todos** de la etapa determinística; la etapa Gemini asigna `confianza ∈
  {0,85, 0,90, 0,95, 0,98}` y nunca por debajo de 0,85. `confianza ≥ 0,90`: `46`
  casos con `13` errores (el tramo citado en `07-resultados.tex:165` es
  reproducible). `8` casos tienen `sectores_adicionales` no vacío: son etiquetas
  **predichas** adicionales del clasificador (`predicciones.json`), NO la
  referencia multietiqueta. La referencia del corpus tiene `107/200` casos con
  más de un sector de verdad (`53,5 %`).
- `07-resultados.tex`: Tabla 7.5 (`:145-163`), gate del 70 % (`:136`,`:165`),
  9,5 %/19 casos (`:138`), 131/69 (`:108`), proyección 45,0 h en
  `08-discusion.tex:14`, universo `3.700 = 42×88` en `04-marco-metodologico.tex:45`.
- Funciones existentes reutilizables sin re-ejecutar el sistema:
  `evaluation/metrics.py` expone `calibracion_por_bandas` y
  `contingencia_confianza` (probadas en `evaluation/tests/test_calibracion_confianza.py`).

**Nota sobre numeración de líneas.** Las referencias `archivo:línea` de este
`design.md` usan la numeración de editores y Python (universal newlines), igual
que el memo canónico. `07-resultados.tex` contiene un único carácter CR suelto
en su línea 17; las herramientas que solo cortan por LF (`grep -n`, `sed -n`,
`awk`) reportan un número uno menor para todas las líneas posteriores (p. ej.
`:108` aquí aparece como `:107` en `grep -n`). Los demás archivos citados no
tienen CR sueltos.

## Goals / Non-Goals

**Goals:**

- Producir el memo canónico con tabla final, decisiones, evidencia (archivo y
  línea) y sección de decisiones no resolubles.
- Cerrar o declarar no resoluble cada una de las siete contradicciones del alcance.
- Dar a las ramas de corrección posteriores (incluida c-104) una fuente única
  verificable, para evitar drift numérico.

**Non-Goals:**

- No editar `.tex`, no tocar `CHANGES.md` ni `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- No re-ejecutar el sistema, no recolectar datos, no llamar a APIs (Gemini, N8N, Twilio).
- No resolver las decisiones editoriales de los autores (se declaran, no se inventan).

## Decisions

- **D1 — Método de verificación read-only.** Los valores se recalculan desde
  `evaluation/predicciones.json` usando `python -c`/`jq` y las funciones de
  `evaluation/metrics.py`; no se invoca el clasificador. Alternativa descartada:
  re-ejecutar `run_evaluation.py` (prohibido por alcance y por determinismo del corpus).
- **D2 — Campos de procedencia y estado por valor.** Cada fila de la tabla canónica
  lleva `valor`, `fuente` (archivo:línea) y `estado ∈ {vigente, retirado, condicional}`.
  El estado `retirado` se usa cuando la evidencia desmiente el número vigente en el
  `.tex` (p. ej. el 9,5 %); `condicional` cuando depende de una decisión editorial.
- **D3 — Gate de intervención: reconstrucción y regla.** Se publica la tabla de
  contingencia `confianza (<0,70 vs ≥0,70) × etapa × acierto` derivada de
  `predicciones.json`. La regla efectiva que los datos soportan es: la confianza
  < 0,70 no es un disparador universal de revisión porque la etapa determinística
  la emite como passthrough y resuelve sin escalar; la etapa Gemini es la única
  que asigna confianza y, en el corpus, siempre ≥ 0,85. Se documenta esta regla y
  su divergencia con el texto de §7.3. Alternativa descartada: asumir que el gate
  del 70 % actúa sobre todos los casos (contradice los datos).
- **D4 — 9,5 % / 19 casos: no derivable de las fuentes permitidas.** No existe
  registro por caso de la intervención humana en `predicciones.json`, `report.md`
  ni `data/`. Decisión editorial propuesta: RETIRAR el 9,5 % y reformular el aporte
  operativo (intervención por gate) como no medido, salvo que el autor aporte la
  tabla de contingencia primaria; queda en "decisiones no resolubles".
- **D5 — Universo y proyección horaria: criterio único.** El memo declara las dos
  lecturas: calendario (`42 × 88 ≈ 3.700`; `43,82 s × 3.700 / 3.600 ≈ 45,0 h`) y
  hábiles (≈ 63 días hábiles → `≈ 2.646`; `≈ 32,2 h`). Decisión propuesta: adoptar
  el criterio de DÍAS HÁBILES como valor canónico, por coherencia con la tasa
  diaria tomada de una semana laboral; el valor calendario se conserva como
  `retirado`. Propagación obligatoria a `04:45`, `08:14` y `09:24`.
- **D6 — Paradigma métrico.** La verdad de referencia es multietiqueta
  (`107/200` casos del corpus con más de un sector de verdad, `53,5 %`), y el
  clasificador emite UNA etiqueta principal (más etiquetas adicionales
  **predichas** en `8` casos, que NO constituyen la referencia). Set métrico final: primario monoetiqueta = exactitud estricta
  `0,7350` + macro-F1 `0,5207`; secundario multietiqueta = subset accuracy `0,43`
  y Hamming `0,3586`, reportados SOLO contra la referencia multietiqueta y con la
  advertencia de penalización estructural; micro-F1 `0,6654` se conserva como
  métrica multietiqueta, no como equivalente de la exactitud. El recálculo se hace
  desde `predicciones.json` (ver D1); queda definido en el memo.
- **D7 — Clase "Bases de Datos" (n=1).** Decisión propuesta: declararla NO
  ESTIMABLE y excluirla del macro-F1 reportado como métrica de umbral, reportando
  además el macro-F1 con las cinco clases y el macro-F1 sobre las cuatro
  estimables; el umbral 0,85 se informa sobre métricas sin la clase no estimable.
  Alternativa descartada: dejar el `0,0000` dentro del macro (cero estructural).
- **D8 — Capacidad nueva en lugar de `skip_specs`.** Se introduce la capability
  `tesis-numeros-canonicos` (no una modificación de `tesis-document`) porque el
  memo es un artefacto nuevo de gobernanza numérica con contrato propio; así las
  ramas posteriores tienen un ancla de spec. Alternativa descartada: `skip_specs: true`
  (dejaría el memo sin contrato verificable).

## Risks / Trade-offs

- **[Riesgo] Datos primarios ausentes.** No hay registro por caso de la
  intervención humana ni del gate aplicado caso a caso. → **Mitigación**: la
  contingencia se reconstruye solo con `predicciones.json`; lo que no sea derivable
  se declara en "decisiones no resolubles" con la decisión editorial adoptada
  (retirar el 9,5 % es la propuesta, sujeta a que el autor aporte la tabla primaria).
- **[Riesgo] Drift numérico entre ramas.** Varias ramas reescriben `04/07/08/09` y
  podrían reintroducir valores stale. → **Mitigación**: el memo es la única fuente;
  cada valor lleva fuente y estado; se cita el SHA-256 del corpus y el commit de
  revisión; cada rama consumidora debe verificar contra el memo.
- **[Riesgo] Conflicto con c-104.** c-104 (aún no creada) reescribirá el texto con
  criterios propios y podría fijar números distintos. → **Mitigación**: c-102 se
  declara Gate 0 y PRERREQUISITO de c-104; c-104 MUST consumir la tabla canónica y
  no redefinir valores; cualquier divergencia debe resolverse actualizando el memo,
  no el `.tex` por separado.
- **[Trade-off] El memo congela el 9,5 % como retirado.** Si el autor aporta el
  registro primario, el memo debe actualizarse (upsert) y propagarse; el costo es
  aceptable frente al riesgo de defender una cifra no sustentada.
- **[Trade-off] Adoptar días hábiles reduce la proyección de 45,0 h a ~32,2 h.**
  Es una cifra menos vistosa pero coherente con la tasa diaria; el dictamen lo
  respalda explícitamente.