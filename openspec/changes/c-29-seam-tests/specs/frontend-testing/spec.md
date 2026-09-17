## ADDED Requirements

### Requirement: Alineación de las rutas del cliente HTTP con la especificación OpenAPI

Las rutas invocadas por la capa de servicios del frontend SHALL coincidir con las rutas declaradas en la especificación OpenAPI (`docs/openapi.json`), incluyendo el trailing slash cuando la especificación lo declare, de modo que ninguna petición del cliente dispare una redirección 307 a través del proxy. La suite de pruebas SHALL comparar las rutas del cliente contra las rutas de la especificación, sin requerir un backend en ejecución.

#### Scenario: La ruta de listado/creación de incidentes coincide con OpenAPI

- **WHEN** la suite de pruebas resuelve la ruta que el cliente usa para listar o crear incidentes
- **THEN** la ruta coincide exactamente con `/api/v1/incidentes/` (con trailing slash) declarada en `docs/openapi.json`

#### Scenario: Ninguna ruta del cliente existe solo con redirección

- **WHEN** la suite compara cada ruta del cliente contra el conjunto de rutas de `docs/openapi.json`
- **THEN** cada ruta del cliente existe como ruta exacta en la especificación (o normaliza al trailing slash declarado)
- **AND** ninguna ruta depende de una redirección 307 para llegar al handler

#### Scenario: El detalle de incidente usa la ruta de la especificación

- **WHEN** la suite resuelve la ruta que el cliente usa para el detalle de un incidente
- **THEN** la ruta coincide con `/api/v1/incidentes/{incidente_id}` de la especificación
- **AND** la petición no depende de una redirección para alcanzar el recurso
