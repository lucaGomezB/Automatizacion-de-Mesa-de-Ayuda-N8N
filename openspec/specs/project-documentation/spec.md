## Purpose

This specification defines the documentation artifacts required for the Mesa de Ayuda project: architecture diagrams, OpenAPI specification, database schema reference, evaluation corpus description, operational guide, troubleshooting guide, and README deployment instructions. Every artifact must be reproducible, version-controlled, and kept in sync with the live system configuration.

## Requirements

### Requirement: Diagramas de arquitectura UML

El proyecto SHALL incluir, bajo `docs/diagrams/`, tres diagramas de arquitectura en notación UML mantenidos como fuente de texto versionable (Mermaid): un diagrama de despliegue, un diagrama de secuencia y un diagrama de componentes. El diagrama de despliegue MUST representar los componentes de infraestructura reales declarados en `docker-compose.yml` (PostgreSQL, Redis, backend FastAPI, N8N) y sus relaciones de comunicación. El diagrama de secuencia MUST ilustrar el flujo extremo a extremo de un incidente desde su recepción en un canal de entrada hasta la confirmación al usuario. El diagrama de componentes MUST reflejar la organización en capas del módulo Python (routes, services, repositories, classifiers, models). Cada archivo de diagrama MUST contener un bloque de código Mermaid sintácticamente válido.

#### Scenario: Los tres diagramas existen y son válidos

- **WHEN** se inspecciona el directorio `docs/diagrams/`
- **THEN** existen los tres diagramas (despliegue, secuencia, componentes), cada uno con un bloque Mermaid sintácticamente parseable

#### Scenario: El diagrama de despliegue refleja la infraestructura real

- **WHEN** se compara el diagrama de despliegue contra `docker-compose.yml`
- **THEN** los cuatro servicios de infraestructura (postgres, redis, backend, n8n) aparecen como nodos del diagrama, sin inventar componentes inexistentes

### Requirement: Especificación OpenAPI 3.1 estática generada desde la app

El proyecto SHALL publicar la especificación OpenAPI 3.1 de la interfaz REST en `docs/openapi.json`, generada **desde la aplicación FastAPI** (`app.main:app`) mediante un script reproducible, nunca escrita a mano. El documento MUST declarar versión OpenAPI `3.1.x` y MUST contener los puntos de entrada efectivamente expuestos por la app (incidentes, clasificaciones, health). El script de generación MUST poder ejecutarse en un entorno limpio, sin base de datos en ejecución y sin variables de entorno reales, inyectando dummies suficientes para instanciar `Settings`; ese conjunto MUST incluir explícitamente `JWT_SECRET_KEY`, además de `DATABASE_URL`, `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`. El uso documentado del script (docstring) MUST referenciar las rutas vigentes bajo `App/Backend/`, MUST NOT presentar `Gestion_Incidentes/` como ubicación del módulo ni de sus comandos, y su ejemplo de `--output` MUST ser consistente con la ruta de salida por defecto real del script.

#### Scenario: openapi.json es un OpenAPI 3.1 bien formado

- **WHEN** se carga `docs/openapi.json`
- **THEN** es JSON válido, su campo `openapi` comienza con `3.1`, y contiene un objeto `paths` no vacío con las rutas bajo `/api/v1`

#### Scenario: El spec se genera desde la app, no a mano

- **WHEN** se ejecuta el script de generación apuntando a `app.main:app`
- **THEN** produce un `openapi.json` cuyos `paths` coinciden con los `@router` declarados en `App/Backend/app/routes/`

#### Scenario: El script corre con dummies suficientes, sin JWT_SECRET_KEY real

- **WHEN** se ejecuta el script de generación en un entorno sin `JWT_SECRET_KEY` definida y sin un `.env` descubrible, apuntando a una salida temporal
- **THEN** termina con código de salida 0 y produce un documento OpenAPI 3.1 válido, sin fallar la validación de `Settings`

#### Scenario: El uso documentado del script no referencia la ruta obsoleta

- **WHEN** se inspecciona el docstring de `App/Backend/scripts/export_openapi.py`
- **THEN** los comandos y rutas que documenta referencian `App/Backend/` y su ejemplo de `--output` es consistente con la salida por defecto real
- **AND** no presenta `Gestion_Incidentes` como ubicación del módulo, de su `.env` ni de sus archivos

### Requirement: Verificación de sincronía de openapi.json

El proyecto SHALL proveer una verificación que falle cuando `docs/openapi.json` quede desactualizado respecto del esquema que la app FastAPI genera en el momento. La verificación MUST regenerar el esquema en memoria y compararlo contra el archivo commiteado, y MUST poder ejecutarse en CI siguiendo el patrón de jobs de C-09.

#### Scenario: Spec en sincronía pasa la verificación

- **WHEN** `docs/openapi.json` coincide con el esquema generado por la app
- **THEN** la verificación termina con éxito (exit code 0)

