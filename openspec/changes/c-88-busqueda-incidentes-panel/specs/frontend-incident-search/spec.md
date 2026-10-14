## Purpose

Define la barra de busqueda por texto libre del Panel de Administracion: su comportamiento de entrada, su integracion con los filtros y la paginacion existentes, su cableado por la capa de datos del frontend y el estado vacio cuando la busqueda no arroja resultados.

## ADDED Requirements

### Requirement: FIS-001 — Barra de busqueda en el Panel de Administracion

El Panel de Administracion SHALL exponer un campo de busqueda de texto en la pestana de listado de tickets. La entrada SHALL aplicar un debounce de 300 ms antes de disparar la consulta, de modo que escribir no genere una solicitud por cada pulsacion. Un termino con menos de 2 caracteres tras recortar espacios SHALL tratarse como busqueda vacia (sin filtro). El termino SHALL viajar como el parametro `q` a traves de `IncidenteListParams` -> `useIncidentes` -> `listarIncidentes`, sin construir la consulta por fuera de esa cadena. La busqueda SHALL coexistir con los filtros de estado, sector y prioridad (combinacion AND). Ante cualquier cambio del termino de busqueda, la paginacion SHALL reiniciarse a la primera pagina.

#### Scenario: El campo de busqueda esta disponible

- **WHEN** el usuario abre la pestana de listado de tickets del Panel de Administracion
- **THEN** ve un campo de busqueda de texto

#### Scenario: La escritura se debounce

- **WHEN** el usuario escribe un termino de 2 o mas caracteres de forma continua
- **THEN** la consulta al API se dispara una sola vez tras 300 ms sin nuevas pulsaciones

#### Scenario: Termino corto no dispara busqueda

- **WHEN** el usuario escribe un unico caracter o deja el campo vacio
- **THEN** la consulta se emite sin el parametro `q` (equivalente a busqueda vacia)

#### Scenario: El termino viaja por la capa de datos existente

- **WHEN** la busqueda tiene un termino valido
- **THEN** la solicitud al endpoint de listado incluye `q` con ese termino, emitida por el hook de la lista a traves del servicio existente

#### Scenario: La busqueda se combina con los filtros

- **WHEN** el usuario tiene activo un filtro de estado, sector o prioridad y ademas escribe un termino
- **THEN** la consulta enviada incluye el termino y los filtros activos

#### Scenario: Cambiar la busqueda reinicia la paginacion

- **WHEN** el usuario esta en una pagina distinta de la primera y modifica el termino de busqueda
- **THEN** la lista vuelve a la primera pagina

### Requirement: FIS-002 — Estado vacio y limpieza de la busqueda

Cuando la busqueda no arroja resultados, el Panel de Administracion SHALL mostrar un estado vacio con un mensaje neutro en espanol que indique que no hay incidentes para el criterio. El control de limpieza de filtros SHALL ademas limpiar el termino de busqueda y reiniciar la paginacion.

#### Scenario: Estado vacio ante busqueda sin resultados

- **WHEN** la consulta con un termino de busqueda devuelve una lista vacia
- **THEN** la tabla muestra un estado vacio con un mensaje neutro y NO un estado de error

#### Scenario: Limpiar filtros limpia tambien la busqueda

- **WHEN** el usuario activa la limpieza de filtros con un termino de busqueda presente
- **THEN** el campo de busqueda queda vacio y la lista vuelve a la primera pagina sin filtro de texto
