# Tasks: Integrar el clasificador supervisado en la configuracion entregada

Al final de cada tarea, entre parentesis, el requisito del change que cumple, por nombre corto precedido de su capacidad. Nombres cortos: `SCI` (`supervised-classifier-integration`) «SCI-001», «SCI-002», «SCI-003»; `DCD` (`delivered-classifier-decision`) «DCD-001», «DCD-002»; `IPA` (`inference-provider-abstraction`) «Proveedor supervisado»; `TD` (`tesis-document`) «Veredicto honesto»; `NC` (`tesis-numeros-canonicos`) «Registro aditivo». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Este change SÍ escribe codigo ejecutable: aplica el ciclo TDD estricto (RED → GREEN → TRIANGULATE → REFACTOR) sobre las funciones puras del congelado y del contraste pareado, con la suite de `evaluation/` y la del backend como red de seguridad. El contraste real y el veredicto quedan **condicionados** a que `c-228`/`c-229`/`c-230` entreguen sus artefactos; si no, las tareas se bloquean y se registran.

Gobernanza **ALTA** (toca la linea del clasificador de produccion y la configuracion entregada). Checkpoints humanos obligatorios: **CHECKPOINT A** antes de consumir el resultado de `c-228` y congelar el modelo; **CHECKPOINT B** antes de cambiar el default entregado o registrar el adaptador como seleccionable; **CHECKPOINT C** antes de emitir el veredicto y de tocar la declaracion de configuracion entregada.

## 0. Preparacion y verificacion de estado

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D8) y los cinco specs delta; cargar los `SKILL.md` completos de `python-testing`, `python-design-patterns` y `pytest-coverage` antes de escribir codigo y registrar la resolucion.
- [ ] 0.2 Capturar la linea de base como evidencia de partida: `git status`, `git rev-parse HEAD`, `sha256sum evaluation/data/campana/predicciones_arbitrado.json data/corpus_evaluacion_pseudonimizado.json`, y los anclajes (`0,6893/206`, macro-F1 `0,7024`, techo `0,835`, manual `0,8278`, frontera `16/64`). Registrar modificaciones preexistentes ajenas a este change y no tocarlas.
- [ ] 0.3 **Red de seguridad:** correr `cd evaluation && pytest -q` y `cd App/Backend && pytest -m "not integration"` y registrar el resultado (debe pasar antes de editar; si algo falla, detenerse y reportarlo como fallo preexistente).
- [ ] 0.4 Releer `App/Backend/app/classifiers/provider.py`, `base.py`, `hybrid.py` y `Settings` (`inference_provider`/`inference_model`); confirmar que la integracion puede apoyarse en la abstraccion de `c-227` sin reescribirla.
- [ ] 0.5 **[CHECKPOINT A — BLOQUEA EL GRUPO 1]** Confirmar con los autores el criterio de seleccion del «mejor modelo» de `c-228` (OQ1) y presentar el esquema de congelado y versionado (binario o puntero + hash) antes de consumir o copiar artefactos. Registrar la respuesta.
- [ ] 0.6 **[CHECKPOINT C — prospectivo]** Confirmar con los autores, y registrar, la regla de decision pre-registrada (umbrales de IC, margen de macro-F1, correccion por comparaciones multiples, OQ2) ANTES de correr el contraste. La regla no se modifica despues.
- [ ] 0.7 Releer el indice de `numeros-canonicos.md` y fijar el primer numero de seccion libre (hoy la ultima planificada es `3.41`; esperado `3.42`). Registrar el numero elegido.
- [ ] 0.8 Verificar la disponibilidad de los insumos de `c-228`, `c-229` y `c-230`; si falta alguno, registrar el bloqueo de las tareas dependientes sin sustituirlo por datos de conveniencia.

## 1. Congelado del modelo seleccionado (TDD, SCI; depende de c-228 y del CHECKPOINT A)

- [ ] 1.1 **RED:** escribir `evaluation/tests/test_congelado_modelo_c232.py` con pruebas sinteticas del lector/validador del manifiesto de congelado (campos obligatorios, hashes presentes, comando de evaluacion) antes de existir el modulo; ejecutar y confirmar que fallan por ausencia de la implementacion. (SCI-001)
- [ ] 1.2 **GREEN:** implementar el lector/validador con la minima logica para pasar las pruebas (funcion pura sobre un manifiesto en memoria). (SCI-001)
- [ ] 1.3 **TRIANGULATE:** agregar casos con manifiesto incompleto, hash de split ausente y campos extra; confirmar que GENERALIZA y que rechaza lo invalido. (SCI-001)
- [ ] 1.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (SCI-001)
- [ ] 1.5 Consumir el resultado del benchmark de `c-228` y seleccionar exactamente un modelo (el mejor por los criterios fijados de antemano); emitir `evaluation/data/modelo_supervisado_c232/` con el manifiesto (pesos/puntero + SHA-256, tokenizer, version del codebook, hash del split, preprocesamiento, comando de evaluacion) y registrar la decision del CHECKPOINT A. (SCI-001)
- [ ] 1.6 Verificar con una prueba que el artefacto aborta/registra el bloqueo si `c-228` no entrego modelo o benchmark; registrar los SHA-256 del artefacto congelado. (SCI-001)
- [ ] 1.7 Verificar con `git diff --stat` que no se modifico el clasificador de produccion, el prompt vigente ni las predicciones congeladas. (SCI-001)

