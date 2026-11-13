# Tasks: Desarrollo de la linea de base clasica

Convenciones: `E/` = `evaluation/`; `T/` = `evaluation/tests/`. La implementacion es solo
lectura sobre los corpus versionados. NO se edita `App/`, `n8n/`, el clasificador de
produccion, los corpus, los numeros canonicos ni la tesis. NO se ejecuta la medicion final
(eso es c-210).

## 1. TDD del modulo

- [ ] 1.1 (RED) Escribir `T/test_linea_de_base.py` con una prueba que importe `E/linea_de_base.py` (inexistente) y verifique que el documento trae entrenamiento `200`, prueba `103`, metricas globales y por clase; correr `cd evaluation && python -m pytest tests/test_linea_de_base.py -q` y verificar que falla por modulo ausente. Verificacion: la prueba falla con error de importacion.
- [ ] 1.2 (GREEN) Crear `E/linea_de_base.py` con el pipeline TF-IDF + regresion logistica, la carga de los dos corpus y la construccion del documento; correr la prueba de 1.1 y verificar que pasa. Verificacion: la prueba pasa.
- [ ] 1.3 (TRIANGULATE) Agregar casos sinteticos con entradas y resultados esperados distintos (exactitud estricta, laxa, macro-F1 con clase de soporte cero y balanced accuracy) y verificar que pasan. Verificacion: al menos dos entradas distintas con resultados esperados distintos pasan.
- [ ] 1.4 Agregar la prueba de determinismo: dos corridas producen el JSON y el Markdown identicos byte a byte y los SHA-256 coinciden. Verificacion: la prueba de reproducibilidad pasa.
- [ ] 1.5 Agregar la prueba de ausencia de red, Gemini y API paga: el modulo no importa clientes de red ni `google.generativeai` y no toca `App/`. Verificacion: la prueba de offline pasa.
- [ ] 1.6 Correr `cd evaluation && python -m pytest tests/test_linea_de_base.py -q` y verificar que todas las pruebas del modulo pasan. Verificacion: exit 0 y conteo reportado.

## 2. Implementacion y contrato

- [ ] 2.1 Implementar el modelo primario con `class_weight="balanced"` y la variante de sensibilidad con `class_weight=None`, semilla fija `42`, y verificar que el documento reporta ambas variantes. Verificacion: ambas variantes figuran con sus metricas.
- [ ] 2.2 Implementar las metricas con las funciones de `evaluation/metrics.py` (`aciertos_estrictos`, `aciertos_laxos`, `matriz_confusion`, `f1_por_clase`, `f1_macro`, `sensibilidad_por_clase`, `soporte_por_clase`) y verificar que el soporte por clase suma `103`. Verificacion: las cinco clases con soporte `40/24/21/13/5`.
- [ ] 2.3 Implementar la lectura muestral y la lectura ponderada a la prevalencia natural de los `200` casos, y verificar que ambas figuran rotuladas. Verificacion: el documento trae las dos lecturas con su procedencia.
- [ ] 2.4 Implementar el CLI (`python3 -m evaluation.linea_de_base`) con `--salida`, que escriba JSON y Markdown con `sort_keys=True`, `indent=2`, `ensure_ascii=False`, LF y UTF-8 sin BOM, e imprima el SHA-256 de cada salida. Verificacion: la corrida termina y los archivos se escriben con el formato declarado.
- [ ] 2.5 Implementar la carga de solo lectura con `cargar_corpus_solo_lectura` y verificar que la corrida no modifica los corpus. Verificacion: `git status` sin cambios en `evaluation/data/campana/*.json`.
- [ ] 2.6 Implementar el documento con la declaracion de cifras aditivas y la exclusion de los `47` discordantes. Verificacion: el JSON declara que no reemplaza numeros canonicos y que el `n` de prueba es `103`.

## 3. Validacion y cierre

- [ ] 3.1 Correr `cd evaluation && python -m pytest tests/test_linea_de_base.py -q` y verificar exit 0. Verificacion: todas las pruebas pasan.
- [ ] 3.2 Correr `openspec validate c-209-linea-de-base-clasica-desarrollo --strict --no-interactive` y verificar que imprime `is valid` con exit 0. Verificacion: validacion estricta aprobada.
- [ ] 3.3 Revisar `git diff --stat` y confirmar que solo se agregaron `E/linea_de_base.py`, `T/test_linea_de_base.py` y los artefactos de la change. Verificacion: ningun archivo ajeno modificado.
