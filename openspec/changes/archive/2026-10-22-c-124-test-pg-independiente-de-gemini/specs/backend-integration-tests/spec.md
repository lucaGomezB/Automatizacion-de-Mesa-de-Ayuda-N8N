## ADDED Requirements

### Requirement: Aislamiento del clasificador en los tests de integracion PostgreSQL

La suite de pruebas de integracion PostgreSQL SHALL proveer una factoria de cliente HTTP respaldado por PostgreSQL que inyecte el clasificador como doble de prueba determinista, de modo que ningun test que cree incidentes a traves de la API dependa del servicio externo de Gemini. La factoria SHALL sobrescribir las dependencias de sesion de base de datos (con el motor PostgreSQL), de servicio de incidentes (con un `IncidenteService` cuyo clasificador es un doble), de autenticacion, de alcance y de guarda de costo, y SHALL neutralizar la notificacion a N8N, replicando el aislamiento que la suite SQLite ya aplica mediante `make_client_with_classifier`. El doble SHALL devolver un `ClasificacionResult` controlado por el test cuyo `sector_predicho` corresponda a un sector sembrado, de modo que el sector asignado al incidente sea determinista y no dependa de la clave de Gemini.

#### Scenario: La creacion via API con clasificador inyectado asigna un sector determinista

- **WHEN** un test PostgreSQL crea un incidente a traves de `POST /api/v1/incidentes/` usando la factoria con un doble que predice el sector sembrado "Sistemas" con alta confianza
- **THEN** la respuesta es HTTP 201 y el incidente queda asociado al sector sembrado "Sistemas", sin que se invoque la API de Gemini

#### Scenario: El test de PATCH con FK inexistente no depende de Gemini

- **WHEN** se ejecuta `test_patch_incidente_nonexistent_fk_returns_4xx` con una clave de Gemini ficticia (condiciones de CI)
- **THEN** el incidente creado en el setup obtiene un sector no nulo provisto por el doble, el `PATCH` con un `estado_id` inexistente devuelve 4xx y el incidente conserva su sector previo

#### Scenario: Ningun test PostgreSQL contacta el clasificador externo

- **WHEN** se ejecuta un test PostgreSQL que crea incidentes con la factoria, con cualquier valor de la variable de entorno de la clave de Gemini
- **THEN** el sector resultante coincide exactamente con el `sector_predicho` del doble y no se realiza ninguna peticion de red a la API de Gemini
