## 1. Preparacion y seguridad neta

- [ ] 1.1 Confirmar el estado de partida: correr `cd evaluation && pytest tests/test_sensibilidad_ajustes.py -q` y registrar el conteo de pruebas en verde como linea base (si hay fallos preexistentes, reportarlos como tales y NO corregirlos en este change). Verificacion: se anota el numero de pruebas que pasan antes de tocar el codigo.
- [ ] 1.2 Reconfirmar los dos defectos sobre el codigo vigente: localizar `preparar_entorno_offline`/`ENTORNO_OFFLINE` y el import anticipado de `gemini_classifier` en `App/Backend/app/classifiers/__init__.py`. Verificacion: se citan las lineas exactas y se confirma que siguen siendo la causa raiz descrita en `design.md`.

## 2. Defecto A — credencial real en el camino pago (TDD)

- [ ] 2.1 RED: escribir una prueba en `evaluation/tests/test_sensibilidad_ajustes.py` que fije que el camino pago resuelve `GEMINI_API_KEY` desde `App/Backend/.env` y NO con el valor inerte de `ENTORNO_OFFLINE`, incluso si `preparar_entorno_offline` se ejecuto antes en el mismo proceso. Verificacion: la prueba falla contra el codigo actual (`pytest -k credencial` en rojo).
- [ ] 2.2 GREEN: implementar en `_cli_prompt` (o en un helper dedicado) la resolucion de la credencial real desde `App/Backend/.env` con `python-dotenv`, la inyeccion en `os.environ` antes de construir el clasificador y la limpieza de la cache de `get_settings()`; fallar con un error claro si no hay credencial en el entorno ni en el archivo. Verificacion: la prueba del 2.1 pasa.
- [ ] 2.3 TRIANGULATE: agregar un segundo caso con insumos distintos (por ejemplo, la credencial ya presente en `os.environ` no se pisa; y la ausencia total de credencial falla antes de construir el clasificador). Verificacion: ambas variantes pasan y la prueba de ausencia no deja archivo de salida.
- [ ] 2.4 REFACTOR: extraer la resolucion de la credencial a una funcion nombrada y legible, sin cambiar comportamiento. Verificacion: `cd evaluation && pytest tests/test_sensibilidad_ajustes.py -q` sigue en verde.

## 3. Defecto B — el brazo carga su propio prompt (TDD)

- [ ] 3.1 RED: escribir una prueba que fije que importar `app.classifiers` (o `app.classifiers.deterministic`) NO carga `gemini_classifier` de forma anticipada, y que tras fijar `GEMINI_PROMPT_PATH` para el brazo `sin-reglas` el prompt efectivamente cargado tiene el SHA-256 esperado (distinto del vigente). Verificacion: la prueba falla contra el codigo actual.
- [ ] 3.2 GREEN: convertir `App/Backend/app/classifiers/__init__.py` a import perezoso mediante `__getattr__` de modulo (PEP 562), preservando `BaseClassifier`, `DeterministicClassifier`, `GeminiClassifier`, `HybridClassifier` y `__all__`. Verificacion: la prueba del 3.1 pasa.
- [ ] 3.3 TRIANGULATE: agregar pruebas de que (a) `from app.classifiers import GeminiClassifier` sigue resolviendo el nombre, (b) el brazo `vigente` sigue cargando el prompt vigente y (c) `correr_brazo_prompt` acepta el brazo `sin-reglas` sin lanzar `PromptInesperadoError`. Verificacion: las tres pruebas pasan.
- [ ] 3.4 REFACTOR: ordenar el `__getattr__` y comentar el porque del import perezoso; correr `cd App/Backend && ruff check .` y `cd evaluation && pytest tests/test_sensibilidad_ajustes.py -q`. Verificacion: sin hallazgos de lint y suite en verde.

## 4. No regresion de los caminos offline y cierre de la correccion

- [ ] 4.1 Escribir una prueba de no regresion que verifique que `preparar_entorno_offline` sigue completando los valores inertes con `setdefault`, no pisa una credencial real ya presente y los caminos offline siguen operando sin invocar al proveedor. Verificacion: la prueba pasa.
- [ ] 4.2 Correr la suite completa de evaluacion `cd evaluation && pytest -q` (incluye `test_sensibilidad_corpus.py` y el resto). Verificacion: 0 fallos.
- [ ] 4.3 Correr la suite del backend que cubre el prompt y los clasificadores (`cd App/Backend && pytest tests/test_prompt_resolution.py -q`; y `pytest -m "not integration"` si el tiempo lo permite). Verificacion: 0 fallos, sin cambios de comportamiento del clasificador.

## 5. Corrida autorizada, cierre del reporte y propagacion (grupo final)

- [ ] 5.1 Ejecutar el brazo vigente: `cd App/Backend; PYTHONPATH=../.. python -m evaluation.sensibilidad_ajustes prompt --brazo vigente --confirm-paid`. Verificacion: se escribe `evaluation/predicciones_sensibilidad_prompt_vigente.json` con `cache_meta.prompt_sha256` igual al esperado y `fallbacks` bajo (no 69/69 por `API_KEY_INVALID`).
- [ ] 5.2 Ejecutar el brazo sin reglas: `cd App/Backend; PYTHONPATH=../.. python -m evaluation.sensibilidad_ajustes prompt --brazo sin-reglas --confirm-paid`. Verificacion: se escribe `evaluation/predicciones_sensibilidad_prompt_sin_reglas.json` con `cache_meta.prompt_sha256` igual al del prompt previo a c-72 y `fallbacks` bajo.
- [ ] 5.3 Cerrar el reporte offline pasando ambos brazos (comando offline sin subcomando con `--brazo-vigente` y `--brazo-sin-reglas`) para que el nivel c se calcule y se escriba en `evaluation/report_sensibilidad_ajustes.md`. Verificacion: el reporte incluye la seccion del nivel c con los aciertos, las reservas y el McNemar de ambos brazos, en lugar de "no computado".
- [ ] 5.4 Propagar el nivel c a `docs/Tesis/Correcciones/numeros-canonicos.md` (fila del nivel c de la seccion de sensibilidad). Verificacion: la fila deja de declarar "no computado", cita la linea del reporte y mantiene los rotulos de procedencia y estado exigidos por el spec.
- [ ] 5.5 Propagar el nivel c a `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex`. Verificacion: la subseccion de sensibilidad del prompt reporta el valor calculado con su cita al reporte, sin contradecir los niveles a y b.
- [ ] 5.6 Propagar el nivel c a `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex`. Verificacion: la limitacion sobre las reglas del prompt deja de afirmar que el efecto "no se cuantifico" y declara el resultado calculado.
- [ ] 5.7 Registrar el cierre en la entrada G0.7a de `docs/Tesis/Correcciones/dictamen-correcciones.md`. Verificacion: la entrada pasa de "BLOQUEADA por defectos del arnes" a "ejecutada", con el valor del nivel c y la referencia al reporte, conservando el historial previo.
- [ ] 5.8 Verificar la coherencia final de la propagacion: los cuatro documentos citan el mismo valor y la misma linea del reporte. Verificacion: busqueda cruzada del valor del nivel c en los cuatro archivos sin discrepancias.
