## Context

Ver `proposal.md` — Why. La verdad operativa vigente la fijan `n8n/workflow.json` (29 nodos: 26 operativos + 3 sticky notes), `docker-compose.yml` (imagen `n8nio/n8n:2.11.2`, `BACKEND_URL=http://backend:8000`, `OPERATOR_EMAIL`, `SMTP_FROM_EMAIL`) y `App/Backend/app/config/settings.py` (costos unitarios). El change es de documentación: no toca runtime ni infraestructura.

Restricción dura: un conjunto de pruebas automatizadas lee estos documentos y define criterios de aceptación. Las invariantes están en `App/Backend/tests/test_n8n_workflow.py` (conteo de nodos, conteo de propiedades estructurales, ausencia de la excepción de rama de revisión, ausencia de TwiML), `test_c33_cost_guard_wiring.py` (tokens del webhook dedicado), y `test_docs_bootstrap_sync.py` / `test_docs_restructure_sync.py` / `test_docs_evaluation_sync.py` (guía operativa y README). Estas pruebas SHALL quedar en verde y no se modifican.

## Goals / Non-Goals

**Goals:**
- Alinear toda la documentación en alcance con el JSON del workflow y el transporte IMAP/SMTP vigentes.
- Preservar las invariantes que leen las pruebas de sincronía de docs.

**Non-Goals:**
- No modificar `n8n/workflow.json`, `docker-compose.yml`, `App/Backend/.env.example` ni código de producción.
- No agregar ni modificar pruebas automatizadas.
- No tocar `openspec/changes/c-56-notificaciones-por-rol/design.md`, `docs/Comandos_para_iniciar_proyecto.txt`, `docs/anexo_h_prompt_gemini.md`, `docs/c-72-unificacion-clasificacion-telefonica.md`, `docs/seguridad/*` ni `docs/cumplimiento/*`.

## Decisions

1. **Una sola capability (`n8n-workflow`) para los requisitos de documentación.** Todo el drift en alcance es sobre la verdad del workflow N8N y su transporte: la rama IA retirada, el cambio a IMAP/SMTP, la topología de los diagramas y las menciones de Outlook/Twilio/Redis. Reutilizar `n8n-workflow` mantiene el alcance cohesionado, evita fragmentar requisitos en capabilities ajenas y coincide con que las pruebas que los verifican viven en `test_n8n_workflow.py`. Alternativa descartada: crear una capability nueva `n8n-docs-sync` o repartir requisitos entre `project-documentation`, `dry-run-harness` y `e2e-timing-instrumentation`; ambas añaden superficie sin mejorar la verificabilidad.
2. **Requirement IDs N8N-DOC-004/005/006** siguen la convención `N8N-<TEMA>-<NNN>` ya usada por la capability (N8N-EMAIL-001, N8N-AUDIT-001, etc.).
3. **Sin pruebas nuevas.** Los escenarios de la delta se anclan a las pruebas existentes y a búsquedas de tokens prohibidos. Extender los guards para cubrir la prosa corregida es un cambio de código fuera de alcance; queda como pregunta abierta.
4. **Corrección por búsqueda de tokens.** Cada tarea de corrección se verifica por ausencia de los tokens retirados (`AI Agent`, `Guard de costo`, `microsoftOutlook*`, `twilioTrigger`, `memoryRedisChat`, `n8nio/n8n:latest`, `TWILIO_*`/`REDIS_URL` de workflow) y por presencia de los vigentes, además de la suite de regresión.

## Risks / Trade-offs

- [Romper una invariante leída por las pruebas] -> Se declaran como escenarios y se re-ejecutan en la verificación final; los documentos se editan sin tocar las líneas estructuradas (conteo, cobertura, tokens de bootstrap).
- [Reintroducir un nodo retirado al reescribir una sección] -> Verificación por búsqueda de tokens prohibidos archivo por archivo.
- [Desliz de alcance hacia `workflow.json`/compose/código] -> Non-Goal explícito; `git status --porcelain` acotado antes del cierre.
- [Alcance amplio en un solo change] -> Se ordena por Tier 1/Tier 2 y por archivo, con una verificación única al final.

## Migration Plan

1. Capturar baseline ejecutando las pruebas de sincronía de docs y la suite estructural.
2. Corregir Tier 1 (`n8n-workflow-guide.md`, `por_implementar.md`, `runbook-verificacion-telefonia-c52.md`, diagramas).
3. Corregir Tier 2 (`dry-run-harness.md`, `operational-guide.md`, `medicion-latencia-e2e.md`, `troubleshooting.md`).
4. Ejecutar la verificación de la suite de docs y `openspec validate --strict`.
5. Rollback: revertir el commit de documentación; no hay estado de runtime que restaurar.

## Open Questions

- ¿Conviene, en un change posterior, extender `test_n8n_workflow.py` o los `test_docs_*_sync.py` con aserciones de prosa para que el drift corregido quede protegido automáticamente? No cambia este change ni sus tareas.
