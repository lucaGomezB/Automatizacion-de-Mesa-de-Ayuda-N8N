# Diagrama de Componentes — Módulo Python (Backend FastAPI)

Refleja la organización en capas del módulo `Gestion_Incidentes/app/`, siguiendo
el principio de separación de responsabilidades: cada capa solo conoce a la capa
inmediatamente inferior.

```mermaid
graph TD
    subgraph Routes["Capa de Rutas (app/routes/)"]
        RI["incidentes.py\nPOST / GET / PATCH /api/v1/incidentes"]
        RC["clasificaciones.py\nGET /revision-pendiente\nGET /incidente/{id}\nPATCH /{id}/validar"]
        RH["health.py\nGET /health\nGET /health/db"]
    end

    subgraph Services["Capa de Servicios (app/services/)"]
        SI["IncidenteService\ncreate_and_classify()\nlist_incidentes()\nget_by_id()\nupdate_incidente()"]
        SC["ClasificacionService\nlist_pending_review()\nlist_by_incidente()\nvalidate()"]
        SN["notify_n8n()\n(fire-and-forget)"]
    end

    subgraph Classifiers["Clasificador Híbrido (app/classifiers/)"]
        CH["HybridClassifier\nclassify()"]
        CD["DeterministicClassifier\n(reglas, umbral ≥ 0.90)"]
        CG["GeminiClassifier\n(LLM, umbral ≥ 0.70)"]
    end

    subgraph Repositories["Capa de Repositorios (app/repositories/)"]
        RIR["IncidenteRepository\ncreate() / get_by_id()\nlist_filtered() / update()"]
        RCR["ClasificacionRepository\ncreate_log() / get_pending()\nget_by_incidente() / update_log()"]
        RSR["SectorRepository\nget_by_name()"]
        RER["EstadoRepository\nget_by_name()"]
    end

    subgraph Models["Modelos ORM (app/models/)"]
        MI["Incidente\n(descripcion_original cifrada,\ndescripcion_pseudonimizada,\nindices compuestos)"]
        MCL["ClasificacionLog\n(doble FK a sector:\npredicho / validado)"]
        MS["Sector / Estado / CanalOrigen\n(tablas de catálogo)"]
    end

    subgraph Utils["Utilidades transversales (app/utils/ / app/core/)"]
        UP["Pseudonimizador\n(reemplaza PII con etiquetas)"]
        UE["EncryptedText\n(Fernet, cifrado at-rest)"]
        DB["Database / get_db_session\n(SQLAlchemy async + PostgreSQL)"]
        ER["Error Handlers\n(HTTP 404, 409, 422, 500)"]
        LOG["Logging estructurado\n(structlog)"]
    end

    subgraph Config["Configuración (app/config/)"]
        SET["Settings\n(pydantic-settings)\nDATABASE_URL\nGEMINI_API_KEY\nENCRYPTION_KEY"]
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

    SC --> RCR

    CH --> CD
    CH --> CG
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
