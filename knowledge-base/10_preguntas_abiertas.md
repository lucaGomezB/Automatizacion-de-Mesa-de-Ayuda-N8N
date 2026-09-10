# Preguntas Abiertas

## Inconsistencias detectadas

### IN-01 — Endpoint de clasificacion: ¿separado o integrado?
**La tesis dice** (§5.7, Tabla 5; §6.3): N8N invoca `POST /api/v1/clasificar` (descripcion -> categoria + confianza) y luego `POST /api/v1/incidentes` para persistir — dos llamadas.
**El codigo dice**: `POST /api/v1/incidentes` clasifica y persiste en una sola operacion; `POST /clasificar` no existe.
**Estado actual (2026-07-02)**: Decidido — la clasificacion permanece embebida en `POST /api/v1/incidentes`. El workflow N8N usa una sola llamada HTTP. La tesis sera corregida en futura revision para reflejar la arquitectura real. NO se agrega endpoint `/clasificar` separado.

### IN-02 — Autenticacion declarada pero no implementada
**La tesis dice** (§5.7): tokens portadores firmados validados contra clave compartida con N8N; 401 ante fallo.
**El codigo dice**: ningun endpoint exige autenticacion (auditado 2026-07-02).
**Impacto**: brecha de seguridad y de fidelidad a la tesis; cualquier actor en la red puede crear/leer tickets.
**Estado actual**: C-15 (jwt-auth-backend-frontend) en curso. Implementa JWT Bearer token con Python-Jose + middleware FastAPI. Governance: ALTO.

### IN-03 — Driver de base de datos
**La tesis dice** (§5.4): psycopg2-binary 2.9. **El código dice**: asyncpg + SQLAlchemy async.
**Impacto**: ninguno funcional (la elección del código es superior para FastAPI); solo desfase documental.
**Resolución propuesta**: anotar la divergencia en el Anexo B/C al cerrar C-10 (ya documentada en DD-08).

### IN-04 — Cifrado en reposo y HMAC ausentes
**La tesis dice** (§11.4): pgcrypto para campos sensibles; identificadores firmados HMAC-SHA-256.
**El código dice**: no implementado.
**Impacto**: compromiso de cumplimiento §11.4 si se despliega productivamente sin esto.
**Resolución propuesta**: evaluar si entra en C-10 o en un change de seguridad dedicado junto con IN-02.

### IN-05 — Política de retención no implementada
**La tesis dice** (§11.2): 90 días operativos / 1 año resueltos / 30 días logs N8N.
**El código dice**: sin job de purga ni anonimización.
**Impacto**: incumplimiento de RN-PR-04 en operación prolongada.
**Resolución propuesta**: tarea programada (cron N8N o script) — candidato a línea futura o C-10.

### IN-06 — Workflow N8N del repo vs. descripcion de la tesis
**La tesis dice** (§6.3): 12 nodos con normalizacion, IF por confianza, dos llamadas HTTP y notificaciones paralelas.
**El repo dice**: `n8n/workflow.json` con 16 nodos operativos reales + 3 sticky notes. Trigger email es Microsoft Outlook (NO IMAP). Clasificacion embebida en backend (una sola llamada HTTP). Canal telefonico con AI Agent (LangChain) + Redis.
**Estado actual (2026-07-02)**: workflow funcional con 16 nodos. Divergencias documentadas: (a) Outlook vs IMAP, (b) 16 nodos vs 12, (c) clasificacion embebida vs endpoint separado, (d) AI Agent + Redis para canal telefonico.

## Preguntas abiertas (priorizadas)

| Prioridad | Pregunta | Bloquea | Decisor |
|---|---|---|---|
| Alta | ¿Donde esta el CSV del corpus de 200 casos? → Resuelto: se construye simulado en C-17 | C-17 (nuevo) | Equipo tecnico |
| Alta | ¿Se agrega `POST /api/v1/clasificar` (IN-01)? → Resuelto: NO. Clasificacion embebida en POST /incidentes | — | Decidido (2026-07-02) |
| Alta | ¿Credenciales reales de Outlook y Twilio disponibles para pruebas? | C-05 | Organizacion |
| Alta | ¿Auth JWT Bearer token se implementa? → Si, en C-15 (jwt-auth-backend-frontend) | C-15 (nuevo) | Equipo + director |
| Media | ¿La instancia N8N de pruebas corre en el mismo compose? URL del webhook | C-02 | Equipo tecnico |
| Baja | ¿K8s 1.30 es alcance real o aspiracional (SU-05)? | C-10 | Equipo + director |
| Baja | ¿Se implementa retencion/purga automatica (IN-05)? | Operacion prolongada | Responsable de datos |

## [DISCOVERY] Campos inferidos con confianza — sin pendientes

Los seis campos de discovery (problem, system_type, domain, scale, stack, needs_infra) se infirieron con confianza alta desde la tesis. No quedan incertidumbres de discovery.
