## MODIFIED Requirements

### Requirement: Anexo G — Guía operativa

La guia operativa (`docs/operational-guide.md`) SHALL presentar el comando unico de arranque (`bash scripts/up.sh` en Linux/macOS, `.\scripts\up.ps1` en Windows, o `make up` cuando `make` este disponible) como el camino recomendado para desplegar el stack local, y MUST mantener el camino manual (`openssl/generate-certs.sh` o `openssl/generate-certs.ps1` seguido de `docker compose up -d`) documentado como alternativa. La guia SHALL documentar que el comando unico ejecuta el preflight de costo antes de tocar Docker y que, si el preflight falla, el arranque se bloquea; asimismo MUST documentar el bypass explicito `UP_SKIP_COST_PREFLIGHT=1` y la advertencia audible que el arranque imprime al usarlo. El bloque dotenv de la seccion 1.2 (Configurar variables de entorno) MUST listar `JWT_SECRET_KEY`, ademas de `DATABASE_URL`, `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`, con una descripcion de su proposito como clave de firma HS256. Los comandos y rutas de archivo de la guia MUST referenciar la ubicacion post-reestructuracion del modulo (`App/Backend/`) y MUST NOT presentar `Gestion_Incidentes/` como la ubicacion vigente del modulo, de su `.env` o de sus archivos. La guia SHALL incluir referencias a los scripts automatizados de backup (`scripts/backup.sh` y `scripts/backup.ps1`) como metodo recomendado para backups diarios, reemplazando el comando manual de cron documentado en la seccion 3.

#### Scenario: Despliegue presenta el comando unico como camino recomendado

- **WHEN** se lee la seccion 1.3 (Generar certificados TLS y levantar los servicios) de `docs/operational-guide.md`
- **THEN** el documento referencia el comando unico (`bash scripts/up.sh`, `.\scripts\up.ps1` o `make up`) como camino recomendado
- **AND** describe que ese comando genera los certificados TLS si faltan, levanta el stack y valida la salud

#### Scenario: Gate de costo y bypass documentados en la guia

- **WHEN** se lee la seccion de despliegue de `docs/operational-guide.md`
- **THEN** el documento menciona el preflight de costo que corre antes del arranque
- **AND** documenta el bypass explicito `UP_SKIP_COST_PREFLIGHT=1` y que su uso emite una advertencia audible

#### Scenario: Camino manual permanece documentado

- **WHEN** se lee la seccion 1.3 de la guia operativa
- **THEN** los comandos de generacion manual de certificados (`openssl/generate-certs.sh` / `openssl/generate-certs.ps1`) y `docker compose up -d` siguen documentados como alternativa
- **AND** la guia no afirma que el camino manual sea el recomendado

#### Scenario: Seccion 1.2 lista JWT_SECRET_KEY

- **WHEN** se lee la seccion 1.2 (Configurar variables de entorno) de `docs/operational-guide.md`
- **THEN** el bloque dotenv incluye `JWT_SECRET_KEY` junto a `DATABASE_URL`, `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`
- **AND** describe `JWT_SECRET_KEY` como la clave de firma HS256 e incluye como generarla

#### Scenario: Comandos de la guia usan rutas post-reestructuracion

- **WHEN** se inspeccionan los comandos y rutas de archivo de `docs/operational-guide.md`
- **THEN** referencian `App/Backend/.env`, `App/Backend/requirements.txt` y `App/Backend/` donde corresponde
- **AND** no presentan `Gestion_Incidentes/` como la ubicacion vigente del modulo

#### Scenario: Seccion de backup referencia scripts

- **WHEN** se lee la seccion 3 (Backup y restauracion de PostgreSQL) de `docs/operational-guide.md`
- **THEN** el documento referencia los scripts `scripts/backup.sh` y `scripts/backup.ps1`
- **AND** describe como configurar la ejecucion automatica via cron (Linux/macOS) o Task Scheduler (Windows)
- **AND** incluye el comando de ejemplo para ambos entornos

#### Scenario: Comando manual permanece documentado

- **WHEN** se lee la seccion 3 de la guia operativa
- **THEN** el comando `docker compose exec postgres pg_dump` sigue documentado como alternativa manual
- **AND** la documentacion de restauracion no sufre cambios

### Requirement: README de despliegue local reproducible

El proyecto SHALL actualizar `README.md` con instrucciones de despliegue local que permitan levantar el sistema completo en menos de 15 minutos a partir de un clon limpio, ofreciendo un comando unico de arranque como camino recomendado. Las instrucciones MUST documentar el comando unico (`make up` o, en su defecto, `bash scripts/up.sh` en Linux/macOS y `scripts/up.ps1` en Windows), MUST listar los prerrequisitos (Docker + Docker Compose, OpenSSL para la generacion de certificados, y `make` como conveniencia opcional) incluyendo como obtener `make` en Windows (`choco install make`) o como ejecutar el `.ps1` directamente sin make, y MUST mantener documentado el camino manual (generacion de certificados via `openssl/generate-certs.sh` o `openssl/generate-certs.ps1`, configuracion de `.env` desde la plantilla `.env.example`, y `docker compose up -d`). La tabla de variables de entorno de la seccion "Configurar las variables de entorno" MUST listar `JWT_SECRET_KEY` ademas de `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` y `DATABASE_URL`, con la descripcion de su proposito como clave de firma HS256 y un comando reproducible para generarla. Las instrucciones MUST documentar las condiciones de fallo del comando unico: la ausencia de `App/Backend/.env` y el hecho de que `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` o `JWT_SECRET_KEY` esten ausentes, vacias o conserven los placeholders de la plantilla. Las instrucciones MUST documentar que el comando unico ejecuta el preflight de costo antes de tocar Docker, que un preflight fallido bloquea el arranque, y el bypass explicito `UP_SKIP_COST_PREFLIGHT=1` con su advertencia audible. Las URL de verificacion de salud MUST referenciar `https://localhost/api/v1/health`. La seccion MUST referenciar la guia operativa y la de troubleshooting para procedimientos detallados, e incluir una nota sobre la advertencia de certificado auto-firmado en el navegador.

