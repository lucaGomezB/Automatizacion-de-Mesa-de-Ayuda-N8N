## Context

Ver `proposal.md — Why` para la motivacion. Estado actual y restricciones que moldean el enfoque:

- El workflow `n8n/workflow.json` define el canal telefonico como `Llamada telefonica -> AI Agent -> Se verifica lo que trajo la IA -> La clasificacion de la IA es valida`; la rama falsa de ese IF vuelve a `AI Agent` sin tope ni contador. El nodo `AI Agent` (typeVersion 3.1) tiene `options: {}`. El unico nodo HTTP de persistencia es `HTTP POST a MTM-SRU`, que hoy envia solo `descripcion`, `prioridad` y `canal_origen_id`.
- El trigger `Llega un email a Mesa de Ayuda` (microsoftOutlookTrigger) filtra `readStatus: unread`, sin filtro de fecha, y expone `id` y `receivedDateTime`. El unico nodo `Marcar correo como leido` cuelga de la salida 1 (correo) de `Rutear por canal de origen`; las ramas de rechazo y error no lo alcanzan.
- `App/Backend` tiene capas `routes -> services -> repositories -> models`; el endpoint de alta (`POST /api/v1/incidentes/`) delega en `IncidenteService.create_and_classify`, que pseudonimiza, persiste y clasifica con `HybridClassifier` (deterministico -> Gemini pago). No hay idempotencia ni aceptacion de clasificacion precalculada.
- `IncidenteCreate` acepta `descripcion`, `prioridad`, `canal_origen_id`. `ClasificacionEtapa` es un `Literal` restringido a `deterministic | gemini | fallback`; la columna `clasificacion_log.etapa` es `String(30)`.
- `docker-compose.yml:74` fija `N8N_WEBHOOK_URL=http://n8n:5678/webhook` (sin ruta); el unico webhook de N8N es `path: "incidente-web"`. La notificacion de `notify_n8n` hoy 404ea de forma accidental.
- Convenciones de test: `App/Backend/tests/test_n8n_workflow.py` valida la ESTRUCTURA del JSON sin runtime N8N; `test_api_incidentes.py` usa el cliente ASGI y `make_client_with_classifier`; las migraciones se prueban contra la base descartable (c-32).
- **Gobernanza**: los cambios en `n8n/workflow.json` son ALTA (modifican comportamiento que afecta datos de usuario) y la migracion de esquema es ALTA. El apply MUST obtener checkpoint de aprobacion humana antes de escribir esos artefactos.

## Goals / Non-Goals

**Goals:**

- Eliminar los tres caminos de gasto pago no acotado: reintento telefonico sin tope, reclasificacion server-side sobre resultado ya producido, y reproceso por correo no leido / replay de webhook.
- Que cada guarda sea verificable sin credenciales reales: tests estructurales del workflow + tests de contrato de la API.
- Mantener el comportamiento de refinamiento dentro del tope y la clasificacion server-side para el camino sin resultado precalculado.
- Hacer explicita (no accidental) la separacion entre el webhook de alta y la superficie de notificacion.

**Non-Goals:**

- No se toca el doble transcribe de Twilio ni la version de la imagen `n8nio/n8n`.
- No se modifica el pipeline deterministico ni los umbrales de clasificacion.
- No se agrega autenticacion nueva al webhook de notificacion mas alla del secreto existente `X-N8N-Secret`.
- No se implementa deduplicacion generica de correos historicos ni backfill de datos.

## Decisions

### D1 — Tope de refinamiento telefonico con `maxIterations` + contador explicito y salida terminal a revision humana

Se fija `options.maxIterations = 2` en el nodo `AI Agent` como backstop duro, y ademas un contador explicito `intento_agente` que el nodo `Se verifica lo que trajo la IA` incrementa en cada pasada. La rama falsa de `La clasificacion de la IA es valida` deja de ir directo a `AI Agent`: pasa por un IF nuevo `Tope de refinamiento alcanzado` con condicion `intento_agente < 2`; verdadero -> `AI Agent` (refina), falso -> `Derivar a revision humana` (Code). El nodo terminal marca `confianza=0.0`, `requiere_revision_humana=true`, `revision_forzada=true` y conserva `canal_raw='telefonia'`, y alimenta un camino de persistencia que NO vuelve al agente. El normalizador y el IF compartido se ajustan para que un item con `revision_forzada=true` llegue a `Login operador -> HTTP POST a MTM-SRU` sin pasar por la rama de descarte.

