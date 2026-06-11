## Context

Estado tras C-04 (verificado contra `Automatizacion_Mesa_de_Ayuda.json`, 15 nodos funcionales + sticky notes, `active: false`):

- **Canal correo**: `microsoftOutlookTrigger` (sondeo cada minuto) → `code` validación de correo (≥10, ≤5000 chars; emite `es_valido` y `canal_raw = 'correo'`) → `code` "Normalizar entrada del incidente" → `if` `confianza >= 0.70` → rama true: `httpRequest` `POST $env.BACKEND_URL/api/v1/incidentes`; rama false: `microsoftOutlook` (pedir datos).
- **Canal telefonía**: `twilioTrigger` → `agent` (LangChain) + `memoryRedisChat` (Redis) → `code` validación 5 pasos Anexo H §H.3 (emite `canal_raw = 'telefonia'`) → `if` `confianza >= 0.70` → rama true: `httpRequest` `POST /api/v1/incidentes`; rama false: loop al AI Agent.
- **Normalizador** (C-04): un único nodo `code` que produce `{id, timestamp (ISO-8601 ms), canal_origen, descripcion, prioridad, es_valido}` y ya soporta `canal_origen ∈ {correo, web, telefonia}`. El canal `web` está soportado en código pero **no tiene disparador**.

Lo que falta para cumplir la tesis §5.2 (tres canales), §5.3 (auditoría 30 días) y §6.3 (12 nodos: 3 triggers, normalizador, clasificación, condicional, persistencia, y **3 nodos paralelos** de notificación al usuario + registro de auditoría):

1. El disparador `webhook` del **formulario web** (el frontend ya existe y lo consume).
2. Los **nodos de notificación** al usuario post-registro (confirmación web + correo de confirmación).
3. El **nodo de auditoría** con retención de 30 días.

Verificación: la tesis §6.3 menciona "tres nodos paralelos" para notificar al usuario y registrar la ejecución. C-04 documentó (guía + Decisión 1) que el backend usa **un solo endpoint** `POST /api/v1/incidentes` con clasificación embebida, y que la pseudonimización ocurre en el backend (Decisión 2). C-05 respeta ambas decisiones y NO reabre el backend.

Constraints: Strict TDD sobre la estructura del JSON (pytest, sin runtime N8N), siguiendo el patrón de `Gestion_Incidentes/tests/test_n8n_workflow.py` (búsqueda de nodos por `type`/`name`, no por índice). Governance MEDIO. `active` permanece `false` en el JSON versionado.

## Goals / Non-Goals

**Goals:**
- Agregar el disparador `webhook` del formulario web y cablearlo al normalizador con `canal_raw = "web"`.
- Marcar de forma explícita el `canal_raw` en los tres triggers (correo, web, telefonía) para que el normalizador asigne `canal_origen` sin ambigüedad.
- Agregar los nodos de notificación al usuario post-registro (confirmación web con número de incidente; correo de confirmación) cableados después del `httpRequest` de persistencia.
- Agregar el nodo de auditoría que registra metadatos de cada ejecución (sin PII en claro) y declara la retención de 30 días.
- Extender la suite estructural pytest con casos RED→GREEN→TRIANGULATE→REFACTOR para el webhook web, las notificaciones y la auditoría.
- Actualizar `docs/n8n-workflow-guide.md` con los tres triggers, las rutas de webhook y los nodos nuevos.

**Non-Goals:**
- NO se modifica el backend FastAPI ni se crea un endpoint nuevo (se respeta la Decisión 1 de C-04: un solo `POST /api/v1/incidentes`).
- NO se reimplementa pseudonimización en N8N (se respeta la Decisión 2 de C-04); el nodo de auditoría no reintroduce PII en claro.
- NO se cambia la lógica de los nodos `code` de validación ni del normalizador ya definidos por C-04 (salvo marcar `canal_raw` en los triggers).
- NO se activa el workflow en producción (`active` queda `false`); la verificación funcional contra Docker N8N vivo se deja como tarea manual documentada (como en C-04).
- NO se implementa la persistencia real del log de auditoría en un almacén externo (Loki, Elastic, tabla SQL): el alcance es el nodo de auditoría en el workflow + la declaración de retención; el almacén concreto se eleva como decisión (ver Decisión 4).

## Decisions

### Decisión 1 — Ratificar los triggers existentes (Outlook como "IMAP", Twilio) y agregar solo el webhook web

**Elección**: el roadmap pide "trigger IMAP para Outlook". El workflow ya trae un `microsoftOutlookTrigger` (sondeo). Se **ratifica ese nodo** como el canal de correo (equivalente nativo N8N del IMAP genérico) en lugar de reemplazarlo por un nodo IMAP crudo, y se ratifica el `twilioTrigger` existente. El único trigger **nuevo** es el `webhook` del formulario web. Cada trigger marca su `canal_raw` (`correo` / `web` / `telefonia`).