#### Scenario: Spec desactualizado falla la verificación

- **WHEN** la app expone un endpoint que `docs/openapi.json` no contiene (o viceversa)
- **THEN** la verificación falla con un mensaje accionable que indica regenerar el archivo

### Requirement: Anexo C — Esquema de base de datos

El proyecto SHALL incluir `docs/anexo_c_esquema_bd.md` con el script SQL completo de las tablas del modelo de datos (`sector`, `estado`, `canal_origen`, `incidente`, `clasificacion_log`) más las estructuras de persistencia multietiqueta incorporadas por la migración `004` (tabla de unión de sectores adicionales del incidente y las estructuras de los conjuntos predicho/validado del log de clasificación), derivado fielmente de los modelos ORM en `App/Backend/app/models/`. El documento MUST declarar, por cada tabla, sus columnas con tipos, las claves primarias, las claves foráneas con su acción `ON DELETE` real (`SET NULL`, `RESTRICT`, `CASCADE`), las restricciones de unicidad y los índices secundarios e índices compuestos definidos en el código. El documento MUST documentar la doble representación de la descripción (`descripcion_original` cifrada at-rest, `descripcion_pseudonimizada` en claro) conforme a la arquitectura de pseudonimización.

#### Scenario: Las cinco tablas están definidas
- **WHEN** se inspecciona `docs/anexo_c_esquema_bd.md`
- **THEN** contiene sentencias `CREATE TABLE` para `sector`, `estado`, `canal_origen`, `incidente` y `clasificacion_log`, y ninguna tabla inventada fuera de ese conjunto más las estructuras multietiqueta de la migración `004`

#### Scenario: Las estructuras multietiqueta están documentadas
- **WHEN** se inspeccionan las tablas documentadas en el anexo
- **THEN** aparece la tabla de unión de sectores adicionales del incidente con sus claves foráneas a `incidente` y `sector`, y la representación de los conjuntos predicho/validado del log

#### Scenario: Las claves foráneas reflejan el comportamiento ON DELETE real
- **WHEN** se comparan las FKs documentadas contra los modelos ORM
- **THEN** `incidente.estado_id` usa `RESTRICT`, `incidente.sector_id` y `incidente.canal_origen_id` usan `SET NULL`, y `clasificacion_log.incidente_id` usa `CASCADE`

#### Scenario: Los índices compuestos del incidente están documentados
- **WHEN** se revisan los índices declarados en el anexo
- **THEN** aparecen los índices compuestos `(created_at, sector_id)` y `(estado_id, created_at)` de la tabla `incidente`

### Requirement: Anexo F — Corpus de validación

El proyecto SHALL incluir `docs/anexo_f_corpus.md` describiendo el corpus de validación en su formato JSON (`schema_version`, `metadata`, `casos` con `id`, `descripcion`, `canal_origen`, `sector_asignado`, `sectores_adicionales`, `tiempo_manual_s` y `tiempo_automatizado_s`), el conjunto exacto de cinco categorías canónicas (`Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`) y las invariantes de la verdad multietiqueta. El documento MUST declarar que el corpus sintético de 200 casos fue descartado y eliminado del proyecto, y MUST NOT presentar datos sintéticos como resultados experimentales reales.

#### Scenario: Esquema y categorías documentados
- **WHEN** se inspecciona `docs/anexo_f_corpus.md`
- **THEN** describe los campos JSON `sector_asignado` y `sectores_adicionales` y enumera las cinco categorías canónicas exactas, consistentes con el contrato del framework de evaluación

#### Scenario: Naturaleza multietiqueta documentada
- **WHEN** se lee la sección sobre la estructura del corpus
- **THEN** declara que `sectores_adicionales` es requerido, que no repite el sector asignado y que todos los valores pertenecen al conjunto canónico

#### Scenario: Naturaleza provisional declarada explícitamente
- **WHEN** se lee la sección sobre la procedencia del corpus
- **THEN** afirma de forma inequívoca que el corpus sintético de 200 casos fue descartado por los revisores y eliminado del repositorio

### Requirement: Anexo G — Guía operativa

