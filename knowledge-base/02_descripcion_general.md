# Descripción General

## Stack tecnológico

| Capa | Tecnología | Versión | Notas |
|---|---|---|---|
| Orquestación | N8N | 1.62 | Docker autoalojado; webhooks + triggers |
| API / Procesamiento | FastAPI + Uvicorn | 0.115 / 0.32 | Python 3.12; patrón factory `create_app()` |
| ORM | SQLAlchemy | 2.0 | API declarativa async (`Mapped`/`mapped_column`) |
| Driver DB | asyncpg | — | La tesis menciona psycopg2; el código usa asyncpg (ver [09](09_decisiones_y_supuestos.md) DD-08) |
| Base de datos | PostgreSQL | 15.5 | Imagen `postgres:15.5-alpine`, volumen persistente |
| Migraciones | Alembic | — | `alembic/versions/001_seed_catalogs.py` siembra catálogos |
| Inferencia LLM | Gemini 2.5 Flash | `google-genai` ≥ 1.0 | temp 0,3 · top_p 0,9 · max_tokens 100 · timeout 10 s; reemplaza al deprecado `google-generativeai` |
| Telefonía | Twilio Programmable Voice | — | TwiML + transcripción automática nativa |
| Frontend | React 18 + TypeScript + Vite | — | React Query + Axios + shadcn/ui |
| Logging | structlog | — | JSON (prod) / consola (dev) |
| Config | pydantic-settings | — | `.env`, caché LRU |
| Testing backend | pytest | 8.3 | Objetivo cobertura ≥ 80 % (tesis reporta 87 %) |
| Contenedores | Docker + Docker Compose | — | K8s 1.30 declarado para producción en la tesis |

## Arquitectura general (5 capas)

```
┌──────────────────────────────────────────────────────────────┐
│ 1. CANALES DE ENTRADA                                        │
│    IMAP correo │ Formulario web (React) │ Twilio (voz→texto) │
└───────────────┬──────────────────────────────────────────────┘
                ▼ webhooks / triggers
┌──────────────────────────────────────────────────────────────┐
│ 2. ORQUESTACIÓN — N8N v1.62 (Docker autoalojado)             │
│    Normalización → invocación API → ruteo por confianza      │
└───────────────┬──────────────────────────────────────────────┘
                ▼ HTTP/REST (TLS 1.3)
┌──────────────────────────────────────────────────────────────┐
│ 3. PROCESAMIENTO — FastAPI (App/Backend/app/)         │
│    routes → services → repositories → models                 │
│    Clasificador híbrido: deterministic → gemini → fallback   │
└──────┬────────────────────────────────────────┬──────────────┘
       ▼ solo si reglas < 0,90                  ▼ asyncpg
┌─────────────────────────┐      ┌────────────────────────────┐
│ 4. INFERENCIA           │      │ 5. PERSISTENCIA            │
│    Gemini 2.5 Flash     │      │    PostgreSQL 15.5         │
│    (pseudonimizado)     │      │    5 tablas + auditoría    │
└─────────────────────────┘      └────────────────────────────┘
```

Principios: cohesión alta / acoplamiento bajo; cada capa reemplazable de forma independiente; comunicación REST sin estado.

## Integraciones externas

| Servicio | Propósito | Tipo |
|---|---|---|
| Google Gemini API | Clasificación semántica (etapa 2) | SDK `google-genai` |
| Twilio | Recepción telefónica + transcripción | Webhook → N8N |
| Servidor IMAP (Outlook) | Trigger de correos entrantes | Polling IMAP en N8N |
| N8N | Orquestación; recibe webhook post-clasificación | Webhook saliente (`notify_n8n`) |

## API REST (implementada en `App/Backend/app/routes/`)

| Método | Ruta | Éxito | Función |
|---|---|---|---|
| POST | `/api/v1/incidentes` | 201 | Crea ticket **y lo clasifica automáticamente** en la misma llamada |
| GET | `/api/v1/incidentes` | 200 | Listado con filtros y paginación |
| GET | `/api/v1/incidentes/{id}` | 200 | Detalle de un ticket |
| PATCH | `/api/v1/incidentes/{id}` | 200 | Actualización parcial |
| GET | `/api/v1/clasificaciones/revision-pendiente` | 200 | Cola FIFO de revisión humana |
| GET | `/api/v1/clasificaciones/incidente/{id}` | 200 | Historial de clasificaciones |
| PATCH | `/api/v1/clasificaciones/{log_id}/validar` | 200 | Registrar validación humana |
| GET | `/health` · `/health/db` (también bajo `/api/v1`) | 200 | Liveness / readiness |

> ⚠️ La tesis (§5.7, Tabla 5) define `POST /api/v1/clasificar` como endpoint separado que N8N invoca antes de persistir. El código actual clasifica dentro de `POST /incidentes`. Ver [10_preguntas_abiertas.md](10_preguntas_abiertas.md) IN-01.

Documentación interactiva: `/docs` (Swagger UI) solo con `DEBUG=true`.
