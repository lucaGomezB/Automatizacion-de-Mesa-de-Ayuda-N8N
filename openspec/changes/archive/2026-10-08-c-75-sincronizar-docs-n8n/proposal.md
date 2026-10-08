## Why

La verdad del workflow N8N se movio y la documentacion no. El change archivado c-72 retiro la rama de clasificacion telefonica con IA (el workflow paso de 38 nodos a 28, y hoy tiene 29 tras c-56) y c-55 cambio el transporte de correo de Outlook a IMAP/SMTP. Varios documentos siguen describiendo nodos eliminados (`AI Agent`, `Google Gemini Chat Model`, `memoryRedisChat`, `Guard de costo`, `Restaurar item telefonia`, etc.) y un transporte/credenciales que ya no existen (Outlook/OAuth2, `twilioTrigger`, memoria Redis del agente, `n8nio/n8n:latest`). El resultado es evidencia operativa incorrecta para la tesis: quien sigue la guia configura recursos inexistentes y audita un flujo que no es el vigente.

## What Changes

- Corregir `docs/n8n-workflow-guide.md`: retirar la seccion de `AI Agent`/`Guard de costo`/`Tope de refinamiento` y las filas de nodos retirados de las tablas del canal telefonia; conservar el conteo `29 nodos (26 operativos + 3 sticky notes)`; alinear transporte IMAP/SMTP, credenciales `imap`/`smtp`, `BACKEND_URL` (origen sin `/api/v1`) y la imagen fijada `n8nio/n8n:2.11.2`; corregir los encabezados C-33/C-40/C-45/C-47.
- Corregir `docs/por_implementar.md`: retirar las secciones de Outlook OAuth2, Twilio Trigger y Redis Chat Memory; corregir "16 nodos" al conteo vigente.
- Corregir `docs/runbook-verificacion-telefonia-c52.md`: reemplazar el flujo `Guard de costo -> AI Agent` por el vigente `Sellar -> Normalizar`; eliminar la afirmacion falsa sobre variables del handoff no definidas en el repo.
- Corregir `docs/diagrams/despliegue.md` y `docs/diagrams/secuencia.md`: quitar Outlook, Redis de memoria del `AI Agent` y `Twilio -> N8N`; citar la version de N8N del compose.
- Corregir Tier 2: `docs/dry-run-harness.md` (Outlook/`Mesa de Ayuda - Outlook`/Twilio Trigger), `docs/operational-guide.md` (§11 n8n `AI Agent`/`Guard de costo`, costos unitarios reales), `docs/medicion-latencia-e2e.md` y `docs/troubleshooting.md` (menciones de Outlook).
- Preservar sin cambios las invariantes que las pruebas de sincronia de docs leen (conteo de nodos, conteo de propiedades, tokens de cost-guard y de bootstrap).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `n8n-workflow`: se agregan requisitos de documentacion (N8N-DOC-004, N8N-DOC-005, N8N-DOC-006) que exigen que la documentacion del workflow refleje el JSON exportado vigente y el transporte IMAP/SMTP, sin describir componentes retirados por c-55/c-72.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `docs/n8n-workflow-guide.md` | Modified | Secciones de IA/cost-guard, tablas de canal telefonia, transporte, credenciales, version y encabezados |
| `docs/por_implementar.md` | Modified | Outlook/Twilio/Redis retirados; conteo de nodos |
| `docs/runbook-verificacion-telefonia-c52.md` | Modified | Flujo telefonico vigente; retiro de afirmacion falsa de variables |
| `docs/diagrams/despliegue.md`, `docs/diagrams/secuencia.md` | Modified | Proveedores y topologia vigentes; version de N8N |
| `docs/dry-run-harness.md` | Modified | Credencial Outlook -> IMAP/SMTP; nota Twilio Trigger |
| `docs/operational-guide.md` | Modified | §11 sin `AI Agent`/`Guard de costo`; costos unitarios reales |
| `docs/medicion-latencia-e2e.md`, `docs/troubleshooting.md` | Modified | Menciones de Outlook corregidas |
| `n8n/workflow.json`, `docker-compose.yml`, codigo de produccion | Out of scope | Sin cambios |

Sin cambios en API, esquema de datos, dependencias de runtime ni infraestructura.

## Governance

Nivel MEDIUM: solo documentacion, pero es evidencia operativa de la tesis. Se propone y se revisa antes de escribir; no hay cambio de runtime, API, esquema ni infraestructura.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Romper una invariante que una prueba de sincronia de docs lee | Low | Las invariantes se declaran como escenarios y se re-ejecutan al cierre |
| Reintroducir una mencion a un nodo retirado al reescribir | Med | Verificacion por busqueda de tokens prohibidos por archivo |
| Desliz de alcance hacia `workflow.json`/compose/codigo | Low | Non-Goal explicito; verificacion con `git status` de un conjunto acotado |
| Reescribir historia ya registrada como correcta | Low | `docs/c-72-unificacion-clasificacion-telefonica.md` y anexos quedan fuera de alcance |

## Rollback Plan

Revertir el commit de documentacion. No hay cambios de runtime, esquema ni infraestructura, por lo que no existe estado que restaurar.

## Success Criteria

- [ ] La guia conserva `Estado: 29 nodos (26 operativos + 3 sticky notes)` y `Verifica 163 propiedades estructurales`, y no contiene `queda sin marcar`, `no** pasa por \`Marcar correo como leido\``, `TwiML` ni `<Say>`.
- [ ] Los documentos corregidos no presentan como vigentes `AI Agent`, `Guard de costo`, `microsoftOutlook*`, `twilioTrigger`, `memoryRedisChat`, `REDIS_URL` de workflow ni `n8nio/n8n:latest`.
- [ ] `cd App/Backend; pytest tests/test_n8n_workflow.py tests/test_c33_cost_guard_wiring.py tests/test_docs_bootstrap_sync.py tests/test_docs_restructure_sync.py tests/test_docs_evaluation_sync.py -q` pasa.
- [ ] `openspec validate c-75-sincronizar-docs-n8n --strict` pasa.
