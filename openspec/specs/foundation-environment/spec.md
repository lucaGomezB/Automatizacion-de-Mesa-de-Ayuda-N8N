# foundation-environment — Spec

## Purpose

Define los requisitos del entorno base del proyecto: configuración OPSX, resolución determinística del prompt de Gemini, estado inicial de la base de datos, y versionado de la memoria compartida del proyecto.

## Requirements

### Requirement: Configuración OPSX del proyecto
El repositorio SHALL contener `openspec/config.yaml` declarando el stack tecnológico (FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15, N8N, Gemini 2.5 Flash, React 19 + TypeScript + Vite) y las rutas canónicas del proyecto (`App/Backend/`, `App/Frontend/`, `knowledge-base/`, `CHANGES.md`).

#### Scenario: Sub-agente consulta el contexto del proyecto
- **WHEN** un agente ejecuta `openspec status` o lee `openspec/config.yaml`
- **THEN** obtiene el stack y las rutas reales del proyecto sin inferirlas del código

### Requirement: Resolución del prompt de Gemini independiente del cwd
El clasificador Gemini SHALL resolver la ruta de `prompt_gemini.txt` de forma determinística e independiente del directorio de trabajo, con default anclado a la raíz del repositorio (`docs/prompt_gemini.txt`) y override posible vía variable de entorno `GEMINI_PROMPT_PATH`.

#### Scenario: Arranque desde App/Backend/
- **WHEN** la aplicación se inicia con cwd en `App/Backend/`
- **THEN** el prompt se carga correctamente y NO se emite el warning `prompt_file_not_found`

#### Scenario: Override por variable de entorno
- **WHEN** `GEMINI_PROMPT_PATH` apunta a una ruta válida alternativa
- **THEN** el clasificador usa esa ruta en lugar del default

#### Scenario: Prompt inexistente
- **WHEN** la ruta resuelta no existe
- **THEN** se emite un log de advertencia con la ruta intentada y el clasificador Gemini queda en modo degradado (fallback), sin impedir el arranque de la aplicación

### Requirement: Migraciones y catálogos sembrados
La base de datos SHALL estar al día con las migraciones Alembic, y las tablas de catálogo SHALL contener sus valores canónicos: sector (`Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`), estado (nuevo, en proceso, en espera, resuelto, cerrado), canal_origen (correo electrónico, formulario web, llamada telefónica). Los cinco sectores canónicos SHALL quedar sembrados por la migración `004`, que MUST NOT modificar la migración ya aplicada `001_seed_catalogs.py`.

#### Scenario: Base de datos nueva
- **WHEN** se ejecuta `alembic upgrade head` sobre una base vacía
- **THEN** se crean las tablas y los catálogos quedan sembrados con sus valores canónicos, incluyendo los cinco sectores canónicos y las estructuras de persistencia multietiqueta

#### Scenario: Base de datos existente (idempotencia)
- **WHEN** se ejecuta `alembic upgrade head` sobre una base ya migrada
- **THEN** la operación es no-op y los catálogos no se duplican

#### Scenario: Operaciones ausente y Sistemas presente
- **WHEN** se inspecciona el catálogo `sector` tras las migraciones
- **THEN** `Operaciones` no existe como fila y `Sistemas` permanece como sector propio

### Requirement: Memoria compartida del proyecto versionada
El repositorio SHALL versionar `.engram/` con la memoria del proyecto exportada por `engram sync` (filtrada por proyecto, nunca `--all`), y el `README.md` SHALL documentar el workflow: exportar antes de push, importar (`engram sync --import`) después de clone/pull.

#### Scenario: Colaborador clona el repo
- **WHEN** un colaborador ejecuta `engram sync --import` tras clonar
- **THEN** recupera la memoria del proyecto en su base local de engram

#### Scenario: Export filtrado
- **WHEN** se ejecuta `engram sync` desde la raíz del proyecto
- **THEN** solo se exporta memoria de este proyecto a `.engram/chunks/`

### Requirement: Foundation environment SHALL include Dockerized services
The foundation environment SHALL provide Docker containers for backend, frontend, and supporting services with security best practices and production-ready configurations.

#### Scenario: All services start with docker compose
- **WHEN** user runs `docker compose up -d`
- **THEN** all services SHALL start successfully with healthchecks passing
- **AND** containers SHALL run as non-root users