- **Razon**: `maxIterations` solo es un backstop del runtime y no distingue "refinamiento intencional" de "bucle"; el contador explicito hace el tope verificable por la suite estructural y garantiza que NUNCA se reinvoca al agente pago al agotarse. El marcador `revision_forzada` separa la persistencia-para-revision de telefono del rechazo de correo (que no debe crear incidente).
- **Alternativas consideradas**: (a) solo `maxIterations` — descartado porque al agotarse el runtime corta sin persistir, incumpliendo "persiste con requiere_revision_humana=true"; (b) solo contador sin `maxIterations` — descartado porque deja el backstop del runtime sin red de seguridad; (c) crear el incidente directo a la base desde N8N — descartado por romper la capa API y la disciplina de capas.

### D2 — Marcar el correo como leido en las tres ramas terminales, con guarda de canal

Se agrega una guarda de canal (`Es correo?` sobre `canal_origen == 'correo'`) delante de `Marcar correo como leido` en las ramas de rechazo y error, porque el nodo referencia `$('Llega un email a Mesa de Ayuda').item.json.id` y fallaria en canales que no pasaron por el trigger de Outlook. Para la rama de error se configura `onError: "continueErrorOutput"` en los nodos de persistencia relevantes y se cablea su salida de error a la rama que marca como leido (guardada por canal). La rama de exito existente se conserva.

- **Razon**: un mensaje no leido se re-levanta cada minuto; marcar como leido es la unica forma de cerrar el ciclo del canal correo. La guarda de canal evita que la guarda de costo introduzca un nuevo defecto de cableado en web/telefonia.
- **Alternativas consideradas**: (a) mover el nodo a un punto comun previo al ruteo — descartado porque marcaria como leido un correo antes de saber si el alta fue exitosa; (b) un unico nodo con `alwaysOutputData` sin guarda — descartado porque la referencia al trigger de Outlook es invalida en otros canales.

### D3 — Lookback de 24 horas declarado en el trigger de Outlook

El trigger `Llega un email a Mesa de Ayuda` agrega a `filters` un filtro de fecha sobre `receivedDateTime` con lookback de 24 horas (expresion relativa a `$now`), conservando `readStatus: unread`. El valor elegido es 24 h: cubre el backlog de un dia de operacion sin arrastrar el historial completo, y queda declarado en el JSON.

- **Razon**: el arranque con una casilla real puede tener cientos de no leidos; sin tope, la rafaga dispara un incidente por correo (y potencial clasificacion paga) de forma simultanea. 24 h acota el dano y es un valor operativamente razonable y facil de auditar.
- **Alternativas consideradas**: (a) ventana de 1 h — descartado por riesgo de perder correos legitimos fuera de horario; (b) 7 dias — descartado por mantener una rafaga grande; (c) depender de que el operador archive manualmente — descartado por no ser automatico ni verificable.
- **Nota**: la forma exacta del objeto de filtro (`receivedDateTime`) se confirma contra la version de la imagen durante el apply; el comportamiento especificado (solo mensajes dentro de 24 h) y el desglose de tareas no cambian.

### D4 — Idempotencia por `origen_message_id` con restriccion UNIQUE nullable e implementacion idempotente ante carrera

Se agrega `origen_message_id: Mapped[str | None]` (`String(255)`, `unique=True`, `nullable=True`, indexado) al modelo `Incidente`, con una migracion nueva (`005`) que no muta `001`. El repositorio expone `get_by_origen_message_id`. El servicio busca por ese identificador ANTES de pseudonimizar y clasificar: si existe, retorna el incidente existente sin clasificar ni notificar. Ante una violacion de unicidad concurrente (`IntegrityError`), el servicio re-consulta por el identificador y retorna el incidente ya persistido.

