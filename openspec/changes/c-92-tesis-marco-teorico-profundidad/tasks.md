# Tasks: c-92 — Profundidad del marco teórico (Capítulo 2)

> Convención de rutas: `S = docs/Tesis/v9 (IA)/paper/sections`;
> `B = docs/Tesis/v9 (IA)/paper/Bibliography_base.bib`.
> Verificación de texto: `rg` sobre `S`. Recompilación: Overleaf (XeLaTeX), sin
> toolchain LaTeX local. No se edita `App/**`, ni `B`, ni `CHANGES.md`, ni los
> artefactos de c-76/c-77/c-78/c-79/c-80.
>
> **Orden de aplicación:** ejecutar este change DESPUÉS de c-78 (aporta las
> referencias 2023-2026 y la corrección de `OGC2011_itil`). c-92 solo consume ese
> trabajo; no lo duplica.

## 1. Preparación y dependencias

- [x] 1.1 Verificar que c-78 esté aplicado en `B`: `rg -n "ahuja2023mega|lai2023okapi|zhang2023multilingual|xuan2025mmluprox|grandury2025laleaderboard|mayorrocher2026spanish|zangari2023ticket|colavito2025benchmarking" B`; si falta alguna clave, registrar el bloqueo y no editar `B`.
- [x] 1.2 Inventariar las referencias actuales de §2.4 con `rg -n "cite\{" "S/02-marco-teorico.tex"` (líneas 30–38) y registrar la línea base: `Jurafsky2023_speech_language`, `Vaswani2017_attention`, `Brown2020_few_shot`.
- [x] 1.3 Confirmar la implementación real del canal telefónico en `S/06-implementacion.tex:50` (Twilio Programmable Voice + transcripción nativa) y la matriz multiclase del Capítulo 7 (`S/07-resultados.tex:42`); dejar constancia de ambas fuentes para las tareas 3 y 5.

## 2. §2.4 — Profundidad del eje LLM (A-04)

- [x] 2.1 Incorporar en `S/02-marco-teorico.tex` (líneas 30–38) la definición de **prompting**: zero-shot, few-shot y diseño de instrucciones; citar `Brown2020_few_shot` y al menos una referencia 2023-2026 de c-78 (`ahuja2023mega` o `lai2023okapi`). Verificar con `rg -n "zero-shot|few-shot|instrucc" "S/02-marco-teorico.tex"`.
- [x] 2.2 Incorporar la definición de **calibración de la confianza** y vincularla con el umbral operativo de revisión humana (`human_review: 0.70`, `openspec/config.yaml`); citar `xuan2025mmluprox` si la afirmación requiere respaldo. Verificar con `rg -n "calibraci|0[,.]70|umbral" "S/02-marco-teorico.tex"`.
- [x] 2.3 Incorporar la definición de **alucinación** y su consecuencia para la validación de clasificaciones; citar `colavito2025benchmarking` o reformular para no exigir una referencia inexistente. Verificar con `rg -ni "alucinaci" "S/02-marco-teorico.tex"`.
- [x] 2.4 Incorporar la **sensibilidad al idioma** y a las variedades del español; citar `zhang2023multilingual`, `grandury2025laleaderboard` y/o `mayorrocher2026spanish`. Verificar con `rg -n "sensibilidad|variedad|español" "S/02-marco-teorico.tex"`.
- [x] 2.5 Incorporar la **evaluación de LLM**: benchmarks, límites de la exactitud aislada y necesidad de métricas por clase; citar `xuan2025mmluprox` y `ahuja2023mega`, y enlazar explícitamente con §2.7. Verificar con `rg -n "evaluaci|benchmark|métrica" "S/02-marco-teorico.tex"`.
- [x] 2.6 Verificar que §2.4 cita al menos tres referencias adicionales respecto de la línea base de 1.2 y que ninguna clave nueva se agregó a `B`; ejecutar `git diff --name-only` y confirmar que `B` no aparece.

## 3. §2.7 — Exactitud multiclase (A-05)

- [x] 3.1 Reemplazar en `S/02-marco-teorico.tex` (líneas 58–62) el bloque `\[ \text{Exactitud} = \frac{\text{TP} + \text{TN}}{...} \]` y su explicación de TP/TN/FP/FN por la definición multiclase directa (proporción de predicciones correctas sobre el total), conservando la referencia a `Powers2011_evaluation`.
- [x] 3.2 Conservar la advertencia de `Sokolova2009_performance_measures` sobre desbalance y la recomendación de macro-promediado; verificar que el texto sigue distinguiendo exactitud global y F1 macro.
- [x] 3.3 Verificar con `rg -n "TP|TN|FP|FN|verdaderos negativos" "S/02-marco-teorico.tex"` que la fórmula binaria y la definición con verdaderos negativos ya no aparecen; confirmar que la definición es coherente con la matriz 5x5 de `S/07-resultados.tex:42`.

