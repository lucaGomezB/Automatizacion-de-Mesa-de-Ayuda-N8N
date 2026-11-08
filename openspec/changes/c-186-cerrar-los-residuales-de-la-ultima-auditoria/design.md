# Design: Cerrar los residuales de la última auditoría

## Contexto

El dictamen CONEAU del 2026-10-28 sobre `v1.2.5` (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`)
señala cinco residuales de forma, redacción y trazabilidad. Son correcciones de documento:
no cambian datos, código, corpus ni valores canónicos. Este design fija, por residual, la
ubicación exacta y la corrección planificada.

## Decisiones por residual

### D1 — Xuan et al. (2025) en la sección 3.3

- **Ubicación**: `docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex:56`.
- **Estado actual**: la oración afirma que "el rendimiento de clasificación depende
  fuertemente del idioma del corpus" y agrupa `\parencite{ahuja2023mega, xuan2025mmluprox}`.
- **Dictamen**: MMLU-ProX es un benchmark de razonamiento de opción múltiple, no de
  clasificación (MEGA sí incluye tareas de clasificación); la atribución es imprecisa.
- **Corrección**: separar la afirmación de CLASIFICACIÓN (respaldada por MEGA,
  `ahuja2023mega`) de la de rendimiento multilingüe general (`xuan2025mmluprox`), sin
  atribuir a Xuan una afirmación sobre clasificación. No se agrega ni quita bibliografía.

### D2 — Sokolova y Lapalme (2009) como fuente que "confirma"

- **Ubicación**: `07-resultados.tex:153` ("Estas métricas confirman ... \parencite{Sokolova2009_performance_measures}").
- **Dictamen** (sección 5, obs. 3): una fuente puede fundamentar una métrica, no confirmar
  un resultado propio. La misma fuente ya se cita correctamente por las DEFINICIONES en
  `07-resultados.tex:130`, `02-marco-teorico.tex:78` y `04-marco-metodologico.tex:69`.
- **Corrección**: reformular `:153` para presentar el desempeño desigual como hallazgo
  propio y citar a Sokolova y Lapalme por las definiciones de las métricas; retirar el
  verbo "confirman".

### D3 — Tensión de la sección 9.2 (comparabilidad)

- **Ubicación**: `08-discusion.tex:32` ("no admiten una comparación directa con la
  literatura revisada") frente a `:38` (comparación del F1 macro 0,6508 con "el reportado
  para el inglés").
- **Dictamen** (dimensión 6, obs. viii): la tensión debe resolverse en favor de la primera
  afirmación o acotar explícitamente la segunda.
- **Corrección**: en `:38`, calificar la comparación con el inglés como indirecta y no
  comparable con las cifras de etiqueta única de la literatura revisada, coherente con
  `:32`. No se retira el dato; se le agrega el calificativo faltante.

### D4 — Filas B14 y B16 del Anexo I

- **Ubicación**: `12-anexos.tex:229` (B14) y `:231` (B16).
- **Estado actual**: B14 dice "pendientes (erratas de figuras y `seudonimizado`)" y B16
  "pendiente (fecha de consulta de una referencia)".
- **Evidencia de cierre**: c-163 (recomendaciones 9-13) regeneró las figuras con erratas y
  corrigió `seudonimizado` -> `pseudonimizado` y la fecha de consulta de `ramya2021classifying`;
  c-159 regeneró las figuras del capítulo 5. Verificado en las fuentes: `seudonimizado`,
  "sobre que aspecto" y `categoría_predicha`/`categoría_validada` ya no aparecen.
- **Corrección**: actualizar las filas para declarar esos residuos cerrados por c-159 y
  c-163, sin la palabra "pendiente".

### D5 — Fila `Lím.` (los cinco límites estructurales)

- **Ubicación**: `12-anexos.tex:258` (fila `Lím.` de `tab:anexo-trazabilidad-2810`).
- **Estado actual**: la fila afirma que los cinco límites "se cierran" con la campaña
  complementaria de medición.
- **Evidencia**: c-169 propagó los ítems (a)-(e) con un estado único; el ítem (d)
  validación fuera de muestra quedó como NEGATIVO (sin corpus independiente declarado).
- **Corrección**: reformular la fila para declarar que (d) permanece como limitación
  negativa declarada, no como límite cerrado. No se fabrica un cierre para (d).

### D6 — B9: fechas de las iteraciones Scrumban

- **Ubicación**: `06-implementacion.tex:68` y `12-anexos.tex:224` (fila B9).
- **Recuperabilidad**: NO son recuperables. `docs/diagrams/cronograma.md` documenta
  OQ-1 (RESUELTA, 2026-10-26, confirmada por el autor): el tablero técnico fue Jira y su
  trial se dio de baja sin export; GitHub Projects se usó para coordinación y su campo de
  iteración no es legible con el token local; el autor confirmó que no hubo un número fijo
  de iteraciones. La construcción se representa con dos barras de mes.
- **Corrección**: declarar de forma explícita y consistente que las fechas de las
  iteraciones no son recuperables por ausencia de fuente primaria, como limitación
  declarada (no como pendiente). `06-implementacion.tex:68` ya dice "sin fechar por
  separado"; se agrega la razón (fuente primaria no recuperable) y se alinea la fila B9.

## Gobernanza

- **LOW/MEDIUM (docs-only)**: solo `docs/Tesis/` y el registro de correcciones. Sin
  cambios de código, esquema, migración, configuración, corpus ni valores canónicos.

## Verificación (al aplicar)

- `rg "xuan2025mmluprox"` en `03-estado-del-arte.tex`: solo atribuciones de rendimiento
  multilingüe.
- `rg "confirma" 07-resultados.tex:153`: sin verbo de confirmación atribuido a Sokolova.
- `rg "no admiten una comparación directa"` y la comparación con el inglés: calificadas de
  forma coherente en `08-discusion.tex`.
- `rg "pendiente"` en las filas B9/B14/B16 de `12-anexos.tex`: sin residuos cerrados
  marcados como pendientes.
- Compilación `latexmk` sin errores fatales ni referencias indefinidas; `verify_citations.py`
  PASS; conteo de páginas registrado en `dictamen-correcciones.md`.
- `openspec validate c-186-cerrar-los-residuales-de-la-ultima-auditoria --strict --no-interactive`.

## Rollback

Revertir los cinco archivos de sección y `dictamen-correcciones.md` al commit previo; el
change no altera datos ni artefactos fuera de `docs/Tesis/`.
