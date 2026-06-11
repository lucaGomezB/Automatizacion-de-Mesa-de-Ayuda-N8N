## Context

El workflow `Automatizacion_Mesa_de_Ayuda.json` (N8N 1.62, `active: false`) tiene 16 nodos. Estado actual verificado contra el JSON:

- **Canal correo**: `microsoftOutlookTrigger` → `code` (validación, placeholder `myNewField = 1`) → `if` (sin condiciones) → rama NO: `microsoftOutlook` (pedir datos) / rama SÍ: `httpRequest` "HTTP POST a MTM-SRU".
- **Canal telefonía**: `twilioTrigger` → `agent` (LangChain AI Agent) + `memoryRedisChat` (Redis) → `code` (validación, placeholder) → `if` (sin condiciones) → `httpRequest` "HTTP POST a MTM-SRU se crea un incidente".
- 6 nodos `stickyNote` (documentación visual, se conservan).
- No existe nodo de normalización; cada canal tiene su forma cruda.

Backend FastAPI verificado (`Gestion_Incidentes/app/`):

- `POST /api/v1/incidentes` (`routes/incidentes.py`) recibe `IncidenteCreate` (`descripcion` 10–5000 chars, `prioridad`, `canal`) y llama `IncidenteService.create_and_classify(payload)`, que ejecuta el **pipeline híbrido completo** (determinístico → Gemini → fallback) y devuelve `IncidenteRead` con `sector`, `confianza` y el indicador de revisión humana. Status 201.
- `/api/v1/clasificaciones` (`routes/clasificaciones.py`) expone solo GET (cola de revisión, historial) y PATCH (validación humana). **No existe `POST /api/v1/clasificar`.**

Constraints: tesis §5.3 (estructura unificada: id, timestamp ms, canal, descripción), §6.3 (12 nodos, ruteo por confianza), Anexo H §H.3 (validación de 5 pasos), umbral 0.70 inclusivo, categorías exactas case-sensitive. Strict TDD activo. Governance MEDIO. C-03 ya pseudonimiza el texto que va a Gemini.

## Goals / Non-Goals

**Goals:**
- Dejar el workflow exportado funcional: sin placeholders, con condiciones IF reales, con normalización de canales y persistencia contra el backend real.
- Implementar la validación del Anexo H (entrada por canal + respuesta de clasificación de 5 pasos) en los nodos `code`.
- Hacer el JSON declarativo verificable bajo Strict TDD mediante pruebas pytest sobre la estructura exportada.
- Documentar el flujo en `docs/n8n-workflow-guide.md`.

**Non-Goals:**
- NO se configuran los triggers de los canales (IMAP, Webhook web, Webhook Twilio) ni los nodos de notificación/auditoría — eso es C-05.
- NO se implementa un endpoint `POST /api/v1/clasificar` en el backend (ver Decisión 1).
- NO se modifica el pipeline de clasificación ni los servicios del backend.
- NO se activa el workflow en producción (`active` queda en `false`); la verificación es en entorno de pruebas.

## Decisions

### Decisión 1 — Una sola llamada HTTP (`POST /api/v1/incidentes`) en lugar de clasificar + persistir por separado [REVISIÓN — governance MEDIO]

**Elección**: el workflow invoca **un único** nodo HTTP a `POST /api/v1/incidentes`. La clasificación y la persistencia ocurren atómicamente en el backend vía `create_and_classify`; la respuesta 201 ya trae `sector`, `confianza` y el flag de revisión. El nodo `if` rutea evaluando la respuesta del backend (o, para el canal telefónico, la `confianza` ya validada del AI Agent antes de persistir).

**Por qué**: el backend implementado **no expone** el `POST /api/v1/clasificar` que describen la tesis §6.3 y el roadmap. La clasificación está embebida en el create. Forzar dos llamadas exigiría crear un endpoint nuevo en el backend (governance ALTO, fuera de scope de C-04 que es MEDIO y centrado en el workflow) y duplicaría la invocación al pipeline.

**Alternativas consideradas**:
- (B) Crear `POST /api/v1/clasificar` que clasifique sin persistir, para que el workflow decida el ruteo *antes* de crear. Rechazada en C-04: agrega superficie de API y toca el backend (otro change/governance). Se registra como gap para un change posterior si la tesis exige fidelidad literal al diagrama de §6.3.
- (C) Que el nodo `if` evalúe la `confianza` de la respuesta 201 y, si está bajo umbral, haga un PATCH a `/clasificaciones/{id}/validar` para encolar revisión. Viable pero el backend ya marca `requiere_revision` internamente; el ruteo del workflow sería redundante. Se documenta como comportamiento del backend a confirmar en verificación.

**Implicancia documentada**: existe una discrepancia entre el diagrama conceptual de la tesis (2 endpoints) y la implementación real (1 endpoint con clasificación embebida). Se documenta en `docs/n8n-workflow-guide.md` para que el Anexo E de la tesis (C-10) refleje la arquitectura real.

### Decisión 2 — La pseudonimización NO ocurre en el nodo N8N; se asume aplicada aguas arriba o delegada al backend [REVISIÓN — governance MEDIO, toca privacidad]

**Elección**: el nodo de normalización del workflow trata `descripcion` como texto a transmitir; la pseudonimización (C-03, Fernet + doble representación) es responsabilidad del backend / del borde de captura, no de un nodo `code` de N8N. El spec exige que la PII no viaje en claro hacia el subsistema de clasificación, pero el *punto* donde se pseudonimiza se confirma en verificación.

**Por qué**: reimplementar el pseudonimizador en JavaScript dentro de N8N duplicaría lógica de seguridad crítica (governance ALTO) fuera de su módulo Python testeado. Mantener la pseudonimización en el backend conserva una sola fuente de verdad.

