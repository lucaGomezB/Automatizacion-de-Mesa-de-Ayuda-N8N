# Tasks: Integrar el clasificador supervisado en la configuracion entregada

Al final de cada tarea, entre parentesis, el requisito del change que cumple, por nombre corto precedido de su capacidad. Nombres cortos: `SCI` (`supervised-classifier-integration`) «SCI-001», «SCI-002», «SCI-003»; `DCD` (`delivered-classifier-decision`) «DCD-001», «DCD-002», «DCD-003»; `IPA` (`inference-provider-abstraction`) «Proveedor supervisado»; `TD` (`tesis-document`) «Ejemplar sin cambios», «Veredicto posterior»; `NC` (`tesis-numeros-canonicos`) «Registro aditivo 3.42». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

**Alcance (adaptacion a la devolucion de tercera instancia, ver `proposal.md`):** por defecto este change se aplica DESPUES de cerrar la entrega (`c-235` → `c-239`) y queda BLOQUEADO hasta que `c-228`, `c-229` y `c-230` entreguen. No modifica el ejemplar que se defiende ni el default entregado. Ninguna tarea usa cifras ni artefactos retirados por `c-235`, el corpus de 200 casos como conjunto de contraste ni el canario de `c-227` como referencia.

Este change SI escribe codigo ejecutable: aplica el ciclo TDD estricto (RED → GREEN → TRIANGULATE → REFACTOR) con fixtures rotulados como sinteticos en nombre de archivo, cabecera y salida, y con la suite de `evaluation/` y la del backend como red de seguridad.

Gobernanza **ALTA**. Checkpoints: **A** antes de consumir `c-228` y congelar; **B** antes de cambiar el default; **C** antes de emitir el veredicto; **D** antes de cualquier envio de texto a terceros (incluida la Gemini API).

## 0. Preparacion, compuertas y linea de base

- [ ] 0.1 Leer `proposal.md`, `design.md` (D0 a D10) y los cinco specs delta; cargar los `SKILL.md` de `python-testing`, `python-design-patterns` y `pytest-coverage` y registrar la resolucion.
- [ ] 0.2 Verificar que `c-235` a `c-239` estan archivados (o registrar la decision de los autores de adelantar el grupo 1, OQ6) y el estado de `c-228`, `c-229` y `c-230`; registrar como bloqueados los grupos 2, 5 y 6 si falta alguno, sin sustituir insumos.
- [ ] 0.3 Capturar la linea de base: `git status`, `git rev-parse HEAD` y `sha256sum` de `App/Backend/app/classifiers/*.py`. Registrar modificaciones ajenas y no tocarlas.
- [ ] 0.4 **Red de seguridad:** correr `cd evaluation && pytest -q` y `cd App/Backend && pytest -m "not integration"`; si algo falla, detenerse y reportarlo como fallo preexistente.
- [ ] 0.5 Releer `App/Backend/app/classifiers/provider.py`, `base.py`, `hybrid.py` y `Settings`; confirmar que la integracion se apoya en la abstraccion de `c-227` sin reescribirla.
- [ ] 0.6 **[CHECKPOINT D — K-02, BLOQUEA EL GRUPO 5]** Registrar la respuesta de los autores a OQ3: si existen predicciones del hibrido registradas en operacion para el corpus acreditado o si la autorizacion escrita de la organizacion cubre expresamente enviar esos textos a la Gemini API. Sin una de las dos, registrar el bloqueo del contraste. (DCD-003)
- [ ] 0.7 **[K-01, BLOQUEA EL GRUPO 5]** Verificar que `c-229` y `c-230` registraron cerradas sus compuertas de procedencia y etica (export crudo, constancia de la organizacion en custodia del director, SHA-256, verificacion del director) para el corpus y la referencia que se consumen. (DCD-003)
- [ ] 0.8 Releer el indice de `numeros-canonicos.md` y confirmar que la seccion `3.42` sigue reservada a este change y libre; si esta ocupada, detenerse y reportar.

## 1. Sin datos nuevos: funciones puras y adaptador (TDD; posterior a la entrega salvo OQ6)

