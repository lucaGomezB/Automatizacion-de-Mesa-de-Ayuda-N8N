## ADDED Requirements

### Requirement: Aislamiento de servicios externos en la suite de integración

La suite de pruebas de integración SHALL ejercitar los endpoints HTTP a través de la aplicación ASGI real (`httpx.ASGITransport`) contra una base de datos SQLite in-memory, y MUST aislar por completo todos los servicios externos: el clasificador híbrido (Gemini), el webhook de N8N, Twilio y Outlook. El clasificador MUST inyectarse como doble de prueba mediante `app.dependency_overrides`, devolviendo un `ClasificacionResult` controlado por el test. La notificación `notify_n8n` (fire-and-forget de C-02) MUST neutralizarse de modo que ningún test realice una petición de red saliente. Ningún test SHALL contactar la API real de Gemini ni ningún servicio de red externo.

#### Scenario: La creación de un incidente no invoca la API real de Gemini

- **WHEN** se ejecuta un test de creación de incidente con el clasificador inyectado como doble de prueba
- **THEN** la respuesta del endpoint refleja la categoría y confianza provistas por el doble, y no se realiza ninguna llamada a la API de Gemini

#### Scenario: La notificación a N8N queda neutralizada durante los tests

- **WHEN** se ejecuta cualquier test que cree un incidente
- **THEN** `notify_n8n` no realiza ninguna petición HTTP saliente y el test no depende de un servidor N8N disponible

### Requirement: Catálogos sembrados disponibles para los tests de integración

La suite SHALL proveer una fixture que siembre en la base de datos de test los registros de catálogo mínimos que la capa de servicio resuelve por nombre: el `Estado` "nuevo", los tres `Sector` (`Sistemas`, `Operaciones`, `Soporte Técnico`) y los `CanalOrigen` del dominio. La fixture MUST estar disponible para los tests que crean incidentes, ya que sin el `Estado` "nuevo" la creación falla con `EstadoNotFoundError`. La fixture MUST garantizar el aislamiento entre tests, sin filtrar datos sembrados de un test al siguiente.

#### Scenario: Creación de incidente con catálogos sembrados

- **WHEN** un test crea un incidente y los catálogos requeridos están sembrados
- **THEN** el incidente se persiste en estado "nuevo" sin lanzar `EstadoNotFoundError`

#### Scenario: Resolución de sector desde la clasificación

- **WHEN** el clasificador inyectado predice la categoría "Sistemas" y el sector homónimo está sembrado
- **THEN** el incidente creado queda asociado al sector "Sistemas"

### Requirement: Integración de creación y clasificación de incidentes (POST /api/v1/incidentes)

La suite SHALL verificar de extremo a extremo el endpoint `POST /api/v1/incidentes`. Un payload válido MUST producir HTTP 201 con un cuerpo conforme al contrato `IncidenteRead` (incluyendo `id`, `descripcion_pseudonimizada`, `prioridad`, `requiere_revision_humana`, `sector`, `estado` y `canal_origen`). El sector asignado MUST corresponder a la categoría predicha por el clasificador inyectado, y la marca `requiere_revision_humana` MUST reflejar el resultado de la clasificación. Un payload inválido (descripción por debajo del mínimo, vacía o solo espacios) MUST producir HTTP 422 sin persistir incidente alguno.

#### Scenario: Creación exitosa con clasificación de alta confianza

- **WHEN** se envía un payload válido y el clasificador inyectado devuelve categoría "Sistemas" con confianza 0.95 y `requiere_revision_humana` false
- **THEN** la respuesta es HTTP 201, el cuerpo expone el sector "Sistemas", `requiere_revision_humana` es false y `estado.nombre` es "nuevo"

#### Scenario: Creación con baja confianza marca revisión humana

- **WHEN** se crea un incidente y el clasificador inyectado devuelve confianza por debajo de 0.70 con `requiere_revision_humana` true
- **THEN** la respuesta es HTTP 201 y el incidente queda con `requiere_revision_humana` true

#### Scenario: Payload con descripción inválida es rechazado

- **WHEN** se envía un payload cuya descripción está vacía, es solo espacios o tiene menos del mínimo de caracteres
- **THEN** la respuesta es HTTP 422 y no se crea ningún incidente en la base de datos

