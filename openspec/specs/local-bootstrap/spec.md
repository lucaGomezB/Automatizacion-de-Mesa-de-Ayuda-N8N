# local-bootstrap Specification

## Purpose
Definir el comportamiento del arranque local del stack completo mediante un unico comando: verificacion previa del entorno, generacion de certificados TLS cuando faltan, arranque y espera de salud de los servicios, verificacion de endpoints de salud y salida de URLs y recordatorios de configuracion manual.

## Requirements

### Requirement: Preflight de entorno con fallo ruidoso

El comando unico de arranque SHALL verificar, antes de tocar Docker, que `App/Backend/.env` existe y que las variables `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `JWT_SECRET_KEY` y `COST_GUARD_CALLER_HMAC_KEY` estan definidas, no vacias y no siguen siendo valores placeholder de la plantilla `App/Backend/.env.example`. Cuando `App/Backend/.env` no existe, o cuando alguna de esas variables esta ausente, vacia o es un placeholder, el comando MUST terminar con exit code distinto de cero sin arrancar el stack, MUST imprimir un mensaje accionable que indique el prerrequisito faltante, y MUST NOT imprimir el valor de ningun secreto. El chequeo de las cuatro variables MUST aplicarse tanto en `scripts/up.sh` como en `scripts/up.ps1`, preservando la equivalencia multiplataforma.

#### Scenario: Archivo .env ausente

- **WHEN** se ejecuta el comando unico y `App/Backend/.env` no existe
- **THEN** el comando termina con exit code distinto de cero, no arranca el stack, e indica que debe copiarse `App/Backend/.env.example` a `App/Backend/.env`

#### Scenario: Variable secreta vacia o placeholder

- **WHEN** `App/Backend/.env` existe pero `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `JWT_SECRET_KEY` o `COST_GUARD_CALLER_HMAC_KEY` esta vacia o conserva el valor placeholder de la plantilla
- **THEN** el comando termina con exit code distinto de cero, identifica la variable problematica y no arranca el stack

#### Scenario: JWT_SECRET_KEY ausente

- **WHEN** `App/Backend/.env` existe, las demas variables secretas son validas, pero `JWT_SECRET_KEY` no esta definida
- **THEN** el comando termina con exit code distinto de cero, nombra `JWT_SECRET_KEY` como el prerrequisito faltante y no arranca el stack

#### Scenario: JWT_SECRET_KEY con placeholder de la plantilla

- **WHEN** `JWT_SECRET_KEY` conserva el valor placeholder definido en `App/Backend/.env.example`
- **THEN** el comando termina con exit code distinto de cero, identifica `JWT_SECRET_KEY` y no arranca el stack

#### Scenario: COST_GUARD_CALLER_HMAC_KEY ausente o con placeholder

- **WHEN** `App/Backend/.env` existe, las demas variables secretas son validas, pero `COST_GUARD_CALLER_HMAC_KEY` no esta definida o conserva el valor placeholder de la plantilla
- **THEN** el comando termina con exit code distinto de cero, identifica `COST_GUARD_CALLER_HMAC_KEY` y no arranca el stack

#### Scenario: Los valores de secretos nunca se muestran

- **WHEN** el preflight detecta cualquier problema con las variables secretas
- **THEN** la salida nombra la variable faltante pero no incluye el valor de la variable ni ningun otro secreto

#### Scenario: Preflight exitoso