- [ ] 1.1 **RED:** escribir `evaluation/tests/test_congelado_modelo_c232.py` con manifiestos sinteticos rotulados (campos obligatorios, hashes, `procedencia_datos`, comando); confirmar que fallan. (SCI-001)
- [ ] 1.2 **GREEN:** implementar el validador de manifiesto como funcion pura. (SCI-001)
- [ ] 1.3 **TRIANGULATE:** manifiesto incompleto, hash ausente, campos extra, procedencia ausente; confirmar que rechaza lo invalido. (SCI-001)
- [ ] 1.4 **REFACTOR:** correr las pruebas tras cada paso. (SCI-001)
- [ ] 1.5 **RED:** escribir pruebas del adaptador local del modelo supervisado a traves de `BaseClassifier`/registro de `c-227`, con un modelo sintetico rotulado, sin tocar el hibrido; confirmar que fallan. (SCI-002, IPA «Proveedor supervisado»)
- [ ] 1.6 **GREEN:** implementar el adaptador offline y registrarlo como proveedor seleccionable, con default sin cambios. (SCI-002, SCI-003, IPA «Proveedor supervisado»)
- [ ] 1.7 **TRIANGULATE:** seleccion por configuracion, cinco cadenas exactas, proveedor desconocido, ausencia de llamadas de red; confirmar que generaliza. (SCI-002, IPA «Proveedor supervisado»)
- [ ] 1.8 **REFACTOR:** correr las pruebas tras cada paso; verificar con una prueba de neutralidad que el default reproduce el hibrido. (SCI-003)
- [ ] 1.9 **RED:** escribir `evaluation/tests/test_contraste_cabeza_a_cabeza_c232.py` con datos sinteticos rotulados (tabla 2x2, diferencia pareada con IC, McNemar, caso sin pareja, hash de entrada que no coincide); confirmar que fallan. (DCD-001)
- [ ] 1.10 **GREEN:** implementar las funciones puras del contraste reutilizando `evaluation/metrics.py` y `evaluation/stats.py` sin modificarlos. (DCD-001)
- [ ] 1.11 **TRIANGULATE:** sin discordancias, caso sin pareja, subconjunto no pre-especificado rechazado; confirmar que generaliza. (DCD-001)
- [ ] 1.12 **REFACTOR:** correr las pruebas tras cada paso. (DCD-001)
- [ ] 1.13 **RED:** escribir `evaluation/tests/test_regla_veredicto_c232.py` con resultados sinteticos de las tres salidas, «no supera» y empate en el limite del IC; confirmar que fallan. (DCD-002)
- [ ] 1.14 **GREEN:** implementar la funcion pura de la regla de tres vias. (DCD-002)
- [ ] 1.15 **TRIANGULATE:** confirmar salida exhaustiva y exclusiva. (DCD-002)
- [ ] 1.16 **REFACTOR:** correr las pruebas tras cada paso. (DCD-002)

## 2. Congelado del modelo seleccionado (depende de c-228; CHECKPOINT A)

- [ ] 2.1 **[CHECKPOINT A]** Confirmar con los autores el criterio de seleccion de `c-228` (OQ1) y el esquema binario o puntero + hash. (SCI-001)
- [ ] 2.2 **[BLOQUEADA HASTA c-228]** Consumir el benchmark de `c-228`, seleccionar exactamente un modelo y emitir `evaluation/data/modelo_supervisado_c232/` con el manifiesto validado; si `c-228` no entrego, registrar el bloqueo. (SCI-001)
- [ ] 2.3 Verificar con `git diff --stat` que no cambio el clasificador de produccion, el prompt ni las predicciones congeladas. (SCI-001)

## 3. Integracion con el modelo real (CHECKPOINT B)

- [ ] 3.1 **[BLOQUEADA HASTA 2.2]** Conectar el adaptador del grupo 1 a los pesos congelados; verificar inferencia local, determinista y sin red. (SCI-002, IPA «Proveedor supervisado»)
- [ ] 3.2 **[CHECKPOINT B]** Registrar con los autores que el default sigue en el hibrido; solo un veredicto reemplazar (grupo 5) habilita revisar ese default. (SCI-003)

## 4. Regla pre-registrada y constancia (DCD-002; antes del grupo 5)

- [ ] 4.1 Registrar la regla en `docs/campana-medicion/runbook-veredicto-c232.md` (umbrales, margen de macro-F1, subconjuntos pre-especificados, correccion por comparaciones multiples, SHA-256 de las entradas previstas; OQ2) ANTES de obtener las predicciones sobre el corpus acreditado. (DCD-002)
- [ ] 4.2 Entregar al director la constancia del pre-registro con el SHA-256 del runbook (OQ4) y registrar su fecha en `dictamen-correcciones.md`; sin constancia, el grupo 5 queda bloqueado. (DCD-002)