- **Razon**: el chequeo previo elimina la llamada paga en el caso comun (replay secuencial) y la restriccion UNIQUE + manejo de `IntegrityError` elimina la carrera. Nullable preserva el alta directa sin identificador (formulario web y clientes API).
- **Alternativas consideradas**: (a) tabla de deduplicacion separada — descartada por agregar una entidad y un join sin beneficio; (b) hash de contenido como clave — descartado porque el `Message-ID` es el identificador estable provisto por Outlook y el scope lo aprueba explicitamente; (c) solo chequeo aplicativo sin constraint — descartado porque no protege contra concurrencia.

### D5 — Clasificacion precalculada opcional con origen auditable via `etapa`

`IncidenteCreate` incorpora campos opcionales: `origen_message_id`, un marcador de evento (`origen_evento`) y un bloque `clasificacion` (`ClasificacionPrecalculada`) con `sector_predicho`, `sectores_adicionales`, `confianza`, `requiere_revision_humana` y `origen`. La presencia del bloque hace que el servicio construya un `ClasificacionResult` con `etapa="precalculada"` y lo aplique SIN invocar `HybridClassifier`. Los campos ausentes se persisten como nulos. El `origen` del emisor se conserva en `respuesta_raw` como metadata de auditoria. Se extiende el `Literal` `ClasificacionEtapa` con `"precalculada"` (la columna `String(30)` no requiere migracion). Para telefono agotado, el terminal envia el bloque con `requiere_revision_humana=true` y `confianza=0.0`, sin sector.

- **Razon**: un bloque opcional hace explicita la intencion ("clasificacion provista") y evita ambiguedad con valores sueltos; `etapa="precalculada"` reutiliza un campo de auditoria existente y permite distinguir el origen sin nueva columna; admitir ausencia de sector cubre el caso de refinamiento agotado sin forzar un sector invalido.
- **Alternativas consideradas**: (a) campos planos en `IncidenteCreate` — descartado por ambiguedad entre "no provisto" y "provisto nulo"; (b) nueva columna `clasificacion_origen` — descartada por migracion adicional cuando `etapa` + `respuesta_raw` ya auditan; (c) exigir sector siempre — descartado porque el caso de agotamiento no tiene sector valido y forzarlo seria incorrecto.

### D6 — Validacion estricta de lo provisto y rechazo de eventos que no crean incidentes

Los validadores del schema rechazan un `sector_predicho` presente fuera del conjunto canonico y una `confianza` presente fuera de `[0.0, 1.0]`. El endpoint rechaza con 422 un `origen_evento` cuyo valor no sea de creacion de incidente (por ejemplo `notificacion`); un payload sin marcador se trata como alta directa. El `origen_evento` validado se persiste en la fila creada (columna nullable de la migracion 005); el reintento idempotente no lo reescribe.

- **Razon**: la validacion en el borde evita que un emisor con un contrato roto omita la clasificacion server-side con datos invalidos, y el marcador de evento es la barrera explicita contra el bucle backend -> N8N -> backend.
- **Alternativas consideradas**: confiar en el emisor — descartado porque el objetivo del change es precisamente no confiar en la disciplina externa.

### D7 — Notificacion a un webhook dedicado que no crea incidentes

Se agrega al workflow un webhook dedicado (`path: "notificacion-clasificacion"`) que NO se conecta a la creacion de incidentes (destino no-op/auditoria), y `docker-compose.yml` apunta `N8N_WEBHOOK_URL` a `http://n8n:5678/webhook/notificacion-clasificacion`. El payload de `notify_n8n` agrega el marcador `evento: "notificacion"`. La guia del workflow documenta el acoplamiento de forma explicita.

- **Razon**: el 404 actual es una seguridad accidental; separar la superficie de notificacion del webhook de alta convierte la garantia en una propiedad verificable (dos rutas distintas) reforzada por el marcador de evento. El cambio es de configuracion y no bloquea la respuesta (fire-and-forget).
- **Alternativas consideradas**: (a) dejar la URL vacia — descartada porque deshabilita la notificacion y mantiene la ambiguedad; (b) apuntar al webhook `incidente-web` — descartado porque expondria el bucle backend -> N8N -> backend; (c) crear la ruta por defecto sin nodo — descartada porque la ruta debe existir en el workflow para no ser un 404 accidental.

