## MODIFIED Requirements

### Requirement: Notificación fire-and-forget no bloqueante
La notificación a N8N SHALL ser fire-and-forget: NO SHALL bloquear, demorar de forma observable, ni alterar la respuesta HTTP del endpoint que creó el incidente. El incidente persistido y clasificado SHALL retornarse al llamador independientemente del estado de la notificación a N8N. La tarea asíncrona SHALL conservar una referencia retenida durante su ciclo de vida, de modo que el recolector de basura no la cancele antes de completarse.

#### Scenario: La respuesta no espera el resultado de N8N
- **WHEN** un incidente se crea y clasifica correctamente
- **THEN** `create_and_classify()` retorna el incidente completo sin que su valor de retorno dependa de la respuesta del webhook de N8N

#### Scenario: La tarea fire-and-forget no es cancelada por el recolector de basura
- **WHEN** se dispara la notificación a N8N mediante una tarea asíncrona fire-and-forget
- **THEN** la tarea conserva una referencia retenida hasta completar y el webhook efectivamente se invoca
