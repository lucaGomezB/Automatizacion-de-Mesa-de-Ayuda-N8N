# Tasks — c-27-rediseno-sectores-json

Modo Strict TDD: en cada capa se escribe primero el test que describe el comportamiento (RED), luego la implementacion minima (GREEN) y, cuando el spec define varios escenarios, se triangula con casos adicionales antes de refactorizar. Las tareas de red de seguridad se ejecutan antes de modificar archivos existentes.

## 1. Red de seguridad y vocabulario canonico

- [x] 1.1 Activar el hook (`git config core.hooksPath .githooks`) y capturar el baseline de las tres suites: `cd App/Backend; pytest`, `cd App/Frontend; npm run test`, `cd evaluation; pytest`. Registrar el conteo de tests en verde; si hay fallos preexistentes, reportarlos y NO corregirlos en este cambio.
- [x] 1.2 RED: crear `App/Backend/tests/test_sector_vocabulary.py` con tests que exijan exactamente los cinco strings canonicos sin tildes, que `Operaciones` no pertenezca al conjunto y que las variantes con tilde o casing distinto se rechacen. Verificar que fallan.
- [x] 1.3 GREEN: crear la constante canonica del backend (p. ej. `App/Backend/app/constants.py` con `SECTORES_CANONICOS`) y hacerla consumir por el vocabulario del backend. Verificar que `pytest tests/test_sector_vocabulary.py` pasa.
- [x] 1.4 TRIANGULAR: agregar casos para cada uno de los cinco sectores y un caso de string vacio/desconocido. Verificar que los tests siguen en verde.
- [x] 1.5 RED: en `evaluation/tests/test_corpus.py`, test que exija que el conjunto canonico de evaluacion coincida exactamente con el del backend. Verificar que falla.
- [x] 1.6 GREEN: actualizar `evaluation/corpus.py` (`CATEGORIAS_VALIDAS`) al conjunto canonico y verificar que el test pasa. Marcar los tests que referencian la taxonomia previa para su actualizacion en la capa 7.

## 2. Backend: migracion 004 y persistencia relacional (GOBERNANZA ALTA/CRITICA)

- [x] 2.1 RED: escribir tests de la migracion (p. ej. `App/Backend/tests/test_migration_sectores.py`) que exijan: `alembic upgrade head` siembra los cinco sectores, `Operaciones` no existe, las tablas de union existen, `001_seed_catalogs.py` no fue modificada (hash igual) y `downgrade` deja el esquema consistente. Verificar que fallan.
- [x] 2.2 GREEN: crear `App/Backend/alembic/versions/004_*.py` que cree las tablas de union, ponga en NULL y elimine las filas `Operaciones`/`Soporte Técnico`, y haga upsert de los cinco sectores canonicos. Verificar los tests de 2.1 con PostgreSQL local; si no hay PostgreSQL, marcar como integracion y ejecutar en CI.
- [x] 2.3 RED: test de modelos ORM de las tablas de union (FK a `incidente` con `CASCADE`, FK a `sector`, unicidad que impida duplicar el mismo sector adicional en un incidente). Verificar que falla.
- [x] 2.4 GREEN: implementar los modelos de asociacion en `App/Backend/app/models/` y verificar que los tests pasan.
- [x] 2.5 TRIANGULAR: test de integridad referencial (sector inexistente rechazado) y de cascada al eliminar el incidente. Verificar en verde.
- [x] 2.6 Ejecutar `alembic upgrade head` y luego `alembic downgrade 001` y re-upgrade sobre una base local; documentar el resultado y verificar que no quedan residuos.

## 3. Clasificadores

