# Tareas — c-71-hardening-clasificador-determinista

> Governance: MEDIO. Modo TDD estricto (RED-GREEN-TRIANGULATE-REFACTOR) en todo el codigo.
> Cada tarea de codigo que modifica un archivo existente arranca con una safety net (correr los tests actuales del area y registrar la linea base; si algo falla, reportarlo como fallo pre-existente y NO corregirlo).
> Los gates de la seccion 0 los resuelve el autor; las tareas dependientes NO se ejecutan hasta que su gate este resuelto.

## 0. Prerequisitos y gates de decision (autor)

- [ ] 0.1 (Gate OQ1) Definir el piso de precision aceptable del cortocircuito y el objetivo de cobertura, e incorporarlos como criterio de la calibracion (§3). Verificacion: el valor queda escrito en el design/docs antes de calibrar.
- [ ] 0.2 (Gate OQ2) Definir la politica de no-match: escalar SIEMPRE a Gemini (recomendado) vs derivar directo a revision humana. Verificacion: la politica queda registrada y condiciona la implementacion de §1.10.
- [ ] 0.3 (Gate OQ3) Definir si el umbral queda como setting fijo o se vuelve derivado del corpus. Verificacion: la decision queda registrada y condiciona §3.6.
- [ ] 0.4 (OQ4, documental) Registrar que la unificacion de `telefono` a la cascada queda FUERA DE ALCANCE (pasa por el AI Agent de n8n con clasificacion precalculada). Verificacion: nota en el design/proposal.
- [ ] 0.5 (Gate OQ5) Definir cuando se captura la linea base de F1 Gemini/hibrido (cuota restaurada). Verificacion: la linea base se registra o se declara PENDIENTE en §4.3.
- [ ] 0.6 Safety net global: correr `cd App/Backend; pytest -m "not integration"` y registrar la linea base completa; correr la medicion offline de cobertura determinista y registrar la linea base (tasa de no-match y sobre-prediccion de `Seguridad Informatica` sobre 200 casos). Verificacion: baseline numerico documentado en la nota de tareas.

## 1. (a) No-match y tie-break (TDD)

- [ ] 1.1 Safety net: correr `cd App/Backend; pytest tests/test_deterministic_classifier.py tests/test_hybrid_classifier.py -m "not integration"` y registrar la linea base del area. Si algo falla, reportarlo como fallo pre-existente.
- [ ] 1.2 (RED) Escribir el test de que una descripcion sin ningun termino del vocabulario NO devuelve un sector canonico arbitrario: senala ausencia de prediccion y `confianza == 0.0`. Debe fallar contra la implementacion actual (hoy devuelve la primera clave). — `tests/test_deterministic_classifier.py`.
- [ ] 1.3 (GREEN) Implementar en `DeterministicClassifier.classify` el estado explicito de ausencia de prediccion cuando `winner_score == 0`. Correr el test: debe pasar.
- [ ] 1.4 (TRIANGULATE) Cubrir descripcion vacia, texto sin terminos, texto con solo terminos genericos y texto con un unico termino; verificar que ninguno inventa un sector y que la confianza es 0.0. Tests en verde.
- [ ] 1.5 (RED) Escribir el test de que dos o mas sectores con el MISMO puntaje maximo marcan ambiguedad y NO cortocircuitan (no dependen del orden de las claves). Debe fallar.
- [ ] 1.6 (GREEN) Implementar la marca de ambiguedad por empate en `classify`, sin elegir ganador por orden del mapa. Correr el test: debe pasar.
- [ ] 1.7 (TRIANGULATE) Cubrir empate 2-vias, empate 3-vias, empate donde la clave ganadora esta en distinta posicion del mapa, y un ganador estrictamente dominante que NO se marca ambiguo. Tests en verde.
- [ ] 1.8 (RED) Escribir el test de contrato de `ClasificacionResult`: `sin_prediccion` y `ambiguo` aditivos con default seguro y `sector_predicho` admite ausencia; los consumidores no rompen. Debe fallar.
- [ ] 1.9 (GREEN) Actualizar `schemas/clasificacion.py` con los campos aditivos y el tipo opcional, preservando los defaults. Correr los tests: deben pasar.
- [ ] 1.10 (GREEN) Ajustar el ruteo del no-match/ambiguedad en `hybrid.py` segun la politica de OQ2 (recomendado: escalar a Gemini). Tests en verde.
- [ ] 1.11 (TRIANGULATE) Cubrir el pipeline con ausencia de prediccion (escala), con ambiguedad (escala) y con senal dominante (cortocircuita si supera el umbral). Tests en verde.
- [ ] 1.12 (REFACTOR) Limpiar duplicacion y confirmar que todos los tests siguen verdes.

## 2. (b) Ampliacion del vocabulario (TDD)

