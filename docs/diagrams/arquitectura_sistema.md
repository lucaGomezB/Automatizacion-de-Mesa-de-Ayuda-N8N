# Diagrama de Arquitectura del Sistema — Cinco Capas y Tres Canales

Representa las cinco capas de la arquitectura (Tabla `tab:capas`) y los tres canales
de entrada del sistema entregado (release `v1.2.5`). Reemplaza al diagrama de flujo de
un solo canal que se usaba antes como Figura `fig:arquitectura` (c-159).

Procedencia: Tabla `tab:capas` de la tesis, `n8n/workflow.json` (disparador IMAP,
webhook `incidente-web` y webhook `telefonia-handoff`), `docker-compose.yml` y
`App/Backend/app/routes/incidentes.py`. Los rótulos no llevan versiones de bibliotecas:
viven en la Tabla `tab:capas` y en la tabla de configuración evaluada frente a entregada.

```mermaid
flowchart LR
    subgraph C1["1. Canales de entrada"]
        direction TB
        COR["Correo<br/>IMAP / SMTP"]
        WEB["Formulario web"]
        TEL["Telefonía Twilio<br/>(transcripción y pseudonimización<br/>de la llamada en el backend)"]
    end

    subgraph C2["2. Orquestación - N8N"]
        direction TB
        TRI["Disparador IMAP<br/>webhook incidente-web<br/>webhook telefonia-handoff"]
        NOR["Normalización<br/>y validación de entrada"]
        ALT["Alta del incidente<br/>y notificaciones"]
    end

    subgraph C3["3. Procesamiento - FastAPI"]
        direction TB
        API["API REST<br/>(consumida también<br/>por el frontend React)"]
        SEU["Pseudonimización"]
        CLA["Clasificador híbrido<br/>determinístico, Gemini, reserva"]
    end

    subgraph C4["4. Inferencia"]
        GEM["Gemini<br/>solo si el filtro no resuelve"]
    end

    subgraph C5["5. Persistencia"]
        PG[("PostgreSQL<br/>incidente, clasificacion_log,<br/>directorio")]
    end

    C1 --> C2
    C2 --> C3
    C3 --> C4
    C3 --> C5
```