### Requirement: Integración de listado de incidentes (GET /api/v1/incidentes)

La suite SHALL verificar el endpoint `GET /api/v1/incidentes`. La respuesta MUST ser HTTP 200 con una lista de elementos conformes a `IncidenteListItem`. Los tests MUST cubrir el listado sin filtros, los filtros combinables (`sector_id`, `estado_id`, `prioridad`, `requiere_revision_humana`, `desde`, `hasta`) aplicados con conjunción lógica, la paginación mediante `limit` y `offset`, y el orden por fecha de creación descendente.

#### Scenario: Listado sin filtros devuelve todos los incidentes

- **WHEN** existen varios incidentes y se consulta el listado sin parámetros de filtro
- **THEN** la respuesta es HTTP 200 con todos los incidentes, ordenados del más reciente al más antiguo

#### Scenario: Filtro por sector devuelve solo los coincidentes

- **WHEN** se consulta el listado filtrando por un `sector_id` específico
- **THEN** la respuesta contiene únicamente los incidentes asignados a ese sector

#### Scenario: Paginación limita y desplaza los resultados

- **WHEN** se consulta el listado con `limit` y `offset` sobre un conjunto mayor que `limit`
- **THEN** la respuesta contiene a lo sumo `limit` elementos, omitiendo los primeros `offset`

### Requirement: Integración de detalle de incidente (GET /api/v1/incidentes/{id})

La suite SHALL verificar el endpoint `GET /api/v1/incidentes/{id}`. Para un incidente existente, la respuesta MUST ser HTTP 200 con el contrato completo `IncidenteRead`, incluyendo la descripción pseudonimizada y los objetos de catálogo relacionados. Para un identificador inexistente, la respuesta MUST ser HTTP 404 con un cuerpo de error estructurado `{"error": {"code": "NOT_FOUND", ...}}`.

#### Scenario: Detalle de un incidente existente

- **WHEN** se solicita el detalle de un incidente previamente creado
- **THEN** la respuesta es HTTP 200 y el cuerpo expone su `id`, `descripcion_pseudonimizada` y los objetos de catálogo relacionados

#### Scenario: Detalle de un incidente inexistente

- **WHEN** se solicita el detalle de un `id` que no existe
- **THEN** la respuesta es HTTP 404 con cuerpo `{"error": {"code": "NOT_FOUND", ...}}`

### Requirement: Integración de actualización parcial de incidente (PATCH /api/v1/incidentes/{id})

La suite SHALL verificar el endpoint `PATCH /api/v1/incidentes/{id}` con semántica PATCH parcial: solo los campos presentes y no nulos del payload se modifican; los ausentes permanecen sin cambios. Para un incidente existente, la respuesta MUST ser HTTP 200 con el `IncidenteRead` actualizado. Para un identificador inexistente, la respuesta MUST ser HTTP 404.

#### Scenario: Actualización parcial modifica solo los campos enviados

- **WHEN** se envía un PATCH que cambia únicamente la `prioridad` de un incidente existente
- **THEN** la respuesta es HTTP 200, la `prioridad` queda actualizada y los demás campos conservan su valor previo

#### Scenario: Actualización de un incidente inexistente

- **WHEN** se envía un PATCH sobre un `id` que no existe
- **THEN** la respuesta es HTTP 404 con cuerpo de error estructurado

### Requirement: Integración de la cola de revisión pendiente (GET /api/v1/clasificaciones/revision-pendiente)

La suite SHALL verificar el endpoint `GET /api/v1/clasificaciones/revision-pendiente`. La respuesta MUST ser HTTP 200 con la lista de registros de clasificación que cumplen simultáneamente `requiere_revision_humana == True` y `sector_id_validado IS NULL`, ordenados en modo FIFO (el más antiguo primero). Los registros ya validados o de alta confianza MUST quedar excluidos de la cola. La suite MUST verificar la paginación mediante `limit` y `offset`.

#### Scenario: La cola contiene solo registros pendientes de revisión

