# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a UTN thesis project (2026) that automates help desk ticket classification using **N8N** (workflow automation platform) and **Google Gemini 2.5 Flash**. Incoming incidents from email (Microsoft Outlook) and phone calls (Twilio) are automatically classified into one of three categories in Spanish:

- **Sistemas**: Infrastructure, networks, servers, databases, cybersecurity
- **Operaciones**: Shared processes, service management, planning, business continuity  
- **Soporte Técnico**: User equipment, peripherals, client software, remote assistance

## Key Files

| File | Purpose |
|------|---------|
| `Automatizacion_Mesa_de_Ayuda.json` | The N8N workflow definition — the core of the project |
| `docs/prompt_gemini.txt` | The exact prompt sent to Gemini for classification |
| `docs/parameters_gemini.md` | Gemini API parameter configuration and rationale |
| `ANEXO_H_Prompt_Gemini_Especificacion.md` | Full specification for the Gemini prompt design |

## Architecture

The N8N workflow has two parallel processing channels:

### Channel 1: Email Incidents
```
Outlook Email Trigger
  → JavaScript Validation Node (verify required fields)
  → IF Node: data complete?
    ├─ YES → HTTP POST to MTM-SRU (create incident)
    └─ NO  → Send email requesting missing data
```

### Channel 2: Phone/Call Incidents
```
Twilio Webhook (call transcription)
  → LangChain AI Agent (parse call with custom prompt)
  → Redis Memory (store parsed JSON session data)
  → Python Validation Node (verify extracted fields)
  → IF Node: can incident be created?
    ├─ YES → HTTP POST to MTM-SRU (create incident)
    └─ NO  → Loop back to AI Agent for refinement
```

### AI Classification (Gemini 2.5 Flash)
- **Response format**: Strict JSON with `"categoría"` (one of three strings) and `"confianza"` (float 0.0–1.0)
- **Confidence threshold**: ≥ 0.7 required; below that routes to human review
- **Temperature**: 0.3 | **Top_p**: 0.9 | **Max tokens**: 100 | **Timeout**: 10s
- **Language**: Rioplatense Spanish dialect

### Validation Logic (per ANEXO_H specification)
Response validation must perform in order:
1. JSON syntax check via `json.loads()`
2. Field presence: both `"categoría"` and `"confianza"` must exist
3. Category string must match one of the three exact Spanish strings (case-sensitive)
4. Confidence must be float in range [0.0, 1.0]
5. On any failure: log exception, set confidence = 0.0, escalate to human review

## Memoria Compartida (Engram)

Las decisiones, descubrimientos y progreso del proyecto se persisten mediante **Engram**,
un sistema de memoria persistente que sobrevive entre sesiones y compactiones.

**La memoria se comparte via el repositorio** — no es solo local. El directorio `.engram/chunks/`
contiene chunks comprimidos exportados que deben trackearse en git.

**Workflow para colaboradores:**

```bash
# Al clonar o antes de empezar a trabajar:
engram sync --import --project "Automatizacion-de-Mesa-de-Ayuda-N8N"

# Durante la sesion, la memoria se guarda automaticamente via MCP

# Al finalizar la sesion (antes de commitear):
engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"
```

**Recomendacion:** alias en `.bashrc` / `$PROFILE`:
```powershell
function engram-sync-all { engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N" }
function engram-import { engram sync --import --project "Automatizacion-de-Mesa-de-Ayuda-N8N" }
```

## External Integrations

- **Microsoft Outlook**: Email trigger and automated reply
- **Twilio**: Receives phone call transcription via webhook
- **MTM-SRU**: Internal incident management system, receives HTTP POST to create tickets
- **Google Gemini API**: Classification requests (`google-genai >= 1.0`, the new SDK that replaces the deprecated `google-generativeai`)
- **Redis**: Session/memory storage for the LangChain AI agent

## Development Notes

- The workflow is currently set to **inactive** (`"active": false` in the JSON). Activate it in the N8N UI before testing.
- The JavaScript and Python code nodes in the workflow have been fully implemented (C-04): validation, normalization, Anexo H §H.3 checks, and HTTP payload mapping. No placeholders remain.
- The IF node conditions are configured: `confianza >= 0.70` (inclusive) in both channels.
- To deploy: import `Automatizacion_Mesa_de_Ayuda.json` into an N8N instance and configure credentials for Outlook, Twilio, and Gemini. The backend endpoint is `POST /api/v1/incidentes`.
- A `docker-compose.yml` for local testing (N8N 1.62 + FastAPI backend + PostgreSQL + Redis) is available at the root of the repository (added in C-04 verification). See `docs/n8n-workflow-guide.md` for setup instructions.
- The evaluation corpus (`data/corpus_evaluacion_pseudonimizado.csv`, 200 labeled cases) is not tracked in git.

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
- Author a backlog-ready spec/issue → invoke /spec