**Por qué**: cambiar el `microsoftOutlookTrigger` por un nodo IMAP genérico rompería el cableado y las credenciales ya configuradas de C-04 sin beneficio funcional; el trigger de Outlook ya cumple la función de "recepción de correos del canal correo" que pide §5.2. El verdadero hueco de §5.2 es el canal web, que hoy no tiene disparador.

**Alternativa considerada**: (B) reemplazar Outlook por `n8n-nodes-base.emailReadImap`. Rechazada: rehace trabajo de C-04 sin valor; la tesis describe "monitoreado por un nodo IMAP" de forma genérica y el Outlook trigger lo satisface. Se documenta esta equivalencia en la guía para el Anexo E.

### Decisión 2 — Notificaciones por canal via Switch único; subgrafo huérfano de telefonía eliminado [REVISADA — fix apply C-05]

**Elección original**: la telefonía tenía su propio subgrafo de validación IF → HTTP POST paralelo.

**Decisión revisada (fix apply C-05)**: los tres canales convergen en el normalizador único → IF único (`La informacion esta OK`) → un único `HTTP POST a MTM-SRU`. Las notificaciones post-registro se distinguen por canal usando un nodo `switch` `Rutear por canal de origen` después del HTTP POST:
- **canal web**: Switch branch 0 → `Confirmacion web al usuario` (`respondToWebhook` con `incidente_id`).
- **canal correo / telefonía**: Switch fallback → `Correo de confirmacion al usuario` (`microsoftOutlook`).

El subgrafo huérfano anterior (`Lo que trajo puede crear un incidente` + `HTTP POST a MTM-SRU se crea un incidente`) fue **eliminado**: no tenía ninguna conexión entrante y producía código muerto que nunca se ejecutaba. Los sticky notes vacíos asociados (Sticky Note3, Sticky Note4) también se eliminaron.

El `Webhook formulario web` tiene `responseMode: responseNode`; el `respondToWebhook` queda alcanzable desde el trigger web a través del camino real (Marcar canal web → Normalizar → IF → HTTP POST → Switch → Confirmacion web).

**Por qué**: el apply C-05 introdujo el cableado incorrecto al dejar `Lo que trajo puede crear un incidente` sin entrada. La spec manda tres canales convergentes en un solo endpoint. El switch `Rutear por canal de origen` resuelve el fanout de notificaciones sin duplicar el endpoint de persistencia.

### Decisión 3 — Auditoría en TODAS las ramas; notificación al usuario solo en alta exitosa [CONFIRMADA — governance MEDIO]

**Elección original**: solo las altas exitosas llegaban a auditoría.

**Decisión confirmada (fix apply C-05)**: el log de auditoría registra **TODAS** las ramas del flujo:
- **Rama exitosa** (`confianza >= 0.70`): `HTTP POST a MTM-SRU` → nodo de auditoría con `resultado: 'creado'`.
- **Rama de rechazo** (`confianza < 0.70` o datos incompletos): la rama false del IF `La informacion esta OK` → nodo de auditoría con `resultado: 'rechazado_datos_incompletos'`.

Las **notificaciones al usuario** (confirmación web / correo de confirmación) siguen ocurriendo únicamente después de la alta exitosa (via el switch `Rutear por canal de origen`).

El nodo de auditoría usa operadores tolerantes (`|| null`, `?? null`) para todos los campos que solo existen en la respuesta HTTP (id, categoria, confianza), de forma que no explota en la rama de rechazo.

**Por qué**: la tesis §6.3 y la confirmación del usuario en governance MEDIO exigen una traza completa de auditabilidad (§11). Sin registrar los rechazos, los eventos de datos incompletos quedan sin traza. La notificación y la auditoría se mantienen desacopladas (no bloqueantes entre sí).

### Decisión 4 — El nodo de auditoría: implementación y destino del log [REVISIÓN — governance MEDIO, toca retención de datos]

**Elección**: el nodo de auditoría se implementa como un nodo `code` (JS) que arma un objeto de auditoría `{incidente_id, canal_origen, timestamp, categoria, confianza, resultado, retencion_dias: 30}` con solo metadatos (sin `descripcion` en claro). En este change el log se **emite/estructura** dentro del workflow y la retención de 30 días se **declara** como metadato y en la guía. El **destino persistente concreto** (stdout de N8N capturado por Docker logging con rotación a 30 días, vs. tabla SQL, vs. servicio de logs) se documenta como recomendación operativa, sin implementarse aquí.

**Por qué**: el alcance de C-05 es la capa de canales y el cierre del ciclo en el workflow; montar un almacén de logs con política de retención forzada es infraestructura (más cercano a C-09/C-10). Estructurar el evento de auditoría sin PII y declarar la retención cumple el requisito verificable por estructura sin sobre-construir.

