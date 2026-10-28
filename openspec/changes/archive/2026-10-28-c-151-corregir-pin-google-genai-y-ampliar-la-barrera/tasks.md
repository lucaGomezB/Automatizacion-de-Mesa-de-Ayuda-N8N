> Ejecucion en orden estricto. Rutas relativas a la raiz del repositorio. `PARAMS` = `docs/parameters_gemini.md`; `BARRIER` = `scripts/preflight/docs_stack_sync.py`; `SUITE` = `scripts/preflight/test_docs_stack_sync.py`; `REQ` = `App/Backend/requirements.txt`. TDD estricto en el Bloque B (RED -> GREEN -> TRIANGULATE -> REFACTOR). Gobernanza: BAJO.

## 1. Red de seguridad y linea base

- [x] 1.1 Ejecutar `python3 scripts/preflight/docs_stack_sync.py` y registrar la salida base: 17/17 PASS, exit 0 (el residual aun no se detecta).
- [x] 1.2 Ejecutar `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` y registrar la linea base: 63 passed.
- [x] 1.3 Confirmar el residual con `rg -n "google-genai >=2\\.31" PARAMS` (deben aparecer las lineas 5 y 101) y verificar que la linea 101 esta bajo el encabezado `## Historial de Cambios` (marcador historico) y que la linea 5 esta bajo `## Invocacion de API` (sin marcador); consignarlo.

## 2. Bloque B (RED) — test que falla

- [x] 2.1 En `SUITE`, agregar un test que construya/obre el arbol sintetico con una linea `google-genai >=2.31,<3` en un pasaje NO historico de `docs/parameters_gemini.md` (sin encabezado con marcador) y afirme que el chequeo 17 (`_check_versiones_componentes` o su resultado en `run_docs_stack_sync`) devuelve FAIL nombrando `parameters_gemini.md`; verificar la RED ejecutando `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` (el test debe fallar con la implementacion actual, porque el chequeo 17 no escanea el material de referencia).
- [x] 2.2 Registrar la evidencia de la RED (nombre del test, salida `assert`/FAIL observado) en el reporte del change.

## 3. Bloque B (GREEN) — ampliar la superficie de la restriccion de google-genai

- [x] 3.1 En `BARRIER`, extraer el escaneo de la restriccion de `google-genai` a un helper puro que reciba la lista de rutas y el pin derivado de `requirements.txt` (diseno D4), reutilizando `_restricciones_genai_en_linea`, `_restriccion_compatible` y `_lineas_con_marcador`.
- [x] 3.2 En `_check_versiones_componentes`, invocar el helper sobre la union de `knowledge-base/**` y `DOCS_REFERENCIA` para la restriccion de `google-genai`, dejando los barridos de N8N, FastAPI y Uvicorn sobre `_leer_superficie_kb(kb_dir)` (diseno D2). Verificar que el test RED de 2.1 ahora PASA y que `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` sigue en verde.
- [x] 3.3 Verificar que el valor esperado no se hardcodea: `rg -n "2\\.33|2\\.31" BARRIER` no debe mostrar versiones literales en el chequeo (solo derivadas de `requirements.txt`).

## 4. Bloque B (TRIANGULATE) — casos que fijan la propiedad

- [x] 4.1 En `SUITE`, agregar el caso positivo: con `google-genai >=2.33,<3` en `parameters_gemini.md` del fixture, el chequeo 17 PASA (`python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` verde).
- [x] 4.2 En `SUITE`, agregar el caso de exencion historica: una restriccion `>=2.31,<3` bajo un encabezado con marcador historico (por ejemplo `## Historial de Cambios`) NO produce FAIL; verificar en verde.
- [x] 4.3 En `SUITE`, agregar el caso de no regresion de alcance: un registro como `N8N 2.25.7` en `docs/n8n-workflow-guide.md` del fixture NO produce FAIL (los barridos de N8N/FastAPI/Uvicorn no se ampliaron al material de referencia); verificar en verde.
- [x] 4.4 Registrar la triangulacion y ejecutar `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` (verde con los nuevos casos).

## 5. Bloque B (REFACTOR)

- [x] 5.1 Revisar que no quede duplicacion del bucle de `google-genai`; confirmar que los helpers son puros y que `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` sigue verde tras cada paso de refactor.

## 6. Bloque A — corregir el documento

- [x] 6.1 En `PARAMS` linea 5, cambiar `Versión de cliente: \`google-genai >=2.31,<3\`` a `>=2.33,<3`; verificar con `rg -n "Versión de cliente" PARAMS` y que la linea quede sin `2.31`.
- [x] 6.2 En `PARAMS` linea 101, cambiar la restriccion citada como valor vigente `\`google-genai >=2.31,<3\`` a `>=2.33,<3`, sin alterar el resto de la nota ni el encabezado `## Historial de Cambios`; verificar con `rg -n "google-genai >=2\\.31" PARAMS` (sin coincidencias).
- [x] 6.3 Ejecutar `python3 scripts/preflight/docs_stack_sync.py` y verificar 17/17 PASS con exit 0 (GREEN del Bloque A sobre el arbol real).

## 7. Verificacion y cierre

- [x] 7.1 Ejecutar `python3 -m pytest scripts/preflight -q` (directorio completo) y registrar el total en verde, sin regresiones respecto de la linea base.
- [x] 7.2 Ejecutar `openspec validate "c-151-corregir-pin-google-genai-y-ampliar-la-barrera" --strict --no-interactive` y registrar "Change is valid".
- [x] 7.3 Agregar en `CHANGES.md` la entrada del change con alcance (bloques A y B), gobernanza BAJO, RED/GREEN/TRIANGULATE y el resultado de la barrera; verificar con `rg -n "c-151|C-151" CHANGES.md`.
- [x] 7.4 Marcar las tareas `[x]` al completarlas y documentar el rollback (`git revert` de los commits del change; sin tag ni release).