- [ ] 2.1 Safety net: correr los tests de `test_deterministic_classifier.py` y la medicion offline de cobertura; registrar la linea base por sector (sobre-prediccion de `Seguridad Informatica`: 126 predicciones vs 31 reales; registrar tambien la tasa real de casos sin match).
- [ ] 2.2 (RED) Escribir el test de cobertura que exige una tasa de no-match ESTRICTAMENTE menor a la linea base y cobertura no nula para Hardware y Software. Debe fallar.
- [ ] 2.3 (GREEN) Ampliar `keywords.py` con sinonimos, variantes morfologicas y frases por sector, priorizando Hardware y Software, guiado por las misclasificaciones del corpus. Correr el test: debe pasar.
- [ ] 2.4 (TRIANGULATE) Agregar casos positivos y negativos por sector (falsos positivos) y el test estructural de que `set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)` sigue vigente y los cinco strings canonicos no cambian. Tests en verde.
- [ ] 2.5 (REFACTOR) Organizar el vocabulario y confirmar todos los tests verdes; re-medir la cobertura y registrar el delta.

## 3. (c) Confianza y recalibracion del umbral (TDD)

- [ ] 3.1 Safety net: correr los tests de determinista/hibrido y registrar la linea base.
- [ ] 3.2 (RED) Escribir los tests de la nueva confianza: un unico match NO alcanza confianza alta; un ganador dominante (conteo minimo + margen) SI; un empate da confianza nula; el valor permanece en [0.0, 1.0]. Deben fallar.
- [ ] 3.3 (GREEN) Implementar la confianza con conteo minimo `min_matches` y margen sobre el segundo en `deterministic.py`. Correr los tests: deben pasar.
- [ ] 3.4 (TRIANGULATE) Cubrir bordes: `winner_score == min_matches`, `winner_score == min_matches - 1`, margen 0, margen maximo, y multiples sectores con senal. Tests en verde.
- [ ] 3.5 (RED) Escribir el test de la calibracion offline: existe una curva precision/cobertura del subconjunto cortocircuitado y el umbral elegido respeta el piso de precision de OQ1. Debe fallar.
- [ ] 3.6 (GREEN) Implementar la calibracion offline (reutilizando el corpus y `evaluation/metrics.py`, sin invocar Gemini) y fijar el umbral segun OQ3 (setting fijo o derivado). Correr el test: debe pasar.
- [ ] 3.7 (TRIANGULATE) Cubrir umbrales por encima y por debajo del calibrado, verificando que el piso de precision se respeta y la cobertura se reporta. Tests en verde.
- [ ] 3.8 (RED) Escribir el test de que el cortocircuito del `HybridClassifier` solo ocurre con la confianza calibrada (no con el valor degenerado 1.0 por un unico match) y que el no-match/ambiguedad escala. Debe fallar.
- [ ] 3.9 (GREEN) Ajustar `hybrid.py`: cortocircuito gobernado por el umbral calibrado; escalamiento por ausencia/ambiguedad; fallback que NO fabrica sector cuando no hubo estimacion. Correr los tests: deben pasar.
- [ ] 3.10 (TRIANGULATE) Cubrir no-match con Gemini OK, no-match con Gemini caido (fallback sin sector fabricado), empate, y senal dominante que cortocircuita. Tests en verde.
- [ ] 3.11 (REFACTOR) Limpiar y confirmar todos los tests verdes.

## 4. (d) Re-medicion y documentacion

- [ ] 4.1 (RED) Escribir el test de que `HYBRID_CACHE_VERSION == "hybrid-v2"` y que un cambio de version invalida el cache de predicciones. Debe fallar.
- [ ] 4.2 (GREEN) Subir `HYBRID_CACHE_VERSION` a `hybrid-v2` en `constants.py`. Correr los tests: deben pasar (incluye `evaluation/tests/test_run_evaluation.py`).
- [ ] 4.3 (Medicion offline) Correr la medicion determinista sobre el corpus (sin Gemini): F1 estricto, F1 de pertenencia, cobertura y curva precision/cobertura; registrar los valores y el delta contra la linea base. Verificacion: reporte numerico documentado.
- [ ] 4.4 (Medicion hibrida, gate OQ5) Re-correr `evaluation/run_evaluation.py` sobre el corpus cuando la cuota de Gemini este disponible y registrar el delta de F1 hibrido vs determinista. Si no hay cuota, declarar la linea base PENDIENTE y no fabricar comparaciones. Verificacion: reporte o declaracion explicita de pendiente.
- [ ] 4.5 Documentar la calibracion (piso de precision, cobertura, umbral elegido) y el delta de F1 en `docs/` (parametros/Anexo H). Verificacion: doc actualizado.
- [ ] 4.6 Actualizar los tests estructurales y, si el contrato de API cambia, regenerar `docs/openapi.json` y verificar `pytest tests/test_openapi_sync.py`. Verificacion: sync en verde.

## 5. Verificacion final

- [ ] 5.1 Correr `cd App/Backend; pytest -m "not integration"` y `ruff check .`; suite en verde y lint limpio.
- [ ] 5.2 Correr `openspec validate c-71-hardening-clasificador-determinista --strict` y confirmar que pasa.
- [ ] 5.3 Verificar que los cinco strings canonicos no cambiaron y que `evaluation/corpus.py::_a_float` permanece intacto (tests estructurales). Verificacion: diff acotado y tests en verde.
