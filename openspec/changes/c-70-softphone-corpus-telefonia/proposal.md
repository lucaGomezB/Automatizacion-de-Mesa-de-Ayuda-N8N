# Proposal: Medicion del corpus de telefonia por el flujo real

## Why

El corpus de tesis tiene 81 casos de `llamada telefonica` con `tiempo_automatizado_s = null`, y el harness `c-68-corpus-ingesta-n8n` los dejo explicitamente FUERA DE ALCANCE para carga manual del autor. Hasta hoy no existe ninguna via reproducible para medir esos 81 casos por el flujo telefonico REAL (grabacion -> STT -> pseudonimizacion -> handoff -> alta), ni para correlacionar de forma EXACTA una llamada con su caso del corpus. Cargarlos "a mano" sin esa correlacion romperia la trazabilidad, la comparabilidad entre canales y la auditoria de la tesis.

## What Changes

- **Softphone (extiende C-59)**: `<select>` en `scripts/voip_softphone/softphone.html` poblado SOLO con los casos telefonicos del corpus (por defecto vacio). El modo `serve` de `mint_token.py` expone la lista de casos telefonicos leyendo `data/corpus_evaluacion_pseudonimizado.json`. El autor RECITA el texto del caso (sin reproduccion de audio) y el id viaja a Twilio como parametro custom de la llamada.
- **Backend (persistencia)**: `telefonia_ingreso` gana una columna nullable `corpus_case_id` (migracion Alembic). El id viaja del softphone al webhook de voz, se propaga al `recordingStatusCallback` y se persiste al sellar `ingresado_en`. NO se toca `call_sid` ni `origen_message_id` (idempotencia intacta).
- **Recuperacion + write-back**: script que lee el ULTIMO `telefonia_ingreso` de un `corpus_case_id`, deriva la metrica desde `latencia_e2e_ms` del incidente vinculado y escribe `tiempo_automatizado_s` en el corpus (CSV + XLSX + JSON), reutilizando el merge/skip y las reglas de privacidad de `ingest_via_n8n.py`.
- **Metrica canonica de telefonia**: `tiempo_automatizado_s = latencia_e2e_ms / 1000 = t_pipeline_s = t_e2e_s`. `t_espera_s` NO es medible en telefonia (el ingreso se sella en la recepcion del callback de grabacion, no en el inicio de la llamada); se deja vacio/N-A y se documenta.
- **`--replace`**: al re-medir un caso, elimina el/los ingresos e incidentes telefonicos previos de ese `corpus_case_id` (conserva solo el nuevo) y reemplaza el valor del corpus.
- **Base descartable (perfil `corpus`)**: perfil de Compose que corre el flujo telefonico contra una base DESCARTABLE (`mesa_de_ayuda_corpus`) con sus propios volumenes, para no contaminar la base de la app y poder limpiarla.
- **Cobertura completa**: los 81 casos los mide el autor (sin muestreo).

## Capabilities

### New Capabilities

- `telefonia-corpus-medicion`: contrato de la corrida de medicion del corpus por telefonia real (base descartable, seleccion/correlacion del caso, metrica canonica de telefonia, recuperacion por `corpus_case_id`, write-back al corpus y reemplazo de mediciones previas).

### Modified Capabilities

