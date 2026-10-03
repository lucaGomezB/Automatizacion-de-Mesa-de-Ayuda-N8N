# Tareas — c-70-softphone-corpus-telefonia

> Estado: propuesto (2026-10-02). Planning completo (proposal + design + specs + tasks).
> Governance: ALTO. Modo TDD estricto para todo el codigo: RED -> GREEN -> TRIANGULATE -> REFACTOR.
> Cada tarea de codigo que modifica un archivo existente arranca con una safety net (correr los tests actuales del area y registrar la linea base). No escribir codigo de produccion antes del test que falla.

## 0. Prerequisitos, decisiones y gating

- [ ] 0.1 Confirmar OQ1 (mecanismo de propagacion): Opcion A (query param en `recordingStatusCallback`) vs Opcion B (store keyed-by-CallSid) y validar la firma Twilio con query param. Gate de la fase 2.
- [ ] 0.2 Confirmar OQ2 (alcance del perfil `corpus` y conmutacion de la Voice URL). Gate de la fase 6.
- [ ] 0.3 Confirmar OQ3 (listado por endpoint vs embebido y auth de la GUI). Gate de la fase 4.
- [ ] 0.4 Confirmar OQ4 (`t_espera_s` vacio/N-A vs 0). Gate de la fase 5.
- [ ] 0.5 Confirmar OQ5 (auth de recuperacion y exposicion de `corpus_case_id`). Gate de la fase 3.
- [ ] 0.6 Confirmar OQ6 (alcance de `--replace` por `corpus_case_id` y FK/hijas). Gate de la fase 5.
- [ ] 0.7 Verificar el head Alembic actual y reservar el numero de migracion (hoy `011`, ajustar si C-60 aterriza la `011` primero). Documentado (D12).

## 1. Backend: persistencia del `corpus_case_id` en el ingreso (TDD)

- [ ] 1.1 Safety net: correr `cd App/Backend; pytest -m "not integration"` y registrar la linea base de tests del area de telefonia (modelo, repositorio, servicio). Si algo falla, reportarlo como fallo pre-existente y NO corregirlo.
- [ ] 1.2 (RED) Escribir el test de que `TelefoniaIngreso` acepta y persiste `corpus_case_id` nullable, y que el ingreso sin el queda en `None`. Debe fallar porque la columna no existe.
- [ ] 1.3 (GREEN) Agregar `corpus_case_id: Mapped[str | None]` (String(64), nullable, indexado) al modelo `TelefoniaIngreso`. Correr el test: debe pasar.
- [ ] 1.4 (TRIANGULATE) Agregar casos con `corpus_case_id` presente, ausente y en reproceso; verificar que `call_sid` sigue siendo la clave unica y que `origen_message_id` no cambia. Tests en verde.
- [ ] 1.5 (RED) Escribir el test de que el repositorio expone una recuperacion del ultimo ingreso por `corpus_case_id` (con `selectinload(incidente)` explicito) y devuelve `None` si no existe.
- [ ] 1.6 (GREEN) Implementar el metodo de repositorio (routes -> services -> repositories -> models, sin saltear capas). Correr el test: debe pasar.
- [ ] 1.7 (TRIANGULATE) Cubrir multiples ingresos del mismo caso (devuelve el ultimo), caso inexistente y caso con incidente vinculado. Tests en verde.
- [ ] 1.8 Escribir la migracion Alembic aditiva (`corpus_case_id` nullable + indice), encadenada al head vigente; `downgrade` dropea la columna. Verificar `alembic upgrade head` y `downgrade` en la base descartable.
- [ ] 1.9 (REFACTOR) Limpiar duplicacion y confirmar que todos los tests siguen verdes.

## 2. Backend: propagacion del parametro en el flujo de voz (TDD)

