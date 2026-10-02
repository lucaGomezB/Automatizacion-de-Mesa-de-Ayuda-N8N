## Why

El corpus de tesis NO es cargable: los 200 casos de `data/corpus_evaluacion_pseudonimizado.json` tienen `tiempo_automatizado_s = null`, y `evaluation/corpus.py::_a_float` rechaza null. Sin tiempos automaticos numericos, el framework de evaluacion y el Capitulo 7 no pueden reportar la latencia del sistema. El harness existente (`scripts/corpus_ingest/ingest_corpus.py`) mide un POST DIRECTO al backend: no ejercita el flujo real de N8N ni la espera del poller de correo, y por lo tanto no produce las mediciones end-to-end que la tesis necesita.

## What Changes

- Nuevo harness `scripts/corpus_ingest/ingest_via_n8n.py` que ingesta el corpus POR el flujo N8N real:
  - **Web**: POST al webhook `incidente-web`; lectura del incidente por `id` para tomar `ingresado_en`/`persistido_en`.
  - **Correo**: envio SMTP al buzon dedicado; trigger IMAP (`everyMinute`) procesa; el harness sondea el backend y lee los instantes.
- **Metrica hibrida (opcion D)**: `t_pipeline_s = latencia_e2e_ms/1000`, `t_espera_s = ingresado_en - t_envio`, `t_e2e_s = persistido_en - t_envio`. `tiempo_automatizado_s = t_e2e_s` para web y correo. La descomposicion se reporta por canal segun `docs/medicion-latencia-e2e.md` §5.
- **Chequeo secundario de confirmacion (OQ4)**: el correo de confirmacion al remitente se observa por un camino de recepcion SEPARADO (carpeta/buzon dedicado no leido por el trigger de ingesta) para no contaminar el corpus; la medicion primaria sigue siendo los instantes de la API.
- **Write-back (OQ3)**: columna existente `TIempo de Registro Automatico (Segundos)` + columnas nuevas `Tiempo pipeline (s)` y `Tiempo espera (s)` + `Latencia e2e (ms)` en XLSX Y CSV (ambos); sidecar JSON sin descripciones; merge de `tiempo_automatizado_s` numerico en el JSON de evaluacion (sin debilitar `_a_float`).
- **Prerrequisitos**: procedimiento para activar el workflow N8N y cablear credenciales IMAP/SMTP/operador; login desde env (`INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD`); camino de confirmacion separado.
- **Dependencia c-69 (OQ2/OQ6)**: dedup web y correlacion exacta de correo los resuelve el change hermano `c-69-dedup-correlacion-altas`, prerequisito de c-68 para la corrida completa. La ventana temporal queda solo como fallback documentado.
- Tests unitarios offline (TDD) de la logica pura: metrica, payload, Message-ID, mapeo de canal, escritores y chequeo de confirmacion.
- **Telefono (OQ5)**: el harness cubre SOLO web+correo (119 casos). Los 81 casos de `llamada telefonica` los mide y carga el autor MANUALMENTE. El harness reporta el conteo de casos aun nulos (telefono pendiente) y NUNCA sobrescribe un `tiempo_automatizado_s` no nulo con null.

## Capabilities

### New Capabilities

- `corpus-n8n-ingest`: contrato del camino de ingesta del corpus por el flujo N8N real (web y correo), derivacion de la metrica hibrida de latencia por canal, write-back a XLSX/CSV/JSON, chequeo secundario por correo de confirmacion, y garantias de privacidad de las descripciones.

### Modified Capabilities

- None. `evaluation-corpus` ya exige `tiempo_automatizado_s` numerico (CORPUS-012): este change lo satisface sin cambiar el spec. `e2e-timing-instrumentation` y `dry-run-harness` se consumen como fuente de verdad, sin modificar requerimientos.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `scripts/corpus_ingest/ingest_via_n8n.py` | New | Harness de ingesta por el flujo N8N real |
| `scripts/corpus_ingest/test_ingest_via_n8n.py` | New | Tests offline de la logica pura |
| `scripts/corpus_ingest/README.md` | Modified | Documentar el harness y el runbook |
| `data/Corpus Tesis.xlsx`, `data/Corpus Tesis - Hoja 1.csv` | Modified | Tiempos + columnas de descomposicion |
| `data/corpus_evaluacion_pseudonimizado.json` | Modified | `tiempo_automatizado_s` numerico (merge) |
| `data/corpus_resultados_n8n.json` | New | Sidecar sin descripciones |
| `n8n/workflow.json` | Config | Activacion e IDs de credenciales (placeholder -> real) |
| `docs/como_cargar_datos_corpus.md`, `docs/medicion-latencia-e2e.md` | Modified | Referenciar el camino N8N y la metrica D |

