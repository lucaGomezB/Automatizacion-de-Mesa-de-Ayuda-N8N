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

### Requirement: DOC-004 — Descripcion del gate de revision y del cortocircuito sincronizada con el comportamiento

La configuracion para agentes (`openspec/config.yaml`, `CLAUDE.md`), la base de conocimiento (`knowledge-base/`) y los comentarios de los clasificadores (`App/Backend/app/classifiers/hybrid.py`, `deterministic.py` y `gemini_classifier.py`) SHALL describir el gate de revision humana y el cortocircuito conforme a `Settings` y al codigo: el cortocircuito deterministico se decide por `score_correctitud >= deterministic_score_threshold` con senal dominante; `human_review_threshold` (0.70) se aplica solo a la salida de Gemini; la etapa fallback marca revision siempre con confianza 0.0; la etapa deterministica no marca revision por su confianza; y el backend tambien deriva a revision ante un reportante no identificado. Ninguno de esos artefactos MUST declarar un umbral de cortocircuito de 0.90 sobre la confianza ni un umbral de 0.70 aplicable a toda clasificacion. Los cambios en los clasificadores MUST limitarse a comentarios y docstrings, sin alterar el comportamiento. El contrato SHALL quedar fijado por un test que verifique que el cortocircuito deterministico no marca revision aunque la confianza sea inferior a 0.70.

#### Scenario: Umbrales declarados en la configuracion del proyecto

- **WHEN** se lee `conventions.thresholds` en `openspec/config.yaml`
- **THEN** declara el punto de operacion del score de correctitud (0.5166) y el umbral de revision (0.70) con su alcance
- **AND** no declara un umbral deterministico de 0.90

#### Scenario: Instrucciones para agentes alineadas

- **WHEN** se leen las lineas de `CLAUDE.md` que describen el umbral de confianza y los nodos IF del flujo
- **THEN** describen el alcance del gate por etapa y el cortocircuito por score de correctitud
- **AND** distinguen el IF de validacion de entrada previo al POST del IF que evalua el indicador del backend

#### Scenario: Base de conocimiento sin reglas retiradas

- **WHEN** se busca en `knowledge-base/` un umbral de 0,90 como criterio de cortocircuito o un umbral de 0,70 aplicado a toda clasificacion
- **THEN** no aparece como regla, decision ni flujo vigente

#### Scenario: Docstrings coherentes y sin cambio de comportamiento

- **WHEN** se leen los docstrings y comentarios de los tres clasificadores
- **THEN** no afirman un umbral de cortocircuito de 0.90 ni que la revision humana se evalue para cualquier etapa
- **AND** el arbol sintactico de cada archivo, sin docstrings, es identico al previo al change

#### Scenario: Contrato fijado por test de caracterizacion

- **WHEN** se ejecuta el test con un resultado deterministico cuyo score alcanza el punto de operacion y cuya confianza vale 0.0, 1/6 o 0.5
- **THEN** el resultado tiene `etapa == "deterministic"` y `requiere_revision_humana is False`
- **AND** la etapa Gemini no se invoca

### Requirement: DOC-005 — Stack declarado en la documentacion para agentes sincronizado con el codigo

La documentacion que heredan los agentes (`CLAUDE.md` y `openspec/config.yaml`), la base de conocimiento (`knowledge-base/**`) y el material de referencia que esos documentos alcanzan (`docs/parameters_gemini.md` y `docs/n8n-workflow-guide.md`) SHALL declarar solo valores de stack que se puedan reproducir desde el codigo o desde los archivos de dependencias: el modelo de inferencia y sus parametros desde `App/Backend/app/config/settings.py`, los umbrales de decision desde el mismo `Settings`, el conjunto canonico de sectores desde `App/Backend/app/constants.py`, y las versiones de framework y librerias desde `App/Backend/requirements.txt` y `docker-compose.yml`. Ningun valor MUST provenir de otro documento, y ningun valor retirado MUST citarse como vigente.

El flujo de clasificacion y los servicios de infraestructura que esos documentos describan MUST existir en el repositorio; una etapa o un servicio que ya no existe MUST retirarse o declararse historico, no describirse como vigente.

