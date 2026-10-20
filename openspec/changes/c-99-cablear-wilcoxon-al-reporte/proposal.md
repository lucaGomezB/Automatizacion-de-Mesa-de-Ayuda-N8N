## Why

`evaluation/stats.py` ya implementa la prueba de Wilcoxon corregida (C-77) y el tamaño del efecto rank-biserial, pero está HUÉRFANA: su único consumidor son sus tests unitarios. `evaluation/run_evaluation.py::generar_reporte()` nunca importa `evaluation.stats` y emite SOLO métricas de clasificación, por lo que `evaluation/report.md` no tiene sección de tiempos. Peor aún, la sección "Normalidad (Shapiro-Wilk)" que hoy exhibe `report.md` fue agregada a mano en C-95 y NO la produce el generador: regenerar el reporte la BORRA. Los números de la tesis se computaron ad hoc, no por este pipeline. Esto rompe la reproducibilidad end-to-end de la evidencia estadística de la tesis.

## What Changes

- Cablear `evaluation/stats.py` en `evaluation/run_evaluation.py`: `generar_reporte()` emite una sección "Tiempos" ADITIVA con normalidad (Shapiro-Wilk), prueba de Wilcoxon (estadístico `W`, `T+`, `T−`, valor `p`) y tamaño del efecto rank-biserial `r`.
- Incorporar el contraste de normalidad de Shapiro-Wilk como función pura en `evaluation/stats.py` (hoy la normalidad solo existe como comando ad-hoc en `report.md` y en la tesis).
- Incluir el desglose por canal (`canal_origen`) en el análisis de tiempos, con la misma convención de Wilcoxon, y declarar "no aplicable" cuando un canal tenga menos de dos pares en lugar de fabricar un resultado.
- Emitir en `report.md` la divulgación de redondeo al alza del tiempo manual, la reducción conservadora y la cantidad de pares invertidos, de modo que la evidencia sea reproducible sin edición manual.
- Alinear `openspec/specs/evaluation-framework/spec.md` con este comportamiento mediante un delta spec (runner + análisis de tiempos + divulgación + segmentación por canal).
- Mantener intactas las métricas de clasificación y NO debilitar `evaluation/corpus.py::_a_float` (requisito numérico de `corpus-n8n-ingest`).

Fuera de alcance (documentado como no-goal): separar el contrato del loader en variantes "clasificación vs tiempos" (fue el hueco (b) del nunca-creado c-50). No se toca el backend, ni el clasificador, ni la derivación de tiempos del corpus.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `evaluation-framework`: el runner MUST emitir una sección "Tiempos" (normalidad, Wilcoxon con `W`/`T+`/`T−`/`p`/`r` y desglose por canal) en `evaluation/report.md`, de forma reproducible; el análisis de tiempos incorpora Shapiro-Wilk como función pura; la divulgación de redondeo/sensibilidad/pares invertidos se emite en `report.md`; se agrega la segmentación por canal.

## Impact

- `evaluation/run_evaluation.py`: `generar_reporte()` incorpora la sección de tiempos y recibe el SHA-256 del corpus (parámetro opcional).
- `evaluation/stats.py`: nueva función pura de normalidad y utilidades de reducción/invertidos.
- `evaluation/report.md`: regenerado con sección "Tiempos" y normalidad emitidas por el pipeline.
- `evaluation/tests/`: tests nuevos (Strict TDD, primero en rojo) para normalidad, sección de tiempos, determinismo, no-regresión de clasificación, divulgación y desglose por canal.
- `openspec/specs/evaluation-framework/spec.md`: delta spec.
- NO afecta clasificación, corpus loader, backend ni dependencias nuevas (`scipy` ya está pinneada en `evaluation/requirements.txt`).