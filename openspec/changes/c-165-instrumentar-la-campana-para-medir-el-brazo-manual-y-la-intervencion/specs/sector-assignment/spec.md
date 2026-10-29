## MODIFIED Requirements

### Requirement: ASG-005 — Persistencia de los conjuntos predicho y validado del log de clasificacion

El log de clasificacion SHALL soportar los conjuntos multietiqueta de sectores predichos y validados, ademas del sector principal predicho y validado. La validacion humana SHALL poder registrar el conjunto validado de sectores del caso y MUST NOT perder los sectores adicionales al confirmar o corregir una clasificacion. Ademas, cada validacion humana SHALL registrar los metadatos de la INTERVENCION: el ACTOR (id de empleado, sin PII en claro), un INSTANTE de validacion propio y distinguible del `created_at` del log, el ORIGEN de la intervencion (uno de: `gate`, `review`, `sample`, `manual_completion`, `reassignment`) y el DELTA de sector antes/despues (predicho vs validado, incluidos los conjuntos adicionales). La ausencia de intervencion MUST permanecer representable como estado no intervenido.

#### Scenario: Log guarda el conjunto predicho

- **WHEN** se registra una clasificacion con sector principal y sectores adicionales predichos
- **THEN** el log conserva el sector principal y el conjunto completo de sectores predichos

#### Scenario: Validacion humana registra el conjunto validado

- **WHEN** un operador valida o corrige una clasificacion indicando sectores adicionales
- **THEN** el log conserva el conjunto validado de sectores y el incidente refleja la correccion

#### Scenario: La intervencion registra actor instante y origen

- **WHEN** un operador con empleado vinculado valida o corrige una clasificacion
- **THEN** el log persiste el id del empleado actor, un instante de validacion propio y el origen de la intervencion, sin exponer email ni telefono en claro

#### Scenario: El delta de sector antes y despues queda registrado

- **WHEN** la validacion humana confirma o cambia el sector del caso
- **THEN** el log permite reconstruir el sector predicho y el validado (principal y adicionales) como delta antes/despues

#### Scenario: Un caso sin intervencion no inventa metadatos

- **WHEN** un log aun no fue validado por ningun operador
- **THEN** el log permanece en estado no intervenido, sin actor, instante de validacion ni origen ficticios
