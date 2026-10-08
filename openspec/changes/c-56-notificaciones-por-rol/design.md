# Design: Notificaciones de incidente con destinatarios resueltos por rol

## Context

Ver `proposal.md` — Why. Restricciones verificadas que moldean el enfoque:

- **Directorio y roles ya existen (c-54, no archivado).** `directorio_empleado` (migraciones 009/010) guarda `legajo`, `nombre`, `email` (texto plano, unico), `telefono`, `sector_id` (FK al catalogo canonico `sector`), `rol` (`usuario_final` | `operador` | `administrador_directorio`), `activo` y `fecha_baja`. `DIR-003` declara que un `operador` MAY ser destino de enrutamiento de su sector; `DIR-004` exige sector para `usuario_final`/`operador` y lo prohibe para `administrador_directorio`.
- **Seam de resolución ya existe (c-54).** `ContactResolutionService` resuelve un empleado por telefono/email/usuario. `RES-005` anticipa su uso para "resolucion de destinatario y enrutamiento por sector/rol", pero hoy solo resuelve identidad individual, NO enumera destinatarios por rol/sector.
- **La notificación de revisión vive en el flujo de alta, no en el webhook.** El nodo `Notificar operador designado` cuelga del gate post-POST `Requiere revision humana` (rama true), dentro del flujo disparado por la respuesta de `POST /api/v1/incidentes`. El webhook dedicado `notificacion-clasificacion` (C-33) es OTRO flujo: recibe `notify_n8n` y hoy solo audita (`Auditar notificacion`).
- **El backend conoce el sector al clasificar.** `IncidenteService._apply_classification` resuelve `sector_id` desde `result.sector_predicho` y ya llama a `_dispatch_notification(incidente.id, result)` fire-and-forget.
- **`numero_incidente` es un campo derivado (c-53).** `IncidenteRead.numero_incidente` se deriva del PK en un único punto (`formatear_numero_incidente`); todas las notificaciones lo usan.
- **Estado del workflow (c-53/c-55).** El nodo del operador es `n8n-nodes-base.emailSend` (SMTP) con `toEmail = "={{ $env.OPERATOR_EMAIL }}"`. `OPERATOR_EMAIL` y `SMTP_FROM_EMAIL` se exponen desde `docker-compose.yml`; el valor por defecto de `OPERATOR_EMAIL` es un placeholder, no una direccion real.
- **Privacidad (c-54, Ley 25.326).** `DIR-005` guarda el contacto en texto plano (personal pero no sensible, art. 2); `DIR-006` prohibe PII en logs, respuestas de error y auditoria, y exige que la resolucion interna no atraviese la API publica ni exponga datos de contacto fuera del proceso. `RES-006` prohibe telefono/email en claro en la trazabilidad.
- **Realidad de bootstrap.** Hoy el usuario tiene UNA casilla personal en el `.env` raiz (usada por compose para `OPERATOR_EMAIL`/`SMTP_FROM_EMAIL`); mas adelante se le asignara un rol en el directorio. La resolucion por directorio debe agregarse ENCIMA del camino de un solo destinatario, sin romperlo.

## Goals / Non-Goals

**Goals:**

- Resolver backend-side los destinatarios de la notificación de revisión humana desde el directorio, por rol y sector.
- Entregar a N8N la lista de destinatarios resueltos, con precedencia del directorio y fallback al destinatario unico del entorno.
- Preservar el camino de un solo destinatario y el caracter fire-and-forget de la notificacion.
- Minimizar la exposicion de PII y no duplicar el seam de resolucion de c-54.

**Non-Goals:**

- Cambiar el transporte de correo (c-55) ni el SMS de telefonia (c-53, diferido).
- Enrutar a `administrador_directorio`/`usuario_final` o por sectores adicionales (diferido).
- UI de administracion del directorio ni sincronizacion con RRHH.
- Migracion de esquema.
- Implementar codigo en esta fase (propose/design only).

## Decisions

### D1 — Fuente de verdad y semantica del rol

