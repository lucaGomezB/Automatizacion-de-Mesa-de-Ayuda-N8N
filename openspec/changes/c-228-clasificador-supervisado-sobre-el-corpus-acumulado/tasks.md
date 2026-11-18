# Tasks: Clasificador supervisado sobre el corpus acumulado

Al final de cada tarea, entre parentesis, el requisito del change que cumple, por nombre corto entre comillas angulares precedido de su capacidad. Nombres cortos: `SCC` (`supervised-corpus-curation`) «SCC-001», «SCC-002», «SCC-003», «SCC-004»; `SCB` (`supervised-classifier-benchmark`) «SCB-001», «SCB-002», «SCB-003»; `TCR` (`taxonomy-codebook-revision`) «TCR-001», «TCR-002», «TCR-003»; `NPE` (`natural-prevalence-evaluation-corpus`) «NPE-001», «NPE-002», «NPE-003»; `TD` (`tesis-document`) «Ejemplar sin cambios», «Informe posterior»; `NC` (`tesis-numeros-canonicos`) «Registro aditivo 3.41». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

**Alcance (adaptacion a la devolucion de tercera instancia, ver `proposal.md`):** por defecto este change se aplica DESPUES de cerrar la entrega (`c-235` → `c-239`) y despues de `c-229` y `c-230`. No modifica el ejemplar que se defiende. Ninguna tarea usa cifras ni artefactos retirados por `c-235`.

Este change SI escribe codigo ejecutable: aplica el ciclo TDD estricto (RED → GREEN → TRIANGULATE → REFACTOR) sobre las funciones puras de curacion y de particion, con la suite de `evaluation/` como red de seguridad. Los fixtures de prueba son sinteticos y se rotulan como tales en nombre de archivo, cabecera y salida. El entrenamiento real queda condicionado al volumen (OQ3) y a las compuertas K-01 y K-02.

Gobernanza **ALTA**. Checkpoints humanos: **CHECKPOINT A** antes de tocar el esquema de `clasificacion_log`; **CHECKPOINT B** compuertas K-01 y K-02 antes de exportar o etiquetar datos reales; **CHECKPOINT C** antes de entrenar o publicar un modelo; **CHECKPOINT D** antes de cualquier envio de texto a terceros.

## Estado: DETENIDO (18/11/2026)

El change queda **detenido** y se conserva como trabajo futuro la maquinaria offline del horizonte 1 (funciones puras de curacion y particion, arnes con fixtures sinteticos rotulados). Las tareas quedan **sin marcar**; nada se aplico. Faltan los dos insumos de la familia post-entrega (marco poblacional completo y `clasificacion_log` real acumulado) y las condiciones de consentimiento de etiquetadores nuevos (desde `E6`) y K-02. Reapertura solo con un periodo real de operacion, la exportacion completa de la tabla `incidente` (marco para `c-229` y log real para este change), el consentimiento escrito de los etiquetadores independientes y la decision K-02.

## 0. Preparacion, compuertas y linea de base

- [ ] 0.1 Leer `proposal.md`, `design.md` (D0 a D10) y los seis specs delta; cargar los `SKILL.md` de `python-testing` y `pytest-coverage` antes de escribir codigo y registrar la resolucion.
- [ ] 0.2 Verificar que `c-235` a `c-239` estan archivados (o registrar la decision de los autores de adelantar, OQ7) y que `c-229` y `c-230` estan aplicados o registrar que el grupo 4 queda bloqueado.
- [ ] 0.3 Capturar la linea de base: `git status`, `git rev-parse HEAD`, `sha256sum data/corpus_evaluacion_pseudonimizado.json evaluation/data/campana/doble_etiquetado.csv evaluation/data/campana/codebook_doble_etiquetado.md`; reproducir por comando la composicion por sector del corpus de 200 (esperado: Hardware 85, Software 67, Seguridad 31, Sistemas 16, Bases de Datos 1) y los discordantes E1/E2 (esperado: 62, de ellos 29 `Sistemas`/`Soporte Tecnico Software`). Si no coinciden, detenerse y reportar. (TCR-002)
- [ ] 0.4 **Red de seguridad:** correr `cd evaluation && pytest -q` y registrar el resultado (si algo falla, detenerse y reportarlo como fallo preexistente).
- [ ] 0.5 Releer `App/Backend/app/models/clasificacion_log.py`, `evaluation/no_solape.py`, `scripts/corpus_ingest/pseudonymize_corpus.py`, `evaluation/metrics.py` y `evaluation/stats.py`; confirmar que la curacion y la particion se apoyan en ellos sin reescribirlos.
- [ ] 0.6 **[CHECKPOINT A — BLOQUEA 1.5]** Si la curacion exige una tabla o columna nueva, presentar al autor el esquema y la migracion y no avanzar sin confirmacion. Si no hace falta, registrar la decision.
- [ ] 0.7 **[CHECKPOINT B — K-02, BLOQUEA 1.5, 3.3 Y 4]** Registrar la respuesta de los autores a OQ1 y OQ2: si `clasificacion_log` tiene filas reales de operacion; autorizacion institucional escrita (original en custodia del director); base de licitud bajo la Ley 25.326 e informacion o consentimiento de los empleados. Sin respuesta afirmativa y documentada, registrar el bloqueo. (SCC-001)
- [ ] 0.8 **[CHECKPOINT B — K-01, BLOQUEA 1.5 Y 3.3]** Definir con los autores y el director el procedimiento de procedencia: export crudo del sistema con sus marcas temporales originales, constancia de la organizacion sobre la extraccion (original en custodia del director), SHA-256 del export crudo a versionar, prohibicion de textos redactados por los autores o generados o asistidos por IA como datos, y verificacion del director antes del analisis. Registrarlo en `dictamen-correcciones.md`. (SCC-004)
- [ ] 0.9 **[CHECKPOINT D — OQ4]** Registrar, por modelo (BERT, Llama 3, Mistral, Qwen), donde corre (local por defecto; API de terceros solo con K-02) y si el comparador hibrido sale de predicciones ya registradas o exige una corrida nueva contra la Gemini API; en ese caso, bloquear hasta K-02. (SCB-002)
- [ ] 0.10 **[OQ3]** Registrar el volumen minimo para el entrenamiento real y el modelo base (`BETO` vs `xlm-roberta`).
- [ ] 0.11 Releer el indice de `numeros-canonicos.md` y confirmar que la seccion `3.41` sigue reservada a este change y libre; si esta ocupada, detenerse y reportar al orquestador.