## Open Questions

1. **OQ1 (RESUELTA)** — Canonico de correo: `tiempo_automatizado_s = t_e2e_s` (poller-inclusivo), con `t_espera_s` aparte y `t_pipeline_s` como cota inferior (D1).
2. **OQ2 (DELEGADA a c-69)** — Dedup web: lo resuelve `c-69-dedup-correlacion-altas`, prerequisito de c-68.
3. **OQ3 (RESUELTA)** — Descomposicion: columnas nuevas en XLSX Y CSV (`Tiempo pipeline (s)`, `Tiempo espera (s)`, `Latencia e2e (ms)`) ademas del sidecar (D5).
4. **OQ4 (RESUELTA)** — Confirmacion de correo: chequeo end-to-end secundario por camino de recepcion separado (D14).
5. **OQ5 (RESUELTA)** — Telefono: 81 valores cargados manualmente por el autor; el harness cubre web+correo (119) y reporta el conteo de nulos pendientes (D5).
6. **OQ6 (DELEGADA a c-69)** — Correlacion exacta de correo via contrato de lectura de c-69; ventana temporal solo como fallback documentado (D3).

## Dependencies

- **`c-69-dedup-correlacion-altas` (prerequisito)**: dedup web y correlacion exacta de correo (contrato de lectura). Gatea la corrida completa, no la implementacion del harness.
- **Autor (manual)**: carga de los 81 valores de `llamada telefonica`; gatea unicamente la carga COMPLETA del JSON de evaluacion.
- N8N activo con credenciales IMAP/SMTP/operador y camino de confirmacion separado (D10/D14).

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Doble conteo por re-run de web (sin dedup) | High | Dedup web delegado a c-69 (prerequisito); hasta entonces, corrida unica documentada |
| Correlacion de correo ambigua | Med | Correlacion exacta via contrato de lectura de c-69; fallback por ventana con buzon dedicado e ids reclamados |
| Confirmacion re-ingestada por el poller contamina el corpus | Med | Camino de recepcion separado obligatorio, verificado antes de correr (D14) |
| Corrida parcial deja el JSON sin cargar | Med | Merge idempotente; reporte de casos aun nulos (telefono); no escribir null |
| Fuga de PII de descripciones | Med | Nunca log/print/sidecar; default sobre el JSON pseudonimizado |
| Activacion de N8N con credenciales reales | Med | Runbook explicito; login desde env; sin secretos en el repo |
| Latencias anomalas contaminan el corpus | Low | Excluir casos con `latencia_anomala`/valor nulo; reportarlos |

## Rollback Plan

Revertir el commit elimina el harness y sus tests. Los archivos del corpus (`data/`) NO estan trackeados en git: restaurar el respaldo previo de `data/` si se corrio escritura (el harness opera con `--dry-run` por defecto para el smoke). Revertir las credenciales/activacion de N8N a su estado previo (workflow inactivo, placeholders). No hay migracion de esquema ni cambios en `App/**`.

## Success Criteria

- [ ] El harness ingesta web y correo por el flujo N8N real y deriva `t_pipeline_s`, `t_espera_s`, `t_e2e_s` por caso.
- [ ] XLSX Y CSV reciben `tiempo_automatizado_s` y las columnas nuevas `Tiempo pipeline (s)`/`Tiempo espera (s)`; el sidecar no contiene descripciones.
- [ ] La confirmacion de correo se observa por un camino separado y se reporta como chequeo secundario sin romper la medicion primaria.
- [ ] `data/corpus_evaluacion_pseudonimizado.json` carga en `evaluation/corpus.py` sin debilitar `_a_float` UNA VEZ COMPLETO (web+correo por el harness + 81 telefono del autor); antes se reporta el conteo de nulos pendientes.
- [ ] Los tests offline del harness pasan y cubren metrica, payload, Message-ID, mapeo, escritores y confirmacion (RED/GREEN/TRIANGULATE/REFACTOR).
- [ ] `openspec validate --strict --changes c-68-corpus-ingesta-n8n` pasa.

## Governance

- **Governance**: MEDIO (pipeline de medicion que produce evidencia de tesis; escribe sobre el corpus y activa el workflow N8N). Las decisiones OQ1/OQ3/OQ4/OQ5 ya estan resueltas; la corrida completa queda gateada por la dependencia c-69 y por el completado manual de telefono.
