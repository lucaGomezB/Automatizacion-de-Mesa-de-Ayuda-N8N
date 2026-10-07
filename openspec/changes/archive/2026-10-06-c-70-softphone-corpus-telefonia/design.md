# Design — c-70-softphone-corpus-telefonia

## Context

C-59 (archivado 2026-10-01) dejo un softphone VoIP de navegador que inyecta la voz del operador en el flujo telefonico real de C-52. C-68 (activo) mide web y correo por el flujo N8N real y dejo los 81 casos de `llamada telefonica` FUERA DE ALCANCE, a cargo manual del autor. Cargarlos manualmente sin correlacion exacta rompe la trazabilidad y la comparabilidad por canal que exige `docs/medicion-latencia-e2e.md` §5.

El flujo real de telefonia (C-52):

```
softphone -> TwiML App Voice URL -> backend /cost-guard/twilio/voice
   -> <Record recordingStatusCallback=/telefonia/recording-status>
   -> callback: backend sella ingresado_en -> descarga -> STT -> pseudonimiza
   -> handoff n8n -> alta incidente (origen_message_id = CallSid) -> persistido_en
```

La metrica canonica de la tesis es `tiempo_automatizado_s = latencia_e2e_ms / 1000`, con `latencia_e2e_ms = persistido_en - ingresado_en` derivada en `IncidenteRead`. En telefonia `ingresado_en` se sella en la recepcion del callback (no en el inicio de la llamada).

## Goals / Non-Goals

**Goals**
- Correlacion EXACTA llamada <-> caso del corpus por `corpus_case_id`.
- Medir los 81 casos por el flujo real y escribir `tiempo_automatizado_s` con la misma metrica canonica que los otros canales.
- Aislar la corrida en una base descartable que no contamine la operativa.
- Reutilizar el write-back, el merge/skip y la privacidad de `ingest_via_n8n.py`.

**Non-Goals**
- No se reproduce audio del caso (el autor recita): no hay TTS ni playback.
- No se mide desde el inicio de la llamada (Voice Insights queda para Fase 2, `docs/medicion-latencia-e2e.md` §5).
- No se toca `call_sid` ni `origen_message_id` ni el flujo de produccion.
- No se modifica `evaluation/corpus.py::_a_float`.

## Decisions

### D1: `corpus_case_id` nullable en `telefonia_ingreso` (persistencia)

Se agrega `corpus_case_id: Mapped[str | None]` (String(64), nullable, indexado) al modelo `TelefoniaIngreso` y a la migracion Alembic. Es ADITIVA y sin backfill: las filas historicas quedan nulas. Se persiste al sellar `ingresado_en` en el alta nueva (`_create_new`) y se preserva en el reproceso. NO se agrega a `incidente`: la correlacion vive en el ingreso y se resuelve por join/consulta. El indice acelera la recuperacion del ultimo ingreso por caso.

### D2: Propagacion del `corpus_case_id` (OQ1 = Opcion B, resuelta)

El parametro custom se origina en el softphone (`device.connect({ params: { corpus_case_id } })`) y llega al webhook de voz (`/cost-guard/twilio/voice`) junto con `CallSid`. La propagacion elegida es un STORE KEYED-BY-CallSid materializado en una TABLA DE VIDA CORTA de PostgreSQL, sin dependencias nuevas:

1. El webhook de voz persiste `call_sid -> corpus_case_id` en la tabla corta `telefonia_pending_call` (upsert por `call_sid`).
2. El callback `/telefonia/recording-status` (que ya recibe `CallSid`) resuelve `corpus_case_id` por `call_sid`, lo pasa al servicio para persistirlo al sellar `ingresado_en` y BORRA la fila pendiente.

La tabla `telefonia_pending_call` tiene `call_sid` (String, primary key/unique), `corpus_case_id` (String(64)) y `created_at` (UTC timezone-aware), sin PII. Se implementa con SQLAlchemy 2.0 async y se encapsula tras una interfaz de repositorio (`upsert/get/delete/purge`) para testearla sin red (SQLite + fixtures). El ciclo de vida se acota con TTL: ademas del borrado explicito en el callback, se purgan las filas mas viejas que la ventana de la llamada (orden de minutos) para que nunca se acumulen filas huerfanas. La tabla viaja en la MISMA migracion Alembic que la columna `telefonia_ingreso.corpus_case_id` (ver D12); el propose no crea el archivo de migracion.

Se DESCARTA la Opcion A (query param urlencoded en `recordingStatusCallback`) porque exigiria que la firma Twilio siga validando sobre la URL con query; tambien se descarta depender de cambios de firma. Tradeoff: se agrega una tabla y su ciclo de vida (TTL + limpieza), a cambio de no tocar la URL del callback ni la firma y de NO introducir ninguna dependencia nueva. La tabla corta reutiliza la infraestructura PostgreSQL ya presente y NO agrega un cliente externo ni un servicio adicional al backend.

