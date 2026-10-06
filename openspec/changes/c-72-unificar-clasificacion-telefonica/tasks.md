# Tareas — c-72-unificar-clasificacion-telefonica

> Governance: ALTO. La reestructuracion del workflow, el traslado de costo y el cambio de arquitectura quedan bajo revision del autor (OQ de la seccion 0).
> Modo TDD estricto (RED-GREEN-TRIANGULATE-REFACTOR) en todo el codigo.
> Cada tarea de codigo que modifica un archivo existente arranca con una safety net (correr los tests actuales del area y registrar la linea base; si algo falla, reportarlo como fallo pre-existente y NO corregirlo).
> Los gates de la seccion 0 los resuelve el autor; las tareas dependientes NO se ejecutan hasta que su gate este resuelto.

## 0. Prerequisitos y gates de decision (autor)

- [x] 0.1 (Prerequisito) c-71 aterrizado: el determinista endurecido (piso de precision 0.90, `min_matches >= 2`, no-match/empate escalan) esta en el codigo. Verificacion: tests de c-71 en verde y `HYBRID_CACHE_VERSION == "hybrid-v2"`.
- [x] 0.2 (Gate OQ1) Reestructuracion del workflow: eliminar el `AI Agent` para telefonia o conservarlo para un sub-caso reducido. Criterio de la seccion 2.
- [x] 0.3 (Gate OQ2) Traslado de costo confirmado: sin reserva `n8n_gemini` por clasificar telefonia; `backend_gemini` en escalacion. Criterio de la seccion 4.
- [x] 0.4 (Gate OQ3) Bucle de refinamiento (2 intentos): preservarlo en algun lugar o retirarlo con camino terminal con revision humana. Criterio de la seccion 2.
- [x] 0.5 (Gate OQ4) Backfill de incidentes telefonicos historicos: requerido o no. Criterio de la seccion 6.
- [x] 0.6 (Gate OQ5) Redaccion final de las reglas de frontera del prompt compartido. Criterio de la seccion 3.
- [x] 0.7 Safety net global: correr `cd App/Backend; pytest -m "not integration"` y registrar la linea base; correr la medicion determinista de telefonia sobre el corpus y registrar la linea base (tasa de cortocircuito y exactitud estricta del subconjunto). Verificacion: baseline numerico documentado.

## 1. Backend: telefonia por la cascada (TDD)

- [x] 1.1 Safety net: correr `cd App/Backend; pytest tests/test_api_incidentes.py tests/ -k "clasificacion or precalculada" -m "not integration"` y registrar la linea base. Si algo falla, reportarlo como fallo pre-existente.
- [x] 1.2 (RED) Escribir el test de que un alta telefonica con `clasificacion` precalculada NO usa ese valor como sector, sino que resuelve por la cascada del backend. Debe fallar contra la implementacion actual. — `tests/` del servicio/API.
- [x] 1.3 (GREEN) Implementar en `IncidenteService._resolve_classification` la resolucion por cascada para telefonia, ignorando la `clasificacion` precalculada del canal. Correr el test: debe pasar.
- [x] 1.4 (TRIANGULATE) Cubrir: alta telefonica sin precalculada (cascada), con precalculada que difiere del corpus (gana la cascada), y correo/web sin cambios de comportamiento. Tests en verde.
- [x] 1.5 (RED) Escribir el test de contrato de que la descripcion que entra a la cascada es la pseudonimizada y que el transcript crudo no es la entrada. Debe fallar.
- [x] 1.6 (GREEN) Ajustar el camino para preservar el borde de pseudonimizacion. Correr los tests: deben pasar.
- [x] 1.7 (REFACTOR) Limpiar la rama precalculada y confirmar que todos los tests siguen verdes.

## 2. Workflow n8n (tests estructurales)

