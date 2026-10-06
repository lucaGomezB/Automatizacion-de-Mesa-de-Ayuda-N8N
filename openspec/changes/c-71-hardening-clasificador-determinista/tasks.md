# Tareas — c-71-hardening-clasificador-determinista

> Governance: MEDIO. Modo TDD estricto (RED-GREEN-TRIANGULATE-REFACTOR) en todo el codigo.
> Cada tarea de codigo que modifica un archivo existente arranca con una safety net (correr los tests actuales del area y registrar la linea base; si algo falla, reportarlo como fallo pre-existente y NO corregirlo).
> Los gates de la seccion 0 los resuelve el autor; las tareas dependientes NO se ejecutan hasta que su gate este resuelto.

## 0. Prerequisitos y gates de decision (autor)

- [x] 0.1 (Gate OQ1 RESUELTO) Piso de precision del cortocircuito: **>= 0.90** (exactitud estricta sobre el subconjunto cortocircuitado), prefiriendo PRECISION sobre cobertura ante conflicto; evidencia minima `min_matches >= 2`. Criterio de la calibracion (§3).
- [x] 0.2 (Gate OQ2 RESUELTO) No-match/empate: **escalar SIEMPRE a Gemini**; si Gemini falla, fallback SIN fabricar sector (`sin_prediccion`).
- [x] 0.3 (Gate OQ3 RESUELTO) Umbral: **setting fijo** (`deterministic_confidence_threshold`) re-derivado de la curva offline en apply y documentado; NO derivado en runtime.
- [x] 0.4 (OQ4 RESUELTO) La unificacion de `telefono` a la cascada queda **FUERA DE ALCANCE de c-71** y se mueve al change **c-72** (`unificar-clasificacion-telefonica`).
- [x] 0.5 (Gate OQ5 RESUELTO) Linea base F1 Gemini/hibrido: **capturar ahora** (cuota restaurada al corregir la clave de Gemini); la tarea 4.4 corre `evaluation/run_evaluation.py`; si la cuota falla, declarar PENDIENTE sin fabricar.
- [x] 0.6 Safety net global: correr `cd App/Backend; pytest -m "not integration"` y registrar la linea base completa; correr la medicion offline de cobertura determinista y registrar la linea base (tasa de no-match y sobre-prediccion de `Seguridad Informatica` sobre 200 casos). Verificacion: baseline numerico documentado en la nota de tareas.

## 1. (a) No-match y tie-break (TDD)

- [x] 1.1 Safety net: correr `cd App/Backend; pytest tests/test_deterministic_classifier.py tests/test_hybrid_classifier.py -m "not integration"` y registrar la linea base del area. Si algo falla, reportarlo como fallo pre-existente.
- [x] 1.2 (RED) Escribir el test de que una descripcion sin ningun termino del vocabulario NO devuelve un sector canonico arbitrario: senala ausencia de prediccion y `confianza == 0.0`. Debe fallar contra la implementacion actual (hoy devuelve la primera clave). — `tests/test_deterministic_classifier.py`.
- [x] 1.3 (GREEN) Implementar en `DeterministicClassifier.classify` el estado explicito de ausencia de prediccion cuando `winner_score == 0`. Correr el test: debe pasar.
- [x] 1.4 (TRIANGULATE) Cubrir descripcion vacia, texto sin terminos, texto con solo terminos genericos y texto con un unico termino; verificar que ninguno inventa un sector y que la confianza es 0.0. Tests en verde.
- [x] 1.5 (RED) Escribir el test de que dos o mas sectores con el MISMO puntaje maximo marcan ambiguedad y NO cortocircuitan (no dependen del orden de las claves). Debe fallar.
- [x] 1.6 (GREEN) Implementar la marca de ambiguedad por empate en `classify`, sin elegir ganador por orden del mapa. Correr el test: debe pasar.
- [x] 1.7 (TRIANGULATE) Cubrir empate 2-vias, empate 3-vias, empate donde la clave ganadora esta en distinta posicion del mapa, y un ganador estrictamente dominante que NO se marca ambiguo. Tests en verde.
- [x] 1.8 (RED) Escribir el test de contrato de `ClasificacionResult`: `sin_prediccion` y `ambiguo` aditivos con default seguro y `sector_predicho` admite ausencia; los consumidores no rompen. Debe fallar.
- [x] 1.9 (GREEN) Actualizar `schemas/clasificacion.py` con los campos aditivos y el tipo opcional, preservando los defaults. Correr los tests: deben pasar.
- [x] 1.10 (GREEN) Ajustar el ruteo del no-match/ambiguedad en `hybrid.py` segun la politica de OQ2 (recomendado: escalar a Gemini). Tests en verde.
- [x] 1.11 (TRIANGULATE) Cubrir el pipeline con ausencia de prediccion (escala), con ambiguedad (escala) y con senal dominante (cortocircuita si supera el umbral). Tests en verde.
- [x] 1.12 (REFACTOR) Limpiar duplicacion y confirmar que todos los tests siguen verdes.

## 2. (b) Ampliacion del vocabulario (TDD)

- [x] 2.1 Safety net: correr los tests de `test_deterministic_classifier.py` y la medicion offline de cobertura; registrar la linea base por sector (sobre-prediccion de `Seguridad Informatica`: 126 predicciones vs 31 reales; registrar tambien la tasa real de casos sin match).
- [x] 2.2 (RED) Escribir el test de cobertura que exige una tasa de no-match ESTRICTAMENTE menor a la linea base y cobertura no nula para Hardware y Software. Debe fallar.
- [x] 2.3 (GREEN) Ampliar `keywords.py` con sinonimos, variantes morfologicas y frases por sector, priorizando Hardware y Software, guiado por las misclasificaciones del corpus. Correr el test: debe pasar.
- [x] 2.4 (TRIANGULATE) Agregar casos positivos y negativos por sector (falsos positivos) y el test estructural de que `set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)` sigue vigente y los cinco strings canonicos no cambian. Tests en verde.
- [x] 2.5 (REFACTOR) Organizar el vocabulario y confirmar todos los tests verdes; re-medir la cobertura y registrar el delta.