Los destinatarios se resuelven desde `directorio_empleado` (c-54), que es la unica fuente de verdad de roles/emails. Un destinatario valido es un empleado `activo=true` con `rol=operador` cuyo `sector_id` coincide con el sector predicho principal del incidente. `usuario_final` (reportante) y `administrador_directorio` (gestion) MUST NOT ser destinatarios. Alternativa rechazada: mantener la lista de destinatarios hardcodeada en variables de entorno de N8N — es el problema que este change elimina. Alternativa rechazada: derivar el rol del sector — confundiria "que sector atiende" con "que puede hacer" (ya rechazado en c-54 D2).

### D2 — Contrato backend -> n8n: respuesta de alta (opcion ELEGIDA)

La lista de destinatarios viaja en la **respuesta de alta** `POST /api/v1/incidentes` como `destinatarios_revision: list[str]`. Justificacion: es el payload que YA impulsa el gate `Requiere revision humana` donde vive el nodo del operador, por lo que el cambio preserva la topologia, las garantias de auditoria (c-38/c-40) y la ubicacion del nodo.

| Opcion | Trade-off | Decision |
|--------|-----------|----------|
| **Respuesta de alta** | Cambia el contrato de la respuesta de creacion (OpenAPI); pone emails en una respuesta autenticada consumida por N8N | **Elegida** |
| Webhook `notificacion-clasificacion` | Mejor privacidad (canal dedicado con `X-N8N-Secret`) y mas limpio conceptualmente, pero OBLIGA a MOVER el nodo del operador al flujo de notificacion; la notificacion pasaria a depender del webhook fire-and-forget (si `N8N_WEBHOOK_URL` esta vacio, no habria aviso) | Rechazada por regresion funcional y blast radius |
| Endpoint que N8N consulta | Round-trip extra y superficie HTTP que expone contactos (oraculo); `DIR-006` lo prohibe | Rechazada |

Se expone el campo SOLO en la respuesta de creacion (modelo de respuesta dedicado o campo con default vacio); no se agrega a `GET`/list para no ampliar la superficie. La interpolacion de la PII y su conciliacion con `DIR-006` se tratan en D8.

### D3 — Precedencia del directorio y fallback

Regla de precedencia: si el directorio resuelve >=1 operador activo del sector, se usan esos; si resuelve 0 (directorio vacio, sin operador del sector, o todos inactivos), el backend emite una lista VACIA y N8N cae al fallback `$env.OPERATOR_EMAIL` (un unico destinatario). Asi el comportamiento actual (una casilla) queda intacto mientras el directorio esta vacio, y el directorio gana en cuanto se puebla ("directory takes precedence once populated"). Alternativa rechazada: que el backend duplique el valor de fallback en su propia configuracion — duplicaria el dato y exigiria cablear compose; el fallback ya vive donde hoy funciona. Alternativa rechazada: fallback silencioso a "no enviar" — perderia el aviso.

### D4 — Multiples destinatarios: un correo por destinatario

N8N `emailSend` acepta una lista separada por comas en `toEmail`, y N8N ejecuta un nodo una vez por item. Se agrega un Code node `Preparar destinatarios de revision` que lee `destinatarios_revision` y, si esta vacio, usa `[ $env.OPERATOR_EMAIL ]`; emite UN item por destinatario con el `numero_incidente`. El nodo `Notificar operador designado` usa `toEmail = {{ $json.destinatario }}`, de modo que se envia una copia por destinatario y la lista completa NO se expone entre operadores. Alternativas rechazadas: un solo correo con `To` multi-direccion (expone los emails del sector entre si), `Cc`/`Bcc` (el `To` sigue exponiendo al menos uno, y complica la resolucion del fallback). Auditoria: `Registro de auditoria` se cuelga en PARALELO desde la rama true del gate (una entrada por incidente, no una por destinatario) y con `onError: continueRegularOutput` en el nodo de envio se preserva `N8N-AUDIT-003` (la auditoria es alcanzable aunque el envio falle).