- [ ] 2.1 Safety net: correr los tests de `cost_guard`/TwiML y de `telefonia` y registrar la linea base.
- [ ] 2.2 (RED) Escribir el test de que `render_twiml_allowed` incluye el `corpus_case_id` urlencoded en `recordingStatusCallback` cuando se provee, y NO lo incluye cuando es `None` (retrocompatible). Debe fallar.
- [ ] 2.3 (GREEN) Extender `render_twiml_allowed` con el parametro opcional y `urlencode`. Correr el test: debe pasar.
- [ ] 2.4 (TRIANGULATE) Casos: id con caracteres especiales, ausencia del param y verificacion de que el `<Record>` conserva sus atributos (mono, maxLength, action).
- [ ] 2.5 (RED) Escribir el test de que `/cost-guard/twilio/voice` acepta `corpus_case_id` como campo de formulario opcional y lo pasa al renderizado; y de que `/telefonia/recording-status` lo lee de `request.query_params` (o del store, segun OQ1) hacia `RecordingStatusCallback`.
- [ ] 2.6 (GREEN) Implementar la recepcion y el paso del parametro en los endpoints y el schema. Correr los tests: deben pasar.
- [ ] 2.7 (TRIANGULATE) Cubrir llamada sin param (produccion) y verificacion de que la firma Twilio sigue validando con y sin el query param (segun OQ1).
- [ ] 2.8 (RED) Escribir el test de que `TelefoniaService._create_new` persiste el `corpus_case_id` al sellar `ingresado_en` y de que `_retry_existing` lo preserva.
- [ ] 2.9 (GREEN) Implementar la persistencia en el servicio (nunca obligatoria) sin tocar la idempotencia, la reserva ni el orden del pipeline. Tests en verde.
- [ ] 2.10 (TRIANGULATE) Cubrir reproceso de estado terminal de error con y sin `corpus_case_id`, y ausencia total del param.
- [ ] 2.11 (REFACTOR) Limpiar y confirmar todos los tests verdes.

## 3. Backend: camino de lectura / borrado por `corpus_case_id` (TDD, segun OQ5/OQ6)

- [ ] 3.1 Safety net: correr los tests de lectura de incidentes/telefonia y registrar la linea base.
- [ ] 3.2 (RED) Escribir el test del camino de lectura elegido en OQ5 (endpoint dedicado de telefonia o `IncidenteRead` + filtro exacto del listado) que devuelve el ultimo ingreso/incidente de un `corpus_case_id` con su `latencia_e2e_ms`. Debe fallar.
- [ ] 3.3 (GREEN) Implementar la lectura respetando la disciplina de capas y `selectinload` explicito. Tests en verde.
- [ ] 3.4 (TRIANGULATE) Casos: sin resultados, multiples resultados (devuelve el ultimo) y visibilidad por rol `administrador_directorio`.
- [ ] 3.5 (RED) Escribir el test del borrado acotado por `corpus_case_id` (si OQ6 lo aprueba): elimina el/los ingresos e incidentes previos, respeta `clasificacion_log` (CASCADE) y `telefonia_ingreso.incidente_id` (SET NULL), y no toca otros casos.
- [ ] 3.6 (GREEN) Implementar el borrado con el orden correcto y transaccionalidad. Tests en verde.
- [ ] 3.7 (TRIANGULATE) Casos: borrado de varios ingresos del mismo caso, caso con y sin incidente, caso inexistente (no-op) y no afectacion de otros `corpus_case_id`.
- [ ] 3.8 (REFACTOR) Limpiar y confirmar todos los tests verdes.

## 4. Softphone: listado de casos y selector (TDD)

- [ ] 4.1 Safety net: correr los tests de `scripts/voip_softphone/` y registrar la linea base.
- [ ] 4.2 (RED) Escribir el test de que `mint_token.py serve` expone `GET /corpus-cases` con la lista de casos telefonicos leida del JSON pseudonimizado, tolerante al rotulo de canal (`llamada telefonica` / `llamada telefónica` / `telefono`). Debe fallar.
- [ ] 4.3 (GREEN) Implementar el endpoint y el filtrado (solo loopback). Tests en verde.
- [ ] 4.4 (TRIANGULATE) Casos: corpus sin casos telefonicos, archivo inexistente (error claro) y exclusion de casos de otros canales.
- [ ] 4.5 (RED) Escribir el test estructural de `softphone.html`: existe el `<select>` por defecto vacio y `device.connect` envia `{ params: { corpus_case_id } }` solo con seleccion.
- [ ] 4.6 (GREEN) Implementar el selector, la muestra del texto del caso para recitar (sin playback) y el envio del parametro. Tests en verde.
- [ ] 4.7 (TRIANGULATE) Casos: sin seleccion no envia el param (retrocompatible con C-59); con seleccion lo envia; la descripcion no se loguea.
- [ ] 4.8 (REFACTOR) Actualizar `scripts/voip_softphone/README.md` con el flujo de seleccion y recitacion; confirmar todos los tests verdes.

