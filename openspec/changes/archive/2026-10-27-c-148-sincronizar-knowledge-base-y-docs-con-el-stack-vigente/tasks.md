> Ejecucion en orden estricto. Rutas relativas a la raiz del repositorio. `KB` = `knowledge-base/`; `PARAMS` = `docs/parameters_gemini.md`; `N8N_DOC` = `docs/n8n-workflow-guide.md`; `BARRIER` = `scripts/preflight/docs_stack_sync.py`; `BARRIER_TEST` = `scripts/preflight/test_docs_stack_sync.py`. Ninguna tarea se marca `[x]` en la fase propose.

## 1. Red de seguridad y linea base

- [x] 1.1 Registrar el estado de la barrera antes de tocarla con `python3 scripts/preflight/docs_stack_sync.py`; verificar que sale con codigo 0 y 12/12 PASS (la superficie actual no incluye `KB`). Registrar la salida.
- [x] 1.2 Ejecutar `python3 -m pytest scripts/preflight -q`; registrar el conteo (esperado 83 passed, de los cuales 35 son de `BARRIER_TEST`). Verificar que `python3 -m pytest scripts/preflight/test_docs_stack_sync.py --collect-only -q` reporta 35 pruebas.
- [x] 1.3 Registrar la fuente de verdad del stack antes de editar: leer `App/Backend/app/config/settings.py:78,85,97,104` y `App/Backend/requirements.txt:37`; anotar `gemini-3.6-flash`, 30 s, 60 s, 2 reintentos, `google-genai>=2.31.0,<3`. Verificar que `openspec/config.yaml:33,34` ya coincide.
- [x] 1.4 Registrar la linea base de la deriva con `grep -rn "2\.5 Flash\|gemini-2\.5-flash\|timeout 10\|timeout=10" "$KB" "$PARAMS" "$N8N_DOC"`; consignar el resultado completo (es la evidencia de que la barrera debe fallar tras 2.5).

## 2. Bloque D — extension de la barrera (TDD estricto)

- [x] 2.1 RED: escribir en `BARRIER_TEST` las pruebas de los tres chequeos de superficie nuevos de D4 (13 modelo vigente en la superficie ampliada, 14 timeout vigente en contexto de Gemini, 15 superficie cubierta). Cada prueba MUST fallar porque el chequeo no existe. Verificar con `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` que las pruebas nuevas fallan y que las 35 previas siguen en verde.
- [x] 2.2 GREEN: implementar en `BARRIER` los chequeos 13, 14 y 15 con las constantes `SUPERFICIE_KB` y `DOCS_REFERENCIA`, sin alterar los chequeos 1-12 ni el contrato (`Check`, `exit_code`, `format_summary`). Verificar `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` en verde.
- [x] 2.3 TRIANGULATE: agregar casos con (a) superficie sincronizada -> 0 hallazgos; (b) "Gemini 2.5 Flash" en un archivo de `KB` sin marcador historico -> FAIL que nombra archivo, linea y token; (c) el mismo token con marcador historico -> PASS; (d) "timeout 10 s" en contexto de Gemini sin marcador -> FAIL del chequeo 14; (e) timeout 30 en contexto de Gemini -> PASS; (f) archivo esperado ausente -> FAIL del chequeo 15, sin excepcion; (g) un token de modelo nuevo distinto de `Settings.gemini_model` -> FAIL (la regla no esta hardcodeada a 2.5). Verificar todos en verde.
- [x] 2.4 REFACTOR: extraer los parsers de la superficie ampliada (`_leer_superficie_kb`, `_lineas_con_marcador`) como funciones puras; ejecutar `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` despues de cada paso.
- [x] 2.5 PRUEBA DE LA BARRERA (antes de los bloques A/B/C): ejecutar `python3 scripts/preflight/docs_stack_sync.py` sobre el arbol con la documentacion **sin corregir** y verificar que termina con codigo distinto de cero y que los hallazgos nombran, como minimo, "Gemini 2.5 Flash" y "timeout 10 s" en `KB` y en `PARAMS`. Conservar la salida completa como evidencia. Si el preflight sale 0, la extension no detecta la deriva real y el apply se DETIENE.
- [x] 2.6 Verificar que el cableado en CI no necesita cambios: confirmar que `.github/workflows/ci.yml` ya ejecuta `python scripts/preflight/docs_stack_sync.py` en el job `backend-tests` y `python -m pytest scripts/preflight -q`. Si falta alguno, agregarlo y verificar que el YAML parsea (`python3 -c "import yaml;yaml.safe_load(open('.github/workflows/ci.yml'))"`).
- [x] 2.7 RED/GREEN/TRIANGULATE del **chequeo 16 (invariante del timeout del cliente)**: RED con una prueba que declare `timeout: 20_000` en `api.ts` y espere FAIL (20 s <= 60 s) y otra con `65_000` que espere PASS; GREEN implementando el chequeo 16 (compara el timeout de Axios en ms contra `Settings.gemini_total_timeout_seconds * 1000`, sin hardcodear 65); TRIANGULATE con un valor limite (`60_000` -> FAIL, no estrictamente mayor) y con la ausencia de la declaracion de timeout -> FAIL. Verificar `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` en verde.

