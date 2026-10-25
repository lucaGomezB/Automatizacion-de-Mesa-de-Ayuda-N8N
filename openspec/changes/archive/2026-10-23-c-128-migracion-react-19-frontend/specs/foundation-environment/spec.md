## MODIFIED Requirements

### Requirement: Configuración OPSX del proyecto
El repositorio SHALL contener `openspec/config.yaml` declarando el stack tecnológico (FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15, N8N, Gemini 2.5 Flash, React 19 + TypeScript + Vite) y las rutas canónicas del proyecto (`App/Backend/`, `App/Frontend/`, `knowledge-base/`, `CHANGES.md`).

#### Scenario: Sub-agente consulta el contexto del proyecto
- **WHEN** un agente ejecuta `openspec status` o lee `openspec/config.yaml`
- **THEN** obtiene el stack y las rutas reales del proyecto sin inferirlas del código