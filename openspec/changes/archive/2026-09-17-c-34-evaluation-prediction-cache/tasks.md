## 1. RED — Tests para el cache de predicciones (TDD: escribir los tests antes del codigo)

- [x] 1.1 Escribir `test_cache_hit_omite_clasificacion`: usar `FakeClassifier` con un spy (subclase que cuenta llamadas a `classify`); correr `main_con_corpus_real` dos veces sobre el mismo corpus fixture y `tmp_path`; verificar que en la segunda corrida el clasificador NO recibe ninguna llamada. El test debe fallar (RED) antes de implementar el cache.
- [x] 1.2 Escribir `test_cambio_en_corpus_invalida_cache`: correr `main_con_corpus_real` una vez para generar el cache; modificar el archivo de corpus (agregar un caso dummy o cambiar una descripcion); correr nuevamente; verificar que el clasificador fue invocado en la segunda corrida. El test debe fallar (RED) antes del codigo.
- [x] 1.3 Escribir `test_force_flag_bypasea_cache_valido`: correr `main_con_corpus_real` una vez; correr nuevamente con `force=True`; verificar que el clasificador fue invocado en la segunda corrida aunque el cache era valido. El test debe fallar (RED) antes del codigo.
- [x] 1.4 Escribir `test_predicciones_json_incluye_cache_meta`: correr `main_con_corpus_real` y leer `predicciones.json`; verificar que el JSON contiene los campos `cache_meta.corpus_hash`, `cache_meta.corpus_count`, `cache_meta.classifier_version` y `cache_meta.generated_at`. El test debe fallar (RED) antes del codigo.
- [x] 1.5 Escribir `test_predicciones_json_sin_cache_meta_se_considera_invalido`: crear un `predicciones.json` con formato antiguo (arreglo plano sin `cache_meta`); correr `main_con_corpus_real`; verificar que el clasificador fue invocado (cache invalido). El test debe fallar (RED) antes del codigo.
- [x] 1.6 Verificar que los cinco tests del paso 1.x fallan con el codigo actual antes de continuar: `cd evaluation; pytest tests/test_run_evaluation.py -k "cache" -v` — esperado: 5 FAILED.

## 2. GREEN — Implementacion minima del cache

- [x] 2.1 Agregar funcion auxiliar `_compute_corpus_hash(corpus_path: pathlib.Path) -> str` en `run_evaluation.py` que devuelve el SHA-256 hex del contenido binario del archivo. Verificar con un test unitario inline o con los tests existentes.
- [x] 2.2 Agregar funcion auxiliar `_get_classifier_version(classifier) -> str` que devuelve `classifier.CACHE_VERSION` si existe, o `type(classifier).__name__` como fallback. Verificar con los tests del paso 1.
- [x] 2.3 Modificar `guardar_predicciones()` para escribir el nuevo formato `{"cache_meta": {...}, "predictions": [...]}`. Actualizar `cargar_predicciones()` para leer desde `data["predictions"]` con fallback a arreglo plano (compatibilidad hacia atras). Verificar que los tests existentes del runner siguen pasando: `cd evaluation; pytest tests/test_run_evaluation.py -v`.
- [x] 2.4 Modificar `main_con_corpus_real()` para recibir `force: bool = False` y ejecutar la logica de cache: (a) si `force=False` y `predicciones_path` existe, leer el archivo y comparar `cache_meta`; si coincide, cargar y saltar `evaluar_corpus`; (b) en cualquier otro caso, ejecutar `evaluar_corpus` y guardar con metadata. Verificar que los cinco tests RED del paso 1 pasan (GREEN): `cd evaluation; pytest tests/test_run_evaluation.py -k "cache" -v` — esperado: 5 PASSED.
- [x] 2.5 Verificar que todos los tests existentes del runner siguen verdes: `cd evaluation; pytest tests/test_run_evaluation.py -v` — ninguno debe romper.

## 3. TRIANGULATE — Casos adicionales y cobertura de bordes