- [x] 3.1 RED: en `App/Backend/tests/test_deterministic_classifier.py`, escribir tests que exijan que los cinco sectores tengan terminos, que un termino de hardware clasifique como `Soporte Tecnico Hardware` y que ninguna prediccion sea `Operaciones`. Verificar que fallan.
- [x] 3.2 GREEN: redistribuir `App/Backend/app/classifiers/keywords.py` en los cinco sectores canonicos y eliminar `Operaciones`; verificar los tests.
- [x] 3.3 TRIANGULAR: agregar al menos un caso por sector y un caso de termino ambiguo; verificar en verde.
- [x] 3.4 RED: actualizar `App/Backend/tests/test_gemini_validation.py` y `test_gemini_casing_fix.py` para exigir los cinco sectores en el prompt, el enum y la validacion. Verificar que fallan.
- [x] 3.5 GREEN: actualizar `App/Backend/app/classifiers/gemini_classifier.py` (prompt embebido, `_VALID_CATEGORIES`, `response_schema` enum) y `docs/prompt_gemini.txt`; verificar los tests.
- [x] 3.6 RED: en `App/Backend/tests/test_pseudonymizer.py`, test que exija que los cinco nombres canonicos NO se reemplacen por `[PERSONA]`. Verificar que falla.
- [x] 3.7 GREEN: agregar los cinco nombres a `_EXCLUSION_PERSONA` en `App/Backend/app/utils/pseudonymizer.py`; verificar el test.
- [x] 3.8 REFACTOR: dejar `keywords.py` y `gemini_classifier.py` consumiendo la constante canonica de 1.3; verificar que la suite de clasificadores sigue en verde.

## 4. API, servicios y webhook

- [x] 4.1 RED: test que exija que `ClasificacionResult` y los schemas expongan `sector_predicho` + `sectores_adicionales` y NO `categoria`. Verificar que falla.
- [x] 4.2 GREEN: actualizar `App/Backend/app/schemas/clasificacion.py` y el resultado del clasificador; verificar.
- [x] 4.3 RED: test de servicio que exija persistir el sector principal y N sectores adicionales del incidente, y los conjuntos predicho/validado del log. Verificar que falla.
- [x] 4.4 GREEN: actualizar `App/Backend/app/services/incidente_service.py` y repositorios para persistir los sectores adicionales; verificar.
- [x] 4.5 RED: test que exija que el payload de `App/Backend/app/utils/n8n_webhook.py` use `sector_predicho`/`sectores_adicionales` sin `categoria`. Verificar que falla.
- [x] 4.6 GREEN: actualizar `n8n_webhook.py`; verificar.
- [x] 4.7 RED: test del schema de validacion humana con sector por nombre y capaz de aceptar sectores adicionales validados. Verificar que falla.
- [x] 4.8 GREEN: actualizar el schema/endpoint de validacion y su test; verificar.
- [x] 4.9 Red de seguridad: actualizar los ~16 tests de backend que referencian los strings o el contrato viejos (`test_api_clasificaciones.py`, `test_api_incidentes.py`, `test_api_estadisticas.py`, `test_api_validar_cascade.py`, `test_hybrid_classifier.py`, `test_incidente_notify_n8n.py`, `test_pseudonymization_integration.py`, `test_schemas_pseudonimizacion.py`, `test_integration_postgresql.py`, `tests/conftest.py`) y verificar que la suite completa pasa.
- [x] 4.10 REFACTOR: eliminar duplicacion de listas de sectores en schemas/servicio; verificar suite en verde.

## 5. Workflow N8N

- [x] 5.1 RED: actualizar `App/Backend/tests/test_n8n_workflow.py` para exigir el validador con los cinco sectores y los campos `sector_predicho`/`sectores_adicionales` en el contrato. Verificar que falla.
- [x] 5.2 GREEN: actualizar el nodo validador de `n8n/workflow.json` (set canonico de cinco sectores, campos nuevos) y el prompt del AI Agent si enumera categorias; verificar el test.
- [x] 5.3 TRIANGULAR: test que rechace `Operaciones` y variantes con tilde en el validador; verificar en verde.
- [x] 5.4 Actualizar `docs/n8n-workflow-guide.md` con el contrato nuevo y verificar que el test estructural sigue pasando.

