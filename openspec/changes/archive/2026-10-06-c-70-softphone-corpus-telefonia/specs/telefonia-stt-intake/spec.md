# Delta for telefonia-stt-intake

## ADDED Requirements

### Requirement: Correlacion opcional del ingreso con un caso del corpus

El backend SHALL aceptar un `corpus_case_id` opcional en el webhook de voz pre-llamada, proveniente de un parametro custom de la llamada, y SHALL propagarlo al callback de estado de grabacion para que el ingreso quede correlacionado con su caso del corpus. La propagacion SHALL usar un store keyed-by-CallSid materializado en una tabla de vida corta de PostgreSQL (`telefonia_pending_call`): el webhook de voz SHALL persistir el mapeo `call_sid -> corpus_case_id` (upsert por `call_sid`) y el callback de estado de grabacion SHALL resolver el `corpus_case_id` por `call_sid`, SHALL borrar la fila pendiente tras resolverla y SHALL purgar las filas mas viejas que la ventana acotada de la llamada. La propagacion MUST NOT introducir dependencias nuevas. El ingreso de telefonia SHALL persistir el `corpus_case_id` como una columna nullable cuando sella `ingresado_en`, tanto en el alta nueva como en el reproceso de un ingreso en estado terminal de error. La ausencia del parametro SHALL ser valida y MUST NOT bloquear ni alterar el flujo de una llamada de produccion. El `corpus_case_id` MUST NOT sustituir ni modificar `call_sid` (clave de idempotencia) ni `origen_message_id` del incidente (que sigue siendo el `CallSid`), y MUST NOT alterar ninguna de las garantias de idempotencia, reintento, reserva de la guarda, descarga, transcripcion, pseudonimizacion ni handoff ya especificadas.

#### Scenario: El caso de corpus viaja del webhook de voz al ingreso

- **WHEN** una llamada llega al webhook de voz con un `corpus_case_id` y su grabacion queda disponible
- **THEN** el webhook persiste `call_sid -> corpus_case_id` en la tabla corta `telefonia_pending_call`, el callback de estado de grabacion lo resuelve por `call_sid`, borra la fila pendiente y el ingreso lo persiste junto con su `ingresado_en`

#### Scenario: El mapeo de la tabla corta es efimero

- **WHEN** el callback de estado de grabacion resuelve el `corpus_case_id` de un `call_sid`
- **THEN** la fila pendiente se borra al resolverla y cualquier fila vencida se purga, de modo que el mapeo no persiste mas alla de la ventana acotada de la llamada

#### Scenario: Sin caso de corpus el ingreso es valido

- **WHEN** una llamada llega sin `corpus_case_id`
- **THEN** el ingreso se procesa con `corpus_case_id` nulo sin bloquearse ni comportarse distinto de una llamada de produccion

#### Scenario: El reproceso preserva el caso de corpus

- **WHEN** un ingreso con `corpus_case_id` queda en un estado terminal de error y un callback repetido lo reprocesa
- **THEN** el reproceso preserva el `corpus_case_id` y el `ingresado_en` original

#### Scenario: La idempotencia y el origen del alta no cambian

- **WHEN** se persiste un ingreso con `corpus_case_id`
- **THEN** `call_sid` sigue siendo la clave unica de idempotencia del ingreso y el incidente conserva el `CallSid` como `origen_message_id`
