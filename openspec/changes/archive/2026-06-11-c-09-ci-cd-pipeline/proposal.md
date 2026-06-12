## Why

El proyecto ya tiene dos suites de pruebas automatizadas maduras —backend pytest (187 passed / 1 skipped / 1 xfailed, cobertura 89% en routes/services/repositories tras C-06) y frontend Vitest (68 tests, cobertura 98.6% en el alcance, tras C-07)— pero **nada las ejecuta automáticamente**: no existe el directorio `.github/`, así que hoy una regresión solo se detecta si un colaborador corre las suites a mano antes de mergear. El §6.5 de la tesis afirma textualmente que «la integración continua se ejecuta automáticamente en cada solicitud de incorporación al repositorio mediante GitHub Actions, ejecutando la suite completa antes de permitir la fusión a la rama principal»; C-09 hace que esa afirmación sea verdadera, cerrando el GATE 3 del roadmap y dejando la calidad del repo auditable de forma reproducible y sin intervención manual.

## What Changes

- **Workflow de GitHub Actions** en `.github/workflows/ci.yml`, disparado en cada `push` a `main` y en cada `pull_request`. El directorio `.github/` no existe hoy y se crea con este change.
- **Job `backend-tests`** (Python 3.12): hace checkout, configura Python con caché de pip, instala `Gestion_Incidentes/requirements.txt`, corre `ruff check` sobre el código del backend, y ejecuta la suite pytest con cobertura (`--cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing`) desde `Gestion_Incidentes/`. La suite corre 100% offline (servicios externos ya mockeados, SQLite in-memory); no consume ningún secreto.
- **Job `frontend-tests`** (Node 20): hace checkout, configura Node con caché de npm, ejecuta `npm ci` en `Frontend/`, corre el lint del frontend, y ejecuta `npm run test:coverage` (Vitest con proveedor `v8`).
- **Linting introducido por este change** (hoy no hay ninguno configurado):
  - Backend: se introduce **ruff** en modo permisivo para no bloquear CI por deuda de estilo del código existente. Se fija la versión de ruff en el workflow (no se agrega a `requirements.txt` de runtime) y se incluye una configuración mínima (`Gestion_Incidentes/ruff.toml`) que arranca conservadora.
  - Frontend: el proyecto fue generado con Vite y **no tiene ESLint configurado** ni un script `lint` en `package.json`. C-09 agrega ESLint (flat config para TS + React) como `devDependency`, un script `lint`, y lo ejecuta en CI.
- **Badge de cobertura/CI en `README.md`**: se agrega el badge de estado del workflow de GitHub Actions (status del CI), que no requiere servicios de terceros ni tokens. Un badge de porcentaje de cobertura vía Codecov/Coveralls se descarta por requerir cuenta/secreto externo; la decisión queda registrada en design.md.

No hay cambios BREAKING. C-09 es **aditivo**: agrega configuración de CI y de linters; no modifica el código de aplicación del backend ni del frontend ni el comportamiento de las suites existentes.

## Capabilities

### New Capabilities
- `ci-pipeline`: define el contrato de la integración continua del repositorio —los disparadores (push a `main`, pull requests), los dos jobs paralelos (`backend-tests` en Python 3.12, `frontend-tests` en Node 20), la ejecución de las suites de prueba con cobertura, los pasos de linting (ruff para Python, ESLint para el frontend) y la restricción de que el pipeline corre completamente offline sin requerir ningún secreto. Es la capacidad que orquesta la ejecución de las suites que `backend-integration-tests` y `frontend-testing` ya especifican; no redefine esas suites, las consume.

### Modified Capabilities
<!-- Ninguna. C-09 es aditivo: no cambia los requisitos de las capacidades existentes.
     backend-integration-tests y frontend-testing especifican QUÉ verifican las suites
     y su cobertura; C-09 solo agrega el orquestador (CI) que las corre. Las demás
     capacidades (data-pseudonymization, evaluation-framework, foundation-environment,
     n8n-notification, n8n-workflow) no se ven afectadas. -->

## Impact

- **Código nuevo**:
  - `.github/workflows/ci.yml` (el workflow; nuevo directorio `.github/`).
  - `Gestion_Incidentes/ruff.toml` (config mínima permisiva de ruff).
  - Configuración de ESLint del frontend (flat config `Frontend/eslint.config.js`).
- **Edición mínima**:
  - `Frontend/package.json`: agrega ESLint y plugins como `devDependencies` y un script `lint`. Sin tocar `dependencies` de runtime.
  - `README.md`: agrega el badge de estado del workflow de CI cerca del título.
- **Dependencias nuevas**:
  - Frontend (solo dev): `eslint` y los plugins/parsers necesarios para TS + React, fijados a versiones compatibles con la toolchain Vite 5 / TS 5.5.
  - Backend: `ruff` NO se agrega a `requirements.txt`; se instala con versión fija dentro del job de CI para no contaminar las dependencias de runtime/test del módulo.
- **Restricción de seguridad (Governance BAJO, pero explícita)**: el CI **NO** debe declarar ni requerir ningún secreto (`GEMINI_API_KEY`, credenciales de Twilio/Outlook, DB, etc.). Las dos suites ya mockean todo servicio externo y corren contra SQLite in-memory / Axios mockeado.
- **Corpus de evaluación**: la suite de `evaluation/` corre con un `corpus_fixture.csv` versionado y un `FakeClassifier`; no depende del corpus real (`data/corpus_evaluacion_pseudonimizado.csv`, no trackeado en git), por lo que el CI no necesita ese archivo. La decisión sobre si el job de backend incluye o no la suite de `evaluation/` se documenta en design.md.
- **Versión de Python en CI vs. local**: el roadmap fija Python **3.12** para CI, mientras el dev local corre 3.13. coverage.py reporta más bajo en 3.13 por un artefacto con líneas post-`await`; en 3.12 la cobertura medida puede diferir, así que el umbral de cobertura de CI (si se fija un `--cov-fail-under`) debe dejar margen o medirse primero. Decisión registrada en design.md.
- **Tesis**: hace verdadera la afirmación del §6.5 sobre CI con GitHub Actions ejecutándose en cada PR antes del merge a `main`.