**A confirmar con el usuario (governance MEDIO)**: ¿dónde debe persistir el log de auditoría para los 30 días? Opciones: (A) logging de Docker/N8N con rotación (default, cero código nuevo de backend); (B) una tabla `auditoria_ejecucion` en PostgreSQL (requiere endpoint/repo nuevo → toca backend, governance ALTO, otro change); (C) un archivo append-only montado. Default propuesto: (A), declarando la rotación de 30 días en `docker-compose`/guía. Se eleva por tocar política de retención de datos.

### Decisión 5 — Verificación Strict TDD sobre la estructura del JSON, espejando C-04

**Elección**: extender `Gestion_Incidentes/tests/test_n8n_workflow.py` con un grupo nuevo de tests (Grupo 9 en adelante) que valide, sobre el JSON exportado: presencia del `webhook` web (`type == n8n-nodes-base.webhook`, `httpMethod == POST`, `path` no vacío) cableado al normalizador; `canal_raw` por trigger; presencia de los nodos de notificación cableados tras la persistencia; presencia del nodo de auditoría con sus campos de metadatos y la retención de 30 días; y que el log de auditoría no referencie la `descripcion` cruda. Los tests buscan por `type`/`name` y por contenido del `jsCode`/parámetros, nunca por índice. La verificación funcional contra N8N vivo queda como sección manual final (como tareas 8.x de C-04).

**Por qué**: N8N no ofrece un harness liviano de CI; el JSON exportado es el artefacto de entrega y su estructura es determinística. Encaja en el nivel "unit" de la pirámide (§6.5) y permite ciclos RED→GREEN→TRIANGULATE→REFACTOR.

### Decisión 6 — Ruta del webhook web estable y documentada

**Elección**: el `webhook` web usa una ruta fija y legible (p. ej. `path: "incidente-web"`), de modo que el frontend la consuma como `POST {N8N_BASE_URL}/webhook/incidente-web`. La ruta se documenta en la guía; el `webhookId` lo asigna N8N.

**Por qué**: una ruta estable es contrato con el frontend; dejarla autogenerada la haría frágil entre importaciones.

## Risks / Trade-offs

- **[La telefonía no recibe notificación explícita de confirmación]** → Mitigación: Decisión 2 documenta que la confirmación telefónica se da en la respuesta del webhook; se eleva al usuario si requiere SMS de confirmación (otro producto Twilio, fuera de scope).
- **[La retención de 30 días se declara pero no se fuerza por infraestructura en este change]** → Mitigación: Decisión 4 estructura el evento y declara la política; el destino persistente con rotación se documenta como recomendación operativa para C-09/C-10. Riesgo de que en un despliegue real no se configure la rotación → se marca explícitamente en la guía.
- **[El nodo de auditoría podría filtrar PII si se incluye `descripcion` por error]** → Mitigación: el spec y un test estructural verifican que el log de auditoría NO referencie `descripcion`/PII; solo metadatos.
- **[El webhook web sin autenticación quedaría expuesto]** → Mitigación: §5.2 indica acceso "mediante autenticación corporativa única"; se documenta que el webhook debe protegerse (header de auth / red interna) en el despliegue. La auth concreta no se implementa en C-05 (depende del entorno) y se anota como Open Question.
- **[Tests de estructura no garantizan ejecución funcional en N8N]** → Mitigación: verificación manual documentada (import + corrida por canal) en la guía, como en C-04. Los tests cubren el contrato estructural, no la semántica del runtime.
- **[Discrepancia tesis §6.3 (POST /api/v1/clasificar separado) ya documentada en C-04]** → C-05 no reabre esa decisión; la hereda. Se mantiene la nota para el Anexo E (C-10).

## Open Questions

- ~~¿La auditoría registra solo altas o también rechazos y ruteos a revisión humana?~~ **CERRADA**: confirmado en fix apply C-05 — todas las ramas.
- ~~¿El canal web confirmación llega al respondToWebhook?~~ **CERRADA**: fix apply C-05 resolvió el subgrafo huérfano; ahora el canal web alcanza `Confirmacion web al usuario` via Switch.
- ¿La notificación telefónica debe ser un SMS de confirmación vía Twilio, o basta la respuesta del webhook/TwiML? (Decisión 2 — pendiente; la telefonía hoy usa el correo de confirmación como fallback del Switch.)
- ¿Dónde persiste el log de auditoría para los 30 días: logging Docker/N8N con rotación (default), tabla SQL (toca backend), o archivo? (Decisión 4 — elevar; toca retención de datos.)
- ¿Cómo se autentica el webhook web (header firmado, red interna, SSO corporativo)? La tesis §5.2 menciona "autenticación corporativa única"; el mecanismo concreto depende del entorno de despliegue.
