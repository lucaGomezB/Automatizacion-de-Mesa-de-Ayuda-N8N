## Purpose

Gestion de vulnerabilidades y cadena de suministro del repositorio: mantiene actualizadas las dependencias de forma automatizada, fija las imagenes Docker que publica el stack y deja trazable la politica de pinning y el alcance evaluado y diferido, alineada con ISO/IEC 27002:2022 8.8, 8.28, 8.29 y 5.19-5.23.

## ADDED Requirements

### Requirement: Actualizacion automatizada de dependencias con Dependabot

El repositorio SHALL incluir `.github/dependabot.yml` con `version: 2` y una entrada de `updates` por cada ecosistema del stack: `pip` sobre el directorio `/App/Backend`, `npm` sobre el directorio `/App/Frontend` y `github-actions` sobre el directorio raiz (`/`). Cada entrada MUST declarar una programacion recurrente (semanal) y MUST agrupar las actualizaciones para evitar una avalancha de pull requests. La configuracion MUST NOT incluir credenciales ni valores de secretos.

#### Scenario: Existen las tres entradas de ecosistema

- **WHEN** se inspecciona `.github/dependabot.yml`
- **THEN** declara `version: 2` y contiene entradas para `pip` en `/App/Backend`, `npm` en `/App/Frontend` y `github-actions` en `/`

#### Scenario: La programacion es recurrente y las actualizaciones se agrupan

- **WHEN** se lee una entrada de `updates`
- **THEN** su `schedule.interval` es `weekly` y define agrupacion de actualizaciones (`groups`)

#### Scenario: La configuracion no contiene secretos

- **WHEN** se inspecciona `.github/dependabot.yml`
- **THEN** no contiene tokens, claves ni valores de credenciales

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
