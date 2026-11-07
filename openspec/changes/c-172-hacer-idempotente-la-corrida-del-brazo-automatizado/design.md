## Context

Ver `proposal.md` — Why. Estado actual verificado contra el codigo (2026-11-05):

- `run` (`scripts/corpus_ingest/ingest_via_n8n.py:1255`) recorre `selected` en un `for` (`:1331-1382`), acumula `results` y llama a `write_sidecar_json` UNA sola vez, despues del loop (`:1386`). Si el proceso muere dentro del loop, no hay sidecar.
- En modo campana, `modo_campana.anotar_resultados` (`modo_campana.py:231`) corre DESPUES del loop (`:1384-1385`) y copia `orden/posicion/mitad/brazo_primero/id_corrida` a cada resultado. El `id_corrida` existe por eso solo en el sidecar final.
- `write_sidecar_json` (`:738-775`) mergea por `case_id`: preserva entradas ausentes, reemplaza una entrada existente solo con un resultado valido (`_should_write_metric`, `:601-608`: `error is None and not anomalo`) y agrega un `case_id` nuevo aunque sea invalido.
- `verificar_sidecar_de_corrida` (`:778-800`) ya permite reanudar con el MISMO `id_corrida` y rechaza un sidecar de otra corrida; `modo_campana.preflight` (`modo_campana.py:151`) lo invoca antes de leer credenciales.
- Correlacion: correo usa `correlation_keys(case_id, domain)` (`:241-250`) y `find_incidente_by_origen` (`:1026-1070`) con el guard `min_ingresado_en` (`select_correlated_incident`, `:253-267`); web usa `build_web_payload` (`:208-220`, `origen_message_id = corpus-<ID>`) y correlaciona por el `incidente_id` devuelto por el webhook (`ingest_web_case`, `:951-1005`).
- `min_ingresado_en` es CORRECTO y se conserva: evita acreditar un incidente viejo y mantiene `t_espera_s >= 0`. El defecto es asumir que un reenvio crea un incidente nuevo, cosa que la dedup del backend (`incidente_service.py:315-393`) viola.

## Goals / Non-Goals

**Goals:**

- Que una corrida interrumpida conserve la trazabilidad de los casos ya procesados (ledger incremental).
- Que una re-corrida con `--resume` no reenvie casos ya medidos y no fabrique mediciones para residuos preexistentes (politica B1).
- Mantener la conducta por defecto EXACTAMENTE igual (sin `--resume`).

**Non-Goals:**

- No cambiar el backend, la DB, N8N ni `evaluation/`.
- No cambiar la semantica de merge de `write_sidecar_json`.
- No adoptar un id de correlacion por corrida (crearia incidentes duplicados y romperia la dedup de c-69).
- No tocar `ingest_corpus.py` ni `ingest_telefonia_corpus.py` (telefonia es read-back y ya es idempotente).

## Decisions

### D1. Escritura incremental siempre activa (A)

Se llama a `write_sidecar_json(args.sidecar, [result])` dentro del loop, inmediatamente despues de producir cada `result`. El resultado DEBE ir anotado antes de escribir cuando la corrida es de campana (ver D2), de modo que cada entrada lleve su `id_corrida` y la asignacion del plan. Reutiliza el merge existente sin tocarlo: al final de una corrida completa el sidecar queda identico al de hoy (mejora pura, sin cambio de conducta observable). Trade-off: I/O O(n) con relectura por caso; con n ~ 200 es despreciable y el beneficio (no perder trazabilidad) es el objetivo del change.

### D2. Anotacion por caso en modo campana

Hoy `anotar_resultados` corre una sola vez al final. Con la escritura incremental, cada `result` se anota con `modo_campana.anotar_resultados([result], seleccion.asignaciones, args.id_corrida)[0]` ANTES de persistirlo. Asi el ledger incremental ya trae `id_corrida/posicion/mitad/brazo_primero/orden` y la reanudacion (D3) puede filtrar por `id_corrida`. Fuera de campana no hay anotacion (los cinco campos quedan `None`).

### D3. Reanudacion explicita tras `--resume` (B)

Se agrega `--resume` (`store_true`) a `parse_args`. Sin el flag, no hay skip ni sonda. Con `--resume`, antes del loop:

