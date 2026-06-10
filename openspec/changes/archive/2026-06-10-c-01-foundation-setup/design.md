# Design — c-01-foundation-setup

## Context

El repo ya tiene backend (`Gestion_Incidentes/`, FastAPI completo), frontend (`Frontend/`), roadmap (`CHANGES.md`), KB (`knowledge-base/`) y `openspec/` inicializado — pero sin `config.yaml`. La memoria compartida `.engram/` no está versionada. El clasificador Gemini emite `prompt_file_not_found` al arrancar: `gemini_classifier.py` resuelve `docs/prompt_gemini.txt` relativo al cwd/paquete del backend, pero el archivo vive en `docs/` de la raíz del repo. La base de datos corre en Docker Compose (`Gestion_Incidentes/docker-compose.yml`) con migraciones Alembic que incluyen el seed de catálogos (`001_seed_catalogs.py`).

Restricción de governance: BAJO (CHANGES.md) — autonomía completa si los tests pasan.

## Goals / Non-Goals

**Goals:**
- Entorno OPSX completamente operativo (`config.yaml` con stack real).
- Memoria compartida `.engram/` versionable + workflow documentado.
- Etapa Gemini del clasificador funcional (prompt resuelto correctamente desde cualquier cwd).
- Migraciones aplicadas y catálogos sembrados de forma verificable.

**Non-Goals:**
- No tocar lógica de negocio (clasificadores, servicios, rutas).
- No implementar pseudonimización (C-03) ni webhook N8N (C-02).
- No configurar CI/CD (C-09).
- No resolver IN-01 (`POST /clasificar`) ni IN-02 (auth) — requieren decisión aparte.

## Decisions

### D1 — Resolución del prompt: ruta anclada al repo con fallback configurable
El prompt se resolverá desde `settings` con una nueva variable `GEMINI_PROMPT_PATH` cuyo default es la ruta absoluta calculada desde la raíz del repo (`Path(__file__)` ancestors), no desde el cwd. **Alternativas**: (a) copiar `prompt_gemini.txt` dentro de `Gestion_Incidentes/docs/` — descartada: duplica la fuente de verdad que la tesis documenta en `docs/`; (b) mover el archivo a `Gestion_Incidentes/` — descartada: `docs/` es la ubicación canónica referenciada por la tesis y el Anexo H. La env var permite override en Docker (donde la estructura de carpetas difiere).

### D2 — `openspec/config.yaml` mínimo y declarativo
Solo stack, convenciones y rutas que los sub-agentes necesitan; sin duplicar la KB. **Alternativa**: config exhaustivo — descartada: la KB ya es la fuente de contexto; el config debe ser apuntador, no copia.

### D3 — `.engram/` versionado con sync por proyecto
Se corre `engram sync` (filtro por proyecto, NUNCA `--all` — el repo es público y el filtro evita fugas de memoria de otros proyectos) y se versionan los chunks. El workflow va al README: export antes de push, `--import` después de clone/pull.

### D4 — Verificación de DB idempotente
`alembic upgrade head` + query de conteo sobre los 3 catálogos. La migración 001 ya siembra; si la DB es nueva, el upgrade siembra todo; si existe, el upgrade es no-op. No se escribe SQL manual.

## Risks / Trade-offs

- [PostgreSQL no disponible al correr la verificación] → la verificación de DB se documenta como script reproducible (`alembic upgrade head` + chequeo) y se ejecuta con el compose levantado; si Docker no está disponible en la sesión, la tarea queda marcada con instrucciones exactas para ejecutarla.
- [Default de ruta del prompt incorrecto dentro del contenedor Docker] → la env var `GEMINI_PROMPT_PATH` permite override explícito en `docker-compose.yml`; el Dockerfile puede copiar `docs/` al build context si hiciera falta.
- [`.engram/` en repo público expone memoria del proyecto] → se versiona solo memoria de ESTE proyecto (filtro por defecto de `engram sync`); el contenido es técnico, no personal. Confirmado aceptable porque el repo ya es público con la tesis completa.

## Migration Plan

Cambios aditivos y de configuración; sin migración de datos. Rollback = revertir el commit.

## Open Questions

- ¿La instancia N8N de pruebas corre en el mismo compose? (afecta C-02, no bloquea C-01).
