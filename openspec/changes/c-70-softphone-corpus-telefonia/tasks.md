# Tareas — c-70-softphone-corpus-telefonia

> Estado: aplicado (2026-10-05). Governance: ALTO. Modo TDD estricto aplicado en todo el codigo.
> Progress: 70/72. Pendientes: 8.2 (corrida completa de los 81 por el autor) y 8.3 (carga del corpus).
> Cada tarea de codigo que modifica un archivo existente arranco con una safety net (correr los tests actuales del area y registrar la linea base).

## 0. Prerequisitos y decisiones resueltas (sin gating)

> Las Open Questions OQ1..OQ6 fueron resueltas por el autor. No hay gating de decision para el apply: los items de esta seccion son preparacion tecnica, no aprobaciones pendientes.

- [x] 0.1 Definir el esquema de la tabla corta `telefonia_pending_call` (`call_sid`, `corpus_case_id`, `created_at` UTC), la clave de upsert, el TTL de purga y el contrato `call_sid -> corpus_case_id` (OQ1 = Opcion B; ver D2). — `call_sid` PK, `corpus_case_id` String(64), `created_at` UTC, TTL 1800 s.
- [x] 0.2 Definir los servicios del perfil `corpus` (`postgres-corpus`, `backend-corpus`, `n8n-corpus`, volumenes propios) y el runbook de conmutacion de la Voice URL (OQ2 = stack aislado completo; ver D8). — implementado por la seccion 6.
- [x] 0.3 Definir el contrato de `GET /corpus-cases` y el filtrado tolerante de canal telefonico (OQ3 = endpoint; ver D3). — implementado por la seccion 4.
- [x] 0.4 Definir el contrato de `CaseResult` con `t_espera_s=None` y la omision de la celda (OQ4 = vacio/N-A; ver D4). — implementado por la seccion 5.
- [x] 0.5 Definir el contrato de `GET /api/v1/telefonia/ingresos?corpus_case_id=X&latest=true` y el rol `administrador_directorio` (OQ5 = Opcion 1; ver D5). — implementado por la seccion 3.
- [x] 0.6 Definir el orden de borrado FK para `--replace` (SET NULL / CASCADE) con dry-run por defecto (OQ6 = confirmada; ver D7). — orden: incidente -> ingreso; dry-run por defecto.
- [x] 0.7 Verificar el head Alembic actual y reservar el numero de migracion (hoy `011`, ajustar si C-60 aterriza la `011` primero). Documentado (D12). — head verificado `010`; migracion `011`.

## 1. Backend: persistencia del `corpus_case_id` en el ingreso (TDD)

- [x] 1.1 Safety net: correr `cd App/Backend; pytest -m "not integration"` y registrar la linea base de tests del area de telefonia (modelo, repositorio, servicio). Si algo falla, reportarlo como fallo pre-existente y NO corregirlo. — baseline 878 passed; sin fallos pre-existentes.
- [x] 1.2 (RED) Escribir el test de que `TelefoniaIngreso` acepta y persiste `corpus_case_id` nullable, y que el ingreso sin el queda en `None`. Debe fallar porque la columna no existe. — `tests/test_telefonia_corpus_case_id.py`.
- [x] 1.3 (GREEN) Agregar `corpus_case_id: Mapped[str | None]` (String(64), nullable, indexado) al modelo `TelefoniaIngreso`. Correr el test: debe pasar.
- [x] 1.4 (TRIANGULATE) Agregar casos con `corpus_case_id` presente, ausente y en reproceso; verificar que `call_sid` sigue siendo la clave unica y que `origen_message_id` no cambia. Tests en verde.
- [x] 1.5 (RED) Escribir el test de que el repositorio expone una recuperacion del ultimo ingreso por `corpus_case_id` (con `selectinload(incidente)` explicito) y devuelve `None` si no existe.
- [x] 1.6 (GREEN) Implementar el metodo de repositorio (routes -> services -> repositories -> models, sin saltear capas). Correr el test: debe pasar. — `get_latest_by_corpus_case_id`.
- [x] 1.7 (TRIANGULATE) Cubrir multiples ingresos del mismo caso (devuelve el ultimo), caso inexistente y caso con incidente vinculado. Tests en verde.
- [x] 1.8 Escribir la migracion Alembic aditiva (`corpus_case_id` nullable + indice, y la tabla corta `telefonia_pending_call`), encadenada al head vigente; `downgrade` dropea la columna y la tabla. Verificar `alembic upgrade head` y `downgrade` en la base descartable. — `011_telefonia_corpus_case_id.py`; upgrade/downgrade/upgrade verificados en PostgreSQL descartable.
- [x] 1.9 (REFACTOR) Limpiar duplicacion y confirmar que todos los tests siguen verdes. — ruff limpio.