- [x] 2.1 Safety net: correr la suite estructural del workflow y registrar la linea base.
- [x] 2.2 (RED) Escribir el test estructural de que el body del POST telefonico NO incluye `clasificacion`. Debe fallar.
- [x] 2.3 (GREEN) Quitar `clasificacion` del body del POST en `n8n/workflow.json`. Correr el test: debe pasar.
- [x] 2.4 (GREEN, gate OQ1/OQ3) Retirar o reducir la rama `AI Agent` de telefonia segun OQ1; si se conserva, acotar sus invocaciones pagas y garantizar que no determina el sector. Correr los tests estructurales.
- [x] 2.5 (RED) Escribir el test de que ninguna rama terminal telefonica queda sin salida y de que existe un camino terminal con `requiere_revision_humana=true`. Debe fallar si la reestructuracion deja huecos.
- [x] 2.6 (GREEN/TRIANGULATE) Ajustar el cableado hasta que la alcanzabilidad y el camino terminal pasen. Cubrir con el `AI Agent` retirado y con el `AI Agent` reducido. Tests en verde.
- [x] 2.7 (REFACTOR) Limpiar nodos huerfanos y confirmar los tests estructurales verdes.

## 3. Prompt compartido y reglas de frontera

- [x] 3.1 (RED) Escribir el test de que `docs/prompt_gemini.txt` contiene las reglas de frontera (Software para accesos, Hardware para digitalizacion, Sistemas para infraestructura) y usa los cinco strings canonicos. Debe fallar.
- [x] 3.2 (GREEN, gate OQ5) Agregar las reglas de frontera con la redaccion del autor. Correr el test: debe pasar.
- [x] 3.3 (TRIANGULATE) Cubrir los tres casos de frontera con ejemplos del corpus (R002, R038 y un caso de infraestructura) y verificar que no hay prompt divergente en n8n. Tests en verde.

## 4. Cost guard: traslado de superficie

- [x] 4.1 (RED) Escribir el test de que la clasificacion telefonica no reserva `n8n_gemini` y de que la escalacion reserva `backend_gemini`. Debe fallar. (Gate OQ2.)
- [x] 4.2 (GREEN) Ajustar el workflow y/o el enforcement para que la clasificacion telefonica no reserve `n8n_gemini`. Correr los tests: deben pasar.
- [x] 4.3 (TRIANGULATE) Cubrir: cortocircuito telefonico (sin reserva), escalacion con guarda permitiendo (reserva `backend_gemini`) y guarda denegando (fallback con revision humana). Tests en verde.

## 5. Medicion del beneficio determinista-primero en telefonia

- [x] 5.1 (Medicion offline) Correr la medicion determinista sobre el corpus filtrando telefonia: fraccion que cortocircuita, exactitud estricta del subconjunto y cobertura. Registrar valores y delta contra la linea base. Verificacion: reporte numerico. No invoca Gemini ni toca `_a_float`.
- [x] 5.2 (Medicion hibrida, dependiente de c-71 OQ5) Re-correr `evaluation/run_evaluation.py` sobre telefonia cuando haya cuota de Gemini y registrar el delta de F1 hibrido vs determinista. Si no hay cuota, declarar PENDIENTE sin fabricar.
- [x] 5.3 Documentar el beneficio medido (atajo determinista, Gemini evitado) en la nota de evaluacion. Verificacion: reporte documentado.

## 6. Documentacion y backfill

- [x] 6.1 Actualizar `docs/anexo_h_prompt_gemini.md` al camino unico de clasificacion y a las reglas de frontera. Verificacion: doc actualizado.
- [x] 6.2 Actualizar la narrativa de tesis (`docs/Tesis/`) para reflejar un solo clasificador y el traslado de costo. Verificacion: doc actualizado.
- [x] 6.3 (Gate OQ4) Si el autor lo requiere, documentar el backfill de incidentes telefonicos historicos; si no, declararlo explicitamente fuera de alcance. Verificacion: decision documentada.

## 7. Verificacion final

- [x] 7.1 Correr `cd App/Backend; pytest -m "not integration"` y `ruff check .`; suite en verde y lint limpio.
- [x] 7.2 Correr la suite estructural del workflow y los tests de contrato; en verde.
- [x] 7.3 Verificar que los cinco strings canonicos no cambiaron y que `evaluation/corpus.py::_a_float` permanece intacto. Verificacion: tests estructurales y diff acotado.
- [x] 7.4 Correr `openspec validate c-72-unificar-clasificacion-telefonica --strict` y confirmar que pasa.
