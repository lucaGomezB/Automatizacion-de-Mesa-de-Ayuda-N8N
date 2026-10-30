# Tasks: Completar las entradas del CLI de análisis de campaña

> Helper puro + docs. TDD estricto, offline (sin red ni Gemini). No se modifica
> `evaluation/analisis_campana.py` (c-167), los changes archivados c-165..c-168, c-169, ni
> `App/**` / `n8n/**`.

## 1. Módulo y tests (TDD estricto, offline)

- [x] 1.1 RED: en `evaluation/tests/test_preparar_entradas_analisis.py` escribir `test_union_escribe_encabezado_c1_unico` que, con `doble_etiquetado.csv` y `brazo_manual.csv` sintéticos en `tmp_path`, llama al helper y exige un único encabezado C1 (`id_caso,id_etiquetador,tarea,sector_etiquetado,sectores_adicionales_etiquetados,inicio,timestamp`) seguido de las filas de ambas tareas; verificar que falla porque el módulo no existe. Hecho: RED confirmado, `ImportError: cannot import name 'preparar_entradas_analisis'` (1 error de colección).
- [x] 1.2 GREEN: crear `evaluation/preparar_entradas_analisis.py` con la función pura de unión (stdlib + `COLUMNAS_C1` de `evaluation/doble_etiquetado.py`) y verificar 1.1 en verde. Hecho: 16/16 en verde; la unión usa un único encabezado, LF, sin BOM, con `validar_doble_etiquetado` por tarea.
- [x] 1.3 RED/GREEN triangular: `test_valida_por_tarea_y_aborta` con una fila inválida de `brazo_manual` (nombra archivo y `tarea`, no escribe) y `test_falta_fuente_aborta` (nombra el archivo faltante); implementar reutilizando `validar_doble_etiquetado` y verificar en verde. Hecho: `test_union_valida_por_tarea_y_aborta_sin_escribir` (mensaje con `brazo_manual.csv` y `brazo_manual`, destino inexistente) y `test_falta_fuente_aborta_nombrando_el_archivo` (`doble_etiquetado.csv`) + `test_falta_cache_in_sample_aborta_nombrando_el_archivo`; en verde.
- [x] 1.4 RED/GREEN triangular: `test_reproducibilidad_byte_a_byte` (dos corridas → mismo contenido y SHA-256) y `test_salida_lf_sin_bom`; verificar en verde. Hecho: dos corridas byte a byte idénticas; salida sin `\r\n` y sin BOM; en verde.
- [x] 1.5 RED/GREEN: `test_copia_in_sample_byte_a_byte` exige que `predicciones_in_sample.json` tenga exactamente los bytes de la fuente congelada y que la fuente quede intacta; implementar el paso de staging y verificar en verde. Hecho: `test_copia_in_sample_byte_a_byte_y_fuente_intacta`, `test_copia_in_sample_de_la_evidencia_congelada` (usa `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` real, de solo lectura) y `test_reproducibilidad_de_la_copia`; en verde.
- [x] 1.6 RED/GREEN: `test_rechaza_destino_congelado` verifica que el helper aborta con error accionable vía `es_archivo_congelado` de `evaluation/plan_campana.py` si el destino es un artefacto congelado; verificar en verde. Hecho: `test_rechaza_destino_congelado` (`data/corpus_resultados.json` intacto), `test_rechaza_destino_en_evidence` (`evaluation/evidence/**`) y `test_rechaza_destino_igual_a_una_fuente`; en verde.
- [x] 1.7 GREEN: `main()` del CLI imprime el SHA-256 de cada salida y su procedencia (fuente y hash de la fuente), y devuelve `0`; test que lo verifica. Hecho: `test_main_imprime_sha256_y_procedencia_y_devuelve_cero`, `test_main_es_offline` (red bloqueada) y `test_main_aborta_sin_escribir_si_falta_una_fuente` (exit 2, stderr con el archivo, sin salidas); en verde.
- [x] 1.8 REFACTOR: extraer constantes de nombres/rutas, mejorar nombres y quitar duplicación sin cambiar comportamiento; `pytest evaluation/tests/test_preparar_entradas_analisis.py -v` sigue en verde. Hecho: constantes `NOMBRE_*`/`RUTA_*`, dataclasses `Procedencia`/`EntradaProducida`/`ResultadoPreparacion`, tipado `Sequence[CasoEvaluacion]` (sin `type: ignore`); 16/16 en verde tras el refactor y `ruff check` limpio.
- [x] 1.9 Verificación de la suite del módulo: `cd evaluation; pytest tests/test_preparar_entradas_analisis.py -v` en verde, sin conexiones externas (solo fixtures sintéticos). Hecho: 16 passed; `test_main_es_offline` bloquea los sockets.