Las versiones de componentes que declaren `knowledge-base/**` y el material de referencia (`docs/parameters_gemini.md`) SHALL coincidir con la misma fuente de verdad que usan `CLAUDE.md` y `openspec/config.yaml`: FastAPI, Uvicorn y la restriccion de `google-genai` desde `App/Backend/requirements.txt`, y la version de N8N desde la imagen pinneada de `docker-compose.yml`. En particular, la restriccion de `google-genai` declarada en `docs/parameters_gemini.md` MUST ser al menos tan estricta como el pin de `App/Backend/requirements.txt`; una restriccion mas laxa (por ejemplo `>=2.31,<3` frente al pin `>=2.33.0,<3`) MUST reportarse como hallazgo. Una version de componente retirada MUST NOT presentarse como vigente; solo se admite en un pasaje rotulado como historico. El marcador historico MUST identificar el hecho historico que rotula y MUST NOT inferirse de una palabra que en el mismo pasaje describa otra cosa: en particular, la mencion de que el SDK `google-generativeai` esta deprecado no convierte en historica una mencion del modelo retirado en esa misma linea.

Cada valor volatil MUST tener una sola fuente declarada: cuando `CLAUDE.md` repita un valor que ya vive en `openspec/config.yaml`, MUST remitir a esa seccion en lugar de restatear el literal, para que la superficie vigilada no tenga dos copias que puedan divergir. La unica excepcion es el nombre del modelo, que se declara en ambos documentos y se verifica por coincidencia con `Settings.gemini_model`.

Los hechos historicos documentados SHALL conservarse y rotularse de forma explicita como historicos, sin presentarse como el valor vigente. En particular, la calibracion empirica de los parametros de generacion realizada sobre `gemini-2.5-flash` y la decision DD-04 de `knowledge-base/09_decisiones_y_supuestos.md` son hechos historicos declarados que SHALL permanecer citables, rotulados como antecedente, mientras que el valor vigente (`gemini-3.6-flash`, timeout 30 s por intento, 60 s total y 2 reintentos, con `google-genai >=2.33,<3`) SHALL ser el que la documentacion declare como actual. Un pasaje que mencione el modelo retirado MUST distinguir de forma explicita el valor vigente del hecho historico y MUST NOT afirmar un invariante de tiempos que el valor vigente desmienta.

El timeout del cliente HTTP declarado en `App/Frontend/src/services/api.ts` SHALL superar el peor caso total de una clasificacion del backend (`Settings.gemini_total_timeout_seconds`), de modo que el cliente no desista antes que la API resuelva su propio fallback.

La suite de pruebas de la barrera (`scripts/preflight/test_docs_stack_sync.py`) SHALL ser hermética respecto del estado real del repositorio: sus fixtures MUST construir arboles sinteticos autosuficientes con las versiones de componentes fijadas por la propia prueba, y MUST NOT derivar la linea base de las versiones reales declaradas en `App/Backend/requirements.txt`, `docker-compose.yml` u `openspec/config.yaml`. Un cambio legitimo de version de dependencia MUST NOT producir hallazgos por si mismo en la suite, y una unica deriva inyectada sobre un arbol sincronizado MUST aislar exactamente un hallazgo.

#### Scenario: Modelo y parametros de inferencia coinciden con la configuracion

- **WHEN** se leen las lineas de `CLAUDE.md` y de `openspec/config.yaml` que declaran el modelo y los parametros de inferencia
- **THEN** el modelo coincide con `Settings.gemini_model`
- **AND** temperature, top_p y max_output_tokens coinciden con `Settings`
- **AND** el timeout, el timeout total y los reintentos declarados coinciden con `Settings.gemini_timeout_seconds`, `gemini_total_timeout_seconds` y `gemini_max_retries`

#### Scenario: Versiones de framework y dependencias coinciden con los pines

- **WHEN** se leen las versiones de FastAPI, Uvicorn y `google-genai` declaradas en `openspec/config.yaml`
- **THEN** coinciden con las restricciones vigentes de `App/Backend/requirements.txt`
- **AND** la version de N8N declarada coincide con la imagen pinneada del compose

#### Scenario: Umbrales y sectores canonicos coinciden con el codigo

- **WHEN** se leen `conventions.thresholds` y `conventions.categorias` de `openspec/config.yaml`
- **THEN** los umbrales coinciden con `Settings.deterministic_score_threshold` y `Settings.human_review_threshold`
- **AND** los sectores coinciden, en contenido y en orden, con `SECTORES_CANONICOS` de `App/Backend/app/constants.py`

#### Scenario: Un valor volatil no se duplica fuera de su fuente

