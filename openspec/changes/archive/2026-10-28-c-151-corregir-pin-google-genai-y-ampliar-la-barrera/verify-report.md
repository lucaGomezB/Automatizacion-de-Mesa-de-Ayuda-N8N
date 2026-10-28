## Verification Report: c-151-corregir-pin-google-genai-y-ampliar-la-barrera

**Date**: 2026-10-28
**Tasks**: 20/20 complete (`openspec list --json`: `completedTasks=20`, `totalTasks=20`, `status=complete`; conteo manual `- [x]` = 20, `- [ ]` = 0)
**Verification mode**: independiente y adversarial (no se confio en los checkboxes; cada afirmacion se reprodujo con comandos propios)

### Test Results (ejecutados por el verificador)

| Comando | Resultado observado | Esperado | Estado |
|---------|---------------------|----------|--------|
| `python3 scripts/preflight/docs_stack_sync.py` | `RESULT: 17/17 chequeos en PASS`, `EXIT=0` | 17/17 PASS, exit 0 | PASS |
| `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` | `67 passed in 1.42s` | 67 passed | PASS |
| `python3 -m pytest scripts/preflight -q` | `115 passed in 2.26s` | 115 passed | PASS |
| `openspec validate "c-151-..." --strict --no-interactive` | `Change '...' is valid`, `VALIDATE_EXIT=0` | valido | PASS |

La barrera imprime **exactamente 17** chequeos (conteo de `def _check_` = 17; lista de `check_docs` = 17 entradas; no existe chequeo 18).

### Ground-truth claims (contrastados contra los archivos reales)

| Claim | Evidencia observada | Estado |
|-------|---------------------|--------|
| `docs/parameters_gemini.md` linea 5 (`Versión de cliente`) = `>=2.33,<3` | linea 5: `Versión de cliente: \`google-genai >=2.33,<3\` ...` | PASS |
| `docs/parameters_gemini.md` linea 101 (nota "valor vigente") = `>=2.33,<3` | linea 101: `... y \`google-genai >=2.33,<3\`.` | PASS |
| Historial de Cambios intacto con referencias historicas | Diff de `docs/parameters_gemini.md` = solo 2 lineas (5 y 101). Encabezado de linea 98 sin tocar; `2.5 Flash` se conserva en linea 106 | PASS |
| `App/Backend/requirements.txt:42` = `google-genai>=2.33.0,<3` (fuente de verdad) | `sed -n '42p'` → `google-genai>=2.33.0,<3` | PASS |
| Existe helper puro `_restricciones_genai_no_compatibles(rutas, genai_req)` | `docs_stack_sync.py:480` | PASS |
| `_check_versiones_componentes` aplica el helper sobre KB ∪ `DOCS_REFERENCIA` para google-genai | `_check_versiones_componentes(..., referencia_paths)` invoca `_restricciones_genai_no_compatibles(_archivos_superficie(kb_dir, referencia_paths), genai_req)`; N8N/FastAPI/Uvicorn siguen sobre `_leer_superficie_kb(kb_dir)` | PASS |
| Sin hardcodear `2.31`/`2.33` en el chequeo | `rg -n "2\.31\|2\.33" scripts/preflight/docs_stack_sync.py` → sin coincidencias (RC=1) | PASS |
| `docs/n8n-workflow-guide.md:767` (`N8N 2.25.7`) no produce FAIL | linea 767 confirmada; barrera sigue `17/17 PASS` | PASS |
| Barrera de 17 (sin chequeo 18) | 17 `_check_` + lista de 17; `rg "chequeo 18\|_check_.*18"` → NONE | PASS |
| Sin emojis en archivos cambiados | scan de rango emoji sobre `docs/parameters_gemini.md`, `docs_stack_sync.py`, `test_docs_stack_sync.py`, `CHANGES.md` y el change dir → sin coincidencias | PASS |

### Adversarial checks (intentos de falsacion)

- **RED genuino**: se copio el repo a `/tmp`, se revirtio SOLO `docs_stack_sync.py` a `HEAD` (helper `_restricciones_genai_no_compatibles` ausente) y se corrio el test RED. Resultado: `1 failed, 66 deselected` con `AssertionError: Se esperaba al menos un FAIL ... assert []` — el chequeo 17 pre-c-151 NO escaneaba el material de referencia. RED confirmado genuino. El test es significativo: afirma `_assert_fails_naming(checks, "parameters_gemini.md")` (nombra el archivo), `_assert_fails_naming(checks, "google-genai >=2.31,<3")` (nombra la restriccion) y `_solo_un_fail(checks)` (exactamente un FAIL). PASS.
- **Ningun test existente debilitado**: el diff de `test_docs_stack_sync.py` toca 3 hunks de tests preexistentes, todos con el MISMO patron: bump de la linea base `_VERS_BASE` (`>=2.31.0,<3`/`>=2.31,<3` → `>=2.33.0,<3`/`>=2.33,<3`) y los anclajes de `_mutar` correspondientes (`test_chequeo_5...` y `test_chequeo_17_genai_retirado_en_kb_falla`); las aserciones se conservan intactas. Se agregan 4 tests nuevos. 63 + 4 = 67, consistente. PASS.
- **Marcador historico**: `_tiene_marcador("## Historial de Cambios")` = `False`; con el parentetico `(registro historico; antecedentes)` = `True`. El fixture del test de exencion usa la forma con marcador. PASS.
- **Delta spec bien formado**: `## MODIFIED Requirements` + `### Requirement: DOC-005 ...` coincidente con el nombre del spec principal (`openspec/specs/project-documentation/spec.md:285`). El delta es un superset COMPLETO: 18 escenarios (los 17 preexistentes de DOC-005 + 1 nuevo "La restriccion de google-genai del material de referencia se valida contra requirements.txt"). `openspec validate --strict` OK. PASS.