## 1. Curacion del corpus (TDD, SCC)

- [ ] 1.1 **RED:** escribir `evaluation/tests/test_curacion_corpus_supervisado_c228.py` con fixtures rotulados como sinteticos (`*_sintetico*`, cabecera `"naturaleza": "sintetico"`) que prueben la seleccion de casos validados, el descarte de `fallback`/`confianza 0.0`, la exclusion de filas de corridas de evaluacion y de textos ya versionados, y el control de calidad; confirmar que fallan por ausencia del modulo. (SCC-001, SCC-003)
- [ ] 1.2 **GREEN:** implementar `evaluation/curacion_corpus_supervisado.py` con la minima logica, reutilizando `evaluation/no_solape.py` sin modificarlo. (SCC-002, SCC-003)
- [ ] 1.3 **TRIANGULATE:** agregar casos con y sin `sector_id_validado`, etapas `deterministic`/`gemini`/`fallback`, etiquetas canonicas y fuera de conjunto, duplicados de texto y solape con el corpus de 200; confirmar que generaliza. (SCC-002, SCC-003)
- [ ] 1.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso. (SCC-003)
- [ ] 1.5 **[BLOQUEADA HASTA 0.6, 0.7 Y 0.8]** Implementar y ejecutar el `main()` sobre el export crudo acreditado: verificar que las compuertas estan cerradas, registrar el SHA-256 del export crudo, pseudonimizar, deduplicar, verificar no solape con el corpus de 200 y con el conjunto retenido que exista, y emitir el corpus versionado mas el resumen de control de calidad. (SCC-001, SCC-002, SCC-003, SCC-004)
- [ ] 1.6 Verificar con una prueba que el pipeline aborta sin escribir si falta una compuerta, si el hash del export no coincide o si hay solape; registrar los SHA-256 del corpus emitido. (SCC-001, SCC-002, SCC-004)
- [ ] 1.7 Verificar con `git diff --stat` que no cambio el clasificador de produccion, el prompt vigente ni las predicciones congeladas. (SCC-002)

## 2. Particion y arnes (TDD, SCB)

- [ ] 2.1 **RED:** escribir `evaluation/tests/test_particion_supervisado_c228.py` con fixtures sinteticos rotulados que prueben la particion disjunta, agrupada y estratificada, con el conjunto retenido fuera de `train`/`dev`; confirmar que fallan. (SCB-001)
- [ ] 2.2 **GREEN:** implementar la funcion pura de particion. (SCB-001)
- [ ] 2.3 **TRIANGULATE:** agregar textos casi duplicados entre particiones e ids del conjunto retenido; confirmar interseccion vacia y rotulo «interna» cuando el retenido sale de `clasificacion_log`. (SCB-001)
- [ ] 2.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso. (SCB-001)
- [ ] 2.5 Implementar el arnes de entrenamiento local tipo BERT (pesos fijados por hash, sin red en la inferencia, semilla fija, `dev` para parada temprana, `test` una vez); registrar `n` de entrenamiento y de prueba. (SCB-002)
- [ ] 2.6 Implementar el benchmark local de `Llama 3`, `Mistral` y `Qwen`; tomar el comparador hibrido de las predicciones registradas segun 0.9. (SCB-002)
- [ ] 2.7 Implementar el reporte por clase con `evaluation/metrics.py`, con el rotulo del conjunto retenido («corpus probabilistico acreditado» o «particion retenida interna») y, si se informa algo sobre el corpus de 200, el rotulo de contraste descriptivo dentro de la muestra que no evalua el supervisado. (SCB-003)
- [ ] 2.8 **[CHECKPOINT C]** Verificar que el arnes, sin volumen o con compuertas abiertas, registra el bloqueo en lugar de emitir un modelo; verificar que dos corridas con la misma semilla son identicas. (SCB-002)

