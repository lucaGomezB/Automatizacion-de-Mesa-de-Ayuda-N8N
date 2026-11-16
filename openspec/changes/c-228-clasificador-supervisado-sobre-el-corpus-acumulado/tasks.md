# Tasks: Clasificador supervisado sobre el corpus acumulado

Al final de cada tarea, entre parentesis, el requisito del change que cumple, por nombre corto entre comillas angulares precedido de su capacidad. Nombres cortos: `SCC` (`supervised-corpus-curation`) «SCC-001», «SCC-002», «SCC-003»; `SCB` (`supervised-classifier-benchmark`) «SCB-001», «SCB-002», «SCB-003»; `TCR` (`taxonomy-codebook-revision`) «TCR-001», «TCR-002», «TCR-003»; `NPE` (`natural-prevalence-evaluation-corpus`) «NPE-001», «NPE-002», «NPE-003»; `TD` (`tesis-document`) «Estado honesto», «Frontera Sistemas-Software»; `NC` (`tesis-numeros-canonicos`) «Registro aditivo». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Este change SÍ escribe codigo ejecutable: aplica el ciclo TDD estricto (RED → GREEN → TRIANGULATE → REFACTOR) sobre las funciones puras de curacion y de particion, con la suite de `evaluation/` como red de seguridad. El entrenamiento real queda **condicionado** al volumen del corpus (OQ1) y no se ejecuta si no se alcanza.

Gobernanza **ALTA** (datos nuevos, datos personales y entrenamiento). Checkpoints humanos obligatorios: **CHECKPOINT A** antes de tocar el esquema de `clasificacion_log` o crear tablas; **CHECKPOINT B** antes de exportar o etiquetar datos reales (consentimiento); **CHECKPOINT C** antes de entrenar o publicar cualquier modelo.

## 0. Preparacion y verificacion de estado

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D8) y los seis specs delta; cargar los `SKILL.md` completos de `python-testing` y `pytest-coverage` antes de escribir codigo y registrar la resolucion.
- [ ] 0.2 Capturar la linea de base como evidencia de partida: `git status`, `git rev-parse HEAD`, `sha256sum data/corpus_evaluacion_pseudonimizado.json evaluation/data/campana/doble_etiquetado_arbitrado.csv evaluation/data/campana/codebook_doble_etiquetado.md`, y los anclajes (`0,6893/206`, `+34`, techo `0,835`, manual `0,8278`, frontera `16/64`) del memo y del estudio de mejora. Registrar modificaciones preexistentes ajenas a este change y no tocarlas.
- [ ] 0.3 **Red de seguridad:** correr `cd evaluation && pytest -q` y registrar el resultado (debe pasar antes de editar; si algo falla, detenerse y reportarlo como fallo preexistente).
- [ ] 0.4 Releer `App/Backend/app/models/clasificacion_log.py` (columnas de validacion e intervencion), `evaluation/no_solape.py`, `scripts/corpus_ingest/pseudonymize_corpus.py` y `evaluation/metrics.py`/`evaluation/stats.py`; confirmar que la curacion y la particion pueden apoyarse en ellos sin reescribirlos.
- [ ] 0.5 **[CHECKPOINT A — BLOQUEA EL GRUPO 1]** Si la curacion exige una tabla o columna nueva en `clasificacion_log`, presentar al autor el esquema y la migracion propuestos y no avanzar sin confirmacion explicita. Si no hace falta, registrar la decision.
- [ ] 0.6 **[CHECKPOINT B — BLOQUEA LAS TAREAS 1.5 Y 4]** Confirmar con los autores el registro del consentimiento y la base de licitud antes de exportar o etiquetar datos reales. Registrar la respuesta.
- [ ] 0.7 **[CHECKPOINT/OQ1]** Confirmar el volumen minimo del corpus para habilitar el entrenamiento real y el modelo base (`BETO` vs `xlm-roberta`). Registrar la decision.
- [ ] 0.8 Releer el indice de `numeros-canonicos.md` y fijar el primer numero de seccion libre (hoy la ultima es `3.37`; esperado `3.41`). Registrar el numero elegido.

## 1. Curacion del corpus (TDD, SCC)

