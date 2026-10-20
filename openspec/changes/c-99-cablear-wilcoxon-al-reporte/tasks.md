## 1. Red — tests de normalidad en `evaluation/stats.py`

- [x] 1.1 Escribir en `evaluation/tests/test_stats.py` un test FALLIDO para `shapiro_normalidad(datos)`: una serie aproximadamente normal y una fuertemente sesgada (por ejemplo uniforme/exponencial) devuelven `W`, `p` y `n`, y el caso sesgado rechaza la normalidad (`p < 0.05`). Verificar RED con `cd evaluation; pytest tests/test_stats.py -k shapiro`.
- [x] 1.2 Escribir un test FALLIDO para la serie con menos del mínimo de pares (n < 3): declara no aplicable (o lanza error controlado) en lugar de producir `W`/`p`. Verificar RED con `cd evaluation; pytest tests/test_stats.py -k shapiro`.

## 2. Red — tests de la sección "Tiempos" en el reporte

- [x] 2.1 Escribir un test FALLIDO en `evaluation/tests/test_run_evaluation.py`: `generar_reporte` emite la sección "Tiempos" con "Shapiro", "Wilcoxon", y los campos `W`, `T+`, `T−`, `p` y el tamaño del efecto. Verificar RED con `cd evaluation; pytest tests/test_run_evaluation.py -k tiempos`.
- [x] 2.2 Escribir un test FALLIDO de determinismo: dos corridas con cache válido producen un `report.md` idéntico byte a byte Y ambas incluyen la sección "Tiempos" (extender el patrón de `test_cache_hit_produce_mismo_reporte`). Verificar RED.
- [x] 2.3 Escribir un test FALLIDO de no-regresión: agregar la sección de tiempos NO altera exactitud, matriz 5x5, F1 macro/micro, subset accuracy ni Hamming loss (comparar los valores del bloque de clasificación antes/después o contra constantes esperadas del fixture). Verificar RED.
- [x] 2.4 Escribir un test FALLIDO de divulgación: la sección de tiempos declara que `tiempo_manual_s` está redondeado al alza, reporta una reducción conservadora además de la reportada y reporta la cantidad de pares invertidos/empatados. Verificar RED.
- [x] 2.5 Escribir un test FALLIDO de desglose por canal: el reporte lista por cada `canal_origen` su cantidad de pares y el resultado de Wilcoxon (o "no aplicable" si hay menos de 2 pares válidos). Verificar RED.

## 3. Green — implementar normalidad y sección de tiempos

- [x] 3.1 Implementar `shapiro_normalidad(datos)` pura en `evaluation/stats.py` (dataclass de resultado con `w`, `p`, `n`; no aplicable con `n < 3`); verificar que 1.1 y 1.2 pasan.
- [x] 3.2 Implementar en `evaluation/stats.py` las utilidades puras de reducción/invertidos (reducción reportada media/mediana, reducción conservadora con descuento de 1 s, conteo de pares invertidos); verificar con tests unitarios.
- [x] 3.3 Implementar en `evaluation/run_evaluation.py` el armado de la sección "Tiempos" (normalidad + Wilcoxon con `W`/`T+`/`T−`/`p`/`r` + divulgación + desglose por canal), cableando `evaluation.stats` y agrupando por `canal_origen` crudo; manejar pares con tiempo nulo y canales con n < 2 como "no aplicable". Verificar que 2.1, 2.4 y 2.5 pasan.
- [x] 3.4 Cablear la sección en `generar_reporte` (insertarla tras "Métricas de conjunto") y agregar el parámetro opcional `corpus_hash`; pasar el hash desde `main_con_corpus_real` para emitir el SHA-256 del corpus. Verificar que 2.2, 2.3 y `cd evaluation; pytest` pasan.

## 4. Triangulate

- [x] 4.1 Añadir un caso de triangulación para `shapiro_normalidad` y para la reducción: serie con empates y pares invertidos con valores conocidos; verificar valores esperados.
- [x] 4.2 Añadir un caso de triangulación para el reporte con un corpus sintético de tiempos y canales conocidos (incluyendo un canal con n < 2): verificar `W`, `T+`, `T−`, `p`, `r`, reducción conservadora y desglose por canal contra valores calculados a mano.

## 5. Refactor

- [x] 5.1 Extraer constantes de formato y nombres; eliminar duplicación entre el bloque global y el por canal; correr `cd evaluation; pytest` y confirmar que sigue verde tras cada paso.

## 6. Regenerar y verificar evidencia

- [ ] 6.1 Regenerar `evaluation/report.md` end-to-end desde `evaluation/` con el corpus real (`python run_evaluation.py`, usando el cache válido o `--confirm-paid` según corresponda) y verificar que la sección "Tiempos" y "Normalidad (Shapiro-Wilk)" están presentes y que las métricas de clasificación no cambiaron. — BLOQUEADA: el cache `evaluation/predicciones.json` es INVÁLIDO (`cache_meta.corpus_hash=5f062e14…` ≠ hash actual `1fd17d7e…`); el runner iría al camino pago. No se regeneró `report.md` (sin `--confirm-paid`, sin gasto). Evidencia alternativa en `/tmp` (determinismo + sección + no-regresión) documentada en el reporte de apply.
- [ ] 6.2 Regenerar dos veces y confirmar que el reporte es idéntico (idempotencia) y que la normalidad ya no depende de edición manual. — BLOQUEADA por la misma causa que 6.1. La idempotencia del generador SÍ se verificó en `/tmp` (dos salidas byte a byte idénticas) sobre el corpus real; `report.md` no se sobrescribió.
- [x] 6.3 Correr la suite completa de evaluación desde `evaluation/` (`cd evaluation; pytest`) y confirmar 0 fallos. — 141 passed, 1 failed pre-existente y no atribuible a este change (`test_umbral_settings_oof.py::test_settings_tau_deriva_del_oof_del_corpus` falla idéntico con los cambios en stash; exige `Settings.cost_guard_caller_hmac_key`).

## 7. Verificación de especificación y no-goal

- [x] 7.1 Verificar que el no-goal (separar el contrato del loader clasificación vs tiempos, hueco (b) de c-50) está documentado en `proposal.md`/`design.md` como follow-up.
- [x] 7.2 Verificar el change con `openspec validate c-99-cablear-wilcoxon-al-reporte --strict` y confirmar que el delta de `evaluation-framework` es válido.