## 3. Taxonomia y codebook (TCR)

- [ ] 3.1 Revisar en `codebook_doble_etiquetado.md` las definiciones de `Sistemas` y `Soporte Tecnico Software` y el criterio de frontera, con ejemplos tomados solo de textos versionados y acreditados (nunca redactados por los autores ni generados por IA); documentar la definicion anterior y la nueva. (TCR-001)
- [ ] 3.2 Verificar que las cinco cadenas canonicas permanecen exactas. (TCR-001)
- [ ] 3.3 **[BLOQUEADA HASTA 0.7 Y 0.8]** Medir la ambiguedad: «antes» con E1/E2 sobre los 200 (0.3); «despues» con etiquetado nuevo bajo compuertas, con planillas originales, marcas temporales de la herramienta y etiquetadores registrados. Sin etiquetado nuevo, registrar que no hay «despues». Reportar aunque no mejore. (TCR-002)
- [ ] 3.4 Registrar, si corresponde, la propuesta de actualizacion de `TAX-004` y del prompt, sin aplicarla. (TCR-003)

## 4. Corpus probabilistico acreditado (NPE; depende de c-229, c-230 y del CHECKPOINT B)

- [ ] 4.1 **[BLOQUEADA HASTA c-229 Y c-230]** Consumir el corpus probabilistico acreditado de `c-229` con la referencia por mayoria de `c-230`; verificar que sus compuertas de procedencia y etica constan cerradas, cuotas prefijadas y disjuncion con el corpus de 200 y con el curado. Si no esta disponible, registrar el bloqueo sin sustituirlo. (NPE-001)
- [ ] 4.2 Verificar la regla de referencia por mayoria y la fiabilidad multi-evaluador registradas por `c-230`. (NPE-002)
- [ ] 4.3 Evaluar el supervisado y el hibrido sobre el corpus sin exclusiones, con el estimador de `c-229` y `evaluation/metrics.py`; rotular cada lectura. (NPE-002, NPE-003)

## 5. Memo, registro y tesis posterior (TD, NC)

- [ ] 5.1 Agregar la seccion `### 3.41` en `numeros-canonicos.md` solo con valores producidos con compuertas cerradas, cada uno con procedencia, ambito y estado; si no hay ninguno, registrar la seccion con el estado de bloqueo y sin cifras. (NC «Registro aditivo 3.41»)
- [ ] 5.2 Verificar con `git diff` dirigido que la seccion es aditiva y que no aparece ninguna cifra retirada por `c-235`. (NC «Registro aditivo 3.41»)
- [ ] 5.3 Verificar con `git diff --stat "docs/Tesis/v10 (IA)/paper/sections"` que este change no modifico el ejemplar de la defensa. (TD «Ejemplar sin cambios»)
- [ ] 5.4 Solo en una version posterior a la defensa y con compuertas cerradas: informar los resultados respetando lo que `c-235` fija en `subsec:clasificador-supervisado`, `subsec:frontera-sistemas` y la limitacion de `Sistemas`; compilar con XeLaTeX y verificar referencias. Si no se cumplen las condiciones, registrar la tarea como no aplicable. (TD «Informe posterior»)
- [ ] 5.5 Agregar en `dictamen-correcciones.md` la entrada del change con las compuertas, los artefactos y la seccion `3.41`.
- [ ] 5.6 Registrar en `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (archivo de `c-237`) el trabajo de este change hecho con asistentes de IA: que codigo, analisis o texto produjo, con que herramienta y como verificaron los autores cada cifra.

## 6. Verificacion de cierre

- [ ] 6.1 Volver a correr `cd evaluation && pytest -q`; repetir curacion y particion y comparar SHA-256.
- [ ] 6.2 Confirmar con `git diff --stat` que no cambiaron el clasificador de produccion, el prompt, la configuracion, las cinco cadenas ni el ejemplar.
- [ ] 6.3 Correr sobre los artefactos nuevos del change la busqueda de cifras y alias retirados que fija la seccion de adaptacion de `proposal.md` y confirmar que no hay coincidencias.
- [ ] 6.4 Confirmar que los checkpoints A a D quedaron registrados y que lo no ejecutado figura como bloqueado.
- [ ] 6.5 Correr `openspec validate c-228-clasificador-supervisado-sobre-el-corpus-acumulado --strict`.
- [ ] 6.6 Dejar a cargo del orquestador `CHANGES.md` y el `engram sync`; no pushear, no crear tag.
- [ ] 6.7 Guardar en Engram el resumen y reportar con la tabla de evidencia del ciclo TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1-1.4 | `evaluation/tests/test_curacion_corpus_supervisado_c228.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | validado/fallback, canonicas/fuera, duplicados, solape con los 200 | limpio |
| 2.1-2.4 | `evaluation/tests/test_particion_supervisado_c228.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | casi duplicados, ids del retenido, rotulo interna | limpio |
