## ADDED Requirements

### Requirement: DOC-005 — Stack declarado en la documentacion para agentes sincronizado con el codigo

La documentacion que heredan los agentes (`CLAUDE.md` y `openspec/config.yaml`) SHALL declarar solo valores de stack que se puedan reproducir desde el codigo o desde los archivos de dependencias: el modelo de inferencia y sus parametros desde `App/Backend/app/config/settings.py`, y las versiones de framework y librerias desde `App/Backend/requirements.txt` y `docker-compose.yml`. Ningun valor MUST provenir de otro documento, y ningun valor retirado MUST citarse como vigente.

El flujo de clasificacion y los servicios de infraestructura que esos documentos describan MUST existir en el repositorio; una etapa o un servicio que ya no existe MUST retirarse o declararse historico, no describirse como vigente.

#### Scenario: Modelo y parametros de inferencia coinciden con la configuracion

- **WHEN** se leen las lineas de `CLAUDE.md` y de `openspec/config.yaml` que declaran el modelo y los parametros de inferencia
- **THEN** el modelo coincide con `Settings.gemini_model`
- **AND** temperature, top_p y max_output_tokens coinciden con `Settings`
- **AND** el timeout, el timeout total y los reintentos declarados coinciden con `Settings.gemini_timeout_seconds`, `gemini_total_timeout_seconds` y `gemini_max_retries`

#### Scenario: Versiones de framework y dependencias coinciden con los pines

- **WHEN** se leen las versiones de FastAPI, Uvicorn y `google-genai` declaradas en `openspec/config.yaml`
- **THEN** coinciden con las restricciones vigentes de `App/Backend/requirements.txt`
- **AND** la version de N8N declarada coincide con la imagen pinneada del compose

#### Scenario: Flujo y servicios descritos existen en el repositorio

- **WHEN** la documentacion para agentes describe una etapa de clasificacion o un servicio de infraestructura
- **THEN** la etapa o el servicio existe en el codigo o en el compose
- **AND** ninguna etapa o servicio retirado se describe como vigente

#### Scenario: Valores retirados no se citan como vigentes

- **WHEN** se busca en `CLAUDE.md` y `openspec/config.yaml` un modelo, una version o un servicio que el codigo ya no usa
- **THEN** no aparece como valor vigente del stack

#### Scenario: Barrera ejecutable detecta la divergencia

- **WHEN** un valor de stack declarado en `CLAUDE.md` u `openspec/config.yaml` diverge de `settings.py`, de `requirements.txt` o del compose, o se describe un servicio o etapa que ya no existe
- **THEN** el preflight `scripts/preflight/docs_stack_sync.py` termina con codigo distinto de cero
- **AND** el hallazgo nombra el valor o el servicio divergente
- **AND** el paso corre en el job `backend-tests` del pipeline de integracion continua

#### Scenario: Barrera ejecutable en verde con la documentacion sincronizada

- **WHEN** la documentacion para agentes declara unicamente valores que coinciden con el codigo y el compose
- **THEN** el preflight termina con codigo 0 y sin hallazgos
- **AND** su suite de pruebas queda incluida en `python -m pytest scripts/preflight -q`

#### Scenario: Documentacion de agentes valida como configuracion

- **WHEN** se carga `openspec/config.yaml` con un lector YAML y se ejecuta el CLI de OpenSpec
- **THEN** el archivo parsea sin errores
- **AND** los comandos de OpenSpec siguen respondiendo sobre el proyecto