- **WHEN** existen registros con `requiere_revision_humana` true sin validar, junto a registros de alta confianza y registros ya validados
- **THEN** la cola contiene únicamente los registros pendientes sin validar

#### Scenario: La cola respeta el orden FIFO

- **WHEN** hay múltiples registros pendientes creados en distintos momentos
- **THEN** la cola los devuelve del más antiguo al más reciente

### Requirement: Integración de la validación humana de clasificaciones (PATCH /api/v1/clasificaciones/{id}/validar)

La suite SHALL verificar el endpoint `PATCH /api/v1/clasificaciones/{id}/validar`. Una validación válida MUST producir HTTP 200, asignar `sector_id_validado` al registro y retirarlo de la cola de revisión pendiente. La suite MUST verificar tanto el caso en que el sector validado coincide con el predicho (acierto del clasificador) como el caso en que difiere (corrección humana). Un `log_id` inexistente o un `sector_id_validado` inexistente MUST producir HTTP 404.

La validación MUST además propagarse al incidente en la misma transacción: `incidente.sector_id` queda asignado al sector validado y `requiere_revision_humana` queda en falso, de modo que el ticket quede ruteado según el veredicto humano y salga del estado de revisión pendiente. La auditoría NO SHALL alterarse: el registro de clasificación conserva `sector_id_predicho` intacto como etiqueta para las métricas de la tesis. (Comportamiento agregado en el fix ISSUE-002 de la sesión de QA 2026-06-12; cubierto por `tests/test_api_validar_cascade.py`.)

#### Scenario: Validación humana retira el registro de la cola

- **WHEN** un operador valida un registro pendiente indicando un sector existente
- **THEN** la respuesta es HTTP 200 con `sector_validado` asignado, y ese registro ya no aparece en la cola de revisión pendiente

#### Scenario: La corrección humana se propaga al incidente

- **WHEN** un operador valida un registro pendiente indicando un sector distinto del predicho
- **THEN** el incidente queda asignado al sector validado con `requiere_revision_humana` en falso, y el registro de clasificación conserva `sector_predicho` original para auditoría

#### Scenario: La confirmación humana limpia el flag de revisión del incidente

- **WHEN** un operador valida un registro pendiente confirmando el sector predicho
- **THEN** el incidente conserva el sector predicho y `requiere_revision_humana` queda en falso

#### Scenario: Validación de un log inexistente

- **WHEN** se valida un `log_id` que no existe
- **THEN** la respuesta es HTTP 404 con cuerpo de error estructurado

#### Scenario: Validación con un sector inexistente

- **WHEN** se valida un registro existente indicando un `sector_id_validado` que no existe en el catálogo
- **THEN** la respuesta es HTTP 404 y el registro no queda validado

### Requirement: Integración de los endpoints de salud (GET /api/v1/health)

La suite SHALL verificar los endpoints de salud. `GET /api/v1/health` (liveness) MUST devolver HTTP 200 con un cuerpo que incluya `status` igual a "ok" y la versión de la aplicación, sin acceder a la base de datos. `GET /api/v1/health/db` (readiness) MUST devolver HTTP 200 confirmando que la base de datos es alcanzable.

#### Scenario: Liveness probe responde sin tocar la base de datos

- **WHEN** se consulta `GET /api/v1/health`
- **THEN** la respuesta es HTTP 200 con `status` "ok" y la versión de la aplicación

#### Scenario: Readiness probe confirma la base de datos

- **WHEN** se consulta `GET /api/v1/health/db` con la base de datos de test disponible
- **THEN** la respuesta es HTTP 200 indicando que la base de datos es alcanzable

### Requirement: Cobertura de código sobre las capas de la API

La suite de integración, junto con la suite existente, SHALL alcanzar una cobertura de código superior al 85% sobre los módulos `app/routes/`, `app/services/` y `app/repositories/`, medible con `pytest --cov`. La medición MUST poder ejecutarse de forma reproducible con un único comando que reporte las líneas no cubiertas.

#### Scenario: La cobertura sobre las capas de la API supera el umbral

- **WHEN** se ejecuta la suite completa con medición de cobertura sobre `app/routes/`, `app/services/` y `app/repositories/`
- **THEN** la cobertura reportada para esos módulos es superior al 85%
