## ADDED Requirements

### Requirement: PRIV-003 — Aviso de privacidad en el canal telefonico

El sistema SHALL informar al titular en el canal telefonico, en el punto de recoleccion y antes de grabar, mediante el saludo TwiML del webhook de voz. El aviso SHALL indicar, en texto estatico y sin interpolar datos del llamante: que la llamada se graba para registrar el incidente, la finalidad del tratamiento, la existencia del responsable y la referencia a la politica de privacidad, la transferencia internacional aplicable y el canal para ejercer los derechos de acceso, rectificacion y supresion. El aviso MUST NOT prometer la creacion inmediata del incidente ni introducir campos de recoleccion adicionales. El aviso MUST conservar las restricciones de seguridad del documento: texto estatico, sin datos del llamador y sin inyeccion en el XML. El aviso SHALL declarar que el sistema esta alineado con la Ley 25.326 y MUST NOT afirmar certificacion ni conformidad.

#### Scenario: El saludo telefonico informa antes de grabar

- **WHEN** se solicita el TwiML de una llamada admitida
- **THEN** el documento contiene un `<Say>` previo al `<Record>` con el aviso de grabacion, finalidad, responsable, transferencia y derechos

#### Scenario: El aviso no recolecta ni promete de mas

- **WHEN** se inspecciona el texto del aviso
- **THEN** no contiene datos del llamante, no promete el alta inmediata del incidente y no agrega campos de recoleccion

#### Scenario: Las restricciones del documento se conservan

- **WHEN** se valida el TwiML generado
- **THEN** el `<Record>` conserva sus atributos y callbacks, el XML es valido y el texto del aviso es estatico

#### Scenario: El aviso no afirma conformidad

- **WHEN** se revisa el texto del aviso telefonico
- **THEN** usa lenguaje de alineacion y no contiene los terminos "certificado", "compliant" ni "cumple"