La guia operativa (`docs/operational-guide.md`) SHALL presentar el comando unico de arranque (`bash scripts/up.sh` en Linux/macOS, `.\scripts\up.ps1` en Windows, o `make up` cuando `make` este disponible) como el camino recomendado para desplegar el stack local, y MUST mantener el camino manual (`openssl/generate-certs.sh` o `openssl/generate-certs.ps1` seguido de `docker compose up -d`) documentado como alternativa. La guia SHALL documentar que el comando unico ejecuta el preflight de costo antes de tocar Docker y que, si el preflight falla, el arranque se bloquea; asimismo MUST documentar el bypass explicito `UP_SKIP_COST_PREFLIGHT=1` y la advertencia audible que el arranque imprime al usarlo. El bloque dotenv de la seccion 1.2 (Configurar variables de entorno) MUST listar `JWT_SECRET_KEY`, ademas de `DATABASE_URL`, `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`, con una descripcion de su proposito como clave de firma HS256. Los comandos y rutas de archivo de la guia MUST referenciar la ubicacion post-reestructuracion del modulo (`App/Backend/`) y MUST NOT presentar `Gestion_Incidentes/` como la ubicacion vigente del modulo, de su `.env` o de sus archivos. La guia SHALL incluir referencias a los scripts automatizados de backup (`scripts/backup.sh` y `scripts/backup.ps1`) como metodo recomendado para backups diarios, reemplazando el comando manual de cron documentado en la seccion 3. La seccion 8 (Evaluacion del clasificador) MUST documentar la invocacion real del runner desde la raiz del repositorio (`PYTHONPATH=App/Backend python -m evaluation.run_evaluation`), MUST NOT indicar `python run_evaluation.py` ni un `cd evaluation` que no resuelva los imports del paquete, MUST NOT referenciar `evaluation/generate_corpus.py` ni afirmar la existencia de un generador de corpus con seed fijo, y MUST apuntar al procedimiento real de carga del corpus documentado en `docs/como_cargar_datos_corpus.md`. La seccion 8 MUST documentar el gate de corrida paga del runner: que una corrida que invocaria el clasificador real exige confirmacion explicita con `--confirm-paid` o `EVALUATION_CONFIRM_PAID=1`, que sin confirmacion aborta con codigo de salida 2, y que al confirmar se imprime una estimacion de costo.

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

#### Scenario: Seccion 8 usa la invocacion real del runner

- **WHEN** se lee la seccion 8 (Evaluacion del clasificador) de `docs/operational-guide.md`
- **THEN** el comando de corrida documentado es `PYTHONPATH=App/Backend python -m evaluation.run_evaluation`, ejecutado desde la raiz del repositorio
- **AND** el documento no presenta `python run_evaluation.py` ni un `cd evaluation` como forma de invocacion

#### Scenario: Seccion 8 no referencia el generador de corpus eliminado

- **WHEN** se inspecciona la seccion 8 de `docs/operational-guide.md`
- **THEN** el documento no referencia `evaluation/generate_corpus.py` ni afirma un generador de corpus con seed fijo
- **AND** apunta al procedimiento real de carga del corpus en `docs/como_cargar_datos_corpus.md`

#### Scenario: Gate de corrida paga documentado en la guia

- **WHEN** se lee la seccion 8 de `docs/operational-guide.md`
- **THEN** el documento menciona que una corrida que invocaria el clasificador real exige confirmacion explicita con `--confirm-paid` o `EVALUATION_CONFIRM_PAID=1`
- **AND** documenta que sin confirmacion la corrida aborta con codigo de salida 2 y que al confirmar se imprime una estimacion de costo

### Requirement: Guía de troubleshooting para operadores

El proyecto SHALL incluir `docs/troubleshooting.md` con una guía de resolución de problemas dirigida a operadores, organizada por síntoma. Cada entrada MUST describir un síntoma observable, su causa probable y los pasos de remediación. La guía MUST cubrir como mínimo los fallos operativos previsibles del stack (servicio que no levanta, base de datos no disponible, clasificación que cae a revisión humana por baja confianza, fallo de Gemini).

#### Scenario: Entradas estructuradas por síntoma

- **WHEN** se inspecciona `docs/troubleshooting.md`
- **THEN** cada entrada presenta síntoma, causa probable y remediación, cubriendo al menos los fallos del backend, de la base de datos y del clasificador

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

### Requirement: DOC-002 — Tesis v8 K8s language verified

La tesis en version 8 (LaTeX) SHALL mantener el lenguaje suavizado sobre Kubernetes: "preparados para migracion" (futuro), no "mediante un cluster Kubernetes" (presente). Este requisito es de VERIFICACION unicamente.

#### Scenario: Lenguaje K8s es futuro, no presente
- **WHEN** se inspecciona `docs/Tesis/v8 (IA)/paper/sections/06-implementacion.tex` linea 8
- **THEN** el texto contiene "preparados para migracion a un cluster Kubernetes~1.30"
- **AND** NO contiene frases que afirmen que Kubernetes esta desplegado actualmente ("mediante un cluster", "se despliega en Kubernetes")

### Requirement: DOC-003 — Anexo G referencia scripts de backup

La documentacion operativa del Anexo G en la tesis SHALL mencionar la existencia de scripts automatizados de backup con retencion de 7 dias.

#### Scenario: Anexo G menciona backup automatizado
- **WHEN** se lee la seccion del Anexo G en la tesis v8
- **THEN** el texto menciona que existen scripts de backup automatizados (`backup.sh` y `backup.ps1`)
- **AND** describe la politica de retencion (7 backups diarios)

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