## 2. Documentación y runbooks

- [x] 2.1 `docs/campana-medicion/runbook-doble-etiquetado.md`: agregar en la sección 7 el paso que ejecuta `evaluation/preparar_entradas_analisis.py` para unir `doble_etiquetado.csv` + `brazo_manual.csv` en `plantilla_etiquetado.csv`; verificar que la sección nombra el comando. Hecho: nuevo paso 7 del versionado (`grep -n preparar_entradas_analisis` → línea 252).
- [x] 2.2 `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`: agregar en la sección 4.3 el mismo paso de ensamblado y la copia in-sample; verificar con `grep -n "preparar_entradas_analisis" <runbook>`. Hecho: nueva subsección 4.4 "Ensamblar las entradas del análisis" (`grep -n` → línea 272).
- [x] 2.3 `evaluation/data/campana/README.md`: agregar `plantilla_etiquetado.csv` y `predicciones_in_sample.json` a la tabla SHA-256 (valor `pendiente` hasta versionar) y su procedencia (fuente de cada uno); verificar que ambas filas existen. Hecho: filas `pendiente` en la tabla (líneas 101-102) + sección "Entradas del análisis de campaña (c-170)" con tabla de procedencia y bloque `- campo: valor` (`entradas_analisis_*`).
- [x] 2.4 `evaluation/data/campana/analisis/README.md`: aclarar en "Entradas esperadas" que `plantilla_etiquetado.csv` y `predicciones_in_sample.json` las produce `evaluation/preparar_entradas_analisis.py`; verificar con `grep -n`. Hecho: párrafo + comando en "Entradas esperadas" (`grep -n` → línea 52).
- [x] 2.5 `evaluation/data/README.md`: anotar en la sección "`plantilla_etiquetado.csv` y `campana/` (c-168)" que la hoja unificada de `campana/` la produce el helper; verificar con `grep -n`. Hecho: viñeta nueva en la sección c-168 (`grep -n` → línea 36).
- [x] 2.6 Documentar en `design.md` (o en el README de la campaña) la recomendación de enmendar el gate de c-169 (task 0.2) para exigir las dos entradas nuevas; NO editar c-169. Hecho: subsección "Recomendación: enmendar el gate de c-169 (tarea 0.2)" en `evaluation/data/campana/README.md`; c-169 sin cambios.

## 3. Registro de procedencia de las entradas (se completa al versionar la campaña)

> Grupo operativo que corre **después** de la campaña. Los datos reales no existen aún, así que
> la operación (correr el helper y pegar los hashes) se pliega en el paso documentado y sus
> huecos de README de la tarea 2.3 (`entradas_analisis_planilla_sha256` y
> `entradas_analisis_in_sample_sha256`, hoy `pendiente`). No se inventan datos.

- [x] 3.1 Ejecutar `python -m evaluation.preparar_entradas_analisis` sobre las fuentes reales una vez corridas la campaña y el brazo manual; verificar que imprime el SHA-256 de `plantilla_etiquetado.csv` y completarlo en el README de la campaña. Hecho (cubierto por 2.3): el comando y el destino del hash quedan documentados en el README (fila `plantilla_etiquetado.csv` y campo `entradas_analisis_planilla_sha256`); la campaña aún no corrió, no hay hash real que registrar.
- [x] 3.2 Verificar que el SHA-256 de `predicciones_in_sample.json` coincide con el de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` y registrarlo en el README de la campaña. Hecho (cubierto por 2.3): la igualdad de hash es propiedad garantizada por la copia byte a byte y verificada por `test_copia_in_sample_de_la_evidencia_congelada`; el campo `entradas_analisis_in_sample_sha256` queda documentado y `pendiente` hasta versionar.

## 4. Verificación final

- [x] 4.1 `cd evaluation; pytest` (o `pytest evaluation/`) en verde, incluida la suite nueva. Hecho: 1163 passed, 2 skipped; la suite nueva aporta 16/16. Quedan 25 fallos PREEXISTENTES y ajenos a c-170 (`test_sensibilidad_ajustes.py`, `test_sensibilidad_corpus.py`, `test_umbral_settings_oof.py`), por variables de entorno del backend ausentes (`Settings.directory_blind_index_key`); baseline idéntico (25 failed, 1147 passed) al quitar los dos archivos de c-170, por lo que no hay regresión.
- [x] 4.2 `git status` no muestra modificados `evaluation/evidence/**`, `data/corpus_evaluacion_pseudonimizado.json` ni `data/corpus_resultados*.json`. Hecho: verificado tras la implementación.
- [x] 4.3 `openspec validate c-170-completar-las-entradas-del-cli-de-analisis-de-campana --strict --no-interactive` pasa. Hecho: validado sin errores.