- [x] 3.1 Agregar `test_cache_hit_produce_mismo_reporte`: correr dos veces con cache valido y comparar el contenido de `report.md`; verificar que son identicos byte a byte. Confirmar que el test pasa (GREEN): `cd evaluation; pytest tests/test_run_evaluation.py::test_cache_hit_produce_mismo_reporte -v`.
- [x] 3.2 Agregar `test_cambio_en_classifier_version_invalida_cache`: correr con `FakeClassifier`; luego correr con otra instancia cuyo `CACHE_VERSION` difiere; verificar que el clasificador fue invocado en la segunda corrida. Confirmar GREEN.
- [x] 3.3 Agregar `test_no_cache_flag_es_equivalente_a_force`: verificar que `force=True` y `--no-cache` CLI producen el mismo comportamiento (clasificador invocado). Confirmar GREEN.
- [x] 3.4 Correr la suite completa de evaluacion y verificar que no hay regresiones: `cd evaluation; pytest -v` — todos PASSED.

## 4. REFACTOR — Limpieza

- [x] 4.1 Extraer la logica de verificacion del cache a una funcion privada `_is_cache_valid(predicciones_path, corpus_hash, corpus_count, classifier_version) -> bool` para mejorar legibilidad. Correr `cd evaluation; pytest -v` — todos PASSED.
- [x] 4.2 Actualizar el docstring de `main_con_corpus_real()` y `guardar_predicciones()` para reflejar el nuevo parametro `force` y el nuevo formato del archivo. Verificar que el modulo se importa sin errores: `cd evaluation; python -c "from evaluation.run_evaluation import main_con_corpus_real; print('ok')"`.

## 5. CLI — Punto de entrada con argparse

- [x] 5.1 Refactorizar `main()` para usar `argparse` con el argumento `--force` / `--no-cache` (ambos mapean a `force=True`). Verificar: `cd evaluation; python -m evaluation.run_evaluation --help` muestra la opcion `--force`.
- [x] 5.2 Verificar que `python -m evaluation.run_evaluation --force` lanza `FileNotFoundError` (corpus real ausente) y NO un error de argparse: `cd evaluation; python -m evaluation.run_evaluation --force 2>&1 | grep -i "corpus"` debe mostrar el mensaje de error esperado. (Verificado por el test unitario `test_runner_corpus_real_ausente_falla_claro`; la corrida CLI real se omitio a proposito porque el corpus real esta presente y `--force` dispararia clasificacion paga.)

## 6. A2 — Pin de imagen N8N

- [x] 6.1 En `docker-compose.yml`, reemplazar `image: n8nio/n8n:latest` por `image: n8nio/n8n:2.11.2` y actualizar el comentario de la linea para indicar la version fijada y el motivo del pin. Verificar: `grep "n8n:" docker-compose.yml` muestra `n8nio/n8n:2.11.2`.

## 7. A4 — Comentar variables Twilio en .env.example

- [x] 7.1 En `App/Backend/.env.example`, comentar las cuatro lineas `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` y `TWILIO_WEBHOOK_URL`. Agregar un comentario explicativo antes del bloque indicando que esas credenciales pertenecen a la configuracion del trigger de N8N (no al backend FastAPI). Verificar: `grep "TWILIO" App/Backend/.env.example` muestra todas las lineas con `#` al inicio.

## 8. Verificacion final

- [x] 8.1 Correr la suite completa de evaluacion y confirmar que todos los tests pasan: `cd evaluation; pytest -v` — 0 FAILED.
- [x] 8.2 Correr la suite del backend (subset SQLite, sin Docker) y confirmar que no hay regresiones: `cd App/Backend; pytest -m "not integration" -v` — 0 FAILED.
- [x] 8.3 Confirmar que el archivo `docker-compose.yml` no contiene `n8nio/n8n:latest`: `grep "n8n:latest" docker-compose.yml` debe retornar sin resultados.
- [x] 8.4 Confirmar que `.env.example` no expone las variables Twilio sin comentar: `grep -E "^TWILIO_" App/Backend/.env.example` debe retornar sin resultados.
