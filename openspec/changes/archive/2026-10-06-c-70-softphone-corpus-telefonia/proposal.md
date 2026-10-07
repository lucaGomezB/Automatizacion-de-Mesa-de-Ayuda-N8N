# Proposal: Medicion del corpus de telefonia por el flujo real

## Why

El corpus de tesis tiene 81 casos de `llamada telefonica` con `tiempo_automatizado_s = null`, y el harness `c-68-corpus-ingesta-n8n` los dejo explicitamente FUERA DE ALCANCE para carga manual del autor. Hasta hoy no existe ninguna via reproducible para medir esos 81 casos por el flujo telefonico REAL (grabacion -> STT -> pseudonimizacion -> handoff -> alta), ni para correlacionar de forma EXACTA una llamada con su caso del corpus. Cargarlos "a mano" sin esa correlacion romperia la trazabilidad, la comparabilidad entre canales y la auditoria de la tesis.

## What Changes

- **Softphone (extiende C-59)**: `<select>` en `scripts/voip_softphone/softphone.html` poblado SOLO con los casos telefonicos del corpus (por defecto vacio). El modo `serve` de `mint_token.py` expone la lista de casos telefonicos leyendo `data/corpus_evaluacion_pseudonimizado.json`. El autor RECITA el texto del caso (sin reproduccion de audio) y el id viaja a Twilio como parametro custom de la llamada.
- **Backend (persistencia)**: `telefonia_ingreso` gana una columna nullable `corpus_case_id` (migracion Alembic). El id viaja del softphone al webhook de voz, que persiste el mapeo `call_sid -> corpus_case_id` en una tabla corta de PostgreSQL (`telefonia_pending_call`, TTL de purga acotado); el callback de grabacion lo resuelve por `call_sid`, lo persiste al sellar `ingresado_en` y borra la fila pendiente. NO se toca `call_sid` ni `origen_message_id` (idempotencia intacta). Sin dependencias nuevas.
- **Recuperacion + write-back**: script que lee el ULTIMO `telefonia_ingreso` de un `corpus_case_id`, deriva la metrica desde `latencia_e2e_ms` del incidente vinculado y escribe `tiempo_automatizado_s` en el corpus (CSV + XLSX + JSON), reutilizando el merge/skip y las reglas de privacidad de `ingest_via_n8n.py`.
- **Metrica canonica de telefonia**: `tiempo_automatizado_s = latencia_e2e_ms / 1000 = t_pipeline_s = t_e2e_s`. `t_espera_s` NO es medible en telefonia (el ingreso se sella en la recepcion del callback de grabacion, no en el inicio de la llamada); se deja vacio/N-A y se documenta.
- **`--replace`**: al re-medir un caso, elimina SOLO las filas de ese `corpus_case_id` (conserva solo el ultimo ingreso valido) y reemplaza el valor del corpus; destructivo con dry-run por defecto y aprobacion del autor.
- **Stack aislado (perfil `corpus`)**: perfil de Compose con `postgres-corpus` (base `mesa_de_ayuda_corpus`, volumen propio), `backend-corpus` (`DATABASE_URL` -> postgres-corpus, `alembic upgrade head`) y `n8n-corpus` (`BACKEND_URL` -> backend-corpus, volumen propio); no contamina la base de la app y se limpia con `docker compose --profile corpus down -v postgres-corpus backend-corpus n8n-corpus` (acotado por servicio, para no borrar los volumenes base).
- **Cobertura completa**: los 81 casos los mide el autor (sin muestreo).

## Capabilities

### New Capabilities

- `telefonia-corpus-medicion`: contrato de la corrida de medicion del corpus por telefonia real (base descartable, seleccion/correlacion del caso, metrica canonica de telefonia, recuperacion por `corpus_case_id`, write-back al corpus y reemplazo de mediciones previas).

### Modified Capabilities

