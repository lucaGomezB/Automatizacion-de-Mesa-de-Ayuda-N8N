## ADDED Requirements

### Requirement: Guarda de integridad referencial de la memoria de Engram en CI

El workflow de integracion continua SHALL ejecutar una guarda que valide la integridad referencial de la memoria de Engram versionada en `.engram/`. La guarda SHALL cargar TODOS los chunks `.jsonl.gz` en una base de datos TEMPORAL y SHALL fallar (codigo de salida distinto de cero) si alguna mutacion de relacion (`entity == "relation"`, `op == "upsert"`) referencia como `source_id` o `target_id` una observacion (`sync_id`) ausente en TODOS los chunks. La guarda MUST NOT depender de secretos, red ni servicios externos (solo biblioteca estandar y los archivos versionados), y MUST NOT modificar ningun chunk, el manifest ni el arbol de dependencias. La guarda SHALL publicar un mensaje accionable que nombre la relacion y el extremo faltante cuando falla, y el repositorio SHALL versionar la suite de pruebas de la guarda (un fixture sano pasa; un fixture con una referencia colgante falla).

#### Scenario: La guarda pasa con la memoria integra

- **WHEN** se ejecuta la guarda sobre `.engram/` con todos los extremos de relacion presentes en la union de chunks
- **THEN** termina con codigo de salida cero y reporta cero referencias colgantes

#### Scenario: La guarda falla ante una referencia colgante

- **WHEN** un chunk contiene una mutacion de relacion cuyo `source_id` o `target_id` no existe como observacion en ningun chunk
- **THEN** la guarda termina con codigo de salida distinto de cero
- **AND** el mensaje nombra la relacion y el extremo faltante

#### Scenario: La guarda es hermética

- **WHEN** la guarda se ejecuta sin red y sin secretos configurados
- **THEN** completa su corrida usando solo la biblioteca estandar y los archivos versionados de `.engram/`
- **AND** no modifica ningun chunk, el manifest ni el arbol de dependencias de las pruebas

#### Scenario: La guarda esta cableada al pipeline

- **WHEN** se inspecciona `.github/workflows/ci.yml`
- **THEN** la guarda corre como un paso del job `secret-scan` o como un job dedicado del workflow
- **AND** el workflow sigue sin referenciar `secrets.*` ni variables de entorno con credenciales reales

#### Scenario: La suite de la guarda fija el contrato

- **WHEN** se ejecuta la suite de pruebas de la guarda
- **THEN** el caso de un fixture sano pasa y el caso de un fixture con una referencia colgante falla