#### Scenario: README cubre el camino de despliegue local

- **WHEN** se lee la seccion de despliegue local del `README.md`
- **THEN** presenta el comando unico de arranque (`make up` o `bash scripts/up.sh` / `scripts/up.ps1`) como camino recomendado, e incluye prerrequisitos (Docker + Docker Compose, OpenSSL, `make` opcional), generacion de certificados, configuracion de `.env`, el comando `docker compose up -d` y una verificacion de salud con HTTPS, sin contradecir `docker-compose.yml`

#### Scenario: README explica como obtener make en Windows

- **WHEN** se lee la seccion de despliegue local del `README.md`
- **THEN** documenta como instalar `make` en Windows (por ejemplo `choco install make`) o como ejecutar `scripts/up.ps1` directamente sin make

#### Scenario: README documenta la tabla de variables de entorno

- **WHEN** se lee la seccion "Configurar las variables de entorno" del `README.md`
- **THEN** la tabla lista `JWT_SECRET_KEY` ademas de `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` y `DATABASE_URL`
- **AND** describe `JWT_SECRET_KEY` como clave de firma HS256 e incluye un comando para generarla

#### Scenario: README documenta las condiciones de fallo del preflight de entorno

- **WHEN** se lee la descripcion del comando unico en el `README.md`
- **THEN** menciona que el comando falla si `App/Backend/.env` no existe
- **AND** nombra `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` y `JWT_SECRET_KEY` como las variables que no deben estar ausentes, vacias ni conservar placeholders

#### Scenario: README documenta el gate de costo y su bypass

- **WHEN** se lee la descripcion del comando unico en el `README.md`
- **THEN** menciona que el arranque ejecuta un preflight de costo antes de tocar Docker y que un preflight fallido bloquea el arranque
- **AND** documenta el bypass explicito `UP_SKIP_COST_PREFLIGHT=1` y que su uso emite una advertencia audible

#### Scenario: README advierte sobre certificado auto-firmado

- **WHEN** se lee la seccion de despliegue local del `README.md`
- **THEN** incluye una nota explicando que el navegador mostrara una advertencia de seguridad por ser un certificado auto-firmado y que es seguro proceder en el entorno de desarrollo local

#### Scenario: README enlaza la documentacion operativa

- **WHEN** se revisan los enlaces del README
- **THEN** referencia `docs/operational-guide.md` y `docs/troubleshooting.md` para los procedimientos detallados

## ADDED Requirements

### Requirement: Consistencia de rutas post-reestructuracion

La documentacion del proyecto, excluyendo el texto de tesis bajo `docs/Tesis/**`, SHALL referenciar la ubicacion vigente del modulo Python como `App/Backend/` y MUST NOT presentar `Gestion_Incidentes/` como la ubicacion actual del modulo, de su `.env`, de sus modelos, migraciones, clasificadores, scripts o comandos. Un documento MAY conservar la cadena `Gestion_Incidentes/` unicamente cuando narra un hecho historico verificado (por ejemplo, un incidente de seguridad pasado en el que el archivo estaba realmente en esa ruta), y en ese caso MUST anotar de forma explicita que se trata de una ruta historica y cual es la ubicacion vigente. Cada reemplazo de ruta MUST verificarse contra la estructura real del repositorio antes de aplicarse.

#### Scenario: Documentos vigentes referencian la ruta actual

- **WHEN** se inspeccionan `docs/operational-guide.md`, `docs/troubleshooting.md`, `docs/como_cargar_datos_corpus.md`, `docs/diagrams/componentes.md`, `docs/parameters_gemini.md`, `docs/pseudonymization.md` y `docs/anexo_c_esquema_bd.md`
- **THEN** referencian las rutas vigentes bajo `App/Backend/` donde describen la ubicacion del modulo, su `.env`, modelos, migraciones o comandos
- **AND** no presentan `Gestion_Incidentes/` como la ubicacion actual

#### Scenario: La narrativa historica conserva el hecho con anotacion

- **WHEN** se lee `docs/security-hardening.md` en la seccion del caso de estudio de filtracion de la clave Gemini
- **THEN** el hecho documentado (el archivo estaba en `Gestion_Incidentes/.env`) se conserva sin reescribirse
- **AND** la mencion se anota como ruta historica, indicando que hoy el modulo vive en `App/Backend/`

#### Scenario: El texto de tesis queda fuera de alcance

- **WHEN** se inspeccionan los archivos bajo `docs/Tesis/**`
- **THEN** no forman parte del conjunto de documentos corregidos por este requisito
- **AND** cualquier mencion a la estructura antigua en la tesis permanece sin cambios