## 3. Bloque A — sincronizacion de la base de conocimiento

- [x] 3.1 Regla del bloque: cada valor se lee de `settings.py`/`requirements.txt`, nunca de otro documento. Verificar que cada edicion de las tareas 3.2 a 3.7 tiene su fuente citada.
- [x] 3.2 `01_vision_y_objetivos.md`: en la linea 5 y en la linea 22 reemplazar "Gemini 2.5 Flash" por "Gemini 3.6 Flash". Verificar `grep -n "2\.5 Flash" "$KB/01_vision_y_objetivos.md"` sin coincidencias.
- [x] 3.3 `02_descripcion_general.md`: en la linea 13 reemplazar el modelo por "Gemini 3.6 Flash", `google-genai` >= 1.0 por `>=2.31,<3` y "timeout 10 s" por "timeout 30 s (total 60 s, 2 reintentos)"; en la linea 42 reemplazar el modelo. Verificar `grep -n "2\.5 Flash\|google-genai.*1\.0\|timeout 10" "$KB/02_descripcion_general.md"` sin coincidencias.
- [x] 3.4 `05_reglas_de_negocio.md`: en la linea 9 reemplazar "Gemini 2.5 Flash" por "Gemini 3.6 Flash" y "timeout 10 s" por "timeout 30 s por intento, 60 s total". Verificar sin coincidencias de "2.5 Flash" ni "timeout 10".
- [x] 3.5 `07_flujos_principales.md` (D2, restaurado): reescribir el parentesis de la linea 7 para declarar los valores reales de cada capa (Axios 65 s; Gemini 30 s por intento, 60 s total) y afirmar la desigualdad VERDADERA "timeout del cliente 65 s > peor caso total del backend 60 s"; remitir a `App/Frontend/src/services/api.ts`. Verificar que la linea no contiene "2.5" ni "timeout Gemini 10 s" y que la desigualdad que afirma la desmiente el valor vigente: NO (es verdadera).
- [x] 3.6 `08_arquitectura_propuesta.md`: en la linea 63 reemplazar `gemini-2.5-flash` por `gemini-3.6-flash` y el ultimo valor `10` por `30` en la tupla de parametros. Verificar que la fila declara `gemini-3.6-flash · 0.3 · 0.9 · 100 · 1 · 30`.
- [x] 3.7 `09_decisiones_y_supuestos.md` (D1, D3): en la linea 14 y 15, conservar DD-04 como decision historica y rotularla explicitamente como antecedente (por ejemplo "DD-04 (historico) — ... calibrados sobre Gemini 2.5 Flash"), actualizar el timeout vigente a 30 s por intento / 60 s total / 2 reintentos, y remitir al valor vigente. Verificar que la mencion de "2.5 Flash" en el archivo aparece en un pasaje con marcador historico y que no se declara "timeout 10 s" como actual.
- [x] 3.8 Verificacion del bloque: `grep -rn "2\.5 Flash" "$KB"` solo devuelve lineas con marcador historico; `grep -rn "timeout 10 s\|timeout=10" "$KB"` sin coincidencias fuera de pasajes rotulados.

## 4. Bloque B — material de referencia de `docs/`

- [x] 4.1 `PARAMS` (D3): retitular la linea 1 con el modelo vigente; en la linea 5 reemplazar `google-genai >= 1.0` por `>=2.31,<3`; en la linea 51 reemplazar `model="gemini-2.5-flash"` por `model="gemini-3.6-flash"`; en la linea 55 reemplazar `timeout=10` por `timeout=30`; en la linea 75 actualizar la fila `timeout` a 30 s (con 60 s total y 2 reintentos).
- [x] 4.2 `PARAMS` (D1): conservar el relato de calibracion de las lineas 100-105 y las menciones historicas de "Gemini 2.5 Flash" (lineas 73, 102, 103) bajo una rotulacion historica explicita; no presentarlas como el valor vigente. Verificar que cada "2.5 Flash" del archivo tiene marcador historico.
- [x] 4.3 `N8N_DOC`: en la linea 852 reemplazar "etapa: gemini (Gemini 2.5 Flash)" por "etapa: gemini (Gemini 3.6 Flash)". Verificar `grep -n "2\.5 Flash" "$N8N_DOC"` sin coincidencias. **[ANOTADO 2026-10-28: implementacion divergente deliberada y correcta. La linea 852 de `N8N_DOC` NO se reemplazo por "Gemini 3.6 Flash": se conservo "Gemini 2.5 Flash" y se agrego la rotulacion ", valor historico de la corrida". Esto es fiel a 4.2/D1 y a 4.4 (cada "2.5 Flash" del material cae en un pasaje rotulado) y al criterio de exito "no presentar 2.5 Flash como valor vigente"; la linea 852 es el eco de una corrida historica, no una declaracion de valor vigente. La verificacion literal de 4.3 (grep sin coincidencias) aplica al resto de la superficie, no a esta linea.]**
- [x] 4.4 Verificacion del bloque: `grep -rn "2\.5 Flash\|gemini-2\.5-flash" "$PARAMS" "$N8N_DOC"` solo devuelve lineas con marcador historico; `grep -n "google-genai.*1\.0" "$PARAMS"` sin coincidencias.