- `telephony-test-softphone`: se agrega la seleccion del caso de corpus en el softphone y el endpoint de loopback que sirve la lista de casos telefonicos.
- `telefonia-stt-intake`: se agrega la correlacion opcional del ingreso con un caso del corpus (`corpus_case_id` nullable) propagada desde el webhook de voz y persistida en el ingreso.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/models/telefonia_ingreso.py` | Modified | Columna nullable `corpus_case_id` |
| `App/Backend/alembic/versions/0XX_*.py` | New | Migracion aditiva (numero segun head actual) |
| `App/Backend/app/cost_guard/twiml.py`, `app/routes/cost_guard.py` | Modified | Param custom de voz y propagacion a `recordingStatusCallback` |
| `App/Backend/app/routes/telefonia.py`, `app/schemas/telefonia.py`, `app/services/telefonia_service.py`, `app/repositories/telefonia_ingreso_repository.py` | Modified | Recibir/persistir/leer/borrar por `corpus_case_id` |
| `scripts/voip_softphone/{softphone.html,mint_token.py,README.md,test_*}` | Modified | Selector de caso + endpoint de lista + tests |
| `scripts/corpus_ingest/ingest_telefonia_corpus.py` (+ tests) | New | Recuperacion y write-back con `--replace` |
| `docker-compose.yml` (+ posible override) | Modified | Perfil `corpus` con base descartable |
| `CHANGES.md` | Modified | FASE 23 + entrada activa |

## Governance

ALTO (esquema de backend, parametros de llamada Twilio, infra de base descartable y credenciales). Las decisiones sensibles quedan como Open Questions para el autor.

## Open Questions

- **OQ1** — Mecanismo exacto de propagacion de `corpus_case_id` (param custom -> TwiML -> `recordingStatusCallback` por query param vs store keyed-by-CallSid) y limitaciones de Twilio.
- **OQ2** — Alcance del perfil `corpus`: stack completo vs backend+postgres; como se conmuta la Voice URL del TwiML App al backend del corpus (manual por corrida?) y el procedimiento de wipe.
- **OQ3** — Origen de la lista de casos telefonicos (endpoint del servidor del softphone vs embebida) y si la GUI necesita auth para leerla.
- **OQ4** — Columnas de descomposicion de telefonia: `t_espera_s` vacio/N-A vs 0; confirmar el comportamiento del escritor del corpus para telefonia.
- **OQ5** — Auth de recuperacion (operador con alcance `administrador_directorio`) y si el camino de lectura del backend expone `corpus_case_id`.
- **OQ6** — Si el borrado de `--replace` es solo por `corpus_case_id` y sus implicaciones de FK/tablas hijas.

## Dependencies

- `C-59` (softphone, archivado 2026-10-01): herramienta a extender.
- `C-52` (intake telefonico async, archivado 2026-09-30): flujo real a preservar.
- `C-68` (corpus por N8N real, activo): define el write-back, el merge y la privacidad que este change reutiliza; c-70 cubre la parte de telefonia que c-68 dejo manual.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| El parametro custom no llega al callback o rompe la firma Twilio | Med | Prototipo de propagacion y verificacion; fallback keyed-by-CallSid (OQ1) |
| `--replace` borra datos equivocados | Med | Borrado acotado por `corpus_case_id`, dry-run y aprobacion del autor (OQ6) |
| El perfil `corpus` no aisla bien la base de la app | Med | Base y volumenes dedicados; wipe explicito; tradeoffs documentados (OQ2) |
| Re-mediciones duplican filas y contaminan la metrica | Med | `--replace` purga lo previo y conserva solo el ultimo ingreso valido |
| Colision de numero de migracion con C-60 (011) | Med | Asignar el numero segun el head real en apply; documentado en el design |

## Rollback Plan

Revertir el commit elimina migraciones, endpoints, script y cambios del softphone; `alembic downgrade` dropea la columna `corpus_case_id` sin tocar `call_sid` ni `origen_message_id`. Los archivos del corpus (`data/`) NO estan trackeados: restaurar el respaldo previo de `data/` si se corrio escritura. El perfil `corpus` se elimina del compose y sus volumenes con `--profile corpus down -v`.

## Success Criteria

- [ ] Los 81 casos de `llamada telefonica` tienen `tiempo_automatizado_s` numerico medido por el flujo real y correlacionados por `corpus_case_id`.
- [ ] Cada llamada del softphone viaja con su `corpus_case_id` y el ingreso lo persiste.
- [ ] El write-back produce las columnas del corpus (`TIempo de Registro Automatico (Segundos)`, `Tiempo pipeline (s)`, `Tiempo espera (s)`, `Latencia e2e (ms)`) con valores propios de telefonia (espera N-A).
- [ ] `--replace` deja una sola medicion valida por caso y reemplaza el valor del corpus.
- [ ] La corrida no contamina la base de la app (perfil `corpus` + base descartable).
- [ ] Tests TDD offline del backend y de la logica pura del script; `openspec validate --strict --changes c-70-softphone-corpus-telefonia` pasa.
