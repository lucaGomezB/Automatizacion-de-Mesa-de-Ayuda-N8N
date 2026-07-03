# Funcionalidades

Organizadas por épica. Estado: ✅ implementado · 🔶 parcial · ❌ pendiente (referencia al change de `CHANGES.md`).

> Ultima actualizacion: 2026-07-02. Auditado contra codigo real. C-02 a C-10 archivados.

## Épica 1: Recepción multicanal

### US-001 — Reportar incidente por formulario web ✅
**Como** usuario interno **quiero** completar un formulario web **para** registrar un incidente sin llamar ni escribir un correo.
- CA: el formulario valida campos requeridos; al enviar muestra número de ticket y sector asignado.
- Implementación: Frontend React (`ReportarIncidente`) → `POST /api/v1/incidentes`.

### US-002 — Reportar incidente por correo 🔶 (C-05)
**Como** usuario interno **quiero** enviar un correo a la casilla institucional **para** que el ticket se genere solo.
- CA: trigger de Microsoft Outlook en N8N detecta el correo (NO IMAP — divergencia con tesis); nodo Code valida campos requeridos; IF datos incompletos → respuesta automatica solicitando lo faltante.
- Estado: nodos N8N implementados (16 nodos operativos). Canal funcional con credenciales Outlook. Tesis dice IMAP — codigo usa Microsoft Graph API.

### US-003 — Reportar incidente por teléfono 🔶 (C-05)
**Como** usuario interno **quiero** llamar a un número y describir mi problema **para** registrar el incidente por voz.
- CA: trigger Twilio en N8N (Voice Insights call-summary) + AI Agent (LangChain) con Redis para parsear transcripcion. Pipeline de validacion con nodo Code dedicado.
- Estado: trigger Twilio + AI Agent + Redis implementados en N8N. **Falta script TwiML** (C-16). Sin credenciales Twilio reales no se puede probar end-to-end.

## Épica 2: Clasificación automática

### US-004 — Clasificación híbrida ✅
**Como** organización **quiero** que cada incidente se derive automáticamente al sector correcto **para** eliminar la derivación manual.
- CA: etapa determinística ≥ 0,90 decide sola; si no, Gemini; fallback ante fallo. Reglas RN-CL-01…07.
- Implementación: `app/classifiers/` (deterministic, gemini_classifier, hybrid) + keywords (24 Sistemas / 16 Operaciones / 20 Soporte Técnico).

### US-005 — Pseudonimización pre-Gemini ✅ (C-03)
**Como** responsable de datos **quiero** que ningún dato personal salga hacia Gemini **para** cumplir la Ley 25.326.
- CA: 4 categorias PII detectadas y reemplazadas (EMAIL, TELEFONO, HOST, PERSONA) en orden fijo. Double representation: original encriptado via Fernet + pseudonimizado en claro. Clasificador solo recibe texto pseudonimizado.
- Implementacion: `app/utils/pseudonymizer.py` (220 lineas, funcion pura) + `app/utils/encryption.py` (EncryptedText TypeDecorator). Tests unitarios por categoria. Ley 25.326 compliant.

## Épica 3: Registro y persistencia

### US-006 — CRUD de incidentes ✅
**Como** operador **quiero** crear, listar (con filtros y paginación), consultar y actualizar tickets **para** gestionar el ciclo de vida.
- Implementación: `routes/incidentes.py`, `IncidenteService`, repositorios.

### US-007 — Notificación a N8N post-clasificación ✅ (C-02)
**Como** orquestador **quiero** recibir un webhook al clasificarse un incidente **para** continuar el flujo (notificaciones al usuario).
- CA: `notify_n8n()` fire-and-forget via `asyncio.create_task()`. Timeout 5s. Header `X-N8N-Secret` opcional. Falla silenciosa (logged warning, no propaga). Si `N8N_WEBHOOK_URL` vacio → no-op.
- Implementacion: `app/utils/n8n_webhook.py` (91 lineas). Invocado desde `IncidenteService._apply_classification()`. Mockeado globalmente en conftest para tests.

## Épica 4: Revisión humana

