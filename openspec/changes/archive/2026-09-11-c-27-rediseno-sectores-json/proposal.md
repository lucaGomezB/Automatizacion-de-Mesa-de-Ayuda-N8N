## Why

La taxonomia de sectores vigente (`["Sistemas", "Operaciones", "Soporte Técnico"]`) no refleja la operacion real de la mesa de ayuda y el corpus sintetico de 200 casos que la respaldaba fue descartado por los revisores de tesis. Se necesita una taxonomia de 5 sectores alineada con el dominio, un corpus de evaluacion en JSON con verdad multietiqueta, y persistencia real de los sectores adicionales en el backend.

## What Changes

- **BREAKING** Nuevo vocabulario canonico de sectores (5 strings exactos, case-sensitive, SIN tildes): `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`. `Operaciones` se elimina por completo y `Sistemas` se mantiene como categoria propia. Se invierte la convencion previa "con tildes" para evitar bugs de normalizacion Unicode.
- **BREAKING** Redistribucion real de keywords en `App/Backend/app/classifiers/keywords.py` (no es solo un renombrado: cambia la precision del clasificador determinista y la matriz de confusion de referencia).
- **BREAKING** Migracion del esquema del corpus de CSV a JSON: se elimina `categoria_real` y se agregan `sector_asignado` (string) y `sectores_adicionales` (array de strings, requerido, `[]` cuando no hay). Verdad de referencia multietiqueta.
- Persistencia backend de `sectores_adicionales` mediante una migracion Alembic **nueva (004)** que NO muta `001_seed_catalogs.py`, con tabla de union normalizada para los sectores adicionales del incidente y soporte para los conjuntos predicho/validado del log de clasificacion.
- **BREAKING** Rename del contrato de clasificacion: `categoria` -> `sector_predicho` y agregado de `sectores_adicionales` (predichos) en resultado del clasificador, schemas, servicios, payload del webhook N8N y validador N8N. Rompe ~16 tests de backend y el contrato N8N.
- Rediseno de `evaluation/metrics.py` de single-label estricto a multietiqueta: matriz de confusion primaria 5x5, exactitud primaria, subset accuracy, Hamming loss, micro-F1, macro-F1, tabla one-vs-rest por sector y Wilson CI sobre las dos definiciones de acierto (igualdad estricta y pertenencia).
- Eliminacion permanente del corpus sintetico de 200 casos (generador, datos, tests y artefactos provisionales); el fixture de tests pasa a JSON con las etiquetas nuevas.
- Frontend: dejar de depender de IDs numericos de sector y usar los nombres canonicos (`catalog.ts`, `SectorBadge`, `SectorPieChart`, formulario de reporte).
- Actualizacion de documentacion, knowledge-base, `openspec/config.yaml`, `AGENTS.md`, `CLAUDE.md`, `CHANGES.md`, prompt de Gemini y regeneracion de `docs/openapi.json`.

Fuera de alcance: texto de tesis (`docs/Tesis/**`) y cambios archivados (`openspec/changes/archive/**`).

## Capabilities

### New Capabilities

- `sector-taxonomy`: vocabulario canonico de los 5 sectores (strings exactos sin tildes), reglas de redistribucion de keywords deterministas, prompt/enum/validacion de Gemini y consumo de los nombres canonicos desde el frontend sin IDs numericos.
- `sector-assignment`: contrato multietiqueta de asignacion de sector (`sector_predicho` + `sectores_adicionales`) en resultado del clasificador, schemas de API, servicio y payload del webhook; persistencia normalizada de los sectores adicionales del incidente y de los conjuntos predicho/validado del log de clasificacion mediante la migracion 004.

### Modified Capabilities

- `evaluation-corpus`: el corpus pasa de CSV a JSON, elimina `categoria_real`, agrega `sector_asignado`/`sectores_adicionales`, elimina el requisito de 200 casos sinteticos y las referencias a la Tabla 7.
- `evaluation-framework`: el loader lee JSON, el modelo `Prediccion` se renombra a `sector_asignado`/`sector_predicho` + adicionales, y las metricas pasan a multietiqueta.
- `n8n-workflow`: el validador de categorias acepta los 5 sectores nuevos y el contrato de payload usa `sector_predicho` + `sectores_adicionales`.
- `n8n-notification`: el payload de notificacion a N8N refleja el rename de `categoria` a `sector_predicho` y el agregado de `sectores_adicionales`.
- `dashboard-analytics`: el grafico de distribucion por sector contempla los 5 sectores.
- `foundation-environment`: los catalogos sembrados contienen los 5 sectores canonicos via la migracion 004.
- `project-documentation`: el Anexo F documenta el esquema JSON y las 5 categorias; `docs/openapi.json` se regenera.
- `data-pseudonymization`: los 5 nombres de sector nuevos se agregan a `_EXCLUSION_PERSONA` para que nunca se enmascaren como `[PERSONA]`.

## Impact

- **Backend** (`App/Backend/`): `classifiers/{keywords,gemini_classifier}.py`, `alembic/versions/004_*`, `models/catalog.py` y nuevos modelos de asociacion, `schemas/{clasificacion,catalog,estadisticas}.py`, `services/incidente_service.py`, `utils/n8n_webhook.py`, `utils/pseudonymizer.py`, ~16 archivos de tests.
- **Evaluation** (`evaluation/`): `corpus.py`, `metrics.py`, `run_evaluation.py`, `tests/conftest.py`, `tests/*`, `tests/fixtures/corpus_fixture.*`, `README.md`, `data/README.md`; se eliminan `generate_corpus.py`, `tests/test_corpus_generated.py`, `tests/data/fake_classifier_mappings.py`, `predicciones_provisional.json`, `report_provisional.md`.
- **Frontend** (`App/Frontend/`): `src/types/catalog.ts`, `components/shared/SectorBadge.tsx`, `pages/Dashboard/SectorPieChart.tsx`, `pages/ReportarIncidente/{IncidenteForm.tsx,index.tsx}` y sus tests.
- **Orquestacion**: `n8n/workflow.json` (validador y contrato).
- **Datos/raiz**: se eliminan `data/corpus_sintetico_provisional.csv`, `scripts/gen_corpus.py`, `scripts/run_provisional.py`; se actualizan `data/README.md` y `evaluation/data/README.md`. La ruta del corpus real pasa a JSON (`data/corpus_evaluacion_pseudonimizado.json`, gitignored/ausente).
- **CI**: bloque `evaluation` de `.github/workflows/ci.yml` deja de depender del corpus sintetico y usa el fixture JSON.
- **Docs/config**: `docs/{anexo_f_corpus,como_cargar_datos_corpus,anexo_h_prompt_gemini,parameters_gemini,pseudonymization,anexo_c_esquema_bd,n8n-workflow-guide}.md`, `docs/prompt_gemini.txt`, `docs/openapi.json`, `knowledge-base/{01,03,04,05,06,11}.md`, `openspec/config.yaml`, `AGENTS.md`, `CLAUDE.md`, `CHANGES.md`.
- **Gobernanza**: ALTA/CRITICA (strings de dominio + migracion de base de datos); requiere aprobacion humana explicita antes de apply.
- **Metricas superadas**: la distribucion 82/64/54, la exactitud 92%, el F1 macro ~0.919 y la Tabla 7 del corpus sintetico de 3 categorias quedan invalidadas y no deben citarse como evidencia.
