## ADDED Requirements

### Requirement: Registro de confirmaciones del autor en el ledger del dictamen

Las decisiones provisionales del autor sobre el documento de tesis SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md` (el ledger del dictamen) con su estado explicito y su fecha, sin reescribir las entradas provisionales previas, que se conservan como historia de la decision. Una decision que recibe ratificacion del autor SHALL anotarse como CONFIRMADA con la fecha (2026-10-27 para las ratificadas en esta iteracion) y remitir al item original. Las decisiones que NO fueron autorizadas (en particular G0.7a/OQ7a, la ablacion paga del prompt, y OQ6, la validacion por `usuario_final` de su propio incidente, en dominio critico) MUST quedar registradas como PENDIENTES de resolucion y MUST NOT registrarse como autorizadas.

#### Scenario: Ratificacion registrada con fecha

- **WHEN** el autor ratifica una decision que estaba provisional
- **THEN** el ledger agrega una entrada fechada que la declara confirmada
- **AND** la entrada provisional original se conserva sin reescribirse
- **AND** la entrada remite al item original (por ejemplo G0.2/OQ3 en `:724`, G0.3/OQ4 en `:759` y `:772`, G0.4/OQ2 en `:774`, OQ5 en `:1086` y `:1089`, c-131 Q1-Q3 en `:1223-1225`, y c-142 bloque-2 OQ3/OQ4 en `:1356-1357`)

#### Scenario: La corrida paga no se registra como autorizada

- **WHEN** se busca la autorizacion de la ablacion paga del prompt (G0.7a/OQ7a) en el ledger
- **THEN** no aparece una autorizacion registrada
- **AND** el item se declara pendiente de resolucion del autor u orquestador

#### Scenario: La decision de dominio critico queda abierta

- **WHEN** se busca la autorizacion de OQ6 (que `usuario_final` valide su propio incidente) en el ledger
- **THEN** no aparece una autorizacion registrada
- **AND** el item se declara pendiente de resolucion

#### Scenario: Ratificacion del texto final de la tesis registrada

- **WHEN** el autor aprueba la redaccion final de `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex` y `09-conclusiones.tex`
- **THEN** el ledger registra esa aprobacion con su fecha
- **AND** no modifica el contenido de los `.tex` (solo registra la aprobacion)

#### Scenario: Un dato aun no provisto se registra como confirmado-a-proveer

- **WHEN** una decision se confirma pero un valor que la acompania (por ejemplo la version del prompt FORCE-ESCALATE) aun no fue provisto
- **THEN** la decision se registra como confirmada
- **AND** el valor faltante se consigna como pendiente de ser provisto