### US-008 — Cola de revisión pendiente ✅
**Como** operador **quiero** ver los casos de baja confianza en orden FIFO **para** validarlos sin que nada quede olvidado.
- Implementación: `GET /clasificaciones/revision-pendiente` + tabla en frontend.

### US-009 — Validación / corrección humana ✅
**Como** sector responsable **quiero** confirmar o corregir la categoría predicha **para** cerrar el ciclo y alimentar el corpus.
- Implementación: `PATCH /clasificaciones/{log_id}/validar` + modal "Validación Humana".

## Épica 5: Orquestación N8N

### US-010 — Workflow funcional end-to-end 🔶 (C-04)
**Como** organización **quiero** el flujo de 16 nodos operativo **para** que los 3 canales converjan en un único pipeline.
- CA: normalizacion unificada (UUID v4, timestamp, canal, descripcion); IF por confianza ≥ 0.70; invocacion HTTP a API; notificaciones paralelas post-registro; logs de auditoria 30 dias. Canal telefonico con AI Agent (LangChain) + Redis.
- Estado: `n8n/workflow.json` con 16 nodos operativos reales + 3 sticky notes. Trigger email es Microsoft Outlook (NO IMAP). Clasificacion embebida en backend (no existe nodo HTTP a `/api/v1/clasificar` — divergencia con tesis §6.3). Funcional con credenciales configuradas.

## Épica 6: Evaluación experimental

### US-011 — Framework de evaluación ✅ (C-08)
**Como** equipo de investigación **quiero** ejecutar el clasificador sobre el corpus de 200 casos y calcular métricas **para** validar la hipótesis.
- CA: exactitud global, matriz de confusión 3x3, precision/recall/F1 por clase, F1 macro, IC Wilson 95%, Wilcoxon pareado con rank-biserial effect size. Reporte md + Jupyter notebook con visualizaciones.
- Estado: `evaluation/` con 20 archivos (corpus.py, metrics.py, stats.py, run_evaluation.py, tests/, analysis.ipynb). FakeClassifier para CI. **Corpus real de 200 casos no versionado** (C-17). Ver [11_evaluacion_experimental.md](11_evaluacion_experimental.md).

## Épica 7: Calidad e infraestructura

### US-012 — Tests backend ✅ (C-06)
**Como** equipo **quiero** tests unitarios y de integracion con cobertura > 85% **para** garantizar calidad.
- Estado: 23 archivos de test en `App/Backend/tests/`. Cobertura de routes, services, repositories. SQLite in-memory via aiosqlite. Conftest con seed_catalogs, make_client_with_classifier. Tests para classifiers (deterministico, gemini, hybrid), pseudonymization, encryption, schemas, API endpoints, N8N workflow, OpenAPI sync.

### US-013 — Testing frontend ✅ (C-07)
**Como** equipo **quiero** tests de componentes y hooks con cobertura > 70% **para** garantizar calidad del frontend.
- Estado: 12 archivos de test en `App/Frontend/src/`. Vitest 2.1 + Testing Library 16 + happy-dom. Tests para services (api, incidentes, clasificaciones), hooks (useReportarIncidente, useIncidentes, useRevisionPendiente), pages (IncidenteForm, SuccessCard, TicketsTable, RevisionHumanaTable), shared components (SectorBadge, ConfianzaIndicator).

### US-014 — CI/CD GitHub Actions ✅ (C-09)
**Como** equipo **quiero** integracion continua en cada PR **para** no romper nada al mergear.
- Estado: `.github/workflows/ci.yml` (107 lineas). 2 jobs paralelos: backend-tests (ruff + pytest con cobertura + OpenAPI sync + evaluation tests) y frontend-tests (ESLint + Vitest con cobertura). Sin secretos requeridos (tests 100% offline).

### US-015 — Anexos y documentacion operativa 🔶 (C-10)
**Como** organizacion adoptante **quiero** docs de despliegue, operacion y anexos tecnicos **para** operar el sistema sin depender del equipo original.
- Estado: `docs/` con operational-guide.md, n8n-workflow-guide.md, troubleshooting.md, pseudonymization.md, parameters_gemini.md, diagramas UML, OpenAPI spec. `knowledge-base/` con 11 archivos canonicos. README con quick start. Anexos de tesis (C, D, E, F) implementados como artifacts.