1. Se cargan las entradas del sidecar objetivo con `_load_sidecar_entries` y se arma el conjunto de `case_id` con entrada VALIDA (`_should_write_metric` sobre un `CaseResult` reconstruido) cuyo `id_corrida` coincide con la corrida actual (en modo no-campana, `id_corrida is None` coincide con entradas del harness sin corrida).
2. Por cada caso del loop: si su `case_id` esta en el conjunto, se SALTA el envio y se reutiliza la medicion almacenada (no se agrega un resultado nuevo; ya esta en el sidecar).
3. Si no esta en el conjunto, se SONDEA la preexistencia (D4) antes de enviar.

### D4. Sonda de preexistencia sin el guard de ingreso

La sonda NO puede usar `find_incidente_by_origen` tal cual: su `min_ingresado_en` RECHAZARIA justamente el incidente preexistente que queremos detectar. Se agrega un helper single-shot `probe_existing_incident(session, base_url, token, keys, verify, timeout, backoff)` que hace UNA consulta por clave al filtro exacto `origen_message_id` (sin poll, sin guard) y devuelve el primer incidente listado o `None`. Claves: correo `correlation_keys(case_id, domain)`; web `[payload["origen_message_id"]]` (`corpus-<ID>`). Si hay incidente:

- si el `case_id` ya tenia entrada valida → ya se salto en D3.3 (no se llega aqui);
- si NO → se construye un `CaseResult` con `error="incidente_preexistente_sin_t_envio"`, `incidente_id` del hallado, `t_envio` en el instante del intento y TODAS las metricas (`t_pipeline_s`, `t_espera_s`, `t_e2e_s`, `latencia_e2e_ms`) en `None`, y NO se envia. Al ser `error is not None`, `_should_write_metric` es falso: no reemplaza una entrada valida previa y, si el `case_id` es nuevo, se agrega y queda declarado. Politica B1: excluir y declarar, nunca inventar una medicion.

Si la sonda no encuentra incidente, se procede con `ingest_web_case`/`ingest_email_case` como hoy (con su guard `min_ingresado_en` intacto).

### D5. Alternativa descartada: id de correlacion por corrida

Un `origen_message_id`/`Message-ID` que incluya `id_corrida` forzaria un incidente NUEVO por corrida: duplicaria altas y romperia el invariante de dedup de c-69 y la correlacion exacta del harness. Descartada.

### D6. Alternativa descartada: skip siempre activo

Saltar casos ya medidos sin flag cambiaria la conducta por defecto de una re-corrida (hoy reenvia todo). Se exige `--resume` para preservar la postura aditiva de c-166.

## Risks / Trade-offs

- La sonda agrega un GET por caso no salteado cuando `--resume` esta activo → mitigado: solo con el flag y reutiliza el filtro exacto indexado de c-69.
- Reconstruir `CaseResult` desde el JSON del sidecar para evaluar validez → mitigado: `_load_sidecar_entries` ya tolera entradas corruptas y solo los campos usados por `_should_write_metric` (`error`, `anomalo`) importan.
- I/O incremental O(n) con relectura → mitigado: n ~ 200; el merge es la garantia de correccion.
- Un residuo podria confundirse con medible → mitigado: B1 lo registra con `error` y sin metricas; `_should_write_metric` lo excluye.

## Migration Plan

Aditivo y retrocompatible: sin `--resume` los harnesses se comportan como hoy y el sidecar final es identico (la escritura incremental no cambia el contenido final). Rollback: quitar `--resume`, la sonda y el skip, y volver a llamar `write_sidecar_json` solo al final. No hay migracion de datos. Los 17 incidentes de la corrida interrumpida no se "refrescan": con `--resume` quedan declarados como preexistentes/no medibles, y el plan de campana es resetear la DB antes de la corrida definitiva.

## Open Questions

- Ninguna abierta. Resuelta: el skip por sidecar se gatea detras de `--resume` (D3/D6) para no alterar la conducta por defecto; la sonda no aplica el guard `min_ingresado_en` (D4) porque su objetivo es detectar el residuo, mientras que el guard se conserva en el camino de envio.