- `telephony-test-softphone`: se agrega la seleccion del caso de corpus en el softphone y el endpoint de loopback `GET /corpus-cases` que sirve la lista de casos telefonicos.
- `telefonia-stt-intake`: se agrega la correlacion opcional del ingreso con un caso del corpus (`corpus_case_id` nullable) propagada desde el webhook de voz y persistida en el ingreso.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/models/telefonia_ingreso.py` | Modified | Columna nullable `corpus_case_id` |
| `App/Backend/alembic/versions/0XX_*.py` | New | Migracion aditiva (numero segun head actual) |
| `App/Backend/app/routes/cost_guard.py`, `app/routes/telefonia.py` | Modified | Recepcion del param custom y resolucion de la tabla corta keyed-by-CallSid |
| `App/Backend/app/models/`, `app/repositories/` (tabla corta) | New | Modelo/repositorio `call_sid -> corpus_case_id` (tabla corta `telefonia_pending_call`), TTL de purga |
| `App/Backend/app/routes/telefonia.py`, `app/schemas/telefonia.py`, `app/services/telefonia_service.py`, `app/repositories/telefonia_ingreso_repository.py` | Modified | Recibir/persistir/leer/borrar por `corpus_case_id` |
| `scripts/voip_softphone/{softphone.html,mint_token.py,README.md,test_*}` | Modified | Selector de caso + endpoint de lista + tests |
| `scripts/corpus_ingest/ingest_telefonia_corpus.py` (+ tests) | New | Recuperacion y write-back con `--replace` |
| `docker-compose.yml` | Modified | Perfil `corpus` con stack aislado (postgres-corpus, backend-corpus, n8n-corpus) |
| `CHANGES.md` | Modified | FASE 23 + entrada activa (gestionado por el orquestador) |

## Governance

ALTO (esquema de backend, parametros de llamada Twilio, infra de base descartable y credenciales). Las decisiones sensibles fueron resueltas por el autor (ver Decisions); `--replace` y el wipe no se ejecutan sin aprobacion explicita.

## Decisions (resolved)

OQ1..OQ6 fueron resueltas por el autor; no queda gating de decision para el apply.

- **OQ1 = Opcion B (store keyed-by-CallSid)**: el webhook de voz (`/cost-guard/twilio/voice`) recibe `call_sid` + `corpus_case_id`, persiste `call_sid -> corpus_case_id` en la tabla corta de PostgreSQL `telefonia_pending_call` (upsert por `call_sid`) y el callback `/telefonia/recording-status` resuelve `corpus_case_id` por `call_sid`, lo persiste al sellar `ingresado_en` y borra la fila pendiente. Se descarta el query param en el callback (Opcion A) y no se depende de cambios de firma Twilio. El ciclo de vida se acota con TTL: ademas del borrado explicito en el callback, se purgan las filas mas viejas que la ventana de la llamada (minutos) para que no se acumulen. La tabla reutiliza la infraestructura PostgreSQL ya presente y NO agrega dependencias nuevas. El softphone sigue originando el parametro con `device.connect({ params: { corpus_case_id } })`.
- **OQ2 = stack aislado completo**: servicios `postgres-corpus` (base `mesa_de_ayuda_corpus`, volumen propio), `backend-corpus` (`DATABASE_URL` -> postgres-corpus, `alembic upgrade head`) y `n8n-corpus` (`BACKEND_URL` -> backend-corpus, volumen propio), todos bajo `profiles: ["corpus"]`. Wipe acotado por servicio: `docker compose --profile corpus down -v postgres-corpus backend-corpus n8n-corpus` (el comando sin nombres de servicio borraria tambien los volumenes base). La Voice URL del TwiML App se conmuta MANUALMENTE al backend del corpus durante la corrida y se restaura al terminar.
- **OQ3 = endpoint de listado**: `mint_token.py serve` agrega `GET /corpus-cases` que lee el JSON pseudonimizado (`--corpus-json` configurable) y devuelve `[{id, descripcion}]` filtrando los casos de canal telefonico de forma tolerante. `softphone.html` agrega un `<select>` por defecto vacio y muestra la descripcion del caso seleccionado para recitar. El servidor escucha solo en loopback: sin auth adicional; nunca se loguean descripciones.
- **OQ4 = vacio / N-A (no 0)**: en telefonia `ingresado_en` se sella en la recepcion del callback, por lo que `t_espera_s` no es medible. El script construye `CaseResult` con `t_espera_s=None` y los escritores existentes omiten la celda. `tiempo_automatizado_s = latencia_e2e_ms/1000 = t_pipeline_s = t_e2e_s`.
- **OQ5 = Opcion 1 (camino de lectura dedicado)**: `GET /api/v1/telefonia/ingresos?corpus_case_id=X&latest=true` (routes -> services -> repositories) devuelve el ultimo ingreso con la metrica del incidente vinculado. Requiere JWT de un operador `administrador_directorio`; credenciales solo desde entorno.
- **OQ6 = confirmado**: `--replace` borra SOLO las filas del `corpus_case_id`, dejando el ultimo ingreso valido; el orden respeta FKs (`telefonia_ingreso.incidente_id` SET NULL; `clasificacion_log.incidente_id` CASCADE) sin huerfanos. Destructivo con dry-run por defecto y aprobacion explicita del autor.

## Dependencies

- `C-59` (softphone, archivado 2026-10-01): herramienta a extender.
- `C-52` (intake telefonico async, archivado 2026-09-30): flujo real a preservar.
- `C-68` (corpus por N8N real, activo): define el write-back, el merge y la privacidad que este change reutiliza; c-70 cubre la parte de telefonia que c-68 dejo manual.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| La tabla corta keyed-by-CallSid no se resuelve o acumula filas | Med | TTL de purga acotado a la ventana de la llamada + borrado explicito en el callback; repositorio tras interfaz mockeable |
| `--replace` borra datos equivocados | Med | Borrado acotado por `corpus_case_id`, orden FK explicito, dry-run por defecto y aprobacion del autor |
| El perfil `corpus` no aisla bien la base de la app | Med | Base y volumenes dedicados; wipe acotado por servicio `--profile corpus down -v postgres-corpus backend-corpus n8n-corpus`; tradeoffs documentados |
| Re-mediciones duplican filas y contaminan la metrica | Med | `--replace` purga lo previo y conserva solo el ultimo ingreso valido |
| Colision de numero de migracion con C-60 (011) | Med | Asignar el numero segun el head real en apply; documentado en el design |

## Rollback Plan

Revertir el commit elimina migraciones, endpoints, script y cambios del softphone; `alembic downgrade` dropea la columna `corpus_case_id` y la tabla corta `telefonia_pending_call` sin tocar `call_sid` ni `origen_message_id`. Los archivos del corpus (`data/`) NO estan trackeados: restaurar el respaldo previo de `data/` si se corrio escritura. El perfil `corpus` se elimina del compose y sus volumenes con `docker compose --profile corpus down -v postgres-corpus backend-corpus n8n-corpus`.

## Success Criteria

- [ ] Los 81 casos de `llamada telefonica` tienen `tiempo_automatizado_s` numerico medido por el flujo real y correlacionados por `corpus_case_id`.
- [ ] Cada llamada del softphone viaja con su `corpus_case_id` y el ingreso lo persiste.
- [ ] El write-back produce las columnas del corpus (`TIempo de Registro Automatico (Segundos)`, `Tiempo pipeline (s)`, `Tiempo espera (s)`, `Latencia e2e (ms)`) con valores propios de telefonia (espera N-A).
- [ ] `--replace` deja una sola medicion valida por caso y reemplaza el valor del corpus.
- [ ] La corrida no contamina la base de la app (perfil `corpus` + base descartable).
- [ ] Tests TDD offline del backend y de la logica pura del script; `openspec validate --strict --changes c-70-softphone-corpus-telefonia` pasa.
