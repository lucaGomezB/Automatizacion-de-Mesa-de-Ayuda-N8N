## MODIFIED Requirements

### Requirement: Job de pruebas del backend

El workflow SHALL definir un job `backend-tests` que se ejecute sobre Python 3.12. El job MUST hacer checkout del repositorio, configurar Python 3.12 con cache de dependencias de pip, instalar las dependencias declaradas en `App/Backend/requirements.txt`, y ejecutar la suite pytest del backend con medicion de cobertura sobre `app.routes`, `app.services` y `app.repositories`, usando el reporte `term-missing`. El job MUST ejecutarse desde el directorio `App/Backend/`. El job MUST poder completarse sin acceso a servicios externos: la suite mockea Gemini, Twilio, Outlook y N8N, y usa SQLite in-memory para la base de datos.

#### Scenario: El job de backend instala dependencias y corre la suite con cobertura

- **WHEN** se ejecuta el job `backend-tests`
- **THEN** instala las dependencias de `App/Backend/requirements.txt` y ejecuta pytest con cobertura sobre `app.routes`, `app.services` y `app.repositories`, reportando las lineas faltantes

#### Scenario: El job de backend corre sobre Python 3.12

- **WHEN** se ejecuta el job `backend-tests`
- **THEN** el interprete de Python configurado por el paso de setup es la version 3.12

#### Scenario: El job de backend no requiere secretos

- **WHEN** se ejecuta el job `backend-tests` en un repositorio sin ningun secreto configurado (sin `GEMINI_API_KEY` ni credenciales de Twilio, Outlook o base de datos)
- **THEN** la suite completa el run usando los mocks y SQLite in-memory, sin fallar por falta de credenciales

### Requirement: Job de pruebas del frontend

El workflow SHALL definir un job `frontend-tests` que se ejecute sobre Node 20. El job MUST hacer checkout del repositorio, configurar Node 20 con cache de npm, instalar las dependencias del frontend con `npm ci` desde `App/Frontend/`, y ejecutar la suite de pruebas con cobertura mediante el script `test:coverage` de `App/Frontend/package.json` (Vitest con proveedor `v8`). El job MUST poder completarse sin acceso a servicios externos: la suite mockea Axios y no levanta el backend.

#### Scenario: El job de frontend instala dependencias y corre la suite con cobertura

- **WHEN** se ejecuta el job `frontend-tests`
- **THEN** ejecuta `npm ci` en `App/Frontend/` y luego el script `test:coverage`, que corre Vitest con reporte de cobertura del proveedor `v8`

#### Scenario: El job de frontend corre sobre Node 20

- **WHEN** se ejecuta el job `frontend-tests`
- **THEN** la version de Node configurada por el paso de setup es la 20

### Requirement: Linting en el pipeline

El workflow SHALL ejecutar analisis estatico (linting) sobre ambas bases de codigo como parte de la integracion continua. El job `backend-tests` MUST ejecutar `ruff check` sobre el codigo del backend, usando una configuracion versionada en el repositorio que arranque en modo permisivo para no bloquear el pipeline por la deuda de estilo del codigo existente. El job `frontend-tests` MUST ejecutar el linter del frontend (ESLint) mediante un script `lint` declarado en `App/Frontend/package.json`. ESLint y ruff MUST introducirse como parte de este change, ya que el proyecto no los tiene configurados.

#### Scenario: El backend pasa el lint de ruff con la configuracion permisiva

- **WHEN** se ejecuta el paso de `ruff check` del job `backend-tests` sobre el codigo actual del backend
- **THEN** ruff usa la configuracion versionada del repositorio y el paso completa sin marcar la corrida como fallida por estilo preexistente

#### Scenario: El frontend ejecuta el lint configurado

- **WHEN** se ejecuta el paso de lint del job `frontend-tests`
- **THEN** se invoca el script `lint` de `App/Frontend/package.json`, que corre ESLint sobre el codigo del frontend