## 5. Script de recuperacion y write-back del corpus de telefonia (TDD)

- [ ] 5.1 (RED) Escribir tests de la logica pura: derivacion de la metrica de telefonia (`t_e2e_s = t_pipeline_s = latencia_e2e_ms/1000`, `t_espera_s` N-A segun OQ4) y construccion del `CaseResult`. Deben fallar.
- [ ] 5.2 (GREEN) Implementar la derivacion y el `CaseResult` reutilizando `ingest_via_n8n`. Tests en verde.
- [ ] 5.3 (TRIANGULATE) Casos: latencia valida, nula, negativa/anomala (excluida sin recortar) y redondeo a 3 decimales.
- [ ] 5.4 (RED) Escribir tests del write-back: CSV + XLSX + JSON de evaluacion + sidecar, reutilizando `_should_write_metric`, sin escribir `null` sobre un valor existente, sin duplicar columnas y con `Tiempo espera (s)` vacia/N-A.
- [ ] 5.5 (GREEN) Implementar el script `ingest_telefonia_corpus.py` que recupera el ultimo ingreso por `corpus_case_id` (camino de OQ5, auth desde entorno) y escribe solo resultados de telefonia. Tests en verde.
- [ ] 5.6 (TRIANGULATE) Casos: caso sin ingreso (pendiente, no escribe), re-ejecucion idempotente, merge del JSON sin debilitar `_a_float` y sidecar sin descripciones.
- [ ] 5.7 (RED) Escribir tests de `--replace` (si OQ6 lo aprueba): dry-run no borra ni escribe; `--replace` elimina lo previo del caso y reemplaza el valor; sin `--replace` conserva el historial.
- [ ] 5.8 (GREEN) Implementar `--replace` y el dry-run. Tests en verde.
- [ ] 5.9 (TRIANGULATE) Casos: multiples previos, caso sin previos y no afectacion de otros casos.
- [ ] 5.10 (REFACTOR) Documentar el script en `scripts/corpus_ingest/README.md`; confirmar todos los tests verdes.

## 6. Infra: perfil `corpus` con base descartable (segun OQ2)

- [ ] 6.1 Implementar el perfil `corpus` en `docker-compose.yml` (o override) con base/volumenes dedicados y los servicios del flujo telefonico.
- [ ] 6.2 Verificar el aislamiento: una corrida escribe en la base descartable y NO en la base de la aplicacion.
- [ ] 6.3 Verificar el wipe (`--profile corpus down -v`) sin afectar la base de la aplicacion.
- [ ] 6.4 Documentar en el runbook la conmutacion y restauracion de la Voice URL del TwiML App.

## 7. Documentacion y CHANGES

- [ ] 7.1 Documentar la metrica de telefonia y la espera N-A en `docs/medicion-latencia-e2e.md` §5 (o en el runbook de telefonia).
- [ ] 7.2 Actualizar `CHANGES.md` (FASE 23 + entrada activa + arbol de dependencias). Hecho en el propose.
- [ ] 7.3 Actualizar `scripts/voip_softphone/README.md` y `scripts/corpus_ingest/README.md` con la corrida completa.

## 8. Verificacion final

- [ ] 8.1 Corrida acotada: 1-2 casos de telefono en el perfil `corpus`, con correlacion exacta y write-back verificado.
- [ ] 8.2 Corrida completa de los 81 casos por el autor (sin muestreo).
- [ ] 8.3 Verificar la carga del corpus: `cd evaluation; pytest -q` sin `CorpusError` una vez cargados web + correo + los 81 telefonos.
- [ ] 8.4 `openspec validate --strict --changes c-70-softphone-corpus-telefonia` en verde.
- [ ] 8.5 Suite backend offline y tests del softphone/script en verde; `ruff check` sin hallazgos.

## Notas de desviacion

- (Reservado para registrar desviaciones durante el apply.)
