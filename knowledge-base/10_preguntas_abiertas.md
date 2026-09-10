# Preguntas Abiertas

## Inconsistencias detectadas

### IN-01 — Endpoint de clasificacion: ¿separado o integrado?
**La tesis dice** (§5.7, Tabla 5; §6.3): N8N invoca `POST /api/v1/clasificar` (descripcion -> categoria + confianza) y luego `POST /api/v1/incidentes` para persistir — dos llamadas.
**El codigo dice**: `POST /api/v1/incidentes` clasifica y persiste en una sola operacion; `POST /clasificar` no existe.
**Estado actual (2026-07-02)**: Decidido — la clasificacion permanece embebida en `POST /api/v1/incidentes`. El workflow N8N usa una sola llamada HTTP. La tesis sera corregida en futura revision para reflejar la arquitectura real. NO se agrega endpoint `/clasificar` separado.

### IN-02 — Autenticacion declarada pero no implementada — RESUELTO (C-15)

**La tesis dice** (seccion 5.7): tokens portadores firmados validados contra clave compartida con N8N; 401 ante fallo.
**Estado actual**: Implementado en C-15 (jwt-auth-backend-frontend). JWT Bearer token con python-jose + middleware FastAPI. Todos los endpoints protegidos requieren autenticacion. Frontend con AuthContext y ruta `/login`. Governance: ALTO. Completado y archivado (2026-07-02).

### IN-03 — Driver de base de datos
**La tesis dice** (§5.4): psycopg2-binary 2.9. **El código dice**: asyncpg + SQLAlchemy async.
**Impacto**: ninguno funcional (la elección del código es superior para FastAPI); solo desfase documental.
**Resolución propuesta**: anotar la divergencia en el Anexo B/C al cerrar C-10 (ya documentada en DD-08).

### IN-04 — Cifrado en reposo y HMAC — RESUELTO (2026-09-10)

**La tesis corregida dice** (v8 LaTeX, C-18, seccion 11.4): Fernet a nivel de aplicacion (AES-128-CBC con HMAC-SHA-256 integrado) para campos sensibles.
**El codigo dice**: `App/Backend/app/utils/encryption.py` implementa un `EncryptedText` TypeDecorator de SQLAlchemy que usa Fernet (biblioteca `cryptography`). La columna `incidente.descripcion_original` esta cifrada en reposo con este mecanismo. Fernet incorpora HMAC-SHA-256 en su modo de operacion -- todo ciphertext es autenticado; si se altera, `decrypt()` lanza `InvalidToken`.
**Estado actual**: Resuelto. C-03 eligio Fernet sobre pgcrypto explicitamente (Decision 4 del revisor). C-18 corrigio el LaTeX de la tesis: `pgcrypto -> Fernet, eliminar HMAC-SHA-256 independiente`. La implementacion satisface los requisitos de confidencialidad e integridad de la seccion 11.4. No se requiere accion adicional.

### IN-05 — Politica de retencion — RESUELTO (2026-09-10)

**La tesis corregida dice** (v8 LaTeX, C-18, seccion 11.2): "conservacion indefinida de los incidentes, justificada por el valor estadistico de los datos historicos para el analisis de tendencias y la identificacion de problemas recurrentes. Los incidentes en estado cerrado se preservan como registro auditable permanente: pueden consultarse pero no editarse ni eliminarse desde la interfaz de usuario."
**El codigo dice**: El bloqueo de escritura sobre incidentes cerrados esta implementado (C-23: `PATCH /api/v1/incidentes/{id}` devuelve 409 si el estado es terminal). No se requiere purga automatica.
**Estado actual**: Resuelto. C-18 redefinio la politica de retencion a conservacion indefinida. La pseudonimizacion y el cifrado Fernet garantizan la proteccion de datos en periodos prolongados. La version v7 de `tesis_para_agente.md` (que aun dice "90 dias / 1 ano") quedo desactualizada; la fuente de verdad es el LaTeX corregido en `v8 (IA)/paper/sections/11-aspectos-legales.tex`.

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

## [DISCOVERY] Campos inferidos con confianza — sin pendientes

Los seis campos de discovery (problem, system_type, domain, scale, stack, needs_infra) se infirieron con confianza alta desde la tesis. No quedan incertidumbres de discovery.
