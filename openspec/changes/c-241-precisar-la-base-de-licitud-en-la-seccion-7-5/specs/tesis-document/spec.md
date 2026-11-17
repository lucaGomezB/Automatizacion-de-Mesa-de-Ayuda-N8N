<!--
  ORDEN DE FUSION (dependencia critica): este delta MODIFICA el requisito
  "Parrafo de licitud y alcance en §7.5 para los datos del corpus retirado",
  que solo existe en el delta del change c-240 (aun NO archivado en openspec/specs/).
  `openspec validate --strict` NO verifica la existencia de la base, pero
  `openspec archive` SI la exige: si se intenta fusionar este delta antes de
  archivar c-240, el archivado falla con "MODIFIED ... not found" sin modificar
  archivos. Por lo tanto c-241 SOLO puede archivarse DESPUES de c-240.
  La base debe reproducirse completa (texto + TODOS los escenarios vigentes),
  porque el archivado rechaza un MODIFIED que omita escenarios presentes.
-->

## MODIFIED Requirements

### Requirement: Parrafo de licitud y alcance en §7.5 para los datos del corpus retirado

La subseccion `subsec:consentimiento-derechos` de §7.5 (`11-aspectos-legales.tex`) SHALL contener un parrafo con la base de licitud y el alcance de la autorizacion de los datos del corpus independiente retirado (los textos que en las versiones 1.3.0 a 1.5.2 se presentaron como de una tercera organizacion). El parrafo SHALL declarar de forma explicita: (i) los textos del corpus retirado no contenian datos de una tercera organizacion ni datos personales — eran descripciones genericas de incidentes construidas por los autores — y fueron retirados del repositorio publico y de la tesis; (ii) por lo tanto no corresponde autorizacion ni base de licitud de terceros; (iii) la transferencia de esos textos a la Gemini API se registra en §7.3 (`subsec:transferencia-internacional`); y (iv) la base de licitud de los datos que SI se conservan (corpus de 200 casos pseudonimizado y campana complementaria). La clausula (iv) SHALL declarar la base de licitud por artefacto conservado y distinguirla, y MUST NOT colapsar ambas bases en una unica invocacion generica del articulo~5 de la Ley~25.326 con el consentimiento informado. La base que la subseccion atribuya al corpus de 200 casos SHALL ser la misma que §7.2 (`subsec:principios-datos`) declara para los datos derivados de la relacion de empleo (hoy articulo~5, inciso~2, apartado~d) de la Ley~25.326), salvo que los autores ratifiquen de forma registrada otra asignacion; y la subseccion MUST NOT fundar en el consentimiento los datos cuya base no sea el consentimiento (entre ellos el corpus de 200, cuya base no es el consentimiento). La asignacion exacta del inciso o apartado a cada artefacto conservado y la redaccion final de (iv) SHALL quedar ratificada por los autores antes de escribirla (compuertas del change). El contenido factual SHALL quedar respaldado por la respuesta registrada de los autores (compuertas P4 y P8 de c-235, reabiertas por c-240); sin esa respuesta, la tarea que escribe el parrafo queda bloqueada. El parrafo MUST NOT resolverse por omision y MUST NOT contener nombres reales ni la correspondencia alias-identidad.

#### Scenario: Parrafo presente

- **WHEN** se lee §7.5 tras aplicar el change
- **THEN** existe un parrafo de licitud y alcance del corpus retirado
- **AND** declara el retiro del repositorio publico y la ausencia de datos de terceros

#### Scenario: Sin datos de terceros y retiro declarados

- **WHEN** se lee el parrafo de licitud
- **THEN** declara que los textos retirados no contenian datos de terceros ni personales
- **AND** que fueron retirados del repositorio publico y de la tesis
- **AND** que no corresponde autorizacion ni base de licitud de terceros

#### Scenario: Transferencia y licitud de lo conservado

- **WHEN** se lee el parrafo de licitud
- **THEN** remite a §7.3 para la transferencia de los textos a la Gemini API
- **AND** declara la base de licitud de los datos que se conservan (Ley 25.326, articulo citado)

#### Scenario: Bases de licitud distinguidas por artefacto

- **WHEN** se lee la clausula (iv) de licitud de los datos conservados en §7.5
- **THEN** la base de licitud se declara por artefacto (corpus de 200 casos y campana complementaria)
- **AND** la base del corpus de 200 es consistente con la declarada en §7.2 (articulo 5, inciso 2, apartado d) de la Ley 25.326)
- **AND** no se colapsan ambas bases en una unica invocacion generica del articulo 5 con consentimiento
- **AND** no se funda en el consentimiento un artefacto cuya base no sea el consentimiento

#### Scenario: Coherencia con §7.2

- **WHEN** se comparan §7.2 (`subsec:principios-datos`) y §7.5 (`subsec:consentimiento-derechos`)
- **THEN** la base declarada para el corpus derivado de la relacion de empleo es la misma en ambas subsecciones
- **AND** §7.5 no atribuye el consentimiento como base del corpus derivado de la relacion de empleo

#### Scenario: Ratificacion de autores registrada

- **WHEN** se compara la asignacion de inciso o apartado por artefacto con la tabla de compuertas de `dictamen-correcciones.md`
- **THEN** figura la ratificacion de los autores con fecha y responsable
- **AND** sin esa ratificacion, la oracion de licitud de los datos conservados no se escribe

#### Scenario: Respaldo registrado

- **WHEN** se compara cada frase factual del parrafo con la tabla de compuertas de `dictamen-correcciones.md`
- **THEN** cada afirmacion tiene una respuesta de autores registrada con fecha
- **AND** sin respuesta, el parrafo no se escribe (tarea bloqueada)
