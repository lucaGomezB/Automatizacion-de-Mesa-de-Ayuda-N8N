# Diagrama de Despliegue — Anexo A

Representa los servicios del entorno local definidos en `docker-compose.yml` (raíz del
repositorio). Todos los servicios corren dentro de la red Docker `mesa_local_default`.

> **Nota sobre el formato**: los diagramas se mantienen en Mermaid (texto versionable)
> en lugar de `.drawio` binario, para facilitar diffs en revisiones de código. Mermaid
> renderiza nativamente en GitHub y GitLab. (Decisión D1 del diseño de C-10.)

```mermaid
graph TD
    subgraph Host["Host (maquina local)"]
        subgraph Docker["Red Docker: mesa_local_default"]
            PG["PostgreSQL 15.5-alpine\npuerto host: 5433\nvolumen: postgres_data\nDB: mesa_de_ayuda"]
            RD["Redis 7.2-alpine\npuerto host: 6379"]
            BE["Backend FastAPI\n(sin puerto host)\nuvicorn app.main:app\nalembic upgrade head al iniciar"]
            N8N["N8N latest\npuerto host: 5678\nBasic Auth: admin/admin\nvolumen: n8n_data"]
            FE["Frontend React 18 + Vite\n(sin puerto host)\nVite dev server :3000"]
            NGX["Nginx alpine\npuerto host: 80, 443\nTLS 1.3 termination\nHTTP → HTTPS redirect\nHSTS header"]
        end

        ENV[".env\n(credenciales reales,\ngitignorado)"]
        WF["n8n/workflow.json\n(workflow N8N, montado :ro)"]
        PROMPT["docs/prompt_gemini.txt\n(prompt Gemini, montado :ro)"]
        CERTS["openssl/\n(certificados TLS,\ngenerados con script)"]
    end

    subgraph External["Servicios Externos"]
        GEMINI["Google Gemini API\n(clasificacion LLM)"]
        OUTLOOK["Microsoft Outlook\n(trigger de correo)"]
        TWILIO["Twilio\n(webhook de llamadas)"]
    end

    %% Dependencias de salud declaradas en el compose
    PG -- "service_healthy (pg_isready)" --> BE
    RD -- "service_healthy (redis-cli ping)" --> BE
    BE -- "service_healthy (/health)" --> N8N
    BE -- "service_started" --> NGX
    FE -- "service_started" --> NGX

    %% Comunicacion entre servicios
    BE -- "asyncpg (PostgreSQL protocol)" --> PG
    N8N -- "Redis (memoria AI Agent)" --> RD
    N8N -- "HTTP POST /api/v1/incidentes" --> BE
    BE -- "HTTPS (google-genai SDK)" --> GEMINI

    %% Nginx proxy rutas
    NGX -- "/api/* → backend:8000" --> BE
    NGX -- "/* → frontend:3000" --> FE

    %% Canales de entrada externos
    OUTLOOK -- "trigger (email)" --> N8N
    TWILIO -- "webhook (transcripcion)" --> N8N

    %% Volumenes y archivos
    ENV -. "env_file" .-> BE
    WF -. "montado :ro en /data/" .-> N8N
    PROMPT -. "montado :ro en /app/docs/" .-> BE
    CERTS -. "montado :ro en /etc/nginx/certs/" .-> NGX
```

## Puertos del host

| Servicio   | Puerto host | Puerto contenedor | Protocolo        |
|------------|------------|-------------------|------------------|
| nginx      | 80         | 80                | HTTP (redirect)  |
| nginx      | 443        | 443               | HTTPS (TLS 1.3)  |
| postgres   | 5433       | 5432              | TCP              |
| redis      | 6379       | 6379              | TCP              |
| n8n        | 5678       | 5678              | HTTP (directo)   |
| backend    | —          | 8000              | HTTP (interno)   |
| frontend   | —          | 3000              | HTTP (interno)   |

> El backend (puerto 8000) y el frontend (puerto 3000) NO se publican en el host.
> Todo el trafico HTTP/HTTPS externo pasa a traves del proxy Nginx. N8N mantiene
> su puerto directo (5678) por limitaciones con path-prefix en el proxy.

## Healthchecks

| Servicio | Comando                                   | Condicion para dependientes |
|----------|-------------------------------------------|-----------------------------|
| postgres | `pg_isready -U mesa -d mesa_de_ayuda`     | `service_healthy`           |
| redis    | `redis-cli ping`                          | `service_healthy`           |
| backend  | `GET http://localhost:8000/health`        | `service_healthy`           |

El healthcheck del backend se ejecuta INTERNAMENTE en el contenedor (via
`http://localhost:8000/health`) y no se ve afectado por el proxy Nginx.
El frontend y Nginx usan `depends_on` con `condition: service_started`
(sin healthcheck propio).
