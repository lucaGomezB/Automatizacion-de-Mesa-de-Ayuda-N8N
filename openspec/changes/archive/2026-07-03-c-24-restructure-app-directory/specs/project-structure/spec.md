## ADDED Requirements

### Requirement: Directorio unificado App/

El repositorio SHALL contener un directorio `App/` en la raiz que agrupe los componentes principales del sistema. `App/Backend/` SHALL contener la aplicacion FastAPI (antes `Gestion_Incidentes/`) y `App/Frontend/` SHALL contener la aplicacion React (antes `Frontend/`). Ambos directorios SHALL preservar su estructura interna sin modificaciones.

#### Scenario: Backend bajo App/

- **WHEN** se inspecciona el directorio `App/Backend/`
- **THEN** contiene `app/`, `tests/`, `alembic/`, `requirements.txt`, `pytest.ini`, y `.env.example`, igual que el antiguo `Gestion_Incidentes/`

#### Scenario: Frontend bajo App/

- **WHEN** se inspecciona el directorio `App/Frontend/`
- **THEN** contiene `src/`, `package.json`, `vite.config.ts`, `tsconfig.json`, e `index.html`, igual que el antiguo `Frontend/`

#### Scenario: Historial de git preservado

- **WHEN** se ejecuta `git log --follow -- App/Backend/app/main.py`
- **THEN** muestra el historial completo de commits del archivo, incluyendo commits anteriores al rename

### Requirement: Configuracion OPSX actualizada

El archivo `openspec/config.yaml` SHALL declarar las rutas canonicas actualizadas: `App/Backend/` para el backend y `App/Frontend/` para el frontend. El resto de la configuracion (stack, convenciones, thresholds) SHALL permanecer sin cambios.

#### Scenario: openspec/config.yaml refleja las nuevas rutas

- **WHEN** se lee `openspec/config.yaml`
- **THEN** `stack.backend.path` es `App/Backend/` y `stack.frontend.path` es `App/Frontend/`

### Requirement: Docker Compose con rutas actualizadas

El archivo `docker-compose.yml` SHALL referenciar las nuevas rutas `./App/Backend` para el contexto de build del backend y `./App/Frontend` para el contexto de build y volumenes del frontend. Los volumenes de frontend SHALL apuntar a `./App/Frontend/src`, `./App/Frontend/index.html`, y `./App/Frontend/vite.config.ts`.

#### Scenario: Docker compose levanta el sistema completo

- **WHEN** se ejecuta `docker compose up -d` desde la raiz del repositorio
- **THEN** los servicios `backend`, `frontend`, `postgres`, `redis`, y `n8n` inician correctamente y pasan sus healthchecks

#### Scenario: Hot reload del frontend funciona

- **WHEN** se modifica un archivo en `App/Frontend/src/`
- **THEN** el cambio se refleja en el contenedor de frontend en tiempo real (volume mount activo)

### Requirement: CI pipeline con rutas actualizadas

El workflow `.github/workflows/ci.yml` SHALL usar `App/Backend/` como `working-directory` y `cache-dependency-path` para los jobs de backend, y `App/Frontend/` para los jobs de frontend. Los nombres de jobs y steps SHALL reflejar los nuevos paths.

#### Scenario: Job backend-tests ejecuta desde App/Backend/

- **WHEN** se ejecuta el job `backend-tests` en GitHub Actions
- **THEN** instala dependencias desde `App/Backend/requirements.txt`, ejecuta pytest con cobertura desde `App/Backend/`, y completa exitosamente

#### Scenario: Job frontend-tests ejecuta desde App/Frontend/

- **WHEN** se ejecuta el job `frontend-tests` en GitHub Actions
- **THEN** instala dependencias con `npm ci` desde `App/Frontend/`, ejecuta `npm run test:coverage` desde `App/Frontend/`, y completa exitosamente

### Requirement: Documentacion del proyecto actualizada

Los archivos `AGENTS.md`, `CHANGES.md`, `README.md`, `knowledge-base/`, `twilio/README.md`, y `scripts/run_provisional.py` SHALL referenciar las nuevas rutas `App/Backend/` y `App/Frontend/` en lugar de `Gestion_Incidentes/` y `Frontend/` respectivamente. Las secciones de comandos de desarrollo SHALL actualizar sus prefijos `cd`.

#### Scenario: AGENTS.md muestra los nuevos paths

- **WHEN** se lee la seccion "Component Map" de `AGENTS.md`
- **THEN** `├── Gestion_Incidentes/` fue reemplazado por `├── App/Backend/` y `├── Frontend/` por `├── App/Frontend/`

#### Scenario: README.md tiene comandos actualizados

- **WHEN** se lee `README.md`
- **THEN** los comandos de configuracion referencian `App/Backend/.env` en lugar de `Gestion_Incidentes/.env`

### Requirement: Cambios activos documentados para follow-up

Los archivos `CHANGES.md` y las notas de C-24 SHALL documentar que los cambios activos C-19 y C-23 contienen referencias a rutas obsoletas en sus proposal.md y deben ser actualizados antes de su aplicacion. C-20 no requiere actualizacion por carecer de proposal.md.

#### Scenario: CHANGES.md advierte sobre paths en cambios activos

- **WHEN** se lee la entrada de C-24 en `CHANGES.md`
- **THEN** menciona explicitamente que C-19 y C-23 requieren actualizacion de paths en sus proposal files
