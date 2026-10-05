## Context

Ver `proposal.md` — Why. Estado actual y restricciones verificadas:

- **Indice unico ya existe**: la migracion `005_add_origen_message_id.py` agrega `origen_message_id` (String(255), nullable) con indice unico `ix_incidente_origen_message_id`. La unicidad aplica solo a valores no nulos; varios `NULL` conviven. No se requiere migracion nueva.
- **Idempotencia backend ya existe**: `IncidenteService.create_and_classify` cortocircuita por `origen_message_id` ANTES de pseudonimizar/clasificar y resuelve la carrera con `IntegrityError` reconsultando (`incidente_repository.get_by_origen_message_id`). El unico cambio de comportamiento web es que el payload ahora SI trae el id; el mecanismo server-side no cambia.
- **Rama web de n8n**: el nodo "Normalizar entrada del incidente" calcula (`n8n/workflow.json`):
  ```js
  const messageIdHeader = (item.json.metadata && item.json.metadata['message-id']) || null;
  const uidFallback = (item.json.attributes && item.json.attributes.uid != null) ? String(item.json.attributes.uid) : null;
  const origenMessageId =
    canalOrigen === 'correo' ? (messageIdHeader || uidFallback)
    : canalOrigen === 'telefonia' ? (item.json.call_sid || null)
    : null;  // <-- web fuerza null
  ```
  Para web el body del formulario llega anidado en `item.json.body` (`webBody`). El nodo `Marcar canal web` sella `canal_raw='web'` e `ingresado_en`. El POST (`HTTP POST a MESA-AYUDAS`) envia `origen_message_id: $('Normalizar entrada del incidente').item.json.origen_message_id || null`.
- **Contrato de lectura**: `IncidenteRead` expone `id`, instantes (`ingresado_en`, `persistido_en`), latencia derivada y `numero_incidente`; NO expone `origen_message_id`. `IncidenteListItem` no lo expone. `list_filtered` filtra por sector/estado/prioridad/revision/desde/hasta; no por origen.
- **Replays**: `e2e-timing-instrumentation` (spec) y `docs/medicion-latencia-e2e.md` §6 exigen que un replay con el mismo `origen_message_id` devuelva la fila existente SIN re-medir (la medicion vive en la fila).

## Goals / Non-Goals

**Goals:**
- Que el canal web declare siempre un `origen_message_id`, habilitando dedup server-side por el indice unico existente.
- Permitir un id deterministico provisto por el llamador (harness: `corpus-<ID>`) sin romper el formulario web real.
- Exponer `origen_message_id` en lectura y permitir filtrado exacto para correlacion determinista.

**Non-Goals:**
- Migracion de esquema o backfill (OQ-D: legacy queda nulo).
- Cambiar el mecanismo de idempotencia del backend (ya correcto).
- Tocar las ramas correo/telefonia del normalizador.
- Modificar el formulario frontend (el id lo genera n8n).

## Decisions

### D1: Generacion del id en el nodo n8n (PRIMARIA — OQ-A resuelta), default backend opcional

El nodo normalizador construye `origenMessageId` para web con esta precedencia:

1. **Id explicito del llamador (PRIMARIO)**: `webBody.origen_message_id` (o `webBody.case_id` -> `corpus-<case_id>`, o `item.json.origen_message_id`) si viene no vacio. El harness envia `corpus-<ID>` deterministico.
2. **Id generado por n8n (PRIMARIO cuando falta el del llamador)**: si no viene, se deriva un id unico por envio. El `id` del item ya se sintetiza como `item.json.id || $execution.id + '-' + Date.now()`; se reutiliza esa base para el web, p.ej. `web-<execution.id>-<timestamp>`. Como `$execution.id` es unico por ejecucion, dos usuarios reales NUNCA colisionan: la unicidad jamas rechaza un alta legitima distinta.
3. **Default del backend (OPCIONAL/SECUNDARIO — OQ-A)**: si el payload llega con `origen_message_id` nulo y `canal_origen_id` corresponde a web, el backend PUEDE generar un UUID. La fuente primaria es n8n; este default es defensa en profundidad, NO obligatorio para cerrar el change. Si se implementa, la unicidad la garantiza el UUID.

**Decision del autor (OQ-A)**: n8n genera el id — id deterministico del llamador cuando viene, id unico por ejecucion cuando falta. Backend UUID solo como respaldo opcional.

**Alternativas**: (a) que el formulario real genere el id — descartada: no se puede confiar en el cliente y exigiria cambiar el frontend; (b) hash de la descripcion — descartada: colision entre usuarios con texto similar y posible correlacion por contenido; (c) no tocar web y documentar corrida unica — descartada: es la deuda que este change cierra.

### D2: Preservar las ramas correo/telefonia

El ternario se extiende solo en el caso web. Correo (`messageIdHeader || uidFallback`) y telefonia (`call_sid`) quedan byte-identicos. El test estructural del workflow verifica que las tres ramas coexisten y que la de web ya no es `null`.

### D3: Exposicion en lectura — `IncidenteRead` + filtro exacto (OQ-B resuelta)

**Decision del autor (OQ-B)**: se implementan AMBOS — el campo en `IncidenteRead` y el filtro exacto server-side en el listado.

