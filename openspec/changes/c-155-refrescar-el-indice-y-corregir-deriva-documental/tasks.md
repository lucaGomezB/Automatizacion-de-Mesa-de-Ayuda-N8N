## 1. Refrescar el indice CHANGES.md

- [x] 1.1 Actualizar la entrada de C-151 a `ARCHIVADO (2026-10-28, BAJO)` y quitar "pendiente de archive" del encabezado y de la cita de la FASE 44; verificar que no queda la frase "pendiente de archive" asociada a C-151
- [x] 1.2 Actualizar la entrada de C-153 a `ARCHIVADO (2026-10-28, HIGH)` con 42/42 tareas; verificar que no queda "EN APLICACION" asociado a C-153
- [x] 1.3 Agregar la entrada de C-152 (`corregir-deriva-documental-knowledge-base-y-guia-n8n`) como `ARCHIVADO (2026-10-28, 12/12)` con bloques Scope, Verificacion, Rollback y Leer antes; verificar que el commit `76695e6` figura como fuente
- [x] 1.4 Agregar la entrada de C-154 (`corregir-el-harness-de-la-ablacion-paga`) como `ARCHIVADO (2026-10-28, 21/21)` con bloques Scope, Verificacion, Rollback y Leer antes; verificar que el commit `a493083` figura como fuente
- [x] 1.5 Agregar el encabezado `FASE 46 — Regularizacion del indice (C-152, C-154)` agrupando 1.3 y 1.4 segun la decision D2 del design; verificar que el formato coincide con las FASE existentes
- [x] 1.6 Actualizar la linea Total, la linea Fases, la numeracion y los dos parrafos de "Estado actual" para que alcancen C-154, citen las FASES 43-46 y sean consistentes con `openspec/changes/archive/`; verificar con `ls openspec/changes/archive/ | wc -l` y `openspec list --json`
- [x] 1.7 Verificar que las actualizaciones fechadas previas de CHANGES.md quedan integras y que no se introduce ningun pictograma ni la marca U+2713

## 2. Corregir la deriva de la base de conocimiento

- [x] 2.1 Corregir `knowledge-base/07_flujos_principales.md` linea 31 para que el nodo JS del canal correo no se describa como "hoy placeholder", dado que C-04/C-05 estan archivados; verificar leyendo el Flujo 2 completo
- [x] 2.2 Corregir el Flujo 3 (`knowledge-base/07_flujos_principales.md` lineas 42-43) para describir la resolucion por la cascada `HybridClassifier` del backend (C-72) y rotular como historico el `AI Agent`/Redis/bucle de refinamiento retirados; verificar que no queda ningun componente retirado descrito como vigente
- [x] 2.3 Corregir `knowledge-base/03_actores_y_roles.md` linea 28 para incluir el modo de visibilidad SECTOR ademas de PROPIO, GLOBAL y VACIO, citando `App/Backend/app/services/role_policy.py:38` e `incident_visibility.py`; verificar que la frase "el aislamiento por sector NO existe" no persiste como vigente
- [x] 2.4 Verificar que los cinco strings canonicos de sector y los valores del stack citados en ambos archivos quedan intactos; ejecutar `python3 scripts/preflight/docs_stack_sync.py` y confirmar que no hay FAIL nuevos

## 3. Alinear docs/por_implementar.md

- [x] 3.1 Actualizar el encabezado de estado (linea 3) para reflejar la revision actual, o rotular explicitamente como historicas las secciones que no se puedan confirmar
- [x] 3.2 Corregir el umbral retirado `< 0.90` (linea 18) al umbral vigente de revision humana `0.70` y, donde corresponda, al punto de operacion del cortocircuito `0.5166`; verificar contra `App/Backend/app/config/settings.py` (`human_review_threshold`, `deterministic_score_threshold`)
- [x] 3.3 Verificar que el resto de los valores citados en `docs/por_implementar.md` no contradicen `settings.py` ni el estado archivado; registrar en la verificacion final cualquier valor que se haya dejado como historico

## 4. Verificacion final

- [x] 4.1 Ejecutar `openspec validate "c-155-refrescar-el-indice-y-corregir-deriva-documental" --strict --no-interactive` y confirmar que pasa
- [x] 4.2 Barrer los cuatro archivos editados en busca de pictogramas y de U+2713 y confirmar que no hay coincidencias
- [x] 4.3 Confirmar que no se modifico codigo (`git status --porcelain` limitado a los cuatro documentos) ni `requirements.txt` ni `openspec/config.yaml`
