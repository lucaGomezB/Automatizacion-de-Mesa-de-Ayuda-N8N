## ADDED Requirements

### Requirement: Reanudacion idempotente de la corrida del brazo automatizado

El harness `scripts/corpus_ingest/ingest_via_n8n.py` SHALL persistir el sidecar de trazabilidad de forma INCREMENTAL tras CADA caso procesado por el recorrido de ingesta, y no solamente al final de la corrida, de modo que una corrida interrumpida conserve la trazabilidad de todos los casos ya procesados. La escritura incremental SHALL reutilizar la semantica de merge por `case_id` ya existente en `write_sidecar_json` (entradas de casos ausentes preservadas, entrada existente reemplazada solo por un resultado valido) sin cambiarla. Al iniciar, el harness SHALL cargar el sidecar objetivo y, cuando el ledger corresponda a la MISMA corrida (`id_corrida`), SHALL SALTAR todo `case_id` que ya tenga una entrada VALIDA (sin error y no anomala, consistente con `_should_write_metric`), reutilizando la medicion almacenada sin volver a enviar el caso. El harness SHALL ofrecer un modo de reanudacion explicito (`--resume`) que, ANTES de enviar un caso, consulte la existencia de un incidente por la clave de correlacion determinista del caso (correo: `Message-ID` normalizado; web: `corpus-<ID>`) usando el contrato de lectura exacto por `origen_message_id` provisto por c-69. Si el incidente ya existe y el sidecar NO tiene una entrada valida para el caso (residuo de una corrida interrumpida), el harness MUST NOT reenviar el caso y MUST registrarlo con una etiqueta de error explicita de incidente preexistente; en ese caso MUST NOT escribir ni inferir `t_e2e_s`, `t_espera_s` ni `t_pipeline_s`. El harness SHALL conservar el guard `min_ingresado_en` de la correlacion (anti-incidente-viejo). Sin `--resume`, el comportamiento por defecto SHALL permanecer identico al previo a este change.

#### Scenario: El sidecar incremental sobrevive a una interrupcion

- **WHEN** una corrida procesa casos y se interrumpe despues de N casos validos (sin llegar al final del recorrido)
- **THEN** el sidecar ya contiene N entradas validas para esos casos y ninguna entrada de caso procesado se pierde

#### Scenario: La reanudacion salta los casos ya medidos y procesa los nuevos

- **WHEN** se reanuda una corrida con el MISMO `id_corrida` sobre un sidecar que ya tiene entradas validas para una parte de los casos
- **THEN** el harness NO reenvia los `case_id` con entrada valida (reutiliza su medicion almacenada) y si procesa y envia los casos que aun no tienen entrada para esa corrida

#### Scenario: Un incidente preexistente sin medicion no se reenvia y se declara

- **WHEN** con `--resume` el sondeo de pre-envio encuentra un incidente ya existente cuya `ingresado_en` es anterior al envio y el sidecar no tiene una entrada valida para ese caso
- **THEN** el harness NO reenvia el caso, lo registra con una etiqueta de error de incidente preexistente, y no reporta `timeout_correlacion`, no lo marca `anomalo` y no escribe ningun `t_e2e_s`/`t_espera_s`/`t_pipeline_s`

#### Scenario: Sin el modo de reanudacion la conducta no cambia

- **WHEN** el harness corre sin `--resume`
- **THEN** se comporta como antes de este change para la seleccion, el envio y la correlacion de los casos

#### Scenario: El guard anti-incidente-viejo se mantiene

- **WHEN** el harness correlaciona un caso por su clave determinista
- **THEN** sigue exigiendo que el `ingresado_en` del incidente sea posterior al instante de envio, de modo que un incidente viejo no se acredita como el incidente del caso
