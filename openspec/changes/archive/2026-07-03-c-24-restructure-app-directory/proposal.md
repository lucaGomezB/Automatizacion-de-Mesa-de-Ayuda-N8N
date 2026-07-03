# C-24: Reestructuracion del Directorio App

## Why

El repositorio tiene sus componentes principales — backend FastAPI y frontend React — dispersos en la raiz como `Gestion_Incidentes/` y `Frontend/`. Para la presentacion como anexo de tesis universitaria (UTN-FRM 2026), el proyecto necesita una estructura mas limpia y ordenada donde ambos componentes convivan bajo un directorio unificado `App/` (`App/Backend/` y `App/Frontend/`). Esto no cambia funcionalidad, pero mejora la legibilidad y la organizacion del repositorio para evaluadores academicos que leen el proyecto por primera vez.

## What Changes

- **Reubicacion de directorios**: `Gestion_Incidentes/` se mueve a `App/Backend/` y `Frontend/` se mueve a `App/Frontend/` mediante `git mv` (preserva historial).
- **Actualizacion de rutas en archivos de configuracion**: docker-compose.yml, CI pipeline, README.md, AGENTS.md, CHANGES.md, openspec/config.yaml, scripts, twilio, knowledge-base, y specs principales.
- **Actualizacion de referencias en cambios activos**: los proposal files de C-19, C-20, C-23 deben reflejar las nuevas rutas.
- **Sin cambios en codigo interno**: imports relativos dentro de cada proyecto, tests, y el workflow N8N JSON permanecen intactos.
- **Sin cambios en directorios no afectados**: evaluation/, data/, docs/, openspec/, knowledge-base/, scripts/, twilio/ conservan su ubicacion en la raiz.

## Capabilities

### New Capabilities
- `project-structure`: Define la nueva disposicion de directorios del repositorio, con backend y frontend bajo `App/`, y documenta las rutas canonicas actualizadas.

### Modified Capabilities
- `foundation-environment`: La configuracion OPSX (`openspec/config.yaml`) debe declarar las nuevas rutas `App/Backend/` y `App/Frontend/` en lugar de `Gestion_Incidentes/` y `Frontend/`. El escenario de arranque desde el directorio del backend debe referir `App/Backend/`.
- `ci-pipeline`: Todas las referencias a `Gestion_Incidentes/` y `Frontend/` en los steps del workflow CI deben actualizarse a `App/Backend/` y `App/Frontend/`.
- `project-documentation`: Las referencias a `Gestion_Incidentes/app/models/` y `Gestion_Incidentes/app/routes/` en los specs de documentacion deben actualizarse a `App/Backend/app/models/` y `App/Backend/app/routes/`.
- `frontend-testing`: Las referencias a `Frontend/package.json` deben actualizarse a `App/Frontend/package.json`.

## Impact

### Archivos de configuracion (7 archivos, ~60 referencias)
- `docker-compose.yml` — 7 referencias a `./Gestion_Incidentes` y `./Frontend`
- `.github/workflows/ci.yml` — 10 referencias (working-directory, cache-dependency-path)
- `openspec/config.yaml` — 2 referencias (paths de backend y frontend)
- `AGENTS.md` — ~15 referencias (component map, dev commands, env vars)
- `CHANGES.md` — ~20 referencias en secciones "Leer antes"
- `README.md` — ~5 referencias (setup commands, frontend section)
- `.gitignore` — sin cambios necesarios (usa patrones genericos)

### Documentacion del proyecto (5+ archivos)
- `knowledge-base/` — 8 referencias (08_arquitectura_propuesta.md, 05_reglas_de_negocio.md, 06_funcionalidades.md, 04_modelo_de_datos.md, 02_descripcion_general.md)
- `twilio/README.md` — 1 referencia a `.env`
- `scripts/run_provisional.py` — 4 referencias (ruta de .env, sys.path)
- `openspec/specs/foundation-environment/spec.md` — 3 referencias
- `openspec/specs/ci-pipeline/spec.md` — 7 referencias
- `openspec/specs/project-documentation/spec.md` — 2 referencias
- `openspec/specs/frontend-testing/spec.md` — 2 referencias

### Cambios activos afectados (post-C-24)
- `openspec/changes/c-19-integration-tests-postgresql/proposal.md` — contiene referencias a `Gestion_Incidentes/`
- `openspec/changes/c-23-dashboard-analytics-implementation/proposal.md` — contiene referencias a `Gestion_Incidentes/` y `Frontend/`
- `openspec/changes/c-20-tls-docker-compose/` — sin proposal aun, no afectado

### Que NO cambia
- Codigo fuente interno de `Gestion_Incidentes/` (ahora `App/Backend/`) — imports relativos
- Codigo fuente interno de `Frontend/` (ahora `App/Frontend/`) — imports relativos
- Suites de test — usan paths relativos internos
- `Automatizacion_Mesa_de_Ayuda.json` — workflow N8N
- `evaluation/` y su `pytest.ini`
- `.engram/` y `.opencode/`
- `.githooks/` y `.github/` (excepto ci.yml)
