# local-bootstrap Specification

## Purpose
Definir el comportamiento del arranque local del stack completo mediante un unico comando: verificacion previa del entorno, generacion de certificados TLS cuando faltan, arranque y espera de salud de los servicios, verificacion de endpoints de salud y salida de URLs y recordatorios de configuracion manual.

## Requirements

### Requirement: Preflight de entorno con fallo ruidoso

El comando unico de arranque SHALL verificar, antes de tocar Docker, que `App/Backend/.env` existe y que las variables `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` y `JWT_SECRET_KEY` estan definidas, no vacias y no siguen siendo valores placeholder de la plantilla `App/Backend/.env.example`. Cuando `App/Backend/.env` no existe, o cuando alguna de esas variables esta ausente, vacia o es un placeholder, el comando MUST terminar con exit code distinto de cero sin arrancar el stack, MUST imprimir un mensaje accionable que indique el prerrequisito faltante, y MUST NOT imprimir el valor de ningun secreto. El chequeo de `JWT_SECRET_KEY` MUST aplicarse tanto en `scripts/up.sh` como en `scripts/up.ps1`, preservando la equivalencia multiplataforma.

#### Scenario: Archivo .env ausente

- **WHEN** se ejecuta el comando unico y `App/Backend/.env` no existe
- **THEN** el comando termina con exit code distinto de cero, no arranca el stack, e indica que debe copiarse `App/Backend/.env.example` a `App/Backend/.env`

#### Scenario: Variable secreta vacia o placeholder

- **WHEN** `App/Backend/.env` existe pero `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` o `JWT_SECRET_KEY` esta vacia o conserva el valor placeholder de la plantilla
- **THEN** el comando termina con exit code distinto de cero, identifica la variable problematica y no arranca el stack

#### Scenario: JWT_SECRET_KEY ausente

- **WHEN** `App/Backend/.env` existe, las demas variables secretas son validas, pero `JWT_SECRET_KEY` no esta definida
- **THEN** el comando termina con exit code distinto de cero, nombra `JWT_SECRET_KEY` como el prerrequisito faltante y no arranca el stack

#### Scenario: JWT_SECRET_KEY con placeholder de la plantilla

- **WHEN** `JWT_SECRET_KEY` conserva el valor placeholder definido en `App/Backend/.env.example`
- **THEN** el comando termina con exit code distinto de cero, identifica `JWT_SECRET_KEY` y no arranca el stack

#### Scenario: Los valores de secretos nunca se muestran

- **WHEN** el preflight detecta cualquier problema con las variables secretas
- **THEN** la salida nombra la variable faltante pero no incluye el valor de la variable ni ningun otro secreto

#### Scenario: Preflight exitoso

- **WHEN** `App/Backend/.env` existe y las variables secretas requeridas, incluida `JWT_SECRET_KEY`, estan definidas y no son placeholders
- **THEN** el comando continua con el arranque del stack

### Requirement: Generacion automatica de certificados TLS cuando faltan

El comando unico SHALL verificar la existencia de `openssl/mesa.crt` y `openssl/mesa.key`; si cualquiera de los dos falta, MUST invocar el generador de certificados existente (`openssl/generate-certs.sh` en Linux/macOS o `openssl/generate-certs.ps1` en Windows) antes de arrancar el stack. Si los certificados ya existen, el comando MUST NOT regenerarlos.

#### Scenario: Certificados ausentes

- **WHEN** se ejecuta el comando unico y al menos uno de `openssl/mesa.crt` o `openssl/mesa.key` no existe
- **THEN** el comando invoca el generador correspondiente al sistema operativo y continua solo si la generacion termina con exito

#### Scenario: Certificados presentes

- **WHEN** se ejecuta el comando unico y `openssl/mesa.crt` y `openssl/mesa.key` ya existen
- **THEN** el comando no invoca el generador y continua con el arranque

#### Scenario: Fallo del generador de certificados

- **WHEN** el generador de certificados falla
- **THEN** el comando termina con exit code distinto de cero e informa que la generacion de certificados TLS no se pudo completar

### Requirement: Arranque del stack y espera de salud acotada