## 2. Backend: propagacion del parametro en el flujo de voz (TDD, OQ1 = Opcion B)

- [x] 2.1 Safety net: correr los tests de `cost_guard`/TwiML y de `telefonia` y registrar la linea base. — 878 passed (base compartida).
- [x] 2.2 (RED) Escribir el test de que el repositorio de correlacion persiste `call_sid -> corpus_case_id` en la tabla corta `telefonia_pending_call` cuando el webhook recibe el param, y NO escribe nada cuando es `None` (retrocompatible). Debe fallar. — `tests/test_telefonia_pending_call.py`.
- [x] 2.3 (GREEN) Implementar el modelo y el repositorio de la tabla corta `telefonia_pending_call` (SQLAlchemy 2.0 async; upsert por `call_sid`, get y delete) y la purga TTL de filas mas viejas que la ventana de la llamada, tras una interfaz `upsert/get/delete/purge`. Correr el test: debe pasar.
- [x] 2.4 (TRIANGULATE) Casos: id con caracteres especiales, ausencia del param, upsert idempotente por `call_sid`, get miss y purga TTL (no purga filas dentro de la ventana, purga las vencidas).
- [x] 2.5 (RED) Escribir el test de que `/cost-guard/twilio/voice` lee `corpus_case_id` del formulario opcional (junto con `CallSid`) y escribe la tabla pendiente; y de que `/telefonia/recording-status` resuelve `corpus_case_id` por `call_sid` desde la tabla pendiente y borra la fila. Debe fallar. — `tests/test_api_telefonia_corpus.py`.
- [x] 2.6 (GREEN) Implementar la recepcion del param en el webhook de voz, la resolucion en el callback, el borrado explicito de la fila pendiente y la purga TTL oportunista. Correr los tests: deben pasar.
- [x] 2.7 (TRIANGULATE) Cubrir llamada sin param (produccion, miss en la tabla), hit, borrado idempotente y ausencia de cambios en la firma Twilio (no se agrega query a la URL del callback).
- [x] 2.8 (RED) Escribir el test de que `TelefoniaService._create_new` persiste el `corpus_case_id` al sellar `ingresado_en` y de que `_retry_existing` lo preserva.
- [x] 2.9 (GREEN) Implementar la persistencia en el servicio (nunca obligatoria) sin tocar la idempotencia, la reserva ni el orden del pipeline. Tests en verde.
- [x] 2.10 (TRIANGULATE) Cubrir reproceso de estado terminal de error con y sin `corpus_case_id`, y ausencia total del param.
- [x] 2.11 (REFACTOR) Limpiar y confirmar todos los tests verdes.

## 3. Backend: camino de lectura / borrado por `corpus_case_id` (TDD, OQ5 = Opcion 1, OQ6 confirmada)