### D5 — Resolucion reutilizando el seam de c-54 (sin duplicar)

Se agrega `EmpleadoRepository.listar_operadores_por_sector(sector_id)` (activos, `rol=operador`) y un servicio `NotificationRecipientService` que lo compone y devuelve la lista de emails normalizados (`normalizar_email`). NO se reimplementa la resolucion de identidad (`RES-001..RES-006`): la enumeracion por rol/sector es una consulta nueva sobre el MISMO directorio, no un segundo resolutor. Alternativa rechazada: un modulo de resolucion propio — duplicaria logica y divergiria de la fuente de verdad.

### D6 — Momento de la resolucion y no-bloqueo

La resolucion se ejecuta en `IncidenteService._apply_classification`/`create_and_classify`, SOLO cuando `result.requiere_revision_humana` es verdadero, y adjunta la lista al incidente para serializarla en la respuesta. Es una lectura indexada (`sector_id` indexado) acotada al caso de revision; el ENVIO del correo sigue ocurriendo en N8N despues de la respuesta, por lo que la garantia fire-and-forget del alta se conserva. Un fallo o directorio vacio NO es fatal: produce lista vacia y el flujo continua. Alternativa rechazada: resolver dentro de la tarea fire-and-forget de `notify_n8n` — esa tarea no tiene sesion de base de datos y agregar una abriria ciclo de vida de sesion en background.

### D7 — Alcance del enrutamiento

Se enruta por el sector PREDICHO PRINCIPAL del incidente. Los sectores adicionales (`sectores_adicionales`, c-27) quedan DIFERIDOS: incluirlos multiplicaria los avisos por incidente y un operador pertenece a un solo sector (c-54). Un incidente sin sector resuelto (p. ej. derivado a revision forzada con `sector_id` nulo) produce lista vacia y usa el fallback. Alternativa considerada y diferida: union de operadores de sectores principal + adicionales.

### D8 — Privacidad: frontera de los emails de destinatario

El email del operador es dato personal (c-54 DIR-005) y debe llegar al componente que envia el correo (N8N SMTP, c-55). Conciliacion con `DIR-006`: lo que c-54 prohibe es que el SERVICIO DE RESOLUCION se convierta en un oraculo publico de contactos y que la PII aparezca en logs/auditoria; no prohibe direccionar una notificacion a su destinatario legitimo. Precedente ya existente: la confirmacion al reportante YA manda el email del remitente a N8N (`N8N-EMAIL-002`). Mitigaciones: el campo viaja solo en la respuesta de creacion autenticada (JWT), no se agrega a `GET`/list, no se registra en logs ni en el nodo de auditoria, y el backend no loguea emails en claro (`RES-006`). Governance ALTO: requiere revision humana.

### D9 — Sin migracion de esquema

No hay tablas ni columnas nuevas. Se reutiliza `directorio_empleado` y el catalogo `sector`. La migracion 009/010 de c-54 es prerequisito. El alta del operador real (hoy casilla personal del `.env`) se hace cargando una fila en el directorio via la API de c-54 (`rol=operador`, con sector), sin semilla de PII real; una vez activa, el directorio toma precedencia.

### D10 — Estrategia de tests

- **Unit (SQLite, `-m "not integration"`)**: `listar_operadores_por_sector` (solo activos, solo `operador`); `NotificationRecipientService` (0/1/N, sector sin match, sector nulo, inactivos excluidos, `usuario_final`/`administrador` excluidos); la respuesta de alta incluye `destinatarios_revision` poblada solo con revision; sin revision => vacia; ausencia de emails en logs.
- **Integration (PostgreSQL, `-m integration`)**: FK a `sector`, indice de `sector_id`, igualdad real de la enumeracion.
- **Estructural N8N (offline)**: presencia del Code node, `toEmail` por item, fallback `$env.OPERATOR_EMAIL`, auditoria en paralelo, `onError`, no regresion c-38/c-40/c-53/c-55, conteo de nodos.
- **Smoke manual**: requiere la casilla Gmail de c-55 y un operador cargado en el directorio.

