# Tasks: Contrabalanceo del diseno y corpus independiente

## 1. Funcion pura de orden (TDD)

- [ ] 1.1 Escribir tests en `scripts/corpus_ingest/test_ingest_via_n8n.py` para `ordenar_casos(casos, modo, seed)` (RED): directo, inverso, alternado, aleatorio. Verificacion: tests fallan por funcion inexistente.
- [ ] 1.2 Implementar `ordenar_casos` en `ingest_via_n8n.py` (GREEN): `directo` preserva, `inverso` invierte, `alternado` intercala mitades (regla para N impar documentada), `aleatorio` usa `random.Random(seed)`. Verificacion: tests en verde.
- [ ] 1.3 Triangular: caso N impar en `alternado` y reproducibilidad de `aleatorio` con la misma semilla. Verificacion: nuevos tests en verde.
- [ ] 1.4 `aleatorio` sin `--seed` produce error accionable (test RED+GREEN). Verificacion: test de error en verde.

## 2. CLI y sidecar en los tres harnesses

- [ ] 2.1 Agregar `--orden` (choices) y `--seed` a `parse_args` de `ingest_via_n8n.py`, aplicando `ordenar_casos` tras `select_cases`. Verificacion: test de CLI verifica el orden de procesamiento.
- [ ] 2.2 Agregar el campo `orden: str | None` a `CaseResult` y poblarlo en la corrida. Verificacion: `write_sidecar_json` expone `orden` por caso (test).
- [ ] 2.3 Test de compatibilidad: un sidecar previo sin `orden` se mergea sin errores. Verificacion: test en verde.
- [ ] 2.4 Replicar `--orden`/`--seed` + campo sidecar en `ingest_corpus.py` (CLI :485-503) con sus tests. Verificacion: tests de `test_ingest_corpus.py` en verde.
- [ ] 2.5 Replicar `--orden`/`--seed` + campo sidecar en `ingest_telefonia_corpus.py` (CLI :260-287) con sus tests. Verificacion: tests de `test_ingest_telefonia_corpus.py` en verde.
- [ ] 2.6 Ejecutar `pytest scripts/corpus_ingest/test_ingest_via_n8n.py test_ingest_corpus.py test_ingest_telefonia_corpus.py` (offline). Verificacion: suite en verde.

## 3. Runbook de campana contrabalanceada

- [ ] 3.1 Crear `docs/runbook-campana-contrabalanceada.md` definiendo reparto en mitades/brazos y el orden asignado a cada uno. Verificacion: artifact existe y cubre el reparto.
- [ ] 3.2 Documentar la estimacion del efecto de orden (primera vs segunda mitad y/o termino de orden) y su criterio de aceptacion. Verificacion: artifact cubre el procedimiento y el criterio.

## 4. Corpus independiente y no solape (TDD)

- [ ] 4.1 Escribir tests (RED) para `verificar_no_solape(ajuste, candidato)` que falla ante id o descripcion normalizada compartida. Verificacion: tests fallan por funcion inexistente.
- [ ] 4.2 Implementar `verificar_no_solape` (GREEN) con error accionable que identifica el caso infractor. Verificacion: tests en verde.
- [ ] 4.3 Triangular: "mismo caso con distinto id pero misma descripcion" bloquea; corpus disjunto pasa. Verificacion: tests en verde.
- [ ] 4.4 Exponer la verificacion como paso previo obligatorio en la ruta de harness para corpus independiente. Verificacion: test de integracion del paso en verde.
- [ ] 4.5 Crear `docs/runbook-corpus-independiente.md`: requisito de no solape con los 200 casos, misma pseudonimizacion y doble etiquetado. Verificacion: artifact existe y cubre ambos requisitos.

## 5. Reporte out-of-sample

- [ ] 5.1 Tests (RED) de que el reporte etiqueta bloques `in-sample`/`out-of-sample` y rechaza agregados mixtos. Verificacion: tests fallan por funcion inexistente.
- [ ] 5.2 Implementar el reporte con etiquetado de origen y metrica por ambas etapas sobre el corpus independiente (GREEN). Verificacion: tests en verde.

## 6. Validacion y cierre

- [ ] 6.1 Ejecutar `openspec validate "c-166-contrabalanceo-del-diseno-y-corpus-independiente" --strict --no-interactive`. Verificacion: validacion en verde.
- [ ] 6.2 Marcar tareas y confirmar que no se toco `docs/Tesis/v9 (IA)/`, strings de categorias ni numeros canonicos. Verificacion: `git diff --stat` sin esos paths.
