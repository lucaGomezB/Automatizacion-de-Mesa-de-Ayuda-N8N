# Tasks: Publicar las predicciones como evidencia versionada

## 1. Crear la evidencia congelada

- [ ] 1.1 Crear el directorio `evaluation/evidence/` — verificación: el directorio existe y no está cubierto por ninguna regla de `.gitignore`
- [ ] 1.2 Copiar `evaluation/predicciones.json` a `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` sin transformación — verificación: `sha256sum` del destino igual al de la fuente
- [ ] 1.3 Copiar `evaluation/predicciones_calibracion.json` a `evaluation/evidence/predicciones_calibracion_hybrid-v2_2026-10-07.json` sin transformación — verificación: `sha256sum` del destino igual al de la fuente

## 2. Documentar la evidencia

- [ ] 2.1 Escribir `evaluation/evidence/README.md` describiendo cada archivo con su `classifier_version`, `corpus_hash` y `generated_at` — verificación: los tres campos figuran por cada snapshot y coinciden con el `cache_meta` real
- [ ] 2.2 Documentar en el README el recálculo por caso sin invocar Gemini (join por `caso_id` con el corpus público `data/corpus_evaluacion_pseudonimizado.json`) — verificación: la instrucción de join es correcta y explícita sobre el campo `id` del corpus
- [ ] 2.3 Agregar en el README la advertencia de que el `corpus_hash` del snapshot de calibración (`5f062e14…`) NO coincide con el corpus actual (`1fd17d7e…`) — verificación: la advertencia es explícita y cita ambos hashes

## 3. Especificación

- [ ] 3.1 Escribir el delta spec `specs/evaluation-prediction-cache/spec.md` con el requisito de snapshot versionado y cache vivo gitignoreado — verificación: el delta usa `## ADDED Requirements` y escenarios WHEN/THEN bien formados

## 4. Verificación y validación

- [ ] 4.1 Confirmar que `.gitignore` quedó sin cambios y que el cache vivo sigue ignorado (`git check-ignore evaluation/predicciones.json`) — verificación: ambos caches devueltos como ignorados
- [ ] 4.2 Confirmar que los snapshots NO están ignorados (`git check-ignore evaluation/evidence/*.json` no devuelve nada) — verificación: Git no reporta los snapshots como ignorados
- [ ] 4.3 Ejecutar `openspec validate c-143-publicar-predicciones-como-evidencia-de-evaluacion --strict` — verificación: PASS
- [ ] 4.4 Ejecutar `openspec validate --changes --strict` — verificación: todos los changes pasan

## 5. Cierre

- [ ] 5.1 Commit local de la evidencia y el change; NO push — verificación: `git status` limpio tras el commit y sin push
- [ ] 5.2 Registrar como follow-up pendiente la incorporación de c-143 a `CHANGES.md` (bloqueada por el PR #40) — verificación: la nota figura en el `proposal.md`
