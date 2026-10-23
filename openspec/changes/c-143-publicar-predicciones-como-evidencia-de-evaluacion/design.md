# Design: Publicar las predicciones como evidencia versionada

## Context

Ver `proposal.md` (Why). Las predicciones existen como dos archivos de cache en `evaluation/`: `predicciones.json` (`classifier_version` `hybrid-v3`, `corpus_hash` `1fd17d7e…`, `generated_at` `2026-10-07T22:22:01.947873+00:00`, `corpus_count` 200) y `predicciones_calibracion.json` (`classifier_version` `hybrid-v2`, `corpus_hash` `5f062e14…`, `generated_at` `2026-10-07T20:33:03.438926+00:00`, `corpus_count` 200). El corpus pseudonimizado público es `data/corpus_evaluacion_pseudonimizado.json` (`sha256` `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`). El campo `descripcion` de las predicciones coincide byte a byte con el corpus (200/200). La spec `evaluation-prediction-cache` describe el archivo como cache regenerable y autoinvalidable.

## Goals / Non-Goals

**Goals**
- Publicar una copia congelada, byte-idéntica, de las predicciones como evidencia versionada y auditable.
- Preservar intacta la condición de cache (regenerable) del archivo vivo, manteniéndolo gitignoreado.
- Documentar metadatos y la divergencia de corpus del snapshot de calibración.

**Non-Goals**
- No se regenera ninguna predicción ni se invoca Gemini.
- No se modifica el `.gitignore` ni la lógica del runner de evaluación.
- No se re-mide ni se recalcula ninguna métrica; solo se publica la evidencia existente.

## Decisions

### D1 — Ubicación de la evidencia: `evaluation/evidence/`
Los snapshots se publican bajo `evaluation/evidence/` con nombres descriptivos que codifican versión del clasificador y fecha: `predicciones_hybrid-v3_2026-10-07.json` y `predicciones_calibracion_hybrid-v2_2026-10-07.json`. `evaluation/report.md` ya se versiona como evidencia agregada; `evaluation/evidence/` agrupa la evidencia por caso sin mezclarla con los caches.
- Alternativa descartada: publicar en `data/` (mezcla evidencia con corpus) o versionar directamente el cache (contradice su naturaleza de cache).

### D2 — El cache vivo permanece gitignoreado
`evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` siguen excluidos. Razón: son artefactos regenerables, llevan `generated_at` que cambia en cada corrida y producirían ruido de diff sin valor de evidencia. La evidencia congelada es estable y trazable.

### D3 — Fidelidad byte a byte
El snapshot ES el archivo de origen copiado sin transformación ni renumeración. No se re-serializa el JSON (evita cambios de orden de claves o de espacios). La verificación es la igualdad de `sha256`. Esto permite que la evidencia sea citable por hash.

### D4 — El snapshot de calibración declara corpus divergente
El `corpus_hash` de `predicciones_calibracion.json` (`5f062e14…`) NO coincide con el corpus actual (`1fd17d7e…`): documenta un estado anterior del corpus. El `README.md` lo advierte explícitamente para que el snapshot no se lea como representativo del corpus vigente. El snapshot de `hybrid-v3` sí coincide con el corpus actual.

## Risks / Trade-offs

- **Confusión entre evidencia y cache** → nombres con versión y fecha, y `README.md` que distingue snapshot (versionado, inmutable por hash) de cache (regenerable, gitignoreado).
- **Lectura errónea del snapshot de calibración** como estado vigente → advertencia explícita en el README sobre el `corpus_hash` divergente.
- **PII residual** → mitigado: el corpus pseudonimizado ya es público y las descripciones son byte-idénticas; la evidencia no agrega datos nuevos.

## Migration Plan

1. Crear `evaluation/evidence/` y copiar ambos archivos byte a byte.
2. Escribir `evaluation/evidence/README.md` con metadatos, join por caso y advertencia de calibración.
3. Verificar: hash de cada snapshot == hash del origen; los snapshots no están ignorados; los caches sí lo están.
4. Validar la spec y el change con `openspec validate --strict`.
5. **Rollback**: eliminar `evaluation/evidence/`; no hay migración de datos ni cambios de esquema.

## Open Questions

- Ninguna que cambie specs, enfoque o desglose de tareas.
