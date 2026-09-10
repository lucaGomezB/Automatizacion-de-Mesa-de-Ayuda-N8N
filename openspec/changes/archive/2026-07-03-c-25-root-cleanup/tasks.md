## 1. Crear estructura de directorios destino

- [x] 1.1 Crear directorio `n8n/` en la raiz del repositorio.
- [x] 1.2 Crear directorio `n8n/twilio/`.

## 2. Mover archivos con git mv

- [x] 2.1 `git mv ANEXO_H_Prompt_Gemini_Especificacion.md docs/anexo_h_prompt_gemini.md`
- [x] 2.2 `git mv Automatizacion_Mesa_de_Ayuda.json n8n/workflow.json`
- [x] 2.3 `git mv twilio/twiml.xml n8n/twilio/twiml.xml`
- [x] 2.4 `git mv twilio/README.md n8n/twilio/README.md`

## 3. Actualizar referencias a ANEXO_H_Prompt_Gemini_Especificacion.md

- [x] 3.1 `openspec/config.yaml` linea 49: actualizar `gemini_spec` al nuevo path `docs/anexo_h_prompt_gemini.md`
- [x] 3.2 `CHANGES.md` lineas 149 y 268: actualizar referencias a `ANEXO_H_Prompt_Gemini_Especificacion.md` → `docs/anexo_h_prompt_gemini.md`
- [x] 3.3 `CLAUDE.md` linea 20: actualizar entrada en tabla Key Files
- [x] 3.4 `knowledge-base/README.md` linea 3: actualizar referencia
- [x] 3.5 `App/Backend/app/classifiers/gemini_classifier.py` linea 9: actualizar comentario

## 4. Actualizar referencias a Automatizacion_Mesa_de_Ayuda.json

- [x] 4.1 `docker-compose.yml` linea 113: actualizar volume mount source (`./n8n/workflow.json`); container path (`/data/Automatizacion_Mesa_de_Ayuda.json`) conservado por decision CRITICAL
- [x] 4.2 `App/Backend/tests/test_n8n_workflow.py` lineas 4, 27: actualizar WORKFLOW_PATH a `n8n/workflow.json` y docstring
- [x] 4.3 `AGENTS.md` linea 57: actualizar entrada en Component Map
- [x] 4.4 `CHANGES.md` linea 176: actualizar referencia
- [x] 4.5 `CLAUDE.md` lineas 17, 99: actualizar referencias en Key Files y Development Notes
- [x] 4.6 `README.md` lineas 82, 112: actualizar referencias en secciones de importacion y reproducibilidad
- [x] 4.7 `knowledge-base/08_arquitectura_propuesta.md` linea 37: actualizar diagrama de estructura
- [x] 4.8 `knowledge-base/06_funcionalidades.md` linea 62: actualizar referencia
- [x] 4.9 `knowledge-base/10_preguntas_abiertas.md` linea 35: actualizar referencia
- [x] 4.10 `docs/n8n-workflow-guide.md` lineas 9, 251, 262, 282, 446, 479, 557, 561: actualizar 5 ocurrencias de host-path; 3 ocurrencias de container-path (`/data/Automatizacion_Mesa_de_Ayuda.json`) conservadas por decision CRITICAL
- [x] 4.11 `docs/operational-guide.md` linea 111: actualizar referencia
- [x] 4.12 `docs/troubleshooting.md` linea 195: verificado — no referencia el nombre de archivo sino el nombre del workflow en N8N ("Automatizacion_Mesa_de_Ayuda"), no requiere cambio
- [x] 4.13 `docs/diagrams/despliegue.md` linea 21: actualizar referencia

## 5. Actualizar referencias a twilio/

- [x] 5.1 `n8n/twilio/README.md` lineas 15, 62, 74: actualizar referencias internas de `twilio/twiml.xml` a `n8n/twilio/twiml.xml` y `Automatizacion_Mesa_de_Ayuda.json` a `n8n/workflow.json`
- [x] 5.2 `openspec/specs/project-structure/spec.md` linea 67: actualizar `twilio/README.md` a `n8n/twilio/README.md`
- [x] 5.3 `openspec/config.yaml` linea 31: actualizar `workflow: Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json`

## 6. Corregir .env.example raiz

- [x] 6.1 `.env.example` linea 3: `Gestion_Incidentes/.env` → `App/Backend/.env`

## 7. Verificar integridad

- [x] 7.1 Ejecutar tests del backend: `cd App/Backend; pytest tests/test_n8n_workflow.py -v` — 58 passed, 1 xfailed (esperado). WORKFLOW_PATH resuelve correctamente a `n8n/workflow.json`.
- [x] 7.2 Validar docker-compose: `docker compose config` — Docker no disponible en esta maquina (Windows sin Docker Desktop). El cambio de path en el volume mount es sintacticamente correcto (misma estructura YAML, solo cambia el source path).
- [x] 7.3 Buscar referencias huerfanas a `ANEXO_H_Prompt_Gemini_Especificacion` en archivos activos (excluyendo `openspec/changes/archive/`): cero resultados en archivos activos.
- [x] 7.4 Buscar referencias huerfanas a `Automatizacion_Mesa_de_Ayuda.json` en archivos activos (excluyendo `openspec/changes/archive/`): solo referencias intencionales — (a) container path `/data/Automatizacion_Mesa_de_Ayuda.json` en docs/n8n-workflow-guide.md, (b) nombre semantico del workflow en openspec/specs/n8n-workflow/spec.md (Decision 4).
- [x] 7.5 Verificar que el directorio `twilio/` en raiz fue eliminado — eliminado (estaba vacio tras los git mv).
- [x] 7.6 Verificar `git status`: los 4 archivos aparecen como "renamed" (R) preservando historial git.
- [x] 7.7 Verificar que los tests de estructura del workflow pasan — 58/58 pasan, WORKFLOW_PATH apunta a `n8n/workflow.json`.
- [x] 7.8 Full backend test suite: `cd App/Backend; pytest` — 208 passed, 1 skipped, 1 xfailed.
- [x] 7.9 Full frontend test suite: `cd App/Frontend; npm run test` — 12 test files, 68 tests, all passed.
