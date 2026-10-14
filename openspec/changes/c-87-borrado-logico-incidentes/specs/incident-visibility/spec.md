## ADDED Requirements

### Requirement: VIS-009 — Exclusión de incidentes borrados lógicamente de las superficies de lectura

El sistema SHALL excluir a los incidentes borrados lógicamente (`deleted_at` no nulo) de TODAS las superficies de lectura, sin revelar su existencia ni su contenido:

- El listado `GET /api/v1/incidentes` SHALL NOT incluirlos.
- El detalle `GET /api/v1/incidentes/{id}` SHALL comportarse como NO ENCONTRADO (HTTP 404) para un incidente borrado.
- Las colas de error y de revisión humana donde aplique SHALL NOT incluirlos.
- La pestaña "Historial de Incidentes Cerrados" (introducida por el ciclo de cierre) SHALL NOT mostrarlos, aunque el incidente esté cerrado.
- Las operaciones de escritura (`PATCH`) SHALL comportarse como NO ENCONTRADO (HTTP 404) sobre un incidente borrado.

La exclusión SHALL aplicarse con independencia del rol y del alcance del llamante: ni siquiera `administrador_directorio` SHALL ver un incidente borrado por las superficies de lectura ordinarias. La exclusión SHALL resolverse en un punto único de la capa de datos (el repositorio), de modo que ninguna consulta nueva omita el filtro por omisión.

#### Scenario: El listado omite los incidentes borrados

- **WHEN** un usuario (de cualquier rol) lista incidentes
- **THEN** el sistema no devuelve ningún incidente con `deleted_at` no nulo

#### Scenario: El detalle de un incidente borrado no se encuentra

- **WHEN** un usuario solicita el detalle de un incidente borrado lógicamente
- **THEN** el sistema responde como no encontrado (HTTP 404), sin revelar su existencia ni su contenido

#### Scenario: La cola de revisión omite los borrados

- **WHEN** un usuario consulta la cola de revisión pendiente
- **THEN** el sistema no incluye clasificaciones cuyo incidente esté borrado lógicamente

#### Scenario: El historial de cerrados omite los borrados

- **WHEN** un usuario abre la pestaña "Historial de Incidentes Cerrados"
- **THEN** el sistema no muestra incidentes borrados lógicamente aunque estén cerrados

#### Scenario: La escritura sobre un incidente borrado no se encuentra

- **WHEN** un usuario intenta modificar (PATCH) un incidente borrado lógicamente
- **THEN** el sistema responde como no encontrado (HTTP 404) y no modifica la fila

#### Scenario: La exclusión no depende del rol ni del alcance

- **WHEN** un usuario con rol `administrador_directorio` lista o consulta el detalle de un incidente borrado
- **THEN** el incidente no aparece en el listado y el detalle responde como no encontrado, igual que para cualquier otro rol
