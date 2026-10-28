## ADDED Requirements

### Requirement: Coherencia del estado de los changes referenciados en la base de conocimiento

Ningun archivo de `knowledge-base/` SHALL presentar como pendiente, abierto o en curso un change que ya figura archivado bajo `openspec/changes/archive/`. Cuando un archivo de la base de conocimiento referencie un change como pendiente, su texto SHALL declarar el estado real (completado y archivado). Si se conserva una descripcion de la etapa en la que ese trabajo estaba pendiente, SHALL rotularse de forma explicita como historica, sin reescribir la afirmacion original de estado. Un cambio posterior que deje obsoleta una afirmacion de estado de la base de conocimiento SHALL corregirse a la realidad y, cuando corresponda preservar el hecho previo, SHALL agregarse como anotacion historica junto al texto original.

#### Scenario: Los flujos ya implementados no se presentan como pendientes

- **WHEN** se lee `knowledge-base/07_flujos_principales.md` y se busca el rotulo "pendiente" asociado a los changes `C-02`, `C-04` o `C-05`
- **THEN** el texto no presenta como pendiente ningun flujo cuyo change ya figure archivado
- **AND** el estado real de esos tramos (implementado y archivado) se declara de forma explicita
- **AND** el contexto genuinamente historico, si se conserva, queda rotulado como historico

#### Scenario: Las preguntas ya resueltas se marcan como resueltas

- **WHEN** se lee `knowledge-base/10_preguntas_abiertas.md` y se buscan las preguntas que bloqueaban `C-17` (CSV del corpus), `C-05` (credenciales Outlook/Twilio) y `C-02` (instancia N8N de pruebas)
- **THEN** esas preguntas figuran como resueltas o cerradas, no como abiertas
- **AND** la tabla de preguntas abiertas no lista como pendiente ninguna pregunta cuyo change ya este archivado

#### Scenario: La correccion de estado no borra la historia

- **WHEN** se compara el texto corregido de la base de conocimiento con la afirmacion de estado original
- **THEN** la afirmacion de estado se corrige a la realidad del archivo de changes
- **AND** el hecho previo que quedo obsoleto, si es evidencia relevante, se conserva como anotacion historica rotulada y no se elimina

### Requirement: Rotulacion historica del registro de verificacion del workflow N8N

El registro de verificacion funcional del workflow N8N de `docs/n8n-workflow-guide.md` SHALL rotularse como historico mediante un marcador reconocido por `MARCADORES_HISTORICOS` de `scripts/preflight/docs_stack_sync.py`. La version de N8N citada en ese registro SHALL NOT leerse como la version vigente del stack; la version vigente es la imagen pinneada de `docker-compose.yml`. El texto original del registro SHALL conservarse sin reescribirse: la correccion SHALL expresarse como rotulacion historica o anotacion fechada, nunca como sustitucion del hecho registrado.

#### Scenario: El registro de verificacion lleva un marcador historico reconocido

- **WHEN** se inspecciona el bloque "Resultados de verificacion 7.1-7.6" de `docs/n8n-workflow-guide.md`
- **THEN** el bloque o su encabezado de seccion contiene al menos un marcador de `MARCADORES_HISTORICOS`
- **AND** el marcador rotula explicitamente el registro como historico

#### Scenario: La version de N8N del registro no se lee como vigente

- **WHEN** se lee el bloque "Resultados de verificacion 7.1-7.6" y se compara la version de N8N que cita con la imagen pinneada de `docker-compose.yml`
- **THEN** la version citada queda dentro de un pasaje rotulado como historico y no se presenta como el valor vigente
- **AND** la version vigente declarada en el resto de la guia sigue coincidiendo con la imagen pinneada del compose

#### Scenario: El hecho historico se conserva sin reescritura

- **WHEN** se aplica la rotulacion historica al registro de verificacion
- **THEN** el texto original del registro y su fecha se conservan integros
- **AND** la version de N8N observada en esa verificacion no se reemplaza por la version vigente