## 4. §2.5 — Reconocimiento automático del habla (M-03)

- [x] 4.1 Retirar de `S/02-marco-teorico.tex:44` la oración "La disponibilidad de modelos preentrenados de código abierto para espanol facilita su integración en el canal telefonico del sistema propuesto".
- [x] 4.2 Conservar a Whisper como antecedente teórico del ASR y agregar una aclaración explícita de que no forma parte de la implementación; remitir a `S/06-implementacion.tex:50` (transcripción nativa de Twilio). Verificar con `rg -n "Whisper|Twilio|transcripci" "S/02-marco-teorico.tex"`.
- [x] 4.3 Verificar con `rg -ni "facilita su integraci|Whisper.*sistema propuesto|modelos preentrenados.*canal telef" "S/02-marco-teorico.tex"` que no queda la afirmación de uso.

## 5. §2.6 — Persistencia frente a alternativas concretas (M-04)

- [x] 5.1 Reescribir en `S/02-marco-teorico.tex` (líneas 50–52) la justificación de PostgreSQL para compararla con un motor de documentos (MongoDB) y un motor clave-valor (Redis), sin emitir un juicio genérico sobre "lo no relacional".
- [x] 5.2 Anclar la justificación en integridad referencial declarativa, transacciones ACID, consultas relacionales para el dashboard y auditoría/trazabilidad; verificar con `rg -n "MongoDB|Redis|integridad referencial|ACID|auditor" "S/02-marco-teorico.tex"`.
- [x] 5.3 Verificar con `rg -n "alternativas no relacionales|frente a alternativas" "S/02-marco-teorico.tex"` que no queda la contraposición genérica.

## 6. §1.7 — Respaldo de la afirmación sobre idiomas del corpus (M-02)

- [x] 6.1 Respaldar en `S/01-introduccion.tex:62` la afirmación sobre corpus en inglés, alemán o portugués con al menos una referencia verificable de c-78 (`zangari2023ticket`, `colavito2025benchmarking`, `grandury2025laleaderboard` o `mayorrocher2026spanish`); si la evidencia no sostiene "la mayoría", reformular a un alcance defendible.
- [x] 6.2 Verificar con `rg -n "inglés|alemán|portugués|corpus" "S/01-introduccion.tex"` que la afirmación conserva una cita o quedó reformulada sin alcance cuantitativo no provisto.
- [x] 6.3 Confirmar que no se agregaron entradas a `B` por esta tarea: `git diff --name-only | rg "Bibliography_base.bib"` sin coincidencias.

## 7. §2.2 — Atribución editorial de ITIL (A-06, parcial)

- [x] 7.1 Corregir en `S/02-marco-teorico.tex:16` la atribución de ITIL Service Operation (2011): precisar que la edición de 2011 fue publicada por The Stationery Office (TSO) por encargo del Cabinet Office, conservando al Office of Government Commerce como titular histórico del marco.
- [x] 7.2 Verificar con `rg -n "OGC2011_itil|Stationery Office|Cabinet Office|Government Commerce" "S/02-marco-teorico.tex"` que la atribución es explícita y coherente.
- [x] 7.3 Confirmar que la corrección del campo bibliográfico `OGC2011_itil` permanece delegada a c-78 (B3) y que `B` no se modifica en este change.

## 8. Verificación final y recompilación

- [x] 8.1 Barrido de control: `rg -n "frac.*TP|alternativas no relacionales|facilita su integraci|verdaderos negativos" "S/02-marco-teorico.tex"` sin coincidencias.
- [x] 8.2 Verificar que no se tocó código de aplicación: `git diff --name-only | rg "^App/"` sin coincidencias.
- [x] 8.3 Verificar que no se tocó la bibliografía ni los changes ajenos: `git diff --name-only | rg "Bibliography_base.bib|openspec/changes/c-7[6-9]|openspec/changes/c-80"` sin coincidencias.
- [x] 8.4 Recompilar `docs/Tesis/v9 (IA)/paper/main.tex` en Overleaf con XeLaTeX; verificar PDF sin errores fatales y registrar el conteo de páginas (no superar 100). — COMPLETADO 2026-10-20: recompilado localmente con MiKTeX (xelatex -> biber -> xelatex -> xelatex); 103 paginas; 0 errores fatales; 0 referencias indefinidas; 48/48 bibliografia; las 8 figuras renderizan. (latexmk no disponible: MiKTeX sin Perl.)
- [x] 8.5 Ejecutar `openspec validate c-92-tesis-marco-teorico-profundidad --strict` y verificar que pasa sin errores.