**Alternativas**: (B) pseudonimizar en un nodo `code` de N8N — rechazada: duplica lógica de seguridad sin tests del módulo C-03. (C) llamar a un endpoint de pseudonimización dedicado — no existe hoy; sería otro change.

**A confirmar en verificación**: si hoy el backend pseudonimiza *después* de recibir la descripción en claro, la PII viaja N8N→backend sin pseudonimizar. Eso es un gap de privacidad a elevar (no se resuelve silenciosamente en C-04).

### Decisión 3 — El workflow declarativo se testea con pytest sobre el JSON exportado, sin runtime N8N

**Elección**: agregar `Gestion_Incidentes/tests/test_n8n_workflow.py` que carga `Automatizacion_Mesa_de_Ayuda.json` y valida su estructura: nodos presentes, `code` sin `myNewField = 1`, `if` con condiciones no vacías que referencian la confianza y 0.70, nodo `httpRequest` apuntando a `/api/v1/incidentes`, y forma del payload de normalización.

**Por qué**: N8N no ofrece un test harness liviano para CI; levantar una instancia por test es costoso y frágil. El JSON exportado ES el artefacto de entrega, y su estructura es determinística y verificable. Esto encaja en el nivel "unit" de la pirámide (tesis §6.5) y permite ciclos RED→GREEN→TRIANGULATE→REFACTOR: el test RED falla contra el JSON placeholder actual, y GREEN se logra editando el JSON.

**Alternativas**: (B) e2e con N8N real (tesis §6.5 nivel superior) — valioso pero fuera del alcance de Strict TDD del apply; se deja como verificación manual documentada. (C) sin tests, solo revisión visual — rechazada: viola Strict TDD y deja regresiones silenciosas.

### Decisión 4 — Lógica de validación en los nodos `code` con JavaScript inline, espejando el Anexo H

**Elección**: los dos nodos `code` usan JavaScript (runtime nativo de N8N) que replica las reglas del Anexo H: validación de campos del correo (descripción no vacía, ≥10 chars) y validación de 5 pasos de la respuesta de clasificación (JSON válido, campos presentes, categoría en el set exacto, confianza en `[0,1]`; ante fallo → `confianza = 0.0` + revisión humana).

**Por qué**: los nodos `code` de N8N corren JS por defecto; mantenerlo inline evita dependencias externas. La lógica se mantiene fiel al Anexo H §H.3 que ya es el contrato validado del backend, garantizando consistencia de comportamiento entre workflow y módulo Python.

### Decisión 5 — Estructura unificada exacta: `{id, timestamp, canal_origen, descripcion}`

**Elección**: el nodo de normalización emite exactamente esos cuatro campos (timestamp ISO-8601 con milisegundos), según tesis §5.3. `canal_origen ∈ {correo, web, telefonia}`.

**Por qué**: contrato explícito de la tesis; da una superficie estable y testeable para los nodos posteriores y desacopla la forma cruda de cada canal del resto del flujo.

## Risks / Trade-offs

- **[Discrepancia tesis vs implementación: 2 endpoints vs 1]** → Mitigación: Decisión 1 documenta la arquitectura real en la guía; se eleva al usuario para decidir si el Anexo E debe reflejar 1 endpoint (real) o si se quiere el endpoint de clasificación separado (otro change).
- **[PII podría viajar en claro N8N→backend si la pseudonimización es posterior a la recepción]** → Mitigación: Decisión 2 lo marca como punto a confirmar en verificación; si se confirma el gap, se eleva como hallazgo de privacidad (no se cierra en C-04).
- **[Tests de estructura JSON no garantizan ejecución funcional en N8N]** → Mitigación: complementar con una verificación manual documentada (import + corrida de prueba) en `docs/n8n-workflow-guide.md`; los tests cubren el contrato estructural, no la semántica del runtime.
- **[El JSON exportado es frágil a reordenamientos de nodos por la UI de N8N]** → Mitigación: los tests buscan nodos por `type`/`name` y contenido, no por índice de posición.
- **[Canal "web" no tiene trigger todavía (es C-05)]** → Mitigación: el nodo de normalización soporta `canal_origen = "web"` desde ya, pero su trigger se cablea en C-05; los tests de normalización web usan entradas simuladas.

## Migration Plan

1. Escribir los tests de estructura (RED) contra el JSON placeholder actual → fallan.
2. Editar `Automatizacion_Mesa_de_Ayuda.json`: agregar nodo de normalización, reescribir los 2 `code`, configurar los 2 `if`, ajustar el `httpRequest` de persistencia a `/api/v1/incidentes`.
3. Correr los tests hasta GREEN; triangular con casos límite (umbral exacto, categoría inválida, JSON malformado).
4. Verificación manual: importar el JSON en una instancia N8N de pruebas, correr un caso de correo y uno de telefonía, observar el 201 del backend. NO activar en producción.
5. Documentar en `docs/n8n-workflow-guide.md`.
6. **Rollback**: el cambio es sobre un único archivo JSON versionado; revertir = `git checkout` del JSON. Sin migración de datos ni cambios de esquema.

## Open Questions

- ¿El Anexo E / §6.3 de la tesis debe reescribirse para reflejar 1 endpoint (implementación real) o el proyecto requiere fidelidad literal al diagrama de 2 endpoints? (Decisión 1 — elevar al usuario.)
- ¿En qué punto exacto del pipeline se pseudonimiza hoy la descripción? (Decisión 2 — confirmar en verificación; posible hallazgo de privacidad.)
- ¿El ruteo a revisión humana lo decide el workflow (nodo `if`) o ya lo resuelve el backend con `requiere_revision`? Si es el backend, el `if` del workflow es informativo/redundante — confirmar comportamiento esperado para la tesis.