- [x] 3.1 Safety net: correr los tests de lectura de incidentes/telefonia y registrar la linea base.
- [x] 3.2 (RED) Escribir el test del endpoint dedicado `GET /api/v1/telefonia/ingresos?corpus_case_id=X&latest=true` (routes -> services -> repositories) que devuelve el ultimo ingreso/incidente de un `corpus_case_id` con su `latencia_e2e_ms`. Debe fallar.
- [x] 3.3 (GREEN) Implementar la lectura respetando la disciplina de capas y `selectinload` explicito. Tests en verde.
- [x] 3.4 (TRIANGULATE) Casos: sin resultados, multiples resultados (devuelve el ultimo) y visibilidad por rol `administrador_directorio`.
- [x] 3.5 (RED) Escribir el test del borrado acotado por `corpus_case_id` (dry-run por defecto; ejecucion destructiva solo con aprobacion del autor): elimina el/los ingresos e incidentes previos, respeta `clasificacion_log` (CASCADE) y `telefonia_ingreso.incidente_id` (SET NULL), y no toca otros casos. — expuesto como `DELETE /api/v1/telefonia/ingresos?corpus_case_id=X&dry_run=true`.
- [x] 3.6 (GREEN) Implementar el borrado con el orden correcto y transaccionalidad. Tests en verde. — `hard_delete` en repositorios (Core DELETE, CASCADE a nivel DB).
- [x] 3.7 (TRIANGULATE) Casos: borrado de varios ingresos del mismo caso, caso con y sin incidente, caso inexistente (no-op) y no afectacion de otros `corpus_case_id`.
- [x] 3.8 (REFACTOR) Limpiar y confirmar todos los tests verdes.

## 4. Softphone: listado de casos y selector (TDD)

- [x] 4.1 Safety net: correr los tests de `scripts/voip_softphone/` y registrar la linea base. — 52 passed.
- [x] 4.2 (RED) Escribir el test de que `mint_token.py serve` expone `GET /corpus-cases` con la lista de casos telefonicos leida del JSON pseudonimizado, tolerante al rotulo de canal (`llamada telefonica` / `llamada telefónica` / `telefono`). Debe fallar. — `test_corpus_cases.py`.
- [x] 4.3 (GREEN) Implementar el endpoint y el filtrado (solo loopback). Tests en verde.
- [x] 4.4 (TRIANGULATE) Casos: corpus sin casos telefonicos, archivo inexistente (error claro) y exclusion de casos de otros canales.
- [x] 4.5 (RED) Escribir el test estructural de `softphone.html`: existe el `<select>` por defecto vacio y `device.connect` envia `{ params: { corpus_case_id } }` solo con seleccion.
- [x] 4.6 (GREEN) Implementar el selector, la muestra del texto del caso para recitar (sin playback) y el envio del parametro. Tests en verde.
- [x] 4.7 (TRIANGULATE) Casos: sin seleccion no envia el param (retrocompatible con C-59); con seleccion lo envia; la descripcion no se loguea.
- [x] 4.8 (REFACTOR) Actualizar `scripts/voip_softphone/README.md` con el flujo de seleccion y recitacion; confirmar todos los tests verdes. — suite final 69 passed.

## 5. Script de recuperacion y write-back del corpus de telefonia (TDD)

- [x] 5.1 (RED) Escribir tests de la logica pura: derivacion de la metrica de telefonia (`t_e2e_s = t_pipeline_s = latencia_e2e_ms/1000`, `t_espera_s=None` vacio/N-A) y construccion del `CaseResult`. Deben fallar. — `test_ingest_telefonia_corpus.py`.
- [x] 5.2 (GREEN) Implementar la derivacion y el `CaseResult` reutilizando `ingest_via_n8n`. Tests en verde. — `ingest_telefonia_corpus.py`.
- [x] 5.3 (TRIANGULATE) Casos: latencia valida, nula, negativa/anomala (excluida sin recortar) y redondeo a 3 decimales.
- [x] 5.4 (RED) Escribir tests del write-back: CSV + XLSX + JSON de evaluacion + sidecar, reutilizando `_should_write_metric`, sin escribir `null` sobre un valor existente, sin duplicar columnas y con `Tiempo espera (s)` vacia/N-A.
- [x] 5.5 (GREEN) Implementar el script `ingest_telefonia_corpus.py` que recupera el ultimo ingreso por `corpus_case_id` (endpoint dedicado `GET /api/v1/telefonia/ingresos?latest=true`, auth desde entorno) y escribe solo resultados de telefonia. Tests en verde.
- [x] 5.6 (TRIANGULATE) Casos: caso sin ingreso (pendiente, no escribe), re-ejecucion idempotente, merge del JSON sin debilitar `_a_float` y sidecar sin descripciones.
- [x] 5.7 (RED) Escribir tests de `--replace` (dry-run por defecto; ejecucion destructiva solo con aprobacion del autor): dry-run no borra ni escribe; `--replace` elimina lo previo del caso y reemplaza el valor; sin `--replace` conserva el historial. — flag destructivo explicito `--confirm-replace`.
- [x] 5.8 (GREEN) Implementar `--replace` y el dry-run. Tests en verde.
- [x] 5.9 (TRIANGULATE) Casos: multiples previos, caso sin previos y no afectacion de otros casos.
- [x] 5.10 (REFACTOR) Documentar el script en `scripts/corpus_ingest/README.md`; confirmar todos los tests verdes. — suite final 153 passed.

