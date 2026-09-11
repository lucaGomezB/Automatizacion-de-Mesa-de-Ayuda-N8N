## MODIFIED Requirements

### Requirement: Migraciones y catálogos sembrados
La base de datos SHALL estar al día con las migraciones Alembic, y las tablas de catálogo SHALL contener sus valores canónicos: sector (`Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`), estado (nuevo, en proceso, en espera, resuelto, cerrado), canal_origen (correo electrónico, formulario web, llamada telefónica). Los cinco sectores canónicos SHALL quedar sembrados por la migración `004`, que MUST NOT modificar la migración ya aplicada `001_seed_catalogs.py`.

#### Scenario: Base de datos nueva
- **WHEN** se ejecuta `alembic upgrade head` sobre una base vacía
- **THEN** se crean las tablas y los catálogos quedan sembrados con sus valores canónicos, incluyendo los cinco sectores canónicos y las estructuras de persistencia multietiqueta

#### Scenario: Base de datos existente (idempotencia)
- **WHEN** se ejecuta `alembic upgrade head` sobre una base ya migrada
- **THEN** la operación es no-op y los catálogos no se duplican

#### Scenario: Operaciones ausente y Sistemas presente
- **WHEN** se inspecciona el catálogo `sector` tras las migraciones
- **THEN** `Operaciones` no existe como fila y `Sistemas` permanece como sector propio
