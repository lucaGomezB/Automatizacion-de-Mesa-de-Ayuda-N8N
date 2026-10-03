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

### D2: Propagacion del `corpus_case_id` (OQ1)

El parametro custom se origina en el softphone (`device.connect({ params: { corpus_case_id } })`), llega al webhook de voz y debe alcanzar el callback de grabacion. Dos opciones:

- **Opcion A (recomendada): query param en la URL del callback.** El webhook de voz (`/cost-guard/twilio/voice`) recibe `corpus_case_id` como campo de formulario y `render_twiml_allowed(base_url, corpus_case_id)` lo agrega urlencoded a `recordingStatusCallback="{base}/api/v1/telefonia/recording-status?corpus_case_id=..."`. El endpoint `/recording-status` lo lee de `request.query_params`. Ventaja: sin estado nuevo. Caveat: la `X-Twilio-Signature` se calcula sobre la URL completa (con query); el backend valida con `str(request.url)`, de modo que debe verificarse que la firma sigue validando con el query param agregado.
- **Opcion B (fallback): store keyed-by-CallSid.** El webhook de voz (que ya recibe `CallSid`) persiste `CallSid -> corpus_case_id` en una tabla corta/Redis; el callback lo resuelve por `CallSid`. Evita el manejo de query en la firma, a costa de un store y su limpieza.

El design deja la eleccion en **OQ1**; los tests cubren la propagacion de forma independiente del mecanismo.

### D3: Selector del caso y listado en el softphone (OQ3)

`mint_token.py serve` agrega `GET /corpus-cases` que lee `data/corpus_evaluacion_pseudonimizado.json` (ruta configurable por `--corpus-json`) y devuelve `[{id, descripcion}]` filtrando los casos de canal telefonico de forma tolerante (via `map_canal`-like: `"llamada telefonica"`, `"llamada telefónica"`, `"telefono"`). `softphone.html` agrega un `<select>` por defecto vacio y muestra la descripcion del caso seleccionado para recitar; en `device.connect()` envia `{ params: { corpus_case_id } }` solo si hay seleccion. El servidor ya escucha solo en loopback, por lo que el listado no requiere auth adicional; las descripciones (pseudonimizadas) nunca se loguean. La variante "embebida vs endpoint" y la necesidad de auth quedan en **OQ3**.

### D4: Metrica canonica de telefonia y `t_espera_s` (OQ4)

`tiempo_automatizado_s = latencia_e2e_ms / 1000` (fuente unica: `IncidenteRead.latencia_e2e_ms`). En telefonia `ingresado_en` = recepcion del callback, por lo que `t_e2e_s = t_pipeline_s = latencia_e2e_ms/1000` y NO hay espera del cliente: `t_espera_s` no es medible. Se decide escribirla VACIA/N-A (no 0, para no fabricar un valor inexistente) y documentarlo. El script construye un `CaseResult` con `t_espera_s=None`, de modo que los escritores existentes (`write_csv_results`/`write_xlsx_results`) la omiten sin tocar la celda. **OQ4** pide confirmar vacio/N-A vs 0.

### D5: Recuperacion de la medicion y auth (OQ5)

El script necesita el ULTIMO ingreso de un `corpus_case_id` y la latencia del incidente vinculado. Opciones:

- **Opcion 1 (recomendada): camino de lectura dedicado en telefonia.** `GET /api/v1/telefonia/ingresos?corpus_case_id=X&latest=true` (routes -> services -> repositories) devuelve el ingreso con la metrica del incidente vinculado. Coincide con la semantica "ultimo ingreso".
- **Opcion 2: exposicion en `IncidenteRead` + filtro exacto del listado** (patron c-69), resolviendo el join incidente -> ingreso por `origen_message_id = call_sid`.

Ambas exigen JWT de un operador `administrador_directorio`. **OQ5** decide. El script lee credenciales solo del entorno.

### D6: Write-back reutilizando el harness existente

`scripts/corpus_ingest/ingest_telefonia_corpus.py` importa y reutiliza `ingest_via_n8n` (`CaseResult`, `_should_write_metric`, `write_csv_results`, `write_xlsx_results`, `write_sidecar_json`, `merge_evaluation_json`) y `map_canal`. Escribe solo resultados de telefonia, de modo que no pisa web/correo. Reglas duras: no escribe `null` sobre un valor existente, excluye anomalos, nunca toca `_a_float`, nunca loguea descripciones.

### D7: `--replace` (OQ6)