## 6. Infra: perfil `corpus` con stack aislado (OQ2 = stack aislado completo)

- [x] 6.1 Implementar el perfil `corpus` en `docker-compose.yml` con `postgres-corpus`, `backend-corpus` (`DATABASE_URL` -> postgres-corpus, `alembic upgrade head`) y `n8n-corpus` (`BACKEND_URL` -> backend-corpus, volumenes propios), todos bajo `profiles: ["corpus"]`. — cambio aditivo (+120 lineas, 0 removidas); servicios base intactos.
- [x] 6.2 Verificar el aislamiento: una corrida escribe en la base descartable y NO en la base de la aplicacion. — `mesa_de_ayuda_corpus` migrada a head; contenedores corpus montan solo volumenes del corpus.
- [x] 6.3 Verificar el wipe acotado (`--profile corpus down -v postgres-corpus backend-corpus n8n-corpus`) sin afectar la base de la aplicacion. — VERIFICADO con el comando ACOTADO; los volumenes base sobrevivieron. El comando literal sin nombres de servicio es DESTRUCTIVO (borra todos los volumenes top-level del proyecto compartido) y NO se usa; ver Notas de desviacion.
- [x] 6.4 Documentar en el runbook la conmutacion y restauracion de la Voice URL del TwiML App. — `docs/runbook-corpus-telefonia.md` §7.

## 7. Documentacion y CHANGES

- [x] 7.1 Documentar la metrica de telefonia y la espera N-A en `docs/medicion-latencia-e2e.md` §5 (o en el runbook de telefonia). — §5 "Telefonia: descomposicion y espera N-A".
- [x] 7.2 Registrar la entrada de c-70 en `CHANGES.md` (FASE 23 + arbol de dependencias); responsabilidad del orquestador, no del apply de c-70. — registrado (FASE 23, arbol, tabla, totales).
- [x] 7.3 Actualizar `scripts/voip_softphone/README.md` y `scripts/corpus_ingest/README.md` con la corrida completa. — ambos actualizados.

## 8. Verificacion final

- [x] 8.1 Corrida acotada: 1-2 casos de telefono en el perfil `corpus`, con correlacion exacta y write-back verificado. — REALIZADO con R002 (2026-10-05): correlacion exacta via `corpus_case_id`, ingreso enlazado (`incidente_id=2`), `latencia_e2e_ms=13012`, write-back `medidos=1` y `tiempo_automatizado_s=13.012` escrito en JSON/CSV/XLSX/sidecar.
- [ ] 8.2 Corrida completa de los 81 casos por el autor (sin muestreo). — BLOCKED: trabajo manual del autor.
- [ ] 8.3 Verificar la carga del corpus: `cd evaluation; pytest -q` sin `CorpusError` una vez cargados web + correo + los 81 telefonos. — BLOCKED by 8.2.
- [x] 8.4 `openspec validate --strict --changes c-70-softphone-corpus-telefonia` en verde. — 5 passed, 0 failed.
- [x] 8.5 Suite backend offline y tests del softphone/script en verde; `ruff check` sin hallazgos. — backend 920 passed (+ integracion 37 passed); softphone 69 passed; corpus_ingest 153 passed; openapi sync 5 passed; ruff All checks passed.

## 9. Fix post-smoke (bugfix, 2026-10-05)

> El smoke real de 8.1 (llamada R002) revelo dos defectos que el verify no detecto (los tests de integracion inyectaban el incidente ya enlazado). El incidente SI se creo (latencia 17.037 s) pero `telefonia_ingreso.incidente_id` quedo NULL porque `link_incidente` nunca se llama; y el handoff loguea `handoff_failed` en falso (timeout 5 s < workflow ~11 s).

