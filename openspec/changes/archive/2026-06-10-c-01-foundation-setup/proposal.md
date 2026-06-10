# Proposal — c-01-foundation-setup

## Why

C-01 es el gate 0 del roadmap (`CHANGES.md`): ningún otro change puede ejecutarse con confianza hasta que la fundación operativa esté verificada. Hoy existen gaps concretos: `openspec/config.yaml` no existe, la memoria compartida `.engram/` no está configurada en el repo, y el entorno de ejecución tiene un defecto conocido — el clasificador Gemini no encuentra su prompt (`prompt_file_not_found` al arrancar, porque busca `docs/prompt_gemini.txt` relativo a `Gestion_Incidentes/` pero el archivo vive en `docs/` de la raíz), lo que deja la etapa 2 del clasificador híbrido inoperante.

## What Changes

- Crear `openspec/config.yaml` con el stack tecnológico del proyecto (FastAPI + SQLAlchemy async + PostgreSQL + N8N + Gemini + React/Vite) para que los sub-agentes OPSX hereden contexto correcto.
- Configurar `.engram/` en el repo para memoria compartida entre colaboradores y documentar el workflow de `engram sync` en el `README.md`.
- Corregir la resolución de la ruta del prompt de Gemini para que la etapa 2 del clasificador funcione desde cualquier directorio de trabajo.
- Verificar que `openspec list` y `openspec status` respondan correctamente (smoke check del CLI).
- Verificar que las migraciones Alembic estén al día y que los catálogos (sector, estado, canal_origen) estén sembrados en la base de datos; sembrarlos si faltan.

## Capabilities

### New Capabilities
- `foundation-environment`: configuración operativa verificable del entorno de desarrollo — config OPSX, memoria compartida, resolución de recursos (prompt Gemini), migraciones y catálogos sembrados.

### Modified Capabilities
<!-- Ninguna: este change no modifica comportamiento de negocio existente; es fundacional. -->

## Impact

- **Código**: `Gestion_Incidentes/app/classifiers/gemini_classifier.py` (o `config/settings.py`) — resolución de ruta del prompt.
- **Configuración**: `openspec/config.yaml` (nuevo), `.engram/` (nuevo), `README.md` (sección engram sync).
- **Base de datos**: verificación/siembra de catálogos vía Alembic (`alembic upgrade head`).
- **Dependencias**: ninguna librería nueva.
- **Desbloquea**: C-02 (notify-n8n-hook), C-03 (pseudonymization-module), C-07 (frontend-testing-setup) — el primer fork de paralelismo del roadmap.
