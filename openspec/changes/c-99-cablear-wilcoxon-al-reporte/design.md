## Context

Estado actual verificado (ver `proposal.md` — Why para la motivación):

- `evaluation/stats.py` implementa `wilcoxon_tiempos_detallado` (C-77) con la convención correcta (`W = min(T+, T−)`, `r = (T+ − T−) / (n(n+1)/2)`); su único consumidor son `evaluation/tests/test_stats.py`.
- `evaluation/run_evaluation.py::generar_reporte()` (líneas ~164-301) construye el Markdown solo con métricas de clasificación; no importa `evaluation.stats`.
- `evaluation/report.md` tiene una sección "Normalidad (Shapiro-Wilk)" (líneas ~55-70) agregada a mano en C-95 y NO emitida por el generador: regenerar el reporte la borra.
- `evaluation/corpus.py::_a_float` (líneas ~138-154) parsea `tiempo_manual_s` y `tiempo_automatizado_s`; el corpus real tiene 200/200 pares no nulos y `canal_origen` con tres valores (`formulario web` 53, `correo electrónico` 66, `llamada telefónica` 81). Hay 12 pares invertidos/empatados.
- El fixture de test (`evaluation/tests/fixtures/corpus_fixture.json`) usa valores de canal cortos (`correo`, `formulario`, `llamada`), distintos de los del corpus real: la segmentación debe derivarse del valor crudo de `canal_origen`, sin mapa fijo.
- La suite de evaluación es autocontenida: `evaluation/pytest.ini`, `evaluation/requirements.txt` (incluye `scipy>=1.13`), `FakeClassifier`, sin Gemini. Se corre desde `evaluation/`.

## Goals / Non-Goals

**Goals:**

- Que `python run_evaluation.py` regenere `evaluation/report.md` con una sección "Tiempos" aditiva (normalidad + Wilcoxon + efecto + desglose por canal), sin perder la normalidad.
- Que la sección sea determinista y reproducible end-to-end.
- Alinear el spec `evaluation-framework` con el nuevo comportamiento.
- Mantener las métricas de clasificación sin cambios y `_a_float` intacto.

**Non-Goals:**

- Separar el contrato del loader en variantes "clasificación vs tiempos" (hueco (b) del nunca-creado c-50). Queda como follow-up documentado.
- Tocar el backend, el clasificador híbrido o la derivación de `tiempo_automatizado_s`.
- Cambiar la fórmula de Wilcoxon o el efecto rank-biserial (ya corregidos por C-77).
- Modificar `evaluation/corpus.py`, `evaluation/metrics.py` o las métricas de clasificación.
- Introducir dependencias nuevas (`scipy` ya está pinneada).

## Decisions

- **D1 — Normalidad como función pura en `stats.py`, no inline en el runner.** Agregar `shapiro_normalidad(datos)` que devuelve un dataclass con `w`, `p`, `n` (y declara no aplicable si `n < 3`, el mínimo de `scipy.stats.shapiro`). Alternativa descartada: calcularla inline en `generar_reporte`; se descarta porque el spec exige "función pura" y porque así es testeable de forma aislada (Strict TDD).
- **D2 — La sección se deriva del parámetro `corpus` ya existente.** `generar_reporte(predicciones, corpus, output_path)` ya recibe `List[CasoEvaluacion]`, que expone `tiempo_manual_s`, `tiempo_automatizado_s` y `canal_origen`. No hace falta una señal nueva; se extraen los pares desde el corpus en su orden original para mantener determinismo.
- **D3 — SHA-256 del corpus opcional.** La sección manual actual incluye el SHA-256 del corpus. `generar_reporte` no conoce la ruta; se agrega un parámetro opcional `corpus_hash: Optional[str] = None`. `main_con_corpus_real` ya calcula `corpus_hash` (`_compute_corpus_hash`) y lo pasa. Los tests que llaman `generar_reporte` directo sin hash siguen funcionando (la línea se omite).
- **D4 — Formato decimal fijo y orden canónico.** Todos los números con precisión fija (`:.4f`/notación científica para p pequeños) y los canales en orden canónico estable (por conteo descendente y desempate alfabético) para garantizar idempotencia byte a byte entre corridas (regresión que hoy cubre `test_cache_hit_produce_mismo_reporte`).
- **D5 — Reducción conservadora: descuento de 1 s por manual.** `tiempo_manual_s` está redondeado hacia arriba, por lo que el valor real es `manual_true >= manual_reportado − 1`. La reducción reportada usa el valor reportado; la cota conservadora usa `manual − 1` por caso. Se reportan media y mediana de la reducción reportada, la reducción conservadora y el conteo de pares invertidos/empatados. Alternativa descartada: recalcular con un factor arbitrario; se descarta por no ser defendible y no surgir del spec.
- **D6 — Segmentación por `canal_origen` crudo.** Se agrupa por el string tal cual viene en el corpus (sin normalizar ni mapear), porque el fixture usa etiquetas cortas y el corpus real largas. Un canal con menos de 2 pares válidos se marca "no aplicable (n<2)". Un par con `None` en cualquier tiempo se excluye y se contabiliza.
- **D7 — Aditividad estricta.** La sección nueva se inserta después de "Métricas de conjunto" y antes del pie `---`/`_Generado automáticamente..._`. El bloque de clasificación existente no se reordena ni se re-formatea, para no romper asserts por substring ni el determinismo.

## Risks / Trade-offs

- [Regresión de determinismo] La sección nueva podría introducir no-determinismo (floats, orden de canales) → mitigado por D4 (precisión fija y orden canónico) y por los tests de idempotencia.
- [`scipy` ausente en el entorno] `shapiro` y `wilcoxon` importan `scipy` dentro de la función, con error explícito que nombra `evaluation/requirements.txt`; el import perezoso evita romper el resto del runner → mitigado por el mensaje ya existente en `stats.py` y por la dependencia pinneada.
- [Canales con n pequeño] Un canal podría no alcanzar el mínimo de la prueba → mitigado por D6 ("no aplicable"), que evita fabricar resultados.
- [Cambiar el reporte rompe comparaciones byte a byte externas] El reporte cambia al agregar sección; es el objetivo, no una regresión. Las métricas de clasificación deben permanecer idénticas (assert explícito en los tests).
- [La tesis y el reporte divergen] Al cablear, `report.md` pasa a ser la fuente reproducible; conviene que la tesis referencie esta salida. No se modifica la tesis en este change (fuera de alcance).

## Migration Plan

- No hay migración de datos. Se implementa, se regenera `evaluation/report.md` con el corpus real una vez, y se verifica la sección "Tiempos" + normalidad y la no-regresión de clasificación.
- Rollback: revertir los cambios de código de `stats.py`/`run_evaluation.py` y regenerar el reporte.

## Open Questions

Ninguna pendiente que cambie specs, enfoque o desglose de tareas. La única pregunta abierta real (contrato del loader clasificación vs tiempos) se declara como Non-Goal/follow-up, no como decisión diferida de este change.