- **`IncidenteRead`**: se agrega `origen_message_id: str | None = None`. `from_attributes=True` ya permite resolverlo del ORM.
- **`IncidenteListItem`**: NO es requisito de este change; se puede exponer de forma aditiva si simplifica el harness, pero el minimo obligatorio es el detalle (`IncidenteRead`).
- **Filtro server-side**: `GET /api/v1/incidentes/?origen_message_id=<valor>` como `Query(None, max_length=255)`, propagado routes -> service -> `IncidenteRepository.list_filtered` como condicion exacta `Incidente.origen_message_id == valor` (solo si no es None). La correlacion exacta del harness es `GET ...?origen_message_id=corpus-R001` -> `[incidente]` -> `GET /{id}`. Respeta el alcance por rol VIS-001 sin cambios.

**Alternativas**: (a) solo `IncidenteRead` y correlacion client-side — suficiente pero obliga a traer el listado entero; (b) endpoint dedicado `/incidentes/by-origen/{id}` — descartado: mas superficie y un filtro reutiliza el listado existente. El filtro mantiene la disciplina de capas y respeta el alcance por rol (VIS-001) sin cambios.

### D4: Alineacion con la exclusion de replays

Un replay con el mismo id devuelve la fila existente con `ingresado_en`/`persistido_en` originales; el filtro por `origen_message_id` ubica esa misma fila. No se agrega marca de replay. Consistente con `docs/medicion-latencia-e2e.md` §6.

### D5: Sin migracion, sin backfill (OQ-D resuelta)

**Decision del autor (OQ-D)**: sin backfill. El indice unico 005 ya soporta el web. Las filas legacy web quedan con `NULL`. No hay cambio de esquema ni Alembic.

### D6: TDD y verificacion estructural

- Backend (SQLite unit): tests de schema (`IncidenteRead` expone el campo), del filtro de repositorio/servicio/ruta, y de idempotencia web (dos altas con el mismo id -> una fila). `pytest -m "not integration"` + `test_openapi_sync`.
- Workflow: test estructural que lee `n8n/workflow.json`, ejecuta/inspecciona el `jsCode` del normalizador con entradas web (con y sin `origen_message_id`) y verifica el id resultante; verifica que correo/telefonia siguen igual.

### D7: Opcion de SPLIT (analizada) y recomendacion

**Split A — web-dedup**: n8n web + spec `incident-intake-guards`.
**Split B — read-contract**: schemas/routes/repos + nueva spec `incident-origin-correlation`.

**Recomendacion: UN SOLO change combinado** (postura del autor). Motivos: (1) ambos cierran las OQ2/OQ6 de c-68 y c-68 depende de los dos; partirlos obliga a c-68 a declarar dos dependencias y a correlacionar el mismo flujo dos veces; (2) el filtro de lectura es lo que vuelve verificable el dedup web; (3) el alcance es pequeno y cohesivo (un ternario, un campo, un filtro). El split queda documentado como plan B si el autor prefiere revisiones separadas.

## Risks / Trade-offs

- **[Colision de ids generados]** -> `$execution.id` es unico; nunca derivar del contenido.
- **[Regresion del ternario]** -> solo se toca la rama `else`; test estructural de las tres ramas.
- **[Indice unico rechaza un web legitimo reenviado]** -> es el comportamiento deseado (dedup); un caso nuevo con texto distinto usa un id distinto.
- **[Regresion de contrato de lectura]** -> `test_openapi_sync` + tests de schema; el campo es aditivo y nullable.
- **[Correlacion por formato]** -> el harness normaliza corchetes/espacios igual que c-68 D6.

## Migration Plan

1. Implementar contrato de lectura (schemas -> repositorio -> servicio -> ruta) con tests SQLite.
2. Modificar el nodo normalizador (rama web) con test estructural del workflow.
3. Regenerar `docs/openapi.json` si el contrato cambia (`test_openapi_sync`).
4. No hay migracion Alembic. Rollback: revertir el commit (codigo + JSON); las columnas nullable no requieren limpieza.
5. Actualizar `docs/medicion-latencia-e2e.md` §6 para referenciar la correlacion exacta.

## Resolved Open Questions

Todas las OQ de este change quedaron RESUELTAS por el autor. No hay preguntas abiertas bloqueantes.

- **OQ-A (RESUELTA) — Origen del id web**: n8n es la fuente PRIMARIA (id deterministico del llamador `webBody.origen_message_id`/`corpus-<case_id>`; si falta, `web-<execution.id>-<timestamp>` unico por ejecucion). El default UUID del backend es opcional/secundario. La unicidad nunca rechaza un usuario real distinto. → D1.
- **OQ-B (RESUELTA) — Superficie de lectura**: exponer `origen_message_id` en `IncidenteRead` Y agregar el filtro exacto opcional en el listado (routes -> service -> repository), respetando VIS-001. → D3.
- **OQ-C (RESUELTA) — Formulario real**: el formulario web real NO envia id; n8n lo genera. Sin cambio de frontend. → D1 (paso 2) y D2.
- **OQ-D (RESUELTA) — Backfill**: NO hay backfill; las filas web legacy quedan con `origen_message_id` nulo. Sin migracion. → D5.
