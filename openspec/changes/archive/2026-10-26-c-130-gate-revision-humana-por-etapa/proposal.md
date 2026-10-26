## Why

El dictamen CONEAU del 22-10-2026 sobre la release v1.1.0/v1.1.1 (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`) aprueba la tesis con observaciones y ubica en primer lugar (VEREDICTO punto 1; secciones 5, 6 y 7(a); recomendacion **A1**) que la salvaguarda *human in the loop* descrita en `02-marco-teorico.tex`, `05-arquitectura.tex` y `06-implementacion.tex` no es la que opero en el experimento: el texto afirma que todo caso con confianza inferior a 0,70 escala a revision y que ese umbral es el "unico disparador automatico", pero `07-resultados.tex` registra 124 de 200 casos bajo 0,70 que no escalaron; y `05-arquitectura.tex:80` afirma que el filtro deterministico decide solo con confianza "superior al 90 %", incompatible con esos mismos 124 casos. Mientras no se corrija, la justificacion etica y legal del sistema descansa sobre una salvaguarda que no existio en el 62 % del corpus.

La verificacion contra el codigo y la historia del repositorio confirma el diagnostico y agrega hallazgos que el dictamen no vio y que condicionan como puede redactarse la correccion:

1. **Dos magnitudes distintas.** Desde c-74 el cortocircuito de la etapa deterministica se gobierna por `score_correctitud >= deterministic_score_threshold` (0,5166, `App/Backend/app/config/settings.py:134`), no por la confianza; la `confianza` deterministica es un indice de fuerza de senal (ASG-009) que vale 0,0 en 90 de los 131 casos resueltos por reglas. El umbral 0,70 solo se evalua sobre la salida de Gemini (`hybrid.py:252`, `gemini_classifier.py:534`); la reserva deriva siempre (confianza 0,0) y el cortocircuito devuelve el resultado deterministico con `requiere_revision_humana=False` (`deterministic.py:294`). El docstring de `HybridClassifier.classify` (`hybrid.py:143-147`) afirma que la revision se verifica "de cualquier etapa": es falso desde c-74. Los docstrings de `deterministic.py:8-10` y `gemini_classifier.py:11-13` conservan el umbral 0,90 retirado.
2. **Un segundo disparador.** Desde c-82 (VIS-005) el backend tambien deriva a revision cuando no identifica al reportante (`incidente_service.py:405-407`), de modo que el 0,70 tampoco es "unico disparador" en el sistema entregado.
3. **Ajustes sobre el corpus.** El vocabulario del filtro (c-71, commit `1368fd8`) se amplio "guiado por las misclasificaciones del corpus", las reglas de frontera del prompt (c-72) se redactaron a partir de casos del corpus (R002, R038) y el punto de operacion (c-74) se derivo por validacion cruzada sobre el mismo corpus. Esto contradice las afirmaciones de "sin exposicion al corpus" (`05-arquitectura.tex:78`, `06-implementacion.tex:75`, `08-discusion.tex:18`, `12-anexos.tex:135`) e impide presentar la calibracion comparativa (precision 0,7405 del filtro frente a 0,6769 de Gemini sobre los mismos casos) como garantia independiente: es una estimacion dentro de la muestra.

Corregir la descripcion antes de la defensa condiciona la aprobacion plena (A1) y es prerrequisito de c-131, c-132, c-133 y c-136, que necesitan una definicion unica de las magnitudes y del alcance del gate.

## What Changes

- **Definicion de las magnitudes (marco teorico y arquitectura).** `02-marco-teorico.tex:34,46` y `05-arquitectura.tex:24,80,82` definen la confianza por etapa (indice de fuerza de senal en la etapa deterministica; confianza autodeclarada en Gemini; 0,0 por construccion en la reserva) y el puntaje de correctitud (`score_correctitud`) como unico criterio de cortocircuito, con su punto de operacion 0,5166, su procedencia (validacion cruzada de cinco pliegues con piso comparativo), su equivalencia en el corpus (los 131 casos con senal dominante) y el reemplazo del piso absoluto 0,90 del diseno inicial (que habria resuelto un solo caso). Se retira "umbral de confianza superior al 90 %".
- **Alcance del gate por etapa (implementacion).** `06-implementacion.tex:39,40,87,95` declaran que el indicador `requiere_revision_humana` se activa con Gemini por debajo de 0,70 o con la etapa de reserva, que queda en falso para los casos resueltos por el filtro y que el backend tiene un segundo disparador (reportante no identificado). Se retira "unico disparador automatico de revision humana".
- **Resultados.** `07-resultados.tex:136` (`subsec:reduccion-intervencion`) consigna que 124 de 200 casos (62 %) tuvieron confianza registrada inferior a 0,70 y no escalaron, que todos pertenecen a la etapa deterministica y por que; que los 69 casos de Gemini declararon siempre >= 0,85 y que la reserva no se activo.
- **Discusion.** `08-discusion.tex:16` (ultima oracion, introducida por c-121) corrige "sobre los 200 casos" por los 69 casos de Gemini y deja la valoracion del hallazgo a la calibracion por etapa (c-131). `08-discusion.tex:18`, `06-implementacion.tex:75` y `12-anexos.tex:135` reescriben la procedencia de los datos de ajuste (bloque con checkpoint de autores, decision D9).
- **Aspectos legales.** `11-aspectos-legales.tex:34` (ultima oracion) declara el alcance real de la salvaguarda: el 0,70 solo alcanza a Gemini y a la reserva; sobre el 65,5 % resuelto por reglas no hay derivacion por caso; las mitigaciones son el criterio de diseno del punto de operacion (estimado sobre el mismo corpus) y la reasignacion trazable por el sector responsable.
- **Anexo H.** Nueva fila del umbral de revision humana, con su alcance, en `tab:anexo_gemini_params` (`12-anexos.tex:96-107`).
- **Numeros canonicos.** Nueva Seccion 3.7 en `docs/Tesis/Correcciones/numeros-canonicos.md` con 124/200 (62,0 %), 0,5166, 97/131 (0,7405), 88/130 (0,6769) y 1/200 (piso absoluto 0,90 retirado), con procedencia y estado.
- **Documentacion para agentes.** `openspec/config.yaml` (`thresholds` y descripcion), `CLAUDE.md` (lineas 50 y 100) y las lineas afectadas de `knowledge-base/` (RN-CL-02, RN-CL-03, RN-CL-05, DD-07 y afines) pasan a describir el comportamiento vigente.
- **Codigo: solo comentarios y un test de caracterizacion.** Docstrings de `hybrid.py`, `deterministic.py` y `gemini_classifier.py` alineados con el comportamiento; un test fija que el cortocircuito deterministico no marca revision aunque la confianza sea inferior a 0,70. Cero cambios de comportamiento.
- **Specs con deriva.** Se corrige la redaccion de `classification-resilience` (telefonia: "confianza calibrada" -> puntaje de correctitud) y de `incident-visibility` VIS-005 (formula del indicador).
- **Trazabilidad y verificacion.** Grupo c-130 en `docs/Tesis/Correcciones/dictamen-correcciones.md`; regeneracion de `tesis_para_agente.md`; compilacion y conteo de paginas (el veredicto final del presupuesto es de c-141).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos sobre la definicion de las dos magnitudes de la etapa deterministica, el alcance del gate por etapa, la procedencia del punto de operacion, la consignacion de los 124 casos no escalados, el alcance real de la salvaguarda en el capitulo legal, la procedencia de los ajustes realizados sobre el corpus y el parametro del gate en el Anexo H; se modifica el requisito "Hallazgo del gate de clasificacion presentado como resultado propio" (69 casos de Gemini, no 200; valoracion delegada a la calibracion por etapa).
- `tesis-numeros-canonicos`: se agrega el registro canonico del gate por etapa y del punto de operacion del cortocircuito.
- `project-documentation`: se agrega la sincronia de la descripcion del gate y del cortocircuito en la configuracion para agentes, la base de conocimiento y los comentarios del codigo.
- `classification-resilience`: se corrige la redaccion de "Clasificacion telefonica determinista-primero" para que el cortocircuito telefonico se describa por el puntaje de correctitud, como el resto de la spec.
- `incident-visibility`: se corrige en VIS-005 la formula del indicador combinado para que la condicion del clasificador sea su indicador por etapa y no `confianza < 0.70`.

## Impact

- **Edita (tesis):** `docs/Tesis/v10 (IA)/paper/sections/{02-marco-teorico,05-arquitectura,06-implementacion,07-resultados,08-discusion,11-aspectos-legales,12-anexos}.tex`; regenera `docs/Tesis/v10 (IA)/tesis_para_agente.md`.
- **Edita (soporte):** `docs/Tesis/Correcciones/numeros-canonicos.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md`, `openspec/config.yaml`, `CLAUDE.md`, `knowledge-base/{01,02,03,04,05,06,07,08,09}_*.md` (solo las lineas del gate y del cortocircuito).
- **Edita (codigo, sin cambio de comportamiento):** docstrings de `App/Backend/app/classifiers/{hybrid,deterministic,gemini_classifier}.py`; agrega un test de caracterizacion en `App/Backend/tests/test_hybrid_classifier.py`.
- **No toca:** la logica del clasificador y del flujo N8N, `Settings`, los numeros canonicos existentes (solo agrega filas), las cinco cadenas canonicas, figuras, `evaluation/` (solo lectura), `Bibliography_base.bib`, tags y `CHANGES.md`.
- **Gobernanza:** LOW (reconciliacion documental con el codigo) salvo dos bloques MEDIUM con checkpoint de autores: la procedencia de los ajustes sobre el corpus (D9) y el alcance de la salvaguarda en el capitulo legal (D7).
- **Presupuesto de paginas:** medido sobre los textos ANTES/DESPUES de `design.md`, el change agrega aprox. +250 palabras netas con la compensacion ya incluida (aprox. +0,7 pagina; rango +0,6 a +0,9 con interlineado doble), mas una compensacion condicional si el PDF supera 101 paginas; con 101 paginas de base puede llevar el PDF a 102. La verificacion final y la decision sobre el tope (recorte global o renegociacion, inevitable para la familia completa) corresponden a c-141.
- **Dependencias:** requiere la version de trabajo v10 (c-122, aplicado). Precede a c-131, c-132, c-133 y c-136, que consumen sus definiciones; se coordina con c-135 (`06-implementacion.tex:75`), c-137 (acentuacion fuera de los fragmentos reescritos), c-139 (cita de `02-marco-teorico.tex:46`), c-140 (fila `timeout` del Anexo H) y c-141 (integracion y release v1.2.0).

## Rollback

Revertir los archivos editados con `git checkout <commit-previo> -- <rutas>` (secciones `.tex`, `numeros-canonicos.md`, `dictamen-correcciones.md`, `openspec/config.yaml`, `CLAUDE.md`, `knowledge-base/`, los tres clasificadores y el test agregado), regenerar `tesis_para_agente.md` y recompilar el PDF. Como el change no altera comportamiento ni datos, el rollback no requiere migraciones ni re-ejecucion de la evaluacion. Si c-131, c-132, c-133 o c-136 ya consumieron las definiciones, deben revertirse en orden inverso o reapuntarse a la redaccion previa.

## Success Criteria

- [ ] Ningun capitulo afirma que el umbral 0,70 alcanza a todos los casos, que es el "unico disparador automatico" ni que el filtro decide con confianza "superior al 90 %".
- [ ] Las dos magnitudes de la etapa deterministica quedan definidas una sola vez y usadas con el mismo nombre en `02`, `05`, `06`, `07`, `08`, `11` y `12`.
- [ ] `07-resultados.tex` consigna 124/200 (62 %) casos no escalados y explica por que; todo numero nuevo figura en `numeros-canonicos.md` con procedencia.
- [ ] El capitulo legal declara el alcance real de la salvaguarda sin presentar la calibracion comparativa como garantia independiente.
- [ ] Ninguna seccion afirma separacion estricta entre datos de ajuste y de validacion (sujeto al checkpoint de autores de D9).
- [ ] `openspec/config.yaml`, `CLAUDE.md`, `knowledge-base/` y los docstrings ya no declaran el 0,90 de cortocircuito ni el 0,70 universal; la suite del backend sigue verde y el test de caracterizacion pasa.
- [ ] El PDF compila sin errores ni referencias indefinidas y se registra el conteo de paginas resultante para c-141.
