## ADDED Requirements

### Requirement: Diagramas de arquitectura UML

El proyecto SHALL incluir, bajo `docs/diagrams/`, tres diagramas de arquitectura en notación UML mantenidos como fuente de texto versionable (Mermaid): un diagrama de despliegue, un diagrama de secuencia y un diagrama de componentes. El diagrama de despliegue MUST representar los componentes de infraestructura reales declarados en `docker-compose.yml` (PostgreSQL, Redis, backend FastAPI, N8N) y sus relaciones de comunicación. El diagrama de secuencia MUST ilustrar el flujo extremo a extremo de un incidente desde su recepción en un canal de entrada hasta la confirmación al usuario. El diagrama de componentes MUST reflejar la organización en capas del módulo Python (routes, services, repositories, classifiers, models). Cada archivo de diagrama MUST contener un bloque de código Mermaid sintácticamente válido.

#### Scenario: Los tres diagramas existen y son válidos

- **WHEN** se inspecciona el directorio `docs/diagrams/`
- **THEN** existen los tres diagramas (despliegue, secuencia, componentes), cada uno con un bloque Mermaid sintácticamente parseable

#### Scenario: El diagrama de despliegue refleja la infraestructura real

- **WHEN** se compara el diagrama de despliegue contra `docker-compose.yml`
- **THEN** los cuatro servicios de infraestructura (postgres, redis, backend, n8n) aparecen como nodos del diagrama, sin inventar componentes inexistentes

### Requirement: Especificación OpenAPI 3.1 estática generada desde la app

El proyecto SHALL publicar la especificación OpenAPI 3.1 de la interfaz REST en `docs/openapi.json`, generada **desde la aplicación FastAPI** (`app.main:app`) mediante un script reproducible, nunca escrita a mano. El documento MUST declarar versión OpenAPI `3.1.x` y MUST contener los puntos de entrada efectivamente expuestos por la app (incidentes, clasificaciones, health). El script de generación MUST poder ejecutarse con las variables de entorno dummy que ya emplea CI (`database_url`, `gemini_api_key`, `pseudonymization_encryption_key`) sin requerir una base de datos en ejecución.

#### Scenario: openapi.json es un OpenAPI 3.1 bien formado

- **WHEN** se carga `docs/openapi.json`
- **THEN** es JSON válido, su campo `openapi` comienza con `3.1`, y contiene un objeto `paths` no vacío con las rutas bajo `/api/v1`

#### Scenario: El spec se genera desde la app, no a mano

- **WHEN** se ejecuta el script de generación apuntando a `app.main:app`
- **THEN** produce un `openapi.json` cuyos `paths` coinciden con los `@router` declarados en `App/Backend/app/routes/`

### Requirement: Verificación de sincronía de openapi.json

El proyecto SHALL proveer una verificación que falle cuando `docs/openapi.json` quede desactualizado respecto del esquema que la app FastAPI genera en el momento. La verificación MUST regenerar el esquema en memoria y compararlo contra el archivo commiteado, y MUST poder ejecutarse en CI siguiendo el patrón de jobs de C-09.

#### Scenario: Spec en sincronía pasa la verificación

- **WHEN** `docs/openapi.json` coincide con el esquema generado por la app
- **THEN** la verificación termina con éxito (exit code 0)

#### Scenario: Spec desactualizado falla la verificación

- **WHEN** la app expone un endpoint que `docs/openapi.json` no contiene (o viceversa)
- **THEN** la verificación falla con un mensaje accionable que indica regenerar el archivo

### Requirement: Anexo C — Esquema de base de datos

El proyecto SHALL incluir `docs/anexo_c_esquema_bd.md` con el script SQL completo de las cinco tablas del modelo de datos (`sector`, `estado`, `canal_origen`, `incidente`, `clasificacion_log`), derivado fielmente de los modelos ORM en `App/Backend/app/models/`. El documento MUST declarar, por cada tabla, sus columnas con tipos, las claves primarias, las claves foráneas con su acción `ON DELETE` real (`SET NULL`, `RESTRICT`, `CASCADE`), las restricciones de unicidad y los índices secundarios e índices compuestos definidos en el código. El documento MUST documentar la doble representación de la descripción (`descripcion_original` cifrada at-rest, `descripcion_pseudonimizada` en claro) conforme a la arquitectura de pseudonimización.

#### Scenario: Las cinco tablas están definidas

- **WHEN** se inspecciona `docs/anexo_c_esquema_bd.md`
- **THEN** contiene sentencias `CREATE TABLE` para `sector`, `estado`, `canal_origen`, `incidente` y `clasificacion_log`, y ninguna tabla inventada fuera de ese conjunto

