# Arquitectura Propuesta

## Patrones aplicados

| Patrón | Dónde | Por qué |
|---|---|---|
| Arquitectura por capas | routes → services → repositories → models | Cohesión alta, acoplamiento bajo; cada capa testeable |
| Repository | `app/repositories/` (BaseRepository genérico + concretos) | Aísla SQLAlchemy de la lógica de negocio |
| Unit of Work | `get_db_session()` (commit/rollback centralizados) | Transacción atómica por request |
| Factory | `create_app()` en `main.py` | Instancias aisladas para testing |
| Inyección de dependencias | FastAPI `Depends` (SessionDep, ServiceDep) | Reemplazo de implementaciones en tests |
| Chain of Responsibility | `HybridClassifier`: deterministic → gemini → fallback | Optimiza exactitud/latencia/costo |
| Orquestación (vs coreografía) | N8N centraliza el control de flujo | Trazabilidad auditiva prioritaria (Hohpe & Woolf) |
| Settings cacheadas | `get_settings()` con `lru_cache` | Una sola lectura de `.env` |

## Estructura de directorios (real)

```
Automatizacion-de-Mesa-de-Ayuda-N8N/
├── App/Backend/            # Backend FastAPI
│   ├── app/
│   │   ├── main.py                # create_app + middleware CORS/errores
│   │   ├── config/settings.py     # pydantic-settings
│   │   ├── core/                  # database, exceptions, error_handlers, logging
│   │   ├── models/                # ORM: incidente, catalog, clasificacion_log
│   │   ├── schemas/               # Pydantic: incidente, clasificacion, catalog
│   │   ├── classifiers/           # keywords, deterministic, gemini, hybrid
│   │   ├── repositories/          # base genérico + concretos
│   │   ├── services/              # incidente_service, clasificacion_service
│   │   ├── routes/                # incidentes, clasificaciones, health
│   │   └── utils/                 # n8n_webhook, pagination, (futuro: pseudonymizer)
│   ├── alembic/                   # migraciones + seed de catálogos
│   ├── tests/                     # pytest (conftest listo para integración)
│   └── docker-compose.yml / Dockerfile
├── App/Frontend/                      # React 18 + TS + Vite
│   └── src/{components,hooks,services,types,utils,lib}
├── n8n/workflow.json   # Workflow N8N exportado
├── docs/                          # Tesis md, prompt y parámetros Gemini
├── knowledge-base/                # Esta KB
├── openspec/                      # Artefactos OPSX (changes/specs)
└── CHANGES.md                     # Roadmap de 10 changes
```

## Seguridad

| Aspecto | Tesis (objetivo) | Estado actual |
|---|---|---|---|
| Cifrado en transito | TLS 1.3 entre todos los componentes | HTTP local en dev; TLS pendiente para despliegue |
| Autenticacion API | Tokens portadores firmados, clave compartida con N8N | ✅ JWT Bearer token (C-15) |
| Integridad | HMAC-SHA-256 en identificadores; validacion Pydantic | Pydantic ✅; HMAC integrado en Fernet ✅ |
| Cifrado en reposo | pgcrypto para campos sensibles | ✅ Fernet a nivel aplicación (EncryptedText) |
| Secrets | Solo variables de entorno (12-Factor) | ✅ `.env` + pydantic-settings (.env fuera de git) |
| Auditoria | Registro de actor + timestamp + delta por modificacion | Parcial: `clasificacion_log` ✅; audit general ❌ |
| Pseudonimizacion pre-LLM | Regex PERSONA/EMAIL/TELEFONO/HOST + tests | ✅ implementado (C-03). 4 categorias PII. Double representation. |
| CORS | Restringir origenes en produccion | Permisivo (`*`) en dev; configurable via `CORS_ALLOW_ORIGINS` |

## Variables de entorno (settings.py)

| Variable | Descripción | Ejemplo | Sensible |
|---|---|---|---|
| DATABASE_URL | URL asyncpg de PostgreSQL | `postgresql+asyncpg://user:pass@host:5432/db` | Y |
| GEMINI_API_KEY | Clave Google AI | — | Y |
| GEMINI_MODEL / TEMPERATURE / TOP_P / MAX_OUTPUT_TOKENS / CANDIDATE_COUNT / TIMEOUT_SECONDS | Parámetros del modelo | `gemini-2.5-flash` · 0.3 · 0.9 · 100 · 1 · 10 | N |
| DETERMINISTIC_CONFIDENCE_THRESHOLD | Umbral etapa 1 | 0.90 | N |
| HUMAN_REVIEW_THRESHOLD | Umbral revisión humana | 0.70 | N |
| N8N_WEBHOOK_URL / N8N_WEBHOOK_SECRET | Webhook post-clasificación | vacío ⇒ se omite | Y |
| DB_POOL_SIZE / DB_MAX_OVERFLOW / DB_ECHO | Pool SQLAlchemy | 10 / 20 / false | N |
| DEBUG / ENVIRONMENT | Habilita /docs; etiqueta de entorno | false / production | N |
| LOG_LEVEL / LOG_FORMAT | structlog | INFO / json | N |
| CORS_ALLOW_ORIGINS | Orígenes permitidos | `["*"]` dev; dominio real en prod | N |

## Despliegue

- Dev/preprod: Docker Compose (api + postgres + n8n).
- Producción (tesis §6.1): Kubernetes 1.30 — sin manifiestos en el repo aún.
- Imágenes: `python:3.12-slim`, `postgres:15.5-alpine`, N8N oficial 1.62.
- Healthchecks: `/health` (liveness) y `/health/db` (readiness) ya expuestos.