## 2. Integracion detras del mismo contrato (TDD, SCI, IPA; CHECKPOINT B)

- [ ] 2.1 **RED:** escribir pruebas que describan el adaptador del modelo supervisado a traves del contrato de `c-227` (`BaseClassifier`/registro de proveedores) sin tocar el hibrido, antes de la implementacion; ejecutar y confirmar que fallan. (SCI-002, IPA «Proveedor supervisado»)
- [ ] 2.2 **GREEN:** implementar el adaptador y registrar el proveedor supervisado (offline, pesos congelados), con la minima logica para pasar las pruebas. (SCI-002, IPA «Proveedor supervisado»)
- [ ] 2.3 **TRIANGULATE:** agregar casos de seleccion por configuracion, de contrato canonico preservado (cinco cadenas exactas) y de fallo explicito ante proveedor desconocido; confirmar que GENERALIZA. (SCI-002, IPA «Proveedor supervisado»)
- [ ] 2.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (SCI-002)
- [ ] 2.5 Implementar la seleccion por configuracion del proveedor supervisado (default sin cambios: resuelve al hibrido salvo que el veredicto sea reemplazar). (SCI-003, IPA «Proveedor supervisado»)
- [ ] 2.6 Verificar con una prueba de neutralidad que, con el default, se reproducen caso por caso las predicciones del hibrido y que ningun numero canonico cambia; verificar que las cinco cadenas canonicas permanecen exactas. (SCI-003)
- [ ] 2.7 **[CHECKPOINT B]** Confirmar con los autores, y registrar, la decision sobre el default entregado (BLOQUEA la 2.5 si implica cambiar el default). Si el veredicto (grupo 4) aun no existe, dejar 2.5 en hibrido por defecto. (SCI-003)

## 3. Contraste cabeza a cabeza (TDD, DCD-001; depende de c-229 y c-230)

- [ ] 3.1 **RED:** escribir `evaluation/tests/test_contraste_cabeza_a_cabeza_c232.py` con pruebas sinteticas de la tabla pareada (aciertos por sistema, tabla 2x2, diferencia pareada con IC, McNemar) antes de existir el modulo; ejecutar y confirmar que fallan. (DCD-001)
- [ ] 3.2 **GREEN:** implementar las funciones puras del contraste con la minima logica para pasar las pruebas, reutilizando `evaluation/metrics.py` y `evaluation/stats.py` sin modificarlos. (DCD-001)
- [ ] 3.3 **TRIANGULATE:** agregar casos sin discordancias, con un caso sin pareja y con interseccion de textos, y confirmar que GENERALIZA sin romper. (DCD-001)
- [ ] 3.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (DCD-001)
- [ ] 3.5 Implementar el script `evaluation/data/campana/analisis/analisis_veredicto_c232.py` (solo lectura, determinista, sin red ni Gemini): lee el modelo congelado, las predicciones del hibrido y la referencia retenida, y el corpus de `c-229`; emite `analisis_veredicto_c232.{json,md,SHA256SUMS.txt}`. (DCD-001)
- [ ] 3.6 Implementar el anclaje que aborta antes de escribir si no reproduce `142/206` y macro-F1 `0,7024` sobre la referencia vigente; verificar que el script termina con error sin escribir si un caso carece de pareja. (DCD-001)
- [ ] 3.7 Verificar que dos corridas con los mismos insumos son identicas byte a byte y que los SHA-256 de las entradas no cambian. (DCD-001)
- [ ] 3.8 Verificar que cada lectura sobre los `206` queda rotulada como contraste descriptivo y declara que `0,85` no es alcanzable sobre esa referencia. (DCD-001)

## 4. Regla pre-registrada y veredicto (DCD-002; CHECKPOINT C)

- [ ] 4.1 **RED:** escribir pruebas de la evaluacion de la regla de tres vias (reemplazar / complementar / conservar) sobre resultados sinteticos, antes de la implementacion; ejecutar y confirmar que fallan. (DCD-002)
- [ ] 4.2 **GREEN:** implementar la funcion pura que aplica la regla pre-registrada y devuelve el veredicto con su evidencia, con la minima logica para pasar las pruebas. (DCD-002)
- [ ] 4.3 **TRIANGULATE:** agregar casos de cada salida, incluida la de «no supera» y el empate en el limite del IC; confirmar que GENERALIZA y que la salida es exhaustiva y exclusiva. (DCD-002)
- [ ] 4.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (DCD-002)
- [ ] 4.5 Registrar la regla pre-registrada en `docs/campana-medicion/runbook-veredicto-c232.md` con los umbrales y el margen (OQ2), fechada ANTES de correr el contraste; verificar que no se modifica despues de observar el resultado. (DCD-002)
- [ ] 4.6 **[CHECKPOINT C]** Presentar a los autores el veredicto con su evidencia y su IC; registrar la decision. Si el veredicto es reemplazar, presentar tambien el cambio del default entregado antes de aplicarlo. (DCD-002, TD «Veredicto honesto»)
- [ ] 4.7 Producir el veredicto del script y verificar que es exactamente uno de los tres, con evidencia y sin ocultar la salida «no supera». (DCD-002)

