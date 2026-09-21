## 1. RED — Red de seguridad estructural y funcional

- [x] 1.1 Crear `App/Backend/tests/test_docs_evaluation_sync.py` con un helper de lectura por path relativo a la raiz (`Path(__file__).resolve().parents[3]`, patron de `test_docs_restructure_sync.py`), un helper que aisla una seccion por su encabezado ignorando fences, y un helper de assert por token; ejecutar `cd App/Backend; pytest tests/test_docs_evaluation_sync.py -q` y confirmar que el modulo se recolecta sin errores de importacion
- [x] 1.2 Agregar el test que asserta que la seccion 8 de `docs/operational-guide.md` contiene `PYTHONPATH=App/Backend python -m evaluation.run_evaluation` y NO contiene `python run_evaluation.py`; ejecutar el archivo y confirmar RED porque §8.1 usa hoy la invocacion rota
- [x] 1.3 Agregar el test que asserta que la seccion 8 de la guia NO contiene `generate_corpus.py` y apunta a `docs/como_cargar_datos_corpus.md`; ejecutar y confirmar RED porque §8.3 invoca hoy el generador inexistente
- [x] 1.4 Agregar un test parametrizado que asserta que `docs/operational-guide.md` y `evaluation/README.md` contienen los tokens del gate `confirm-paid` y `EVALUATION_CONFIRM_PAID`; ejecutar y confirmar RED en ambos documentos
- [x] 1.5 Agregar el test que asserta que `App/Backend/scripts/export_openapi.py` NO contiene `Gestion_Incidentes` y que su bloque `_DUMMIES` declara `JWT_SECRET_KEY`; ejecutar y confirmar RED en ambas aserciones
- [x] 1.6 Agregar el test funcional que ejecuta `App/Backend/scripts/export_openapi.py` en un subproceso con `JWT_SECRET_KEY` eliminado del entorno, `cwd` en un directorio temporal sin `.env` descubrible y `--output` a un archivo temporal; asserta exit code 0 y JSON OpenAPI 3.1 valido con `paths` no vacio; ejecutar y confirmar RED por el error de validacion de `Settings` (`jwt_secret_key` requerido)

## 2. GREEN — Guia operativa, seccion 8

- [x] 2.1 Corregir `docs/operational-guide.md` §8.1 para usar `PYTHONPATH=App/Backend python -m evaluation.run_evaluation` desde la raiz del repositorio, eliminando el `cd evaluation; python run_evaluation.py`; ejecutar `cd App/Backend; pytest tests/test_docs_evaluation_sync.py -q` y confirmar GREEN del test 1.2
- [x] 2.2 Eliminar §8.3 (regeneracion del corpus sintetico) y reemplazarla por un puntero al procedimiento real en `docs/como_cargar_datos_corpus.md`; ejecutar el archivo y confirmar GREEN del test 1.3
- [x] 2.3 Documentar el gate de corrida paga en §8: `--confirm-paid` y `EVALUATION_CONFIRM_PAID=1`, aborto con codigo de salida 2 sin confirmacion y estimacion de costo al confirmar; ejecutar el archivo y confirmar GREEN de la parte de la guia en el test 1.4

## 3. GREEN — `evaluation/README.md`

- [x] 3.1 Documentar el gate de corrida paga junto al comando unico de corrida y a la configuracion de `GEMINI_API_KEY`, nombrando `--confirm-paid` y `EVALUATION_CONFIRM_PAID=1`, el aborto sin confirmacion y la estimacion de costo; ejecutar `cd App/Backend; pytest tests/test_docs_evaluation_sync.py -q` y confirmar GREEN de la parte del README en el test 1.4

## 4. GREEN — `App/Backend/scripts/export_openapi.py`

- [x] 4.1 Agregar `JWT_SECRET_KEY` al diccionario `_DUMMIES` con un valor dummy estable; ejecutar `cd App/Backend; pytest tests/test_docs_evaluation_sync.py::test_export_openapi_runs_without_jwt_env -q` y confirmar GREEN (exit code 0 y OpenAPI 3.1 valido)
- [x] 4.2 Corregir el docstring: `cd Gestion_Incidentes` → `cd App/Backend`, `pip install -r Gestion_Incidentes/requirements.txt` → `App/Backend/requirements.txt`, el comentario `(Gestion_Incidentes/)` → `(App/Backend/)` y el ejemplo `--output ../docs/openapi.json` → `--output ../../docs/openapi.json`, consistente con `_DEFAULT_OUTPUT`; ejecutar el archivo y confirmar GREEN del test 1.5

