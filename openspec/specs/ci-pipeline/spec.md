# ci-pipeline Specification

## Purpose

Esta especificación define el pipeline de integración continua en GitHub Actions: los disparadores del workflow, los jobs de pruebas de backend y frontend, el linting, el manejo seguro de secretos y el badge de estado en el README.

## Requirements

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

El workflow SHALL definir un job `frontend-tests` que se ejecute sobre Node 24. El job MUST hacer checkout del repositorio, configurar Node 24 con caché de npm, instalar las dependencias del frontend con `npm ci` desde `App/Frontend/`, y ejecutar la suite de pruebas con cobertura mediante el script `test:coverage` de `App/Frontend/package.json` (Vitest con proveedor `v8`). El job MUST poder completarse sin acceso a servicios externos: la suite mockea Axios y no levanta el backend.

#### Scenario: El job de frontend instala dependencias y corre la suite con cobertura

- **WHEN** se ejecuta el job `frontend-tests`
- **THEN** ejecuta `npm ci` en `App/Frontend/` y luego el script `test:coverage`, que corre Vitest con reporte de cobertura del proveedor `v8`

#### Scenario: El job de frontend corre sobre Node 24

- **WHEN** se ejecuta el job `frontend-tests`
- **THEN** la versión de Node configurada por el paso de setup es la 24

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

### Requirement: Escaneo de seguridad de dependencias y SAST en el pipeline

El workflow de integracion continua SHALL ejecutar un job de escaneo de seguridad, en paralelo a los jobs de pruebas existentes, que corra sobre Python 3.12 y Node 24 y cubra: auditoria de vulnerabilidades conocidas de las dependencias del backend (`pip-audit` sobre `App/Backend/requirements.txt`), analisis estatico de seguridad del codigo del backend (SAST) y auditoria de dependencias del frontend (`npm audit` sobre `App/Frontend/package-lock.json`). El job MUST declarar de forma explicita su politica de bloqueo (que hallazgos hacen fallar la corrida) y MUST poder completarse sin secretos del repositorio. El job MUST NOT modificar el arbol de dependencias instalado por los jobs de pruebas.

La politica de bloqueo SHALL ser conservadora y estar justificada: el SAST MUST bloquear ante hallazgos de severidad alta en el codigo del backend; la auditoria de dependencias del backend MUST bloquear ante vulnerabilidades conocidas con una correccion NO rompiente disponible, y MUST ofrecer una via documentada para exceptuar de forma explicita y por ID los hallazgos SIN correccion publicada. Los hallazgos corregibles solo mediante una actualizacion mayor rompiente NO MUST exceptuarse mientras la actualizacion sea viable: MUST resolverse subiendo la dependencia. Si la actualizacion resulta NO viable sin rotura desproporcionada, la excepcion MAY mantenerse con el seguimiento revisado registrado, y el bloqueo MUST seguir siendo explicito y auditable. La auditoria de dependencias del frontend MUST operar en modo reporte (no bloqueante) en esta primera iteracion, con su justificacion registrada. Las excepciones MUST ser explicitas y auditables por ID; NO MUST existir un mecanismo global de omision (por ejemplo `continue-on-error`) que suprima el bloqueo de forma silenciosa.

#### Scenario: El job corre los tres escaneos

- **WHEN** se ejecuta el job de escaneo de seguridad
- **THEN** ejecuta la auditoria de dependencias del backend, el analisis estatico de seguridad del backend y la auditoria de dependencias del frontend

#### Scenario: El job declara su politica de bloqueo

- **WHEN** se inspecciona el job de escaneo de seguridad en `.github/workflows/ci.yml`
- **THEN** deja explicito que el SAST bloquea ante severidad alta, que la auditoria del backend bloquea ante vulnerabilidades con correccion NO rompiente (exceptuando de forma explicita y por ID solo los hallazgos sin correccion publicada) y que la auditoria del frontend es no bloqueante en esta iteracion

#### Scenario: Las excepciones de la auditoria del backend son explicitas y auditables

- **WHEN** se inspecciona la politica de bloqueo de la auditoria de dependencias del backend en `.github/workflows/ci.yml` junto con la lista de excepciones versionada en `scripts/security/pip_audit_exceptions.txt`
- **THEN** cada hallazgo exceptuado figura de forma explicita por ID con su motivo, y no existe ningun `continue-on-error` global que suprima de forma silenciosa el bloqueo