## 6. Frontend

- [x] 6.1 RED: test que exija que las opciones de sector se deriven de los nombres canonicos y NO de IDs numericos fijos; en paralelo, test del endpoint `GET /api/v1/catalogos/sectores` en el backend. Verificar que fallan.
- [x] 6.2 GREEN: agregar el endpoint de catalogo en el backend y actualizar `App/Frontend/src/types/catalog.ts` para consumirlo; verificar ambos tests.
- [x] 6.3 RED: actualizar `SectorBadge.test.tsx` y `SectorPieChart.test.tsx` para los cinco sectores y un nombre desconocido. Verificar que fallan.
- [x] 6.4 GREEN: actualizar `App/Frontend/src/components/shared/SectorBadge.tsx` y `App/Frontend/src/pages/Dashboard/SectorPieChart.tsx`; verificar.
- [x] 6.5 RED: actualizar `IncidenteForm.test.tsx` y el test de `pages/ReportarIncidente/index.tsx` para cinco opciones sin IDs fijos. Verificar que fallan.
- [x] 6.6 GREEN: actualizar `IncidenteForm.tsx` y `pages/ReportarIncidente/index.tsx`; verificar.
- [x] 6.7 Red de seguridad: actualizar los tests de frontend que usan nombres viejos (`useEstadisticas`, `useIncidentes`, `useReportarIncidente`, `RevisionHumanaTable`, `TicketsTable`, `Dashboard`, `TendenciaChart`, `SuccessCard`, `clasificacionesService`, `estadisticasService`, `incidentesService`) y ejecutar `cd App/Frontend; npm run test`.
- [x] 6.8 REFACTOR: quitar `SECTOR_IDS` y cualquier acoplamiento a IDs numericos; ejecutar `npm run lint` y `npm run test`.

## 7. Evaluacion: corpus JSON y metricas multietiqueta

- [x] 7.1 Red de seguridad: capturar el baseline de `cd evaluation; pytest` y confirmar que `evaluation/tests/test_stats.py` no depende de categorias.
- [x] 7.2 RED: reescribir `evaluation/tests/test_corpus.py` para el loader JSON: estructura `schema_version`/`metadata`/`casos`, campos requeridos, invariantes (adicionales requeridos, sin repetir el asignado, valores canonicos). Verificar que falla.
- [x] 7.3 GREEN: reescribir `evaluation/corpus.py` (dataclass `CasoEvaluacion` con `sector_asignado`/`sectores_adicionales`, lectura JSON, validaciones); verificar.
- [x] 7.4 TRIANGULAR: casos de campo faltante, sector invalido, sector repetido, `sectores_adicionales: []` y `total_casos` desincronizado (debe normalizarse, no rechazarse); verificar en verde.
- [x] 7.5 RED: reescribir `evaluation/tests/test_metrics.py` para las metricas multietiqueta: matriz primaria 5x5, exactitud primaria, subset accuracy, Hamming loss, micro-F1, macro-F1, tabla one-vs-rest y Wilson en las dos definiciones de acierto. Verificar que falla.
- [x] 7.6 GREEN: reescribir `evaluation/metrics.py` con las definiciones del design (D5); verificar.
- [x] 7.7 TRIANGULAR: casos de coincidencia perfecta, solapamiento parcial y disjuntos; verificar Jaccard y Hamming.
- [x] 7.8 RED: actualizar `evaluation/tests/test_run_evaluation.py` para `Prediccion` con `sector_asignado`/`sector_predicho`/`sectores_adicionales` y la ruta JSON. Verificar que falla.
- [x] 7.9 GREEN: actualizar `evaluation/run_evaluation.py`; verificar.
- [x] 7.10 Migrar `evaluation/tests/fixtures/corpus_fixture.csv` a `evaluation/tests/fixtures/corpus_fixture.json` con las etiquetas canonicas y `sectores_adicionales`; verificar que los tests lo cargan.
- [x] 7.11 Eliminar permanentemente `evaluation/data/corpus_evaluacion.csv`, `evaluation/generate_corpus.py`, `evaluation/tests/test_corpus_generated.py`, `evaluation/tests/data/fake_classifier_mappings.py`, `data/corpus_sintetico_provisional.csv`, `scripts/gen_corpus.py`, `scripts/run_provisional.py`, `evaluation/predicciones_provisional.json` y `evaluation/report_provisional.md`. Verificar que no existen.
- [x] 7.12 Refactorizar `evaluation/tests/conftest.py` para quitar `CALIBRATED_CORPUS_PATH` y el `FakeClassifier` calibrado, dejando el fixture JSON como unica fuente. Verificar que no quedan referencias al corpus sintetico.
- [x] 7.13 Actualizar el bloque `evaluation` de `.github/workflows/ci.yml` para usar el fixture JSON y verificar el comando localmente. Ejecutar `cd evaluation; pytest`.
- [x] 7.14 RED: test del loader que exija error claro (con ruta y motivo) ante JSON malformado, y que `total_casos` desincronizado se NORMALICE a `len(casos)` y se PERSISTA en disco antes de validar/usar el corpus. Verificar que falla.
- [x] 7.15 GREEN: implementar en `evaluation/corpus.py` la validacion de JSON malformado y la normalizacion persistente e idempotente de `total_casos`; verificar en verde.

