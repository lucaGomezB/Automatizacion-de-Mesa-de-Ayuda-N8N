# Funcionalidades

Organizadas por épica. Estado: ✅ implementado · 🔶 parcial · ❌ pendiente (referencia al change de `CHANGES.md`).

## Épica 1: Recepción multicanal

### US-001 — Reportar incidente por formulario web ✅
**Como** usuario interno **quiero** completar un formulario web **para** registrar un incidente sin llamar ni escribir un correo.
- CA: el formulario valida campos requeridos; al enviar muestra número de ticket y sector asignado.
- Implementación: Frontend React (`ReportarIncidente`) → `POST /api/v1/incidentes`.

### US-002 — Reportar incidente por correo ❌ (C-05)
**Como** usuario interno **quiero** enviar un correo a la casilla institucional **para** que el ticket se genere solo.
- CA: trigger IMAP en N8N detecta el correo; si faltan datos requeridos, respuesta automática los solicita.
- Estado: nodos N8N en placeholder.

### US-003 — Reportar incidente por teléfono ❌ (C-05)
**Como** usuario interno **quiero** llamar a un número y describir mi problema **para** registrar el incidente por voz.
- CA: TwiML da bienvenida en español rioplatense; graba hasta 45 s (corte con `#`); transcribe; webhook a N8N; latencia cuelgue→confirmación 12-15 s.

## Épica 2: Clasificación automática

### US-004 — Clasificación híbrida ✅
**Como** organización **quiero** que cada incidente se derive automáticamente al sector correcto **para** eliminar la derivación manual.
- CA: etapa determinística ≥ 0,90 decide sola; si no, Gemini; fallback ante fallo. Reglas RN-CL-01…07.
- Implementación: `app/classifiers/` (deterministic, gemini_classifier, hybrid) + keywords (24 Sistemas / 16 Operaciones / 20 Soporte Técnico).

### US-005 — Pseudonimización pre-Gemini ❌ (C-03, governance ALTO)
**Como** responsable de datos **quiero** que ningún dato personal salga hacia Gemini **para** cumplir la Ley 25.326.
- CA: regex reemplazan PERSONA/EMAIL/TELEFONO/HOST antes de la transmisión; tests unitarios por patrón.

## Épica 3: Registro y persistencia

### US-006 — CRUD de incidentes ✅
**Como** operador **quiero** crear, listar (con filtros y paginación), consultar y actualizar tickets **para** gestionar el ciclo de vida.
- Implementación: `routes/incidentes.py`, `IncidenteService`, repositorios.

### US-007 — Notificación a N8N post-clasificación ❌ (C-02)
**Como** orquestador **quiero** recibir un webhook al clasificarse un incidente **para** continuar el flujo (notificaciones al usuario).
- CA: `notify_n8n()` (ya existe en `utils/n8n_webhook.py`) se invoca fire-and-forget desde `IncidenteService._apply_classification()`; fallos no bloquean la respuesta HTTP.

## Épica 4: Revisión humana

### US-008 — Cola de revisión pendiente ✅
**Como** operador **quiero** ver los casos de baja confianza en orden FIFO **para** validarlos sin que nada quede olvidado.
- Implementación: `GET /clasificaciones/revision-pendiente` + tabla en frontend.

### US-009 — Validación / corrección humana ✅
**Como** sector responsable **quiero** confirmar o corregir la categoría predicha **para** cerrar el ciclo y alimentar el corpus.
- Implementación: `PATCH /clasificaciones/{log_id}/validar` + modal "Validación Humana".

## Épica 5: Orquestación N8N

### US-010 — Workflow funcional end-to-end ❌ (C-04)
**Como** organización **quiero** el flujo de 12 nodos operativo **para** que los 3 canales converjan en un único pipeline.
- CA: normalización unificada; IF por confianza ≥ 0,70; invocación de la API; notificaciones paralelas post-registro; logs de auditoría 30 días.
- Estado: `Automatizacion_Mesa_de_Ayuda.json` tiene lógica placeholder y condiciones IF vacías.

## Épica 6: Evaluación experimental

### US-011 — Framework de evaluación ❌ (C-08)
**Como** equipo de investigación **quiero** ejecutar el clasificador sobre el corpus de 200 casos y calcular métricas **para** validar la hipótesis.
- CA: exactitud global, matriz de confusión, precision/recall/F1 por clase, F1 macro, IC Wilson, Wilcoxon; reporte md + notebook con visualizaciones. Ver [11_evaluacion_experimental.md](11_evaluacion_experimental.md).

## Épica 7: Calidad e infraestructura

### US-012 — Tests de integración backend ❌ (C-06) · cobertura objetivo > 85 %
### US-013 — Testing frontend (Vitest + Testing Library) ❌ (C-07) · cobertura objetivo > 70 %
### US-014 — CI/CD GitHub Actions ❌ (C-09)
### US-015 — Anexos y documentación operativa ❌ (C-10)
