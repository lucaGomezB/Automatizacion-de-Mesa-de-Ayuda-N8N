# Tasks: Completar las entradas del CLI de análisis de campaña

> Helper puro + docs. TDD estricto, offline (sin red ni Gemini). No se modifica
> `evaluation/analisis_campana.py` (c-167), los changes archivados c-165..c-168, c-169, ni
> `App/**` / `n8n/**`.

## 1. Módulo y tests (TDD estricto, offline)

- [ ] 1.1 RED: en `evaluation/tests/test_preparar_entradas_analisis.py` escribir `test_union_escribe_encabezado_c1_unico` que, con `doble_etiquetado.csv` y `brazo_manual.csv` sintéticos en `tmp_path`, llama al helper y exige un único encabezado C1 (`id_caso,id_etiquetador,tarea,sector_etiquetado,sectores_adicionales_etiquetados,inicio,timestamp`) seguido de las filas de ambas tareas; verificar que falla porque el módulo no existe
- [ ] 1.2 GREEN: crear `evaluation/preparar_entradas_analisis.py` con la función pura de unión (stdlib + `COLUMNAS_C1` de `evaluation/doble_etiquetado.py`) y verificar 1.1 en verde
- [ ] 1.3 RED/GREEN triangular: `test_valida_por_tarea_y_aborta` con una fila inválida de `brazo_manual` (nombra archivo y `tarea`, no escribe) y `test_falta_fuente_aborta` (nombra el archivo faltante); implementar reutilizando `validar_doble_etiquetado` y verificar en verde
- [ ] 1.4 RED/GREEN triangular: `test_reproducibilidad_byte_a_byte` (dos corridas → mismo contenido y SHA-256) y `test_salida_lf_sin_bom`; verificar en verde
- [ ] 1.5 RED/GREEN: `test_copia_in_sample_byte_a_byte` exige que `predicciones_in_sample.json` tenga exactamente los bytes de la fuente congelada y que la fuente quede intacta; implementar el paso de staging y verificar en verde
- [ ] 1.6 RED/GREEN: `test_rechaza_destino_congelado` verifica que el helper aborta con error accionable vía `es_archivo_congelado` de `evaluation/plan_campana.py` si el destino es un artefacto congelado; verificar en verde
- [ ] 1.7 GREEN: `main()` del CLI imprime el SHA-256 de cada salida y su procedencia (fuente y hash de la fuente), y devuelve `0`; test que lo verifica
- [ ] 1.8 REFACTOR: extraer constantes de nombres/rutas, mejorar nombres y quitar duplicación sin cambiar comportamiento; `pytest evaluation/tests/test_preparar_entradas_analisis.py -v` sigue en verde
- [ ] 1.9 Verificación de la suite del módulo: `cd evaluation; pytest tests/test_preparar_entradas_analisis.py -v` en verde, sin conexiones externas (solo fixtures sintéticos)

## 2. Documentación y runbooks

- [ ] 2.1 `docs/campana-medicion/runbook-doble-etiquetado.md`: agregar en la sección 7 el paso que ejecuta `evaluation/preparar_entradas_analisis.py` para unir `doble_etiquetado.csv` + `brazo_manual.csv` en `plantilla_etiquetado.csv`; verificar que la sección nombra el comando
- [ ] 2.2 `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`: agregar en la sección 4.3 el mismo paso de ensamblado y la copia in-sample; verificar con `grep -n "preparar_entradas_analisis" <runbook>`
- [ ] 2.3 `evaluation/data/campana/README.md`: agregar `plantilla_etiquetado.csv` y `predicciones_in_sample.json` a la tabla SHA-256 (valor `pendiente` hasta versionar) y su procedencia (fuente de cada uno); verificar que ambas filas existen
- [ ] 2.4 `evaluation/data/campana/analisis/README.md`: aclarar en "Entradas esperadas" que `plantilla_etiquetado.csv` y `predicciones_in_sample.json` las produce `evaluation/preparar_entradas_analisis.py`; verificar con `grep -n`
- [ ] 2.5 `evaluation/data/README.md`: anotar en la sección "`plantilla_etiquetado.csv` y `campana/` (c-168)" que la hoja unificada de `campana/` la produce el helper; verificar con `grep -n`
- [ ] 2.6 Documentar en `design.md` (o en el README de la campaña) la recomendación de enmendar el gate de c-169 (task 0.2) para exigir las dos entradas nuevas; NO editar c-169

## 3. Registro de procedencia de las entradas (se completa al versionar la campaña)

- [ ] 3.1 Ejecutar `python -m evaluation.preparar_entradas_analisis` sobre las fuentes reales una vez corridas la campaña y el brazo manual; verificar que imprime el SHA-256 de `plantilla_etiquetado.csv` y completarlo en el README de la campaña
- [ ] 3.2 Verificar que el SHA-256 de `predicciones_in_sample.json` coincide con el de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` y registrarlo en el README de la campaña

## 4. Verificación final

- [ ] 4.1 `cd evaluation; pytest` (o `pytest evaluation/`) en verde, incluida la suite nueva
- [ ] 4.2 `git status` no muestra modificados `evaluation/evidence/**`, `data/corpus_evaluacion_pseudonimizado.json` ni `data/corpus_resultados*.json`
- [ ] 4.3 `openspec validate c-170-completar-las-entradas-del-cli-de-analisis-de-campana --strict --no-interactive` pasa
