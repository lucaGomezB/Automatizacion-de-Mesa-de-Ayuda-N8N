## ADDED Requirements

### Requirement: NR-008 — Notificacion post-revision a gestion_incidentes de los sectores

El sistema SHALL, una vez que un incidente HA PASADO la revision humana (validacion que deja `requiere_revision_humana` en falso), resolver como destinatarios del aviso post-revision a los empleados ACTIVOS con rol `gestion_incidentes` cuyo sector pertenece al CONJUNTO de sectores validados del incidente. La resolucion SHALL provenance del directorio `directorio_empleado` (NR-001) y el rol destinatario SHALL derivarse del registro unico de politica (RP-002), sin listas fijas ni duplicacion. El sistema SHALL exponer los destinatarios resueltos a N8N en el payload del aviso como una lista (vacia cuando no haya coincidencia) acompanada del identificador del incidente y de un marcador de evento, y MUST NOT exigir que N8N resuelva destinatarios por su cuenta. El aviso SHALL ser fire-and-forget: MUST NOT bloquear, demorar de forma observable ni alterar la respuesta de la validacion. La trazabilidad MUST NOT registrar emails en claro.

#### Scenario: Gestion del sector recibe el aviso validado

- **WHEN** un incidente con el sector S en su conjunto validado pasa la revision humana y existe un `gestion_incidentes` activo del sector S
- **THEN** ese empleado es un destinatario del aviso post-revision

#### Scenario: Varios sectores resuelven varios destinatarios

- **WHEN** el conjunto validado del incidente incluye N sectores con `gestion_incidentes` activos
- **THEN** la resolucion devuelve los destinatarios de esos sectores, sin duplicados

#### Scenario: Sin coincidencia no es fatal

- **WHEN** no existe ningun `gestion_incidentes` activo para los sectores validados
- **THEN** la resolucion devuelve una lista vacia sin lanzar excepcion y la validacion concluye con normalidad

#### Scenario: Lista vacia representable en el payload

- **WHEN** no se resuelve ningun destinatario post-revision
- **THEN** el payload del aviso presenta una lista vacia (no ausencia de campo ni error)

#### Scenario: La validacion no depende del aviso

- **WHEN** el aviso post-revision falla o el directorio no responde
- **THEN** la respuesta de la validacion se completa con independencia del resultado del aviso

#### Scenario: Trazabilidad sin emails

- **WHEN** se resuelve o se envia el aviso post-revision
- **THEN** la trazabilidad registra el resultado y la cantidad de destinatarios, sin emails en claro

#### Scenario: Empleados de otros roles excluidos

- **WHEN** el directorio contiene `usuario_final`, `mesa_de_ayuda` o `administrador_directorio` activos
- **THEN** ninguno de ellos es destinatario del aviso post-revision
