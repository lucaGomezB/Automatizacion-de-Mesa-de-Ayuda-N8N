# Preguntas Abiertas

## Inconsistencias detectadas

### IN-01 — Endpoint de clasificación: ¿separado o integrado?
**La tesis dice** (§5.7, Tabla 5; §6.3): N8N invoca `POST /api/v1/clasificar` (descripción → categoría + confianza) y luego `POST /api/v1/incidentes` para persistir — dos llamadas.
**El código dice**: `POST /api/v1/incidentes` clasifica y persiste en una sola operación; `POST /clasificar` no existe.
**Impacto**: C-04 (workflow N8N) no puede implementarse como lo describe la tesis sin agregar el endpoint, o bien el workflow debe simplificarse a una sola llamada.
**Resolución propuesta**: agregar `POST /api/v1/clasificar` como endpoint sin efectos (clasifica sin persistir) — alinea código y tesis, da a N8N el control del IF por confianza, y mantiene `POST /incidentes` como vía integrada para el frontend.

### IN-02 — Autenticación declarada pero no implementada
**La tesis dice** (§5.7): tokens portadores firmados validados contra clave compartida con N8N; 401 ante fallo.
**El código dice**: ningún endpoint exige autenticación.
**Impacto**: brecha de seguridad y de fidelidad a la tesis; cualquier actor en la red puede crear/leer tickets.
**Resolución propuesta**: middleware de API key/Bearer simple (clave compartida en env var) — alcance acotado, alto valor. Candidato a change nuevo (no está en CHANGES.md). Governance: ALTO.

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

### IN-06 — Workflow N8N del repo vs. descripción de la tesis
**La tesis dice** (§6.3): 12 nodos con normalización, IF por confianza, dos llamadas HTTP y notificaciones paralelas.
**El repo dice**: `Automatizacion_Mesa_de_Ayuda.json` con lógica placeholder (`myNewField = 1`), IF vacíos, y un agente LangChain + Redis para llamadas que la tesis no describe en ese nivel de detalle.
**Impacto**: C-04/C-05 deben reconciliar ambas versiones.
**Resolución propuesta**: tratar la tesis §6.3 como especificación normativa y el JSON como esqueleto a reescribir.

## Preguntas abiertas (priorizadas)

| Prioridad | Pregunta | Bloquea | Decisor |
|---|---|---|---|
| Alta | ¿Dónde está el CSV del corpus de 200 casos? (no versionado) | C-08 | Autores de la tesis |
| Alta | ¿Se agrega `POST /api/v1/clasificar` (IN-01)? | C-04 | Equipo técnico |
| Alta | ¿Credenciales reales de IMAP/Outlook y Twilio disponibles para pruebas? | C-05 | Organización |
| Media | ¿Auth de API entra al roadmap como change nuevo (IN-02)? | Despliegue productivo | Equipo + director |
| Media | ¿La instancia N8N de pruebas corre en el mismo compose? URL del webhook | C-02 | Equipo técnico |
| Baja | ¿K8s 1.30 es alcance real o aspiracional (SU-05)? | C-10 | Equipo + director |
| Baja | ¿Se implementa retención/purga automática (IN-05)? | Operación prolongada | Responsable de datos |

## [DISCOVERY] Campos inferidos con confianza — sin pendientes

Los seis campos de discovery (problem, system_type, domain, scale, stack, needs_infra) se infirieron con confianza alta desde la tesis. No quedan incertidumbres de discovery.
