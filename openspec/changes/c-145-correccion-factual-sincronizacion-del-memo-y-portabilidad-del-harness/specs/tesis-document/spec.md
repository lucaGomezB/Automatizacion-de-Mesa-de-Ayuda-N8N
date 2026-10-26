## MODIFIED Requirements

### Requirement: Verificabilidad de las afirmaciones de pruebas del Capitulo 6

La tesis SHALL afirmar unicamente lo que el repositorio permite verificar. El §6.7
SHALL NOT declarar pruebas de extremo a extremo que instancien N8N y ejecuten el flujo
completo desde el envio de un correo simulado hasta la persistencia del ticket, porque
ninguna prueba del repositorio instancia N8N. El §6.7 SHALL describir lo que existe
(pruebas estructurales del `n8n/workflow.json`, pruebas de API y pruebas de integracion
contra PostgreSQL) o retraer la afirmacion. El recuento y la cobertura de la suite de
frontend declarados en §6.7 SHALL ser reproducibles contra el estado del repositorio en
el momento de la correccion, o SHALL acompanarse de un informe de cobertura versionado
como evidencia; la tesis SHALL NOT publicar cifras de pruebas o de cobertura que el
repositorio no reproduzca.

Toda afirmacion del §6.7 sobre la suite de integracion PostgreSQL SHALL declarar un
recuento igual al que devuelve `pytest -m integration --collect-only -q` sobre
`App/Backend` en el commit publicado, y SHALL describir el comportamiento ante la
ausencia de PostgreSQL tal como lo implementa `App/Backend/tests/conftest.py`: la suite
FALLA de forma ruidosa y MUST NOT declararse una omision automatica con `pytest.skip`.
Cuando la suite de frontend no pueda ejecutarse en el entorno documentado, el §6.7
SHALL omitir los recuentos numericos congelados y conservar la remision al reporte
vigente del pipeline, sin publicar un numero de pruebas ni de archivos que no se haya
reproducido.

#### Scenario: Sin afirmacion de pruebas e2e de N8N no verificable

- **WHEN** se busca en el repositorio una prueba que instancie N8N y ejecute el flujo completo hasta la persistencia
- **THEN** no existe ninguna prueba de ese tipo
- **AND** el §6.7 no afirma que tales pruebas existan o se hayan ejecutado

#### Scenario: Recuento y cobertura de frontend reproducibles

- **WHEN** se cuenta la suite de pruebas de frontend en HEAD y se genera el informe de cobertura con el comando documentado
- **THEN** las cifras declaradas en §6.7 coinciden con el resultado reproducible, o existe un informe de cobertura versionado que las respalda
- **AND** no queda publicada la cifra 89/98,6 % sin evidencia que la respalde

#### Scenario: Recuento de integracion PostgreSQL reproducible

- **WHEN** se ejecuta `cd App/Backend && pytest -m integration --collect-only -q` sobre el commit publicado
- **THEN** el recuento de pruebas de integracion que declara el §6.7 coincide con el total informado por el comando
- **AND** el §6.7 no describe una omision automatica con `pytest.skip` cuando PostgreSQL no esta disponible

#### Scenario: Comportamiento ante PostgreSQL ausente declarado

- **WHEN** se lee `App/Backend/tests/conftest.py` en el commit publicado
- **THEN** las fixtures de integracion fallan de forma ruidosa si PostgreSQL no esta disponible
- **AND** la tesis describe ese comportamiento y no el de una omision silenciosa

#### Scenario: Recuentos de frontend retirados si no son reproducibles

- **WHEN** la suite de frontend no puede ejecutarse en el entorno documentado por falta de dependencias instaladas
- **THEN** el §6.7 no publica recuentos numericos congelados de pruebas ni de archivos
- **AND** conserva la remision al reporte vigente del pipeline de integracion continua

## ADDED Requirements

### Requirement: Publicacion de una release de correccion sin mover tags publicados

Cuando una release publicada contenga afirmaciones que el repositorio desmienta, el
proyecto SHALL publicar una release de correccion nueva (por ejemplo `v1.2.1`) en lugar
de mover el tag existente. El tag de correccion SHALL ser anotado y SHALL crearse sobre
el commit C3, que contiene el texto corregido y el PDF recompilado. Ese commit C3 SHALL
actualizar el tag del Anexo B y retirar el hash de la release anterior, pero MUST NOT
intentar consignar su propio hash. Un commit posterior C4 SHALL consignar el hash
completo de 40 caracteres de C3 en el Anexo B y la nota de trazabilidad en
`docs/Tesis/Correcciones/dictamen-correcciones.md`. El tag superado SHALL registrarse
como superado y MUST NOT borrarse, recrearse ni reapuntarse.

#### Scenario: Tag de correccion anotado sobre el texto corregido

- **WHEN** se ejecutan `git cat-file -t v1.2.1` y `git rev-parse v1.2.1^{commit}`
- **THEN** el tag existe, es anotado (devuelve `tag`) y apunta al commit que contiene el texto corregido y el PDF recompilado
- **AND** el tag esta publicado en `origin`

#### Scenario: Tag publicado inmutable

- **WHEN** se compara `git rev-parse v1.2.0^{commit}` con el valor registrado antes de este change (`a49d035c67b32ae17e633ec04b09ecdd2781aac6`)
- **THEN** el valor no cambio
- **AND** el registro declara `v1.2.0` como superada por `v1.2.1`

#### Scenario: Hash en el commit posterior al tag

- **WHEN** se lee `sec:anexo-repositorio` en el commit C4 y se compara con `git rev-parse v1.2.1^{commit}`
- **THEN** figura el tag `v1.2.1` y el hash completo de 40 caracteres de C3
- **AND** el hash coincide en los 40 caracteres y figura tambien en la nota de trazabilidad del registro
