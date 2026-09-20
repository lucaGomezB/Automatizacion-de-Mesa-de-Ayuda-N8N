## Context

Ver `proposal.md` — Why. Este change introduce un contrato de medicion temporal; el design fija las fronteras exactas y su trazabilidad. Estado verificado del codigo:

- El normalizador de N8N (`n8n/workflow.json`, nodo `Normalizar entrada del incidente`) emite `timestamp: new Date().toISOString()` en su `jsCode`, pero el body del nodo `HTTP POST a MTM-SRU` solo envia `descripcion`, `prioridad`, `canal_origen_id`, `origen_message_id`, `origen_evento` y `clasificacion`. El `timestamp` nunca sale del workflow.
- `IncidenteCreate` (`App/Backend/app/schemas/incidente.py:75-156`) no tiene campo de ingreso.
- `Incidente` (`App/Backend/app/models/incidente.py:59-186`) hereda `TimestampMixin` (`App/Backend/app/models/base.py:33-60`), que solo aporta `created_at`/`updated_at`. Las migraciones 001-005 confirman que no existe columna de ingreso ni de latencia.
- `IncidenteService.create_and_classify` (`App/Backend/app/services/incidente_service.py:174-275`): cortocircuito idempotente por `origen_message_id` (206-216); INSERT (241-250); clasificacion (271); `_apply_classification` ejecuta el UPDATE del incidente y el INSERT del log (374-434); relectura con `selectinload` (275). El commit ocurre DESPUES de que el handler retorna, en `get_db_session` (`App/Backend/app/core/database.py:93-109`).
- En el grafo N8N la telefonia corre `Llamada telefonica -> AI Agent -> Se verifica lo que trajo la IA -> ... -> Normalizar`. El `timestamp` del normalizador es POSTERIOR al agente pago: usarlo excluiria el costo dominante de ese canal.
- El trigger de correo es `microsoftOutlookTrigger` con `pollTimes.everyMinute` y filtro de 24 h sobre `receivedDateTime`; su `output: fields` incluye `receivedDateTime`.
- El nodo `Registro de auditoria` genera su propio `timestamp` y no empareja ingreso con persistencia.
- `updated_at` usa `onupdate=utcnow` (`App/Backend/app/models/base.py:55-60`): se recalcula en cada UPDATE, incluidos los PATCH posteriores del operador.
- Frontera con `c-40-n8n-wiring-fixes`: ambos editan `n8n/workflow.json`; c-40 depende de c-39 y aporta los fixes de cableado. c-39 NO los duplica.

## Goals / Non-Goals

**Goals:**

- Definir y persistir el instante de ingreso y el de persistencia confirmada por incidente.
- Medir latencia END-TO-END real (incluye agente LLM y validacion; excluye la espera previa a la recogida del poller de correo y la duracion de la llamada telefonica), no solo la clasificacion.
- Dejar la latencia consultable para derivar `tiempo_automatizado_s` del corpus.
- Hacer el contrato testeable sin runtime N8N ni PostgreSQL.

**Non-Goals:**

- No corregir el cableado de canales ni agregar remitente al payload (c-40).
- No implementar Voice Insights, transcripcion ni medicion desde el inicio de la llamada (Fase 2).
- No cablear el corpus `tiempo_automatizado_s` en este change; la latencia queda disponible como consumidor.
- No cambiar el clasificador ni el umbral de confianza.
- No backfill de filas historicas.

## Decisions

### D1: "Ingreso" se captura en el borde del trigger, no en el normalizador

El instante de ingreso se sella en el borde de cada trigger y se propaga al normalizador. En telefonia el sello va inmediatamente despues de `Llamada telefonica` y ANTES de `AI Agent`; en web se sella en `Marcar canal web` (nodo inmediatamente posterior al webhook); en correo se sella al INICIO del flujo del trigger de Outlook, en el instante en que el poller recoge el mensaje (mismo patron que web y telefonia), no en el `receivedDateTime` del mensaje.

- Alternativa considerada: usar el `timestamp` del normalizador (un solo punto, mas simple). Se descarta porque en telefonia es posterior al `AI Agent` y subestima la latencia al excluir la llamada paga; contradice el requisito explicito de end-to-end.
- Alternativa considerada: medir desde que el backend recibe el POST. Se descarta porque mide solo el backend y no el sistema completo.

