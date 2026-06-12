# Diagrama de Despliegue — Anexo A

Representa los servicios del entorno local definidos en `docker-compose.yml` (raíz del
repositorio). Todos los servicios corren dentro de la red Docker `mesa_local_default`.

> **Nota sobre el formato**: los diagramas se mantienen en Mermaid (texto versionable)
> en lugar de `.drawio` binario, para facilitar diffs en revisiones de código. Mermaid
> renderiza nativamente en GitHub y GitLab. (Decisión D1 del diseño de C-10.)

```mermaid
graph TD
    subgraph Host["Host (máquina local)"]
        subgraph Docker["Red Docker: mesa_local_default"]
            PG["PostgreSQL 15.5-alpine\npuerto host: 5433\nvolumen: postgres_data\nDB: mesa_de_ayuda"]
            RD["Redis 7.2-alpine\npuerto host: 6379"]
            BE["Backend FastAPI\npuerto host: 8000\nuvicorn app.main:app\nalembic upgrade head al iniciar"]
            N8N["N8N latest\npuerto host: 5678\nBasic Auth: admin/admin\nvolumen: n8n_data"]
        end

        ENV[".env\n(credenciales reales,\ngitignorado)"]
        WF["Automatizacion_Mesa_de_Ayuda.json\n(workflow N8N, montado :ro)"]
        PROMPT["docs/prompt_gemini.txt\n(prompt Gemini, montado :ro)"]
    end

    subgraph External["Servicios Externos"]
        GEMINI["Google Gemini API\n(clasificación LLM)"]
        OUTLOOK["Microsoft Outlook\n(trigger de correo)"]
        TWILIO["Twilio\n(webhook de llamadas)"]
    end

    subgraph FrontendOpt["Frontend (opcional, fuera del compose)"]
        FE["React 18 + Vite\npuerto: 3000\nnpm run dev"]
    end

    %% Dependencias de salud declaradas en el compose
    PG -- "service_healthy (pg_isready)" --> BE
    RD -- "service_healthy (redis-cli ping)" --> BE
    BE -- "service_healthy (/health)" --> N8N

    %% Comunicación entre servicios
    BE -- "asyncpg (PostgreSQL protocol)" --> PG
    N8N -- "Redis (memoria AI Agent)" --> RD
    N8N -- "HTTP POST /api/v1/incidentes" --> BE
    BE -- "HTTPS (google-genai SDK)" --> GEMINI

    %% Canales de entrada externos
    OUTLOOK -- "trigger (email)" --> N8N
    TWILIO -- "webhook (transcripción)" --> N8N

    %% Volúmenes y archivos
    ENV -. "env_file" .-> BE
    WF -. "montado :ro en /data/" .-> N8N
    PROMPT -. "montado :ro en /app/docs/" .-> BE

    %% Frontend (opcional)
    FE -- "HTTP /api/v1/*" --> BE
```

## Puertos del host

| Servicio   | Puerto host | Puerto contenedor | Protocolo |
|------------|------------|-------------------|-----------|
| postgres   | 5433       | 5432              | TCP       |
| redis      | 6379       | 6379              | TCP       |
| backend    | 8000       | 8000              | HTTP      |
| n8n        | 5678       | 5678              | HTTP      |
| frontend   | 3000       | 3000              | HTTP (dev)|

## Healthchecks

| Servicio | Comando                                   | Condición para dependientes |
|----------|-------------------------------------------|-----------------------------|
| postgres | `pg_isready -U mesa -d mesa_de_ayuda`     | `service_healthy`           |
| redis    | `redis-cli ping`                          | `service_healthy`           |
| backend  | `GET http://localhost:8000/health`        | `service_healthy`           |

El Frontend (React + Vite, puerto 3000) no está declarado en el compose y se levanta
de forma opcional con `npm run dev` en el directorio `Frontend/`. Ver
[`docs/operational-guide.md`](../operational-guide.md) para el procedimiento completo.
