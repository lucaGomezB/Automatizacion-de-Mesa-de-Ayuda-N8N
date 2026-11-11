# Diagrama de Componentes — Módulo Python (Backend FastAPI)

Refleja la organización en capas del módulo `App/Backend/app/`, siguiendo
el principio de separación de responsabilidades: cada capa solo conoce a la capa
inmediatamente inferior.

> **Figura dividida en dos partes** (observación N-11 del tribunal). La parte A muestra las
> capas de rutas, servicios y clasificadores; la parte B, las capas de repositorios, modelos,
> utilidades y configuración. Los nodos punteados de cada parte señalan la capa vecina, que se
> detalla en la otra parte.

### Parte A — Rutas, servicios y clasificadores

```mermaid
%%{init: {"fontFamily":"Arial, Helvetica, sans-serif","themeVariables":{"fontFamily":"Arial, Helvetica, sans-serif","fontSize":"16px"},"flowchart":{"useMaxWidth":false,"nodeSpacing":20,"rankSpacing":35,"padding":6,"wrappingWidth":400}}}%%
graph TD
    subgraph Routes["Capa de Rutas (app/routes/)"]
        RI["incidentes.py<br/>POST / GET / PATCH<br/>/api/v1/incidentes"]
        RC["clasificaciones.py<br/>GET /revision-pendiente<br/>GET /incidente/{id}<br/>PATCH /{id}/validar"]
        RH["health.py<br/>GET /health<br/>GET /health/db"]
    end

    subgraph Services["Capa de Servicios (app/services/)"]
        SI["IncidenteService<br/>create_and_classify()<br/>list_incidentes()<br/>get_by_id()<br/>update_incidente()<br/>revisión = clasificador OR<br/>reportante no identificado"]
        SCR["ContactResolutionService<br/>resuelve el reportante<br/>en el directorio<br/>(desde el 13-10-2026;<br/>posterior a la campaña 2026-10)"]
        SC["ClasificacionService<br/>list_pending_review()<br/>list_by_incidente()<br/>validate()"]
        SN["notify_n8n()<br/>(fire-and-forget)"]
    end

    subgraph Classifiers["Clasificador Híbrido (app/classifiers/)"]
        CH["HybridClassifier<br/>classify()"]
        CD["DeterministicClassifier<br/>(reglas: cortocircuito con<br/>señal dominante y<br/>score_correctitud ≥ 0,5166;<br/>no deriva a revisión<br/>por su confianza)"]
        CG["GeminiClassifier<br/>(LLM: revisión si<br/>confianza &lt; 0,70)"]
        CR["Etapa de reserva<br/>(timeout, indisponibilidad,<br/>salida inválida o guarda de costo:<br/>confianza 0,0 y revisión siempre)"]
    end

    subgraph Resto["Capas inferiores (detalle en la parte B)"]
        RP["Capa de Repositorios<br/>(app/repositories/)"]
        DBX["Database / get_db_session"]
        SETX["Settings (app/config/)"]
        UPX["Pseudonimizador<br/>(app/utils/)"]
    end

    RI --> SI
    RC --> SC
    RH --> DBX

    SI --> RP
    SI --> CH
    SI --> SN
    SI --> SCR
    SI --> UPX

    SC --> RP

    CH --> CD
    CH --> CG
    CH --> CR
    CG --> SETX

    SCR ~~~ CH
    SN ~~~ CH
    SC ~~~ CH
```

### Parte B — Repositorios, modelos, utilidades y configuración

```mermaid
%%{init: {"fontFamily":"Arial, Helvetica, sans-serif","themeVariables":{"fontFamily":"Arial, Helvetica, sans-serif","fontSize":"16px"},"flowchart":{"useMaxWidth":false,"nodeSpacing":20,"rankSpacing":35,"padding":6,"wrappingWidth":400}}}%%
graph TD
    subgraph Superiores["Capas superiores (ver parte A)"]
        RHX["health.py<br/>(app/routes/)"]
        SIX["IncidenteService<br/>(app/services/)"]
        SCX["ClasificacionService<br/>(app/services/)"]
        CGX["GeminiClassifier<br/>(app/classifiers/)"]
    end

    subgraph Repositories["Capa de Repositorios (app/repositories/)"]
        RIR["IncidenteRepository<br/>create() / get_by_id()<br/>list_filtered() / update()"]
        RCR["ClasificacionRepository<br/>create_log() / get_pending()<br/>get_by_incidente()<br/>update_log()"]
        RSR["SectorRepository<br/>get_by_name()"]
        RER["EstadoRepository<br/>get_by_name()"]
    end

    subgraph Models["Modelos ORM (app/models/)"]
        MI["Incidente<br/>(descripcion_original cifrada,<br/>descripcion_pseudonimizada,<br/>indices compuestos)"]
        MCL["ClasificacionLog<br/>(doble FK a sector:<br/>predicho / validado)"]
        MS["Sector / Estado / CanalOrigen<br/>(tablas de catálogo)"]
    end

    subgraph Utils["Utilidades transversales (app/utils/ / app/core/)"]
        UP["Pseudonimizador<br/>(reemplaza PII<br/>con etiquetas)"]
        UE["EncryptedText<br/>(Fernet, cifrado<br/>at-rest)"]
        DB["Database / get_db_session<br/>(SQLAlchemy async<br/>+ PostgreSQL)"]
        ER["Error Handlers<br/>(HTTP 404, 409,<br/>422, 500)"]
        LOG["Logging estructurado<br/>(structlog)"]
    end

    subgraph Config["Configuración (app/config/)"]
        SET["Settings<br/>(pydantic-settings)<br/>DATABASE_URL<br/>GEMINI_API_KEY<br/>ENCRYPTION_KEY"]
    end

    RHX --> DB
    SIX --> RIR
    SIX --> RCR
    SIX --> RSR
    SIX --> RER
    SIX --> UP
    SCX --> RCR
    CGX --> SET

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

    UP ~~~ ER
    UE ~~~ LOG
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