### D2: "Persistencia confirmada" es el boundary de commit, con columna dedicada e inmutable; `updated_at` queda descalificado

Se agrega la columna `persistido_en`, sellada una sola vez dentro de la transaccion de alta y clasificacion, en el punto en que finalizan las escrituras del incidente y su log (inmediatamente antes del commit). Es inmutable: no figura en `IncidenteUpdate` ni usa `onupdate`.

- Precision: `persistido_en` es el ultimo instante de escritura de la transaccion; el round-trip del commit a PostgreSQL no queda incluido. Se documenta y se acota como despreciable frente a latencias de segundos. La confirmacion fuerte la aporta el 201: el backend commitea antes de emitir la respuesta (`get_db_session` cierra la transaccion al finalizar la dependencia, antes de enviar el response).
- Alternativa considerada: capturar el instante post-commit real. Requiere una segunda transaccion/escritura (una fila no puede contener un instante posterior a su propio commit dentro de la misma transaccion) y abre una ventana con `persistido_en` nulo. Se descarta por complejidad y perdida de atomicidad.
- Alternativa considerada: usar `updated_at`. Se descarta: se recalcula en cada UPDATE posterior (`onupdate`), por lo que la revision humana o un PATCH del operador lo sobrescribirian, destruyendo la medicion.
- Alternativa considerada: usar `created_at`. Se descarta: se sella en el INSERT, antes de la clasificacion, y excluye el costo dominante.

### D3: Se persisten los dos instantes fuente; la latencia se deriva

`latencia_e2e_ms = (persistido_en - ingresado_en)` en milisegundos, derivada en la capa de lectura. No se denormaliza una columna de latencia. Para el corpus, `tiempo_automatizado_s = latencia_e2e_ms / 1000`.

- Alternativa considerada: columna `latencia_e2e_ms` denormalizada. Se descarta por redundante y propensa a drift respecto de los instantes fuente.

### D4: Validacion y nullability de `ingresado_en`

Se acepta solo ISO-8601 con zona horaria explicita; un valor naive se rechaza con error de validacion. Se rechaza un valor posterior al ahora del servidor mas alla de una tolerancia configurable (por defecto 30 s) para evitar latencias negativas por skew de relojes entre contenedores. La tolerancia se fija en 30 s porque en el despliegue local con docker-compose todos los contenedores comparten el reloj del kernel del host, por lo que el skew n8n<->backend es practicamente nulo; 300 s era excesivo y aceptaria en silencio valores futuros absurdos y latencias negativas. El campo es nullable: los clientes API directos y las filas legacy pueden no proveerlo.

- Alternativa considerada: asumir UTC para valores naive. Se descarta porque enmascara errores del emisor y contamina la medicion.
- Alternativa considerada: mantener una tolerancia amplia (300 s) para absorber skew de relojes. Se descarta por lo anterior: sin skew real en el despliegue objetivo, solo encubre datos invalidos.

### D5: Exclusion de replays idempotentes por construccion

El cortocircuito por `origen_message_id` devuelve la fila existente sin re-medir, y la carrera por `IntegrityError` devuelve el ganador. Como la medicion vive en la fila, un replay no crea fila ni latencia nueva: la exclusion es por construccion y no requiere una marca adicional en el workflow.

- Alternativa considerada: deduplicar en el corpus por `execution id`. Se descarta porque el corpus se construye desde filas y la deduplicacion por fila es mas robusta.
- Nota: distinguir el replay en la auditoria requeriria que el backend senalice el cortocircuito (por ejemplo un campo o header), lo que excede el alcance de este change; queda como mejora diferible.

### D6: Caveats por canal

- Correo: ingreso = instante en que el poller de Outlook recoge el mensaje, NO la llegada al buzon; la latencia EXCLUYE la espera previa a la recogida (hasta ~60 s por `everyMinute`), por lo que sub-mide respecto de la llegada real al buzon y no es comparable caso a caso con web/telefonia; el analisis se reporta por canal.
- Telefonia: ingreso = recepcion del `call-summary.complete` de Twilio, despues del fin de la llamada y de la generacion del resumen. No incluye duracion de llamada ni generacion del resumen; la hipotesis de Voice Insights queda diferida a Fase 2.
- Web: ingreso = recepcion del webhook; exacto.