## 5. Tesis, memo y trazabilidad (TD, NC; tras 0.7)

- [ ] 5.1 Informar en `07-resultados.tex` el contraste cabeza a cabeza por sistema y por lectura (retenida y prevalencia natural) con sus intervalos, rotulado; no presentar una lectura como si la otra no existiera. (TD «Veredicto honesto»)
- [ ] 5.2 Acotar en `08-discusion.tex` el alcance y las limitaciones del veredicto, sin afirmar mas de lo medido. (TD «Veredicto honesto»)
- [ ] 5.3 Declarar en `09-conclusiones.tex` y `10-recomendaciones.tex` el veredicto (reemplazar / complementar / conservar), incluido «no supera», y su consecuencia sobre la configuracion entregada; si no es reemplazar, declarar que el hibrido sigue siendo el clasificador entregado; declarar la dependencia de `c-228`/`c-229`/`c-230` y de datos inexistentes. (TD «Veredicto honesto»)
- [ ] 5.4 Si el veredicto es reemplazar, revisar con los autores la declaracion de la configuracion entregada (Anexo B / nota de version, `12-anexos.tex`) y actualizarla; si no, verificar que la declaracion no cambia. (TD «Veredicto honesto»)
- [ ] 5.5 Agregar la seccion aditiva (ver 0.7) en `numeros-canonicos.md` con las dos lecturas, la diferencia pareada, McNemar y el veredicto, cada uno con procedencia, ambito y estado; declarar que no cambia `0,6893`, el macro-F1 `0,7024` ni el veredicto del `0,85` y que no altera las secciones `3.1` a `3.41`. (NC «Registro aditivo»)
- [ ] 5.6 Verificar con `git diff` dirigido que la seccion del memo es aditiva y que la prosa no introduce identificadores `c-NNN` ni valores canonicos nuevos; verificar que `rg` no encuentra el `0,85` presentado como alcanzable sobre los `206` ni el modelo presentado como entregado si no lo es. (TD «Veredicto honesto», NC «Registro aditivo»)
- [ ] 5.7 Compilar con XeLaTeX (`latexmk -xelatex main.tex`), verificar `\@abspage@last`, cero referencias indefinidas y cero etiquetas duplicadas; registrar el delta de paginas. Si el entorno no tiene LaTeX, registrar la compilacion como tarea diferida al release. (TD «Veredicto honesto»)
- [ ] 5.8 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada del change con los artefactos nuevos, la seccion del memo y las anclas de prosa (archivo:linea y frase verificable). (NC «Registro aditivo»)

## 6. Verificacion de cierre

- [ ] 6.1 Volver a correr `cd evaluation && pytest -q` y `cd App/Backend && pytest -m "not integration"` y confirmar que no hay regresiones; correr el contraste una vez mas y comparar SHA-256 con 3.7.
- [ ] 6.2 Confirmar con `git diff --stat` que no cambiaron las cinco cadenas canonicas, el prompt vigente, los parametros de inferencia, la evidencia congelada ni las predicciones; confirmar que el default entrega el hibrido salvo veredicto reemplazar.
- [ ] 6.3 Confirmar que los tres checkpoints (A, B, C) quedaron registrados, que la regla pre-registrada es anterior al contraste y que las tareas condicionadas se declaran bloqueadas si faltaron los insumos.
- [ ] 6.4 Correr `openspec validate c-232-integrar-el-clasificador-supervisado-en-la-configuracion-entregada --strict` y verificar que pasa.
- [ ] 6.5 Dejar a cargo del orquestador la actualizacion de `CHANGES.md` y el `engram sync`; no pushear, no crear tag ni release.
- [ ] 6.6 Guardar en Engram el resumen del change con el nombre, los artefactos, la seccion del memo, los SHA-256, el veredicto y el resultado de las verificaciones; reportar al orquestador con la tabla de evidencia del ciclo TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1-1.4 | `evaluation/tests/test_congelado_modelo_c232.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | manifiesto incompleto, hash ausente, extras | limpio |
| 2.1-2.4 | `App/Backend/tests/test_*_c232.py` | Unit | `pytest -m "not integration"` | falla por ausencia | pasa | config, contrato canonico, proveedor desconocido | limpio |
| 3.1-3.4 | `evaluation/tests/test_contraste_cabeza_a_cabeza_c232.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | sin discordancias, sin pareja, interseccion | limpio |
| 4.1-4.4 | `evaluation/tests/test_regla_veredicto_c232.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | reemplazar/complementar/conservar, limite de IC | limpio |