#### Scenario: Backend container runs with security hardening
- **WHEN** the backend container starts
- **THEN** it SHALL run as a non-root user
- **AND** include a healthcheck that verifies FastAPI availability on port 8000

#### Scenario: Frontend container serves production build
- **WHEN** the frontend container starts in production mode
- **THEN** it SHALL serve static assets via nginx
- **AND** run as a non-root user
- **AND** include a healthcheck that verifies nginx availability on port 3000

### Requirement: Docker build context SHALL be optimized
The project SHALL include .dockerignore files to exclude unnecessary files from Docker build context.

#### Scenario: Backend build excludes development files
- **WHEN** building the backend Docker image
- **THEN** the build context SHALL exclude .git, __pycache__, tests/, .pytest_cache, and .env files

#### Scenario: Frontend build excludes development files
- **WHEN** building the frontend Docker image
- **THEN** the build context SHALL exclude .git, node_modules/, dist/, and .env files

### Requirement: Frontend SHALL support production-ready Docker builds
The frontend Dockerfile SHALL implement multi-stage builds with nginx for production deployment.

#### Scenario: Multi-stage build produces optimized image
- **WHEN** the frontend Docker image is built
- **THEN** it SHALL use a multi-stage build with build and production stages
- **AND** the production stage SHALL only contain nginx and static assets
- **AND** use npm ci for deterministic dependency installation

#### Scenario: Nginx serves SPA with proper routing
- **WHEN** the frontend container serves the application
- **THEN** nginx SHALL serve index.html for all routes to support client-side routing
- **AND** static assets SHALL be served with appropriate caching headers

### Requirement: ENV-001 — N8N configurado con retencion de ejecuciones

El servicio N8N en `docker-compose.yml` SHALL incluir variables de entorno que configuren la poda automatica de datos de ejecucion con antiguedad mayor a 30 dias (720 horas). La exposicion de red del servicio N8N (puertos publicados, redes y credenciales de servicios de datos) PUEDE cambiar por un change de hardening de infraestructura sin que la retencion se altere.

#### Scenario: Variables de retencion presentes en compose

- **WHEN** se inspecciona la seccion `services.n8n.environment` en `docker-compose.yml`
- **THEN** la variable `EXECUTIONS_DATA_PRUNE` tiene el valor `"true"`
- **AND** la variable `EXECUTIONS_DATA_MAX_AGE` tiene el valor `"720"`

#### Scenario: Resto de la configuracion N8N sin cambios

- **WHEN** se inspeccionan el resto de las variables de entorno del servicio N8N
- **THEN** las variables de negocio (`BACKEND_URL`, `COST_GUARD_SHARED_SECRET`, etc.) permanecen sin modificacion
- **AND** los volumes del servicio N8N no se alteran

#### Scenario: La exposicion de red puede cambiar sin afectar la retencion

- **WHEN** un change de hardening de infraestructura (c-62) modifica los puertos publicados, las redes o las credenciales de servicios de datos del servicio N8N
- **THEN** la retencion de ejecuciones (`EXECUTIONS_DATA_PRUNE`, `EXECUTIONS_DATA_MAX_AGE`) permanece vigente

### Requirement: Integridad referencial y restaurabilidad de la memoria exportada

La memoria del proyecto versionada en `.engram/` (chunks `.jsonl.gz` direccionados por contenido) SHALL ser autocontenida y restaurable: un clon limpio SHALL poder ejecutar `engram sync --import --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` y aplicar TODOS los chunks sin error. En particular, todo extremo (`source_id` o `target_id`) de una mutacion de relacion (`entity == "relation"`, `op == "upsert"`) registrada en cualquier chunk SHALL existir como observacion (`sync_id`) en la union de TODOS los chunks. El repositorio SHALL mantener esta invariante de forma APPEND-ONLY: los chunks existentes MUST NOT editarse ni borrarse (su identidad depende de su contenido), y las correcciones SHALL expresarse agregando chunks nuevos. El repositorio MUST NOT alterar esta invariante por las siguientes vias prohibidas: gitignorear o destrackear `.engram/`, reescribir el historial de git, o ejecutar `engram sync --all` (que exportaria memoria de otros proyectos). El repositorio SHALL proveer, ademas, un procedimiento de recuperacion reproducible y documentado que detecte los datos locales (observaciones y prompts del proyecto) ausentes en todos los chunks y los re-exporte hacia un chunk NUEVO, sin editar chunks existentes, sin exponer secretos y sin incluir el nombre real de ningun colaborador.