#### Scenario: Las claves foráneas reflejan el comportamiento ON DELETE real

- **WHEN** se comparan las FKs documentadas contra los modelos ORM
- **THEN** `incidente.estado_id` usa `RESTRICT`, `incidente.sector_id` y `incidente.canal_origen_id` usan `SET NULL`, y `clasificacion_log.incidente_id` usa `CASCADE`

#### Scenario: Los índices compuestos del incidente están documentados

- **WHEN** se revisan los índices declarados en el anexo
- **THEN** aparecen los índices compuestos `(created_at, sector_id)` y `(estado_id, created_at)` de la tabla `incidente`

### Requirement: Anexo F — Corpus de validación

El proyecto SHALL incluir `docs/anexo_f_corpus.md` describiendo el corpus de validación: su esquema CSV (columnas requeridas `id`, `descripcion`, `categoria_real`, y opcionales de cronometraje), el conjunto exacto de categorías válidas (`Sistemas`, `Operaciones`, `Soporte Técnico`) y su tamaño objetivo de 200 casos. El documento MUST declarar explícitamente que el corpus actualmente disponible en el repositorio es **sintético/provisional** y que el corpus real es trabajo de campo futuro, sin presentar los datos sintéticos como resultados experimentales reales.

#### Scenario: Esquema y categorías documentados

- **WHEN** se inspecciona `docs/anexo_f_corpus.md`
- **THEN** describe las columnas `id`, `descripcion` y `categoria_real` y enumera las tres categorías válidas exactas, consistentes con el contrato del framework de evaluación (C-08)

#### Scenario: Naturaleza provisional declarada explícitamente

- **WHEN** se lee la sección sobre la procedencia del corpus
- **THEN** afirma de forma inequívoca que el corpus disponible es sintético/provisional y que el corpus real proviene de trabajo de campo futuro

### Requirement: Anexo G — Guía operativa

El proyecto SHALL incluir `docs/operational-guide.md` con los procedimientos operativos del sistema: despliegue (vía `docker compose`), respaldo (backup) y restauración de la base PostgreSQL, y monitoreo de salud mediante los endpoints de chequeo expuestos por el backend. Los comandos documentados MUST ser coherentes con la configuración real de `docker-compose.yml` (nombres de servicios, puertos, credenciales de ejemplo y endpoints de health).

#### Scenario: Procedimientos cubren despliegue, backup y monitoreo

- **WHEN** se inspecciona `docs/operational-guide.md`
- **THEN** incluye secciones para despliegue, backup/restauración de PostgreSQL y monitoreo de salud, cada una con comandos concretos

#### Scenario: Los comandos coinciden con docker-compose

- **WHEN** se contrastan los comandos de la guía contra `docker-compose.yml`
- **THEN** los nombres de servicios y endpoints de monitoreo referenciados existen en el compose (p. ej. servicio `backend` y su healthcheck a `/health`)

### Requirement: Guía de troubleshooting para operadores

El proyecto SHALL incluir `docs/troubleshooting.md` con una guía de resolución de problemas dirigida a operadores, organizada por síntoma. Cada entrada MUST describir un síntoma observable, su causa probable y los pasos de remediación. La guía MUST cubrir como mínimo los fallos operativos previsibles del stack (servicio que no levanta, base de datos no disponible, clasificación que cae a revisión humana por baja confianza, fallo de Gemini).

#### Scenario: Entradas estructuradas por síntoma

- **WHEN** se inspecciona `docs/troubleshooting.md`
- **THEN** cada entrada presenta síntoma, causa probable y remediación, cubriendo al menos los fallos del backend, de la base de datos y del clasificador

### Requirement: README de despliegue local reproducible

El proyecto SHALL actualizar `README.md` con instrucciones de despliegue local que permitan levantar el sistema completo en menos de 15 minutos a partir de un clon limpio. Las instrucciones MUST listar los prerrequisitos, el paso de configuración de variables de entorno (desde una plantilla `.env.example`) y el comando de arranque (`docker compose up`), y MUST referenciar la guía operativa y la de troubleshooting para procedimientos detallados.

#### Scenario: README cubre el camino de despliegue local

- **WHEN** se lee la sección de despliegue local del `README.md`
- **THEN** incluye prerrequisitos, configuración de `.env`, el comando `docker compose up` y una verificación de salud, sin contradecir `docker-compose.yml`

#### Scenario: README enlaza la documentación operativa

- **WHEN** se revisan los enlaces del README
- **THEN** referencia `docs/operational-guide.md` y `docs/troubleshooting.md` para los procedimientos detallados
