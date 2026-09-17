## REMOVED Requirements

### Requirement: PostgreSQL unavailability triggers skip

**Reason**: El auto-skip silencioso permitió que la suite PostgreSQL de integración nunca corriera en verde sin que ninguna señal lo indicara: sin PostgreSQL los tests se saltaban (exit code 0) y con PostgreSQL fallaban por incompatibilidad de event loop. PostgreSQL es un prerrequisito OBLIGATORIO de esta suite, no opcional; saltar oculta los defectos que la suite existe para detectar.

**Migration**: Ejecutar `docker compose up -d postgres` antes de correr la suite de integración (`pytest -m integration`). Si PostgreSQL no está disponible, la suite ahora falla con un mensaje accionable que nombra el destino de conexión y el comando de remediación. Ver el requisito agregado "PostgreSQL unavailability fails loudly".

## ADDED Requirements

### Requirement: PostgreSQL unavailability fails loudly

Si PostgreSQL no es alcanzable, la suite de tests marcados como `integration` SHALL fallar con un mensaje accionable y exit code distinto de cero, y NO SHALL saltar ningún test. El mensaje SHALL nombrar el destino de conexión (la URL efectiva) y la acción concreta de remediación (levantar el servicio de PostgreSQL del proyecto). Los tests sin el marker `integration` NO SHALL verse afectados por la ausencia de PostgreSQL.

#### Scenario: PostgreSQL ausente falla con mensaje accionable

- **WHEN** se ejecuta la suite de integración y PostgreSQL no es alcanzable en la URL configurada
- **THEN** la ejecución falla con exit code distinto de cero
- **AND** ningún test marcado como `integration` queda skipped
- **AND** el mensaje nombra la URL de conexión efectiva y el comando de remediación

#### Scenario: La ausencia de PostgreSQL no afecta a la suite SQLite

- **WHEN** se ejecuta la suite sin el marker `integration` y PostgreSQL no está disponible
- **THEN** los tests SQLite se ejecutan normalmente
- **AND** la ausencia de PostgreSQL no produce fallos en esa suite

#### Scenario: Configurable connection string

- **WHEN** la variable de entorno `TEST_PG_URL` está definida
- **THEN** los fixtures de PostgreSQL usan esa URL en lugar de la cadena por defecto de docker-compose
- **AND** el mensaje de fallo, si la conexión falla, nombra la URL efectiva provista por la variable

### Requirement: Endpoints de estadísticas operan sobre PostgreSQL

La suite de integración SHALL verificar que `GET /api/v1/estadisticas/tendencias` y `GET /api/v1/estadisticas/resumen` responden HTTP 200 contra PostgreSQL real, con al menos un incidente creado en la base de datos. La verificación SHALL ejercitar tanto la agrupación por día como por mes en tendencias. La suite NO SHALL aceptar un error 500 del servidor como resultado válido.

#### Scenario: Tendencias responde 200 en PostgreSQL

- **WHEN** existe al menos un incidente en PostgreSQL y se consulta `GET /api/v1/estadisticas/tendencias`
- **THEN** la respuesta es HTTP 200
- **AND** el cuerpo expone la estructura de series temporales con los periodos del rango solicitado

#### Scenario: Tendencias agrupa por mes en PostgreSQL

- **WHEN** se consulta `GET /api/v1/estadisticas/tendencias?agrupar_por=mes`
- **THEN** la respuesta es HTTP 200
- **AND** cada periodo de la serie tiene formato de mes

#### Scenario: Resumen responde 200 en PostgreSQL

- **WHEN** existe al menos un incidente en PostgreSQL y se consulta `GET /api/v1/estadisticas/resumen`
- **THEN** la respuesta es HTTP 200
- **AND** el cuerpo expone los KPIs agregados (total de incidentes, promedio diario y distribuciones)

### Requirement: PATCH con FK inexistente devuelve error de cliente en PostgreSQL

La suite de integración SHALL verificar que `PATCH /api/v1/incidentes/{id}` sobre un incidente existente, con un `estado_id` o `sector_id` que NO existe en el catálogo, responde con un código de error de cliente (4xx) y NO con HTTP 500. El incidente NO SHALL quedar modificado con una referencia inválida.

#### Scenario: FK inexistente en PATCH produce 4xx

- **WHEN** se envía un PATCH a un incidente existente indicando un `estado_id` inexistente
- **THEN** la respuesta es un código 4xx con cuerpo de error estructurado
- **AND** la respuesta NO es HTTP 500

#### Scenario: El incidente no queda con referencia inválida

- **WHEN** un PATCH con FK inexistente es rechazado
- **THEN** el incidente conserva su `estado_id` y `sector_id` previos
- **AND** no se persiste ninguna referencia a una fila inexistente del catálogo