- **WHEN** se busca en `CLAUDE.md` un umbral, una version de framework o de plataforma que ya declara `openspec/config.yaml`
- **THEN** el valor no aparece como literal repetido
- **AND** el texto remite a la seccion correspondiente de `openspec/config.yaml`
- **AND** el nombre del modelo es la excepcion: figura en ambos documentos y ambos coinciden con `Settings.gemini_model`

#### Scenario: Flujo y servicios descritos existen en el repositorio

- **WHEN** la documentacion para agentes describe una etapa de clasificacion o un servicio de infraestructura
- **THEN** la etapa o el servicio existe en el codigo o en el compose
- **AND** ninguna etapa o servicio retirado se describe como vigente

#### Scenario: Valores retirados no se citan como vigentes

- **WHEN** se busca en `CLAUDE.md` y `openspec/config.yaml` un modelo, una version o un servicio que el codigo ya no usa
- **THEN** no aparece como valor vigente del stack

#### Scenario: Barrera ejecutable detecta la divergencia

- **WHEN** un valor de stack declarado en `CLAUDE.md`, en `openspec/config.yaml`, en `knowledge-base/**` o en el material de referencia (`docs/parameters_gemini.md`, `docs/n8n-workflow-guide.md`) diverge de `settings.py`, de `requirements.txt` o del compose, o se describe un servicio o etapa que ya no existe
- **THEN** el preflight `scripts/preflight/docs_stack_sync.py` termina con codigo distinto de cero
- **AND** el hallazgo nombra el valor o el servicio divergente
- **AND** el paso corre en el job `backend-tests` del pipeline de integracion continua

#### Scenario: Barrera ejecutable en verde con la documentacion sincronizada

- **WHEN** la documentacion para agentes declara unicamente valores que coinciden con el codigo y el compose
- **THEN** el preflight termina con codigo 0 y sin hallazgos
- **AND** su suite de pruebas queda incluida en `python -m pytest scripts/preflight -q`

#### Scenario: Documentacion de agentes valida como configuracion

- **WHEN** se carga `openspec/config.yaml` con un lector YAML y se ejecuta el CLI de OpenSpec
- **THEN** el archivo parsea sin errores
- **AND** los comandos de OpenSpec siguen respondiendo sobre el proyecto

#### Scenario: Base de conocimiento y material de referencia declaran el modelo vigente

- **WHEN** se buscan tokens de modelo (`gemini-<version>-flash` o `<version> Flash`) en `knowledge-base/**` y en `docs/parameters_gemini.md` y `docs/n8n-workflow-guide.md`
- **THEN** todo token que no sea `Settings.gemini_model` aparece unicamente en un pasaje rotulado como historico
- **AND** los archivos que declaran la configuracion vigente citan `gemini-3.6-flash` y `google-genai >=2.33,<3`
- **AND** el timeout declarado en contexto de parametros de Gemini es 30 s por intento, con 60 s total y 2 reintentos

#### Scenario: Versiones de componentes de la base de conocimiento coinciden con los pins

- **WHEN** se leen las versiones de N8N, FastAPI, Uvicorn y `google-genai` declaradas en `knowledge-base/**` y en `docs/parameters_gemini.md`
- **THEN** N8N coincide con la imagen pinneada de `docker-compose.yml`
- **AND** FastAPI y Uvicorn coinciden con los pines exactos de `App/Backend/requirements.txt`
- **AND** la restriccion de `google-genai` declarada en `knowledge-base/**` y en `docs/parameters_gemini.md` es al menos tan estricta como `>=2.33.0,<3`
- **AND** una version de componente retirada solo aparece en un pasaje rotulado como historico

#### Scenario: El marcador historico no se infiere de una palabra que rotula otra cosa

- **WHEN** una linea de `knowledge-base/**` menciona un token de modelo retirado junto a la palabra "deprecado" o "deprecada" referida al SDK `google-generativeai`
- **THEN** la linea no se considera historica por esa palabra
- **AND** el preflight reporta el token de modelo retirado si no hay un marcador historico que lo rotule

#### Scenario: Hechos historicos preservados y rotulados como historicos

