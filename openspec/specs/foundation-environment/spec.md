# foundation-environment — Spec

## Purpose

Define los requisitos del entorno base del proyecto: configuración OPSX, resolución determinística del prompt de Gemini, estado inicial de la base de datos, y versionado de la memoria compartida del proyecto.
## Requirements
### Requirement: Configuración OPSX del proyecto
El repositorio SHALL contener `openspec/config.yaml` declarando el stack tecnológico (FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15, N8N, Gemini 2.5 Flash, React 18 + TypeScript + Vite) y las rutas canónicas del proyecto (`App/Backend/`, `App/Frontend/`, `knowledge-base/`, `CHANGES.md`).

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
La base de datos SHALL estar al día con las migraciones Alembic, y las tablas de catálogo SHALL contener sus valores canónicos: sector (Sistemas, Operaciones, Soporte Técnico), estado (nuevo, en proceso, en espera, resuelto, cerrado), canal_origen (correo electrónico, formulario web, llamada telefónica).

#### Scenario: Base de datos nueva
- **WHEN** se ejecuta `alembic upgrade head` sobre una base vacía
- **THEN** se crean las 5 tablas y los catálogos quedan sembrados con sus valores canónicos

#### Scenario: Base de datos existente (idempotencia)
- **WHEN** se ejecuta `alembic upgrade head` sobre una base ya migrada
- **THEN** la operación es no-op y los catálogos no se duplican

### Requirement: Memoria compartida del proyecto versionada
El repositorio SHALL versionar `.engram/` con la memoria del proyecto exportada por `engram sync` (filtrada por proyecto, nunca `--all`), y el `README.md` SHALL documentar el workflow: exportar antes de push, importar (`engram sync --import`) después de clone/pull.

#### Scenario: Colaborador clona el repo
- **WHEN** un colaborador ejecuta `engram sync --import` tras clonar
- **THEN** recupera la memoria del proyecto en su base local de engram

#### Scenario: Export filtrado
- **WHEN** se ejecuta `engram sync` desde la raíz del proyecto
- **THEN** solo se exporta memoria de este proyecto a `.engram/chunks/`

### Requirement: ENV-001 — N8N configurado con retencion de ejecuciones

El servicio N8N en `docker-compose.yml` SHALL incluir variables de entorno que configuren la poda automatica de datos de ejecucion con antiguedad mayor a 30 dias (720 horas).

#### Scenario: Variables de retencion presentes en compose
- **WHEN** se inspecciona la seccion `services.n8n.environment` en `docker-compose.yml`
- **THEN** la variable `EXECUTIONS_DATA_PRUNE` tiene el valor `"true"`
- **AND** la variable `EXECUTIONS_DATA_MAX_AGE` tiene el valor `"720"`

#### Scenario: Resto de la configuracion N8N sin cambios
- **WHEN** se inspeccionan el resto de las variables de entorno del servicio N8N
- **THEN** las variables existentes (`N8N_BASIC_AUTH_ACTIVE`, `BACKEND_URL`, `QUEUE_BULL_REDIS_HOST`, etc.) permanecen sin modificacion
- **AND** los volumes, puertos y dependencias del servicio N8N no se alteran

