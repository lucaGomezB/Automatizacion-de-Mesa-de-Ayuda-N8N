> Ejecucion en orden estricto. Rutas relativas a la raiz del repositorio. `REQ` = `App/Backend/requirements.txt`; `CFG` = `openspec/config.yaml`; `KB02` = `knowledge-base/02_descripcion_general.md`; `KB09` = `knowledge-base/09_decisiones_y_supuestos.md`; `BARRIER` = `scripts/preflight/docs_stack_sync.py`; `SUITE` = `scripts/preflight/test_docs_stack_sync.py`. TDD estricto en el Bloque C.

## 1. Red de seguridad y linea base

- [x] 1.1 Ejecutar `python3 scripts/preflight/docs_stack_sync.py` y registrar la salida base: 17/17 PASS, exit 0.
- [x] 1.2 Ejecutar `python3 -m pytest scripts/preflight/ -q` y registrar la linea base: 108 passed.
- [x] 1.3 Registrar las versiones objetivo del PR #42 con `git show origin/dependabot/pip/App/Backend/backend-python-39ad50631f:App/Backend/requirements.txt` y diffearlas contra `REQ`; consignar las seis actualizaciones exactas (code lines identicas al PR).

## 2. Bloque A — tomar el bump de Dependabot

- [x] 2.1 En `REQ` aplicar `fastapi==0.143.3` -> `0.162.0`, `starlette==1.8.0` -> `1.10.0`, `sqlalchemy[asyncio]==2.1.5` -> `2.1.6`, `alembic==1.20.0` -> `1.20.1`, `pydantic-settings==2.16.0` -> `2.16.1`, `google-genai>=2.31.0,<3` -> `>=2.33.0,<3`; verificado: las lineas de codigo son identicas al PR y `uvicorn[standard]==0.54.0` no cambia (`diff` de lineas sin comentario contra el PR = idénticas).
- [x] 2.2 En `REQ` conservar los comentarios y actualizar los que citan una version como hecho vigente y quedarian falsos (la linea de `starlette` y "Ultima verificada"); se anadio la nota del bump de c-149 conservando los registros historicos de c-127/c-97.
- [x] 2.3 Ejecutar `python3 scripts/preflight/docs_stack_sync.py` y registrar la RED del Bloque B: 14/17 PASS con los chequeos 4 (FastAPI `0.143` vs `0.162.0`), 5 (`google-genai >=2.31,<3` vs `>=2.33.0,<3`) y 17 (`02_descripcion_general.md:8,13`, `09_decisiones_y_supuestos.md:21`) en FAIL, exit 1.

## 3. Bloque C — suite hermética de la barrera (TDD estricto)

- [x] 3.1 RED: con el bump de 2.1 aplicado y antes de tocar `SUITE`, ejecutar `python3 -m pytest scripts/preflight/ -q` y registrar los fallos por acoplamiento: `17 failed, 91 passed`, con `assert 4 == 1` (los FAILs extra de los chequeos 4/5/17 se sumaban al drift inyectado). Evidencia de la RED.
- [x] 3.2 GREEN: reescribir en `SUITE` los fixtures (`_arbol_sincronizado`, `_contenido_arbol`, `_VERS_BASE`) para construir un arbol sintetico autosuficiente con versiones fijas por la propia suite, sin copiar ningun archivo real; redirigir `_literales_volatiles_del_config` al `config.yaml` del fixture. Con el bump de 2.1 todavia aplicado: `python3 -m pytest scripts/preflight/ -q` -> 111 passed. Verificado que no queda lectura real en los fixtures (`rg "shutil|REPO_ROOT / (REQUIREMENTS|COMPOSE|CONFIG)" SUITE` sin coincidencias de copia).
- [x] 3.3 TRIANGULATE: agregadas en `SUITE` (a) `test_un_bump_coordinado_sigue_sincronizado_y_aisla_un_drift` (17/17 PASS y, con un drift, exactamente 1 FAIL), (b) `test_bump_del_solo_pin_de_fastapi_aisla_solo_los_chequeos_de_version` (exactamente 2 FAIL, ambos de version), (c) `test_fixture_no_hereda_los_archivos_reales`. `python3 -m pytest scripts/preflight/ -q` -> 111 passed.
- [x] 3.4 REFACTOR: el mapa de versiones (`_VERS_BASE`) y el constructor de contenido (`_contenido_arbol`) ya son funciones/estructuras puras extraidas; no requirio refactor adicional. `python3 -m pytest scripts/preflight/ -q` en verde tras cada paso.

## 4. Bloque B — espejar las versiones nuevas en la documentacion

- [x] 4.1 En `CFG` `stack.backend.framework` = `FastAPI 0.162 + Uvicorn 0.54` y `stack.inference.model` = `Gemini 3.6 Flash (google-genai >=2.33,<3)`; verificado con `rg -n "0.162|2.33" CFG`.
- [x] 4.2 En `KB02` linea 8 = `FastAPI + Uvicorn | 0.162.0 / 0.54.0` y linea 13 = `` `google-genai` >=2.33,<3 ``; N8N 2.11.2 sin cambios.
- [x] 4.3 En `KB09` linea 21 = `FastAPI 0.162.0 sobre Uvicorn 0.54.0` (DD-06 es una decision VIGENTE: se actualiza la version, no se rotula como historia); verificado con `rg -n "0.162" KB09`.
- [x] 4.4 Ejecutar `python3 scripts/preflight/docs_stack_sync.py` y verificar 17/17 PASS con exit 0 (GREEN del Bloque B).

## 5. OpenAPI y suites de regresion

- [x] 5.1 Ejecutar desde `App/Backend/` `python3 -m pytest tests/test_openapi_sync.py -v`: 5 passed; NO hizo falta regenerar `docs/openapi.json`. Caveat: el entorno tiene las dependencias viejas instaladas, de modo que la verificacion corrio contra FastAPI 0.143.3 (ver Duda residual del design y de CHANGES.md).
- [x] 5.2 `cd App/Backend && python3 -m pytest -m "not integration" -q`: 1498 passed, 54 deselected, 1 xfailed (sin regresiones respecto de la linea base de c-148).
- [x] 5.3 `cd App/Backend && ruff check .`: All checks passed.
- [x] 5.4 `cd App/Frontend && npm run test`: 384 passed (59 archivos), sin regresiones.

## 6. Cierre documental y validacion

- [x] 6.1 Agregada en `CHANGES.md` la entrada FASE 42 (`[C-149]`) con alcance (bloques A, B, C), governance (A BAJO; B y C MEDIO), RED/GREEN/TRIANGULATE, barrier 14/17 -> 17/17 y verificaciones; verificado con `rg -n "FASE 42|C-149" CHANGES.md`.
- [x] 6.2 `openspec validate "c-149-actualizar-dependencias-y-endurecer-la-barrera" --strict`: Change is valid.
- [x] 6.3 Tareas marcadas `[x]`; la unica no ejecutada (7.1) queda consignada abajo con su motivo.

## 7. Rollback documentado

- [ ] 7.1 Documentar que `git revert` de los commits del change restaura `REQ`, la documentacion y la suite acoplada, sin tag ni release que deshacer (NO EJECUTADA: no hay commits del change; el arbol queda sin commitear por indicacion del orquestador). — ANOTACION (2026-10-27, c-150 W2): la justificacion "no hay commits del change" quedo OBSOLETA. c-149 se commiteo en f666316 y se fusiono en PR #55 (merge 4d9e072); la verificacion de rollback es MOOT. El texto original se conserva.