## 4b. Bloque E — noveno archivo: timeout del cliente Axios (`API_TS` = `App/Frontend/src/services/api.ts`)

- [x] 4b.1 `API_TS`: en la linea 44 reemplazar `timeout: 20_000,` por `timeout: 65_000,` (el cliente debe superar el peor caso total del backend, 60 s).
- [x] 4b.2 `API_TS`: reescribir el comentario de cabecera (lineas 7-8) y el comentario en linea (lineas 42-43) para declarar el invariante verdadero: el cliente (65 s) espera mas que el peor caso total de una clasificacion del backend (60 s, `Settings.gemini_total_timeout_seconds`). Verificar que el archivo no afirma un valor de Gemini de 10 s.
- [x] 4b.3 Verificacion del bloque: `grep -n "65_000" "$API_TS"` devuelve la declaracion; `grep -n "10 s\|20_000" "$API_TS"` sin coincidencias de timeout vigente; el chequeo 16 del preflight sale PASS.

## 5. Bloque C — procedencia historica rotulada

- [x] 5.1 Verificar que la calibracion sobre 2.5 Flash sobrevive y esta rotulada: `grep -rn "calibrad\|historico\|antecedente" "$KB/09_decisiones_y_supuestos.md" "$PARAMS"` devuelve los pasajes; y que cada mencion de "2.5 Flash" en la superficie cae en un pasaje rotulado.
- [x] 5.2 Verificar que ningun pasaje presenta "2.5 Flash" ni "timeout 10 s" como el valor vigente: `grep -rn "es el modelo vigente\|modelo actual.*2\.5\|timeout 10 s" "$KB" "$PARAMS"` sin coincidencias no rotuladas.
- [x] 5.3 Confirmar que la tesis y `openspec/config.yaml`/`CLAUDE.md` no se tocaron: `git diff --name-only` no incluye rutas bajo `docs/Tesis/`, `openspec/config.yaml` ni `CLAUDE.md`.

## 6. Verificacion de la barrera y de las pruebas

- [x] 6.1 Ejecutar `python3 scripts/preflight/docs_stack_sync.py` sobre el arbol corregido y verificar exit 0 y 0 hallazgos; registrar la salida junto a la de 2.5 para que el ledger muestre el fallo y su resolucion.
- [x] 6.2 Ejecutar `python3 -m pytest scripts/preflight -q` y verificar verde con las pruebas nuevas incluidas; registrar el conteo final (mayor que 83).
- [x] 6.3 Verificar que la suite de backend no se afecta (no se toco `App/Backend/`): `cd App/Backend && pytest -m "not integration" -q` sin fallos nuevos respecto del baseline (1552 passed, 1 xfailed).
- [x] 6.4 Verificar el frontend tras el cambio del Bloque E: `cd App/Frontend && npm run lint`, `npm run test` y `npm run build` (typecheck) en verde; confirman que `timeout: 65_000` compila y no rompe pruebas.

## 7. Hallazgos adyacentes (documentar, no corregir)

- [x] 7.1 Confirmar que el hallazgo de `App/Frontend/src/services/api.ts` quedo RESUELTO por el Bloque E (ya no es un hallazgo pendiente); registrar en `CHANGES.md` que paso de fuera de alcance a corregido.
- [x] 7.2 Registrar el hallazgo de los umbrales `0.90` en `docs/n8n-workflow-guide.md:598,610` como perteneciente al dominio de DOC-004, fuera del alcance de c-148.

## 8. Cierre documental y validacion