### D11 — Dependencias y orden de archivado

Los deltas de `n8n-workflow` se basan en el estado vigente de la main spec; c-53, c-54 y c-55 estan sin archivar. Orden: c-52 -> c-53, c-54, c-55 (cualquier orden entre los tres) -> c-56. El delta del operador de c-56 asume el nodo `emailSend`/SMTP que introduce c-55.

### D12 — Documentacion y conteos

`docs/n8n-workflow-guide.md` y `N8N-DOC-001` exigen que los conteos de nodos y pruebas coincidan con el JSON y la suite. Se agrega 1 Code node (28 -> 29; el conteo real del `workflow.json` vigente, corregido respecto del `37 -> 38` originalmente estimado) y se actualiza la tabla de variables (`OPERATOR_EMAIL` pasa a ser fallback). Regenerar `docs/openapi.json`.

## Risks / Trade-offs

- **[PII en la respuesta de alta]** emails de operadores en un body HTTP autenticado -> Mitigacion: campo solo en creacion y solo con revision, no en `GET`/list, sin logs ni auditoria (D8); revision humana HIGH.
- **[Regresion estructural N8N]** agregar Code node y cambiar el nodo del operador -> Mitigacion: tests estructurales de no regresion (c-38/c-40/c-53/c-55) y auditoria en paralelo (D4).
- **[Directorio vacio o desactualizado]** sin operador del sector -> Mitigacion: fallback al destinatario unico del entorno (D3); "no encontrado" no es fatal.
- **[Fuga entre destinatarios]** exponer la lista del sector -> Mitigacion: un correo por destinatario (D4).
- **[Lectura adicional en el alta]** resolver en el camino de creacion -> Mitigacion: solo con revision y sobre columna indexada (D6).
- **[Choque con c-53/c-55 sin archivar]** deltas sobre specs compartidas -> Mitigacion: orden de archivado y delta base sobre el estado vigente (D11).

## Migration Plan

1. `EmpleadoRepository.listar_operadores_por_sector` + tests RED/GREEN/TRIANGULATE.
2. `NotificationRecipientService` (compone repositorio + `normalizar_email`) con tests.
3. Esquema de respuesta y `IncidenteService` (poblar `destinatarios_revision` solo con revision) con tests; regenerar `docs/openapi.json`.
4. `n8n/workflow.json`: Code node `Preparar destinatarios de revision`, `toEmail` por item, auditoria en paralelo y `onError`; actualizar `test_n8n_workflow.py` y la guia.
5. Verificacion: suite offline, integracion, OpenAPI sync, ruff, `openspec validate --strict`.
6. Smoke manual con Gmail y un operador sintetico cargado en el directorio.
7. Rollback: revertir el commit y reimportar `n8n/workflow.json` previo; sin migracion ni backfill.

## Open Questions

RESUELTAS por el autor el 2026-10-07:

1. **Contrato (D2)** — RESUELTA (A): los destinatarios viajan en la respuesta de alta `POST /api/v1/incidentes` como `destinatarios_revision`. Se acepta el costo de PII en el body autenticado (menor blast radius).
2. **Frontera de PII (D8)** — RESUELTA (SI): enviar los emails de operadores a N8N en la respuesta de alta es consistente con `DIR-006` (no convierte al resolutor en un oraculo publico y no se registra en logs/auditoria). Aceptado explicitamente por el autor (governance ALTO).
3. **Alcance (D7)** — RESUELTA (SI): enrutamiento por el sector PRINCIPAL predicho unicamente; los sectores adicionales quedan diferidos.
4. **Fallback (D3)** — RESUELTA (SI): el fallback sigue siendo `$env.OPERATOR_EMAIL` en N8N (un unico destinatario); el backend emite lista vacia cuando no hay operador activo del sector.
5. **Smoke (D10)** — RESUELTA: el autor confirma disponibilidad para el smoke manual con la casilla Gmail de c-55 y un operador cargado en el directorio.