- Alternativa considerada: usar el `receivedDateTime` de Outlook y restar la espera del poller para aproximar la llegada al buzon. Se descarta: la resta es un ajuste estadistico sobre un intervalo desconocido (0-60 s) y no recupera el instante exacto de llegada; la metrica principal es end-to-end cruda y el analisis se reporta por canal.

### D7: Migracion aditiva 006, sin backfill

Revision `006_add_timing_instrumentation.py`, `down_revision="005"`, agrega `ingresado_en` y `persistido_en` como `TIMESTAMPTZ` nullable. Sin indices y sin backfill; `downgrade` dropea ambas. Requiere aprobacion humana (governance ALTA).

- Alternativa considerada: backfill de historicos. Se descarta: no existe el dato de ingreso y fabricarlo violaria la honestidad de la medicion.

### D8: Frontera con c-40

c-39 introduce el campo `ingresado_en` en el payload y la columna/migracion; c-40 corrige cableado de canales y puede agregar un campo de remitente. Ambos editan `n8n/workflow.json`; c-40 depende de c-39. Este change no toca los defectos de cableado de c-40.

### D9: Politica de latencia negativa

Si `latencia_e2e_ms < 0` (por ejemplo, por ingreso futuro dentro de la tolerancia o por desalineacion de relojes), el sistema NO la reporta como medicion valida: la marca como anomalia y la excluye del corpus y del analisis. Nunca se acepta en silencio. La anomalia se registra para diagnostico.

- Alternativa considerada: reportar la latencia negativa tal cual y decidir en el analisis. Se descarta: un valor negativo es fisicamente invalido como latencia y contaminaria el corpus si se filtra por accidente.
- Alternativa considerada: recortar (`clamp`) la latencia negativa a cero. Se descarta: fabrica un valor que no ocurrio y oculta la causa raiz.

## Risks / Trade-offs

- [El instante post-commit real no se captura; el round-trip del commit queda fuera] -> Documentado y acotado; la confirmacion fuerte es el 201 (commit antes de responder).
- [El ingreso de correo se sella en la recogida del poller, no en la llegada al buzon; la latencia sub-mide respecto de la llegada real y rompe la comparabilidad caso a caso] -> Caveat declarado; analisis por canal.
- [Telefonia no mide desde el inicio de la llamada] -> Caveat declarado; Fase 2 (Voice Insights) diferida explicitamente.
- [Relojes desalineados entre n8n y backend] -> Tolerancia de futuro configurable por defecto 30 s (suficiente porque los contenedores comparten el reloj del host); valores fuera de tolerancia se rechazan y latencias negativas se marcan anomalas y se excluyen.
- [Latencias negativas por ingreso futuro dentro de la tolerancia o skew] -> Politica de latencia negativa (D9): se marcan anomalas y se excluyen del corpus y del analisis.
- [Nodos de sello que no se ejecutan en ramas de error] -> Tests estructurales verifican el sello aguas arriba del agente y en los tres bordes de trigger.
- [Migracion sobre base productiva] -> Aditiva nullable, sin backfill; rollback por `downgrade`.

## Migration Plan

1. Aprobar este design (governance ALTA, revision humana previa a implementar).
2. Aplicar la migracion 006 aditiva en dev/test y verificar `upgrade`/`downgrade`.
3. Desplegar el backend tolerante (schema nullable + sello del servicio) ANTES de que N8N envie el campo.
4. Actualizar `n8n/workflow.json` para capturar y enviar `ingresado_en`.
5. Rollback: `downgrade` de 006 y reversion del JSON. El backend tolera la ausencia del campo (nullable) en ambos sentidos.

## Open Questions

- Ninguna que cambie las specs, el enfoque o el desglose de tareas.
- Diferible: el cableado del corpus (`tiempo_automatizado_s = latencia_e2e_ms / 1000`) queda como consumidor fuera de este change; se puede abordar en un change posterior.
- Diferible: si el volumen de consultas del corpus lo justifica, evaluar un indice sobre `persistido_en` en una migracion futura. No se agrega ahora.