- **WHEN** se lee la procedencia de la calibracion de parametros y la decision DD-04 en `knowledge-base/09_decisiones_y_supuestos.md` y en `docs/parameters_gemini.md`
- **THEN** el hecho de que los parametros se calibraron sobre `gemini-2.5-flash` se conserva
- **AND** el pasaje esta rotulado de forma explicita como antecedente historico
- **AND** no se presenta `gemini-2.5-flash` ni un timeout de 10 s como el valor vigente
- **AND** el pasaje remite al valor vigente (`gemini-3.6-flash`, 30 s por intento, 60 s total, 2 reintentos)

#### Scenario: Barrera ejecutable cubre la base de conocimiento y el material de referencia

- **WHEN** un token de modelo retirado, un timeout retirado o una version de componente retirada aparece en `knowledge-base/**` o en el material de referencia sin rotulacion historica
- **THEN** el preflight `scripts/preflight/docs_stack_sync.py` termina con codigo distinto de cero
- **AND** el hallazgo nombra el archivo, la linea y el token o valor divergente
- **AND** los valores esperados de las versiones de componentes se derivan en tiempo de ejecucion de `requirements.txt` y de `docker-compose.yml`, no se hardcodean en el chequeo
- **AND** la lista de archivos inspeccionados por el preflight incluye `knowledge-base/**`, `docs/parameters_gemini.md` y `docs/n8n-workflow-guide.md`

#### Scenario: La restriccion de google-genai del material de referencia se valida contra requirements.txt

- **WHEN** `docs/parameters_gemini.md` declara una restriccion de `google-genai` mas laxa que el pin de `App/Backend/requirements.txt` (por ejemplo `>=2.31,<3` frente al pin `>=2.33.0,<3`) en un pasaje no rotulado como historico
- **THEN** el preflight `scripts/preflight/docs_stack_sync.py` termina con codigo distinto de cero
- **AND** el hallazgo nombra `docs/parameters_gemini.md`, la linea y la restriccion divergente
- **AND** el valor esperado de la restriccion de `google-genai` se deriva en tiempo de ejecucion de `App/Backend/requirements.txt`, no se hardcodea
- **AND** cuando el mismo archivo declara la restriccion corregida (`google-genai >=2.33,<3`), el chequeo pasa

#### Scenario: El timeout del cliente supera el peor caso total del backend

- **WHEN** se compara el timeout de Axios declarado en `App/Frontend/src/services/api.ts` con `Settings.gemini_total_timeout_seconds`
- **THEN** el timeout del cliente es estrictamente mayor que el peor caso total del backend (65 s > 60 s)
- **AND** el comentario del cliente declara ese invariante sin afirmar un valor de Gemini retirado
- **AND** la barrera `scripts/preflight/docs_stack_sync.py` verifica el invariante y termina con codigo distinto de cero si el timeout del cliente no supera el peor caso del backend

#### Scenario: La suite de la barrera es hermética frente a las versiones reales del repositorio

- **WHEN** se ejecuta `python3 -m pytest scripts/preflight -q` con una version de dependencia distinta de la que la suite tiene fijada (por ejemplo, tras un bump de `App/Backend/requirements.txt`)
- **THEN** la suite permanece en verde y no depende del contenido real de `requirements.txt`, `docker-compose.yml` ni `openspec/config.yaml`
- **AND** sus fixtures construyen el arbol sobre el que corren los chequeos con las versiones fijadas por la propia prueba

#### Scenario: Una deriva inyectada aísla exactamente un hallazgo

- **WHEN** sobre un arbol sintetico sincronizado se muta un unico valor (un modelo, una version de componente, un umbral o un timeout)
- **THEN** la barrera reporta exactamente un FAIL, nombrando el valor divergente
- **AND** el resto de los chequeos sigue en PASS, tambien cuando el arbol sintetico usa versiones de componentes nuevas

### Requirement: Sincronia de la base de conocimiento con la release publicada de la tesis

`knowledge-base/11_evaluacion_experimental.md` SHALL presentar los resultados vigentes de la ultima release publicada de la tesis, con valores identicos a los valores `vigente` de `docs/Tesis/Correcciones/numeros-canonicos.md`, SHALL citar ese memo como fuente unica y SHALL identificar la release a la que corresponden. El archivo MUST NOT afirmar que los resultados estan pendientes de medicion; si conserva los valores del corpus sintetico descartado, SHALL presentarlos solo como antecedente historico rotulado como superado. Ningun archivo de `knowledge-base/` MUST afirmar que el vocabulario del filtro determinista o el prompt se construyeron sin acceso al corpus de evaluacion ni que la evaluacion es estrictamente fuera de muestra; cuando la base de conocimiento describa la procedencia de esos ajustes, SHALL coincidir con la que declara la tesis (vocabulario de c-71, reglas de frontera de c-72 y punto de operacion de c-74, ajustados con el corpus de evaluacion) y remitir a su analisis de sensibilidad. `knowledge-base/README.md` SHALL referenciar la ruta vigente del render de la tesis (`docs/Tesis/v10 (IA)/tesis_para_agente.md`) y la version del modelo que declara la tesis, y su resumen ejecutivo SHALL presentar los resultados vigentes sin citar valores retirados como vigentes. Ningun archivo de `knowledge-base/` MUST introducir un valor numerico de resultado que no figure en el memo.