## 8. Documentacion, config y OpenAPI

- [x] 8.1 Actualizar `openspec/config.yaml` (categorias) y `AGENTS.md` (regla de category strings), `CLAUDE.md` y `CHANGES.md`; verificar que no queda `Operaciones` ni la lista de 3 sectores.
- [x] 8.2 Actualizar `knowledge-base/{01_vision_y_objetivos,03_actores_y_roles,04_modelo_de_datos,05_reglas_de_negocio,06_funcionalidades,11_evaluacion_experimental}.md`; verificar que el vocabulario coincide con la constante canonica.
- [x] 8.3 Actualizar `docs/{anexo_f_corpus,como_cargar_datos_corpus,anexo_h_prompt_gemini,parameters_gemini,pseudonymization,anexo_c_esquema_bd,n8n-workflow-guide}.md` y `docs/prompt_gemini.txt`; verificar que el Anexo F describe el esquema JSON y las 5 categorias y que `prompt_gemini.txt` no menciona `Operaciones`.
- [x] 8.4 Regenerar `docs/openapi.json` con el comando del proyecto y verificar `cd App/Backend; pytest tests/test_openapi_sync.py -v`.
- [x] 8.5 Actualizar `evaluation/README.md`, `evaluation/data/README.md` y `data/README.md` al corpus JSON y al corpus sintetico eliminado; verificar que no quedan referencias a CSV ni a 200 casos.
- [x] 8.6 Verificar que `.gitignore` cubre `data/corpus_evaluacion_pseudonimizado.json` y `.csv` (PII, Ley 25.326) y que `git check-ignore` los confirma.

## 9. Verificacion final

- [x] 9.1 Ejecutar `cd App/Backend; pytest` y verificar que toda la suite pasa (o que los unicos fallos son los preexistentes reportados en 1.1).
- [x] 9.2 Ejecutar `cd App/Frontend; npm run test` y `npm run lint`; verificar en verde.
- [x] 9.3 Ejecutar `cd evaluation; pytest` y verificar en verde.
- [x] 9.4 Ejecutar `openspec validate c-27-rediseno-sectores-json --strict` y verificar que pasa.
- [x] 9.5 Ejecutar `git status` y verificar que NO se modifico ningun archivo bajo `openspec/changes/archive/**` ni bajo `docs/Tesis/**`.
