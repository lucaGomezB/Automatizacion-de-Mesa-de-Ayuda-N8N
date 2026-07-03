## MODIFIED Requirements

### Requirement: Configuracion OPSX del proyecto

El repositorio SHALL contener `openspec/config.yaml` declarando el stack tecnologico (FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15, N8N, Gemini 2.5 Flash, React 18 + TypeScript + Vite) y las rutas canonicas del proyecto (`App/Backend/`, `App/Frontend/`, `knowledge-base/`, `CHANGES.md`).

#### Scenario: Sub-agente consulta el contexto del proyecto
- **WHEN** un agente ejecuta `openspec status` o lee `openspec/config.yaml`
- **THEN** obtiene el stack y las rutas reales del proyecto sin inferirlas del codigo

#### Scenario: Arranque desde App/Backend/
- **WHEN** la aplicacion se inicia con cwd en `App/Backend/`
- **THEN** el prompt se carga correctamente y NO se emite el warning `prompt_file_not_found`
