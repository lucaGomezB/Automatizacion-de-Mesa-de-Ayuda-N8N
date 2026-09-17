## ADDED Requirements

### Requirement: La costura SQLite de los tests aplica integridad referencial

La suite de tests del backend que usa SQLite in-memory SHALL habilitar la verificacion de claves foraneas (`PRAGMA foreign_keys=ON`) en cada conexion, de modo que las violaciones de integridad referencial se detecten tambien en el entorno rapido, igual que en PostgreSQL. La suite MUST NOT dar verde ante una violacion de FK que PostgreSQL rechazaria.

#### Scenario: Una FK invalida falla en SQLite

- **WHEN** una prueba persiste una entidad referenciando una clave foranea inexistente bajo SQLite in-memory
- **THEN** la operacion falla con un error de integridad referencial, igual que en PostgreSQL

#### Scenario: Los datos validos siguen persistiendo

- **WHEN** una prueba persiste entidades con claves foraneas existentes
- **THEN** la operacion se completa normalmente y las filas quedan disponibles para la prueba

### Requirement: La suite PostgreSQL corre en verde de forma aislada

Las pruebas de integracion de PostgreSQL SHALL ejecutarse en verde contra una instancia real, con fixtures cuyo ciclo de vida este aislado entre pruebas y con un alcance de event loop coherente entre fixtures y tests. La suite MUST NOT fallar por un problema de infraestructura de test (por ejemplo, un event loop de alcance incorrecto) presentado como si fuera un fallo de producto.

#### Scenario: La suite PG pasa contra PostgreSQL

- **WHEN** se ejecuta la suite marcada como integracion contra una instancia PostgreSQL healthy
- **THEN** todas las pruebas de integracion pasan y ninguna falla por infraestructura de test

#### Scenario: El aislamiento entre pruebas se mantiene

- **WHEN** se ejecutan pruebas de integracion consecutivas
- **THEN** los datos de una prueba no filtran a la siguiente y no se producen errores de event loop
