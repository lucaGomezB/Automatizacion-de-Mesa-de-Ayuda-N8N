## ADDED Requirements

### Requirement: Workflow de integración continua en GitHub Actions

El repositorio SHALL definir un workflow de GitHub Actions en `.github/workflows/ci.yml` que se dispare automáticamente en cada `push` a la rama `main` y en cada `pull_request`. El workflow MUST ejecutar las suites de prueba del proyecto antes de que un cambio pueda fusionarse a `main`. El workflow MUST fijar (pin) las versiones mayores de las acciones que utiliza (por ejemplo `actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`) para que las corridas sean reproducibles.

#### Scenario: El workflow se dispara en un pull request

- **WHEN** se abre o actualiza un pull request contra cualquier rama del repositorio
- **THEN** GitHub Actions inicia el workflow `ci.yml` y ejecuta sus jobs

#### Scenario: El workflow se dispara en push a main

- **WHEN** se hace push de uno o más commits a la rama `main`
- **THEN** GitHub Actions inicia el workflow `ci.yml` y ejecuta sus jobs

#### Scenario: Las acciones usadas están fijadas a una versión mayor

- **WHEN** se inspecciona el contenido de `.github/workflows/ci.yml`
- **THEN** cada `uses:` de una acción de terceros referencia una versión mayor explícita (por ejemplo `@v4`), sin usar una referencia flotante de rama

### Requirement: Job de pruebas del backend

El workflow SHALL definir un job `backend-tests` que se ejecute sobre Python 3.12. El job MUST hacer checkout del repositorio, configurar Python 3.12 con caché de dependencias de pip, instalar las dependencias declaradas en `App/Backend/requirements.txt`, y ejecutar la suite pytest del backend con medición de cobertura sobre `app.routes`, `app.services` y `app.repositories`, usando el reporte `term-missing`. El job MUST ejecutarse desde el directorio `App/Backend/`. El job MUST poder completarse sin acceso a servicios externos: la suite mockea Gemini, Twilio, Outlook y N8N, y usa SQLite in-memory para la base de datos.

#### Scenario: El job de backend instala dependencias y corre la suite con cobertura

- **WHEN** se ejecuta el job `backend-tests`
- **THEN** instala las dependencias de `App/Backend/requirements.txt` y ejecuta pytest con cobertura sobre `app.routes`, `app.services` y `app.repositories`, reportando las líneas faltantes

#### Scenario: El job de backend corre sobre Python 3.12

- **WHEN** se ejecuta el job `backend-tests`
- **THEN** el intérprete de Python configurado por el paso de setup es la versión 3.12

#### Scenario: El job de backend no requiere secretos

- **WHEN** se ejecuta el job `backend-tests` en un repositorio sin ningún secreto configurado (sin `GEMINI_API_KEY` ni credenciales de Twilio, Outlook o base de datos)
- **THEN** la suite completa el run usando los mocks y SQLite in-memory, sin fallar por falta de credenciales

### Requirement: Job de pruebas del frontend

El workflow SHALL definir un job `frontend-tests` que se ejecute sobre Node 20. El job MUST hacer checkout del repositorio, configurar Node 20 con caché de npm, instalar las dependencias del frontend con `npm ci` desde `Frontend/`, y ejecutar la suite de pruebas con cobertura mediante el script `test:coverage` de `App/Frontend/package.json` (Vitest con proveedor `v8`). El job MUST poder completarse sin acceso a servicios externos: la suite mockea Axios y no levanta el backend.

#### Scenario: El job de frontend instala dependencias y corre la suite con cobertura

- **WHEN** se ejecuta el job `frontend-tests`
- **THEN** ejecuta `npm ci` en `App/Frontend/` y luego el script `test:coverage`, que corre Vitest con reporte de cobertura del proveedor `v8`

#### Scenario: El job de frontend corre sobre Node 20

- **WHEN** se ejecuta el job `frontend-tests`
- **THEN** la versión de Node configurada por el paso de setup es la 20

### Requirement: Linting en el pipeline

El workflow SHALL ejecutar análisis estático (linting) sobre ambas bases de código como parte de la integración continua. El job `backend-tests` MUST ejecutar `ruff check` sobre el código del backend, usando una configuración versionada en el repositorio que arranque en modo permisivo para no bloquear el pipeline por la deuda de estilo del código existente. El job `frontend-tests` MUST ejecutar el linter del frontend (ESLint) mediante un script `lint` declarado en `App/Frontend/package.json`. ESLint y ruff MUST introducirse como parte de este change, ya que el proyecto no los tiene configurados.

#### Scenario: El backend pasa el lint de ruff con la configuración permisiva

- **WHEN** se ejecuta el paso de `ruff check` del job `backend-tests` sobre el código actual del backend
- **THEN** ruff usa la configuración versionada del repositorio y el paso completa sin marcar la corrida como fallida por estilo preexistente

#### Scenario: El frontend ejecuta el lint configurado

- **WHEN** se ejecuta el paso de lint del job `frontend-tests`
- **THEN** se invoca el script `lint` de `App/Frontend/package.json`, que corre ESLint sobre el código del frontend

### Requirement: Pipeline sin secretos

El workflow de CI SHALL ejecutarse íntegramente sin requerir ningún secreto del repositorio. El workflow MUST NOT declarar, leer ni depender de secretos como `GEMINI_API_KEY`, credenciales de Twilio, Outlook, base de datos u otros servicios externos. Todas las pruebas que necesitarían servicios externos MUST estar mockeadas en las suites.

#### Scenario: El workflow no referencia ningún secreto

- **WHEN** se inspecciona el contenido de `.github/workflows/ci.yml`
- **THEN** no aparece ninguna referencia a `secrets.*` ni la declaración de variables de entorno que contengan credenciales

#### Scenario: El pipeline completa en un fork sin secretos heredados

- **WHEN** un pull request proviene de un fork que no tiene acceso a los secretos del repositorio base
- **THEN** ambos jobs completan correctamente porque ninguna prueba depende de un secreto

### Requirement: Badge de estado del CI en el README

El `README.md` del repositorio SHALL mostrar un badge que refleje el estado del workflow de integración continua de GitHub Actions. El badge MUST poder renderizarse sin requerir cuentas ni tokens de servicios de terceros (usa la URL de badge nativa de GitHub Actions del propio repositorio).

#### Scenario: El README muestra el badge de estado del workflow

- **WHEN** se visualiza el `README.md` del repositorio
- **THEN** se muestra un badge que enlaza al workflow de CI y refleja su estado (passing/failing), servido por GitHub Actions sin tokens de terceros
