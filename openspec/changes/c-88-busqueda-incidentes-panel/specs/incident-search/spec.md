## Purpose

Define la busqueda de incidentes por texto libre en el listado de la API: un filtro opcional que localiza incidentes por su descripcion pseudonimizada o por su numero, combinable con los filtros existentes y siempre acotado por el alcance de visibilidad del usuario.

## ADDED Requirements

### Requirement: IS-001 — Busqueda por texto libre en el listado de incidentes

El listado `GET /api/v1/incidentes` SHALL aceptar un parametro de consulta opcional `q` que filtre incidentes por texto libre. La coincidencia SHALL ser PARCIAL (subcadena) y CASE-INSENSITIVE contra `descripcion_pseudonimizada`. Cuando el valor de `q`, ya recortado, contenga unicamente digitos, el filtro SHALL incluir ademas la coincidencia EXACTA por `id` del incidente, combinando ambas condiciones con OR logico (descripcion coincide O id coincide). El filtro `q` SHALL combinarse con todos los demas filtros del listado con AND logico y SHALL conservar el orden por `created_at` descendente. Un `q` ausente, vacio o con menos de 2 caracteres tras recortar espacios SHALL comportarse como si no se hubiera provisto (sin filtro de texto), preservando exactamente el resultado previo del listado.

Los caracteres comodines de patron (`%`, `_`) y el caracter de escape SHALL tratarse como literales dentro del termino buscado, de modo que su presencia no altere el patron de coincidencia.

#### Scenario: Coincidencia parcial por descripcion

- **WHEN** se consulta el listado con un `q` que es una subcadena de la `descripcion_pseudonimizada` de un incidente
- **THEN** el listado incluye ese incidente

#### Scenario: Coincidencia case-insensitive

- **WHEN** se consulta el listado con un `q` cuya capitalizacion difiere de la de la descripcion
- **THEN** el listado devuelve el incidente de todos modos

#### Scenario: Busqueda por numero de incidente

- **WHEN** se consulta el listado con un `q` compuesto solo por digitos que coincide con el `id` de un incidente
- **THEN** el listado incluye ese incidente junto con los que coincidan por descripcion

#### Scenario: Se combina con los filtros existentes

- **WHEN** se consulta el listado con `q` y ademas con `estado_id`, `sector_id` o `prioridad`
- **THEN** el resultado contiene unicamente incidentes que cumplen el texto Y cada uno de los filtros provistos

#### Scenario: Sin coincidencias devuelve lista vacia

- **WHEN** se consulta el listado con un `q` que no coincide con ninguna descripcion ni id
- **THEN** el listado devuelve una lista vacia, sin error

#### Scenario: Termino demasiado corto se ignora

- **WHEN** se consulta el listado con un `q` vacio, de solo espacios o de un unico caracter
- **THEN** el listado se comporta como si `q` no se hubiera provisto

#### Scenario: Los comodines se tratan como texto literal

- **WHEN** se consulta el listado con un `q` que contiene `%` o `_`
- **THEN** el filtro busca esos caracteres como parte literal del texto y no como comodines de patron

### Requirement: IS-002 — Seguridad y respeto del alcance en la busqueda

La busqueda SHALL ejecutarse con parametros vinculados (consulta parametrizada), sin interpolar el valor de `q` en la sentencia, y SHALL escapar los comodines LIKE del termino. La busqueda MUST NOT leer, devolver ni filtrar por `descripcion_original` (texto con PII cifrado) en ningun caso. La busqueda SHALL aplicarse como una condicion adicional sobre el conjunto de incidentes ya acotado por el alcance de visibilidad del usuario (VIS-001), de modo que MUST NOT permitir ver incidentes fuera del alcance. El requisito SHALL cumplirse para todo modo de alcance vigente (GLOBAL, PROPIO y VACIO) y para los modos que se agreguen en el futuro (por ejemplo, alcance por sector de `gestion_incidentes`, c-86), sin cambios en la logica de busqueda.

#### Scenario: El alcance PROPIO no se saltea

- **WHEN** un usuario con alcance PROPIO busca un texto que coincide con un incidente reportado por otro empleado
- **THEN** el incidente ajeno NO aparece en el resultado

#### Scenario: El alcance vacio no ve resultados

- **WHEN** una cuenta de alcance vacio consulta el listado con cualquier `q`
- **THEN** el resultado es una lista vacia

#### Scenario: La busqueda no expone la descripcion original

- **WHEN** se busca un termino que existe unicamente en la `descripcion_original` (antes de pseudonimizar) y no en la `descripcion_pseudonimizada`
- **THEN** el incidente no se devuelve por ese termino y ninguna respuesta incluye texto de la descripcion original

#### Scenario: La busqueda respeta cualquier modo de alcance vigente

- **WHEN** un usuario cuyo alcance no es GLOBAL consulta el listado con `q`
- **THEN** los resultados son un subconjunto de los incidentes que su alcance le permite ver, con independencia del modo de alcance aplicado
