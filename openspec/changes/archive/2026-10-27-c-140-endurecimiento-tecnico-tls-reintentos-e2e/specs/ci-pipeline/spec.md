## ADDED Requirements

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