El comando unico SHALL arrancar el stack con `docker compose up -d --build` sin pasar `-p` (el nombre de proyecto esta fijado a `mesa_local` en `docker-compose.yml`). Luego MUST consultar el estado con `docker compose ps` de forma repetida hasta que los servicios queden sanos o hasta agotar un timeout acotado. Si el timeout se agota sin que los servicios esten sanos, el comando MUST terminar con exit code distinto de cero e imprimir el estado observado para diagnostico.

#### Scenario: Arranque exitoso

- **WHEN** `docker compose up -d --build` termina y los servicios alcanzan el estado sano dentro del timeout
- **THEN** el comando continua con la verificacion de salud

#### Scenario: Timeout de salud agotado

- **WHEN** los servicios no alcanzan el estado sano antes de agotar el timeout
- **THEN** el comando termina con exit code distinto de cero e imprime el estado de los servicios para diagnostico

#### Scenario: Nombre de proyecto fijado

- **WHEN** el comando invoca `docker compose`
- **THEN** no incluye el flag `-p` y opera sobre el proyecto `mesa_local` declarado en `docker-compose.yml`

### Requirement: Verificacion de salud y salida de acceso

Una vez que los servicios estan sanos, el comando unico SHALL verificar `curl -k https://localhost/api/v1/health` y `curl -k https://localhost/api/v1/health/db`; si cualquiera de las dos verificaciones falla, el comando MUST terminar con exit code distinto de cero e informar el endpoint que fallo. Cuando ambas verificaciones pasan, el comando MUST imprimir las URLs de acceso: interfaz web `https://localhost/` y N8N `http://localhost:5678` (credenciales configuradas en el entorno, sin hardcodear valores en el repo).

#### Scenario: Ambos endpoints de salud responden

- **WHEN** las peticiones a `https://localhost/api/v1/health` y `https://localhost/api/v1/health/db` responden con exito
- **THEN** el comando imprime las URLs de acceso de la interfaz web y de N8N y termina con exit code cero

#### Scenario: Endpoint de salud falla

- **WHEN** alguna de las dos verificaciones de salud no responde con exito
- **THEN** el comando termina con exit code distinto de cero e identifica el endpoint que fallo

### Requirement: Recordatorio manual de configuracion de N8N

El comando unico SHALL imprimir, al finalizar con exito, un recordatorio explicito de que el operador debe importar manualmente `n8n/workflow.json` y configurar las credenciales de Outlook, Twilio y Gemini en la interfaz de N8N. El comando MUST NOT intentar importar el workflow de forma automatica.

#### Scenario: Recordatorio presente en la salida exitosa

- **WHEN** el comando termina con exit code cero
- **THEN** la salida incluye el recordatorio de importar `n8n/workflow.json` y de configurar las credenciales de Outlook, Twilio y Gemini

#### Scenario: Sin importacion automatica

- **WHEN** el comando arranca el stack
- **THEN** no ejecuta ninguna importacion de `n8n/workflow.json` ni crea workflows en N8N

### Requirement: Equivalencia multiplataforma y alias opcional

El comando unico SHALL estar disponible como `scripts/up.sh` (bash, Linux/macOS) y `scripts/up.ps1` (PowerShell, Windows) con comportamiento equivalente segun los requisitos anteriores. Adicionalmente, la raiz del repositorio SHALL ofrecer un `Makefile` opcional con objetivos `up`, `down`, `ps`, `logs` y `health` que detecten el sistema operativo y deleguen en el script pareado correspondiente; los scripts MUST seguir siendo ejecutables directamente sin Make.

#### Scenario: Ambos scripts ofrecen el mismo flujo

- **WHEN** se ejecuta `bash scripts/up.sh` en Linux/macOS o `scripts/up.ps1` en Windows
- **THEN** cada script aplica el mismo preflight, generacion de certificados, arranque, espera de salud, verificacion y recordatorios definidos en esta capacidad

#### Scenario: Make delega en el script del sistema operativo

- **WHEN** se ejecuta `make up` sobre un sistema con `make` disponible
- **THEN** el objetivo detecta el sistema operativo e invoca `scripts/up.sh` en Linux/macOS o `scripts/up.ps1` en Windows

#### Scenario: Make es opcional

- **WHEN** un operador ejecuta el script pareado directamente sin tener `make` instalado
- **THEN** el flujo de arranque completo funciona igualmente

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