- [x] 9.1 Safety net: correr los tests de telefonia + incidentes y registrar la linea base. — baseline 920 passed.
- [x] 9.2 (RED) Test: crear un incidente de telefonia (`origen_message_id = call_sid`) enlaza el `telefonia_ingreso` existente (`incidente_id` seteado) y el endpoint de lectura pasa a devolver `latencia_e2e_ms`. Debe fallar (hoy `link_incidente` no se llama). — RED confirmado.
- [x] 9.3 (GREEN) Cablear `link_incidente` en el alta del incidente: con `TelefoniaIngresoRepository.get_by_call_sid(origen_message_id)`, setear `incidente_id`. Aplica al camino normal y al idempotente (auto-sanado). No toca otras capas ni casos. — `_link_telefonia_ingreso` en `IncidenteService` (normal + early-return + IntegrityError).
- [x] 9.4 (TRIANGULATE) Incidente sin ingreso coincidente (no-op), replay idempotente que enlaza, y el ingreso de otro `call_sid` no se toca. — 3 casos en verde.
- [x] 9.5 (RED/GREEN) Subir el timeout del handoff (`app/utils/n8n_webhook.py`) de 5 s a 30 s para no loguear `handoff_failed` en falso cuando el workflow tarda ~11 s (es fire-and-forget). Ajustar aserciones existentes si las hubiera. — constante `TELEFONIA_HANDOFF_TIMEOUT_S=30.0` + test de captura; el `notify_n8n` generico se dejo en 5 s (justificado).
- [x] 9.6 (REFACTOR) Limpiar; suite offline + integracion en verde; `ruff` limpio; `openspec validate --strict --changes c-70-softphone-corpus-telefonia` pasa. — 925 passed (+37 integracion); ruff limpio; validate 6/6.
- [x] 9.7 Re-smoke: con el fix, repetir R002 y confirmar `telefonia_ingreso.incidente_id` enlazado y que el write-back escribe `tiempo_automatizado_s`. — VERIFICADO: handoff HTTP 200 (sin falso fallo), ingreso 4 enlazado a incidente 2, endpoint devuelve `latencia_e2e_ms=13012`, write-back escribio `13.012`.

## Notas de desviacion

- **6.3 (wipe):** el design/spec originales afirmaban que `docker compose --profile corpus down -v` borra SOLO los volumenes del corpus. Es FALSO: el nombre de proyecto Compose es compartido (`mesa_local`), asi que el comando sin nombres de servicio elimina todos los volumenes top-level, incluidos `mesa_local_postgres_data` y `mesa_local_n8n_data`. Verificado empiricamente en un probe aislado. Se corrigieron `design.md` (D8, riesgos), `proposal.md` (scope, decision OQ2, riesgos, rollback) y `specs/telefonia-corpus-medicion/spec.md` al wipe ACOTADO POR SERVICIO: `docker compose --profile corpus down -v postgres-corpus backend-corpus n8n-corpus`. El runbook documenta el procedimiento seguro.
- **3.5/3.6 (endpoint de borrado):** ademas del `GET` de lectura, se expuso `DELETE /api/v1/telefonia/ingresos?corpus_case_id=X&dry_run=true` (admin-only, `dry_run=true` por defecto) porque la seccion 5 (`--replace`) necesita un camino HTTP de borrado. El flag destructivo es explicito (`dry_run=false`).
- **5.7 (flag):** la aprobacion explicita para el borrado destructivo se implemento como `--confirm-replace` (el design solo exigia "aprobacion explicita").
- **Fix de test (5.x):** `test_evaluation_a_float_still_rejects_non_numeric` importaba `evaluation` (paquete de la raiz) sin agregar la raiz a `sys.path`; fallaba al correr desde el directorio. Se agrego el ajuste relativo al archivo (mismo patron que `pseudonymize_corpus.py`), dejando la suite en 153 passed desde la raiz y desde el directorio.
- **Aislamiento de tests (backend):** el cleanup autouse de los tests nuevos tambien borra la fila de soporte `Estado` para no romper `seed_catalogs` de otros modulos por UNIQUE.