- [x] 8.1 Agregar en `CHANGES.md` la entrada C-148 con su alcance, governance MEDIO (A, B, C, E) / BAJO (D) y el estado de cada bloque. Verificar `grep -n "C-148" CHANGES.md`.
- [x] 8.2 Ejecutar `openspec validate c-148-sincronizar-knowledge-base-y-docs-con-el-stack-vigente --strict --no-interactive` y verificar que pasa. Registrar la salida.
- [x] 8.3 Ejecutar `openspec validate --specs --strict --no-interactive` y verificar el total esperado. Si difiere, detenerse y reportar el spec afectado.
- [x] 8.4 Verificar que no se marco ninguna tarea `[x]` durante la fase propose: `git show <commit-propose>:.../tasks.md | grep -c "^- \[x\]"` = 0.

## 9. Rollback documentado

- [ ] 9.1 `git revert` de los commits de c-148 restaura la documentacion previa y la barrera a 12 chequeos; verificar que `python3 scripts/preflight/docs_stack_sync.py` vuelve a 12/12 PASS y que no hay tag ni release que deshacer. (NO EJECUTADA: no hay commits de c-148; el change queda sin commitear por indicacion del orchestrator.) — ANOTACION (2026-10-27, c-150 W2): la justificacion "no hay commits del change" quedo OBSOLETA. c-148 se commiteo en 3392012 y se fusiono en PR #53 (merge 6516f5f); la verificacion de rollback es MOOT. El texto original se conserva como evidencia historica.
- [ ] 9.2 Verificar que los hechos historicos conservados y rotulados permanecen citables tras el revert (no se elimina la calibracion). (NO EJECUTADA: depende de 9.1.) — ANOTACION (2026-10-27, c-150 W2): depende de 9.1, que quedo MOOT por el merge de c-148 (commit 3392012, PR #53, merge 6516f5f). El texto original se conserva.

## 10. Residuales absorbidos en el mismo change (bloques F y G)

- [x] 10.1 Registrar la fuente de verdad de las versiones de componentes: `requirements.txt` (`fastapi==0.143.3`, `uvicorn[standard]==0.54.0`, `google-genai>=2.31.0,<3`) y `docker-compose.yml` (`n8nio/n8n:2.11.2`). Verificar que `openspec/config.yaml:17,30,33` ya coincide.
- [x] 10.2 RED del **chequeo 17**: agregar a `BARRIER_TEST` las pruebas de N8N retirado/desconocido/rotulado, FastAPI y Uvicorn de tabla, FastAPI/Uvicorn en prosa, `google-genai` retirado y la derivacion de valores en runtime. Ejecutar `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` y registrar 9 fallos (el chequeo no existe).
- [x] 10.3 RED del **residual 2**: agregar la prueba de que una linea con `Gemini 2.5 Flash` y la palabra "deprecado" produce un hallazgo del chequeo 13. Registrar que hoy pasa (exencion falsa).
- [x] 10.4 GREEN del residual 2: retirar `deprecad` de `MARCADORES_HISTORICOS` y documentar en el codigo por que no es un marcador valido.
- [x] 10.5 GREEN del chequeo 17: implementar `_check_versiones_componentes` con parsers anclados (`_versiones_n8n_en_linea`, `_versiones_fastapi_uvicorn_en_linea`, `_restricciones_genai_en_linea`) y valores derivados en runtime; extender `_GENAI_RE` para aceptar el nombre entre backticks. Verificar `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` en verde (60 pruebas).
- [x] 10.6 Evidencia de la barrera antes de corregir la KB: ejecutar `python3 scripts/preflight/docs_stack_sync.py` y registrar 16/17 PASS con el chequeo 17 en FAIL nombrando `02_descripcion_general.md:7,8,30`, `08_arquitectura_propuesta.md:76` y `09_decisiones_y_supuestos.md:6,21`.
- [x] 10.7 Bloque F: actualizar `knowledge-base/02_descripcion_general.md:7,8,30`, `knowledge-base/08_arquitectura_propuesta.md:76` y `knowledge-base/09_decisiones_y_supuestos.md:6,21` con los valores vigentes. Decision por linea: DD-01/DD-06 son decisiones vigentes (solo cambia la version con la que se implementan), no registros historicos; no se rotulan como historia.
- [x] 10.8 Verificar el bloque F: `grep -rn "1\.62\|0\.115\|0\.32" knowledge-base/` sin coincidencias y `python3 scripts/preflight/docs_stack_sync.py` en 17/17 PASS (exit 0).
- [x] 10.9 Verificar que retirar `deprecad` no rompio ningun pasaje legitimo: el preflight real sigue 17/17 PASS y los hechos historicos del modelo conservan sus marcadores (`historico`, `antecedente`, `calibrad`).
- [x] 10.10 Verificar la suite completa: `python3 -m pytest scripts/preflight/ -q` en verde (108 pruebas) y `openspec validate "c-148-..." --strict` en verde.
- [x] 10.11 Actualizar `proposal.md`, `design.md`, `tasks.md` y el delta `specs/project-documentation/spec.md` con los residuales (bloques F y G, decisiones D7 y D8, escenarios nuevos).
