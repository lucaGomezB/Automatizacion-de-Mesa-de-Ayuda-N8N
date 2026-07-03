## MODIFIED Requirements

### Requirement: Especificacion OpenAPI 3.1 estatica generada desde la app

El proyecto SHALL publicar la especificacion OpenAPI 3.1 de la interfaz REST en `docs/openapi.json`, generada **desde la aplicacion FastAPI** (`app.main:app`) mediante un script reproducible, nunca escrita a mano. El documento MUST declarar version OpenAPI `3.1.x` y MUST contener los puntos de entrada efectivamente expuestos por la app (incidentes, clasificaciones, health). El script de generacion MUST poder ejecutarse con las variables de entorno dummy que ya emplea CI (`database_url`, `gemini_api_key`, `pseudonymization_encryption_key`) sin requerir una base de datos en ejecucion.

#### Scenario: openapi.json es un OpenAPI 3.1 bien formado

- **WHEN** se carga `docs/openapi.json`
- **THEN** es JSON valido, su campo `openapi` comienza con `3.1`, y contiene un objeto `paths` no vacio con las rutas bajo `/api/v1`

#### Scenario: El spec se genera desde la app, no a mano

- **WHEN** se ejecuta el script de generacion apuntando a `app.main:app`
- **THEN** produce un `openapi.json` cuyos `paths` coinciden con los `@router` declarados en `App/Backend/app/routes/`

### Requirement: Anexo C — Esquema de base de datos

El proyecto SHALL incluir `docs/anexo_c_esquema_bd.md` con el script SQL completo de las cinco tablas del modelo de datos (`sector`, `estado`, `canal_origen`, `incidente`, `clasificacion_log`), derivado fielmente de los modelos ORM en `App/Backend/app/models/`. El documento MUST declarar, por cada tabla, sus columnas con tipos, las claves primarias, las claves foraneas con su accion `ON DELETE` real (`SET NULL`, `RESTRICT`, `CASCADE`), las restricciones de unicidad y los indices secundarios e indices compuestos definidos en el codigo. El documento MUST documentar la doble representacion de la descripcion (`descripcion_original` cifrada at-rest, `descripcion_pseudonimizada` en claro) conforme a la arquitectura de pseudonimizacion.

#### Scenario: Las cinco tablas estan definidas

- **WHEN** se inspecciona `docs/anexo_c_esquema_bd.md`
- **THEN** contiene sentencias `CREATE TABLE` para `sector`, `estado`, `canal_origen`, `incidente` y `clasificacion_log`, y ninguna tabla inventada fuera de ese conjunto

#### Scenario: Las claves foraneas reflejan el comportamiento ON DELETE real

- **WHEN** se comparan las FKs documentadas contra los modelos ORM
- **THEN** `incidente.estado_id` usa `RESTRICT`, `incidente.sector_id` y `incidente.canal_origen_id` usan `SET NULL`, y `clasificacion_log.incidente_id` usa `CASCADE`

#### Scenario: Los indices compuestos del incidente estan documentados

- **WHEN** se revisan los indices declarados en el anexo
- **THEN** aparecen los indices compuestos `(created_at, sector_id)` y `(estado_id, created_at)` de la tabla `incidente`
