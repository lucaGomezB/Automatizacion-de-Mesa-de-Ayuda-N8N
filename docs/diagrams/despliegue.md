# Diagrama de Despliegue — Anexo A

Representa los servicios del entorno local definidos en `docker-compose.yml` (raíz del
repositorio, proyecto `mesa_local`). Los servicios se reparten en las redes Docker `edge`,
`data` (interna, sin egreso), `automation` y `host_access`; el frontend es el bundle
compilado por Vite, servido por `nginx:alpine` en el puerto 3000, y N8N se construye
desde la imagen derivada de `docker/n8n/Dockerfile` (N8N 2.11.2 con el parche IMAP de c-182).

> **Nota sobre el formato**: los diagramas se mantienen en Mermaid (texto versionable)
> en lugar de `.drawio` binario, para facilitar diffs en revisiones de código. Mermaid
> renderiza nativamente en GitHub y GitLab. (Decisión D1 del diseño de C-10.)

```mermaid
%%{init: {"flowchart":{"useMaxWidth":false,"nodeSpacing":20,"rankSpacing":40,"padding":6,"wrappingWidth":400}}}%%
graph TD
    subgraph Host["Host (máquina local)"]
        subgraph Docker["Redes Docker: edge, data (interna), automation, host_access"]
            PG["PostgreSQL 15.5-alpine<br/>puerto host: 5433<br/>volumen: postgres_data<br/>DB: mesa_de_ayuda"]
            BE["Backend FastAPI<br/>(sin puerto host)<br/>uvicorn app.main:app<br/>alembic upgrade head<br/>al iniciar"]
            N8N["N8N 2.11.2 derivada<br/>(parche IMAP)<br/>puerto host: 5678<br/>acceso: cuenta owner<br/>(primer arranque)<br/>volumen: n8n_data"]
            FE["Frontend (bundle Vite)<br/>sin puerto host<br/>nginx:alpine :3000"]
            NGX["Nginx alpine<br/>puerto host: 80, 443<br/>TLS 1.2/1.3 termination<br/>HTTP → HTTPS redirect<br/>HSTS header"]
        end

        ENV[".env<br/>(credenciales reales,<br/>gitignorado)"]
        WF["n8n/workflow.json<br/>(workflow N8N,<br/>montado :ro)"]
        PROMPT["docs/prompt_gemini.txt<br/>(prompt Gemini,<br/>montado :ro)"]
        CERTS["openssl/<br/>(certificados TLS,<br/>generados con script)"]
    end

    subgraph External["Servicios Externos"]
        GEMINI["Google Gemini API<br/>(clasificación y<br/>transcripción)"]
        IMAP["Gmail IMAP/SMTP<br/>(correo: trigger<br/>y envio)"]
        TWILIO["Twilio<br/>(voz / callback<br/>de grabación)"]
    end

    PG -- "service_healthy<br/>(pg_isready)" --> BE
    BE -- "service_healthy<br/>(/health)" --> N8N
    BE -- "service_started" --> NGX
    FE -- "service_started" --> NGX

    BE -- "asyncpg<br/>(PostgreSQL protocol)" --> PG
    N8N -- "HTTP POST<br/>/api/v1/incidentes" --> BE
    BE -- "HTTPS: clasificación y<br/>transcripción<br/>(google-genai SDK)" --> GEMINI

    NGX -- "/api/* →<br/>backend:8000" --> BE
    NGX -- "/* →<br/>frontend:3000" --> FE

    IMAP -- "IMAP/SMTP<br/>(correo)" --> N8N
    TWILIO -- "webhook de voz /<br/>callback" --> BE
    BE -- "handoff<br/>pseudonimizado" --> N8N

    ENV -. "env_file" .-> BE
    WF -. "montado :ro<br/>en /data/" .-> N8N
    PROMPT -. "montado :ro<br/>en /app/docs/" .-> BE
    CERTS -. "montado :ro en<br/>/etc/nginx/certs/" .-> NGX
```

## Puertos del host

| Servicio   | Puerto host | Puerto contenedor | Protocolo        |
|------------|------------|-------------------|------------------|
| nginx      | 80         | 80                | HTTP (redirect)  |
| nginx      | 443        | 443               | HTTPS (TLS 1.2/1.3) |
| postgres   | 5433       | 5432              | TCP              |
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
| backend  | `GET http://localhost:8000/health`        | `service_healthy`           |

El healthcheck del backend se ejecuta INTERNAMENTE en el contenedor (via
`http://localhost:8000/health`) y no se ve afectado por el proxy Nginx.
El frontend y Nginx usan `depends_on` con `condition: service_started`
(sin healthcheck propio).
