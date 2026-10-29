## Context

Ver `proposal.md` (Why). Estado actual verificado:

- Los tres harnesses (`scripts/corpus_ingest/ingest_via_n8n.py`, `ingest_corpus.py`, `ingest_telefonia_corpus.py`) NO tienen soporte de orden/brazo: `rg 'counterbal|contrabal|orden|order|shuffle|random' scripts/corpus_ingest/*.py` no devuelve nada.
- `ingest_via_n8n.py`: CLI en `parse_args` (:1145-1167), `select_cases` (:575) filtra por canal y aplica `limit` preservando el orden del corpus; `CaseResult` (:519-528) es el contrato del sidecar; `write_sidecar_json` (:728) serializa `asdict(result)` mergeando por `case_id`.
- `evaluation/deterministic_measurement.py` solo hace cross-fitting WITHIN-corpus para tau (`asignar_folds` :304-317, `calibrar_out_of_fold` :335, `calibrar_comparativo_out_of_fold` :543); NO cubre vocabulario/prompt ni validacion out-of-sample.
- `openspec/changes/archive/2026-10-23-c-144-...` declara la ausencia de corpus de preproduccion.
- Coordinacion: c-165 introduce `evaluation-campaign-instrumentation` (ECM-001..003) como delta aun no archivado; c-166 AGREGA ECM-004..007 a la misma capability. Al archivar ambos, el main spec resultante contiene ECM-001..007. c-165 debe archivar primero.

## Goals / Non-Goals

**Goals:**
- Orden de procesamiento determinista y reproducible, registrado por caso, sin acoplar a servicios externos.
- Protocolo (runbook) ejecutable que haga estimable el efecto de orden.
- Ruta de harness + verificacion de no solape para un corpus independiente y reporte out-of-sample separado.

**Non-Goals:**
- Ejecutar la campana de campo o recolectar datos (c-169 documenta resultados).
- Reemplazar el cross-fitting within-corpus de tau (se conserva).
- Cambiar contratos de `corpus-n8n-ingest`, strings de categorias o numeros canonicos.

## Decisions

- **Orden como funcion pura**: nueva `ordenar_casos(casos, modo, seed)` que recibe y devuelve `list[Case]`; se compone con `select_cases`. Motivo: testeable en TDD sin I/O. Alternativa descartada: ordenar durante el envio (entrelaza orden y red, no testeable).
- **Modos y semilla**: `directo` (default, preserva conducta), `inverso` (`reversed`), `alternado` (mitad 1 y mitad 2 intercaladas: 1, n/2+1, 2, n/2+2, ...), `aleatorio` (`random.Random(seed).shuffle`). `--seed` obligatorio en `aleatorio`; error accionable si falta. Alternativa descartada: `shuffle` global (no reproducible).
- **Registro por caso**: agregar `orden: str | None` a `CaseResult`; `write_sidecar_json` lo serializa automaticamente via `asdict` (campo aditivo NULL-able). Motivo: trazabilidad por caso sin tocar el merge existente. Alternativa descartada: archivo de orden separado (rompe la unidad de trazabilidad).
- **Efecto de orden**: el runbook lo estima comparando primera vs segunda mitad del corpus (mismo caso, distinto orden entre mitades) y opcionalmente ajustando un termino de orden; se documenta el criterio de aceptacion. No se implementa un modelo estadistico en repo.
- **Corpus independiente**: `verificar_no_solape(corpus_ajuste, corpus_candidato)` compara ids y hashes de descripcion (normalizadas) y falla con el caso infractor. Motivo: "mismo caso en otro id" no debe pasar como out-of-sample. Alternativa descartada: confiar solo en el id (un caso re-etiquetado con nuevo id solaparia).
- **Reporte**: el reporte etiqueta cada bloque como `in-sample`/`out-of-sample`; prohibe agregados mixtos. Se apoya en el pipeline de metricas de clasificacion existente sin cambiar su contrato.

## Risks / Trade-offs

- Orden correlacionado con canal/brazo → el runbook exige contrabalancear por mitad y registrar `orden` por caso para diagnosticar.
- `alternado` ambiguo para N impar → regla documentada (el caso medio va a la segunda mitad).
- Campo nuevo en sidecar → aditivo y NULL-able; test de compatibilidad con sidecar previo.
- Verificacion de no solape con descripciones pseudonimizadas → usa la descripcion pseudonimizada versionada; el hash normaliza espacios/case.

## Migration Plan

Aditivo y retrocompatible: default `directo` no altera corridas ni sidecars previos. Rollback: quitar `--orden`/`--seed` y el campo `orden`; los consumidores ignoran claves desconocidas. No hay migracion de datos.

## Open Questions

- Nombre final del archivo runbook (`docs/runbook-campana-contrabalanceada.md` vs uno combinado con el de corpus independiente): se decide al implementar; no altera specs ni tasks.