## 3. (c) Confianza y recalibracion del umbral (TDD)

- [x] 3.1 Safety net: correr los tests de determinista/hibrido y registrar la linea base.
- [x] 3.2 (RED) Escribir los tests de la nueva confianza: un unico match NO alcanza confianza alta; un ganador dominante (conteo minimo + margen) SI; un empate da confianza nula; el valor permanece en [0.0, 1.0]. Deben fallar.
- [x] 3.3 (GREEN) Implementar la confianza con conteo minimo `min_matches` y margen sobre el segundo en `deterministic.py`. Correr los tests: deben pasar.
- [x] 3.4 (TRIANGULATE) Cubrir bordes: `winner_score == min_matches`, `winner_score == min_matches - 1`, margen 0, margen maximo, y multiples sectores con senal. Tests en verde.
- [x] 3.5 (RED) Escribir el test de la calibracion offline: existe una curva precision/cobertura del subconjunto cortocircuitado y el umbral elegido respeta el piso de precision de OQ1. Debe fallar.
- [x] 3.6 (GREEN) Implementar la calibracion offline (reutilizando el corpus y `evaluation/metrics.py`, sin invocar Gemini) y fijar el umbral segun OQ3 (setting fijo o derivado). Correr el test: debe pasar.
- [x] 3.7 (TRIANGULATE) Cubrir umbrales por encima y por debajo del calibrado, verificando que el piso de precision se respeta y la cobertura se reporta. Tests en verde.
- [x] 3.8 (RED) Escribir el test de que el cortocircuito del `HybridClassifier` solo ocurre con la confianza calibrada (no con el valor degenerado 1.0 por un unico match) y que el no-match/ambiguedad escala. Debe fallar.
- [x] 3.9 (GREEN) Ajustar `hybrid.py`: cortocircuito gobernado por el umbral calibrado; escalamiento por ausencia/ambiguedad; fallback que NO fabrica sector cuando no hubo estimacion. Correr los tests: deben pasar.
- [x] 3.10 (TRIANGULATE) Cubrir no-match con Gemini OK, no-match con Gemini caido (fallback sin sector fabricado), empate, y senal dominante que cortocircuita. Tests en verde.
- [x] 3.11 (REFACTOR) Limpiar y confirmar todos los tests verdes.

## 4. (d) Re-medicion y documentacion

- [x] 4.1 (RED) Escribir el test de que `HYBRID_CACHE_VERSION == "hybrid-v2"` y que un cambio de version invalida el cache de predicciones. Debe fallar.
- [x] 4.2 (GREEN) Subir `HYBRID_CACHE_VERSION` a `hybrid-v2` en `constants.py`. Correr los tests: deben pasar (incluye `evaluation/tests/test_run_evaluation.py`).
- [x] 4.3 (Medicion offline) Correr la medicion determinista sobre el corpus (sin Gemini): F1 estricto, F1 de pertenencia, cobertura y curva precision/cobertura; registrar los valores y el delta contra la linea base. Verificacion: reporte numerico documentado.
- [x] 4.4 (Medicion hibrida, gate OQ5) Re-correr `evaluation/run_evaluation.py` sobre el corpus cuando la cuota de Gemini este disponible y registrar el delta de F1 hibrido vs determinista. Si no hay cuota, declarar la linea base PENDIENTE y no fabricar comparaciones. Verificacion: reporte o declaracion explicita de pendiente.
- [x] 4.5 Documentar la calibracion (piso de precision, cobertura, umbral elegido) y el delta de F1 en `docs/` (parametros/Anexo H). Verificacion: doc actualizado.
- [x] 4.6 Actualizar los tests estructurales y, si el contrato de API cambia, regenerar `docs/openapi.json` y verificar `pytest tests/test_openapi_sync.py`. Verificacion: sync en verde.

## 5. Verificacion final

- [x] 5.1 Correr `cd App/Backend; pytest -m "not integration"` y `ruff check .`; suite en verde y lint limpio.
- [x] 5.2 Correr `openspec validate c-71-hardening-clasificador-determinista --strict` y confirmar que pasa.
- [x] 5.3 Verificar que los cinco strings canonicos no cambiaron y que `evaluation/corpus.py::_a_float` permanece intacto (tests estructurales). Verificacion: diff acotado y tests en verde.

## Notas de desviacion

- **Calibracion (OQ1):** con el piso de precision estricta >= 0.90, ningun umbral da cobertura util: el umbral calibrado es **1.0** y cortocircuita **1/200** casos (el hibrido escala ~99.5% a Gemini). Honra 'precision sobre cobertura', pero **desactiva el atajo barato**. El trade-off queda documentado en `docs/deterministic_calibration.md` (opciones: aceptar / bajar el piso / invertir en vocabulario). **Pendiente de decision del autor.**
- **Corpus con tiempos nulos:** 56 casos tienen `tiempo_automatizado_s: null` y `cargar_corpus` los rechaza (con `_a_float` intocable); la medicion hibrida (4.4) se corrio sobre una copia normalizada en `/tmp`. Deuda aparte: arreglar el corpus/loader.
- **Vocabulario:** no-match 119->57; cobertura global 0.715; sesgo de default eliminado; determinista estricto 0.485->0.670, macro-F1 0.4196->0.4801. `HYBRID_CACHE_VERSION` -> `hybrid-v2`.
