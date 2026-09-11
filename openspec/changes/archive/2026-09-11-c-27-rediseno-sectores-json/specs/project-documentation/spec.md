## MODIFIED Requirements

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
