## Context

Ver `proposal.md` — Why. El workflow ya está implementado y commiteado (`5efce4b`); este change es de formalización, no de construcción. La spec `openspec/specs/n8n-workflow/spec.md` quedó desactualizada respecto del workflow de 29 nodos y hay que alinearla al archivar.

Restricciones relevantes:

- El backend `IncidenteService.create_and_classify` clasifica dentro de la creación y devuelve el incidente con `requiere_revision_humana`; la respuesta `IncidenteRead` NO incluye `confianza`.
- El umbral de revisión humana es `0.70` (inclusivo para no revisar): `requiere_revision_humana = confianza < 0.70`.
- La suite estructural `App/Backend/tests/test_n8n_workflow.py` ya verifica el comportamiento nuevo y corre sin runtime N8N.

## Goals / Non-Goals

**Goals:**

- Que la spec archivada de `n8n-workflow` describa la compuerta de dos capas realmente implementada.
- Dejar trazable la decisión de evaluar el flag del backend en lugar de la confianza en el tramo post-POST.
- Documentar la notificación al operador designado y la resolución de URLs por entorno.

**Non-Goals:**

- No modificar `n8n/workflow.json`, `docker-compose.yml`, `.env.example`, la guía ni los tests: ya están implementados.
- No rediseñar el pipeline de clasificación del backend.
- No tocar el tope de refinamiento del agente ni el ciclo de vida del correo (cubiertos por C-33).

## Decisions

### Decisión 1: Separar validación de entrada (pre-POST) de gate de revisión (post-POST)

El nodo `if` pre-POST se renombra a `Entrada valida` y pasa a ser validación de entrada con `confianza >= 0.70 OR revision_forzada == true`. El gate de revisión real se mueve a un `if` post-POST que evalúa `requiere_revision_humana` del response.

Alternativa considerada: mantener un único `if` pre-POST sobre `confianza`. Se descarta porque el backend es quien clasifica dentro del alta y devuelve el flag; evaluar la confianza antes del POST obligaría al workflow a duplicar la lógica de umbral y a asumir un campo que el response no expone. La condición con `revision_forzada` conserva la persistencia de los incidentes derivados por el tope de refinamiento del agente.

### Decisión 2: El gate post-POST lee `requiere_revision_humana`, no `confianza`

La respuesta de `POST /api/v1/incidentes/` (`IncidenteRead`) incluye `sector`, `sectores_adicionales` y `requiere_revision_humana`, pero no `confianza`. La compuerta se apoya en el booleano que el backend ya calculó (`confianza < 0.70`).

Alternativa considerada: que el backend agregue `confianza` al response para que el workflow evalúe el umbral. Se descarta porque duplica la decisión de umbral en dos subsistemas y el flag ya es el contrato estable.

### Decisión 3: Notificación al operador en la rama verdadera, antes de auditoría

La rama verdadera del gate post-POST encadena `Notificar operador designado` (`microsoftOutlook` a `$env.OPERATOR_EMAIL`) y luego `Registro de auditoria`. Para el canal correo, la misma rama reutiliza `Es correo?` para marcar el mensaje como leído. La rama falsa sigue por `Rutear por canal de origen` y auditoría.

Alternativa considerada: notificar desde el backend. Se descarta para mantener la notificación dentro de la orquestación N8N y no acoplar el backend al canal de correo saliente.

### Decisión 4: URLs del backend por variable de entorno

Los nodos HTTP resuelven el host con `$env.BACKEND_URL`, expuesta por el servicio N8N en `docker-compose.yml`, y `OPERATOR_EMAIL` se expone de la misma forma. El JSON exportado no contiene el host hardcodeado.

Alternativa considerada: hardcodear `http://backend:8000`. Se descarta porque ata el workflow exportado a un único entorno.

## Risks / Trade-offs

- [La variable `$env.BACKEND_URL` no está disponible si N8N bloquea el acceso a entorno en los nodos] → La variable se define en el servicio N8N del compose; la suite estructural falla si algún nodo vuelve a hardcodear el host.
- [Divergencia residual: el requerimiento "Persistencia del incidente vía backend FastAPI" menciona `confianza` en el response, que no existe] → Fuera del alcance de este change; se deja registrado como observación para un follow-up.
- [La notificación al operador usa un placeholder `operador@example.com` por defecto] → `OPERATOR_EMAIL` es configurable por entorno; el placeholder no es una dirección real.

## Migration Plan

No aplica: no hay migración de datos ni cambio de contrato. El comportamiento ya está desplegado en el workflow exportado. El único efecto de este change es la sincronización de la spec al archivar.

## Open Questions

Ninguna que cambie la spec, el enfoque o el desglose de tareas.
