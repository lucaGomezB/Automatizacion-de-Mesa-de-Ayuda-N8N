# supply-chain-security Specification

## Purpose

Gestion de vulnerabilidades y cadena de suministro del repositorio: mantiene actualizadas las dependencias de forma automatizada, fija las imagenes Docker que publica el stack y deja trazable la politica de pinning y el alcance evaluado y diferido, alineada con ISO/IEC 27002:2022 8.8, 8.28, 8.29 y 5.19-5.23.

## Requirements

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

### Requirement: Imagenes Docker fijadas a versiones explicitas

Toda imagen de contenedor referenciada por `docker-compose.yml` SHALL estar fijada a una version explicita (tag o digest). El archivo MUST NOT usar la etiqueta `latest` ni dejar una imagen sin tag. El pinning MUST preservar el funcionamiento del stack local (`mesa_local`) y MUST registrarse de forma que permita actualizarlo de forma deliberada.

#### Scenario: Nginx queda fijado a una version explicita

- **WHEN** se inspecciona la referencia a la imagen de nginx en `docker-compose.yml`
- **THEN** usa una version explicita y no `nginx:alpine` sin version

#### Scenario: Ngrok queda fijado a una version explicita

- **WHEN** se inspecciona la referencia a la imagen de ngrok en `docker-compose.yml`
- **THEN** usa una version explicita y no `ngrok/ngrok:latest`

#### Scenario: No quedan imagenes flotantes

- **WHEN** se buscan las lineas `image:` de `docker-compose.yml`
- **THEN** ninguna referencia termina en `:latest` ni omite el tag

### Requirement: Politica de pinning de dependencias documentada y conservadora

El repositorio SHALL documentar, en `design.md` del change y en la configuracion versionada que corresponda, la politica de pinning de las dependencias de Python (`App/Backend/requirements.txt`) y de JavaScript (`App/Frontend/package.json`). Las dependencias con rango abierto MUST acotarse o justificarse explicitamente; la politica MUST preferir la mejora mas segura que no rompa el build antes que convertir todos los rangos en pins duros. `App/Frontend/package-lock.json` MUST permanecer versionado y la instalacion reproducible MUST usar `npm ci`. La politica MUST distinguir las dependencias sensibles (criptografia, autenticacion, SDK de inferencia) del resto.

#### Scenario: Los rangos abiertos quedan acotados o justificados

- **WHEN** se revisan las dependencias de `App/Backend/requirements.txt` que usan `>=` sin limite superior
- **THEN** cada una tiene un limite superior de compatibilidad o una justificacion documentada de por que se deja abierta

#### Scenario: La instalacion del frontend es reproducible

- **WHEN** se inspecciona `App/Frontend/`
- **THEN** `package-lock.json` esta versionado y el workflow de CI instala con `npm ci`

#### Scenario: La politica distingue dependencias sensibles

- **WHEN** se lee la politica de pinning en `design.md`
- **THEN** identifica las dependencias sensibles (criptografia, autenticacion, SDK de inferencia) y su tratamiento

### Requirement: Alcance evaluado y diferido registrado

El repositorio SHALL registrar en `design.md` del change las capacidades de cadena de suministro evaluadas y diferidas, con su motivo. Como minimo MUST registrar el escaneo de imagenes (trivy) y la generacion de SBOM como evaluados y diferidos. El registro MUST NOT declarar implementadas esas capacidades.

#### Scenario: Trivy y SBOM figuran como diferidos

- **WHEN** se lee `design.md` del change
- **THEN** trivy y SBOM aparecen como evaluados y diferidos, con el motivo de la decision y sin declararlos implementados

### Requirement: Resolucion de excepciones de auditoria con correccion rompiente

El repositorio SHALL resolver las excepciones de la auditoria de dependencias del backend que solo sean corregibles mediante una actualizacion mayor rompiente, subiendo las dependencias afectadas de forma que la lista de excepciones de `scripts/security/pip_audit_exceptions.txt` contenga unicamente hallazgos SIN correccion publicada. Las dependencias afectadas SHALL subirse a versiones que resuelvan las advisories de `starlette` y de `pytest` registradas como seguimiento en c-64. Cuando la actualizacion mayor NO sea viable sin una rotura desproporcionada, la excepcion MAY mantenerse, pero el `design.md` del change MUST registrar la conclusion con evidencia y MUST dejar un seguimiento revisado.

#### Scenario: Las advisories de starlette y pytest quedan resueltas

- **WHEN** se corre `pip-audit -r App/Backend/requirements.txt` contra los pins actualizados
- **THEN** ninguna de las 7 advisories de `starlette` (PYSEC-2026-161/249/248/1943/1941/2281/2280) ni `PYSEC-2026-1845` de `pytest` figura como hallazgo exceptuado, porque `starlette` resuelve a una version al menos `1.3.1` y `pytest` a 9.x

#### Scenario: La lista de excepciones solo conserva hallazgos sin correccion publicada

- **WHEN** se inspecciona `scripts/security/pip_audit_exceptions.txt`
- **THEN** sus entradas por ID corresponden solo a `python-jose` y `ecdsa`, cada una con su motivo de "sin correccion publicada", y no quedan entradas de `starlette` ni de `pytest`

#### Scenario: La matriz de versiones y la compatibilidad quedan registradas

- **WHEN** se lee el `design.md` del change
- **THEN** registra las versiones objetivo exactas de `fastapi`, `starlette`, `pytest` y `pytest-asyncio`, la restriccion de compatibilidad que las vincula y el plan de rollback

#### Scenario: Fallback documentado cuando la actualizacion no es viable

- **WHEN** la actualizacion mayor resulta NO viable sin rotura desproporcionada
- **THEN** el `design.md` registra esa conclusion con evidencia y la excepcion permanece con un seguimiento revisado, sin declarar resuelta la advisory
