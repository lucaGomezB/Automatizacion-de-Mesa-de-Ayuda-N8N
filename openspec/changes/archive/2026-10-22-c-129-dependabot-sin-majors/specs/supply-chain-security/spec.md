## MODIFIED Requirements

### Requirement: Actualizacion automatizada de dependencias con Dependabot

El repositorio SHALL incluir `.github/dependabot.yml` con `version: 2` y una entrada de `updates` por cada ecosistema del stack: `pip` sobre el directorio `/App/Backend`, `npm` sobre el directorio `/App/Frontend` y `github-actions` sobre el directorio raiz (`/`). Cada entrada MUST declarar una programacion recurrente (semanal) y MUST agrupar las actualizaciones para evitar una avalancha de pull requests. Cada entrada MUST excluir las actualizaciones de version mayor (salto de `major`) mediante una regla `ignore` con `dependency-name: "*"` y `update-types` que incluya `version-update:semver-major`, de modo que Dependabot NO abra pull requests de version por saltos de version mayor. La configuracion MUST NOT incluir credenciales ni valores de secretos.

#### Scenario: Existen las tres entradas de ecosistema

- **WHEN** se inspecciona `.github/dependabot.yml`
- **THEN** declara `version: 2` y contiene entradas para `pip` en `/App/Backend`, `npm` en `/App/Frontend` y `github-actions` en `/`

#### Scenario: La programacion es recurrente y las actualizaciones se agrupan

- **WHEN** se lee una entrada de `updates`
- **THEN** su `schedule.interval` es `weekly` y define agrupacion de actualizaciones (`groups`)

#### Scenario: La configuracion no contiene secretos

- **WHEN** se inspecciona `.github/dependabot.yml`
- **THEN** no contiene tokens, claves ni valores de credenciales

#### Scenario: Las actualizaciones de version mayor no se proponen

- **WHEN** se inspecciona la entrada de `updates` de un ecosistema
- **THEN** declara una regla `ignore` con `dependency-name: "*"` y `update-types` que incluye `version-update:semver-major`, de modo que no se abren pull requests de version por saltos de version mayor

#### Scenario: Las actualizaciones menores y de parche siguen proponiendose

- **WHEN** se inspecciona la regla `ignore` de una entrada de `updates`
- **THEN** excluye unicamente `version-update:semver-major` y NO excluye `version-update:semver-minor` ni `version-update:semver-patch`

#### Scenario: Las migraciones de version mayor se gestionan con un change explicito

- **WHEN** una actualizacion de version mayor queda pendiente (por ejemplo sqlalchemy 2.0->2.1 en el backend o React 18->19 en el frontend)
- **THEN** se gestiona mediante un change OpenSpec explicito (por ejemplo c-127 para el backend y c-128 para el frontend), no mediante un pull request automatico de Dependabot