### D3: Selector del caso y listado en el softphone (OQ3 = endpoint, resuelta)

`mint_token.py serve` agrega `GET /corpus-cases` que lee `data/corpus_evaluacion_pseudonimizado.json` (ruta configurable por `--corpus-json`) y devuelve `[{id, descripcion}]` filtrando los casos de canal telefonico de forma tolerante (via `map_canal`-like: `"llamada telefonica"`, `"llamada telefónica"`, `"telefono"`). `softphone.html` agrega un `<select>` por defecto vacio y muestra la descripcion del caso seleccionado para recitar; en `device.connect()` envia `{ params: { corpus_case_id } }` solo si hay seleccion. El servidor escucha solo en loopback, por lo que el listado no requiere auth adicional; las descripciones (pseudonimizadas) nunca se loguean. Se descarta la variante embebida: el endpoint mantiene una unica fuente de verdad (el JSON pseudonimizado) y evita duplicar la lista en el HTML.

### D4: Metrica canonica de telefonia y `t_espera_s` (OQ4 = vacio/N-A, resuelta)

`tiempo_automatizado_s = latencia_e2e_ms / 1000` (fuente unica: `IncidenteRead.latencia_e2e_ms`). En telefonia `ingresado_en` = recepcion del callback, por lo que `t_e2e_s = t_pipeline_s = latencia_e2e_ms/1000` y NO hay espera del cliente: `t_espera_s` no es medible. Decision: escribirla VACIA/N-A (no 0, para no fabricar un valor inexistente) y documentarlo. El script construye un `CaseResult` con `t_espera_s=None`, de modo que los escritores existentes (`write_csv_results`/`write_xlsx_results`) la omiten sin tocar la celda.

### D5: Recuperacion de la medicion y auth (OQ5 = Opcion 1, resuelta)

El script necesita el ULTIMO ingreso de un `corpus_case_id` y la latencia del incidente vinculado. Decision: camino de lectura DEDICADO en telefonia, `GET /api/v1/telefonia/ingresos?corpus_case_id=X&latest=true` (routes -> services -> repositories), que devuelve el ingreso con la metrica del incidente vinculado. Coincide con la semantica "ultimo ingreso" y no expone el campo en `IncidenteRead`. Se descarta la Opcion 2 (`IncidenteRead` + filtro exacto del listado). El endpoint exige JWT de un operador `administrador_directorio`; el script lee credenciales solo del entorno.

### D6: Write-back reutilizando el harness existente

`scripts/corpus_ingest/ingest_telefonia_corpus.py` importa y reutiliza `ingest_via_n8n` (`CaseResult`, `_should_write_metric`, `write_csv_results`, `write_xlsx_results`, `write_sidecar_json`, `merge_evaluation_json`) y `map_canal`. Escribe solo resultados de telefonia, de modo que no pisa web/correo. Reglas duras: no escribe `null` sobre un valor existente, excluye anomalos, nunca toca `_a_float`, nunca loguea descripciones.

### D7: `--replace` (OQ6 = confirmada)

Sin `--replace`: recupera el ultimo ingreso, actualiza el valor del corpus y conserva las filas previas. Con `--replace`: elimina SOLO las filas del `corpus_case_id`, dejando unicamente el ultimo ingreso valido, y reemplaza el valor del corpus. Orden FK: `telefonia_ingreso.incidente_id` es `SET NULL` y `clasificacion_log.incidente_id` es `CASCADE`; el borrado elimina el ingreso y el incidente en el orden correcto para no dejar huerfanos ni filas hijas. El borrado es destructivo (governance ALTO): DRY-RUN por defecto y ejecucion solo con aprobacion explicita del autor. No afecta filas de otros `corpus_case_id`.

### D8: Perfil Compose `corpus` (OQ2 = stack aislado completo, resuelta)

Perfil que corre el flujo telefonico contra una base DESCARTABLE. Decision: stack aislado completo con servicios `postgres-corpus` (base `mesa_de_ayuda_corpus`, volumen propio), `backend-corpus` (`DATABASE_URL` -> `postgres-corpus`, `alembic upgrade head`) y `n8n-corpus` (`BACKEND_URL` -> `backend-corpus`, volumen propio), todos bajo `profiles: ["corpus"]`. Wipe con `docker compose --profile corpus down -v postgres-corpus backend-corpus n8n-corpus` (ACOTADO POR SERVICIO). Correccion verificada en apply: como el nombre de proyecto Compose es compartido (`mesa_local`), el comando sin nombres de servicio (`docker compose --profile corpus down -v`) borraria TAMBIEN los volumenes base `mesa_local_postgres_data`/`mesa_local_n8n_data`; por eso el wipe va con los tres nombres de servicio. La Voice URL del TwiML App se conmuta MANUALMENTE a la URL publica del backend del corpus durante la corrida (ngrok/tunel propio) y se restaura al terminar; el runbook documenta ambos pasos. Tradeoffs: mas servicios que mantener y un N8N adicional; a cambio, aislamiento total y wipe acotado. Se descarta reusar el nginx/ngrok/n8n del stack base para no contaminar la operativa.

