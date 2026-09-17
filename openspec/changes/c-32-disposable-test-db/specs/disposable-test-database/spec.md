## Purpose

Define la base de datos descartable que la suite de integración PostgreSQL usa como destino: cómo se resuelve su URL, cómo se aprovisiona y descarta, y qué guardia de seguridad impide que una corrida por defecto pueda destruir la base de datos de la aplicación. También define la documentación del flujo local seguro.

## ADDED Requirements

### Requirement: Destino descartable dedicado

La suite de integración PostgreSQL SHALL ejecutar su DDL destructivo (`drop_all`/`create_all` y cualquier `DROP`) exclusivamente contra una base de datos DESCARTABLE, distinta de la base de datos de la aplicación declarada por el proyecto (la del `docker-compose.yml`). La base descartable SHALL poder crearse y eliminarse de forma automatizada: provista por una conexión de mantenimiento al mismo servidor, `CREATE DATABASE` en el setup y `DROP DATABASE` en el teardown de la sesión. La suite NO SHALL depender de que exista previamente la base descartable.

#### Scenario: La base descartable se crea y se destruye por corrida

- **WHEN** se ejecuta la suite de integración contra un PostgreSQL alcanzable sin haber creado manualmente la base descartable
- **THEN** la fixture la crea antes de aplicar el esquema
- **AND** al finalizar la sesión la fixture la elimina junto con su contenido

#### Scenario: El DDL destructivo no alcanza la base de la aplicación

- **WHEN** la suite de integración aplica `drop_all` y `create_all`
- **THEN** el destino efectivo es la base descartable
- **AND** los objetos de la base de datos de la aplicación permanecen intactos

#### Scenario: Aprovisionamiento no disponible

- **WHEN** no es posible crear la base descartable (por ejemplo, la conexión de mantenimiento o el privilegio `CREATE DATABASE` no están disponibles) y el destino resuelto NO es la base de la aplicación
- **THEN** la suite puede continuar con el ciclo de vida de esquema sobre el destino resuelto, con una advertencia visible que explica la degradación
- **AND** la suite NO continúa nunca si el destino resuelto coincide con la base de la aplicación

### Requirement: La URL de test no apunta por defecto a la base de aplicación

La resolución de la URL de la suite de integración NO SHALL tener ningún camino por defecto que produzca la base de datos de la aplicación. Si la variable de entorno `TEST_PG_URL` está definida, la suite SHALL usarla. Si no está definida, la suite SHALL resolver a la base descartable dedicada derivada de las credenciales de desarrollo del proyecto. La resolución SHALL ser determinista y verificable.

#### Scenario: Sin variable de entorno, el destino es la base descartable

- **WHEN** se ejecuta la suite de integración sin `TEST_PG_URL` definida
- **THEN** el destino efectivo es la base descartable dedicada (por ejemplo `mesa_de_ayuda_test`), no la base de la aplicación

#### Scenario: La variable de entorno tiene prioridad

- **WHEN** `TEST_PG_URL` está definida apuntando a una instancia PostgreSQL
- **THEN** la suite usa exactamente esa URL como destino
- **AND** el mensaje de fallo ante una conexión fallida nombra la URL efectiva provista por la variable

#### Scenario: Ningún valor por defecto coincide con la base de la aplicación

- **WHEN** se inspeccionan todos los caminos de resolución de la URL de test cuando `TEST_PG_URL` no está definida
- **THEN** ninguno produce el nombre de la base de datos de la aplicación

### Requirement: Guardia de seguridad contra destrucción de la base de aplicación

Antes de ejecutar cualquier DDL destructivo, la suite SHALL comparar el nombre de la base destino con el nombre de la base de datos de la aplicación. Si coinciden, la suite SHALL abortar con un mensaje accionable y exit code distinto de cero, salvo que exista una habilitación explícita e inequívoca del operador. La suite NO SHALL destruir la base de la aplicación como consecuencia de una corrida por defecto.

#### Scenario: Destino igual a la base de aplicación aborta

- **WHEN** la base destino resuelta coincide en nombre con la base de datos de la aplicación y no hay habilitación explícita
- **THEN** la suite aborta antes de ejecutar DDL destructivo
- **AND** el mensaje nombra la base destino, la base de la aplicación y la acción de remediación
- **AND** el exit code es distinto de cero

#### Scenario: Habilitación explícita permite entornos dedicados

- **WHEN** el operador declara explícitamente que acepta un destino cuyo nombre coincide con el de la aplicación (por ejemplo, un contenedor de CI dedicado y efímero)
- **THEN** la suite procede sin abortar

#### Scenario: Un destino descartable distinto no se bloquea

- **WHEN** el nombre de la base destino difiere del de la base de la aplicación
- **THEN** la guardia no bloquea la ejecución

### Requirement: Compatibilidad con el CI

El pipeline de integración continua SHALL seguir funcionando sin cambios. La suite SHALL honrar `TEST_PG_URL` cuando el CI la define apuntando a su service container PostgreSQL dedicado, y la guardia de seguridad NO SHALL bloquear esa corrida.

#### Scenario: El CI apunta a su propio contenedor

- **WHEN** el CI define `TEST_PG_URL` hacia su service container PostgreSQL dedicado y efímero
- **THEN** la suite usa esa URL y completa sus pruebas de integración sin ser bloqueada por la guardia

### Requirement: Documentación del flujo local seguro

La documentación de desarrollo del proyecto (`AGENTS.md` y cualquier documento que repita la afirmación) SHALL declarar con exactitud que la suite del backend requiere una instancia PostgreSQL para el subconjunto de integración, cómo apuntarla a una base descartable y cuál es el flujo local seguro. La documentación NO SHALL afirmar que el backend corre completamente offline ni que no requiere Docker para la porción de integración.

#### Scenario: La documentación declara el prerequisito PostgreSQL

- **WHEN** se lee la sección de comandos de desarrollo de `AGENTS.md`
- **THEN** declara que el subconjunto de integración requiere una instancia PostgreSQL alcanzable
- **AND** describe cómo configurar el destino descartable y el comando del flujo local seguro

#### Scenario: La afirmación de offline queda acotada

- **WHEN** se revisa la documentación de tests del backend
- **THEN** la afirmación de "offline / sin Docker" queda limitada explícitamente a la suite SQLite
- **AND** no se presenta como válida para el subconjunto de integración

#### Scenario: La configuración de testing refleja la realidad

- **WHEN** se inspecciona `openspec/config.yaml`
- **THEN** la descripción de testing del backend menciona el subconjunto de integración PostgreSQL además de la suite SQLite in-memory