## Risks / Trade-offs

- **[Forma exacta de opciones de N8N segun `latest`]** `maxIterations` y el filtro de fecha del trigger pueden variar entre versiones. -> Mitigacion: los tests estructurales afirman la presencia del tope y del lookback; el arnés de c-31 valida el comportamiento end-to-end; un desalineamiento produce fallo ruidoso, no un falso verde.
- **[El nodo de marcado de correo referencia el trigger por nombre]** Si se ejecuta en un canal que no paso por Outlook, la expresion falla. -> Mitigacion: guarda de canal `Es correo?` obligatoria en las ramas de rechazo y error.
- **[Persistencia de telefono agotado sin sector]** El incidente puede quedar con `sector_id` nulo y `requiere_revision_humana=true`. -> Mitigacion: es el comportamiento correcto de "pendiente de revision"; el esquema ya admite `sector_id` nullable y el log de clasificacion registra `etapa="precalculada"`.
- **[Confianza en el emisor N8N]** Al omitir la reclasificacion server-side, una clasificacion precalculada erronea ya no se corrige en el backend. -> Mitigacion: validacion estricta de vocabulario y rango en el borde, mas el validador N8N existente (Anexo H §H.3); confianza menor al umbral deriva a revision humana.
- **[Idempotencia estricta por `Message-ID`]** Si Outlook reutiliza un `Message-ID` (no deberia) o el campo no llega, la guarda no aplica. -> Mitigacion: `origen_message_id` nullable y opcional; el comportamiento por defecto sin identificador es el alta normal.
- **[Migracion sobre datos existentes]** Agregar una columna nullable con unique no rompe filas existentes, pero un indice unico en PostgreSQL convive con muchos NULL. -> Mitigacion: columna nullable; verificar `upgrade`/`downgrade` en la base descartable y la migracion 005 no muta 001.
- **[Cambio de `N8N_WEBHOOK_URL`]** Al apuntar a una ruta nueva, mientras el workflow no tenga el nodo el POST seguira fallando (pero de forma no bloqueante). -> Mitigacion: la notificacion es fire-and-forget y se aisla de fallos; la ruta dedicada se agrega en el mismo change.

## Migration Plan

1. Backend: agregar la migracion `005` (`origen_message_id` UNIQUE nullable + `origen_evento` nullable sin unicidad), los campos en el modelo, el metodo del repositorio, los schemas y la rama del servicio; extender `ClasificacionEtapa` con `"precalculada"`. La columna `origen_evento` viaja en la misma revision 005 para satisfacer el escenario "Evento de creacion crea el incidente" (el marcador declarado queda persistido; sin marcador, nulo).
2. Tests: escribir primero los RED (API + migracion) y luego el GREEN (SQLite unit subset y subconjunto PostgreSQL con la base descartable de c-32).
3. N8N (checkpoint de aprobacion ALTA): tope de refinamiento + salida terminal, marcado de correo en todas las ramas, lookback de 24 h, payload enriquecido y webhook dedicado de notificacion.
4. Infra: apuntar `N8N_WEBHOOK_URL` al webhook dedicado.
5. Documentacion: actualizar `docs/n8n-workflow-guide.md` (tope, ciclo de vida del correo, lookback y acoplamiento de la notificacion).
6. Rollback: `alembic downgrade` de la 005 (elimina columna/constraint); revertir `n8n/workflow.json`, `docker-compose.yml` y la documentacion. Como `origen_message_id` es nullable y los campos nuevos son opcionales, un backend viejo y un workflow nuevo (o viceversa) conviven sin perdida de datos.

## Open Questions

- La forma exacta del filtro `receivedDateTime` y la clave de la opcion de tope del agente (`maxIterations` u otra) segun la version de `n8nio/n8n:latest` se confirman durante el apply; no cambian el comportamiento especificado ni el desglose de tareas.
