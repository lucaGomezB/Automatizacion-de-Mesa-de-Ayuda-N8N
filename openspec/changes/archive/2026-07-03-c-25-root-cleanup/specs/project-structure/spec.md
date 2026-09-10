## MODIFIED Requirements

### Requirement: Documentacion del proyecto actualizada

Los archivos `AGENTS.md`, `CHANGES.md`, `README.md`, `knowledge-base/`, `n8n/twilio/README.md`, y `scripts/run_provisional.py` SHALL referenciar las nuevas rutas `App/Backend/` y `App/Frontend/` en lugar de `Gestion_Incidentes/` y `Frontend/` respectivamente. Las secciones de comandos de desarrollo SHALL actualizar sus prefijos `cd`.

#### Scenario: AGENTS.md muestra los nuevos paths

- **WHEN** se lee la seccion "Component Map" de `AGENTS.md`
- **THEN** `├── Gestion_Incidentes/` fue reemplazado por `├── App/Backend/` y `├── Frontend/` por `├── App/Frontend/`

#### Scenario: README.md tiene comandos actualizados

- **WHEN** se lee `README.md`
- **THEN** los comandos de configuracion referencian `App/Backend/.env` en lugar de `Gestion_Incidentes/.env`

## ADDED Requirements

### Requirement: Directorio n8n/ para artefactos de orquestacion

El repositorio SHALL contener un directorio `n8n/` en la raiz que agrupe todos los artefactos relacionados con la orquestacion N8N. El workflow principal SHALL residir en `n8n/workflow.json`. Los artefactos de integracion Twilio (TwiML script y documentacion) SHALL residir en `n8n/twilio/`.

#### Scenario: Workflow N8N bajo n8n/

- **WHEN** se inspecciona el directorio `n8n/`
- **THEN** contiene `workflow.json` (el workflow N8N exportado) y `twilio/twiml.xml` con `twilio/README.md`

#### Scenario: docker-compose monta el workflow desde n8n/

- **WHEN** se inspecciona el archivo `docker-compose.yml`
- **THEN** el volume mount del servicio `n8n` referencia `./n8n/workflow.json` como fuente

### Requirement: Raiz del repositorio ordenada para presentacion de tesis

La raiz del repositorio SHALL contener exclusivamente archivos de configuracion y tooling de proyecto (`docker-compose.yml`, `README.md`, `CHANGES.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `.env.example`, `.jr-orchestrator-state.json`), directorios de infraestructura oculta (`.github/`, `.claude/`, `.engram/`, `.githooks/`, `.opencode/`), y directorios de primer nivel para cada componente del sistema (`App/`, `data/`, `docs/`, `evaluation/`, `knowledge-base/`, `n8n/`, `openspec/`, `scripts/`). Los archivos de tesis y los artefactos N8N NO SHALL residir sueltos en la raiz.

#### Scenario: No hay archivos de tesis sueltos en raiz

- **WHEN** se lista el contenido de la raiz del repositorio
- **THEN** `ANEXO_H_Prompt_Gemini_Especificacion.md` NO aparece; el anexo H reside en `docs/anexo_h_prompt_gemini.md`

#### Scenario: No hay workflow JSON suelto en raiz

- **WHEN** se lista el contenido de la raiz del repositorio
- **THEN** `Automatizacion_Mesa_de_Ayuda.json` NO aparece; el workflow reside en `n8n/workflow.json`

#### Scenario: No hay directorio twilio/ en raiz

- **WHEN** se lista el contenido de la raiz del repositorio
- **THEN** `twilio/` NO aparece; los artefactos Twilio residen en `n8n/twilio/`

### Requirement: Anexo H de tesis en docs/ con nombre normalizado

El anexo H de la tesis (especificacion del prompt Gemini) SHALL residir en `docs/anexo_h_prompt_gemini.md`, siguiendo la misma convencion de nomenclatura que los otros anexos en `docs/` (`anexo_c_esquema_bd.md`, `anexo_f_corpus.md`). El archivo `openspec/config.yaml` SHALL referenciarlo con su nuevo path.

#### Scenario: openspec/config.yaml referencia el anexo H correctamente

- **WHEN** se lee `openspec/config.yaml`
- **THEN** `context_files.gemini_spec` es `docs/anexo_h_prompt_gemini.md`

#### Scenario: El anexo H es accesible desde docs/

- **WHEN** se lee `docs/anexo_h_prompt_gemini.md`
- **THEN** contiene la especificacion completa del prompt Gemini (mismo contenido que el antiguo `ANEXO_H_Prompt_Gemini_Especificacion.md`)