Sin `--replace`: recupera el ultimo ingreso, actualiza el valor del corpus y conserva las filas previas. Con `--replace`: elimina el/los ingreso(s) e incidente(s) previos de ese `corpus_case_id` (dejando solo el ultimo) y reemplaza el valor. FK relevantes: `telefonia_ingreso.incidente_id` es `SET NULL` y `clasificacion_log.incidente_id` es `CASCADE`; el borrado debe eliminar el ingreso y el incidente en el orden correcto para no dejar huerfanos ni filas hijas. El borrado es destructivo (governance ALTO): dry-run por defecto y aprobacion del autor. El alcance "solo por `corpus_case_id`" y el manejo de hijas quedan en **OQ6**.

### D8: Perfil Compose `corpus` (OQ2)

Perfil que corre el flujo telefonico contra una base DESCARTABLE. Forma recomendada: servicios `postgres-corpus` (base `mesa_de_ayuda_corpus`, volumen propio), `backend-corpus` (`DATABASE_URL` -> `postgres-corpus`, `alembic upgrade head`) y `n8n-corpus` (`BACKEND_URL` -> `backend-corpus`, volumen propio), todos bajo `profiles: ["corpus"]`. Wipe con `docker compose --profile corpus down -v` (borra solo los volumenes del corpus). La Voice URL del TwiML App se conmuta MANUALMENTE a la URL publica del backend del corpus durante la corrida (ngrok/tunel propio) y se restaura al terminar. Tradeoffs: mas servicios que mantener y doble N8N; a cambio, aislamiento total y wipe limpio. Si el split completo es ambiguo (reusar nginx/ngrok/n8n del stack base), **OQ2** lo decide.

### D9: Cobertura completa de los 81 casos

No hay modo muestra. El autor recita cada uno de los 81 casos; el script reporta medidos/pendientes/anomalos. El gate final es la carga del JSON de evaluacion sin `CorpusError`.

### D10: TDD y verificacion

Backend y logica pura del script con RED-GREEN-TRIANGULATE-REFACTOR. La propagacion, la persistencia, el filtro/lectura y el write-back se testean sin red (SQLite + mocks), con casos borde: sin `corpus_case_id`, reproceso, anomalia, merge idempotente, `--replace`.

### D11: Gobernanza

ALTO: esquema de backend, parametros de llamada Twilio, infra de base descartable y credenciales. Las decisiones sensibles (OQ1..OQ6) se elevan al autor; `--replace` y el wipe no se ejecutan sin aprobacion.

### D12: Numero de migracion (colision con C-60)

El head actual es `010`; C-60 (activo, 0/33) introducira la `011`. Dos changes sin aplicar no pueden reclamar el mismo numero. La migracion de c-70 se numera en APPLY segun el head real (hoy `011_add_telefonia_corpus_case_id`, `down_revision = "010"`, ajustando a `012` si C-60 aterriza primero). El propose no crea archivos de migracion.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|--------|------------|
| La firma Twilio falla con query param en el callback (Opcion A) | Verificacion temprana; fallback Opcion B keyed-by-CallSid |
| `--replace` borra de mas | Borrado acotado por `corpus_case_id` + dry-run + aprobacion |
| El perfil `corpus` no aisla la base | Base y volumenes dedicados + wipe verificado |
| La metrica difiere de otros canales | Misma fuente (`IncidenteRead.latencia_e2e_ms`); `t_espera_s` N/A documentada |
| Colision de migracion con C-60 | Numero asignado en apply segun el head |

## Migration Plan

1. Migracion aditiva `corpus_case_id` (nullable) + modelo + repositorio.
2. Backend tolerante: propagacion y persistencia del param (nunca obligatorio).
3. Softphone: listado + selector (retrocompatible: sin seleccion no envia param).
4. Script de recuperacion/write-back con dry-run.
5. Perfil `corpus` + runbook.
6. Corrida del autor (81 casos) y `--replace` segun OQ6.

`downgrade`: dropea la columna; no restaura datos de negocio. Sin backfill.

## Open Questions

- **OQ1**: mecanicmo de propagacion (Opcion A query param vs Opcion B store keyed-by-CallSid) y limitaciones de Twilio (firma, longitud de URL, disponibilidad de params custom en `<Record>`).
- **OQ2**: alcance del perfil `corpus` (stack completo vs backend+postgres; reusar nginx/ngrok/n8n del stack base?), conmutacion de la Voice URL y wipe.
- **OQ3**: listado de casos servido por endpoint vs embebido y necesidad de auth en la GUI.
- **OQ4**: `t_espera_s` vacio/N-A vs 0 y confirmacion del escritor para telefonia.
- **OQ5**: auth de recuperacion y si el camino de lectura expone `corpus_case_id` (camino dedicado vs `IncidenteRead` + filtro).
- **OQ6**: alcance de `--replace` (solo por `corpus_case_id`) e implicaciones de FK/tablas hijas (`clasificacion_log`, `telefonia_ingreso`).