### D9: Cobertura completa de los 81 casos

No hay modo muestra. El autor recita cada uno de los 81 casos; el script reporta medidos/pendientes/anomalos. El gate final es la carga del JSON de evaluacion sin `CorpusError`.

### D10: TDD y verificacion

Backend y logica pura del script con RED-GREEN-TRIANGULATE-REFACTOR. La propagacion (tabla corta), la persistencia, el filtro/lectura y el write-back se testean sin red con la infraestructura existente (SQLite + fixtures; mocks solo para servicios externos), con casos borde: sin `corpus_case_id`, reproceso, anomalia, merge idempotente, `--replace`.

### D11: Gobernanza

ALTO: esquema de backend, parametros de llamada Twilio, infra de base descartable y credenciales. Las decisiones OQ1..OQ6 fueron resueltas por el autor y quedan como decisiones (no como gating). `--replace` y el wipe son destructivos: dry-run por defecto y ejecucion solo con aprobacion explicita.

### D12: Numero de migracion (colision con C-60)

El head actual es `010`; C-60 (activo, 0/33) introducira la `011`. Dos changes sin aplicar no pueden reclamar el mismo numero. La migracion de c-70 se numera en APPLY segun el head real (hoy `011_add_telefonia_corpus_case_id`, `down_revision = "010"`, ajustando a `012` si C-60 aterriza primero). El propose no crea archivos de migracion.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|--------|------------|
| La tabla corta keyed-by-CallSid no se resuelve o acumula filas | TTL de purga acotado a la ventana de la llamada + borrado explicito en el callback; repositorio tras interfaz mockeable (SQLite) |
| `--replace` borra de mas | Borrado acotado por `corpus_case_id` + orden FK explicito + dry-run por defecto + aprobacion del autor |
| El perfil `corpus` no aisla la base | Base y volumenes dedicados + wipe acotado `--profile corpus down -v postgres-corpus backend-corpus n8n-corpus` verificado |
| La metrica difiere de otros canales | Misma fuente (`IncidenteRead.latencia_e2e_ms`); `t_espera_s` vacio/N-A documentada |
| Colision de migracion con C-60 | Numero asignado en apply segun el head |

## Migration Plan

1. Migracion aditiva `corpus_case_id` (nullable) + modelo + repositorio; en la MISMA migracion, la tabla corta `telefonia_pending_call`.
2. Backend tolerante: tabla corta keyed-by-CallSid + propagacion y persistencia del param (nunca obligatorio).
3. Softphone: listado + selector (retrocompatible: sin seleccion no envia param).
4. Script de recuperacion/write-back con dry-run.
5. Perfil `corpus` + runbook.
6. Corrida del autor (81 casos) y `--replace` (dry-run por defecto; ejecucion con aprobacion).

`downgrade`: dropea la columna y la tabla corta; no restaura datos de negocio. Sin backfill.

## Decisions Resueltas (OQ1..OQ6)

No quedan Open Questions: el autor resolvio OQ1..OQ6 y no hay gating de decision para el apply.

- **OQ1 = Opcion B**: store keyed-by-CallSid materializado en la tabla corta de PostgreSQL `telefonia_pending_call` (TTL de purga acotado + borrado en el callback); sin dependencias nuevas. Ver D2.
- **OQ2 = stack aislado completo**: `postgres-corpus` + `backend-corpus` + `n8n-corpus` bajo `profiles: ["corpus"]`; conmutacion manual de la Voice URL. Ver D8.
- **OQ3 = endpoint**: `GET /corpus-cases` en `mint_token.py serve`; `<select>` vacio por defecto; solo loopback, sin auth adicional. Ver D3.
- **OQ4 = vacio/N-A**: `t_espera_s=None` (no 0); `tiempo_automatizado_s = t_pipeline_s = t_e2e_s`. Ver D4.
- **OQ5 = Opcion 1**: `GET /api/v1/telefonia/ingresos?corpus_case_id=X&latest=true`, JWT `administrador_directorio`. Ver D5.
- **OQ6 = confirmada**: `--replace` solo por `corpus_case_id`, FK `SET NULL`/`CASCADE`, dry-run por defecto. Ver D7.
