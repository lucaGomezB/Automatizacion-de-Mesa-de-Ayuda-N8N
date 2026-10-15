# frontend-incidentes-historial Specification

## Purpose

Define la superficie del panel de administracion para el ciclo de cierre: la pestaña "Historial de Incidentes Cerrados", el listado activo acotado al sector para `gestion_incidentes` y la visualizacion de comentarios del incidente.

## Requirements

### Requirement: FIH-001 — Pestaña "Historial de Incidentes Cerrados"

El panel de administracion SHALL exponer una pestaña "Historial de Incidentes Cerrados" que liste incidentes cerrados de acuerdo con el alcance del usuario devuelto por el backend: los roles de alcance GLOBAL (`mesa_de_ayuda`, `administrador_directorio`) SHALL ver los incidentes globalmente cerrados; un `gestion_incidentes` SHALL ver los incidentes cerrados de su sector (incluidos los cerrados solo por su sector, aunque no esten globalmente cerrados); un `usuario_final` SHALL ver unicamente sus propios incidentes cerrados. El historial SHALL mostrar el estado como "Cerrado" y MUST NOT mostrar incidentes eliminados. La UI MUST NOT ampliar por su cuenta el alcance devuelto por el backend.

#### Scenario: GLOBAL ve el historial completo de cerrados

- **WHEN** un `mesa_de_ayuda` o `administrador_directorio` abre la pestaña de historial
- **THEN** la UI muestra los incidentes globalmente cerrados

#### Scenario: Gestion ve el historial de su sector

- **WHEN** un `gestion_incidentes` abre la pestaña de historial
- **THEN** la UI muestra los incidentes cerrados de su sector, incluidos los cerrados solo por su sector

#### Scenario: Usuario final ve su historial propio

- **WHEN** un `usuario_final` abre la pestaña de historial
- **THEN** la UI muestra unicamente sus propios incidentes cerrados

#### Scenario: Estado mostrado como Cerrado

- **WHEN** se lista una fila del historial
- **THEN** el estado mostrado es "Cerrado"

#### Scenario: Incidente eliminado no aparece

- **WHEN** un incidente fue eliminado
- **THEN** la UI no lo muestra en el historial

### Requirement: FIH-002 — Listado activo acotado al sector para gestion

La vista operativa de incidentes SHALL presentar a un `gestion_incidentes` UNICAMENTE los incidentes de su sector que no estan cerrados para su sector, y SHALL ofrecer las acciones de cierre por sector y edicion de estado sobre esas filas. La UI MUST NOT ocultar por su cuenta datos que el backend autorice ni mostrar datos que el backend no devuelva; el filtro de sector visible SHALL seguir siendo una conveniencia de UX y no un control de acceso.

#### Scenario: Gestion ve solo su sector activo

- **WHEN** un `gestion_incidentes` abre la vista operativa
- **THEN** la UI muestra los incidentes de su sector que no cerraron para su sector

#### Scenario: Acciones disponibles para gestion

- **WHEN** un `gestion_incidentes` abre el detalle de un incidente de su sector
- **THEN** la UI ofrece cerrar por su sector y editar el estado a valores no terminales

#### Scenario: El filtro de sector no es limite de seguridad

- **WHEN** un `gestion_incidentes` limpia o cambia el filtro de sector
- **THEN** el conjunto de datos sigue siendo el que determina el backend

### Requirement: FIH-003 — Comentarios visibles en el detalle del incidente

La UI SHALL mostrar los comentarios del incidente en su detalle, con el formato `HH:MM:SS DD/MM/AAAA : {texto}` y el separador `----------` entre entradas, y SHALL ofrecer agregar un comentario a quien tenga visibilidad del incidente. Tras agregar un comentario, la UI SHALL reflejar la nueva entrada sin exponer datos fuera de alcance.

#### Scenario: Se muestran los comentarios con formato

- **WHEN** se abre el detalle de un incidente con comentarios
- **THEN** cada entrada se muestra como `HH:MM:SS DD/MM/AAAA : {texto}` separadas por `----------`

#### Scenario: Se agrega un comentario

- **WHEN** un usuario con visibilidad agrega un comentario desde el detalle
- **THEN** la UI incorpora la nueva entrada y la muestra con el formato definido

#### Scenario: Sin visibilidad no se ofrecen comentarios

- **WHEN** el backend responde que el incidente esta fuera de alcance
- **THEN** la UI no muestra el detalle ni los comentarios

### Requirement: FIH-004 — La UI no sustituye el enforcement del backend

Las acciones del ciclo de cierre y de comentarios SHALL ser de experiencia de usuario y MUST NOT considerarse el limite de seguridad. Ante una respuesta del backend que deniegue una accion (por ejemplo 403 o 404), la UI SHALL manejarla sin mutar su estado asumiendo exito y sin exponer el recurso.

#### Scenario: Accion denegada por el backend

- **WHEN** el backend deniega un cierre, una edicion de estado o un comentario
- **THEN** la UI muestra el error y no presenta la accion como exitosa

#### Scenario: La UI no concede acceso por si misma

- **WHEN** el backend no devuelve una accion o un recurso por estar fuera de alcance
- **THEN** ninguna logica del frontend lo habilita
