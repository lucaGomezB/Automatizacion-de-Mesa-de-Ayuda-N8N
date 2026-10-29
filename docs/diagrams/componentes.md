# Diagrama de Componentes — Módulo Python (Backend FastAPI)

Refleja la organización en capas del módulo `App/Backend/app/`, siguiendo
el principio de separación de responsabilidades: cada capa solo conoce a la capa
inmediatamente inferior.

```mermaid
graph TD
    subgraph Routes["Capa de Rutas (app/routes/)"]
        RI["incidentes.py<br/>POST / GET / PATCH /api/v1/incidentes"]
        RC["clasificaciones.py<br/>GET /revision-pendiente<br/>GET /incidente/{id}<br/>PATCH /{id}/validar"]
        RH["health.py<br/>GET /health<br/>GET /health/db"]
    end

    subgraph Services["Capa de Servicios (app/services/)"]
        SI["IncidenteService<br/>create_and_classify()<br/>list_incidentes()<br/>get_by_id()<br/>update_incidente()<br/>revisión = clasificador OR<br/>reportante no identificado"]
        SCR["ContactResolutionService<br/>resuelve el reportante en el directorio<br/>(c-82, desde el 13-10-2026;<br/>posterior a la campaña de medición)"]
        SC["ClasificacionService<br/>list_pending_review()<br/>list_by_incidente()<br/>validate()"]
        SN["notify_n8n()<br/>(fire-and-forget)"]
    end

    subgraph Classifiers["Clasificador Híbrido (app/classifiers/)"]
        CH["HybridClassifier<br/>classify()"]
        CD["DeterministicClassifier<br/>(reglas: cortocircuito con señal dominante<br/>y score_correctitud ≥ 0,5166;<br/>no deriva a revisión por su confianza)"]
        CG["GeminiClassifier<br/>(LLM: revisión si confianza &lt; 0,70)"]
        CR["Etapa de reserva<br/>(timeout, indisponibilidad, salida inválida<br/>o guarda de costo:<br/>confianza 0,0 y revisión siempre)"]
    end

    subgraph Repositories["Capa de Repositorios (app/repositories/)"]
        RIR["IncidenteRepository<br/>create() / get_by_id()<br/>list_filtered() / update()"]
        RCR["ClasificacionRepository<br/>create_log() / get_pending()<br/>get_by_incidente() / update_log()"]
        RSR["SectorRepository<br/>get_by_name()"]
        RER["EstadoRepository<br/>get_by_name()"]
    end

    subgraph Models["Modelos ORM (app/models/)"]
        MI["Incidente<br/>(descripcion_original cifrada,<br/>descripcion_pseudonimizada,<br/>indices compuestos)"]
        MCL["ClasificacionLog<br/>(doble FK a sector:<br/>predicho / validado)"]
        MS["Sector / Estado / CanalOrigen<br/>(tablas de catálogo)"]
    end

    subgraph Utils["Utilidades transversales (app/utils/ / app/core/)"]
        UP["Pseudonimizador<br/>(reemplaza PII con etiquetas)"]
        UE["EncryptedText<br/>(Fernet, cifrado at-rest)"]
        DB["Database / get_db_session<br/>(SQLAlchemy async + PostgreSQL)"]
        ER["Error Handlers<br/>(HTTP 404, 409, 422, 500)"]
        LOG["Logging estructurado<br/>(structlog)"]
    end

    subgraph Config["Configuración (app/config/)"]
        SET["Settings<br/>(pydantic-settings)<br/>DATABASE_URL<br/>GEMINI_API_KEY<br/>ENCRYPTION_KEY"]
    end

    %% Dependencias entre capas
    RI --> SI
    RC --> SC
    RH --> DB

    SI --> RIR
    SI --> RCR
    SI --> RSR
    SI --> RER
    SI --> CH
    SI --> UP
    SI --> SN
    SI --> SCR

    SC --> RCR

    CH --> CD
    CH --> CG
    CH --> CR
    CG --> SET

    RIR --> MI
    RCR --> MCL
    RSR --> MS
    RER --> MS

    MI --> UE
    MI --> DB
    MCL --> DB
    MS --> DB

    SET --> DB
    SET --> UE
```

## Descripción de capas

| Capa | Directorio | Responsabilidad |
|------|-----------|-----------------|
| **Rutas** | `app/routes/` | Deserializar HTTP, delegar al servicio, serializar respuesta |
| **Servicios** | `app/services/` | Orquestar casos de uso (pseudonimizar, clasificar, persistir) |
| **Clasificadores** | `app/classifiers/` | Pipeline híbrido: determinístico → Gemini → fallback |
| **Repositorios** | `app/repositories/` | Acceso a datos; las queries de SQLAlchemy viven aquí |
| **Modelos ORM** | `app/models/` | Definición de tablas y relaciones (ver Anexo C) |
| **Utilidades** | `app/utils/` `app/core/` | Pseudonimizador, cifrado Fernet, logging, error handlers |
| **Configuración** | `app/config/` | `Settings` con pydantic-settings; sin defaults, valores en `.env` |