- [ ] 1.1 **RED:** escribir `evaluation/tests/test_curacion_corpus_supervisado_c228.py` con pruebas sinteticas de la seleccion de casos validados, del descarte de `fallback`/`confianza 0.0` y del control de calidad, antes de existir el modulo; ejecutar y confirmar que fallan por ausencia de la implementacion. (SCC-001, SCC-003)
- [ ] 1.2 **GREEN:** implementar `evaluation/curacion_corpus_supervisado.py` con la minima logica para pasar las pruebas, reutilizando `evaluation/no_solape.py` sin modificarlo. (SCC-002, SCC-003)
- [ ] 1.3 **TRIANGULATE:** agregar casos con entradas distintas (con y sin `sector_id_validado`; etapa `deterministic`/`gemini`/`fallback`; etiquetas canonicas y fuera de conjunto; duplicados de texto) y confirmar que GENERALIZA sin romper. (SCC-003)
- [ ] 1.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (SCC-003)
- [ ] 1.5 Implementar el `main()` de curacion: verificar consentimiento (CHECKPOINT B), leer `clasificacion_log` e `incidente`, pseudonimizar con `scripts/corpus_ingest/pseudonymize_corpus.py`, deduplicar, verificar no solape con los `206` y emitir el corpus versionado (UTF-8 sin BOM, LF) mas el resumen de control de calidad. (SCC-001, SCC-002, SCC-003)
- [ ] 1.6 Verificar con una prueba que el pipeline aborta sin escribir si no hay consentimiento o si hay solape con los `206`; registrar los SHA-256 del corpus emitido. (SCC-001, SCC-002)
- [ ] 1.7 Verificar con `git diff --stat` que no se modifico el clasificador de produccion, el prompt vigente ni las predicciones congeladas. (SCC-002)

## 2. Particion y arnes de evaluacion (TDD, SCB)

- [ ] 2.1 **RED:** escribir `evaluation/tests/test_particion_supervisado_c228.py` con pruebas sinteticas de la particion `train`/`dev`/`test` (disjunta, agrupada, estratificada, con los `206` retenidos) antes de existir el modulo; ejecutar y confirmar que fallan. (SCB-001)
- [ ] 2.2 **GREEN:** implementar la funcion pura de particion con la minima logica para pasar las pruebas. (SCB-001)
- [ ] 2.3 **TRIANGULATE:** agregar casos con textos casi duplicados entre particiones y con ids de los `206`; confirmar que la interseccion de textos es vacia y que los `206` no caen en `train`/`dev`. (SCB-001)
- [ ] 2.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (SCB-001)
- [ ] 2.5 Implementar el arnes de entrenamiento: ajuste de un modelo tipo BERT sobre `train` con `dev` para parada temprana, semilla fija, y evaluacion unica de `test`; registrar el `n` de entrenamiento y de prueba por separado. (SCB-002)
- [ ] 2.6 Implementar el benchmark de modelos abiertos (`Llama 3`, `Mistral`, `Qwen`) contra el hibrido congelado sobre las mismas particiones. (SCB-002)
- [ ] 2.7 Implementar el reporte de metricas por clase con `evaluation/metrics.py` (exactitud estricta y laxa, macro-F1, P/R/F1 con soporte) y el contraste descriptivo sobre los `206` con el rotulo de no alcanzabilidad del `0,85`. (SCB-003)
- [ ] 2.8 Verificar que el arnes, sin volumen suficiente, registra el bloqueo en lugar de emitir un modelo; verificar que dos corridas con la misma semilla son identicas. (SCB-002)

## 3. Taxonomia y codebook (TCR)

- [ ] 3.1 Revisar en `evaluation/data/campana/codebook_doble_etiquetado.md` las definiciones de `Sistemas` y `Soporte Tecnico Software` y el criterio de frontera, con ejemplos de casos limitrofes del corpus disponible; documentar la definicion anterior y la nueva con su procedencia. (TCR-001)
- [ ] 3.2 Verificar que las cinco cadenas canonicas permanecen exactas, sensibles a mayusculas y sin tildes, y que no se introdujo ningun sector fuera del conjunto canonico. (TCR-001)
- [ ] 3.3 Medir la ambiguedad de la frontera (proporcion de asignacion a una sola clase) antes y despues de la revision, con el `n` declarado; reportar el resultado aunque no mejore. (TCR-002)
- [ ] 3.4 Registrar, si corresponde, la propuesta de actualizacion de `TAX-004` y del prompt compartido, sin aplicarla; dejar constancia de que su aplicacion requiere aprobacion de los autores y se difiere por defecto. (TCR-003)

## 4. Corpus de prevalencia natural (NPE; depende de c-229 y del CHECKPOINT B)

