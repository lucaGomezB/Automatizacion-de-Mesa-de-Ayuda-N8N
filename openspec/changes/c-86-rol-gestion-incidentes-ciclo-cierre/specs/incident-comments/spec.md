## Purpose

Define un registro de comentarios durable y APPEND-ONLY sobre un incidente, disponible para cualquier rol que tenga visibilidad del incidente, con un formato de visualizacion uniforme y sin numeracion de entradas.

## ADDED Requirements

### Requirement: ICM-001 — Comentario append-only sobre el incidente

El sistema SHALL permitir agregar comentarios de texto a un incidente y SHALL persistirlos de forma APPEND-ONLY en una tabla dedicada (`incidente_comentario`), conservando por cada entrada el incidente, el empleado autor, el texto y el instante de creacion. Las entradas MUST NOT poder editarse ni borrarse por la API. Las entradas MUST NOT numerarse. El texto de un comentario MUST NOT exponer datos personales del autor en la trazabilidad estructurada.

#### Scenario: Alta de comentario persiste la entrada

- **WHEN** un usuario con visibilidad del incidente agrega un comentario
- **THEN** el sistema persiste una nueva entrada con autor y fecha, sin alterar las entradas previas

#### Scenario: Los comentarios no se editan ni se borran

- **WHEN** se inspecciona la API de comentarios
- **THEN** no existe operacion de edicion ni de borrado de una entrada existente

#### Scenario: Las entradas no se numeran

- **WHEN** se listan los comentarios de un incidente
- **THEN** las entradas se presentan sin numeracion

### Requirement: ICM-002 — Permiso de comentarios derivado de la visibilidad

El sistema SHALL permitir agregar y leer comentarios UNICAMENTE a las cuentas con visibilidad del incidente, reutilizando el servicio de visibilidad sin duplicar la derivacion rol -> alcance. Un `usuario_final` SHALL comentar solo incidentes que reporto; un `gestion_incidentes` SHALL comentar solo incidentes de su sector dentro de su alcance; los roles de alcance GLOBAL (`mesa_de_ayuda`, `administrador_directorio`) SHALL comentar cualquier incidente. Un incidente fuera del alcance SHALL comportarse como NO ENCONTRADO (HTTP 404), sin revelar su existencia ni sus comentarios.

#### Scenario: Usuario final comenta su propio incidente

- **WHEN** un `usuario_final` agrega un comentario a un incidente que reporto
- **THEN** el sistema registra la entrada

#### Scenario: Gestion comenta un incidente de su sector

- **WHEN** un `gestion_incidentes` agrega un comentario a un incidente de su sector
- **THEN** el sistema registra la entrada

#### Scenario: Rol global comenta cualquier incidente

- **WHEN** un `mesa_de_ayuda` o `administrador_directorio` agrega un comentario a cualquier incidente
- **THEN** el sistema registra la entrada

#### Scenario: Comentario fuera de alcance es no encontrado

- **WHEN** un usuario agrega o lee comentarios de un incidente fuera de su alcance
- **THEN** el sistema responde como no encontrado (HTTP 404) y NO registra ni expone la entrada

### Requirement: ICM-003 — Formato de visualizacion de los comentarios

El sistema SHALL presentar cada entrada de comentario con el formato `HH:MM:SS DD/MM/AAAA : {texto}`, con el instante resuelto en la zona horaria `America/Argentina/Buenos_Aires`, y SHALL separar entradas consecutivas con una linea horizontal `----------`. Las entradas SHALL presentarse en orden cronologico ascendente (de la mas antigua a la mas reciente). La fecha de la entrada MUST NOT depender de la zona horaria del servidor.

#### Scenario: Formato de una entrada

- **WHEN** se muestra una entrada creada el 14/10/2026 a las 09:05:03 (hora de Argentina)
- **THEN** la entrada se muestra como `09:05:03 14/10/2026 : {texto}`

#### Scenario: Separador entre entradas

- **WHEN** un incidente tiene dos o mas comentarios
- **THEN** el sistema separa las entradas con una linea horizontal `----------`

#### Scenario: Orden cronologico

- **WHEN** se listan los comentarios de un incidente
- **THEN** las entradas aparecen ordenadas de la mas antigua a la mas reciente

#### Scenario: La fecha no depende del servidor

- **WHEN** el servidor opera en una zona horaria distinta de la de Argentina
- **THEN** la hora mostrada de cada entrada corresponde a `America/Argentina/Buenos_Aires`
