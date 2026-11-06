## ADDED Requirements

### Requirement: ECM-014 — Reanudacion idempotente de la corrida de campana del brazo automatizado

En modo campana (`--plan` o `--orden` con `--id-corrida`), el harness `scripts/corpus_ingest/ingest_via_n8n.py` SHALL persistir su sidecar de forma incremental y, al reanudar una corrida con el MISMO `id_corrida`, SHALL saltar los `case_id` ya medidos en lugar de reenviarlos. El ledger incremental MUST seguir siendo por `id_corrida` (la reanudacion de una corrida MUST NOT mezclar ni pisar entradas de otra corrida) y MUST conservar la semantica de merge por `case_id` de `write_sidecar_json`. El harness SHALL aceptar `--resume` para sondear la preexistencia del incidente por el contrato exacto de `origen_message_id` (c-69) antes de enviar; un incidente preexistente sin medicion valida en el ledger SHALL registrarse como no medible, sin reenvio y sin ningun `t_e2e_s` fabricado (politica B1). El harness SHALL documentar en su propia ayuda (`--help`/docstring) que las corridas de campana usan `--resume`. Los harnesses `ingest_corpus.py` e `ingest_telefonia_corpus.py` MUST NOT cambiar con este change. Sin `--resume` la conducta de la corrida de campana SHALL ser la previa a este change.

#### Scenario: La corrida de campana se reanuda con el mismo id_corrida

- **WHEN** una corrida de campana se interrumpe y se relanza con `--resume` y el mismo `--id-corrida` y el mismo `--sidecar`
- **THEN** los casos ya medidos en el sidecar no se reenvian y los casos pendientes si se procesan

#### Scenario: El ledger incremental no mezcla corridas

- **WHEN** el sidecar de la corrida contiene entradas de un `id_corrida` distinto
- **THEN** el harness aborta como hoy (no reanuda contra otra corrida) y solo reanuda cuando el `id_corrida` coincide

#### Scenario: Un residuo de una corrida de campana se declara no medible

- **WHEN** con `--resume` un caso de la corrida de campana encuentra un incidente preexistente y el sidecar no tiene medicion valida para ese caso
- **THEN** el caso queda registrado como no medible con su etiqueta de incidente preexistente y no aporta un `t_e2e_s` inventado al analisis

#### Scenario: La ayuda del harness declara el uso de reanudacion

- **WHEN** un operador consulta `--help` o el docstring del harness
- **THEN** encuentra que las corridas de campana usan `--resume` y que el ledger de reanudacion es por `id_corrida`