- [ ] 4.1 **[BLOQUEADA HASTA c-229]** Consumir el corpus de prevalencia natural de `c-229`; verificar cuotas prefijadas por canal y sector, disjuncion con el corpus de ajuste y del curado, y procedencia documentada. Si no esta disponible, registrar el bloqueo y no sustituirlo por muestreo de conveniencia. (NPE-001)
- [ ] 4.2 Verificar el etiquetado limpio e independiente con la regla de referencia declarada y la fiabilidad inter-etiquetador registrada. (NPE-002)
- [ ] 4.3 Evaluar el modelo supervisado y el hibrido congelado sobre el corpus sin exclusiones, con intervalos sobre el universo (`evaluation/stats.py`) y metricas por clase (`evaluation/metrics.py`); rotular cada lectura y declarar la composicion de prevalencia natural. (NPE-002, NPE-003)

## 5. Tesis y memo (TD, NC; tras 0.8)

- [ ] 5.1 Declarar en `10-recomendaciones.tex::subsec:clasificador-supervisado` y `subsec:frontera-sistemas` que la linea depende de datos inexistentes y de consentimiento, que no se entrena ni se mide en este trabajo, y que `0,85` no es alcanzable sobre los `206` (`+34`, techo `0,835`, manual `0,8278`); mantener el caracter indicativo del umbral de volumen. (TD «Estado honesto»)
- [ ] 5.2 Precisar en `08-discusion.tex` la limitacion de `Sistemas`: la frontera como problema de taxonomia o de criterio de etiquetado (`16/64`), con remision a la revision del codebook y a la no alcanzabilidad del umbral, sin afirmar mejora del clasificador. (TD «Frontera Sistemas-Software»)
- [ ] 5.3 Agregar la seccion aditiva `### 3.41` (ver 0.8) en `numeros-canonicos.md` con los anclajes (`0,6893/206`, `+34`, techo `0,835`, manual `0,8278`, frontera `16/64`), cada uno con procedencia, ambito y estado; declarar la dependencia de datos y que no cambia ningun valor de las secciones `3.1` a `3.37`. (NC «Registro aditivo»)
- [ ] 5.4 Verificar con `git diff` dirigido que la seccion del memo es aditiva y que `10-recomendaciones.tex` no introduce identificadores `c-NNN` ni valores canonicos nuevos; verificar que `rg` no encuentra el `0,85` presentado como alcanzable sobre los `206`. (TD «Estado honesto», NC «Registro aditivo»)
- [ ] 5.5 Compilar con XeLaTeX (`latexmk -xelatex main.tex`), verificar `\@abspage@last`, cero referencias indefinidas y cero etiquetas duplicadas; registrar el delta de paginas. Si el entorno no tiene LaTeX, registrar la compilacion como tarea diferida al release. (TD «Estado honesto», TD «Frontera Sistemas-Software»)
- [ ] 5.6 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada del change con los artefactos nuevos, la seccion del memo y las anclas de prosa (archivo:linea y frase verificable). (NC «Registro aditivo»)

## 6. Verificacion de cierre

- [ ] 6.1 Volver a correr `cd evaluation && pytest -q` y confirmar que no hay regresiones; correr la curacion y la particion una vez mas y comparar SHA-256 con 1.6 y 2.3.
- [ ] 6.2 Confirmar con `git diff --stat` que no cambiaron el clasificador de produccion, el prompt vigente, la configuracion, las cinco cadenas canonicas ni las predicciones congeladas.
- [ ] 6.3 Confirmar que los tres checkpoints (A, B, C) quedaron registrados y que el entrenamiento real, si no se ejecuto por volumen, quedo declarado como condicionado.
- [ ] 6.4 Correr `openspec validate c-228-clasificador-supervisado-sobre-el-corpus-acumulado --strict` y verificar que pasa.
- [ ] 6.5 Dejar a cargo del orquestador la actualizacion de `CHANGES.md` y el `engram sync`; no pushear, no crear tag ni release.
- [ ] 6.6 Guardar en Engram el resumen del change con el nombre, los artefactos, la seccion del memo, los SHA-256 y el resultado de las verificaciones; reportar al orquestador con la tabla de evidencia del ciclo TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1-1.4 | `evaluation/tests/test_curacion_corpus_supervisado_c228.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | validado/fallback, canonicas/fuera, duplicados | limpio |
| 2.1-2.4 | `evaluation/tests/test_particion_supervisado_c228.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | casi duplicados, ids de los `206` | limpio |