#### Scenario: La lista de excepciones solo contiene hallazgos sin correccion publicada

- **WHEN** se revisa `scripts/security/pip_audit_exceptions.txt` despues del cambio
- **THEN** sus entradas corresponden unicamente a hallazgos sin correccion publicada (`python-jose`, `ecdsa`) y las advisories corregibles solo con una actualizacion mayor rompiente ya no figuran porque la dependencia se subio

#### Scenario: El job no requiere secretos

- **WHEN** se ejecuta el job de escaneo de seguridad en un repositorio sin secretos configurados
- **THEN** completa su corrida analizando los archivos de dependencias y el codigo versionados, sin fallar por falta de credenciales

#### Scenario: El job no altera el arbol de dependencias de las pruebas

- **WHEN** el job de escaneo de seguridad instala herramientas o dependencias para escanear
- **THEN** lo hace en su propio entorno y no modifica el conjunto de dependencias instalado por los jobs de pruebas

#### Scenario: El workflow sigue sin referenciar secretos

- **WHEN** se inspecciona `.github/workflows/ci.yml` despues de agregar el job
- **THEN** no aparece ninguna referencia a `secrets.*` ni variables de entorno con credenciales reales

### Requirement: Workflow opcional de humo del stack de referencia

El repositorio SHALL definir un workflow de GitHub Actions separado de `ci.yml`, `.github/workflows/smoke-stack.yml`, que levante el stack de referencia (`docker-compose.yml` con el override de costo cero del arnes) y ejecute el arnes de `scripts/dry_run/` con los grupos de verificacion vigentes. El workflow SHALL dispararse unicamente de forma manual (`workflow_dispatch`) y por `push` de tags que comiencen con `v`, y MUST NOT dispararse en pull requests. MUST ejecutarse sin secretos: genera en tiempo de ejecucion un `App/Backend/.env` con valores ficticios a partir de la plantilla y certificados autofirmados efimeros, y MUST NOT referenciar `secrets.*`. Las acciones de terceros MUST fijarse a una version mayor explicita. El job MUST declarar un `timeout-minutes` acotado, MUST publicar como artefactos el reporte JSON del arnes y los logs de `docker compose`, y MUST desmontar el stack al terminar, aun ante fallo.

#### Scenario: Disparo manual y por tag de release

- **WHEN** se inspeccionan los disparadores de `.github/workflows/smoke-stack.yml`
- **THEN** solo figuran `workflow_dispatch` y `push` de tags `v*`, y no figura `pull_request`

#### Scenario: Ejecucion sin secretos

- **WHEN** se inspecciona el contenido del workflow de humo
- **THEN** no aparece ninguna referencia a `secrets.*` y los valores de entorno del backend se generan como ficticios durante la corrida

#### Scenario: Evidencia publicada y stack desmontado

- **WHEN** el workflow de humo termina, con exito o con fallo
- **THEN** el reporte JSON del arnes y los logs de `docker compose` quedan publicados como artefactos y el stack queda desmontado

#### Scenario: Acciones fijadas y tiempo acotado

- **WHEN** se inspecciona el workflow de humo
- **THEN** cada `uses:` referencia una version mayor explicita y el job declara `timeout-minutes`

### Requirement: Pruebas offline del arnes en el job de backend

El job `backend-tests` de `.github/workflows/ci.yml` SHALL ejecutar la suite offline del arnes (`python -m pytest scripts/dry_run -q`), que no requiere Docker, red ni secretos, para que la transformacion de costo cero, el modelo de checks y el contrato de exit code no se degraden entre releases.

#### Scenario: El job de backend corre las pruebas del arnes

- **WHEN** se ejecuta el job `backend-tests` en un pull request
- **THEN** corre `python -m pytest scripts/dry_run -q` y el job falla si alguna de esas pruebas falla

#### Scenario: Las pruebas del arnes no requieren servicios externos

- **WHEN** las pruebas del arnes se ejecutan en el runner de CI sin Docker ni red de salida
- **THEN** completan usando solo la biblioteca estandar, los archivos del repositorio y dobles de prueba