- **WHEN** `App/Backend/.env` existe y las cuatro variables secretas requeridas (`GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `JWT_SECRET_KEY` y `COST_GUARD_CALLER_HMAC_KEY`) estan definidas y no son placeholders
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

El comando unico SHALL imprimir, al finalizar con exito, un recordatorio explicito de que el operador debe importar manualmente `n8n/workflow.json` y, en la interfaz de N8N, crear las credenciales IMAP, SMTP, el login del operador y el secreto del webhook de telefonia (ver `docs/n8n-workflow-guide.md`). El recordatorio MUST aclarar que Gemini se configura en el `.env` del backend y no en N8N. El comando MUST NOT intentar importar el workflow de forma automatica.

#### Scenario: Recordatorio presente en la salida exitosa

- **WHEN** el comando termina con exit code cero
- **THEN** la salida incluye el recordatorio de importar `n8n/workflow.json`, de crear las credenciales IMAP, SMTP, el login del operador y el secreto del webhook de telefonia, y aclara que Gemini se configura en el `.env` del backend

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

Las credenciales de desarrollo local (password de PostgreSQL) SHALL resolverse por variables de entorno con sustitucion `${VAR:-default}` en los archivos compose, de modo que sean sobreescribibles sin editar archivos versionados. Los valores por defecto de las passwords SHALL no ser trivialmente adivinables (no `mesa` ni `admin`). Los valores reales SHALL vivir unicamente en el archivo `.env` gitignorado. Ningun archivo versionado (compose, scripts, CI, tests o documentacion) SHALL hardcodear una credencial real ni un default adivinable de password. El acceso a la UI de N8N NO se parametriza por variables de entorno de basic auth (n8n removio Basic Auth en v1.0): se resuelve con la cuenta owner creada en el primer arranque y persistida en el volumen `n8n_data`.

#### Scenario: Sustitucion por variables de entorno en el compose

- **WHEN** se inspeccionan los archivos compose de la raiz y del backend
- **THEN** `POSTGRES_PASSWORD` se resuelve con sustitucion `${VAR:-default}` en lugar de un valor literal

#### Scenario: Default de password no adivinable

- **WHEN** se inspecciona el valor por defecto de la password en los compose
- **THEN** no es `mesa` ni `admin`, sino un valor de desarrollo no trivialmente adivinable

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

### Requirement: Preflight de preparacion de costo antes del arranque

El comando unico de arranque SHALL ejecutar, despues del preflight de entorno y antes de tocar Docker, un preflight estatico de preparacion de costo que verifica las guardas de costo cableadas en `n8n/workflow.json` y `docker-compose.yml`. El preflight SHALL usar unicamente artefactos del repositorio: MUST NOT acceder a red, MUST NOT requerir Docker ni credenciales, y MUST NOT leer ni imprimir la clave `GEMINI_API_KEY` ni ningun otro secreto. La verificacion SHALL implementarse invocando el verificador `scripts/preflight/cost_readiness.py`, cuyo exit code es cero si y solo si todas las guardas estan en PASS. Cuando el verificador termina con exit code distinto de cero, el comando MUST terminar con exit code distinto de cero sin arrancar el stack y MUST imprimir el resumen de guardas, incluidas las que quedaron en FAIL, para diagnostico. `UP_SKIP_COST_PREFLIGHT=1` SHALL ser el unico bypass y MUST ser ruidoso: al definir esa variable el comando omite el gate unicamente si imprime una advertencia explicita; nunca omite el gate en silencio. El gate MUST aplicarse tanto en `scripts/up.sh` como en `scripts/up.ps1`, preservando la equivalencia multiplataforma.

#### Scenario: Guardas de costo en PASS

- **WHEN** el verificador de costo termina con exit code cero porque todas las guardas estan en PASS
- **THEN** el comando imprime el resumen del preflight y continua con el siguiente paso del arranque

#### Scenario: Guarda de costo en FAIL bloquea el arranque

- **WHEN** el verificador de costo termina con exit code distinto de cero porque al menos una guarda esta en FAIL
- **THEN** el comando termina con exit code distinto de cero, imprime el resumen de guardas con las fallidas e informa que el stack NO se arranco

#### Scenario: Preflight de costo estatico sin red ni credenciales

- **WHEN** el comando ejecuta el preflight de costo
- **THEN** el preflight verifica unicamente `n8n/workflow.json` y `docker-compose.yml` sin acceder a red, sin requerir Docker ni credenciales y sin leer ni imprimir ningun secreto

#### Scenario: Falla cerrada ante verificador o interprete ausente

- **WHEN** el script `scripts/preflight/cost_readiness.py` no existe o no hay interprete de Python disponible
- **THEN** el comando termina con exit code distinto de cero, informa la dependencia faltante y no arranca el stack

#### Scenario: Bypass explicito y ruidoso del gate de costo

- **WHEN** se define `UP_SKIP_COST_PREFLIGHT=1`
- **THEN** el comando omite el gate de costo e imprime una advertencia explicita de que el stack puede arrancar con guardas de costo rotas

### Requirement: Preflight de preparacion de Gemini antes del arranque

El comando unico de arranque SHALL ejecutar, en el mismo punto del arranque que el preflight de costo (despues del preflight de entorno y antes de tocar Docker), un preflight estatico de la superficie Gemini del workflow que verifica que el nodo de modelo Gemini declara un `modelName` explicito no vacio y que el nodo agente declara un reintento acotado y explicito. Como la rama de IA de N8N fue retirada, estas guardas SHALL conservarse como verificacion de regresion: SHALL pasar cuando el nodo esta ausente y SHALL fallar solo si el nodo reaparece mal configurado. El preflight SHALL usar unicamente artefactos del repositorio: MUST NOT acceder a red, MUST NOT requerir Docker ni credenciales, y MUST NOT leer ni imprimir `GEMINI_API_KEY` ni ningun otro secreto. La verificacion SHALL implementarse invocando el verificador `scripts/preflight/gemini_readiness.py`, cuyo exit code es cero si y solo si todas las guardas estan en PASS. Cuando el verificador termina con exit code distinto de cero, el comando MUST terminar con exit code distinto de cero sin arrancar el stack y MUST imprimir el resumen de guardas para diagnostico. `UP_SKIP_GEMINI_PREFLIGHT=1` SHALL ser el unico bypass y MUST ser ruidoso: al definir esa variable el comando omite el gate unicamente si imprime una advertencia explicita; nunca omite el gate en silencio. El gate MUST aplicarse tanto en `scripts/up.sh` como en `scripts/up.ps1`, preservando la equivalencia multiplataforma.

#### Scenario: Superficie Gemini en PASS

- **WHEN** el verificador de Gemini termina con exit code cero porque el modelo esta pineado o ausente y el reintento del agente esta acotado o el nodo esta ausente
- **THEN** el comando imprime el resumen del preflight y continua con el siguiente paso del arranque

#### Scenario: Guarda de Gemini en FAIL bloquea el arranque

- **WHEN** el verificador de Gemini termina con exit code distinto de cero porque el nodo de modelo reaparece sin `modelName` explicito o el nodo agente reaparece con un reintento no acotado
- **THEN** el comando termina con exit code distinto de cero, imprime el resumen de guardas e informa que el stack NO se arranco

#### Scenario: Preflight de Gemini estatico sin red ni clave

- **WHEN** el comando ejecuta el preflight de Gemini
- **THEN** el preflight verifica unicamente `n8n/workflow.json` sin acceder a red, sin requerir Docker ni credenciales y sin leer ni imprimir `GEMINI_API_KEY` ni ningun otro secreto

#### Scenario: Falla cerrada ante verificador o interprete ausente

- **WHEN** el script `scripts/preflight/gemini_readiness.py` no existe o no hay interprete de Python disponible
- **THEN** el comando termina con exit code distinto de cero, informa la dependencia faltante y no arranca el stack

#### Scenario: Bypass explicito y ruidoso del gate de Gemini

- **WHEN** se define `UP_SKIP_GEMINI_PREFLIGHT=1`
- **THEN** el comando omite el gate de Gemini e imprime una advertencia explicita de que el stack puede arrancar con un modelo Gemini implicito o sin reintentos acotados
