## ADDED Requirements

### Requirement: Credenciales de desarrollo local parametrizadas por entorno

Las credenciales de desarrollo local (password de PostgreSQL y password de autenticacion basica de N8N) SHALL resolverse por variables de entorno con sustitucion `${VAR:-default}` en los archivos compose, de modo que sean sobreescribibles sin editar archivos versionados. Los valores por defecto de las passwords SHALL no ser trivialmente adivinables (no `mesa` ni `admin`). Los valores reales SHALL vivir unicamente en el archivo `.env` gitignorado. Ningun archivo versionado (compose, scripts, CI, tests o documentacion) SHALL hardcodear una credencial real ni un default adivinable de password.

#### Scenario: Sustitucion por variables de entorno en el compose

- **WHEN** se inspeccionan los archivos compose de la raiz y del backend
- **THEN** `POSTGRES_PASSWORD` y `N8N_BASIC_AUTH_PASSWORD` se resuelven con sustitucion `${VAR:-default}` en lugar de un valor literal

#### Scenario: Default de password no adivinable

- **WHEN** se inspecciona el valor por defecto de las passwords en los compose
- **THEN** no es `mesa` ni `admin`, sino valores de desarrollo no trivialmente adivinables

#### Scenario: Override sin editar archivos versionados

- **WHEN** existe un `.env` en la raiz (gitignorado) con un valor propio para una credencial
- **THEN** el compose usa ese valor sin requerir modificar ningun archivo versionado

#### Scenario: Valores reales solo en el .env

- **WHEN** se buscan credenciales reales en archivos versionados
- **THEN** los valores reales residen unicamente en el `.env` gitignorado y no en el arbol versionado

#### Scenario: Script de creacion de base parametrizado

- **WHEN** se ejecuta `scripts/create_db.sql`
- **THEN** requiere el parametro `psql -v db_password=...` y no contiene una password literal

#### Scenario: Credencial efimera de CI no real

- **WHEN** se inspecciona la configuracion de CI
- **THEN** la password efimera del contenedor de servicio es un valor de prueba dedicado y no una credencial real
