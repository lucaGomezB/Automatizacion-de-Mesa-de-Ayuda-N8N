# C-18: Alineacion Tecnologica de la Tesis

## Por que

La auditoria del 2026-07-02 revelo 27 brechas entre lo que la tesis describe y lo que el codigo realmente implementa. El usuario decidio corregir en la tesis aquellas discrepancias donde la implementacion real es la fuente de verdad, y mantener como "trabajo futuro" o "aspiracional" lo que no se va a implementar ahora.

## Que cambia

### Cambios en la tesis (LaTeX, capitulos 5 y 6)

| Claim actual en tesis | Correccion |
|---|---|
| "casilla IMAP de correo electronico" (§5.2, §6.3) | Microsoft Outlook (Graph API) |
| "google-generativeai~0.8" (§5.4, §6.1) | google-genai >=2.0 (SDK unificado) |
| "psycopg2-binary~2.9" (§5.4) | asyncpg (driver asincronico) |
| "12 nodos principales" (§6.3) | 19 nodos (16 operativos + 3 sticky notes) |
| Pipeline de 5 etapas lineal (§6.3) | Pipeline con AI Agent (LangChain) + Redis para canal telefonico |
| "Uvicorn~0.32" (§6.1) | Uvicorn 0.30.6 |
| "coverage.py~7.6" (§6.7) | pytest-cov 5.0.0 |
| "N8N v1.62" (§6.1) | N8N latest (1.62 no disponible en Docker Hub) |
| GET /api/v1/health (§5.7) | /health y /health/db |
| "pruebas de integracion... PostgreSQL real" (§6.7) | SQLite en memoria para tests unitarios; PostgreSQL en CI futuro (C-19) |
| "5 entidades" (§5.6) | 6 entidades (agregar users para autenticacion) |
| "formulario web... bajo N8N" (§5.2) | Frontend React SPA independiente + admin panel |
| Nombres de campos: id_incidente, id_canal (§5.6) | id, canal_origen_id (convencion SQLAlchemy) |
| "autenticacion... SSO" (§5.2) | JWT Bearer token; SSO como trabajo futuro (§10) |

### Lo que NO se corrige (se mantiene como aspiracional o trabajo futuro)

| Claim | Razon |
|---|---|
| TLS 1.3 (§5.1, §11) | Aspiracional. HTTP plano en dev. Documentar como requisito productivo. |
| HMAC-SHA-256 (§5, §11) | No implementado. Mover a trabajo futuro. |
| pgcrypto (§11.4) | Se usa Fernet a nivel app. Aclarar la diferencia. |
| Retencion de datos (§11.2) | No implementado. Mover a trabajo futuro. |
| POST /api/v1/clasificar (§5.7) | No existe. Clasificacion embebida en POST /incidentes. Reflejar arquitectura real. |
| Script TwiML (§6.4) | Ya creado en C-16. Actualizar referencia en tesis. |

### Cambios en la KB

- Actualizar `09_decisiones_y_supuestos.md`: documentar decisiones DD-08 (asyncpg), DD-10 (clasificacion embebida), DD-12 (JWT sobre SSO)
- Actualizar `08_arquitectura_propuesta.md`: corregir versiones, protocolos, entidades

## Gobernanza

MEDIUM — cambios documentales en LaTeX, sin impacto en codigo.

## Dependencias

Ninguna. Cambio independiente.