## 5. TRIANGULATE — Cobertura de los escenarios de la spec

- [x] 5.1 Agregar un caso que asserta que la seccion 8 conserva la mencion a `evaluation/report.md` (comportamiento del runner que no debe perderse al reescribir la seccion); ejecutar y confirmar que pasa
- [x] 5.2 Agregar un caso que asserta que `evaluation/README.md` conserva el comando unico `PYTHONPATH=App/Backend python -m evaluation.run_evaluation` y la configuracion de `GEMINI_API_KEY` como no-regresion; ejecutar y confirmar que pasa
- [x] 5.3 Agregar un caso que asserta que `docs/operational-guide.md` conserva los tokens de c-43 (`App/Backend/`, `UP_SKIP_COST_PREFLIGHT`, `docker compose up -d`) para evitar regresion cruzada; ejecutar y confirmar que pasa
- [x] 5.4 Agregar un caso funcional de triangulacion que ejecuta el script con `JWT_SECRET_KEY` presente en el entorno y un output distinto, y confirma que el resultado sigue siendo OpenAPI 3.1 valido (el dummy no pisa el valor del entorno); ejecutar y confirmar que pasa

## 6. REFACTOR y verificacion final

- [x] 6.1 Refactorizar `App/Backend/tests/test_docs_evaluation_sync.py` extrayendo constantes de path y tokens y helpers reutilizables, dejando los asserts legibles; ejecutar `cd App/Backend; pytest tests/test_docs_evaluation_sync.py -q` y confirmar que sigue GREEN
- [x] 6.2 Ejecutar `cd App/Backend; pytest tests/test_docs_bootstrap_sync.py tests/test_docs_restructure_sync.py tests/test_docs_evaluation_sync.py -q` y confirmar que los tres modulos pasan (sin regresion de c-42/c-43)
- [x] 6.3 Ejecutar la suite offline completa `cd App/Backend; pytest -m "not integration" -q` y confirmar que no hay regresiones
- [x] 6.4 Ejecutar `openspec validate --strict --changes c-44-docs-evaluation-sync` y confirmar que pasa
- [x] 6.5 Confirmar que `docs/anexo_f_corpus.md` y `docs/Tesis/**` no fueron modificados: ejecutar `git status --porcelain docs/anexo_f_corpus.md docs/Tesis` y verificar que no hay entradas
- [x] 6.6 Ejecutar `openspec status --change c-44-docs-evaluation-sync` y confirmar que las tareas quedan registradas

## 7. Cierre de drift relacionado — invocacion del runner en como_cargar_datos_corpus.md

- [x] 7.1 RED: agregar a `App/Backend/tests/test_docs_evaluation_sync.py` el test `test_corpus_procedure_runner_invocation_has_no_cd` que asserta que `docs/como_cargar_datos_corpus.md` contiene `PYTHONPATH=App/Backend python -m evaluation.run_evaluation` y que su bloque de invocacion del runner NO contiene `cd evaluation`; ejecutar `cd App/Backend; pytest tests/test_docs_evaluation_sync.py -q` y confirmar RED en la asercion de ausencia
- [x] 7.2 GREEN: eliminar la linea `cd evaluation` del bloque de invocacion del runner en `docs/como_cargar_datos_corpus.md` §8 (el comentario «Desde la raiz del repositorio» y el comando quedan correctos; el `cd evaluation` legitimo de `evaluation/README.md` y de la guia §8.3 no se toca); re-ejecutar el archivo y confirmar GREEN
- [x] 7.3 Verificacion: ejecutar `cd App/Backend; pytest tests/test_docs_bootstrap_sync.py tests/test_docs_restructure_sync.py tests/test_docs_evaluation_sync.py -q` y la suite offline `cd App/Backend; pytest -m "not integration" -q`, y `openspec validate --strict --changes c-44-docs-evaluation-sync`, confirmando que no hay regresiones