#### Scenario: Valores iguales al memo

- **WHEN** se comparan los valores de resultado de `knowledge-base/11_evaluacion_experimental.md` con el memo canonico
- **THEN** cada valor coincide con su fila `vigente` del memo
- **AND** el archivo identifica la release `v1.2.0` y remite al memo como fuente

#### Scenario: Sin resultados pendientes de medicion

- **WHEN** se busca en `knowledge-base/11_evaluacion_experimental.md` la afirmacion de que los numeros "se re-miden" o estan pendientes
- **THEN** no aparece
- **AND** las cifras del corpus sintetico, si se conservan, figuran rotuladas como superadas

#### Scenario: Sin la afirmacion de ausencia de fuga refutada por el dictamen

- **WHEN** se busca en `knowledge-base/` la afirmacion de que keywords y prompt se construyeron sin acceso al corpus de validacion o de que la evaluacion es "estrictamente held-out"
- **THEN** no aparece
- **AND** la procedencia de los ajustes del clasificador, si se menciona, coincide con la que declara la tesis y remite a su analisis de sensibilidad

#### Scenario: Ruta y modelo vigentes en el README

- **WHEN** se lee `knowledge-base/README.md`
- **THEN** remite a `docs/Tesis/v10 (IA)/tesis_para_agente.md` como render de la tesis
- **AND** nombra el modelo con la misma version que declara la tesis (`gemini-3.6-flash`)

#### Scenario: Sin valores retirados presentados como vigentes

- **WHEN** se buscan en `knowledge-base/` los valores que el memo marca `retirado` (por ejemplo, 9,5 % de intervencion humana o el universo de 3.700 incidentes)
- **THEN** no aparecen presentados como resultados vigentes

### Requirement: Registro documental libre de emojis

Los artefactos documentales del proyecto (al menos `CHANGES.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md` y `docs/directorio-evidencia-cumplimiento.md`) SHALL NOT contener emojis ni pictogramas, conforme a la regla dura del proyecto. En particular, `CHANGES.md` MUST NOT contener la marca de verificacion U+2713 (CHECK MARK) ni ninguna otra variante de marca de verificacion. La finalidad de completitud o de estado SHALL expresarse con texto explicito (por ejemplo `COMPLETADO` o `(completado)`) o con la casilla markdown `[x]`, nunca con un pictograma.

#### Scenario: Sin marcas de verificacion en el registro

- **WHEN** se busca en `CHANGES.md` el caracter U+2713 (o cualquier pictograma de estado)
- **THEN** no aparece ninguna coincidencia

#### Scenario: El estado se expresa con texto

- **WHEN** se lee un encabezado de gate o de fase de `CHANGES.md` que antes llevaba una marca de verificacion
- **THEN** su estado se declara con texto explicito
- **AND** el sentido de la linea no cambia

### Requirement: Anotacion fechada de los registros historicos sin reescritura

Un registro historico del proyecto (entradas fechadas de `CHANGES.md`, tareas de un change archivado bajo `openspec/changes/archive/`) MUST NOT reescribirse en su texto original. Cuando un hecho posterior vuelva obsoleta una afirmacion de ese registro, la correccion SHALL agregarse como una ANOTACION FECHADA junto al texto original, conservandolo integro como evidencia. La anotacion MUST declarar la fecha, el hecho que la motiva y la fuente verificable (por ejemplo el commit y el merge), y MUST explicitar que el texto original se conserva como historia.

#### Scenario: Nota de estado stale corregida sin falsificar la historia

- **WHEN** una afirmacion de estado actual de `CHANGES.md` quedo desmentida por un cierre posterior ya registrado
- **THEN** la afirmacion se corrige al estado real
- **AND** las entradas fechadas que documentan los hechos previos se conservan sin reescribirse

