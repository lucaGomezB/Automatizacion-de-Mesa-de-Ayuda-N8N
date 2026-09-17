## ADDED Requirements

### Requirement: La suite de integración se ejecuta contra una base descartable

Las fixtures PostgreSQL de la suite de integración SHALL operar sobre la base de datos descartable definida por la capability `disposable-test-database`, y NO SHALL aplicar DDL destructivo sobre la base de datos de la aplicación. El fallo ruidoso ante PostgreSQL ausente (sin skip silencioso) SHALL conservarse, la ausencia de PostgreSQL NO SHALL afectar a la suite SQLite, y los tests de integración PostgreSQL existentes SHALL permanecer en verde.

#### Scenario: La suite de integración usa el destino descartable

- **WHEN** se ejecuta la suite marcada como integración
- **THEN** las fixtures provisionan y usan la base descartable como destino
- **AND** no se ejecuta DDL destructivo sobre la base de datos de la aplicación

#### Scenario: PostgreSQL ausente sigue fallando ruidosamente

- **WHEN** se ejecuta la suite de integración y PostgreSQL no es alcanzable
- **THEN** la ejecución falla con exit code distinto de cero y un mensaje que nombra la URL efectiva
- **AND** ningún test marcado como integración queda skipped

#### Scenario: La suite SQLite no se ve afectada

- **WHEN** se ejecuta la suite sin el marker de integración
- **THEN** los tests SQLite se ejecutan normalmente con el enforcement de claves foráneas habilitado
- **AND** la ausencia o presencia de PostgreSQL no altera su resultado

#### Scenario: Los tests de integración existentes siguen pasando

- **WHEN** se ejecuta la suite de integración contra un PostgreSQL saludable
- **THEN** los tests PostgreSQL existentes pasan contra la base descartable