## 5. Contraste y veredicto (depende de c-229, c-230, 0.6, 0.7 y 4.2; CHECKPOINTS C y D)

- [ ] 5.1 **[BLOQUEADA]** Obtener las predicciones del hibrido sobre el corpus acreditado segun 0.6 (registradas en operacion o corrida autorizada contra la Gemini API, declarando cantidad de textos, fecha y modelo) y las del modelo congelado (local). (DCD-001, DCD-003)
- [ ] 5.2 Implementar y correr `evaluation/data/campana/analisis/analisis_veredicto_c232.py` (solo lectura, determinista, sin red) sobre el corpus acreditado con la referencia por mayoria; emitir `analisis_veredicto_c232.{json,md,SHA256SUMS.txt}`. (DCD-001)
- [ ] 5.3 Verificar que el script aborta sin escribir si un hash de entrada no coincide con el pre-registrado o si un caso carece de pareja, y que dos corridas son identicas byte a byte. (DCD-001)
- [ ] 5.4 **[CHECKPOINT C]** Aplicar la regla y presentar a los autores el veredicto con evidencia e IC; registrar la decision. Si es reemplazar, presentar el cambio del default antes de aplicarlo. (DCD-002)

## 6. Memo, registro y tesis posterior (TD, NC)

- [ ] 6.1 Agregar la seccion `### 3.42` en `numeros-canonicos.md` solo con valores producidos con compuertas cerradas; si no hay ninguno, registrar el bloqueo sin cifras. (NC «Registro aditivo 3.42»)
- [ ] 6.2 Verificar con `git diff` dirigido que la seccion es aditiva y no cita cifras retiradas por `c-235`. (NC «Registro aditivo 3.42»)
- [ ] 6.3 Verificar con `git diff --stat "docs/Tesis/v10 (IA)/paper/sections"` que este change no modifico el ejemplar de la defensa. (TD «Ejemplar sin cambios»)
- [ ] 6.4 Solo en una version posterior a la defensa y con compuertas cerradas: informar el veredicto respetando el texto que deja `c-235`; compilar y verificar referencias. Si no se cumplen las condiciones, registrar la tarea como no aplicable. (TD «Veredicto posterior»)
- [ ] 6.5 Agregar en `dictamen-correcciones.md` la entrada del change con compuertas, constancia del pre-registro, artefactos y seccion `3.42`.
- [ ] 6.6 Registrar en `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (archivo de `c-237`) el trabajo de este change hecho con asistentes de IA, con herramienta y verificacion de los autores.

## 7. Verificacion de cierre

- [ ] 7.1 Volver a correr `cd evaluation && pytest -q` y `cd App/Backend && pytest -m "not integration"`; comparar SHA-256 del contraste con 5.3.
- [ ] 7.2 Confirmar con `git diff --stat` que no cambiaron cadenas canonicas, prompt, parametros, gate ni el ejemplar; que el default sigue en el hibrido salvo veredicto reemplazar.
- [ ] 7.3 Correr sobre los artefactos nuevos la busqueda de cifras y alias retirados que fija la seccion de adaptacion de `proposal.md` y confirmar que no hay coincidencias.
- [ ] 7.4 Confirmar que los checkpoints A a D y la constancia del pre-registro quedaron registrados, y que lo no ejecutado figura como bloqueado.
- [ ] 7.5 Correr `openspec validate c-232-integrar-el-clasificador-supervisado-en-la-configuracion-entregada --strict`.
- [ ] 7.6 Dejar a cargo del orquestador `CHANGES.md` y el `engram sync`; no pushear ni crear tag.
- [ ] 7.7 Guardar en Engram el resumen y reportar con la tabla de evidencia del ciclo TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1-1.4 | `evaluation/tests/test_congelado_modelo_c232.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | manifiesto incompleto, hash ausente, extras, procedencia | limpio |
| 1.5-1.8 | `App/Backend/tests/test_*_c232.py` | Unit | `pytest -m "not integration"` | falla por ausencia | pasa | config, contrato canonico, proveedor desconocido, sin red | limpio |
| 1.9-1.12 | `evaluation/tests/test_contraste_cabeza_a_cabeza_c232.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | sin discordancias, sin pareja, hash, subconjunto no pre-especificado | limpio |
| 1.13-1.16 | `evaluation/tests/test_regla_veredicto_c232.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | tres salidas, limite de IC | limpio |