#### Scenario: Un clon limpio restaura la memoria sin error

- **WHEN** un colaborador clona el repositorio y ejecuta `git config core.hooksPath .githooks` y `engram sync --import --project "Automatizacion-de-Mesa-de-Ayuda-N8N"`
- **THEN** el import aplica todos los chunks y termina sin el error `relation FK precondition not met: referenced observation missing`
- **AND** la memoria del proyecto queda disponible en la base local de Engram

#### Scenario: Toda relacion referencia observaciones presentes en la union de chunks

- **WHEN** se recorre cada chunk de `.engram/chunks/` y se recolecta el conjunto de `sync_id` de sus observaciones
- **THEN** cada mutacion de relacion con `op == "upsert"` tiene su `source_id` y su `target_id` dentro de ese conjunto
- **AND** el numero de referencias colgantes es cero

#### Scenario: La correccion es append-only

- **WHEN** se re-exporta un dato local que el watermark omitio
- **THEN** la correccion se materializa como un chunk NUEVO bajo `.engram/chunks/`
- **AND** ningun chunk preexistente se edita ni se borra
- **AND** la entrada correspondiente se agrega a `.engram/manifest.json` sin remover entradas previas

#### Scenario: Vias de correccion prohibidas

- **WHEN** se inspecciona la configuracion y el historial del repositorio
- **THEN** `.engram/` no figura en `.gitignore` ni fue destrackeado
- **AND** no se ejecuto `engram sync --all` para reparar la memoria
- **AND** no se reescribio el historial de git

#### Scenario: Recuperacion reproducible de los datos omitidos por el watermark

- **WHEN** se ejecuta el procedimiento de recuperacion documentado sobre una base local con datos del proyecto ausentes en los chunks
- **THEN** los datos omitidos quedan exportados en un chunk nuevo
- **AND** el procedimiento no imprime secretos ni nombres reales de colaboradores
- **AND** al re-ejecutar la deteccion no quedan datos del proyecto ausentes en los chunks

### Requirement: Nota tecnica exacta de la version de Engram y la decision de actualizacion

El repositorio SHALL documentar de forma exacta, en una nota canonica de la memoria de Engram, la version efectivamente usada (Engram 1.20.0 con manifest version 1) y la decision del equipo de NO actualizar a Engram 3.x por ahora, con su justificacion. La justificacion escrita MUST NOT afirmar que Engram 3.x rechaza el manifest v1 del repositorio como un todo. La nota SHALL declarar que Engram v3.7.1 ACEPTA el manifest v1 y lo MIGRA a manifest v2 al exportar cuando hay sesiones propias del proyecto, y que lo que Engram rechaza son ciertas DEGRADACIONES (bajadas de version), no el manifest v1 en si. La nota SHALL registrar ademas el mecanismo de defecto conocido y su mitigacion vigente: el watermark global `lastChunkTime` del export incremental puede omitir datos locales mas viejos que el ultimo chunk de otra maquina, y el repositorio se protege con la guarda de integridad de CI y el procedimiento de recuperacion append-only; el parche del CLI queda pendiente para una futura actualizacion.

#### Scenario: La nota declara la version usada y la decision

- **WHEN** se lee la nota canonica de la memoria de Engram
- **THEN** declara Engram 1.20.0 con manifest version 1 como la version en uso
- **AND** declara la decision de no actualizar a Engram 3.x por ahora, con su motivo

#### Scenario: La justificacion no afirma que el v3 rechaza el manifest v1

- **WHEN** se busca en la documentacion del repositorio la afirmacion de que Engram 3.x rechaza el manifest v1 como un todo
- **THEN** no aparece
- **AND** la nota declara que v3.7.1 acepta el manifest v1 y lo migra a v2 al exportar cuando hay sesiones propias del proyecto, y que rechaza ciertas degradaciones, no el v1 en si

#### Scenario: El defecto del watermark y su mitigacion quedan registrados

- **WHEN** se lee la nota canonica de la memoria de Engram
- **THEN** describe el watermark global `lastChunkTime` como causa del dato omitido
- **AND** remite a la guarda de integridad de CI y al procedimiento de recuperacion append-only como mitigacion vigente