### Spec Compliance — Success Criteria (proposal)

| Criterio | Status | Notas |
|----------|--------|-------|
| Doc cita `>=2.33,<3` en lineas 5 y 101; historial intacto | PASS | Diff = 2 lineas; `2.5 Flash` conservado |
| Suite en verde con test nuevo (falla con 2.31, pasa con 2.33) | PASS | RED reproducido independientemente; 67 passed |
| N8N/FastAPI/Uvicorn siguen limitados a KB; no reporta `n8n-workflow-guide.md:767` | PASS | Diferenciacion de superficie verificada en el diff |
| Con `2.31` la barrera daria FAIL; corregido → 17/17 exit 0 | PASS | `docs_stack_sync.py` real: 17/17, exit 0 |
| `pytest scripts/preflight -q` en verde | PASS | 115 passed |
| `openspec validate --strict` pasa | PASS | VALIDATE_EXIT=0 |

### Spec Compliance — Delta DOC-005 (18 escenarios)

Los 18 escenarios del delta se confrontaron contra el comportamiento implementado. Los 17 heredados permanecen cubiertos por la barrera (17/17 PASS sobre el arbol real y suite de 67 pruebas); el escenario nuevo ("La restriccion de google-genai del material de referencia se valida contra requirements.txt") queda cubierto por los 4 tests nuevos, en particular `test_chequeo_17_genai_no_historico_en_referencia_falla` (FAIL + nombra archivo/linea/restriccion) y `test_chequeo_17_genai_corregido_en_referencia_pasa` (PASS con `>=2.33,<3`). Status global: **PASS**.

### Design Coherence

- **D1 — Corregir ambas ocurrencias vigentes (lineas 5 y 101)**: FOLLOWED. Ambas lineas llevan `>=2.33,<3`.
- **D2 — Ampliar solo la restriccion de `google-genai`, no todo el barrido**: FOLLOWED. El helper se aplica sobre `_archivos_superficie` (KB + referencia) SOLO para google-genai; los bucles de N8N/FastAPI/Uvicorn siguen sobre `_leer_superficie_kb(kb_dir)`.
- **D3 — Reutilizar helpers y regla de exencion; valor esperado derivado, no hardcodeado**: FOLLOWED. Usa `_restricciones_genai_en_linea`, `_restriccion_compatible`, `_lineas_con_marcador`; `genai_req` proviene de `requirements.txt`; sin literales `2.31`/`2.33` en el chequeo.
- **D4 — Un helper puro con superficie parametrizable**: FOLLOWED. `_restricciones_genai_no_compatibles(rutas, genai_req)` pura, invocada una sola vez con la union de superficies; sin duplicacion del bucle.
- **D5 — TDD sobre el arbol sintetico**: FOLLOWED. RED/GREEN/TRIANGULATE con 4 tests nuevos sobre el fixture `_arbol_sincronizado`; el arbol es hermetico (`_VERS_BASE` con `2.33`).

### TDD Cycle Evidence

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 2.1 | `scripts/preflight/test_docs_stack_sync.py` | Unit (barrera) | 63/63 baseline | Genuino (1 failed vs HEAD) | Pasa tras ampliar superficie | 4 casos nuevos | Helper puro, sin duplicacion |

### Summary

- CRITICAL: ninguna. No hay blockers para el archive.
- WARNING: ninguna que bloquee.
- SUGGESTION (RESUELTO 2026-10-28): `test_chequeo_17_genai_laxo_bajo_encabezado_historico_pasa` NO aisla la exencion por ENCABEZADO. El cuerpo del fixture contiene la palabra `antecedente` (marcador de `MARCADORES_HISTORICOS`), por lo que el caso PASA aun con un encabezado pelado sin marcador (verificado: `BARE heading + marker word in body -> findings: []`). El docstring afirma que la exencion proviene del encabezado, pero la asercion no discrimina el origen del marcador. El comportamiento probado (un pasaje con marcador en linea o encabezado queda exento) es correcto y coincide con la linea 101 real; solo el test era mas debil de lo que declaraba. Se fijo la regla del encabezado evitando palabras marcadoras en el cuerpo (ver resolucion abajo).
  - **Resolucion (2026-10-28)**: se edito el cuerpo del fixture a `> El valor vigente es \`google-genai >=2.31,<3\`.` (sin palabras marcadoras); la exencion proviene ahora exclusivamente del encabezado `## Historial de Cambios (registro historico; antecedentes)`. Verificado: `_tiene_marcador` del cuerpo = `False`; del encabezado = `True`; del encabezado pelado `## Historial de Cambios` = `False`. Test especifico = 1 passed; suite del archivo = 67 passed; `scripts/preflight` = 115 passed; barrera real = 17/17 PASS, exit 0.

**Verdict**: READY FOR ARCHIVE
