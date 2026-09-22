## ADDED Requirements

### Requirement: N8N-TIMING-003 — Recuperación robusta del sello de ingreso de telefonía a través del AI Agent

El workflow SHALL recuperar el instante de ingreso sellado por `Sellar ingreso telefonia` mediante una referencia de nodo que resuelva al primer item sellado (`$('Sellar ingreso telefonia').first().json.ingresado_en`), tanto en el validador `Se verifica lo que trajo la IA` como en el terminal `Derivar a revision humana`. La recuperación MUST NOT depender de la resolución de `pairedItem` implícita en `$('Sellar ingreso telefonia').item`, porque el item corriente proviene del `AI Agent` (y del bucle de refinamiento) y ese emparejamiento se rompe.

El workflow MUST NOT silenciar la ausencia del sello: un `catch` o un `|| null` que devuelva `ingresado_en` nulo sin señal queda prohibido. Cuando el sello no pueda resolverse, el workflow SHALL emitir un WARN estructurado, SHALL marcar el item resultante con `requiere_revision_humana=true` y SHALL continuar hacia la persistencia creando igualmente el ticket. La ejecución MUST NOT abortarse y el incidente MUST NOT perderse. El backend MUST NOT cambiar su contrato: `ingresado_en` sigue siendo nullable y la revisión humana se rige por el flag explícito.

#### Scenario: El validador referencia el sello por el primer item

- **WHEN** la suite estructural inspecciona el `jsCode` del nodo `Se verifica lo que trajo la IA`
- **THEN** el código referencia `$('Sellar ingreso telefonia').first()` y NO referencia `$('Sellar ingreso telefonia').item`

#### Scenario: El terminal referencia el sello por el primer item

- **WHEN** la suite estructural inspecciona el `jsCode` del nodo `Derivar a revision humana`
- **THEN** el código referencia `$('Sellar ingreso telefonia').first()` y NO referencia `$('Sellar ingreso telefonia').item`

#### Scenario: La ausencia del sello no se silencia

- **WHEN** el sello de `Sellar ingreso telefonia` no puede resolverse en el validador
- **THEN** el workflow emite un WARN estructurado y NO devuelve silenciosamente `null` mediante un `catch` o un `|| null`

#### Scenario: Sello ausente deriva a revisión humana conservando el ticket

- **WHEN** el sello de `Sellar ingreso telefonia` no puede resolverse
- **THEN** el item resultante tiene `requiere_revision_humana=true` y el flujo continúa hacia la persistencia, de modo que el ticket se crea y la ejecución no se aborta

#### Scenario: El contrato de persistencia del backend no cambia

- **WHEN** se inspecciona el body del nodo `HTTP POST a MTM-SRU` y el contrato del backend
- **THEN** `ingresado_en` puede ser nulo y la revisión humana se resuelve por el flag explícito, sin cambios en el schema del backend