#### Scenario: Tarea de rollback obsoleta anotada y no borrada

- **WHEN** una tarea no ejecutada de un change archivado justifica su omision con un hecho que despues dejo de ser cierto (el change fue commiteado y fusionado)
- **THEN** la tarea conserva su texto original
- **AND** recibe una anotacion fechada que cita el commit y el merge, declara la justificacion obsoleta y el rollback moot

### Requirement: Coherencia del estado de los changes referenciados en la base de conocimiento

Ningun archivo de `knowledge-base/` SHALL presentar como pendiente, abierto o en curso un change que ya figura archivado bajo `openspec/changes/archive/`. Cuando un archivo de la base de conocimiento referencie un change como pendiente, su texto SHALL declarar el estado real (completado y archivado). Si se conserva una descripcion de la etapa en la que ese trabajo estaba pendiente, SHALL rotularse de forma explicita como historica, sin reescribir la afirmacion original de estado. Un cambio posterior que deje obsoleta una afirmacion de estado de la base de conocimiento SHALL corregirse a la realidad y, cuando corresponda preservar el hecho previo, SHALL agregarse como anotacion historica junto al texto original.

#### Scenario: Los flujos ya implementados no se presentan como pendientes

- **WHEN** se lee `knowledge-base/07_flujos_principales.md` y se busca el rotulo "pendiente" asociado a los changes `C-02`, `C-04` o `C-05`
- **THEN** el texto no presenta como pendiente ningun flujo cuyo change ya figure archivado
- **AND** el estado real de esos tramos (implementado y archivado) se declara de forma explicita
- **AND** el contexto genuinamente historico, si se conserva, queda rotulado como historico

#### Scenario: Las preguntas ya resueltas se marcan como resueltas

- **WHEN** se lee `knowledge-base/10_preguntas_abiertas.md` y se buscan las preguntas que bloqueaban `C-17` (CSV del corpus), `C-05` (credenciales Outlook/Twilio) y `C-02` (instancia N8N de pruebas)
- **THEN** esas preguntas figuran como resueltas o cerradas, no como abiertas
- **AND** la tabla de preguntas abiertas no lista como pendiente ninguna pregunta cuyo change ya este archivado

#### Scenario: La correccion de estado no borra la historia

- **WHEN** se compara el texto corregido de la base de conocimiento con la afirmacion de estado original
- **THEN** la afirmacion de estado se corrige a la realidad del archivo de changes
- **AND** el hecho previo que quedo obsoleto, si es evidencia relevante, se conserva como anotacion historica rotulada y no se elimina

### Requirement: Rotulacion historica del registro de verificacion del workflow N8N

El registro de verificacion funcional del workflow N8N de `docs/n8n-workflow-guide.md` SHALL rotularse como historico mediante un marcador reconocido por `MARCADORES_HISTORICOS` de `scripts/preflight/docs_stack_sync.py`. La version de N8N citada en ese registro SHALL NOT leerse como la version vigente del stack; la version vigente es la imagen pinneada de `docker-compose.yml`. El texto original del registro SHALL conservarse sin reescribirse: la correccion SHALL expresarse como rotulacion historica o anotacion fechada, nunca como sustitucion del hecho registrado.

#### Scenario: El registro de verificacion lleva un marcador historico reconocido

- **WHEN** se inspecciona el bloque "Resultados de verificacion 7.1-7.6" de `docs/n8n-workflow-guide.md`
- **THEN** el bloque o su encabezado de seccion contiene al menos un marcador de `MARCADORES_HISTORICOS`
- **AND** el marcador rotula explicitamente el registro como historico

#### Scenario: La version de N8N del registro no se lee como vigente

- **WHEN** se lee el bloque "Resultados de verificacion 7.1-7.6" y se compara la version de N8N que cita con la imagen pinneada de `docker-compose.yml`
- **THEN** la version citada queda dentro de un pasaje rotulado como historico y no se presenta como el valor vigente
- **AND** la version vigente declarada en el resto de la guia sigue coincidiendo con la imagen pinneada del compose

#### Scenario: El hecho historico se conserva sin reescritura

- **WHEN** se aplica la rotulacion historica al registro de verificacion
- **THEN** el texto original del registro y su fecha se conservan integros
- **AND** la version de N8N observada en esa verificacion no se reemplaza por la version vigente
